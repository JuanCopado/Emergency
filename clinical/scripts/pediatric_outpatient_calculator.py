#!/usr/bin/env python3
"""Deterministic pediatric outpatient/home medication calculator.

Safety contract:
- Drug/regimen selection remains diagnosis-specific and comes from the registry.
- Weight basis is explicit: actual, ideal, adjusted, fixed age/weight band, or device.
- Adult/source maximums are always applied.
- Liquid volume is returned ONLY after a verified product concentration is supplied.
- Drop counts are returned ONLY for an exact product with a verified drop factor (mg/drop or drops/mL).
- The engine never substitutes one concentration or drop factor for another.
"""

import json
import math
from pathlib import Path
from pediatric_outpatient_alert_engine import evaluate as evaluate_alerts

REGISTRY = Path(__file__).parents[1] / "qa" / "pediatric-outpatient-medications.json"

class MedicationSafetyStop(ValueError):
    """Raised when the central alert engine detects a STOP-level medication conflict."""
    def __init__(self, alert_result):
        self.alert_result=alert_result
        messages=" | ".join(a["message"] for a in alert_result.get("alerts",[]) if a.get("severity")=="STOP")
        super().__init__("medication safety STOP: "+messages)

def preflight(regimen_id, patient, active_medications=None, product=None, registry=None):
    registry=registry or load_registry()
    return evaluate_alerts(regimen_id,patient,active_medications=active_medications,product=product,registry=registry)

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

def _matched_verified_concentration(entry, concentration_mg_per_ml):
    conc=_num(concentration_mg_per_ml,"concentration_mg_per_ml")
    for item in entry.get("verified_concentrations",[]):
        value=item.get("mg_per_ml")
        if value is not None and abs(float(value)-conc)<1e-9:
            return item
    return None

def _drops(dose_mg, volume_ml, product, entry):
    """Return drop-device conversion only when the exact drop factor is verified.

    Never infer a universal drops/mL value. Prefer registry metadata for the
    exact concentration. External factors require explicit verification plus
    exact product identity and source URL.
    """
    if not product:
        return None
    factor_source=None
    mg_per_drop=None
    drops_per_ml=None
    matched=None
    if product.get("concentration_mg_per_ml") is not None:
        matched=_matched_verified_concentration(entry,product["concentration_mg_per_ml"])
    if matched:
        mg_per_drop=matched.get("mg_per_drop")
        drops_per_ml=matched.get("drops_per_ml")
        if mg_per_drop is not None or drops_per_ml is not None:
            factor_source="registry_verified_exact_product"
    if mg_per_drop is None and drops_per_ml is None:
        if product.get("external_drop_factor_verified") is not True:
            return None
        if not product.get("exact_product_name") or not product.get("drop_factor_source_url"):
            raise ValueError("external drop factor requires exact_product_name and drop_factor_source_url")
        mg_per_drop=product.get("mg_per_drop")
        drops_per_ml=product.get("drops_per_ml")
        if mg_per_drop is None and drops_per_ml is None:
            raise ValueError("external_drop_factor_verified requires mg_per_drop or drops_per_ml")
        factor_source="externally_verified_exact_product"
    if mg_per_drop is not None:
        mg_per_drop=_num(mg_per_drop,"mg_per_drop")
        if mg_per_drop<=0:
            raise ValueError("mg_per_drop must be >0")
        exact=float(dose_mg)/mg_per_drop
        implied_drops_per_ml=None
        if product.get("concentration_mg_per_ml") is not None:
            implied_drops_per_ml=_num(product["concentration_mg_per_ml"],"concentration_mg_per_ml")/mg_per_drop
    else:
        drops_per_ml=_num(drops_per_ml,"drops_per_ml")
        if drops_per_ml<=0:
            raise ValueError("drops_per_ml must be >0")
        exact=float(volume_ml)*drops_per_ml
        implied_drops_per_ml=drops_per_ml
        if product.get("concentration_mg_per_ml") is not None:
            mg_per_drop=_num(product["concentration_mg_per_ml"],"concentration_mg_per_ml")/drops_per_ml
    rounded=int(math.floor(exact+0.5))
    delivered_mg=rounded*mg_per_drop if mg_per_drop is not None else None
    error_pct=None
    if delivered_mg is not None and dose_mg:
        error_pct=(delivered_mg-float(dose_mg))/float(dose_mg)*100.0
    return {
        "exact_drops": exact,
        "rounded_whole_drops": rounded,
        "mg_per_drop": mg_per_drop,
        "drops_per_ml": implied_drops_per_ml,
        "delivered_mg_at_rounded_drops": delivered_mg,
        "rounding_error_percent": error_pct,
        "factor_source": factor_source,
        "exact_product_name": product.get("exact_product_name") or (matched or {}).get("exact_product_name"),
        "drop_factor_source_url": product.get("drop_factor_source_url") or (matched or {}).get("drop_factor_source_url"),
        "warning": "Use only the verified dropper for this exact product; drops are not interchangeable between products."
    }

