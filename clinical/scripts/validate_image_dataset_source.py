#!/usr/bin/env python3
"""Fail-closed admission gate for candidate real-image dataset sources."""

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
    for field in ("id", "modality", "official_url", "access_model", "license_or_dua"):
        if not source.get(field):
            errors.append(f"{source.get('id', '<unknown>')}: {field} required")
    for field in REQUIRED_TRUE:
        if source.get(field) is not True:
            errors.append(f"{source.get('id', '<unknown>')}: {field} must be true before real-data intake")
    derived_ready = not errors
    if source.get("intake_ready") is not derived_ready:
        errors.append(
            f"{source.get('id', '<unknown>')}: intake_ready must equal the derived gate ({derived_ready})"
        )
    return errors

def validate_registry(data):
    errors = []
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        return {"errors": ["sources must be a non-empty list"], "ready_sources": []}
    seen = set()
    ready = []
    for source in sources:
        sid = source.get("id")
        if sid in seen:
            errors.append(f"duplicate source id: {sid}")
        seen.add(sid)
        item_errors = validate_source(source)
        errors.extend(item_errors)
        if not item_errors and source.get("intake_ready") is True:
            ready.append(sid)
    return {"errors": errors, "ready_sources": sorted(ready), "source_count": len(sources)}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("registry", type=Path)
    args = p.parse_args()
    result = validate_registry(json.loads(args.registry.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(bool(result["errors"]))
