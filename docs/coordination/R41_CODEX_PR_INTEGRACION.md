# R41 · PR de integración limpia

Fecha: 24/11/2026.

- Rama: `codex/r41-pr89-clean-integration-20261124`.
- Receptor: `codex/v144-international-scope-20261116` @ `dcc48b3cc115a7de5f45e9a2a89d06673ba8fe15`.
- Commit de integración: `b5e8c1e1ec6226d4fca05d3fbc9f94a98776bfba`.
- PR: [PR99](https://github.com/JuanCopado/Emergency/pull/99).
- Sustituye técnicamente a PR89 sin modificarla ni forzar su historial.

## Alcance

1. Manifiesto de 30 posiciones con 10 archivos presentes y 20 ausentes.
2. Cinco blobs nuevos de PR89 y tres PDF históricos del receptor restaurados en R41.1.
3. Generador, verificador, auditoría externa, dry-run y fixtures focales.
4. Pruebas R25 y regresión de los 24 registros históricos contra los archivos y el manifiesto definitivo de `canonical-r27-v1.2`.
5. Informes R41 y fichas individuales.

## Exclusiones

- Sin cambios clínicos.
- Sin imágenes nuevas de heridas, Rx o POCUS.
- Sin sello `HF_ETAPA1_STIMULI_SHA256.txt`.
- Sin declaración 30/30.
- Sin reclutamiento ni `GO_RELEASE`.

## C12

- PR obligatoria: **PASS**.
- Sin force-push/borrado: **PASS**.
- Rama creada desde receptor vigente: **PASS**.
- Conversaciones: pendiente de la revisión de la PR.
- Checks Semgrep, Trivy, cobertura, T05, T06 y SonarQube: pendientes de CI.
- Ruleset remoto: `BLOCKED_ADMIN`; el proceso se aplica de forma disciplinaria, no se declara protección activa.
