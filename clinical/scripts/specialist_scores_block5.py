#!/usr/bin/env python3
"""SPECIALIST block 5: psychiatry / oncology / infection / obstetrics."""

import math

SOURCES={
 "phq9":{"url":"https://pubmed.ncbi.nlm.nih.gov/11556941/","version":"PHQ-9 0-27"},
 "gad7":{"url":"https://pubmed.ncbi.nlm.nih.gov/16717171/","version":"GAD-7 0-21"},
 "cisne":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6404710/","version":"CISNE 0-8"},
 "lrinec":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC5449710/","version":"LRINEC 0-13"},
 "puqe":{"url":"https://www.rcog.org.uk/media/5quba1n4/nvpandhyperemesisvpeer_review.pdf","version":"PUQE-24 3-15"},
 "fullpiers":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7643272/","version":"Original fullPIERS 48-h maternal adverse outcome model"},
}

def _num(v,n):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{n} must be finite")
    return float(v)
def _bool(v,n):
    if not isinstance(v,bool): raise ValueError(f"{n} must be boolean")
    return v

def _questionnaire_scores(items, expected, name):
    if not isinstance(items,list) or len(items)!=expected:
        raise ValueError(f"{name} requires exactly {expected} explicit item scores")
    vals=[]
    for i,x in enumerate(items):
        if isinstance(x,bool) or not isinstance(x,int) or x not in (0,1,2,3):
            raise ValueError(f"{name} item {i+1} must be 0-3")
        vals.append(x)
    return vals

def calculate_phq9(d):
    vals=_questionnaire_scores(d.get("item_scores"),9,"PHQ-9")
    total=sum(vals)
    if total<=4: severity="minimal_0_4"
    elif total<=9: severity="mild_5_9"
    elif total<=14: severity="moderate_10_14"
    elif total<=19: severity="moderately_severe_15_19"
    else: severity="severe_20_27"
    return {
      "id":"phq9","status":"complete","total":total,"range":[0,27],"severity":severity,
      "self_harm_item_positive":vals[8]>0,
      "warning":"PHQ-9 is a screening/severity instrument, not a diagnosis. Any non-zero item 9 requires direct suicide/self-harm assessment; the calculator does not automate a disposition decision.",
      "source":SOURCES["phq9"]}

def calculate_gad7(d):
    vals=_questionnaire_scores(d.get("item_scores"),7,"GAD-7")
    total=sum(vals)
    severity="minimal_0_4" if total<=4 else "mild_5_9" if total<=9 else "moderate_10_14" if total<=14 else "severe_15_21"
    return {"id":"gad7","status":"complete","total":total,"range":[0,21],"severity":severity,
            "warning":"GAD-7 is a screening/severity tool and does not establish an anxiety-disorder diagnosis.","source":SOURCES["gad7"]}

def calculate_cisne(d):
    req=("ecog_ge2","stress_hyperglycemia","copd","cardiovascular_disease","mucositis_grade_ge2","monocytes_per_uL","clinically_stable","solid_tumor")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing CISNE inputs: "+", ".join(miss))
    for k in req:
        if k!="monocytes_per_uL": _bool(d[k],k)
    if not d["clinically_stable"] or not d["solid_tumor"]:
        raise ValueError("CISNE applies to clinically stable febrile neutropenia in solid-tumor patients")
    mono=_num(d["monocytes_per_uL"],"monocytes_per_uL")
    c={"ecog_ge2":2 if d["ecog_ge2"] else 0,"stress_hyperglycemia":2 if d["stress_hyperglycemia"] else 0,
       "copd":1 if d["copd"] else 0,"cardiovascular_disease":1 if d["cardiovascular_disease"] else 0,
       "mucositis_grade_ge2":1 if d["mucositis_grade_ge2"] else 0,"monocytes_lt200":1 if mono<200 else 0}
    total=sum(c.values()); cls="I_low_0" if total==0 else "II_intermediate_1_2" if total<=2 else "III_high_ge3"
    return {"id":"cisne","status":"complete","components":c,"total":total,"range":[0,8],"class":cls,
            "warning":"CISNE is for apparently stable solid-tumor febrile neutropenia; instability or other high-risk features supersede the score.","source":SOURCES["cisne"]}

