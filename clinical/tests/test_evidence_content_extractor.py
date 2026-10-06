import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evidence_content_extractor import canonical_text,clinical_fingerprint
class ExtractionTests(unittest.TestCase):
 def test_navigation_noise_removed(self):
  a=b"<html><nav>Menu version 1</nav><main><p>Guideline recommendation: give treatment A.</p></main></html>"
  b=b"<html><nav>Menu version 2</nav><main><p>Guideline recommendation: give treatment A.</p></main></html>"
  self.assertEqual(clinical_fingerprint(a)["sha256"],clinical_fingerprint(b)["sha256"])
 def test_clinical_change_detected(self):
  a=b"<html><main><p>Guideline recommendation: treatment A is indicated.</p></main></html>"
  b=b"<html><main><p>Guideline recommendation: treatment B is indicated.</p></main></html>"
  self.assertNotEqual(clinical_fingerprint(a)["sha256"],clinical_fingerprint(b)["sha256"])
 def test_scripts_do_not_pollute(self):
  x=canonical_text(b"<html><script>dose=999</script><p>Safety recommendation remains unchanged.</p></html>")
  self.assertNotIn("999",x)
if __name__=="__main__":unittest.main()
