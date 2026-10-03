#!/usr/bin/env python3
"""Source-encoded CORE clinical scores — block 1.

Implemented:
- NIHSS (NINDS NIH Stroke Scale; explicit item scores only)
- Glasgow Coma Scale (structured adult GCS)
- NEWS2 (Royal College of Physicians 2017)
- SOFA-1 / Sepsis-3 classic score

This module is deliberately fail-closed. It does not infer score components from
free clinical text.
"""

import math

SOURCES = {
    "nihss": {
        "authority": "NINDS",
        "version": "NIH Stroke Scale updated February 2024",
        "url": "https://www.ninds.nih.gov/sites/default/files/documents/NIH-Stroke-Scale_updatedFeb2024_508.pdf",
    },
    "gcs": {
        "authority": "Glasgow Coma Scale / University of Glasgow",
        "version": "Structured GCS",
        "url": "https://www.glasgowcomascale.org/",
    },
    "news2": {
        "authority": "Royal College of Physicians",
        "version": "NEWS2 2017",
        "url": "https://www.rcp.ac.uk/resources/national-early-warning-score-news-2/",
    },
    "sofa": {
        "authority": "Sepsis-3 / JAMA",
        "version": "SOFA-1 classic table used in Sepsis-3 (2016)",
        "url": "https://jamanetwork.com/journals/jama/fullarticle/2492881",
        "version_warning": "SOFA-2 was published in 2025 and must be treated as a separate score/version.",
    },
}

NIHSS_ITEM_MAX = {
    "1a_loc": 3,
    "1b_loc_questions": 2,
    "1c_loc_commands": 2,
    "2_best_gaze": 2,
    "3_visual": 3,
    "4_facial_palsy": 3,
    "5a_left_arm": 4,
    "5b_right_arm": 4,
    "6a_left_leg": 4,
    "6b_right_leg": 4,
    "7_limb_ataxia": 2,
    "8_sensory": 2,
    "9_best_language": 3,
    "10_dysarthria": 2,
    "11_extinction_inattention": 2,
}

GCS_EYE = {
    "spontaneous": 4,
    "to_sound": 3,
    "to_pressure": 2,
    "none": 1,
}
GCS_VERBAL = {
    "oriented": 5,
    "orientated": 5,
    "confused": 4,
    "words": 3,
    "sounds": 2,
    "none": 1,
}
GCS_MOTOR = {
    "obeys_commands": 6,
    "localizing": 5,
    "localising": 5,
    "normal_flexion": 4,
    "abnormal_flexion": 3,
    "extension": 2,
    "none": 1,
}


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def _canonical_component(value, mapping, name):
    if isinstance(value, str):
        key = value.strip().lower()
        if key in {"nt", "not_testable", "untestable"}:
            return None
        if key not in mapping:
            raise ValueError(f"{name}: unsupported category {value!r}")
        return mapping[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name}: use a canonical category or integer component score")
    allowed = set(mapping.values())
    if value not in allowed:
        raise ValueError(f"{name}: invalid component score {value}")
    return value


def calculate_gcs(data):
    missing = [k for k in ("eye", "verbal", "motor") if data.get(k) is None]
    if missing:
        raise ValueError("missing GCS components: " + ", ".join(missing))

    eye = _canonical_component(data["eye"], GCS_EYE, "eye")
    verbal = _canonical_component(data["verbal"], GCS_VERBAL, "verbal")
    motor = _canonical_component(data["motor"], GCS_MOTOR, "motor")
    components = {"E": eye, "V": verbal, "M": motor}

    if any(v is None for v in components.values()):
        return {
            "id": "gcs",
            "status": "not_testable_component_present",
            "components": components,
            "total": None,
            "display": "Record components individually; do not impute a total when a component is not testable.",
            "source": SOURCES["gcs"],
        }

    total = eye + verbal + motor
    if total >= 13:
        head_injury_severity = "mild_13_15"
    elif total >= 9:
        head_injury_severity = "moderate_9_12"
    else:
        head_injury_severity = "severe_below_9"

    return {
        "id": "gcs",
        "status": "complete",
        "components": components,
        "total": total,
        "head_injury_severity_band": head_injury_severity,
        "display": f"E{eye} V{verbal} M{motor} = {total}",
        "source": SOURCES["gcs"],
    }


def calculate_nihss(data):
    items = data.get("items")
    if not isinstance(items, dict):
        raise ValueError("NIHSS requires an items object with all 15 item scores")

    missing = [item for item in NIHSS_ITEM_MAX if item not in items]
    extra = [item for item in items if item not in NIHSS_ITEM_MAX]
    if missing:
        raise ValueError("missing NIHSS items: " + ", ".join(missing))
    if extra:
        raise ValueError("unknown NIHSS items: " + ", ".join(extra))

    normalized = {}
    untestable = []
    for item, maximum in NIHSS_ITEM_MAX.items():
        value = items[item]
        if isinstance(value, str) and value.strip().upper() == "UN":
            normalized[item] = "UN"
            untestable.append(item)
            continue
        if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > maximum:
            raise ValueError(f"{item}: expected integer 0-{maximum} or UN")
        normalized[item] = value

    if untestable:
        return {
            "id": "nihss",
            "status": "untestable_item_present",
            "items": normalized,
            "untestable_items": untestable,
            "total": None,
            "display": "NIHSS contains UN item(s); preserve item-level result and do not invent a total.",
            "source": SOURCES["nihss"],
        }

    total = sum(normalized.values())
    return {
        "id": "nihss",
        "status": "complete",
        "items": normalized,
        "total": total,
        "range": [0, 42],
        "interpretation": "Higher total indicates greater measured neurological deficit; treatment decisions must not be based on NIHSS alone.",
        "source": SOURCES["nihss"],
    }


