import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_review_pipeline import evaluate_change
class PipelineE2E(unittest.TestCase):
 def test_dose_safety_change_routes_but_never_applies(self):
  src={"id":"reg","organization":"Regulator","url":"https://example.test","domains":["medication-safety"]}
  mods=[{"id":"medication-selection-safety","domains":["medication-safety"]},{"id":"cardiology","domains":["cardiology"]}]
  r=evaluate_change(src,"Recommended dose 5 mg daily","Safety warning: recommended dose 2.5 mg daily",mods)
  self.assertEqual("critical",r["diff"]["priority"])
  self.assertIn("medication-selection-safety",r["impact"]["candidate_module_ids"])
  self.assertTrue(r["impact"]["requires_pharmacist_review"])
  self.assertFalse(r["impact"]["clinical_change_authorized"])
  self.assertFalse(r["invariants"]["production_mutation"])
 def test_nonclinical_text_never_authorizes_change(self):
  src={"id":"x","organization":"X","url":"https://example.test","domains":[]}
  r=evaluate_change(src,"Updated January","Updated February",[])
  self.assertEqual("low",r["diff"]["priority"]);self.assertFalse(r["invariants"]["auto_apply"])
if __name__=="__main__":unittest.main()
