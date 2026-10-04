#!/usr/bin/env python3
import json, sys
from pathlib import Path

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from clinical_note_support import new_note, add_report
from clinical_note_diagnostic_engine import analyze

CASES=[ROOT/"qa"/"clinical-note-diagnostic-synthetic-cases.json", ROOT/"qa"/"clinical-note-diagnostic-final-cases-a.json", ROOT/"qa"/"clinical-note-diagnostic-final-cases-b.json"]

def build(case):
    n=new_note(age_years=case.get("age_years"),sex=case.get("sex","unknown"),language="pt-PT")
    n["history"]["chief_complaint"]=case.get("chief_complaint")
    n["history"]["present_illness"]=case.get("hpi")
    n["history"]["allergies"]=[]
    if case.get("exam_respiratory"): n["exam"]["respiratory"]=case["exam_respiratory"]
    if case.get("exam_neurologic"): n["exam"]["neurologic"]=case["exam_neurologic"]
    if case.get("exam_cardiovascular"): n["exam"]["cardiovascular"]=case["exam_cardiovascular"]
    if case.get("vitals"):
        v=dict(case["vitals"]); v["time_label"]="admissão"; v["source"]="device_measurement"
        n["exam"]["vitals"]=[v]
    if case.get("ecg"):
        add_report(n,"ecg","official_report",official_report=case["ecg"],privacy_checked=True,burned_in_identifiers_checked=True)
    if case.get("labs"):
        add_report(n,"laboratory_report","laboratory_system",findings=case["labs"],privacy_checked=True,burned_in_identifiers_checked=True)
    if case.get("blood_gas"):
        add_report(n,"blood_gas_image","official_report",official_report=case["blood_gas"],privacy_checked=True,burned_in_identifiers_checked=True)
    n["privacy"].update({"direct_identifiers_removed":True,"free_text_screened":True,"source_metadata_checked":True,"burned_in_identifiers_checked":True})
    return n

def run():
    all_cases=[]
    for path in CASES:
        all_cases.extend(json.loads(path.read_text(encoding="utf-8"))["cases"])
    errors=[]; passed=0
    for case in all_cases:
        try:
            result=analyze(build(case),apply_to_note=True)
            if result["blocked"]: raise AssertionError("analysis blocked: "+json.dumps(result.get("issues",[]),ensure_ascii=False))
            assessment=result["assessment"]
            likely=[x["diagnosis"] for x in assessment["likely_diagnoses"]]
            if case["expected_likely"] not in likely:
                raise AssertionError(f"expected likely {case['expected_likely']!r}; got {likely!r}")
            modules={m for x in assessment["likely_diagnoses"] for m in x.get("source_modules",[])}
            for m in case.get("expected_modules",[]):
                if m not in modules: raise AssertionError(f"missing module {m}")
            if case.get("expected_must_not_miss"):
                names=[x["diagnosis"] for x in assessment["must_not_miss"]]
                for name in case["expected_must_not_miss"]:
                    if name not in names: raise AssertionError(f"missing must-not-miss {name}")
            if case.get("expected_test_contains"):
                joined=" | ".join(x["action"] for x in assessment["suggested_tests"])
                if case["expected_test_contains"].lower() not in joined.lower():
                    raise AssertionError(f"test recommendation missing {case['expected_test_contains']}")
            if case.get("expected_immediate_treatment_module"):
                found=False
                for x in assessment["treatment_suggestions"]:
                    if case["expected_immediate_treatment_module"] in x.get("source_modules",[]):
                        found=True; break
                if not found: raise AssertionError("expected treatment module missing")
            if result["note"]["clinician_validation"]["reviewed"] is not False:
                raise AssertionError("AI assessment did not reset clinician review")
            passed+=1
        except Exception as exc:
            errors.append(f"{case['id']}: {exc}")
    return {"cases":len(all_cases),"passed":passed,"errors":errors}

if __name__=="__main__":
    result=run()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(1 if result["errors"] else 0)
