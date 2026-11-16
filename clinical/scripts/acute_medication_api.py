"""Source-bound calculations and faithful exports for acute medication workflows."""
import base64
import hashlib
import json
import tempfile
from acid_base_hyperglycemia import calculate as hyperglycemia_calculate
from copy import deepcopy
from pathlib import Path

from acute_medication_contracts import regimens
from clinical_note_exporter import export_sections_pdf, export_sections_docx
from pediatric_numbers import finite_tree, finite_number, finite_result
import acute_reviewed_status
import acute_reviewed_anaphylaxis
import acute_reviewed_reversal

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_WORKFLOWS = {
    'status': acute_reviewed_status,
    'anaphylaxis': acute_reviewed_anaphylaxis,
    'reversal': acute_reviewed_reversal,
}


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
    acceptance_path = ROOT / 'references/acute-contract-owner-acceptance-2026-11-16.json'
    acceptance = json.loads(acceptance_path.read_text(encoding='utf-8'))
    rows = []
    contracts = regimens()
    reviewed_ids = {row['id'] for row in contracts if row.get('reviewed_workflow')}
    if reviewed_ids != set(acceptance['contract_ids']):
        raise ValueError('Reviewed release does not match the owner acceptance scope')
    for row in contracts:
        fields = {item['key']: item for item in row['fields']}
        if len(fields) != len(row['fields']):
            raise ValueError('Duplicate input field in contract: ' + row['id'])
        for item in row['fields']:
            condition = item.get('required_if')
            if condition is not None:
                driver = fields.get(condition.get('key')) if isinstance(condition, dict) else None
                if (not driver or driver['kind'] != 'choice' or driver.get('required_if')
                        or condition.get('equals') not in driver['options']
                        or set(condition) != {'key', 'equals'}):
                    raise ValueError('Invalid conditional input in contract: ' + row['id'])
        preamble, body = _section(row['bundle'], row['module'])
        for anchor in row['anchors']:
            if anchor not in body:
                raise ValueError('Canonical source changed; reconcile contract: ' + row['id'])
        local = next((x for x in localization if x['drug'] == row.get('localization_drug')), None)
        if row.get('product_anchor') and (local is None or row['product_anchor'] not in local['product_strength']):
            raise ValueError('Canonical product reference changed; reconcile contract: ' + row['id'])
        source = {'module': row['module'], 'path': 'clinical/modules/' + row['bundle'],
                  'preamble': preamble, 'body': body, 'evidence': evidence[row['module']], 'localization': local}
        if row.get('reviewed_workflow'):
            if row['reviewed_workflow'] not in REVIEWED_WORKFLOWS:
                raise ValueError('Unknown reviewed workflow')
            if row['id'] not in acceptance['contract_ids'] or row.get('block_reason'):
                raise ValueError('Reviewed contract acceptance or release mismatch')
            reference = ROOT / row['review_reference']
            if reference.resolve().parent != (ROOT / 'references').resolve():
                raise ValueError('Review reference must be a canonical reference file')
            source['contract_review'] = {
                'path': 'clinical/' + row['review_reference'],
                'body': reference.read_text(encoding='utf-8'),
                'sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
                'owner_acceptance': acceptance,
            }
        rows.append({**row, 'source': source})
    serialized = json.dumps(rows, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
    # A change in an imported calculation must invalidate snapshots and exports too.
    implementation = [Path(__file__), Path(__file__).with_name('acute_medication_contracts.py'),
                      Path(__file__).with_name('acid_base_hyperglycemia.py'),
                      Path(__file__).with_name('pediatric_numbers.py')]
    implementation.extend(Path(module.__file__) for module in REVIEWED_WORKFLOWS.values())
    for module in REVIEWED_WORKFLOWS.values():
        implementation.extend(Path(p) for p in getattr(module, 'IMPLEMENTATION_FILES', []))
    digest = hashlib.sha256(serialized)
    for path in sorted(set(implementation)):
        digest.update(path.name.encode('utf-8'))
        digest.update(path.read_bytes())
    revision = digest.hexdigest()
    return {'source_revision': revision, 'clinical_status': 'CLINICALLY_PENDING', 'regimens': rows}


def _alert(code, message):
    return {'severity': 'STOP', 'code': code, 'message': message}


def _is_finite(value):
    try:
        finite_number('value', value)
    except ValueError:
        return False
    return True


def _field_active(field, inputs):
    condition = field.get('required_if')
    return condition is None or inputs.get(condition['key']) == condition['equals']


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
        if not _field_active(f, inputs):
            if value is not None:
                alerts.append(_alert(key, 'Dato no aplicable al modo seleccionado: ' + f['label'] + '. Retirar el valor anterior.'))
            continue
        invalid = value is None
        if kind == 'boolean':
            invalid |= type(value) is not bool
        elif kind == 'number':
            invalid |= type(value) not in (int, float) or not _is_finite(value)
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
    if not alerts and row.get('reviewed_workflow'):
        module = REVIEWED_WORKFLOWS[row['reviewed_workflow']]
        alerts.extend(_alert(code, message) for code, message in module.validation_errors(row, inputs))
    if not alerts and row['model'] == 'adrenaline_im' and inputs['prior_im_doses'] == 1 and inputs['elapsed_min'] < 5:
        alerts.append(_alert('repeat_interval', 'Reevaluar; no se cumple el intervalo de 5 min de esta pauta IM.'))
    return alerts


@finite_result
def _calculate(row, inputs):
    if row.get('reviewed_workflow'):
        module = REVIEWED_WORKFLOWS[row['reviewed_workflow']]
        values = module.calculate(row, inputs)
        result = {
            'indication': row['label'], 'drug': row['drug'], 'route': row['route'],
            'dose': None, 'dose_unit': None, 'concentration': None, 'components': None,
            'withdrawal_ml': None, 'administration_volume_ml': None, 'pump_ml_h': None,
            'duration_min': None, 'amount_per_hour': None, 'amount_per_hour_unit': None,
            'maximum': row.get('maximum'), 'preparation': row.get('preparation'),
            'compatibility': row.get('compatibility'), 'stability': row.get('stability'),
            'administration': row.get('administration'), 'limitations': row.get('limitations', []),
            'result_kind': 'calculation', 'decision_support': None, 'next_actions': [],
            **values,
            'monitoring_and_warnings': row['source']['body'],
            'clinical_status': 'CLINICALLY_PENDING',
            'review_status': 'OWNER_VALIDATED_2026_11_16',
            'source': row['source'],
        }
        if result['result_kind'] == 'decision_support':
            if any(result.get(k) is not None for k in ('dose', 'dose_unit', 'withdrawal_ml', 'administration_volume_ml', 'pump_ml_h',
                                                  'components', 'concentration', 'duration_min', 'amount_per_hour',
                                                  'amount_per_hour_unit', 'maximum')):
                raise ValueError('A decision-support-only flow cannot silently issue a medication calculation')
        return result
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
        dose = min(dose * inputs['enoxaparin_mg'], row['maximum']['value'])
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
    heading = ('Farmacología aguda — apoyo de decisión' if result.get('result_kind') == 'decision_support'
               else 'Farmacología aguda — cálculo condicionado')
    report = {'snapshot': snapshot, 'sections': [
        [heading, []],
        ['Estado y límites de validación', ['CLINICALLY_PENDING', 'Functional validation does not constitute prospective clinical validation.']],
        ['Datos y selección confirmados', _lines({'regimen_id': row['id'], 'inputs': payload['inputs']})],
        ['Resultado, preparación, límites, monitorización y evidencia', _lines(result)],
        ['Procedencia', _lines({'source_revision': current['source_revision']})],
    ]}
    return {'blocked': False, 'alerts': [], 'result': result, 'report': report}


def _same_result(a, b):
    """JSON numbers survive JS/Python round trips; booleans remain a distinct type."""
    if type(a) in (int, float) and type(b) in (int, float):
        return _is_finite(a) and _is_finite(b) and a == b
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
