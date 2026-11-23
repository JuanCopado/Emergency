"""R21-PAR · deterministic simulator of the Layer 7 triggers (laboratory only; results are simulated, not product behaviour)."""
import ast
import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from human_factors import layer7_simulator as sim  # noqa: E402

SCHEMA = json.loads(sim.CONTRACT.read_text(encoding="utf-8"))
VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


def descriptor(**changes):
    base = {"flow": "modality_entry", "modality_declared": True, "declared_kind": "ecg", "signature_kind": "jpeg",
            "container_parse_ok": True, "declared_mime_type": "image/jpeg", "declared_extension": ".jpg"}
    base.update(changes)
    return base


class Layer7Simulator(unittest.TestCase):
    def run_case(self, **changes):
        out = sim.evaluate(descriptor(**changes))
        VALIDATOR.validate(out["document"])        # every result is a valid contract document
        self.assertIs(out["simulated"], True)
        return out

    def trigger(self, **changes):
        return self.run_case(**changes)["document"].get("trigger_id")

    def test_each_trigger_and_its_exact_approved_text(self):
        cases = ((dict(modality_declared=False, declared_kind=None), "T7-01_UNDECLARED_MODALITY", "MSG_T7_A"),
                 (dict(declared_kind="unknown_kind"), "T7-02_UNKNOWN_CONTRACT", "MSG_T7_A"),
                 (dict(container_parse_ok=False), "T7-03_CORRUPT_UNPROCESSABLE", "MSG_T7_C"),
                 (dict(signature_kind="audio"), "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_D"),
                 (dict(declared_kind="skin_wound", signature_kind="pdf"), "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_B"))
        for changes, trigger, message in cases:
            out = self.run_case(**changes)
            self.assertEqual((out["document"]["trigger_id"], out["document"]["message_id"]), (trigger, message), changes)
            self.assertEqual(out["message_texts"], sim.MESSAGE_TEXTS[message])
            self.assertIs(out["document"]["send_allowed"], False)

    def test_a_technically_valid_photo_of_any_modality_is_never_rejected(self):
        for kind in ("ecg", "xray", "pocus", "document"):
            for signature in ("jpeg", "png", "webp"):
                out = self.run_case(declared_kind=kind, signature_kind=signature)
                self.assertEqual(out["document"]["decision"], "none", (kind, signature))
                self.assertNotIn("message_texts", out)

    def test_protected_flows_get_no_selection_blocks(self):
        for flow in ("classic_upload", "document_legacy_bridge"):
            changes = dict(flow=flow, modality_declared=False, declared_kind=None)
            self.assertIsNone(self.trigger(**changes))
            self.assertEqual(self.trigger(container_parse_ok=False, **changes), "T7-03_CORRUPT_UNPROCESSABLE")
            self.assertEqual(self.trigger(signature_kind="audio", **changes), "T7-04_FORMAT_CONTAINER_MISMATCH")
        self.assertIsNone(self.trigger(flow="classic_upload", declared_kind="whatever"))

    def test_the_selection_gate_precedes_integrity_which_precedes_compatibility(self):
        self.assertEqual(self.trigger(modality_declared=False, declared_kind=None, container_parse_ok=False, signature_kind="audio"),
                         "T7-01_UNDECLARED_MODALITY")
        self.assertEqual(self.trigger(container_parse_ok=False, signature_kind="audio"), "T7-03_CORRUPT_UNPROCESSABLE")
        self.assertEqual(sim.PRECEDENCE, ("T7-01", "T7-02", "T7-03", "T7-04"))

    def test_malformed_descriptors_are_rejected(self):
        for bad in (dict(flow="web"), dict(signature_kind="gif"), dict(modality_declared="yes"), dict(container_parse_ok=1),
                    dict(declared_kind=5), dict(flow="document_legacy_bridge", declared_kind="ecg", modality_declared=True),
                    dict(modality_declared=False, declared_kind="ecg"), dict(declared_mime_type=3)):
            with self.assertRaises(ValueError, msg=str(bad)):
                sim.evaluate(descriptor(**bad))
        for broken in ({}, {**descriptor(), "pixels": "x"}, {k: v for k, v in descriptor().items() if k != "flow"}, [], None):
            with self.assertRaises(ValueError):
                sim.evaluate(broken)

    def test_the_simulator_reads_no_pixels_exif_filenames_dicom_absence_or_files(self):
        tree = ast.parse(Path(sim.__file__).read_text(encoding="utf-8"))
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertEqual(names & {"open", "read_bytes", "read_text_file", "exif", "getpixel", "filename", "rgb", "pixels", "Image"}, set())
        self.assertEqual(sim.DESCRIPTOR_FIELDS & {"pixels", "exif", "filename", "rgb", "dicom_absent"}, set())

    def test_it_is_not_wired_into_the_product(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            self.assertNotIn("layer7_simulator", path.read_text(encoding="utf-8", errors="ignore"), str(path))


if __name__ == "__main__":
    unittest.main()
