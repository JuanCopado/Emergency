"""Thin API boundary for the existing pediatric outpatient calculator."""
from pediatric_catalog import build_catalog
from pediatric_outpatient_calculator import calculate, MedicationSafetyStop


def calculate_request(payload):
    if not isinstance(payload, dict):
        raise ValueError('request must be an object')
    if payload.get('source_revision') != build_catalog()['source_revision']:
        raise ValueError('Pediatric catalog changed; rebuild/reload the frontend before calculating')
    if not isinstance(payload.get('regimen_id'), str):
        raise ValueError('regimen_id must be a string')
    patient = payload.get('patient')
    if not isinstance(patient, dict):
        raise ValueError('patient must be an object')
    for field in ('allergies', 'active_medications'):
        if field in patient and (not isinstance(patient[field], list) or
                                any(not isinstance(x, (str, dict)) for x in patient[field])):
            raise ValueError(f'{field} must be a list of names or structured records')
    try:
        result = calculate(payload['regimen_id'], patient, payload.get('product'),
                           selected_dose_per_kg=payload.get('selected_dose_per_kg'),
                           selected_duration_days=payload.get('selected_duration_days'),
                           selected_volume_ml=payload.get('selected_volume_ml'))
        from pediatric_result_exporter import build_report
        return {'blocked': False, 'result': result, 'safety': result['medication_safety'],
                'export_report': build_report(payload, result)}
    except MedicationSafetyStop as exc:
        return {'blocked': True, 'safety': exc.alert_result}
