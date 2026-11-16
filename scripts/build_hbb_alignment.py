
"""Build a human-reference-guided HBB coding-sequence alignment.

Read three Hiller MAF exon slices, collect aligned nucleotides for the
selected assemblies, and write a 444-base FASTA alignment.
Missing or unaligned positions remain N. This script does not verify orthology.
Run from the repository root on a system with Biopython installed.
"""

import csv
from pathlib import Path
from Bio import AlignIO
from Bio.Seq import Seq

# Directory containing extracted HBB MAF exon files and final FASTA output.
base = Path("/scratch/spathare/hibernation_rer/gene_alignments")

# Three HBB genomic coding intervals on the human hg38 reference.
# They are listed in genomic order; HBB is on the reverse strand.
# Coordinates are zero-based, with the end position excluded.
exons = [
    (5225597, 5225726),
    (5226576, 5226799),
    (5226929, 5227021)
]

# Read our curated target species and their Hiller assembly identifiers.
with open("config/species_metadata.tsv") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

# Select assembly IDs for species labeled as present in Hiller.
selected = {
    row["assembly_id"].strip()
    for row in rows
    if row["in_hiller"].strip().lower() == "yes"
}

# Always include the human reference assembly as an alignment control.
selected.add("hg38")

# Store bases for each assembly in exon order.
# Each output position corresponds to a human-reference coding position.
sequences = {
    assembly: []
    for assembly in selected
}

# Record cases where overlapping MAF blocks disagree on a base.
conflicts = []

# Process each coding exon independently.
for start, end in exons:
    # Start every reference position as unknown (N); fill when covered.
    positions = {
        assembly: ["N"] * (end - start)
        for assembly in selected
    }

    # Each input MAF contains alignment blocks overlapping this interval.
    maf = base / f"HBB_{start}_{end}.maf"

    # A MAF file contains one or more blocks of aligned sequences.
    for block in AlignIO.parse(str(maf), "maf"):
        # Locate the hg38 reference row within the current alignment block.
        reference = next(
            (record for record in block if record.id.startswith("hg38.")),
            None
        )

        # Ignore blocks that do not contain the human reference.
        if reference is None:
            continue

        # The extracted alignment is expected in positive genomic orientation.
        if reference.annotations.get("strand") != 1:
            raise ValueError("Unexpected reference strand")

        # Track the corresponding genomic coordinate in hg38.
        ref_pos = reference.annotations["start"]

        # Walk alignment columns; advance the reference position only for
        # non-gap human bases. Insertions relative to hg38 are skipped.
        for col, ref_base in enumerate(str(reference.seq).upper()):
            if ref_base == "-":
                continue

            # Only save aligned columns within the requested coding interval.
            if start <= ref_pos < end:
                index = ref_pos - start

                # Look up the base for each selected genome in this column.
                for record in block:
                    # MAF row IDs have assembly and sequence separated by a dot.
                    assembly = record.id.split(".")[0]

                    if assembly not in selected:
                        continue

                    base_call = str(record.seq[col]).upper()
                    # Ignore gaps and ambiguous bases; those positions stay N.
                    if base_call not in "ACGT":
                        continue

                    # Detect inconsistent nucleotide calls across MAF blocks.
                    previous = positions[assembly][index]

                    if previous != "N" and previous != base_call:
                        conflicts.append((assembly, ref_pos))
                    else:
                        positions[assembly][index] = base_call

            ref_pos += 1

    # Append this exon to each species alignment, preserving exon order.
    for assembly in selected:
        sequences[assembly].extend(positions[assembly])

# Stop if overlapping blocks gave conflicting nucleotides.
if conflicts:
    raise ValueError(
        f"Conflicting bases at {len(conflicts)} assembly-position pairs"
    )

# HBB is on the negative genomic strand; reverse-complement the joined
# genomic-order exons to obtain the coding orientation.
output = base / "HBB_53species_CDS.fasta"

with open(output, "w") as f:
    for assembly in sorted(selected):
        sequence = "".join(sequences[assembly])
        sequence = str(Seq(sequence).reverse_complement())

        # All assemblies must retain the same 444 reference-aligned positions.
        if len(sequence) != 444:
            raise ValueError(f"Incorrect length for {assembly}")

        f.write(f">{assembly}\n{sequence}\n")

# Report output path, sequence count, and missing N positions per genome.
print("FASTA saved:", output)
print("Species:", len(selected))
print("Alignment length: 444 bp")

# Missing N counts are calculated before reverse-complementing; the
# number of Ns is the same in either orientation.
for assembly in sorted(selected):
    sequence = "".join(sequences[assembly])
    print(assembly, "missing bases:", sequence.count("N"))
