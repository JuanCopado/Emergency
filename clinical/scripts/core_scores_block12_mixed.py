#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 12 sepsis/hematology/renal/surgery."""

import math

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)
def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def calculate_qsofa(data):
    req=("respiratory_rate","systolic_bp_mmHg","altered_mentation")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing qSOFA inputs: "+", ".join(missing))
    rr=_num(data["respiratory_rate"],"respiratory_rate"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); _bool(data["altered_mentation"],"altered_mentation")
    comp={"rr_ge22":1 if rr>=22 else 0,"sbp_le100":1 if sbp<=100 else 0,"altered_mentation":1 if data["altered_mentation"] else 0}
    total=sum(comp.values())
    return {"id":"qsofa","status":"complete","components":comp,"total":total,"range":[0,3],
            "warning":"qSOFA is a bedside risk signal, not a sepsis definition and not a stand-alone sepsis screening rule.",
            "source":{"url":"https://jamanetwork.com/journals/jama/fullarticle/2492881","version":"Sepsis-3 qSOFA"}}

def calculate_isth_dic(data):
    if data.get("dic_associated_disorder") is not True:
        raise ValueError("ISTH overt DIC score should only be applied when a DIC-associated disorder is present")
    req=("platelets_10e9_L","fibrin_marker_multiple_uln","pt_prolongation_seconds","fibrinogen_mg_dL")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing ISTH DIC inputs: "+", ".join(missing))
    p=_num(data["platelets_10e9_L"],"platelets_10e9_L"); fm=_num(data["fibrin_marker_multiple_uln"],"fibrin_marker_multiple_uln"); pt=_num(data["pt_prolongation_seconds"],"pt_prolongation_seconds"); fib=_num(data["fibrinogen_mg_dL"],"fibrinogen_mg_dL")
    comp={
      "platelets":0 if p>=100 else 1 if p>=50 else 2,
      "fibrin_marker":0 if fm<=1 else 2 if fm<5 else 3,
      "pt_prolongation":0 if pt<3 else 1 if pt<6 else 2,
      "fibrinogen":1 if fib<100 else 0,
    }
    total=sum(comp.values())
    return {"id":"isth-dic","status":"complete","components":comp,"total":total,"overt_dic_score_ge5":total>=5,
            "warning":"Interpret fibrin-marker categories using the local validated D-dimer/FDP assay and repeat serially when clinically indicated.",
            "source":{"url":"https://www.isth.org/resource/resmgr/Workshops/Chinthammitr_DIC.pdf","version":"ISTH overt DIC"}}

def classify_kdigo_aki(data):
    req=("current_creatinine_mg_dL","baseline_creatinine_mg_dL","creatinine_increase_mg_dL_48h","urine_ml_kg_h","urine_duration_h","rrt_started")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing KDIGO AKI inputs: "+", ".join(missing))
    cur=_num(data["current_creatinine_mg_dL"],"current_creatinine_mg_dL"); base=_num(data["baseline_creatinine_mg_dL"],"baseline_creatinine_mg_dL"); delta=_num(data["creatinine_increase_mg_dL_48h"],"creatinine_increase_mg_dL_48h"); uo=_num(data["urine_ml_kg_h"],"urine_ml_kg_h"); dur=_num(data["urine_duration_h"],"urine_duration_h"); _bool(data["rrt_started"],"rrt_started")
    if base<=0 or cur<0 or delta<0 or uo<0 or dur<0: raise ValueError("invalid KDIGO inputs")
    ratio=cur/base
    cr_stage=0
    if data["rrt_started"] or ratio>=3 or cur>=4.0: cr_stage=3
    elif ratio>=2: cr_stage=2
    elif ratio>=1.5 or delta>=0.3: cr_stage=1
    u_stage=0
    if uo<0.3 and dur>=24: u_stage=3
    elif uo==0 and dur>=12: u_stage=3
    elif uo<0.5 and dur>=12: u_stage=2
    elif uo<0.5 and dur>=6: u_stage=1
    stage=max(cr_stage,u_stage)
    aki=stage>=1 or delta>=0.3 or ratio>=1.5
    return {"id":"kdigo-aki","status":"complete","aki":aki,"stage":stage,"creatinine_stage":cr_stage,"urine_stage":u_stage,"creatinine_ratio":ratio,
            "warning":"KDIGO 2012 remains the published reference guideline; a 2026 update was still in draft/public-review process and must not silently replace it.",
            "source":{"url":"https://kdigo.org/wp-content/uploads/2016/10/KDIGO-2012-AKI-Guideline-English.pdf","version":"KDIGO AKI 2012"}}

