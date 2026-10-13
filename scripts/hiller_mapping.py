#!/usr/bin/env python3
"""Match our target species to Hiller 470 genome assemblies."""

import csv
import os
import shutil
from pathlib import Path
from collections import defaultdict
from Bio import Phylo

scratch = Path(os.environ.get(
    "SCRATCH_ROOT", "/scratch/spathare/hibernation_rer"
))
tree_dir = scratch / "raw_alignments" / "hiller470"
metadata_file = Path("config/species_metadata.tsv")
results_dir = scratch / "rer_results"

# Read the two Hiller trees
species_tree = Phylo.read(
    tree_dir / "hg38.470way.scientificNames.nh", "newick"
)
assembly_tree = Phylo.read(
    tree_dir / "hg38.470way.nh", "newick"
)


def same_tree(a, b):
    # Make sure the trees have matching branches
    if len(a.clades) != len(b.clades):
        return False
    if a.branch_length != b.branch_length:
        return False

    return all(
        same_tree(x, y)
        for x, y in zip(a.clades, b.clades)
    )


if not same_tree(species_tree.root, assembly_tree.root):
    raise ValueError("Hiller trees do not match")

# Pair scientific names with assembly IDs
species_tips = species_tree.get_terminals()
assembly_tips = assembly_tree.get_terminals()

mapping = defaultdict(list)

for species, assembly in zip(species_tips, assembly_tips):
    mapping[species.name].append(assembly.name)

# Save the complete Hiller mapping in scratch
results_dir.mkdir(parents=True, exist_ok=True)

with open(results_dir / "hiller_assembly_mapping.tsv", "w") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["scientific_name", "assembly_id"])

    for name, assemblies in mapping.items():
        for assembly in assemblies:
            writer.writerow([name, assembly])

# Read our target species table
with open(metadata_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    columns = reader.fieldnames
    rows = list(reader)

# Keep a copy of the original table in scratch
backup = results_dir / "species_metadata_backup.tsv"
if not backup.exists():
    shutil.copy2(metadata_file, backup)

updated = 0
missing = []
multiple = []

for row in rows:
    name = row["scientific_name"].strip().replace(" ", "_")

    # Find exact species matches and subspecies matches
    matches = []

    for hiller_name, assemblies in mapping.items():
        if hiller_name == name or hiller_name.startswith(name + "_"):
            matches.extend(assemblies)

    matches = sorted(set(matches))

    # Record whether this species is represented in Hiller
    row["in_hiller"] = "Yes" if matches else "No"

    # Only fill missing IDs when there is one choice
    if len(matches) == 1:
        if row["assembly_id"].strip().lower() in {"", "pending"}:
            row["assembly_id"] = matches[0]
            updated += 1

    elif len(matches) > 1:
        multiple.append((name, matches))

    else:
        missing.append(name)
        row["assembly_id"] = ""

# Save the updated species metadata
with open(metadata_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

print("Total target species:", len(rows))
print("Species found:", len(rows) - len(missing))
print("Species missing:", len(missing))
print("Assembly IDs newly filled:", updated)

print("\nSpecies with multiple assemblies:")
for name, assemblies in multiple:
    print(name, ":", ", ".join(assemblies))

print("\nSpecies not found:")
for name in missing:
    print("-", name)
