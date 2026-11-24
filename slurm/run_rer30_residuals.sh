#!/bin/bash
#SBATCH --job-name=rer30_rates
#SBATCH --partition=128x24
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=rer30_rates_%j.out
#SBATCH --error=rer30_rates_%j.err

# Calculate preliminary relative-rate residuals from rer30_trees.rds.
# This job does not perform hibernation association testing.
set -e
module load rerconverge/0.3.0
cd ~/kelley-hibernation-rer
Rscript scripts/calculate_rer30.R
