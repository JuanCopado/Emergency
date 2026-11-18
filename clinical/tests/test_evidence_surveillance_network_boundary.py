"""Offline boundary tests: no real HTTP requests or clinical records."""
import ipaddress
import json
import pathlib
import socket
import sys
import tempfile
import unittest
import urllib.parse
from unittest.mock import Mock, patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_surveillance as es


class _Response:
    status = 200

    def __init__(self, url, content=b"synthetic"):
        self.url = url
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self, size):
        return self.content[:size]


class SurveillanceNetworkBoundaryTests(unittest.TestCase):
    PUBLIC_DNS = [(socket.AF_INET, socket.SOCK_STREAM, 6, "",
                   ("93.184.216.34", 443))]

    def test_all_current_catalog_hosts_are_explicitly_vetted(self):
        data = json.loads(es.DEFAULT_SOURCES.read_text(encoding="utf-8"))
        hosts = {urllib.parse.urlsplit(row["url"]).hostname for row in data["sources"]}
        self.assertTrue(hosts)
        self.assertTrue(hosts.issubset(es.APPROVED_EVIDENCE_HOSTS))

    def test_unapproved_urls_rejected_before_dns_or_network(self):
        malicious = (
            "http://www.who.int/guidance",
            "https://127.0.0.1/admin",
            "https://169.254.169.254/latest/meta-data",
            "https://[::1]/",
            "https://localhost/",
            "https://evil.example/test",
            "https://www.who.int.evil.example/",
            "https://www.who.int@127.0.0.1/",
            "https://user:pass@www.who.int/",
            "https://www.who.int:8443/",
            "https://www.who.int/#fragment",
            "file:///etc/passwd",
            "https://www.who.int/a\nInjected: yes",
            "https://www.who.int/\u202e",
        )
        with patch.object(es.socket, "getaddrinfo",
                          side_effect=AssertionError("DNS must not run")), \
             patch.object(es.urllib.request, "build_opener",
                          side_effect=AssertionError("HTTP must not run")):
            for url in malicious:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    es.fetch(url)

    def test_reject_private_or_mixed_dns_addresses_before_http(self):
        private = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.4.5.6", 443)),
        ]
        with patch.object(es.urllib.request, "build_opener",
                          side_effect=AssertionError("HTTP must not run")):
            for addresses in (private, self.PUBLIC_DNS + private, []):
                with self.subTest(addresses=addresses), \
                     patch.object(es.socket, "getaddrinfo", return_value=addresses), \
                     self.assertRaises(ValueError):
                    es.fetch("https://www.who.int/publications/who-guidelines")

    def test_public_source_fetch_uses_reject_redirect_handler(self):
        url = "https://www.who.int/publications/who-guidelines"
        opener = Mock()
        opener.open.return_value = _Response(url, b"synthetic")
        with patch.object(es.socket, "getaddrinfo",
                          return_value=self.PUBLIC_DNS), \
             patch.object(es.urllib.request, "build_opener",
                          return_value=opener) as factory:
            self.assertEqual(b"synthetic", es.fetch(url))
        self.assertTrue(any(isinstance(h, es._RejectRedirects)
                            for h in factory.call_args.args))
        handler = es._RejectRedirects()
        self.assertIsNone(handler.redirect_request(
            None, None, 302, "Found", {}, "http://127.0.0.1/"))
        self.assertEqual("GET", opener.open.call_args.args[0].get_method())

    def test_response_size_limit_and_falsified_final_host(self):
        original = "https://www.who.int/publications/who-guidelines"
        opener = Mock()
        with patch.object(es.socket, "getaddrinfo", return_value=self.PUBLIC_DNS), \
             patch.object(es.urllib.request, "build_opener", return_value=opener):
            opener.open.return_value = _Response(original, b"x" * 5_000_001)
            with self.assertRaisesRegex(ValueError, "size cap"):
                es.fetch(original)
            opener.open.return_value = _Response("https://evil.example/", b"x")
            with self.assertRaises(ValueError):
                es.fetch(original)

    def test_failure_report_does_not_echo_exception_details(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "sources.json"
            path.write_text(json.dumps({"sources": [{
                "id": "synthetic", "organization": "Test",
                "url": "https://www.who.int/publications/who-guidelines",
                "cadence": "weekly", "authority_type": "formal-guideline-body"
            }]}), encoding="utf-8")
            with patch.object(es, "fetch",
                              side_effect=RuntimeError("PRIVATE_SYNTHETIC_IDENTIFIER")):
                result = es.run(path)
            self.assertEqual("error", result["sources"]["synthetic"]["status"])
            self.assertNotIn("PRIVATE_SYNTHETIC_IDENTIFIER",
                             result["sources"]["synthetic"]["error"])
            self.assertFalse(result["production_changes_applied"])


if __name__ == "__main__":
    unittest.main()
