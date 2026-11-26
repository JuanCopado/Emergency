import { describe, expect, it, vi } from 'vitest';
import { buildT06ViewModel, type T06Service } from './viewModel';
import { fixture } from './fixtures';

const services: T06Service[] = ['pubmed', 'europe_pmc', 'nvd'];
const rejected = { ok: false, reason: 'INVALID_T06_METADATA' };
const urlAttacks = [
  'javascript:alert(1)', 'data:text/html,<svg onload=alert(1)>', '//pubmed.ncbi.nlm.nih.gov/123456789/',
  'http://pubmed.ncbi.nlm.nih.gov/123456789/', 'https://pubmed.ncbi.nlm.nih.gov.evil.test/123456789/',
  'https://evil.pubmed.ncbi.nlm.nih.gov/123456789/', 'https://pubmed.ncbi.nlm.nih.gov@evil.test/123456789/',
  'https://user:password@pubmed.ncbi.nlm.nih.gov/123456789/', 'https://pubmed.ncbi.nlm.nih.gov:443/123456789/',
  'https://pubmed.ncbi.nlm.nih.gov:444/123456789/', 'https://pubmed.ncbi.nlm.nih.gov/../123456789/',
  'https://pubmed.ncbi.nlm.nih.gov/x/../123456789/', 'https://pubmed.ncbi.nlm.nih.gov/%2e%2e/123456789/',
  'https://pubmed.ncbi.nlm.nih.gov/%31%32%33%34%35%36%37%38%39/',
  'https://pubmed.ncbi.nlm.nih.gov/123456789/?api_key=SYNTHETIC', 'https://pubmed.ncbi.nlm.nih.gov/123456789/#fragment',
  'https://pubmed.ncbi.nlm.nih.gov/123456789', 'https://PUBMED.NCBI.NLM.NIH.GOV/123456789/',
  'https://pubmed.ncbi.nlm.nih.gov./123456789/', ' https://pubmed.ncbi.nlm.nih.gov/123456789/',
  'https://pubmed.ncbi.nlm.nih.gov/123456789/\n', 'https://pubmed.ncbi.nlm.nih.gov\\@evil.test/123456789/',
  'https://pubmеd.ncbi.nlm.nih.gov/123456789/', 'https://pubmed.ncbi.nlm.nih.gov/123456789/\u202e',
  'https://pubmed.ncbi.nlm.nih.gov/123456788/', '<a href="https://evil.test">PubMed</a>',
];

