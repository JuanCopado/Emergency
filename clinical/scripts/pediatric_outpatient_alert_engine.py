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

def evaluate(regimen_id, patient, active_medications=None, product=None, registry=None, rules=None):
    registry=registry or _load(REGISTRY)
    rules=rules or _load(RULES)
    e=_entry(registry,regimen_id)
    drug=e["drug"]
    drug_norm=_norm(drug)
    classes=_drug_classes(drug,rules)
    alerts=[]

    # Safety-context completeness.
    if "allergies" not in patient:
        alerts.append(_alert("ALERT","ALLERGY_STATUS_NOT_DOCUMENTED",
          "Drug-allergy status has not been explicitly reviewed for this prescription.",
          "Confirm and document drug allergies before prescribing."))
    if active_medications is None and "active_medications" not in patient:
        alerts.append(_alert("ALERT","MEDICATION_RECONCILIATION_NOT_DOCUMENTED",
          "Active medication reconciliation is missing, so interaction screening may be incomplete.",
          "Confirm current medicines, including OTC/herbal products, before prescribing."))

    # Age/weight and registry-gate preflight.
    age=patient.get("age_months")
    if (e.get("min_age_months") is not None or e.get("max_age_months") is not None) and age is None:
        alerts.append(_alert("STOP","AGE_REQUIRED","Age is required for this regimen.","Enter age before prescribing."))
    elif age is not None:
        try:
            av=float(age)
            if e.get("min_age_months") is not None and av < e["min_age_months"]:
                alerts.append(_alert("STOP","AGE_BELOW_RANGE","Patient is below the regimen minimum age.","Choose an age-appropriate regimen."))
            if e.get("max_age_months") is not None and av > e["max_age_months"]:
                alerts.append(_alert("STOP","AGE_ABOVE_RANGE","Patient is above the regimen maximum age.","Choose an age-appropriate regimen."))
        except Exception:
            alerts.append(_alert("STOP","AGE_INVALID","Age value is invalid.","Correct age before prescribing."))

    basis=e.get("weight_basis")
    required_weight_field={"actual":"actual_weight_kg","ideal":"ideal_weight_kg","adjusted":"adjusted_weight_kg"}.get(basis)
    if required_weight_field and patient.get(required_weight_field) is None:
        alerts.append(_alert("STOP","DOSING_WEIGHT_REQUIRED",
          f"{required_weight_field} is required for this regimen.",
          "Enter the required dosing weight before calculating the dose."))
    if basis in {"fixed_weight_band","device"} and any(("min_weight_kg" in b or "min_weight_kg_inclusive" in b or "max_weight_kg" in b) for b in e.get("bands",[])) and patient.get("actual_weight_kg") is None:
        alerts.append(_alert("STOP","ACTUAL_WEIGHT_REQUIRED","Actual weight is required to select the correct dose/device band.","Enter current measured weight."))

    for gate in e.get("required_patient_flags",[]):
        if patient.get(gate["field"]) != gate.get("equals",True):
            alerts.append(_alert("STOP","REQUIRED_CLINICAL_CRITERION_NOT_MET",
              gate.get("message",f"{gate['field']} must be confirmed before prescribing."),
              "Resolve the clinical criterion or choose another regimen.",details={"field":gate["field"]}))
    for gate in e.get("excluded_patient_flags",[]):
        if patient.get(gate["field"]) == gate.get("equals",True):
            alerts.append(_alert("STOP","CLINICAL_EXCLUSION_PRESENT",
              gate.get("message",f"{gate['field']} excludes this regimen."),
              "Do not use this standard regimen while the exclusion is present.",details={"field":gate["field"]}))
    for gate in e.get("minimum_patient_values",[]):
        value=patient.get(gate["field"])
        if value is None:
            alerts.append(_alert("STOP","REQUIRED_CLINICAL_VALUE_MISSING",
              gate.get("missing_message",f"{gate['field']} is required."),
              "Enter/verify the required clinical value.",details={"field":gate["field"]}))
        else:
            try:
                if float(value) < float(gate["minimum"]):
                    alerts.append(_alert("STOP","CLINICAL_VALUE_BELOW_MINIMUM",
                      gate.get("message",f"{gate['field']} is below the safe range for this regimen."),
                      "Use the alternative/adjusted pathway.",details={"field":gate["field"],"value":value}))
            except Exception:
                alerts.append(_alert("STOP","CLINICAL_VALUE_INVALID",f"{gate['field']} is invalid.","Correct the clinical value."))
    for gate in e.get("maximum_patient_values",[]):
        value=patient.get(gate["field"])
        if value is None:
            alerts.append(_alert("STOP","REQUIRED_CLINICAL_VALUE_MISSING",
              gate.get("missing_message",f"{gate['field']} is required."),
              "Enter/verify the required clinical value.",details={"field":gate["field"]}))
        else:
            try:
                if float(value) > float(gate["maximum"]):
                    alerts.append(_alert("STOP","CLINICAL_VALUE_ABOVE_MAXIMUM",
                      gate.get("message",f"{gate['field']} is above the safe range for this regimen."),
                      "Use the alternative/adjusted pathway.",details={"field":gate["field"],"value":value}))
            except Exception:
                alerts.append(_alert("STOP","CLINICAL_VALUE_INVALID",f"{gate['field']} is invalid.","Correct the clinical value."))

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
        severe=a["severity"] in {"severe","anaphylaxis","life_threatening"} or a["phenotype"] in {"immediate_severe","anaphylaxis","scar","sjs","ten","dress","agep"}
        beta_classes={"penicillins","cephalosporins"}
        if (cls=="beta_lactam" or cls in beta_classes) and (beta_classes & classes):
            same_class = cls in classes
            sev="STOP" if severe or same_class else "ALERT"
            alerts.append(_alert(sev,"ALLERGY_BETA_LACTAM",
              "Recorded beta-lactam allergy may conflict with this beta-lactam regimen.",
              "Review timing, phenotype and severity; immediate/severe reactions require avoidance of relevant beta-lactams.",
              "https://www.rch.org.au/clinicalguide/guideline_index/Antibiotic_prescribing_in_children_with_reported_penicillin_or_cephalosporin_allergy/",
              {"allergy":raw,"recorded_class":cls,"prescribed_classes":sorted(classes)}))
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
        for cls in _med_classes(x):
            active_classes.add(rules.get("class_aliases",{}).get(cls,cls))
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

    renal=e.get("renal_adjustment")
    if patient.get("known_renal_impairment") is True and renal:
        mode=renal.get("mode")
        if mode=="block_standard_regimen":
            alerts.append(_alert("STOP","RENAL_STANDARD_REGIMEN_BLOCKED",
              renal.get("message","Standard regimen is not valid in renal impairment."),
              "Use a renal-adjusted/product-specific regimen."))
        elif mode=="standard_if_egfr_at_least":
            egfr=patient.get("egfr_mL_min")
            if egfr is None:
                alerts.append(_alert("STOP","EGFR_REQUIRED","eGFR is required to assess this standard regimen.","Enter current eGFR/renal function."))
            else:
                try:
                    if float(egfr) < float(renal["minimum_egfr"]):
                        alerts.append(_alert("STOP","RENAL_THRESHOLD_FAILED",
                          renal.get("message","Renal function is below the standard-regimen threshold."),
                          "Use the renal-adjusted/product-specific regimen.",details={"egfr_mL_min":egfr}))
                except Exception:
                    alerts.append(_alert("STOP","EGFR_INVALID","eGFR value is invalid.","Correct renal function data."))
    hepatic=e.get("hepatic_adjustment")
    if patient.get("known_hepatic_impairment") is True and hepatic:
        severity=_norm(patient.get("hepatic_severity",""))
        if hepatic.get("mode")=="block_standard_regimen":
            alerts.append(_alert("STOP","HEPATIC_STANDARD_REGIMEN_BLOCKED",
              hepatic.get("message","Standard regimen is not valid in hepatic impairment."),
              "Use a product-specific/adjusted regimen."))
        elif hepatic.get("block_if_severe") and severity=="severe":
            alerts.append(_alert("STOP","HEPATIC_SEVERE_BLOCK",
              hepatic.get("message","Severe hepatic impairment blocks this regimen."),
              "Use an alternative/product-specific regimen."))

    if patient.get("known_renal_impairment") is True and not e.get("renal_adjustment"):
        alerts.append(_alert("ALERT","RENAL_REVIEW_REQUIRED",
          "Known renal impairment but this regimen has no encoded renal dosing rule.",
          "Check the exact product SmPC/renal dosing reference before prescribing."))
    if patient.get("known_hepatic_impairment") is True and not e.get("hepatic_adjustment"):
        alerts.append(_alert("ALERT","HEPATIC_REVIEW_REQUIRED",
          "Known hepatic impairment but this regimen has no encoded hepatic dosing rule.",
          "Check the exact product SmPC/hepatic dosing reference before prescribing."))

    if product is not None and product.get("concentration_mg_per_ml") is not None:
        try:
            conc=float(product["concentration_mg_per_ml"])
            allowed=[float(x["mg_per_ml"]) for x in e.get("verified_concentrations",[]) if x.get("mg_per_ml") is not None]
            if conc<=0:
                alerts.append(_alert("STOP","PRODUCT_CONCENTRATION_INVALID","Product concentration must be >0.","Verify the exact product concentration."))
            elif allowed and not any(abs(conc-x)<1e-9 for x in allowed) and product.get("external_concentration_verified") is not True:
                alerts.append(_alert("STOP","PRODUCT_CONCENTRATION_MISMATCH",
                  "Selected liquid concentration is not one of the verified concentrations for this regimen.",
                  "Verify the exact product/SmPC or explicitly mark an externally verified concentration.",
                  details={"selected_mg_per_ml":conc,"verified_mg_per_ml":allowed}))
        except Exception:
            alerts.append(_alert("STOP","PRODUCT_CONCENTRATION_INVALID","Product concentration is invalid.","Verify the exact product concentration."))
    elif e.get("liquid_capable") is True:
        alerts.append(_alert("CAUTION","PRODUCT_CONCENTRATION_REQUIRED",
          "A liquid-capable regimen has no selected product concentration, so mL cannot be safely calculated.",
          "Select and verify the exact product concentration before finalizing the prescription."))

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
    p.add_argument("regimen_id"); p.add_argument("patient_json"); p.add_argument("--active-medications-json"); p.add_argument("--product-json")
    a=p.parse_args()
    patient=json.loads(Path(a.patient_json).read_text())
    active=json.loads(Path(a.active_medications_json).read_text()) if a.active_medications_json else None
    product=json.loads(Path(a.product_json).read_text()) if a.product_json else None
    print(json.dumps(evaluate(a.regimen_id,patient,active,product=product),indent=2,ensure_ascii=False))
