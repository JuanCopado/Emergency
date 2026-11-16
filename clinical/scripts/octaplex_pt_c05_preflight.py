"""C05 Octaplex Portuguese-RCM reference reconciler — QA ONLY.

Records differences between Portuguese Octapharma RCM (08/2020) and
owner-reported dose bands. Not connected to acute_medication_api.
It deliberately NEVER returns a dose recommendation or enables an order.
The dated 2020 document is not independently proven current for local lots.
"""
from decimal import Decimal, InvalidOperation

RCM_PT_URL = "https://www.octapharma.pt/api/download/x/291a94e4c6/rcm-octaplex.pdf"
PT_REVISION = "2020-08"
CONTRACT = "reversal-vka-pcc"
CONTRACT_STATUS = "BLOCKED"
FIX_IU_PER_ML = Decimal("25")
MAX_PT_SINGLE_DOSE_IU = Decimal("3000")
PRESENTATIONS = {500: 20, 1000: 40}
# RCM PT: 0.9-1.3, 1.3-1.6, 1.6-1.9, >1.9 mL/kg.
PT_BANDS_ML_KG = (
    (Decimal("2"), Decimal("2.5"), Decimal("0.9"), Decimal("1.3")),
    (Decimal("2.5"), Decimal("3"), Decimal("1.3"), Decimal("1.6")),
    (Decimal("3"), Decimal("3.5"), Decimal("1.6"), Decimal("1.9")),
    (Decimal("3.5"), None, Decimal("1.9"), None),
)
OWNER_BANDS_IU_KG = (
    (Decimal("25"), Decimal("32.5")),
    (Decimal("32.5"), Decimal("40")),
    (Decimal("40"), Decimal("47.5")),
    (Decimal("47.5"), Decimal("50")),
)


def _num(x):
    if type(x) not in (int, float, Decimal):
        return None
    try:
        v = Decimal(str(x))
        return v if v.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def source_band_differences():
    """Static documentary reconciliation: no dose is calculated."""
    differences = []
    for i, (_, _, ml_low, ml_high) in enumerate(PT_BANDS_ML_KG):
        rcm_lower = ml_low * FIX_IU_PER_ML
        rcm_upper = None if ml_high is None else ml_high * FIX_IU_PER_ML
        local_lower, local_upper = OWNER_BANDS_IU_KG[i]
        if rcm_lower != local_lower:
            differences.append({
                "band": i+1, "type": "LOWER_BOUND_DIFFERENCE",
                "rcm_iu_kg": str(rcm_lower), "owner_iu_kg": str(local_lower),
            })
        if rcm_upper != local_upper:
            differences.append({
                "band": i+1, "type": "UPPER_BOUND_DIFFERENCE",
                "rcm_iu_kg": None if rcm_upper is None else str(rcm_upper),
                "owner_iu_kg": str(local_upper),
            })
    return differences


def review_input(*, inr=None, presentation_iu=None, proposed_total_iu=None,
                 infusion_stage="initial", proposed_rate_ml_min=None,
                 complication=False, source_revision=PT_REVISION,
                 exact_product_verified=False, clinical_review_signed=False):
    """Fail-closed test helper, never a prescription or pump program.

    No patient weight, INR-guided exact dose or individual vial count is returned.
    All input is synthetic QA. Values only screen for source consistency.
    """
    flags = ["NOT_INTEGRATED_NO_PATIENT_ORDER"]
    n_inr = _num(inr)
    n_dose = _num(proposed_total_iu)
    n_rate = _num(proposed_rate_ml_min)
    if n_inr is None or n_inr <= 0:
        flags.append("INR_MISSING_OR_INVALID")
    elif n_inr < 2:
        flags.append("GENERAL_PT_2020_INR_TABLE_NOT_APPLICABLE")
    elif n_inr in (Decimal("2.5"), Decimal("3"), Decimal("3.5")):
        flags.append("INR_BOUNDARY_RULE_REQUIRES_SIGNOFF")
    if presentation_iu not in PRESENTATIONS or type(presentation_iu) is not int:
        flags.append("PRESENTATION_UNKNOWN_OR_INVALID")
    if n_dose is None or n_dose <= 0:
        flags.append("TOTAL_IU_MISSING_OR_INVALID")
    elif n_dose > MAX_PT_SINGLE_DOSE_IU:
        flags.append("EXCEEDS_PT_2020_SINGLE_DOSE_3000_IU")
    if infusion_stage not in ("initial", "after_initial"):
        flags.append("UNSUPPORTED_INFUSION_STAGE")
    if n_rate is None or n_rate <= 0:
        flags.append("INFUSION_RATE_MISSING_OR_INVALID")
    elif infusion_stage == "initial" and n_rate != Decimal("1"):
        flags.append("INITIAL_RATE_MUST_BE_1_ML_MIN_PER_PT_2020")
    elif infusion_stage == "after_initial" and not Decimal("2") <= n_rate <= Decimal("3"):
        flags.append("POST_INITIAL_RATE_OUTSIDE_2_TO_3_ML_MIN")
    if complication is not False:
        flags.append("COMPLICATION_REQUIRES_STOP_AND_HUMAN_REVIEW")
    if source_revision != PT_REVISION:
        flags.append("SOURCE_REVISION_CHANGED_OR_UNKNOWN")
    if exact_product_verified is not True:
        flags.append("PORTUGUESE_PRODUCT_AND_STOCK_VERIFICATION_REQUIRED")
    if clinical_review_signed is not True:
        flags.append("CLINICAL_SOURCE_SELECTION_AND_LOCAL_RANGES_NOT_SIGNED")
    if source_band_differences():
        flags.append("OWNER_BANDS_DIFFER_FROM_PT_2020_RCM")
    return {
        "contract_id": CONTRACT,
        "status": CONTRACT_STATUS,
        "prescription_enabled": False,
        "no_release": True,
        "flags": sorted(set(flags)),
        "product_source": RCM_PT_URL,
        "rcm_revision_for_comparison_only": PT_REVISION,
        "source_band_differences": source_band_differences(),
        "notes": [
            "No INR-to-dose selection, vial rounding, pump rate or order output",
            "No automatic merging of UK and Portuguese SmPC tables",
            "Vitamin K and intracerebral bleeding require separate pathway review",
            "Local Pharmacy must verify current product RCM and source applicability",
        ],
    }
