"""Isolated PAR-02 laboratory: actual frozen R6 + B1 + synthetic TLS + JSON.

Not part of shared Emergency backend. No clinical decision support. Fixed test
scenarios are the only inputs. All Python socket destinations are loopback.
"""
from __future__ import annotations
import argparse
import dataclasses
import hashlib
import importlib.metadata
import ipaddress
import json
import logging
import os
from pathlib import Path
import signal
import socket
import ssl
import sys
import tempfile
import threading
import time
import traceback
from urllib.parse import parse_qs, urlsplit
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
# Reuse the audited shared transport without adding a clinical dispatch route.
sys.path.insert(0, str(HERE.parents[3] / "clinical/scripts"))
from http_transport import BoundedHTTPServer, DeadlineRequestHandler
DEFAULT_B1 = HERE.parents[1] / "recovered" / "b1"
SCENARIOS = (
    "success", "pubmed", "nvd", "long_text", "limit50", "limit51",
    "unsafe_unicode", "invalid_json", "invalid_utf8", "oversize", "http_error",
    "redirect", "timeout", "client_timeout", "retry_429", "invalid_normalized", "empty", "combined_limits",
)
ERRORS = {
    "invalid_request": "Solicitud de laboratorio no válida.",
    "request_too_large": "La solicitud supera el límite del laboratorio.",
    "upstream_error": "No se pudieron validar los metadatos del proveedor sintético.",
    "upstream_timeout": "El proveedor sintético superó el tiempo permitido.",
    "upstream_too_large": "La respuesta del proveedor sintético supera el límite permitido.",
    "redirect_blocked": "La redirección del proveedor sintético está bloqueada.",
    "not_found": "Ruta de laboratorio no disponible.",
    "method_not_allowed": "Método no permitido.",
    "internal_error": "Error interno del laboratorio.",
}

def audit_loopback(event, args):
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "socket.gethostbyaddr"}:
        if "RECORDER" in globals():
            RECORDER.event({"event": "python_socket_audit", "socket_event": event,
                            "pid": os.getpid(), "address": args[1] if event in {"socket.connect", "socket.bind"} else args[0]})
    if event in {"socket.connect", "socket.bind"}:
        address = args[1]
        if not (isinstance(address, tuple) and ipaddress.ip_address(address[0]).is_loopback):
            raise PermissionError("PAR02_LOOPBACK_ONLY")
    if event == "socket.getaddrinfo":
        host = args[0]
        if host not in {"127.0.0.1", "::1"}:
            raise PermissionError("PAR02_NO_PUBLIC_DNS")
    if event == "socket.gethostbyaddr" and args[0] not in {"127.0.0.1", "::1"}:
        raise PermissionError("PAR02_NO_PUBLIC_DNS")

def write_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n")
    temporary.replace(path)

class Recorder:
    def __init__(self, directory):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.receipts = []
    def event(self, value):
        with self.lock:
            with (self.directory / "events.jsonl").open("a") as stream:
                stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
    def receipt(self, value):
        with self.lock:
            self.receipts.append(value)
            write_json(self.directory / (value["request_id"] + ".json"), value)
    def status(self):
        with self.lock:
            return {
                "clinical_status": "CLINICALLY_PENDING",
                "scope": "synthetic_loopback_only",
                "completed_requests": len(self.receipts),
                "last_request_id": self.receipts[-1]["request_id"] if self.receipts else None,
                "completed_receipts_tls_requests_sum": sum(x.get("provider_requests") or 0 for x in self.receipts),
                "completed_receipts_with_unknown_provider_count": sum(x.get("provider_requests") is None for x in self.receipts),
                "completed_receipts_worker_live_sum": sum(x.get("worker_stats", {}).get("live", 0) for x in self.receipts),
                "active_worker_census": "not_collected",
                "runtime": RUNTIME,
                "scenarios": list(SCENARIOS),
            }

