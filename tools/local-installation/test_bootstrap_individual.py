import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import backend_runtime
import zipfile
from unittest.mock import patch
import bootstrap_individual as boot

class BootstrapTests(unittest.TestCase):
    def test_bootstrap_environment_preserves_user_paths_without_provider_secrets(self):
        with patch.dict(boot.os.environ,{'USERPROFILE':'C:/SyntheticUser','LOCALAPPDATA':'C:/SyntheticLocal',
                                        'HTTPS_PROXY':'PRIVATE','OPENAI_API_KEY':'PRIVATE','PYTHONPATH':'PRIVATE'}):
            env=boot.environment()
            self.assertEqual(env['USERPROFILE'],'C:/SyntheticUser')
            self.assertEqual(env['LOCALAPPDATA'],'C:/SyntheticLocal')
            self.assertFalse(any('PRIVATE' in x for x in env.values()))
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.root=Path(self.temporary.name)
        self.rows=[];self.data={}
        for name,version in boot.PACKAGES.items():
            filename=f'{name}-{version}-py3-none-any.whl';data=name.encode()
            self.rows.append({'file':filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            self.data['backend/wheels/'+filename]=data
        self.lock=self.root/'lock.json'
        self.lock.write_text(json.dumps({'schema':'emergency.bootstrap-crypto.v1','python':[3,12],
            'platform':'win-amd64','wheels':self.rows}))
    def tearDown(self):self.temporary.cleanup()
    def archive(self,changes=None):
        files=dict(self.data);files.update(changes or {})
        target=self.root/'package.zip'
        with zipfile.ZipFile(target,'w') as archive:
            for name,data in files.items():archive.writestr(name,data)
        return target
    def test_synthetic_verified_extraction_only_wheels(self):
        archive=self.archive({'backend/launcher/untrusted.py':b'raise Exception()'})
        requirements=boot.extract_verifier_wheels(archive,self.root/'out',self.lock)
        self.assertTrue(requirements.is_file())
        self.assertEqual(len(list(requirements.parent.glob('*.whl'))),3)
        self.assertFalse(list(requirements.parent.glob('*.py')))
        self.assertIn('--hash=sha256:',requirements.read_text())
    def test_tampered_wheel_rejected_before_destination_created(self):
        name=next(iter(self.data));archive=self.archive({name:b'BAD'})
        with self.assertRaises(ValueError):boot.extract_verifier_wheels(archive,self.root/'out',self.lock)
        self.assertFalse((self.root/'out').exists())
    def test_unsafe_archive_path_rejected(self):
        archive=self.archive({'../outside':b'bad'})
        with self.assertRaises(ValueError):boot.extract_verifier_wheels(archive,self.root/'out',self.lock)
        self.assertFalse((self.root/'outside').exists())
    def test_missing_dependency_rejected(self):
        del self.data[next(iter(self.data))]
        with self.assertRaises(ValueError):boot.extract_verifier_wheels(self.archive(),self.root/'out',self.lock)
    def test_independent_fingerprint_required_before_process(self):
        with patch.object(boot.subprocess,'check_output') as process:
            with self.assertRaises(ValueError):boot.run_install(self.root/'a',self.root/'s',self.root/'r',self.root/'p',self.root/'pub','')
            process.assert_not_called()
    def test_install_handoff_is_offline_and_uses_external_publisher(self):
        with patch.object(boot.subprocess,'check_output',return_value='[[3,12],"win-amd64"]'),\
             patch.object(boot,'prepare_verifier',return_value=self.root/'verifier.exe'),\
             patch.object(boot.subprocess,'run',return_value=type('Result',(),{'stdout':'{"version":"synthetic-v1","activated":false}'})()) as run:
            boot.run_install(self.root/'a',self.root/'s',self.root/'r',self.root/'p',self.root/'pub','a'*64)
        self.assertEqual(run.call_count,1)
        cli=run.call_args.args[0]
        self.assertIn('--expected-publisher-fingerprint',cli);self.assertIn('a'*64,cli)
        self.assertIn(str(self.root/'pub'),cli)

    def test_existing_actions_use_verified_persistent_runtime_without_archive(self):
        with patch.object(boot,'verified_verifier',return_value=self.root/'verifier.exe') as verify,\
             patch.object(boot.subprocess,'run') as run,patch.object(boot,'supervise_serve') as serve:
            boot.run_existing(self.root,'activate','synthetic-v1')
            boot.run_existing(self.root,'serve')
        self.assertEqual(verify.call_count,2)
        self.assertIn('activate',run.call_args_list[0].args[0])
        self.assertIn('serve',serve.call_args.args[0]);self.assertIn('--parent-gate',serve.call_args.args[0])

    @unittest.skipUnless(boot.os.name=='nt','Windows bootstrap Job containment')
    def test_bootstrap_job_assignment_failure_never_opens_start_gate(self):
        from unittest.mock import Mock
        process=Mock();process.stdin.closed=False
        with patch.object(boot.subprocess,'Popen',return_value=process),\
             patch.object(backend_runtime,'_WindowsChildJob',side_effect=OSError('synthetic')):
            with self.assertRaises(OSError):boot.supervise_serve(['synthetic'])
        process.stdin.write.assert_not_called();process.stdin.close.assert_called_once()

    @unittest.skipUnless(boot.os.name=='nt','Windows bootstrap Job containment')
    def test_bootstrap_job_precedes_gate_and_closes(self):
        from unittest.mock import Mock
        events=[];process=Mock();process.stdin.closed=False;process.wait.return_value=0
        process.stdin.write.side_effect=lambda value:events.append(('start',value))
        job=Mock();job.close.side_effect=lambda:events.append(('closed',))
        def assign(_):events.append(('assigned',));return job
        with patch.object(boot.subprocess,'Popen',return_value=process),\
             patch.object(backend_runtime,'_WindowsChildJob',side_effect=assign):boot.supervise_serve(['synthetic'])
        self.assertEqual(events,[('assigned',),('start',b'START\n'),('closed',)])

    @unittest.skipUnless(boot.os.name=='nt','Windows bootstrap real descendant containment')
    def test_bootstrap_parent_death_kills_owned_child_and_grandchild(self):
        import ctypes
        from ctypes import wintypes
        child="import sys,subprocess,os,json;assert sys.stdin.buffer.readline(7)==b'START\\n';p=subprocess.Popen([sys.executable,'-I','-B','-c','import time;time.sleep(60)']);print(json.dumps([os.getpid(),p.pid]),flush=True);p.wait()"
        helper="import sys;sys.path.insert(0,sys.argv[1]);import bootstrap_individual as b;b.supervise_serve([sys.executable,'-I','-B','-c',sys.argv[2]])"
        process=subprocess.Popen([sys.executable,'-I','-B','-c',helper,str(Path(boot.__file__).parent),child],
                                 stdout=subprocess.PIPE,text=True,env=boot.environment())
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        kernel.TerminateProcess.argtypes=[wintypes.HANDLE,wintypes.UINT]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handles=[]
        try:
            pids=json.loads(process.stdout.readline())
            handles=[kernel.OpenProcess(0x00100001,False,pid) for pid in pids]
            self.assertTrue(all(handles))
            process.kill();process.wait(timeout=10)
            for handle in handles:self.assertEqual(kernel.WaitForSingleObject(handle,10000),0)
        finally:
            if process.poll() is None:process.kill();process.wait(timeout=10)
            for handle in handles:
                if handle:
                    if kernel.WaitForSingleObject(handle,0)!=0:kernel.TerminateProcess(handle,1)
                    kernel.CloseHandle(handle)
            process.stdout.close()

    def test_persistent_verifier_extra_or_tampered_bytes_rejected(self):
        directory,fingerprint=boot.verifier_location(self.root)
        directory.mkdir(parents=True)
        python=directory/'Scripts/python.exe';python.parent.mkdir();python.write_bytes(b'FAKE')
        receipt={'fingerprint':fingerprint,'files':[{'path':'Scripts/python.exe','sha256':hashlib.sha256(b'FAKE').hexdigest()}],
                 'packages':boot.PACKAGES,'trust':'Local integrity only'}
        (directory/'INSTALLATION_RECEIPT.json').write_text(json.dumps(receipt))
        self.assertEqual(boot.verified_verifier(self.root),python)
        extra=directory/'Scripts/INSTALLATION_RECEIPT.json';extra.write_text('{}')
        with self.assertRaises(ValueError):boot.verified_verifier(self.root)
        extra.unlink();python.write_bytes(b'TAMPER')
        with self.assertRaises(ValueError):boot.verified_verifier(self.root)

if __name__=='__main__':unittest.main()
