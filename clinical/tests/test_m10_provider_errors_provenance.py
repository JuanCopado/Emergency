"""R6 · M10 N3/N2: provider failures are not request errors; abstention is not AI provenance.

Synthetic images and mocked transports only. No network, provider or patient data.
"""
import base64
import http.client
import io
import json
import sys
import unittest
import urllib.error
from email.message import Message
from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import synthetic_images as si  # noqa: E402
import clinical_note_api as api  # noqa: E402
import clinical_note_vision_adapter as adapter  # noqa: E402
import image_upload_guard as guard  # noqa: E402
from clinical_note_support import new_note  # noqa: E402

ENV = {"CLINICAL_VISION_PROVIDER_URL": "https://vision.example.test"}


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


def prepared_for(raw, name="herida_pierna.png", kind="skin_wound"):
    return api.prepare_upload(name, "image/png", b64(raw), explicit_kind=kind)


def ok_response(**kw):
    base = {"contract_version": "1.0", "status": "ok", "provider": "synthetic", "model": "synthetic",
            "official_report": None, "ai_interpretation": "Erythematous patch.",
            "findings": "Erythema, 3 cm.", "impression": None, "limitations": [], "confidence": None}
    base.update(kw)
    return base


def interpret(raw, **kw):
    prepared = prepared_for(raw)
    return api.interpret_prepared_upload(prepared, b64(raw), privacy_checked=True,
                                         burned_in_identifiers_checked=True, **kw)


class FakeOpener:
    def __init__(self, exc=None, body=b""):
        self.exc, self.body = exc, body

    def open(self, request, timeout=None):
        if self.exc:
            raise self.exc
        response = Mock()
        response.read.return_value = self.body
        response.__enter__ = lambda s: response
        response.__exit__ = lambda *a: False
        return response


class N3ProviderErrors(unittest.TestCase):
    def setUp(self):
        self.raw = si.png()

    def test_configuration_failures_are_typed_and_skip_raster_work(self):
        for label, env in (("unset", {}), ("http", {"CLINICAL_VISION_PROVIDER_URL": "http://x.test"}),
                           ("timeout", {**ENV, "CLINICAL_VISION_TIMEOUT_SECONDS": "abc"}),
                           ("range", {**ENV, "CLINICAL_VISION_TIMEOUT_SECONDS": "999"})):
            with self.subTest(label), patch.object(guard, "strip_metadata") as strip, \
                    self.assertRaises(adapter.VisionProviderConfigError):
                interpret(self.raw, vision_env=env)
            strip.assert_not_called()

    def test_transport_failures_are_unavailable(self):
        failures = (urllib.error.URLError("synthetic"), TimeoutError("synthetic"), ConnectionResetError(),
                    http.client.BadStatusLine("synthetic"), http.client.IncompleteRead(b""),
                    urllib.error.HTTPError("https://vision.example.test", 500, "x", Message(), io.BytesIO()))
        for exc in failures:
            with self.subTest(type(exc).__name__), \
                    patch.object(adapter.urllib.request, "build_opener", return_value=FakeOpener(exc)), \
                    self.assertRaises(adapter.VisionProviderUnavailable):
                interpret(self.raw, vision_env=ENV)

    def test_malformed_provider_body_remains_response_error(self):
        for body in (b"not json", b"\xff\xfe", b"[]", b'{"contract_version":"9"}'):
            with self.subTest(body=body), \
                    patch.object(adapter.urllib.request, "build_opener", return_value=FakeOpener(body=body)), \
                    self.assertRaises(adapter.VisionProviderResponseError):
                interpret(self.raw, vision_env=ENV)

    def test_input_and_gate_errors_are_not_provider_errors(self):
        prepared = prepared_for(self.raw)
        with self.assertRaises(adapter.VisionAdapterError) as ctx:
            api.interpret_prepared_upload(prepared, b64(self.raw), vision_env=ENV,
                                          vision_transport=lambda c, r: ok_response())
        self.assertNotIsInstance(ctx.exception, (adapter.VisionProviderConfigError,
                                                 adapter.VisionProviderUnavailable))

    @staticmethod
    def request(path, payload):
        body = json.dumps(payload).encode()
        handler = Mock()
        handler.headers = Message()
        handler.headers["Content-Type"] = "application/json"
        handler.headers["Content-Length"] = str(len(body))
        handler.server = SimpleNamespace(server_address=("127.0.0.1", 8765), server_port=8765)
        api.configure_local_server(handler.server)
        handler.client_address = ("127.0.0.1", 1)
        handler.headers["Host"] = "127.0.0.1:8765"
        handler.headers["Origin"] = "http://127.0.0.1:8765"
        handler.headers["X-Emergency-Local-Token"] = handler.server.clinical_session_token
        handler.rfile = io.BytesIO(body)
        handler.path = path
        return handler

    def post(self, error):
        handler = self.request("/api/clinical-note/upload/interpret", {})
        with patch.object(api, "dispatch", side_effect=error):
            api.ClinicalNoteHandler.do_POST(handler)
        return handler._send.call_args.args

    def test_http_contract_separates_service_from_request_errors(self):
        secret = "https://user:TOKEN-123@vision.internal.example/path"
        self.assertEqual(self.post(adapter.VisionProviderConfigError(secret)),
                         (HTTPStatus.SERVICE_UNAVAILABLE, {"error": "clinical vision provider is not configured"}))
        self.assertEqual(self.post(adapter.VisionProviderUnavailable(secret)),
                         (HTTPStatus.SERVICE_UNAVAILABLE, {"error": "clinical vision provider unavailable"}))
        self.assertEqual(self.post(adapter.VisionProviderResponseError(secret)),
                         (HTTPStatus.BAD_GATEWAY,
                          {"error": "clinical vision provider returned an invalid response"}))
        self.assertEqual(self.post(adapter.VisionAdapterError("privacy STOP " + secret)),
                         (HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "invalid clinical request"}))
        self.assertEqual(self.post(guard.MediaRejected("truncated")),
                         (HTTPStatus.UNPROCESSABLE_ENTITY,
                          {"error": "invalid or unsupported clinical image or filename"}))
        for error in (adapter.VisionProviderConfigError(secret), adapter.VisionProviderUnavailable(secret)):
            self.assertNotIn("TOKEN-123", json.dumps(self.post(error)[1]))


