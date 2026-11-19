"""PAR-01 regression tests. All source documents and reviews are synthetic."""
import copy
import io
import os
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from test_blood_gas_multiformat import pdf
from blood_gas_review import extract, interpret, parse, sample_type, samples
from blood_gas_local import make_server, preserve_specimen_types, specimen_sources


class SampleSegmentation(unittest.TestCase):
    def test_unambiguous_equivalents_only(self):
        for value, expected in [('ARTERIAL  blood', 'arterial'), ('sangre venosa', 'venosa'),
                                ('capillary blood', 'capilar'), ('mixed venous', None),
                                ('ART', None), ('arterial / venous', None), ('unknown', None)]:
            with self.subTest(value=value):
                self.assertEqual(sample_type(value), expected)

    def test_short_heading_can_be_both_boundary_and_declaration(self):
        groups = samples("Muestra: arterial\npH 7.30\nMuestra: venosa\npH 7.25", 3)
        self.assertEqual([[g['label'], g['fields'][0]['number']] for g in groups],
                         [['arterial', '7.30'], ['venosa', '7.25']])
        for group, line in zip(groups, [1, 3]):
            meta, = group['metadata']
            self.assertEqual((meta['page'], meta['line'], meta['raw'], meta['source_sample_label']),
                             (3, line, 'Muestra: '+group['label'], group['label']))
            self.assertEqual(meta['kind'], 'sample_type')

    def test_identifier_and_declaration_keep_their_sample(self):
        groups = samples("Sample #A\nFecha: synthetic\nMuestra: arterial\npH 7.30\n"
                         "Sample #B\nMuestra: desconocida\nNa 140 mmol/L", 2)
        self.assertEqual([g['label'] for g in groups], ['A', 'B'])
        self.assertEqual([f['line'] for g in groups for f in g['fields']], [4, 7])
        self.assertEqual([m['value'] for m in groups[0]['metadata']], ['synthetic', 'arterial'])
        self.assertEqual([(m['value'], m['source_sample_label'], m['line']) for m in groups[1]['metadata']],
                         [('desconocida', 'B', 6)])

    def test_long_declarations_between_disjoint_fields_split_the_acquisitions(self):
        groups=samples('Sample type: arterial\npO2 80 mmHg\nSample type: venous\nFiO2 40 %', 1)
        self.assertEqual([[f['name'] for f in g['fields']] for g in groups], [['pO2'],['FiO2']])
        self.assertEqual([g['metadata'][0]['line'] for g in groups],[1,3])
        for group in groups:
            result=interpret([{**f,'review':'confirmed'} for f in group['fields']], 'arterial')
            self.assertNotIn('pao2_fio2_ratio_mm_hg',result)

    def test_pdf_raster_specimen_and_conflicting_text_layer_retain_provenance(self):
        for native in ['', 'Muestra: venosa']:
            with self.subTest(native=native):
                buf=io.BytesIO()
                c=Canvas(buf,pagesize=(350,280),invariant=1)
                raster=Image.new('RGB',(680,100),'white')
                font=ImageFont.truetype(os.getenv('BG_TEST_FONT','arial.ttf'),40)
                ImageDraw.Draw(raster).text((5,10),'Muestra: arterial',font=font,fill='black')
                c.drawImage(ImageReader(raster),15,213,width=310,height=45)
                c.setFont('Helvetica',16)
                if native:
                    c.saveState()
                    c.setFillAlpha(0)
                    c.drawString(17,239,native)
                    c.restoreState()
                c.drawString(16,178,'pH 7.30')
                c.showPage()
                c.save()
                page,=extract(buf.getvalue())
                meta=page['metadata']
                visual,=[m for m in meta if m['source_layer']=='visual_ocr']
                self.assertEqual((visual['raw'],visual['normalized_sample_type']),('Muestra: arterial','arterial'))
                self.assertEqual(visual['page'],1)
                self.assertIsNotNone(visual['bbox'])
                if native:
                    printed,=[m for m in meta if m['source_layer']=='pdf_text']
                    self.assertEqual(printed['raw'],native)
                    self.assertTrue(printed.get('type_discrepancy'))
                    self.assertTrue(visual.get('type_discrepancy'))

    def test_unassigned_visual_header_requires_scope_on_every_sample(self):
        from blood_gas_review import compare_specimen_layers
        common=dict(text='Sample type: arterial blood', bbox=[10,10,180,25])
        native_fields=[dict(text=text, bbox=[10,40+30*i,140,52+30*i]) for i,text in enumerate(
                       ['Sample 1','pH 7.30','Sample 2','pH 7.24'])]
        for header_in_text in [False, True]:
            with self.subTest(header_in_text=header_in_text):
                native=([common] if header_in_text else [])+native_fields
                visual=[common]+native_fields
                segments=samples('\n'.join(x['text'] for x in native),1)
                for s in segments:
                    for m in s['metadata']:
                        m.update(bbox=native[m['line']-1]['bbox'],source_layer='pdf_text')
                compare_specimen_layers(segments,native,visual,1)
                self.assertEqual(len(segments),2)
                for segment in segments:
                    m,=segment['metadata']
                    self.assertEqual((m['raw'],m['scope']), ('Sample type: arterial blood','unassigned'))

    def test_undetermined_or_blank_declaration_is_retained(self):
        for heading in ['Sample type: ART', 'Sample type:', 'Muestra: indistinta', 'Muestra:', 'Muestra: V', 'Sample: A']:
            with self.subTest(heading=heading):
                meta, = samples(heading+'\npH 7.30', 1)[0]['metadata']
                self.assertEqual(meta['raw'], heading)
                self.assertIsNone(meta['normalized_sample_type'])

    def test_crop_retains_original_declaration_and_distinguishes_samples(self):
        pages = samples("Muestra: arterial\npH 7.30\nMuestra: venosa\nNa 140 mmol/L", 1)
        for i, page in enumerate(pages):
            page.update(source_page=1, sample_label=page['label'])
            page['fields'][0]['bbox']=[10, 100*i+12, 150, 100*i+20]
            page['metadata'][0]['bbox']=[10, 100*i, 150, 100*i+8]
        sources = specimen_sources(pages)
        cropped=dict(source_page=1, fields=[pages[1]['fields'][0]], metadata=[])
        preserve_specimen_types(cropped, sources)
        self.assertEqual([(m['value'],m['line']) for m in cropped['metadata']], [('venosa', 3)])
        self.assertEqual(cropped['metadata'][0]['source_sample_label'], 'venosa')
        mixed=dict(source_page=1, fields=[p['fields'][0] for p in pages], metadata=[])
        preserve_specimen_types(mixed, sources)
        self.assertTrue(mixed['blocked'])
        self.assertEqual([m['value'] for m in mixed['metadata']], ['arterial','venosa'])

    def test_ambiguous_multiple_unit_tokens_are_not_dropped(self):
        for raw in ['FiO2 0.40', 'FiO2 0.40 ?', 'FiO2 0.40 % / fraction']:
            with self.subTest(raw=raw):
                f, = parse(raw, 2)
                self.assertEqual((f['raw'],f['legibility']), (raw,'unit_unreadable'))
                with self.assertRaises(ValueError):
                    interpret([{**f, 'review':'confirmed'}], 'arterial')


