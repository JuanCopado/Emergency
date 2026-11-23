"""Technical probe of a stimulus FILE for the Layer 7 harness · LABORATORY ONLY.

Reads the file's bytes to obtain the objective container descriptor the contract allows (signature kind and whether the container parses).
It never inspects pixels for clinical or visual meaning, EXIF, the file name's meaning or DICOM absence; the declared MIME type and
extension are taken from the file suffix as the browser would declare them.
"""
import io
import wave
from pathlib import Path

SUFFIX_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".pdf": "application/pdf",
               ".wav": "audio/wav", ".dcm": "application/dicom", ".txt": "text/plain"}


def signature_kind(data):
    if data[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:5] == b"%PDF-":
        return "pdf"
    if data[128:132] == b"DICM":
        return "dicom"
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "audio"
    if not data:
        return "unknown"
    try:
        data.decode("utf-8")
        return "text" if b"\x00" not in data else "binary"
    except UnicodeDecodeError:
        return "binary"


def container_parses(data, kind):
    """True when the container is structurally readable. Truncated images and empty files fail; nothing else is judged."""
    if not data:
        return False
    try:
        if kind in ("jpeg", "png", "webp"):
            from PIL import Image
            img = Image.open(io.BytesIO(data))
            img.load()                        # full decode: a truncated JPEG raises here
            return True
        if kind == "pdf":
            return b"%%EOF" in data[-1024:] and b"startxref" in data
        if kind == "audio":
            with wave.open(io.BytesIO(data)) as w:
                w.getnframes()
            return True
        return True
    except Exception:
        return False


def describe(path, flow, declared_kind):
    """Descriptor accepted by layer7_simulator.validate_descriptor. `declared_kind` None means no modality was selected."""
    path = Path(path)
    data = path.read_bytes()
    kind = signature_kind(data)
    suffix = path.suffix.lower()
    return {"flow": flow, "modality_declared": declared_kind is not None, "declared_kind": declared_kind, "signature_kind": kind,
            "container_parse_ok": container_parses(data, kind), "declared_mime_type": SUFFIX_MIME.get(suffix), "declared_extension": suffix or None}
