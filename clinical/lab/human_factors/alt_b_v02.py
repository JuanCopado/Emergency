"""alt-b-0.2 · canonical vocabulary and STRICT adapter from alt-b-0.1 records. LABORATORY ONLY.

Source of the target vocabulary: the values quoted by the owner's coordination comment on PR #87 (which cites the Gemini R24 capture table).
The complete Gemini R26 canonical table was NOT received: every value below is marked with its provenance and nothing else is invented.
Rules (R27): historical records are never mutated; an ambiguous conversion is a BLOCKING error (AmbiguousConversion); coarse 0.1 outcomes
(completed / abandoned / blocked_by_layer7) are never promoted to a more specific category without events that prove the cause;
`alt-b-0.1` stays valid and untouched (alt_b.SUPPORTED_VERSIONS is not changed here).
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import alt_b  # noqa: E402

SCHEMA_VERSION = "alt-b-0.2"
SUPPORTED_SOURCE = alt_b.SCHEMA_VERSION
QUOTED = "OWNER_COMMENT_ON_PR87_QUOTING_GEMINI_R24"
INFERRED = "INFERRED_NOT_CONFIRMED"

# field -> (0.1 value -> 0.2 value, provenance). Bijective by construction (checked in the tests).
CROSSWALK = {
    "arm": ({"A": "A_legacy", "B": "B_prototype_alt_b"}, QUOTED),
    "mechanism_id": ({"M1": "M1_bypass_selection", "M2": "M2_layer7_abstention", "M3": "M3_valid_non_interference"}, QUOTED),
    "language_stratum": ({"es-ES": "ES", "pt-PT": "pt-PT", "pt-BR": "pt-BR", "en": "EN"}, QUOTED),
    "role_group": ({"medicine": "M", "nursing": "E"}, INFERRED),            # 'M/E' read as Medicina/Enfermeria: NOT stated by the source
}
DEVICE_VIEWPORTS = {360: "mobile_narrow_360", 390: "mobile_narrow_390"}
# Needed by 0.2 and absent from every 0.1 record: they must come from capture evidence, never from a default.
REQUIRED_EXTRAS = ("viewport_width", "outcome_events", "entry_flow", "transport_mode")
BLOCKED_REASON = {
    "device_type": "0.1 'mobile_narrow' does not say whether the viewport was 360 or 390 px: viewport_width is required",
    "outcome_status": "0.1 outcomes are coarse; a specific 0.2 outcome requires the closed events that prove the cause (outcome_events)",
    "entry_flow": "not captured by 0.1; must be supplied by the capture layer",
    "transport_mode": "not captured by 0.1; must be supplied by the capture layer",
    "role_group": "the M/E reading of the source is inferred, not confirmed; pass allow_inferred=True only after Gemini confirms it",
}


class AmbiguousConversion(ValueError):
    """A 0.1 -> 0.2 conversion that would need a guess. Never caught inside this module."""


def mapped(field, value, allow_inferred=False):
    table, provenance = CROSSWALK[field]
    if value not in table:
        raise AmbiguousConversion(f"{field}={value!r} is not in the 0.1 vocabulary")
    if provenance == INFERRED and not allow_inferred:
        raise AmbiguousConversion(f"role_group: {BLOCKED_REASON['role_group']}")
    return table[value]


def upgrade_record(record, extras=None, allow_inferred=False):
    """Returns a NEW 0.2 record; raises AmbiguousConversion when any field needs a guess. The input is never modified."""
    if not isinstance(record, dict) or set(record) != alt_b.RECORD_FIELDS:
        raise AmbiguousConversion("not a closed alt-b-0.1 record")
    extras = dict(extras or {})
    out = copy.deepcopy(record)
    for field in CROSSWALK:
        out[field] = mapped(field, record[field], allow_inferred)
    if record["device_type"] == "desktop_web":
        out["device_type"] = "desktop_web"
    elif record["device_type"] == "mobile_narrow":
        width = extras.get("viewport_width")
        if width not in DEVICE_VIEWPORTS:
            raise AmbiguousConversion("device_type: " + BLOCKED_REASON["device_type"])
        out["device_type"] = DEVICE_VIEWPORTS[width]
    else:
        raise AmbiguousConversion("device_type is not in the 0.1 vocabulary")
    for name in ("outcome_events", "entry_flow", "transport_mode"):
        if not extras.get(name):
            raise AmbiguousConversion(f"{'outcome_status' if name == 'outcome_events' else name}: "
                                      + BLOCKED_REASON["outcome_status" if name == "outcome_events" else name])
    out["outcome_status_v01"] = record["outcome_status"]                       # the coarse value is kept, never overwritten
    out["outcome_status"] = None                                               # the 0.2 outcome vocabulary is not available: NOT converted
    out["outcome_events"] = list(extras["outcome_events"])
    out["entry_flow"], out["transport_mode"] = extras["entry_flow"], extras["transport_mode"]
    out["schema_version"] = SCHEMA_VERSION
    out["conversion_status"] = "PARTIAL_NOT_CANONICAL_R27_V1"                   # never canonical-r27-v1: outcome_status stays None, HARD FAIL above if events are missing
    return out


def downgrade_reversible_fields(v02_record):
    """Inverse of the bijective fields only (arm, mechanism_id, language_stratum, role_group); proves reversibility, restores nothing else."""
    out = {}
    for field, (table, _) in CROSSWALK.items():
        inverse = {v: k for k, v in table.items()}
        if v02_record[field] not in inverse:
            raise AmbiguousConversion(f"{field}={v02_record[field]!r} has no 0.1 equivalent")
        out[field] = inverse[v02_record[field]]
    return out


def crosswalk_report(records):
    """Audit view, no mutation: per field, how many 0.1 records can convert deterministically and which fields block."""
    blocked = {"role_group": 0, "device_type": 0, "outcome_status": 0, "entry_flow": 0, "transport_mode": 0}
    deterministic = {field: 0 for field in CROSSWALK if CROSSWALK[field][1] != INFERRED}
    for r in records:
        for field in deterministic:
            if r[field] in CROSSWALK[field][0]:
                deterministic[field] += 1
        blocked["role_group"] += 1                                                  # every record: inferred mapping
        blocked["device_type"] += r["device_type"] == "mobile_narrow"
        for field in ("outcome_status", "entry_flow", "transport_mode"):
            blocked[field] += 1                                                     # never derivable from 0.1
    return {"records": len(records), "deterministic": deterministic, "blocked_without_extra_evidence": blocked,
            "provenance": {f: p for f, (_, p) in CROSSWALK.items()}, "schema_version_target": SCHEMA_VERSION,
            "status": "BLOCKED_PENDING_GEMINI_R26_TABLE"}
