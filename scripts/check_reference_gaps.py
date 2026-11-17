"""Count human-reference gap columns in the three extracted HBB MAF files."""
import argparse
import csv
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--scratch", type=Path, default=Path("/scratch/spathare/hibernation_rer"))
p.add_argument("--metadata", type=Path, default=Path("config/species_metadata.tsv"))
args = p.parse_args()

# Only count nucleotide calls from assemblies selected for our project.
with args.metadata.open() as f:
    selected = {r["assembly_id"] for r in csv.DictReader(f, delimiter="\t")
                if r["in_hiller"].strip().lower() == "yes"}

def blocks(path):
    """Yield the sequence rows from each MAF alignment block."""
    block = []
    with path.open() as f:
        for line in f:
            fields = line.split()
            if not fields or fields[0] == "a":
                if block:
                    yield block
                    block = []
            elif fields[0] == "s":
                block.append(fields)
    if block:
        yield block

total = [0, 0, 0, 0]
for start, end in [(5225597, 5225726), (5226576, 5226799), (5226929, 5227021)]:
    counts = [0, 0, 0, 0]
    path = args.scratch / "gene_alignments" / f"HBB_{start}_{end}.maf"
    for block in blocks(path):
        ref = next((r for r in block if r[1].split(".")[0] == "hg38"), None)
        if ref is None:
            continue
        if ref[4] != "+":
            raise ValueError("Expected positive-strand hg38 MAF reference")
        pos = int(ref[2])
        mammals = [r[6].upper() for r in block
                   if r[1].split(".")[0] in selected and r is not ref]
        # The reference coordinate advances only when hg38 has a base.
        for i, base in enumerate(ref[6]):
            if base != "-":
                pos += 1
                continue
            internal = start < pos < end
            has_base = any(seq[i] in "ACGT" for seq in mammals)
            counts[0] += 1
            counts[1] += int(internal)
            counts[2] += int(has_base)
            counts[3] += int(internal and has_base)
    total = [a+b for a,b in zip(total, counts)]
    print(start, end, counts)
# These are column occurrences, not verified biological insertion events.
print("Total gaps, internal gaps, selected calls, internal selected calls:", total)
