import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from clinical_note_diagnostic_engine import analyze
from clinical_note_exporter import note_to_sections
from clinical_note_support import validate_contract
from run_clinical_note_diagnostic_cases import build
from test_clinical_note_provenance import corpus


def result(text, **fields):
    return analyze(build({"age_years": 40, "hpi": text, **fields}), apply_to_note=True)


def candidate(response, module):
    assessment = response["assessment"]
    return next(item for key in ("likely_diagnoses", "differential_diagnoses")
                for item in assessment[key] if module in item["source_modules"])


class DiagnosticObservations(unittest.TestCase):
    def test_only_explicit_current_denials_are_opposing_observations(self):
        for phrase in ("Denies chest pain.", "Niega dolor torácico.", "Sem dor torácica."):
            with self.subTest(phrase=phrase):
                item = candidate(result("ST elevation. " + phrase), "acute-coronary-syndrome")
                self.assertEqual(len(item["evidence_against"]), 1)
                self.assertIn("elevación del ST", item["evidence_for"])
        for phrase in ("", "Previously denied chest pain.", "Possible chest pain.", "Chest pain."):
            with self.subTest(phrase=phrase):
                self.assertFalse(candidate(result("ST elevation. " + phrase), "acute-coronary-syndrome")["evidence_against"])

    def test_uncertain_mentions_are_disclosed_for_review(self):
        for text in ("Possible chest pain.", "Dolor torácico?", "Não se pode excluir dor torácica.",
                     "No se descarta dolor torácico.", "Pendiente de confirmar elevación del ST."):
            with self.subTest(text=text):
                assessment = result(text)["assessment"]
                self.assertTrue(any("Menções incertas" in line for line in assessment["limitations"]))
                self.assertFalse(assessment["likely_diagnoses"] or assessment["differential_diagnoses"])
                self.assertFalse(assessment["treatment_suggestions"])

    def test_other_subject_is_not_patient_evidence(self):
        for text in ("Mother has chest pain.", "Antecedentes familiares de dolor torácico."):
            with self.subTest(text=text):
                response = result(text)
                self.assertFalse(response["rule_hits"])
                self.assertFalse(response["assessment"]["likely_diagnoses"])
                self.assertFalse(response["assessment"]["treatment_suggestions"])
                self.assertTrue(response["assessment"]["limitations"])
        self.assertTrue(result("Mother has chest pain. Currently has chest pain.")["rule_hits"])
        for text in ("Possible nausea, ECG shows ST elevation.", "Mother has chest pain, patient has ST elevation.",
                     "Possible nausea, now ST elevation."):
            with self.subTest(text=text):
                self.assertIn("elevación del ST", candidate(result(text), "acute-coronary-syndrome")["evidence_for"])

    def test_ecg_report_presence_does_not_assert_test_adequacy(self):
        item = candidate(result("Chest pain. ST elevation.", ecg="ST elevation."), "acute-coronary-syndrome")
        self.assertIn("ECG: relatório oficial registado; verificar conteúdo e adequação.", item["missing_discriminating_data"])
        item = candidate(result("Chest pain. ST elevation. ECG pendiente."), "acute-coronary-syndrome")
        self.assertIn("ECG", item["missing_discriminating_data"])

    def test_mixed_note_identifies_contribution_to_candidate_and_export(self):
        response = result("Possible ST elevation. Nausea.")
        item = candidate(response, "acute-coronary-syndrome")
        self.assertEqual(item["weighted_uncertainty"], ["st elevation"])
        self.assertEqual(item["evidence_for"], ["síntomas autonómicos"])
        note = response["note"]
        self.assertEqual(validate_contract(note), [])
        for language, warning in (("pt-PT", "Classificação inclui menções não confirmadas"),
                                  ("es-ES", "La clasificación incluye menciones sin confirmar")):
            note["language"] = language
            lines = [line for _, section in note_to_sections(note) for line in section]
            self.assertTrue(any(warning + ": st elevation" in line for line in lines))
        affirmed = candidate(result("ST elevation. Possible STEMI."), "acute-coronary-syndrome")
        self.assertNotIn("weighted_uncertainty", affirmed)

    def test_discriminants_use_exact_independent_structured_observations(self):
        case = "Sickle cell."
        def missing(**fields):
            return candidate(result(case, **fields), "hematology-oncology")["missing_discriminating_data"]
        self.assertIn("SpO2", missing())
        self.assertNotIn("SpO2", missing(vitals={"spo2": 96}))
        self.assertIn("SpO2", missing(vitals={"spo2": 120}))
        self.assertIn("dor/analgesia prévia", missing(vitals={"spo2": 96}))

    def test_unresolved_relation_visible_without_fabricated_candidate(self):
        for text, age, relation in (
            ("Sickle cell.", 40, "acute-chest-syndrome"),
            ("Politrauma.", 40, "traumatic-intracranial-mass-effect"),
            ("Intoxicação.", 40, "arrhythmias-cardiac-arrest"),
            ("CAD pediátrica.", 10, "pediatric-electrolyte-emergencies"),
        ):
            with self.subTest(relation=relation):
                response = result(text, age_years=age)
                assessment = response["assessment"]
                self.assertTrue(any(relation in line for line in assessment["limitations"]))
                self.assertFalse(any(x["diagnosis"] == relation for x in assessment["must_not_miss"]))
                self.assertEqual(assessment, response["note"]["assessment"])

    def test_simple_fields_do_not_satisfy_compound_requests(self):
        missing = "missing_discriminating_data"
        trauma = candidate(result("Politrauma.", vitals={"gcs": "15"}), "trauma-major-hemorrhage")
        self.assertNotIn("GCS", trauma[missing])
        head = candidate(result("Traumatismo craniano.", vitals={"gcs": "15"}), "traumatic-intracranial-mass-effect")
        self.assertIn("GCS e componentes", head[missing])
        infant = candidate(result("Bronchiolitis.", age_years=1), "bronchiolitis")
        self.assertNotIn("idade", infant[missing])
        asthma = candidate(result("Wheezing.", vitals={"rr": 22}), "acute-severe-asthma")
        self.assertNotIn("frequência respiratória", asthma[missing])

    def test_priority_overflow_and_age_filtered_relations_stay_visible(self):
        notes = dict(corpus())
        for case_id, notice, relation in (
            ("mesenteric-ischemia", "além das cinco apresentadas", "pulmonary-embolism"),
            ("peds-drowning", "fora dos limites etários", "adult-cardiac-arrest"),
            ("peds-drowning", "fora dos limites etários", "adult-arrhythmias"),
        ):
            with self.subTest(case_id=case_id, relation=relation):
                assessment = analyze(notes[case_id])["assessment"]
                self.assertTrue(any(notice in line and relation in line for line in assessment["limitations"]))
