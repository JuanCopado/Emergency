"""Repeat technical QA without replacing the previous acute/pediatric evidence.

This runner does not approve products, preparations or clinical protocols.
Browser drivers are copied temporarily beside their originals. Only the output
URL changes; assertions, inputs, browser interactions and sources are identical.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'clinical/qa/product-reconciliation-v144'
DRIVERS = {
    'check-acute-medications-v144.mjs': 'V1.44_ACUTE_${group.toUpperCase()}_BROWSER_RESULTS.json',
    'check-pediatric-complete-v144.mjs': "V1.44_PEDIATRIC_${only ? 'FILTERED' : 'COMPLETE'}_BROWSER_RESULTS.json",
    'check-pediatric-export-v144.mjs': 'V1.44_PEDIATRIC_EXPORT_BROWSER_RESULTS.json',
    'check-pharmacology-v144.mjs': 'V1.44_PHARMACOLOGY_BROWSER_RESULTS.json',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    baseline = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT/'clinical/qa').glob('*BROWSER_RESULTS.json')}
    report = {
        'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'tested_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'version_status': 'OPEN', 'clinical_status': 'CLINICALLY_PENDING',
        'purpose': 'Technical regression with unchanged clinical implementation; no product or local protocol approved.',
        'checks': [], 'browser_driver_copies': [], 'historical_evidence_hashes': baseline,
    }

    def save():
        target = OUT/'QA_RESULTS.json'
        temp = target.with_suffix('.json.tmp')
        temp.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
        temp.replace(target)

    def run(command, cwd=ROOT):
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        print('RUN ' + ' '.join(map(str, command)), flush=True)
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        check = {'command': command, 'cwd': str(cwd.relative_to(ROOT)), 'started_at': started,
                 'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
        report['checks'].append(check)
        save()
        print(('PASS ' if result.returncode == 0 else 'FAIL ') + ' '.join(map(str, command)), flush=True)
        if result.returncode:
            raise RuntimeError(f'QA command failed: {command}; see {OUT}/QA_RESULTS.json')

    env = os.environ
    env['PYTHONUTF8'] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['NODE_OPTIONS'] = '--max-old-space-size=512 --max-semi-space-size=2'
    env['UV_THREADPOOL_SIZE'] = '1'
    env['CLINICAL_QA_PYTHON'] = sys.executable
    env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
    env['FLOW_FILTER'] = 'all'
    env.pop('PEDIATRIC_CASE_FILTER', None)
    temp_dir = ROOT/'.qa-tmp'
    temp_dir.mkdir(exist_ok=True)
    env['TEMP'] = env['TMP'] = str(temp_dir)
    try:
        for pattern in ['test_acute_medication_v144.py', 'test_pharmacology_v144.py', 'test_pediatric_export_v144.py']:
            run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'clinical/tests', '-p', pattern])
        run([sys.executable, '-B', 'clinical/qa/qa_runner.py'])
        for args in [
            ['test', '--', '--maxWorkers=1', '--minWorkers=1', '--reporter=json', '--outputFile=../clinical/qa/product-reconciliation-v144/FRONTEND_RESULTS.json'],
            ['run', 'guides:test'], ['run', 'procedures:test'], ['run', 'lint'], ['run', 'typecheck'], ['run', 'build'],
        ]:
            run(['npm.cmd' if os.name == 'nt' else 'npm', *args], ROOT/'app')
        for driver, basename in DRIVERS.items():
            source = ROOT/'app/scripts'/driver
            old = '../../clinical/qa/' + basename
            new = '../../clinical/qa/product-reconciliation-v144/' + basename
            text = source.read_text(encoding='utf-8')
            assert text.count(old) == 1, driver
            redirected = text.replace(old, new)
            assert redirected.replace(new, old) == text, driver
            copy = source.with_name('check-reconciliation-' + driver.removeprefix('check-'))
            assert not copy.exists(), f'Refusing to overwrite {copy}'
            try:
                copy.write_text(redirected, encoding='utf-8', newline='\n')
                report['browser_driver_copies'].append({'original': str(source.relative_to(ROOT)),
                    'original_sha256': sha(source), 'executed_sha256': sha(copy),
                    'only_change': {'from': old, 'to': new}})
                run(['node', 'scripts/' + copy.name], ROOT/'app')
            finally:
                if copy.exists():
                    copy.unlink()
        report['status'] = 'PASS'
    except Exception as exc:
        report['status'] = 'FAIL'
        report['error'] = str(exc)
    finally:
        report['historical_evidence_unchanged'] = all(sha(ROOT/p) == h for p, h in baseline.items())
        if not report['historical_evidence_unchanged']:
            report['status'] = 'FAIL'
        report['finished_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
    print(json.dumps({'status': report['status'], 'historical_evidence_unchanged': report['historical_evidence_unchanged']}), flush=True)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
