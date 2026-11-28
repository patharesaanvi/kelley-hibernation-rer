#!/usr/bin/env Rscript
# End-to-end technical smoke test of the 30-gene binary-phenotype analysis.
# Uses preliminary hibernation classifications from config/species_metadata.tsv.
# Foreground: Hibernation; background: Non-hibernation; Conditional: NA.
# Only terminal branches are labeled; internal branches remain background (0).
# This is NOT a validated phenotype model or a biological result.

suppressPackageStartupMessages(library(RERconverge))

root <- "/scratch/spathare/hibernation_rer/pilot30_combined"
outdir <- "/scratch/spathare/hibernation_rer/pilot30_binary_smoketest"
metadata_file <- "config/species_metadata.tsv"
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

trees <- readRDS(file.path(root, "rer30_trees.rds"))
rer <- readRDS(file.path(root, "rer30_residuals.rds"))
metadata <- read.delim(metadata_file, stringsAsFactors = FALSE, check.names = FALSE)

stopifnot(is.matrix(rer))
tip_names <- trees$masterTree$tip.label
stopifnot(!anyDuplicated(tip_names))
stopifnot(!anyDuplicated(metadata$assembly_id[metadata$assembly_id != ""]))

# Match master-tree labels to assembly identifiers, never to common names.
matched <- match(tip_names, metadata$assembly_id)
if (anyNA(matched)) {
  stop("Missing metadata for master-tree tips: ",
       paste(tip_names[is.na(matched)], collapse = ", "))
}
metadata <- metadata[matched, , drop = FALSE]
state <- tolower(trimws(metadata$hibernation_status))
foreground <- state == "hibernation"
background <- state %in% c("non-hibernation", "non hibernation")
conditional <- state == "conditional"
if (any(!(foreground | background | conditional))) {
  stop("Unrecognized phenotype labels: ",
       paste(unique(metadata$hibernation_status[!(foreground | background | conditional)]),
             collapse = ", "))
}
if (sum(foreground) < 2L || sum(background) < 2L) {
  stop("Need both foreground and background species for the demonstration.")
}

classification <- data.frame(
  assembly_id = tip_names,
  common_name = metadata$common_name,
  original_status = metadata$hibernation_status,
  phenotype = ifelse(foreground, "foreground",
                     ifelse(background, "background", "excluded_conditional"))
)
write.table(classification, file.path(outdir, "phenotype_species.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
cat("Foreground:", sum(foreground), "Background:", sum(background),
    "Conditional excluded:", sum(conditional), "\n")

# Represent the phenotype on the master topology. For the technical test,
# terminal branches receive 1 (foreground), 0 (background), or NA (conditional).
# Internal branches remain 0: no ancestral hibernation transitions are assumed.
trait_tree <- trees$masterTree
trait_tree$edge.length <- rep(0, nrow(trait_tree$edge))
terminal_row <- match(seq_along(tip_names), trait_tree$edge[, 2])
stopifnot(!anyNA(terminal_row))
trait_tree$edge.length[terminal_row[foreground]] <- 1
trait_tree$edge.length[terminal_row[conditional]] <- NA_real_

# Figure 1: visualize the preliminary phenotype assignments.
pdf(file.path(outdir, "foreground_background_tree.pdf"), width = 12, height = 15)
tryCatch({
  plot(trees$masterTree, cex = 0.55,
       tip.color = ifelse(foreground, "firebrick",
                          ifelse(background, "steelblue", "gray55")),
       main = "Provisional hibernation labels: foreground / background")
  legend("topleft", legend = c("Hibernation (foreground)",
                               "Non-hibernation (background)", "Conditional (excluded)"),
         col = c("firebrick", "steelblue", "gray55"), pch = 16, bty = "n", cex = 0.75)
}, finally = dev.off())

# Turn the binary trait tree into paths compatible with the gene-tree collection.
# RERconverge walkthrough: tree2Paths(trait_tree, trees).
phenv <- tree2Paths(trait_tree, trees)
saveRDS(phenv, file.path(outdir, "hibernation_paths.rds"))
cat("Trait paths created; number of path entries:", length(phenv), "\n")
cat("Residual matrix dimensions:", paste(dim(rer), collapse = " x "), "\n")

# The path vector must be compatible with the pre-computed RER columns.
if (length(phenv) != ncol(rer)) {
  stop("Phenotype paths and residual columns have different lengths: ",
       length(phenv), " vs ", ncol(rer),
       ". Inspect path naming/mapping before running correlation.")
}

# Run the association step exactly as a technical test.
# min.sp and min.pos follow example settings from the walkthrough.
association <- correlateWithBinaryPhenotype(
  rer, phenv, min.sp = 10, min.pos = 2,
  weighted = "auto", winsorizeRER = NULL,
  winsorizetrait = NULL, bootstrap = FALSE
)
saveRDS(association, file.path(outdir, "binary_association.rds"))
write.table(as.data.frame(association),
            file.path(outdir, "binary_association.tsv"),
            sep = "\t", quote = FALSE, col.names = NA)
cat("Association table dimensions:",
    paste(dim(association), collapse = " x "), "\n")

# Figure 2: distribution of available association p-values.
if ("P" %in% colnames(association)) {
  p_values <- as.numeric(association[, "P"])\n  p <- p_values[is.finite(p_values)]
  if (length(p) > 0L) {
    pdf(file.path(outdir, "association_pvalues.pdf"), width = 8, height = 6)
    tryCatch(hist(p, breaks = 10, xlab = "Unadjusted p-value",
                  main = "30-gene pilot: exploratory binary association"),
             finally = dev.off())
  }
}

# Figure 3: attempt a gene-specific relative-rate plot for the first gene.
# Visualization may fail if path structure or missing values are unsuitable.
first_gene <- rownames(rer)[1]
if (!is.null(first_gene) && nzchar(first_gene)) {
  pdf(file.path(outdir, "example_gene_rers.pdf"), width = 12, height = 9)
  tryCatch(plotRers(rer, first_gene, phenv = phenv),
           error = function(e) {
             message("plotRers could not render: ", conditionMessage(e))
             plot.new()
             text(0.5, 0.5, paste("plotRers failed:", conditionMessage(e)),
                  cex = 0.7)
           },
           finally = dev.off())
}
cat("Technical binary-trait run finished. Files in:", outdir, "\n")
