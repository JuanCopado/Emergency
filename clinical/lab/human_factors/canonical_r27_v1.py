"""canonical-r27-v1 · closed record contract and STRICT adapter (laboratory only).

Source: R27_GEMINI_INFORME_INTEGRADO_FINAL, part II table 4 (rows 1-9). Gemini declares it did NOT read the literal alt-b-0.1 enums of
PR87 (NO VERIFICADO); the 0.1 side below is read from alt_b.py in this repository. Nothing is coerced: every violation raises
CanonicalViolation (HARD FAIL). Historical alt-b-0.1 / alt-b-0.2 records are never modified.

Vocabulary left OPEN by the source (not invented here): `recovery_action_type` has no closed list in the report; it is accepted only as
null or a short token and is reported as NOT_SPECIFIED_VOCABULARY."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import alt_b  # noqa: E402

SCHEMA_VERSION = "canonical-r27-v1"
OPEN_VOCABULARY = {"recovery_action_type": "NOT_SPECIFIED_VOCABULARY"}
ROLE = {"medicine": "M", "nursing": "E"}
ARM = ("A_real_react_control", "B_prototype_alt_b")
DEVICE = ("mobile_narrow_360", "mobile_narrow_390", "desktop_web")
MECHANISM = {"M1": "M1_bypass_selection", "M2": "M2_layer7_abstention", "M3": "M3_valid_non_interference"}
SCENARIO_MECHANISM = {"A": "M3_valid_non_interference", "F": "M3_valid_non_interference", "B": "M1_bypass_selection",
                      "C": "M1_bypass_selection", "D": "M1_bypass_selection", "E1": "M2_layer7_abstention", "E2": "M2_layer7_abstention"}
LANGUAGE = {"es": "ES", "es-ES": "ES", "pt-PT": "pt-PT", "pt-BR": "pt-BR", "en": "EN", "en-US": "EN", "en-GB": "EN"}
OUTCOME = ("valid_completed", "bypass_residual", "detected_before_submit", "false_cancellation_human", "technical_abstention_correct",
           "system_technical_error", "protocol_deviation")
ENTRY_FLOW = ("legacy_circuit", "explicit_prototype")
MODALITY = ("skin_wound", "ecg", "xray", "pocus", "document")
SELECTION_ORIGIN = ("legacy_implicit", "explicit_user_selection", "none")
TRANSPORT = ("legacy_passthrough", "document_legacy_bridge", "typed_contract")
RECOVERY = ("NA", "recovered_correctly", "abandoned", "attempted_force_blocked")
L7_MODE = ("DISCONNECTED_LEGACY", "SIMULATED_LAB_HARNESS_ONLY")
L7_TRIGGER = ("NONE", "T7-01", "T7-02", "T7-03", "T7-04")
L7_SUBREASON = ("NONE", "explicit_flow_missing_selection", "unknown_or_unsupported_contract_id", "zero_bytes_or_decode_or_pr66_limit",
                "global_unsupported_format", "modality_container_incompatible")
L7_MESSAGE = ("NONE", "MSG_T7_NO_MODALITY", "MSG_T7_INCOMPATIBLE_MODALITY", "MSG_T7_CORRUPT_FILE", "MSG_T7_UNSUPPORTED_FORMAT")
# (trigger, subreason) -> message key, as in table row 9
L7_MAP = {("T7-01", "explicit_flow_missing_selection"): "MSG_T7_NO_MODALITY", ("T7-02", "unknown_or_unsupported_contract_id"): "MSG_T7_NO_MODALITY",
          ("T7-03", "zero_bytes_or_decode_or_pr66_limit"): "MSG_T7_CORRUPT_FILE", ("T7-04", "modality_container_incompatible"): "MSG_T7_INCOMPATIBLE_MODALITY",
          ("T7-04", "global_unsupported_format"): "MSG_T7_UNSUPPORTED_FORMAT"}
FIELDS = {"participant_opaque_id", "role_group", "language_stratum", "sequence", "period", "arm", "arm_a_implementation_mode",
          "arm_a_verified_real_react", "layer7_ui_enabled", "device_type", "viewport_width_px", "mechanism_id", "scenario_id", "outcome_status",
          "entry_flow", "declared_modality", "selection_origin", "transport_mode", "recovery_outcome", "recovery_action_type",
          "attempted_force_blocked", "layer7_execution_mode", "layer7_trigger_code", "layer7_subreason_code", "layer7_message_key",
          "layer7_banner_rendered_ms", "schema_version"}
OPAQUE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class CanonicalViolation(ValueError):
    """HARD FAIL: the record or the conversion violates canonical-r27-v1."""


def _need(condition, message):
    if not condition:
        raise CanonicalViolation(message)


def device_for_width(width):
    _need(isinstance(width, int) and not isinstance(width, bool) and width > 0, "viewport_width_px must be a positive integer")
    if 350 <= width <= 375:
        return "mobile_narrow_360"
    if 376 <= width <= 414:
        return "mobile_narrow_390"
    _need(width >= 1024, f"viewport_width_px={width} is neither mobile (350-414) nor desktop (>=1024)")
    return "desktop_web"


def validate_record(r):
    _need(isinstance(r, dict) and set(r) == FIELDS, "closed record: fields must be exactly the canonical-r27-v1 fields")
    _need(r["schema_version"] == SCHEMA_VERSION, "schema_version")
    _need(isinstance(r["participant_opaque_id"], str) and OPAQUE.match(r["participant_opaque_id"]), "participant_opaque_id must be opaque")
    _need(r["role_group"] in ("M", "E"), "role_group must be M or E (no 'clinician', null or rare subspecialties)")
    _need(r["language_stratum"] in ("ES", "pt-PT", "pt-BR", "EN"), "language_stratum (generic 'pt' is refused)")
    _need(r["sequence"] in ("AB", "BA") and r["period"] in (1, 2), "sequence/period")
    arm = r["arm"]
    _need(arm in ARM, "arm")
    if arm == "A_real_react_control":
        _need(r["arm_a_implementation_mode"] == "real_react_r5_1_off", "arm A must come from the real React app (mock refused)")
        _need(r["arm_a_verified_real_react"] is True, "arm_a_verified_real_react must be true")
        _need(r["layer7_execution_mode"] == "DISCONNECTED_LEGACY" and r["layer7_trigger_code"] == "NONE", "no layer 7 in arm A")
    else:
        _need(r["layer7_ui_enabled"] is True, "arm B requires the full layer 7 UI")
        _need(r["layer7_execution_mode"] == "SIMULATED_LAB_HARNESS_ONLY", "arm B layer 7 must be SIMULATED_LAB_HARNESS_ONLY")
    _need(r["device_type"] == device_for_width(r["viewport_width_px"]), "device_type must match viewport_width_px (trial level)")
    _need(r["mechanism_id"] in MECHANISM.values() and SCENARIO_MECHANISM.get(r["scenario_id"]) == r["mechanism_id"],
          "scenario_id and mechanism_id are inconsistent")
    _need(r["outcome_status"] in OUTCOME, "outcome_status")
    _need(r["entry_flow"] in ENTRY_FLOW and r["selection_origin"] in SELECTION_ORIGIN and r["transport_mode"] in TRANSPORT, "declarative envelope")
    _need(r["declared_modality"] is None or r["declared_modality"] in MODALITY, "declared_modality")
    _need(r["layer7_trigger_code"] in L7_TRIGGER and r["layer7_subreason_code"] in L7_SUBREASON and r["layer7_message_key"] in L7_MESSAGE, "layer 7 fields")
    _need(r["recovery_outcome"] in RECOVERY, "recovery_outcome")
    _need(isinstance(r["attempted_force_blocked"], bool), "attempted_force_blocked")
    _need(r["recovery_action_type"] is None or (isinstance(r["recovery_action_type"], str) and OPAQUE.match(r["recovery_action_type"])), "recovery_action_type")
    banner = r["layer7_banner_rendered_ms"]
    _need(banner is None or (isinstance(banner, int) and not isinstance(banner, bool) and banner >= 0), "layer7_banner_rendered_ms")
    # row 7: document chosen through the legacy bridge is a selection, not a missing one; E1 (null, none) is what triggers T7-01
    if r["transport_mode"] == "document_legacy_bridge":
        _need(r["declared_modality"] == "document" and r["selection_origin"] == "explicit_user_selection", "document bridge needs explicit selection")
        _need(r["layer7_trigger_code"] != "T7-01", "the document bridge must not trigger T7-01")
    if r["entry_flow"] == "explicit_prototype" and r["selection_origin"] == "none":
        _need(r["declared_modality"] is None, "selection_origin none implies no declared modality")
    if r["entry_flow"] == "explicit_prototype":
        _need(r["selection_origin"] != "legacy_implicit", "explicit flow cannot have legacy_implicit origin")
    else:
        _need(r["selection_origin"] != "explicit_user_selection" or r["declared_modality"] is not None, "selection needs a modality")
    # row 9: layer 7 mapping
    trigger, sub, msg = r["layer7_trigger_code"], r["layer7_subreason_code"], r["layer7_message_key"]
    if trigger == "NONE":
        _need(sub == "NONE" and msg == "NONE", "no trigger implies NONE subreason and message")
    else:
        _need(arm == "B_prototype_alt_b", "layer 7 trigger outside arm B")
        _need(L7_MAP.get((trigger, sub)) == msg, "trigger/subreason/message combination is not an approved one (T7-04 needs its subreason)")
    # row 6: outcomes
    outcome, mech = r["outcome_status"], r["mechanism_id"]
    if outcome in ("bypass_residual", "detected_before_submit"):
        _need(mech == MECHANISM["M1"] and trigger == "NONE", "bypass states only in M1 with trigger NONE")
    if outcome == "technical_abstention_correct":
        _need(mech == MECHANISM["M2"] and arm == "B_prototype_alt_b" and trigger in ("T7-01", "T7-03", "T7-04"), "technical abstention only in M2 arm B")
    if outcome == "false_cancellation_human":
        _need(mech == MECHANISM["M3"], "false human cancellation only in M3")
    if mech == MECHANISM["M1"]:
        _need(trigger != "T7-04", "M1 cannot trigger T7-04")
    # row 8: recovery
    if mech == MECHANISM["M2"] and arm == "B_prototype_alt_b":
        _need(r["recovery_outcome"] != "NA", "M2 arm B needs a recovery state")
    else:
        _need(r["recovery_outcome"] == "NA", "recovery states only in M2 arm B")
    if r["recovery_outcome"] == "attempted_force_blocked":
        _need(r["attempted_force_blocked"] is True, "attempted_force_blocked flag")
    return r


def from_alt_b_01(record, capture):
    """Strict alt-b-0.1 -> canonical-r27-v1 conversion. `capture` must carry what 0.1 never recorded; anything missing or a source from
    the discarded mock / synthetic driver raises CanonicalViolation. No default is ever assumed."""
    _need(isinstance(record, dict) and set(record) == alt_b.RECORD_FIELDS, "not a closed alt-b-0.1 record")
    _need(isinstance(capture, dict), "capture evidence is required")
    required = ("arm_a_implementation_mode", "layer7_ui_enabled", "viewport_width_px", "outcome_status", "entry_flow", "declared_modality",
                "selection_origin", "transport_mode", "recovery_outcome", "attempted_force_blocked", "layer7_message_key")
    if record["layer7_trigger_code"] is not None:
        required += ("layer7_subreason_code",)            # 0.1 subreason names differ from the canonical ones: never mapped by name
    missing = [k for k in required if k not in capture]
    _need(not missing, f"capture evidence missing: {missing}")
    _need(record["role_group"] in ROLE and record["language_stratum"] in LANGUAGE, "role_group / language_stratum outside the 0.1 vocabulary")
    arm = {"A": "A_real_react_control", "B": "B_prototype_alt_b"}[record["arm"]]
    out = {"participant_opaque_id": record["participant_opaque_id"], "role_group": ROLE[record["role_group"]],
           "language_stratum": LANGUAGE[record["language_stratum"]], "sequence": record["sequence"], "period": record["period"], "arm": arm,
           "arm_a_implementation_mode": capture["arm_a_implementation_mode"],
           "arm_a_verified_real_react": capture["arm_a_implementation_mode"] == "real_react_r5_1_off" if arm.startswith("A") else True,
           "layer7_ui_enabled": capture["layer7_ui_enabled"], "device_type": device_for_width(capture["viewport_width_px"]),
           "viewport_width_px": capture["viewport_width_px"], "mechanism_id": MECHANISM[record["mechanism_id"]],
           "scenario_id": record["scenario_code"], "outcome_status": capture["outcome_status"], "entry_flow": capture["entry_flow"],
           "declared_modality": capture["declared_modality"], "selection_origin": capture["selection_origin"],
           "transport_mode": capture["transport_mode"], "recovery_outcome": capture["recovery_outcome"],
           "recovery_action_type": capture.get("recovery_action_type"), "attempted_force_blocked": capture["attempted_force_blocked"],
           "layer7_execution_mode": "DISCONNECTED_LEGACY" if arm.startswith("A") else "SIMULATED_LAB_HARNESS_ONLY",
           "layer7_trigger_code": "NONE" if record["layer7_trigger_code"] is None else record["layer7_trigger_code"].split("_")[0],
           "layer7_subreason_code": capture["layer7_subreason_code"] if record["layer7_trigger_code"] is not None else "NONE", "layer7_message_key": capture["layer7_message_key"],
           "layer7_banner_rendered_ms": capture.get("layer7_banner_rendered_ms"), "schema_version": SCHEMA_VERSION}
    return validate_record(out)
