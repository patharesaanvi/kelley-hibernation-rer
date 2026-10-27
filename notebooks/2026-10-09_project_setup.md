# Lab notebook — Project setup and October 2026 progress

These are my notes as I learn how to prepare genomic data for our Kelley Lab hibernation project. For a beginner-friendly overview, start with the [project README](../README.md). For a full explanation of the HBB test, see [HBB pilot: step by step](../docs/hbb_pilot.md).

## Research question

Which protein-coding genes evolve faster or slower in hibernating mammals than in non-hibernating mammals? Do any rate shifts appear independently in different hibernating groups (bats, rodents, bears, lemurs)? Eventually, can we compare these findings with RNA-seq differential-expression results?

## Project dataset

We're working with **Hiller 470-way mammalian genome alignments** from UCSC, not the UCSC 100-way dataset mentioned in the original grant.

- [Hiller alignment](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge GitHub](https://github.com/nclark-lab/RERconverge)
- [Species metadata](../config/species_metadata.tsv)
- [Current species summary](../results/species_summary.tsv)

### Species work completed

I added six hibernating candidate species (western European hedgehog, hazel dormouse, fat dormouse, woodchuck, Asian black bear, and northern long-eared bat), reviewed assembly choices where Hiller had more than one, and updated the metadata. We currently list **58 candidate species, of which 53 are represented in Hiller**. The 53 break down into **29 foreground candidates, 19 background candidates, and five uncertain**. These phenotype classifications are preliminary and will need review before we define foreground branches for RERconverge.

## My scripts: what they do and where the output goes

Run the scripts from the repository folder (`~/kelley-hibernation-rer`) on Hummingbird. The scratch folder is `/scratch/spathare/hibernation_rer/`.

| Script | What it does | Output and where it is saved |
| --- | --- | --- |
| [`scripts/check_species.py`](../scripts/check_species.py) | Checks the metadata for duplicates, missing assembly IDs, and statuses to review. | **Prints checks in the terminal**; does not write an output file. |
| [`scripts/hiller_mapping.py`](../scripts/hiller_mapping.py) | Reads the Hiller trees, matches species names to assemblies, and checks our species list. | Writes `rer_results/hiller_assembly_mapping.tsv` in scratch, updates the local [metadata](../config/species_metadata.tsv), and makes a scratch backup `rer_results/species_metadata_backup.tsv` if one does not already exist. |
| [`scripts/species_summary.py`](../scripts/species_summary.py) | Counts hibernating, non-hibernating, and uncertain candidates by mammal group. | Writes `rer_results/species_summary.tsv` in scratch. A separately committed copy is at [`results/species_summary.tsv`](../results/species_summary.tsv). |
| [`scripts/build_hbb_alignment.py`](../scripts/build_hbb_alignment.py) | Reads the three extracted HBB MAF files and combines the reference-guided coding sequences for our species. | Writes `gene_alignments/HBB_53species_CDS.fasta` in scratch and prints missing base counts. |

**Important:** Scratch outputs don't automatically show up on GitHub. The small summary in `results/` is a saved copy, so it needs to be updated manually if the script is run again. Running the mapping script can change your **local** metadata; commit and push it only after reviewing those changes.

### Hiller trees I downloaded

The two tree files are saved on Hummingbird, under `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/`:

- `hg38.470way.nh` — tree tips have assembly IDs, such as `hg38` and `mm39`.
- `hg38.470way.scientificNames.nh` — tree tips use scientific names.

## HBB test — figuring out the gene-tree input format

Our task was to figure out **how to go from Hiller gene alignments to gene-tree inputs for RERconverge**. I used HBB as a small test gene because it is well studied and short, **not** because we already know it is important for hibernation.

For the detailed explanation, genomic coordinates, run command, and quality concerns, see [the full HBB pilot notes](../docs/hbb_pilot.md).

### What I did and why

| Step | Why I did it | Output (under `/scratch/spathare/hibernation_rer/`) |
| --- | --- | --- |
| Extracted the three HBB coding regions using `bigBedToBed` | Needed the same genomic region aligned across mammals without downloading huge chromosome files. | `gene_alignments/HBB_5225597_5225726.maf`, `HBB_5226576_5226799.maf`, `HBB_5226929_5227021.maf` |
| Built the 53-species HBB alignment using [my script](../scripts/build_hbb_alignment.py) | Wanted one FASTA sequence for each of our Hiller assemblies. | `gene_alignments/HBB_53species_CDS.fasta` |
| Checked and filtered the alignment | Seven species had missing nucleotide positions, so I kept 46 complete sequences for this **first test**. | `gene_alignments/HBB_complete_CDS.fasta` |
| Pruned the Hiller tree | The original tree includes hundreds of assemblies; the tree tips needed to match the same 46 HBB sequences. | `gene_trees/HBB_pruned_topology.nwk` |
| Ran RAxML-NG | Estimated **HBB-specific branch lengths** while keeping Hiller's branching pattern fixed. | `gene_trees/HBB_test.raxml.bestTree`, plus `HBB_test.raxml.bestModel` and `HBB_test.raxml.log` |
| Made the gene-tree TSV | RERconverge expects a gene name followed by its Newick tree, separated by a tab. | `gene_trees/hiller_hibernation_gene_trees.tsv` (currently one HBB row) |

### Results of the HBB test

- Initial alignment: **53 sequences**, **444 bp** each.
- Strict complete-sequence filter: **46 sequences** retained.
- Pruned Hiller tree: **46 tips**, exactly matching the filtered FASTA.
- RAxML-NG final log-likelihood: **−5033.417582**.
- RAxML-NG warning: **seven near-zero branches**.
- The RERconverge input TSV has **one line starting with `HBB`**.
- **I have not tested reading the file with RERconverge yet.** I have not established that HBB shows a hibernation-related rate shift.

### What I still need to check

The alignment is a preliminary **human-reference-guided** extraction. It doesn't preserve species-specific insertions, and I haven't verified that every aligned sequence is a true HBB ortholog. The final missing-data rule and method for estimating branch lengths also need to be decided.

The HBB filtering, Hiller-tree pruning, and final tree formatting were **one-off terminal commands**, not separately committed Python scripts.

## Questions for Avrami

1. I used **RAxML-NG** to estimate HBB branch lengths because it was on Hummingbird. Is this the method we want for the full pipeline, or is there a lab-preferred method?
2. For genes with some missing nucleotides, how much missing sequence data should be acceptable? Should we drop very incomplete species but retain those with only a few missing positions?
3. How should we validate orthology and alignments before generating gene trees for many genes?
4. How should we define the hibernating foreground branches, especially for species with uncertain classifications?
5. Once the HBB input-loading test works, should I start by automating a small set of orthologous genes?

## Next to-dos

- [ ] Discuss the gene-tree method and missing-data choices with Avrami.
- [ ] Check HBB orthology, sequence alignment, coding frame, and gaps.
- [ ] Test loading `hiller_hibernation_gene_trees.tsv` with RERconverge.
- [ ] Save the temporary filter, tree-prune, and TSV-formatting commands as reusable scripts.
- [ ] Test the workflow on several additional orthologous genes.
- [ ] Finalize the phenotype assignments and gene-tree QC rules before processing the larger Hiller dataset.

## My main takeaway

I was able to **produce one preliminary gene-tree input from Hiller data**, but the important next step is to make sure the alignment and methods are reliable before scaling up. This week was about building the workflow, not making biological conclusions.
