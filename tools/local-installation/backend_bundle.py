"""Canonical backend files and offline dependency bootstrap; no clinical edits."""
from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import sysconfig

from local_installation import no_links, regular_bytes, safe_name, canonical_json, object_json, ReleaseError, require

PACKAGES = {"reportlab": "5.0.1", "pillow": "13.0.0", "charset-normalizer": "3.5.2",
            "cryptography": "50.0.2", "cffi": "2.1.1", "pycparser": "3.12"}
DATA = {
    "clinical/calculators/registry.json",
    "clinical/references/module-index.md", "clinical/references/evidence-registry.json",
    "clinical/references/acute-contract-owner-acceptance-2026-11-16.json",
    *('clinical/qa/' + n + '.json' for n in (
        'clinical-note-privacy-policy', 'clinical-note-schema', 'clinical-note-diagnostic-rules',
        'pediatric-outpatient-medications', 'pediatric-outpatient-alert-rules', 'localization-portugal-azores')),
    *('clinical/assets/fonts/' + n for n in (
        'DejaVuSans.ttf', 'DejaVuSans-Bold.ttf', 'EmergencyCJK-Regular.ttf', 'EmergencyCJK-Bold.ttf',
        'LICENSE-DejaVu.txt', 'LICENSE-NotoSansSC.txt', 'README.md', 'noto-cjk-manifest.json')),
}


def clean_environment(temp=None):
    """No user site, proxy, provider credential, Python/Git redirection or logs."""
    env = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR', 'COMSPEC') if k in os.environ}
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    if temp:
        env.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    return env


def _git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='NUL' if os.name == 'nt' else '/dev/null')
    return subprocess.check_output(['git', '--no-pager', '-c', 'core.autocrlf=false', *args], cwd=root,
                                   env=env, timeout=30)


def collect_backend(source_root, wheelhouse, revision=None):
    """Read exact Git blobs, including dynamic canonical data, without copying a checkout."""
    root, wheelhouse = no_links(source_root), no_links(wheelhouse)
    revision = revision or _git(root, 'rev-parse', 'HEAD').decode().strip()
    require(bool(re.fullmatch('[0-9a-f]{40}', revision)), 'Exact backend Git revision required')
    tracked = set(_git(root, 'ls-tree', '-r', '--name-only', revision).decode().splitlines())
    def blob(name):
        require(name in tracked, 'Backend canonical dependency is not tracked')
        return _git(root, 'show', revision + ':' + name)
    available = {Path(n).stem: n for n in tracked if n.startswith('clinical/scripts/') and n.endswith('.py')}
    pending = ['clinical_note_api']; selected = set(); texts = []
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        require(name in available, 'Backend import is missing')
        selected.add(name)
        text = blob(available[name]).decode('utf-8-sig'); texts.append(text)
        for node in ast.walk(ast.parse(text)):
            imports = [a.name.split('.')[0] for a in node.names] if isinstance(node, ast.Import) else ([node.module.split('.')[0]] if isinstance(node, ast.ImportFrom) and node.module else [])
            pending.extend(n for n in imports if n in available and n not in selected)
    paths = set(DATA) | {available[n] for n in selected}
    index = blob('clinical/references/module-index.md').decode('utf-8')
    for name in re.findall(r'^\| [a-z0-9-]+ \| `([^`]+)` \|$', index, re.M):
        safe_name(name)
        require(name.startswith('modules/') and name.endswith('.md'), 'Unexpected canonical module location')
        paths.add('clinical/' + name)
    for text in texts:
        for name in re.findall(r"references/[A-Za-z0-9_./-]+\.md", text):
            paths.add('clinical/' + safe_name(name))
    files = {'backend/' + n: blob(n) for n in sorted(paths)}
    # Explicit bootstrap allowlist. These bytes are authenticated by the outer release.
    for name in ('backend_runtime.py', 'backend_bundle.py', 'local_installation.py',
                 'auth_release.py', 'stable_launcher.py', 'individual_cli.py'):
        files['backend/launcher/' + name] = blob('tools/local-installation/' + name)
    requirements = []
    wheel_rows = []
    for wheel in sorted(wheelhouse.glob('*.whl')):
        name = wheel.name
        safe_name(name)
        distribution, version = name.split('-')[:2]
        normalized = distribution.lower().replace('_', '-')
        require(normalized in PACKAGES and version == PACKAGES[normalized], 'Unexpected runtime wheel')
        require(normalized not in {r['distribution'] for r in wheel_rows}, 'Duplicate runtime distribution')
        data = regular_bytes(wheel)
        sha = hashlib.sha256(data).hexdigest()
        files['backend/wheels/' + name] = data
        requirements.append(f'{normalized}=={version} --hash=sha256:{sha}')
        wheel_rows.append({'path': 'backend/wheels/' + name, 'distribution': normalized, 'version': version, 'sha256': sha, 'bytes': len(data)})
    require({r['distribution'] for r in wheel_rows} == set(PACKAGES), 'Incomplete offline wheelhouse')
    files['backend/requirements.lock'] = ('\n'.join(sorted(requirements)) + '\n').encode()
    files['backend/runtime.json'] = canonical_json({
        'schema': 'emergency.backend-runtime.v1', 'source_sha': revision,
        'python': [3, 12], 'platform': 'win-amd64', 'packages': PACKAGES,
        'interpreter': 'Compatible Python 3.12 x64 must already be installed; interpreter not redistributed',
        'network': 'disabled in clinical worker', 'wheels': wheel_rows,
    })
    inventory = [{'path': n, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                  'role': 'third-party-wheel' if n.startswith('backend/wheels/') else 'canonical-or-launcher-source'}
                 for n, data in sorted(files.items())]
    files['backend/BACKEND_MANIFEST.json'] = canonical_json({
        'schema': 'emergency.backend-bundle.v1', 'source_sha': revision, 'files': inventory,
        'rights': 'Existing owner-authorized project sources and fonts with accompanying licenses; no original publications, loans or patient assets',
        'trust': 'This inner manifest is integrity only; caller must verify the outer signed release first',
        'clinical': 'CLINICALLY_PENDING', 'release': 'NO_GO_CLINICAL_RELEASE'})
    return files


