import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(here, '..');
const repoRoot = resolve(appRoot, '..');
const clinicalRoot = resolve(repoRoot, 'clinical');

const indexText = await readFile(resolve(clinicalRoot, 'references/module-index.md'), 'utf8');
const modulesText = await readFile(resolve(clinicalRoot, 'MODULES.md'), 'utf8');

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
  if (!cache.has(bundle)) cache.set(bundle, await readFile(resolve(clinicalRoot, bundle), 'utf8'));
  return cache.get(bundle);
}

const titleize = (id) => id.split('-').map((w) => w ? w[0].toUpperCase() + w.slice(1) : w).join(' ');
const guides = [];

for (const entry of entries) {
  const content = await getBundle(entry.bundle);
  const marker = '## ' + entry.id;
  const start = content.indexOf(marker);
  if (start < 0) throw new Error('Missing canonical heading: ' + entry.id);
  const bodyStart = start + marker.length;
  const next = content.indexOf('\n## ', bodyStart);
  guides.push({
    id: entry.id,
    title: titleize(entry.id),
    bundle: entry.bundle,
    sourcePath: 'clinical/' + entry.bundle,
    status: statusMap.get(entry.id) ?? 'yellow',
    body: content.slice(bodyStart, next >= 0 ? next : content.length).trim(),
  });
}

const out = resolve(appRoot, 'src/data/generatedClinicalGuides.json');
await writeFile(out, JSON.stringify(guides, null, 2) + '\n', 'utf8');
console.log('Generated ' + guides.length + ' canonical clinical guides');
