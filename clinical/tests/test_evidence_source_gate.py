import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_source_gate import assess_source
class GateTests(unittest.TestCase):
 def test_pending_official_source_can_signal_not_propose(self):
  r=assess_source({"url":"https://www.infarmed.pt/","authority_type":"medicines-regulator","validation_status":"official-authority-confirmed-specific-current-index-pending"})
  self.assertTrue(r["review_signal_allowed"]);self.assertFalse(r["eligible_for_clinical_change_proposal"]);self.assertFalse(r["auto_apply"])
 def test_unapproved_source_fails_closed(self):
  r=assess_source({"url":"https://blog.example/","authority_type":"blog"})
  self.assertFalse(r["trusted_for_surveillance"]);self.assertFalse(r["eligible_for_clinical_change_proposal"])
if __name__=="__main__":unittest.main()
