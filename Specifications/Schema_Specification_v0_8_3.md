# Schema Specification v0.8 — Industrial Engineering Documentation (Instrument_Loop_Diagram + Terminal_Diagram + Circuit_Diagram)

## 0. Document Information

| Field | Value |
|---|---|
| Schema Version | v0.8.3 (content patch of the v0.8.2 structure patch; see §13 for the itemized change list) |
| Status | Pre-Release (schema-stability and interoperability baseline) |
| Lookup Version | v0.8.0 |
| Predecessor | v0.8.2 (structure patch of the v0.8.1 freeze; content-identical to v0.8) |
| Publication Date | 2026-07-29 |
| Scope | Instrument_Loop_Diagram + Terminal_Diagram + Circuit_Diagram |
| Language | English (Schema values and specification text harmonized; see §17 for German→English term migration from legacy v0.4 documents) |

**Reading hint:** This specification is **standalone**. It contains the complete schema for industrial engineering documentation as a self-contained document. Predecessor versions (v0.4 Instrument_Loop_Diagram baseline; v0.5 Terminal_Diagram extension; v0.5.1 Circuit_Diagram extension; v0.8.2 structure patch) are referenced for historical context in §1 and §13, but no §-references reach across version boundaries within this document.

**v0.8.3 in one paragraph:** This is a content patch driven by build-and-check experience on three real source documents from two laboratory plants (Instrument_Loop_Diagram from the pumping station; Terminal_Diagram and Circuit_Diagram from plant HC10). Every change closes a gap identified during that exercise and is scoped strictly to *extraction* rules (what a workbook must record from one document), never to cross-document interpretation or aggregation, which remain out of scope per §1.1 Principle 6 and `K2`. See §13 for the itemized list; each entry cites the concrete finding that motivated it.

**Cross-reference — Object-Sheet structure:** The `Object` sheet is the foundation for source-content preservation per §0.1 and for graphical reconstructability. Each `Object` row represents one atomic source artifact (text label, symbol primitive, geometric position) and carries `Object_ID`, `Content_Text`, `Object_Type`, positional metadata, and `Source_Operation`. Provenance from `Element_Data`, `Connection_Data`, etc. references `Object` rows by `Object_ID`. Full positional metadata in `Object` supports downstream rendering and graphical reconstructability of source documents.

### 0.1 Language and Encoding Convention

A strict separation governs which content is in English and which remains in its original form. This convention is **fundamental** and overrides any apparent inconsistency:

| Category | Language/Form | Examples |
|---|---|---|
| **Schema structures** (sheet names, column names, Field_Names) | English | `Element_ID`, `Wire_Color`, `Attribute_Name` |
| **Schema classifications** (schema-defined enums) | English | `Element_Type=Terminal`, `Connection_Type=Bridge_Longitudinal`, `Match_Status=Matched`, `RepresentedItem_Type=Terminal_Strip` |
| **Source-extracted raw content** (read from the source document) | **Original — never translated** | `Object.Content_Text="L3 gebrückt"`, `Document_Data.Project_Name="Technikumsanlage"`, `Element_Data.Manufacturer="Phoenix Contact"` |
| **Norm-codable enum values** | language-neutral norm code; original preserved in `Object` | `Wire_Color=RD` (IEC 60757), source text `"rot"` preserved in the linked `Object.Content_Text` |
| **International codes** | unchanged | `Polarity=L1/N/PE`, `Cable_Type=LiYCY`, `IEC_81346_2_Class=X` |

**Critical principle — no translation of source content:** Values read from the source document (title-block fields, free-text descriptions, manufacturer names, color words, designations) are **preserved verbatim in their original language**. Translation of source content would violate the single-source-of-truth discipline. The schema classifies and codes; it does not translate the source.

**Universal encoding convention (applies to ALL Enum_Lookup fields):** Every enum-typed value in the schema is stored as a **language-neutral code** in `Allowed_Value`. Where an established norm code exists (IEC 60757 for wire colors, IEC 60529 for IP protection, IEC 81346-2 for classification letters, IEC 60898-1 for trip characteristics, …), that norm code is the `Allowed_Value`. Where no norm code exists, the canonical English schema term serves as the code. In every case, the `Enum_Lookup.Description` field carries a bilingual (DE / EN) reading aid, and `Normative_Reference` names the code's source. The full per-field encoding table is in §9.3.

**Wire_Color as the exemplar:** A wire labeled `rot` in a German source document keeps `rot` in the corresponding `Object.Content_Text`. The classified `Connection_Data` value `Wire_Color` carries the language-neutral IEC 60757 code `RD`. The `Enum_Lookup` row for `RD` carries `Description = "rot / red"` and `Normative_Reference = IEC 60757`. Provenance via `Connection_Data_Source → Object` preserves the link to the original `rot`. Nothing is translated — the source word stays, the schema value is encoded. The same pattern applies to every other enum field.



---

## Table of Contents (added in v0.8.2)

**Conventions and scope:** §0 Document Information · §0.1 Language and Encoding Convention · §1 Scope Overview (incl. §1.3 Conformance Levels) · §2 Schema Application per Document Type
**Architecture and extraction:** §3 Sheet Architecture (§3.7 Identifiers, §3.8 Core-Minimum Designation Normalization, §3.9 SemanticID Convention) · §4 Source Extraction Rules (§4.2.3 Bulk/Range Terminal Notation)
**Document-type-specific provisions (Terminal_Diagram):** §5 Element_Types · §6 Connection Modeling · §7 RepresentedItem_Type
**Classification and catalogs:** §8 Normative Classification · §9 Lookup Tables · §10 Hierarchical Structures
**Rules and process:** §11 Rule Catalogs (A/C/M/P/E/K/I/AG; process P0–P9; validator order)
**Examples:** §12 Worked Examples
**Status and history:** §13 Version History · §14 Known Limitations · §15 Roadmap · §16 Normative Updates for Full Release · §17 Term Migration (relocated to Appendix B)
**Appendices:** A Sheet Column Definitions · B Relocated Historical and Migration Material (original numbering retained)

## 1. Scope Overview

This specification defines a machine-readable Excel schema for three classes of industrial engineering documentation:

| Document Type | Purpose | Norm anchors |
|---|---|---|
| **Instrument_Loop_Diagram** (Stellenplan) | Process measurement and control instrument loops (PCE_Request) | IEC 81346-1/2, IEC 62424, DIN 19227-2, IEC 60050-351 |
| **Terminal_Diagram** (Klemmenplan) | Terminal strips, wiring, cables, bridges, and connected devices | IEC 81346-1/2, IEC 60617-3/-7, IEC 60757, DIN VDE 0100-200, DIN VDE 0281 |
| **Circuit_Diagram** (Stromlaufplan) | Electrical circuit symbols and connections, primary and secondary circuits | IEC 81346-1/2, IEC 60617-2/-6/-7/-8 |

All three document types share **one schema** (the same 28 mandatory sheets, the same lookup mechanism, the same integrity-rule framework). Document-type-specific behavior is controlled via `Type_Constraint` in `Attribute_Lookup` (see §9.4) and via rule scoping (see §11).

### 1.1 Design principles

1. **Content-level reconstructability and evidence-based traceability:** The schema enables content-level reconstruction of original source documents from Excel alone and provides evidence-based traceability for every recorded fact. Source content is preserved verbatim in `Object.Content_Text` (see §0.1); schema values are encoded classifications. Graphical-fidelity reconstructability (exact pixel-level rendering of source drawings — line widths, font glyphs, layout grids, symbol shapes) is supported where positional and graphical source objects are captured (BBox, Geometry_Type, Geometry_Closed per A.7) but is **not guaranteed for all source formats** — Excel and Verschaltungsliste sources do not carry graphical primitives in the schema, and even for PDF sources the recording is coordinate-and-text-based, not vector-shape-based. Downstream consumers of the Excel workbook (e.g. graph-building tools, ontology exporters, visualization layers) consume the Excel evidence and produce richer graphical or semantic artifacts where needed.
2. **Norm-anchored classification:** Every classification value (Element_Type, Wire_Color, Polarity, Connection_Type, etc.) traces to a specific norm without interpretation. Norms are inventoried in §16.
3. **Cross-document linkage via shared designation:** Objects appearing in multiple documents (e.g. a contactor in both Terminal_Diagram and Circuit_Diagram) are linked via shared Primary_RKZ — never via structural grouping invented in the schema.
4. **Source-faithful identity:** Objects are identified only by reference designations present in the source documents. No inference, no manufactured identifiers.
5. **Sheet-sharing maximum:** All 28 mandatory sheets are document-type-agnostic. No document type owns dedicated sheets.
6. **Single-document invariant:** Each Excel workbook represents **exactly one source document**, identified by exactly one row in `Document_ID`. All FKs in all 28 mandatory sheets are **local to the workbook** — no FK references a row in another workbook. Cross-document relationships (e.g. a contactor distributed across a Terminal_Diagram workbook and a Circuit_Diagram workbook; a Stromlaufplan-internal cross-reference `(001.8-A)` pointing to another sheet) are expressed as: (a) shared `Primary_RKZ` (designation prefix match, per principle 3); or (b) parsed-text attributes captured as `Element_Data` rows (e.g. `Cross_Reference_Target_Document_Number`, see §4.3.3). Reconstruction of cross-document continuations is the responsibility of the downstream aggregation / ontology layer — not the schema.

### 1.2 Historical change log

| Version | Year | Content |
|---|---|---|
| v0.4 | 2025 | Initial Instrument_Loop_Diagram baseline (PCE_Request modeling, 23 sheets, rules I1–I22, German schema language) |
| v0.5 | 2026-05 | Terminal_Diagram extension (2 new sheets, rules I23–I25, English schema language, IEC 60757 Wire_Color encoding) |
| v0.5.1 | 2026-05 | Circuit_Diagram extension (0 new sheets, 4 new Element_Types, rules I26–I28, CAEX connection-point convention) |
| v0.6 | 2026-05 | Structural consolidation: v0.4 + v0.5 + v0.5.1 unified into one standalone specification; sheet-count and provenance structure consolidated to the 28-mandatory-sheet model |
| v0.7 | 2026-05 | Semantic completeness pass: AG rule class, optional node/cable sheets, audit-trail alignment, value-normalization semantics, and three-level conformance distinction |
| v0.8 | 2026-05 | Schema-stability and interoperability pass: single authoritative sheet-header source, Long-Form attribute validation, mandatory Source_Format rule, stable cable-profile headers, Source_Operation/Object_Role enum treatment, manual-evidence object convention, classification FK validation, and review/provenance rule alignment |
| v0.8.3 | 2026-07 | Content patch from first real-workbook build-and-check experience: `Connection_Point` Element_Type (decouples generated CAEX connection-points from Terminal's mandatory attributes), `SemanticID` normative definition, S2 bulk/range-terminal notation, S3.1 grid-observation clarification, `Cross_Reference_*` extended to Instrument_Loop_Diagram, Wire_Color sourcing clarification, eight missing §9.2 Attribute_Lookup blocks, `Required=TRUE` conformance-severity clarification (non-blocking finding, not a Level-1 defect), and Document_Type-scoped `Rated_Current`/`Input_Voltage`/`Output_Voltage` (required for Terminal_Diagram, optional for Circuit_Diagram). See §13 for the itemized list. |

The pre-v0.8 delta documents are preserved in version-control history; this document supersedes them as the single source of truth. The migration from legacy v0.4 documents (German schema values) is documented in §17.

### 1.3 Implementation Implications

This specification defines **what** a compliant Excel workbook contains, not **how** a tool produces it. The separation enables (a) multiple independent tool implementations producing structurally equivalent workbooks; (b) automated comparison of workbooks across plant scope per principle 5; (c) verification that any workbook conforms to the spec without dependence on the specific tool that produced it.

**What this specification provides** (sufficient to build the Excel and to build the tool that fills it):

- The 28 mandatory sheet structures, column names, datatypes, sheet ordering (§3.0, §A)
- Identifier conventions and sub-element naming (§3.7)
- Source-extraction rules per document type (§4.1 S1, §4.2 S2, §4.3 S3, §4.4 Verschaltungsliste)
- Source-format conventions for PDF, Excel, Verschaltungsliste (§A.7)
- The complete process workflow P0–P9 with pre/post-conditions (§11.4)
- The complete rule catalogs A/C/M/E/K (§11.1–§11.6)
- The complete integrity-rule catalog I1–I26 + I28–I32 (§11.7, §11.9), the aggregation-rule catalog AG1 (§11.10), and validator execution order (§11.8)
- The full lookup tables — Enum_Lookup (§9.3) and Attribute_Lookup (§9.2) — with completeness conventions (§A.24, §A.25)
- The normative reference inventory with verified editions (§16)
- Worked examples per document type (§12.1, §12.2, §12.3)

**What this specification deliberately does not provide:**

- A choice of source-extraction technology — implementations are free to use native PDF text extraction, OCR for scanned PDFs, `openpyxl` for Excel sources, or any other mechanism that produces the `Object` content required by P1
- A choice of LLM provider, RAG architecture, or norm-access mechanism — implementations are free in how they realize symbol classification, terminology resolution, and norm-driven enum encoding
- The content of the normative references themselves — symbol meanings (IEC 60617), classification letters (IEC 81346-2), PCE letters (IEC 62424), function letters (DIN 19227-2), color codes (IEC 60757), etc. are not duplicated here. The spec references norms; it does not replace them (per §16.2 D9)
- Excel-rendering details (font, color, column width, border styles, cell formatting) — these are presentation-layer concerns and do not affect schema conformance

**What implementations SHALL do** to be spec-compliant — three distinct conformance levels:

**Level 1 — Workbook Conformance (structural, mandatory for every spec-compliant workbook):**
- Execute all 10 process steps P0–P9 in sequence per §11.4 (no skipped steps, no stub populations of Object/Cluster sheets)
- Satisfy all workbook-local integrity rules I1–I26 + I28–I32 in §11.7 and §11.9 against the produced workbook. (Aggregation rules AG1 per §11.10 are evaluated at project level, not Level-1 conformance.)
- Conform to the 28-mandatory-sheet structure (§3.0) and naming conventions (§3.7)
- Include the full Enum_Lookup catalog per §9.3 and the full Attribute_Lookup catalog per §9.2 (per completeness conventions in §A.24, §A.25)
- Maintain the single-document invariant (§1.1 principle 6): one workbook per source document, no cross-workbook FKs

**Level 2 — Extraction Tool Conformance (for tools that automate workbook generation from source artifacts):**
- Have access to all normative references in §16.1 (for symbol-to-Element_Type and symbol-to-Classification_Code mappings)
- Implement the source-format-specific extraction conventions in §A.7 (PDF, Excel, Verschaltungsliste)
- Record `Extraction_Method`, `Confidence`, `Extraction_Timestamp` per §A.16 audit fields

**Level 3 — Classification Assurance (for tools that produce Element_Classification rows):**
- Validate `Classification_Code` against the active `Classification_System` per §A.19 typing rule
- For norm-anchored classifications, the tool SHALL be capable of citing the verbatim norm passage (verified anchor); for `Unclassified` rows, `Source_Symbol_Reference` SHALL document the reason
- Manual classifications populate `Element_Classification_Source` with `Extraction_Method = Manual_Entry` per the I12 manual-evidence convention

A workbook may carry Level-1 conformance without the producing tool having Level-2 or Level-3 capability (e.g. a manually authored workbook is Level-1 conformant; the validator does not need Level-2 capability to check it).

**Typical tool architecture (illustrative, not prescriptive):** A tool implementing this specification typically combines (a) deterministic source parsers for title-block fields, terminal-strip designations, and Verschaltungsliste rows; (b) OCR for scanned-PDF sources; (c) LLM-based symbol classification with RAG access to the §16.1 normative texts for IEC 60617 symbol decoding and IEC 81346-2 / IEC 62424 letter assignment; (d) deterministic Excel-generation logic that materializes the 28 mandatory sheets with their full lookup catalogs. Two independent tool implementations following these guidelines should produce workbooks identical in structure and content (deviations would indicate either a spec gap to be reported, or a normative-interpretation difference rooted in the §16.1 references themselves — both addressable without changing the spec's coverage).

---

## 2. Schema Application per Document Type

This section explains how the generic 28-mandatory-sheet schema is applied to each of the three document types in scope (Instrument_Loop_Diagram, Terminal_Diagram, Circuit_Diagram).

### 2.1 Instrument_Loop_Diagram (Stellenplan)

**Definition:** An Instrument_Loop_Diagram (PCE_Request loop diagram, German `Stellenplan`) documents a single process measurement-and-control loop: the sensing element, the transmitter chain, signal processing, and the actuator (where present). The document is structured around one or more `Document_RepresentedItem` rows (one per PCE_Request, e.g. `TU10.F17.FIC` for a flow indication and control loop at position TU10.F17).

**Norm anchors:** IEC 62424 (PCE_Request structure), IEC 81346-1/2 (reference designations), DIN 19227-2 (Sensor function letters), DIN 1319-1 (metrology terminology), IEC 60050-351 (control-technology vocabulary).

**Application of the 28 mandatory sheets:**
- **`Document_ID`** carries one row per Stellenplan sheet; `Document_Type=Instrument_Loop_Diagram`.
- **`Document_RepresentedItem`** carries one row per PCE_Request loop (typically one per sheet). The `Primary_RKZ` follows the S1-rule (see §4.1): `<Position>.<Function>` (e.g. `TU10.F17.FIC`).
- **`Element_ID`** carries the loop's physical elements: sensor (Element_Type=Sensor), transmitter, valve actuator (Element_Type=Valve_Actuator), PLC module (Element_Type=PLC_Module), etc.
- **`Element_Classification`** carries the IEC 81346-2 class letter per element according to the current element-type classification rules in §5 and §8 and, where applicable, IEC 62424 PCE_Category (B/F/T/P/L/…) and PCE_Processing_Function letter combinations.
- **`Element_RepresentedItem_Mapping`** links each element to the PCE_Request RepresentedItem with `Relationship_Type=Primary` (loop-defining element) or `Secondary` (auxiliary element).
- **`Connection_ID` / `Connection_Data`** carry the signal connections within the loop (4–20 mA, digital signal, etc.); fewer rows than in a Terminal_Diagram of comparable area.

**Source extraction:** S1 (§4.1).

**Cross-document linkage:** Loops referenced by their PCE_Request designation in Terminal_Diagrams (e.g. `TU10.F17` annotated next to a terminal in a Klemmenplan) are linked via the shared `Primary_RKZ` prefix — no FK across documents.

### 2.2 Terminal_Diagram (Klemmenplan)

**Definition of Terminal_Diagram:**

A Terminal_Diagram is documentation of the electrical wiring at terminal strips within a control cabinet or distribution panel. For each terminal strip it lists every terminal with its source connections (incoming) and target connections (outgoing), together with properties of the wiring between them (wire color, cross-section, bridges, polarity).

**Normative anchors:**

> ⚠ **Note on norm currency:** Several of the following standards are withdrawn or superseded in the editions cited. They are retained in v0.8 (pre-release) because only these editions are currently accessible. The full list of update needs is in §16.

- DIN EN IEC 81346-1:2024-07 — Structuring principles
- DIN EN 81346-2:2019 — Classification
- DIN EN 60617-3:1996 — Graphical symbols, Part 3: Conductors and connecting devices
- DIN EN 60617-7:1996 — Graphical symbols, Part 7: Switchgear, controlgear and protective devices
- DIN EN 61082-1:2015 — Preparation of documents used in electrotechnology
- DIN EN 60446 [⚠ replaced by DIN EN IEC 60445:2018, see §16] — Identification of conductors by colors
- DIN EN 60757 [⚠ withdrawn, replaced by HD 308 S2 / DIN VDE 0293-308, see §16] — Code for designation of colors
- DIN VDE 0100-200 [⚠ see §16] — Erection of low-voltage installations, definitions
- DIN VDE 0281 [⚠ see §16] — PVC-insulated cables for industrial wiring (NYY, H07V-K)
- DIN 19227-2 [⚠ withdrawn, see §16] — Graphical symbols and identification letters for process control technology
- DIN 1319-1:1995-01 — Fundamentals of metrology — General terms
- IEC 60050-351:2014-09 — International Electrotechnical Vocabulary, Part 351: Control technology (Sensor definition)

#### 2.2.1 Application of the common schema to Terminal_Diagram

| Sheet | Terminal_Diagram Usage |
|---|---|
| `Document_ID` | 1 row with `Document_Type=Terminal_Diagram` |
| `Document_Data` | Title-block attributes (project, plant, cabinet designation, author, revision date) |
| `Document_RepresentedItem` | N rows: one per Terminal_Strip (RepresentedItem_Type=Terminal_Strip), or one per cabinet (RepresentedItem_Type=Control_Cabinet); see §7 |
| `Object` | PDF/Excel atoms (text cells, lines, rectangles of the terminal-strip representation) |
| `Cluster` | Containment cluster per terminal-strip block; proximity cluster for row grouping |
| `Element_ID` | N terminals + N terminal strips + switchgear + protective devices (all as InternalElement or ExternalInterface per CAEX model) |
| `Connection_ID` | One stem-data row per wire/strand (From=terminal A, To=terminal B or element) |
| `Connection_Data` | Wire_Color, Polarity, Cross_Section, Cable_Number, Connection_Type per Connection_ID |
| `Connection_Data_Source` | Provenance to source object per Connection_Data row |
| `Layer_ID` | Useful for structured Terminal_Diagrams with layer separation (e.g. by voltage level 230VAC, 24VDC, Signal_Line); optional — see best-practice example in §2.2.3 |
| `Element_Classification` | Multiple classifications per element per IEC 81346-2 + IEC 60617 as needed |

#### 2.2.2 Source Formats for Terminal_Diagram

Terminal_Diagrams typically come as Excel, Word, or PDF tables. Object extraction is source-specific:

- **PDF Terminal_Diagram:** PDF parser per A1–A5 (as for Instrument_Loop_Diagram)
- **Excel Terminal_Diagram:** Cell-based; each non-empty cell becomes a Text-Object; column headers become their own objects with Source_Role=Label
- **Word table:** analogous to Excel

The A-rules remain valid; the `Source_Operation` column is populated with `Cell` for Excel sources (new Enum_Lookup value).

#### 2.2.3 Best Practice: Layer Schema for Terminal_Diagram

For structured Terminal_Diagrams (multiple voltage levels, separated functional sections), use of `Layer_ID` is recommended. Typical layer schema for a control cabinet with mixed voltage levels:

| Layer_ID | Description | Typical contents |
|---|---|---|
| L.1 | 230V_AC_Supply | Supply terminal strip, FI/LS protective switches |
| L.2 | 230V_AC_Distribution | Consumer terminal strips 230V, contactors for 230V loads |
| L.3 | 24V_DC_Supply | Power-supply terminal strip, 24V main fuses |
| L.4 | 24V_DC_Distribution | Consumer terminal strips 24V (sensors, valves, PLC) |
| L.5 | Signal_Line_Analog | Signal terminal strips 4–20mA / 0–10V, PLC analog input modules |
| L.6 | Signal_Line_Digital | Digital-signal terminal strips, PLC digital input/output modules |
| L.7 | Protective_Elements | Fuses, FI switches (if recorded separately) |
| L.8 | Control | Contactors, auxiliary contactors, control relays |

Concrete layer assignment is project-specific and is held in `Layer_ID` of the document. Terminal strips link to the matching layer via `Element_ID.Layer_ID`.

### 2.3 Circuit_Diagram (Stromlaufplan)

**Definition:** A Circuit_Diagram (German `Stromlaufplan`) represents an electrical circuit as a set of normalized symbols (per IEC 60617) organized into vertical current paths. Each path carries one logical signal/current flow from top (positive rail) to bottom (negative rail or neutral). Primary circuits handle power distribution (typically 400V 3-phase); secondary circuits handle control logic (typically 24VDC or 230VAC).

**Norm anchors:** IEC 81346-1/2 (reference designations), IEC 60617-2/-6/-7/-8 (graphical symbols), DIN EN 61082-1 (preparation of documents).

**Document_Subtype:** A Circuit_Diagram is further classified as `Primary` or `Secondary` via the reserved `Document_Subtype` attribute (§9.1, §9.2). This distinction is mandatory for Circuit_Diagram documents.

**Application of the 28 mandatory sheets:**
- **`Document_ID`** carries one local row per Stromlaufplan logical sheet with `Document_Type=Circuit_Diagram`. `Document_Subtype` is stored as a `Document_Data` row with `Attribute_Name=Document_Subtype` and `Attribute_Value ∈ {Primary, Secondary}`.
- **`Element_ID`** carries each spatially appearing sub-element of a switching device — `Coil`, `Main_Contact`, `Auxiliary_Contact`, `Indicator_Lamp` (see §5.13) — plus all other Element_Types (Sensor, Motor, Fuse, Switch, etc.) reused from the Terminal_Diagram catalog (§5.1–§5.12).
- **`Element_Data.Current_Path_Number`** records the vertical grid position of each Element_ID.
- **`Element_Data.Contact_Designation`** records the terminal identifier per contact (e.g. `1/2`, `13/14`).
- **`Element_Classification`** carries IEC 81346-2 class (Q for switching, S for manual switches, P for indicators) plus IEC 60617 Part 7 / 8 item code.
- **`Connection_ID` / `Connection_Data`** carry the wires between `Connection_Point` sub-Element_IDs (per CAEX connection-point convention in §5.13; `Element_Type=Connection_Point` as of v0.8.3).

**Source extraction:** S3 (§4.3). Alternative source format: Verschaltungsliste (§4.4).

**Cross-document linkage:** Switching-device sub-elements (Coil + Contacts) appearing across Primary and Secondary Circuit_Diagrams (and possibly cross-linked to a Terminal_Diagram-modeled Contactor aggregate) are linked via shared `Primary_RKZ` prefix (e.g. all elements with `Primary_RKZ LIKE '-K1:%'` belong to contactor `-K1`). Cross-document integrity is enforced by AG1 (§11.10) at the project-aggregation level.

**Multi-page convention:** Per §2.4, each logical Stromlaufplan sheet is represented by one separate workbook with exactly one local `Document_ID` row. A plant's Primary and Secondary Stromlaufplan sheets are linked at project level by identical `Project_Name` values in `Document_Data`.

---

### 2.4 Multi-Page Source Documents — Pagination Convention (universal)

This convention applies to all document types (Instrument_Loop_Diagram, Terminal_Diagram, Circuit_Diagram).

A source package may contain multiple physical pages or multiple logical sheets. The schema applies the **Single-document invariant** from §1.1 principle 6 strictly:

1. **One workbook contains exactly one `Document_ID` row.** One logical engineering document is represented by one workbook.
2. **One logical sheet with its own title block is one separate workbook.** A `Stromlaufplan_Primär` sheet and a `Stromlaufplan_Sekundär` sheet of the same plant are therefore two separate workbooks, not two `Document_ID` rows in one workbook.
3. **Project membership across these workbooks** is recorded by identical `Document_Data` rows with `Attribute_Name=Project_Name` and equal `Attribute_Value` after the project-specific normalization rules. Cross-workbook checks are aggregation-layer checks, not workbook-local FK checks.
4. **Sheet number / page index** of the source document is recorded in `Document_Data` with an attribute such as `Sheet_Number` when populated in the source title block. It is not a primary key.
5. **Multi-page single-logical-document sources** remain one workbook with one `Document_ID`. Physical source pagination is recorded through `Object.Page_Number` and the corresponding source-provenance rows.

The distinction is governed by the source document's own logical title-block structure. A new title block that starts a new logical engineering document starts a new workbook.

## 3. Sheet Architecture

### 3.0 Sheet Catalog (28 mandatory sheets)

The v0.8 schema uses **28 mandatory sheets**, all generic across the three document types. Each sheet has a specific purpose in the schema's data flow.

| # | Sheet | Purpose | Populated in step |
|---|---|---|---|
| 1 | `Rules` | Authoritative rule catalog (Static; entire content of §11) | Static |
| 2 | `Schema_Metadata` | Schema_Version and Lookup_Version metadata | Static |
| 3 | `Document_ID` | Document identification + applied versions | P0 |
| 4 | `Document_Data` | Title-block attributes (long-form) | P0 |
| 5 | `Revision_Data` | Revision history | P0 |
| 6 | `Document_RepresentedItem` | What the document is about (per S-rule) | P0 (header) + P8 |
| 7 | `Object` | Atomic objects from the source document | P1 |
| 8 | `Cluster` | Cluster metadata | P3 |
| 9 | `Object_Cluster` | Object-to-cluster membership (M:N) | P3 |
| 10 | `Elements_TopDown` | Top-Down identified elements | P2 |
| 11 | `Elements_from_Cluster` | Cluster-derived elements | P4 |
| 12 | `Match_Result` | Match reconciliation between TopDown and Cluster-derived | P5–P6 |
| 13 | `Element_ID` | Validated consolidated elements | P7 |
| 14 | `Element_RepresentedItem_Mapping` | SPoT for Element ↔ RepresentedItem | P8 |
| 15 | `Element_Data` | Element attributes (long-form, key-value pairs) | P8 |
| 16 | `Element_Data_Source` | Provenance for `Element_Data` rows | P8 |
| 17 | `RepresentedItem_Data` | RepresentedItem attributes (long-form) | P8 |
| 18 | `RepresentedItem_Data_Source` | Provenance for `RepresentedItem_Data` rows | P8 |
| 19 | `Element_Classification` | Norm-based classifications for classified schema objects | P8 |
| 20 | `Connection_ID` | Topological connections | P9 |
| 21 | `Connection_Data` | Connection attributes (long-form, key-value pairs) | P9 |
| 22 | `Connection_Data_Source` | Provenance for `Connection_Data` rows | P9 |
| 23 | `Layer_ID` | Project/document-type-specific layer structure | P8 |
| 24 | `Attribute_Lookup` | Catalog of allowed attribute names per scope + Type_Constraint (§9.2, §9.4) | Static |
| 25 | `Enum_Lookup` | Catalog of allowed enum values per Field_Name (§9.1, §9.3) | Static |
| 26 | `Document_Data_Source` | Provenance for `Document_Data` rows | P0 |
| 27 | `Revision_Data_Source` | Provenance for `Revision_Data` rows | P0 |
| 28 | `Element_Classification_Source` | Provenance for `Element_Classification` rows | P8 |

**Optional sheets** (project-specific, not required for spec conformance):

| # (optional) | Sheet | Purpose | Reference |
|---|---|---|---|
| O1 | `Designation` | Advanced reference-designation modeling with normalized forms and aspect (per IEC 81346-1) for projects needing cross-workbook joins beyond Primary_RKZ-prefix matching | §A.O1 |
| O2 | `Electrical_Node` | Star-point / ring-node modeling for sources with multi-endpoint nodes  | §A.O2 |
| O2b | `Electrical_Node_Member` | Member normalization for Electrical_Node; required iff `Electrical_Node` is active | §A.O2b |
| O3 | `Cable_Data` | Cable-as-asset modeling with length, route, and shielding attributes; activates the generic Asset cable profile via `Schema_Metadata.Cable_Modeling_Profile=Asset` | §A.O3 |

> *Note on sheet count (historical): relocated to Appendix B (v0.8.2 structure patch); content unchanged.*

**Sheet ordering in the workbook (D2):** Excel workbooks created from this specification **SHALL** contain the 28 mandatory sheets in the exact order listed in this Catalog (Sheet #1 `Rules` first, …, Sheet #28 `Element_Classification_Source` last). Optional sheets, when present, follow after Sheet #28 in the order O1 → O2 → O2b → O3. The ordering is part of the schema, not a cosmetic decision. Tools loading the workbook may rely on Catalog position when reading.

**Rename note (`PDF_Operation` → `Source_Operation`):** relocated to Appendix B (v0.8.2 structure patch); content unchanged. Tools migrating from earlier versions: see Appendix B.

**Per-sheet column definitions** are documented in **Appendix §A.1–§A.28** in the same order as the mandatory Sheet Catalog. Optional sheets are documented in **§A.O1–§A.O3**. The Appendix is the authoritative source for sheet headers.

### 3.1 Renaming `Connection_Data` → `Connection_ID`

**Reason:** Consistency with the v0.4 pattern (stem-data sheet named after its primary key: `Document_ID`, `Element_ID`, `Match_ID`, `Cluster_ID`). The former `Connection_Data` held stem data (From/To/Status), but bore a data-sheet name. The rename closes this inconsistency.

**Column authority:** This section is historical and explanatory only. The authoritative header definition for the stem sheet is **Appendix §A.20 `Connection_ID`**. Implementations SHALL NOT derive sheet headers from this historical section.

### 3.2 Sheet `Connection_Data`

**Purpose:** Variable attributes per connection, analogous to `Element_Data` and `RepresentedItem_Data`.

**Column authority:** The authoritative header definition for `Connection_Data` is **Appendix §A.21**. The Appendix includes canonical value fields, raw-value preservation, normalization fields, parsing status, and semantic identifiers. Implementations SHALL NOT use a shortened legacy header definition.

### 3.3 Sheet `Connection_Data_Source`

**Purpose:** Provenance of every `Connection_Data` row, analogous to `Element_Data_Source`.

**Column authority:** The authoritative header definition for `Connection_Data_Source` is **Appendix §A.22**. The Appendix includes source-object references and audit fields. Implementations SHALL NOT use a shortened legacy header definition.

### 3.4 Extension of `Attribute_Lookup` with new Scope value

The existing value range for `Attribute_Lookup.Scope` (Document, Element, RepresentedItem) is extended by **Connection**. This enables `Connection_Data.Attribute_Name` validation against `Attribute_Lookup` with `Scope=Connection`. I13 is extended accordingly: `Attribute_Name` validation applies to `Document_Data`, `Element_Data`, `RepresentedItem_Data`, and `Connection_Data`; the value range of the `Scope` field that I13 validates against includes `Connection`.

### 3.5 Historical: Impact of the v0.4→v0.5 Connection_Data → Connection_ID Rename on Pre-v0.5 I-Rules

*Relocated to Appendix B (v0.8.2 structure patch); content unchanged, original numbering retained there.*

### 3.6 Historical: Impact of the v0.4→v0.5 German→English Language Migration on Pre-v0.5 Rule Texts

*Relocated to Appendix B (v0.8.2 structure patch); content unchanged, original numbering retained there.*

### 3.7 Identifier and Naming Conventions (D1)

This section is normative. Every ID generated for any sheet **SHALL** follow these patterns; implementations that diverge are not spec-compliant.

#### 3.7.1 General ID format

```
<Prefix>.<Sequential_Integer>
```

- **Prefix** is a fixed string per sheet (see §3.7.2 table); always uppercase, no spaces.
- **Sequential_Integer** is 1-based, incremented per row, **without zero-padding** (use `1`, `2`, …, `42`, …, `123`, not `001` or `D-0001`).
- **Separator** is exactly one dot `.` between prefix and integer.
- **Examples:** `D.1`, `E.1`, `E.42`, `MAP.7`, `O.123`.

#### 3.7.2 Prefix table per sheet

| Sheet | ID column | Prefix |
|---|---|---|
| `Document_ID` | `Document_ID` | `D` |
| `Document_Data` | `Document_Data_ID` | `DD` |
| `Revision_Data` | `Revision_ID` | `R` |
| `Document_RepresentedItem` | `RepresentedItem_ID` | `RI` |
| `RepresentedItem_Data` | `RepresentedItem_Data_ID` | `RID` |
| `Object` | `Object_ID` | `O` |
| `Cluster` | `Cluster_ID` | `CL` |
| `Elements_TopDown` | `Element_TopDown_ID` | `ETD` |
| `Elements_from_Cluster` | `Element_from_Cluster_ID` | `EFC` |
| `Match_Result` | `Match_ID` | `M` |
| `Element_ID` | `Element_ID` | `E` |
| `Element_RepresentedItem_Mapping` | `Mapping_ID` | `MAP` |
| `Element_Data` | `Element_Data_ID` | `ED` |
| `Element_Classification` | `Classification_ID` | `EC` |
| `Connection_ID` | `Connection_ID` | `C` |
| `Connection_Data` | `Connection_Data_ID` | `CD` |
| `Layer_ID` | `Layer_ID` | (project-specific pattern, e.g. `5.0-1`; no prefix imposed — Layer_ID semantics are project-defined per §2.2.3) |
| `Attribute_Lookup` | `Lookup_ID` | `AL` |
| `Enum_Lookup` | `Enum_Lookup_ID` | `EL` |

The Provenance-Source sheets (`Element_Data_Source`, `RepresentedItem_Data_Source`, `Connection_Data_Source`) **do not have their own primary key**; they hold the FK to the parent `*_Data_ID` plus `Source_Object_ID`. No separate prefix needed.

#### 3.7.3 Sub-element ID convention (CAEX connection-points)

When an `Element_ID` row represents a connection-point sub-element of a parent Element (per §5.13 CAEX convention), its ID is constructed as:

```
<Parent_Element_ID>.<connection_point_role>
```

- `Parent_Element_ID` is the ID of the InternalElement that owns this ExternalInterface
- `connection_point_role` is a lower_snake_case role descriptor (e.g. `signal_out`, `signal_in`, `input`, `output`, `command_in`, `coil_a1`, `coil_a2`, `main_l1`, `main_l2`, `main_l3`, `nc_21`, `nc_22`, `no_13`, `no_14`).
- **Examples:** `E.1.signal_out`, `E.3.input`, `E.7.coil_a1`, `E.42.main_l1`.

The dot `.` separator is reused (not changed to `-` or `:`) so the ID remains uniformly parseable.

#### 3.7.4 Sequential numbering rules

- Within one sheet, IDs are assigned in the order rows are created (P0–P9 sequence per §11.4).
- IDs are **never reused** within a workbook: if a row is deleted, its ID is retired.
- IDs are **not stable across rebuilds**: a re-extraction of the same source PDF may produce different sequential numbers; downstream consumers must not depend on the specific integer, only on the FK relationships within one workbook.
- Sub-element IDs (per §3.7.3) inherit the parent's stability: when E.1 is renumbered to E.2 in a rebuild, E.1.signal_out becomes E.2.signal_out.

---

### 3.8 Core-Minimum Designation Normalization

The core-minimum designation normalization is part of the mandatory workbook schema and does not require the optional `A.O1 Designation` sheet. Every workbook SHALL apply the following rule to `Primary_RKZ` values in `Element_ID` and `Document_RepresentedItem`:

1. Trim outer whitespace and collapse internal whitespace to single spaces.
2. Preserve source-document case; aggregation matching is case-insensitive.
3. Preserve the `:` separator between aggregate prefix and sub-element designation, for example `-K1:11`.
4. Preserve the leading product-aspect hyphen `-` when present in the source.
5. Store the normalized value in `Primary_RKZ`. Preserve the raw source string through the linked source evidence. For `Element_ID`, this evidence is resolved through `Source_Match_ID → Match_Result → Elements_from_Cluster.Source_Cluster_ID → Object_Cluster → Object.Content_Text` where the source designation was extracted. For `Document_RepresentedItem`, the evidence is resolved through the source objects used during the applicable S-rule population and the corresponding data-source rows for source-derived attributes. The optional `A.O1 Designation` sheet may store explicit `Raw_RKZ` and `Normalized_RKZ` pairs when projects require direct raw/normalized designation auditing.

**Clarification:** The above resolution chains are the **authoritative method** for retrieving the raw (pre-normalization) source string of a `Primary_RKZ` in v0.8. Workbooks SHALL NOT introduce ad-hoc shadow columns such as `Raw_Primary_RKZ` or `Primary_RKZ_Original` on `Element_ID` or `Document_RepresentedItem`; if direct raw/normalized pairs are needed for project tooling, the optional `A.O1 Designation` sheet (with `Raw_RKZ` and `Normalized_RKZ` columns) is the structurally correct mechanism. Schema-internal raw-preservation in v0.8 is therefore indirect via provenance, and this is the deliberate v0.8 design choice; explicit `Raw_Primary_RKZ` / `Normalized_Primary_RKZ` columns on the core sheets are deferred to v1.0 if implementation experience shows the indirect chain is too cumbersome for common queries.

This rule is the mandatory cross-workbook matching contract used by AG1 and by project-level Primary_RKZ-prefix matching. The optional `A.O1 Designation` sheet adds aspect decomposition and richer designation tracking; it does not define the mandatory minimum.

### 3.9 SemanticID Convention (added v0.8.3)

`SemanticID` (String, optional) is present on every mandatory sheet (§A.1–§A.28) but was not normatively defined in v0.8/v0.8.2 beyond its column type. This section fixes its meaning.

**Definition:** `SemanticID` is an optional, tool- or project-assigned key used to mark that two or more rows — on the same sheet, on different sheets, or (informatively) across different workbooks — refer to the **same real-world entity or fact**, when their own natural identifiers (`Primary_RKZ`, `Content_Text`, `Element_Data.Attribute_Value`, etc.) differ as literal strings but are judged to denote the same thing.

**Motivating case:** A source document may refer to one physical device with slightly different text depending on context — e.g. a Terminal_Diagram target column reading `"Beckhoff 230VAC/24VDC"` in one row and `"PE Beckhoff 230VAC/24VDC"` in another, for the same physical power supply. Per Principle 4 (§1.1) and the source-faithful-identity rule, each distinct source string legitimately produces its own `Element_ID` row with its own `Primary_RKZ` (no invention, no silent merging of source text). `SemanticID` lets a tool or reviewer additionally record — without touching `Primary_RKZ` — that both rows are believed to denote the same physical entity, by giving both rows the same `SemanticID` value.

**What `SemanticID` is not:**
- It is **not** a replacement for `Primary_RKZ`, `Object_ID`, or any other structural identifier. It carries no FK semantics and is not referenced by any I-rule.
- It does **not** cause consolidation of rows within the workbook. Two `Element_ID` rows sharing a `SemanticID` remain two distinct, independently valid rows; no rule merges them.
- It is **not validated** by any integrity rule in §11. A workbook with no `SemanticID` values populated anywhere is fully v0.8.3-conformant (the column remains optional, matching its v0.4–v0.8.2 status).
- It does **not** establish cross-document identity. Using the same `SemanticID` string in two different workbooks is an informative hint only, subject to the same best-effort caveat as any other cross-document matching (`K2`); it does not upgrade to a guaranteed identity relationship, and no AG-rule currently consumes it.

**Recommended population practice (non-normative):** a stable value derived from the judged real-world entity (e.g. a manufacturer+model+cabinet string, or a project-internal asset tag), assigned consistently by whichever mechanism (tool, LLM classification, manual review) determines the equivalence, with the determination's rationale traceable the same way any other classification decision is — via the row's own provenance (`*_Data_Source` / `Element_Classification_Source`), not via `SemanticID` itself.

## 4. Source Extraction Rules

Source-extraction rules define how each document type's title-block, designations, and source structure map to schema rows. One S-rule per document type; tools apply the matching rule based on `Document_Type`.

### 4.1 S1 — Instrument_Loop_Diagram extraction (Stellenplan)

**Document_ID derivation:** Extract from the title-block (Schriftfeld) of the source document by combining the `Position` field and the `Function_Designation` (PCE letter combination per IEC 62424 / DIN 19227-2) with `.` as separator, conforming to IEC 81346 function-aspect hierarchy notation.

**Example for pumping-station sheet TU10.F17:**
- `Position = TU10.F17`
- `Function = FIC` (Flow Indication and Control per IEC 62424 Table 2)
- → `Primary_RKZ = TU10.F17.FIC`

The optional function-aspect prefix `=` (per IEC 81346-1 §5.2) is included if present in the source.

**Typical cardinality:** One `Document_RepresentedItem` per Stellenplan sheet (one PCE_Request per loop diagram). Where multiple instrument loops share a sheet, multiple `Document_RepresentedItem` rows are generated.

**Element extraction:** Every distinct device symbol on the sheet (sensors, transmitters, valves, PLC modules, terminal references) produces one `Element_ID` row. Cross-references to terminals on Klemmenplan sheets are recorded via shared `Primary_RKZ` (designation), not via FK — those terminals exist as `Element_ID` rows in the corresponding Klemmenplan document.

**Classification:** Every `Element_ID` receives an `Element_Classification` row with `Classification_System=IEC 81346-2` (class letter B/F/Y/M/etc.) and, where applicable, additional rows for `Classification_System ∈ {IEC 62424, IEC 60617-3, DIN 19227-2}`.

**PCE function-channel suffix `.<Signal_Direction>` and `.<Signal_Type>`:** Stellenplan source documents append channel-specific suffixes to the PCE function-aspect designation. Example from the pumping-station sheet TU10.F17: the full designation `=0.H1.T1.TU10.F17.FIC.I` denotes the **input** signal channel of the FIC loop (PLC AI module), and `=0.H1.T1.TU10.F17.FIC.A+` denotes the **analog-positive** signal output channel. These suffixes identify individual signal-path Element_IDs within the loop, not separate logical loops.

| Suffix | Meaning | Source norm |
|---|---|---|
| `.I` | Input signal channel (e.g. PLC digital/analog input) | IEC 62424 §6.6.2 PCE_Processing_Function detail |
| `.O` | Output signal channel (e.g. PLC digital/analog output) | IEC 62424 §6.6.2 |
| `.A+` / `.A-` | Analog positive/negative signal channel | IEC 62424 (analog-detail) |
| `.D` | Digital signal channel | IEC 62424 |

**Modeling:** The full designation including channel suffix is captured as `Element_ID.Primary_RKZ` (e.g. `=0.H1.T1.TU10.F17.FIC.I`) per IEC 81346-1 §5.2 (function-aspect notation). The bare PCE_Request prefix (without channel suffix) — `TU10.F17.FIC` — remains the `Document_RepresentedItem.Primary_RKZ`. The channel suffix itself is additionally stored as `Element_Data.PCE_Channel_Suffix` (Scope=Element, Type_Constraint=Document_Type=Instrument_Loop_Diagram) for direct queryability. **Enum_Lookup** for `PCE_Channel_Suffix`: `I`, `O`, `A+`, `A-`, `D` (open list; project-specific extensions permitted via the K-rule free-form convention).

### 4.2 S2 — Terminal_Diagram extraction

**S2 — Terminal_Diagram RKZ extraction**

A Terminal_Diagram typically documents multiple RepresentedItems per document (one per Terminal_Strip). Extraction proceeds in four steps:

1. **Document_ID** is built from the title block following the pattern:

  `<Plant-Aspect>.<Cabinet-or-Position-Aspect>` with `.`-separator, IEC 81346-conformant.

  Example for HC10 Terminal_Diagram: `=0.H1.T1.HC10` (where `=0.H1.T1` is the higher-level plant position and `HC10` is the cabinet sub-unit).

  For Terminal_Diagrams without an explicit cabinet sub-unit in the title block: Document_ID = `<Plant-Aspect>` (analogous to Instrument_Loop_Diagram).

2. **Terminal_Strip identification:** every explicitly named Terminal_Strip designation (`-X1`, `-X2`, `-X3`, …) produces a row in `Document_RepresentedItem` with `RepresentedItem_Type=Terminal_Strip`. The Primary_RKZ follows the pattern:

  `<Document-Plant>.<Terminal_Strip>` with `.`-separator

  Example: `=0.H1.T1.HC10.-X1` (hyphen normalization per S2.2 below).

3. **Terminal extraction:** every terminal of a Terminal_Strip becomes its own row in `Element_ID` with:
  - `Element_Type=Terminal`
  - `Primary_RKZ` in the pattern `<Terminal_Strip>:<Terminal-Number>[/<Polarity>]`, e.g. `-X1:11/L3` or `-X2:5`
  - `Parent_Element_ID` references the Terminal_Strip element ID
  - `Layer_ID` per the functional layer (Supply, Distribution, Signal_Line, etc.) — see best-practice schema §2.2.3

4. **Connection extraction:** for each row in the source Terminal_Diagram, **one** Connection_ID row is created linking the terminal with its outgoing/incoming endpoint. Wire color, polarity, cross-section, etc. become Connection_Data rows.

**Topic_Identification_Status:**
- `Confirmed`: Terminal_Strip uniquely named in the source document
- `Inferred`: Terminal_Strip derivable from column header and terminal designation but not explicitly listed as a header
- `Ambiguous`: multiple plausible interpretations

#### 4.2.1 S2.1 Polarity / Strand Separator Convention

The notation `X1:11/L3` decomposes by convention as:

| Part | Meaning | Standard |
|---|---|---|
| `-X1` | Terminal_Strip designation (product aspect) | IEC 81346-1 |
| `:` | Separator Terminal_Strip → terminal number | — |
| `11` | Terminal number (sequential) | — |
| `/` | Separator terminal number → polarity/strand | — |
| `L3` | Polarity/strand identification | DIN VDE 0100-200 |

If the polarity notation is missing (`-X2:6`), polarity is captured as a separate attribute in `Element_Data` with `Attribute_Name=Polarity` — if derivable. Otherwise it remains empty.

#### 4.2.2 S2.2 Terminal_Strip Prefix Normalization

Source documents notate Terminal_Strip designations inconsistently: sometimes with leading hyphen (`-X1`, IEC 81346-conformant for product aspect), sometimes without (`X1`). Schema v0.5 fixes a uniform normalization convention:

**Convention:** The hyphen prefix `-` is **always prepended** in the `Primary_RKZ` of every Terminal_Strip and every Terminal, regardless of the source document.

- Source document `X1:11/L3` → schema RKZ `-X1:11/L3`
- Source document `-X1:11/L3` → schema RKZ `-X1:11/L3` (unchanged)

Rationale follows IEC 81346-1: the hyphen denotes the product aspect. Normalization ensures machine-readable uniqueness and avoids semantically identical but syntactically different RKZ values.

#### 4.2.3 S2.3 Bulk/Range Terminal Notation (added v0.8.3)

Some terminal strips (typically factory-supplied power-supply blocks, e.g. a WAGO 787-series feed-in terminal) are documented in the source not as individually enumerated terminals but as a **bulk range** sharing one function, using a dot-separated range notation distinct from the single-terminal colon notation of §4.2.1 — e.g. `X3.1 - X3.4` (labelled `G+`) and `X3.5 - X3.8` (labelled `G-`) for one physical 8-position feed-in terminal.

**Convention:**

1. When the source names a terminal range as a single bulk-labelled unit (rather than enumerating each terminal number individually with its own row/annotation), it is modeled as **one `Element_ID` row per named range**, not as one row per individual terminal number within it. `Primary_RKZ` follows the pattern `<Strip>.<FirstNumber>-<Strip>.<LastNumber>` exactly as written in the source (e.g. `-X3.1-X3.4`), preserving whatever separator the source itself uses (this schema does not force the range notation's `.` separator to match the `:` separator used elsewhere in the same document — see the worked caveat below).
2. `Element_Data.Terminal_Number` for a range-modeled terminal carries the verbatim range string (e.g. `"1-4"`); `Terminal_Strip_Designation` carries the strip designation as usual.
3. **Mixed-notation cross-references:** a source document that uses bulk range notation for one strip's own section header MAY still refer to individual positions within that range elsewhere using the document's normal single-terminal notation (e.g. a different terminal's target column reading `"X3:1 (V+, Wago)"`). Such a reference is resolved to whichever range-modeled `Element_ID` numerically contains the referenced position (e.g. `X3:1` and `X3:6` both resolve against `-X3.1-X3.4` / `-X3.5-X3.8` by range membership). This is a **designation-resolution convention**, not a re-normalization of the source text: the raw referring text (`"X3:1"`) is preserved verbatim in the originating `Object`/`Connection_Data_Source`; only the resolved `Connection_ID.To_Element_ID` FK points at the containing range element.
4. An implementation MAY instead choose to model each physical terminal individually (one `Element_ID` per terminal number within the range, synthesizing the individual numbers) if a project requires per-terminal addressability; both treatments are v0.8.3-conformant. An implementation SHALL NOT silently do only part of one treatment (e.g. some rows range-modeled, others individually enumerated, for the *same* range) — pick one treatment per range and apply it consistently within that workbook.

---

### 4.3 S3 — Circuit_Diagram extraction

**S3 — Circuit_Diagram extraction**

A Circuit_Diagram represents an electrical circuit as a set of normalized symbols (per IEC 60617) organized into vertical current paths. Extraction proceeds in four steps parallel to S2:

1. **Document_ID** is built from the title block following the same pattern as S2 (`<Plant-Aspect>.<Cabinet-or-Position-Aspect>`, IEC 81346-conformant). The Document_Type is `Circuit_Diagram`; the Document_Subtype attribute (`Primary` or `Secondary`) is read from the title-block label (`Stromlaufplan_Primär` → `Primary`, `Stromlaufplan_Sekundär` → `Secondary`); the German title-block string is preserved verbatim in `Object.Content_Text` per §0.1.

2. **Element extraction:** every distinct symbol on the sheet produces one `Element_ID` row. For switching devices (contactors, auxiliary contactors, relays) that appear in spatially-separated parts (coil at one current path, contacts at others), each spatial appearance is **one Element_ID**:
  - `Element_Type=Coil` for the coil portion (terminals A1/A2)
  - `Element_Type=Main_Contact` for each main contact (1/2, 3/4, 5/6)
  - `Element_Type=Auxiliary_Contact` for each auxiliary contact (13/14, 21/22, 53/54)
  - `Primary_RKZ` follows the pattern `<Aggregate-Designation>:<Sub-Designation>` (analog to Terminal pattern `-X1:11/L3`): e.g. `-K1:A1/A2` (Coil), `-K1:1/2` (Main_Contact), `-K1:13/14` (Auxiliary_Contact)
  - `Current_Path_Number` attribute records the spatial position (path number from sheet grid)
  - `Contact_Designation` attribute records the contact identifier (e.g. `1/2`, `13/14`) for Main_Contact and Auxiliary_Contact

3. **Connection extraction:** wires between Element_IDs produce `Connection_ID` rows; attributes (Wire_Color, Cable_Number, polarity) go into `Connection_Data`. Identical to S2 mechanics.

4. **Classification:** every Element_ID receives at minimum one `Element_Classification` row with `Classification_System=IEC 81346-2` (class letter per device) and one with `Classification_System ∈ {IEC 60617-2, -6, -7, -8}` (per symbol family). For switching-device sub-elements, the IEC 60617 reference is part 7 with item codes derivable from §5.13.

#### 4.3.1 S3.1 Current Path Identification

The vertical grid columns of a Circuit_Diagram (typically numbered 1–8 or similar) define Current_Path_Numbers. Every Element_ID placed on the sheet receives the `Current_Path_Number` attribute corresponding to its horizontal grid position, **as observed from the source grid** — never computed from raw coordinates. If the source uses a secondary axis (e.g. row labels A–F), it is recorded in `Object` but not propagated to `Element_Data`.

**Clarification (v0.8.3):** "As observed from the source grid, never computed from raw coordinates" governs the *source of truth*, not the *arithmetic permitted to resolve it*. Most Circuit_Diagram sheets print the grid-column numbers (`1`…`8`) only once, at the sheet's top/bottom border, not repeated next to every element — a human reader determines an element's path number by visually noting which printed column it falls under, which is inherently a position comparison. This is permitted and is **not** the "computed from raw coordinates" case the rule forbids. What the rule forbids is *inventing* a path number from an element's absolute position when no printed grid-column reference exists at all on the sheet (e.g. assigning `Current_Path_Number` to a document that has no path-numbered grid, or extrapolating a path number arithmetically beyond what the printed grid actually spans). Concretely: comparing an element's horizontal position against the positions of the printed grid-column header labels (`1`…`8`) to determine which printed column it falls under is the required method when no closer per-element annotation exists; it is source-observation, not coordinate invention.

#### 4.3.2 S3.2 Symbol Classification (IEC 60617 Parts 2/6/7/8)

Every Element_ID arising from S3 receives at least one `Element_Classification` row referencing the appropriate IEC 60617 part and item code. The authoritative table of Element_Type → IEC 60617 item code for all Circuit_Diagram-relevant elements is held in **§5.13** (single source of truth — no duplicate listing here, to avoid synchronization risk). All codes in §5.13 have been verified against the project's IEC 60617 norm PDFs (Parts 2/6/7/8, edition 1997-08).

When the source symbol does not match any IEC 60617 item, `Classification_Code=Unclassified` with `Source_Symbol_Reference` recording the as-drawn glyph.

#### 4.3.3 S3.3 Cross-Reference Resolution via Primary_RKZ

**Within-document distributed device linkage (Primary_RKZ prefix match):** For any switching device appearing distributed within the current sheet/workbook, the cross-reference is resolved by Primary_RKZ prefix match: all Element_IDs with `Primary_RKZ LIKE '<Aggregate>:%'` belong to the same physical device within the current workbook. Example: `SELECT * FROM Element_ID WHERE Primary_RKZ LIKE '-K1:%'` returns the coil and contacts of contactor K1 that are present in the current workbook. Cross-workbook completion is handled by AG1 (§11.10). No structural aggregation (no `Parent_Element_ID` linking sub-elements to a virtual aggregate within the Circuit_Diagram) is required — the device exists only as the set of its appearances.

**Textual cross-reference notation `(<Doc>.<Path>-<Row>)`:** In addition to the implicit RKZ-prefix linkage above, Circuit_Diagrams use an **explicit textual cross-reference notation** drawn next to a target line/symbol. The format is `(<Document_Number>.<Current_Path_Number>-<Row_Letter>)`, in parentheses. Example from HC10 Primärstromkreis: `(001.8-A)` next to the supply lines `-L1/-L2/-L3/-N/-PE` means "this line is continued at document 001, current path 8, row A". Components:

| Field | Meaning | Source |
|---|---|---|
| `Document_Number` | The target document, numbered per project convention (typically the 3-digit sheet number from the title-block) | `Document_Data.Sheet_Number` of the referenced document |
| `Current_Path_Number` | The vertical grid position (1, 2, 3, …) on the target sheet | `Element_Data.Current_Path_Number` of the target Element_ID |
| `Row_Letter` | The horizontal grid row (A, B, C, D, …) on the target sheet | `Element_Data.Grid_Row` of the target Element_ID |

**Modeling in the schema (single-document invariant, per §1.1):**

The textual cross-reference is captured as data on the originating Element_ID only — never as a `Connection_ID` spanning workbooks. Connection_ID is strictly single-document; FKs (`From_Element_ID`, `To_Element_ID`) are always local to the workbook (see §A.18). Cross-document resolution is **out of scope for the schema** and is the responsibility of the downstream ontology / aggregation layer.

Per-line population:

- The cross-reference text itself is captured as an `Object` (Object_Type=Text, Content_Text="(001.8-A)") during P1, with provenance to the source page coordinates.
- During P8 (Element_Data population), the cross-reference is parsed and stored on the originating Element_ID (the line/symbol the reference is annotated next to) as **four `Element_Data` rows**:
  - `Cross_Reference_Raw` = `"(001.8-A)"` (the verbatim text, for full reconstructability per §1.1 principle 1)
  - `Cross_Reference_Target_Document_Number` = `"001"`
  - `Cross_Reference_Target_Path` = `"8"`
  - `Cross_Reference_Target_Row` = `"A"`
- The originating Element_ID is **not** linked to any `Connection_ID` row representing the cross-document continuation. The line endpoint that "ends" at the cross-reference is modeled as a `Connection_Point` sub-Element_ID (per §5.13 CAEX convention, v0.8.3 naming — see §5.13) with no outgoing Connection_ID within this workbook — the topology is "open" at that endpoint from the schema's perspective.
- The actual cross-document continuation is reconstructed downstream by joining: workbook A `Element_Data.Cross_Reference_Target_*` columns ↔ workbook B `Document_Data.Sheet_Number` + `Element_Data.Current_Path_Number` + `Element_Data.Grid_Row`. The join is best-effort per K2 convention; the schema does not enforce identity.

**Extension to Instrument_Loop_Diagram (v0.8.3):** the annotated-open-wire-end convention described above is not exclusive to Circuit_Diagram sheets: Instrument_Loop_Diagram (Stellenplan) sources exhibit the identical pattern — a floating connection-point drawn with no further wire, annotated with a plant-location cross-reference string (e.g. `"+10.O001.K002-L+"`) pointing to a continuation elsewhere in the plant that is not part of this sheet. The mechanism (four `Element_Data` rows: `Cross_Reference_Raw` plus three parsed components) and the underlying rationale (§1.1 Principle 1, full reconstructability of the verbatim annotation) apply identically; only the *shape* of the parsed target differs by convention (a Circuit_Diagram target is `Document.Path-Row`; an Instrument_Loop_Diagram target may instead be a bare plant/location-aspect string with no path/row decomposition). Where the target string does not decompose into the three Circuit_Diagram-shaped components, `Cross_Reference_Target_Document_Number`/`_Target_Path`/`_Target_Row` are left unpopulated and only `Cross_Reference_Raw` is recorded — this is not a violation, since those three are individually optional (see below).

**Required/optional Attribute_Lookup entries (Scope=Element, Type_Constraint=`Document_Type ∈ {Circuit_Diagram, Instrument_Loop_Diagram}`, extended v0.8.3):**
- `Cross_Reference_Raw` (String) — raw cross-reference text as appearing in the source
- `Cross_Reference_Target_Document_Number` (String, optional) — parsed Document_Number component, where the source's cross-reference notation decomposes into one
- `Cross_Reference_Target_Path` (String, optional) — parsed Current_Path_Number component, where applicable
- `Cross_Reference_Target_Row` (String, optional) — parsed Row_Letter component, where applicable
- `Current_Path_Number` (Integer) — own grid path on this sheet (for being a cross-reference target from another workbook; Circuit_Diagram only, per §4.3.1)
- `Grid_Row` (String) — own grid row letter on this sheet (likewise; Circuit_Diagram only)

**Cross-workbook device identity (Primary_RKZ-based, separate from cross-reference notation):** When the same physical device appears in a Terminal_Diagram workbook **and** a Circuit_Diagram workbook (e.g. contactor `-K1` with coil in the Stromlaufplan and its switched contacts cross-listed in the Klemmenplan), the linkage is via the shared `Primary_RKZ` prefix (`-K1:%`). This is **designation-only linkage**, not a structural FK between workbooks. The downstream ontology layer joins by Primary_RKZ — see §11.6 K2 convention rule.

---

### 4.4 Verschaltungsliste — alternative source format (column schema)

A Verschaltungsliste (tabular wiring list) is an alternative or complementary source format for Circuit_Diagrams and Terminal_Diagrams. Each row of a Verschaltungsliste describes one electrical connection (one wire or bridge between two terminals). The schema below is a **canonical mapping** of Verschaltungsliste columns to Excel-schema sheets. Real-world Verschaltungsliste tables vary in column composition; the column-mapping must be verified against the actual file used as source before mechanical import.

#### 4.4.1 Canonical column mapping

| Verschaltungsliste column (typical names DE / EN) | Maps to schema | Required? |
|---|---|---|
| `Kabel-Nr.` / `Cable_Number` | `Connection_Data.Cable_Number` | optional (only when wire belongs to a multi-conductor cable) |
| `Ader-Nr.` / `Wire_Number` | `Connection_Data.Wire_Number` | optional |
| `Von-Element` / `From_Element` (designation, e.g. `-X1`) | resolves to `Connection_ID.From_Element_ID` via Element_ID lookup by Primary_RKZ | required |
| `Von-Klemme` / `From_Terminal` (e.g. `11`) | resolves the connection-point sub-Element_ID (Terminal) of the From-Element | required (when From-Element is `InternalElement` — see §5.13 CAEX convention) |
| `Nach-Element` / `To_Element` | resolves to `Connection_ID.To_Element_ID` | required |
| `Nach-Klemme` / `To_Terminal` | resolves the connection-point sub-Element_ID of the To-Element | required (per CAEX convention) |
| `Aderfarbe` / `Wire_Color` (source word, e.g. `braun`) | encoded to `Connection_Data.Wire_Color` (IEC 60757 code per §8.3); source word preserved in linked `Object.Content_Text` | required for color-bound connections |
| `Querschnitt` / `Cross_Section` (e.g. `1.5 mm²`) | `Connection_Data.Cross_Section` | optional |
| `Länge` / `Length` | `Connection_Data.Length` | optional |
| `Kabeltyp` / `Cable_Type` (e.g. `LiYCY`, `NYM`) | `Connection_Data.Cable_Type` (per §8.5) | optional |
| `Polarität` / `Polarity` / `Funktion` (L1/N/PE/L+/L-/…) | `Connection_Data.Polarity` (per v0.8 Polarity enum) | required for power circuits |
| `Pfad` / `Current_Path_Number` | `Connection_Data.Current_Path_Number` — only for Circuit_Diagram-derived rows | optional |
| `Brücke` / `Bridge` (flag or type, e.g. `Längsbr.`) | `Connection_Data.Connection_Type` (per v0.8 Connection_Type enum: `Bridge_Longitudinal`, `Bridge_Cross_Fixed`, `Bridge_Cross_Pluggable`, `Bridge_Insulated`) | required for bridges (otherwise `Wire`) |
| `Schirm` / `Shielding` | `Connection_Data.Shielding` | optional |
| `Bemerkung` / `Remark` | `Connection_Data.Remark` | optional |

#### 4.4.2 Population sequence

For a Verschaltungsliste import:
1. **Create one `Object` row per Verschaltungsliste row** with `Source_Operation=VL_Row`, `Page_Number`=sheet index in the VL-workbook, `BBox_X1`=row index, `Content_Text`=pipe-separated serialisation of the row content. This is the provenance anchor for all downstream rows derived from this VL row. (See §A.7 Source-format-specific column semantics for the full column convention.)
2. Verify that all referenced Element_IDs (Von-Element, Nach-Element) exist in `Element_ID` — populated either from a parallel graphical-source extraction (S2/S3) or from the Verschaltungsliste's own From/To columns (when Verschaltungsliste is the sole source; see §4.4.3).
3. For each Verschaltungsliste row, create one `Connection_ID` row (stem data: From_Element_ID, To_Element_ID, both via terminal sub-Element_IDs per §5.13 CAEX convention). `Source_Topology_Object_ID` references the `Object` row from step 1.
4. For each Verschaltungsliste row, create one or more `Connection_Data` rows (one per populated attribute column).
5. Create `Connection_Data_Source` provenance rows linking each `Connection_Data` row to the originating VL-row Object: `Source_Object_ID` → the `Object` row from step 1 (one VL row may anchor multiple `Connection_Data_Source` rows — one per attribute column). The `Object` row's `Content_Text` preserves the verbatim VL-row content for full reconstructability per §1.1 principle 1.

#### 4.4.3 Verschaltungsliste-only documentation

When no graphical source exists (only Verschaltungsliste), Element_IDs are derived by deduplication of From/To-Element designations. `Element_Classification` rows for IEC 60617 cannot be filled (symbol unknown); `Classification_Code=Unclassified` per I28 is admissible.

**IEC 81346-2 classification from designation prefix:** In IEC-81346-2-conformant plants, the designation prefix letter equals the IEC 81346-2 class (e.g. `-Q1` → class Q for a contactor, `-F10` → class F for a fuse, `-B12` → class B for a sensor — see §8.1 for the full class-letter table). In **legacy plants** (designation conventions originating from DIN 19227-2 or pre-IEC 81346-2 practice), the prefix may diverge from the IEC class — most notably `-K` is historically used for contactors (whereas IEC 81346-2 prescribes Q for switching devices and reserves K for processing/logic objects such as PLCs and control relays). When importing from such plants, the IEC 81346-2 classification MUST be assigned by domain knowledge (not mechanically from prefix), and the divergence MAY be recorded as a project-level `Designation_Convention` attribute in `Document_Data` (e.g. `Designation_Convention=Legacy_DIN19227` vs. `IEC_81346_Conformant`).

#### 4.4.4 Verification before mechanical import

The column-name conventions above (German and English forms) are typical but **not normative**. Before any mechanical import of a real Verschaltungsliste, the actual column headers MUST be inspected and mapped explicitly to the canonical schema columns. The mapping itself may be recorded as a Verschaltungsliste-specific import-configuration outside the schema. The schema only fixes the **target columns** in `Connection_ID` / `Connection_Data` / `Connection_Data_Source`.

---

## 5. Element_Types for Terminal_Diagram

Each Element_Type is normatively anchored. For each type the following appears: definition, IEC 81346-2 classification code, IEC 60617 symbol reference (where applicable), mandatory and optional attributes.

### 5.1 Terminal

**Definition:** An individual electrical connection point of a Terminal_Strip. Represents a detachable electrical connection between two or more conductors.

| Property | Value |
|---|---|
| IEC 81346-2 class | **X** (Connecting objects) |
| IEC 60617 area | Part 3 (Connecting devices), symbol family 03-02 |
| CAEX_Type | ExternalInterface |
| Typical CAEX_InterfaceClass | TerminalConnectorIC |
| Parent_Element_ID | Terminal_Strip (Element_Type=Terminal_Strip) |

**Attributes (mandatory/optional):**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Terminal_Number | ✓ | string | Terminal number within the strip (e.g. "11") |
| Terminal_Strip_Designation | ✓ | string | Parent Terminal_Strip (e.g. "-X1") — redundant with Parent_RKZ, serves as cross-check |
| Polarity | – | enum | L1 \| L2 \| L3 \| L \| N \| PE \| PEN \| L+ \| L- \| G+ \| G- \| V+ \| V- \| FE \| AC \| DC (full list §8.4; missing values via `Unspecifiable` per E5) |
| Terminal_Type | – | enum | FeedThrough_Terminal \| DoubleLevel_Terminal_Internal_Connected \| DoubleLevel_Terminal_Internal_Separated \| MultiLevel_Terminal \| Disconnect_Terminal \| Pluggable_Terminal \| SpringClamp_Terminal \| Screw_Terminal (manufacturer-specific brand names like WAGO go in the `Manufacturer` attribute) |
| Manufacturer | – | string | e.g. Phoenix Contact, WAGO, Weidmüller |
| Type_Designation | – | string | Manufacturer type designation |
| Rated_Cross_Section | – | float | Maximum connectable cross-section in mm² |
| Rated_Voltage | – | float | Rated voltage in V |
| Rated_Current | – | float | Rated current in A |

### 5.2 Terminal_Strip

**Definition:** Aggregate of multiple terminals, typically mounted on a DIN rail. Carries its own reference designation (e.g. `-X1`).

| Property | Value |
|---|---|
| IEC 81346-2 class | **X** (Connecting, aggregate connection object) |
| IEC 60617 area | Part 3, no own symbol — aggregate of 03-02-02 symbols |
| CAEX_Type | InternalElement |
| Typical CAEX_RoleClass | DeviceRoleClassLib/TerminalStrip |
| Parent_Element_ID | optional: Control_Cabinet |

**Attributes:**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Terminal_Count | – | integer | Number of contained terminals |
| Function | – | string | Free text e.g. "230VAC supply", "Signal_Line 2-wire" |
| Position_in_Cabinet | – | string | Mounting position |
| Manufacturer | – | string | – |
| Terminal_System | – | string | e.g. "Phoenix Combi", "WAGO 280 series" |

### 5.3 Contactor

**Definition:** Electromechanical switching device for frequent switching of loads (motors, heaters, large consumers). Consists of main contacts, auxiliary contacts, and a coil.

| Property | Value |
|---|---|
| IEC 81346-2 class | **Q** (Switching electrical energy) |
| IEC 60617 area | Part 7, symbol family 07-13 (Schaltgeräte / power-switching devices) per IEC 60617-7:1996 Stichwortverzeichnis; the contactor symbol itself is **07-13-02** "Schütz" |
| CAEX_Type | InternalElement |
| Typical CAEX_RoleClass | DeviceRoleClassLib/Contactor |

**Attributes:**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Coil_Voltage | ✓ | string | e.g. "230 V AC", "24 V DC" |
| Rated_Operational_Current | – | float | I_e in A per IEC 60947-4-1 |
| Main_Contact_Count | – | integer | Typically 3 (3-pole) |
| Aux_Contact_NO_Count | – | integer | Normally-open auxiliary contacts |
| Aux_Contact_NC_Count | – | integer | Normally-closed auxiliary contacts |
| Utilization_Category | – | enum | AC-1 \| AC-2 \| AC-3 \| AC-4 \| DC-1 \| DC-3 \| DC-5 (per IEC 60947-4-1) [⚠ norm update see §16] |
| Manufacturer | – | string | – |
| Type_Designation | – | string | – |
| Target_Load | – | string | Reference to controlled equipment (e.g. "HC10N12 Stirrer") |

### 5.4 Auxiliary_Contactor

**Definition:** Small switching device for control and logic purposes (lower switching capacity than a Contactor). Often socket-mounted.

| Property | Value |
|---|---|
| IEC 81346-2 class | **K** by default (processing electrical/electronic signals); **Q** when `Element_Data.Function_Scope=Power` documents load-switching use |
| IEC 60617 area | Part 7, symbol family 07-13 (Schaltgeräte) and 07-15 (Antriebe / Operating devices) per IEC 60617-7:1996 Stichwortverzeichnis; auxiliary contactors are drawn as a combination of a coil (07-15-01 "elektromechanischer Antrieb, allgemein") and contact symbols (07-02-01 "Schließer" / 07-02-03 "Öffner"). Earlier draft cited 07-08 (Section 8 "Position switches") — this is corrected in v0.8 per Stichwortverzeichnis verification. |
| CAEX_Type | InternalElement |

**Classification rationale:** Auxiliary_Contactors are classified per IEC 81346-2:2009 Ed. 2 Table 1 as **K** (subclass KF "Processing of electrical and electronic signals"), because their main function is signal-processing in control circuits (energizing relay coils, indicator lamps, interlocks) — Table 1 explicitly lists "Contactor relay" as a class K example. v0.7 classified Auxiliary_Contactor as Q, which corresponds to power contactors per Table 1 ("Contactor (for power)"); v0.8 corrects this to K as the default. **Discriminator:** if a specific Auxiliary_Contactor in a project switches power loads (e.g. a small fan or heater), the per-device override is `Element_Data.Function_Scope=Power` → classification Q. Default Function_Scope is `Signal` → classification K.

**Distinction from Q:** Class **K** is the default for auxiliary contactors used as control-circuit signal-processing devices. Class **Q** is used only when the specific device's documented main function is switching electrical energy for a load; this override is recorded per device with `Element_Data.Function_Scope=Power`.

**Attributes:** identical to Contactor, typically with smaller values.

### 5.5 Fuse

**Definition:** Protective element that interrupts on overcurrent. Melting fuse or miniature circuit breaker (MCB).

| Property | Value |
|---|---|
| IEC 81346-2 class | **F** (Protection from undesired conditions) |
| IEC 60617 area | Part 7, symbol family 07-21 (melting fuse), 07-13 (MCB) |
| CAEX_Type | InternalElement |

**Attributes:**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Rated_Current | ✓ | float | Nominal current I_n in A |
| Trip_Characteristic | – | enum | gG \| gL \| aM \| B \| C \| D \| K \| Z (per IEC 60898-1 / IEC 60269) [⚠ norm update see §16, differentiation by protective-element type] |
| Protection_Form | – | enum | Fuse_NH \| Fuse_Diazed \| MCB \| RCBO \| RCD |
| Pole_Count | – | integer | 1, 2, 3, 4 |
| Rated_Voltage | – | float | U_n in V |
| Rated_Breaking_Capacity | – | float | I_cu in kA |
| Manufacturer | – | string | – |
| Type_Designation | – | string | – |
| Target_Load | – | string | Protected circuit/consumer |

### 5.6 Circuit_Breaker (FI/LS, FI, RCBO)

**Definition:** Combined protective element against overcurrent and residual current. Common for socket-outlet circuits and sensitive consumers.

| Property | Value |
|---|---|
| IEC 81346-2 class | **F** (Protection from undesired conditions) |
| IEC 60617 area | Part 7, symbol family 07-21 |

**Classification rationale:** Circuit_Breakers (RCBO, pure RCD) are classified per IEC 81346-2 §4.4 as **F** because their main function is protection (against overcurrent, residual current). The switching capability is a secondary means to the protective end; F dominates functionally. This is consistent with the Fuse classification (§5.5).

**Attributes:** as for Fuse, plus:

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Trip_Current_Residual | – | float | I_Δn in mA (typically 30, 100, 300) |
| Residual_Current_Type | – | enum | AC \| A \| F \| B \| B+ (per IEC 60755) [⚠ norm update see §16] |

### 5.7 Switch (manual)

**Definition:** Manually operated switching device for isolation or selection (e.g. main switch, rotary switch, selector switch).

| Property | Value |
|---|---|
| IEC 81346-2 class | **Q** (switching) if load-breaking, **S** (manual control) if signal-generating |
| IEC 60617 area | Part 7, symbol family 07-13 |

**Distinction Q vs. S:**
- **Q**: load-break isolator, main switch (switches energy flow)
- **S**: push-button, selector switch (produces a signal to the control system)

**Attributes:**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Switch_Type | – | enum | Main_Switch \| Rotary_Switch \| Selector_Switch \| Push_Button_NO \| Push_Button_NC \| Key_Switch \| Emergency_Stop |
| Pole_Count | – | integer | – |
| Rated_Current | – | float | – |
| Rated_Voltage | – | float | – |
| Rated_Breaking_Capacity | – | float | – |
| Manufacturer | – | string | – |
| Type_Designation | – | string | – |

### 5.8 Socket_Outlet

**Definition:** Connecting element for the temporary connection of electrical devices. Schuko, CEE, etc.

| Property | Value |
|---|---|
| IEC 81346-2 class | **X** (Connecting) |
| IEC 60617 area | Part 3, symbol family 03-03 |
| CAEX_Type | InternalElement (often also modeled as ExternalInterface) |

**Attributes:**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Socket_Type | – | enum | Schuko \| CEE_16A_3P \| CEE_16A_5P \| CEE_32A_5P \| French_Type \| USB |
| Rated_Voltage | – | float | – |
| Rated_Current | – | float | – |
| IP_Protection | – | enum | IP20 \| IP44 \| IP54 \| IP65 \| IP67 [⚠ list incomplete, see §16] |
| Mounting_Type | – | enum | Surface | Flush | DIN_Rail | Wall |

### 5.9 Power_Supply

**Definition:** Active converter between voltage levels, typically 230VAC → 24VDC.

| Property | Value |
|---|---|
| IEC 81346-2 class | **T** (Conversion of energy/signal/material) |
| IEC 60617 area | Part 6, symbol family 06-04 |
| CAEX_Type | InternalElement |

**Attributes:**

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Input_Voltage | ✓ | string | e.g. "230 V AC" |
| Output_Voltage | ✓ | string | e.g. "24 V DC" |
| Output_Power | – | float | in W |
| Output_Current | – | float | in A |
| Manufacturer | – | string | – |
| Type_Designation | – | string | – |
| Circuit_Topology | – | enum | linear \| switched \| galvanically_isolated \| non_isolated |

### 5.10 PLC_Module (carried from v0.4)

Already defined in v0.4 (→ v0.4 §5.4). Terminal_Diagram-specific addition: PLC modules are often the **target** of a terminal connection (e.g. `X5:1 → AI, EL3182/2`). In that case the Connection_ID.To_Element_ID references the PLC module.

**IEC 81346-2 classification convention — `-A` vs `-K` for PLC modules and control aggregates:**

Industrial designation practice and IEC 81346-2 partially conflict here, and source documents reflect this. The convention retained in v0.8:

| Source designation | Industrial meaning | IEC 81346-2 class (v0.8 convention) | Rationale |
|---|---|---|---|
| `-A1`, `-A2`, … | Steuerschrank / control cabinet aggregate (the whole assembly: PLC + power supply + I/O modules) | **A** (Multi-Function aggregate) | The aggregate is multi-functional; its top-level designation per IEC 81346-2:2019 Table 1 class A "Two or more purposes or tasks" applies. |
| `-A1-M01`, `-A1-M05`, … | Individual I/O module within the cabinet (e.g. Siemens 321-1BL00 DI module, Beckhoff EL3182 AI module) | **K** (Processing object) — sub-element | The sub-module performs signal processing; per IEC 81346-2:2019 Table 1 class K "Processing of signals or information". The structural relation to the parent `-A1` aggregate is captured via IEC 81346 sub-designation notation `-A1-M01` (product-aspect hierarchy). |
| Bare `-K1`, `-K2`, … (no parent aggregate) | Standalone PLC module or processing unit | **K** | Direct application of class K. |

**Modeling:** The aggregate `-A1` is captured as one `Element_ID` with `Element_Type=Cabinet_Aggregate` (canonical Element_Type per §9.3) and `Element_Classification.Classification_Code=A`. Each sub-module is a separate `Element_ID` with `Element_Type=PLC_Module` and `Element_Classification.Classification_Code=K`. The parent-child relation is recorded via `Element_ID.Parent_Element_ID` (per §10 hierarchical structures). This avoids the "A vs K" conflict by recognizing that the source uses `-A` for the aggregate level and `K` is correct for the module level — both are right at their respective levels.

### 5.11 Consumer (generic) / Actuator / Sensor / Motor

**Definition:** End or beginning of an electrical connection outside terminal strips — the actual electrical consumer or signal source.

In the Terminal_Diagram context, the consumer is often not modeled as an element itself but referenced as an RKZ string (e.g. "HC10W15 Thermostat" as Connection_Data.Attribute_Name=Target_RKZ). When the consumer also carries elementary data in the Terminal_Diagram (terminals, manufacturer), it can be carried as an Element_ID row.

| Element_Type | IEC 81346-2 class | Norm reference | Example |
|---|---|---|---|
| Motor | **M** | IEC 81346-2 Table 1 (Class M "Providing mechanical energy", electrical examples: "Electric motor, linear motor"); subclass **MA** "Driving by electromagnetic force" per Table 2 | Stirrer N12, Pump N13 |
| Valve_Actuator | **M** (verified against the currently available IEC 81346-2 project norm source: examples include mechanical actuator, fluid actuator, fluid cylinder, and spring-loaded actuator); subclass **MM** "Driving by hydraulic or pneumatic means" per Table 2. Earlier drafts assigned class `Y` to Valve_Actuator; v0.8 uses class M under the currently available norm basis. Project-internal designations using `Y` letters (e.g. Y17, Y20) are legacy DIN 19227-2 style and remain in the source documents; the IEC 81346-2 classification assigned by this schema is M. | DIN 19227-2 legacy designation `Y17`/`Y20`/`Y21`/`Y22` (source-preserved); IEC 81346-2 classification: **M** (subclass MM) |
| Sensor | **B** | IEC 81346-2 Table 1 (Class B "Converting input variable into a signal", electrical examples include "Sensor" explicitly); also DIN 19227-2; DIN 1319-1; IEC 60050-351 | T10 (temperature), L11 (level), F16 (flow) |
| Thermostat (depends on design) | **B** (bimetal switch) or **S** (manual setpoint setter) | see discriminator below | W15 |
| Heater | **E** | IEC 81346-2 Table 1 (Class E "Providing radiant or thermal energy", examples: "Heater, electrical boiler, electric furnace, infrared heating element"); subclass **EB** "Generation of heat by conversion of electrical energy" per Table 2 | – |

**Discriminator Thermostat B vs. S:**
- **B** (Converting input variable into signal): if the thermostat is an automatic temperature switch (bimetal, reed contact) that switches at a threshold — sensory main function
- **S** (Converting manual action into signal): if the thermostat is a manual setpoint setter (dial for temperature setting)

In the HC10 Terminal_Diagram example, HC10W15 is a bimetal thermostat → **B**.

### 5.12 Overview Table of all Terminal_Diagram-relevant Element_Types

| Element_Type | IEC 81346-2 | IEC 60617 Part | CAEX_Type |
|---|---|---|---|
| Terminal | X | 3 (03-02-02) | ExternalInterface |
| Terminal_Strip | X | 3 (aggregate) | InternalElement |
| Contactor | Q (subclass QA) | 7 (07-13-02 "Schütz") | InternalElement |
| Auxiliary_Contactor | K (subclass KF) — primary classification per IEC 81346-2 Table 2 Class K "Contactor relay" for control-circuit signal processing; **discriminator:** if the device switches power loads (motors, heaters) rather than control signals, use Q instead. The choice is design-dependent and documented per device in `Element_Data.Function_Scope` (`Signal` → K / `Power` → Q). v0.7 used Q uniformly; v0.8 uses K as the default for signal-processing auxiliary contactors. | 7 (07-13 family; in practice rendered as 07-15-01 coil + 07-02-01/07-02-03 contacts) | InternalElement |
| Fuse | F | 7 (07-21) | InternalElement |
| Circuit_Breaker | F (when primary purpose is protection per IEC 81346-2 Table 1 Class F note "If main purpose is protection, see class F"; Q (QA) when primary purpose is switching of electrical energy circuits). The default classification in this schema is F (protection-focused industrial circuit-breakers); projects where the CB is primarily a load-switching device may override to Q. | 7 (07-21) | InternalElement |
| Switch (load-break) | Q (subclass QB "Isolation of electrical energy circuits") | 7 (07-13) | InternalElement |
| Switch (manual, signal-generating) | S | 7 (07-15) | InternalElement |
| Socket_Outlet | X | 3 (03-03) | InternalElement |
| Power_Supply | T (subclass TB "Converting electrical energy retaining type, changing form" per IEC 81346-2 Table 2 — Rectifier, inverter) for converter-based industrial power supplies. G (Initiating flow of energy) is the correct class only when the device is a primary source (battery, generator, solar cell) rather than a converter from another supply. | 6 (IEC 60617-6 code not yet verified against project norm PDF; v0.8 records `Unclassified` with `Source_Symbol_Reference` until anchored — unresolved norm anchor; `Unclassified` fallback used until anchored) | InternalElement |
| PLC_Module | K (subclass KF "Processing of electrical and electronic signals") | 7 (07-15-04) | InternalElement |
| Motor | M (subclass MA "Driving by electromagnetic force") | (mechanical) | InternalElement |
| Valve_Actuator | M (subclass MM "Driving by hydraulic or pneumatic means"; v0.7 used Y under a different draft interpretation) | (pneumatic) | InternalElement |
| Sensor | B | 8 (08) | InternalElement |
| Heater | E (subclass EB "Generation of heat by conversion of electrical energy") | 8 (08) | InternalElement |

### 5.13 Additional Element_Types for Circuit_Diagram

Sub-element granularity for switching devices when documented in Circuit_Diagrams (where coil and contacts appear at spatially separated locations). The aggregate device (Contactor / Auxiliary_Contactor — see §5.3, §5.4) is **not** modeled as a parent Element_ID within the Circuit_Diagram document; cross-reference is via Primary_RKZ prefix match (see S3.3).

**Authoritative IEC 60617 item-code reference for Circuit_Diagram elements** (verified against project PDFs DIN EN 60617-2/-6/-7/-8:1997-08):

| Element_Type | IEC 81346-2 | IEC 60617 Part | IEC 60617 item code | Norm verbatim | CAEX_Type |
|---|---|---|---|---|---|
| Coil | Q | 7 | **07-15-01** | „elektromechanischer Antrieb, allgemein" | InternalElement |
| Main_Contact | Q | 7 | **07-13-02** | „Leistungskontakt eines Schütz" | InternalElement |
| Auxiliary_Contact (NO) | Q | 7 | **07-02-01** | „Schließer" | InternalElement |
| Auxiliary_Contact (NC) | Q | 7 | **07-02-03** | „Öffner" | InternalElement |
| Indicator_Lamp | P | 8 | **08-10-01** | „Lampe / Leuchtmelder" | InternalElement |
| Switch with Switch_Type=Push_Button_NO/NC (§5.7) | S | 7 | **07-07-02** | „Druckschalter, handbetätigter Schalter" | InternalElement |
| Switch with Switch_Type=Emergency_Stop (§5.7) | S | 7 | **07-07-06** | „Pilz-Notdrucktaster" | InternalElement |
| Motor (§5.11) | M | 6 | **06-04-01** | „Motor" | InternalElement |
| Heater (§5.11) | E | 6 | **06-17-01** | „Heizquelle, allgemein" | InternalElement |

This table is the **single source of truth** for IEC 60617 codes referenced by §4.3 S3.2 and §9.1 Classification_System. All codes are verified verbatim from the project's IEC 60617-2/-6/-7/-8 norm PDFs (edition 1997-08).

**Modeling principles:**
- A Circuit_Diagram document containing the parts of contactor `-K1` has Element_IDs `-K1:A1/A2` (Coil), `-K1:1/2` (Main_Contact), `-K1:3/4` (Main_Contact), `-K1:13/14` (Auxiliary_Contact), etc. — no aggregate `-K1` Element_ID is created within this document.
- A Terminal_Diagram document modeling the same physical device has **one** Element_ID with `Element_Type=Contactor` and `Primary_RKZ=-K1`, carrying aggregate attributes (Main_Contact_Count, Aux_Contact_NO_Count, etc.) per §5.3.
- Cross-document consistency (Coil↔Contact) is enforced by AG1 (§11.10) at the project-aggregation level via Primary_RKZ prefix match.
- Switch with `Switch_Type=Push_Button_NO/NC/Emergency_Stop` (already in §5.7) covers pushbuttons and emergency-stop devices in Circuit_Diagrams — no new Element_Types for these (avoiding duplication with v0.5).

**CAEX connection-point convention**(applies to all `InternalElement`-typed switching-device sub-elements):

The Element_Types Coil, Main_Contact, Auxiliary_Contact, and Indicator_Lamp carry `CAEX_Type=InternalElement` per the table above. Per §3.1, `Connection_ID.From_Element_ID` and `To_Element_ID` reference Element_IDs with `CAEX_Type=ExternalInterface`. Therefore each such sub-element MUST have **connection-point sub-Element_IDs** (one per physical terminal — structurally analogous to, but not the same `Element_Type` as, the Terminal_Strip → Terminal hierarchy in §10.1):

> **`Element_Type=Connection_Point` (introduced v0.8.3, replaces reuse of `Terminal` for this purpose):** In v0.8/v0.8.2, generated connection-point sub-elements were typed `Element_Type=Terminal`, reusing the same canonical type as an actual terminal-strip terminal (§5.1). This caused every generated connection point to inherit the `Terminal_Number`/`Terminal_Strip_Designation` mandatory attributes from §9.2 — attributes a generated pass-through pin never had in the source, since it was never itself assigned a terminal number or listed on a terminal strip. As of v0.8.3, generated connection-point sub-elements SHALL use the canonical `Element_Type=Connection_Point` instead. `Element_Type=Terminal` remains reserved for §5.1 terminals: terminals that are themselves distinct, individually-designated objects appearing in the source (i.e. real terminal-strip terminals extracted per S2, §4.2). `Connection_Point` carries `CAEX_Type=ExternalInterface` exactly like `Terminal` and satisfies `I8` identically; it carries **no mandatory attributes** in §9.2 (see §9.2 — no Attribute_Lookup block is defined for it, by design). **Backward compatibility:** workbooks produced under v0.8/v0.8.2 that used `Element_Type=Terminal` for generated connection points remain readable; the `I28` exemption clause (§11.9) recognizes both spellings for the transition period, but new workbooks SHALL use `Connection_Point`.

| Sub-Element | Connection-point sub-Element_IDs | Parent_Element_ID | Element_Type | CAEX_Type |
|---|---|---|---|---|
| Coil (`-K1:A1/A2`) | 2 (terminals A1, A2) | Coil's Element_ID | `Connection_Point` | `ExternalInterface` |
| Main_Contact (`-K1:1/2`) | 2 (terminals 1, 2) | Main_Contact's Element_ID | `Connection_Point` | `ExternalInterface` |
| Auxiliary_Contact (`-K1:13/14`) | 2 (terminals 13, 14) | Auxiliary_Contact's Element_ID | `Connection_Point` | `ExternalInterface` |
| Indicator_Lamp | 2 (`+`, `–` terminals) or per actual device count | Indicator_Lamp's Element_ID | `Connection_Point` | `ExternalInterface` |

Connections in Circuit_Diagrams reference these **`Connection_Point` sub-Element_IDs**, not the parent Coil/Contact/Lamp Element_IDs themselves. This convention is structurally analogous to the v0.8 Terminal_Strip→Terminal pattern (§10.1) — a parent/child pair resolving the CAEX_Type requirement of Connection_ID — but intentionally uses a distinct `Element_Type` so that the two cases can carry different Attribute_Lookup obligations (§9.2).

The same convention applies retroactively to the v0.5 `InternalElement`-typed Element_Types (Contactor, Auxiliary_Contactor, Switch, Fuse, Circuit_Breaker, Socket_Outlet, Power_Supply, Motor, Valve_Actuator, Sensor, Thermostat, Heater, PLC_Module): each Element_ID has `Connection_Point` sub-Element_IDs corresponding to the physical terminals of the device. This convention is explicit for all InternalElement Element_Types.

**Source_Match_ID convention for generated `Connection_Point` sub-elements:** `Connection_Point` sub-elements inherit `Source_Match_ID` from their parent `InternalElement` unless the source document explicitly contains separately extractable connection-point symbols. If separately extracted, the `Connection_Point` element receives its own `Source_Match_ID`. This keeps generated CAEX-compatible connection points traceable without requiring artificial match rows for every inherited terminal.

**Attributes:**

| Attribute_Name | Applies to | Required | Type | Description |
|---|---|---|---|---|
| Current_Path_Number | Coil, Main_Contact, Auxiliary_Contact, Indicator_Lamp, Switch, Fuse, etc. (any Element on a Circuit_Diagram sheet) | – | integer | Vertical current-path number from sheet grid (S3.1) |
| Contact_Designation | Main_Contact, Auxiliary_Contact | ✓ | string | Contact identifier as in source: `1/2`, `3/4`, `13/14`, `21/22`, `53/54`, … |
| Coil_Voltage | Coil | – | string | Inherited semantic from §5.3 Contactor.Coil_Voltage |
| Lamp_Color, Lamp_Function, Rated_Voltage, Manufacturer, Type_Designation | Indicator_Lamp | – | mixed | Standard element attributes — `Lamp_Color` is an Enum bound to `Wire_Color` (IEC 60757 codes); other attributes follow v0.8 conventions |
| Grid_Row | Any Element on a Circuit_Diagram sheet | – | string | Horizontal row letter from sheet grid (`A`, `B`, `C`, …); pairs with Current_Path_Number to identify grid position |
| Cross_Reference_Raw | Element that carries a cross-reference annotation in source | – | string | Verbatim raw text of the cross-reference annotation, e.g. `"(001.8-A)"` — preserves source for full reconstructability (per §4.3.3) |
| Cross_Reference_Target_Document_Number | Element with cross-reference | – | string | Parsed `Document_Number` component from Cross_Reference_Raw |
| Cross_Reference_Target_Path | Element with cross-reference | – | string | Parsed `Current_Path_Number` component from Cross_Reference_Raw |
| Cross_Reference_Target_Row | Element with cross-reference | – | string | Parsed `Row_Letter` component from Cross_Reference_Raw |
| PCE_Channel_Suffix | Sensor, Transducer, PLC_Module (any Element on an Instrument_Loop_Diagram sheet that represents a signal channel) | – | enum | PCE function-channel suffix per IEC 62424 (`I`, `O`, `A+`, `A-`, `D`); see §4.1 (T2 resolution). Validated against `Enum_Lookup` for `Field_Name=PCE_Channel_Suffix`. |

---

## 6. Connection Modeling for Terminal_Diagram

### 6.1 Principle

**One `Connection_ID` row represents exactly one wire/strand between two electrical connection points.** The From/To endpoints are always ExternalInterface elements (typically terminals, PLC module pins, or switchgear connection points). This constraint is checked by the v0.4 rule **I8** (FK validity + CAEX_Type=ExternalInterface) — it applies unchanged to Terminal_Diagram connections.

Wire color, polarity, cross-section, etc. are attributes of the connection (not separate elements).

### 6.2 Bridge Modeling

A bridge (cross-bridge, longitudinal bridge, pluggable bridge) is a special form of connection — it links two terminals of the same Terminal_Strip (`Parent_Element_ID` of both terminals refers to the same Terminal_Strip). This constraint is checked by I23 (see §11).

**Attributes of a bridge connection:**
- `Connection_Type = Bridge_Cross_Fixed` (or `Bridge_Cross_Pluggable`, `Bridge_Insulated`, `Bridge_Longitudinal`, etc.)
- `Wire_Color`: usually empty (a bridge is a component, not a wire)
- `Polarity`: identical to the connected terminals

### 6.3 Multi-wire Connections (Cables with Multiple Wires)

A physical cable with n wires produces n Connection_ID rows. Common cable membership is expressed by a shared `Cable_Number` attribute. `Wire_Color` carries the language-neutral IEC 60757 code; the original color word from the source document is preserved in the linked `Object.Content_Text`:

| Connection_ID | From | To | Wire_Color (IEC 60757) | Source word (in Object) | Polarity | Cable_Number |
|---|---|---|---|---|---|---|
| C.1 | X2:3 (L) | HC10W15:L | BN | braun | L | W123 |
| C.2 | X2:3 (N) | HC10W15:N | BU | blau | N | W123 |
| C.3 | X2:3 (PE) | HC10W15:PE | GNYE | grn/glb | PE | W123 |

There is no `Element_Type=Cable`. Cable bundling is a **property of the connections**, not a structural object.

### 6.4 Connection Attributes (Complete List)

| Attribute_Name | Type | Example | Norm reference |
|---|---|---|---|
| Wire_Color | enum | "BU" (IEC 60757; source word "blau" preserved in Object) | IEC 60757 (code); DIN EN 60446 (function) [⚠ see §16] |
| Wire_Color_Secondary | enum | "GNYE" (IEC 60757; protective conductor) | IEC 60757 (code); DIN EN 60446 (function) [⚠ see §16] |
| Polarity | enum | "L1", "N", "PE" | DIN VDE 0100-200 |
| Cross_Section | float | 2.5 (mm²) | DIN VDE 0298 |
| Wire_Number | string | "Strand 1" | – |
| Cable_Number | string | "W123" | – |
| Cable_Type | enum | "LiYCY", "NYM", "H07V-K" | DIN VDE 0281; manufacturer spec (LiYCY, Ölflex) |
| Total_Wire_Count | integer | 5 | – (informative) |
| Shielding | enum | "Shielded" / "Unshielded" / "Foil" / "Braid" | – |
| Connection_Type | enum | "Wire", "Bridge_Cross_Fixed", "Bridge_Cross_Pluggable", "Bridge_Insulated", "Bridge_Longitudinal" | – |
| Length | float | 1.5 (m) | – |
| Connection_Point_From | string | "L1" / "Terminal 31" | – (for consumers when terminal is not its own element) |
| Connection_Point_To | string | "N" / "EL3182/2" | – |
| Remark | string | free text | – |

---

## 7. RepresentedItem_Type for Terminal_Diagram

### 7.1 RepresentedItem Modeling

In the Terminal_Diagram, the central "business unit" is the Terminal_Strip. Every Terminal_Strip with its own designation gets one `Document_RepresentedItem` row:

- `RepresentedItem_Type = Terminal_Strip`
- `Primary_RKZ = =0.H1.T1.HC10.-X1` (Terminal_Strip RKZ)
- `Topic_Identification_Status = Confirmed` (when the Terminal_Strip header is unambiguous)

Alternatively — when the Terminal_Diagram document covers an entire control cabinet — an additional higher-level RepresentedItem for the cabinet may be set up:

- `RepresentedItem_Type = Control_Cabinet` or `Distribution_Panel`
- `Parent_RepresentedItem_ID = NULL`
- The individual Terminal_Strip RepresentedItems have `Parent_RepresentedItem_ID` = Cabinet RepresentedItem_ID

### 7.2 RepresentedItem Attributes for Terminal_Strip

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Function | – | string | e.g. "230VAC supply", "Signal_Line 2-wire" |
| Voltage_Level | – | enum | 230V_AC \| 400V_AC \| 24V_DC \| Signal_4_20mA \| Signal_0_10V \| Bus_Signal |
| Terminal_Count | – | integer | – |
| Terminal_System | – | string | e.g. "Phoenix Combi", "WAGO 280" |
| Position_in_Cabinet | – | string | – |

### 7.3 RepresentedItem Attributes for Control_Cabinet

| Attribute_Name | Required | Type | Description |
|---|---|---|---|
| Cabinet_Manufacturer | – | string | e.g. Rittal, Eldon |
| Cabinet_Type | – | string | – |
| IP_Protection | – | enum | IP20 \| IP44 \| IP54 \| IP65 \| IP67 [⚠ list incomplete, see §16] |
| Dimensions_HxWxD | – | string | "1000x600x300 mm" |
| Terminal_Strip_Count | – | integer | – |

---

## 8. Normative Classification

### 8.1 IEC 81346-2:2019 classification letters (full table)

> **Norm-edition note:** This table follows **IEC 81346-2:2019 (Ed. 3)**. The 2009-edition (Ed. 2) is the only version currently present in the project library — see §16 entry #19 for the open issue of obtaining the 2019-edition PDF. The Y-class definition below ("Mechanical action on a processing object") is per the 2019-edition; in the 2009-edition Y was reserved for future standardization. The H-class is listed for completeness but is not typically used in Terminal_Diagram or Circuit_Diagram contexts (production of materials).
>
> **v0.8 transition-status statement (Ed. 2 ↔ Ed. 3):** The table is retained as a forward-looking 2019-oriented class overview, while v0.8 validation uses the currently available Ed. 2 project basis as encoded in the §9.3 Seed Catalog (`Field_Name=IEC_81346_2_Class`). Edition-related conflicts, including the Y-class status and any class assignments that depend on the Ed. 3 reinterpretation of Y, are tracked in §16 (entries #18, #19, #24) and are **not resolved in v0.8**. v0.8 therefore deliberately presents Ed. 3 as the descriptive overview here and Ed. 2 as the validation basis in §9.3; consumers must read both sections together. A unified single-edition table is a planned v0.9 schema update once the Ed. 3 PDF is anchored in the project library.

| Letter | Main function | Terminal_Diagram application |
|---|---|---|
| A | Multiple functions (collection) | Complex assemblies, cabinets |
| B | Convert input variable into signal | Sensors, sensing elements, transducers, detectors |
| C | Store (energy/information) | Accumulators, capacitors |
| E | Provide radiation/heat | Heaters, lamps, emitters |
| F | Protection from undesired conditions | Fuses, circuit breakers, FI, surge protection |
| G | Generate electrical energy | Generators, voltage sources |
| H | Produce new kind of material or product | – (not typical for Terminal_Diagram / Circuit_Diagram; relevant in P&ID / process flow) |
| K | Processing object (logical) | PLC modules, control relays, computers, logic blocks |
| M | Generate mechanical energy | Motors, pumps, drives |
| P | Display, record, measure | Displays, indicating instruments, counters |
| Q | Switch electrical energy | Contactors, load-break isolators, disconnectors |
| R | Limit electrical quantities | Resistors, chokes, current limiters |
| S | Convert manual action into signal | Push buttons, selector switches |
| T | Convert energy/signal/material | Transformers, power supplies, transducers |
| U | Hold/position | Mechanical fixtures, supports |
| V | Process material | – |
| W | Transmit between objects | Cables, lines, antennas, optical fibers |
| X | Connect objects (interface) | Terminals, plugs, sockets, couplings |
| Y | Mechanical action on a processing object (per 2019-edition) | Valves, actuators, magnets |

This table is held in full in `Enum_Lookup` with `Field_Name=IEC_81346_2_Class`, so that the schema can validate `Element_Classification.Classification_Code`. The letters D, I, J, L, N, O, Z are deliberately omitted: D/J/L/N/Z are "Reserved for future standardization" per IEC 81346-2, and I/O are "Not to be applied" (to avoid confusion with digits 1/0).

### 8.1.1 Multi-Classification Convention

A single `Element_ID` MAY (and typically WILL) have **multiple `Element_Classification` rows**, one per classification system applicable. The cardinality is **1:N from Element_ID to Element_Classification**, with no upper bound.

Typical patterns:

| Element_ID | Classifications expected |
|---|---|
| Terminal | 1× IEC 81346-2 (`X`) + 1× IEC 60617-3 (`03-02-02` "Anschluß (z.B. Klemme)" per Stichwortverzeichnis IEC 60617-3:1996) |
| Contactor (aggregate) | 1× IEC 81346-2 (`Q`) + 1× IEC 60617-7 (`07-13-02` "Schütz" per Stichwortverzeichnis IEC 60617-7:1996) |
| Coil (sub-element) | 1× IEC 81346-2 (`Q`) + 1× IEC 60617-7 (`07-15-01`) |
| Sensor | 1× IEC 81346-2 (`B`) + 1× IEC 60617-8 + possibly 1× IEC 62424 (PCE_Category) |

Each `Element_Classification` row carries exactly **one** `Classification_System` value and **one** `Classification_Code`. Multiple classifications per element are represented by multiple rows, never by concatenated values within a single row.

**Validator behavior (per I28):** for `Document_Type=Circuit_Diagram`, at least one IEC 60617 classification row MUST exist per Element_ID (or `Unclassified` with provenance reference). For Terminal_Diagram and Instrument_Loop_Diagram, the existing v0.4/v0.5 rules apply unchanged.

### 8.2 IEC 60617 graphical symbols — parts relevant to Terminal_Diagram

| Part | Content | Terminal_Diagram application |
|---|---|---|
| IEC 60617-2 | Symbol elements, qualifying symbols | General graphical conventions |
| IEC 60617-3 | Conductors and connecting devices | Terminals, plugs, sockets, bridges, cables |
| IEC 60617-6 | Production and conversion of electrical energy | Power supplies, transformers |
| IEC 60617-7 | Switchgear, controlgear and protective devices | Contactors, relays, fuses, switches |
| IEC 60617-8 | Measuring instruments, signal generators | Indicators |

The `Classification_Code` values in `Element_Classification` follow the IEC 60617 schema with dot notation (e.g. `03-02-02` for a basic terminal/Anschluß per IEC 60617-3:1996 Stichwortverzeichnis, `07-13-02` for a contactor/Schütz per IEC 60617-7:1996 Stichwortverzeichnis; earlier draft examples used `03-02-01` for terminals and `07-08-01` for contactors — both are corrected in v0.8 per Stichwortverzeichnis-Verifikation: `03-02-01` is "Verbindungspunkt" and `07-08-01` is "Schließer, Endschalter").

### 8.3 Wire-Color Coding (IEC 60757 codes; function per DIN EN 60446 [⚠ see §16])

`Wire_Color` is stored as a language-neutral IEC 60757 letter code. The original source color word is preserved in `Object.Content_Text` (see §0.1). The `Enum_Lookup` Description field carries a multilingual reading aid.

| Code (IEC 60757) | Color (DE / EN) | Function | Application |
|---|---|---|---|
| GNYE | grün-gelb / green-yellow | Protective conductor (PE) | Mandatory, exclusive |
| BU | blau / blue | Neutral conductor (N) | Mandatory when N is present |
| BK | schwarz / black | Line conductor L1 or any phase | Standard |
| BN | braun / brown | Line conductor L2 or any phase | Standard |
| GY | grau / grey | Line conductor L3 or any phase | Standard |
| RD | rot / red | Free choice, often 24V DC + or control line | Informal |
| OG | orange / orange | Control/signal lines | Per application |
| YE | gelb / yellow | Control/signal lines | Per application |
| GN | grün / green | Control/signal lines | Per application |
| VT | violett / violet | Control/signal lines | Per application |
| WH | weiß / white | Control/signal lines | Per application |
| PK | rosa / pink | Control/signal lines | Per application |
| TQ | türkis / turquoise | Control/signal lines | Per application |

These codes are held in full in `Enum_Lookup` with `Field_Name=Wire_Color`, each with a `Description` carrying the DE/EN color words and `Normative_Reference=IEC 60757`. Code validation of `Wire_Color` against this list is performed via I14 (the validation always operates against the code `Allowed_Value`, never against the bilingual `Description`; see §9.3). Bi-colored wires beyond GNYE are recorded via a composite code or supplemented via `Wire_Color_Secondary`.

**Sourcing clarification (added v0.8.3):** `Wire_Color` SHALL be populated only from an **explicit textual colour designation present in the source** (a written colour word, a legend/key entry, or an equivalent explicit annotation) — never inferred from the rendered stroke or layer colour of a graphic object in a vector drawing. Circuit_Diagram and similar CAD-originated sources routinely render conductors in colours that encode a *drawing-tool layer or line-type convention* (e.g. "green = power circuit", "black dashed = neutral") rather than the conductor's physical insulation colour; treating such rendering colours as `Wire_Color` would misrepresent a CAD styling choice as a norm-anchored physical fact and would violate the `I24` wire-colour/polarity consistency rule's own premise that `Wire_Color` denotes an actually-stated physical colour. Where a source document does not state a wire's physical colour in text, `Wire_Color` is left unpopulated (or `Unspecifiable` where the schema context requires an explicit marker, per E5) — it is **not** backfilled from the drawing's rendering. The sole exception is a source document that itself explicitly defines its rendering-colour convention as a wire-colour legend (e.g. a title-block note stating "line colour = conductor colour per DIN EN 60445"); in that documented case, the rendering colour **is** the stated physical colour and may be used, with the legend itself captured as the `Object` provenance for the resulting `Connection_Data_Source` rows.

> **Encoding, not translation:** Mapping a source word (`rot`, `blau`, `grn/glb`) to its IEC 60757 code (`RD`, `BU`, `GNYE`) is a norm-based encoding, not a translation. The original word remains in `Object.Content_Text`; provenance via `Connection_Data_Source` keeps it retrievable. This satisfies the §0.1 principle.

### 8.4 Polarity Notation (DIN VDE 0100-200)

| Symbol | Meaning | Voltage level |
|---|---|---|
| L1, L2, L3 | Line conductors (phases) | Three-phase 400V AC |
| L | Line conductor (single-phase) | 230V AC |
| N | Neutral conductor | – |
| PE | Protective earth | – |
| PEN | Combined PE+N | – |
| L+, L- | DC positive/negative | typ. 24V DC |
| G+, G- | DC supply (Beckhoff convention) | typ. 24V DC |
| V+, V- | DC supply (alternative naming) | typ. 24V DC |
| FE | Functional earth | EMC earth |
| AC | AC voltage (generic) | see note below |
| DC | DC voltage (generic) | see note below |

These values are held in full in `Enum_Lookup` with `Field_Name=Polarity`.

> **Semantic note:** The `Polarity` field mixes line-conductor function (L1/L2/L3/N/PE/L+/L-/...) with generic voltage type (AC/DC). A strict normative reading would split these into two separate fields (`Polarity` + `Voltage_Type`). This schema retains the pragmatic mixed representation because it is widely practiced in Terminal_Diagrams. The generic values AC/DC should only be used when no more specific conductor function is derivable (fallback values). A potential split into separate fields is a candidate for Schema v1.0.

### 8.5 Cable Types (DIN VDE 0281 and successors)

| Code | Meaning | Typical application | Normative reference |
|---|---|---|---|
| NYM | PVC-sheathed cable, copper conductor | Domestic installation 230V | DIN VDE 0281 |
| NYY | PVC-sheathed underground cable | Outdoor / primary circuit | DIN VDE 0281 |
| H07V-K | Flexible PVC single-conductor cable | Control-cabinet wiring | DIN VDE 0281 |
| LiYCY | Flexible control cable with braided shield | EMC-loaded control signals | Manufacturer spec (e.g. LAPP, Helukabel) |
| LiYY | Flexible control cable without shield | Standard control signals | Manufacturer spec |
| JE-LiYCY | Paired and twisted with braided shield | Measurement signals 4–20mA | Manufacturer spec |
| JZ-500 | Flexible control cable with outer sheath (e.g. LAPP Ölflex JZ-500) | Machine wiring | Manufacturer spec |

> **Norm scope note:** DIN VDE 0815 (Telecommunication and Information-Technology installation cables, e.g. J-Y(St)Y) does **not** cover the industrial control and power cables used in HC10/HC20 plant documentation; it was incorrectly cited in an earlier draft and is removed in v0.5. Industrial PVC cables follow DIN VDE 0281; flexible control cables (LiYCY, LiYY, Ölflex variants) follow manufacturer specifications because no single DIN VDE document covers them uniformly. The harmonized DIN EN 50525 series is the modern alternative anchor and is a candidate for v1.0 re-anchoring.

List is held in `Enum_Lookup` with `Field_Name=Cable_Type`; open list, can be extended project-specifically.

---

## 9. Lookup Tables

### 9.1 Enum_Lookup Additions

> **Status of §9.1:** This section provides **canonical-value descriptions, source-extraction guidance, and didactic context** for enum fields used by Terminal_Diagram and Circuit_Diagram. It is **explanatory**, not the authoritative source for `Enum_Lookup` materialization. The single authoritative source is the **Authoritative Enum_Lookup Seed Catalog in §9.3**. When a value appears here but not in §9.3, the §9.3 catalog governs (the value must be either added to §9.3 or removed from §9.1). For v0.8, the §9.1 enum value sets have been migrated into the §9.3 Seed Catalog; the descriptions and discriminator guidance below remain for reading-aid purposes only.

> **Element_Type — controlled vocabulary:** `Element_Type` is **enum-validated** via `Enum_Lookup` (`Field_Name=Element_Type`), consistent with the other `*_Type` fields (`Document_Type`, `RepresentedItem_Type`, `Object_Type`, `Cluster_Type`, etc.). The canonical values are defined in §5.1–§5.13 and listed in the §9.3 Authoritative Seed Catalog. **Project-specific extensions** are permitted via the `Schema_Metadata.Allowed_Element_Type_Extensions` key (CSV list); values declared there are accepted by I14 alongside the §9.3 catalog. This preserves cross-workbook comparability while still allowing controlled project extensions. The `Type_Constraint` fields in `Attribute_Lookup` reference these canonical or declared-extension strings.

**Extension of Element_Type** (canonical Terminal_Diagram values in addition to v0.4 values Terminal, Terminal_Strip, PLC_Module, Transducer, Sensor):

```
Contactor, Auxiliary_Contactor, Fuse, Circuit_Breaker, Switch, Socket_Outlet,
Power_Supply, Motor, Valve_Actuator, Thermostat, Heater, Actuator, Consumer,
Control_Cabinet, Cabinet_Aggregate
```

**canonical Element_Type values for Circuit_Diagram (sub-element granularity per §5.13):**

```
Coil, Main_Contact, Auxiliary_Contact, Indicator_Lamp
```

**canonical Element_Type value for generated CAEX connection-points (added v0.8.3, applies to all document types per §5.13):**

```
Connection_Point
```

> **Note:** Pushbuttons and emergency-stop devices use `Element_Type=Switch` with `Switch_Type ∈ {Push_Button_NO, Push_Button_NC, Emergency_Stop}` (already in §9.1 and §5.7). No new Element_Types for these.

> **Note Sensor:** The v0.4 value `Sensor` (formerly `Aufnehmer` in German; see §17) remains canonical (normatively anchored per DIN 19227-2, DIN 1319-1, IEC 60050-351, IEC 81346-2 class B). No duplicate term is introduced.

> **Connection-point convention (revised v0.8.3):** In v0.8/v0.8.2, generic device connection points were modeled as `Element_Type=Terminal` with `CAEX_Type=ExternalInterface`; the previously discussed `ConnectionPoint` value was explicitly deferred ("not an active canonical `Element_Type` in v0.8"). Build-and-check experience (three real workbooks, see §13 v0.8.3 entry) showed this reuse to be a structural defect: it caused every generated connection point to inherit `Terminal`'s mandatory `Terminal_Number`/`Terminal_Strip_Designation` attributes (§9.2), which a generated pass-through pin never has in the source. **As of v0.8.3, `Connection_Point` is an active canonical `Element_Type`**, reserved for generated CAEX connection-point sub-elements (§5.13); it carries `CAEX_Type=ExternalInterface` and no mandatory attributes. `Element_Type=Terminal` remains reserved for terminals that are themselves distinct, individually-designated objects in the source (§5.1, extracted per S2). See §5.13 for the full convention and the v0.8/v0.8.2 backward-compatibility note.

> **Cable convention:** `Element_Type=Cable` is not an active canonical `Element_Type` in v0.8. Cable bundling is modeled in the Core profile via `Connection_Data.Cable_Number`; cable-as-asset modeling is available only through the optional `A.O3 Cable_Data` profile.

**Fallback Element_Type convention:** `Element_Type=Actuator` and `Element_Type=Consumer` are fallback values. They SHALL only be used when no more specific canonical Element_Type (for example `Valve_Actuator`, `Motor`, `Heater`, `Power_Supply`, `Sensor`, `Switch`) is derivable from the source evidence.

**Extension of RepresentedItem_Type** (in addition to PCE_Request, Terminal_Strip, Circuit, Plant_Section):

```
Control_Cabinet, Distribution_Panel, Function_Group
```

**Extension of Document_Type:** no new values in v0.5 — Terminal_Diagram was already declared as enum value in v0.4 (in German as `Klemmenplan`; migrated per §17).

**Note:** `Circuit_Diagram` (new value); used together with the reserved `Document_Subtype` attribute (Type_Constraint=Document_Type=Circuit_Diagram, allowed values `Primary` and `Secondary`; see §9.2).

**New Field_Names in Enum_Lookup** (the complete and binding `Allowed_Value` set for each field is in the §9.3 Authoritative Enum_Lookup Seed Catalog — only the catalog governs):

- `Polarity` (see §8.4 semantic note for the mixed line-function / voltage-type representation)
- `Wire_Color` (IEC 60757 letter codes; `Description` carries DE/EN color words; complete set per §9.3)
- `Cable_Type` (mirrors §8.5)
- `Connection_Type` (Wire / Bridge_* variants per §9.3)
- `Terminal_Type`, `Switch_Type`, `Socket_Type` (project-extensible per §9.3)
- `Utilization_Category`, `Trip_Characteristic`, `Protection_Form`, `IP_Protection`, `Residual_Current_Type` (project-extensible per §9.3) [⚠ norm updates see §16]
- `Voltage_Level` (six values per §9.3)
- `IEC_81346_2_Class` (per §8.1 class table; complete set per §9.3 with Y-class caveat)
- `Source_Operation` (closed enum extension by `Cell` for Excel/Word-based source documents per K1 and `VL_Row` for Verschaltungsliste per K3, plus `Manual_Entry`; see §A.7 source-format-specific column semantics for the interpretation of `Object`-sheet columns under each value, and §9.3 for the complete PDF-operator value set)
- `Scope` (extended by value `Connection`)
- `Source` (for Element_ID): unchanged

**Additional fields** (complete `Allowed_Value` sets in the §9.3 Authoritative Enum_Lookup Seed Catalog):

- `Document_Subtype` (new Field_Name; Type_Constraint=Document_Type=Circuit_Diagram; Description carries `Primärstromkreis / Primary circuit` and `Sekundärstromkreis / Secondary circuit` per §9.3 encoding convention)
- `Classification_System` (extended set including IEC 60617-2, IEC 60617-6, IEC 60617-8 in addition to the previously used IEC 60617-3, IEC 60617-7, IEC 81346-2; complete set per §9.3)
- `Source_Format` (extended by `Verschaltungsliste` alongside `PDF_Drawing`, `Excel_Sheet`, `Manual_Entry`; complete closed set per §9.3)
- `Object_Role` (closed enum; complete set per §9.3)
- `Source_Operation` (closed enum; complete set per §9.3 — PDF content-stream operators plus `Cell`, `VL_Row`, `Manual_Entry`)

> **Note on Terminal_Type:** Manufacturer-specific brand names (e.g. "Wago terminal") are **not** carried as Terminal_Type values. The norm-conformant construction designation is `SpringClamp_Terminal`. Manufacturer information is captured separately in the `Manufacturer` attribute of Element_Data. This avoids mixing norm classification with brand designation.

### 9.2 Attribute_Lookup Additions

> **Authoritative Attribute_Lookup Seed Catalog for v0.8.** The entries in this section are the **single normative source** for `Attribute_Lookup` materialization. Every `Attribute_Name` listed here SHALL be materialized as one `Attribute_Lookup` row with the specified `Scope`, `Type_Constraint`, `Data_Type`, `Required` flag, and (where applicable) `Allowed_Values_Enum_Field` binding to the §9.3 Authoritative Enum_Lookup Seed Catalog. The catalog is part of this specification and is required for Level-1 Workbook Conformance. Projects MAY add project-local `Attribute_Lookup` rows beyond this catalog via their `Project_Lookup_Profile_ID`; the base set listed here SHALL always remain present in every workbook.

> **Conformance severity of `Required=TRUE` (clarified v0.8.3, patch).** A `Required=TRUE` row states that a competently executed extraction of a document of this `Type_Constraint` typically CAN populate this attribute — not that every individual source document is guaranteed to contain the value. Real-world build-and-check experience (three workbooks from two laboratory plants) showed that a source document can be entirely correctly and completely extracted per this specification and still leave a `Required=TRUE` attribute unpopulated, simply because that specific source instance never carried the value (e.g. a Fuse symbol drawn without an annotated rated current). This is a **source-content completeness** fact, not an **artifact-conformance** defect (per §1 Level 1 vs. content correctness) — Principle 4 (§1.1) forbids inventing a value to satisfy the flag. A validator therefore SHALL report an unpopulated `Required=TRUE` attribute as a non-blocking finding (distinct from a Level-1 conformance failure) rather than withholding Level-1 conformance for it; the finding remains visible for downstream review, it merely does not gate conformance. Correspondingly, P8's post-condition (§11.4, "All required attributes per Attribute_Lookup populated") is satisfied by a good-faith, non-fabricated extraction attempt, not by every value being literally present. **Where an attribute would be absent for the clear majority of documents of a given `Document_Type`** — i.e. it is not merely occasionally missing but structurally atypical for that document family — the correct fix is instead a catalog correction: scope the `Required=TRUE` row's `Type_Constraint` to the `Document_Type`(s) where it is actually typical, and add a companion `Required=False` row (same `Attribute_Name`, `Document_Type`-restricted to the others) so the attribute remains a valid, documented, optional field there. `Rated_Current` (`Fuse`, `Circuit_Breaker`) and `Input_Voltage`/`Output_Voltage` (`Power_Supply`) are corrected this way below: required for `Document_Type=Terminal_Diagram` (where a dedicated ratings table, e.g. a "Sicherung/Nennstrom" block, is a typical Klemmenplan feature), optional for `Document_Type=Circuit_Diagram` (a pure wiring schematic structurally does not carry nameplate data unless the drafter chose to annotate it inline).

The compact-notation blocks below are the catalog rendering — each line is one `Attribute_Lookup` row group (commas separate attributes that share the same `Scope` and `Type_Constraint`). The mapping from this notation to physical `Attribute_Lookup` rows is mechanical: one row per `Attribute_Name`, copying the `Scope` and `Type_Constraint` from the block header.

```
Scope=Element, Type_Constraint=Element_Type=Terminal:
 Terminal_Number (mandatory), Terminal_Strip_Designation (mandatory),
 Polarity (Enum), Terminal_Type (Enum), Manufacturer, Type_Designation,
 Rated_Cross_Section, Rated_Voltage, Rated_Current

Scope=Element, Type_Constraint=Element_Type=Terminal_Strip:
 Terminal_Count, Function, Position_in_Cabinet, Manufacturer, Terminal_System

Scope=Element, Type_Constraint=Element_Type=Contactor:
 Coil_Voltage (mandatory), Rated_Operational_Current, Main_Contact_Count,
 Aux_Contact_NO_Count, Aux_Contact_NC_Count, Utilization_Category,
 Manufacturer, Type_Designation, Target_Load

Scope=Element, Type_Constraint=Element_Type=Fuse AND Document_Type=Terminal_Diagram (Document_Type-scoped as of v0.8.3-patch; see Required=TRUE conformance-severity note above):
 Rated_Current (mandatory), Trip_Characteristic, Protection_Form, Pole_Count,
 Rated_Voltage, Rated_Breaking_Capacity, Manufacturer, Type_Designation,
 Target_Load

Scope=Element, Type_Constraint=Element_Type=Fuse AND Document_Type=Circuit_Diagram (added v0.8.3-patch):
 Rated_Current (optional — a pure wiring schematic does not structurally
 carry nameplate/rating data; populate when the drafter annotated it inline,
 otherwise leave unpopulated), Trip_Characteristic, Protection_Form,
 Pole_Count, Rated_Voltage, Rated_Breaking_Capacity, Manufacturer,
 Type_Designation, Target_Load

Scope=Element, Type_Constraint=Element_Type=Circuit_Breaker AND Document_Type=Terminal_Diagram (Document_Type-scoped as of v0.8.3-patch):
 (all Fuse/Terminal_Diagram attributes) + Trip_Current_Residual, Residual_Current_Type

Scope=Element, Type_Constraint=Element_Type=Circuit_Breaker AND Document_Type=Circuit_Diagram (added v0.8.3-patch):
 (all Fuse/Circuit_Diagram attributes, all optional) + Trip_Current_Residual, Residual_Current_Type

Scope=Element, Type_Constraint=Element_Type=Switch:
 Switch_Type, Pole_Count, Rated_Current, Rated_Voltage,
 Rated_Breaking_Capacity, Manufacturer, Type_Designation

Scope=Element, Type_Constraint=Element_Type=Socket_Outlet:
 Socket_Type, Rated_Voltage, Rated_Current, IP_Protection, Mounting_Type

Scope=Element, Type_Constraint=Element_Type=Power_Supply AND Document_Type=Terminal_Diagram (Document_Type-scoped as of v0.8.3-patch):
 Input_Voltage (mandatory), Output_Voltage (mandatory), Output_Power,
 Output_Current, Manufacturer, Type_Designation, Circuit_Topology

Scope=Element, Type_Constraint=Element_Type=Power_Supply AND Document_Type=Circuit_Diagram (added v0.8.3-patch):
 Input_Voltage (optional — see Required=TRUE conformance-severity note above),
 Output_Voltage (optional, same reason), Output_Power, Output_Current,
 Manufacturer, Type_Designation, Circuit_Topology

Scope=RepresentedItem, Type_Constraint=RepresentedItem_Type=Terminal_Strip:
 Function, Voltage_Level, Terminal_Count, Terminal_System,
 Position_in_Cabinet

Scope=RepresentedItem, Type_Constraint=RepresentedItem_Type=Control_Cabinet:
 Cabinet_Manufacturer, Cabinet_Type, IP_Protection, Dimensions_HxWxD,
 Terminal_Strip_Count

Scope=Connection (all Terminal_Diagram connections, no Type_Constraint):
 Wire_Color (Enum), Wire_Color_Secondary (Enum), Polarity (Enum),
 Cross_Section, Wire_Number, Cable_Number, Cable_Type (Enum),
 Total_Wire_Count, Shielding, Connection_Type (Enum), Length,
 Connection_Point_From, Connection_Point_To, Remark

Scope=Element, Type_Constraint=Element_Type=Auxiliary_Contactor (added v0.8.3):
 Coil_Voltage, Rated_Operational_Current, Aux_Contact_NO_Count,
 Aux_Contact_NC_Count, Manufacturer, Type_Designation, Target_Load,
 Function_Scope (Enum: Signal | Power, per §5.4 discriminator).
  §5.4 describes this Element_Type as "attributes identical to Contactor",
  but unlike Contactor's Coil_Voltage (mandatory), Coil_Voltage is deliberately
  OPTIONAL here: reserve/unused Auxiliary_Contactor positions (a common
  as-built pattern — a relay slot reserved but not yet wired to a coil
  circuit) would otherwise fail Required-attribute checks for a position
  the source explicitly documents as unused. Projects requiring strict
  mandatory enforcement MAY override via a project-local Attribute_Lookup row.

Scope=Element, Type_Constraint=Element_Type=Motor (added v0.8.3):
 Manufacturer, Type_Designation, Target_Load, Rated_Power, Rated_Current,
 Rated_Voltage (all optional; §5.11 defines classification for Motor but no
 dedicated attribute set — this closes that gap without introducing any
 mandatory attribute)

Scope=Element, Type_Constraint=Element_Type=Valve_Actuator (added v0.8.3):
 Manufacturer, Type_Designation, Signal_Standard (all optional)

Scope=Element, Type_Constraint=Element_Type=Sensor (added v0.8.3):
 Manufacturer, Type_Designation, Measured_Variable (DIN 19227-2 measured-variable
 code as drawn on the symbol, e.g. "F" for flow), Signal_Standard (all optional)

Scope=Element, Type_Constraint=Element_Type=Transducer (added v0.8.3):
 Manufacturer, Type_Designation, Measured_Variable, Signal_Standard (all optional)

Scope=Element, Type_Constraint=Element_Type=PLC_Module (added v0.8.3):
 Address (I/O address as printed, e.g. "EW8", "E1.0"), Module_Type (manufacturer
 order code), Channel, Slot, Manufacturer (all optional)

Scope=Element, Type_Constraint=Element_Type=Cabinet_Aggregate (added v0.8.3):
 Manufacturer, Type_Designation (all optional)

Scope=Element, Type_Constraint=Element_Type=Control_Cabinet (added v0.8.3):
 Cabinet_Manufacturer, Cabinet_Type, IP_Protection, Dimensions_HxWxD,
 Terminal_Strip_Count (all optional; mirrors the existing §7.3
 RepresentedItem_Type=Control_Cabinet block for the case — per §10.1 — where
 Control_Cabinet is modeled as an Element_ID rather than only as a
 Document_RepresentedItem)
```

**Additional fields for Circuit_Diagram:**

```
Scope=Document, Type_Constraint=Document_Type=Circuit_Diagram:
 Document_Subtype (Enum: Primary | Secondary, mandatory)

Scope=Document (no Type_Constraint — applicable to every workbook):
 Source_Format (Enum: PDF_Drawing | Excel_Sheet | Verschaltungsliste | Manual_Entry, MANDATORY).
  Every workbook SHALL contain exactly one Document_Data row with Attribute_Name='Source_Format'
  and an Attribute_Value listed in the Enum_Lookup for Field_Name='Source_Format'. Process steps
  P1 (Object extraction) and P3 (Cluster formation) consume this value to select the correct
  extraction and cluster regime; without it, the workbook is not generatable in a deterministic
  way and is not spec-compliant. Attribute registration is checked by I13, enum validity is checked
  by I14, and mandatory one-row cardinality is enforced explicitly by I29. Validators MUST report
  a violation if Source_Format is missing, duplicated, or carries a value outside the Enum.

Scope=Element (no Type_Constraint — applicable to any element on a Circuit_Diagram sheet):
 Current_Path_Number (integer, optional, per S3.1)

Scope=Element, Type_Constraint=Element_Type ∈ {Main_Contact, Auxiliary_Contact}:
 Contact_Designation (string, mandatory): contact identifier as in source
  document (e.g. "1/2", "3/4", "13/14", "21/22", "53/54")

Scope=Element, Type_Constraint=Element_Type=Coil:
 Coil_Voltage (string, optional): semantic inherited from §5.3 Contactor

Scope=Element, Type_Constraint=Element_Type=Indicator_Lamp:
 Lamp_Color (Enum: Wire_Color codes per IEC 60757),
 Lamp_Function (string), Rated_Voltage, Manufacturer, Type_Designation
```

**Attribute_Lookup completeness pass :** The following additional `Attribute_Lookup` entries are required to cover attributes that are referenced by rules, worked examples, or aggregation logic but were not previously registered. Validators SHALL accept these registrations as part of the v0.8 baseline `Attribute_Lookup` seed.

```
Scope=Document (no Type_Constraint — applicable to every workbook):
 Project_Name (string, mandatory for AG-eligibility — see §11.10):
  Project membership identifier; AG rules are evaluated across workbooks
  sharing the same Project_Name value. Without Project_Name, a workbook
  is treated as a project-singleton for aggregation purposes.

 Primary_RKZ (string, optional): document-level reference designation
  (used as Document_RepresentedItem.Primary_RKZ shadow in workbooks
  that maintain a Document-level RKZ such as the full sheet path
  "Technikumsanlage.Stellenplan.TU10.F17"). Distinct from Element_ID.Primary_RKZ
  and Document_RepresentedItem.Primary_RKZ; this Document_Data attribute
  carries the bare sheet-path string for cross-workbook lookup.

 Sheet_Number (string, optional): the project-internal sheet identifier
  (e.g. "F17") as printed on the source document title block; used by
  cross-reference notation (§11.9 I26 Stromlaufplan Path-Row references
  and similar conventions).

 Bearbeiter (string, optional): processor/operator name as printed on
  the source title block (German source vocabulary, retained verbatim
  to preserve title-block fidelity per §3.7).

 Designation_Convention (Enum: IEC_81346_Conformant | DIN_19227_2_Legacy |
  Mixed | Other, optional): declares the designation convention used by
  the source document, informing I8-style normalization decisions.

 Cross_Project_Reference (string, optional, multi-value via repetition):
  per AG1 (§11.10), declares that a Coil or Contact on this document has
  its counterpart in a named different project; the Attribute_Value is
  the cross-referenced project name. Repeated rows are admitted for
  multi-project references. AG1 suppresses Coil↔Contact false-positives
  along these declared links.

Scope=RepresentedItem, Type_Constraint=RepresentedItem_Type=PCE_Request:
 Loop_Description (string, optional): free-text description of the
  PCE loop function in the source language (e.g. German title-block
  text "Sekundär-Kühlwasser-Eintritt (Vorlauf)"); preserved verbatim
  from Object.Content_Text per §3.7 Source Format Preservation.

Scope=Connection (no Type_Constraint — applicable to any connection):
 Voltage_Level (Enum: 230V_AC | 400V_AC | 24V_DC | Signal_4_20mA |
  Signal_0_10V | Bus_Signal, optional): the connection's voltage level
  per §9.3 Authoritative Seed Catalog; consumed by I24 (Stromlaufplan-
  specific Wire_Color/Voltage_Level coherence rule) and by Electrical_Node
  binding when the optional A.O2 sheet is used.

 Signal_Standard (string, optional): industrial signal standard identifier
  (e.g. "4..20mA", "0..10V", "PT100", "PROFIBUS", "PROFINET", "HART").
  Used in worked examples §12.1 and §12.3 to record signal-loop properties
  not captured by Voltage_Level alone (which is a coarse voltage tier).

Scope=Element, Type_Constraint=Document_Type=Circuit_Diagram:
 Path_Numbering_Grid (Enum: Strompfad | None, optional): declares whether
  the document uses Stromlaufplan current-path numbering (Strompfad grid
  along the lower edge of the diagram); consumed by I26 (Stromlaufplan
  cross-reference notation).
```

**Validator binding:** I13 (Attribute_Lookup-only attributes) and I14 (enum validity) operate against this registered set. Worked examples in §12 that reference an attribute not present in this Attribute_Lookup seed must be read as compact-notation excerpts — they remain explanatory until the attribute is registered above.

### 9.3 Unified Enum_Lookup Encoding Convention

Per §0.1, **every** enum-typed field follows one uniform encoding pattern, using the existing v0.4 `Enum_Lookup` columns (`Allowed_Value`, `Description`, `Normative_Reference`) — no structural change is required:

1. **`Allowed_Value` = language-neutral code.** Norm code where one is established; otherwise the canonical English schema term.
2. **`Description` = bilingual reading aid** in the form `"<DE> / <EN>"`. This field SHOULD be populated for any field whose values carry a language-bound plain-text meaning (colors, switch types, terminal types, …) — this is a **recommended documentation convention, not a validation rule**. The v0.4 column definition (`Required = No`) is **unchanged**; no I-rule enforces Description presence. For purely schema-internal codes (Object_Type, Match_Status) where the code is self-explanatory, the convention does not apply.
3. **`Normative_Reference` = source of the code** (norm number, or `Schema` for schema-internal codes, or a rule ID like `M3`).
4. **Source originals are preserved in `Object`.** For source-extracted enum values, the verbatim source word stays in `Object.Content_Text`; the encoded value lives in the relevant Data sheet; provenance links the two.

**Validation note:** I14 (every enum value must exist in `Enum_Lookup` for its `Field_Name`) operates against `Allowed_Value` — i.e. against the **code**, not the description. The bilingual `Description` is a reading aid only and is never validated against.

**`Unspecifiable` marker exemption:** The universal `Unspecifiable` marker (E5) is exempted from the Description convention. By definition (v0.4 §E5) it has no `Enum_Lookup` entry — and therefore no Description — and is universally accepted by I14 in any enum-typed field. The encoding convention does not introduce any change to E5.

#### Master encoding table — code system per Field_Name

| Field_Name | Code system | `Allowed_Value` example | `Description` example | `Normative_Reference` | Source-extracted? |
|---|---|---|---|---|---|
| Wire_Color | IEC 60757 letter code | `RD` | `rot / red` | IEC 60757 | yes (original in Object) |
| Polarity | IEC 60445 / VDE conductor marking | `L1` | `Außenleiter 1 / line conductor 1` | DIN VDE 0100-200 | yes |
| Cable_Type | VDE type designation / manufacturer spec | `LiYCY` | `geschirmte Steuerleitung / shielded control cable` | DIN VDE 0281 (NYM, NYY, H07V-K); manufacturer spec (LiYCY, Ölflex) | yes (source-extracted) |
| IEC_81346_2_Class | IEC 81346-2 letter | `X` | `Verbinden / connecting` | IEC 81346-2 | classified |
| Trip_Characteristic | IEC 60898-1 / IEC 60269 | `C` | `Charakteristik C / type C` | IEC 60898-1 [⚠ §16] | yes |
| Utilization_Category | IEC 60947-4-1 | `AC-3` | `Gebrauchskategorie AC-3 / utilization category AC-3` | IEC 60947-4-1 [⚠ §16] | yes |
| Residual_Current_Type | IEC TR 60755 | `A` | `Typ A / type A` | IEC TR 60755 [⚠ §16] | yes |
| IP_Protection | IEC 60529 IP code | `IP54` | `Schutzart IP54 / degree of protection IP54` | IEC 60529 [⚠ §16] | yes |
| Socket_Type | IEC 60309 / 60884 | `CEE_16A_5P` | `CEE 16A 5-polig / CEE 16A 5-pole` | IEC 60309 | classified |
| Protection_Form | IEC abbreviations | `RCBO` | `FI/LS-Schalter / residual-current breaker w. overcurrent` | IEC 61009 | classified |
| Terminal_Type | Schema (aligned to IEC 60947-7-1) | `FeedThrough_Terminal` | `Reihenklemme / feed-through terminal` | IEC 60947-7-1 | classified |
| Connection_Type | Schema | `Wire` | `Ader / wire` | Schema | classified |
| Connection_Type | Schema | `Bridge_Longitudinal` | `Längsbrücke / longitudinal bridge` | Schema | classified |
| Connection_Type | Schema | `Bridge_Cross_Fixed` | `feste Querbrücke / fixed cross bridge` | Schema | classified |
| Connection_Type | Schema | `Bridge_Cross_Pluggable` | `steckbare Querbrücke / pluggable cross bridge` | Schema | classified |
| Connection_Type | Schema | `Bridge_Insulated` | `isolierte Brücke / insulated bridge` | Schema | classified |
| Connection_Status | Schema | `Resolved` | `aufgelöst / resolved connection` | P9 | schema-internal |
| Connection_Status | Schema | (`Endpoint_Unassigned` was a v0.7 schema value; deprecated in v0.8 see §11 E4 and §9.3 Seed Catalog) | – | E4 | schema-internal |
| Connection_Status | Schema | `Unresolved` | `nicht aufgelöst / unresolved connection` | C3 | schema-internal |
| Switch_Type | Schema (aligned to IEC 60947) | `Main_Switch` | `Hauptschalter / main switch` | IEC 60947 | classified |
| Voltage_Level | Schema (technical) | `230V_AC` | `230V Wechselspannung / 230V AC` | Schema | classified |
| Layer_Type | Schema | `Voltage_Level` | `Spannungsebene / voltage level` | Schema | schema-internal |
| Layer_Type | Schema | `Functional_Section` | `Funktionsabschnitt / functional section` | Schema | schema-internal |
| Layer_Type | Schema | `Signal_Group` | `Signalgruppe / signal group` | Schema | schema-internal |
| Layer_Type | Schema | `Protection_Group` | `Schutzgruppe / protection group` | Schema | schema-internal |
| Cable_Modeling_Profile | Schema | `Core` | `Kabelnummern-basiertes Kernprofil / cable-number based core profile` | Schema | schema-internal |
| Cable_Modeling_Profile | Schema | `Asset` | `Kabel-Asset-Profil / cable asset profile` | Schema | schema-internal |
| Review_Status | Schema | `Unreviewed` | `nicht geprüft / unreviewed` | Schema | schema-internal |
| Review_Status | Schema | `Requires_Review` | `Prüfung erforderlich / requires review` | Schema | schema-internal |
| Review_Status | Schema | `Auto_Approved` | `automatisch freigegeben / auto-approved` | Schema | schema-internal |
| Review_Status | Schema | `Manually_Reviewed` | `manuell geprüft / manually reviewed` | Schema | schema-internal |
| Review_Status | Schema | `Manually_Corrected` | `manuell korrigiert / manually corrected` | Schema | schema-internal |
| Review_Status | Schema | `Rejected` | `verworfen / rejected` | Schema | schema-internal |
| Object_Type | Schema | `Text` | `Text-Objekt / text object` | A1 | schema-internal |
| Geometry_Type | Schema | `rect` | `Rechteck / rectangle` | Schema | schema-internal |
| Cluster_Type | Schema | `Containment` | `Enthaltensein / containment` | C1 | schema-internal |
| Cluster_Type | Schema | `Proximity` | `Nähe / proximity` | C2 | schema-internal |
| Cluster_Type | Schema | `Topology` | `Topologie / topology` | C3 | schema-internal |
| Cluster_Type | Schema | `Pre_Existing_Structural` | `vorgegebene Quellstruktur / pre-existing structural grouping from source format` | C0 | schema-internal (per §11.2) |
| Membership_Reason | Schema | `Containment` | `Enthaltensein / containment` | C1 | schema-internal |
| Membership_Reason | Schema | `Proximity` | `Nähe / proximity` | C2 | schema-internal |
| Membership_Reason | Schema | `Pre_Existing_Structural` | `vorgegebene Quellstruktur / pre-existing structural grouping` | C0 | schema-internal (per §11.2) |
| Match_Status | Schema | `Matched` | `übereinstimmend / matched` | M3 | schema-internal |
| Source_Role | Schema | `Label` | `Bezeichner / label` | E-rules | schema-internal |
| Source_Operation | Schema | `Tj` | `PDF text-showing operator / PDF text-showing operator` | PDF | schema-internal |
| Source_Operation | Schema | `TJ` | `PDF text-array operator / PDF text-array operator` | PDF | schema-internal |
| Source_Operation | Schema | `'` | `PDF next-line text operator / PDF next-line text operator` | PDF | schema-internal |
| Source_Operation | Schema | `"` | `PDF next-line text operator with spacing / PDF next-line text operator with spacing` | PDF | schema-internal |
| Source_Operation | Schema | `f` | `PDF fill path operator / PDF fill path operator` | PDF | schema-internal |
| Source_Operation | Schema | `F` | `PDF fill path operator / PDF fill path operator` | PDF | schema-internal |
| Source_Operation | Schema | `f*` | `PDF even-odd fill path operator / PDF even-odd fill path operator` | PDF | schema-internal |
| Source_Operation | Schema | `S` | `PDF stroke path operator / PDF stroke path operator` | PDF | schema-internal |
| Source_Operation | Schema | `s` | `PDF close-and-stroke path operator / PDF close-and-stroke path operator` | PDF | schema-internal |
| Source_Operation | Schema | `B` | `PDF fill-and-stroke path operator / PDF fill-and-stroke path operator` | PDF | schema-internal |
| Source_Operation | Schema | `b` | `PDF close-fill-and-stroke path operator / PDF close-fill-and-stroke path operator` | PDF | schema-internal |
| Source_Operation | Schema | `re` | `PDF rectangle operator / PDF rectangle operator` | PDF | schema-internal |
| Source_Operation | Schema | `Cell` | `Excel-Zelle / Excel cell` | Schema | schema-internal |
| Source_Operation | Schema | `VL_Row` | `Verschaltungslisten-Zeile / Verschaltungsliste row` | Schema | schema-internal (per §A.7 and §4.4.2) |
| Source_Operation | Schema | `Manual_Entry` | `manuelle Eingabe / manual entry` | Schema | synthetic evidence object |
| Object_Role | Schema | `Connection_Point` | `Anschlusspunkt / connection point` | Schema | schema-internal |
| Object_Role | Schema | `Label` | `Beschriftung / label` | Schema | schema-internal |
| Object_Role | Schema | `Symbol` | `Symbol / symbol` | Schema | schema-internal |
| Object_Role | Schema | `Border` | `Rahmen / border` | Schema | schema-internal |
| Object_Role | Schema | `Annotation` | `Annotation / annotation` | Schema | schema-internal |
| Object_Role | Schema | `Topology` | `Topologie / topology` | Schema | schema-internal |
| PCE_Channel_Suffix | Source | `I` | `Eingangssignal / input signal channel` | IEC 62424 | IEC 62424 §6.6.2 (T2 resolution per §4.1) |
| PCE_Channel_Suffix | Source | `O` | `Ausgangssignal / output signal channel` | IEC 62424 | IEC 62424 §6.6.2 |
| PCE_Channel_Suffix | Source | `A+` | `analoges Plus-Signal / analog positive signal channel` | IEC 62424 | IEC 62424 (analog-detail) |
| PCE_Channel_Suffix | Source | `A-` | `analoges Minus-Signal / analog negative signal channel` | IEC 62424 | IEC 62424 (analog-detail) |
| PCE_Channel_Suffix | Source | `D` | `digitales Signal / digital signal channel` | IEC 62424 | IEC 62424 |
| Element_Type | Source | `Sensor` | `Sensor / sensor (Instrument_Loop_Diagram and Terminal_Diagram)` | §5.11 / §4.1 | canonical |
| Element_Type | Source | `Transducer` | `Messumformer / transducer (Instrument_Loop_Diagram)` | §4.1 / legacy v0.4 carried value | canonical |
| Element_Type | Source | `Valve_Actuator` | `Ventilantrieb / valve actuator (Instrument_Loop_Diagram and Terminal_Diagram)` | §5.11 / §4.1 | canonical |
| Element_Type | Source | `Motor` | `Motor / motor (Terminal_Diagram and Circuit_Diagram)` | §5.11 | canonical |
| Element_Type | Source | `Actuator` | `Aktor (allgemein) / general actuator (Terminal_Diagram)` | §5.11 | canonical |
| Element_Type | Source | `Consumer` | `Verbraucher (allgemein) / general consumer (Terminal_Diagram)` | §5.11 | canonical |
| Element_Type | Source | `Terminal` | `Klemme / terminal (Terminal_Diagram and Circuit_Diagram)` | §5.1 | canonical |
| Element_Type | Source | `Terminal_Strip` | `Klemmleiste / terminal strip (Terminal_Diagram)` | §5.2 | canonical |
| Element_Type | Source | `Contactor` | `Schütz (Aggregat) / contactor (Terminal_Diagram aggregate)` | §5.3 | canonical |
| Element_Type | Source | `Auxiliary_Contactor` | `Hilfsschütz / auxiliary contactor (Terminal_Diagram and Circuit_Diagram)` | §5.4 | canonical |
| Element_Type | Source | `Fuse` | `Sicherung / fuse (Terminal_Diagram and Circuit_Diagram)` | §5.5 | canonical |
| Element_Type | Source | `Circuit_Breaker` | `Leistungsschalter / circuit breaker (Terminal_Diagram and Circuit_Diagram)` | §5.6 | canonical |
| Element_Type | Source | `Switch` | `Schalter / switch (Terminal_Diagram and Circuit_Diagram)` | §5.7 | canonical |
| Element_Type | Source | `Socket_Outlet` | `Steckdose / socket outlet (Terminal_Diagram)` | §5.8 | canonical |
| Element_Type | Source | `Power_Supply` | `Netzteil / power supply (Terminal_Diagram and Circuit_Diagram)` | §5.9 | canonical |
| Element_Type | Source | `PLC_Module` | `SPS-Modul / PLC module (Instrument_Loop_Diagram and Terminal_Diagram)` | §5.10 | canonical |
| Element_Type | Source | `Coil` | `Spule / coil (Circuit_Diagram switching-device sub-element)` | §5.13 | canonical |
| Element_Type | Source | `Main_Contact` | `Hauptkontakt / main contact (Circuit_Diagram switching-device sub-element)` | §5.13 | canonical |
| Element_Type | Source | `Auxiliary_Contact` | `Hilfskontakt / auxiliary contact (Circuit_Diagram switching-device sub-element)` | §5.13 | canonical |
| Element_Type | Source | `Indicator_Lamp` | `Meldeleuchte / indicator lamp (Circuit_Diagram and Terminal_Diagram)` | §5.13 | canonical |
| Element_Type | Source | `Control_Cabinet` | `Schaltschrank / control cabinet (aggregate, all document types)` | §7.3 / §10.1 | canonical |
| Element_Type | Source | `Cabinet_Aggregate` | `Schaltschrank-Aggregat / cabinet aggregate (composite-device aggregation, all document types)` | §5.10 | canonical |
| Element_Type | Schema | `Connection_Point` | `generierter Anschlusspunkt / generated CAEX connection-point sub-element (all document types)` | §5.13 (added v0.8.3) | classified |

**Rationale for the split:**
- **Source-extracted fields** (Wire_Color, Polarity, Cable_Type, IP_Protection, Trip_Characteristic, Utilization_Category, Residual_Current_Type) read a value from the document. The original word/code stays in `Object`; the `Allowed_Value` is the norm code. This is the Wire_Color pattern generalized.
- **Classified fields** (Terminal_Type, Connection_Type, Switch_Type, Socket_Type, Protection_Form, Voltage_Level, IEC_81346_2_Class) are not read verbatim but assigned by the recorder based on observation. Their `Allowed_Value` is the canonical schema code; the source observation that led to the classification is captured via the element's normal provenance.
- **Schema-internal fields** (Object_Type, Match_Status, …) never originate from the source; they are pure schema codes.

> **Note on classified vs. extracted:** For a field like Terminal_Type, if the source document literally contains the word `Federkraftklemme`, that word is preserved verbatim in the corresponding `Object.Content_Text`. The `Element_Data` value `Terminal_Type=SpringClamp_Terminal` is the encoded classification. The bilingual `Description` (`Federkraftklemme / spring-clamp terminal`) bridges the two. No source content is overwritten.


#### Authoritative Enum_Lookup Seed Catalog

> **Authoritative source for Enum_Lookup generation.** The following table is the **single normative reference** for which enum fields exist in this schema and which `Allowed_Value` set each field carries. Every `Field_Name` listed here SHALL be expanded into one `Enum_Lookup` row per `Allowed_Value`. Enum values mentioned elsewhere in §9.1 or in descriptive sections are explanatory only — when in conflict, this table governs. The Master encoding table above provides encoding-convention examples (norm-code vs. schema-code, bilingual Description usage) and is **not** authoritative for completeness.

**Materialization rule (Excel workbook generation, A.25 binding):** For every `(Field_Name, Allowed_Value)` pair listed in this catalog, exactly **one physical `Enum_Lookup` row** SHALL be created. The physical `Enum_Lookup.Allowed_Value` cell SHALL contain **exactly one value**. CSV lists, set notation (`{A, B}`), pipe-separated lists (`A | B`), or ranges (`1..5`) inside a single `Allowed_Value` cell are **not permitted** — they appear in this catalog purely as a compact specification convenience. Validators SHALL reject any `Enum_Lookup` row whose `Allowed_Value` contains a comma, pipe, brace, or whitespace-separated multiple tokens. Bilingual `Description` and `Normative_Reference` are populated per the Master encoding table convention above; for schema-internal fields without an external norm, `Normative_Reference="Schema"`.

**Enum closedness convention:**
- **Closed** (default): the catalog lists the complete set of admitted values; new values require a schema-version bump.
- **(project-extensible)**: the catalog lists the schema-default values; projects MAY add additional values via project-local `Enum_Lookup` rows under their `Project_Lookup_Profile_ID` (per §11.7 I14 and §3.4). The base set listed here SHALL always remain valid.

**Project-local enum-extension binding:** In v0.8, `Enum_Lookup` has no separate `Project_Lookup_Profile_ID` column. All project-local `Enum_Lookup` rows contained in a workbook are governed by the workbook-level `Schema_Metadata` row with `Metadata_Key=Project_Lookup_Profile_ID`. If this key is empty, project-local enum extensions are workbook-local. If this key is populated, aggregation-level validators apply the governance behavior defined in I14.

| Field_Name | Closedness | Allowed_Value set | Normative_Reference |
|---|---|---|---|
| `Document_Type` | Closed | `Instrument_Loop_Diagram`, `Terminal_Diagram`, `Circuit_Diagram` | Schema |
| `Document_Subtype` | Closed | `Primary`, `Secondary` | Schema |
| `RepresentedItem_Type` | Closed | `PCE_Request`, `Terminal_Strip`, `Circuit`, `Plant_Section`, `Control_Cabinet`, `Distribution_Panel`, `Function_Group` | Schema |
| `Element_Type` | Closed | `Sensor`, `Transducer`, `Valve_Actuator`, `Motor`, `Actuator`, `Consumer`, `Terminal`, `Terminal_Strip`, `Contactor`, `Auxiliary_Contactor`, `Fuse`, `Circuit_Breaker`, `Switch`, `Socket_Outlet`, `Power_Supply`, `PLC_Module`, `Coil`, `Main_Contact`, `Auxiliary_Contact`, `Indicator_Lamp`, `Control_Cabinet`, `Cabinet_Aggregate`, `Thermostat`, `Heater`, `Connection_Point` (added v0.8.3, §5.13) | Schema (per §5, §9.3 Master table for descriptions) |
| `Classification_System` | Closed | `IEC 81346-2`, `IEC 62424`, `IEC 60617-2`, `IEC 60617-3`, `IEC 60617-6`, `IEC 60617-7`, `IEC 60617-8`, `DIN 19227-2` | Schema / referenced norms |
| `Source_Format` | Closed | `PDF_Drawing`, `Excel_Sheet`, `Verschaltungsliste`, `Manual_Entry` | Schema |
| `Scope` | Closed | `Document`, `Element`, `RepresentedItem`, `Connection` | Schema |
| `Match_Status` | Closed | `Matched`, `Only_TopDown`, `Only_Cluster` | M-rules |
| `Match_Rule` | Closed | `M1_Primary_RKZ`, `M2_Spatial`, `Manual_Resolution`, `Not_Applicable` | M-rules |
| `Resolution_Status` | Closed | `Open`, `Resolved_AutoMatch`, `Resolved_KeepBoth`, `Resolved_TopDown_Valid`, `Resolved_Cluster_Valid`, `Rejected` | Schema |
| `Connection_Type` | Closed | `Wire`, `Bridge_Longitudinal`, `Bridge_Cross_Fixed`, `Bridge_Cross_Pluggable`, `Bridge_Insulated` | Schema |
| `Connection_Status` | Closed | `Resolved`, `Unresolved` | P9, E4, C3. `Endpoint_Unassigned` is deprecated for Connection_ID rows in v0.8 because `Connection_ID.From_Element_ID` and `Connection_ID.To_Element_ID` are required per §A.20. `Connection_Status=Unresolved` is permitted only when both endpoints are resolved but connection semantics or attributes still require review. Unresolved topology evidence with missing endpoints remains in `Object.Topology_Validation_Status=Unresolved`; no `Connection_ID` row is created for missing endpoints. |
| `Object_Type` | Closed | `Text`, `Graphic`, `Topology` | A4 |
| `Object_Role` | Closed | `Connection_Point`, `Label`, `Symbol`, `Border`, `Annotation`, `Topology` | Schema (per §A.7, C3) |
| `Geometry_Type` | Closed | `rect`, `line`, `path` | Schema (per A.7 — minimum set of graphic primitives required for PDF source reconstructability; covers PDF content-stream operators `re` for rectangles, line-drawing for `S`/`s`/`f` segments, and arbitrary path constructions) |
| `Source_Operation` | Closed | `Tj`, `TJ`, `'`, `"`, `f`, `F`, `f*`, `S`, `s`, `B`, `b`, `re`, `Cell`, `VL_Row`, `Manual_Entry` | Schema (PDF operators per ISO 32000-1; Schema-internal markers for non-PDF sources) |
| `Source_Role` | Closed | `Label`, `Value`, `Symbol` | Schema (E-rules) |
| `Cluster_Type` | Closed | `Containment`, `Proximity`, `Topology`, `Pre_Existing_Structural` | C0–C3 |
| `Membership_Reason` | Closed | `Containment`, `Proximity`, `Pre_Existing_Structural` | C0–C2 |
| `Membership_Status` | Closed | `Confirmed`, `Inferred` | Schema |
| `Topology_Validation_Status` | Closed | `Valid_Connection`, `Unresolved` | C3 |
| `Rule_Category` | Closed | `A`, `C`, `M`, `P`, `E`, `K`, `I`, `S`, `AG` | Schema |
| `Data_Type` | Closed | `String`, `Enum`, `Integer`, `Float`, `Boolean`, `FK`, `Date`, `DateTime` | Schema |
| `Source` | Closed | `TopDown`, `Cluster`, `Matched`, `Manual_Entry`, `Rule_Derived` | Schema |
| `CAEX_Type` | Closed | `InternalElement`, `ExternalInterface` | CAEX / AML convention |
| `Relationship_Type` | Closed | `Primary`, `Shared`, `Secondary` | Schema |
| `Derivation_Status` | Closed | `Element_Derived`, `No_Element_Derivable`, `Ambiguous`, `Failed` | Schema |
| `Extraction_Method` | Closed | `OCR`, `Native_Text`, `LLM_Classification`, `Manual_Entry`, `Rule_Based_Parser` | Schema |
| `Classified_Object_Type` | Closed | `Element`, `RepresentedItem`, `Connection`, `Document` | Schema |
| `Aspect` | Closed | `Function`, `Location`, `Product` | IEC 81346-1 Ed. 2 (2009) Three main aspects. **Note:** DIN EN IEC 81346-1:2024-07 (Ed. 3, EN IEC 81346-1:2022) extends the aspect enumeration to **five values** — `FUNCTION_ASPECT`, `PRODUCT_ASPECT`, `LOCATION_ASPECT`, `TYPE_ASPECT`, `OTHER_ASPECT` (per §A.4.1 EXPRESS aspect_kind enumeration in that edition). The v0.8 schema retains the three main aspects of Ed. 2 for backward compatibility with existing project tooling; extension to five values is a planned v0.9 schema change. See §16 Entry 18. |
| `Designation_Convention` | Closed | `IEC_81346_Conformant`, `DIN_19227_2_Legacy`, `Mixed`, `Other` | Schema (per §9.2 Attribute_Lookup baseline) |
| `Path_Numbering_Grid` | Closed | `Strompfad`, `None` | Schema (per §9.2 Attribute_Lookup baseline; consumed by I26) |
| `Node_Type` | Closed | `Star_Point`, `Ring_Node`, `Bus_Tap`, `Junction` | Schema |
| `Shielding` | Closed | `Shielded`, `Unshielded`, `Foil`, `Braid` | Schema |
| `Parsing_Status` | Closed | `Parsed_OK`, `Parsed_Ambiguous`, `Parsed_Failed` | Schema |
| `Topic_Identification_Status` | Closed | `Confirmed`, `Inferred`, `Ambiguous`, `Failed` | Schema |
| `Layer_Type` | Closed | `Voltage_Level`, `Functional_Section`, `Signal_Group`, `Protection_Group` | Schema (per A.O2) |
| `Cable_Modeling_Profile` | Closed | `Core`, `Asset` | Schema (per A.O3) |
| `Review_Status` | Closed | `Unreviewed`, `Requires_Review`, `Auto_Approved`, `Manually_Reviewed`, `Manually_Corrected`, `Rejected` | Schema (per F3) |
| `Voltage_Level` | Closed | `230V_AC`, `400V_AC`, `24V_DC`, `Signal_4_20mA`, `Signal_0_10V`, `Bus_Signal` | Schema (per §5.10, I24) |
| `Wire_Color` | Closed | `BK`, `BN`, `RD`, `OG`, `YE`, `GN`, `BU`, `VT`, `GY`, `WH`, `PK`, `TQ`, `GNYE` | IEC 60757 |
| `Wire_Color_Secondary` | Closed | `BK`, `BN`, `RD`, `OG`, `YE`, `GN`, `BU`, `VT`, `GY`, `WH`, `PK`, `TQ`, `GNYE` | IEC 60757 |
| `Polarity` | Closed | `L1`, `L2`, `L3`, `L`, `N`, `PE`, `PEN`, `L+`, `L-`, `G+`, `G-`, `V+`, `V-`, `FE`, `AC`, `DC` | DIN VDE 0100-200 / IEC 60445 |
| `IEC_81346_2_Class` | Closed | `A`, `B`, `C`, `E`, `F`, `G`, `H`, `K`, `M`, `P`, `Q`, `R`, `S`, `T`, `U`, `V`, `W`, `X`, `Y` | IEC 81346-2:2009 Ed. 2 Table 1 (D, J, L, N, Z reserved; I, O not to be applied — deliberately excluded; Y carried with the Ed. 2 "reserved" caveat — see §16 Entry 19) |
| `PCE_Channel_Suffix` | (project-extensible) | `I`, `O`, `A+`, `A-`, `D` | IEC 62424 §6.6.2 (T2 resolution per §4.1); project-local extensions permitted where source documents use additional channel suffixes |
| `Terminal_Type` | (project-extensible) | `FeedThrough_Terminal`, `DoubleLevel_Terminal_Internal_Connected`, `DoubleLevel_Terminal_Internal_Separated`, `MultiLevel_Terminal`, `Disconnect_Terminal`, `Pluggable_Terminal`, `SpringClamp_Terminal`, `Screw_Terminal` | IEC 60947-7-1 (base set); project-local extensions permitted |
| `Switch_Type` | (project-extensible) | `Main_Switch`, `Selector_Switch`, `Push_Button_NO`, `Push_Button_NC`, `Emergency_Stop`, `Limit_Switch`, `Pressure_Switch`, `Temperature_Switch`, `Float_Switch`, `Toggle_Switch`, `Rotary_Switch`, `Key_Switch` | IEC 60947 (base set); project-local extensions permitted |
| `Cable_Type` | (project-extensible) | `NYM`, `NYY`, `H07V-K`, `LiYCY`, `LiYY`, `JE-LiYCY`, `JZ-500` | DIN VDE 0281 (NYM, NYY, H07V-K); manufacturer specification (LiYCY, LiYY, JE-LiYCY, JZ-500 — see §8.5 for typical applications) — project-local extensions permitted for project-specific cable families. The §9.3 Seed Catalog mirrors §8.5 verbatim; if a project introduces additional manufacturer-specific cable families (Ölflex variants, etc.), these are added via project-local Enum_Lookup rows under the workbook's `Project_Lookup_Profile_ID`. |
| `Socket_Type` | (project-extensible) | `Schuko`, `CEE_16A_3P`, `CEE_16A_5P`, `CEE_32A_5P`, `French_Type`, `USB` | IEC 60309 (CEE); IEC 60884 (Schuko); project-local extensions permitted |
| `Protection_Form` | (project-extensible) | `Fuse_NH`, `Fuse_Diazed`, `MCB`, `RCBO`, `RCD` | IEC 60269 (Fuse_NH, Fuse_Diazed); IEC 60898-1 (MCB); IEC 61009 (RCBO); IEC 61008 (RCD) [⚠ see §16] — project-local extensions permitted for finer protection-form distinctions (Fuse_D01/D02, MCCB, RCCB, MotorProtectionRelay, ThermalOverloadRelay are common project-local extensions). The §9.3 Seed Catalog mirrors §5.5 verbatim. |
| `Utilization_Category` | (project-extensible) | `AC-1`, `AC-3`, `AC-4`, `AC-15`, `DC-1`, `DC-3` | IEC 60947-4-1 [⚠ see §16] — project-local extensions permitted |
| `Trip_Characteristic` | (project-extensible) | `B`, `C`, `D`, `K`, `Z`, `gG`, `gL`, `aM` | IEC 60898-1 (B/C/D/K/Z for MCB); IEC 60269 (gG/gL/aM for fuse) [⚠ see §16] — project-local extensions permitted |
| `IP_Protection` | (project-extensible) | `IP00`, `IP20`, `IP44`, `IP54`, `IP55`, `IP65`, `IP67`, `IP68`, `IP69K` | IEC 60529 [⚠ see §16] — project-local extensions permitted |
| `Residual_Current_Type` | (project-extensible) | `AC`, `A`, `F`, `B`, `B+` | IEC TR 60755 [⚠ see §16] — project-local extensions permitted |
| `Mounting_Type` | (project-extensible) | `Surface`, `Flush`, `DIN_Rail`, `Wall` | Schema (per §5.8 Socket_Outlet) — project-local extensions permitted |
| `Circuit_Topology` | (project-extensible) | `linear`, `switched`, `galvanically_isolated`, `non_isolated` | Schema (per §5.9 Power_Supply) — project-local extensions permitted |

`Unspecifiable` (per E5) is the universal fallback and is **not** materialized as a separate `Enum_Lookup` row for every field. It is implicitly accepted by I14 in every enum-typed field. The same applies to project-local enum extensions: when a project adds an `Enum_Lookup` row under its `Project_Lookup_Profile_ID`, the schema-default row stays untouched.

**Consistency with §9.1:** The §9.1 sub-sections (Wire_Color, Polarity, Cable_Type, etc.) describe canonical examples, source-extraction guidance, and discriminators. They are **explanatory**, not authoritative. When a value appears in §9.1 but not in the Seed Catalog above, the Seed Catalog governs (the value is either to be added to the catalog or removed from §9.1). For v0.8, the §9.1 values have been migrated into the Seed Catalog above; §9.1 may continue to carry didactic context for these enums without re-stating the catalog.



### 9.4 Type_Constraint Syntax

The `Type_Constraint` column of `Attribute_Lookup` restricts an attribute's applicability to documents/elements/connections of a specific class. Three syntactic forms are admitted; validators MUST recognize all three:

| Form | Pattern | Example | Meaning |
|---|---|---|---|
| **Equality** | `Field=Value` | `Document_Type=Circuit_Diagram` | Attribute applies only when the named field has the literal value |
| **Set inclusion** | `Field ∈ {V1, V2, …}` | `Element_Type ∈ {Main_Contact, Auxiliary_Contact}` | Attribute applies when the named field has any of the listed values |
| **Conjunction** | `<C1> AND <C2>` (each `<Ci>` is one of the above) | `Document_Type=Circuit_Diagram AND Element_Type=Coil` | Both sub-constraints must hold simultaneously |

**No further forms** (disjunction, negation, regex matching, range comparison) are admitted in v0.8. Use of any other syntactic form in `Type_Constraint` is a schema-conformance violation. If a more expressive constraint is required, multiple `Attribute_Lookup` rows with separate `Type_Constraint` values are used (e.g. one row per applicable Element_Type), each row producing the same attribute scope by repetition.

**Empty Type_Constraint** (cell blank) means the attribute applies universally within its `Scope` (no further restriction).

**Field names admissible in Type_Constraint:** v0.8 admits only stable structural fields: `Document_Type`, `RepresentedItem_Type`, and `Element_Type`. **Clarification:** `Connection_Type` is **NOT** admissible in `Type_Constraint` in v0.8, because `Connection_Type` is itself a Long-Form attribute carried in `Connection_Data` (Attribute_Name=Connection_Type, Scope=Connection) rather than a stable column in `Connection_ID`. Validators must not require Long-Form lookups to evaluate Type_Constraint expressions, since this would couple Attribute_Lookup validation to per-row Connection_Data scans. Attribute-based constraints on Long-Form values (including any future `Type_Constraint=Connection_Type=…`) are deferred to a later schema revision because their evaluation requires owner-context lookup semantics across multiple data rows. If a Connection-scoped attribute must vary by Connection_Type, model it via separate `Attribute_Lookup` rows with `Scope=Connection` (no Type_Constraint) and let workbook-level rules describe the conditional applicability. The right-hand side `Value`, `V1`, `V2`, … must exist in `Enum_Lookup` if the corresponding field is enum-validated; otherwise it is a literal string.

**Validator implementation note:** Validators evaluate `Type_Constraint` as a tree expression: split on `AND` → for each sub-expression, parse as equality or set inclusion → evaluate against the row being validated. Rows whose constraints evaluate to false are excluded from validity-checking; the rule is then "if Type_Constraint matches, the attribute is required (per `Required` column); otherwise not required". This formalization makes I13-style validation deterministic.

---

## 10. Hierarchical Structures

### 10.1 Element Hierarchy in Terminal_Diagram

```
Control_Cabinet (Element_Type=Control_Cabinet, optional)
└─ Terminal_Strip (Element_Type=Terminal_Strip, RepresentedItem)
  ├─ Terminal X1:1/L1 (Element_Type=Terminal, ExternalInterface)
  ├─ Terminal X1:2/L2
  ├─...
  └─ Terminal X1:22/PE

Switchgear (separate in Element_ID, no parent or parent=Control_Cabinet):
- Contactor K1 (Element_Type=Contactor, InternalElement)
- Fuse F1 (Element_Type=Fuse)
-...
```

Hierarchy is expressed via `Parent_Element_ID` (I16-conformant).

### 10.2 Connection Modeling

Connections are **flat** (no hierarchy): each Connection_ID row is standalone. Grouping is done via the `Cable_Number` attribute, not via parent relationship.

---

## 11. Rule Catalogs

The schema's rule framework spans seven families. **A/C/M-rules** govern PDF parsing and object/cluster/match logic (§11.1–§11.3). **P-rules** define the sequential process steps for populating sheets (§11.4). **E-rules** define error-marker conventions (§11.5). **K-rules** define lookup-table conventions (§11.6). **I-rules** define cross-sheet integrity (§11.7–§11.9). Source-extraction rules (S1–S3) are documented separately in §4.

### 11.1 Object Rules (A)

| ID | Rule |
|---|---|
| **A1** | A **Text-Object** is a contiguous text run delivered by the PDF parser in exactly one text operation (`TJ`, `Tj`, `'`, `"`). |
| **A2** | A **Graphic-Object** is a contiguous path delivered by the PDF parser in exactly one path operation (`f`, `F`, `f*`, `S`, `s`, `B`, `b`, `re` followed by `S` or `f`). |
| **A3** | A Text-Object and a Graphic-Object are never the same Object, even with identical bounding boxes. |
| **A4** | Every Object carries mandatorily: unique `Object_ID`, `Object_Type` (`Text` \| `Graphic` \| `Topology`), content, and source-format-specific positional metadata as defined in §A.7. PDF sources use PDF-coordinate bounding boxes. Excel, Verschaltungsliste, and `Manual_Entry` sources use the source-format-specific positional conventions of §A.7; PDF bounding boxes are not universally required. |
| **A5** | A Graphic-Object is classified as a **candidate Topology-Object** iff (a) it is an open path with exactly two endpoints (one `moveto` followed by exactly one `lineto`, or equivalent), AND (b) its bounding box diagonal exceeds a minimum length threshold (default: 5 PDF points ≈ 1.8 mm; configurable tool parameter, starting value, to be calibrated against real data). The threshold filters out short scribbles, tick marks, decimal points and similar sub-line artifacts. Final classification — whether the candidate is a valid connection, decorative, or has unresolved endpoints — is recorded in `Object.Topology_Validation_Status` after C3 evaluation. |

### 11.2 Cluster Rules (C)

**Applicability by source format:** C0 applies when the source format provides intrinsic structure (Excel sheets with header blocks, XML with sections, JSON objects, CSV with header rows, etc.). C1–C5 apply when the source format is unstructured at the byte level (typically: PDFs without a structure-tree). For a given Document, exactly one of the two regimes applies, determined by the source format detected during P0/P1.

| ID | Rule |
|---|---|
| **C0 — Pre-existing structural clusters** *(applies when source format provides intrinsic structure)* | When the source format already delivers structural grouping (e.g. Excel header blocks, XML sections, JSON objects, CSV header rows), those structural groupings are taken **verbatim** as clusters with `Cluster_Type=Pre_Existing_Structural`. The geometric rules C1–C3 are **not** evaluated for such sources. The pre-existing structure is captured as: (a) `Cluster.Container_Object_ID` → the header/section-defining Object (e.g. the cell containing the block header `"Einspeisung 230VAC"`); (b) `Object_Cluster` membership → all Objects belonging to that structural block (e.g. all Excel cells in the row range under the header, up to the next block-header row); (c) `Cluster.Cluster_Type=Pre_Existing_Structural`; (d) `Object_Cluster.Membership_Reason=Pre_Existing_Structural`. Nested structures (e.g. an Excel block-header containing sub-block-headers) populate `Parent_Cluster_ID` analogously to C1's nested containment. |
| **C1 — Containment** *(applies only when source has no intrinsic structure; PDF)* | An Object A belongs to the cluster of a closed Graphic-Object G iff G is a closed path AND the centroid of A's bounding box lies inside G's bounding box. C1 evaluated before C2. **Nested containment:** the innermost G is the primary cluster; the chain is preserved via `Parent_Cluster_ID` in `Cluster`. |
| **C2 — Proximity** *(applies only when source has no intrinsic structure; PDF)* | **Non-normative heuristic.** Objects without C1 assignment are connected via nearest-neighbor distance. For each resulting cluster, compute mean nearest-neighbor distance d̄. Objects whose nearest-neighbor distance exceeds `2 · d̄` are separated and form singleton clusters. The factor 2 is a starting value, tool parameter, to be calibrated. **The specific algorithm is not mandated by this schema** — implementations MAY use other proximity-based clustering (DBSCAN, grid-based, etc.). What is mandated: for every `Cluster` row produced by a proximity-clustering pass, the `Cluster` sheet SHALL record `Cluster_Method` (algorithm identifier) and `Cluster_Parameter_Set` (serialized parameter dictionary) so that the clustering is **reproducible** from the workbook alone. Two implementations may produce different clusters and remain conformant, provided each declares its method and parameters. |
| **C3 — Topology** *(applies only when source has no intrinsic structure; PDF)* | Topology-Object candidates (per A5) are NOT assigned to spatial clusters. For each endpoint of a candidate, find the nearest **connection-point source object** in any cluster within a configurable distance threshold (default: 2 PDF points ≈ 0.7 mm; tool parameter, calibrate against authoring practice — endpoints in cleanly drawn PDFs typically land directly on connection point symbols). **A connection-point source object is formally defined as an `Object` row whose `Object_Role` field is set to `Connection_Point`** — this is a small filled circle or pin marker indicating a terminal connection point in the source drawing. The `Object_Role` field is an enum-validated classifier on the `Object` sheet (per §A.7 and §9.3) and accepts the values `Connection_Point`, `Label`, `Symbol`, `Border`, `Annotation`, `Topology` (for the topology candidates themselves). For sources where connection-point source objects are not explicitly drawn (e.g. simplified circuit diagrams without pin markers), C3 falls back to nearest-neighbor against any `Object_Type=Graphic` member of a cluster — `Topology_Validation_Status` is set to `Unresolved` until the endpoint is confirmed per the Match_Result workflow (tool-agnostic per §1.3: auto-resolved, tool/LLM-driven, or manual correction; mechanism recorded in `Match_Result.Reviewed_By`). Outcome stored on the Object: (a) `Topology_From_Object_ID`, `Topology_To_Object_ID` — the resolved endpoint references (null when no nearby connection point found); (b) `Topology_Validation_Status` — `Valid_Connection` (both endpoints resolved) or `Unresolved` (at least one endpoint not resolved). The classification of `Unresolved` candidates as decorative lines (separators, annotation lines, dimension lines) is not performed within the Excel; it is left to downstream consumers of the workbook. Decorative candidates therefore remain `Unresolved` in the Excel — they carry no signal information and are simply excluded from downstream Connection_Data consumption. |
| **C4 — Cluster identification** *(both regimes)* | Each cluster receives: unique `Cluster_ID`, encompassing BBox (in PDF coordinates for PDF sources; row/column range for Excel sources per §A.7), `Cluster_Type` (derivable from membership reasons: `Containment`, `Proximity`, `Topology` for PDF; `Pre_Existing_Structural` for Excel/XML/JSON/CSV), `Parent_Cluster_ID` (nullable, for nested containment/structure), `Container_Object_ID` (for `Containment` clusters: the enclosing Graphic-Object; for `Pre_Existing_Structural` clusters: the header-defining cell or section node). |
| **C5 — Cluster page-locality** *(both regimes)* | A Cluster contains only Objects from a single page/sheet (`Object.Page_Number` identical for all members; for Excel sources, `Page_Number` is the sheet index). Multi-page/multi-sheet documents produce per-page/per-sheet cluster sets. Cross-page semantic linking is an ontology-layer concern, not a schema-level concern. |

**Enum_Lookup additions required (K2 resolution):**
- `Cluster_Type`: add value `Pre_Existing_Structural` (in addition to `Containment`, `Proximity`, `Topology`)
- `Membership_Reason`: add value `Pre_Existing_Structural` (in addition to `Containment`, `Proximity`)

### 11.3 Match Rules (M)

| ID | Rule |
|---|---|
| **M1 — Primary RKZ match** | A Top-Down Element T and a from-Cluster Element C match iff the underlying cluster contains a Text-Object whose content contains T's `Primary_RKZ` as substring after whitespace normalization. |
| **M2 — Secondary spatial match** | If M1 yields no unique match: bounding box overlap > 50% AND identical `Element_Type`. |
| **M3 — Match classification** | `Matched` (unique pairing), `Only_TopDown` (T without cluster counterpart — requires resolution per §A.12 `Resolution_Status` workflow), `Only_Cluster` (C without TopDown — requires resolution per §A.12 `Resolution_Status` workflow). The resolution mechanism is tool-agnostic per §1.3 — auto-resolved by Match_Rule, tool/LLM-corrected, manually corrected, or rejected, with the chosen mechanism recorded in `Match_Result.Reviewed_By` (`Auto` for tool-driven resolution, otherwise an identifier of the resolving agent). |
| **M4 — Validation gate** | Validated `Element_ID` entries produced only after every `Match_Result` row has `Resolution_Status ≠ Open`. Classification, categorization, attribute interpretation only on validated list. |

### 11.4 Process Steps with Pre/Post-Conditions (P0–P9)

**Completeness contract (D3, D4, D5):** Every spec-compliant Excel SHALL be the result of executing all 10 process steps P0–P9 in sequence. Skipping a step (e.g. omitting P1 Object extraction or P3 Cluster formation as a "mini-build" shortcut) produces a workbook that is **not** spec-compliant — even if the I-rules are individually satisfied by the partial data, because the resulting workbook is not reproducible by an independent implementation. The only exception: when a P-step has an empty post-condition for a particular source (e.g. a Verschaltungsliste-only source has no `Cluster` rows because the structural-cluster pass per C0 finds no header blocks), the corresponding sheet is left empty with headers only — but the step was still executed and produced its (empty) result.

| Step | Pre-Condition | Action | Post-Condition |
|---|---|---|---|
| **P0** Document metadata population | PDF/Excel/VL source available; Schema_Metadata, Attribute_Lookup, Enum_Lookup seeded | Create `Document_ID` (assign identifier per §3.7), populate `Document_Data` with title-block attribute values per the relevant `Attribute_Lookup` entries (`Scope = Document`), populate `Revision_Data`, create initial `Document_RepresentedItem` row(s) per applicable S-rule (S1–S3). **Populate `Document_Data_Source` and `Revision_Data_Source` for every `Document_Data` and `Revision_Data` row produced** (per I12). **Clarification:** P0 SHALL create the minimum `Object` rows required to back the `Document_Data_Source` and `Revision_Data_Source` row references — typically one synthetic `Object` per title-block source unit (e.g. one for each title-block field extracted from a PDF, or one synthetic `Source_Operation=Manual_Entry` Object per manually entered metadata field). These P0-seeded Object rows are then **augmented and finalized by P1** (which performs the complete Object extraction over the full source). The I12 provenance link can therefore be satisfied at the end of P0, without violating P1's completeness contract — P1 starts from a partially populated `Object` sheet (containing P0's metadata-backing Objects) and adds all remaining source units. For manually entered metadata (no source extraction), the corresponding Source row references a synthetic `Object` of `Source_Operation = Manual_Entry` per the I12 manual-evidence convention. | `Document_ID` exists with valid `Schema_Version` and `Lookup_Version` from `Schema_Metadata`; `Document_Data` carries title-block attributes; `Document_RepresentedItem` has at least one row; `Document_Data_Source` and `Revision_Data_Source` cover every `Document_Data` and `Revision_Data` row (I12); `Object` sheet contains at least the metadata-backing Objects referenced by the Source rows just created. |
| **P1** Object extraction | P0 complete | Parse source completely; populate `Object` per A1–A5 (PDF source) or per the source-format conventions in §A.7 (Excel `Cell`, Verschaltungsliste `VL_Row`). **`Object` SHALL contain every atomic source unit** — every PDF text run, vector path, connection point-marker for PDF sources; every non-empty cell for Excel sources; every logical row for VL sources. A workbook with a stub or partial `Object` sheet is not spec-compliant. | All source content captured as Objects with valid `Object_Type`, content where applicable, and source-format-specific positional metadata per §A.7. Topology-Objects have endpoint references (or null pending C3). |
| **P2** Top-Down Element capture | P0 complete; `Document_RepresentedItem` populated for context | Identify the main elements of the source document by domain-knowledge-driven classification of source content against the symbol/function norms cited in §16.1 (IEC 60617, IEC 81346-2, IEC 62424). The classification mechanism is tool-agnostic and may be (a) LLM-based classification with RAG access to the §16.1 normative texts (typical tool architecture per §1.3); (b) deterministic rule-based parsing where the source format permits (Excel/Verschaltungsliste); (c) any combination thereof. The `Source` column on each `Elements_TopDown` row records which mechanism produced that row. Note: P2 and P1 may execute in parallel or in either order after P0; P5 requires both complete. | `Elements_TopDown` populated with at least one entry, or explicit empty-set acknowledgment |
| **P3** Cluster formation | P1 complete; all Objects have valid `Object_Type`; A5 applied | Apply the cluster regime per source format: **C0** for sources with intrinsic structure (Excel, XML, JSON, CSV); **C1, C2, C3, C4** for sources without intrinsic structure (PDF). Apply C5 (page-locality) in both regimes. | **Clarification:** For source formats with an applicable cluster regime (PDF via C1/C2/C3; Excel/XML/JSON/CSV via C0), every non-Topology Object SHALL appear in `Object_Cluster` at least once. For source formats where P3 legitimately produces an **empty cluster result** (e.g. a Verschaltungsliste-only source with no header blocks that meet C0's structural-cluster criteria, or any source where neither geometric containment nor pre-existing structure is recoverable), `Object_Cluster` MAY remain empty and the P3 post-condition is then "P3 was executed with an empty result". The empty result SHALL be documented via a `Document_Data` row with `Attribute_Name=Cluster_Method` and `Attribute_Value=P3_Empty_Result`. The `Cluster` sheet has one row per unique Cluster_ID, or zero rows when P3 produced an empty result. `Parent_Cluster_ID` forms a valid tree (no cycles) when populated. |
| **P4** Cluster → Element derivation | P3 complete | Derive candidate Element per cluster via RKZ-pattern matching and Element_Type inference against the `Attribute_Lookup` catalog and §9.3 Seed Catalog. The derivation mechanism is tool-agnostic per §1.3 (deterministic parser for structured sources, LLM/RAG-based inference for PDF sources, or combination thereof). When no element is derivable from a cluster, set `Derivation_Status = No_Element_Derivable`. | `Elements_from_Cluster` has one row per cluster, with `Derivation_Status` explicitly set |
| **P5** Matching | P2 AND P4 complete | Apply M1, M2, M3 | Every `Element_TopDown` and `Element_from_Cluster` (whose `Derivation_Status = Element_Derived`) appears in at least one `Match_Result` row. `Match_Status` is set per actual cluster-pass outcome — `Matched`, `Only_TopDown`, or `Only_Cluster`. `Only_TopDown` for every element is only the correct outcome when the cluster pass genuinely produced no clusters (e.g. empty source). |
| **P6** Discrepancy resolution | P5 complete | Resolve every `Only_TopDown` and `Only_Cluster` row produced by P5 to a terminal `Resolution_Status` value per §A.12. The resolution mechanism is tool-agnostic per §1.3 and may be (a) automatic by Match_Rule (`Resolved_AutoMatch`); (b) tool/LLM-driven correction; (c) manual correction by an operator; or (d) explicit rejection (`Rejected`). The chosen mechanism is recorded per row in `Match_Result.Reviewed_By` (`Auto` for tool-driven resolution, otherwise an identifier of the resolving agent) and `Match_Result.Resolution_Status`. | All `Match_Result` rows have `Resolution_Status ≠ Open` |
| **P7** Consolidation | P6 complete | Create one `Element_ID` per validated match per M4 | `Element_ID` populated; every entry has valid `Source_Match_ID` |
| **P8** Classification & attributes | P7 complete; `Attribute_Lookup` available | Populate `Element_Classification`, `Element_Data`, `Element_Data_Source`, `RepresentedItem_Data`, `RepresentedItem_Data_Source`, `Element_RepresentedItem_Mapping`; complete `Document_RepresentedItem`. **Populate `Element_Classification_Source` for every `Element_Classification` row** (per I12). For classifications derived by manual decision or rule, the Source row references a synthetic `Object` of `Source_Operation = Manual_Entry` per the I12 manual-evidence convention. | All required attributes per `Attribute_Lookup` populated; provenance recorded in all six `*_Source` sheets; every `Element_Classification` row has at least one `Element_Classification_Source` row (I12). |
| **P9** Topology resolution and connection population | P7 complete; Topology candidate Objects have `Topology_Validation_Status` set by C3 (PDF) or connections are listed in the source (Excel Klemmenplan, Verschaltungsliste) | Map Topology-Objects (PDF) or source connection rows (Excel/VL) to `Connection_ID` + `Connection_Data` + `Connection_Data_Source`. **Every `Connection_Data` row SHALL have a corresponding `Connection_Data_Source` row referencing the `Object` it was derived from** (per K3 provenance principle). | One `Connection_ID` row per resolved connection; `Connection_Data` rows per attribute per connection; `Connection_Data_Source` rows for provenance. |

### 11.5 Edge Case Rules (E)

| ID | Rule |
|---|---|
| **E1 — Composite symbols** | Multi-path symbols (e.g. transducer box + inner `E` + diagonal stroke) unified into one cluster via C1. Composition emerges from containment, no special-case rule. |
| **E2 — Shared labels** | Labels positioned between multiple objects are assigned via C2 to the cluster whose member-objects yield the smallest sum of nearest-neighbor distances. Tiebreak: cluster whose BBox most closely encloses label centroid. |
| **E3 — Cluster without RKZ** | Cluster with no RKZ text not eligible for M1; M2 takes over. |
| **E4 — Topology with free endpoint** | Topology-Object endpoint without nearby connection-point cluster (per C3 distance threshold): primary marker `Object.Topology_Validation_Status = Unresolved`. **Clarification:** a Connection_ID row SHALL NOT be created for unresolved endpoints — Connection_ID requires both `From_Element_ID` and `To_Element_ID`. Unresolved topology candidates remain solely in `Object` with `Topology_Validation_Status=Unresolved` and queue for resolution per the Match_Result workflow (tool-agnostic per §1.3). |
| **E5 — Unspecifiable failure mode** | When any field cannot be determined and has an enum type, set the value to the universal marker `Unspecifiable`. This marker is implicitly accepted for every enum-typed field; it does NOT need to be explicitly listed in `Enum_Lookup` for each `Field_Name`. The corresponding provenance row in the relevant `*_Source` sheet SHALL carry `Review_Status=Requires_Review`. If no `*_Source` row exists for the affected value, the workbook violates I12. |
| **E6 — Empty sheets are valid** | Sheets that do not apply to a given document (e.g. `Connection_Data` for a document without topology-objects; `Layer_ID` for documents without layer structuring) remain empty (headers and explanation rows only). Empty sheets are not an error condition. |

### 11.6 Convention Rules (K)

| ID | Convention |
|---|---|
| **K1 — Scope separation by sheet, not by value** | `RepresentedItem_Type` and `Element_Type` may carry identical string values but live in different sheets and denote different scopes (document-level vs. element-level). Sheet context determines meaning. Tools must not query for a value across both sheets without scope qualification. |
| **K2 — Cross-document RepresentedItem identity is best-effort** | The schema does not guarantee identity of `RepresentedItem_ID` or `Primary_RKZ` across documents. Fuzzy matching / alias resolution is responsibility of the downstream ontology layer. |
| **K3 — Single Source of Truth (SPoT)** | Each relationship has exactly one canonical location. Element ↔ RepresentedItem only in `Element_RepresentedItem_Mapping` (no FK in `Element_ID`); cluster membership only in `Object_Cluster`; cluster metadata only in `Cluster`; attribute provenance only in `*_Data_Source` sheets. Element-attributes only in `Element_Data`; RepresentedItem-attributes only in `RepresentedItem_Data` (no polymorphism). **Acknowledged controlled redundancy:** the `Position` field appears in `Document_Data` as the raw Schriftfeld entry AND as a component of `Document_RepresentedItem.Primary_RKZ` (where it is combined per S1). These are semantically distinct — the raw field vs. the derived normative identifier — and therefore not a SPoT violation. |
| **K4 — Enum disambiguation via Field_Name** | Two `Enum_Lookup` entries may carry the same `Allowed_Value` (e.g. `PCE-Aufgabe` exists for both `Field_Name = RepresentedItem_Type` and `Field_Name = Element_Type` — different scopes per K1). Tools must always qualify lookups by `Field_Name`, never query `Allowed_Value` alone. |



Cross-sheet referential and value validity rules. These must hold after the relevant process steps complete. A failed integrity check blocks downstream consumption until resolved.

### 11.7 Baseline Integrity Rules I1–I22

These rules apply to all document types unless otherwise constrained.

| ID | Rule |
|---|---|
| **I1** | Every `Element_ID.Source_Match_ID` must reference an existing `Match_Result.Match_ID`. |
| **I2** | Every `Match_Result` with `Match_Status = Matched` must have both `Element_TopDown_ID` and `Element_from_Cluster_ID` populated, and both must reference existing entries. |
| **I3** | Every `Match_Result` with `Match_Status = Only_TopDown` must have `Element_TopDown_ID` populated and `Element_from_Cluster_ID` null. |
| **I4** | Every `Match_Result` with `Match_Status = Only_Cluster` must have `Element_from_Cluster_ID` populated and `Element_TopDown_ID` null. |
| **I5** | Every `Object_Cluster.Cluster_ID` must reference an existing `Cluster.Cluster_ID`; every `Object_Cluster.Object_ID` must reference an existing `Object.Object_ID`. |
| **I6** | `Cluster.Parent_Cluster_ID` references must form a valid tree (no cycles, no orphans). A cluster may be a root (null parent) but cannot reference a non-existent parent. (Specific case of I16; retained for explicitness.) |
| **I7** | `Object.Topology_From_Object_ID` and `Topology_To_Object_ID` must reference existing `Object.Object_ID` entries whose `Object_Type ∈ {Text, Graphic}` (not `Topology`). |
| **I8** | `Connection_ID.From_Element_ID` and `To_Element_ID` must reference existing `Element_ID` entries with `CAEX_Type = ExternalInterface` (per CAEX connection-point convention in §5.13). |
| **I9** | `Element_RepresentedItem_Mapping.Element_ID` and `RepresentedItem_ID` must reference existing entries in their respective sheets. |
| **I10** | `Element_Data.Element_ID` must reference existing `Element_ID`. |
| **I11** | `RepresentedItem_Data.RepresentedItem_ID` must reference existing `Document_RepresentedItem.RepresentedItem_ID`. |
| **I12** | All `*_Source` sheets are FK-linked to their parent rows: `Element_Data_Source.Element_Data_ID → Element_Data.Element_Data_ID`; `RepresentedItem_Data_Source.RepresentedItem_Data_ID → RepresentedItem_Data.RepresentedItem_Data_ID`; `Connection_Data_Source.Connection_Data_ID → Connection_Data.Connection_Data_ID`; `Document_Data_Source.Document_Data_ID → Document_Data.Document_Data_ID`; `Revision_Data_Source.Revision_ID → Revision_Data.Revision_ID`; `Element_Classification_Source.Classification_ID → Element_Classification.Classification_ID`. Every `Document_Data`, `Element_Data`, `RepresentedItem_Data`, `Connection_Data`, `Revision_Data`, and `Element_Classification` row SHALL have at least one corresponding `*_Source` row (D6). **Source row content rule (manual-evidence convention):** a Source row's `Source_Object_ID` SHALL reference an existing `Object` when the data row was extracted from an actual source artifact. When the data row originates from a non-extracted decision (manual classification, rule-derived value, norm-derived value, project aggregation), the Source row SHALL still exist and SHALL declare its origin via the `Extraction_Method` field (`Manual_Entry`, `Rule_Based_Parser`, `LLM_Classification`, etc.) with `Source_Object_ID` referencing a synthetic `Object` row of `Source_Operation=Manual_Entry` carrying the rationale in `Content_Text`. This avoids null FKs and keeps every data row traceable to an addressable provenance artifact. |
| **I13** | `Attribute_Name` values in `Document_Data`, `Element_Data`, `RepresentedItem_Data`, and `Connection_Data` must exist in `Attribute_Lookup` with a matching `Scope` and (where applicable) `Type_Constraint` (per §9.4 Type_Constraint syntax). |
| **I14** | Every enum-typed value must exist in `Enum_Lookup` for the corresponding `Field_Name`, OR equal the literal string value `Unspecifiable` (the universal failure marker per E5, accepted for every enum-typed field without explicit Enum_Lookup entry). For `Field_Name=Element_Type`, values declared in `Schema_Metadata.Allowed_Element_Type_Extensions` are accepted in addition to the §9.3 catalog. The analogous extension mechanism applies to `RepresentedItem_Type` via `Schema_Metadata.Allowed_RepresentedItem_Type_Extensions`. **Project-Profile binding :** when `Schema_Metadata.Project_Lookup_Profile_ID` is populated with a non-empty value, the workbook declares membership in a named cross-workbook lookup profile. The profile master is an external project-side artifact (for example a controlled project profile file) and is not embedded as a mandatory workbook sheet. **Validator behavior for v0.8 is explicitly:** (a) **Workbook-level (Level-1) validators SHALL NOT fail a workbook** because `Project_Lookup_Profile_ID` is populated but the external profile master is absent — the profile is a governance hook, not a Level-1 validation gate. (b) **Aggregation-level validators MAY report a WARNING** when `Project_Lookup_Profile_ID` is set across workbooks and either no profile master is supplied, or the declared `Allowed_*_Extensions` in a workbook diverge from the master. When such a profile master is supplied to an aggregation-capable validator, the `Allowed_*_Extensions` CSV-list in each workbook SHALL be a subset of the profile's master extension list; divergence is then a Level-3 (aggregation) error. If no external profile master is supplied, the validator can still check consistency of declared `Allowed_*_Extensions` across workbooks with the same `Project_Lookup_Profile_ID`, but this remains a warning, not an error. When `Project_Lookup_Profile_ID` is empty, extensions are workbook-local. |
| **I15** | Every mandatory-sheet `Document_ID` foreign-key reference (in `Document_Data`, `Revision_Data`, `Document_RepresentedItem`, `Object`, `Cluster`, `Elements_TopDown`, `Elements_from_Cluster`, `Match_Result`, `Element_ID`, `Connection_ID`, `Element_Classification`, `Layer_ID`) must point to an existing `Document_ID` entry. When optional extension sheets are active, `Designation.Document_ID`, `Electrical_Node.Document_ID`, and `Cable_Data.Document_ID` must also point to an existing `Document_ID` entry; the remaining optional-sheet FKs are checked by I32. |
| **I16** | All hierarchical `Parent_*_ID` columns (`Cluster.Parent_Cluster_ID`, `Document_RepresentedItem.Parent_RepresentedItem_ID`, `Elements_TopDown.Parent_Element_TopDown_ID`, `Element_ID.Parent_Element_ID`) must form valid trees per document: no cycles, no orphan references, no self-references. Supersedes I6 (which is retained as the Cluster-specific case). |
| **I17** | `Cluster.Container_Object_ID` (when present) is validated per `Cluster_Type` : for `Cluster_Type = Containment`, `Container_Object_ID` SHALL reference an `Object` with `Object_Type = Graphic` AND `Geometry_Closed = true` (required by C1). For `Cluster_Type = Pre_Existing_Structural` (Excel, XML, JSON, CSV per C0), `Container_Object_ID` MAY reference a structure-defining `Object` of any `Object_Type` (typically `Text` for header cells or `Topology` for structural anchors). For `Cluster_Type = Proximity` (C2, C5), `Container_Object_ID` is null (no single container). |
| **I18** | `Elements_from_Cluster.Source_Cluster_ID` must reference an existing `Cluster.Cluster_ID`. |
| **I19** | When populated, `Match_Result.Element_TopDown_ID` and `Match_Result.Element_from_Cluster_ID` must reference existing entries in their respective sheets. (Population is conditional per I2–I4.) |
| **I20** | `Resolution_Status` must be consistent with `Match_Status`: `Matched` → `Resolved_AutoMatch` (set automatically by P5); `Only_TopDown` or `Only_Cluster` → `Open` initially, after P6 one of `Resolved_KeepBoth`, `Resolved_TopDown_Valid`, `Resolved_Cluster_Valid`. |
| **I21** | `Element_ID.Layer_ID` (when populated) must reference an existing `Layer_ID.Layer_ID`. |
| **I22** | For any `Element_ID`, at most one row in `Element_RepresentedItem_Mapping` may have `Relationship_Type = Primary`. Multiple `Shared` or `Secondary` rows are permitted. |

### 11.8 Validator Execution Order

This convention applies to all integrity rules (A1–A5, C1–C5, M1–M4, P0–P9, E1–E6, S1–S3, K1–K4, I1–I26 + I28–I32, AG1). It is a recommendation for validator implementations to produce deterministic, comprehensible error reports; the rules themselves are independent of execution order in their definitions.

Validators SHOULD evaluate rules in the following layered order. Within each layer, rule numbering provides the secondary order. A failure in an earlier layer typically renders later-layer checks meaningless on the affected row — validators MAY short-circuit further checks on a row after a layer-1 failure.

| Layer | Rule families | Purpose |
|---|---|---|
| 1 — **Structural** | A1–A5 (sheet existence, column presence, primary-key uniqueness, FK referential integrity), P0 (provenance baseline) | Validates that the workbook is structurally well-formed and that all FK references resolve. Until this layer passes, all higher-layer checks may produce spurious errors. |
| 2 — **Lookup / Enum** | I13 (Attribute_Lookup completeness), I14 (Enum_Lookup existence per Field_Name), I29 (Source_Format cardinality), K1–K4 (lookup-table conventions) | Validates that all enum and attribute references exist in the lookup tables. Required before any rule that interprets enum values. |
| 3 — **Object / Cluster / Match** | C1–C5 (cluster validity), M1–M4 (match resolution), S1–S3 (source-extraction-rule conformance) | Validates the object/cluster/match graph derived from sources. |
| 4 — **Element / Connection integrity** | I1–I12, I15–I22, I25 (Cable_Number, etc.), I30 (polymorphic classification FK), I31 (cable profile activation), I32 (optional extension sheet FKs) | Validates Element/Connection rows for content consistency. |
| 5 — **Document-type-specific integrity** | I23 (Terminal_Diagram bridges), I24 (wire color/polarity), I26 (Current_Path_Number), I28 (IEC 60617 classification completeness) | Document-type-bound rules; trigger only when Type_Constraint matches. |
| 6 — **Project-aggregation rules** | AG1 (Coil↔Contact cross-workbook) | Evaluated only at project level by an aggregator that combines all workbooks of a project; not part of Level-1 workbook conformance. |
| 7 — **Provenance completeness** | E1–E6 (error marker presence), P1–P9 | Final integrity layer; reports missing-evidence markers. |

**Rationale:** This layering ensures that a validator never reports e.g. "AG1 cross-workbook Coil-Contact failed" when the underlying problem is "I14 — `Element_Type=Coil` not in Enum_Lookup". The earlier layer catches the root cause; the later layer would otherwise produce a derivative error misleading the implementer.

**Implementation note:** Validators MAY parallelize within a layer but SHOULD NOT cross layers without ensuring the lower layer has fully passed first.

---

### 11.9 Document-Type-Specific and Global Integrity Rules I23–I26, I28–I30

Rules I23, I24, I26, and I28 are scoped via `Type_Constraint=Document_Type=...` and only trigger on the matching document types. I25 applies whenever the relevant cable grouping information is populated. I29 and I30 are global workbook-level rules. (Note: I27 was moved to §11.10 as `AG1`; the I-numbering retains the gap to keep historical references stable.)

#### I23 — Bridge / Terminal_Strip consistency

**Rule:** A connection is a bridge iff the connection has a `Connection_Data` row with the same `Connection_ID`, `Attribute_Name=Connection_Type`, and `Attribute_Value` starting with `Bridge_`. For such a connection, `Connection_ID.From_Element_ID` and `Connection_ID.To_Element_ID` SHALL both reference `Element_ID` rows with `Element_Type=Terminal`, and both terminal rows SHALL have the same `Parent_Element_ID` (= same Terminal_Strip).

**Rationale:** Bridges (cross-bridge, longitudinal bridge, pluggable bridge) are physically rigid connecting components within the same Terminal_Strip. A connection between terminals of different Terminal_Strips is by definition a wire, not a bridge (`Connection_Type=Wire`).

#### I24 — Wire-color / Polarity consistency (DIN EN 60446) [⚠ norm update see §16]

**Rule:** For a connection `C`, `Wire_Color`, `Polarity`, and `Voltage_Level` are resolved from Long-Form attribute rows, not from physical columns. `Wire_Color=X` means that `Connection_Data` contains a row with `Connection_ID=C`, `Attribute_Name=Wire_Color`, and `Attribute_Value=X`. `Polarity` and `Voltage_Level` are resolved analogously. If `Wire_Color=GNYE`, then `Polarity=PE` must hold. If `Wire_Color=BU` and the resolved voltage level is `230V_AC` or `400V_AC`, then `Polarity=N` must hold. Color codes are IEC 60757 codes registered in §9.3 Enum_Lookup.

**Voltage-level source priority:** the voltage level used by this rule SHALL be resolved in the following priority order:
1. `Connection_Data` row with `Attribute_Name=Voltage_Level` for connection `C`.
2. If absent, `Element_Data` rows with `Attribute_Name=Voltage_Level` for the connected endpoints; both endpoints must agree.
3. If absent, `Layer_ID.Voltage_Level` of the endpoint layers, provided both endpoints resolve to the same populated value.
4. If none of these values is available, the rule does not fire (silent abstention; no violation reported).

**Rationale:** DIN EN 60446 prescribes these colors mandatorily for protective and neutral conductors.

**Note:** The rule can be abstained from via `Unspecifiable` or by missing polarity. It is a conditional consistency check that applies only to populated values.

#### I25 — Cable grouping consistency

**Rule:** I25 operates in two modes depending on `Schema_Metadata.Cable_Modeling_Profile`.

**Core mode (`Cable_Modeling_Profile=Core`):** A connection belongs to cable group `K` iff it has a `Connection_Data` row with `Attribute_Name=Cable_Number` and `Attribute_Value=K`. Connections in the same cable group SHALL carry identical values for `Cable_Type` and `Shielding` where these attributes are populated. `Total_Wire_Count` SHALL be consistent when populated on more than one connection of the cable group.

**Asset mode (`Cable_Modeling_Profile=Asset`):** A connection belongs to a cable asset iff `Connection_ID.Cable_Data_ID` is populated. Populated `Cable_Data_ID` values SHALL reference existing `Cable_Data.Cable_Data_ID` rows. Cable-level attributes are authoritative on `Cable_Data`. **Clarification:** if a cable-level attribute (`Cable_Number`, `Cable_Type`, `Shielding`, `Total_Wire_Count`) is populated **both** on the `Cable_Data` row referenced by `Connection_ID.Cable_Data_ID` **and** on `Connection_Data` (Attribute_Name=that attribute, for the same Connection_ID) in Asset mode, the values SHALL match — divergence is a hard I25 violation. To avoid the ambiguity entirely, the recommended Asset-mode workbook practice is: cable-level attributes appear **only** on `Cable_Data` rows; only connection-specific attributes (Wire_Color, Polarity, Voltage_Level, Wire_Number) appear on `Connection_Data`. Validators MAY warn (rather than error) when both layers carry consistent values, but SHALL error when values diverge.

**Application:** In Core mode, the rule fires only when `Cable_Number` is populated. In Asset mode, FK consistency fires for every populated `Cable_Data_ID`. Missing cable grouping information means that no cable-level consistency relationship can be established.

**Rationale:** A physical cable has exactly one type, one shielding property, and a fixed wire count. The Core profile checks this through shared `Cable_Number` values; the Asset profile checks it structurally through `Cable_Data_ID`.

#### I31 — Cable profile activation consistency

**Rule:** The `Schema_Metadata` sheet SHALL contain exactly one row with `Metadata_Key=Cable_Modeling_Profile`. Its `Metadata_Value` SHALL be either `Core` or `Asset`. If the value is `Core`, `A.O3 Cable_Data` is absent and every `Connection_ID.Cable_Data_ID` cell SHALL be null. If the value is `Asset`, `A.O3 Cable_Data` SHALL be present, populated `Connection_ID.Cable_Data_ID` values SHALL reference existing `Cable_Data.Cable_Data_ID` rows, and unassigned connections MAY leave `Cable_Data_ID` null.

**Rationale:** `Connection_ID.Cable_Data_ID` is always present for header stability. I31 prevents the profile declaration from drifting away from the actual workbook content.

#### I32 — Optional extension sheet FK validity

**Rule:** When optional extension sheets are present, their FK columns SHALL resolve locally within the same workbook. `Designation.Document_ID`, `Electrical_Node.Document_ID`, and `Cable_Data.Document_ID` SHALL reference `Document_ID.Document_ID`. `Designation.Source_Object_ID`, `Electrical_Node.Source_Object_ID`, `Electrical_Node_Member.Source_Object_ID`, and `Cable_Data.Source_Object_ID`, when populated, SHALL reference `Object.Object_ID`. `Electrical_Node_Member.Electrical_Node_ID` SHALL reference `Electrical_Node.Electrical_Node_ID`; `Electrical_Node_Member.Element_ID` SHALL reference `Element_ID.Element_ID`. `Designation.Parent_Designation_ID`, when populated, SHALL reference another `Designation.Designation_ID` in the same workbook and SHALL NOT create cycles.

**Activation coupling:** if `A.O2 Electrical_Node` is present, `A.O2b Electrical_Node_Member` SHALL also be present. If `A.O2b Electrical_Node_Member` is present without `A.O2 Electrical_Node`, the workbook violates I32.

**Rationale:** Optional sheets do not change mandatory workbook conformance, but when a project activates them their relationships must be FK-valid and workbook-local.

---

**Circuit_Diagram-specific integrity rules** (apply only when `Document_Type=Circuit_Diagram`; baseline rules I1–I25 above continue to apply to all document types unchanged unless explicitly scoped otherwise):

#### I26 — Current_Path_Number consistency (Circuit_Diagram-specific)

**Rule:** For every `Element_ID` in a Document of `Document_Type=Circuit_Diagram`, the `Current_Path_Number` attribute (when populated) MUST be a positive integer or a source-native path identifier (e.g. `1.1`, `1a`, `2b` when the source uses sub-path numbering). The set of Current_Path_Numbers used in a single Document_ID is **expected** to be contiguous from 1 to N; non-contiguous numbering is permitted (real-world circuit diagrams have path-gaps from block-reservations, sheet-grids, or project-specific numbering schemes) and produces a **warning** rather than a violation. A warning is suppressed when (a) an `Object` row at the gap position carries `Content_Text` matching a reserved-path marker (e.g. `Reserve`, `Frei`, `Free`), or (b) `Document_Data` carries an `Attribute_Name = 'Path_Numbering_Grid'` row declaring the project-specific numbering scheme.

**Application:** Validators report non-contiguous numbering as a warning, not as a violation. For documents without populated Current_Path_Number (legacy or simplified circuit drawings), the rule does not fire.

#### I28 — IEC 60617 classification completeness (Circuit_Diagram-specific)

**Rule:** For every Element_ID in a Document of `Document_Type=Circuit_Diagram`, at least one `Element_Classification` row with `Classification_System ∈ {IEC 60617-2, IEC 60617-3, IEC 60617-6, IEC 60617-7, IEC 60617-8}` MUST exist, OR `Classification_Code=Unclassified` MUST be explicitly set with `Source_Symbol_Reference` populated.

**Rationale:** Symbol identity is core to a Circuit_Diagram; no Element_ID should remain symbol-anonymous unless explicitly so marked.

**Application:** When a Circuit_Diagram is sourced from a Verschaltungsliste alone (no graphical document), IEC 60617 classification may be unobtainable — `Unclassified` with provenance reference satisfies the rule. The IEC 81346-2 classification is independently mandatory per v0.4 conventions and is not weakened.

**Clarification (updated v0.8.3 for the `Connection_Point` Element_Type):** Element_IDs that exist solely as connection-point sub-Elements of a classified parent (i.e. `Element_Type=Connection_Point` rows — or, for workbooks built under v0.8/v0.8.2, `Element_Type=Terminal` rows carrying the same structural pattern — with non-null `Parent_Element_ID` and `CAEX_Type=ExternalInterface`, modeling the wire-attachment points of a parent device such as a Contactor or PLC_Module rather than a free-standing terminal block) are **exempt from I28** when their parent already carries an IEC 60617 classification. In other words: if a Coil sub-Element has parent K1 with `Element_Classification.Classification_System=IEC 60617-7` and `Classification_Code=07-15-01`, and that Coil is structurally a "wire-attachment connection-point" of K1 rather than an independently symbol-rendered element in the drawing, then the Coil sub-Element does not need its own IEC 60617 classification row to satisfy I28. The parent's symbol classification covers the sub-Element through the `Parent_Element_ID` link. **Discriminator:** an Element_ID is treated as a "connection-point sub-Element" for I28-exemption purposes if and only if (i) `Parent_Element_ID` is non-null, (ii) `CAEX_Type=ExternalInterface`, and (iii) `Element_Type=Connection_Point` (or, for pre-v0.8.3 workbooks retained for backward compatibility, `Element_Type=Terminal` used in this same generated-sub-element pattern — the CAEX-style connection-point modeling pattern per §5.13). The exemption applies only to generated connection-point rows, not to functional sub-elements such as `Coil`, `Main_Contact`, `Auxiliary_Contact`, or `Indicator_Lamp`; these remain subject to I28 because they carry their own distinct IEC 60617 symbols. A validator that cannot distinguish a v0.8.3 `Connection_Point` row from a genuine, individually-designated `Terminal` (§5.1) SHOULD prefer the `Connection_Point` reading only when `Element_Type=Connection_Point` is literally present; the `Terminal` fallback exists solely for pre-v0.8.3 artifacts and SHOULD NOT be relied upon for workbooks produced under v0.8.3 or later.


#### I29 — Source_Format cardinality and enum validity

**Rule:** Each workbook SHALL contain exactly one `Document_Data` row with `Attribute_Name=Source_Format`. Its `Attribute_Value` SHALL be enum-valid for `Field_Name=Source_Format`.

**Rationale:** `Source_Format` selects the source-object and cluster regime used by P1 and P3. Without exactly one valid value, source processing is not deterministic.

#### I30 — Polymorphic classification target validity

**Rule:** Every `Element_Classification` row SHALL reference a valid target according to `Classified_Object_Type`: `Element` references `Element_ID.Element_ID`; `RepresentedItem` references `Document_RepresentedItem.RepresentedItem_ID`; `Connection` references `Connection_ID.Connection_ID`; `Document` references `Document_ID.Document_ID`.

**Rationale:** `Element_Classification` keeps its historical sheet name for compatibility, but the row target is polymorphic. Target validity must therefore be checked against the sheet implied by `Classified_Object_Type`.

---

### 11.10 Aggregation Rules (AG) — Project-Level Cross-Workbook Integrity

Aggregation rules operate on a **project-container** holding multiple workbooks belonging to the same project. They are **not workbook-local**: a single workbook alone cannot violate or satisfy an AG rule. An aggregation-capable validator evaluates AG rules by ingesting all workbooks of a project and applying the rule across the combined Element_ID / Document_RepresentedItem / Connection_ID populations.

**Project membership definition (mandatory for AG evaluation):** A workbook belongs to project `P` if and only if it contains a `Document_Data` row with `Attribute_Name = 'Project_Name'` and `Attribute_Value` matching `P` after string normalization (trim outer whitespace, collapse internal whitespace, case-insensitive). Workbooks lacking a `Project_Name` row are project-singletons (no AG rules apply across workbook boundaries). `Project_Name` is the Long-Form `Attribute_Value` of this designated row — not a separate column.

**Conformance impact:** AG rules are **not part of Level 1 (Workbook Conformance)** per §1 — a workbook can be Level-1 conformant without any AG evaluation. AG evaluation is part of project-level audit (e.g. by a project aggregator combining all sheets of an HC10 plant package). A workbook MAY include the `Document_Data` row `Project_Name` even when no AG evaluator is present; the row is then informational.

**Project container completeness:** AG evaluation assumes that the aggregation tool has been supplied with the complete set of workbooks to be evaluated for a project. The recommended project-side artifact is an external manifest, not a mandatory workbook sheet. Such a manifest should list at minimum `Project_Name`, `Workbook_ID`, `Document_Filename`, `Document_Type`, optional `Document_Subtype`, and whether the workbook is included in AG evaluation. Without such a manifest, AG results are best-effort and may produce false positives when relevant project workbooks are missing.

#### AG1 — Coil↔Contact consistency (cross-workbook, Circuit_Diagram-derived; formerly I27)

**Rule:** Within a project `P`, for every Element_ID with `Element_Type=Coil` and Primary_RKZ prefix `X` (where prefix `X` is the part of Primary_RKZ before the `:` separator) in any workbook of `P`, at least one Element_ID with `Element_Type ∈ {Main_Contact, Auxiliary_Contact}` and Primary_RKZ prefix `X` MUST exist in any workbook of `P` (same workbook or another workbook of the same project). Conversely: for every Element_ID with `Element_Type ∈ {Main_Contact, Auxiliary_Contact}` and Primary_RKZ prefix `X`, an Element_ID with `Element_Type=Coil` and Primary_RKZ prefix `X` MUST exist in any workbook of `P`.

**Rationale:** A switching device without a coil or without contacts is physically impossible; source documentation across a project should not produce one without the other.

**Application:** AG1 is evaluated by combining all `Element_ID` rows of all workbooks in project `P` and applying the bidirectional existence check on `Primary_RKZ` prefix matches. False-positive suppression: an explicit `Cross_Project_Reference` row in `Document_Data` (`Attribute_Name = 'Cross_Project_Reference'`, `Attribute_Value` = the cross-referenced project name) declares that a Coil or Contact has its counterpart in a different project; the rule does not fire across this declared link.

**Clarification:** AG1 results are only valid when the complete project workbook set is loaded into the aggregator. Without a manifest declaring the expected workbook set of the project, an aggregator cannot distinguish "Coil-without-Contact" (a real finding) from "Coil-without-Contact in the workbooks I happen to have loaded" (a false positive due to incomplete loading). v0.8 does **not** introduce a mandatory manifest sheet inside workbooks (that would change the schema architecture). Instead: **an external project manifest is recommended** (a YAML/JSON/TOML file at project root listing the expected workbook filenames and their Document_IDs, plus the `Project_Lookup_Profile_ID` reference). When no such external manifest is supplied to the aggregator, AG1 findings SHALL be reported as **warnings**, not as conformance failures. When the external manifest is supplied and the loaded workbook set matches the manifest, AG1 findings SHALL be reported as **errors** (true conformance failures). The format of the external manifest is not specified by v0.8 and is left to project tooling; v1.0 may add a normative manifest schema.

**Clarification:** Even when a project consists of a single workbook (one Document_ID, no project siblings, manifest implicitly empty), AG1 **remains an aggregation-level rule** and is **not** part of Level-1 workbook conformance. In this degenerate case, AG1 may be evaluated against one workbook, and the bidirectional Coil↔Contact existence check then reduces to a workbook-local query; but the rule's classification stays Level-3 (aggregation). This explicit clarification prevents the misreading that "if there is only one workbook, AG1 becomes Level-1".

---

## 12. Worked Examples

The examples in §12 are explanatory excerpts, not authoritative workbook header definitions. Appendix §A remains the authoritative source for sheet headers and required columns. Where examples use compact notation, the corresponding full workbook representation SHALL still follow Appendix §A and the integrity rules in §11.

### 12.1 Instrument_Loop_Diagram — TU10.F17 (Flow loop) from the pumping station

A concrete example illustrating Instrument_Loop_Diagram modeling. The pumping-station sheet `TU10.F17` documents a flow indication and control loop (`Function=FIC`) for the secondary cooling water inlet of plant section TU10.

**Source content (verbatim from the Stellenplan title-block):**
```
Position field  : TU10.F17
Function     : FIC (Flow Indication and Control)
Loop description : Sekundär-Kühlwasser-Eintritt (Vorlauf)
Sheet number   : F17
Bearbeiter    : Y.ZHAO
```

**Resulting schema entries (excerpt — provenance and Object rows omitted for brevity):**

> **Compact notation for readability.** The block below uses inline `Field=Value` notation and omits some Appendix-required columns. Actual workbook rows SHALL follow Appendix §A and the integrity rules in §11. For a fully Appendix-conformant rendering of the same modeling pattern in tabular form, see §12.2.

```
Document_ID:
 D.1 | Document_Type=Instrument_Loop_Diagram | Document_Filename=TU10F17.pdf | Page_Count=1 | Schema_Version=v0.8 | Lookup_Version=v0.8.0

Document_Data:
 DD.1 | D.1 | Project_Name | Technikumsanlage
 DD.2 | D.1 | Source_Format | PDF_Drawing
 DD.3 | D.1 | Primary_RKZ | Technikumsanlage.Stellenplan.TU10.F17
 DD.4 | D.1 | Sheet_Number | F17
 DD.5 | D.1 | Bearbeiter | Y.ZHAO
 DD.6 | D.1 | Designation_Convention | IEC_81346_Conformant

Document_RepresentedItem (per S1, §4.1):
 D.1 | RI.1 | RepresentedItem_Type=PCE_Request | Primary_RKZ=TU10.F17.FIC

RepresentedItem_Data:
 RI.1 | Loop_Description="Sekundär-Kühlwasser-Eintritt (Vorlauf)"  (Object.Content_Text verbatim preserved)
 (Note: PCE_Category and PCE_Processing_Function are recorded as Element_Classification rows below,
  not as RepresentedItem_Data attributes — they are classifications per IEC 62424, not data attributes.
  Enum_Lookup entries for the IEC 62424 letter tables are not part of v0.8 and are planned for v0.9 per §15 Roadmap.)

Element_ID (loop devices):
 D.1 | E.1 | -B17_F | Element_Type=Sensor   (Flow sensor — vortex/coriolis/orifice; per DIN 19227-2)
 D.1 | E.2 | -B17_T | Element_Type=Transducer (Signal transducer: 4–20 mA output)
 D.1 | E.3 | -A1.AI3 | Element_Type=PLC_Module (PLC analog input channel 3 of module -A1)
 D.1 | E.4 | -Y17  | Element_Type=Valve_Actuator (Control valve actuator)

Element_Data (Long-Form rows per A.15 — exemplary for the PCE channel suffix on E.3):
 ED.1 | E.3 | PCE_Channel_Suffix | I
 ED.2 | E.4 | Signal_Standard | 4..20mA

Element_RepresentedItem_Mapping:
 E.1 | RI.1 | Relationship_Type=Primary  (the sensing element defines the loop)
 E.2 | RI.1 | Relationship_Type=Secondary
 E.3 | RI.1 | Relationship_Type=Secondary
 E.4 | RI.1 | Relationship_Type=Secondary

Element_Classification:
 EC.1 | D.1 | Element | E.1 | IEC 81346-2 | B          (B = Convert input variable into signal — Sensor)
 EC.2 | D.1 | Element | E.1 | IEC 62424  | F          (Flow per Table 2; v0.8 records as free-form until Enum_Lookup detail tables are added in v0.9)
 EC.3 | D.1 | Element | E.1 | DIN 19227-2 | FI         (Flow Indication — function letter combination)
 EC.4 | D.1 | RepresentedItem | RI.1 | IEC 62424 | FIC  (Loop-level: Flow Indication + Control — applied to RepresentedItem)
 EC.5 | D.1 | Element | E.2 | IEC 81346-2 | T          (Conversion of energy/signal — Transducer)
 EC.6 | D.1 | Element | E.3 | IEC 81346-2 | K          (Processing object — PLC module)
 EC.7 | D.1 | Element | E.4 | IEC 81346-2 | M          (M = Providing mechanical energy for driving; subclass MM "Driving by hydraulic or pneumatic means" — Valve_Actuator under the current v0.8 convention. The legacy designation `-Y17` from the source document is preserved verbatim in `Object.Content_Text` and `Element_ID.Primary_RKZ`; only the IEC 81346-2 schema classification is M.)

Connection_ID (signal flow within the loop):
 D.1 | C.1 | From=E.1.signal_out | To=E.2.signal_in  (sensor → transducer)
 D.1 | C.2 | From=E.2.signal_out | To=E.3.input    (transducer → PLC AI)
 D.1 | C.3 | From=E.3.output   | To=E.4.command_in (PLC AO → valve actuator)

Connection_Data (Long-Form rows per A.21):
 CD.1 | C.1 | Connection_Type | Wire
 CD.2 | C.1 | Wire_Color | Unspecifiable
 CD.3 | C.1 | Signal_Standard | 4..20mA
 CD.4 | C.2 | Connection_Type | Wire
 CD.5 | C.2 | Cable_Number | K10.S1
 CD.6 | C.2 | Signal_Standard | 4..20mA
 CD.7 | C.3 | Connection_Type | Wire
 CD.8 | C.3 | Cable_Number | K10.S2
 CD.9 | C.3 | Signal_Standard | 4..20mA
```

**Rule checks on the example:**

- **S1 (§4.1):** `Primary_RKZ=TU10.F17.FIC` correctly composed from Position + Function with `.` separator per IEC 81346.
- **I13 (§11.7):** All Attribute_Names (Project_Name, Loop_Description, Signal_Standard, …) exist in `Attribute_Lookup` with matching Scope and Type_Constraint.
- **I14 (§11.7):** All enum-validated values (Element_Type=Sensor/Transducer/PLC_Module/Valve_Actuator, Connection_Type=Wire, Wire_Color=Unspecifiable, …) exist in `Enum_Lookup`. IEC 62424 PCE_Category and PCE_Processing_Function values (F, FIC) are recorded in `Element_Classification.Classification_Code` as free-form strings — Enum_Lookup validation for IEC 62424 letter tables is not part of v0.8 and is planned for v0.9 (see §15 Roadmap); in v0.8 these classifications pass structural validation as `Element_Classification` rows, not enum validation as `Element_Data` values.
- **I22 (§11.7):** Exactly one `Element_RepresentedItem_Mapping` row per Element_ID has `Relationship_Type=Primary` (namely E.1 → RI.1). ✓
- **I8 (§11.7):** Connections from E.1/E.2/E.3/E.4 are via their connection-point sub-Element_IDs (signal_out, signal_in, etc.) with `Element_Type=Connection_Point` (v0.8.3 naming) and CAEX_Type=ExternalInterface (per §5.13 convention applied retroactively to all InternalElement types).
- **Multi-Classification (§8.1.1):** E.1 has 3 Element_Classification rows (IEC 81346-2, IEC 62424, DIN 19227-2) — cardinality 1:N satisfied. RI.1 has 1 Element_Classification row (IEC 62424 loop-level). ✓

**Cross-document linkage:** Where wire C.2 (cable K10.S1) terminates physically on a terminal strip in cabinet TU10, the corresponding `Element_ID` in a Klemmenplan document (e.g. `-X1:11` with Layer_ID `4.10-1` per layer schema §2.2.3) shares the same `Cable_Number` attribute → cross-document linkage by shared designation, not by FK.

### 12.2 Terminal_Diagram — Terminals X1:11/L3 and X1:12/L3 from HC10

A concrete example to illustrate the full modeling. Two consecutive terminals are shown that hang via longitudinal bridge on strand L3 — representative of the actual 5-bridge chain in the HC10 Terminal_Diagram (X1:11/12/13/14/15 all bridged to X1:3).

> **Reference Long-Form rendering.** This example renders `Document_Data`, `Element_Data`, and `Connection_Data` as Appendix-conformant Long-Form tables with the columns required by §A.6, §A.15, and §A.21 respectively. It is the canonical reference for how workbook rows should look. The compact-notation excerpts in §12.1 and §12.3 illustrate the same patterns in abbreviated form and SHALL be read against this tabular reference when implementing a generator.

**Source rows in the Terminal_Diagram (verbatim, original German — not translated):**
```
X1:11/L3 | rot | L3 gebrückt (X1:3) | rot  | Beckhoff 230VAC/24VDC
X1:12/L3 | rot | L3 gebrückt (X1:3) | rot  | – (frei)
```

**Resulting schema entries:**

`Document_ID` (mandatory A.3 fields not shown are omitted for brevity):

| Document_ID | Document_Type | Document_Filename | Page_Count | Schema_Version | Lookup_Version |
|---|---|---|---|---|---|
| D.1 | Terminal_Diagram | HC10_Klemmenplan_X1.pdf | 1 | v0.8 | v0.8.0 |

`Document_Data` (Long-Form rows; source rows omitted for brevity):

| Document_Data_ID | Document_ID | Attribute_Name | Attribute_Value |
|---|---|---|---|
| DD.1 | D.1 | Project_Name | HC10 |
| DD.2 | D.1 | Source_Format | PDF_Drawing |
| DD.3 | D.1 | Primary_RKZ | HC10.Klemmenplan.X1 |
| DD.4 | D.1 | Sheet_Number | X1 |

`Element_ID` (simplified):

| Element_ID | Element_Type | Primary_RKZ | Parent_Element_ID | CAEX_Type |
|---|---|---|---|---|
| E.1 | Control_Cabinet | HC10 | | InternalElement |
| E.2 | Terminal_Strip | -X1 | E.1 (=Control_Cabinet) | InternalElement |
| E.3 | Terminal | -X1:3/L3 | E.2 | ExternalInterface |
| E.11 | Terminal | -X1:11/L3 | E.2 | ExternalInterface |
| E.12 | Terminal | -X1:12/L3 | E.2 | ExternalInterface |
| E.50 | Power_Supply | (HC10 Beckhoff power supply) | E.1 | InternalElement |

`Element_Data` (for E.11, exemplary):

| Element_Data_ID | Attribute_Name | Attribute_Value |
|---|---|---|
| ED.20 | Terminal_Number | 11 |
| ED.21 | Terminal_Strip_Designation | -X1 |
| ED.22 | Polarity | L3 |

`Connection_ID`:

| Connection_ID | From | To | Source_Topology_Object_ID | Status |
|---|---|---|---|---|
| C.20 | E.3 (X1:3/L3) | E.11 (X1:11/L3) | O.140 | Resolved |
| C.21 | E.3 (X1:3/L3) | E.12 (X1:12/L3) | O.141 | Resolved |
| C.22 | E.11 (X1:11/L3) | E.50 (Beckhoff power-supply L terminal) | O.142 | Resolved |

`Connection_Data` (for the three connections):

| Connection_Data_ID | Connection_ID | Attribute_Name | Attribute_Value |
|---|---|---|---|
| CD.40 | C.20 | Connection_Type | Bridge_Longitudinal |
| CD.41 | C.20 | Polarity | L3 |
| CD.42 | C.21 | Connection_Type | Bridge_Longitudinal |
| CD.43 | C.21 | Polarity | L3 |
| CD.44 | C.22 | Connection_Type | Wire |
| CD.45 | C.22 | Wire_Color | RD |
| CD.46 | C.22 | Polarity | L3 |

`Connection_Data_Source` (provenance — source text preserved verbatim in original German):

| Connection_Data_ID | Source_Object_ID | Source_Role |
|---|---|---|
| CD.40 | O.80 (text "L3 gebrückt (X1:3)" in source cell column 3, row X1:11) | Label |
| CD.42 | O.82 (text "L3 gebrückt (X1:3)" in source cell column 3, row X1:12) | Label |
| CD.45 | O.84 (text "rot" in source cell column 4, row X1:11) | Value |

`Element_Classification`:

| Classification_ID | Document_ID | Classified_Object_Type | Classified_Object_ID | Classification_System | Classification_Code | Classification_Description | Source_Symbol_Reference |
|---|---|---|---|---|---|---|---|
| EC.1 | D.1 | Element | E.11 | IEC 81346-2 | X | Connecting objects | |
| EC.2 | D.1 | Element | E.11 | IEC 60617-3 | 03-02-02 | Anschluß (z.B. Klemme) | |
| EC.3 | D.1 | Element | E.50 | IEC 81346-2 | T | Conversion of energy | |
| EC.4 | D.1 | Element | E.50 | IEC 60617-6 | Unclassified | Power supply symbol not yet anchored against the available project norm PDF | Netzteil 230V_AC / 24V_DC; Schaltzeichen-Code-Verifizierung gegen DIN EN 60617-6:1997-08 ausstehend |

`Match_Result`: for E.11 / E.12, typically Matched, since terminals are both TopDown-identifiable (domain knowledge) and cluster-derivable (Excel row).

**Rule checks on the example:**

- **I23 for C.20:** From E.3 has Parent_Element_ID = E.2 (-X1), To E.11 has Parent_Element_ID = E.2 (-X1). Identical → I23 satisfied. ✓
- **I23 for C.21:** Analogous. ✓
- **I23 for C.22:** Connection_Type = Wire → I23 does not fire (only for Bridge types). ✓
- **I24 for C.22:** Wire_Color=RD (source word "rot"), Polarity=L3 → RD/red has no norm polarity binding (red is freely choosable per the cited wire-color standard). Passes. ✓
- **I25 for C.20/021/022:** No Cable_Number set → rule does not fire. ✓

### 12.3 Circuit_Diagram — Contactor -K1 (stirrer) coil + main contacts from HC10

A concrete example to illustrate Circuit_Diagram modeling. Contactor `-K1_stirrer_N12` is shown as it spatially appears in the Stromlaufplan: the coil (at terminals A1/A2) is drawn on current path 5 of the Secondary circuit (control voltage 24VDC); its three main contacts (terminals 1/2, 3/4, 5/6) are drawn on current path 2 of the Primary circuit (400V 3-phase power); one auxiliary contact (terminals 13/14) is drawn on current path 7 of the Secondary circuit for self-holding logic.

**Source content (verbatim from the Stromlaufplan sheets):**
```
Sheet "Primärstromkreis HC10", Path 2:
 -K1:1/2   L1 → motor terminal U
 -K1:3/4   L2 → motor terminal V
 -K1:5/6   L3 → motor terminal W
 Source label: "Schütz stirrer N12"

Sheet "Sekundärstromkreis HC10", Path 5:
 -K1:A1/A2  coil 24VDC, fed from F10 (fuse)

Sheet "Sekundärstromkreis HC10", Path 7:
 -K1:13/14  auxiliary contact, NO, used in self-holding line
```

**Resulting project-aggregation view (excerpt — provenance and Object rows omitted for brevity):**

> **Compact notation for readability:** same convention as the note in §12.1 applies; see there. For a fully Appendix-conformant tabular rendering, see §12.2.

```
Workbook A — HC10_Stromlaufplan_Primary.xlsx:
Document_ID:
 D.1 | Document_Type=Circuit_Diagram | Document_Filename=HC10_Stromlaufplan_Primary.pdf | Page_Count=1 | Schema_Version=v0.8 | Lookup_Version=v0.8.0

Document_Data:
 DD.1 | D.1 | Project_Name | HC10
 DD.2 | D.1 | Source_Format | PDF_Drawing
 DD.3 | D.1 | Document_Subtype | Primary
 DD.4 | D.1 | Primary_RKZ | HC10.Stromlaufplan_Primär
 DD.5 | D.1 | Sheet_Number | 1
 DD.6 | D.1 | Bearbeiter | Y.ZHAO
 DD.7 | D.1 | Designation_Convention | Legacy_DIN19227

Element_ID (local Document_ID, Element_ID, Primary_RKZ, Element_Type):
 D.1 | E.110 | -K1:1/2   | Main_Contact
 D.1 | E.111 | -K1:3/4   | Main_Contact
 D.1 | E.112 | -K1:5/6   | Main_Contact

Workbook B — HC10_Stromlaufplan_Secondary.xlsx:
Document_ID:
 D.1 | Document_Type=Circuit_Diagram | Document_Filename=HC10_Stromlaufplan_Secondary.pdf | Page_Count=1 | Schema_Version=v0.8 | Lookup_Version=v0.8.0

Document_Data:
 DD.1 | D.1 | Project_Name | HC10
 DD.2 | D.1 | Source_Format | PDF_Drawing
 DD.3 | D.1 | Document_Subtype | Secondary
 DD.4 | D.1 | Primary_RKZ | HC10.Stromlaufplan_Sekundär
 DD.5 | D.1 | Sheet_Number | 2
 DD.6 | D.1 | Bearbeiter | Y.ZHAO
 DD.7 | D.1 | Designation_Convention | Legacy_DIN19227

Element_ID (local Document_ID, Element_ID, Primary_RKZ, Element_Type):
 D.1 | E.100 | -K1:A1/A2  | Coil
 D.1 | E.120 | -K1:13/14  | Auxiliary_Contact
 (each Element_ID is InternalElement; their connection-point sub-Elements
  E.100.t1 / E.100.t2 / E.110.t1 / E.110.t2 / … are Element_Type=Connection_Point,
  CAEX_Type=ExternalInterface; per §5.13 convention, v0.8.3 naming)

Element_Data (Long-Form rows per A.15):
 ED.1 | E.100 | Current_Path_Number | 5
 ED.2 | E.100 | Coil_Voltage | 24VDC
 ED.3 | E.110 | Current_Path_Number | 2
 ED.4 | E.110 | Contact_Designation | 1/2
 ED.5 | E.111 | Current_Path_Number | 2
 ED.6 | E.111 | Contact_Designation | 3/4
 ED.7 | E.112 | Current_Path_Number | 2
 ED.8 | E.112 | Contact_Designation | 5/6
 ED.9 | E.120 | Current_Path_Number | 7
 ED.10 | E.120 | Contact_Designation | 13/14

Element_Classification (Classification_ID, Document_ID, Classified_Object_Type, Classified_Object_ID, Classification_System, Classification_Code):
 EC.1 | D.1 | Element | E.100 | IEC 81346-2 | Q
 EC.2 | D.1 | Element | E.100 | IEC 60617-7 | 07-15-01      (Norm wording: "elektromechanischer Antrieb, allgemein")
 EC.3 | D.1 | Element | E.110 | IEC 81346-2 | Q
 EC.4 | D.1 | Element | E.110 | IEC 60617-7 | 07-13-02      (Norm wording: "Leistungskontakt eines Schütz")
 EC.5 | D.1 | Element | E.111 | IEC 81346-2 | Q
 EC.6 | D.1 | Element | E.111 | IEC 60617-7 | 07-13-02
 EC.7 | D.1 | Element | E.112 | IEC 81346-2 | Q
 EC.8 | D.1 | Element | E.112 | IEC 60617-7 | 07-13-02
 EC.9 | D.1 | Element | E.120 | IEC 81346-2 | Q
 EC.10 | D.1 | Element | E.120 | IEC 60617-7 | 07-02-01      (Norm wording: "Schließer" — NO contact)
```

**Cross-reference resolution (S3.3 + AG1):** All five Element_IDs have Primary_RKZ matching the prefix `-K1:`. A project-aggregation query over the Primary and Secondary workbooks returns the complete contactor — coil and all four contacts — across the two local workbooks. The aggregate Contactor itself does not exist as an Element_ID within either Circuit_Diagram document; it would exist only in a Terminal_Diagram (with `Element_Type=Contactor`, `Primary_RKZ=-K1`, Main_Contact_Count=3, Aux_Contact_NO_Count=1).

**Rule checks on the example:**

- **I26 (Current_Path_Number consistency, per workbook):** The Primary workbook uses path 2; the Secondary workbook uses paths 5 and 7 (gap at 6). Validator flags gap at path 6 unless an `Object` row at path 6 carries `Content_Text="Reserve"` or similar. Resolution: source documentation is checked, and if the gap is justified, no error; otherwise I26 fires.
- **AG1 (Coil↔Contact, cross-workbook, project HC10):** E.100 (Coil with prefix `-K1:`) has corresponding contact Element_IDs E.110/E.111/E.112/E.120 with prefix `-K1:` in the same project (Project_Name=HC10). Both directions satisfied. ✓
- **I28 (IEC 60617 classification completeness):** All five Element_IDs carry IEC 60617-7 classification rows with verified item codes. ✓
- **CAEX consistency:** Each Element_ID is InternalElement; `Connection_Point` sub-Element_IDs (v0.8.3 naming; `Terminal` in pre-v0.8.3 workbooks) exist for every used terminal (A1, A2, 1, 2, 3, 4, 5, 6, 13, 14). Wire Connections reference the `Connection_Point` sub-Element_IDs, not the parent Coil/Contact. ✓
- **Designation_Convention=Legacy_DIN19227:** confirms that the prefix letter `-K` is interpreted as a contactor (Q-class) by domain knowledge, even though IEC 81346-2-conformant practice would prescribe `-Q1`. Validators checking strict IEC 81346 prefix-class matching are informed by this attribute to suppress false-positives.

---

## 13. Version History

| Version | Date | Summary |
|---|---|---|
| v0.4 | 2026-05-24 | Initial `Instrument_Loop_Diagram` baseline with 23 mandatory sheets, rules A1–I22, and lookup version v0.4.0. |
| v0.5 | 2026-05-29 | Added `Terminal_Diagram` support, connection modeling, rules I23–I25, English schema values, and unified enum-encoding conventions. |
| v0.5.1 | 2026-05-29 | Added `Circuit_Diagram` support through additional values and rules, including `Document_Subtype`, circuit sub-element types, S3 extraction logic, and rules I26–I28. |
| v0.6 | 2026-05-29 | Consolidated v0.4, v0.5, and v0.5.1 into one standalone specification with the 28 mandatory-sheet model, closed provenance structure, and harmonized Appendix numbering. |
| v0.7 | 2026-05-29 | Added semantic-completeness features: aggregation-rule class, optional node/cable extensions, value-normalization fields, project lookup-profile metadata, review metadata, and the three-level conformance model. |
| v0.8 | 2026-05-29 | Established the schema-stability and interoperability baseline: Appendix-only header authority, Long-Form validation, mandatory `Source_Format`, stable cable-profile headers, manual-evidence objects, polymorphic classification FK validation, optional-extension FK validation, and an authoritative `Enum_Lookup` seed catalog. Norm-dependent anchors that are not yet available remain marked as open tasks in §16. |
| v0.8.2 | 2026-07-17 | Structure patch of v0.8.1: content-neutral reorganization only — table of contents added; historical subsections §3.5, §3.6, the sheet-count and `PDF_Operation` rename notes, and §17 relocated verbatim to Appendix B with original numbering retained; §3.8 heading level corrected; duplicate compact-notation note in §12 replaced by a reference. No rule, value, sheet, or process content changed. |
| v0.8.3 | 2026-07-29 | **Content patch**, driven by findings from building and checking three real Instrument_Loop_Diagram / Terminal_Diagram / Circuit_Diagram workbooks end to end (Instrument_Loop_Diagram from the pumping station; Terminal_Diagram and Circuit_Diagram from plant HC10). Each item below is scoped strictly to single-document extraction; none touches cross-document interpretation or aggregation (§1.1 Principle 6, `K2` remain unchanged). Itemized changes: (1) **New canonical `Element_Type=Connection_Point`** (§5.13, §9.1, §9.3): generated CAEX connection-point sub-elements on non-Terminal-Strip devices (Coil, Main_Contact, Motor, Fuse, Power_Supply, etc., per the §5.13 convention) are now typed `Connection_Point` instead of reusing `Terminal`. `Element_Type=Terminal` is reserved for terminals that are themselves distinct, individually-designated objects in the source (§5.1) — i.e. real terminal-strip terminals. This closes a structural gap: v0.8/v0.8.2 required every `Terminal`-typed row to carry `Terminal_Number`/`Terminal_Strip_Designation` (§9.2), which a generated pass-through connection point never had in the source, producing spurious required-attribute failures. `Connection_Point` carries no mandatory attributes. The `I28` exemption clause (§11.9) is updated accordingly; workbooks built under v0.8/v0.8.2 that used `Element_Type=Terminal` for this purpose remain readable (see §11.9 I28 note) but SHOULD be regenerated as `Connection_Point` under v0.8.3. (2) **`SemanticID` normative definition** (new §3.9): the `SemanticID` column present on every mandatory sheet since v0.4 was never defined in prose. §3.9 now defines it as an optional, tool- or project-assigned key for marking that two or more rows refer to the same real-world entity or fact (e.g. two `Element_ID` rows with different source-verbatim `Primary_RKZ` text that a human or tool judges to be the same physical device), without altering the row's own natural key, `Primary_RKZ`, or `Content_Text` (Principle 4 unaffected — `SemanticID` is an additional, non-authoritative consolidation hint, not a replacement identity). Not validated by any I-rule; purely additive. (3) **S2 bulk/range terminal notation** (new §4.2.3): a source-native rule for terminal strips that bulk-label several physical terminals as one range (e.g. `X3.1 - X3.4`) instead of enumerating them individually, with a documented cross-reference resolution convention for later single-terminal references into that range. (4) **S3.1 grid-observation clarification** (§4.3.1): clarifies that "as observed from the source grid, never computed from raw coordinates" permits determining `Current_Path_Number` by nearest printed grid-column header when no per-element grid annotation exists — otherwise the rule was not applicable to sheets where the grid header is printed only once at the sheet border. (5) **`Cross_Reference_*` extended to Instrument_Loop_Diagram** (§4.3.3, §9.2): the annotated-open-wire-end convention is not unique to Circuit_Diagram; the `Type_Constraint` for this attribute family now reads `Document_Type ∈ {Circuit_Diagram, Instrument_Loop_Diagram}`. (6) **Wire_Color sourcing clarification** (§8.3): `Wire_Color` SHALL be populated only from an explicit textual colour designation in the source, never inferred from a CAD drawing's line/layer stroke colour, unless the source document itself defines its stroke-colour convention as a wire-colour legend. (7) **Eight missing §9.2 `Attribute_Lookup` blocks added**: `Auxiliary_Contactor`, `Motor`, `Valve_Actuator`, `Sensor`, `Transducer`, `PLC_Module`, `Cabinet_Aggregate`, and `Control_Cabinet` (as `Element`) now have their own catalog blocks; §5.4 already described `Auxiliary_Contactor` as attribute-identical to `Contactor` but §9.2 never materialized this. All eight are optional-only (no new mandatory attributes introduced). **(8) `Required=TRUE` conformance-severity clarified** (§9.2, patch added after first real-workbook check run against this same version): a `Required=TRUE` `Attribute_Lookup` row unpopulated in a specific workbook is a source-content completeness finding, not a Level-1 artifact-conformance defect — Principle 4 forbids inventing a value to close it. A validator SHALL report it as a non-blocking finding rather than a conformance failure; P8's "populated" post-condition (§11.4) is satisfied by a good-faith, non-fabricated extraction attempt. **(9) `Rated_Current` (`Fuse`, `Circuit_Breaker`) and `Input_Voltage`/`Output_Voltage` (`Power_Supply`) Document_Type-scoped** (§9.2, same patch): confirmed against the HC10 Stromlaufplan source that a pure Circuit_Diagram wiring schematic structurally never carries this nameplate/rating data (no field, table, or legend anywhere on the sheet), while the HC10 Klemmenplan source has a dedicated ratings table (e.g. "Sicherung/Nennstrom") confirming the attribute is typical for Terminal_Diagram. The `Attribute_Lookup` catalog now scopes these four attributes `Required=TRUE` to `Document_Type=Terminal_Diagram` only, with a companion `Required=False` row for `Document_Type=Circuit_Diagram` — this is item (9)'s worked instance of the item (8) severity policy combined with a catalog correction where an attribute is structurally atypical for an entire document family, not merely absent from one instance. |

Detailed migration notes for pre-v0.8 cleanup decisions are intentionally kept outside this release-facing history. The table above records only release-relevant changes.

---

## 14. Known Limitations

1. **Cable inventory** can now be modeled as an asset via the optional `A.O3 Cable_Data` sheet (`Cable_Modeling_Profile=Asset`). For projects on the default `Core` profile, cables remain modeled through `Connection_Data.Cable_Number` only — full cable-as-asset modeling requires switching to the Asset profile.
2. **Multi-conductor wires** with different functions in one cable are modeled as multiple `Connection_ID` rows. Physical sheathing is retained via shared `Cable_Number` (Core profile) or via shared `Connection_ID.Cable_Data_ID` (Asset profile).
3. **Semi-graphical Terminal_Diagram representations** can be covered by the Object-Cluster logic, but Terminal_Strip header detection can be impeded by graphical elements.
4. **Cabinet hierarchies** are modelable via `Parent_Element_ID` / `Parent_RepresentedItem_ID`, but detection from the source document is generally not deterministic from drawing geometry alone and requires domain-knowledge-driven curation (LLM-based, rule-based, or manual; see P2).
5. **Ring or star wiring** at a terminal is now modelable via the optional `A.O2 Electrical_Node` + `A.O2b Electrical_Node_Member` sheets. For projects without these optional sheets, the legacy workaround (multiple `Connection_ID` rows with identical `Source_Topology_Object_ID`) remains available.
6. **Cross-document designation linkage** uses Core-Minimum normalization (§3.8) at the prefix level. Full aspect-decomposition per IEC 81346-1 (function vs. location vs. product) is available via the optional `A.O1 Designation` sheet — recommended for projects with mixed legacy and IEC-81346-conformant designation schemes.
7. **Provenance closure** for `Document_Data`, `Revision_Data`, and `Element_Classification` is part of the 28-mandatory-sheet structure. Manual decisions without source extraction are represented through Source rows that reference a manual-entry `Object` (Source_Operation=Manual_Entry) per the I12 manual-evidence convention.
8. **`Element_Type=Cable`** is not an active canonical value in v0.8. Workbooks should not instantiate `Element_Type=Cable` rows. Element-level cable modeling (with sub-elements per strand) is reserved for a future revision.
9. **`Element_Classification` sheet name** is retained for backward compatibility despite the polymorphic content (now classifying RepresentedItem, Connection, and Document rows as well). A rename to `Classification` is evaluated for v1.0 with deprecated-alias migration.
10. **AG-rule evaluation** requires a project-aggregation context (multiple workbooks of the same project sharing a `Project_Name` Document_Data attribute). Workbook-level conformance (Level 1) does not require AG evaluation.

## 15. Roadmap

| Version | Planned content |
|---|---|
| v0.7 | Semantic completeness pass; AG rule class; model updates; 28 mandatory + up to 4 optional sheets (A.O1, A.O2, A.O2b, A.O3); Core-Minimum designation normalization mandatory; three-level conformance distinction |
| v0.8 (current) | Schema-stability and interoperability baseline: header authority, Long-Form rules, Source_Format cardinality, cable profile header stability, source evidence semantics, global classification FK validation, cable-profile activation validation, optional extension FK validation, and review/provenance alignment. **Norm-anchoring patch:** Valve_Actuator IEC 81346-2 reclassified from Y (Ed. 2 reserved) to **M** (subclass MM "fluid drive") per Table 1 + Table 2 Ed. 2 verification; Auxiliary_Contactor IEC 81346-2 reclassified from Q to **K** (subclass KF "Processing electrical signals") per Table 1 "Contactor relay" example, with Function_Scope=Power override for load-switching cases; IEC 60617-6 placeholder `06-04-xx` for Power_Supply replaced by explicit `Unclassified` + `Source_Symbol_Reference` per §A.19 fallback convention; IEC 62424 explicitly declared **syntax-only** for v0.8 — Detail-Tables 2/3/5 integration deferred to v0.9. |
| v0.9 (planned) | IEC 62424 detail tables in Enum_Lookup; AG2 aggregate-class consistency if required; P&ID extension candidate; Composite_Device evaluation only if explicit aggregate grouping is required in practice. |
| v1.0 | First release; all `[OPEN]` §16 entries resolved (including DIN EN 81346-2:2019 PDF for #19, IEC 60529, IEC 60898-1, IEC 60269, IEC 60947-4-1, IEC 60755 alternative, DIN VDE 0100-200/0281/0293-308, DIN EN IEC 60445); CAEX path validation against external library; provenance-completeness I-rule; **norm updates from §16 fully implemented**; evaluation of `Element_Classification` → `Classification` rename with deprecated-alias migration path |

---

## 16. Normative Updates for Full Release

This section separates the normative references currently used in v0.8 from open norm-update tasks for the full release (v1.0). Some currently used norm editions are transitional because newer editions were not available at the time of v0.8 creation.

**Background:** The schema specification requires norm anchoring of structural and classification decisions. v0.8 uses the norms available in the project library as a transitional solution where current editions were not accessible. Entries marked `[OPEN]` remain update tasks for v1.0.

### 16.1 Normative references and update status

Each entry carries an explicit status tag:
- **[OPEN]** — update required before v1.0
- **[VERIFIED]** — current edition confirmed available and in scope; no further action
- **[CLOSED]** — entry resolved by removal or correction within v0.8

| # | Currently cited in v0.8 | Status | Target norm for full release | Affected spec locations |
|---|---|---|---|---|
| 1 | DIN EN 60446 | **[OPEN]** withdrawn 2010; successor identified but not in project library | **DIN EN IEC 60445:2018-02** (Identification of terminals and conductors) | §2.2, §6.4, §8.3, §11 I24 |
| 2 | IEC 60757 / DIN EN 60757 | **[OPEN]** DIN EN 60757 withdrawn 2008; code system persists in successor norms | **HD 308 S2:2001 / DIN VDE 0293-308:2003-01** (Identification of cores in cables). **Note:** the IEC 60757 two-letter color-code system (RD, BU, GNYE, …) is **actively used in v0.8** as the `Wire_Color` encoding (see §0.1, §8.3, §9.3). The code system itself persists in HD 308 S2 / DIN VDE 0293-308; only the standalone DIN EN 60757 document is withdrawn. For v1.0, re-anchor the `Normative_Reference` of Wire_Color codes to HD 308 S2 / DIN VDE 0293-308 while keeping the identical code letters | §0.1, §6.4, §8.3, §9.3 |
| 3 | "per IEC 60529" (IP-protection reference without concrete list) | **[OPEN]** not in project library | **IEC 60529:2014** (Degrees of protection by enclosures, IP code) — full IP-value list IP00–IP69K to be adopted | §9.1 IP_Protection enum |
| 4 | "per IEC 60898-1" (MCB trip characteristic) | **[OPEN]** not in project library | **IEC 60898-1:2015** + **DIN EN 60898-1:2019** | §9.1 Trip_Characteristic B/C/D |
| 5 | "per IEC 60269" (melting-fuse trip characteristic) | **[OPEN]** not in project library | **IEC 60269-1:2014** + **DIN EN 60269-1:2014** | §9.1 Trip_Characteristic gG/gL/aM |
| 6 | "per IEC 60947-4-1" (contactor utilization category) | **[OPEN]** not in project library | **IEC 60947-4-1:2018** | §5.3, §9.1 Utilization_Category |
| 7 | "per IEC 60755" (FI residual-current types) | **[OPEN]** status uncertain — possibly withdrawn or not separately available | **Primary candidate:** IEC TR 60755:2017. **Fallback if 60755 not retrievable:** the residual-current types A / AC / F / B / B+ are equivalently established in **IEC 61008-1:2012** (RCCB) and **IEC 61009-1:2013** (RCBO) which are widely available. For v1.0, anchor on whichever of {60755, 61008/61009} is verified accessible | §5.6, §9.1 Residual_Current_Type |
| 8 | DIN VDE 0100-200 | **[OPEN]** date in v0.8 unspecified | **DIN VDE 0100-200:2018-10** as documented anchor; a 2023 edition is reported to exist and should be verified before v1.0 | §2.2, §8.4 |
| 9 | DIN VDE 0281 | **[OPEN]** date in v0.8 unspecified | **DIN VDE 0281 series, current part: 2000-09** + check for harmonized successors (DIN EN 50525-2-x:2011) | §2.2, §8.5, §9.3 |
| 10 | DIN VDE 0815 (formerly cited as "Installation cables") | **[CLOSED]** incorrectly cited — DIN VDE 0815 covers telecommunication/Fernmelde installation cables (J-Y(St)Y), not industrial control cables | **Removed before v0.8 consolidation.** Industrial PVC cables (NYM, NYY, H07V-K) are covered by DIN VDE 0281; flexible control cables (LiYCY, Ölflex variants) follow manufacturer specifications; harmonized successor anchor: DIN EN 50525 series. No further action required | §2.2, §8.5 (corrected) |
| 11 | IEC 61082-1 | **[VERIFIED]** date consistent | **DIN EN 61082-1:2015-04** (already OK, anchor verified) | §2.2 |
| 12 | "per DIN 19227-2" (Sensor classification) | **[OPEN]** norm withdrawn 2005; not in project library | **DIN 19227-2:1991-02** (withdrawn 2005; substantively replaced by IEC 62424) — Sensor term remains anchored in usage and is reinforced by IEC 60050-351 (see #14) | §5.11, §9.1 (Sensor classification) |
| 13 | "per DIN 1319-1" (basic metrology terms) | **[VERIFIED]** **DIN 1319-1:1995-01** is current edition and confirmed in scope | DIN 1319-1:1995-01 — Fundamentals of metrology — General terms (anchor verified, no further action) | §5.11, §9.1 (Sensor definition) |
| 14 | "per IEC 60050-351" (Sensor in IEV) | **[VERIFIED]** **DIN IEC 60050-351:2014-09** present in project library; Sensor synonym verbatim anchored | DIN IEC 60050-351:2014-09 — IEV Part 351: Control technology (anchor verified, no further action) | §5.11 (Sensor synonym anchoring) |
| 15 | DIN EN 60617-2 (Circuit_Diagram symbol elements / qualifying symbols) | **[VERIFIED]** DIN EN 60617-2:1997-08 present in project library; codes used in §5.13 verified verbatim against this PDF | DIN EN 60617-2:1997-08 (anchor verified, no further action) | §4.3 S3.2, §5.13, §9.1 Classification_System |
| 16 | DIN EN 60617-6 (Production/conversion of electrical energy — Motor, Heater, Power_Supply) | **[VERIFIED for Motor and Heater; OPEN for Power_Supply]** DIN EN 60617-6:1997-08 present in project library; codes 06-04-01 (Motor) and 06-17-01 (Heater) verified verbatim against this PDF. Per v0.8 validation finding, the IEC 60617-6 code for `Element_Type=Power_Supply` is **not yet anchored** against this norm PDF — the v0.7 placeholder `06-04-xx` is replaced by `Classification_Code=Unclassified` with `Source_Symbol_Reference` populated, per the §A.19 fallback convention. A project-side norm-anchoring pass is required to confirm or correct the Power_Supply symbol code before v1.0 freeze. | DIN EN 60617-6:1997-08 (anchor verified for Motor and Heater; Power_Supply code anchoring pending) | §4.3 S3.2, §5.12, §5.13, §9.1 Classification_System |
| 17 | DIN EN 60617-8 (Measuring instruments, lamps, signaling devices — Indicator_Lamp) | **[VERIFIED]** DIN EN 60617-8:1997-08 present in project library; code 08-10-01 (Lampe/Leuchtmelder) verified verbatim against this PDF | DIN EN 60617-8:1997-08 (anchor verified, no further action) | §4.3 S3.2, §5.13, §9.1 Classification_System |
| 18 | DIN EN 60617-7 (Switchgear, controlgear, protective devices — Coil, Contacts, Push_Button, Emergency_Stop) | **[VERIFIED with corrections per Stichwortverzeichnis-Verifikation]** DIN EN 60617-7:1997-08 present in project library. **Verified codes (verbatim per Stichwortverzeichnis):** `07-02-01` "Schließer" (NO contact), `07-02-03` "Öffner" (NC contact), `07-07-02` "Druckschalter, handbetätigte Schalter", `07-13-02` "Schütz / Leistungskontakt eines Schütz" (Main_Contact and Contactor aggregate), `07-15-01` "elektromechanischer Antrieb, allgemein" (Coil). **Corrections applied in v0.8 per Stichwortverzeichnis-Verifikation:** (1) `07-08` family is **Section 8 "Position switches"** (Endschalter), NOT contactors — earlier drafts used `07-08`/`07-08-01` for Contactor and Auxiliary_Contactor; v0.8 corrects to `07-13` family (Schütz block at `07-13-02`; auxiliary contactors as composition of `07-15-01` coil + `07-02-01`/`07-02-03` contact symbols). (2) `07-21-04` is "Sicherung mit Meldekontakt und drei Anschlüssen" per Stichwortverzeichnis, NOT RCBO — earlier drafts used this for RCBO; v0.8 removes the RCBO citation (RCBOs are not assigned a single IEC 60617-7 code; they are anchored on IEC 61009 per §16 Entry 23). **Codes carried forward without re-verification in v0.8:** `07-07-06` (cited in earlier drafts for "Pilz-Notdrucktaster"; Stichwortverzeichnis lists `02-13-08` "Notschalter, Typ Pilz-Notdrucktaster" in IEC 60617-2 as the dedicated symbol) — anchoring pending, recommended replacement: `02-13-08`. `07-15-04` (cited for PLC_Module; Section 15 is "Operating devices" / electromechanical drives, so `07-15-04` is likely a specific drive variant rather than a PLC; the verifying entry "Antrieb mit zwei getrennten Wicklungen, aufgelöste Darstellung" was found at `07-15-05`, so `07-15-04` likely exists but for an analogous drive type) — anchoring pending. | DIN EN 60617-7:1997-08 (Stichwortverzeichnis-verified for the five core codes; 07-07-06 and 07-15-04 anchoring pending — see audit notes) | §4.3 S3.2, §5.3, §5.4, §5.12, §5.13, §11.7, §11.8, §12.2, §12.3, §9.1 Classification_System |
| 19 | DIN EN 81346-2:2019 (Ed. 3, classification — Y-class reinterpretation) | **[OPEN, mitigated]** project library contains only **IEC 81346-2 Ed. 2 (2009)**; the 2019-edition Ed. 3 is referenced by §8.1 but not directly verifiable against an available PDF. Y-class definition differs between editions (Ed. 2: "Reserved for future standardization"; Ed. 3: "Mechanical action on a processing object"). **Under the current v0.8 convention**, the v0.7 assignment of class `Y` to `Element_Type=Valve_Actuator` is **incorrect against the available Ed. 2 norm PDF** (Y reserved). v0.8 reclassifies Valve_Actuator to class **M** (subclass MM "Driving by hydraulic or pneumatic means") which is verified against Ed. 2 Table 1 examples ("Fluid actuator", "Mechanical actuator"). If a future v0.9 verifies Ed. 3 norm content and the Ed. 3 Y-class definition is project-acceptable, an alternative `Y` assignment may be reintroduced for Valve_Actuator. Until then, M is the authoritative classification. | DIN EN 81346-2:2019-06 to be obtained for full Ed. 3 anchoring; Ed. 2 verified for current schema | §2.2, §8.1, §5.11, §5.12, §9.1 Classification_System |
| 19b | IEC 81346-2 Ed. 2 (2009) — Auxiliary_Contactor classification | **[VERIFIED, corrected under the current v0.8 convention]** project library contains IEC 81346-2 Ed. 2 (2009); Table 1 Class K "Processing (receiving, treating and providing) signals or information" explicitly lists "Contactor relay" (Hilfsschütz / auxiliary contactor used in control circuits) as an electrical-component example. Class Q "Controlled switching" Table 1 lists "Contactor (for power)" — i.e. main contactors for load switching. Under the current v0.8 convention, v0.8 reclassifies `Element_Type=Auxiliary_Contactor` from Q (v0.7) to **K (subclass KF "Processing of electrical and electronic signals")** as the default classification for signal-processing auxiliary contactors. Projects using Auxiliary_Contactor devices for load switching (rare but possible) may override to Q on a per-device basis via `Element_Data.Function_Scope=Power`. | IEC 81346-2 Ed. 2 (2009) Table 1 K-class examples (anchor verified) | §5.3, §5.12, §9.1 Classification_System |
| 20 | DIN VDE 0298 (current-carrying capacity of cables) | **[OPEN]** referenced in §8.5 (Cable Types) for current-rating tables; specific edition not documented in v0.8 | DIN VDE 0298-4:2013-06 (current-carrying capacity for fixed installations) — to be verified | §8.5 |
| 21 | IEC 60309 (industrial plugs and socket-outlets) | **[OPEN]** referenced in §5 (Socket_Outlet) for industrial CEE plug standard; specific edition not documented | IEC 60309-1:2021 / DIN EN 60309-1:2022 — to be verified | §5.8 |
| 22 | IEC 60947-7-1 (terminal blocks for copper conductors) | **[OPEN]** referenced in §5 (Terminal classification) for industrial terminal block standard | IEC 60947-7-1:2009 / DIN EN 60947-7-1:2013 — to be verified | §5.1 |
| 23 | IEC 61009 (RCBO — residual-current operated circuit breakers) | **[OPEN]** referenced in §5.6 (Circuit_Breaker RCBO classification); alternative anchor to IEC 60755 (general FI requirements per §16 entry #7) | IEC 61009-1:2010+A1:2012+A2:2013 / DIN EN 61009-1:2013 — to be verified | §5.6 |
| 24 | IEC 81346-1 / DIN EN IEC 81346-1 (Structuring principles and reference designations) | **[VERIFIED with note]** project library contains **DIN EN IEC 81346-1:2024-07** (PDF available, file `DIN_EN_IEC_81346-1_2024-07-00_DE_3484369.pdf`); cited 9× in body for `=` (function aspect), `+` (location aspect), `-` (product aspect) prefix conventions and `.` / `:` separator semantics. **Aspect enumeration note (per Stichwortverzeichnis verification §A.4.1):** the available 2024 edition (Ed. 3 / EN IEC 81346-1:2022) defines the `aspect_kind` EXPRESS enumeration with **five values**: `FUNCTION_ASPECT`, `PRODUCT_ASPECT`, `LOCATION_ASPECT`, `TYPE_ASPECT`, `OTHER_ASPECT`. The v0.8 `Aspect` enum (§9.3 Seed Catalog) retains the three main aspects of the earlier Ed. 2 (2009) — `Function, Location, Product` — for backward compatibility with existing project tooling and PDFs that pre-date Ed. 3. Extension to the full five-value enumeration (with `Type` and `Other`) is a planned v0.9 schema update. Until then, project use of `Type` or `Other` aspects must be recorded via `Schema_Metadata` rather than as `Aspect` enum values. | DIN EN IEC 81346-1:2024-07 (Ed. 3) | §1.1, §2.1, §2.2, §2.3, §4.1, §4.2, §4.3, §5.1, §A.7, §9.3 Aspect enum |
| 25 | IEC 62424 / DIN EN 62424 (Representation of process control engineering — Requests in P&I diagrams and data exchange) | **[VERIFIED (syntax-only for v0.8 in v0.8)]** project library contains **IEC 62424:2010** (PDF available, file `IEC_62424_2010.pdf`) and **DIN EN 62424:2017** draft approval document (PDF available, file `941_2009-0011_draft approval document_von_DIN_EN_62424__VDE_.pdf`); cited 14× in body as the anchor for `PCE_Request` (RepresentedItem_Type), `PCE_Category` letter (Tabelle 2: B, F, T, P, L, …), `PCE_Processing_Function` letter combinations (Tabelle 3: I, C, R, …), and `Actuator_Category` (Tabelle 5). **Status in v0.8 (in v0.8):** the norm PDF is present, but the Detail-Tables 2 / 3 / 5 are **not** yet integrated as `Enum_Lookup` master rows in §9.3. v0.8 therefore performs **syntax-only validation** of `Classification_Code` values when `Classification_System=IEC 62424` per the typing rule in §A.19 — structural format is checked, but individual codes against the norm tables are not. Integration of the Detail-Tables into `Enum_Lookup` (`Field_Name=PCE_Category`, `Field_Name=PCE_Processing_Function`, `Field_Name=Actuator_Category`) is the headline scope item for **v0.9** (see §15 Roadmap). Workbooks generated under v0.8 with IEC 62424 classifications remain forward-compatible with v0.9: when v0.9 ships, `Classification_Code` values become subject to full Enum_Lookup validation against the imported norm tables. | IEC 62424:2010 / DIN EN 62424:2017-09 | §2.1, §4.1, §8 (multi-classification), §12.1 worked example, §15 Roadmap (Enum_Lookup detail tables) |
| 26 | DIN EN 60617-3 (Graphical symbols for diagrams, Part 3: Conductors and connecting devices) | **[VERIFIED]** project library contains **DIN EN 60617-3:1996-08** (PDF available, file `DIN_EN_606173_19970800_ML_7366832.pdf`); per Stichwortverzeichnis verification: code `03-02-02` corresponds to "Anschluß (z.B. Klemme)" for `Element_Type=Terminal`. Earlier drafts used `03-02-01` which is "Verbindungspunkt" (T-junction) — corrected in v0.8 across §5.12, §11.7, §11.8, §12.2. | DIN EN 60617-3:1996-08 | §1.1, §2.2, §4.1, §8.1, §9.1 (Classification_System enum), §5.12, §12.2 worked example |

### 16.2 Consequences for Validators and Tools

- **Specification scope and normative content (D9):** This specification defines the **application and generation of the schema** — sheet structures, identifier conventions, process steps, integrity rules, lookup conventions. It does **not** duplicate normative content (symbol definitions per IEC 60617, classification letters per IEC 81346-2, PCE letters per IEC 62424, function letters per DIN 19227-2, color codes per IEC 60757, etc.). Any LLM, tool, or person applying this specification to interpret a source document SHALL have access to the normative references inventoried in §16.1. Without access to those normative texts, symbol-to-Element_Type and symbol-to-Classification_Code assignments cannot be performed correctly. The spec **references** norms; it does **not** replace them.

- **I24 (wire-color / polarity consistency)** is formulated against DIN EN 60446. The normative requirement (Green_Yellow = PE; Blue = N in LV AC distribution) has been largely adopted unchanged in DIN EN IEC 60445:2018-02. At norm update for v1.0, the rule wording is to be linguistically adjusted; the rule content is expected to remain the same.

- **IP_Protection list (§9.1)** is extensible without invalidating v0.8-conformant documents — later lookup enlargement is additive.

- **Trip_Characteristic differentiation by protective-element type:** for v1.0, Trip_Characteristic should be restricted per `Type_Constraint` in Attribute_Lookup:
 - `Attribute_Name=Trip_Characteristic` with `Type_Constraint=Element_Type=Fuse` → Enum {gG, gL, aM} per IEC 60269
 - `Attribute_Name=Trip_Characteristic` with `Type_Constraint=Element_Type=Circuit_Breaker` → Enum {B, C, D, K, Z} per IEC 60898-1 / IEC 60947-2

### 16.3 Maintenance Responsibility

The entries in §16.1 carry explicit status tags (`[OPEN]`, `[VERIFIED]`, `[CLOSED]`). Maintenance scope before the jump from pre-release to release (v1.0) is therefore precisely defined:

- **`[OPEN]` entries** (#1–#9, #12, #19, #20–#23 — fifteen entries) require a norm update before v1.0. Each represents an explicit "knowledge debt" held in the spec itself, so no update can be silently forgotten. Total inventory: 15 OPEN, 10 VERIFIED (#10, #11, #13–#18, #24–#26), 1 CLOSED.
- **`[VERIFIED]` entries** (#11, #13, #14, #15, #16, #17, #18 — seven entries) have their current editions confirmed available and in scope. No further v1.0 action is required.
- **`[CLOSED]` entries** (#10 — one entry) have been resolved by removal or correction within v0.8 itself. No further v1.0 action is required.

Before v1.0, every spec location marked `[⚠ norm update see §16]` traces back to an `[OPEN]` entry and is to be reviewed. The `[VERIFIED]` and `[CLOSED]` entries serve as historical record and remain in §16.1 for traceability of the consolidation decisions; they do not generate v1.0 work items.

---

## 17. Term Migration v0.4 → v0.5 (German → English)

*Relocated to Appendix B (v0.8.2 structure patch); content unchanged, original numbering retained there.*
## A. Appendix: Sheet Column Definitions

This appendix provides the column-level specification for the **28 mandatory schema sheets**. The numbering follows the Sheet Catalog in §3.0 exactly. `A.1` corresponds to Sheet #1 `Rules`; `A.28` corresponds to Sheet #28 `Element_Classification_Source`.

### A.1 `Rules`

| Column | Type | Required |
|---|---|---|
| Rule_ID | String | Yes (PK) |
| Rule_Category | Enum | Yes |
| Rule_Name | String | Yes |
| Rule_Description | String | Yes |
| Rule_Reference | String | No |
| Schema_Version_Introduced | String | Yes |

### A.2 `Schema_Metadata`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Metadata_Key | String | Yes (PK) |
| Metadata_Value | String | Yes |
| Description | String | No |

Seed content:

| Metadata_Key | Metadata_Value | Description |
|---|---|---|
| Schema_Version | v0.8 | Current schema version, used as default for new `Document_ID` rows |
| Lookup_Version | v0.8.0 | Current lookup catalog version |
| Publication_Date | 2026-05-29 | Date of this schema specification |
| Allowed_Element_Type_Extensions | (empty CSV) | Project-specific Element_Type extensions accepted by I14, comma-separated; default empty (only §9.3 canonical values accepted) |
| Allowed_RepresentedItem_Type_Extensions | (empty CSV) | Project-specific RepresentedItem_Type extensions accepted by I14, comma-separated; default empty |
| Cable_Modeling_Profile | Core | Cable modeling profile; allowed values `Core` (default; `A.O3 Cable_Data` absent and `Connection_ID.Cable_Data_ID` present but null) or `Asset` (activates `A.O3 Cable_Data` and permits `Connection_ID.Cable_Data_ID` FK population). The `Connection_ID.Cable_Data_ID` column is always present for header stability. |
| Project_Lookup_Profile_ID | (empty) | Optional reference to a project-side lookup profile that constrains workbook-local extensions to a project-consistent set; default empty (workbook-local extensions only, no cross-workbook profile binding) |

### A.3 `Document_ID`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Document_ID | String | Yes (PK) |
| Document_Type | Enum | Yes |
| Document_Filename | String | Yes |
| Page_Count | Integer | Yes |
| Schema_Version | String | Yes (from `Schema_Metadata`) |
| Lookup_Version | String | Yes (from `Schema_Metadata`) |
| Created_Timestamp | DateTime | Yes |
| Created_By | String | Yes (tool or user identifier) |
| SemanticID | String | No |

### A.4 `Document_Data`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes (orientation only, no semantics) |
| Document_Data_ID | String | Yes (PK; pattern `DD.N` per §3.7) |
| Document_ID | FK | Yes |
| Attribute_Name | String | Yes (must exist in `Attribute_Lookup` with `Scope = Document`) |
| Attribute_Value | String | Yes (canonical schema value — see §A.15 for full semantics) |
| Raw_Value | String | No (source-verbatim string — see §A.15) |
| Normalized_Value | String | No (numeric/canonical scalar portion — see §A.15) |
| Unit | String | No (physical unit only, SI conventions — see §A.15) |
| Quantity_Qualifier | String | No (non-unit qualifier: DC/AC/RMS/peak/… — see §A.15) |
| Parsing_Status | Enum | No (`Parsed_OK` / `Parsed_Ambiguous` / `Parsed_Failed` / `Unspecifiable`) |
| SemanticID | String | No |

### A.5 `Revision_Data`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Revision_ID | String | Yes (PK; pattern `R.N`) |
| Document_ID | FK | Yes |
| Revision_Index | String | Yes |
| Revision_Date | Date | Yes |
| Revision_Author | String | No |
| Revision_Description | String | No |
| SemanticID | String | No |

### A.6 `Document_RepresentedItem`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| RepresentedItem_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| RepresentedItem_Type | Enum | Yes (from `Enum_Lookup`) |
| Primary_RKZ | String | Conditional (null if `Topic_Identification_Status` indicates failure) |
| Parent_RepresentedItem_ID | FK | No |
| Topic_Identification_Status | Enum | Yes (`Confirmed` \| `Inferred` \| `Ambiguous` \| `Failed` \| `Unspecifiable`) |
| CAEX_RoleClass_Path | String | No |
| CAEX_SystemUnitClass_Path | String | No |
| SemanticID | String | No |

Attributes of a RepresentedItem are stored in `RepresentedItem_Data` (separate sheet — no polymorphism with `Element_Data`).

**Schriftfeld mapping (Stellenplan):** the seed `Attribute_Lookup` entries with `Scope = Document` (e.g. `Project_Name`, `Plant_Designation`, `Position`, `Drawing_Number`, `Created_Date`, `Author`, `Reviewer`) constitute the title-block attributes for Stellenpläne. `Document_RepresentedItem` is derived from these via S-rules (S1 for Stellenplan).

**CAEX Interface derivation (no separate column needed):** Interface definitions of a RepresentedItem (e.g. the Signal/Indication/Actuator interfaces of a PCE-Aufgabe per IEC 62424 Annex C) are derived from the boundary Elements assigned to this RepresentedItem. Derivation path:
1. `Document_RepresentedItem.RepresentedItem_ID`
2. → `Element_RepresentedItem_Mapping` (linked Elements)
3. → filter `Element_ID.CAEX_Type = ExternalInterface`
4. → the resulting Elements' `CAEX_InterfaceClass_Path` values are the InterfaceClasses of this RepresentedItem

The interface definitions are therefore not stored on `Document_RepresentedItem` itself, but are recoverable from the Element layer.

### A.7 `Object`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Object_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| Page_Number | Integer | Yes |
| Object_Type | Enum | Yes |
| Source_Operation | Enum | Yes |
| BBox_X1, BBox_Y1, BBox_X2, BBox_Y2 | Float | Conditional (source-format-specific; see table below) |
| Content_Text | String | Conditional (if `Text`) |
| Content_Font_Size | Float | Conditional (if `Text`) |
| Geometry_Type | Enum | Conditional (if `Graphic` or `Topology`) |
| Geometry_Closed | Boolean | Conditional (if `Graphic`) |
| Topology_From_Object_ID | FK | Conditional (if `Topology`, per C3) |
| Topology_To_Object_ID | FK | Conditional (if `Topology`, per C3) |
| Topology_Validation_Status | Enum | Conditional (if `Topology`): `Valid_Connection` \| `Unresolved` \| `Unspecifiable` |
| Object_Role | Enum | No (`Connection_Point` / `Label` / `Symbol` / `Border` / `Annotation` / `Topology`; used by C3 to identify connection-point source objects as endpoint targets for topology resolution) |
| SemanticID | String | No |

**Source-format-specific column semantics (K1 + K3 resolution):** The `Object` sheet is universal across PDF, Excel and Verschaltungsliste source formats. The column names are source-format neutral; their interpretation depends on the source format, distinguished by `Source_Operation`:

| Column | PDF source (`Source_Operation ∈ {Tj, TJ, ', ", f, F, f*, S, s, B, b, re}` per §9.3 Authoritative Seed Catalog) | Excel source (`Source_Operation = Cell`) | Verschaltungsliste source (`Source_Operation = VL_Row`) | Manual evidence (`Source_Operation = Manual_Entry`) |
|---|---|---|---|---|
| `Page_Number` | PDF page number (1-based) | Sheet index in the source workbook (1-based, in workbook `sheetnames` order) | Sheet index in the VL-workbook (1-based) | `0` |
| `Source_Operation` | PDF content-stream operator | Constant string `Cell` | Constant string `VL_Row` | Constant string `Manual_Entry` |
| `BBox_X1` | left X coordinate (PDF points) | Row index (1-based) of the source cell | Row index (1-based) of the VL row | `null` |
| `BBox_Y1` | bottom Y coordinate (PDF points) | Column index (1-based) of the source cell | `null` (whole row, not a single cell) | `null` |
| `BBox_X2` | right X coordinate | For merged cells: end-row index; otherwise = `BBox_X1` | `null` | `null` |
| `BBox_Y2` | top Y coordinate | For merged cells: end-column index; otherwise = `BBox_Y1` | `null` | `null` |
| `Content_Text` | text run delivered by the PDF parser | Cell value as string (only present for non-empty cells; numeric values stringified per ISO encoding) | Serialised row content (pipe-separated cell values in column order; empty cells appear as empty strings between separators) | rationale or decision evidence text |
| `Content_Font_Size` | font size in points | `null` (Excel cells do not carry font sizes in a stable way for source provenance) | `null` | `null` |
| `Geometry_Type`, `Geometry_Closed`, `Topology_*` | populated for `Graphic`/`Topology` objects | `null` (Excel sources have no graphic/topology objects in the structural sense) | `null` | `null` |

**Object_Type values for Excel sources:** Excel cells with non-empty content map to `Object_Type=Text`. Cells with only formatting (e.g. merged cells used as visual separators) may map to `Object_Type=Graphic` if they carry structural meaning — this is a tool-parameter decision.

**Object_Type values for Verschaltungsliste sources:** VL rows always map to `Object_Type=Text`. The granularity is one Object per logical VL row (not one per cell within the row); this matches the population sequence in §4.4.2 (one Connection_ID per VL row).

**Object_Type values for manual evidence:** Synthetic manual-evidence rows always map to `Object_Type=Text`, `Source_Operation=Manual_Entry`, and `Page_Number=0`. They provide an addressable provenance artifact for manual, rule-derived, norm-derived, or aggregation-derived decisions and do not represent a spatial source object.

### A.8 `Cluster`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Cluster_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| Parent_Cluster_ID | FK | No |
| Container_Object_ID | FK | Conditional  |
| Cluster_Type | Enum | Yes |
| Cluster_BBox_X1, Y1, X2, Y2 | Float | Yes |
| Cluster_Method | String | Conditional (required when `Cluster_Type = Proximity`; identifies the clustering algorithm, e.g. `NearestNeighbor_2xMean`, `DBSCAN`, `Grid_Based`) |
| Cluster_Parameter_Set | String | Conditional (required when `Cluster_Type = Proximity`; serialized JSON of algorithm parameters, e.g. `{"factor":2.0,"unit":"mean_nn"}`; enables reproducibility of the clustering pass from the workbook alone) |
| SemanticID | String | No |

### A.9 `Object_Cluster`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Object_ID | FK | Yes |
| Cluster_ID | FK | Yes |
| Membership_Reason | Enum | Yes |

Topology-Objects do not appear in this sheet (per C3).

### A.10 `Elements_TopDown`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Element_TopDown_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| Element_Name | String | Yes |
| Primary_RKZ | String | Conditional |
| Element_Type | Enum | Yes (validated via `Enum_Lookup.Field_Name=Element_Type`) |
| Parent_Element_TopDown_ID | FK | No |
| SemanticID | String | No |

### A.11 `Elements_from_Cluster`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Element_from_Cluster_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| Source_Cluster_ID | FK | Yes |
| Element_Name | String | Conditional (required if `Derivation_Status = Element_Derived`) |
| Primary_RKZ_Extracted | String | No |
| Element_Type_Inferred | Enum | Conditional (required if `Derivation_Status = Element_Derived`; validated via `Enum_Lookup.Field_Name=Element_Type`) |
| Derivation_Status | Enum | Yes (`Element_Derived` \| `No_Element_Derivable` \| `Ambiguous` \| `Failed` \| implicit `Unspecifiable`) |
| SemanticID | String | No |

### A.12 `Match_Result`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Match_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| Element_TopDown_ID | FK | Conditional |
| Element_from_Cluster_ID | FK | Conditional |
| Match_Status | Enum | Yes |
| Match_Rule | Enum | Conditional |
| Resolution_Note | String | No |
| Resolution_Status | Enum | Yes |
| Reviewed_By | String | No (agent identifier — `Auto` when auto-resolved by Match_Rule without further intervention; otherwise an identifier of the resolving agent: tool name, LLM identifier, or operator user-id depending on the resolution mechanism per §1.3 tool-agnostic principle) |
| Review_Status | Enum | No (`Unreviewed` / `Requires_Review` / `Auto_Approved` / `Manually_Reviewed` / `Manually_Corrected` / `Rejected`; null defaults to `Unreviewed`) |
| Correction_Reason | String | No (free-text rationale when `Review_Status = Manually_Corrected` or `Rejected`; null otherwise) |
| Review_Timestamp | DateTime | No (ISO 8601, when the review/decision was performed; null when no review has occurred) |
| SemanticID | String | No |

**Audit-trail alignment:** the four review-related columns above mirror the audit-trail columns introduced for the six `*_Source` sheets. Match_Result is the home of TopDown↔Cluster reconciliation decisions; recording the reviewer/status/reason/timestamp directly on the Match_Result row keeps the audit trail co-located with the decision being audited. A separate `Review_Log` table is not required.

### A.13 `Element_ID`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Element_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| Source_Match_ID | FK | Yes |
| Source | Enum | Yes |
| Element_Type | Enum | Yes (validated via `Enum_Lookup.Field_Name=Element_Type`) |
| Primary_RKZ | String | Conditional |
| Parent_Element_ID | FK | No |
| Layer_ID | FK | No (→ `Layer_ID.Layer_ID`; nullable for documents without layer structure) |
| CAEX_Type | Enum | Yes |
| CAEX_RoleClass_Path | String | No |
| CAEX_SystemUnitClass_Path | String | No |
| CAEX_InterfaceClass_Path | String | No |
| SemanticID | String | No |

Per K3: this sheet has NO `RepresentedItem_ID` column.

### A.14 `Element_RepresentedItem_Mapping`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Mapping_ID | String | Yes (PK; pattern `MAP.N`) |
| Element_ID | FK | Yes |
| RepresentedItem_ID | FK | Yes |
| Relationship_Type | Enum | Yes (`Primary` \| `Shared` \| `Secondary`) |
| SemanticID | String | No |

**Relationship_Type semantics:**
- `Primary`: The element is intrinsically/dedicatedly part of this RepresentedItem; the element's existence is justified primarily by serving this RepresentedItem. **Constraint (I22):** at most one `Primary` row per Element.
- `Shared`: The element serves multiple RepresentedItems with equivalent functional weight (e.g. a multi-channel SPS module whose channels are used by two different PCE-Aufgaben). Multiple `Shared` rows per Element allowed.
- `Secondary`: The element auxiliarily supports this RepresentedItem but is dedicated elsewhere (i.e. has a Primary or Shared relationship to another RepresentedItem). Multiple `Secondary` rows per Element allowed.

### A.15 `Element_Data`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes (orientation only, no semantics) |
| Element_Data_ID | String | Yes (PK; pattern `ED.N` per §3.7) |
| Element_ID | FK | Yes |
| Attribute_Name | String | Yes (must exist in `Attribute_Lookup` with `Scope = Element` and matching `Type_Constraint`) |
| Attribute_Value | String | Yes (**canonical schema value** — the value that downstream consumers read; for enum-typed attributes this is the language-neutral code per §0.1, e.g. `RD` for Wire_Color; for free-form attributes this is the verbatim source string) |
| Raw_Value | String | No (**source-verbatim string** before any normalization; populated when `Attribute_Value` differs from the source word, e.g. source carries `"rot"` → `Raw_Value="rot"`, `Attribute_Value="RD"`; or for parseable scalars e.g. source `"24V DC"` → `Raw_Value="24V DC"`, then split into the three normalization fields below) |
| Normalized_Value | String | No (**numeric or canonical scalar portion** extracted from `Raw_Value`, e.g. `"24"` for the example above; null when no numeric portion is meaningful) |
| Unit | String | No (**physical unit only** per the SI conventions; `"V"`, `"A"`, `"mm²"`, `"Ω"`; SHALL NOT contain qualifiers like `"DC"`, `"AC"`, `"RMS"`) |
| Quantity_Qualifier | String | No (: **qualifier of the quantity** that is not a unit, e.g. `"DC"`, `"AC"`, `"RMS"`, `"peak"`, `"nominal"`; for the `"24V DC"` example: `Quantity_Qualifier="DC"`) |
| Parsing_Status | Enum | No (normalization field: `Parsed_OK` / `Parsed_Ambiguous` / `Parsed_Failed` / `Unspecifiable`) |
| SemanticID | String | No |

**Encoding semantics for Wire_Color and similar enum-typed attributes:** Take Wire_Color as the exemplar. Source document text: `rot`. The Element_Data / Connection_Data row carries: `Attribute_Name=Wire_Color`, `Attribute_Value=RD` (the canonical schema code, per §0.1 universal encoding convention), `Raw_Value=rot` (source-verbatim), `Normalized_Value=null` (no numeric portion), `Unit=null`, `Quantity_Qualifier=null`. The corresponding `Object` row preserves `Content_Text=rot`. The chain `source → Object → Raw_Value → Attribute_Value` is fully traceable.

**Encoding semantics for scalar attributes (e.g. `Rated_Voltage=24V DC`):** `Attribute_Value="24V DC"` (canonical, the human-readable composite as recorded), `Raw_Value="24V DC"` (verbatim from source), `Normalized_Value="24"`, `Unit="V"`, `Quantity_Qualifier="DC"`, `Parsing_Status=Parsed_OK`. The split into `Normalized_Value` + `Unit` + `Quantity_Qualifier` enables machine-comparable processing; `Attribute_Value` and `Raw_Value` preserve the unsplit form for display and round-trip fidelity.

### A.16 `Element_Data_Source`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes (orientation only, no semantics) |
| Element_Data_ID | FK | Yes (→ `Element_Data.Element_Data_ID`) |
| Source_Object_ID | FK | Yes |
| Source_Role | Enum | No (`Label` / `Value` / `Symbol`) |
| Extraction_Method | Enum | No (audit field: `OCR` / `Native_Text` / `LLM_Classification` / `Manual_Entry` / `Rule_Based_Parser` / `Unspecifiable`) |
| Confidence | Float | No (audit field: 0.0–1.0; null when no confidence model applies) |
| Reviewed_By | String | No (audit field: agent identifier — `Auto` for tool-driven population, otherwise tool name, LLM identifier, or operator user-id per §1.3 tool-agnostic principle) |
| Review_Status | Enum | No (audit field: `Unreviewed` / `Requires_Review` / `Auto_Approved` / `Manually_Reviewed` / `Manually_Corrected` / `Rejected`) |
| Correction_Reason | String | No (audit field: rationale if a manual correction was applied) |
| Extraction_Timestamp | DateTime | No (audit field: ISO 8601 timestamp) |
| SemanticID | String | No |

### A.17 `RepresentedItem_Data`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes (orientation only, no semantics) |
| RepresentedItem_Data_ID | String | Yes (PK; pattern `RID.N` per §3.7) |
| RepresentedItem_ID | FK | Yes |
| Attribute_Name | String | Yes (must exist in `Attribute_Lookup` with `Scope = RepresentedItem` and matching `Type_Constraint`) |
| Attribute_Value | String | Yes (canonical schema value — see §A.15 for full semantics) |
| Raw_Value | String | No (source-verbatim string — see §A.15) |
| Normalized_Value | String | No (numeric/canonical scalar — see §A.15) |
| Unit | String | No (physical unit only — see §A.15) |
| Quantity_Qualifier | String | No (non-unit qualifier — see §A.15) |
| Parsing_Status | Enum | No (`Parsed_OK` / `Parsed_Ambiguous` / `Parsed_Failed` / `Unspecifiable`) |
| SemanticID | String | No |

### A.18 `RepresentedItem_Data_Source`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes (orientation only, no semantics) |
| RepresentedItem_Data_ID | FK | Yes (→ `RepresentedItem_Data.RepresentedItem_Data_ID`) |
| Source_Object_ID | FK | Yes |
| Source_Role | Enum | No (`Label` / `Value` / `Symbol`) |
| Extraction_Method | Enum | No (audit field; same value range as A.16) |
| Confidence | Float | No (audit field) |
| Reviewed_By | String | No (audit field) |
| Review_Status | Enum | No (audit field; same value range as A.16) |
| Correction_Reason | String | No (audit field) |
| Extraction_Timestamp | DateTime | No (audit field) |
| SemanticID | String | No |

### A.19 `Element_Classification`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Classification_ID | String | Yes (PK; pattern `EC.N`) |
| Document_ID | FK | Yes |
| Classified_Object_Type | Enum | Yes (`Element` \| `RepresentedItem` \| `Connection` \| `Document`) |
| Classified_Object_ID | String | Yes (FK resolved according to `Classified_Object_Type`) |
| Classification_System | Enum | Yes (validated against `Enum_Lookup` with `Field_Name=Classification_System` per I14; values per §9.3, namespace `IEC 81346-2 \| IEC 62424 \| IEC 60617-2 \| IEC 60617-3 \| IEC 60617-6 \| IEC 60617-7 \| IEC 60617-8 \| DIN 19227-2`) |
| Classification_Code | String | Yes (system-dependent validation per the rule below) |
| Classification_Description | String | No |
| Source_Symbol_Reference | String | Conditional (required if `Classification_Code=Unclassified`) |
| SemanticID | String | No |


**Special value precedence:** If `Classification_Code=Unclassified`, system-specific pattern validation is skipped and `Source_Symbol_Reference` is mandatory. For all other values, the system-dependent validation rule applies.

**Polymorphic target validity:** `Classified_Object_ID` SHALL reference the sheet implied by `Classified_Object_Type`: `Element` → `Element_ID.Element_ID`; `RepresentedItem` → `Document_RepresentedItem.RepresentedItem_ID`; `Connection` → `Connection_ID.Connection_ID`; `Document` → `Document_ID.Document_ID`.

`Element_Classification` keeps its historical sheet name for compatibility, but the row target is defined by `Classified_Object_Type` and `Classified_Object_ID`. For `Classified_Object_Type=Element`, `Classified_Object_ID` references `Element_ID.Element_ID`. For `RepresentedItem`, it references `Document_RepresentedItem.RepresentedItem_ID`.

**Naming note:** The sheet name `Element_Classification` is retained for backward compatibility with v0.4 / v0.5 / v0.6 / v0.7 workbooks, but is now a misnomer — the polymorphic content also classifies `RepresentedItem`, `Connection`, and `Document` rows. A rename to `Classification` is semantically cleaner and is evaluated for v1.0; until then, the historical name is normative and tools SHALL accept `Element_Classification` as the sheet name. A v1.0 migration would introduce `Classification` as the canonical name with `Element_Classification` as a deprecated alias accepted on read.

**Classification_Code typing rule:** Although the column type is `String`, validation is **system-dependent** on `Classification_System`:
- `Classification_System = IEC 81346-2` → `Classification_Code` SHALL be a single uppercase letter from the set `{A, B, C, E, F, G, H, K, M, P, Q, R, S, T, U, V, W, X, Y}` per IEC 81346-2 Table 1.
- `Classification_System ∈ {IEC 60617-2, IEC 60617-3, IEC 60617-6, IEC 60617-7, IEC 60617-8}` → `Classification_Code` SHALL match the item-code pattern `NN-NN-NN` (e.g. `07-15-01`, `06-04-01`) per IEC 60617 indexing convention.
- `Classification_System = IEC 62424` → syntax-only validation (free-form code); the detailed code tables (PCE_Category Table 2, PCE_Processing_Function Table 3, Actuator_Category Table 5) are not part of v0.8 and are planned for v0.9 (see §15). Until those tables are added, validators perform structural validation only.
- `Classification_System = DIN 19227-2` → syntax-only validation (legacy code, free-form).
- `Classification_Code = Unclassified` is universally admissible (per I28 fallback) — it indicates an explicit non-classification with `Source_Symbol_Reference` documenting the reason.

### A.20 `Connection_ID`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Connection_ID | String | Yes (PK) |
| Document_ID | FK | Yes |
| From_Element_ID | FK | Yes |
| To_Element_ID | FK | Yes |
| Source_Topology_Object_ID | FK | Yes |
| Connection_Status | Enum | Yes (`Resolved` \| `Unresolved`) |
| Cable_Data_ID | FK | No (always present for header stability; populated only when `Schema_Metadata.Cable_Modeling_Profile=Asset` and `A.O3 Cable_Data` is active; references `Cable_Data.Cable_Data_ID`; null otherwise) |
| SemanticID | String | No |

**Single-document invariant:** `From_Element_ID` and `To_Element_ID` reference `Element_ID` rows **in the same workbook** (i.e. with the same `Document_ID` as this `Connection_ID` row). Cross-document connections (e.g. a wire that physically continues into a separate document's workbook) are **not** modeled as Connection_ID rows; they are captured on the originating Element_ID as `Element_Data.Cross_Reference_*` attributes per §4.3.3. Cross-document continuation is reconstructed by the downstream aggregation layer, not by FK in the schema.

**Source connection object semantics:** `Source_Topology_Object_ID` is the source artifact that justifies the existence of the connection row. For PDF sources it references the topology line/path object. For Excel Terminal_Diagram sources it references the row or cell object representing the connection row. For Verschaltungsliste sources it references the `VL_Row` object. For manual connections it references a synthetic `Manual_Entry` object. The historical column name is retained for compatibility, but the semantics are source-format-neutral.

### A.21 `Connection_Data`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Connection_Data_ID | String | Yes (PK; pattern `CD.N`) |
| Connection_ID | FK | Yes (→ `Connection_ID.Connection_ID`) |
| Attribute_Name | String | Yes (must exist in `Attribute_Lookup` with `Scope = Connection`) |
| Attribute_Value | String | Yes (canonical schema value — see §A.15 for full semantics) |
| Raw_Value | String | No (source-verbatim string — see §A.15) |
| Normalized_Value | String | No (numeric/canonical scalar — see §A.15) |
| Unit | String | No (physical unit only — see §A.15) |
| Quantity_Qualifier | String | No (non-unit qualifier — see §A.15) |
| Parsing_Status | Enum | No (`Parsed_OK` / `Parsed_Ambiguous` / `Parsed_Failed` / `Unspecifiable`) |
| SemanticID | String | No |

### A.22 `Connection_Data_Source`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Connection_Data_ID | FK | Yes (→ `Connection_Data.Connection_Data_ID`) |
| Source_Object_ID | FK | Yes |
| Source_Role | Enum | No (`Label` / `Value` / `Symbol`) |
| Extraction_Method | Enum | No (audit field; same value range as A.16) |
| Confidence | Float | No (audit field) |
| Reviewed_By | String | No (audit field) |
| Review_Status | Enum | No (audit field; same value range as A.16) |
| Correction_Reason | String | No (audit field) |
| Extraction_Timestamp | DateTime | No (audit field) |
| SemanticID | String | No |

### A.23 `Layer_ID`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Layer_ID | String | Yes (PK; project-internal pattern, e.g. `5.0-1`) |
| Document_ID | FK | Yes |
| Layer_Description | String | No (human-readable description, e.g. `Signalanpassung`) |
| Layer_Type | Enum | No (e.g. `Voltage_Level`, `Functional_Section`, `Signal_Group`, `Protection_Group`) |
| Voltage_Level | Enum | No (optional machine-readable voltage level used by I24 when populated) |
| SemanticID | String | No |

### A.24 `Attribute_Lookup`

`Element_Type` is enum-validated via `Enum_Lookup.Field_Name=Element_Type`. Project-specific extensions require explicit declaration in `Schema_Metadata.Allowed_Element_Type_Extensions` and are accepted by I14 only when declared.

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Lookup_ID | String | Yes (PK) |
| Scope | Enum | Yes (`Document` \| `Element` \| `RepresentedItem` \| `Connection`) |
| Type_Constraint | String | No (filters per `Scope`: for `Scope=Document` use `Document_Type=Instrument_Loop_Diagram`; for `Scope=Element` use `Element_Type=PLC_Module`; for `Scope=RepresentedItem` use `RepresentedItem_Type=PCE_Request`; empty = applies to all types in the scope; syntax per §9.4) |
| Attribute_Name | String | Yes |
| Required | Boolean | Yes |
| Data_Type | Enum | Yes |
| Allowed_Values_Enum_Field | String | Conditional |
| Normative_Reference | String | No |
| Description | String | No |
| Schema_Version_Introduced | String | Yes (`v0.4` for all entries in initial seed) |

**Completeness convention (D8):** `Attribute_Lookup` is a **static spec artifact**. Every workbook generated under this specification **SHALL** contain the union of: (a) every Attribute_Name listed in §9.2 (Attribute_Lookup Additions), and (b) every Attribute_Name referenced from `Document_Data.Attribute_Name`, `Element_Data.Attribute_Name`, `RepresentedItem_Data.Attribute_Name`, or `Connection_Data.Attribute_Name` in the workbook itself. Implementations SHALL NOT prune Attribute_Lookup entries to "only what is used" — the full §9.2 catalog appears in every workbook regardless of whether all attributes are populated, ensuring downstream consumers see the same lookup table in every workbook. Project-specific extensions beyond §9.2 are permitted but SHALL be documented in a project-side appendix and clearly marked.

### A.25 `Enum_Lookup`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Enum_Lookup_ID | String | Yes (PK; pattern `EL.N`) |
| Field_Name | String | Yes |
| Allowed_Value | String | Yes |
| Description | String | No |
| Normative_Reference | String | No |

**Completeness convention (D7):** `Enum_Lookup` is a **static spec artifact**. Every workbook generated under this specification **SHALL** contain every `(Field_Name, Allowed_Value)` pair listed in §9.3 (Unified Enum_Lookup Encoding Convention). Compact value sets listed in §9.3 are specification shorthand only and SHALL be expanded into one Excel row per `(Field_Name, Allowed_Value)` pair. Implementations SHALL NOT prune Enum_Lookup entries to "only what is used in this workbook" — the full §9.3 catalog appears verbatim in every workbook. The universal `Unspecifiable` marker per E5 is implicit and SHALL NOT be duplicated as a regular Enum_Lookup row. It is accepted for every enum-typed Field_Name by I14.

**Project-Profile binding:** Project-local `Enum_Lookup` rows are governed by the workbook-level `Schema_Metadata` row with `Metadata_Key=Project_Lookup_Profile_ID`. `Enum_Lookup` itself has **no** `Project_Lookup_Profile_ID` column — there is no per-row profile attribution at the Enum_Lookup level. When `Project_Lookup_Profile_ID` is empty, project-local enum extensions are workbook-local and validated only within the workbook. When `Project_Lookup_Profile_ID` is populated, aggregation-level validators MAY compare the project-local `Enum_Lookup` extensions across all workbooks declaring the same profile, and MAY warn or fail on divergence depending on whether an external profile master is supplied (per I14 Project-Profile binding clause in §11.7).

### A.26 `Document_Data_Source`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Document_Data_ID | FK | Yes (→ `Document_Data.Document_Data_ID`) |
| Source_Object_ID | FK | Yes |
| Source_Role | Enum | No (`Label` / `Value` / `Symbol`) |
| Extraction_Method | Enum | No (audit field; same value range as A.16) |
| Confidence | Float | No (audit field) |
| Reviewed_By | String | No (audit field) |
| Review_Status | Enum | No (audit field; same value range as A.16) |
| Correction_Reason | String | No (audit field) |
| Extraction_Timestamp | DateTime | No (audit field) |
| SemanticID | String | No |

### A.27 `Revision_Data_Source`
| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Revision_ID | FK | Yes (→ `Revision_Data.Revision_ID`) |
| Source_Object_ID | FK | Yes |
| Source_Role | Enum | No (`Label` / `Value` / `Symbol`) |
| Extraction_Method | Enum | No (audit field; same value range as A.16) |
| Confidence | Float | No (audit field) |
| Reviewed_By | String | No (audit field) |
| Review_Status | Enum | No (audit field; same value range as A.16) |
| Correction_Reason | String | No (audit field) |
| Extraction_Timestamp | DateTime | No (audit field) |
| SemanticID | String | No |

### A.28 `Element_Classification_Source`

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Classification_ID | FK | Yes (→ `Element_Classification.Classification_ID`) |
| Source_Object_ID | FK | Yes |
| Source_Role | Enum | No (`Label` \| `Value` \| `Symbol`) |
| Extraction_Method | Enum | No (audit field; same value range as A.16) |
| Confidence | Float | No (audit field) |
| Reviewed_By | String | No (audit field) |
| Review_Status | Enum | No (audit field; same value range as A.16) |
| Correction_Reason | String | No (audit field) |
| Extraction_Timestamp | DateTime | No (audit field) |
| SemanticID | String | No |



### A.O1 `Designation` (optional extension)

**Purpose:** Advanced reference-designation modeling for projects that require cross-document identity tracking beyond simple Primary_RKZ-prefix matching. Captures designation aspects (function, location, product) per IEC 81346-1, plus normalized forms for cross-workbook joins. Workbook conformance does not require this sheet.

**Relation to the mandatory core rule:** Core-minimum designation normalization is defined in §3.8 and applies even when `A.O1 Designation` is absent. The optional `A.O1 Designation` sheet provides advanced aspect decomposition and normalized designation management beyond the mandatory core rule.

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Designation_ID | String | Yes (PK; pattern `DSG.N`) |
| Document_ID | FK | Yes |
| Raw_RKZ | String | Yes (verbatim from source) |
| Normalized_RKZ | String | Yes (canonical form for cross-workbook joins) |
| Aspect | Enum | Yes (`Function` / `Location` / `Product` per IEC 81346-1) |
| Parent_Designation_ID | FK | No |
| Namespace | String | No (project namespace, e.g. `Legacy_DIN19227`, `IEC_81346_Conformant`) |
| Source_Object_ID | FK | No |
| SemanticID | String | No |

### A.O2 `Electrical_Node` (optional extension)

**Purpose:** Models electrical nodes (star points, ring nodes) where more than two endpoints meet. Replaces the workaround of multiple Connection_ID rows with identical Source_Topology_Object_ID. the relationship "which Elements participate in this node" is normalized into a dedicated member sheet `A.O2b Electrical_Node_Member` rather than encoded as a CSV-list — this enables proper FK validation. Workbook conformance does not require this sheet.

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Electrical_Node_ID | String | Yes (PK; pattern `EN.N`) |
| Document_ID | FK | Yes |
| Node_Type | Enum | Yes (`Star_Point` / `Ring_Node` / `Bus_Tap` / `Junction`) |
| Source_Object_ID | FK | No |
| SemanticID | String | No |

### A.O2b `Electrical_Node_Member` (optional extension)

**Purpose:** Normalization sheet for the many-to-many relationship between `Electrical_Node` and `Element_ID`. Each row registers one Element_ID's participation in one Electrical_Node, with role and validation status. Required if and only if `A.O2 Electrical_Node` is active in the workbook.

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Electrical_Node_Member_ID | String | Yes (PK; pattern `ENM.N`) |
| Electrical_Node_ID | FK | Yes (→ `Electrical_Node.Electrical_Node_ID`) |
| Element_ID | FK | Yes (→ `Element_ID.Element_ID`; the participating Element, typically of `Element_Type=Terminal`) |
| Terminal_Role | String | No (free-form: `Star_Center`, `Branch_Endpoint`, `Ring_Member`, etc.) |
| Membership_Status | Enum | No (`Confirmed` / `Inferred` / `Unspecifiable`) |
| Source_Object_ID | FK | No |
| SemanticID | String | No |

**Integrity rule (workbook-local, applies only when A.O2 is active):** every `Electrical_Node_ID` SHALL have at least two `Electrical_Node_Member` rows. Single-member nodes are not electrically meaningful and indicate authoring error.

### A.O3 `Cable_Data` (optional extension)

**Purpose:** Models a physical cable as an asset object when project requirements demand cable inventory, route assignment, or cable-level attributes beyond shared `Cable_Number`. connections belonging to a cable are linked via a dedicated **nullable FK column on `Connection_ID`** rather than as a Long-Form attribute row — this enables proper FK validation. Workbook conformance does not require this sheet.

| Column | Type | Required |
|---|---|---|
| Index | Integer | Yes |
| Cable_Data_ID | String | Yes (PK; pattern `CAB.N`) |
| Document_ID | FK | Yes |
| Cable_Number | String | Yes (shared identifier; matches the `Cable_Number` attribute used by I25) |
| Cable_Type | Enum | No (validated via `Enum_Lookup.Field_Name=Cable_Type`; the §9.3 Seed Catalog mirrors §8.5 verbatim, see Cable_Type entry) |
| Shielding | Enum | No |
| Total_Wire_Count | Integer | No |
| Length | Float | No |
| Route_Description | String | No |
| Source_Object_ID | FK | No |
| SemanticID | String | No |

**Connection linkage:** `Connection_ID` always carries the nullable FK column `Cable_Data_ID` for header stability. When `A.O3 Cable_Data` is active in the workbook, populated `Cable_Data_ID` values reference `Cable_Data.Cable_Data_ID`. When `A.O3` is absent or a connection has no modeled cable asset, `Cable_Data_ID` remains null. No `Connection_ID` header changes between Core and Asset profiles.

**I25 profile-awareness:** I25 (Cable_Number consistency) operates in two modes depending on whether `A.O3` is active:
- **Core mode (A.O3 absent):** I25 fires on `Connection_Data.Cable_Number` value equality, as defined in §11.9. Cable_Type / Shielding / Total_Wire_Count consistency is checked across connections sharing the same `Cable_Number` value.
- **Asset mode (A.O3 active):** `Cable_Data` is authoritative for cable-level attributes. If `Cable_Number`, `Cable_Type`, `Shielding`, or `Total_Wire_Count` are redundantly populated in `Connection_Data` for a connection whose `Cable_Data_ID` references a `Cable_Data` row, they SHALL match the referenced `Cable_Data` row. Divergence is an I25 violation. Recommended Asset-mode practice: cable-level attributes are populated only in `Cable_Data`. `Connection_Data` carries connection-specific attributes such as `Wire_Color`, `Polarity`, `Voltage_Level`, and `Wire_Number`. A.O3 and §11.9 I25 state this conflict rule identically.

**Cable modeling profile:** The schema supports two cable modeling profiles, declared via `Schema_Metadata` attribute `Cable_Modeling_Profile` with allowed values:
- `Core` (default): connections carry the plain `Connection_Data.Cable_Number` attribute. `A.O3 Cable_Data` is absent and `Connection_ID.Cable_Data_ID` remains null. I25 operates in Core mode. This profile is the recommended default for projects that do not need cable-asset modeling.
- `Asset`: `A.O3 Cable_Data` sheet is present and `Connection_ID.Cable_Data_ID` may be populated. I25 operates in Asset mode. Use this profile when projects require cable inventory, route assignment, or cable-level attribute tracking.

`Element_Type=Cable` is not an active canonical value in v0.8. Workbooks SHALL NOT instantiate cable assets as `Element_ID` rows unless a future schema revision explicitly activates that modeling pattern. Cable-as-asset modeling in v0.8 is represented only through the optional `A.O3 Cable_Data` profile.


---

## B. Appendix: Relocated Historical and Migration Material (v0.8.2)

The following material was relocated verbatim from the main body in the v0.8.2 structure patch. Original numbering and wording are retained so that all existing cross-references (e.g. §3.5, §17) continue to resolve. Normative obligations stated below (e.g. migration behavior of tools) remain normative.

### B.1 Sheet-count note (formerly in §3.0)

> **Note on sheet count:** v0.4 had 23 sheets. v0.5 added `Connection_Data` and `Connection_Data_Source`, and renamed the v0.4 `Connection_Data` stem-sheet to `Connection_ID`. v0.6 consolidated the schema to **28 mandatory sheets** by adding `Document_Data_Source`, `Revision_Data_Source`, and `Element_Classification_Source`. Optional sheets remain project-specific extensions and do not change mandatory conformance.

### B.2 Rename note `PDF_Operation` → `Source_Operation` (formerly in §3.0)

**Rename note:** The Object-sheet column historically named `PDF_Operation` (v0.4/v0.5) is renamed to **`Source_Operation`** in v0.6. The value space is now a closed enum (per §9.3 Authoritative Seed Catalog) covering both PDF content-stream operators (`Tj`, `TJ`, `'`, `"`, `f`, `F`, `f*`, `S`, `s`, `B`, `b`, `re`) and non-PDF source-format markers (`Cell`, `VL_Row`, `Manual_Entry`); see §9.3 for the authoritative complete set. Tools migrating from earlier versions SHALL rename the column on read.

### 3.5 Historical: Impact of the v0.4→v0.5 Connection_Data → Connection_ID Rename on Pre-v0.5 I-Rules

The rename of `Connection_Data` to `Connection_ID` (§3.1) touches one v0.4 I-rule formulation that mentions the old sheet by name:

**Affected rule — I15 (Document_ID FK validity):**

**v0.4 original text (shortened):**
> Every Document_ID foreign-key reference (in `Document_Data`, `Revision_Data`, `Document_RepresentedItem`, `Object`, `Cluster`, `Elements_TopDown`, `Elements_from_Cluster`, `Match_Result`, `Element_ID`, **`Connection_Data`**, `Element_Classification`, `Layer_ID`) must point to an existing `Document_ID` entry.

**v0.5 interpretation:** The sheet listing is **transitively updated** by the sheet rename. In v0.5, I15 reads:

> Every Document_ID foreign-key reference (in `Document_Data`, `Revision_Data`, `Document_RepresentedItem`, `Object`, `Cluster`, `Elements_TopDown`, `Elements_from_Cluster`, `Match_Result`, `Element_ID`, **`Connection_ID`**, `Element_Classification`, `Layer_ID`) must point to an existing `Document_ID` entry.

**Rationale:** The new `Connection_Data` (attribute sheet, §3.2) and `Connection_Data_Source` (§3.3) carry **no** Document_ID column; they are document-bound only indirectly via `Connection_Data.Connection_ID → Connection_ID.Document_ID`. The direct FK holder is therefore `Connection_ID` (formerly `Connection_Data`). The I15 enumeration of sheets to be checked is updated accordingly.

**Validator implementation:** Validators that process v0.5 Excel files must use the updated sheet list. On the v0.4→v0.5 migration path, the listing is mechanically substituted (`Connection_Data` → `Connection_ID`). No content change to the rule, only name adjustment.

In the Rules sheet of the v0.5 Excel, the I15 description is entered with `Connection_ID` (not `Connection_Data`).

No other v0.4 I-rule references the renamed sheet by name; all other rules apply unchanged.

### 3.6 Historical: Impact of the v0.4→v0.5 German→English Language Migration on Pre-v0.5 Rule Texts

The German→English schema-value migration (§17) affects not only data values in the Lookup and Data sheets, but also the **example values cited in the wording of several v0.4 rules**. These rule texts continue to apply unchanged in content; only the **schema-classification example values** they cite are transitively updated to their English equivalents per §17. **Source-extracted example values** (positional designations, function codes such as `TU10.F17`, `FIC`, RKZ strings) remain unchanged in accordance with §0.1.

The following v0.4 rule texts are affected:

| v0.4 Rule / Section | German example value cited | v0.5 reading |
|---|---|---|
| K4 — Enum disambiguation via Field_Name | `PCE-Aufgabe` exists for both `Field_Name=RepresentedItem_Type` and `Field_Name=Element_Type` | `PCE_Request` exists for both `Field_Name=RepresentedItem_Type` and `Field_Name=Element_Type` |
| S1 — Stellenplan/Instrument_Loop_Diagram RKZ | `Document_Type=Stellenplan`; example `Position=TU10.F17`, `Function=FIC` → `Primary_RKZ=TU10.F17.FIC` | `Document_Type=Instrument_Loop_Diagram`; example `Position=TU10.F17`, `Function=FIC` → `Primary_RKZ=TU10.F17.FIC` (source-extracted values unchanged) |
| S2 — Klemmenplan/Terminal_Diagram | `Document_Type=Klemmenplan` | `Document_Type=Terminal_Diagram` |
| Attribute_Lookup (§9.2) — Element_Type free-form clarification | `Element_Type=SPS-Modul` | `Element_Type=PLC_Module` |
| Attribute_Lookup (§9.2) — Type_Constraint example values | `Document_Type=Stellenplan`, `Element_Type=SPS-Modul`, `RepresentedItem_Type=PCE-Aufgabe` | `Document_Type=Instrument_Loop_Diagram`, `Element_Type=PLC_Module`, `RepresentedItem_Type=PCE_Request` |
| v0.4-§14 — Element_Type overview table | `SPS-Modul, Klemme, Umformer, Aufnehmer` | `PLC_Module, Terminal, Transducer, Sensor` (the v0.5 equivalent is §5.12 and is already in English) |

**Validator implementation:** Validators that interpret v0.4 rule texts symbolically (rather than by string-matching their example values) are unaffected. Validators that string-match rule examples must update those examples to the English equivalents per §17. The rule content (logical predicate) is unchanged in every case.

**Rationale:** This section makes explicit, alongside §3.5 (sheet-rename impact), the second transitive consequence of v0.5's restructuring: the language migration of schema values cascades into v0.4 rule texts that cite those values as examples. Distinguishing schema-classification values (migrated) from source-extracted values (unchanged) follows the §0.1 separation strictly.

---

## 17. Term Migration v0.4 → v0.5 (German → English)

Schema v0.5 harmonizes all schema values (Lookup strings, Element_Type, RepresentedItem_Type, Attribute_Name, enum values) on English. The v0.4 implementation had several German values (legacy from the original German-language project context). The migration is mechanical and content-preserving: each German value is replaced by its English equivalent per the table below. The structural data (sheets, columns, rows) remain identical.

### 17.1 Element_Type

| v0.4 (German) | v0.5 (English) | Norm reference |
|---|---|---|
| PCE-Aufgabe | PCE_Request | IEC 62424 (CAEX RoleClass already uses this name) |
| SPS-Modul | PLC_Module | IEC 61131 |
| Klemme | Terminal | IEC 60617-3 |
| Klemmleiste | Terminal_Strip | IEC 60617-3 |
| Umformer | Transducer | IEC 60050-351 |
| Aufnehmer | Sensor | IEC 60050-351-44-04 |
| Schütz | Contactor | IEC 60947-4-1 |
| Hilfsschütz | Auxiliary_Contactor | IEC 60947-4-1 |
| Sicherung | Fuse | IEC 60269 |
| Schutzschalter | Circuit_Breaker | IEC 60898-1 |
| Schalter | Switch | IEC 60947 |
| Steckdose | Socket_Outlet | IEC 60884 |
| Netzteil | Power_Supply | IEC 61204 |
| Ventil_Aktor | Valve_Actuator | IEC 60534 |
| Heizung | Heater | – |

### 17.2 RepresentedItem_Type

| v0.4 (German) | v0.5 (English) | Norm reference |
|---|---|---|
| PCE-Aufgabe | PCE_Request | IEC 62424 |
| Klemmleiste | Terminal_Strip | IEC 60617-3 |
| Stromkreis | Circuit | IEC 60617 |
| Schaltschrank | Control_Cabinet | IEC 61439 |
| Verteilung | Distribution_Panel | IEC 61439 |
| Funktionsgruppe | Function_Group | IEC 81346-1 |

### 17.3 Document_Type

| v0.4 (German) | v0.5 (English) | Norm reference |
|---|---|---|
| Stellenplan | Instrument_Loop_Diagram | IEC 62424 |
| Klemmenplan | Terminal_Diagram | IEC 61082-1 |
| Stromlaufplan | Circuit_Diagram | IEC 60617, IEC 61082-1 |
| Geraetebeschreibung | Equipment_Datasheet | – |

### 17.4 Attribute_Name (Selection)

| v0.4 (German) | v0.5 (English) |
|---|---|
| PCE_Kategorie | PCE_Category |
| Verarbeitungsfunktion | Processing_Function |
| Ort_Bedienoberflaeche | Operating_Interface_Location |
| Messgroesse | Measured_Variable |
| Messeinheit | Measurement_Unit |
| Messprinzip | Measurement_Principle |
| Hersteller | Manufacturer |
| Typ_Bezeichnung | Type_Designation |
| Modul_Typ | Module_Type |
| Kanal | Channel |
| Adresse | Address |
| Steckplatz | Slot |
| Baugruppen_Art | Module_Category |
| Anschluss_Nummer | Terminal_Number |
| Klemmleisten_Bezeichnung | Terminal_Strip_Designation |
| Polarität | Polarity |
| Klemmen_Typ | Terminal_Type |
| Nenn_Querschnitt | Rated_Cross_Section |
| Nennspannung / Bemessungsspannung | Rated_Voltage |
| Nennstrom / Bemessungsstrom | Rated_Current |
| Anzahl_Klemmen | Terminal_Count |
| Funktion | Function |
| Position_im_Schrank | Position_in_Cabinet |
| Klemmen_System | Terminal_System |
| Spulen_Spannung | Coil_Voltage |
| Bemessungsbetriebsstrom | Rated_Operational_Current |
| Anzahl_Hauptkontakte | Main_Contact_Count |
| Anzahl_Hilfskontakte_NO | Aux_Contact_NO_Count |
| Anzahl_Hilfskontakte_NC | Aux_Contact_NC_Count |
| Gebrauchskategorie | Utilization_Category |
| Ziel_Verbraucher | Target_Load |
| Auslösecharakteristik | Trip_Characteristic |
| Bauform | Protection_Form |
| Anzahl_Pole | Pole_Count |
| Bemessungsschaltvermögen | Rated_Breaking_Capacity |
| Auslösestrom_Fehlerstrom | Trip_Current_Residual |
| Typ_Fehlerstrom | Residual_Current_Type |
| Schaltertyp | Switch_Type |
| Steckdosentyp | Socket_Type |
| Schutzart | IP_Protection |
| Montageart | Mounting_Type |
| Eingangsspannung | Input_Voltage |
| Ausgangsspannung | Output_Voltage |
| Ausgangsleistung | Output_Power |
| Ausgangsstrom | Output_Current |
| Schaltungstopologie | Circuit_Topology |
| Schrank_Hersteller | Cabinet_Manufacturer |
| Schrank_Typ | Cabinet_Type |
| Abmessungen_HxBxT | Dimensions_HxWxD |
| Anzahl_Klemmleisten | Terminal_Strip_Count |
| Spannungsebene | Voltage_Level |
| Aderfarbe | Wire_Color |
| Aderfarbe_Sekundär | Wire_Color_Secondary |
| Querschnitt | Cross_Section |
| Adernummer | Wire_Number |
| Kabel_Nummer | Cable_Number |
| Kabel_Bauform | Cable_Type |
| Adernzahl_Gesamt | Total_Wire_Count |
| Schirmung | Shielding |
| Verbindungs_Art | Connection_Type |
| Länge | Length |
| Anschluss_Punkt_From | Connection_Point_From |
| Anschluss_Punkt_To | Connection_Point_To |
| Bemerkung | Remark |

### 17.5 Enum Values (Selection)

| v0.4 (German) | v0.5 (English) | Field_Name |
|---|---|---|
| Brücke_Querbrücke_fest | Bridge_Cross_Fixed | Connection_Type |
| Brücke_Querbrücke_steckbar | Bridge_Cross_Pluggable | Connection_Type |
| Brücke_isoliert | Bridge_Insulated | Connection_Type |
| Brücke_Längs | Bridge_Longitudinal | Connection_Type |
| Ader | Wire | Connection_Type |
| Reihenklemme | FeedThrough_Terminal | Terminal_Type |
| Doppelstockklemme_intern_verbunden | DoubleLevel_Terminal_Internal_Connected | Terminal_Type |
| Doppelstockklemme_intern_getrennt | DoubleLevel_Terminal_Internal_Separated | Terminal_Type |
| Mehrstockklemme | MultiLevel_Terminal | Terminal_Type |
| Trennklemme | Disconnect_Terminal | Terminal_Type |
| Steckklemme | Pluggable_Terminal | Terminal_Type |
| Federkraftklemme | SpringClamp_Terminal | Terminal_Type |
| Schraubklemme | Screw_Terminal | Terminal_Type |
| Hauptschalter | Main_Switch | Switch_Type |
| Drehschalter | Rotary_Switch | Switch_Type |
| Wahlschalter | Selector_Switch | Switch_Type |
| Druckknopf_NO | Push_Button_NO | Switch_Type |
| Druckknopf_NC | Push_Button_NC | Switch_Type |
| Schluesselschalter | Key_Switch | Switch_Type |
| Not_Aus | Emergency_Stop | Switch_Type |
| Schmelzsicherung_NH | Fuse_NH | Protection_Form |
| Schmelzsicherung_Diazed | Fuse_Diazed | Protection_Form |
| LS_Schalter | MCB | Protection_Form |
| FI_LS | RCBO | Protection_Form |
| FI_Schalter | RCD | Protection_Form |
| 230V_AC_Einspeisung | 230V_AC_Supply | Voltage_Level |
| 230V_AC_Verteilung | 230V_AC_Distribution | Voltage_Level |
| 24V_DC_Einspeisung | 24V_DC_Supply | Voltage_Level |
| 24V_DC_Verteilung | 24V_DC_Distribution | Voltage_Level |
| Signalleitung_Analog | Signal_Line_Analog | Voltage_Level |
| Signalleitung_Digital | Signal_Line_Digital | Voltage_Level |
| Steuerung | Control | Layer_Description |
| Signalanpassung | Signal_Conditioning | Layer_Description |
| Rangierverteiler | Marshalling | Layer_Description |
| Feldverteiler | Field_Distribution | Layer_Description |

Polarity codes (L1, L2, L3, N, PE, PEN, L+, L-, G+, G-, V+, V-, FE, AC, DC), cable codes (NYM, NYY, H07V-K, LiYCY, …), and IEC 81346-2 classification letters (A, B, …, Y) are international by IEC convention and remain unchanged.

### 17.6 Migration Path for Existing v0.4 Documents

For TU10F17 (existing v0.4 implementation) and any other v0.4-conformant documents, the migration is mechanical:

1. **Sheet rename:** `Connection_Data` → `Connection_ID`
2. **Add new sheets** (empty): `Connection_Data` (attribute sheet), `Connection_Data_Source`
3. **Replace values** in lookup-bound columns according to the tables in §17.1–§17.5
4. **Update Schema_Metadata:** `Schema_Version=v0.5`, `Lookup_Version=v0.5.0`
5. **Update I15 rule text** in the Rules sheet (Connection_Data → Connection_ID, see §3.5)
6. **Update v0.4 rule-text example values** in the Rules sheet (K4, S1, S2) and the affected carried-over Attribute_Lookup (§A.24) / overview-table wording per §3.6: replace German schema-classification example values with the English equivalents from §17.1–§17.5. The v0.6 equivalent of the v0.4 overview table is §5.12 (already in English). **Source-extracted example values** (positional designations, function codes such as `TU10.F17`, `FIC`) remain unchanged. No content change to any rule predicate; only example wording is updated.
7. **Re-run validator** (all 22 v0.4 I-rules + 3 new I23–I25 must pass = 25/25 for TU10F17)

No data is lost; no semantic change occurs. The migration is reversible by applying the §17 tables in reverse, with one exception: the **Wire_Color encoding** (e.g. source word `rot` → code `RD`) is not uniquely reversible at the value-mapping level because multiple source words (`rot`, `red`) can encode to the same code. However, the original source word remains accessible via provenance (`Connection_Data_Source → Object.Content_Text`, see §0.1 and §3.3); the reversal path is therefore provenance-based rather than table-based. All other migrated values are reversible by direct table inversion of §17.1–§17.5.

---
