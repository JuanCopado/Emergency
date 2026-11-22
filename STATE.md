# STATE · correcciones de problemas actuales · 22/11/2026

Estado global: **CLINICALLY_PENDING**. Registro: **129 GREEN / 2 YELLOW / 0 RED**, 131 módulos.
Validador clínico final: Dr. Juan Copado Ceballos; Farmacia consultiva, según PR35.

**22/11 · correcciones actuales integradas.** [PR70](https://github.com/JuanCopado/Emergency/pull/70) integra doce correcciones en `e8de202d874c6db588d3561ff13859e5ee53c96d`; [PR71](https://github.com/JuanCopado/Emergency/pull/71) añade la publicación atómica de recibos C14 en `842e4a2864f7b746659504dd8ae53faaac3e58b2`. El [checklist](docs/coordination/CURRENT_DEFECTS_CHECKLIST_20261122.md) registra **13 puntos OK** y **C12 pendiente de acceso administrativo**. Clinical QA del último candidato: 1.205 pruebas, 14 omitidas; Security and quality de push/PR: seis jobs PASS en cada ejecución, incluido T05 Windows. La evidencia UI 947/947 corresponde a PR70/e8; PR71 no cambia la interfaz. El [recibo](docs/coordination/PR70_INTEGRACION_20261122.md) conserva el fallo de arranque posterior a PR70, su corrección, las pruebas y los límites del escáner. Se mantienen decisiones clínicas, procesos en construcción y CLINICALLY_PENDING; no se acredita una instalación asistencial.

Seguimiento de PR61, 21/11. [QA de PDF nativo y Narrador](clinical/qa/PR61_NATIVE_PDF_NARRATOR_QA_20261121.md) incorpora el informe R2 y el cotejo aportado por el usuario, con sus límites literales y evidencias verificadas. CLINICALLY_PENDING.

**R4, 21/11.** El [resumen de la nota, imágenes, impresión y G05](docs/coordination/R4_INTEGRACION_20261121.md) recoge los ensayos posteriores al corte PR54 y las limitaciones clínicas pendientes.

- [PR53 · nota](https://github.com/JuanCopado/Emergency/pull/53) integrada en `fc8d5da2`. [PR51 · piel y heridas](https://github.com/JuanCopado/Emergency/pull/51) integrada en `bbd53d42`, árbol `46e7a8ceb69758be0ec3d9423f365722083c723c`.
- En `8179853e`, de árbol idéntico al merge de PR51, [9/9 checks aprobados](https://github.com/JuanCopado/Emergency/pull/51/checks). Sonar registró 87,2 % de cobertura nueva. Pasaron [853 pruebas de interfaz](https://github.com/JuanCopado/Emergency/actions/runs/44902659649) y [Clinical QA](https://github.com/JuanCopado/Emergency/actions/runs/44902659668) contabilizó 1.148 pruebas, 14 omitidas.
- [Recorrido Chromium del árbol integrado](https://github.com/JuanCopado/Emergency/actions/runs/44903275835): 12/12 comprobaciones sintéticas. En ese corte de PR51, impresión nativa y lector de pantalla estaban pendientes. La [QA posterior de PR61](clinical/qa/PR61_NATIVE_PDF_NARRATOR_QA_20261121.md) acredita un PDF nativo concreto y cinco cifras cotejadas; conserva límites de unidades/comparador y del recorrido gráfico completo. [Seguridad y calidad tras la fusión de PR51](https://github.com/JuanCopado/Emergency/actions/runs/44903396363).
- T05/T06 integrados mediante PR33; correcciones previas Sonar en PR34. Alcance: `clinical/qa/T05_T06_INTEGRATION_20261119.md`.
- PR48: accesibilidad y prototipo multimodal sintético E1; sin inferencia ciega ni validación diagnóstica.
- Gate de referencia revisado íntegramente y GREEN con la aceptación PR35 ya existente; no es autorización asistencial.
- Nota: corregidas fuentes de 18 síndromes y una referencia vasoactiva; 60 casos sin cambios fuera de procedencia.
- Nota: 60 casos conservados; negaciones, discriminantes y relaciones visibles. P1 de puntuación en notas mixtas y rendimiento clínico pendientes. Alcance: `clinical/qa/NOTE_OBSERVATIONS_20261121.md`.
- PR51/M10: normalización técnica de rasters, abstención y exclusión externa de PDF/DICOM. Alcance y controles en `clinical/qa/M10_TECHNICAL_FOLLOWUP_20261121.md`.
- Nueve fichas de imagen v1 aceptadas: «si claro que si», 20/11; GREEN de referencia con alcance y fuentes registrados.
- POCUS-MODE v1 aplicado exactamente; 12 pruebas de proyección, 4 de normalización y 2 del gate PASS; QA remota: checks del commit entregado.
- Aceptación: `clinical/qa/IMAGE_REFERENCE_OWNER_APPROVAL_20261120.md`; padres de imagen y nota YELLOW, rendimiento pendiente.
- ECG-PT v1 ya aceptado e integrado en PR47; cuatro flujos posteriores al merge PASS. Cola técnica conciliada.
- T05: revisión visual y trazabilidad FiO₂; extracción protegida solo Windows, bloqueo explícito en Linux.
- T06: R6/B1/Q4 se verificó con TLS sintético y backend Linux. G05 sigue abierto. Los proveedores públicos, las consultas libres y RAG quedan fuera del circuito verificado.
- Aplicación/launcher comunes; procesos y límites separados. Uso: `docs/LOCAL_REVIEW.md`.
- JSON estricto, protección no nulo→cero y fronteras HTTP/Host/Origin conservadas.
- SCORE-REF-20261120: 13 formularios aceptados, entrada manual o importación revisada y cálculo a petición médica.
- ARR-SELECTOR-20261120: cuatro circuitos manuales aceptados; ocho recorridos Chromium verificados en dos vistas.
- T02: once anotaciones aceptadas; escalas/fórmulas/PDF en PR41/44. Se conservan sus alcances y decisiones.
- Preservar los 46 IDs del catálogo y el alcance aceptado de los 19 contratos antes bloqueados; no restablecer bloqueos históricos ni repetir aceptación.
- `main`, RC1 y v1.43 reservados por las instrucciones de colaboración. Esto no acredita protección automática de GitHub: el 22/11/2026 la API devuelve `protected: false` para `main` y la rama internacional, sin rulesets. Sin GO_RELEASE ni exactitud prospectiva inferida de pruebas técnicas.

R4 · 21/11/2026 · Se verificó la presentación compartida de la fuente de farmacología aguda en ambos PDF. [Ensayo sintético de impresión](clinical/qa/R4_ACUTE_PRINT_MARKUP_20261121.md).

R4 · Seguimiento de formato e idioma en copia aislada. El conversor de farmacología reconoce el énfasis en prosa mixta y conserva los literales de código. La nota transmite el idioma de interfaz y localiza sus avisos automáticos. Los cálculos y estados de evidencia se conservan. Las comprobaciones del PDF nativo y de la entrega se registran en el expediente de seguimiento.

R5 · 21/11/2026 · [Consolidación técnica y límites](docs/coordination/R5_INTEGRACION_20261121.md). Estudio offline de 153 casos sin cambio clínico, corrección focal de presentación S8786 y auditorías reales Claude Code/Gemini. G05 global y QA gráfica nueva pendientes según expediente. CLINICALLY_PENDING, 129 GREEN / 2 YELLOW / 0 RED.

R6 · 21/11/2026 · [Consolidación y límites](docs/coordination/R6_INTEGRACION_20261121.md): avisos de calidad previos a interpretar, auditoría Claude Code, instrumento externo con 153 registros conservados y expedientes Gemini inactivos. [G05](docs/coordination/R6_G05_20261121.md) global BLOCKED. CLINICALLY_PENDING; 129 GREEN / 2 YELLOW / 0 RED. CI e integración final se registran por SHA en recibo separado.

R6 · 21/11/2026 · M10 N3/N2 técnico: errores del proveedor distinguidos (503/502/422) y procedencia manual tras abstención. CLINICALLY_PENDING, 129 GREEN / 2 YELLOW / 0 RED.

R6 · 21/11/2026 · M10 N4/N1b técnico: cota de segmentos JPEG/WebP y avisos categóricos de metadatos. CLINICALLY_PENDING, 129 GREEN / 2 YELLOW / 0 RED.

R7 · 21/11/2026 · M10 R5-2 técnico: normalización de codificación en el filtro de tranquilización; R5-1/R5-2 restantes en [ficha](clinical/qa/R7_M10_R5_RESIDUAL_FICHA_20261121.md), sin decisión médica aún. CLINICALLY_PENDING, 129 GREEN / 2 YELLOW / 0 RED.

R8 · 21/11/2026 · M10 R5-1 técnico de transparencia: categoría efectiva y origen visibles antes de interpretar; sin cambio de encaminamiento ni de criterios. CLINICALLY_PENDING, 129 GREEN / 2 YELLOW / 0 RED.

R8 · 21/11/2026 · M10 R5-1/R5-2: [contratos propuestos inactivos y corpus sintético](clinical/qa/R8_M10_R5_CONTRATOS_PROPUESTOS_20261121.md); decisiones DEC-CLIN-R7-03/06 pendientes. CLINICALLY_PENDING, 129 GREEN / 2 YELLOW / 0 RED.

R11 · 22/11/2026 · Nota clínica, conexión (técnico, sin cambio clínico): `postJson` distingue fallo de red y tiempo agotado (60 s; 200 s para la llamada al proveedor, por encima de su máximo de 180 s) de una respuesta del servidor, muestra mensajes localizados pt/es/en/zh sin el texto crudo del navegador, avisa de que una petición al proveedor pudo haber llegado y nunca reintenta. Un fallo de conexión no es un resultado clínico. No añade almacenamiento ni cambia la API local. Mensajes específicos para HEIC/HEIF y para fotografías por encima del límite técnico de ≈ 12,5 MP, sin reescalado automático ([medición](clinical/qa/R11_IMAGENES_HEIC_Y_GRANDES_20261122.md)). CLINICALLY_PENDING.

R10 · 22/11/2026 · M10 R5-1 Fase A (solo datos): `prepared.kind_assessment` registra categoría declarada, todas las pistas del nombre, sospechas técnicas y `modality_verification=not_verified`, dentro del token HMAC y sin llegar al proveedor; encaminamiento, confianza, salida clínica y abstenciones sin cambio (equivalencia probada). La modalidad real no se verifica (RGB, EXIF y la ausencia de DICOM no son prueba). El servidor distingue `other_image` explícito de la ausencia de categoría cuando recibe `explicit_kind`, pero la interfaz actual no envía «Outro» (`undefined`): un «Outro» elegido y el predeterminado siguen indistinguibles de extremo a extremo; cambio de interfaz posterior y separado, no incluido. Fase B, opciones 2A–2E y clasificación visual siguen pendientes de decisión médica. CLINICALLY_PENDING.

R11 · 22/11/2026 · Decisiones médicas registradas ([expediente](clinical/qa/R10_DECISION_MEDICA_FASE_A_B_20261122.md)): `DEC-CLIN-R10-FASE-A` SÍ (instrumentación técnica de R5-1 sin modificar resultados clínicos, con HMAC, equivalencia, CI y auditoría independiente) y `DEC-CLIN-R10-FASE-B` SÍ a mantenerla desactivada (solo prototipos inactivos hasta tener evidencia de falsos avisos y usabilidad). R5-1/R5-2 siguen abiertos; opciones 2A–2E, clasificación visual y regex nuevas no autorizadas. CLINICALLY_PENDING.

R10 · 22/11/2026 · PWA (técnico, sin cambio clínico): prueba `pwa:offline-check` con el service worker instalado y la conexión cortada (servidor detenido y navegador sin red) sobre las rutas locales y `/api/*`; reproduce que, sin red, una navegación a `/api/*` recibía el shell de la aplicación y lo corrige con `navigateFallbackDenylist` solo para `/api/`. Límites: Chromium en Linux; no sustituye dispositivos Android/iOS ni verifica HEIC. CLINICALLY_PENDING.

R11 · 22/11/2026 · Identidad de compilación en Windows (técnico, sin cambio clínico): `readBuildIdentity` fijaba `GIT_CONFIG_GLOBAL=os.devNull` (`\\.\nul`), que Git for Windows 2.56.1 rechaza (exit 128), y devolvía revisión desconocida en Windows; ahora usa `NUL` en Windows y mantiene el aislamiento (medido: solo se lee `.git/config`). Defecto previo, ajeno a PR74. CLINICALLY_PENDING.

R12 · 22/11/2026 · R5-2, corpus ciego independiente (DEC-CLIN-R8-06B: SÍ; ninguna regex nueva autorizada): [protocolo](clinical/qa/corpus/blind/PROTOCOL.md) y herramientas `clinical/scripts/blind_corpus_tools.py` (manifiesto de recuentos y hash, paquetes de adjudicación sin etiquetas, validación y concordancia). Aislamiento: las herramientas no acceden al sistema de archivos (solo entrada y salida estándar; prueba estructural), nada del corpus ni de las claves en el repositorio y ninguna herramienta importada por el producto o el filtro (pruebas). Tres lenguas base (es, pt, en) y cuatro estratos (es-ES, pt-PT, pt-BR, en); portugués conforme al AO90 conservando las diferencias terminológicas regionales. No se ha construido corpus ni designado adjudicadores; no cambia el filtro; R5-2 sigue abierto. CLINICALLY_PENDING.

R12 · 22/11/2026 · Contrato inactivo de Fase 1 (piel/heridas), enmienda 0.2 (DEC-CLIN-R8-03: SÍ, cinco estados): se añade `not_applicable` solo a `clinical/references/skin-wound-phase1-contract.proposed.json`, y solo con `premise_absent_confirmed=true` (ausencia confirmada de la premisa clínica del signo); las premisas de cada signo siguen pendientes de redacción médica. No conectado al producto; no modifica la salida actual, el filtro ni las abstenciones; Fase 2 bloqueada. CLINICALLY_PENDING.

R12 · 22/11/2026 · Decisiones médicas registradas ([expediente](clinical/qa/R12_DECISION_MEDICA_R8_20261122.md)): `DEC-CLIN-R8-06A` SÍ (política de seguridad en ocho capas, prototipos inactivos y pruebas sintéticas; la definición de las capas no consta en el repositorio y no se implementa), `DEC-CLIN-R8-06B` SÍ (corpus ciego R5-2 independiente; ninguna regex nueva) y `DEC-CLIN-R8-03` SÍ (cinco estados, «No aplicable» solo en el contrato inactivo; Fase 2 bloqueada). R5-1 (P1) y R5-2 siguen abiertos. CLINICALLY_PENDING.

R15 · 22/11/2026 · Contrato inactivo de Fase 1, enmienda 0.3 (DEC-CLIN-R14-02: SÍ, con precisión; [expediente](clinical/qa/R15_DECISION_MEDICA_R14_02_20261122.md)): `not_applicable` exige confirmación con procedencia verificable (`premise_confirmation_source`; un booleano aislado no vale), está prohibido para `necrotic_appearing_tissue` y en `visible_edge_separation` exige `wound_closure_history="never_closed"` (si falta: `uncertain`/`closure_history_unavailable`, sin inferir de la foto); sin texto libre. Solo `skin-wound-phase1-contract.proposed.json` y sus pruebas negativas por signo y estado; Fase 1 PROPOSED_INACTIVE, Fase 2 bloqueada, sin cambio de salida clínica. CLINICALLY_PENDING.
