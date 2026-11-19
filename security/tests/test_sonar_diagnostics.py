"""Exercise the actual urllib dispatch without sending a credential to a network."""
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import importlib.util
import io
import json
import os
from pathlib import Path
import ssl
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPSHandler
from urllib.response import addinfourl


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/security/sonar_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("sonar_diagnostics", SCRIPT)
DIAGNOSTICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIAGNOSTICS)
TOKEN = "synthetic-credential-never-export-this"
ENV = {"SONAR_TOKEN": TOKEN, "SONAR_PULL_REQUEST": "33", "GITHUB_EVENT_NAME": "pull_request"}
GATE = {"projectStatus": {"status": "ERROR", "conditions": [
    {"status": "ERROR", "metricKey": "new_security_rating", "comparator": "GT",
     "errorThreshold": "1", "actualValue": "5", "source": "SOURCE_SENTINEL"}]}}
ISSUE = {"rule": "python:S0000", "component": "JuanCopado_Emergency:synthetic.py",
         "line": 7, "severity": "BLOCKER", "message": "Synthetic diagnostic",
         "source": "SOURCE_SENTINEL", "flows": [{"code": "SOURCE_SENTINEL"}]}


class SonarDiagnosticsTests(unittest.TestCase):
    def run_helper(self, payloads, environment=None, argv=()):
        requests = []
        contexts = []
        pending = list(payloads)

        class SyntheticHTTPS(HTTPSHandler):
            def __init__(self, **kwargs):
                contexts.append(kwargs["context"])
                super().__init__(**kwargs)

            def https_open(self, request):
                requests.append(request)
                payload = pending.pop(0)
                if isinstance(payload, Exception):
                    raise payload
                status, headers, body = payload if isinstance(payload, tuple) else (
                    200, {"Content-Type": "application/json"}, json.dumps(payload).encode())
                message = Message()
                for key, value in headers.items():
                    message[key] = value
                response = addinfourl(io.BytesIO(body), message, request.full_url, status)
                response.msg = "Synthetic response"
                return response

        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, ENV if environment is None else environment, clear=True), \
                patch.object(DIAGNOSTICS, "HTTPSHandler", SyntheticHTTPS), \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = DIAGNOSTICS.main(list(argv))
        output = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn(TOKEN, output)
        self.assertNotIn("SOURCE_SENTINEL", output)
        return code, json.loads(stdout.getvalue()), requests, contexts

    def test_fixed_https_get_pr_and_allowlisted_metadata(self):
        code, data, requests, contexts = self.run_helper([GATE, {"total": 1, "issues": [ISSUE]}])
        self.assertEqual(code, 0)
        self.assertEqual(data["diagnostic_status"], "COLLECTED")
        self.assertEqual(set(data), {"diagnostic_status", "conditions", "issues", "issues_truncated", "context"})
        self.assertEqual(set(data["issues"][0]), set(DIAGNOSTICS.ISSUE_FIELDS))
        self.assertEqual(set(data["conditions"][0]), set(DIAGNOSTICS.CONDITION_FIELDS))
        for request in requests:
            url = urlsplit(request.full_url)
            self.assertEqual((url.scheme, url.netloc), ("https", "sonarcloud.io"))
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual(request.get_header("Authorization"), "Bearer " + TOKEN)
            self.assertEqual(parse_qs(url.query)["pullRequest"], ["33"])
            self.assertEqual(request.timeout, DIAGNOSTICS.TIMEOUT)
            self.assertNotIn(TOKEN, request.full_url)
        self.assertTrue(all(context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
                            for context in contexts))
        self.assertEqual(parse_qs(urlsplit(requests[1].full_url).query)["organization"], ["juancopado"])

    def test_redirect_never_forwards_authorization(self):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                response = (status, {"Location": "https://untrusted.invalid/collect?" + TOKEN},
                            ("SOURCE_SENTINEL " + TOKEN).encode())
                code, data, requests, _ = self.run_helper([response])
                self.assertEqual(code, 2)
                self.assertEqual(data["diagnostic_status"], "UNAVAILABLE")
                self.assertEqual(data["failure"], {"stage": "gate", "code": "HTTP_STATUS", "http_status": status})
                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0].host, "sonarcloud.io")

    def test_ambient_proxy_and_host_overrides_are_not_used(self):
        env = {**ENV, "HTTPS_PROXY": "http://untrusted.invalid:8080", "NO_PROXY": "",
               "SONAR_HOST_URL": "https://untrusted.invalid", "SONAR_PROJECT_KEY": "untrusted",
               "SONAR_ORGANIZATION": "untrusted"}
        code, _, requests, _ = self.run_helper([GATE, {"total": 0, "issues": []}], env)
        self.assertEqual(code, 0)
        self.assertTrue(all(request.host == "sonarcloud.io" for request in requests))
        self.assertEqual(parse_qs(urlsplit(requests[0].full_url).query)["projectKey"],
                         [DIAGNOSTICS.PROJECT])
        self.assertEqual(parse_qs(urlsplit(requests[1].full_url).query)["organization"], ["juancopado"])

    def test_invalid_selection_and_header_credentials_make_no_request(self):
        invalid = [{**ENV, "SONAR_PULL_REQUEST": value} for value in ("-1", "33&branch=other", "３３", "33.0", "")]
        invalid += [{**ENV, "SONAR_TOKEN": value} for value in ("", TOKEN + "\nInjected: value")]
        invalid += [{"SONAR_TOKEN": TOKEN, "GITHUB_REF_NAME": value} for value in ("", " topic", "topic\nother")]
        invalid.append({"SONAR_TOKEN": TOKEN, "GITHUB_REF_NAME": "v1", "GITHUB_REF_TYPE": "tag"})
        for env in invalid:
            with self.subTest(env_keys=sorted(env)):
                code, _, requests, _ = self.run_helper([], env)
                self.assertEqual(code, 2)
                self.assertEqual(requests, [])

    def test_exact_branch_context_and_declared_limit(self):
        branch = "codex/integrate-t05-t06-20261119"
        env = {"SONAR_TOKEN": TOKEN, "GITHUB_REF_NAME": branch, "GITHUB_REF_TYPE": "branch",
               "GITHUB_SHA": "a" * 40, "GITHUB_RUN_ID": "44533322847"}
        first = {"paging": {"total": 101}, "issues": [ISSUE] * 100}
        code, data, requests, _ = self.run_helper([GATE, first], env)
        self.assertEqual(code, 0)
        self.assertEqual(len(data["issues"]), 100)
        self.assertTrue(data["issues_truncated"])
        self.assertEqual(data["context"], {"branch": branch, "github_sha": "a" * 40,
                                           "github_run_id": "44533322847"})
        self.assertTrue(all(parse_qs(urlsplit(request.full_url).query)["branch"] == [branch]
                            for request in requests))
        self.assertEqual(len(requests), 2)

    def test_token_echo_is_redacted_even_in_allowlisted_fields(self):
        issue = {**ISSUE, "message": "Do not disclose " + TOKEN}
        code, data, _, _ = self.run_helper([GATE, {"total": 1, "issues": [issue]}])
        self.assertEqual(code, 0)
        self.assertEqual(data["issues"][0]["message"], "Do not disclose [REDACTED]")

    def test_transport_errors_and_raw_bodies_are_static(self):
        errors = [OSError(TOKEN + " SOURCE_SENTINEL"),
                  HTTPError("https://sonarcloud.io/?" + TOKEN, 403, TOKEN, Message(), io.BytesIO(b"SOURCE_SENTINEL")),
                  (200, {"Content-Type": "application/json"}, ("{ " + TOKEN).encode()),
                  (200, {"Content-Type": "text/html"}, b"SOURCE_SENTINEL")]
        for error, expected_code in zip(errors, ("TRANSPORT_ERROR", "HTTP_STATUS", "JSON_INVALID", "CONTENT_TYPE")):
            with self.subTest(kind=type(error).__name__):
                code, data, _, _ = self.run_helper([error])
                self.assertEqual(code, 2)
                self.assertEqual(data["diagnostic_status"], "UNAVAILABLE")
                self.assertEqual(data["failure"]["stage"], "gate")
                self.assertEqual(data["failure"]["code"], expected_code)
                self.assertEqual(data["conditions"], [])
                self.assertEqual(data["issues"], [])

    def test_issue_http_failure_is_distinguished_without_server_text(self):
        error = HTTPError("https://sonarcloud.io/?" + TOKEN, 403, TOKEN, Message(), io.BytesIO(b"SOURCE_SENTINEL"))
        code, data, requests, _ = self.run_helper([GATE, error])
        self.assertEqual(code, 2)
        self.assertEqual(len(requests), 2)
        self.assertEqual(data["failure"], {"stage": "issues", "code": "HTTP_STATUS", "http_status": 403})

    def test_http_400_exports_only_redacted_validation_messages(self):
        payload = {"errors": [
            {"msg": "The 'organization' parameter is missing.", "source": "SOURCE_SENTINEL"},
            {"msg": "Reflected " + TOKEN + " at https://untrusted.invalid/" + TOKEN},
            {"msg": "Credentials Bearer synthetic-other-secret and squ_shortsecret "
                    "and abcdef0123456789abcdef0123456789"}], "source": "SOURCE_SENTINEL"}
        response = (400, {"Content-Type": "application/json"}, json.dumps(payload).encode())
        code, data, requests, _ = self.run_helper([GATE, response])
        self.assertEqual(code, 2)
        self.assertEqual(len(requests), 2)
        self.assertEqual(data["failure"], {
            "stage": "issues", "code": "HTTP_STATUS", "http_status": 400,
            "validation_messages": ["The 'organization' parameter is missing.",
                                    "Reflected [REDACTED] at [REDACTED]",
                                    "Credentials [REDACTED] and [REDACTED] and [REDACTED]"]})

    def test_validation_messages_have_body_count_and_combined_character_limits(self):
        short = {"errors": [{"msg": str(index)} for index in range(4)]}
        _, data, _, _ = self.run_helper([(400, {"Content-Type": "application/json"},
                                         json.dumps(short).encode())])
        self.assertEqual(data["failure"]["validation_messages"], ["0", "1", "2"])
        payload = {"errors": [{"msg": "Validation message. " * 20}] * 4}
        response = (400, {"Content-Type": "application/json"}, json.dumps(payload).encode())
        _, data, _, _ = self.run_helper([response])
        messages = data["failure"]["validation_messages"]
        self.assertLessEqual(len(messages), 3)
        self.assertEqual(sum(map(len, messages)), 512)
        for body in (b" " * (DIAGNOSTICS.MAX_ERROR_BYTES + 1), b"SOURCE_SENTINEL",
                     b'{"errors":[],"errors":[{"msg":"SOURCE_SENTINEL"}]}'):
            with self.subTest(length=len(body)):
                _, data, _, _ = self.run_helper([(400, {"Content-Type": "application/json"}, body)])
                self.assertNotIn("validation_messages", data["failure"])

    def test_response_limits_and_ambiguous_json_rejected(self):
        bodies = [b" " * (DIAGNOSTICS.MAX_BYTES + 1), b'{"projectStatus":{},"projectStatus":{}}',
                  b'{"projectStatus":{"conditions":[NaN]}}', b'[]', b'\xff']
        for body in bodies:
            with self.subTest(length=len(body)):
                code, _, _, _ = self.run_helper([(200, {"Content-Type": "application/json"}, body)])
                self.assertEqual(code, 2)
        for result in ({"total": 501, "issues": []}, {"total": True, "issues": []},
                       {"total": 1, "issues": []}, {"total": 0, "issues": [ISSUE]},
                       {"total": 1, "issues": [{**ISSUE, "line": True}]}):
            code, _, _, _ = self.run_helper([GATE, result])
            self.assertEqual(code, 2)

    def test_no_command_line_or_arbitrary_endpoint_capability(self):
        code, _, requests, _ = self.run_helper([], argv=("--token", TOKEN))
        self.assertEqual(code, 2)
        self.assertEqual(requests, [])
        with self.assertRaises(DIAGNOSTICS.DiagnosticError):
            DIAGNOSTICS.request_json(None, "https://untrusted.invalid", {}, TOKEN)


if __name__ == "__main__":
    unittest.main()
