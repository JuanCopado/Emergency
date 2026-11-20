# ECG y POCUS · revisión focal de evidencia · 20/11/2026

Base examinada: `cdca8e34013bba891a1c49f5ea859f933fcbea63`, árbol `977ec9cd9443bf0e7a284de13e00f242ea80ef92`. Alcance: las secciones canónicas `ecg-image`, `pocus-image` y `ecg-pocus-integration`, con sus preámbulos. Esta es una revisión bibliográfica focal asistida por IA; no una medición del rendimiento diagnóstico. Conserva YELLOW, las fechas canónicas de 27/09/2026 y `CLINICALLY_PENDING`.

## Fuentes comprobadas y límites de acceso

Consulta: 20/11/2026. El enlace identifica el documento; el localizador delimita lo contrastado. No se extrapola la vigencia a otras recomendaciones del mismo documento.

| ID | Fuente primaria, versión y localizador | Acceso observado y alcance |
| --- | --- | --- |
| ECG-SBC-2022 | Samesima et al., Sociedade Brasileira de Cardiologia, guía de informes ECG, 08/09/2022, DOI [10.36660/abc.20220623](https://doi.org/10.36660/abc.20220623), [texto en PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9563889/), §§6.1.2 y 6.1.5.2 | Texto recuperado. Permite contrastar la identidad del epónimo y distinguirlo de los criterios ventriculares. No es una validación de fotografías ni del modelo. |
| ECG-PT-2017 | Santos et al., J Electrocardiol 2017;50:960–963, DOI [10.1016/j.jelectrocard.2017.07.009](https://doi.org/10.1016/j.jelectrocard.2017.07.009), [PMID 28807354](https://pubmed.ncbi.nlm.nih.gov/28807354/), resumen | Resumen primario recuperado; texto íntegro no revisado. Caso de aneurisma aórtico que ilustra la inespecificidad del signo. No se deduce sensibilidad o especificidad de un caso. |
| ECG-ACC-2022 | ACC, Expert Consensus Decision Pathway on Acute Chest Pain, DOI [10.1016/j.jacc.2022.08.750](https://www.jacc.org/doi/10.1016/j.jacc.2022.08.750), §5.2.1 y tabla 1 | Texto de esas secciones recuperado por índice del editor; apertura JACC 403 y PMC10691881 con comprobación de navegador. Contraste limitado a ECG y patrones de isquemia, sin revisar todo el itinerario. |
| ECG-ACS-2025 | ACC/AHA/ACEP/NAEMSP/SCAI, ACS Guideline 2025, DOI [10.1161/CIR.0000000000001309](https://www.ahajournals.org/doi/10.1161/CIR.0000000000001309), tabla «Initial In-Hospital Assessment…», recomendación 2 y texto de apoyo | Texto indexado del editor; apertura directa 403. Apoya repetir ECG ante sospecha persistente y que uno no diagnóstico no excluye SCA. No se presenta como revisión integral de la guía. |
| US-ACEP-2023 | ACEP, Ultrasound Guidelines, Ann Emerg Med 2023;82:e115–e155, DOI [10.1016/j.annemergmed.2023.06.005](https://doi.org/10.1016/j.annemergmed.2023.06.005), [PMID 37596025](https://pubmed.ncbi.nlm.nih.gov/37596025/) | Identidad bibliográfica comprobada. La página oficial requiere acceso de miembro; el PDF espejo devolvió 403. No se atribuye revisión completa de ACEP2023 a esta sesión. |
| US-LUNG-2021 | [ACEP Sonoguide, Lung](https://www.acep.org/sonoguide/basic/lung), 08/03/2021, «Lung Sliding» y técnica para neumotórax | Texto oficial recuperado: fenómeno dinámico y limitaciones de adquisición. Material docente profesional, separado de una guía nueva. |
| US-DVT-2020 | [ACEP Sonoguide, DVT](https://www.acep.org/sonoguide/basic/dvt), 18/08/2020, §III «Compression technique» y «Common Mistakes» | Texto oficial recuperado: compresión y posibilidad de error técnico. No se trasladan métricas de operadores humanos a Emergency. |
| US-CARDIAC-2020 | [ACEP Sonoguide, Cardiac](https://www.acep.org/sonoguide/basic/cardiac), 18/08/2020, «Anatomy», «Right Heart Strain» y «Pitfalls» | Texto oficial recuperado: evaluación durante el ciclo cardíaco, contexto clínico y límites del estudio focal. |
| PE-AHA-ACC-2026 | Guía conjunta de embolia pulmonar aguda en adultos 2026, DOI [10.1016/j.jacc.2025.11.005](https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005), tabla de imagen diagnóstica, recomendación 9 y explicación correspondiente | Texto indexado del editor. La ecocardiografía aislada no confirma ni descarta EP. Contraste de esa afirmación, sin nueva revisión de tratamiento ni extrapolación pediátrica. |

## Comparación y resultado

| Módulo | Comparación realizada | Resultado y siguiente requisito |
| --- | --- | --- |
| `ecg-image` | Calibración y trazado completo; ECG no diagnóstico; de Winter/Wellens; identidad de Peñaloza–Tranchesi | Se detecta una errata clínica concreta, `ECG-PT-20261120`, descrita abajo. Las fuentes ACC/AHA consultadas respaldan el carácter urgente de los patrones isquémicos y la ausencia de exclusión por ECG no diagnóstico. No se ha validado reconocimiento visual ni cada trastorno de conducción. |
| `pocus-image` | Imagen estática frente a movimiento cardíaco, deslizamiento pleural y compresión venosa; calidad y límites | Se conserva la abstención ante evidencia dinámica insuficiente. El contraste se limita a estas tres tareas. Un trazado M-mode o Doppler con eje temporal contiene información distinta de un único fotograma B-mode: la evidencia futura debe distinguir formatos y no atribuir evaluación de clips que no se han leído. Falta un banco independiente y criterios previos por tarea. |
| `ecg-pocus-integration` | Integración con contexto y límites para SCA/EP; datos discordantes | Conservación justificada del principio de no descartar síndromes graves por estudios normales o limitados. No se han contrastado aquí todos los diagnósticos mencionados ni medido rendimiento combinado. |

No se ha demostrado sustitución integral de las fuentes históricas. Los registros compuestos se mantienen identificados como pendientes de conciliación; este expediente aporta localizadores concretos para la revisión posterior. La aceptación del marco POCUS del 14/11 conserva su alcance y no se solicita de nuevo.

## ECG-PT-20261120 · errata candidata v1

**Hallazgo confirmado:** el módulo describe Peñaloza–Tranchesi mediante S profundas en V5–V6 y sobrecarga ventricular derecha. ECG-SBC-2022 sitúa el signo en la sección auricular y describe otro patrón; las ondas S mencionadas aparecen en su sección ventricular. Es una atribución clínica errónea, reproducida en el catálogo generado de la aplicación.

**Propuesta exacta en inglés, idioma del módulo:**

> **Peñaloza–Tranchesi sign (historical, indirect finding):** low-amplitude QRS in V1 with a marked amplitude increase in V2, described as an indirect sign of right atrial enlargement. It is nonspecific and does not establish chamber enlargement alone; correlate with lead placement, the full ECG and echocardiography.

La propuesta corrige identidad, cavidad y límites de un único epónimo. No introduce una regla dosificadora ni una vía de tratamiento. El caso ECG-PT-2017 respalda la cautela de inespecificidad; no aporta una estimación de rendimiento. No se declara que la guía brasileña sea obligatoria en todos los países: se utiliza por su definición explícita y contrastable, coincidente con la descripción del signo en el caso clínico de 2017.

Consumidores afectados: `clinical/modules/image-modalities.md`, sección `ecg-image`, y su proyección `app/src/data/generatedClinicalGuides.json`. Parche preparado: [ECG_PT_20261120.patch](../updates/candidates/ECG_PT_20261120.patch). No se aplica al contenido estable en esta entrega. La cola canónica `updates/pending-updates.json` registra la decisión pendiente. Las demás secciones y el estado del módulo se conservan.

**Pregunta clínica:** ¿Aprueba sustituir exclusivamente la definición de Peñaloza–Tranchesi de `ecg-image` por el texto de la propuesta v1 y regenerar su ficha en la aplicación, manteniendo YELLOW y `CLINICALLY_PENDING`? **SÍ / NO**.

**Respuesta del médico:** pendiente; fecha de aceptación: no registrada. La exigencia procede de `AGENTS.md`, decisión del propietario del 20/11/2026: solo su respuesta explícita acepta el alcance presentado. La solicitud general de continuar autoriza esta investigación y preparación, pero no se registra como respuesta a una propuesta que aún no había sido presentada.

## Comprobaciones y límites

La identidad del epónimo se cotejó en dos publicaciones primarias con alcances distintos. Se buscó su presencia en fuentes canónicas y en consumidores; se encontraron las dos ubicaciones descritas. En una copia aislada de la base se prepararon el texto y la proyección mediante el generador existente. Las cuatro pruebas `build-clinical-guides.node-test.mjs` pasan; los otros 130 módulos y todos los estados permanecen idénticos. `git apply --check --unidiff-zero clinical/updates/candidates/ECG_PT_20261120.patch` comprueba el parche sin aplicarlo. Las pruebas estructurales no demuestran exactitud diagnóstica.

No se han procesado imágenes de pacientes, enviado datos clínicos, inferido una cohorte ni atribuido al proyecto las cifras de precisión publicadas para ecografía realizada por personas. Las fechas vencidas siguen visibles hasta completar el alcance de revisión que representan y registrar la decisión clínica aplicable.

## Adenda de decisión médica · 20/11/2026

El propietario médico respondió expresamente «Si acepto el cambio» a la propuesta **ECG-PT-20261120 v1**, fechada en su mensaje a las 17:16:52 UTC. La aceptación se documenta en [ECG_PT_OWNER_APPROVAL_20261120.md](ECG_PT_OWNER_APPROVAL_20261120.md) y en la cola canónica. Se aplica exclusivamente la definición corregida en la guía y su proyección a la aplicación. Las menciones de «pendiente» anteriores son históricas; el módulo sigue YELLOW, su `last_checked` original no se renueva y el proyecto continúa CLINICALLY_PENDING.
