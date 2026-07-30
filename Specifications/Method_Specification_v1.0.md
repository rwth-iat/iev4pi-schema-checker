# Method Specification — Traceable and Verifiable Extraction from Engineering Documents

| Field | Value |
|---|---|
| Document | Method Specification (technology- and document-independent) |
| Version | v1.0 |
| Status | Normative foundation |
| Scope | The general extraction-and-transformation method |
| Relationship to schema specifications | This document defines the method. A schema specification (e.g. Schema Specification v0.8.2) is one *instantiation* of this method for a concrete set of document families, carriers, and catalogs. Where the two differ, this document governs the method; the schema specification governs its instantiation. |
| Independence | This specification fixes *what* an application must produce and *which properties* the result must satisfy. It does not prescribe an extraction technology, a physical carrier, a document family, or a downstream use. Those are instantiation choices. |

**Reading hint.** This specification is self-contained. It defines the conceptual functions, the process, the formal method record, the obligations, and the conformance model of the extraction method. Terms such as *workbook*, *sheet*, *row*, or a specific rule identifier belong to an instantiation and appear here only as non-normative examples.

---

## 1. Purpose and Scope

### 1.1 Purpose

The method defines extraction as the **controlled derivation of structured engineering information from document-bound source content**. It separates five conceptual functions — source capture, element identification, reconciliation, consolidation, and engineering structuring — and fixes the intermediate results, obligations, and conformance criteria that make the derivation traceable and independently verifiable.

### 1.2 What the method fixes and what it leaves open

The method fixes:

- the conceptual functions (§3) and the process that operationalizes them (§4);
- the structure of the method record and its formal constraints (§5);
- the obligations every application must satisfy (§6);
- the layered conformance model (§7).

The method leaves open, as **instantiation choices** (§8):

- the extraction *technology* (e.g. LLM-based classification, deterministic parsing, or any combination);
- the *document family* and its source-object definition;
- the *physical carrier* of the method record (e.g. a workbook, a graph, an object model);
- the *catalogs and normative anchors* that bind enumerated values to defining standards;
- the *downstream use* of the produced engineering representation.

### 1.3 Two guiding properties

Two properties are used throughout and are the ultimate targets of the obligations in §6.

- **Traceability.** Source relations are retained across all intermediate results, so that every structured value can be followed back to the source objects and the extraction decisions that produced it.
- **Verifiability.** Conformance to the specification is decidable from the produced artifact and the specification alone, without access to the producing implementation.

---

## 2. Terms and Definitions

| Term | Definition |
|---|---|
| **Document** | A single engineering document that is the sole source for one method record. |
| **Document context** | The identification, descriptive/revision information, and the engineering subject a document represents; it scopes top-down identification and the interpretation of captured content. |
| **Source object** | An addressable unit retained from the document — a text unit, graphical primitive, table cell, structured node, or equivalent. Its concrete definition depends on the document family. |
| **Synthetic source object** | A source object recorded for a manual, rule-derived, or norm-derived value. It carries an explicit **operation marker** that distinguishes it from a captured source object while still terminating a traceability path. |
| **Cluster** | A grouping of source objects induced by document structure, used by the cluster-based identification path. |
| **Top-down candidate** | An engineering element proposed by the top-down identification path. |
| **Cluster-based candidate** | An engineering element proposed by the cluster-based identification path. |
| **Match record** | A pairing that references a candidate from either or both identification paths. |
| **Resolution state** | The status assigned to a match record: undecided, accepted (terminal), or rejected (terminal). |
| **Consolidated element** | An engineering element admitted from an accepted match record. |
| **Engineering structuring** | The derivation of classifications, attributes, and connections from the consolidated element set. |
| **Traceability relation** | The relation linking every derived record to a source object, directly or transitively. |
| **Instantiation** | A concrete application of this method to one or more document families, fixing technology, carrier, source-object definition, catalogs, and anchors. |

---

## 3. Conceptual Functions

The method comprises five conceptual functions. It prescribes no particular extraction technology, document representation, or downstream use; these are defined when the method is applied to a document family (§8).

### 3.1 Document context

Before source-object capture, an application establishes the **document context**. The context identifies the document, retains its descriptive and revision information, and records the engineering subject it represents. It thereby provides the basis for top-down identification and the scope within which captured source content is interpreted.

