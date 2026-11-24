"""Owner-authorized R54 safety instructions; structural regressions, not vision validation."""
import sys
import json
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load


class Safeguards(unittest.TestCase):
    def section(self, module):
        # Exercise the clinical loader, including the safety preamble.
        return load(ROOT, module)

    def test_parent_never_excludes_urgent_pathology(self):
        self.assertIn('No system output alone excludes urgent pathology.', self.section('clinical-image-interpretation'))

    def test_pocus_stills_do_not_exclude_acute_pathology(self):
        self.assertIn('Isolated static POCUS images do not exclude acute pathology.', self.section('pocus-image'))

    def test_incomplete_ct_mri_does_not_replace_complete_evaluation(self):
        self.assertIn('Isolated CT/MRI screenshots or incomplete series do not replace a complete evaluation.', self.section('ct-mri-screenshot'))

    def test_hand_wound_requires_direct_examination(self):
        self.assertIn('Hand wounds require direct neurovascular and tendon examination.', self.section('skin-wound-image'))

    def test_dark_phototypes_require_caution_and_review(self):
        self.assertIn('Phototypes V–VI require special caution and clinical review.', self.section('skin-wound-image'))

    def test_each_modality_receives_shared_urgent_safety_rule(self):
        for module in ('pocus-image', 'ct-mri-screenshot', 'skin-wound-image', 'ecg-image', 'chest-xray'):
            with self.subTest(module=module):
                self.assertIn('No system output alone excludes urgent pathology.', self.section(module))

    def test_approved_r50_refinements_survive_loading(self):
        pocus = self.section('pocus-image')
        self.assertIn('rule-in philosophy', pocus)
        self.assertIn('archived for QA', pocus)
        skin = self.section('skin-wound-image')
        self.assertIn('before local anesthesia', skin)
        self.assertIn('stratified validation', skin)
        self.assertIn('not a universal contraindication', skin)
        self.assertIn('intact volumetric DICOM series', self.section('ct-mri-screenshot'))

    def test_parent_covers_abstention_and_no_image_based_prophylaxis(self):
        parent = self.section('clinical-image-interpretation')
        self.assertIn('absence of an alert and a technical Layer 7 abstention', parent)
        self.assertIn('Do not recommend empirical antibiotics or tetanus/rabies prophylaxis', parent)

    def test_evidence_parent_unchanged_and_yellow(self):
        record = json.loads((ROOT / 'references/evidence-registry.json').read_text())['modules']['clinical-image-interpretation']
        frozen = json.loads((ROOT.parent / 'docs/coordination/r54/literal/base/evidence-registry.json').read_text())
        self.assertEqual(record, frozen)
        self.assertEqual(record['status'], 'yellow')
        self.assertEqual(record['last_checked'], '2026-09-17')

    def test_literal_artifacts_have_recorded_hashes(self):
        evidence = ROOT.parent / 'docs/coordination/r54'
        for artifact in json.loads((evidence / 'ARTIFACTS.json').read_text())['artifacts']:
            with self.subTest(path=artifact['path']):
                self.assertEqual(hashlib.sha256((ROOT.parent / artifact['path']).read_bytes()).hexdigest(), artifact['sha256'])

    def test_both_medical_authorizations_are_approved(self):
        record = json.loads((ROOT / 'qa/R54_MEDICAL_OWNER_DECISIONS_20261124.json').read_text())
        self.assertEqual(record['authorization_date'], '2026-11-24')
        self.assertEqual({d['id'] for d in record['decisions']}, {'MED-DEC-R46-01', 'MED-DEC-R46-02'})
        self.assertTrue(all(d['status'] == 'APPROVED_MEDICAL_OWNER' for d in record['decisions']))
