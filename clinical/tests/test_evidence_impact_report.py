import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_impact_report import build_impact
class ImpactTests(unittest.TestCase):
 def test_medication_change_requires_pharmacist(self):
  d={"priority":"critical","categories":{"dose_change":["x"]}}
  r=build_impact({"id":"ema","organization":"EMA","url":"https://example.test"},d,["drug-safety"])
  self.assertTrue(r["requires_pharmacist_review"]);self.assertFalse(r["clinical_change_authorized"]);self.assertEqual("pending_review",r["status"])
if __name__=="__main__":unittest.main()
