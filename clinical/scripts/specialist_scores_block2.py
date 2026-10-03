#!/usr/bin/env python3
"""SPECIALIST block 2: cardiology / TEV / sepsis / deterioration."""

import math

SOURCES={
  "edacs":{"authority":"Than et al. / ACC chest pain pathway","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC10691881/","version":"EDACS"},
  "orbit-bleeding":{"authority":"O'Brien et al. ORBIT","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC4670965/","version":"ORBIT 0-7"},
  "tisdale-qt":{"authority":"Tisdale QT risk score","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11765673/","version":"Tisdale 0-21"},
  "bova":{"authority":"Bova PE score","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6421363/","version":"Bova 0-7"},
  "sic":{"authority":"ISTH Sepsis-Induced Coagulopathy","url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11415329/","version":"ISTH SIC"},
  "mews":{"authority":"Subbe MEWS","url":"https://www.ncbi.nlm.nih.gov/books/NBK543670/table/ch10.Tab1/","version":"Classic MEWS"},
  "sirs":{"authority":"ACCP/SCCM SIRS criteria","url":"https://www.clevelandclinicmeded.com/medicalpubs/pharmacy/janfeb2002/table1.htm","version":"SIRS 4 criteria"},
}

def _num(v,n):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v): raise ValueError(f"{n} must be finite")
    return float(v)
def _bool(v,n):
    if not isinstance(v,bool): raise ValueError(f"{n} must be boolean")
    return v

