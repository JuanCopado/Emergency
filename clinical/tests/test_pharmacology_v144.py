import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'qa'))
from run_pharmacology_v144 import run

class PharmacologyCoverageTests(unittest.TestCase):
    def test_all_source_examples_and_preparations_match_python_engine(self):
        report=run()
        self.assertEqual(report['adult']['drugs'],17)
        self.assertEqual(report['pediatric']['regimens'],89)
        self.assertEqual(len({c['preparation'] for c in report['adult_cases']}),report['adult']['preparations'])
        self.assertEqual(len({c['drug'] for c in report['adult_cases']}),17)
        self.assertEqual(report['clinical_status'],'CLINICALLY_PENDING')
