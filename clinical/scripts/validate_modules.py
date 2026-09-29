#!/usr/bin/env python3
"""Validate that every module manifest entry resolves to a real bundle section."""

import re
import sys
from pathlib import Path


ROW = re.compile(r"^\| ([a-z0-9-]+) \| `([^`]+)` \|$", re.MULTILINE)
HEADING = re.compile(r"^## ([a-z0-9-]+)$", re.MULTILINE)


def validate(root: Path):
    index = (root / "references/module-index.md").read_text(encoding="utf-8")
    manifest = dict(ROW.findall(index))
    errors = []

    if not manifest:
        errors.append("module manifest has no entries")

    seen_sections = set()
    for module_id, relative_path in manifest.items():
        target = root / relative_path
        if not target.is_file():
            errors.append(f"{module_id}: missing bundle {relative_path}")
            continue
        headings = set(HEADING.findall(target.read_text(encoding="utf-8")))
        if module_id not in headings:
            errors.append(f"{module_id}: missing '## {module_id}' in {relative_path}")
        key = (relative_path, module_id)
        if key in seen_sections:
            errors.append(f"{module_id}: duplicate manifest mapping")
        seen_sections.add(key)

    router = (root / "references/router.md").read_text(encoding="utf-8")
    route_lines = [line for line in router.splitlines() if "->" in line]
    for line in route_lines:
        if not any(module_id in line for module_id in manifest):
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
