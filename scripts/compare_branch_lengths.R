# Compare the original HBB fit with the relaxed missing-data fit.
library(ape)
args <- commandArgs(trailingOnly=TRUE)
base <- if (length(args)) args[1] else "/scratch/spathare/hibernation_rer/gene_trees"
old <- unroot(read.tree(file.path(base, "HBB_test.raxml.bestTree")))
new <- unroot(read.tree(file.path(base, "HBB_10pct.raxml.bestTree")))
stopifnot(all(old$tip.label %in% new$tip.label))
# Prune AFTER the 51-species fit, preserving summed path lengths.
new <- unroot(keep.tip(new, old$tip.label))
stopifnot(setequal(old$tip.label, new$tip.label),
          isTRUE(all.equal(old, new, use.edge.length=FALSE)))

# Compare each unique tip-to-tip distance, not the diagonal or duplicates.
d1 <- cophenetic.phylo(old)
d2 <- cophenetic.phylo(new)[rownames(d1), colnames(d1)]
upper <- upper.tri(d1)
summarize <- function(a,b) {
  c(n=length(a), correlation=cor(a,b), mean_abs=mean(abs(a-b)),
    max_abs=max(abs(a-b)))
}
print(summarize(d1[upper], d2[upper]))

# Label each unrooted edge by its two sets of tips, independent of node numbering.
split_lengths <- function(tree) {
  descendants <- function(node) {
    if (node <= Ntip(tree)) return(tree$tip.label[node])
    unlist(lapply(tree$edge[tree$edge[,1]==node,2], descendants),
           use.names=FALSE)
  }
  keys <- vapply(tree$edge[,2], function(node) {
    side <- descendants(node)
    left <- paste(sort(side), collapse=",")
    right <- paste(sort(setdiff(tree$tip.label, side)), collapse=",")
    paste(sort(c(left,right)), collapse="|")
  }, character(1))
  stopifnot(!anyDuplicated(keys))
  setNames(tree$edge.length, keys)
}
a <- split_lengths(old)
b <- split_lengths(new)
stopifnot(setequal(names(a), names(b)))
print(summarize(a, b[names(a)]))
