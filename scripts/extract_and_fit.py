#!/usr/bin/env python3
"""Build technical-pilot reference-guided alignments and RAxML trees.
Must run on cluster with Biopython, bigBedToBed, raxml-ng. Does not verify orthology.
"""
import argparse,csv,subprocess,shutil,re,io,sys
from pathlib import Path
from Bio import AlignIO,Phylo
from Bio.Seq import Seq
# Inputs: staged exon BED4 files, candidate-gene table, species metadata,
# and the master species-tree topology. Outputs: per-gene alignments,
# RAxML-NG branch-length trees, a status table, and a combined tree TSV.
p=argparse.ArgumentParser()
p.add_argument('--candidates',required=True,type=Path)
p.add_argument('--species',required=True,type=Path)
p.add_argument('--master',required=True,type=Path)
p.add_argument('--bigmaf',required=True)
p.add_argument('--outdir',required=True,type=Path)
p.add_argument('--target',type=int,default=50)
p.add_argument('--min-species',type=int,default=35)
p.add_argument('--max-missing',type=float,default=.10)
p.add_argument('--min-bp',type=int,default=600)
p.add_argument('--threads',type=int,default=2)
a=p.parse_args()
for binary in ('bigBedToBed','raxml-ng'):
    if not shutil.which(binary):raise SystemExit(f'Missing executable: {binary}; load the cluster module first')
if not a.master.is_file():raise SystemExit('Missing master species tree')
a.outdir.mkdir(parents=True,exist_ok=True)
# Retain only requested assemblies that are present in the master tree.
selected={'hg38'}
with a.species.open() as f:
    for row in csv.DictReader(f,delimiter='\t'):
        if row['in_hiller'].strip().lower()=='yes' and row['assembly_id'].strip():selected.add(row['assembly_id'].strip())
master=Phylo.read(str(a.master),'newick'); labels={t.name for t in master.get_terminals()}
selected &= labels
print('Selected tree-compatible assemblies:',len(selected),flush=True)
summary=a.outdir/'pilot_status.tsv'
if summary.exists():raise SystemExit('Status file exists; use a NEW output directory to avoid overwrites')
with a.candidates.open() as f:candidates=list(csv.DictReader(f,delimiter='\t'))

# Process one candidate gene. The exon files are staged in advance;
# this function does not retrieve bigMaf data from the network.
def process(row,folder):
    gene=row['gene'];chrom=row['chrom']; strand=row['strand']; coords=[]
    for part in row['coordinates'].split(','):
        lo,hi=map(int,part.split('-'))
        if lo>=hi:raise ValueError('Invalid exon coordinates')
        coords.append((lo,hi))
    if strand not in ('+','-'):raise ValueError('Gene strand must be + or -; check annotation columns')
    if sum(y-x for x,y in coords)%3:raise ValueError('CDS length not divisible by 3')
    pieces={s:[] for s in selected}
    for exon_i,(start,end) in enumerate(coords):
        # BED4 bigMaf records carry a single MAF block in their fourth field.
        bed=folder/f'exon_{exon_i+1}.bed'
        if bed.exists():
            if bed.stat().st_size == 0:
                raise ValueError('Cached BED file is empty')
        else:
            raise ValueError(f'Missing staged BED file: {bed}')
        # Initialize each exon with Ns so uncovered bases count as missing data.
        positions={s:['N']*(end-start) for s in selected}
        maf=[]
        with bed.open() as f:
            for line in f:
                fields=line.rstrip('\n').split('\t',3)
                if len(fields)<4:raise ValueError('Expected BED4 bigMaf records')
                maf.append(fields[3].replace(';', '\n').rstrip() + '\n\n')
        if not maf:raise ValueError(f'No bigMaf records for exon {chrom}:{start}-{end}')
        # Place aligned bases at their hg38 reference positions, ignoring gaps.
        for block in AlignIO.parse(io.StringIO(''.join(maf)),'maf'):
            ref=next((rec for rec in block if rec.id.startswith('hg38.')),None)
            if ref is None:continue
            if ref.annotations.get('strand')!=1:raise ValueError('Unexpected hg38 reference orientation')
            ref_pos=ref.annotations['start']
            for col,base in enumerate(str(ref.seq).upper()):
                if base=='-':continue
                if start<=ref_pos<end:
                    offset=ref_pos-start
                    for rec in block:
                        assembly=rec.id.split('.')[0]
                        if assembly not in selected:continue
                        nucleotide=str(rec.seq[col]).upper()
                        if nucleotide not in 'ACGT':continue
                        prev=positions[assembly][offset]
                        if prev!='N' and prev!=nucleotide:
                            raise ValueError(f'Conflicting MAF block for {assembly} at {ref_pos}')
                        positions[assembly][offset]=nucleotide
                ref_pos+=1
        for s in selected:pieces[s].extend(positions[s])
    seqs={}
    # Concatenate coding exons, orient negative-strand genes, and filter
