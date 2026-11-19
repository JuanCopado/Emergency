"""Decode medication requests without ambiguous members or lossy clinical gates."""
from decimal import Decimal, InvalidOperation
import json

from acute_medication_contracts import regimens
from pediatric_numbers import MIN_PATIENT_WEIGHT_KG, MAX_PATIENT_WEIGHT_KG


_PEDIATRIC_WEIGHTS = ('actual_weight_kg', 'ideal_weight_kg', 'adjusted_weight_kg')
_MEDICATION_INPUTS = {
    '/api/acute-medications/calculate': ('inputs', ('weight_kg',)),
    '/api/acute-medications/export': ('inputs', ('weight_kg',)),
    '/api/pediatric-outpatient/calculate': ('patient', _PEDIATRIC_WEIGHTS),
    '/api/pediatric-outpatient/export': ('patient', _PEDIATRIC_WEIGHTS),
}


# The contract supplies both integer counters and numeric fields with a fixed
# integer value (for example shock_count). Keep the scope specific to each regimen.
_ACUTE_INTEGER_FIELDS = {
    row['id']: tuple(field['key'] for field in row['fields']
                     if field.get('integer') or
                     (field['kind'] == 'number' and type(field.get('expected')) is int))
    for row in regimens()
}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate medication request member')
        result[key] = value
    return result


def _check_integer_precision(calculation, inputs):
    regimen = calculation.get('regimen_id')
    if not isinstance(regimen, str):
        return
    for key in _ACUTE_INTEGER_FIELDS.get(regimen, ()):
        exact = inputs.get(key)
        if isinstance(exact, Decimal):
            converted = float(exact)
            if converted.is_integer() and exact != converted:
                raise ValueError('medication input rounded to a different integer')


def _decimal_literal(value):
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValueError('invalid JSON numeric value') from None


def _restore_json_numbers(value):
    if isinstance(value, Decimal):
        converted = float(value)
        if converted == 0 and value != 0:
            raise ValueError('nonzero medication input underflowed')
        return converted
    if isinstance(value, dict):
        return {key: _restore_json_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_restore_json_numbers(item) for item in value]
    return value


def parse_medication_request(raw, path):
    """Keep the JSON numeric contract; do not inspect derived result weights."""
    if path not in _MEDICATION_INPUTS:
        return json.loads(raw)
    payload = json.loads(raw, parse_float=_decimal_literal, object_pairs_hook=_unique_object)
    container, fields = _MEDICATION_INPUTS[path]
    calculation = payload.get('calculation') if path.endswith('/export') and isinstance(payload, dict) else payload
    inputs = calculation.get(container) if isinstance(calculation, dict) else None
    if isinstance(inputs, dict):
        if container == 'inputs':
            _check_integer_precision(calculation, inputs)
        for field in fields:
            value = inputs.get(field)
            # Missing values, booleans and strings remain subject to the existing
            # active-field/required/type checks; they are never coerced here.
            if isinstance(value, Decimal) and not (
                    value.is_finite() and
                    Decimal(MIN_PATIENT_WEIGHT_KG) <= value <= Decimal(MAX_PATIENT_WEIGHT_KG)):
                raise ValueError('patient weight must be between 1 and 180 kg inclusive')
    return _restore_json_numbers(payload)
