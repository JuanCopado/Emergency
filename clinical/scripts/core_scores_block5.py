#!/usr/bin/env python3
"""CORE scores block 5: adult/transversal wrappers and rules."""

import math

SOURCES={
  "oakland":{
    "authority":"Oakland et al / external validation",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7341175/",
    "version":"Oakland Score original 7-variable form",
  },
  "obstetric-shock-index":{
    "authority":"Obstetric shock-index literature",
    "url":"https://pubmed.ncbi.nlm.nih.gov/31345740/",
    "version":"Obstetric Shock Index HR/SBP",
  },
  "revised-baux":{
    "authority":"Osler et al. J Trauma 2010",
    "url":"https://pubmed.ncbi.nlm.nih.gov/20038856/",
    "version":"Revised Baux Score",
  },
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be a finite number")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool):
        raise ValueError(f"{name} must be boolean")
    return v

def calculate_oakland(data):
    required=("age","sex","previous_lgib_admission","dre_blood","heart_rate_bpm","systolic_bp_mmHg","hemoglobin_g_dL")
    missing=[k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing Oakland inputs: "+", ".join(missing))
    age=_num(data["age"],"age")
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    hb=_num(data["hemoglobin_g_dL"],"hemoglobin_g_dL")
    if min(age,hr,sbp,hb)<0:
        raise ValueError("Oakland numeric inputs cannot be negative")
    sex=str(data["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}:
        raise ValueError("sex must be male/female")
    _bool(data["previous_lgib_admission"],"previous_lgib_admission")
    _bool(data["dre_blood"],"dre_blood")

    age_score=0 if age<=39 else 1 if age<=69 else 2
    sex_score=1 if sex in {"male","m"} else 0
    prior_score=1 if data["previous_lgib_admission"] else 0
    dre_score=1 if data["dre_blood"] else 0
    hr_score=0 if hr<=69 else 1 if hr<=89 else 2 if hr<=109 else 3
    if sbp>=160: sbp_score=0
    elif sbp>=130: sbp_score=2
    elif sbp>=120: sbp_score=3
    elif sbp>=90: sbp_score=4
    elif sbp>=50: sbp_score=5
    else:
        raise ValueError("Oakland score is not validated for SBP <50 mmHg; use clinical resuscitation pathway")

    if hb>=16.0: hb_score=0
    elif hb>=13.0: hb_score=4
    elif hb>=11.0: hb_score=8
    elif hb>=9.0: hb_score=13
    elif hb>=7.0: hb_score=17
    elif hb>=3.6: hb_score=22
    else:
        raise ValueError("Oakland score table is not defined for hemoglobin <3.6 g/dL")

    components={
        "age":age_score,
        "sex":sex_score,
        "previous_lgib_admission":prior_score,
        "dre_blood":dre_score,
        "heart_rate":hr_score,
        "systolic_bp":sbp_score,
        "hemoglobin":hb_score,
    }
    total=sum(components.values())
    return {
        "id":"oakland","status":"complete","components":components,"total":total,"range":[0,35],
        "low_risk_original_threshold_le_8":total<=8,
        "warning":"Oakland supports identification of selected low-risk lower-GI-bleed patients. A low score does not override ongoing bleeding, instability, major comorbidity or clinical judgment.",
        "source":SOURCES["oakland"],
    }

def calculate_obstetric_shock_index(data):
    if data.get("heart_rate_bpm") is None or data.get("systolic_bp_mmHg") is None:
        raise ValueError("obstetric shock index requires heart_rate_bpm and systolic_bp_mmHg")
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    if hr<0 or sbp<=0:
        raise ValueError("invalid heart rate or systolic blood pressure")
    value=hr/sbp
    return {
        "id":"obstetric-shock-index","status":"complete","value":value,"unit":"ratio",
        "formula":"heart_rate_bpm / systolic_bp_mmHg",
        "warning":"Obstetric shock index is an adjunct in pregnancy/postpartum hemorrhage. Threshold performance varies by setting; do not use a single cutoff as a stand-alone transfusion or intervention rule.",
        "source":SOURCES["obstetric-shock-index"],
    }

def calculate_revised_baux(data):
    required=("age","tbsa_percent","inhalation_injury")
    missing=[k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing Revised Baux inputs: "+", ".join(missing))
    age=_num(data["age"],"age")
    tbsa=_num(data["tbsa_percent"],"tbsa_percent")
    _bool(data["inhalation_injury"],"inhalation_injury")
    if age<0 or not 0<=tbsa<=100:
        raise ValueError("age must be >=0 and tbsa_percent 0-100")
    score=age+tbsa+(17 if data["inhalation_injury"] else 0)
    return {
        "id":"revised-baux","status":"complete","value":score,"unit":"points",
        "formula":"age + TBSA% + 17*(inhalation injury)",
        "warning":"Revised Baux is a population prognostic model, not an individual treatment-withdrawal rule.",
        "source":SOURCES["revised-baux"],
    }
