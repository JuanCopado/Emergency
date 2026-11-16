# Anafilaxia: contratos revisados de IM en menores de 6 meses y perfusión IV

**Revisión focal: 16/11/2026.** Contratos: `anaphylaxis-under6months` y `anaphylaxis-refractory`. Núcleo internacional, sin país u hospital obligatorios. Aplicar [la política de guías internacionales](international-guideline-policy.md); las fuentes se seleccionan por alcance y calidad, no por la ubicación del propietario.

## Aceptación y procedencia

Juan ha autorizado resolver estos contratos y ha declarado su validación clínica en esta sesión. La presente entrega registra esa aceptación del propietario; no inventa una firma independiente de Farmacia/Pediatría, una auditoría de existencias ni una evaluación prospectiva. El estado global `CLINICALLY_PENDING` se conserva. Los controles individuales que se describen abajo siguen siendo necesarios.

Base comunicada por coordinación: `062d890b4fc92369b83c87664bb4bb0205ccb33f`, repositorio `JuanCopado/Emergency`. Se reutilizó material de:

- `review/anaphylaxis-under6months-evidence-20261116` en `e9855dbd37409189757c94900ee03e06ef25af3d`: conciliación de fuentes, acta funcional, preflight de microvolumen y revisión de selección de aguja. Su aclaración final diferencia IM sin diluir de la dilución IV de 1 mg hasta 10 mL.
- `review/anaphylaxis-refractory-20261116` en `0bff44dded89ea9da7f178ddf526d44969586c9c`: conciliación C04 y anexo pediátrico/pruebas negativas. La receta de perfusión ya figura en el módulo con aceptación del propietario de 13/11/2026.

Esos antecedentes documentaban cálculos o escenarios aún bloqueados. No se convierten retrospectivamente sus casos `NOT_RUN` en pruebas superadas. Esta entrega añade cálculo y comprobaciones propias; la integración en API/UI y la publicación se verifican por coordinación. Las exigencias históricas de un centro concreto no se trasladan al núcleo internacional.

## Fuentes primarias y decisión

