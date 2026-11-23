"""R27 · BCa admissibility conditions C1-C4 (explicit, no silent substitutions) and Gemini REF-STAT golden fixtures.
C2's numeric threshold is PROVISIONAL (not in any available source). REF-STAT-01P / 03A / 03B / 04 (R26) were not received: NOT_VERIFIED."""
import math
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import human_factors_tools as hf  # noqa: E402
from test_r14_human_factors_tools import trial  # noqa: E402
from test_r24_stats_boundaries import make_rows  # noqa: E402


def cell_of(rows, resamples=300):
    out = hf.summarize(rows, resamples=resamples, seed="r27")
    return out["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]


class Conditions(unittest.TestCase):
    def test_version_and_policy_declare_the_conditions(self):
        self.assertEqual(hf.TOOL_VERSION, "hf-tools-0.5")
        out = hf.summarize(make_rows(20, 10), resamples=200, seed="r27")
        policy = out["design"]["bca_policy"]
        self.assertIn("C4", policy["conditions"])
        self.assertIn("PROVISIONAL", policy["conditions"])

    def test_all_four_conditions_met_gives_bca_with_parameters(self):
        cell = cell_of(make_rows(30, 12))
        self.assertEqual(cell["bca_status"], "BCA_PRIMARY")
        c = cell["bca_conditions"]
        self.assertEqual((c["C1_min_participants"], c["C2_sequences_represented"], c["C3_variation_and_events"], c["C4_parameters_valid"]),
                         (True, True, True, True))
        self.assertEqual(c["failed"], [])
        params = cell["bca_parameters"]
        self.assertTrue(math.isfinite(params["z0"]) and math.isfinite(params["acceleration"]))
        self.assertLess(params["adjusted_alphas"][0], params["adjusted_alphas"][1])
        self.assertTrue(all(0 < a < 1 for a in params["adjusted_alphas"]))

    def test_c1_fewer_than_20_participants(self):
        cell = cell_of(make_rows(19, 8))
        self.assertEqual(cell["bca_conditions"]["failed"], ["C1_min_participants"])
        self.assertEqual(cell["bca_status"], hf.BCA_FALLBACK)

    def test_c3_without_events_or_with_a_single_event(self):
        for events in (0, 1):
            cell = cell_of(make_rows(20, events))
            self.assertIn("C3_variation_and_events", cell["bca_conditions"]["failed"], events)
            self.assertEqual(cell["primary_interval"] in (None, "percentile"), True)
            self.assertIsNone(cell["cluster_bootstrap_bca_95"])

    def test_c4_refusals_are_explicit_and_never_replaced_silently(self):
        samples = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        cases = {
            "bias_correction_degenerate": (0.05, samples, [0.1, 0.2, 0.3]),                 # no sample below the point estimate
            "acceleration_undefined_null_jackknife_variance": (0.35, samples, [0.3, 0.3, 0.3]),
            "insufficient_bootstrap_or_jackknife_values": (0.35, [0.3], [0.3, 0.4]),
        }
        for reason, (point, boot, jack) in cases.items():
            with self.subTest(reason=reason):
                bounds, diag = hf._bca_diagnosed(point, boot, jack)
                self.assertIsNone(bounds)
                self.assertEqual(diag["failure"], reason)
                self.assertIsNone(hf._bca(point, boot, jack))              # historical interface keeps returning None
        bounds, diag = hf._bca_diagnosed(0.35, samples, [0.2, 0.3, 0.5, 0.4, 0.6])
        self.assertIsNotNone(bounds)
        self.assertIsNone(diag["failure"])

    def test_c4_large_acceleration_that_makes_the_denominator_non_positive_is_refused(self):
        samples = [i / 100 for i in range(1, 100)]
        jackknife = [0.0] * 40 + [1.0] * 2                                # strongly skewed leave-one-out values
        bounds, diag = hf._bca_diagnosed(0.5, samples, jackknife)
        if bounds is None:
            self.assertIn(diag["failure"], {"adjusted_quantile_denominator_not_positive", "adjusted_quantile_invalid",
                                            "adjusted_quantiles_not_ordered"})
        else:                                                              # then the parameters really are valid
            self.assertTrue(0 < diag["adjusted_alphas"][0] < diag["adjusted_alphas"][1] < 1)

    def test_c2_a_sequence_with_a_single_participant_withholds_bca(self):
        ids = [f"P{i:02d}" for i in range(20)]
        strata = {p: ("AB" if i < 19 else "BA") for i, p in enumerate(ids)}      # 19 + 1: BA is not represented
        flags = {p: (i % 2 == 0) for i, p in enumerate(ids)}
        res = hf._bootstrap(ids, 200, random.Random(1), lambda d: sum(flags[x] for x in d) / len(d), strata, flags)
        self.assertFalse(res["bca_conditions"]["C2_sequences_represented"])
        self.assertEqual(res["bca_status"], hf.BCA_FALLBACK)
        self.assertIsNone(res["cluster_bootstrap_bca_95"])
        balanced = {p: ("AB" if i < 10 else "BA") for i, p in enumerate(ids)}
        ok = hf._bootstrap(ids, 200, random.Random(1), lambda d: sum(flags[x] for x in d) / len(d), balanced, flags)
        self.assertTrue(ok["bca_conditions"]["C2_sequences_represented"])
        self.assertEqual(hf.BCA_C2_THRESHOLD_STATUS, "PROVISIONAL_NOT_SPECIFIED_IN_AVAILABLE_SOURCES")


def ref01_rows():
    a_mob, a_web, b_mob = [2, 2, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0]
    rows = []
    for i in range(12):
        k, first = i % 6, ("baseline" if i < 6 else "prototype")
        for period, cond in ((1, first), (2, "prototype" if first == "baseline" else "baseline")):
            counts = {"mobile": a_mob[k] if cond == "baseline" else b_mob[k], "web": a_web[k] if cond == "baseline" else 0}
            order = 0
            for platform in ("mobile", "web"):
                for s in range(2):
                    order += 1
                    rows.append(trial(f"P{i:02d}", f"S{period}{platform[0]}{s}", cond, "ecg", "ecg", "xray" if s < counts[platform] else "ecg",
                                      period=period, platform=platform, order=order))
    return rows


class GoldenFixtures(unittest.TestCase):
    """Numbers published in R25_GEMINI_INFORME_INTEGRADO_FINAL part III (synthetic fixtures; not clinical data)."""

    @classmethod
    def setUpClass(cls):
        cls.out = hf.summarize(ref01_rows(), resamples=5000, seed="ref01")
        cls.tl, cls.pl = cls.out["trial_level_metrics"], cls.out["participant_level_metrics"]

    def test_ref_stat_01_trial_level(self):
        by = self.tl["by_condition"]
        self.assertAlmostEqual(by["baseline"]["confirmation_error_rate"]["estimate"], 12 / 48, places=4)
        self.assertAlmostEqual(by["prototype"]["confirmation_error_rate"]["estimate"], 2 / 48, places=4)
        paired = self.tl["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]
        self.assertAlmostEqual(paired["estimate"], -10 / 48, places=4)
        low, high = paired["cluster_bootstrap_95"]
        self.assertLessEqual(abs(low - (-0.3333)), 1 / 48)
        self.assertLessEqual(abs(high - (-0.0833)), 1 / 48)
        self.assertEqual(paired["bca_status"], "FALLBACK_SMALL_SAMPLE_OR_DEGENERATE")
        self.assertTrue(paired["small_cluster_warning"] and paired["very_small_cluster_descriptive_only"])

    def test_ref_stat_01_participant_level_and_mcnemar(self):
        base = self.pl["by_condition"]["baseline"]["confirmation_error_rate"]
        proto = self.pl["by_condition"]["prototype"]["confirmation_error_rate"]
        self.assertAlmostEqual(base["estimate"], 0.5, places=4)
        self.assertAlmostEqual(proto["estimate"], 2 / 12, places=4)
        exact = self.pl["exact_over_participants"]
        self.assertEqual((exact["baseline"]["confirmation_error_rate"]["with_event"], exact["prototype"]["confirmation_error_rate"]["with_event"]), (6, 2))
        low, high = hf.clopper_pearson(6, 12)
        self.assertLess(abs(low - 0.2109), 1e-4); self.assertLess(abs(high - 0.7891), 1e-4)
        low, high = hf.clopper_pearson(2, 12)
        self.assertLess(abs(low - 0.0209), 1e-4); self.assertLess(abs(high - 0.4841), 1e-4)
        mc = self.pl["mcnemar_exact"]["confirmation_error_rate"]
        self.assertEqual((mc["baseline_only_event"], mc["prototype_only_event"]), (4, 0))
        self.assertAlmostEqual(mc["p_value_exact_two_sided"], 0.125, places=4)

    def test_ref_stat_02_zero_events_dual_count_and_bounds(self):
        report = hf.zero_event_report(0, 64, 0, 16)
        self.assertEqual((report["events_over_trials"], report["participants_with_event_over_participants"]), ("0/64", "0/16"))
        self.assertEqual(report["participant_risk_upper_95_one_sided"], 0.1707)
        self.assertEqual(report["participant_risk_upper_95_two_sided"], 0.2059)
        text = str(report)
        for forbidden in ("0.0457", "0.0560"):
            self.assertNotIn(forbidden, text)                                 # Clopper-Pearson over 0/64 trials is PROHIBITED
        self.assertIn("never an exact trial-rate interval", report["label"])

    def test_ref_stat_03a_m2_participant_level_only(self):
        low, high = hf.clopper_pearson(10, 12)
        self.assertLess(abs(low - 0.5159), 1e-4); self.assertLess(abs(high - 0.9791), 1e-4)

    def test_ref_stat_03_m3_wilcoxon_reference_is_arithmetically_consistent_but_not_implemented_in_the_tool(self):
        deltas = [2, 3, 4, 5, 5, 6, 6, 7, 8, 9, 10, 13]
        self.assertAlmostEqual(sum(deltas) / 12, 6.5)
        self.assertEqual(sorted(deltas)[5:7], [6, 6])                          # median 6.0
        n = len(deltas)
        w_plus = sum(rank for rank in range(1, n + 1))                         # all deltas positive: W+ = n(n+1)/2 = 78
        self.assertEqual(w_plus, 78)
        self.assertEqual(2 ** n, 4096)                                          # exact two-sided p = 2 / 2^n
        self.assertAlmostEqual(2 / 4096, 0.000488, places=6)
        self.assertFalse(hasattr(hf, "wilcoxon_signed_rank"))                   # NOT_IMPLEMENTED: reported, not faked


if __name__ == "__main__":
    unittest.main()
