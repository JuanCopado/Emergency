"""R41 · PR89 clean integration: verify every physical stimulus through canonical-r27-v1.2."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))

import canonical_r27_v12 as canonical  # noqa: E402
from canonical_r27_v1 import CanonicalViolation  # noqa: E402


class R41BankCanonicalV12(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = canonical.load_manifest()
        cls.present = {sid: entry for sid, entry in cls.manifest.items() if entry.get("file")}
        cls.pending = {sid: entry for sid, entry in cls.manifest.items() if not entry.get("file")}

    def test_inventory_is_explicitly_ten_present_twenty_pending(self):
        self.assertEqual((len(self.manifest), len(self.present), len(self.pending)), (30, 10, 20))

    def test_all_present_stimuli_verify_against_real_bytes(self):
        for stimulus_id in sorted(self.present):
            with self.subTest(stimulus_id=stimulus_id):
                verified = canonical.verified_stimulus(stimulus_id, self.manifest)
                self.assertEqual(verified["sha256"], self.present[stimulus_id]["sha256"])

    def test_pending_positions_fail_closed(self):
        for stimulus_id in sorted(self.pending):
            with self.subTest(stimulus_id=stimulus_id):
                with self.assertRaises(CanonicalViolation):
                    canonical.verified_stimulus(stimulus_id, self.manifest)

    def test_no_medical_adjudication_or_freeze_is_claimed(self):
        for entry in self.manifest.values():
            self.assertEqual(entry["clinical_adjudication_status"], "PENDING_CLINICAL_ADJUDICATION")
            self.assertEqual(entry["clinical_adjudicator_signoff"], "PENDING")
            self.assertFalse(entry["review_controls"]["freeze_seal_eligible"])


if __name__ == "__main__":
    unittest.main()
