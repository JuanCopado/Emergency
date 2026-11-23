"""R27 · alt-b-0.2 strict adapter: reversible fields, blocking errors for ambiguity, no mutation, alt-b-0.1 untouched."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
from human_factors import alt_b, alt_b_v02 as v02, dryrun, bank_r23 as bank  # noqa: E402

MANIFEST = bank.build_manifest()
RECORDS, _ = dryrun.run(MANIFEST, count=4)
GOOD_EXTRAS = {"viewport_width": 360, "outcome_events": ["submit_clicked"], "entry_flow": "prototype_selector", "transport_mode": "base64_json"}


class Adapter(unittest.TestCase):
    def test_historical_records_are_never_mutated(self):
        before = copy.deepcopy(RECORDS)
        for r in RECORDS[:20]:
            try:
                v02.upgrade_record(r, GOOD_EXTRAS, allow_inferred=True)
            except v02.AmbiguousConversion:
                pass
        self.assertEqual(RECORDS, before)

    def test_reversible_fields_round_trip(self):
        r = next(x for x in RECORDS if x["device_type"] == "desktop_web")
        up = v02.upgrade_record(r, GOOD_EXTRAS, allow_inferred=True)
        back = v02.downgrade_reversible_fields(up)
        self.assertEqual(back, {k: r[k] for k in ("arm", "mechanism_id", "language_stratum", "role_group")})
        for field, (table, _) in v02.CROSSWALK.items():
            self.assertEqual(len(set(table.values())), len(table), field)         # bijective

    def test_target_vocabulary_is_the_quoted_one(self):
        self.assertEqual(v02.CROSSWALK["arm"][0], {"A": "A_legacy", "B": "B_prototype_alt_b"})
        self.assertEqual(set(v02.CROSSWALK["mechanism_id"][0].values()), {"M1_bypass_selection", "M2_layer7_abstention", "M3_valid_non_interference"})
        self.assertEqual(v02.CROSSWALK["language_stratum"][0]["pt-BR"], "pt-BR")           # pt-PT and pt-BR stay distinct
        self.assertNotEqual(v02.CROSSWALK["language_stratum"][0]["pt-PT"], v02.CROSSWALK["language_stratum"][0]["pt-BR"])
        self.assertEqual(v02.DEVICE_VIEWPORTS, {360: "mobile_narrow_360", 390: "mobile_narrow_390"})

    def test_role_group_is_blocked_until_the_inferred_mapping_is_confirmed(self):
        with self.assertRaisesRegex(v02.AmbiguousConversion, "role_group"):
            v02.upgrade_record(RECORDS[0], GOOD_EXTRAS)
        self.assertEqual(v02.CROSSWALK["role_group"][1], v02.INFERRED)

    def test_mobile_without_viewport_is_blocked_and_360_390_are_kept_apart(self):
        mobile = next(x for x in RECORDS if x["device_type"] == "mobile_narrow")
        with self.assertRaisesRegex(v02.AmbiguousConversion, "device_type"):
            v02.upgrade_record(mobile, {k: v for k, v in GOOD_EXTRAS.items() if k != "viewport_width"}, allow_inferred=True)
        with self.assertRaises(v02.AmbiguousConversion):
            v02.upgrade_record(mobile, dict(GOOD_EXTRAS, viewport_width=375), allow_inferred=True)
        a = v02.upgrade_record(mobile, dict(GOOD_EXTRAS, viewport_width=360), allow_inferred=True)
        b = v02.upgrade_record(mobile, dict(GOOD_EXTRAS, viewport_width=390), allow_inferred=True)
        self.assertEqual((a["device_type"], b["device_type"]), ("mobile_narrow_360", "mobile_narrow_390"))

    def test_coarse_outcomes_are_never_promoted_without_events(self):
        for outcome in alt_b.OUTCOMES:
            r = next((x for x in RECORDS if x["outcome_status"] == outcome), None)
            if r is None:
                continue
            with self.assertRaises(v02.AmbiguousConversion):
                v02.upgrade_record(r, dict(GOOD_EXTRAS, outcome_events=[]), allow_inferred=True)
            up = v02.upgrade_record(r, GOOD_EXTRAS, allow_inferred=True)
            self.assertEqual(up["outcome_status_v01"], outcome)                    # preserved
            self.assertIsNone(up["outcome_status"])                                # NOT converted to a specific category

    def test_missing_capture_fields_block(self):
        for missing in ("entry_flow", "transport_mode"):
            with self.assertRaisesRegex(v02.AmbiguousConversion, missing):
                v02.upgrade_record(RECORDS[0], {k: v for k, v in GOOD_EXTRAS.items() if k != missing}, allow_inferred=True)

    def test_unknown_values_and_open_records_are_rejected(self):
        bad = dict(RECORDS[0], arm="C")
        with self.assertRaises(v02.AmbiguousConversion):
            v02.upgrade_record(bad, GOOD_EXTRAS, allow_inferred=True)
        with self.assertRaises(v02.AmbiguousConversion):
            v02.upgrade_record(dict(RECORDS[0], extra_field=1), GOOD_EXTRAS, allow_inferred=True)

    def test_alt_b_0_1_stays_supported_and_unchanged(self):
        self.assertEqual(alt_b.SCHEMA_VERSION, "alt-b-0.1")
        self.assertEqual(alt_b.SUPPORTED_VERSIONS, ("alt-b-0.1",))
        alt_b.validate_records(RECORDS, MANIFEST)

    def test_report_states_what_is_blocked_and_never_claims_a_complete_table(self):
        rep = v02.crosswalk_report(RECORDS)
        self.assertEqual(rep["status"], "BLOCKED_PENDING_GEMINI_R26_TABLE")
        self.assertEqual(rep["blocked_without_extra_evidence"]["outcome_status"], len(RECORDS))
        self.assertEqual(rep["deterministic"]["arm"], len(RECORDS))
        self.assertEqual(rep["provenance"]["role_group"], v02.INFERRED)


if __name__ == "__main__":
    unittest.main()


class PartialConversionIsNeverCanonical(unittest.TestCase):
    def test_converted_record_is_partial_and_outcome_status_is_not_assigned(self):
        r = next(x for x in RECORDS if x["device_type"] == "desktop_web")
        up = v02.upgrade_record(r, GOOD_EXTRAS, allow_inferred=True)
        self.assertEqual(up["conversion_status"], "PARTIAL_NOT_CANONICAL_R27_V1")
        self.assertIsNone(up["outcome_status"])                       # no M/E state derived from completed/abandoned/blocked
        self.assertEqual(up["outcome_status_v01"], r["outcome_status"])
        with self.assertRaises(v02.AmbiguousConversion):              # HARD FAIL when the observed events are missing
            v02.upgrade_record(r, dict(GOOD_EXTRAS, outcome_events=[]), allow_inferred=True)
