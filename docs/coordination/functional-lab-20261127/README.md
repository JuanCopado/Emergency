# Functional local laboratory — 2026-11-27

Base: international receiver fa2381dcfe77253f575ac843860b3167125f1e1e (PR127 merged with explicit owner authorization). This candidate is a separate task branch; no deployment or new clinical approval.

- RAG: real extraction from two own governance documents plus separate invented fixtures, with pinned citations, versions, integrity, source expiry and abstention. It is not clinical primary evidence retrieval. Document text remains untrusted data; no model, tools, network or prescribing. Full indexes and quoted-output artifacts remain local.
- Interchange: closed local FHIR R4 4.0.1 Bundle/Observation, HL7 v2.5.1 ORU to FHIR/ACK, DICOM P10 registered procedural phantom to PNG/static HTML. No hospital connector, listener, general PACS or conformance claim.
- Dermatology: 24 purpose records/23 cases, 13 local preparations, nine specific privacy/context gaps and two excluded faces. Zero media admitted to product/repository. Build/development gates reject the26 known exact hashes and reserved namespace; this is not proof of anonymity for unknown/transformed files.
- Measurement: interoperability sources/tests added to Sonar's explicit source/test classification and existing Python coverage via a test-suite bridge. No gate, threshold or executable-source exclusion weakened. The new Vitest .test.mjs is classified as a test, not product code.

Observed local checks: RAG16 new content tests plus13 provenance regressions PASS; interop29 PASS through the existing QA bridge; dermatology15 Node lifecycle tests plus9 Vitest contracts PASS. DICOM PNG decoded by Windows WPF (4096 pixels/zero mismatch) and viewer opened in Edge. Full remote CI and independent audit must be recorded for the published candidate SHA; earlier PR127 checks are not transferred.

Evidence and receipts: https://drive.google.com/drive/folders/1DUeujW5m2tVRiJxzg4mk1I4mOyAy86ah
Clinical state: CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
Existing19 accepted contracts,45 formulas and MED-DEC-R46-01/02 retain their scope. Insulin original remains unidentified. No new last_checked or clinical status promotion.
