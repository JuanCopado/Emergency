import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(here, '..');
const repoRoot = resolve(appRoot, '..');
const clinicalRoot = resolve(repoRoot, 'clinical');

const readCanonical = async (path) => (await readFile(path, 'utf8')).replace(/\r\n?/g, '\n');
const indexText = await readCanonical(resolve(clinicalRoot, 'references/module-index.md'));
const modulesText = await readCanonical(resolve(clinicalRoot, 'MODULES.md'));
const evidence = JSON.parse(await readCanonical(resolve(clinicalRoot, 'references/evidence-registry.json'))).modules;

const entries = indexText
  .split('\n')
  .map((line) => {
    const cells = line.split('|');
    if (cells.length !== 4 || cells[0] !== '' || cells[3] !== '') return null;
    const id = cells[1].trim();
    const bundle = cells[2].trim();
    if (!id || !/^`[^`]+`$/.test(bundle)) return null;
    const unquotedId = id.replace(/^`/, '').replace(/`$/, '');
    if (!unquotedId || unquotedId.includes('`')) return null;
    return [line, unquotedId, bundle.slice(1, -1)];
  })
  .filter(Boolean)
  .map((match) => ({ id: match[1].trim(), bundle: match[2].trim() }))
  .filter((entry) => entry.id !== 'Module ID');

const statusMap = new Map();
for (const line of modulesText.split('\n')) {
  const parts = line.split('|').map((part) => part.trim());
  if (parts.length < 5) continue;
  const idMatch = parts[1]?.match(/^`([^`]+)`$/);
  const status = parts[3]?.toLowerCase();
  if (idMatch) {
    if (statusMap.has(idMatch[1])) throw new Error('Duplicate module status: ' + idMatch[1]);
    if (!['green', 'yellow', 'red'].includes(status)) throw new Error('Invalid module status: ' + idMatch[1]);
    statusMap.set(idMatch[1], status);
  }
}

// The index is a complete projection, not a selectable subset of the registry.
// Validate all three inventories before reading bundles or writing any output.
const indexIds = new Set();
for (const { id } of entries) {
  if (indexIds.has(id)) throw new Error('Duplicate module index ID: ' + id);
  indexIds.add(id);
}
for (const id of Object.keys(evidence ?? {})) {
  if (!indexIds.has(id)) throw new Error('Evidence module absent from index: ' + id);
}
for (const id of statusMap.keys()) {
  if (!indexIds.has(id)) throw new Error('Module table entry absent from index: ' + id);
}

const cache = new Map();
async function getBundle(bundle) {
  if (!cache.has(bundle)) cache.set(bundle, await readCanonical(resolve(clinicalRoot, bundle)));
  return cache.get(bundle);
}

const titleize = (id) => id.split('-').map((w) => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ');

const PROCEDURE_MODULES = new Set([
  'airway-rsi',
  'pediatric-airway-rsi',
  'sedoanalgesia',
  'pediatric-procedural-sedation',
  'emergency-procedures',
]);

const ALGORITHM_PATTERN = /(arrest|arrhythm|shock|anaphylaxis|stroke|status-epilepticus|dka|electrolyte|hypertensive-emergency|tension-pneumothorax|sepsis|acute-severe-asthma|croup|bronchiolitis|dehydration|hemorrhage|bleeding|tamponade|aortic-syndrome|pulmonary-embolism)/;

function classifyFormat(id) {
  if (PROCEDURE_MODULES.has(id)) return 'procedure';
  if (ALGORITHM_PATTERN.test(id)) return 'algorithm';
  return 'guide';
}

const guides = [];

for (const entry of entries) {
  // Project the authoritative status; absent or conflicting metadata must not
  // silently become a new clinical state in a generated catalog.
  const status = evidence?.[entry.id]?.status;
  if (!['green', 'yellow', 'red'].includes(status)) throw new Error('Missing or invalid evidence status: ' + entry.id);
  if (statusMap.get(entry.id) !== status) throw new Error('Module/evidence status mismatch: ' + entry.id);
  const content = await getBundle(entry.bundle);
  const headings = [...content.matchAll(/^## (.+)$/gm)];
  const matches = headings.filter((heading) => heading[1].trim() === entry.id);
  if (matches.length !== 1) throw new Error('Expected one canonical heading: ' + entry.id);
  const heading = matches[0];
  const position = headings.indexOf(heading);
  // Same canonical boundary as clinical/scripts/load_module.py: everything
  // before the first level-two heading applies to every module in the bundle.
  const sharedPreamble = content.slice(0, headings[0].index).trim();
  const sectionBody = content.slice(heading.index + heading[0].length,
    headings[position + 1]?.index ?? content.length).trim();
  guides.push({
    id: entry.id,
    title: titleize(entry.id),
    bundle: entry.bundle,
    sourcePath: 'clinical/' + entry.bundle,
    status,
    format: classifyFormat(entry.id),
    sharedPreamble,
    sectionBody,
  });
}

// A small navigation projection avoids loading full clinical prose on Home.
const grouped = new Map();
for (const guide of guides) {
  const group = grouped.get(guide.bundle) ?? { id: guide.bundle.split('/').pop().replace(/\.md$/, ''), bundle: guide.bundle, count: 0 };
  group.count++;
  grouped.set(guide.bundle, group);
}
const outputs = [
  ['generatedClinicalGuides.json', guides],
  ['generatedGuideGroups.json', [...grouped.values()].sort((a,b)=>a.bundle.localeCompare(b.bundle))],
];
for (const [filename, value] of outputs) {
  const out = resolve(appRoot, 'src/data', filename);
  const serialized = JSON.stringify(value, null, 2) + '\n';
  if (process.argv.includes('--check')) {
    if ((await readCanonical(out)) !== serialized) throw new Error('Clinical guide projection is stale: ' + filename);
  } else await writeFile(out, serialized, 'utf8');
}
console.log((process.argv.includes('--check') ? 'Checked ' : 'Generated ') + guides.length + ' canonical clinical guides and navigation groups');
