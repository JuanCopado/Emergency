#!/usr/bin/env python3
"""Build deterministic visual briefs from the canonical procedure family Markdown.

This does not generate clinical images. It creates a reviewable queue that an
image-generation stage can consume only after Clinical QA.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC_DIR = ROOT / "modules" / "procedures"
OUT = ROOT / "qa" / "procedure-visual-briefs.json"

HEADER = re.compile(r"^##\s+(PROC-[A-Z]+-\d{3})\s+—\s+(.+?)(?:\s+—\s+([A-Z/]+))?$", re.M)

def parse_cards():
    cards = []
    for path in sorted(PROC_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(HEADER.finditer(text))
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            proc_id, title, level = match.group(1), match.group(2).strip(), match.group(3)
            if "REFERENCIA" in (level or ""):
                continue
            cards.append({
                "procedure_id": proc_id,
                "title": title,
                "level": level or "UNSPECIFIED",
                "family_file": str(path.relative_to(ROOT)),
                "clinical_text": body,
                "required_frames": [
                    "anatomy_orientation",
                    "patient_and_operator_preparation",
                    "sequential_critical_steps",
                    "success_confirmation",
                    "safety_stop_points"
                ],
                "pocus_frame": "POCUS" in (level or "") or "ecogui" in (title.lower() + " " + body.lower()),
                "clinical_qa": "pending",
                "visual_qa": "pending",
                "image_status": "not_generated"
            })
    dedup = {}
    for card in cards:
        dedup[card["procedure_id"]] = card
    return [dedup[k] for k in sorted(dedup)]

def main():
    cards = parse_cards()
    payload = {
        "schema_version": "1.0",
        "count": len(cards),
        "policy": "Text -> evidence review -> Clinical QA -> image generation -> Visual QA",
        "procedures": cards,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(cards)} visual briefs to {OUT}")
    return 0 if len(cards) == 192 else 2

if __name__ == "__main__":
    raise SystemExit(main())
