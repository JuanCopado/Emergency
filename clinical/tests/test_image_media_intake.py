"""Admission cannot silently turn teaching images into diagnostic evidence."""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_image_media_intake import validate


class ImageMediaIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'one.png').write_bytes(b'synthetic file-integrity fixture, not a clinical image')
        payload = (self.root / 'one.png').read_bytes()
        self.row = dict(id='one', source_case_group_id='same-patient-group', modality='chest_xray',
                        source_page='https://example.org/case', author='Fixture', license='CC0',
                        license_url='https://creativecommons.org/publicdomain/zero/1.0/',
                        license_checked='2026-11-14', file='one.png', size_bytes=len(payload),
                        sha256=hashlib.sha256(payload).hexdigest(), metrics_eligible=False,
                        dataset_class='teaching_source_known', split='teaching_development',
                        training_performed=False)
        self.data = dict(dataset_class='teaching_source_known', metrics_eligible=False,
                         metrics_requested=False, external_inference_performed=False,
                         media_count=1, source_case_groups=1, items=[self.row])

    def test_source_known_case_never_reports_accuracy_or_training(self):
        report = validate(self.data, self.root)
        self.assertEqual(report['errors'], [])
        self.assertFalse(report['metrics_eligible'])
        self.assertFalse(report['training_performed'])

    def test_corrupt_or_replaced_bytes_are_rejected(self):
        (self.root / 'one.png').write_bytes(b'replaced')
        self.assertTrue(validate(self.data, self.root)['errors'])

    def test_path_outside_batch_is_rejected(self):
        self.row['file'] = '../outside.png'
        self.assertTrue(any('escapes' in e for e in validate(self.data, self.root)['errors']))

    def test_copy_cannot_be_counted_as_a_second_independent_case(self):
        duplicate = copy.deepcopy(self.row)
        duplicate['id'] = 'two'
        duplicate['source_case_group_id'] = 'pretend-new-patient'
        self.data.update(items=[self.row, duplicate], media_count=2, source_case_groups=2)
        self.assertTrue(any('duplicate binary' in e for e in validate(self.data, self.root)['errors']))

    def test_two_views_can_share_one_case_without_inflating_patient_count(self):
        (self.root / 'two.png').write_bytes(b'different synthetic view')
        row = copy.deepcopy(self.row)
        row.update(id='two', file='two.png', size_bytes=24,
                   sha256=hashlib.sha256(b'different synthetic view').hexdigest())
        self.data.update(items=[self.row, row], media_count=2)
        self.assertEqual(validate(self.data, self.root)['errors'], [])
        self.assertEqual(validate(self.data, self.root)['source_case_groups'], 1)

    def test_accuracy_promotion_and_test_contamination_are_blocked(self):
        self.data['metrics_eligible'] = True
        self.row['split'] = 'held_out_test'
        self.row['dataset_class'] = 'blinded_accuracy'
        self.assertGreaterEqual(len(validate(self.data, self.root)['errors']), 3)


if __name__ == '__main__':
    unittest.main()
