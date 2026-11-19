import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { withClinicalApp } from './functional-harness.mjs';
import { writeEvidence } from './write-qa-evidence.mjs';

// One driver for the reviewed release and the legacy all-contract entry point.
// Historical v1.44 evidence is written only when its compatibility wrapper runs.
const bankURL = new URL('../../clinical/qa/V1.44_ACUTE_MEDICATION_CASES.json', import.meta.url);
const acceptanceURL = new URL('../../clinical/references/acute-contract-owner-acceptance-2026-11-16.json', import.meta.url);
const bankBytes = readFileSync(bankURL);
const acceptanceBytes = readFileSync(acceptanceURL);
const bank = JSON.parse(bankBytes);
const acceptance = JSON.parse(acceptanceBytes);
const acceptedIDs = new Set(acceptance.contract_ids);
const scope = process.env.ACUTE_SCOPE || 'reviewed';
const group = process.env.FLOW_FILTER || 'all';
const exportsOnly = process.argv.includes('--exports-only');
const legacyOutput = process.env.ACUTE_LEGACY_OUTPUT === '1';
assert.ok(['reviewed', 'all'].includes(scope), 'ACUTE_SCOPE must be reviewed or all');
assert.ok(group === 'all' || bank.cases.some(item => item.group === group), 'Unknown FLOW_FILTER');
assert.ok(!legacyOutput || scope === 'all', 'Historical output requires the all-contract compatibility mode');
const reviewedCases = bank.cases.filter(item => acceptedIDs.has(item.id));
const scopeCases = scope === 'all' ? bank.cases : reviewedCases;
const cases = scopeCases.filter(item => group === 'all' || item.group === group);
const expectedIDs = [...new Set(cases.map(item => item.id))].sort();
const suffix = (group === 'all' ? '' : `_${group.toUpperCase()}`) + (exportsOnly ? '_EXPORTS_ONLY' : '');
assert.ok(!legacyOutput || !exportsOnly, 'Legacy evidence includes the browser print simulation');
const filename = legacyOutput ? `V1.44_ACUTE_${group.toUpperCase()}_BROWSER_RESULTS.json`
  : `${scope === 'all' ? 'ALL' : 'REVIEWED'}_ACUTE_BROWSER_2026-11-16${suffix}.json`;
const target = process.env.ACUTE_EVIDENCE_PATH || new URL(`../../clinical/qa/${filename}`, import.meta.url);
const digest = value => createHash('sha256').update(value).digest('hex');
const norm = value => String(value).replace(/\s+/g, '');
const active = (field, inputs) => !field.required_if || inputs[field.required_if.key] === field.required_if.equals;
const has = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
const record = {
  started_at: new Date().toISOString(), clinical_status: 'CLINICALLY_PENDING',
  scope: scope === 'all' ? 'Acute contracts selected from the complete manual fixture bank' : 'Owner-accepted acute contracts, including explicit additional fixture modes',
  selection_mode: scope, group, legacy_output: legacyOutput, native_print_q5: 'EXCLUDED',
  browser_print_simulation: exportsOnly ? 'EXCLUDED' : 'IN_SCOPE',
  fixture_oracle: bank.oracle, fixtures_sha256: digest(bankBytes),
  acceptance_sha256: digest(acceptanceBytes), accepted_contract_ids: [...acceptedIDs].sort(), expected_contract_ids: expectedIDs,
  execution_context: {
    ci: process.env.CI === 'true', github_sha: process.env.GITHUB_SHA || null,
    github_run_id: process.env.GITHUB_RUN_ID || null, github_run_attempt: process.env.GITHUB_RUN_ATTEMPT || null,
    configured_browser: process.env.CHROMIUM_PATH || null,
  },
  attempted_case_count: 0, cases: [], errors: [], underflow_rejections: [],
};

