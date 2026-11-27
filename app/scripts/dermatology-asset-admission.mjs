/** Purpose-specific non-admission guard; no image decoding, transfer or diagnosis. */
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

// Preserve Array.sort's original UTF-16 code-unit order, independent of locale.
function compareCodeUnits(left, right) {
  if (left < right) return -1;
  if (left > right) return 1;
  return 0;
}

const IDENTITY_DIGEST = '938e04ec4500be994a5b0d39fa36a469c456d074c8cdf22fed813f2f0dc5fdce';
const DERIVATIVE_DIGEST = 'b3c3d2294aab934dd32fe9452b3ebe6ddea83861e1446360b04c82083be805f2';
const DERIVATIVE_EVIDENCE = '3b640e2da27f265766d97463815e18ad1e4a90a3eaa9389fda8e60842fd29857';
const DERIVATIVE_KEYS = ['asset_id', 'source_sha256', 'frame_index', 'derivative_sha256'].sort(compareCodeUnits);
const CONTAINMENT_KEYS = ['schema_version', 'purpose', 'evidence_artifact',
  'evidence_sha256', 'identity_digest', 'derivatives'].sort(compareCodeUnits);
const FACIAL_IDS = new Set(['DERMA_CDC_2874', 'DERMA_CDC_27799']);
const MEDIA_ADMISSIONS = ['product_media_admitted', 'repository_media_redistribution_admitted',
  'independent_evaluation_admitted', 'ai_training_admitted', 'external_service_transfer_admitted'];
const RECORD_KEYS = ['asset_id', 'case_id', 'source_sha256', 'technical_derivative_sha256',
  'local_reference_scope', ...MEDIA_ADMISSIONS].sort(compareCodeUnits);
const SKIP_DIRECTORIES = new Set(['.git', 'node_modules', 'dist', 'coverage', '__pycache__',
  '.pytest_cache', '.venv', '.cache']);
const RASTER_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.webp', '.tif', '.tiff']);
const RESERVED_MEDIA = /^(app\/(public|src\/assets)|clinical\/assets)\/dermatology(?:\/|$)/i;
const digest = (value) => createHash('sha256').update(value).digest('hex');

export class AssetAdmissionError extends Error {
  constructor(code) { super(code); this.code = code; }
}
const requirePolicy = (condition) => {
  if (!condition) throw new AssetAdmissionError('DERM_POLICY_INVALID');
};

function validateDerivativeContainment(manifest) {
  const containment = manifest.technical_containment;
  requirePolicy(containment?.schema_version === '1.0'
    && containment.purpose === 'NON_ADMISSION_HASH_COVERAGE_ONLY'
    && containment.evidence_artifact === 'FASE2/DERMA/ASSET_FINALITY_UPDATE_24.json'
    && containment.evidence_sha256 === DERIVATIVE_EVIDENCE
    && containment.identity_digest === DERIVATIVE_DIGEST
    && JSON.stringify(Object.keys(containment).sort(compareCodeUnits)) === JSON.stringify(CONTAINMENT_KEYS)
    && Array.isArray(containment.derivatives) && containment.derivatives.length === 5);
  const identities = [];
  for (const derivative of containment.derivatives) {
    requirePolicy(derivative !== null && typeof derivative === 'object' && !Array.isArray(derivative));
    const source = manifest.assets.find((asset) => asset.asset_id === derivative.asset_id);
    requirePolicy(JSON.stringify(Object.keys(derivative).sort(compareCodeUnits)) === JSON.stringify(DERIVATIVE_KEYS)
      && source?.source_sha256 === derivative.source_sha256 && !FACIAL_IDS.has(derivative.asset_id)
      && Number.isInteger(derivative.frame_index) && derivative.frame_index >= 0
      && /^[a-f0-9]{64}$/.test(derivative.derivative_sha256));
    identities.push([derivative.asset_id, derivative.source_sha256,
      derivative.frame_index, derivative.derivative_sha256]);
  }
  identities.sort((left, right) => compareCodeUnits(left[0], right[0]) || left[2] - right[2]);
  requirePolicy(new Set(identities.map((row) => row[3])).size === 5
    && digest(JSON.stringify(identities)) === DERIVATIVE_DIGEST);
}

