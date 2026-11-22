"""R10 · M10 R5-1 Phase A: record how the category was reached and which filename hints matched.

DATA ONLY. Routing, confidence, abstention, the provider request and every clinical output are
unchanged. `kind_assessment` never verifies the real modality: RGB, EXIF or a missing DICOM header
are not used, because a camera photo can legitimately show an ECG, a radiograph or a POCUS screen.
Synthetic images and names only; no provider.
"""
import base64
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import synthetic_images as si  # noqa: E402
import clinical_note_api as api  # noqa: E402
import image_upload_guard  # noqa: E402

ENV = {"CLINICAL_VISION_PROVIDER_URL": "https://vision.example.test"}


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


def legacy_infer(filename, mime_type=None, explicit_kind=None):
    """Frozen copy of the routing chain as merged in 432da13 (before the rule table)."""
    if explicit_kind:
        return str(explicit_kind).strip().lower(), "explicit"
    name = image_upload_guard.clean_filename(filename).lower()
    mime = str(mime_type or "").lower()
    if any(x in name for x in ("ecg", "ekg", "electrocard")):
        return "ecg", "inferred_from_filename"
    if any(x in name for x in ("gasometr", "blood_gas", "abg", "vbg")):
        return "blood_gas", "inferred_from_filename"
    if any(x in name for x in ("microbi", "culture", "cultivo", "hemocult")):
        return "microbiology", "inferred_from_filename"
    if any(x in name for x in ("laborat", "analit", "analyt", "hemogram", "bioq")):
        return "laboratory_report", "inferred_from_filename"
    if any(x in name for x in ("pocus", "ultrasound", "ecografia", "ultrasom")):
        return "pocus", "inferred_from_filename"
    if any(x in name for x in ("ct_", "ct-", "tac", "tc_", "tc-", "mri", "rm_")):
        return "ct", "inferred_from_filename"
    if any(x in name for x in ("xray", "x-ray", "radiogr", "_rx", "rx_")):
        return "xray", "inferred_from_filename"
    if any(x in name for x in api.SKIN_WOUND_NAME_HINTS):
        return "skin_wound", "inferred_from_filename"
    if name.endswith(".dcm") or "dicom" in mime:
        return "other_image", "inferred_from_container"
    if name.endswith(".pdf") or mime == "application/pdf":
        return "pdf_document", "inferred_from_container"
    return "other_image", "default_unclassified"


def candidate_names():
    names = ["herida_pierna.png", "dermatitis_contacto.png", "IMG_1234.jpg", "foto.png", "lesion_rx_01.png",
             "piel_tac.png", "rash_abdomen.png", "DSC0042.jpg", "ecg_01.png", "informe.pdf", "serie.dcm",
             "gasometria.png", "ulcera_pie_rm_03.png", "QUEMADURA_mano.JPG", "x-ray_torax.png", "pocus_fast.mp4",
             "hemocultivo.pdf", "analitica.pdf", "a" * 80 + ".png"]
    for _, hints in api.NAME_HINT_RULES:
        for hint in hints:
            names += [f"{hint}.png", f"pre_{hint}_post.jpg", f"{hint.upper()}.PNG"]
    for left in ("ecg", "tac", "rx_", "piel", "pocus"):
        for right in ("piel", "tac", "xray", "herida", "ecg"):
            names.append(f"{left}_{right}.png")
    return names


def outcome(function, *args):
    try:
        return ("ok", function(*args))
    except Exception as exc:  # noqa: BLE001 - equivalence also covers identical failures
        return ("raises", type(exc).__name__, str(exc))


class RoutingEquivalence(unittest.TestCase):
    def test_invalid_names_fail_exactly_as_before(self):
        for name in ("", "..", "."):
            for explicit in (None, "skin_wound"):
                with self.subTest(name=name, explicit=explicit):
                    self.assertEqual(outcome(api.infer_attachment_kind_with_source, name, None, explicit),
                                     outcome(legacy_infer, name, None, explicit))

    def test_rule_table_is_identical_to_the_previous_chain(self):
        count = 0
        for name in candidate_names():
            for mime in (None, "image/png", "application/pdf", "application/dicom"):
                for explicit in (None, "", "skin_wound", " XRAY ", "other_image", "ecg"):
                    with self.subTest(name=name, mime=mime, explicit=explicit):
                        self.assertEqual(api.infer_attachment_kind_with_source(name, mime, explicit),
                                         legacy_infer(name, mime, explicit))
                        count += 1
        self.assertGreater(count, 2000)

    def test_hint_categories_follow_the_routing_order_and_do_not_decide(self):
        self.assertEqual(api.name_hint_categories("dermatitis_contacto.png"), ["ct", "skin_wound"])
        self.assertEqual(api.name_hint_categories("IMG_1234.jpg"), [])
        for name in candidate_names():
            hints = api.name_hint_categories(name)
            kind, source = api.infer_attachment_kind_with_source(name)
            if source == "inferred_from_filename":
                self.assertEqual(kind, hints[0])
            else:
                self.assertEqual(hints, [])


