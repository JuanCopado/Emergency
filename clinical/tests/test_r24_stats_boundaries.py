"""R24 · BCa / small-cluster policy of the R23 protocol: boundary tests (P = 1, 2, 12, 15, 16, 19, 20, 30) and event patterns."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import human_factors_tools as hf  # noqa: E402
from test_r14_human_factors_tools import trial  # noqa: E402

B = 60


def make_rows(participants, with_event, trials=4, every_trial=False):
    """AB/BA crossed rows. The `with_event` event participants are SPREAD over both sequences (an event set that equals one
    sequence would be a degenerate design under sequence-stratified resampling). Event participants err in one trial
    (or in every trial when `every_trial`), under baseline only."""
    n_ab = (participants + 1) // 2
    event_ids = {int(j * participants / with_event) for j in range(with_event)} if with_event else set()
    assert len(event_ids) == with_event
    rows = []
    for i in range(participants):
        first = "baseline" if i < n_ab else "prototype"
        for period, condition in ((1, first), (2, "prototype" if first == "baseline" else "baseline")):
            for s in range(trials):
                wrong = condition == "baseline" and i in event_ids and (every_trial or s == 0)
                rows.append(trial(f"P{i:02d}", f"S{period}{s}", condition, "ecg", "ecg", "xray" if wrong else "ecg",
                                  period=period, platform="web", order=s + 1))
    return rows


def run(participants, with_event, every_trial=False):
    rows = make_rows(participants, with_event, every_trial=every_trial)
    out = hf.summarize(rows, resamples=B, seed="r24")
    cell = out["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]
    return out, cell


def expected_bca(participants, with_event):
    return participants >= 20 and 2 <= with_event <= participants - 2 and 0 < with_event < participants


class Boundaries(unittest.TestCase):
    def test_flags_follow_the_16_and_30_thresholds(self):
        for participants in (1, 2, 12, 15, 16, 19, 20, 30):
            _, cell = run(participants, min(1, participants))
            self.assertEqual(cell["very_small_cluster_descriptive_only"], participants < 16, participants)
            self.assertEqual(cell["small_cluster_warning"], participants < 30, participants)
            self.assertEqual(cell["participants_in_estimand"], participants)

    def test_bca_only_with_20_participants_and_two_with_and_two_without_events(self):
        for participants in (1, 2, 12, 15, 16, 19, 20, 30):
            for with_event in sorted({0, 1, 2, participants // 2, participants - 2, participants - 1, participants}):
                if not 0 <= with_event <= participants:
                    continue
                _, cell = run(participants, with_event)
                label = (participants, with_event)
                if expected_bca(participants, with_event):
                    self.assertEqual(cell["primary_interval"], "bca", label)
                    self.assertEqual(cell["bca_status"], "BCA_PRIMARY", label)
                    self.assertIsNotNone(cell["cluster_bootstrap_bca_95"], label)
                else:
                    self.assertEqual(cell["bca_status"], hf.BCA_FALLBACK, label)
                    self.assertIsNone(cell["cluster_bootstrap_bca_95"], label)
                    self.assertNotEqual(cell["primary_interval"], "bca", label)
                self.assertEqual(cell["participants_with_event"], with_event)
                self.assertEqual(cell["participants_without_event"], participants - with_event)

    def test_exactly_the_boundary_cases(self):
        self.assertEqual(run(20, 2)[1]["bca_status"], "BCA_PRIMARY")            # 2 with, 18 without, P = 20
        self.assertEqual(run(20, 18)[1]["bca_status"], "BCA_PRIMARY")           # 18 with, 2 without
        self.assertEqual(run(20, 1)[1]["bca_status"], hf.BCA_FALLBACK)          # only 1 with event
        self.assertEqual(run(20, 19)[1]["bca_status"], hf.BCA_FALLBACK)         # only 1 without event
        self.assertEqual(run(19, 9)[1]["bca_status"], hf.BCA_FALLBACK)          # P = 19 < 20
        self.assertEqual(run(30, 15)[1]["bca_status"], "BCA_PRIMARY")

    def test_zero_events_and_all_positive_are_degenerate_and_never_a_zero_interval(self):
        for participants in (1, 2, 12, 20, 30):
            for with_event in (0, participants):
                out, cell = run(participants, with_event, every_trial=True)
                self.assertEqual(cell["bca_status"], hf.BCA_FALLBACK)
                if participants >= 2:
                    self.assertTrue(cell["degenerate_interval"], (participants, with_event))
                    self.assertIsNone(cell["cluster_bootstrap_95"])
                    self.assertIsNone(cell["primary_interval"])
                self.assertNotEqual(cell["cluster_bootstrap_95"], [0.0, 0.0])

    def test_zero_events_report_exact_participant_bounds_and_never_a_trial_interval(self):
        for participants in (2, 12, 20):
            out, _ = run(participants, 0)
            report = out["zero_event_reports"]["baseline"]["confirmation_error_rate"]
            self.assertEqual(report["participants_with_event_over_participants"], f"0/{participants}")
            self.assertAlmostEqual(report["participant_risk_upper_95_one_sided"], round(1 - 0.05 ** (1 / participants), 4))
            self.assertAlmostEqual(report["participant_risk_upper_95_two_sided"], round(1 - 0.025 ** (1 / participants), 4))
            self.assertIn("upper bound", report["label"])
            self.assertIn("never an exact trial-rate interval", report["label"])
            self.assertIn("0/N trials", report["forbidden"])

    def test_the_participant_level_exact_bounds_are_reported_when_bca_is_withheld(self):
        out, cell = run(12, 3)
        self.assertEqual(cell["bca_status"], hf.BCA_FALLBACK)
        exact = out["participant_level_metrics"]["exact_over_participants"]["baseline"]["confirmation_error_rate"]
        self.assertEqual((exact["participants"], exact["with_event"]), (12, 3))
        self.assertEqual(len(exact["exact_95_over_participants"]), 2)

    def test_the_paired_and_participant_level_estimands_apply_the_same_policy(self):
        out, _ = run(12, 4)
        paired = out["trial_level_metrics"]["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]
        part = out["participant_level_metrics"]["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]
        for block in (paired, part):
            self.assertEqual(block["bca_status"], hf.BCA_FALLBACK)
            self.assertTrue(block["very_small_cluster_descriptive_only"])
        big, _ = run(24, 6)
        paired = big["trial_level_metrics"]["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]
        self.assertEqual(paired["bca_status"], "BCA_PRIMARY")
        self.assertFalse(paired["very_small_cluster_descriptive_only"])
        self.assertTrue(paired["small_cluster_warning"])   # 24 < 30

    def test_the_design_block_declares_the_policy(self):
        out, _ = run(12, 3)
        design = out["design"]
        self.assertTrue(design["very_small_cluster_descriptive_only"])
        self.assertEqual(design["bca_policy"], {"min_participants": 20, "min_with_event": 2, "min_without_event": 2, "otherwise": hf.BCA_FALLBACK})

    def test_the_tool_never_claims_stage_2_models(self):
        out, _ = run(12, 3)
        self.assertEqual(out["crossover_and_device_models"]["status"], "NOT_IMPLEMENTED_STDLIB_ONLY")
        self.assertEqual(out["crossover_and_device_models"]["carryover_pretest"], "PROHIBITED_NEVER_PERFORMED")
        self.assertEqual(out["acceptance_decision"], "PENDING_PHYSICIAN_OWNER_REVIEW")


if __name__ == "__main__":
    unittest.main()
