library(RERconverge)

root <- "/scratch/spathare/hibernation_rer"

input <- file.path(root, "pilot30_combined/gene_trees_30.tsv")

outdir <- file.path(root, "pilot30_combined")

cat("=== Reading 30 gene trees ===\n")

trees <- readTrees(
  input,
  minTreesAll = 3,
  max.read = 30
)

cat("=== Import summary ===\n")

cat("Gene trees imported:", length(trees$trees), "\n")

cat("Master tree species:", length(trees$masterTree$tip.label), "\n")

stopifnot(length(trees$trees) == 30)

stopifnot(length(trees$masterTree$tip.label) == 53)

saveRDS(trees, file.path(outdir, "rer30_trees.rds"))

cat("SUCCESS: RERconverge tree import completed\n")
