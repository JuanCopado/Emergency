"""R24 · R8-ORACLE: independent oracle for the category routing, frozen against the exact base.

Replaces the self-referential check (`with_source` vs the wrapper that calls it).
Three independent anchors:
  1. GOLDEN: outputs of the pre-R8 function (commit 2116899b) for every combination below, frozen in a
     JSON file with its SHA-256. The base source is never imported here.
  2. ORACLE: a literal re-implementation written from the documented precedence, sharing NO code or data
     with clinical_note_api (own hint tables, own file-name cleaner).
  3. MUTATION: mutated oracles (swapped precedence, dropped rule, wrong MIME handling) MUST disagree with
     the golden file, proving the golden can detect a broken helper.

Documented precedence: explicit kind > filename hints in this order (ecg, blood_gas, microbiology,
laboratory_report, pocus, ct, xray, skin_wound) > DICOM (".dcm" extension or "dicom" inside the lowercased
MIME) > PDF (".pdf" extension or lowercased MIME exactly "application/pdf") > other_image.
"""
import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import clinical_note_api as api  # noqa: E402

GOLDEN = json.loads((ROOT / "tests/fixtures/r24_kind_oracle_golden.json").read_text(encoding="utf-8"))
BASE = "2116899bf43fd836173384af27d6e22a6480c51d"

ORDER = [
    ("ecg", ("ecg", "ekg", "electrocard")),
    ("blood_gas", ("gasometr", "blood_gas", "abg", "vbg")),
    ("microbiology", ("microbi", "culture", "cultivo", "hemocult")),
    ("laboratory_report", ("laborat", "analit", "analyt", "hemogram", "bioq")),
    ("pocus", ("pocus", "ultrasound", "ecografia", "ultrasom")),
    ("ct", ("ct_", "ct-", "tac", "tc_", "tc-", "mri", "rm_")),
    ("xray", ("xray", "x-ray", "radiogr", "_rx", "rx_")),
    ("skin_wound", ("piel", "pele", "skin", "wound", "herida", "ferida", "lesion", "lesao", "lesão", "ulcer",
                    "úlcera", "quemadura", "queimadura", "burn", "dermat", "rash", "celulit", "cellulit",
                    "absces", "abscess", "mordedura", "mordedur")),
]


def clean(filename):
    if filename is None or filename == "":
        return "upload"
    if not isinstance(filename, str) or not filename.isprintable():
        return None
    name = filename.replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not name or len(name) > 255 or name.endswith("."):
        return None
    return name.lower()


def oracle(filename, mime, explicit, *, order=ORDER, dicom_before_hints=False, pdf_by_substring=False,
           skip_rule=None):
    if explicit:
        return str(explicit).strip().lower()
    name = clean(filename)
    if name is None:
        return "REJECT"
    mime = str(mime or "").lower()
    is_dicom = name.endswith(".dcm") or "dicom" in mime
    if dicom_before_hints and is_dicom:
        return "other_image"
    for kind, hints in order:
        if kind != skip_rule and any(h in name for h in hints):
            return kind
    if is_dicom:
        return "other_image"
    if name.endswith(".pdf") or (("pdf" in mime) if pdf_by_substring else mime == "application/pdf"):
        return "pdf_document"
    return "other_image"


def current(filename, mime, explicit):
    try:
        return api.infer_attachment_kind_with_source(filename, mime, explicit)[0]
    except api.image_upload_guard.MediaRejected:
        return "REJECT"


def golden_rows():
    for name, mime, explicit, expected in GOLDEN["cases"]:
        yield name, mime, explicit, ("REJECT" if str(expected).startswith("REJECT:") else expected)


