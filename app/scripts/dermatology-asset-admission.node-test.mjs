import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { validateManifest, loadManifest, authorizeAssetImport, productAssetCatalog,
  protectedHashIndex, scanMediaFiles, checkRepository } from './dermatology-asset-admission.mjs';

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO = path.resolve(APP, '..');
const policy = loadManifest(REPO);
const sha = (data) => createHash('sha256').update(data).digest('hex');
const fixtureBytes = Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
  Buffer.from('synthetic signature fixture, no clinical pixels')]);

function temporary(callback) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'emergency-derm-gate-'));
  try { return callback(directory); } finally {
    const resolved = path.resolve(directory);
    const intended = path.resolve(os.tmpdir()) + path.sep;
    assert.ok(resolved.startsWith(intended) && path.basename(resolved).startsWith('emergency-derm-gate-'));
    fs.rmSync(resolved, { recursive: true, force: true });
  }
}

function put(root, relative, data) {
  const target = path.join(root, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, data);
  return target;
}

function copyGuard(root) {
  for (const filename of ['dermatology-asset-admission.mjs', 'check-dermatology-asset-admission.mjs']) {
    put(root, `app/scripts/${filename}`, fs.readFileSync(path.join(APP, 'scripts', filename)));
  }
  put(root, 'clinical/qa/dermatology-asset-use-manifest.json', JSON.stringify(policy));
  put(root, 'app/package.json', JSON.stringify({ type: 'module' }));
}

test('24 assets/23 cases remain metadata-only, with13 local preparations and26 protected file identities', () => {
  assert.deepEqual(validateManifest(policy), { assets: 24, cases: 23,
    local_reference_prepared: 13, product_media_admitted: 0 });
  assert.equal(protectedHashIndex(policy).size, 26);
  assert.deepEqual(productAssetCatalog(policy), []);
});

test('all24 asset IDs deny product import, including all13 local-reference preparations', () => {
  for (const asset of policy.assets) {
    assert.throws(() => authorizeAssetImport(policy, asset.asset_id, 'product_display'),
      (error) => ['DERM_FACIAL_ASSET_EXCLUDED', 'DERM_MEDIA_PURPOSE_NOT_ADMITTED'].includes(error.code));
  }
});

test('metadata purpose returns no media authority; local development is not product admission', () => {
  const id = policy.assets[0].asset_id;
  assert.deepEqual(authorizeAssetImport(policy, id, 'documentary_metadata_review'),
    { asset_id: id, outcome: 'METADATA_ONLY', media_authorized: false });
  for (const purpose of ['local_reference_development', 'repository_redistribution',
    'independent_evaluation', 'ai_training', 'external_service_transfer']) {
    assert.throws(() => authorizeAssetImport(policy, id, purpose), /NOT_ADMITTED/);
  }
});

test('unknown IDs cannot be laundered into a product import', () => {
  assert.throws(() => authorizeAssetImport(policy, 'UNKNOWN', 'product_display'), /UNKNOWN_ASSET/);
});

test('checkbox permission promotion cannot alter the current evidence contract', () => {
  const changed = structuredClone(policy);
  changed.assets[0].product_media_admitted = true;
  assert.throws(() => validateManifest(changed), /POLICY_INVALID/);
});

test('facial status cannot be cleared by changing a flag', () => {
  const changed = structuredClone(policy);
  changed.assets.find((a) => a.asset_id === 'DERMA_CDC_2874').local_reference_scope = 'LOCAL_REFERENCE_DEVELOPMENT_ONLY';
  assert.throws(() => validateManifest(changed), /POLICY_INVALID/);
});

test('identity swaps, duplicated cases and clinical promotion fail closed', () => {
  for (const mutate of [
    (p) => { p.assets[0].source_sha256 = '0'.repeat(64); },
    (p) => { p.assets[1].case_id = p.assets[0].case_id; },
    (p) => { p.clinical = 'APPROVED'; },
    (p) => { p.assets[0].unrestricted_consent = true; },
  ]) {
    const changed = structuredClone(policy); mutate(changed);
    assert.throws(() => validateManifest(changed), /POLICY_INVALID/);
  }
});

