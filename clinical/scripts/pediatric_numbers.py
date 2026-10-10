"""Shared numeric boundary for pediatric arithmetic; never coerce user types."""
import math
from functools import wraps


def finite_number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        value = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{name} must be a finite number") from None
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def positive(name, value):
    value = finite_number(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return value


def nonnegative(name, value):
    value = finite_number(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return value


def finite_tree(value, name="result"):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        finite_number(name, value)
    elif isinstance(value, dict):
        for key, item in value.items():
            finite_tree(item, f"{name}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            finite_tree(item, f"{name}[{i}]")
    return value


def finite_result(function):
    @wraps(function)
    def checked(*args, **kwargs):
        try:
            return finite_tree(function(*args, **kwargs))
        except (OverflowError, ZeroDivisionError):
            raise ValueError("calculated result must be finite; invalid arithmetic") from None
    return checked


def outpatient_inputs(patient, product=None, entry=None):
    if not isinstance(patient, dict):
        raise ValueError("patient must be an object")
    if product is not None and not isinstance(product, dict):
        raise ValueError("product must be an object")
    for field in ('actual_weight_kg', 'ideal_weight_kg', 'adjusted_weight_kg'):
        if field in patient:
            positive(field, patient[field])
    for field in ('age_months', 'egfr_mL_min'):
        if field in patient:
            nonnegative(field, patient[field])
    for gate in (entry or {}).get('minimum_patient_values', []) + (entry or {}).get('maximum_patient_values', []):
        if gate['field'] in patient:
            nonnegative(gate['field'], patient[gate['field']])
    for field in ('concentration_mg_per_ml', 'mg_per_drop', 'drops_per_ml'):
        if field in (product or {}):
            positive(field, product[field])