class Frozen(unittest.TestCase):
    def test_golden_is_the_frozen_base_artifact(self):
        body = json.dumps(GOLDEN["cases"], ensure_ascii=False, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), GOLDEN["cases_sha256"])
        self.assertEqual(GOLDEN["base_commit"], BASE)
        self.assertEqual(len(GOLDEN["cases"]), GOLDEN["count"])
        self.assertGreater(GOLDEN["count"], 8000)

    def test_golden_covers_normal_ambiguous_and_boundary_cases(self):
        rows = list(golden_rows())
        kinds = {r[3] for r in rows}
        for needed in ("ecg", "blood_gas", "microbiology", "laboratory_report", "pocus", "ct", "xray",
                       "skin_wound", "pdf_document", "other_image", "REJECT"):
            self.assertIn(needed, kinds)
        names = {r[0] for r in rows}
        self.assertTrue({"ecg_herida.png", "piel_tac.png", "herida.pdf", "herida.dcm", "foto.", None, ""} <= names)

    def test_current_routing_equals_frozen_base_for_every_case(self):
        bad = [(n, m, e, exp, current(n, m, e)) for n, m, e, exp in golden_rows() if current(n, m, e) != exp]
        self.assertEqual(bad[:5], [])

    def test_public_function_equals_frozen_base_for_every_case(self):
        def public(n, m, e):
            try:
                return api.infer_attachment_kind(n, m, e)
            except api.image_upload_guard.MediaRejected:
                return "REJECT"
        bad = [(n, m, e, exp) for n, m, e, exp in golden_rows() if public(n, m, e) != exp]
        self.assertEqual(bad[:5], [])


class IndependentOracle(unittest.TestCase):
    def test_oracle_agrees_with_frozen_base(self):
        bad = [(n, m, e, exp, oracle(n, m, e)) for n, m, e, exp in golden_rows() if oracle(n, m, e) != exp]
        self.assertEqual(bad[:5], [])

    def test_oracle_agrees_with_current_code(self):
        bad = [(n, m, e) for n, m, e, _ in golden_rows() if oracle(n, m, e) != current(n, m, e)]
        self.assertEqual(bad[:5], [])

    def test_documented_mime_precedence(self):
        for args, expected in (
            (("x.pdf", "application/dicom", None), "other_image"),      # DICOM MIME outranks .pdf name
            (("x.dcm", "application/pdf", None), "other_image"),        # .dcm outranks PDF MIME
            (("x.png", "APPLICATION/PDF", None), "pdf_document"),       # MIME compared lowercased
            (("x.png", "application/pdf; charset=binary", None), "other_image"),  # exact match only
            (("herida.pdf", None, None), "skin_wound"),                 # name hint outranks container
            (("herida.png", "application/dicom", None), "skin_wound"),
            (("x.png", "application/pdf", "xray"), "xray"),             # explicit outranks everything
        ):
            with self.subTest(args=args):
                self.assertEqual(current(*args), expected)
                self.assertEqual(oracle(*args), expected)

    def test_oracle_shares_nothing_with_the_module_under_test(self):
        self.assertIsNot(ORDER, api.NAME_HINT_RULES)
        self.assertEqual([(k, tuple(h)) for k, h in api.NAME_HINT_RULES], ORDER)  # equal data, written apart
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        used = {n.attr for n in ast.walk(tree)
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "api"}
        self.assertFalse(used & {"_clean_name", "SKIN_WOUND_NAME_HINTS", "name_hint_categories"})


class MutationControl(unittest.TestCase):
    def disagreements(self, **kwargs):
        return sum(1 for n, m, e, exp in golden_rows() if oracle(n, m, e, **kwargs) != exp)

    def test_golden_detects_swapped_precedence(self):
        swapped = [ORDER[7]] + ORDER[:7]
        self.assertGreater(self.disagreements(order=swapped), 0)
        self.assertGreater(self.disagreements(order=list(reversed(ORDER))), 0)

    def test_golden_detects_each_dropped_rule(self):
        for kind, _ in ORDER:
            with self.subTest(rule=kind):
                self.assertGreater(self.disagreements(skip_rule=kind), 0)

    def test_golden_detects_mime_precedence_errors(self):
        self.assertGreater(self.disagreements(dicom_before_hints=True), 0)
        self.assertGreater(self.disagreements(pdf_by_substring=True), 0)

    def test_golden_detects_a_broken_current_helper(self):
        original = api.infer_attachment_kind_with_source
        try:
            api.infer_attachment_kind_with_source = lambda f, m=None, e=None: ("other_image", "default_unclassified")
            broken = sum(1 for n, m, e, exp in golden_rows() if current(n, m, e) != exp)
            self.assertGreater(broken, 1000)
        finally:
            api.infer_attachment_kind_with_source = original


class RoutingInvariance(unittest.TestCase):
    def test_kind_source_never_changes_the_kind(self):
        for n, m, e, exp in golden_rows():
            if exp == "REJECT":
                continue
            kind, source = api.infer_attachment_kind_with_source(n, m, e)
            self.assertEqual(kind, exp)
            self.assertIn(source, {"explicit", "inferred_from_filename", "inferred_from_container",
                                   "default_unclassified"})


if __name__ == "__main__":
    unittest.main()
