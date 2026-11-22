"""Deterministic publication checks for the launcher's filesystem receipts."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/run_local_review.py'
SPEC = importlib.util.spec_from_file_location('run_local_review_receipts', SCRIPT)
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)


class InterruptedWrite:
    """Keep real file I/O, but fail after writing a prefix of the JSON."""

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def write(self, data):
        self.stream.write(data[:max(1, len(data) // 2)])
        self.stream.flush()
        raise OSError('Synthetic interrupted receipt write')


class LocalReviewReceiptTests(unittest.TestCase):
    def check_publication(self, name, previous):
        """Read after the writer opens its file, before it can write any JSON."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / name
            if previous is not None:
                path.write_text(json.dumps(previous), encoding='utf8')
            receipt = {'state': 'CLINICALLY_PENDING', 'synthetic_only': True,
                       'capabilities': {'t05_native_extraction': True},
                       'label': 'Revisión sintética', 'processes': {'app': 123}}
            opened, resume = Event(), Event()
            original_open = io.open

            def paused_open(file, mode='r', *args, **kwargs):
                stream = original_open(file, mode, *args, **kwargs)
                if 'w' in mode:
                    opened.set()
                    if not resume.wait(timeout=5):
                        stream.close()
                        raise TimeoutError('Receipt observer did not release the writer')
                return stream

            with patch('io.open', side_effect=paused_open), ThreadPoolExecutor(max_workers=1) as pool:
                pending = pool.submit(LAUNCHER.write_receipt, path, receipt)
                try:
                    self.assertTrue(opened.wait(timeout=5), 'Writer did not open its file')
                    # This is the readiness/read sequence used by check_local_review.py.
                    observed = json.loads(path.read_text()) if path.is_file() else None
                    self.assertEqual(observed, previous)
                finally:
                    resume.set()
                pending.result(timeout=5)
            self.assertEqual(json.loads(path.read_text()), receipt)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_initial_launch_never_exposes_empty_or_partial_json(self):
        self.check_publication('LAUNCH.json', None)

    def test_replacement_keeps_complete_previous_receipt_visible(self):
        self.check_publication('STOP.json', {'exit_codes': {'app': 0}})

    def test_interrupted_write_leaves_no_readiness_marker_or_temporary_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'LAUNCH.json'
            original_open = io.open

            def interrupted_open(file, mode='r', *args, **kwargs):
                stream = original_open(file, mode, *args, **kwargs)
                return InterruptedWrite(stream) if 'w' in mode else stream

            with patch('io.open', side_effect=interrupted_open):
                with self.assertRaisesRegex(OSError, 'Synthetic interrupted'):
                    LAUNCHER.write_receipt(path, {'synthetic_only': True})
            self.assertFalse(path.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_failed_publication_preserves_previous_receipt_and_cleans_temporary_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'STOP.json'
            previous = {'exit_codes': {'app': 0}}
            path.write_text(json.dumps(previous), encoding='utf8')
            with patch.object(LAUNCHER.os, 'replace', side_effect=OSError('Synthetic publication failure')):
                with self.assertRaisesRegex(OSError, 'Synthetic publication'):
                    LAUNCHER.write_receipt(path, {'exit_codes': {'app': 1}})
            self.assertEqual(json.loads(path.read_text()), previous)
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
