"""Prepare review dossiers from manifest rows and physical bytes; never adjudicate.

Laboratory only. No clinical output, model invocation, patient data or network.
R50 §7 controls applicability. R56 slot numbers never assign actual IDs.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = HERE / 'bank'
SCENARIO_MECHANISM = {'A': 'M3', 'B': 'M1', 'C': 'M1', 'D': 'M1', 'E1': 'M2', 'E2': 'M2', 'F': 'M3'}


def build_dossiers(manifest, bank_dir):
    """Return unsigned dossiers, preserving real IDs; raise on inconsistent linkage."""
    bank_dir = Path(bank_dir).resolve()
    rows = manifest['stimuli']
    if len(rows) != 30 or len({r['stimulus_id'] for r in rows}) != 30:
        raise ValueError('exactly 30 distinct manifest IDs required')
    if {r['set_id'] for r in rows} != {1, 2}:
        raise ValueError('sets 1 and 2 required')
    for set_id in (1, 2):
        if Counter(r['mechanism_id'] for r in rows if r['set_id'] == set_id) != {'M1': 4, 'M2': 2, 'M3': 9}:
            raise ValueError('each set must preserve 4 M1 / 2 M2 / 9 M3')
    result = []
    for row in rows:
        mechanism = row['mechanism_id']
        if SCENARIO_MECHANISM.get(row['scenario_code']) != mechanism:
            raise ValueError('scenario and mechanism disagree')
        file = row['file']
        sha = None
        if file:
            path = (bank_dir / file).resolve()
            if not path.is_relative_to(bank_dir / 'stimuli') or not path.is_file():
                raise ValueError('physical stimulus missing or outside bank/stimuli')
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            if sha != row['sha256'] or len(data) != row['bytes']:
                raise ValueError('physical bytes do not match manifest')
        elif row.get('sha256') is not None or row.get('bytes') is not None or row['generation_status'] != 'PENDING_STIMULUS_GENERATION':
            raise ValueError('absent stimulus cannot have a hash or generated status')
        # Existing M1 scenarios have no explicit diagnostic target/red-flag objective.
        # Do not infer one from morphology in spec_text; a new explicit target needs review.
        needs_diagnosis = (mechanism == 'M3' and row['true_modality'] != 'document') or (
            mechanism == 'M1' and bool(row.get('diagnostic_target') or row.get('explicit_clinical_red_flag')))
        clinical = 'PENDING_CLINICAL_ADJUDICATION' if needs_diagnosis else 'N/A'
        if mechanism == 'M1':
            behavior = 'SELECTOR_BYPASS_REVIEW_NOT_CONTENT_CLASSIFICATION; preserve manifest trigger; no automatic clinical-modality detection'
        elif mechanism == 'M2':
            behavior = 'TECHNICAL_ABSTENTION_ARM_B_ONLY; no clinical evaluation; verify manifest trigger from objective container/selection evidence'
        else:
            behavior = 'VALID_NON_INTERFERENCE; clinical support only, no autonomous exclusion of urgent pathology'
        result.append({
            'stimulus_id': row['stimulus_id'], 'set_id': row['set_id'], 'pair_id': row['pair_id'],
            'mechanism_id': mechanism, 'scenario_code': row['scenario_code'],
            'file': file, 'stimulus_hash_sha256': sha, 'bytes': row['bytes'],
            'physical_status': 'VERIFIED_BYTES' if file else 'PENDING_STIMULUS_GENERATION',
            'clinical_domain': row['true_modality'] or 'N/A', 'expected_modality': row['true_modality'] or 'N/A',
            'route_modality': row['route_modality'], 'expected_layer7_trigger': row['expected_layer7_trigger'],
            'spec_text': row['spec_text'], 'source': row['origin_type'], 'license': row['license_ref'],
            'clinical_ground_truth': clinical, 'red_flags': clinical, 'independent_reference': clinical,
            'diagnostic_applicability': 'REQUIRED' if needs_diagnosis else 'N/A',
            'technical_integrity_review': 'PENDING', 'expected_system_behavior': behavior,
            'metadata_scan_status': row['phi_audit_status'], 'pixel_privacy_review': 'PENDING',
            'age_group': 'PENDING' if needs_diagnosis else 'N/A',
            'fitzpatrick_phototype': 'PENDING' if row['true_modality'] == 'skin_wound' else 'N/A',
            'mst_band_specification': row['mst_band'],
            'subgroup_note': 'MST specification is not an adjudicated Fitzpatrick phototype; never infer age or phototype from pixels.',
            'review_controls': row['review_controls'], 'generation_impediment': row['generation_impediment'],
            'reviewer_1': 'PENDING', 'reviewer_2': 'PENDING', 'third_adjudicator_if_disagreement': 'PENDING',
            'owner_decision': 'PENDING', 'signature_date': 'PENDING',
            'clinical_adjudication_status': row['clinical_adjudication_status'],
            'release_status': 'NO_GO_CLINICAL_RELEASE', 'clinical_status': 'CLINICALLY_PENDING',
        })
    return result


if __name__ == '__main__':
    manifest_path = BANK / 'stimuli_manifest.json'
    rows = build_dossiers(json.loads(manifest_path.read_text(encoding='utf-8')), BANK)
    print(json.dumps({'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                      'dossiers': rows}, ensure_ascii=False, indent=2))
