#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 9 respiratory."""

import math

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)
def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

SOURCES={
 "crb65":{"url":"https://thorax.bmj.com/content/58/5/377","version":"CRB-65"},
 "psi-port":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7135093/","version":"PSI/PORT Fine 1997"},
 "decaf":{"url":"https://pubmed.ncbi.nlm.nih.gov/22895999/","version":"DECAF"},
 "berlin-ards":{"url":"https://pubmed.ncbi.nlm.nih.gov/22797452/","version":"Berlin ARDS 2012"},
}

def calculate_crb65(data):
    req=("confusion","respiratory_rate","systolic_bp_mmHg","diastolic_bp_mmHg","age")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing CRB-65 inputs: "+", ".join(missing))
    _bool(data["confusion"],"confusion")
    rr=_num(data["respiratory_rate"],"respiratory_rate"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); dbp=_num(data["diastolic_bp_mmHg"],"diastolic_bp_mmHg"); age=_num(data["age"],"age")
    comp={
      "confusion":1 if data["confusion"] else 0,
      "respiratory_rate_ge30":1 if rr>=30 else 0,
      "low_bp":1 if (sbp<90 or dbp<=60) else 0,
      "age_ge65":1 if age>=65 else 0,
    }
    total=sum(comp.values())
    return {"id":"crb65","status":"complete","components":comp,"total":total,"range":[0,4],
            "warning":"CRB-65 is a CAP severity aid when urea is unavailable; disposition also depends on oxygenation, comorbidity, complications and clinical judgment.",
            "source":SOURCES["crb65"]}

