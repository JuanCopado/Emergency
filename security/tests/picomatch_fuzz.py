#!/usr/bin/env python3
"""Read-only bounded picomatch/Rollup probes. Python stdlib + an installed Node.
Windows: hard Job Object committed-memory cap; POSIX: RLIMIT_AS + RLIMIT_CPU.
Node heap cap is additional, not a claim that heap == process RSS.
Known audited dependencies only: resource isolation is not a filesystem/network sandbox.
"""
import argparse, collections, ctypes, hashlib, json, os, random, shutil, signal
import subprocess, sys, tempfile, time
from pathlib import Path

CHILD = r'''
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', data => input += data);
process.stdin.on('end', async () => {
  const task = JSON.parse(input);
  const stage = value => console.log(JSON.stringify({stage:value,child_ms:Math.round(performance.now()*100)/100}));
  stage('loading');
  try {
    if (task.kind.startsWith('rollup')) {
      const path = require('node:path');
      const rollup = require(task.module);
      stage('rollup-call');
      if (task.kind === 'rollup-filter') {
        const filter = rollup.createFilter(task.pattern, null, {resolve:false});
        stage('matching');
        console.log(JSON.stringify({kind:'RESULT', match:filter(task.subject)}));
      } else {
        const id = path.join(process.cwd(), task.subject);
        const pattern = path.join(process.cwd(), task.pattern).replaceAll('\\','/');
        let transformed = 0;
        const bundle = await rollup.rollup({input:id, onLog(){}, plugins:[{
          name:'audit-synthetic-only', resolveId(){return id;},
          load(){return 'export const synthetic = 1;';},
          transform:{filter:{id:pattern}, handler(code){transformed++;return code;}}
        }]});
        await bundle.close();
        console.log(JSON.stringify({kind:'RESULT', transformed}));
      }
    } else {
      const pm = require(task.module), options = task.options;
      stage('compiling');
      let result;
      if (task.api === 'isMatch') {
        stage('compile-match'); result = pm.isMatch(task.subject, task.pattern, options);
      } else {
        let matcher;
        if (task.api === 'makeRe') {
          const re = pm.makeRe(task.pattern, options); matcher = value => re.test(value);
        } else if (task.api === 'parse' || task.api === 'parser') {
          const state = task.api === 'parse' ? pm.parse(task.pattern, options) : require(task.module + '/lib/parse.js')(task.pattern, options);
          const re = pm.compileRe(state, options); matcher = value => re.test(value);
        } else matcher = pm(task.api === 'array' ? [task.pattern,'**/*.synthetic'] : task.pattern, options);
        stage('matching'); result = matcher(task.subject);
      }
      console.log(JSON.stringify({kind:'RESULT', match:result}));
    }
  } catch(error) {
    console.log(JSON.stringify({kind:(String(error.code || '').startsWith('ERR_PICOMATCH_') || (error.code === 'PLUGIN_ERROR' && String(error.message).startsWith('Temporary picomatch policy:'))) ? 'GUARD_REJECT' : 'ERROR', code:error.code || error.name, message:String(error.message).slice(0,160)}));
  }
});
'''

def sha(data): return hashlib.sha256(data).hexdigest()

class WindowsJob:
    def __init__(self, process, memory):
        from ctypes import wintypes as w
        class Basic(ctypes.Structure):
            _fields_=[('ProcessTime',ctypes.c_int64),('JobTime',ctypes.c_int64),('Flags',w.DWORD),('MinWS',ctypes.c_size_t),('MaxWS',ctypes.c_size_t),('Active',w.DWORD),('Affinity',ctypes.c_size_t),('Priority',w.DWORD),('Scheduling',w.DWORD)]
        class IO(ctypes.Structure):
            _fields_=[(n,ctypes.c_uint64) for n in ['ReadOps','WriteOps','OtherOps','ReadBytes','WriteBytes','OtherBytes']]
        class Extended(ctypes.Structure):
            _fields_=[('Basic',Basic),('IO',IO),('ProcessMemory',ctypes.c_size_t),('JobMemory',ctypes.c_size_t),('PeakProcess',ctypes.c_size_t),('PeakJob',ctypes.c_size_t)]
        self.kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR];self.kernel.CreateJobObjectW.restype=w.HANDLE
        self.kernel.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
        self.kernel.CloseHandle.argtypes=[w.HANDLE]
        self.handle=self.kernel.CreateJobObjectW(None,None)
        if not self.handle:raise OSError(ctypes.get_last_error(),'CreateJobObject failed')
        info=Extended();info.Basic.Flags=0x100|0x200|0x2000|0x8;info.Basic.Active=1
        info.ProcessMemory=memory;info.JobMemory=memory
        if not self.kernel.SetInformationJobObject(self.handle,9,ctypes.byref(info),ctypes.sizeof(info)):
            self.close();raise OSError(ctypes.get_last_error(),'Memory-limit setup failed')
        if not self.kernel.AssignProcessToJobObject(self.handle,int(process._handle)):
            self.close();raise OSError(ctypes.get_last_error(),'Cannot attach isolated process; refusing unrestricted execution')
    def close(self):
        if self.handle:self.kernel.CloseHandle(self.handle);self.handle=None


