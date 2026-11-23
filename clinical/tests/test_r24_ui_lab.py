"""R24 · interactive lab UI for E1/E2 (arm B Layer 7 harness + arm A mock): fixtures fidelity, static safety scan, node unit tests, real-browser check."""
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "lab" / "human_factors" / "ui"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors" / "ui"))
sys.path.insert(0, str(ROOT / "tests"))
import make_fixtures  # noqa: E402
from test_r14_layer7_contract import APPROVED_MESSAGES  # noqa: E402

NODE = shutil.which("node")


def node_has_playwright():
    if not NODE:
        return False
    return subprocess.run([NODE, "-e", "require('playwright')"], capture_output=True, cwd=UI).returncode == 0


class Fixtures(unittest.TestCase):
    def test_the_committed_fixtures_are_exactly_what_the_audited_harness_produces(self):
        self.assertEqual(json.loads((UI / "fixtures.json").read_text(encoding="utf-8")), make_fixtures.build())

    def test_the_embedded_script_matches_the_json(self):
        embedded = (UI / "fixtures.js").read_text(encoding="utf-8")
        self.assertTrue(embedded.startswith("window.__HF_FIXTURES__ = "))
        self.assertEqual(json.loads(embedded[len("window.__HF_FIXTURES__ = "):].rstrip().rstrip(";")), json.loads((UI / "fixtures.json").read_text(encoding="utf-8")))

    def test_every_text_is_the_approved_literal_and_every_abstention_blocks_the_send(self):
        data = json.loads((UI / "fixtures.json").read_text(encoding="utf-8"))
        self.assertEqual(data["layer7_result_label"], "SIMULATED_LAYER7_HARNESS_LAB_ONLY")
        seen = set()
        for trial in data["trials"]:
            for table in (trial["by_modality"], trial["replacement_by_modality"]):
                for decision in table.values():
                    if decision["trigger_id"]:
                        self.assertFalse(decision["send_allowed"])
                        self.assertEqual(decision["texts"], APPROVED_MESSAGES[decision["message_id"]])
                        seen.add(decision["message_id"])
                    else:
                        self.assertTrue(decision["send_allowed"]); self.assertIsNone(decision["texts"])
        self.assertEqual(seen, {"MSG_T7_A", "MSG_T7_B", "MSG_T7_C", "MSG_T7_D"})      # all four messages are reachable and exact

    def test_the_scenarios_follow_the_r23_triggers(self):
        data = {t["stimulus_id"]: t for t in json.loads((UI / "fixtures.json").read_text(encoding="utf-8"))["trials"]}
        self.assertEqual(data["S1-14"]["by_modality"]["none"]["trigger_id"], "T7-01_UNDECLARED_MODALITY")
        self.assertEqual(data["S1-15"]["by_modality"]["skin_wound"]["trigger_id"], "T7-03_CORRUPT_UNPROCESSABLE")
        self.assertEqual(data["S2-15"]["by_modality"]["skin_wound"]["trigger_id"], "T7-04_FORMAT_CONTAINER_MISMATCH")
        self.assertEqual(data["QA-01"]["by_modality"]["skin_wound"]["message_id"], "MSG_T7_D")
        self.assertEqual(data["S1-14"]["replacement_by_modality"]["none"]["trigger_id"], "T7-01_UNDECLARED_MODALITY")   # replacing the file does not declare a modality


class StaticSafety(unittest.TestCase):
    FILES = ("index.html", "app.js", "ui-logic.js")

    def text(self, name):
        return (UI / name).read_text(encoding="utf-8")

    def test_there_is_no_force_send_control_or_api(self):
        for name in ("index.html", "app.js"):
            self.assertIsNone(re.search(r"forzar|force|enviar de todos modos|send anyway|ignorar|ignore|omitir|\bskip\b|override", self.text(name), re.I), name)
        logic = self.text("ui-logic.js")
        self.assertNotRegex(logic, r"forceSend|sendAnyway|override|bypass")
        self.assertIn("forced_send_available: false", logic)

    def test_the_ui_has_no_network_storage_or_clinical_api_access(self):
        for name in self.FILES:
            self.assertIsNone(re.search(r"XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage|indexedDB|/api/|https?://", self.text(name)), name)
        self.assertNotIn("fetch(", self.text("app.js"))

    def test_the_ui_never_uses_calendar_time(self):
        for name in ("app.js", "ui-logic.js"):
            self.assertIsNone(re.search(r"\bDate\b|toISOString|getTime\(", self.text(name)), name)

    def test_the_page_identifies_the_experimental_mechanism_and_the_simulation(self):
        html = self.text("index.html")
        for needle in ('data-mechanism="M2"', "SIMULATED_LAB_HARNESS_ONLY", "no es el producto", "sin datos de pacientes"):
            self.assertIn(needle, html)
        self.assertIn('role="alert"', html)

    def test_the_product_does_not_reference_the_ui(self):
        repo = ROOT.parent
        for base in ("app/src", "app/vite.config.ts", "app/package.json", "app/index.html", "app/public"):
            path = repo / base
            files = [path] if path.is_file() else list(path.rglob("*")) if path.exists() else []
            for f in files:
                if f.is_file() and f.suffix in {".ts", ".tsx", ".js", ".mjs", ".json", ".html"} and "generatedClinicalGuides" not in f.name:
                    self.assertNotRegex(f.read_text(encoding="utf-8", errors="ignore"), r"fixtures\.js|ui-logic|__HF_|clinical/lab")


@unittest.skipUnless(NODE, "node is not installed")
class NodeUnit(unittest.TestCase):
    def test_the_state_machine_unit_tests_pass(self):
        run = subprocess.run([NODE, "--test", "ui-logic.test.js"], capture_output=True, text=True, cwd=UI)
        self.assertEqual(run.returncode, 0, run.stdout[-1500:] + run.stderr[-500:])


@unittest.skipUnless(node_has_playwright(), "node + playwright (Chromium) not available: the real-browser check is skipped")
class RealBrowser(unittest.TestCase):
    def test_the_page_behaves_in_chromium_at_360_390_and_desktop(self):
        run = subprocess.run([NODE, "e2e.cjs"], capture_output=True, text=True, cwd=UI, timeout=180)
        self.assertEqual(run.returncode, 0, run.stdout[-1500:] + run.stderr[-800:])
        report = json.loads(run.stdout.strip().splitlines()[-1])
        self.assertEqual(report["failed"], [])
        self.assertGreaterEqual(report["checks"], 100)


if __name__ == "__main__":
    unittest.main()
