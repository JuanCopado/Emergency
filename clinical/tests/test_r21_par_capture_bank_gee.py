"""R21-PAR · capture, synthetic bank and optional GEE reference (laboratory only, no study executed)."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "lab"))
import human_factors_tools as hf  # noqa: E402
from human_factors import capture, gee_reference, synthetic_bank as bank  # noqa: E402
from human_factors import layer7_simulator as sim  # noqa: E402


def trial(**over):
    base = dict(participant="HF1-abc", role="physician", scenario_id="SKI-11", condition="prototype", period=1,
                intended_modality="skin_wound", platform="web", order_in_period=1, start_ms=1000)
    base.update(over)
    return capture.TrialRecorder(**base)


class Capture(unittest.TestCase):
    def test_correct_confirmation(self):
        t = trial(); t.event("select", 1500, "skin_wound"); t.event("confirm", 4500); t.answer_comprehension(True)
        r = t.record()
        self.assertEqual((r["seconds"], r["chosen_modality"], r["changed_modality_count"], r["confirmed"]), (3.5, "skin_wound", 0, True))

    def test_change_then_bypass_flags(self):
        t = trial(); t.event("select", 1200, "skin_wound"); t.event("change", 2000, "xray"); t.event("confirm", 3000)
        r = t.record()
        f = hf.flags(r)
        self.assertEqual(r["changed_modality_count"], 1)
        self.assertTrue(f["bypass"] and f["false_cancellation"] and f["confirmation_error"])

    def test_cancel_has_no_chosen_modality(self):
        t = trial(); t.event("select", 1200, "skin_wound"); t.event("cancel", 2000)
        r = t.record()
        self.assertFalse(r["confirmed"]); self.assertIsNone(r["chosen_modality"])
        self.assertTrue(hf.flags(r)["false_cancellation"])

    def test_invalid_sequences_rejected(self):
        for steps in ([("confirm", 1)], [("change", 1, "xray")], [("select", 1, "skin_wound"), ("select", 2, "ecg")],
                      [("select", 1, "skin_wound"), ("change", 2, "skin_wound")], [("select", 5, "nope")],
                      [("select", 9, "ecg"), ("confirm", 8)], [("bogus", 1)]):
            t = trial()
            with self.assertRaises(ValueError, msg=str(steps)):
                for s in steps:
                    t.event(s[0], s[1], s[2] if len(s) > 2 else None)

    def test_closed_trial_and_open_record(self):
        t = trial()
        with self.assertRaises(ValueError):
            t.record()
        t.event("select", 1100, "ecg"); t.event("confirm", 1200)
        with self.assertRaises(ValueError):
            t.event("change", 1300, "xray")

    def test_bad_times_and_codes(self):
        for bad in (-1, float("nan"), True, "1"):
            with self.assertRaises(ValueError):
                trial(start_ms=bad)
        t = trial(participant="Dr. Perez")
        t.event("select", 1100, "ecg"); t.event("confirm", 1200)
        with self.assertRaises(ValueError):
            t.record()

    def test_opaque_participant(self):
        a = capture.opaque_participant("custodian-secret-0001", 1)
        self.assertEqual(a, capture.opaque_participant("custodian-secret-0001", 1))
        self.assertNotEqual(a, capture.opaque_participant("custodian-secret-0001", 2))
        self.assertNotEqual(a, capture.opaque_participant("custodian-secret-0002", 1))
        self.assertRegex(a, hf.CODE)
        for bad in (("short", 1), ("custodian-secret-0001", 0), ("custodian-secret-0001", True)):
            with self.assertRaises(ValueError):
                capture.opaque_participant(*bad)

    def test_collect_rejects_what_the_tool_rejects(self):
        t = trial(); t.event("select", 1100, "skin_wound"); t.event("confirm", 1200)
        r = t.record()
        self.assertEqual(capture.collect([r])["count"], 1)
        with self.assertRaises(ValueError):
            capture.collect([r, dict(r)])           # duplicate participant/scenario/condition
        with self.assertRaises(ValueError):
            capture.collect([r, dict(r, scenario_id="SKI-12", condition="baseline")])  # mixed conditions in one period
        with self.assertRaises(ValueError):
            capture.collect([])


class Bank(unittest.TestCase):
    def test_manifest_reproducible_balanced_disjoint(self):
        m1, m2 = bank.build_manifest("s", 2), bank.build_manifest("s", 2)
        self.assertEqual(m1, m2)
        self.assertNotEqual(m1, bank.build_manifest("other", 2))
        self.assertEqual(bank.audit_manifest(m1), [])
        banks = {b: {s["case_code"] for s in m1["scenarios"] if s["bank_set"] == b} for b in hf.BANK_SETS}
        self.assertFalse(banks["set1"] & banks["set2"])
        self.assertEqual(len({s["stimulus_sha256"] for s in m1["scenarios"]}), len(m1["scenarios"]))

    def test_audit_detects_problems(self):
        m = bank.build_manifest("s", 2)
        broken = json.loads(json.dumps(m)); broken["scenarios"] = [s for s in broken["scenarios"] if not (s["intended_modality"] == "ecg" and s["bank_set"] == "set2")]
        self.assertTrue(any("ecg" in p for p in bank.audit_manifest(broken)))
        unbal = json.loads(json.dumps(m)); unbal["scenarios"] = unbal["scenarios"][:-1]
        self.assertTrue(any("unbalanced" in p for p in bank.audit_manifest(unbal)))
        nohash = json.loads(json.dumps(m)); del nohash["scenarios"][0]["stimulus_sha256"]
        self.assertTrue(any("hashes" in p for p in bank.audit_manifest(nohash)))
        dup = json.loads(json.dumps(m)); dup["scenarios"][1]["stimulus_sha256"] = dup["scenarios"][0]["stimulus_sha256"]
        with self.assertRaises(ValueError):
            bank.audit_manifest(dup)
        both = json.loads(json.dumps(m)); both["scenarios"][1]["case_code"] = both["scenarios"][0]["case_code"]; both["scenarios"][1]["bank_set"] = "set2"
        with self.assertRaises(ValueError):
            bank.audit_manifest(both)
        with self.assertRaises(ValueError):
            bank.build_manifest("s", 0)

    def test_descriptor_bank_matches_independent_expectations(self):
        for case_id, descriptor, expected in bank.layer7_descriptors():
            out = sim.evaluate(descriptor)
            got = out["document"].get("trigger_id")
            self.assertEqual(got, expected, case_id)
            self.assertTrue(out["simulated"])
            if expected:
                self.assertFalse(out["document"]["send_allowed"])

    def test_fingerprint_changes_with_content(self):
        m, d = bank.build_manifest("s"), bank.layer7_descriptors()
        f = bank.fingerprint(m, d)
        self.assertEqual(f, bank.fingerprint(bank.build_manifest("s"), bank.layer7_descriptors()))
        self.assertNotEqual(f["manifest_sha256"], bank.fingerprint(bank.build_manifest("t"), d)["manifest_sha256"])
        d2 = list(d); d2[0] = (d2[0][0], dict(d2[0][1], signature_kind="png"), d2[0][2])
        self.assertNotEqual(f["descriptors_sha256"], bank.fingerprint(m, d2)["descriptors_sha256"])

    def test_synthetic_session_runs_through_tool_and_export(self):
        m = bank.build_manifest("s", 2)
        rows = bank.synthetic_session(m, 12)
        package = hf.export_package({"manifest": m, "records": rows}, resamples=200, seed="s")
        self.assertEqual(package["study_status"], "NOT_EXECUTED_TOOLING_ONLY")
        self.assertEqual(hf.sequences(rows).keys(), {r["participant"] for r in rows})

    def test_edge_datasets_are_handled(self):
        m = bank.build_manifest("s", 1)
        rows = bank.synthetic_session(m, 12)
        for r in rows:                                   # all events negative
            r["chosen_modality"] = r["initial_modality"] = r["intended_modality"]
        s0 = hf.summarize(rows, 200, "s")
        self.assertIn("zero_event_report", json.dumps(s0))
        for r in rows:                                   # all events positive
            wrong = "ecg" if r["intended_modality"] != "ecg" else "xray"
            r["chosen_modality"] = wrong
        hf.summarize(rows, 200, "s")
        with self.assertRaises(ValueError):
            hf.validate_records(rows + [dict(rows[0])])  # duplicate
        with self.assertRaises(ValueError):
            hf.validate_records([dict(rows[0], seconds=float("nan"))])
        with self.assertRaises(json.JSONDecodeError):
            json.loads("{malformed")


HAS_SM = gee_reference.available()


class Gee(unittest.TestCase):
    def test_status_is_honest(self):
        s = gee_reference.status()
        self.assertEqual(s["glmm"], "NOT_IMPLEMENTED")
        self.assertEqual(s["gee"], "AVAILABLE_OPTIONAL" if HAS_SM else "NOT_IMPLEMENTED")

    def test_design_denominators_follow_tool_flags(self):
        m = bank.build_manifest("s", 2)
        rows = bank.synthetic_session(m, 8)
        d = gee_reference.design(rows, "bypass_rate")
        self.assertEqual(len(d), sum(1 for r in rows if r["intended_modality"] == "skin_wound"))
        self.assertTrue(all(set(x) == {"y", "prototype", "period2", "mobile", "participant"} for x in d))

    @unittest.skipUnless(HAS_SM, "statsmodels not installed: GEE reference is optional (NOT_IMPLEMENTED)")
    def test_independence_gee_equals_glm_and_cluster_robust(self):
        import random
        import pandas as pd
        import statsmodels.api as sm
        rows = bank.synthetic_session(bank.build_manifest("s", 3), 20, seed="gee")
        rng = random.Random("both")
        for r in rows:                                   # errors in BOTH conditions (no separation), clustered by participant
            p_err = 0.35 if r["condition"] == "baseline" else 0.15
            wrong = rng.random() < p_err
            r["chosen_modality"] = r["initial_modality"] = ("ecg" if r["intended_modality"] != "ecg" else "xray") if wrong else r["intended_modality"]
        fit = gee_reference.fit_gee(rows, "confirmation_error_rate", "independence")
        self.assertEqual(fit["status"], "ESTIMATED")
        frame = pd.DataFrame(gee_reference.design(rows, "confirmation_error_rate"))
        exog = sm.add_constant(frame[["prototype", "period2", "mobile"]].astype(float), has_constant="add")
        glm = sm.GLM(frame["y"], exog, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(frame["participant"])[0]})
        for name in exog.columns:
            self.assertAlmostEqual(fit["coefficients"][name]["log_odds"], float(glm.params[name]), places=5)
            self.assertAlmostEqual(fit["coefficients"][name]["robust_se"], float(glm.bse[name]), delta=0.05 * max(float(glm.bse[name]), 1e-9))

    @unittest.skipUnless(HAS_SM, "statsmodels not installed")
    def test_exchangeable_runs_and_edge_cases_are_declared(self):
        rows = bank.synthetic_session(bank.build_manifest("s", 3), 20, seed="gee")
        # the bare synthetic session only errs under baseline: separation must be declared, not a diverging coefficient
        sep = gee_reference.fit_gee(rows, "confirmation_error_rate")
        self.assertEqual(sep["status"], "NOT_ESTIMABLE"); self.assertIn("separation", sep["reason"])
        import random
        rng = random.Random("ex")
        for r in rows:
            if rng.random() < 0.3:
                r["chosen_modality"] = r["initial_modality"] = "ecg" if r["intended_modality"] != "ecg" else "xray"
        self.assertEqual(gee_reference.fit_gee(rows, "confirmation_error_rate")["status"], "ESTIMATED")
        for r in rows:
            r["chosen_modality"] = r["initial_modality"] = r["intended_modality"]
        self.assertEqual(gee_reference.fit_gee(rows, "confirmation_error_rate")["status"], "NOT_ESTIMABLE")

    @unittest.skipUnless(HAS_SM, "statsmodels not installed")
    def test_collinear_design_is_declared_not_crashed(self):
        rows = bank.synthetic_session(bank.build_manifest("s", 3), 20, seed="gee")
        for r in rows:
            r["platform"] = "web" if r["period"] == 1 else "mobile"      # platform fully confounded with period
        self.assertEqual(gee_reference.fit_gee(rows, "confirmation_error_rate")["status"], "NOT_ESTIMABLE")


if __name__ == "__main__":
    unittest.main()
