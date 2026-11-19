"""Synthetic replacement attempts must not retain earlier review authority."""
import unittest
from unittest.mock import patch

import test_blood_gas_review_contract as review_fixture
from test_blood_gas_review_contract import InMemoryReview
from blood_gas_review import LIMIT


class SessionSafety(unittest.TestCase):
    def setUp(self):
        self.fixture = review_fixture.ReviewContract()
        self.fixture.setUp()
        self.server = self.fixture.server
        self.server.source = b'synthetic previous document'
        self.server.document_context = [dict(scope='unassigned', page=1, label='Date', value='synthetic')]
        self.fixture.request['metadata'] = self.fixture.confirmed_metadata()

    def assert_revoked(self):
        self.assertIsNone(self.server.ticket)
        self.assertIsNone(self.server.source)
        self.assertEqual(self.server.pages, [])
        self.assertEqual(self.server.document_context, [])
        old = InMemoryReview(self.server, self.fixture.request)
        old.handle_post()
        self.assertEqual(old.response[0], 422)

    def test_malformed_authenticated_replacements_revoke_previous_document(self):
        cases = [
            ('/regions', b'{', None),
            ('/regions', [], None),
            ('/regions', {'ticket': 'test-ticket'}, None),
            ('/regions', {'ticket': 'test-ticket', 'regions': None}, None),
            ('/regions', b'{}', str(LIMIT + 1)),
            ('/extract', b'', None),
            ('/extract', b'{}', str(LIMIT + 1)),
            ('/extract', b'{}', 'invalid-length'),
            ('/extract', b'{}', '3'),
        ]
        for route, body, length in cases:
            with self.subTest(route=route, body=body, length=length):
                self.setUp()
                handler = InMemoryReview(self.server, body, route)
                if length is not None:
                    handler.headers.replace_header('Content-Length', length)
                handler.handle_post()
                self.assertIn(handler.response[0], (400, 413, 422))
                self.assert_revoked()

    def test_unauthenticated_attempts_do_not_revoke_valid_document(self):
        for header, value in (('Host', 'untrusted.invalid'),
                              ('Origin', 'https://untrusted.invalid'),
                              ('X-Session', 'wrong-token')):
            with self.subTest(header=header):
                handler = InMemoryReview(self.server, b'{', '/regions')
                handler.headers.replace_header(header, value)
                handler.handle_post()
                self.assertEqual(handler.response[0], 403)
                self.assertEqual(self.server.ticket, 'test-ticket')
                self.assertEqual(self.server.source, b'synthetic previous document')
                self.assertEqual(len(self.server.document_context), 1)

    def test_regions_use_previous_snapshot_and_issue_fresh_authority(self):
        regions = [dict(page=1, bbox=[0, 0, 580, 220], label='synthetic')]
        previous_pages = self.server.pages
        handler = InMemoryReview(self.server, {'ticket': 'test-ticket', 'regions': regions}, '/regions')
        def extraction(source, requested):
            self.assertIsNone(self.server.ticket)
            self.assertIsNone(self.server.source)
            self.assertEqual(self.server.pages, [])
            self.assertEqual(source, b'synthetic previous document')
            self.assertEqual(requested, regions)
            return previous_pages
        with patch('blood_gas_local.safe_extract', side_effect=extraction):
            handler.handle_post()
        self.assertEqual(handler.response[0], 200)
        self.assertNotEqual(self.server.ticket, 'test-ticket')
        old = InMemoryReview(self.server, self.fixture.request)
        old.handle_post()
        self.assertEqual(old.response[0], 422)

    def test_worker_failure_leaves_no_previous_or_new_document(self):
        handler = InMemoryReview(self.server, b'synthetic failed upload', '/extract')
        with patch('blood_gas_local.safe_extract', side_effect=ValueError('synthetic rejection')):
            handler.handle_post()
        self.assertEqual(handler.response[0], 422)
        self.assert_revoked()

    def test_failed_delivery_revokes_new_document(self):
        class Disconnected(InMemoryReview):
            def reply(self, status, data, mime):
                if status == 200:
                    raise ConnectionError('synthetic client disconnected')
                super().reply(status, data, mime)
        handler = Disconnected(self.server, b'synthetic new document', '/extract')
        with patch('blood_gas_local.safe_extract', return_value=self.server.pages):
            handler.handle_post()
        self.assertEqual(handler.response[0], 422)
        self.assert_revoked()


if __name__ == '__main__':
    unittest.main()
