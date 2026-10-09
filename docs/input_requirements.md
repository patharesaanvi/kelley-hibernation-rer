# Input requirements and acquisition plan

## Candidate datasets

### Hiller/UCSC 470-way (initial candidate)
Track: https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way
470 mammal *assemblies*, representing 431 distinct species (UCSC). Determine exact alignment download path from track documentation and record release/checksum before transfers.

### Zoonomia 241-way (alternative)
Track: https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons241way
Project source: https://zoonomiaproject.org/the-data/
241-way Cactus whole-genome multiple alignment; select an accessible gene/region extraction strategy before downloading a very large alignment.

### UCSC hg38 100-way (proposal baseline)
https://hgdownload.gi.ucsc.edu/goldenPath/hg38/multiz100way/
Available MAF and human known-gene CDS alignments; use only if species overlap and methodological comparability support it.

## Must obtain before analysis
1. **Assembly species manifest:** scientific name, assembly accession/version, exact MAF/HAL tip name, duplicates, and quality status.
2. **Target taxon manifest:** species chosen for the analysis, overlap across candidate alignments, foreground/background/ambiguous labels and citations supporting phenotypes.
3. **Gene orthology list:** one-to-one ortholog IDs, consistent transcript/isoform choice, gene annotation release, coordinates, CDS extraction strategy.
4. **Reference species tree:** consistent topology, taxon labels, branch interpretation, and pruning decisions.
5. **Aligned CDS:** quality-controlled homologous coding sequences with comparable coordinates/frames; gaps and missingness assessed.
6. **Gene trees:** tab-separated gene IDs and Newick trees whose branches encode gene-specific sequence divergence; subset-compatible topology and at least one full taxon-coverage tree (per RERconverge docs).
7. **Phenotype/foreground definition:** foreground lineages independently assigned from evidence; verify internal-branch assumptions.
8. **Software and compute:** R, RERconverge, tree estimation tools, alignment extraction software and suitable scratch space.

## Avoid common pitfalls
- Do not equate genome-wide phyloP or phastCons scores with gene-specific branch lengths.
- Do not treat 470 assemblies as 470 independently sampled species.
- Do not label a species a non-hibernator merely because evidence is missing.
- Do not label every ancestral branch in a hibernator clade as foreground without biological justification.
- Do not compare genes with conflicting topology or mix gene coordinate builds.
- Do not infer positive selection from accelerated RER alone; branch-site codeml is a separate follow-up analysis.
