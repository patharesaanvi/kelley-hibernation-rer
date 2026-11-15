#!/usr/bin/env python3
"""Match target species to assembly IDs in the Hiller 470-way trees.

This script reads two differently labeled versions of the Hiller tree,
uses corresponding tip positions to associate scientific names with assembly
IDs, and updates availability and some IDs in config/species_metadata.tsv.
Run it from the repository root. It writes to the metadata file, so review
changes before committing them.
"""

import csv
import os
import shutil
from pathlib import Path
from collections import defaultdict
from Bio import Phylo

# Use SCRATCH_ROOT if provided; otherwise use the project scratch directory.
scratch = Path(os.environ.get(
    "SCRATCH_ROOT", "/scratch/spathare/hibernation_rer"
))
# Location of the Hiller tree files and the metadata table to update.
tree_dir = scratch / "raw_alignments" / "hiller470"
metadata_file = Path("config/species_metadata.tsv")
# Save mapping reports and the first metadata backup here.
results_dir = scratch / "rer_results"

# The scientific-name and assembly-ID trees should have corresponding tips.
# Newick is the text format used to represent each phylogenetic tree.
species_tree = Phylo.read(
    tree_dir / "hg38.470way.scientificNames.nh", "newick"
)
assembly_tree = Phylo.read(
    tree_dir / "hg38.470way.nh", "newick"
)


def same_tree(a, b):
# Compare the branching structure and branch lengths recursively.
    # This does not compare tip names or independently prove correct tip labels.
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

# Pair tips by their traversal order after checking the tree structure.
# This assumes the two source trees label the same tips in the same order.
species_tips = species_tree.get_terminals()
assembly_tips = assembly_tree.get_terminals()

# A scientific name can map to more than one genome assembly.
mapping = defaultdict(list)

for species, assembly in zip(species_tips, assembly_tips):
    mapping[species.name].append(assembly.name)

# Write the full scientific-name/assembly-ID mapping for later inspection.
results_dir.mkdir(parents=True, exist_ok=True)

with open(results_dir / "hiller_assembly_mapping.tsv", "w") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["scientific_name", "assembly_id"])

    for name, assemblies in mapping.items():
        for assembly in assemblies:
            writer.writerow([name, assembly])

# Read the project metadata, including the original column order.
with open(metadata_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    columns = reader.fieldnames
    rows = list(reader)

# Create a backup only if one does not already exist.
# Re-running the script does not replace that earlier backup.
backup = results_dir / "species_metadata_backup.tsv"
if not backup.exists():
    shutil.copy2(metadata_file, backup)

# Track how many IDs were newly filled and which species need attention.
updated = 0
missing = []
multiple = []

for row in rows:
# Hiller tip names use underscores instead of spaces in scientific names.
    name = row["scientific_name"].strip().replace(" ", "_")

# Match either the exact scientific name or names beginning with it
    # followed by an underscore (potential subspecies or extra suffixes).
    # These matches still need biological/taxonomic verification.
    matches = []

    for hiller_name, assemblies in mapping.items():
        if hiller_name == name or hiller_name.startswith(name + "_"):
            matches.extend(assemblies)

# Remove repeated assembly IDs and keep their order predictable.
    matches = sorted(set(matches))

# Set availability based on whether any name matches were found.
    row["in_hiller"] = "Yes" if matches else "No"

# If there is one match, fill the ID only when the existing field
    # is blank or says pending; existing IDs are not checked or replaced.
    if len(matches) == 1:
        if row["assembly_id"].strip().lower() in {"", "pending"}:
            row["assembly_id"] = matches[0]
            updated += 1

# Multiple matches are recorded for manual review; no ID is chosen.
    elif len(matches) > 1:
        multiple.append((name, matches))

# No Hiller name match: report species and clear its assembly ID.
    else:
        missing.append(name)
        row["assembly_id"] = ""

# Overwrite the local metadata file with updated availability/IDs.
# This operation changes a repository file, unlike check_species.py.
with open(metadata_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

# Summarize the matching results in the terminal.
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
