import {chromium} from 'playwright-core';
import {fileURLToPath} from 'node:url';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const out=new URL('../../preview/combined/',import.meta.url);mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,chromiumSandbox:true});
const page=await browser.newPage({viewport:{width:1440,height:1080},serviceWorkers:'block'});
const errors=[];page.on('pageerror',e=>errors.push(e.message));const report={themes:[],navigation:[],checks:[],page_errors:errors};
const base='http://127.0.0.1:5186/design/arrhythmia-combined';
const guides=JSON.parse(readFileSync(new URL('../src/data/generatedClinicalGuides.json',import.meta.url)));
try{
await page.goto(base+'?theme=light');await page.getByRole('heading',{name:'Arritmias y parada cardíaca.'}).waitFor();
let geometry;
for(const theme of ['light','dark']){
 await page.setViewportSize({width:1440,height:1080});await page.goto(base+'?theme='+theme);
 const root=page.locator('.combined-preview');await root.waitFor();assert.equal(await root.getAttribute('data-theme'),theme);await page.evaluate(()=>globalThis.document.fonts.ready);assert.equal(await root.evaluate(el=>globalThis.getComputedStyle(el).fontFamily.includes('DM Sans Preview')),true);assert.equal(await page.evaluate(()=>globalThis.document.fonts.check('14px "DM Sans Preview"')),true);
 const rects=await page.locator('.circuit-link').evaluateAll(nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};}));
 if(geometry)assert.deepEqual(rects,geometry);else geometry=rects;
 assert.equal(await page.locator('.selector-master-status').innerText(),'YELLOW');assert.equal(await page.locator('.circuit-status[data-status=green]').count(),4);
 await page.screenshot({path:fileURLToPath(new URL(theme+'-desktop.png',out)),fullPage:true});
 for(const width of [390,320]){await page.setViewportSize({width,height:844});assert.equal(await page.evaluate(()=>globalThis.document.documentElement.scrollWidth>globalThis.innerWidth),false);if(width===390)await page.screenshot({path:fileURLToPath(new URL(theme+'-mobile.png',out)),fullPage:true});}
 report.themes.push({theme,status:'PASS',selector:'YELLOW',destinations_green:4,mobile_widths:[390,320]});
}
report.checks.push({name:'Same desktop layout in both themes',result:'PASS'},{name:'Self-hosted DM Sans loaded in both themes',result:'PASS'});
await page.setViewportSize({width:1440,height:1080});await page.goto(base+'?theme=light');const dark=page.getByRole('button',{name:'Oscuro',exact:true});await dark.focus();await page.keyboard.press('Enter');assert.equal(await dark.getAttribute('aria-pressed'),'true');await page.goto(base);assert.equal(await page.locator('.combined-preview').getAttribute('data-theme'),'dark');report.checks.push({name:'Keyboard theme switch and persistence',result:'PASS'});
for(const theme of ['light','dark'])for(const id of ['adult-arrhythmias','adult-cardiac-arrest','pediatric-arrhythmias','pediatric-cardiac-arrest']){
 await page.goto(base+'?theme='+theme);const nav=page.getByRole('navigation',{name:'Circuitos de reanimación'});await nav.waitFor();assert.equal(await nav.getByRole('link').count(),4);const link=nav.locator(`a[href="/guides/${id}"]`);await link.focus();await page.keyboard.press('Enter');await page.waitForURL('**/guides/'+id);await page.getByRole('heading',{level:1,name:guides.find(g=>g.id===id).title,exact:true}).waitFor();report.navigation.push({theme,target:id,result:'PASS'});
}
assert.deepEqual(errors,[]);report.status='PASS';
}finally{report.timestamp=new Date().toISOString();report.browser=browser.version();await browser.close();writeFileSync(new URL('validation.json',out),JSON.stringify(report,null,2));console.log(JSON.stringify(report));}