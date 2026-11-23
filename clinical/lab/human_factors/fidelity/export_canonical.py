"""stdin JSON {log, context} -> stdout JSON {status, record | reason}. Lab runner helper: converts the events the PR95 lab entry really emitted
into a canonical-r27-v1.1 record. LABORATORY ONLY; no network; nothing is guessed (HARD FAIL is reported as NOT_EXPORTED with its reason)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canonical_r27_v1 as canonical  # noqa: E402

request = json.load(sys.stdin)
try:
    record = canonical.from_lab_ui_log(request["log"], request["context"])
    print(json.dumps({"status": "EXPORTED", "record_valid": True, "record": record}))
except canonical.CanonicalViolation as error:
    print(json.dumps({"status": "NOT_EXPORTED", "reason": str(error)}))
