# T01-R — revisión y desbloqueo controlado

**Resultados separados:** revisión del diff PASS técnico; PDF PASS; Clinical QA FAIL/BLOCKED. Integración de T01 no autorizada por estos resultados. CLINICALLY_PENDING.

## Identificación

Commit auditado: `ed9b983f0b77a49e049f512b57e31d0d0a7602e2`.
Base: `ada519ac2f8e31ce807f397319ce260724642756`.
Rama/worktree preservados: `codex/v144-t01-architecture-ci`, `/workspace/work/Emergency-T01`.
No merge, rebase, push, PR ni modificación de main, RC1 o v1.43. C01 permanece intacto en su worktree original.

## Fase 1 — auditoría del diff

Revisados los 25 archivos del commit y contrastado `docs/T01_IMPLEMENTATION_REPORT.md` con el diff y los logs. Inventario y hashes del commit: `DIFF_AUDIT.json`. Una revisión independiente confirma que no quedan defectos críticos/importantes demostrados en esa integración técnica; no constituye aprobación clínica.

- Las tres regresiones de procedencia quedan corregidas: no se colapsan títulos/versiones distintos por URL compartida; se conserva toda identidad canónica junto a los componentes históricos; se detecta el separador compuesto ` + `.
- Normalización 4/4, grafo 14/14, endurecimiento 5/5 y CI 8/8 pasan.
- Se conservan 131 módulos, 220 fuentes, 249 relaciones módulo-fuente, 363 nodos y 380 aristas. HIGH_RISK conserva sus 57 IDs.
- La afirmación histórica de T01 sobre texto PDF ausente se precisa en esta entrega: el texto estaba presente, pero las ligaduras impedían la comparación literal de su extracción. No se reescribe el informe histórico para ocultar el fallo.
- Los cuatro P1 originales siguen abiertos: GMA-P1-001, GMA-P1-002, GMA-P1-003, GMA-C-P1-001. Los 19 contratos bloqueados y sus expedientes no se alteran.

### Riesgo de las 77 identidades compuestas

El inventario `COMPOUND_IDENTITIES_PENDING.json` contiene los 77 source_id, títulos, módulos, procedencia y licencias. Afectan a 71 módulos: 69 identidades proceden del registro legado y 8 de metadatos históricos pendientes de verificación individual.

No se puede atribuir cada recomendación a cada componente por la existencia de una cita compuesta. Permanecen pendientes identidad individual, edición/fecha, vigencia, ámbito exacto de la recomendación, licencia y conciliación con productos/protocolos locales. Una URL compartida no demuestra identidad equivalente. Los componentes históricos no sustituyen una revisión actual. No dividir automáticamente, promover estados ni considerar estas referencias corpus RAG de producción aprobado. Los recuentos de fuentes no son recuentos de aprobaciones clínicas.

## Fase 2 — fallo PDF y corrección técnica

Se reprodujo el mismo fallo de `/clinical/airway-rsi` tanto en T01 como en una extracción limpia de app/ y clinical/ del SHA base, con las mismas dependencias y Chromium. Las copias se ejecutaron sin modificar la rama base.

Diagnóstico con PDF real:

- El DOM contenía íntegra la frase canónica que empieza `For oral liquid/drop formulations`.
- El PDF previo tenía dos páginas y contenía el texto; pypdf extraía `veriﬁed` con U+FB01 en vez de `verified`. En todo ese PDF aparecían ocho ligaduras U+FB01, una U+FB03 y una U+FB02.
- La comparación original elimina sólo espacios, por lo que correctamente no consideraba iguales esas secuencias Unicode.
- Una prueba de hipótesis inyectando únicamente CSS de impresión sin ligaduras hizo pasar las cuatro rutas.

Corrección: cinco líneas añadidas en `app/src/index.css`, dentro de `@media print`, para `.clinical-guide-sheet` y `.clinical-module-sheet`:

```css
font-variant-ligatures: none;
```

No se cambia contenido, dosis, layout de pantalla, formato A4, políticas de evidencia ni lógica del verificador. No se normalizan ligaduras ni se debilita la comparación para aceptar el PDF anterior. La regresión existente se observa RED antes y GREEN después, conservando su hash original y comprobando cada línea canónica y la no duplicación del preámbulo.

Tras recompilar, el verificador original pasa:

1. `/clinical/airway-rsi`
2. `/guides/airway-rsi`
3. `/guides/vf-pvt`
4. `/guides/clinical-scores-calculators`

El PDF diagnóstico posterior no contiene U+FB01/U+FB03/U+FB02 y extrae dos apariciones literales de `verified`. El alcance acreditado es Chromium instalado y pypdf del entorno; no equivale a probar todos los visores, navegadores o los 131 módulos impresos.

## Fase 3 — revisiones GREEN

