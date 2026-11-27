"""Private offline clinical worker around the unchanged canonical HTTP contracts."""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import queue
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid

ALLOWED_ROUTES = frozenset({
    '/api/acute-medications/catalog', '/api/acute-medications/calculate', '/api/acute-medications/export',
    '/api/clinical-scores/catalog', '/api/clinical-scores/calculate',
    '/api/pediatric-outpatient/calculate', '/api/pediatric-outpatient/export',
    '/api/clinical-note/new', '/api/clinical-note/preflight', '/api/clinical-note/analyze',
    '/api/clinical-note/upload/prepare', '/api/clinical-note/upload/accept',
    '/api/clinical-note/therapy/catalog', '/api/clinical-note/therapy/suggest',
    '/api/clinical-note/therapy/validate', '/api/clinical-note/medication/preflight',
    '/api/clinical-note/export',
})
MAX_INPUT = 26_165_824  # Canonical 12 MiB binary upload plus base64/metadata envelope.
MAX_OUTPUT = 32 * 1024 * 1024


class BackendUnavailable(RuntimeError):
    pass


class _WorkLease:
    def __init__(self, path):
        from backend_bundle import no_links
        no_links(path)
        self.stream=open(path,'a+b')
        if self.stream.seek(0,2)==0:
            self.stream.write(b'0');self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BaseException:
            self.stream.close();raise

    def close(self):
        if not self.stream.closed:self.stream.close()


class _PrivateWork:
    """App-owned marked directories; OS leases live outside case temporary data."""
    SCHEMA='emergency.private-work.v1'
    @classmethod
    def namespace(cls, release_root):
        from backend_bundle import no_links
        release_root=no_links(release_root)
        installation=release_root.parent.parent if release_root.parent.name=='releases' else release_root
        userlocal=os.environ.get('LOCALAPPDATA')
        base=(Path(userlocal) if userlocal else Path(tempfile.gettempdir()))/'Emergency/PrivateWork'
        return no_links(base/hashlib.sha256(os.path.normcase(str(installation)).encode()).hexdigest())

    @classmethod
    def _delete_marked(cls, root, directory):
        from backend_bundle import no_links, regular_bytes
        no_links(root);no_links(directory)
        if directory.parent!=root or not re.fullmatch('[0-9a-f]{32}',directory.name):
            return False
        # Never follow a reparse point, including a descendant inside owned data.
        for child in directory.rglob('*'):no_links(child)
        marker=json.loads(regular_bytes(directory/'OWNER.json',256))
        if marker!={'schema':cls.SCHEMA,'session':directory.name}:return False
        if directory.resolve().parent!=root.resolve():return False
        shutil.rmtree(directory)
        return True

    @classmethod
    def reap(cls, root):
        from backend_bundle import no_links
        no_links(root)
        for directory in root.iterdir():
            if not re.fullmatch('[0-9a-f]{32}',directory.name):continue
            leasepath=root/'leases'/(directory.name+'.lock')
            if not leasepath.is_file():continue
            lease=None
            try:
                lease=_WorkLease(leasepath)
                cls._delete_marked(root,directory)
            except (OSError,ValueError):
                # Active sessions, damaged markers or untrusted paths remain untouched.
                continue
            finally:
                if lease:lease.close()

    def __init__(self, release_root):
        self.root=self.namespace(release_root)
        self.root.mkdir(parents=True,exist_ok=True)
        from backend_bundle import no_links
        no_links(self.root/'leases').mkdir(exist_ok=True)
        self.reap(self.root)
        self.path=self.root/uuid.uuid4().hex
        self.lease=_WorkLease(self.root/'leases'/(self.path.name+'.lock'))
        try:
            self.path.mkdir()
            (self.path/'OWNER.json').write_text(json.dumps({'schema':self.SCHEMA,'session':self.path.name}),encoding='utf-8')
        except BaseException:
            self.lease.close();raise

    def cleanup(self):
        try:self._delete_marked(self.root,self.path)
        finally:self.lease.close()


