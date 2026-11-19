"""Preserve JSON number precision until explicit medication weights are checked."""
from decimal import Decimal, InvalidOperation
import json

from pediatric_numbers import MIN_PATIENT_WEIGHT_KG, MAX_PATIENT_WEIGHT_KG


_WEIGHT_PATHS = {
    '/api/acute-medications/calculate': (('inputs',), ('weight_kg',)),
    '/api/acute-medications/export': (('calculation', 'inputs'), ('weight_kg',)),
    '/api/pediatric-outpatient/calculate': (('patient',), (
        'actual_weight_kg', 'ideal_weight_kg', 'adjusted_weight_kg')),
    '/api/pediatric-outpatient/export': (('calculation', 'patient'), (
        'actual_weight_kg', 'ideal_weight_kg', 'adjusted_weight_kg')),
}


def _decimal_literal(value):
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValueError('invalid JSON numeric value') from None


def _restore_json_numbers(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: _restore_json_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_restore_json_numbers(item) for item in value]
    return value


def parse_medication_request(raw, path):
    """Keep the JSON numeric contract; do not inspect derived result weights."""
    if path not in _WEIGHT_PATHS:
        return json.loads(raw)
    payload = json.loads(raw, parse_float=_decimal_literal)
    parents, fields = _WEIGHT_PATHS[path]
    inputs = payload
    for key in parents:
        inputs = inputs.get(key) if isinstance(inputs, dict) else None
    if isinstance(inputs, dict):
        for field in fields:
            value = inputs.get(field)
            # Missing values, booleans and strings remain subject to the existing
            # active-field/required/type checks; they are never coerced here.
            if isinstance(value, Decimal) and not (
                    value.is_finite() and
                    Decimal(MIN_PATIENT_WEIGHT_KG) <= value <= Decimal(MAX_PATIENT_WEIGHT_KG)):
                raise ValueError('patient weight must be between 1 and 180 kg inclusive')
    return _restore_json_numbers(payload)
