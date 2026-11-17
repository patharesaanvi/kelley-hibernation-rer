"""Keep aligned sequences whose fraction of non-ACGT positions is acceptable."""
import argparse
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("input", type=Path)
p.add_argument("output", type=Path)
p.add_argument("--threshold", type=float, default=0.10,
               help="Maximum missing fraction, e.g. 0.10 for 10 percent")
a = p.parse_args()
if not 0 <= a.threshold <= 1:
    p.error("Threshold must be between 0 and 1")

# Read multiline FASTA records without requiring Biopython.
def records(path):
    name, parts = None, []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(parts).upper()
                name, parts = line[1:], []
            elif line:
                if name is None:
                    raise ValueError("Sequence before FASTA header")
                parts.append(line)
    if name is not None:
        yield name, "".join(parts).upper()

seqs = list(records(a.input))
if not seqs or len({len(s) for _, s in seqs}) != 1 or not seqs[0][1]:
    raise ValueError("Expected a nonempty alignment with equal sequence lengths")
# Count N, gaps and other ambiguous bases as missing. Keep the original columns.
kept = 0
with a.output.open("x") as out:
    for name, seq in seqs:
        fraction = sum(b not in "ACGT" for b in seq) / len(seq)
        accept = fraction <= a.threshold
        print(f"{name}\t{fraction:.6f}\t{'keep' if accept else 'exclude'}")
        if accept:
            out.write(f">{name}\n{seq}\n")
            kept += 1
print(f"Retained {kept}/{len(seqs)} sequences")
