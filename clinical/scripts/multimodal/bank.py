"""Private case catalog and allowlisted blind projection; no label exports."""
import re
from pathlib import PurePosixPath

from .adapters import TASKS, build_input, context_valid
from .intake import inspect_media

SPLITS = {'teaching', 'development', 'blind_test'}
ID = re.compile(r'[a-z0-9][a-z0-9-]{0,63}\Z')
DIGEST = re.compile(r'[0-9a-f]{64}\Z')


def _id(value):
    return isinstance(value, str) and bool(ID.fullmatch(value))


def validate_bank(bank):
    errors = []
    if not isinstance(bank, dict) or bank.get('schema_version') != '1.0':
        return dict(errors=['invalid_bank_schema'], clinical_release_status='CLINICALLY_PENDING')
    cases = bank.get('cases')
    if not isinstance(cases, list) or not cases or len(cases) > 10000:
        return dict(errors=['nonempty_bounded_cases_required'], clinical_release_status='CLINICALLY_PENDING')
    ids, asset_ids, groups, digests, assets_by_hash, parents = set(), set(), {}, set(), {}, []
    for index, row in enumerate(cases):
        prefix = f'case_index_{index}'  # Never interpolate untrusted text in errors.
        if not isinstance(row, dict):
            errors.append(prefix + ':invalid_case')
            continue
        for key in ('id', 'patient_group_id', 'study_group_id', 'source_group_id'):
            if not _id(row.get(key)):
                errors.append(prefix + ':invalid_' + key)
        cid = row.get('id')
        if _id(cid):
            if cid in ids:
                errors.append(prefix + ':duplicate_case')
            ids.add(cid)
        split = row.get('split')
        if not isinstance(split, str) or split not in SPLITS:
            errors.append(prefix + ':invalid_split')
            split = 'invalid'
        kind = row.get('data_kind')
        if kind not in ('synthetic', 'authorized_deidentified'):
            errors.append(prefix + ':invalid_data_kind')
        if type(row.get('source_known')) is not bool or type(row.get('annotated')) is not bool:
            errors.append(prefix + ':explicit_source_and_annotation_flags_required')
        if split == 'blind_test' and (kind != 'authorized_deidentified' or
                row.get('source_known') is not False or row.get('annotated') is not False):
            errors.append(prefix + ':blind_test_contamination')
        if split == 'blind_test' and (not isinstance(cid, str) or not re.fullmatch(r'case-[0-9]{3,12}', cid)):
            errors.append(prefix + ':neutral_blind_case_id_required')
        task = row.get('task_id')
        if not isinstance(task, str) or task not in TASKS or TASKS[task][0] != row.get('modality'):
            errors.append(prefix + ':invalid_task_modality')
        if not context_valid(row.get('context', {})):
            errors.append(prefix + ':invalid_context')
        rights = row.get('rights', {})
        privacy = row.get('privacy', {})
        if not isinstance(rights, dict):
            rights = {}
        if not isinstance(privacy, dict):
            privacy = {}
        uses = rights.get('allowed_uses')
        if (rights.get('authorized') is not True or not _id(rights.get('authorization_ref'))
                or not isinstance(uses, list) or split not in uses):
            errors.append(prefix + ':authorization_or_intended_use_missing')
        if (privacy.get('metadata_reviewed') is not True or privacy.get('pixels_reviewed') is not True
                or not _id(privacy.get('reviewer_id'))):
            errors.append(prefix + ':human_privacy_review_required')
        reviewed = privacy.get('reviewed_sha256')
        if not isinstance(reviewed, list):
            reviewed = []
        assets = row.get('assets')
        if not isinstance(assets, list) or not assets or len(assets) > 100:
            errors.append(prefix + ':invalid_assets')
            continue
        keys = [(key, row.get(key)) for key in ('patient_group_id', 'study_group_id', 'source_group_id')]
        if 'lineage_group_id' in row:
            if not _id(row['lineage_group_id']):
                errors.append(prefix + ':invalid_lineage')
            keys.append(('lineage_group_id', row['lineage_group_id']))
        for asset in assets:
            if not isinstance(asset, dict):
                errors.append(prefix + ':invalid_asset')
                continue
            aid, digest = asset.get('id'), asset.get('sha256')
            if not _id(aid) or aid in asset_ids:
                errors.append(prefix + ':invalid_or_reused_asset_id')
            elif _id(aid):
                asset_ids.add(aid)
            if split == 'blind_test' and (not isinstance(aid, str) or not re.fullmatch(r'asset-[0-9]{3,12}', aid)):
                errors.append(prefix + ':neutral_blind_asset_id_required')
            if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
                errors.append(prefix + ':invalid_digest')
            else:
                keys.append(('sha256', digest))
                if digest in digests:
                    errors.append(prefix + ':duplicate_binary_reuse_forbidden')
                digests.add(digest)
                assets_by_hash[digest] = row
                if digest not in reviewed:
                    errors.append(prefix + ':privacy_review_not_bound_to_bytes')
            if type(asset.get('derivative')) is not bool:
                errors.append(prefix + ':explicit_derivative_flag_required')
            parent = asset.get('parent_sha256')
            if asset.get('derivative') is True:
                if (not isinstance(parent, str) or not DIGEST.fullmatch(parent) or parent == digest
                        or not _id(row.get('lineage_group_id'))):
                    errors.append(prefix + ':valid_parent_and_lineage_required')
                else:
                    parents.append((digest, parent, row))
            elif parent is not None:
                errors.append(prefix + ':parent_requires_derivative_flag')
            if type(asset.get('size_bytes')) is not int or not 0 < asset['size_bytes'] <= 64 * 1024 * 1024:
                errors.append(prefix + ':invalid_size')
            if not isinstance(asset.get('path'), str) or not asset['path']:
                errors.append(prefix + ':invalid_path')
        for key, value in keys:
            if not isinstance(value, str):
                continue
            identity = (key, value)
            if identity in groups and groups[identity] != split:
                errors.append(prefix + ':cross_split_' + key)
            groups[identity] = split
    parent_edges = {}
    for child, parent, row in parents:
        parent_edges[child] = parent
        ancestor = assets_by_hash.get(parent)
        if ancestor is None:
            errors.append('derivative_parent_not_in_bank')
        elif any(row.get(k) != ancestor.get(k) for k in
                 ('split', 'patient_group_id', 'study_group_id', 'source_group_id', 'lineage_group_id')):
            errors.append('derivative_must_inherit_partition_identity_and_lineage')
    for child in parent_edges:
        visited = set()
        while child in parent_edges:
            if child in visited:
                errors.append('cyclic_derivative_lineage')
                break
            visited.add(child)
            child = parent_edges[child]
    return dict(errors=errors, case_count=len(cases),
        clinical_release_status='CLINICALLY_PENDING',
        diagnostic_validation=False, training_performed=False)


