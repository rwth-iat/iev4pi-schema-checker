#!/usr/bin/env python3
"""Minimal violate/satisfy fixtures for every new or changed
schema_conformance_checker.py rule.

Each test builds a tiny synthetic workbook (all 28 mandatory sheets, minimal
but structurally valid content) via openpyxl, runs checker.check() against
it, and asserts the resulting status of the rule under test. No new
dependencies; run with:

    python test_checker.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl

import schema_conformance_checker as c

SHEET_HEADERS = {
    "Rules": ["Rule_ID", "Rule_Category", "Rule_Name", "Rule_Description", "Rule_Reference", "Schema_Version_Introduced"],
    "Schema_Metadata": ["Index", "Metadata_Key", "Metadata_Value", "Description"],
    "Document_ID": ["Index", "Document_ID", "Document_Type", "Document_Filename", "Page_Count",
                    "Schema_Version", "Lookup_Version", "Created_Timestamp", "Created_By", "SemanticID"],
    "Document_Data": ["Index", "Document_Data_ID", "Document_ID", "Attribute_Name", "Attribute_Value",
                       "Raw_Value", "Normalized_Value", "Unit", "Quantity_Qualifier", "Parsing_Status", "SemanticID"],
    "Revision_Data": ["Index", "Revision_ID", "Document_ID", "Revision_Index", "Revision_Date",
                       "Revision_Author", "Revision_Description", "SemanticID"],
    "Document_RepresentedItem": ["Index", "RepresentedItem_ID", "Document_ID", "RepresentedItem_Type",
                                  "Primary_RKZ", "Parent_RepresentedItem_ID", "Topic_Identification_Status",
                                  "CAEX_RoleClass_Path", "CAEX_SystemUnitClass_Path", "SemanticID"],
    "Object": ["Index", "Object_ID", "Document_ID", "Page_Number", "Object_Type", "Source_Operation",
               "BBox_X1", "BBox_Y1", "BBox_X2", "BBox_Y2", "Content_Text", "Content_Font_Size",
               "Geometry_Type", "Geometry_Closed", "Topology_From_Object_ID", "Topology_To_Object_ID",
               "Topology_Validation_Status", "Object_Role", "SemanticID"],
    "Cluster": ["Index", "Cluster_ID", "Document_ID", "Parent_Cluster_ID", "Container_Object_ID",
                "Cluster_Type", "Cluster_BBox_X1", "Cluster_BBox_Y1", "Cluster_BBox_X2", "Cluster_BBox_Y2",
                "Cluster_Method", "Cluster_Parameter_Set", "SemanticID"],
    "Object_Cluster": ["Index", "Object_ID", "Cluster_ID", "Membership_Reason"],
    "Elements_TopDown": ["Index", "Element_TopDown_ID", "Document_ID", "Element_Name", "Primary_RKZ",
                          "Element_Type", "Parent_Element_TopDown_ID", "SemanticID"],
    "Elements_from_Cluster": ["Index", "Element_from_Cluster_ID", "Document_ID", "Source_Cluster_ID",
                               "Element_Name", "Primary_RKZ_Extracted", "Element_Type_Inferred",
                               "Derivation_Status", "SemanticID"],
    "Match_Result": ["Index", "Match_ID", "Document_ID", "Element_TopDown_ID", "Element_from_Cluster_ID",
                      "Match_Status", "Match_Rule", "Resolution_Note", "Resolution_Status", "Reviewed_By",
                      "Review_Status", "Correction_Reason", "Review_Timestamp", "SemanticID"],
    "Element_ID": ["Index", "Element_ID", "Document_ID", "Source_Match_ID", "Source", "Element_Type",
                    "Primary_RKZ", "Parent_Element_ID", "Layer_ID", "CAEX_Type", "CAEX_RoleClass_Path",
                    "CAEX_SystemUnitClass_Path", "CAEX_InterfaceClass_Path", "SemanticID"],
    "Element_RepresentedItem_Mapping": ["Index", "Mapping_ID", "Element_ID", "RepresentedItem_ID",
                                         "Relationship_Type", "SemanticID"],
    "Element_Data": ["Index", "Element_Data_ID", "Element_ID", "Attribute_Name", "Attribute_Value",
                      "Raw_Value", "Normalized_Value", "Unit", "Quantity_Qualifier", "Parsing_Status", "SemanticID"],
    "Element_Data_Source": ["Index", "Element_Data_ID", "Source_Object_ID", "Source_Role", "Extraction_Method",
                             "Confidence", "Reviewed_By", "Review_Status", "Correction_Reason",
                             "Extraction_Timestamp", "SemanticID"],
    "RepresentedItem_Data": ["Index", "RepresentedItem_Data_ID", "RepresentedItem_ID", "Attribute_Name",
                              "Attribute_Value", "Raw_Value", "Normalized_Value", "Unit", "Quantity_Qualifier",
                              "Parsing_Status", "SemanticID"],
    "RepresentedItem_Data_Source": ["Index", "RepresentedItem_Data_ID", "Source_Object_ID", "Source_Role",
                                     "Extraction_Method", "Confidence", "Reviewed_By", "Review_Status",
                                     "Correction_Reason", "Extraction_Timestamp", "SemanticID"],
    "Element_Classification": ["Index", "Classification_ID", "Document_ID", "Classified_Object_Type",
                                "Classified_Object_ID", "Classification_System", "Classification_Code",
                                "Classification_Description", "Source_Symbol_Reference", "SemanticID"],
    "Connection_ID": ["Index", "Connection_ID", "Document_ID", "From_Element_ID", "To_Element_ID",
                       "Source_Topology_Object_ID", "Connection_Status", "Cable_Data_ID", "SemanticID"],
    "Connection_Data": ["Index", "Connection_Data_ID", "Connection_ID", "Attribute_Name", "Attribute_Value",
                         "Raw_Value", "Normalized_Value", "Unit", "Quantity_Qualifier", "Parsing_Status", "SemanticID"],
    "Connection_Data_Source": ["Index", "Connection_Data_ID", "Source_Object_ID", "Source_Role",
                                "Extraction_Method", "Confidence", "Reviewed_By", "Review_Status",
                                "Correction_Reason", "Extraction_Timestamp", "SemanticID"],
    "Layer_ID": ["Index", "Layer_ID", "Document_ID", "Layer_Description", "Layer_Type", "Voltage_Level", "SemanticID"],
    "Attribute_Lookup": ["Index", "Lookup_ID", "Scope", "Type_Constraint", "Attribute_Name", "Required",
                          "Data_Type", "Allowed_Values_Enum_Field", "Normative_Reference", "Description",
                          "Schema_Version_Introduced"],
    "Enum_Lookup": ["Index", "Enum_Lookup_ID", "Field_Name", "Allowed_Value", "Description", "Normative_Reference"],
    "Document_Data_Source": ["Index", "Document_Data_ID", "Source_Object_ID", "Source_Role", "Extraction_Method",
                              "Confidence", "Reviewed_By", "Review_Status", "Correction_Reason",
                              "Extraction_Timestamp", "SemanticID"],
    "Revision_Data_Source": ["Index", "Revision_ID", "Source_Object_ID", "Source_Role", "Extraction_Method",
                              "Confidence", "Reviewed_By", "Review_Status", "Correction_Reason",
                              "Extraction_Timestamp", "SemanticID"],
    "Element_Classification_Source": ["Index", "Classification_ID", "Source_Object_ID", "Source_Role",
                                       "Extraction_Method", "Confidence", "Reviewed_By", "Review_Status",
                                       "Correction_Reason", "Extraction_Timestamp", "SemanticID"],
}
SHEET_ORDER = list(SHEET_HEADERS.keys())


def baseline_sheets(doc_type="Instrument_Loop_Diagram", source_format="PDF_Drawing"):
    """A minimal, structurally complete and Level-1-conformant workbook (as
    dict-of-rows) covering one Terminal element, one Proximity cluster, one
    Matched pairing, and full provenance closure. Callers mutate copies."""
    s = {name: [] for name in SHEET_HEADERS}
    s["Rules"].append({"Rule_ID": "I1", "Rule_Category": "I", "Rule_Name": "x", "Rule_Description": "x",
                       "Schema_Version_Introduced": "v0.4"})
    s["Schema_Metadata"].append({"Index": 1, "Metadata_Key": "Cable_Modeling_Profile", "Metadata_Value": "Core"})
    s["Document_ID"].append({"Index": 1, "Document_ID": "D.1", "Document_Type": doc_type,
                             "Document_Filename": "x.pdf", "Page_Count": 1, "Schema_Version": "v0.8.2",
                             "Lookup_Version": "v0.8.0"})
    s["Document_Data"].append({"Index": 1, "Document_Data_ID": "DD.1", "Document_ID": "D.1",
                               "Attribute_Name": "Source_Format", "Attribute_Value": source_format})
    s["Document_Data_Source"].append({"Index": 1, "Document_Data_ID": "DD.1", "Source_Object_ID": "O.1",
                                      "Source_Role": "Value"})
    s["Document_RepresentedItem"].append({"Index": 1, "RepresentedItem_ID": "RI.1", "Document_ID": "D.1",
                                          "RepresentedItem_Type": "PCE_Request", "Primary_RKZ": "X.1",
                                          "Topic_Identification_Status": "Confirmed"})
    s["Object"].append({"Index": 1, "Object_ID": "O.1", "Document_ID": "D.1", "Page_Number": 1,
                        "Object_Type": "Text", "Source_Operation": "Tj", "Content_Text": "X1:1"})
    s["Cluster"].append({"Index": 1, "Cluster_ID": "CL.1", "Document_ID": "D.1", "Cluster_Type": "Proximity",
                         "Cluster_BBox_X1": 0, "Cluster_BBox_Y1": 0, "Cluster_BBox_X2": 1, "Cluster_BBox_Y2": 1,
                         "Cluster_Method": "NearestNeighbor", "Cluster_Parameter_Set": "{}"})
    s["Object_Cluster"].append({"Index": 1, "Object_ID": "O.1", "Cluster_ID": "CL.1", "Membership_Reason": "Proximity"})
    s["Elements_TopDown"].append({"Index": 1, "Element_TopDown_ID": "ETD.1", "Document_ID": "D.1",
                                  "Element_Name": "X1:1", "Primary_RKZ": "X1:1", "Element_Type": "Terminal"})
    s["Elements_from_Cluster"].append({"Index": 1, "Element_from_Cluster_ID": "EFC.1", "Document_ID": "D.1",
                                       "Source_Cluster_ID": "CL.1", "Element_Name": "X1:1",
                                       "Primary_RKZ_Extracted": "X1:1", "Element_Type_Inferred": "Terminal",
                                       "Derivation_Status": "Element_Derived"})
    s["Match_Result"].append({"Index": 1, "Match_ID": "M.1", "Document_ID": "D.1", "Element_TopDown_ID": "ETD.1",
                              "Element_from_Cluster_ID": "EFC.1", "Match_Status": "Matched",
                              "Match_Rule": "M1_Primary_RKZ", "Resolution_Status": "Resolved_AutoMatch",
                              "Reviewed_By": "Auto"})
    s["Element_ID"].append({"Index": 1, "Element_ID": "E.1", "Document_ID": "D.1", "Source_Match_ID": "M.1",
                            "Source": "Matched", "Element_Type": "Terminal", "Primary_RKZ": "X1:1",
                            "CAEX_Type": "ExternalInterface"})
    s["Element_RepresentedItem_Mapping"].append({"Index": 1, "Mapping_ID": "MAP.1", "Element_ID": "E.1",
                                                 "RepresentedItem_ID": "RI.1", "Relationship_Type": "Primary"})
    s["Element_Data"].append({"Index": 1, "Element_Data_ID": "ED.1", "Element_ID": "E.1",
                              "Attribute_Name": "Terminal_Number", "Attribute_Value": "1"})
    s["Element_Data_Source"].append({"Index": 1, "Element_Data_ID": "ED.1", "Source_Object_ID": "O.1",
                                     "Source_Role": "Value"})
    s["Element_Classification"].append({"Index": 1, "Classification_ID": "EC.1", "Document_ID": "D.1",
                                        "Classified_Object_Type": "Element", "Classified_Object_ID": "E.1",
                                        "Classification_System": "IEC 81346-2", "Classification_Code": "X"})
    s["Element_Classification_Source"].append({"Index": 1, "Classification_ID": "EC.1", "Source_Object_ID": "O.1",
                                               "Source_Role": "Value"})
    s["Attribute_Lookup"] += [
        {"Index": 1, "Lookup_ID": "AL.1", "Scope": "Document", "Type_Constraint": None,
         "Attribute_Name": "Source_Format", "Required": "True", "Data_Type": "Enum",
         "Allowed_Values_Enum_Field": "Source_Format"},
        {"Index": 2, "Lookup_ID": "AL.2", "Scope": "Element", "Type_Constraint": "Element_Type=Terminal",
         "Attribute_Name": "Terminal_Number", "Required": "True", "Data_Type": "String"},
        {"Index": 3, "Lookup_ID": "AL.3", "Scope": "Element", "Type_Constraint": "Element_Type=Terminal",
         "Attribute_Name": "Terminal_Strip_Designation", "Required": "False", "Data_Type": "String"},
    ]
    s["Enum_Lookup"] += [
        {"Index": i + 1, "Enum_Lookup_ID": f"EL.{i+1}", "Field_Name": fn, "Allowed_Value": av}
        for i, (fn, av) in enumerate([
            ("Document_Type", "Instrument_Loop_Diagram"), ("Document_Type", "Terminal_Diagram"),
            ("Document_Type", "Circuit_Diagram"), ("Element_Type", "Terminal"), ("Element_Type", "Coil"),
            ("Element_Type", "Motor"), ("CAEX_Type", "ExternalInterface"), ("CAEX_Type", "InternalElement"),
            ("Object_Type", "Text"), ("Object_Type", "Graphic"), ("Object_Type", "Topology"),
            ("Source_Operation", "Tj"), ("Source_Operation", "S"), ("Cluster_Type", "Proximity"),
            ("Match_Status", "Matched"), ("Resolution_Status", "Resolved_AutoMatch"),
            ("Classification_System", "IEC 81346-2"), ("Classification_System", "IEC 60617-7"),
            ("Relationship_Type", "Primary"), ("Source_Format", "PDF_Drawing"), ("Source_Format", "Excel_Sheet"),
            ("RepresentedItem_Type", "PCE_Request"), ("Topic_Identification_Status", "Confirmed"),
            ("Membership_Reason", "Proximity"), ("Derivation_Status", "Element_Derived"),
        ])
    ]
    return s


def write_workbook(sheets, path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for name in SHEET_ORDER:
        ws = wb.create_sheet(name)
        headers = SHEET_HEADERS[name]
        ws.append(headers)
        for row in sheets.get(name, []):
            ws.append([row.get(h) for h in headers])
    wb.save(path)


def run_check(sheets):
    """Write sheets to a temp file, run checker.check(), return RULE_RESULTS (copied).

    Uses a manually-managed temp dir (not TemporaryDirectory's context manager):
    openpyxl's read_only loader keeps a file handle open on Windows, which makes
    the context manager's automatic rmtree-on-exit raise PermissionError/
    NotADirectoryError. Cleanup is therefore best-effort here."""
    tmp = tempfile.mkdtemp()
    try:
        p = Path(tmp) / "wb.xlsx"
        write_workbook(sheets, p)
        c.check(p, output_path=Path(tmp) / "out.txt")
        return {k: dict(v) for k, v in c.RULE_RESULTS.items()}
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def add_cd(sheets, connection_id, attrs, prov_oid="O.1"):
    for i, (name, val) in enumerate(attrs.items()):
        cdid = f"CD.{connection_id}.{i}"
        sheets["Connection_Data"].append({"Connection_Data_ID": cdid, "Connection_ID": connection_id,
                                          "Attribute_Name": name, "Attribute_Value": val})
        sheets["Connection_Data_Source"].append({"Connection_Data_ID": cdid, "Source_Object_ID": prov_oid,
                                                 "Source_Role": "Value"})


class TestNotImplementedMechanism(unittest.TestCase):
    def test_all_declared_rules_are_implemented_or_marked(self):
        results = run_check(baseline_sheets())
        for rule in c.RULE_DEFINITIONS:
            self.assertIn(rule, results)
            if rule in c.IMPLEMENTED_RULES:
                self.assertNotEqual(results[rule]["status"], "NOT_RUN",
                                    f"{rule} is declared implemented but was never executed")
            else:
                self.assertEqual(results[rule]["status"], "NOT_IMPLEMENTED")

    def test_fake_unimplemented_rule_is_not_silently_passed(self):
        # Simulates the old bug: a declared rule with no check code must show
        # NOT_IMPLEMENTED, never PASS, once it is excluded from IMPLEMENTED_RULES.
        old_defs = dict(c.RULE_DEFINITIONS)
        old_impl = set(c.IMPLEMENTED_RULES)
        try:
            c.RULE_DEFINITIONS["Z_fake"] = "A rule nobody implemented."
            c.IMPLEMENTED_RULES.discard("Z_fake")
            results = run_check(baseline_sheets())
            self.assertEqual(results["Z_fake"]["status"], "NOT_IMPLEMENTED")
        finally:
            c.RULE_DEFINITIONS.clear(); c.RULE_DEFINITIONS.update(old_defs)
            c.IMPLEMENTED_RULES.clear(); c.IMPLEMENTED_RULES.update(old_impl)


class TestSkipBookkeeping(unittest.TestCase):
    def test_skip_recorded_on_real_rule_key_not_pseudo_key(self):
        results = run_check(baseline_sheets(doc_type="Instrument_Loop_Diagram"))
        self.assertEqual(results["I23"]["status"], "SKIP")
        self.assertNotIn("I23-skipped", results)
        self.assertEqual(results["I28"]["status"], "SKIP")
        self.assertNotIn("I28-skipped", results)


class TestCrashFix(unittest.TestCase):
    def test_empty_document_id_sheet_does_not_crash(self):
        s = baseline_sheets()
        s["Document_ID"] = []  # no rows -> doc_type is None downstream
        try:
            results = run_check(s)
        except TypeError as e:
            self.fail(f"check() crashed on empty Document_ID sheet: {e}")
        self.assertEqual(results["D1/A-structural"]["status"], "FAIL")
        # type-scoped rules must report SKIP (not applicable), not crash
        self.assertEqual(results["I23"]["status"], "SKIP")


class TestI23(unittest.TestCase):
    def _wb(self):
        s = baseline_sheets(doc_type="Terminal_Diagram", source_format="Excel_Sheet")
        s["Enum_Lookup"].append({"Enum_Lookup_ID": "EL.99", "Field_Name": "Connection_Type", "Allowed_Value": "Bridge_Longitudinal"})
        s["Enum_Lookup"].append({"Enum_Lookup_ID": "EL.98", "Field_Name": "Connection_Type", "Allowed_Value": "Wire"})
        s["Attribute_Lookup"].append({"Lookup_ID": "AL.9", "Scope": "Connection", "Attribute_Name": "Connection_Type",
                                      "Required": "False", "Data_Type": "Enum",
                                      "Allowed_Values_Enum_Field": "Connection_Type"})
        # second terminal E.2, different Parent_Element_ID (no strip set on either -> both None -> "same" by default)
        s["Element_ID"].append({"Element_ID": "E.2", "Document_ID": "D.1", "Source_Match_ID": "M.1",
                                "Source": "Matched", "Element_Type": "Terminal", "Primary_RKZ": "X1:2",
                                "Parent_Element_ID": "STRIP.A", "CAEX_Type": "ExternalInterface"})
        s["Element_ID"][0]["Parent_Element_ID"] = "STRIP.A"
        s["Connection_ID"].append({"Connection_ID": "C.1", "Document_ID": "D.1", "From_Element_ID": "E.1",
                                   "To_Element_ID": "E.2", "Source_Topology_Object_ID": "O.1",
                                   "Connection_Status": "Resolved"})
        return s

    def test_violation_bridge_between_different_strips(self):
        s = self._wb()
        s["Element_ID"][1]["Parent_Element_ID"] = "STRIP.B"  # different strip than E.1's STRIP.A
        add_cd(s, "C.1", {"Connection_Type": "Bridge_Longitudinal"})
        results = run_check(s)
        self.assertEqual(results["I23"]["status"], "FAIL")

    def test_satisfies_bridge_within_same_strip(self):
        s = self._wb()
        add_cd(s, "C.1", {"Connection_Type": "Bridge_Longitudinal"})
        results = run_check(s)
        self.assertEqual(results["I23"]["status"], "PASS")


class TestI24(unittest.TestCase):
    def _wb(self):
        s = baseline_sheets(doc_type="Terminal_Diagram", source_format="Excel_Sheet")
        for fn, av in [("Wire_Color", "GNYE"), ("Wire_Color", "BU"), ("Polarity", "PE"), ("Polarity", "N")]:
            s["Enum_Lookup"].append({"Enum_Lookup_ID": f"EL.w{fn}{av}", "Field_Name": fn, "Allowed_Value": av})
        s["Attribute_Lookup"] += [
            {"Lookup_ID": "AL.10", "Scope": "Connection", "Attribute_Name": "Wire_Color", "Required": "False",
             "Data_Type": "Enum", "Allowed_Values_Enum_Field": "Wire_Color"},
            {"Lookup_ID": "AL.11", "Scope": "Connection", "Attribute_Name": "Polarity", "Required": "False",
             "Data_Type": "Enum", "Allowed_Values_Enum_Field": "Polarity"},
        ]
        s["Element_ID"].append({"Element_ID": "E.2", "Document_ID": "D.1", "Source_Match_ID": "M.1",
                                "Source": "Matched", "Element_Type": "Terminal", "Primary_RKZ": "X1:2",
                                "CAEX_Type": "ExternalInterface"})
        s["Connection_ID"].append({"Connection_ID": "C.1", "Document_ID": "D.1", "From_Element_ID": "E.1",
                                   "To_Element_ID": "E.2", "Source_Topology_Object_ID": "O.1",
                                   "Connection_Status": "Resolved"})
        return s

    def test_violation_gnye_with_wrong_polarity(self):
        s = self._wb()
        add_cd(s, "C.1", {"Wire_Color": "GNYE", "Polarity": "N"})
        results = run_check(s)
        self.assertEqual(results["I24"]["status"], "FAIL")

    def test_satisfies_gnye_with_pe(self):
        s = self._wb()
        add_cd(s, "C.1", {"Wire_Color": "GNYE", "Polarity": "PE"})
        results = run_check(s)
        self.assertEqual(results["I24"]["status"], "PASS")

    def test_satisfies_gnye_with_missing_polarity_abstains(self):
        s = self._wb()
        add_cd(s, "C.1", {"Wire_Color": "GNYE"})
        results = run_check(s)
        self.assertEqual(results["I24"]["status"], "PASS")


class TestI26(unittest.TestCase):
    def _wb(self):
        s = baseline_sheets(doc_type="Circuit_Diagram", source_format="PDF_Drawing")
        s["Element_ID"][0]["Element_Type"] = "Coil"
        s["Element_ID"][0]["CAEX_Type"] = "InternalElement"
        s["Element_Data"][0]["Attribute_Name"] = "Current_Path_Number"
        s["Element_Data"][0]["Attribute_Value"] = "1"
        s["Attribute_Lookup"][1] = {"Lookup_ID": "AL.2", "Scope": "Element", "Type_Constraint": None,
                                    "Attribute_Name": "Current_Path_Number", "Required": "False", "Data_Type": "Integer"}
        s["Element_Classification"][0]["Classification_System"] = "IEC 60617-7"
        s["Element_Classification"][0]["Classification_Code"] = "07-15-01"
        return s

    def test_violation_non_integer_path_number(self):
        s = self._wb()
        s["Element_Data"][0]["Attribute_Value"] = "abc"
        results = run_check(s)
        self.assertEqual(results["I26"]["status"], "FAIL")

    def test_satisfies_contiguous_path_numbers(self):
        s = self._wb()
        results = run_check(s)
        self.assertEqual(results["I26"]["status"], "PASS")

    def test_gap_is_warning_not_failure(self):
        s = self._wb()
        s["Element_ID"].append({"Element_ID": "E.2", "Document_ID": "D.1", "Source_Match_ID": "M.1",
                                "Source": "Matched", "Element_Type": "Coil", "Primary_RKZ": "K2",
                                "CAEX_Type": "InternalElement"})
        s["Element_Data"].append({"Element_Data_ID": "ED.2", "Element_ID": "E.2",
                                  "Attribute_Name": "Current_Path_Number", "Attribute_Value": "3"})
        s["Element_Data_Source"].append({"Element_Data_ID": "ED.2", "Source_Object_ID": "O.1", "Source_Role": "Value"})
        s["Element_Classification"].append({"Classification_ID": "EC.2", "Document_ID": "D.1",
                                            "Classified_Object_Type": "Element", "Classified_Object_ID": "E.2",
                                            "Classification_System": "IEC 60617-7", "Classification_Code": "07-15-01"})
        s["Element_Classification_Source"].append({"Classification_ID": "EC.2", "Source_Object_ID": "O.1",
                                                   "Source_Role": "Value"})
        results = run_check(s)  # gap at path 2, no reserve marker/grid declared
        self.assertEqual(results["I26"]["status"], "PASS",
                         "a non-contiguous gap is a warning per §11.9, not a hard violation")
        self.assertTrue(any("WARNING" in d for d in results["I26"]["details"]))


class TestI28(unittest.TestCase):
    def _wb(self):
        s = baseline_sheets(doc_type="Circuit_Diagram", source_format="PDF_Drawing")
        s["Element_ID"][0]["Element_Type"] = "Coil"
        s["Element_ID"][0]["CAEX_Type"] = "InternalElement"
        s["Element_Classification"] = []  # remove the IEC 81346-2-only baseline row
        s["Element_Classification_Source"] = []
        s["Enum_Lookup"].append({"Enum_Lookup_ID": "EL.60617", "Field_Name": "Classification_System",
                                 "Allowed_Value": "IEC 60617-7"})
        return s

    def test_violation_no_iec60617_and_no_unclassified_fallback(self):
        results = run_check(self._wb())
        self.assertEqual(results["I28"]["status"], "FAIL")

    def test_satisfies_with_iec60617_row(self):
        s = self._wb()
        s["Element_Classification"].append({"Classification_ID": "EC.1", "Document_ID": "D.1",
                                             "Classified_Object_Type": "Element", "Classified_Object_ID": "E.1",
                                             "Classification_System": "IEC 60617-7", "Classification_Code": "07-15-01"})
        s["Element_Classification_Source"].append({"Classification_ID": "EC.1", "Source_Object_ID": "O.1",
                                                    "Source_Role": "Value"})
        results = run_check(s)
        self.assertEqual(results["I28"]["status"], "PASS")

    def test_satisfies_with_unclassified_fallback(self):
        s = self._wb()
        s["Element_Classification"].append({"Classification_ID": "EC.1", "Document_ID": "D.1",
                                             "Classified_Object_Type": "Element", "Classified_Object_ID": "E.1",
                                             "Classification_System": "IEC 60617-7", "Classification_Code": "Unclassified",
                                             "Source_Symbol_Reference": "symbol not verified"})
        s["Element_Classification_Source"].append({"Classification_ID": "EC.1", "Source_Object_ID": "O.1",
                                                    "Source_Role": "Value"})
        results = run_check(s)
        self.assertEqual(results["I28"]["status"], "PASS")

    def test_violation_bad_code_pattern(self):
        s = self._wb()
        s["Element_Classification"].append({"Classification_ID": "EC.1", "Document_ID": "D.1",
                                             "Classified_Object_Type": "Element", "Classified_Object_ID": "E.1",
                                             "Classification_System": "IEC 60617-7", "Classification_Code": "not-a-code"})
        s["Element_Classification_Source"].append({"Classification_ID": "EC.1", "Source_Object_ID": "O.1",
                                                    "Source_Role": "Value"})
        results = run_check(s)
        self.assertEqual(results["I28"]["status"], "FAIL")


class TestRequiredAttributes(unittest.TestCase):
    def test_violation_missing_required_attribute(self):
        # Non-blocking by design: a Required=TRUE attribute absent from the source
        # is a content-completeness gap, not a conformance defect -- WARNING, not FAIL.
        s = baseline_sheets()
        s["Element_Data"] = []  # Terminal_Number (Required=True) now unpopulated
        s["Element_Data_Source"] = []
        results = run_check(s)
        self.assertEqual(results["Required_Attributes"]["status"], "WARNING")

    def test_satisfies_when_required_attribute_present(self):
        results = run_check(baseline_sheets())
        self.assertEqual(results["Required_Attributes"]["status"], "PASS")

    def test_unspecifiable_counts_as_populated(self):
        s = baseline_sheets()
        s["Element_Data"][0]["Attribute_Value"] = "Unspecifiable"
        results = run_check(s)
        self.assertEqual(results["Required_Attributes"]["status"], "PASS")


class TestClusterCoverage(unittest.TestCase):
    def test_violation_uncovered_object_in_pdf_source(self):
        s = baseline_sheets(source_format="PDF_Drawing")
        s["Object"].append({"Object_ID": "O.2", "Document_ID": "D.1", "Page_Number": 1,
                            "Object_Type": "Text", "Source_Operation": "Tj", "Content_Text": "orphan"})
        # O.2 intentionally not added to Object_Cluster
        results = run_check(s)
        self.assertEqual(results["Cluster_Coverage"]["status"], "FAIL")

    def test_satisfies_full_coverage(self):
        results = run_check(baseline_sheets(source_format="PDF_Drawing"))
        self.assertEqual(results["Cluster_Coverage"]["status"], "PASS")

    def test_skipped_for_non_pdf_source(self):
        results = run_check(baseline_sheets(source_format="Excel_Sheet"))
        self.assertEqual(results["Cluster_Coverage"]["status"], "SKIP")

    def test_manual_entry_object_exempt(self):
        s = baseline_sheets(source_format="PDF_Drawing")
        s["Object"].append({"Object_ID": "O.99", "Document_ID": "D.1", "Page_Number": 0,
                            "Object_Type": "Text", "Source_Operation": "Manual_Entry", "Content_Text": "rationale"})
        results = run_check(s)
        self.assertEqual(results["Cluster_Coverage"]["status"], "PASS")

    def test_empty_result_marker_permits_empty_clusters(self):
        s = baseline_sheets(source_format="PDF_Drawing")
        s["Cluster"] = []
        s["Object_Cluster"] = []
        s["Document_Data"].append({"Document_Data_ID": "DD.2", "Document_ID": "D.1",
                                   "Attribute_Name": "Cluster_Method", "Attribute_Value": "P3_Empty_Result"})
        s["Document_Data_Source"].append({"Document_Data_ID": "DD.2", "Source_Object_ID": "O.1", "Source_Role": "Value"})
        results = run_check(s)
        self.assertEqual(results["Cluster_Coverage"]["status"], "PASS")


class TestProcessStepPostConditions(unittest.TestCase):
    def test_p6_violated_by_open_resolution(self):
        s = baseline_sheets()
        s["Match_Result"][0]["Resolution_Status"] = "Open"
        proc = self._compute(s)
        self.assertFalse(proc["P6"]["satisfied"])

    def test_p6_satisfied(self):
        proc = self._compute(baseline_sheets())
        self.assertTrue(proc["P6"]["satisfied"])

    def test_p7_violated_by_dangling_source_match_id(self):
        s = baseline_sheets()
        s["Element_ID"][0]["Source_Match_ID"] = "M.999"
        proc = self._compute(s)
        self.assertFalse(proc["P7"]["satisfied"])

    def test_stub_28_empty_sheets_no_longer_counts_as_10_of_10(self):
        # Regression test for the exact bug report: a workbook with all sheets
        # present but essentially no content must NOT report all steps satisfied.
        s = {name: [] for name in SHEET_HEADERS}
        s["Document_ID"].append({"Document_ID": "D.1", "Document_Type": "Instrument_Loop_Diagram",
                                 "Document_Filename": "x", "Page_Count": 1, "Schema_Version": "v0.8.2",
                                 "Lookup_Version": "v0.8.0"})
        s["Schema_Metadata"].append({"Metadata_Key": "Cable_Modeling_Profile", "Metadata_Value": "Core"})
        proc = self._compute(s)
        decidable_satisfied = sum(1 for v in proc.values() if v["decidable"] and v["satisfied"])
        self.assertLess(decidable_satisfied, 10)

    @staticmethod
    def _compute(sheets):
        import shutil
        tmp = tempfile.mkdtemp()
        try:
            p = Path(tmp) / "wb.xlsx"
            write_workbook(sheets, p)
            order, loaded = c.load(p)
            doc_ids = c.ids(loaded, "Document_ID", "Document_ID")
            E = c.ids(loaded, "Element_ID", "Element_ID")
            OBJ = c.ids(loaded, "Object", "Object_ID")
            CL = c.ids(loaded, "Cluster", "Cluster_ID")
            ETD = c.ids(loaded, "Elements_TopDown", "Element_TopDown_ID")
            EFC = c.ids(loaded, "Elements_from_Cluster", "Element_from_Cluster_ID")
            MR = c.ids(loaded, "Match_Result", "Match_ID")
            RIT = c.ids(loaded, "Document_RepresentedItem", "RepresentedItem_ID")
            CID = c.ids(loaded, "Connection_ID", "Connection_ID")
            LAY = c.ids(loaded, "Layer_ID", "Layer_ID")
            return c.compute_process_step_post_conditions(loaded, doc_ids, E, OBJ, CL, ETD, EFC, MR, RIT, CID, LAY)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
