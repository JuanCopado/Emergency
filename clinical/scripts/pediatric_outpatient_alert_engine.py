#!/usr/bin/env python3
"""Central pediatric outpatient medication safety alert engine."""

import json
import re
from pathlib import Path

ROOT=Path(__file__).parents[1]
RULES=ROOT/"qa"/"pediatric-outpatient-alert-rules.json"
REGISTRY=ROOT/"qa"/"pediatric-outpatient-medications.json"

SEVERITY_ORDER={"STOP":4,"ALERT":3,"CAUTION":2,"INFO":1}

def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _norm(value):
    return re.sub(r"[^a-z0-9]+"," ",str(value).strip().lower()).strip()

def _med_name(item):
    if isinstance(item,str): return _norm(item)
    if isinstance(item,dict): return _norm(item.get("name") or item.get("drug") or item.get("active_ingredient") or "")
    return ""

def _med_classes(item):
    if isinstance(item,dict):
        vals=item.get("classes") or item.get("class") or []
        if isinstance(vals,str): vals=[vals]
        return {_norm(v).replace(" ","_") for v in vals}
    return set()

def _allergy_parts(item):
    if isinstance(item,str):
        return {"substance":_norm(item),"class":"","phenotype":"","severity":"","confirmed":False}
    if isinstance(item,dict):
        return {
          "substance":_norm(item.get("substance") or item.get("drug") or item.get("name") or ""),
          "class":_norm(item.get("class") or "").replace(" ","_"),
          "phenotype":_norm(item.get("phenotype") or item.get("reaction_type") or "").replace(" ","_"),
          "severity":_norm(item.get("severity") or "").replace(" ","_"),
          "confirmed":bool(item.get("confirmed",False)),
        }
    return {"substance":"","class":"","phenotype":"","severity":"","confirmed":False}

def _entry(registry,regimen_id):
    for e in registry["entries"]:
        if e["id"]==regimen_id:return e
    raise ValueError("unknown pediatric outpatient regimen: "+regimen_id)

def _drug_classes(drug,rules):
    out=set()
    nd=_norm(drug)
    for cls,drugs in rules.get("drug_classes",{}).items():
        if any(_norm(d)==nd for d in drugs): out.add(cls)
    return out

def _match_med(rule_med, active_name):
    a=_norm(rule_med); b=_norm(active_name)
    return a==b or (a and b and (a in b or b in a))

def _alert(severity,code,message,action,source_url=None,details=None):
    return {
      "severity":severity,"code":code,"message":message,"action":action,
      "source_url":source_url,"details":details or {}
    }

