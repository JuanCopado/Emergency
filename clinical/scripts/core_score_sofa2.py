#!/usr/bin/env python3
"""SOFA-2 (2025) — source-encoded contemporary organ dysfunction score.

Primary source:
Ranzani OT, Singer M, Salluh JIF, et al. JAMA. 2025;334(23):2090-2103.
doi:10.1001/jama.2025.20516

This implementation keeps SOFA-2 separate from SOFA-1 and requires explicit
classification of contemporary organ supports rather than inferring them from text.
"""

import math

SOURCE={
    "authority":"JAMA 2025 SOFA-2 development/validation",
    "version":"SOFA-2 2025",
    "doi":"10.1001/jama.2025.20516",
    "url":"https://jamanetwork.com/journals/jama/fullarticle/2840822",
}

def _num(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)

def _bool(value,name):
    if not isinstance(value,bool):
        raise ValueError(f"{name} must be boolean")
    return value

def _brain(gcs, delirium_drug_required):
    g=int(_num(gcs,"gcs"))
    if g<3 or g>15:
        raise ValueError("gcs must be 3-15")
    _bool(delirium_drug_required,"delirium_drug_required")
    if g==15:
        score=0
    elif g>=13:
        score=1
    elif g>=9:
        score=2
    elif g>=6:
        score=3
    else:
        score=4
    if delirium_drug_required:
        score=max(score,1)
    return score

def _respiratory(pf, advanced_support, ecmo):
    ratio=_num(pf,"pao2_fio2_mmHg")
    if ratio<0:
        raise ValueError("pao2_fio2_mmHg cannot be negative")
    _bool(advanced_support,"advanced_ventilatory_support")
    _bool(ecmo,"ecmo")
    if ecmo:
        return 4
    if ratio<=75 and advanced_support:
        return 4
    if ratio<=150 and advanced_support:
        return 3
    if ratio<=225:
        return 2
    if ratio<=300:
        return 1
    return 0

def _cardiovascular(map_mmHg, norepi, epi, other_vasoactive, mechanical_support):
    m=_num(map_mmHg,"map_mmHg")
    ne=_num(norepi,"norepinephrine_mcg_kg_min")
    ep=_num(epi,"epinephrine_mcg_kg_min")
    if min(m,ne,ep)<0:
        raise ValueError("MAP and catecholamine doses cannot be negative")
    _bool(other_vasoactive,"other_vasopressor_or_inotrope")
    _bool(mechanical_support,"mechanical_circulatory_support")
    cate=ne+ep
    if mechanical_support:
        return 4
    if cate>0.4:
        return 4
    if cate>0.2:
        return 4 if other_vasoactive else 3
    if cate>0:
        return 3 if other_vasoactive else 2
    if other_vasoactive:
        return 2
    return 0 if m>=70 else 1

def _liver(bilirubin):
    b=_num(bilirubin,"bilirubin_mg_dL")
    if b<0:
        raise ValueError("bilirubin_mg_dL cannot be negative")
    if b<=1.2:
        return 0
    if b<=3.0:
        return 1
    if b<=6.0:
        return 2
    if b<=12.0:
        return 3
    return 4

def _kidney(creatinine, oliguria_6_12h, oliguria_ge12h, severe_oliguria_ge24h, anuria_ge12h, rrt):
    cr=_num(creatinine,"creatinine_mg_dL")
    if cr<0:
        raise ValueError("creatinine_mg_dL cannot be negative")
    flags={
        "urine_lt_0_5_ml_kg_h_6_12h":oliguria_6_12h,
        "urine_lt_0_5_ml_kg_h_ge12h":oliguria_ge12h,
        "urine_lt_0_3_ml_kg_h_ge24h":severe_oliguria_ge24h,
        "anuria_ge12h":anuria_ge12h,
        "receiving_or_meets_rrt_criteria":rrt,
    }
    for k,v in flags.items():
        _bool(v,k)
    if rrt:
        return 4
    urine_score=0
    if severe_oliguria_ge24h or anuria_ge12h:
        urine_score=3
    elif oliguria_ge12h:
        urine_score=2
    elif oliguria_6_12h:
        urine_score=1
    if cr<=1.2:
        cr_score=0
    elif cr<=2.0:
        cr_score=1
    elif cr<=3.5:
        cr_score=2
    else:
        cr_score=3
    return max(cr_score,urine_score)

def _hemostasis(platelets):
    p=_num(platelets,"platelets_10e3_uL")
    if p<0:
        raise ValueError("platelets_10e3_uL cannot be negative")
    if p>150:
        return 0
    if p>100:
        return 1
    if p>80:
        return 2
    if p>50:
        return 3
    return 4

def calculate_sofa2(data):
    required=(
        "gcs","delirium_drug_required",
        "pao2_fio2_mmHg","advanced_ventilatory_support","ecmo",
        "map_mmHg","norepinephrine_mcg_kg_min","epinephrine_mcg_kg_min",
        "other_vasopressor_or_inotrope","mechanical_circulatory_support",
        "bilirubin_mg_dL","creatinine_mg_dL",
        "urine_lt_0_5_ml_kg_h_6_12h","urine_lt_0_5_ml_kg_h_ge12h",
        "urine_lt_0_3_ml_kg_h_ge24h","anuria_ge12h",
        "receiving_or_meets_rrt_criteria","platelets_10e3_uL",
    )
    missing=[k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing SOFA-2 inputs: "+", ".join(missing))

    components={
        "brain":_brain(data["gcs"],data["delirium_drug_required"]),
        "respiratory":_respiratory(
            data["pao2_fio2_mmHg"],
            data["advanced_ventilatory_support"],
            data["ecmo"],
        ),
        "cardiovascular":_cardiovascular(
            data["map_mmHg"],
            data["norepinephrine_mcg_kg_min"],
            data["epinephrine_mcg_kg_min"],
            data["other_vasopressor_or_inotrope"],
            data["mechanical_circulatory_support"],
        ),
        "liver":_liver(data["bilirubin_mg_dL"]),
        "kidney":_kidney(
            data["creatinine_mg_dL"],
            data["urine_lt_0_5_ml_kg_h_6_12h"],
            data["urine_lt_0_5_ml_kg_h_ge12h"],
            data["urine_lt_0_3_ml_kg_h_ge24h"],
            data["anuria_ge12h"],
            data["receiving_or_meets_rrt_criteria"],
        ),
        "hemostasis":_hemostasis(data["platelets_10e3_uL"]),
    }
    total=sum(components.values())
    return {
        "id":"sofa-2",
        "version":"SOFA-2 2025",
        "status":"complete",
        "components":components,
        "total":total,
        "range":[0,24],
        "warning":"SOFA-2 describes organ dysfunction in critically ill adults. Do not mix its thresholds with SOFA-1/Sepsis-3 and do not use it as a stand-alone mortality prediction or treatment rule.",
        "source":SOURCE,
    }
