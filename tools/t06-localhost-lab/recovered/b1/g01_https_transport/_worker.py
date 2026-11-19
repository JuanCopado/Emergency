"""G-01 worker: one HTTPS GET per process. Killed by the parent at the absolute deadline.

Runs as `python -I _worker.py`; reads a JSON spec on stdin, writes ONE frame on stdout:
  {"ok":true,"status":200,"headers":{...},"body_len":N}\n<body bytes>   or   {"ok":false,"code":"..."}\n
stderr is discarded by the parent. Nothing here ever prints URLs, queries, headers or bodies
except the validated response in the success frame. The parent re-validates every field.
Transport stack: stdlib socket + ssl (OpenSSL) + h11 (sans-IO HTTP/1.1, MIT).
"""
import importlib.util
import ipaddress
import json
import os
import socket
import ssl
import sys
import time
from pathlib import Path

try:  # avoid core dumps / fd + address-space blow-ups inside the sandboxed child
    import resource
except ImportError:  # pragma: no cover (non-POSIX)
    resource = None

_spec = importlib.util.spec_from_file_location("_g01_policy", Path(__file__).with_name("_policy.py"))
_policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_policy)
import h11  # noqa: E402


class W(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _now():
    return time.clock_gettime(time.CLOCK_BOOTTIME) if hasattr(time, "CLOCK_BOOTTIME") else time.monotonic()


def production_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()           # CERT_REQUIRED + check_hostname + system trust
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_alpn_protocols(["http/1.1"])
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
    return ctx


def production_resolver(host, port):
    return [(ai[0], ai[4][0]) for ai in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            if ai[0] in (socket.AF_INET, socket.AF_INET6)]


def _is_public(addr: str) -> bool:
    ip = ipaddress.ip_address(addr.split("%", 1)[0])
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


def fetch(spec, *, resolver, ssl_context, port, require_global_ip):
    if not (ssl_context.verify_mode == ssl.CERT_REQUIRED and ssl_context.check_hostname):
        raise W("tls_error")  # fail closed: never run with verification disabled
    host, target, hdrs = _policy.parse_request("https://" + spec["host"] + spec["target"], spec["headers"])
    t_end = _now() + float(spec["remaining"])

    def left():
        r = t_end - _now()
        if r <= 0:
            raise W("timeout")
        return r

    # ---- DNS ----
    try:
        found = resolver(host, port)
    except (socket.gaierror, UnicodeError):
        raise W("dns_failure") from None
    seen, addrs = set(), []
    for fam, a in found:
        if a not in seen:
            seen.add(a)
            addrs.append((fam, a))
    if not addrs:
        raise W("dns_failure")
    if require_global_ip:
        addrs = [(f, a) for f, a in addrs if _is_public(a)]
        if not addrs:
            raise W("dns_non_global")
    addrs = addrs[:4]
    left()
    # ---- TCP ----
    sock = None
    for i, (fam, a) in enumerate(addrs):
        s = socket.socket(fam, socket.SOCK_STREAM)
        try:
            s.settimeout(max(0.05, left() / (len(addrs) - i)))
            s.connect((a, port))
            sock = s
            break
        except (OSError, TimeoutError):
            s.close()
    if sock is None:
        left()
        raise W("connect_failed")
    try:
        # ---- TLS (SNI = host, cert + hostname verified by ssl module) ----
        tls = ssl_context.wrap_socket(sock, server_hostname=host, do_handshake_on_connect=False)
        sock = tls
        try:
            tls.settimeout(left())
            tls.do_handshake()
        except ssl.SSLCertVerificationError:
            raise W("tls_verify_failed") from None
        except (TimeoutError, socket.timeout):
            raise W("timeout") from None
        except ssl.SSLError:
            raise W("tls_error") from None
        except OSError:
            raise W("connection_reset") from None
        # ---- HTTP/1.1 via h11 ----
        conn = h11.Connection(h11.CLIENT, max_incomplete_event_size=_policy.MAX_HEADER_BYTES)
        req_headers = [("Host", host), ("User-Agent", hdrs.get("user-agent", "g01")),
                       ("Accept", hdrs.get("accept", "application/json")),
                       ("Accept-Encoding", "identity"), ("Connection", "close")]
        data = conn.send(h11.Request(method="GET", target=target, headers=req_headers))
        data += conn.send(h11.EndOfMessage())
        tls.settimeout(left())
        tls.sendall(data)
        status = None
        out_headers = {}
        body = bytearray()
        read_body = False
        got_eof = False
        while True:
            try:
                ev = conn.next_event()
            except h11.RemoteProtocolError:
                raise W("truncated_body" if (status is not None and got_eof) else "protocol_error") from None
            if ev is h11.NEED_DATA:
                tls.settimeout(left())
                try:
                    chunk = tls.recv(65536)
                except (TimeoutError, socket.timeout):
                    raise W("timeout") from None
                except ssl.SSLError:
                    raise W("tls_error") from None
                except OSError:
                    raise W("connection_reset") from None
                got_eof = not chunk
                try:
                    conn.receive_data(chunk)
                except h11.RemoteProtocolError:
                    raise W("protocol_error") from None
                if not chunk and status is not None:
                    pass  # EOF handled by next_event(): mid-body EOF -> RemoteProtocolError -> truncated
                continue
            if isinstance(ev, h11.InformationalResponse):
                raise W("informational_response")
            if isinstance(ev, h11.Response):
                status = ev.status_code
                items = [(k.decode("ascii"), v.decode("ascii")) for k, v in ev.headers.raw_items()] \
                    if all(k.isascii() and v.isascii() for k, v in ev.headers.raw_items()) else None
                if items is None:
                    raise W("protocol_error")
                if len(items) > _policy.MAX_HEADER_COUNT or sum(len(k) + len(v) for k, v in items) > _policy.MAX_HEADER_BYTES:
                    raise W("headers_too_large")
                for k, v in items:
                    if not _policy.HEADER_NAME_RE.fullmatch(k) or not _policy.HEADER_VALUE_RE.fullmatch(v):
                        raise W("protocol_error")
                    lk = k.lower()
                    if lk in out_headers:
                        if lk in _policy.SENSITIVE_SINGLETONS:
                            raise W("ambiguous_framing")
                        out_headers[lk] += ", " + v
                    else:
                        out_headers[lk] = v
                if 300 <= status < 400:
                    raise W("redirect_blocked")
                if not 200 <= status <= 599:
                    raise W("protocol_error")
                ce = out_headers.get("content-encoding", "identity").strip().lower()
                if ce not in ("", "identity"):
                    raise W("content_encoding_unsupported")
                te = out_headers.get("transfer-encoding")
                cl = out_headers.get("content-length")
                if te is not None and cl is not None:
                    raise W("ambiguous_framing")
                if te is not None and te.strip().lower() != "chunked":
                    raise W("ambiguous_framing")
                if status == 200:
                    if te is None and cl is None:
                        raise W("ambiguous_framing")      # close-delimited body = truncation-indistinguishable
                    if cl is not None:
                        if not cl.isascii() or not cl.isdigit() or len(cl) > 9:
                            raise W("ambiguous_framing")
                        if int(cl) > _policy.MAX_BODY_BYTES:
                            raise W("response_too_large")
                    read_body = True
                else:
                    break  # error bodies are discarded (R6 never uses them); headers suffice
                continue
            if isinstance(ev, h11.Data):
                body += ev.data
                if len(body) > _policy.MAX_BODY_BYTES:
                    raise W("response_too_large")
                continue
            if isinstance(ev, h11.EndOfMessage):
                break
            if isinstance(ev, h11.ConnectionClosed):
                raise W("truncated_body")
        if status is None or (status == 200 and not read_body):
            raise W("protocol_error")
        return status, out_headers, bytes(body)
    finally:
        try:
            sock.close()
        except OSError:
            pass


def main(*, resolver=production_resolver, ssl_context=None, port=443, require_global_ip=True):
    out = sys.stdout.buffer
    try:
        if resource is not None:
            for lim, val in ((resource.RLIMIT_CORE, 0), (resource.RLIMIT_NOFILE, 64),
                             (resource.RLIMIT_AS, 1 << 30), (resource.RLIMIT_NPROC, 1)):
                try:
                    resource.setrlimit(lim, (val, val))
                except (ValueError, OSError):
                    pass
        spec = json.loads(sys.stdin.buffer.read(8192).decode("ascii"))
        status, headers, body = fetch(spec, resolver=resolver, ssl_context=ssl_context or production_context(),
                                      port=port, require_global_ip=require_global_ip)
        head = json.dumps({"ok": True, "status": status, "headers": headers, "body_len": len(body)}).encode("ascii")
        out.write(head + b"\n" + body)
    except W as e:
        out.write(json.dumps({"ok": False, "code": e.code}).encode("ascii") + b"\n")
    except BaseException:
        out.write(b'{"ok":false,"code":"worker_failed"}\n')
    out.flush()


if __name__ == "__main__":
    main()