def _news2_rr(rr):
    rr = _finite_number(rr, "respiratory_rate")
    if rr <= 8:
        return 3
    if rr <= 11:
        return 1
    if rr <= 20:
        return 0
    if rr <= 24:
        return 2
    return 3


def _news2_spo2_scale1(spo2):
    spo2 = _finite_number(spo2, "spo2_percent")
    if not 0 <= spo2 <= 100:
        raise ValueError("spo2_percent must be 0-100")
    if spo2 <= 91:
        return 3
    if spo2 <= 93:
        return 2
    if spo2 <= 95:
        return 1
    return 0


def _news2_spo2_scale2(spo2, supplemental_oxygen):
    spo2 = _finite_number(spo2, "spo2_percent")
    if not 0 <= spo2 <= 100:
        raise ValueError("spo2_percent must be 0-100")
    if spo2 <= 83:
        return 3
    if spo2 <= 85:
        return 2
    if spo2 <= 87:
        return 1
    if spo2 <= 92:
        return 0
    if not supplemental_oxygen:
        return 0
    if spo2 <= 94:
        return 1
    if spo2 <= 96:
        return 2
    return 3


def _news2_sbp(sbp):
    sbp = _finite_number(sbp, "systolic_bp_mmHg")
    if sbp <= 90:
        return 3
    if sbp <= 100:
        return 2
    if sbp <= 110:
        return 1
    if sbp <= 219:
        return 0
    return 3


def _news2_pulse(pulse):
    pulse = _finite_number(pulse, "pulse_bpm")
    if pulse <= 40:
        return 3
    if pulse <= 50:
        return 1
    if pulse <= 90:
        return 0
    if pulse <= 110:
        return 1
    if pulse <= 130:
        return 2
    return 3


def _news2_temperature(temp):
    temp = _finite_number(temp, "temperature_c")
    if temp <= 35.0:
        return 3
    if temp <= 36.0:
        return 1
    if temp <= 38.0:
        return 0
    if temp <= 39.0:
        return 1
    return 2


