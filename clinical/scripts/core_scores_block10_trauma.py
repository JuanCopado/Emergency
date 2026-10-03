#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 10 trauma."""

import math

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)
def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def _rts_code_gcs(g):
    return 4 if g>=13 else 3 if g>=9 else 2 if g>=6 else 1 if g>=4 else 0
def _rts_code_sbp(s):
    return 4 if s>89 else 3 if s>=76 else 2 if s>=50 else 1 if s>=1 else 0
def _rts_code_rr(r):
    return 4 if 10<=r<=29 else 3 if r>29 else 2 if r>=6 else 1 if r>=1 else 0

def calculate_rts(data):
    for k in ("gcs","systolic_bp_mmHg","respiratory_rate"):
        if data.get(k) is None: raise ValueError("missing RTS input: "+k)
    g=int(_num(data["gcs"],"gcs")); s=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); r=_num(data["respiratory_rate"],"respiratory_rate")
    if not 3<=g<=15 or s<0 or r<0: raise ValueError("invalid RTS input")
    codes={"gcs":_rts_code_gcs(g),"sbp":_rts_code_sbp(s),"rr":_rts_code_rr(r)}
    score=0.9368*codes["gcs"]+0.7326*codes["sbp"]+0.2908*codes["rr"]
    return {"id":"rts","status":"complete","coded_values":codes,"value":score,"range":[0,7.8408],
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC5496419/","version":"Revised Trauma Score"}}

ISS_REGIONS=("head_neck","face","chest","abdomen_pelvic_contents","extremities_pelvic_girdle","external")
def calculate_iss(data):
    ais=data.get("highest_ais_by_region")
    if not isinstance(ais,dict): raise ValueError("ISS requires highest_ais_by_region")
    missing=[k for k in ISS_REGIONS if ais.get(k) is None]
    if missing: raise ValueError("missing ISS regions: "+", ".join(missing))
    vals={}
    for k in ISS_REGIONS:
        v=ais[k]
        if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=6: raise ValueError(f"{k} AIS must be 0-6")
        vals[k]=v
    if 6 in vals.values(): total=75
    else:
        top=sorted(vals.values(),reverse=True)[:3]
        total=sum(x*x for x in top)
    return {"id":"iss","status":"complete","highest_ais_by_region":vals,"total":total,"range":[0,75],
            "warning":"ISS requires valid AIS coding and uses only the highest AIS in each ISS body region.",
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC2568949/","version":"ISS"}}

def calculate_abc_massive_transfusion(data):
    req=("penetrating_mechanism","positive_fast","systolic_bp_mmHg","heart_rate_bpm")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing ABC inputs: "+", ".join(missing))
    _bool(data["penetrating_mechanism"],"penetrating_mechanism"); _bool(data["positive_fast"],"positive_fast")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    comp={"penetrating_mechanism":1 if data["penetrating_mechanism"] else 0,"positive_fast":1 if data["positive_fast"] else 0,"sbp_le90":1 if sbp<=90 else 0,"hr_ge120":1 if hr>=120 else 0}
    total=sum(comp.values())
    return {"id":"abc-massive-transfusion","status":"complete","components":comp,"total":total,"range":[0,4],"abc_positive_ge2":total>=2,
            "warning":"ABC supports early massive-transfusion assessment; activation must follow hemorrhage physiology and local MTP protocol.",
            "source":{"url":"https://pubmed.ncbi.nlm.nih.gov/19204506/","version":"Assessment of Blood Consumption"}}

def calculate_canadian_ct_head(data):
    req=("eligible_minor_head_injury","age","gcs_at_2h","suspected_open_or_depressed_skull_fracture","basal_skull_fracture_sign","vomiting_episodes","retrograde_amnesia_minutes","dangerous_mechanism")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing CCHR inputs: "+", ".join(missing))
    if data["eligible_minor_head_injury"] is not True: raise ValueError("Canadian CT Head Rule requires explicit eligible minor head injury population")
    age=_num(data["age"],"age"); g=int(_num(data["gcs_at_2h"],"gcs_at_2h")); vom=int(_num(data["vomiting_episodes"],"vomiting_episodes")); amn=_num(data["retrograde_amnesia_minutes"],"retrograde_amnesia_minutes")
    if age<16 or not 13<=g<=15: raise ValueError("CCHR requires age >=16 and eligible GCS 13-15 population")
    for k in ("suspected_open_or_depressed_skull_fracture","basal_skull_fracture_sign","dangerous_mechanism"):_bool(data[k],k)
    high={
      "gcs_lt15_at_2h":g<15,
      "suspected_open_or_depressed_skull_fracture":data["suspected_open_or_depressed_skull_fracture"],
      "basal_skull_fracture_sign":data["basal_skull_fracture_sign"],
      "vomiting_ge2":vom>=2,
      "age_ge65":age>=65,
    }
    medium={"retrograde_amnesia_ge30min":amn>=30,"dangerous_mechanism":data["dangerous_mechanism"]}
    return {"id":"canadian-ct-head","status":"complete","high_risk":high,"medium_risk":medium,
            "ct_indicated_by_rule":any(high.values()) or any(medium.values()),
            "source":{"url":"https://pubmed.ncbi.nlm.nih.gov/11356436/","version":"Canadian CT Head Rule"}}

def calculate_canadian_cspine(data):
    req=("eligible_alert_stable_gcs15","age","dangerous_mechanism","paresthesias_extremities","simple_rear_end_mvc","sitting_position_ed","ambulatory_any_time","delayed_neck_pain","midline_cspine_tenderness","can_rotate_45_left_and_right")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Canadian C-Spine inputs: "+", ".join(missing))
    if data["eligible_alert_stable_gcs15"] is not True: raise ValueError("Canadian C-Spine Rule requires alert stable GCS 15 eligible population")
    age=_num(data["age"],"age")
    for k in req:
        if k not in ("age","eligible_alert_stable_gcs15"):_bool(data[k],k)
    high=age>=65 or data["dangerous_mechanism"] or data["paresthesias_extremities"]
    if high: decision="imaging_required_high_risk"
    else:
        low=any((data["simple_rear_end_mvc"],data["sitting_position_ed"],data["ambulatory_any_time"],data["delayed_neck_pain"],not data["midline_cspine_tenderness"]))
        if not low: decision="imaging_required_no_low_risk_factor"
        elif data["can_rotate_45_left_and_right"]: decision="no_imaging_by_rule"
        else: decision="imaging_required_unable_rotate_45"
    return {"id":"canadian-cspine","status":"complete","decision":decision,
            "source":{"url":"https://jamanetwork.com/journals/jama/fullarticle/194296","version":"Canadian C-Spine Rule"}}

def calculate_nexus_cspine(data):
    req=("eligible_blunt_cspine_assessment","midline_cervical_tenderness","focal_neurologic_deficit","normal_alertness","intoxication","painful_distracting_injury")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing NEXUS inputs: "+", ".join(missing))
    if data["eligible_blunt_cspine_assessment"] is not True: raise ValueError("NEXUS requires eligible blunt trauma cervical-spine assessment")
    for k in req[1:]:_bool(data[k],k)
    low=(not data["midline_cervical_tenderness"] and not data["focal_neurologic_deficit"] and data["normal_alertness"] and not data["intoxication"] and not data["painful_distracting_injury"])
    return {"id":"nexus-cspine","status":"complete","nexus_low_risk":low,"imaging_indicated_by_rule":not low,
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC5994619/","version":"NEXUS C-spine"}}
