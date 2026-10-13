"""Canonical pediatric snapshot and existing document formats; no dose logic."""
import base64
import json
import tempfile
from copy import deepcopy
from pathlib import Path
from pediatric_catalog import build_catalog, ROOT
from clinical_note_exporter import export_sections_docx, export_sections_pdf


def lines(value, prefix=''):
    """Lossless field paths. Absent fields stay absent; explicit null stays null."""
    if isinstance(value, dict) and value:
        return [line for k, v in value.items() for line in lines(v, f'{prefix}.{k}' if prefix else k)]
    if isinstance(value, list) and value:
        return [line for i, v in enumerate(value) for line in lines(v, f'{prefix}[{i}]')]
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, allow_nan=False)
    return [f'{prefix}: {text}']


def build_report(payload, result):
    catalog = build_catalog()
    regimen = next(r for r in catalog['regimens'] if r['id'] == payload['regimen_id'])
    evidence = json.loads((ROOT/'references/evidence-registry.json').read_text(encoding='utf-8'))['modules']['pediatric-outpatient-medications']
    snapshot = {
        'clinical_status': 'CLINICALLY_PENDING',
        'evidence_status': evidence['status'],
        'source_revision': catalog['source_revision'],
        'inputs': {k: deepcopy(payload[k]) for k in ('regimen_id', 'patient', 'product', 'selected_dose_per_kg', 'selected_duration_days', 'selected_volume_ml') if k in payload},
        'safety': deepcopy(result['medication_safety']),
        'result': deepcopy(result),
        'regimen': deepcopy(regimen),
        'source': catalog['source'],
        'evidence': evidence,
    }
    sections = [
        ['Resultado pediátrico — apoyo aritmético', []],
        ['Estado y límites', ['CLINICALLY_PENDING', evidence['status'].upper(), 'QA técnico ≠ validación clínica prospectiva. El cálculo no confirma indicación ni criterios de alta.']],
        ['Alertas y revisión', lines(snapshot['safety'])],
        ['Datos utilizados', lines(snapshot['inputs'])],
        ['Resultado canónico', lines(snapshot['result'])],
        ['Ficha canónica: indicación, instrucciones y precauciones', lines(regimen)],
        ['Fuente y evidencia', lines({'source': snapshot['source'], 'source_revision': snapshot['source_revision'], 'evidence': evidence})],
    ]
    return {'snapshot': snapshot, 'sections': sections}


def export_request(payload):
    from pediatric_outpatient_api import calculate_request
    if not isinstance(payload, dict) or payload.get('format') not in ('json', 'pdf', 'docx'):
        raise ValueError('format must be json, pdf or docx')
    computed = calculate_request(payload.get('calculation'))
    if computed['blocked']:
        raise ValueError('Export blocked: medication safety STOP')
    if payload.get('expected_result') != computed['result']:
        raise ValueError('Calculation changed; calculate again before exporting')
    report = computed['export_report']
    fmt = payload['format']
    if fmt == 'json':
        data = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')
    else:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/('pediatric-result.'+fmt)
            (export_sections_pdf if fmt == 'pdf' else export_sections_docx)(report['sections'], path)
            data = path.read_bytes()
    mime = {'json': 'application/json', 'pdf': 'application/pdf', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}[fmt]
    return {'filename': 'pediatric-result.'+fmt, 'mime_type': mime, 'content_base64': base64.b64encode(data).decode('ascii')}
