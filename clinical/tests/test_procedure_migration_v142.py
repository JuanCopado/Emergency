"""Source fidelity and hostile-data checks for structural migration (not clinical validation)."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from procedure_structured import ALIASES, DATA, REVIEW, canonical, load, project, serialize, validate


class ProcedureMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards, cls.aliases = canonical()
        cls.reviews = load(REVIEW)

    def test_exact_inventory_unique_ids_and_families(self):
        self.assertEqual(len(self.cards), 196)
        self.assertEqual(len(self.aliases), 4)
        self.assertEqual(len({c['family'] for c in self.cards.values()}), 16)
        self.assertFalse(set(self.cards) & set(self.aliases))

    def test_alias_targets_and_no_duplicate_cards(self):
        self.assertEqual(self.aliases, ALIASES)
        for alias, target in self.aliases.items():
            self.assertIn(target, self.cards)
            self.assertNotIn(target, self.aliases)
            self.assertFalse((DATA / (alias + '.json')).exists())

    def test_every_projection_schema_and_source_fidelity(self):
        for pid, card in self.cards.items():
            with self.subTest(pid=pid):
                data = project(card, self.reviews)
                self.assertEqual(validate(data), [])
                self.assertEqual(data['name'], card['name'])
                self.assertEqual(data['family'], card['family'])
                self.assertEqual(data['level'], card['level'])
                self.assertEqual(data['objective'], card['sections']['Objetivo'])
                self.assertEqual(data['indications'], [card['sections']['Indicaciones']])
                self.assertEqual(data['stop_points'], [card['sections']['STOP']])
                self.assertEqual(data['confirmation'], [card['sections']['Confirmación']])
                self.assertEqual(data['sources'][0]['title'], card['sections']['Fuentes'])
                self.assertEqual(data['provenance']['sections'], card['sections'])
                self.assertEqual(data['provenance']['family_preamble'], card['family_preamble'])
                for step in data['steps']:
                    self.assertIn(step['action'], card['sections']['Técnica paso a paso'])
                for field in ('rescue', 'escalation'):
                    excerpts = data['provenance']['safety_excerpts'][field]
                    self.assertEqual(data[field], [e['quote'] for e in excerpts] or None)
                    for excerpt in excerpts:
                        self.assertIn(excerpt['quote'], card['sections'][excerpt['section']])

    def test_committed_artifacts_match_source_and_schema(self):
        selected = os.environ.get('PROCEDURE_MIGRATION_FAMILY')
        # During rollout a family is an explicit test target; final/default checks all 196.
        ids = [pid for pid in self.cards if not selected or pid.split('-')[1] == selected]
        self.assertTrue(ids)
        for pid in ids:
            with self.subTest(pid=pid):
                path = DATA / (pid + '.json')
                self.assertTrue(path.exists())
                data = load(path)
                self.assertEqual(validate(data), [])
                self.assertEqual(data, project(self.cards[pid], self.reviews))
        self.assertFalse({p.stem for p in DATA.glob('*.json')} - set(self.cards))

    def test_deterministic_projection_and_yellow_only(self):
        for card in self.cards.values():
            first = project(card, self.reviews)
            self.assertEqual(serialize(first), serialize(project(card, self.reviews)))
            self.assertEqual(first['status'], 'YELLOW')
            self.assertEqual(first['qa']['clinical_qa'], 'pending')
            self.assertIs(first['qa']['human_review_required'], True)
            self.assertIsNone(first['qa']['last_updated'])

    def test_missing_rescue_is_explicitly_pending_not_stop_copy(self):
        card = copy.deepcopy(self.cards['PROC-AIR-004'])
        data = project(card)
        self.assertIsNone(data['rescue'])
        self.assertIn('rescue', data['pending_review'])
        data['pending_review'].remove('rescue')
        self.assertTrue(validate(data))

    def test_unsupported_safety_text_is_rejected(self):
        card = self.cards['PROC-AIR-001']
        for field in ('rescue', 'escalation'):
            with self.assertRaisesRegex(ValueError, 'unsupported'):
                project(card, {card['procedure_id']: {field: [{'section': 'STOP', 'quote': 'Invented rescue 999 mg'}]}})

    def test_schema_rejects_types_empty_duplicates_and_promotions(self):
        good = project(self.cards['PROC-AIR-001'])
        mutations = [('objective', ''), ('objective', '   '), ('objective', 5),
                     ('status', 'GREEN'), ('steps', []), ('indications', ['', '']),
                     ('stop_points', ['same', 'same']), ('rescue', []), ('rescue', 'stop'),
                     ('rescue', [True]), ('level', 'UNSPECIFIED'), ('extra', 'unexpected')]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                self.assertTrue(validate({**good, key: value}))
        for value in (float('inf'), float('-inf'), float('nan'), True, '1'):
            bad = copy.deepcopy(good); bad['steps'][0]['order'] = value
            self.assertTrue(validate(bad))

    def test_json_loader_rejects_nonfinite_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            for raw in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}', '{"a":1,"a":2}'):
                path.write_text(raw, encoding='utf-8')
                with self.assertRaises(ValueError): load(path)

    def test_both_schemas_are_valid(self):
        from jsonschema import Draft202012Validator
        for version in ('1.41', '1.42'):
            Draft202012Validator.check_schema(load(ROOT / f'schemas/procedure-v{version}.schema.json'))


if __name__ == '__main__':
    unittest.main()
