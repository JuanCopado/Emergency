#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from clinical_note_support import new_note
from clinical_note_diagnostic_engine import analyze

CASES=ROOT/"qa"/"clinical-note-diagnostic-closure-cases.json"

def build(case):
    n=new_note(age_years=case.get("age_years"),sex=case.get("sex","unknown"),language="pt-PT")
    n["history"]["chief_complaint"]=case.get("chief_complaint")
    n["history"]["present_illness"]=case.get("hpi")
    n["history"]["allergies"]=[]
    if case.get("vitals"):
        v=dict(case["vitals"]); v["time_label"]="admissão"; v["source"]="device_measurement"; n["exam"]["vitals"]=[v]
    n["privacy"].update({"direct_identifiers_removed":True,"free_text_screened":True,"source_metadata_checked":True,"burned_in_identifiers_checked":True})
    return n

def run():
    spec=json.loads(CASES.read_text(encoding="utf-8"))
    errors=[]; passed=0
    for case in spec["cases"]:
        try:
            result=analyze(build(case),apply_to_note=True)
            if result["blocked"]: raise AssertionError("analysis blocked")
            assessment=result["assessment"]
            likely=[x["diagnosis"] for x in assessment["likely_diagnoses"]]
            if case["expected_likely"] not in likely:
                raise AssertionError(f"expected likely {case['expected_likely']!r}; got {likely!r}")
            modules={m for x in assessment["likely_diagnoses"] for m in x.get("source_modules",[])}
            for m in case.get("expected_modules",[]):
                if m not in modules: raise AssertionError(f"missing module {m}")
            if case.get("expected_test_contains"):
                joined=" | ".join(x["action"] for x in assessment["suggested_tests"])
                if case["expected_test_contains"].lower() not in joined.lower():
                    raise AssertionError(f"test recommendation missing {case['expected_test_contains']}")
            if case.get("expected_immediate_treatment_module"):
                if not any(case["expected_immediate_treatment_module"] in x.get("source_modules",[]) for x in assessment["treatment_suggestions"]):
                    raise AssertionError("expected treatment module missing")
            passed+=1
        except Exception as exc:
            errors.append(f"{case['id']}: {exc}")
    return {"cases":len(spec["cases"]),"passed":passed,"errors":errors}

if __name__=="__main__":
    result=run(); print(json.dumps(result,indent=2,ensure_ascii=False)); raise SystemExit(1 if result["errors"] else 0)