function fixtureInputs(row, fixture) {
  const byKey = new Map(row.fields.map(field => [field.key, field]));
  for (const key of Object.keys(fixture.inputs)) {
    // Old fixtures historically carried annotations not declared by a contract.
    // Preserve their filtering only for legacy IDs; reviewed inputs remain strict.
    if (acceptedIDs.has(fixture.id)) assert.ok(byKey.has(key), `${fixture.case_id || fixture.id}: unknown explicit fixture input ${key}`);
  }
  const raw = {...bank.common, ...fixture.inputs};
  for (const [index, field] of row.fields.entries()) {
    if (!field.required_if) continue;
    const driver = row.fields.findIndex(item => item.key === field.required_if.key);
    assert.ok(driver >= 0 && driver < index, `${row.id}: conditional driver must precede ${field.key}`);
    if (!active(field, raw) && has(fixture.inputs, field.key)) {
      assert.equal(fixture.inputs[field.key], null, `${row.id}: positive fixture contains inactive ${field.key}`);
    }
  }
  return Object.fromEntries(row.fields.filter(field => active(field, raw)).map(field => {
    assert.ok(has(raw, field.key) && raw[field.key] !== null, `${row.id}: positive fixture is missing ${field.key}`);
    return [field.key, raw[field.key]];
  }));
}

async function setControl(page, field, value) {
  const control = page.locator(`[data-field="${field.key}"]`);
  await control.waitFor({state: 'visible'});
  if (field.kind === 'number') await control.fill(value == null ? '' : String(value));
  else await control.selectOption(value == null ? '' : typeof value === 'boolean' ? value ? 'yes' : 'no' : String(value));
}

async function fillControls(page, row, inputs) {
  // Follow the contract order so choice drivers render their dependent fields first.
  for (const field of row.fields) {
    if (!active(field, inputs)) continue;
    await setControl(page, field, inputs[field.key]);
    if (field.option_labels) {
      const labels = await page.locator(`[data-field="${field.key}"] option`).evaluateAll(options =>
        Object.fromEntries(options.map(option => [option.value, option.textContent])));
      for (const [value, label] of Object.entries(field.option_labels)) {
        assert.equal(labels[value], label, `${row.id}: readable option label ${field.key}/${value}`);
      }
    }
  }
  for (const field of row.fields) {
    assert.equal(await page.locator(`[data-field="${field.key}"]`).count(), active(field, inputs) ? 1 : 0,
      `${row.id}: active/inactive control ${field.key}`);
  }
}

async function assertInvalidated(page) {
  assert.equal(await page.getByRole('region', {name: 'Resultado farmacológico'}).count(), 0);
  assert.equal(await page.locator('[data-result]').count(), 0);
  assert.equal(await page.locator('.acute-print-sheet').count(), 0);
  assert.equal(await page.getByTestId('acute-export-content').count(), 0);
  assert.equal(await page.getByRole('button', {name: 'Exportar JSON', exact: true}).count(), 0);
}

async function assertBlockedUI(page) {
  await page.getByRole('heading', {name: 'Cálculo bloqueado', exact: true}).waitFor();
  assert.equal(await page.locator('[data-result]').count(), 0);
  assert.equal(await page.locator('.acute-print-sheet').count(), 0);
  assert.equal(await page.getByRole('button', {name: 'Exportar JSON', exact: true}).count(), 0);
}

async function submit(page, regimenID, expectedInputs) {
  const pending = page.waitForResponse(response => response.url().endsWith('/api/acute-medications/calculate'));
  await page.getByRole('button', {name: 'Comprobar y calcular', exact: true}).click();
  const response = await pending;
  const value = await response.json();
  assert.equal(response.status(), 200, JSON.stringify(value));
  assert.equal(response.request().postDataJSON().regimen_id, regimenID);
  assert.deepEqual(response.request().postDataJSON().inputs, expectedInputs, `${regimenID}: only active fields submitted`);
  return value;
}

function expectedDisplay(value, nested = false) {
  if (value == null) return {kind: 'scalar', text: norm(nested ? 'No registrado' : 'No especificado en la fuente; requiere verificación profesional')};
  if (Array.isArray(value)) return {kind: 'array', items: value.map(item => expectedDisplay(item, true))};
  if (typeof value === 'object') return {kind: 'object', entries: Object.entries(value).map(([key, item]) => ({key: key.replaceAll('_', ' '), value: expectedDisplay(item, true)}))};
  const text = typeof value === 'number' ? Number.isFinite(value) ? String(value).replace('.', ',') : '—'
    : typeof value === 'boolean' ? value ? 'Sí' : 'No' : String(value);
  return {kind: 'scalar', text: norm(text)};
}

