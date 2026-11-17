
#!/usr/bin/env python3
"""Count selected Hiller mammals by taxonomic order and phenotype label.

Reads config/species_metadata.tsv and saves a tab-separated summary under
scratch/rer_results. This script does not infer taxonomy or phenotype;
it reports the labels already present in the metadata file.
Run from the repository root.
"""

import csv
import os
from collections import Counter
from pathlib import Path

# Read the curated species metadata; each row is one target species.
# DictReader lets us refer to columns by header, e.g., "mammal_group".
with open("config/species_metadata.tsv", newline="") as file:
    species = list(csv.DictReader(file, delimiter="\t"))

# Counter stores the number of species for each (group, category) pair.
counts = Counter()

for row in species:

    # Exclude target species whose metadata says they are absent from Hiller.
    if row["in_hiller"].strip().lower() != "yes":
        continue

    # Read the phenotype label used to decide which summary column to count.
    name = row["scientific_name"].strip()
    status = row["hibernation_status"].strip().lower()

    # "hibernation" is a preliminary foreground candidate, not a final
    # evolutionary foreground branch assignment. "non-hibernation" is
    # background; all other labels count as uncertain.
    if status == "hibernation":
        category = "Foreground candidate"
    elif status == "non-hibernation":
        category = "Background"
    else:
        category = "Uncertain"

    # The taxonomic order is read from metadata, not inferred by this code.
    group = row["mammal_group"].strip()
    counts[(group, category)] += 1

# Use a configurable scratch directory, rather than saving outputs in Git.
scratch = Path(os.environ.get(
    "SCRATCH_ROOT", "/scratch/spathare/hibernation_rer"
))
output = scratch / "rer_results" / "species_summary.tsv"
output.parent.mkdir(parents=True, exist_ok=True)

# Discover all taxonomic-order labels among included species.
# This avoids hardcoding a list of orders in the Python script.
groups = sorted({row["mammal_group"].strip() for row in species if row["in_hiller"].strip().lower() == "yes"})
categories = ["Foreground candidate", "Background", "Uncertain"]

# Write a TSV table: one row per mammal group and counts for each label.
with open(output, "w", newline="") as file:
    writer = csv.writer(file, delimiter="\t")
    writer.writerow(["mammal_group"] + categories + ["total"])

    for group in groups:
        values = [counts[(group, category)] for category in categories]
        writer.writerow([group] + values + [sum(values)])

# Print the same overall totals to the terminal for quick inspection.
print("Total species in Hiller:", sum(
    row["in_hiller"].strip().lower() == "yes"
    for row in species
))
print("Foreground candidates:", sum(
    counts[(g, "Foreground candidate")] for g in groups
))
print("Background candidates:", sum(
    counts[(g, "Background")] for g in groups
))
print("Uncertain:", sum(
    counts[(g, "Uncertain")] for g in groups
))

print("\nGroup summary:")
for group in groups:
    values = [counts[(group, c)] for c in categories]
    print(group, ":", values)

print("\nSummary saved to:", output)

