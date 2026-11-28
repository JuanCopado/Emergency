"""Synthetic offline runtime controls; canonical clinical engines are not altered."""
import base64
import hashlib
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import unittest
import zipfile
from unittest.mock import patch

import backend_bundle as bundle
import backend_runtime as runtime


class BackendWheelPinTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.root=Path(self.temporary.name)
        self.pins={}
        for name,version in bundle.PACKAGES.items():
            data=('SYNTHETIC '+name).encode()
            filename=name.replace('-','_')+'-'+version+'-py3-none-any.whl'
            (self.root/filename).write_bytes(data)
            self.pins[name]=(version,hashlib.sha256(data).hexdigest())
    def tearDown(self):self.temporary.cleanup()
    def test_complete_trusted_fixture_passes(self):
        self.assertEqual(len(bundle.collect_wheels(self.root,self.pins)),6)
    def test_only_root_runtime_receipt_is_exempt_from_inventory(self):
        root_receipt=self.root/'INSTALLATION_RECEIPT.json';root_receipt.write_text('{}')
        nested=self.root/'nested/INSTALLATION_RECEIPT.json';nested.parent.mkdir();nested.write_text('{}')
        self.assertNotIn(root_receipt,bundle._runtime_files(self.root))
        self.assertIn(nested,bundle._runtime_files(self.root))
    def test_correct_wheel_name_with_inert_or_modified_bytes_rejected(self):
        next(self.root.glob('*.whl')).write_bytes(b'INERT_AUDIT_BYTES_NOT_A_WHEEL')
        with self.assertRaises(ValueError):bundle.collect_wheels(self.root,self.pins)
    def test_missing_and_extra_wheels_rejected(self):
        existing=next(self.root.glob('*.whl'));data=existing.read_bytes();existing.unlink()
        with self.assertRaises(ValueError):bundle.collect_wheels(self.root,self.pins)
        existing.write_bytes(data);(self.root/'extra-1.0-py3-none-any.whl').write_bytes(b'EXTRA')
        with self.assertRaises(ValueError):bundle.collect_wheels(self.root,self.pins)
    def test_committed_lock_strictly_requires_all_six_exact_versions(self):
        raw='\n'.join(f'{name}=={version} --hash=sha256:{digest}' for name,(version,digest) in self.pins.items()).encode()
        self.assertEqual(bundle.read_wheel_pins(raw),self.pins)
        for invalid in (raw+b'\n'+raw.splitlines()[0],b'\n'.join(raw.splitlines()[:-1]),raw.replace(b'50.0.2',b'50.0.1')):
            with self.assertRaises(ValueError):bundle.read_wheel_pins(invalid)
    def test_collector_reads_lock_from_same_git_revision(self):
        path='tools/local-installation/requirements-runtime-ci.lock';revision='a'*40;calls=[]
        def git(root,*args):
            calls.append(args)
            if args[0]=='ls-tree':return path.encode()
            if args==('show',revision+':'+path):return b'INERT_UNREVIEWED_LOCK'
            raise AssertionError(args)
        with patch.object(bundle,'_git',side_effect=git):
            with self.assertRaises(ValueError):bundle.collect_backend(self.root,self.root,revision)
        self.assertIn(('show',revision+':'+path),calls)


