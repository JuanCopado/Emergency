#!/usr/bin/env python3
"""Exercise the real composed launcher and browser in the supported platform."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('module', choices=('t05', 't06'))
    parser.add_argument('--t06-python', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ocr-model', type=Path)
    args = parser.parse_args()
    if (args.module == 't05' and sys.platform != 'win32') or (args.module == 't06' and sys.platform != 'linux'):
        parser.error('The selected test must run on its native supported platform')
    output = args.output.absolute()
    output.mkdir(parents=True, exist_ok=False)
    session = output / 'session'
    command = [sys.executable, '-B', str(ROOT / 'scripts/run_local_review.py'),
               '--blood-python', sys.executable, '--evidence-dir', str(session)]
    if args.t06_python:
        command += ['--t06-python', str(args.t06_python.absolute())]
    if args.ocr_model:
        command += ['--ocr-model', str(args.ocr_model.absolute())]
    environment = {**os.environ, 'CLINICAL_PYTHON': sys.executable,
                   'T05_APP_URL': 'http://127.0.0.1:5173', 'T06_APP_URL': 'http://127.0.0.1:5173/',
                   'T05_BROWSER_OUT': str(output / 'browser'), 'T06_BROWSER_OUT': str(output / 'browser'),
                   'T06_BACKEND_EVIDENCE_DIR': str(session / 't06')}
    group = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
    with (output / 'launcher.log').open('wb') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT, **group)
        try:
            deadline = time.monotonic() + 60
            while not (session / 'LAUNCH.json').is_file():
                if process.poll() is not None:
                    raise RuntimeError(f'Composed launcher exited with {process.returncode}; see {output / "launcher.log"}')
                if time.monotonic() >= deadline:
                    raise RuntimeError('Composed launcher did not become ready within 60 seconds')
                time.sleep(0.1)
            receipt = json.loads((session / 'LAUNCH.json').read_text())
            required = 't05_native_extraction' if args.module == 't05' else 't06_transport'
            if receipt['capabilities'][required] is not True:
                raise RuntimeError('The launcher did not enable the actual native capability')
            subprocess.run([shutil.which('node') or 'node', f'app/scripts/check-{args.module}-local-review.mjs'],
                           cwd=ROOT, env=environment, check=True, timeout=360)
        finally:
            if process.poll() is None:
                process.send_signal(signal.CTRL_BREAK_EVENT if os.name == 'nt' else signal.SIGINT)
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                    raise RuntimeError('The composed launcher did not stop its owned services')
    if not (session / 'STOP.json').is_file():
        raise RuntimeError('The launcher did not record shutdown of its owned processes')
    print(f'PASS: composed {args.module} browser and launcher; evidence {output}')


if __name__ == '__main__':
    main()