def calculate_psi_port(data):
    req=("age","sex","nursing_home","neoplastic_disease","liver_disease","heart_failure","cerebrovascular_disease","renal_disease","altered_mental_status","respiratory_rate","systolic_bp_mmHg","temperature_c","heart_rate_bpm")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing PSI core inputs: "+", ".join(missing))
    age=int(_num(data["age"],"age")); sex=str(data["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    bools=("nursing_home","neoplastic_disease","liver_disease","heart_failure","cerebrovascular_disease","renal_disease","altered_mental_status")
    for k in bools:_bool(data[k],k)
    rr=_num(data["respiratory_rate"],"respiratory_rate"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); temp=_num(data["temperature_c"],"temperature_c"); hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")

    step1_low = (
      age<=50 and not any(data[k] for k in ("neoplastic_disease","liver_disease","heart_failure","cerebrovascular_disease","renal_disease"))
      and not data["altered_mental_status"] and rr<30 and sbp>=90 and 35<=temp<40 and hr<125
    )
    if step1_low:
        return {"id":"psi-port","status":"complete","risk_class":"I","score":None,"step1_class_i":True,
                "warning":"PSI Class I derives from the step-1 screen. Site-of-care decisions still require oxygenation, oral-intake, social/support and complication assessment.",
                "source":SOURCES["psi-port"]}

    labs=("arterial_ph","bun_mg_dL","sodium_mmol_L","glucose_mg_dL","hematocrit_percent","pleural_effusion")
    missing_labs=[k for k in labs if data.get(k) is None]
    if data.get("pao2_mmHg") is None and data.get("oxygen_saturation_percent") is None:
        missing_labs.append("pao2_mmHg_or_oxygen_saturation_percent")
    if missing_labs: raise ValueError("PSI step 2 requires: "+", ".join(missing_labs))
    _bool(data["pleural_effusion"],"pleural_effusion")
    ph=_num(data["arterial_ph"],"arterial_ph"); bun=_num(data["bun_mg_dL"],"bun_mg_dL"); na=_num(data["sodium_mmol_L"],"sodium_mmol_L"); glucose=_num(data["glucose_mg_dL"],"glucose_mg_dL"); hct=_num(data["hematocrit_percent"],"hematocrit_percent")
    oxygen_abnormal=False
    if data.get("pao2_mmHg") is not None: oxygen_abnormal=_num(data["pao2_mmHg"],"pao2_mmHg")<60
    elif data.get("oxygen_saturation_percent") is not None: oxygen_abnormal=_num(data["oxygen_saturation_percent"],"oxygen_saturation_percent")<90

    score=age-(10 if sex in {"female","f"} else 0)
    score+=10 if data["nursing_home"] else 0
    score+=30 if data["neoplastic_disease"] else 0
    score+=20 if data["liver_disease"] else 0
    score+=10 if data["heart_failure"] else 0
    score+=10 if data["cerebrovascular_disease"] else 0
    score+=10 if data["renal_disease"] else 0
    score+=20 if data["altered_mental_status"] else 0
    score+=20 if rr>=30 else 0
    score+=20 if sbp<90 else 0
    score+=15 if (temp<35 or temp>=40) else 0
    score+=10 if hr>=125 else 0
    score+=30 if ph<7.35 else 0
    score+=20 if bun>=30 else 0
    score+=20 if na<130 else 0
    score+=10 if glucose>=250 else 0
    score+=10 if hct<30 else 0
    score+=10 if oxygen_abnormal else 0
    score+=10 if data["pleural_effusion"] else 0
    klass="II" if score<=70 else "III" if score<=90 else "IV" if score<=130 else "V"
    return {"id":"psi-port","status":"complete","risk_class":klass,"score":score,"step1_class_i":False,
            "warning":"PSI is a mortality-risk/site-of-care aid, not a stand-alone severity or ICU rule; it may underweight severe hypoxemia or social barriers in younger patients.",
            "source":SOURCES["psi-port"]}

def calculate_decaf(data):
    req=("emrcd_category","eosinophils_10e9_L","consolidation","arterial_ph","atrial_fibrillation")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing DECAF inputs: "+", ".join(missing))
    dysp=str(data["emrcd_category"]).strip().lower()
    dmap={"below_5a":0,"5a":1,"5b":2}
    if dysp not in dmap: raise ValueError("emrcd_category must be below_5a/5a/5b")
    eos=_num(data["eosinophils_10e9_L"],"eosinophils_10e9_L"); ph=_num(data["arterial_ph"],"arterial_ph")
    _bool(data["consolidation"],"consolidation"); _bool(data["atrial_fibrillation"],"atrial_fibrillation")
    comp={
      "dyspnea":dmap[dysp],
      "eosinopenia_lt_0_05":1 if eos<0.05 else 0,
      "consolidation":1 if data["consolidation"] else 0,
      "acidemia_ph_lt_7_3":1 if ph<7.3 else 0,
      "atrial_fibrillation":1 if data["atrial_fibrillation"] else 0,
    }
    total=sum(comp.values())
    band="low_0_1" if total<=1 else "moderate_2" if total==2 else "high_3_6"
    return {"id":"decaf","status":"complete","components":comp,"total":total,"range":[0,6],"risk_band":band,
            "warning":"DECAF was developed for hospitalised acute COPD exacerbations and is a mortality-risk tool, not a treatment rule.",
            "source":SOURCES["decaf"]}

def classify_berlin_ards(data):
    req=("within_1_week","bilateral_opacities_not_explained_by_effusions_collapse_nodules","respiratory_failure_not_fully_explained_by_cardiac_failure_or_fluid_overload","pao2_fio2_mmHg","peep_or_cpap_cmH2O")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Berlin ARDS inputs: "+", ".join(missing))
    for k in req[:3]:_bool(data[k],k)
    pf=_num(data["pao2_fio2_mmHg"],"pao2_fio2_mmHg"); peep=_num(data["peep_or_cpap_cmH2O"],"peep_or_cpap_cmH2O")
    criteria_ok=data["within_1_week"] and data["bilateral_opacities_not_explained_by_effusions_collapse_nodules"] and data["respiratory_failure_not_fully_explained_by_cardiac_failure_or_fluid_overload"] and peep>=5 and pf<=300
    severity=None
    if criteria_ok:
        severity="severe" if pf<=100 else "moderate" if pf<=200 else "mild"
    return {"id":"berlin-ards","status":"complete","meets_berlin_ards":criteria_ok,"severity":severity,
            "version":"Berlin 2012",
            "warning":"This is the Berlin 2012 definition only. Do not silently substitute the newer Global ARDS Definition, which has different non-intubated/SF criteria.",
            "source":SOURCES["berlin-ards"]}
