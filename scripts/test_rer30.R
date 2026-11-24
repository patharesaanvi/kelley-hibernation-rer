# Import the completed pilot gene trees into RERconverge.
# Input: gene_trees_30.tsv (gene ID plus Newick tree per row).
# Output: rer30_trees.rds (RERconverge tree collection).
library(RERconverge)

root <- "/scratch/spathare/hibernation_rer"

input <- file.path(root, "pilot30_combined/gene_trees_30.tsv")

outdir <- file.path(root, "pilot30_combined")

cat("=== Reading 30 gene trees ===\n")

# Build a common reference for the 30 gene trees. minTreesAll=3
# permits a master tree from species represented by enough input trees.
trees <- readTrees(
  input,
  minTreesAll = 3,
  max.read = 30
)

cat("=== Import summary ===\n")

cat("Gene trees imported:", length(trees$trees), "\n")

cat("Master tree species:", length(trees$masterTree$tip.label), "\n")

# Fail early if the expected 30 trees or 53-species master tree are missing.
stopifnot(length(trees$trees) == 30)

stopifnot(length(trees$masterTree$tip.label) == 53)

saveRDS(trees, file.path(outdir, "rer30_trees.rds"))

cat("SUCCESS: RERconverge tree import completed\n")
