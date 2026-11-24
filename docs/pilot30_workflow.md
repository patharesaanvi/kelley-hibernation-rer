# 30-gene pilot workflow — November 24, 2026

This page describes the **workflow that was tested** and the saved outputs. It is not yet a self-contained executable tutorial: several scripts used on Hummingbird have not been added to GitHub. For exact counts and limitations see [the dated notebook](../notebooks/2026-11-24_pilot30.md).

## 1. Prepare the candidate genes
- Starting point: a larger candidate list of human **MANE** protein-coding transcripts.
- Pilot selection: first **30** candidate genes; the original 50-gene list was preserved.
- Relevant per-gene information: gene, transcript, chromosome, strand, coding-exon intervals, and coding-sequence length.
- Working candidate file on Hummingbird: `~/kelley_50gene_pilot/kelley_50gene_pilot/annotations/pilot30_candidates.tsv`.

## 2. Retrieve coding-exon alignment regions
- Alignment source: UCSC **Hiller hg38 470-way** mammalian alignment (indexed bigMaf regions).
- Selected analysis set: **53** mammalian genome assemblies.
- Used the multi-gene staging workflow, including `stage_thirty.py`, to retrieve exon-level alignment regions and save them locally.
- Observed result: **153 nonempty coding-exon files** across the 30 genes.
- Hummingbird output: `/scratch/spathare/hibernation_rer/pilot30_run1/genes/`.
- Network requests and compute-intensive fitting were separated because compute-node network requests could time out.

## 3. Filter alignments and estimate gene trees
- The extraction/fitting script used during the pilot was `extract_and_fit.py` on Hummingbird (not yet tracked on GitHub).
- **Maximum missing-data fraction:** 0.10.
- **Minimum species:** initially 35; reduced to 4 for **testing only** after TRIM52 retained 30 species.
- **Observed gene coverage:** 30–53 species per gene; the temporary 4-species minimum did not result in four-species trees.
- Fit gene-specific branch lengths using **RAxML-NG** with a fixed, pruned Hiller topology and GTR+G substitution model.
- First five successful trees: ANKRD49, INHBB, IYD, TMEM126B, TRIM52.
- Additional 25 genes completed as a batch (SLURM job 1016493). Three genes (ADNP, SAMD8, RELL2) had full 53-species coverage.

## 4. Combine and validate gene trees
- Combined 30 records (gene ID + Newick tree) into `/scratch/spathare/hibernation_rer/pilot30_combined/gene_trees_30.tsv`.
- The full 30-gene set had **53 species in the union**, **10 species in the intersection**.
- Compared nontrivial **unrooted splits** on matched species sets, using ADNP as a full-coverage topology reference.
- All 30 trees passed those preliminary topology checks; no negative, missing, or nonfinite branch lengths were found.
- These tests do **not** establish orthology, codon-frame correctness, or reliability of every evolutionary-rate estimate.

## 5. Import into RERconverge
The RERconverge import was run in a compute allocation via SLURM. Conceptual R invocation (the exact saved batch script has not yet been committed):

```r
library(RERconverge)
input <- "/scratch/spathare/hibernation_rer/pilot30_combined/gene_trees_30.tsv"
trees <- readTrees(input, minTreesAll = 3, max.read = 30)
```

**Observed:** all 30 gene trees were imported, a master tree with 53 species was built, and master-tree branch lengths were estimated from **three complete-coverage genes**. This is adequate to test whether the software executes but needs review before biological interpretation.

Saved object: `/scratch/spathare/hibernation_rer/pilot30_combined/rer30_trees.rds`.

## 6. Compute preliminary relative evolutionary-rate residuals
The successful residual run used `getAllResiduals()` with:
- `transform = "sqrt"`
- `weighted = TRUE`
- `scale = TRUE`
- `useSpecies = trees$masterTree$tip.label`

The installed function reported a default cutoff of **0.00187805**. Output: a **30 × 627** matrix stored at `/scratch/spathare/hibernation_rer/pilot30_combined/rer30_residuals.rds`.

The 627 columns are indexed **phylogenetic-path entries**, not 627 species or 627 independent lineages. Their structure and missing values need further interpretation. Recorded cell counts: **2,199 finite**, **16,088 NA**, **523 NaN**, **0 infinite**. Subsequent mapping diagnostics showed that most completely nonfinite path columns were not selected by the algorithm, but some selected paths also contain undefined values.

## 7. Reproduction and remaining work
The following are **existing working files on Hummingbird**, not verified tracked files in this GitHub repository:
- `stage_thirty.py` — multi-gene exon staging
- `extract_and_fit.py` — local alignment extraction/filtering and RAxML-NG fitting
- SLURM batch scripts for the first five and next 25 genes
- R scripts for `readTrees()` and `getAllResiduals()`

Before treating this workflow as fully reproducible from GitHub, copy and review those scripts, commit their **actual** contents, record exact command-line arguments, software versions and run commands, and keep data paths configurable. Do not commit large exon files, gene alignments, RAxML-NG scratch outputs, or RDS matrices.

**Not done:** final species-coverage decision, genome-scale analysis, hibernation association testing, candidate gene identification, and biological interpretation.
