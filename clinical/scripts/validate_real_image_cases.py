#!/usr/bin/env python3
"""Validate provenance and leakage boundaries for published image cases."""

import json
import sys
from pathlib import Path


def validate(root: Path):
    path = root / "tests" / "real-image-cases.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if not data.get("require_blinded_for_metrics"):
        errors.append("published source-known cases must require blinding for metrics")
    for case in data.get("cases", []):
        case_id = case.get("id", "unknown")
        source = case.get("source", {})
        evaluation = case.get("evaluation", {})
        for field in ("article_url", "image_url", "reference_standard", "license"):
            if not source.get(field):
                errors.append(f"{case_id}: missing source.{field}")
        if not isinstance(source.get("redistribution_permitted"), bool):
            errors.append(f"{case_id}: redistribution permission must be explicit")
        if evaluation.get("mode") not in {"blinded", "unblinded"}:
            errors.append(f"{case_id}: invalid evaluation mode")
        if not isinstance(evaluation.get("annotated"), bool):
            errors.append(f"{case_id}: annotated status must be explicit")
        if not case.get("reference") or not case.get("prediction"):
            errors.append(f"{case_id}: missing reference or recorded prediction")
        if not case.get("workflow_check"):
            errors.append(f"{case_id}: missing workflow check")
    return data.get("cases", []), errors


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1])
    cases, errors = validate(root)
    print(json.dumps({"cases": len(cases), "errors": errors}, indent=2))
    raise SystemExit(bool(errors))
