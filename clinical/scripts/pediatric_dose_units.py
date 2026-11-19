"""Total-dose labels after weight multiplication; no drug or dose selection."""


def total_dose_unit(reference_unit):
    """Remove only the weight denominator, retaining time/component qualifiers."""
    supported = {
        'mg/kg', 'micrograms/kg', 'mL/kg', 'g/kg', 'units/kg', 'mmol/kg',
        'mg/kg/day', 'mg/kg piperacillin component',
    }
    if not isinstance(reference_unit, str) or reference_unit not in supported:
        raise ValueError('unsupported weight-based dose unit')
    return reference_unit.replace('/kg', '', 1)
