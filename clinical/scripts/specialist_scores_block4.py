#!/usr/bin/env python3
"""SPECIALIST block 4: GI / hepatology / toxicology."""

import math

SOURCES={
 "rockall":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC2660506/","version":"Complete Rockall 0-11"},
 "ranson":{"url":"https://www.ncbi.nlm.nih.gov/books/NBK482345/","version":"Ranson non-gallstone and gallstone-modified"},
 "meld-3":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8608337/","version":"MELD 3.0"},
 "lille":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6448617/","version":"Lille model day 7"},
 "poisoning-severity":{"url":"https://www.who.int/publications/m/item/poisoning-severity-score","version":"IPCS/EAPCCT Poisoning Severity Score 0-4"},
 "pawss":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6905615/","version":"PAWSS 0-10"},
}
def _num(v,n):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v): raise ValueError(f"{n} must be finite")
    return float(v)
def _bool(v,n):
    if not isinstance(v,bool): raise ValueError(f"{n} must be boolean")
    return v

def calculate_rockall(d):
    req=("age","heart_rate_bpm","systolic_bp_mmHg","comorbidity","endoscopic_diagnosis","stigmata")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing Rockall inputs: "+", ".join(miss))
    age=_num(d["age"],"age"); hr=_num(d["heart_rate_bpm"],"hr"); sbp=_num(d["systolic_bp_mmHg"],"sbp")
    agep=0 if age<60 else 1 if age<80 else 2
    shock=0 if sbp>=100 and hr<100 else 1 if sbp>=100 else 2
    com=str(d["comorbidity"]).strip().lower()
    cmap={"none":0,"major_other_or_ihd_or_chf":2,"renal_failure":3,"liver_failure":3,"disseminated_malignancy":3}
    if com not in cmap: raise ValueError("unsupported Rockall comorbidity")
    dx=str(d["endoscopic_diagnosis"]).strip().lower()
    dmap={"mallory_weiss_or_no_lesion":0,"all_other_diagnoses":1,"upper_gi_malignancy":2}
    if dx not in dmap: raise ValueError("unsupported Rockall diagnosis")
    st=str(d["stigmata"]).strip().lower()
    smap={"none_or_dark_spot":0,"blood_clot_visible_or_spurting_vessel":2}
    if st not in smap: raise ValueError("unsupported Rockall stigmata")
    c={"age":agep,"shock":shock,"comorbidity":cmap[com],"diagnosis":dmap[dx],"stigmata":smap[st]}
    total=sum(c.values())
    return {"id":"rockall","status":"complete","components":c,"total":total,"range":[0,11],
            "low_risk_complete_le2":total<=2,"source":SOURCES["rockall"]}

def calculate_ranson(d):
    req=("etiology","age","wbc_per_uL","glucose_mg_dL","ast_IU_L","ldh_IU_L",
         "calcium_mg_dL_48h","hematocrit_fall_percent_48h","bun_rise_mg_dL_48h",
         "base_deficit_mEq_L_48h","fluid_sequestration_L_48h")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing Ranson inputs: "+", ".join(miss))
    et=str(d["etiology"]).strip().lower()
    if et not in {"non_gallstone","gallstone"}: raise ValueError("etiology must be non_gallstone or gallstone")
    vals={k:_num(d[k],k) for k in req if k!="etiology"}
    c={}
    if et=="non_gallstone":
        if d.get("pao2_mmHg_48h") is None: raise ValueError("pao2_mmHg_48h required for non-gallstone Ranson")
        pa=_num(d["pao2_mmHg_48h"],"pao2_mmHg_48h")
        c={"age":vals["age"]>55,"wbc":vals["wbc_per_uL"]>16000,"glucose":vals["glucose_mg_dL"]>200,
           "ast":vals["ast_IU_L"]>250,"ldh":vals["ldh_IU_L"]>350,"calcium":vals["calcium_mg_dL_48h"]<8,
           "hct_fall":vals["hematocrit_fall_percent_48h"]>10,"bun_rise":vals["bun_rise_mg_dL_48h"]>=5,
           "pao2":pa<60,"base_deficit":vals["base_deficit_mEq_L_48h"]>4,"fluid":vals["fluid_sequestration_L_48h"]>6}
    else:
        c={"age":vals["age"]>70,"wbc":vals["wbc_per_uL"]>18000,"glucose":vals["glucose_mg_dL"]>220,
           "ast":vals["ast_IU_L"]>250,"ldh":vals["ldh_IU_L"]>400,"calcium":vals["calcium_mg_dL_48h"]<8,
           "hct_fall":vals["hematocrit_fall_percent_48h"]>10,"bun_rise":vals["bun_rise_mg_dL_48h"]>=2,
           "base_deficit":vals["base_deficit_mEq_L_48h"]>5,"fluid":vals["fluid_sequestration_L_48h"]>4}
    total=sum(1 for v in c.values() if v)
    return {"id":"ranson","status":"complete","etiology":et,"criteria":c,"total":total,
            "max_score":11 if et=="non_gallstone" else 10,
            "warning":"Ranson is completed over 48 h and the gallstone version uses different thresholds; do not mix the two variants.",
            "source":SOURCES["ranson"]}

