import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_clinical_diff import structured_diff
class ClinicalDiffTests(unittest.TestCase):
 def test_dose_change_high(self):
  r=structured_diff("Recommended dose 5 mg daily","Recommended dose 10 mg daily")
  self.assertIn("dose_change",r["categories"]);self.assertEqual("high",r["priority"]);self.assertFalse(r["auto_apply"])
 def test_new_contraindication_critical(self):
  r=structured_diff("Treatment recommended","Treatment recommended\nNew contraindication in severe renal failure")
  self.assertIn("contraindication_change",r["categories"]);self.assertEqual("critical",r["priority"])
 def test_withdrawal_critical(self):
  r=structured_diff("Drug A recommended","Drug A no longer recommended")
  self.assertIn("withdrawal_change",r["categories"]);self.assertEqual("critical",r["priority"])
 def test_cosmetic_change_low(self):
  r=structured_diff("Updated January","Updated February")
  self.assertEqual({},r["categories"]);self.assertEqual("low",r["priority"])
if __name__=="__main__":unittest.main()