class BackendBoundaryUnitTests(unittest.TestCase):
    @unittest.skipUnless(os.name=='nt','Windows user environment')
    def test_clean_child_resolves_home_and_namespace_in_localappdata(self):
        module=str(Path(runtime.__file__).resolve().parent)
        code="import sys,json,os;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from backend_runtime import _PrivateWork;print(json.dumps({'home':str(Path.home()),'namespace':str(_PrivateWork.namespace(Path(os.environ['USERPROFILE'])/'synthetic-install')),'local':os.environ['LOCALAPPDATA']}))"
        result=json.loads(subprocess.check_output([sys.executable,'-I','-B','-c',code,module],
                                                env=bundle.clean_environment(),text=True))
        self.assertEqual(Path(result['home']),Path(os.environ['USERPROFILE']))
        self.assertTrue(Path(result['namespace']).is_relative_to(Path(result['local'])/'Emergency/PrivateWork'))

    def test_localappdata_namespace_does_not_eagerly_evaluate_fallback(self):
        with patch.dict(os.environ,{'LOCALAPPDATA':str(Path(tempfile.gettempdir())/'synthetic-local')}),\
             patch.object(runtime.tempfile,'gettempdir',side_effect=RuntimeError('fallback must not run')):
            self.assertIn('synthetic-local',str(runtime._PrivateWork.namespace(Path.cwd())))

    def test_environment_never_inherits_provider_proxy_or_python_keys(self):
        with patch.dict(os.environ, {'CLINICAL_NOTE_VISION_API_KEY':'PRIVATE','HTTPS_PROXY':'PRIVATE',
                                     'PYTHONPATH':'PRIVATE','SONAR_TOKEN':'PRIVATE'}):
            clean=bundle.clean_environment('/owned/temp')
            self.assertTrue(all('PRIVATE' not in str(v) for v in clean.values()))
            self.assertEqual(clean['TMP'],'/owned/temp')
            self.assertEqual(clean['PYTHONDONTWRITEBYTECODE'],'1')

    def test_offline_audit_denies_tcp_dns_udp_and_process_without_network(self):
        module=str(Path(runtime.__file__).resolve().parent)
        code='''import sys,socket,subprocess,json
sys.path.insert(0,sys.argv[1]);from backend_runtime import install_offline_policy
install_offline_policy();results=[]
for f in [lambda:socket.create_connection(('198.51.100.1',443),timeout=.01),lambda:socket.getaddrinfo('example.invalid',443),lambda:socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(b'x',('198.51.100.1',1)),lambda:subprocess.run([sys.executable,'-c','pass'])]:
 try:f();results.append(False)
 except PermissionError:results.append(True)
print(json.dumps(results))
'''
        output=subprocess.check_output([sys.executable,'-I','-c',code,module],text=True)
        self.assertEqual(json.loads(output),[True]*4)

    def test_route_allowlist_keeps_existing_deterministic_contracts_only(self):
        self.assertIn('/api/clinical-note/export',runtime.ALLOWED_ROUTES)
        self.assertIn('/api/clinical-note/upload/prepare',runtime.ALLOWED_ROUTES)
        self.assertNotIn('/api/clinical-note/upload/interpret',runtime.ALLOWED_ROUTES)
        self.assertFalse(any('blood-gas' in p for p in runtime.ALLOWED_ROUTES))
        self.assertEqual(runtime.MAX_INPUT,26_165_824)
        self.assertEqual(runtime.MAX_OUTPUT,32*1024*1024)

    def test_private_work_reaps_only_marked_stale_and_preserves_live_unmarked(self):
        with tempfile.TemporaryDirectory() as base, patch.dict(os.environ,{'LOCALAPPDATA':base}):
            live=runtime._PrivateWork(Path(base)/'installation')
            stale=runtime._PrivateWork(Path(base)/'installation')
            (stale.path/'synthetic.tmp').write_text('SYNTHETIC')
            stale.lease.close()  # Simulates OS release after owner death.
            unmarked=live.root/('f'*32);unmarked.mkdir()
            (unmarked/'export.txt').write_text('USER CONTROLLED TEST')
            lease=runtime._WorkLease(live.root/'leases'/(unmarked.name+'.lock'));lease.close()
            following=runtime._PrivateWork(Path(base)/'installation')
            try:
                self.assertFalse(stale.path.exists())
                self.assertTrue(live.path.is_dir())
                self.assertTrue((unmarked/'export.txt').is_file())
            finally:following.cleanup();live.cleanup()

    def test_private_namespace_is_stable_across_installed_release_update(self):
        with tempfile.TemporaryDirectory() as base, patch.dict(os.environ,{'LOCALAPPDATA':base}):
            installation=Path(base)/'installation'
            first=runtime._PrivateWork.namespace(installation/'releases'/'release-a')
            second=runtime._PrivateWork.namespace(installation/'releases'/'release-b')
            self.assertEqual(first,second)
            self.assertNotEqual(first,runtime._PrivateWork.namespace(Path(base)/'standalone-fixture'))