def _check_patient_gates(entry, patient):
    for gate in entry.get("required_patient_flags", []):
        field=gate["field"]
        expected=gate.get("equals", True)
        if patient.get(field) != expected:
            raise ValueError(gate.get("message", f"{field} must equal {expected!r}"))
    for gate in entry.get("excluded_patient_flags", []):
        field=gate["field"]
        excluded=gate.get("equals", True)
        if patient.get(field) == excluded:
            raise ValueError(gate.get("message", f"{field} is an exclusion for this regimen"))
    for gate in entry.get("minimum_patient_values", []):
        field=gate["field"]
        if patient.get(field) is None:
            raise ValueError(gate.get("missing_message", f"{field} required"))
        value=_num(patient[field],field)
        if value < gate["minimum"]:
            raise ValueError(gate.get("message", f"{field} below minimum"))
    for gate in entry.get("maximum_patient_values", []):
        field=gate["field"]
        if patient.get(field) is None:
            raise ValueError(gate.get("missing_message", f"{field} required"))
        value=_num(patient[field],field)
        if value > gate["maximum"]:
            raise ValueError(gate.get("message", f"{field} above maximum"))

def _check_organ_function_gates(entry, patient):
    renal=entry.get("renal_adjustment")
    if renal and patient.get("known_renal_impairment") is True:
        mode=renal.get("mode")
        if mode=="standard_if_egfr_at_least":
            if patient.get("egfr_mL_min") is None:
                raise ValueError("egfr_mL_min required when known renal impairment is present")
            egfr=_num(patient["egfr_mL_min"],"egfr_mL_min")
            if egfr < renal["minimum_egfr"]:
                raise ValueError(renal.get("message","standard regimen is not valid below the renal threshold"))
        elif mode=="block_standard_regimen":
            raise ValueError(renal.get("message","standard regimen requires renal dose individualization"))
        elif mode=="none_required":
            pass
    hepatic=entry.get("hepatic_adjustment")
    if hepatic and patient.get("known_hepatic_impairment") is True:
        severity=str(patient.get("hepatic_severity","")).strip().lower()
        mode=hepatic.get("mode")
        if mode=="block_standard_regimen":
            raise ValueError(hepatic.get("message","standard regimen requires hepatic dose individualization"))
        if hepatic.get("block_if_severe") and severity=="severe":
            raise ValueError(hepatic.get("message","standard regimen is not valid in severe hepatic impairment"))

