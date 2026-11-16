"""I01 clinical-design preflight for IV phenytoin in adult status epilepticus.

RESEARCH/QA ONLY. Not connected to acute_medication_api, not a prescription,
not validated for clinical use, and MUST NOT clear its BLOCKED guard.

Protocol reference (accessed 2026-11-15):
  https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults
Source/formulation scope: 250 mg/5 mL, 50 mg/mL (not unspecified 100 mg/2 mL).
Local pharmacy validation: owner-reported, no independently verifiable signed record.
"""

from math import ceil, isfinite


PROTOCOL = "Medinfo Galway — Phenytoin Intravenous for Adults"
PROTOCOL_URL = "https://www.medinfogalway.ie/ivguides/phenytoin-intravenous-adults"
ALWAYS_BLOCKED = True


def preflight(*, weight_kg, max_rate_mg_min, age_class="adult",
              product_strength="250mg/5mL", bag_ml=None, risk_review_confirmed=False,
              time_since_preparation_min=0, pharmacy_formulary_approved=False,
              pharmacy_signed_approval_ref=None, contraindication_present=False,
              monitoring_ready=False, iv_access_ready=False):
    """Assess *whether* an adult load is eligible for human review, never prescribe.

    A successful assessment means arithmetic constraints are consistent, NOT that a
    clinical medication order can be generated. No mL/h or product withdrawal
    is returned. All clinical execution remains BLOCKED in the main API.
    """
    reasons = []
    def number(value):
        return type(value) in (int, float) and isfinite(value)

    if age_class != "adult":
        reasons.append("ADULT_ONLY")
    if product_strength != "250mg/5mL":
        reasons.append("PRODUCT_OUTSIDE_DOCUMENTED_GALWAY_SCOPE")
    if not number(weight_kg) or weight_kg <= 0:
        reasons.append("INVALID_WEIGHT")
    if not number(max_rate_mg_min) or not 0 < max_rate_mg_min <= 50:
        reasons.append("INVALID_INDIVIDUAL_RATE")
    if not number(time_since_preparation_min) or time_since_preparation_min < 0:
        reasons.append("INVALID_PREPARATION_ELAPSED_TIME")
    if contraindication_present is not False:
        reasons.append("CLINICAL_CONTRAINDICATION")
    if risk_review_confirmed is not True:
        reasons.append("CLINICAL_RATE_AND_RISK_REVIEW_REQUIRED")
    if monitoring_ready is not True:
        reasons.append("CONTINUOUS_ECG_BP_RESPIRATORY_MONITORING_REQUIRED")
    if iv_access_ready is not True:
        reasons.append("SUITABLE_IV_ACCESS_AND_FLUSH_REQUIRED")
    if pharmacy_formulary_approved is not True or not isinstance(pharmacy_signed_approval_ref, str) or not pharmacy_signed_approval_ref.strip():
        reasons.append("PHARMACY_PRODUCT_AND_PREPARATION_ATTESTATION_REQUIRED")

    if not all((number(weight_kg) and weight_kg > 0,
                number(max_rate_mg_min) and 0 < max_rate_mg_min <= 50,
                number(time_since_preparation_min) and time_since_preparation_min >= 0)):
        return {"status":"BLOCKED", "reasons":sorted(set(reasons)),
                "source":PROTOCOL_URL, "prescription_enabled":False}

    dose_mg = min(20 * weight_kg, 2000)
    expected_bag_ml = 50 if dose_mg < 500 else 100 if dose_mg <= 1000 else 250
    if bag_ml != expected_bag_ml:
        reasons.append("DILUENT_BAG_NOT_IN_SELECTED_PROTOCOL_TABLE")
    min_duration_min = max(40, ceil(dose_mg / max_rate_mg_min))
    if min_duration_min + time_since_preparation_min >= 60:
        # Fail conservatively at the 60-minute boundary to avoid claiming
        # immediate start and guaranteed completion, particularly after delays.
        reasons.append("PREPARATION_60_MIN_WINDOW_NOT_SATISFIED")
    # Do not compute apparent final concentration or pump speed from labeled bag
    # volume: actual final volume, additive displacement, overfill, and product
    # compatibility are not sufficiently verified.
    return {
        "status":"BLOCKED" if reasons else "CANDIDATE_FOR_NOMINAL_REVIEW_ONLY",
        "reasons":sorted(set(reasons)),
        "dose_mg_for_review_only":dose_mg,
        "expected_nacl09_bag_ml":expected_bag_ml,
        "minimum_duration_min_for_review_only":min_duration_min,
        "source":PROTOCOL_URL,
        "prescription_enabled":False,
        "limitations":["No mL/h, order, or drug withdrawal produced",
                       "No additional load or maintenance generated",
                       "Confirm actual final volume, formulation, filter and stability at use",
                       "Pharmacy/clinical sign-off and target-commit functional QA required"],
    }
