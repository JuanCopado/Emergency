"""Controlled localhost lab. NO public network. Hostnames are mapped to 127.0.0.1 by the TEST worker only."""
import datetime, os, re, shutil, socket, ssl, struct, tempfile, threading, time
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

HOSTS = ["eutils.ncbi.nlm.nih.gov", "www.ebi.ac.uk", "services.nvd.nist.gov"]
HERE = Path(__file__).resolve().parent
LAB_WORKER = str(HERE / "lab_worker.py")
OK_BODY = b'{"resultsPerPage":0,"totalResults":0,"vulnerabilities":[]}'
PUBMED_BODY = b'{"esearchresult":{"count":"1","idlist":["1234567"]}}'


def _name(cn): return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def make_ca(cn):
    key = ec.generate_private_key(ec.SECP256R1())
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(_name(cn)).issuer_name(_name(cn)).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .add_extension(x509.KeyUsage(True, False, False, False, False, True, True, False, False), critical=True)
            .sign(key, hashes.SHA256()))
    return key, cert


def make_leaf(ca_key, ca_cert, hosts):
    key = ec.generate_private_key(ec.SECP256R1())
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(_name(hosts[0])).issuer_name(ca_cert.subject).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=5))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(h) for h in hosts]), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_cert.public_key()), critical=False)
            .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .sign(ca_key, hashes.SHA256()))
    return key, cert


def pem_cert(c): return c.public_bytes(serialization.Encoding.PEM)
def pem_key(k): return k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())