def calculate_news2(data):
    required = (
        "respiratory_rate", "spo2_percent", "supplemental_oxygen",
        "systolic_bp_mmHg", "pulse_bpm", "consciousness", "temperature_c",
    )
    missing = [k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing NEWS2 inputs: " + ", ".join(missing))
    if not isinstance(data["supplemental_oxygen"], bool):
        raise ValueError("supplemental_oxygen must be boolean")

    scale = int(data.get("spo2_scale", 1))
    if scale not in (1, 2):
        raise ValueError("spo2_scale must be 1 or 2")
    if scale == 2 and data.get("scale2_authorized_hypercapnic_failure") is not True:
        raise ValueError(
            "NEWS2 SpO2 Scale 2 requires explicit clinician authorization for confirmed hypercapnic respiratory failure"
        )

    consciousness = str(data["consciousness"]).strip().lower()
    if consciousness in {"alert", "a"}:
        consciousness_score = 0
    elif consciousness in {"new_confusion", "confusion", "c", "voice", "v", "pain", "p", "unresponsive", "u"}:
        consciousness_score = 3
    else:
        raise ValueError("consciousness must be alert or new_confusion/C/V/P/U")

    components = {
        "respiratory_rate": _news2_rr(data["respiratory_rate"]),
        "spo2": (
            _news2_spo2_scale1(data["spo2_percent"])
            if scale == 1
            else _news2_spo2_scale2(data["spo2_percent"], data["supplemental_oxygen"])
        ),
        "supplemental_oxygen": 2 if data["supplemental_oxygen"] else 0,
        "systolic_bp": _news2_sbp(data["systolic_bp_mmHg"]),
        "pulse": _news2_pulse(data["pulse_bpm"]),
        "consciousness": consciousness_score,
        "temperature": _news2_temperature(data["temperature_c"]),
    }
    total = sum(components.values())
    any_single_3 = any(v == 3 for v in components.values())

    if total >= 7:
        trigger = "high_7_or_more"
    elif total >= 5:
        trigger = "medium_5_6"
    elif any_single_3:
        trigger = "low_medium_single_parameter_3"
    else:
        trigger = "low_0_4"

    return {
        "id": "news2",
        "status": "complete",
        "spo2_scale": scale,
        "components": components,
        "total": total,
        "single_parameter_score_3": any_single_3,
        "trigger_band": trigger,
        "warning": "NEWS2 supports detection of deterioration; it does not diagnose sepsis and must not delay clinical escalation.",
        "source": SOURCES["news2"],
    }


def _sofa_resp(pf, respiratory_support):
    pf = _finite_number(pf, "pao2_fio2_mmHg")
    if pf >= 400:
        return 0
    if pf >= 300:
        return 1
    if pf >= 200:
        return 2
    if respiratory_support and pf < 100:
        return 4
    if respiratory_support and pf < 200:
        return 3
    return 2


def _sofa_platelets(platelets):
    p = _finite_number(platelets, "platelets_10e3_uL")
    if p >= 150:
        return 0
    if p >= 100:
        return 1
    if p >= 50:
        return 2
    if p >= 20:
        return 3
    return 4


def _sofa_bilirubin(bilirubin):
    b = _finite_number(bilirubin, "bilirubin_mg_dL")
    if b < 1.2:
        return 0
    if b < 2.0:
        return 1
    if b < 6.0:
        return 2
    if b < 12.0:
        return 3
    return 4


def _sofa_cns(gcs):
    g = int(_finite_number(gcs, "gcs"))
    if g < 3 or g > 15:
        raise ValueError("gcs must be 3-15")
    if g == 15:
        return 0
    if g >= 13:
        return 1
    if g >= 10:
        return 2
    if g >= 6:
        return 3
    return 4


def _sofa_renal(creatinine, urine_output):
    cr = _finite_number(creatinine, "creatinine_mg_dL")
    if cr < 1.2:
        cr_score = 0
    elif cr < 2.0:
        cr_score = 1
    elif cr < 3.5:
        cr_score = 2
    elif cr < 5.0:
        cr_score = 3
    else:
        cr_score = 4

    urine_score = 0
    if urine_output is not None:
        uo = _finite_number(urine_output, "urine_output_mL_day")
        if uo < 200:
            urine_score = 4
        elif uo < 500:
            urine_score = 3
    return max(cr_score, urine_score)


def _sofa_cardio(map_mmHg, vasoactive):
    if not isinstance(vasoactive, dict):
        raise ValueError("vasoactive_mcg_kg_min object required")
    required = ("dopamine", "epinephrine", "norepinephrine")
    missing = [k for k in required if vasoactive.get(k) is None]
    if missing:
        raise ValueError("missing SOFA vasoactive doses: " + ", ".join(missing))
    doses = {k: _finite_number(vasoactive[k], k) for k in required}
    if any(v < 0 for v in doses.values()):
        raise ValueError("vasoactive doses cannot be negative")
    dobutamine = vasoactive.get("dobutamine_any_dose")
    if not isinstance(dobutamine, bool):
        raise ValueError("dobutamine_any_dose must be boolean")

    dopamine = doses["dopamine"]
    epi = doses["epinephrine"]
    norepi = doses["norepinephrine"]

    if dopamine > 15 or epi > 0.1 or norepi > 0.1:
        return 4
    if dopamine > 5 or epi > 0 or norepi > 0:
        return 3
    if dopamine > 0 or dobutamine:
        return 2

    map_value = _finite_number(map_mmHg, "map_mmHg")
    return 0 if map_value >= 70 else 1


def calculate_sofa1(data):
    required = (
        "pao2_fio2_mmHg", "respiratory_support", "platelets_10e3_uL",
        "bilirubin_mg_dL", "map_mmHg", "vasoactive_mcg_kg_min",
        "gcs", "creatinine_mg_dL",
    )
    missing = [k for k in required if data.get(k) is None]
    if missing:
        raise ValueError("missing SOFA-1 inputs: " + ", ".join(missing))
    if not isinstance(data["respiratory_support"], bool):
        raise ValueError("respiratory_support must be boolean")

    components = {
        "respiration": _sofa_resp(data["pao2_fio2_mmHg"], data["respiratory_support"]),
        "coagulation": _sofa_platelets(data["platelets_10e3_uL"]),
        "liver": _sofa_bilirubin(data["bilirubin_mg_dL"]),
        "cardiovascular": _sofa_cardio(data["map_mmHg"], data["vasoactive_mcg_kg_min"]),
        "cns": _sofa_cns(data["gcs"]),
        "renal": _sofa_renal(data["creatinine_mg_dL"], data.get("urine_output_mL_day")),
    }
    total = sum(components.values())
    baseline = data.get("baseline_sofa")
    delta = None
    if baseline is not None:
        baseline = int(_finite_number(baseline, "baseline_sofa"))
        if baseline < 0 or baseline > 24:
            raise ValueError("baseline_sofa must be 0-24")
        delta = total - baseline

    return {
        "id": "sofa",
        "version": "SOFA-1 / Sepsis-3 classic",
        "status": "complete",
        "components": components,
        "total": total,
        "baseline_sofa": baseline,
        "delta_sofa": delta,
        "sepsis3_organ_dysfunction_signal": (delta >= 2) if delta is not None else None,
        "warning": "SOFA characterizes organ dysfunction and is not a stand-alone management rule. Do not mix SOFA-1 thresholds with SOFA-2.",
        "source": SOURCES["sofa"],
    }
