"""Test-only wrapper around the unmodified B1 test worker. No public DNS."""
import ipaddress
import json
import os
from pathlib import Path
import runpy
import sys
sys.dont_write_bytecode = True

def audit_loopback(event, args):
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "socket.gethostbyaddr"}:
        with open(os.environ["PAR02_NETWORK_LOG"], "a") as stream:
            stream.write(json.dumps({"event": event, "pid": os.getpid(),
                "request_id": os.environ["PAR02_REQUEST_ID"],
                "address": args[1] if event in {"socket.connect", "socket.bind"} else args[0]}) + "\n")
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

sys.addaudithook(audit_loopback)
assert os.environ.get("G01T_ADDR") == "127.0.0.1"
b1 = Path(os.environ["PAR02_B1_DIR"]).resolve()
runpy.run_path(str(b1 / "tests" / "lab_worker.py"), run_name="__main__")
