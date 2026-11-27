import hashlib
import json
from pathlib import Path
import tempfile
import unittest
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
             patch.object(boot.subprocess,'run') as run:
            boot.run_existing(self.root,'activate','synthetic-v1')
            boot.run_existing(self.root,'serve')
        self.assertEqual(verify.call_count,2)
        self.assertIn('activate',run.call_args_list[0].args[0])
        self.assertIn('serve',run.call_args_list[1].args[0])

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
