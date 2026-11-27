# Revisión Codex separada — PR122

Candidato `a625267c2aea5b23e1d517d59251eb3d4924856f`, árbol `cf01aba0df5143ee6093618de13cba73e8d37c18`, base `2058e97179ae793914dcd016e4fd033395dbc3e2`. Árbol comprobado mediante GitHub Git API. Dictamen: **FAVORABLE_TECHNICAL_HISTORICAL_PROTAMINE_SCOPE_WITH_DOCUMENTARY_FOLLOWUP**. No es dictamen Antigravity ni validación clínica humana independiente.

Se revisaron los 15 archivos del diff, el validador documental y las 18 regresiones definidas. El cierre de protamina respeta MED-RES-PROT-01 v1: perfil histórico revocado español, inactivo, límite histórico estricto conservado y sin sustitución automática o cambio de rutas activas. Los 12 hashes del recibo de preservación coinciden con los blobs Git locales del árbol base, equivalente al receptor. No hay cambios en fuentes clínicas ejecutables existentes, fórmulas, rutas, catálogos o estados de evidencia.

No se reejecutaron pruebas numéricas ni suites. En la única consulta de CI del SHA exacto, Security `45959957685`, Clinical `45959957789` y App UI `45959957750` seguían en ejecución. Los 18 PASS locales se atribuyen al ejecutor; el gate anterior de `94a983b` no se transfiere.

## Cardiovascular: recepción recuperada, comparación pendiente

Se leyeron las seis propuestas originales y la aceptación literal a través de Drive, después de consultar metadatos. Los originales físicos ya existentes mantienen sus bytes: propuesta 11.634 bytes, SHA-256 `2d4d303c835779143d126b31917060e403f5aa7f1b5d86d5aef60b401ceaa036`; aceptación 404 bytes, SHA-256 `10f5dcb68a6e02cae4341d3996fc95348befd305af9603a6627506bba21647ec`. El recibo físico tiene SHA-256 `6ce1167b7de7724cff39b5eacc3cd66c470a3867a7f557f43ef302bb96889884`. Coinciden con el expediente recuperado. No se reconstruyeron originales ni se copiaron imágenes.

| Decisión | Cotejo documental y siguiente dependencia |
|---|---|
| CARDIO-01 | Las cuatro rutas y la excepción pediátrica ya existen. Cotejar la monitorización por situación, capnografía y posreanimación sin cambiar algoritmos ni dosis. |
| CARDIO-02 | El módulo ya diferencia estenosis/regurgitación y amenaza protésica/endocarditis. Comparar las cinco ramas originales y la monitorización explícita antes de ampliar la estructura. |
| CARDIO-03 | El texto canónico ya incluye captura, imán y consulta/extracción especializada. Cotejar la rama de asistencia ventricular; no convertir el imán en respuesta universal. |
| CARDIO-04 | Conservar objetivos por síndrome. La secuencia general y las cifras originales necesitan su localizador primario exacto; no insertarlas por la sola recepción del texto. |
| CARDIO-05 | Mantener selección por contexto y perfiles por jurisdicción. La comparación US/ES de clevidipino y el perfil portugués requieren verificación antes de cualquier uso operativo. |
| CARDIO-06 | Rutas etiológicas, ECG inicial y rechazo del antitrombótico genérico ya constan en el módulo. Comparar el resto de estructura y seguimiento sin alta automática ni nuevas pautas. |

La aceptación dice expresamente que no habilita dosis no revisadas ni libera clínicamente el producto. La falta de recepción del original queda resuelta; permanecen comparación científica y materialización verificables. La implementación está asignada al chat responsable de PR122: no se duplica ni se solicita otro voto.

PR122 conserva el corte anterior con `RECORDED_PENDING_ORIGINAL_FICHE` y fichas nulas. Mantener ese SHA como snapshot; un seguimiento posterior debe reflejar la recepción nueva y distinguirla de implementación. El validador actual rechaza `IMPLEMENTED`: no alterar estados para pasar pruebas.

## Composición

Los cambios de PR122 y PR121 son disjuntos por ruta. Puede prepararse una composición aislada preservando sus identidades; deberá obtener QA/CI propias. La matriz vigente debe superar expresamente el estado histórico de candidato no recibido y original ausente. Sin fusión en receptor protegido ni despliegue.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
