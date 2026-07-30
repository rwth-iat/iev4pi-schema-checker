# Seeded Non-Conformant Variants

These 12 workbooks are deliberately corrupted copies of the three example
artefacts in `artefacts/Standardized Intermediate/`, used in the paper's
Feasibility Assessment (§5) to confirm that the checker actually enforces
its constraints rather than passing everything. Each variant introduces
exactly one deliberate defect; the corresponding report in
`results/Seeds/` shows the checker detecting and localizing it.

They are **not** picked up by `python schema_conformance_checker.py` run
without arguments (that scans `artefacts/Standardized Intermediate/` only).
To check one directly:

```
python schema_conformance_checker.py artefacts/Seeds/single_violation/seed_A_ObjectType_Terminal_Diagram.xlsx
```

## single_violation/ -- one variant per rule family (§11 A/C/M/P/E/K/I/S)

| File | Base workbook | Mutation | Expected detection |
|---|---|---|---|
| `seed_A_ObjectType_Terminal_Diagram.xlsx` | Terminal Diagram | `Object.Object_Type` cleared on one already-clustered Object row | P1 process-step post-condition: NOT SATISFIED (no dedicated finding-level rule for A-family) |
| `seed_C_ContainmentContainer_Circuit_Diagram.xlsx` | Circuit Diagram | A `Proximity` cluster redeclared as `Cluster_Type=Containment` with `Container_Object_ID` pointing at a `Text` object (not a closed `Graphic`) | `I17` FAIL |
| `seed_M_MatchedIncomplete_Terminal_Diagram.xlsx` | Terminal Diagram | `Element_from_Cluster_ID` nulled on a `Match_Status=Matched` row | `I2` FAIL (plus coupled P5 non-satisfaction: the orphaned cluster candidate is no longer matched) |
| `seed_P_DerivationStatusMissing_Circuit_Diagram.xlsx` | Circuit Diagram | `Derivation_Status` cleared on an `Elements_from_Cluster` row | P4 process-step post-condition: NOT SATISFIED (no dedicated finding-level rule for P-family) |
| `seed_E_UnspecifiableNoSource_Terminal_Diagram.xlsx` | Terminal Diagram | New `Element_Data` row with `Attribute_Value=Unspecifiable` added without a matching `Element_Data_Source` row | `I12`/D6 FAIL (E5's "Unspecifiable still needs a Source row" convention) |
| `seed_K_DuplicatePrimaryMapping_Circuit_Diagram.xlsx` | Circuit Diagram | Second `Element_RepresentedItem_Mapping` row with `Relationship_Type=Primary` added for an Element that already has one | `I22` FAIL (K3 single-source-of-truth violated at the Primary link) |
| `seed_I_DocumentIDUnresolved_Instrument_Loop_Diagram.xlsx` | Instrument Loop | `Revision_Data.Document_ID` set to a non-existent `Document_ID` | `I15` FAIL |
| `seed_S_InvalidPCEChannelSuffix_Instrument_Loop_Diagram.xlsx` | Instrument Loop | `Element_Data` row with `Attribute_Name=PCE_Channel_Suffix` (an S1-defined field) set to a value outside its `Enum_Lookup` catalog | `I14` FAIL |

Two of the eight (A, P) surface only through a process-step post-condition
flipping from SATISFIED to NOT SATISFIED, not through the FAIL/violations
list -- both families have no dedicated finding-level rule in this checker
version. This is a property of the checker's implemented scope, not a
detection failure.

## dual_path/ -- dual-path safety-net refusal (§11.3 M3/M4)

Each variant takes one `Match_Status=Matched` record, removes one side of
the match (the `Elements_TopDown` or `Elements_from_Cluster` candidate),
flips the record to the corresponding single-path status
(`Only_TopDown`/`Only_Cluster`) with `Resolution_Status=Open`, and
cascade-deletes the `Element_ID` that had been consolidated from that
match together with everything depending on it (`Element_Data`,
`Element_Classification`, `Element_RepresentedItem_Mapping`,
`Connection_ID` endpoints, and any child `Element_ID` rows) -- simulating
what a conformant tool must do once a previously dual-path-confirmed match
becomes single-path and unresolved again.

| File | Base workbook | Side removed | Elements cascaded |
|---|---|---|---|
| `seed_DualPath_TopDownRemoved_Instrument_Loop_Diagram.xlsx` | Instrument Loop | Elements_TopDown | 1 |
| `seed_DualPath_TopDownRemoved_Terminal_Diagram.xlsx` | Terminal Diagram | Elements_TopDown | 1 |
| `seed_DualPath_ClusterRemoved_Circuit_Diagram.xlsx` | Circuit Diagram | Elements_from_Cluster | 7 |
| `seed_DualPath_ClusterRemoved_Terminal_Diagram.xlsx` | Terminal Diagram | Elements_from_Cluster | 1 |

All four are detected via `I20` FAIL ("terminal status required") plus the
P6 process-step post-condition (and P4 for the cluster-removed pair, since
the removed cluster candidate was that Cluster's only derivation).
