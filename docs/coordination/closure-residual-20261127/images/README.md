# Imágenes y estímulos: cierre residual documental

Base: PR125 `54285f88c3901c63dff017ad0413593c0e0a8271`. Entrega de Codex; no es una nueva auditoría de Antigravity ni una adjudicación clínica humana. No modifica el candidato, los originales ni los manifiestos históricos.

Se generó un manifiesto por finalidad para los 24 activos/23 casos y una cola de las 20 posiciones canónicas pendientes, reutilizando los votos existentes. Nueve controles de consistencia pasan. Los 24 originales y los cinco candidatos de captura siguen presentes y sus tamaños coinciden con los recibos; no se recalcularon hashes de imágenes ni se abrieron píxeles. Los hashes anteriores siguen atribuidos a su auditor y alcance originales.

## Corrección material de licencia SCIN

Se recuperó la licencia primaria exacta del commit `b5a498233ef23b24c2f9fdb41b53e162c6eeb98d`; el addendum previo identifica el blob `b73abe395e1a01467c215f456fe1b95f80a12a49`. **No contiene una restricción de uso no comercial**. Debe corregirse la afirmación previa de que ocho imágenes SCIN tenían una cláusula NC. La pregunta por finalidad comercial no debe mantenerse como un bloqueo contractual NC. Las condiciones de atribución/licencia y no reidentificación sí permanecen; la privacidad se trata separadamente en §2(b)(1). Véase `SCIN_LICENSE_CORRECTION.json`.

Esto no admite automáticamente imágenes a un producto ni autoriza un estudio nuevo. Se mantienen la finalidad exacta, exposición/retención, revisión de privacidad y demás condiciones reales por uso. Los dos rostros CDC conservan su exclusión por el obstáculo documentado de consentimiento; las aprobaciones médicas de representatividad no se repiten. Consulta/desarrollo condicionado no equivale a autorización de publicación, entrenamiento o validación independiente.

## Veinte posiciones pendientes

| Posiciones | Cantidad | Dependencia material |
|---|---:|---|
| S1-01/S2-01 a S1-07/S2-07 | 14 | Adaptación metodológica al objetivo dermatológico. Existen 14 especificaciones DEV-DERM, no 14 imágenes ni reasignaciones canónicas; no reactivar heridas. |
| S1-10, S2-10, S1-11, S1-12 | 4 | Candidatos físicos condicionales presentes; observaciones de perspectiva, aviso de pantalla, moiré/realismo, detalle/reflejos y privacidad por resolver según ficha. |
| S2-11 | 1 | Nueva toma física para reducir moiré; una edición informática no acredita esa toma. |
| S2-12 | 1 | Fuente/panel, condición experimental sin derrame y permiso concreto incompletos; no inferirlos de otros paneles. |

La cola JSON identifica individualmente los 20 IDs, requisitos y expedientes existentes, disponibilidad material y próxima evidencia. No se puede producir evidencia auténtica de una nueva toma física desde estos archivos ni inventar el panel o los permisos de S2-12. Las especificaciones DEV-DERM siguen separadas del conjunto de validación, con parejas del mismo caso que no son independientes.

Resultado: **10/30 canónicos sin cambios, 20 pendientes, cero nuevos estímulos/imágenes, cero adjudicaciones**. La preparación documental ejecutable queda reconciliada. Los requisitos de captura/fuente/privacidad y evaluación independiente siguen abiertos de forma explícita; no se atribuye su cierre a este manifiesto.

Archivos: `ASSET_ADMISSIBILITY_BY_USE_24.json`, `PENDING_EXPERIMENTAL_SLOTS_20.json`, `SCIN_LICENSE_CORRECTION.json`, `VERIFICATION.json`. Reproducir con `python closure-residual-20261127/images/build_residual_manifest.py` desde la raíz del proyecto.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
