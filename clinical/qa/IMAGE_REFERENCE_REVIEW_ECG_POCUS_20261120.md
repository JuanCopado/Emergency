# ECG, POCUS e integración · revisión del contenido de referencia · 20/11/2026

## 1. Identidad y alcance de la decisión

Base clínica examinada: commit `21defd4efc4f1b6d15ddb28c655772ca3e4b8a0c`, árbol `d4b2eba6048fe8b8731bb991ad126c8058a9755a`. Preparación documental sobre `e7c5722045852d654f756d5f3928d4c14daf2dbf`, árbol `b49ea28981e84f234a90aa2095ac5bbebb4ef92d`; ese cambio de infraestructura no modifica los tres textos examinados. Fecha de consulta de las fuentes: **20/11/2026**. Esta fecha no renueva ningún `last_checked` del registro.

Se contrasta todo el contenido actualmente almacenado de **`ecg-image`**, **`pocus-image`** y **`ecg-pocus-integration`**. «Todo el contenido» significa sus instrucciones y afirmaciones breves, no una auditoría integral de cada guía citada, de todos los diagnósticos posibles o de la exactitud del sistema. La matriz identifica tanto el respaldo externo como las restricciones propias del proyecto y las inferencias de alcance.

El preámbulo de imagen conserva la obligación de acceder a los píxeles, registrar calidad/contexto, separar observado/inferido/no evaluable y abstenerse cuando falte lo requerido. Son contratos vigentes del proyecto: estas fichas no sustituyen su [módulo padre](../modules/clinical-images.md#clinical-image-interpretation), su revisión humana ni el informe formal o estudio completo pertinente.

**Resultado para decisión:** `ECG-REF-20261120 v1` e `ECG-POCUS-REF-20261120 v1` quedan preparados para aceptación del propietario en su alcance de referencia. `POCUS-REF-20261120 v1` incluye como condición material la aclaración exacta **POCUS-MODE-20261120 v1**, todavía candidata. No se registra aquí ninguna respuesta médica ni se modifica contenido clínico activo, semáforo o fecha. Se conserva **CLINICALLY_PENDING**.

| Módulo y texto canónico | Identidad del fragmento revisado |
| --- | --- |
| [`ecg-image`](../modules/image-modalities.md#ecg-image) | SHA-256 `4e55394d4a42830d1d2ee5d1ca7c5416b72854e9a89d16d3952fecfac27209cd` |
| [`pocus-image`](../modules/image-modalities.md#pocus-image) | SHA-256 `831d81da4b2a01d1ea643c397ac741539d3d537b5b829354a60c0e1fb8301087` |
| [`ecg-pocus-integration`](../modules/disposition-crosscutting.md#ecg-pocus-integration) | SHA-256 `94a6e4f786f4ca50c3243e66df1007dcfe0344cd170662bb68f015766d2f65c1` |

Los hashes incluyen el encabezado `##`, el contenido y los saltos de línea hasta el siguiente encabezado `##`, excluido. Permiten distinguir una aceptación de estos textos de futuras modificaciones.

## 2. Trabajo previo que se conserva

- La [revisión focal ECG/POCUS del 20/11](ECG_POCUS_EVIDENCE_FOLLOWUP_20261120.md) aporta fuentes, localizadores y la discrepancia del epónimo. Esta revisión amplía sus huecos de alcance: técnica ECG, arritmias, documentación ecográfica, aorta y taponamiento.
- **ECG-PT-20261120 v1 ya está aceptado y aplicado.** La [aceptación del propietario](ECG_PT_OWNER_APPROVAL_20261120.md) registra su respuesta explícita; PR47 incorporó la definición corregida. Se revisa el texto resultante. No se vuelve a pedir esa decisión ni se propone otro cambio del epónimo.
- El [marco POCUS aceptado el 14/11](POCUS_FRAMEWORK_OWNER_ACCEPTANCE_2026-11-14.json) conserva su alcance: pregunta focal, adquisición, calidad, documentación, límites e integración. No se atribuye automáticamente esa aceptación a `pocus-image` ni se repite la pregunta del marco general.
- La separación entre referencia, exactitud y despliegue, los diez módulos y el trabajo real previo PTB-XL/E1 se detallan en [IMAGE_VALIDATION_CLOSURE_20261120.md](IMAGE_VALIDATION_CLOSURE_20261120.md). Es el mapa complementario de este expediente.

## 3. Fuentes y acceso efectivamente comprobado

Los localizadores delimitan lo utilizado. «Indexado» significa que se recuperó texto del editor mediante su índice, aunque la apertura directa estuviera bloqueada. No equivale a haber descargado y revisado íntegramente esa guía. Los casos clínicos sirven para contrastar descripción o nomenclatura; no aportan aquí estimaciones de rendimiento. Sonoguide es material docente oficial de ACEP, no una nueva guía de práctica clínica de 2026.

### 3.1 ECG

| ID | Fuente, versión y localizador | Acceso y función en esta revisión |
| --- | --- | --- |
| E1 | Samesima et al., SBC, *Guideline on the Analysis and Issuance of Electrocardiographic Reports*, 2022, DOI [10.36660/abc.20220623](https://doi.org/10.36660/abc.20220623); [texto bilingüe PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9563889/), §§1.2.1–1.2.3, 2.1.1–2.1.3 y 6.1.2 | Texto recuperado. Análisis sistemático, calibración, electrodos, interferencias y signo auricular. Se utiliza por su contenido explícito; no se impone una norma nacional brasileña al proyecto internacional. |
| E2 | ACC, *Expert Consensus Decision Pathway on Acute Chest Pain*, 2022, DOI [10.1016/j.jacc.2022.08.750](https://www.jacc.org/doi/10.1016/j.jacc.2022.08.750), tabla 1 y §§5.2.1–5.2.2 | Texto indexado del editor; apertura directa 403. Patrones de Winter/Wellens, riesgo isquémico, comparación y ECG seriados. |
| E3 | ACC/AHA/ACEP/NAEMSP/SCAI, ACS Guideline 2025, DOI [10.1161/CIR.0000000000001309](https://www.ahajournals.org/doi/10.1161/CIR.0000000000001309), §§3.1.1–3.1.2 y tabla 3 | Texto indexado. ECG inicial no diagnóstico, repetición según sospecha/evolución y ecocardiografía urgente cuando procede. No se revisan aquí todas las recomendaciones de tratamiento. |
| E4 | de Winter et al., *A New ECG Sign of Proximal LAD Occlusion*, NEJM 2008;359:2071–2073, DOI [10.1056/NEJMc0804737](https://www.nejm.org/doi/abs/10.1056/NEJMc0804737), descripción inicial y figura 1 | Texto original indexado oficial; apertura 403. Fuente histórica del descriptor **1–3 mm** ya almacenado. Su interpretación actual se contrasta con E2/E3. |
| E5 | Lutz, Mullen y Litwin, *Flash Pulmonary Edema in a 70-Year-Old Man*, Circulation 2021;143:1331–1334, DOI [10.1161/CIRCULATIONAHA.121.053333](https://www.ahajournals.org/doi/pdf/10.1161/CIRCULATIONAHA.121.053333), respuesta y figuras 2, 3 y 5 | PDF oficial recuperado. Caso original que explicita la nomenclatura A/B y el contexto clínico de Wellens; no sustituye E2/E3 como guía de actuación. |
| E6 | AHA/ACC y sociedades colaboradoras, Chest Pain Guideline 2021, resumen ejecutivo, DOI [10.1016/j.jacc.2021.07.052](https://www.jacc.org/doi/10.1016/j.jacc.2021.07.052), tabla 4 | Tabla indexada oficial; apertura 403. Contraindicaciones de pruebas de estrés en SCA activo/angina inestable de alto riesgo. |
| E7 | ISHNE–HRS, consenso sobre ECG ambulatorio y monitorización externa, 2017, [PMC6931745](https://pmc.ncbi.nlm.nih.gov/articles/PMC6931745/), resumen y §1 | Texto recuperado. Respalda el límite temporal del ECG convencional ante arritmias intermitentes. No se incorpora una indicación nueva de dispositivo o duración de monitorización. |
| E8 | [RCUK Adult Advanced Life Support Guidelines](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/adult-advanced-life-support-guidelines), edición 2025, «Peri-arrest arrhythmias», «Tachycardia» y «Bradycardia» | HTML oficial recuperado; coincide con la fuente de referencia ya conciliada de `adult-arrhythmias`. Se utiliza para prioridad clínica, sin trasladar dosis o nuevas reglas. |
| E9 | [RCUK Special Circumstances Guidelines](https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/special-circumstances-guidelines), edición 2025, «Hyperkalaemia» | HTML oficial recuperado. Respalda la urgencia de alteraciones ECG en el contexto de hiperpotasemia. No se modifica el módulo ni el contrato farmacológico de potasio. |
| E10 | Santos et al., J Electrocardiol 2017;50:960–963, DOI [10.1016/j.jelectrocard.2017.07.009](https://doi.org/10.1016/j.jelectrocard.2017.07.009), [PMID 28807354](https://pubmed.ncbi.nlm.nih.gov/28807354/), resumen | Reutilización del resumen primario comprobado en el expediente del 20/11; texto íntegro no revisado. Sustenta la cautela de inespecificidad del signo Peñaloza–Tranchesi, ya aceptada. |

### 3.2 POCUS y documentación

| ID | Fuente, versión y localizador | Acceso y función en esta revisión |
| --- | --- | --- |
| U1 | [ACEP Sonoguide, Physics and Technical Facts for the Beginner](https://www.acep.org/sonoguide/basic/ultrasound-physics-and-technical-facts-for-the-beginner), 16/07/2020, §§II–VI, figura 2 | HTML oficial recuperado. Modos B/M/Doppler, artefactos, orientación, maniobras y controles del equipo. |
| U2 | [ACEP Sonoguide, Lung](https://www.acep.org/sonoguide/basic/lung), 08/03/2021, §II «Lung Sliding», figura 8 | HTML oficial recuperado. Contraste focal del fenómeno temporal y de su representación M-mode. |
| U3 | [ACEP Sonoguide, Echocardiography for Emergency Physicians](https://www.acep.org/sonoguide/basic/cardiac), 18/08/2020, §§II–III, «Effusion, Trauma, and Tamponade» y §V | HTML oficial recuperado. Ventanas, secuencias cardíacas, contexto y limitaciones. No se adoptan sus estimaciones publicadas de precisión como resultados de Emergency. |
| U4 | [ACEP Sonoguide, DVT](https://www.acep.org/sonoguide/basic/dvt), 18/08/2020, §III «Compression technique», «Respiratory variation/phasic flow» y «Pearls and Pitfalls» | HTML oficial recuperado. Compresión, registro temporal y errores de adquisición; necesidad de consulta/imagen adicional ante incertidumbre. |
| U5 | [ACEP Sonoguide, Small Parts — Testicular Ultrasound](https://www.acep.org/sonoguide/advanced/testicular), 01/04/2025, §III, párrafos de ajustes Doppler | HTML oficial recuperado. Ejemplo técnico explícito de dependencia del flujo visible respecto a ajustes y modos. Su aplicación aquí es el límite de un único fotograma color; no un algoritmo nuevo de torsión. |
| U6 | AIUM, *Practice Parameter for Documentation of an Ultrasound Examination, 2025 Revision*, publicado 10/01/2026, J Ultrasound Med 45:E26–E29, DOI [10.1002/jum.70168](https://onlinelibrary.wiley.com/doi/10.1002/jum.70168), «Requirements for the Ultrasound Examination», «Final Report…» y «Reporting of Critical Results» | Texto íntegro abierto del editor. Registro recuperable, estática/cine según tarea, orientación, examen incompleto y comunicación. Se adopta como respaldo documental; no se importan plazos, identificadores o requisitos legales estadounidenses a la configuración local. |
| U7 | ACEP, *Ultrasound Guidelines*, Ann Emerg Med 2023;82:e115–e155, DOI [10.1016/j.annemergmed.2023.06.005](https://doi.org/10.1016/j.annemergmed.2023.06.005), [PMID 37596025](https://pubmed.ncbi.nlm.nih.gov/37596025/) | Identidad y revisión previa del marco POCUS conservadas. El PDF oficial actual redirige a acceso de miembro. No se afirma una nueva lectura íntegra; U1–U6 aportan los localizadores accesibles para el texto almacenado. |

### 3.3 Límites de integración

| ID | Fuente, versión y localizador | Acceso y función en esta revisión |
| --- | --- | --- |
| I1 | AHA/ACC y sociedades colaboradoras, Acute Pulmonary Embolism Guideline 2026, DOI [10.1016/j.jacc.2025.11.005](https://www.jacc.org/doi/10.1016/j.jacc.2025.11.005), §3.1.2, recomendación 9 y texto de apoyo | Texto indexado oficial recuperado; apertura 403. La versión recuperada enlaza una corrección y conserva explícitamente el límite diagnóstico del ecocardiograma aislado. La [fe de erratas de agosto de 2026](https://pubmed.ncbi.nlm.nih.gov/42583992/), DOI 10.1016/j.jacc.2026.06.033, se identifica bibliográficamente; su cuerpo no fue accesible. No se afirma haber revisado todo su contenido ni otros cambios de la guía. |
| I2 | ACC/AHA, Aortic Disease Guideline 2022, DOI [10.1161/CIR.0000000000001106](https://doi.org/10.1161/CIR.0000000000001106), [PMC10784847](https://pmc.ncbi.nlm.nih.gov/articles/PMC10784847/), §7.2 «AAS: Diagnostic Evaluation» | Tabla y explicación recuperadas por índice; apertura AHA 403 y PMC con comprobación de navegador. Delimita el papel del estudio focal frente a TC, ETE o RM seleccionadas según sospecha/contexto. |
| I3 | ESC, Myocarditis and Pericarditis Guidelines 2025, DOI [10.1093/eurheartj/ehaf192](https://doi.org/10.1093/eurheartj/ehaf192), §11.8.2 y tabla 17 | Texto indexado del editor recuperado; apertura directa no accesible. Diagnóstico clínico de taponamiento con confirmación ecocardiográfica y características de sus signos. No se revisan aquí drenaje ni tratamiento. |

## 4. Matriz de `ecg-image`

| Afirmación/instrucción almacenada | Contraste y reconciliación | Resultado para referencia |
| --- | --- | --- |
| Trazado de doce derivaciones, calibración, velocidad, etiquetas, línea de base y perspectiva | E1 §§1.2 y 2 sustenta la adquisición identificable y el control técnico; E2/E3 utilizan ECG de doce derivaciones. Verificar velocidad y distorsión antes de medir es una condición de lectura del proyecto, no una capacidad de corregir fotografías validada por estas guías. | Conservar. Si falta información, explicitarla; no inferir que la fotografía permite una medición exacta. |
| Ritmo, frecuencia aproximada, eje, conducción, intervalos y ST–T; no inventar QTc/intervalos | E1 §1.2.1 enumera los componentes del análisis; §1.2.3 exige verificar las mediciones automáticas. El límite ante recorte, borrosidad o falta de escala procede además del contrato de entrada y abstención del proyecto. | Conservar. No se introduce un método de medición, fórmula o umbral nuevo. |
| Consistencia de derivaciones, inversión y artefacto | E1 §§2.1.2–2.1.3 identifica errores de electrodos e interferencias que pueden simular enfermedad. | Conservar como paso previo de calidad. |
| Urgencia de isquemia, arritmia maligna, bloqueo avanzado e hiperpotasemia | E2/E3 respaldan el riesgo isquémico; E8 diferencia arritmias con compromiso y bloqueos relevantes; E9 aborda los cambios ECG de hiperpotasemia. «Time-sensitive» exige valoración contextual, no que cualquier morfología aislada dicte automáticamente tratamiento. | Conservar; el módulo no contiene una pauta terapéutica que deba añadirse o recalcularse. |
| Un ECG no diagnóstico no excluye SCA ni arritmia | E3 respalda explícitamente la primera parte. E7 explica que la arritmia intermitente puede no registrarse en el ECG convencional: esta es la interpretación de la segunda parte, no una afirmación de que ningún ECG pueda diagnosticar una arritmia presente. | Conservar con ese alcance temporal. |
| de Winter: morfología, distribución, asociación LAD y activación urgente | E4 aporta el descriptor histórico 1–3 mm; E2, tabla 1, usa depresión ascendente en J >1 mm con T prominentes y reconoce la urgencia. Son descripciones compatibles: el «typically» almacenado no convierte 3 mm en techo de exclusión. E3 mantiene la valoración de oclusión sin depender solo de elevación clásica del ST. | Conservar el texto y las cifras existentes; no añadir una regla binaria de elegibilidad. |
| Wellens: T bifásica A/inversión simétrica B, V2–V3 y extensión posible, ST poco alterado, angina reciente/ausencia de dolor, riesgo LAD | E2 tabla 1 y E5, figuras 2/3/5, sustentan morfología, nomenclatura y contexto. «Suggests» expresa sospecha; no demuestra por sí solo anatomía coronaria ni excluye imitadores. | Conservar. La denominación A/B está descrita en la fuente, sin asignar porcentajes diagnósticos al producto. |
| Wellens: valoración cardiológica urgente y no prueba de estrés | E2/E3 sitúan los patrones isquémicos de alto riesgo fuera de una tranquilización por ausencia de elevación clásica; E6 contraindica estrés en SCA activo/angina inestable de alto riesgo. Aplicarlo a una sospecha clínica de Wellens es una **inferencia clínica explícita y concordante**, no una cita literal de Wellens en esa tabla. | Conservar la precaución; no extenderla a toda inversión inespecífica de T. |
| Peñaloza–Tranchesi: patrón auricular indirecto, inespecificidad y correlación | E1 §6.1.2 y E10 son las fuentes de la corrección ya aprobada. Se conserva la cautela sobre colocación, ECG completo y ecocardiografía. | Revisión del contenido aplicado, sin reabrir ECG-PT ni atribuir sensibilidad/especificidad. |

No queda una nueva discrepancia material identificada en este texto para resolver antes de su decisión de referencia. Esta conclusión se limita a las afirmaciones examinadas y no certifica reconocimiento visual, QTc automático ni sensibilidad para las urgencias enumeradas.

## 5. Matriz de `pocus-image`

| Afirmación/instrucción almacenada | Contraste y reconciliación | Resultado para referencia |
| --- | --- | --- |
| Órgano, plano, sonda, orientación, profundidad, ganancia, foco, Doppler y formato | U1 §§II, IV–VI y U3 §III permiten identificar los elementos técnicos; U6 exige documentación apta para revisión. El proyecto solo debe declarar los datos conocidos o visibles. | Conservar. No inferir configuración ausente. |
| Ecogenicidad, bordes, líquido, artefactos, sombra/refuerzo y cálipers visibles | U1 §§II–III describe esos componentes; U6 incluye hallazgos y mediciones pertinentes. Describir un cáliper visible no valida su colocación o la medida. | Conservar como descripción de lo suministrado. |
| Una «still» no prueba fenómenos dinámicos | U1 §II y U2 muestran que M-mode conserva tiempo en una imagen. La palabra «still» sin distinguir modo es demasiado amplia. U3/U4 sustentan las secuencias necesarias para evaluación cardíaca, compresión y variación respiratoria. | **Aclaración candidata POCUS-MODE-20261120 v1**, abajo. El texto actual no recibe una conformidad sin esa reconciliación. |
| Un fotograma color no demuestra ausencia de flujo | U1 §II distingue modos; U5 §III muestra dependencia de ajustes y comprobación con Doppler apropiado. La abstención general es una inferencia conservadora sobre evidencia insuficiente; no declara que un examen Doppler completo sea inútil. | Conservar, sin incorporar un protocolo vascular o de torsión nuevo. |
| Pregunta binaria, vistas/maniobra mínimas y declaración de si se aportaron | U3 §III, U4 §III y U6 documentan secuencias, vistas y componentes ausentes. El conjunto necesario depende de la tarea: no se fija aquí un número universal de imágenes. | Conservar. No atribuir una maniobra que no se ha examinado. |
| Estudio limitado no excluye un síndrome grave; escalar cuando supera el alcance focal | U3 §V, U4 «Pearls and Pitfalls» e I1–I3 justifican límites y alternativas según el problema. Es una regla de prudencia ante un examen insuficiente, no un estimador del valor predictivo negativo del producto. | Conservar con contexto clínico y alcance de cada prueba. |
| Conservar imágenes/clips | U6 exige un registro recuperable y admite estática o cine según examen. El proyecto debe aplicar además su propia autorización, minimización y custodia. | Conservar; no interpretar «preserve» como almacenamiento indefinido, subida automática o permiso para datos identificables. |

### POCUS-MODE-20261120 v1 · texto exacto aún no activado

**Antes**, tercer párrafo canónico:

> A still cannot prove lung sliding, compressibility, respiratory variation, valve motion, ejection fraction or dynamic response. One color-Doppler frame cannot establish absent flow.

**Después propuesto**, idéntico al candidato del mapa de cierre:

> A single static B-mode frame cannot establish lung sliding, compressibility, respiratory variation, valve motion, ejection fraction or dynamic response. An M-mode tracing of the pleural line contains temporal information along the sampled line; assess only the acquisition, location and recorded interval actually shown, with an identifiable time axis. It does not establish that a complete cine or compression sequence has been reviewed. One color-Doppler frame cannot establish absent flow.

Fuente específica de la aclaración: U2, §II «Lung Sliding», figura 8; corroboración física U1, §II, figura 2. La propuesta no afirma que Emergency procese cine, no habilita vídeo ni permite convertir una línea M-mode en un examen completo. No incorpora umbrales diagnósticos. La afectación prevista se limita al párrafo canónico y a su proyección generada en la aplicación.

## 6. Matriz de `ecg-pocus-integration`

| Afirmación/instrucción almacenada | Contraste y reconciliación | Resultado para referencia |
| --- | --- | --- |
| Pregunta clínica y probabilidad previa; registro ECG y hallazgos cardíacos/pulmonares/vasculares focales | E1/E2, U2–U4 e I1 §3.1.2 respaldan la lectura orientada por la pregunta. Es un esquema de integración, no una combinación matemática validada ni un algoritmo único para todos los síndromes. | Conservar, sin añadir pesos, puntuación o probabilidades automáticas. |
| Conciliar datos discordantes y repetir según intervención o cambio clínico | E2/E3 respaldan comparación y repetición ante evolución; U6 documenta comparación, limitaciones y discrepancias. La frase se interpreta como reevaluación **pertinente a la pregunta y al cambio**, sin imponer repetir todas las pruebas después de cualquier intervención. | Conservar; explicitar incertidumbre y alternativas cuando los datos no concuerdan. |
| Estudios normales/limitados no excluyen SCA | E3: el ECG no diagnóstico no excluye SCA. Una imagen focal sin alteraciones no sustituye la evaluación clínica/analítica y el itinerario aplicable. Esta segunda parte es una inferencia de alcance, no una cifra de sensibilidad del sistema. | Conservar para ECG/POCUS focal. |
| No excluyen EP | I1 §3.1.2, recomendación 9, lo establece para ecocardiografía aislada. | Conservar; no se extiende a decir que una prueba dedicada adecuada nunca pueda excluir EP. |
| No excluyen enfermedad aórtica | I2 §7.2 distingue pruebas diagnósticas y señala ventajas de ETE frente a ETT. Inferencia explícita: un ECG o barrido focal normal no sustituye el estudio indicado ante sospecha de síndrome aórtico. | Conservar; no convertir la cautela en descalificación de TC/ETE/RM completas. |
| No excluyen taponamiento inicial | I3 §11.8.2/tabla 17 exige integración clínica y ecocardiográfica; U3 §V insiste en el contexto. «Early» no define un estadio ni un umbral operativo aquí: un estudio focal normal o limitado no garantiza ausencia de un proceso incipiente/evolutivo. | Conservar como cautela contextual, no como autorización para diagnosticar taponamiento sin evidencia adecuada. |
| Otros síndromes graves; límites técnicos y alternativas | No es una lista exhaustiva de enfermedades ni un rendimiento universal. Es la restricción del proyecto frente a muestreo insuficiente, compatible con U6 y con los ejemplos específicos anteriores. | Conservar el alcance abierto sin declarar validadas patologías adicionales. |

## 7. Fichas de decisión médica SÍ / NO

La [política de revisión humana](final-human-review-policy.json) y la [política de actualizaciones](../references/update-policy.md) requieren que la aceptación corresponda al módulo y al expediente concretos. Las preguntas siguientes quedan **preparadas, sin respuesta registrada**. Su aceptación permitiría documentar el cierre del alcance bibliográfico correspondiente; no constituye validación diagnóstica, piloto, autorización asistencial ni GO_RELEASE. La aplicación de cualquier cambio y su comprobación posterior deben quedar trazadas antes de actualizar el registro.

### ECG-REF-20261120 v1 · `ecg-image`

**Contenido propuesto:** aceptar la conciliación de las nueve filas de §4 sobre el texto identificado en §1, incluida la corrección ECG-PT ya aplicada. No se propone otra modificación clínica. Se conserva la abstención ante calidad insuficiente y la distinción entre descripción de patrones y confirmación diagnóstica.

**Pregunta:** ¿Aprueba **ECG-REF-20261120 v1** como cierre de la revisión de referencias del contenido actual de `ecg-image`, con los alcances y límites documentados, sin atribuir rendimiento diagnóstico al sistema? **SÍ / NO**.

### POCUS-REF-20261120 v1 · `pocus-image`

**Contenido propuesto:** aceptar las siete filas de §5 **incluyendo expresamente la sustitución del tercer párrafo por POCUS-MODE-20261120 v1**. El cierre de referencia requiere que esa misma versión quede aplicada y su proyección comprobada; el texto actual ambiguo no se da por corregido. Esta ficha reúne la decisión bibliográfica y su única corrección material para que no haya una aprobación implícita de otro texto.

**Pregunta:** ¿Aprueba **POCUS-REF-20261120 v1**, incluida la aclaración exacta **POCUS-MODE-20261120 v1** de §5, para cerrar la revisión de referencias tras su aplicación comprobada, manteniendo los límites de formato, alcance focal y rendimiento no validado? **SÍ / NO**.

### ECG-POCUS-REF-20261120 v1 · `ecg-pocus-integration`

**Contenido propuesto:** aceptar las siete filas de §6 sobre el texto identificado en §1. Se mantienen integración contextual, reevaluación pertinente y alternativas; las limitaciones de un estudio focal no se extrapolan a todas las pruebas diagnósticas completas.

**Pregunta:** ¿Aprueba **ECG-POCUS-REF-20261120 v1** como cierre de la revisión de referencias de `ecg-pocus-integration`, con esta delimitación de alcance y sin afirmar rendimiento combinado validado? **SÍ / NO**.

## 8. Pendientes que estas fichas no cierran

| Capa | Evidencia reutilizable y pendiente real |
| --- | --- |
| Referencia | Queda la decisión explícita sobre las tres fichas y, para POCUS, la aplicación y verificación de la versión exacta aceptada. La corrección ECG-PT y el marco POCUS de 14/11 ya tienen sus decisiones y no se vuelven a solicitar. |
| Exactitud ECG | Existe el [resultado real PTB-XL natural500](results/PTBXL_NATURAL500_V2_AFIB_BASELINE_V1_RESULT.json): es exploratorio tras revelar etiquetas y corresponde a una línea base concreta. No se declara inexistente ese trabajo ni se extrapola a fotografías, QTc, patrones isquémicos o al sistema completo. |
| Exactitud POCUS/integración | Para afirmar rendimiento por tarea se necesitan datos autorizados, referencia adjudicada, separación independiente y criterios fijados antes de ver resultados conforme a [IMAGE_VALIDATION_POLICY.md](IMAGE_VALIDATION_POLICY.md). No se inventa una cohorte, tamaño, umbral de éxito o resultado. No son requisitos nuevos para el mero contraste bibliográfico de este expediente. |
| Despliegue/piloto | La compatibilidad técnica, los ejemplos sintéticos y E1 no equivalen a un piloto clínico. Las afirmaciones generalizables requieren la validación prospectiva prevista en la política, además de la autorización, custodia y condiciones de uso aplicables. El módulo padre conserva su gate propio. |

## 9. Comprobación documental y límites

Se ha leído el texto canónico completo de los tres módulos y contrastado cada instrucción/afirmación en las matrices. Las fuentes inaccesibles o consultadas parcialmente quedan identificadas; no se atribuye una revisión integral a ACEP2023 ni a las guías extensas enlazadas. La búsqueda es focal sobre el contenido almacenado, no una revisión sistemática exhaustiva de toda la literatura.

Se han comprobado identidad de fragmentos, enlaces locales y formato del documento. No se ejecutaron suites clínicas, nuevas inferencias, benchmark ni pruebas de navegador para elaborar estas fichas. No se procesaron imágenes clínicas como casos de evaluación ni se transmitieron datos clínicos; se consultaron publicaciones. Ninguna métrica de publicaciones sobre operadores humanos se convierte en rendimiento de Emergency.
