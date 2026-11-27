# Ejecución focal CARDIO — 27/11/2026

Base PR126 `a606a442c071b3f84c17b43f45704ae62d30d44a`, árbol `9d7bfd58cca76b968eee1ec3ee7a411c87a3d274`. Rama aislada; sin modificar main, ramas protegidas, matriz de Work, Drive ni documentos centrales. Sin merge ni despliegue.

Se recuperaron las seis propuestas originales y la aceptación literal ya acreditada. Los hashes de ambos textos íntegros coinciden con los recibos previos: `2d4d303c835779143d126b31917060e403f5aa7f1b5d86d5aef60b401ceaa036` y `10f5dcb68a6e02cae4341d3996fc95348befd305af9603a6627506bba21647ec`. Asociación de mensajes y límites de timestamp en `IMPLEMENTATION_RECEIPT.json`; procedencia previa en `closure-residual-20261127/science/SCIENCE_CARDIO_TRACE.json`. No se pidieron nuevas aprobaciones. Los problemas previos eran de trazabilidad del expediente, no ausencia de aceptación médica.

| ID | Estado y ejecución | Pendiente real |
|---|---|---|
| MED-RES-CARDIO-01 v1 | Añadida monitorización estructurada al selector existente: arritmia con pulso, parada, ROSC y pediatría. Preserva ETCO₂, excepción pediátrica y cuatro rutas manuales. | Sin algoritmo ROSC nuevo ni cambio de dosis/energías. Cada destino conserva estado. |
| MED-RES-CARDIO-02 v1 | Cinco ramas existentes preservadas, sin cambios. | No reabrir ni añadir otro algoritmo. |
| MED-RES-CARDIO-03 v1 | Alcance ya presente en `cardiovascular.md`, sección `device-complications`: captura/perfusión, descargas/imán condicionado, infección y dispositivo de asistencia. | No duplicar módulo ni ampliar tratamiento. |
| MED-RES-CARDIO-04 v1 | Fase estable ya implementada preservada. | No añadir una fase 24–48 h ni mezclar objetivos de fuentes distintas. |
| MED-RES-CARDIO-05 v1 | Tres identidades PT documentales añadidas con registro, fuente, versión, localizador y límites; las referencias US/ES permanecen intactas. Gtn incluye advertencia sobre discrepancia de §§4.2/4.3. | Todos los perfiles siguen no operativos. Vigencia nacional/stock no verificados. Producto original de labetalol SIN IDENTIFICAR. Cuatro genéricos sin ficha PT suficiente. |
| MED-RES-CARDIO-06 v1 | Cinco rutas etiológicas conservadas; añadido acceso auxiliar manual `observation-discharge`, separado de las causas y sin autorizar alta. | Las tres causas sin ID propio se evalúan en el módulo actual. Nuevas pautas requieren evidencia primaria concreta, no se inventan destinos. |

## CARDIO06: comparación por causa

SCA → `acute-coronary-syndrome`; disección → `acute-aortic-syndrome`; TEP → `pulmonary-embolism`; neumotórax **a tensión** → `tension-pneumothorax` / procedimiento único `PROC-THX-001`; taponamiento → `cardiac-tamponade-pericardial-emergency` / procedimiento único `PROC-CV-006` (`PROC-US-007` es referencia cruzada).

Miocarditis/pericarditis: sin módulo etiológico independiente acreditado; evaluación inicial y escalada por riesgo ya están en `non-coronary-chest-pain`. Taponamiento no sustituye la evaluación de toda miopericarditis. Una pauta farmacológica nueva necesitaría cotejo focal ESC2025 por afirmación; el recibo de revisión de 14/11 no acredita revisión farmacológica completa.

Rotura esofágica: ya se exige evaluación quirúrgica/torácica urgente y planificación de control del foco, sin ID independiente. No se inventa pauta de antibióticos, imagen o instrumentación. `acute-abdomen` no es sustituto automático.

Causas musculoesqueléticas/digestivas: diferencial y reevaluación existentes; sin ruta universal. El módulo `acute-musculoskeletal-pain` tiene población/lesiones elegibles delimitadas y no debe aplicarse automáticamente a toda pared torácica; `acute-abdomen` tampoco equivale a reflujo. La ausencia de un ID independiente no obliga a duplicar módulos ni significa falta de aprobación de las seis propuestas estructurales.

## QA y conservación

Antes del cambio: 10 regresiones nuevas fallaron y 44 existentes pasaron. Después: 62/62 pruebas focales PASS, incluidos positivos y negativos en ambas vistas y comprobación de traducciones. Build TypeScript/Vite PASS. ESLint focal PASS. Navegador real Linux Chromium: ocho casos móviles ES/PT-PT/EN/ZH × `/clinical`/`/guides`, monitorización, cuatro algoritmos, navegación manual auxiliar, tres identidades PT y cuatro genéricos desconocidos, sin controles de administración ni desbordamiento. Recibo `CARDIO_BROWSER_QA.json`; capturas sintéticas locales en `/workspace/nextphase-cardio-browser`.

Los 131 módulos canónicos generados son idénticos a la base. No cambian recomendaciones, números, estados, fuentes heredadas ni `last_checked`. Se preservan CARDIO02/04 con hashes de sección/preámbulo en el recibo, las 23 aprobaciones dermatológicas, la aceptación Clinical Minimal, los 19 contratos aceptados, 45 fórmulas y MED46. Insulina SIN IDENTIFICAR.

Revisión interna focal de solo lectura: sin defectos accionables ni exceso clínico detectado. No comprobó externamente las fuentes PT y no constituye auditoría independiente. Antigravity de PR126 sigue bajo coordinación de Work, sin duplicación. Esta entrega necesita su propio cotejo del diff final por ese canal.

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**.
