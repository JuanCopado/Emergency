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
import hmac
import json
import mimetypes
import os
import secrets
import tempfile
import uuid
from datetime import datetime, timezone
from threading import RLock
from copy import deepcopy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from clinical_note_diagnostic_engine import analyze
from clinical_note_exporter import export_docx, export_json, export_pdf
from clinical_note_vision_adapter import invoke as invoke_clinical_vision, is_configured as clinical_vision_is_configured
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
PREPARED_HMAC_KEY = (os.environ.get("CLINICAL_NOTE_PREPARED_HMAC_KEY") or "").encode("utf-8") or secrets.token_bytes(32)
AUDIT_HMAC_KEY = (os.environ.get("CLINICAL_NOTE_AUDIT_HMAC_KEY") or "").encode("utf-8") or secrets.token_bytes(32)
AUDIT_DIR = os.environ.get("CLINICAL_NOTE_AUDIT_DIR")
BUILD_SHA = os.environ.get("CLINICAL_NOTE_BUILD_SHA") or "unversioned"
AUDIT_LOCK = RLock()
AUDIT_MEMORY = {}
CLINICAL_ROOT = Path(__file__).parents[1]
DIAGNOSTIC_RULES_PATH = CLINICAL_ROOT / "qa" / "clinical-note-diagnostic-rules.json"
TEXT_MIME_TYPES = {
    "text/plain", "text/csv", "application/json", "application/xml",
    "text/xml", "text/markdown", "text/tab-separated-values",
}



def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_encounter_id(note_or_id):
    if isinstance(note_or_id, dict):
        encounter_id = str((note_or_id.get("encounter") or {}).get("encounter_id") or "")
    else:
        encounter_id = str(note_or_id or "")
    encounter_id = encounter_id.strip()
    if len(encounter_id) < 8 or len(encounter_id) > 128:
        raise ValueError("valid pseudonymous encounter_id is required for audit")
    if any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:" for ch in encounter_id):
        raise ValueError("encounter_id contains unsupported characters")
    return encounter_id


def _rules_digest():
    try:
        return hashlib.sha256(DIAGNOSTIC_RULES_PATH.read_bytes()).hexdigest()
    except OSError:
        return None


def diagnostic_provenance(assessment=None):
    modules = set()
    if isinstance(assessment, dict):
        for key in ("likely_diagnoses", "differential_diagnoses", "must_not_miss"):
            for item in assessment.get(key) or []:
                modules.update(str(x) for x in (item.get("source_modules") or []) if str(x).strip())
        for key in ("suggested_tests", "treatment_suggestions", "disposition", "reassessment"):
            for item in assessment.get(key) or []:
                modules.update(str(x) for x in (item.get("source_modules") or []) if str(x).strip())
    return {
        "api_version": API_VERSION,
        "build_sha": BUILD_SHA,
        "diagnostic_rules_sha256": _rules_digest(),
        "source_modules": sorted(modules),
        "generated_at": _utc_now(),
    }


