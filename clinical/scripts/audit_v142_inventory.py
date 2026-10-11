"""Derive current consolidation counts without timestamps or clinical promotion."""
from collections import Counter
import argparse
import re

from procedure_structured import ROOT, DATA, canonical, load, validate, serialize
from pediatric_catalog import build_catalog
from audit_clinical_note_diagnostic_coverage import audit


def inventory():
    cards, aliases = canonical()
    records = [load(path) for path in sorted(DATA.glob('*.json'))]
    evidence = load(ROOT / 'references/evidence-registry.json')['modules']
    calculators = load(ROOT / 'calculators/registry.json')
    sources = load(ROOT / 'references/evidence-surveillance-sources.json')['sources']
    app = ROOT.parent / 'app/src/data'
    index = (ROOT / 'references/module-index.md').read_text(encoding='utf-8')
    module_ids = re.findall(r'^\| ([a-z0-9-]+) \|', index, re.M)
    tests = sorted(p.name for p in (ROOT / 'tests').glob('test_*.py'))
    return {
        'modules': {'manifest_total': len(module_ids), 'evidence_total': len(evidence),
                    'status_counts': dict(sorted(Counter(e['status'] for e in evidence.values()).items())),
                    'missing_evidence': sorted(set(module_ids)-set(evidence)),
                    'orphan_evidence': sorted(set(evidence)-set(module_ids))},
        'procedures': {'canonical': len(cards), 'aliases': aliases, 'textual_ids': len(cards)+len(aliases),
                       'families': dict(sorted(Counter(p.split('-')[1] for p in cards).items())),
                       'structured': len(records), 'schema_valid': sum(not validate(d) for d in records),
                       'rescue_explicit': sum(d['rescue'] is not None for d in records),
                       'rescue_pending': sum(d['rescue'] is None for d in records),
                       'escalation_explicit': sum(d['escalation'] is not None for d in records),
                       'escalation_pending': sum(d['escalation'] is None for d in records),
                       'status_counts': dict(Counter(d['status'] for d in records)),
                       'index_card_differences': [
                           {'procedure_id': p, 'index_name': c['name'], 'card_name': c['card_name'],
                            'index_level': c['level'], 'card_level': c['card_level']}
                           for p, c in cards.items() if c['name'] != c['card_name'] or c['level'] != c['card_level']]},
        'calculators': {'scales': len(calculators['scales']), 'formulas': len(calculators['formulas']),
                        'implementation_counts': dict(sorted(Counter(s.get('implementation_status', 'unspecified') for s in calculators['scales']).items())),
                        'wrappers': [s['id'] for s in calculators['scales'] if s.get('implementation_status') == 'validated_official_external_wrapper'],
                        'formula_aliases': [s['id'] for s in calculators['scales'] if s.get('implementation_status') == 'central_formula_alias']},
        'clinical_note': audit(),
        'pediatrics': build_catalog()['inventory'],
        'frontend': {'clinical_guides': len(load(app / 'generatedClinicalGuides.json')),
                     'canonical_procedures': len(load(app / 'generatedProcedures.json')),
                     'pediatric_regimens': len(load(app / 'generatedPediatricOutpatient.json')['regimens'])},
        'surveillance': {'configured_sources': len(sources),
                         'enabled_sources': sum(s.get('enabled', True) is not False for s in sources),
                         'source_ids': [s['id'] for s in sources],
                         'evidence_primary_urls': len({e['primary_source_url'] for e in evidence.values() if e.get('primary_source_url')})},
        'python_test_files': tests,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = serialize(inventory())
    output = ROOT / 'qa/V1.42_INVENTORY.json'
    if args.check:
        if not output.exists() or output.read_text(encoding='utf-8') != content:
            raise SystemExit('Current inventory artifact is stale')
    else:
        output.write_text(content, encoding='utf-8', newline='\n')
    print(content)
