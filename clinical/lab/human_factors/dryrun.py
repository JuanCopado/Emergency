"""Technical DRY-RUN of the Stage 1 alternative-B pipeline · LABORATORY ONLY · NO professionals, NO people.

A deterministic TECHNICAL DRIVER (not a participant) walks the 30 tasks (15 per period, two disjoint sets, two arms, AB/BA, M1/M2/M3, mobile
and desktop labels) and produces telemetry records. Layer 7 decisions come from the audited harness evaluating the REAL BYTES of the stimuli that
exist; for stimuli still PENDING_STIMULUS_GENERATION the descriptor is built from the specification and flagged. Error/cancellation events follow
a neutral hash pattern that does NOT depend on the arm. The ONLY arm-dependent item is POSITIVE_CONTROL_MS: a documented constant added to the duration
of arm-B M1/M3 trials as a positive control of the additional-time computation (set it to 0 for a null driver). Nothing here replaces human observation.
"""
import hashlib
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import alt_b  # noqa: E402
import bank_r23 as bank  # noqa: E402
import file_probe  # noqa: E402
import human_factors_tools as hf  # noqa: E402
import layer7_harness as harness  # noqa: E402

POSITIVE_CONTROL_MS = 2500      # documented positive control for the delta-t pipeline; the only arm-dependent quantity of the driver
LANGUAGE_OF = {"es-ES": "es", "pt-PT": "pt", "pt-BR": "pt", "en": "en"}
CONTAINER_SIGNATURE = {"jpeg": "jpeg", "webp": "webp", "pdf": "pdf", "unspecified_image": "png"}
MIME = {"jpeg": "image/jpeg", "webp": "image/webp", "pdf": "application/pdf", "png": "image/png"}
EXT = {"jpeg": ".jpg", "webp": ".webp", "pdf": ".pdf", "png": ".png"}


def _h(*parts):
    return int(hashlib.sha256(":".join(map(str, parts)).encode()).hexdigest(), 16)


def trial_order(seed, participant, period, pairs=range(1, 16)):
    """Pseudo-random order with the anti-priming constraint: the first two tasks are never both M1 injections."""
    rng = random.Random(f"{seed}:{participant}:{period}")
    for _ in range(200):
        order = list(pairs)
        rng.shuffle(order)
        if not (bank.MECHANISM[bank.PAIR_CODES[order[0]]] == "M1" and bank.MECHANISM[bank.PAIR_CODES[order[1]]] == "M1"):
            return order
    raise RuntimeError("could not satisfy the ordering constraint")


