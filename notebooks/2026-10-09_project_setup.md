# Lab notebook — 2026-10-09

## Research question
Which protein-coding genes display convergent accelerated or decelerated relative evolutionary rates across independently hibernating mammalian lineages? How do these intersect with cross-species hibernation-associated expression genes?

## Project context
Proposal: ~20,000 orthologous alignments from UCSC 100-way with missing orthologs added using MUSCLE, gene-specific branch lengths estimated for RERconverge, Kendall's tau testing, BH FDR, pathway enrichment, comparison with expression signatures, and follow-up branch-site tests using codeml/PAML.

## Today's actions
- Reviewed UCSC Hiller 470-mammal, Zoonomia 241-way, and UCSC 100-way sources.
- Selected **Hiller 470-way as initial candidate only**; selection is pending taxon coverage and quality audit.
- Set up the GitHub repository with folders for scripts, species metadata, and lab notes. 
- Established phenotype table template. Status assignments and target alignment IDs remain unverified.

## Sources consulted
- https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way
- https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons241way
- https://hgdownload.gi.ucsc.edu/goldenPath/hg38/multiz100way/
- https://github.com/nclark-lab/RERconverge
