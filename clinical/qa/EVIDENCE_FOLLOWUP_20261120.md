# Continuidad T05/T06 y evidencia pendiente · 20/11/2026

**Actualización posterior (20/11/2026):** la corrección puntual ECG-PT-20261120 v1 fue aprobada expresamente y aplicada a la rama de desarrollo internacional. Ver [ECG_PT_OWNER_APPROVAL_20261120.md](ECG_PT_OWNER_APPROVAL_20261120.md). El estado previo de propuesta pendiente descrito abajo se conserva como antecedente; las ocho revisiones integrales no se consideran completadas.

## Resultado y alcance

La revisión parte del HEAD internacional `cdca8e34013bba891a1c49f5ea859f933fcbea63`, árbol `977ec9cd9443bf0e7a284de13e00f242ea80ef92`. Se comprueba primero el trabajo ya integrado para no duplicarlo. PR33 incorporó T05/T06; PR34 resolvió las cinco incidencias Sonar que quedaban identificadas en el cierre anterior. PR35 estableció al Dr. Juan Copado Ceballos como único validador clínico final. Las entregas posteriores PR36–44 conservan su alcance y sus propias decisiones.

Esta continuación entrega el cierre técnico actualizado, expedientes focales de los ocho registros vencidos, conciliación de metadatos de gobernanza y una errata ECG concreta preparada para decisión. **No completa una revisión clínica integral de esos ocho módulos.** Los estados continúan en **118 GREEN / 13 YELLOW / 0 RED**, con **CLINICALLY_PENDING** global. La documentación revisada no equivale a GO_RELEASE ni a validación prospectiva.

## Cierre técnico que ya estaba conseguido

Los enlaces y resultados por commit están en [T05_T06_INTEGRATION_20261119.md](T05_T06_INTEGRATION_20261119.md), ahora actualizado con el cierre de PR33 y PR34. En el HEAD de partida, Clinical QA, App UI QA y Security and quality terminaron correctamente. Sonar registra 0 incidencias nuevas y 0 aceptadas. Se conservan los cortes anteriores y sus fallos para no atribuir el PASS final a un candidato previo.

Windows es el entorno de extracción protegida T05; Linux/POSIX, el de T06/B1. No se ha añadido compatibilidad conjunta en una plataforma. El laboratorio T06 sigue siendo sintético y local, sin cierre global G05. Las pruebas nativas y Sonar tienen ámbitos diferentes.

## Ocho registros: qué se ha contrastado y qué falta

Antigüedad calculada el 20/11/2026; límite de revisión canónico de 30 días. Todos permanecen YELLOW. «Antigüedad» mide días desde `last_checked`, no días adicionales de retraso.

| Módulo | Última fecha canónica | Antigüedad | Trabajo de esta continuación y límite pendiente |
| --- | --- | --- | --- |
| `clinical-image-interpretation` | 17/09/2026 | 64 días | Fuentes de evaluación de IA y seguridad de imagen; no hay una nueva cohorte adjudicada ni medición diagnóstica. |
| `blood-gas-image` | 27/09/2026 | 54 días | Contraste de muestra, preanalítica, oxigenación y requisitos de evaluación; falta validar el recorrido con tickets independientes y referencia por campo. |
| `ct-mri-screenshot` | 27/09/2026 | 54 días | Localizadores ACR y límites del estudio parcial; no se valida lectura de series completas ni se simula acceso íntegro a fuentes restringidas. |
| `ecg-image` | 27/09/2026 | 54 días | Error de identidad del epónimo Peñaloza–Tranchesi confirmado. Parche v1 preparado y comprobado; decisión médica pendiente. |
| `ecg-pocus-integration` | 27/09/2026 | 54 días | Contraste focal del principio de integración y de los límites para SCA/EP; no revisión de todos los síndromes ni rendimiento combinado. |
| `ophthalmology-image` | 27/09/2026 | 54 días | Fuentes AAO identificadas con versión y acceso real; falta completar el texto sustantivo inaccesible y la validación por tarea. |
| `pocus-image` | 27/09/2026 | 54 días | Contraste de adquisición dinámica cardíaca, pulmonar y venosa. Se conserva la aceptación previa del marco general; no se extrapola a la lectura automática de imágenes. |
| `final-human-review-gate` | 06/10/2026 | 45 días | Metadatos reconciliados con la decisión PR35 ya aceptada; no se presenta esa conciliación como una nueva revisión clínica final. |

Expedientes con fuentes, versiones, localizadores, comparaciones e incertidumbres:

- [IMAGE_EVIDENCE_FOLLOWUP_20261120.md](IMAGE_EVIDENCE_FOLLOWUP_20261120.md): imagen general, TC/RM, oftalmología y gobernanza.
- [BLOOD_GAS_EVIDENCE_FOLLOWUP_20261120.md](BLOOD_GAS_EVIDENCE_FOLLOWUP_20261120.md): gasometría, preanalítica y evaluación pendiente.
- [ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md): ECG, POCUS e integración, incluida la propuesta clínica exacta.

La fecha de consulta de una fuente en estos expedientes es 20/11/2026. No sustituye `last_checked` del módulo completo: hay contrastes focales, accesos parciales y requisitos de validación pendientes. Los ocho avisos de antigüedad continúan visibles.

## Conciliación de gobernanza ya autorizada

El módulo canónico y `qa/final-human-review-policy.json` ya aplicaban PR35. El registro aún citaba una obligación general de revisión especialista, una versión de octubre y una cifra histórica de 14 módulos amarillos. Se actualizan únicamente `primary_source`, su enlace, `stored_version` y la nota de `final-human-review-gate` para reflejar la autoridad de Juan, Farmacia consultiva y una cola dinámica sin cifra congelada. Se preservan `last_checked`, estado y requisitos de producto, privacidad, operación y QA que correspondan.

Se regenera `evidence-sources.json` mediante su generador existente. El catálogo conserva 254 fuentes; el contador de identidades compuestas pasa de 109 a 108 porque la identidad del gate ya no mezcla autoridades de revisión. **No es la división ni el cierre de una fuente clínica compuesta.** Las otras identidades compuestas siguen pendientes y no se modifican los overrides históricos.

## Decisión clínica nueva preparada

`ECG-PT-20261120`, versión 1: corregir exclusivamente la definición del epónimo en `ecg-image` y su proyección de la aplicación. La ficha contiene la pregunta SÍ/NO exigida por `AGENTS.md`, el texto exacto y dos publicaciones primarias. Respuesta: **pendiente**. La cola canónica conserva `owner_response: null` y `clinical_content_activated: false`.

El [parche candidato](../updates/candidates/ECG_PT_20261120.patch) contiene ambos consumidores y está comprobado sin aplicación a la entrega estable. Así la decisión se refiere a un cambio concreto y revisable. No se solicita de nuevo ninguna aceptación previa.

## Verificación de esta continuación

La comprobación estructural y sus límites se registran en [EVIDENCE_FOLLOWUP_QA_20261120.json](EVIDENCE_FOLLOWUP_QA_20261120.json). Se verifican el manifiesto de módulos, la normalización, la cobertura de evidencia, los enlaces locales de la entrega y la preservación de estados, fechas y contenido clínico activo. En la copia aislada del candidato ECG pasan las cuatro pruebas existentes de la proyección de guías; los otros 130 módulos no cambian.

No se reutilizan los resultados de cdca como si fueran ejecuciones del commit documental posterior. La publicación y sus controles se identifican mediante la PR de esta entrega. Esta continuación no repite las suites clínicas completas localmente ni interpreta imágenes de pacientes.