class _WindowsChildJob:
    """Parent-held, non-inherited handle kills only our worker on parent exit."""
    def __init__(self, process):
        self.handle = None
        if os.name != 'nt':
            return
        import ctypes
        from ctypes import wintypes
        class Basic(ctypes.Structure):
            _fields_ = [('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),
                        ('flags',wintypes.DWORD),('minimum',ctypes.c_size_t),('maximum',ctypes.c_size_t),
                        ('processes',wintypes.DWORD),('affinity',ctypes.c_size_t),
                        ('priority',wintypes.DWORD),('scheduling',wintypes.DWORD)]
        class Extended(ctypes.Structure):
            _fields_ = [('basic',Basic),('io',ctypes.c_uint64*6),('memory',ctypes.c_size_t*4)]
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,wintypes.LPCWSTR]
        kernel.CreateJobObjectW.restype=wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD]
        kernel.SetInformationJobObject.restype=wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes=[wintypes.HANDLE,wintypes.HANDLE]
        kernel.AssignProcessToJobObject.restype=wintypes.BOOL
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        kernel.CloseHandle.restype=wintypes.BOOL
        self.kernel=kernel
        self.handle=kernel.CreateJobObjectW(None,None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits=Extended();limits.basic.flags=0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if (not kernel.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits))
                or not kernel.AssignProcessToJobObject(self.handle,wintypes.HANDLE(int(process._handle)))):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle);self.handle=None


def install_offline_policy():
    """Deny outgoing sockets/DNS/process creation in the dedicated worker only."""
    def guard(event, _args):
        if event in {'socket.connect', 'socket.sendto', 'socket.getaddrinfo', 'socket.gethostbyname',
                     'socket.gethostbyaddr', 'socket.getnameinfo', 'subprocess.Popen', 'os.system', 'os.posix_spawn'}:
            raise PermissionError('External transport and child commands are disabled in the offline worker')
    sys.addaudithook(guard)


def _worker():
    # Only a private parent pipe carries the token. No command line/env/log token.
    line = sys.stdin.buffer.readline(4097)
    if len(line) > 4096:
        raise BackendUnavailable('Invalid startup contract')
    config = json.loads(line)
    if (set(config) != {'release_root', 'ui_port', 'revision', 'token'}
            or type(config['ui_port']) is not int or not 1 <= config['ui_port'] <= 65535
            or not re.fullmatch('[a-f0-9]{40}', config['revision'])
            or not re.fullmatch('[a-f0-9]{64}', config['token'])):
        raise BackendUnavailable('Invalid startup contract')
    clinical = Path(config['release_root']) / 'backend/clinical/scripts'
    sys.path.insert(0, str(clinical))
    install_offline_policy()
    import clinical_note_api
    from clinical_http_boundary import configure_local_server, require_local_request
    from http_transport import BoundedHTTPServer, RequestRejection
    class OfflineHandler(clinical_note_api.ClinicalNoteHandler):
        def do_POST(self):
            # Authenticate even rejected routes; never turn an unknown route into a capability.
            try:
                require_local_request(self)
            except RequestRejection as error:
                self._send(error.status, {'error': 'local request rejected'})
                return
            if self.path not in ALLOWED_ROUTES:
                self.close_connection = True
                self._send(503 if self.path == '/api/clinical-note/upload/interpret' else 404,
                           {'error': 'capability_not_available_offline'})
                return
            super().do_POST()
    class OfflineServer(BoundedHTTPServer):
        def server_bind(self):
            # Avoid HTTPServer.getfqdn(): no DNS/reverse-DNS is needed for a literal loopback bind.
            import socketserver
            socketserver.TCPServer.server_bind(self)
            self.server_name = '127.0.0.1'
            self.server_port = self.server_address[1]
    server = OfflineServer(('127.0.0.1', 0), OfflineHandler)
    configure_local_server(server, ui_port=config['ui_port'], session_token=config['token'])
    print(json.dumps({'port': server.server_port, 'revision': config['revision'], 'offline': True}), flush=True)
    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        server.server_close()


