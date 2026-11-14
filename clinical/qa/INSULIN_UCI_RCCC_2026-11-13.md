# Insulinoterapia UCI — implementación RCCC en revisión

Fecha: 2026-11-13. Rama: `codex/v144-insulin-uci-rccc`.
Base publicada verificada: T01-R `4dd47604e24cb59f60c263e362dc207826f34887`.
No se afirma conciliación con Windows local ni con Emergency-Private-Backup.

## Entrega

Ruta `/insulin-uci`, accesible desde Home y farmacología aguda. Cuatro recorridos:
inicio IV, ajuste IV, inicio SC y ajuste SC. Formularios propios React/TypeScript;
no se copian código, estilos o recursos de RCCC. No nuevas dependencias.
Motor separado de los contratos canónicos. Toda salida: CLINICALLY_PENDING,
clinicalUseAllowed=false y NO ADMINISTRABLE. Sólo datos sintéticos; no persiste
ni envía valores. No integra prescripción, exportación de dosis ni orden de bomba.
La casilla de simulación no permite habilitar uso clínico.

## Diferencias deliberadas respecto de RCCC

- Se recoge el tiempo entre controles y se calcula la tendencia por hora. El
  ajuste histórico sólo se simula con 60 minutos: no se asume ese intervalo.
- Se aceptan coma decimal y cero UI/h como entrada de simulación; no equivale
  a autorizar el inicio/reinicio clínico. Entradas inválidas no conservan resultados.
- Se evalúan las reglas coincidentes de forma declarativa. Si hay solapamientos
  o huecos, no se imita la última asignación Javascript del sitio original.
  Ejemplos: 144/150 mg/dL y 0,7 UI/h sin regla; 230/250 mg/dL y 2 UI/h
  reglas solapadas; 252/260 mg/dL sin regla; 108,5 mg/dL fuera de intervalos.
- No se reproduce el tratamiento histórico de hipoglucemia ni sus bolos. Valores
  bajos seleccionados se bloquean. No se incorpora un protocolo de rescate nuevo.
- SC: reparto oral histórico y cambios absolutos, no dosis finales ni transición
  IV→SC. La alternativa de nutrición enteral del original no está implementada.
- El redondeo SC no se corrige ocultamente: para 10 UI/día el reparto redondeado
  suma 11 UI, diferencia +1 UI; se muestra y requiere revisión.
- No reproduce las alternativas opcionales del algoritmo IV. Los intervalos de
  control se identifican como históricos, sin función de alarma ni instrucción.
- A 1 UI/mL se muestra una equivalencia hipotética UI/h→mL/h; no acredita
  producto, preparación, envase, cebado, compatibilidad o estabilidad.
- Excluye pediatría, CAD/HHS e hiperpotasemia. Las cuatro ramas canónicas de
  insulina existentes y los 19 bloqueos de farmacología aguda siguen intactos.

## Fuentes y límites de evidencia

RCCC / R. Pitarch 2012: índice, inicioIV, ajusteIV, inicioSC y ajusteSC. Se
recuperaron las cinco páginas; hashes de bytes originales y URLs en
`INSULIN_UCI_RCCC_SOURCES_2026-11-13.json`. Se registra la atribución del sitio;
no se afirma que RCCC sea autor del ensayo NICE-SUGAR ni que exista licencia
para redistribuir su programa. No se redistribuye ese programa.

