#!/bin/bash
#SBATCH --job-name=rer30_binary
#SBATCH --partition=128x24
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=rer30_binary_%j.out
#SBATCH --error=rer30_binary_%j.err

# Preliminary end-to-end RERconverge binary-phenotype smoke test.
# Uses provisional labels from config/species_metadata.tsv and saves
# the association table and figures in pilot30_binary_smoketest/.
set -e
module load rerconverge/0.3.0
cd ~/kelley-hibernation-rer
Rscript scripts/run_rer30_binary.R
