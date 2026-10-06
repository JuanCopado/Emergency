import json, pathlib, sys, tempfile, unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import evidence_surveillance as es

class EvidenceSurveillanceTests(unittest.TestCase):
    def config(self,td):
        p=pathlib.Path(td)/"s.json"; p.write_text(json.dumps({"sources":[{"id":"x","organization":"X","url":"https://example.test","cadence":"weekly","authority_type":"formal-guideline-body"}]})); return p
    def test_first_observation_does_not_claim_change(self):
        with tempfile.TemporaryDirectory() as td, patch.object(es,"fetch",return_value=b"abc"):
            r=es.run(self.config(td)); self.assertTrue(r["sources"]["x"]["first_observation"]); self.assertFalse(r["sources"]["x"]["changed"]); self.assertEqual([],r["review_queue"]); self.assertFalse(r["production_changes_applied"])
    def test_change_creates_review_only(self):
        with tempfile.TemporaryDirectory() as td, patch.object(es,"fetch",return_value=b"new"):
            r=es.run(self.config(td),{"sources":{"x":{"sha256":es.digest(b"old")}}}); self.assertTrue(r["sources"]["x"]["changed"]); self.assertTrue(r["review_queue"][0]["requires_human_review"]); self.assertFalse(r["production_changes_applied"])
    def test_failure_is_explicit_not_no_change(self):
        with tempfile.TemporaryDirectory() as td, patch.object(es,"fetch",side_effect=RuntimeError("offline")):
            r=es.run(self.config(td)); self.assertEqual("error",r["sources"]["x"]["status"]); self.assertNotIn("changed",r["sources"]["x"])
if __name__=="__main__": unittest.main()
