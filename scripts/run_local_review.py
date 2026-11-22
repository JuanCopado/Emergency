#!/usr/bin/env python3
"""Start the composed Emergency synthetic review on loopback only.

The three backends remain separate processes. In particular, the T06 loopback
audit hook must never be imported into the clinical-note process.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from http.client import HTTPConnection, HTTPException
import json
import os
import secrets
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
MODEL_SHA256 = '7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2'
BACKEND_PORTS = (8765, 8766, 8767)


def port_number(value):
    port = int(value)
    if not 1024 <= port <= 65535 or port in BACKEND_PORTS:
        raise argparse.ArgumentTypeError('Choose a UI port from 1024 to 65535, excluding 8765–8767')
    return port


def check_python(interpreter, code):
    return json.loads(subprocess.check_output([str(interpreter), '-c', code], text=True))


def service_ready(name, ui_port):
    """Probe one fixed loopback service; redirects and ambient proxies are unused."""
    if type(ui_port) is not int or not 1024 <= ui_port <= 65535 or ui_port in BACKEND_PORTS:
        raise ValueError('Invalid local UI port')
    endpoints = {'clinical': (8765, '/api/clinical-note/health'),
                 'blood-gas': (8767, '/api/blood-gas/session'),
                 't06': (8766, '/api/lab-status'), 'app': (ui_port, '/')}
    if name not in endpoints:
        raise ValueError('Unknown local service')
    port, path = endpoints[name]
    connection = HTTPConnection('127.0.0.1', port, timeout=1)
    try:
        connection.request('GET', path, headers={
            'Origin': f'http://127.0.0.1:{ui_port}',
            'X-Emergency-T06-Lab': 'synthetic-loopback'})
        with connection.getresponse() as response:
            return response.status == 200
    except (OSError, HTTPException):
        return False
    finally:
        connection.close()


def stop_process(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


def main():
    if os.name == 'nt':
        signal.signal(signal.SIGBREAK, signal.default_int_handler)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blood-python', type=Path, default=Path(sys.executable))
    parser.add_argument('--t06-python', type=Path, help='Isolated T06 interpreter; required on Linux')
    parser.add_argument('--ocr-model', type=Path, default=os.environ.get('BG_OCR_MODEL'))
    parser.add_argument('--ui-port', type=port_number, default=5173)
    parser.add_argument('--evidence-dir', type=Path)
    parser.add_argument('--check', action='store_true', help='Check prerequisites without starting servers')
    args = parser.parse_args()
    if sys.platform not in ('linux', 'win32'):
        parser.error('This launcher supports the verified Linux and Windows adapters only')
    native_extraction = sys.platform == 'win32'
    native_t06 = sys.platform == 'linux'
    if native_t06 and args.t06_python is None:
        parser.error('Provide the isolated Linux T06 interpreter with --t06-python')
    model = args.ocr_model.resolve() if args.ocr_model else None
    if native_extraction and (model is None or model.name != 'eng.traineddata' or not model.is_file()):
        parser.error('Provide the verified eng.traineddata with --ocr-model or BG_OCR_MODEL')
    if model is not None and (not model.is_file() or hashlib.sha256(model.read_bytes()).hexdigest() != MODEL_SHA256):
        parser.error('The OCR model does not match the verified T05 delivery')
    node = shutil.which('node')
    if node is None or not (ROOT / 'app/node_modules/vite/bin/vite.js').is_file():
        parser.error('Install Node and the app dependencies from the committed lock first')
    ocr_modules = ROOT / 'tools/blood-gas-ocr/node_modules'
    if native_extraction and not (ocr_modules / 'tesseract.js/package.json').is_file():
        parser.error('Install tools/blood-gas-ocr dependencies from its committed lock first')
    # Resolving a venv's executable symlink would select its base interpreter
    # and silently discard the isolated dependencies.
    blood_python = args.blood_python.absolute()
    t06_python = args.t06_python.absolute() if args.t06_python else None
    versions = {
        'blood_gas': check_python(blood_python,
            "import json,sys,importlib.metadata as m;print(json.dumps(dict(python=sys.version,"
            "packages={n:m.version(n) for n in ['Pillow','pypdf','reportlab']})))"),
        'node': subprocess.check_output([node, '--version'], text=True).strip(),
    }
    if native_t06:
        versions['t06'] = check_python(t06_python,
            "import json,sys,importlib.metadata as m;print(json.dumps(dict(python=sys.version,"
            "packages={n:m.version(n) for n in ['h11','cryptography']})))")
        if versions['t06']['packages'] != {'h11': '0.16.0', 'cryptography': '50.0.1'}:
            parser.error('T06 requires its original h11 0.16.0 and cryptography 50.0.1 pins')
    if native_extraction:
        versions['blood_gas']['pdfium'] = check_python(blood_python,
            "import json,importlib.metadata as m;print(json.dumps(m.version('pypdfium2')))")
    subprocess.run([node, 'scripts/picomatch-mitigation.mjs', '--check'],
                   cwd=ROOT / 'app', check=True, stdout=subprocess.DEVNULL)
    if native_extraction:
        subprocess.run([node, '-e', "require('tesseract.js'); require('tesseract.js-core')"],
                       env={**os.environ, 'NODE_PATH': str(ocr_modules)}, check=True)
    for port in (8765, 8767, args.ui_port, *((8766,) if native_t06 else ())):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', port))
    if args.check:
        print(json.dumps({'status': 'PREREQUISITES_OK', 'versions': versions,
                          'capabilities': {'t05_native_extraction': native_extraction, 't06_transport': native_t06}}, indent=2))
        return

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    evidence = args.evidence_dir.resolve() if args.evidence_dir else ROOT / '.local-review' / stamp
    evidence.mkdir(parents=True, exist_ok=False)
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1',
                   **({'BG_OCR_MODEL': str(model)} if model is not None else {}), 'NODE_PATH': str(ocr_modules),
                   'EMERGENCY_LOCAL_REVIEW': '1', 'EMERGENCY_LOCAL_REVIEW_PORT': str(args.ui_port)}
    # Provision a fresh process credential for this launch; never log it or send it to T05/T06.
    clinical_token = secrets.token_hex(32)
    commands = {
        'clinical': [str(blood_python), '-B', 'clinical/scripts/clinical_note_api.py', '--port', '8765',
                     '--ui-port', str(args.ui_port)],
        'blood-gas': [str(blood_python), '-B', 'clinical/scripts/blood_gas_local.py', '--port', '8767',
                      '--ui-port', str(args.ui_port)],
        'app': [node, 'node_modules/vite/bin/vite.js', '--host', '127.0.0.1',
                '--port', str(args.ui_port), '--strictPort'],
    }
    if native_t06:
        commands['t06'] = [str(t06_python), '-B', 'tools/t06-localhost-lab/run_local.py',
                           '--python', str(t06_python), '--port', '8766', '--ui-port', str(args.ui_port),
                           '--evidence-dir', str(evidence / 't06')]
    processes, logs = {}, []
    origin = f'http://127.0.0.1:{args.ui_port}'
    started = datetime.now(timezone.utc).isoformat()
    try:
        for name, command in commands.items():
            child_environment = {key: value for key, value in environment.items()
                                 if key != 'EMERGENCY_LOCAL_API_TOKEN'}
            if name in {'clinical', 'app'}:
                child_environment['EMERGENCY_LOCAL_API_TOKEN'] = clinical_token
            log = (evidence / f'{name}.log').open('wb')
            logs.append(log)
            group = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
            processes[name] = subprocess.Popen(command, cwd=ROOT / 'app' if name == 'app' else ROOT,
                                                env=child_environment, stdout=log, stderr=subprocess.STDOUT, **group)
        pending, deadline = set(processes), time.monotonic() + 45
        while pending:
            for name, process in processes.items():
                if process.poll() is not None:
                    raise RuntimeError(f'{name} exited during startup; inspect {evidence / (name + ".log")}')
            for name in list(pending):
                if service_ready(name, args.ui_port):
                    pending.remove(name)
            if time.monotonic() >= deadline:
                raise RuntimeError('Local startup did not complete: ' + ', '.join(sorted(pending)))
            time.sleep(0.1)
        (evidence / 'LAUNCH.json').write_text(json.dumps({
            'started_utc': started, 'origin': origin, 'state': 'CLINICALLY_PENDING',
            'synthetic_only': True, 'versions': versions, 'model_sha256': MODEL_SHA256,
            'capabilities': {'t05_native_extraction': native_extraction, 't06_transport': native_t06},
            'processes': {name: process.pid for name, process in processes.items()},
        }, indent=2) + '\n', encoding='utf8')
        print(f'Emergency · revisión local con datos sintéticos: {origin}', flush=True)
        print(f'Gasometría: {origin}/blood-gas · T06: {origin}/t06-lab', flush=True)
        print('Extracción T05: ' + ('Windows disponible' if native_extraction else 'requiere Windows; bloqueada en Linux'), flush=True)
        print('Transporte T06: ' + ('Linux disponible' if native_t06 else 'requiere Linux; no iniciado en Windows'), flush=True)
        print('CLINICALLY_PENDING. Ctrl+C detiene únicamente los procesos de esta sesión.', flush=True)
        while all(process.poll() is None for process in processes.values()):
            time.sleep(0.2)
        raise RuntimeError('A local service stopped; all services in this session will stop')
    except KeyboardInterrupt:
        pass
    finally:
        for process in reversed(list(processes.values())):
            stop_process(process)
        for log in logs:
            log.close()
        (evidence / 'STOP.json').write_text(json.dumps({
            'stopped_utc': datetime.now(timezone.utc).isoformat(),
            'exit_codes': {name: process.returncode for name, process in processes.items()},
        }, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
