# CHEXPERT EXPERT TEST — BLINDED CXR PROTOCOL v1.0

Fecha de congelación: 02/10/2026.

## Cohorte permitida
Solo el test set experto de CheXpert: 500 estudios de 500 pacientes no vistos.

## Referencia
- 8 radiólogos board-certified anotaron cada estudio.
- Ground truth: majority vote de 5 radiólogos.
- Los 3 radiólogos restantes se reservaron para benchmark humano.
- No usar las etiquetas del training set derivadas automáticamente de informes como referencia experta de blinded_accuracy.

Fuentes:
- https://stanfordmlgroup.github.io/competitions/chexpert/
- https://github.com/rajpurkarlab/cheXpert-test-set-labels

## Targets
Un dataset independiente por target. Targets inicialmente permitidos:
- Atelectasis
- Cardiomegaly
- Consolidation
- Edema
- Pleural Effusion

No mezclar targets en una sola métrica primaria.

## Unidad
- Estudio/paciente como unidad de agrupación.
- Si un estudio contiene múltiples vistas, todas permanecen juntas.
- La predicción primaria se emite a nivel de estudio.

## Cegamiento
1. Ingestar únicamente imágenes del test set experto y groundtruth oficial.
2. Hash de paciente/estudio.
3. Separar imagen/manifiesto ciego del groundtruth.
4. Congelar predicción por estudio.
5. Revelar majority-vote groundtruth solo después del freeze.

## Gate legal
La referencia y el aislamiento de labels están preespecificados, pero el intake real permanece bloqueado hasta verificar y documentar los términos/licencia aplicables al download actual de Stanford AIMI/Redivis. La política general AIMI de uso no comercial no sustituye la revisión del acuerdo específico presentado al descargar.

## Límites
- Dataset público histórico: posible exposición previa del modelo.
- Benchmark retrospectivo, no validación prospectiva.
- No promover módulos a green por el resultado.
