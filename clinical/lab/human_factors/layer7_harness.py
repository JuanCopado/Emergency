"""Stage 1 arm-B HARNESS for Layer 7 (DEC-CLIN-R22-01, alternative B). LABORATORY ONLY, never imported by the product.

Wraps the deterministic simulator: arm A (current interface) never shows Layer 7; arm B shows the approved abstention (exact DEC-CLIN-R15-01
texts) when a closed technical trigger fires. Every output is labelled SIMULATED_LAYER7_HARNESS_LAB_ONLY. It adds no rules: decisions come
from layer7_simulator.evaluate. Texts come from the inactive contract and the approved pt-BR lab catalog. The harness has no network access.
Using it with people requires the independent audit of the exact commit (Antigravity) and the ethical/institutional prerequisites.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layer7_simulator as sim  # noqa: E402

LABEL = "SIMULATED_LAYER7_HARNESS_LAB_ONLY"
ARMS = ("A", "B")
LANGUAGES = ("es", "pt", "en")
VARIANTS = ("pt-PT", "pt-BR")                  # regional Portuguese: explicit, lab only; generic pt carries variant None and is never upgraded
_PTBR = json.loads((Path(__file__).resolve().parent / "layer7_ptbr_texts.json").read_text(encoding="utf-8"))
PTBR_TEXTS = _PTBR["message-texts"]            # approved 24/11/2026 (MED-DEC-R39-PTBR-FINAL); the historical contract is not modified
# Scenario classes of the Stage 1 protocol -> analysis stratum (kept separate in the analysis) and the independently stated expectation.
SCENARIO_CLASSES = {
    "A": ("non_interference", None),          # valid skin/wound photographs (R23 mechanism M3 together with F)
    "B": ("selector_bypass", None),
    "C": ("selector_bypass", None),
    "D": ("selector_bypass", None),
    "E1": ("layer7_comprehension", "T7-01_UNDECLARED_MODALITY"),
    "E2": ("layer7_comprehension", ("T7-03_CORRUPT_UNPROCESSABLE", "T7-04_FORMAT_CONTAINER_MISMATCH")),
    "F": ("non_interference", None),
}


def stratum(scenario_class):
    if scenario_class not in SCENARIO_CLASSES:
        raise ValueError("unknown scenario class")
    return SCENARIO_CLASSES[scenario_class][0]


def expected_trigger(scenario_class):
    if scenario_class not in SCENARIO_CLASSES:
        raise ValueError("unknown scenario class")
    return SCENARIO_CLASSES[scenario_class][1]


def run_case(arm, descriptor, language, scenario_class=None, variant=None):
    if arm not in ARMS:
        raise ValueError("arm must be A or B")
    if language not in LANGUAGES:
        raise ValueError("language must be es, pt or en (no other language has an approved text)")
    if variant is not None and (variant not in VARIANTS or language != "pt"):
        raise ValueError("a regional variant needs language pt and must be pt-PT or pt-BR")
    sim.validate_descriptor(descriptor)           # closed fields only: no pixel, EXIF, file-name or model evidence can enter
    out = {"label": LABEL, "arm": arm, "language": language, "scenario_class": scenario_class,
           "stratum": stratum(scenario_class) if scenario_class else None}
    if arm == "A":
        out.update(layer7_shown=False, trigger_id=None, message_text=None, send_allowed=True)
        return out
    result = sim.evaluate(descriptor)
    document = result["document"]
    abstains = document["decision"] == "abstain"
    text = None
    if abstains:
        text = PTBR_TEXTS[document["message_id"]] if variant == "pt-BR" else result["message_texts"][language]
    out.update(layer7_shown=abstains, trigger_id=document.get("trigger_id"), message_id=document.get("message_id"),
               message_text=text,
               send_allowed=document.get("send_allowed", True) if abstains else True, document=document)
    return out


def conforms(case_result):
    """True when an arm-B result matches the protocol expectation of its scenario class (E1/E2 trigger; B/C/D/F no Layer 7)."""
    scenario_class = case_result["scenario_class"]
    if scenario_class is None or case_result["arm"] != "B":
        raise ValueError("conformance needs an arm-B result with a scenario class")
    expected = expected_trigger(scenario_class)
    if expected is None:
        return not case_result["layer7_shown"] and case_result["trigger_id"] is None
    allowed = (expected,) if isinstance(expected, str) else expected
    return case_result["trigger_id"] in allowed
