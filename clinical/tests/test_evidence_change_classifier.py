import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_change_classifier import classify,map_modules
from urgent_safety_triage import urgent_items
class EvidenceTriageTests(unittest.TestCase):
 def test_urgent_safety_never_auto_applies(self):
  r=classify("Urgent medicine safety alert: contraindication")
  self.assertEqual("urgent-safety",r["classification"]);self.assertFalse(r["auto_apply"]);self.assertTrue(r["requires_human_review"])
 def test_domain_mapping_is_deterministic(self):
  mods=[{"id":"a","domains":["cardiology"]},{"id":"b","domains":["neurology"]}]
  self.assertEqual(["a"],map_modules(["cardiology"],mods))
 def test_urgent_queue_filters(self):
  r={"review_queue":[{"source_id":"a","classification":"urgent-safety"},{"source_id":"b","classification":"untriaged"}]}
  x=urgent_items(r);self.assertEqual(1,len(x));self.assertFalse(x[0]["auto_apply"])
if __name__=="__main__":unittest.main()
