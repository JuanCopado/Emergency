#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 7 cardiology."""

import math

SOURCES={
 "timi-ua-nstemi":{"url":"https://pubmed.ncbi.nlm.nih.gov/10938172/","version":"TIMI UA/NSTEMI 2000"},
 "has-bled":{"url":"https://pubmed.ncbi.nlm.nih.gov/21111555/","version":"HAS-BLED"},
 "canadian-syncope":{"url":"https://pubmed.ncbi.nlm.nih.gov/27378464/","version":"Canadian Syncope Risk Score"},
 "killip-kimball":{"url":"https://academic.oup.com/eurheartj/article/26/4/384/2888056","version":"Killip-Kimball"},
 "scai-shock":{"url":"https://www.jacc.org/doi/10.1016/j.jacc.2022.01.018","version":"SCAI SHOCK 2022 update"},
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be finite")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def calculate_timi_ua_nstemi(data):
    req=("age","cad_risk_factor_count","known_coronary_stenosis_ge50","st_deviation","severe_angina_ge2_episodes_24h","aspirin_last_7d","elevated_cardiac_markers")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing TIMI inputs: "+", ".join(missing))
    age=_num(data["age"],"age"); rf=int(_num(data["cad_risk_factor_count"],"cad_risk_factor_count"))
    if age<0 or rf<0: raise ValueError("age/risk factors cannot be negative")
    for k in req[2:]: _bool(data[k],k)
    comp={
      "age_ge65":1 if age>=65 else 0,
      "three_or_more_cad_risk_factors":1 if rf>=3 else 0,
      "known_coronary_stenosis_ge50":1 if data["known_coronary_stenosis_ge50"] else 0,
      "st_deviation":1 if data["st_deviation"] else 0,
      "severe_angina_ge2_episodes_24h":1 if data["severe_angina_ge2_episodes_24h"] else 0,
      "aspirin_last_7d":1 if data["aspirin_last_7d"] else 0,
      "elevated_cardiac_markers":1 if data["elevated_cardiac_markers"] else 0,
    }
    total=sum(comp.values())
    return {"id":"timi-ua-nstemi","status":"complete","components":comp,"total":total,"range":[0,7],
            "warning":"TIMI UA/NSTEMI is a prognostic risk score for NSTE-ACS and is not a diagnostic rule-out test.",
            "source":SOURCES["timi-ua-nstemi"]}

def calculate_has_bled(data):
    req=("hypertension","abnormal_renal_function","abnormal_liver_function","stroke_history","bleeding_history_or_predisposition","labile_inr","age_over_65","drugs_predisposing_bleeding","alcohol_use")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing HAS-BLED components: "+", ".join(missing))
    for k in req: _bool(data[k],k)
    comp={
      "H_hypertension":1 if data["hypertension"] else 0,
      "A_renal":1 if data["abnormal_renal_function"] else 0,
      "A_liver":1 if data["abnormal_liver_function"] else 0,
      "S_stroke":1 if data["stroke_history"] else 0,
      "B_bleeding":1 if data["bleeding_history_or_predisposition"] else 0,
      "L_labile_inr":1 if data["labile_inr"] else 0,
      "E_age_over65":1 if data["age_over_65"] else 0,
      "D_drugs":1 if data["drugs_predisposing_bleeding"] else 0,
      "D_alcohol":1 if data["alcohol_use"] else 0,
    }
    total=sum(comp.values())
    return {"id":"has-bled","status":"complete","components":comp,"total":total,"range":[0,9],
            "warning":"HAS-BLED identifies modifiable bleeding-risk factors and need for closer review; a high score alone is not a reason to withhold indicated anticoagulation.",
            "source":SOURCES["has-bled"]}

def calculate_canadian_syncope(data):
    req=("predisposition_vasovagal","history_heart_disease","any_sbp_below90_or_above180","troponin_above_99pct","qrs_axis_deg","qrs_duration_ms","qtc_ms","ed_diagnosis")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing Canadian Syncope inputs: "+", ".join(missing))
    for k in req[:4]: _bool(data[k],k)
    axis=_num(data["qrs_axis_deg"],"qrs_axis_deg"); qrs=_num(data["qrs_duration_ms"],"qrs_duration_ms"); qtc=_num(data["qtc_ms"],"qtc_ms")
    diagnosis=str(data["ed_diagnosis"]).strip().lower()
    if diagnosis not in {"vasovagal","cardiac","other"}: raise ValueError("ed_diagnosis must be vasovagal/cardiac/other")
    comp={
      "predisposition_vasovagal":-1 if data["predisposition_vasovagal"] else 0,
      "history_heart_disease":1 if data["history_heart_disease"] else 0,
      "sbp_extreme":2 if data["any_sbp_below90_or_above180"] else 0,
      "troponin_above_99pct":2 if data["troponin_above_99pct"] else 0,
      "abnormal_qrs_axis":1 if (axis < -30 or axis > 100) else 0,
      "qrs_duration_gt130":1 if qrs>130 else 0,
      "qtc_gt480":2 if qtc>480 else 0,
      "ed_diagnosis":-2 if diagnosis=="vasovagal" else 2 if diagnosis=="cardiac" else 0,
    }
    total=sum(comp.values())
    band="very_low" if total<=-2 else "low" if total<=0 else "medium" if total<=3 else "high" if total<=5 else "very_high"
    return {"id":"canadian-syncope","status":"complete","components":comp,"total":total,"range":[-3,11],"risk_band":band,
            "warning":"CSRS applies after ED assessment of syncope. It does not replace evaluation for immediately dangerous causes or clinical judgment.",
            "source":SOURCES["canadian-syncope"]}

def calculate_killip_kimball(data):
    state=data.get("state")
    if state is None: raise ValueError("Killip state required")
    key=str(state).strip().lower()
    mapping={
      "no_heart_failure":1,
      "mild_moderate_heart_failure":2,
      "pulmonary_edema":3,
      "cardiogenic_shock":4,
    }
    if key not in mapping: raise ValueError("state must be no_heart_failure/mild_moderate_heart_failure/pulmonary_edema/cardiogenic_shock")
    klass=mapping[key]
    return {"id":"killip-kimball","status":"complete","class":klass,"state":key,"range":[1,4],
            "warning":"Killip-Kimball is a bedside severity classification developed in acute MI; assignment remains clinical and should be updated if the patient's condition changes.",
            "source":SOURCES["killip-kimball"]}

def calculate_scai_shock(data):
    req=("at_risk_condition","hemodynamic_instability","hypoperfusion","initial_support_started","initial_support_failed","circulatory_collapse_or_extremis")
    missing=[k for k in req if data.get(k) is None]
    if missing: raise ValueError("missing SCAI shock inputs: "+", ".join(missing))
    for k in req: _bool(data[k],k)
    if data["circulatory_collapse_or_extremis"]:
        stage="E"
    elif data["hypoperfusion"] and data["initial_support_started"] and data["initial_support_failed"]:
        stage="D"
    elif data["hypoperfusion"]:
        if not data["initial_support_started"]:
            raise ValueError("SCAI stage C+ hypoperfusion requires explicit initial_support_started status")
        stage="C"
    elif data["hemodynamic_instability"]:
        stage="B"
    elif data["at_risk_condition"]:
        stage="A"
    else:
        raise ValueError("patient does not meet SCAI A-E input definition; confirm at-risk condition and shock context")
    names={"A":"at_risk","B":"beginning","C":"classic","D":"deteriorating","E":"extremis"}
    return {"id":"scai-shock","status":"complete","stage":stage,"stage_name":names[stage],
            "warning":"SCAI shock stage is dynamic. Reassess over time; stage D requires failure of an initial support strategy and stage E denotes actual/impending collapse.",
            "source":SOURCES["scai-shock"]}
