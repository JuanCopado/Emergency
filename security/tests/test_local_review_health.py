"""Exercise launcher health probes against real, synthetic loopback servers."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
import importlib.util
import os
from pathlib import Path
from threading import Thread
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/run_local_review.py'
SPEC = importlib.util.spec_from_file_location('run_local_review', SCRIPT)
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)


class ProbeHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def setup(self):
        super().setup()
        self.connection.settimeout(1)

    def log_message(self, *args):
        pass

    def do_GET(self):
        self.server.requests.append({'path': self.path, 'headers': dict(self.headers)})
        self.send_response(self.server.reply_status)
        if self.server.redirect_to:
            self.send_header('Location', self.server.redirect_to)
        self.send_header('Content-Length', '0')
        self.end_headers()


@contextmanager
def loopback_server():
    server = HTTPServer(('127.0.0.1', 0), ProbeHandler)
    server.requests = []
    server.reply_status = 200
    server.redirect_to = None
    thread = Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


class LocalReviewHealthTests(unittest.TestCase):
    def test_actual_redirect_is_not_followed_and_only_200_is_ready(self):
        with loopback_server() as destination, loopback_server() as source:
            target = f'http://127.0.0.1:{destination.server_port}/unexpected'
            source.redirect_to = target
            proxy_env = {name: target for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
                                                  'http_proxy', 'https_proxy', 'all_proxy')}
            proxy_env.update(NO_PROXY='', no_proxy='')
            with patch.dict(os.environ, proxy_env):
                for status in (302, 204, 503):
                    with self.subTest(status=status):
                        source.reply_status = status
                        self.assertFalse(LAUNCHER.service_ready('app', source.server_port))
                        self.assertEqual(destination.requests, [])
                source.reply_status = 200
                source.redirect_to = None
                self.assertTrue(LAUNCHER.service_ready('app', source.server_port))
            self.assertEqual(destination.requests, [])
            self.assertEqual(len(source.requests), 4)
            for request in source.requests:
                self.assertEqual(request['path'], '/')
                self.assertEqual(request['headers']['Host'], f'127.0.0.1:{source.server_port}')
                self.assertEqual(request['headers']['Origin'], f'http://127.0.0.1:{source.server_port}')
                self.assertEqual(request['headers']['X-Emergency-T06-Lab'], 'synthetic-loopback')

    def test_invalid_port_or_service_is_rejected_before_connecting(self):
        invalid = (-1, 0, 1023, 65536, 8765, 8766, 8767, True, False, 5173.5,
                   '5173', '5173@untrusted.invalid', None)
        with patch.object(LAUNCHER, 'HTTPConnection') as connection:
            for port in invalid:
                with self.subTest(port=port), self.assertRaises(ValueError):
                    LAUNCHER.service_ready('app', port)
            with self.assertRaises(ValueError):
                LAUNCHER.service_ready('https://untrusted.invalid/', 5173)
            connection.assert_not_called()


if __name__ == '__main__':
    unittest.main()
