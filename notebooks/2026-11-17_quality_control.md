# Lab notebook — November, 2026

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
module load ohpc
module load rerconverge/0.3.0
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

To compare the existing trees:

```bash
module load ohpc
module load rerconverge/0.3.0
Rscript scripts/compare_branch_lengths.R
```

The reference-gap, topology and one-gene RERconverge checks are kept below as notebook code instead of separate scripts.

## Saved results

### Bootstrap results

| Metric | Value |
| --- | ---: |
| `replicates` | 100 |
| `internal_splits` | 43 |
| `mean_support_percent` | 55.58 |
| `median_support_percent` | 53 |
| `minimum_support_percent` | 2 |
| `maximum_support_percent` | 100 |
| `support_ge70_count` | 16 |
| `support_ge95_count` | 11 |

### Missing-data comparison (0% vs 10%)

| Metric | Value |
| --- | ---: |
| `strict_species` | 46 |
| `relaxed_species` | 51 |
| `relaxed_max_missing_fraction` | 0.10 |
| `common_species` | 46 |
| `pairwise_distance_count` | 1035 |
| `pairwise_distance_correlation` | 0.9970543 |
| `pairwise_distance_mean_absolute_difference` | 0.006230502 |
| `pairwise_distance_max_absolute_difference` | 0.031482 |
| `matched_branch_count` | 89 |
| `branch_length_correlation` | 0.9970099 |
| `branch_length_mean_absolute_difference` | 0.001681562 |
| `branch_length_max_absolute_difference` | 0.012494 |
| `strict_near_zero_count` | 7 |
| `relaxed_near_zero_count` | 7 |
- [Detailed pilot notes](../docs/hbb_pilot.md)

The summary values were copied from the recorded pilot results; they were not newly calculated when this summary was added.

## Questions / to do

- Finish checking species metadata, unusual sequences, coding frame/internal stops and HBB orthology.
- Identify the seven near-zero branches and see if they are the same in both fits.
- Look into how RERconverge assigns master-tree branch lengths and compare the imported gene-tree branches individually.
- Decide on a missing-data threshold and whether to continue with GTR+G or use model selection. Consider whether to bootstrap every gene or a subset.
- Automate the workflow and try around 50 orthologous genes before scaling up. This is a proposed pilot size, not a minimum requirement.

No hibernation-associated rate shifts have been identified yet.

## Exploratory checks — saved code

I kept these one-time HBB checks here to keep the scripts folder focused on the main pipeline. The code is preserved as written; it has not been rerun on Hummingbird in this form. Run from the repository root with the appropriate Python or R environment.

### Reference-gap check

Counts reference-gap columns in the three extracted MAF files.

```python
"""Count human-reference gap columns in the three extracted HBB MAF files."""
import argparse
import csv
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--scratch", type=Path, default=Path("/scratch/spathare/hibernation_rer"))
p.add_argument("--metadata", type=Path, default=Path("config/species_metadata.tsv"))
args = p.parse_args()

# Only count nucleotide calls from assemblies selected for our project.
with args.metadata.open() as f:
    selected = {r["assembly_id"] for r in csv.DictReader(f, delimiter="\t")
                if r["in_hiller"].strip().lower() == "yes"}

def blocks(path):
    """Yield the sequence rows from each MAF alignment block."""
    block = []
    with path.open() as f:
        for line in f:
            fields = line.split()
            if not fields or fields[0] == "a":
                if block:
                    yield block
                    block = []
            elif fields[0] == "s":
                block.append(fields)
    if block:
        yield block

total = [0, 0, 0, 0]
for start, end in [(5225597, 5225726), (5226576, 5226799), (5226929, 5227021)]:
    counts = [0, 0, 0, 0]
    path = args.scratch / "gene_alignments" / f"HBB_{start}_{end}.maf"
    for block in blocks(path):
        ref = next((r for r in block if r[1].split(".")[0] == "hg38"), None)
        if ref is None:
            continue
        if ref[4] != "+":
            raise ValueError("Expected positive-strand hg38 MAF reference")
        pos = int(ref[2])
        mammals = [r[6].upper() for r in block
                   if r[1].split(".")[0] in selected and r is not ref]
        # The reference coordinate advances only when hg38 has a base.
        for i, base in enumerate(ref[6]):
            if base != "-":
                pos += 1
                continue
            internal = start < pos < end
            has_base = any(seq[i] in "ACGT" for seq in mammals)
            counts[0] += 1
            counts[1] += int(internal)
            counts[2] += int(has_base)
            counts[3] += int(internal and has_base)
    total = [a+b for a,b in zip(total, counts)]
    print(start, end, counts)
# These are column occurrences, not verified biological insertion events.
print("Total gaps, internal gaps, selected calls, internal selected calls:", total)
```

### Tree topology and polytomy check

Checks matching species, unrooted topology and binary branching.

```r
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
```

### Single-gene RERconverge test

Imports HBB and attempts residual calculation; the original test returned a matrix-dimension error.

```r
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
```