export function validateManifest(manifest) {
  requirePolicy(manifest?.schema_version === '1.0'
    && manifest.clinical === 'CLINICALLY_PENDING' && manifest.release === 'NO_GO_CLINICAL_RELEASE'
    && manifest.evidence_receptor === '1f0fed8d731f65168ac338b5ddb18f451fccc6d6');
  const assets = manifest.assets;
  requirePolicy(Array.isArray(assets) && assets.length === 24
    && new Set(assets.map((asset) => asset.asset_id)).size === 24
    && new Set(assets.map((asset) => asset.case_id)).size === 23);
  for (const asset of assets) {
    requirePolicy(JSON.stringify(Object.keys(asset).sort(compareCodeUnits)) === JSON.stringify(RECORD_KEYS)
      && MEDIA_ADMISSIONS.every((key) => asset[key] === false)
      && /^[a-f0-9]{64}$/.test(asset.source_sha256)
      && (asset.technical_derivative_sha256 === null || /^[a-f0-9]{64}$/.test(asset.technical_derivative_sha256)));
    requirePolicy((asset.local_reference_scope === 'EXCLUDED_IDENTIFIABLE_FACE') === FACIAL_IDS.has(asset.asset_id));
  }
  const identity = assets.map((asset) => [asset.asset_id, asset.case_id, asset.source_sha256,
    asset.technical_derivative_sha256, asset.local_reference_scope])
    .sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0);
  requirePolicy(manifest.identity_digest === IDENTITY_DIGEST && digest(JSON.stringify(identity)) === IDENTITY_DIGEST);
  validateDerivativeContainment(manifest);
  const expectedCounts = { assets: 24, cases: 23, local_reference_prepared: 13,
    privacy_context_pending: 9, facial_excluded: 2, product_media_admitted: 0, repository_media_admitted: 0 };
  requirePolicy(Object.entries(expectedCounts).every(([key, value]) => manifest.counts?.[key] === value)
    && assets.filter((a) => a.local_reference_scope === 'LOCAL_REFERENCE_DEVELOPMENT_ONLY').length === 13
    && assets.filter((a) => a.local_reference_scope === 'PRIVACY_CONTEXT_PENDING').length === 9);
  return { assets: 24, cases: 23, local_reference_prepared: 13, product_media_admitted: 0 };
}

export function loadManifest(repositoryRoot) {
  try {
    const manifest = JSON.parse(fs.readFileSync(path.join(repositoryRoot,
      'clinical/qa/dermatology-asset-use-manifest.json'), 'utf8'));
    validateManifest(manifest);
    return manifest;
  } catch {
    throw new AssetAdmissionError('DERM_POLICY_INVALID');
  }
}

/** Metadata review is the only purpose exposed by this product-side consumer. */
export function authorizeAssetImport(manifest, assetId, purpose) {
  validateManifest(manifest);
  const asset = manifest.assets.find((item) => item.asset_id === assetId);
  if (!asset) throw new AssetAdmissionError('DERM_UNKNOWN_ASSET');
  if (purpose === 'documentary_metadata_review') {
    return { asset_id: asset.asset_id, outcome: 'METADATA_ONLY', media_authorized: false };
  }
  throw new AssetAdmissionError(FACIAL_IDS.has(assetId)
    ? 'DERM_FACIAL_ASSET_EXCLUDED' : 'DERM_MEDIA_PURPOSE_NOT_ADMITTED');
}

export function productAssetCatalog(manifest) {
  validateManifest(manifest);
  // There is no admitted product-media record, URL or file path to consume.
  return [];
}

