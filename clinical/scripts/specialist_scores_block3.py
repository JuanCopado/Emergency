#!/usr/bin/env python3
"""SPECIALIST block 3: ICU / respiratory / trauma."""

import math

SOURCES={
 "apache2":{"url":"https://www.msdmanuals.com/professional/multimedia/table/acute-physiologic-assessment-and-chronic-health-evaluation-apache-ii-scoring-system","version":"APACHE II"},
 "saps3":{"url":"https://pubmed.ncbi.nlm.nih.gov/16450055/","version":"SAPS 3"},
 "bps":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC2391268/","version":"Behavioral Pain Scale 3-12"},
 "age-shock-index":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6698590/","version":"Age Shock Index"},
 "smart-cop":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7147127/","version":"SMART-COP 0-11"},
 "mmrc":{"url":"https://goldcopd.org/","version":"mMRC 0-4"},
 "hacor":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC9225644/","version":"HACOR 0-25"},
 "niss":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8858478/","version":"NISS 0-75"},
 "triss":{"url":"https://pubmed.ncbi.nlm.nih.gov/3106646/","version":"TRISS MTOS coefficients"},
 "nexus-head-ct":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC5507397/","version":"NEXUS Head CT"},
}

def _num(v,n):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v): raise ValueError(f"{n} must be finite")
    return float(v)
def _bool(v,n):
    if not isinstance(v,bool): raise ValueError(f"{n} must be boolean")
    return v

def _apache_temp(x):
    return 4 if x>=41 or x<=29.9 else 3 if x>=39 or x<=31.9 else 2 if 32<=x<=33.9 else 1 if 38.5<=x<=38.9 or 34<=x<=35.9 else 0
def _apache_map(x):
    return 4 if x>=160 or x<=49 else 3 if 130<=x<=159 else 2 if 110<=x<=129 or 50<=x<=69 else 0
def _apache_hr(x):
    return 4 if x>=180 or x<=39 else 3 if 140<=x<=179 or 40<=x<=54 else 2 if 110<=x<=139 or 55<=x<=69 else 0
def _apache_rr(x):
    return 4 if x>=50 or x<=5 else 3 if 35<=x<=49 else 2 if 6<=x<=9 else 1 if 25<=x<=34 or 10<=x<=11 else 0
def _apache_ph(x):
    return 4 if x>=7.7 or x<7.15 else 3 if 7.6<=x<7.7 or 7.15<=x<7.25 else 2 if 7.25<=x<7.33 else 1 if 7.5<=x<7.6 else 0
def _apache_na(x):
    return 4 if x>=180 or x<=110 else 3 if 160<=x<=179 or 111<=x<=119 else 2 if 120<=x<=129 else 1 if 155<=x<=159 else 0
def _apache_k(x):
    return 4 if x>=7 or x<2.5 else 3 if 6<=x<7 else 2 if 2.5<=x<3 else 1 if 5.5<=x<6 or 3<=x<3.5 else 0
def _apache_hct(x):
    return 4 if x>=60 or x<20 else 2 if 50<=x<60 or 20<=x<30 else 1 if 46<=x<50 else 0
def _apache_wbc(x):
    return 4 if x>=40 or x<1 else 2 if 1<=x<3 else 1 if 15<=x<40 else 0

