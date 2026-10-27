# Mammalian Hibernation — Comparative Genomics and Evolutionary Rates

**Kelley Lab | Undergraduate research project | Research in progress**

## What is this project about?

Some mammals can enter hibernation, slowing down their metabolism and changing their body temperature, heart rate, and energy use. Hibernation has evolved in different groups of mammals, including rodents, bats, bears, and lemurs.

Our main question is: **Do the same genes evolve faster or slower in different hibernating mammals compared with non-hibernating mammals?**

We want to find changes shared across independently hibernating lineages (convergent patterns) and changes specific to a particular group. Eventually, we'll compare these results with genes whose expression changes during hibernation.

This repository documents my progress developing the comparative genomics workflow, including species selection, gene alignment extraction, and preparation of gene trees for **RERconverge**. **This is an ongoing project, not a completed analysis or a set of confirmed hibernation genes.**

## Where the project stands (October 2026)

| Part of project | Current progress |
| --- | --- |
| Choose mammalian species | 58 candidate species in our metadata; 53 represented in Hiller |
| Hibernation classifications | Among the 53 Hiller species: 29 foreground candidates, 19 background candidates, 5 uncertain; assignments still need biological review |
| Match species to Hiller | Python scripts check species names, genome assemblies, and Hiller availability |
| Extract gene alignments | Completed an initial test with **HBB**, a hemoglobin gene |
| Prepare a test gene tree | Completed a 46-species HBB tree with estimated branch lengths using RAxML-NG |
| Format gene tree for RERconverge | Created a one-gene, tab-separated Newick file |
| Run RERconverge | **Not done yet** |
| Genome-wide gene analysis | **Not done yet**; requires additional alignment and orthology validation |

### Why we're using Hiller 470

The project uses the **[Hiller 470-way mammalian genome alignment](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)**. It contains genome-wide alignments across many mammalian assemblies and includes many of the hibernating lineages we're interested in.

Although the original project grant described using UCSC 100-way alignments, **our current chosen dataset is Hiller 470**.

We keep candidate species and assembly choices in [`config/species_metadata.tsv`](config/species_metadata.tsv). The current [species group summary](results/species_summary.tsv) is a saved snapshot; classifications and choices are still provisional.

## Our planned workflow

```text
Hiller 470-way genome alignment
        |
        v
Choose species and confirm assembly IDs
        |
        v
Extract the same orthologous gene across species
        |
        v
Check alignment quality, missing data, and orthology
        |
        v
Use a species-tree topology and estimate gene-specific branch lengths
        |
        v
Write gene ID + Newick tree on each line of a TSV file
        |
        v
RERconverge: estimate relative rates across genes and branches
        |
        v
Test associations with hibernation (Kendall's tau)
        |
        v
Correct for multiple testing (Benjamini–Hochberg)
        |
        v
Pathway enrichment, compare with RNA-seq, selected PAML follow-up tests
```

**Important:** The early steps have been tested using **one gene**. The later RERconverge and downstream analysis steps have not been run yet. The method for estimating branch lengths across the full dataset still needs to be confirmed with Avrami.

## The HBB test — what we did and why

We chose **HBB (hemoglobin subunit beta)** as a test gene because it is short and well studied. It is involved in oxygen transport, but we have **not shown that HBB is associated with hibernation**. The purpose was to understand how to prepare the inputs for RERconverge before processing many genes.

1. Looked up the human HBB transcript and its three coding regions (444 reference-aligned coding bases in total).
2. Retrieved those regions from Hiller using UCSC's `bigBedToBed` utility, saving three **MAF** (multiple alignment format) files.
3. Used [`build_hbb_alignment.py`](scripts/build_hbb_alignment.py) to reconstruct a 53-assembly FASTA alignment from those MAF blocks.
4. Checked the sequences. Seven had one or more missing nucleotides, so for this **strict initial test** we kept 46 complete sequences. Missing nucleotides do **not** always require excluding a species in the final pipeline.
5. Pruned the Hiller species tree so it contained exactly those 46 assemblies. **Pruning removed extra tree tips, not DNA bases.**
6. Used **RAxML-NG** to estimate HBB-specific branch lengths while keeping the pruned Hiller topology fixed.
7. Saved a gene-tree input file containing one row: `HBB<TAB><Newick tree>`.

