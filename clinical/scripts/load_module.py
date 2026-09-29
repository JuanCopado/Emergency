#!/usr/bin/env python3
"""Print one or more module sections resolved through the module manifest."""

import argparse
import re
from pathlib import Path


ROW = re.compile(r"^\| ([a-z0-9-]+) \| `([^`]+)` \|$", re.MULTILINE)


def manifest(root: Path):
    text = (root / "references/module-index.md").read_text(encoding="utf-8")
    return dict(ROW.findall(text))


def load(root: Path, module_id: str):
    mapping = manifest(root)
    if module_id not in mapping:
        raise KeyError(f"unknown module: {module_id}")
    source = root / mapping[module_id]
    text = source.read_text(encoding="utf-8")
    match = re.search(
        rf"^## {re.escape(module_id)}\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise RuntimeError(f"module section missing: {module_id} in {source}")
    # Shared bundle instructions apply to every section, even when loaded alone.
    preamble = re.split(r"^## ", text, maxsplit=1, flags=re.MULTILINE)[0].strip()
    return f"{preamble}\n\n## {module_id}\n{match.group('body').rstrip()}\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("module_ids", nargs="+")
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args()
    for position, module_id in enumerate(args.module_ids):
        if position:
            print()
        print(load(args.root, module_id), end="")
