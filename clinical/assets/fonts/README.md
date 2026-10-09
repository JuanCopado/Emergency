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
bundled font raise an explicit error before writing output; there is no ASCII
fallback or silent substitution. Complex-script shaping is not validated here.
