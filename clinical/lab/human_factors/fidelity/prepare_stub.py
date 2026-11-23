"""Answers one /api/clinical-note/upload/prepare request with the REAL server dispatch (no provider, no network, no persistence).

Reads {"path":..., "payload":...} from stdin; prints {"status": int, "body": {...}}. Laboratory fidelity tool only.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import clinical_note_api as api  # noqa: E402

request = json.load(sys.stdin)
try:
    status, body = api.dispatch(request["path"], request["payload"])
except api.image_upload_guard.MediaRejected:       # same public mapping as the HTTP handler
    status, body = 422, {"error": "invalid or unsupported clinical image or filename"}
except ValueError:
    status, body = 422, {"error": "invalid clinical request"}
print(json.dumps({"status": int(status), "body": body}))
