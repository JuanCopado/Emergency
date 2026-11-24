"""R28 · counterbalancing S1-S4: the published matrix fails the 15/15 invariant; the candidate passes and is NOT Gemini-validated."""
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from human_factors import counterbalance as cb  # noqa: E402


class Counterbalance(unittest.TestCase):
    def test_published_matrix_gives_16_14_or_14_16_per_participant(self):
        report = cb.audit(cb.PUBLISHED)
        self.assertFalse(report["ok"])
        self.assertEqual(report["per_sequence"]["S1"], {"mobile": 16, "web": 14})
        self.assertEqual(report["per_sequence"]["S2"], {"mobile": 14, "web": 16})
        self.assertEqual(report["per_sequence"]["S3"], {"mobile": 16, "web": 14})
        self.assertEqual(report["per_sequence"]["S4"], {"mobile": 14, "web": 16})
        self.assertTrue(any("required 15/15" in v for v in report["violations"]))

    def test_candidate_matrix_satisfies_every_invariant(self):
        report = cb.audit(cb.CANDIDATE)
        self.assertTrue(report["ok"], report["violations"])
        for name, devices in report["per_sequence"].items():
            self.assertEqual(devices, {"mobile": 15, "web": 15}, name)
        self.assertEqual(set(report["pooled_arm_device"].values()), {30})          # arm x device balanced over S1-S4

    def test_candidate_trial_content_per_arm_and_device(self):
        for name, periods in cb.CANDIDATE.items():
            trials = cb.expand_trials(periods)
            self.assertEqual(len(trials), 30, name)
            self.assertEqual(Counter(p for p, *_ in trials), {1: 15, 2: 15}, name)
            for arm in ("A", "B"):
                for device in ("mobile", "web"):
                    mech = Counter(m for _, a, d, m in trials if a == arm and d == device)
                    self.assertEqual((mech["M1"], mech["M2"]), (2, 1), (name, arm, device))   # 2 M1 + 1 M2 per device per arm
            self.assertEqual(Counter(m for *_, m in trials), {"M1": 8, "M2": 4, "M3": 18}, name)

    def test_mutations_are_detected(self):
        bad = dict(cb.CANDIDATE)
        bad["S1"] = (("A", (("mobile", 8), ("mobile", 7))), cb.CANDIDATE["S1"][1])         # no device change
        self.assertFalse(cb.audit(bad)["ok"])
        bad = {k: v for k, v in cb.CANDIDATE.items() if k in ("S1", "S2")}                 # BA sequences missing
        self.assertFalse(cb.audit(bad)["ok"])


if __name__ == "__main__":
    unittest.main()
