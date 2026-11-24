#!/usr/bin/env python3
"""Create a reproducible candidate list from a MANE CDS exon-interval TSV.
No alignment files are changed. Python 3 standard library only.
"""
import argparse,csv,random,collections,re
from pathlib import Path
# Select a reproducible subset of compact, multi-exon MANE coding sequences.
# Input: a tab-separated table of coding-exon intervals in hg38 coordinates.
# Output: candidate genes with transcript IDs and comma-separated exon ranges.
p=argparse.ArgumentParser()
p.add_argument('--intervals',required=True,type=Path)
p.add_argument('--out',required=True,type=Path)
p.add_argument('--n',type=int,default=50)
p.add_argument('--backups',type=int,default=50)
a=p.parse_args()
with a.intervals.open() as f:
    reader=csv.DictReader(f,delimiter='\t'); headers=reader.fieldnames or []
    print('Detected columns:', ', '.join(headers))
    def resolve(candidates,required=True):
        m={re.sub(r'[^a-z0-9]','',h.lower()):h for h in headers}
        for candidate in candidates:
            key=re.sub(r'[^a-z0-9]','',candidate.lower())
            if key in m:return m[key]
        if required: raise SystemExit('Cannot identify required column from '+repr(candidates)+'. Please show the first 3 rows of the TSV; no outputs created.')
        return None
    g=resolve(['gene_name','gene_symbol','gene','symbol','hgnc_symbol'])
    t=resolve(['transcript_id','transcript','mane_transcript','refseq_transcript','transcript_accession'],False)
    chrom=resolve(['chrom','chr','chromosome','seqname'])
    start=resolve(['start','cds_start','chrom_start','exon_start','start0','start_0based'])
    end=resolve(['end','cds_end','chrom_end','exon_end','end0','end_0based'])
    strand=resolve(['strand','gene_strand'],False)
    records=list(reader)
print('Input rows:',len(records))
# This program requires explicitly 0-based half-open coordinates, consistent with HBB.
# Detect common 1-based conventions and exit rather than silently shifting exons.
if any('1based' in h.lower().replace('_','') for h in [start,end]):
    raise SystemExit('Input labels imply 1-based coordinates; convert to BED 0-based half-open before proceeding.')
# Group exon intervals by gene, transcript, chromosome, and strand.
groups=collections.defaultdict(list)
for row in records:
    try: lo,hi=int(row[start]),int(row[end])
    except (ValueError,TypeError):continue
    if not (0<=lo<hi):continue
    gene=row[g].strip(); assembly_chr=row[chrom].strip()
    if not gene or not re.fullmatch(r'chr(?:[1-9]|1[0-9]|2[0-2])',assembly_chr):continue
    transcript=row[t].strip() if t else gene
    orientation=row[strand].strip() if strand else '?'
    groups[(gene,transcript,assembly_chr,orientation)].append((lo,hi))
# Keep genes with 2–8 non-overlapping exons and a 600–3500 bp CDS.
# These are technical pilot-selection criteria, not biological filters.
options=[]
for (gene,transcript,c,s),ranges in groups.items():
    ranges=sorted(set(ranges)); length=sum(y-x for x,y in ranges)
    # Require compact, multi-exon genes to bound pilot downloads and avoid single-exon families.
    if 2<=len(ranges)<=8 and 600<=length<=3500 and length%3==0 and ranges[-1][1]-ranges[0][0]<=80000:
        if all(ranges[i][1]<=ranges[i+1][0] for i in range(len(ranges)-1)):
            options.append((gene,transcript,c,s,ranges,length))
# If duplicate gene occurs under multiple transcripts, choose lexicographically first.
by_gene={}
for x in sorted(options,key=lambda z:(z[0],z[1])):by_gene.setdefault(x[0],x)
selected=list(by_gene.values())
# Fix the shuffle seed so the candidate order is reproducible.
random.Random(20261123).shuffle(selected)
print('Eligible distinct genes:',len(selected))
if len(selected)<a.n:raise SystemExit(f'Insufficient eligible genes ({len(selected)}). No files written; inspect columns and selection thresholds.')
a.out.parent.mkdir(parents=True,exist_ok=True)
if a.out.exists():raise SystemExit(f'Refusing to overwrite {a.out}')
# Export a candidate table consumed by staging and tree-fitting scripts.
with a.out.open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t');w.writerow(['gene','transcript','chrom','strand','exons','cds_bp','coordinates'])
    for x in selected[:a.n+a.backups]:
        gene,tx,c,s,exons,l=x
        w.writerow([gene,tx,c,s,len(exons),l,','.join(f'{b}-{e}' for b,e in exons)])
print('Saved:',a.out,'candidates:',min(len(selected),a.n+a.backups))
print('NOTE: requires independent confirmation that CDS coordinates are hg38 0-based half-open and exon rows belong to the MANE transcript.')
