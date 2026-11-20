"""Bridge to canonical metrics, with bank linkage and human safety adjudication."""
from datetime import datetime
import hashlib
import json
import re

from calculate_blinded_image_metrics import calculate
from .bank import validate_bank, blinded_inputs, _id
from .intake import local_path
from .json_io import loads_object


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp_required')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timezone_required')
    return parsed


def _verify_freeze(dataset, root, inputs, anchor):
    if not isinstance(anchor, str) or not re.fullmatch('[0-9a-f]{64}', anchor):
        raise ValueError('external_freeze_anchor_required')
    path = local_path(root, dataset.get('freeze_receipt_file'))
    with path.open('rb') as stream:
        raw = stream.read(8 * 1024 * 1024 + 1)
    if len(raw) > 8 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != anchor:
        raise ValueError('frozen_receipt_digest_mismatch')
    receipt = loads_object(raw)
    if not isinstance(receipt, dict) or receipt.get('schema_version') != '1.0':
        raise ValueError('invalid_frozen_receipt')
    digest = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if receipt.get('inputs_sha256') != digest or receipt.get('run') != dataset['run']:
        raise ValueError('frozen_inputs_or_run_changed')
    predictions = [{k: c[k] for k in ('id', 'prediction')} for c in dataset['cases']]
    if receipt.get('predictions') != predictions:
        raise ValueError('frozen_predictions_changed')
    frozen = _timestamp(receipt.get('frozen_at'))
    if any(_timestamp(c['evaluation']['prediction_frozen_at']) != frozen for c in dataset['cases']):
        raise ValueError('freeze_timestamp_changed')
    protocol = local_path(root, receipt.get('protocol_file'))
    with protocol.open('rb') as stream:
        raw_protocol = stream.read(8 * 1024 * 1024 + 1)
    if len(raw_protocol) > 8 * 1024 * 1024 or hashlib.sha256(raw_protocol).hexdigest() != dataset['run']['protocol_sha256']:
        raise ValueError('frozen_protocol_changed')


def evaluate(bank, dataset, root, *, freeze_sha256=None):
    errors = list(validate_bank(bank)['errors'])
    result = dict(errors=errors, metrics=None, critical_errors=None,
                  clinical_release_status='CLINICALLY_PENDING', diagnostic_validation=False)
    if errors:
        return result
    if not isinstance(dataset, dict) or dataset.get('dataset_class') not in {'blinded_accuracy', 'prospective_validation'}:
        errors.append('real_blinded_dataset_required')
        return result
    rows = {r['id']: r for r in bank['cases'] if r['split'] == 'blind_test'}
    if not rows:
        errors.append('no_valid_real_blind_cases')
        return result
    try:
        inputs = blinded_inputs(bank, root)
    except ValueError:
        errors.append('blind_inputs_not_admissible')
        return result
    run = dataset.get('run')
    if not isinstance(run, dict) or any(not _id(run.get(key)) for key in
            ('model_version', 'prompt_version', 'preprocessing_version', 'rubric_id')):
        errors.append('frozen_run_versions_required')
        return result
    if not isinstance(run.get('protocol_sha256'), str) or not re.fullmatch('[0-9a-f]{64}', run['protocol_sha256']):
        errors.append('protocol_digest_required')
    cases = dataset.get('cases')
    if not isinstance(cases, list) or not cases or any(not isinstance(c, dict) or not _id(c.get('id')) for c in cases):
        errors.append('valid_evaluation_cases_required')
        return result
    if len({c['id'] for c in cases}) != len(cases) or {c['id'] for c in cases} != set(rows):
        errors.append('evaluation_must_cover_exact_blind_partition')
        return result
    # This initial bridge requires one patient per task; no naive binomial CI
    # for clustered multiple studies. Existing grouped evaluator is preserved.
    if len({r['patient_group_id'] for r in rows.values()}) != len(rows):
        errors.append('independent_patient_unit_required_for_this_bridge')
    task_ids = {r['task_id'] for r in rows.values()}
    if len(task_ids) != 1 or any('video' in t for t in task_ids):
        errors.append('single_static_task_required_temporal_evaluation_not_validated')
    critical = 0
    for case in cases:
        row = rows[case['id']]
        if (case.get('patient_uid_hash') != row['patient_group_id'] or
                case.get('study_uid_hash') != row['study_group_id'] or
                row['modality'] != dataset.get('modality')):
            errors.append('case_identity_or_modality_mismatch')
        ref, pred, ev, safety = (case.get(k) for k in ('reference', 'prediction', 'evaluation', 'safety'))
        if (not isinstance(ref, dict) or type(ref.get('target_positive')) is not bool
                or not _id(ref.get('source_id')) or not _id(ref.get('reviewer_id'))):
            errors.append('independent_human_reference_required')
        if not isinstance(pred, dict) or pred.get('class') not in ('positive', 'negative', 'abstain', 'nondiagnostic'):
            errors.append('explicit_prediction_class_required')
        if (not isinstance(safety, dict) or safety.get('reviewed') is not True
                or not _id(safety.get('reviewer_id')) or type(safety.get('critical_error')) is not bool
                or safety.get('rubric_id') != run['rubric_id']):
            errors.append('all_case_critical_error_adjudication_required')
        else:
            critical += int(safety['critical_error'])
        try:
            if not isinstance(ev, dict) or not isinstance(pred, dict):
                raise ValueError('evaluation_required')
            stamp = _timestamp(pred.get('timestamp'))
            frozen = _timestamp(ev.get('prediction_frozen_at'))
            revealed = _timestamp(ev.get('reference_revealed_at'))
            if not stamp <= frozen < revealed:
                errors.append('prediction_freeze_reveal_order_invalid')
        except (TypeError, ValueError):
            errors.append('valid_timezone_aware_timestamps_required')
    # Request strict positive/negative denominator checks even if a caller
    # attempts to disable metrics_requested in the old dataset format.
    if errors:
        return result
    try:
        _verify_freeze(dataset, root, inputs, freeze_sha256)
    except Exception:
        errors.append('freeze_receipt_or_external_anchor_not_verified')
        return result
    canonical = calculate({**dataset, 'metrics_requested': True})
    if canonical['errors']:
        errors.extend(canonical['errors'])
        return result
    result['metrics'] = canonical['metrics']
    result['critical_errors'] = dict(count=critical, adjudicated_cases=len(cases),
                                     rate=critical / len(cases), rubric_id=run['rubric_id'])
    result['scope'] = 'Retrospective dataset calculation only; not clinical validation or generalizable accuracy.'
    result['freeze_anchor_scope'] = 'Receipt bytes match caller-supplied SHA256; external custody must establish prereveal anchoring.'
    return result
