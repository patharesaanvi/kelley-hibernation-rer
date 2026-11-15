#!/usr/bin/env python3
"""Check the species metadata before analysis.

This script reports possible metadata problems; it does not edit the table.
Run it from the root of the GitHub repository.
"""

import csv  # Read the tab-separated metadata file

file = "config/species_metadata.tsv"

# Each row is a species; DictReader uses column names as dictionary keys.
with open(file, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

# Keep separate lists so we can report each type of issue at the end.
names = []
pending = []
review = []
availability_review = []

# Go through the metadata one species at a time.
for row in rows:
    # Use the scientific name to identify this species in the report.
    name = row["scientific_name"].strip()
    names.append(name)

    # Remove extra spaces and ignore capitalization when checking values.
    assembly = row["assembly_id"].strip().lower()
    in_hiller = row["in_hiller"].strip().lower()
    status = row["hibernation_status"].strip().lower()

    # The Hiller availability column should only say Yes or No.
    if in_hiller not in {"yes", "no"}:
        availability_review.append(name)

    # Species marked as present in Hiller should have an assembly ID.
    if in_hiller == "yes" and assembly in {"", "pending"}:
        pending.append(name)

    # Flag any hibernation-status label outside the accepted set below.
    # A flagged label needs review; it does not automatically mean it is wrong.
    if status not in {"hibernation", "non-hibernation", "daily torpor", "non"}:
        review.append(name)

# Find scientific names that appear more than once in the metadata.
duplicates = sorted({
    name for name in names if names.count(name) > 1
})

# Print the checks to the terminal; this script does not save a results file.
print("Total species:", len(rows))
print("Duplicate species:", duplicates)

print("\nHiller availability needing review:")
for name in availability_review:
    print("-", name)

print("\nPending assembly IDs:")
for name in pending:
    print("-", name)

print("\nPhenotypes needing review:")
for name in review:
    print("-", name)

print("\nHiller availability needing review:", len(availability_review))
print("Pending assemblies:", len(pending))
print("Phenotypes to review:", len(review))

# If any check found an issue, remind us to review the metadata.
if duplicates or pending or review or availability_review:
    print("\nMetadata still needs review.")
else:
    print("\nNo issues detected by these checks.")
