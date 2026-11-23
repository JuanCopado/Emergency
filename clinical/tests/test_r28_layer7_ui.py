"""R28 · Layer 7 UI of arm B in the real app (lab build only): observed-report consistency and source-level isolation."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "clinical" / "lab" / "human_factors" / "fidelity" / "layer7_ui_report.json"
LAB_SRC = ROOT / "app" / "src" / "lab"


class Layer7UiReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.summary = cls.report["summary"]

    def test_every_gate_of_the_run_is_true_and_limits_are_declared(self):
        for key in ("abstentions_as_expected", "banner_above_fold_everywhere", "banner_inside_viewport_width_everywhere", "no_horizontal_overflow",
                    "e1_file_input_before_modality", "other_trials_keep_approved_flow", "e1_recovery_by_choosing_modality", "valid_trials_not_blocked"):
            self.assertIs(self.summary[key], True, key)
        self.assertEqual(self.summary["trials"], 36)
        self.assertEqual(self.summary["study_with_humans"], "NOT_AUTHORISED")
        for key in ("contrast_measured", "screen_reader_tested", "edge_checked"):
            self.assertIs(self.summary[key], False, key)                    # NOT_VERIFIED is declared, not hidden

    def test_no_force_send_and_no_confirmation_while_the_abstention_is_visible(self):
        shown = [r for r in self.report["results"] if r["banner_shown"]]
        self.assertTrue(shown)
        for r in shown:
            self.assertEqual((r["force_send_controls"], r["confirm_buttons"]), (0, 0), r["scenario"])
            self.assertTrue(r["text_equals_adapter_text"] and r["focused"] and r["role_alert"], r["scenario"])

    def test_e1_is_observed_in_every_language_and_viewport(self):
        e1 = [r for r in self.report["results"] if r["scenario"].startswith("E1")]
        self.assertEqual({(r["language"], r["viewport"]) for r in e1}, {(l, v) for l in ("es", "pt", "en") for v in (360, 390)})
        self.assertTrue(all(r["adapter_trigger"] == "T7-01_UNDECLARED_MODALITY" and r["banner_shown"] for r in e1))


class SourceIsolation(unittest.TestCase):
    def test_the_lab_module_is_only_reachable_through_a_build_time_guarded_dynamic_import(self):
        note = (ROOT / "app" / "src" / "pages" / "ClinicalNote.tsx").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"from '\.\./lab/|import\('\.\./lab/", note)), 1)
        self.assertIn("!import.meta.env.PROD && import.meta.env.VITE_R51_PROTOTYPE === '1' && import.meta.env.VITE_LAB_LAYER7 === '1'", note)
        for path in (ROOT / "app" / "src").rglob("*.ts*"):
            if LAB_SRC in path.parents or path.name == "ClinicalNote.tsx" or "test" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"from '(\.\./)+lab/|import\('(\.\./)+lab/", text), f"{path} imports the lab module")

    def test_the_lab_module_has_no_force_send_and_no_visual_inference_terms(self):
        text = "\n".join(p.read_text(encoding="utf-8") for p in LAB_SRC.glob("*"))
        self.assertIsNone(re.search(r"""['">`][^'"<>`]*(forzar|forçar|force send|send anyway)[^'"<>`]*['"<`]""", text, re.I))   # no such UI string
        self.assertNotIn("getImageData", text)


if __name__ == "__main__":
    unittest.main()
