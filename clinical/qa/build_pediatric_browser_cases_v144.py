"""Synthetic browser fixtures, independently derived from the versioned registry.

Never imports the calculator. Decimal arithmetic and literal source fields form
the oracle; fixtures are test data, not prescriptions or new clinical defaults.
"""
import copy
import hashlib
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'clinical' / 'qa'
registry_bytes = (QA / 'pediatric-outpatient-medications.json').read_bytes()
entries = json.loads(registry_bytes)['entries']
previous = json.loads((QA / 'V1.44_PHARMACOLOGY_BROWSER_RESULTS.json').read_text(encoding='utf-8'))
covered = {c['regimen_id'] for c in previous['pediatric']}


def number(v):
    return Decimal(str(v))


def band_for(e, p):
    for b in e.get('bands', []):
        age, weight = p['age_months'], p['actual_weight_kg']
        if (age >= b.get('min_age_months', 0) and age <= b.get('max_age_months', float('inf'))
                and weight > b.get('min_weight_kg', -1)
                and weight >= b.get('min_weight_kg_inclusive', 0)
                and weight <= b.get('max_weight_kg', float('inf'))):
            return b
    return None


def expected(e, c):
    """Expected numeric/text result fields from the registry, not the API."""
    p = c['patient']
    b = band_for(e, p)
    model = e['dose_model']
    if e.get('bands') and b is None:
        return None
    out = {'route': e.get('route', 'PO'), 'weight_basis': e['weight_basis']}
    duration = (b or {}).get('duration_days', e.get('duration_days'))
    if isinstance(duration, list):
        duration = c['selected_duration_days']
    daily = (b or {}).get('doses_per_day', e.get('doses_per_day'))
    out.update(duration_days=duration, doses_per_day=daily)
    conc = c.get('product', {}).get('concentration_mg_per_ml')
    basis = {'actual': 'actual_weight_kg', 'ideal': 'ideal_weight_kg', 'adjusted': 'adjusted_weight_kg'}
    weight = number(p[basis[e['weight_basis']]]) if e['weight_basis'] in basis else None

    def dose(fields):
        if fields.get('dose_mg') is not None:
            raw = number(fields['dose_mg'])
        else:
            raw = number(fields['dose_mg_per_kg']) * (weight or number(p['actual_weight_kg']))
        return float(min(raw, number(fields['max_mg_per_dose']))) if fields.get('max_mg_per_dose') else float(raw)

    def volume(path, mg):
        if conc is not None:
            out[path + 'volume_per_dose.exact_ml'] = float(number(mg) / number(conc))
            out[path + 'volume_per_dose.concentration_mg_per_ml'] = conc

    mg = None
    if model == 'mg_per_kg_per_dose':
        perkg = e.get('dose_mg_per_kg', c.get('selected_dose_per_kg'))
        mg = dose({**e, 'dose_mg_per_kg': perkg})
        out.update(dosing_weight_kg=float(weight), dose_mg_per_kg=perkg)
    elif model == 'fixed_dose':
        mg = dose({**e, 'dose_mg': e['fixed_dose_mg']})
    elif model in ('fixed_age_band', 'fixed_weight_band'):
        mg = dose({**e, **b}) if 'dose_mg' in b or 'dose_mg_per_kg' in b else None
        out['matched_band'] = b
    elif model in ('fixed_schedule', 'schedule_by_day'):
        total, ml = 0, Decimal(0)
        for i, phase in enumerate(e['schedule']):
            amount = dose({**e, **phase})
            count = phase.get('total_phase_doses', phase.get('doses', 1)) if model == 'fixed_schedule' else phase.get('days', 1) * phase.get('doses_per_day', 1)
            out[f'schedule.{i}.dose_mg'] = amount
            out[f'schedule.{i}.total_phase_doses'] = count
            volume(f'schedule.{i}.', amount)
            total += count
            if conc:
                ml += number(amount) / number(conc) * number(count)
        out['total_doses'] = total
        if conc:
            out['estimated_total_course_ml'] = float(ml)
    elif model == 'fixed_volume_band':
        out['matched_band'] = b
        out['dose_unit'] = 'mL'
        out['volume_per_dose.exact_ml'] = b.get('dose_ml', c.get('selected_volume_ml'))
        out['volume_per_dose.concentration_mg_per_ml'] = None
    elif model == 'sachet_schedule':
        out.update(matched_band=b, dose_unit='sachet', sachets_per_day=b.get('sachets_per_day'), sachet_schedule=b.get('schedule'))
    elif model == 'device':
        out['device'] = b
    elif model == 'topical':
        out['instructions'] = e['topical_instructions']
        for key in ('drops_per_dose', 'doses_per_day_range', 'volume_per_administration_ml', 'applications_per_day', 'repeat_after_days', 'product_strength'):
            if key in e:
                out[key] = e[key]
    elif model == 'volume_ml_per_kg_course':
        ml = number(p['actual_weight_kg']) * number(e['volume_ml_per_kg'])
        out.update(total_rehydration_ml=float(ml), administration_hours=e['administration_hours'], target_ml_per_hour=float(ml / number(e['administration_hours'])))
    else:
        raise AssertionError(model)
    if mg is not None:
        out['dose_mg'] = mg
        volume('', mg)
        if daily and duration:
            out['total_doses'] = daily * duration
            if conc:
                out['estimated_total_course_ml'] = float(number(mg) / number(conc) * number(daily) * number(duration))
    return out


