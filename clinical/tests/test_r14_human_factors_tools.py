"""R14/R15 · R5-1 policy layer 8 tooling (human factors). Pseudonymous codes and placeholder values only.

The decisive tests use CLUSTERED, CROSSED synthetic data: they prove the main analysis resamples
participants (never single trials) and keeps the pairing between conditions.
"""
import ast
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import human_factors_tools as hf  # noqa: E402

TOOL = ROOT / "scripts" / "human_factors_tools.py"
B = 400  # resamples: enough for the tests, fast


def trial(participant="P01", scenario="S1", condition="baseline", intended="ecg", initial="ecg", chosen="ecg",
          confirmed=True, seconds=10.0, comprehension=True, period=1, role="physician", changes=0,
          platform="web", order=1):
    return {"participant": participant, "role": role, "scenario_id": scenario, "condition": condition, "period": period,
            "intended_modality": intended, "initial_modality": initial, "chosen_modality": chosen, "confirmed": confirmed,
            "changed_modality_count": changes, "seconds": seconds, "comprehension_correct": comprehension,
            "platform": platform, "order_in_period": order}


def width(interval):
    return interval[1] - interval[0]


def clustered_baseline():
    """8 participants x 10 trials; ALL the confirmation errors belong to P01 (errors cluster in people)."""
    rows = []
    for p in range(8):
        for s in range(10):
            wrong = p == 0
            rows.append(trial(f"P{p:02d}", f"S{s}", "baseline", "ecg", "xray" if wrong else "ecg", "xray" if wrong else "ecg"))
    return rows


class Validation(unittest.TestCase):
    def test_a_valid_crossed_set_passes(self):
        rows = [trial(), trial(condition="prototype", period=2), trial(scenario="S2", chosen=None, confirmed=False, initial=None)]
        self.assertEqual(hf.validate_records(rows), 3)

    def test_free_text_names_unknown_values_and_inconsistencies_are_rejected(self):
        for bad in (dict(trial(), comment="texto libre"), dict(trial(), name="Ana"), trial(participant="Ana Pérez"),
                    trial(participant="Dra. Ana"), trial(scenario="S 1"), trial(role="student"), trial(condition="control"),
                    trial(period=3), trial(period=True), trial(intended="ct"), trial(chosen="ct"), trial(initial="ct"),
                    trial(confirmed="yes"), trial(confirmed=True, chosen=None), trial(changes=-1), trial(changes=True),
                    trial(seconds=-1), trial(seconds=float("inf")), trial(comprehension="maybe")):
            with self.assertRaises(ValueError, msg=str(bad)):
                hf.validate_records([bad])
        for invalid in ([], "text"):
            with self.assertRaises(ValueError):
                hf.validate_records(invalid)

    def test_a_participant_cannot_repeat_a_scenario_in_the_same_condition(self):
        with self.assertRaises(ValueError):
            hf.validate_records([trial(), trial()])
        self.assertEqual(hf.validate_records([trial(), trial(condition="prototype", period=2)]), 2)


class DerivedFlags(unittest.TestCase):
    def test_bypass_confirmation_error_and_false_cancellation_are_different_events(self):
        skin_as_ecg = hf.flags(trial(intended="skin_wound", initial="skin_wound", chosen="ecg"))
        self.assertTrue(skin_as_ecg["bypass"] and skin_as_ecg["confirmation_error"] and skin_as_ecg["false_cancellation"])
        xray_as_pocus = hf.flags(trial(intended="xray", initial="pocus", chosen="pocus"))
        self.assertTrue(xray_as_pocus["confirmation_error"])
        self.assertFalse(xray_as_pocus["bypass"])  # bypass is only the skin photograph leaving the dermatological contract
        self.assertFalse(xray_as_pocus["false_cancellation"])  # the first choice was already wrong
        dropped = hf.flags(trial(intended="ecg", initial="ecg", chosen=None, confirmed=False))
        self.assertTrue(dropped["false_cancellation"])
        self.assertFalse(dropped["confirmation_error"])  # nothing was confirmed
        correct = hf.flags(trial())
        self.assertFalse(correct["bypass"] or correct["confirmation_error"] or correct["false_cancellation"])

    def test_flags_are_derived_from_the_closed_fields_and_never_taken_from_the_input(self):
        self.assertNotIn("bypass", hf.FIELDS)
        with self.assertRaises(ValueError):
            hf.validate_records([dict(trial(), bypass=False)])


