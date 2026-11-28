"""Trusted external stdlib bootstrap: verify crypto wheels before loading verifier."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
import uuid

sys.path.insert(0,str(Path(__file__).resolve().parent))
import local_installation as local

PACKAGES={'cryptography':'50.0.2','cffi':'2.1.1','pycparser':'3.12'}

def environment():
    return {k:os.environ[k] for k in ('SystemRoot','WINDIR','COMSPEC','USERPROFILE','LOCALAPPDATA') if k in os.environ}

def load_lock(path):
    value=local.object_json(local.regular_bytes(path,16384))
    local.require(value.get('schema')=='emergency.bootstrap-crypto.v1' and value.get('python')==[3,12]
                  and value.get('platform')=='win-amd64','Unsupported bootstrap lock')
    wheels=value.get('wheels');local.require(type(wheels) is list and len(wheels)==3,'Incomplete verifier closure')
    found=set()
    for row in wheels:
        name=local.safe_name(row['file'])
        local.require('/' not in name and name.endswith('.whl'),'Invalid bootstrap wheel name')
        package,version=name.split('-')[:2]
        local.require(package in PACKAGES and version==PACKAGES[package] and package not in found,'Invalid verifier package')
        local.require(type(row['bytes']) is int and 0<row['bytes']<8*1024*1024
                      and type(row['sha256']) is str and re.fullmatch('[a-f0-9]{64}',row['sha256']), 'Invalid verifier identity')
        found.add(package)
    local.require(found==set(PACKAGES),'Incomplete verifier closure')
    return wheels

def extract_verifier_wheels(archive_path,destination,lock_path):
    """Only external-lock-approved bytes can become executable pip dependencies."""
    archive_path=local.no_links(archive_path);destination=local.no_links(destination)
    rows=load_lock(lock_path)
    local.require(not destination.exists(),'Verifier wheel directory already exists')
    local.preflight_zip(archive_path)
    expected={'backend/wheels/'+row['file']:row for row in rows}
    contents={}
    with zipfile.ZipFile(archive_path) as archive:
        names=set();total=0
        for info in archive.infolist():
            name=local.safe_name(info.filename)
            local.require(info.orig_filename==name and name.casefold() not in names,'Duplicate/noncanonical ZIP path')
            names.add(name.casefold())
            local.require(not info.is_dir() and stat.S_IFMT(info.external_attr>>16) in {0,stat.S_IFREG}
                          and not info.flag_bits&1,'Unsupported archive entry')
            total+=info.file_size
            local.require(info.file_size<=local.MAX_FILE and total<=local.MAX_TOTAL+local.MAX_MANIFEST,'Archive size limit')
            if name in expected:
                row=expected[name]
                local.require(info.file_size==row['bytes'],'Verifier wheel size differs')
                with archive.open(info) as stream:data=stream.read(row['bytes']+1)
                local.require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'Verifier wheel hash differs')
                contents[row['file']]=data
    local.require(len(contents)==3,'Verifier wheels missing')
    destination.mkdir(parents=True)
    for name,data in contents.items():(destination/name).write_bytes(data)
    requirements=[]
    for row in rows:
        name,version=row['file'].split('-')[:2]
        requirements.append(name+'=='+version+' --hash=sha256:'+row['sha256'])
    (destination/'requirements.lock').write_text('\n'.join(sorted(requirements))+'\n',encoding='ascii')
    return destination/'requirements.lock'

def verifier_location(root):
    lock=Path(__file__).with_name('bootstrap_crypto_lock.json')
    load_lock(lock)
    fingerprint=hashlib.sha256(local.regular_bytes(lock,16384)).hexdigest()
    return local.no_links(Path(root)/'bootstrap-verifiers'/fingerprint),fingerprint

def verified_verifier(root):
    directory,fingerprint=verifier_location(root)
    return verify_verifier_directory(directory,fingerprint)

def verify_verifier_directory(directory,fingerprint):
    from backend_bundle import verify_runtime
    directory=local.no_links(directory)
    receipt=local.object_json(local.regular_bytes(directory/'INSTALLATION_RECEIPT.json',8*1024*1024))
    local.require(set(receipt)=={'fingerprint','files','packages','trust'} and receipt['packages']==PACKAGES
                  and type(receipt['files']) is list,'Invalid verifier receipt')
    for row in receipt['files']:
        local.require(type(row) is dict and set(row)=={'path','sha256'}
                      and type(row['path']) is str and type(row['sha256']) is str
                      and bool(re.fullmatch('[a-f0-9]{64}',row['sha256'])),'Invalid verifier file identity')
    names=[local.safe_name(row['path']) for row in receipt['files']]
    local.require(len(names)==len(set(names)) and 'INSTALLATION_RECEIPT.json' not in names,'Invalid verifier receipt paths')
    actual=set()
    for path in directory.rglob('*'):
        local.no_links(path)
        if path.is_file() and path!=directory/'INSTALLATION_RECEIPT.json':actual.add(path.relative_to(directory).as_posix())
    local.require(actual==set(names),'Verifier file set differs')
    return verify_runtime(directory,fingerprint)

def prepare_verifier(archive,root,python):
    from backend_bundle import verify_runtime, _runtime_files
    with local.writer(root):
        directory,fingerprint=verifier_location(root)
        if directory.exists():return verified_verifier(root)
        directory.parent.mkdir(parents=True,exist_ok=True)
        # Equal length to final SHA-256 directory avoids changing Windows path
        # limits when publishing a venv with deeply nested pip cache filenames.
        stage=local.no_links(directory.parent/('stage-'+uuid.uuid4().hex+uuid.uuid4().hex[:27]))
        with tempfile.TemporaryDirectory(prefix='emergency-verifier-wheels-',ignore_cleanup_errors=True) as work:
            requirements=extract_verifier_wheels(archive,Path(work)/'wheels',Path(__file__).with_name('bootstrap_crypto_lock.json'))
            subprocess.run([str(python),'-I','-B','-m','venv',str(stage)],check=True,env=environment(),timeout=120)
            verifier=stage/'Scripts/python.exe'
            subprocess.run([str(verifier),'-I','-B','-m','pip','--isolated','install','--no-index',
                '--require-hashes','--only-binary=:all:','--no-compile','--find-links',str(Path(work)/'wheels'),
                '-r',str(requirements)],check=True,env=environment(),timeout=180)
            files=[]
            for path in _runtime_files(stage):
                data=local.regular_bytes(path)
                files.append({'path':path.relative_to(stage).as_posix(),'sha256':hashlib.sha256(data).hexdigest()})
            (stage/'INSTALLATION_RECEIPT.json').write_bytes(local.canonical_json({
                'fingerprint':fingerprint,'files':files,'packages':PACKAGES,
                'trust':'Local integrity receipt; not protection against a malicious process of the same OS user'}))
            verify_verifier_directory(stage,fingerprint)
            # Failed stages remain public-only for inspection; never select them.
            # Publish only a complete receipt-verified directory while holding writer.
            os.replace(stage,directory)
        return verified_verifier(root)

def run_existing(root,action,version=None):
    local.require(action in {'activate','serve','rollback'},'Invalid installed action')
    local.require(action=='serve' or bool(version),'Exact installed version required')
    command=[str(verified_verifier(root)),'-I','-B',str(Path(__file__).with_name('individual_cli.py')),
             action,'--root',str(root)]
    if action!='serve':command+=['--version',version]
    if action=='serve':
        command+=['--parent-gate']
        supervise_serve(command)
    else:subprocess.run(command,check=True,env=environment())

def supervise_serve(command):
    from backend_runtime import _WindowsChildJob
    process=subprocess.Popen(command,stdin=subprocess.PIPE,env=environment(),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    job=None
    try:
        job=_WindowsChildJob(process) if os.name=='nt' else None
        process.stdin.write(b'START\n');process.stdin.flush()
        code=process.wait()
        if code:raise subprocess.CalledProcessError(code,command)
    finally:
        if process.stdin and not process.stdin.closed:process.stdin.close()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill();process.wait(timeout=5)
        if job:job.close()

def run_install(archive,signature,root,python,publisher,fingerprint):
    local.require(bool(re.fullmatch('[a-f0-9]{64}',fingerprint)),'Independent publisher fingerprint required')
    for path in (archive,signature,publisher,python):local.no_links(path)
    probe=subprocess.check_output([str(python),'-I','-B','-c',
        'import sys,sysconfig,json;print(json.dumps([list(sys.version_info[:2]),sysconfig.get_platform()]))'],
        env=environment(),timeout=20,text=True)
    local.require(json.loads(probe)==[[3,12],'win-amd64'],'Installed Python 3.12 x64 required')
    verifier=prepare_verifier(archive,root,python)
    result=subprocess.run([str(verifier),'-I','-B',str(Path(__file__).with_name('individual_cli.py')),
        'install','--archive',str(archive),'--signature',str(signature),'--root',str(root),
        '--python',str(python),'--publisher-file',str(publisher),
        '--expected-publisher-fingerprint',fingerprint],check=True,env=environment(),timeout=300,
        capture_output=True,text=True)
    installed=json.loads(result.stdout)
    local.require(type(installed) is dict and type(installed.get('version')) is str,'Missing installed version')
    installed['next_activate']=['START_INDIVIDUAL.ps1','-Python',str(python),'-InstallRoot',str(root),'-Action','activate','-Version',installed['version']]
    installed['next_serve']=['START_INDIVIDUAL.ps1','-Python',str(python),'-InstallRoot',str(root),'-Action','serve']
    print(json.dumps(installed))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action',choices=['install','activate','serve','rollback'],default='install')
    parser.add_argument('--root',required=True)
    parser.add_argument('--version')
    for name in ('archive','signature','python','publisher-file','expected-publisher-fingerprint'):
        parser.add_argument('--'+name)
    args=parser.parse_args()
    if args.action!='install':
        run_existing(Path(args.root).absolute(),args.action,args.version);return
    local.require(all(getattr(args,name) for name in ('archive','signature','python','publisher_file','expected_publisher_fingerprint')),'Install arguments required')
    run_install(Path(args.archive).absolute(),Path(args.signature).absolute(),Path(args.root).absolute(),
                Path(args.python).absolute(),Path(args.publisher_file).absolute(),args.expected_publisher_fingerprint)

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,subprocess.SubprocessError,zipfile.BadZipFile):
        print('{"status":"bootstrap_rejected","clinical":"CLINICALLY_PENDING","release":"NO_GO_CLINICAL_RELEASE"}',file=sys.stderr)
        sys.exit(1)
