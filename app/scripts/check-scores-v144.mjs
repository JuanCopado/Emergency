import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { withClinicalApp } from './functional-harness.mjs';
const qa=new URL('../../clinical/qa/',import.meta.url);
const cases=JSON.parse(readFileSync(new URL('V1.44_SCORE_CASES.json',qa),'utf8')).cases;
const flat=(obj,prefix='')=>Object.fromEntries(Object.entries(obj).flatMap(([k,v])=>v&&typeof v==='object'?Object.entries(flat(v,`${prefix}${k}.`)):[[prefix+k,v]]));
const report={cases:[],errors:[]};
await withClinicalApp(async({page,base,browser})=>{
  report.browser=browser.version();page.on('pageerror',e=>report.errors.push(e.message));
  for(const c of cases){
    await page.goto(`${base}/scores?score=${c.id}`);
    await page.locator('[data-field]').first().waitFor();
    for(const variant of ['normal','boundary']){
      const inputs=flat(c[variant]);
      for(const [key,value] of Object.entries(inputs)){
        const field=page.locator(`[data-field="${key}"]`);
        if(await field.evaluate(el=>el.tagName==='SELECT'))await field.selectOption(JSON.stringify(value));
        else await field.fill(String(value));
      }
      const responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/clinical-scores/calculate'));
      await page.getByRole('button',{name:c.id==='grace-2'?'Validar y abrir GRACE oficial':'Calcular',exact:true}).click();
      const response=await responsePromise;const body=await response.json();
      assert.equal(response.status(),200,JSON.stringify(body));
      for(const [k,v] of Object.entries(c['expected_'+variant]))assert.deepEqual(body.result[k],v);
      const result=page.getByRole('region',{name:'Resultado del score'});await result.waitFor();
      // Every scalar returned by the canonical engine is rendered, including warnings and units.
      const visible=await result.innerText();
      const check=value=>{if(value==null)return;if(typeof value==='object')return Object.values(value).forEach(check);assert(visible.includes(typeof value==='boolean'?(value?'Sí':'No'):String(value)),`UI omitted ${value}`);};
      check(body.result);
      await page.getByRole('button',{name:'Reiniciar',exact:true}).click();
      assert.equal(await result.count(),0);
      assert(await page.locator('[data-field]').evaluateAll(fields=>fields.every(f=>f.value==='')));
    }
    await page.getByRole('button',{name:c.id==='grace-2'?'Validar y abrir GRACE oficial':'Calcular',exact:true}).click();
    await page.getByRole('alert').filter({hasText:'requerido'}).waitFor();
    assert.equal(await page.getByRole('region',{name:'Resultado del score'}).count(),0);
    report.cases.push({id:c.id,normal:'PASS',boundary:'PASS',missing_input:'PASS',reset:'PASS',canonical_output_visible:'PASS'});
    console.log(`PASS ${c.id}: normal, boundary, missing, reset, canonical output`);
  }
  assert.deepEqual(report.errors,[]);
});
writeFileSync(new URL('V1.44_SCORE_BROWSER_RESULTS.json',qa),JSON.stringify(report,null,2)+'\n');
