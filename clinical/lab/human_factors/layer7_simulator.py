"""Deterministic SIMULATOR of the four Layer 7 triggers (T7-01..T7-04) for the experimental arm B.

It is a laboratory instrument, not the product: it decides ONLY from objective technical descriptors of a synthetic file
(declared flow, whether a modality was declared, the declared kind, the container signature kind, whether the container parsed,
and the declared MIME/extension). It has no access to pixels, EXIF, file names or DICOM absence and cannot read files.
Messages are the exact approved texts of the inactive contract (DEC-CLIN-R15-01); no text is generated here.
Every result is labelled simulated. Using it with professionals requires independent audit and agreement with the approved protocol.
"""
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[2] / "references" / "modality-abstention-layer7.contract.proposed.json"
_SPEC = json.loads(CONTRACT.read_text(encoding="utf-8"))
MESSAGE_TEXTS = _SPEC["x-message-texts"]

FLOWS = ("modality_entry", "classic_upload", "document_legacy_bridge")
SIGNATURE_KINDS = ("jpeg", "png", "webp", "pdf", "dicom", "text", "audio", "binary", "unknown")
# Experimental assumption mirroring the prototype's accepted formats (r51Prototype.ts); NOT a clinical rule.
IMAGES = ("jpeg", "png", "webp")
MODALITY_FORMATS = {
    "skin_wound": IMAGES,
    "ecg": IMAGES + ("pdf",),
    "xray": IMAGES + ("pdf", "dicom"),
    "pocus": IMAGES + ("pdf", "dicom"),
    "document": IMAGES + ("pdf", "text"),
}
CONTRACT_REGISTRY = tuple(MODALITY_FORMATS)
GLOBAL_SUPPORTED = tuple(sorted({f for formats in MODALITY_FORMATS.values() for f in formats}))
DESCRIPTOR_FIELDS = {"flow", "modality_declared", "declared_kind", "signature_kind", "container_parse_ok", "declared_mime_type", "declared_extension"}
PRECEDENCE = ("T7-01", "T7-02", "T7-03", "T7-04")   # simulation assumption: selection gate first, then technical integrity, then compatibility


def validate_descriptor(descriptor):
    if not isinstance(descriptor, dict) or set(descriptor) != DESCRIPTOR_FIELDS:
        raise ValueError(f"descriptor fields must be exactly {sorted(DESCRIPTOR_FIELDS)}")
    if descriptor["flow"] not in FLOWS:
        raise ValueError("unknown flow")
    if not isinstance(descriptor["modality_declared"], bool) or not isinstance(descriptor["container_parse_ok"], bool):
        raise ValueError("modality_declared and container_parse_ok must be booleans")
    if descriptor["declared_kind"] is not None and not isinstance(descriptor["declared_kind"], str):
        raise ValueError("declared_kind must be a string or null")
    if descriptor["signature_kind"] not in SIGNATURE_KINDS:
        raise ValueError("unknown signature kind")
    for field in ("declared_mime_type", "declared_extension"):
        if descriptor[field] is not None and not isinstance(descriptor[field], str):
            raise ValueError(f"{field} must be a string or null")
    if descriptor["flow"] == "document_legacy_bridge" and descriptor["declared_kind"] is not None:
        raise ValueError("the document legacy bridge carries no kind")
    if not descriptor["modality_declared"] and descriptor["declared_kind"] is not None:
        raise ValueError("an undeclared modality carries no kind")
    return descriptor


def _base(descriptor):
    return {"contract_version": "layer7-0.2-proposed", "flow": descriptor["flow"], "modality_declared": descriptor["modality_declared"],
            "declared_kind": descriptor["declared_kind"], "provenance": "deterministic_rule"}


def _abstention(descriptor, trigger, message, sources):
    result = dict(_base(descriptor), decision="abstain", trigger_id=trigger, message_id=message, send_allowed=False,
                  evidence={"sources": sources})
    return result


def evaluate(descriptor):
    """Returns the contract document for the descriptor, plus the approved texts when it abstains. Always simulated."""
    validate_descriptor(descriptor)
    flow, kind = descriptor["flow"], descriptor["declared_kind"]
    entry = flow == "modality_entry"
    document = dict(_base(descriptor), decision="none")
    if entry and not descriptor["modality_declared"]:
        document = _abstention(descriptor, "T7-01_UNDECLARED_MODALITY", "MSG_T7_A", ["declared_modality_absent"])
    elif entry and kind not in CONTRACT_REGISTRY:
        document = _abstention(descriptor, "T7-02_UNKNOWN_CONTRACT", "MSG_T7_A", ["declared_kind_not_in_contract_registry"])
    elif not descriptor["container_parse_ok"]:
        document = _abstention(descriptor, "T7-03_CORRUPT_UNPROCESSABLE", "MSG_T7_C", ["container_parse_error"])
    elif descriptor["signature_kind"] not in GLOBAL_SUPPORTED:
        document = _abstention(descriptor, "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_D", ["container_format_unsupported"])
    elif kind in MODALITY_FORMATS and descriptor["signature_kind"] not in MODALITY_FORMATS[kind] and entry:
        document = _abstention(descriptor, "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_B",
                               ["container_signature", "declared_mime_type" if descriptor["declared_mime_type"] else "declared_extension"])
    out = {"simulated": True, "simulator": "layer7-simulator-0.1", "document": document}
    if document["decision"] == "abstain":
        out["message_texts"] = MESSAGE_TEXTS[document["message_id"]]
    return out
