import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ProcedureCardQualityTest(unittest.TestCase):
    def test_structural_validator_has_no_errors(self):
        path=ROOT/"scripts"/"validate_procedure_cards_v141.py"
        spec=importlib.util.spec_from_file_location("procval",path)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        report=mod.validate()
        self.assertEqual([], report["errors"], "\n".join(report["errors"]))

if __name__=="__main__":
    unittest.main()
