"""Read-only preflight for a locally delivered stimulus batch."""
import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

from human_factors.image_structure import VALIDATORS

BANK = Path(__file__).resolve().parent / "bank"
KINDS = {"synthetic", "phantom", "authorized_clinical"}
ROLES = {"original", "derivative", "target", "distractor"}
MAX_ASSET_BYTES = 64 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000
IMAGE_SUFFIXES = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
REQUIRED_TEXT = ("source", "license", "permission_ref", "privacy_ref", "transformation")


def check_image(sid, data, suffix, required_format):
    expected_format = IMAGE_SUFFIXES.get(suffix)
    if not expected_format:
        raise ValueError(f"{sid}: unsupported image extension")
    if not 0 < len(data) <= MAX_ASSET_BYTES:
        raise ValueError(f"{sid}: image size is outside intake limits")
    try:
        VALIDATORS[expected_format](data)
    except ValueError as error:
        raise ValueError(f"{sid}: unreadable image container") from error
    try:
        with Image.open(io.BytesIO(data), formats=[expected_format]) as image:
            if required_format and image.format.lower() != required_format:
                raise ValueError(f"{sid}: image format does not match the stimulus specification")
            if image.width * image.height > MAX_IMAGE_PIXELS or getattr(image, "n_frames", 1) != 1:
                raise ValueError(f"{sid}: expected a bounded still image")
            image.load()
    except (OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise ValueError(f"{sid}: unreadable image container") from error


def check_receipt(receipt, root, manifest):
    pending = {row["stimulus_id"]: row["container_spec"] for row in manifest["stimuli"] if row["file"] is None}
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
        expected_size = asset["bytes"]
        if type(expected_size) is not int or not 0 < expected_size <= MAX_ASSET_BYTES:
            raise ValueError(f"{sid}: receipt size is outside intake limits")
        with path.open("rb") as stream:
            data = stream.read(expected_size + 1)
        size = len(data)
        measured = hashlib.sha256(data).hexdigest()
        if size != expected_size or asset["sha256"] != measured:
            raise ValueError(f"{sid}: physical bytes do not match receipt")
        check_image(sid, data, path.suffix.lower(), None if role == "original" else pending[sid])
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
