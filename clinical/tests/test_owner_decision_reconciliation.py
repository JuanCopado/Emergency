"""Prevent accepted owner scopes from becoming product or release permission."""
import copy
import json
import os
import subprocess
import sys
import tempfile
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

    def test_verified_originals_survive_git_checkout_with_autocrlf(self):
        import hashlib
        expected = {
            self.record["decision_source"]: self.record["decision_source_sha256"],
            self.record["protamine"]["original_fiche"]: self.record["protamine"]["original_fiche_sha256"],
        }
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1",
                   GIT_CONFIG_GLOBAL="NUL" if os.name == "nt" else os.devnull)
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary)
            (checkout / ".gitattributes").write_bytes((ROOT.parent / ".gitattributes").read_bytes())
            for relative in expected:
                path = checkout / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT.parent / relative).read_bytes())

            def git(*args):
                subprocess.run(["git", "-C", temporary, *args], env=env, check=True, capture_output=True)

            git("init", "-q")
            git("config", "core.autocrlf", "false")
            git("add", ".")
            git("-c", "user.name=Synthetic QA", "-c", "user.email=qa@example.invalid", "commit", "-qm", "checkout fixture")
            git("config", "core.autocrlf", "true")
            for relative in expected:
                (checkout / relative).unlink()
            git("checkout", "HEAD", "--", *expected)
            for relative, digest in expected.items():
                with self.subTest(relative=relative):
                    self.assertEqual(hashlib.sha256((checkout / relative).read_bytes()).hexdigest(), digest)

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

    def test_protamine_acceptance_cannot_be_assigned_to_another_decision(self):
        for key, value in [("id", "OTHER"), ("decided_at_utc", "2026-11-26T06:14:21Z")]:
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                record["protamine"][key] = value
                self.assertTrue(validate(record, ROOT.parent))

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

    def test_cardiovascular_acceptance_cannot_bind_a_different_scope_or_version(self):
        for key, value in [("version", "v2"), ("decided_at_utc", "2026-11-26T06:12:33Z"),
                           ("scope_summary", "UNIVERSAL_TREATMENT"), ("canonical_modules", ["acute-coronary-syndrome"]),
                           ("pending_kind", "MEDICAL_APPROVAL_MISSING")]:
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                record["cardiovascular"][0][key] = value
                self.assertTrue(validate(record, ROOT.parent))

    def test_visual_approval_does_not_deploy_the_prototype(self):
        self.record["clinical_minimal"]["deployed"] = True
        self.assertIn("clinical-minimal: approval scope widened", validate(self.record, ROOT.parent))

    def test_visual_acceptance_cannot_be_reassigned_or_lost(self):
        for key, value in [("response", "NO"), ("scope", "PUBLIC_DEPLOYMENT"),
                           ("decided_at_utc", "2026-11-26T06:37:53Z")]:
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                record["clinical_minimal"][key] = value
                self.assertTrue(validate(record, ROOT.parent))

    def test_technical_record_does_not_invent_independent_review(self):
        self.record["independent_review"]["review_status"] = "FAVORABLE"
        self.assertTrue(validate(self.record, ROOT.parent))

    def test_inventory_is_not_an_adjudicated_or_physically_reconciled_bank(self):
        for key, value in [("experimental_adjudications", 1), ("per_asset_file_hashes_reconciled", True)]:
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                record["dermatology"][key] = value
                self.assertTrue(validate(record, ROOT.parent))

    def test_technical_reconciliation_does_not_grant_release(self):
        self.record["clinical_status"] = "VALIDATED"
        self.assertIn("release: CLINICALLY_PENDING required", validate(self.record, ROOT.parent))
