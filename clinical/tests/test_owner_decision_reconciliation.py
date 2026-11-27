"""Prevent accepted owner scopes from becoming product or release permission."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from owner_decision_reconciliation import validate


class OwnerDecisionReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / "references/owner-decisions-2026-11-27.json").read_text(encoding="utf-8"))

    def test_current_reconciliation_accepts_only_recorded_scopes(self):
        self.assertEqual(validate(self.record, ROOT.parent), [])

    def test_historical_product_cannot_be_reactivated_or_substituted(self):
        for key, value in [("runtime_enabled", True), ("runtime_enabled", 0), ("replacement_product_id", "UNREVIEWED"),
                           ("jurisdiction", "GLOBAL"), ("classification", "ACTIVE")]:
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                record["protamine"][key] = value
                self.assertTrue(validate(record, ROOT.parent))

    def test_historical_strict_limit_cannot_become_inclusive(self):
        self.record["protamine"]["historical_rate_limit"]["operator"] = "<="
        self.assertIn("protamine: historical limit changed", validate(self.record, ROOT.parent))

    def test_another_fiche_cannot_inherit_the_protamine_acceptance(self):
        self.record["protamine"]["original_fiche_sha256"] = "0" * 64
        self.assertIn("protamine: original fiche changed", validate(self.record, ROOT.parent))

    def test_dermatology_acceptance_cannot_grant_publication_or_diagnostic_validation(self):
        for key in ("redistribution_authorized", "product_incorporation_authorized", "diagnostic_validation"):
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                record["dermatology"]["cases"][0][key] = True
                self.assertTrue(validate(record, ROOT.parent))

    def test_duplicate_dermatology_vote_does_not_replace_a_case(self):
        self.record["dermatology"]["cases"][-1] = copy.deepcopy(self.record["dermatology"]["cases"][0])
        self.assertIn("dermatology: case identities differ from decision record", validate(self.record, ROOT.parent))

    def test_representativeness_only_does_not_become_development_permission(self):
        self.record["dermatology"]["cases"][1]["scope_kind"] = "CONSULTATION_DEVELOPMENT_ONLY"
        self.assertIn("dermatology: recorded case scope changed", validate(self.record, ROOT.parent))

    def test_summary_is_not_an_original_cardiovascular_fiche(self):
        self.record["cardiovascular"][0]["implementation_status"] = "IMPLEMENTED"
        self.assertIn("cardiovascular: original fiches not verified", validate(self.record, ROOT.parent))

    def test_visual_approval_does_not_deploy_the_prototype(self):
        self.record["clinical_minimal"]["deployed"] = True
        self.assertIn("clinical-minimal: approval scope widened", validate(self.record, ROOT.parent))

    def test_technical_reconciliation_does_not_grant_release(self):
        self.record["clinical_status"] = "VALIDATED"
        self.assertIn("release: CLINICALLY_PENDING required", validate(self.record, ROOT.parent))
