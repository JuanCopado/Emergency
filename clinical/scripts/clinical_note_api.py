#!/usr/bin/env python3
"""Trusted clinical-note API facade and local HTTP adapter.

Safety properties:
- pseudonymous note contract only;
- direct-identifier privacy checks run before diagnostic analysis/export;
- uploaded originals are never persisted by this adapter;
- text extraction is limited to plain-text-like files;
- binary image/PDF/DICOM uploads are routed but never autonomously interpreted here;
- only clinician-accepted upload results are persisted into the structured note;
- deterministic diagnostic support resets clinician sign-off;
- exports use the central privacy-gated exporter.
"""

import argparse
import base64
import binascii
import hashlib
import json
import mimetypes
import tempfile
import uuid
from copy import deepcopy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from clinical_note_diagnostic_engine import analyze
from clinical_note_exporter import export_docx, export_json, export_pdf
from clinical_note_support import (
    add_report,
    new_note,
    route_attachment,
    scan_privacy,
    validate_for_analysis,
    validate_for_export,
)

try:
    from pediatric_outpatient_alert_engine import evaluate as pediatric_medication_alerts
except Exception:
    pediatric_medication_alerts = None

API_VERSION = "1.0"
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MAX_TEXT_CHARS = 120_000
TEXT_EXTENSIONS = {".txt", ".csv", ".json", ".xml", ".md", ".log", ".tsv"}
TEXT_MIME_TYPES = {
    "text/plain", "text/csv", "application/json", "application/xml",
    "text/xml", "text/markdown", "text/tab-separated-values",
}


def _clean_filename(filename):
    name = Path(str(filename or "upload")).name.strip()
    return name or "upload"


def infer_attachment_kind(filename, mime_type=None, explicit_kind=None):
    if explicit_kind:
        return str(explicit_kind).strip().lower()
    name = _clean_filename(filename).lower()
    mime = str(mime_type or "").lower()
    if any(x in name for x in ("ecg", "ekg", "electrocard")):
        return "ecg"
    if any(x in name for x in ("gasometr", "blood_gas", "abg", "vbg")):
        return "blood_gas"
    if any(x in name for x in ("microbi", "culture", "cultivo", "hemocult")):
        return "microbiology"
    if any(x in name for x in ("laborat", "analit", "analyt", "hemogram", "bioq")):
        return "laboratory_report"
    if any(x in name for x in ("pocus", "ultrasound", "ecografia", "ultrasom")):
        return "pocus"
    if any(x in name for x in ("ct_", "ct-", "tac", "tc_", "tc-", "mri", "rm_")):
        return "ct"
    if any(x in name for x in ("xray", "x-ray", "radiogr", "_rx", "rx_")):
        return "xray"
    if name.endswith(".dcm") or "dicom" in mime:
        return "other_image"
    if name.endswith(".pdf") or mime == "application/pdf":
        return "pdf_document"
    return "other_image"


