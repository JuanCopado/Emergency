# Sustitución del laboratorio RCCC por protocolo local de insulina UCI

Fecha: 2026-11-13. Rama local: codex/v144-insulin-uci-rccc.

## Cambios ejecutados

Se retiran el motor y pruebas RCCC de la ruta activa. Nuevo motor puro en
app/src/insulin/protocol.ts y nueva interfaz en /insulin-uci. Cinco recorridos:
inicio IV, ajuste IV, reinicio IV, transición SC y conversión de bolo prescrito.
No se modifica el catálogo/API canónico de farmacología aguda ni sus 19 bloqueos.

ADA 2026 continúa como marco; las reglas concretas son el protocolo local
seleccionado por el propietario, no se atribuyen a ADA, Glytec o Yale.
La revisión clínica y de Farmacia consta como declaración del propietario,
no como firma electrónica verificada. Sigue CLINICALLY_PENDING.

La preparación elegida es 100 UI de insulina humana regular hasta 100 mL
finales de SF 0,9%, concentración 1 UI/mL. Se muestran el cebado de 20 mL y el
recambio elegido de 24 h con sus condiciones de producto, envase y asepsia.
No se declaran comprobadas físicamente la bolsa o línea locales.

## Decisiones inequívocas y pendientes preservados

- Se calcula el ritmo previo más 1, 2 o 3 UI/h en las bandas elegidas; mantener
  entre 140 y 180; pausa preventiva entre 70 y 100; hipoglucemia <70 con controles
  cada 15 min e intervalo de glucosa 10–20 g, sin elegir gramos automáticamente.
- Nueva instrucción del propietario: reducción de 1–2 UI/h sustituye a la
  alternativa anterior del 50% en 101–139. Se selecciona explícitamente 1 o 2
  UI/h en el formulario, sin inventar un umbral de descenso. Si el resultado
  fuera cero o negativo, se exige decisión de pausa; no se impone un mínimo.
- Los valores decimales entre bandas originales se bloquean sin redondearlos.
- El ajuste horario no se extrapola a intervalos distintos de 60 minutos.
- La tendencia se calcula y muestra. No se importa el umbral de caída de otro
  protocolo ni se afirma que esta tabla ya resuelva todos los descensos rápidos.
- Un ritmo cero no genera una dosis inicial por aplicación de incrementos.
- Inicio IV: comprueba persistencia y umbral ≥180; no calcula un ritmo inicial
  que el propietario todavía no ha definido inequívocamente.
- Reinicio al 50% estrictamente con glucemia >140 tras pausa preventiva de
  70–100. No se extrapola a hipoglucemia u otras interrupciones.
- Transición SC: requiere 6–8 h estables, estabilidad clínica/hemodinámica y
  nutricional y el criterio local de requerimiento <2 UI/h. Muestra el rango
  60–80% de la extrapolación a 24 h y la mitad basal, sin elegir un porcentaje
  ni dividir bolos prandiales automáticamente.
- Bolo: conversión UI→mL de una dosis explícitamente prescrita. Los criterios
  de perfusión y glucemia >300 no activan bolos ni el cálculo 0,1 UI/kg o
  glucemia/100. No calcula velocidad ni duración de administración. CAD/EHH
  permanecen excluidos y remiten al circuito propio.
- Editar, cambiar recorrido, desmarcar datos sintéticos o borrar invalida el
  resultado. Sin persistencia de entradas ni envío a un servicio de cálculo.

## Verificación nueva, no reutilizada

- Motor local: 45 pruebas PASS. Interfaz DOM: 5 pruebas PASS (50 focales).
- Frontend completo: 426/426 PASS, tras retirar 28 pruebas históricas RCCC y
  sustituir las 3 UI anteriores por las 5 nuevas (376 preexistentes + 50 locales).
- Typecheck, lint y build: PASS. Catálogos preservados: 131 módulos, 196
  procedimientos canónicos + 4 alias, 89 pautas pediátricas.
- QA global: 7/7 controles PASS y 603/603 pruebas Python PASS.
- Catálogo de fuentes normalizado: --check PASS, 220 fuentes/131 módulos.
- Prueba de invariantes del registro: sólo 27 cambios GREEN→YELLOW, con fechas,
  fuentes, versiones y ventanas de revisión idénticas; cero promociones a GREEN.
- Navegador real: BLOQUEADO. Chromium aborta antes de abrir página: socket()
  Operation not permitted. El intento de ejecutar el conductor local con
  permisos ampliados fue rechazado por la política del entorno: sandbox_approval
  false. No se ha sorteado esa restricción. No se afirma verificación visual,
  móvil u offline en navegador real. El conductor reproducible se actualizó
  a los cinco recorridos en app/scripts/check-insulin-uci.mjs.

## Evidencia vencida: corrección del estado, no renovación

Se aplicó la regla de clinical/references/update-policy.md: una revisión fuera
de ventana es YELLOW. Antes: 29 GREEN/102 YELLOW, 27 errores por GREEN vencidos.
Después: 2 GREEN/129 YELLOW, cero errores estructurales y 116 avisos de revisión
vencida conservados. El detalle de los 27 cambios está en
EVIDENCE_EXPIRY_STATUS_RECONCILIATION_2026-11-13.json.

No se han renovado esas 116 revisiones bibliográficas, no se han cambiado
last_checked ni ampliado ventanas, y no se han relajado validadores. PASS es del
QA técnico de integridad: la revisión de fuentes actuales sigue pendiente donde
corresponde y la liberación clínica sigue CLINICALLY_PENDING.

## Límites de entrega

Cambios guardados localmente, sin publicación ni merge. Se respeta el rechazo
previo de publicación pública. Main y referencias protegidas intactos.
No se declara cierre clínico global ni se habilita prescripción automatizada.
