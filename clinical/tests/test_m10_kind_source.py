"""R8 · M10 R5-1 transparency: the prepared upload reports where its category came from.

Routing is unchanged; `kind_source` is informational and never verifies the real modality.
Synthetic images only; no provider.
"""
import base64
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import synthetic_images as si  # noqa: E402
import clinical_note_api as api  # noqa: E402

ENV = {"CLINICAL_VISION_PROVIDER_URL": "https://vision.example.test"}
NAMES = ["herida_pierna.png", "dermatitis_contacto.png", "IMG_1234.jpg", "foto.png", "lesion_rx_01.png",
         "piel_tac.png", "rash_abdomen.png", "DSC0042.jpg", "ecg_01.png", "informe.pdf", "serie.dcm",
         "gasometria.png", "ulcera_pie_rm_03.png"]


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


class KindSource(unittest.TestCase):
    def test_routing_is_identical_to_the_previous_function(self):
        for name in NAMES:
            for explicit in (None, "", "skin_wound", "XRAY", "other_image"):
                with self.subTest(name=name, explicit=explicit):
                    kind, _ = api.infer_attachment_kind_with_source(name, None, explicit)
                    self.assertEqual(kind, api.infer_attachment_kind(name, None, explicit))

    def test_sources_are_reported_without_changing_the_kind(self):
        cases = (
            (("foto.png", None, "skin_wound"), ("skin_wound", "explicit")),
            (("herida_pierna.png", None, None), ("skin_wound", "inferred_from_filename")),
            (("dermatitis_contacto.png", None, None), ("ct", "inferred_from_filename")),
            (("IMG_1234.jpg", None, None), ("other_image", "default_unclassified")),
            (("foto.png", "image/png", None), ("other_image", "default_unclassified")),
            (("serie.dcm", None, None), ("other_image", "inferred_from_container")),
            (("informe.pdf", None, None), ("pdf_document", "inferred_from_container")),
        )
        for args, expected in cases:
            with self.subTest(args=args):
                self.assertEqual(api.infer_attachment_kind_with_source(*args), expected)

    def test_prepared_upload_carries_the_source_and_signs_it(self):
        raw = si.png()
        for name, kind, source in (("herida.png", "skin_wound", "explicit"),
                                   ("herida.png", None, "inferred_from_filename"),
                                   ("IMG_0001.png", None, "default_unclassified")):
            with self.subTest(name=name, kind=kind):
                prepared = api.prepare_upload(name, "image/png", b64(raw), explicit_kind=kind)
                self.assertEqual(prepared["kind_source"], source)
        prepared["kind_source"] = "explicit"  # tampering must be rejected by the integrity token
        with self.assertRaises(ValueError) as ctx:
            api.interpret_prepared_upload(prepared, b64(raw), privacy_checked=True,
                                          burned_in_identifiers_checked=True,
                                          vision_transport=lambda c, r: {}, vision_env=ENV)
        self.assertIn("integrity", str(ctx.exception))

    def test_no_change_to_the_provider_request_or_the_filter(self):
        raw = si.png()
        response = {"contract_version": "1.0", "status": "ok", "provider": "synthetic", "model": "synthetic",
                    "official_report": None, "ai_interpretation": "Benign lesion, no signs of infection.",
                    "findings": "Erythema.", "impression": None, "limitations": [], "confidence": "high"}
        seen = {}

        def transport(cfg, request):
            seen["request"] = request
            return response

        for name, kind, status in (("herida.png", "skin_wound", "vision_abstained"),
                                   ("IMG_0001.png", None, "vision_interpreted")):
            prepared = api.prepare_upload(name, "image/png", b64(raw), explicit_kind=kind)
            out = api.interpret_prepared_upload(prepared, b64(raw), privacy_checked=True,
                                                burned_in_identifiers_checked=True,
                                                vision_transport=transport, vision_env=ENV)
            self.assertEqual(out["prepared"]["processing"]["status"], status)
            self.assertNotIn("kind_source", seen["request"])
            self.assertEqual(out["prepared"]["kind_source"], prepared["kind_source"])

    def test_older_prepared_uploads_without_the_field_still_verify(self):
        raw = si.png()
        prepared = api.prepare_upload("IMG_0001.png", "image/png", b64(raw))
        legacy = {k: v for k, v in prepared.items() if k not in ("kind_source", "integrity_token")}
        legacy = api._sign_prepared(legacy)
        api._verify_prepared(legacy)
        self.assertNotIn("kind_source", legacy)


if __name__ == "__main__":
    unittest.main()
