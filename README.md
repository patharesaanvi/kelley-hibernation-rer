# Mammalian Hibernation — Relative Evolutionary Rate Analysis

Kelley Lab computational research project investigating evolutionary rate shifts associated with hibernation across mammalian species using RERconverge.

## Research Objective

Identify genes exhibiting accelerated or decelerated evolutionary rates in hibernating mammals compared to non-hibernating mammals.

## Workflow

1. Obtain the Hiller 470-mammal genome alignment.
2. Identify target hibernating species and suitable non-hibernating comparison species.
3. Extract orthologous gene alignments.
4. Generate gene-specific phylogenetic trees and estimate branch lengths.
5. Run RERconverge to identify evolutionary rate shifts associated with hibernation.
6. Perform statistical analysis, multiple-testing correction, and functional enrichment.
7. Compare evolutionary findings with differential gene expression results.

## Repository Structure

- config/ — Species metadata and configuration files
- scripts/ — Analysis and validation scripts
- notebooks/ — Markdown lab notebook documenting research progress
- docs/ — Additional documentation

## Data Storage

All raw genomic data, alignments, gene trees, intermediate files, and analysis outputs will be stored in Hummingbird scratch storage, not in the GitHub repository.

GitHub will contain only code, configuration templates, small metadata files, documentation, and lab notebook entries.

## Resources

- [Hiller Lab 470 Mammals — UCSC Genome Browser](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge — GitHub](https://github.com/nclark-lab/RERconverge)