def evaluate(regimen_id, patient, active_medications=None, registry=None, rules=None):
    registry=registry or _load(REGISTRY)
    rules=rules or _load(RULES)
    e=_entry(registry,regimen_id)
    drug=e["drug"]
    drug_norm=_norm(drug)
    classes=_drug_classes(drug,rules)
    alerts=[]

    allergies=patient.get("allergies") or []
    for raw in allergies:
        a=_allergy_parts(raw)
        if a["substance"] and (a["substance"]==drug_norm or a["substance"] in drug_norm or drug_norm in a["substance"]):
            alerts.append(_alert("STOP","ALLERGY_EXACT",
              f"Recorded allergy matches {drug}.",
              "Do not prescribe until the allergy record is clarified or an alternative is chosen.",
              details={"allergy":raw}))
        cls=rules.get("class_aliases",{}).get(a["class"],a["class"])
        if not cls and a["substance"]:
            alias_key=a["substance"].replace(" ","_")
            cls=rules.get("class_aliases",{}).get(alias_key,"")
        if cls=="beta_lactam" and ({"penicillins","cephalosporins"} & classes):
            severe=a["severity"] in {"severe","anaphylaxis","life_threatening"} or a["phenotype"] in {"immediate_severe","anaphylaxis","scar","sjs","ten","dress","agep"}
            sev="STOP" if severe else "ALERT"
            alerts.append(_alert(sev,"ALLERGY_BETA_LACTAM",
              "Recorded beta-lactam allergy may conflict with this beta-lactam regimen.",
              "Review timing, phenotype and severity; immediate/severe reactions require avoidance of relevant beta-lactams.",
              "https://www.rch.org.au/clinicalguide/guideline_index/Antibiotic_prescribing_in_children_with_reported_penicillin_or_cephalosporin_allergy/",
              {"allergy":raw}))
        elif cls in classes:
            severe=a["severity"] in {"severe","anaphylaxis","life_threatening"} or a["phenotype"] in {"immediate_severe","anaphylaxis","scar","sjs","ten","dress","agep"}
            alerts.append(_alert("STOP" if severe else "ALERT","ALLERGY_CLASS",
              f"Recorded {cls} allergy may conflict with {drug}.",
              "Review allergy phenotype/severity and choose an alternative if clinically significant.",
              details={"allergy":raw,"drug_class":cls}))

        if a["substance"] in {"amoxicillin","ampicillin"} and "cephalosporins" in classes:
            severe=a["severity"] in {"severe","anaphylaxis","life_threatening"} or a["phenotype"] in {"immediate","immediate_severe","anaphylaxis","scar","sjs","ten","dress","agep"}
            alerts.append(_alert("STOP" if severe else "ALERT","ALLERGY_SHARED_SIDE_CHAIN",
              "Amoxicillin/ampicillin allergy may cross-react with cefalexin, especially with immediate/severe reactions.",
              "Avoid cefalexin in immediate/severe allergy; use alternate beta-lactam only for non-immediate non-severe reactions after review.",
              "https://www.rch.org.au/clinicalguide/guideline_index/Antibiotic_prescribing_in_children_with_reported_penicillin_or_cephalosporin_allergy/",
              {"allergy":raw}))

    active=active_medications if active_medications is not None else patient.get("active_medications") or []
    active_names=[_med_name(x) for x in active if _med_name(x)]
    active_classes=set()
    for x in active:
        active_classes |= _med_classes(x)
    for cls,members in rules.get("medication_class_members",{}).items():
        for act in active_names:
            if any(_match_med(member,act) for member in members):
                active_classes.add(cls)

    for name in active_names:
        if name==drug_norm or (name and drug_norm and (name in drug_norm or drug_norm in name)):
            alerts.append(_alert("ALERT","DUPLICATE_INGREDIENT",
              f"{drug} appears to duplicate an active medication.",
              "Confirm whether the existing medicine should be stopped, continued or replaced before prescribing.",
              details={"active_medication":name}))

    for dr in rules.get("duplicate_rules",[]):
        cls=dr["class_name"]
        if cls in classes and cls in active_classes:
            alerts.append(_alert(dr["severity"],"DUPLICATE_CLASS",
              dr["message"],"Review therapeutic duplication and cumulative dose before prescribing.",
              details={"drug_class":cls}))

    for rule in rules.get("interactions",[]):
        if _norm(rule.get("drug",""))!=drug_norm: continue
        matched=[]
        for wanted in rule.get("medications",[]):
            for act in active_names:
                if _match_med(wanted,act): matched.append(act)
        if set(rule.get("medication_classes",[])) & active_classes:
            matched.extend(sorted(set(rule.get("medication_classes",[])) & active_classes))
        if matched:
            alerts.append(_alert(rule["severity"],"DRUG_INTERACTION:"+rule["id"],
              rule["message"],rule["action"],rule.get("source_url"),{"matched":sorted(set(matched))}))

    for rule in rules.get("condition_rules",[]):
        if rule.get("drug") and _norm(rule["drug"])!=drug_norm: continue
        if rule.get("categories") and e.get("category") not in rule["categories"]: continue
        if patient.get(rule["field"])==rule.get("equals",True):
            alerts.append(_alert(rule["severity"],"CONDITION:"+rule["id"],
              rule["message"],rule["action"],rule.get("source_url"),{"field":rule["field"]}))

    if patient.get("known_renal_impairment") is True and not e.get("renal_adjustment"):
        alerts.append(_alert("ALERT","RENAL_REVIEW_REQUIRED",
          "Known renal impairment but this regimen has no encoded renal dosing rule.",
          "Check the exact product SmPC/renal dosing reference before prescribing."))
    if patient.get("known_hepatic_impairment") is True and not e.get("hepatic_adjustment"):
        alerts.append(_alert("ALERT","HEPATIC_REVIEW_REQUIRED",
          "Known hepatic impairment but this regimen has no encoded hepatic dosing rule.",
          "Check the exact product SmPC/hepatic dosing reference before prescribing."))

    if e.get("liquid_capable") is True and not e.get("verified_concentrations"):
        alerts.append(_alert("CAUTION","CONCENTRATION_NOT_PREVERIFIED",
          "No product concentration is pre-verified for automatic volume calculation.",
          "Verify the exact product/SmPC concentration before calculating mL."))

    seen=set(); dedup=[]
    for a in alerts:
        key=(a["severity"],a["code"],a["message"])
        if key not in seen:
            seen.add(key); dedup.append(a)
    dedup.sort(key=lambda x:(-SEVERITY_ORDER[x["severity"]],x["code"]))
    counts={k:sum(1 for a in dedup if a["severity"]==k) for k in SEVERITY_ORDER}
    return {
      "regimen_id":regimen_id,"drug":drug,"alerts":dedup,"counts":counts,
      "blocked":counts["STOP"]>0,
      "highest_severity":next((s for s in ("STOP","ALERT","CAUTION","INFO") if counts[s]>0),None),
      "prescription_status":"BLOCKED" if counts["STOP"] else ("REVIEW_REQUIRED" if counts["ALERT"] else "OK_WITH_CAUTIONS" if counts["CAUTION"] else "OK")
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("regimen_id"); p.add_argument("patient_json"); p.add_argument("--active-medications-json")
    a=p.parse_args()
    patient=json.loads(Path(a.patient_json).read_text())
    active=json.loads(Path(a.active_medications_json).read_text()) if a.active_medications_json else None
    print(json.dumps(evaluate(a.regimen_id,patient,active),indent=2,ensure_ascii=False))
