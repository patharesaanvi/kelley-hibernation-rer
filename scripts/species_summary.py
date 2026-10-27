
#!/usr/bin/env python3
"""Summarize mammal groups in our Hiller species metadata."""

import csv
import os
from collections import Counter
from pathlib import Path

# Read the current species metadata table
with open("config/species_metadata.tsv", newline="") as file:
    species = list(csv.DictReader(file, delimiter="\t"))

counts = Counter()

for row in species:

    # Only include species available in Hiller 470
    if row["in_hiller"].strip().lower() != "yes":
        continue

    name = row["scientific_name"].strip()
    status = row["hibernation_status"].strip().lower()

    # Classify from the reviewed phenotype field, not a fixed name list
    if status == "hibernation":
        category = "Foreground candidate"
    elif status == "non-hibernation":
        category = "Background"
    else:
        category = "Uncertain"

    # Use the explicitly assigned group in species_metadata.tsv
    group = row["mammal_group"].strip()
    counts[(group, category)] += 1

# Save the summary in scratch
scratch = Path(os.environ.get(
    "SCRATCH_ROOT", "/scratch/spathare/hibernation_rer"
))
output = scratch / "rer_results" / "species_summary.tsv"
output.parent.mkdir(parents=True, exist_ok=True)

# Use the taxonomic orders present in metadata rather than a fixed group list
groups = sorted({row["mammal_group"].strip() for row in species if row["in_hiller"].strip().lower() == "yes"})
categories = ["Foreground candidate", "Background", "Uncertain"]

with open(output, "w", newline="") as file:
    writer = csv.writer(file, delimiter="\t")
    writer.writerow(["mammal_group"] + categories + ["total"])

    for group in groups:
        values = [counts[(group, category)] for category in categories]
        writer.writerow([group] + values + [sum(values)])

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

