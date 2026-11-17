# Check whether RAxML-NG preserved the Hiller branching relationships.
library(ape)
args <- commandArgs(trailingOnly=TRUE)
base <- if (length(args)) args[1] else "/scratch/spathare/hibernation_rer/gene_trees"
hiller <- read.tree(file.path(base, "HBB_pruned_topology.nwk"))
hbb <- read.tree(file.path(base, "HBB_test.raxml.bestTree"))

# Compare assembly IDs without requiring the same order.
print(c(Hiller=length(hiller$tip.label), HBB=length(hbb$tip.label)))
print(setequal(hiller$tip.label, hbb$tip.label))
# Ignore rooting and length differences because we only want the topology.
print(all.equal(unroot(hiller), unroot(hbb), use.edge.length=FALSE))
print(c(Hiller_rooted=is.rooted(hiller), HBB_rooted=is.rooted(hbb)))
print(c(Hiller_binary=is.binary(hiller), HBB_binary=is.binary(hbb)))
print(c(Hiller_unrooted_binary=is.binary(unroot(hiller)),
        HBB_unrooted_binary=is.binary(unroot(hbb))))
