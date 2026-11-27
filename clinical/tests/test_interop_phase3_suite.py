"""Include synthetic phase-three exchange regressions in existing clinical QA discovery."""
import importlib.util
import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parents[2] / "tools" / "interop-local"


def load_tests(loader, tests, pattern):
    names = ("interop_lab", "interop_phase2", "interop_phase3")
    previous = {name: sys.modules.get(name) for name in names}
    try:
        for name in names:
            spec = importlib.util.spec_from_file_location(name, LAB / (name+".py"))
            implementation = importlib.util.module_from_spec(spec)
            sys.modules[name] = implementation
            spec.loader.exec_module(implementation)
        spec = importlib.util.spec_from_file_location(
            "_emergency_interop_phase3_tests", LAB / "test_interop_phase3.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return loader.loadTestsFromModule(module)
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


if __name__ == "__main__":
    unittest.main()
