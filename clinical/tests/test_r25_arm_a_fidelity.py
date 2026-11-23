"""R25 · arm A fidelity tool (laboratory only): the stub uses the REAL server dispatch, and the committed measurement never claims equivalence."""
import base64
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
FID = ROOT / "lab" / "human_factors" / "fidelity"
REPORT = json.loads((FID / "arm_a_fidelity_report.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(ROOT / "tests"))
import synthetic_images as si  # noqa: E402


def stub(payload):
    out = subprocess.run([sys.executable, "-I", str(FID / "prepare_stub.py")], check=True, capture_output=True,
                         input=json.dumps({"path": "/api/clinical-note/upload/prepare", "payload": payload}).encode())
    return json.loads(out.stdout)


class Stub(unittest.TestCase):
    def test_valid_image_is_prepared_by_the_real_dispatch(self):
        r = stub({"filename": "foto.png", "mime_type": "image/png", "content_base64": base64.b64encode(si.png()).decode()})
        self.assertEqual(r["status"], 200)
        self.assertEqual((r["body"]["kind"], r["body"]["kind_source"]), ("other_image", "default_unclassified"))

    def test_rejections_use_the_public_http_mapping(self):
        r = stub({"filename": "a.wav", "mime_type": "audio/wav", "content_base64": base64.b64encode(b"RIFF").decode()})
        self.assertEqual((r["status"], r["body"]), (422, {"error": "invalid or unsupported clinical image or filename"}))
        r = stub({"filename": "a.jpg", "mime_type": "image/jpeg", "content_base64": ""})
        self.assertEqual(r["status"], 422)


class Report(unittest.TestCase):
    def test_mockup_is_not_declared_equivalent(self):
        self.assertEqual(REPORT["verdict"]["functional_equivalence"], "NOT_EQUIVALENT")
        self.assertTrue(REPORT["verdict"]["gaps"])
        self.assertFalse(REPORT["edge_checked"])

    def test_measurement_covers_the_requested_viewports_and_languages(self):
        seen = {(r["lang"], r["viewport"]["width"]) for r in REPORT["real_ui"]}
        self.assertEqual(seen, {(l, w) for l in ("es", "pt", "en") for w in (320, 360, 390, 1280)})

    def test_real_control_has_no_layer7_and_pdf_keeps_the_known_label_defect_on_the_base(self):
        pdf = next(u for u in REPORT["uploads"] if u["file"] == "S1-13.pdf")
        self.assertTrue(pdf["review_card"]); self.assertFalse(pdf["interpret_button"])
        self.assertIn("Categoría efectiva: Otro", pdf["card_text"])      # R8-PDF defect on the base (fixed in PR #88)
        for u in REPORT["uploads"]:
            self.assertNotIn("capa 7", (u["card_text"] or "").lower())


if __name__ == "__main__":
    unittest.main()
