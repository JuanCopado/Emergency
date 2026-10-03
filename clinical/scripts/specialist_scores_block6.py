#!/usr/bin/env python3
"""SPECIALIST block 6: pediatric ICU/surgery and geriatrics."""

import math

SOURCES={
 "psofa":{
   "url":"https://jamanetwork.com/journals/jamapediatrics/fullarticle/2646857",
   "version":"pSOFA Matics/Sanchez-Pinto 2017, 0-24",
 },
 "pelod2":{
   "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11554295/",
   "version":"PELOD-2, 0-33",
 },
 "parc":{
   "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC5869337/",
   "version":"pARC 2018 logistic model",
 },
 "charlson":{
   "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC3677715/",
   "version":"Original Charlson Comorbidity Index",
 },
 "barthel":{
   "url":"https://www.sralab.org/rehabilitation-measures/barthel-index",
   "version":"Barthel Index 0-100",
 },
}

def _num(v,n):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{n} must be finite")
    return float(v)
def _bool(v,n):
    if not isinstance(v,bool): raise ValueError(f"{n} must be boolean")
    return v

def _age_group(months):
    m=_num(months,"age_months")
    if m<0: raise ValueError("age_months cannot be negative")
    if m<1:return 0
    if m<12:return 1
    if m<24:return 2
    if m<60:return 3
    if m<144:return 4
    if m<=216:return 5
    return 6

_PSOFA_MAP_NORMAL=[46,55,60,62,65,67,70]
_PSOFA_CR_RANGES=[
 [(0.0,0.8,0),(0.8,1.0,1),(1.0,1.2,2),(1.2,1.6,3),(1.6,float("inf"),4)],
 [(0.0,0.3,0),(0.3,0.5,1),(0.5,0.8,2),(0.8,1.2,3),(1.2,float("inf"),4)],
 [(0.0,0.4,0),(0.4,0.6,1),(0.6,1.1,2),(1.1,1.5,3),(1.5,float("inf"),4)],
 [(0.0,0.6,0),(0.6,0.9,1),(0.9,1.6,2),(1.6,2.3,3),(2.3,float("inf"),4)],
 [(0.0,0.7,0),(0.7,1.1,1),(1.1,1.8,2),(1.8,2.6,3),(2.6,float("inf"),4)],
 [(0.0,1.0,0),(1.0,1.7,1),(1.7,2.9,2),(2.9,4.2,3),(4.2,float("inf"),4)],
 [(0.0,1.2,0),(1.2,2.0,1),(2.0,3.5,2),(3.5,5.0,3),(5.0,float("inf"),4)],
]

def _psofa_resp(d):
    support=d["respiratory_support"]
    _bool(support,"respiratory_support")
    if d.get("pao2_fio2") is not None:
        x=_num(d["pao2_fio2"],"pao2_fio2")
        if x>=400:return 0
        if x>=300:return 1
        if x>=200:return 2
        if support and x>=100:return 3
        if support and x<100:return 4
        return 2
    if d.get("spo2_fio2") is not None:
        x=_num(d["spo2_fio2"],"spo2_fio2")
        if x>=292:return 0
        if x>=264:return 1
        if x>=221:return 2
        if support and x>=148:return 3
        if support and x<148:return 4
        return 2
    raise ValueError("pSOFA requires pao2_fio2 or spo2_fio2")

def calculate_psofa(d):
    req=("age_months","respiratory_support","platelets_10e3_uL","bilirubin_mg_dL","map_mmHg",
         "dopamine_mcg_kg_min","epinephrine_mcg_kg_min","norepinephrine_mcg_kg_min","dobutamine_any_dose",
         "gcs","creatinine_mg_dL")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing pSOFA inputs: "+", ".join(miss))
    group=_age_group(d["age_months"])
    p=_num(d["platelets_10e3_uL"],"platelets")
    b=_num(d["bilirubin_mg_dL"],"bilirubin")
    m=_num(d["map_mmHg"],"map")
    dopamine=_num(d["dopamine_mcg_kg_min"],"dopamine")
    epi=_num(d["epinephrine_mcg_kg_min"],"epinephrine")
    norepi=_num(d["norepinephrine_mcg_kg_min"],"norepinephrine")
    _bool(d["dobutamine_any_dose"],"dobutamine_any_dose")
    g=int(_num(d["gcs"],"gcs"))
    cr=_num(d["creatinine_mg_dL"],"creatinine")
    if g<3 or g>15 or min(p,b,m,dopamine,epi,norepi,cr)<0: raise ValueError("invalid pSOFA input")

    coag=0 if p>=150 else 1 if p>=100 else 2 if p>=50 else 3 if p>=20 else 4
    liver=0 if b<1.2 else 1 if b<2 else 2 if b<6 else 3 if b<12 else 4
    if dopamine>15 or epi>0.1 or norepi>0.1: cardio=4
    elif dopamine>5 or epi>0 or norepi>0: cardio=3
    elif dopamine>0 or d["dobutamine_any_dose"]: cardio=2
    else: cardio=0 if m>=_PSOFA_MAP_NORMAL[group] else 1
    cns=0 if g==15 else 1 if g>=13 else 2 if g>=10 else 3 if g>=6 else 4
    renal=None
    for low,high,points in _PSOFA_CR_RANGES[group]:
        if low<=cr<high: renal=points; break
    if renal is None: raise ValueError("unable to classify pSOFA creatinine")
    comp={"respiratory":_psofa_resp(d),"coagulation":coag,"liver":liver,"cardiovascular":cardio,"cns":cns,"renal":renal}
    return {"id":"psofa","status":"complete","components":comp,"total":sum(comp.values()),"range":[0,24],
            "warning":"pSOFA is an adapted pediatric organ-dysfunction score. Do not mix thresholds with adult SOFA or Phoenix.",
            "source":SOURCES["psofa"]}

