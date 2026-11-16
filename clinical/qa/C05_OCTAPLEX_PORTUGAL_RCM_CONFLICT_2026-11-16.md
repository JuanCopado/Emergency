# EMERGENCY — C05: OCTAPLEX, PRODUCTO LOCAL SELECCIONADO Y CONFLICTO ENTRE RCM
**Fecha de conciliación:** 2026-11-16. **ID:** `reversal-vka-pcc`. **Estado:** `BLOCKED / CLINICAL_REVIEW_REQUIRED`. **Prioridad:** discrepancia farmacológica P1 para la futura implementación (no cambia el inventario P1 histórico).
**Procedencia del dato local:** el propietario confirma que el 4F-PCC utilizado en el Hospital da Horta es **Octaplex**, sin especificar aún **500 UI, 1000 UI o ambas**. No atribuirle un registro de stock, SKU/lote ni aprobación formal de Farmacia.

## 1. Fuente portuguesa localizada

[Octapharma Portugal — RCM Octaplex](https://www.octapharma.pt/api/download/x/291a94e4c6/rcm-octaplex.pdf), accesible desde la [página de producto portuguesa](https://www.octapharma.pt/produtos/produtos-visao-geral/cuidados-intensivos/octaplex). **Fecha de revisión interna del documento: 08/2020**; esta revisión **no demuestra que sea la última versión autorizada por INFARMED en noviembre de 2026**. Solicitar a Farmacia el RCM aplicable al lote dispensado o confirmación del titular.

| Presentación del documento portugués | Registro AIM portugués | Disolvente suministrado | Concentración nominal tras reconstitución |
|---|---|---:|---:|
| Octaplex 500 UI | 5260369 | 20 mL agua para inyectables | 25 UI de factor IX/mL |
| Octaplex 1000 UI | 5658331 | 40 mL agua para inyectables | 25 UI de factor IX/mL |

RCM portugués sección **4.2** para corrección urgente en tratamiento con AVK:

| INR inicial | Volumen orientativo del producto reconstituido |
|---|---:|
| 2–2,5 | 0,9–1,3 mL/kg |
| 2,5–3,0 | 1,3–1,6 mL/kg |
| 3,0–3,5 | 1,6–1,9 mL/kg |
| >3,5 | >1,9 mL/kg |

**Máximo individual: 3000 UI = 120 mL**, según este RCM portugués. Esta tabla **no selecciona una dosis exacta** dentro de sus rangos, y los límites 2,5 y 3,0 necesitan una decisión explícita de correspondencia. No convertir la tabla en dosis automáticas ni extrapolar «>1,9» a infinito; respetar el techo tras reconciliar la versión de ficha utilizada.

**Administración portuguesa (RCM 4.2):** IV, comenzar **1 mL/min** y aumentar posteriormente a **2–3 mL/min**, conforme a supervisión médica y etiqueta del producto. No aplicar automáticamente una tasa máxima de 8 mL/min tomada de otras jurisdicciones.

**Seguridad portuguesa (RCM 4.3–4.4):** contiene heparina; contraindicación por alergia conocida a heparina / antecedente HIT; también déficit IgA con anticuerpos anti-IgA. Vigilar trombosis/CID y reacciones de hipersensibilidad; documentar nombre y lote. No hay datos en población pediátrica.

**Estabilidad (RCM 6.3):** química y física demostrada durante **8 h a 25°C**; **uso microbiológico inmediato** salvo reconstitución con prevención adecuada de contaminación y protocolo institucional que asuma responsabilidad. El «8 h» **no equivale a caducidad clínica rutinaria de 8 h**. Conservar vial sin abrir protegido de luz y por debajo de 25°C. Solvente solo el suministrado, no mezclar con otros medicamentos; transferencia Nextaro®. Confirmar que la presentación real mantiene esos detalles.

## 2. Conflicto con la ficha de Octaplex en otros países

[SmPC británico Octaplex, revisión 16/10/2024](https://www.medicines.org.uk/emc/product/6566/smpc) y [ficha AEMPS española](https://cima.aemps.es/cima/dochtml/ft/66447/FichaTecnica_66447.html) describen esquema **25/35/50 UI de factor IX/kg** para INR **2–<4, 4–6 y >6**, con peso limitado a 100 kg y máximos **2500/3500/5000 UI** según INR. La administración descrita es **0,12 mL/kg/min hasta 8 mL/min**.

**DIFERENCIA MATERIAL / STOP:** el RCM portugués 08/2020 describe **tabla mL/kg diferente, techo 3000 UI y tasa 1→2–3 mL/min**. NO mezclar elementos de estos documentos para producir una regla «híbrida» que no figure en ninguna ficha. La tabla 25/35/50 y techo 5000 IU documentados anteriormente en el expediente C05 deben etiquetarse **NO VALIDOS COMO AUTOMATISMO PORTUGUÉS** hasta verificar el RCM actual por Farmacia. Ni siquiera confirmar la marca resuelve la discrepancia de versión/autorización.

## 3. Reglas de implementación y pruebas específicas

**Candidatos para preflight y validación:** producto `OCTAPLEX` (identificado por propietario, no lote), `PRESENTATION_UNKNOWN` (pendiente 500/1000 UI), vía IV, indicación de reversión urgente de AVK confirmada; datos INR/peso de calidad; heparina/HIT/IgA, alto riesgo trombótico; vitamina K según indicación; producto, mezcla, caducidad, monitorización y seguimiento INR.

**Prohibiciones antes del release:** no activar Beriplex ni sustituciones, no mezclar tablas PT/UK, no elegir arbitrariamente un valor dentro de un intervalo mL/kg de Octaplex PT, no usar 5000 UI como techo universal, no fijar 8 mL/min en el circuito portugués sin RCM local vigente, no usar estabilidad fisicoquímica como tiempo de uso microbiológico, no administrar a pacientes reales desde una calculadora incompleta.

**Casos negativos nuevos** (incorporados a `C05_VKA_PCC_NEGATIVE_CASES_2026-11-16.json`): detectar dosis >3000 UI bajo RCM PT 08/2020; bloquear velocidad de 8 mL/min importada del UK cuando PT 1→2–3 aplica; rechazar ausencia de versión del RCM local; rechazar cruce de tablas y falta de selección puntual bajo tabla mL/kg; prohibir declarar automáticamente caducidad de 8 h y rechazar autoelección 500/1000 UI.

## 4. Pendientes para cierre

1. Farmacia confirma **si Octaplex 500 UI, 1000 UI o ambas presentaciones** están en stock, referencia, RCM vigente aplicable y si la tabla/velocidad 08/2020 o posterior autorizada rige en Horta.
2. Hematología/Urgencias revisa algoritmo para hemorragia mayor, cirugía urgente y HIC con INR bajo, y estrategia de vitamina K según indicación.
3. Farmacia/Enfermería valida reconstitución, transferencia, estabilidad microbiológica, caducidad real, control de HIT, IgA y monitorización; firma nominal/fechada.
4. Desarrollo/QA implementa algoritmo **solo tras seleccionar fuente vigente**; pruebas negativas e integración sin modificar otros 18 bloqueos, 4 P1 ni `main`.
5. Revisión humana independiente de la versión publicada, con SHA de código probado, antes de levantar `block_reason`.

**Estado:** producto identificado por propietario, RCM portugués 08/2020 identificado, divergencia de jurisdicciones **ABIERTA**, motor clínico y 22+ pruebas negativas **NOT_RUN**, contrato 5 **BLOCKED**, `CLINICALLY_PENDING`. No se certifica validación clínica ni de Farmacia.


## Adenda 16/11/2026 — presentaciones, dosis comunicadas y velocidad

**Fuente local:** confirmación del responsable del proyecto, 16/11/2026. Sustituye la duda de presentación: declara disponibles **Octaplex 500 UI/20 mL y 1000 UI/40 mL**, ambas **25 UI de factor IX/mL**, según [RCM portugués de Octapharma (08/2020)](https://www.octapharma.pt/api/download/x/291a94e4c6/rcm-octaplex.pdf). La declaración no equivale a inventario/RCM vigente firmado por Farmacia.

**Administración local:** iniciar **1 mL/min**; aumentar a **2–3 mL/min** si no hay incidencias. Coincide con sección 4.2 del RCM portugués. No importar velocidad UK de hasta 8 mL/min.

### Comparación obligatoria: dato local y conversión literal del RCM portugués

| INR inicial | Pauta local comunicada (UI factor IX/kg) | Tabla RCM Portugal (mL/kg) | Conversión aritmética exacta de RCM a 25 UI/mL | Decisión |
|---|---|---|---|---|
| 2–2,5 | **25–32,5** | **0,9–1,3** | **22,5–32,5** | **Discrepancia**: límite inferior 25 local, 22,5 de RCM |
| 2,5–3 | **32,5–40** | **1,3–1,6** | **32,5–40** | Coincide |
| 3–3,5 | **40–47,5** | **1,6–1,9** | **40–47,5** | Coincide |
| >3,5 | **47,5–50** | **>1,9** | **>47,5**, sin techo UI/kg expreso en la fila | **Discrepancia**: 50 UI/kg local no es límite por kg transcrito del RCM |

**Tope individual de RCM portugués revisado:** **3000 UI = 120 mL**. No aplicar el máximo 5000 UI de versiones británicas. No derivar número de viales ni redondear a presentaciones de 500/1000 UI sin aprobación.

**INR exactos 2,5, 3,0 y 3,5:** los intervalos de la tabla se solapan formalmente. La asignación del extremo y el redondeo de laboratorio necesitan una regla clínica única definida y firmada. No elegir de oficio el tramo superior/inferior.

**Intervalos, no dosis fijas:** el RCM pide individualización por INR previo, INR objetivo, localización, gravedad y evolución. La relación dimensional dosis = kg por UI/kg seleccionada y volumen = UI / 25 solo se admite en una herramienta de revisión teórica, no como prescripción ni como elección automática de límite inferior/medio/superior.

**Separar vitamina K y HIC:** la pauta y formulación de vitamina K se verifican individualmente; el caso HIC con INR <2 requiere circuito distinto, no aplicación de la tabla genérica.

### Puertas de seguridad tras esta incorporación

- PRODUCTO: **Octaplex de 500 UI/20 mL y 1000 UI/40 mL declarados por propietario**; lotes, ficha vigente, reconstitución y stock verificable aún pendientes.
- VELOCIDAD: **1 mL/min inicial y 2–3 mL/min posteriormente** como referencia local/RCM 2020, pendiente de aprobación técnica de administración.
- DOSIS: cuatro **bandas locales declaradas** separadas de conversión literal del RCM; primer y último tramo **NO CONCILIADOS**.
- DOSIS MÁXIMA: **3000 UI por administración** en el RCM portugués disponible; no sustituir por UK.
- BLOQUEO: contrato 5 **BLOCKED / CLINICAL_REVIEW_REQUIRED**; QA integrada y revisión galénica no ejecutadas; mantener CLINICALLY_PENDING y main intacta.
