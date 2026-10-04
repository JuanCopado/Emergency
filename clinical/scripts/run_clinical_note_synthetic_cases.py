#!/usr/bin/env python3
import json, tempfile, zipfile
from pathlib import Path
import sys

ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from clinical_note_support import (
    new_note, add_report, route_attachment, scan_privacy,
    validate_for_export, detect_data_quality_issues
)
from clinical_note_exporter import export_docx, export_pdf
from final_human_review_gate import build_review_queue

CASES=ROOT/"qa"/"clinical-note-synthetic-cases.json"

def base_note():
    n=new_note(age_years=68,sex="female",language="pt-PT")
    n["history"]["chief_complaint"]="Dor torácica e dispneia."
    n["history"]["present_illness"]="Sintomas com 3 horas de evolução, sem identificadores diretos."
    n["history"]["allergies"]=[]
    n["exam"]["vitals"]=[{"time_label":"admissão","bp":"132/78","hr":92,"rr":20,"spo2":95,"oxygen":"ar ambiente","temperature_c":36.7,"gcs":"15","source":"device_measurement"}]
    n["assessment"]["problem_representation"]="Mulher de 68 anos com dor torácica e dispneia agudas."
    n["assessment"]["active_problems"]=["Dor torácica","Dispneia"]
    n["clinician_validation"]={"reviewed":True,"reviewer_role":"physician","reviewed_at":"relative: after assessment","changes_made":None}
    n["privacy"].update({"direct_identifiers_removed":True,"free_text_screened":True,"source_metadata_checked":True,"burned_in_identifiers_checked":True,"export_allowed":True})
    return n

def run():
    spec=json.loads(CASES.read_text(encoding="utf-8"))
    errors=[]; passed=0
    for case in spec["cases"]:
        cid=case["id"]
        try:
            if cid=="safe-basic-note":
                n=base_note()
                if validate_for_export(n)["blocked"]: raise AssertionError("safe note blocked")
            elif cid=="direct-name-in-free-text":
                n=base_note(); n["history"]["present_illness"]="Nome: Maria Silva, dor torácica."
                if not scan_privacy(n): raise AssertionError("identifier not detected")
            elif cid=="direct-patient-name-field":
                n=base_note(); n["patient_name"]="Maria Silva"
                f=scan_privacy(n)
                if not any(x["code"]=="DIRECT_IDENTIFIER_FIELD" for x in f): raise AssertionError("patient_name field not blocked")
            elif cid=="external-mode-missing-source-metadata":
                n=base_note(); n["privacy"]["mode"]="external_anonymized"; n["privacy"]["source_metadata_checked"]=False
                if not validate_for_export(n)["blocked"]: raise AssertionError("external metadata gate failed")
            elif cid=="external-image-without-burned-in-check":
                n=base_note(); n["privacy"]["mode"]="external_anonymized"; n["privacy"]["burned_in_identifiers_checked"]=False
                add_report(n,"ct","ai_image_interpretation",ai_interpretation="Sem hemorragia aguda.",privacy_checked=True,burned_in_identifiers_checked=False)
                if not validate_for_export(n)["blocked"]: raise AssertionError("burned-in gate failed")
            elif cid=="ecg-routing":
                if route_attachment("ecg")["modules"]!=["ecg-image"]: raise AssertionError("ecg route")
            elif cid=="ct-routing":
                if "ct-mri-screenshot" not in route_attachment("ct")["modules"]: raise AssertionError("ct route")
            elif cid=="medication-discrepancy":
                n=base_note(); n["history"]["medication_discrepancies"]=["RSE vs lista domiciliária"]
                q=detect_data_quality_issues(n)
                if not any(x["code"]=="MEDICATION_RECONCILIATION_DISCREPANCY" for x in q): raise AssertionError("med discrepancy not detected")
            elif cid=="clinician-review-missing":
                n=base_note(); n["clinician_validation"]["reviewed"]=False
                if not validate_for_export(n)["blocked"]: raise AssertionError("clinician gate failed")
            elif cid=="official-vs-ai-provenance":
                n=base_note()
                r=add_report(n,"chest_xray","official_report",official_report="Sem pneumotórax.",ai_interpretation="Sem pneumotórax evidente.",privacy_checked=True,burned_in_identifiers_checked=True)
                if r["official_report"]==r["ai_interpretation"]: raise AssertionError("provenance collision")
                if r["provenance"]!="official_report": raise AssertionError("provenance lost")
            elif cid=="long-note-docx-pdf":
                n=base_note()
                n["history"]["present_illness"]=" ".join(["Evolução clínica complexa sem identificadores diretos."]*500)
                with tempfile.TemporaryDirectory() as td:
                    d=Path(td)/"a.docx"; p=Path(td)/"a.pdf"
                    export_docx(n,d); export_pdf(n,p)
                    if d.stat().st_size<500 or p.stat().st_size<500: raise AssertionError("exports too small")
                    with zipfile.ZipFile(d) as z:
                        if "word/document.xml" not in z.namelist(): raise AssertionError("docx malformed")
            elif cid=="yellow-review-queue":
                q=build_review_queue(ROOT)
                ev=json.loads((ROOT/"references"/"evidence-registry.json").read_text(encoding="utf-8"))
                yellow={k for k,v in ev["modules"].items() if v.get("status")=="yellow"}
                queued={x["module_id"] for x in q["queue"]}
                if yellow!=queued: raise AssertionError("yellow queue mismatch")
            else:
                raise AssertionError("unknown case")
            passed+=1
        except Exception as exc:
            errors.append(f"{cid}: {exc}")
    return {"cases":len(spec["cases"]),"passed":passed,"errors":errors}

if __name__=="__main__":
    r=run()
    print(json.dumps(r,indent=2,ensure_ascii=False))
    raise SystemExit(1 if r["errors"] else 0)