class BackendSession:
    """Caller MUST authenticate the outer release before constructing this object."""
    def __init__(self, release_root, ui_port, revision, python_executable=None):
        from backend_bundle import verify_backend, clean_environment, PACKAGES
        if type(ui_port) is not int or not 1 <= ui_port <= 65535 or not re.fullmatch('[a-f0-9]{40}', revision):
            raise BackendUnavailable('Invalid UI revision or port')
        self._closed = False
        self._process = None
        self._job = None
        self._temporary = None
        self._token = secrets.token_hex(32)
        self._ui_port = ui_port
        self.revision = revision
        self.release_root = Path(release_root).absolute()
        runtime = verify_backend(self.release_root)
        if runtime['source_sha'] != revision:
            raise BackendUnavailable('Backend and UI revision differ')
        python = str(python_executable or sys.executable)
        command = ('import importlib.metadata,json,sys,sysconfig;print(json.dumps({'
                   '"python":list(sys.version_info[:2]),"platform":sysconfig.get_platform(),'
                   '"packages":{n:importlib.metadata.version(n) for n in '+repr(list(PACKAGES))+'}}))')
        try:
            observed = json.loads(subprocess.check_output([python, '-I', '-c', command], env=clean_environment(),
                                                         timeout=20, text=True, stderr=subprocess.DEVNULL))
            if observed != {'python': runtime['python'], 'platform': runtime['platform'], 'packages': PACKAGES}:
                raise BackendUnavailable('Compatible verified offline runtime is required')
            self._temporary = _PrivateWork(self.release_root)
            self.temp_directory = self._temporary.path
            worker = self.release_root / 'backend/launcher/backend_runtime.py'
            args = [python, '-I', '-B', str(worker), '--worker']
            options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                             env=clean_environment(self.temp_directory), **options)
            # Worker is blocked on stdin until it belongs to the parent-held job.
            self._job = _WindowsChildJob(self._process)
            startup = {'release_root': str(self.release_root), 'ui_port': ui_port, 'revision': revision, 'token': self._token}
            self._process.stdin.write((json.dumps(startup)+'\n').encode('utf-8')); self._process.stdin.close()
            q = queue.Queue(maxsize=1)
            def receive():
                q.put(self._process.stdout.readline(4097))
            threading.Thread(target=receive, daemon=True).start()
            response = q.get(timeout=20)
            ready = json.loads(response)
            if (set(ready) != {'port','revision','offline'} or ready['revision'] != revision or ready['offline'] is not True
                    or type(ready['port']) is not int or not 1 <= ready['port'] <= 65535):
                raise BackendUnavailable('Clinical worker did not become ready')
            self._port = ready['port']
        except (BackendUnavailable, OSError, ValueError, subprocess.SubprocessError, queue.Empty):
            self.close()
            raise BackendUnavailable('Clinical worker runtime is unavailable') from None

    def request(self, path, payload):
        if self._closed or self._process is None or self._process.poll() is not None:
            raise BackendUnavailable('Clinical worker is not running')
        if path not in ALLOWED_ROUTES:
            return (503 if path == '/api/clinical-note/upload/interpret' else 404), {'error':'capability_not_available_offline'}
        if type(payload) is not dict:
            return 400, {'error':'JSON object required'}
        try:
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode('utf-8')
        except (TypeError, ValueError, UnicodeError):
            return 400, {'error':'invalid_json'}
        if len(body) > MAX_INPUT:
            return 413, {'error':'request_too_large'}
        connection = http.client.HTTPConnection('127.0.0.1', self._port, timeout=60)
        try:
            connection.request('POST', path, body=body, headers={
                'Content-Type':'application/json', 'Origin':f'http://127.0.0.1:{self._ui_port}',
                'X-Emergency-Local-Token':self._token, 'Sec-Fetch-Site':'same-origin'})
            response = connection.getresponse()
            raw = response.read(MAX_OUTPUT+1)
            if len(raw) > MAX_OUTPUT or not response.getheader('Content-Type','').startswith('application/json'):
                raise BackendUnavailable('Invalid bounded clinical response')
            result = json.loads(raw)
            if type(result) is not dict:
                raise BackendUnavailable('Invalid clinical response')
            return response.status, result
        except (OSError, ValueError, http.client.HTTPException):
            raise BackendUnavailable('Clinical worker transport failed') from None
        finally:
            connection.close()

    def close(self):
        if self._process is not None:
            if self._process.poll() is None:
                self._process.terminate()
                try:self._process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self._process.kill(); self._process.wait(timeout=3)
            if self._process.stdout:self._process.stdout.close()
            self._process = None
        if self._job is not None:
            self._job.close();self._job=None
        if self._temporary is not None:
            self._temporary.cleanup(); self._temporary = None
        self._token = None
        self._closed = True

    def __enter__(self):return self
    def __exit__(self, *_):self.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker',action='store_true')
    args=parser.parse_args()
    if not args.worker:parser.error('Start only through the verified local launcher')
    try:_worker()
    except Exception:
        # No submitted payload, environment, token or filesystem path is echoed.
        print('{"error":"offline_worker_unavailable"}',flush=True)
        sys.exit(1)