**Pilot results:** 46 matching tree tips; RAxML-NG completed with final log-likelihood **−5033.417582** and warned about **7 near-zero branches**. These results show that the commands produced the expected files, **not** that the gene alignment is fully validated or that HBB has an unusual hibernation-associated evolutionary rate.

See the [step-by-step HBB explanation](docs/hbb_pilot.md) for methods, actual file paths, outputs, limitations, and what remains to check.

## Where everything is in this repository

| Location | What you'll find |
| --- | --- |
| [`config/species_metadata.tsv`](config/species_metadata.tsv) | Candidate mammal names, genome assembly IDs, Hiller availability, preliminary hibernation status, and mammal groups |
| [`scripts/check_species.py`](scripts/check_species.py) | Checks the metadata for problems and prints a report |
| [`scripts/hiller_mapping.py`](scripts/hiller_mapping.py) | Compares the species list with Hiller's trees; saves an assembly mapping and updates local metadata |
| [`scripts/species_summary.py`](scripts/species_summary.py) | Counts foreground/background/uncertain species by mammal group |
| [`scripts/build_hbb_alignment.py`](scripts/build_hbb_alignment.py) | Builds the HBB reference-guided coding alignment from saved MAF regions |
| [`results/species_summary.tsv`](results/species_summary.tsv) | Small, committed snapshot of species-group counts |
| [`docs/input_requirements.md`](docs/input_requirements.md) | What information is needed to run the broader analysis |
| [`docs/hbb_pilot.md`](docs/hbb_pilot.md) | The HBB example, why each step was done, how outputs connect |
| [`notebooks/2026-10-09_project_setup.md`](notebooks/2026-10-09_project_setup.md) | My lab notebook, with script-to-output links and open questions |
| [`config/paths.example.env`](config/paths.example.env) | Example scratch path configuration |

## How to find the results

This GitHub repository contains **code, small metadata files, and notes**. The actual genome alignments and generated gene trees are kept on **Hummingbird scratch**, not in GitHub.

- Repository on Hummingbird: `~/kelley-hibernation-rer`
- Scratch root: `/scratch/spathare/hibernation_rer`
- Hiller species trees: `raw_alignments/hiller470/`
- HBB MAF and FASTA alignments: `gene_alignments/`
- HBB gene trees and logs: `gene_trees/`
- Generated species summaries and mapping: `rer_results/`

For instance, the pilot's branch-length tree is at:
`/scratch/spathare/hibernation_rer/gene_trees/HBB_test.raxml.bestTree`

The RERconverge-formatted pilot file is at:
`/scratch/spathare/hibernation_rer/gene_trees/hiller_hibernation_gene_trees.tsv`

These paths refer to files on Hummingbird and cannot be downloaded by clicking a GitHub link. Scratch storage is subject to cluster retention policies.

## What needs to happen next

- **Review methodology with Avrami:** confirm whether to keep using RAxML-NG to estimate gene-specific branch lengths.
- **Validate the HBB pilot:** confirm orthology, inspect alignment gaps and coding frame, and review the seven near-zero branches.
- **Test RERconverge:** check that it can load the gene-tree TSV; one gene is insufficient for the full relative-rate analysis.
- **Decide missing-data thresholds and finalize phenotype/foreground assignments.**
- **Automate the remaining manual steps**, then pilot several genes before trying a genome-wide analysis.
- **Scale to orthologous genes across our chosen Hiller species**, only after the workflow is validated.

## Key concepts

- **Orthologs:** corresponding genes in different species inherited through speciation. An aligned region isn't automatically a confirmed ortholog.
- **MAF:** a format for aligned DNA blocks across genomes.
- **FASTA:** a format for named DNA or protein sequences.
- **Species tree:** phylogenetic relationships among species.
- **Gene-specific branch lengths:** model-based estimates of sequence change for one gene on each branch.
- **RERconverge:** compares gene-specific evolutionary-rate patterns to identify associations with traits, such as hibernation.
- **Newick:** text format representing a phylogenetic tree and its branch lengths.

## References

- [Hiller 470-way — UCSC Genome Browser](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge software](https://github.com/nclark-lab/RERconverge)
- [RAxML-NG software](https://github.com/amkozlov/raxml-ng)

The HBB pilot is an **input-preparation example**. It should not yet be interpreted as a biological result about hibernation.
