"""TEST-ONLY worker profile: same _worker.py code path, but hostnames resolve to 127.0.0.1:PORT and the
lab CA is trusted. Certificate verification and hostname checking remain ENABLED (CERT_REQUIRED)."""
import importlib.util, os, socket, ssl, sys, time
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "g01_https_transport" / "_worker.py"
spec = importlib.util.spec_from_file_location("g01_worker_under_test", p)
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
port = int(os.environ["G01T_PORT"])
delay = float(os.environ.get("G01T_DNS_DELAY", "0"))
ctx = ssl.create_default_context(cafile=os.environ["G01T_CA"])
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
def resolver(host, prt):
    if delay: time.sleep(delay)          # SIMULATED stalled resolver (blocking call inside the worker)
    return [(socket.AF_INET, os.environ.get("G01T_ADDR", "127.0.0.1"))]
if os.environ.get("G01T_NO_COOP") == "1":
    # TEST ONLY: disable the worker's cooperative deadline so ONLY the parent's SIGKILL can stop it.
    _orig = w.fetch
    w.fetch = lambda spec, **kw: _orig({**spec, "remaining": 1000.0}, **kw)
w.main(resolver=resolver, ssl_context=ctx, port=port, require_global_ip=os.environ.get("G01T_GLOBAL") == "1")
