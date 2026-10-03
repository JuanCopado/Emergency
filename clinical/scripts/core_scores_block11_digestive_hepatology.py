#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 11 digestive/hepatology."""

import math

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)
def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

SOURCES={
 "aims65":{"url":"https://pubmed.ncbi.nlm.nih.gov/21907980/","version":"AIMS65"},
 "bisap":{"url":"https://pubmed.ncbi.nlm.nih.gov/18519429/","version":"BISAP"},
 "child-pugh":{"url":"https://www.ncbi.nlm.nih.gov/books/NBK598240/table/table4/","version":"Child-Turcotte-Pugh"},
 "kings-college":{"url":"https://easl.eu/wp-content/uploads/2018/10/LiverFailure-English-report.pdf","version":"King's College acute liver failure criteria"},
}

def calculate_aims65(data):
    req=("albumin_g_dL","inr","altered_mental_status","systolic_bp_mmHg","age")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing AIMS65 inputs: "+", ".join(missing))
    albumin=_num(data["albumin_g_dL"],"albumin_g_dL"); inr=_num(data["inr"],"inr"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); age=_num(data["age"],"age")
    _bool(data["altered_mental_status"],"altered_mental_status")
    comp={
      "albumin_lt3":1 if albumin<3.0 else 0,
      "inr_gt1_5":1 if inr>1.5 else 0,
      "altered_mental_status":1 if data["altered_mental_status"] else 0,
      "sbp_le90":1 if sbp<=90 else 0,
      "age_gt65":1 if age>65 else 0,
    }
    total=sum(comp.values())
    return {"id":"aims65","status":"complete","components":comp,"total":total,"range":[0,5],
            "warning":"AIMS65 predicts adverse outcome/mortality risk in acute upper GI bleeding; it is not a stand-alone disposition or endoscopy rule.",
            "source":SOURCES["aims65"]}

def calculate_bisap(data):
    req=("bun_mg_dL","impaired_mental_status","sirs","age","pleural_effusion")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing BISAP inputs: "+", ".join(missing))
    bun=_num(data["bun_mg_dL"],"bun_mg_dL"); age=_num(data["age"],"age")
    for k in ("impaired_mental_status","sirs","pleural_effusion"):_bool(data[k],k)
    comp={
      "bun_gt25":1 if bun>25 else 0,
      "impaired_mental_status":1 if data["impaired_mental_status"] else 0,
      "sirs":1 if data["sirs"] else 0,
      "age_gt60":1 if age>60 else 0,
      "pleural_effusion":1 if data["pleural_effusion"] else 0,
    }
    total=sum(comp.values())
    return {"id":"bisap","status":"complete","components":comp,"total":total,"range":[0,5],
            "warning":"BISAP is an early mortality-risk score in acute pancreatitis and must not substitute for organ-failure assessment or local severity pathways.",
            "source":SOURCES["bisap"]}

def calculate_child_pugh(data):
    req=("bilirubin_mg_dL","albumin_g_dL","inr","ascites","encephalopathy_grade")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Child-Pugh inputs: "+", ".join(missing))
    bili=_num(data["bilirubin_mg_dL"],"bilirubin_mg_dL"); alb=_num(data["albumin_g_dL"],"albumin_g_dL"); inr=_num(data["inr"],"inr")
    asc=str(data["ascites"]).strip().lower()
    amap={"none":1,"mild_or_diuretic_responsive":2,"moderate_severe_or_refractory":3}
    if asc not in amap: raise ValueError("ascites must be none/mild_or_diuretic_responsive/moderate_severe_or_refractory")
    he=int(_num(data["encephalopathy_grade"],"encephalopathy_grade"))
    if he<0 or he>4: raise ValueError("encephalopathy_grade must be 0-4")
    comp={
      "bilirubin":1 if bili<2 else 2 if bili<=3 else 3,
      "albumin":1 if alb>3.5 else 2 if alb>=2.8 else 3,
      "inr":1 if inr<1.7 else 2 if inr<=2.3 else 3,
      "ascites":amap[asc],
      "encephalopathy":1 if he==0 else 2 if he<=2 else 3,
    }
    total=sum(comp.values())
    klass="A" if total<=6 else "B" if total<=9 else "C"
    return {"id":"child-pugh","status":"complete","components":comp,"total":total,"class":klass,"range":[5,15],
            "warning":"Child-Pugh was developed for chronic liver disease/cirrhosis; subjective ascites/encephalopathy grading and etiology-specific bilirubin variants require clinical context.",
            "source":SOURCES["child-pugh"]}

def calculate_kings_college(data):
    if data.get("paracetamol_related") is None: raise ValueError("paracetamol_related required")
    _bool(data["paracetamol_related"],"paracetamol_related")
    if data["paracetamol_related"]:
        req=("arterial_ph_after_resuscitation","hours_since_ingestion","lactate_mmol_L_after_resuscitation","encephalopathy_grade","creatinine_umol_L","inr")
        missing=[k for k in req if data.get(k) is None]
        if missing: raise ValueError("missing paracetamol King's College inputs: "+", ".join(missing))
        ph=_num(data["arterial_ph_after_resuscitation"],"arterial_ph_after_resuscitation"); hours=_num(data["hours_since_ingestion"],"hours_since_ingestion"); lact=_num(data["lactate_mmol_L_after_resuscitation"],"lactate_mmol_L_after_resuscitation"); he=int(_num(data["encephalopathy_grade"],"encephalopathy_grade")); cr=_num(data["creatinine_umol_L"],"creatinine_umol_L"); inr=_num(data["inr"],"inr")
        ph_criterion=ph<7.3 and hours>24
        lactate_criterion=lact>3.0
        triad=(he>3 and cr>300 and inr>6.5)
        meets=ph_criterion or lactate_criterion or triad
        return {"id":"kings-college","status":"complete","etiology":"paracetamol","meets_criteria":meets,
                "criteria":{"ph_lt7_3_after_resuscitation_and_gt24h":ph_criterion,"lactate_gt3_after_resuscitation":lactate_criterion,"grade4_he_creatinine_gt300_inr_gt6_5_triad":triad},
                "warning":"King's College criteria support urgent transplant-center assessment in acute liver failure; absence of criteria does not justify delaying transfer or specialist consultation.",
                "source":SOURCES["kings-college"]}
    req=("inr","age","unfavorable_etiology","jaundice_to_encephalopathy_days","bilirubin_umol_L")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing non-paracetamol King's College inputs: "+", ".join(missing))
    inr=_num(data["inr"],"inr"); age=_num(data["age"],"age"); interval=_num(data["jaundice_to_encephalopathy_days"],"jaundice_to_encephalopathy_days"); bili=_num(data["bilirubin_umol_L"],"bilirubin_umol_L")
    _bool(data["unfavorable_etiology"],"unfavorable_etiology")
    factors={
      "unfavorable_etiology":data["unfavorable_etiology"],
      "age_lt10_or_gt40":age<10 or age>40,
      "jaundice_to_encephalopathy_gt7d":interval>7,
      "bilirubin_gt300_umol_L":bili>300,
      "inr_gt3_5":inr>3.5,
    }
    meets=inr>6.5 or sum(1 for v in factors.values() if v)>=3
    return {"id":"kings-college","status":"complete","etiology":"non_paracetamol","meets_criteria":meets,
            "inr_gt6_5":inr>6.5,"five_factor_count":sum(1 for v in factors.values() if v),"factors":factors,
            "warning":"King's College criteria support emergency liver-transplant evaluation; refer early because criteria have imperfect sensitivity.",
            "source":SOURCES["kings-college"]}