async function structuredDisplay(cell) {
  return cell.evaluate(container => {
    function read(parent) {
      const root = parent.firstElementChild;
      if (root?.tagName === 'UL') return {kind: 'array', items: [...root.children].map(read)};
      if (root?.tagName === 'DL') return {kind: 'object', entries: [...root.children].map(entry => {
        const key = entry.querySelector(':scope > dt');
        const value = entry.querySelector(':scope > dd');
        if (!key || !value) throw new Error('Incomplete structured clinical value');
        return {key: key.textContent, value: read(value)};
      })};
      return {kind: 'scalar', text: parent.textContent.replace(/\s+/g, '')};
    }
    return read(container);
  });
}

async function verifyResultUI(page, fixture, calculated) {
  const result = calculated.result;
  assert.ok(result, `${fixture.id}: no result`);
  assert.equal(result.clinical_status, 'CLINICALLY_PENDING');
  if (acceptedIDs.has(fixture.id)) {
    assert.equal(result.review_status, 'OWNER_VALIDATED_2026_11_16');
    assert.ok(has(result, 'result_kind'), `${fixture.id}: reviewed output must declare its result kind`);
  }
  for (const [key, expected] of Object.entries(fixture.expect)) {
    assert.ok(has(result, key), `${fixture.id}: expected API key missing: ${key}`);
    assert.deepEqual(result[key], expected, `${fixture.case_id || fixture.id}: manual expectation ${key}`);
  }
  await page.getByRole('region', {name: 'Resultado farmacológico'}).waitFor();
  const resultKind = result.result_kind ?? 'calculation';
  const decision = resultKind === 'decision_support';
  await page.getByRole('heading', {name: decision ? 'Orientación clínica y siguientes pasos' : 'Resultado del cálculo', exact: true}).waitFor();
  if (decision) {
    for (const key of ['dose', 'dose_unit', 'withdrawal_ml', 'administration_volume_ml', 'pump_ml_h', 'duration_min', 'amount_per_hour']) {
      assert.equal(result[key], null, `${fixture.id}: decision support must not calculate ${key}`);
      assert.equal(await page.locator(`[data-result="${key}"]`).count(), 0, `${fixture.id}: decision must not render medication arithmetic`);
    }
    assert.notEqual(result.treatment_calculated, true, `${fixture.id}: decision support must not claim treatment calculation`);
    assert.ok(result.decision_support, `${fixture.id}: decision rationale missing`);
    assert.ok(Array.isArray(result.next_actions) && result.next_actions.length, `${fixture.id}: actions missing`);
    for (const key of ['indication', 'decision_support', 'next_actions', 'limitations']) {
      assert.equal(await page.locator(`[data-result="${key}"]`).count(), 1, `${fixture.id}: visible decision field ${key}`);
    }
  } else {
    for (const key of ['dose', 'dose_unit', 'withdrawal_ml', 'administration_volume_ml', 'pump_ml_h', 'duration_min']) {
      assert.equal(await page.locator(`[data-result="${key}"]`).count(), 1, `${fixture.id}: visible calculation field ${key}`);
    }
  }
  // Internal keys (e.g. result_kind, decision_code, infusion_rate_mg_min) are
  // checked against the manual API oracle above; they need not have fake UI cells.
  const shownKeys = await page.locator('[data-result]').evaluateAll(nodes => nodes.map(node => node.dataset.result));
  for (const key of shownKeys) {
    const shown = await page.locator(`[data-result="${key}"]`).innerText();
    const expected = expectedDisplay(result[key]);
    assert.deepEqual(await structuredDisplay(page.locator(`[data-result="${key}"]`)), expected, `${fixture.id}: complete structured/localized display ${key}`);
    assert.ok(!shown.includes('[object Object]'), `${fixture.id}: unrendered structured result ${key}`);
  }
  assert.equal(norm(await page.getByTestId('acute-warnings').innerText()), norm(result.monitoring_and_warnings));
  return {result_kind: resultKind, visible_result_fields: shownKeys, api_expected_fields: Object.keys(fixture.expect)};
}

