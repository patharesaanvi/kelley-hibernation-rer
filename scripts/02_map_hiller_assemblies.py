
#!/usr/bin/env python3
"""Map Hiller 470 scientific-name tree tips to assembly IDs."""

import csv
import os
from collections import Counter
from pathlib import Path
from Bio import Phylo

scratch = Path(os.environ["SCRATCH_ROOT"])
tree_dir = scratch / "raw_alignments" / "hiller470"

scientific_tree = Phylo.read(
    tree_dir / "hg38.470way.scientificNames.nh", "newick"
)
assembly_tree = Phylo.read(
    tree_dir / "hg38.470way.nh", "newick"
)

def same_structure(a, b):
    """Check topology and corresponding branch lengths recursively."""
    if len(a.clades) != len(b.clades):
        return False
    if a.is_terminal() != b.is_terminal():
        return False
    if a.branch_length != b.branch_length:
        return False
    return all(
        same_structure(x, y)
        for x, y in zip(a.clades, b.clades)
    )

if not same_structure(scientific_tree.root, assembly_tree.root):
    raise ValueError(
        "Tree structure or branch lengths differ. "
        "Cannot safely pair species and assembly IDs."
    )

mapping = []

def pair_tips(scientific_node, assembly_node):
    if scientific_node.is_terminal():
        mapping.append({
            "scientific_name": scientific_node.name,
            "assembly_id": assembly_node.name
        })
        return

    for s, a in zip(scientific_node.clades, assembly_node.clades):
        pair_tips(s, a)

pair_tips(scientific_tree.root, assembly_tree.root)

output = scratch / "rer_results" / "hiller_assembly_mapping.tsv"
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=["scientific_name", "assembly_id"],
        delimiter="\t"
    )
    writer.writeheader()
    writer.writerows(mapping)

counts = Counter(row["scientific_name"] for row in mapping)

print("Total assembly tips:", len(mapping))
print("Unique scientific labels:", len(counts))
print("\nRepeated species labels:")

for name, count in sorted(counts.items()):
    if count > 1:
        assemblies = [
            row["assembly_id"]
            for row in mapping
            if row["scientific_name"] == name
        ]
        print(f"{name}: {', '.join(assemblies)}")

print("\nMapping saved to:", output)
