#!/usr/bin/env python3
"""Deterministic pediatric outpatient/home medication calculator.

Safety contract:
- Drug/regimen selection remains diagnosis-specific and comes from the registry.
- Weight basis is explicit: actual, ideal, adjusted, fixed age/weight band, or device.
- Adult/source maximums are always applied.
- Liquid volume is returned ONLY after a verified product concentration is supplied.
- The engine never substitutes one concentration for another.
"""

import json
import math
from pathlib import Path

REGISTRY = Path(__file__).parents[1] / "qa" / "pediatric-outpatient-medications.json"

def load_registry(path=REGISTRY):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be a finite number")
    return float(v)

def _entry(registry, regimen_id):
    for x in registry.get("entries",[]):
        if x.get("id")==regimen_id:
            return x
    raise ValueError("unknown pediatric outpatient regimen: "+regimen_id)

def _weight(entry, patient):
    basis=entry.get("weight_basis")
    if basis=="actual":
        return _num(patient.get("actual_weight_kg"),"actual_weight_kg")
    if basis=="ideal":
        return _num(patient.get("ideal_weight_kg"),"ideal_weight_kg")
    if basis=="adjusted":
        return _num(patient.get("adjusted_weight_kg"),"adjusted_weight_kg")
    if basis in {"fixed_age_band","fixed_weight_band","device","topical","not_weight_based"}:
        return None
    raise ValueError("unsupported or missing weight_basis")

def _check_age(entry, patient):
    age_months=patient.get("age_months")
    if age_months is None:
        if entry.get("min_age_months") is not None or entry.get("max_age_months") is not None:
            raise ValueError("age_months required")
        return
    age=_num(age_months,"age_months")
    if entry.get("min_age_months") is not None and age < entry["min_age_months"]:
        raise ValueError("patient below regimen minimum age")
    if entry.get("max_age_months") is not None and age > entry["max_age_months"]:
        raise ValueError("patient above regimen maximum age")

def _fixed_band(entry, patient):
    age=patient.get("age_months")
    weight=patient.get("actual_weight_kg")
    for band in entry.get("bands",[]):
        ok=True
        if "min_age_months" in band: ok &= age is not None and age >= band["min_age_months"]
        if "max_age_months" in band: ok &= age is not None and age <= band["max_age_months"]
        if "min_weight_kg" in band: ok &= weight is not None and weight > band["min_weight_kg"]
        if "min_weight_kg_inclusive" in band: ok &= weight is not None and weight >= band["min_weight_kg_inclusive"]
        if "max_weight_kg" in band: ok &= weight is not None and weight <= band["max_weight_kg"]
        if ok: return band
    raise ValueError("no matching age/weight band for regimen")

def _apply_max(dose, entry):
    cap=entry.get("max_mg_per_dose")
    return min(dose,cap) if cap is not None else dose

def _volume(dose_mg, concentration_mg_per_ml, entry, verified_external=False):
    conc=_num(concentration_mg_per_ml,"concentration_mg_per_ml")
    if conc<=0: raise ValueError("concentration_mg_per_ml must be >0")
    allowed=[float(x["mg_per_ml"]) for x in entry.get("verified_concentrations",[]) if x.get("mg_per_ml") is not None]
    if allowed and not any(abs(conc-x)<1e-9 for x in allowed) and not verified_external:
        raise ValueError("concentration is not in registry; set external_concentration_verified=true only after checking the exact product/SmPC")
    exact=dose_mg/conc
    return {"exact_ml":exact,"rounded_0_1_ml":round(exact+1e-12,1),"concentration_mg_per_ml":conc}

