# PEDIATRIC HUMAN REVIEW READINESS — v1.36

Fecha: 02/10/2026.

## Objetivo
Cerrar la parte automatizable de Fase 4 sin atribuir al QA una revisión clínica humana que no ha ocurrido.

## Regla de promoción
Ningún módulo pediátrico high-risk pasa de yellow a green por tests, cobertura documental o revisión del modelo. Para promoverlo se requiere un registro humano completo usando `qa/HUMAN_REVIEW_TEMPLATE.md`.

## Paquete mínimo del revisor
Para cada módulo high-risk pediátrico:
1. confirmar indicación, exclusiones y población/edad;
2. confirmar dosis, máximos, energía, concentración y tiempo de administración cuando aplique;
3. confirmar discrepancias entre ERC/RCUK, AHA/AAP PALS, SSC pediátrica, NICE, HSE, PANDEM, SmPC y otras fuentes usadas;
4. confirmar que bolos y perfusiones no heredan concentraciones adultas;
5. confirmar que una concentración comercial no se convierte a mL sin seleccionar el producto/concentración real;
6. revisar límites de función renal/hepática, alergias, QT, interacciones y contraindicaciones cuando apliquen;
7. registrar decisión: approve / approve with limitations / reject.

## Estado
- QA automático: completado; no sustituye revisión humana.
- Cobertura de evidencia: completada para los 127 módulos.
- Pediatría: Horta-local no es requisito general de liberación; producto/SmPC sí debe respetarse cuando determine concentración o restricción.
- Gate pendiente de Fase 4: revisión humana pediatría/farmacia.
