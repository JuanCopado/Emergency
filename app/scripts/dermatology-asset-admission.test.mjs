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
    expect(policy.identity_digest).toBe('938e04ec4500be994a5b0d39fa36a469c456d074c8cdf22fed813f2f0dc5fdce');
    const reordered = { ...policy, assets: policy.assets.map((asset) =>
      Object.fromEntries(Object.entries(asset).reverse())) };
    expect(validateManifest(reordered)).toMatchObject({ assets: 24, cases: 23, product_media_admitted: 0 });
    expect(checkRepository(repository)).toMatchObject({ status: 'PASS', registry_assets: 24,
      product_catalog_size: 0, product_media_admitted: 0, clinical: 'CLINICALLY_PENDING' });
    expect(productAssetCatalog(policy)).toEqual([]);
    expect(protectedHashIndex(policy).size).toBe(31);
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

  it('contains all five new derivative hashes without granting their four parent assets a media purpose', () => {
    const index = protectedHashIndex(policy);
    expect(policy.technical_containment.derivatives).toHaveLength(5);
    for (const row of policy.technical_containment.derivatives) {
      expect(index.get(row.derivative_sha256)).toBe(row.asset_id);
      expect(() => authorizeAssetImport(policy, row.asset_id, 'external_service_transfer')).toThrow('NOT_ADMITTED');
    }
  });

  it('rejects missing, spoofed and structurally invalid containment records before scanning', () => {
    for (const mutate of [
      (p) => { p.technical_containment.schema_version = 'other'; },
      (p) => { p.technical_containment.purpose = 'PRODUCT_ADMISSION'; },
      (p) => { p.technical_containment.product_media_admitted = true; },
      (p) => { p.technical_containment.derivatives = []; },
      (p) => { p.technical_containment.derivatives[0].source_sha256 = '0'.repeat(64); },
      (p) => { p.technical_containment.derivatives[0].derivative_sha256 = 'invalid'; },
      (p) => { p.technical_containment.derivatives[0].frame_index = -1; },
      (p) => { p.technical_containment.derivatives[0] = null; },
      (p) => { p.technical_containment.derivatives[0].unrestricted_consent = true; },
      (p) => { p.technical_containment.evidence_sha256 = '0'.repeat(64); },
    ]) {
      const changed = structuredClone(policy); mutate(changed);
      fixture(({ root }) => expect(() => checkRepository(root)).toThrow('POLICY_INVALID'), changed);
    }
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

  it('scans artifact basenames under public and arbitrary nested directories, including extensionless files', () => fixture(({ root, put }) => {
    const locations = ['app/public/dist/a.png', 'app/public/nested/coverage/a.png',
      'app/public/a/b/node_modules/a.png', 'docs/.cache/a.png', 'dist', 'app/public/coverage'];
    for (const location of locations) put(location, bytes);
    const result = scanMediaFiles(root, new Map([[hash(bytes), 'SYNTHETIC_EXACT_BYTE_IDENTITY']]));
    expect(result.examined_raster_files).toBe(locations.length);
    expect(result.issues).toHaveLength(locations.length);
    expect(result.issues.every((issue) => issue.code === 'DERM_REPOSITORY_MEDIA_NOT_ADMITTED')).toBe(true);
  }));

  it('retains reserved namespace protection below nested artifact and dependency names', () => fixture(({ root, put }) => {
    const locations = ['app/public/dermatology/dist/a.png',
      'app/public/dermatology/deep/node_modules/a.png',
      'app/src/assets/dermatology/a/coverage/a.png', 'clinical/assets/dermatology/a/b/.venv/a.png'];
    for (const location of locations) put(location, bytes);
    const result = checkRepository(root);
    expect(result.issues).toHaveLength(locations.length);
    expect(result.issues.every((issue) => issue.code === 'DERM_RESERVED_MEDIA_NOT_ADMITTED')).toBe(true);
  }));

  it('rejects public artifact links and dependency junctions before path exclusions', () => fixture(({ root }) => {
    const target = path.join(root, 'target'); fs.mkdirSync(target);
    for (const location of ['app/public/dist', 'app/public/dermatology/coverage', 'app/node_modules']) {
      const link = path.join(root, location); fs.mkdirSync(path.dirname(link), { recursive: true });
      fs.symlinkSync(target, link, process.platform === 'win32' ? 'junction' : 'dir');
    }
    expect(checkRepository(root).issues).toEqual(
      Array.from({ length: 3 }, () => ({ code: 'DERM_SCAN_LINK_FORBIDDEN' })));
  }));
});