export function protectedHashIndex(manifest) {
  validateManifest(manifest);
  const index = new Map();
  for (const asset of manifest.assets) {
    index.set(asset.source_sha256, asset.asset_id);
    if (asset.technical_derivative_sha256) index.set(asset.technical_derivative_sha256, asset.asset_id);
  }
  for (const derivative of manifest.technical_containment.derivatives) {
    index.set(derivative.derivative_sha256, derivative.asset_id);
  }
  requirePolicy(index.size === 31);
  return index;
}

function rasterSignature(head) {
  return head.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
    || (head[0] === 0xff && head[1] === 0xd8 && head[2] === 0xff)
    || (head.subarray(0, 4).toString() === 'RIFF' && head.subarray(8, 12).toString() === 'WEBP')
    || head.subarray(0, 4).equals(Buffer.from([73, 73, 42, 0]))
    || head.subarray(0, 4).equals(Buffer.from([77, 77, 0, 42]));
}

function readHead(file) {
  const descriptor = fs.openSync(file, 'r');
  try {
    const buffer = Buffer.alloc(16);
    return buffer.subarray(0, fs.readSync(descriptor, buffer, 0, buffer.length, 0));
  } finally { fs.closeSync(descriptor); }
}

function hashFile(file) {
  const descriptor = fs.openSync(file, 'r');
  const hash = createHash('sha256');
  try {
    const buffer = Buffer.alloc(65536);
    for (let read; (read = fs.readSync(descriptor, buffer, 0, buffer.length, null)) > 0;) {
      hash.update(buffer.subarray(0, read));
    }
    return hash.digest('hex');
  } finally { fs.closeSync(descriptor); }
}

function inspectFile(file, relative, protectedHashes) {
  const headerIsRaster = rasterSignature(readHead(file));
  const namedRaster = RASTER_EXTENSIONS.has(path.extname(file).toLowerCase());
  if (RESERVED_MEDIA.test(relative) && (headerIsRaster || namedRaster)) {
    return { examined: 0, issue: { code: 'DERM_RESERVED_MEDIA_NOT_ADMITTED' } };
  }
  if (!headerIsRaster) return { examined: 0 };
  const assetId = protectedHashes.get(hashFile(file));
  return { examined: 1, issue: assetId
    ? { code: 'DERM_REPOSITORY_MEDIA_NOT_ADMITTED', asset_id: assetId } : null };
}

function inspectEntry(directory, entry, state) {
  if (SKIP_DIRECTORIES.has(entry.name)) return;
  const file = path.join(directory, entry.name);
  if (entry.isSymbolicLink()) {
    state.issues.push({ code: 'DERM_SCAN_LINK_FORBIDDEN' });
    return;
  }
  if (entry.isDirectory()) {
    walkDirectory(file, state);
    return;
  }
  if (!entry.isFile()) return;
  const relative = path.relative(state.root, file).split(path.sep).join('/');
  const result = inspectFile(file, relative, state.protectedHashes);
  state.examined += result.examined;
  if (result.issue) state.issues.push(result.issue);
}

function walkDirectory(directory, state) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    inspectEntry(directory, entry, state);
  }
}

/** Low-level scanner accepts an index for synthetic tests; production builds derive it only from validated policy. */
export function scanMediaFiles(repositoryRoot, protectedHashes) {
  const state = { root: fs.realpathSync(repositoryRoot), protectedHashes, issues: [], examined: 0 };
  walkDirectory(state.root, state);
  return { status: state.issues.length ? 'FAIL' : 'PASS', examined_raster_files: state.examined,
    product_media_admitted: 0, issues: state.issues };
}

export function checkRepository(repositoryRoot) {
  const manifest = loadManifest(repositoryRoot);
  const protectedHashes = protectedHashIndex(manifest);
  const result = scanMediaFiles(repositoryRoot, protectedHashes);
  return { ...result, registry_assets: manifest.assets.length,
    product_catalog_size: productAssetCatalog(manifest).length,
    protected_file_identities: protectedHashes.size, additional_derivatives_contained: 5,
    clinical: manifest.clinical, release: manifest.release };
}
