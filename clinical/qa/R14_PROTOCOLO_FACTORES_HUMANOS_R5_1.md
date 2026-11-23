# R5-1 · evaluación de factores humanos de la elección de modalidad · protocolo (PROPUESTO)

**22 de noviembre de 2026 · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED)**

Prepara, **sin ejecutarla ni activar nada**, la capa 8 de la [política R5-1](R13_R5_1_POLITICA_SEGURIDAD_OCHO_CAPAS_v1.md) (`DEC-CLIN-R8-06A`): evaluación independiente con profesionales, imágenes sintéticas y medición del error humano residual. No hay sesiones realizadas, participantes ni resultados. R5-1 (P1) sigue abierto.

## Qué mide y qué no

- **Mide** el error humano al elegir la modalidad con las entradas del [prototipo inactivo](R13_R5_1_POLITICA_SEGURIDAD_OCHO_CAPAS_v1.md) (bandera `VITE_R51_PROTOTYPE=1`, solo en un entorno de evaluación).
- **No mide** rendimiento clínico, exactitud de ningún modelo ni utilidad diagnóstica. La confirmación humana no verifica el contenido de la imagen; este estudio cuantifica cuánto falla esa confirmación, no la sustituye.

## Material

- **Solo imágenes sintéticas.** Ningún dato de pacientes, ni siquiera anonimizado.
- Casos que la elección de modalidad debe resistir (propuestos): una fotografía de pantalla de ECG, de radiografía o de POCUS (la fotografía RGB puede representar legítimamente cualquiera); un archivo cuyo **nombre** sugiere otra modalidad (p. ej. un nombre de piel sobre un ECG); una imagen de aspecto cutáneo enviada como otra modalidad; documentos.
- Las imágenes y sus etiquetas de modalidad las prepara una persona **distinta de quien implementa la interfaz** (a designar por el propietario).

## Diseño, participantes y tareas (a fijar por el propietario)

- **Diseño cruzado con ensayos repetidos:** cada profesional realiza varios escenarios bajo **ambas** condiciones (`baseline`: interfaz vigente; `prototype`: entradas por modalidad), en dos periodos con orden aleatorizado y contrabalanceado (propuesto). Por eso **los ensayos de un mismo participante no son independientes** y las condiciones están emparejadas.
- Profesionales sanitarios (médicos, enfermería, paramédicos, otros). **Tamaño (número de participantes) y de escenarios por decidir.** La unidad de análisis es el **participante**, no el ensayo: añadir ensayos por persona no sustituye a añadir personas.
- Tareas por escenario: elegir la modalidad, ver la vista previa, confirmar o cambiar de modalidad, y una pregunta cerrada de comprensión sobre qué verifica la confirmación.
- **Aprobación institucional, consentimiento y gestión de datos de los participantes: no evaluados aquí**; pendientes antes de cualquier sesión. **No se ejecuta ningún estudio sin este protocolo aprobado y sus autorizaciones.**

## Registro (cerrado, sin texto libre, con seudónimos)

Un registro por participante, escenario y condición: código **seudónimo** de participante (sin nombres ni datos personales), rol, escenario, condición, periodo, plataforma (`web`/`mobile`), orden del ensayo dentro del periodo, modalidad prevista, modalidad **inicial** y **final** elegidas, si se confirmó, número de cambios, segundos y respuesta de comprensión (acierta, falla o sin respuesta). La herramienta `clinical/scripts/human_factors_tools.py` rechaza cualquier otro campo y cualquier texto que no sea un código. **Los eventos no se registran a mano: se derivan de los campos cerrados** (no se confía en un campo «bypass» del registro).

## Variables de resultado (definiciones)

| Resultado | Definición (derivada de los campos) | Denominador |
|---|---|---|
| Confirmación errónea | Se confirmó una modalidad distinta de la prevista | Todos los ensayos |
| Bypass | Fotografía de piel/herida confirmada bajo otra modalidad (sale del contrato dermatológico) | Ensayos con modalidad prevista piel/herida |
| Falsa cancelación | La primera elección era correcta y se abandonó o se cambió a una incorrecta | Ensayos con primera elección correcta |
| Tiempo adicional | Diferencia pareada (prototipo − base) del tiempo medio | Participantes con ambas condiciones |
| Comprensión | Acierto en la pregunta cerrada sobre qué verifica la confirmación | Ensayos con respuesta |

