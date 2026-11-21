"""R7 · M10 R5-2 (encoding level only): invisible/compatibility characters must not hide an
already-defined reassurance phrase. No wording is added to the lexicon and the guard scope
(skin_wound only, R5-1) is intentionally unchanged. Synthetic text and mocked transport."""
import base64
import sys
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import synthetic_images as si  # noqa: E402
import clinical_note_api as api  # noqa: E402
import clinical_note_vision_adapter as adapter  # noqa: E402

ENV = {"CLINICAL_VISION_PROVIDER_URL": "https://vision.example.test"}
ZW, SHY = "​", "­"
VARIANTS = {
    "zero-width inside word": "Be" + ZW + "nign lesion.",
    "soft hyphen inside word": "be" + SHY + "nign lesion",
    "zero-width joiner": "ru‍led out",
    "fullwidth letters": "ｂｅｎｉｇｎ lesion",
    "decomposed accents": unicodedata.normalize("NFD", "Infección excluída."),
    "zero-width inside phrase": "no signs" + ZW + " of infection",
}
CLEAN = ("Erythema 3 cm, central ulcer.", "Eritema de 3 cm con úlcera central.", "Café au lait macule, 2 cm.")


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


def response(**kw):
    base = {"contract_version": "1.0", "status": "ok", "provider": "synthetic", "model": "synthetic",
            "official_report": None, "ai_interpretation": "Erythematous patch.", "findings": "Erythema.",
            "impression": None, "limitations": [], "confidence": None}
    base.update(kw)
    return base


def run(kind, payload):
    raw = si.png()
    prepared = api.prepare_upload("herida.png", "image/png", b64(raw), explicit_kind=kind)
    out = api.interpret_prepared_upload(prepared, b64(raw), privacy_checked=True,
                                        burned_in_identifiers_checked=True,
                                        vision_transport=lambda c, r: payload, vision_env=ENV)
    return out["prepared"]["processing"]


class EncodingLevelNormalization(unittest.TestCase):
    def test_variants_of_defined_phrases_are_flagged_in_every_clinical_field(self):
        for label, text in VARIANTS.items():
            for field in ("ai_interpretation", "findings", "impression"):
                with self.subTest(label=label, field=field):
                    proc = run("skin_wound", response(**{field: text}))
                    self.assertEqual(proc["status"], "vision_abstained")
                    self.assertIn("reassurance_language", proc["safety_flags"])
                    self.assertIsNone(proc["findings"])

    def test_variants_in_limitations_and_labels_are_removed(self):
        for label, text in VARIANTS.items():
            with self.subTest(label=label):
                proc = run("skin_wound", response(limitations=[text, "Photograph only."]))
                self.assertNotIn(text, proc["limitations"])
                self.assertIn("reassurance_language", proc["safety_flags"])
                if text.isprintable():  # invisible characters are already rejected in labels (502)
                    proc = run("skin_wound", response(provider=text))
                    self.assertEqual(proc["provider"], "configured-provider")
                else:
                    with self.assertRaises(adapter.VisionProviderResponseError):
                        run("skin_wound", response(provider=text))

    def test_clean_descriptive_text_is_not_flagged(self):
        for text in CLEAN:
            with self.subTest(text=text):
                proc = run("skin_wound", response(impression=text))
                self.assertEqual(proc["status"], "vision_interpreted")
                self.assertNotIn("reassurance_language", proc["safety_flags"])

    def test_fold_only_changes_encoding_not_wording(self):
        self.assertEqual(adapter._fold("a" + ZW + "b  \n c" + SHY), "ab c")
        self.assertEqual(adapter._fold("ｆｕｌｌ"), "full")
        self.assertEqual(adapter._fold("Lesión"), unicodedata.normalize("NFC", "Lesión"))

    def test_guard_scope_is_unchanged_for_other_categories(self):
        for kind in ("other_image", "xray"):
            with self.subTest(kind=kind):
                proc = run(kind, response(impression="Be" + ZW + "nign lesion."))
                self.assertEqual(proc["status"], "vision_interpreted")
                self.assertNotIn("reassurance_language", proc["safety_flags"])


if __name__ == "__main__":
    unittest.main()
