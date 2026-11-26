"""Localization of presentation copy preserves clinical output and entered text."""
from copy import deepcopy
import sys
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
from clinical_note_diagnostic_engine import analyze
from clinical_note_exporter import note_to_sections, export_docx, export_pdf, export_sections_pdf
from run_clinical_note_diagnostic_cases import build
from therapy_test_fixtures import review_synthetic_therapy

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
                review_synthetic_therapy(note)
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
                export_pdf(note, pdf)
                self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))


    def test_cjk_pdf_preserves_text_and_embeds_both_fonts(self):
        from pypdf import PdfReader
        text = '患者记录：恶心，血压 120/80 mmHg；剂量 300 mg；FiO₂ 0.21。'
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'cjk.pdf'
            export_sections_pdf([('临床记录', [text])], target)
            reader = PdfReader(target)
            extracted = ''.join(page.extract_text() for page in reader.pages)
            self.assertIn(text, extracted)
            fonts = [font.get_object() for page in reader.pages
                     for font in page['/Resources']['/Font'].get_object().values()]
            embedded = [font for font in fonts if font.get('/FontDescriptor')
                        and font['/FontDescriptor'].get_object().get('/FontFile2')]
            self.assertGreaterEqual(len(embedded), 2)
            with self.assertRaisesRegex(ValueError, r'U\+10FFFF'):
                export_sections_pdf([('Unsupported', ['\U0010ffff'])], Path(tmp) / 'bad.pdf')
            self.assertFalse((Path(tmp) / 'bad.pdf').exists())

    def test_cjk_font_assets_match_provenance_manifest(self):
        root = ROOT / 'assets' / 'fonts'
        manifest = json.loads((root / 'noto-cjk-manifest.json').read_text(encoding='utf-8'))
        for name, metadata in manifest['files'].items():
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), metadata['sha256'])


if __name__ == '__main__':
    unittest.main()
