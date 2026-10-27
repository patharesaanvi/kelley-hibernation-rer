# HBB pilot: from Hiller alignment to a gene-tree input

**Status:** Preliminary pipeline test completed in October 2026. Not yet validated for biological interpretation or loaded into RERconverge.

## Why I tested HBB

Our assigned task was to figure out **how to prepare gene-tree inputs for RERconverge**. Instead of starting with thousands of genes, I chose **HBB (hemoglobin subunit beta)**, a short and well-studied coding gene. HBB is involved in oxygen transport, but I didn't choose it because we knew it was associated with hibernation.

The main idea was to see whether I could extract sequences from our **Hiller 470** dataset, create a gene alignment, estimate branch lengths, and format a tree that RERconverge could potentially read.

## What I started with

- **Species list:** [`config/species_metadata.tsv`](../config/species_metadata.tsv), with 53 selected Hiller assemblies.
- **Source:** UCSC Hiller 470-way multiple genome alignment.
- **Human transcript:** HBB RefSeq `NM_000518.5` on the negative strand of hg38 chromosome 11.
- **Hiller tree:** `/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.nh`.

### The three human HBB coding regions

These use **0-based, half-open hg38 coordinates**. The end coordinate is excluded.

| Coding region | Start | End | Length |
| --- | ---: | ---: | ---: |
| Exon 1 coding part | 5,225,597 | 5,225,726 | 129 bp |
| Exon 2 coding part | 5,226,576 | 5,226,799 | 223 bp |
| Exon 3 coding part | 5,226,929 | 5,227,021 | 92 bp |
| **Total** | | | **444 bp** |

The coding regions are separated by introns. Because HBB is on the negative strand, the extracted reference-order DNA must be reverse-complemented into coding orientation.

## Step 1 — Extract the genomic alignment regions

Hiller chromosome-wide MAF files are extremely large. I used UCSC's **`bigBedToBed`** command-line utility against the indexed Hiller bigMaf resource to get the three HBB exon regions without downloading whole chromosomes.

The three intermediate MAF files were saved under `/scratch/spathare/hibernation_rer/gene_alignments/`:

```text
HBB_5225597_5225726.maf
HBB_5226576_5226799.maf
HBB_5226929_5227021.maf
```

**MAF** (Multiple Alignment Format) stores alignment blocks showing which bases from different mammalian genomes align to the same human reference region.

**Why we did this:** RAxML-NG needs an aligned DNA sequence for each species, not a full chromosome-wide genome alignment.

## Step 2 — Build the 53-species coding alignment

Script: [`scripts/build_hbb_alignment.py`](../scripts/build_hbb_alignment.py)

The script reads the three MAF files, selects assemblies marked `in_hiller=Yes` in our species metadata, and reconstructs one HBB coding sequence per assembly.

In more detail, it:
1. Creates 444 human-reference-based positions for each selected assembly.
2. Reads each MAF alignment block and finds where it maps onto the human HBB exons.
3. Fills positions with a known A/C/G/T base when available, otherwise leaving `N`.
4. Combines the three exon regions and reverse-complements them into coding orientation.
5. Saves a FASTA file and prints the number of missing bases per assembly.

**Output:**
`/scratch/spathare/hibernation_rer/gene_alignments/HBB_53species_CDS.fasta`

The result had **53 FASTA sequences of 444 bases each**.

**Limitations:** For this test, I used the human HBB reference positions to extract sequences from other mammals, so the alignment might miss extra nucleotides present in other species. I also still need to confirm that the sequences I extracted are the correct HBB orthologs across all species. These are things I need to check before using the alignment for the actual evolutionary analysis.

## Step 3 — Perform basic checks and filter for the pilot

Using Biopython in the Hummingbird terminal, I checked:
- 53 sequences, all 444 bp.
- All begin with `ATG`.
- No internal stop codons were detected in the translated sequences.
- Human sequence translates to a beta-globin beginning `MVHLTPEEKSAVTALWGKVN`, and ends with `TAA`.
- Seven assemblies contained unknown nucleotide positions (`N`).

Seven incomplete assemblies were:

| Assembly | Missing bases |
| --- | ---: |
| `HLailMel2` | 2 |
| `HLmarFla1` | 78 |
| `HLtadBra1` | 4 |
| `bosTau9` | 6 |
| `mesAur1` | 19 |
| `speTri2` | 127 |
| `HLuroPar1` | 1 |

For this first test, I kept only sequences made entirely of A/C/G/T. This left **46 complete sequences**.

**Output:** `/scratch/spathare/hibernation_rer/gene_alignments/HBB_complete_CDS.fasta`

For this initial test, I removed all seven species that had missing nucleotides in their HBB sequences to make the initial test simpler. Missing nucleotides give us less sequence information to work with which can make it harder to accurately estimate branch lengths, especially when a species has a lot of missing data. However, RAxML-NG can handle some missing nucleotides, so I still need to figure out how much missing data we should allow before excluding species from our actual analysis. 

