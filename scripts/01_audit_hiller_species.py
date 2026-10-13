
#!/usr/bin/env python3
"""Compare target species with the Hiller 470 scientific-name tree."""

import csv
import re
import sys
from pathlib import Path
from collections import Counter

def main(metadata_path, tree_path, output_path):
    # Read the Hiller Newick tree
    tree = Path(tree_path).read_text(encoding="utf-8")

    # Extract scientific names occurring at tree tips
    tips = re.findall(r"(?<=[(,])\s*([^():,\s]+)\s*:", tree)
    counts = Counter(tips)

    # Read target species metadata
    with open(metadata_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    results = []

    for row in rows:
        species = row["scientific_name"].strip()
        target = species.replace(" ", "_")

        # Exact scientific-name matches
        exact = [tip for tip in counts if tip == target]

        # Subspecies matches, e.g. Ursus_arctos_horribilis
        subspecies = [
            tip for tip in counts
            if tip.startswith(target + "_")
        ]

        if exact:
            status = "exact_match"
            matches = exact
        elif subspecies:
            status = "subspecies_match"
            matches = subspecies
        else:
            status = "not_found"
            matches = []

        results.append({
            "common_name": row["common_name"],
            "scientific_name": species,
            "match_status": status,
            "hiller_tree_tips": ";".join(matches),
            "tip_occurrences": sum(counts[t] for t in matches),
        })

    # Save audit results in scratch
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    print(f"Species checked: {len(results)}")
    for status in ("exact_match", "subspecies_match", "not_found"):
        n = sum(r["match_status"] == status for r in results)
        print(f"{status}: {n}")

    print("\nSpecies requiring review:")
    for r in results:
        if r["match_status"] != "exact_match" or r["tip_occurrences"] > 1:
            print(
                f"  {r['scientific_name']}: "
                f"{r['match_status']} "
                f"({r['hiller_tree_tips'] or 'no match'}; "
                f"occurrences={r['tip_occurrences']})"
            )

    print(f"\nResults saved to: {output}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(
            "Usage: python3 scripts/01_audit_hiller_species.py "
            "metadata.tsv scientificNames.nh output.tsv"
        )

    main(sys.argv[1], sys.argv[2], sys.argv[3])
