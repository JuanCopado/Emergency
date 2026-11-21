import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { withClinicalApp } from './functional-harness.mjs';

const out = process.env.REVIEW_SHOTS_DIR || fileURLToPath(new URL('../review-shots/', import.meta.url));
const bank = JSON.parse(await readFile(new URL('../../clinical/qa/V1.44_ACUTE_MEDICATION_CASES.json', import.meta.url),'utf8'));
const fixture = bank.cases.find(x => x.case_id === 'status-phenytoin-dose-only');
const report = {case: fixture.case_id, scope:'Chromium print CSS, synthetic case; native dialog not observed', samples:[]};
await mkdir(out,{recursive:true});
const py = process.env.CLINICAL_QA_PYTHON || 'python';
const extractor = [
  'import io,json,sys,re',
  'from pypdf import PdfReader',
  'r=PdfReader(io.BytesIO(sys.stdin.buffer.read()))',
  'targets=json.loads(sys.argv[1])',
  'clean=lambda s: re.sub(r"\\s+","",s).casefold()',
  'pages=[[clean(x) for x in p.extract_text().splitlines() if clean(x)] for p in r.pages]',
  'print(json.dumps({"pages":len(pages),"hits":[[[i+1,j+1] for i,p in enumerate(pages) for j,x in enumerate(p) if x==clean(t)] for t in targets]}))'
].join('\n');
function inspect(buf,targets) {
  const q=spawnSync(py,['-B','-c',extractor,JSON.stringify(targets)],{input:buf,maxBuffer:2e6});
  assert.equal(q.status,0,q.stderr?.toString());
  return JSON.parse(q.stdout.toString());
}
try {
  await withClinicalApp(async ({page,base,browser}) => {
    report.chromium=browser.version();
    await page.setViewportSize({width:794,height:1000});
    const catResponse=page.waitForResponse(r=>r.url().includes('/api/acute-medications/catalog') && r.status()===200);
    await page.goto(base+'/drugs');
    await page.getByRole('link',{name:'Farmacología aguda por indicación'}).click();
    const cat=await (await catResponse).json();
    const row=cat.regimens.find(x=>x.id===fixture.id);
    const values={...bank.common,...fixture.inputs};
    await page.getByLabel('Grupo farmacológico',{exact:true}).selectOption(fixture.group);
    await page.getByLabel('Indicación y opción',{exact:true}).selectOption(fixture.id);
    for(const f of row.fields){
      if(f.required_if && values[f.required_if.key]!==f.required_if.equals) continue;
      const ctl=page.locator('[data-field="'+f.key+'"]');
      const v=values[f.key];
      if(f.kind==='number') await ctl.fill(String(v));
      else await ctl.selectOption(typeof v==='boolean'?(v?'yes':'no'):String(v));
    }
    const request=page.waitForResponse(r=>r.url().endsWith('/api/acute-medications/calculate'));
    await page.getByRole('button',{name:'Comprobar y calcular',exact:true}).click();
    const value=await (await request).json();
    assert.equal(value.blocked,false);
    assert.equal(value.result.dose,fixture.expect.dose);
    assert.equal(value.result.dose_unit,fixture.expect.dose_unit);
    await page.getByLabel('Confirmo haber revisado').check();
    const printButton=page.getByRole('button',{name:'Imprimir resultado',exact:true});
    assert.ok(await printButton.isEnabled());
    await page.emulateMedia({media:'print'});
    const g=page.locator('.acute-print-sheet .acute-print-measure').first();
    await g.waitFor();
    const measured=await g.evaluate(el=>({prior:el.previousElementSibling.textContent.trim(),pair:[...el.querySelectorAll('p')].map(p=>p.textContent.trim()),top:el.getBoundingClientRect().top+window.scrollY,line:el.firstElementChild.getBoundingClientRect().height,avoid:getComputedStyle(el).breakInside}));
    assert.equal(measured.avoid,'avoid');
    report.group=measured;
    const targets=[measured.prior,...measured.pair];
    const origin=Math.ceil(measured.top+measured.line);
    const heights=[...new Set([0,-3,3,-6,6,-10,10,-14,14,-20,20,-27,27,-35,35,-45,45,-60,60,...Array.from({length:39},(_,i)=>(i-19)*8)].map(delta=>origin+delta).filter(v=>v>=240))];
    for(const h of heights) {
      const layout=await page.addStyleTag({content:'@page acute-report {size: 794px '+h+'px; margin:0;}'});
      const css=await page.addStyleTag({content:'@media print {.acute-print-sheet .acute-print-measure {break-inside:auto !important; page-break-inside:auto !important;}}'});
      assert.equal(await g.evaluate(el=>getComputedStyle(el).breakInside),'auto');
      const opts={preferCSSPageSize:true,printBackground:true,displayHeaderFooter:false};
      const control=inspect(await page.pdf({...opts,pageRanges:'1-2'}),targets);
      await css.evaluate(n=>n.remove());
      assert.equal(await g.evaluate(el=>getComputedStyle(el).breakInside),'avoid');
      const dh=control.hits[1][0], uh=control.hits[2][0];
      report.samples.push({height_px:h,control});
      if(dh && uh && uh[0]===dh[0]+1) {
        const original=await page.pdf(opts);
        const p=inspect(original,targets);
        report.samples.at(-1).original=p;
        const d=p.hits[1][0], u=p.hits[2][0];
        if(d && u && d[0]===u[0] && u[1]===d[1]+1 && d[1]<=3 && p.hits[0].some(x=>x[0]===d[0]-1)) {
          report.pass=true;
          report.witness={height_px:h,width_px:794,margin_px:0,control,original:p,targets};
          await writeFile(path.join(out,'Q5_CHROMIUM_FRONTERA.pdf'),original);
        }
      }
      await layout.evaluate(n=>n.remove());
      if(report.pass) break;
    }
    assert.ok(report.pass,'No boundary witness meeting all predeclared conditions');
  });
} catch(e) {report.pass=false; report.error=String(e); process.exitCode=1;}
await writeFile(path.join(out,'Q5_CHROMIUM_FRONTERA.json'),JSON.stringify(report,null,2));
console.log('PRINT_RESULT '+JSON.stringify(report));
