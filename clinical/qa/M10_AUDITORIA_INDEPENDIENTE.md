# M10 · Auditoría independiente — `skin-wound-image` (piel y heridas desde imagen)

Tarea M10-IMAGE-VALIDATION-20261120 · 20/11/2026 · Estado clínico: **M10 sigue YELLOW; proyecto CLINICALLY_PENDING**. Este documento es QA técnico y revisión bibliográfica; **no es validación diagnóstica** ni cambia dosis, algoritmos, recomendaciones ni estados de evidencia.

## 1. Procedencia y alcance

| Dato | Valor |
|---|---|
| Rama de referencia | `codex/v144-international-scope-20261116` |
| SHA base verificado | `21defd4efc4f1b6d15ddb28c655772ca3e4b8a0c` (PR48) |
| Árbol base | `d4b2eba6048fe8b8731bb991ad126c8058a9755a` |
| Rama de trabajo | `claude/m10-image-validation-20261120` (worktree aislado; no se tocó `main`, RC1, v1.43, PR47/48/49 ni sus workflows) |
| ID del módulo | `skin-wound-image` (en `FOUR_YELLOW_REVIEW_20261120.md` figura como «10 · Piel y heridas»; `ESTADO_ACTUAL.md` lo numera 11) |
| Registro | `evidence-registry.json`: `status yellow`, `workflow v1.17; diagnostic performance not established`, `last_checked 2026-09-27` |
| Revisado | PR39 (`FOUR_YELLOW_REVIEW_20261120.md`: define la pregunta inicial y la lista de requisitos de evaluación, sin cohorte), `IMAGE_VALIDATION_POLICY.md`, `IMAGE_VALIDATION_ROADMAP_2026-11-14.md`, `IMAGE_EVIDENCE_FOLLOWUP_20261120.md` (no trata M10) |
| Trabajo ajeno no duplicado | PR48 (`clinical/scripts/multimodal/*`): valida medios del **banco multimodal**, ruta distinta de la subida de la nota clínica. PR47/PR49 no tocados |

## 2. Capacidades reales del software (separadas de lo que se afirma)

**Existe:** (a) texto de procedimiento `modules/image-modalities.md#skin-wound-image` (4 viñetas); (b) ruta de subida de la nota clínica: `ClinicalNote.tsx` → `clinical_note_api.prepare_upload` → `clinical_note_vision_adapter.invoke` → **proveedor externo HTTPS opcional**; (c) puertas de privacidad y aceptación por el médico.

**No existe:** ningún modelo, clasificador ni extractor de rasgos de piel/heridas en el repositorio. El «análisis» lo haría un proveedor configurable que **no está configurado** en el entorno (`ESTADO_ACTUAL.md`). Por tanto no hay sensibilidad, especificidad ni exactitud medibles aquí y **no se afirma ninguna**. Las pruebas de este expediente cubren higiene de entrada, privacidad y comportamiento seguro de la tubería con un proveedor simulado.

## 3. Evidencia científica (verificada en PubMed; solo resúmenes leídos)

