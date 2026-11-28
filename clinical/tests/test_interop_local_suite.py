"""Run the synthetic interchange contracts in the existing QA/coverage pipeline."""
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'tools' / 'interop-local'


def load_tests(loader, tests, pattern):
    """Load actual laboratory tests; do not duplicate their assertions."""
    previous = sys.modules.get('interop_lab')
    spec = importlib.util.spec_from_file_location('interop_lab', LAB / 'interop_lab.py')
    implementation = importlib.util.module_from_spec(spec)
    sys.modules['interop_lab'] = implementation
    try:
        spec.loader.exec_module(implementation)
        test_spec = importlib.util.spec_from_file_location(
            '_emergency_interop_local_tests', LAB / 'test_interop_lab.py')
        test_module = importlib.util.module_from_spec(test_spec)
        test_spec.loader.exec_module(test_module)
        return loader.loadTestsFromModule(test_module)
    finally:
        if previous is None:
            sys.modules.pop('interop_lab', None)
        else:
            sys.modules['interop_lab'] = previous


if __name__ == '__main__':
    unittest.main()
