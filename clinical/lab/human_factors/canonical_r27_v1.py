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


# ---------------------------------------------------------------------------------------------------------------------------------
# canonical-r27-v1.1 · additive, backwards-compatible extension (R29_GEMINI_INFORME_MAESTRO_INTEGRADO, part II s.4). canonical-r27-v1 is NOT
# replaced: its validator is reused unchanged on the v1 projection of every v1.1 record. Laboratory only.
# ---------------------------------------------------------------------------------------------------------------------------------
import counterbalance as _cb  # noqa: E402

SCHEMA_VERSION_V11 = "canonical-r27-v1.1"
V11_ADDED = {"sequence_code", "subblock", "set_id", "e1_entry_mode", "stimulus_id", "stimulus_hash_sha256",
             "layer7_banner_to_first_action_ms", "task_duration_ms"}
E1_ENTRY_MODES = ("NONE", "ISOLATED_LAB_ENTRY_PR95")
STIMULUS = re.compile(r"^S[12]-(0[1-9]|1[0-5])$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
CLASS_OF_DEVICE = {"mobile_narrow_360": "mobile", "mobile_narrow_390": "mobile", "desktop_web": "web"}


def _count(value, minimum=0):
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def validate_record_v11(r):
    _need(isinstance(r, dict) and set(r) == FIELDS | V11_ADDED, "closed record: fields must be exactly canonical-r27-v1.1")
    _need(r["schema_version"] == SCHEMA_VERSION_V11, "schema_version must be canonical-r27-v1.1")
    projection = {k: v for k, v in r.items() if k not in V11_ADDED}
    projection["schema_version"] = SCHEMA_VERSION
    validate_record(projection)                                                          # every v1 rule still applies, untouched
    spec = _cb.NORMATIVE_R29.get(r["sequence_code"])
    _need(spec is not None, "sequence_code must be one of S1a..S4b")
    _need(r["period"] in (1, 2) and r["subblock"] in (1, 2), "period/subblock")
    arm_code, set_id, devices = spec[r["period"] - 1]
    _need(r["sequence"] == ("AB" if spec[0][0] == "A" else "BA"), "sequence disagrees with sequence_code")
    _need(r["arm"] == {"A": "A_real_react_control", "B": "B_prototype_alt_b"}[arm_code], "arm disagrees with sequence_code and period")
    _need(r["set_id"] == set_id, "set_id disagrees with sequence_code and period")
    _need(CLASS_OF_DEVICE[r["device_type"]] == devices[r["subblock"] - 1], "device disagrees with the sub-block of the matrix")
    _need(isinstance(r["stimulus_id"], str) and STIMULUS.match(r["stimulus_id"]), "stimulus_id")
    _need(r["stimulus_id"][:2] == ("S1" if set_id == "SET_1" else "S2"), "stimulus_id set disagrees with set_id")
    pair = int(r["stimulus_id"][3:])
    _need(_cb.PAIR_SCENARIO[pair] == r["scenario_id"], "stimulus pair disagrees with scenario_id")
    _need(isinstance(r["stimulus_hash_sha256"], str) and SHA256.match(r["stimulus_hash_sha256"]), "stimulus_hash_sha256")
    _need(r["e1_entry_mode"] in E1_ENTRY_MODES, "e1_entry_mode")
    isolated = r["scenario_id"] == "E1" and r["arm"] == "B_prototype_alt_b"
    _need((r["e1_entry_mode"] == "ISOLATED_LAB_ENTRY_PR95") == isolated, "e1_entry_mode must be ISOLATED only for scenario E1 in arm B")
    _need(_count(r["task_duration_ms"], 1), "task_duration_ms must be a positive integer (relative ms, never a calendar timestamp)")
    banner = r["layer7_banner_to_first_action_ms"]
    _need((banner is None) == (r["layer7_trigger_code"] == "NONE"), "banner-to-action time only when a layer 7 message was shown")
    _need(banner is None or _count(banner), "layer7_banner_to_first_action_ms")
    return r


_SUBREASON_OF = {(trigger, message): sub for (trigger, sub), message in L7_MAP.items()}
CONTEXT_REQUIRED = ("participant_opaque_id", "role_group", "language_stratum", "sequence_code", "period", "subblock", "stimulus_id",
                    "stimulus_hash_sha256", "task_duration_ms", "force_attempts")


def from_lab_ui_log(log, context):
    """canonical-r27-v1.1 record from the events the PR95 lab entry really emits (window.__LAB_LAYER7_LOG__) plus the harness context.
    Only facts the UI proves are derived (viewport, selection, banner, recovery by a confirmed upload). Abandonment, cancellation and
    forced-send attempts have no UI event: they must come from the harness (`trial_end`, `force_attempts`) or the conversion HARD FAILS."""
    _need(isinstance(log, list) and isinstance(context, dict), "log and context are required")
    missing = [k for k in CONTEXT_REQUIRED if k not in context]
    _need(not missing, f"harness context missing: {missing}")
    spec = _cb.NORMATIVE_R29.get(context["sequence_code"])
    _need(spec is not None and context["period"] in (1, 2), "sequence_code/period")
    arm_code = spec[context["period"] - 1][0]
    _need(STIMULUS.match(str(context["stimulus_id"])), "stimulus_id")
    pair = int(context["stimulus_id"][3:])
    scenario = _cb.PAIR_SCENARIO[pair]
    mechanism = MECHANISM[_cb.PAIR_MECHANISM[pair]]
    selected = [e for e in log if e.get("type") == "file_selected"]
    _need(selected and _count(selected[0]["detail"].get("viewport_width_px"), 1), "viewport_width_px was not captured by the UI")
    width = selected[0]["detail"]["viewport_width_px"]
    modality_events = [e for e in log if e.get("type") == "modality_selected"]
    declared = modality_events[-1]["detail"]["modality"] if modality_events else None
    banners = [e for e in log if e.get("type") == "layer7_banner_rendered"]
    confirmed = any(e.get("type") == "confirm_clicked" for e in log)
    trigger = message = subreason = "NONE"
    banner_ms = None
    if banners:
        detail = banners[0]["detail"]
        trigger, message = str(detail["trigger"])[:5], detail["message_id"]
        subreason = _SUBREASON_OF.get((trigger, message))
        _need(subreason is not None, "trigger/message combination has no approved subreason")
        actions = [e for e in log if e.get("type") in ("recovery_action", "modality_selected") and e["at_ms"] >= banners[0]["at_ms"]]
        banner_ms = int(round(actions[0]["at_ms"] - banners[0]["at_ms"])) if actions else None
        _need(banner_ms is not None or context.get("trial_end") == "abandoned", "no action after the banner and no abandonment reported by the harness")
        banner_ms = banner_ms if banner_ms is not None else 0
    end = context.get("trial_end") or ("completed" if confirmed else None)
    _need(end in ("completed", "abandoned", "cancelled_by_user"), "trial end is not provable from the UI log: harness must report trial_end")
    arm_b = arm_code == "B"
    if banners and len(banners) >= 1:
        last_banner = banners[-1]["at_ms"]
        recovered = confirmed and any(e.get("type") == "confirm_clicked" and e["at_ms"] > last_banner for e in log)
        recovery = "recovered_correctly" if recovered and end == "completed" else "abandoned" if end == "abandoned" else None
        _need(recovery is not None, "recovery outcome is not provable (banner without a confirmed upload or an abandonment)")
    else:
        recovery = "NA"
    if _cb.PAIR_MECHANISM[pair] == "M2":
        outcome = "technical_abstention_correct"
    elif _cb.PAIR_MECHANISM[pair] == "M1":
        _need(end == "completed", "M1 without a confirmed upload needs an adjudicated outcome from the harness")
        outcome = "bypass_residual"
    else:
        outcome = "valid_completed" if end == "completed" else "false_cancellation_human"
    actions_taken = [e["detail"].get("action") for e in log if e.get("type") == "recovery_action"]
    force = context["force_attempts"]
    _need(_count(force), "force_attempts")
    record = {"participant_opaque_id": context["participant_opaque_id"], "role_group": context["role_group"],
              "language_stratum": context["language_stratum"], "sequence": "AB" if spec[0][0] == "A" else "BA", "period": context["period"],
              "arm": {"A": "A_real_react_control", "B": "B_prototype_alt_b"}[arm_code], "arm_a_implementation_mode": None if arm_b else "real_react_r5_1_off",
              "arm_a_verified_real_react": not arm_b, "layer7_ui_enabled": arm_b, "device_type": device_for_width(width), "viewport_width_px": width,
              "mechanism_id": mechanism, "scenario_id": scenario, "outcome_status": outcome, "entry_flow": "explicit_prototype" if arm_b else "legacy_circuit",
              "declared_modality": declared, "selection_origin": "explicit_user_selection" if declared else "none",
              "transport_mode": "document_legacy_bridge" if declared == "document" else ("typed_contract" if arm_b else "legacy_passthrough"),
              "recovery_outcome": recovery, "recovery_action_type": actions_taken[0] if actions_taken else None, "attempted_force_blocked": force > 0,
              "layer7_execution_mode": "SIMULATED_LAB_HARNESS_ONLY" if arm_b else "DISCONNECTED_LEGACY",
              "layer7_trigger_code": trigger, "layer7_subreason_code": subreason, "layer7_message_key": message,
              "layer7_banner_rendered_ms": int(round(banners[0]["at_ms"])) if banners else None, "schema_version": SCHEMA_VERSION_V11,
              "sequence_code": context["sequence_code"], "subblock": context["subblock"], "set_id": spec[context["period"] - 1][1],
              "e1_entry_mode": "ISOLATED_LAB_ENTRY_PR95" if scenario == "E1" and arm_b else "NONE", "stimulus_id": context["stimulus_id"],
              "stimulus_hash_sha256": context["stimulus_hash_sha256"], "layer7_banner_to_first_action_ms": banner_ms,
              "task_duration_ms": context["task_duration_ms"]}
    return validate_record_v11(record)
