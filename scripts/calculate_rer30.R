# Calculate preliminary relative evolutionary-rate residuals.
# Input: the RERconverge tree collection saved by test_rer30.R.
# Output: rer30_residuals.rds (gene-by-path residual matrix).
library(RERconverge)

root <- "/scratch/spathare/hibernation_rer/pilot30_combined"

trees <- readRDS(file.path(root, "rer30_trees.rds"))

cat("=== Starting relative-rate calculation ===\n")

cat("Gene trees:", length(trees$trees), "\n")

cat("Species:", length(trees$masterTree$tip.label), "\n")

# Use the parameters supported by the installed version.
# Parameter names differ across RERconverge versions; inspect the
# installed function so weighting and scaling use supported arguments.
args <- names(formals(getAllResiduals))

# Transform branch lengths with square root and use master-tree tips.
settings <- list(
  trees,
  useSpecies = trees$masterTree$tip.label,
  transform = "sqrt"
)

if ("weighted" %in% args) {
  settings$weighted <- TRUE
} else if ("use.weights" %in% args) {
  settings$use.weights <- TRUE
}

if ("scale" %in% args) {
  settings$scale <- TRUE
} else if ("norm" %in% args) {
  settings$norm <- "scale"
}

cat("=== Calculating residuals ===\n")

# Compute residuals; these are not hibernation-association statistics.
rer <- do.call(getAllResiduals, settings)

cat("=== Results ===\n")

cat("Object class:", class(rer), "\n")
cat("Dimensions:", paste(dim(rer), collapse = " x "), "\n")

if (is.matrix(rer)) {
  cat("Finite values:", sum(is.finite(rer)), "\n")
  cat("Missing/nonfinite values:", sum(!is.finite(rer)), "\n")
}

saveRDS(rer, file.path(root, "rer30_residuals.rds"))

cat("SUCCESS: Residual calculation completed\n")
