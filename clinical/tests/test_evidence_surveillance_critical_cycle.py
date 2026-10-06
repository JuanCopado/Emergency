import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_review_pipeline import evaluate_change
from urgent_safety_triage import urgent_items

class CriticalCycleTests(unittest.TestCase):
 def test_baseline_to_critical_safety_change_is_review_only(self):
  source={"id":"regulator","organization":"Medicines Regulator","url":"https://example.test","domains":["medication-safety"]}
  modules=[{"id":"medication-selection-safety","domains":["medication-safety"]}]
  old="Guideline recommendation: Drug A dose 10 mg daily."
  new="Safety alert: Drug A dose 5 mg daily. New contraindication in severe renal failure."
  result=evaluate_change(source,old,new,modules)
  self.assertEqual("critical",result["diff"]["priority"])
  self.assertEqual("urgent-safety",result["triage"]["classification"])
  self.assertIn("medication-selection-safety",result["impact"]["candidate_module_ids"])
  self.assertTrue(result["impact"]["requires_pharmacist_review"])
  self.assertTrue(result["impact"]["requires_clinician_review"])
  self.assertTrue(result["impact"]["qa_required"])
  self.assertFalse(result["impact"]["clinical_change_authorized"])
  self.assertFalse(result["invariants"]["production_mutation"])
  queue=urgent_items({"review_queue":[{"source_id":"regulator",**result["triage"]}]})
  self.assertEqual(1,len(queue));self.assertFalse(queue[0]["auto_apply"])

if __name__=="__main__":unittest.main()
