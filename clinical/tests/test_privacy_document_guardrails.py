"""Bounded synthetic document/identifier regressions; no network or patient data."""
import base64
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import clinical_note_api as api
import clinical_note_support as support


def text_payload(text):
    return {"filename": "synthetic.txt", "mime_type": "text/plain",
            "content_base64": base64.b64encode(text.encode("utf-8")).decode("ascii")}


class MeteredText(str):
    """Count input visits, without a timing threshold tied to the test runner."""
    work = 0

    def find(self, sub, start=0, end=None):
        stop = len(self) if end is None else end
        result = super().find(sub, start, stop)
        self.work += (stop if result < 0 else result + len(sub)) - start
        return result

    def __getitem__(self, index):
        self.work += 1
        return super().__getitem__(index)


class PrivacyDocumentGuardrails(unittest.TestCase):
    def test_text_at_limit_is_preserved_including_last_character(self):
        text = "á" * (api.MAX_TEXT_CHARS - 1) + "终"
        status, prepared = api.dispatch("/api/clinical-note/upload/prepare", text_payload(text))
        self.assertEqual(status, 200)
        self.assertEqual(prepared["extracted"]["official_report"], text)
        self.assertEqual(prepared["size_bytes"], len(text.encode("utf-8")))
        self.assertFalse(prepared["original_retained"])
        api._verify_prepared(prepared)

    def test_text_over_limit_is_rejected_before_any_privacy_scan(self):
        for suffix in ("x", "SYNTHETIC_END_MARKER"):
            with self.subTest(extra_characters=len(suffix)):
                text = "x" * api.MAX_TEXT_CHARS + suffix
                with patch.object(api, "_privacy_for_text", side_effect=AssertionError("must not scan")) as scan:
                    with self.assertRaisesRegex(ValueError, "clinical text upload exceeds character limit"):
                        api.prepare_upload(**text_payload(text))
                scan.assert_not_called()

    def test_oversized_dispatch_has_safe_localizable_error_and_no_partial_upload(self):
        with patch.object(api, "_privacy_for_text") as scan:
            status, response = api.dispatch(
                "/api/clinical-note/upload/prepare",
                text_payload("x" * api.MAX_TEXT_CHARS + "SYNTHETIC_END_MARKER"),
            )
        self.assertEqual(status, 422)
        self.assertEqual(response, {
            "error": "clinical text upload exceeds character limit",
            "error_code": "text_upload_too_large", "max_text_chars": 120000,
        })
        self.assertNotIn("SYNTHETIC_END_MARKER", json.dumps(response))
        self.assertNotIn("prepared", response)
        scan.assert_not_called()

    def test_utf8_bom_and_nontext_routing_are_preserved(self):
        raw = b"\xef\xbb\xbf" + "x".encode() * api.MAX_TEXT_CHARS
        self.assertEqual(api._extract_text(raw, "synthetic.txt", "text/plain"), "x" * api.MAX_TEXT_CHARS)
        self.assertIsNone(api._extract_text(b"not interpreted here", "synthetic.bin", "application/octet-stream"))

    def test_name_labels_in_supported_languages_trigger_stop(self):
        values = [
            "Name: Synthetic Person", "Patient name: Synthetic Person", "Patient: Synthetic Person",
            "Nome: Pessoa Sintética", "Nome completo: Pessoa Sintética", "Doente: Pessoa Sintética",
            "Nombre: Persona Sintética", "Nombre completo: Persona Sintética", "Paciente: Persona Sintética",
            "姓名：合成示例", "患者姓名: 合成示例", "患者：合成示例", "病人姓名：合成示例",
        ]
        for value in values:
            with self.subTest(value=value):
                hits = support.scan_privacy({"text": value})
                self.assertTrue(any(h.get("pattern_id") == "labelled_name" and h["severity"] == "STOP" for h in hits))
                self.assertNotIn(value, json.dumps(hits, ensure_ascii=False))

    def test_contact_and_identifier_labels_extend_existing_languages(self):
        cases = {
            "labelled_phone": ["Teléfono: +34 600 000 000", "Telefone: +351 900 000 000",
                               "Phone: +44 7000 000000", "电话：13800000000"],
            "labelled_address": ["Dirección: Calle Sintética 00", "Morada: Rua Sintética 00",
                                 "Address: Synthetic Street 00", "地址：合成街道零号"],
            "labelled_identifier": ["DNI: 00000000X", "NIF: 000000000",
                                    "Passport: TEST00000", "身份证：000000000000000000"],
        }
        for expected, values in cases.items():
            for value in values:
                with self.subTest(value=value):
                    self.assertTrue(any(h.get("pattern_id") == expected for h in support.scan_privacy({"text": value})))

    def test_pasted_whitespace_before_name_and_address_delimiters(self):
        cases = [
            ("es", "Nombre", "Persona Sintética", "labelled_name"),
            ("pt", "Nome", "Pessoa Sintética", "labelled_name"),
            ("en", "Name", "Synthetic Person", "labelled_name"),
            ("zh", "姓名", "合成示例", "labelled_name"),
            ("es", "Dirección", "Calle Sintética 00", "labelled_address"),
            ("pt", "Morada", "Rua Sintética 00", "labelled_address"),
            ("en", "Address", "Synthetic Street 00", "labelled_address"),
            ("zh", "地址", "合成街道零号", "labelled_address"),
        ]
        for language, label, value, expected in cases:
            for separator in ("\u00a0", "\n"):
                with self.subTest(language=language, label=label, separator=repr(separator)):
                    hits = support.scan_privacy({"text": f"{label}{separator}: {value}"})
                    self.assertTrue(any(h.get("pattern_id") == expected and h["severity"] == "STOP" for h in hits))

    def test_unlabelled_clinical_prose_is_not_a_name(self):
        for value in ["Paciente estable. Niega dolor.", "Patient stable.", "Doente consciente.",
                      "患者意识清楚。", "Nombre del medicamento: ejemplo", "Patient condition: stable",
                      "Nome do exame: exemplo", "Surname-like fragment without a label"]:
            with self.subTest(value=value):
                self.assertFalse(support.scan_privacy({"text": value}))

    def test_email_matches_legacy_shape_on_positive_and_negative_examples(self):
        legacy = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
        cases = ["", "Synthetic text", "@example.invalid", "a@local", "a@local.a",
                 "a@.ab", "a@localhost.12", "a@example.invalid", "A.B+tag@sub-domain.invalid",
                 "<a@example.invalid>", "a@..invalid", "x@y.invalid@example.invalid",
                 "a@example.ab12", "a@example.ſK", "İ@example.invalid", "x@@a.invalid"]
        for value in cases:
            with self.subTest(value=value):
                self.assertEqual(support.contains_email_shape(value), bool(legacy.search(value)))
        hits = support.scan_privacy({"history": ["synthetic@example.invalid"]})
        self.assertEqual([(h["path"], h["pattern_id"]) for h in hits], [("$.history[0]", "email")])

    def test_email_scan_input_work_stays_linear_for_long_nonmatches(self):
        for size in (2000, 4000, 8000, 16000):
            for raw in ("a" * size, "a@" + "a" * size, "a@" * size,
                        "a@" + "a." * size + "a"):
                value = MeteredText(raw)
                self.assertFalse(support.contains_email_shape(value))
                self.assertLessEqual(value.work, 6 * len(value) + 10)

    def test_long_document_with_email_at_end_is_still_screened(self):
        email = "synthetic@example.invalid"
        text = "x" * (api.MAX_TEXT_CHARS - len(email) - 1) + " " + email
        prepared = api.prepare_upload(**text_payload(text))
        self.assertEqual(prepared["extracted"]["official_report"], text)
        self.assertEqual(prepared["privacy"]["status"], "STOP")
        self.assertTrue(any(x.get("pattern_id") == "email" for x in prepared["privacy"]["findings"]))

    def test_unknown_detector_is_not_silently_ignored(self):
        policy = {"forbidden_direct_identifier_fields": [],
                  "free_text_flag_patterns": [{"id": "synthetic", "detector": "unknown"}]}
        with self.assertRaisesRegex(ValueError, "unknown privacy detector"):
            support.scan_privacy({"text": "Synthetic"}, policy)


if __name__ == "__main__":
    unittest.main()