def calculate_apache2(d):
    req=("temperature_c_core","map_mmHg","heart_rate_bpm","respiratory_rate","fio2_fraction",
         "arterial_ph","sodium_mmol_L","potassium_mmol_L","creatinine_mg_dL","acute_renal_failure",
         "hematocrit_percent","wbc_10e3_uL","gcs","age","severe_chronic_health","admission_type")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing APACHE II inputs: "+", ".join(miss))
    vals={k:_num(d[k],k) for k in ("temperature_c_core","map_mmHg","heart_rate_bpm","respiratory_rate","fio2_fraction","arterial_ph","sodium_mmol_L","potassium_mmol_L","creatinine_mg_dL","hematocrit_percent","wbc_10e3_uL","gcs","age")}
    _bool(d["acute_renal_failure"],"acute_renal_failure"); _bool(d["severe_chronic_health"],"severe_chronic_health")
    fio2=vals["fio2_fraction"]
    if fio2>=0.5:
        if d.get("aa_gradient_mmHg") is None: raise ValueError("aa_gradient_mmHg required when FiO2 >=0.5")
        aa=_num(d["aa_gradient_mmHg"],"aa_gradient_mmHg")
        oxy=4 if aa>=500 else 3 if aa>=350 else 2 if aa>=200 else 0
    else:
        if d.get("pao2_mmHg") is None: raise ValueError("pao2_mmHg required when FiO2 <0.5")
        p=_num(d["pao2_mmHg"],"pao2_mmHg")
        oxy=0 if p>70 else 1 if p>=61 else 3 if p>=55 else 4
    cr=vals["creatinine_mg_dL"]
    crpts=4 if cr>=3.5 else 3 if cr>=2 else 2 if cr>=1.5 else 0 if cr>=0.6 else 2
    if d["acute_renal_failure"] and cr>=1.5: crpts*=2
    g=int(vals["gcs"])
    if g<3 or g>15: raise ValueError("gcs must be 3-15")
    aps={
      "temperature":_apache_temp(vals["temperature_c_core"]),"map":_apache_map(vals["map_mmHg"]),
      "heart_rate":_apache_hr(vals["heart_rate_bpm"]),"respiratory_rate":_apache_rr(vals["respiratory_rate"]),
      "oxygenation":oxy,"arterial_ph":_apache_ph(vals["arterial_ph"]),"sodium":_apache_na(vals["sodium_mmol_L"]),
      "potassium":_apache_k(vals["potassium_mmol_L"]),"creatinine":crpts,"hematocrit":_apache_hct(vals["hematocrit_percent"]),
      "wbc":_apache_wbc(vals["wbc_10e3_uL"]),"gcs":15-g
    }
    aps_total=sum(aps.values())
    age=vals["age"]; agepts=0 if age<45 else 2 if age<55 else 3 if age<65 else 5 if age<75 else 6
    adm=str(d["admission_type"]).strip().lower()
    if adm not in {"nonoperative_or_emergency_postop","elective_postop"}: raise ValueError("unsupported admission_type")
    chronic=0
    if d["severe_chronic_health"]: chronic=5 if adm=="nonoperative_or_emergency_postop" else 2
    total=aps_total+agepts+chronic
    return {"id":"apache2","status":"complete","acute_physiology_components":aps,"acute_physiology_total":aps_total,
            "age_points":agepts,"chronic_health_points":chronic,"total":total,"range":[0,71],
            "warning":"APACHE II is an ICU severity score; mortality estimates require diagnostic-category calibration and should not be inferred from the raw total alone.",
            "source":SOURCES["apache2"]}

def prepare_saps3(d):
    if d.get("saps3_score") is None: raise ValueError("saps3_score from validated SAPS 3 worksheet required")
    score=int(_num(d["saps3_score"],"saps3_score"))
    if score<16 or score>217: raise ValueError("SAPS 3 score must be 16-217")
    return {"id":"saps3","status":"validated_score_wrapper","score":score,
            "mortality_probability":None,
            "warning":"SAPS 3 mortality conversion is calibration/region dependent. This wrapper preserves the validated score but does not invent a mortality probability without a specified published equation.",
            "source":SOURCES["saps3"]}

BPS_MAPS={
 "facial":{"relaxed":1,"partially_tightened":2,"fully_tightened":3,"grimacing":4},
 "upper_limbs":{"no_movement":1,"partially_bent":2,"fully_bent_finger_flexion":3,"permanently_retracted":4},
 "ventilation":{"tolerating":1,"coughing_but_tolerating":2,"fighting_ventilator":3,"unable_to_control_ventilation":4},
}
def calculate_bps(d):
    c={}
    for k,m in BPS_MAPS.items():
        v=str(d.get(k,"")).strip().lower()
        if v not in m: raise ValueError(f"unsupported BPS {k}")
        c[k]=m[v]
    return {"id":"bps","status":"complete","components":c,"total":sum(c.values()),"range":[3,12],"source":SOURCES["bps"]}

def calculate_age_shock_index(d):
    for k in ("age","heart_rate_bpm","systolic_bp_mmHg"):
        if d.get(k) is None: raise ValueError("missing age shock index input: "+k)
    age=_num(d["age"],"age"); hr=_num(d["heart_rate_bpm"],"hr"); sbp=_num(d["systolic_bp_mmHg"],"sbp")
    if sbp<=0: raise ValueError("SBP must be >0")
    si=hr/sbp
    return {"id":"age-shock-index","status":"complete","shock_index":si,"value":age*si,"unit":"age*ratio","source":SOURCES["age-shock-index"]}

def calculate_smart_cop(d):
    req=("age","systolic_bp_mmHg","multilobar_infiltrates","albumin_g_L","respiratory_rate","heart_rate_bpm","confusion","arterial_ph")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing SMART-COP inputs: "+", ".join(miss))
    age=_num(d["age"],"age"); sbp=_num(d["systolic_bp_mmHg"],"sbp"); alb=_num(d["albumin_g_L"],"albumin"); rr=_num(d["respiratory_rate"],"rr"); hr=_num(d["heart_rate_bpm"],"hr"); ph=_num(d["arterial_ph"],"ph")
    _bool(d["multilobar_infiltrates"],"multilobar_infiltrates"); _bool(d["confusion"],"confusion")
    resp_thresh=25 if age<=50 else 30
    oxy_abnormal=None
    if d.get("pao2_mmHg") is not None:
        pa=_num(d["pao2_mmHg"],"pao2"); oxy_abnormal=pa<(70 if age<=50 else 60)
    elif d.get("spo2_percent") is not None:
        sp=_num(d["spo2_percent"],"spo2"); oxy_abnormal=sp<=(93 if age<=50 else 90)
    elif d.get("pao2_fio2") is not None:
        pf=_num(d["pao2_fio2"],"pao2_fio2"); oxy_abnormal=pf<(333 if age<=50 else 250)
    else: raise ValueError("SMART-COP requires PaO2, SpO2, or P/F oxygenation input")
    c={"sbp_lt90":2 if sbp<90 else 0,"multilobar":1 if d["multilobar_infiltrates"] else 0,"albumin_lt35":1 if alb<35 else 0,
       "rr_high":1 if rr>=resp_thresh else 0,"hr_ge125":1 if hr>=125 else 0,"confusion":1 if d["confusion"] else 0,
       "oxygenation":2 if oxy_abnormal else 0,"ph_lt7_35":2 if ph<7.35 else 0}
    total=sum(c.values()); band="low_0_2" if total<=2 else "moderate_3_4" if total<=4 else "high_5_6" if total<=6 else "very_high_ge7"
    return {"id":"smart-cop","status":"complete","components":c,"total":total,"range":[0,11],"risk_band":band,"source":SOURCES["smart-cop"]}

