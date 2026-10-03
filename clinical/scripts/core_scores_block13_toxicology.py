#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 13 toxicology."""

import math

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)
def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def evaluate_rumack_matthew(data):
    req=("single_acute_ingestion_known_time","hours_since_ingestion","acetaminophen_mcg_mL","extended_release_or_delayed_absorption")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Rumack-Matthew inputs: "+", ".join(missing))
    if data["single_acute_ingestion_known_time"] is not True:
        raise ValueError("Rumack-Matthew cannot be used for unknown-time, repeated supratherapeutic, or staggered ingestion")
    _bool(data["extended_release_or_delayed_absorption"],"extended_release_or_delayed_absorption")
    h=_num(data["hours_since_ingestion"],"hours_since_ingestion")
    level=_num(data["acetaminophen_mcg_mL"],"acetaminophen_mcg_mL")
    if h<4 or h>24: raise ValueError("Rumack-Matthew single-level interpretation is restricted to 4-24 hours")
    treatment_line=150.0*(0.5**((h-4.0)/4.0))
    above=level>=treatment_line
    if data["extended_release_or_delayed_absorption"]:
        status="serial_level_required"
        interpretation="single_point_not_sufficient"
    else:
        status="complete"
        interpretation="at_or_above_150_treatment_line" if above else "below_150_treatment_line"
    return {"id":"rumack-matthew","status":status,"hours":h,"level_mcg_mL":level,
            "treatment_line_mcg_mL":treatment_line,"at_or_above_treatment_line":above,
            "interpretation":interpretation,
            "warning":"Nomogram applies only to a single acute ingestion with a reliable time. Extended-release/delayed absorption requires repeat levels; unknown-time or repeated supratherapeutic ingestion follows a different pathway.",
            "source":{"url":"https://www.merckmanuals.com/professional/injuries-poisoning/poisoning/acetaminophen-poisoning","version":"Rumack-Matthew 150-line"}}

def evaluate_hunter_serotonin(data):
    req=("serotonergic_exposure","spontaneous_clonus","inducible_clonus","ocular_clonus","agitation","diaphoresis","tremor","hyperreflexia","hypertonia","temperature_c")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Hunter inputs: "+", ".join(missing))
    for k in req[:-1]: _bool(data[k],k)
    temp=_num(data["temperature_c"],"temperature_c")
    if not data["serotonergic_exposure"]:
        return {"id":"hunter-serotonin","status":"complete","criteria_met":False,"reason":"no_serotonergic_exposure",
                "source":{"url":"https://pubmed.ncbi.nlm.nih.gov/12925718/","version":"Hunter Serotonin Toxicity Criteria"}}
    met=(
      data["spontaneous_clonus"]
      or (data["inducible_clonus"] and (data["agitation"] or data["diaphoresis"]))
      or (data["ocular_clonus"] and (data["agitation"] or data["diaphoresis"]))
      or (data["tremor"] and data["hyperreflexia"])
      or (data["hypertonia"] and temp>38 and (data["ocular_clonus"] or data["inducible_clonus"]))
    )
    return {"id":"hunter-serotonin","status":"complete","criteria_met":bool(met),
            "warning":"Hunter criteria support diagnosis in a serotonergic exposure context and do not replace evaluation for mimics or severity/complications.",
            "source":{"url":"https://pubmed.ncbi.nlm.nih.gov/12925718/","version":"Hunter Serotonin Toxicity Criteria"}}

CIWA_MAX={"nausea_vomiting":7,"tremor":7,"paroxysmal_sweats":7,"anxiety":7,"agitation":7,
          "tactile_disturbances":7,"auditory_disturbances":7,"visual_disturbances":7,
          "headache_fullness":7,"orientation":4}
def calculate_ciwa_ar(data):
    items=data.get("items")
    if not isinstance(items,dict): raise ValueError("CIWA-Ar requires explicit item scores")
    missing=[k for k in CIWA_MAX if items.get(k) is None]
    if missing: raise ValueError("missing CIWA-Ar items: "+", ".join(missing))
    norm={}
    for k,mx in CIWA_MAX.items():
        v=items[k]
        if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=mx: raise ValueError(f"{k} must be integer 0-{mx}")
        norm[k]=v
    total=sum(norm.values())
    band="minimal_lt8" if total<8 else "mild_8_15" if total<=15 else "moderate_severe_ge16"
    return {"id":"ciwa-ar","status":"complete","items":norm,"total":total,"range":[0,67],"severity_band":band,
            "warning":"CIWA-Ar requires a communicative patient and serial clinician assessment; it is unreliable in delirium, severe cognitive impairment or inability to communicate.",
            "source":{"url":"https://pubmed.ncbi.nlm.nih.gov/2597811/","version":"CIWA-Ar"}}

COWS_ALLOWED={
 "resting_pulse":{0,1,2,4},"sweating":{0,1,2,3,4},"restlessness":{0,1,3,5},
 "pupil_size":{0,1,2,5},"bone_joint_aches":{0,1,2,4},"runny_nose_tearing":{0,1,2,4},
 "gi_upset":{0,1,2,3,5},"tremor":{0,1,2,4},"yawning":{0,1,2,4},
 "anxiety_irritability":{0,1,2,4},"gooseflesh":{0,3,5},
}
def calculate_cows(data):
    items=data.get("items")
    if not isinstance(items,dict): raise ValueError("COWS requires explicit item scores")
    missing=[k for k in COWS_ALLOWED if items.get(k) is None]
    if missing: raise ValueError("missing COWS items: "+", ".join(missing))
    norm={}
    for k,allowed in COWS_ALLOWED.items():
        v=items[k]
        if isinstance(v,bool) or not isinstance(v,int) or v not in allowed: raise ValueError(f"{k}: invalid COWS item score")
        norm[k]=v
    total=sum(norm.values())
    band="mild_5_12" if 5<=total<=12 else "moderate_13_24" if total<=24 and total>=13 else "moderately_severe_25_36" if total<=36 and total>=25 else "severe_gt36" if total>36 else "minimal_0_4"
    return {"id":"cows","status":"complete","items":norm,"total":total,"range":[0,48],"severity_band":band,
            "warning":"COWS is clinician-administered and measures opioid withdrawal severity; treatment timing must consider last opioid exposure and risk of precipitated withdrawal.",
            "source":{"url":"https://nida.nih.gov/sites/default/files/ClinicalOpiateWithdrawalScale.pdf","version":"COWS"}}