def calculate_mcmahon(data):
    req=("age","sex","creatinine_mg_dL","calcium_mg_dL","ck_u_L","etiology_low_risk_group","phosphate_mg_dL","bicarbonate_mEq_L")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing McMahon inputs: "+", ".join(missing))
    age=_num(data["age"],"age"); cr=_num(data["creatinine_mg_dL"],"creatinine_mg_dL"); ca=_num(data["calcium_mg_dL"],"calcium_mg_dL"); ck=_num(data["ck_u_L"],"ck_u_L"); phos=_num(data["phosphate_mg_dL"],"phosphate_mg_dL"); bicarb=_num(data["bicarbonate_mEq_L"],"bicarbonate_mEq_L")
    sex=str(data["sex"]).lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    _bool(data["etiology_low_risk_group"],"etiology_low_risk_group")
    comp={
      "age":1.5 if 50<age<=70 else 2.5 if 70<age<=80 else 3 if age>80 else 0,
      "female":1 if sex in {"female","f"} else 0,
      "creatinine":1.5 if 1.4<=cr<=2.2 else 3 if cr>2.2 else 0,
      "calcium_lt7_5":2 if ca<7.5 else 0,
      "ck_gt40000":2 if ck>40000 else 0,
      "etiology_other":0 if data["etiology_low_risk_group"] else 3,
      "phosphate":1.5 if 4.0<=phos<=5.4 else 3 if phos>5.4 else 0,
      "bicarbonate_lt19":2 if bicarb<19 else 0,
    }
    total=sum(comp.values())
    return {"id":"mcmahon-rhabdo","status":"complete","components":comp,"total":total,"higher_risk_ge6":total>=6,
            "warning":"etiology_low_risk_group=true only for seizure, syncope, exercise, statin or myositis; McMahon predicts RRT/death risk and does not replace rhabdomyolysis management.",
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8804685/","version":"McMahon rhabdomyolysis score"}}

def calculate_alvarado(data):
    req=("migration_rlq","anorexia","nausea_or_vomiting","rlq_tenderness","rebound_or_percussion_tenderness","temperature_c","wbc_10e9_L","neutrophil_left_shift")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Alvarado inputs: "+", ".join(missing))
    for k in req[:5]: _bool(data[k],k)
    _bool(data["neutrophil_left_shift"],"neutrophil_left_shift")
    temp=_num(data["temperature_c"],"temperature_c"); wbc=_num(data["wbc_10e9_L"],"wbc_10e9_L")
    comp={"migration_rlq":1 if data["migration_rlq"] else 0,"anorexia":1 if data["anorexia"] else 0,"nausea_vomiting":1 if data["nausea_or_vomiting"] else 0,"rlq_tenderness":2 if data["rlq_tenderness"] else 0,"rebound_percussion":1 if data["rebound_or_percussion_tenderness"] else 0,"temperature_gt37_5":1 if temp>37.5 else 0,"wbc_gt10":2 if wbc>10 else 0,"left_shift":1 if data["neutrophil_left_shift"] else 0}
    total=sum(comp.values())
    band="low_0_4" if total<=4 else "equivocal_5_6" if total<=6 else "probable_7_8" if total<=8 else "high_9_10"
    return {"id":"alvarado","status":"complete","components":comp,"total":total,"range":[0,10],"risk_band":band,
            "warning":"Alvarado supports appendicitis probability assessment; it must not substitute for clinical reassessment/imaging where indicated.",
            "source":{"url":"https://pubmed.ncbi.nlm.nih.gov/3963537/","version":"Alvarado 1986"}}

def calculate_air(data):
    req=("vomiting","right_iliac_fossa_pain","guarding_rebound_severity","temperature_c","wbc_10e9_L","neutrophils_percent","crp_mg_L")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing AIR inputs: "+", ".join(missing))
    _bool(data["vomiting"],"vomiting"); _bool(data["right_iliac_fossa_pain"],"right_iliac_fossa_pain")
    sev=str(data["guarding_rebound_severity"]).lower()
    smap={"none":0,"slight":1,"moderate":2,"strong":3}
    if sev not in smap: raise ValueError("guarding_rebound_severity must be none/slight/moderate/strong")
    temp=_num(data["temperature_c"],"temperature_c"); wbc=_num(data["wbc_10e9_L"],"wbc_10e9_L"); neut=_num(data["neutrophils_percent"],"neutrophils_percent"); crp=_num(data["crp_mg_L"],"crp_mg_L")
    comp={"vomiting":1 if data["vomiting"] else 0,"right_iliac_fossa_pain":1 if data["right_iliac_fossa_pain"] else 0,"guarding_rebound":smap[sev],"temperature_ge38_5":1 if temp>=38.5 else 0,"wbc":0 if wbc<10 else 1 if wbc<15 else 2,"neutrophils":0 if neut<70 else 1 if neut<85 else 2,"crp":0 if crp<10 else 1 if crp<50 else 2}
    total=sum(comp.values()); band="low_0_4" if total<=4 else "intermediate_5_8" if total<=8 else "high_9_12"
    return {"id":"air-appendicitis","status":"complete","components":comp,"total":total,"range":[0,12],"risk_band":band,
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8154764/","version":"Appendicitis Inflammatory Response"}}
