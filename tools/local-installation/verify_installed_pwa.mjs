import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn,execFileSync} from 'node:child_process';
import readline from 'node:readline';
import {randomUUID} from 'node:crypto';
import {chromium} from '../../app/node_modules/playwright-core/index.mjs';
const repository=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const root=path.resolve(process.argv[2]);
const nativeReparent=process.argv.slice(3).includes('--native-reparent');
const worldDiagnostic=process.argv.slice(3).includes('--world-diagnostic');
const manualDocuments=process.argv.slice(3).includes('--manual-documents');
const proof=JSON.parse(fs.readFileSync(path.join(root,'EVIDENCIAS/PAQUETES_FIRMADOS.json')));
const cli=path.join(repository,'tools/local-installation/bootstrap_individual.py');
const bootstrapPython=proof.bootstrap_python??proof.python;
const result={synthetic_only:true,steps:[],errors:[],native_pwa:{status:'NOT_EXECUTED'}};
let context,session,owned,manifestId,nativeInstalled=false,diagnosticPage;
result.console_errors=[];result.request_failures=[];result.worker_fetches=[];
result.worker_checkpoints=[];
result.startup_evidence_note='Prior async waitForFunction boolean startup claims are invalid: installed Playwright polls Promise truthiness without awaiting the predicate. This run uses strict resolved Node polling.';
result.worker_startup_polls=[];
function progress(phase){
 result.progress={phase,utc:new Date().toISOString()};
 fs.writeFileSync(path.join(root,'EVIDENCIAS',manualDocuments?'BROWSER_MANUAL_PROGRESS.json':'BROWSER_PROGRESS.json'),JSON.stringify(result,null,2)+'\n');
}
async function bounded(label,promise,ms=45000){
 let timer;
 try{return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error(label+' timed out after '+ms+'ms')),ms)})]);}
 finally{clearTimeout(timer);}
}
function evaluate(page,fn,arg){return bounded('page.evaluate',page.evaluate(fn,arg));}
async function cdpSend(client,method,params={}){progress(method);return bounded(method,client.send(method,params));}
function safeAddress(url){try{const u=new URL(url);return u.origin+u.pathname;}catch{return 'non-http-url';}}
function observe(page){
 page.on('console',message=>{if(message.type()==='error'&&result.console_errors.length<100)result.console_errors.push(message.text().slice(0,500));});
}
async function workerDiagnostic(){
 if(!diagnosticPage||diagnosticPage.isClosed())return;
 try{
  result.worker_state=await bounded('service-worker diagnostic',diagnosticPage.evaluate(async()=>{
   const rows=await navigator.serviceWorker.getRegistrations();
   return {secureContext:isSecureContext,controller:navigator.serviceWorker.controller?.state??null,registrations:rows.map(r=>({scope:new URL(r.scope).pathname,installing:r.installing?.state??null,waiting:r.waiting?.state??null,active:r.active?.state??null}))};
  }),5000);
 }catch(error){result.worker_state={diagnostic_error:String(error)};}
}
async function workerCheckpoint(page,label){
 const checkpoint={label,utc:new Date().toISOString(),execution_world:'main',world_source:'installed playwright-core/lib/coreBundle.js:24378-24384'};
 // Exactly the same function runs through two public Playwright API paths.
 // This installed version defaults waitForFunctionExpression to MAIN too.
 const snapshot=async()=>{
  const rows=await navigator.serviceWorker.getRegistrations();
  const current=await navigator.serviceWorker.getRegistration();
  return {href:location.href,origin:location.origin,title:document.title,
   buildSHA:document.querySelector('[data-testid="build-identity"] code')?.getAttribute('title')??null,
   metas:Array.from(document.querySelectorAll('meta[name]')).map(m=>({name:m.name,content:m.content})),
   secureContext:isSecureContext,current_scope:current?new URL(current.scope).pathname:null,
   controller:navigator.serviceWorker.controller?{state:navigator.serviceWorker.controller.state,script:new URL(navigator.serviceWorker.controller.scriptURL).pathname}:null,
   registrations:rows.map(r=>({scope:new URL(r.scope).pathname,installing:r.installing?.state??null,waiting:r.waiting?.state??null,active:r.active?.state??null}))};
 };
 try{
  checkpoint.evaluate_path=await bounded('evaluate checkpoint '+label,evaluate(page,snapshot),5000);
 }catch(error){checkpoint.evaluate_error=String(error);}
 let handle;
 try{
  // The snapshot is always a truthy object: one observation, not a state retry.
  handle=await page.waitForFunction(snapshot,null,{timeout:5000});
  checkpoint.waitForFunction_path=await bounded('waitForFunction snapshot '+label,handle.jsonValue(),5000);
 }catch(error){checkpoint.waitForFunction_error=String(error);}
 finally{if(handle)await bounded('snapshot handle dispose',handle.dispose(),5000).catch(()=>{});}
 result.worker_checkpoints.push(checkpoint);progress('worker-checkpoint-'+label);
}
async function requireActiveWorker(page,label){
 const deadline=Date.now()+35000;
 const poll={label,attempts:0,status:'PENDING',last_state:null,last_error:null};
 result.worker_startup_polls.push(poll);
 progress('strict-worker-poll-'+label);
 while(Date.now()<deadline){
  poll.attempts++;
  try{
   const state=await bounded('resolved worker state '+label,evaluate(page,async()=>{
    const registration=await navigator.serviceWorker.getRegistration();
    return {href:location.href,active:registration?.active?.state??null,
     controller_present:!!navigator.serviceWorker.controller,
     controller_state:navigator.serviceWorker.controller?.state??null};
   }),Math.min(5000,Math.max(1,deadline-Date.now())));
   poll.last_state=state;poll.last_error=null;
   // This checks the RESOLVED object in Node, never a Promise's truthiness.
   if(state.active==='activated'&&state.controller_present===true){
    poll.status='PASS';progress('strict-worker-active-'+label);return state;
   }
  }catch(error){poll.last_error=String(error);}
  if(Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,Math.min(100,deadline-Date.now())));
 }
 poll.status='FAILED';progress('strict-worker-timeout-'+label);
 throw new Error('Active service worker and controller not observed within 35000ms: '+label);
}
function select(artifact,command='activate'){
 return JSON.parse(execFileSync(bootstrapPython,['-I','-B',cli,'--action',command,'--root',proof.installer_root,'--version',artifact.version],{encoding:'utf8',windowsHide:true}));
}
async function launch(){
 const child=spawn(bootstrapPython,['-I','-B',cli,'--action','serve','--root',proof.installer_root],{windowsHide:true,stdio:['ignore','pipe','pipe']});
 let errors='';child.stderr.on('data',b=>{errors+=b.toString()});
 const info=await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('server startup timeout: '+errors)),45000);
  const lines=readline.createInterface({input:child.stdout});
  lines.once('line',line=>{clearTimeout(timer);try{resolve(JSON.parse(line))}catch(e){reject(e)}});
  child.once('exit',code=>{clearTimeout(timer);reject(new Error('server exited '+code+': '+errors))});
 }); return {child,info};
}
async function stop(){
 if(!owned)return;const child=owned.child;owned=null;
 if(child.exitCode!==null||child.signalCode!==null)return;
 await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('owned launcher stop timed out')),15000);
  child.once('exit',()=>{clearTimeout(timer);resolve()});child.kill();
 });
}
async function api(page,revision,route='/api/clinical-note/new',body={age_years:45,language:'es-ES'}){
 return bounded('local API '+route,evaluate(page,async({revision,route,body})=>{
  const r=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json','X-Emergency-Revision':revision},body:JSON.stringify(body)});
  return {status:r.status,type:r.headers.get('content-type'),body:await r.json()};
 },{revision,route,body}));
}
async function identity(page,artifact){
 await page.getByTestId('build-identity').waitFor();
 // playwright-core is installed without @playwright/test: use its native polling
 // predicate rather than an immediate assertion against the pre-reload document.
 await page.waitForFunction(sha=>document.querySelector('[data-testid="build-identity"] code')?.getAttribute('title')===sha,artifact.source_sha,{timeout:35000});
 assert.equal(await page.getByTestId('build-identity').locator('code').getAttribute('title'),artifact.source_sha);
}
async function launchedNativePage(targetId){
 const deadline=Date.now()+25000;
 const observed=new Set();
 while(Date.now()<deadline){
  for(const candidate of context.pages()){
   if(candidate.isClosed())continue;
   let cdp;
   try{
    cdp=await context.newCDPSession(candidate);
    const {targetInfo}=await bounded('Target.getTargetInfo',cdp.send('Target.getTargetInfo'),5000);
    observed.add(targetInfo.targetId);
    if(targetInfo.targetId===targetId){
     result.native_target_matching={requested:targetId,matched:targetInfo.targetId,observed:[...observed]};
     return candidate;
    }
   }catch(error){if(!candidate.isClosed())throw error;}
   finally{if(cdp)await cdp.detach().catch(()=>{});}
  }
  await new Promise(resolve=>setTimeout(resolve,100));
 }
 const targets=await cdpSend(session,'Target.getTargets');
 result.native_target_matching={requested:targetId,observed:[...observed],timeout_targets:targets.targetInfos.map(({targetId,type})=>({targetId,type}))};
 throw new Error('PWA.launch target was not attached in the owned browser context: '+targetId);
}
async function runManualDocuments(){
 const [a,b]=proof.artifacts;
 result.scope='NOT_PWA_UPGRADE';result.native_pwa={status:'NOT_EXECUTED',reason:'Manual document scope'};
 result.installed_pwa_upgrade={status:'NOT_VERIFIED'};result.cached_offline={status:'NOT_VERIFIED'};
 result.start_action={action:'rollback',version:a.version,result:select(a,'rollback')};
 owned=await launch();const origin=owned.info.url;progress('manual-documents-start-A');
 result.executable='C:/Program Files/Google/Chrome/Application/chrome.exe';
 result.owned_profile=path.resolve(proof.installer_root,'../OWNED_BROWSER_MANUAL_'+a.source_sha.slice(0,12)+'_'+randomUUID());
 context=await chromium.launchPersistentContext(result.owned_profile,{executablePath:result.executable,headless:false,viewport:{width:1280,height:900},args:['--no-first-run','--no-default-browser-check']});
 context.setDefaultTimeout(35000);context.setDefaultNavigationTimeout(45000);result.browser=context.browser().version();
 result.page_errors=[];result.external_requests=[];
 const watch=p=>{observe(p);p.on('pageerror',e=>result.page_errors.push(e.message));};
 context.on('page',watch);for(const p of context.pages())watch(p);
 await context.route('**/*',route=>{const url=route.request().url();if(/^https?:/.test(url)&&new URL(url).origin!==origin){result.external_requests.push(safeAddress(url));return route.abort();}return route.continue();});
 const dirty=context.pages()[0]??await context.newPage();diagnosticPage=dirty;
 await dirty.goto(origin,{waitUntil:'networkidle'});await identity(dirty,a);
 await evaluate(dirty,()=>{localStorage.setItem('emergency.lang','en');localStorage.setItem('emergency.theme','dark');localStorage.setItem('emergency.micro','mcg')});
 await dirty.goto(origin+'/clinical-note',{waitUntil:'networkidle'});await identity(dirty,a);
 await dirty.locator('textarea').first().fill('SYNTHETIC MANUAL DOCUMENT — RETAIN');
 await evaluate(dirty,()=>{window.__syntheticDocumentMarker=crypto.randomUUID()});
 const marker=await evaluate(dirty,()=>window.__syntheticDocumentMarker);
 const note=await dirty.locator('textarea').first().inputValue();const encounter=await dirty.getByTestId('note-encounter').innerText();
 assert.equal((await api(dirty,a.source_sha)).status,200);
 progress('manual-documents-switch-B');await stop();select(b);owned=await launch();assert.equal(owned.info.url,origin);
 const cleanB=await context.newPage();await cleanB.goto(origin+'/calculator?drug=norepinephrine&weight=70&dose=0.05',{waitUntil:'networkidle'});await identity(cleanB,b);
 assert.equal((await api(cleanB,b.source_sha)).status,200);assert.equal((await api(dirty,a.source_sha)).status,409);
 for(const destination of ['/pediatrics','/procedures']){
  await evaluate(dirty,destination=>{history.pushState({},'',destination);dispatchEvent(new PopStateEvent('popstate'))},destination);
  await dirty.getByTestId('local-stale-navigation').waitFor();await dirty.waitForURL(origin+'/clinical-note');
  assert.equal(await evaluate(dirty,()=>window.__syntheticDocumentMarker),marker);
  assert.equal(await dirty.locator('textarea').first().inputValue(),note);assert.equal(await dirty.getByTestId('note-encounter').innerText(),encounter);await identity(dirty,a);
 }
 await dirty.screenshot({path:path.join(root,'EVIDENCIAS/MANUAL_EPISODIO_PROTEGIDO.png'),fullPage:true});
 const prefs=p=>evaluate(p,()=>({lang:localStorage.getItem('emergency.lang'),theme:localStorage.getItem('emergency.theme'),micro:localStorage.getItem('emergency.micro')}));
 const expected={lang:'en',theme:'dark',micro:'mcg'};assert.deepEqual(await prefs(cleanB),expected);
 result.steps.push({test:'Manual new B document, WAN blocked, B API200, stale A409, unchanged old A note/document/encounter through blocked unseen routes',status:'PASS',origin});
 progress('manual-documents-rollback-A');await stop();select(a,'rollback');owned=await launch();assert.equal(owned.info.url,origin);
 const cleanA=await context.newPage();await cleanA.goto(origin+'/calculator?drug=norepinephrine&weight=70&dose=0.05',{waitUntil:'networkidle'});await identity(cleanA,a);
 assert.deepEqual(await prefs(cleanA),expected);assert.equal((await api(cleanA,a.source_sha)).status,200);
 assert.equal(await evaluate(dirty,()=>window.__syntheticDocumentMarker),marker);assert.equal(await dirty.locator('textarea').first().inputValue(),note);
 result.steps.push({test:'Explicit rollback, manual new A document, same origin and retained preferences, local A API200 under WAN block',status:'PASS'});
 assert.deepEqual(result.page_errors,[]);
 result.full_update_rollback={status:'PASS_MANUAL_DOCUMENTS_ONLY',not_pwa_upgrade:true};
 dirty.once('dialog',d=>d.accept());await dirty.getByRole('button',{name:'New note',exact:true}).click();
 assert.equal(await dirty.locator('textarea').first().inputValue(),'');await dirty.close();
}
try{
 if(manualDocuments){await runManualDocuments();}else{
 progress('activate-and-start-A');
 const [a,b]=proof.artifacts;select(a);owned=await launch();const origin=owned.info.url;
 result.executable='C:/Program Files/Google/Chrome/Application/chrome.exe';
 // Fresh profile per attempt; the same profile is retained throughout A/B/A.
 // Previous attempts and their waiting service workers remain untouched.
 result.owned_profile=path.resolve(proof.installer_root,'../OWNED_BROWSER_PROFILE_'+a.source_sha.slice(0,12)+'_'+randomUUID());
 context=await chromium.launchPersistentContext(result.owned_profile,{executablePath:result.executable,headless:false,viewport:{width:1280,height:900},args:['--no-first-run','--no-default-browser-check']});
 result.browser=context.browser().version();
 context.setDefaultTimeout(35000);context.setDefaultNavigationTimeout(45000);
 const errors=[],externals=[];
 context.on('page',page=>{observe(page);page.on('pageerror',e=>errors.push(e.message));});
 context.on('requestfailed',request=>{if(result.request_failures.length<100)result.request_failures.push({url:safeAddress(request.url()),failure:request.failure()?.errorText});});
 context.on('response',response=>{if(/\/(?:sw\.js|workbox[^/]*)/.test(new URL(response.url()).pathname)&&result.worker_fetches.length<100)result.worker_fetches.push({url:safeAddress(response.url()),status:response.status()});});
 context.on('request',request=>{const u=request.url();if(/^https?:/.test(u)&&new URL(u).origin!==origin)externals.push(u)});
 let page=context.pages()[0]??await context.newPage();
 diagnosticPage=page;observe(page);progress('initial-navigation-A');
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin,{waitUntil:'networkidle'});
 progress('write-synthetic-preferences');
 await evaluate(page,()=>{localStorage.setItem('emergency.lang','en');localStorage.setItem('emergency.theme','dark');localStorage.setItem('emergency.micro','mcg')});
 await page.reload({waitUntil:'networkidle'});await identity(page,a);
 progress('wait-active-service-worker-and-controller-A');
 await requireActiveWorker(page,'initial-A');
 progress('local-api-A');
 assert.equal((await api(page,a.source_sha)).status,200);
 // WAN is blocked while localhost remains available: local deterministic API works.
 await context.route('**/*',route=>/^https?:/.test(route.request().url())&&new URL(route.request().url()).origin!==origin?route.abort():route.continue());
 assert.equal((await api(page,a.source_sha,'/api/clinical-scores/catalog',{})).status,200);
 assert.equal((await api(page,a.source_sha,'/api/blood-gas/session',{})).status,503);
 for(const p of ['/backend/runtime.json','/backend/launcher/individual_cli.py'])assert.notEqual((await page.request.get(origin+p)).status(),200);
 result.steps.push({test:'A local API, WAN blocked, private backend hidden, absent OCR explicit',status:'PASS',origin});
 session=await context.browser().newBrowserCDPSession();manifestId=origin+'/';
 try{
  await cdpSend(session,'PWA.install',{manifestId,installUrlOrBundleUrl:origin+'/'});
  nativeInstalled=true;
  await workerCheckpoint(page,'post-install-original-document');
  const state=await cdpSend(session,'PWA.getOsAppState',{manifestId});
  let nativePage;
  if(nativeReparent){
   const nativeSession=await bounded('owned page CDP session',context.newCDPSession(page));
   try{
    const before=await cdpSend(nativeSession,'Target.getTargetInfo');
    const windowBefore=await cdpSend(session,'Browser.getWindowForTarget',{targetId:before.targetInfo.targetId});
    result.native_pwa={status:'IN_PROGRESS',method:'PWA.openCurrentPageInApp',manifest_id:manifestId,state,target_before:before.targetInfo.targetId,window_before:windowBefore.windowId};
    // Official protocol requires a PAGE target session. Reparent the exact
    // already verified document; do not substitute a generic page event.
    await cdpSend(nativeSession,'PWA.openCurrentPageInApp',{manifestId});
    await page.waitForFunction(()=>matchMedia('(display-mode: standalone)').matches,null,{timeout:35000});
    const after=await cdpSend(nativeSession,'Target.getTargetInfo');
    assert.equal(after.targetInfo.targetId,before.targetInfo.targetId);
    const windowAfter=await cdpSend(session,'Browser.getWindowForTarget',{targetId:after.targetInfo.targetId});
    await identity(page,a);
    result.native_pwa={...result.native_pwa,status:'PASS',target_after:after.targetInfo.targetId,window_after:windowAfter.windowId,window_changed:windowAfter.windowId!==windowBefore.windowId,standalone:true,source_sha:a.source_sha};
    nativePage=page;
   }finally{await bounded('owned page CDP detach',nativeSession.detach(),5000);}
  }else{
  const launched=await cdpSend(session,'PWA.launch',{manifestId});
  assert.ok(launched.targetId);
  // PWA.install may open a different page before PWA.launch does. Match the
  // returned CDP target identity, never the first generic page event.
  nativePage=await launchedNativePage(launched.targetId);
  await nativePage.waitForLoadState('domcontentloaded');
  const nativeSession=await context.newCDPSession(nativePage);
  const target=await cdpSend(nativeSession,'Target.getTargetInfo');
  assert.equal(target.targetInfo.targetId,launched.targetId);
  await nativeSession.detach();
  await identity(nativePage,a);
  assert.equal(await evaluate(nativePage,()=>matchMedia('(display-mode: standalone)').matches),true);
  result.native_pwa={status:'PASS',method:'PWA.launch',manifest_id:manifestId,state,target_created:true,target_id:launched.targetId,standalone:true};
  }
  await workerCheckpoint(nativePage,'post-native-open-before-reload');
  // A normal first launch reloads the newly installed application's own page.
  // Do this before creating ANY episode, then require its real registration;
  // never repair missing registrations by manually registering a worker.
  diagnosticPage=nativePage;progress('first-installed-startup-reload-A');
  await nativePage.reload({waitUntil:'networkidle'});await identity(nativePage,a);
  await requireActiveWorker(nativePage,'installed-cold-start-A');
  await workerCheckpoint(nativePage,'post-installed-startup-reload-A');
  result.native_startup={status:'PASS',registration_active:true,controller_present:true};
  await evaluate(nativePage,()=>{localStorage.setItem('emergency.lang','en');localStorage.setItem('emergency.theme','dark');localStorage.setItem('emergency.micro','mcg')});
  // Execute the actual update/rollback proof in the launched OS app window.
  for(const other of context.pages())if(other!==nativePage)await other.close();
  page=nativePage;diagnosticPage=page;progress('native-PWA-confirmed-A');
 }catch(error){
  if(result.native_pwa.status==='PASS')result.native_startup={status:'FAILED',error:String(error)};
  else result.native_pwa={...result.native_pwa,status:'FAILED',method:nativeReparent?'PWA.openCurrentPageInApp':'PWA.launch',error:String(error)};
  throw error;
 }
 if(worldDiagnostic){
  result.diagnostic_only=true;
  result.full_update_rollback={status:'NOT_EXECUTED',reason:'Requested API-path diagnosis; evaluate and waitForFunction both use MAIN in installed Playwright. Stopped before episodes or B switch'};
  progress('world-diagnostic-complete-before-B');
 }else{
 const dirty=await context.newPage();await dirty.goto(origin+'/clinical-note',{waitUntil:'networkidle'});
 await dirty.locator('textarea').first().fill('SYNTHETIC OPEN ENCOUNTER — DO NOT RELOAD');
 const note=await dirty.locator('textarea').first().inputValue();
 await evaluate(dirty,()=>{window.__syntheticDocumentMarker=crypto.randomUUID()});
 const dirtyDocument=await evaluate(dirty,()=>window.__syntheticDocumentMarker);
 await page.goto(origin+'/calculator?drug=norepinephrine&weight=70&dose=0.05',{waitUntil:'networkidle'});
 await page.getByTestId('rate-display').waitFor();assert.equal(await page.getByTestId('rate-display').innerText(),'5.3');
 await page.screenshot({path:path.join(root,'EVIDENCIAS/A_INSTALADA.png'),fullPage:true});
 await workerCheckpoint(page,'pre-stop-runtime-A');
 progress('switch-runtime-B');await stop();select(b);owned=await launch();assert.equal(owned.info.url,origin);
 await workerCheckpoint(page,'post-start-runtime-B-before-update');
 assert.equal((await api(dirty,a.source_sha)).status,409);
 assert.equal(await dirty.locator('textarea').first().inputValue(),note);
 progress('check-service-worker-B');await bounded('service-worker update B',evaluate(page,async()=>{const r=await navigator.serviceWorker.getRegistration();if(!r)throw new Error('Service-worker registration missing after runtime restart');await r.update()}));
 await page.getByTestId('local-update-notice').waitFor({timeout:35000});
 await dirty.getByTestId('local-update-notice').waitFor({timeout:35000});
 assert.equal(await dirty.getByTestId('local-update-confirm').isDisabled(),true);
 assert.equal(await dirty.getByTestId('local-update-apply').isDisabled(),true);
 await page.getByTestId('local-update-confirm').check();await page.getByTestId('local-update-apply').click();
 await identity(page,b);
 // The worker update must not have navigated or reconstructed the second tab.
 assert.equal(await evaluate(dirty,()=>window.__syntheticDocumentMarker),dirtyDocument);
 assert.equal(await dirty.locator('textarea').first().inputValue(),note);await identity(dirty,a);
 const encounter=await dirty.getByTestId('note-encounter').innerText();
 for(const destination of ['/pediatrics','/procedures']){
  // Popstate exercises the existing BrowserRouter without a document navigation.
  // Neither lazy module has been visited in this old-version document.
  await evaluate(dirty,destination=>{history.pushState({},'',destination);dispatchEvent(new PopStateEvent('popstate'))},destination);
  await dirty.getByTestId('local-stale-navigation').waitFor();
  await dirty.waitForURL(origin+'/clinical-note');
  assert.equal(await evaluate(dirty,()=>window.__syntheticDocumentMarker),dirtyDocument);
  assert.equal(await dirty.locator('textarea').first().inputValue(),note);
  assert.equal(await dirty.getByTestId('note-encounter').innerText(),encounter);
  await identity(dirty,a);
 }
 assert.equal((await api(page,b.source_sha)).status,200);
 const prefs=await evaluate(page,()=>({lang:localStorage.getItem('emergency.lang'),theme:localStorage.getItem('emergency.theme'),micro:localStorage.getItem('emergency.micro')}));
 assert.deepEqual(prefs,{lang:'en',theme:'dark',micro:'mcg'});
 await dirty.screenshot({path:path.join(root,'EVIDENCIAS/EPISODIO_PROTEGIDO.png'),fullPage:true});
 await page.screenshot({path:path.join(root,'EVIDENCIAS/B_ACTUALIZADA.png'),fullPage:true});
 result.steps.push({test:'Installed PWA A→B, stable origin, prefs preserved, dirty second tab retained through blocked unseen pediatrics/procedures navigation, stale API409, clean tab explicit consent',status:'PASS',prefs});
 // Use the real reset action: clearing one textarea does not clear other draft
 // fields (for example a vital timestamp), and closing a dirty tab can prompt.
 dirty.once('dialog',dialog=>dialog.accept());
 await dirty.getByRole('button',{name:'New note',exact:true}).click();
 await dirty.waitForFunction(()=>!document.querySelector('[data-testid="local-update-confirm"]')?.disabled);
 assert.equal(await dirty.locator('textarea').first().inputValue(),'');
 await dirty.close();
 // Leave B in the installed document; select A explicitly and restart same origin.
 progress('rollback-runtime-A');await stop();select(a,'rollback');owned=await launch();assert.equal(owned.info.url,origin);
 await bounded('service-worker rollback A',evaluate(page,async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}));
 await page.getByTestId('local-update-notice').waitFor({timeout:35000});
 await page.getByTestId('local-update-confirm').check();await page.getByTestId('local-update-apply').click();await identity(page,a);
 assert.deepEqual(await evaluate(page,()=>({lang:localStorage.getItem('emergency.lang'),theme:localStorage.getItem('emergency.theme'),micro:localStorage.getItem('emergency.micro')})),prefs);
 assert.equal((await api(page,a.source_sha)).status,200);
 await page.goto(origin+'/calculator?drug=norepinephrine&weight=70&dose=0.05',{waitUntil:'networkidle'});
 await stop();await context.setOffline(true);await page.reload({waitUntil:'domcontentloaded'});
 await page.getByTestId('rate-display').waitFor();assert.equal(await page.getByTestId('rate-display').innerText(),'5.3');
 const outage=await evaluate(page,async()=>{try{const r=await fetch('/api/clinical-note/new',{method:'POST',body:'{}'});return{status:r.status,type:r.headers.get('content-type')}}catch{return{network_failed:true}}});
 assert.equal(outage.network_failed,true);
 await page.screenshot({path:path.join(root,'EVIDENCIAS/A_ROLLBACK_OFFLINE.png'),fullPage:true});
 result.steps.push({test:'Explicit B→A rollback, preferences retained; server stopped and browser offline, cached calculator5.3, API fails explicitly',status:'PASS',outage});
 assert.deepEqual(errors,[]);assert.deepEqual(externals,[]);result.page_errors=errors;result.external_requests=externals;
 }
 }
}catch(error){result.failure_phase=result.progress;result.errors.push(String(error));await workerDiagnostic();progress('FAILED');process.exitCode=1;}
finally{
 if(context)await context.setOffline(false).catch(()=>{});
 if(session&&nativeInstalled)try{await cdpSend(session,'PWA.uninstall',{manifestId});result.native_pwa.test_installation_removed=true}catch(error){result.errors.push('Own PWA cleanup: '+String(error));process.exitCode=1}
 if(context)await bounded('owned browser close',context.close(),15000).catch(error=>result.errors.push(String(error)));await stop();
 progress('FINISHED');
 fs.writeFileSync(path.join(root,'EVIDENCIAS',manualDocuments?'BROWSER_MANUAL_DOCUMENTS.json':'BROWSER_INDIVIDUAL_REAL.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result));
}