_PELOD_MAP=[
 (46,31,17,16),(55,39,25,24),(60,44,31,30),(62,46,32,31),(65,49,36,35),(67,52,38,37)
]
_PELOD_CR=[69,22,34,50,58,92]

def _pelod_group(months):
    m=_num(months,"age_months")
    if m<0: raise ValueError("age_months cannot be negative")
    if m<1:return 0
    if m<12:return 1
    if m<24:return 2
    if m<60:return 3
    if m<144:return 4
    return 5

def calculate_pelod2(d):
    req=("age_months","gcs","both_pupils_fixed","lactate_mmol_L","map_mmHg","creatinine_umol_L",
         "pao2_fio2","paco2_mmHg","invasive_ventilation","wbc_10e9_L","platelets_10e9_L")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing PELOD-2 inputs: "+", ".join(miss))
    group=_pelod_group(d["age_months"])
    g=int(_num(d["gcs"],"gcs")); _bool(d["both_pupils_fixed"],"both_pupils_fixed")
    lact=_num(d["lactate_mmol_L"],"lactate"); m=_num(d["map_mmHg"],"map")
    cr=_num(d["creatinine_umol_L"],"creatinine_umol_L"); pf=_num(d["pao2_fio2"],"pao2_fio2")
    co2=_num(d["paco2_mmHg"],"paco2"); _bool(d["invasive_ventilation"],"invasive_ventilation")
    wbc=_num(d["wbc_10e9_L"],"wbc"); plt=_num(d["platelets_10e9_L"],"platelets")
    if g<3 or g>15 or min(lact,m,cr,pf,co2,wbc,plt)<0: raise ValueError("invalid PELOD-2 input")

    gpts=0 if g>=11 else 1 if g>=5 else 4
    pupil=5 if d["both_pupils_fixed"] else 0
    lactpts=0 if lact<5 else 1 if lact<11 else 4
    normal,mid_hi,low_hi,very_low=_PELOD_MAP[group]
    if m>=normal: mappts=0
    elif m>=mid_hi: mappts=2
    elif m>very_low: mappts=3
    else: mappts=6
    crpts=2 if cr>_PELOD_CR[group] else 0
    pfpts=2 if pf<=60 else 0
    co2pts=0 if co2<=58 else 1 if co2<=94 else 3
    ventpts=3 if d["invasive_ventilation"] else 0
    wbcpts=2 if wbc<=2 else 0
    pltpts=0 if plt>=142 else 1 if plt>=77 else 2
    comp={"gcs":gpts,"pupils":pupil,"lactate":lactpts,"map":mappts,"creatinine":crpts,
          "pao2_fio2":pfpts,"paco2":co2pts,"invasive_ventilation":ventpts,"wbc":wbcpts,"platelets":pltpts}
    total=sum(comp.values())
    return {"id":"pelod2","status":"complete","components":comp,"total":total,"range":[0,33],
            "warning":"PELOD-2 uses age-specific thresholds and worst values over the defined observation window; mortality models must not be inferred from the total without the published calibration.",
            "source":SOURCES["pelod2"]}