def calculate_meld3(d):
    req=("female","bilirubin_mg_dL","inr","creatinine_mg_dL","sodium_mmol_L","albumin_g_dL")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing MELD 3.0 inputs: "+", ".join(miss))
    _bool(d["female"],"female")
    bili=max(1.0,_num(d["bilirubin_mg_dL"],"bilirubin"))
    inr=max(1.0,_num(d["inr"],"inr"))
    cr=_num(d["creatinine_mg_dL"],"creatinine")
    if d.get("dialysis_twice_last_7_days") is True or d.get("cvvhd_24h_last_7_days") is True: cr=3.0
    cr=min(max(cr,1.0),3.0)
    na=min(max(_num(d["sodium_mmol_L"],"sodium"),125.0),137.0)
    alb=min(max(_num(d["albumin_g_dL"],"albumin"),1.5),3.5)
    score=(1.33 if d["female"] else 0)+4.56*math.log(bili)+0.82*(137-na)-0.24*(137-na)*math.log(bili)+9.09*math.log(inr)+11.14*math.log(cr)+1.85*(3.5-alb)-1.83*(3.5-alb)*math.log(cr)+6
    score=min(max(round(score),6),40)
    return {"id":"meld-3","status":"complete","score":score,"range":[6,40],"source":SOURCES["meld-3"]}

def calculate_lille(d):
    req=("age","albumin_day0_g_L","bilirubin_day0_umol_L","bilirubin_day7_umol_L","pt_seconds","renal_insufficiency")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing Lille inputs: "+", ".join(miss))
    _bool(d["renal_insufficiency"],"renal_insufficiency")
    age=_num(d["age"],"age"); alb=_num(d["albumin_day0_g_L"],"albumin"); b0=_num(d["bilirubin_day0_umol_L"],"bilirubin0"); b7=_num(d["bilirubin_day7_umol_L"],"bilirubin7"); pt=_num(d["pt_seconds"],"pt")
    R=3.19-0.101*age+0.147*alb+0.0165*(b0-b7)-0.206*(1 if d["renal_insufficiency"] else 0)-0.0065*b0-0.0096*pt
    lille=math.exp(-R)/(1+math.exp(-R))
    return {"id":"lille","status":"complete","score":lille,"nonresponse_common_cutoff_ge_0_45":lille>=0.45,
            "source":SOURCES["lille"]}

def classify_poisoning_severity(d):
    if d.get("grade") is None: raise ValueError("Poisoning Severity Score requires explicit WHO/IPCS grade 0-4")
    grade=int(_num(d["grade"],"grade"))
    if grade not in (0,1,2,3,4): raise ValueError("grade must be 0-4")
    labels={0:"none",1:"minor",2:"moderate",3:"severe",4:"fatal"}
    return {"id":"poisoning-severity","status":"explicit_official_grade","grade":grade,"label":labels[grade],
            "warning":"PSS is an outcome/severity grading framework across organ systems. Assign the grade from the official IPCS/EAPCCT criteria; do not infer it from free text.",
            "source":SOURCES["poisoning-severity"]}

def calculate_pawss(d):
    threshold=d.get("threshold_recent_alcohol_or_positive_bal")
    if threshold is None: raise ValueError("PAWSS threshold criterion required")
    _bool(threshold,"threshold_recent_alcohol_or_positive_bal")
    keys=("previous_withdrawal","withdrawal_seizures","delirium_tremens","rehab_treatment","blackouts",
          "downers_last_90d","other_substances_last_90d","bal_over_200","autonomic_hyperactivity")
    miss=[k for k in keys if d.get(k) is None]
    if miss: raise ValueError("missing PAWSS inputs: "+", ".join(miss))
    for k in keys:_bool(d[k],k)
    if not threshold:
        return {"id":"pawss","status":"outside_threshold_window","total":0,"high_risk_ge4":False,"source":SOURCES["pawss"]}
    # PAWSS has 10 yes/no items; threshold/recent intoxication is item 1.
    total=1+sum(1 for k in keys if d[k])
    return {"id":"pawss","status":"complete","total":total,"range":[0,10],"high_risk_ge4":total>=4,
            "source":SOURCES["pawss"]}
