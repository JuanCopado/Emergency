#!/usr/bin/env python3
import json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
REG=ROOT/"references"/"visual-asset-sources.json"
REQUIRED={"procedure_id","source_url","source_title","source_organization","license","attribution_text","intended_use","clinical_qa_status","visual_qa_status"}

def validate(data):
    errors=[]
    for i,a in enumerate(data.get("assets",[])):
        missing=sorted(REQUIRED-set(a))
        if missing:
            errors.append(f"asset[{i}] missing: {', '.join(missing)}")
        if a.get("intended_use")=="final_reuse":
            if a.get("license") in {None,"","unknown"}:
                errors.append(f"asset[{i}] final_reuse has unknown license")
            if a.get("commercial_use_allowed") is False and a.get("project_use")=="commercial":
                errors.append(f"asset[{i}] commercial use conflicts with license")
    return errors

def main():
    data=json.loads(REG.read_text(encoding="utf-8"))
    errors=validate(data)
    if errors:
        print("\n".join(errors),file=sys.stderr)
        return 1
    print("visual asset metadata: PASS")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