def payload(scenario, service, fixture_dir):
    if service == "pubmed":
        return (fixture_dir / "pubmed_esearch.json").read_bytes()
    if service == "nvd":
        if scenario == "combined_limits":
            data = {"resultsPerPage": 50, "startIndex": 0, "totalResults": 50, "vulnerabilities": [
                {"cve": {"id": "CVE-2026-" + str(1000+i),
                         "published": "2026-01-01", "lastModified": "2026-01-02",
                         "descriptions": [{"lang": "en", "value": "😀" * 1800}]}}
                for i in range(50)
            ]}
            return json.dumps(data, ensure_ascii=False).encode("utf-8")
        return (fixture_dir / "nvd_cves.json").read_bytes()
    data = json.loads((fixture_dir / "europe_pmc_search.json").read_text())
    if scenario == "empty":
        data = {"hitCount": 0, "resultList": {"result": []}}
    elif scenario == "long_text":
        data["resultList"]["result"][0]["title"] = "🩺" * 1300
    elif scenario in {"limit50", "limit51"}:
        amount = 50 if scenario == "limit50" else 51
        data = {"hitCount": amount, "resultList": {"result": [
            {"id": str(i + 1), "source": "SYNTHETIC", "title": "Registro sintético " + str(i + 1)}
            for i in range(amount)
        ]}}
    elif scenario == "unsafe_unicode":
        data["resultList"]["result"][0]["title"] = "Metadato\u202einseguro"
    else:
        data["resultList"]["result"][0]["title"] = 'Metadatos sintéticos — Niño, ação, 北京, 𝒜🩺, e\u0301 <img src="https://external.example/pixel" onerror="window.PAR02_XSS=1">'
        data["resultList"]["result"][1]["title"] = '<script>window.PAR02_XSS=2</script> Texto literal sintético'
    return json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")

