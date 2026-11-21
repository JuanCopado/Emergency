# Embedded PDF fonts

Unmodified DejaVu Sans Regular and Bold 2.37, distributed under the accompanying
`LICENSE-DejaVu.txt` (Bitstream Vera license; DejaVu changes public domain).
No system or proprietary font is required. The PDF embeds the used glyph subsets.

Official release:
https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip

Archive SHA-256 (verified before extraction):
`7576310b219e04159d35ff61dd4a4ec4cdba4f35c00e002a136f00e96a908b0a`

Published checksum: https://dejavu-fonts.github.io/Download.html

- `DejaVuSans.ttf`: `7da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954`
- `DejaVuSans-Bold.ttf`: `e6476c1b80502924294eed40894c5b18e06c181444ca953e5334262df9c27724`

Install PDF runtime with `python -m pip install -r clinical/requirements.txt`;
for QA use `clinical/requirements-test.txt` instead. Characters absent from the
bundled fonts raise an explicit error before writing output; there is no ASCII
fallback or silent substitution. Complex-script shaping is not validated here.


## Emergency CJK Regular and Bold

Static instances of Noto Sans SC 2.004 support Simplified Chinese text in PDF
exports. The font software is Copyright 2014–2021 Adobe, with Reserved Font
Name “Source”. The derived family is named Emergency CJK. The accompanying
`LICENSE-NotoSansSC.txt` preserves SIL Open Font License 1.1.

The upstream font and license came from the official `notofonts/noto-cjk`
repository at commit `523d033d6cb47f4a80c58a35753646f5c3608a78` (tag
`Sans2.004`). `noto-cjk-manifest.json` records immutable URLs, the upstream
Git blob and SHA-256, output SHA-256, file sizes and weight axes. The original
variable font was pinned at weights 400 and 700 with `fonttools==4.68.0`.
FontTools is used only to prepare assets. The application uses its existing
ReportLab runtime and embeds a subset of the glyphs actually used.

To reproduce the files, obtain the source from the manifest and run the
preparation script. The script checks both the source hash and tool version.

```text
python build_noto_instances.py NotoSansSC-VF.ttf output-directory
```

PDF paragraphs use the original DejaVu fonts when all characters are supported.
A paragraph requiring additional glyphs uses the corresponding regular or bold
Emergency CJK font for those character runs, retaining DejaVu for its supported
characters, with CJK wrapping. Missing glyphs still raise an explicit
error before an output file is written. This establishes character rendering
for the tested Simplified Chinese text. Complex-script shaping and exhaustive
coverage of all Unicode or regional CJK variants require separate evaluation.
