#!/usr/bin/env python3
"""Validate species metadata before it is used as a phenotype table.
No external dependencies. Does not assign or infer any phenotype.
"""
import csv
import sys
from pathlib import Path

REQUIRED = ["common_name", "scientific_name", "alignment_tip", "assembly_accession",
            "hibernation_status", "foreground_decision", "phenotype_source", "comments"]


def main(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = set(REQUIRED) - set(reader.fieldnames or [])
        if missing:
            print("Missing columns:", ", ".join(sorted(missing)))
            return 2
        rows = list(reader)
    print(f"Rows: {len(rows)}")
    tips = [r["alignment_tip"].strip() for r in rows if r["alignment_tip"].strip()]
    duplicates = sorted({t for t in tips if tips.count(t) > 1})
    if duplicates:
        print("ERROR duplicate alignment tips:", ", ".join(duplicates))
        return 2
    unverified = [r["scientific_name"] for r in rows if
                  not r["alignment_tip"].strip() or
                  r["hibernation_status"].lower().strip() in {"", "unknown", "ambiguous"} or
                  not r["phenotype_source"].strip()]
    if unverified:
        print("NOT ANALYSIS-READY; verify species mapping and phenotype evidence:")
        for name in unverified:
            print(" -", name)
        return 1
    print("Basic metadata checks passed; scientific accuracy still requires review.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 scripts/check_species_table.py config/species_template.tsv")
    sys.exit(main(Path(sys.argv[1])))
