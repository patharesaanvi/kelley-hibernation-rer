# Lab notebook — Project setup and October 2026 progress

## Research question

Which protein-coding genes evolve faster or slower in hibernating mammals than in non-hibernating mammals? Do any rate shifts appear independently in different hibernating groups (bats, rodents, bears, lemurs)? Eventually, can we compare these findings with RNA-seq differential-expression results?

## Project dataset

We're working with **Hiller 470-way mammalian genome alignments** from UCSC, not the UCSC 100-way dataset mentioned in the original grant.

- [Hiller alignment](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- [RERconverge GitHub](https://github.com/nclark-lab/RERconverge)
- [Species metadata](../config/species_metadata.tsv)
- [Current species summary](../results/species_summary.tsv)

### Species work completed

I added six hibernating candidate species (western European hedgehog, hazel dormouse, fat dormouse, woodchuck, Asian black bear, and northern long-eared bat), reviewed assembly choices where Hiller had more than one, and updated the metadata. We currently list **58 candidate species, of which 53 are represented in Hiller**. The 53 break down into **29 foreground candidates, 19 background candidates, and five uncertain**. These phenotype classifications are preliminary and will need review before we define foreground branches for RERconverge.

## My scripts: what they do and where the output goes

Run the scripts from the repository folder (`~/kelley-hibernation-rer`) on Hummingbird. The scratch folder is `/scratch/spathare/hibernation_rer/`.

| Script | What it does | Output and where it is saved |
| --- | --- | --- |
| [`scripts/check_species.py`](../scripts/check_species.py) | Checks the metadata for duplicates, missing assembly IDs, and statuses to review. | **Prints checks in the terminal**; does not write an output file. |
| [`scripts/hiller_mapping.py`](../scripts/hiller_mapping.py) | Reads the Hiller trees, matches species names to assemblies, and checks our species list. | Writes `rer_results/hiller_assembly_mapping.tsv` in scratch, updates the local [metadata](../config/species_metadata.tsv), and makes a scratch backup `rer_results/species_metadata_backup.tsv` if one does not already exist. |
| [`scripts/species_summary.py`](../scripts/species_summary.py) | Counts hibernating, non-hibernating, and uncertain candidates by mammal group. | Writes `rer_results/species_summary.tsv` in scratch. A separately committed copy is at [`results/species_summary.tsv`](../results/species_summary.tsv). |
| [`scripts/build_hbb_alignment.py`](../scripts/build_hbb_alignment.py) | Reads the three extracted HBB MAF files and combines the reference-guided coding sequences for our species. | Writes `gene_alignments/HBB_53species_CDS.fasta` in scratch and prints missing base counts. |

**Important:** Scratch outputs don't automatically show up on GitHub. The small summary in `results/` is a saved copy, so it needs to be updated manually if the script is run again. 

### Hiller trees I downloaded

The two tree files are saved on Hummingbird, under `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/`:

- `hg38.470way.nh` — tree tips have assembly IDs, such as `hg38` and `mm39`.
- `hg38.470way.scientificNames.nh` — tree tips use scientific names.

## HBB test — figuring out the gene-tree input format

Our task was to figure out **how to go from Hiller gene alignments to gene-tree inputs for RERconverge**. I used HBB as a small test gene because it is well studied and short, **not** because we already know it is important for hibernation.

For the detailed explanation, genomic coordinates, run command, and quality concerns, see [the full HBB pilot notes](../docs/hbb_pilot.md).

### What I did and why

| Step | Why I did it | Output (under `/scratch/spathare/hibernation_rer/`) |
| --- | --- | --- |
| Extracted the three HBB coding regions using `bigBedToBed` | Needed the same genomic region aligned across mammals without downloading huge chromosome files. | `gene_alignments/HBB_5225597_5225726.maf`, `HBB_5226576_5226799.maf`, `HBB_5226929_5227021.maf` |
| Built the 53-species HBB alignment using [my script](../scripts/build_hbb_alignment.py) | Wanted one FASTA sequence for each of our Hiller assemblies. | `gene_alignments/HBB_53species_CDS.fasta` |
| Checked and filtered the alignment | Seven species had missing nucleotide positions, so I kept 46 complete sequences for this **first test**. | `gene_alignments/HBB_complete_CDS.fasta` |
| Pruned the Hiller tree | The original tree includes hundreds of assemblies; the tree tips needed to match the same 46 HBB sequences. | `gene_trees/HBB_pruned_topology.nwk` |
| Ran RAxML-NG | Estimated **HBB-specific branch lengths** while keeping Hiller's branching pattern fixed. | `gene_trees/HBB_test.raxml.bestTree`, plus `HBB_test.raxml.bestModel` and `HBB_test.raxml.log` |
| Made the gene-tree TSV | RERconverge expects a gene name followed by its Newick tree, separated by a tab. | `gene_trees/hiller_hibernation_gene_trees.tsv` (currently one HBB row) |

### Results of the HBB test

- Initial alignment: **53 sequences**, **444 bp** each.
- Strict complete-sequence filter: **46 sequences** retained.
- Pruned Hiller tree: **46 tips**, exactly matching the filtered FASTA.
- RAxML-NG final log-likelihood: **−5033.417582**.
- RAxML-NG warning: **seven near-zero branches**.
- The RERconverge input TSV has **one line starting with `HBB`**.
- **I successfully tested importing the HBB tree with RERconverge's `readTrees()` function.** I have not established that HBB shows a hibernation-related rate shift.

### What I still need to check

The alignment is a preliminary **human-reference-guided** extraction. It doesn't preserve species-specific insertions, and I haven't verified that every aligned sequence is a true HBB ortholog. The final missing-data rule and method for estimating branch lengths also need to be decided.

### October 27, 2026 — RERconverge HBB input test

**Progress made**
- Loaded R and RERconverge on Hummingbird and confirmed the package worked. The RERconverge environment ran R 4.2.3.
- Used `readTrees()` with the HBB gene-tree TSV and 46-species pruned Hiller topology (`max.read = 1`, `minSpecs = 46`).
- Successfully imported one HBB gene tree containing all 46 species.
- Confirmed the imported tree retained the original RAxML-NG branch-length range (0.000001–0.247934); a branch-by-branch comparison is still needed.
- RERconverge returned a master tree with branch lengths, but reported that the supplied pruned topology lacked lengths. The master-tree estimates are not yet validated as a genome-wide reference.

**Next steps**
- Investigate master-tree handling and compare branch lengths individually.
- Validate HBB alignment quality and orthology, including possible globin paralogs.
- Generate more orthologous gene trees before genome-wide relative-rate analysis.

**Takeaway:** The basic RERconverge import worked. This is a technical input check, not evidence of hibernation-associated rate shifts. Full commands and results are in [the HBB pilot notes](../docs/hbb_pilot.md).
