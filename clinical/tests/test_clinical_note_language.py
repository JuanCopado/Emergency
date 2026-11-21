"""Localization of presentation copy preserves clinical output and entered text."""
from copy import deepcopy
import sys
import tempfile
import unittest
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
from clinical_note_diagnostic_engine import analyze
from clinical_note_exporter import note_to_sections, export_docx, export_pdf
from run_clinical_note_diagnostic_cases import build

LANGUAGES = {
    'pt-PT': ('Menções incertas', 'Sem dados laboratoriais', 'Nota Clínica', 'Limitações'),
    'es-ES': ('Menciones inciertas', 'La nota no contiene datos de laboratorio', 'Nota clínica', 'Limitaciones'),
    'en': ('Uncertain mentions', 'No structured laboratory', 'Clinical note', 'Limitations'),
    'zh': ('引擎可能计分', '病历中没有结构化', '诊断支持病历', '局限性'),
}


class NoteLanguage(unittest.TestCase):
    def test_diagnostic_values_preserved_and_limitations_follow_language(self):
        note = build({'age_years': 40, 'hpi': 'Possible ST elevation. Nausea.'})
        original = analyze(note, apply_to_note=True)
        for language, (uncertain, laboratory, _, _) in LANGUAGES.items():
            with self.subTest(language=language):
                current = deepcopy(note)
                current['language'] = language
                output = analyze(current, apply_to_note=True)
                self.assertTrue(any(uncertain in x for x in output['assessment']['limitations']))
                self.assertTrue(any(laboratory in x for x in output['assessment']['limitations']))
                for key in ('assessment',):
                    expected = deepcopy(original[key])
                    observed = deepcopy(output[key])
                    expected.pop('limitations')
                    observed.pop('limitations')
                    self.assertEqual(expected, observed)
                self.assertEqual(original['rule_hits'], output['rule_hits'])
                self.assertEqual(original['signals'], output['signals'])
                self.assertEqual(current['history'], output['note']['history'])

    def test_exports_localize_labels_and_preserve_entered_text(self):
        for language, (_, _, title, limitations) in LANGUAGES.items():
            with self.subTest(language=language), tempfile.TemporaryDirectory() as tmp:
                note = build({'age_years': 40, 'hpi': 'Possible ST elevation. Nausea.'})
                note['language'] = language
                note['history']['chief_complaint'] = 'QA synthetic <unchanged> 7.4 mg'
                note = analyze(note, apply_to_note=True)['note']
                note['clinician_validation']['reviewed'] = True
                sections = note_to_sections(note)
                self.assertIn(title, sections[0][0])
                self.assertIn(limitations, [heading for heading, _ in sections])
                text = '\n'.join(line for _, paragraphs in sections for line in paragraphs)
                self.assertIn('QA synthetic <unchanged> 7.4 mg', text)
                docx = Path(tmp) / 'note.docx'
                export_docx(note, docx)
                with zipfile.ZipFile(docx) as z:
                    xml = z.read('word/document.xml').decode('utf-8')
                self.assertIn(sections[0][0], xml)
                self.assertIn('QA synthetic &lt;unchanged&gt; 7.4 mg', xml)
                pdf = Path(tmp) / 'note.pdf'
                if language == 'zh':
                    with self.assertRaisesRegex(ValueError, 'PDF font does not support Unicode'):
                        export_pdf(note, pdf)
                    self.assertFalse(pdf.exists())
                else:
                    export_pdf(note, pdf)
                    self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))


if __name__ == '__main__':
    unittest.main()
