# Ceftriaxona: conciliación de población y salvedades

Fecha: 2026-11-16. Hallazgo de referencia: `GMA-C-P1-001`.

## Resultado y alcance

Implementación focal candidata para `sepsis-community-ceftriaxone`, solicitada por el propietario: actualizar a menores de 16 años e incorporar salvedades clínicas y farmacéuticas. Las dos representaciones de catálogo usan ahora NICE NG254 (19/11/2025), edad desde 28 días y antes del cumpleaños 16. Se conserva la referencia 80 mg/kg IV una vez al día, máximo 4 g/día. La aritmética automática se limita a <50 kg y a contexto elegible explícito.

Base exacta: `JuanCopado/Emergency`, commit `761f42d9afc8a7b7202d18bb0fd506d721dd4e50`, árbol `f834c6f8e77c7006082c909bc28f8bfaa8a72d61`, correspondiente al respaldo público `backup/2026-11-14-v144-90c95ce`. Rama de entrega de este componente: `codex/v144-ceftriaxone-under16-20261116`. Es una derivación del candidato C; no compone ni integra por sí sola las contribuciones A/B/C/D de I02.

Se preservan `CLINICALLY_PENDING`, los estados globales de evidencia y los 19 bloqueos de farmacología aguda. La corrección no declara aceptación integral del candidato, cierre de todos los P1, aprobación asistencial o validación prospectiva.

## Cambios clínicos y farmacéuticos

La justificación y las fuentes primarias están en [ceftriaxone-sepsis-under16-safety.md](../references/ceftriaxone-sepsis-under16-safety.md).

| Regla | Implementación y precisión incorporada |
|---|---|
| Edad | ≥28 días y <16 años por fechas de calendario. El día 28 conserva las restricciones neonatales del producto. |
| Peso | ≥50 kg sale del cálculo y requiere elegir pauta adulta según indicación. No se codifica una regla universal de 2 g/4 g. |
| Selección | Se exige sepsis comunitaria sin foco claro ni antecedente de resistencia a ceftriaxona; otros escenarios requieren su vía clínica local. |
| Menores de tres meses | Se exige plan explícito de cobertura frente a Listeria; no se calcula aquí el acompañante. |
| Calcio | Prohibición general de mezcla y simultaneidad; ≤28 días también con calcio previsto/secuencial. >28 días exige condiciones de línea para administración secuencial. La excepción específica de NPT continua queda fuera de la automatización. |
| Prematuridad | Contraindicación hasta 41 semanas posmenstruales. Se verifica coherencia de PMA y edad cronológica con nacimiento antes de 37 semanas. |
| Riesgo neonatal de bilirrubina | En el día 28 exige información explícita sobre hiperbilirrubinemia/ictericia/hipoalbuminemia/acidosis. |
| Vía y lidocaína | La entrada sigue siendo IV. Se rechazan lidocaína o calcio como diluyentes. Las salvedades IM son documentales: 1 g/sitio; los 3,5 mL de ciertas presentaciones son disolvente, no un volumen final universal. |
| Función orgánica | CrCl <10 mL/min deriva a revisión; la ficha señala un límite de 2 g/día en ese escenario. Hepatopatía grave, combinación grave o función desconocida requieren revisión individual. |
| Unidades y volumen | Este ID devuelve dosis total en mg y referencia separada en mg/kg. No calcula mL y rechaza una concentración añadida a un catálogo personalizado. |

La declaración de ausencia de ajuste hepático se limita a insuficiencia aislada leve/moderada con función renal conservada. La insuficiencia renal aislada se interpreta con función hepática preservada y con la salvedad de CrCl <10 mL/min. No se atribuye un techo universal de 2 g/día exclusivamente a la combinación renal/hepática grave.

## Contrato técnico

`pediatric_antibiotic_calculator.calculate(entry_id, weight_kg, path=..., *, context=None)` conserva la interfaz previa para otras entradas. Para el ID objetivo exige un objeto de contexto explícito; la CLI admite `--context-json PATH`.

Campos comunes: `birth_date`, `assessment_date` (YYYY-MM-DD), `community_acquired`, `known_infection_focus`, `ceftriaxone_resistance_history`, `calcium_iv_mode`, `premature`, `diluent_contains_lidocaine`, `diluent_contains_calcium` y `renal_hepatic_status`. Las afirmaciones booleanas deben ser booleanos reales.

