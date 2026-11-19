"""Explicit offline HTML presentation boundary for untrusted metadata.

Not an LLM sanitizer or a web/PWA integration. Never place raw external text
into HTML attributes, script, URL navigation, CSS, or prompts.
"""
from __future__ import annotations

from collections.abc import Mapping
from html import escape
import re
from types import MappingProxyType
from .clients import APIResult, ValidationError, _has_unsafe_controls

DISPLAY_FIELDS = MappingProxyType({
    "pubmed": ("pmid", "article_url"),
    "europe_pmc": ("id", "source", "title", "author_string", "pub_year", "journal", "pmid", "doi"),
    "nvd": ("cve_id", "published", "last_modified", "description_en", "cve_url"),
})

# Exact canonical URL forms. These are TEXT only: not an HTML hyperlink API.
# Validation prevents accidental unsafe link reuse in a future consumer.
_OFFICIAL_URL_PATTERNS = MappingProxyType({
    "article_url": re.compile(r"https://pubmed\.ncbi\.nlm\.nih\.gov/[0-9]{1,9}/", re.ASCII),
    "cve_url": re.compile(r"https://nvd\.nist\.gov/vuln/detail/CVE-[0-9]{4}-[0-9]{4,12}", re.ASCII),
})


def _html_cell(value: object, *, field: str) -> str:
    """Safely render one untrusted text node, including type and URL gates.

    No navigation or HTML attributes are generated here. Exact URL validation
    ensures future consumers cannot mistake arbitrary text for an official link.
    """
    if value is None:
        return ""
    if type(value) not in (str, int):
        raise ValidationError("Unsupported external presentation value")
    if isinstance(value, str) and _has_unsafe_controls(value):
        raise ValidationError("External presentation value contains unsafe Unicode")
    if field in _OFFICIAL_URL_PATTERNS:
        if not isinstance(value, str) or not _OFFICIAL_URL_PATTERNS[field].fullmatch(value):
            raise ValidationError("Unsupported external reference URL")
    return escape(str(value), quote=True)


def render_static_html(result: APIResult) -> str:
    """Safe *static* HTML display, no external assets/scripts/navigation/LLM.

    Escaping is contextual for HTML *text nodes only*. This deliberately does
    not accept HTML templates or provide a general HTML-sanitization API.
    """
    if not isinstance(result, APIResult) or result.service not in DISPLAY_FIELDS:
        raise ValidationError("Unsupported external presentation result")
    if not isinstance(result.provenance, Mapping):
        raise ValidationError("Invalid provenance metadata")
    if result.provenance.get("external_data_trust") != "untrusted_not_safe_for_html_or_llm_instructions":
        raise ValidationError("External data provenance label missing")
    fields = DISPLAY_FIELDS[result.service]
    head = "".join(f"<th>{escape(field)}</th>" for field in fields)
    rows: list[str] = []
    if len(result.records) > 50:
        raise ValidationError("Too many records for static display")
    for record in result.records:
        if not isinstance(record, dict):
            raise ValidationError("External record schema mismatch")
        cells = "".join(f"<td>{_html_cell(record.get(field), field=field)}</td>" for field in fields)
        rows.append("<tr>" + cells + "</tr>")
    # CSP adds defense in depth for this standalone file; actual web apps must
    # enforce HTTP-header CSP and React DOM text escaping on every relevant route.
    csp = "default-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta http-equiv="Content-Security-Policy" content="' + csp + '">'
            '<title>Emergency T06 — metadatos externos no verificados</title></head><body>'
            '<h1>Datos externos no verificados — uso documental</h1>'
            '<p>Sin validación clínica. No introducir en indicaciones terapéuticas ni prompts LLM.</p>'
            '<table><thead><tr>' + head + '</tr></thead><tbody>' + ''.join(rows) +
            '</tbody></table></body></html>')
