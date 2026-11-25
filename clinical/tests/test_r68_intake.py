"""Exercise the local intake contract with synthetic file bytes."""
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab"))
from human_factors import intake_r68 as intake

MANIFEST = {"stimuli": [
    {"stimulus_id": "S1-10", "file": None, "container_spec": "jpeg"},
    {"stimulus_id": "S2-09", "file": "stimuli/S2-09.jpg"},
]}


class Intake(unittest.TestCase):
    def receipt_for_bytes(self, data, suffix):
        """Bind the receipt to the actual candidate, even when it is malformed."""
        path = self.delivery / ("candidate" + suffix)
        path.write_bytes(data)
        return {"assets": [{**self.asset, "file": path.name,
                            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}]}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.delivery = root / "incoming"
        self.delivery.mkdir()
        output = io.BytesIO()
        Image.new("RGB", (20, 20)).save(output, format="JPEG")
        data = output.getvalue()
        (root / "outside.jpg").write_bytes(data)
        self.file = self.delivery / "original.jpg"
        self.file.write_bytes(data)
        self.asset = {
            "stimulus_id": "S1-10", "role": "original", "kind": "synthetic",
            "source": "example author and version", "license": "example declaration",
            "permission_ref": "example permissions document", "privacy_ref": "synthetic fixture",
            "transformation": "original", "file": self.file.name,
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        }

    def test_reports_verified_bytes_without_promoting_stimulus(self):
        result = intake.check_receipt({"assets": [self.asset]}, self.delivery, MANIFEST)
        self.assertEqual(result["status"], "BYTES_VERIFIED_REVIEW_PENDING")
        self.assertEqual(result["assets"][0]["sha256"], self.asset["sha256"])
        self.assertIsNone(MANIFEST["stimuli"][0]["file"])

    def test_cli_reads_receipt_and_fails_closed_on_changed_file(self):
        bank = self.delivery.parent / "bank"
        bank.mkdir()
        (bank / "stimuli_manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
        receipt = self.delivery / "recepcion.json"
        receipt.write_text(json.dumps({"assets": [self.asset]}), encoding="utf-8")
        output = io.StringIO()
        with patch.object(intake, "BANK", bank), patch.object(sys, "argv", ["intake", str(receipt)]):
            with redirect_stdout(output):
                intake.main()
            self.assertEqual(json.loads(output.getvalue())["status"], "BYTES_VERIFIED_REVIEW_PENDING")
            self.file.write_bytes(b"changed")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
                intake.main()
            self.assertEqual(result.exception.code, 1)

    def test_rejects_unusable_entries(self):
        for change in (
            {"bytes": 0}, {"sha256": "0" * 64}, {"permission_ref": ""},
            {"file": "../outside.jpg"}, {"file": "missing.jpg"},
            {"stimulus_id": "S2-09"}, {"kind": "unknown"}, {"role": "unknown"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                intake.check_receipt({"assets": [{**self.asset, **change}]}, self.delivery, MANIFEST)
        for assets in ([], [self.asset, self.asset]):
            with self.assertRaises(ValueError):
                intake.check_receipt({"assets": assets}, self.delivery, MANIFEST)

    def test_rejects_corrupt_images_even_when_the_receipt_matches(self):
        data = self.file.read_bytes()[:-12]
        self.file.write_bytes(data)
        asset = {**self.asset, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        with self.assertRaisesRegex(ValueError, "unreadable image"):
            intake.check_receipt({"assets": [asset]}, self.delivery, MANIFEST)

    def test_applies_canonical_format_to_derivatives_but_accepts_an_original_png(self):
        png = self.delivery / "source.png"
        Image.new("RGB", (20, 20)).save(png)
        data = png.read_bytes()
        asset = {**self.asset, "file": png.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        intake.check_receipt({"assets": [asset]}, self.delivery, MANIFEST)
        with self.assertRaisesRegex(ValueError, "stimulus specification"):
            intake.check_receipt({"assets": [{**asset, "role": "derivative"}]}, self.delivery, MANIFEST)

    def test_static_formats_decode_and_have_complete_containers(self):
        for fmt, suffix, options in (
            ("JPEG", ".jpg", {}), ("JPEG", ".jpg", {"progressive": True}),
            ("PNG", ".png", {}), ("WEBP", ".webp", {}),
            ("WEBP", ".webp", {"lossless": True}),
        ):
            with self.subTest(fmt=fmt, options=options):
                output = io.BytesIO()
                Image.new("RGB", (21, 19)).save(output, format=fmt, **options)
                intake.check_image("S1-10", output.getvalue(), suffix, None)

    def test_rejects_incomplete_and_trailing_containers_for_every_format(self):
        for fmt, suffix in (("JPEG", ".jpg"), ("PNG", ".png"), ("WEBP", ".webp")):
            output = io.BytesIO()
            Image.new("RGB", (21, 19)).save(output, format=fmt)
            data = output.getvalue()
            missing_end = data[:-12] if fmt == "PNG" else data[:-2]
            for mutated in (missing_end, data + b"trailer", data + b"\xff\xd9", data + data):
                with self.subTest(fmt=fmt, size=len(mutated)), self.assertRaises(ValueError):
                    intake.check_image("S1-10", mutated, suffix, None)

    def test_png_crc_length_and_end_chunk_are_checked(self):
        import zlib
        output = io.BytesIO()
        Image.new("RGB", (21, 19)).save(output, format="PNG")
        data = output.getvalue()
        bad_crc = bytearray(data)
        bad_crc[-1] ^= 1
        body = b"x"
        malformed_iend = (1).to_bytes(4, "big") + b"IEND" + body
        malformed_iend += zlib.crc32(b"IEND" + body).to_bytes(4, "big")
        for mutated in (bytes(bad_crc), data[:-12] + malformed_iend, data[:8] + b"\xff\xff\xff\xff" + data[12:]):
            with self.subTest(size=len(mutated)), self.assertRaises(ValueError):
                intake.check_image("S1-10", mutated, ".png", None)

    def test_webp_riff_size_chunk_length_and_padding_are_checked(self):
        output = io.BytesIO()
        Image.new("RGB", (21, 19)).save(output, format="WEBP")
        data = output.getvalue()
        too_short = data[:4] + (len(data) - 10).to_bytes(4, "little") + data[8:]
        bad_chunk = data[:16] + b"\xff\xff\xff\xff" + data[20:]
        fragment = data + b"x"
        fragment = fragment[:4] + (len(fragment) - 8).to_bytes(4, "little") + fragment[8:]
        for mutated in (too_short, bad_chunk, fragment):
            with self.subTest(size=len(mutated)), self.assertRaises(ValueError):
                intake.check_image("S1-10", mutated, ".webp", None)

    def test_jpeg_eoi_in_metadata_is_not_the_image_end(self):
        data = self.file.read_bytes()
        payload = b"embedded\xff\xd9marker"
        comment = b"\xff\xfe" + (len(payload) + 2).to_bytes(2, "big") + payload
        intake.check_image("S1-10", data[:2] + comment + data[2:], ".jpg", None)
        for mutated in (data[:2] + comment + data[2:-2], data[:2] + b"\xff\xfe\xff\xff" + data[2:]):
            with self.assertRaises(ValueError):
                intake.check_image("S1-10", mutated, ".jpg", None)

    def test_resolution_and_receipt_size_limits_remain_enforced(self):
        with patch.object(intake, "MAX_IMAGE_PIXELS", 10), self.assertRaises(ValueError):
            intake.check_image("S1-10", self.file.read_bytes(), ".jpg", None)
        with patch.object(intake, "MAX_ASSET_BYTES", 10), self.assertRaises(ValueError):
            intake.check_receipt({"assets": [self.asset]}, self.delivery, MANIFEST)

    def test_transparency_remains_supported(self):
        for fmt, suffix in (("PNG", ".png"), ("WEBP", ".webp")):
            output = io.BytesIO()
            Image.new("RGBA", (21, 19), (2, 3, 4, 100)).save(output, format=fmt)
            intake.check_image("S1-10", output.getvalue(), suffix, None)

    def test_webp_nonzero_or_missing_padding_is_rejected(self):
        output = io.BytesIO()
        Image.new("RGB", (21, 19)).save(output, format="WEBP")
        data = output.getvalue()
        chunk = b"test" + (1).to_bytes(4, "little") + b"x"
        for pad in (b"\x01", b""):
            mutated = data + chunk + pad
            mutated = mutated[:4] + (len(mutated) - 8).to_bytes(4, "little") + mutated[8:]
            with self.assertRaises(ValueError):
                intake.check_image("S1-10", mutated, ".webp", None)

    def test_animated_containers_remain_rejected(self):
        for fmt, suffix in (("PNG", ".png"), ("WEBP", ".webp")):
            output = io.BytesIO()
            Image.new("RGB", (21, 19), "red").save(
                output, format=fmt, save_all=True,
                append_images=[Image.new("RGB", (21, 19), "blue")], duration=100,
            )
            with self.assertRaises(ValueError):
                intake.check_image("S1-10", output.getvalue(), suffix, None)

    def test_every_truncated_prefix_is_rejected_structurally(self):
        from human_factors.image_structure import VALIDATORS
        for fmt in ("JPEG", "PNG", "WEBP"):
            output = io.BytesIO()
            Image.new("RGB", (2, 2)).save(output, format=fmt)
            data = output.getvalue()
            for cut in range(len(data)):
                with self.subTest(fmt=fmt, cut=cut), self.assertRaises(ValueError):
                    VALIDATORS[fmt](data[:cut])

    def test_jpeg_rejects_false_markers_and_unterminated_scans(self):
        from human_factors.image_structure import jpeg
        for data in (
            b"\xff\xd8\xff\xd9", b"\xff\xd8\xff\xd8", b"\xff\xd8\xff\x00",
            b"\xff\xd8\xff\xda\x00\x02abc",
            b"\xff\xd8\xff\xda\x00\x02abc\xff",
            b"\xff\xd8\xff\xda\x00\x02abc\xff\xff\x00\xff\xd9",
            b"\xff\xd8\xff\xda\x00\x02abc\xff\x00",
            b"\xff\xd8\xff\xfe\x00\x01",
        ):
            with self.subTest(data=data), self.assertRaises(ValueError):
                jpeg(data)

    def test_segment_work_budget_rejects_even_decodable_containers(self):
        from human_factors import image_structure
        for fmt, suffix in (("JPEG", ".jpg"), ("PNG", ".png"), ("WEBP", ".webp")):
            output = io.BytesIO()
            Image.new("RGB", (21, 19)).save(output, format=fmt)
            with patch.object(image_structure, "MAX_PARTS", 0), self.assertRaises(ValueError):
                intake.check_image("S1-10", output.getvalue(), suffix, None)

    def test_receipt_rejects_r84_png_and_jpeg_defects_with_matching_hashes(self):
        output = io.BytesIO()
        Image.new("RGB", (20, 20)).save(output, format="PNG")
        png = output.getvalue()
        # Corrupt the IDAT CRC while preserving every other chunk and IEND.
        idat = png.index(b"IDAT")
        crc_offset = idat + 4 + int.from_bytes(png[idat - 4:idat], "big")
        bad_crc = bytearray(png)
        bad_crc[crc_offset] ^= 1
        jpeg = self.file.read_bytes()
        cases = (
            ("png_without_iend", ".png", png[:-12]),
            ("png_truncated_inside_idat", ".png", png[:-20]),
            ("png_invalid_idat_crc", ".png", bytes(bad_crc)),
            ("jpeg_payload_after_eoi", ".jpg", jpeg + b"payload"),
            ("jpeg_space_after_eoi", ".jpg", jpeg + b" "),
            ("jpeg_second_eoi", ".jpg", jpeg + b"\xff\xd9"),
            ("jpeg_concatenated_image", ".jpg", jpeg + jpeg),
        )
        for name, suffix, data in cases:
            receipt = self.receipt_for_bytes(data, suffix)
            with self.subTest(case=name), self.assertRaisesRegex(ValueError, "unreadable image"):
                intake.check_receipt(receipt, self.delivery, MANIFEST)

    def test_receipt_rejects_webp_framing_with_matching_hashes(self):
        output = io.BytesIO()
        Image.new("RGB", (20, 20)).save(output, format="WEBP")
        webp = output.getvalue()
        odd_chunk = b"test" + (1).to_bytes(4, "little") + b"x"
        cases = [webp[:-2], webp + b"payload", webp + webp,
                 webp[:16] + b"\xff\xff\xff\xff" + webp[20:]]
        for pad in (b"", b"\x01"):
            data = webp + odd_chunk + pad
            cases.append(data[:4] + (len(data) - 8).to_bytes(4, "little") + data[8:])
        for index, data in enumerate(cases):
            receipt = self.receipt_for_bytes(data, ".webp")
            with self.subTest(case=index), self.assertRaisesRegex(ValueError, "unreadable image"):
                intake.check_receipt(receipt, self.delivery, MANIFEST)

    def test_receipt_accepts_compatible_valid_variants_in_all_three_formats(self):
        from PIL.PngImagePlugin import PngInfo
        text = PngInfo()
        text.add_text("Comment", "synthetic fixture")
        exif = Image.Exif()
        exif[270] = "synthetic fixture metadata"
        variants = (
            ("JPEG", ".jpg", "RGB", {}),
            ("JPEG", ".jpeg", "RGB", {"progressive": True}),
            ("JPEG", ".jpg", "L", {}),
            ("JPEG", ".jpg", "CMYK", {}),
            ("JPEG", ".jpg", "RGB", {"exif": exif.tobytes()}),
            ("PNG", ".png", "RGB", {"pnginfo": text}),
            ("PNG", ".png", "RGBA", {}),
            ("PNG", ".png", "P", {}),
            ("PNG", ".png", "L", {}),
            ("PNG", ".png", "I;16", {}),
            ("WEBP", ".webp", "RGB", {}),
            ("WEBP", ".webp", "RGB", {"lossless": True}),
            ("WEBP", ".webp", "RGBA", {"lossless": True}),
            ("WEBP", ".webp", "RGB", {"exif": exif.tobytes()}),
        )
        for fmt, suffix, mode, options in variants:
            output = io.BytesIO()
            Image.new(mode, (21, 19)).save(output, format=fmt, **options)
            receipt = self.receipt_for_bytes(output.getvalue(), suffix)
            with self.subTest(fmt=fmt, mode=mode, options=options):
                result = intake.check_receipt(receipt, self.delivery, MANIFEST)
                self.assertEqual(result["status"], "BYTES_VERIFIED_REVIEW_PENDING")
                self.assertEqual(result["assets"][0]["sha256"], receipt["assets"][0]["sha256"])
                self.assertIsNone(MANIFEST["stimuli"][0]["file"])

    def test_direct_cli_accepts_a_matching_physical_receipt(self):
        import subprocess
        receipt = self.delivery / "recepcion.json"
        receipt.write_text(json.dumps({"assets": [self.asset]}), encoding="utf-8")
        run = subprocess.run(
            [sys.executable, str(Path(intake.__file__).resolve()), str(receipt)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["status"], "BYTES_VERIFIED_REVIEW_PENDING")