class N2ProvenanceAfterAbstention(unittest.TestCase):
    def accept(self, prepared, edit):
        note = new_note(age_years=40, sex="female")
        out = api.accept_prepared_upload(note, prepared, clinician_edit=edit, privacy_checked=True,
                                         burned_in_identifiers_checked=True)
        return out["report"]

    def test_abstention_before_provider_with_manual_text_is_clinician_entry(self):
        raw = si.png(width=32, height=32)
        prepared = interpret(raw, vision_env=ENV)["prepared"]
        self.assertEqual(prepared["processing"]["status"], "vision_abstained")
        for field in ("official_report", "ai_interpretation", "findings"):
            with self.subTest(field):
                report = self.accept(prepared, {field: "Manual observation by clinician."})
                self.assertEqual(report["provenance"], "clinician_entry")
                self.assertTrue(any(x.startswith("abstained:") for x in report["limitations"]))
                audit = report["acceptance_provenance"]
                self.assertEqual(audit["prepared_integrity_token"], prepared["integrity_token"])
                self.assertIn(field, audit["edited_fields"])
                self.assertIsNone(audit["original"]["ai_interpretation"])

    def test_provider_abstention_with_manual_text_is_clinician_entry(self):
        abstain = {"contract_version": "1.0", "status": "abstain", "limitations": ["Image not diagnostic."]}
        prepared = interpret(si.png(), vision_env=ENV, vision_transport=lambda c, r: abstain)["prepared"]
        self.assertEqual(prepared["processing"]["status"], "vision_abstained")
        report = self.accept(prepared, {"ai_interpretation": "Typed by clinician."})
        self.assertEqual(report["provenance"], "clinician_entry")
        self.assertIn("Image not diagnostic.", report["limitations"])

    def test_abstention_without_text_still_cannot_be_accepted(self):
        prepared = interpret(si.png(width=32, height=32), vision_env=ENV)["prepared"]
        with self.assertRaises(ValueError):
            self.accept(prepared, {})

    def test_other_provenance_values_are_unchanged(self):
        prepared = interpret(si.png(), vision_env=ENV, vision_transport=lambda c, r: ok_response())["prepared"]
        self.assertEqual(prepared["processing"]["status"], "vision_interpreted")
        self.assertEqual(self.accept(prepared, {})["provenance"], "ai_image_interpretation")
        routed = prepared_for(si.png())
        self.assertEqual(routed["processing"]["status"], "routed_external")
        self.assertEqual(self.accept(routed, {"official_report": "Device reading."})["provenance"],
                         "device_measurement")
        text = api.prepare_upload("note.txt", "text/plain", b64(b"Synthetic report text."))
        self.assertEqual(self.accept(text, {})["provenance"], "external_record")


if __name__ == "__main__":
    unittest.main()
