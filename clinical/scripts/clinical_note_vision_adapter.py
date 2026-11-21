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
  "filename": "clinical-source.<ext>",
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

import base64
import binascii
import json
import os
import re
import ssl
import urllib.error
import urllib.request
import uuid
from clinical_note_support import scan_privacy
import image_upload_guard

CONTRACT_VERSION = "1.0"
DEFAULT_TIMEOUT_SECONDS = 45
MAX_PROVIDER_RESPONSE_BYTES = 2 * 1024 * 1024
ALLOWED_CONFIDENCE = {None, "high", "moderate", "low"}
BINARY_KINDS = {
    "ecg", "xray", "chest_xray", "xray_chest", "musculoskeletal_xray",
    "ct", "ct_head", "ct_body", "mri", "pocus", "ultrasound",
    "blood_gas_image", "skin_wound", "ophthalmology", "other_image",
}


class VisionAdapterError(ValueError):
    pass


class VisionProviderResponseError(VisionAdapterError):
    """The configured provider returned an unusable answer; the note is untouched."""


# M10: rules already stated in modules/image-modalities.md#skin-wound-image, enforced on output.
SKIN_WOUND_FIXED_LIMITATIONS = (
    "Photograph only: warmth, tenderness, fluctuance, crepitus, depth and pain out of "
    "proportion are not assessable.",
    "Lighting, white balance and skin tone alter apparent colour; diagnostic performance of "
    "this workflow is not established. Does not exclude necrotizing infection, "
    "malignancy or any other diagnosis; examine in person when concerned.",
)
_REASSURANCE = re.compile(
    r"\b(benign|benigno|benigna|ruled out|excluded|reassuring|tranquilizador|descarta\w*|"
    r"exclu[ií]d[oa]|no (?:signs? of |evidence of )?(?:infection|necrosis|malignan\w*)|"
    r"sin (?:signos de )?(?:infecci[oó]n|necrosis|malignidad)|"
    r"sem (?:sinais de )?(?:infe[cç][aã]o|necrose|malignidade)|"
    r"not (?:an? )?(?:infected|necrotizing|malignant)|normal skin|piel normal|pele normal|"
    r"safe to (?:observe|discharge)|no urgent|sin riesgo|sem risco|"
    r"no further (?:assessment|evaluation|review) (?:is )?(?:needed|required)|"
    r"no (?:requiere|necesita) (?:m[aá]s |otra )?(?:valoraci[oó]n|evaluaci[oó]n)|"
    r"n[aã]o (?:necessita de |precisa de |requer )(?:mais |nova )?avalia[cç][aã]o)\b", re.IGNORECASE)


