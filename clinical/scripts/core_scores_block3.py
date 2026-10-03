#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 3 pulmonary embolism."""

import math

SOURCES={
  "wells-pe":{
    "authority":"2026 AHA/ACC/ACCP/ACEP/CHEST/SCAI/SHM/SIR/SVM/SVN PE Guideline",
    "url":"https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005",
    "version":"Wells PE standard and modified interpretations",
  },
  "perc":{
    "authority":"2026 AHA/ACC/ACCP/ACEP/CHEST PE Guideline + PERC validation literature",
    "url":"https://www.ahajournals.org/doi/pdf/10.1161/CIR.0000000000001415",
    "version":"PERC 8-item rule",
  },
  "years-pe":{
    "authority":"YEARS prospective multicentre cohort",
    "url":"https://pubmed.ncbi.nlm.nih.gov/28549662/",
    "version":"YEARS 2017",
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

def calculate_wells_pe(data):
    required=(
      "clinical_signs_dvt","pe_more_likely_than_alternative","heart_rate_bpm",
      "immobilization_ge3d_or_surgery_4w","previous_dvt_pe","hemoptysis","active_cancer"
    )
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing Wells PE inputs: "+", ".join(missing))
    for k in required:
        if k!="heart_rate_bpm": _bool(data[k],k)
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    if hr<0: raise ValueError("heart_rate_bpm cannot be negative")

    components={
      "clinical_signs_dvt":3.0 if data["clinical_signs_dvt"] else 0.0,
      "pe_more_likely_than_alternative":3.0 if data["pe_more_likely_than_alternative"] else 0.0,
      "heart_rate_gt_100":1.5 if hr>100 else 0.0,
      "immobilization_or_surgery":1.5 if data["immobilization_ge3d_or_surgery_4w"] else 0.0,
      "previous_dvt_pe":1.5 if data["previous_dvt_pe"] else 0.0,
      "hemoptysis":1.0 if data["hemoptysis"] else 0.0,
      "active_cancer":1.0 if data["active_cancer"] else 0.0,
    }
    total=sum(components.values())
    standard="low" if total<2 else "moderate" if total<=6 else "high"
    modified="pe_unlikely" if total<=4 else "pe_likely"
    return {
      "id":"wells-pe","status":"complete","components":components,"total":total,
      "standard_three_level":standard,"modified_two_level":modified,
      "warning":"Wells estimates pretest probability and must be integrated with the chosen diagnostic pathway, D-dimer strategy, pregnancy status and hemodynamic context.",
      "source":SOURCES["wells-pe"],
    }

def calculate_perc(data):
    required=(
      "low_pretest_probability","age","heart_rate_bpm","spo2_percent","hemoptysis",
      "estrogen_use","previous_dvt_pe","unilateral_leg_swelling",
      "recent_surgery_or_trauma_requiring_hospitalization_4w"
    )
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing PERC inputs: "+", ".join(missing))
    if data["low_pretest_probability"] is not True:
        raise ValueError("PERC may only be applied after explicit low pretest probability assessment")
    for k in ("hemoptysis","estrogen_use","previous_dvt_pe","unilateral_leg_swelling",
              "recent_surgery_or_trauma_requiring_hospitalization_4w"):
        _bool(data[k],k)
    age=_num(data["age"],"age")
    hr=_num(data["heart_rate_bpm"],"heart_rate_bpm")
    spo2=_num(data["spo2_percent"],"spo2_percent")
    if age<0 or hr<0 or not 0<=spo2<=100: raise ValueError("invalid age/heart rate/SpO2")

    positive_criteria={
      "age_50_or_more":age>=50,
      "heart_rate_100_or_more":hr>=100,
      "spo2_below_95":spo2<95,
      "hemoptysis":data["hemoptysis"],
      "estrogen_use":data["estrogen_use"],
      "previous_dvt_pe":data["previous_dvt_pe"],
      "unilateral_leg_swelling":data["unilateral_leg_swelling"],
      "recent_surgery_or_trauma_hospitalization":data["recent_surgery_or_trauma_requiring_hospitalization_4w"],
    }
    count=sum(1 for v in positive_criteria.values() if v)
    return {
      "id":"perc","status":"complete","positive_criteria":positive_criteria,
      "positive_count":count,"perc_negative":count==0,
      "interpretation":"PERC-negative only supports stopping PE testing in an appropriately selected very-low/low-risk population.",
      "source":SOURCES["perc"],
    }

def calculate_years(data):
    required=("clinical_signs_dvt","hemoptysis","pe_most_likely","d_dimer_ng_mL_feu")
    missing=[k for k in required if data.get(k) is None]
    if missing: raise ValueError("missing YEARS inputs: "+", ".join(missing))
    for k in ("clinical_signs_dvt","hemoptysis","pe_most_likely"): _bool(data[k],k)
    dd=_num(data["d_dimer_ng_mL_feu"],"d_dimer_ng_mL_feu")
    if dd<0: raise ValueError("d_dimer_ng_mL_feu cannot be negative")
    items={
      "clinical_signs_dvt":1 if data["clinical_signs_dvt"] else 0,
      "hemoptysis":1 if data["hemoptysis"] else 0,
      "pe_most_likely":1 if data["pe_most_likely"] else 0,
    }
    n=sum(items.values())
    threshold=1000.0 if n==0 else 500.0
    excluded=dd<threshold
    return {
      "id":"years-pe","status":"complete","items":items,"years_item_count":n,
      "d_dimer_ng_mL_feu":dd,"active_threshold_ng_mL_feu":threshold,
      "pe_excluded_by_years":excluded,
      "next_step":"no_ctpa_by_years" if excluded else "ctpa_or_pathway_imaging_required",
      "warning":"Thresholds are encoded in ng/mL FEU. Do not silently apply them to DDU or a differently reported assay. Pregnancy-adapted YEARS is a separate rule.",
      "source":SOURCES["years-pe"],
    }
