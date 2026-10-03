#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 8 venous thromboembolism."""

import math

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)
def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

SOURCES={
 "revised-geneva":{"url":"https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005","version":"Revised Geneva 2026 guideline table"},
 "pesi":{"url":"https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005","version":"PESI"},
 "spesi":{"url":"https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005","version":"sPESI"},
 "hestia":{"url":"https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005","version":"Hestia 11 criteria"},
 "wells-dvt":{"url":"https://www.nice.org.uk/guidance/ng158/chapter/Recommendations","version":"2-level DVT Wells"},
}

def calculate_revised_geneva(data):
    req=("age","previous_dvt_pe","surgery_ga_or_lower_limb_fracture_1mo","active_cancer","unilateral_lower_limb_pain","hemoptysis","heart_rate_bpm","deep_vein_palpation_pain_and_unilateral_edema")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Revised Geneva inputs: "+", ".join(missing))
    age=_num(data["age"],"age"); hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    for k in req:
        if k not in ("age","heart_rate_bpm"): _bool(data[k],k)
    comp={
      "age_gt65":1 if age>65 else 0,
      "previous_dvt_pe":3 if data["previous_dvt_pe"] else 0,
      "surgery_or_fracture_1mo":2 if data["surgery_ga_or_lower_limb_fracture_1mo"] else 0,
      "active_cancer":2 if data["active_cancer"] else 0,
      "unilateral_lower_limb_pain":3 if data["unilateral_lower_limb_pain"] else 0,
      "hemoptysis":2 if data["hemoptysis"] else 0,
      "heart_rate":5 if hr>=95 else 3 if hr>=75 else 0,
      "deep_vein_pain_and_unilateral_edema":4 if data["deep_vein_palpation_pain_and_unilateral_edema"] else 0,
    }
    total=sum(comp.values())
    group="low" if total<=3 else "intermediate" if total<=10 else "high"
    return {"id":"revised-geneva","status":"complete","components":comp,"total":total,"risk_group":group,"source":SOURCES["revised-geneva"]}

def calculate_pesi(data):
    req=("age","sex","cancer","heart_failure","chronic_lung_disease","heart_rate_bpm","systolic_bp_mmHg","respiratory_rate","temperature_c","altered_mental_status","spo2_percent")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing PESI inputs: "+", ".join(missing))
    age=int(_num(data["age"],"age")); sex=str(data["sex"]).lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    for k in ("cancer","heart_failure","chronic_lung_disease","altered_mental_status"): _bool(data[k],k)
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); rr=_num(data["respiratory_rate"],"respiratory_rate"); temp=_num(data["temperature_c"],"temperature_c"); spo2=_num(data["spo2_percent"],"spo2_percent")
    total=age
    total+=10 if sex in {"male","m"} else 0
    total+=30 if data["cancer"] else 0
    total+=10 if data["heart_failure"] else 0
    total+=10 if data["chronic_lung_disease"] else 0
    total+=20 if hr>=110 else 0
    total+=30 if sbp<100 else 0
    total+=20 if rr>=30 else 0
    total+=20 if temp<36 else 0
    total+=60 if data["altered_mental_status"] else 0
    total+=20 if spo2<90 else 0
    klass="I" if total<=65 else "II" if total<=85 else "III" if total<=105 else "IV" if total<=125 else "V"
    return {"id":"pesi","status":"complete","total":total,"class":klass,"low_risk_class_i_ii":klass in {"I","II"},"source":SOURCES["pesi"]}

def calculate_spesi(data):
    req=("age","cancer","chronic_cardiopulmonary_disease","heart_rate_bpm","systolic_bp_mmHg","spo2_percent")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing sPESI inputs: "+", ".join(missing))
    age=_num(data["age"],"age"); hr=_num(data["heart_rate_bpm"],"heart_rate_bpm"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); spo2=_num(data["spo2_percent"],"spo2_percent")
    _bool(data["cancer"],"cancer"); _bool(data["chronic_cardiopulmonary_disease"],"chronic_cardiopulmonary_disease")
    comp={
      "age_gt80":1 if age>80 else 0,
      "cancer":1 if data["cancer"] else 0,
      "chronic_cardiopulmonary_disease":1 if data["chronic_cardiopulmonary_disease"] else 0,
      "heart_rate_ge110":1 if hr>=110 else 0,
      "sbp_lt100":1 if sbp<100 else 0,
      "spo2_lt90":1 if spo2<90 else 0,
    }
    total=sum(comp.values())
    return {"id":"spesi","status":"complete","components":comp,"total":total,"low_risk":total==0,"source":SOURCES["spesi"]}

HESTIA_KEYS=(
 "hemodynamically_unstable","thrombolysis_or_embolectomy_needed","active_bleeding_or_high_bleeding_risk",
 "oxygen_gt24h_to_keep_spo2_gt90","pe_diagnosed_during_anticoagulation","iv_pain_medication_gt24h",
 "medical_or_social_reason_hospital_gt24h","creatinine_clearance_lt30","severe_liver_impairment",
 "pregnant","history_heparin_induced_thrombocytopenia",
)
def calculate_hestia(data):
    missing=[k for k in HESTIA_KEYS if data.get(k) is None]
    if missing: raise ValueError("missing Hestia criteria: "+", ".join(missing))
    for k in HESTIA_KEYS: _bool(data[k],k)
    positive=[k for k in HESTIA_KEYS if data[k]]
    return {"id":"hestia","status":"complete","positive_criteria":positive,"positive_count":len(positive),"hestia_negative":len(positive)==0,
            "outpatient_candidate_by_hestia":len(positive)==0,
            "warning":"Hestia supports outpatient-selection after confirmed acute PE; final disposition still requires clinical judgment and local pathway.",
            "source":SOURCES["hestia"]}

WELLS_DVT_POSITIVE_KEYS=(
 "active_cancer","paralysis_paresis_or_recent_cast","bedridden_ge3d_or_major_surgery_12w",
 "localized_deep_vein_tenderness","entire_leg_swollen","calf_swelling_ge3cm",
 "pitting_edema_symptomatic_leg","collateral_superficial_nonvaricose_veins","previous_dvt",
)
def calculate_wells_dvt(data):
    req=WELLS_DVT_POSITIVE_KEYS+("alternative_diagnosis_at_least_as_likely",)
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Wells DVT criteria: "+", ".join(missing))
    for k in req: _bool(data[k],k)
    comp={k:(1 if data[k] else 0) for k in WELLS_DVT_POSITIVE_KEYS}
    comp["alternative_diagnosis_at_least_as_likely"]=-2 if data["alternative_diagnosis_at_least_as_likely"] else 0
    total=sum(comp.values())
    return {"id":"wells-dvt","status":"complete","components":comp,"total":total,
            "two_level_probability":"dvt_likely" if total>=2 else "dvt_unlikely",
            "source":SOURCES["wells-dvt"]}
