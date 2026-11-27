import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { loadManifest, validateManifest, authorizeAssetImport, productAssetCatalog,
  protectedHashIndex, scanMediaFiles, checkRepository } from './dermatology-asset-admission.mjs';

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const policy = loadManifest(repository);
const bytes = Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
  Buffer.from('synthetic contract fixture; no clinical source pixels')]);
const hash = (value) => createHash('sha256').update(value).digest('hex');

function fixture(run, initial = policy) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'emergency-derm-contract-'));
  const put = (relative, data) => {
    const target = path.join(root, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, data);
    return target;
  };
  if (initial) put('clinical/qa/dermatology-asset-use-manifest.json', JSON.stringify(initial));
  try { return run({ root, put }); } finally {
    const resolved = path.resolve(root);
    expect(resolved.startsWith(path.resolve(os.tmpdir()) + path.sep)).toBe(true);
    expect(path.basename(resolved).startsWith('emergency-derm-contract-')).toBe(true);
    fs.rmSync(resolved, { recursive: true, force: true });
  }
}

describe('product/repository dermatology admission contract', () => {
  it('reads the real repository evidence and supplies an empty media catalog', () => {
    expect(checkRepository(repository)).toMatchObject({ status: 'PASS', registry_assets: 24,
      product_catalog_size: 0, product_media_admitted: 0, clinical: 'CLINICALLY_PENDING' });
    expect(productAssetCatalog(policy)).toEqual([]);
    expect(protectedHashIndex(policy).size).toBe(26);
  });

  it('permits documentary metadata for every source while denying every product media request', () => {
    for (const asset of policy.assets) {
      expect(authorizeAssetImport(policy, asset.asset_id, 'documentary_metadata_review'))
        .toMatchObject({ outcome: 'METADATA_ONLY', media_authorized: false });
      for (const purpose of ['product_display', 'repository_redistribution', 'ai_training', 'independent_evaluation']) {
        expect(() => authorizeAssetImport(policy, asset.asset_id, purpose)).toThrow(/EXCLUDED|NOT_ADMITTED/);
      }
    }
    expect(() => authorizeAssetImport(policy, 'missing', 'product_display')).toThrow('DERM_UNKNOWN_ASSET');
  });

  it('rejects actual persisted permission escalation before scanning any media', () => {
    const changed = structuredClone(policy);
    changed.assets[0].repository_media_redistribution_admitted = true;
    fixture(({ root }) => expect(() => checkRepository(root)).toThrow('DERM_POLICY_INVALID'), changed);
  });

  it('does not equate facial reclassification, new hashes or unsupported clinical state with evidence', () => {
    for (const mutate of [
      (p) => { p.assets.find((a) => a.asset_id === 'DERMA_CDC_27799').local_reference_scope = 'LOCAL_REFERENCE_DEVELOPMENT_ONLY'; },
      (p) => { p.assets[0].source_sha256 = '0'.repeat(64); },
      (p) => { p.assets[0].technical_derivative_sha256 = 'invalid'; },
      (p) => { p.clinical = 'GREEN'; },
      (p) => { p.counts.privacy_context_pending = 0; },
      (p) => { p.assets = []; },
    ]) {
      const changed = structuredClone(policy); mutate(changed);
      expect(() => validateManifest(changed)).toThrow('DERM_POLICY_INVALID');
    }
  });

  it('fails closed when the actual policy file is missing or invalid JSON', () => {
    fixture(({ root }) => expect(() => checkRepository(root)).toThrow('DERM_POLICY_INVALID'), null);
    fixture(({ root, put }) => {
      put('clinical/qa/dermatology-asset-use-manifest.json', '{broken');
      expect(() => checkRepository(root)).toThrow('DERM_POLICY_INVALID');
    });
  });

  it('refuses an unknown reserved media file without deleting unrelated artwork', () => fixture(({ root, put }) => {
    const icon = put('app/public/icon.png', bytes);
    expect(checkRepository(root).status).toBe('PASS');
    put('app/public/dermatology/unknown-raster-without-extension', bytes);
    const result = checkRepository(root);
    expect(result.status).toBe('FAIL');
    expect(result.issues).toContainEqual({ code: 'DERM_RESERVED_MEDIA_NOT_ADMITTED' });
    expect(hash(fs.readFileSync(icon))).toBe(hash(bytes));
    expect(result.product_catalog_size).toBe(0);
  }));

  it('binds rejection to exact bytes rather than filename or extension', () => fixture(({ root, put }) => {
    put('docs/alias-without-extension', bytes);
    const result = scanMediaFiles(root, new Map([[hash(bytes), 'SYNTHETIC_EXACT_BYTE_IDENTITY']]));
    expect(result.issues).toContainEqual({ code: 'DERM_REPOSITORY_MEDIA_NOT_ADMITTED', asset_id: 'SYNTHETIC_EXACT_BYTE_IDENTITY' });
  }));

  it('rejects reserved deceptive filenames and does not follow filesystem links', () => fixture(({ root, put }) => {
    put('clinical/assets/dermatology/not-a-real-raster.JPEG', 'plain synthetic fixture');
    const target = path.join(root, 'target'); fs.mkdirSync(target);
    fs.symlinkSync(target, path.join(root, 'linked'), process.platform === 'win32' ? 'junction' : 'dir');
    const codes = checkRepository(root).issues.map((issue) => issue.code);
    expect(codes).toContain('DERM_RESERVED_MEDIA_NOT_ADMITTED');
    expect(codes).toContain('DERM_SCAN_LINK_FORBIDDEN');
  }));

  it('keeps ignored dependencies outside its claim without treating them as product admission', () => fixture(({ root, put }) => {
    put('node_modules/fixture/dermatology/ignored.png', bytes);
    const result = checkRepository(root);
    expect(result).toMatchObject({ status: 'PASS', examined_raster_files: 0, product_catalog_size: 0 });
    // This explicitly documents the scan boundary; it is not a privacy certificate for ignored folders.
  }));
});
