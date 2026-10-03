#!/usr/bin/env python3
"""Source-encoded / official-wrapper CORE tools — block 14 adult criteria, geriatrics, ICU, oncology."""

def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def classify_duke_iscvid(data):
    for k in ("pathologic_definite","major_count","minor_count","firm_alternative_diagnosis"):
        if data.get(k) is None: raise ValueError("missing Duke-ISCVID input: "+k)
    _bool(data["pathologic_definite"],"pathologic_definite"); _bool(data["firm_alternative_diagnosis"],"firm_alternative_diagnosis")
    major=int(data["major_count"]); minor=int(data["minor_count"])
    if major<0 or minor<0: raise ValueError("criteria counts cannot be negative")
    if data["pathologic_definite"]: cls="definite"
    elif data["firm_alternative_diagnosis"]: cls="rejected"
    elif major>=2 or (major>=1 and minor>=3) or minor>=5: cls="definite"
    elif (major>=1 and minor>=1) or minor>=3: cls="possible"
    else: cls="rejected"
    return {"id":"duke-iscvid","status":"complete_from_adjudicated_criteria","classification":cls,
            "major_count":major,"minor_count":minor,
            "warning":"This classifier requires Major/Minor criteria already adjudicated against the full 2023 Duke-ISCVID microbiology, imaging, surgical and minor definitions; it does not infer those criteria from raw data.",
            "source":{"url":"https://academic.oup.com/cid/article/77/4/518/7151107","version":"2023 Duke-ISCVID"}}

