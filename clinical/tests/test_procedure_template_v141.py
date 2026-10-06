import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_procedure_template_v141 import validate
class ProcedureTemplateV141(unittest.TestCase):
 def test_normalized_families_complete(self):
  r=validate()
  self.assertEqual(56,r["normalized_cards"])
  self.assertEqual([],r["errors"],"\n".join(r["errors"]))
if __name__=="__main__":unittest.main()
