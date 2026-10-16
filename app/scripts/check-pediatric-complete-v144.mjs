import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { writeEvidence } from './write-qa-evidence.mjs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { withClinicalApp } from './functional-harness.mjs';

const fixtures = JSON.parse(readFileSync(new URL('../../clinical/qa/V1.44_PEDIATRIC_BROWSER_CASES.json', import.meta.url), 'utf8'));
const catalog = JSON.parse(readFileSync(new URL('../src/data/generatedPediatricOutpatient.json', import.meta.url), 'utf8'));
const only = process.env.PEDIATRIC_CASE_FILTER;
const target = new URL(`../../clinical/qa/V1.44_PEDIATRIC_${only ? 'FILTERED' : 'COMPLETE'}_BROWSER_RESULTS.json`, import.meta.url);
const source = readFileSync(new URL('../../clinical/qa/pediatric-outpatient-medications.json', import.meta.url));
assert.equal(createHash('sha256').update(source).digest('hex'), fixtures.source_sha256, 'Regenerate stale pediatric fixtures');
assert.deepEqual([...new Set(fixtures.cases.map(c => c.regimen_id))].sort(), catalog.regimens.map(r => r.id).sort(), 'Fixtures must cover the entire catalog');
const norm = s => String(s).replace(/\s+/g, ' ').trim();
const at = (obj, path) => path.split('.').reduce((value, key) => value?.[key], obj);
const labels = {age_months:'Edad (meses)', actual_weight_kg:'Peso real (kg)', ideal_weight_kg:'Peso ideal (kg)', adjusted_weight_kg:'Peso ajustado (kg)', egfr_mL_min:'Filtrado renal (mL/min)', known_renal_impairment:'Insuficiencia renal conocida', known_hepatic_impairment:'Insuficiencia hepática conocida'};
const selectedLabels = {selected_duration_days:'Duración elegida', selected_dose_per_kg:'Dosis elegida dentro', selected_volume_ml:'Volumen elegido dentro'};
const results = {started_at:new Date().toISOString(), clinical_status:'CLINICALLY_PENDING', source_sha256:fixtures.source_sha256, source_revision:catalog.source_revision, oracle:fixtures.oracle, cases:[], page_errors:[]};
const repository = new URL('../../', import.meta.url);
const sourcePaths = [
  'clinical/scripts/pediatric_outpatient_calculator.py',
  'clinical/scripts/pediatric_outpatient_api.py',
  'clinical/scripts/pediatric_outpatient_alert_engine.py',
  'clinical/scripts/pediatric_result_exporter.py',
  'clinical/qa/build_pediatric_browser_cases_v144.py',
  'clinical/qa/V1.44_PEDIATRIC_BROWSER_CASES.json',
  'app/scripts/check-pediatric-complete-v144.mjs',
  'app/src/pages/PediatricOutpatient.tsx',
  'app/src/pediatrics/PediatricExport.tsx',
  'app/src/data/generatedPediatricOutpatient.json',
  'app/dist/index.html',
  ...readdirSync(new URL('../dist/assets/', import.meta.url)).sort().map(name => `app/dist/assets/${name}`),
];
results.provenance = {
  head: execFileSync('git', ['rev-parse', 'HEAD'], {cwd:fileURLToPath(repository), encoding:'utf8', windowsHide:true}).trim(),
  sha256: Object.fromEntries(sourcePaths.map(path => [path, createHash('sha256').update(readFileSync(new URL(path, repository))).digest('hex')])),
};
const cases = fixtures.cases.filter(c => !only || c.id.includes(only));
assert.ok(cases.length, 'No pediatric cases match the filter');
await withClinicalApp(async ({page, base, browser}) => {
  results.browser = browser.version();
  page.on('pageerror', e => results.page_errors.push(e.message));
  for (const c of cases) {
    const record = {id:c.id, regimen_id:c.regimen_id, scenario:c.scenario, input: {patient:c.patient, product:c.product, ...Object.fromEntries(Object.keys(selectedLabels).filter(k=>c[k]!==undefined).map(k=>[k,c[k]]))}, expected_rejection:c.expect_rejection, expected:c.expect, expected_alerts:c.expect_alerts, source_band_gap:c.source_band_gap || false};
    try {
      const regimen = catalog.regimens.find(e => e.id === c.regimen_id);
      await page.goto(`${base}/pediatrics`);
      await page.getByLabel('Fármaco o combinación').selectOption(regimen.drug_id);
      await page.getByLabel('Diagnóstico y régimen').selectOption(c.regimen_id);
      for (const [key, value] of Object.entries(c.patient)) {
        if (key === 'allergies' || key === 'active_medications') {
          if (value === null) continue;
          await page.getByLabel(key === 'allergies' ? 'Alergias: sustancias o clases, separadas por comas' : 'Medicamentos actuales, separados por comas', {exact:true}).fill(value.join(','));
          await page.getByLabel(key === 'allergies' ? 'Estado de alergias revisado' : 'Medicación actual revisada').check();
        } else {
          const field = key === 'hepatic_severity' ? page.getByLabel(/^Gravedad de insuficiencia hepática/) : page.getByLabel(labels[key] || key.replaceAll('_', ' '), {exact:true});
          if (typeof value === 'boolean') await field.selectOption(value ? 'yes' : 'no');
          else if (key === 'hepatic_severity') await field.selectOption(value);
          else await field.fill(String(value));
        }
      }
      for (const [key, title] of Object.entries(selectedLabels)) if (c[key] !== undefined) await page.getByLabel(title).fill(String(c[key]));
      if (c.product) {
        await page.getByLabel('Concentración verificada (mg/mL)', {exact:true}).fill(String(c.product.concentration_mg_per_ml));
        await page.getByLabel('He verificado la concentración del producto exacto', {exact:true}).check();
      }
      const responsePromise = c.local_error ? null : page.waitForResponse(r => r.url().endsWith('/api/pediatric-outpatient/calculate'));
      await page.getByRole('button', {name:'Comprobar y calcular'}).click();
      if (c.local_error) {
        await page.getByRole('alert').waitFor();
        record.error = await page.getByRole('alert').innerText();
        assert.equal(await page.getByRole('region', {name:'Resultado pediátrico'}).count(), 0);
      } else {
        const response = await responsePromise;
        const data = await response.json();
        record.http_status = response.status();
        record.blocked = data.blocked;
        record.error = data.error;
        record.alerts = data.safety?.alerts;
        for (const code of c.expect_alerts) assert.ok(data.safety?.alerts.some(a=>a.code===code), `Missing ${code}`);
        if (c.expect_rejection) {
          assert.ok(data.blocked || !response.ok(), `Expected rejection; ${JSON.stringify(data.result)}`);
          if (data.blocked) await page.getByRole('heading', {name:'Cálculo bloqueado', exact:true}).waitFor();
          else await page.getByRole('alert').waitFor();
          assert.equal(await page.getByRole('button', {name:'Exportar JSON', exact:true}).count(), 0);
        } else {
          assert.equal(response.status(), 200, JSON.stringify(data));
          assert.equal(data.blocked, false, JSON.stringify(data));
          const region = page.getByRole('region', {name:'Resultado pediátrico'});
          await region.waitFor();
          const visible = norm(await region.innerText());
          record.actual = {};
          for (const [path, expected] of Object.entries(c.expect)) {
            const value = at(data.result, path);
            record.actual[path] = value;
            if (typeof expected === 'number') assert.ok(typeof value === 'number' && Math.abs(value-expected)<1e-8*Math.max(1,Math.abs(expected)), `${path}: ${value} != ${expected}`);
            else assert.deepEqual(value, expected, path);
          }
          for (const [path, label] of Object.entries({dose_mg:'Dosis por toma (mg)', dose_mg_per_kg:'Dosis (mg/kg)', 'volume_per_dose.exact_ml':'Volumen exacto (mL)', total_rehydration_ml:'total rehydration ml', dose_unit:'dose unit'})) {
            if (path in c.expect) assert.ok(visible.includes(label), `Missing visible unit label ${label}`);
          }
          const reference = norm(await page.getByRole('region', {name:'Ficha canónica'}).innerText());
          for (const text of [...(regimen.cautions || []), ...(regimen.contraindications || []), regimen.administration, regimen.frequency].filter(Boolean)) assert.ok(reference.includes(norm(text)), `Missing reference ${text}`);
          assert.ok(visible.includes('requiere revisión clínica'));
          record.visible_result_sha256 = createHash('sha256').update(visible).digest('hex');
          if (c.scenario === 'nominal') {
            const pending = page.waitForEvent('download');
            await page.getByRole('button', {name:'Exportar JSON', exact:true}).click();
            const exported = JSON.parse(readFileSync(await (await pending).path(), 'utf8'));
            assert.deepEqual(exported.snapshot.result, data.result);
            assert.deepEqual(exported.snapshot.safety, data.safety);
            record.export = 'PASS';
            record.visible_result = visible;
            record.result = data.result;
          }
        }
        if (data.safety) {
          const visible = norm(await page.getByRole('region', {name:'Resultado pediátrico'}).innerText());
          for (const alert of data.safety.alerts) for (const text of [alert.message, alert.action].filter(Boolean)) assert.ok(visible.includes(norm(text)), `Missing alert ${alert.code}`);
        }
      }
      await page.getByLabel('Edad (meses)', {exact:true}).fill('');
      assert.equal(await page.getByRole('region', {name:'Resultado pediátrico'}).count(), 0, 'Stale result after edit');
      assert.equal(await page.getByRole('button', {name:'Exportar JSON', exact:true}).count(), 0);
      record.status = 'PASS';
    } catch (error) {
      record.status = 'FAIL'; record.failure = error.stack;
      console.error(`FAIL ${c.id}: ${error.message.split('\n')[0]}`);
    }
    results.cases.push(record);
    if (c.scenario === 'nominal' || record.status === 'FAIL') console.log(`${record.status} ${c.id}`);
    await writeEvidence(target, results);
  }
});
results.finished_at = new Date().toISOString();
results.summary = {regimens:new Set(results.cases.map(c=>c.regimen_id)).size, scenarios:results.cases.length, pass:results.cases.filter(c=>c.status==='PASS').length, fail:results.cases.filter(c=>c.status==='FAIL').length, nominal_exports:results.cases.filter(c=>c.export==='PASS').length};
await writeEvidence(target, results);
console.log(JSON.stringify(results.summary));
if (results.summary.fail || results.page_errors.length) process.exitCode = 1;
