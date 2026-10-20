# Lab notebook — October 9, 2026

## Research question
Which genes evolve faster or slower in hibernating mammals compared to non-hibernating mammals? Are these changes shared across different hibernating groups, and do they overlap with genes that change expression during hibernation?

## Project overview
We're using the **Hiller 470-way mammal alignment** for this project. The goal is to get gene alignments, generate gene trees with branch lengths, and use RERconverge to look for evolutionary rate shifts. Later, we'll look at pathways, compare our results with RNA-seq findings, and use PAML for follow-up selection tests.

## Links I used
- [Hiller 470 alignment](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge GitHub](https://github.com/nclark-lab/RERconverge)

## My scripts and where the results go

I run these scripts from `~/kelley-hibernation-rer` on Hummingbird. Most output files are saved under `/scratch/spathare/hibernation_rer/`, since the larger analysis files are not stored on GitHub.

| Script | What I used it for | Where to find the output |
| --- | --- | --- |
| [`check_species.py`](../scripts/check_species.py) | Checks our species list for duplicate species, missing assembly IDs, and hibernation classifications that still need review. | Prints the results in the terminal; it doesn't save a file. |
| [`hiller_mapping.py`](../scripts/hiller_mapping.py) | Compares our species list with the Hiller trees to see which species and assemblies are available. | `/scratch/spathare/hibernation_rer/rer_results/hiller_assembly_mapping.tsv`. It also updates [`config/species_metadata.tsv`](../config/species_metadata.tsv) locally and saves a backup in scratch. |
| [`species_summary.py`](../scripts/species_summary.py) | Counts how many species we have in each mammal group and hibernation category. | `/scratch/spathare/hibernation_rer/rer_results/species_summary.tsv`. I also saved a copy in GitHub: [`results/species_summary.tsv`](../results/species_summary.tsv). |

**Note:** Running these scripts on Hummingbird doesn't automatically update GitHub. I still need to commit and push any changed files.

## Hiller tree files

The species trees I used are saved on Hummingbird:

- `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.nh` — assembly IDs
- `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.scientificNames.nh` — scientific names

## HBB test — gene-tree input for RERconverge

I used HBB as a test gene to figure out how to go from the Hiller alignment to a gene tree. I started with the same **53 species** from our Hiller dataset. Seven had missing bases for HBB, so I kept 46 complete sequences for this first test.

| What I did | Output saved on Hummingbird |
| --- | --- |
| Extracted the three HBB coding regions from Hiller using `bigBedToBed` | `gene_alignments/HBB_5225597_5225726.maf`, `HBB_5226576_5226799.maf`, `HBB_5226929_5227021.maf` |
| Used `build_hbb_alignment.py` to put together the HBB sequences | `gene_alignments/HBB_53species_CDS.fasta` |
| Filtered out sequences with missing bases | `gene_alignments/HBB_complete_CDS.fasta` |
| Pruned the Hiller tree to match the 46 sequences | `gene_trees/HBB_pruned_topology.nwk` |
| Used RAxML-NG to estimate HBB branch lengths | `gene_trees/HBB_test.raxml.bestTree` (also `HBB_test.raxml.log` and `HBB_test.raxml.bestModel`) |
| Put the gene name and tree into the format RERconverge expects | `gene_trees/hiller_hibernation_gene_trees.tsv` |

All the HBB paths in this table start with `/scratch/spathare/hibernation_rer/`.

I made `scripts/build_hbb_alignment.py` on Hummingbird, but **I still need to upload it to GitHub**. The filtering, tree-pruning, and final formatting steps were commands I ran in the terminal, not separate GitHub scripts yet.

## What I still need to do

- Check that the HBB sequences are correctly aligned and that they represent the same gene across species.
- Test whether RERconverge can read the gene-tree file.
- Ask Avrami if RAxML-NG is the method we should use for branch lengths.
- Put the HBB steps into reusable scripts, then test the process on more genes.
