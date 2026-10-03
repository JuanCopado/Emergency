#!/usr/bin/env python3
"""CORE scores block 8: young febrile infant rules and APGAR."""

import math

SOURCES={
  "pecarn-febrile-infant":{
    "authority":"PECARN febrile infant rule",
    "url":"https://pubmed.ncbi.nlm.nih.gov/30776077/",
    "version":"PECARN 2019 low-risk SBI rule, febrile infants <=60 days",
  },
  "step-by-step-infant":{
    "authority":"European Step-by-Step validation",
    "url":"https://pubmed.ncbi.nlm.nih.gov/27382134/",
    "version":"Step-by-Step febrile infant approach <=90 days",
  },
  "apgar":{
    "authority":"AAP/ACOG",
    "url":"https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2015/10/the-apgar-score",
    "version":"APGAR 0-10 at 1 and 5 minutes; repeat q5 min to 20 min if 5-min score <7",
  },
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be a finite number")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def classify_pecarn_febrile_infant(data):
    required=("age_days","well_appearing","urinalysis_negative","anc_per_uL","procalcitonin_ng_mL")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing PECARN febrile infant inputs: "+", ".join(missing))
    age=_num(data["age_days"],"age_days")
    if age<0 or age>60:
        raise ValueError("PECARN 2019 febrile-infant rule applies to age <=60 days")
    _bool(data["well_appearing"],"well_appearing")
    _bool(data["urinalysis_negative"],"urinalysis_negative")
    anc=_num(data["anc_per_uL"],"anc_per_uL")
    pct=_num(data["procalcitonin_ng_mL"],"procalcitonin_ng_mL")
    if anc<0 or pct<0: raise ValueError("ANC/PCT cannot be negative")
    rule_low=bool(data["urinalysis_negative"] and anc<=4090 and pct<=1.71)
    if not data["well_appearing"]:
        classification="not_low_risk_due_to_clinical_appearance"
        low=False
    else:
        low=rule_low
        classification="low_risk_by_pecarn_2019" if low else "not_low_risk_by_pecarn_2019"
    return {
      "id":"pecarn-febrile-infant","status":"complete","age_days":age,
      "criteria":{
        "urinalysis_negative":data["urinalysis_negative"],
        "anc_le_4090":anc<=4090,
        "pct_le_1_71":pct<=1.71,
      },
      "low_risk_sbi":low,"classification":classification,
      "warning":"This 2019 PECARN rule identifies low risk for serious bacterial infection; current age-specific febrile-infant guidelines and clinical appearance still govern LP, antibiotics and disposition.",
      "source":SOURCES["pecarn-febrile-infant"],
    }

def classify_step_by_step(data):
    required=("age_days","well_appearing","leukocyturia","procalcitonin_ng_mL","crp_mg_L","anc_per_uL")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Step-by-Step inputs: "+", ".join(missing))
    age=_num(data["age_days"],"age_days")
    if age<0 or age>90: raise ValueError("Step-by-Step applies to febrile infants <=90 days")
    _bool(data["well_appearing"],"well_appearing")
    _bool(data["leukocyturia"],"leukocyturia")
    pct=_num(data["procalcitonin_ng_mL"],"procalcitonin_ng_mL")
    crp=_num(data["crp_mg_L"],"crp_mg_L")
    anc=_num(data["anc_per_uL"],"anc_per_uL")
    if min(pct,crp,anc)<0: raise ValueError("PCT/CRP/ANC cannot be negative")

    if not data["well_appearing"]:
        classification="high_risk_ill_appearing"
    elif age<=21:
        classification="high_risk_age_le_21d"
    elif data["leukocyturia"]:
        classification="high_risk_leukocyturia"
    elif pct>=0.5:
        classification="high_risk_pct_ge_0_5"
    elif crp>20 or anc>10000:
        classification="intermediate_risk"
    else:
        classification="low_risk"

    return {
      "id":"step-by-step-infant","status":"complete","classification":classification,
      "low_risk":classification=="low_risk",
      "criteria":{
        "well_appearing":data["well_appearing"],
        "age_gt_21d":age>21,
        "no_leukocyturia":not data["leukocyturia"],
        "pct_lt_0_5":pct<0.5,
        "crp_le_20":crp<=20,
        "anc_le_10000":anc<=10000,
      },
      "warning":"Step-by-Step is a sequential risk tool for young febrile infants; management must follow current age-specific guidance and local access to PCT, cultures and follow-up.",
      "source":SOURCES["step-by-step-infant"],
    }

def calculate_apgar(data):
    required=("time_minutes","heart_rate_bpm","respiratory_effort","muscle_tone","reflex_irritability","color")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing APGAR inputs: "+", ".join(missing))
    time=_num(data["time_minutes"],"time_minutes")
    if time<=0 or time>20: raise ValueError("time_minutes must be >0 and <=20")
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    if hr<0: raise ValueError("heart_rate_bpm cannot be negative")
    pulse=0 if hr==0 else 1 if hr<100 else 2

    maps={
      "respiratory_effort":{"absent":0,"slow_irregular_gasping":1,"good_crying":2},
      "muscle_tone":{"flaccid":0,"some_flexion":1,"active_motion":2},
      "reflex_irritability":{"no_response":0,"grimace":1,"cry_cough_sneeze_withdrawal":2},
      "color":{"blue_or_pale":0,"pink_body_blue_extremities":1,"completely_pink":2},
    }
    components={"pulse":pulse}
    for key,mapping in maps.items():
        value=str(data[key]).strip().lower()
        if value not in mapping: raise ValueError(f"unsupported APGAR {key} category")
        components[key]=mapping[value]
    total=sum(components.values())
    repeat_needed=bool(time==5 and total<7)
    return {
      "id":"apgar","status":"complete","time_minutes":time,
      "components":components,"total":total,"range":[0,10],
      "repeat_every_5_min_to_20_if_5min_below_7":repeat_needed,
      "warning":"APGAR reports newborn condition and response to resuscitation. Do not delay resuscitation to obtain the score and do not use APGAR alone to diagnose asphyxia or predict individual neurologic outcome.",
      "source":SOURCES["apgar"],
    }
