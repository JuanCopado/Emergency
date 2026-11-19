# P3/P4 conciliado con PR20 en R2

Candidato sin commit basado en PR20 `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`; delta técnico P3/P4 `b92eb9dc96e00ea1ad2fae33426965e91852f80c`. No se importa el estado farmacológico histórico de esa rama.

| Interfaz | Entrada sin agrupación | Número JSON | Salida |
|---|---|---|---|
| ES/PT | 0.1 | 0.1 numérico | 0,1 |
| EN/ZH | 0.1 | 0.1 numérico | 0.1 |

Los formatos ambiguos (coma, espacios internos, hexadecimales), no finitos y underflow de mantisa no nula se rechazan. Los consumidores conservan sus límites específicos; cero explícito no equivale a underflow. `formatCanonicalNumber` cambia solo el separador sin redondeo nuevo, incluido resultado anidado; bomba y demás redondeos previos mantienen su alcance. Nunca se reconvierte salida localizada en entrada de cálculo.

La interfaz usa recursos estáticos en cuatro idiomas; las nuevas etiquetas de los contratos PR20 se agregan sin traducir campos clínicos, opciones canónicas, fuentes, mensajes del backend ni contenido del caso. No se invoca traducción remota. La UI y exportación muestran el límite de traducción clínica integral pendiente. No se atribuye revisión lingüística profesional.

AcuteMedications conserva campos condicionales, etiquetas de opción, aceptación del propietario, tipo de resultado (6 cálculos/13 vías sin dosis entre los19 aceptados), confirmación e invalidación. La nota impide enviar edad inválida como null y rechaza signos vitales con formato inválido antes de guardarlos. El contexto opcional no depende del idioma ni modifica cálculos.

Procedencia y límites: `coordination/EMERGENCY_INTG_R2_20261116/COMPOSITION.md`. Resultados actuales, logs, árbol efectivo y manifest se entregan en OUTPUT_DIRECTORY del despacho; no se reutilizan cifras PASS históricas. El intento de navegador se informa separado, BLOCKED_ENVIRONMENT con cero casos si no arranca. CLINICALLY_PENDING conservado.
