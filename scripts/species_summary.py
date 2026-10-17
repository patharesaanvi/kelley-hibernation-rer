
#!/usr/bin/env python3
"""Summarize mammal groups in our Hiller species metadata."""

import csv
import os
from collections import Counter
from pathlib import Path

# Read our 51-species metadata table
with open("config/species_metadata.tsv", newline="") as file:
    species = list(csv.DictReader(file, delimiter="\t"))

# The 20 proposed background species from our project list
background = {
    "Felis catus", "Canis lupus familiaris",
    "Ailuropoda melanoleuca", "Ursus maritimus",
    "Bos taurus", "Sus scrofa",
    "Pteropus vampyrus", "Desmodus rotundus",
    "Oryctolagus cuniculus", "Xerus inauris",
    "Sciurus carolinensis", "Rattus norvegicus",
    "Mus musculus", "Cavia porcellus",
    "Otolemur garnettii", "Lepilemur ankaranensis",
    "Gorilla gorilla", "Homo sapiens",
    "Pan troglodytes", "Macaca mulatta"
}

bats = {
    "Rhinolophus", "Myotis", "Miniopterus",
    "Hipposideros", "Eptesicus", "Lasiurus",
    "Pipistrellus", "Tadarida", "Pteropus", "Desmodus"
}
squirrels = {"Ictidomys", "Urocitellus", "Spermophilus",
             "Xerus", "Sciurus"}
lemurs = {"Cheirogaleus", "Microcebus", "Lepilemur"}
primates = {"Otolemur", "Gorilla", "Homo", "Pan", "Macaca"}
rodents = {"Mesocricetus", "Phodopus", "Marmota",
           "Allactaga", "Ellobius", "Zapus",
           "Rattus", "Mus", "Cavia"}

# Group each species by mammalian category
def get_group(name):
    genus = name.split()[0]

    if genus in bats:
        return "Bats"
    if genus in squirrels or genus == "Marmota":
        return "Squirrels and marmots"
    if genus == "Ursus" or genus == "Ailuropoda":
        return "Bears"
    if genus in lemurs:
        return "Lemurs"
    if genus in primates:
        return "Other primates"
    if genus in rodents:
        return "Other rodents"
    return "Other mammals"


counts = Counter()

for row in species:

    # Only include species available in Hiller 470
    if row["in_hiller"].strip().lower() != "yes":
        continue

    name = row["scientific_name"].strip()
    status = row["hibernation_status"].strip().lower()

    # Separate proposed background species from foreground candidates
    if name in background:
        category = "Background"
    elif status == "hibernation":
        category = "Foreground candidate"
    else:
        category = "Uncertain"

    group = get_group(name)
    counts[(group, category)] += 1

# Save the summary in scratch
scratch = Path(os.environ.get(
    "SCRATCH_ROOT", "/scratch/spathare/hibernation_rer"
))
output = scratch / "rer_results" / "species_summary.tsv"
output.parent.mkdir(parents=True, exist_ok=True)

groups = [
    "Bats", "Squirrels and marmots", "Bears",
    "Lemurs", "Other primates", "Other rodents",
    "Other mammals"
]
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

