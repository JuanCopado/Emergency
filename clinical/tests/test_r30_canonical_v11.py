"""R30 · canonical-r27-v1.1 (additive extension) and the converter from the events the PR95 lab entry really emits."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
from human_factors import canonical_r27_v1 as c  # noqa: E402
from human_factors.canonical_r27_v1 import CanonicalViolation  # noqa: E402

SHA = "a" * 64


def ev(kind, at, **detail):
    return {"type": kind, "at_ms": at, "detail": detail}


GEMINI_TEXT = {  # R28/R29 Gemini literal texts (DEC-CLIN-R15-01) keyed by the canonical message key
    "MSG_T7_NO_MODALITY": {"es": "No se ha seleccionado una modalidad admitida. Este sistema no identifica automáticamente el tipo de imagen o documento. Elija la modalidad correspondiente antes de continuar.",
                           "pt": "Não foi selecionada uma modalidade admitida. Este sistema não identifica automaticamente o tipo de imagem ou documento. Selecione a modalidade adequada antes de continuar.",
                           "en": "No supported modality was selected. This system does not automatically identify the image or document type. Choose the appropriate modality before continuing."},
    "MSG_T7_INCOMPATIBLE_MODALITY": {"es": "El archivo no es técnicamente compatible con la modalidad seleccionada. No se ha evaluado el contenido ni se descarta patología. Suba un archivo compatible o elija la modalidad adecuada.",
                                     "pt": "O ficheiro não é tecnicamente compatível com a modalidade selecionada. O conteúdo não foi avaliado nem se exclui patologia. Envie um ficheiro compatível ou escolha a modalidade adequada.",
                                     "en": "This file is not technically compatible with the selected modality. The content was not evaluated and no condition is ruled out. Upload a compatible file or choose the matching modality."},
    "MSG_T7_CORRUPT_FILE": {"es": "El archivo está dañado o no puede procesarse técnicamente. No se ha realizado ninguna evaluación clínica. Repita la captura o cargue una copia íntegra del archivo.",
                            "pt": "O ficheiro está danificado ou não pode ser processado tecnicamente. Não foi realizada qualquer avaliação clínica. Repita a captura ou carregue uma cópia íntegra.",
                            "en": "This file is corrupted or cannot be technically processed. No clinical evaluation was performed. Retake the capture or upload an intact copy of the file."},
    "MSG_T7_UNSUPPORTED_FORMAT": {"es": "El formato de archivo no está admitido por esta función. No se ha analizado el contenido ni se excluye ninguna afección. Convierta o vuelva a cargar el archivo en un formato compatible.",
                                  "pt": "O formato do ficheiro não é suportado por esta função. O conteúdo não foi analisado nem se exclui qualquer condição. Converta ou reenvie num formato compatível.",
                                  "en": "This file format is not supported by this feature. The content was not analyzed and no condition is ruled out. Convert or re-upload the file in a supported format."},
}


def context(**over):
    base = {"participant_opaque_id": "HF1-P001", "role_group": "M", "language_stratum": "ES", "sequence_code": "S1a", "period": 2, "subblock": 1,
            "stimulus_id": "S2-14", "stimulus_hash_sha256": SHA, "task_duration_ms": 9000, "force_attempts": 0,
            "data_provenance": "SYNTHETIC_LAB_HARNESS"}
    base.update(over)
    return base


E1_LOG = [ev("file_selected", 100, size=2048, with_modality=False, viewport_width_px=1280, e1_entry=True),
          ev("layer7_banner_rendered", 150, trigger="T7-01_UNDECLARED_MODALITY", message_id="MSG_T7_NO_MODALITY"),
          ev("modality_selected", 900, modality="ecg", origin="after_layer7"), ev("recovery_action", 901, action="change_modality", trigger="T7-01_UNDECLARED_MODALITY"),
          ev("confirm_clicked", 2000, modality="ecg")]


class Converter(unittest.TestCase):
    def test_e1_recovered_trial_becomes_a_valid_v11_record(self):
        r = c.from_lab_ui_log(E1_LOG, context())
        self.assertEqual((r["schema_version"], r["arm"], r["scenario_id"], r["e1_entry_mode"]), ("canonical-r27-v1.1", "B_prototype_alt_b", "E1", "ISOLATED_LAB_ENTRY_PR95"))
        self.assertEqual((r["layer7_trigger_code"], r["layer7_subreason_code"], r["layer7_message_key"]), ("T7-01", "explicit_flow_missing_selection", "MSG_T7_NO_MODALITY"))
        self.assertEqual((r["recovery_outcome"], r["layer7_banner_to_first_action_ms"], r["device_type"]), ("recovered_correctly", 750, "desktop_web"))
        self.assertEqual((r["outcome_status"], r["set_id"], r["subblock"]), ("technical_abstention_correct", "SET_2", 1))
        c.validate_record_v11(r)

    def test_a_valid_m3_trial_without_banner_has_no_recovery_state(self):
        log = [ev("file_selected", 50, size=10, with_modality=True, viewport_width_px=360, e1_entry=False), ev("modality_selected", 20, modality="ecg", origin="initial"),
               ev("confirm_clicked", 800, modality="ecg")]
        r = c.from_lab_ui_log(log, context(stimulus_id="S2-08", sequence_code="S3a", period=1, subblock=1))
        self.assertEqual((r["scenario_id"], r["recovery_outcome"], r["layer7_trigger_code"], r["outcome_status"], r["e1_entry_mode"]), ("F", "NA", "NONE", "valid_completed", "NONE"))
        self.assertIsNone(r["layer7_banner_to_first_action_ms"])

    def test_document_bridge_is_a_selection_and_never_t7_01(self):
        log = [ev("file_selected", 50, size=10, with_modality=True, viewport_width_px=1280, e1_entry=False), ev("modality_selected", 20, modality="document", origin="initial"),
               ev("confirm_clicked", 800, modality="document")]
        r = c.from_lab_ui_log(log, context(stimulus_id="S2-13", subblock=1))
        self.assertEqual((r["transport_mode"], r["selection_origin"], r["layer7_trigger_code"]), ("document_legacy_bridge", "explicit_user_selection", "NONE"))

    def test_t7_03_banner_recovered_by_a_confirmed_replacement(self):
        log = [ev("file_selected", 50, size=10, with_modality=True, viewport_width_px=390, e1_entry=False), ev("modality_selected", 20, modality="skin_wound", origin="initial"),
               ev("layer7_banner_rendered", 80, trigger="T7-03_CORRUPT_UNPROCESSABLE", message_id="MSG_T7_CORRUPT_FILE"),
               ev("recovery_action", 400, action="replace_file", trigger="T7-03_CORRUPT_UNPROCESSABLE"), ev("file_selected", 600, size=99, with_modality=True, viewport_width_px=390, e1_entry=False),
               ev("confirm_clicked", 900, modality="skin_wound")]
        r = c.from_lab_ui_log(log, context(stimulus_id="S2-15", subblock=2))
        self.assertEqual((r["layer7_subreason_code"], r["recovery_outcome"], r["recovery_action_type"], r["device_type"]), ("zero_bytes_or_decode_or_pr66_limit", "recovered_correctly", "replace_file", "mobile_narrow_390"))

    def test_abandonment_cancellation_and_force_attempts_are_never_guessed(self):
        no_confirm = E1_LOG[:-1]
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log(no_confirm, context())                                         # banner, no confirmed upload, no harness verdict
        r = c.from_lab_ui_log(no_confirm, context(trial_end="abandoned"))
        self.assertEqual(r["recovery_outcome"], "abandoned")
        ctx = context()
        del ctx["force_attempts"]
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log(E1_LOG, ctx)
        self.assertTrue(c.from_lab_ui_log(E1_LOG, context(force_attempts=2))["attempted_force_blocked"])

    def test_missing_viewport_unknown_trigger_and_missing_context_fail_hard(self):
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log([ev("confirm_clicked", 5)], context())
        bad = copy.deepcopy(E1_LOG)
        bad[1]["detail"]["message_id"] = "MSG_T7_CORRUPT_FILE"                               # T7-01 with the T7-03 text: no approved subreason
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log(bad, context())


class Validator(unittest.TestCase):
    def good(self):
        return c.from_lab_ui_log(E1_LOG, context())

    def reject(self, **change):
        r = self.good()
        r.update(change)
        with self.assertRaises(CanonicalViolation):
            c.validate_record_v11(r)

    def test_added_fields_are_closed_and_checked_against_the_matrix(self):
        r = self.good()
        r["extra"] = 1
        with self.assertRaises(CanonicalViolation):
            c.validate_record_v11(r)
        self.reject(sequence_code="S9a")
        self.reject(sequence="BA")                                                           # S1a is AB
        self.reject(set_id="SET_1")                                                          # period 2 of S1a is Set 2
        self.reject(device_type="mobile_narrow_360", viewport_width_px=360)                  # sub-block 1 of period 2 is web
        self.reject(stimulus_id="S1-14")                                                     # set prefix disagrees
        self.reject(stimulus_id="S2-08")                                                     # pair disagrees with scenario E1
        self.reject(stimulus_hash_sha256="xyz")
        self.reject(subblock=2, device_type="mobile_narrow_360", viewport_width_px=360)           # pair 14 belongs to sub-block 1, not 2
        self.reject(e1_entry_mode="NONE")                                                    # E1 in arm B must carry the isolated-entry label
        self.reject(task_duration_ms=0)
        self.reject(layer7_banner_to_first_action_ms=None)                                   # a banner was shown

    def test_v1_records_are_still_valid_under_the_v1_validator_and_v11_is_not_v1(self):
        r = self.good()
        with self.assertRaises(CanonicalViolation):
            c.validate_record(r)                                                             # v1 validator refuses the extra fields: no silent mixing
        projection = {k: v for k, v in r.items() if k not in c.V11_ADDED}
        projection["schema_version"] = c.SCHEMA_VERSION
        c.validate_record(projection)


if __name__ == "__main__":
    unittest.main()


class HistoricalKeys(unittest.TestCase):
    def test_the_evaluator_texts_equal_the_gemini_literals_and_the_key_crosswalk_is_exact(self):
        import base64
        import layer7_adapter as adapter
        stimuli = ROOT / "lab" / "human_factors" / "bank" / "stimuli"

        def body(name):
            return {"filename": name, "mime_type": None, "content_base64": base64.b64encode((stimuli / name).read_bytes()).decode(), "explicit_kind": None}

        cases = (("S2-14.pdf", None, "MSG_T7_A"), ("S2-15.pdf", "skin_wound", "MSG_T7_B"), ("S1-15.jpg", "skin_wound", "MSG_T7_C"), ("QA-01.wav", "skin_wound", "MSG_T7_D"))
        for name, modality, historical in cases:
            for language in ("es", "pt", "en"):
                result = adapter.evaluate_upload(body(name), modality, language)
                self.assertEqual(result["message_id"], historical)
                self.assertEqual(result["message_text"], GEMINI_TEXT[c.HISTORICAL_MESSAGE_KEYS[historical]][language], (historical, language))
        self.assertEqual(len(set(c.HISTORICAL_MESSAGE_KEYS.values())), 4)

    def test_an_unknown_message_key_is_refused(self):
        bad = copy.deepcopy(E1_LOG)
        bad[1]["detail"]["message_id"] = "MSG_T7_Z"
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log(bad, context())