def calculate(regimen_id, patient, product=None, selected_dose_per_kg=None, selected_duration_days=None, selected_volume_ml=None, registry=None, active_medications=None):
    registry=registry or load_registry()
    safety=preflight(regimen_id,patient,active_medications=active_medications,product=product,registry=registry)
    if safety["blocked"]:
        raise MedicationSafetyStop(safety)
    e=_entry(registry,regimen_id)
    _check_age(e,patient)
    _check_patient_gates(e,patient)
    _check_organ_function_gates(e,patient)
    result={
      "regimen_id":regimen_id,"drug":e["drug"],"diagnosis":e["diagnosis"],"route":e.get("route","PO"),
      "weight_basis":e.get("weight_basis"),"frequency":e.get("frequency"),
      "administration":e.get("administration"),"contraindications":e.get("contraindications",[]),
      "cautions":e.get("cautions",[]),"renal_adjustment":e.get("renal_adjustment"),
      "hepatic_adjustment":e.get("hepatic_adjustment"),"source":e.get("source"),"source_url":e.get("source_url"),
      "medication_safety":safety,"prescription_status":safety["prescription_status"],
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
        if dose is None and band.get("dose_mg_per_kg") is not None:
            w=_num(patient.get("actual_weight_kg"),"actual_weight_kg")
            dose=_apply_max(_num(band["dose_mg_per_kg"],"dose_mg_per_kg")*w,{**e,"max_mg_per_dose":band.get("max_mg_per_dose",e.get("max_mg_per_dose"))})
            result["dosing_weight_kg"]=w
            result["dose_mg_per_kg"]=band["dose_mg_per_kg"]
        doses_per_day=band.get("doses_per_day",doses_per_day)
        band_duration=band.get("duration_days",duration)
        if isinstance(band_duration,list):
            if selected_duration_days is None:
                raise ValueError(f"duration selection required within {band_duration}")
            if selected_duration_days < band_duration[0] or selected_duration_days > band_duration[1]:
                raise ValueError("selected_duration_days outside source range")
            duration=selected_duration_days
        else:
            duration=band_duration
        result["matched_band"]=band
        if dose is not None: result["dose_mg"]=dose
    elif model=="schedule_by_day":
        w=_weight(e,patient)
        schedule=[]
        course_doses=0
        course_ml=0.0
        for phase in e["schedule"]:
            perkg=phase["dose_mg_per_kg"]
            phase_dose=_apply_max(perkg*w,{**e,"max_mg_per_dose":phase.get("max_mg_per_dose")})
            phase_out={**phase,"dose_mg":phase_dose}
            phase_days=int(phase.get("days",1))
            phase_doses_per_day=int(phase.get("doses_per_day",1))
            phase_out["total_phase_doses"]=phase_days*phase_doses_per_day
            course_doses += phase_out["total_phase_doses"]
            if product is not None and product.get("concentration_mg_per_ml") is not None:
                vol=_volume(
                    phase_dose,product["concentration_mg_per_ml"],e,
                    verified_external=product.get("external_concentration_verified") is True
                )
                phase_out["volume_per_dose"]=vol
                drop_out=_drops(phase_dose,vol["exact_ml"],product,e)
                if drop_out is not None:
                    phase_out["drops_per_dose"]=drop_out
                elif product.get("form") in {"oral_drops","drops","drop_solution"}:
                    phase_out["drops_status"]="verified_exact_product_drop_factor_required"
                phase_out["estimated_phase_ml"]=vol["exact_ml"]*phase_out["total_phase_doses"]
                course_ml += phase_out["estimated_phase_ml"]
            schedule.append(phase_out)
        result.update({"dosing_weight_kg":w,"schedule":schedule,"total_doses":course_doses})
        if product is not None and product.get("concentration_mg_per_ml") is not None:
            result["estimated_total_course_ml"]=course_ml
        elif e.get("liquid_capable",False):
            result["volume_status"]="concentration_required_for_ml"
    elif model=="fixed_schedule":
        schedule=[]
        course_doses=0
        course_ml=0.0
        w=None
        for phase in e["schedule"]:
            if phase.get("dose_mg") is not None:
                phase_dose=_apply_max(_num(phase["dose_mg"],"dose_mg"),{**e,"max_mg_per_dose":phase.get("max_mg_per_dose",e.get("max_mg_per_dose"))})
            elif phase.get("dose_mg_per_kg") is not None:
                if w is None:
                    w=_weight(e,patient)
                phase_dose=_apply_max(_num(phase["dose_mg_per_kg"],"dose_mg_per_kg")*w,{**e,"max_mg_per_dose":phase.get("max_mg_per_dose",e.get("max_mg_per_dose"))})
            else:
                raise ValueError("fixed_schedule phase requires dose_mg or dose_mg_per_kg")
            phase_out={**phase,"dose_mg":phase_dose}
            phase_doses=int(phase.get("total_phase_doses",phase.get("doses",1)))
            phase_out["total_phase_doses"]=phase_doses
            course_doses += phase_doses
            if product is not None and product.get("concentration_mg_per_ml") is not None:
                vol=_volume(
                    phase_dose,product["concentration_mg_per_ml"],e,
                    verified_external=product.get("external_concentration_verified") is True
                )
                phase_out["volume_per_dose"]=vol
                drop_out=_drops(phase_dose,vol["exact_ml"],product,e)
                if drop_out is not None:
                    phase_out["drops_per_dose"]=drop_out
                elif product.get("form") in {"oral_drops","drops","drop_solution"}:
                    phase_out["drops_status"]="verified_exact_product_drop_factor_required"
                phase_out["estimated_phase_ml"]=vol["exact_ml"]*phase_doses
                course_ml += phase_out["estimated_phase_ml"]
            schedule.append(phase_out)
        result["schedule"]=schedule
        result["total_doses"]=course_doses
        if w is not None:
            result["dosing_weight_kg"]=w
        if product is not None and product.get("concentration_mg_per_ml") is not None:
            result["estimated_total_course_ml"]=course_ml
        elif e.get("liquid_capable",False):
            result["volume_status"]="concentration_required_for_ml"
    elif model=="fixed_dose":
        dose=_apply_max(_num(e["fixed_dose_mg"],"fixed_dose_mg"),e)
        result["dose_mg"]=dose
    elif model=="fixed_volume_band":
        band=_fixed_band(e,patient)
        if band.get("dose_ml") is not None:
            volume_ml=_num(band["dose_ml"],"dose_ml")
        else:
            lo,hi=band["dose_ml_range"]
            if selected_volume_ml is None:
                raise ValueError(f"volume selection required within {lo}-{hi} mL")
            volume_ml=_num(selected_volume_ml,"selected_volume_ml")
            if volume_ml<lo or volume_ml>hi:
                raise ValueError("selected_volume_ml outside source range")
        doses_per_day=band.get("doses_per_day",doses_per_day)
        duration=band.get("duration_days",duration)
        result["matched_band"]=band
        result["volume_per_dose"]={"exact_ml":volume_ml,"rounded_0_1_ml":round(volume_ml+1e-12,1),"concentration_mg_per_ml":None}
        result["dose_unit"]="mL"
    elif model=="volume_ml_per_kg_course":
        w=_num(patient.get("actual_weight_kg"),"actual_weight_kg")
        perkg=_num(e["volume_ml_per_kg"],"volume_ml_per_kg")
        total_volume=w*perkg
        hours=_num(e["administration_hours"],"administration_hours")
        result.update({"dosing_weight_kg":w,"total_rehydration_ml":total_volume,"administration_hours":hours,"target_ml_per_hour":total_volume/hours})
        dose=None
    elif model=="sachet_schedule":
        band=_fixed_band(e,patient)
        result["matched_band"]=band
        result["sachets_per_day"]=band.get("sachets_per_day")
        result["sachet_schedule"]=band.get("schedule")
        duration=band.get("duration_days",duration)
        result["dose_unit"]="sachet"
    elif model=="device":
        band=_fixed_band(e,patient)
        result["device"]=band
    elif model=="topical":
        result["instructions"]=e["topical_instructions"]
        for field in (
            "drops_per_dose","doses_per_day_range","volume_per_administration_ml",
            "applications_per_day","repeat_after_days","product_strength"
        ):
            if e.get(field) is not None:
                result[field]=e[field]
    else:
        raise ValueError("unsupported dose_model")

    if dose is not None and product is not None and product.get("concentration_mg_per_ml") is not None:
        vol=_volume(
          dose,product["concentration_mg_per_ml"],e,
          verified_external=product.get("external_concentration_verified") is True
        )
        result["volume_per_dose"]=vol
        drop_out=_drops(dose,vol["exact_ml"],product,e)
        if drop_out is not None:
            result["drops_per_dose"]=drop_out
        elif product.get("form") in {"oral_drops","drops","drop_solution"}:
            result["drops_status"]="verified_exact_product_drop_factor_required"

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
    p.add_argument("--dose-per-kg",type=float); p.add_argument("--duration-days",type=int); p.add_argument("--volume-ml",type=float); p.add_argument("--active-medications-json")
    a=p.parse_args()
    patient=json.loads(Path(a.patient_json).read_text())
    product=json.loads(Path(a.product_json).read_text()) if a.product_json else None
    active=json.loads(Path(a.active_medications_json).read_text()) if a.active_medications_json else None
    print(json.dumps(calculate(a.regimen_id,patient,product,a.dose_per_kg,a.duration_days,a.volume_ml,active_medications=active),indent=2,ensure_ascii=False))
