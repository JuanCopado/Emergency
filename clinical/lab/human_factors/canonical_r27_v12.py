"""canonical-r27-v1.2 · explicit successor of canonical-r27-v1.1 (laboratory only).

canonical-r27-v1 and canonical-r27-v1.1 stay untouched (their validators are reused, never edited in behaviour). v1.2 keeps the 39 fields of
v1.1 and adds `payload_sha256` and `expected_modality` (Antigravity R33 proposal; the reduced 22-field Gemini R32 schema is NOT applied: see
R34_CLAUDE_CROSSWALK_FINAL.md). Nothing is coerced; every violation raises CanonicalViolation (HARD FAIL).

Integrity
  * stimulus_hash_sha256 must equal the SHA-256 in the stimulus manifest AND, when the file is present, the SHA-256 of the real bytes.
    A manifest entry without a hash (bank not generated / not frozen) makes the record un-exportable.
  * payload_sha256 = SHA-256 of the canonical UTF-8 JSON of the record without payload_sha256 (sorted keys, no spaces, no NaN).
Ground truth
  * expected_modality comes from the manifest (`true_modality`); the harness cannot supply it.
Provenance vocabulary (Gemini R32, as relayed by the owner; the Gemini file itself was NOT available to this implementation)
  * SYNTHETIC_FIXTURE, SYNTHETIC_LAB_HARNESS, TECHNICAL_DRY_RUN, STAGE1_HUMAN_PILOT. STAGE1_HUMAN_PILOT is refused while STAGE1_AUTHORIZED is False.
  * The v1.1 value HUMAN_PARTICIPANT is not part of this vocabulary and is never migrated automatically."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import canonical_r27_v1 as c1  # noqa: E402
from canonical_r27_v1 import CanonicalViolation, _need  # noqa: E402

SCHEMA_VERSION_V12 = "canonical-r27-v1.2"
V12_ADDED = {"payload_sha256", "expected_modality"}
FIELDS_V12 = c1.FIELDS | c1.V11_ADDED | V12_ADDED
PROVENANCE_V12 = ("SYNTHETIC_FIXTURE", "SYNTHETIC_LAB_HARNESS", "TECHNICAL_DRY_RUN", "STAGE1_HUMAN_PILOT")
STAGE1_AUTHORIZED = False            # institutional + medical authorization for Stage 1 does not exist: never flip this in code
HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "bank" / "stimuli_manifest.json"
DEFAULT_STIMULI = HERE / "bank" / "stimuli"


def load_manifest(path=DEFAULT_MANIFEST):
    data = json.loads(Path(path).read_text(encoding="utf8"))
    return {entry["stimulus_id"]: entry for entry in data["stimuli"]}


def canonical_bytes(record):
    """Deterministic UTF-8 serialization of the record without its own hash."""
    body = {k: v for k, v in record.items() if k != "payload_sha256"}
    try:
        return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise CanonicalViolation(f"record is not canonically serializable: {error}") from error


def payload_hash(record):
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def seal(record):
    """Return a copy of a record (without payload_sha256) carrying the correct hash."""
    sealed = dict(record)
    sealed["payload_sha256"] = payload_hash(sealed)
    return sealed


def _check_provenance(value):
    _need(value in PROVENANCE_V12, "data_provenance is not in the canonical-r27-v1.2 vocabulary (HUMAN_PARTICIPANT is never accepted)")
    _need(value != "STAGE1_HUMAN_PILOT" or STAGE1_AUTHORIZED, "STAGE1_HUMAN_PILOT is refused: no institutional and medical authorization for Stage 1")


def verified_stimulus(stimulus_id, manifest, stimuli_dir=DEFAULT_STIMULI):
    """Manifest entry whose hash is checked against the real bytes. Raises when the entry has no hash or the bytes disagree."""
    entry = manifest.get(stimulus_id)
    _need(entry is not None, "stimulus is not in the manifest")
    declared = entry.get("sha256")
    _need(isinstance(declared, str) and c1.SHA256.match(declared), "manifest has no verified hash for this stimulus (bank not generated or not frozen)")
    file_name = entry.get("file")
    _need(file_name, "manifest has a hash but no file for this stimulus")
    path = Path(stimuli_dir) / Path(file_name).name
    _need(path.is_file(), "stimulus file is missing: the hash cannot be verified against real bytes")
    _need(hashlib.sha256(path.read_bytes()).hexdigest() == declared, "stimulus bytes do not match the manifest hash")
    return entry


def validate_record_v12(r, manifest=None, stimuli_dir=DEFAULT_STIMULI):
    manifest = load_manifest() if manifest is None else manifest
    _need(isinstance(r, dict) and set(r) == FIELDS_V12, "closed record: fields must be exactly canonical-r27-v1.2")
    _need(r["schema_version"] == SCHEMA_VERSION_V12, "schema_version must be canonical-r27-v1.2")
    _check_provenance(r["data_provenance"])
    projection = {k: v for k, v in r.items() if k not in V12_ADDED}
    projection["schema_version"] = c1.SCHEMA_VERSION_V11
    c1.validate_record_v11(projection, provenance_vocab=PROVENANCE_V12)                    # every v1.1 rule (and through it every v1 rule)
    entry = verified_stimulus(r["stimulus_id"], manifest, stimuli_dir)
    _need(r["stimulus_hash_sha256"] == entry["sha256"], "stimulus_hash_sha256 does not match the manifest")
    truth = entry.get("true_modality")
    _need(r["expected_modality"] == truth, "expected_modality must equal the manifest true_modality (the harness cannot supply it)")
    _need(truth is None or truth in c1.MODALITY, "manifest true_modality is outside the closed vocabulary")
    _need(isinstance(r["payload_sha256"], str) and c1.SHA256.match(r["payload_sha256"]) and r["payload_sha256"] == payload_hash(r),
          "payload_sha256 does not match the record (modified after sealing, absent or false)")
    if r["mechanism_id"] == c1.MECHANISM["M1"]:                                              # conditional rules that need the ground truth
        _need(truth is not None, "M1 needs a manifest ground truth")
        declared = r["declared_modality"]
        if r["outcome_status"] == "bypass_residual":
            _need(declared != truth, "bypass_residual requires a submitted modality different from the expected one")
        elif r["outcome_status"] in ("detected_before_submit", "valid_completed"):
            _need(declared == truth, "this M1 outcome requires the submitted modality to equal the expected one")
    return r


def from_v11(record, manifest=None, stimuli_dir=DEFAULT_STIMULI):
    """Deterministic v1.1 -> v1.2 migration. Provenance HUMAN_PARTICIPANT is ambiguous and is refused, never aliased."""
    manifest = load_manifest() if manifest is None else manifest
    c1.validate_record_v11(record)
    _need(record["data_provenance"] != "HUMAN_PARTICIPANT", "HUMAN_PARTICIPANT cannot be migrated: provenance must be re-established by the study")
    entry = verified_stimulus(record["stimulus_id"], manifest, stimuli_dir)
    out = {k: v for k, v in record.items()}
    out["schema_version"] = SCHEMA_VERSION_V12
    out["expected_modality"] = entry.get("true_modality")
    return validate_record_v12(seal(out), manifest, stimuli_dir)


UI_LANGUAGE_OF = {"ES": "es", "EN": "en", "pt-PT": "pt", "pt-BR": "pt"}


def _check_locale_evidence(log, stratum):
    """The language stratum must be proven by the UI (locale_resolved), never taken from the harness alone. Generic pt is never upgraded."""
    _need(stratum in UI_LANGUAGE_OF, "language_stratum (generic 'pt' is refused)")
    events = [e for e in log if isinstance(e, dict) and e.get("type") == "locale_resolved"]
    _need(events, "the UI log has no locale_resolved event: the language of the trial is not proven")
    detail = events[-1].get("detail", {})
    _need(detail.get("status") == "OK", "the UI refused this locale (no approved texts)")
    _need(detail.get("language") == UI_LANGUAGE_OF[stratum], "UI language disagrees with language_stratum")
    if stratum.startswith("pt"):
        _need(detail.get("variant") == stratum, "regional Portuguese must be selected explicitly in the UI (lab_locale); generic pt is not upgraded")
    else:
        _need(detail.get("variant") is None, "a non-Portuguese stratum cannot carry a regional variant")


def from_lab_ui_log_v12(log, context, manifest=None, stimuli_dir=DEFAULT_STIMULI):
    """React UI events + harness context -> sealed v1.2 record. The harness may NOT pass expected_modality: it is read from the manifest."""
    manifest = load_manifest() if manifest is None else manifest
    _need(isinstance(context, dict), "context is required")
    _need("expected_modality" not in context, "expected_modality is manifest-only: the harness cannot supply the ground truth")
    _need("data_provenance" in context, "harness context missing: ['data_provenance']")
    _check_provenance(context["data_provenance"])
    entry = verified_stimulus(str(context.get("stimulus_id")), manifest, stimuli_dir)
    _need(context.get("stimulus_hash_sha256") == entry["sha256"], "stimulus_hash_sha256 does not match the manifest")
    _check_locale_evidence(log, context.get("language_stratum"))
    inner = dict(context)
    inner["data_provenance"] = "SYNTHETIC_LAB_HARNESS"                                    # v1.1 pass only; the real value is restored below
    if entry.get("true_modality") is not None:
        inner["expected_modality"] = entry["true_modality"]
    record = c1.from_lab_ui_log(log, inner)
    record["schema_version"] = SCHEMA_VERSION_V12
    record["data_provenance"] = context["data_provenance"]
    record["expected_modality"] = entry.get("true_modality")
    return validate_record_v12(seal(record), manifest, stimuli_dir)