## Análisis

- **Análisis principal: remuestreo por participante (*cluster bootstrap*).** Se sortean participantes con reemplazo, se conservan **todos** los ensayos de cada participante sorteado y se evalúan **ambas** condiciones sobre los mismos participantes sorteados, de modo que se preserva el emparejamiento. Intervalo percentil al 95 %, con semilla reproducible. Se informa por condición, por modalidad prevista, por escenario y por participante (solo recuentos y tasas), y las diferencias pareadas prototipo − base por resultado y modalidad.
- **Wilson y Clopper-Pearson** suponen ensayos independientes; aquí **no lo son**. Se conservan solo como **exploración descriptiva etiquetada** (`descriptive_exploration_only`) y **no deben usarse para inferir**. Una prueba con datos sintéticos agrupados demuestra la diferencia: tratar los ensayos como independientes da un intervalo mucho más estrecho que remuestrear a las personas.
- **No fija margen de aceptación**: qué error residual es aceptable es decisión médica (`acceptance_margin = NOT_SET_MEDICAL_DECISION`). El estado de la herramienta es `NOT_EXECUTED_TOOLING_ONLY`: **no se ha ejecutado ningún estudio** y los resultados de una ejecución sintética de prueba no son resultados de investigación.
- Con pocos participantes los intervalos del *bootstrap* son poco fiables; con un solo participante no se calcula intervalo.

## Ampliaciones R18 (diseño estadístico; el expediente Gemini R16 no está en el repositorio: **No verificado**, se aplican los requisitos de la instrucción R18)

- **Diseño cruzado AB/BA y estratificación por secuencia.** Cada participante usa **una** condición por periodo (la herramienta rechaza mezclar condiciones dentro de un periodo). La secuencia (`AB` = base primero, `BA` = prototipo primero) se deriva de los registros y el remuestreo se hace **dentro de cada secuencia**, de modo que cada réplica conserva el equilibrio AB/BA de la muestra.
- **Réplicas:** al menos **5.000** réplicas *bootstrap* (valor por defecto de la herramienta).
- **Nivel de ensayo y nivel de participante, separados** (`trial_level_metrics` y `participant_level_metrics`): la tasa por ensayo y el **riesgo de al menos un error por participante** son magnitudes distintas (p. ej. 6 errores en 48 ensayos = 12,5 % por ensayo, pero 2 de 8 participantes = 25 % con al menos un error).
- **Ceros eventos con honestidad:** una celda sin eventos no se presenta como «riesgo cero». Si no hay variación entre réplicas (p. ej. cero eventos en todos los participantes) el intervalo *bootstrap* se declara **degenerado** (`degenerate_interval`) y no se informa; el resumen honesto es el límite superior exacto descriptivo (≈ 3/n para n ensayos independientes), que con datos agrupados es optimista.
- **Web frente a móvil:** campo cerrado `platform` (`web`/`mobile`); resultados por condición y plataforma, descriptivos (la plataforma no se supone aleatorizada).
- **Periodo y aprendizaje:** efecto de periodo (periodo 2 − periodo 1) y aprendizaje (ensayos tardíos − tempranos, según `order_in_period`; corte en la mediana), ambos agrupados por condición; con remuestreo estratificado no se leen como efecto de la condición. El aprendizaje se confunde con la dificultad del escenario salvo que los escenarios se contrabalanceen.
- **Pocos participantes:** los intervalos percentiles pueden infracubrir; se leen junto al número de participantes. **No se fija tamaño muestral ni umbral clínico** (`sample_size = NOT_SET_STUDY_DESIGN_DECISION`, `acceptance_margin = NOT_SET_MEDICAL_DECISION`).
- El estudio sigue `NOT_EXECUTED`; la capa 7 sigue `PROPOSED_INACTIVE` y desconectada del producto.

## Pendiente

- Margen de aceptación, número de participantes y de escenarios; participantes, responsable independiente del material y aprobación institucional.
- Redacción médica de los textos de limitación fija de cada modalidad (capa 6) antes de evaluar su legibilidad en móvil.
- Ejecución del estudio y su informe agregado. Hasta entonces la capa 8 figura **no realizada**.
