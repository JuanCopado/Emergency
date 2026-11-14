/* global document, window */
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
try {
 const context=await browser.newContext({viewport:{width:1280,height:900}});const page=await context.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(process.env.INSULIN_APP_URL||'http://127.0.0.1:4173/');
 await page.getByRole('link',{name:'Insulinoterapia UCI · simulación',exact:true}).click();
 await page.getByRole('heading',{name:'Insulinoterapia UCI',exact:true}).waitFor();
 assert.equal(await page.getByText('RCCC',{exact:false}).count(),0);
 const fill=async(label,value)=>page.getByLabel(label,{exact:true}).fill(value);
 const select=async(label,value)=>page.getByLabel(label,{exact:true}).selectOption(value);
 const submit=async()=>{await page.getByLabel(/Usaré exclusivamente datos sintéticos/).check();await page.getByRole('button',{name:'Simular cálculo',exact:true}).click();};
 const result=()=>page.getByLabel('Resultado de simulación');
 await fill('Glucemia actual (mg/dL)','220');await fill('Glucemia previa (mg/dL)','220');await fill('Ritmo previo (UI/h)','2');await fill('Minutos entre controles','60');await submit();
 assert.match(await result().innerText(),/4 UI\/h/);
 await page.screenshot({path:'/tmp/emergency-insulin-local-desktop.png',fullPage:true});
 await fill('Glucemia actual (mg/dL)','120');assert.equal(await result().count(),0);
 await page.getByRole('button',{name:'Simular cálculo',exact:true}).click();assert.match(await result().innerText(),/Selecciona la reducción/);
 await select('Reducción prescrita (UI/h)','1');await page.getByRole('button',{name:'Simular cálculo',exact:true}).click();assert.match(await result().innerText(),/1 UI\/h/);
 await page.getByRole('button',{name:'Inicio IV',exact:true}).click();await fill('Glucemia actual (mg/dL)','250');await select('Hiperglucemia persistente confirmada','yes');await submit();assert.match(await result().innerText(),/Ritmo inicial pendiente/);
 await page.getByRole('button',{name:'Reinicio IV',exact:true}).click();await fill('Glucemia actual (mg/dL)','141');await fill('Ritmo previo a la pausa (UI/h)','4');await select('Motivo de la pausa','preventive');await submit();assert.match(await result().innerText(),/2 UI\/h/);
 await page.getByRole('button',{name:'Transición SC',exact:true}).click();await fill('Ritmo medio IV (UI/h)','1');await fill('Horas estables evaluadas','6');await select('Estabilidad clínica y hemodinámica','yes');await select('Nutrición estable','yes');await submit();assert.match(await result().innerText(),/14,4–19,2 UI\/día/);
 await page.getByRole('button',{name:'Bolo prescrito',exact:true}).click();await fill('Glucemia actual (mg/dL)','350');await select('Indicación médica del bolo','severe-unresponsive');await fill('Dosis de bolo prescrita (UI)','4');await submit();assert.equal(await page.getByTestId('bolus-volume').count(),0);
 await context.setOffline(true);await select('Existe prescripción médica explícita','yes');await page.getByRole('button',{name:'Simular cálculo',exact:true}).click();assert.match(await page.getByTestId('bolus-volume').innerText(),/4 UI = 4 mL/);
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'Mobile overflow');
 await page.screenshot({path:'/tmp/emergency-insulin-local-mobile.png',fullPage:true});
 await page.getByRole('button',{name:'Borrar datos',exact:true}).click();assert.equal(await result().count(),0);assert.deepEqual(errors,[]);
 console.log('PASS: five local workflows, rate and volume, explicit reduction, no inferred starting rate, preventive restart, SC range, prescribed bolus gate, offline arithmetic, mobile width, reset, no page errors. Synthetic values only.');
}finally{await browser.close();}
