#!/usr/bin/env python3
"""CORE scores block 6: obstetrics and burn-size tools."""

import math

SOURCES={
  "bishop":{
    "authority":"Bishop score table / NCBI Bookshelf",
    "url":"https://www.ncbi.nlm.nih.gov/books/NBK615337/table/ch10.tab8/",
    "version":"Traditional Bishop Score",
  },
  "meows":{
    "authority":"Norfolk and Norwich University Hospitals NHS Foundation Trust",
    "url":"https://www.nnuh.nhs.uk/publication/download/modified-early-obstetric-warning-score-meows-mid33-ao13-v7/",
    "version":"NNUH MEOWS v7 (2022 guideline; embedded chart)",
  },
  "rule-of-nines":{
    "authority":"WHO burns mass-casualty standards 2024",
    "url":"https://www.ncbi.nlm.nih.gov/sites/books/NBK609553/",
    "version":"Wallace Rule of Nines — adults",
  },
  "lund-browder":{
    "authority":"Lund-Browder age-adjusted burn chart",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC8690712/",
    "version":"Lund-Browder age bands <1, 1-<5, 5-<10, 10-14, >14 years",
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

def calculate_bishop(data):
    required=("dilation_cm","effacement_band","station","consistency","position")
    missing=[k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing Bishop inputs: "+", ".join(missing))
    dilation=_num(data["dilation_cm"],"dilation_cm")
    if dilation<0:
        raise ValueError("dilation_cm cannot be negative")
    if dilation==0:
        dilation_score=0
    elif dilation<=2:
        dilation_score=1
    elif dilation<=4:
        dilation_score=2
    else:
        dilation_score=3

    eff=str(data["effacement_band"]).strip().lower()
    eff_map={"0_30":0,"40_50":1,"60_70":2,"80_plus":3}
    if eff not in eff_map:
        raise ValueError("effacement_band must be 0_30, 40_50, 60_70, or 80_plus")

    station=_num(data["station"],"station")
    if station==-3:
        station_score=0
    elif station==-2:
        station_score=1
    elif station in (-1,0):
        station_score=2
    elif station in (1,2):
        station_score=3
    else:
        raise ValueError("station must be -3, -2, -1, 0, +1, or +2")

    consistency=str(data["consistency"]).strip().lower()
    consistency_map={"firm":0,"medium":1,"soft":2}
    if consistency not in consistency_map:
        raise ValueError("consistency must be firm, medium, or soft")

    position=str(data["position"]).strip().lower()
    position_map={"posterior":0,"mid":1,"midposition":1,"anterior":2}
    if position not in position_map:
        raise ValueError("position must be posterior, mid, or anterior")

    components={
        "dilation":dilation_score,
        "effacement":eff_map[eff],
        "station":station_score,
        "consistency":consistency_map[consistency],
        "position":position_map[position],
    }
    total=sum(components.values())
    return {
        "id":"bishop","status":"complete","components":components,"total":total,"range":[0,13],
        "warning":"Bishop score estimates cervical favorability; induction decisions depend on the full obstetric context and local protocol.",
        "source":SOURCES["bishop"],
    }

def _meows_temperature(x):
    if x<35:return 2
    if x<36:return 1
    if x<37.5:return 0
    if x<38:return 1
    if x<39:return 2
    return 3

def _meows_sbp(x):
    if x<=70:return 3
    if x<=79:return 2
    if x<=89:return 1
    if x<=139:return 0
    if x<=149:return 1
    if x<=159:return 2
    return 3

def _meows_dbp(x):
    if x<=49:return 1
    if x<=89:return 0
    if x<=99:return 1
    if x<=109:return 2
    return 3

def _meows_pulse(x):
    if x<40:return 2
    if x<=49:return 1
    if x<=99:return 0
    if x<=109:return 1
    if x<=129:return 2
    return 3

def _meows_rr(x):
    if x<=10:return 3
    if x<=20:return 0
    if x<=24:return 1
    if x<=29:return 2
    return 3

def calculate_meows_nnuh_v7(data):
    required=("temperature_c","systolic_bp_mmHg","diastolic_bp_mmHg","pulse_bpm","respiratory_rate","avpu")
    missing=[k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing MEOWS inputs: "+", ".join(missing))
    t=_num(data["temperature_c"],"temperature_c")
    sbp=_num(data["systolic_bp_mmHg"],"systolic_bp_mmHg")
    dbp=_num(data["diastolic_bp_mmHg"],"diastolic_bp_mmHg")
    pulse=_num(data["pulse_bpm"],"pulse_bpm")
    rr=_num(data["respiratory_rate"],"respiratory_rate")
    if min(sbp,dbp,pulse,rr)<0:
        raise ValueError("MEOWS vital signs cannot be negative")

    avpu=str(data["avpu"]).strip().lower()
    avpu_map={"alert":0,"a":0,"voice":1,"v":1,"pain":2,"p":2,"unconscious":3,"unresponsive":3,"u":3}
    if avpu not in avpu_map:
        raise ValueError("avpu must be A/V/P/U")

    community_without_spo2=bool(data.get("community_without_spo2",False))
    spo2=data.get("spo2_percent")
    if spo2 is None and not community_without_spo2:
        raise ValueError("spo2_percent required unless community_without_spo2=true")
    if spo2 is None:
        spo2_score=None
    else:
        spo2=_num(spo2,"spo2_percent")
        if not 0<=spo2<=100:
            raise ValueError("spo2_percent must be 0-100")
        spo2_score=3 if spo2<=94 else 0

    urine=data.get("urine_output_mL_h")
    if urine is None:
        urine_score=0
        urine_measured=False
    else:
        urine=_num(urine,"urine_output_mL_h")
        if urine<0:
            raise ValueError("urine_output_mL_h cannot be negative")
        urine_score=3 if urine<10 else 2 if urine<30 else 0
        urine_measured=True

    components={
        "temperature":_meows_temperature(t),
        "systolic_bp":_meows_sbp(sbp),
        "diastolic_bp":_meows_dbp(dbp),
        "pulse":_meows_pulse(pulse),
        "respiratory_rate":_meows_rr(rr),
        "spo2":spo2_score,
        "avpu":avpu_map[avpu],
        "urine_output":urine_score,
    }
    scored=[v for v in components.values() if v is not None]
    total=sum(scored)
    any_single_3=any(v==3 for v in scored)
    if total>=4 or any_single_3:
        action="call_out_cascade"
    elif total>=1:
        action="repeat_observations_and_consider_review"
    else:
        action="routine_observation"
    return {
        "id":"meows","version":"NNUH MEOWS v7","status":"complete",
        "components":components,"total":total,"single_parameter_score_3":any_single_3,
        "action_band":action,"spo2_measured":spo2 is not None,"urine_output_measured":urine_measured,
        "warning":"This is the NNUH MEOWS chart, not a universal MEOWS. Local maternity policy may use different thresholds and must supersede this chart.",
        "source":SOURCES["meows"],
    }

RULE_OF_NINES_ADULT={
    "head_neck":9.0,
    "left_upper_limb":9.0,
    "right_upper_limb":9.0,
    "anterior_trunk":18.0,
    "posterior_trunk":18.0,
    "left_lower_limb":18.0,
    "right_lower_limb":18.0,
    "perineum":1.0,
}

def calculate_rule_of_nines(data):
    fractions=data.get("fractions")
    if not isinstance(fractions,dict):
        raise ValueError("fractions object required")
    unknown=[k for k in fractions if k not in RULE_OF_NINES_ADULT]
    if unknown:
        raise ValueError("unknown Rule of Nines regions: "+", ".join(unknown))
    contributions={}
    for region,percent in RULE_OF_NINES_ADULT.items():
        f=_num(fractions.get(region,0.0),region)
        if not 0<=f<=1:
            raise ValueError(f"{region} fraction must be 0-1")
        contributions[region]=percent*f
    total=sum(contributions.values())
    return {
        "id":"rule-of-nines","status":"complete","tbsa_percent":total,
        "contributions":contributions,
        "warning":"Adult Wallace Rule of Nines is a rapid estimate. Count partial- and full-thickness burns, not superficial erythema; use Lund-Browder in children or when greater precision is needed.",
        "source":SOURCES["rule-of-nines"],
    }

def _lb_age_values(age):
    if age<0: raise ValueError("age_years cannot be negative")
    if age<1:return 9.5,2.75,2.5
    if age<5:return 8.5,3.25,2.5
    if age<10:return 6.5,4.0,2.5
    if age<=14:return 5.5,4.25,3.0
    return 4.5,4.5,3.25

def calculate_lund_browder(data):
    if data.get("age_years") is None:
        raise ValueError("age_years required")
    age=_num(data["age_years"],"age_years")
    head,thigh,leg=_lb_age_values(age)
    # Each listed limb surface is for one limb and one surface. Buttocks are each whole buttock.
    weights={
        "head_anterior":head,"head_posterior":head,
        "neck_anterior":1.0,"neck_posterior":1.0,
        "trunk_anterior":13.0,"trunk_posterior":13.0,
        "left_upper_arm_anterior":2.0,"left_upper_arm_posterior":2.0,
        "right_upper_arm_anterior":2.0,"right_upper_arm_posterior":2.0,
        "left_forearm_anterior":1.5,"left_forearm_posterior":1.5,
        "right_forearm_anterior":1.5,"right_forearm_posterior":1.5,
        "left_hand_anterior":1.25,"left_hand_posterior":1.25,
        "right_hand_anterior":1.25,"right_hand_posterior":1.25,
        "left_thigh_anterior":thigh,"left_thigh_posterior":thigh,
        "right_thigh_anterior":thigh,"right_thigh_posterior":thigh,
        "left_leg_anterior":leg,"left_leg_posterior":leg,
        "right_leg_anterior":leg,"right_leg_posterior":leg,
        "left_foot_anterior":1.75,"left_foot_posterior":1.75,
        "right_foot_anterior":1.75,"right_foot_posterior":1.75,
        "left_buttock":2.5,"right_buttock":2.5,
        "perineum":1.0,
    }
    fractions=data.get("fractions")
    if not isinstance(fractions,dict):
        raise ValueError("fractions object required")
    unknown=[k for k in fractions if k not in weights]
    if unknown:
        raise ValueError("unknown Lund-Browder regions: "+", ".join(unknown))
    contributions={}
    for region,pct in weights.items():
        f=_num(fractions.get(region,0.0),region)
        if not 0<=f<=1:
            raise ValueError(f"{region} fraction must be 0-1")
        contributions[region]=pct*f
    total=sum(contributions.values())
    return {
        "id":"lund-browder","status":"complete","age_years":age,
        "tbsa_percent":total,"contributions":contributions,
        "full_body_check_percent":sum(weights.values()),
        "warning":"Count partial- and full-thickness burns only. Age-adjusted Lund-Browder is preferred over Rule of Nines for children; clinical burn mapping still requires direct examination.",
        "source":SOURCES["lund-browder"],
    }
