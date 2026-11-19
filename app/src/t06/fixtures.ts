import type { T06Service } from './viewModel';

/** Synthetic R6 APIResult.as_dict() fixtures; no patients or reserved exams. */
export function fixture(service: T06Service): { service: T06Service; records: Record<string, unknown>[]; total: number | null; provenance: Record<string, unknown> } {
  const endpoints = {
    pubmed: 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi',
    europe_pmc: 'https://www.ebi.ac.uk/europepmc/webservices/rest/search',
    nvd: 'https://services.nvd.nist.gov/rest/json/cves/2.0',
  };
  const records = {
    pubmed: [{ pmid: '123456789', article_url: 'https://pubmed.ncbi.nlm.nih.gov/123456789/' }],
    europe_pmc: [{ id: 'SYNTHETIC-1', source: 'SYNTHETIC', title: 'Documento sintético de prueba', author_string: 'Autor sintético', pub_year: '2026', journal: 'Revista sintética', pmid: null, doi: null }],
    nvd: [{ cve_id: 'CVE-2026-1234', published: '2026-01-01T00:00:00', last_modified: null, description_en: 'Synthetic software metadata; not a clinical recommendation.', cve_url: 'https://nvd.nist.gov/vuln/detail/CVE-2026-1234' }],
  };
  return { service, records: records[service], total: 1, provenance: {
    source: service, endpoint: endpoints[service], query_fingerprint_hmac_sha256: '0'.repeat(64),
    retrieved_utc: '2026-11-16T00:00:00+00:00', from_cache: false, cache_write_status: 'cache_disabled',
    client_version: '0.7.0-R6-transport-contract-candidate', http_status: 200,
    raw_body_sha256: '0'.repeat(64), normalized_content_sha256: '0'.repeat(64), requested_limit: 1,
    api_family: { pubmed: 'NCBI E-utilities ESearch', europe_pmc: 'Europe PMC REST', nvd: 'NIST NVD CVE API 2.0' }[service],
    content_license: null, license_verified: false,
    external_data_trust: 'untrusted_not_safe_for_html_or_llm_instructions',
    scope: 'technical_reference_only_not_clinically_validated',
  } };
}
