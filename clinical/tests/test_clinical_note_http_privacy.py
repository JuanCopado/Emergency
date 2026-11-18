"""Synthetic HTTP adapter privacy regressions, entirely offline."""
import io
import json
import pathlib
import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import clinical_note_api as api


def make_handler(payload=b"{}", path="/api/clinical-note/analyze"):
    handler = object.__new__(api.ClinicalNoteHandler)
    handler.path = path
    handler.headers = {"Content-Length": str(len(payload))}
    handler.rfile = io.BytesIO(payload)
    handler.wfile = io.BytesIO()
    handler.sent_status = []
    handler.sent_headers = {}
    handler.send_response = lambda status: handler.sent_status.append(int(status))
    handler.send_header = lambda key, value: handler.sent_headers.__setitem__(key, value)
    handler.end_headers = lambda: None
    return handler


class ClinicalNoteHttpPrivacyTests(unittest.TestCase):
    def test_unhandled_error_never_returns_private_exception_details(self):
        h = make_handler()
        with patch.object(api, "dispatch",
                          side_effect=RuntimeError("PRIVATE_SYNTHETIC_IDENTIFIER")):
            h.do_POST()
        self.assertEqual(500, h.sent_status[-1])
        self.assertEqual({"error": "clinical-note backend failure"},
                         json.loads(h.wfile.getvalue()))
        self.assertNotIn(b"PRIVATE_SYNTHETIC_IDENTIFIER", h.wfile.getvalue())

    def test_value_error_never_reflects_submitted_identifiers(self):
        h = make_handler()
        with patch.object(api, "dispatch",
                          side_effect=ValueError("PRIVATE_SYNTHETIC_IDENTIFIER")):
            h.do_POST()
        self.assertEqual(422, h.sent_status[-1])
        self.assertEqual({"error": "invalid clinical request"},
                         json.loads(h.wfile.getvalue()))

    def test_invalid_json_is_bad_request_not_generic_value_error(self):
        h = make_handler(b'{"note":')
        h.do_POST()
        self.assertEqual(400, h.sent_status[-1])
        self.assertEqual({"error": "invalid JSON"},
                         json.loads(h.wfile.getvalue()))

    def test_nonobject_json_rejected_before_dispatch(self):
        h = make_handler(b"[]")
        with patch.object(api, "dispatch",
                          side_effect=AssertionError("dispatch must not run")) as dispatch:
            h.do_POST()
        dispatch.assert_not_called()
        self.assertEqual(422, h.sent_status[-1])

    def test_success_retains_api_contract_and_hardens_headers(self):
        h = make_handler()
        with patch.object(api, "dispatch",
                          return_value=(HTTPStatus.OK, {"accepted": True})):
            h.do_POST()
        self.assertEqual(200, h.sent_status[-1])
        self.assertEqual({"accepted": True}, json.loads(h.wfile.getvalue()))
        self.assertEqual("nosniff", h.sent_headers["X-Content-Type-Options"])
        self.assertEqual("no-store", h.sent_headers["Cache-Control"])
        self.assertIn("default-src 'none'", h.sent_headers["Content-Security-Policy"])
        self.assertEqual("no-referrer", h.sent_headers["Referrer-Policy"])

    def test_audited_pediatric_band_stop_keeps_safe_explanation(self):
        h = make_handler(path="/api/pediatric-outpatient/calculate")
        with patch.object(api, "dispatch",
                          side_effect=ValueError("no matching age/weight band for regimen")):
            h.do_POST()
        self.assertEqual(422, h.sent_status[-1])
        self.assertEqual({"error": "no matching age/weight band for regimen"},
                         json.loads(h.wfile.getvalue()))

    def test_pediatric_error_message_not_exposed_on_other_endpoints(self):
        h = make_handler(path="/api/clinical-note/analyze")
        with patch.object(api, "dispatch",
                          side_effect=ValueError("no matching age/weight band for regimen")):
            h.do_POST()
        self.assertEqual({"error": "invalid clinical request"},
                         json.loads(h.wfile.getvalue()))

    def test_access_log_never_echoes_path_or_identifiers(self):
        h = make_handler()
        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            h.log_message("%s %s", "/api?patient=PRIVATE_SYNTHETIC_IDENTIFIER", "200")
        self.assertNotIn("PRIVATE_SYNTHETIC_IDENTIFIER", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