def run_probe(task, args, directory, remaining):
    env={k:v for k,v in os.environ.items() if k.upper() in {'PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','LANG'}}
    env['NODE_NO_WARNINGS']='1'
    kwargs={'cwd':directory,'stdin':subprocess.PIPE,'stdout':subprocess.PIPE,'stderr':subprocess.PIPE,'env':env}
    if os.name=='nt':kwargs['creationflags']=subprocess.CREATE_NO_WINDOW
    else:
        import resource
        def limits():
            cap=args.virtual_mib*1024*1024
            resource.setrlimit(resource.RLIMIT_AS,(cap,cap));resource.setrlimit(resource.RLIMIT_CPU,(2,2))
        kwargs.update(start_new_session=True,preexec_fn=limits)
    started=time.monotonic();process=subprocess.Popen([args.node,'--max-old-space-size='+str(args.heap_mib),'-e',CHILD],**kwargs)
    job=None;timed_out=False
    try:
        # The child waits for stdin. No target module runs before memory limits are attached.
        if os.name=='nt':job=WindowsJob(process,args.job_mib*1024*1024)
        try:out,err=process.communicate(json.dumps(task).encode(),timeout=min(args.timeout_ms/1000,remaining))
        except subprocess.TimeoutExpired:
            timed_out=True
            if os.name=='nt':process.kill()
            else:os.killpg(process.pid,signal.SIGKILL)
            out,err=process.communicate(timeout=5)
    except BaseException:
        process.kill();process.communicate(timeout=5);raise
    finally:
        if job:job.close()
        elif os.name!='nt':
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
    events=[]
    for line in out.decode('utf-8',errors='replace').splitlines():
        try:events.append(json.loads(line))
        except json.JSONDecodeError:pass
    final=next((e for e in reversed(events) if 'kind' in e),{})
    last_stage=next((e['stage'] for e in reversed(events) if 'stage' in e),'startup')
    status='TIMEOUT' if timed_out else final.get('kind','RESOURCE_OR_PROCESS_ERROR')
    return {**task,'status':status,'stage':last_stage,'stage_times':[e for e in events if 'stage' in e],'exit':process.returncode,'elapsed_ms':round((time.monotonic()-started)*1000,2),'result':final,'stderr_tail':err.decode('utf-8',errors='replace')[-240:] if not final else ''}


