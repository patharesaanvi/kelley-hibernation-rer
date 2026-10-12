# Hiller 470 — Data Requirements and Analysis Plan

## 1. Alignment Selection

For our hibernation project, we are planning to use the **Hiller 470-mammal alignment** from UCSC.

- **Hiller 470:** Contains 470 mammalian genome assemblies representing 431 species.
- **Zoonomia 241:** Another alignment we considered, but Hiller has better coverage of our target species.

We chose Hiller as our starting dataset because it includes more of the hibernating mammals we want to study, including brown bears, black bears, bats, and rodents.

**Source:** [UCSC Hiller 470 Alignment](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)

## 2. Data We Need

Before running RERconverge, we need the following inputs:

**1. Species list and genome assembly IDs**
- Identify which target species are available in Hiller.
- Match their scientific names to the genome assembly IDs used by UCSC.
- Resolve cases where more than one assembly exists for the same species.

**2. Hibernation classifications**
- Identify which species are confirmed hibernators.
- Select appropriate non-hibernating species for comparison.
- Decide which branches should be considered hibernating foreground lineages.

**3. Orthologous gene alignments**
- Extract corresponding protein-coding gene sequences across mammals.
- Make sure we're comparing the same genes across species.
- Check for missing sequences and alignment quality.

**4. Phylogenetic trees**
- Use the Hiller species tree to represent evolutionary relationships between mammals.
- Generate gene-specific trees with estimated branch lengths for each gene.
- Make sure the species identifiers and tree structures are compatible.

**5. RERconverge inputs**
- Format the gene trees as a tab-separated file with gene IDs and Newick trees.
- Prepare the hibernation phenotype information.
- Use these inputs to calculate relative evolutionary rates and test their association with hibernation.

## 3. Work Completed So Far

- Set up the GitHub repository and Hummingbird scratch storage.
- Downloaded the Hiller 470 scientific-name and assembly-name phylogenetic trees.
- Wrote a Python script to compare our 32 target species against Hiller.
- Found 28 matches: 26 exact species-name matches and 2 subspecies matches.
- Wrote a second script to match the scientific names with genome assembly IDs.
- Identified duplicate assemblies for American black bear, little brown bat, and common pipistrelle.
- Created a species metadata table to organize our candidate species.

## 4. Next Steps

1. Decide which assemblies to use for species with duplicates.
2. Finalize the hibernating and non-hibernating species classifications.
3. Determine how to format the gene-tree inputs for RERconverge.
4. Extract a small set of orthologous gene alignments.
5. Generate pilot gene trees and check that RERconverge can read them.

## 5. Important Considerations

- Multiple genome assemblies from the same species should not automatically be treated as independent species.
- Having more bat species could influence our results, so we need to consider phylogenetic bias.
- Not every species in Hiller necessarily has usable sequence data for every gene.
- Faster evolutionary rates do not automatically mean positive selection.
- The hibernation status of each species needs to be supported by scientific evidence.

## 6. Data Storage

- **GitHub:** Python scripts, species metadata, documentation, and Markdown lab notebook.
- **Hummingbird scratch:** Genome alignments, generated gene trees, intermediate files, and analysis results.

Scratch directory: `/scratch/spathare/hibernation_rer`

## References

- [Hiller 470 — UCSC Genome Browser](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge — GitHub](https://github.com/nclark-lab/RERconverge)
