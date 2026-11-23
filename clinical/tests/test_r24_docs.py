"""R24 · documentation pipeline (single editable source -> PDF): unit tests without external tools + an optional full build when KaTeX is available."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "lab" / "docs"
sys.path.insert(0, str(DOCS))
import build_pdf  # noqa: E402


class Pure(unittest.TestCase):
    def test_math_is_protected_and_restored_in_order(self):
        text, items = build_pdf.protect_math("a $x^2$ b $$\\frac{1}{P}$$ c $y$")
        self.assertEqual(items, [("x^2", False), ("\\frac{1}{P}", True), ("y", False)])
        self.assertNotIn("$", text)
        self.assertEqual(text.count("@@MATH"), 3)

    def test_a_dollar_amount_with_spaces_is_not_math_and_escaped_percent_is_plain(self):
        text, items = build_pdf.protect_math("cuesta 5 $ y 6 $ hoy, pérdida 0\\% de bloqueos")
        self.assertEqual(items, [])
        self.assertIn("0% de bloqueos", text)

    def test_headings_are_numbered_and_indexed_without_touching_the_title(self):
        page, toc = build_pdf.number_headings("<h1>T</h1><h2>Uno</h2><h3>a</h3><h3>b</h3><h2>Dos</h2>")
        self.assertIn("<h1>T</h1>", page)
        self.assertEqual([(lv, lab) for lv, lab, _, _ in toc], [(2, "1."), (3, "1.1"), (3, "1.2"), (2, "2.")])

    def test_a_heading_that_already_carries_its_number_is_not_numbered_twice(self):
        page, toc = build_pdf.number_headings("<h1>T</h1><h2>1. Resultado</h2><h2>Sin numero</h2><h3>2.1 ya numerado</h3>")
        self.assertIn("<h2 id=\"s0\">1. Resultado</h2>", page)
        self.assertNotIn("1. 1.", page)
        self.assertIn(">1. Sin numero<", page)          # the unnumbered one is numbered by the generator
        self.assertEqual(toc[0][1], "")

    def test_wide_tables_get_the_compact_class(self):
        narrow = "<table><thead><tr><th>a</th><th>b</th></tr></thead></table>"
        wide = "<table><thead><tr>" + "<th>x</th>" * 7 + "</tr></thead></table>"
        out = build_pdf.mark_wide_tables(narrow + wide)
        self.assertEqual(out.count('class="wide"'), 1)
        self.assertTrue(out.endswith(wide.replace("<table>", '<table class="wide">', 1)))

    def test_the_stylesheet_repeats_table_headers_and_avoids_row_splits_and_letter_breaks(self):
        css = (DOCS / "style.css").read_text(encoding="utf-8")
        self.assertIn("thead { display: table-header-group; }", css)
        self.assertIn("tr { break-inside: avoid; }", css)
        self.assertNotIn("overflow-wrap: anywhere", css.split("th, td")[1].split("}")[0])   # cells must not break words letter by letter
        self.assertIn("@page { size: A4;", css)


def katex_dir():
    path = os.environ.get("HF_KATEX_DIR")
    return path if path and (Path(path) / "node_modules" / "katex").exists() else None


@unittest.skipUnless(katex_dir() and shutil.which("node") and shutil.which("pdftotext") and importlib.util.find_spec("markdown"),
                     "full build needs HF_KATEX_DIR (KaTeX), node + playwright, pdftotext and the 'markdown' package")
class FullBuild(unittest.TestCase):
    def test_the_sample_builds_to_a_clean_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample.pdf"
            code = build_pdf.main(["--katex-dir", katex_dir(), "--out", str(out), "--title", "Muestra", str(DOCS / "sample.md")])
            self.assertEqual(code, 0)
            self.assertGreater(out.stat().st_size, 10000)
            text = subprocess.run(["pdftotext", "-layout", str(out), "-"], capture_output=True, text=True).stdout
            self.assertNotRegex(text, r"\\frac|\\hat|@@MATH|0\\%")
            self.assertGreaterEqual(text.count("Concepto"), 3)      # long table header repeated on each page

    def test_math_that_katex_cannot_render_fails_loudly(self):
        with self.assertRaises(ValueError):
            build_pdf.render_math([("\\unknowncommand{x}", False)], katex_dir())


if __name__ == "__main__":
    unittest.main()
