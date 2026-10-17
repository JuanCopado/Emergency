"""Validate dossier coverage and non-promotion invariants, never clinical validity."""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT/'clinical/qa'
sys.path.insert(0, str(ROOT/'clinical/scripts'))
from acute_medication_api import catalog


def main():
    dossier = json.loads((QA/'V1.44_MEDICATION_PRODUCT_PROTOCOL_RECONCILIATION.json').read_text(encoding='utf-8'))
    baseline = json.loads((QA/'product-reconciliation-v144/BASELINE.json').read_text(encoding='utf-8'))
    current = catalog()
    expected = {r['id'] for r in current['regimens'] if r.get('block_reason')}
    actual = [r['id'] for r in dossier['blocked_contracts']]
    assert len(actual) == len(set(actual)) and set(actual) == expected
    assert dossier['source_revision'] == current['source_revision']
    assert dossier['non_executable_research_dossier'] is True
    assert dossier['clinical_implementation_changed'] is False
    assert dossier['professionally_reconciled_count'] == 0
    assert dossier['version_status'] == 'OPEN' and dossier['clinical_status'] == 'CLINICALLY_PENDING'
    assert dossier['local_override'] is None and dossier['local_protocol']['approved'] is False
    sources = {s['id']: s for s in dossier['sources']}
    product_ids = {p['id'] for p in dossier['products']}
    preparation_ids = {p['id'] for p in dossier['preparations']}
    assert len(product_ids) == len(dossier['products'])
    assert len(preparation_ids) == len(dossier['preparations'])
    for row in dossier['blocked_contracts']:
        assert row['execution_status'] == 'BLOCKED'
        assert row['human_review'] is None and row['local_protocol'] is None and row['local_override'] is None
        assert set(row['product_candidates']) <= product_ids
        assert set(row['preparation_candidates']) <= preparation_ids
        assert set(row['block_categories']) <= set('ABCDEFGH')
    for product in dossier['products']:
        assert product['runtime_enabled'] is False and product['human_review'] is None
        assert product['local_stock'] is None and product['local_protocol'] is None
        assert product['status'] == 'CLINICAL_REVIEW_REQUIRED'
        assert sources[product['source']]['review_status'] == 'FOCUSED_SOURCE_REVIEW_NOT_HUMAN_APPROVAL'
    for preparation in dossier['preparations']:
        assert preparation['runtime_enabled'] is False and preparation['status'] == 'BLOCKED'
        assert preparation['human_review'] is None and preparation['local_protocol'] is None
        assert set(preparation['product_ids']) <= product_ids
        assert set(preparation['source']) <= sources.keys()
    for item in dossier['professional_checklist'].values():
        assert item['status'] in ('REVIEW', 'BLOCKED')
        assert item['reviewer'] is None and item['date'] is None and item['evidence'] is None
    for name, expected_hash in baseline['unchanged_files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected_hash, name
    for ref, expected_sha in baseline['protected_refs'].items():
        assert subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip() == expected_sha, ref
    report = {'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'PASS',
              'scope': 'Inventory, references and unchanged implementation/evidence safeguards only; no clinical approval.',
              'blocked_contracts': len(actual), 'by_group': dict(collections.Counter(r['flow'] for r in dossier['blocked_contracts'])),
              'product_profiles': len(product_ids), 'preparation_profiles': len(preparation_ids),
              'unchanged_file_hashes': len(baseline['unchanged_files']), 'protected_refs_unchanged': True,
              'clinical_status': 'CLINICALLY_PENDING', 'version_status': 'OPEN'}
    (QA/'product-reconciliation-v144/RECONCILIATION_INTEGRITY.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
