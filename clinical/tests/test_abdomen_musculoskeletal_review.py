"""Guard against dangerous reassurance and blanket rules in adult triage guides."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load


class AbdominalMusculoskeletalSafetyTests(unittest.TestCase):
    def test_abdomen_does_not_defer_source_control_or_reassure_from_one_test(self):
        text = ' '.join(load(ROOT, 'acute-abdomen').split())
        for safety_boundary in (
            'do not wait for all tests before calling for shock or peritonitis',
            'normal lactate does not exclude early mesenteric ischemia',
            'this is not a universal CT prescription',
            'negative POCUS does not exclude rupture or ischemia',
            'not routine conservative waiting',
            'improvement after analgesia alone does not establish benign disease',
            'written return instructions',
        ):
            with self.subTest(boundary=safety_boundary):
                self.assertIn(safety_boundary, text)

    def test_musculoskeletal_separates_minor_injury_from_limb_and_sepsis_threats(self):
        text = ' '.join(load(ROOT, 'acute-musculoskeletal-pain').split())
        for safety_boundary in (
            'normal pulses do not exclude compartment syndrome',
            'do not delay for routine imaging',
            'without waiting for aspiration',
            'Crystals or normal blood inflammatory markers do not exclude infection',
            'only in eligible patients',
            'does not exclude an occult fracture',
            'acute non-low-back musculoskeletal injuries in adults',
            'Avoid opioids, including tramadol, as routine first-line treatment',
            'no unresolved limb/systemic red flags',
        ):
            with self.subTest(boundary=safety_boundary):
                self.assertIn(safety_boundary, text)


if __name__ == '__main__':
    unittest.main()
