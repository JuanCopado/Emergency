"""Read-only preflight for a locally delivered stimulus batch."""
import argparse
import hashlib
import json
from pathlib import Path

BANK = Path(__file__).resolve().parent / "bank"
KINDS = {"synthetic", "phantom", "authorized_clinical"}
ROLES = {"original", "derivative", "target", "distractor"}
REQUIRED_TEXT = ("source", "license", "permission_ref", "privacy_ref", "transformation")


def check_receipt(receipt, root, manifest):
    pending = {row["stimulus_id"] for row in manifest["stimuli"] if row["file"] is None}
    assets = receipt["assets"]
    if not isinstance(assets, list) or not assets:
        raise ValueError("receipt must list at least one physical asset")
    root = root.resolve()
    reported = []
    seen = set()
    for asset in assets:
        sid, role = asset["stimulus_id"], asset["role"]
        if sid not in pending or role not in ROLES or asset["kind"] not in KINDS:
            raise ValueError("asset must name a pending stimulus and a supported role and kind")
        if any(not isinstance(asset.get(key), str) or not asset[key].strip() for key in REQUIRED_TEXT):
            raise ValueError(f"{sid}: provenance, license, permission, privacy and transformation are required")
        relative = Path(asset["file"])
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"{sid}: physical asset missing or outside delivery folder")
        identity = (sid, role, path)
        if identity in seen:
            raise ValueError(f"{sid}: duplicate receipt entry")
        seen.add(identity)
        expected = asset["sha256"]
        with path.open("rb") as stream:
            measured = hashlib.file_digest(stream, "sha256").hexdigest()
        size = path.stat().st_size
        if not size or type(asset["bytes"]) is not int or size != asset["bytes"] or expected != measured:
            raise ValueError(f"{sid}: physical bytes do not match receipt")
        reported.append({"stimulus_id": sid, "role": role, "bytes": size, "sha256": measured})
    return {"status": "BYTES_VERIFIED_REVIEW_PENDING", "assets": reported}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        manifest = json.loads((BANK / "stimuli_manifest.json").read_text(encoding="utf-8"))
        result = check_receipt(receipt, args.receipt.parent, manifest)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
