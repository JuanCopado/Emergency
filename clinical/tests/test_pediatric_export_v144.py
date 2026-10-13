import base64
import io
import json
from pathlib import Path
import sys
import unittest
import zipfile
from xml.etree import ElementTree
from copy import deepcopy
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pediatric_catalog import build_catalog
from pediatric_outpatient_api import calculate_request
from pediatric_result_exporter import export_request

CASES=json.loads((ROOT/'qa/V1.44_PEDIATRIC_EXPORT_CASES.json').read_text(encoding='utf-8'))['cases']

def request(case):
    return {**deepcopy(case['calculation']), 'source_revision':build_catalog()['source_revision']}

def norm(s): return ''.join(s.split())

class PediatricExportTests(unittest.TestCase):
    def test_all_three_formats_preserve_all_canonical_fields_and_alerts(self):
        for case in CASES:
            with self.subTest(case=case['id']):
                body=request(case);computed=calculate_request(body);result=computed['result'];report=computed['export_report']
                for key,want in case['expected'].items():
                    got=result
                    for part in key.split('.'):got=got[part]
                    self.assertAlmostEqual(got,want)
                self.assertEqual(report['snapshot']['inputs'],case['calculation'])
                self.assertEqual(report['snapshot']['result'],result)
                self.assertEqual(report['snapshot']['safety'],computed['safety'])
                self.assertEqual(report['snapshot']['clinical_status'],'CLINICALLY_PENDING')
                self.assertEqual(report['snapshot']['evidence_status'],'yellow')
                for fmt in ('json','pdf','docx'):
                    data=base64.b64decode(export_request({'format':fmt,'calculation':body,'expected_result':result})['content_base64'])
                    if fmt=='json':self.assertEqual(json.loads(data),report);continue
                    if fmt=='pdf':
                        pdf=PdfReader(io.BytesIO(data));self.assertGreater(len(pdf.pages),1)
                        text='\n'.join(p.extract_text() for p in pdf.pages)
                    else:
                        with zipfile.ZipFile(io.BytesIO(data)) as z:
                            xml=ElementTree.fromstring(z.read('word/document.xml'))
                            text='\n'.join(x.text or '' for x in xml.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
                    for heading,paragraphs in report['sections']:
                        for line in [heading,*paragraphs]:self.assertIn(norm(line),norm(text))

    def test_rejects_stop_boundary_stale_tampered_and_unknown_format(self):
        body=request(CASES[0]);result=calculate_request(body)['result']
        good={'format':'json','calculation':body,'expected_result':result}
        variants=[]
        bad=deepcopy(good);bad['expected_result']['dose_mg']=1;variants.append(bad)
        bad=deepcopy(good);bad['calculation']['source_revision']='old';variants.append(bad)
        bad=deepcopy(good);bad['calculation']['patient'].pop('home_analgesia_antipyresis_appropriate');variants.append(bad)
        bad=deepcopy(good);bad['format']='html';variants.append(bad)
        bad=deepcopy(good);bad['calculation']=request(CASES[2]);bad['calculation']['patient']['actual_weight_kg']=40;variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):export_request(bad)

    def test_missing_values_are_not_filled_in(self):
        report=calculate_request(request(CASES[2]))['export_report']
        self.assertNotIn('product',report['snapshot']['inputs'])
        self.assertNotIn('concentration_mg_per_ml',report['snapshot']['result'])
        self.assertNotIn('ideal_weight_kg',report['snapshot']['inputs']['patient'])

if __name__=='__main__': unittest.main()