def admitted_inputs(bank, root, split):
    gate = validate_bank(bank)
    if gate['errors']:
        raise ValueError('bank_rejected:' + ','.join(gate['errors']))
    if split not in SPLITS:
        raise ValueError('invalid_split')
    result = []
    for case in bank['cases']:
        if case['split'] != split:
            continue
        # This delivery has no validated blind-video contract. Reject before
        # opening a codec, independently of container tags or review claims.
        if split == 'blind_test' and (TASKS[case['task_id']][1] == 'video'
                or any(PurePosixPath(asset['path']).suffix.lower() in {'.mp4', '.webm'}
                       for asset in case['assets'])):
            raise ValueError('blind_video_not_supported')
        if split == 'blind_test' and any(
                PurePosixPath(asset['path']).suffix.lower() not in {'.png', '.jpg', '.jpeg'}
                for asset in case['assets']):
            raise ValueError('blind_image_format_required')
        reports = [inspect_media(root, asset) for asset in case['assets']]
        if any(r['errors'] for r in reports):
            raise ValueError('media_admission_failed')
        if any(r['kind'] == 'video' for r in reports) and case['privacy'].get('full_video_reviewed') is not True:
            raise ValueError('full_video_privacy_review_required')
        # Fail closed on metadata-bearing material in a blind input. Review or
        # stripping must create a new derivative/hash and be registered anew.
        if split == 'blind_test' and any(r['metadata_present'] for r in reports):
            raise ValueError('blind_media_metadata_requires_clean_derivative')
        result.append(build_input(case, reports))
    return result


def blinded_inputs(bank, root):
    return admitted_inputs(bank, root, 'blind_test')