def verify_backend(release_root):
    root = no_links(release_root)
    value = object_json(regular_bytes(root / 'backend/BACKEND_MANIFEST.json', 1024 * 1024))
    require(value.get('schema') == 'emergency.backend-bundle.v1' and type(value.get('files')) is list, 'Invalid backend inventory')
    require(0 < len(value['files']) <= 2048, 'Invalid backend file count')
    expected = {'backend/BACKEND_MANIFEST.json'}
    for row in value['files']:
        name = safe_name(row['path'])
        require(name.startswith('backend/') and name not in expected, 'Invalid backend inventory path')
        data = regular_bytes(root / name)
        require(type(row['bytes']) is int and len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], 'Backend dependency bytes changed')
        expected.add(name)
    actual = set()
    for p in (root / 'backend').rglob('*'):
        no_links(p)
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
    require(actual == expected, 'Unmanifested or missing backend file')
    return object_json(regular_bytes(root / 'backend/runtime.json'))


def runtime_fingerprint(release_root):
    root = no_links(release_root)
    runtime = verify_backend(root)
    material = regular_bytes(root / 'backend/requirements.lock') + canonical_json({'python': runtime['python'], 'platform': runtime['platform']})
    return hashlib.sha256(material).hexdigest()


def _runtime_files(directory):
    return [p for p in directory.rglob('*') if p.is_file() and p.name != 'INSTALLATION_RECEIPT.json']


def verify_runtime(directory, expected_fingerprint):
    directory = no_links(directory)
    receipt = object_json(regular_bytes(directory / 'INSTALLATION_RECEIPT.json', 8 * 1024 * 1024))
    require(receipt.get('fingerprint') == expected_fingerprint, 'Runtime does not match signed wheel lock')
    expected = {r['path']: r for r in receipt['files']}
    actual = {p.relative_to(directory).as_posix(): p for p in _runtime_files(directory)}
    require(set(actual) == set(expected), 'Runtime file set changed')
    for name, path in actual.items():
        data = regular_bytes(path)
        require(hashlib.sha256(data).hexdigest() == expected[name]['sha256'], 'Runtime installation bytes changed')
    return directory / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def install_runtime(release_root, runtime_root, python_executable):
    """Offline wheel install into a caller-owned new directory. No global install."""
    release_root, directory = no_links(release_root), no_links(runtime_root)
    runtime = verify_backend(release_root)
    fingerprint = runtime_fingerprint(release_root)
    if directory.exists():
        return verify_runtime(directory, fingerprint)
    executable = no_links(python_executable)
    probe = subprocess.check_output([str(executable), '-I', '-c', 'import json,sys,sysconfig;print(json.dumps([list(sys.version_info[:2]),sysconfig.get_platform()]))'],
                                    env=clean_environment(), timeout=20, text=True)
    require(json.loads(probe) == [runtime['python'], runtime['platform']], 'Compatible Python 3.12 x64 is required for this offline runtime')
    directory.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([str(executable), '-I', '-m', 'venv', str(directory)], env=clean_environment(),
                       check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        python = directory / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        subprocess.run([str(python), '-I', '-m', 'pip', '--isolated', 'install', '--no-index', '--require-hashes',
                        '--only-binary=:all:', '--no-compile', '--find-links', str(release_root / 'backend/wheels'),
                        '-r', str(release_root / 'backend/requirements.lock')], env=clean_environment(),
                       check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        command = 'import importlib.metadata,json;print(json.dumps({n:importlib.metadata.version(n) for n in '+repr(list(PACKAGES))+'}))'
        versions = json.loads(subprocess.check_output([str(python), '-I', '-c', command], env=clean_environment(), timeout=20, text=True))
        require(versions == PACKAGES, 'Installed runtime versions differ')
        files = []
        for p in _runtime_files(directory):
            no_links(p)
            files.append({'path': p.relative_to(directory).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        (directory / 'INSTALLATION_RECEIPT.json').write_bytes(canonical_json({'fingerprint': fingerprint, 'packages': versions, 'files': files,
                   'reproducibility': 'Pinned wheel/ABI/version identity; venv paths are installation-specific, not a byte-identical cross-host executable'}))
        return verify_runtime(directory, fingerprint)
    except BaseException:
        # Retain failed installation for inspection; never silently trust or reuse it.
        raise
