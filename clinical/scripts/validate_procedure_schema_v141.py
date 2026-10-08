#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "procedure-v1.41.schema.json"
TEMPLATE = ROOT / "templates" / "procedure-template-v1.41.json"

def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def validate_template(schema, data):
    errors = []
    required = set(schema.get("required", []))
    missing = sorted(required - set(data))
    if missing:
        errors.append("missing required: " + ", ".join(missing))
    if data.get("status") != "YELLOW":
        errors.append("template status must default to YELLOW")
    qa = data.get("qa", {})
    if qa.get("human_review_required") is not True:
        errors.append("human_review_required must default true")
    if qa.get("visual_qa") != "paused":
        errors.append("visual_qa must default paused")
    if data.get("procedure_id") != "PROC-XXX-000":
        errors.append("template placeholder procedure_id changed")
    return errors

def main():
    schema = _load(SCHEMA)
    template = _load(TEMPLATE)
    errors = validate_template(schema, template)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("procedure schema/template: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