def _skin_wound_guard(normalized):
    """Fail-safe post-processing for skin_wound output (no clinical judgement added).

    - reassurance wording is flagged and surfaced in limitations (regex ceiling: also
      matches negated forms such as 'cannot be excluded'; over-flagging is intended);
    - provider confidence is withheld: no diagnostic performance has been established.
    """
    text = " ".join(str(normalized.get(k) or "") for k in
                    ("ai_interpretation", "findings", "impression"))
    flags = list(normalized.get("safety_flags") or [])
    limitations = list(normalized.get("limitations") or [])
    if _REASSURANCE.search(text):
        flags.append("reassurance_language")
        normalized["abstained"] = True
        for field in ("ai_interpretation", "findings", "impression"):
            normalized[field] = None
        limitations.append("Flagged: output contains reassurance/exclusion wording that a "
                           "photograph cannot support. Disregard it and examine in person.")
    if normalized.get("confidence") is not None:
        normalized["provider_confidence"] = normalized["confidence"]
        normalized["confidence"] = None
        flags.append("confidence_withheld")
    for fixed in SKIN_WOUND_FIXED_LIMITATIONS:
        if fixed not in limitations:
            limitations.append(fixed)
    normalized["limitations"] = limitations
    normalized["safety_flags"] = flags
    return normalized


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
    if len(content_base64) > 4 * ((image_upload_guard.MAX_TRANSFER_BYTES + 2) // 3):
        raise VisionAdapterError("vision raster exceeds transport limit")
    try:
        raw = base64.b64decode(content_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise VisionAdapterError("invalid raster encoding") from exc
    media = image_upload_guard.inspect_media(raw, prepared.get("filename"), prepared.get("mime_type"))
    if media["format"] not in image_upload_guard.IMAGE_FORMATS or media["status"] == "unsuitable":
        raise VisionAdapterError("only inspected, reviewable still rasters are eligible for transport")
    clean = image_upload_guard.strip_metadata(raw, media["format"])
    if len(clean) > image_upload_guard.MAX_TRANSFER_BYTES:
        raise VisionAdapterError("normalized raster exceeds transport limit")
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": str(uuid.uuid4()),
        "kind": kind,
        "mime_type": "image/png",
        "filename": "clinical-source.png",
        "routed_modules": list(prepared.get("processing", {}).get("modules") or []),
        "content_base64": base64.b64encode(clean).decode("ascii"),
    }


def _normalize_response(payload):
    if not isinstance(payload, dict):
        raise VisionProviderResponseError("vision provider returned a non-object response")
    if payload.get("contract_version") != CONTRACT_VERSION:
        raise VisionProviderResponseError("vision provider contract version mismatch")
    for field in ("ai_interpretation", "findings", "impression", "official_report", "provider", "model"):
        value = payload.get(field)
        if value is not None and not isinstance(value, str):
            raise VisionProviderResponseError(f"vision provider {field} must be a string or null")
    for field in ("provider", "model"):
        label = payload.get(field)
        if label is not None and (not label.strip() or len(label) > 128 or not label.isprintable()):
            raise VisionProviderResponseError(f"vision provider {field} must be a short printable label")
    if payload.get("status") == "abstain":
        # M10-F05: an explicit abstention (e.g. non-diagnostic image) is a valid outcome,
        # distinct from a provider failure. A reason is mandatory; no clinical text allowed.
        if payload.get("confidence") is not None:
            raise VisionProviderResponseError("vision provider abstention must not carry confidence")
        reasons = payload.get("limitations")
        if (not isinstance(reasons, list) or not reasons
                or any(not isinstance(x, str) or not x.strip() for x in reasons)):
            raise VisionProviderResponseError("vision provider abstention requires a limitations reason")
        if any((payload.get(k) or "").strip() for k in
               ("ai_interpretation", "findings", "impression", "official_report")
               if isinstance(payload.get(k), str)):
            raise VisionProviderResponseError("vision provider abstention must not carry clinical content")
        return {"provider": str(payload.get("provider") or "configured-provider"),
                "model": str(payload.get("model") or "unspecified"),
                "official_report": None, "ai_interpretation": None, "findings": None,
                "impression": None, "limitations": reasons, "confidence": None,
                "abstained": True, "safety_flags": ["provider_abstained"]}
    if payload.get("status") != "ok":
        raise VisionProviderResponseError("vision provider did not return status=ok")
    confidence = payload.get("confidence")
    if (confidence is not None and not isinstance(confidence, str)) or confidence not in ALLOWED_CONFIDENCE:
        raise VisionProviderResponseError("vision provider confidence must be high/moderate/low or null")
    ai_text = (payload.get("ai_interpretation") or "").strip()
    findings = (payload.get("findings") or "").strip()
    impression = (payload.get("impression") or "").strip()
    official = (payload.get("official_report") or "").strip()
    if not any((ai_text, findings, impression, official)):
        raise VisionProviderResponseError("vision provider returned no reviewable clinical content")
    limitations = payload.get("limitations", [])
    if not isinstance(limitations, list) or any(not isinstance(x, str) for x in limitations):
        raise VisionProviderResponseError("vision provider limitations must be a string array")
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


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise VisionAdapterError("clinical vision provider redirects are not allowed")


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
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=context),
            _NoRedirect(),
        )
        try:
            with opener.open(request, timeout=cfg["timeout"]) as response:
                raw = response.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
        except VisionAdapterError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise VisionAdapterError("clinical vision provider request failed") from exc
        if len(raw) > MAX_PROVIDER_RESPONSE_BYTES:
            raise VisionProviderResponseError("clinical vision provider response exceeds limit")
        try:
            response_payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VisionProviderResponseError("clinical vision provider returned invalid JSON") from exc

    normalized = _normalize_response(response_payload)
    if any(item.get("severity") == "STOP" for item in scan_privacy(normalized)):
        raise VisionProviderResponseError("vision interpretation output contains possible direct identifiers")
    if request_payload["kind"] == "skin_wound" and not normalized.get("abstained"):
        normalized = _skin_wound_guard(normalized)
    if normalized.get("official_report"):
        raise VisionProviderResponseError(
            "vision provider must not label generated image interpretation as an official report"
        )
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_payload["request_id"],
        "kind": request_payload["kind"],
        "sha256": prepared.get("sha256"),
        "routed_modules": request_payload["routed_modules"],
        "review_required": True,
        "persisted": False,
        "result": normalized,
    }
