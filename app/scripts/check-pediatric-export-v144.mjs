import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {withClinicalApp} from './functional-harness.mjs';

const bank=JSON.parse(readFileSync(new URL('../../clinical/qa/V1.44_PEDIATRIC_EXPORT_CASES.json',import.meta.url),'utf8'));
const labels={age_months:'Edad (meses)',actual_weight_kg:'Peso real (kg)',ideal_weight_kg:'Peso ideal (kg)'};
const results=[];
await withClinicalApp(async({page,base})=>{
  for(const c of bank.cases){
    await page.goto(`${base}/pediatrics?regimen=${c.calculation.regimen_id}`);
    for(const [key,value] of Object.entries(c.calculation.patient)){
      const field=page.getByLabel(labels[key]||key.replaceAll('_',' '),{exact:true});
      if(typeof value==='boolean')await field.selectOption(value?'yes':'no');else await field.fill(String(value));
    }
    if(c.calculation.selected_duration_days)await page.getByLabel('Duración elegida',{exact:false}).fill(String(c.calculation.selected_duration_days));
    if(c.calculation.product){
      await page.getByLabel('Concentración verificada (mg/mL)',{exact:true}).fill(String(c.calculation.product.concentration_mg_per_ml));
      await page.getByLabel('He verificado la concentración del producto exacto',{exact:true}).check();
    }
    const response=page.waitForResponse(r=>r.url().endsWith('/calculate'));
    await page.getByRole('button',{name:'Comprobar y calcular'}).click();
    const calculated=await (await response).json();assert.equal(calculated.blocked,false);
    const report=calculated.export_report;
    await page.getByText('Ver contenido íntegro de la exportación',{exact:true}).click();
    const visible=await page.getByTestId('pediatric-export-content').innerText();
    const norm=s=>s.replace(/\s+/g,'');
    for(const [heading,paragraphs] of report.sections)for(const text of [heading,...paragraphs])assert.ok(norm(visible).includes(norm(text)),text);
    const files={};
    for(const format of ['json','pdf','docx']){
      const promise=page.waitForEvent('download');await page.getByRole('button',{name:`Exportar ${format.toUpperCase()}`,exact:true}).click();
      const download=await promise;assert.equal(download.suggestedFilename(),`pediatric-result.${format}`);
      files[format]=readFileSync(await download.path());
    }
    assert.deepEqual(JSON.parse(files.json),report);
    // Exercise the print control, then render Chromium's actual print layout.
    await page.evaluate(()=>{globalThis.print=()=>{globalThis.__printed=true;};});
    await page.getByRole('button',{name:'Imprimir resultado'}).click();assert.equal(await page.evaluate(()=>globalThis.__printed),true);
    files.print=await page.pdf({format:'A4',printBackground:true});
    const check=spawnSync(process.env.CLINICAL_QA_PYTHON||'python',['-B','-c',`
import sys,json,base64,io,zipfile
from pypdf import PdfReader
from xml.etree import ElementTree
d=json.load(sys.stdin);norm=lambda s:''.join(s.split());pages={}
for fmt,b64 in d['files'].items():
 raw=base64.b64decode(b64)
 if fmt in ('pdf','print'):
  pdf=PdfReader(io.BytesIO(raw));pages[fmt]=len(pdf.pages);assert len(pdf.pages)>1
  text='\\n'.join(p.extract_text() for p in pdf.pages)
 else:
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   xml=ElementTree.fromstring(z.read('word/document.xml'));text='\\n'.join(x.text or '' for x in xml.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
 for heading,lines in d['sections']:
  for line in [heading,*lines]:assert norm(line) in norm(text),(fmt,line)
print(json.dumps(pages))
`],{input:JSON.stringify({sections:report.sections,files:Object.fromEntries(['pdf','docx','print'].map(f=>[f,files[f].toString('base64')]))}),encoding:'utf8',windowsHide:true});
    assert.equal(check.status,0,check.stderr);
    await page.getByLabel('Edad (meses)',{exact:true}).fill('121');
    assert.equal(await page.getByRole('button',{name:'Exportar JSON'}).count(),0);
    assert.equal(await page.locator('.pediatric-print-sheet').count(),0);
    results.push({id:c.id,json:'PASS',pdf:'PASS',docx:'PASS',print:'PASS',fidelity:'all canonical sections',invalidated_on_edit:'PASS',pages:JSON.parse(check.stdout)});
    console.log(`PASS pediatric exports: ${c.id}`);
  }
  await page.goto(`${base}/pediatrics?regimen=rizatriptan-migraine-rch`);
  await page.getByLabel('Edad (meses)',{exact:true}).fill('120');await page.getByLabel('Peso real (kg)',{exact:true}).fill('40');
  await page.getByLabel('secondary headache red flags excluded',{exact:true}).selectOption('yes');
  await page.getByRole('button',{name:'Comprobar y calcular'}).click();await page.getByRole('alert').filter({hasText:'no matching'}).waitFor();
  assert.equal(await page.getByRole('button',{name:'Exportar JSON'}).count(),0);
});
writeFileSync(new URL('../../clinical/qa/V1.44_PEDIATRIC_EXPORT_BROWSER_RESULTS.json',import.meta.url),JSON.stringify({cases:results,boundary_40kg:'blocked',clinical_status:'CLINICALLY_PENDING'},null,2)+'\n');
