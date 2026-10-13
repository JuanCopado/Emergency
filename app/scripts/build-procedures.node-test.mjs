import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile, mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildProcedureCatalog, buildProcedureSheets, serializeCatalog } from './build-procedures.mjs';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const aliases = { 'PROC-ENT-011': 'PROC-ORTHO-022', 'PROC-PED-008': 'PROC-ORTHO-004',
  'PROC-SP-006': 'PROC-EYE-001', 'PROC-US-007': 'PROC-CV-006' };

test('all 196 complete sheets preserve every canonical section and explicit extraction', async () => {
  const sheets = await buildProcedureSheets();
  assert.equal(sheets.length,196);
  assert.equal(new Set(sheets.map(s=>s.procedure_id)).size,196);
  for (const sheet of sheets) {
    const canonical=JSON.parse(await readFile(resolve(repo,`clinical/data/procedures/${sheet.procedure_id}.json`),'utf8'));
    for(const [key,value] of Object.entries(sheet)) assert.deepEqual(value,canonical[key],`${sheet.procedure_id}: ${key}`);
    assert.equal(sheet.status,'YELLOW');
  }
  const generated=await readFile(resolve(repo,'app/src/data/generatedProcedureSheets.json'),'utf8');
  assert.equal(generated.replace(/\r\n/g,'\n'),serializeCatalog(sheets));
});

test('196 canonical IDs + 4 aliases = 200 textual IDs across 16 families', async () => {
  const catalog = await buildProcedureCatalog();
  const ids = catalog.map((p) => p.id);
  const references = catalog.flatMap((p) => p.aliases);
  assert.equal(ids.length, 196);
  assert.equal(new Set(ids).size, 196);
  assert.equal(references.length, 4);
  assert.equal(new Set([...ids, ...references]).size, 200);
  assert.equal(new Set(catalog.map((p) => p.family)).size, 16);
  assert.ok(ids.includes('PROC-VASC-001'));
  assert.ok(ids.includes('PROC-VASC-007'));
});

test('all four aliases resolve directly to existing canonical IDs', async () => {
  const catalog = await buildProcedureCatalog();
  const actual = Object.fromEntries(catalog.flatMap((p) => p.aliases.map((id) => [id, p.id])));
  assert.deepEqual(actual, aliases);
  assert.ok(catalog.every((p) => !(p.id in aliases)));
});

test('all metadata and source headings derive from canonical text', async () => {
  const catalog = await buildProcedureCatalog();
  const index = await readFile(resolve(repo, 'clinical/modules/emergency-procedures-index.md'), 'utf8');
  for (const p of catalog) {
    assert.ok(index.includes(`**${p.id} — ${p.name}** — ${p.level}`), p.id);
    assert.ok(index.includes(p.family), p.id);
    assert.ok(p.sourcePath.startsWith('clinical/modules/procedures/'), p.id);
    const source = await readFile(resolve(repo, p.sourcePath), 'utf8');
    assert.ok(source.includes(`## ${p.sourceHeading}`), p.id);
    assert.ok(p.sourceHeading.startsWith(p.id + ' — '), p.id);
  }
});

test('regeneration is deterministic and committed artifact is current', async () => {
  const first = serializeCatalog(await buildProcedureCatalog());
  const second = serializeCatalog(await buildProcedureCatalog());
  assert.equal(first, second);
  const committed = (await readFile(resolve(repo, 'app/src/data/generatedProcedures.json'), 'utf8')).replace(/\r\n/g, '\n');
  assert.equal(first, committed, 'Run npm run procedures:build');
});

for (const [name, index, cards, error] of [
  ['duplicate index', '1. **PROC-T-001 — One** — CORE\n2. **PROC-T-001 — One** — CORE', '## PROC-T-001 — One — CORE\nBody.', /duplicate index/],
  ['dangling alias', '1. **PROC-T-001 — One** — referencia cruzada a T-002', '## PROC-T-001 — One — REFERENCIA\nVer **PROC-T-002**.', /must target a canonical/],
  ['alias chain', '1. **PROC-T-001 — One** — referencia cruzada a T-002\n2. **PROC-T-002 — Two** — referencia cruzada a T-001', '## PROC-T-001 — One — REFERENCIA\nVer **PROC-T-002**.\n## PROC-T-002 — Two — REFERENCIA\nVer **PROC-T-001**.', /must target a canonical/],
  ['inconsistent sources', '1. **PROC-T-001 — One** — CORE', '## PROC-T-002 — Two — CORE\nBody.', /disagree/],
]) {
  test(`generation rejects ${name}`, async (t) => {
    const root = await mkdtemp(resolve(tmpdir(), 'emergency-catalog-'));
    assert.equal(dirname(root), resolve(tmpdir()));
    t.after(() => rm(root, { recursive: true, force: true }));
    await mkdir(resolve(root, 'modules/procedures'), { recursive: true });
    await writeFile(resolve(root, 'modules/emergency-procedures-index.md'), '# 1. Test family\n' + index);
    await writeFile(resolve(root, 'modules/procedures/01-test.md'), cards);
    await assert.rejects(() => buildProcedureCatalog(root), error);
  });
}
