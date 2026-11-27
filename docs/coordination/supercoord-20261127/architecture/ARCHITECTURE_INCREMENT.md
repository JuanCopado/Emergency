# Arquitectura e interoperabilidad — corte verificable 27/11/2026

Base local `5494b0037dcfe2c2565187985b862ffa8ea1d83b`, árbol `78e27cb900f7dd901eb5aeb48026276dc48b942c`, igual al árbol receptor2058 confirmado por coordinación. Auditoría técnica Codex, sin cambio de runtime ni transmisión de datos.

La revisión corrige un límite del informe previo: el grafo **sí tiene generador y pruebas**, y DICOM tiene preparación/renderizador local y guardas. Ninguno acredita RAG clínico operativo, integración PACS o conformidad de intercambio.

| Capacidad | Evidencia observada | Dependencia para ampliar |
|---|---|---|
| Grafo | Generador determinista ejecutado:131módulos,254fuentes,397nodos,417relaciones;102fuentes compuestas | Reusar procedencia; no inferir conocimiento clínico |
| RAG | Contrato de diseño y catálogo, sin retrieval clínico operativo | Consumidor, permisos por campo/uso y contrato de recuperación |
| FHIR / HL7 | Sin consumidor en los ámbitos de código revisados | Contrato de destino/campos, versión/perfil oficial y pruebas sintéticas |
| PACS / DICOM | Exclusión de envío DICOM y rendererRSNA local | Contrato de píxeles, derechos, privacidad y sistema autorizado |
| Agentes | Metadatos/configuración y adaptador de visión | Contratos de capacidad/proveedor y revisión humana; sin autonomía clínica |
| G05 | T06/Q4 sintético y seis requisitos canónicos preservados | Consumidor público, derechos, retención/responsables, QA/auditoría exactas y PTBR-PIX |

Se materializó `project-graph.json` mediante el generador existente y se ejecutó `test_project_graph.py`: **14/14 PASS**, incluidos negativos de módulo ausente y fuente inexistente, determinismo y no promoción de estados. Registro conserva129GREEN/2YELLOW, sin inferencia clínica. Los resultados son propios de esta ejecución, no CI ni auditoría Antigravity.

No se creó un segundo esquema, grafo, servicio o conector. El siguiente incremento de expansión necesita un contrato de consumidor sintético por source_id/module_id; no debe cargar texto prestado, datos clínicos reales o píxeles por inferencia de permiso. No se seleccionó versión de FHIR/HL7/DICOM ni se afirma conformidad; su elección futura deberá verificarse contra documentación oficial.

Se conserva `CLINICALLY_PENDING` y `NO_GO_CLINICAL_RELEASE`. No se reabren19contratos niMED-DEC-R46-01/02. R5-1/R5-2/SCA independientes aplazadas no se presentan como impedimento del trabajo técnico completado.

Detalles de rutas, hashes Git y bytes locales, dependencias y límites de búsqueda en `CAPABILITY_DEPENDENCY_MAP.json`. La salida completa del ensayo está en `graph-tests.log`.
