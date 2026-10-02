#!/usr/bin/env python3
"""Fail-closed admission gate for candidate real-image dataset sources.

A registry may contain pending candidates. QA fails only for malformed entries or
when a source is declared intake_ready=true without satisfying every required gate.
"""

import argparse
import json
from pathlib import Path

REQUIRED_TRUE = (
    "license_or_dua_verified",
    "redistribution_rule_documented",
    "deidentified_source",
    "reference_strategy_prespecified",
    "label_separation_plan",
)

def validate_source(source):
    errors = []
    pending = []
    sid = source.get("id", "<unknown>")
    for field in ("id", "modality", "official_url", "access_model", "license_or_dua"):
        if not source.get(field):
            errors.append(f"{sid}: {field} required")
    for field in REQUIRED_TRUE:
        if source.get(field) is not True:
            pending.append(field)

    derived_ready = not pending and not errors
    declared_ready = source.get("intake_ready")
    if declared_ready not in (True, False):
        errors.append(f"{sid}: intake_ready must be boolean")
    elif declared_ready is True and not derived_ready:
        errors.append(
            f"{sid}: intake_ready=true but pending gates remain: {', '.join(pending)}"
        )
    elif declared_ready is False and derived_ready:
        errors.append(
            f"{sid}: all admission gates are satisfied; set intake_ready=true or document a new blocking gate"
        )
    return errors, pending, derived_ready

def validate_registry(data):
    errors = []
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        return {
            "errors": ["sources must be a non-empty list"],
            "ready_sources": [],
            "pending_sources": [],
            "source_count": 0,
        }

    seen = set()
    ready = []
    pending_sources = []
    for source in sources:
        sid = source.get("id")
        if sid in seen:
            errors.append(f"duplicate source id: {sid}")
        seen.add(sid)

        item_errors, pending, derived_ready = validate_source(source)
        errors.extend(item_errors)
        if derived_ready and source.get("intake_ready") is True:
            ready.append(sid)
        else:
            pending_sources.append({"id": sid, "pending_gates": pending})

    return {
        "errors": errors,
        "ready_sources": sorted(ready),
        "pending_sources": pending_sources,
        "source_count": len(sources),
    }

def require_ready_source(data, source_id):
    registry = validate_registry(data)
    errors = list(registry["errors"])
    source = next((x for x in data.get("sources", []) if x.get("id") == source_id), None)
    if source is None:
        errors.append(f"unknown source id: {source_id}")
    elif source.get("intake_ready") is not True:
        errors.append(f"{source_id}: source is not intake-ready")
    return {
        "errors": errors,
        "source_id": source_id,
        "intake_ready": not errors,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("registry", type=Path)
    p.add_argument("--require-ready-source")
    args = p.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    result = (
        require_ready_source(data, args.require_ready_source)
        if args.require_ready_source
        else validate_registry(data)
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