### 3.2 Complete source capture

Complete source capture establishes the document-bound basis of the method. A **source object** is an addressable unit retained from the document. Capture is **complete**: every atomic source unit of the document is retained as a source object. Source objects are retained rather than replaced by the engineering information derived from them, so that a decision can later be reviewed against what the document stated.

A value that is not extracted from the document but introduced manually, by rule, or by norm is recorded as a **synthetic source object** carrying an explicit operation marker. Such values remain distinguishable from extracted ones while still satisfying traceability.

### 3.3 Element identification along two structurally distinct paths

Element identification is performed **twice**, by two methods that differ in their **starting point**.

- The **top-down path** starts from the engineering objects the document context announces and searches for supporting source objects.
- The **cluster-based path** starts from the captured source objects, groups them by document structure, and derives candidates from these groups.

Because neither starting point reveals every element, both candidate sets are produced **independently** and remain **separate** until their correspondence has been assessed. Their comparison then serves as a **mutual cross-check**: an element found by only one path becomes an explicit unmatched candidate instead of a silent omission.

### 3.4 Reconciliation

Candidate comparison determines agreements and deviations between the two identification results. **No candidate enters the consolidated element set before its match or deviation status is resolved.** Reconciliation assigns every match record a terminal resolution state (§5.4).

### 3.5 Consolidation and engineering structuring

Only resolved and accepted candidates are consolidated into engineering elements. Classifications, attributes, and connections are derived **only** from the consolidated set. Source relations are retained across all intermediate results, so that each structured result remains traceable to the document content and the decisions that produced it.

---

## 4. Process

The five conceptual functions are operationalized as **ten process steps, P0–P9**, with the dependencies given below. Step *purposes* are normative; the artifact names in the "typical instantiation" column are illustrative and belong to a schema specification, not to this document.

| Step | Purpose (normative) | Precondition | Postcondition |
|---|---|---|---|
| **P0** | Establish the document context: identify the document, capture descriptive and revision information, record the represented engineering subject; seed the synthetic source objects backing any manually entered context values. | Source available; catalogs/anchors seeded | Document identified; context and revision information present; every context value has a provenance link to a source object. |
| **P1** | **Complete** source-object capture: retain every atomic source unit of the document as a source object. A stub or partial capture is not conformant. | P0 complete | All source content captured as source objects with valid type and, where applicable, positional metadata. |
| **P2** | Top-down identification: identify the main elements by domain-knowledge-driven classification of source content against the cited symbol/function norms. The classification mechanism is technology-independent. | P0 complete; context populated | Top-down candidate set populated, or an explicit empty-set acknowledgment. |
| **P3** | Cluster formation: group source objects by the applicable cluster regime for the source format (intrinsic-structure regime for structured sources; geometric/containment regimes for unstructured sources). An empty result is admissible **only** when documented as such. | P1 complete | Clusters formed, or an explicitly documented empty cluster result. |
| **P4** | Cluster-based derivation: derive one candidate per cluster by identifier-pattern matching and type inference. Where no element is derivable, set an explicit *no-element-derivable* status. | P3 complete | Cluster-based candidate set with an explicit derivation status per cluster. |
| **P5** | Matching: pair top-down and cluster-based candidates. Each candidate appears in at least one match record; match status reflects the actual outcome (matched, top-down-only, cluster-only). | P2 **and** P4 complete | Every candidate referenced by at least one match record. |
| **P6** | Reconciliation: resolve every match record to a **terminal** resolution state — automatic, tool/operator-corrected, or explicitly rejected. The mechanism and the resolving agent are recorded per record. | P5 complete | No match record remains undecided. |
| **P7** | Consolidation: admit one consolidated element per accepted match record. | P6 complete | Consolidated element set populated; every element traces to an accepted match record. |
| **P8** | Engineering structuring — classification and attributes: derive classifications and attributes for consolidated elements, each with recorded provenance. | P7 complete; catalogs available | Required classifications and attributes populated; provenance recorded for each. |
| **P9** | Engineering structuring — connections: derive connections between consolidated elements from source topology, each with recorded provenance. | P7 complete; topology available in source | Connections populated; provenance recorded for each. |

