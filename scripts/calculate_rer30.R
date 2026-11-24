library(RERconverge)

root <- "/scratch/spathare/hibernation_rer/pilot30_combined"

trees <- readRDS(file.path(root, "rer30_trees.rds"))

cat("=== Starting relative-rate calculation ===\n")

cat("Gene trees:", length(trees$trees), "\n")

cat("Species:", length(trees$masterTree$tip.label), "\n")

# Use the parameters supported by the installed version.
args <- names(formals(getAllResiduals))

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
