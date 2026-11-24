#!/bin/bash
#SBATCH --job-name=hibernation25
#SBATCH --partition=128x24
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --output=pilot25_%j.out
#SBATCH --error=pilot25_%j.err

# Run the additional 25-gene pilot batch with staged exon alignments.
# The 4-species threshold was used for technical testing; observed gene
# trees in the completed pilot retained substantially more species.
set -e
source ~/kelley-hibernation-env/bin/activate
module load ohpc
module load raxml-ng/1.2.0
cd ~/kelley-hibernation-rer
SCRATCH=/scratch/spathare/hibernation_rer
echo "=== Starting 25-gene pilot ==="
hostname
date
# Use the remaining-25 candidate file; gene trees are saved in scratch.
python scripts/extract_and_fit.py \
  --candidates "$SCRATCH/annotations/pilot30_remaining25.tsv" \
  --species ~/kelley-hibernation-rer/config/species_metadata.tsv \
  --master "$SCRATCH/raw_alignments/hiller470/hg38.470way.nh" \
  --bigmaf "unused-in-offline-mode" \
  --outdir "$SCRATCH/pilot30_run1" \
  --target 25 \
  --min-species 4 \
  --max-missing 0.10 \
  --threads 2
echo "=== Completed ==="
date
