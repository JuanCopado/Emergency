"""Source-bound calculations and faithful exports for acute medication workflows."""
import base64
import hashlib
import json
import math
import tempfile
from acid_base_hyperglycemia import calculate as hyperglycemia_calculate
from copy import deepcopy
from pathlib import Path

from acute_medication_contracts import regimens
from clinical_note_exporter import export_sections_pdf, export_sections_docx
from pediatric_numbers import finite_tree

ROOT = Path(__file__).resolve().parents[1]


def _section(bundle, module):
    content = (ROOT / 'modules' / bundle).read_text(encoding='utf-8')
    preamble = content.split('\n## ', 1)[0]
    marker = '\n## ' + module + '\n'
    if marker not in content:
        raise ValueError('Canonical module missing: ' + module)
    body = content.split(marker, 1)[1].split('\n## ', 1)[0].strip()
    return preamble, body


def catalog():
    evidence = json.loads((ROOT / 'references/evidence-registry.json').read_text(encoding='utf-8'))['modules']
    localization = json.loads((ROOT / 'qa/localization-portugal-azores.json').read_text(encoding='utf-8'))['items']
    rows = []
    for row in regimens():
        preamble, body = _section(row['bundle'], row['module'])
        for anchor in row['anchors']:
            if anchor not in body:
                raise ValueError('Canonical source changed; reconcile contract: ' + row['id'])
        local = next((x for x in localization if x['drug'] == row.get('localization_drug')), None)
        if row.get('product_anchor') and (local is None or row['product_anchor'] not in local['product_strength']):
            raise ValueError('Canonical product reference changed; reconcile contract: ' + row['id'])
        rows.append({**row, 'source': {'module': row['module'], 'path': 'clinical/modules/' + row['bundle'],
                                    'preamble': preamble, 'body': body, 'evidence': evidence[row['module']], 'localization': local}})
    serialized = json.dumps(rows, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
    revision = hashlib.sha256(serialized + Path(__file__).read_bytes()).hexdigest()
    return {'source_revision': revision, 'clinical_status': 'CLINICALLY_PENDING', 'regimens': rows}


def _alert(code, message):
    return {'severity': 'STOP', 'code': code, 'message': message}


def _validate(row, inputs):
    if not isinstance(inputs, dict):
        raise ValueError('inputs must be an object')
    unknown = set(inputs) - {f['key'] for f in row['fields']}
    if unknown:
        raise ValueError('Unsupported inputs: ' + ', '.join(sorted(unknown)))
    alerts = []
    for f in row['fields']:
        key, kind = f['key'], f['kind']
        value = inputs.get(key)
        invalid = value is None
        if kind == 'boolean':
            invalid |= type(value) is not bool
        elif kind == 'number':
            invalid |= type(value) not in (int, float) or not math.isfinite(value)
            if not invalid:
                invalid |= f.get('positive', False) and value <= 0
                invalid |= 'minimum' in f and value < f['minimum']
                invalid |= 'maximum' in f and value > f['maximum']
                invalid |= 'exclusive_minimum' in f and value <= f['exclusive_minimum']
                invalid |= 'exclusive_maximum' in f and value >= f['exclusive_maximum']
                invalid |= f.get('integer', False) and value != int(value)
        elif kind == 'choice':
            invalid |= not isinstance(value, str) or value not in f['options']
        if 'expected' in f:
            invalid |= value != f['expected']
        if invalid:
            rule = ('; valor requerido: ' + str(f['expected'])) if 'expected' in f else ''
            alerts.append(_alert(key, 'Revisar ' + f['label'] + rule + '. No se cumple el contrato de esta pauta.'))
    if not alerts and row.get('sodium_correction'):
        ceiling = 8 if inputs['high_ods_risk'] or inputs['correction_window'] == 'subsequent24' else 10
        if inputs['sodium_current_mmol_l'] - inputs['sodium_start_mmol_l'] >= ceiling:
            alerts.append(_alert('sodium_correction', 'Límite de corrección alcanzado: no calcular otro bolo; revisión urgente de trayectoria y plan de parada/relowering.'))
    if row.get('block_reason'):
        alerts.append(_alert('CLINICAL_REVIEW_REQUIRED', row['block_reason']))
    if not alerts and row['model'] == 'adrenaline_im' and inputs['prior_im_doses'] == 1 and inputs['elapsed_min'] < 5:
        alerts.append(_alert('repeat_interval', 'Reevaluar; no se cumple el intervalo de 5 min de esta pauta IM.'))
    return alerts


def _calculate(row, inputs):
    dose = row['dose']
    pump = None
    components = row.get('components')
    if row['model'] == 'weight_volume':
        dose *= inputs['weight_kg']
    if row['model'] == 'weight':
        coefficient = inputs[row['coefficient_field']] if row.get('coefficient_field') else row['dose']
        dose = min(coefficient * inputs['weight_kg'], row['maximum']['value'])
    if row['model'] == 'andexanet':
        high = inputs['last_dose_hours'] < 8 and inputs['last_dose_mg'] > row['threshold_mg']
        dose, rate = (800, 8) if high else (400, 4)
        components = {'bolus_mg': dose, 'infusion_mg_min': rate, 'infusion_duration_min': 120, 'infusion_total_mg': rate * 120}
    if row['model'] == 'ufh':
        dose = min(inputs['recent_ufh_units'] / 100, row['maximum']['value'])
    if row['model'] == 'enoxaparin':
        dose *= inputs['enoxaparin_mg']
    if row['model'] == 'insulin':
        reference = hyperglycemia_calculate({'weight_kg': inputs['weight_kg'],
            'insulin_concentration_units_ml': inputs['concentration']})['insulin_infusion_reference']
        dose = reference[row['insulin_key'] + '_units_h']
        pump = reference[row['insulin_key'] + '_ml_h']
    duration = row.get('duration_min', inputs.get('duration_min'))
    concentration = row.get('concentration')
    withdrawal = dose / concentration['value'] if concentration and concentration['role'] == 'stock' else None
    return {'indication': row['label'], 'drug': row['drug'], 'route': row['route'],
            'dose': dose, 'dose_unit': row['dose_unit'], 'concentration': concentration, 'components': components,
            'withdrawal_ml': withdrawal, 'administration_volume_ml': dose if row['model'] in ('volume', 'weight_volume') else dose / 1000 / concentration['value'] if row['model'] == 'adrenaline_im' else None, 'pump_ml_h': pump,
            'duration_min': duration, 'amount_per_hour': dose * 60 / duration if duration else None,
            'amount_per_hour_unit': row['dose_unit'] + '/h' if duration else None,
            'correction_ceiling_mmol_l': (8 if inputs['high_ods_risk'] or inputs['correction_window'] == 'subsequent24' else 10) if row.get('sodium_correction') else None,
            'maximum': row['maximum'], 'preparation': row['preparation'],
            'compatibility': row['compatibility'], 'stability': row['stability'],
            'administration': row['administration'],
            'monitoring_and_warnings': row['source']['body'],
            'limitations': row['limitations'], 'clinical_status': 'CLINICALLY_PENDING',
            'review_status': 'CLINICAL_REVIEW_REQUIRED', 'source': row['source']}


def _lines(value, prefix=''):
    if isinstance(value, dict) and value:
        return [line for k, v in value.items() for line in _lines(v, f'{prefix}.{k}' if prefix else k)]
    if isinstance(value, list) and value:
        return [line for i, v in enumerate(value) for line in _lines(v, f'{prefix}[{i}]')]
    return [prefix + ': ' + (value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, allow_nan=False))]


