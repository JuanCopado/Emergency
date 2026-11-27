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
const proof=JSON.parse(fs.readFileSync(path.join(root,'EVIDENCIAS/PAQUETES_FIRMADOS.json')));
const cli=path.join(repository,'tools/local-installation/bootstrap_individual.py');
const bootstrapPython=proof.bootstrap_python??proof.python;
const result={synthetic_only:true,steps:[],errors:[],native_pwa:{status:'NOT_EXECUTED'}};
let context,session,owned,manifestId,nativeInstalled=false;
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
 return page.evaluate(async({revision,route,body})=>{
  const r=await fetch(route,{method:'POST',headers:{'Content-Type':'application/json','X-Emergency-Revision':revision},body:JSON.stringify(body)});
  return {status:r.status,type:r.headers.get('content-type'),body:await r.json()};
 },{revision,route,body});
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
    const {targetInfo}=await cdp.send('Target.getTargetInfo');
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
 const targets=await session.send('Target.getTargets');
 result.native_target_matching={requested:targetId,observed:[...observed],timeout_targets:targets.targetInfos.map(({targetId,type})=>({targetId,type}))};
 throw new Error('PWA.launch target was not attached in the owned browser context: '+targetId);
}
try{
 const [a,b]=proof.artifacts;select(a);owned=await launch();const origin=owned.info.url;
 result.executable='C:/Program Files/Google/Chrome/Application/chrome.exe';
 // Fresh profile per attempt; the same profile is retained throughout A/B/A.
 // Previous attempts and their waiting service workers remain untouched.
 result.owned_profile=path.resolve(proof.installer_root,'../OWNED_BROWSER_PROFILE_'+a.source_sha.slice(0,12)+'_'+randomUUID());
 context=await chromium.launchPersistentContext(result.owned_profile,{executablePath:result.executable,headless:false,viewport:{width:1280,height:900},args:['--no-first-run','--no-default-browser-check']});
 result.browser=context.browser().version();
 const errors=[],externals=[];
 context.on('page',page=>page.on('pageerror',e=>errors.push(e.message)));
 context.on('request',request=>{const u=request.url();if(/^https?:/.test(u)&&new URL(u).origin!==origin)externals.push(u)});
 let page=context.pages()[0]??await context.newPage();
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin,{waitUntil:'networkidle'});
 await page.evaluate(()=>{localStorage.setItem('emergency.lang','en');localStorage.setItem('emergency.theme','dark');localStorage.setItem('emergency.micro','mcg')});
 await page.reload({waitUntil:'networkidle'});await identity(page,a);
 await page.evaluate(async()=>navigator.serviceWorker.ready);
 await page.waitForFunction(()=>!!navigator.serviceWorker.controller,null,{timeout:25000});
 assert.equal((await api(page,a.source_sha)).status,200);
 // WAN is blocked while localhost remains available: local deterministic API works.
 await context.route('**/*',route=>/^https?:/.test(route.request().url())&&new URL(route.request().url()).origin!==origin?route.abort():route.continue());
 assert.equal((await api(page,a.source_sha,'/api/clinical-scores/catalog',{})).status,200);
 assert.equal((await api(page,a.source_sha,'/api/blood-gas/session',{})).status,503);
 for(const p of ['/backend/runtime.json','/backend/launcher/individual_cli.py'])assert.notEqual((await page.request.get(origin+p)).status(),200);
 result.steps.push({test:'A local API, WAN blocked, private backend hidden, absent OCR explicit',status:'PASS',origin});
 session=await context.browser().newBrowserCDPSession();manifestId=origin+'/';
 try{
  await session.send('PWA.install',{manifestId,installUrlOrBundleUrl:origin+'/'});
  nativeInstalled=true;
  const state=await session.send('PWA.getOsAppState',{manifestId});
  const launched=await session.send('PWA.launch',{manifestId});
  assert.ok(launched.targetId);
  // PWA.install may open a different page before PWA.launch does. Match the
  // returned CDP target identity, never the first generic page event.
  const nativePage=await launchedNativePage(launched.targetId);
  await nativePage.waitForLoadState('domcontentloaded');
  const nativeSession=await context.newCDPSession(nativePage);
  const target=await nativeSession.send('Target.getTargetInfo');
  assert.equal(target.targetInfo.targetId,launched.targetId);
  await nativeSession.detach();
  await identity(nativePage,a);
  assert.equal(await nativePage.evaluate(()=>matchMedia('(display-mode: standalone)').matches),true);
  result.native_pwa={status:'PASS',manifest_id:manifestId,state,target_created:true,target_id:launched.targetId,standalone:true};
  // Execute the actual update/rollback proof in the launched OS app window.
  for(const other of context.pages())if(other!==nativePage)await other.close();
  page=nativePage;
 }catch(error){result.native_pwa={status:'FAILED',error:String(error)};throw error;}
 const dirty=await context.newPage();await dirty.goto(origin+'/clinical-note',{waitUntil:'networkidle'});
 await dirty.locator('textarea').first().fill('SYNTHETIC OPEN ENCOUNTER — DO NOT RELOAD');
 const note=await dirty.locator('textarea').first().inputValue();
 await dirty.evaluate(()=>{window.__syntheticDocumentMarker=crypto.randomUUID()});
 const dirtyDocument=await dirty.evaluate(()=>window.__syntheticDocumentMarker);
 await page.goto(origin+'/calculator?drug=norepinephrine&weight=70&dose=0.05',{waitUntil:'networkidle'});
 await page.getByTestId('rate-display').waitFor();assert.equal(await page.getByTestId('rate-display').innerText(),'5.3');
 await page.screenshot({path:path.join(root,'EVIDENCIAS/A_INSTALADA.png'),fullPage:true});
 await stop();select(b);owned=await launch();assert.equal(owned.info.url,origin);
 assert.equal((await api(dirty,a.source_sha)).status,409);
 assert.equal(await dirty.locator('textarea').first().inputValue(),note);
 await page.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()});
 await page.getByTestId('local-update-notice').waitFor({timeout:35000});
 await dirty.getByTestId('local-update-notice').waitFor({timeout:35000});
 assert.equal(await dirty.getByTestId('local-update-confirm').isDisabled(),true);
 assert.equal(await dirty.getByTestId('local-update-apply').isDisabled(),true);
 await page.getByTestId('local-update-confirm').check();await page.getByTestId('local-update-apply').click();
 await identity(page,b);
 // The worker update must not have navigated or reconstructed the second tab.
 assert.equal(await dirty.evaluate(()=>window.__syntheticDocumentMarker),dirtyDocument);
 assert.equal(await dirty.locator('textarea').first().inputValue(),note);await identity(dirty,a);
 const encounter=await dirty.getByTestId('note-encounter').innerText();
 for(const destination of ['/pediatrics','/procedures']){
  // Popstate exercises the existing BrowserRouter without a document navigation.
  // Neither lazy module has been visited in this old-version document.
  await dirty.evaluate(destination=>{history.pushState({},'',destination);dispatchEvent(new PopStateEvent('popstate'))},destination);
  await dirty.getByTestId('local-stale-navigation').waitFor();
  await dirty.waitForURL(origin+'/clinical-note');
  assert.equal(await dirty.evaluate(()=>window.__syntheticDocumentMarker),dirtyDocument);
  assert.equal(await dirty.locator('textarea').first().inputValue(),note);
  assert.equal(await dirty.getByTestId('note-encounter').innerText(),encounter);
  await identity(dirty,a);
 }
 assert.equal((await api(page,b.source_sha)).status,200);
 const prefs=await page.evaluate(()=>({lang:localStorage.getItem('emergency.lang'),theme:localStorage.getItem('emergency.theme'),micro:localStorage.getItem('emergency.micro')}));
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
 await stop();select(a,'rollback');owned=await launch();assert.equal(owned.info.url,origin);
 await page.evaluate(async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()});
 await page.getByTestId('local-update-notice').waitFor({timeout:35000});
 await page.getByTestId('local-update-confirm').check();await page.getByTestId('local-update-apply').click();await identity(page,a);
 assert.deepEqual(await page.evaluate(()=>({lang:localStorage.getItem('emergency.lang'),theme:localStorage.getItem('emergency.theme'),micro:localStorage.getItem('emergency.micro')})),prefs);
 assert.equal((await api(page,a.source_sha)).status,200);
 await page.goto(origin+'/calculator?drug=norepinephrine&weight=70&dose=0.05',{waitUntil:'networkidle'});
 await stop();await context.setOffline(true);await page.reload({waitUntil:'domcontentloaded'});
 await page.getByTestId('rate-display').waitFor();assert.equal(await page.getByTestId('rate-display').innerText(),'5.3');
 const outage=await page.evaluate(async()=>{try{const r=await fetch('/api/clinical-note/new',{method:'POST',body:'{}'});return{status:r.status,type:r.headers.get('content-type')}}catch{return{network_failed:true}}});
 assert.equal(outage.network_failed,true);
 await page.screenshot({path:path.join(root,'EVIDENCIAS/A_ROLLBACK_OFFLINE.png'),fullPage:true});
 result.steps.push({test:'Explicit B→A rollback, preferences retained; server stopped and browser offline, cached calculator5.3, API fails explicitly',status:'PASS',outage});
 assert.deepEqual(errors,[]);assert.deepEqual(externals,[]);result.page_errors=errors;result.external_requests=externals;
}catch(error){result.errors.push(String(error));process.exitCode=1;}
finally{
 if(context)await context.setOffline(false).catch(()=>{});
 if(session&&nativeInstalled)try{await session.send('PWA.uninstall',{manifestId});result.native_pwa.test_installation_removed=true}catch(error){result.errors.push('Own PWA cleanup: '+String(error));process.exitCode=1}
 if(context)await context.close();await stop();
 fs.writeFileSync(path.join(root,'EVIDENCIAS/BROWSER_INDIVIDUAL_REAL.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result));
}
