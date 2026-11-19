import { afterEach, describe, expect, it } from 'vitest';
import { readFile, mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { dirname, basename, resolve } from 'node:path';
import { tmpdir } from 'node:os';
import { buildProcedureCatalog, buildProcedureSheets, serializeCatalog } from '../../scripts/build-procedures.mjs';

const repo = resolve(process.cwd(), '..');
const fixtures = [];
afterEach(async () => {
  for (const directory of fixtures.splice(0)) {
    if (dirname(directory) !== resolve(tmpdir()) || !basename(directory).startsWith('emergency-sec-catalog-')) {
      throw new Error('Refusing unexpected fixture cleanup path');
    }
    await rm(directory, { recursive: true });
  }
});

describe('Canonical build adapters under measured coverage', () => {
  it('preserves all canonical metadata, aliases and every structured sheet field', async () => {
    const catalog = await buildProcedureCatalog();
    const sheets = await buildProcedureSheets();
    expect(catalog).toHaveLength(196);
    expect(sheets).toHaveLength(196);
    expect(new Set(catalog.map(p => p.id)).size).toBe(196);
    expect(catalog.flatMap(p => p.aliases)).toHaveLength(4);
    expect(new Set(catalog.map(p => p.family)).size).toBe(16);
    const committedCatalog = (await readFile(resolve(repo, 'app/src/data/generatedProcedures.json'), 'utf8')).replace(/\r\n/g, '\n');
    const committedSheets = (await readFile(resolve(repo, 'app/src/data/generatedProcedureSheets.json'), 'utf8')).replace(/\r\n/g, '\n');
    expect(serializeCatalog(catalog)).toBe(committedCatalog);
    expect(serializeCatalog(sheets)).toBe(committedSheets);
    for (const sheet of sheets) {
      const canonical = JSON.parse(await readFile(resolve(repo, `clinical/data/procedures/${sheet.procedure_id}.json`), 'utf8'));
      for (const [field, value] of Object.entries(sheet)) expect(value).toEqual(canonical[field]);
      expect(sheet.status).toBe('YELLOW');
    }
  });

  it.each([
    ['duplicate ID', '1. **PROC-T-001 — One** — CORE\n2. **PROC-T-001 — One** — CORE', '## PROC-T-001 — One — CORE\nBody.', /duplicate index/],
    ['unresolved alias', '1. **PROC-T-001 — One** — referencia cruzada a T-002', '## PROC-T-001 — One — REFERENCIA\nBody.', /Unresolved alias/],
    ['dangling alias', '1. **PROC-T-001 — One** — referencia cruzada a T-002', '## PROC-T-001 — One — REFERENCIA\nVer **PROC-T-002**.', /must target a canonical/],
    ['invalid level', '1. **PROC-T-001 — One** — INVALID', '## PROC-T-001 — One — CORE\nBody.', /Unknown level/],
    ['duplicate card', '1. **PROC-T-001 — One** — CORE', '## PROC-T-001 — One — CORE\nBody.\n## PROC-T-001 — Again — CORE\nBody.', /Duplicate canonical/],
    ['different IDs', '1. **PROC-T-001 — One** — CORE', '## PROC-T-002 — Two — CORE\nBody.', /disagree/],
  ])('rejects %s before publishing a catalog', async (_name, index, cards, error) => {
    const directory = await mkdtemp(resolve(tmpdir(), 'emergency-sec-catalog-'));
    fixtures.push(directory);
    await mkdir(resolve(directory, 'modules/procedures'), { recursive: true });
    await writeFile(resolve(directory, 'modules/emergency-procedures-index.md'), '# 1. Synthetic family\n' + index);
    await writeFile(resolve(directory, 'modules/procedures/01-synthetic.md'), cards);
    await expect(buildProcedureCatalog(directory)).rejects.toThrow(error);
  });

  it('checks guide regeneration without writing the committed clinical projection', async () => {
    const file = resolve(repo, 'app/src/data/generatedClinicalGuides.json');
    const before = await readFile(file);
    const originalArgs = process.argv;
    try {
      process.argv = [...originalArgs, '--check'];
      await import('../../scripts/build-clinical-guides.mjs');
    } finally {
      process.argv = originalArgs;
    }
    expect((await readFile(file)).equals(before)).toBe(true);
  });
});
