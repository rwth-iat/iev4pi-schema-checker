# IEV4PI Schema Checker

Companion repository for the paper **"A General Method for Traceable and Verifiable
Extraction from Engineering Documents"** (Schmetz, Chen, Miny, Kleinert, Vogel-Heuser),
submitted to IECON 2026.

This repository contains the artifact-only conformance checker for the **Schema
Specification v0.8.3**, the concrete workbook-based instantiation of the paper's
general extraction method for instrument loop diagrams, terminal diagrams, and
circuit diagrams. The checker evaluates a populated Excel workbook against the
specification alone — without access to the tool that produced it — and reports
whether the workbook is Level-1 conformant (§1.3 of the specification).

## Abstract

Engineering information in process automation is distributed across heterogeneous
documents whose structures, semantics, and levels of detail differ substantially.
Individual extraction techniques recover selected content, but they do not define
which intermediate results a transformation must produce for its outcome to remain
traceable to the source and verifiable without the producing implementation. This
paper presents a general method for extracting and transforming document-based
engineering information into a structured engineering representation. It combines
complete source-object capture, two structurally distinct identification paths,
explicit comparison and deviation resolution, consolidation, and engineering
structuring, and fixes these stages in a formal specification independent of a
particular extraction technology. Instantiated for three document families, it
populates three complete workbooks from two laboratory plants that pass all
artifact-level checks with zero violations, while twelve seeded variants are
detected and localized to their expected outcome. Making conformance decidable
from the artifact alone lets results from different implementations be compared
on a common basis.

## Repository structure

```
.
├── schema_conformance_checker.py  # Artifact-only conformance checker (entry point)
├── requirements.txt          # Python dependencies
├── Specifications/
│   ├── Method_Specification_v1.0.md       # Technology-independent method (RQ1, RQ2)
│   └── Schema_Specification_v0_8_3.md     # Workbook instantiation for 3 document families (RQ3)
├── artefacts/
│   ├── Engineering Documents/     # Raw source documents (PDF/xlsx) the example artefacts were extracted from
│   ├── Standardized Intermediate/ # Example workbooks (the laboratory-plant instances from the paper);
│   │                               # scanned by a no-argument checker run
│   └── Seeds/                     # Deliberately non-conformant variants used in the paper's Feasibility
│                                   # Assessment (§5); see artefacts/Seeds/README.md. Not scanned by a
│                                   # no-argument checker run.
└── results/                   # Checker output (report .txt + machine-readable .json) for the example
                                # artefacts and, under results/Seeds/, for the seeded variants
```

## Requirements

Python 3.9 or newer.

```
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

```
python schema_conformance_checker.py PATH\TO\WORKBOOK.xlsx
```

Example, using one of the provided example artefacts:

```
python schema_conformance_checker.py "artefacts\Standardized Intermediate\Pumpwerk_TU10F17_Instrument_Loop_Diagram_v0_8_3.xlsx"
```

Called without arguments, the checker discovers and evaluates every workbook in
`artefacts/Standardized Intermediate/`, writing one report and one JSON summary
per file to `results/`.

## Output

Each run writes a text report and a matching JSON summary to `results/`.
Excerpt from a conformant run:

```
=== Conformance Check Report ===
Document_Type: Instrument_Loop_Diagram
Schema_Version (as declared in Document_ID of this artifact): v0.8.3
Total findings (violations): 0
Total warnings (non-blocking): 0
...
Rule overview:
- I23: SKIP — Prüft inhaltlich Brücken-/Klemmleisten-Konsistenz für Terminal_Diagram-Workbooks (§11.9).
...
Detailed findings:
- No violations detected.
```

- `Total findings (violations): 0` means Level-1 conformant within the
  implemented rule scope.
- Every rule's status (`PASS`/`FAIL`/`WARNING`/`SKIP`/`NOT_RUN`/`NOT_IMPLEMENTED`)
  is listed under "Rule overview"; any violations are listed in full under
  "Detailed findings" as `[L<Layer>] <Rule>: <Detail>`.
- `SKIP` marks document-type-bound rules that do not apply to this
  `Document_Type` (the `Type_Constraint` does not match).

## Checked rule scope

- **§3** D1/D2 — mandatory sheets and sheet ordering
- **§11.7** I1–I22 — foreign keys, element/connection integrity, match states
- **§11.9** I29–I32 — `Source_Format` cardinality, polymorphic classification,
  cable-modeling-profile activation, optional extension sheets
- **Lookup layer** I13/I14 — `Attribute_Lookup` completeness, `Enum_Lookup`
  existence, including `Unspecifiable` handling
- **D6** — provenance cardinality
- **§11.8** — layer ordering of rule evaluation
- **§9.2** `Required_Attributes` — required-attribute coverage per `Attribute_Lookup`
- **§11.4** `Cluster_Coverage` — P3 post-condition (every non-topology Object covered
  by a Cluster) for PDF-sourced artefacts

Document-type-bound rules (I23, I24, I26, I28) are only evaluated when the
`Document_Type` activates them.

## Limitations

The checker verifies **conformance, not correctness**. A structurally complete
entry with incorrect content — e.g. a valid IEC 60757 code on the wrong
connection — remains conformant. Likewise, whether source capture was complete
is not assessed. See §1.3 and §7 of the specifications for the full conformance
model and its levels.

## Citation

If you use this repository, please cite the paper and/or the software — see
[CITATION.cff](CITATION.cff).

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgment

This work is based on results of the research project *Inkonsistenzerkennung
und -verfolgung für die PLT-Planung von Feldgeräten in der Prozessindustrie
(IEV4PI)*. The project is funded within the framework of the *Industrielle
Gemeinschaftsforschung* (IGF) by the Federal Ministry of Economic Affairs and
Climate Action (BMWK) on the basis of a decision by the German Bundestag and is
supported by the *Forschungsvereinigung Elektrotechnik* im ZVEI e.V.
