"""Start only the synthetic T06 loopback adapter with the original B1 pins."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--ui-port", type=int, default=5173)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("This integrated B1 laboratory is verified on Linux; use its Linux runtime.")
    if not 1 <= args.port <= 65535 or not 1 <= args.ui_port <= 65535:
        parser.error("Both ports must be in [1, 65535].")
    # Keep the venv symlink path: resolving it would silently select the base interpreter.
    interpreter = args.python.expanduser().absolute()
    if not interpreter.is_file() or not os.access(interpreter, os.X_OK):
        parser.error("--python must point to the existing isolated T06 interpreter.")
    check = subprocess.run([
        str(interpreter), "-I", "-c",
        "import json,sys,platform,importlib.metadata as m;"
        "print(json.dumps({'python':platform.python_version(),'version':list(sys.version_info[:2]),"
        "'h11':m.version('h11'),'cryptography':m.version('cryptography')}))",
    ], capture_output=True, text=True, check=False)
    if check.returncode:
        parser.error("Missing T06 dependencies. Prepare a separate venv from recovered/b1/requirements.lock and pass --python.")
    versions = json.loads(check.stdout)
    if versions["version"] < [3, 12] or versions["h11"] != "0.16.0" or versions["cryptography"] != "50.0.1":
        parser.error("T06 requires Python >=3.12, h11==0.16.0 and cryptography==50.0.1; observed " + json.dumps(versions))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence = (args.evidence_dir or here / "evidence" / (stamp + "-" + uuid.uuid4().hex[:8])).resolve()
    command = [str(interpreter), "-B", str(here / "lab/backend/server.py"),
               "--port", str(args.port), "--ui-port", str(args.ui_port), "--evidence-dir", str(evidence)]
    print("T06 synthetic loopback laboratory: 127.0.0.1:" + str(args.port), flush=True)
    # Replace this launcher so the caller can stop the owned backend process directly.
    os.execv(str(interpreter), command)


if __name__ == "__main__":
    main()