class SyntheticProvider:
    def __init__(self, scenario, service, request_id, b1_dir, recorder, lab_helpers):
        self.scenario, self.service, self.request_id = scenario, service, request_id
        self.recorder, self.lab_helpers = recorder, lab_helpers
        self.stop = threading.Event()
        self.requests, self.sni = [], []
        self.connections = []
        self.threads = []
        self.temp = tempfile.TemporaryDirectory(prefix="par02_tls_")
        d = Path(self.temp.name)
        ca_key, ca = lab_helpers.make_ca("PAR02 synthetic temporary CA")
        leaf_key, leaf = lab_helpers.make_leaf(ca_key, ca, lab_helpers.HOSTS)
        self.ca_path = d / "ca.pem"
        self.ca_path.write_bytes(lab_helpers.pem_cert(ca))
        cert, key = d / "cert.pem", d / "key.pem"
        cert.write_bytes(lab_helpers.pem_cert(leaf))
        key.write_bytes(lab_helpers.pem_key(leaf_key))
        key.chmod(0o600)
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.context.load_cert_chain(cert, key)
        self.context.sni_callback = lambda sock, name, context: self.sni.append(name)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("127.0.0.1", 0))
        self.socket.listen(8)
        self.socket.settimeout(0.1)
        self.port = self.socket.getsockname()[1]
        self.body = payload(scenario, service, b1_dir / "frozen_r6/fixtures")
        self.thread = threading.Thread(target=self.accept_loop, name="par02-tls", daemon=True)
        self.thread.start()
    def accept_loop(self):
        while not self.stop.is_set():
            try:
                raw, peer = self.socket.accept()
            except OSError:
                continue
            t = threading.Thread(target=self.serve, args=(raw, peer), name="par02-tls-request", daemon=True)
            self.threads.append(t)
            t.start()
    def serve(self, raw, peer):
        try:
            raw.settimeout(4)
            with self.context.wrap_socket(raw, server_side=True) as stream:
                self.connections.append(stream)
                buf = b""
                while b"\r\n\r\n" not in buf and len(buf) <= 16384:
                    chunk = stream.recv(4096)
                    if not chunk:
                        return
                    buf += chunk
                line = buf.split(b"\r\n", 1)[0]
                # Request target is a fixed synthetic approved catalog value; retain hash only.
                entry = {
                    "event": "provider_tls_request",
                    "request_id": self.request_id,
                    "scenario": self.scenario,
                    "peer": list(peer),
                    "local": list(stream.getsockname()),
                    "tls_version": stream.version(),
                    "target_sha256": hashlib.sha256(line).hexdigest(),
                    "at_monotonic": time.monotonic(),
                }
                self.requests.append(entry)
                self.recorder.event(entry)
                index = len(self.requests)
                status, extra, body = "200 OK", [], self.body
                if self.scenario == "invalid_json":
                    body = b'{"broken":'
                elif self.scenario == "invalid_utf8":
                    body = b'{"bad":"\xff"}'
                elif self.scenario == "http_error":
                    status, body = "503 Service Unavailable", b"SYNTHETIC_NOT_ECHOED"
                elif self.scenario == "redirect":
                    status, extra, body = "302 Found", [("Location", "https://external.example/blocked")], b""
                elif self.scenario == "retry_429" and index == 1:
                    status, extra, body = "429 Too Many Requests", [("Retry-After", "0")], b""
                if self.scenario == "oversize":
                    stream.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2000001\r\nConnection: close\r\n\r\n")
                    return
                if self.scenario == "timeout":
                    stream.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{")
                    self.stop.wait(3)
                    return
                if self.scenario == "client_timeout" and self.stop.wait(2):
                    return
                headers = [("Content-Type", "application/json; charset=utf-8"),
                           ("Content-Length", str(len(body))), ("Connection", "close")] + extra
                head = "HTTP/1.1 " + status + "\r\n" + "".join(k + ": " + v + "\r\n" for k, v in headers) + "\r\n"
                stream.sendall(head.encode("ascii") + body)
        except (OSError, ssl.SSLError):
            pass
        finally:
            raw.close()
    def close(self):
        self.stop.set()
        self.socket.close()
        for stream in self.connections:
            try: stream.close()
            except OSError: pass
        self.thread.join(1)
        for thread in self.threads:
            thread.join(1)
        self.temp.cleanup()

class ObservedTransport:
    """Records actual stock B1 outcomes; never substitutes network responses."""
    def __init__(self, actual):
        self.actual = actual
        self.calls = []
    def __call__(self, *args):
        start = time.monotonic()
        try:
            result = self.actual(*args)
        except Exception as exc:
            self.calls.append({"outcome": "error", "code": getattr(exc, "code", "gateway_error"), "elapsed_seconds": time.monotonic()-start})
            raise
        self.calls.append({"outcome": "reply", "status": result.status, "body_bytes": len(result.body),
                           "body_sha256": hashlib.sha256(result.body).hexdigest(), "elapsed_seconds": time.monotonic()-start})
        return result
    def close(self):
        self.actual.close()

def execute(scenario, request_id):
    service = "nvd" if scenario == "combined_limits" else scenario if scenario in {"pubmed", "nvd"} else "europe_pmc"
    query = "vite" if service == "nvd" else "sepsis"
    provider = SyntheticProvider(scenario, service, request_id, B1_DIR, RECORDER, lab)
    total = 1.2 if scenario == "timeout" else 3.0
    native = HardenedHTTPSTransport(
        max_concurrency=2, max_call_seconds=3.0,
        _worker_script=str(HERE / "loopback_worker.py"),
        _worker_env={"G01T_PORT": str(provider.port), "G01T_CA": str(provider.ca_path),
                     "G01T_ADDR": "127.0.0.1", "PAR02_B1_DIR": str(B1_DIR),
                     "PAR02_NETWORK_LOG": str(RECORDER.directory / "worker_network.jsonl"),
                     "PAR02_REQUEST_ID": request_id},
    )
    transport = ObservedTransport(native)
    gateway = G01Gateway(total_budget_seconds=total, attempt_timeout_seconds=3.0,
                         retries=1 if scenario == "retry_429" else 0, transport=transport,
                         hmac_key=bytes(range(32)), cache_dir=None)
    start = time.monotonic()
    status, result, fault = 200, None, None
    try:
        result = gateway.search(service, query, limit=50 if scenario in {"limit50", "limit51", "combined_limits"} else 10).as_dict()
        if scenario == "invalid_normalized":
            result["service"] = "nvd"
            fault = "POST_NORMALIZATION_FAULT_INJECTION"
    except (APIGatewayError, OSError):
        codes = {x.get("code") for x in transport.calls}
        if "timeout" in codes or "budget_exhausted" in codes:
            code, status = "upstream_timeout", 504
        elif "response_too_large" in codes:
            code, status = "upstream_too_large", 502
        elif "redirect_blocked" in codes:
            code, status = "redirect_blocked", 502
        else:
            code, status = "upstream_error", 502
        result = error_body(code)
    finally:
        gateway.close()
        provider.close()
    encoded = json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    receipt = {
        "request_id": request_id, "scenario": scenario, "service": service, "scope": "synthetic_loopback_only",
        "clinical_status": "CLINICALLY_PENDING", "http_status": status,
        "duration_seconds": time.monotonic() - start, "total_budget_seconds": total,
        "provider_bind": ["127.0.0.1", provider.port], "provider_requests": len(provider.requests),
        "provider_sni": provider.sni, "tls_records": provider.requests, "transport_calls": transport.calls,
        "worker_stats": {k: getattr(native.stats, k) for k in ["spawned", "unreaped", "killed", "live", "peak_live"]},
        "json_sha256": hashlib.sha256(encoded).hexdigest(), "json_bytes": len(encoded),
        "post_normalization_fault": fault,
        "runtime": RUNTIME,
    }
    if status == 200:
        receipt["record_count"] = len(result["records"])
        receipt["raw_body_sha256"] = result["provenance"]["raw_body_sha256"]
        receipt["raw_hash_matches_transport"] = receipt["raw_body_sha256"] == transport.calls[-1]["body_sha256"]
    else:
        receipt["error_code"] = result["error"]["code"]
    return status, encoded, receipt

def error_body(code):
    return {"error": {"code": code, "message": ERRORS[code]}, "clinical_status": "CLINICALLY_PENDING"}

class Handler(DeadlineRequestHandler):
    server_version = "PAR02SyntheticLab"
    sys_version = ""
    protocol_version = "HTTP/1.1"
    def log_message(self, format, *args):
        # Do not echo arbitrary target/query or input into logs.
        return
    def send_json(self, status, encoded, request_id, *, head_only=False):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Par02-Request-Id", request_id)
        self.send_header("Connection", "close")
        self.end_headers()
        if head_only:
            return "headers_only"
        try:
            self.wfile.write(encoded)
            return "sent"
        except (BrokenPipeError, ConnectionResetError):
            return "client_disconnected"
    def send_error(self, code, message=None, explain=None):
        # The stdlib parser must not reflect an untrusted request line in HTML.
        self.close_connection = True
        if self.request_version == "HTTP/0.9":
            self.request_version = "HTTP/1.0"
        request_id = "par02-" + uuid.uuid4().hex
        encoded = json.dumps(error_body("invalid_request"), ensure_ascii=False).encode()
        self.send_json(code, encoded, request_id, head_only=self.command == "HEAD")
        RECORDER.receipt({"request_id": request_id, "scenario": None, "http_status": code,
                          "error_code": "invalid_request", "provider_requests": 0,
                          "request_rejected_before_transport": True})
    def error(self, code, status, request_id, *, pre_transport=True):
        body = json.dumps(error_body(code), ensure_ascii=False).encode()
        self.send_json(status, body, request_id)
        RECORDER.receipt({"request_id": request_id, "scenario": None, "http_status": status,
                          "error_code": code, "provider_requests": 0 if pre_transport else None,
                          "request_rejected_before_transport": True if pre_transport else None})
    def trusted_local_request(self):
        hosts = self.headers.get_all("Host", [])
        port = self.server.server_port
        if len(hosts) != 1 or hosts[0] not in {f"127.0.0.1:{port}", f"localhost:{port}"}:
            return False
        origins = self.headers.get_all("Origin", [])
        if len(origins) > 1 or (origins and origins[0] not in self.server.allowed_origins):
            return False
        sites = self.headers.get_all("Sec-Fetch-Site", [])
        if len(sites) > 1 or (sites and sites[0] not in {"same-origin", "same-site", "none"}):
            return False
        # A fixed same-origin application header rejects browser-simple requests.
        # It is a routing guard, not a credential or public authentication scheme.
        return self.headers.get_all("X-Emergency-T06-Lab", []) == ["synthetic-loopback"]
    def do_GET(self):
        request_id = "par02-" + uuid.uuid4().hex
        if not self.trusted_local_request():
            self.error("invalid_request", 403, request_id); return
        lengths = self.headers.get_all("Content-Length", [])
        if self.headers.get_all("Transfer-Encoding") or len(lengths) > 1 or (lengths and lengths != ["0"]):
            self.error("invalid_request", 400, request_id); return
        if len(self.path) > 1024:
            self.error("request_too_large", 414, request_id); return
        route = urlsplit(self.path)
        if route.scheme or route.netloc or route.fragment:
            self.error("invalid_request", 400, request_id); return
        if route.path == "/api/lab-status" and not route.query:
            data = json.dumps(RECORDER.status(), ensure_ascii=False).encode()
            self.send_json(200, data, request_id); return
        if route.path != "/api/search":
            self.error("not_found", 404, request_id); return
        try:
            params = parse_qs(route.query, strict_parsing=True, keep_blank_values=True, max_num_fields=2)
        except ValueError:
            self.error("invalid_request", 400, request_id); return
        if set(params) != {"scenario"} or len(params["scenario"]) != 1 or params["scenario"][0] not in SCENARIOS:
            self.error("invalid_request", 400, request_id); return
        scenario = params["scenario"][0]
        try:
            status, body, receipt = execute(scenario, request_id)
        except Exception:
            RECORDER.event({"event": "internal_harness_error", "request_id": request_id,
                            "traceback": traceback.format_exc()})
            self.error("internal_error", 500, request_id, pre_transport=False); return
        receipt["delivery"] = self.send_json(status, body, request_id)
        RECORDER.receipt(receipt)
    def do_POST(self):
        self.error("method_not_allowed", 405, "par02-" + uuid.uuid4().hex)
    do_PUT = do_POST
    do_DELETE = do_POST
    do_PATCH = do_POST

def main():
    global B1_DIR, RECORDER, RUNTIME, lab, G01Gateway, HardenedHTTPSTransport, APIGatewayError
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--ui-port", type=int, default=5173)
    parser.add_argument("--b1-dir", type=Path, default=DEFAULT_B1)
    parser.add_argument("--evidence-dir", type=Path, default=HERE.parents[1] / "evidence/backend/live")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("The recovered B1 process containment requires the verified Linux runtime.")
    if not 1 <= args.ui_port <= 65535:
        parser.error("--ui-port must be in [1, 65535]")
    B1_DIR = args.b1_dir.resolve()
    sys.addaudithook(audit_loopback)
    sys.path[:0] = [str(B1_DIR / "frozen_r6"), str(B1_DIR), str(B1_DIR / "tests")]
    import lab
    from emergency_apis.clients import APIGatewayError
    from g01_https_transport import G01Gateway, HardenedHTTPSTransport
    RECORDER = Recorder(args.evidence_dir.resolve())
    RUNTIME = {
        "python": sys.version.split()[0], "python_executable": sys.executable,
        "openssl": ssl.OPENSSL_VERSION,
        "h11": importlib.metadata.version("h11"),
        "cryptography": importlib.metadata.version("cryptography"),
        "declared_lock": {"h11": "0.16.0", "cryptography": "50.0.1"},
        "author_python": "3.13.18",
        "python_matches_author": sys.version.split()[0] == "3.13.18",
        "pin_equivalence": (importlib.metadata.version("h11") == "0.16.0"
                            and importlib.metadata.version("cryptography") == "50.0.1"),
    }
    write_json(args.evidence_dir / "runtime.json", RUNTIME)
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    server = BoundedHTTPServer(("127.0.0.1", args.port), Handler, request_timeout=5.0, max_workers=4)
    server.allowed_origins = {f"http://{host}:{port}" for host in ("127.0.0.1", "localhost")
                              for port in (args.ui_port, server.server_port)}
    print(json.dumps({"ready": True, "bind": list(server.server_address), "runtime": RUNTIME}), flush=True)
    def stop(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        write_json(args.evidence_dir / "final_status.json", RECORDER.status())

if __name__ == "__main__":
    main()