class Lab:
    """Servers: tls (behaviour per request), hold (TCP accept, never speaks), backlog (accept queue saturated),
    badca (valid chain but untrusted CA), badhost (trusted CA, wrong SAN)."""
    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="g01lab_"))
        self.ca_key, self.ca = make_ca("g01-lab-ca")
        (self.dir / "ca.pem").write_bytes(pem_cert(self.ca))
        self.mode = "ok"
        self.requests = []          # (mode, monotonic)
        self.sni = []
        self.servers, self.threads, self.stop = [], [], threading.Event()
        self.held, self.fillers = [], []
        self.tls_port = self._tls_server(HOSTS, trusted=True)
        self.badhost_port = self._tls_server(["other.example"], trusted=True)
        self.badca_port = self._tls_server(HOSTS, trusted=False)
        self.hold_port = self._raw_server(accept=True)
        self.backlog_port = self._raw_server(accept=False)

    # --- servers ---
    def _listen(self, backlog):
        s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0)); s.listen(backlog); self.servers.append(s); return s

    def _spawn(self, fn, *a):
        t = threading.Thread(target=fn, args=a, daemon=True, name='lab-srv'); t.start(); self.threads.append(t)

    def _raw_server(self, accept):
        s = self._listen(128 if accept else 0)
        if accept:
            def loop():
                s.settimeout(0.2)
                while not self.stop.is_set():
                    try: c, _ = s.accept(); self.held.append(c)
                    except OSError: pass
            self._spawn(loop)
        else:
            # fill the accept queue so further SYNs are dropped (connect() hangs)
            for _ in range(8):
                c = socket.socket(); c.setblocking(False)
                try: c.connect(("127.0.0.1", s.getsockname()[1]))
                except (BlockingIOError, OSError): pass
                self.fillers.append(c)
        return s.getsockname()[1]

    def _tls_server(self, hosts, trusted):
        if trusted: ck, cc = self.ca_key, self.ca
        else: ck, cc = make_ca("untrusted-ca")
        lk, lc = make_leaf(ck, cc, hosts)
        cf, kf = self.dir / f"c{len(self.servers)}.pem", self.dir / f"k{len(self.servers)}.pem"
        cf.write_bytes(pem_cert(lc)); kf.write_bytes(pem_key(lk))
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(cf, kf)
        ctx.sni_callback = lambda sock, name, c: self.sni.append(name)
        s = self._listen(64)
        def loop():
            s.settimeout(0.2)
            while not self.stop.is_set():
                try: c, _ = s.accept()
                except OSError: continue
                self._spawn(self._serve, c, ctx)
        self._spawn(loop)
        return s.getsockname()[1]

    def _serve(self, raw, ctx):
        c = None
        try:
            raw.settimeout(5)
            c = ctx.wrap_socket(raw, server_side=True)
            buf = b""
            while b"\r\n\r\n" not in buf and len(buf) < 16384:
                d = c.recv(4096)
                if not d: return
                buf += d
            line = buf.split(b"\r\n", 1)[0].decode("latin-1")
            mode = self.mode
            import re as _re
            m = _re.search(r"[?&]b=([a-z0-9_]+)", line)
            if m:
                mode = m.group(1)
            else:
                # Special sentinel in values of allowed query parameters; never a new param.
                m = _re.search(r"G01LAB_([a-z0-9_]+)", line)
                if m:
                    mode = m.group(1)
            self.requests.append((mode, time.monotonic()))
            self._respond(c, mode)
        except (OSError, ssl.SSLError):
            pass
        finally:
            try:
                if c is not None:
                    c.close()
            except OSError:
                pass
            try: raw.close()
            except OSError: pass

    def _respond(self, c, mode):
        def hdr(status, extra, body=None, cl=True):
            h = f"HTTP/1.1 {status}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in extra) + (
                f"Content-Length: {len(body)}\r\n" if (cl and body is not None) else "") + "Connection: close\r\n\r\n"
            return h.encode() + (body or b"")
        send = c.sendall
        if mode == "ok": send(hdr("200 OK", [("Content-Type", "application/json")], OK_BODY))
        elif mode == "ok_pubmed": send(hdr("200 OK", [], PUBMED_BODY))
        elif mode == "ok_chunked":
            send(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n"
                 + hex(len(OK_BODY))[2:].encode() + b"\r\n" + OK_BODY + b"\r\n0\r\n\r\n")
        elif mode in ("r302", "r307", "r308"):
            send(hdr({"r302": "302 Found", "r307": "307 Temporary Redirect", "r308": "308 Permanent Redirect"}[mode],
                     [("Location", "http://169.254.169.254/latest/")], b""))
        elif mode == "r429": send(hdr("429 Too Many Requests", [("Retry-After", "2")], b""))
        elif mode == "r429_once":
            if sum(1 for m, _ in self.requests if m == "r429_once") == 1:
                send(hdr("429 Too Many Requests", [("Retry-After", "1")], b""))
            else: send(hdr("200 OK", [], PUBMED_BODY))
        elif mode == "r503": send(hdr("503 Service Unavailable", [], b"nope"))
        elif mode == "truncated": send(f"HTTP/1.1 200 OK\r\nContent-Length: 1000\r\nConnection: close\r\n\r\n".encode() + b"x" * 100)
        elif mode == "big": send(f"HTTP/1.1 200 OK\r\nContent-Length: 3000000\r\nConnection: close\r\n\r\n".encode())
        elif mode == "big_chunked":
            send(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n")
            chunk = b"x" * 65536
            for _ in range(48):
                send(hex(len(chunk))[2:].encode() + b"\r\n" + chunk + b"\r\n")
            send(b"0\r\n\r\n")
        elif mode == "exact_cap": send(hdr("200 OK", [], b"{" + b" " * 1_999_998 + b"}"))
        elif mode == "over_cap": send(hdr("200 OK", [], b"{" + b" " * 1_999_999 + b"}"))
        elif mode == "gzip": send(hdr("200 OK", [("Content-Encoding", "gzip")], b"\x1f\x8b"))
        elif mode == "both": send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nTransfer-Encoding: chunked\r\nConnection: close\r\n\r\n2\r\n{}\r\n0\r\n\r\n")
        elif mode == "dupcl": send(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Length: 3\r\nConnection: close\r\n\r\n{}")
        elif mode == "noframe": send(b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n" + OK_BODY)
        elif mode == "manyhdr": send(hdr("200 OK", [(f"X-H{i}", "v") for i in range(100)], OK_BODY))
        elif mode == "bighdr": send(hdr("200 OK", [("X-Big", "a" * 20000)], OK_BODY))
        elif mode == "ctrlhdr": send(b"HTTP/1.1 200 OK\r\nX-A: a\x01b\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}")
        elif mode == "slow_headers":
            for ch in b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{}":
                send(bytes([ch])); self.stop.wait(0.2)
        elif mode == "slow_body":
            send(b"HTTP/1.1 200 OK\r\nContent-Length: 1000\r\nConnection: close\r\n\r\n")
            for _ in range(1000):
                if self.stop.is_set(): break
                send(b" "); self.stop.wait(0.2)
        elif mode == "last_byte":
            send(b"HTTP/1.1 200 OK\r\nContent-Length: 100\r\nConnection: close\r\n\r\n" + b" " * 99)
            if not self.stop.wait(4): send(b" ")
        elif mode == "stall_after_request": self.stop.wait(30)
        else: send(hdr("500 Internal Server Error", [], b""))

    def close(self):
        self.stop.set()
        for s in self.servers + self.held + self.fillers:
            try: s.close()
            except OSError: pass
        join_deadline = time.monotonic() + 2.0
        for t in self.threads:
            if t.is_alive() and t is not threading.current_thread():
                t.join(timeout=max(0.0, join_deadline - time.monotonic()))
        shutil.rmtree(self.dir, ignore_errors=True)
