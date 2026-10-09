# Lab notebook — 2026-10-09

## Research question
Which protein-coding genes display convergent accelerated or decelerated relative evolutionary rates across independently hibernating mammalian lineages? How do these intersect with cross-species hibernation-associated expression genes?

## Project context
Proposal: ~20,000 orthologous alignments from UCSC 100-way with missing orthologs added using MUSCLE, gene-specific branch lengths estimated for RERconverge, Kendall's tau testing, BH FDR, pathway enrichment, comparison with expression signatures, and follow-up branch-site tests using codeml/PAML.

## Today's actions
- Reviewed UCSC Hiller 470-mammal, Zoonomia 241-way, and UCSC 100-way sources.
- Selected **Hiller 470-way as initial candidate only**; selection is pending taxon coverage and quality audit.
- Created project skeleton with Git exclusion rules for scratch-generated output.
- Established phenotype table template. Status assignments and target alignment IDs remain unverified.

## Working hypothesis
Convergent hibernation phenotypes may associate with recurrent changes in gene-specific evolutionary rates. This is a testable hypothesis, not a result.

## Sources consulted
- https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way
- https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons241way
- https://hgdownload.gi.ucsc.edu/goldenPath/hg38/multiz100way/
- https://github.com/nclark-lab/RERconverge

## Open decisions
1. Confirm with supervisor which species count as hibernators, non-hibernators or ambiguous phenotypes, especially bears.
2. Determine authorized scratch path and software/modules on the lab HPC.
3. Obtain exact Hiller and Zoonomia assembly/sequence-name manifests and audit target species coverage.
4. Agree on orthology, reference species, transcript selection, alignment QC and missing-data thresholds.
5. Select constrained topology and gene-tree branch-length estimation method.
6. Determine if the lab already has a validated precomputed gene-tree dataset.

## Next experiment (pilot; NOT RUN)
Take 10–20 single-copy protein-coding orthologs represented in several independent hibernating clades and adequate controls. Extract per-gene coding alignments, inspect missingness and frames, estimate branch lengths on the same topology, then run the documented RERconverge tutorial pattern. Expand only after QC is approved.

## Results
No computational experiment has been run. No results or biological conclusions yet.
