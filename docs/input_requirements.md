# Inputs and decisions for the hibernation evolutionary-rate analysis

This page explains what data the project needs, which parts we've prepared, and which decisions are still open. See the [README](../README.md) for the overall goal and [HBB pilot](hbb_pilot.md) for a concrete example.

## 1. Genome alignment source

**Chosen source: Hiller 470-way mammalian alignment**, accessed through UCSC. It includes hundreds of mammalian assemblies, including many of our species of interest.

- [UCSC Hiller 470-way page](https://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg38&g=cons470way)
- The original grant described UCSC 100-way, but the current research plan uses Hiller 470.
- We can retrieve specific reference-genome regions rather than downloading complete chromosome MAF files.

## 2. Target species and phenotype information

Main input: [`config/species_metadata.tsv`](../config/species_metadata.tsv).

It has six columns:

| Column | Meaning |
| --- | --- |
| `common_name` | Common mammal name |
| `scientific_name` | Scientific name used to match species |
| `assembly_id` | Selected UCSC/Hiller genome assembly |
| `in_hiller` | Whether a Hiller match was identified |
| `hibernation_status` | Preliminary classification |
| `mammal_group` | Major group (bats, bears, etc.) |

Current snapshot: **58 candidates, 53 in Hiller**. Among the 53, **29 hibernating/foreground candidates, 19 non-hibernating/background candidates, 5 uncertain**. The saved group counts are in [`results/species_summary.tsv`](../results/species_summary.tsv).

**Still to resolve:** verify phenotype evidence for uncertain or nonstandard species, confirm selected assembly quality, and decide how to assign *phylogenetic branches*, not merely species tips, as foreground or background. Presence in Hiller does not ensure good sequence coverage for every gene.

## 3. Orthologous gene alignments

For each gene, we'll need aligned DNA sequences from as many of the selected mammals as we can reliably include.

Questions that matter:
- Are these the corresponding **orthologs** across species, rather than nearby similar genes or paralogs?
- Are the sequences properly aligned, with insertions/deletions and strand orientation accounted for?
- Are there too many missing bases or low-quality regions?
- Do any genomes or genes require extra alignment work?

We tested extraction using human HBB coding coordinates and Hiller bigMaf data. See [`docs/hbb_pilot.md`](hbb_pilot.md).

**Important HBB limitation:** The pilot reconstruction follows **human reference positions** and ignores species insertions relative to human. Its 444-bp length and reasonable human translation do not by themselves establish correct orthology or a valid codon-aware alignment for every mammal.

## 4. Phylogenetic topology and branch lengths

We have Hiller trees with two types of tip labels:

```text
/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.nh
/scratch/spathare/hibernation_rer/raw_alignments/hiller470/hg38.470way.scientificNames.nh
```

For a given gene, the included tree tips must match the aligned sequences. For HBB, we **pruned the Hiller topology to the 46 complete sequences**, then used **RAxML-NG `--evaluate`** to optimize branch lengths on that fixed topology.

This is a **pilot method**, not an approved choice for every gene. We need to confirm the intended tree-estimation method with Avrami, especially for missing taxa, short alignments, and branches close to zero.

## 5. RERconverge input

Our pilot file is:
`/scratch/spathare/hibernation_rer/gene_trees/hiller_hibernation_gene_trees.tsv`

It is a tab-delimited text file with one row per gene:

```text
HBB<TAB>((speciesA:0.01,speciesB:0.02):0.03,speciesC:0.04);
```

Here, `<TAB>` represents an actual tab; the example species and numbers are **illustrative**. The real pilot file contains a 46-tip tree. A larger run would need many gene-specific trees plus a validated phenotype/foreground definition.

**Status:** Generated a one-gene file; not yet tested with RERconverge.

## 6. Planned downstream analysis

Once the gene trees and phenotype definitions are validated, the proposed research includes:
- RERconverge relative-rate calculations and association testing (Kendall's tau).
- Multiple-testing correction using Benjamini–Hochberg.
- Identifying shared and lineage-specific patterns.
- GO/pathway enrichment of accelerated or decelerated genes.
- Comparison with genes showing shared hibernation-associated differential expression.
- Follow-up branch-site tests using PAML `codeml` to help investigate selection versus relaxation of constraint.

None of these biological analyses has been completed using the HBB pilot.

## 7. Where scripts and output files are kept

| Code or file | Where |
| --- | --- |
| [`check_species.py`](../scripts/check_species.py) | Prints metadata checks to terminal |
| [`hiller_mapping.py`](../scripts/hiller_mapping.py) | Writes scratch `rer_results/hiller_assembly_mapping.tsv`; can update local metadata |
| [`species_summary.py`](../scripts/species_summary.py) | Writes scratch `rer_results/species_summary.tsv` |
| [`build_hbb_alignment.py`](../scripts/build_hbb_alignment.py) | Writes scratch `gene_alignments/HBB_53species_CDS.fasta` |
| [Committed species summary](../results/species_summary.tsv) | Snapshot in GitHub, not automatically refreshed |

All scratch paths are relative to `/scratch/spathare/hibernation_rer/`.

## 8. Next decisions

1. Confirm the preferred gene-tree branch-length estimation method with Avrami.
2. Review orthology and codon alignment of the HBB pilot.
3. Decide how much missing data is acceptable per species/gene.
4. Test reading the pilot gene-tree file in RERconverge.
5. Turn temporary filtering/pruning/formatting commands into reusable scripts.
6. Pilot multiple orthologous genes before scaling up.
