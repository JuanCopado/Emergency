"""Project decision and evidence must refer to the exact module under review."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from final_human_review_gate import POLICY, build_review_queue, can_promote


class OwnerDecisionTests(unittest.TestCase):
    def test_queue_requires_single_clinical_reviewer(self):
        for row in build_review_queue()["queue"]:
            self.assertIn("clinical", row["required_reviews"])
            self.assertNotIn("pharmacy", row["required_reviews"])
            self.assertEqual(row["clinical_decision_owner"], POLICY["clinical_decision_owner"])

    def test_only_explicit_approval_for_the_reviewed_dossier_is_eligible(self):
        item = dict(module_id="synthetic", status="PASS", evidence_ref="dossier-v2",
                    qa_after_review="PASS")
        self.assertFalse(can_promote(item))
        decision = dict(module_id="synthetic", approved=True, evidence_ref="dossier-v2",
                        reviewer=POLICY["clinical_decision_owner"], date="2026-11-20")
        self.assertTrue(can_promote(dict(item, owner_decision=decision)))
        for change in (dict(approved=False), dict(approved="yes"), dict(date=""),
                       dict(reviewer="another reviewer"), dict(module_id="other"),
                       dict(evidence_ref="dossier-v1")):
            with self.subTest(change=change):
                self.assertFalse(can_promote(dict(item, owner_decision=decision | change)))
        self.assertFalse(can_promote(dict(item, owner_decision=decision, qa_after_review="FAIL")))
