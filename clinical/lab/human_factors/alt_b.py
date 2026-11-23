"""Alternative B (DEC-CLIN-R22-01) · telemetry records, M1/M2/M3 partition and versioned export. LABORATORY ONLY, stdlib + jsonschema in tests.

Implements the R23 protocol (Gemini): the 15 trials of each period are split in three mechanisms that are NEVER mixed:
  M1 (scenarios B, C, D)  crossed AB/BA contrast B vs A (selector bypass);
  M2 (scenarios E1, E2)   Layer 7 abstention: descriptive, ARM B ONLY; any between-arm contrast is PROHIBITED and not computed;
  M3 (scenarios A, F)     crossed AB/BA contrast B vs A (non-interference, false cancellations, time).
It reuses the audited statistical engine (human_factors_tools.summarize) on the legacy trial records derived from each mechanism.
Nothing here is clinical evidence: with the technical driver the records are SYNTHETIC and the study status is NOT_EXECUTED.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import human_factors_tools as hf  # noqa: E402

SCHEMA_VERSION = "alt-b-0.1"
SUPPORTED_VERSIONS = (SCHEMA_VERSION,)
LEGACY_STAGE = "STAGE_1_FORMATIVE_ESTIMATION"          # historical label (PR83 export), kept for the legacy schema only
STAGE = "STAGE_1_FORMATIVE_ALT_B"
HARNESS_MODE = "SIMULATED_LAB_HARNESS_ONLY"            # package-level / per-record execution mode of Layer 7
LAYER7_RESULT_LABEL = "SIMULATED_LAYER7_HARNESS_LAB_ONLY"   # specific label of a harness RESULT (layer7_harness.run_case)
NOT_APPLICABLE_ARM_A = "NOT_APPLICABLE_ARM_A"
STUDY_STATUS = "NOT_EXECUTED_PROTOCOL_ONLY"
TOOLING_STATUS = "NOT_EXECUTED_TOOLING_ONLY"
ACCEPTANCE = "PENDING_PHYSICIAN_OWNER_REVIEW"
UNIMPLEMENTED_STAGE2 = ["GLMM", "GEE_SMALL_SAMPLE", "DEVICE_ARM_INTERACTION"]
DATA_ORIGIN = "SYNTHETIC_TECHNICAL_DRIVER"             # the only origin admitted by 0.1: no study with professionals is authorised

SCENARIO_MECHANISM = {"A": "M3", "B": "M1", "C": "M1", "D": "M1", "E1": "M2", "E2": "M2", "F": "M3"}
MECHANISMS = ("M1", "M2", "M3")
ARMS = ("A", "B")
DEVICES = ("mobile_narrow", "desktop_web")
ROLE_GROUPS = ("medicine", "nursing")
LANGUAGE_STRATA = ("es-ES", "pt-PT", "pt-BR", "en")
SEQUENCES = ("AB", "BA")
RECOVERY = ("not_applicable", "recovered", "not_recovered", "forced_send_attempt_blocked")
OUTCOMES = ("completed", "abandoned", "blocked_by_layer7")
SELECTION_ORIGINS = ("explicit_prototype", "none", "legacy_classic", "legacy_document_bridge")
TRIGGERS = ("T7-01_UNDECLARED_MODALITY", "T7-02_UNKNOWN_CONTRACT", "T7-03_CORRUPT_UNPROCESSABLE", "T7-04_FORMAT_CONTAINER_MISMATCH")
SUBREASONS = ("declared_modality_absent", "declared_kind_not_in_contract_registry", "container_parse_error",
              "modality_container_incompatible", "global_unsupported_format")
OPAQUE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
RECORD_FIELDS = {"participant_opaque_id", "role_group", "language_stratum", "sequence", "period", "arm", "device_type", "mechanism_id",
                 "scenario_id", "scenario_code", "trial_order", "stimulus_hash_sha256", "declared_envelope", "preview_shown_ms",
                 "initial_modality", "chosen_modality", "modality_change_count", "modality_changed_after_preview", "confirmation_clicked",
                 "comprehension_correct", "layer7_execution_mode", "layer7_trigger_code", "layer7_subreason_code", "recovery_outcome",
                 "outcome_status", "task_duration_ms"}
ENVELOPE_FIELDS = {"declared_modality", "selection_origin", "declared_mime_type", "declared_extension"}
FORBIDDEN_KEY = re.compile(r"verdict|approved|safe_for_use|pass_fail|clinical_conclusion|diagnos|name|email|phone|ip_address|timestamp|date", re.I)


def _count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _manifest_index(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get("stimuli"), list):
        raise ValueError("stimuli manifest must contain a stimuli list")
    index = {}
    for entry in manifest["stimuli"]:
        sid = entry["stimulus_id"]
        if sid in index:
            raise ValueError(f"stimulus {sid} is listed twice")
        index[sid] = entry
    return index


def validate_records(records, manifest):
    """Closed-field validation + consistency with the stimuli manifest. No free text, no calendar timestamps, no PII."""
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")
    index = _manifest_index(manifest)
    seen, arm_of_period, sequence_of = set(), {}, {}
    for r in records:
        if not isinstance(r, dict) or set(r) != RECORD_FIELDS:
            raise ValueError(f"record fields must be exactly {sorted(RECORD_FIELDS)}")
        for key in r:
            if FORBIDDEN_KEY.search(key) and key not in ("participant_opaque_id", "scenario_id"):
                raise ValueError(f"forbidden field name {key}")
        if not isinstance(r["participant_opaque_id"], str) or not OPAQUE.match(r["participant_opaque_id"]):
            raise ValueError("participant_opaque_id must be an opaque code")
        for field, allowed in (("role_group", ROLE_GROUPS), ("language_stratum", LANGUAGE_STRATA), ("sequence", SEQUENCES),
                               ("arm", ARMS), ("device_type", DEVICES), ("mechanism_id", MECHANISMS),
                               ("recovery_outcome", RECOVERY), ("outcome_status", OUTCOMES)):
            if r[field] not in allowed:
                raise ValueError(f"unknown {field}")
        if r["period"] not in (1, 2) or isinstance(r["period"], bool):
            raise ValueError("period must be 1 or 2")
        if r["scenario_code"] not in SCENARIO_MECHANISM or SCENARIO_MECHANISM[r["scenario_code"]] != r["mechanism_id"]:
            raise ValueError("mechanism_id does not match the scenario code (M1: B,C,D · M2: E1,E2 · M3: A,F)")
        entry = index.get(r["scenario_id"])
        if entry is None:
            raise ValueError(f"scenario {r['scenario_id']} is not in the stimuli manifest")
        if entry["scenario_code"] != r["scenario_code"] or entry["mechanism_id"] != r["mechanism_id"]:
            raise ValueError("record disagrees with the manifest on scenario code or mechanism")
        if r["stimulus_hash_sha256"] != entry["sha256"]:
            raise ValueError(f"stimulus hash of {r['scenario_id']} does not match the manifest")
        if r["stimulus_hash_sha256"] is not None and not SHA.match(r["stimulus_hash_sha256"]):
            raise ValueError("stimulus_hash_sha256 must be 64 lowercase hex characters or null (pending stimulus)")
        env = r["declared_envelope"]
        if not isinstance(env, dict) or set(env) != ENVELOPE_FIELDS or env["selection_origin"] not in SELECTION_ORIGINS:
            raise ValueError("declared_envelope must carry exactly declared_modality, selection_origin, declared_mime_type, declared_extension")
        for field in ("declared_modality", "declared_mime_type", "declared_extension"):
            if env[field] is not None and not isinstance(env[field], str):
                raise ValueError(f"declared_envelope.{field} must be a string or null")
        if env["declared_modality"] is not None and env["declared_modality"] not in hf.MODALITIES:
            raise ValueError("unknown declared modality")
        for field in ("initial_modality", "chosen_modality"):
            if r[field] is not None and r[field] not in hf.MODALITIES:
                raise ValueError(f"unknown {field}")
        for field in ("trial_order", "modality_change_count", "task_duration_ms"):
            if not _count(r[field]):
                raise ValueError(f"{field} must be a non-negative integer")
        if r["trial_order"] < 1:
            raise ValueError("trial_order must be positive")
        if r["preview_shown_ms"] is not None and not _count(r["preview_shown_ms"]):
            raise ValueError("preview_shown_ms must be a non-negative integer or null")
        for field in ("modality_changed_after_preview", "confirmation_clicked"):
            if not isinstance(r[field], bool):
                raise ValueError(f"{field} must be a boolean")
        if r["comprehension_correct"] is not None and not isinstance(r["comprehension_correct"], bool):
            raise ValueError("comprehension_correct must be true, false or null")
        if r["arm"] == "A":
            if r["layer7_execution_mode"] != NOT_APPLICABLE_ARM_A or r["layer7_trigger_code"] is not None or r["layer7_subreason_code"] is not None:
                raise ValueError("arm A has no Layer 7: execution mode must be NOT_APPLICABLE_ARM_A and no trigger may be recorded")
        else:
            if r["layer7_execution_mode"] != HARNESS_MODE:
                raise ValueError(f"arm B Layer 7 execution mode must be {HARNESS_MODE}")
        if r["layer7_trigger_code"] is not None and r["layer7_trigger_code"] not in TRIGGERS:
            raise ValueError("unknown Layer 7 trigger")
        if r["layer7_subreason_code"] is not None and r["layer7_subreason_code"] not in SUBREASONS:
            raise ValueError("unknown Layer 7 subreason")
        if r["layer7_trigger_code"] is None and r["layer7_subreason_code"] is not None:
            raise ValueError("a subreason needs a trigger")
        if r["layer7_trigger_code"] is not None and r["confirmation_clicked"] and r["outcome_status"] == "completed":
            raise ValueError("a Layer 7 abstention cannot end in a completed send (no 'force send')")
        key = (r["participant_opaque_id"], r["scenario_id"])
        if key in seen:
            raise ValueError(f"participant {key[0]} has scenario {key[1]} twice")
        seen.add(key)
        pp = (r["participant_opaque_id"], r["period"])
        if arm_of_period.setdefault(pp, r["arm"]) != r["arm"]:
            raise ValueError(f"participant {pp[0]} mixes arms inside period {pp[1]}")
        if sequence_of.setdefault(r["participant_opaque_id"], r["sequence"]) != r["sequence"]:
            raise ValueError("a participant has one sequence only")
    for (participant, period), arm in arm_of_period.items():
        sequence = sequence_of[participant]
        if period == 1 and arm != sequence[0]:
            raise ValueError(f"participant {participant}: period-1 arm contradicts sequence {sequence}")
        if period == 2 and arm != sequence[1]:
            raise ValueError(f"participant {participant}: period-2 arm contradicts sequence {sequence}")
    return len(records)


def to_legacy(record, manifest):
    """One telemetry record -> one record of the audited statistical engine (M1/M3 only). The mechanism never reaches the engine."""
    entry = _manifest_index(manifest)[record["scenario_id"]]
    if record["mechanism_id"] == "M2":
        raise ValueError("M2 records are never converted: they are excluded from between-arm contrasts")
    chosen = record["chosen_modality"]
    return {"participant": record["participant_opaque_id"], "role": "physician" if record["role_group"] == "medicine" else "nurse",
            "scenario_id": record["scenario_id"], "condition": "baseline" if record["arm"] == "A" else "prototype", "period": record["period"],
            "intended_modality": entry["true_modality"], "initial_modality": record["initial_modality"], "chosen_modality": chosen,
            "confirmed": bool(record["confirmation_clicked"] and chosen is not None), "changed_modality_count": record["modality_change_count"],
            "seconds": record["task_duration_ms"] / 1000.0, "comprehension_correct": record["comprehension_correct"],
            "platform": "mobile" if record["device_type"] == "mobile_narrow" else "web", "order_in_period": record["trial_order"]}


def _median_iqr(values):
    ordered = sorted(values)
    if not ordered:
        return None
    def q(p):
        pos = p * (len(ordered) - 1)
        lo, hi = int(pos), min(int(pos) + 1, len(ordered) - 1)
        return ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo)
    return {"median": round(q(0.5), 1), "q1": round(q(0.25), 1), "q3": round(q(0.75), 1), "n": len(ordered)}


def _participant_exact(with_event, participants):
    interval = hf.clopper_pearson(with_event, participants)
    return {"participants": participants, "with_event": with_event,
            "exact_95_over_participants": [round(x, 4) for x in interval] if interval else None,
            "label": "Clopper-Pearson over independent PARTICIPANTS, descriptive; never a trial-rate interval",
            "zero_event_report": hf.zero_event_report(0, 1, 0, participants) if with_event == 0 and participants else None}


def summarize_m2(records, manifest):
    """Descriptive, ONE ARM (B). No contrast against arm A is computed: that is prohibited by the protocol."""
    index = _manifest_index(manifest)
    arm_b = [r for r in records if r["mechanism_id"] == "M2" and r["arm"] == "B"]
    arm_a = [r for r in records if r["mechanism_id"] == "M2" and r["arm"] == "A"]
    by_scenario = {}
    for code in ("E1", "E2"):
        rows = [r for r in arm_b if r["scenario_code"] == code]
        fired = [r for r in rows if r["layer7_trigger_code"] is not None]
        matching = [r for r in rows if r["layer7_trigger_code"] == index[r["scenario_id"]]["expected_layer7_trigger"]]
        by_scenario[code] = {"trials": len(rows), "layer7_fired": len(fired), "fired_as_expected": len(matching),
                             "recovered": sum(r["recovery_outcome"] == "recovered" for r in rows),
                             "not_recovered": sum(r["recovery_outcome"] == "not_recovered" for r in rows),
                             "forced_send_attempts_blocked": sum(r["recovery_outcome"] == "forced_send_attempt_blocked" for r in rows),
                             "comprehension_answered": sum(r["comprehension_correct"] is not None for r in rows),
                             "comprehension_correct": sum(r["comprehension_correct"] is True for r in rows),
                             "task_duration_ms": _median_iqr([r["task_duration_ms"] for r in rows])}
    participants = sorted({r["participant_opaque_id"] for r in arm_b})
    def with_unrecovered(p):
        return any(r["recovery_outcome"] in ("not_recovered",) for r in arm_b if r["participant_opaque_id"] == p)
    def with_misread(p):
        return any(r["comprehension_correct"] is False for r in arm_b if r["participant_opaque_id"] == p)
    flags = {"small_cluster_warning": len(participants) < hf.SMALL_CLUSTER_REFERENCE,
             "very_small_cluster_descriptive_only": len(participants) < hf.VERY_SMALL_CLUSTER}
    return {"mechanism": "M2", "scenarios": "E1, E2", "design": "ONE ARM (B), descriptive and formative",
            "between_arm_contrast": "PROHIBITED_NOT_COMPUTED", "arm_b": {"participants": len(participants), "trials": len(arm_b), "by_scenario": by_scenario,
                                                                         "participants_with_unrecovered_trial": _participant_exact(sum(map(with_unrecovered, participants)), len(participants)),
                                                                         "participants_with_misread_message": _participant_exact(sum(map(with_misread, participants)), len(participants))},
            "arm_a_baseline_descriptive_only": {"trials": len(arm_a), "note": "legacy interface has no Layer 7 and no declared-modality gate; qualitative baseline, excluded from any contrast",
                                                "layer7_triggers_recorded": sum(r["layer7_trigger_code"] is not None for r in arm_a)},
            **flags}


def unexpected_layer7(records, mechanism):
    """Layer 7 firing on M1/M3 arm-B trials (protocol: it must never fire there). Reported with the dual zero-event rule."""
    rows = [r for r in records if r["mechanism_id"] == mechanism and r["arm"] == "B"]
    fired = [r for r in rows if r["layer7_trigger_code"] is not None]
    participants = sorted({r["participant_opaque_id"] for r in rows})
    with_fire = len({r["participant_opaque_id"] for r in fired})
    return {"arm_b_trials": len(rows), "layer7_fired": len(fired), "participants": len(participants), "participants_with_firing": with_fire,
            "expected": "0 (Layer 7 must not fire on valid photographs or on the kind=null document bridge)",
            "zero_event_report": hf.zero_event_report(len(fired), len(rows), with_fire, len(participants)) if not fired and rows else None}


def summarize_alt_b(records, manifest, resamples=hf.DEFAULT_RESAMPLES, seed="r24"):
    validate_records(records, manifest)
    partition = Counter(r["mechanism_id"] for r in records)
    summary = {}
    for mechanism in ("M1", "M3"):
        legacy = [to_legacy(r, manifest) for r in records if r["mechanism_id"] == mechanism]
        if not legacy:
            summary[mechanism.lower()] = {"mechanism": mechanism, "status": "NO_RECORDS"}
            continue
        block = hf.summarize(legacy, resamples, f"{seed}:{mechanism}")
        block["mechanism"] = mechanism
        block["design_note"] = "crossed AB/BA contrast B vs A, pairing and participant resampling preserved; exploratory"
        block["layer7_firing_on_this_mechanism"] = unexpected_layer7(records, mechanism)
        summary[mechanism.lower()] = block
    summary["m2"] = summarize_m2(records, manifest)
    return {"mechanism_partition": {m: partition.get(m, 0) for m in MECHANISMS}, "excluded_from_between_arm_contrasts": ["M2"],
            "m1": summary["m1"], "m2": summary["m2"], "m3": summary["m3"]}


def stimuli_bytes_digest(manifest):
    """Digest of the (stimulus_id, sha256-of-bytes) list: binds the export to the real files of the bank."""
    return hf.digest(sorted((s["stimulus_id"], s["sha256"]) for s in manifest["stimuli"]))


def export_alt_b(records, manifest, resamples=hf.DEFAULT_RESAMPLES, seed="r24", git_commit_sha=None):
    validate_records(records, manifest)
    if git_commit_sha is not None and not re.fullmatch(r"[0-9a-f]{7,40}", str(git_commit_sha)):
        raise ValueError("git_commit_sha must be a 7-40 character lowercase hexadecimal commit id")
    summary = summarize_alt_b(records, manifest, resamples, seed)
    return {"schema_version": SCHEMA_VERSION, "study_stage": STAGE, "layer7_execution_mode": HARNESS_MODE,
            "layer7_result_label": LAYER7_RESULT_LABEL, "study_status": STUDY_STATUS, "tooling_status": TOOLING_STATUS,
            "data_origin": DATA_ORIGIN, "unimplemented_stage2_models": list(UNIMPLEMENTED_STAGE2), "acceptance_decision": ACCEPTANCE,
            "tool_version": hf.TOOL_VERSION, "git_commit_sha": git_commit_sha, "resamples": resamples, "seed": str(seed),
            "stimuli_manifest_sha256": hf.digest(manifest), "stimuli_bytes_sha256": stimuli_bytes_digest(manifest),
            "records_sha256": hf.digest(records), "summary_sha256": hf.digest(summary),
            "mechanism_partition": summary["mechanism_partition"], "summary": summary,
            "limitations": list(hf.LIMITATIONS) + ["Records come from a technical driver, not from people: nothing here is evidence of safe human use.",
                                                   "M2 (E1/E2) is descriptive and one-arm; no between-arm statistic exists for it."]}


def scan_export_for_verdicts(document):
    """Every KEY of the export, recursively, must be free of verdict-like names (no automatic clinical conclusion)."""
    bad = []
    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                if re.search(r"verdict|approved|safe_for_use|pass_fail|clinical_conclusion|diagnos", str(key), re.I):
                    bad.append(path + "/" + str(key))
                walk(value, path + "/" + str(key))
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
    walk(document, "")
    return bad


SCHEMA_PATH = Path(__file__).resolve().parent / "export-alt-b.schema.json"


def validate_export(document, records=None, manifest=None):
    """Version gate + JSON Schema + (when the sources are given) recomputed SHA-256 + no-verdict scan. Raises ValueError."""
    import jsonschema
    if not isinstance(document, dict):
        raise ValueError("export must be a JSON object")
    version = document.get("schema_version")
    if version is None and document.get("study_stage") == LEGACY_STAGE:
        raise ValueError("historical stage1-0.1 export: validate it with human-factors-export.schema.json, not with the alternative-B schema")
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(f"unsupported export schema_version {version!r}; supported: {list(SUPPORTED_VERSIONS)}")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(document), key=lambda e: list(e.path))
    if errors:
        raise ValueError("; ".join(f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors[:5]))
    if hf.digest(document["summary"]) != document["summary_sha256"]:
        raise ValueError("summary_sha256 does not match the summary")
    if document["mechanism_partition"] != document["summary"]["mechanism_partition"]:
        raise ValueError("mechanism_partition differs between the header and the summary")
    if records is not None and hf.digest(records) != document["records_sha256"]:
        raise ValueError("records_sha256 does not match the records")
    if manifest is not None:
        if hf.digest(manifest) != document["stimuli_manifest_sha256"]:
            raise ValueError("stimuli_manifest_sha256 does not match the manifest")
        if stimuli_bytes_digest(manifest) != document["stimuli_bytes_sha256"]:
            raise ValueError("stimuli_bytes_sha256 does not match the manifest file hashes")
    bad = scan_export_for_verdicts(document)
    if bad:
        raise ValueError(f"verdict-like keys are not allowed in an export: {bad[:3]}")
    return True
