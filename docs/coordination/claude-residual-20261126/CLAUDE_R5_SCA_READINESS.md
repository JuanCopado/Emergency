# R5-1 · R5-2 · cohorte silenciosa SCA · preparación técnica · 26/11/2026

CLINICALLY_PENDING. R5-1 (P1) abierto, R5-2 pendiente. No se inició ningún estudio con pacientes, no hay corpus real en el repositorio, no se adjudicó nada, no se cambió el filtro ni ninguna regla.

## Cambio ejecutado (commit `5746d3dd103d7d66e9e4fb1ee8d6b35ed4237dd2`)
Herramientas del corpus ciego R5-2: `clinical/scripts/blind_corpus_tools.py`.
- Defecto demostrado: la herramienta aceptaba `--primary ana ana` (acuerdo trivial) y un desempate igual a un primario, y no comprobaba separación de roles.
- Corrección: dos primarios distintos; desempate distinto de ambos; función y subcomando `roles` (autor, evaluador, custodio, adjudicador): ninguna persona con dos roles, mínimo tres adjudicadores; `agreement` con `roles` rechaza jueces fuera del rol de adjudicador.
- Sigue sin acceso a archivos (entrada y salida estándar), sin texto de corpus y sin etiquetas de ingeniería.
- Pruebas: `clinical/tests/test_r12_blind_corpus_tools.py` 20/20 PASS (5 nuevas, datos sintéticos). Comprobado: contra la versión anterior de la herramienta (`87a17301`) fallan las 5 nuevas (2 fallos y 3 errores); con la corrección, 20/20.

## Estado de R5-2 (corpus textual ciego)
Actualización de cierre coordinado: 26/26 pruebas focales con marcadores sintéticos PASS tras hacer obligatorio el manifiesto y sus paneles por idioma. Las 20 pruebas de PR119 anteriores se conservan como antecedente del commit indicado; los seis casos nuevos cubren la ausencia del manifiesto, alias de identidad, roles completos, compromiso del corpus, paneles distintos y conservación de estadísticas. No son resultados clínicos.

| Componente | Estado |
|---|---|
| Manifiesto, paquetes sin etiquetas, validación de adjudicaciones, kappa, regla de etiqueta final | Implementado y probado |
| Separación autores/evaluadores/custodios/adjudicadores | CLI `agreement` exige manifiesto ligado al corpus con IDs estables, referencias opacas del registro del custodio y panel por lengua. Solo acredita consistencia formal; personas, competencia e independencia se verifican fuera del software |
| Corpus independiente | AUSENTE por diseño (una prueba falla si el repositorio contiene corpus) |
| Evaluación reproducible con datos sintéticos | Las pruebas usan `placeholder_corpus`; no mide rendimiento clínico |

## Cohorte silenciosa SCA
- Es un ensayo offline sintético (`clinical/qa/R5_NOTE_SHADOW_EXTENSION_20261121.md`): 153 casos, 7/153 marcas, sin marca en producto.
- **Artefactos externos separados:** el ejecutable `run_r5_note_shadow_study.py` está recuperado localmente en `Downloads/Emergency-R5-20261121/evidencias/`, 10.858 bytes, SHA-256 `47255392cbdbe26f6ce7d92d0636be55b1f3d4b011a3d302be4854782c9e4445`. No está integrado en el repositorio y no se ha repetido el estudio en este corte. El hash `1d219bdd7ef8ca8a3f4f0fca4ad464faac4987e4ad2a0a9691fb6e986f7de44b` identifica `study.json`, no el ejecutable. Los límites históricos de 90 s en CI y 240 s en Windows se conservan; recuperar el archivo no acredita reproducción nueva ni validación prospectiva.
- No existe infraestructura de cohorte prospectiva y no se creó. Hacerlo exige aprobación clínica y ética previas.

## Banco de imágenes (contexto)
STATE vigente: 10/30 archivos técnicos, 20 pendientes, 0/30 adjudicados. No se inventaron estímulos.

## Pendiente
Designación de personas y custodio con verificación de identidad, competencias y conflictos; corpus real y estadística preespecificada. Son dependencias operativas, no adjudicaciones inventadas ni nueva aprobación clínica. El filtro tranquilizador R5-2 (cuatro estratos por siete clases) no sustituye la evaluación de notas clínicas con tres referencias independientes (aserción textual, prioridad t0 y diagnóstico final).