@unittest.skipUnless(os.environ.get('EMERGENCY_BACKEND_RELEASE') and os.environ.get('EMERGENCY_BACKEND_PYTHON'),
                     'Requires a physically bundled backend and its offline installed compatible Python runtime')
class ActualBundledBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release=Path(os.environ['EMERGENCY_BACKEND_RELEASE'])
        cls.python=Path(os.environ['EMERGENCY_BACKEND_PYTHON'])
        cls.contract=bundle.verify_backend(cls.release)
        cls.revision=cls.contract['source_sha']
        cls.session=runtime.BackendSession(cls.release,15877,cls.revision,cls.python)

    @classmethod
    def tearDownClass(cls):cls.session.close()

    def test_catalogs_real_canonical_counts_and_sources(self):
        status,scores=self.session.request('/api/clinical-scores/catalog',{})
        self.assertEqual(status,200);self.assertEqual(scores['total_formulas'],45)
        self.assertTrue(scores['scores']);self.assertEqual(scores['clinical_status'],'CLINICALLY_PENDING')
        status,acute=self.session.request('/api/acute-medications/catalog',{})
        self.assertEqual(status,200);self.assertTrue(acute['regimens'])
        self.assertTrue(all(r['source']['body'] for r in acute['regimens']))
        status,therapy=self.session.request('/api/clinical-note/therapy/catalog',{})
        self.assertEqual(status,200);self.assertTrue(therapy['modules'])

    def test_score_calculation_uses_original_source_revision_and_engine(self):
        status,catalog=self.session.request('/api/clinical-scores/catalog',{})
        body={'revision':catalog['revision'],'score_id':'news2','values':{
            'respiratory_rate':16,'spo2_percent':98,'supplemental_oxygen':False,
            'systolic_bp_mmHg':120,'pulse_bpm':70,'consciousness':'alert',
            'temperature_c':37,'spo2_scale':1}}
        status,result=self.session.request('/api/clinical-scores/calculate',body)
        self.assertEqual(status,200)
        self.assertEqual(result['score_id'],'news2')
        self.assertEqual(result['result']['total'],0)
        bad=dict(body,revision='0'*64)
        status,invalid=self.session.request('/api/clinical-scores/calculate',bad)
        self.assertEqual(status,422);self.assertNotIn('0'*64,json.dumps(invalid))

    def test_plain_document_import_preparation_and_privacy_boundary(self):
        body={'filename':'synthetic.txt','mime_type':'text/plain','content_base64':base64.b64encode(b'Synthetic educational case only.').decode()}
        status,prepared=self.session.request('/api/clinical-note/upload/prepare',body)
        self.assertEqual(status,200);self.assertEqual(prepared['processing']['status'],'text_extracted')
        self.assertEqual(prepared['extracted']['official_report'],'Synthetic educational case only.')
        status,result=self.session.request('/api/clinical-note/upload/interpret',{})
        self.assertEqual(status,503);self.assertEqual(result['error'],'capability_not_available_offline')

    def test_note_exports_pdf_docx_json_with_original_review_gates(self):
        status,note=self.session.request('/api/clinical-note/new',{'age_years':45,'language':'es-ES'})
        self.assertEqual(status,200)
        # Existing new endpoint returns the canonical note, not an invented clinical case.
        if 'note' in note:note=note['note']
        status,blocked=self.session.request('/api/clinical-note/export',{'note':note,'format':'pdf'})
        self.assertEqual(status,422)
        note['privacy'].update(direct_identifiers_removed=True,free_text_screened=True,
                               source_metadata_checked=True,burned_in_identifiers_checked=True)
        note['clinician_validation'].update(reviewed=True,reviewer_role='treating_clinician')
        for fmt,magic in [('pdf',b'%PDF'),('docx',b'PK'),('json',b'{')]:
            with self.subTest(format=fmt):
                status,export=self.session.request('/api/clinical-note/export',{'note':note,'format':fmt})
                self.assertEqual(status,200)
                raw=base64.b64decode(export['content_base64']);self.assertTrue(raw.startswith(magic))
                if fmt=='docx':self.assertIn('word/document.xml',zipfile.ZipFile(io.BytesIO(raw)).namelist())
                if fmt=='json':self.assertEqual(json.loads(raw),note)

    def test_direct_process_port_rejects_missing_wrong_tokens_foreign_origins(self):
        for headers in [
            {'Origin':'http://127.0.0.1:15877'},
            {'Origin':'http://127.0.0.1:15877','X-Emergency-Local-Token':'0'*64},
            {'Origin':'https://foreign.invalid','X-Emergency-Local-Token':self.session._token},
        ]:
            connection=http.client.HTTPConnection('127.0.0.1',self.session._port,timeout=10)
            try:
                connection.request('POST','/api/clinical-note/new',body=b'{}',headers={'Content-Type':'application/json',**headers})
                response=connection.getresponse();self.assertIn(response.status,(401,403));response.read()
            finally:connection.close()

    def test_oversized_input_and_invalid_tree_fail_without_echo(self):
        status,body=self.session.request('/api/clinical-note/new',{'x':'PRIVATE-SYNTHETIC-MARKER'*(runtime.MAX_INPUT//24+1)})
        self.assertEqual(status,413);self.assertNotIn('PRIVATE',json.dumps(body))
        self.assertEqual(self.session.request('/api/clinical-note/new',{'x':float('nan')})[0],400)
        self.assertEqual(self.session.request('/api/unknown',{})[0],404)

    def test_21_mib_json_frame_preserves_canonical_transport_capacity(self):
        status,body=self.session.request('/api/clinical-note/new',{'synthetic_padding':'x'*(21*1024*1024)})
        self.assertEqual(status,200)
        self.assertNotIn('synthetic_padding',body)

    def test_worker_temp_cleanup_and_no_artifact_token_or_bytecode(self):
        with runtime.BackendSession(self.release,15878,self.revision,self.python) as worker:
            temporary=worker.temp_directory
            self.assertTrue(temporary.is_dir())
            private_token=worker._token.encode()
            self.assertTrue(all(private_token not in p.read_bytes() for p in (self.release/'backend').rglob('*') if p.is_file()))
        self.assertFalse(temporary.exists())
        self.assertFalse(list((self.release/'backend').rglob('__pycache__')))

    @unittest.skipUnless(os.name=='nt','Windows Job Object parent-death containment')
    def test_parent_abrupt_exit_kills_only_its_owned_worker(self):
        code='''import sys,json,os
sys.path.insert(0,sys.argv[1]);from backend_runtime import BackendSession
s=BackendSession(sys.argv[2],15879,sys.argv[3],sys.argv[4])
print(json.dumps({'pid':s._process.pid,'temporary':str(s.temp_directory)}),flush=True)
os._exit(0)
'''
        helper=subprocess.Popen([str(self.python),'-I','-B','-c',code,str(Path(runtime.__file__).parent),
                                 str(self.release),self.revision,str(self.python)],stdout=subprocess.PIPE,text=True)
        owned=json.loads(helper.stdout.readline());helper.wait(timeout=25);helper.stdout.close()
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(0x00100000,False,owned['pid'])
        if handle:
            try:self.assertEqual(kernel.WaitForSingleObject(handle,10000),0)
            finally:kernel.CloseHandle(handle)
        temporary=Path(owned['temporary'])
        self.assertEqual(temporary.parent,runtime._PrivateWork.namespace(self.release))
        with runtime.BackendSession(self.release,15880,self.revision,self.python) as restarted:
            self.assertFalse(temporary.exists())
            self.assertTrue(self.session.temp_directory.exists())
            self.assertTrue(restarted.temp_directory.exists())


if __name__=='__main__':unittest.main(verbosity=2)

