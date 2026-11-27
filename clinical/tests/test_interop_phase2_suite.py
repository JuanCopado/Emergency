"""Discover phase-two synthetic exchange tests in the existing QA/coverage runner."""
import importlib.util
import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parents[2] / "tools" / "interop-local"


def load_tests(loader, tests, pattern):
    previous = {name: sys.modules.get(name) for name in ("interop_lab", "interop_phase2")}
    try:
        for name in previous:
            spec = importlib.util.spec_from_file_location(name, LAB / (name+".py"))
            implementation = importlib.util.module_from_spec(spec)
            sys.modules[name] = implementation
            spec.loader.exec_module(implementation)
        test_spec = importlib.util.spec_from_file_location(
            "_emergency_interop_phase2_tests", LAB / "test_interop_phase2.py")
        test_module = importlib.util.module_from_spec(test_spec)
        test_spec.loader.exec_module(test_module)
        return loader.loadTestsFromModule(test_module)
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


if __name__ == "__main__":
    unittest.main()
