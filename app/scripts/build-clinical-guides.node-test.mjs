import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, writeFile, copyFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..');

test('module table and every frontend status match authoritative evidence', async () => {
  const evidence = JSON.parse(await readFile(resolve(repo, 'clinical/references/evidence-registry.json'), 'utf8')).modules;
  const table = await readFile(resolve(repo, 'clinical/MODULES.md'), 'utf8');
  const statuses = new Map([...table.matchAll(/^\| `([^`]+)` \|[^|]+\| (green|yellow|red) \|/gm)].map((m) => [m[1], m[2]]));
  const guides = JSON.parse(await readFile(resolve(repo, 'app/src/data/generatedClinicalGuides.json'), 'utf8'));
  assert.equal(statuses.size, Object.keys(evidence).length);
  assert.equal(guides.length, Object.keys(evidence).length);
  for (const guide of guides) {
    assert.equal(statuses.get(guide.id), evidence[guide.id].status, `MODULES: ${guide.id}`);
    assert.equal(guide.status, evidence[guide.id].status, `frontend: ${guide.id}`);
  }
});

async function buildFixture(t, index, bundles) {
  const root = await mkdtemp(resolve(tmpdir(), 'emergency-guides-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  for (const dir of ['app/scripts', 'app/src/data', 'clinical/references', 'clinical/modules']) {
    await mkdir(resolve(root, dir), { recursive: true });
  }
  await copyFile(resolve(repo, 'app/scripts/build-clinical-guides.mjs'), resolve(root, 'app/scripts/build-clinical-guides.mjs'));
  await writeFile(resolve(root, 'clinical/references/module-index.md'), index);
  await writeFile(resolve(root, 'clinical/MODULES.md'), await readFile(resolve(repo, 'clinical/MODULES.md')));
  for (const [path, text] of Object.entries(bundles)) await writeFile(resolve(root, 'clinical', path), text);
  const result = spawnSync(process.execPath, [resolve(root, 'app/scripts/build-clinical-guides.mjs')], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(await readFile(resolve(root, 'app/src/data/generatedClinicalGuides.json'), 'utf8'));
}

test('shared safety preamble and exact section body survive once, including CRLF', async (t) => {
  const preamble = '# Shared bundle\n\nSafety: verify allergies; SpO₂ ≤ 92% → reassess.';
  const section = '### Scope\n\nSpecific body ≥ threshold.';
  const guides = await buildFixture(t, '| example | `modules/example.md` |\n', {
    'modules/example.md': `${preamble}\n\n## example-long\nWrong section.\n\n## example\n\n${section}\n\n## next\nOther.`.replaceAll('\n', '\r\n'),
  });
  assert.equal(guides[0].sharedPreamble, preamble);
  assert.equal(guides[0].sectionBody, section);
  const text = [guides[0].sharedPreamble, guides[0].sectionBody].filter(Boolean).join('\n\n');
  assert.equal(text, `${preamble}\n\n${section}`);
  assert.equal(text.split('Safety:').length - 1, 1);
  assert.ok(!text.includes('Wrong section'));
});

test('a section without shared preamble still retains its full body', async (t) => {
  const guides = await buildFixture(t, '| alone | `modules/alone.md` |\n', {
    'modules/alone.md': '## alone\n\nBody without preamble.\n',
  });
  assert.equal(guides[0].sharedPreamble, '');
  assert.equal(guides[0].sectionBody, 'Body without preamble.');
});

test('all committed guides match canonical preamble and section, without stale artifacts', async (t) => {
  const index = await readFile(resolve(repo, 'clinical/references/module-index.md'), 'utf8');
  const rows = [...index.matchAll(/^\| ([a-z0-9-]+) \| `([^`]+)` \|$/gm)];
  const bundles = {};
  for (const [, , path] of rows) bundles[path] = (await readFile(resolve(repo, 'clinical', path), 'utf8')).replaceAll('\r\n', '\n');
  const generated = await buildFixture(t, index, bundles);
  assert.equal(generated.length, rows.length);
  for (const guide of generated) {
    const source = bundles[guide.bundle];
    const preamble = source.split(/^## /m)[0].trim();
    const section = source.split(`\n## ${guide.id}\n`)[1]?.split(/\n## /)[0].trim();
    assert.ok(section, guide.id);
    assert.equal(guide.sharedPreamble, preamble, guide.id);
    assert.equal(guide.sectionBody, section, guide.id);
  }
  const committed = JSON.parse(await readFile(resolve(repo, 'app/src/data/generatedClinicalGuides.json'), 'utf8'));
  assert.deepEqual(committed, generated, 'Run guides:build after any canonical source change');
});
