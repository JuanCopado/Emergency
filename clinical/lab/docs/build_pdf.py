#!/usr/bin/env python3
"""Single editable source (Markdown + LaTeX math) -> HTML -> PDF with repeated table headers, KaTeX math, numbered index and layout checks.

Usage: python3 build_pdf.py --katex-dir DIR --out OUT.pdf [--title T] SOURCE.md [SOURCE2.md ...]
Needs: python 'markdown', node + playwright (Chromium) and KaTeX installed in DIR/node_modules (not committed). It does not change the content of
the sources: numbering, index and typesetting only. Math is written $...$ (inline) and $$...$$ (display)."""
import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATH = re.compile(r"\$\$(.+?)\$\$|(?<![\\$])\$(?!\s)([^$\n]+?)(?<!\s)\$", re.S)


def protect_math(markdown_text):
    items = []
    def swap(match):
        display = match.group(1) is not None
        items.append((match.group(1) if display else match.group(2), display))
        return f"@@MATH{len(items) - 1}@@"
    text = MATH.sub(swap, markdown_text)
    return re.sub(r"\\%", "%", text), items          # a TeX-style escaped percent outside math is a plain percent sign


def render_math(items, katex_dir):
    if not items:
        return []
    run = subprocess.run(["node", str(HERE / "katex_render.cjs"), "--katex-dir", str(katex_dir)], input=json.dumps(items), capture_output=True, text=True)
    if run.returncode != 0:
        raise RuntimeError(run.stderr)
    rendered = json.loads(run.stdout)
    bad = [items[i][0] for i, r in enumerate(rendered) if r is None]
    if bad:
        raise ValueError(f"math that KaTeX cannot render: {bad[:3]}")
    return rendered


def number_headings(page_html):
    """Adds 1., 1.1 numbering to h2/h3 and builds the index. A heading that already starts with its own number keeps it (no double numbering)."""
    counters, toc = [0, 0], []
    already = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s")
    def repl(match):
        level, attrs, inner = int(match.group(1)), match.group(2), match.group(3)
        plain = re.sub(r"<[^>]+>", "", inner)
        anchor = f"s{len(toc)}"
        if level == 1:                                   # a document title: listed in the index, numbering restarts for the next document
            counters[0] = counters[1] = 0
            toc.append((1, "", plain, anchor))
            return f'<h1 id="{anchor}"{attrs}>{inner}</h1>'
        if already.match(plain):
            toc.append((level, "", plain, anchor))
            return f'<h{level} id="{anchor}"{attrs}>{inner}</h{level}>'
        if level == 2:
            counters[0] += 1; counters[1] = 0; label = f"{counters[0]}."
        else:
            counters[1] += 1; label = f"{counters[0]}.{counters[1]}"
        toc.append((level, label, plain, anchor))
        return f'<h{level} id="{anchor}"{attrs}>{label} {inner}</h{level}>'
    return re.sub(r"<h([1-3])([^>]*)>(.*?)</h\1>", repl, page_html, flags=re.S), toc


def mark_wide_tables(page_html):
    def repl(match):
        columns = len(re.findall(r"<th", match.group(0).split("</tr>")[0]))
        return match.group(0).replace("<table>", '<table class="wide">', 1) if columns >= 6 else match.group(0)
    return re.sub(r"<table>.*?</table>", repl, page_html, flags=re.S)


def build(sources, katex_dir, title):
    import markdown
    body = "\n\n".join(Path(s).read_text(encoding="utf-8") for s in sources)
    body, items = protect_math(body)
    rendered = render_math(items, katex_dir)
    page = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])
    for index, tex in enumerate(rendered):
        page = page.replace(f"@@MATH{index}@@", tex)
    if re.search(r"@@MATH\d+@@", page):
        raise ValueError("a math placeholder was not restored")
    page, toc = number_headings(page)
    page = mark_wide_tables(page)
    toc_html = "<nav class=\"toc\"><h2>Índice</h2><ol>" + "".join(f'<li class="l{lv}"><a href="#{a}">{(lab + " ") if lab else ""}{html.escape(text)}</a></li>' for lv, lab, text, a in toc) + "</ol></nav>"
    katex_css = (Path(katex_dir) / "node_modules" / "katex" / "dist" / "katex.min.css").resolve().as_uri()
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{html.escape(title)}</title><link rel="stylesheet" href="{katex_css}">'
            f'<style>{(HERE / "style.css").read_text(encoding="utf-8")}</style></head><body><div class="cover"><h1>{html.escape(title)}</h1></div>{toc_html}{page}</body></html>')


def verify_pdf(pdf):
    import shutil
    problems = []
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    for token in re.findall(r"\\(?:frac|hat|times|text|sum|Delta|rho|qquad|begin)\b|@@MATH", text):
        problems.append(f"unrendered math or placeholder in PDF text: {token}")
    fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    not_embedded = [f for f in fonts if f.split() and f.split()[-5:-4] == ["no"]]
    pages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    return {"pages": pages, "problems": problems, "fonts_not_embedded": len(not_embedded), "fonts": len(fonts), "has_pdftoppm": bool(shutil.which("pdftoppm"))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sources", nargs="+")
    parser.add_argument("--katex-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="Documento")
    args = parser.parse_args(argv)
    out = Path(args.out)
    html_path = out.with_suffix(".html")
    html_path.write_text(build(args.sources, args.katex_dir, args.title), encoding="utf-8")
    run = subprocess.run(["node", str(HERE / "render_pdf.cjs"), str(html_path), str(out)], capture_output=True, text=True, cwd=HERE)
    if run.returncode != 0:
        raise RuntimeError(run.stderr)
    layout = json.loads(run.stdout.strip().splitlines()[-1])
    result = {"layout": layout, "pdf": verify_pdf(out)}
    failures = []
    if layout["overflowTables"] or layout["overflowingCells"]:
        failures.append("table or cell overflow")
    if layout["katexErrors"] or layout["rawMathTokens"]:
        failures.append("unrendered math")
    failures += result["pdf"]["problems"]
    result["ok"] = not failures
    result["failures"] = failures
    print(json.dumps(result, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
