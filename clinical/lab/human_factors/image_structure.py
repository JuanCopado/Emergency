"""Bounded container framing checks before decoding local laboratory images.

A single image must consume the entire file. Bytes following its container are
rejected, including whitespace, padding outside RIFF and concatenated images.
Metadata inside a valid container is retained for the separate privacy review.
"""
import zlib

MAX_PARTS = 65536


def png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("invalid PNG signature")
    offset, parts, seen_data, data_ended = 8, 0, False, False
    while offset < len(data):
        parts += 1
        if parts > MAX_PARTS or offset + 12 > len(data):
            break
        size = int.from_bytes(data[offset:offset + 4], "big")
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + size
        if end > len(data) or not all(65 <= c <= 90 or 97 <= c <= 122 for c in kind):
            break
        if zlib.crc32(data[offset + 4:end - 4]) != int.from_bytes(data[end - 4:end], "big"):
            break
        if parts == 1 and (kind != b"IHDR" or size != 13):
            break
        if kind == b"IHDR" and parts != 1:
            break
        if kind == b"IDAT":
            if data_ended:
                break
            seen_data = True
        elif seen_data:
            data_ended = True
        if kind == b"IEND":
            if size == 0 and seen_data and end == len(data):
                return
            break
        offset = end
    raise ValueError("invalid PNG chunks, CRC or image end")


def jpeg(data):
    if data[:2] != b"\xff\xd8":
        raise ValueError("invalid JPEG signature")
    offset, parts, scans = 2, 0, 0
    while offset < len(data):
        parts += 1
        if parts > MAX_PARTS or data[offset] != 0xff:
            break
        while offset < len(data) and data[offset] == 0xff:
            offset += 1
        if offset == len(data):
            break
        marker = data[offset]
        offset += 1
        if marker == 0xd9:
            if scans and offset == len(data):
                return
            break
        if marker in (0, 0xd8) or 0xd0 <= marker <= 0xd7:
            break
        if marker == 0x01:
            continue
        if offset + 2 > len(data):
            break
        size = int.from_bytes(data[offset:offset + 2], "big")
        if size < 2 or offset + size > len(data):
            break
        offset += size
        if marker != 0xda:
            continue
        scans += 1
        # All scans are walked. EOI in a length-delimited segment is payload.
        while offset < len(data):
            found = data.find(b"\xff", offset)
            if found < 0:
                raise ValueError("missing JPEG image end")
            following = found + 1
            while following < len(data) and data[following] == 0xff:
                following += 1
            if following == len(data):
                raise ValueError("truncated JPEG marker")
            code = data[following]
            if code == 0:
                if following != found + 1:
                    raise ValueError("invalid JPEG byte stuffing")
                offset = following + 1
            elif 0xd0 <= code <= 0xd7:
                offset = following + 1
            else:
                offset = found
                break
    raise ValueError("invalid JPEG segments or image end")


def webp(data):
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("invalid WebP signature")
    if int.from_bytes(data[4:8], "little") + 8 != len(data):
        raise ValueError("invalid WebP RIFF length")
    offset, parts, images = 12, 0, 0
    while offset < len(data):
        parts += 1
        if parts > MAX_PARTS or offset + 8 > len(data):
            break
        kind = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], "little")
        end = offset + 8 + size
        padded_end = end + (size & 1)
        if padded_end > len(data) or (size & 1 and data[end] != 0):
            break
        if kind in (b"ANIM", b"ANMF"):
            break
        if kind == b"VP8X" and (parts != 1 or size != 10 or data[offset + 8] & 2):
            break
        if kind in (b"VP8 ", b"VP8L"):
            images += 1
        offset = padded_end
    else:
        if images == 1:
            return
    raise ValueError("invalid WebP chunks, padding or image end")


VALIDATORS = {"JPEG": jpeg, "PNG": png, "WEBP": webp}
