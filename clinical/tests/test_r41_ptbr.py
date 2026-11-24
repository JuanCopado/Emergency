"""R41 · approved pt-BR texts (MED-DEC-R39-PTBR-FINAL, 24/11/2026). Laboratory only: explicit variant, pt-PT untouched, historical contract untouched."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
sys.path.insert(0, str(ROOT / "tests"))
from human_factors import layer7_adapter as ad  # noqa: E402
import canonical_r27_v12 as c12  # noqa: E402
from canonical_r27_v1 import CanonicalViolation  # noqa: E402
from test_r27_layer7_adapter import body  # noqa: E402
from test_r31_outcomes_and_recovery import ev, selected  # noqa: E402
from test_r34_canonical_v12 import Bank, locale_event  # noqa: E402

CONTRACT_FILE = ROOT / "references" / "modality-abstention-layer7.contract.proposed.json"
CONTRACT = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))
CONTRACT_SHA256 = "a476454522f96b59a05d9aac15e95c1f104baede15ad2880bbfd089fe3cec2b7"      # as received at dcc48b3: never edited by R41

APPROVED = {
    "MSG_T7_A": "Não foi selecionada uma modalidade permitida. Este sistema não identifica automaticamente o tipo de imagem ou documento. Selecione a modalidade adequada antes de continuar.",
    "MSG_T7_B": "O arquivo não é tecnicamente compatível com a modalidade selecionada. O conteúdo não foi avaliado nem se exclui patologia. Envie um arquivo compatível ou escolha a modalidade adequada.",
    "MSG_T7_C": "O arquivo está danificado ou não pode ser processado tecnicamente. Não foi realizada nenhuma avaliação clínica. Repita a captura ou envie uma cópia íntegra.",
    "MSG_T7_D": "O formato do arquivo não é suportado por esta função. O conteúdo não foi analisado nem se exclui nenhuma condição. Converta ou reenvie em um formato compatível.",
}
CONTROLS = ["Substituir arquivo", "Verifique o arquivo na tela", "Enviar arquivo", "Selecionar modalidade", "Envio bloqueado"]
CASES = {  # trigger -> (file, explicit_kind, ui_modality, message id)
    "T7-01": (("S1-14.png", None, "image/png"), None, "MSG_T7_A"),
    "T7-03": (("S1-15.jpg", "skin_wound", "image/jpeg"), "skin_wound", "MSG_T7_C"),
    "T7-04B": (("S2-15.pdf", "skin_wound", "application/pdf"), "skin_wound", "MSG_T7_B"),
    "T7-04A": (("QA-01.wav", "skin_wound", "audio/wav"), "skin_wound", "MSG_T7_D"),
}


class ApprovedTexts(unittest.TestCase):
    def test_texts_and_controls_are_the_literal_approved_ones(self):
        data = json.loads((ROOT / "lab" / "human_factors" / "layer7_ptbr_texts.json").read_text(encoding="utf-8"))
        self.assertEqual(data["message-texts"], APPROVED)
        self.assertEqual(data["controls"], CONTROLS)
        self.assertEqual(data["x-decision"], "MED-DEC-R39-PTBR-FINAL")
        for text in APPROVED.values():
            self.assertNotIn("ficheiro", text)                     # no European wording leaks into the Brazilian texts
            self.assertNotIn("qualquer", text)

    def test_the_historical_contract_is_byte_identical_and_still_european(self):
        self.assertEqual(hashlib.sha256(CONTRACT_FILE.read_bytes()).hexdigest(), CONTRACT_SHA256)
        self.assertIn("ficheiro", CONTRACT["x-message-texts"]["MSG_T7_B"]["pt"])
        self.assertNotIn("pt-BR", CONTRACT["x-message-texts"]["MSG_T7_B"])


class HarnessAndAdapter(unittest.TestCase):
    def test_each_trigger_returns_its_approved_pt_br_text_only_with_the_explicit_variant(self):
        for name, (args, modality, message_id) in CASES.items():
            with self.subTest(trigger=name):
                br = ad.evaluate_upload(body(*args), modality, "pt", "pt-BR")
                self.assertEqual((br["abstains"], br["message_id"], br["variant"]), (True, message_id, "pt-BR"))
                self.assertEqual(br["message_text"], APPROVED[message_id])
                self.assertFalse(br["force_send_available"])
                pt = ad.evaluate_upload(body(*args), modality, "pt", "pt-PT")           # pt-PT: contract text, unchanged
                generic = ad.evaluate_upload(body(*args), modality, "pt")                # generic pt: contract text, variant None
                self.assertEqual(pt["message_text"], CONTRACT["x-message-texts"][message_id]["pt"])
                self.assertEqual(generic["message_text"], CONTRACT["x-message-texts"][message_id]["pt"])
                self.assertNotIn("variant", generic)
                for lang in ("es", "en"):
                    self.assertEqual(ad.evaluate_upload(body(*args), modality, lang)["message_text"], CONTRACT["x-message-texts"][message_id][lang])

    def test_a_variant_is_refused_outside_a_portuguese_ui_or_when_unknown(self):
        args = CASES["T7-03"]
        for language, variant in (("es", "pt-BR"), ("en", "pt-BR"), ("pt", "pt"), ("pt", "pt-AO"), ("pt", "PT-BR")):
            with self.subTest(language=language, variant=variant):
                with self.assertRaises(ValueError):
                    ad.evaluate_upload(body(*args[0]), args[1], language, variant)

    def test_valid_uploads_are_not_blocked_in_pt_br(self):
        out = ad.evaluate_upload(body("S1-14.png", "ecg", "image/png"), "ecg", "pt", "pt-BR")
        self.assertEqual((out["abstains"], out["message_text"], out["variant"]), (False, None, "pt-BR"))


class CanonicalEvidence(unittest.TestCase):
    """language_stratum=pt-BR is only valid when the UI itself logged a locale_resolved event for pt-BR (v1.2 contract, unchanged)."""
    def setUp(self):
        self.bank = Bank({"S1-08": None})
        self.addCleanup(self.bank.dir.cleanup)
        self.log = lambda w: [selected(w), ev("confirm_clicked", 500)]

    def export(self, events):
        context, width = self.bank.context("S1a", 1, 8, language_stratum="pt-BR", data_provenance="SYNTHETIC_FIXTURE")
        return c12.from_lab_ui_log_v12(events + self.log(width), context, self.bank.manifest, self.bank.dir.name)

    def test_pt_br_stratum_requires_the_observable_pt_br_event(self):
        self.assertEqual(self.export([locale_event("pt", "pt-BR")])["language_stratum"], "pt-BR")
        for events in ([], [locale_event("pt", None)], [locale_event("pt", "pt-PT")], [locale_event("pt", "pt-BR", "UNSUPPORTED")], [locale_event("es", "pt-BR")]):
            with self.subTest(events=events):
                with self.assertRaises(CanonicalViolation):
                    self.export(events)


class RealAppEvidence(unittest.TestCase):
    """The committed Chromium run on the real lab build: pt-BR strata come from the UI's own locale_resolved event, with literal controls."""
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / "lab" / "human_factors" / "fidelity" / "layer7_ui_report_ptbr.json").read_text(encoding="utf-8"))
        cls.sealed = json.loads((ROOT / "lab" / "human_factors" / "fidelity" / "layer7_ui_records_v12_ptbr.json").read_text(encoding="utf-8"))

    def test_pt_br_trials_prove_their_stratum_with_an_observable_event(self):
        br = [r for r in self.report["results"] if r["language"] == "pt-BR"]
        self.assertEqual(len(br), 12)
        applicable = [r for r in br if r["canonical_export"]["status"] != "NOT_APPLICABLE"]
        self.assertEqual(len(applicable), 8)
        for trial in applicable:
            self.assertEqual(trial["canonical_export"]["status"], "EXPORTED")
            events = [e["detail"] for e in trial["ui_log"] if e["type"] == "locale_resolved"]
            self.assertTrue(events)
            for detail in events:
                self.assertEqual(detail, {"language": "pt", "lab_locale": "pt-BR", "variant": "pt-BR", "status": "OK"})
        self.assertEqual(len(self.sealed), 8)
        self.assertEqual(
            {(x["scenario"], x["viewport"]) for x in self.sealed},
            {(r["scenario"], r["viewport"]) for r in applicable},
        )
        manifest = c12.load_manifest()
        for item in self.sealed:
            record = item["record"]
            self.assertEqual((item["language"], record["language_stratum"]), ("pt-BR", "pt-BR"))
            c12.validate_record_v12(record, manifest, c12.DEFAULT_STIMULI)

    def test_banner_text_is_the_adapter_text_and_controls_are_literal_without_force_send(self):
        approved = set(CONTROLS)
        for r in self.report["results"]:
            if r["language"] != "pt-BR" or not r["banner_shown"]:
                continue
            self.assertTrue(r["text_equals_adapter_text"])
            self.assertEqual((r["force_send_controls"], r["confirm_buttons"]), (0, 0))
            self.assertTrue(set(r["recovery_controls"]) <= approved, r["recovery_controls"])
            if r["scenario"] == "E2_T7-04_audio_global_format":
                self.assertEqual(r["recovery_controls"], ["Enviar arquivo"])
            if r["scenario"] == "E2_T7-04_pdf_on_photo_route":
                self.assertEqual(r["recovery_controls"], ["Selecionar modalidade", "Enviar arquivo"])

    def test_unapproved_regional_requests_stay_closed(self):
        self.assertTrue(self.report["summary"]["unapproved_regional_requests_fail_closed"])
        self.assertEqual([(t["ui_language"], t["lab_locale"], t["file_inputs"]) for t in self.report["unapproved_regional_fail_closed_trace"]],
                         [("es", "pt-BR", 0), ("pt", "pt-AO", 0), ("pt", "pt", 0)])
        self.assertEqual(sum(1 for x in self.report["results"] if x["language"] == "pt" and x["canonical_export"]["status"] == "NOT_EXPORTED"), 8)  # bare pt still refused


if __name__ == "__main__":
    unittest.main()