def calculate_request(payload):
    if not isinstance(payload, dict) or set(payload) != {'regimen_id', 'source_revision', 'inputs'}:
        raise ValueError('Required contract: regimen_id, source_revision, inputs')
    current = catalog()
    if payload['source_revision'] != current['source_revision']:
        raise ValueError('Source revision changed; reload the catalog and calculate again')
    row = next((r for r in current['regimens'] if r['id'] == payload['regimen_id']), None)
    if row is None:
        raise ValueError('Unsupported indication/regimen')
    alerts = _validate(row, payload['inputs'])
    if alerts:
        return {'blocked': True, 'alerts': alerts, 'clinical_status': 'CLINICALLY_PENDING'}
    result = _calculate(row, payload['inputs'])
    finite_tree(result)
    snapshot = {'clinical_status': 'CLINICALLY_PENDING', 'regimen_id': row['id'],
                'source_revision': current['source_revision'], 'inputs': deepcopy(payload['inputs']), 'result': result}
    report = {'snapshot': snapshot, 'sections': [
        ['Farmacología aguda — apoyo aritmético', []],
        ['Estado y límites de validación', ['CLINICALLY_PENDING', 'Functional validation does not constitute prospective clinical validation.']],
        ['Datos y selección confirmados', _lines({'regimen_id': row['id'], 'inputs': payload['inputs']})],
        ['Resultado, preparación, límites, monitorización y evidencia', _lines(result)],
        ['Procedencia', _lines({'source_revision': current['source_revision']})],
    ]}
    return {'blocked': False, 'alerts': [], 'result': result, 'report': report}


def _same_result(a, b):
    """JSON numbers survive JS/Python round trips; booleans remain a distinct type."""
    if type(a) in (int, float) and type(b) in (int, float):
        return math.isfinite(a) and math.isfinite(b) and a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same_result(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_same_result(x, y) for x, y in zip(a, b))
    return a == b


def export_request(payload):
    if not isinstance(payload, dict) or payload.get('confirmed') is not True:
        raise ValueError('Confirm the complete result before export')
    fmt = payload.get('format')
    if fmt not in ('json', 'pdf', 'docx'):
        raise ValueError('Unsupported export format')
    calculated = calculate_request(payload.get('calculation'))
    if calculated['blocked']:
        raise ValueError('Export blocked by clinical safety gates')
    if not _same_result(payload.get('expected_result'), calculated['result']):
        raise ValueError('Result changed; calculate and confirm again')
    report = calculated['report']
    if fmt == 'json':
        data = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    else:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ('acute-medication.' + fmt)
            (export_sections_pdf if fmt == 'pdf' else export_sections_docx)(report['sections'], path)
            data = path.read_bytes()
    mime = {'json': 'application/json', 'pdf': 'application/pdf', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
    return {'filename': 'acute-medication.' + fmt, 'mime_type': mime[fmt], 'content_base64': base64.b64encode(data).decode('ascii')}