async function verifyExports(page, calculated) {
  for (const format of ['JSON', 'PDF', 'DOCX']) {
    assert.equal(await page.getByRole('button', {name: `Exportar ${format}`, exact: true}).isDisabled(), true);
  }
  if (!exportsOnly) assert.equal(await page.getByRole('button', {name: 'Imprimir resultado', exact: true}).isDisabled(), true);
  await page.getByLabel('Confirmo haber revisado').check();
  const files = {};
  for (const format of ['json', 'pdf', 'docx']) {
    const downloaded = page.waitForEvent('download').catch(error => ({error}));
    const exported = page.waitForResponse(response => response.url().endsWith('/api/acute-medications/export'));
    await page.getByRole('button', {name: `Exportar ${format.toUpperCase()}`, exact: true}).click();
    const response = await exported;
    assert.equal(response.status(), 200, JSON.stringify(await response.json()));
    const file = await downloaded;
    if (file.error) throw file.error;
    files[format] = readFileSync(await file.path());
  }
  assert.deepEqual(JSON.parse(files.json), calculated.report);
  const documents = ['pdf', 'docx'];
  if (!exportsOnly) {
    await page.evaluate(() => {globalThis.__reviewedAcutePrinted = false; globalThis.print = () => {globalThis.__reviewedAcutePrinted = true;};});
    await page.getByRole('button', {name: 'Imprimir resultado', exact: true}).click();
    assert.equal(await page.evaluate(() => globalThis.__reviewedAcutePrinted), true);
    assert.equal(await page.locator('.acute-print-sheet').count(), 1);
    files.print = await page.pdf({format: 'A4', printBackground: true});
    documents.push('print');
  }
  const check = spawnSync(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-c', `
import io,json,base64,zipfile,sys
from pypdf import PdfReader
from xml.etree import ElementTree
data=json.load(sys.stdin); norm=lambda s:''.join(s.split()); pages={}
for fmt,b64 in data['files'].items():
 raw=base64.b64decode(b64)
 if fmt in ('pdf','print'):
  pdf=PdfReader(io.BytesIO(raw)); pages[fmt]=len(pdf.pages)
  text='\\n'.join(page.extract_text() or '' for page in pdf.pages)
 else:
  with zipfile.ZipFile(io.BytesIO(raw)) as document:
   xml=ElementTree.fromstring(document.read('word/document.xml'))
  text='\\n'.join(node.text or '' for node in xml.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
 for heading,paragraphs in data['sections']:
  for expected in [heading]+paragraphs:
   assert norm(expected) in norm(text),(fmt,expected)
print(json.dumps(pages))
`], {input: JSON.stringify({sections: calculated.report.sections, files: Object.fromEntries(documents.map(key => [key, files[key].toString('base64')]))}), encoding: 'utf8', windowsHide: true, maxBuffer: 4 * 1024 * 1024});
  assert.equal(check.status, 0, check.stderr || check.error?.message);
  return {formats: Object.keys(files), pages: JSON.parse(check.stdout), sha256: Object.fromEntries(Object.entries(files).map(([key, value]) => [key, digest(value)])), all_report_sections_preserved: true};
}

const underflowInputs = new Map([
  ['anaphylaxis-refractory-reviewed-3', 'weight_kg'],
  ['reversal-other-lmwh', 'dalteparin_dose_to_neutralize_anti_xa_iu'],
  ['status-phenytoin-dose-only', 'weight_kg'],
]);

async function verifyUnderflow(page, fixture, row, inputs) {
  const id = fixture.case_id || fixture.id;
  const fieldKey = underflowInputs.get(id);
  if (!fieldKey) return;
  const field = row.fields.find(item => item.key === fieldKey);
  await setControl(page, field, Number.MIN_VALUE);
  await assertInvalidated(page);
  const pending = page.waitForResponse(response => response.url().endsWith('/api/acute-medications/calculate'));
  await page.getByRole('button', {name: 'Comprobar y calcular', exact: true}).click();
  const response = await pending;
  const value = await response.json();
  assert.equal(response.request().postDataJSON().inputs[fieldKey], Number.MIN_VALUE);
  assert.equal(response.status() === 422 || (response.status() === 200 && value.blocked === true), true, id);
  assert.equal(value.result, undefined);
  await page.getByRole('alert').first().waitFor();
  assert.equal(await page.locator('[data-result]').count(), 0);
  assert.equal(await page.getByRole('button', {name: /^Exportar /}).count(), 0);
  record.underflow_rejections.push({id, field: fieldKey, http_status: response.status()});
  await setControl(page, field, inputs[fieldKey]);
  const restored = await submit(page, row.id, inputs);
  await verifyResultUI(page, fixture, restored);
}

async function apiReject(context, base, revision, row, inputs, updates, omitted) {
  const changed = {...inputs, ...updates};
  if (omitted) delete changed[omitted];
  const response = await context.request.post(`${base}/api/acute-medications/calculate`, {data: {regimen_id: row.id, source_revision: revision, inputs: changed}});
  const value = await response.json();
  assert.equal(response.status(), 200, JSON.stringify(value));
  assert.equal(value.blocked, true, `${row.id}: invalid inputs accepted ${JSON.stringify(updates || {omitted})}`);
  assert.equal(value.result, undefined, `${row.id}: blocked case leaked a result`);
  if (omitted) assert.ok(value.alerts.some(alert => alert.code === omitted), `${row.id}: missing-field gate ${omitted}`);
  return value.alerts;
}

try {
  assert.equal(acceptedIDs.size, 19, 'This release checkpoint must cover the 19 accepted contract IDs');
  // These release-wide checks remain mandatory even when a caller filters cases.
  assert.deepEqual([...new Set(reviewedCases.map(item => item.id))].sort(), [...acceptedIDs].sort());
  for (const item of reviewedCases) {
    assert.ok(!item.blocked && item.expect && Object.keys(item.expect).length, `${item.id}: reviewed positive fixture required`);
    assert.ok(item.manual_reason, `${item.id}: independent reviewed fixture rationale is required`);
  }
  assert.ok(cases.length, 'Empty flow filter for the selected ACUTE_SCOPE');
  assert.equal(new Set(cases.map(item => item.case_id || item.id)).size, cases.length, 'Case IDs must be unique across mode/boundary fixtures');
  for (const item of cases) {
    assert.ok(!item.blocked && item.expect && Object.keys(item.expect).length, `${item.id}: positive fixture required; use reject for negative checks`);
  }
  record.expected_case_count = cases.length;
  await withClinicalApp(async ({page, context, base, browser}) => {
    record.browser = browser.version();
    record.built_index_sha256 = digest(readFileSync(new URL('../dist/index.html', import.meta.url)));
    page.on('pageerror', error => record.errors.push(error.message));
    let browserCalculations = 0;
    page.on('request', request => {if (request.url().endsWith('/api/acute-medications/calculate')) browserCalculations++;});
    const response = await context.request.post(`${base}/api/acute-medications/catalog`, {data: {}});
    const catalog = await response.json();
    assert.equal(response.status(), 200, JSON.stringify(catalog));
    record.source_revision = catalog.source_revision;
    const reviewedRows = catalog.regimens.filter(row => row.reviewed_workflow);
    assert.deepEqual(reviewedRows.map(row => row.id).sort(), [...acceptedIDs].sort());
    assert.ok(reviewedRows.every(row => !row.block_reason), 'Reviewed contracts must not retain their historical universal blocker');
    const selectedRows = catalog.regimens.filter(row => (scope === 'all' || acceptedIDs.has(row.id))
      && (group === 'all' || row.group === group));
    assert.deepEqual(selectedRows.map(row => row.id).sort(), expectedIDs, 'Fixtures must cover every catalog contract in the requested scope/group');

    for (const fixture of cases) {
      record.attempted_case_count++;
      const row = catalog.regimens.find(item => item.id === fixture.id);
      assert.ok(row, `${fixture.id}: catalog row missing`);
      assert.equal(row.group, fixture.group, `${fixture.id}: fixture group must match the catalog`);
      const inputs = fixtureInputs(row, fixture);
      await page.goto(`${base}/drugs`);
      await page.getByRole('link', {name: 'Farmacología aguda por indicación'}).click();
      await page.getByRole('heading', {name: 'Farmacología aguda', exact: true}).waitFor();
      await page.getByLabel('Grupo farmacológico', {exact: true}).selectOption(fixture.group);
      await page.getByLabel('Indicación y opción', {exact: true}).selectOption(fixture.id);
      await fillControls(page, row, inputs);
      const calculated = await submit(page, fixture.id, inputs);
      assert.equal(calculated.blocked, false, JSON.stringify(calculated));
      const presentation = await verifyResultUI(page, fixture, calculated);
      const exports = await verifyExports(page, calculated);
      await verifyUnderflow(page, fixture, row, inputs);

      // When the bank supplies another independently specified mode of this ID,
      // switch in the same live form. Hidden state must not reach the API/export.
      const drivers = [...new Set(row.fields.filter(field => field.required_if).map(field => field.required_if.key))];
      const companion = cases.slice(0, cases.indexOf(fixture)).find(item => item.id === fixture.id
        && drivers.some(key => ({...bank.common, ...item.inputs})[key] !== inputs[key]));
      const modeSwitches = [];
      if (companion) {
        const alternate = fixtureInputs(row, companion);
        const driver = row.fields.find(field => drivers.includes(field.key) && alternate[field.key] !== inputs[field.key]);
        await setControl(page, driver, alternate[driver.key]);
        await assertInvalidated(page);
        await fillControls(page, row, alternate);
        const switched = await submit(page, companion.id, alternate);
        assert.equal(switched.blocked, false, JSON.stringify(switched));
        await verifyResultUI(page, companion, switched);
        modeSwitches.push({driver: driver.key, from: inputs[driver.key], to: alternate[driver.key],
          manual_case: companion.case_id || companion.id, submitted_keys: Object.keys(alternate),
          manual_expected: companion.expect, stale_result_invalidated: true, inactive_fields_omitted: true});
        await fillControls(page, row, inputs);
        const restored = await submit(page, fixture.id, inputs);
        assert.equal(restored.blocked, false, JSON.stringify(restored));
        await verifyResultUI(page, fixture, restored);
      }

      // Editing an applicable required field must remove the previous result,
      // confirmation and printable report even in decision-only workflows.
      const required = row.fields.find(field => active(field, inputs) && field.kind === 'boolean' && typeof field.expected === 'boolean')
        || row.fields.find(field => active(field, inputs));
      await setControl(page, required, null);
      await assertInvalidated(page);
      const beforeMissing = browserCalculations;
      await page.getByRole('button', {name: 'Comprobar y calcular', exact: true}).click();
      await page.getByRole('alert').waitFor();
      assert.equal(browserCalculations, beforeMissing, `${fixture.id}: missing UI input must not produce a request`);
      await assertInvalidated(page);
      const gates = [{field: required.key, omitted: true, layer: 'UI required input and API gate', alerts: await apiReject(context, base, catalog.source_revision, row, inputs, {}, required.key)}];
      await setControl(page, required, inputs[required.key]);

      const guarded = row.fields.find(field => active(field, inputs) && field.kind === 'boolean' && typeof field.expected === 'boolean');
      if (guarded) {
        const updates = {[guarded.key]: !guarded.expected};
        gates.push({field: guarded.key, updates, layer: 'Applicable explicit expected-value API gate', alerts: await apiReject(context, base, catalog.source_revision, row, inputs, updates)});
      }
      const rejectedInputs = [];
      for (const updates of fixture.reject || []) {
        for (const key of Object.keys(updates)) assert.ok(row.fields.some(field => field.key === key), `${fixture.id}: unknown negative fixture field ${key}`);
        const candidate = {...inputs, ...updates};
        const alerts = await apiReject(context, base, catalog.source_revision, row, inputs, updates);
        const unavailable = row.fields.filter(field => has(updates, field.key) && field.kind === 'choice' && !field.options.includes(updates[field.key]));
        if (unavailable.length) {
          for (const field of unavailable) {
            if (!active(field, inputs)) continue;
            const options = await page.locator(`[data-field="${field.key}"] option`).evaluateAll(items => items.map(item => item.value));
            assert.ok(!options.includes(updates[field.key]), `${fixture.id}: unsupported option exposed by UI`);
          }
          rejectedInputs.push({updates, layer: 'Unavailable UI choice and API gate', alerts});
          continue;
        }
        const typed = row.fields.filter(field => has(updates, field.key)).every(field =>
          field.kind === 'number' ? typeof updates[field.key] === 'number' && Number.isFinite(updates[field.key]) :
          field.kind === 'boolean' ? typeof updates[field.key] === 'boolean' : typeof updates[field.key] === 'string');
        if (!typed) {
          rejectedInputs.push({updates, layer: 'API type/missing-value gate', alerts});
          continue;
        }
        for (const field of row.fields) {
          if (has(updates, field.key) && active(field, candidate)) await setControl(page, field, updates[field.key]);
        }
        await assertInvalidated(page);
        const activeCandidate = Object.fromEntries(Object.entries(candidate).filter(([key]) => active(row.fields.find(field => field.key === key), candidate)));
        const blocked = await submit(page, fixture.id, activeCandidate);
        assert.equal(blocked.blocked, true, `${fixture.id}: negative UI fixture accepted ${JSON.stringify(updates)}`);
        assert.equal(blocked.result, undefined);
        await assertBlockedUI(page);
        rejectedInputs.push({updates, layer: 'UI and API gates', alerts: blocked.alerts});
        for (const field of row.fields) {
          if (has(updates, field.key) && active(field, inputs)) await setControl(page, field, inputs[field.key]);
        }
      }

      record.cases.push({
        id: fixture.case_id || fixture.id, regimen: fixture.id, status: 'PASS',
        manual_reason: fixture.manual_reason, inputs, expected: fixture.expect,
        ignored_legacy_fixture_keys: acceptedIDs.has(fixture.id) ? [] : Object.keys(fixture.inputs).filter(key => !row.fields.some(field => field.key === key)),
        actual: calculated.result, report: calculated.report, presentation,
        exports: exports.formats, pages: exports.pages, export_verification: exports, modeSwitches,
        gates, rejectedInputs, invalidation: 'PASS',
      });
      console.log(legacyOutput ? `PASS acute flow: ${fixture.id}` : `PASS ${scope} acute: ${fixture.case_id || fixture.id} (${presentation.result_kind})`);
    }
    assert.deepEqual(record.errors, []);
    assert.equal(record.cases.length, cases.length);
    record.covered_contract_ids = [...new Set(record.cases.map(item => item.regimen))].sort();
    assert.deepEqual(record.covered_contract_ids, expectedIDs);
    record.all_accepted_contracts_executed = [...acceptedIDs].every(id => record.covered_contract_ids.includes(id));
  });
  record.status = 'PASS';
  record.functional_result = 'PASS';
} catch (error) {
  record.failure = error.stack;
  const blockedLaunch = !record.browser && record.attempted_case_count === 0
    && /browserType\.launch/.test(error.stack || '')
    && /socket\(\) failed: Operation not permitted/.test(error.stack || '');
  record.status = blockedLaunch ? 'BLOCKED_ENVIRONMENT' : 'FAIL';
  record.functional_result = blockedLaunch ? 'NOT_EXECUTED' : 'FAIL';
  if (blockedLaunch) record.environment_blocker = {
    stage: 'browser_launch', code: 'SOCKET_EPERM',
    detail: 'The operating environment denied a socket required by Chromium before any browser case ran.',
  };
  process.exitCode = 1; console.error(error);
}
record.completed_case_count = record.cases.length;
record.finished_at = new Date().toISOString();
await writeEvidence(target, record);
