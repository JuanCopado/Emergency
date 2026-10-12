"""Synthetic functional regression; expectations predate v1.44. No clinical release claim."""
import argparse
import io
import json
import math
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree

QA = Path(__file__).resolve().parent
sys.path.insert(0, str(QA.parent / 'scripts'))
from run_clinical_note_diagnostic_cases import build
from clinical_note_diagnostic_engine import analyze
from clinical_note_api import dispatch, export_note_bytes
from clinical_note_support import validate_for_export
from pediatric_outpatient_calculator import calculate
from pediatric_catalog import build_catalog


def expect_assessment(case, assessment):
    assert case['expected_likely'] in [x['diagnosis'] for x in assessment['likely_diagnoses']]
    modules = {m for x in assessment['likely_diagnoses'] for m in x['source_modules']}
    assert set(case.get('expected_modules', [])) <= modules
    names = {x['diagnosis'] for x in assessment['must_not_miss']}
    assert set(case.get('expected_must_not_miss', [])) <= names
    if case.get('expected_test_contains'):
        assert case['expected_test_contains'].lower() in ' '.join(x['action'] for x in assessment['suggested_tests']).lower()
    if case.get('expected_immediate_treatment_module'):
        assert any(case['expected_immediate_treatment_module'] in x['source_modules'] for x in assessment['treatment_suggestions'])


def check_note(case):
    note = build(case)
    result = analyze(deepcopy(note), apply_to_note=True)
    status, api = dispatch('/api/clinical-note/analyze', {'note': deepcopy(note)})
    assert status == 200 and not api['blocked'] and not result['blocked']
    expect_assessment(case, api['assessment'])
    assert api['assessment'] == result['assessment'], 'engine/API assessment divergence'
    accepted = api['note']
    assert accepted['clinician_validation']['reviewed'] is False
    assert validate_for_export(accepted)['blocked']
    accepted['clinician_validation'].update(reviewed=True, reviewer_role='treating_clinician', reviewed_at='2026-10-12T00:00:00Z')
    assert not validate_for_export(accepted)['blocked']
    exported = json.loads(export_note_bytes(accepted, 'json'))
    assert exported == accepted, 'JSON export changed note'
    json.dumps(exported, allow_nan=False)
    # Check representative actual binary contents, not merely file extensions.
    if case['id'] == 'acs-st-elevation':
        from pypdf import PdfReader
        sample = 'DEMO Unicode SpO₂ ≤ 92% → ≥ 38 °C ± β µ'
        accepted['history']['present_illness'] = '\n'.join([sample] * 120 + ['DEMO FINAL ≥'])
        pdf = PdfReader(io.BytesIO(export_note_bytes(accepted, 'pdf')))
        text = '\n'.join(p.extract_text() for p in pdf.pages)
        assert len(pdf.pages) > 2 and text.count(sample) == 120 and 'DEMO FINAL ≥' in text
        assert case['expected_likely'] in text
        with zipfile.ZipFile(io.BytesIO(export_note_bytes(accepted, 'docx'))) as archive:
            xml = ElementTree.fromstring(archive.read('word/document.xml'))
            text = ''.join(xml.itertext())
        assert text.count(sample) == 120 and 'DEMO FINAL ≥' in text and case['expected_likely'] in text
    return {'engine_api': 'PASS', 'expectations': 'PASS', 'review_gate': 'PASS', 'json_export': 'PASS', 'browser': 'NOT_RUN_HERE'}


def check_pediatrics(case):
    args = {k: case[k] for k in ('regimen_id', 'patient', 'product', 'selected_dose_per_kg', 'selected_duration_days', 'selected_volume_ml') if k in case}
    payload = dict(args, source_revision=build_catalog()['source_revision'])
    if case.get('expect_error_contains'):
        for action in (lambda: calculate(**deepcopy(args)), lambda: dispatch('/api/pediatric-outpatient/calculate', deepcopy(payload))):
            try:
                action()
            except ValueError as exc:
                assert case['expect_error_contains'] in str(exc), str(exc)
            else:
                raise AssertionError('expected safety rejection absent')
        return {'engine_api': 'PASS', 'expected_rejection': case['expect_error_contains'], 'browser': 'NOT_RUN_HERE', 'export': 'UNAVAILABLE'}
    direct = calculate(**deepcopy(args))
    status, body = dispatch('/api/pediatric-outpatient/calculate', payload)
    assert status == 200 and not body['blocked']
    assert direct == body['result']
    for key, expected in case['expect'].items():
        actual = direct
        for part in key.split('.'):
            actual = actual[part]
        assert math.isclose(actual, expected, rel_tol=1e-12) if isinstance(expected, (int, float)) else actual == expected, (key, actual, expected)
    json.dumps(body, allow_nan=False)
    return {'engine_api': 'PASS', 'expected_values': case['expect'], 'browser': 'NOT_RUN_HERE', 'export': 'UNAVAILABLE'}


def run(pilot=False):
    bank = json.loads((QA / 'V1.44_DEMO_CASES.json').read_text(encoding='utf-8'))
    rows = []
    for entry in bank['cases']:
        if pilot and not entry['pilot']:
            continue
        row = {'id': entry['id'], 'layer': entry['layer']}
        try:
            source, source_id = entry['provenance'].split('#')
            original = next(c for c in json.loads((QA / source).read_text(encoding='utf-8'))['cases'] if c['id'] == source_id)
            assert original == entry['input'], 'fixture silently diverged from source'
            row.update(check_note(original) if entry['layer'] == 'note' else check_pediatrics(original))
            row['status'] = 'PASS'
        except Exception as exc:
            row.update(status='FAIL', error=f'{type(exc).__name__}: {exc}')
        rows.append(row)
    return {'scope': 'pilot' if pilot else 'bank', 'base_sha': bank['base_sha'], 'clinically_pending': True, 'cases': rows, 'passed': sum(r['status'] == 'PASS' for r in rows)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = run(args.pilot)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(serialized, encoding='utf-8', newline='\n')
    print(serialized)
    sys.exit(report['passed'] != len(report['cases']))
