#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 5 adult neurology."""

import math

SOURCES={
 "abcd2":{"url":"https://pubmed.ncbi.nlm.nih.gov/17258668/","version":"ABCD2 2007"},
 "aspects":{"url":"https://pubmed.ncbi.nlm.nih.gov/10905241/","version":"ASPECTS 2000"},
 "modified-rankin":{"url":"https://manual.jointcommission.org/releases/TJC2026B/DataElem0569.html","version":"mRS 0-6"},
 "ich-score":{"url":"https://pubmed.ncbi.nlm.nih.gov/11283388/","version":"ICH Score 2001"},
 "modified-fisher":{"url":"https://pubmed.ncbi.nlm.nih.gov/16823296/","version":"Modified Fisher 0-4"},
 "cincinnati-stroke":{"url":"https://www.stroke.org/en/professionals/stroke-resource-library/pre-hospitalems","version":"CPSS"},
 "race-stroke":{"url":"https://racescale.org/how-to-use/table/","version":"RACE"},
 "fast-ed":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC4961538/","version":"FAST-ED"},
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def calculate_abcd2(data):
    req=("age","systolic_bp_mmHg","diastolic_bp_mmHg","clinical_feature","duration_minutes","diabetes")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing ABCD2 inputs: "+", ".join(missing))
    age=_num(data["age"],"age"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg"); dbp=_num(data["diastolic_bp_mmHg"],"diastolic_bp_mmHg"); dur=_num(data["duration_minutes"],"duration_minutes")
    _bool(data["diabetes"],"diabetes")
    feat=str(data["clinical_feature"]).strip().lower()
    fmap={"unilateral_weakness":2,"speech_impairment_without_weakness":1,"other":0}
    if feat not in fmap: raise ValueError("clinical_feature invalid")
    components={
      "age_ge_60":1 if age>=60 else 0,
      "bp_ge_140_or_90":1 if (sbp>=140 or dbp>=90) else 0,
      "clinical_features":fmap[feat],
      "duration":2 if dur>=60 else 1 if dur>=10 else 0,
      "diabetes":1 if data["diabetes"] else 0,
    }
    total=sum(components.values())
    return {"id":"abcd2","status":"complete","components":components,"total":total,"range":[0,7],
            "warning":"ABCD2 supports short-term stroke-risk stratification after a clinical TIA diagnosis; it must not delay urgent etiologic evaluation or be used to exclude TIA/stroke.",
            "source":SOURCES["abcd2"]}

ASPECTS_REGIONS=("caudate","lentiform","internal_capsule","insula","m1","m2","m3","m4","m5","m6")
def calculate_aspects(data):
    regions=data.get("early_ischemic_change")
    if not isinstance(regions,dict): raise ValueError("ASPECTS requires early_ischemic_change object")
    missing=[r for r in ASPECTS_REGIONS if regions.get(r) is None]
    if missing: raise ValueError("missing ASPECTS regions: "+", ".join(missing))
    extra=[r for r in regions if r not in ASPECTS_REGIONS]
    if extra: raise ValueError("unknown ASPECTS regions: "+", ".join(extra))
    for k,v in regions.items(): _bool(v,k)
    abnormal=[k for k,v in regions.items() if v]
    total=10-len(abnormal)
    return {"id":"aspects","status":"complete","total":total,"range":[0,10],
            "abnormal_regions":abnormal,"normal_region_count":total,
            "warning":"ASPECTS requires expert image interpretation of the MCA territory. This calculator only subtracts explicitly marked abnormal regions; it does not interpret CT images.",
            "source":SOURCES["aspects"]}

MRS_TEXT={
 0:"no symptoms",
 1:"no significant disability despite symptoms; able to carry out usual activities",
 2:"slight disability; unable to carry out all previous activities but independent in own affairs",
 3:"moderate disability; requires some help but walks without another person's assistance",
 4:"moderately severe disability; unable to walk or attend bodily needs without assistance",
 5:"severe disability; bedridden, incontinent and requiring constant nursing care/attention",
 6:"dead",
}
def calculate_modified_rankin(data):
    score=data.get("score")
    if score is None: raise ValueError("mRS requires explicit structured score 0-6")
    if isinstance(score,bool) or not isinstance(score,int) or score not in MRS_TEXT: raise ValueError("mRS score must be integer 0-6")
    return {"id":"modified-rankin","status":"complete","score":score,"description":MRS_TEXT[score],
            "warning":"mRS should be assigned from a structured functional assessment; this engine does not infer disability grade from free text.",
            "source":SOURCES["modified-rankin"]}

def calculate_ich_score(data):
    req=("gcs","age","ich_volume_cm3","intraventricular_hemorrhage","infratentorial_origin")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing ICH Score inputs: "+", ".join(missing))
    g=int(_num(data["gcs"],"gcs")); age=_num(data["age"],"age"); vol=_num(data["ich_volume_cm3"],"ich_volume_cm3")
    if g<3 or g>15 or age<0 or vol<0: raise ValueError("invalid ICH Score numeric input")
    _bool(data["intraventricular_hemorrhage"],"intraventricular_hemorrhage"); _bool(data["infratentorial_origin"],"infratentorial_origin")
    comp={
      "gcs":2 if g<=4 else 1 if g<=12 else 0,
      "age_ge_80":1 if age>=80 else 0,
      "ich_volume_ge_30_cm3":1 if vol>=30 else 0,
      "intraventricular_hemorrhage":1 if data["intraventricular_hemorrhage"] else 0,
      "infratentorial_origin":1 if data["infratentorial_origin"] else 0,
    }
    total=sum(comp.values())
    return {"id":"ich-score","status":"complete","components":comp,"total":total,"range":[0,6],
            "warning":"ICH Score is a severity/risk-stratification scale and must not be used to limit treatment or prognosticate an individual patient in isolation.",
            "source":SOURCES["ich-score"]}

def calculate_modified_fisher(data):
    if data.get("sah_thickness") is None or data.get("ivh") is None:
        raise ValueError("modified Fisher requires sah_thickness and ivh")
    thickness=str(data["sah_thickness"]).strip().lower()
    if thickness not in {"none","thin","thick"}: raise ValueError("sah_thickness must be none/thin/thick")
    _bool(data["ivh"],"ivh")
    if thickness=="none":
        if data["ivh"]: raise ValueError("grade 0 requires no SAH and no IVH; isolated IVH is outside this simplified modified Fisher mapping")
        grade=0
    elif thickness=="thin": grade=2 if data["ivh"] else 1
    else: grade=4 if data["ivh"] else 3
    return {"id":"modified-fisher","status":"complete","grade":grade,"range":[0,4],
            "warning":"Modified Fisher grades CT blood burden after aneurysmal SAH; it is not a stand-alone DCI management rule.",
            "source":SOURCES["modified-fisher"]}

def calculate_cincinnati(data):
    req=("facial_droop","arm_drift","abnormal_speech")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing CPSS inputs: "+", ".join(missing))
    for k in req: _bool(data[k],k)
    abnormal={k:bool(data[k]) for k in req}; count=sum(abnormal.values())
    return {"id":"cincinnati-stroke","status":"complete","abnormal_items":abnormal,"abnormal_count":count,
            "screen_positive":count>=1,
            "warning":"CPSS is a prehospital stroke screen, not a diagnostic confirmation and not an LVO severity score.",
            "source":SOURCES["cincinnati-stroke"]}

def calculate_race(data):
    req=("facial_palsy","arm_motor","leg_motor","head_gaze_deviation","cortical_item")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing RACE inputs: "+", ".join(missing))
    limits={"facial_palsy":2,"arm_motor":2,"leg_motor":2,"head_gaze_deviation":1,"cortical_item":2}
    comp={}
    for k,mx in limits.items():
        v=data[k]
        if isinstance(v,bool) or not isinstance(v,int) or not 0<=v<=mx: raise ValueError(f"{k} must be integer 0-{mx}")
        comp[k]=v
    total=sum(comp.values())
    return {"id":"race-stroke","status":"complete","components":comp,"total":total,"range":[0,9],
            "lvo_screen_positive_ge5":total>=5,
            "warning":"RACE is an LVO screening/triage tool; cortical_item is aphasia for right hemiparesis or agnosia/neglect for left hemiparesis.",
            "source":SOURCES["race-stroke"]}

def calculate_fast_ed(data):
    req=("nihss_facial_palsy","nihss_arm_motor","nihss_language","nihss_gaze","nihss_neglect")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing FAST-ED inputs: "+", ".join(missing))
    fp=int(_num(data["nihss_facial_palsy"],"nihss_facial_palsy")); arm=int(_num(data["nihss_arm_motor"],"nihss_arm_motor")); lang=int(_num(data["nihss_language"],"nihss_language")); gaze=int(_num(data["nihss_gaze"],"nihss_gaze")); neg=int(_num(data["nihss_neglect"],"nihss_neglect"))
    if not 0<=fp<=3 or not 0<=arm<=4 or not 0<=lang<=3 or not 0<=gaze<=2 or not 0<=neg<=2: raise ValueError("FAST-ED NIHSS source items out of range")
    comp={
      "facial_palsy":0 if fp<=1 else 1,
      "arm_weakness":0 if arm==0 else 1 if arm<=2 else 2,
      "speech_changes":0 if lang==0 else 1 if lang==1 else 2,
      "eye_deviation":gaze,
      "denial_neglect":neg,
    }
    total=sum(comp.values())
    return {"id":"fast-ed","status":"complete","components":comp,"total":total,"range":[0,9],
            "lvo_screen_positive_ge4":total>=4,
            "warning":"FAST-ED is a prehospital LVO screening tool derived from NIHSS items; time is documented for triage but carries no score points.",
            "source":SOURCES["fast-ed"]}
