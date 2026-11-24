"""External-tool audit of the generated stimuli (R25 Gemini criterion 1). LABORATORY ONLY.

Runs `pdfinfo` and `exiftool` when they exist and records what was (not) run; nothing is assumed. Writes bank/external_audit_report.json.
This is NOT a PHI review and NOT a visual inspection: both stay PENDING in the manifest.
"""
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "bank" / "stimuli_manifest.json").read_text(encoding="utf-8"))
REPORT = HERE / "bank" / "external_audit_report.json"
GENERIC_PDF_PRODUCER = "ReportLab PDF Library - (opensource)"
IDENTIFYING = ("author", "creator", "producer", "title", "subject", "keywords")


def run(tool, path):
    done = subprocess.run([tool, str(path)], capture_output=True, text=True, timeout=30, check=False)
    return done.stdout


def pdfinfo_fields(text):
    return {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in text.splitlines() if ":" in line}


def main():
    tools = {name: shutil.which(name) for name in ("pdfinfo", "exiftool")}
    files = []
    for entry in list(MANIFEST["stimuli"]) + list(MANIFEST["qa_technical"]):
        if not entry.get("file"):
            continue
        path = HERE / "bank" / entry["file"]
        row = {"stimulus_id": entry["stimulus_id"], "file": entry["file"], "exiftool": "NOT_RUN_TOOL_UNAVAILABLE", "pdfinfo": "NOT_APPLICABLE"}
        if tools["exiftool"]:
            row["exiftool"] = run("exiftool", path)[:2000]
        if path.suffix == ".pdf":
            if tools["pdfinfo"]:
                fields = pdfinfo_fields(run("pdfinfo", path))
                producer = fields.get("Producer")
                if producer == GENERIC_PDF_PRODUCER:
                    del fields["Producer"]
                    row["generic_pdf_producer"] = producer
                row["pdfinfo"] = {"identifying_fields_with_value": sorted(k for k, v in fields.items() if k.lower() in IDENTIFYING and v),
                                  "pages": fields.get("Pages")}
            else:
                row["pdfinfo"] = "NOT_RUN_TOOL_UNAVAILABLE"
        files.append(row)
    REPORT.write_text(json.dumps({"tools_found": {k: bool(v) for k, v in tools.items()}, "files": files,
                                  "scope": "container metadata only; not a PHI review; visual review remains PENDING"},
                                 ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: bool(v) for k, v in tools.items()}), len(files))


if __name__ == "__main__":
    main()
