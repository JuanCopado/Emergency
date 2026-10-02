# MIMIC-CXR-JPG 2.1.0 — MANUALLY CURATED TEST PROTOCOL v1.0

Fecha de congelación: 02/10/2026.

## Acceso y licencia
- PhysioNet credentialed access.
- PhysioNet Credentialed Health Data License 1.5.0 + DUA 1.5.0.
- CITI Data or Specimens Only Research requerido.
- No compartir datos; no reidentificación; mantener imágenes fuera del repositorio.

## Referencia
Usar únicamente mimic-cxr-2.1.0-test-set-labeled.csv para blinded_accuracy.
Este archivo contiene etiquetas manualmente curadas del test set usadas para evaluar CheXpert/NegBio.
Las etiquetas automáticas CheXpert/NegBio del resto del dataset NO son referencia experta.

## Target
Un target por dataset. Solo valores explícitos 1.0 vs 0.0 entran en la evaluación binaria.
Valores -1.0 (uncertain) y blank quedan excluidos por regla preespecificada antes del cegamiento.

## Límite de referencia
La referencia es human-curated test labeling, no majority multi-reader adjudication. Tratar los resultados como benchmark exploratorio de menor jerarquía que CheXpert expert-test/RSNA multi-reader.

## Unidad
study_id, agrupando todas las imágenes del estudio y manteniendo subject_id unido entre shards.

## Cegamiento
Separar imágenes/manifiesto de labels; congelar predicción antes de reveal; nunca subir datos restringidos al repo.
