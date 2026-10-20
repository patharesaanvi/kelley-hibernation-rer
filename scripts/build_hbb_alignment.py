
import csv
from pathlib import Path
from Bio import AlignIO
from Bio.Seq import Seq

base = Path("/scratch/spathare/hibernation_rer/gene_alignments")

exons = [
    (5225597, 5225726),
    (5226576, 5226799),
    (5226929, 5227021)
]

with open("config/species_metadata.tsv") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

selected = {
    row["assembly_id"].strip()
    for row in rows
    if row["in_hiller"].strip().lower() == "yes"
}

selected.add("hg38")

# Store one base for each selected species at each reference position
sequences = {
    assembly: []
    for assembly in selected
}

conflicts = []

for start, end in exons:
    positions = {
        assembly: ["N"] * (end - start)
        for assembly in selected
    }

    maf = base / f"HBB_{start}_{end}.maf"

    for block in AlignIO.parse(str(maf), "maf"):
        reference = next(
            (record for record in block if record.id.startswith("hg38.")),
            None
        )

        if reference is None:
            continue

        if reference.annotations.get("strand") != 1:
            raise ValueError("Unexpected reference strand")

        ref_pos = reference.annotations["start"]

        for col, ref_base in enumerate(str(reference.seq).upper()):
            if ref_base == "-":
                continue

            if start <= ref_pos < end:
                index = ref_pos - start

                for record in block:
                    assembly = record.id.split(".")[0]

                    if assembly not in selected:
                        continue

                    base_call = str(record.seq[col]).upper()
                    if base_call not in "ACGT":
                        continue

                    previous = positions[assembly][index]

                    if previous != "N" and previous != base_call:
                        conflicts.append((assembly, ref_pos))
                    else:
                        positions[assembly][index] = base_call

            ref_pos += 1

    for assembly in selected:
        sequences[assembly].extend(positions[assembly])

if conflicts:
    raise ValueError(
        f"Conflicting bases at {len(conflicts)} assembly-position pairs"
    )

# Reverse-complement the combined genomic-order coding sequence
output = base / "HBB_53species_CDS.fasta"

with open(output, "w") as f:
    for assembly in sorted(selected):
        sequence = "".join(sequences[assembly])
        sequence = str(Seq(sequence).reverse_complement())

        if len(sequence) != 444:
            raise ValueError(f"Incorrect length for {assembly}")

        f.write(f">{assembly}\n{sequence}\n")

print("FASTA saved:", output)
print("Species:", len(selected))
print("Alignment length: 444 bp")

for assembly in sorted(selected):
    sequence = "".join(sequences[assembly])
    print(assembly, "missing bases:", sequence.count("N"))