def calculate_lrinec(d):
    req=("crp_mg_L","wbc_10e3_uL","hemoglobin_g_dL","sodium_mmol_L","creatinine_mg_dL","glucose_mg_dL")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing LRINEC inputs: "+", ".join(miss))
    crp=_num(d["crp_mg_L"],"crp"); wbc=_num(d["wbc_10e3_uL"],"wbc"); hb=_num(d["hemoglobin_g_dL"],"hemoglobin")
    na=_num(d["sodium_mmol_L"],"sodium"); cr=_num(d["creatinine_mg_dL"],"creatinine"); glu=_num(d["glucose_mg_dL"],"glucose")
    c={"crp":4 if crp>=150 else 0,
       "wbc":0 if wbc<15 else 1 if wbc<=25 else 2,
       "hemoglobin":0 if hb>13.5 else 1 if hb>=11 else 2,
       "sodium":2 if na<135 else 0,
       "creatinine":2 if cr>1.6 else 0,
       "glucose":1 if glu>180 else 0}
    total=sum(c.values()); band="low_le5" if total<=5 else "intermediate_6_7" if total<=7 else "high_ge8"
    return {"id":"lrinec","status":"complete","components":c,"total":total,"range":[0,13],"risk_band":band,
            "warning":"LRINEC has insufficient sensitivity to rule out necrotizing soft-tissue infection. A low score must never delay surgical assessment, imaging when appropriate, or empiric treatment when clinical suspicion is high.","source":SOURCES["lrinec"]}

def calculate_puqe24(d):
    req=("nausea_hours","vomiting_count","retching_count")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing PUQE-24 inputs: "+", ".join(miss))
    nausea=_num(d["nausea_hours"],"nausea_hours"); vom=int(_num(d["vomiting_count"],"vomiting_count")); ret=int(_num(d["retching_count"],"retching_count"))
    if nausea<0 or nausea>24 or vom<0 or ret<0: raise ValueError("invalid PUQE-24 values")
    n=1 if nausea==0 else 2 if nausea<=1 else 3 if nausea<=3 else 4 if nausea<=6 else 5
    def countscore(x): return 1 if x==0 else 2 if x<=2 else 3 if x<=4 else 4 if x<=6 else 5
    c={"nausea":n,"vomiting":countscore(vom),"retching":countscore(ret)}
    total=sum(c.values()); sev="mild_le6" if total<=6 else "moderate_7_12" if total<=12 else "severe_13_15"
    return {"id":"puqe","status":"complete","components":c,"total":total,"range":[3,15],"severity":sev,"source":SOURCES["puqe"]}

def calculate_fullpiers(d):
    req=("gestational_age_weeks","chest_pain_or_dyspnea","creatinine_umol_L","platelets_10e9_L","ast_IU_L","spo2_percent")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing fullPIERS inputs: "+", ".join(miss))
    ga=_num(d["gestational_age_weeks"],"gestational_age_weeks"); cr=_num(d["creatinine_umol_L"],"creatinine_umol_L")
    pl=_num(d["platelets_10e9_L"],"platelets_10e9_L"); ast=_num(d["ast_IU_L"],"ast_IU_L"); spo2=_num(d["spo2_percent"],"spo2_percent")
    _bool(d["chest_pain_or_dyspnea"],"chest_pain_or_dyspnea")
    if ga<=0 or cr<0 or pl<0 or ast<0 or not 0<=spo2<=100: raise ValueError("invalid fullPIERS input range")
    x=(2.68 -0.0541*ga +1.23*(1 if d["chest_pain_or_dyspnea"] else 0)
       -0.0271*cr +0.207*pl +0.0000400*(pl**2) +0.0101*ast -0.00000305*(ast**2)
       +0.000250*cr*pl -0.0000699*pl*ast -0.00256*pl*spo2)
    probability=1/(1+math.exp(-x))
    return {"id":"fullpiers","status":"complete","linear_predictor":x,"probability_adverse_maternal_outcome_48h":probability,
            "input_units":{"gestational_age":"weeks","creatinine":"umol/L","platelets":"10^9/L","AST":"IU/L","SpO2":"percent"},
            "warning":"fullPIERS predicts adverse maternal outcomes in preeclampsia; it is an adjunct to obstetric assessment, not an autonomous delivery or transfer decision.","source":SOURCES["fullpiers"]}