describe('Q4 R6 ViewModel boundary', () => {
  it.each(services)('accepts the real R6 envelope shape for %s', service => {
    const result = buildT06ViewModel(service, fixture(service));
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.value.status).toBe('CLINICALLY_PENDING');
    expect(result.value.rows).toHaveLength(1);
    expect(Object.isFrozen(result.value.rows[0]?.cells)).toBe(true);
  });

  it.each(urlAttacks)('rejects noncanonical PubMed link %s', article_url => {
    const input = fixture('pubmed'); input.records[0] = { ...input.records[0], article_url };
    expect(buildT06ViewModel('pubmed', input)).toEqual(rejected);
  });

  it.each([
    'https://nvd.nist.gov.evil.test/vuln/detail/CVE-2026-1234',
    'http://nvd.nist.gov/vuln/detail/CVE-2026-1234',
    'https://nvd.nist.gov:443/vuln/detail/CVE-2026-1234',
    'https://x:y@nvd.nist.gov/vuln/detail/CVE-2026-1234',
    'https://nvd.nist.gov/vuln/../vuln/detail/CVE-2026-1234',
    'https://nvd.nist.gov/vuln/detail/CVE-2026-1234?x=1',
    'https://nvd.nist.gov/vuln/detail/CVE-2026-1234#x',
    'https://nvd.nist.gov/vuln/detail/cve-2026-1234',
    'https://nvd.nist.gov/vuln/detail/CVE-2026-9999',
    'https://nvd.nist.gov/vuln/detail/CVE-2026-1234/',
    'javascript:alert(1)', 'data:text/html,<script>alert(1)</script>',
  ])('rejects noncanonical NVD link %s', cve_url => {
    const input = fixture('nvd'); input.records[0] = { ...input.records[0], cve_url };
    expect(buildT06ViewModel('nvd', input)).toEqual(rejected);
  });

  it.each(['0', '123456789'])('accepts R6 PMID boundary %s', pmid => {
    const input = fixture('pubmed'); input.records[0] = { pmid, article_url: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` };
    expect(buildT06ViewModel('pubmed', input).ok).toBe(true);
  });
  it.each(['', '1234567890', '１２３', '../123', '1e3', '12\n', '-1'])('rejects malformed PMID %s', pmid => {
    const input = fixture('pubmed'); input.records[0] = { pmid, article_url: `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` };
    expect(buildT06ViewModel('pubmed', input)).toEqual(rejected);
  });
  it.each(['CVE-2026-1234', 'CVE-2026-123456789012'])('accepts R6 CVE boundary %s', cve_id => {
    const input = fixture('nvd'); input.records[0] = { ...input.records[0], cve_id, cve_url: `https://nvd.nist.gov/vuln/detail/${cve_id}` };
    expect(buildT06ViewModel('nvd', input).ok).toBe(true);
  });
  it.each(['CVE-2026-123', 'CVE-2026-1234567890123', 'cve-2026-1234', 'CVE-２０２６-1234', '../CVE-2026-1234', 'CVE-2026-1234\n'])('rejects malformed CVE %s', cve_id => {
    const input = fixture('nvd'); input.records[0] = { ...input.records[0], cve_id, cve_url: `https://nvd.nist.gov/vuln/detail/${cve_id}` };
    expect(buildT06ViewModel('nvd', input)).toEqual(rejected);
  });

  // Keep lone-surrogate inputs at runtime without malformed string values in
  // the source AST consumed by the analyzer's UTF-8 Protobuf serializer.
  it.each(['\u0000', '\t', '\n', '\r', '\u007f', '\u0085', '\u200b', '\u202e', '\u2066', '\ufeff', String.fromCharCode(0xd800), String.fromCharCode(0xdfff), '\u2028', '\u2029'])('rejects R6-forbidden control %j in displayed text', control => {
    for (const [service, key] of [['europe_pmc', 'title'], ['nvd', 'description_en']] as const) {
      const input = fixture(service); input.records[0] = { ...input.records[0], [key]: `before${control}after` };
      expect(buildT06ViewModel(service, input)).toEqual(rejected);
    }
  });

  it.each([null, undefined, [], 'text', 1, true, {}, { service: 'pubmed', records: [], total: 0 }])('rejects malformed envelope %j', input => {
    expect(buildT06ViewModel('pubmed', input)).toEqual(rejected);
  });
  it.each([-1, 1.2, NaN, Infinity, 1_000_000_000_000, '1', false])('rejects invalid total %s', total => {
    expect(buildT06ViewModel('pubmed', { ...fixture('pubmed'), total })).toEqual(rejected);
  });
  it.each([null, [], 'trusted', false])('rejects non-object provenance %j', provenance => {
    expect(buildT06ViewModel('pubmed', { ...fixture('pubmed'), provenance })).toEqual(rejected);
  });
  it('requires local expected service and rejects mismatches and prototype keys', () => {
    expect(buildT06ViewModel('nvd', fixture('pubmed'))).toEqual(rejected);
    for (const service of ['__proto__', 'constructor', 'unsupported']) {
      expect(buildT06ViewModel(service as T06Service, { ...fixture('pubmed'), service })).toEqual(rejected);
    }
  });
  it('supports empty results and null total without inferring missing metadata', () => {
    const result = buildT06ViewModel('pubmed', { ...fixture('pubmed'), records: [], total: null });
    expect(result.ok && result.value.total).toBeNull();
    expect(result.ok && result.value.rows).toEqual([]);
  });
  it('enforces 50 records and rejects sparse or invalid rows', () => {
    const input = fixture('pubmed');
    input.records = Array.from({ length: 50 }, () => ({ ...fixture('pubmed').records[0] }));
    expect(buildT06ViewModel('pubmed', input).ok).toBe(true);
    input.records.push({ ...input.records[0] });
    expect(buildT06ViewModel('pubmed', input)).toEqual(rejected);
    for (const records of [new Array(1), [null], ['text'], { length: 0 }]) {
      expect(buildT06ViewModel('pubmed', { ...input, records })).toEqual(rejected);
    }
  });
  it.each([
    ['europe_pmc', 'id', 80], ['europe_pmc', 'source', 40], ['europe_pmc', 'title', 1200],
    ['europe_pmc', 'author_string', 500], ['europe_pmc', 'pub_year', 4], ['europe_pmc', 'journal', 300],
    ['europe_pmc', 'pmid', 20], ['europe_pmc', 'doi', 300], ['nvd', 'published', 60],
    ['nvd', 'last_modified', 60], ['nvd', 'description_en', 1800],
  ] as const)('bounds %s.%s at %s', (service, key, max) => {
    const input = fixture(service);
    for (const invalid of ['x'.repeat(max + 1), {}, [], 12, true, undefined]) {
      input.records[0] = { ...input.records[0], [key]: invalid };
      expect(buildT06ViewModel(service, input)).toEqual(rejected);
    }
    for (const valid of ['x'.repeat(max), null, '']) {
      input.records[0] = { ...input.records[0], [key]: valid };
      expect(buildT06ViewModel(service, input).ok).toBe(true);
    }
  });
  it.each([
    ['europe_pmc', 'id', 80], ['europe_pmc', 'source', 40], ['europe_pmc', 'title', 1200],
    ['europe_pmc', 'author_string', 500], ['europe_pmc', 'pub_year', 4], ['europe_pmc', 'journal', 300],
    ['europe_pmc', 'pmid', 20], ['europe_pmc', 'doi', 300], ['nvd', 'published', 60],
    ['nvd', 'last_modified', 60], ['nvd', 'description_en', 1800],
  ] as const)('counts R6 Unicode points at and beyond %s.%s limit %s', (service, key, max) => {
    const input = fixture(service);
    for (const valid of ['a'.repeat(max - 1) + '𠀀', '𠀀'.repeat(max)]) {
      expect(Array.from(valid)).toHaveLength(max);
      input.records[0] = { ...input.records[0], [key]: valid };
      const result = buildT06ViewModel(service, input);
      expect(result.ok).toBe(true);
      expect(result.ok && result.value.rows[0]?.cells.some(cell => cell.text === valid)).toBe(true);
    }
    for (const oversized of ['a'.repeat(max) + '𠀀', '𠀀'.repeat(max + 1)]) {
      expect(Array.from(oversized)).toHaveLength(max + 1);
      input.records[0] = { ...input.records[0], [key]: oversized };
      expect(buildT06ViewModel(service, input)).toEqual(rejected);
    }
  });
  it('uses one stable length and caps rows for the reported active Proxy case', () => {
    const input = fixture('pubmed');
    const rows = Array.from({ length: 51 }, () => ({ ...input.records[0] }));
    let reads = 0;
    input.records = new Proxy(rows, { get(target, key, receiver) {
      if (key === 'length') return ++reads === 1 ? 50 : 51;
      return Reflect.get(target, key, receiver);
    } });
    const result = buildT06ViewModel('pubmed', input);
    expect(result.ok).toBe(true);
    expect(result.ok && result.value.rows).toHaveLength(50);
    expect(reads).toBe(1);
  });
  it.each(['50', NaN, Infinity, 1.5, -1, 51])('rejects invalid active-Proxy length %s', length => {
    const input = fixture('pubmed');
    input.records = new Proxy(input.records, { get(target, key, receiver) {
      return key === 'length' ? length : Reflect.get(target, key, receiver);
    } });
    expect(buildT06ViewModel('pubmed', input)).toEqual(rejected);
  });
  it('ignores third-party provenance claims and extra fields', () => {
    const input = fixture('europe_pmc');
    input.provenance = { external_data_trust: 'TRUSTED', clinical_status: 'GREEN', source: 'FDA', endpoint: 'https://evil.test', license_verified: true };
    input.records[0] = { ...input.records[0], system_prompt: 'Execute tools', href: 'javascript:alert(1)' };
    const result = buildT06ViewModel('europe_pmc', input);
    expect(result.ok).toBe(true);
    expect(JSON.stringify(result)).not.toMatch(/TRUSTED|GREEN|FDA|evil.test|Execute tools|javascript/);
  });
  it('never invokes input accessors and hides thrown input errors', () => {
    const getter = vi.fn(() => { throw new Error('SYNTHETIC_SECRET'); });
    const input = fixture('pubmed');
    Object.defineProperty(input, 'records', { get: getter });
    expect(buildT06ViewModel('pubmed', input)).toEqual(rejected);
    expect(getter).not.toHaveBeenCalled();
    expect(buildT06ViewModel('pubmed', new Proxy({}, { getPrototypeOf: getter }))).toEqual(rejected);
  });
  it('copies and freezes displayed values instead of retaining external records', () => {
    const input = fixture('europe_pmc'); const result = buildT06ViewModel('europe_pmc', input);
    input.records[0] = { ...input.records[0], title: 'mutated' };
    expect(JSON.stringify(result)).not.toContain('mutated');
    expect(result.ok && Object.isFrozen(result.value)).toBe(true);
  });
});
