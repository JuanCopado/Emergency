"""Synthetic HTTP errors through an actual loopback socket, no external network."""
import contextlib
import http.client
from http.server import ThreadingHTTPServer
import io
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'clinical/scripts'))
import clinical_note_api as api


class HttpSocketPrivacyTests(unittest.TestCase):
    def request(self, body, error=None):
        captured = io.StringIO()
        with contextlib.redirect_stderr(captured):
            server = ThreadingHTTPServer(('127.0.0.1', 0), api.ClinicalNoteHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with patch.object(api, 'dispatch', side_effect=error):
                    connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                    connection.request('POST', '/api/clinical-note/analyze?case=R3_PRIVATE_SYNTHETIC',
                                       body=body, headers={'Content-Type': 'application/json'})
                    response = connection.getresponse()
                    status, headers, result = response.status, dict(response.getheaders()), response.read()
                    connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
        self.assertNotIn('R3_PRIVATE_SYNTHETIC', captured.getvalue())
        self.assertNotIn(b'R3_PRIVATE_SYNTHETIC', result)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(headers['Referrer-Policy'], 'no-referrer')
        return status, result

    def test_invalid_json_over_http(self):
        self.assertEqual(self.request(b'{"note":')[0], 400)

    def test_value_error_is_redacted_over_http(self):
        self.assertEqual(self.request(b'{}', ValueError('R3_PRIVATE_SYNTHETIC')),
                         (422, b'{"error": "invalid clinical request"}'))

    def test_internal_error_is_redacted_over_http(self):
        self.assertEqual(self.request(b'{}', RuntimeError('R3_PRIVATE_SYNTHETIC')),
                         (500, b'{"error": "clinical-note backend failure"}'))


if __name__ == '__main__':
    unittest.main()
