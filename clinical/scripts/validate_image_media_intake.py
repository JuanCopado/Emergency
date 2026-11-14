#!/usr/bin/env python3
"""Offline integrity check for source-known teaching media, never accuracy QA.

This complements the existing blinded dataset validator: it does not replace it,
download files, invoke a provider, authenticate a diagnosis, or enable training.
"""
import argparse
import hashlib
import json
from pathlib import Path


def validate(data, root):
    root = Path(root).resolve()
    errors = []
    if data.get('dataset_class') != 'teaching_source_known':
        errors.append('Use the existing blinded validator for diagnostic evaluation.')
    for key in ('metrics_eligible', 'metrics_requested', 'external_inference_performed'):
        if data.get(key) is not False:
            errors.append(f'{key} must be explicitly false for this intake workflow')
    items = data.get('items')
    if not isinstance(items, list) or not items:
        return {'errors': errors + ['items must be non-empty'], 'status': 'BLOCKED'}
    seen_ids, hashes, groups = set(), set(), set()
    for item in items:
        if not isinstance(item, dict):
            errors.append('Each item must be an object')
            continue
        mid = item.get('id', '<missing>')
        if not isinstance(mid, str) or not mid or mid in seen_ids:
            errors.append('Missing/duplicate media id')
            continue
        seen_ids.add(mid)
        for key in ('source_case_group_id', 'modality', 'source_page', 'author',
                    'license', 'license_url', 'license_checked', 'sha256'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f'{mid}: {key} required')
        group = item.get('source_case_group_id')
        if isinstance(group, str) and group:
            groups.add(group)
        if item.get('dataset_class') != 'teaching_source_known':
            errors.append(f'{mid}: source-known case cannot become blinded by renaming')
        if item.get('split') != 'teaching_development':
            errors.append(f'{mid}: teaching examples must remain outside held-out test')
        if item.get('metrics_eligible') is not False or item.get('training_performed') is not False:
            errors.append(f'{mid}: cannot claim accuracy eligibility or completed training')
        value = item.get('file')
        if not isinstance(value, str) or not value:
            errors.append(f'{mid}: relative file path required')
            continue
        relative = Path(value)
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root):
            errors.append(f'{mid}: file escapes batch root')
            continue
        if not path.is_file():
            errors.append(f'{mid}: file missing')
            continue
        digest = hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
        actual_hash = digest.hexdigest()
        if actual_hash != item.get('sha256') or path.stat().st_size != item.get('size_bytes'):
            errors.append(f'{mid}: size/hash mismatch')
        if actual_hash in hashes:
            errors.append(f'{mid}: duplicate binary; deduplicate before counting')
        hashes.add(actual_hash)
    if data.get('media_count') != len(items) or data.get('source_case_groups') != len(groups):
        errors.append('Declared media/group counts do not match records')
    return {
        'status': 'BLOCKED' if errors else 'REGISTERED_NOT_DIAGNOSTICALLY_VALIDATED',
        'errors': errors, 'media_count': len(items), 'source_case_groups': len(groups),
        'scope': 'Offline file/provenance integrity only; no clinical or rights certification',
        'metrics_eligible': False, 'training_performed': False,
        'human_review': 'Clinical reference and full privacy review remain separate',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.manifest.read_text(encoding='utf-8')), args.manifest.parent)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
