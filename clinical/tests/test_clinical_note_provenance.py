"""Canonical provenance must not change diagnostic behavior or syndrome identity."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_clinical_note_diagnostic_coverage as coverage
from clinical_note_diagnostic_engine import analyze, _candidate
from clinical_note_support import new_note
from run_clinical_note_diagnostic_cases import build as build_general
from run_clinical_note_diagnostic_closure_cases import build as build_closure
from run_clinical_note_pediatric_routing_cases import build as build_pediatric


EXPECTED_SOURCES = {
    "major-trauma": "trauma-major-hemorrhage",
    "traumatic-head-injury": "traumatic-intracranial-mass-effect",
    "ectopic-pregnancy": "obstetric-emergencies",
    "preeclampsia-eclampsia": "obstetric-emergencies",
    "postpartum-hemorrhage": "obstetric-emergencies",
    "neutropenic-sepsis": "hematology-oncology",
    "sickle-cell-acute-emergency": "hematology-oncology",
    "testicular-torsion": "urologic-emergencies",
    "acute-angle-closure-glaucoma": "ophthalmology-emergencies",
    "ent-airway-emergency": "ent-emergencies",
    "septic-arthritis-orthopedic": "orthopedic-emergencies",
    "self-harm-suicide-risk": "suicide-risk",
    "acute-agitation-psychosis": "psychiatric-emergencies",
    "environmental-hypothermia": "environmental-emergencies",
    "environmental-heat-illness": "environmental-emergencies",
    "drowning-emergency": "environmental-emergencies",
    "pyelonephritis-urologic-emergency": "urologic-emergencies",
    "geriatric-delirium-emergency": "geriatric-emergencies",
}

EXTRA_INPUTS = {
    "traumatic-head-injury": "traumatismo craniano; perda de consciência; vómitos repetidos",
    "postpartum-hemorrhage": "hemorragia pós-parto; atonia uterina; puerpério imediato",
    "ent-airway-emergency": "epiglotite; estridor",
    "acute-agitation-psychosis": "agitação grave; ameaça a terceiros",
    "environmental-hypothermia": "hipotermia; bradicardia",
    "drowning-emergency": "afogamento; aspiração de água",
}


def corpus():
    banks = (
        ("clinical-note-diagnostic-synthetic-cases.json", build_general),
        ("clinical-note-diagnostic-final-cases-a.json", build_general),
        ("clinical-note-diagnostic-final-cases-b.json", build_general),
        ("clinical-note-diagnostic-closure-cases.json", build_closure),
        ("clinical-note-diagnostic-pediatric-routing-cases.json", build_pediatric),
    )
    for name, build in banks:
        for case in json.loads((ROOT / "qa" / name).read_text(encoding="utf-8"))["cases"]:
            yield case["id"], build(case)


def source_modules(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "source_modules":
                yield from item
            else:
                yield from source_modules(item)
    elif isinstance(value, list):
        for item in value:
            yield from source_modules(item)


def without_provenance(value):
    if isinstance(value, dict):
        return {key: without_provenance(item) for key, item in value.items()
                if key != "source_modules"}
    if isinstance(value, list):
        return [without_provenance(item) for item in value]
    return value


class ClinicalNoteProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = json.loads((ROOT / "qa" / "clinical-note-diagnostic-rules.json").read_text(encoding="utf-8"))
        cls.registered = set(json.loads((ROOT / "references" / "evidence-registry.json").read_text(encoding="utf-8"))["modules"])
        cls.notes = list(corpus())
        cls.results = [(case_id, analyze(note, apply_to_note=True)) for case_id, note in cls.notes]

    def test_every_output_source_resolves_in_the_existing_sixty_case_corpus(self):
        self.assertEqual(len(self.results), 60)
        for case_id, result in self.results:
            with self.subTest(case_id=case_id):
                self.assertFalse(result["blocked"])
                self.assertEqual(set(source_modules(result)) - self.registered, set())

    def test_eighteen_syndromes_retain_identity_and_show_the_canonical_source(self):
        results = [result for _, result in self.results]
        for syndrome_id, text in EXTRA_INPUTS.items():
            note = new_note(age_years=40, sex="female" if syndrome_id == "postpartum-hemorrhage" else "unknown")
            note["history"]["chief_complaint"] = text
            note["history"]["allergies"] = []
            note["privacy"].update(direct_identifiers_removed=True, free_text_screened=True,
                                   source_metadata_checked=True, burned_in_identifiers_checked=True)
            result = analyze(note)
            self.assertFalse(result["blocked"])
            self.assertIn(syndrome_id, {hit["module"] for hit in result["rule_hits"]})
            results.append(result)
        rules_by_id = {rule["id"]: rule for rule in self.rules["syndromes"]}
        for syndrome_id, expected in EXPECTED_SOURCES.items():
            with self.subTest(syndrome_id=syndrome_id):
                self.assertNotIn(syndrome_id, self.registered)
                diagnosis = rules_by_id[syndrome_id]["diagnosis"]
                candidates = [candidate for result in results
                              for group in ("likely_diagnoses", "differential_diagnoses", "must_not_miss")
                              for candidate in result["assessment"][group]
                              if candidate["diagnosis"] == diagnosis]
                self.assertTrue(candidates, "syndrome must be exercised through analyze")
                for candidate in candidates:
                    self.assertEqual(candidate["source_modules"], [expected])

    def test_provenance_metadata_preserves_all_other_output_in_sixty_cases(self):
        legacy_rules = deepcopy(self.rules)
        for rule in legacy_rules["syndromes"]:
            rule.pop("source_modules", None)
            if rule["id"] == "cardiogenic-shock":
                for suggestion in rule["treatment"]:
                    suggestion["source_modules"] = [
                        "vasoactive-inotrope-therapy" if value == "vasoactive-inotrope-infusions" else value
                        for value in suggestion["source_modules"]
                    ]
        for (case_id, note), (_, current) in zip(self.notes, self.results):
            with self.subTest(case_id=case_id):
                legacy = analyze(note, rules=legacy_rules, apply_to_note=True)
                self.assertEqual(without_provenance(current), without_provenance(legacy))

    def test_audit_accepts_syndrome_ids_but_requires_registered_source_modules(self):
        result = coverage.audit()
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["invalid_source_modules"], [])

    def test_audit_rejects_unknown_or_syndrome_ids_used_as_source_modules(self):
        for invalid in ("nonexistent-source-module", "acute-angle-closure-glaucoma"):
            with self.subTest(invalid=invalid):
                rules = deepcopy(self.rules)
                rules["syndromes"][0]["suggested_tests"][0]["source_modules"].append(invalid)
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "rules.json"
                    path.write_text(json.dumps(rules), encoding="utf-8")
                    with patch.object(coverage, "RULES", path):
                        result = coverage.audit()
                self.assertEqual(result["status"], "FAIL", result)
                self.assertIn(invalid, [row.get("source_module") for row in result["invalid_source_modules"]])

    def test_audit_rejects_an_empty_explicit_source_list(self):
        rules = deepcopy(self.rules)
        rules["syndromes"][0]["source_modules"] = []
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "rules.json"
            path.write_text(json.dumps(rules), encoding="utf-8")
            with patch.object(coverage, "RULES", path):
                result = coverage.audit()
        self.assertEqual(result["status"], "FAIL", result)
        self.assertTrue(result["invalid_source_modules"])

    def test_candidate_does_not_share_mutable_provenance_with_the_rule(self):
        rule = {"id": "synthetic-syndrome", "source_modules": ["ophthalmology-emergencies"]}
        result = _candidate(rule, 1, [], "low")
        result["source_modules"].append("another-value")
        self.assertEqual(rule["source_modules"], ["ophthalmology-emergencies"])


if __name__ == "__main__":
    unittest.main()
