#!/usr/bin/env python3
"""SPECIALIST block 1: neurology / neurocritical care."""

import math

SOURCES={
  "canadian-tia-score":{
    "authority":"Perry et al., BMJ 2021",
    "url":"https://www.bmj.com/content/372/bmj.n49",
    "version":"Canadian TIA Score -3 to 23",
  },
  "pc-aspects":{
    "authority":"Puetz et al. / posterior circulation ASPECTS",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC7051302/",
    "version":"pc-ASPECTS 0-10",
  },
  "four-score":{
    "authority":"Wijdicks et al., Ann Neurol 2005",
    "url":"https://pubmed.ncbi.nlm.nih.gov/16178024/",
    "version":"FOUR Score 0-16",
  },
  "hunt-hess":{
    "authority":"Traditional Hunt-Hess SAH grade",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6404699/",
    "version":"Hunt-Hess I-V",
  },
  "wfns-sah":{
    "authority":"WFNS SAH grade",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC4794735/",
    "version":"WFNS I-V",
  },
  "stess":{
    "authority":"Rossetti et al. / STESS",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC10839336/",
    "version":"STESS 0-6",
  },
  "bacterial-meningitis-score":{
    "authority":"Nigrovic et al. / Bacterial Meningitis Score",
    "url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC4543184/",
    "version":"BMS 0-6",
  },
}

def _num(v,name):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError(f"{name} must be a finite number")
    return float(v)

def _bool(v,name):
    if not isinstance(v,bool): raise ValueError(f"{name} must be boolean")
    return v

def calculate_canadian_tia(data):
    bool_keys=(
      "first_tia","symptoms_ge_10_min","history_carotid_stenosis","on_antiplatelet",
      "gait_disturbance","unilateral_weakness","vertigo","dysarthria_or_aphasia",
      "af_on_ecg","infarct_on_ct"
    )
    missing=[k for k in bool_keys if data.get(k) is None]
    for k in ("diastolic_bp_mmHg","platelets_10e9_L","glucose_mmol_L"):
        if data.get(k) is None: missing.append(k)
    if missing: raise ValueError("missing Canadian TIA Score inputs: "+", ".join(missing))
    for k in bool_keys: _bool(data[k],k)
    dbp=_num(data["diastolic_bp_mmHg"],"diastolic_bp_mmHg")
    platelets=_num(data["platelets_10e9_L"],"platelets_10e9_L")
    glucose=_num(data["glucose_mmol_L"],"glucose_mmol_L")
    components={
      "first_tia":2 if data["first_tia"] else 0,
      "symptoms_ge_10_min":2 if data["symptoms_ge_10_min"] else 0,
      "history_carotid_stenosis":2 if data["history_carotid_stenosis"] else 0,
      "on_antiplatelet":3 if data["on_antiplatelet"] else 0,
      "gait_disturbance":1 if data["gait_disturbance"] else 0,
      "unilateral_weakness":1 if data["unilateral_weakness"] else 0,
      "vertigo":-3 if data["vertigo"] else 0,
      "dbp_ge_110":3 if dbp>=110 else 0,
      "dysarthria_or_aphasia":1 if data["dysarthria_or_aphasia"] else 0,
      "af_on_ecg":2 if data["af_on_ecg"] else 0,
      "infarct_on_ct":1 if data["infarct_on_ct"] else 0,
      "platelets_ge_400":2 if platelets>=400 else 0,
      "glucose_ge_15":3 if glucose>=15 else 0,
    }
    total=sum(components.values())
    tier="low" if total<=3 else "medium" if total<=8 else "high"
    return {
      "id":"canadian-tia-score","status":"complete","components":components,
      "total":total,"range":[-3,23],"risk_tier":tier,
      "warning":"Canadian TIA Score stratifies short-term risk after a clinician-diagnosed TIA/minor stroke; it does not establish the diagnosis or replace urgent vascular/cardiac evaluation.",
      "source":SOURCES["canadian-tia-score"],
    }

def calculate_pc_aspects(data):
    keys=(
      "left_thalamus","right_thalamus","left_cerebellum","right_cerebellum",
      "left_pca_territory","right_pca_territory","midbrain","pons"
    )
    missing=[k for k in keys if data.get(k) is None]
    if missing: raise ValueError("missing pc-ASPECTS regions: "+", ".join(missing))
    for k in keys: _bool(data[k],k)
    penalties={
      "left_thalamus":1,"right_thalamus":1,"left_cerebellum":1,"right_cerebellum":1,
      "left_pca_territory":1,"right_pca_territory":1,"midbrain":2,"pons":2
    }
    deductions={k:(penalties[k] if data[k] else 0) for k in keys}
    score=10-sum(deductions.values())
    return {
      "id":"pc-aspects","status":"complete","deductions":deductions,"score":score,"range":[0,10],
      "warning":"pc-ASPECTS is an imaging score and requires direct review of the appropriate posterior-circulation study; do not infer regions from narrative alone.",
      "source":SOURCES["pc-aspects"],
    }

FOUR_MAPS={
  "eye":{"tracking_or_blinking_command":4,"open_no_tracking":3,"opens_to_loud_voice":2,"opens_to_pain":1,"closed_with_pain":0},
  "motor":{"thumbs_fist_peace":4,"localizes_pain":3,"flexion_to_pain":2,"extension_to_pain":1,"no_response_or_myoclonus":0},
  "brainstem":{"pupil_and_corneal_present":4,"one_pupil_wide_fixed":3,"pupil_or_corneal_absent":2,"pupil_and_corneal_absent":1,"pupil_corneal_cough_absent":0},
  "respiration":{"regular_not_intubated":4,"cheyne_stokes_not_intubated":3,"irregular_not_intubated":2,"breathes_above_ventilator":1,"ventilator_rate_or_apnea":0},
}