def calculate_edacs(d):
    req=("age","sex","known_cad_or_age18_50_ge3_risk_factors","diaphoresis","radiation","pleuritic","palpation_reproduces")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing EDACS inputs: "+", ".join(miss))
    age=_num(d["age"],"age")
    if age<18: raise ValueError("EDACS adult pathway requires age >=18")
    sex=str(d["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    for k in req[2:]: _bool(d[k],k)
    if age<=45: age_pts=2
    elif age<=50: age_pts=4
    elif age<=55: age_pts=6
    elif age<=60: age_pts=8
    elif age<=65: age_pts=10
    elif age<=70: age_pts=12
    elif age<=75: age_pts=14
    elif age<=80: age_pts=16
    elif age<=85: age_pts=18
    else: age_pts=20
    c={
      "age":age_pts,
      "male":6 if sex in {"male","m"} else 0,
      "cad_or_risk_factors":4 if d["known_cad_or_age18_50_ge3_risk_factors"] else 0,
      "diaphoresis":3 if d["diaphoresis"] else 0,
      "radiation":5 if d["radiation"] else 0,
      "pleuritic":-4 if d["pleuritic"] else 0,
      "palpation_reproduces":-6 if d["palpation_reproduces"] else 0,
    }
    total=sum(c.values())
    return {"id":"edacs","status":"complete","components":c,"total":total,"low_score_lt16":total<16,
            "warning":"EDACS score alone is not the EDACS accelerated diagnostic pathway; low-risk discharge additionally requires a non-ischemic ECG and appropriate serial troponin testing.",
            "source":SOURCES["edacs"]}

def calculate_orbit(d):
    req=("age","sex","hemoglobin_g_dL","bleeding_history","egfr_mL_min_1_73m2","antiplatelet")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing ORBIT inputs: "+", ".join(miss))
    age=_num(d["age"],"age"); hb=_num(d["hemoglobin_g_dL"],"hemoglobin_g_dL"); egfr=_num(d["egfr_mL_min_1_73m2"],"egfr")
    sex=str(d["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    _bool(d["bleeding_history"],"bleeding_history"); _bool(d["antiplatelet"],"antiplatelet")
    anemia=hb<13 if sex in {"male","m"} else hb<12
    c={"age_gt74":1 if age>74 else 0,"anemia":2 if anemia else 0,"bleeding_history":2 if d["bleeding_history"] else 0,
       "egfr_lt60":1 if egfr<60 else 0,"antiplatelet":1 if d["antiplatelet"] else 0}
    total=sum(c.values()); band="low_0_2" if total<=2 else "medium_3" if total==3 else "high_ge4"
    return {"id":"orbit-bleeding","status":"complete","components":c,"total":total,"range":[0,7],"risk_band":band,"source":SOURCES["orbit-bleeding"]}

def calculate_tisdale(d):
    req=("age","female","loop_diuretic","potassium_mmol_L","baseline_qtc_ms","acute_mi","qt_prolonging_drug_count","heart_failure","sepsis")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing Tisdale inputs: "+", ".join(miss))
    age=_num(d["age"],"age"); k=_num(d["potassium_mmol_L"],"potassium_mmol_L"); qtc=_num(d["baseline_qtc_ms"],"baseline_qtc_ms")
    for x in ("female","loop_diuretic","acute_mi","heart_failure","sepsis"): _bool(d[x],x)
    n=int(_num(d["qt_prolonging_drug_count"],"qt_prolonging_drug_count"))
    if n<0: raise ValueError("qt_prolonging_drug_count cannot be negative")
    c={"age_ge68":1 if age>=68 else 0,"female":1 if d["female"] else 0,"loop_diuretic":1 if d["loop_diuretic"] else 0,
       "k_le3_5":2 if k<=3.5 else 0,"qtc_ge450":2 if qtc>=450 else 0,"acute_mi":2 if d["acute_mi"] else 0,
       "one_or_more_qt_drug":3 if n>=1 else 0,"two_or_more_qt_drugs_additional":3 if n>=2 else 0,
       "heart_failure":3 if d["heart_failure"] else 0,"sepsis":3 if d["sepsis"] else 0}
    total=sum(c.values()); band="low_lt7" if total<7 else "moderate_7_10" if total<=10 else "high_ge11"
    return {"id":"tisdale-qt","status":"complete","components":c,"total":total,"range":[0,21],"risk_band":band,"source":SOURCES["tisdale-qt"]}

def calculate_bova(d):
    req=("systolic_bp_mmHg","troponin_elevated","rv_dysfunction","heart_rate_bpm")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing Bova inputs: "+", ".join(miss))
    sbp=_num(d["systolic_bp_mmHg"],"sbp"); hr=_num(d["heart_rate_bpm"],"hr")
    _bool(d["troponin_elevated"],"troponin_elevated"); _bool(d["rv_dysfunction"],"rv_dysfunction")
    if sbp<90: raise ValueError("Bova is for normotensive PE; SBP <90 mmHg is outside intended population")
    c={"sbp_90_100":2 if 90<=sbp<=100 else 0,"troponin":2 if d["troponin_elevated"] else 0,
       "rv_dysfunction":2 if d["rv_dysfunction"] else 0,"hr_ge110":1 if hr>=110 else 0}
    total=sum(c.values()); stage="I" if total<=2 else "II" if total<=4 else "III"
    return {"id":"bova","status":"complete","components":c,"total":total,"range":[0,7],"stage":stage,"source":SOURCES["bova"]}

def calculate_sic(d):
    req=("platelets_10e9_L","pt_inr","sofa_four_system_score")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing SIC inputs: "+", ".join(miss))
    p=_num(d["platelets_10e9_L"],"platelets"); inr=_num(d["pt_inr"],"pt_inr"); sofa=_num(d["sofa_four_system_score"],"sofa_four_system_score")
    pscore=0 if p>=150 else 1 if p>=100 else 2
    iscore=0 if inr<=1.2 else 1 if inr<=1.4 else 2
    sscore=0 if sofa<=0 else 1 if sofa==1 else 2
    total=pscore+iscore+sscore
    # Published SIC requires total >=4 and coagulation subtotal (platelets+INR) >2.
    diagnosis=total>=4 and (pscore+iscore)>2
    return {"id":"sic","status":"complete","components":{"platelets":pscore,"pt_inr":iscore,"sofa":sscore},
            "total":total,"sic_positive":diagnosis,
            "warning":"Use the four-system SOFA component specified by the SIC definition (respiratory, cardiovascular, hepatic, renal), not an arbitrary SOFA variant.",
            "source":SOURCES["sic"]}

def calculate_mews(d):
    req=("systolic_bp_mmHg","heart_rate_bpm","respiratory_rate","temperature_c","avpu")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing MEWS inputs: "+", ".join(miss))
    sbp=_num(d["systolic_bp_mmHg"],"sbp"); hr=_num(d["heart_rate_bpm"],"hr"); rr=_num(d["respiratory_rate"],"rr"); t=_num(d["temperature_c"],"temperature")
    if sbp<70: s=3
    elif sbp<=80: s=2
    elif sbp<=100: s=1
    elif sbp<=199: s=0
    else: s=2
    if hr<40: h=2
    elif hr<=50: h=1
    elif hr<=100: h=0
    elif hr<=110: h=1
    elif hr<=129: h=2
    else: h=3
    if rr<9: r=2
    elif rr<=14: r=0
    elif rr<=20: r=1
    elif rr<=29: r=2
    else: r=3
    temp=2 if t<35 else 0 if t<38.5 else 2
    av=str(d["avpu"]).strip().lower(); amap={"a":0,"alert":0,"v":1,"voice":1,"p":2,"pain":2,"u":3,"unresponsive":3}
    if av not in amap: raise ValueError("avpu must be A/V/P/U")
    c={"systolic_bp":s,"heart_rate":h,"respiratory_rate":r,"temperature":temp,"avpu":amap[av]}
    return {"id":"mews","status":"complete","components":c,"total":sum(c.values()),"source":SOURCES["mews"]}

def calculate_sirs(d):
    req=("temperature_c","heart_rate_bpm","respiratory_rate","paco2_mmHg","wbc_per_uL","bands_percent")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing SIRS inputs: "+", ".join(miss))
    t=_num(d["temperature_c"],"temperature"); hr=_num(d["heart_rate_bpm"],"hr"); rr=_num(d["respiratory_rate"],"rr")
    co2=_num(d["paco2_mmHg"],"paco2"); wbc=_num(d["wbc_per_uL"],"wbc"); bands=_num(d["bands_percent"],"bands")
    c={"temperature":t<36 or t>38,"heart_rate":hr>90,"respiratory":rr>20 or co2<32,
       "wbc_or_bands":wbc>12000 or wbc<4000 or bands>10}
    total=sum(1 for v in c.values() if v)
    return {"id":"sirs","status":"complete","criteria":c,"positive_count":total,"sirs_ge2":total>=2,
            "warning":"SIRS is nonspecific and should not be used alone to diagnose or exclude sepsis.","source":SOURCES["sirs"]}
