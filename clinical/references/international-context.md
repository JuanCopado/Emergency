# International clinical context

Owner direction: 2026-11-16. Canonical project scope: [Emergency international scope](../../docs/INTERNATIONAL_SCOPE.md).

Emergency has an international, extensible clinical core. Country, regional and organizational contexts are selectable profiles; they do not define the whole product. Portugal, the Azores and Hospital da Horta remain identifiable contexts for the evidence and operational decisions already recorded. They are not default requirements for every user, module or future implementation.

This reference governs how contributors and clinical workflows interpret context. It does not claim that a multi-country profile selector, regulatory service or every proposed capability is already implemented.

## Separate the relevant contexts

| Context | What it determines |
|---|---|
| Shared clinical core | Canonical syndrome modules, source-specific recommendations, deterministic calculations, procedures, education and evidence provenance. |
| Jurisdiction | Applicable national/regional guidance, product information, regulation, referral or emergency-service arrangements. |
| Organization | The selected organization's approved protocols, formulary, preparations, equipment, personnel and transfer arrangements. |
| Care setting | Relevant resources and workflows for the actual setting, such as prehospital care, emergency department, critical care, outpatient care or remote/resource-limited care. Coverage must be stated per implemented module. |
| Language and presentation | The user's chosen language, terminology and clearly labelled units. Language does not select a country, drug product or clinical protocol. |

Do not infer a clinical jurisdiction from the owner's biography, interface language, geographic metadata, a past hospital example or the country in which a source was published. A cited UK, European, US or other national source retains its provenance and applicability limits; citing it does not make that country the patient's setting.

## Select only the context needed for the task

- Use an explicitly selected jurisdiction, organization and care setting when provided. Treat absent information as unknown, not as Portugal/Horta or as confirmation that every resource is available.
- For general knowledge, education, evidence comparison and development, continue with the shared core and clearly attributed sources. A missing institutional profile does not suspend these capabilities or block unrelated modules.
- For an operational recommendation that depends on a particular product, resource, legal pathway or institutional standard, identify the missing dependency and limit only the affected action or output until it is resolved. Existing clinical safety gates remain applicable.
- For medication arithmetic, preserve source-specific indication, population and dose limits. A verified exact concentration remains necessary for a volume or pump-rate output; international scope does not authorize guessing a preparation.
- Ask for jurisdiction or organization only when it materially changes the requested result. Do not delay urgent stabilization while retrieving profile documents.

## Evidence and reconciliation

Record the source, version/date, verification date, population, indication, jurisdiction and material limitations relevant to each recommendation. Compare current international/specialty evidence with the applicable national guidance and, for operational use, the selected organization's protocol. Preserve disagreements and their provenance; do not average incompatible thresholds, combine different regimens or silently turn one institution's convention into a universal rule.

Verify product-specific information and regulatory or safety claims against the applicable authoritative sources. Distinguish authorization, marketing/supply status, confirmed local stock and the actual product/preparation selected. An official foreign label can support an explicitly attributed reference; it does not certify authorization or availability elsewhere.

Existing canonical modules and calculators remain shared. Attach jurisdiction or organizational applicability to their references/configuration rather than duplicating an entire clinical module for each hospital. A profile-specific exception must identify its scope and review basis.

## Validation and continuity

Keep technical QA, evidence review, clinical validation and operational readiness distinct. A local acceptance or product verification applies to its documented scope and does not certify every country or organization. Conversely, an unresolved local deployment dependency does not by itself invalidate unrelated shared clinical content or educational use.

This change of scope does not promote evidence states, resolve blocked medication contracts or alter doses, formulas, contraindications or clinical release status. Record capability coverage accurately as implemented, candidate or planned. Preserve historical local decisions and audits as traceable records under their original context.

For care in Portugal or explicitly requested Portuguese alignment, use [the Portugal profile](portugal-context.md). Other jurisdictions require their applicable sources and explicit context; absence of a dedicated profile is not evidence of conformity or a reason to default to Portugal.
