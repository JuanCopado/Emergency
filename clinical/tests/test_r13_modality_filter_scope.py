"""R13 · R5-1 policy layer 5: the dermatological reassurance filter belongs to skin_wound only.

Backend behaviour as it stands (no change in R13). The same reassuring provider text, sent under each
modality the inactive UI prototype offers, is abstained only for skin_wound; ECG, radiograph, POCUS and
documents are interpreted without a dermatological block. Synthetic image and provider only.
"""
import base64
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import synthetic_images as si  # noqa: E402
import clinical_note_api as api  # noqa: E402
import clinical_note_vision_adapter as adapter  # noqa: E402

ENV = {"CLINICAL_VISION_PROVIDER_URL": "https://vision.example.test"}
REASSURING = {"contract_version": "1.0", "status": "ok", "provider": "synthetic", "model": "synthetic",
              "official_report": None, "ai_interpretation": "Benign lesion, no signs of infection.",
              "findings": "Erythema.", "impression": "Safe to observe.", "limitations": [], "confidence": "high"}
PROTOTYPE_TS = ROOT.parent / "app" / "src" / "clinical-note" / "r51Prototype.ts"


def run(kind):
    raw = si.png()
    content = base64.b64encode(raw).decode("ascii")
    prepared = api.prepare_upload("IMG_0001.png", "image/png", content, explicit_kind=kind)
    return api.interpret_prepared_upload(prepared, content, privacy_checked=True,
                                         burned_in_identifiers_checked=True,
                                         vision_transport=lambda cfg, req: dict(REASSURING), vision_env=ENV)


class FilterScope(unittest.TestCase):
    def test_only_skin_wound_is_abstained_for_reassuring_text(self):
        self.assertEqual(run("skin_wound")["prepared"]["processing"]["status"], "vision_abstained")
        for kind in ("ecg", "xray", "pocus"):
            with self.subTest(kind=kind):
                processing = run(kind)["prepared"]["processing"]
                self.assertEqual(processing["status"], "vision_interpreted")
                self.assertNotIn("reassurance_language", processing.get("safety_flags", []))

    def test_documents_never_reach_the_vision_provider_so_no_dermatological_filter_can_apply(self):
        with self.assertRaises(adapter.VisionAdapterError) as ctx:
            run("pdf_document")
        self.assertIn("not eligible for binary interpretation", str(ctx.exception))

    def test_the_prototype_table_marks_the_dermatological_filter_for_exactly_skin_wound(self):
        text = PROTOTYPE_TS.read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"dermatologicFilter:\s*true", text)), 1)
        self.assertRegex(text, r"kind:\s*'skin_wound'[^\n]*dermatologicFilter:\s*true")
        for kind in ("ecg", "xray", "pocus", "pdf_document"):
            self.assertRegex(text, rf"kind:\s*'{kind}'[^\n]*dermatologicFilter:\s*false")

    def test_the_prototype_adds_no_backend_behaviour(self):
        text = PROTOTYPE_TS.read_text(encoding="utf-8")
        self.assertNotIn("/api/", text)
        self.assertNotIn("fetch(", text)


if __name__ == "__main__":
    unittest.main()
