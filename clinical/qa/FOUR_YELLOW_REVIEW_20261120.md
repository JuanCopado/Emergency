# Preparación de revisión clínica · 20 noviembre 2026

Base de integración `19716c41f2bdb426bae4984c000a218ccb64f6ba`. Cuatro módulos YELLOW. Esta revisión no modifica su estado.

## 11 · Selector manual de arritmias y parada

PR #16 conserva ocho navegaciones Windows en dos superficies y cuatro destinos. Comparados con su HEAD, son idénticos el componente ResuscitationCircuits, ClinicalGuides, el acceso canónico y el script original. El test original buscaba texto sensible a mayúsculas aunque el estado se presenta en mayúsculas por CSS. Se comprueba el estado completo del destino y se incorpora la ejecución con Chrome al trabajo App UI QA. La salida individual del paso identifica cada ruta. No se infiere rendimiento clínico de la navegación.

## 2 · Imagen de gasometría

El desafío existente clinical/tests/blood_gas_photo_challenge.py genera un ticket sintético con tres campos y cinco variantes visuales. Para evaluación clínica preparar tickets disociados de diferentes analizadores, reservar pacientes independientes del desarrollo y registrar original del analizador, tipo de muestra explícito y transcripción de referencia antes de mostrar el resultado al evaluador. Medir por campo concordancia exacta de analito, cifra, separador y unidad, incluyendo campos extra, omisiones y abstenciones. Registrar errores de atribución del tipo de muestra por ticket. Evaluar después la interpretación con transcripción de referencia y por separado con OCR. Conservar denominadores, fallos críticos y límites de precisión por dispositivo. Fijar criterios de aceptación antes de abrir el conjunto reservado.

## 10 · Piel y heridas

Pregunta inicial propuesta para valoración de fotografías: ¿se puede describir de forma reproducible lo visible o debe solicitarse otra imagen o exploración presencial? Antes de evaluar, fijar variables observables, exclusiones y umbral de aceptación; separar este objetivo de cualquier clasificación diagnóstica. Reservar casos autorizados independientes por paciente con tonos de piel, iluminación, zonas y calidades variadas. Referencia clínica cegada a la salida, con adjudicación documentada de discordancias. Registrar por caso respuesta, abstención y falsa tranquilidad, con su denominador. Si se incorpora un objetivo diagnóstico, definir previamente su patrón de referencia. No se ha verificado aquí una cohorte clínica evaluable para ninguno de los dos módulos de imagen.

## 12 · Escalas y fórmulas

El registro contiene 135 escalas con source_url y 45 fórmulas sin ese campo por fila. La existencia del enlace no acredita validez de la implementación. Primer cotejo estático de ckd-epi-2021 en clinical/scripts/clinical_calculator.py: constantes, exponentes por sexo, edad en años, creatinina en mg/dL y unidad final coinciden con NIDDK, sección «2021 CKD-EPI Creatinine Equation», ecuación y tabla 1 (https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/adults). El motor rechaza edad menor de 18. Falta completar pruebas de frontera, campos no finitos y metadatos visibles antes de someter esta entrada a aprobación. Las otras 44 fórmulas quedan pendientes de cotejo en este expediente. Las validaciones previas de escalas conservan su alcance.
