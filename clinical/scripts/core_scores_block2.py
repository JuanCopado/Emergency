#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 2 cardiology."""

import math

SOURCES={
  "heart":{
    "authority":"Original/validated HEART literature",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6005932/",
    "version":"HEART 0-10 using local troponin upper reference limit ratio",
  },
  "grace-2":{
    "authority":"GRACE 2.0 ACS Risk Calculator",
    "url":"https://www.gracescore.org/website.html",
    "version":"GRACE 2.0 official external calculator",
  },
  "cha2ds2-vasc":{
    "authority":"ESC AF guidance / established CHA2DS2-VASc",
    "url":"https://www.escardio.org/static-file/Escardio/Guidelines/ehw128_Addenda.pdf",
    "version":"CHA2DS2-VASc",
  },
  "cha2ds2-va":{
    "authority":"2024 ESC AF Guidelines",
    "url":"https://www.escardio.org/static-file/Escardio/Guidelines/Products/Essential%20Messages/2024%20EM/Essential%20Messages_2024%20AFib.pdf",
    "version":"CHA2DS2-VA (ESC 2024)",
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

def calculate_heart(data):
    required=("history","ecg","age","risk_factor_count","known_atherosclerotic_disease","troponin_multiple_uln")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing HEART inputs: "+", ".join(missing))

    history_map={"slightly_suspicious":0,"nonspecific":0,"moderately_suspicious":1,"highly_suspicious":2}
    ecg_map={"normal":0,"nonspecific_repolarization":1,"significant_st_depression":2}
    h=str(data["history"]).strip().lower()
    e=str(data["ecg"]).strip().lower()
    if h not in history_map: raise ValueError("history must be slightly_suspicious/moderately_suspicious/highly_suspicious")
    if e not in ecg_map: raise ValueError("ecg must be normal/nonspecific_repolarization/significant_st_depression")

    age=_num(data["age"],"age")
    if age<0: raise ValueError("age cannot be negative")
    age_score=0 if age<45 else 1 if age<65 else 2

    rf=int(_num(data["risk_factor_count"],"risk_factor_count"))
    if rf<0: raise ValueError("risk_factor_count cannot be negative")
    known=_bool(data["known_atherosclerotic_disease"],"known_atherosclerotic_disease")
    rf_score=2 if known or rf>=3 else 1 if rf>=1 else 0

    trop=_num(data["troponin_multiple_uln"],"troponin_multiple_uln")
    if trop<0: raise ValueError("troponin_multiple_uln cannot be negative")
    trop_score=0 if trop<=1 else 1 if trop<3 else 2

    components={"history":history_map[h],"ecg":ecg_map[e],"age":age_score,"risk_factors":rf_score,"troponin":trop_score}
    total=sum(components.values())
    band="low_0_3" if total<=3 else "intermediate_4_6" if total<=6 else "high_7_10"
    return {
      "id":"heart","status":"complete","components":components,"total":total,"range":[0,10],
      "risk_band":band,
      "warning":"HEART is a risk-stratification aid, not a stand-alone rule-out of ACS. History scoring is clinician-judged and troponin must be normalized to the local assay upper reference limit.",
      "source":SOURCES["heart"],
    }

def prepare_grace2(data):
    required=("age","heart_rate_bpm","systolic_bp_mmHg","cardiac_arrest_at_admission","st_segment_deviation","elevated_cardiac_biomarkers")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing GRACE 2.0 inputs: "+", ".join(missing))
    for key in ("age","heart_rate_bpm","systolic_bp_mmHg"):
        if _num(data[key],key)<0: raise ValueError(f"{key} cannot be negative")
    for key in ("cardiac_arrest_at_admission","st_segment_deviation","elevated_cardiac_biomarkers"):
        _bool(data[key],key)
    if data.get("creatinine_mg_dL") is not None and _num(data["creatinine_mg_dL"],"creatinine_mg_dL")<=0:
        raise ValueError("creatinine_mg_dL must be >0")
    if data.get("killip_class") is not None:
        k=int(_num(data["killip_class"],"killip_class"))
        if k not in (1,2,3,4): raise ValueError("killip_class must be 1-4")
    complete=data.get("creatinine_mg_dL") is not None and data.get("killip_class") is not None
    return {
      "id":"grace-2",
      "status":"official_external_calculator_required",
      "input_mode":"complete_grace2" if complete else "mini_grace_possible",
      "validated_inputs":{k:data.get(k) for k in (
        "age","heart_rate_bpm","systolic_bp_mmHg","creatinine_mg_dL","killip_class",
        "cardiac_arrest_at_admission","st_segment_deviation","elevated_cardiac_biomarkers"
      )},
      "official_calculator":"https://www.gracescore.org/website.html",
      "warning":"Do not approximate GRACE 2.0 probabilities locally. The official calculator uses revised non-linear algorithms and can invoke mini-GRACE when creatinine or Killip class is unavailable.",
      "source":SOURCES["grace-2"],
    }

def _cha_common(data):
    required=("age","heart_failure_or_lvd","hypertension","diabetes","prior_stroke_tia_thromboembolism","vascular_disease")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing CHA2DS2 inputs: "+", ".join(missing))
    age=_num(data["age"],"age")
    if age<0: raise ValueError("age cannot be negative")
    for k in required[1:]: _bool(data[k],k)
    points={
      "C_heart_failure_lvd":1 if data["heart_failure_or_lvd"] else 0,
      "H_hypertension":1 if data["hypertension"] else 0,
      "A2_age_75_or_more":2 if age>=75 else 0,
      "D_diabetes":1 if data["diabetes"] else 0,
      "S2_stroke_tia_thromboembolism":2 if data["prior_stroke_tia_thromboembolism"] else 0,
      "V_vascular_disease":1 if data["vascular_disease"] else 0,
      "A_age_65_74":1 if 65<=age<75 else 0,
    }
    return points

def calculate_cha2ds2_vasc(data):
    points=_cha_common(data)
    if data.get("sex") is None: raise ValueError("sex required for CHA2DS2-VASc")
    sex=str(data["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    points["Sc_female_sex"]=1 if sex in {"female","f"} else 0
    total=sum(points.values())
    return {
      "id":"cha2ds2-vasc","status":"complete","components":points,"total":total,"range":[0,9],
      "warning":"CHA2DS2-VASc is retained for compatibility with guidance/studies that use it. Do not mix its treatment thresholds with CHA2DS2-VA thresholds.",
      "source":SOURCES["cha2ds2-vasc"],
    }

def calculate_cha2ds2_va(data):
    points=_cha_common(data)
    total=sum(points.values())
    if total==0: context="esc2024_low_risk_no_score_based_oac_trigger"
    elif total==1: context="esc2024_oac_should_be_considered"
    else: context="esc2024_oac_recommended_if_eligible"
    return {
      "id":"cha2ds2-va","status":"complete","components":points,"total":total,"range":[0,8],
      "esc2024_context":context,
      "warning":"Score supports thromboembolic-risk assessment in AF; anticoagulation still requires eligibility, contraindication, bleeding-risk and patient-context assessment.",
      "source":SOURCES["cha2ds2-va"],
    }
