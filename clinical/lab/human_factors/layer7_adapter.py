"""Layer 7 ADAPTER for the experimental arm B on the REAL app. LABORATORY ONLY: never imported by the product, no network, no provider.

The real app has no Layer 7 UI, so the lab runner asks this module, for every /upload/prepare request the app is about to send, whether
the simulated Layer 7 (R22 harness, exact DEC-CLIN-R15-01 texts from the inactive contract) abstains. It adds NO rule: the decision comes
from layer7_simulator.evaluate; the descriptor uses only closed technical fields (never pixels, EXIF, file name or model output).
Arm A never calls it. A technical abstention has no force-send path: `force_send_available` is always False.
Whether the app UI could even reach the case is reported by `reachable_in_real_prototype_ui`: with the R5-1 flag ON the file input does
not exist until a modality is chosen, so T7-01 (no modality) cannot be produced by the real B interface (a finding, see R27 report).
"""
import base64
import binascii
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import file_probe  # noqa: E402
import layer7_harness as harness  # noqa: E402

MODE = "SIMULATED_LAB_HARNESS_ONLY"
EXTENSION_MIME = file_probe.SUFFIX_MIME
UI_MODALITIES = ("skin_wound", "ecg", "xray", "pocus", "document")      # R5-1 prototype modalities


def descriptor_for(body, ui_modality):
    """Closed technical descriptor from the prepare request body and the modality the UI had selected (None = none)."""
    try:
        data = base64.b64decode(body.get("content_base64") or "", validate=True)
    except (binascii.Error, ValueError):
        data = b""
    name = str(body.get("filename") or "")
    suffix = Path(name).suffix.lower()
    kind = file_probe.signature_kind(data)
    declared = body.get("explicit_kind")
    document = ui_modality == "document"
    flow = "document_legacy_bridge" if document else "modality_entry"
    declared_kind = None if document or ui_modality is None else (declared if isinstance(declared, str) else ui_modality)
    return {"flow": flow, "modality_declared": ui_modality is not None and declared_kind is not None, "declared_kind": declared_kind,
            "signature_kind": kind, "container_parse_ok": file_probe.container_parses(data, kind),
            "declared_mime_type": body.get("mime_type") or EXTENSION_MIME.get(suffix), "declared_extension": suffix or None}


def evaluate_upload(body, ui_modality, language="es", variant=None):
    if ui_modality is not None and ui_modality not in UI_MODALITIES:
        raise ValueError("unknown UI modality")
    descriptor = descriptor_for(body, ui_modality)
    # Document through the legacy bridge has modality_declared False by design (kind=null); the simulator accepts that flow.
    if descriptor["flow"] == "document_legacy_bridge":
        descriptor["modality_declared"] = False
    result = harness.run_case("B", descriptor, language, variant=variant)
    return {"mode": MODE, "arm": "B", "abstains": bool(result["layer7_shown"]), "trigger_id": result["trigger_id"],
            "message_id": result.get("message_id"), "message_text": result["message_text"], "language": language,
            **({"variant": variant} if variant is not None else {}),
            "force_send_available": False, "descriptor": descriptor,
            "reachable_in_real_prototype_ui": ui_modality is not None}


if __name__ == "__main__":                                   # lab runner entry point: JSON on stdin -> JSON on stdout
    import json
    request = json.load(sys.stdin)
    print(json.dumps(evaluate_upload(request["body"], request.get("ui_modality"), request.get("language", "es"), request.get("variant"))))
