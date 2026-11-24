# 30-gene pilot workflow — November 24, 2026

## 1. Prepare the candidate genes
- Starting point: a larger candidate list of human **MANE** protein-coding transcripts.
- Pilot selection: first **30** candidate genes; the original 50-gene list was preserved.
- Relevant per-gene information: gene, transcript, chromosome, strand, coding-exon intervals, and coding-sequence length.
- Original candidate file on Hummingbird: `/scratch/spathare/hibernation_rer/annotations/pilot30_candidates.tsv`. The candidate list is also committed under [`annotations/pilot30_candidates.tsv`](../annotations/pilot30_candidates.tsv).

## 2. Retrieve coding-exon alignment regions
- Alignment source: UCSC **Hiller hg38 470-way** mammalian alignment (indexed bigMaf regions).
- Selected analysis set: **53** mammalian genome assemblies.
- Used the multi-gene staging workflow, including `stage_thirty.py`, to retrieve exon-level alignment regions and save them locally.
- Observed result: **153 nonempty coding-exon files** across the 30 genes.
- Hummingbird output: `/scratch/spathare/hibernation_rer/pilot30_run1/genes/`.
- Network requests and compute-intensive fitting were separated because compute-node network requests could time out.

## 3. Filter alignments and estimate gene trees
- The extraction/fitting script used during the pilot was `extract_and_fit.py` on Hummingbird; its source is now tracked at [`scripts/extract_and_fit.py`](../scripts/extract_and_fit.py).
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
The RERconverge import was run in a compute allocation via SLURM. The import script and SLURM wrapper are now committed as [`scripts/test_rer30.R`](../scripts/test_rer30.R) and [`slurm/run_rer30_test.sh`](../slurm/run_rer30_test.sh):

```r
library(RERconverge)
input <- "/scratch/spathare/hibernation_rer/pilot30_combined/gene_trees_30.tsv"
trees <- readTrees(input, minTreesAll = 3, max.read = 30)
```

**Observed:** all 30 gene trees were imported, a master tree with 53 species was built, and master-tree branch lengths were estimated from **three complete-coverage genes**. This is adequate to test whether the software executes but needs review before biological interpretation.

Saved object: `/scratch/spathare/hibernation_rer/pilot30_combined/rer30_trees.rds`.

## 6. Calculate preliminary relative evolutionary-rate residuals

The residual calculation was completed using RERconverge's `getAllResiduals()` with a square-root transformation, weighted fitting, scaling, and the species listed in the master tree. The corresponding analysis code is committed as [`scripts/calculate_rer30.R`](../scripts/calculate_rer30.R).

**Observed output:** A residual matrix containing **30 genes and 627 phylogenetic-path columns**, saved at `/scratch/spathare/hibernation_rer/pilot30_combined/rer30_residuals.rds`.

**Next step:** Understand how the phylogenetic paths are represented in this matrix and validate the results before interpreting evolutionary-rate differences. No hibernation association analysis or biological result is claimed at this stage.

## 7. Reproducibility and remaining work

**GitHub repository:** The Python scripts for candidate-gene preparation, exon staging, and gene-tree generation, along with the RERconverge analysis scripts, SLURM submission scripts, and pilot candidate gene lists, have been committed to GitHub. The SLURM scripts have been updated to use the repository's `scripts/` paths; their analysis parameters were not changed.

**Saved data and outputs:** The staged exon alignment files, gene trees, and RERconverge output files remain stored on Hummingbird. These large computational outputs have not been uploaded to GitHub.

**Remaining reproducibility work:** Verify the updated SLURM launch paths and required input dependencies, document the software environment and run commands, and establish that the workflow can be reproduced using the repository. `stage_thirty.py` still uses fixed Hummingbird scratch paths. The separately rerun TRIM52 wrapper references `$SCRATCH/annotations/TRIM52_only.tsv`, which is not currently tracked in GitHub; that input needs to be included or its generation documented. Some output files use exclusive creation, so a rerun may require a fresh output directory. The updated wrappers have not yet been independently executed on Hummingbird.

**Next research steps:** Understand and validate the 627 phylogenetic-path columns before interpreting evolutionary-rate differences. Subsequent work includes deciding final species-coverage criteria, scaling the analysis to additional genes, testing evolutionary-rate associations with hibernation, and interpreting any supported biological findings.
