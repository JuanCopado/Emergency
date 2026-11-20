# Nota clínica · corrección de procedencia · 20/11/2026

**Identificador:** `NOTE-PROVENANCE-20261120`, versión 1. **Alcance:** referencias canónicas emitidas por el motor determinista de nota clínica. **Estado clínico:** `CLINICALLY_PENDING`.

La lectura inicial corresponde a `21defd4efc4f1b6d15ddb28c655772ca3e4b8a0c`. La implementación parte de `e7c5722045852d654f756d5f3928d4c14daf2dbf`, árbol `b49ea28981e84f234a90aa2095ac5bbebb4ef92d`; los archivos de motor, reglas, auditor y pruebas afectados eran idénticos entre ambos commits antes de esta corrección. Esta entrega no modifica el registro de evidencia ni sus fechas o estados, ni supone aceptación clínica del razonador.

## 1. Problema confirmado

[`clinical_note_diagnostic_engine.py`](../scripts/clinical_note_diagnostic_engine.py), función `_candidate`, publicaba `source_modules: [rule["id"]]`. Ese ID identifica un **síndrome**: también lo utilizan la resolución de relaciones y `rule_hits`. De las 92 reglas, 18 tienen IDs de síndrome distintos de los módulos canónicos del proyecto. Usarlos como módulos fuente producía referencias no resolubles.

Las reglas no tenían `source_module` ni `source_modules` a nivel superior. Sí tenían `source_modules` en las sugerencias de pruebas y tratamiento, y el contrato de salida de candidatos ya incluye ese campo. Además, el tratamiento de `cardiogenic-shock` citaba `vasoactive-inotrope-therapy`, un nombre ausente del registro; el módulo existente es `vasoactive-inotrope-infusions`.

El auditor comprobaba módulos sin cobertura, pero no rechazaba referencias sobrantes o incorrectas en `source_modules`. Por ello, su PASS previo no demostraba que todas las referencias emitidas fueran canónicas.

**Reproducción previa:** 13 casos seleccionados de los bancos existentes y seis notas sintéticas para los otros síndromes, mediante llamadas reales a `analyze`, sin HTTP ni proveedor externo. Las 19 llamadas devolvieron `blocked: false`; entre sus salidas se observaron los 18 IDs de síndrome en `source_modules` y la referencia vasoactiva incorrecta. Los seis textos adicionales solo comprueban procedencia; no constituyen casos independientes de validación diagnóstica.

## 2. Cambio aplicado

Se añade un `source_modules` explícito a cada una de las 18 reglas. Su destino ya aparece en las sugerencias de la misma regla y existe en [`MODULES.md`](../MODULES.md) y el registro. `_candidate` copia esa lista; cuando no hay una lista explícita, conserva el ID de regla como fuente para los 74 síndromes cuyo ID ya es un módulo canónico. No se crean módulos, alias de registro ni diagnósticos nuevos.

Los IDs de síndrome, desencadenantes, pesos, umbrales, población, orden, textos de recomendaciones y relaciones `differential`/`must_not_miss` no cambian. Se corrige también el nombre de la referencia vasoactiva anidada.

| ID conservado del síndrome | Módulo fuente emitido después | Sección canónica que sustenta la correspondencia |
|---|---|---|
| `major-trauma` | `trauma-major-hemorrhage` | [`trauma-surgical.md`](../modules/trauma-surgical.md), trauma y hemorragia mayor |
| `traumatic-head-injury` | `traumatic-intracranial-mass-effect` | [`neurologic.md`](../modules/neurologic.md), lesión intracraneal traumática |
| `ectopic-pregnancy` | `obstetric-emergencies` | [`special-populations.md`](../modules/special-populations.md), amenazas obstétricas |
| `preeclampsia-eclampsia` | `obstetric-emergencies` | Misma sección, preeclampsia/eclampsia |
| `postpartum-hemorrhage` | `obstetric-emergencies` | Misma sección, hemorragia obstétrica y puerperio |
| `neutropenic-sepsis` | `hematology-oncology` | [`disposition-crosscutting.md`](../modules/disposition-crosscutting.md), urgencias hematológicas/oncológicas |
| `sickle-cell-acute-emergency` | `hematology-oncology` | Misma sección, complicaciones de enfermedad falciforme |
| `testicular-torsion` | `urologic-emergencies` | [`renal-metabolic.md`](../modules/renal-metabolic.md), urgencias urológicas |
| `acute-angle-closure-glaucoma` | `ophthalmology-emergencies` | [`disposition-crosscutting.md`](../modules/disposition-crosscutting.md), urgencias oftalmológicas |
| `ent-airway-emergency` | `ent-emergencies` | Misma familia, urgencias ORL con compromiso de vía aérea |
| `septic-arthritis-orthopedic` | `orthopedic-emergencies` | [`trauma-surgical.md`](../modules/trauma-surgical.md), articulación séptica |
| `self-harm-suicide-risk` | `suicide-risk` | [`special-populations.md`](../modules/special-populations.md), autoagresión y riesgo suicida |
| `acute-agitation-psychosis` | `psychiatric-emergencies` | Misma familia, agitación y urgencias psiquiátricas |
| `environmental-hypothermia` | `environmental-emergencies` | [`disposition-crosscutting.md`](../modules/disposition-crosscutting.md), hipotermia |
| `environmental-heat-illness` | `environmental-emergencies` | Misma sección, enfermedad por calor |
| `drowning-emergency` | `environmental-emergencies` | Misma sección, ahogamiento |
| `pyelonephritis-urologic-emergency` | `urologic-emergencies` | [`renal-metabolic.md`](../modules/renal-metabolic.md), infección y obstrucción urológica |
| `geriatric-delirium-emergency` | `geriatric-emergencies` | [`special-populations.md`](../modules/special-populations.md), evaluación geriátrica y enlace al módulo de delirium |