class DirectReviewHTTP(unittest.TestCase):
    """Real TCP/HTTP review and revocation. Install the real PDF/OCR result before each test."""
    @classmethod
    def setUpClass(cls):
        cls.data = pdf([['Sample type: arterial blood','pH 7.30','pO2 80 mmHg','FiO2 40 %'],
                        ['Muestra: arterial','pH 7.30','pO2 80 mmHg','FiO2 0.4 %'],
                        ['Sample type: mixed venous','pH 7.29','FiO2 0.40'],
                        ['Muestra: capilar','pH 7.33','FiO2 0.40 % / fraction']])
        cls.extracted = extract(cls.data)
        cls.app = make_server()
        cls.thread = threading.Thread(target=cls.app.serve_forever, daemon=True)
        cls.thread.start()
        cls.client = build_opener(ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.app.shutdown()
        cls.thread.join()
        cls.app.server_close()

    def setUp(self):
        self.app.ticket = 'synthetic-par01'
        self.app.source = self.data
        self.app.pages = copy.deepcopy(self.extracted)

    def send(self, route, payload):
        request = Request('http://'+self.app.address+'/api/blood-gas'+route,
                          json.dumps(payload).encode(), headers={
                          'Origin':'http://'+self.app.address, 'X-Session':self.app.token,
                          'Content-Type':'application/json'})
        try:
            with self.client.open(request, timeout=10) as res:
                return res.status, json.load(res)
        except HTTPError as error:
            return error.code, json.load(error)

    def request(self, idx, sample):
        p = self.app.pages[idx]
        return dict(ticket=self.app.ticket, page=idx, sample=sample, oneSample=True,
                    areaConfirmed=True, medicalConfirmed=True,
                    rows=[dict(name=f['name'], number=f['number'], unit=f['unit'], review='confirmed',
                               visualReviewed=True, transcribed=True) for f in p['fields']],
                    metadata=[dict(label=m['label'],value=m['value'],review='confirmed') for m in p['metadata']])

    def test_both_audited_headers_require_resolution_bound_to_manual_sample(self):
        for idx, raw in [(0,'Sample type: arterial blood'),(1,'Muestra: arterial')]:
            with self.subTest(source=raw):
                req = self.request(idx, 'venosa')
                if idx == 1:
                    req['rows'][-1]['review']='rejected'
                item, = req['metadata']
                item.update(scope='unassigned', applies_to_sample=False, normalized_sample_type='venosa')
                self.assertEqual(self.send('/review', req)[0], 422)
                item['resolved_sample_type']='venosa'
                self.assertEqual(self.send('/review', req)[0], 422)
                item['reason']='Cotejo explícito de la muestra sintética'
                code, result = self.send('/review',req)
                self.assertEqual(code,200)
                traced,=result['reviewed_metadata']
                self.assertEqual((traced['raw'],traced['page'],traced['line'],traced['original_type'],
                                  traced['resolved_sample_type']), (raw,idx+1,1,'arterial','venosa'))
                self.assertTrue(traced['bbox'])
                self.assertNotIn('pao2_fio2_ratio_mm_hg',result)
                if idx == 0:
                    self.assertIsNone(result['fio2_trace']['used_fraction'])
                req['sample']='capilar'
                self.assertEqual(self.send('/review',req)[0],422)

    def test_unknown_and_edited_metadata_need_reason_even_if_new_value_matches(self):
        req = self.request(2,'venosa')
        req['rows'][-1]['review']='rejected'
        item, = req['metadata']
        for value in ['mixed venous','venosa']:
            item.update(value=value, resolved_sample_type='venosa', reason='  ')
            self.assertEqual(self.send('/review',req)[0],422)
            item['reason']='Informe sintético cotejado'
            code,result=self.send('/review',req)
            self.assertEqual(code,200)
            self.assertEqual(result['reviewed_metadata'][0]['original_value'],'mixed venous')

    def test_literal_percent_fraction_and_revocation(self):
        for idx, fraction, ratio in [(0,0.40,200)]:
            req=self.request(idx,'arterial')
            code,result=self.send('/review',req)
            self.assertEqual(code,200)
            trace=result['fio2_trace']
            self.assertEqual((trace['normalized_fraction'],trace['used_fraction']), (fraction, fraction))
            self.assertEqual(result['pao2_fio2_ratio_mm_hg'],ratio)
        invalid=self.request(1,'arterial')
        self.assertEqual(self.send('/review',invalid)[0],422)
        self.assertEqual(self.send('/reject',dict(ticket=self.app.ticket))[0],200)
        self.assertEqual(self.send('/review',req)[0],422)

    def test_missing_or_ambiguous_unit_requires_transcription_reason_and_current_pair(self):
        for idx in [2,3]:
            req=self.request(idx,'arterial')
            req['metadata'][0].update(resolved_sample_type='arterial',reason='Muestra sintética cotejada')
            row=req['rows'][-1]
            self.assertEqual(self.send('/review',req)[0],422)
            row.update(unit='fraction',transcribed=False,correction_reason='Unidad transcrita',
                       fio2_attestation=['0.40','fraction'])
            self.assertEqual(self.send('/review',req)[0],422)
            row.update(transcribed=True,correction_reason='  ')
            self.assertEqual(self.send('/review',req)[0],422)
            row['correction_reason']='Unidad transcrita'
            code,result=self.send('/review',req)
            self.assertEqual(code,200)
            trace=result['fio2_trace']
            self.assertEqual((trace['original_unit'],trace['reviewed_unit'],trace['used_fraction']),
                             ('' if idx==2 else '% / fraction','fraction',0.40))
            self.assertTrue(trace['corrected'])
            self.assertEqual(trace['correction_reason'],'Unidad transcrita')
            row['unit']='%'
            self.assertEqual(self.send('/review',req)[0],422)
            row.update(unit='fraction',number='0.41')
            self.assertEqual(self.send('/review',req)[0],422)

    def test_clinical_fio2_interval_and_decimal_separators_over_http(self):
        cases=[('21','%',0.21),('100','%',1),('40','%',0.4),
               ('0.40','fraction',0.4),('0,4','fraction',0.4),('0,21','fracción',0.21),
               ('1','fraction',1),('0.4','%',None),('20.99','%',None),
               ('100.01','%',None),('0.2099','fraction',None),('1.0001','fraction',None),
               ('40','fraction',None),('0.4','',None),
               ('20.9999999999999999','%',None),('100.000000000000000001','%',None),
               ('0.20999999999999999999','fraction',None),('1.00000000000000000001','fraction',None)]
        for number,unit,expected in cases:
            with self.subTest(number=number,unit=unit):
                req=self.request(0,'arterial')
                req['rows'][-1].update(number=number,unit=unit,
                    fio2_attestation=[number,unit],correction_reason='Cotejo sintético')
                status,result=self.send('/review',req)
                self.assertEqual(status,422 if expected is None else 200)
                if expected is not None:
                    self.assertEqual(result['fio2_trace']['used_fraction'],expected)
                    self.assertAlmostEqual(result['pao2_fio2_ratio_mm_hg'],80/expected)

    def test_three_global_and_visual_confirmations_still_enforced(self):
        req=self.request(0,'arterial')
        for gate in ['areaConfirmed','medicalConfirmed','oneSample']:
            self.assertEqual(self.send('/review',{**req, gate:False})[0],422)
        req['rows'][0]['visualReviewed']=False
        self.assertEqual(self.send('/review',req)[0],422)

if __name__=='__main__':
    unittest.main()
