"""Fail-closed review of an adult IV phenytoin status loading-dose candidate.

RESEARCH/QA ONLY. This module is NOT connected to the acute medication API.
No prescription, pump rate, or product withdrawal is provided; the production
regimen remains BLOCKED.

Reference: https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults
Reference scope: phenytoin 250 mg/5 mL, NaCl 0.9% only, Galway dilution table.
Local Pharmacy adoption is reported by the project owner, but a dated signed
product-specific authorization has not been independently authenticated.
"""

from math import ceil, isfinite

PROTOCOL_URL = "https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults"
DOSE_MG_PER_KG = 20
INITIAL_LOAD_CAP_MG = 2000
MAX_ADULT_RATE_MG_MIN = 50
REFERENCE_MIN_DURATION_MIN = 40  # owner-selected local reference, not Galway mandate
PREPARATION_WINDOW_MIN = 60
ALWAYS_BLOCKED = True


def _number(x):
    return type(x) in (int, float) and isfinite(x)


def galway_minimum_nacl09_volume_ml(dose_mg):
    """Source-specific volume bracket, not a general stability authorization."""
    if not _number(dose_mg) or dose_mg <= 0:
        raise ValueError("Dose must be positive and finite")
    return 50 if dose_mg < 500 else 100 if dose_mg <= 1000 else 250


def preflight(*, weight_kg, max_rate_mg_min, age_class="adult",
              product_strength="250mg/5mL", diluent="NaCl 0.9%", bag_ml=None,
              risk_review_confirmed=False, time_since_preparation_min=0,
              pharmacy_formulary_approved=False, pharmacy_signed_approval_ref=None,
              contraindication_present=False, monitoring_ready=False,
              iv_access_ready=False, visible_precipitate=False):
    """Assess source-based *review readiness*, never create a medication order.

    For adult, phenytoin-naive initial loading only. Doses and proposed durations
    are displayed for manual review. Any dilution volume BELOW its Galway table
    bracket is rejected even if nominal concentration appears <=10 mg/mL.
    Larger volumes (including 500mL) also need separate manufacturer/pharmacy
    validation; mere saline-bag availability does not approve a mixture.
    """
    reasons = []
    if age_class != "adult":
        reasons.append("ADULT_ONLY")
    if product_strength != "250mg/5mL":
        reasons.append("PRODUCT_OUTSIDE_DOCUMENTED_GALWAY_SCOPE")
    if diluent != "NaCl 0.9%":
        reasons.append("DILUENT_MUST_BE_NACL_0_9")
    if not _number(weight_kg) or weight_kg <= 0:
        reasons.append("INVALID_WEIGHT")
    if not _number(max_rate_mg_min) or not 0 < max_rate_mg_min <= MAX_ADULT_RATE_MG_MIN:
        reasons.append("INVALID_INDIVIDUAL_RATE")
    if not _number(time_since_preparation_min) or time_since_preparation_min < 0:
        reasons.append("INVALID_PREPARATION_ELAPSED_TIME")
    if not _number(bag_ml) or bag_ml <= 0:
        reasons.append("INVALID_BAG_VOLUME")
    if contraindication_present is not False:
        reasons.append("CLINICAL_CONTRAINDICATION")
    if risk_review_confirmed is not True:
        reasons.append("CLINICAL_RATE_AND_RISK_REVIEW_REQUIRED")
    if monitoring_ready is not True:
        reasons.append("CONTINUOUS_ECG_BP_RESPIRATORY_MONITORING_REQUIRED")
    if iv_access_ready is not True:
        reasons.append("SUITABLE_IV_ACCESS_AND_FLUSH_REQUIRED")
    if visible_precipitate is not False:
        reasons.append("PRECIPITATE_OR_UNCONFIRMED_CLARITY")
    if (pharmacy_formulary_approved is not True
            or not isinstance(pharmacy_signed_approval_ref, str)
            or not pharmacy_signed_approval_ref.strip()):
        reasons.append("PHARMACY_PRODUCT_AND_PREPARATION_ATTESTATION_REQUIRED")

    if not all((_number(weight_kg) and weight_kg > 0,
                _number(max_rate_mg_min) and 0 < max_rate_mg_min <= MAX_ADULT_RATE_MG_MIN,
                _number(time_since_preparation_min) and time_since_preparation_min >= 0,
                _number(bag_ml) and bag_ml > 0)):
        return {"status": "BLOCKED", "reasons": sorted(set(reasons)),
                "source": PROTOCOL_URL, "prescription_enabled": False}

    dose_mg = min(DOSE_MG_PER_KG * weight_kg, INITIAL_LOAD_CAP_MG)
    min_bag_ml = galway_minimum_nacl09_volume_ml(dose_mg)
    if bag_ml < min_bag_ml:
        reasons.append("NACL09_VOLUME_BELOW_GALWAY_MINIMUM")
    elif bag_ml > min_bag_ml:
        reasons.append("NACL09_VOLUME_ABOVE_GALWAY_TABLE_REQUIRES_SEPARATE_VALIDATION")
    if dose_mg / bag_ml > 10:
        reasons.append("NOMINAL_CONCENTRATION_EXCEEDS_10_MG_ML")

    minimum_minutes = max(REFERENCE_MIN_DURATION_MIN, ceil(dose_mg / max_rate_mg_min))
    if minimum_minutes + time_since_preparation_min >= PREPARATION_WINDOW_MIN:
        # The strict cutoff is a conservative QA margin, not a new expiry rule.
        reasons.append("PREPARATION_60_MIN_WINDOW_NOT_SATISFIED")

    return {
        "status": "BLOCKED" if reasons else "CANDIDATE_FOR_NOMINAL_REVIEW_ONLY",
        "reasons": sorted(set(reasons)),
        "dose_mg_for_review_only": dose_mg,
        "galway_minimum_nacl09_bag_ml": min_bag_ml,
        "selected_nacl09_bag_ml": bag_ml if diluent == "NaCl 0.9%" else None,
        "minimum_duration_min_for_review_only": minimum_minutes,
        "source": PROTOCOL_URL,
        "prescription_enabled": False,
        "limitations": [
            "No drug withdrawal, true final concentration, or pump mL/h calculated",
            "Nominal bag volume does not equal verified final mixture volume",
            "No supplemental load or maintenance dosing calculated",
            "Galway guideline is not automatically the hospital product SmPC",
            "Target-commit clinical/Pharmacy sign-off and functional QA pending",
        ],
    }