La referencia anidada `vasoactive-inotrope-therapy` pasa a `vasoactive-inotrope-infusions`, en [`cardiovascular.md`](../modules/cardiovascular.md). El texto de tratamiento de `cardiogenic-shock` permanece idéntico.

### Auditor de procedencia

[`audit_clinical_note_diagnostic_coverage.py`](../scripts/audit_clinical_note_diagnostic_coverage.py) añade `invalid_source_modules`. Comprueba las fuentes explícitas de los candidatos y las de cada sugerencia de pruebas/tratamiento: deben ser listas no vacías de IDs registrados. Un ID inexistente, una forma inválida o un ID de síndrome utilizado indebidamente como módulo fuente produce FAIL.

`differential` y `must_not_miss` conservan su tratamiento previo como identificadores de síndrome/enrutamiento. No se les impone la pertenencia al catálogo de módulos ni se modifican sus valores. Esta guarda es del auditor de configuración; no constituye un nuevo bloqueo clínico en `analyze`.

## 3. Ajuste exacto de expectativas de procedencia

Se cambian **12 valores de `expected_modules` en 12 casos de dos bancos diagnósticos**, más la expectativa de la copia funcional congelada de `major-trauma` en [`V1.44_DEMO_CASES.json`](V1.44_DEMO_CASES.json). Son **13 valores serializados en tres archivos**, correspondientes a 12 casos diagnósticos distintos; la copia funcional no aumenta el corpus de 60 casos. No cambia `expected_likely`, el texto de entrada, la edad, los hallazgos, las alternativas, las pruebas o los tratamientos esperados. Los otros tres bancos diagnósticos no se modifican.

| Banco | Caso | Antes | Después |
|---|---|---|---|
| `clinical-note-diagnostic-synthetic-cases.json` | `major-trauma` | `major-trauma` | `trauma-major-hemorrhage` |
| Mismo banco | `ectopic-pregnancy` | `ectopic-pregnancy` | `obstetric-emergencies` |
| Mismo banco | `preeclampsia` | `preeclampsia-eclampsia` | `obstetric-emergencies` |
| Mismo banco | `neutropenic-sepsis` | `neutropenic-sepsis` | `hematology-oncology` |
| Mismo banco | `sickle-cell` | `sickle-cell-acute-emergency` | `hematology-oncology` |
| Mismo banco | `testicular-torsion` | `testicular-torsion` | `urologic-emergencies` |
| Mismo banco | `acute-angle-closure` | `acute-angle-closure-glaucoma` | `ophthalmology-emergencies` |
| Mismo banco | `septic-arthritis` | `septic-arthritis-orthopedic` | `orthopedic-emergencies` |
| Mismo banco | `self-harm` | `self-harm-suicide-risk` | `suicide-risk` |
| `clinical-note-diagnostic-final-cases-b.json` | `heat-stroke` | `environmental-heat-illness` | `environmental-emergencies` |
| Mismo banco | `pyelo` | `pyelonephritis-urologic-emergency` | `urologic-emergencies` |
| Mismo banco | `geriatric-delirium` | `geriatric-delirium-emergency` | `geriatric-emergencies` |
| `V1.44_DEMO_CASES.json` | `major-trauma` (copia funcional del primer caso de esta tabla) | `major-trauma` | `trauma-major-hemorrhage` |

La copia funcional conserva su `id`, el `id` de entrada y `provenance: clinical-note-diagnostic-synthetic-cases.json#major-trauma`. Su entrada vuelve a ser exactamente igual al caso fuente. El cotejo del banco completo contra HEAD confirma que esta sustitución es el único cambio; los otros 19 casos permanecen idénticos.

La cobertura de módulos pasa de **115 a 116** al resolver la referencia vasoactiva. Quedan **15 módulos sin cobertura directa**, todos dentro de los permitidos por la política existente. La lista de excepciones permitidas sigue teniendo 16 entradas; una de ellas ya está cubierta y no debe sumarse otra vez al total. Las pruebas existentes se ajustan a ese resultado concreto y conservan una comparación exacta del conjunto restante, sin sustituirla por una comprobación más débil. El informe histórico de octubre no se reescribe.

`covered_or_routed` es una auditoría estática de referencias canónicas. **116 no significa 116 diagnósticos ejecutables ni mide rendimiento**: el registro de reglas sigue teniendo 92 síndromes y las relaciones clínicas conservan los límites descritos en la sección 5.

