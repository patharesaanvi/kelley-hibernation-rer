
#!/usr/bin/env python3
"""Fill in missing assembly IDs using the Hiller 470 mapping."""

import csv
import shutil
from pathlib import Path

# Input files
mapping_file = Path(
    "/scratch/spathare/hibernation_rer/rer_results/"
    "hiller_assembly_mapping.tsv"
)

metadata_file = Path("config/species_metadata.tsv")
backup_file = Path("config/species_metadata.backup.tsv")


# Read the Hiller assembly mappings
with open(mapping_file, newline="", encoding="utf-8") as file:
    mapping = list(csv.DictReader(file, delimiter="\t"))

# Read our species metadata
with open(metadata_file, newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter="\t")
    columns = reader.fieldnames
    species = list(reader)

# Save a backup before making changes
shutil.copy2(metadata_file, backup_file)

updated = 0
unresolved = []

for row in species:

    # Only update species that are present in Hiller
    if row["in_hiller"].strip().lower() != "yes":
        continue

    # Keep assembly IDs that have already been assigned
    if row["assembly_id"].strip().lower() not in {"", "pending"}:
        continue

    # Convert spaces to underscores to match Hiller names
    name = row["scientific_name"].strip().replace(" ", "_")

    matches = []

    for entry in mapping:
        hiller_name = entry["scientific_name"].strip()

        # Match exact species names or their subspecies
        if hiller_name == name or hiller_name.startswith(name + "_"):
            matches.append(entry["assembly_id"].strip())

    matches = sorted(set(matches))

    if len(matches) == 1:
        row["assembly_id"] = matches[0]
        updated += 1
        print("Updated:", row["scientific_name"], "->", matches[0])

    else:
        unresolved.append((row["scientific_name"], matches))

# Write the updated metadata table
with open(metadata_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns, delimiter="\t")
    writer.writeheader()
    writer.writerows(species)

print("\nAssembly IDs filled:", updated)

print("\nSpecies still needing review:")
for name, matches in unresolved:
    print("-", name, ":", ", ".join(matches) if matches else "No match")

print("\nBackup saved to:", backup_file)
print("Updated metadata:", metadata_file)
