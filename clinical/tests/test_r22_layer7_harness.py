"""R22 · Layer 7 arm-B harness (DEC-CLIN-R22-01 alt. B): fidelity, protected flows, forbidden evidence and ISOLATION from the product."""
import ast
import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "clinical"
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "tests"))
from human_factors import layer7_harness as harness, layer7_simulator as sim, synthetic_bank as bank  # noqa: E402
from test_r14_layer7_contract import APPROVED_MESSAGES  # noqa: E402  (independent literal copy of the approved wording)

BASE = {"flow": "modality_entry", "modality_declared": True, "declared_kind": "skin_wound", "signature_kind": "jpeg",
        "container_parse_ok": True, "declared_mime_type": "image/jpeg", "declared_extension": ".jpg"}


def d(**changes):
    return dict(BASE, **changes)


class Fidelity(unittest.TestCase):
    def test_texts_are_the_approved_literals_in_all_three_languages(self):
        self.assertEqual(sim.MESSAGE_TEXTS, APPROVED_MESSAGES)
        for case_id, descriptor, expected in bank.layer7_descriptors():
            for language in harness.LANGUAGES:
                out = harness.run_case("B", descriptor, language)
                if expected:
                    self.assertEqual(out["trigger_id"], expected, case_id)
                    self.assertEqual(out["message_text"], APPROVED_MESSAGES[out["message_id"]][language])
                    self.assertFalse(out["send_allowed"])
                else:
                    self.assertFalse(out["layer7_shown"]); self.assertIsNone(out["message_text"]); self.assertTrue(out["send_allowed"])
                self.assertEqual(out["label"], "SIMULATED_LAYER7_HARNESS_LAB_ONLY")

    def test_arm_a_never_shows_layer7(self):
        for _, descriptor, _ in bank.layer7_descriptors():
            out = harness.run_case("A", descriptor, "es")
            self.assertFalse(out["layer7_shown"]); self.assertIsNone(out["trigger_id"]); self.assertTrue(out["send_allowed"])

    def test_scenario_classes_and_strata(self):
        self.assertEqual({harness.stratum(c) for c in "BCD"}, {"selector_bypass"})
        self.assertEqual({harness.stratum(c) for c in ("E1", "E2")}, {"layer7_comprehension"})
        self.assertEqual(harness.stratum("F"), "non_interference")
        with self.assertRaises(ValueError):
            harness.stratum("Z")

    def test_bypass_scenarios_never_trigger_layer7(self):
        """B/C/D: a technically sound RGB skin photo sent under ECG/Rx/POCUS must NOT abstain (no pixel/EXIF/visual inference)."""
        for scenario_class, kind in (("B", "ecg"), ("C", "xray"), ("D", "pocus")):
            out = harness.run_case("B", d(declared_kind=kind), "es", scenario_class)
            self.assertTrue(harness.conforms(out), scenario_class)

    def test_e1_e2_trigger_as_specified(self):
        e1 = harness.run_case("B", d(modality_declared=False, declared_kind=None), "pt", "E1")
        e2a = harness.run_case("B", d(container_parse_ok=False), "pt", "E2")
        e2b = harness.run_case("B", d(signature_kind="audio", declared_mime_type="audio/mpeg", declared_extension=".mp3"), "pt", "E2")
        for out in (e1, e2a, e2b):
            self.assertTrue(harness.conforms(out)); self.assertTrue(out["layer7_shown"])
        wrong = dict(e1, scenario_class="F")
        self.assertFalse(harness.conforms(wrong))

    def test_zero_false_blocks_on_valid_photos_and_protected_flows(self):
        """F: every valid image container for every modality, plus classic_upload and the kind=null document bridge, shows no Layer 7."""
        count = 0
        for kind, formats in sim.MODALITY_FORMATS.items():
            for signature in formats:
                mime = {"jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "pdf": "application/pdf", "dicom": "application/dicom", "text": "text/plain"}[signature]
                out = harness.run_case("B", d(declared_kind=kind, signature_kind=signature, declared_mime_type=mime, declared_extension=None), "en", "F")
                self.assertTrue(harness.conforms(out), (kind, signature)); count += 1
        for flow in ("classic_upload", "document_legacy_bridge"):
            for signature in ("jpeg", "png", "pdf"):
                out = harness.run_case("B", d(flow=flow, modality_declared=False, declared_kind=None, signature_kind=signature), "es", "F")
                self.assertTrue(harness.conforms(out), (flow, signature)); count += 1
        self.assertGreater(count, 20)

    def test_forbidden_evidence_cannot_enter(self):
        for field in ("rgb_mean", "exif", "file_name", "dicom_absent", "pixel_stats", "model_output", "clinical_suspicion"):
            with self.assertRaises(ValueError, msg=field):
                harness.run_case("B", dict(BASE, **{field: 1}), "es")
        with self.assertRaises(ValueError):
            harness.run_case("B", {k: v for k, v in BASE.items() if k != "flow"}, "es")
        with self.assertRaises(ValueError):
            harness.run_case("B", BASE, "zh")                       # no approved zh text
        with self.assertRaises(ValueError):
            harness.run_case("C", BASE, "es")

    def test_file_name_and_extension_do_not_change_the_decision(self):
        base = harness.run_case("B", d(declared_extension=".jpg"), "es")["trigger_id"]
        for ext in (None, ".png", ".dcm", ".pdf", ".xyz"):
            self.assertEqual(harness.run_case("B", d(declared_extension=ext), "es")["trigger_id"], base)


class Isolation(unittest.TestCase):
    """The harness must not be reachable from the product: no import, no flag read, no bundle or CI path."""

    def test_product_sources_do_not_reference_the_lab(self):
        needles = re.compile(r"layer7_harness|layer7_simulator|human_factors|clinical/lab|VITE_R51_LAYER7")
        offenders = []
        for base in ("app/src", "app/scripts", "app/vite.config.ts", "app/package.json", "app/index.html"):
            path = REPO / base
            files = [path] if path.is_file() else list(path.rglob("*")) if path.exists() else []
            for f in files:
                if f.is_file() and f.suffix in {".ts", ".tsx", ".js", ".mjs", ".cjs", ".json", ".html", ".mts"} and "generatedClinicalGuides" not in f.name:
                    if needles.search(f.read_text(encoding="utf-8", errors="ignore")):
                        offenders.append(str(f.relative_to(REPO)))
        # the A/B preflight legitimately names the study scripts; Layer 7 itself must still be absent from the product
        allowed = {"app/scripts/hf-lab-preflight.mjs", "app/scripts/hf-lab-preflight.d.mts", "app/scripts/hf-lab-preflight.test.ts"}
        bad = [o for o in offenders if o not in allowed]
        self.assertEqual(bad, [], bad)
        for name in allowed & set(offenders):
            self.assertNotRegex((REPO / name).read_text(encoding="utf-8"), r"layer7_harness|layer7_simulator|VITE_R51_LAYER7")

    def test_product_python_does_not_import_the_lab(self):
        for f in (ROOT / "scripts").glob("*.py"):
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                for n in names:
                    self.assertFalse(n.startswith("human_factors") or "layer7_harness" in n or "layer7_simulator" in n, f"{f.name} imports {n}")

    def test_contract_stays_inactive_and_flag_inert(self):
        contract = json.loads(sim.CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["x-feature-flag"], {"name": "VITE_R51_LAYER7", "default": False, "production": "IGNORED", "connected_to_product": False})
        self.assertIn("PROPOSED_INACTIVE", json.dumps(contract["x-status"]))

    def test_harness_has_no_io_beyond_the_contract(self):
        for module in ("layer7_harness.py", "layer7_simulator.py"):
            tree = ast.parse((ROOT / "lab" / "human_factors" / module).read_text(encoding="utf-8"))
            imports = {n.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for n in node.names}
            imports |= {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
            self.assertFalse(imports & {"socket", "urllib", "http", "requests", "subprocess", "os", "shutil"}, (module, imports))
            calls = [n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
            self.assertNotIn("open", calls)


if __name__ == "__main__":
    unittest.main()
