import { readFile, readdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const defaultRoot = resolve(appRoot, '../clinical');
const read = async (path) => (await readFile(path, 'utf8')).replace(/\r\n?/g, '\n');

export async function buildProcedureCatalog(root = defaultRoot) {
  const index = await read(resolve(root, 'modules/emergency-procedures-index.md'));
  const entries = new Map();
  let family;
  for (const line of index.split('\n')) {
    const group = line.match(/^# \d+\. (.+)$/);
    if (group) family = group[1].trim();
    const row = line.match(/^\d+\. \*\*(PROC-[A-Z]+-\d{3}) — (.+?)\*\* — (.+?)\s*$/);
    if (!row) continue;
    const [, id, name, descriptor] = row;
    if (!family || entries.has(id)) throw new Error(`Missing family or duplicate index ID: ${id}`);
    const alias = descriptor.match(/^referencia cruzada a (?:PROC-)?([A-Z]+-\d{3})$/);
    if (!alias && !/^(?:CORE|ADVANCED|SPECIALIST|POCUS|PED)(?:\/(?:CORE|ADVANCED|SPECIALIST|POCUS|PED))*$/.test(descriptor)) {
      throw new Error(`Unknown level/reference: ${id}`);
    }
    entries.set(id, { id, name, family, level: alias ? null : descriptor, target: alias ? `PROC-${alias[1]}` : null });
  }
  const cards = new Map();
  const directory = resolve(root, 'modules/procedures');
  for (const file of (await readdir(directory)).filter((name) => name.endsWith('.md')).sort()) {
    const content = await read(resolve(directory, file));
    const headings = [...content.matchAll(/^## (PROC-[A-Z]+-\d{3}) — (.+?) — ([A-Z/]+)\s*$/gm)];
    for (const [i, heading] of headings.entries()) {
      const id = heading[1];
      if (cards.has(id)) throw new Error(`Duplicate canonical card: ${id}`);
      const body = content.slice(heading.index + heading[0].length, headings[i + 1]?.index ?? content.length);
      const target = heading[3] === 'REFERENCIA' ? body.match(/^\s*Ver \*\*(PROC-[A-Z]+-\d{3})\*\*/)?.[1] : null;
      if (heading[3] === 'REFERENCIA' && !target) throw new Error(`Unresolved alias card: ${id}`);
      cards.set(id, { sourcePath: `clinical/modules/procedures/${file}`, sourceHeading: heading[0].trim().slice(3), target });
    }
  }
  if (entries.size !== cards.size || [...cards.keys()].some((id) => !entries.has(id))) {
    throw new Error('Index and family cards disagree on textual IDs');
  }
  const catalog = [];
  for (const entry of entries.values()) {
    const card = cards.get(entry.id);
    if (!card || entry.target !== card.target) throw new Error(`Index/card alias mismatch: ${entry.id}`);
    if (entry.target) {
      if (!entries.has(entry.target) || entries.get(entry.target).target) throw new Error(`Alias must target a canonical procedure: ${entry.id}`);
      continue;
    }
    catalog.push({ id: entry.id, name: entry.name, level: entry.level, family: entry.family,
      sourcePath: card.sourcePath, sourceHeading: card.sourceHeading,
      aliases: [...entries.values()].filter((other) => other.target === entry.id).map((other) => other.id).sort(),
    });
  }
  return catalog.sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
}

export const serializeCatalog = (catalog) => JSON.stringify(catalog, null, 2) + '\n';

export async function buildProcedureSheets(root = defaultRoot) {
  const catalog = await buildProcedureCatalog(root);
  const directory = resolve(root, 'data/procedures');
  const files = (await readdir(directory)).filter(f => /^PROC-.*\.json$/.test(f));
  if (files.length !== catalog.length) throw new Error('Structured procedure inventory mismatch');
  return Promise.all(catalog.map(async p => {
    const sheet = JSON.parse(await read(resolve(directory, `${p.id}.json`)));
    if (sheet.procedure_id !== p.id || !sheet.provenance?.family_preamble ||
        !sheet.provenance.sections.STOP || !sheet.provenance.sections['Confirmación'] || !sheet.provenance.sections.Fuentes) {
      throw new Error(`Incomplete canonical sheet: ${p.id}`);
    }
    // Preserve every literal section, plus explicitly extracted rescue/escalation.
    const {procedure_id, name, family, level, status, rescue, escalation, provenance} = sheet;
    return {procedure_id, name, family, level, status, rescue, escalation, provenance};
  }));
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const catalog = await buildProcedureCatalog();
  const output = resolve(appRoot, 'src/data/generatedProcedures.json');
  const text = serializeCatalog(catalog);
  if (process.argv.includes('--check')) {
    if (await read(output) !== text) throw new Error('Procedure catalog is stale; run npm run procedures:build');
  } else {
    await writeFile(output, text, 'utf8');
  }
  const sheetsOutput = resolve(appRoot, 'src/data/generatedProcedureSheets.json');
  const sheetsText = serializeCatalog(await buildProcedureSheets());
  if (process.argv.includes('--check')) {
    if (await read(sheetsOutput) !== sheetsText) throw new Error('Procedure sheets are stale');
  } else {
    await writeFile(sheetsOutput, sheetsText, 'utf8');
  }
  console.log(`${catalog.length} canonical procedures + ${catalog.flatMap((p) => p.aliases).length} aliases; ${new Set(catalog.map((p) => p.family)).size} families`);
}
