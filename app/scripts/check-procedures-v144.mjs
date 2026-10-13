import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {withClinicalApp} from './functional-harness.mjs';
const sheets=JSON.parse(readFileSync(new URL('../src/data/generatedProcedureSheets.json',import.meta.url),'utf8'));
const catalog=JSON.parse(readFileSync(new URL('../src/data/generatedProcedures.json',import.meta.url),'utf8'));
const results=[];
const aliases={'PROC-ENT-011':'PROC-ORTHO-022','PROC-PED-008':'PROC-ORTHO-004','PROC-SP-006':'PROC-EYE-001','PROC-US-007':'PROC-CV-006'};
await withClinicalApp(async({page,base})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const sheet of sheets){
    await page.goto(`${base}/procedures/${sheet.procedure_id}`);
    const article=page.getByRole('article');await article.waitFor();
    assert.equal(await article.getByRole('heading',{level:1}).innerText(),sheet.name);
    for(const label of ['STOP','Confirmación','Preámbulo canónico'])assert.equal(await article.getByRole('region',{name:label,exact:true}).isVisible(),true);
    assert.equal(await article.locator('details[open]').isVisible(),true);
    const text=(await article.innerText()).replace(/\s+/g,' ');
    for(const value of [sheet.provenance.family_preamble,...Object.values(sheet.provenance.sections),...(sheet.rescue||[]),...(sheet.escalation||[])])assert.ok(text.includes(value.replace(/\s+/g,' ')),sheet.procedure_id);
    assert.equal(await article.getByRole('region',{name:'Rescate y escalada'}).count(),sheet.rescue?.length || sheet.escalation?.length ? 1 : 0);
    results.push({id:sheet.procedure_id,status:'PASS',all_sections_visible:true});
  }
  for(const [alias,id] of Object.entries(aliases)){
    await page.goto(`${base}/procedures/${alias}`);
    assert.equal(await page.getByRole('article').getByRole('heading',{level:1}).innerText(),sheets.find(s=>s.procedure_id===id).name);
    await page.getByRole('link',{name:'← Procedimientos',exact:true}).click();
    await page.getByLabel('Nombre o PROC-ID').fill(alias);
    assert.equal(await page.getByRole('status').innerText(),'1 procedimientos');
    assert.equal(await page.getByRole('link',{name:new RegExp(id)}).getAttribute('href'),`/procedures/${id}`);
  }
  await page.getByLabel('Nombre o PROC-ID').fill(catalog[0].name);
  assert.ok((await page.getByRole('status').innerText())!=='0 procedimientos');
  await page.getByLabel('Nombre o PROC-ID').fill(catalog[0].id);
  await page.getByLabel('Familia').selectOption(catalog[0].family);await page.getByLabel('Nivel').selectOption(catalog[0].level);
  assert.equal(await page.getByRole('status').innerText(),'1 procedimientos');
  assert.deepEqual(errors,[]);
});
writeFileSync(new URL('../../clinical/qa/V1.44_PROCEDURE_BROWSER_RESULTS.json',import.meta.url),JSON.stringify({cases:results,aliases,search_and_filters:'PASS',clinical_status:'CLINICALLY_PENDING'},null,2)+'\n');
console.log('PASS 196 canonical sheets, 4 aliases, search/filter/navigation and source fidelity');
