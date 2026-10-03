#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 4 GI / pneumonia / pediatric sepsis."""

import math

SOURCES={
  "glasgow-blatchford":{
    "authority":"Blatchford et al. Lancet 2000 + validated table",
    "url":"https://pubmed.ncbi.nlm.nih.gov/11073021/",
    "version":"Glasgow-Blatchford Score",
  },
  "curb65":{
    "authority":"Lim et al. Thorax 2003",
    "url":"https://thorax.bmj.com/content/58/5/377",
    "version":"CURB-65",
  },
  "phoenix-sepsis":{
    "authority":"International Consensus Criteria for Pediatric Sepsis / JAMA 2024",
    "url":"https://doi.org/10.1001/jama.2024.0196",
    "version":"Phoenix Sepsis Score 2024",
  },
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be a finite number")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def calculate_glasgow_blatchford(data):
    required=("hemoglobin_g_dL","sex","systolic_bp_mmHg","pulse_bpm","melena","syncope","hepatic_disease","heart_failure")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing GBS inputs: "+", ".join(missing))
    if data.get("urea_mmol_L") is None and data.get("bun_mg_dL") is None:
        raise ValueError("GBS requires urea_mmol_L or bun_mg_dL")
    if data.get("urea_mmol_L") is not None and data.get("bun_mg_dL") is not None:
        raise ValueError("provide only one of urea_mmol_L or bun_mg_dL")
    urea=_num(data["urea_mmol_L"],"urea_mmol_L") if data.get("urea_mmol_L") is not None else _num(data["bun_mg_dL"],"bun_mg_dL")/2.8
    hb=_num(data["hemoglobin_g_dL"],"hemoglobin_g_dL")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    pulse=_num(data["pulse_bpm"],"pulse_bpm")
    if min(urea,hb,sbp,pulse)<0: raise ValueError("GBS numeric inputs cannot be negative")
    sex=str(data["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    for k in ("melena","syncope","hepatic_disease","heart_failure"): _bool(data[k],k)

    if urea<6.5: urea_score=0
    elif urea<8.0: urea_score=2
    elif urea<10.0: urea_score=3
    elif urea<=25.0: urea_score=4
    else: urea_score=6

    female=sex in {"female","f"}
    if female:
        hb_score=0 if hb>=12 else 1 if hb>=10 else 6
    else:
        hb_score=0 if hb>=13 else 1 if hb>=12 else 3 if hb>=10 else 6

    bp_score=0 if sbp>=110 else 1 if sbp>=100 else 2 if sbp>=90 else 3
    components={
      "urea":urea_score,
      "hemoglobin":hb_score,
      "systolic_bp":bp_score,
      "pulse_ge_100":1 if pulse>=100 else 0,
      "melena":1 if data["melena"] else 0,
      "syncope":2 if data["syncope"] else 0,
      "hepatic_disease":2 if data["hepatic_disease"] else 0,
      "heart_failure":2 if data["heart_failure"] else 0,
    }
    total=sum(components.values())
    return {
      "id":"glasgow-blatchford","status":"complete","components":components,"total":total,"range":[0,23],
      "very_low_risk_score_0_or_1":total<=1,
      "warning":"GBS supports pre-endoscopy risk stratification. Disposition still depends on ongoing bleeding, comorbidity, social/logistic factors and local pathway.",
      "source":SOURCES["glasgow-blatchford"],
    }

def calculate_curb65(data):
    required=("confusion","urea_mmol_L","respiratory_rate","systolic_bp_mmHg","diastolic_bp_mmHg","age")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing CURB-65 inputs: "+", ".join(missing))
    _bool(data["confusion"],"confusion")
    urea=_num(data["urea_mmol_L"],"urea_mmol_L")
    rr=_num(data["respiratory_rate"],"respiratory_rate")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    dbp=_num(data["diastolic_bp_mmHg"],"diastolic_bp_mmHg")
    age=_num(data["age"],"age")
    if min(urea,rr,sbp,dbp,age)<0: raise ValueError("CURB-65 inputs cannot be negative")
    components={
      "confusion":1 if data["confusion"] else 0,
      "urea_gt_7":1 if urea>7 else 0,
      "respiratory_rate_ge_30":1 if rr>=30 else 0,
      "low_bp":1 if (sbp<90 or dbp<=60) else 0,
      "age_ge_65":1 if age>=65 else 0,
    }
    total=sum(components.values())
    band="low_0_1" if total<=1 else "intermediate_2" if total==2 else "high_3_5"
    return {
      "id":"curb65","status":"complete","components":components,"total":total,"range":[0,5],
      "severity_band":band,
      "warning":"CURB-65 supports CAP severity assessment; site-of-care decisions must also consider oxygenation, complications, comorbidity and clinical judgment.",
      "source":SOURCES["curb65"],
    }

def _phoenix_map_points(age_months,map_mmHg):
    age=_num(age_months,"age_months")
    m=_num(map_mmHg,"map_mmHg")
    if age<0 or age>=216: raise ValueError("Phoenix age_months must be 0 to <216")
    if age<1: normal,mid=31,17
    elif age<12: normal,mid=39,25
    elif age<24: normal,mid=44,31
    elif age<60: normal,mid=45,32
    elif age<144: normal,mid=49,36
    else: normal,mid=52,38
    if m>=normal:return 0
    if m>=mid:return 1
    return 2

def calculate_phoenix_sepsis(data):
    if data.get("suspected_or_confirmed_infection") is None:
        raise ValueError("suspected_or_confirmed_infection is required")
    _bool(data["suspected_or_confirmed_infection"],"suspected_or_confirmed_infection")
    if data.get("age_months") is None: raise ValueError("age_months is required")
    age=_num(data["age_months"],"age_months")
    if age<0 or age>=216: raise ValueError("Phoenix is for patients <18 years")

    observed=[]

    # Respiratory: use P/F preferentially when provided, otherwise S/F.
    respiratory=0
    ratio_kind=None
    ratio=None
    if data.get("pao2_fio2") is not None:
        ratio=_num(data["pao2_fio2"],"pao2_fio2"); ratio_kind="PF"; observed.append("respiratory")
    elif data.get("spo2_fio2") is not None:
        ratio=_num(data["spo2_fio2"],"spo2_fio2"); ratio_kind="SF"; observed.append("respiratory")
    any_support=bool(data.get("any_respiratory_support",False))
    imv=bool(data.get("invasive_mechanical_ventilation",False))
    if ratio is not None:
        if ratio_kind=="PF":
            if imv and ratio<100: respiratory=3
            elif imv and ratio<=200: respiratory=2
            elif any_support and ratio<400: respiratory=1
        else:
            if imv and ratio<148: respiratory=3
            elif imv and ratio<=220: respiratory=2
            elif any_support and ratio<292: respiratory=1

    # Cardiovascular: additive 0-6 across vasoactive count, lactate and age-adjusted MAP.
    cardiovascular=0
    cv_observed=False
    if data.get("vasoactive_medication_count") is not None:
        count=int(_num(data["vasoactive_medication_count"],"vasoactive_medication_count"))
        if count<0: raise ValueError("vasoactive_medication_count cannot be negative")
        cardiovascular += 0 if count==0 else 1 if count==1 else 2
        cv_observed=True
    if data.get("lactate_mmol_L") is not None:
        lact=_num(data["lactate_mmol_L"],"lactate_mmol_L")
        if lact<0: raise ValueError("lactate_mmol_L cannot be negative")
        cardiovascular += 0 if lact<5 else 1 if lact<11 else 2
        cv_observed=True
    if data.get("map_mmHg") is not None:
        cardiovascular += _phoenix_map_points(age,data["map_mmHg"])
        cv_observed=True
    if cv_observed: observed.append("cardiovascular")

    # Coagulation: 1 point per abnormal measured variable, max 2.
    coag_abnormal=0; coag_measured=0
    for key,abnormal in (
      ("platelets_10e3_uL",lambda x:x<100),
      ("inr",lambda x:x>1.3),
      ("d_dimer_mg_L_feu",lambda x:x>2),
      ("fibrinogen_mg_dL",lambda x:x<100),
    ):
        if data.get(key) is not None:
            value=_num(data[key],key)
            coag_measured+=1
            if abnormal(value): coag_abnormal+=1
    coagulation=min(coag_abnormal,2)
    if coag_measured: observed.append("coagulation")

    # Neurologic.
    neurologic=0; neuro_observed=False
    if data.get("fixed_pupils_bilateral") is not None:
        _bool(data["fixed_pupils_bilateral"],"fixed_pupils_bilateral")
        neuro_observed=True
        if data["fixed_pupils_bilateral"]: neurologic=2
    if neurologic<2 and data.get("gcs") is not None:
        g=int(_num(data["gcs"],"gcs"))
        if g<3 or g>15: raise ValueError("gcs must be 3-15")
        neuro_observed=True
        if g<=10: neurologic=1
    if neuro_observed: observed.append("neurologic")

    components={
      "respiratory":respiratory,
      "cardiovascular":cardiovascular,
      "coagulation":coagulation,
      "neurologic":neurologic,
    }
    total=sum(components.values())
    sepsis=bool(data["suspected_or_confirmed_infection"] and total>=2)
    shock=bool(sepsis and cardiovascular>=1)
    return {
      "id":"phoenix-sepsis","status":"complete_with_available_variables",
      "components":components,"total":total,"range":[0,13],
      "observed_domains":sorted(set(observed)),
      "observed_domain_count":len(set(observed)),
      "phoenix_sepsis":sepsis,"phoenix_septic_shock":shock,
      "warning":"Phoenix permits scoring with some variables unmeasured; unmeasured variables contribute no points but must not be interpreted as confirmed normal. Apply only in patients <18 years with suspected/confirmed infection for sepsis classification.",
      "source":SOURCES["phoenix-sepsis"],
    }
