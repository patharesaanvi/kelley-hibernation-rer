#!/bin/bash
#SBATCH --job-name=trim52_test
#SBATCH --partition=128x24
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=trim52_%j.out
#SBATCH --error=trim52_%j.err

set -e
source ~/kelley-hibernation-env/bin/activate
module load ohpc
module load raxml-ng/1.2.0
cd ~/kelley-hibernation-rer
SCRATCH=/scratch/spathare/hibernation_rer
python scripts/extract_and_fit.py \
  --candidates "$SCRATCH/annotations/TRIM52_only.tsv" \
  --species ~/kelley-hibernation-rer/config/species_metadata.tsv \
  --master "$SCRATCH/raw_alignments/hiller470/hg38.470way.nh" \
  --bigmaf "unused-in-offline-mode" \
  --outdir "$SCRATCH/pilot50_trim52" \
  --target 1 \
  --min-species 4 \
  --max-missing 0.10 \
  --threads 2
