# Solicitud de auditoría independiente · candidato PR115/PR116

Estado: PUBLISHED_FOR_COLLECTION_IN_PR118, autorizado por el propietario el 26/11/2026; recepción y dictamen no acreditados.

Auditar el HEAD exacto de `codex/pr115-pr116-integrated-20261126` publicado en la PR candidata y en el recibo final. No auditar solo la base `815afcd`, ni atribuir a este árbol los PASS antiguos de PR115/PR116.

1. Verificar SHA y árbol, padres de conciliación y `COMPOSITION_PROOF.json`: PR111 presente una sola vez; once archivos PR111, dos PR112 y diez PR113 byte-idénticos a PR115. Revisar los cuatro destinos PR114 adaptados.
2. Reproducir que el cliente rechaza JSON fallido después de HTTP200, conserva los errores de transporte y el status/código terapéutico. Los tres fallos RED y los recibos GREEN están separados.
3. Verificar revisión terapéutica real por API, HMAC, vigencia de fuente/contexto, privacidad, alergias y confirmaciones; exportación de notas históricas sin tratamiento y bloqueo de tratamiento sin revisión. Confirmaciones del harness son simuladas, nunca aceptación clínica.
4. Confirmar que las expectativas clínicas y los bancos fuente siguen intactos; que el JSON/PDF/Word contienen la misma pauta revisada y no dos tratamientos. Revisar 16 casos navegador, edición posterior y los negativos.
5. Comprobar el manifiesto histórico T06 y la adaptación exacta con el original congelado. No aceptar que retirar aserciones o reetiquetar hashes dé PASS.
6. Revisar la CI completa del mismo SHA: App UI, Clinical QA, seis combinaciones Picomatch, Semgrep, Trivy, T05 Windows, T06 Linux, cobertura y Sonar. Mantener los FAIL históricos y distinguir skipped/cancelled de success.
7. Mantener GMA-P1-003 abierto: perfil específico inactivo y discrepancia documental < frente a ≤. No adjudicar dosis/producto ni reabrir los 19 contratos aceptados.

Emitir hallazgos y dictamen independiente para ese SHA exacto. No fusionar, cambiar protecciones o desplegar durante la auditoría. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

El expediente anterior de Antigravity terminó por permisos antes de leer; no es un dictamen sobre este candidato. No se registra una nueva sesión o recepción sin prueba real del envío.
