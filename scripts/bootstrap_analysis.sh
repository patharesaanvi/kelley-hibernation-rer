#!/usr/bin/env bash
# Reproduce the HBB bootstrap pilot. Run in a compute allocation on Hummingbird.
set -euo pipefail
module load raxml-ng/1.2.0
SCRATCH="${1:-/scratch/spathare/hibernation_rer}"
# Use a new output prefix so the original pilot files are not overwritten.
PREFIX="${2:-$SCRATCH/gene_trees/HBB_bootstrap_recheck}"
# Resample alignment columns and infer each tree without fixing the topology.
raxml-ng --bootstrap --msa "$SCRATCH/gene_alignments/HBB_complete_CDS.fasta" \
  --model GTR+G --bs-trees 100 --seed 42 --threads 2 --prefix "$PREFIX"
# Measure how often the splits in the original fixed tree were recovered.
raxml-ng --support --tree "$SCRATCH/gene_trees/HBB_test.raxml.bestTree" \
  --bs-trees "$PREFIX.raxml.bootstraps" --bs-metric fbp --threads 2 \
  --prefix "${PREFIX}_support"
# Plot the fixed tree with bootstrap values and print its summary statistics.
module load ohpc
module load rerconverge/0.3.0
Rscript - "${PREFIX}_support.raxml.support" "${PREFIX}_support.png" <<'RS'
library(ape)
args <- commandArgs(trailingOnly=TRUE)
tree <- read.tree(args[1])
values <- as.numeric(tree$node.label)
values <- values[is.finite(values)]
print(c(n=length(values), mean=mean(values), median=median(values),
        min=min(values), max=max(values), ge70=sum(values>=70), ge95=sum(values>=95)))
png(args[2], width=2600, height=3200, res=200)
plot(tree, cex=0.65, main="HBB Gene Tree - Bootstrap Support")
nodelabels(tree$node.label, frame="none", cex=0.6, col="blue")
add.scale.bar()
dev.off()
RS
