
#!/usr/bin/env python3
"""Check the species metadata before analysis."""

import csv

file = "config/species_metadata.tsv"

# Read the species table
with open(file, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

names = []
pending = []
review = []

# Check each species
for row in rows:
    name = row["scientific_name"].strip()
    names.append(name)

    assembly = row["assembly_id"].strip().lower()
    in_hiller = row["in_hiller"].strip().lower()
    status = row["hibernation_status"].strip().lower()

    # Check for missing assembly IDs
    if in_hiller == "yes" and assembly in {"", "pending"}:
        pending.append(name)

    # Check for phenotypes needing review
    if status not in {"hibernation", "daily torpor", "non"}:
        review.append(name)

# Check for duplicate species
duplicates = sorted({
    name for name in names if names.count(name) > 1
})

print("Total species:", len(rows))
print("Duplicate species:", duplicates)

print("\nPending assembly IDs:")
for name in pending:
    print("-", name)

print("\nPhenotypes needing review:")
for name in review:
    print("-", name)

print("\nPending assemblies:", len(pending))
print("Phenotypes to review:", len(review))

if duplicates or pending or review:
    print("\nMetadata still needs review.")
else:
    print("\nNo issues detected by these checks.")
