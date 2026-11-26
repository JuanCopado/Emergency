"""Clinical review must bind exact content, context and current canonical sources."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import therapeutic_plan_workflow as therapy
from clinical_note_support import new_note, validate_for_export
from clinical_note_api import dispatch, export_note_bytes
from clinical_note_exporter import note_to_sections


def clean_note(age=45, language="es-ES"):
    note = new_note(age_years=age, language=language)
    note["history"]["chief_complaint"] = "Evaluación clínica sintética"
    note["privacy"].update(direct_identifiers_removed=True, free_text_screened=True,
                           source_metadata_checked=True, burned_in_identifiers_checked=True)
    note["clinician_validation"]["reviewed"] = True
    return note


def add_manual_draft(note, **context):
    response = therapy.suggest({"note": note,
        "selection": {"label": "Problema clínico seleccionado", "module_id": None, "selection": "manual"},
        "context": {"weight_kg": None, "allergies_reviewed": True, **context}})
    if response["blocked"]:
        raise AssertionError(response["issues"])
    note["therapeutic_plan"] = response["plan"]
    return note


def complete_draft(note):
    # Fictional non-prescribing test content; no doses or clinical recommendations.
    note["therapeutic_plan"]["sections"] = {
        "initial_actions": "Medidas individualizadas de prueba A.",
        "medications": "No se indica medicación en este caso sintético.",
        "monitoring": "Plan de monitorización de prueba B.",
        "reassessment": "Reevaluación y escalada de prueba C.",
        "disposition": "Destino y seguimiento de prueba D.",
    }
    return note


def review(note):
    response = therapy.validate({"note": note, "confirmations": {
        "individualized": True, "medication_safety_reviewed": True}})
    if response["blocked"]:
        raise AssertionError(response["issues"])
    note["therapeutic_review"] = response["review"]
    return note


class TherapeuticWorkflowTests(unittest.TestCase):
    def test_manual_draft_is_incomplete_and_not_a_prescription(self):
        note = add_manual_draft(clean_note())
        self.assertTrue(therapy.validate({"note": note})["blocked"])
        self.assertTrue(validate_for_export(note)["blocked"])
        self.assertFalse(note["therapeutic_plan"]["medication_safety"]["actionable"])

    def test_population_age_and_weight_are_not_coerced(self):
        for age, population in ((45, "adult"), (18, "adult"), (17, "pediatric"), (0, "pediatric")):
            self.assertEqual(add_manual_draft(clean_note(age))["therapeutic_plan"]["population"], population)
        for values in ({"years": None, "months": None}, {"years": 5, "months": 60}, {"years": None, "months": 1600}):
            note = clean_note(); note["encounter"]["age"] = values
            result = therapy.suggest({"note": note, "selection": {"label": "X", "module_id": None, "selection": "manual"}, "context": {"weight_kg": None, "allergies_reviewed": True}})
            self.assertTrue(result["blocked"])
        for weight in (True, 0, -1, "12", float("inf"), float("nan")):
            with self.subTest(weight=weight):
                result = therapy.suggest({"note": clean_note(), "selection": {"label": "X", "module_id": None, "selection": "manual"}, "context": {"weight_kg": weight, "allergies_reviewed": True}})
                self.assertTrue(result["blocked"])

    def test_months_only_infant_is_pediatric(self):
        note = clean_note(None); note["encounter"]["age"]["months"] = 8
        self.assertEqual(add_manual_draft(note)["therapeutic_plan"]["population"], "pediatric")

    def test_alleged_diagnostic_selection_must_exist(self):
        result = therapy.suggest({"note": clean_note(), "selection": {"label": "Fabricated", "module_id": "sepsis-shock", "selection": "diagnostic"}, "context": {"weight_kg": None, "allergies_reviewed": True}})
        self.assertTrue(result["blocked"])

    def test_red_to_green_edited_review_and_all_exports(self):
        note = complete_draft(add_manual_draft(clean_note()))
        self.assertTrue(validate_for_export(note)["blocked"])
        review(note)
        self.assertEqual(note["therapeutic_review"]["mode"], "edited")
        self.assertFalse(validate_for_export(note)["blocked"])
        self.assertEqual(note["therapeutic_review"]["scope"], "physician_review_of_this_version")
        for format, magic in (("json", b"{"), ("docx", b"PK"), ("pdf", b"%PDF")):
            self.assertTrue(export_note_bytes(note, format).startswith(magic))
        exported = json.loads(export_note_bytes(note, "json"))
        self.assertEqual(exported["therapeutic_plan"], note["therapeutic_plan"])

    def test_direct_review_as_suggested_when_complete(self):
        base = therapy.build_reference(None, "adult")
        base["sections"] = {key: f"Explicit canonical action for {key}." for key in therapy.SECTION_KEYS}
        with patch.object(therapy, "build_reference", return_value=base):
            note = add_manual_draft(clean_note())
            review(note)
            self.assertEqual(note["therapeutic_review"]["mode"], "as_suggested")
            self.assertFalse(validate_for_export(note)["blocked"])

    def test_edit_requires_new_review_and_changes_digest(self):
        note = review(complete_draft(add_manual_draft(clean_note())))
        old_digest = note["therapeutic_review"]["plan_digest"]
        note["therapeutic_plan"]["sections"]["disposition"] += " Cambio de plan."
        self.assertTrue(validate_for_export(note)["blocked"])
        review(note)
        self.assertNotEqual(note["therapeutic_review"]["plan_digest"], old_digest)
        self.assertFalse(validate_for_export(note)["blocked"])

    def test_case_changes_and_receipt_copy_cannot_export(self):
        original = review(complete_draft(add_manual_draft(clean_note())))
        mutations = (
            lambda n: n.update(language="en"),
            lambda n: n["encounter"].update(encounter_id="different-episode"),
            lambda n: n["history"].update(chief_complaint="Different clinical input"),
            lambda n: n["history"]["chronic_medications"].append({"name": "changed", "dose": None, "schedule": None, "source": None}),
            lambda n: n["assessment"]["likely_diagnoses"].clear(),
        )
        # A genuinely different assessment is also in the signed context.
        mutations = mutations[:-1] + (lambda n: n["assessment"].update(active_problems=["new problem"]),)
        for mutate in mutations:
            note = deepcopy(original); mutate(note)
            self.assertTrue(validate_for_export(note)["blocked"])
            self.assertTrue(therapy.validate({"note": note, "confirmations": {"individualized": True, "medication_safety_reviewed": True}})["blocked"])

    def test_export_flag_and_note_review_timestamp_do_not_change_plan(self):
        note = review(complete_draft(add_manual_draft(clean_note())))
        note["clinician_validation"]["reviewed_at"] = "2026-11-26T12:00:00Z"
        note["privacy"]["export_allowed"] = True
        self.assertFalse(validate_for_export(note)["blocked"])

    def test_forged_metadata_review_or_confirmation_blocked(self):
        original = review(complete_draft(add_manual_draft(clean_note())))
        mutations = (
            lambda n: n["therapeutic_review"].update(validation_token="0" * 64),
            lambda n: n["therapeutic_review"].update(validation_token="中" * 64),
            lambda n: n["therapeutic_review"].update(reviewed_at="2030-01-01"),
            lambda n: n["therapeutic_review"].update(mode="as_suggested"),
            lambda n: n["therapeutic_plan"]["context"].update(weight_kg=99),
            lambda n: n["therapeutic_plan"].update(reference_text="Modified source"),
            lambda n: n["therapeutic_plan"]["medication_safety"].update(actionable=True),
        )
        for mutate in mutations:
            note = deepcopy(original); mutate(note)
            self.assertTrue(validate_for_export(note)["blocked"])
        for confirmation in ({}, {"individualized": True, "medication_safety_reviewed": False}, {"individualized": 1, "medication_safety_reviewed": "true"}):
            self.assertTrue(therapy.validate({"note": original, "confirmations": confirmation})["blocked"])

    def test_changed_canonical_source_invalidates_approval(self):
        note = review(complete_draft(add_manual_draft(clean_note())))
        current = therapy.build_reference(None, "adult"); current["source_revision"] = "9" * 64
        with patch.object(therapy, "build_reference", return_value=current):
            self.assertTrue(validate_for_export(note)["blocked"])

    def test_unknown_allergy_review_and_weight_based_dose_need_context(self):
        for context, text in (({"allergies_reviewed": False}, "No medication indicated."), ({}, "Synthetic weight-based medication mg/kg only for testing.")):
            note = complete_draft(add_manual_draft(clean_note(5), **context))
            note["therapeutic_plan"]["sections"]["medications"] = text
            result = therapy.validate({"note": note, "confirmations": {"individualized": True, "medication_safety_reviewed": True}})
            self.assertTrue(result["blocked"])

    def test_alternative_weight_and_surface_notation_cannot_skip_context(self):
        for notation in ("mg kg⁻¹", "mg/kg", "mg per kg", "mg kg^-1", "mg/m²", "mg/m2", "mg m⁻²"):
            for section in ("medications", "initial_actions"):
                with self.subTest(notation=notation, section=section):
                    note = complete_draft(add_manual_draft(clean_note(5)))
                    note["therapeutic_plan"]["sections"][section] = f"Synthetic formula {notation} for testing."
                    self.assertTrue(therapy.validate({"note": note, "confirmations": {"individualized": True, "medication_safety_reviewed": True}})["blocked"])

    def test_boolean_only_and_omitted_plan_do_not_export_treatment(self):
        note = clean_note()
        note["assessment"]["treatment_suggestions"] = [{"action": "Unreviewed treatment", "source_modules": []}]
        self.assertTrue(validate_for_export(note)["blocked"])
        with self.assertRaises(ValueError):
            export_note_bytes(note, "json")
        signed = review(complete_draft(add_manual_draft(clean_note())))
        del signed["therapeutic_plan"]
        self.assertTrue(validate_for_export(signed)["blocked"])

    def test_export_uses_one_plan_not_legacy_treatment_or_disposition(self):
        note = clean_note()
        note["assessment"]["treatment_suggestions"] = [{"action": "OLD MEDICATION NOT TO EXPORT"}]
        note["assessment"]["disposition"] = [{"action": "OLD DISPOSITION NOT TO EXPORT"}]
        review(complete_draft(add_manual_draft(note)))
        rendered = json.dumps(note_to_sections(note), ensure_ascii=False)
        self.assertNotIn("OLD MEDICATION", rendered)
        self.assertNotIn("OLD DISPOSITION", rendered)
        exported = json.loads(export_note_bytes(note, "json"))
        self.assertEqual(exported["assessment"]["treatment_suggestions"], [])
        self.assertEqual(exported["assessment"]["disposition"], [])
        self.assertEqual(exported["assessment"]["reassessment"], [])
        self.assertFalse(validate_for_export(exported)["blocked"])
        for value in note["therapeutic_plan"]["sections"].values():
            self.assertEqual(rendered.count(value), 1)

    def test_privacy_in_new_manual_selection_and_edited_plan(self):
        note = clean_note()
        response = therapy.suggest({"note": note, "selection": {"label": "Email test@example.com", "module_id": None, "selection": "manual"}, "context": {"weight_kg": None, "allergies_reviewed": True}})
        self.assertTrue(response["blocked"])
        note = complete_draft(add_manual_draft(note))
        note["therapeutic_plan"]["sections"]["medications"] = "test@example.com"
        self.assertTrue(therapy.validate({"note": note})["blocked"])

    def test_exact_public_source_does_not_bypass_edited_text_privacy(self):
        note = clean_note()
        response = therapy.suggest({"note": note, "selection": {"label": "Airway assessment", "module_id": "airway-rsi", "selection": "manual"}, "context": {"weight_kg": 70, "allergies_reviewed": True}})
        self.assertFalse(response["blocked"], response["issues"])
        note["therapeutic_plan"] = response["plan"]
        self.assertTrue(therapy.trusted_source_paths(note))
        note["therapeutic_plan"]["sections"]["medications"] += "\nNombre: Juan Perez"
        self.assertNotIn(("therapeutic_plan", "sections", "medications"), therapy.trusted_source_paths(note))
        self.assertTrue(therapy.validate({"note": note})["blocked"])
        note["therapeutic_plan"]["reference_text"] += "\nNombre: Juan Perez"
        self.assertEqual(therapy.trusted_source_paths(note), set())

    def test_literal_jsonpath_keys_cannot_impersonate_a_public_source(self):
        for key in ("therapeutic_plan.reference_text", "therapeutic_plan.sections.medications", "therapeutic_plan.missing_requirements[0]"):
            with self.subTest(key=key):
                note = complete_draft(add_manual_draft(clean_note()))
                note[key] = "synthetic@example.invalid"
                result = therapy.suggest({"note": note, "selection": note["therapeutic_plan"]["diagnosis"], "context": note["therapeutic_plan"]["context"]})
                self.assertTrue(result["blocked"])
                self.assertTrue(any(x.get("code") == "POSSIBLE_IDENTIFIER_IN_TEXT" for x in result["issues"]))
                self.assertTrue(therapy.validate({"note": note, "confirmations": {"individualized": True, "medication_safety_reviewed": True}})["blocked"])

    def test_all_catalog_sources_pass_privacy_without_screening_as_patient_text(self):
        from therapeutic_plan_sources import catalog
        for item in catalog()["modules"]:
            for population in item["populations"]:
                with self.subTest(module=item["id"], population=population):
                    result = therapy.suggest({"note": clean_note(45 if population == "adult" else 5), "selection": {"label": item["title"], "module_id": item["id"], "selection": "manual"}, "context": {"weight_kg": 70 if population == "adult" else 20, "allergies_reviewed": True}})
                    self.assertFalse(result["blocked"], result["issues"])

    def test_bell_protocol_selects_one_condition_and_does_not_extrapolate_to_children(self):
        selection = {"label": "Parálisis facial de Bell", "module_id": "ent-emergencies:bell-palsy", "selection": "manual"}
        for age in (45, 18, 17, 12, 5):
            result = therapy.suggest({"note": clean_note(age), "selection": selection, "context": {"weight_kg": None, "allergies_reviewed": True}})
            self.assertFalse(result["blocked"], result["issues"])
            plan = result["plan"]
            self.assertEqual(plan["source_refs"][0]["module_id"], "ent-emergencies")
            self.assertIn("### bell-palsy", plan["reference_text"])
            self.assertNotIn("- Airway-threatening ENT", plan["reference_text"])
            if age >= 18:
                self.assertTrue(all(plan["sections"].values()), plan["sections"])
                self.assertIn("25 mg", plan["sections"]["medications"])
            else:
                self.assertFalse(any(plan["sections"].values()))

    def test_asthma_diagnostic_selection_uses_age_appropriate_canonical_module(self):
        from clinical_note_diagnostic_engine import analyze, load_rules
        asthma_rules = {rule["diagnosis"]: rule["id"] for rule in load_rules()["syndromes"]
                        if rule["id"] in ("acute-severe-asthma", "pediatric-acute-asthma")}
        for years, months, expected in ((12, None, "pediatric-acute-asthma"),
                                        (17, None, "pediatric-acute-asthma"),
                                        (None, 204, "pediatric-acute-asthma"),
                                        (18, None, "acute-severe-asthma")):
            with self.subTest(years=years, months=months):
                note = clean_note(years)
                note["encounter"]["age"]["months"] = months
                note["history"]["chief_complaint"] = "Asma pediátrica con wheezing y broncoespasmo"
                analysis = analyze(note, apply_to_note=True)
                self.assertFalse(analysis["blocked"], analysis["issues"])
                analyzed_note = analysis["note"]
                candidates = analysis["assessment"]["likely_diagnoses"] + analysis["assessment"]["differential_diagnoses"]
                asthma_candidates = [item for item in candidates if item["diagnosis"] in asthma_rules]
                self.assertEqual(len(asthma_candidates), 2)
                for candidate in asthma_candidates:
                    self.assertEqual(candidate["source_modules"][0], expected)
                    result = therapy.suggest({"note": analyzed_note, "selection": {
                        "label": candidate["diagnosis"], "module_id": candidate["source_modules"][0],
                        "selection": "diagnostic"}, "context": {"weight_kg": 60, "allergies_reviewed": True}})
                    self.assertFalse(result["blocked"], result["issues"])
                    self.assertEqual(result["plan"]["source_refs"][0]["module_id"], expected)
                    self.assertEqual(result["plan"]["population"], "adult" if expected == "acute-severe-asthma" else "pediatric")
                    self.assertTrue(result["plan"]["sections"]["medications"])

    def test_unknown_age_does_not_reassign_asthma_reference_or_allow_therapy(self):
        from clinical_note_diagnostic_engine import analyze, load_rules
        asthma_rules = {rule["diagnosis"]: rule["id"] for rule in load_rules()["syndromes"]
                        if rule["id"] in ("acute-severe-asthma", "pediatric-acute-asthma")}
        note = clean_note(None)
        note["history"]["chief_complaint"] = "Asma pediátrica con wheezing y broncoespasmo"
        analysis = analyze(note, apply_to_note=True)
        self.assertFalse(analysis["blocked"], analysis["issues"])
        candidates = analysis["assessment"]["likely_diagnoses"] + analysis["assessment"]["differential_diagnoses"]
        asthma_candidates = [item for item in candidates if item["diagnosis"] in asthma_rules]
        self.assertEqual(len(asthma_candidates), 2)
        for candidate in asthma_candidates:
            self.assertEqual(candidate["source_modules"], [asthma_rules[candidate["diagnosis"]]])
            result = therapy.suggest({"note": analysis["note"], "selection": {
                "label": candidate["diagnosis"], "module_id": candidate["source_modules"][0],
                "selection": "diagnostic"}, "context": {"weight_kg": 60, "allergies_reviewed": True}})
            self.assertTrue(result["blocked"])
            self.assertTrue(any(issue["code"] == "THERAPY_AGE_REQUIRED" for issue in result["issues"]))

    def test_http_facade_and_supported_languages(self):
        status, catalog = dispatch("/api/clinical-note/therapy/catalog", {})
        self.assertEqual(status, 200); self.assertTrue(catalog["modules"])
        for language in ("es-ES", "pt-PT", "en", "zh"):
            note = review(complete_draft(add_manual_draft(clean_note(language=language))))
            sections = note_to_sections(note)
            self.assertTrue(any(note["therapeutic_plan"]["sections"]["medications"] in lines for _, lines in sections))


if __name__ == "__main__":
    unittest.main()
