"""R30 · normative driver S1a-S4b (R29 part IV): positive audit and deterministic rejections. The R27 matrices are not valid any more."""
import copy
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from human_factors import counterbalance as cb  # noqa: E402

MANIFEST = json.loads((ROOT / "lab" / "human_factors" / "bank" / "stimuli_manifest.json").read_text(encoding="utf-8"))


class Normative(unittest.TestCase):
    def test_the_matrix_passes_every_decidable_criterion_including_the_manifest(self):
        report = cb.audit_normative(manifest=MANIFEST)
        self.assertTrue(report["ok"], report["violations"])
        self.assertEqual(report["codes"], 8)

    def test_each_code_has_30_trials_15_mobile_15_web_and_15_per_period(self):
        for code in cb.NORMATIVE_R29:
            trials = cb.expand_normative(code)
            self.assertEqual(len(trials), 30, code)
            self.assertEqual(Counter(t["device"] for t in trials), {"mobile": 15, "web": 15}, code)
            self.assertEqual(Counter(t["period"] for t in trials), {1: 15, 2: 15}, code)
            for period in (1, 2):
                rows = [t for t in trials if t["period"] == period]
                self.assertEqual(Counter(t["mechanism"] for t in rows), {"M1": 4, "M2": 2, "M3": 9}, (code, period))
                self.assertEqual(Counter(t["subblock"] for t in rows), {1: 8, 2: 7}, (code, period))
                self.assertEqual(sorted(t["pair"] for t in rows), list(range(1, 16)), (code, period))
                self.assertEqual(len({t["device"] for t in rows}), 2)                                  # one device change per period
                self.assertFalse(all(t["mechanism"] == "M1" for t in rows[:2]), (code, period))
            self.assertEqual({t["set_id"] for t in trials if t["period"] == 1} & {t["set_id"] for t in trials if t["period"] == 2}, set())

    def test_c_and_d_alternate_between_cycles_and_sit_in_different_subblocks(self):
        for cycle, first in (("a", 6), ("b", 7)):
            for n in (1, 2, 3, 4):
                trials = cb.expand_normative(f"S{n}{cycle}")
                sub1 = {t["pair"] for t in trials if t["period"] == 1 and t["subblock"] == 1}
                sub2 = {t["pair"] for t in trials if t["period"] == 1 and t["subblock"] == 2}
                self.assertIn(first, sub1)
                self.assertIn({6: 7, 7: 6}[first], sub2)

    def test_expansion_is_deterministic_for_a_registered_seed(self):
        first = cb.expand_normative("S2b", seed="X")
        second = cb.expand_normative("S2b", seed="X")                              # a fresh call, not the same object
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertNotEqual([t["pair"] for t in cb.expand_normative("S2b", seed="X")], [t["pair"] for t in cb.expand_normative("S2b", seed="Y")])

    def test_washout_is_fixed_at_ten_minutes(self):
        self.assertEqual(cb.WASHOUT_MINUTES, 10)


class Rejections(unittest.TestCase):
    def mutated(self, code, spec):
        matrix = copy.deepcopy(cb.NORMATIVE_R29)
        matrix[code] = spec
        return cb.audit_normative(matrix)

    def test_a_missing_or_extra_code_is_rejected(self):
        matrix = {k: v for k, v in cb.NORMATIVE_R29.items() if k != "S4b"}
        self.assertFalse(cb.audit_normative(matrix)["ok"])
        self.assertFalse(cb.audit_normative({**cb.NORMATIVE_R29, "S5a": cb.NORMATIVE_R29["S1a"]})["ok"])

    def test_the_r27_device_pattern_16_14_is_rejected(self):
        p1, p2, cd = cb.NORMATIVE_R29["S1a"]
        bad = (p1, (p2[0], p2[1], p1[2]), cd)                                   # period 2 repeats period 1 device order: 16/14
        report = self.mutated("S1a", bad)
        self.assertFalse(report["ok"])
        self.assertTrue(any("15 mobile + 15 web" in v or "cell" in v for v in report["violations"]), report["violations"])

    def test_same_arm_or_same_set_in_both_periods_is_rejected(self):
        p1, p2, cd = cb.NORMATIVE_R29["S1a"]
        self.assertFalse(self.mutated("S1a", (p1, ("A", p2[1], p2[2]), cd))["ok"])
        self.assertFalse(self.mutated("S1a", (p1, (p2[0], p1[1], p2[2]), cd))["ok"])

    def test_wrong_c_d_assignment_or_cycle_is_rejected(self):
        p1, p2, _ = cb.NORMATIVE_R29["S1a"]
        self.assertFalse(self.mutated("S1a", (p1, p2, ("X", "Y")))["ok"])
        self.assertFalse(self.mutated("S1a", (p1, p2, ("D", "C")))["ok"])        # cycle a must keep C first

    def test_the_old_r27_and_candidate_matrices_are_not_the_normative_one(self):
        self.assertFalse(cb.audit(cb.PUBLISHED)["ok"])                          # 16/14 per participant
        self.assertEqual(set(cb.CANDIDATE), {"S1", "S2", "S3", "S4"})            # no a/b cycles, no sets, no C/D: not normative
        self.assertFalse(cb.audit_normative(cb.CANDIDATE)["ok"])

    def test_a_manifest_that_disagrees_with_a_pair_is_rejected(self):
        broken = copy.deepcopy(MANIFEST)
        for entry in broken["stimuli"]:
            if entry["stimulus_id"] == "S1-14":
                entry["scenario_code"] = "A"
        self.assertFalse(cb.audit_normative(manifest=broken)["ok"])


if __name__ == "__main__":
    unittest.main()
