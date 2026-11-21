import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { withClinicalApp } from './functional-harness.mjs';

const directory = process.env.REVIEW_SHOTS_DIR || fileURLToPath(new URL('../review-shots/', import.meta.url));
await mkdir(directory, {recursive:true});
const report = {synthetic:true, external_provider_used:false, cases:[], screenshots:[]};
// The Python subprocess inherits these values. Even an unexpected path cannot use
// a configured external endpoint or a stored credential on this run.
delete process.env.CLINICAL_VISION_PROVIDER_URL;
delete process.env.CLINICAL_VISION_PROVIDER_TOKEN;

async function shot(page,name) {
  const file = '13-' + name + '.png';
  await page.screenshot({path:path.join(directory,file)});
  report.screenshots.push(file);
}

async function fixture(page,uniform) {
  const data = await page.evaluate(solid=>{
    const canvas = document.createElement('canvas');
    canvas.width=canvas.height=256;
    const ctx=canvas.getContext('2d');
    ctx.fillStyle='#456'; ctx.fillRect(0,0,256,256);
    if(!solid) {ctx.fillStyle='#f7a';ctx.fillRect(34,26,126,142);}
    return canvas.toDataURL('image/png').split(',')[1];
  },uniform);
  return {name:uniform?'uniforme.png':'geometria.png',mimeType:'image/png',buffer:Buffer.from(data,'base64')};
}

async function selectImage(page,synthetic,index) {
  await page.getByLabel('Carga clínica').setInputFiles(synthetic);
  const card=page.getByTestId('mcdt-review-card').nth(index);
  await card.waitFor();
  await page.waitForFunction(i=>document.querySelectorAll('[data-testid="mcdt-review-card"]')[i]===document.activeElement,index);
  const trigger=card.getByRole('button',{name:'Interpretar con módulo IA'});
  assert.ok(await trigger.isDisabled());
  for(const check of await card.getByRole('checkbox').all()) await check.check();
  assert.ok(await trigger.isEnabled());
  return {card,trigger};
}

try {
  await withClinicalApp(async({page,base,browser})=>{
    report.browser=browser.version();
    await page.goto(base+'/clinical-note');
    await page.getByTestId('note-tab-mcdt').click();
    const category=page.getByRole('button',{name:/Piel\/herida/});
    await category.focus();
    await page.keyboard.press('Space');
    assert.equal(await category.getAttribute('aria-pressed'),'true');
    const selection=await category.evaluate(element=>{
      const style=getComputedStyle(element);
      const rgb=s=>s.match(/[\d.]+/g)?.slice(0,3).map(Number);
      const luminance=values=>values.map(v=>v/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4)
        .reduce((a,v,i)=>a+v*[0.2126,0.7152,0.0722][i],0);
      const fg=style.color, bg=style.backgroundColor;
      let ratio=null;
      if(/^rgb\(/.test(fg)&&/^rgb\(/.test(bg)){
        const a=luminance(rgb(fg)), b=luminance(rgb(bg));
        ratio=Number(((Math.max(a,b)+0.05)/(Math.min(a,b)+0.05)).toFixed(2));
      }
      return {keyboard_focus:document.activeElement===element,foreground:fg,background:bg,contrast_ratio:ratio,
        font_size:style.fontSize,font_weight:style.fontWeight,scope:'selected category text only'};
    });
    assert.equal(selection.keyboard_focus,true);
    report.cases.push({id:'keyboard-category',source:'real Chromium DOM',...selection});

    const {card,trigger}=await selectImage(page,await fixture(page,true),0);
    const response=page.waitForResponse(r=>r.url().endsWith('/api/clinical-note/upload/interpret'));
    await trigger.click();
    const http=await response;
    assert.ok(http.ok());
    const value=await http.json(), processing=value.prepared.processing;
    assert.equal(processing.status,'vision_abstained');
    assert.ok(processing.safety_flags.includes('abstained_before_provider'));
    assert.ok(processing.limitations.some(s=>s.includes('no_visual_content_suspected')));
    assert.equal(processing.provider,null);
    await card.getByText(/Sin interpretación IA/).waitFor();
    await card.getByText(/No se pudo confirmar que hubiera contenido visual utilizable/).waitFor();
    await page.waitForFunction(()=>document.activeElement?.dataset.testid==='mcdt-review-card');
    await shot(page,'abstencion-real');
    report.cases.push({id:'uniform-image',source:'real browser, local backend, synthetic decoded pixels',http_status:http.status(),
      status:processing.status,safety_flags:processing.safety_flags,reported_provider:processing.provider,focus:'review card'});

    const second=await selectImage(page,await fixture(page,false),1);
    // Only this exact response is mocked. The previous interpretation and both
    // uploads, privacy checks and image validation run through the real backend.
    let intercepted=0;
    await page.route('**/api/clinical-note/upload/interpret',route=>{
      intercepted++;
      return route.fulfill({status:502,contentType:'application/json',body:JSON.stringify({
        error:'clinical vision provider returned an invalid response',
      })});
    },{times:1});
    await second.trigger.click();
    const alert=page.getByRole('alert').filter({hasText:'El servicio devolvió una respuesta no válida.'});
    await alert.waitFor();
    assert.ok(await alert.evaluate(el=>el===document.activeElement));
    assert.equal(intercepted,1);
    assert.equal(await second.card.getByLabel(/Hallazgos de la propuesta/).count(),0);
    await shot(page,'proveedor-502-simulado');
    report.cases.push({id:'provider-error-ui',source:'MOCK HTTP 502 on interpret only, real UI and prepare',
      external_provider_tested:false,focused_error:true,accepted_proposal:false});
  });
  report.status='PASS';
} catch(error) {
  report.status='FAIL'; report.error=String(error.message??error).slice(0,650);
  process.exitCode=1;
} finally {
  await writeFile(path.join(directory,'13-resultados.json'),JSON.stringify(report,null,2)+'\n');
  console.log('EXTRA_RESULT '+JSON.stringify(report));
}
