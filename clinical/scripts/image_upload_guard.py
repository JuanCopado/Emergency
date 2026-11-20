#!/usr/bin/env python3
"""Stdlib-only structural guard for clinical image uploads (M10 audit, 2026-11-20).

Scope: technical integrity and privacy of the bytes only. It does NOT assess clinical
content, diagnostic quality or lesion findings. Findings are heuristics with the
ceilings documented per function.

Public API
  inspect_media(raw, filename, mime_type) -> dict   (raises MediaRejected if invalid)
  strip_metadata(raw, fmt)                -> bytes | None  (None = format unsupported)
"""
import struct
import zlib

MAX_PIXELS = 100_000_000          # decompression-bomb ceiling (technical, not clinical)
MIN_SHORT_SIDE_UNSUITABLE = 64    # below this no visual finding can be carried
MIN_SHORT_SIDE_LIMITED = 224      # below this: flagged as limited resolution (technical floor)
MAX_DECODE_BYTES = 50_000_000

PNG_SIG = b"\x89PNG\r\n\x1a\n"
PNG_META_CHUNKS = {b"eXIf", b"tEXt", b"zTXt", b"iTXt", b"tIME"}
EXT_FAMILY = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp",
              ".dcm": "dicom", ".pdf": "pdf"}
MIME_FAMILY = {"image/png": "png", "image/jpeg": "jpeg", "image/jpg": "jpeg",
               "image/webp": "webp", "application/dicom": "dicom",
               "application/pdf": "pdf"}
CANON_MIME = {"png": "image/png", "jpeg": "image/jpeg", "webp": "image/webp",
              "dicom": "application/dicom", "pdf": "application/pdf"}
IMAGE_FORMATS = {"png", "jpeg", "webp"}


class MediaRejected(ValueError):
    def __init__(self, code):
        super().__init__(f"invalid image upload: {code}")
        self.code = code


def sniff(raw):
    if raw.startswith(PNG_SIG):
        return "png"
    if raw.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "webp"
    if raw[128:132] == b"DICM":
        return "dicom"
    if raw.startswith(b"%PDF-"):
        return "pdf"
    return None


def _declared_family(filename, mime_type):
    name = str(filename or "").lower()
    ext = name[name.rfind("."):] if "." in name else ""
    mime = str(mime_type or "").split(";", 1)[0].strip().lower()
    return EXT_FAMILY.get(ext), MIME_FAMILY.get(mime), mime


# ---------------------------------------------------------------- PNG
def _parse_png(raw):
    meta = {"text_chunks": False, "exif": False, "trailing_data": False}
    pos, idat, ihdr, seen_end = 8, [], None, False
    while pos < len(raw):
        if pos + 12 > len(raw):
            raise MediaRejected("truncated")
        length = struct.unpack(">I", raw[pos:pos + 4])[0]
        ctype = raw[pos + 4:pos + 8]
        end = pos + 8 + length
        if end + 4 > len(raw):
            raise MediaRejected("truncated")
        body = raw[pos + 8:end]
        if zlib.crc32(ctype + body) & 0xFFFFFFFF != struct.unpack(">I", raw[end:end + 4])[0]:
            raise MediaRejected("crc_mismatch")
        if pos == 8 and (ctype != b"IHDR" or length != 13):
            raise MediaRejected("bad_header")
        if ctype == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif ctype == b"IDAT":
            idat.append(body)
        elif ctype == b"eXIf":
            meta["exif"] = True
        elif ctype in PNG_META_CHUNKS:
            meta["text_chunks"] = True
        pos = end + 4
        if ctype == b"IEND":
            seen_end = True
            break
    if not seen_end or ihdr is None or not idat:
        raise MediaRejected("truncated")
    if pos < len(raw):
        meta["trailing_data"] = True
    return ihdr, b"".join(idat), meta


def _png_uniform(ihdr, idat):
    """Heuristic ceiling: only 8-bit non-interlaced PNG; flags near-constant pixel data."""
    w, h, depth, ctype, _, _, interlace = ihdr
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(ctype)
    if channels is None or depth != 8 or interlace != 0 or w * h < 64:
        return None
    expected = (w * channels + 1) * h
    if expected > MAX_DECODE_BYTES:
        return None
    try:
        data = zlib.decompressobj().decompress(idat, expected + 1)
    except zlib.error:
        raise MediaRejected("corrupt_pixel_data")
    if len(data) != expected:
        raise MediaRejected("truncated")
    return len(set(data)) <= 8


