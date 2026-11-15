// Local synthetic browser verification; not a clinical simulation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createServer} from 'vite';
import {chromium} from 'playwright-core';
import {chromiumPath} from './chromium.mjs';
const guides=JSON.parse(readFileSync(new URL('../src/data/generatedClinicalGuides.json',import.meta.url),'utf8'));
const targets=['adult-arrhythmias','adult-cardiac-arrest','pediatric-arrhythmias','pediatric-cardiac-arrest'];
const server=await createServer({server:{host:'127.0.0.1',port:0},logLevel:'error'});let browser;
try {
 await server.listen();const port=server.httpServer.address().port;
 browser=await chromium.launch({executablePath:chromiumPath(),headless:true,args:process.getuid?.()===0?['--no-sandbox']:[]});
 const page=await browser.newPage({serviceWorkers:'block'});const errors=[];page.on('pageerror',e=>errors.push(e.message));const results=[];
 for(const base of ['/guides','/clinical'])for(const id of targets){
  await page.goto(`http://127.0.0.1:${port}${base}/arrhythmias-cardiac-arrest`);
  const nav=page.getByRole('navigation',{name:'Circuitos de reanimación'});await nav.waitFor();assert.equal(await nav.getByRole('link').count(),4);
  const body=await page.locator('.canonical-body').innerText();assert.ok(body.includes('even if a pulse remains detectable'));assert.ok(body.includes('transition at birth'));
  const guide=guides.find(x=>x.id===id);assert.ok(guide);
  const link=nav.locator(`a[href="${base}/${id}"]`);assert.ok((await link.innerText()).includes(guide.status));await link.click();
  await page.waitForURL(`**${base}/${id}`);await page.getByRole('heading',{level:1,name:guide.title,exact:true}).waitFor();assert.equal(await page.getByRole('navigation',{name:'Circuitos de reanimación'}).count(),0);
  results.push({base,target:id,target_status:guide.status,result:'PASS'});
 }
 assert.deepEqual(errors,[]);const result={date:new Date().toISOString(),scope:'8 links/2 surfaces, pulse and neonatal exceptions, target content/status',results,page_errors:errors,status:'PASS',clinical_simulation:false};
 if(process.env.ROUTER_QA_OUTPUT)writeFileSync(process.env.ROUTER_QA_OUTPUT,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}catch(error){
 const result={date:new Date().toISOString(),status:'BLOCKED',stage:'browser_execution',reason:String(error.message).slice(0,600),clinical_simulation:false};
 if(process.env.ROUTER_QA_OUTPUT)writeFileSync(process.env.ROUTER_QA_OUTPUT,JSON.stringify(result,null,2)+'\n');
 throw error;
}finally{await browser?.close();await server.close();}
