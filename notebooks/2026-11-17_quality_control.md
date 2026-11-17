# Lab notebook — November 17, 2026

## Progress made

- I added more comments to the original Python scripts so it is easier to understand what each section does.
- I reviewed several hibernation classifications. Some mammals use daily torpor or hibernate only under certain conditions, so the full species list still needs to be verified.
- I checked if skipping human-reference gap columns removed coding information. Of 129 gap-column occurrences, 13 had bases from our selected mammals, but none were strictly inside the chosen HBB coding intervals.
- I compared the original pruned Hiller tree with the HBB tree. Both had the same 46 species and unrooted topology. Both were binary, although short branches in the plot look like polytomies.
- I ran 100 bootstrap replicates to see how well HBB independently supports the evolutionary splits. Average support was 55.58%; 16/43 splits had support >=70% and 11/43 had support >=95%. The bear clade had 100% support, but its internal splits had support of 33% and 16%.
- I tested a 10% missing-nucleotide threshold instead of removing every sequence containing an N. This brought the alignment from 46 to 51 species. After fitting the new tree, I pruned it back to the original 46 species to compare the same branches. Pairwise distance correlation was 0.9970543 and individual branch-length correlation was 0.9970099. Both original fitted trees had seven near-zero branches. This suggests the relaxed threshold is reasonable for HBB, but I still need to test other genes and thresholds.
- I tried running getAllResiduals() with the single HBB tree. The import worked but the residual calculation returned a matrix-dimension error. I still need to establish background evolutionary rates using additional genes.

## Reproducing the checks

Run from the repository folder on Hummingbird. The new scripts reconstruct the terminal analyses as reusable files; they have not yet been rerun on Hummingbird as standalone scripts.

```bash
cd ~/kelley-hibernation-rer
SCRATCH=/scratch/spathare/hibernation_rer
python3 scripts/check_reference_gaps.py
module load ohpc
module load rerconverge/0.3.0
Rscript scripts/check_tree_topology.R
```

For the bootstrap analysis, use a compute allocation and run:

```bash
bash scripts/bootstrap_analysis.sh
```

The script uses a separate output prefix to avoid overwriting the original results. The original bootstrap outputs are in scratch under gene_trees/ (HBB_bootstrap.raxml.bootstraps and HBB_support.raxml.support). The original figures are figures/HBB_gene_tree.png and figures/HBB_bootstrap_tree.png.

To recreate the relaxed-filter alignment without overwriting existing data:

```bash
python3 scripts/filter_missing_data.py \
  "$SCRATCH/gene_alignments/HBB_53species_CDS.fasta" \
  "$SCRATCH/gene_alignments/HBB_10pct_recheck.fasta" --threshold 0.10
```

The original 51-species fit used HBB_10pct_missing_CDS.fasta and HBB_10pct_topology.nwk with the following command (already run; use a different prefix if repeating):

```bash
module load raxml-ng/1.2.0
raxml-ng --evaluate \
  --msa "$SCRATCH/gene_alignments/HBB_10pct_missing_CDS.fasta" \
  --tree "$SCRATCH/gene_trees/HBB_10pct_topology.nwk" \
  --model GTR+G --prefix "$SCRATCH/gene_trees/HBB_10pct" --threads 2
```

To compare the existing trees and reproduce the one-gene import test:

```bash
module load ohpc
module load rerconverge/0.3.0
Rscript scripts/compare_branch_lengths.R
Rscript scripts/test_rerconverge.R
```

The last command is expected to reproduce the original residual error if the same inputs and environment are used. It is not an association test.

## Saved results

- [Bootstrap summary](../results/HBB_bootstrap_summary.tsv)
- [Missing-data comparison](../results/HBB_missing_data_comparison.tsv)
- [Detailed pilot notes](../docs/hbb_pilot.md)

The summary values were copied from the recorded pilot results; they were not newly calculated when these files were added.

## Questions / to do

- Finish checking species metadata, unusual sequences, coding frame/internal stops and HBB orthology.
- Identify the seven near-zero branches and see if they are the same in both fits.
- Look into how RERconverge assigns master-tree branch lengths and compare the imported gene-tree branches individually.
- Decide on a missing-data threshold and whether to continue with GTR+G or use model selection. Consider whether to bootstrap every gene or a subset.
- Automate the workflow and try around 50 orthologous genes before scaling up. This is a proposed pilot size, not a minimum requirement.

No hibernation-associated rate shifts have been identified yet.