**Ordering.** P0 precedes all others. P1 and P2 may proceed in parallel or in either order after P0. P3 and P4 form the cluster-based path and depend on P1. P5 requires **both** P2 and P4. P6 precedes P7; P8 and P9 depend on P7.

---

## 5. Formal Method Record

The conceptual workflow is formalized as a **document-dependent method record**. For an engineering document *D*:

$$
\mathcal{F}_D = \left( S_D,\; K_D,\; E_D^{\mathrm{TD}},\; E_D^{\mathrm{CB}},\; M_D,\; R_D,\; E_D^{\mathrm{C}},\; G_D,\; T_D \right). \tag{1}
$$

### 5.1 Source objects

$S_D$ holds the source objects of the document, comprising both the objects **captured** from the document and the **synthetic** objects recorded for manual, rule-derived, and norm-derived values. Every synthetic object carries an operation marker (§3.2).

### 5.2 Clusters and candidate sets

$K_D$ holds the document-dependent clusters. $E_D^{\mathrm{TD}}$ and $E_D^{\mathrm{CB}}$ hold the top-down and cluster-based candidates, respectively. The two sets are produced independently and are not merged before reconciliation.

### 5.3 Match records

The match records $M_D$ each reference a candidate from either or both sets. Using $\bot$ for a missing reference, the admissible structure is

$$
M_D \subseteq \left[ \left( E_D^{\mathrm{TD}} \cup \{\bot\} \right) \times \left( E_D^{\mathrm{CB}} \cup \{\bot\} \right) \right] \setminus \left\{ (\bot,\bot) \right\}. \tag{2}
$$

Relation (2) represents matched, top-down-only, and cluster-only candidates **without merging the sets**. The exclusion of $(\bot,\bot)$ forbids empty match records.

### 5.4 Resolution

The resolution function $R_D$ assigns to every match record exactly one state from

$$
\mathcal{S} = \{\mathrm{Open}\} \cup \mathcal{A}_D \cup \mathcal{X}_D,
$$

where $\mathcal{A}_D$ are the **accepted** terminal states and $\mathcal{X}_D$ the **rejected** terminal states. A record in $\mathrm{Open}$ is undecided; a record in $\mathcal{A}_D$ contributes to consolidation; a record in $\mathcal{X}_D$ is retained as a documented non-acceptance.

### 5.5 Consolidation

The consolidated element set is constrained by

$$
\begin{aligned}
&\forall m \in M_D \colon R_D(m) \neq \mathrm{Open}, \\
&E_D^{\mathrm{C}} = \operatorname{consolidate}\left( \left\{ m \in M_D \mid R_D(m) \in \mathcal{A}_D \right\} \right),
\end{aligned} \tag{3}
$$

where $\operatorname{consolidate}$ maps the accepted match records **bijectively** onto $E_D^{\mathrm{C}}$, so that no accepted record is merged with another and no accepted record is silently dropped. The first line of (3) makes reconciliation completion a **precondition** of consolidation.

### 5.6 Engineering structuring and traceability

$G_D$ contains the classifications, attributes, and connections derived from $E_D^{\mathrm{C}}$. The traceability relation $T_D$ links every derived record to its source basis: for every result $x$, a traceability path must terminate at a source object,

$$
\forall x \in G_D \; \exists s \in S_D \colon x \, T_D^{+} \, s, \tag{4}
$$

where $T_D^{+}$ is the transitive closure of $T_D$. Because $S_D$ contains synthetic as well as captured objects, a manual, rule-based, or norm-derived decision terminates a path like extracted content while remaining distinguishable through its operation marker.

---

## 6. Obligations

The method record imposes four obligations. An application satisfies the method only if all four hold.

- **(i) Source separation.** Source content shall remain separate from normalized engineering information.
- **(ii) Path distinguishability.** The top-down and cluster-based candidate sets shall remain distinguishable until matching and resolution are complete.
- **(iii) Resolution before consolidation.** Consolidation shall begin only after every match record has reached a terminal resolution state, and only accepted resolutions shall contribute to the consolidated element set.
- **(iv) Explicit gaps.** Absent, non-extractable, rejected, and unresolved information shall remain explicit rather than represented by undocumented empty values.

