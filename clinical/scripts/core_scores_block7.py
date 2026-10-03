#!/usr/bin/env python3
"""CORE scores block 7: pediatric general, trauma, pain, respiratory, surgery."""

import math

SOURCES={
  "pews":{
    "authority":"Parshuram et al. Bedside Paediatric Early Warning System",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC3387627/",
    "version":"Bedside PEWS 7-item score (0-26)",
  },
  "pediatric-trauma-score":{
    "authority":"Pediatric Trauma Score literature",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC11065969/",
    "version":"Pediatric Trauma Score -6 to +12",
  },
  "sipa":{
    "authority":"Pediatric age-adjusted shock index validation",
    "url":"https://pubmed.ncbi.nlm.nih.gov/27814956/",
    "version":"SIPA age 4-16 years",
  },
  "flacc":{
    "authority":"FLACC pain scale literature",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC9689143/",
    "version":"FLACC 0-10",
  },
  "wong-baker":{
    "authority":"Wong-Baker FACES Foundation",
    "url":"https://wongbakerfaces.org/",
    "version":"Official Wong-Baker FACES 0-10",
  },
  "pram":{
    "authority":"Ducharme et al. PRAM",
    "url":"https://pubmed.ncbi.nlm.nih.gov/18346499/",
    "version":"PRAM 0-12",
  },
  "westley-croup":{
    "authority":"Westley Croup Score",
    "url":"https://www.ncbi.nlm.nih.gov/sites/books/NBK431070/table/article-20142.table1/",
    "version":"Westley 0-17",
  },
  "clinical-dehydration":{
    "authority":"Clinical Dehydration Scale",
    "url":"https://pubmed.ncbi.nlm.nih.gov/15289767/",
    "version":"CDS 0-8",
  },
  "pediatric-appendicitis":{
    "authority":"Samuel Pediatric Appendicitis Score",
    "url":"https://pubmed.ncbi.nlm.nih.gov/12037754/",
    "version":"PAS 0-10",
  },
  "pecarn-head-injury":{
    "authority":"PECARN pediatric head trauma rule",
    "url":"https://pubmed.ncbi.nlm.nih.gov/19758692/",
    "version":"PECARN ciTBI rule <2 y and >=2 y",
  },
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be a finite number")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool):
        raise ValueError(f"{name} must be boolean")
    return v

def _pews_age_group(age_months):
    m=_num(age_months,"age_months")
    if m<0:return None
    if m<3:return "0_3m"
    if m<12:return "3_12m"
    if m<60:return "1_4y"
    if m<144:return "5_12y"
    return "12y_plus"

def _score_extremes(value, normal_low, normal_high, one_low, one_high, two_low, two_high, four_low, four_high):
    if value<=four_low or value>=four_high:return 4
    if value<=two_low or value>=two_high:return 2
    if value<=one_low or value>=one_high:return 1
    if normal_low<value<normal_high:return 0
    return 0

def _pews_hr(group,x):
    tables={
      "0_3m":(110,150,110,150,90,180,80,190),
      "3_12m":(100,150,100,150,80,170,70,180),
      "1_4y":(90,120,90,120,70,150,60,170),
      "5_12y":(70,110,70,110,60,130,50,150),
      "12y_plus":(60,100,60,100,50,120,40,140),
    }
    a=tables[group]
    return _score_extremes(x,*a)

def _pews_sbp(group,x):
    tables={
      "0_3m":(60,80,60,80,50,100,45,130),
      "3_12m":(80,100,80,100,70,120,60,150),
      "1_4y":(90,110,90,110,75,125,65,160),
      "5_12y":(90,120,90,120,80,140,70,170),
      "12y_plus":(100,130,100,130,85,150,75,190),
    }
    a=tables[group]
    return _score_extremes(x,*a)

def _pews_rr(group,x):
    tables={
      "0_3m":(29,61,29,61,19,81,15,91),
      "3_12m":(24,51,24,51,19,71,15,81),
      "1_4y":(19,41,19,41,15,61,12,71),
      "5_12y":(19,31,19,31,14,41,10,51),
      "12y_plus":(11,17,11,17,10,23,9,30),
    }
    a=tables[group]
    return _score_extremes(x,*a)

def calculate_bedside_pews(data):
    required=("age_months","heart_rate_bpm","systolic_bp_mmHg","capillary_refill_seconds",
              "respiratory_rate","respiratory_effort","spo2_percent","oxygen_support_level")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Bedside PEWS inputs: "+", ".join(missing))
    group=_pews_age_group(data["age_months"])
    if group is None: raise ValueError("age_months cannot be negative")
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    crt=_num(data["capillary_refill_seconds"],"capillary_refill_seconds")
    rr=_num(data["respiratory_rate"],"respiratory_rate")
    spo2=_num(data["spo2_percent"],"spo2_percent")
    if min(hr,sbp,crt,rr)<0 or not 0<=spo2<=100:
        raise ValueError("invalid PEWS vital signs")
    effort=str(data["respiratory_effort"]).strip().lower()
    effort_map={"normal":0,"mild":1,"moderate":2,"severe":4,"apnea":4,"apnoea":4}
    if effort not in effort_map: raise ValueError("respiratory_effort must be normal/mild/moderate/severe/apnea")
    oxy=str(data["oxygen_support_level"]).strip().lower()
    oxy_map={"room_air":0,"low":2,"less_than_4l_or_less_than_50pct":2,"high":4,"4l_or_more_or_50pct_or_more":4}
    if oxy not in oxy_map: raise ValueError("unsupported oxygen_support_level")
    components={
      "heart_rate":_pews_hr(group,hr),
      "systolic_bp":_pews_sbp(group,sbp),
      "capillary_refill":4 if crt>=3 else 0,
      "respiratory_rate":_pews_rr(group,rr),
      "respiratory_effort":effort_map[effort],
      "spo2":0 if spo2>94 else 1 if spo2>=91 else 2,
      "oxygen_therapy":oxy_map[oxy],
    }
    total=sum(components.values())
    return {
      "id":"pews","version":"Bedside PEWS 7-item","status":"complete",
      "components":components,"total":total,"range":[0,26],
      "warning":"PEWS systems vary by institution. This calculator implements the validated Bedside PEWS table and must not be mixed with local PEWS thresholds.",
      "source":SOURCES["pews"],
    }

def calculate_pediatric_trauma_score(data):
    required=("weight_kg","airway","systolic_bp_mmHg","cns","open_wound","skeletal")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Pediatric Trauma Score inputs: "+", ".join(missing))
    w=_num(data["weight_kg"],"weight_kg"); sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    if w<0 or sbp<0: raise ValueError("weight/SBP cannot be negative")
    weight_score=2 if w>=20 else 1 if w>=10 else -1
    bp_score=2 if sbp>=90 else 1 if sbp>=50 else -1
    maps={
      "airway":{"normal":2,"maintainable":1,"unmaintainable":-1},
      "cns":{"awake":2,"obtunded_or_loc":1,"coma_or_decerebrate":-1},
      "open_wound":{"none":2,"minor":1,"major_or_penetrating":-1},
      "skeletal":{"none":2,"closed_fracture":1,"open_or_multiple_fractures":-1},
    }
    components={"weight":weight_score,"systolic_bp":bp_score}
    for key,mapping in maps.items():
        value=str(data[key]).strip().lower()
        if value not in mapping: raise ValueError(f"unsupported {key} category")
        components[key]=mapping[value]
    total=sum(components.values())
    return {
      "id":"pediatric-trauma-score","status":"complete","components":components,
      "total":total,"range":[-6,12],"high_risk_common_threshold_le_8":total<=8,
      "source":SOURCES["pediatric-trauma-score"],
    }

def calculate_sipa(data):
    required=("age_years","heart_rate_bpm","systolic_bp_mmHg")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing SIPA inputs: "+", ".join(missing))
    age=_num(data["age_years"],"age_years")
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    if age<4 or age>16: raise ValueError("validated SIPA thresholds require age 4-16 years")
    if hr<0 or sbp<=0: raise ValueError("invalid HR/SBP")
    si=hr/sbp
    threshold=1.22 if age<=6 else 1.0 if age<=12 else 0.9
    return {
      "id":"sipa","status":"complete","shock_index":si,
      "age_adjusted_threshold":threshold,"elevated":si>threshold,
      "warning":"SIPA was validated in pediatric trauma populations; it is not a stand-alone diagnosis of shock.",
      "source":SOURCES["sipa"],
    }

def _component_category(value,mapping,name):
    key=str(value).strip().lower()
    if key not in mapping: raise ValueError(f"unsupported {name} category")
    return mapping[key]

def calculate_flacc(data):
    required=("face","legs","activity","cry","consolability")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing FLACC inputs: "+", ".join(missing))
    maps={
      "face":{"relaxed":0,"occasional_grimace":1,"frequent_frown_clenched_jaw":2},
      "legs":{"relaxed":0,"uneasy":1,"kicking_or_drawn_up":2},
      "activity":{"normal":0,"squirming_tense":1,"arched_rigid_jerking":2},
      "cry":{"none":0,"moans_whimpers":1,"steady_cry_screams_sobs":2},
      "consolability":{"content":0,"reassured_or_distractible":1,"difficult_to_console":2},
    }
    components={k:_component_category(data[k],maps[k],k) for k in required}
    total=sum(components.values())
    band="no_observed_pain_behavior" if total==0 else "mild_1_3" if total<=3 else "moderate_4_6" if total<=6 else "severe_7_10"
    return {"id":"flacc","status":"complete","components":components,"total":total,"range":[0,10],"band":band,"source":SOURCES["flacc"]}

def prepare_wong_baker(data):
    if data.get("authorized_official_scale_used") is not True:
        return {
          "id":"wong-baker","status":"official_licensed_scale_required",
          "official_resource":"https://wongbakerfaces.org/",
          "warning":"The official FACES artwork/instructions are copyrighted/licensed. Use the authorized official scale; do not reproduce or modify it in this repository.",
          "source":SOURCES["wong-baker"],
        }
    required=("age_years","patient_self_report_capable","patient_selected_score")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Wong-Baker inputs: "+", ".join(missing))
    age=_num(data["age_years"],"age_years")
    _bool(data["patient_self_report_capable"],"patient_self_report_capable")
    if age<3: raise ValueError("Wong-Baker official guidance recommends ages 3+")
    if not data["patient_self_report_capable"]:
        raise ValueError("Wong-Baker is a patient self-assessment tool, not an observer-rated scale")
    score=int(_num(data["patient_selected_score"],"patient_selected_score"))
    if score not in (0,2,4,6,8,10): raise ValueError("patient_selected_score must be 0,2,4,6,8,10 from the official scale")
    return {"id":"wong-baker","status":"complete_from_authorized_official_scale","score":score,"range":[0,10],"source":SOURCES["wong-baker"]}

def calculate_pram(data):
    required=("spo2_percent","suprasternal_retraction","scalene_contraction","air_entry","wheezing")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing PRAM inputs: "+", ".join(missing))
    spo2=_num(data["spo2_percent"],"spo2_percent")
    if not 0<=spo2<=100: raise ValueError("spo2_percent must be 0-100")
    _bool(data["suprasternal_retraction"],"suprasternal_retraction")
    _bool(data["scalene_contraction"],"scalene_contraction")
    air_map={"normal":0,"decreased_bases":1,"decreased_apex_and_bases":2,"minimal_or_absent":3}
    wheeze_map={"absent":0,"expiratory_only":1,"inspiratory_and_expiratory":2,"audible_or_silent_chest":3}
    air=str(data["air_entry"]).strip().lower(); wheeze=str(data["wheezing"]).strip().lower()
    if air not in air_map or wheeze not in wheeze_map: raise ValueError("unsupported PRAM air_entry/wheezing category")
    components={
      "spo2":0 if spo2>=95 else 1 if spo2>=92 else 2,
      "suprasternal_retraction":2 if data["suprasternal_retraction"] else 0,
      "scalene_contraction":2 if data["scalene_contraction"] else 0,
      "air_entry":air_map[air],
      "wheezing":wheeze_map[wheeze],
    }
    total=sum(components.values())
    band="mild_0_3" if total<=3 else "moderate_4_7" if total<=7 else "severe_8_12"
    return {"id":"pram","status":"complete","components":components,"total":total,"range":[0,12],"severity_band":band,"source":SOURCES["pram"]}

def calculate_westley_croup(data):
    required=("stridor","retractions","air_entry","cyanosis","consciousness")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Westley inputs: "+", ".join(missing))
    maps={
      "stridor":{"none":0,"with_agitation":1,"at_rest":2},
      "retractions":{"none":0,"mild":1,"moderate":2,"severe":3},
      "air_entry":{"normal":0,"decreased":1,"markedly_decreased":2},
      "cyanosis":{"none":0,"with_agitation":4,"at_rest":5},
      "consciousness":{"normal":0,"alert":0,"disoriented":5},
    }
    components={k:_component_category(data[k],maps[k],k) for k in required}
    total=sum(components.values())
    band="mild" if total<=2 else "moderate" if total<=5 else "severe" if total<=11 else "impending_respiratory_failure"
    return {"id":"westley-croup","status":"complete","components":components,"total":total,"range":[0,17],"severity_band":band,"source":SOURCES["westley-croup"]}

def calculate_clinical_dehydration(data):
    required=("general_appearance","eyes","mucous_membranes","tears")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Clinical Dehydration Scale inputs: "+", ".join(missing))
    maps={
      "general_appearance":{"normal":0,"thirsty_restless_lethargic_irritable":1,"drowsy_limp_cold_sweaty_comatose":2},
      "eyes":{"normal":0,"slightly_sunken":1,"very_sunken":2},
      "mucous_membranes":{"moist":0,"sticky":1,"dry":2},
      "tears":{"present":0,"decreased":1,"absent":2},
    }
    components={k:_component_category(data[k],maps[k],k) for k in required}
    total=sum(components.values())
    band="no_dehydration" if total==0 else "some_dehydration_1_4" if total<=4 else "moderate_severe_5_8"
    return {"id":"clinical-dehydration","status":"complete","components":components,"total":total,"range":[0,8],"classification":band,"source":SOURCES["clinical-dehydration"]}

def calculate_pediatric_appendicitis(data):
    required=("migration_pain","anorexia","nausea_vomiting","fever","rlq_tenderness",
              "cough_percussion_hopping_tenderness","leukocytosis","neutrophilia")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Pediatric Appendicitis Score inputs: "+", ".join(missing))
    for k in required: _bool(data[k],k)
    components={
      "migration_pain":1 if data["migration_pain"] else 0,
      "anorexia":1 if data["anorexia"] else 0,
      "nausea_vomiting":1 if data["nausea_vomiting"] else 0,
      "fever":1 if data["fever"] else 0,
      "rlq_tenderness":2 if data["rlq_tenderness"] else 0,
      "cough_percussion_hopping_tenderness":2 if data["cough_percussion_hopping_tenderness"] else 0,
      "leukocytosis":1 if data["leukocytosis"] else 0,
      "neutrophilia":1 if data["neutrophilia"] else 0,
    }
    total=sum(components.values())
    return {
      "id":"pediatric-appendicitis","status":"complete","components":components,"total":total,"range":[0,10],
      "warning":"PAS is an adjunct; imaging/surgical consultation depend on the full clinical context and local pediatric appendicitis pathway.",
      "source":SOURCES["pediatric-appendicitis"],
    }

def classify_pecarn_head_injury(data):
    required=("age_years","altered_mental_status","gcs","severe_mechanism")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing PECARN head injury inputs: "+", ".join(missing))
    age=_num(data["age_years"],"age_years")
    gcs=int(_num(data["gcs"],"gcs"))
    if age<0 or age>=18: raise ValueError("PECARN head injury applies to children <18 years")
    if gcs<14 or gcs>15: raise ValueError("This PECARN minor-head-trauma pathway requires GCS 14-15")
    _bool(data["altered_mental_status"],"altered_mental_status")
    _bool(data["severe_mechanism"],"severe_mechanism")

    if age<2:
        required2=("palpable_skull_fracture","nonfrontal_scalp_hematoma","loc_seconds","acting_normally_parent")
        missing2=[k for k in required2 if data.get(k) is None]
        if missing2: raise ValueError("missing PECARN <2 y inputs: "+", ".join(missing2))
        _bool(data["palpable_skull_fracture"],"palpable_skull_fracture")
        _bool(data["nonfrontal_scalp_hematoma"],"nonfrontal_scalp_hematoma")
        _bool(data["acting_normally_parent"],"acting_normally_parent")
        loc=_num(data["loc_seconds"],"loc_seconds")
        if loc<0: raise ValueError("loc_seconds cannot be negative")
        high=data["altered_mental_status"] or gcs<15 or data["palpable_skull_fracture"]
        intermediate=(
          data["nonfrontal_scalp_hematoma"] or loc>=5 or data["severe_mechanism"] or not data["acting_normally_parent"]
        )
        low_criteria={
          "normal_mental_status":not data["altered_mental_status"] and gcs==15,
          "no_nonfrontal_scalp_hematoma":not data["nonfrontal_scalp_hematoma"],
          "no_loc_or_lt5s":loc<5,
          "nonsevere_mechanism":not data["severe_mechanism"],
          "no_palpable_skull_fracture":not data["palpable_skull_fracture"],
          "acting_normally_parent":data["acting_normally_parent"],
        }
        age_band="<2"
    else:
        required2=("basilar_skull_fracture_signs","loss_of_consciousness","vomiting","severe_headache")
        missing2=[k for k in required2 if data.get(k) is None]
        if missing2: raise ValueError("missing PECARN >=2 y inputs: "+", ".join(missing2))
        for k in required2:_bool(data[k],k)
        high=data["altered_mental_status"] or gcs<15 or data["basilar_skull_fracture_signs"]
        intermediate=(
          data["loss_of_consciousness"] or data["vomiting"] or data["severe_mechanism"] or data["severe_headache"]
        )
        low_criteria={
          "normal_mental_status":not data["altered_mental_status"] and gcs==15,
          "no_loss_of_consciousness":not data["loss_of_consciousness"],
          "no_vomiting":not data["vomiting"],
          "nonsevere_mechanism":not data["severe_mechanism"],
          "no_basilar_skull_fracture_signs":not data["basilar_skull_fracture_signs"],
          "no_severe_headache":not data["severe_headache"],
        }
        age_band=">=2"
    if high: classification="higher_risk_ct_recommended_pathway"
    elif intermediate: classification="intermediate_ct_vs_observation_pathway"
    else: classification="very_low_risk_ciTBI"
    return {
      "id":"pecarn-head-injury","status":"complete","age_band":age_band,
      "classification":classification,"very_low_risk_criteria":low_criteria,
      "warning":"PECARN applies to minor blunt head trauma and supports CT avoidance/risk stratification; it does not replace clinical judgment or management of unstable/penetrating injury.",
      "source":SOURCES["pecarn-head-injury"],
    }
