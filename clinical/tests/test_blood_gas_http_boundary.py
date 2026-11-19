"""Synthetic review requests: exact JSON meaning and composed/standalone origins.

These tests exercise the real decoder, handler and loopback server. They do not
replace the native worker tests or claim image extraction on this platform.
"""
import copy
import http.client
import json
import os
import socket
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import test_blood_gas_review_contract as fixture
from blood_gas_local import make_server, strict_json_object
from http_transport import BoundedHTTPServer, DeadlineRequestHandler


class JSONBoundary(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.ReviewContract()
        self.fixture.setUp()
        self.fixture.request['metadata'] = self.fixture.confirmed_metadata()
        self.server = self.fixture.server

    def review_bytes(self):
        return json.dumps(self.fixture.request).encode()

    def send(self, body, route='/review'):
        handler = fixture.InMemoryReview(self.server, body, route)
        handler.handle_post()
        return handler.response

    def test_duplicate_confirmation_cannot_override_false(self):
        original = self.review_bytes()
        self.assertEqual(self.send(original)[0], 200)
        for gate in ('medicalConfirmed', 'areaConfirmed', 'oneSample'):
            with self.subTest(gate=gate):
                duplicate = original.replace(
                    ('"' + gate + '": true').encode(),
                    ('"' + gate + '": false, "' + gate + '": true').encode())
                self.assertEqual(self.send(duplicate)[0], 422)

    def test_nested_or_escaped_duplicate_keys_are_rejected(self):
        original = self.review_bytes()
        nested = original.replace(b'"review": "confirmed"',
                                  b'"review": "rejected", "review": "confirmed"', 1)
        escaped = original.replace(b'"medicalConfirmed": true',
                                   b'"medicalConfirmed": false, "medical\\u0043onfirmed": true')
        for payload in (nested, escaped):
            with self.subTest(payload=payload):
                self.assertEqual(self.send(payload)[0], 422)

    def test_nonfinite_and_lexical_underflow_are_rejected_before_review(self):
        original = self.review_bytes()
        for token in ('NaN', 'Infinity', '-Infinity', '1e999', '1e-999', '-1e-999'):
            with self.subTest(token=token):
                payload = original[:-1] + b', "syntheticProbe":' + token.encode() + b'}'
                self.assertEqual(self.send(payload)[0], 422)

    def test_zero_and_representable_subnormal_are_not_reclassified(self):
        decoded = strict_json_object(b'{"zero":0,"negative_zero":-0.0,"tiny":5e-324}')
        self.assertEqual(decoded['zero'], 0)
        self.assertEqual(decoded['negative_zero'], 0)
        self.assertGreater(decoded['tiny'], 0)
        self.assertEqual(strict_json_object(b'{"literal":"1e-999"}'), {'literal': '1e-999'})

    def test_only_utf8_json_objects_are_accepted(self):
        for payload in (b'[]', b'null', b'true', b'"text"', b'{} trailing', b'{"x":"\xff"}'):
            with self.subTest(payload=payload):
                self.assertEqual(self.send(payload)[0], 422)

    def test_regions_and_reject_use_the_same_strict_decoder(self):
        previous = b'synthetic source, not a clinical document'
        self.server.source = previous
        duplicate = b'{"ticket":"wrong","ticket":"test-ticket"}'
        self.assertEqual(self.send(duplicate, '/reject')[0], 422)
        self.assertEqual(self.server.ticket, 'test-ticket')
        self.assertEqual(self.server.source, previous)
        self.server.sample_sources = []
        self.server.document_context = []
        with patch('blood_gas_local.safe_extract') as worker:
            self.assertEqual(self.send(duplicate, '/regions')[0], 422)
            worker.assert_not_called()
        self.assertIsNone(self.server.ticket)
        self.assertIsNone(self.server.source)


class HTTPBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(ui_port=5173)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def setUp(self):
        self.fixture = fixture.ReviewContract()
        self.fixture.setUp()
        self.fixture.request['metadata'] = self.fixture.confirmed_metadata()
        self.server.ticket = self.fixture.server.ticket
        self.server.pages = copy.deepcopy(self.fixture.server.pages)
        self.server.source = b'synthetic source'
        self.server.document_context = []
        self.server.sample_sources = []
        self.body = json.dumps(self.fixture.request).encode()

    def request(self, method='POST', route='/review', body=None, headers=None, server=None):
        server = server or self.server
        body = self.body if body is None and method == 'POST' else body
        defaults = [
            ('Host', server.address), ('Origin', 'http://127.0.0.1:5173'),
            ('X-Session', server.token), ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body or b''))),
        ]
        connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
        try:
            connection.putrequest(method, '/api/blood-gas' + route, skip_host=True)
            for name, value in defaults if headers is None else headers:
                connection.putheader(name, value)
            connection.endheaders(body)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def headers(self, **replace):
        headers = {'Host': self.server.address, 'Origin': 'http://127.0.0.1:5173',
                   'X-Session': self.server.token, 'Content-Type': 'application/json',
                   'Content-Length': str(len(self.body))}
        headers.update(replace)
        return [(key, value) for key, value in headers.items() if value is not None]

    def test_review_accepts_configured_ui_and_own_origin_with_session(self):
        for origin in ('http://127.0.0.1:5173', 'http://' + self.server.address):
            with self.subTest(origin=origin):
                status, headers, data = self.request(headers=self.headers(Origin=origin))
                self.assertEqual(status, 200)
                self.assertEqual(json.loads(data)['clinical_status'], 'CLINICALLY_PENDING')
                self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertIsInstance(self.server, BoundedHTTPServer)
        self.assertTrue(issubclass(self.server.RequestHandlerClass, DeadlineRequestHandler))
        self.assertEqual(self.server.request_timeout, 10.0)

    def test_json_response_keeps_markup_as_data_and_preserves_review_round_trip(self):
        status, _, data = self.request()
        self.assertEqual(status, 200)
        baseline = json.loads(data)
        probes = (
            '</script><img src=x onerror="synthetic()"> & clinical trace',
            '&lt; &gt; &amp; &#60; &amp;lt; literal \\u003c',
            'pH < 7.2 & FiO₂ > 0.21 — razón "visual" \\ \n\t\x00 🩺',
            'preserved JSON surrogate: \ud800',
        )
        for probe in probes:
            with self.subTest(probe=probe):
                self.fixture.request['metadata'][0]['reason'] = probe
                self.server.pages[0]['fields'][0]['raw'] = probe
                self.body = json.dumps(self.fixture.request).encode()
                status, headers, data = self.request()
                self.assertEqual(status, 200)
                expected = copy.deepcopy(baseline)
                expected['reviewed_metadata'][0]['reason'] = probe
                expected['review_provenance']['fields'][0]['raw'] = probe
                self.assertEqual(json.loads(data), expected)
                self.assertEqual(headers['Content-Type'], 'application/json')
                self.assertEqual(int(headers['Content-Length']), len(data))
                self.assertEqual(headers['Cache-Control'], 'no-store')
                self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
                for markup in (b'<', b'>', b'&'):
                    self.assertNotIn(markup, data)

    def test_absent_or_empty_origin_configuration_fails_closed(self):
        allowed = self.server.allowed_origins
        try:
            for configuration in (None, set(), 'absent'):
                with self.subTest(configuration=configuration):
                    if configuration == 'absent':
                        del self.server.allowed_origins
                    else:
                        self.server.allowed_origins = configuration
                    for method, route in (('GET', '/session'), ('POST', '/review')):
                        origin = None if method == 'GET' else 'http://' + self.server.address
                        status, _, data = self.request(method=method, route=route,
                                                       headers=self.headers(Origin=origin))
                        self.assertEqual(status, 403)
                        self.assertEqual(json.loads(data), {'error': 'Solicitud HTTP no admisible'})
                    self.assertEqual(self.server.ticket, 'test-ticket')
                    self.assertEqual(self.server.source, b'synthetic source')
        finally:
            self.server.allowed_origins = allowed

    def test_unconfigured_or_ambiguous_browser_authority_is_denied(self):
        rejected = [self.headers(Origin=value) for value in (
            None, 'null', 'http://localhost:5173', 'http://127.0.0.1:5174',
            'https://127.0.0.1:5173', 'http://127.0.0.1:5173.evil.invalid')]
        rejected += [self.headers(**{'Host': 'untrusted.invalid'}),
                     self.headers(**{'X-Session': 'wrong'}),
                     self.headers(**{'Sec-Fetch-Site': 'cross-site'})]
        for name, value in (('Host', self.server.address), ('Origin', 'http://127.0.0.1:5173'),
                            ('X-Session', self.server.token), ('Sec-Fetch-Site', 'cross-site')):
            rejected.append(self.headers(**{'Sec-Fetch-Site': 'same-origin'}) + [(name, value)])
        for headers in rejected:
            with self.subTest(headers=headers):
                self.assertEqual(self.request(headers=headers)[0], 403)
                self.assertEqual(self.server.ticket, 'test-ticket')

    def test_json_media_and_framing_are_checked_before_clinical_review(self):
        cases = [
            (self.headers(**{'Content-Type': None}), 415),
            (self.headers(**{'Content-Type': 'text/plain'}), 415),
            (self.headers(**{'Content-Encoding': 'gzip'}), 415),
            (self.headers(**{'Transfer-Encoding': 'chunked'}), 400),
            (self.headers(**{'Content-Length': None}), 411),
            (self.headers() + [('Content-Length', str(len(self.body)))], 400),
            (self.headers() + [('Content-Type', 'application/json')], 415),
        ]
        for headers, expected in cases:
            with self.subTest(expected=expected, headers=headers):
                self.assertEqual(self.request(headers=headers)[0], expected)

    def test_binary_upload_is_preserved_and_not_decoded_as_json(self):
        body = b'synthetic document bytes, intentionally not JSON'
        headers = self.headers(**{'Content-Type': 'application/octet-stream',
                                  'Content-Length': str(len(body))})
        with patch('blood_gas_local.safe_extract', return_value=self.server.pages) as worker:
            status, _, data = self.request(route='/extract', body=body, headers=headers)
        self.assertEqual(status, 200)
        worker.assert_called_once_with(body, None)
        self.assertIn('ticket', json.loads(data))

    def test_session_get_is_not_exposed_to_untrusted_browser_origin(self):
        status, _, data = self.request(method='GET', route='/session', headers=self.headers(Origin=None))
        self.assertEqual(status, 200)
        payload = json.loads(data)
        self.assertTrue(payload['synthetic_only'])
        self.assertIs(payload['extraction_available'], os.name == 'nt')
        self.assertEqual(payload['required_platform'], 'win32')
        self.assertEqual(self.request(method='GET', route='/session', headers=self.headers(
            Origin='https://untrusted.invalid'))[0], 403)

    def test_protocol_errors_are_static_json_and_head_has_no_body(self):
        marker = b'<img/src=x/onerror=synthetic()>&private-marker'
        with socket.create_connection(('127.0.0.1', self.server.server_port), timeout=5) as connection:
            connection.sendall(b'GET / HTTP/' + marker + b'\r\n\r\n')
            raw = b''
            while chunk := connection.recv(4096):
                raw += chunk
        self.assertIn(b'400 Bad Request', raw)
        self.assertNotIn(marker, raw)
        self.assertIn(b'Content-Type: application/json', raw)
        self.assertIn(b'Cache-Control: no-store', raw)
        self.assertIn(b'Content-Security-Policy:', raw)
        self.assertEqual(json.loads(raw.split(b'\r\n\r\n', 1)[1]),
                         {'error': 'Solicitud HTTP no admisible'})
        status, headers, body = self.request(method='HEAD', route='/session',
                                              headers=self.headers(Origin=None))
        self.assertEqual(status, 501)
        self.assertEqual(body, b'')
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(int(headers['Content-Length']), len(raw.split(b'\r\n\r\n', 1)[1]))
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')

    def test_rejected_review_and_unknown_route_do_not_reflect_submitted_markup(self):
        marker = '<script>synthetic-private-rejection</script>&'
        request = copy.deepcopy(self.fixture.request)
        request['medicalConfirmed'] = False
        request['metadata'][0]['reason'] = marker
        self.body = json.dumps(request).encode()
        status, headers, data = self.request()
        self.assertEqual(status, 422)
        self.assertEqual(json.loads(data), {'error': 'Documento o revision no admisible; revise muestra, campos, unidades y confirmaciones'})
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertNotIn(marker.encode(), data)
        status, headers, data = self.request(route='/unknown?' + marker)
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(data), {'error': 'Solicitud HTTP no admisible'})
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertNotIn(marker.encode(), data)

    def test_standalone_has_only_its_own_origin_and_keeps_ephemeral_marker(self):
        server = make_server()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            self.assertEqual(server.allowed_origins, {'http://' + server.address})
            self.assertEqual(self.request(server=server)[0], 403)
            with tempfile.TemporaryDirectory() as temporary:
                Path(temporary, 'index.html').write_text('<html><head></head><body></body></html>')
                asset = b'<svg xmlns="http://www.w3.org/2000/svg"><text>&amp;</text></svg>'
                Path(temporary, 'favicon.svg').write_bytes(asset)
                with patch('blood_gas_local.DIST', Path(temporary)):
                    connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                    try:
                        connection.request('GET', '/blood-gas')
                        response = connection.getresponse()
                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.getheader('Content-Type'), 'text/html; charset=utf-8')
                        self.assertIn(b'<meta name="blood-gas-local" content="synthetic-only">', response.read())
                    finally:
                        connection.close()
                    connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
                    try:
                        connection.request('GET', '/favicon.svg')
                        response = connection.getresponse()
                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.getheader('Content-Type'), 'image/svg+xml')
                        self.assertEqual(response.read(), asset)
                    finally:
                        connection.close()
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def test_ports_are_exact_integers_without_wildcard_or_remote_host(self):
        for value in (True, 0, -1, 65536, 5173.0, '5173', '0.0.0.0:5173'):
            with self.subTest(ui_port=value):
                with self.assertRaises(ValueError):
                    make_server(ui_port=value)
        for value in (True, -1, 65536, 5173.0, '5173', '0.0.0.0:5173'):
            with self.subTest(port=value):
                with self.assertRaises(ValueError):
                    make_server(port=value)


if __name__ == '__main__':
    unittest.main()
