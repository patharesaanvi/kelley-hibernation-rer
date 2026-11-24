import csv
import subprocess
import time
from pathlib import Path

# Hummingbird-specific working paths; edit these if running elsewhere.
# Inputs are selected gene intervals; output files are exon-level BED4 bigMaf records.
scratch = Path("/scratch/spathare/hibernation_rer")
candidates = scratch / "annotations/pilot30_candidates.tsv"
output = scratch / "pilot30_run1/genes"
url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz470way/multiz470way.bigMaf"

with candidates.open() as f:
    rows = list(csv.DictReader(f, delimiter="\t"))

# Retrieve each coding-exon interval separately for the selected genes.
for row in rows:
    gene = row["gene"]
    folder = output / gene
    folder.mkdir(parents=True, exist_ok=True)

    for i, coordinate in enumerate(row["coordinates"].split(","), 1):
        start, end = map(int, coordinate.split("-"))
        bed = folder / f"exon_{i}.bed"

        # Reuse previously downloaded, nonempty exon files.
        if bed.exists() and bed.stat().st_size > 0:
            print("CACHED", gene, i, flush=True)
            continue

        temp = folder / f"exon_{i}.bed.partial"

        cmd = [
            "bigBedToBed", url, str(temp),
            f'-chrom={row["chrom"]}',
            f"-start={start}",
            f"-end={end}"
        ]

        # Download into a temporary file and rename only after a nonempty result.
        try:
            subprocess.run(cmd, check=True, timeout=120)
            if temp.stat().st_size == 0:
                raise ValueError("Empty BED extraction")
            temp.rename(bed)
            print("STAGED", gene, i, flush=True)
        except Exception as e:
            print("FAILED", gene, i, e, flush=True)
            temp.unlink(missing_ok=True)

        # Space out requests to the UCSC alignment server.
        time.sleep(2)
