# Recibo final · decisiones del propietario

Candidato PR122: `94a983b9580d4ba3f77161590eabd147cc9147aa`. Árbol `2111920882405a51c72af01c0420c8c6930ebba1`. Base `2058e97179ae793914dcd016e4fd033395dbc3e2`.
Checkout CI de PR: `959836d97f66a9dbf818b6d36d34ba9ee9c60513`, árbol idéntico al candidato. Rama de evidencia separada; no se modifica el SHA auditado.

| Workflow del candidato | Recibo | Resultado |
|---|---|---|
| App UI QA | [45957550084](https://github.com/JuanCopado/Emergency/actions/runs/45957550084) | success |
| Clinical QA | [45957550256](https://github.com/JuanCopado/Emergency/actions/runs/45957550256) | success |
| Security and quality | [45957550141](https://github.com/JuanCopado/Emergency/actions/runs/45957550141) | success |

QA local del SHA final: siete controles PASS, **1774 pruebas, 16 omitidas, cero fallos**. Incluye las 16 regresiones nuevas. CI clínica del SHA final: 1774 pruebas registradas, 20 omitidas y cero fallos; omisiones no contadas como pruebas ejecutadas. Frontend 1.118 pruebas y build PASS, ejecutados antes del último cambio del validador; código de app idéntico y verificado de nuevo por la CI UI del candidato. Normalización: 254 fuentes / 131 módulos; grafo determinista PASS. Jobs y checks completos en JSON adjuntos. Ejecuciones anteriores canceladas conservadas sin atribuirles resultados del SHA final.

GMA-P1-003 cerrado sólo en el alcance histórico español aprobado. CARDIO-01..06: SÍ conservado, seis comparaciones documentales; mensaje original de las 06:10:21 UTC pendiente de recuperación y asociación a la aceptación 06:12:33 UTC. Falta de trazabilidad, no de aprobación. No cambios clínicos sustantivos inferidos. 23 DERMA/24 fotografías inventariadas y Clinical Minimal preservados; privacidad/derechos e implementación visual tienen sus carriles separados.

Orden Antigravity publicada para recogida; recepción y dictamen de este candidato no observados. Revisión interna automatizada separada, sin adjudicación clínica humana independiente. Sin merge, despliegue ni modificación de ramas protegidas. **CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.**
