"""Synthetic image/container regressions; no clinical images or real blind bank."""
import hashlib
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zlib

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from multimodal import intake, demo
from multimodal.bank import blinded_inputs


def png_chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


class MediaBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.png = self.image_bytes('PNG')
        self.jpeg = self.image_bytes('JPEG')

    def image_bytes(self, format_, **options):
        buffer = io.BytesIO()
        Image.new('RGB', (16, 12), (20, 60, 90)).save(buffer, format_, **options)
        return buffer.getvalue()

    def asset(self, payload, suffix='.png'):
        path = self.root / ('asset-001' + suffix)
        path.write_bytes(payload)
        return dict(id='asset-001', path=path.name, size_bytes=len(payload),
                    sha256=hashlib.sha256(payload).hexdigest(), derivative=False)

    def blind_bank(self, asset):
        # Artificial pixels and declarations exercise only software gates.
        return dict(schema_version='1.0', cases=[dict(
            id='case-001', patient_group_id='fixture-patient', study_group_id='fixture-study',
            source_group_id='fixture-source', split='blind_test', data_kind='authorized_deidentified',
            source_known=False, annotated=False, modality='ecg', task_id='ecg_still',
            context={}, assets=[asset], rights=dict(authorized=True, authorization_ref='fixture',
                allowed_uses=['blind_test']), privacy=dict(metadata_reviewed=True,
                pixels_reviewed=True, reviewer_id='fixture', reviewed_sha256=[asset['sha256']]))])

    def assert_metadata_blocked(self, payload, suffix='.png'):
        asset = self.asset(payload, suffix)
        report = intake.inspect_media(self.root, asset)
        self.assertEqual(report['errors'], [], report)
        self.assertTrue(report['metadata_present'])
        self.assertNotIn('SECRET-DIAGNOSIS', json.dumps(report))
        with self.assertRaisesRegex(ValueError, '^blind_media_metadata_requires_clean_derivative$'):
            blinded_inputs(self.blind_bank(asset), self.root)
        self.assertEqual((self.root / asset['path']).read_bytes(), payload)

    def test_plain_png_and_baseline_progressive_jpeg_remain_admissible(self):
        for payload, suffix in ((self.png, '.png'), (self.jpeg, '.jpg'),
                                (self.image_bytes('JPEG', progressive=True), '.jpeg')):
            with self.subTest(suffix=suffix, progressive=payload != self.jpeg):
                asset = self.asset(payload, suffix)
                report = intake.inspect_media(self.root, asset)
                self.assertEqual(report['errors'], [])
                self.assertFalse(report['metadata_present'])
                self.assertEqual(len(blinded_inputs(self.blind_bank(asset), self.root)), 1)

    def test_late_png_text_and_exif_chunks_are_not_hidden_by_lazy_decoder(self):
        end = self.png.rindex(b'\x00\x00\x00\x00IEND')
        for kind, payload in ((b'tEXt', b'diagnosis\0SECRET-DIAGNOSIS'),
                              (b'zTXt', b'diagnosis\0\0' + zlib.compress(b'SECRET-DIAGNOSIS')),
                              (b'iTXt', b'diagnosis\0\0\0\0\0SECRET-DIAGNOSIS'),
                              (b'eXIf', b'II\x2a\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00')):
            with self.subTest(kind=kind):
                self.assert_metadata_blocked(self.png[:end] + png_chunk(kind, payload) + self.png[end:])

    def test_png_time_private_and_trailing_bytes_are_metadata(self):
        end = self.png.rindex(b'\x00\x00\x00\x00IEND')
        for kind, payload in ((b'tIME', struct.pack('>H5B', 2026, 11, 20, 12, 0, 0)),
                              (b'prVa', b'SECRET-DIAGNOSIS')):
            with self.subTest(kind=kind):
                self.assert_metadata_blocked(self.png[:end] + png_chunk(kind, payload) + self.png[end:])
        self.assert_metadata_blocked(self.png + b'SECRET-DIAGNOSIS')

    def test_jpeg_unknown_app_comment_and_trailing_bytes_are_metadata(self):
        for marker in (b'\xff\xe7', b'\xff\xfe'):
            payload = b'SECRET-DIAGNOSIS\xff\xd9'
            with self.subTest(marker=marker):
                self.assert_metadata_blocked(self.jpeg[:2] + marker + struct.pack('>H', len(payload) + 2)
                                             + payload + self.jpeg[2:], '.jpg')
        self.assert_metadata_blocked(self.jpeg + b'SECRET-DIAGNOSIS', '.jpg')

    def test_jpeg_metadata_between_progressive_scans_is_detected(self):
        raw = self.image_bytes('JPEG', progressive=True)
        # Insert a legal APP segment between scans, not before the initial SOS.
        position = raw.index(b'\xff\xda', raw.index(b'\xff\xda') + 2)
        data = b'SECRET-DIAGNOSIS'
        raw = raw[:position] + b'\xff\xe7' + struct.pack('>H', len(data) + 2) + data + raw[position:]
        self.assert_metadata_blocked(raw, '.jpg')

    def test_non_jfif_app0_and_jfif_thumbnail_are_not_a_metadata_exception(self):
        for data in (b'not-jfif-SECRET-DIAGNOSIS',
                     b'JFIF\0\x01\x01\x00\x00\x01\x00\x01\x01\x01\x01\x02\x03'):
            raw = self.jpeg[:2] + b'\xff\xe0' + struct.pack('>H', len(data) + 2) + data + self.jpeg[2:]
            self.assert_metadata_blocked(raw, '.jpg')

    def test_corrupt_container_lengths_crc_and_missing_end_fail_closed(self):
        damaged_crc = self.png[:-1] + bytes([self.png[-1] ^ 1])
        for raw, suffix in ((self.png[:-12], '.png'), (damaged_crc, '.png'),
                            (self.jpeg[:-2], '.jpg'),
                            (self.jpeg[:2] + b'\xff\xe7\xff\xffX' + self.jpeg[2:], '.jpg')):
            with self.subTest(suffix=suffix, size=len(raw)):
                self.assertTrue(intake.inspect_media(self.root, self.asset(raw, suffix))['errors'])

    def test_hardlink_is_rejected_when_filesystem_exposes_link_count(self):
        asset = self.asset(self.png)
        try:
            os.link(self.root / asset['path'], self.root / 'alias.png')
        except OSError as exc:
            self.skipTest('filesystem does not permit synthetic hardlink: ' + type(exc).__name__)
        if (self.root / asset['path']).stat().st_nlink < 2:
            self.skipTest('filesystem does not expose hardlink count')
        self.assertEqual(intake.inspect_media(self.root, asset)['errors'], ['hardlinked_file_forbidden'])

    def test_symlink_is_rejected_when_creation_is_supported(self):
        asset = self.asset(self.png)
        link = self.root / 'linked.png'
        try:
            link.symlink_to(self.root / asset['path'])
        except OSError as exc:
            self.skipTest('filesystem does not permit synthetic symlink: ' + type(exc).__name__)
        asset['path'] = link.name
        self.assertEqual(intake.inspect_media(self.root, asset)['errors'], ['linked_path_forbidden'])

    @unittest.skipUnless(os.name == 'nt', 'Windows junction API required')
    def test_windows_junction_is_rejected_without_following_or_removing_target(self):
        import _winapi
        if not hasattr(_winapi, 'CreateJunction'):
            self.skipTest('runtime does not expose CreateJunction')
        target = self.root / 'target'
        target.mkdir()
        (target / 'asset-001.png').write_bytes(self.png)
        link = self.root / 'junction'
        try:
            _winapi.CreateJunction(str(target), str(link))
        except OSError as exc:
            self.skipTest('filesystem does not permit synthetic junction: ' + type(exc).__name__)
        try:
            self.assertTrue(link.is_junction())
            asset = dict(id='asset-001', path='junction/asset-001.png', size_bytes=len(self.png),
                         sha256=hashlib.sha256(self.png).hexdigest(), derivative=False)
            self.assertEqual(intake.inspect_media(self.root, asset)['errors'], ['linked_path_forbidden'])
        finally:
            # Check the lexical absolute link path, not its resolved target.
            self.assertEqual(link.absolute().parent, self.root.resolve())
            self.assertTrue(link.is_junction())
            link.rmdir()  # Nonrecursive removal of the junction itself only.
        self.assertTrue(target.is_dir())
        self.assertEqual((target / 'asset-001.png').read_bytes(), self.png)

    def test_media_tool_is_never_selected_from_current_directory(self):
        poison = self.root / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
        poison.write_bytes(b'not-an-executable')
        poison.chmod(0o755)
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            for value in (str(self.root), '.', ''):
                with self.subTest(path=value), mock.patch.dict(os.environ, {'PATH': value}), \
                        mock.patch.object(intake.subprocess, 'run') as run:
                    run.return_value.returncode = 0
                    with self.assertRaisesRegex(ValueError, '^local_media_tool_unavailable$'):
                        intake._run('ffmpeg', [])
                    run.assert_not_called()
        finally:
            os.chdir(previous)

    def test_demo_preflights_tools_before_creating_any_destination(self):
        destination = self.root / 'new-demo'
        with mock.patch.dict(os.environ, {'PATH': ''}):
            with self.assertRaisesRegex(ValueError, '^demo_requires_ffmpeg_and_ffprobe$'):
                demo.create_demo(destination)
        self.assertFalse(destination.exists())

    def test_absolute_path_tool_is_resolved_and_never_uses_script_launcher(self):
        tool_dir = self.root / 'tools'
        tool_dir.mkdir()
        filename = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        executable = tool_dir / filename
        executable.write_bytes(b'fixture-only-not-executed')
        executable.chmod(0o755)
        with mock.patch.dict(os.environ, {'PATH': str(tool_dir)}):
            self.assertEqual(intake.resolve_media_tool('ffmpeg'), str(executable.resolve()))
            with self.assertRaisesRegex(ValueError, '^local_media_tool_unavailable$'):
                intake.resolve_media_tool('ffmpeg.cmd')

    def test_demo_subprocess_error_has_fixed_message_without_path(self):
        # Test the subprocess error boundary independently of installed tools.
        executable = str((self.root / 'synthetic-media-tool').absolute())
        for index, error in enumerate((subprocess.TimeoutExpired('SECRET-PATH', 30),
                                       OSError('SECRET-PATH'))):
            with self.subTest(error=type(error).__name__), \
                    mock.patch.object(demo, 'resolve_media_tool', return_value=executable), \
                    mock.patch.object(demo.subprocess, 'run', side_effect=error) as run:
                with self.assertRaisesRegex(ValueError, '^demo_media_generation_failed$'):
                    demo.create_demo(self.root / f'new-demo-{index}')
                run.assert_called_once()

    def test_navigation_probes_timestamps_once_for_all_sampled_frames(self):
        try:
            ffmpeg = intake.resolve_media_tool('ffmpeg')
            intake.resolve_media_tool('ffprobe')
        except ValueError:
            self.skipTest('local media tools not available on absolute PATH')
        path = self.root / 'video.mp4'
        subprocess.run([ffmpeg, '-v', 'error', '-nostdin', '-f', 'lavfi', '-i',
                        'testsrc=size=64x48:rate=5', '-t', '1', '-c:v', 'mpeg4',
                        '-an', str(path)], capture_output=True, check=True, timeout=20)
        raw = path.read_bytes()
        asset = dict(id='asset-002', path=path.name, size_bytes=len(raw),
                     sha256=hashlib.sha256(raw).hexdigest(), derivative=False)
        with mock.patch.object(intake, '_run', wraps=intake._run) as run:
            frames = intake.extract_navigation_frames(self.root, asset, self.root / 'frames', count=3)
        self.assertEqual(sum('-show_frames' in call.args[1] for call in run.call_args_list), 1)
        self.assertEqual([f['source_frame_index'] for f in frames['frames']], [0, 2, 4])
        self.assertEqual([f['presentation_time_seconds'] for f in frames['frames']], [0, 0.4, 0.8])


if __name__ == '__main__':
    unittest.main()
