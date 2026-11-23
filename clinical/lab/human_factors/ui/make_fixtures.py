"""Generates ui/fixtures.json from the AUDITED Python harness over the REAL BYTES of the Layer 7 stimuli (single source of truth).
The lab UI never decides anything: it looks the decision up in this table. Run: python3 make_fixtures.py"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
import bank_r23 as bank  # noqa: E402
import file_probe  # noqa: E402
import layer7_harness as harness  # noqa: E402

OPTIONS = [None, "skin_wound", "ecg", "xray", "pocus", "document"]
TRIALS = [("S1-14", "E1"), ("S2-14", "E1"), ("S1-15", "E2"), ("S2-15", "E2"), ("QA-01", "E2"), ("QA-02", "E2")]
REPLACEMENT = "S1-14.png"      # a valid container used as the 'replace the file' recovery target


def decision(descriptor, code):
    out = harness.run_case("B", descriptor, "es", code)
    texts = {lang: harness.run_case("B", descriptor, lang, code)["message_text"] for lang in harness.LANGUAGES}
    document = out.get("document", {})
    return {"trigger_id": out["trigger_id"], "message_id": out.get("message_id"), "send_allowed": out["send_allowed"],
            "texts": texts if out["trigger_id"] else None, "decision": document.get("decision", "none")}


def build():
    manifest = bank.build_manifest()
    files = {s["stimulus_id"]: s["file"] for s in manifest["stimuli"] if s["file"]}
    files.update({q["stimulus_id"]: q["file"] for q in manifest["qa_technical"]})
    trials = []
    for sid, code in TRIALS:
        path = bank.HERE / "bank" / files[sid]
        by_modality = {}
        for option in OPTIONS:
            descriptor = file_probe.describe(path, "modality_entry", option)
            by_modality["none" if option is None else option] = decision(descriptor, code)
        replacement = {("none" if option is None else option): decision(file_probe.describe(bank.STIMULI_DIR / REPLACEMENT, "modality_entry", option), code)
                       for option in OPTIONS}          # a valid replacement file still needs a declared modality
        probe = file_probe.describe(path, "modality_entry", None)
        trials.append({"stimulus_id": sid, "scenario_code": code, "file": files[sid], "sha256": next((s["sha256"] for s in manifest["stimuli"] if s["stimulus_id"] == sid), None) or next(q["sha256"] for q in manifest["qa_technical"] if q["stimulus_id"] == sid),
                       "container": {"signature_kind": probe["signature_kind"], "container_parse_ok": probe["container_parse_ok"], "extension": probe["declared_extension"]},
                       "initial_modality": None if code == "E1" else "skin_wound", "by_modality": by_modality, "replacement_by_modality": replacement})
    return {"fixtures_version": "ui-fixtures-0.1", "layer7_result_label": "SIMULATED_LAYER7_HARNESS_LAB_ONLY", "layer7_execution_mode": "SIMULATED_LAB_HARNESS_ONLY",
            "source": "layer7_harness.run_case over file_probe.describe of real stimulus bytes", "options": ["none"] + OPTIONS[1:], "trials": trials}


if __name__ == "__main__":
    data = build()
    (HERE / "fixtures.json").write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (HERE / "fixtures.js").write_text("window.__HF_FIXTURES__ = " + json.dumps(data, ensure_ascii=False, sort_keys=True) + ";\n", encoding="utf-8")
    print("fixtures.json written")
