#!/bin/bash
#SBATCH --job-name=hibernation5
#SBATCH --partition=128x24
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=pilot5_%j.out
#SBATCH --error=pilot5_%j.err

set -e
source ~/kelley-hibernation-env/bin/activate
module load ohpc
module load raxml-ng/1.2.0
cd ~/kelley_50gene_pilot/kelley_50gene_pilot
SCRATCH=/scratch/spathare/hibernation_rer

echo "=== Starting 5-gene pilot ==="
hostname
date
python extract_and_fit.py \
  --candidates "$SCRATCH/annotations/pilot5_candidates.tsv" \
  --species ~/kelley-hibernation-rer/config/species_metadata.tsv \
  --master "$SCRATCH/raw_alignments/hiller470/hg38.470way.nh" \
  --bigmaf "unused-in-offline-mode" \
  --outdir "$SCRATCH/pilot50_batch01" \
  --target 5 \
  --min-species 35 \
  --max-missing 0.10 \
  --threads 2

echo "=== Completed ==="
date
