"""Synthetic boundary tests for one ceftriaxone sepsis dose guard."""

from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from pediatric_antibiotic_calculator import calculate, load_registry
from ceftriaxone_sepsis_safety import TARGET_ENTRY_ID, DOSE_GUARD_POLICY

REGISTRIES = (
    ROOT / "qa/pediatric-antibiotics.json",
    ROOT / "qa/pediatric-antibiotics-by-syndrome.json",
)


def synthetic_context(birth_date="2018-11-15", assessment_date="2026-11-15", **changes):
    context = {
        "birth_date": birth_date,
        "assessment_date": assessment_date,
        "community_acquired": True,
        "known_infection_focus": False,
        "ceftriaxone_resistance_history": False,
        "route": "IV",
        "calcium_iv_mode": "none",
        "premature": False,
        "neonatal_bilirubin_risk": False,
        "diluent_contains_lidocaine": False,
        "diluent_contains_calcium": False,
        "renal_hepatic_status": "no_impairment",
        "listeria_coverage_planned": True,
    }
    return {**context, **changes}


class CeftriaxoneSepsisSafetyTests(unittest.TestCase):
    def reject(self, code, context, weight=20, registry=REGISTRIES[0]):
        with self.assertRaisesRegex(ValueError, "^" + code + ":"):
            calculate(TARGET_ENTRY_ID, weight, registry, context=context)

    def test_both_catalogs_preserve_dose_sources_and_pending_status(self):
        results = []
        for registry in REGISTRIES:
            with self.subTest(registry=registry.name):
                entry = load_registry(registry)[TARGET_ENTRY_ID]
                result = calculate(TARGET_ENTRY_ID, 20, registry, context=synthetic_context())
                self.assertEqual(result["dose"], 1600)
                self.assertEqual(result["dose_unit"], "mg")
                self.assertEqual(result["dose_per_kg"], 80)
                self.assertEqual(result["dose_per_kg_unit"], "mg/kg")
                self.assertEqual(result["route"], "IV")
                self.assertEqual(result["frequency"], "once daily")
                self.assertEqual(result["dose_guard_policy"], DOSE_GUARD_POLICY)
                self.assertEqual(result["source_refs"], entry["source_refs"])
                self.assertEqual(result["safety_notes"], entry["safety_notes"])
                self.assertEqual(result["population"], entry["population"])
                self.assertEqual(result["clinical_status"], "CLINICAL_REVIEW_REQUIRED")
                self.assertEqual(result["clinical_release_status"], "CLINICALLY_PENDING")
                self.assertEqual(result["age_years_completed"], 8)
                self.assertNotIn("birth_date", result)
                self.assertNotIn("assessment_date", result)
                self.assertNotIn("2018-11-15", json.dumps(result))
                self.assertNotIn("volume_ml", result)
                results.append(result)
        self.assertEqual(results[0], results[1])

    def test_27_28_29_day_boundaries(self):
        assessed = date(2026, 11, 15)
        for days in (27, 28, 29):
            context = synthetic_context((assessed - timedelta(days=days)).isoformat())
            with self.subTest(days=days):
                if days == 27:
                    self.reject("OUTSIDE_VERIFIED_AGE_SCOPE", context, 3.5)
                else:
                    result = calculate(TARGET_ENTRY_ID, 3.5, context=context)
                    self.assertEqual(result["age_days"], days)
                    self.assertEqual(result["dose"], 280)

    def test_sixteenth_birthday_and_leap_calendar(self):
        for birth, before, birthday in (
            ("2010-11-15", "2026-11-14", "2026-11-15"),
            ("2012-02-29", "2028-02-28", "2028-02-29"),
        ):
            with self.subTest(birth=birth):
                result = calculate(TARGET_ENTRY_ID, 49, context=synthetic_context(birth, before))
                self.assertEqual(result["age_years_completed"], 15)
                self.reject("OUTSIDE_VERIFIED_AGE_SCOPE", synthetic_context(birth, birthday), 49)

    def test_three_month_boundary_is_calendar_not_ninety_days(self):
        for birth, before, threshold in (
            ("2026-01-31", "2026-04-29", "2026-04-30"),
            ("2026-02-01", "2026-04-30", "2026-05-01"),
        ):
            with self.subTest(birth=birth):
                self.reject("LISTERIA_COVERAGE_REQUIRED", synthetic_context(birth, before, listeria_coverage_planned=False), 5)
                context = synthetic_context(birth, threshold)
                context.pop("listeria_coverage_planned")
                result = calculate(TARGET_ENTRY_ID, 5, context=context)
                self.assertFalse(result["under_three_calendar_months"])

    def test_listeria_plan_requires_explicit_true_before_three_months(self):
        for value in (None, False, 1, "true", [], {}):
            with self.subTest(value=value):
                self.reject("LISTERIA_COVERAGE_REQUIRED", synthetic_context("2026-10-01", listeria_coverage_planned=value), 4)

    def test_weight_boundary_does_not_invent_adult_dose(self):
        self.assertAlmostEqual(calculate(TARGET_ENTRY_ID, 49.999, context=synthetic_context())["dose"], 3999.92)
        for weight in (50, 80, 1e308):
            with self.subTest(weight=weight):
                self.reject("ADULT_INDICATION_REGIMEN_REQUIRED", synthetic_context(), weight)

    def test_invalid_weight_is_rejected_before_missing_context(self):
        for value in (0, -1, True, False, "20", None, {}, [], float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                self.reject("INVALID_WEIGHT", None, value)

    def test_missing_or_nonobject_context_fails_closed(self):
        for context in (None, [], "{}", True, 1):
            with self.subTest(context=context):
                self.reject("CONTEXT_REQUIRED", context)

    def test_dates_are_explicit_strict_iso_and_ordered(self):
        for key in ("birth_date", "assessment_date"):
            for value in (None, True, 20260101, "20261115", "2026-W46-7", "15/11/2026"):
                with self.subTest(key=key, value=value):
                    self.reject("AGE_CONTEXT_REQUIRED", synthetic_context(**{key: value}))
            self.reject("INVALID_AGE_CONTEXT", synthetic_context(**{key: "2026-02-30"}))
        self.reject("INVALID_AGE_CONTEXT", synthetic_context("2026-11-16", "2026-11-15"))

    def test_sepsis_context_is_strict_and_does_not_select_another_pathway(self):
        for key, excluded in (("community_acquired", False), ("known_infection_focus", True), ("ceftriaxone_resistance_history", True)):
            for value in (excluded, None, 0, 1, "false"):
                with self.subTest(key=key, value=value):
                    self.reject("SEPSIS_CONTEXT_REVIEW_REQUIRED", synthetic_context(**{key: value}))

    def test_iv_route_and_diluents(self):
        for route in ("IM", None, "iv", 1):
            self.reject("ROUTE_NOT_SUPPORTED", synthetic_context(route=route))
        self.reject("IV_LIDOCAINE_CONTRAINDICATED", synthetic_context(diluent_contains_lidocaine=True))
        self.reject("IV_CALCIUM_DILUENT_CONTRAINDICATED", synthetic_context(diluent_contains_calcium=True))
        for key in ("diluent_contains_lidocaine", "diluent_contains_calcium", "premature"):
            for value in (None, 0, 1, "false"):
                with self.subTest(key=key, value=value):
                    self.reject("CONTEXT_REVIEW_REQUIRED", synthetic_context(**{key: value}))

    def test_neonatal_calcium_includes_day_28(self):
        for mode in ("planned", "sequential", "simultaneous"):
            context = synthetic_context("2026-10-18", calcium_iv_mode=mode, calcium_line_changed_or_flushed=True)
            with self.subTest(mode=mode):
                self.reject("NEONATAL_CALCIUM_CONTRAINDICATED", context, 3.5)

    def test_calcium_after_day_28_sequential_requires_line_check(self):
        for value in (None, False, 1, "true"):
            context = synthetic_context("2026-10-17", calcium_iv_mode="sequential", calcium_line_changed_or_flushed=value)
            self.reject("CALCIUM_SEQUENTIAL_LINE_CHECK_REQUIRED", context, 3.5)
        result = calculate(TARGET_ENTRY_ID, 3.5, context=synthetic_context("2026-10-17", calcium_iv_mode="sequential", calcium_line_changed_or_flushed=True))
        self.assertEqual(result["age_days"], 29)

    def test_planned_simultaneous_and_tpn_calcium_require_review(self):
        self.reject("CALCIUM_ADMINISTRATION_REVIEW_REQUIRED", synthetic_context(calcium_iv_mode="planned"))
        self.reject("CALCIUM_SIMULTANEOUS_REVIEW_REQUIRED", synthetic_context(calcium_iv_mode="simultaneous"))
        self.reject("CALCIUM_SIMULTANEOUS_REVIEW_REQUIRED", synthetic_context(calcium_iv_mode="simultaneous", parenteral_nutrition=True, separate_lines=True, specialist_approved=True))
        for value in (None, "unknown", True, {}, []):
            self.reject("CALCIUM_CONTEXT_REQUIRED", synthetic_context(calcium_iv_mode=value))

    def test_prematurity_41_week_boundary_and_required_integer(self):
        base = synthetic_context("2026-10-16", premature=True)
        for value in (None, True, 288.0, "288", -1, float("inf")):
            with self.subTest(value=value):
                self.reject("POSTMENSTRUAL_AGE_REQUIRED", {**base, "postmenstrual_age_days": value}, 3.5)
        self.reject("PREMATURITY_CONTRAINDICATED", {**base, "postmenstrual_age_days": 287}, 3.5)
        self.assertEqual(calculate(TARGET_ENTRY_ID, 3.5, context={**base, "postmenstrual_age_days": 288})["dose"], 280)
        assessed = date(2026, 11, 15)
        context = synthetic_context((assessed - timedelta(days=288)).isoformat(), premature=True)
        self.assertEqual(calculate(TARGET_ENTRY_ID, 8, context=context)["age_days"], 288)

    def test_postmenstrual_age_must_be_consistent_with_premature_birth(self):
        assessed = date(2026, 11, 15)
        for chronological, postmenstrual in ((28, 288), (30, 30), (30, 29), (30, 289), (288, 287), (288, 547)):
            with self.subTest(chronological=chronological, postmenstrual=postmenstrual):
                context = synthetic_context(
                    (assessed - timedelta(days=chronological)).isoformat(),
                    premature=True, postmenstrual_age_days=postmenstrual,
                )
                self.reject("POSTMENSTRUAL_AGE_INCONSISTENT", context, 3.5)
        late_context = synthetic_context((assessed - timedelta(days=288)).isoformat(), premature=True)
        for value in (None, True, "500", float("inf")):
            self.reject("POSTMENSTRUAL_AGE_REQUIRED", {**late_context, "postmenstrual_age_days": value}, 8)
        self.assertEqual(calculate(TARGET_ENTRY_ID, 8, context={**late_context, "postmenstrual_age_days": 500})["dose"], 640)

    def test_day_28_bilirubin_risk_and_day_29_distinction(self):
        self.reject("NEONATAL_BILIRUBIN_CONTRAINDICATED", synthetic_context("2026-10-18", neonatal_bilirubin_risk=True), 3.5)
        for value in (None, 0, "false"):
            self.reject("CONTEXT_REVIEW_REQUIRED", synthetic_context("2026-10-18", neonatal_bilirubin_risk=value), 3.5)
        context = synthetic_context("2026-10-17")
        context.pop("neonatal_bilirubin_risk")
        self.assertEqual(calculate(TARGET_ENTRY_ID, 3.5, context=context)["age_days"], 29)

    def test_renal_clearance_boundary_does_not_apply_an_automatic_cap(self):
        for clearance in (0, 9.999):
            self.reject("RENAL_REGIMEN_REVIEW_REQUIRED", synthetic_context(renal_hepatic_status="isolated_renal", creatinine_clearance_ml_min=clearance))
        self.assertEqual(calculate(TARGET_ENTRY_ID, 20, context=synthetic_context(renal_hepatic_status="isolated_renal", creatinine_clearance_ml_min=10))["dose"], 1600)
        for value in (None, -1, True, "10", float("nan"), float("inf")):
            self.reject("RENAL_CONTEXT_REQUIRED", synthetic_context(renal_hepatic_status="isolated_renal", creatinine_clearance_ml_min=value))

    def test_hepatic_and_combined_impairment_require_specific_review(self):
        for severity in ("mild", "moderate"):
            self.assertEqual(calculate(TARGET_ENTRY_ID, 20, context=synthetic_context(renal_hepatic_status="isolated_hepatic", hepatic_impairment_severity=severity))["dose"], 1600)
        for severity in (None, "severe", "unknown", True):
            self.reject("HEPATIC_REGIMEN_REVIEW_REQUIRED", synthetic_context(renal_hepatic_status="isolated_hepatic", hepatic_impairment_severity=severity))
        for status in ("severe_combined", "unknown"):
            self.reject("RENAL_HEPATIC_REGIMEN_REVIEW_REQUIRED", synthetic_context(renal_hepatic_status=status))
        for status in (None, "normal", True, {}):
            self.reject("RENAL_HEPATIC_CONTEXT_REQUIRED", synthetic_context(renal_hepatic_status=status))

    def test_missing_required_fields_never_produce_a_dose(self):
        required = ("birth_date", "assessment_date", "community_acquired", "known_infection_focus", "ceftriaxone_resistance_history", "calcium_iv_mode", "premature", "diluent_contains_lidocaine", "diluent_contains_calcium", "renal_hepatic_status")
        for key in required:
            context = synthetic_context()
            context.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError):
                calculate(TARGET_ENTRY_ID, 20, context=context)

    def test_custom_registry_cannot_bypass_missing_or_altered_policy(self):
        mutations = (
            lambda e: e.pop("dose_guard_policy"),
            lambda e: e.update(dose_guard_policy="disabled"),
            lambda e: e.pop("population"),
            lambda e: e["population"].update(maximum_age_years_exclusive=18),
            lambda e: e["population"].update(minimum_age_days=0),
            lambda e: e["population"].update(maximum_weight_kg_exclusive=100),
            lambda e: e.update(dose_per_kg=800),
            lambda e: e.update(route="IM"),
            lambda e: e.update(dose_output_unit="mg/kg"),
            lambda e: e.update(source_refs=[]),
            lambda e: e.update(safety_notes=[]),
        )
        for registry in REGISTRIES:
            data = json.loads(registry.read_text(encoding="utf-8"))
            for index, mutation in enumerate(mutations):
                with self.subTest(registry=registry.name, mutation=index), tempfile.TemporaryDirectory() as tmp:
                    changed = deepcopy(data)
                    entry = next(e for e in changed["entries"] if e["id"] == TARGET_ENTRY_ID)
                    mutation(entry)
                    path = Path(tmp) / "registry.json"
                    path.write_text(json.dumps(changed), encoding="utf-8")
                    self.reject("DOSE_GUARD_POLICY_MISMATCH", synthetic_context(), registry=path)

    def test_other_entries_keep_their_existing_interface_and_result(self):
        before = calculate("lower-uti-trimethoprim", 20)
        self.assertEqual(before["dose"], 80)
        self.assertEqual(before["dose_unit"], "mg/kg")
        self.assertNotIn("clinical_status", before)
        self.assertEqual(before, calculate("lower-uti-trimethoprim", 20, context={"unrelated": True}))
        self.assertEqual(calculate("pyelonephritis-ceftriaxone", 20)["dose_range"], [1000, 1600])

    def test_injected_concentration_cannot_create_an_administration_volume(self):
        for registry in REGISTRIES:
            data = json.loads(registry.read_text(encoding="utf-8"))
            for concentration in (40, 0, False, "40"):
                with self.subTest(registry=registry.name, concentration=concentration), tempfile.TemporaryDirectory() as tmp:
                    changed = deepcopy(data)
                    entry = next(e for e in changed["entries"] if e["id"] == TARGET_ENTRY_ID)
                    entry["source_concentration_per_ml"] = concentration
                    path = Path(tmp) / "registry.json"
                    path.write_text(json.dumps(changed), encoding="utf-8")
                    self.reject("DOSE_GUARD_POLICY_MISMATCH", synthetic_context(), registry=path)

    def test_cli_reads_explicit_json_object_and_fails_without_it(self):
        command = [sys.executable, str(ROOT / "scripts/pediatric_antibiotic_calculator.py"), TARGET_ENTRY_ID, "20"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "context.json"
            path.write_text(json.dumps(synthetic_context()), encoding="utf-8")
            result = subprocess.run(command + ["--context-json", str(path)], cwd=tmp, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["dose_unit"], "mg")
            path.write_text("[]", encoding="utf-8")
            bad = subprocess.run(command + ["--context-json", str(path)], cwd=tmp, capture_output=True, text=True, check=False)
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(bad.stdout, "")
            self.assertIn("INVALID_CONTEXT", bad.stderr)
        missing = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(missing.stdout, "")
        self.assertIn("CONTEXT_REQUIRED", missing.stderr)


if __name__ == "__main__":
    unittest.main()
