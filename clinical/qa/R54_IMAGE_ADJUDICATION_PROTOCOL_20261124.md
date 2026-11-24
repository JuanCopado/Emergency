# R54 · Protocolo de adjudicación aprobado (MED-DEC-R46-02)

Autorización expresa del propietario: **SÍ, 24/11/2026**. Se aplica R46 §3 con las
correcciones vinculantes de **R50 §§4, 5 y 7**. R56 §4 confirma esa aprobación;
sus slots ilustrativos no son IDs reales. [Registro](R54_MEDICAL_OWNER_DECISIONS_20261124.md).
Los originales recibidos se conservan literalmente en
[R46](../../docs/coordination/r54/sources/R46_GEMINI.md),
[R50](../../docs/coordination/r54/sources/R50_GEMINI.md) y
[R56](../../docs/coordination/r54/sources/R56_GEMINI.md), con SHA en el dosier.

## Finalidad y composición inmutables

Banco experimental de factores humanos, selección de modalidad, no interferencia,
comprensión/recuperación de abstención técnica y telemetría. **No valida eficacia
diagnóstica**, aun con 30/30 aprobados. Dos sets de 15; cada set tiene 4 M1, 2 M2
y 9 M3: **8 M1 / 4 M2 / 18 M3**. M2 se describe solo en brazo B, sin contraste A/B.
Los controles QA-01/QA-02 quedan fuera de las 30 posiciones.

La fuente autoritativa de IDs, escenario, mecanismo, modalidad y disparador es
`clinical/lab/human_factors/bank/stimuli_manifest.json`. No asignar mecanismos
por número, orden de tabla o slots STIM de Gemini. Conservar el emparejamiento y
el contrabalanceo canónicos. No introducir TC/RM sustituyendo posiciones existentes.

## Aplicabilidad de diagnóstico y referencia

| Mecanismo | Verdad de modalidad | Diagnóstico, red flags y referencia independiente |
|---|---|---|
| M1, 8 | Verificar modalidad real y selección adversarial inequívoca | `N/A`, salvo objetivo/bandera roja clínica explícita del escenario; entonces PENDIENTE hasta adjudicación. La palabra «necrótica» de una especificación no acredita NSTI. |
| M2, 4 | Modalidad recuperable o `N/A` si no procede; no inventar la modalidad desde un archivo corrupto | `N/A`; prohibida adjudicación diagnóstica sobre material no procesable. Verificar defecto/selección y disparador técnico real. |
| M3, 18 | Coincidencia de modalidad y ruta válida | Imágenes clínicas: `PENDING_CLINICAL_ADJUDICATION` hasta diagnóstico/hallazgos críticos respaldados por fuente independiente. Documentos no diagnósticos: `N/A`. |

`N/A` significa que no corresponde; no equivale a dato ausente, resultado negativo,
normalidad ni aprobación. Las imágenes clínicas esquemáticas presentes conservan
su requisito de realismo y referencia pendiente; no se inventan diagnósticos desde
el generador. No utilizar este banco para sensibilidad, especificidad, VPP/VPN,
calibración ni afirmaciones de eficacia clínica.

## Revisión individual antes de aceptación

1. Vincular cada ID a bytes físicos, ruta, formato, tamaño y SHA-256 exacto.
   Un archivo ausente queda pendiente sin hash inventado. Una sustitución cambia
   hash y requiere nueva revisión; conservar sellos y bytes históricos.
2. Verificar origen, autorización/licencia y privacidad del original y derivados:
   píxeles, EXIF/DICOM y documentos. Un escaneo técnico sin hallazgos no es revisión
   humana de privacidad. Prohibido incorporar PHI/PII.
3. Dos revisores independientes confirman modalidad, realismo **≥4/5 por cada
   revisor**, presentación a 360×640, dificultad del par y datos de subgrupo
   pertinentes. Tercero dirime discordancias, conservando ambos dictámenes.
   No inferir edad o Fitzpatrick; MST de la especificación no equivale a Fitzpatrick.
4. Para las imágenes clínicas M3, revisión por expertos del dominio y fuente de
   referencia independiente, sin usar salida del sistema como verdad. Registrar
   hallazgos críticos y límites; un fotograma POCUS no acredita un examen dinámico
   negativo. Aplicar las salvaguardas R50 sin el umbral HIC eliminado de R46.
5. Confirmar integridad técnica y conducta esperada en brazo B a partir del contrato
   y manifiesto. La entrada Documento con puente `kind=null` permanece protegida;
   no toda aparición de null es T7-01. No diagnosticar desde una abstención.
6. El médico propietario registra individualmente **SÍ / ADJUDICATED_APPROVED**
   o **NO / REJECTED_REPLACE_STIMULUS**, comentario, identidad y fecha. Estas fichas
   están preparadas sin respuesta, firma ni adjudicación en su nombre.

## Discrepancia técnica material de R56

R56 §4.2 atribuye a los slots M1 «T2 incompatibilidad» y bloqueo por contenido.
El contrato aprobado prohíbe usar píxeles, RGB, EXIF, ausencia de DICOM o salida de
modelo para clasificar modalidad: **T7-02 significa contrato declarado desconocido**,
no herida declarada ECG. M1 B/C/D tiene `expected_layer7_trigger=null` en el
manifiesto y mide bypass del selector; no se convierte en detector de contenido.
Se incorpora la rúbrica R50 preservando contrato, laboratorio y textos aprobados.
Esta discrepancia se entrega a Gemini para conciliación documental, sin reabrir
MED-DEC-R46-01/02 ni alterar el producto.

## Compuertas conservadas

Banco **NOT_FROZEN_NOT_VALIDATED**, cero adjudicaciones creadas por este trabajo.
No reclutamiento, pacientes ni activación de Capa 7 en producción. Se conservan
auditoría independiente sobre SHA exacto, ética/exención, consentimiento y privacidad
como requisitos del estudio. **YELLOW · CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**.
R5-1 abierto, R5-2 pendiente y G05 bloqueado. Las aprobaciones del protocolo no
constituyen aprobación individual de los 30 estímulos ni autorización de liberación.
