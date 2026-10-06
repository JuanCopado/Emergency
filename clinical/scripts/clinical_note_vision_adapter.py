#!/usr/bin/env python3
"""Production-facing adapter for binary clinical document/image interpretation.

This module deliberately contains orchestration, validation and privacy boundaries,
not a diagnostic model. A configured provider receives the binary source only after
explicit file/privacy review and returns a structured proposal that still requires
clinician Accept/Edit/Reject before persistence in the clinical note.

Provider contract (POST JSON):
{
  "contract_version": "1.0",
  "request_id": "...",
  "kind": "ecg|xray|ct|mri|pocus|other_image|pdf_document|...",
  "mime_type": "...",
  "filename": "...",
  "sha256": "...",
  "routed_modules": ["..."],
  "content_base64": "..."
}

Expected response:
{
  "contract_version": "1.0",
  "status": "ok",
  "provider": "...",
  "model": "...",
  "official_report": null,
  "ai_interpretation": "...",
  "findings": "...",
  "impression": "...",
  "limitations": ["..."],
  "confidence": "high|moderate|low|null"
}

No response is accepted into the medical record by this module itself.
"""

import json
import os
import ssl
import urllib.error
import urllib.request
import uuid

CONTRACT_VERSION = "1.0"
DEFAULT_TIMEOUT_SECONDS = 45
ALLOWED_CONFIDENCE = {None, "high", "moderate", "low"}
BINARY_KINDS = {
    "ecg", "xray", "chest_xray", "xray_chest", "musculoskeletal_xray",
    "ct", "ct_head", "ct_body", "mri", "pocus", "ultrasound",
    "blood_gas_image", "skin_wound", "ophthalmology", "other_image",
    "pdf_document",
}


class VisionAdapterError(ValueError):
    pass


def provider_config(env=None):
    env = env or os.environ
    url = str(env.get("CLINICAL_VISION_PROVIDER_URL") or "").strip()
    token = str(env.get("CLINICAL_VISION_PROVIDER_TOKEN") or "").strip()
    timeout_raw = str(env.get("CLINICAL_VISION_TIMEOUT_SECONDS") or DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout = int(timeout_raw)
    except ValueError as exc:
        raise VisionAdapterError("invalid CLINICAL_VISION_TIMEOUT_SECONDS") from exc
    if timeout < 1 or timeout > 180:
        raise VisionAdapterError("CLINICAL_VISION_TIMEOUT_SECONDS must be 1..180")
    return {"url": url, "token": token, "timeout": timeout}


def is_configured(env=None):
    cfg = provider_config(env)
    return bool(cfg["url"])


def _validate_https(url):
    if not url:
        raise VisionAdapterError("clinical vision provider is not configured")
    if not url.lower().startswith("https://"):
        raise VisionAdapterError("clinical vision provider URL must use HTTPS")


def build_request(prepared, content_base64):
    if not isinstance(prepared, dict):
        raise VisionAdapterError("prepared upload is required")
    if prepared.get("processing", {}).get("status") != "routed_external":
        raise VisionAdapterError("vision adapter accepts only binary/routed uploads")
    kind = str(prepared.get("kind") or "").strip().lower()
    if kind not in BINARY_KINDS:
        raise VisionAdapterError("attachment kind is not eligible for binary interpretation")
    if prepared.get("privacy", {}).get("status") == "STOP":
        raise VisionAdapterError("privacy STOP must be resolved before interpretation")
    if not isinstance(content_base64, str) or not content_base64:
        raise VisionAdapterError("content_base64 is required")
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": str(uuid.uuid4()),
        "kind": kind,
        "mime_type": prepared.get("mime_type") or "application/octet-stream",
        "filename": prepared.get("filename") or "upload",
        "sha256": prepared.get("sha256"),
        "routed_modules": list(prepared.get("processing", {}).get("modules") or []),
        "content_base64": content_base64,
    }


def _normalize_response(payload):
    if not isinstance(payload, dict):
        raise VisionAdapterError("vision provider returned a non-object response")
    if payload.get("status") != "ok":
        raise VisionAdapterError("vision provider did not return status=ok")
    if str(payload.get("contract_version") or "") != CONTRACT_VERSION:
        raise VisionAdapterError("vision provider contract version mismatch")
    confidence = payload.get("confidence")
    if confidence not in ALLOWED_CONFIDENCE:
        raise VisionAdapterError("vision provider confidence must be high/moderate/low or null")
    ai_text = str(payload.get("ai_interpretation") or "").strip()
    findings = str(payload.get("findings") or "").strip()
    impression = str(payload.get("impression") or "").strip()
    official = str(payload.get("official_report") or "").strip()
    if not any((ai_text, findings, impression, official)):
        raise VisionAdapterError("vision provider returned no reviewable clinical content")
    limitations = payload.get("limitations") or []
    if not isinstance(limitations, list) or any(not isinstance(x, str) for x in limitations):
        raise VisionAdapterError("vision provider limitations must be a string array")
    return {
        "provider": str(payload.get("provider") or "configured-provider"),
        "model": str(payload.get("model") or "unspecified"),
        "official_report": official or None,
        "ai_interpretation": ai_text or None,
        "findings": findings or None,
        "impression": impression or None,
        "limitations": limitations,
        "confidence": confidence,
    }


def invoke(prepared, content_base64, *, privacy_checked=False,
           burned_in_identifiers_checked=False, env=None, transport=None):
    privacy = prepared.get("privacy", {}) if isinstance(prepared, dict) else {}
    if privacy.get("manual_file_privacy_review_required") and not privacy_checked:
        raise VisionAdapterError("manual file privacy review is required before external interpretation")
    if privacy.get("burned_in_identifier_review_required") and not burned_in_identifiers_checked:
        raise VisionAdapterError("burned-in identifier review is required before external interpretation")

    request_payload = build_request(prepared, content_base64)
    cfg = provider_config(env)
    _validate_https(cfg["url"])

    if transport is not None:
        response_payload = transport(cfg, request_payload)
    else:
        body = json.dumps(request_payload, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if cfg["token"]:
            headers["Authorization"] = "Bearer " + cfg["token"]
        request = urllib.request.Request(cfg["url"], data=body, headers=headers, method="POST")
        context = ssl.create_default_context()
        try:
            with urllib.request.urlopen(request, timeout=cfg["timeout"], context=context) as response:
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise VisionAdapterError("clinical vision provider request failed") from exc
        try:
            response_payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VisionAdapterError("clinical vision provider returned invalid JSON") from exc

    normalized = _normalize_response(response_payload)
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_payload["request_id"],
        "kind": request_payload["kind"],
        "sha256": request_payload["sha256"],
        "routed_modules": request_payload["routed_modules"],
        "review_required": True,
        "persisted": False,
        "result": normalized,
    }