# --------------------------------------------------------------- JPEG
def _exif_flags(body):
    """body = APP1 payload after b'Exif\\0\\0'. Returns (has_gps, orientation|None)."""
    if len(body) < 8:
        return False, None
    bo = "<" if body[:2] == b"II" else ">" if body[:2] == b"MM" else None
    if bo is None:
        return False, None
    try:
        off = struct.unpack(bo + "I", body[4:8])[0]
        n = struct.unpack(bo + "H", body[off:off + 2])[0]
        gps, orient = False, None
        for i in range(min(n, 256)):
            e = body[off + 2 + 12 * i: off + 14 + 12 * i]
            if len(e) < 12:
                break
            tag = struct.unpack(bo + "H", e[:2])[0]
            if tag == 0x8825:
                gps = True
            elif tag == 0x0112:
                orient = struct.unpack(bo + "H", e[8:10])[0]
        return gps, orient
    except struct.error:
        return False, None


def _jpeg_segments(raw):
    """Yield (marker, start, end) for header segments; return scan_start."""
    pos, segs = 2, []
    while True:
        if pos + 4 > len(raw):
            raise MediaRejected("truncated")
        if raw[pos] != 0xFF:
            raise MediaRejected("bad_marker")
        while pos < len(raw) and raw[pos] == 0xFF:
            pos += 1
        marker = raw[pos]
        pos += 1
        if marker == 0xD9:
            raise MediaRejected("no_image_data")
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue
        if pos + 2 > len(raw):
            raise MediaRejected("truncated")
        length = struct.unpack(">H", raw[pos:pos + 2])[0]
        if length < 2 or pos + length > len(raw):
            raise MediaRejected("truncated")
        segs.append((marker, pos - 2, pos + length))
        pos += length
        if marker == 0xDA:
            return segs, pos


def _parse_jpeg(raw):
    segs, scan_start = _jpeg_segments(raw)
    meta = {"exif": False, "gps": False, "xmp": False, "iptc": False,
            "comment": False, "trailing_data": False}
    dims = None
    orientation = None
    for marker, s, e in segs:
        body = raw[s + 4:e]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC) and dims is None:
            if len(body) < 6:
                raise MediaRejected("truncated")
            _, h, w = struct.unpack(">BHH", body[:5])
            dims = (w, h)
        elif marker == 0xE1 and body.startswith(b"Exif\x00\x00"):
            meta["exif"] = True
            gps, orientation = _exif_flags(body[6:])
            meta["gps"] = meta["gps"] or gps
        elif marker == 0xE1 and body.startswith(b"http://ns.adobe.com/xap"):
            meta["xmp"] = True
        elif marker == 0xED:
            meta["iptc"] = True
        elif marker == 0xFE:
            meta["comment"] = True
    if dims is None:
        raise MediaRejected("bad_dimensions")
    eoi = raw.rfind(b"\xff\xd9")
    if eoi < scan_start:
        raise MediaRejected("truncated")
    if eoi + 2 < len(raw):
        meta["trailing_data"] = True
    return dims, meta, orientation, segs, scan_start, eoi + 2


# --------------------------------------------------------------- WebP
def _webp_chunks(raw):
    if len(raw) < 20:
        raise MediaRejected("truncated")
    riff = struct.unpack("<I", raw[4:8])[0]
    if riff + 8 > len(raw):
        raise MediaRejected("truncated")
    pos, chunks = 12, []
    while pos + 8 <= riff + 8:
        tag = raw[pos:pos + 4]
        size = struct.unpack("<I", raw[pos + 4:pos + 8])[0]
        end = pos + 8 + size
        if end > riff + 8:
            raise MediaRejected("truncated")
        chunks.append((tag, pos, end + (size & 1)))
        pos = end + (size & 1)
    return chunks, riff


def _parse_webp(raw):
    chunks, riff = _webp_chunks(raw)
    meta = {"exif": False, "xmp": False, "trailing_data": riff + 8 < len(raw)}
    dims = None
    for tag, s, e in chunks:
        body = raw[s + 8:e]
        if tag == b"VP8X" and len(body) >= 10:
            dims = (int.from_bytes(body[4:7], "little") + 1,
                    int.from_bytes(body[7:10], "little") + 1)
        elif tag == b"VP8 " and dims is None and body[3:6] == b"\x9d\x01\x2a" and len(body) >= 10:
            dims = (struct.unpack("<H", body[6:8])[0] & 0x3FFF,
                    struct.unpack("<H", body[8:10])[0] & 0x3FFF)
        elif tag == b"VP8L" and dims is None and body[:1] == b"\x2f" and len(body) >= 5:
            bits = int.from_bytes(body[1:5], "little")
            dims = ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        elif tag == b"EXIF":
            meta["exif"] = True
        elif tag == b"XMP ":
            meta["xmp"] = True
    if dims is None:
        raise MediaRejected("bad_dimensions")
    return dims, meta, chunks, riff


