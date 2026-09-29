# Revisión focal — consensos tiroideos conjuntos 2026

Fecha: 27/09/2026  
Estado: propuesta v1.27; revisión clínica humana y verificación local pendientes.

## Alcance

Se comprobó el índice real del paquete v1.26 (93 IDs únicos; todos resuelven) y
se cargaron las secciones `thyroid-storm` y `myxedema-coma`. La búsqueda se limitó
a esas rutas; no se volvieron a redactar ni duplicar otros módulos.

## Tormenta tiroidea

Fuente nueva: Taylor et al. *Management of thyroid emergencies: joint consensus
statement on management of thyroid storm*. European Thyroid Journal 2026;15(4):
ETJ260043. DOI: [10.1530/ETJ-26-0043](https://doi.org/10.1530/ETJ-26-0043); texto
primario en [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13506520/). Consenso de
ETA, BTA, Society for Endocrinology y Welsh Endocrine and Diabetes Society.

Cambios propuestos en el módulo existente:

- Añadir la pauta del consenso de hidrocortisona: 100 mg IV una vez y luego
  50 mg cada 6 h, o 200 mg/24 h por bomba en HDU/UCI. Mantener visible, como pauta
  distinta de ATA 2016, la alternativa de 300 mg IV de carga y 100 mg cada 8 h.
  No combinar ambos esquemas; escoger uno con endocrinología/protocolo local.
- Conservar PTU 500–1.000 mg de carga, luego 250 mg cada 4 h, o metimazol
  60–80 mg/día como opciones no automáticas. Ante lesión hepática clínicamente
  significativa (p. ej., transaminasas >3 veces LSN o bilirrubina ascendente),
  considerar metimazol/carbimazol frente a PTU, salvo que un factor individual
  cambie la elección. El consenso no atribuye superioridad de mortalidad clara
  a PTU.
- Añadir monitorización de K tras glucocorticoides si existe riesgo de parálisis
  periódica tirotóxica; reevaluar si no hay estabilización en 24–48 h. Los
  coadyuvantes/rescates (colestiramina, litio, plasmaféresis, tiroidectomía) quedan
  bajo decisión experta, no como pasos rutinarios.
- Mantener la barrera existente: valorar gasto/función ventricular antes de
  beta-bloquear; evitar beta-bloqueo automático ante shock o fallo de bajo gasto.
  Mantener la secuencia explícita de tionamida antes del yodo según el esquema
  aplicado.

## Coma mixedematoso

Fuente nueva: Taylor et al. *Management of endocrine emergencies: joint consensus
statement for management of myxoedema coma*. European Thyroid Journal 2026;15(4):
ETJ260044. DOI: [10.1530/ETJ-26-0044](https://doi.org/10.1530/ETJ-26-0044); registro
PubMed [PMID 42466568](https://pubmed.ncbi.nlm.nih.gov/42466568/) y texto primario
[PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13452032/).

En los fragmentos terapéuticos primarios recuperados se recomienda levotiroxina
IV de carga 200–400 microgramos, con dosis menor en pacientes pequeños/ancianos o
con cardiopatía isquémica/arritmia significativa; y cobertura con hidrocortisona
100 mg IV seguida de 50 mg cada 6 h o 200 mg/24 h. Coincide con el esquema actual.
No se encontró base suficiente para fijar una dosis enteral de rescate cuando no
hay levotiroxina IV: se conserva la derivación urgente a endocrinología/farmacia,
sin inventar equivalencia oral/IV.

## Portugal y formulaciones

La revisión bibliográfica no confirma stock hospitalario, RCM portugués, estabilidad
de mezclas ni compatibilidad de perfusiones en Azores. No se revisó una norma DGS
individual; la limitación anterior del portal DGS (403) continúa registrada.

## Validación y límites

- Índice: 93 módulos únicos, 93/93 resuelven.
- Registro de evidencia: 93/93; 34 green, 59 yellow, 0 red.
- Pruebas unitarias: 58/58 pasan; validación estructural y cobertura de evidencia
  pasan.
- No se añadieron casos, métricas diagnósticas ni afirmaciones de validación
  clínica. Es un borrador de contenido basado en consensos, no una release
  instalada ni validada prospectivamente.

## Siguiente trabajo sin duplicar módulos

1. Completar revisión regimen-level de anticoagulación en `acute-mesenteric-ischemia`
   y proquinéticos/endoscopia en `upper-gi-bleeding`, ambos ya en cola.
2. Después crear rutas pediátricas específicas (lactante febril, bronquiolitis,
   crup, deshidratación/choque y estatus epiléptico pediátrico) en lugar de duplicar
   el módulo general `pediatric-emergencies`.
3. Reintentar verificación de una norma DGS concreta y comprobar RCM/disponibilidad
   portuguesa antes de marcar recomendaciones como locales.
