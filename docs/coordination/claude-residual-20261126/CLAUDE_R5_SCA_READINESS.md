# R5-1 · R5-2 · cohorte silenciosa SCA · preparación técnica · 26/11/2026

CLINICALLY_PENDING. R5-1 (P1) abierto, R5-2 pendiente. No se inició ningún estudio con pacientes, no hay corpus real en el repositorio, no se adjudicó nada, no se cambió el filtro ni ninguna regla.

## Cambio ejecutado (commit `5746d3dd103d7d66e9e4fb1ee8d6b35ed4237dd2`)
Herramientas del corpus ciego R5-2: `clinical/scripts/blind_corpus_tools.py`.
- Defecto demostrado: la herramienta aceptaba `--primary ana ana` (acuerdo trivial) y un desempate igual a un primario, y no comprobaba separación de roles.
- Corrección: dos primarios distintos; desempate distinto de ambos; función y subcomando `roles` (autor, evaluador, custodio, adjudicador): ninguna persona con dos roles, mínimo tres adjudicadores; `agreement` con `roles` rechaza jueces fuera del rol de adjudicador.
- Sigue sin acceso a archivos (entrada y salida estándar), sin texto de corpus y sin etiquetas de ingeniería.
- Pruebas: `clinical/tests/test_r12_blind_corpus_tools.py` 20/20 PASS (5 nuevas, datos sintéticos). Comprobado: contra la versión anterior de la herramienta (`87a17301`) fallan las 5 nuevas (2 fallos y 3 errores); con la corrección, 20/20.

## Estado de R5-2 (corpus textual ciego)
| Componente | Estado |
|---|---|
| Manifiesto, paquetes sin etiquetas, validación de adjudicaciones, kappa, regla de etiqueta final | Implementado y probado |
| Separación autores/evaluadores/custodios/adjudicadores | Implementado ahora (herramienta). La asignación de personas es decisión del propietario |
| Corpus independiente | AUSENTE por diseño (una prueba falla si el repositorio contiene corpus) |
| Evaluación reproducible con datos sintéticos | Las pruebas usan `placeholder_corpus`; no mide rendimiento clínico |

## Cohorte silenciosa SCA
- Es un ensayo offline sintético (`clinical/qa/R5_NOTE_SHADOW_EXTENSION_20261121.md`): 153 casos, 7/153 marcas, sin marca en producto.
- **Brecha de infraestructura:** el ejecutable `run_r5_note_shadow_study.py` es un artefacto externo, no está en el repositorio. Su integración agotó 90 s en CI con cobertura y 240 s en Windows (conservado en el expediente). Por tanto la reproducción desde el repositorio solo es posible con ese artefacto externo. Su SHA-256 declarado (`study.json`): `1d219bdd7ef8ca8a3f4f0fca4ad464faac4987e4ad2a0a9691fb6e986f7de44b`. NO VERIFICADO aquí: el artefacto no estaba disponible.
- No existe infraestructura de cohorte prospectiva y no se creó. Hacerlo exige aprobación clínica y ética previas.

## Banco de imágenes (contexto)
STATE vigente: 10/30 archivos técnicos, 20 pendientes, 0/30 adjudicados. No se inventaron estímulos.

## Pendiente
Decisión del propietario sobre quiénes ocupan cada rol y sobre el custodio del corpus. Sin esas personas la herramienta no puede ejecutarse con datos reales.