class Assessment(unittest.TestCase):
    def check(self, name, kind, source, explicit, hints, discordance, codes):
        got = api.kind_assessment(name, kind, source, explicit)
        self.assertEqual(got, {"kind_explicit": explicit, "name_hints_matched": hints,
                               "modality_verification": "not_verified",
                               "kind_discordance": discordance, "suspicion_codes": codes})

    def test_cases(self):
        self.check("herida.png", "skin_wound", "inferred_from_filename", None, ["skin_wound"], "none", [])
        self.check("dermatitis_contacto.png", "ct", "inferred_from_filename", None, ["ct", "skin_wound"],
                   "suspected", ["skin_name_hint_not_effective", "multiple_name_hints"])
        self.check("herida.png", "xray", "explicit", "xray", ["skin_wound"], "suspected",
                   ["skin_name_hint_not_effective", "explicit_differs_from_name_hint"])
        self.check("herida.png", "skin_wound", "explicit", "skin_wound", ["skin_wound"], "none", [])
        self.check("IMG_1234.jpg", "other_image", "default_unclassified", None, [], "unknown",
                   ["no_category_no_hint"])
        self.check("IMG_1234.jpg", "xray", "explicit", "xray", [], "none", [])
        self.check("ecg_01.png", "ecg", "inferred_from_filename", None, ["ecg"], "none", [])
        self.check("serie.dcm", "other_image", "inferred_from_container", None, [], "none", [])
        self.check("x.png", "other_image", "explicit", "other_image", [], "none", [])

    def test_demonstrable_is_never_emitted_and_modality_is_never_verified(self):
        for name in candidate_names():
            for explicit in (None, "skin_wound", "xray", "ecg", "pocus", "other_image"):
                kind, source = api.infer_attachment_kind_with_source(name, None, explicit)
                got = api.kind_assessment(name, kind, source, explicit)
                self.assertIn(got["kind_discordance"], {"none", "suspected", "unknown"})
                self.assertEqual(got["modality_verification"], "not_verified")

    def test_pixels_and_metadata_are_not_used(self):
        # Same name, different image bytes: the assessment cannot change (RGB/EXIF are ignored).
        a = api.prepare_upload("IMG_0001.png", "image/png", b64(si.png()))
        b = api.prepare_upload("IMG_0001.png", "image/png", b64(si.png(width=300, height=200)))
        self.assertEqual(a["kind_assessment"], b["kind_assessment"])


class PreparedAndProvider(unittest.TestCase):
    RESPONSE = {"contract_version": "1.0", "status": "ok", "provider": "synthetic", "model": "synthetic",
                "official_report": None, "ai_interpretation": "Benign lesion, no signs of infection.",
                "findings": "Erythema.", "impression": "Safe to observe.", "limitations": [],
                "confidence": "high"}

    def interpret(self, prepared, raw, seen):
        def transport(cfg, request):
            seen.append(copy.deepcopy(request))
            return dict(self.RESPONSE)
        return api.interpret_prepared_upload(prepared, b64(raw), privacy_checked=True,
                                             burned_in_identifiers_checked=True,
                                             vision_transport=transport, vision_env=ENV)

    def test_assessment_is_inside_the_integrity_token(self):
        raw = si.png()
        prepared = api.prepare_upload("herida.png", "image/png", b64(raw), explicit_kind="xray")
        self.assertEqual(prepared["kind_assessment"]["kind_discordance"], "suspected")
        for field, value in (("kind_discordance", "none"), ("suspicion_codes", []),
                             ("name_hints_matched", []), ("modality_verification", "classifier_verified")):
            tampered = copy.deepcopy(prepared)
            tampered["kind_assessment"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError) as ctx:
                self.interpret(tampered, raw, [])
            self.assertIn("integrity", str(ctx.exception))
        removed = copy.deepcopy(prepared)
        del removed["kind_assessment"]
        with self.assertRaises(ValueError):
            self.interpret(removed, raw, [])

    def test_older_prepared_uploads_without_the_field_still_verify_and_interpret(self):
        raw = si.png()
        prepared = api.prepare_upload("IMG_0001.png", "image/png", b64(raw))
        legacy = api._sign_prepared({k: v for k, v in prepared.items()
                                     if k not in ("kind_assessment", "integrity_token")})
        api._verify_prepared(legacy)
        out = self.interpret(legacy, raw, [])
        self.assertNotIn("kind_assessment", out["prepared"])

    def test_provider_request_and_clinical_output_are_unchanged(self):
        raw = si.png()
        cases = (("herida.png", "skin_wound", "vision_abstained"),
                 ("herida.png", "xray", "vision_interpreted"),
                 ("IMG_0001.png", None, "vision_interpreted"),
                 ("dermatitis_contacto.png", None, "vision_interpreted"))
        for name, kind, status in cases:
            with self.subTest(name=name, kind=kind):
                seen_new, seen_old = [], []  # request_id is random per call; everything else must match
                prepared = api.prepare_upload(name, "image/png", b64(raw), explicit_kind=kind)
                stripped = api._sign_prepared({k: v for k, v in prepared.items()
                                               if k not in ("kind_assessment", "integrity_token")})
                new = self.interpret(prepared, raw, seen_new)
                old = self.interpret(stripped, raw, seen_old)
                self.assertEqual(new["prepared"]["processing"]["status"], status)
                for request in (seen_new[0], seen_old[0]):
                    request.pop("request_id", None)
                self.assertEqual(seen_new, seen_old)  # same provider request, field for field
                self.assertEqual(sorted(seen_new[0]), ["content_base64", "contract_version", "filename", "kind",
                                                       "mime_type", "routed_modules"])
                for forbidden in ("kind_assessment", "kind_source", "suspicion_codes", "name_hints_matched"):
                    self.assertNotIn(forbidden, seen_new[0])

                def comparable(result):
                    clean = copy.deepcopy(result["prepared"])
                    for key in ("kind_assessment", "integrity_token", "upload_id"):
                        clean.pop(key, None)
                    return clean

                new_clean, old_clean = comparable(new), comparable(old)
                for key in ("extracted", "processing", "kind", "route"):
                    self.assertEqual(new_clean.get(key), old_clean.get(key), key)


if __name__ == "__main__":
    unittest.main()
