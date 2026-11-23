"""R27 · Layer 7 adapter for arm B: T7-01..T7-04, no false blocks, no visual inference, no force-send, arm A untouched. Laboratory only."""
import base64
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
from human_factors import layer7_adapter as ad, layer7_simulator as sim  # noqa: E402

STIMULI = ROOT / "lab" / "human_factors" / "bank" / "stimuli"
CONTRACT = json.loads((ROOT / "references" / "modality-abstention-layer7.contract.proposed.json").read_text(encoding="utf-8"))
TEXTS = CONTRACT["x-message-texts"]


def synthetic_image(fmt):
    """Valid RGB photo-like file generated in memory (no EXIF, no DICOM): the bank files of the other PRs are not needed here."""
    import io
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (160, 120), (240, 230, 230))
    ImageDraw.Draw(img).line([(0, 60), (160, 40)], fill=(20, 20, 20), width=2)
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return buffer.getvalue()


def body(name, explicit_kind=None, mime=None):
    if name.startswith("syn-"):
        data = synthetic_image({"jpg": "JPEG", "webp": "WEBP", "png": "PNG"}[name.rsplit(".", 1)[1]])
    else:
        data = (STIMULI / name).read_bytes()
    return {"filename": name, "mime_type": mime, "content_base64": base64.b64encode(data).decode(), "explicit_kind": explicit_kind}


class Triggers(unittest.TestCase):
    def test_t7_01_no_modality(self):
        out = ad.evaluate_upload(body("S1-14.png", None, "image/png"), None)
        self.assertEqual((out["abstains"], out["trigger_id"]), (True, "T7-01_UNDECLARED_MODALITY"))
        self.assertFalse(out["reachable_in_real_prototype_ui"])          # the real R5-1 UI cannot send without a modality

    def test_t7_03_corrupt_container_on_the_photo_route(self):
        out = ad.evaluate_upload(body("S1-15.jpg", "skin_wound", "image/jpeg"), "skin_wound")
        self.assertEqual((out["abstains"], out["trigger_id"]), (True, "T7-03_CORRUPT_UNPROCESSABLE"))

    def test_t7_04_pdf_sent_to_a_photo_only_route(self):
        out = ad.evaluate_upload(body("S2-15.pdf", "skin_wound", "application/pdf"), "skin_wound")
        self.assertEqual((out["abstains"], out["trigger_id"]), (True, "T7-04_FORMAT_CONTAINER_MISMATCH"))

    def test_t7_04_global_unsupported_format_audio(self):
        out = ad.evaluate_upload(body("QA-01.wav", "skin_wound", "audio/wav"), "skin_wound")
        self.assertEqual(out["trigger_id"], "T7-04_FORMAT_CONTAINER_MISMATCH")
        self.assertEqual(out["message_id"], "MSG_T7_D")                  # global unsupported format -> text 4
        self.assertIn("container_format_unsupported", json.dumps(sim.evaluate(out["descriptor"])))

    def test_texts_are_the_approved_literals(self):
        for lang in ("es", "pt", "en"):
            out = ad.evaluate_upload(body("S2-15.pdf", "skin_wound", "application/pdf"), "skin_wound", lang)
            self.assertIn(out["message_text"], TEXTS[out["message_id"]].values())
            self.assertEqual(out["message_text"], TEXTS[out["message_id"]][lang])

    def test_no_force_send_path(self):
        for name, kind, mime in (("S1-15.jpg", "skin_wound", "image/jpeg"), ("S2-15.pdf", "skin_wound", "application/pdf")):
            out = ad.evaluate_upload(body(name, kind, mime), "skin_wound")
            self.assertIs(out["force_send_available"], False)
            self.assertEqual(out["mode"], "SIMULATED_LAB_HARNESS_ONLY")


class NoFalseBlocks(unittest.TestCase):
    def test_document_legacy_bridge_kind_null_never_triggers_t7_01(self):
        for name, mime in (("S1-13.pdf", "application/pdf"), ("syn-sheet.jpg", "image/jpeg")):
            out = ad.evaluate_upload(body(name, None, mime), "document")
            self.assertFalse(out["abstains"], name)
            self.assertEqual(out["descriptor"]["flow"], "document_legacy_bridge")
            self.assertIsNone(out["descriptor"]["declared_kind"])

    def test_valid_rgb_ecg_and_monitor_photos_pass_without_dicom(self):
        for name, mime in (("syn-ecg.jpg", "image/jpeg"), ("syn-monitor.webp", "image/webp"), ("syn-ecg.png", "image/png")):
            out = ad.evaluate_upload(body(name, "ecg", mime), "ecg")
            self.assertFalse(out["abstains"], name)

    def test_bypass_scenarios_do_not_infer_from_pixels(self):
        # a skin-like technical placeholder sent under ECG/xray/pocus is technically valid: Layer 7 must NOT act (M1 is a human-factors outcome)
        for declared in ("ecg", "xray", "pocus"):
            out = ad.evaluate_upload(body("S1-14.png", declared, "image/png"), declared)
            self.assertFalse(out["abstains"], declared)

    def test_filename_and_extension_do_not_change_the_decision(self):
        a = ad.evaluate_upload(body("syn-ecg.jpg", "ecg", "image/jpeg"), "ecg")
        renamed = body("syn-ecg.jpg", "ecg", "image/jpeg"); renamed["filename"] = "herida_rx_ecg.jpg"
        b = ad.evaluate_upload(renamed, "ecg")
        self.assertEqual((a["abstains"], a["trigger_id"]), (b["abstains"], b["trigger_id"]))

    def test_unknown_ui_modality_is_rejected(self):
        with self.assertRaises(ValueError):
            ad.evaluate_upload(body("syn-ecg.jpg", "ecg"), "mri")


class Isolation(unittest.TestCase):
    def test_product_sources_do_not_reference_the_adapter(self):
        root = ROOT.parent
        for folder, patterns in ((root / "app" / "src", ("*.ts", "*.tsx")), (ROOT / "scripts", ("*.py",))):
            for pattern in patterns:
                for path in folder.rglob(pattern):
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    self.assertNotIn("layer7_adapter", text, path)
                    self.assertNotIn("SIMULATED_LAB_HARNESS_ONLY", text, path)

    def test_the_adapter_performs_no_network_or_provider_call(self):
        source = (ROOT / "lab" / "human_factors" / "layer7_adapter.py").read_text(encoding="utf-8")
        for needle in ("import socket", "import requests", "import urllib", "http.client", "subprocess"):
            self.assertNotIn(needle, source)


if __name__ == "__main__":
    unittest.main()