def classify_tokyo_biliary(data):
    condition=str(data.get("condition","")).lower()
    if condition not in {"acute_cholangitis","acute_cholecystitis"}: raise ValueError("condition must be acute_cholangitis or acute_cholecystitis")
    organ=data.get("organ_dysfunction")
    if not isinstance(organ,dict): raise ValueError("organ_dysfunction object required")
    for k,v in organ.items(): _bool(v,k)
    if any(organ.values()): grade="III"
    elif condition=="acute_cholangitis":
        req=("wbc_10e9_L","temperature_c","age","bilirubin_mg_dL","albumin_below_0_7_lower_limit_normal")
        for k in req:
            if data.get(k) is None: raise ValueError("missing Tokyo cholangitis input: "+k)
        _bool(data["albumin_below_0_7_lower_limit_normal"],"albumin_below_0_7_lower_limit_normal")
        moderate=sum([
          data["wbc_10e9_L"]>12 or data["wbc_10e9_L"]<4,
          data["temperature_c"]>=39,
          data["age"]>=75,
          data["bilirubin_mg_dL"]>=5,
          data["albumin_below_0_7_lower_limit_normal"],
        ])>=2
        grade="II" if moderate else "I"
    else:
        req=("wbc_10e9_L","palpable_tender_ruq_mass","symptom_duration_h","marked_local_inflammation")
        for k in req:
            if data.get(k) is None: raise ValueError("missing Tokyo cholecystitis input: "+k)
        _bool(data["palpable_tender_ruq_mass"],"palpable_tender_ruq_mass"); _bool(data["marked_local_inflammation"],"marked_local_inflammation")
        moderate=(data["wbc_10e9_L"]>18 or data["palpable_tender_ruq_mass"] or data["symptom_duration_h"]>72 or data["marked_local_inflammation"])
        grade="II" if moderate else "I"
    return {"id":"tokyo-biliary","status":"complete","condition":condition,"grade":grade,
            "warning":"Tokyo severity grading assumes the diagnosis has already been established; it does not itself diagnose cholangitis/cholecystitis.",
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC3429782/","version":"Tokyo severity criteria"}}

def calculate_four_at(data):
    req=("alertness","amt4_mistakes","attention_months_backward","acute_change_or_fluctuation")
    for k in req:
        if data.get(k) is None: raise ValueError("missing 4AT input: "+k)
    alert=str(data["alertness"]).lower()
    if alert not in {"normal","clearly_abnormal"}: raise ValueError("alertness invalid")
    amt=data["amt4_mistakes"]
    if amt=="untestable": amt_score=2
    else:
        amt=int(amt); amt_score=0 if amt==0 else 1 if amt==1 else 2
    att=data["attention_months_backward"]
    if att=="untestable": att_score=2
    else:
        att=int(att); att_score=0 if att>=7 else 1 if att>=1 else 2
    _bool(data["acute_change_or_fluctuation"],"acute_change_or_fluctuation")
    comp={"alertness":0 if alert=="normal" else 4,"amt4":amt_score,"attention":att_score,"acute_change":4 if data["acute_change_or_fluctuation"] else 0}
    total=sum(comp.values())
    band="possible_delirium_ge4" if total>=4 else "possible_cognitive_impairment_1_3" if total>=1 else "no_4at_signal_0"
    return {"id":"four-at","status":"complete","components":comp,"total":total,"range":[0,12],"interpretation":band,
            "source":{"url":"https://www.the4at.com/userguide","version":"4AT"}}

def classify_cam(data, cam_icu=False):
    req=("acute_onset_or_fluctuating_course","inattention","disorganized_thinking","altered_level_of_consciousness")
    for k in req:
        if data.get(k) is None: raise ValueError("missing CAM feature: "+k)
        _bool(data[k],k)
    positive=data["acute_onset_or_fluctuating_course"] and data["inattention"] and (data["disorganized_thinking"] or data["altered_level_of_consciousness"])
    return {"id":"cam-icu" if cam_icu else "cam","status":"complete_from_adjudicated_features","positive":positive,
            "warning":"Features must be assessed with the validated CAM/CAM-ICU bedside method; this logic only applies the published feature-combination rule.",
            "source":{"url":"https://www.icudelirium.org/medical-professionals/downloads/resources-by-category","version":"CAM-ICU" if cam_icu else "CAM"}}

def calculate_rass(data):
    score=data.get("score")
    if isinstance(score,bool) or not isinstance(score,int) or score not in range(-5,5): raise ValueError("RASS score must be integer -5 to +4")
    return {"id":"rass","status":"complete","score":score,"range":[-5,4],
            "warning":"RASS is an observed sedation/agitation state and should be assigned using the bedside stimulation sequence.",
            "source":{"url":"https://www.icudelirium.org/medical-professionals/downloads/resources-by-category","version":"RASS"}}

def calculate_cpot(data):
    items=data.get("items")
    keys=("facial_expression","body_movements","muscle_tension","ventilator_compliance_or_vocalization")
    if not isinstance(items,dict): raise ValueError("CPOT items required")
    for k in keys:
        v=items.get(k)
        if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=2: raise ValueError(f"{k} must be 0-2")
    total=sum(items[k] for k in keys)
    return {"id":"cpot","status":"complete","items":{k:items[k] for k in keys},"total":total,"range":[0,8],
            "warning":"CPOT is for behavioral pain assessment in patients unable to self-report; use self-report when feasible.",
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC9222682/","version":"CPOT"}}

def calculate_mascc(data):
    req=("burden","systolic_bp_mmHg","copd","solid_tumor_or_heme_no_prior_fungal","dehydration_requires_iv","outpatient_at_fever_onset","age")
    for k in req:
        if data.get(k) is None: raise ValueError("missing MASCC input: "+k)
    burden=str(data["burden"]).lower()
    if burden not in {"none_mild","moderate","severe_moribund"}: raise ValueError("burden invalid")
    for k in ("copd","solid_tumor_or_heme_no_prior_fungal","dehydration_requires_iv","outpatient_at_fever_onset"):_bool(data[k],k)
    score=5 if burden=="none_mild" else 3 if burden=="moderate" else 0
    score+=5 if data["systolic_bp_mmHg"]>90 else 0
    score+=4 if not data["copd"] else 0
    score+=4 if data["solid_tumor_or_heme_no_prior_fungal"] else 0
    score+=3 if not data["dehydration_requires_iv"] else 0
    score+=3 if data["outpatient_at_fever_onset"] else 0
    score+=2 if data["age"]<60 else 0
    return {"id":"mascc","status":"complete","total":score,"range":[0,26],"low_risk_ge21":score>=21,
            "warning":"MASCC identifies lower-risk febrile neutropenia; shock, organ dysfunction, uncontrolled infection or other high-risk features override outpatient consideration.",
            "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC4500479/","version":"MASCC Risk Index"}}

def official_wrapper(tool_id, data):
    if tool_id=="clinical-frailty":
        if data.get("permission_or_authorized_use_confirmed") is not True:
            return {"id":tool_id,"status":"permission_required","official_url":"https://www.dal.ca/sites/gmr/our-tools/clinical-frailty-scale.html"}
        score=data.get("explicit_official_score")
        if isinstance(score,bool) or not isinstance(score,int) or not 1<=score<=9: raise ValueError("CFS official score must be 1-9")
        return {"id":tool_id,"status":"explicit_official_result","score":score,"version":"CFS v2.0","official_url":"https://www.dal.ca/sites/gmr/our-tools/clinical-frailty-scale.html"}
    if tool_id=="cssrs":
        return {"id":tool_id,"status":"official_instrument_required","official_url":"https://cssrs.columbia.edu/documents/screening/",
                "warning":"Use the appropriate official C-SSRS version and its triage instructions; this repository does not reproduce or invent a numeric C-SSRS score."}
    raise ValueError("unknown official wrapper")