def tasks_for(app, temporary, args):
    config=json.loads((app.parent/'security/picomatch-mitigation.json').read_text(encoding='utf-8-sig'))
    targets=[];inventory=[];snapshot={};controls={}
    for spec in config['targets']:
        filename=app/spec['path'];digest=sha(filename.read_bytes())
        if digest != spec['patched_sha256']:raise ValueError('Guard missing or unknown dependency bytes: '+str(filename))
        snapshot[str(filename)]=digest
        if not spec['path'].endswith('/lib/parse.js'):continue
        package=app/spec['package'];version=spec['version']
        inventory.append({'package':str(package),'version':version,'parse_sha256':digest,'known_guard_installed':True})
        targets.append({'label':'installed-'+spec['package'],'module':str(package)})
        if version in controls:continue
        control=Path(temporary)/('pristine-'+version);shutil.copytree(package,control)
        for entry in config['targets']:
            if entry['package']!=spec['package']:continue
            p=control/Path(entry['path']).relative_to(entry['package']);text=p.read_text(encoding='utf-8')
            if not text.startswith(entry['header']):raise ValueError('Missing reviewed policy binding')
            text=text[len(entry['header']):]
            for old,new,count in reversed(entry['replacements']):
                if text.count(new)!=count:raise ValueError('Ambiguous reverse patch')
                text=text.replace(new,old)
            if sha(text.encode())!=entry['original_sha256']:raise ValueError('Cannot reconstruct exact original control')
            p.write_bytes(text.encode())
        controls[version]={'label':'original-control-'+version,'module':str(control)}
    targets.extend(controls.values())
    corpus=['+(*a)','+(*)z','*(*)z','**/+(*a)','{+(*a),b}','@(+(a))','!(*a)+(a)','?(*a)*(*a)','\\\\+(*a)','+(?*a)','*(?*a)','[+](*a)','+\\(*a\\)','@(*a|*b)*','@(*a|*a|*a)','*([0-9]).txt','+([a-z]).js','x/*(a)/y','a+(b)','?(a|*)+(b)','(a+)+b','(a|aa)+b','(a*)*b','*a*a*a*a*a*a*a*a*a*b','*.txt','**/*.{js,ts}','[ab]*','{a,b}','a/b','./a','!(a)','?(a)','@(a|b)','\\+(a)','[','(',']','}',')','|','.','/','!','?','+','*','@','{','\\']
    rng=random.Random(args.seed);alphabet=list('+*?@!()|[]{}\\./ab,')
    for _ in range(96):
        pattern=rng.choice(corpus[:25]);position=rng.randrange(len(pattern)+1)
        if rng.randrange(3)==0:pattern=pattern[:position]+rng.choice(alphabet)+pattern[position:]
        elif rng.randrange(2):pattern=rng.choice(['@(', '?(', '!(', '{'])+pattern+rng.choice([')', '|a)', ',b}'])
        else:pattern=pattern.replace(rng.choice(['a','*','(',')']),rng.choice(alphabet),1)
        if len(pattern)<=96:corpus.append(pattern)
    tasks=[]
    for target in targets:
        for pattern,subject in [('a+(b)','abbb'),('*([0-9]).txt','123.txt'),('+([a-z]).js','abc.js'),('x/*(a)/y','x/aaa/y')]:
            tasks.append({'kind':'pm',**target,'api':'matcher','pattern':pattern,'subject':subject,'options':{},'expected_match':True})
    # Controls first, then known vulnerable patterns before mutation fuzzing.
    for target in targets:
        tasks.append({'kind':'pm',**target,'api':'makeRe','pattern':'*.js','subject':'a.js','options':{}})
    for pattern in ['+(*a)','*(*)z','(a+)+b','(a|aa)+b','(a*)*b','*a*a*a*a*a*a*a*a*a*b']:
        for target in targets:tasks.append({'kind':'pm',**target,'api':'makeRe','pattern':pattern,'subject':'a'*36+'!','options':{}})
    rollups=[app/'node_modules/rollup',*[Path(p).resolve() for p in args.rollup_extra]]
    for package in rollups:
        for relative in ['dist/shared/rollup.js','dist/shared/index.js','dist/es/shared/node-entry.js','dist/es/shared/watch.js']:
            p=package/relative
            if p.exists():snapshot[str(p)]=sha(p.read_bytes())
        for kind,module in [('rollup-filter',package/'dist/shared/rollup.js'),('rollup-public',package)]:
            for pattern,subject in [('**/*','a.js'),('+(*a)','a'*8+'!'),('+(*a)','a'*36+'!'),('(a+)+b','a'*36+'!')]:
                task={'kind':kind,'label':'rollup-'+json.loads((package/'package.json').read_text())['version'],'module':str(module),'pattern':pattern,'subject':subject,'options':{}}
                if pattern=='**/*':
                    task['expected_match' if kind=='rollup-filter' else 'expected_transformed']=True if kind=='rollup-filter' else 1
                tasks.append(task)
    options=[{'regex':True}, {}, {'fastpaths':False},{'dot':True},{'windows':True},{'bash':True},{'noextglob':True},{'regex':False},{'maxExtglobRecursion':False},{'contains':True},{'capture':True},{'strictBrackets':True},{'unescape':True},{'nonegate':True},{'posix':True}]
    apis=['matcher','makeRe','isMatch','parse','parser','array']
    for i,pattern in enumerate(corpus):
        target=targets[i%len(targets)];subject=('x/' if i%7==0 else '')+'a'*[16,24,36,48][i%4]+('!/y' if i%7==0 else '!')
        tasks.append({'kind':'pm',**target,'api':apis[(i//len(targets))%len(apis)],'pattern':pattern,'subject':subject,'options':options[(i//3)%len(options)]})
    return tasks,inventory,snapshot,sorted(set(''.join(corpus)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--node',default=shutil.which('node'));parser.add_argument('--probes',type=int,default=360)
    parser.add_argument('--seconds',type=float,default=120);parser.add_argument('--timeout-ms',type=int,default=1200)
    parser.add_argument('--heap-mib',type=int,default=96);parser.add_argument('--job-mib',type=int,default=384)
    parser.add_argument('--virtual-mib',type=int,default=8192);parser.add_argument('--seed',type=int,default=20261118)
    parser.add_argument('--rollup-extra',action='append',default=[])
    args=parser.parse_args();args.app=args.app.resolve();args.out=args.out.resolve()
    if not args.node:parser.error('Node is required; no automatic installation is performed')
    if args.out.exists():parser.error('Output exists; choose a new report filename')
    if not args.out.parent.is_dir():parser.error('Output directory must already exist')
    if args.out.is_relative_to(args.app.parent):parser.error('Output must be outside the candidate source')
    if not (1<=args.probes<=512 and 1<=args.seconds<=120 and 100<=args.timeout_ms<=2000 and 32<=args.heap_mib<=256 and args.heap_mib<args.job_mib<=768 and 2048<=args.virtual_mib<=16384):parser.error('Invalid resource bounds')
    runner_hash=sha(Path(__file__).read_bytes());child_hash=sha(CHILD.encode());node_version=subprocess.check_output([args.node,'--version'],text=True,timeout=5).strip()
    started=time.monotonic();results=[]
    with tempfile.TemporaryDirectory(prefix='pm02-fuzz-') as temporary:
        tasks,inventory,snapshot,alphabet=tasks_for(args.app,temporary,args)
        for number,task in enumerate(tasks[:args.probes]):
            remaining=args.seconds-(time.monotonic()-started)
            if remaining<=0:break
            row=run_probe(task,args,temporary,remaining);row['probe']=number;results.append(row)
            if row['stage']=='startup' and row['status']=='RESOURCE_OR_PROCESS_ERROR':raise RuntimeError('Node cannot start within resource limits; no automatic relaxation. '+row['stderr_tail'])
        mismatches=[p for p,h in snapshot.items() if sha(Path(p).read_bytes())!=h]
        if mismatches:raise RuntimeError('Read-only dependency check failed: '+repr(mismatches))
    assert sha(Path(__file__).read_bytes())==runner_hash, 'Fuzz runner changed during execution'
    failures=[r['probe'] for r in results if not r['label'].startswith('original-control-') and (r['status'] in {'TIMEOUT','RESOURCE_OR_PROCESS_ERROR'} or ('expected_match' in r and r['result'].get('match') != r['expected_match']) or ('expected_transformed' in r and r['result'].get('transformed') != r['expected_transformed']) or (r['status']=='ERROR' and r['result'].get('code')!='SyntaxError'))]
    complete=len(results)==len(tasks)
    report={'gate':'PASS' if complete and not failures else 'FAIL','unexpected_probes':failures,'runner_sha256':runner_hash,'child_source_sha256':child_hash,'node':node_version,'dependency_hashes':snapshot,'seed':args.seed,'elapsed_seconds':round(time.monotonic()-started,3),'requested_probes':args.probes,'completed_probes':len(results),'scheduled_probes':len(tasks),'time_budget_reached':len(results)<len(tasks),'exhaustive':False,'node_heap_mib':args.heap_mib,'windows_job_committed_memory_mib':args.job_mib if os.name=='nt' else None,'posix_address_space_mib':args.virtual_mib if os.name!='nt' else None,'timeout_ms':args.timeout_ms,'alphabet':alphabet,'installed_inventory':inventory,'dependency_hashes_unchanged':True,'counts':dict(collections.Counter(x['status'] for x in results)),'results':results}
    with args.out.open('x',encoding='utf-8') as out:json.dump(report,out,indent=2);out.write('\n')
    print(json.dumps({k:report[k] for k in ['gate','unexpected_probes','completed_probes','scheduled_probes','time_budget_reached','exhaustive','elapsed_seconds','counts','dependency_hashes_unchanged']},indent=2))

    if report['gate']!='PASS':raise SystemExit(1)

if __name__=='__main__':main()
