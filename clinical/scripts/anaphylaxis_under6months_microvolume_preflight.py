"""Research-only IM adrenaline microvolume check for infants <6 months.

Theoretical values are QA evidence, NOT dose recommendations or drug orders.
This code is intentionally NOT connected to acute_medication_api.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

GUIDELINE_DOSE_MG_PER_KG = Decimal('0.01')
GUIDELINE_IM_CONCENTRATION_MG_ML = Decimal('1')
CONTRACT_STATUS = 'BLOCKED'


def _number(value):
    if type(value) not in (int, float, Decimal):
        return None
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return n if n.is_finite() else None


def preflight(*, age_months, weight_kg, route='IM',
              concentration_mg_ml=1, measurement_increment_ml=None,
              prior_im_doses=0, iv_dilution_selected=False):
    """Return unrounded values for synthetic QA; never a clinical order.

    Even a nominally exact graduation or a successful arithmetic check does not
    demonstrate a syringe's delivered-volume accuracy or approved rounding.
    """
    flags = []
    age = _number(age_months)
    weight = _number(weight_kg)
    concentration = _number(concentration_mg_ml)
    if age is None or not Decimal('0') <= age < Decimal('6'):
        flags.append('AGE_OUTSIDE_CONTRACT_OR_INVALID')
    elif age < 1:
        flags.append('NEONATAL_SPECIALIST_REVIEW_REQUIRED')
    if weight is None or weight <= 0:
        flags.append('WEIGHT_MISSING_OR_INVALID_NO_AGE_DEFAULT')
    if route != 'IM':
        flags.append('WRONG_ROUTE_IM_ONLY')
    if concentration != GUIDELINE_IM_CONCENTRATION_MG_ML:
        flags.append('CONCENTRATION_MISMATCH_1MG_ML_IM_REQUIRED')
    if iv_dilution_selected is not False:
        flags.append('IV_DILUTION_FORBIDDEN_IN_IM_CONTRACT')
    if type(prior_im_doses) is not int or prior_im_doses < 0:
        flags.append('INVALID_PRIOR_IM_DOSES')
    elif prior_im_doses >= 2:
        flags.append('SPECIALIST_ESCALATION_ALERT_ONLY_NO_IV_AUTOMATION')

    response = {'status': CONTRACT_STATUS, 'prescription_enabled': False,
                'clinical_validation_complete': False,
                'device_accuracy_verified': False,
                'flags': flags,
                'limitations': ['No dose/volume order or syringe instruction',
                                'No automatic rounding or administration',
                                'No IM-to-IV conversion',
                                'Urgent care must not be delayed by software review']}
    # Do not suggest even theoretical volume for wrong route/strength/age/weight.
    if (age is None or age >= 6 or age < 0 or weight is None or weight <= 0
            or route != 'IM' or concentration != GUIDELINE_IM_CONCENTRATION_MG_ML
            or iv_dilution_selected is not False):
        return response

    # All arithmetic is exact Decimal arithmetic from the selected reference.
    theoretical_mg = weight * GUIDELINE_DOSE_MG_PER_KG
    theoretical_ml = theoretical_mg / GUIDELINE_IM_CONCENTRATION_MG_ML
    response['theoretical_mg_for_qa_only'] = str(theoretical_mg)
    response['theoretical_ml_for_qa_only'] = str(theoretical_ml)
    increment = _number(measurement_increment_ml)
    if increment is None or increment <= 0:
        flags.append('DEVICE_INCREMENT_UNKNOWN_NO_ROUNDING')
    else:
        qa_candidate = ((theoretical_ml / increment).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                        * increment)
        error_pct = (qa_candidate / theoretical_ml - 1) * 100
        response['qa_rounding_candidate_ml_NOT_FOR_ADMINISTRATION'] = str(qa_candidate)
        response['qa_rounding_relative_error_percent'] = str(error_pct.quantize(Decimal('0.001')))
        flags.append('MEASUREMENT_ACCURACY_AND_ROUNDING_POLICY_NOT_APPROVED')
    # Deliberate: NO site/device verification, no acceptable % threshold assumed.
    return response