def calculate_four_score(data):
    components={}
    for domain,mapping in FOUR_MAPS.items():
        value=data.get(domain)
        if value is None: raise ValueError(f"missing FOUR {domain}")
        key=str(value).strip().lower()
        if key not in mapping: raise ValueError(f"unsupported FOUR {domain} category")
        components[domain]=mapping[key]
    return {
      "id":"four-score","status":"complete","components":components,
      "total":sum(components.values()),"range":[0,16],
      "source":SOURCES["four-score"],
    }

def classify_hunt_hess(data):
    grade=data.get("grade")
    if grade is not None:
        g=int(_num(grade,"grade"))
        if g not in (1,2,3,4,5): raise ValueError("Hunt-Hess grade must be 1-5")
        return {"id":"hunt-hess","status":"explicit_grade","grade":g,"source":SOURCES["hunt-hess"]}
    category=str(data.get("clinical_category","")).strip().lower()
    mapping={
      "asymptomatic_or_mild_headache_slight_nuchal_rigidity":1,
      "moderate_severe_headache_nuchal_rigidity_no_deficit_except_cn_palsy":2,
      "drowsy_confused_or_mild_focal_deficit":3,
      "stupor_moderate_severe_hemiparesis_or_early_decerebrate":4,
      "deep_coma_decerebrate_moribund":5,
    }
    if category not in mapping: raise ValueError("unsupported Hunt-Hess clinical_category")
    return {"id":"hunt-hess","status":"complete","grade":mapping[category],"source":SOURCES["hunt-hess"]}

def calculate_wfns_sah(data):
    if data.get("gcs") is None or data.get("focal_motor_deficit") is None:
        raise ValueError("WFNS requires gcs and focal_motor_deficit")
    g=int(_num(data["gcs"],"gcs"))
    if g<3 or g>15: raise ValueError("gcs must be 3-15")
    _bool(data["focal_motor_deficit"],"focal_motor_deficit")
    if g==15: grade=1
    elif g in (13,14): grade=3 if data["focal_motor_deficit"] else 2
    elif 7<=g<=12: grade=4
    else: grade=5
    return {"id":"wfns-sah","status":"complete","grade":grade,"range":[1,5],"source":SOURCES["wfns-sah"]}

def calculate_stess(data):
    required=("age","previous_seizures","consciousness","worst_seizure_type")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing STESS inputs: "+", ".join(missing))
    age=_num(data["age"],"age")
    _bool(data["previous_seizures"],"previous_seizures")
    c=str(data["consciousness"]).strip().lower()
    s=str(data["worst_seizure_type"]).strip().lower()
    c_map={"alert":0,"somnolent":0,"confused":0,"stuporous":1,"comatose":1}
    s_map={"focal":0,"focal_aware":0,"focal_impaired_awareness":0,"absence":0,"myoclonic":0,"generalized_convulsive":1,"ncse_in_coma":2}
    if c not in c_map or s not in s_map: raise ValueError("unsupported STESS category")
    components={
      "age":2 if age>=65 else 0,
      "previous_seizures":0 if data["previous_seizures"] else 1,
      "consciousness":c_map[c],
      "worst_seizure_type":s_map[s],
    }
    total=sum(components.values())
    return {
      "id":"stess","status":"complete","components":components,"total":total,"range":[0,6],
      "warning":"STESS is a prognostic adjunct in status epilepticus and should not be used alone for treatment limitation or neuroprognostication.",
      "source":SOURCES["stess"],
    }

def calculate_bacterial_meningitis_score(data):
    required=("positive_csf_gram_stain","csf_anc_per_uL","csf_protein_mg_dL","peripheral_anc_per_uL","seizure_with_illness")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Bacterial Meningitis Score inputs: "+", ".join(missing))
    _bool(data["positive_csf_gram_stain"],"positive_csf_gram_stain")
    _bool(data["seizure_with_illness"],"seizure_with_illness")
    csf_anc=_num(data["csf_anc_per_uL"],"csf_anc_per_uL")
    protein=_num(data["csf_protein_mg_dL"],"csf_protein_mg_dL")
    pb_anc=_num(data["peripheral_anc_per_uL"],"peripheral_anc_per_uL")
    components={
      "positive_csf_gram_stain":2 if data["positive_csf_gram_stain"] else 0,
      "csf_anc_ge_1000":1 if csf_anc>=1000 else 0,
      "csf_protein_ge_80":1 if protein>=80 else 0,
      "peripheral_anc_ge_10000":1 if pb_anc>=10000 else 0,
      "seizure":1 if data["seizure_with_illness"] else 0,
    }
    total=sum(components.values())
    return {
      "id":"bacterial-meningitis-score","status":"complete","components":components,
      "total":total,"range":[0,6],"very_low_risk_if_zero":total==0,
      "warning":"BMS applies to selected children with CSF pleocytosis and important exclusion criteria; a score of 0 does not override clinical instability, immunosuppression, CNS devices/recent neurosurgery or another bacterial focus.",
      "source":SOURCES["bacterial-meningitis-score"],
    }