def participants(count=4, seed="r24"):
    out = []
    languages = alt_b.LANGUAGE_STRATA
    for i in range(count):
        out.append({"id": f"DRY-{i + 1:02d}", "sequence": "AB" if i % 2 == 0 else "BA", "role_group": alt_b.ROLE_GROUPS[i % 2],
                    "language_stratum": languages[i % len(languages)], "device_first": "mobile_narrow" if (i // 2) % 2 == 0 else "desktop_web"})
    return out


def _descriptor(entry, arm, declared_kind, directory):
    flow = "document_legacy_bridge" if entry["true_modality"] == "document" and arm == "B" else "modality_entry"
    if entry["scenario_code"] == "E1":
        declared_kind = None
    if entry.get("file"):
        return file_probe.describe(Path(directory).parent / entry["file"], flow, declared_kind), "REAL_FILE_BYTES"
    signature = CONTAINER_SIGNATURE.get(entry["container_spec"], "jpeg")
    return ({"flow": flow, "modality_declared": declared_kind is not None, "declared_kind": declared_kind, "signature_kind": signature,
             "container_parse_ok": True, "declared_mime_type": MIME.get(signature), "declared_extension": EXT.get(signature)}, "SPEC_ONLY_NO_FILE")


def run_trial(p, arm, period, device, order_index, entry, directory):
    code, mechanism = entry["scenario_code"], entry["mechanism_id"]
    route, true = entry["route_modality"], entry["true_modality"]
    wrong_selection = mechanism == "M1" and _h(p["id"], entry["stimulus_id"], "err") % 8 == 0     # neutral pattern, independent of the arm
    declared = route if (mechanism == "M1" and wrong_selection) else (true if mechanism in ("M1", "M3") else route)
    if mechanism == "M3" and true == "document":
        declared = None
    descriptor, source = _descriptor(entry, arm, declared, directory)
    harness_out = harness.run_case(arm, descriptor, LANGUAGE_OF[p["language_stratum"]], code)
    trigger, subreason = harness_out["trigger_id"], None
    if trigger:
        subreason = {"T7-01_UNDECLARED_MODALITY": "declared_modality_absent", "T7-02_UNKNOWN_CONTRACT": "declared_kind_not_in_contract_registry",
                     "T7-03_CORRUPT_UNPROCESSABLE": "container_parse_error"}.get(trigger)
        if trigger == "T7-04_FORMAT_CONTAINER_MISMATCH":
            subreason = "global_unsupported_format" if harness_out.get("message_id") == "MSG_T7_D" else "modality_container_incompatible"
    false_cancel = mechanism == "M3" and _h(p["id"], entry["stimulus_id"], "cancel") % 11 == 0
    origin = ("legacy_document_bridge" if (mechanism == "M3" and true == "document" and arm == "B") else
              "none" if code == "E1" else "explicit_prototype" if arm == "B" else "legacy_classic")
    chosen = None if (false_cancel or trigger) else (declared if declared else None)
    if mechanism == "M3" and true == "document" and not false_cancel and not trigger:
        chosen = "document"
    confirmed = chosen is not None and not trigger
    if mechanism == "M2" and arm == "A":
        confirmed, chosen = True, None                        # legacy interface: sends without a declared-modality gate (qualitative baseline)
    recovery = ("not_applicable" if not trigger else "recovered")
    outcome = "blocked_by_layer7" if trigger else ("abandoned" if false_cancel else "completed")
    base_ms = 38000 + _h(p["id"], entry["stimulus_id"], "ms") % 12000 + (POSITIVE_CONTROL_MS if arm == "B" and mechanism != "M2" else 0)
    return {"participant_opaque_id": p["id"], "role_group": p["role_group"], "language_stratum": p["language_stratum"], "sequence": p["sequence"],
            "period": period, "arm": arm, "device_type": device, "mechanism_id": mechanism, "scenario_id": entry["stimulus_id"], "scenario_code": code,
            "trial_order": order_index, "stimulus_hash_sha256": entry["sha256"],
            "declared_envelope": {"declared_modality": declared if code != "E1" else None, "selection_origin": origin,
                                  "declared_mime_type": descriptor["declared_mime_type"], "declared_extension": descriptor["declared_extension"]},
            "preview_shown_ms": 1200 + _h(p["id"], entry["stimulus_id"], "pv") % 800 if arm == "B" and code != "E1" else None,
            "initial_modality": declared, "chosen_modality": chosen, "modality_change_count": 0,
            "modality_changed_after_preview": bool(arm == "B" and wrong_selection), "confirmation_clicked": confirmed,
            "comprehension_correct": (True if trigger else None), "layer7_execution_mode": alt_b.HARNESS_MODE if arm == "B" else alt_b.NOT_APPLICABLE_ARM_A,
            "layer7_trigger_code": trigger if arm == "B" else None, "layer7_subreason_code": subreason if arm == "B" else None,
            "recovery_outcome": recovery if arm == "B" else "not_applicable", "outcome_status": outcome if arm == "B" or mechanism != "M2" else "completed",
            "task_duration_ms": base_ms}, source


def run(manifest, directory=bank.STIMULI_DIR, count=4, seed="r24"):
    by_set = {1: {}, 2: {}}
    for s in manifest["stimuli"]:
        by_set[s["set_id"]][s["pair_id"]] = s
    records, sources = [], {}
    for p in participants(count, seed):
        sets = (1, 2) if (int(p["id"][-2:]) // 2) % 2 == 0 else (2, 1)           # counterbalance Set 1 / Set 2 between periods
        arms = ("A", "B") if p["sequence"] == "AB" else ("B", "A")
        devices = (p["device_first"], "desktop_web" if p["device_first"] == "mobile_narrow" else "mobile_narrow")
        for period in (1, 2):
            order = trial_order(seed, p["id"], period)
            for index, pair in enumerate(order, start=1):
                entry = by_set[sets[period - 1]][pair]
                record, source = run_trial(p, arms[period - 1], period, devices[period - 1], index, entry, directory)
                records.append(record)
                sources[source] = sources.get(source, 0) + 1
    return records, sources


def full_dry_run(resamples=hf.DEFAULT_RESAMPLES, count=4, seed="r24", git_commit_sha=None):
    manifest = bank.build_manifest()
    problems = bank.verify_bank(manifest)
    records, sources = run(manifest, count=count, seed=seed)
    document = alt_b.export_alt_b(records, manifest, resamples, seed, git_commit_sha)
    alt_b.validate_export(document, records, manifest)
    return {"bank_problems": problems, "bank_status": bank.status_counts(manifest), "participants": count, "tasks_per_participant": len(records) // count,
            "records": len(records), "descriptor_sources": sources, "export": document, "records_data": records, "manifest": manifest}
