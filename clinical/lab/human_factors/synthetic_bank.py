"""Reproducible SYNTHETIC scenario bank and descriptor bank for the Stage 1 laboratory (no images, no patient data).

Scenarios are opaque codes bound to a deterministic specification string; `stimulus_sha256` is the SHA-256 of that specification,
so a stimulus cannot be swapped without changing the manifest hash. The two banks are disjoint and balanced per modality.
Layer 7 descriptors (arm B) are technical descriptors only, with their expected simulated outcome derived independently.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import human_factors_tools as hf  # noqa: E402

BANK_VERSION = "synthetic-bank-0.1"
PREFIX = {"skin_wound": "SKI", "ecg": "ECG", "xray": "XRA", "pocus": "POC", "document": "DOC"}


def _spec(seed, modality, bank, index):
    return json.dumps({"bank_version": BANK_VERSION, "seed": str(seed), "modality": modality, "bank": bank, "index": index,
                       "synthetic": True}, sort_keys=True, separators=(",", ":"))


def build_manifest(seed="bank", per_modality_per_bank=2, version=None):
    if not isinstance(per_modality_per_bank, int) or isinstance(per_modality_per_bank, bool) or per_modality_per_bank < 1:
        raise ValueError("per_modality_per_bank must be a positive integer")
    scenarios = []
    for modality in hf.MODALITIES:
        for bank in hf.BANK_SETS:
            for index in range(1, per_modality_per_bank + 1):
                spec = _spec(seed, modality, bank, index)
                sha = hashlib.sha256(spec.encode("utf-8")).hexdigest()
                scenarios.append({"scenario_id": f"{PREFIX[modality]}-{bank[-1]}{index}", "intended_modality": modality, "synthetic": True,
                                  "case_code": f"B-{PREFIX[modality]}-{sha[:8]}", "platforms": ["web", "mobile"], "bank_set": bank,
                                  "stimulus_sha256": sha})
    manifest = {"manifest_version": version or f"bank-{hashlib.sha256(str(seed).encode()).hexdigest()[:8]}", "scenarios": scenarios}
    hf.validate_manifest(manifest)
    return manifest


def audit_manifest(manifest):
    """Independent balance and disjointness checks beyond the tool's own validation. Returns a list of problems (empty = OK)."""
    problems = []
    info = hf.validate_manifest(manifest)
    counts = {}
    for sc in manifest["scenarios"]:
        counts.setdefault(sc["intended_modality"], {}).setdefault(sc.get("bank_set"), 0)
        counts[sc["intended_modality"]][sc.get("bank_set")] += 1
    for modality in hf.MODALITIES:
        per = counts.get(modality, {})
        if set(per) != set(hf.BANK_SETS):
            problems.append(f"{modality}: both banks are required")
        elif len(set(per.values())) != 1:
            problems.append(f"{modality}: banks are unbalanced {per}")
    if not info["stimuli_frozen"]:
        problems.append("stimulus hashes are missing")
    return problems


def layer7_descriptors():
    """Closed descriptor bank for arm B: each case has an expected trigger derived by hand from the contract, not from the simulator."""
    def d(flow, declared, kind, sig, ok=True, mime="image/jpeg", ext=".jpg"):
        return {"flow": flow, "modality_declared": declared, "declared_kind": kind, "signature_kind": sig, "container_parse_ok": ok,
                "declared_mime_type": mime, "declared_extension": ext}
    return [
        ("L7-NEG-01", d("modality_entry", True, "skin_wound", "jpeg"), None),
        ("L7-NEG-02", d("modality_entry", True, "ecg", "pdf", mime="application/pdf", ext=".pdf"), None),
        ("L7-NEG-03", d("classic_upload", True, None, "png", mime="image/png", ext=".png"), None),
        ("L7-NEG-04", d("document_legacy_bridge", False, None, "pdf", mime="application/pdf", ext=".pdf"), None),
        ("L7-T01-01", d("modality_entry", False, None, "jpeg"), "T7-01_UNDECLARED_MODALITY"),
        ("L7-T02-01", d("modality_entry", True, "unknown_kind", "jpeg"), "T7-02_UNKNOWN_CONTRACT"),
        ("L7-T03-01", d("modality_entry", True, "skin_wound", "jpeg", ok=False), "T7-03_CORRUPT_UNPROCESSABLE"),
        ("L7-T04-01", d("modality_entry", True, "skin_wound", "pdf", mime="application/pdf", ext=".pdf"), "T7-04_FORMAT_CONTAINER_MISMATCH"),
        ("L7-T04-02", d("modality_entry", True, "skin_wound", "audio", mime="audio/mpeg", ext=".mp3"), "T7-04_FORMAT_CONTAINER_MISMATCH"),
        ("L7-PRO-01", d("classic_upload", False, None, "jpeg"), None),
        ("L7-PRO-02", d("document_legacy_bridge", False, None, "jpeg"), None),
    ]


def fingerprint(manifest, descriptors):
    return {"manifest_sha256": hf.digest(manifest), "descriptors_sha256": hf.digest([[i, d, e] for i, d, e in descriptors]),
            "bank_version": BANK_VERSION}


def synthetic_session(manifest, participants=12, seed="session"):
    """Complete synthetic dataset for pipeline tests (AB/BA balanced, banks counterbalanced). It simulates NOTHING about people."""
    codes = [f"SYN-{i:03d}" for i in range(1, participants + 1)]
    allocation = hf.assign_sequences(codes, seed)["allocation"]
    rng = random.Random(f"{seed}:syn")
    by_bank = {b: [s for s in manifest["scenarios"] if s["bank_set"] == b] for b in hf.BANK_SETS}
    rows = []
    for index, code in enumerate(codes):
        slot = allocation[code]
        banks = ("set1", "set2") if index % 2 == 0 else ("set2", "set1")
        for period, (condition, bank) in enumerate(((slot["period1"], banks[0]), (slot["period2"], banks[1])), start=1):
            for order, sc in enumerate(by_bank[bank], start=1):
                intended = sc["intended_modality"]
                err = condition == "baseline" and rng.random() < 0.2
                chosen = intended if not err else rng.choice([m for m in hf.MODALITIES if m != intended])
                rows.append({"participant": code, "role": "physician", "scenario_id": sc["scenario_id"], "condition": condition,
                             "period": period, "intended_modality": intended, "initial_modality": chosen, "chosen_modality": chosen,
                             "confirmed": True, "changed_modality_count": 0, "seconds": round(5 + rng.random() * 5, 2),
                             "comprehension_correct": rng.random() < 0.9, "platform": "web" if (index // 2) % 2 == 0 else "mobile",
                             "order_in_period": order})
    return rows
