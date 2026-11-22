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

## Participantes y tareas (a fijar por el propietario)

- Profesionales sanitarios (médicos, enfermería, paramédicos, otros). **Tamaño por celda por decidir**; referencia informativa: con *n* tareas por modalidad y ninguna elección errónea, la cota superior del 95 % de la tasa de error es ≈ 3/*n* (regla de tres).
- Tareas por modalidad: elegir la modalidad, ver la vista previa, confirmar o cambiar de modalidad. Orden aleatorizado y contrabalanceado (propuesto).
- **Aprobación institucional, consentimiento y gestión de datos de los participantes: no evaluados aquí**; pendientes antes de cualquier sesión.

## Registro (cerrado, sin texto libre)

Un registro por participante y tarea, con **códigos opacos** y valores cerrados: participante, rol, tarea, modalidad prevista, modalidad elegida, número de cambios de modalidad, resultado (`correct`, `wrong_modality`, `abandoned`, `timeout`) y segundos. La herramienta `clinical/scripts/human_factors_tools.py` rechaza cualquier otro campo y cualquier texto fuera de un código, para que no entren datos personales.

## Análisis

`human_factors_tools.py summarize` (entrada y salida estándar; **no accede al sistema de archivos**, con prueba estructural): error residual global y por modalidad prevista con intervalo exacto de Clopper-Pearson y de Wilson al 95 %, resultados por categoría y sesiones con cambio de modalidad. **No fija umbral de aceptación**: lo que se considera un error residual aceptable es decisión médica.

## Pendiente

- Umbral de aceptación y tamaño por celda; participantes, responsable independiente del material y aprobación institucional.
- Redacción médica de los textos de limitación fija de cada modalidad (capa 6) antes de evaluar su legibilidad en móvil.
- Ejecución del estudio y su informe agregado. Hasta entonces la capa 8 figura **no realizada**.
