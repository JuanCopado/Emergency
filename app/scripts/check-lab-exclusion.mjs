// Fails when a production build contains any marker of the lab-only Layer 7 harness (SIMULATED_LAB_HARNESS_ONLY).
// Usage: node scripts/check-lab-exclusion.mjs [distDir]. Prints counts only; never prints file content.
import fs from 'node:fs';
import path from 'node:path';

const MARKERS = ['LAB_LAYER7_MARKER', '/api/lab/layer7/evaluate', '__LAB_LAYER7_LOG__', 'SIMULATED_LAB_HARNESS_ONLY', 'data-lab-layer7'];
const root = path.resolve(process.argv[2] ?? 'dist');
if (!fs.existsSync(root)) { console.error(`no build output at ${root}`); process.exit(2); }

const hits = {};
let files = 0;
(function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) { walk(full); continue; }
    if (!/\.(js|mjs|css|html|map|json)$/.test(entry.name)) continue;
    files += 1;
    const text = fs.readFileSync(full, 'utf8');
    for (const marker of MARKERS) if (text.includes(marker)) (hits[marker] ??= []).push(path.relative(root, full));
  }
})(root);

const found = Object.keys(hits);
console.log(JSON.stringify({ scanned_files: files, markers_checked: MARKERS.length, markers_found: found.length, files_with_markers: [...new Set(Object.values(hits).flat())].length }));
process.exit(found.length === 0 ? 0 : 1);
