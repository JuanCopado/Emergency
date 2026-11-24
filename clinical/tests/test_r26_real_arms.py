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
        self.assertLessEqual(S["arm_a_max_relative_box_delta_px"], 4)
        self.assertLessEqual(S["arm_a_max_latency_delta_ms"], 150)
        self.assertIn("arm_a_cells_with_absolute_card_shift_over_4px", S)       # absolute shifts are reported, never hidden
        for cell in S["arm_a_cells_with_absolute_card_shift_over_4px"]:
            self.assertEqual(cell[:2], ["en", 360])                            # known intermittent one-line shift above the card (cause not isolated)
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

    def test_layer7_on_the_real_app_via_the_lab_adapter(self):
        L7 = REPORT["layer7"]
        self.assertEqual(len(L7), 18)                                              # 6 scenarios x es/pt/en
        self.assertTrue(S["layer7_all_as_expected"])
        expected = {"E2_T7-03_corrupt_jpeg": "T7-03_CORRUPT_UNPROCESSABLE", "E2_T7-04_pdf_on_photo_route": "T7-04_FORMAT_CONTAINER_MISMATCH",
                    "E2_T7-04_audio_global_format": "T7-04_FORMAT_CONTAINER_MISMATCH", "F_document_kind_null": None,
                    "F_valid_rgb_ecg_route": None, "M1_valid_rgb_under_xray_route_no_visual_inference": None}
        for r in L7:
            self.assertEqual(r["adapter_trigger"], expected[r["scenario"]], r["scenario"])
            self.assertEqual(r["force_send_controls"], 0)                          # no force-send path after a technical abstention
            if expected[r["scenario"]]:
                self.assertTrue(r["overlay_shown"] and r["overlay_text_equals_adapter_text"])
                self.assertEqual((r["review_cards_created"], r["real_prepare_calls"]), (0, 0))
            else:
                self.assertFalse(r["overlay_shown"])

    def test_ready_states_are_not_confused(self):
        self.assertTrue(S["software_lab_ready"].startswith("SOFTWARE_LAB_READY_CANDIDATE_PENDING_AUDIT"))
        self.assertTrue(S["study_with_humans_ready"].startswith("STUDY_WITH_HUMANS_READY: NO"))
        self.assertIn("app has no Layer 7 UI and was not modified", S["arm_b_layer7"])


if __name__ == "__main__":
    unittest.main()