# ----------------------------------------------------------- public API
def inspect_media(raw, filename, mime_type):
    """Validate declared type vs. content and return a media record.

    Raises MediaRejected for corrupt / mismatching / unrecognized / oversized input.
    status: ok | limited (flags) | unsuitable (no visual content can be interpreted).
    """
    sniffed = sniff(raw)
    by_ext, by_mime, mime = _declared_family(filename, mime_type)
    declared = {x for x in (by_ext, by_mime) if x}
    if sniffed is None:
        raise MediaRejected("unrecognized_type")
    if declared and sniffed not in declared:
        raise MediaRejected("signature_mismatch")
    if len(declared) > 1:
        raise MediaRejected("signature_mismatch")
    record = {"format": sniffed, "mime_type": CANON_MIME[sniffed], "declared_mime_type": mime or None,
              "width": None, "height": None, "status": "ok", "issues": [], "quality_flags": [],
              "metadata": {}, "metadata_present": False, "metadata_strip_supported": sniffed in IMAGE_FORMATS}
    if sniffed in ("dicom", "pdf"):
        record["status"] = "limited"
        record["quality_flags"].append("structure_not_verified")
        record["issues"].append("container_metadata_not_inspected")
        return record
    uniform = None
    if sniffed == "png":
        ihdr, idat, meta = _parse_png(raw)
        dims = (ihdr[0], ihdr[1])
        uniform = _png_uniform(ihdr, idat) if dims[0] * dims[1] <= MAX_PIXELS else None
    elif sniffed == "jpeg":
        dims, meta = _parse_jpeg(raw)[:2]
    else:
        dims, meta = _parse_webp(raw)[:2]
    w, h = dims
    if w < 1 or h < 1:
        raise MediaRejected("bad_dimensions")
    if w * h > MAX_PIXELS:
        raise MediaRejected("too_many_pixels")
    record.update(width=w, height=h, metadata=meta,
                  metadata_present=any(meta.values()))
    short = min(w, h)
    if short < MIN_SHORT_SIDE_UNSUITABLE:
        record["status"] = "unsuitable"
        record["quality_flags"].append("insufficient_resolution")
    elif short < MIN_SHORT_SIDE_LIMITED:
        record["status"] = "limited"
        record["quality_flags"].append("low_resolution")
    if uniform:
        record["status"] = "unsuitable"
        record["quality_flags"].append("no_visual_content_suspected")
    if meta.get("trailing_data"):
        record["issues"].append("trailing_data_after_image")
    if meta.get("gps"):
        record["issues"].append("gps_metadata_present")
    return record


def _minimal_exif(orientation):
    ifd = struct.pack("<HHHIHH", 1, 0x0112, 3, 1, orientation, 0) + b"\x00\x00\x00\x00"
    tiff = b"II*\x00" + struct.pack("<I", 8) + ifd
    payload = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(payload) + 2) + payload


def strip_metadata(raw, fmt):
    """Remove EXIF/GPS/XMP/IPTC/comments/text chunks/trailing data. Orientation is kept
    (JPEG) so the image is not displayed rotated. Returns None if fmt unsupported."""
    if fmt == "png":
        ihdr, idat, _ = _parse_png(raw)
        out, pos = [PNG_SIG], 8
        while pos < len(raw):
            length = struct.unpack(">I", raw[pos:pos + 4])[0]
            ctype = raw[pos + 4:pos + 8]
            end = pos + 12 + length
            if ctype not in PNG_META_CHUNKS:
                out.append(raw[pos:end])
            pos = end
            if ctype == b"IEND":
                break
        return b"".join(out)
    if fmt == "jpeg":
        _, _, orientation, segs, scan_start, end = _parse_jpeg(raw)
        out = [b"\xff\xd8"]
        if orientation in range(1, 9):
            out.append(_minimal_exif(orientation))
        for marker, s, e in segs:
            body = raw[s + 4:e]
            if marker in (0xED, 0xFE):
                continue
            if marker == 0xE1 and (body.startswith(b"Exif\x00\x00") or body.startswith(b"http://ns.adobe.com/xap")):
                continue
            out.append(raw[s:e])
        out.append(raw[scan_start:end])
        return b"".join(out)
    if fmt == "webp":
        chunks, riff = _webp_chunks(raw)
        body = []
        for tag, s, e in chunks:
            if tag in (b"EXIF", b"XMP "):
                continue
            piece = bytearray(raw[s:e])
            if tag == b"VP8X":
                piece[8] &= ~0x0C & 0xFF      # clear EXIF and XMP flags
            body.append(bytes(piece))
        payload = b"WEBP" + b"".join(body)
        return b"RIFF" + struct.pack("<I", len(payload)) + payload
    return None
