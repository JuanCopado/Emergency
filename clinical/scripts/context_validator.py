#!/usr/bin/env python3
"""Context checklist, NOT medical clearance or an autonomous prescribing gate.

CLI: echo a JSON object on stdin; choose task: general, medication,
anticoagulation-reversal, or clinical-image-interpretation.
Unknown values must remain unknown. pregnancy='not_applicable' is allowed only
when the clinician has established that it is irrelevant.
"""
import json
import math
import sys

PROFILES = {
    'general': ('age', 'symptoms', 'onset', 'vitals'),
    'medication': ('age', 'weight_kg', 'allergy', 'renal', 'hepatic', 'pregnancy',
                   'drug', 'indication', 'current_vitals', 'therapeutic_target',
                   'route'),
    'anticoagulation-reversal': ('age', 'weight_kg', 'allergy', 'renal', 'hepatic',
        'anticoagulant', 'last_dose', 'indication', 'bleeding_severity',
        'thrombotic_history', 'hit_history', 'reversal_product'),
    'clinical-image-interpretation': ('age', 'symptoms', 'onset', 'body_region',
        'laterality', 'image_available', 'image_quality', 'modality', 'source_type',
        'images_count'),
}
UNKNOWN = {'', 'unknown', 'desconocido', 'desconocida', 'no se sabe', '?', 'pending'}


def is_missing(value):
    return value is None or (isinstance(value, str) and value.strip().lower() in UNKNOWN)


def validate_inputs(age=None, weight_kg=None, renal=None, hepatic=None,
                    pregnancy=None, allergy=None, task='general', **context):
    if task not in PROFILES:
        raise ValueError(f'Unknown task profile: {task}')
    values = dict(context, age=age, weight_kg=weight_kg, renal=renal,
                  hepatic=hepatic, pregnancy=pregnancy, allergy=allergy)
    required = list(PROFILES[task])
    if task == 'anticoagulation-reversal':
        agent = str(context.get('anticoagulant', '')).strip().lower()
        if agent in {'warfarin', 'warfarina', 'acenocoumarol', 'acenocumarol', 'vka', 'avk'}:
            required.append('inr')
    missing = [field for field in required if is_missing(values.get(field))]
    invalid = []
    for field in ('age', 'weight_kg', 'inr', 'images_count'):
        value = values.get(field)
        if is_missing(value):
            continue
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or (value < 0 if field == 'age' else value <= 0)):
            invalid.append(field)
    if (not is_missing(values.get('images_count'))
            and (isinstance(values.get('images_count'), bool)
                 or not isinstance(values.get('images_count'), int))
            and 'images_count' not in invalid):
        invalid.append('images_count')
    warnings = []
    if task == 'clinical-image-interpretation':
        if values.get('image_available') is not True:
            warnings.append('Do not interpret unseen pixels; request an accessible image.')
        if str(values.get('image_quality', '')).lower() in {'poor', 'inadequate', 'non-diagnostic', 'no diagnostica'}:
            warnings.append('Image may not support a leading diagnosis; explain limitations.')
        modality = str(values.get('modality', '')).lower()
        if modality in {'xray', 'radiograph', 'radiografia', 'radiografía'}:
            for field in ('views', 'laterality_marker'):
                if is_missing(values.get(field)) and field not in missing:
                    missing.append(field)
        if modality in {'ultrasound', 'pocus', 'ecografia', 'ecografía'} and is_missing(values.get('dynamic_type')):
            warnings.append('State whether the ultrasound input is a still, cine or compression sequence.')
        if modality in {'blood-gas', 'blood gas', 'gasometry', 'gasometria', 'gasometría'}:
            for field in ('sample_type', 'oxygen_context'):
                if is_missing(values.get(field)) and field not in missing:
                    missing.append(field)
            warnings.append('Verify every displayed digit and unit before acid-base calculations; do not infer arterial PO2 from an unlabeled sample.')
    return {'task': task, 'missing_high_value_context': missing,
            'invalid_values': invalid, 'warnings': warnings,
            'checklist_complete': not missing and not invalid and not warnings,
            'clinical_clearance': False,
            'note': 'Checklist only. Verify drug-specific contraindications and doses; do not delay emergency stabilization.'}


if __name__ == '__main__':
    try:
        print(json.dumps(validate_inputs(**json.load(sys.stdin)), ensure_ascii=False))
    except (TypeError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        raise SystemExit(2)
