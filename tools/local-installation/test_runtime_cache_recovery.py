"""Cache repair mechanics with inert files; strict runtime verifier remains real."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import backend_bundle as bundle
import individual_cli as cli
import local_installation as local
import stable_launcher

class RuntimeCacheRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'installation';self.root.mkdir()
        self.release=Path(self.temp.name)/'authenticated-release';self.release.mkdir()
        self.fingerprint='a'*64
        self.target=self.root/'runtimes'/self.fingerprint
        self.make_runtime(self.target)
        self.verify=patch.object(cli.auth,'verify_version',return_value=(self.release,{}, {}, {})).start()
        self.addCleanup(patch.stopall)
        patch.object(cli,'runtime_fingerprint',return_value=self.fingerprint).start()
        self.installer=patch.object(cli,'install_runtime',side_effect=lambda release,stage,python:self.make_runtime(stage)).start()

    def make_runtime(self,directory):
        (directory/'Scripts').mkdir(parents=True)
        data=b'INERT_SYNTHETIC_PYTHON_FILE_NEVER_EXECUTED'
        (directory/'Scripts/python.exe').write_bytes(data)
        (directory/'INSTALLATION_RECEIPT.json').write_text(json.dumps({
            'fingerprint':self.fingerprint,'files':[{'path':'Scripts/python.exe','sha256':hashlib.sha256(data).hexdigest()}],
            'packages':{}}),encoding='utf8')
        return directory/'Scripts/python.exe'

    def contaminate(self):
        extra=self.target/'Lib/site-packages/reportlab/__pycache__/__init__.cpython-312.pyc'
        extra.parent.mkdir(parents=True)
        extra.write_bytes(b'INERT_UNMANIFESTED_BYTECODE_NOT_EXECUTABLE')
        return extra

    def tree_bytes(self,path):
        return {p.relative_to(path).as_posix():p.read_bytes() for p in path.rglob('*') if p.is_file()}

    def test_extra_pyc_rejected_then_rebuilt_and_original_quarantined(self):
        self.contaminate();before=self.tree_bytes(self.target)
        with self.assertRaisesRegex(local.ReleaseError,'Runtime file set changed'):
            bundle.verify_runtime(self.target,self.fingerprint)
        result=cli.prepare_runtime(self.root,'signed-version',Path('trusted-python.exe'))
        self.assertEqual(result,self.target/'Scripts/python.exe')
        self.assertEqual(bundle.verify_runtime(self.target,self.fingerprint),result)
        self.installer.assert_called_once()
        retained=list((self.root/'runtimes').glob('retained-*'))
        self.assertEqual(len(retained),1)
        self.assertEqual(self.tree_bytes(retained[0]),before)
        self.assertFalse((self.target/'Lib').exists())
        self.assertEqual(self.installer.call_args.args[0],self.release)

    def test_live_runtime_lease_prevents_rebuild_or_move(self):
        self.contaminate();before=self.tree_bytes(self.target)
        lease=stable_launcher.RuntimeLease(self.root)
        try:
            with self.assertRaisesRegex(local.ReleaseError,'already has an active runtime'):
                cli.prepare_runtime(self.root,'signed-version',Path('trusted-python.exe'))
        finally:lease.close()
        self.installer.assert_not_called()
        self.assertEqual(self.tree_bytes(self.target),before)
        self.assertEqual(list((self.root/'runtimes').glob('retained-*')),[])

    def test_failed_stage_preserves_prior_cache_without_publication(self):
        self.contaminate();before=self.tree_bytes(self.target)
        def fail(release,stage,python):
            stage.mkdir()
            (stage/'INCOMPLETE').write_bytes(b'INERT_PARTIAL_STAGE')
            raise OSError('synthetic stage failure')
        self.installer.side_effect=fail
        with self.assertRaisesRegex(OSError,'synthetic stage failure'):
            cli.prepare_runtime(self.root,'signed-version',Path('trusted-python.exe'))
        self.assertEqual(self.tree_bytes(self.target),before)
        self.assertEqual(list((self.root/'runtimes').glob('retained-*')),[])
        self.assertEqual(len(list(self.root.glob('runtime-stage-*'))),1)

    def test_healthy_cache_never_rebuilt_or_needs_runtime_lease(self):
        before=self.tree_bytes(self.target)
        with patch.object(stable_launcher,'RuntimeLease',side_effect=AssertionError('Healthy cache must not require runtime downtime')):
            result=cli.prepare_runtime(self.root,'signed-version',Path('trusted-python.exe'))
        self.assertEqual(result,self.target/'Scripts/python.exe')
        self.installer.assert_not_called()
        self.assertEqual(self.tree_bytes(self.target),before)

    def test_failed_publish_restores_prior_cache_and_retains_stage(self):
        self.contaminate();before=self.tree_bytes(self.target)
        replace=os.replace
        def guarded(source,destination):
            if Path(source).name.startswith('runtime-stage-') and Path(destination)==self.target:
                raise OSError('synthetic publication failure')
            return replace(source,destination)
        with patch.object(cli.os,'replace',side_effect=guarded):
            with self.assertRaisesRegex(OSError,'synthetic publication failure'):
                cli.prepare_runtime(self.root,'signed-version',Path('trusted-python.exe'))
        self.assertEqual(self.tree_bytes(self.target),before)
        self.assertEqual(len(list(self.root.glob('runtime-stage-*'))),1)
        self.assertEqual(list((self.root/'runtimes').glob('retained-*')),[])
        with self.assertRaisesRegex(local.ReleaseError,'Runtime file set changed'):
            bundle.verify_runtime(self.target,self.fingerprint)

    def test_permission_error_is_not_treated_as_repairable(self):
        with patch.object(cli,'verify_runtime',side_effect=PermissionError('synthetic permission denied')):
            with self.assertRaises(PermissionError):
                cli.prepare_runtime(self.root,'signed-version',Path('trusted-python.exe'))
        self.installer.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)

