# Reproduce the one-gene import and residual test, not a phenotype analysis.
library(ape)
library(RERconverge)
args <- commandArgs(trailingOnly=TRUE)
base <- if (length(args)) args[1] else "/scratch/spathare/hibernation_rer/gene_trees"
master <- read.tree(file.path(base, "HBB_pruned_topology.nwk"))
trees <- readTrees(file.path(base, "hiller_hibernation_gene_trees.tsv"),
                   max.read=1, masterTree=master, minSpecs=46)
# This is a technical test. The original run failed at the residual step;
# more genes are needed before interpreting relative rates.
rer <- getAllResiduals(trees, useSpecies=master$tip.label)
print(dim(rer))