test('protected bytes are detected by hash after rename and extension removal', () => temporary((root) => {
  put(root, 'docs/renamed-no-extension', fixtureBytes);
  const result = scanMediaFiles(root, new Map([[sha(fixtureBytes), 'SYNTHETIC_ASSET']]));
  assert.equal(result.status, 'FAIL');
  assert.deepEqual(result.issues, [{ code: 'DERM_REPOSITORY_MEDIA_NOT_ADMITTED', asset_id: 'SYNTHETIC_ASSET' }]);
}));

test('an unregistered raster in the reserved namespace is rejected even without a known digest', () => temporary((root) => {
  put(root, 'app/public/dermatology/unknown.bin', fixtureBytes);
  assert.equal(scanMediaFiles(root, new Map()).issues[0].code, 'DERM_RESERVED_MEDIA_NOT_ADMITTED');
}));

test('reserved raster filenames do not gain admission by hiding a non-image body', () => temporary((root) => {
  put(root, 'app/src/assets/dermatology/hidden.JPG', 'not image bytes');
  assert.equal(scanMediaFiles(root, new Map()).status, 'FAIL');
}));

test('unrelated existing artwork is not removed or declared clinically admitted', () => temporary((root) => {
  const file = put(root, 'app/public/icon.png', fixtureBytes);
  assert.equal(scanMediaFiles(root, new Map()).status, 'PASS');
  assert.equal(sha(fs.readFileSync(file)), sha(fixtureBytes));
}));

test('directory links cannot redirect the repository scan to another location', () => temporary((root) => {
  const target = path.join(root, 'target'); fs.mkdirSync(target);
  fs.symlinkSync(target, path.join(root, 'linked'), process.platform === 'win32' ? 'junction' : 'dir');
  assert.equal(scanMediaFiles(root, new Map()).issues[0].code, 'DERM_SCAN_LINK_FORBIDDEN');
}));

test('the actual base repository has no admitted corpus media and an empty product catalog', () => {
  const result = checkRepository(REPO);
  assert.equal(result.status, 'PASS');
  assert.equal(result.registry_assets, 24);
  assert.equal(result.product_catalog_size, 0);
});

test('CLI derives the real root from its location and rejects alternate-root arguments', () => temporary((root) => {
  copyGuard(root);
  put(root, 'app/public/dermatology/blocked.png', fixtureBytes);
  const script = path.join(root, 'app/scripts/check-dermatology-asset-admission.mjs');
  const run = spawnSync(process.execPath, [script], { cwd: os.tmpdir(), encoding: 'utf8', windowsHide: true });
  assert.equal(run.status, 1);
  assert.equal(JSON.parse(run.stdout).issues[0].code, 'DERM_RESERVED_MEDIA_NOT_ADMITTED');
  const bypass = spawnSync(process.execPath, [script, '--repo-root', os.tmpdir()], { encoding: 'utf8', windowsHide: true });
  assert.equal(bypass.status, 1);
}));

test('standard npm development/build hooks preserve security and actually stop a prohibited import', () => temporary((root) => {
  copyGuard(root);
  const production = JSON.parse(fs.readFileSync(path.join(APP, 'package.json'), 'utf8'));
  for (const hook of ['predev', 'prebuild']) {
    assert.equal(production.scripts[hook], 'node scripts/check-dermatology-asset-admission.mjs && node scripts/picomatch-mitigation.mjs --check');
  }
  put(root, 'app/package.json', JSON.stringify({ type: 'module', scripts: { prebuild: production.scripts.prebuild } }));
  put(root, 'app/public/dermatology/prohibited.png', fixtureBytes);
  assert.ok(process.env.npm_execpath, 'Run via npm run dermatology:gate:test to verify the npm lifecycle');
  const result = spawnSync(process.execPath, [process.env.npm_execpath, 'run', 'prebuild'],
    { cwd: path.join(root, 'app'), encoding: 'utf8', windowsHide: true });
  assert.notEqual(result.status, 0);
  assert.match(result.stdout, /DERM_RESERVED_MEDIA_NOT_ADMITTED/);
  assert.doesNotMatch(result.stderr, /MODULE_NOT_FOUND/); // guard stops before the intentionally absent second command
}));
