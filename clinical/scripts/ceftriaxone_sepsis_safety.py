"""Fail-closed eligibility for one source-specific ceftriaxone sepsis regimen.

This guard does not choose another indication, dose, route or companion drug.
Passing it is not clinical approval. No date of birth is returned or logged.
"""

from calendar import monthrange
from copy import deepcopy
from datetime import date
import re

from pediatric_numbers import finite_number


TARGET_ENTRY_ID = "sepsis-community-ceftriaxone"
DOSE_GUARD_POLICY = "ceftriaxone-sepsis-under16-v1"
POPULATION = {
    "minimum_age_days": 28,
    "maximum_age_years_exclusive": 16,
    "maximum_weight_kg_exclusive": 50,
}


class CeftriaxoneSafetyError(ValueError):
    """A stable reason code plus an explanation; never a dose fallback."""

    def __init__(self, code, explanation):
        self.code = code
        self.explanation = explanation
        super().__init__(f"{code}: {explanation}")


def _stop(code, explanation):
    raise CeftriaxoneSafetyError(code, explanation)


def _required_bool(context, key, code="CONTEXT_REVIEW_REQUIRED"):
    value = context.get(key)
    if type(value) is not bool:
        _stop(code, f"{key} requires an explicit true or false value.")
    return value


def _iso_date(context, key):
    value = context.get(key)
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        _stop("AGE_CONTEXT_REQUIRED", f"{key} must be an explicit YYYY-MM-DD date.")
    try:
        return date.fromisoformat(value)
    except ValueError:
        _stop("INVALID_AGE_CONTEXT", f"{key} is not a valid calendar date.")


def _add_calendar_months(value, months):
    month_index = value.year * 12 + value.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    if year > date.max.year:
        _stop("INVALID_AGE_CONTEXT", "The age boundary exceeds the supported calendar.")
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def _validate_policy(item):
    if item.get("id") != TARGET_ENTRY_ID or item.get("dose_guard_policy") != DOSE_GUARD_POLICY:
        _stop("DOSE_GUARD_POLICY_MISMATCH", "The source-specific dose guard is missing or altered.")
    population = item.get("population")
    if not isinstance(population, dict) or any(
        isinstance(population.get(key), bool) or population.get(key) != expected
        for key, expected in POPULATION.items()
    ):
        _stop("DOSE_GUARD_POLICY_MISMATCH", "The verified population boundaries are missing or altered.")
    # Reject a custom registry that retains the policy name but changes its regimen.
    fixed_fields = {
        "drug": "ceftriaxone", "dose_per_kg": 80, "dose_unit": "mg/kg",
        "max_dose": 4000, "max_dose_unit": "mg", "route": "IV",
        "frequency": "once daily", "dose_output_unit": "mg",
    }
    if any(item.get(key) != value for key, value in fixed_fields.items()):
        _stop("DOSE_GUARD_POLICY_MISMATCH", "The registry differs from the verified IV sepsis regimen.")
    if item.get("source_concentration_per_ml") is not None:
        _stop("DOSE_GUARD_POLICY_MISMATCH", "This regimen has no verified preparation concentration and cannot generate an administration volume.")
    for key in ("source_refs", "safety_notes"):
        if not isinstance(item.get(key), list) or not item[key]:
            _stop("DOSE_GUARD_POLICY_MISMATCH", f"{key} must preserve the documented source and safety information.")


