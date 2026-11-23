"""R26 · real arms A/B: arm A is the real app (flag OFF) on the same infrastructure as arm B; Layer 7 UI stays BLOCKED. Laboratory only."""
import json
import unittest
from pathlib import Path

REPORT = json.loads((Path(__file__).parents[1] / "lab" / "human_factors" / "fidelity" / "real_arms_report.json").read_text(encoding="utf-8"))
S, RUNS = REPORT["summary"], REPORT["runs"]


class RealArms(unittest.TestCase):
    def test_matrix_is_complete(self):
        keys = {(r["lang"], r["viewport"]["width"], r["scenario"]) for r in RUNS}
        self.assertEqual(keys, {(l, w, s) for l in ("es", "pt", "en") for w in (360, 1280) for s in ("document", "image")})
        self.assertFalse(S["edge_checked"])

    def test_arm_a_is_the_real_app_not_a_mockup(self):
        self.assertTrue(S["arm_a_equals_production_everywhere"])
        self.assertLessEqual(S["arm_a_max_box_delta_px"], 4)
        self.assertLessEqual(S["arm_a_max_latency_delta_ms"], 150)
        for r in RUNS:
            c = r["A_vs_prod"]
            self.assertTrue(c["same_control_names_and_order"] and c["same_card_text"] and c["same_actions"], r["lang"])
            self.assertEqual(c["overflow_px"][0], c["overflow_px"][1])      # the inherited overflow is NOT hidden

    def test_arm_a_has_no_experimental_cues_and_no_layer7(self):
        for r in RUNS:
            text = " ".join(c["name"] for c in r["A_dev"]["controls_before"]).lower() + " " + (r["A_dev"]["card_text"] or "").lower()
            for cue in ("simulated", "harness", "arm a", "capa 7", "layer 7", "t7-0", "lab_only"):
                self.assertNotIn(cue, text)

    def test_arm_b_differs_only_by_the_selector_treatment(self):
        self.assertEqual(S["arm_b_extra_actions_vs_a"], [2])
        for r in RUNS:
            self.assertTrue(r["B_dev"]["review_card"] and r["A_dev"]["review_card"])
            self.assertEqual(r["A_dev"]["prepare_calls"], 1)
            self.assertEqual(r["B_dev"]["prepare_calls"], 1)

    def test_layer7_ui_is_blocked_not_simulated(self):
        self.assertTrue(S["arm_b_layer7_abstention_ui"].startswith("BLOCKED"))


if __name__ == "__main__":
    unittest.main()
