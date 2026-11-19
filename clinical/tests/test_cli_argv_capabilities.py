"""Real argv regression for every changed CLI path boundary; synthetic files only."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SALT = 'synthetic-argv-test-salt'
# Each path slot is attacked independently while every other path is valid.
COMMANDS = [
    ('clinical/qa/run_functional_v144.py', ['--output', 'O']),
    ('clinical/scripts/clinical_note_diagnostic_engine.py', ['I']),
    ('clinical/scripts/pediatric_antibiotic_calculator.py', ['SYNTHETIC', '20', '--registry', 'I', '--context-json', 'I']),
    ('clinical/scripts/pediatric_bolus_calculator.py', ['SYNTHETIC', '20', '--registry', 'I']),
    ('clinical/scripts/pediatric_pump_table.py', ['SYNTHETIC', '20', '--registry', 'I']),
    ('clinical/scripts/pediatric_outpatient_calculator.py', ['SYNTHETIC', 'I', '--product-json', 'I', '--active-medications-json', 'I']),
    ('clinical/scripts/pediatric_outpatient_alert_engine.py', ['SYNTHETIC', 'I', '--product-json', 'I', '--active-medications-json', 'I']),
    ('clinical/scripts/evidence_surveillance.py', ['--sources', 'I', '--previous', 'I', '--output', 'O']),
    ('clinical/scripts/urgent_safety_triage.py', ['I', '--output', 'O']),
    ('clinical/scripts/create_blinded_image_dataset.py', ['ecg', 'SYNTHETIC', 'Synthetic?', 'O']),
    ('clinical/scripts/create_blinded_prediction_template.py', ['I', 'O']),
    ('clinical/scripts/merge_blinded_prediction_shards.py', ['I', 'I', '--output', 'O']),
    ('clinical/scripts/finalize_blinded_image_dataset.py', ['I', 'I', 'I', 'O']),
    ('clinical/scripts/predict_ptbxl_afib_image_baseline.py', ['I', 'ID', 'O']),
    ('clinical/scripts/prepare_chexpert_expert_blinded_cohort.py', ['I', 'I', 'SYNTHETIC', 'OD', '--salt', SALT]),
    ('clinical/scripts/prepare_mimic_cxr_curated_blinded_cohort.py', ['I', 'I', 'SYNTHETIC', 'OD', '--salt', SALT]),
    ('clinical/scripts/prepare_rsna_ich_blinded_cohort.py', ['I', 'I', 'OD', '--salt', SALT]),
    ('clinical/scripts/prepare_ptbxl_blinded_cohort.py', ['I', 'SYNTHETIC', 'O', 'O', '--salt', SALT]),
    ('clinical/scripts/prepare_echonet_dynamic_blinded_cohort.py', ['I', 'OD', '--salt', SALT]),
    ('clinical/scripts/prepare_echonet_visual_input.py', ['I', 'OD']),
    ('clinical/scripts/render_rsna_ich_dicom.py', ['ID', 'OD', 'SYNTHETIC']),
    ('clinical/scripts/build_ptbxl_blinded_benchmark.py', ['I', 'SYNTHETIC', 'OD', '--salt', SALT]),
]


class CliArgvCapabilityTests(unittest.TestCase):
    def test_every_path_argument_rejects_escape_before_data_processing(self):
        extras = all(importlib.util.find_spec(name) is not None for name in ('wfdb', 'numpy', 'matplotlib'))
        required = os.getenv('EMERGENCY_REQUIRE_BENCHMARK_TESTS') == '1'
        if required: self.assertTrue(extras, 'CI must install the scientific wheels')
        exercised = 0
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); allowed = base/'allowed'; outside = base/'outside'
            allowed.mkdir(); outside.mkdir(); (allowed/'input-dir').mkdir()
            (allowed/'input.json').write_text('{}', encoding='utf-8')
            sentinel = outside/'sentinel.json'; sentinel.write_text('SYNTHETIC_UNCHANGED', encoding='utf-8')
            env = dict(os.environ, EMERGENCY_CLI_INPUT_ROOT=str(allowed), EMERGENCY_CLI_OUTPUT_ROOT=str(allowed),
                       PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
            inside = {'I': allowed/'input.json', 'ID': allowed/'input-dir',
                      'O': allowed/'output.json', 'OD': allowed/'output-dir'}
            for script, template in COMMANDS:
                if 'build_ptbxl_blinded_benchmark' in script and not extras:
                    continue  # Required and exercised in Linux security coverage CI.
                exercised += 1
                for index, slot in enumerate(template):
                    if slot not in inside: continue
                    args = [str(inside.get(value, value)) for value in template]
                    args[index] = str(outside if slot in {'ID', 'OD'} else sentinel)
                    with self.subTest(script=script, argument=index, kind=slot):
                        result = subprocess.run([sys.executable, str(ROOT/script), *args], cwd=ROOT,
                                                env=env, text=True, capture_output=True, timeout=30)
                        self.assertEqual(result.returncode, 2, result.stderr[-1500:])
                        self.assertIn('escapes the launcher workspace', result.stderr)
                        self.assertEqual(result.stdout, '')
                        self.assertFalse((allowed/'output.json').exists())
                        self.assertFalse((allowed/'output-dir').exists())
                        self.assertEqual(sentinel.read_text(), 'SYNTHETIC_UNCHANGED')
            self.assertEqual(exercised, 22 if extras else 21)


if __name__ == '__main__':
    unittest.main()