class ClusterBootstrap(unittest.TestCase):
    def test_the_unit_of_resampling_is_the_participant_with_all_its_trials(self):
        tables = {p: hf.tally([t for t in clustered_baseline() if t["participant"] == p]) for p in ("P00", "P01")}
        key = ("baseline", ("all",))
        self.assertEqual(hf.total(tables, ["P00"], key)["trials"], 10)
        self.assertEqual(hf.total(tables, ["P00", "P00"], key)["trials"], 20)  # drawn twice: every trial twice
        self.assertEqual(hf.total(tables, ["P00", "P01"], key)["confirmation_error_rate:num"], 10)
        rng = hf.random.Random("t")
        drawn = hf.cluster_resample(["P00", "P01", "P02"], rng)
        self.assertEqual(len(drawn), 3)
        self.assertTrue(set(drawn) <= {"P00", "P01", "P02"})

    def test_clustered_errors_do_not_look_as_precise_as_independent_trials(self):
        rows = clustered_baseline()  # 80 trials, 10 errors, all in one of 8 participants
        out = hf.summarize(rows, resamples=B)
        cluster_ci = out["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]["cluster_bootstrap_95"]
        naive = out["descriptive_exploration_only"]["by_condition"]["baseline"]["confirmation_error_rate"]
        self.assertEqual(naive["trials"], 80)
        self.assertEqual(naive["events"], 10)
        # treating the 80 trials as independent gives a narrow interval; resampling the 8 people is much wider
        self.assertGreater(width(cluster_ci), 1.8 * width(naive["wilson_95"]))
        self.assertGreater(width(cluster_ci), 1.8 * width(naive["exact_95"]))
        self.assertLessEqual(cluster_ci[0], 0.0001)  # a resample without the one person who erred is possible
        self.assertEqual(out["design"]["independence_of_trials"], "NOT_ASSUMED")

    def test_the_pairing_between_conditions_is_preserved(self):
        rows = []
        for p in range(10):
            high = p < 5  # people differ a lot: half of them err often, half never
            for s in range(10):
                base_wrong = high and s < 8
                proto_wrong = high and s < 7
                rows.append(trial(f"P{p:02d}", f"S{s}", "baseline", "ecg", "xray" if base_wrong else "ecg", "xray" if base_wrong else "ecg", period=1))
                rows.append(trial(f"P{p:02d}", f"S{s}", "prototype", "ecg", "xray" if proto_wrong else "ecg", "xray" if proto_wrong else "ecg", period=2))
        out = hf.summarize(rows, resamples=B)["trial_level_metrics"]
        base = out["by_condition"]["baseline"]["confirmation_error_rate"]
        diff = out["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]
        self.assertAlmostEqual(diff["estimate"], -0.05, places=3)
        self.assertGreater(width(base["cluster_bootstrap_95"]), 0.4)   # people differ: each condition alone is imprecise
        self.assertLess(width(diff["cluster_bootstrap_95"]), 0.12)      # but the paired difference keeps the pairing
        self.assertLessEqual(diff["cluster_bootstrap_95"][1], 0.0)

    def test_only_participants_with_both_conditions_enter_the_paired_difference(self):
        rows = [trial("P00", "S1", "baseline"), trial("P00", "S1", "prototype", period=2),
                trial("P01", "S1", "baseline"), trial("P02", "S1", "prototype", period=2)]
        design = hf.summarize(rows, resamples=50)["design"]
        self.assertEqual(design["participants"], 3)
        self.assertEqual(design["participants_with_both_conditions"], 1)

    def test_results_are_deterministic_for_a_seed_and_a_single_participant_has_no_interval(self):
        rows = clustered_baseline()
        first_run = hf.summarize(rows, resamples=100, seed="a")
        second_run = hf.summarize(rows, resamples=100, seed="a")
        self.assertEqual(first_run, second_run)
        one = hf.summarize([trial()], resamples=100)
        self.assertEqual(one["design"]["resamples"], 0)
        self.assertIsNone(one["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]["cluster_bootstrap_95"])
        self.assertEqual(one["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]["estimate"], 0.0)


class Reporting(unittest.TestCase):
    def setUp(self):
        rows = []
        for p in range(4):
            for scenario, intended in (("S1", "skin_wound"), ("S2", "ecg")):
                rows.append(trial(f"P{p}", scenario, "baseline", intended, intended, "ecg" if intended == "skin_wound" and p == 0 else intended,
                                  seconds=10 + p, comprehension=p != 3))
                rows.append(trial(f"P{p}", scenario, "prototype", intended, intended, intended, seconds=13 + p, comprehension=True, period=2))
        self.out = hf.summarize(rows, resamples=B)

    def test_it_reports_by_condition_modality_scenario_and_participant(self):
        primary = self.out["trial_level_metrics"]
        self.assertEqual(set(primary["by_condition"]), {"baseline", "prototype"})
        self.assertEqual(set(primary["by_condition_and_modality"]["baseline"]), {"skin_wound", "ecg"})
        self.assertEqual(set(primary["by_condition_and_scenario"]["prototype"]), {"S1", "S2"})
        self.assertEqual(set(self.out["by_participant"]), {"P0", "P1", "P2", "P3"})
        self.assertEqual(self.out["by_participant"]["P0"]["baseline"]["trials"], 2)

    def test_it_separates_bypass_confirmation_error_false_cancellation_time_and_comprehension(self):
        by_mod = self.out["trial_level_metrics"]["by_condition_and_modality"]["baseline"]
        self.assertEqual(by_mod["skin_wound"]["bypass_rate"]["estimate"], 0.25)           # 1 of 4 skin photographs
        self.assertIsNone(by_mod["ecg"]["bypass_rate"]["estimate"])                        # bypass is defined for skin only
        self.assertEqual(by_mod["skin_wound"]["confirmation_error_rate"]["estimate"], 0.25)
        self.assertEqual(by_mod["skin_wound"]["false_cancellation_rate"]["estimate"], 0.25)
        self.assertEqual(self.out["trial_level_metrics"]["by_condition"]["baseline"]["comprehension_rate"]["estimate"], 0.75)
        self.assertEqual(self.out["trial_level_metrics"]["by_condition"]["prototype"]["comprehension_rate"]["estimate"], 1.0)
        extra = self.out["trial_level_metrics"]["additional_time_seconds_prototype_minus_baseline"]
        self.assertAlmostEqual(extra["estimate"], 3.0, places=3)

    def test_it_sets_no_acceptance_margin_and_never_says_the_study_ran(self):
        self.assertEqual(self.out["acceptance_margin"], "NOT_SET_MEDICAL_DECISION")
        self.assertEqual(self.out["study_status"], "NOT_EXECUTED_TOOLING_ONLY")
        note = self.out["descriptive_exploration_only"]["note"]
        self.assertIn("independent", note)
        self.assertIn("Descriptive only", note)

    def test_the_descriptive_block_is_labelled_and_the_main_block_never_uses_it(self):
        self.assertIn("descriptive_exploration_only", self.out)
        self.assertNotIn("wilson_95", json.dumps(self.out["trial_level_metrics"]))
        self.assertNotIn("exact_95", json.dumps(self.out["trial_level_metrics"]))


class DescriptiveIntervals(unittest.TestCase):
    def test_exact_interval_matches_known_values(self):
        low, high = hf.clopper_pearson(0, 10)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 1 - 0.025 ** (1 / 10), places=4)
        low, high = hf.clopper_pearson(5, 10)
        self.assertAlmostEqual(low, 0.1871, places=3)
        self.assertAlmostEqual(high, 0.8129, places=3)
        low, high = hf.clopper_pearson(500, 500)
        self.assertEqual(high, 1.0)
        self.assertAlmostEqual(low, 0.025 ** (1 / 500), places=4)

    def test_wilson_matches_known_values_and_empty_input_has_no_interval(self):
        low, high = hf.wilson(5, 10)
        self.assertAlmostEqual(low, 0.2366, places=3)
        self.assertAlmostEqual(high, 0.7634, places=3)
        self.assertIsNone(hf.wilson(0, 0))
        self.assertIsNone(hf.clopper_pearson(0, 0))
        self.assertIsNone(hf.clopper_pearson(3, 2))

    def test_the_binomial_mass_rejects_points_outside_the_open_unit_interval(self):
        for p in (0, 1, -0.1, 1.5):
            with self.assertRaises(ValueError):
                hf._pmf(0, 5, p)


def crossed_rows(n_ab=4, n_ba=4, trials=6, err_proto=0, err_base=0, platform=lambda p: "web"):
    """AB participants do baseline in period 1, BA participants prototype in period 1."""
    rows = []
    for i in range(n_ab + n_ba):
        first = "baseline" if i < n_ab else "prototype"
        second = "prototype" if first == "baseline" else "baseline"
        pid = f"P{i:02d}"
        for period, condition in ((1, first), (2, second)):
            errors = err_base if condition == "baseline" else err_proto
            for s in range(trials):
                wrong = i < errors
                rows.append(trial(pid, f"S{period}{s}", condition, "ecg", "ecg", "xray" if wrong else "ecg",
                                  period=period, platform=platform(i), order=s + 1))
    return rows


class CrossedDesign(unittest.TestCase):
    def test_a_participant_cannot_mix_conditions_inside_one_period(self):
        with self.assertRaises(ValueError):
            hf.validate_records([trial(), trial(scenario="S2", condition="prototype", period=1)])

    def test_platform_and_order_are_closed_fields(self):
        for bad in (trial(platform="desktop"), trial(platform=None), trial(order=0), trial(order=-1),
                    trial(order=True), trial(order="1"), trial(order=1.5)):
            with self.assertRaises(ValueError, msg=str(bad)):
                hf.validate_records([bad])

    def test_sequences_are_derived_from_the_period_in_which_each_condition_was_used(self):
        seq = hf.sequences(crossed_rows(2, 3))
        self.assertEqual(sorted(seq.values()), ["AB", "AB", "BA", "BA", "BA"])
        self.assertEqual(hf.sequences([trial()]), {"P01": "single"})

    def test_resampling_inside_strata_keeps_the_ab_ba_balance_of_the_sample(self):
        strata = hf.sequences(crossed_rows(3, 5))
        rng = hf.random.Random("s")
        ids = sorted(strata)
        for _ in range(50):
            drawn = hf.cluster_resample(ids, rng, strata)
            self.assertEqual(sum(strata[p] == "AB" for p in drawn), 3)
            self.assertEqual(sum(strata[p] == "BA" for p in drawn), 5)

    def test_the_default_number_of_resamples_is_at_least_5000_and_the_design_reports_the_sequences(self):
        self.assertGreaterEqual(hf.DEFAULT_RESAMPLES, 5000)
        out = hf.summarize(crossed_rows(2, 2, trials=2), resamples=30)
        self.assertEqual(out["design"]["sequences"], {"AB": 2, "BA": 2})
        self.assertTrue(out["design"]["resampling_stratified_by_sequence"])
        self.assertEqual(out["design"]["crossed"], "AB/BA")
        self.assertEqual(out["design"]["resamples_default"], hf.DEFAULT_RESAMPLES)


class TrialAndParticipantLevel(unittest.TestCase):
    def test_trial_rate_and_participant_risk_are_different_quantities(self):
        # 8 participants, 2 of them err in 3 of 6 baseline trials: per-trial rate 6/48, participant risk 2/8
        rows = []
        for i in range(8):
            first, second = ("baseline", "prototype") if i % 2 == 0 else ("prototype", "baseline")
            for period, condition in ((1, first), (2, second)):
                for s in range(6):
                    wrong = condition == "baseline" and i in (0, 1) and s < 3
                    rows.append(trial(f"P{i}", f"S{period}{s}", condition, "ecg", "ecg", "xray" if wrong else "ecg", period=period, order=s + 1))
        out = hf.summarize(rows, resamples=B)
        trial_rate = out["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]["estimate"]
        participant_risk = out["participant_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]["estimate"]
        self.assertAlmostEqual(trial_rate, 6 / 48, places=3)
        self.assertAlmostEqual(participant_risk, 2 / 8, places=3)
        self.assertIn("at least one event", out["participant_level_metrics"]["note"])
        self.assertEqual(set(out["participant_level_metrics"]["by_condition"]["baseline"]), set(hf.PARTICIPANT_METRICS))

    def test_the_paired_participant_difference_uses_only_participants_with_both_conditions(self):
        out = hf.summarize(crossed_rows(3, 3, trials=4, err_base=2, err_proto=1), resamples=B)
        diff = out["participant_level_metrics"]["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]
        self.assertAlmostEqual(diff["estimate"], (1 - 2) / 6, places=3)


class ZeroEvents(unittest.TestCase):
    def test_zero_events_are_not_reported_as_zero_risk(self):
        out = hf.summarize(crossed_rows(3, 3, trials=5), resamples=B)
        cell = out["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]
        self.assertEqual(cell["estimate"], 0.0)
        self.assertTrue(cell["degenerate_interval"])
        self.assertIsNone(cell["cluster_bootstrap_95"])
        self.assertIn("not evidence of zero risk", cell["note"])
        descriptive = out["descriptive_exploration_only"]["by_condition"]["baseline"]["confirmation_error_rate"]
        self.assertEqual(descriptive["events"], 0)
        self.assertGreater(descriptive["exact_95"][1], 0.0)   # the honest summary is the upper bound, not zero
        self.assertIn("never 'zero risk'", descriptive["zero_events_note"])
        participant = out["participant_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]
        self.assertTrue(participant["degenerate_interval"])

    def test_cells_with_events_keep_their_interval(self):
        out = hf.summarize(crossed_rows(4, 4, trials=5, err_base=3), resamples=B)
        cell = out["trial_level_metrics"]["by_condition"]["baseline"]["confirmation_error_rate"]
        self.assertFalse(cell["degenerate_interval"])
        self.assertEqual(len(cell["cluster_bootstrap_95"]), 2)
        self.assertIsNone(cell["note"])


class PeriodLearningPlatformAndLimits(unittest.TestCase):
    def test_a_period_effect_is_estimated_separately_from_the_condition_effect(self):
        rows = []
        for i in range(8):
            first, second = ("baseline", "prototype") if i < 4 else ("prototype", "baseline")
            for period, condition in ((1, first), (2, second)):
                for s in range(6):
                    wrong = period == 1 and s < 3   # errors only in period 1, whatever the condition
                    rows.append(trial(f"P{i}", f"S{period}{s}", condition, "ecg", "ecg", "xray" if wrong else "ecg", period=period, order=s + 1))
        out = hf.summarize(rows, resamples=B)
        self.assertAlmostEqual(out["period_and_learning"]["period_effect_period2_minus_period1"]["confirmation_error_rate"]["estimate"], -0.5, places=3)
        self.assertAlmostEqual(out["trial_level_metrics"]["paired_difference_prototype_minus_baseline"]["confirmation_error_rate"]["estimate"], 0.0, places=3)

    def test_learning_compares_late_with_early_trials(self):
        rows = []
        for i in range(6):
            first, second = ("baseline", "prototype") if i < 3 else ("prototype", "baseline")
            for period, condition in ((1, first), (2, second)):
                for s in range(6):
                    wrong = s < 3   # early trials err, late trials never do
                    rows.append(trial(f"P{i}", f"S{period}{s}", condition, "ecg", "ecg", "xray" if wrong else "ecg", period=period, order=s + 1))
        out = hf.summarize(rows, resamples=B)["period_and_learning"]
        self.assertAlmostEqual(out["learning_late_minus_early"]["confirmation_error_rate"]["estimate"], -1.0, places=3)
        self.assertEqual(out["early_late_split"]["median_order_in_period"], 3)

    def test_web_and_mobile_are_reported_separately(self):
        out = hf.summarize(crossed_rows(4, 4, trials=4, err_base=2, platform=lambda p: "web" if p < 4 else "mobile"), resamples=B)
        by_platform = out["trial_level_metrics"]["by_condition_and_platform"]["baseline"]
        self.assertEqual(set(by_platform), {"web", "mobile"})
        web = by_platform["web"]["confirmation_error_rate"]["estimate"]
        mobile = by_platform["mobile"]["confirmation_error_rate"]["estimate"]
        self.assertGreater(web, mobile)  # the two participants who err use the web platform

    def test_limitations_are_stated_and_no_sample_size_or_threshold_is_set(self):
        out = hf.summarize(crossed_rows(2, 2, trials=2), resamples=20)
        text = " ".join(out["limitations"])
        for expected in ("small", "degenerate", "Learning", "Web and mobile", "No sample size"):
            self.assertIn(expected, text)
        self.assertEqual(out["sample_size"], "NOT_SET_STUDY_DESIGN_DECISION")
        self.assertEqual(out["acceptance_margin"], "NOT_SET_MEDICAL_DECISION")
        self.assertEqual(out["study_status"], "NOT_EXECUTED_TOOLING_ONLY")


class CommandLine(unittest.TestCase):
    def test_cli_runs_over_standard_input_only(self):
        raw = json.dumps([trial(), trial(condition="prototype", period=2)]).encode("utf-8")
        self.assertEqual(hf.run(["validate"], raw), {"valid": True, "records": 2})
        out = hf.run(["summarize", "--resamples", "30", "--seed", "x"], raw)
        self.assertEqual(out["design"]["trials"], 2)
        self.assertEqual(out["design"]["seed"], "x")


class Isolation(unittest.TestCase):
    def test_the_tool_has_no_file_system_or_network_access(self):
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual(imported & {"os", "pathlib", "shutil", "tempfile", "glob", "io", "subprocess", "socket", "urllib"}, set())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertEqual(names & {"open", "Path", "eval", "exec", "__import__"}, set())
        self.assertEqual(attrs & {"read_text", "write_text", "read_bytes", "write_bytes", "mkdir", "unlink", "open"}, set())

    def test_nothing_in_the_product_uses_it(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            if path.name != "human_factors_tools.py":
                self.assertNotIn("human_factors_tools", path.read_text(encoding="utf-8", errors="ignore"), str(path))


if __name__ == "__main__":
    unittest.main()
