#!/bin/bash
#SBATCH --job-name=rer30_test
#SBATCH --partition=128x24
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=rer30_%j.out
#SBATCH --error=rer30_%j.err

# Import 30 Newick gene trees into RERconverge and save the tree object.
# Requires gene_trees_30.tsv under the combined scratch output directory.
set -e
module load rerconverge/0.3.0
cd ~/kelley-hibernation-rer
Rscript scripts/test_rer30.R