def _audit_path(encounter_id):
    if not AUDIT_DIR:
        return None
    directory = Path(AUDIT_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / (hashlib.sha256(encounter_id.encode("utf-8")).hexdigest() + ".jsonl")


def _audit_payload(event):
    payload = dict(event)
    payload.pop("event_hmac", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _audit_load(encounter_id):
    encounter_id = _safe_encounter_id(encounter_id)
    if encounter_id in AUDIT_MEMORY:
        return deepcopy(AUDIT_MEMORY[encounter_id])
    events = []
    path = _audit_path(encounter_id)
    if path and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    AUDIT_MEMORY[encounter_id] = events
    return deepcopy(events)


def verify_audit_chain(events):
    previous = "GENESIS"
    for index, event in enumerate(events):
        if event.get("sequence") != index + 1:
            return False
        if event.get("previous_hmac") != previous:
            return False
        token = str(event.get("event_hmac") or "")
        expected = hmac.new(AUDIT_HMAC_KEY, _audit_payload(event), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(token, expected):
            return False
        previous = token
    return True


def append_audit_event(note_or_id, action, target, detail=None, metadata=None):
    encounter_id = _safe_encounter_id(note_or_id)
    action = str(action or "").strip()[:80]
    target = str(target or "").strip()[:160]
    if not action or not target:
        raise ValueError("audit action and target are required")
    detail = str(detail or "").strip()[:500]
    metadata = metadata if isinstance(metadata, dict) else {}
    safe_metadata = {
        str(k)[:80]: (v if isinstance(v, (str, int, float, bool)) or v is None else str(v)[:240])
        for k, v in metadata.items()
    }
    with AUDIT_LOCK:
        events = _audit_load(encounter_id)
        if events and not verify_audit_chain(events):
            raise ValueError("audit chain integrity check failed")
        previous = events[-1]["event_hmac"] if events else "GENESIS"
        event = {
            "sequence": len(events) + 1,
            "event_id": str(uuid.uuid4()),
            "encounter_id": encounter_id,
            "timestamp": _utc_now(),
            "action": action,
            "target": target,
            "detail": detail,
            "metadata": safe_metadata,
            "previous_hmac": previous,
        }
        event["event_hmac"] = hmac.new(
            AUDIT_HMAC_KEY, _audit_payload(event), hashlib.sha256
        ).hexdigest()
        events.append(event)
        AUDIT_MEMORY[encounter_id] = deepcopy(events)
        path = _audit_path(encounter_id)
        if path:
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        return deepcopy(event)


def read_audit_trail(note_or_id):
    encounter_id = _safe_encounter_id(note_or_id)
    events = _audit_load(encounter_id)
    return {
        "encounter_id": encounter_id,
        "events": events,
        "chain_valid": verify_audit_chain(events),
        "storage": "persistent_jsonl" if AUDIT_DIR else "process_memory",
    }



def _prepared_signature_payload(prepared):
    payload = deepcopy(prepared)
    payload.pop("integrity_token", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign_prepared(prepared):
    signed = deepcopy(prepared)
    signed["integrity_token"] = hmac.new(
        PREPARED_HMAC_KEY, _prepared_signature_payload(signed), hashlib.sha256
    ).hexdigest()
    return signed


def _verify_prepared(prepared):
    if not isinstance(prepared, dict):
        raise ValueError("prepared upload is required")
    token = str(prepared.get("integrity_token") or "")
    if not token:
        raise ValueError("prepared upload integrity token is missing")
    expected = hmac.new(
        PREPARED_HMAC_KEY, _prepared_signature_payload(prepared), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(token, expected):
        raise ValueError("prepared upload integrity check failed")



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
    return _sign_prepared({
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
    })



def interpret_prepared_upload(prepared, content_base64, privacy_checked=False,
                              burned_in_identifiers_checked=False,
                              vision_transport=None, vision_env=None):
    """Invoke the configured binary interpreter without persisting its proposal."""
    _verify_prepared(prepared)
    raw = _decode_upload(content_base64)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != str(prepared.get("sha256") or ""):
        raise ValueError("upload content no longer matches the prepared sha256")
    if int(prepared.get("size_bytes") or 0) != len(raw):
        raise ValueError("upload content size no longer matches the prepared upload")

    result = invoke_clinical_vision(
        prepared,
        content_base64,
        privacy_checked=privacy_checked,
        burned_in_identifiers_checked=burned_in_identifiers_checked,
        env=vision_env,
        transport=vision_transport,
    )
    proposal = result.get("result") or {}
    privacy_text = "\n".join(
        str(proposal.get(key) or "")
        for key in ("official_report", "ai_interpretation", "findings", "impression")
    )
    privacy_findings = _privacy_for_text(privacy_text)
    if any(x.get("severity") == "STOP" for x in privacy_findings):
        raise ValueError("vision interpretation output contains possible direct identifiers")

    updated = deepcopy(prepared)
    updated["extracted"] = {
        "official_report": proposal.get("official_report"),
        "ai_interpretation": proposal.get("ai_interpretation"),
    }
    updated["processing"] = {
        **(updated.get("processing") or {}),
        "status": "vision_interpreted",
        "message": "Binary source interpreted by configured provider; clinician review and explicit acceptance remain required.",
        "provider": proposal.get("provider"),
        "model": proposal.get("model"),
        "confidence": proposal.get("confidence"),
        "findings": proposal.get("findings"),
        "impression": proposal.get("impression"),
        "limitations": proposal.get("limitations") or [],
    }
    updated["privacy"] = {
        **(updated.get("privacy") or {}),
        "status": "PASS",
        "manual_file_privacy_review_required": False,
        "burned_in_identifier_review_required": False,
        "provider_output_findings": privacy_findings,
    }
    updated = _sign_prepared(updated)
    return {
        "prepared": updated,
        "review_required": True,
        "persisted": False,
        "routed_modules": result.get("routed_modules") or [],
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
    _verify_prepared(prepared)
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
    result["diagnostic_provenance"] = diagnostic_provenance(assessment)
    try:
        append_audit_event(
            note, "DIAGNOSTIC_ANALYSIS", "assessment",
            detail="Deterministic diagnostic support executed.",
            metadata={
                "build_sha": result["diagnostic_provenance"]["build_sha"],
                "rules_sha256": result["diagnostic_provenance"]["diagnostic_rules_sha256"],
                "source_module_count": len(result["diagnostic_provenance"]["source_modules"]),
            },
        )
    except ValueError:
        pass
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
    if path == "/api/clinical-note/upload/interpret":
        return HTTPStatus.OK, interpret_prepared_upload(
            payload.get("prepared") or {},
            payload.get("content_base64"),
            privacy_checked=bool(payload.get("privacy_checked")),
            burned_in_identifiers_checked=bool(payload.get("burned_in_identifiers_checked")),
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
    if path == "/api/clinical-note/audit/read":
        return HTTPStatus.OK, read_audit_trail(payload.get("note") or payload.get("encounter_id"))
    if path == "/api/clinical-note/audit/append":
        return HTTPStatus.OK, {
            "event": append_audit_event(
                payload.get("note") or payload.get("encounter_id"),
                payload.get("action"),
                payload.get("target"),
                detail=payload.get("detail"),
                metadata=payload.get("metadata"),
            )
        }
    if path == "/api/clinical-note/medication/preflight":
        return HTTPStatus.OK, medication_preflight(payload)
    if path == "/api/clinical-note/export":
        fmt = payload.get("format")
        note = payload.get("note") or {}
        data = export_note_bytes(note, fmt)
        audit_event = append_audit_event(
            note, "EXPORT", str(fmt or "unknown"),
            detail="Clinical note export completed.",
            metadata={"build_sha": BUILD_SHA, "rules_sha256": _rules_digest()},
        )
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
            "audit_event": audit_event,
            "provenance": diagnostic_provenance((note.get("assessment") or {})),
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