Campos condicionales: `calcium_line_changed_or_flushed` para calcio secuencial; `postmenstrual_age_days` cuando es necesario para prematuridad; `neonatal_bilirubin_risk` en ≤28 días; `listeria_coverage_planned` antes de tres meses calendáricos; `creatinine_clearance_ml_min` para insuficiencia renal aislada; `hepatic_impairment_severity` para insuficiencia hepática aislada. Una ruta explícita diferente de IV se rechaza.

Los errores usan códigos estables y no incluyen una dosis alternativa. Se valida primero el peso finito y positivo. La salida contiene edades derivadas, fuentes y salvedades; no devuelve las fechas de nacimiento/evaluación. La salida conserva `CLINICAL_REVIEW_REQUIRED` y `clinical_release_status: CLINICALLY_PENDING`.

## Verificación ejecutada

Se materializaron 27 archivos de la base exacta, comprobando cada SHA de blob contra el árbol Git remoto. Es un entorno local parcial; no se presenta como checkout completo ni como ejecución de QA global.

Ejecución final del coordinador: **28/28 PASS**, 0 fallos, 0 errores; tiempo informado por `unittest`: **0,204 s**.

- **24 pruebas nuevas** de `test_ceftriaxone_sepsis_safety.py`: ambos catálogos, CLI, contexto ausente, tipos, fechas y límites 27/28/29 días, cumpleaños 16, 50 kg, tres meses calendáricos, calcio, prematuridad, función orgánica, catálogos alterados y aislamiento de otras entradas.
- **Cuatro métodos existentes** de `test_skill.py`, ejecutados en un harness AST focal que extrae sus cuerpos sin modificar sus aserciones. No se ejecutó el resto de ese módulo de pruebas.

Los cuatro métodos son:

```text
test_v136_pediatric_antibiotic_syndrome_specific_calculations
test_v136_pediatric_antibiotic_caps_and_boundaries
test_v136_pediatric_antibiotics_are_syndrome_specific_and_calculable
test_v136_pediatric_antibiotic_caps_and_external_dose_gate
```

La suite nueva se puede reproducir desde la raíz del repositorio con:

```bash
python3 -B -m unittest discover -s clinical/tests -p test_ceftriaxone_sepsis_safety.py -v
```

## Comparación estructural y revisión independiente

| Comprobación | Resultado |
|---|---|
| Catálogo canónico | 23 entradas; las 22 ajenas al objetivo y los metadatos superiores se conservan. |
| Catálogo por síndrome | 11 entradas; las 10 ajenas al objetivo y los metadatos superiores se conservan. |
| Entradas objetivo | Una por catálogo, idénticas; coeficiente 80 y techo 4000 conservados. |
| Registro de evidencia | 131 IDs, todos los estados y fechas previas preservados; solo se añade revisión del componente de sepsis pediátrica. |
| Pendientes | 65 registros existentes intactos y un registro añadido. |
| Módulo clínico | Cambios limitados a `pediatric-sepsis`; las demás secciones permanecen iguales. |
| Pruebas previas | Solo cambian los cuatro métodos indicados; el AST restante de `test_skill.py` es idéntico. |
| Contratos y API aguda | `acute_medication_contracts.py` y `acute_medication_api.py` idénticos byte a byte; 19 valores únicos de `block_reason` conservados por inspección del AST. |

Una revisión independiente del contenido corrigió la ambigüedad entre la recomendación ponderal y la selección adulta a partir de 50 kg. La revisión independiente del código detectó dos huecos: concentración añadida capaz de producir mL y edad posmenstrual incoherente. Ambos fueron corregidos, cubiertos por casos adversarios y releídos con resultado PASS focal. Estas revisiones no equivalen a aceptación clínica formal.

## Límites y siguiente integración

La conciliación de fuente y edad está implementada en este componente. Falta aceptar/integrar el candidato dentro del flujo del proyecto y comprobar los consumidores que deban proporcionar el nuevo contexto. No se realizaron pruebas de interfaz, despliegue, validación en la instalación local del propietario ni QA global. El RCM de la presentación realmente disponible, su preparación y el protocolo local siguen siendo decisiones del circuito clínico/farmacéutico correspondiente.

El arreglo de la unidad de salida de este ID no cierra el hallazgo general `GMA-P1-001` para el resto del sistema. Tampoco modifica `GMA-P1-002`, `GMA-P1-003` ni los 19 contratos bloqueados.
