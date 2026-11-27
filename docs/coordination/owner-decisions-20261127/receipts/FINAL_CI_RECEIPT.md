# Recibo final · decisiones del propietario

Candidato PR122: `a625267c2aea5b23e1d517d59251eb3d4924856f`. Árbol `cf01aba0df5143ee6093618de13cba73e8d37c18`. Base `2058e97179ae793914dcd016e4fd033395dbc3e2`.
Checkout CI de PR: `db9abbe5b04b00e0902cd3f1ed07c297278a0a57`, árbol idéntico al candidato. Rama de evidencia separada; no se modifica el SHA auditado.

| Workflow del candidato | Recibo | Resultado |
|---|---|---|
| App UI QA | [45959957750](https://github.com/JuanCopado/Emergency/actions/runs/45959957750) | success |
| Clinical QA | [45959957789](https://github.com/JuanCopado/Emergency/actions/runs/45959957789) | success |
| Security and quality | [45959957685](https://github.com/JuanCopado/Emergency/actions/runs/45959957685) | success |

Sonar: gate PASS, 89.4 % de cobertura nueva, 0.0 % de duplicación, 0 hallazgos nuevos, 0 hotspots; sin aceptar hallazgos ni cambiar reglas, umbrales o exclusiones.

QA local del SHA final: siete controles PASS, **1776 pruebas, 16 omitidas, cero fallos**. Incluye las 18 regresiones nuevas. CI clínica del SHA final: 1776 pruebas registradas, 20 omitidas y cero fallos; omisiones no contadas como pruebas ejecutadas. Frontend 1.118 pruebas y build PASS, ejecutados antes del último cambio del validador; código de app idéntico y verificado de nuevo por la CI UI del candidato. Normalización: 254 fuentes / 131 módulos; grafo determinista PASS. Jobs y checks completos en JSON adjuntos. Ejecuciones anteriores canceladas conservadas sin atribuirles resultados del SHA final.

Correcciones técnicas adicionales: procedencia íntegra tras checkout autocrlf y parser de tabla lineal que resuelve python:S8786 sin alterar aprobaciones. El hallazgo anterior se conserva en los recibos de `94a983b`; el gate final y sus métricas se atribuyen únicamente al nuevo SHA.

GMA-P1-003 cerrado sólo en el alcance histórico español aprobado. CARDIO-01..06: SÍ conservado, seis comparaciones documentales; mensaje original de las 06:10:21 UTC pendiente de recuperación y asociación a la aceptación 06:12:33 UTC. Falta de trazabilidad, no de aprobación. No cambios clínicos sustantivos inferidos. 23 DERMA/24 fotografías inventariadas y Clinical Minimal preservados; privacidad/derechos e implementación visual tienen sus carriles separados.

Orden Antigravity publicada para recogida; recepción y dictamen de este candidato no observados. Revisión interna automatizada separada, sin adjudicación clínica humana independiente. Sin merge, despliegue ni modificación de ramas protegidas. **CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.**
