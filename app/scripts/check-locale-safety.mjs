// Synthetic-only integration checks against the real built frontend in Chromium.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';
const server=await preview({preview:{host:'127.0.0.1',port:0},logLevel:'error'});
let browser;
let checks=0;
const passed=()=>{checks++;};
try {
 browser=await chromium.launch({executablePath:chromiumPath(),headless:true,args:['--no-sandbox']});
 const url=server.resolvedUrls.local[0];
 for(const [lang,decimal,rate,stop] of [['es',',','5,3','STOP de privacidad'],['pt',',','5,3','STOP privacidade'],['en','.','5.3','Privacy STOP'],['zh','.','5.3','隐私 STOP']]) {
  const labels=JSON.parse(readFileSync(new URL(`../src/i18n/locales/${lang}.clinical.json`,import.meta.url)));
  const context=await browser.newContext({serviceWorkers:'block'});
  await context.addInitScript(code=>localStorage.setItem('emergency.lang',code),lang);
  const page=await context.newPage();const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${url}calculator?drug=norepinephrine&weight=70&dose=0.05`);
  await page.getByTestId('rate-display').waitFor();
  assert.equal(await page.getByTestId('rate-display').innerText(),rate);passed();
  assert.equal(await page.getByTestId('calc-dose').inputValue(),'0.05');passed();
  await page.getByTestId('language-switcher').selectOption(lang==='en'?'es':'en');
  assert.equal(await page.getByTestId('rate-display').innerText(),lang==='en'?'5,3':'5.3');
  assert.equal(await page.getByTestId('calc-dose').inputValue(),'0.05');passed();
  await page.getByTestId('language-switcher').selectOption(lang);
  await page.getByTestId('calc-dose').fill('1,000');
  assert.equal(await page.getByTestId('rate-display').count(),0);assert.equal(await page.getByTestId('calc-dose').getAttribute('aria-invalid'),'true');passed();
  await page.goto(`${url}clinical-note`);
  await page.getByTestId('note-origin').fill('Name: Synthetic fixture');
  assert.ok((await page.getByRole('alert').innerText()).includes('STOP'));
  await page.getByText(stop,{exact:true}).waitFor();
  await page.getByTestId('note-tab-export').click();assert.equal(await page.getByRole('button',{name:'PDF',exact:true}).isDisabled(),true);passed();
  await page.getByTestId('note-origin').fill('');await page.getByLabel(labels['Idade'],{exact:true}).fill('1,000');
  await page.getByTestId('note-tab-diagnostic').click();
  assert.equal(await page.getByRole('button',{name:labels['Atualizar apoio diagnóstico'],exact:true}).isDisabled(),true);passed();
  const calls=[];
  await page.route('**/api/acute-medications/**',async route=>{
   const body=route.request().postDataJSON();
   if(route.request().url().endsWith('/catalog'))return route.fulfill({json:{source_revision:'synthetic',regimens:[{id:'fixture',label:'Synthetic fixture',group:'test',group_label:'Synthetic group',drug:'Synthetic',route:'IV',dose_unit:'mg',fields:[{key:'value',label:'Synthetic number',kind:'number'}],limitations:[],source:{body:'Canonical source',preamble:'Synthetic'}}]}});
   calls.push(body);
   const blocked=body.inputs.value===2;
   await route.fulfill({json:blocked?{blocked:true,alerts:[{code:'synthetic',message:'Canonical STOP: review required'}]}:{blocked:false,alerts:[],result:{dose:0.1,components:{sample:1000.5},monitoring_and_warnings:'Canonical warning'},report:{snapshot:{dose:0.1},sections:[['Source',['Canonical warning']]]}}});
  });
  await page.goto(`${url}acute-medications`);
  await page.getByTestId('acute-group').selectOption('test');await page.getByTestId('acute-regimen').selectOption('fixture');
  await page.getByLabel('Synthetic number').fill('0.1');await page.getByTestId('acute-form').evaluate(form=>form.requestSubmit());
  await page.locator('[data-result="dose"]').waitFor();
  assert.equal(await page.locator('[data-result="dose"]').innerText(),`0${decimal}1`);
  assert.ok((await page.locator('[data-result="components"]').innerText()).includes(`1000${decimal}5`));
  assert.deepEqual(calls[0],{regimen_id:'fixture',source_revision:'synthetic',inputs:{value:0.1}});passed();
  assert.equal(await page.getByRole('button',{name:`${labels['Exportar']} JSON`,exact:true}).isDisabled(),true);passed();
  await page.getByLabel('Synthetic number').fill('1,000');await page.getByTestId('acute-form').evaluate(form=>form.requestSubmit());
  await page.getByRole('alert').waitFor();assert.equal(calls.length,1);assert.equal(await page.getByTestId('acute-export').count(),0);passed();
  await page.getByLabel('Synthetic number').fill('2');await page.getByTestId('acute-form').evaluate(form=>form.requestSubmit());
  await page.getByRole('heading',{name:labels['Cálculo bloqueado'],exact:true}).waitFor();
  assert.ok((await page.getByRole('alert').innerText()).includes('Canonical STOP'));
  assert.equal(await page.getByTestId('acute-export').count(),0);passed();
  assert.deepEqual(errors,[]);passed();
  await context.close();console.log(`PASS ${lang}: canonical input, localized output, live language switch, privacy, age, acute result and export guards`);
 }
 console.log(JSON.stringify({status:'PASS',browser:'Chromium',checks,synthetic_only:true}));
} finally {await browser?.close();await new Promise(resolve=>server.httpServer.close(resolve));}