# assemblies exceeding the allowed missing-base fraction.
    for s,parts in pieces.items():
        seq=''.join(parts)
        if strand=='-':seq=str(Seq(seq).reverse_complement())
        missing=sum(b not in 'ACGT' for b in seq)/len(seq)
        if missing<=a.max_missing:seqs[s]=seq
    if 'hg38' not in seqs:raise ValueError('Missing hg38 reference sequence')
    if len(seqs)<a.min_species:raise ValueError(f'Only {len(seqs)} species pass missingness filter')
    if len(next(iter(seqs.values())))<a.min_bp:raise ValueError('CDS shorter than minimum bp')
    # Avoid making branch-length estimates when reference is clearly not a valid CDS.
    human=seqs['hg38']
    if human[:3]!='ATG':raise ValueError('Human sequence does not start with ATG')
    if 'N' in human or '-' in human:raise ValueError('Human reference contains unknown bases')
    if '*' in str(Seq(human[:-3]).translate()):raise ValueError('Human reference contains internal stop')
    fasta=folder/f'{gene}.fasta'
    with fasta.open('x') as f:
        for name in sorted(seqs):f.write(f'>{name}\n{seqs[name]}\n')
    # Prune the fixed species-tree topology to the retained assemblies.
    tree=Phylo.read(str(a.master),'newick')
    for tip in list(tree.get_terminals()):
        if tip.name not in seqs:tree.prune(tip)
    if {tip.name for tip in tree.get_terminals()}!=set(seqs):raise ValueError('Pruned tree tips mismatch FASTA')
    tree_path=folder/f'{gene}.topology.nwk';Phylo.write(tree,str(tree_path),'newick')
    prefix=folder/gene
    # Estimate branch lengths on the FIXED topology under GTR+G;
# --evaluate does not search for a new branching arrangement.
    cmd=['raxml-ng','--evaluate','--msa',str(fasta),'--tree',str(tree_path),'--model','GTR+G','--prefix',str(prefix),'--threads',str(a.threads),'--seed','42']
    with (folder/'raxml.stdout.log').open('w') as out:
        subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,check=True)
    best=Path(str(prefix)+'.raxml.bestTree')
    if not best.exists():raise ValueError('RAxML-NG did not produce bestTree')
    tree_result=Phylo.read(str(best),'newick')
    if {t.name for t in tree_result.get_terminals()}!=set(seqs):raise ValueError('RAxML-NG tip mismatch')
    return len(seqs),len(human),best.read_text().strip()

# Attempt genes in candidate-table order and record individual failures.
successful=[]
with summary.open('x',newline='') as status:
    w=csv.writer(status,delimiter='\t');w.writerow(['gene','status','n_species','cds_bp','reason'])
    for idx,row in enumerate(candidates,1):
        if len(successful)>=a.target:break
        gene=row['gene']; safe=re.fullmatch(r'[A-Za-z0-9_.-]+',gene)
        if not safe:
            w.writerow([gene,'failed','','','unsafe gene symbol']);status.flush();continue
        folder=a.outdir/'genes'/gene;folder.mkdir(parents=True,exist_ok=True)
        try:
            count,bp,tree=process(row,folder)
            successful.append((gene,tree))
            w.writerow([gene,'passed',count,bp,''])
            print(f'PASS {gene}: {count} species, {bp} bp',flush=True)
        except Exception as e:
            w.writerow([gene,'failed','','',str(e).replace('\t',' ').replace('\n',' ')[:300]])
            print(f'FAIL {gene}: {e}',file=sys.stderr,flush=True)
        status.flush()
    status.flush()
# Save successful gene names and Newick trees for RERconverge import.
out=a.outdir/'gene_trees.tsv'
with out.open('x') as f:
    for gene,tree in successful:f.write(gene+'\t'+tree+'\n')
print(f'Completed {len(successful)} gene trees. Output: {out}',flush=True)
if len(successful)<a.target:sys.exit('Fewer than requested successful genes. Inspect pilot_status.tsv.')
