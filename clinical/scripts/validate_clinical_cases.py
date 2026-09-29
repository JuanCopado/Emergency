#!/usr/bin/env python3
"""Validate provenance and safety invariants for sourced clinical regressions."""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from validate_modules import validate as validate_modules


REQUIRED_CASE_FIELDS = {
    "id", "prompt", "expected_modules", "must_do", "must_not_do", "source"
}
REQUIRED_SOURCE_FIELDS = {"organization", "title", "year", "url"}


def validate(root: Path):
    payload = json.loads(
        (root / "tests/clinical-validation-cases.json").read_text(encoding="utf-8")
    )
    manifest, module_errors = validate_modules(root)
    errors = list(module_errors)
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        return [], errors + ["clinical validation case list is empty"]

    seen = set()
    for index, case in enumerate(cases):
        label = case.get("id", f"case-{index}") if isinstance(case, dict) else f"case-{index}"
        if not isinstance(case, dict):
            errors.append(f"{label}: case must be an object")
            continue
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
            continue
        if label in seen:
            errors.append(f"{label}: duplicate id")
        seen.add(label)
        for field in ("expected_modules", "must_do", "must_not_do"):
            values = case[field]
            if not isinstance(values, list) or not values or not all(
                    isinstance(value, str) and value.strip() for value in values):
                errors.append(f"{label}: {field} must be a non-empty string list")
        for module_id in case["expected_modules"]:
            if module_id not in manifest:
                errors.append(f"{label}: unknown module {module_id}")
        source = case["source"]
        if not isinstance(source, dict) or REQUIRED_SOURCE_FIELDS - set(source):
            errors.append(f"{label}: incomplete source provenance")
        else:
            parsed = urlparse(str(source["url"]))
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{label}: source URL must be absolute HTTPS")
    return cases, errors


if __name__ == "__main__":
    skill_root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1])
    validated_cases, problems = validate(skill_root)
    if problems:
        print("CLINICAL CASE VALIDATION FAILED")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print(f"CLINICAL CASE VALIDATION PASSED: {len(validated_cases)} sourced regressions")
