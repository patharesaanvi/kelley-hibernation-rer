
#!/usr/bin/env python3
"""Check the species metadata table for missing or incomplete information."""

import csv
import sys

# Columns expected in the species metadata file
REQUIRED = [
    "common_name",
    "scientific_name",
    "assembly_id",
    "in_hiller",
    "hibernation_status",
    "notes"
]


def main(filename):

    # Read the species metadata TSV file
    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")

        # Check that all required columns are included
        missing = set(REQUIRED) - set(reader.fieldnames or [])

        if missing:
            print("Missing columns:", ", ".join(sorted(missing)))
            return 1

        species = list(reader)

    print("Total species:", len(species))

    # Check if any species appear more than once
    names = [row["scientific_name"].strip() for row in species]
    duplicates = sorted({name for name in names if names.count(name) > 1})

    if duplicates:
        print("Duplicate species:", ", ".join(duplicates))

    # Check which species have missing or pending assembly IDs
    pending = []

    for row in species:
        if row["in_hiller"].strip().lower() == "yes":
            if row["assembly_id"].strip().lower() in {"", "pending"}:
                pending.append(row["scientific_name"])

    print("\nSpecies with pending assembly IDs:")
    for name in pending:
        print("-", name)

    # Identify species whose hibernation status still needs review
    review = []

    for row in species:
        status = row["hibernation_status"].strip().lower()

        if status in {"", "unverified", "conditional", "nonstandard"}:
            review.append(row["scientific_name"])

    print("\nSpecies requiring phenotype review:")
    for name in review:
        print("-", name)

    print("\nMetadata check completed.")
    print("Pending assembly IDs:", len(pending))
    print("Phenotypes requiring review:", len(review))

    return 1 if duplicates or pending or review else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(
            "Usage: python3 scripts/check_species_table.py "
            "config/species_metadata.tsv"
        )

    sys.exit(main(sys.argv[1]))