def calculate(regimen_id, patient, product=None, selected_dose_per_kg=None, selected_duration_days=None, registry=None):
    registry=registry or load_registry()
    e=_entry(registry,regimen_id)
    _check_age(e,patient)
    result={
      "regimen_id":regimen_id,"drug":e["drug"],"diagnosis":e["diagnosis"],"route":e.get("route","PO"),
      "weight_basis":e.get("weight_basis"),"frequency":e.get("frequency"),
      "administration":e.get("administration"),"contraindications":e.get("contraindications",[]),
      "cautions":e.get("cautions",[]),"source":e.get("source"),"source_url":e.get("source_url"),
      "status":"calculated"
    }
    model=e["dose_model"]
    dose=None
    doses_per_day=e.get("doses_per_day")
    duration=e.get("duration_days")
    if isinstance(duration,list):
        if selected_duration_days is None:
            raise ValueError(f"duration selection required within {duration}")
        if selected_duration_days < duration[0] or selected_duration_days > duration[1]:
            raise ValueError("selected_duration_days outside source range")
        duration=selected_duration_days

    if model=="mg_per_kg_per_dose":
        w=_weight(e,patient)
        perkg=e.get("dose_mg_per_kg")
        if perkg is None:
            lo,hi=e["dose_mg_per_kg_range"]
            if selected_dose_per_kg is None:
                raise ValueError(f"dose selection required within {lo}-{hi} mg/kg")
            if selected_dose_per_kg<lo or selected_dose_per_kg>hi:
                raise ValueError("selected_dose_per_kg outside source range")
            perkg=selected_dose_per_kg
        dose=_apply_max(perkg*w,e)
        result.update({"dosing_weight_kg":w,"dose_mg_per_kg":perkg,"dose_mg":dose})
    elif model in {"fixed_age_band","fixed_weight_band"}:
        band=_fixed_band(e,patient)
        dose=band.get("dose_mg")
        doses_per_day=band.get("doses_per_day",doses_per_day)
        duration=band.get("duration_days",duration)
        result["matched_band"]=band
        if dose is not None: result["dose_mg"]=dose
    elif model=="schedule_by_day":
        w=_weight(e,patient)
        schedule=[]
        for phase in e["schedule"]:
            perkg=phase["dose_mg_per_kg"]
            phase_dose=_apply_max(perkg*w,{**e,"max_mg_per_dose":phase.get("max_mg_per_dose")})
            schedule.append({**phase,"dose_mg":phase_dose})
        result.update({"dosing_weight_kg":w,"schedule":schedule})
    elif model=="device":
        band=_fixed_band(e,patient)
        result["device"]=band
    elif model=="topical":
        result["instructions"]=e["topical_instructions"]
    else:
        raise ValueError("unsupported dose_model")

    if dose is not None and product is not None and product.get("concentration_mg_per_ml") is not None:
        vol=_volume(
          dose,product["concentration_mg_per_ml"],e,
          verified_external=product.get("external_concentration_verified") is True
        )
        result["volume_per_dose"]=vol

    if dose is not None and product is None and e.get("liquid_capable",False):
        result["volume_status"]="concentration_required_for_ml"

    result["doses_per_day"]=doses_per_day
    result["duration_days"]=duration
    if dose is not None and doses_per_day and duration:
        result["total_doses"]=int(doses_per_day*duration)
        if result.get("volume_per_dose"):
            result["estimated_total_course_ml"]=result["volume_per_dose"]["exact_ml"]*result["total_doses"]

    daily_limit=e.get("daily_max_mg_per_kg")
    if dose is not None and daily_limit and doses_per_day:
        w=_weight(e,patient)
        if dose*doses_per_day > daily_limit*w + 1e-9:
            raise ValueError("calculated schedule exceeds source daily mg/kg maximum")
    if dose is not None and e.get("adult_max_daily_mg") and doses_per_day:
        if dose*doses_per_day > e["adult_max_daily_mg"] + 1e-9:
            raise ValueError("calculated schedule exceeds adult/source daily maximum")

    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("regimen_id"); p.add_argument("patient_json"); p.add_argument("--product-json")
    p.add_argument("--dose-per-kg",type=float); p.add_argument("--duration-days",type=int)
    a=p.parse_args()
    patient=json.loads(Path(a.patient_json).read_text())
    product=json.loads(Path(a.product_json).read_text()) if a.product_json else None
    print(json.dumps(calculate(a.regimen_id,patient,product,a.dose_per_kg,a.duration_days),indent=2,ensure_ascii=False))
