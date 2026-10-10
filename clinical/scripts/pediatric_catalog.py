"""Lossless outpatient catalog projection; no clinical dose logic is duplicated."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'qa/pediatric-outpatient-medications.json'
RULES = ROOT / 'qa/pediatric-outpatient-alert-rules.json'


def ingredients(label):
    # The registry spells the adrenaline synonym with a slash; it is one agent.
    label = label.replace('epinephrine/adrenaline auto-injector', 'epinephrine')
    parts = []
    for part in label.split(' + '):
        part = re.sub(r'\s+\d+(?:\.\d+)?\s*(?:%|mg|g\b|micrograms?\b).*$', '', part)
        parts.extend(part.replace(' paediatric sachet', '').strip().split('/'))
    return parts


def build_catalog():
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    rules = json.loads(RULES.read_text(encoding='utf-8'))
    entries = sorted(registry['entries'], key=lambda e: e['id'])
    if len({e['id'] for e in entries}) != len(entries):
        raise ValueError('duplicate regimen ID')
    drugs = {}
    regimens = []
    presentations = set()
    for entry in entries:
        if not entry.get('drug') or not entry.get('diagnosis'):
            raise ValueError('each regimen needs a drug and diagnosis')
        names = ingredients(entry['drug'])
        drug_id = re.sub(r'[^a-z0-9]+', '-', ' + '.join(names).lower()).strip('-')
        drug = drugs.setdefault(drug_id, {'id': drug_id, 'name': ' + '.join(names), 'components': names})
        if drug['components'] != names:
            raise ValueError('drug identity collision')
        regimens.append({**entry, 'drug_id': drug_id})
        # Count identifiable source descriptions, not inferred commercial SKUs.
        for item in entry.get('verified_concentrations', []):
            presentations.add((drug_id, entry.get('route'), 'concentration', json.dumps(item, sort_keys=True)))
        if entry.get('product_strength'):
            presentations.add((drug_id, entry.get('route'), 'strength', entry['product_strength']))
        for band in entry.get('bands', []):
            for field in ('device', 'alternative'):
                if band.get(field): presentations.add((drug_id, entry.get('route'), field, band[field]))
        if entry['dose_model'] == 'topical':
            presentations.add((drug_id, entry.get('route'), 'topical', entry['drug']))
    components = {p for d in drugs.values() for p in d['components']}
    unresolved = {'electrolytes', 'low-osmolarity oral rehydration solution'}
    canonical = json.dumps([registry, rules], sort_keys=True, ensure_ascii=False).encode('utf-8')
    return {
        'source': 'clinical/qa/pediatric-outpatient-medications.json',
        'source_revision': hashlib.sha256(canonical).hexdigest(),
        'status': registry['status'], 'safety_rules': registry['safety_rules'],
        'condition_rules': rules.get('condition_rules', []),
        'drugs': sorted(drugs.values(), key=lambda d: d['id']), 'regimens': regimens,
        'inventory': {
            'regimens': len(regimens), 'source_drug_labels': len({e['drug'] for e in entries}),
            'drug_groups': len(drugs), 'named_active_ingredients': len(components - unresolved),
            'unspecified_component_groups': sorted(components & unresolved),
            'diagnoses': len({e['diagnosis'] for e in entries}),
            'drug_diagnosis_pairs': len({(e['drug_id'], e['diagnosis']) for e in regimens}),
            'documented_presentation_descriptions': len(presentations),
            'verified_liquid_products': len({p for p in presentations if p[2] == 'concentration'}),
            'hidden_regimens': 0,
        },
    }


def serialize_catalog():
    return json.dumps(build_catalog(), indent=2, ensure_ascii=False, allow_nan=False) + '\n'
