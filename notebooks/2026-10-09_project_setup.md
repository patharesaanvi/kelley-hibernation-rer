# Lab notebook — 2026-10-09

## Research question
Which protein-coding genes display convergent accelerated or decelerated relative evolutionary rates across independently hibernating mammalian lineages? How do these intersect with cross-species hibernation-associated expression genes?

## Project context
The grant proposes analyzing ~20,000 orthologous genes, using gene-specific branch lengths for RERconverge, Kendall's tau testing, BH FDR correction, pathway enrichment, comparison with expression signatures, and follow-up branch-site tests using codeml/PAML. **Our current project uses the Hiller 470-way mammalian alignment** as the comparative genomic data source (rather than the UCSC 100-way mentioned in the original grant).

## Sources consulted
- https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way
- https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons241way
- https://github.com/nclark-lab/RERconverge

## Where scripts save their outputs

Run repository scripts from the repository root (`~/kelley-hibernation-rer`). The main Hummingbird scratch folder is `/scratch/spathare/hibernation_rer/`.

| Script (GitHub link) | Input | Output / location | Notes |
| --- | --- | --- | --- |
| [`scripts/check_species.py`](../scripts/check_species.py) | [`config/species_metadata.tsv`](../config/species_metadata.tsv) | **Terminal output only** | Prints duplicates, missing assembly IDs, phenotype classifications needing review, and metadata-check summaries; does not write a results file. |
| [`scripts/hiller_mapping.py`](../scripts/hiller_mapping.py) | [`config/species_metadata.tsv`](../config/species_metadata.tsv) and the two Hiller Newick trees in scratch | `/scratch/spathare/hibernation_rer/rer_results/hiller_assembly_mapping.tsv`; updates `config/species_metadata.tsv`; makes `rer_results/species_metadata_backup.tsv` on first run | Mapping and backup are in **Hummingbird scratch**, not GitHub. The metadata file is modified **locally** when the script runs and requires `git add/commit/push` to update GitHub. |
| [`scripts/species_summary.py`](../scripts/species_summary.py) | [`config/species_metadata.tsv`](../config/species_metadata.tsv) | `/scratch/spathare/hibernation_rer/rer_results/species_summary.tsv` | A copy of the current species summary is also committed at [`results/species_summary.tsv`](../results/species_summary.tsv). Running this script does **not** automatically update the GitHub copy. |

### Hiller tree source files (Hummingbird)
- `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.nh` — assembly-ID species tree.
- `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.scientificNames.nh` — scientific-name species tree.

### HBB gene-tree pilot (October 2026)

This test uses the **same 53 species represented in our Hiller metadata**, not a separate species dataset. Seven sequences contained missing nucleotides, so we retained 46 complete coding sequences for this initial tree test.

| Step | Script or program | Output in Hummingbird scratch |
| --- | --- | --- |
| Extract the three HBB exon MAF regions | UCSC `bigBedToBed` command-line utility | `gene_alignments/HBB_5225597_5225726.maf`, `HBB_5226576_5226799.maf`, and `HBB_5226929_5227021.maf` |
| Build reference-guided HBB CDS alignment | `scripts/build_hbb_alignment.py` **(created on Hummingbird; not yet confirmed pushed to GitHub)** | `gene_alignments/HBB_53species_CDS.fasta` |
| Filter to sequences with only A/C/G/T | One-off Python/Biopython terminal command | `gene_alignments/HBB_complete_CDS.fasta` (46 species) |
| Prune Hiller species tree to the 46 sequences | One-off Python/Biopython terminal command | `gene_trees/HBB_pruned_topology.nwk` |
| Estimate HBB branch lengths on fixed topology | RAxML-NG `--evaluate` | `gene_trees/HBB_test.raxml.bestTree`, `HBB_test.raxml.bestModel`, `HBB_test.raxml.log` (and other RAxML-NG intermediates) |
| Format Newick tree for RERconverge | Shell `printf` + `tr` commands | `gene_trees/hiller_hibernation_gene_trees.tsv` (currently one row: HBB + tab + Newick tree) |

All relative HBB paths in the table are under `/scratch/spathare/hibernation_rer/`. **The HBB output files are on Hummingbird scratch, not committed to GitHub.** The RAxML-NG pilot completed and reported seven near-zero branches. Gene orthology/alignment quality and loading with RERconverge are still to be validated; RAxML-NG is a pilot tool choice to confirm with Avrami.

## Follow-up documentation tasks
- Commit the existing local `scripts/build_hbb_alignment.py` script to GitHub after reviewing it.
- Convert the temporary HBB filtering, tree-pruning, and formatting terminal commands into reusable scripts if we keep this workflow.
- Validate the RERconverge input and confirm the final branch-length estimation approach with Avrami.
