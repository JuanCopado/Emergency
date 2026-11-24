"""R31 · outcome adjudication (M1/M2/M3), technical errors and terminal recovery action in canonical-r27-v1.1.
Events below are synthetic lab-harness logs (data_provenance SYNTHETIC_LAB_HARNESS); none is presented as human data."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
from human_factors import canonical_r27_v1 as c  # noqa: E402
from human_factors import counterbalance as cb  # noqa: E402
from human_factors.canonical_r27_v1 import CanonicalViolation  # noqa: E402


def ev(kind, at, **detail):
    return {"type": kind, "at_ms": at, "detail": detail}


def trial(seq, period, pair):
    spec = cb.NORMATIVE_R29[seq]
    sub = next(s for s in (1, 2) if pair in cb._sub_pairs(s, spec[2][0]))
    web = spec[period - 1][2][sub - 1] == "web"
    prefix = "S1" if spec[period - 1][1] == "SET_1" else "S2"
    return {"sequence_code": seq, "period": period, "subblock": sub, "stimulus_id": f"{prefix}-{pair:02d}"}, (1280 if web else 360)


def ctx(seq, period, pair, **over):
    t, width = trial(seq, period, pair)
    base = {"participant_opaque_id": "HF1-P001", "role_group": "M", "language_stratum": "ES", "stimulus_hash_sha256": "b" * 64,
            "task_duration_ms": 8000, "force_attempts": 0, "data_provenance": "SYNTHETIC_LAB_HARNESS", **t}
    base.update(over)
    return base, width


def selected(width, at=10):
    return ev("file_selected", at, size=100, with_modality=True, viewport_width_px=width, e1_entry=False)


def run(seq, period, pair, log_builder, **over):
    context, width = ctx(seq, period, pair, **over)
    return c.from_lab_ui_log(log_builder(width), context)


class M1(unittest.TestCase):
    wrong = staticmethod(lambda w: [selected(w), ev("modality_selected", 20, modality="skin_wound", origin="initial"), ev("confirm_clicked", 900)])

    def test_wrong_modality_submitted_is_the_bypass(self):
        r = run("S1a", 1, 4, self.wrong, expected_modality="ecg")
        self.assertEqual((r["arm"], r["mechanism_id"], r["outcome_status"], r["data_provenance"]), ("A_real_react_control", "M1_bypass_selection", "bypass_residual", "SYNTHETIC_LAB_HARNESS"))

    def test_correct_modality_submitted_is_not_a_bypass(self):
        r = run("S1a", 1, 4, self.wrong, expected_modality="skin_wound")
        self.assertEqual(r["outcome_status"], "valid_completed")

    def test_correction_before_submit_is_detected_before_submit(self):
        build = lambda w: [selected(w), ev("modality_selected", 20, modality="skin_wound", origin="initial"),
                           ev("modality_selected", 400, modality="ecg", origin="initial"), ev("confirm_clicked", 900)]
        self.assertEqual(run("S1a", 1, 4, build, expected_modality="ecg")["outcome_status"], "detected_before_submit")

    def test_m1_never_adjudicated_without_ground_truth_or_selection_or_upload(self):
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 4, self.wrong)                                                      # no expected_modality
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 4, self.wrong, expected_modality="radiograph")                      # not in the vocabulary
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 4, lambda w: [selected(w), ev("confirm_clicked", 900)], expected_modality="ecg")   # no observed selection
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 4, lambda w: [selected(w), ev("modality_selected", 20, modality="ecg", origin="initial")], expected_modality="ecg", trial_end="cancelled_by_user")


class M2(unittest.TestCase):
    def test_m2_arm_a_never_gets_a_simulated_abstention(self):
        build = lambda w: [selected(w), ev("modality_selected", 20, modality="ecg", origin="initial"), ev("confirm_clicked", 700)]
        r = run("S1a", 1, 14, build)                                                          # S1a period 1 is arm A
        self.assertEqual((r["arm"], r["scenario_id"], r["outcome_status"], r["layer7_trigger_code"], r["recovery_outcome"]),
                         ("A_real_react_control", "E1", "valid_completed", "NONE", "NA"))
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 14, lambda w: [selected(w)], trial_end="abandoned")                 # arm A, no upload: needs adjudication

    def test_m2_arm_b_needs_an_observed_banner_for_an_abstention(self):
        build = lambda w: [selected(w), ev("modality_selected", 20, modality="ecg", origin="initial"), ev("confirm_clicked", 700)]
        with self.assertRaises(CanonicalViolation):
            run("S1a", 2, 15, build)                                                          # arm B, layer 7 never fired

    def test_voluntary_abandonment_after_the_banner_keeps_the_abstention(self):
        build = lambda w: [selected(w), ev("layer7_banner_rendered", 80, trigger="T7-03_CORRUPT_UNPROCESSABLE", message_id="MSG_T7_C")]
        r = run("S1a", 2, 15, build, trial_end="abandoned")
        self.assertEqual((r["outcome_status"], r["recovery_outcome"]), ("technical_abstention_correct", "abandoned"))


class M3(unittest.TestCase):
    cancelled = staticmethod(lambda w: [selected(w), ev("modality_selected", 20, modality="ecg", origin="initial")])

    def test_completed_is_valid(self):
        r = run("S1a", 1, 8, lambda w: self.cancelled(w) + [ev("confirm_clicked", 800)])
        self.assertEqual(r["outcome_status"], "valid_completed")

    def test_cancellation_is_human_only_with_explicit_evidence(self):
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 8, self.cancelled, trial_end="cancelled_by_user")                    # no cancel_origin
        r = run("S1a", 1, 8, self.cancelled, trial_end="cancelled_by_user", cancel_origin="human_action")
        self.assertEqual(r["outcome_status"], "false_cancellation_human")

    def test_a_technical_fault_is_never_a_human_error(self):
        r = run("S1a", 1, 8, self.cancelled, trial_end="cancelled_by_user", technical_fault="network_lost")
        self.assertEqual((r["outcome_status"], r["recovery_outcome"]), ("system_technical_error", "NA"))
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 8, self.cancelled, trial_end="abandoned")                            # abandonment without fault or deviation


class TechnicalErrorDuringLayer7(unittest.TestCase):
    def test_fault_with_banner_is_a_system_error_not_an_abstention_plus_abandonment(self):
        build = lambda w: [selected(w), ev("layer7_banner_rendered", 80, trigger="T7-03_CORRUPT_UNPROCESSABLE", message_id="MSG_T7_C")]
        r = run("S1a", 2, 15, build, trial_end="abandoned", technical_fault="browser_crash")
        self.assertEqual((r["outcome_status"], r["recovery_outcome"], r["layer7_trigger_code"], r["layer7_banner_to_first_action_ms"]),
                         ("system_technical_error", "NA", "T7-03", None))
        c.validate_record_v11(r)

    def test_na_recovery_is_only_accepted_for_a_technical_error(self):
        build = lambda w: [selected(w), ev("layer7_banner_rendered", 80, trigger="T7-03_CORRUPT_UNPROCESSABLE", message_id="MSG_T7_C")]
        r = run("S1a", 2, 15, build, trial_end="abandoned", technical_fault="browser_crash")
        r["outcome_status"] = "technical_abstention_correct"
        with self.assertRaises(CanonicalViolation):
            c.validate_record_v11(r)
        projection = {k: v for k, v in r.items() if k not in c.V11_ADDED}
        projection["schema_version"] = c.SCHEMA_VERSION
        with self.assertRaises(CanonicalViolation):
            c.validate_record(projection)                                                      # the historical v1 validator is unchanged


class RecoveryActions(unittest.TestCase):
    def test_terminal_action_trace_and_count(self):
        build = lambda w: [ev("file_selected", 50, size=1, with_modality=False, viewport_width_px=w, e1_entry=True),
                           ev("layer7_banner_rendered", 100, trigger="T7-01_UNDECLARED_MODALITY", message_id="MSG_T7_A"),
                           ev("recovery_action", 200, action="focus_selector"), ev("modality_selected", 300, modality="xray", origin="after_layer7"),
                           ev("recovery_action", 301, action="change_modality"), ev("recovery_action", 500, action="replace_file"), ev("confirm_clicked", 900)]
        r = run("S1a", 2, 14, build, force_attempts=2)
        self.assertEqual((r["recovery_action_type"], r["recovery_action_trace"], r["recovery_action_count"]),
                         ("replace_file", ["focus_selector", "change_modality", "replace_file"], 3))
        self.assertEqual((r["force_submit_attempts_count"], r["attempted_force_blocked"]), (2, True))

    def test_no_actions_means_empty_trace_not_invented_values(self):
        r = run("S1a", 1, 8, lambda w: [selected(w), ev("confirm_clicked", 500)] , )
        self.assertEqual((r["recovery_action_type"], r["recovery_action_trace"], r["recovery_action_count"], r["force_submit_attempts_count"]), (None, [], 0, 0))

    def test_inconsistent_trace_count_or_force_fields_are_refused(self):
        r = run("S1a", 1, 8, lambda w: [selected(w), ev("confirm_clicked", 500)])
        for change in ({"recovery_action_count": 1}, {"recovery_action_trace": ["x"], "recovery_action_count": 1}, {"force_submit_attempts_count": 1},
                       {"attempted_force_blocked": True}, {"data_provenance": "REAL"}, {"recovery_action_trace": ["a b"], "recovery_action_count": 1}):
            with self.subTest(change=change):
                bad = {**r, **change}
                with self.assertRaises(CanonicalViolation):
                    c.validate_record_v11(bad)


class PortugueseAndProvenance(unittest.TestCase):
    def test_generic_pt_is_refused_and_regional_variants_accepted(self):
        build = lambda w: [selected(w), ev("confirm_clicked", 500)]
        for lang in ("pt-PT", "pt-BR"):
            self.assertEqual(run("S1a", 1, 8, build, language_stratum=lang)["language_stratum"], lang)
        with self.assertRaises(CanonicalViolation):
            run("S1a", 1, 8, build, language_stratum="pt")

    def test_provenance_is_mandatory_and_closed(self):
        context, width = ctx("S1a", 1, 8)
        del context["data_provenance"]
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log([selected(width), ev("confirm_clicked", 5)], context)


class RunnerRegression(unittest.TestCase):
    """R32: the real-app Chromium runner exported 0 canonical records after R31 because its context lacked data_provenance."""
    def test_runner_context_declares_synthetic_provenance_and_report_exports_records(self):
        import json
        fidelity = ROOT / "lab" / "human_factors" / "fidelity"
        self.assertIn('data_provenance: "SYNTHETIC_LAB_HARNESS"', (fidelity / "layer7_ui.cjs").read_text(encoding="utf8"))
        report = json.loads((fidelity / "layer7_ui_report.json").read_text(encoding="utf8"))
        exports = [r["canonical_export"] for r in report["results"]]
        count = lambda status: sum(1 for e in exports if e["status"] == status)
        self.assertEqual((count("EXPORTED"), count("NOT_APPLICABLE"), count("NOT_EXPORTED")), (16, 12, 8))
        self.assertTrue(all("generic 'pt'" in e["reason"] for e in exports if e["status"] == "NOT_EXPORTED"))


if __name__ == "__main__":
    unittest.main()