def calculate_mmrc(d):
    grade=d.get("grade")
    if grade is None: raise ValueError("mMRC requires explicit patient-assigned/clinician-recorded grade 0-4")
    g=int(_num(grade,"grade"))
    if g not in range(5): raise ValueError("mMRC grade must be 0-4")
    return {"id":"mmrc","status":"complete","grade":g,"range":[0,4],"source":SOURCES["mmrc"]}

def calculate_hacor(d):
    req=("heart_rate_bpm","arterial_ph","gcs","pao2_fio2","respiratory_rate")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing HACOR inputs: "+", ".join(miss))
    hr=_num(d["heart_rate_bpm"],"hr"); ph=_num(d["arterial_ph"],"ph"); g=int(_num(d["gcs"],"gcs")); pf=_num(d["pao2_fio2"],"pf"); rr=_num(d["respiratory_rate"],"rr")
    h=1 if hr>120 else 0
    a=0 if ph>=7.35 else 2 if ph>=7.30 else 3 if ph>=7.25 else 4
    c=0 if g==15 else 2 if g>=13 else 5 if g>=11 else 10
    o=0 if pf>=201 else 2 if pf>=176 else 3 if pf>=151 else 4 if pf>=126 else 5 if pf>=101 else 6
    r=0 if rr<=30 else 1 if rr<=35 else 2 if rr<=40 else 3 if rr<=45 else 4
    comp={"heart_rate":h,"acidosis":a,"consciousness":c,"oxygenation":o,"respiratory_rate":r}
    return {"id":"hacor","status":"complete","components":comp,"total":sum(comp.values()),"range":[0,25],"source":SOURCES["hacor"]}

def calculate_niss(d):
    scores=d.get("ais_injury_scores")
    if not isinstance(scores,list) or not scores: raise ValueError("ais_injury_scores list required")
    vals=[int(_num(x,"AIS")) for x in scores]
    if any(x<1 or x>6 for x in vals): raise ValueError("AIS scores must be 1-6")
    if 6 in vals: total=75
    else:
        top=sorted(vals,reverse=True)[:3]
        total=sum(x*x for x in top)
    return {"id":"niss","status":"complete","total":total,"range":[1,75],"source":SOURCES["niss"]}

def calculate_triss(d):
    req=("rts","iss","age","trauma_type")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing TRISS inputs: "+", ".join(miss))
    rts=_num(d["rts"],"rts"); iss=_num(d["iss"],"iss"); age=_num(d["age"],"age")
    typ=str(d["trauma_type"]).strip().lower()
    age_index=1 if age>=55 else 0
    if typ=="blunt": b=-0.4499+0.8085*rts-0.0835*iss-1.7430*age_index
    elif typ=="penetrating": b=-2.5355+0.9934*rts-0.0651*iss-1.1360*age_index
    else: raise ValueError("trauma_type must be blunt or penetrating")
    ps=1/(1+math.exp(-b))
    return {"id":"triss","status":"complete","probability_survival_legacy_mtos":ps,
            "warning":"Uses classic MTOS TRISS coefficients; calibration is historical and should not be treated as a contemporary universal individual prognosis.",
            "source":SOURCES["triss"]}

def calculate_nexus_head_ct(d):
    keys=("skull_fracture","scalp_hematoma","neurologic_deficit","abnormal_alertness","abnormal_behavior","persistent_vomiting","coagulopathy")
    miss=[k for k in keys if d.get(k) is None]
    if d.get("age") is None: miss.append("age")
    if miss: raise ValueError("missing NEXUS Head CT inputs: "+", ".join(miss))
    for k in keys:_bool(d[k],k)
    age=_num(d["age"],"age")
    criteria={**{k:d[k] for k in keys},"age_ge65":age>=65}
    positive=[k for k,v in criteria.items() if v]
    return {"id":"nexus-head-ct","status":"complete","criteria":criteria,"positive_count":len(positive),
            "low_risk_all_absent":len(positive)==0,"source":SOURCES["nexus-head-ct"]}
