import json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_visual_asset_metadata import validate

class VisualAssetMetadataTests(unittest.TestCase):
    def test_unknown_license_fails_for_final_reuse(self):
        data={"assets":[{"procedure_id":"PROC-AIR-001","source_url":"https://example.test/x","source_title":"x","source_organization":"x","license":"unknown","attribution_text":"x","intended_use":"final_reuse","clinical_qa_status":"pending","visual_qa_status":"pending"}]}
        self.assertTrue(validate(data))
    def test_reference_use_with_complete_metadata_passes(self):
        data={"assets":[{"procedure_id":"PROC-AIR-001","source_url":"https://example.test/x","source_title":"x","source_organization":"x","license":"all-rights-reserved","attribution_text":"x","intended_use":"anatomical_reference","clinical_qa_status":"pending","visual_qa_status":"pending"}]}
        self.assertEqual([],validate(data))
if __name__=="__main__": unittest.main()
