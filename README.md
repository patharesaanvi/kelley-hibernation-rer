# Mammalian Hibernation — Relative Evolutionary Rate Analysis

Kelley Lab computational research project investigating evolutionary-rate shifts associated with hibernation across mammals using RERconverge.

## Research objective

Identify genes with relatively accelerated or decelerated evolutionary rates associated with hibernation, including possible shared shifts across independently hibernating lineages. **No phenotype-association results or candidate hibernation genes have been established yet.**

## Workflow

1. Start with the **Hiller 470-way mammalian alignment** and the selected mammalian assemblies.
2. Identify human coding-exon intervals from MANE transcript annotations and extract corresponding aligned sequences.
3. Filter gene-specific alignments for missing sequence data and retained taxa.
4. Use RAxML-NG to optimize branch lengths on a fixed species-tree topology.
5. Assemble compatible gene trees and import them using RERconverge `readTrees()`.
6. Calculate preliminary relative evolutionary-rate residuals with `getAllResiduals()`; inspect their structure and quality.
7. **Planned, not yet performed:** expand the background gene set, validate phenotypes, test associations with hibernation, apply multiple-testing correction, and investigate functional enrichment and other biological follow-up analyses.

## Current progress — November 24, 2026

### Initial HBB pilot
- Prepared the selected-species metadata: **58 candidate mammals**, **53 represented in Hiller**.
- Extracted HBB coding-alignment data and fitted RAxML-NG branch lengths on a pruned, fixed Hiller topology.
- Confirmed that RERconverge `readTrees()` could import the single HBB tree; `getAllResiduals()` could not be completed meaningfully with this single-gene input.
- Performed HBB reference-gap, topology, bootstrap (100 replicates), and 10%-missingness checks; see the [November 17 notebook](notebooks/2026-11-17_quality_control.md).

### Multi-gene technical pilot
- Adapted the existing extraction / RAxML-NG workflow for **30 selected protein-coding genes**.
- Staged **153 nonempty coding-exon files** from the Hiller 470-way alignment.
- Generated **30/30 gene-specific trees**, with **30–53 species per gene** after a **10% missing-data filter**. The script's minimum-species threshold was temporarily lowered from 35 to 4 after TRIM52 retained 30 species; this is a permissive **technical-test parameter, not an endorsed biological threshold**.
- Checked that all 30 fitted trees have compatible unrooted topologies on their respective overlapping species sets, with no missing, negative, or nonfinite fitted branch lengths. These checks do **not** establish alignment quality or orthology.
- Imported all 30 trees into RERconverge using `readTrees(minTreesAll = 3, max.read = 30)`. The resulting master tree includes **53 species**, with master branch lengths estimated from **three full-coverage genes**.
- Completed `getAllResiduals()`. The **preliminary** output is a **30 × 627 gene-by-phylogenetic-path residual matrix**. Column meaning, missing/undefined residuals, and the numerical suitability of the rates require further validation.
- **No hibernation-phenotype association test has been run.**

See [November 24 lab notebook](notebooks/2026-11-24_pilot30.md) and [30-gene pilot workflow](docs/pilot30_workflow.md).

## Next steps

- Understand the RERconverge path matrix and the missing/undefined residual values; determine whether further filtering or normalization checks are needed.
- Review coding alignment, strand/frame handling, orthology, and branch-length quality across genes.
- Decide a scientifically suitable minimum species/lineage coverage with the supervising researcher.
- The core Python staging/fitting scripts, five-/25-gene SLURM wrappers, RERconverge scripts and the three pilot candidate tables are committed. Five SLURM wrappers were updated to reference the repository's scripts/ directory; these revised wrappers have not been rerun on Hummingbird. The separate TRIM52-only candidate file and some exact run-preparation steps remain to document.
- Expand to a larger gene set before interpreting rates and performing hibernation association tests.

## Repository structure

- [`config/`](config/) — Species metadata and configuration.
- [`scripts/`](scripts/) — Committed HBB and 30-gene Python/R scripts.
- [`slurm/`](slurm/) — SLURM submission wrappers for the 30-gene pilot, updated to invoke scripts in this repository.
- [`notebooks/`](notebooks/) — Dated research notes.
- [`docs/`](docs/) — Input requirements, HBB pilot, and 30-gene workflow documentation.
- [`results/`](results/) — Small, checked-in summaries (not large analysis outputs).

## Data storage

Large datasets, alignments, estimated trees, RERconverge RDS objects, and job output remain on Hummingbird under:

`/scratch/spathare/hibernation_rer/`

In particular, the combined pilot outputs are under `pilot30_combined/`. Core source code and candidate tables are committed. Full rerun still depends on original Hummingbird software modules, pre-staged UCSC exon data under scratch, and a fresh output directory; the separate TRIM52-only annotation file is not yet tracked. No rerun of the revised wrappers has been verified.

## Resources

- [Hiller 470-way Mammalian Alignment — UCSC](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge — GitHub](https://github.com/nclark-lab/RERconverge)
