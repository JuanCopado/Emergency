# Insulinoterapia UCI: referencia interactiva RCCC

Petición: una experiencia equivalente a https://www.rccc.eu/protocolos/HG/index.html dentro de Emergency. Se mantienen los cuatro recorridos: inicio IV, ajuste IV, inicio SC y ajuste SC. Interfaz propia React/TypeScript, sin copiar HTML, scripts o diseño propietario ni cargar scripts externos.

Decisión de implementación: laboratorio de simulación técnica con datos sintéticos. Toda salida conserva CLINICALLY_PENDING y clinical_use_allowed=false. No permite prescripción ni activa contratos clínicos. Los algoritmos históricos se identifican como RCCC/R. Pitarch 2012, no como ADA 2026. La referencia ADA 2026 se muestra separada. Los solapamientos, huecos y entradas fuera del dominio se bloquean, nunca se resuelven por orden accidental del código web.

Alternativas consideradas: incrustar la página externa (dependencia y fuga de datos); copiar su programa (errores heredados, ausencia de licencia); interfaz propia con reglas declarativas y revisión pendiente (seleccionada por el implementador conforme a las restricciones clínicas existentes). El usuario pidió implementación directa; no se adopta un nuevo algoritmo clínico aprobado.

Integración: ruta /insulin-uci y acceso desde Home y farmacología aguda. Motor y fuentes en src/insulin; UI en pages/InsulinUci.tsx. CAD/HHS, pediatría e hiperpotasemia excluidos. No modificar dosis, fórmulas, catálogo canónico, cuatro P1 ni 19 bloqueos existentes. Una casilla de simulación no autoriza uso clínico.

Validación: pruebas de límites, huecos/solapamientos reales, números no finitos, cero válido de perfusión, minutos entre controles, reparto SC/redondeo, reseteo de resultados, navegación y pruebas generales de app. Revisar 144 mg/dL + 0,7 UI/h, 252/260 mg/dL y huecos decimales. QA técnica no equivale a aprobación clínica; responsable y farmacia deben seleccionar un protocolo inequívoco antes de habilitar decisiones de dosis.
