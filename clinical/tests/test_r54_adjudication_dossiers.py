"""R54: physical linkage, actual manifest IDs and non-invented clinical fields."""
import copy
import hashlib
import json
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'lab'))
from human_factors import adjudication_r54 as dossiers

MANIFEST = json.loads((ROOT / 'lab/human_factors/bank/stimuli_manifest.json').read_text())
BANK = ROOT / 'lab/human_factors/bank'


class Dossiers(unittest.TestCase):
    def test_actual_ids_and_distribution(self):
        rows = dossiers.build_dossiers(MANIFEST, BANK)
        self.assertEqual({r['stimulus_id'] for r in rows}, {r['stimulus_id'] for r in MANIFEST['stimuli']})
        self.assertEqual(Counter(r['mechanism_id'] for r in rows), {'M1': 8, 'M2': 4, 'M3': 18})
        for set_id in (1, 2):
            self.assertEqual(Counter(r['mechanism_id'] for r in rows if r['set_id'] == set_id), {'M1': 4, 'M2': 2, 'M3': 9})

    def test_numbering_and_order_do_not_determine_mechanism(self):
        m = copy.deepcopy(MANIFEST)
        m['stimuli'].reverse()
        for i, row in enumerate(m['stimuli']):
            row['stimulus_id'] = f'opaque-{i}'
        rows = dossiers.build_dossiers(m, BANK)
        self.assertEqual([(r['stimulus_id'], r['mechanism_id']) for r in rows], [(r['stimulus_id'], r['mechanism_id']) for r in m['stimuli']])

    def test_na_only_when_diagnostic_adjudication_does_not_apply(self):
        for r in dossiers.build_dossiers(MANIFEST, BANK):
            expected = 'N/A' if r['mechanism_id'] in ('M1', 'M2') or r['expected_modality'] == 'document' else 'PENDING_CLINICAL_ADJUDICATION'
            self.assertEqual(r['clinical_ground_truth'], expected, r['stimulus_id'])
            self.assertEqual(r['owner_decision'], 'PENDING')
            self.assertEqual(r['signature_date'], 'PENDING')

    def test_hashes_are_measured_and_missing_assets_stay_pending(self):
        rows = dossiers.build_dossiers(MANIFEST, BANK)
        self.assertEqual(sum(r['physical_status'] == 'VERIFIED_BYTES' for r in rows), 10)
        for r in rows:
            if r['file']:
                self.assertEqual(r['stimulus_hash_sha256'], hashlib.sha256((BANK / r['file']).read_bytes()).hexdigest())
            else:
                self.assertIsNone(r['stimulus_hash_sha256'])
                self.assertEqual(r['physical_status'], 'PENDING_STIMULUS_GENERATION')

    def test_indexed_review_dossiers_match_manifest_and_physical_bytes(self):
        review = ROOT.parent / "docs/coordination/r54"
        index = (review / "INVENTORY.md").read_text(encoding="utf-8")
        rows = {line.split("|")[1].strip(): line for line in index.splitlines() if line.startswith(("| S1-", "| S2-"))}
        current = dossiers.build_dossiers(MANIFEST, BANK)
        self.assertEqual(set(rows), {row["stimulus_id"] for row in current})
        for row in current:
            with self.subTest(stimulus_id=row["stimulus_id"]):
                line = rows[row["stimulus_id"]]
                path = re.search(r"\((dossiers/[^)]+\.json)\)", line).group(1)
                self.assertEqual(json.loads((review / path).read_text(encoding="utf-8")), row)
                self.assertEqual(line.split("|")[7].strip(), row["stimulus_hash_sha256"] or "—")

    def test_original_s2_09_dossier_stays_bound_to_historical_manifest(self):
        review = ROOT.parent / "docs/coordination/r54"
        original = json.loads((review / "literal/base/stimuli_manifest.json").read_text(encoding="utf-8"))
        old = next(row for row in original["stimuli"] if row["stimulus_id"] == "S2-09")
        reference = json.loads((review / "dossiers/S2-09.json").read_text(encoding="utf-8"))
        self.assertEqual(reference["stimulus_hash_sha256"], old["sha256"])
        self.assertEqual(reference["bytes"], old["bytes"])

    def test_m1_never_invents_layer7_mismatch_trigger(self):
        for r in dossiers.build_dossiers(MANIFEST, BANK):
            if r['mechanism_id'] == 'M1':
                self.assertIsNone(r['expected_layer7_trigger'])
                self.assertIn('NOT_CONTENT_CLASSIFICATION', r['expected_system_behavior'])

    def test_duplicates_and_wrong_distribution_fail_closed(self):
        for mutation in ('duplicate', 'mechanism', 'set'):
            m = copy.deepcopy(MANIFEST)
            if mutation == 'duplicate':
                m['stimuli'][0]['stimulus_id'] = m['stimuli'][1]['stimulus_id']
            elif mutation == 'mechanism':
                m['stimuli'][0]['mechanism_id'] = 'M1'
            else:
                m['stimuli'][0]['set_id'] = 2
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                dossiers.build_dossiers(m, BANK)

    def test_stale_hash_or_missing_physical_file_fails(self):
        m = copy.deepcopy(MANIFEST)
        row = next(r for r in m['stimuli'] if r['file'])
        row['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            dossiers.build_dossiers(m, BANK)
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            dossiers.build_dossiers(MANIFEST, Path(directory))

    def test_manifest_cannot_escape_bank_directory(self):
        m = copy.deepcopy(MANIFEST)
        next(r for r in m['stimuli'] if r['file'])['file'] = '../stimuli_manifest.json'
        with self.assertRaises(ValueError):
            dossiers.build_dossiers(m, BANK)

    def test_explicit_m1_clinical_target_requires_reference(self):
        m = copy.deepcopy(MANIFEST)
        row = next(r for r in m['stimuli'] if r['mechanism_id'] == 'M1')
        row['explicit_clinical_red_flag'] = 'requires independent expert assessment'
        result = next(r for r in dossiers.build_dossiers(m, BANK) if r['stimulus_id'] == row['stimulus_id'])
        self.assertEqual(result['clinical_ground_truth'], 'PENDING_CLINICAL_ADJUDICATION')

    def test_scenario_mismatch_and_hash_for_absent_file_fail(self):
        for mutation in ('scenario', 'absent_hash'):
            m = copy.deepcopy(MANIFEST)
            if mutation == 'scenario':
                m['stimuli'][0]['scenario_code'] = 'B'
            else:
                m['stimuli'][0]['sha256'] = '0' * 64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                dossiers.build_dossiers(m, BANK)