def validate_context(item, weight_kg, context):
    """Validate before dose arithmetic; return only derived age and source metadata.

    The caller validates a positive finite weight before invoking this function.
    Dates are calendar dates; month-end anniversaries use the last valid day.
    """
    _validate_policy(item)
    if not isinstance(context, dict):
        _stop("CONTEXT_REQUIRED", "An explicit clinical context JSON object is required for this regimen.")
    birth = _iso_date(context, "birth_date")
    assessed = _iso_date(context, "assessment_date")
    if assessed < birth:
        _stop("INVALID_AGE_CONTEXT", "Assessment cannot precede birth.")
    age_days = (assessed - birth).days
    if age_days < 28 or assessed >= _add_calendar_months(birth, 16 * 12):
        _stop("OUTSIDE_VERIFIED_AGE_SCOPE", "This regimen requires age at least 28 days and below 16 years.")
    if weight_kg >= 50:
        _stop("ADULT_INDICATION_REGIMEN_REQUIRED", "At 50 kg or more, select and review the adult indication-specific regimen; no adult dose is inferred.")

    for key, expected in (
        ("community_acquired", True),
        ("known_infection_focus", False),
        ("ceftriaxone_resistance_history", False),
    ):
        if _required_bool(context, key, "SEPSIS_CONTEXT_REVIEW_REQUIRED") is not expected:
            _stop("SEPSIS_CONTEXT_REVIEW_REQUIRED", f"{key} requires a different or professionally reviewed infection pathway.")

    if "route" in context and context["route"] != "IV":
        _stop("ROUTE_NOT_SUPPORTED", "This sepsis contract is IV only; it does not calculate an IM regimen.")
    if _required_bool(context, "diluent_contains_lidocaine"):
        _stop("IV_LIDOCAINE_CONTRAINDICATED", "A lidocaine-containing ceftriaxone preparation must not be administered IV.")
    if _required_bool(context, "diluent_contains_calcium"):
        _stop("IV_CALCIUM_DILUENT_CONTRAINDICATED", "Do not use a calcium-containing diluent for this IV preparation.")

    calcium = context.get("calcium_iv_mode")
    if calcium not in ("none", "planned", "sequential", "simultaneous"):
        _stop("CALCIUM_CONTEXT_REQUIRED", "calcium_iv_mode must be none, planned, sequential or simultaneous.")
    if age_days <= 28 and calcium != "none":
        _stop("NEONATAL_CALCIUM_CONTRAINDICATED", "At 28 days or younger, required or anticipated IV calcium excludes this ceftriaxone regimen.")
    if calcium == "sequential" and _required_bool(
        context, "calcium_line_changed_or_flushed", "CALCIUM_SEQUENTIAL_LINE_CHECK_REQUIRED"
    ) is not True:
        _stop("CALCIUM_SEQUENTIAL_LINE_CHECK_REQUIRED", "Sequential administration requires a documented changed or appropriately flushed line.")
    if calcium == "planned":
        _stop("CALCIUM_ADMINISTRATION_REVIEW_REQUIRED", "Review and document the calcium administration plan before calculating this regimen.")
    if calcium == "simultaneous":
        _stop("CALCIUM_SIMULTANEOUS_REVIEW_REQUIRED", "Simultaneous IV calcium requires a specialist product-specific decision; parenteral-nutrition exceptions cannot bypass this guard.")

    premature = _required_bool(context, "premature")
    if premature and (age_days <= 287 or "postmenstrual_age_days" in context):
        postmenstrual = context.get("postmenstrual_age_days")
        if type(postmenstrual) is not int or postmenstrual < 0:
            _stop("POSTMENSTRUAL_AGE_REQUIRED", "A nonnegative integer postmenstrual_age_days is required for this premature infant.")
        gestational_days_at_birth = postmenstrual - age_days
        if not 0 < gestational_days_at_birth < 259:
            _stop("POSTMENSTRUAL_AGE_INCONSISTENT", "Postmenstrual and chronological ages must imply a positive gestational age below 37 weeks at premature birth.")
        if postmenstrual <= 287:
            _stop("PREMATURITY_CONTRAINDICATED", "Ceftriaxone is excluded through 41 weeks of postmenstrual age.")
    if age_days <= 28 and _required_bool(context, "neonatal_bilirubin_risk"):
        _stop("NEONATAL_BILIRUBIN_CONTRAINDICATED", "Neonatal hyperbilirubinaemia, jaundice, hypoalbuminaemia or acidosis excludes this regimen.")

    organ_status = context.get("renal_hepatic_status")
    if organ_status not in (
        "no_impairment", "isolated_renal", "isolated_hepatic", "severe_combined", "unknown"
    ):
        _stop("RENAL_HEPATIC_CONTEXT_REQUIRED", "An explicit renal_hepatic_status from the supported categories is required.")
    if organ_status == "isolated_renal":
        try:
            clearance = finite_number("creatinine_clearance_ml_min", context.get("creatinine_clearance_ml_min"))
        except ValueError:
            _stop("RENAL_CONTEXT_REQUIRED", "A finite nonnegative creatinine_clearance_ml_min is required.")
        if clearance < 0:
            _stop("RENAL_CONTEXT_REQUIRED", "creatinine_clearance_ml_min cannot be negative.")
        if clearance < 10:
            _stop("RENAL_REGIMEN_REVIEW_REQUIRED", "Severe renal impairment requires regimen review; no automatic alternative dose or cap is applied.")
    elif organ_status == "isolated_hepatic":
        if context.get("hepatic_impairment_severity") not in ("mild", "moderate"):
            _stop("HEPATIC_REGIMEN_REVIEW_REQUIRED", "Hepatic severity must be reviewed; only documented mild or moderate isolated impairment is covered here.")
    elif organ_status in ("severe_combined", "unknown"):
        _stop("RENAL_HEPATIC_REGIMEN_REVIEW_REQUIRED", "Combined severe impairment or unknown organ function requires professional regimen review.")

    under_three_months = assessed < _add_calendar_months(birth, 3)
    if under_three_months and _required_bool(
        context, "listeria_coverage_planned", "LISTERIA_COVERAGE_REQUIRED"
    ) is not True:
        _stop("LISTERIA_COVERAGE_REQUIRED", "Before three calendar months, Listeria-active coverage must be explicitly planned; its dose is not calculated here.")

    age_years = assessed.year - birth.year
    if assessed < _add_calendar_months(birth, age_years * 12):
        age_years -= 1
    return {
        "age_days": age_days,
        "age_years_completed": age_years,
        "under_three_calendar_months": under_three_months,
        "population": deepcopy(item["population"]),
        "source_refs": deepcopy(item["source_refs"]),
        "safety_notes": deepcopy(item["safety_notes"]),
        "dose_guard_policy": DOSE_GUARD_POLICY,
        "clinical_status": "CLINICAL_REVIEW_REQUIRED",
        "clinical_release_status": "CLINICALLY_PENDING",
    }