El enlace al algoritmo primario NICE-SUGAR devolvió 502: no se ha contrastado
fidelidad con el algoritmo original del ensayo. ADA 2026
(https://doi.org/10.2337/dc26-S016) sólo respalda la comparación de objetivo
habitual UCI 140–180 mg/dL y vigilancia durante insulina IV cada 30 min–2 h;
no valida el modelo RCCC ni sus reglas subcutáneas históricas.

## Verificación observada

- `npm test`: 407/407 PASS (376 existentes + 31 nuevas).
- Nuevas: 28 pruebas de motor y 3 de interacción DOM.
- `npm run typecheck`: PASS.
- `npm run lint`: PASS, incluido el conductor de navegador nuevo.
- `npm run build`: PASS; generadores 131 guías, 196 canónicos + 4 alias,
  89 pautas pediátricas sin cambios de catálogo.
- `python3 -m unittest discover -s tests -p test_acute_medication_v144.py`:
  10/10 PASS, incluidos bloqueos farmacológicos existentes.
- `python3 qa/qa_runner.py`: BLOCKED; 5/7 controles pasan. `evidence-coverage`
  falla por revisiones vencidas; `unit-regression-tests` ejecuta 603 pruebas,
  602 PASS y 1 FAIL: `test_all_declared_high_risk_modules_have_evidence_records`.
  Hay 27 errores de revisión vencida en el registro. Registro, validador de
  evidencia y test de integridad permanecen idénticos a la base T01-R.
- Navegador real/inspección visual: NO COMPLETADO. El conductor Playwright
  abortó antes de abrir página: Chromium `socket() failed: Operation not permitted`.
  No se afirma prueba real de móvil, navegación u operación offline. Las pruebas
  DOM sí pasaron. Reproducir con `npm run dev` y `npm run insulin:browser-check`
  en un entorno que permita Chromium; configurable CHROMIUM_PATH/INSULIN_APP_URL.
- Avisos observados no bloqueantes: React Router v7 future flags, anotaciones
  Rollup de zod y configuración npm http-proxy heredada.

## Pendientes para uso clínico

Seleccionar y aprobar un protocolo local inequívoco; contrastar el algoritmo
primario; resolver límites/alternativas/intervalos/reinicio e hipoglucemia;
conciliar producto y equipo; revisión nominal y fechada de clínica y farmacia;
verificación independiente y navegador real. Los tests validan software,
no eficacia, seguridad prospectiva ni aprobación del protocolo.

No se promociona evidencia, no se alteran main/RC1/v1.43 y no se fusiona nada.

## Nuevo protocolo aportado: Hospital de Brotas PR.UTI.002, revisión 00

Documento de cinco páginas; historial de emisión y aprobación fechado 12/06/2024.
Se leyeron las cinco páginas y se inspeccionaron visualmente las páginas 3 y 5.
El PDF original aportado por el propietario NO se incorpora al repositorio.
SHA-256 del PDF: `753a337f3318ffbdc27ce6ed52666cd1a562aba073aa60f543ad3f688b53046f`.

Aporta trazabilidad institucional y una tabla IV con ajustes, pausa y reinicio.
No es la fuente de la tabla UCI de cinco columnas ni valida RCCC. Se limita a
pacientes críticos con aporte calórico continuo y excluye alimentación oral o
enteral intermitente. No se extrapola a CAD/HHS o pediatría.

Pendientes documentados:
- Inicio tras dos glucemias >150 mg/dL y objetivo 91–150 mg/dL; difiere del
  umbral habitual >=180 persistente y objetivo 140–180 de ADA 2026.
- Permite controles cada tres horas tras estabilidad; necesita conciliación con
  vigilancia habitual de 30 min–2 h de insulina IV.
- Preparación descrita como 100 UI en 100 mL de SF 0,9% (1 UI/mL). El texto
  no explicita retirar volumen para lograr un volumen FINAL exacto: no se supone.
- Cebado con descarte de 5 mL, no 20–50 mL. No identifica material/modelo del
  equipo: no acredita automáticamente el sistema local.
- Orden de cambio de bolsa al menos cada seis horas por supuesta precipitación/
  pérdida de eficacia. Es una instrucción institucional, no prueba de estabilidad
  fisicoquímica universal ni respaldo de las 24 horas previamente propuestas.
- Tabla inicial sin regla para exactamente 281 mg/dL (216–280 y >281).
- En 251–395: aumento de 2 UI/h y, tras tres valores >250, aumento del 50%; no
  queda inequívoco si son instrucciones acumulativas o alternativas.
- Reinicio en 71–90: restar 1 UI/h puede producir valor negativo desde un ritmo
  <1 UI/h; no especifica límite inferior. No se corrige inventando un mínimo.
- Bolo descrito como 50% de una tasa de infusión UI/h: requiere convertir a una
  dosis UI con referencia temporal explícita; dimensionalmente no es una dosis.
- Transición SC 30 minutos antes de apagar la perfusión y dosis ligada al ritmo
  horario no equivale a un régimen basal de transición individualizado.
- Nombres y fecha en la aprobación documental del Hospital de Brotas no son
  revisión nominal de clínica/farmacia del Hospital da Horta; firmas gráficas en
  blanco en la copia. No se acredita vigencia local mediante este documento.

Decisión: conservar como evidencia documental para conciliación, sin adoptar
sus dosis, objetivos o reglas en producción y sin desbloquear contratos.

## Publicación

El commit de implementación local es d06f810. El intento de publicación fue
rechazado por revisión automática: repositorio público y ausencia de autorización
explícita para divulgar código y documentación. No se reintenta por otro medio.
Se requiere autorización expresa antes de publicar. Main permanece intacto.