def calculate_parc(d):
    req=("age_years","sex","pain_duration_hours","pain_with_walking_hopping_coughing","migration_to_rlq",
         "maximal_rlq_tenderness","guarding","anc_10e3_uL")
    miss=[k for k in req if d.get(k) is None]
    if miss: raise ValueError("missing pARC inputs: "+", ".join(miss))
    age=_num(d["age_years"],"age_years")
    if age<5 or age>18: raise ValueError("original pARC model applies to age 5-18 years")
    sex=str(d["sex"]).strip().lower()
    if sex not in {"male","female","m","f"}: raise ValueError("sex must be male/female")
    male=sex in {"male","m"}
    duration=_num(d["pain_duration_hours"],"pain_duration_hours")
    if duration<0 or duration>96: raise ValueError("pARC derivation categories cover pain duration 0-96 h")
    for k in ("pain_with_walking_hopping_coughing","migration_to_rlq","maximal_rlq_tenderness","guarding"):_bool(d[k],k)
    anc=_num(d["anc_10e3_uL"],"anc_10e3_uL")
    if anc<0: raise ValueError("ANC cannot be negative")

    z=-8.7 + (1.28 if male else 0)
    if 5<=age<8:
        z += 0.38
        if male: z += -1.05
    elif 8<=age<14:
        # Female age 12-18 is the reference category in the published interaction.
        if male or age<12: z += -0.72
    if 24<=duration<48:z+=0.47
    elif 48<=duration<=96:z+=0.10
    if d["pain_with_walking_hopping_coughing"]:z+=1.05
    if d["migration_to_rlq"]:z+=0.46
    if d["maximal_rlq_tenderness"]:z+=1.14
    if d["guarding"]:z+=0.67
    z += 1.77*math.sqrt(anc) if anc<14 else 6.62
    probability=1/(1+math.exp(-z))
    pct=100*probability
    if pct<5: band="<5"
    elif pct<15: band="5_14"
    elif pct<25: band="15_24"
    elif pct<50: band="25_49"
    elif pct<75: band="50_74"
    elif pct<85: band="75_84"
    else: band="ge85"
    return {"id":"parc","status":"complete","linear_predictor":z,"appendicitis_probability":probability,
            "risk_category_percent":band,
            "warning":"pARC applies to children 5-18 years with acute abdominal pain in the derivation context; it is an adjunct to pediatric appendicitis evaluation, not a stand-alone imaging or surgical decision.",
            "source":SOURCES["parc"]}

_CHARLSON_WEIGHTS={
 "myocardial_infarction":1,"congestive_heart_failure":1,"peripheral_vascular_disease":1,
 "cerebrovascular_disease":1,"dementia":1,"chronic_pulmonary_disease":1,
 "connective_tissue_disease":1,"peptic_ulcer_disease":1,"mild_liver_disease":1,
 "diabetes_uncomplicated":1,"hemiplegia_or_paraplegia":2,"moderate_severe_renal_disease":2,
 "diabetes_with_end_organ_damage":2,"malignancy_nonmetastatic":2,"leukemia":2,"lymphoma":2,
 "moderate_severe_liver_disease":3,"metastatic_solid_tumor":6,"aids":6,
}
def calculate_charlson(d):
    cond=d.get("conditions")
    if not isinstance(cond,dict): raise ValueError("Charlson requires conditions object")
    unknown=[k for k in cond if k not in _CHARLSON_WEIGHTS]
    if unknown: raise ValueError("unknown Charlson conditions: "+", ".join(unknown))
    flags={k:bool(cond.get(k,False)) for k in _CHARLSON_WEIGHTS}
    # Original hierarchy: more severe manifestation supersedes the lower-weight partner.
    if flags["diabetes_with_end_organ_damage"]: flags["diabetes_uncomplicated"]=False
    if flags["moderate_severe_liver_disease"]: flags["mild_liver_disease"]=False
    if flags["hemiplegia_or_paraplegia"]: flags["cerebrovascular_disease"]=False
    if flags["metastatic_solid_tumor"]: flags["malignancy_nonmetastatic"]=False
    comp={k:(_CHARLSON_WEIGHTS[k] if v else 0) for k,v in flags.items()}
    total=sum(comp.values())
    return {"id":"charlson","status":"complete","components":comp,"total":total,
            "version":"original_comorbidity_only_no_age_adjustment",
            "warning":"This implementation is the original comorbidity-weight index, not the later age-adjusted or updated-weight variants.",
            "source":SOURCES["charlson"]}

_BARTHEL_ALLOWED={
 "feeding":{0,5,10},"bathing":{0,5},"grooming":{0,5},"dressing":{0,5,10},
 "bowels":{0,5,10},"bladder":{0,5,10},"toilet":{0,5,10},
 "transfers":{0,5,10,15},"mobility":{0,5,10,15},"stairs":{0,5,10},
}
def calculate_barthel(d):
    points=d.get("item_points")
    if not isinstance(points,dict): raise ValueError("Barthel requires item_points object")
    missing=[k for k in _BARTHEL_ALLOWED if k not in points]
    if missing: raise ValueError("missing Barthel items: "+", ".join(missing))
    extra=[k for k in points if k not in _BARTHEL_ALLOWED]
    if extra: raise ValueError("unknown Barthel items: "+", ".join(extra))
    out={}
    for k,allowed in _BARTHEL_ALLOWED.items():
        v=points[k]
        if isinstance(v,bool) or not isinstance(v,int) or v not in allowed:
            raise ValueError(f"{k}: invalid Barthel point value; allowed {sorted(allowed)}")
        out[k]=v
    total=sum(out.values())
    return {"id":"barthel","status":"complete_from_authorized_item_scores","item_points":out,"total":total,"range":[0,100],
            "warning":"Use an authorized Barthel instrument/translation for item definitions. This engine validates and sums allowed point values without reproducing licensed questionnaire wording.",
            "source":SOURCES["barthel"]}
