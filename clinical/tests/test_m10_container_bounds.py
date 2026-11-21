"""R6 · M10 N4: bounded header-segment / chunk enumeration (synthetic data only)."""
import io
import struct
import sys
import tracemalloc
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import image_upload_guard as guard  # noqa: E402


def pillow_bytes(fmt):
    out = io.BytesIO()
    Image.effect_noise((256, 256), 64).convert("RGB").save(out, format=fmt)
    return out.getvalue()


def jpeg_with_segments(count):
    raw = pillow_bytes("JPEG")
    return raw[:2] + b"\xff\xe2\x00\x02" * count + raw[2:]


def webp_with_chunks(count):
    raw = pillow_bytes("WEBP")
    body = raw[8:] + b"JUNK\x00\x00\x00\x00" * count
    return b"RIFF" + struct.pack("<I", len(body)) + body


def oversized_jpeg():
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, 8, 8, 1) + b"\x01\x11\x00"
    return (b"\xff\xd8" + b"\xff\xe2\x00\x02" * ((guard.MAX_TRANSFER_BYTES - 60) // 4) + sof
            + b"\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00\x00\xff\xd9")


def oversized_webp():
    vp8x = b"VP8X" + struct.pack("<I", 10) + bytes(4) + (63).to_bytes(3, "little") * 2
    body = b"WEBP" + vp8x + b"JUNK\x00\x00\x00\x00" * ((guard.MAX_TRANSFER_BYTES - 30) // 8)
    return b"RIFF" + struct.pack("<I", len(body)) + body


class ContainerBounds(unittest.TestCase):
    def test_ordinary_files_with_many_but_bounded_segments_remain_admissible(self):
        for name, raw, mime in (("a.jpg", jpeg_with_segments(guard.MAX_JPEG_HEADER_SEGMENTS - 20), "image/jpeg"),
                                ("a.webp", webp_with_chunks(guard.MAX_WEBP_CHUNKS - 5), "image/webp")):
            with self.subTest(name):
                self.assertNotEqual(guard.inspect_media(raw, name, mime)["status"], "unsuitable")
        for fmt, mime in (("JPEG", "image/jpeg"), ("WEBP", "image/webp"), ("PNG", "image/png")):
            with self.subTest(fmt):
                self.assertEqual(guard.inspect_media(pillow_bytes(fmt), "a." + fmt.lower(), mime)["status"], "ok")

    def test_excess_segments_are_rejected_at_the_cap(self):
        for name, raw, mime in (("a.jpg", jpeg_with_segments(guard.MAX_JPEG_HEADER_SEGMENTS + 5), "image/jpeg"),
                                ("a.webp", webp_with_chunks(guard.MAX_WEBP_CHUNKS + 5), "image/webp")):
            with self.subTest(name), self.assertRaises(guard.MediaRejected) as ctx:
                guard.inspect_media(raw, name, mime)
            self.assertEqual(ctx.exception.code, "too_many_segments")

    def test_transport_sized_segment_floods_are_rejected_without_large_allocation(self):
        for name, raw, mime in (("a.jpg", oversized_jpeg(), "image/jpeg"), ("a.webp", oversized_webp(), "image/webp")):
            with self.subTest(name):
                self.assertLessEqual(len(raw), guard.MAX_TRANSFER_BYTES)
                tracemalloc.start()
                try:
                    with self.assertRaises(guard.MediaRejected) as ctx:
                        guard.inspect_media(raw, name, mime)
                    peak = tracemalloc.get_traced_memory()[1]
                finally:
                    tracemalloc.stop()
                self.assertEqual(ctx.exception.code, "too_many_segments")
                self.assertLess(peak, 2_000_000)


if __name__ == "__main__":
    unittest.main()