## 4. Verificación observada

Antes de modificar el producto se guardaron las 60 notas sintéticas construidas por los runners existentes y sus salidas reales con `apply_to_note=True`. Después se repitieron exactamente esas entradas con el motor modificado, sin mocks. La comparación recursiva excluyó únicamente claves llamadas `source_modules`, tanto en `assessment` como en la copia de la nota.

| Comprobación | Resultado |
|---|---|
| Nueva regresión antes de corregir | RED: siete pruebas, 52 fallos de subcasos y un error por ausencia del nuevo campo del auditor |
| Nueva regresión después de corregir | **7 pruebas PASS** |
| Igualdad de resultados reales anteriores y posteriores, salvo `source_modules` | **60/60 iguales**; cero diferencias clínicas |
| Casos con cambio de procedencia | 31/60; los demás 29 no cambian |
| Configuración de reglas, excluyendo únicamente `source_modules` | Igualdad completa: IDs, textos, desencadenantes, pesos y límites conservados |
| Runner diagnóstico general | **47/47 PASS**, sin errores |
| Runner de cierre | **8/8 PASS**, sin errores |
| Runner pediátrico | **5/5 PASS**, sin errores |
| Regresiones existentes de cobertura | **3 PASS**, incluido el caso de cierre que reutiliza ocho escenarios |
| Regresión funcional focal de `major-trauma` | RED: `fixture silently diverged from source`; GREEN: igualdad exacta con fuente, motor/API, expectativas, revisión y exportación JSON PASS |
| Auditor | PASS; 131 módulos, 92 reglas, 116 módulos cubiertos/enrutados, cero fuentes inválidas y cero módulos inesperadamente sin cobertura |

Los siete tests nuevos verifican resolución de procedencia, los 18 destinos explícitos, conservación de identidad y comportamiento, rechazo de fuentes desconocidas o IDs de síndrome en el lugar equivocado, rechazo de listas explícitas vacías y ausencia de alias mutables entre regla y resultado. La comparación permanente usa una copia en memoria de las reglas sin los nuevos metadatos; la comparación única anterior/posterior utiliza además las salidas del motor original guardadas antes de editar.

Comandos focales reproducibles desde la raíz:

```bash
python -B -m unittest discover -s clinical/tests -p test_clinical_note_provenance.py
python -B -m unittest discover -s clinical/tests -p test_skill.py -k v139_diagnostic_coverage
python -B clinical/scripts/run_clinical_note_diagnostic_cases.py
python -B clinical/scripts/run_clinical_note_diagnostic_closure_cases.py
python -B clinical/scripts/run_clinical_note_pediatric_routing_cases.py
python -B clinical/scripts/audit_clinical_note_diagnostic_coverage.py
```

La regresión funcional focal usa la misma comprobación de igualdad del runner y su función real `check_note`, sin ejecutar los otros 19 casos ni sustituir dependencias:

```bash
python -B - <<'PY'
import json
import sys
sys.path.insert(0, 'clinical/qa')
from run_functional_v144 import QA, check_note
bank = json.loads((QA / 'V1.44_DEMO_CASES.json').read_text(encoding='utf-8'))
entry = next(case for case in bank['cases'] if case['id'] == 'major-trauma')
source, source_id = entry['provenance'].split('#')
original = next(case for case in json.loads((QA / source).read_text(encoding='utf-8'))['cases'] if case['id'] == source_id)
assert original == entry['input'], 'fixture silently diverged from source'
assert entry['input']['expected_modules'] == ['trauma-major-hemorrhage']
print(json.dumps({'id': entry['id'], 'source_equality': 'PASS', **check_note(entry['input'])}, ensure_ascii=False))
PY
```

Los runners se ejecutaron también por sus funciones `run()` reales en la comparación. No se suman ejecuciones repetidas como casos independientes. No se ejecutan aquí suites globales, navegador, pruebas prospectivas ni un proveedor de interpretación de imagen.

## 5. Límites que permanecen

Esta corrección resuelve la procedencia indicada; no valida exactitud, calibración, sensibilidad ni seguridad clínica prospectiva. El motor conserva `evidence_against: []` y copia la lista configurada de datos discriminantes sin una comprobación general de presencia/ausencia. No se presenta como razonamiento clínico exhaustivo.

Las relaciones clínicas requieren su revisión propia. Por lectura, `must_not_miss` contiene referencias sin regla resoluble: `acute-chest-syndrome`, `arrhythmias-cardiac-arrest`, `pediatric-electrolyte-emergencies` y `traumatic-intracranial-mass-effect`. Las tres últimas sí son módulos registrados; `_resolve_rule` busca reglas de síndrome. No crean un candidato por esa relación cuando no hay regla correspondiente. Este comportamiento no cambia aquí y no se declara cerrado por corregir `source_modules`.

La decisión PR35 y el papel de Juan como único validador clínico se conservan. La revisión clínica del alcance definitivo de nota y la gobernanza de cualquier despliegue con datos reales siguen separadas de este resultado técnico. No se promueven módulos ni se repite una aceptación ya concedida; tampoco se declara `GO_RELEASE`.