Evaluación documental a 26/10/2026. El criterio vigente en `evidence-registry.json` es `high_risk_days=30`; el auditor bloquea si `age_days > 30`. Los tres registros conservan `last_checked=2026-09-14`: 42 días, 12 por encima de la ventana. Último día dentro de ventana: 14/10/2026; vencidos desde 15/10/2026.

| Módulo | Documento y versión registrados | Resultado de búsqueda documental |
|---|---|---|
| acute-ischemic-stroke | AHA/ASA acute ischemic stroke guideline, 2026 | El catálogo canónico no contiene URL/DOI ni fecha de publicación; no se encontró renovación profesional nominal/fechada del módulo completo. |
| acute-coronary-syndrome | ESC acute coronary syndromes guideline, 2023 | El catálogo canónico no contiene URL/DOI ni fecha de publicación; no se encontró renovación profesional nominal/fechada del módulo completo. |
| sepsis-shock | Surviving Sepsis Campaign adult guideline, 2026 | Existe componente histórico con fecha 02/10 y documentación de vasoactivos 29/09 y 02/10; no acredita renovación clínica completa y autorizada de sepsis-shock. |

Las versiones anteriores se transcriben del registro, sin acreditar su vigencia externa. No se ha realizado una nueva revisión clínica ni se ha confirmado una edición por inferencia. La ausencia de un acta en el repositorio no demuestra que no exista fuera de él.

Documentos contrastados: registro canónico, catálogo normalizado, `clinical/SOURCES.md`, updates de sepsis/vasoactivos, informes y colas de continuidad, `clinical/qa/HUMAN_REVIEW_TEMPLATE.md`, política de revisión final. Las colas profesionales relacionadas siguen solicitando revisor nominal y fecha. La documentación de sepsis señala además revisión UCI/farmacia y conciliación local pendientes. Las discrepancias documentales sobre acceso al texto completo requieren revisión profesional, no una renovación automática.

`GREEN_RENEWAL_DOSSIERS.json` prepara un expediente por módulo con entrada canónica, bundle/hash, fechas y cómputos, referencias, colas relacionadas y requisitos de revisión. Revisor, fecha profesional y decisión quedan vacíos. Se requiere: identificar profesional/especialidad, documento oficial exacto y evidencia retenida; revisar el módulo completo; conciliar fuentes y aplicabilidad local; registrar incertidumbres y decisión. Sólo después de autorización clínica expresa podría plantearse una actualización de metadatos y repetir los gates sin modificarlos.

## Fase 4 — validaciones e integridad

| Validación | Resultado observado |
|---|---|
| Diff original T01, 25 archivos, revisión independiente | PASS técnico |
| Normalización / grafo / endurecimiento / CI | 4/4, 14/14, 5/5, 8/8 PASS |
| Sintaxis GitHub Actions, actionlint 1.7.7 | PASS; shellcheck externo desactivado |
| PDF base limpia y T01 previo | FAIL reproducido |
| PDF con corrección, verificador original | 4/4 rutas PASS |
| Frontend global | 376/376 PASS en 10 archivos |
| Lint / typecheck / build | PASS |
| Clinical QA global | BLOCKED; 603 tests, 1 fallo; auditoría también falla |
| Integridad | 672/673 archivos del manifiesto original idénticos; única excepción autorizada: CSS de impresión |
| Código/textos canónicos, registro, módulos, contratos, expedientes y C01 | sin cambios |
| git diff --check | PASS |

La QA global se repitió como gate final tras la corrección técnica. Falla `test_skill.ModularCoreTests.test_all_declared_high_risk_modules_have_evidence_records` por los tres errores de caducidad del auditor; los otros 602 tests pasan. No se cambia esa prueba ni el auditor para ocultarlo. Los restantes checks de QA (integridad de módulos, procedencia de casos/imágenes, registro de fuentes de imagen y plantilla ciega) pasan.

`INTEGRITY_CHECK.json` documenta la única excepción técnica y sus hashes. El normalizador, catálogo, registro de evidencia, ficheros de módulo, contratos, criterios de caducidad, verificador PDF y los cuatro P1 permanecen inalterados respecto a T01. La base compartida y origin/main conservan sus referencias. Logs completos y PDFs diagnósticos locales en `/workspace/work/T01-R-evidence/`.

## Decisión

- **Revisión del diff: PASS técnico.**
- **PDF: PASS en el alcance probado.**
- **Clinical QA: FAIL/BLOCKED por renovación profesional pendiente.**
- **Integración de T01: BLOQUEADA.**

No integrar ni publicar. Preservar CLINICALLY_PENDING, los cuatro P1 abiertos y los 19 contratos bloqueados. La siguiente decisión corresponde a revisión profesional de los expedientes y autorización posterior, no a un ajuste técnico de fechas o estados.