These obligations operationalize the traceability and verifiability properties of §1.3: (i) and (iv) protect traceability of what the document stated; (ii) and (iii) protect the integrity of the dual-path cross-check.

---

## 7. Conformance Model

Conformance is separated into **three levels** so that claims about an artifact remain distinguishable from claims about the producing tool.

- **Level 1 — Artifact conformance.** Assessable from the produced artifact and this specification alone. An application conforms at Level 1 when
  1. the required intermediate results of the method record (§5) are represented,
  2. the four obligations (§6) are satisfied, and
  3. every derived result retains an assessable source basis per (4).

  Level 1 requires no access to the producing implementation. This is the level at which **verifiability** (§1.3) is defined.

- **Level 2 — Source-extraction capability.** Concerns whether the producing implementation captures source content completely and correctly. Requires evidence about the implementation.

- **Level 3 — Classification capability.** Concerns whether the producing implementation classifies and structures elements correctly. Requires evidence about the implementation.

Levels 2 and 3 are out of scope for an artifact-only assessment; a Level-1-conformant artifact may be produced by an implementation of unknown Level-2/Level-3 capability (e.g. a manually authored artifact is Level-1 assessable without the producer having any automated capability).

**Conformance is not correctness.** A Level-1-conformant artifact establishes structural compliance and traceability, **not** extraction accuracy or semantic correctness. A value that is well-formed and fully provenanced but factually wrong (e.g. a valid norm code assigned to the wrong element) remains conformant. The method makes such a value **reviewable**; it does not determine whether it reflects the actual plant state.

---

## 8. Instantiation

An **instantiation** applies this method to one or more document families. A schema specification (e.g. Schema Specification v0.8.2) is such an instantiation. An instantiation SHALL fix, and SHALL NOT contradict this document in fixing:

1. **Document families** in scope, and for each the concrete definition of a **source object** (§3.2).
2. **Source-object capture conventions** per source format that realize the completeness requirement of P1.
3. **Cluster regimes** per source format that realize P3, including the conditions for a documented empty result.
4. **Identifiers, classifications, attributes, and connections** admissible for each family.
5. **Normative anchors** binding enumerated values to defining standards, with the original source term preserved in the corresponding source object (norm anchoring; see §9).
6. A **physical carrier** for the method record (§5) in which the intermediate results and their relations remain distinguishable and independently checkable.
7. **Matching and resolution mechanisms** realizing P5 and P6, each recording the mechanism and resolving agent.

An instantiation MAY add family-specific constraints, catalogs, and optional structures, provided they do not weaken any obligation (§6) or the Level-1 assessability of the artifact (§7). An instantiation MUST NOT introduce a second process model in place of P0–P9; catalogs and control structures provide predefined constraints, not additional process outputs.

---

## 9. Norm Anchoring (Instantiation Rule)

Where an application uses enumerated values, norm anchoring applies: the **original source wording is preserved** in the source object, while the enumerated value is stored as a **language-neutral code** whose catalog entry names the defining standard, linked to the source object by provenance.

*Example (non-normative).* A conductor annotated `rot` in a German source keeps `rot` in its source object; the classified value is the language-neutral IEC 60757 code `RD`; the catalog entry for `RD` names IEC 60757 as the defining standard. Nothing is translated — the source word stays, the schema value is encoded.

This rule ensures that norm-derived values satisfy obligation (i) (source separation) and the traceability property, because the derivation from source term to norm code remains explicit and reviewable.

---

## 10. Relationship to the Paper and to the Schema Specification

- The **paper** *"A General Method for Traceable and Verifiable Extraction from Engineering Documents"* presents this method (§3–§7 correspond to the paper's conceptual method, formal method record, obligations, and conformance model).
- The **Schema Specification v0.8.x** is one instantiation (§8) of this method for instrument loop diagrams, terminal diagrams, and circuit diagrams. Its 28 mandatory sheets, integrity rules, and enum/attribute catalogs realize the carrier, capture conventions, cluster regimes, anchors, and matching/resolution mechanisms required by §8. Where a term in the schema specification (sheet, row, rule identifier) has no counterpart here, it is an instantiation detail, not part of the method.
