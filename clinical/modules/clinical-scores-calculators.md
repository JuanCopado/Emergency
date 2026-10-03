# Clinical Scores & Calculators — central registry

## clinical-scores-calculators

### Objetivo
Registro único reutilizable de escalas clínicas y fórmulas médicas para urgencias, emergencias, UCI, adultos y pediatría. **Ninguna escala o fórmula debe duplicarse en módulos de enfermedad**: los módulos clínicos deben llamar al ID canónico de este registro.

### Comportamiento obligatorio
- Cada herramienta muestra: **nombre, qué mide, para qué se usa, variables necesarias, resultado y breve interpretación**.
- Todos los campos introducidos manualmente son **editables** y el resultado se recalcula al cambiar un dato.
- Autocompletar solo datos explícitamente presentes en el caso/EHR/contexto; marcar su procedencia.
- Nunca inventar un dato faltante. Si falta un campo obligatorio, devolver `incomplete` y listar los campos pendientes.
- Conservar componentes además del total: por ejemplo GCS debe mostrarse como `GCS 10/15 = E3 V3 M4`.
- Respetar la naturaleza de cada herramienta: una regla como PECARN o Duke-ISCVID devuelve criterios/categoría, no una puntuación artificial.
- Mostrar unidad y versión/variante cuando importe (p. ej., QTc Bazett vs Fridericia, MELD-Na vs MELD 3.0).
- No interpretar una escala fuera de su población/indicación validada.
- Una escala apoya decisiones; no sustituye diagnóstico, imagen, juicio clínico ni protocolo local.

### Niveles
- **CORE**: accesible directamente y sugerible automáticamente desde el síndrome.
- **SPECIALIST**: disponible cuando el módulo específico la requiere.
- **LEGACY**: no activa; solo referencia histórica. Las herramientas legacy no forman parte del registro activo.

### Ejemplos de enrutamiento
- Ictus -> `nihss`, `aspects`, `modified-rankin`.
- AIT -> `abcd2` y, cuando se prefiera una estrategia contemporánea local, `canadian-tia-score`.
- Dolor torácico/SCA -> `heart`, `grace-2`, `timi-ua-nstemi`.
- FA -> `cha2ds2-vasc` o `cha2ds2-va` según guía + `has-bled`/alternativa seleccionada.
- TEP -> `wells-pe`, `perc`, `years-pe`, `pesi`/`spesi`, `hestia`.
- Sepsis adulto -> `sofa`, `news2`; `qsofa` solo como señal pronóstica/contextual, no como cribado único.
- Sepsis pediátrica -> `phoenix-sepsis` como criterio contemporáneo; `psofa`/`pelod2` como complementos UCI.
- TCE pediátrico -> `pecarn-head-injury`.
- HDA -> `glasgow-blatchford`, `aims65`, `rockall`.
- Neumonía -> `curb65`/`crb65`, `psi-port`.
- Pancreatitis -> `bisap`.
- Toxicología -> `rumack-matthew`, `hunter-serotonin`, `ciwa-ar`, `cows` según escenario.

### Salida estándar
```
Nombre: ABCD2
Qué mide: riesgo temprano de ictus después de AIT
Uso: estratificación de riesgo tras sospecha de AIT
Datos: edad, TA inicial, clínica, duración, diabetes
Resultado: 5/7
Interpretación: mostrar categoría/riesgo según la versión validada, con advertencia de que no sustituye imagen/etiología/protocolo
Procedencia: edad/TA/DM autocompletados; clínica/duración introducidos manualmente
```

### Registro y motor
- Catálogo canónico: `calculators/registry.json`.
- Motor determinista: `scripts/clinical_calculator.py`.
- Los módulos de enfermedad referencian IDs; no copian fórmulas ni tablas.
- Cualquier cambio de puntuación, umbral, población o versión debe modificar el registro/motor **una sola vez** y actualizar evidencia/QA.

### Seguridad de implementación
- NEWS2 debe reproducirse sin modificar la tabla oficial RCP.
- GCS debe conservar E/V/M por separado además del total.
- Phoenix Sepsis Score se aplica en niños con sospecha de infección; >=2 identifica sepsis según criterios Phoenix 2024.
- Escalas con componentes subjetivos (NIHSS, RASS, CPOT, C-SSRS, mRS, etc.) requieren entrada clínica explícita; no inferir componentes a partir de texto ambiguo.
- Fórmulas renales deben indicar ecuación y unidades. Cockcroft-Gault y eGFR CKD-EPI no son intercambiables para todos los fármacos.
- Fórmulas de infusión solo calculan aritmética con una dosis ya seleccionada/validada; no eligen por sí mismas el tratamiento.