| Fuente | Versión y uso en esta entrega |
|---|---|
| [ERC Paediatric Life Support](https://www.erc.edu/media/03xnpjmj/gl2025-09-pls-e.pdf) | 2025, Resuscitation 215:110767; sección de anafilaxia, p. 20. Fuente principal de la pauta IM ponderal y reevaluación/repetición a 5 min. Población pediátrica desde el nacimiento hasta 18 años; la reanimación al nacimiento pertenece a otro algoritmo. |
| [WAO Anaphylaxis Guidance](https://www.worldallergyorganizationjournal.org/article/S1939-4551%2820%2930375-6/fulltext) | 2020; tratamiento agudo y tabla 6. Respalda 0,01 mg/kg y ausencia de contraindicación absoluta para adrenalina IM en anafilaxia. Aporta alcance internacional; su intervalo de 5–15 min no sustituye el intervalo de 5 min seleccionado de ERC. |
| [RCUK Emergency treatment of anaphylaxis](https://www.resus.org.uk/sites/default/files/2021-05/Emergency%20Treatment%20of%20Anaphylaxis%20May%202021_0.pdf) | Mayo de 2021; tabla de dosis IM, sección 6.6 y apéndice 3. Pauta completa seleccionada para el inicio de perfusión en adultos y niños; discrepancia de banda IM por edad conservada. |
| [Listado oficial RCUK](https://www.resus.org.uk/library/additional-guidance/guidance-anaphylaxis/emergency-treatment-anaphylactic-reactions) | Consultado 16/11/2026: sigue identificando mayo de 2021 como edición completa más reciente. Describe uso por profesionales dentro y fuera del hospital. |
| [RCUK Paediatric emergency algorithms & resources](https://www.resus.org.uk/sites/default/files/2026-02/RCUK%20Paediatric%20emergency%20algorithms%20and%20resources%20Feb%2026%20V6.pdf) | Febrero de 2026, versión 6. Mantiene los algoritmos de anafilaxia y señala revisión de anafilaxia prevista en 2026; no equivale a una nueva guía completa de anafilaxia. |
| [AEMPS: Adrenalina Basi 1 mg/mL, registro 89175](https://cima.aemps.es/cima/dochtml/ft/89175/FT_89175.html) | Ficha consultada 16/11/2026, §§4.2–4.3 y 6.6: confirma la pauta IM ponderal en menores de 6 meses y distingue la dilución IV. Es información de un producto, no una aprobación universal de cualquier preparación ni disponibilidad. |
| [DailyMed: Adrenalin, set b293ad8e…](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=b293ad8e-7055-4a95-a130-9d7d74f19eab) | Etiqueta actualizada 22/10/2026. Su preparación IV para hipotensión por shock séptico no recomienda salino solo y tiene condiciones propias. Demuestra por qué no se extrapolan diluyentes/plazos a otra indicación, concentración o producto. |
| [ASCIA Acute Management of Anaphylaxis](https://www.allergy.org.au/images/ASCIA_HP_Guidelines_Acute_Management_Anaphylaxis_October_2026.pdf) | Edición de octubre de 2026 localizada en la [página oficial](https://www.allergy.org.au/hp/anaphylaxis/acute-management-guidelines). Se registra para vigilancia: no se afirma conciliación íntegra de sus figuras ni se introduce una pauta procedente de ellas en este helper. |

Esta revisión es focal y no acredita concordancia con todas las guías, fichas o jurisdicciones. Los errores de extracción de símbolos en PDF no se trasladan a código: **0,01 mg = 10 microgramos**, nunca 10 mg.

## Contrato IM: selección, cálculo y controles

Ámbito: anafilaxia aguda diagnosticada por el profesional con compromiso ABC persistente, edad cronológica **0 a menos de 6 meses** y peso actual verificado. No diagnostica automáticamente anafilaxia ni cubre parada cardíaca o reanimación al nacimiento. Los neonatos/prematuros precisan valoración individual y ayuda adecuada sin retrasar el tratamiento necesario.

Se selecciona **10 microgramos/kg IM de adrenalina 1 mg/mL SIN DILUIR**, en cara anterolateral del tercio medio del muslo. El techo general ERC/WAO es 500 microgramos por dosis; no es un mínimo ni una dosis esperada en un lactante. La banda RCUK de **100–150 microgramos** para menores de 6 meses queda explícita como otra recomendación. No se promedian las pautas, no se impone 100 microgramos como suelo y no se sustituye el cálculo por una edad de referencia.

Para peso `W` en kg:

`microgramos = min(10 × W, 500)`; `mg = microgramos / 1000`; `mL IM = mg / 1 mg/mL`.

Ejemplo sintético: **5 kg → 50 microgramos → 0,05 mg → 0,05 mL**. No diluir a **0,1 mg/mL** para facilitar la medida: 1 mg hasta 10 mL pertenece a un circuito IV distinto. Tampoco usar la perfusión de 10 microgramos/mL como preparación IM.

La medición requiere intervalo de entrega, capacidad, incremento y exactitud del dispositivo verificados. Se calcula con `Decimal`; si el volumen exacto no puede representarse, se detiene ese cálculo operativo para revisar el método de medida. No se autoriza redondeo, dosis mínima, dilución alternativa ni un porcentaje de error tolerable inventado. Una graduación pequeña no prueba exactitud de entrega; el software no certifica un dispositivo.

`dose_phase=initial` no exige antecedentes ficticios. `repeat` exige recuento entero, dosis previa real en microgramos, pauta previa y minutos transcurridos. Se comprueba la dosis anterior según la fuente declarada, incluyendo una banda RCUK previa cuando corresponda; ello no cambia la pauta ponderal actual. Un antecedente fuera de esas dos pautas necesita conciliación, no se declara incorrecto clínicamente por desconocerse aquí.

La repetición habitual es a **5 min**, según evolución. Con un intervalo menor, el contrato devuelve **apoyo de decisión urgente sin dosis, volumen, concentración ni preparación**, incluso si se declara una decisión experta excepcional. El acta previa CLI-06/TC-09 pedía no bloquear la actuación urgente; se cumple manteniendo orientación y decisión médica individual, sin convertir esa regla de flujo en evidencia para una repetición numérica anticipada. No se acepta tiempo cero ni se generan dosis sucesivas automáticamente. Desde dos dosis previas se exige escalada experta activa; se permite continuar IM mientras se organiza una perfusión segura, pero no una repetición automática con la perfusión ya funcionando.

La casilla genérica de contraindicación absoluta se reemplaza por evaluación de riesgos. No debe interpretarse una contraindicación relativa o una preocupación por excipientes como razón automática para omitir adrenalina IM ante anafilaxia vital. Revisar producto, interacciones, comorbilidad, aguja, lugar de administración y monitorización tan pronto como sea posible.

## Contrato IV: inicio de anafilaxia refractaria

Selección: adultos o niños con **compromiso respiratorio/circulatorio persistente tras dos dosis IM adecuadas**. No basta contar dosis o persistencia de urticaria. Se introducen cantidades, pautas y tiempos de las dos últimas dosis; se comprueban edad/peso, orden temporal e intervalo. Si ambas dosis están separadas por menos de 5 min, se ofrece apoyo de decisión para conciliación urgente sin emitir dosis o velocidad de perfusión; una declaración de excepción no acredita por sí sola la pauta de la fuente. La separación de población adulta a partir de 18 años solo clasifica el formulario y no altera la fórmula.

Preparación seleccionada: **1 mg de adrenalina hasta volumen FINAL de 100 mL con NaCl 0,9% = 10 microgramos/mL**. Desde producto de 1 mg/mL se extrae 1 mL. Corregir volumen de fármaco y sobrellenado real; una bolsa nominal de 100 mL más 1 mL no demuestra volumen final de 100 mL. No sustituir por 1 mg/10 mL, 1 mg/1000 mL, otra masa/volumen equivalente o glucosa 5% sin una conciliación distinta.

El experto selecciona gravedad **moderada: 0,5 mL/kg/h** o **grave con hipotensión/hipoxia: 1 mL/kg/h**, conforme a los puntos iniciales descritos en RCUK. El contrato calcula el inicio; la titulación posterior es individual al menor efecto necesario. No inventa escalones ni un máximo universal. El equilibrio tras cambios puede tardar 5–10 min. Revisar y reducir/detener ante toxicidad significativa; vigilar extravasación. Los bolos IV, otros vasopresores y la retirada no forman parte de este cálculo inicial.

Para coeficiente inicial `R` en mL/kg/h:

`bomba mL/h = W × R`; `microgramos/h = bomba × 10`; `microgramos/min = microgramos/h / 60`.

Por kg, 0,5 mL/kg/h equivale exactamente a **0,083333… microgramos/kg/min**, y 1 mL/kg/h a **0,166666…**. No etiquetar el primero como 0,1 exacto. A 70 kg, inicio moderado: **35 mL/h = 350 microgramos/h = 5,833333… microgramos/min**. `dose` expresa microgramos/min totales; la tasa por kg figura separadamente. No se asigna duración finita ni se presenta la bolsa completa como dosis administrada.

Requisitos operativos: profesional experimentado presente, bomba capaz, línea dedicada cebada y permeable, manguito de PA en otro brazo, ECG/SpO2 continuos, PA al menos cada 5 min, inspección del acceso y respuesta a complicaciones. La solución se prepara para uso inmediato y requiere comprobar producto/diluyente/recipiente/luz/asepsia. Se comparan tiempo desde preparación y límite individual verificado; al alcanzar el límite no se emite el cálculo. **No existe una vida útil universal de 24 h**. La seguridad microbiológica y el tiempo de uso no se deducen de estabilidad fisicoquímica ni de la duración teórica de la bolsa.

Si no puede administrarse con seguridad la perfusión, continuar atención y adrenalina IM cuando esté indicada, con ayuda experta. La indisponibilidad de recursos no autoriza un bolo IV ni debe retrasar reanimación. El contrato no exige un hospital específico; exige capacidades presentes.

## Evidencia técnica de esta entrega

Ejecución observada: `python -m unittest discover -s clinical/tests -p test_acute_reviewed_anaphylaxis.py -v`: **21 pruebas, OK**. Incluye positivos inicial/repetición/perfusión, ausencia de mínimo, microvolúmenes, unidades, concentraciones erróneas, cronología, edad, datos faltantes/inactivos, pediatría, recursos, caducidad y resultados no finitos.

Los tres casos completos para API/navegador están en `BROWSER_ACCEPTANCE_CASES`, dentro de `clinical/tests/test_acute_reviewed_anaphylaxis.py`, con expectativas literales calculadas a mano. El dispositivo y el límite de 60 min de esos fixtures son declaraciones sintéticas, no productos certificados ni una recomendación de estabilidad. Estas pruebas no demuestran entrega física exacta, validación diagnóstica, seguridad prospectiva ni equivalencia regulatoria internacional.
