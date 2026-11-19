/** R6 APIResult.as_dict() presentation boundary. No transport, HTML, or prompt API. */
export type T06Service = 'pubmed' | 'europe_pmc' | 'nvd';

type Cell = Readonly<{ label: string; text: string; href?: string }>;
type Row = Readonly<{ cells: readonly Cell[] }>;
export type T06ViewModel = Readonly<{
  provider: string;
  provenance: string;
  status: 'CLINICALLY_PENDING';
  total: number | null;
  rows: readonly Row[];
}>;
export type T06Validation =
  | Readonly<{ ok: true; value: T06ViewModel }>
  | Readonly<{ ok: false; reason: 'INVALID_T06_METADATA' }>;

const PROVIDERS = {
  pubmed: { name: 'PubMed', origin: 'https://pubmed.ncbi.nlm.nih.gov' },
  europe_pmc: { name: 'Europe PMC', origin: 'https://www.ebi.ac.uk' },
  nvd: { name: 'NVD', origin: 'https://nvd.nist.gov' },
} as const;
// Same forbidden Unicode categories as R6: Cc, Cf, Cs, Zl, Zp.
const UNSAFE_CONTROLS = /[\p{Cc}\p{Cf}\p{Cs}\p{Zl}\p{Zp}]/u;
const INVALID = Object.freeze({ ok: false, reason: 'INVALID_T06_METADATA' } as const);

function service(value: unknown): value is T06Service {
  return value === 'pubmed' || value === 'europe_pmc' || value === 'nvd';
}

function object(value: unknown): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new Error();
  const prototype: unknown = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) throw new Error();
  return value as Record<string, unknown>;
}

// Read own data fields only; no inherited values or accessor execution.
function field(value: Record<string, unknown>, key: string): unknown {
  const descriptor = Object.getOwnPropertyDescriptor(value, key);
  if (!descriptor || !('value' in descriptor)) throw new Error();
  return descriptor.value;
}

function text(value: unknown, max: number, nullable = true): string {
  if (value === null && nullable) return 'No documentado';
  if (typeof value !== 'string') throw new Error();
  // R6 Python len/slicing counts Unicode code points, not UTF-16 units.
  // Stop at max + 1 without allocating an array or scanning an oversized value.
  let length = 0;
  for (const character of value) {
    if (++length > max || UNSAFE_CONTROLS.test(character)) throw new Error();
  }
  return value;
}

function cell(label: string, value: unknown, max: number): Cell {
  return Object.freeze({ label, text: text(value, max) });
}

function canonicalLink(label: string, value: unknown, expected: string): Cell {
  // Byte-for-byte canonical form, before any browser URL normalization. This
  // rejects credentials, explicit ports (including 443), traversal, encoded
  // separators, queries/fragments, deceptive hosts, Unicode and whitespace.
  if (typeof value !== 'string' || value !== expected) throw new Error();
  return Object.freeze({ label, text: expected, href: expected });
}

function row(provider: T06Service, value: unknown): Row {
  const record = object(value);
  let cells: Cell[];
  if (provider === 'pubmed') {
    const id = text(field(record, 'pmid'), 9, false);
    if (!/^[0-9]{1,9}$/u.test(id)) throw new Error();
    cells = [cell('PMID', id, 9), canonicalLink('Artículo', field(record, 'article_url'), `${PROVIDERS.pubmed.origin}/${id}/`)];
  } else if (provider === 'nvd') {
    const id = text(field(record, 'cve_id'), 21, false);
    if (!/^CVE-[0-9]{4}-[0-9]{4,12}$/u.test(id)) throw new Error();
    cells = [cell('CVE', id, 21), cell('Publicación', field(record, 'published'), 60),
      cell('Última modificación', field(record, 'last_modified'), 60),
      cell('Descripción externa', field(record, 'description_en'), 1800),
      canonicalLink('Ficha NVD', field(record, 'cve_url'), `${PROVIDERS.nvd.origin}/vuln/detail/${id}`)];
  } else {
    // R6 supplies no canonical Europe PMC hyperlink; IDs, DOI and source are
    // untrusted text. Never infer a link or authority from these fields.
    cells = [cell('ID', field(record, 'id'), 80), cell('Fuente declarada', field(record, 'source'), 40),
      cell('Título externo', field(record, 'title'), 1200), cell('Autores', field(record, 'author_string'), 500),
      cell('Año', field(record, 'pub_year'), 4), cell('Revista', field(record, 'journal'), 300),
      cell('PMID declarado', field(record, 'pmid'), 20), cell('DOI declarado', field(record, 'doi'), 300)];
  }
  return Object.freeze({ cells: Object.freeze(cells) });
}

/**
 * expectedService must be chosen by local caller configuration, never copied
 * from the external payload. Matching service/URL is not provider authentication.
 * R6 provenance is required structurally but never interpreted as a trust claim.
 */
export function buildT06ViewModel(expectedService: T06Service, input: unknown): T06Validation {
  try {
    if (!service(expectedService)) return INVALID;
    const result = object(input);
    if (field(result, 'service') !== expectedService) return INVALID;
    object(field(result, 'provenance'));
    const total = field(result, 'total');
    if (total !== null && (typeof total !== 'number' || !Number.isSafeInteger(total) || total < 0 || total >= 1_000_000_000_000)) return INVALID;
    const records = field(result, 'records');
    if (!Array.isArray(records)) return INVALID;
    // Snapshot once so even an active Proxy cannot grow this loop beyond 50.
    // The contract is passive JSON; this does not make arbitrary JS objects safe.
    const recordCount = records.length;
    if (!Number.isSafeInteger(recordCount) || recordCount < 0 || recordCount > 50) return INVALID;
    const rows: Row[] = [];
    // Indexed reads deliberately reject sparse arrays instead of silently
    // skipping missing rows; R6 emits dense JSON arrays.
    for (let index = 0; index < recordCount; index++) rows.push(row(expectedService, field(records as unknown as Record<string, unknown>, String(index))));
    const provider = PROVIDERS[expectedService];
    return Object.freeze({ ok: true, value: Object.freeze({
      provider: provider.name,
      provenance: `Contrato local T06/R6: ${provider.name} (${provider.origin}). Contenido externo no verificado; autenticidad y transporte no acreditados.`,
      status: 'CLINICALLY_PENDING', total, rows: Object.freeze(rows),
    }) });
  } catch {
    // No attacker-provided body, URL, metadata or exception text reaches errors.
    return INVALID;
  }
}