def _decode_upload(content_base64):
    if not isinstance(content_base64, str) or not content_base64:
        raise ValueError("content_base64 is required")
    try:
        raw = base64.b64decode(content_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("invalid base64 upload") from exc
    if not raw:
        raise ValueError("empty upload")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError(f"upload exceeds {MAX_UPLOAD_BYTES} bytes")
    return raw


def _extract_text(raw, filename, mime_type):
    suffix = Path(filename).suffix.lower()
    mime = str(mime_type or "").split(";", 1)[0].strip().lower()
    if suffix not in TEXT_EXTENSIONS and mime not in TEXT_MIME_TYPES and not mime.startswith("text/"):
        return None
    if b"\x00" in raw[:4096]:
        return None
    text = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        return None
    return text[:MAX_TEXT_CHARS]


def _privacy_for_text(text):
    probe = new_note()
    probe["history"]["present_illness"] = text
    findings = scan_privacy(probe)
    return findings


def prepare_upload(filename, mime_type, content_base64, explicit_kind=None):
    filename = _clean_filename(filename)
    raw = _decode_upload(content_base64)
    kind = infer_attachment_kind(filename, mime_type, explicit_kind)
    route = route_attachment(kind)
    extracted_text = _extract_text(raw, filename, mime_type)
    digest = hashlib.sha256(raw).hexdigest()
    privacy_probe_text = filename + ("\n" + extracted_text if extracted_text else "")
    privacy_findings = _privacy_for_text(privacy_probe_text)
    privacy_stop = any(x.get("severity") == "STOP" for x in privacy_findings)
    binary_requires_review = extracted_text is None
    burned_in_required = binary_requires_review and kind in {
        "ecg", "xray", "chest_xray", "musculoskeletal_xray", "ct", "mri",
        "pocus", "ultrasound", "other_image", "pdf_document",
    }
    if privacy_stop:
        privacy_status = "STOP"
    elif binary_requires_review:
        privacy_status = "REVIEW_REQUIRED"
    else:
        privacy_status = "PASS"
    processing_status = "text_extracted" if extracted_text is not None else "routed_external"
    return {
        "api_version": API_VERSION,
        "upload_id": str(uuid.uuid4()),
        "filename": filename,
        "mime_type": mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream",
        "size_bytes": len(raw),
        "sha256": digest,
        "kind": kind,
        "route": route,
        "privacy": {
            "status": privacy_status,
            "findings": privacy_findings,
            "manual_file_privacy_review_required": binary_requires_review,
            "burned_in_identifier_review_required": burned_in_required,
        },
        "extracted": {
            "official_report": extracted_text,
            "ai_interpretation": None,
        },
        "processing": {
            "status": processing_status,
            "message": (
                "Text extracted for clinician review; no autonomous clinical interpretation performed."
                if extracted_text is not None
                else "Binary source routed to the central clinical module. Interpretation must be supplied by the trusted module and reviewed by a clinician."
            ),
            "modules": route["modules"],
        },
        "original_retained": False,
    }


def _accepted_provenance(prepared, ai_interpretation):
    if ai_interpretation:
        if prepared.get("processing", {}).get("status") == "text_extracted":
            return "ai_document_extraction"
        return "ai_image_interpretation"
    if prepared.get("processing", {}).get("status") == "text_extracted":
        return "external_record"
    return "device_measurement"


def accept_prepared_upload(note, prepared, clinician_edit=None,
                           privacy_checked=False, burned_in_identifiers_checked=False):
    if not isinstance(note, dict) or not isinstance(prepared, dict):
        raise ValueError("note and prepared upload are required")
    privacy = prepared.get("privacy", {})
    if privacy.get("status") == "STOP":
        raise ValueError("upload privacy STOP must be resolved before acceptance")
    if privacy.get("manual_file_privacy_review_required") and not privacy_checked:
        raise ValueError("manual file privacy review is required before acceptance")
    if privacy.get("burned_in_identifier_review_required") and not burned_in_identifiers_checked:
        raise ValueError("burned-in identifier review is required before acceptance")

    edit = clinician_edit or {}
    official = edit.get("official_report", prepared.get("extracted", {}).get("official_report"))
    ai_text = edit.get("ai_interpretation", prepared.get("extracted", {}).get("ai_interpretation"))
    if not (str(official or "").strip() or str(ai_text or "").strip()):
        raise ValueError("accepted upload must contain reviewed extracted/official or interpreted text")

    candidate = deepcopy(note)
    source_reference = "sha256:" + str(prepared.get("sha256", ""))
    report = add_report(
        candidate,
        prepared.get("kind") or "other_image",
        _accepted_provenance(prepared, ai_text),
        official_report=official,
        ai_interpretation=ai_text,
        findings=edit.get("findings"),
        impression=edit.get("impression"),
        limitations=edit.get("limitations") or [],
        source_reference=source_reference,
        time_label=edit.get("time_label"),
        privacy_checked=privacy_checked or privacy.get("status") == "PASS",
        burned_in_identifiers_checked=burned_in_identifiers_checked,
    )
    candidate.setdefault("timeline", []).append({
        "time_label": edit.get("time_label") or "MCDT",
        "event": f"Accepted {prepared.get('kind') or 'attachment'} result",
        "source": source_reference,
    })
    candidate.setdefault("clinician_validation", {})["reviewed"] = False
    candidate["clinician_validation"]["changes_made"] = "Accepted MCDT result added; clinician validation required again."

    findings = validate_for_analysis(candidate)
    stops = [x for x in findings if x.get("severity") == "STOP"]
    if stops:
        raise ValueError("accepted result fails note privacy/analysis gate: " + " | ".join(x["message"] for x in stops))
    return {"note": candidate, "report": report, "findings": findings}


def run_diagnostic_support(note):
    result = analyze(note, apply_to_note=True)
    assessment = result.get("assessment") or {}
    treatments = assessment.get("treatment_suggestions") or []
    medication_gate = {
        "status": "REVIEW_REQUIRED" if treatments else "NOT_APPLICABLE",
        "actionable": False if treatments else True,
        "required_module": "medication-selection-safety" if treatments else None,
        "message": (
            "Treatment suggestions are diagnostic-support output only. Medication choice/dose must pass the central medication-selection-safety pathway before being displayed as actionable."
            if treatments else "No treatment suggestion requires medication safety review."
        ),
    }
    result["medication_safety_gate"] = medication_gate
    return result


def medication_preflight(payload):
    mode = str(payload.get("mode") or "").strip().lower()
    if mode == "pediatric_outpatient_regimen":
        if pediatric_medication_alerts is None:
            raise ValueError("pediatric medication safety engine unavailable")
        return pediatric_medication_alerts(
            payload.get("regimen_id"),
            payload.get("patient") or {},
            active_medications=payload.get("active_medications"),
            product=payload.get("product"),
        )
    return {
        "blocked": False,
        "prescription_status": "REVIEW_REQUIRED",
        "highest_severity": "ALERT",
        "alerts": [{
            "severity": "ALERT",
            "code": "CENTRAL_MEDICATION_REVIEW_REQUIRED",
            "message": "No structured medication regimen was supplied for deterministic interaction/dose checking.",
            "action": "Route the proposed drug/regimen through medication-selection-safety and the relevant central dosing module before making it actionable.",
        }],
    }


def export_note_bytes(note, fmt):
    fmt = str(fmt or "").lower()
    gate = validate_for_export(note)
    if gate["blocked"]:
        raise ValueError("export blocked: " + " | ".join(
            x["message"] for x in gate["findings"] if x.get("severity") == "STOP"
        ))
    suffix = {"docx": ".docx", "pdf": ".pdf", "json": ".json"}.get(fmt)
    if not suffix:
        raise ValueError("format must be docx, pdf or json")
    with tempfile.TemporaryDirectory() as directory:
        out = Path(directory) / ("clinical-note" + suffix)
        if fmt == "docx":
            export_docx(note, out)
        elif fmt == "pdf":
            export_pdf(note, out)
        else:
            export_json(note, out)
        return out.read_bytes()


def dispatch(path, payload):
    if path == "/api/clinical-note/new":
        return HTTPStatus.OK, new_note(
            age_years=payload.get("age_years"),
            age_months=payload.get("age_months"),
            sex=payload.get("sex", "unknown"),
            language=payload.get("language", "pt-PT"),
            privacy_mode=payload.get("privacy_mode", "clinical_pseudonymized"),
        )
    if path == "/api/clinical-note/preflight":
        note = payload.get("note") or {}
        findings = validate_for_analysis(note)
        return HTTPStatus.OK, {
            "blocked": any(x.get("severity") == "STOP" for x in findings),
            "findings": findings,
        }
    if path == "/api/clinical-note/upload/prepare":
        return HTTPStatus.OK, prepare_upload(
            payload.get("filename"),
            payload.get("mime_type"),
            payload.get("content_base64"),
            payload.get("explicit_kind"),
        )
    if path == "/api/clinical-note/upload/accept":
        return HTTPStatus.OK, accept_prepared_upload(
            payload.get("note") or {},
            payload.get("prepared") or {},
            clinician_edit=payload.get("clinician_edit") or {},
            privacy_checked=bool(payload.get("privacy_checked")),
            burned_in_identifiers_checked=bool(payload.get("burned_in_identifiers_checked")),
        )
    if path == "/api/clinical-note/analyze":
        return HTTPStatus.OK, run_diagnostic_support(payload.get("note") or {})
    if path == "/api/clinical-note/medication/preflight":
        return HTTPStatus.OK, medication_preflight(payload)
    if path == "/api/clinical-note/export":
        fmt = payload.get("format")
        data = export_note_bytes(payload.get("note") or {}, fmt)
        ext = {"docx": "docx", "pdf": "pdf", "json": "json"}[str(fmt).lower()]
        mime = {
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
            "json": "application/json",
        }[ext]
        return HTTPStatus.OK, {
            "filename": f"clinical-note.{ext}",
            "mime_type": mime,
            "content_base64": base64.b64encode(data).decode("ascii"),
        }
    return HTTPStatus.NOT_FOUND, {"error": "unknown endpoint"}


class ClinicalNoteHandler(BaseHTTPRequestHandler):
    server_version = "EmergencyClinicalNoteAPI/1.0"

    def _send(self, status, body):
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/api/clinical-note/health":
            self._send(HTTPStatus.OK, {"status": "ok", "api_version": API_VERSION})
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > (MAX_UPLOAD_BYTES * 2 + 1_000_000):
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            status, body = dispatch(self.path, payload)
            self._send(status, body)
        except ValueError as exc:
            self._send(HTTPStatus.UNPROCESSABLE_ENTITY, {"error": str(exc)})
        except json.JSONDecodeError:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
        except Exception as exc:
            self._send(HTTPStatus.INTERNAL_SERVER_ERROR, {
                "error": "clinical-note backend failure",
                "detail": str(exc),
            })

    def log_message(self, fmt, *args):
        # Do not log request bodies or clinical payloads.
        super().log_message(fmt, *args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"} and not args.allow_network:
        raise SystemExit("Refusing non-loopback bind without --allow-network")
    server = ThreadingHTTPServer((args.host, args.port), ClinicalNoteHandler)
    print(f"Clinical-note API listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
