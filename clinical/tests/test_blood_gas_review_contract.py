"""Exercise the actual review handler without opening a network socket."""
import io
import json
import os
import sys
import unittest
from email.message import Message
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from blood_gas_local import Handler
from blood_gas_review import samples


class InMemoryReview(Handler):
    def __init__(self, server, body, route='/review'):
        self.server = server
        self.path = '/api/blood-gas' + route
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.rfile = io.BytesIO(data)
        self.connection = SimpleNamespace(settimeout=lambda _: None)
        self.headers = Message()
        for key, value in {'Host': server.address, 'X-Session': server.token,
                           'Origin': 'http://' + server.address,
                           'Content-Length': str(len(data)),
                           'Content-Type': 'application/octet-stream' if route == '/extract' else 'application/json'}.items():
            self.headers[key] = value
        self.response = None

    def reply_json(self, status, body):
        self.response = (status, body)

    def send_error(self, code, *args):
        self.response = (code, {})


class ReviewContract(unittest.TestCase):
    def setUp(self):
        segment = samples('pH 7.28\nSample type: venous\nDate: 2026-11-18', 1)[0]
        for field in segment['fields']:
            field.update(legibility='unverified', bbox=[10, 10, 100, 30])
        segment.update(source_page=1, sample_label='synthetic-A', region=[0, 0, 580, 220])
        self.page = segment
        self.server = SimpleNamespace(address='127.0.0.1:12345', token='test-token',
                                      allowed_origins={'http://127.0.0.1:12345'},
                                      ticket='test-ticket', pages=[segment])
        self.request = dict(ticket='test-ticket', page=0, oneSample=True,
                            medicalConfirmed=True, areaConfirmed=True, sample='venosa',
                            rows=[dict(name='pH', number='7.21', unit='',
                                       review='confirmed', visualReviewed=True)])

    def review(self):
        handler = InMemoryReview(self.server, self.request)
        handler.handle_post()
        return handler.response

    def confirmed_metadata(self):
        return [dict(label=m['label'], value=m['value'], review='confirmed')
                for m in self.page['metadata']]

    def test_metadata_must_be_reviewed_before_calculation(self):
        self.assertEqual(self.review()[0], 422)
        self.request['metadata'] = self.confirmed_metadata()
        self.request['metadata'][0]['review'] = 'pending'
        self.assertEqual(self.review()[0], 422)
        self.request['metadata'][0]['review'] = 'confirmed'
        self.assertEqual(self.review()[0], 200)

    def test_sample_type_conflict_requires_explicit_metadata_correction(self):
        self.request.update(sample='arterial', metadata=self.confirmed_metadata())
        self.assertEqual(self.review()[0], 422)
        self.request['metadata'][0]['value'] = 'arterial'
        self.assertEqual(self.review()[0], 422)
        self.request['metadata'][0].update(resolved_sample_type='arterial',
                                           reason='Synthetic source correction checked visually')
        status, result = self.review()
        self.assertEqual(status, 200)
        self.assertEqual(result['reviewed_metadata'][0]['original_value'], 'venous')
        self.assertEqual(result['reviewed_metadata'][0]['value'], 'arterial')
        self.assertTrue(result['reviewed_metadata'][0]['corrected'])

    def test_rejected_metadata_requires_reason_and_keeps_original(self):
        self.request['metadata'] = self.confirmed_metadata()
        self.request['metadata'][0]['review'] = 'rejected'
        self.assertEqual(self.review()[0], 422)
        self.request['metadata'][0]['reason'] = 'Synthetic analyzer label is incorrect'
        status, result = self.review()
        self.assertEqual(status, 200)
        self.assertEqual(result['reviewed_metadata'][0]['original_value'], 'venous')
        self.assertEqual(result['reviewed_metadata'][0]['review'], 'rejected')

    def test_result_preserves_literal_source_and_corrected_values(self):
        self.request['metadata'] = self.confirmed_metadata()
        status, result = self.review()
        self.assertEqual(status, 200)
        self.assertIn('review_provenance', result)
        row = result['review_provenance']['fields'][0]
        self.assertEqual(row['original_number'], '7.28')
        self.assertEqual(row['number'], '7.21')
        self.assertEqual(row['raw'], 'pH 7.28')
        self.assertTrue(row['corrected'])
        self.assertEqual(result['clinical_status'], 'CLINICALLY_PENDING')
        self.assertEqual(self.page['fields'][0]['number'], '7.28')

    @unittest.skipUnless(os.name == 'nt', 'Requires Windows Job Object containment; exercised by Windows OCR CI')
    def test_multiformat_extraction_review_and_revocation_without_socket(self):
        from test_blood_gas_multiformat import encoded, pdf, picture
        lines = ['pH 7.28', 'Na 141 mmol/L', 'Cl 103 mmol/L']
        documents = [('digital PDF', pdf([lines])), ('scanned PDF', pdf([lines], True))]
        documents += [(fmt, encoded(picture(lines), fmt)) for fmt in ('PNG', 'JPEG', 'TIFF', 'WEBP')]
        for name, data in documents:
            with self.subTest(format=name):
                def request(route, body):
                    handler = InMemoryReview(self.server, body, route)
                    handler.handle_post()
                    return handler.response
                status, document = request('/extract', data)
                self.assertEqual(status, 200)
                rows = document['pages'][0]['fields']
                self.assertEqual([(r['name'], r['number'], r['unit']) for r in rows],
                                 [('pH', '7.28', ''), ('Na', '141', 'mmol/L'), ('Cl', '103', 'mmol/L')])
                review = dict(ticket=document['ticket'], page=0, rows=rows, sample='arterial',
                              oneSample=True, medicalConfirmed=True, areaConfirmed=True, metadata=[])
                self.assertEqual(request('/review', review)[0], 422)
                for row in rows:
                    row.update(review='confirmed', visualReviewed=True, transcribed=True)
                for gate in ('medicalConfirmed', 'areaConfirmed', 'oneSample'):
                    self.assertEqual(request('/review', {**review, gate: False})[0], 422)
                status, result = request('/review', review)
                self.assertEqual(status, 200)
                self.assertEqual(result['ph_state'], 'acidemia')
                self.assertEqual(result['clinical_status'], 'CLINICALLY_PENDING')
                request('/reject', {'ticket': document['ticket']})
                self.assertEqual(request('/review', review)[0], 422)
                self.assertIsNone(self.server.source)
                self.assertEqual(self.server.pages, [])

    def test_uncertain_units_and_visual_discrepancies_require_transcription(self):
        for legibility, visual_check in (('unit_unreadable', 'ocr_only'),
                                         ('unverified', 'discrepancy'),
                                         ('unverified', 'visual_only')):
            with self.subTest(legibility=legibility, visual_check=visual_check):
                self.setUp()
                self.page['fields'][0].update(legibility=legibility, visual_check=visual_check)
                self.request['metadata'] = self.confirmed_metadata()
                self.assertEqual(self.review()[0], 422)
                self.request['rows'][0]['transcribed'] = True
                self.assertEqual(self.review()[0], 200)


if __name__ == '__main__':
    unittest.main()
