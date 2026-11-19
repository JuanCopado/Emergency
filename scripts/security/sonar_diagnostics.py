"""Read fixed-project Sonar diagnostics; never change issues or the quality gate.

SONAR_TOKEN is read only from the environment. Set SONAR_PULL_REQUEST for a PR;
otherwise GITHUB_REF_NAME must identify the exact GitHub branch being analysed.
Only allowlisted issue metadata is emitted, never source, response bodies or tokens.
"""
import json
import os
import re
import ssl
import sys
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import (HTTPSHandler, HTTPRedirectHandler, ProxyHandler,
                            Request, build_opener)


ORIGIN = "https://sonarcloud.io"
PROJECT = "JuanCopado_Emergency"
TIMEOUT = 15
MAX_BYTES = 1_000_000
PAGE_SIZE = 100
ENDPOINTS = {"/api/qualitygates/project_status", "/api/issues/search"}
CONDITION_FIELDS = ("status", "metricKey", "comparator", "errorThreshold", "actualValue")
ISSUE_FIELDS = ("rule", "component", "line", "severity", "message")


class DiagnosticError(Exception):
    """Deliberately carries no server, environment or request data."""


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def selector(environment):
    number = environment.get("SONAR_PULL_REQUEST", "")
    if number:
        if not re.fullmatch(r"[1-9][0-9]{0,9}", number, flags=re.ASCII):
            raise DiagnosticError()
        return {"pullRequest": number}
    branch = environment.get("GITHUB_REF_NAME", "")
    if (environment.get("GITHUB_EVENT_NAME", "").startswith("pull_request")
            or environment.get("GITHUB_REF_TYPE", "branch") != "branch"
            or not branch or len(branch) > 255 or branch != branch.strip()
            or any(ord(char) < 32 or ord(char) == 127 for char in branch)):
        raise DiagnosticError()
    return {"branch": branch}


def public_context(environment):
    result = selector(environment)
    for source, target, pattern in (("GITHUB_SHA", "github_sha", r"[a-fA-F0-9]{40}"),
                                    ("GITHUB_RUN_ID", "github_run_id", r"[1-9][0-9]{0,19}")):
        value = environment.get(source, "")
        if value:
            if not re.fullmatch(pattern, value, flags=re.ASCII):
                raise DiagnosticError()
            result[target] = value
    token = environment.get("SONAR_TOKEN", "")
    return {key: value.replace(token, "[REDACTED]") if token else value
            for key, value in result.items()}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DiagnosticError()
        result[key] = value
    return result


def reject_constant(_value):
    raise DiagnosticError()


def request_json(opener, endpoint, parameters, token, progress=None):
    if endpoint not in ENDPOINTS:
        raise DiagnosticError()
    progress = {} if progress is None else progress
    progress.clear()
    progress.update(stage="gate" if endpoint.endswith("project_status") else "issues",
                    code="TRANSPORT_ERROR")
    request = Request(ORIGIN + endpoint + "?" + urlencode(parameters), method="GET",
                      headers={"Authorization": "Bearer " + token,
                               "Accept": "application/json"})
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            progress.update(code="HTTP_STATUS", http_status=response.status)
            if response.status != 200:
                raise DiagnosticError()
            progress["code"] = "CONTENT_TYPE"
            if response.headers.get_content_type() != "application/json":
                raise DiagnosticError()
            progress["code"] = "CONTENT_ENCODING"
            if response.headers.get("Content-Encoding", "identity").lower() != "identity":
                raise DiagnosticError()
            progress["code"] = "RESPONSE_READ"
            body = response.read(MAX_BYTES + 1)
    except HTTPError as error:
        progress.update(code="HTTP_STATUS", http_status=error.code)
        error.close()
        raise DiagnosticError() from None
    progress["code"] = "BODY_LIMIT"
    if len(body) > MAX_BYTES:
        raise DiagnosticError()
    progress["code"] = "JSON_INVALID"
    value = json.loads(body.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise DiagnosticError()
    return value


def public_fields(value, fields, token):
    if not isinstance(value, dict):
        raise DiagnosticError()
    result = {}
    for field in fields:
        if field not in value:
            continue
        item = value[field]
        if field == "line":
            if item is None:
                continue
            if type(item) is not int or item < 1:
                raise DiagnosticError()
        elif not isinstance(item, str) or len(item) > 4096:
            raise DiagnosticError()
        else:
            item = item.replace(token, "[REDACTED]")
        result[field] = item
    return result


def collect(environment, progress):
    token = environment.get("SONAR_TOKEN", "")
    if not token or len(token) > 4096 or any(not 33 <= ord(char) <= 126 for char in token):
        raise DiagnosticError()
    selected = selector(environment)
    if any(token in value for value in selected.values()):
        raise DiagnosticError()
    opener = build_opener(ProxyHandler({}),
                          HTTPSHandler(context=ssl.create_default_context()), NoRedirects())
    gate = request_json(opener, "/api/qualitygates/project_status",
                        {"projectKey": PROJECT, **selected}, token, progress)
    progress["code"] = "GATE_SCHEMA"
    conditions = gate["projectStatus"]["conditions"]
    if not isinstance(conditions, list) or len(conditions) > 50:
        raise DiagnosticError()
    result = {"diagnostic_status": "COLLECTED",
              "conditions": [public_fields(item, CONDITION_FIELDS, token) for item in conditions],
              "issues": []}
    data = request_json(opener, "/api/issues/search", {
        "componentKeys": PROJECT, **selected, "types": "VULNERABILITY",
        "resolved": "false", "ps": str(PAGE_SIZE), "p": "1"}, token, progress)
    progress["code"] = "ISSUE_SCHEMA"
    count = data.get("total", data.get("paging", {}).get("total"))
    issues = data.get("issues")
    if (type(count) is not int or count < 0 or not isinstance(issues, list)
            or len(issues) != min(count, PAGE_SIZE)):
        raise DiagnosticError()
    for item in issues:
        public = public_fields(item, ISSUE_FIELDS, token)
        if not {"rule", "component", "severity", "message"} <= public.keys():
            raise DiagnosticError()
        result["issues"].append(public)
    result["issues_truncated"] = count > PAGE_SIZE
    return result


def main(argv=None):
    context = {}
    progress = {"stage": "configuration", "code": "INVALID_CONFIGURATION"}
    try:
        if (sys.argv[1:] if argv is None else argv):
            raise DiagnosticError()
        context = public_context(os.environ)
        result = collect(os.environ, progress)
        result["context"] = context
        progress.clear()
        progress.update(stage="output", code="OUTPUT_INVALID")
        encoded = json.dumps(result, ensure_ascii=True, allow_nan=False)
        if os.environ["SONAR_TOKEN"] in encoded:
            raise DiagnosticError()
    except Exception:
        # Never print exceptions: transport errors can contain credentials or bodies.
        print(json.dumps({"diagnostic_status": "UNAVAILABLE", "context": context,
                          "failure": progress, "conditions": [], "issues": []}, ensure_ascii=True))
        print("Sonar diagnostics unavailable; no raw response or credential was exported.", file=sys.stderr)
        return 2
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