cases = []
inventory = []
for e in entries:
    age = max(e.get('min_age_months', 60), 1)
    age = min(age, e.get('max_age_months', age))
    p = dict(age_months=age, actual_weight_kg=20, allergies=[], active_medications=[], known_renal_impairment=False, known_hepatic_impairment=False)
    for g in e.get('required_patient_flags', []):
        p[g['field']] = g.get('equals', True)
    for g in e.get('excluded_patient_flags', []):
        p[g['field']] = not g.get('equals', True)
    for g in e.get('minimum_patient_values', []):
        p[g['field']] = g['minimum']
    for g in e.get('maximum_patient_values', []):
        p[g['field']] = g['maximum']
    if e['weight_basis'] in ('ideal', 'adjusted'):
        p[e['weight_basis'] + '_weight_kg'] = 15
    base = {'regimen_id': e['id'], 'patient': p}
    if isinstance(e.get('duration_days'), list):
        base['selected_duration_days'] = e['duration_days'][0]
    if e.get('dose_mg_per_kg_range'):
        base['selected_dose_per_kg'] = e['dose_mg_per_kg_range'][0]
    concentrations = e.get('verified_concentrations', [])
    if e.get('liquid_capable') and concentrations:
        base['product'] = {'concentration_mg_per_ml': concentrations[0]['mg_per_ml']}
    if e.get('bands'):
        b = e['bands'][0]
        p['age_months'] = max(e.get('min_age_months', 0), b.get('min_age_months', min(p['age_months'], b.get('max_age_months', p['age_months']))))
        p['actual_weight_kg'] = b.get('min_weight_kg_inclusive', b.get('min_weight_kg', 0) + 1)
        if not any('weight' in k for k in b):
            p['actual_weight_kg'] = 20
        if isinstance(b.get('duration_days'), list):
            base['selected_duration_days'] = b['duration_days'][0]
        if 'dose_ml_range' in b:
            base['selected_volume_ml'] = b['dose_ml_range'][0]

    def add(name, changes=None, patient=None, rejection=False, alerts=None, local_error=False):
        c = copy.deepcopy(base)
        c.update(changes or {})
        c['patient'].update(patient or {})
        c['id'] = e['id'] + ':' + name
        c['scenario'] = name
        c['expect_rejection'] = rejection
        c['expect_alerts'] = alerts or []
        c['local_error'] = local_error
        if not rejection:
            match = band_for(e, c['patient'])
            if match and 'dose_ml_range' in match:
                c.setdefault('selected_volume_ml', match['dose_ml_range'][0])
            c['expect'] = expected(e, c)
            if c['expect'] is None:
                c['expect_rejection'] = True
                c['source_band_gap'] = True
        cases.append(c)

    add('nominal')
    add('allergy-stop', patient={'allergies': [e['drug']]}, rejection=True, alerts=['ALLERGY_EXACT'])
    add('invalid-numeric', patient={'actual_weight_kg': -1}, rejection=True, local_error=True)
    add('context-alerts', patient={'allergies': None, 'active_medications': None}, alerts=['ALLERGY_STATUS_NOT_DOCUMENTED', 'MEDICATION_RECONCILIATION_NOT_DOCUMENTED'])
    for bound, direction in [('min_age_months', -1), ('max_age_months', 1)]:
        if bound in e:
            add(bound + '-at', patient={'age_months': e[bound]})
            if e[bound] + direction >= 0:
                add(bound + '-outside', patient={'age_months': e[bound] + direction}, rejection=True)
    for i, b in enumerate(e.get('bands', [])):
        for key in ('min_age_months', 'max_age_months', 'min_weight_kg', 'min_weight_kg_inclusive', 'max_weight_kg'):
            if key not in b:
                continue
            field = 'age_months' if 'age' in key else 'actual_weight_kg'
            for suffix, delta in [('at', 0), ('below', -0.001), ('above', 0.001)]:
                value = round(b[key] + delta, 6)
                if value <= 0 or ('age' in key and (value < e.get('min_age_months', 0) or value > e.get('max_age_months', float('inf')))):
                    continue
                selected = {}
                test_patient = {**base['patient'], field: value}
                match = band_for(e, test_patient)
                if match and 'dose_ml_range' in match:
                    selected['selected_volume_ml'] = match['dose_ml_range'][0]
                if match and isinstance(match.get('duration_days'), list):
                    selected['selected_duration_days'] = match['duration_days'][0]
                add(f'band-{i}-{key}-{suffix}', changes=selected, patient={field: value})
    if e.get('max_mg_per_dose') and e['dose_model'] == 'mg_per_kg_per_dose':
        key = e['weight_basis'] + '_weight_kg'
        perkg = e.get('dose_mg_per_kg', base.get('selected_dose_per_kg'))
        add('dose-cap', patient={key: float(number(e['max_mg_per_dose']) / number(perkg) * 2)})
    for field, source in [('selected_dose_per_kg', 'dose_mg_per_kg_range'), ('selected_duration_days', 'duration_days')]:
        if isinstance(e.get(source), list):
            add(field + '-upper', changes={field: e[source][1]})
            add(field + '-outside', changes={field: e[source][1] + 1}, rejection=True)
    for i, g in enumerate(e.get('required_patient_flags', [])):
        add(f'required-{i}', patient={g['field']: not g.get('equals', True)}, rejection=True, alerts=['REQUIRED_CLINICAL_CRITERION_NOT_MET'])
    for i, g in enumerate(e.get('excluded_patient_flags', [])):
        add(f'excluded-{i}', patient={g['field']: g.get('equals', True)}, rejection=True, alerts=['CLINICAL_EXCLUSION_PRESENT'])
    for i, g in enumerate(e.get('minimum_patient_values', [])):
        add(f'minimum-value-{i}', patient={g['field']: g['minimum'] - 0.01}, rejection=True)
    renal = e.get('renal_adjustment', {})
    if renal.get('mode') == 'standard_if_egfr_at_least':
        add('renal-at', patient={'known_renal_impairment': True, 'egfr_mL_min': renal['minimum_egfr']})
        add('renal-below', patient={'known_renal_impairment': True, 'egfr_mL_min': renal['minimum_egfr'] - 0.01}, rejection=True)
    elif renal.get('mode') == 'block_standard_regimen':
        add('renal-block', patient={'known_renal_impairment': True}, rejection=True)
    hepatic = e.get('hepatic_adjustment', {})
    if hepatic.get('mode') == 'block_standard_regimen' or hepatic.get('block_if_severe'):
        add('hepatic-block', patient={'known_hepatic_impairment': True, 'hepatic_severity': 'severe'}, rejection=True)
    for i, concentration in enumerate(concentrations[1:], 1):
        add(f'concentration-{i}', changes={'product': {'concentration_mg_per_ml': concentration['mg_per_ml']}})
    inventory.append({'regimen_id': e['id'], 'dose_model': e['dose_model'], 'previous_browser_case': e['id'] in covered, 'source_url': e.get('source_url'), 'cases': sum(c['regimen_id'] == e['id'] for c in cases)})

output = {'status': 'CLINICALLY_PENDING', 'source_sha256': hashlib.sha256(registry_bytes).hexdigest(), 'oracle': 'Registry literals and independent Decimal arithmetic; no calculator imports. Synthetic inputs are not clinical recommendations.', 'previous_unique_regimens': len(covered), 'previous_missing_regimens': [e['id'] for e in entries if e['id'] not in covered], 'inventory': inventory, 'cases': cases}
(QA / 'V1.44_PEDIATRIC_BROWSER_CASES.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(f'{len(entries)} regimens; {len(entries)-len(covered)} previously missing; {len(cases)} scenarios')
