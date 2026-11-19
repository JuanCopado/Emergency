"""Portable artifact names reject traversal before scientific imports or I/O."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from render_rsna_ich_dicom import _case_output_directory, render_exam


class ArtifactIdentifierBoundaryTests(unittest.TestCase):
    def test_invalid_ids_fail_before_imports_decoding_or_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            for identifier in ('../escape', '..', '.', '/absolute', 'C:/escape',
                    r'C:\escape', r'..\escape', 'a/b', 'a:b', 'a.', 'a ',
                    'a\n', '', 'CON', 'nul', 'COM1', 'LPT9', 'x'*129, None):
                with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                    render_exam([], root, identifier)
            self.assertEqual(list(root.iterdir()), [])

    def test_valid_generated_and_portable_ids_preserve_exact_component(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            for identifier in ('rsnaich-0123456789abcdef', 'SYNTHETIC_01', 'x', 'a'*128):
                self.assertEqual(_case_output_directory(root, identifier), root/identifier)
            self.assertEqual(list(root.iterdir()), [])

    def test_existing_symlink_cannot_redirect_the_case_directory(self):
        with tempfile.TemporaryDirectory() as td:
            base = pathlib.Path(td); root = base/'root'; outside = base/'outside'
            root.mkdir(); outside.mkdir()
            try:
                (root/'synthetic').symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('Symlink creation unavailable on this Windows host')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                _case_output_directory(root, 'synthetic')
            self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