## Step 4 — Prune the Hiller species tree

The original Hiller tree contains hundreds of mammalian assembly tips, but our filtered HBB FASTA contains only 46 sequences.

I used Biopython to remove all tree tips that were **not** in the HBB FASTA.

- Filtering was applied to **the DNA sequences**.
- Pruning was applied to **the phylogenetic tree**.
- Pruning did **not** remove bases from the FASTA.
- The Hiller branching relationships were retained for the selected species.

Validation:

```text
HBB sequences: 46
Species in pruned tree: 46
Tip labels match: True
```

**Output:** `/scratch/spathare/hibernation_rer/gene_trees/HBB_pruned_topology.nwk`

This is a **Newick-format** tree containing the Hiller topology. It did not yet have HBB-specific estimated branch lengths.

## Step 5 — Estimate HBB branch lengths with RAxML-NG

For the pilot, I used **RAxML-NG** because it was available on Hummingbird and supports branch-length optimization while keeping a supplied topology fixed.

The command used:

```bash
module load raxml-ng/1.2.0
SCRATCH="/scratch/spathare/hibernation_rer"

raxml-ng --evaluate \
  --msa "$SCRATCH/gene_alignments/HBB_complete_CDS.fasta" \
  --tree "$SCRATCH/gene_trees/HBB_pruned_topology.nwk" \
  --model GTR+G \
  --prefix "$SCRATCH/gene_trees/HBB_test" \
  --threads 2
```

- **MAF/FASTA** describe aligned DNA sequences.
- **Topology** describes how species are connected.
- **Branch lengths** estimate substitutions along branches under a model.
- `--evaluate` optimized HBB-specific branch lengths on the fixed Hiller topology.

Outputs include:

| Output | Meaning |
| --- | --- |
| `gene_trees/HBB_test.raxml.bestTree` | Newick gene tree with estimated branch lengths |
| `gene_trees/HBB_test.raxml.bestModel` | Tells us the model and estimated parameters used to describe DNA evolution |
| `gene_trees/HBB_test.raxml.log` | Run details, likelihood, and warnings |

The log reported:
- Final log-likelihood **−5033.417582**.
- **46** tree tips, matching the FASTA.
- Minimum reported branch length **0.000001**; maximum **0.247934**.
- **7 near-zero branches**. These may reflect limited HBB sequence variation and should be reviewed.

**Why RAxML-NG?** It was a convenient way to test an upstream branch-length estimation step. **It does not replace RERconverge** and is not named in the grant as a required method. Its use for the final multi-gene pipeline needs approval from Avrami.

## Step 6 — Format the tree for RERconverge

We created a tab-delimited file with **one gene name followed by one Newick tree on the same line**.

The basic layout is:

```text
HBB<TAB>((speciesA:0.01,speciesB:0.02):0.03,speciesC:0.04);
```

This is an illustration; the actual file contains the 46-tip HBB tree and real estimated branch lengths. `<TAB>` stands for a tab character.

**Output:** `/scratch/spathare/hibernation_rer/gene_trees/hiller_hibernation_gene_trees.tsv`

We confirmed that the file has **one line** and the gene identifier is **`HBB`**.

**Not done:** Testing `readTrees()` in RERconverge. One gene alone is not enough for a reliable genome-wide relative-rate analysis.

## File locations at a glance

Everything here is on Hummingbird in `/scratch/spathare/hibernation_rer/`, except the linked Python script saved in GitHub.

| Step | Location relative to scratch root |
| --- | --- |
| Hiller tree | `raw_alignments/hiller470/hg38.470way.nh` |
| Extracted HBB alignment blocks | `gene_alignments/HBB_*.maf` |
| 53-species FASTA | `gene_alignments/HBB_53species_CDS.fasta` |
| 46-species FASTA | `gene_alignments/HBB_complete_CDS.fasta` |
| Pruned topology | `gene_trees/HBB_pruned_topology.nwk` |
| Estimated tree | `gene_trees/HBB_test.raxml.bestTree` |
| RERconverge-format file | `gene_trees/hiller_hibernation_gene_trees.tsv` |

## What still needs to be checked

- **Orthology:** HBB is part of a gene family with related globins; an aligned region isn't automatically the correct ortholog.
- **Alignment quality:** Review gaps, insertions, coding frame, and whether reference-guided reconstruction is appropriate.
- **Missing data:** Choose a sensible gene-level threshold instead of requiring 100% completeness by default.
- **Tree estimation:** Confirm the final branch-length method with Avrami and investigate near-zero branches.
- **RERconverge:** Test `readTrees()` with the one-gene input, then pilot a small multi-gene dataset.
- **Automation:** Filtering, tree pruning, and final TSV formatting were run as one-off terminal commands and have not yet been saved as reusable GitHub scripts.

## What the test showed

**We figured out how to prepare a preliminary gene-tree input from Hiller using one gene.** We have not established that HBB experienced a hibernation-related rate shift, and the pilot needs further validation before scaling up.

[Back to project overview](../README.md)
