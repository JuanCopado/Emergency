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

const entries = indexText
  .split('\n')
  .map((line) => line.match(/^\|\s*\`?([^|\`]+?)\`?\s*\|\s*\`([^\`]+)\`\s*\|$/))
  .filter(Boolean)
  .map((match) => ({ id: match[1].trim(), bundle: match[2].trim() }))
  .filter((entry) => entry.id !== 'Module ID');

const statusMap = new Map();
for (const line of modulesText.split('\n')) {
  const parts = line.split('|').map((part) => part.trim());
  if (parts.length < 5) continue;
  const idMatch = parts[1]?.match(/^\`([^\`]+)\`$/);
  const status = parts[3]?.toLowerCase();
  if (idMatch && ['green', 'yellow', 'red'].includes(status)) statusMap.set(idMatch[1], status);
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
    status: statusMap.get(entry.id) ?? 'yellow',
    format: classifyFormat(entry.id),
    sharedPreamble,
    sectionBody,
  });
}

const out = resolve(appRoot, 'src/data/generatedClinicalGuides.json');
await writeFile(out, JSON.stringify(guides, null, 2) + '\n', 'utf8');
console.log('Generated ' + guides.length + ' canonical clinical guides');
