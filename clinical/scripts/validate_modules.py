#!/usr/bin/env python3
"""Validate that every module manifest entry resolves to a real bundle section."""

import re
import sys
from collections import Counter
from pathlib import Path


ROW = re.compile(r"^\| ([a-z0-9-]+) \| `([^`]+)` \|$", re.MULTILINE)
HEADING = re.compile(r"^## ([a-z0-9-]+)$", re.MULTILINE)


def _contains_exact_module(line: str, module_id: str) -> bool:
    return bool(
        re.search(
            rf"(?<![a-z0-9-]){re.escape(module_id)}(?![a-z0-9-])",
            line,
        )
    )


def validate(root: Path):
    index = (root / "references/module-index.md").read_text(encoding="utf-8")
    rows = ROW.findall(index)
    errors = []

    if not rows:
        errors.append("module manifest has no entries")

    id_counts = Counter(module_id for module_id, _ in rows)
    duplicate_ids = sorted(module_id for module_id, count in id_counts.items() if count > 1)
    if duplicate_ids:
        errors.append(f"duplicate module IDs in manifest: {', '.join(duplicate_ids)}")

    manifest = dict(rows)

    for module_id, relative_path in manifest.items():
        target = root / relative_path
        if not target.is_file():
            errors.append(f"{module_id}: missing bundle {relative_path}")
            continue
        headings = HEADING.findall(target.read_text(encoding="utf-8"))
        heading_count = headings.count(module_id)
        if heading_count == 0:
            errors.append(f"{module_id}: missing '## {module_id}' in {relative_path}")
        elif heading_count > 1:
            errors.append(
                f"{module_id}: duplicate '## {module_id}' sections in {relative_path}"
            )

    router = (root / "references/router.md").read_text(encoding="utf-8")
    route_lines = [line for line in router.splitlines() if "->" in line]
    for line in route_lines:
        rhs = line.split("->", 1)[1]
        if not any(_contains_exact_module(rhs, module_id) for module_id in manifest):
            errors.append(f"route resolves to no known module: {line.strip()}")

    bundle_sections = {}
    for bundle in (root / "modules").glob("*.md"):
        for module_id in HEADING.findall(bundle.read_text(encoding="utf-8")):
            bundle_sections.setdefault(module_id, []).append(bundle.name)
    for module_id, bundles in bundle_sections.items():
        if module_id not in manifest:
            errors.append(f"unindexed section {module_id}: {', '.join(bundles)}")
        if len(bundles) > 1:
            errors.append(f"duplicate section {module_id}: {', '.join(bundles)}")

    return manifest, errors


if __name__ == "__main__":
    skill_root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parents[1])
    modules, problems = validate(skill_root)
    if problems:
        print("MODULE VALIDATION FAILED")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print(f"MODULE VALIDATION PASSED: {len(modules)} modules resolved")
