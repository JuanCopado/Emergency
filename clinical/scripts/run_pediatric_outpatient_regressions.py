#!/usr/bin/env python3
import json, math, sys
from pathlib import Path

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from pediatric_outpatient_calculator import calculate

CASES=ROOT/"qa"/"pediatric-outpatient-regression-cases.json"

def get_path(obj,path):
    cur=obj
    for part in path.split("."):
        if isinstance(cur,list):
            cur=cur[int(part)]
        else:
            cur=cur[part]
    return cur

def eq(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-9)
    return a==b

def run(path=CASES):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    errors=[]
    passed=0
    for case in data["cases"]:
        kwargs={}
        for k in ("selected_dose_per_kg","selected_duration_days","selected_volume_ml"):
            if k in case: kwargs[k]=case[k]
        try:
            out=calculate(case["regimen_id"],case["patient"],case.get("product"),**kwargs)
            if case.get("expect_error_contains"):
                errors.append(f"{case['id']}: expected error containing {case['expect_error_contains']!r}, got success")
                continue
            for path_key,expected in case.get("expect",{}).items():
                try: actual=get_path(out,path_key)
                except Exception as exc:
                    errors.append(f"{case['id']}: missing output path {path_key}: {exc}")
                    break
                if not eq(actual,expected):
                    errors.append(f"{case['id']}: {path_key} expected {expected!r}, got {actual!r}")
                    break
            else:
                passed+=1
        except Exception as exc:
            expected=case.get("expect_error_contains")
            if expected and expected.lower() in str(exc).lower():
                passed+=1
            else:
                errors.append(f"{case['id']}: unexpected error: {exc}")
    return {"cases":len(data["cases"]),"passed":passed,"errors":errors}

if __name__=="__main__":
    result=run()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(1 if result["errors"] else 0)
