"""Canonical provenance must survive technical normalization, without approval."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('normalize_evidence_sources', ROOT / 'scripts/normalize_evidence_sources.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def record(title, version='v1', checked='2026-09-01'):
    return {'primary_source': title, 'primary_source_url': 'https://example.test/shared',
            'stored_version': version, 'last_checked': checked}


class CanonicalProvenanceTests(unittest.TestCase):
    def test_shared_url_does_not_collapse_distinct_canonical_metadata(self):
        records = {'alpha': record('Source A'), 'beta': record('Source B', 'v2', '2026-09-02'),
                   'gamma': record('Source A', 'v3', '2026-09-03')}
        output = MOD.normalize({'modules': records})
        sources = {s['source_id']: s for s in output['sources']}
        self.assertEqual(len(sources), 3)
        for module, canonical in records.items():
            source = sources[output['module_sources'][module][0]['source_id']]
            self.assertEqual(source['title'], canonical['primary_source'])
            self.assertEqual(source['version'], canonical['stored_version'])
            self.assertEqual(source['last_verified'], canonical['last_checked'])
        reversed_output = MOD.normalize({'modules': dict(reversed(list(records.items())))})
        self.assertEqual(output, reversed_output)

    def test_plus_citation_remains_compound_and_unapproved(self):
        output = MOD.normalize({'modules': {'alpha': record('Guideline A + local protocol B')}})
        source = output['sources'][0]
        self.assertTrue(source['compound_identity'])
        self.assertEqual(source['license_status'], 'unknown')
        self.assertIsNone(source['publication_date'])

    def test_overrides_do_not_replace_canonical_relationship(self):
        canonical = record('New guideline + supplied local card')
        override = {'sources': [{'source_id': 'historic', 'title': 'Historical guideline'}],
                    'module_sources': {'alpha': [{'source_id': 'historic',
                        'role': 'primary_guideline', 'claim_scope': 'module-level'}]}}
        output = MOD.normalize({'modules': {'alpha': canonical}}, override)
        sources = {s['source_id']: s for s in output['sources']}
        refs = output['module_sources']['alpha']
        self.assertEqual(len(refs), 2)
        self.assertTrue(any(sources[ref['source_id']]['title'] == canonical['primary_source'] for ref in refs))
        historical = next(ref for ref in refs if ref['source_id'] == 'historic')
        self.assertEqual(historical['role'], 'historical_component_pending_reconciliation')

    def test_current_catalog_preserves_every_canonical_identity(self):
        registry = json.loads((ROOT / 'references/evidence-registry.json').read_text())
        overrides = json.loads((ROOT / 'references/evidence-source-overrides.json').read_text())
        output = MOD.normalize(registry, overrides)
        sources = {s['source_id']: s for s in output['sources']}
        for module, canonical in registry['modules'].items():
            self.assertTrue(any(
                sources[ref['source_id']]['title'] == canonical['primary_source'].strip()
                and sources[ref['source_id']]['version'] == canonical['stored_version']
                and sources[ref['source_id']]['last_verified'] == canonical['last_checked']
                for ref in output['module_sources'][module]), module)


if __name__ == '__main__':
    unittest.main()