| Ref. | Fuente | Qué respalda | Qué NO respalda |
|---|---|---|---|
| E1 | Freeman K et al., BMJ 2020;368:m127, [doi:10.1136/bmj.m127](https://doi.org/10.1136/bmj.m127) | Apps de cribado de lesiones por foto: estudios pequeños, mala calidad, altas tasas de imágenes no evaluables; «no pueden fiarse para detectar todos los melanomas»; rendimiento probablemente peor en uso real | Nada sobre heridas/infección; población de cáncer cutáneo |
| E2 | Chuchu N et al., Cochrane 2018, CD013193, [doi:10.1002/14651858.CD013193](https://doi.org/10.1002/14651858.CD013193) | Teledermatología: imágenes adquiridas por especialistas, aplicabilidad baja a atención primaria; evaluación remota tiende a recomendar más seguimiento que la presencial; sensibilidad variable para melanoma invasivo | Es lectura por dermatólogo de cáncer cutáneo, no IA ni urgencias |
| E3 | Daneshjou R et al., Sci Adv 2022;8:eabq6147, [doi:10.1126/sciadv.abq6147](https://doi.org/10.1126/sciadv.abq6147) | Modelos de IA dermatológica y dermatólogos rinden peor en tonos oscuros y enfermedades infrecuentes (conjunto DDI, confirmación patológica) | No cuantifica eritema/infección en urgencias |
| E4 | Benčević M et al., Comput Methods Programs Biomed 2024;245:108044, [doi:10.1016/j.cmpb.2024.108044](https://doi.org/10.1016/j.cmpb.2024.108044) | Sesgo por color de piel en segmentación de lesiones (correlación fuerte; mitigaciones habituales sin reducción significativa) | Segmentación, no diagnóstico |
| E5 | Tschandl P et al., Nat Med 2020;26:1229, [doi:10.1038/s41591-020-0942-0](https://doi.org/10.1038/s41591-020-0942-0) | Una IA defectuosa puede inducir a error a todos los niveles de experiencia | Una IA buena mejora la precisión: no aplicable sin IA validada |
| E6 | Stevens DL et al., IDSA 2014, CID 59:e10, [doi:10.1093/cid/ciu444](https://doi.org/10.1093/cid/ciu444) | La guía enfatiza la **habilidad clínica** en el diagnóstico rápido de infecciones de piel y partes blandas, incluida fascitis necrosante | Texto completo no leído aquí; no se extraen criterios |
| E7 | Sounderajah V et al., STARD-AI, Nat Med 2025;31:3283, [doi:10.1038/s41591-025-03953-8](https://doi.org/10.1038/s41591-025-03953-8) | Lista de reporte para estudios de exactitud con IA (conjuntos, índice, sesgo/equidad) | Cumplimentar la lista no sustituye el estudio |

Búsquedas sin resultado útil: eritema/celulitis en pieles oscuras (PubMed, 0 resultados); precisión de fotos móviles para infección de herida quirúrgica (2 resultados no pertinentes: un ECA de agentes comunitarios y un modelo térmico, sin lectura de fotos en color). **Lagunas declaradas:** no se verificó literatura primaria sobre exactitud de fotografías para celulitis/heridas agudas, fascitis necrosante visible en foto, lesiones no accidentales pediátricas ni calidad fotográfica de heridas (IWII, WUWHS, AAD). Sin texto completo, solo se usan las conclusiones de los resúmenes.

**Indicaciones de producto:** no existe en el repositorio una ficha de uso previsto, ni marcado/clasificación regulatoria del proveedor. Pendiente de definir antes de cualquier uso fuera de docencia (E1 cuestiona la protección regulatoria de apps con algoritmos).

**Conclusión de evidencia:** la bibliografía respalda las cautelas ya escritas en el módulo (no etiquetar benigno, no excluir necrosis por aspecto, límites por piel y luz) y exige abstención y denominadores explícitos. No respalda ninguna afirmación de rendimiento. No se emite decisión médica nueva (ver §8).

## 4. Hallazgos técnicos

Archivo:línea sobre SHA base `21defd4`. «Corregido» = corregido en esta rama y cubierto por prueba (T = grupo en `tests/test_m10_skin_wound_image_audit.py`).

| ID | Prio | Hallazgo | Archivo:línea (base) | Reproducción | Impacto | Estado |
|---|---|---|---|---|---|---|
| F01 | P1 | `skin_wound` inalcanzable: la inferencia nunca lo devuelve y la UI no ofrece el tipo; una foto de herida acaba en `other-clinical-image` y **no carga `skin-wound-image`** | `clinical_note_api.py:101-124`; `ClinicalNote.tsx:35,38-40,172-181` | `prepare_upload('herida.jpg',…)` → `kind=other_image`, `modules=['other-clinical-image']` (T4) | Las salvaguardas del módulo no se aplican en el flujo real | Corregido |
| F02 | P1 | Sin validación de contenido: solo base64, no vacío y tamaño; un PNG de 8 bytes de cabecera, un ejecutable renombrado `.png`, texto `.jpg` o PNG truncado/CRC roto se aceptan y se enrutarían al proveedor. Los tests existentes usaban PNG falsos | `clinical_note_api.py:127-138,167-218`; `test_skill.py:5727,5746,5774…` | T1 (14 casos) falla 14/14 en base | Entradas corruptas o hostiles llegan a terceros; falsa apariencia de «imagen válida» | Corregido (`image_upload_guard.py`) |
| F03 | P1 | Metadatos no tratados: EXIF/GPS/XMP/comentarios/chunks de texto/datos tras EOF viajan al proveedor; el cribado de privacidad solo mira nombre de archivo y texto | `clinical_note_api.py:172-176`; `clinical_note_vision_adapter.py:87-109` | JPEG con GPS y comentario con nombre: el proveedor recibía el original (T7) | Fuga de ubicación/identidad | Corregido para PNG/JPEG/WebP (se conserva Orientation). **DICOM/PDF: no se inspeccionan ni limpian → F03b abierto (P2)** |
| F04 | P2 | Revisión de identificadores incrustados no exigida para `skin_wound`, `blood_gas_image`, `ophthalmology` ni binarios sin tipo | `clinical_note_api.py:178-181` | `prepare_upload(…, explicit_kind='skin_wound')` → `burned_in_identifier_review_required=False` | Rostro/tatuaje/pulsera sin revisión humana | Corregido (todo binario) |
| F05 | P2 | Abstención indistinguible de fallo: el contrato solo admite `status=ok` con contenido; abstención del proveedor = excepción genérica | `clinical_note_vision_adapter.py:115-116,130-131` | respuesta `status:'abstain'` → `VisionAdapterError` | UX confusa; riesgo de reintentos hasta obtener texto | Corregido (extensión aditiva del contrato 1.0; **requiere soporte del proveedor**) |
| F06 | P1 | Sin salvaguarda de salida contra falsa tranquilidad: texto «benigno / sin infección / descartado» y `confidence:high` pasan tal cual | `clinical_note_vision_adapter.py:119-121,143` | respuesta con «Benign lesion, no signs of infection», `high` (T6) | Contradice el módulo («no etiquetar benigno…»); riesgo de falsa tranquilidad | Corregido para `skin_wound`: marca + limitación visible + confianza retirada. Techo: regex (ver §6) |
| F07 | P2 | Sin puerta de calidad antes del proveedor: 32×32 px o imagen uniforme se envían | `clinical_note_api.py:222-243` | T2/T3 | Coste, interpretación sobre nada | Corregido parcialmente: resolución y PNG uniforme; **desenfoque, exposición, deslumbramiento, escala, JPEG/WebP uniformes no evaluados (abierto, P2)** |
| F08 | P2 | `mime_type` del cliente se guarda y reenvía sin validar contra el contenido | `clinical_note_api.py:193`; `vision_adapter:105` | `image/png; charset=evil` (T7) | Contrabando de metadatos al proveedor, confusión de tipo | Corregido (MIME canónico por firma) |
| F09 | P2 | `inferKind` de la UI usa subcadenas sueltas (`/ct\|tc\|mri\|rm\|tac/` casa «informe», «doctor») y su resultado **sobrescribe** la inferencia del servidor | `ClinicalNote.tsx:172-181,190` | por inspección; no ejecutado en navegador | Mala ruta a otro módulo | **Abierto** (solo se antepuso piel/herida) |
| F10 | P2 | Salida estructurada sin imponer: `references/image-output-schema.json` (calidad `non_diagnostic`, `not_assessable`, urgencia) solo aparece en documentación generada; el adaptador acepta texto libre | `image-output-schema.json`; ninguna referencia en código | `grep` | La abstención por calidad depende de texto libre | **Abierto** (decisión de diseño) |
| F11 | P3 | Precedencia por nombre de archivo (`herida_ecg.png` → `ecg`) | `clinical_note_api.py:106-124` | T4 | Ruta por orden de palabras, no por contenido | Documentado (el `explicit_kind` manda) |
| F12 | P2 | UI no mostraba abstención ni marcas de seguridad (panel solo para `vision_interpreted`; botón solo para `routed_external`) | `ClinicalNote.tsx:352-353`; `types.ts:160` | por inspección | El usuario no ve por qué no hay lectura | Corregido (alerta `role="alert"`, i18n es/pt/en/zh); **sin verificación en navegador real** |
| F13 | P2 | Texto clínico: el módulo cita luz y tono pero no menciona calidad mínima de foto, solicitud de nueva imagen/exploración como salida por defecto, heridas (tunelización, socavamiento), ni la peor discriminación en pieles oscuras (E3/E4) | `image-modalities.md:79-90` | revisión | Lagunas, no contradicciones | **No modificado** (contenido clínico; ver §8) |
| F14 | P3 | Cabecera de petición al proveedor: `invoke` sin verificación de certificado propia más allá del contexto por defecto; redirecciones bloqueadas, HTTPS exigido, respuesta acotada a 2 MiB | `vision_adapter:147-196` | T7 (`http://` rechazado) | — | Sin defecto |

Controles ya correctos (verificados): HTTPS obligatorio, redirecciones prohibidas, tope de respuesta 2 MiB, nombre de archivo saneado a `clinical-source.<ext>`, SHA-256 y tamaño ligados al preparado con HMAC, barrera de privacidad en la salida del proveedor (bloquea SNS/identificadores), `official_report` prohibido para imágenes, el original no se retiene, aceptación explícita del médico antes de persistir.

## 5. Pruebas (Fase 4)

`clinical/tests/test_m10_skin_wound_image_audit.py`, **48 pruebas sintéticas, 48/48 PASS**; **39/48 fallan contra el código base** (reproducen F01-F08). Informe reproducible: `M10_RESULTADOS_PRUEBAS.json`.

| Grupo | Requisito | Pruebas |
|---|---|---|
| T1 | Imagen inválida o corrupta | 14 |
| T2 | Calidad insuficiente | 2 |
| T3 | Sin contenido visual útil | 3 |
| T4 | Entradas ambiguas | 4 |
| T5 | Error y abstención | 7 |
| T6 | Sin afirmaciones no respaldadas | 7 |
| T7 | Integridad y privacidad | 11 |

Datos: PNG decodificables generados por script; JPEG/WebP son **contenedores estructurales** no decodificables. Sin imágenes de pacientes. **Estas pruebas no son validación diagnóstica.**

Regresión: suite `clinical/tests` (venv con `requirements-test.txt`): antes 1067 ejecutadas, 9 fallos + 40 errores; después 1115, idéntico conjunto de 49 (preexistentes, entorno Windows/codificación). `validate_modules.py` PASS (131). App: `tsc -b --noEmit` limpio; `ui`, `locale-safety`, `clinical-note-export-integrity` 47/47.

## 6. Limitaciones

1. Ningún proveedor real probado: contrato simulado. La abstención `status:'abstain'` y la retirada de confianza requieren aceptación del contrato por el proveedor.
2. El guard es estructural y de pila estándar: no decodifica JPEG/WebP; no mide desenfoque/exposición/escala; la detección de «sin contenido» solo existe para PNG 8 bits sin entrelazado (≤8 valores de byte distintos). Umbrales 64/224 px son pisos técnicos arbitrarios, **no estándares clínicos**.
3. El filtro de «tranquilización» es una regex es/pt/en: sobre-marca formas negadas («cannot be excluded») y no detecta paráfrasis. Marca, no bloquea.
4. Resistencia a inyección visual (texto dentro de la imagen) **no medida**: depende del proveedor.
5. Accesibilidad y UX: revisión estática y pruebas de componentes; **sin navegador real ni lector de pantalla**.
6. Sin texto completo de las fuentes; sin literatura primaria sobre foto-diagnóstico de infección aguda de piel/heridas.
7. Árbol de trabajo con cambios sin commit al generar el JSON (SHA base, no del delta); ver hashes de archivos en el JSON.

## 7. Decisiones de producto incluidas (no clínicas, reversibles)

Para conocimiento del médico propietario: (i) la confianza del proveedor se **oculta** (`confidence=null`, original en `provider_confidence`) en `skin_wound`; (ii) se añaden dos limitaciones fijas copiadas del texto del módulo; (iii) imágenes <64 px o PNG uniformes → abstención sin llamada al proveedor. No alteran guías ni estado de evidencia.

## 8. Decisión médica

**No se emite `M10_DECISION_MEDICA.md`.** La única propuesta clínica candidata (F13: ampliar el módulo con calidad mínima fotográfica, abstención por defecto y limitación en pieles oscuras) cuenta con E3/E4 como respaldo de resumen, pero no con fuente primaria vigente para la parte de «eritema menos visible» ni para calidad fotográfica de heridas. Según `AGENTS.md`, se documenta el límite en lugar de pedir decisión. Se retomará cuando exista lectura de texto completo de IWII/WUWHS o estudio de foto-diagnóstico de celulitis.
