"""Deterministic synthetic image bytes (no patient data, no real clinical content).

Ordinary fixtures encode actual two-colour pictures. Dimension-only rejection cases use headers.
"""
import io
import struct
import zlib


def _chunk(ctype, body):
    return (struct.pack(">I", len(body)) + ctype + body
            + struct.pack(">I", zlib.crc32(ctype + body) & 0xFFFFFFFF))


def png(width=256, height=256, seed=1, uniform=False, extra_chunks=(), trailing=b""):
    """8-bit RGB PNG. Non-uniform pixels come from a seeded LCG (many distinct values)."""
    state, rows = seed, []
    for _ in range(height):
        row = bytearray([0])
        for _ in range(width * 3):
            if uniform:
                row.append(120)
            else:
                state = (state * 1103515245 + 12345) & 0x7FFFFFFF
                row.append((state >> 16) & 0xFF)
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
    for ctype, body in extra_chunks:
        out += _chunk(ctype, body)
    out += _chunk(b"IDAT", zlib.compress(b"".join(rows))) + _chunk(b"IEND", b"")
    return out + trailing


def exif_app1(gps=True, orientation=6):
    entries = [(0x0112, 3, 1, orientation)]
    if gps:
        entries.append((0x8825, 4, 1, 38))
    ifd = struct.pack("<H", len(entries))
    for tag, typ, cnt, val in entries:
        ifd += struct.pack("<HHI", tag, typ, cnt) + (struct.pack("<HH", val, 0) if typ == 3
                                                       else struct.pack("<I", val))
    ifd += b"\x00\x00\x00\x00"
    if gps:
        ifd += b"\x00" * 6  # Empty GPS IFD, no location.
    payload = b"Exif\x00\x00" + b"II*\x00" + struct.pack("<I", 8) + ifd
    return b"\xff\xe1" + struct.pack(">H", len(payload) + 2) + payload


def _picture_bytes(fmt, width, height):
    from PIL import Image
    with Image.new("RGB", (width, height), "white") as picture, io.BytesIO() as stream:
        picture.paste("blue", box=(0, 0, width // 2, height))
        picture.save(stream, format=fmt)
        return stream.getvalue()


def jpeg(width=256, height=256, exif=False, gps=True, comment=None, trailing=b"", eoi=True):
    if min(width, height) < 1 or max(width, height) > 2048:
        # Dimension-only rejection case. Never allocate an oversized test raster.
        header = b"\xff\xc0\x00\x0b\x08" + struct.pack(">HH", height, width) + b"\x01\x01\x11\x00"
        return b"\xff\xd8" + header + b"\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\xff\xd9"
    pixels = _picture_bytes("JPEG", width, height)
    metadata = exif_app1(gps=gps) if exif else b""
    if comment is not None:
        metadata += b"\xff\xfe" + struct.pack(">H", len(comment) + 2) + comment
    return pixels[:2] + metadata + (pixels[2:] if eoi else pixels[2:-2]) + trailing


def webp(width=256, height=256, exif=False, xmp=False):
    encoded = _picture_bytes("WEBP", width, height)
    if not (exif or xmp):
        return encoded
    flags = (0x08 if exif else 0) | (0x04 if xmp else 0)
    vp8x = bytes([flags, 0, 0, 0]) + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")
    chunks = b"VP8X" + struct.pack("<I", 10) + vp8x + encoded[12:]
    if exif:
        exif_data = exif_app1()[10:]
        chunks += b"EXIF" + struct.pack("<I", len(exif_data)) + exif_data
        if len(exif_data) % 2:
            chunks += b"\x00"
    if xmp:
        chunks += b"XMP " + struct.pack("<I", 8) + b"XMPDATA!"
    payload = b"WEBP" + chunks
    return b"RIFF" + struct.pack("<I", len(payload)) + payload
