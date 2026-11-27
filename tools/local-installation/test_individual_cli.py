"""Synthetic supervision checks; no publisher keys, clinical cases or real workers."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

import backend_runtime
import individual_cli as cli
import local_installation as local
import stable_launcher


class IndividualCliSupervisionTests(unittest.TestCase):
    def test_public_serve_optional_bootstrap_gate_rejects_before_auth(self):
        for value in (b'',b'OTHER\n'):
            with patch.object(sys,'argv',['individual_cli.py','serve','--root','synthetic','--parent-gate']),\
                 patch.object(sys,'stdin',type('Input',(),{'buffer':io.BytesIO(value)})()),\
                 patch.object(cli.auth,'active_signed_snapshot') as verify:
                with self.assertRaises(local.ReleaseError):cli.main()
                verify.assert_not_called()

    def test_private_serve_rejects_missing_gate_before_reading_release(self):
        for value in (b'', b'START WITHOUT NEWLINE', b'OTHER\n'):
            with self.subTest(gate=value), patch.object(sys, 'stdin', type('Input', (), {'buffer': io.BytesIO(value)})()), \
                    patch.object(cli.auth, 'active_signed_snapshot') as verify:
                with self.assertRaises(local.ReleaseError):
                    cli._serve(Path('synthetic'), 'version-a')
                verify.assert_not_called()

    def test_private_serve_rejects_changed_selection_before_runtime(self):
        with patch.object(sys, 'stdin', type('Input', (), {'buffer': io.BytesIO(b'START\n')})()), \
                patch.object(cli.auth, 'active_signed_snapshot', return_value=(Path('release'), {}, {}, {'version': 'new'})), \
                patch.object(cli, 'verify_runtime') as runtime:
            with self.assertRaises(local.ReleaseError):
                cli._serve(Path('synthetic'), 'old')
            runtime.assert_not_called()

    def test_private_serve_eof_stops_owned_listener_and_outputs_identity_only(self):
        stopped = threading.Event()
        class Server:
            server_port = 15882
            def __enter__(self): return self
            def __exit__(self, *_): self.closed = True
            def shutdown(self): stopped.set()
            def serve_forever(self):
                if not stopped.wait(2): raise AssertionError('Parent EOF did not stop listener')
        server = Server()
        output = io.StringIO()
        selection = {'version': 'synthetic-v1'}
        with patch.object(sys, 'stdin', type('Input', (), {'buffer': io.BytesIO(b'START\n')})()), \
                patch.object(sys, 'stdout', output), \
                patch.object(cli.auth, 'active_signed_snapshot', return_value=(Path('release'), {'source_sha': 'a'*40}, {}, selection)), \
                patch.object(cli.os.path, 'samefile', return_value=True), \
                patch.object(cli, 'runtime_fingerprint', return_value='fingerprint'), \
                patch.object(cli, 'verify_runtime', return_value=Path('python.exe')), \
                patch.object(stable_launcher, 'make_stable_server', return_value=server):
            cli._serve(Path('synthetic'), 'synthetic-v1')
        self.assertTrue(server.closed)
        identity = json.loads(output.getvalue())
        self.assertEqual(set(identity), {'url', 'version', 'source_sha', 'clinical', 'release'})
        self.assertEqual(identity['url'], 'http://127.0.0.1:15882')
        self.assertEqual(identity['release'], 'NO_GO_CLINICAL_RELEASE')

    def supervise(self, job_failure=False):
        events = []
        class Pipe:
            closed = False
            def write(self, data): events.append(('gate', data))
            def flush(self): events.append(('flush',))
            def close(self): self.closed = True; events.append(('pipe_closed',))
        class Process:
            stdin = Pipe()
            def wait(self, timeout=None): events.append(('wait', timeout)); return 7
            def kill(self): events.append(('kill',))
        process = Process()
        def job_factory(_process):
            self.assertIs(_process, process)
            events.append(('assigned',))
            if job_failure: raise OSError('Synthetic assignment failure')
            return type('Job', (), {'close': lambda self: events.append(('job_closed',))})()
        with patch.object(sys, 'argv', ['individual_cli.py', 'serve', '--root', 'synthetic']), \
                patch.object(cli.auth, 'active_signed_snapshot', return_value=(Path('release'), {}, {}, {'version': 'version-a'})), \
                patch.object(cli, 'runtime_fingerprint', return_value='fingerprint'), \
                patch.object(cli, 'verify_runtime', return_value=Path('python.exe')), \
                patch.object(cli.subprocess, 'Popen', return_value=process) as spawn, \
                patch.object(backend_runtime, '_WindowsChildJob', side_effect=job_factory), \
                patch.dict(os.environ, {'HTTPS_PROXY': 'SECRET', 'CLINICAL_NOTE_VISION_API_KEY': 'SECRET', 'PYTHONPATH': 'SECRET'}):
            if job_failure:
                with self.assertRaises(OSError): cli.main()
            else:
                self.assertEqual(cli.main(), 7)
        command = spawn.call_args.args[0]
        self.assertEqual(command[1:3], ['-I', '-B'])
        self.assertEqual(command[-1], 'version-a')
        self.assertEqual(spawn.call_args.kwargs['stdin'], subprocess.PIPE)
        self.assertNotIn('SECRET', json.dumps(spawn.call_args.kwargs['env']))
        self.assertTrue(process.stdin.closed)
        return events

    @unittest.skipUnless(os.name == 'nt', 'Windows owned-process Job Object gate')
    def test_windows_job_assignment_precedes_start_gate_and_closes(self):
        events = self.supervise()
        self.assertLess(events.index(('assigned',)), events.index(('gate', b'START\n')))
        self.assertLess(events.index(('pipe_closed',)), events.index(('job_closed',)))

    @unittest.skipUnless(os.name == 'nt', 'Windows owned-process Job Object gate')
    def test_windows_job_assignment_failure_never_starts_worker(self):
        events = self.supervise(job_failure=True)
        self.assertFalse(any(event[0] == 'gate' for event in events))
        self.assertIn(('pipe_closed',), events)


if __name__ == '__main__':
    unittest.main(verbosity=2)
