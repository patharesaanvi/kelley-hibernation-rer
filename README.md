# Mammalian Hibernation — Relative Evolutionary Rate Analysis

Kelley Lab computational research project investigating evolutionary rate shifts associated with hibernation across mammalian species using RERconverge.

## Research Objective

Identify genes with accelerated or decelerated evolutionary rates in hibernating mammals compared with non-hibernating mammals, including changes shared across independently hibernating lineages.

## Workflow

1. Use the **Hiller 470-way mammalian genome alignment**.
2. Identify hibernating species and suitable non-hibernating comparison species.
3. Extract and check orthologous gene alignments.
4. Generate gene-specific phylogenetic trees and estimate branch lengths.
5. Use RERconverge to identify evolutionary rate shifts associated with hibernation.
6. Perform statistical testing, multiple-testing correction, and functional enrichment.
7. Compare findings with differential gene expression results and perform follow-up selection analyses.

## Current Progress

- Created species metadata for **58 candidate mammals**, with **53 represented in Hiller**.
- Developed scripts to check species availability, genome assembly IDs, and hibernation classifications.
- Used **HBB** as a test gene to extract a 53-species alignment from Hiller.
- Filtered the HBB alignment to **46 complete sequences**, pruned the Hiller species tree, and used **RAxML-NG** to estimate gene-specific branch lengths.
- Formatted the HBB gene tree for RERconverge. **The input has not yet been tested in RERconverge**, and the pilot alignment still needs validation.

## Repository Structure

- [`config/`](config/) — Species metadata and configuration files
- [`scripts/`](scripts/) — Python analysis and validation scripts
- [`notebooks/`](notebooks/) — Research progress and lab notes
- [`docs/`](docs/) — Detailed methodology, including the [HBB pilot](docs/hbb_pilot.md)
- [`results/`](results/) — Small saved analysis summaries

## Data Storage

Raw genomic data, gene alignments, gene trees, and intermediate files are stored on Hummingbird scratch under:

`/scratch/spathare/hibernation_rer/`

GitHub contains the scripts, species metadata, small results, and documentation.

## Resources

- [Hiller 470-way Mammalian Alignment — UCSC](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge — GitHub](https://github.com/nclark-lab/RERconverge)
