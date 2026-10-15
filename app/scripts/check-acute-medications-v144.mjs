import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { withClinicalApp } from './functional-harness.mjs';

const bank = JSON.parse(readFileSync(new URL('../../clinical/qa/V1.44_ACUTE_MEDICATION_CASES.json', import.meta.url),'utf8'));
const group = process.env.FLOW_FILTER || 'all';
const cases = bank.cases.filter(c => group === 'all' || c.group === group);
assert.ok(cases.length, 'Empty flow filter');
const record = {started_at:new Date().toISOString(), clinical_status:'CLINICALLY_PENDING', group, cases:[], errors:[]};
const target = new URL(`../../clinical/qa/V1.44_ACUTE_${group.toUpperCase()}_BROWSER_RESULTS.json`, import.meta.url);
const norm = s => s.replace(/\s+/g,'');
try {
  await withClinicalApp(async ({page,context,base,browser}) => {
    record.browser = browser.version(); page.on('pageerror', e => record.errors.push(e.message));
    const response = await context.request.post(`${base}/api/acute-medications/catalog`, {data:{}});
    assert.equal(response.status(), 200);
    const catalog = await response.json(); record.source_revision = catalog.source_revision;
    record.fixtures_sha256 = createHash('sha256').update(readFileSync(new URL('../../clinical/qa/V1.44_ACUTE_MEDICATION_CASES.json',import.meta.url))).digest('hex');
    for (const c of cases) {
      await page.goto(`${base}/drugs`);
      await page.getByRole('link',{name:'Farmacología aguda por indicación'}).click();
      await page.getByRole('heading',{name:'Farmacología aguda',exact:true}).waitFor();
      await page.getByLabel('Grupo farmacológico',{exact:true}).selectOption(c.group);
      await page.getByLabel('Indicación y opción',{exact:true}).selectOption(c.id);
      const row = catalog.regimens.find(r => r.id === c.id);
      const inputs = Object.fromEntries(Object.entries({...bank.common,...c.inputs}).filter(([k]) => row.fields.some(f => f.key === k)));
      for (const [key,value] of Object.entries(inputs)) {
        const f = row.fields.find(f => f.key === key);
        const field = page.locator(`[data-field="${key}"]`);
        if (f.kind === 'number') await field.fill(String(value));
        else await field.selectOption(typeof value === 'boolean' ? value ? 'yes' : 'no' : value);
      }
      const pending = page.waitForResponse(r => r.url().endsWith('/api/acute-medications/calculate'));
      await page.getByRole('button',{name:'Comprobar y calcular'}).click();
      const calculated = await (await pending).json();
      assert.equal(calculated.blocked, false, JSON.stringify(calculated));
      await page.getByRole('region',{name:'Resultado farmacológico'}).waitFor();
      for (const [key,value] of Object.entries(c.expect)) {
        assert.deepEqual(calculated.result[key], value, `${c.id}: ${key}`);
        if (await page.locator(`[data-result="${key}"]`).count()) {
          const shown = await page.locator(`[data-result="${key}"]`).innerText();
          assert.ok(value === null ? shown.includes('No especificado') : shown === String(value), `${key} rendered`);
        }
      }
      assert.equal(norm(await page.getByTestId('acute-warnings').innerText()), norm(calculated.result.monitoring_and_warnings));
      assert.equal(await page.getByRole('button',{name:'Exportar JSON',exact:true}).isDisabled(), true);
      await page.getByLabel('Confirmo haber revisado').check();
      const files = {};
      for (const format of ['json','pdf','docx']) {
        const downloaded = page.waitForEvent('download').catch(error => ({error}));
        const exported = page.waitForResponse(r => r.url().endsWith('/api/acute-medications/export'));
        await page.getByRole('button',{name:`Exportar ${format.toUpperCase()}`,exact:true}).click();
        const exportedResponse = await exported;
        assert.equal(exportedResponse.status(), 200, JSON.stringify(await exportedResponse.json()));
        const file = await downloaded; if (file.error) throw file.error;
        files[format] = readFileSync(await file.path());
      }
      assert.deepEqual(JSON.parse(files.json), calculated.report);
      await page.evaluate(() => {globalThis.print = () => {globalThis.__acutePrinted = true;};});
      await page.getByRole('button',{name:'Imprimir resultado'}).click();
      assert.equal(await page.evaluate(() => globalThis.__acutePrinted), true);
      files.print = await page.pdf({format:'A4',printBackground:true});
      const check = spawnSync(process.env.CLINICAL_QA_PYTHON || 'python', ['-B','-c', `
import io,json,base64,zipfile,sys
from pypdf import PdfReader
from xml.etree import ElementTree
d=json.load(sys.stdin);norm=lambda s:''.join(s.split());pages={}
for fmt,b64 in d['files'].items():
 raw=base64.b64decode(b64)
 if fmt in ('pdf','print'):
  pdf=PdfReader(io.BytesIO(raw));pages[fmt]=len(pdf.pages);text='\\n'.join(p.extract_text() for p in pdf.pages)
 else:
  with zipfile.ZipFile(io.BytesIO(raw)) as z:xml=ElementTree.fromstring(z.read('word/document.xml'))
  text='\\n'.join(x.text or '' for x in xml.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
 for heading,paragraphs in d['sections']:
  for expected in [heading]+paragraphs:assert norm(expected) in norm(text),(fmt,expected)
print(json.dumps(pages))
`], {input:JSON.stringify({sections:calculated.report.sections,files:Object.fromEntries(['pdf','docx','print'].map(k=>[k,files[k].toString('base64')]))}),encoding:'utf8',windowsHide:true});
      assert.equal(check.status, 0, check.stderr);
      const gates = [];
      for (const [key,value] of Object.entries({route:'PO',allergy_contraindication_present:true,monitoring_ready:false,...(row.fields.some(f=>f.key==='concentration')?{concentration:0}:{})})) {
        const data = await context.request.post(`${base}/api/acute-medications/calculate`, {data:{regimen_id:c.id,source_revision:catalog.source_revision,inputs:{...inputs,[key]:value}}});
        const body = await data.json(); assert.equal(body.blocked,true,`${c.id}: ${key}`); assert.equal(body.result,undefined); gates.push({key,value,alerts:body.alerts});
      }
      const field = page.locator('[data-field="route"]'); await field.selectOption('PO');
      assert.equal(await page.getByRole('region',{name:'Resultado farmacológico'}).count(),0);
      assert.equal(await page.locator('.acute-print-sheet').count(),0);
      await page.getByRole('button',{name:'Comprobar y calcular'}).click();
      await page.getByRole('heading',{name:'Cálculo bloqueado',exact:true}).waitFor();
      assert.equal(await page.getByRole('button',{name:'Exportar JSON',exact:true}).count(),0);
      record.cases.push({id:c.id,status:'PASS',inputs,expected:c.expect,actual:calculated.result,report:calculated.report,gates,exports:['json','pdf','docx','print'],pages:JSON.parse(check.stdout),invalidation:'PASS'});
      console.log(`PASS acute flow: ${c.id}`);
    }
    assert.deepEqual(record.errors,[]);
  });
  record.status = 'PASS';
} catch (e) {record.status = 'FAIL';record.failure = e.stack;process.exitCode = 1;console.error(e);}
record.finished_at = new Date().toISOString();
writeFileSync(target, JSON.stringify(record,null,2)+'\n');
