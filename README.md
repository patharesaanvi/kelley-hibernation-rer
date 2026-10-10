# Mammalian Hibernation — Relative Evolutionary Rate Analysis

Kelley Lab computational research project to test associations between hibernation and gene-specific relative evolutionary rates (RERs) across mammalian lineages.

## Workflow
1. Select a genome alignment (initial candidate: UCSC Hiller 470-mammal Multiz).
2. Audit target species and map names to alignment identifiers.
3. Extract high-quality orthologous coding-sequence alignments for a small pilot gene set.
4. Infer gene-specific branch lengths on a consistent reference topology.
5. Validate foreground/background hibernation branch encoding.
6. Run RERconverge, Kendall's tau analysis, and BH FDR correction.
7. Expand to a genome-wide analysis and integrate cross-species differential expression results.

## Data policy
Raw data, intermediate alignments, generated gene trees, plots, results and logs must live in **scratch**, never in Git. Configure `SCRATCH_ROOT` to the lab/HPC scratch location before running analyses. Paths listed in `config/paths.example.env` are examples, not verified lab paths. The repository contains only code, lab notes, small metadata/configuration files, and documentation.

## Contents
- `notebooks/`: dated Markdown lab notebook entries
- `config/`: input manifests and scratch examples
- `scripts/`: validation utilities
- `docs/`: workflow and decisions

## Initial steps
```bash
cp config/paths.example.env config/paths.env
# Edit SCRATCH_ROOT and DATASET_NAME in config/paths.env
python3 scripts/check_species_table.py config/species_template.tsv
```
The species table is a **template**, not a finalized classification. Populate it from a verified phenotype source and alignment assembly manifest.

## Core sources
- UCSC Hiller 470-mammal track: https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way
- Zoonomia 241-way track: https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons241way
- UCSC 100-way archive: https://hgdownload.gi.ucsc.edu/goldenPath/hg38/multiz100way/
- RERconverge source/tutorials: https://github.com/nclark-lab/RERconverge

## Reproducibility
Record source URLs, download dates, software versions, manifest checksums, reference assembly IDs and filtering thresholds in the lab notebook. Do not treat preliminary or unverified phenotype codes as analysis-ready.
