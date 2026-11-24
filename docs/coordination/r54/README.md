# R54 · Dosier literal para Gemini y Antigravity

Repositorio JuanCopado/Emergency. Fecha 24/11/2026. Núcleo internacional, sin
selección implícita de país/hospital. Receptora verificada:
`codex/v144-international-scope-20261116` en
`203237400698d9f5073c459202df59d0b8eb7ed4` (PR100 incorporada).
La inspección inicial fue sobre `c1ab23f1d9159b8b24a5f29ea1d6d6081e10140a`;
los cuerpos extraídos y el manifiesto son idénticos en ambas bases.
Rama aislada `codex/r54-medical-decisions-20261124`, worktree
`/workspace/Emergency-r54`. Main permanece en
`4f37263f581c41874fd3253147e6679b0b0685d8` y no se modifica.

## Autorización y alcance

**MED-DEC-R46-01 y MED-DEC-R46-02: APPROVED_MEDICAL_OWNER, SÍ, 2026-11-24**.
[Registro y referencia expresa](../../../clinical/qa/R54_MEDICAL_OWNER_DECISIONS_20261124.md).
Se aplican las precisiones corregidas R50. Los pendientes de aprobación citados
en el original R50 son históricos y quedan superados por la autorización R54 y
la confirmación R56. No se solicita nueva aprobación de esas decisiones.

Se añaden salvaguardas al padre y modalidades, se regenera su proyección canónica
en la app y se incorpora el [protocolo de adjudicación](../../../clinical/qa/R54_IMAGE_ADJUDICATION_PROTOCOL_20261124.md).
Sin cambios de dosis, algoritmos, servidor, flags, textos aprobados de Capa 7,
telemetría, contratos, fuentes clínicas canónicas ni producción/despliegue.
El runner de QA de laboratorio carga cuatro assets estáticos por loopback HTTP
para funcionar en navegadores administrados que bloquean `file://`; no abre
un servidor del repositorio ni cambia el flujo experimental.

## Extracción documental R51 completada en R54

Los archivos siguientes permiten el cotejo literal pendiente de Gemini; no se
reconstruye contenido. R51 no tenía artefacto separado en la receptora: se ejecutan
sus requisitos documentales expresamente identificados en R50/R56 y en el encargo R54.

| Cuerpo solicitado | Base anterior a R54 | Candidato R54 |
|---|---|---|
| clinical-images.md íntegro | [literal](literal/base/clinical-images.md) | [literal](literal/candidate/clinical-images.md) |
| image-modalities.md íntegro | [literal](literal/base/image-modalities.md) | [literal](literal/candidate/image-modalities.md) |
| Registro del padre de imagen | [valor JSON](literal/base/evidence-registry.json) | [valor JSON sin cambio](literal/candidate/evidence-registry.json) |
| Manifiesto íntegro de 30 filas | [bytes](literal/base/stimuli_manifest.json) | [bytes idénticos](literal/candidate/stimuli_manifest.json) |
| src-b5e20534 | [objeto JSON literal](literal/src-b5e20534.json) | Sin cambio en catálogo canónico |

[ARTIFACTS.json](ARTIFACTS.json) identifica base, rutas y SHA-256 de cada extracción,
adjunto y ficha. Los dos registros parciales JSON se extraen como valores sin
alterar campos; el objeto de fuente se conserva como subcadena literal. Los dos
módulos, manifiestos y tres adjuntos conservan sus bytes exactos.

## Cotejo de formulaciones aprobadas

| Requisito R50 / R54 | Incorporación verificada en el texto real |
|---|---|
| No exclusión de urgencia | Preámbulos del padre y bundle; el padre incluye ausencia de alerta y abstención técnica. |
| POCUS §4 | Se mantiene uso focal documentable/archivo QA, dinámica dependiente de operador y filosofía rule-in; no exclusión desde una captura aislada. Se preserva el párrafo M-mode ya aprobado. |
| TC/RM §4 | Serie DICOM volumétrica íntegra y especialista para valoración urgente; no exclusión de HIC/isquemia desde cortes/capturas/serie parcial. Sin introducir el umbral 1,5 mL retirado. |
| Mano | Exploración neurovascular/tendinosa directa documentada antes de anestesia local; una foto no excluye lesión profunda/cuerpo extraño/NSTI. |
| Fototipos V–VI §4 | No asumir precisión sin validación estratificada; revisión directa presencial y/o dermatoscópica; ámbito DERM/NHS adulto explícito, sin contraindicación universal. |
| Rx / ECG | Lectura clínica previa a asistencia en Rx, informe definitivo y confirmación clínica/calibración ECG. No extrapolar HTG696 a Rx urgente ni HTG739 al desempeño de este módulo. |
| Terapéutica | Sin pauta antimicrobiana/vacunal desde imagen ni generalizaciones CA-MRSA por país. |
| Rúbrica R50 §7 | [30 fichas reales](INVENTORY.md), N/A por aplicabilidad; M3 clínicos quedan PENDING, no normalidad inventada. |

Esto acredita cotejo documental contra los adjuntos aportados, **no** una nueva
verificación científica de las 19 fuentes primarias que Gemini afirma haber
comprobado. `src-b5e20534` continúa siendo una identidad compuesta de workflow,
sin URL ni identificador persistente. Los artefactos internos no son evidencia de
exactitud diagnóstica. La desagregación bibliográfica propuesta en R56 §3.3 y sus
afirmaciones regulatorias/fechas requieren cotejo primario propio; quedan conservadas
en el original sin incorporarlas como afirmaciones verificadas. **last_checked no
se renueva** y el padre conserva `workflow v1.4; diagnostic performance not established`.

## Discrepancias para conciliación de Gemini

1. Los slots STIM ilustrativos R50/R56 no describen los IDs reales. El inventario
   conserva S1-01…S2-15 y el mecanismo de cada fila: por ejemplo S1-01 es M3,
   S1-04 es M1 y S1-14 es M2. La distribución total sí coincide: 8/4/18.
2. R56 §4.2 propone «T2 incompatibilidad» para M1. El contrato aprobado define
   T7-02 como contrato desconocido y prohíbe clasificar contenido mediante píxeles.
   Se mantienen los M1 sin disparador Capa 7; ver protocolo y regresión específica.
3. El puente Documento con `kind=null` está protegido; E1 sin selección es otro
   flujo. No se transforma cualquier `null` en abstención.
4. La naturaleza clínica de los M3 requiere referencia independiente aun si su
   archivo es esquemático. **16 fichas con diagnóstico pendiente y 14 N/A**; ninguna
   tiene firma o decisión individual prellenada.
5. R50 indicaba repositorio no accesible públicamente en su sesión. En R54 se
   accede al repositorio y su metadata lo declara público; el bloqueo previo se
   resuelve mediante las extracciones, sin alterar la historia del informe recibido.

## Inventario, adquisición y revisión

**10/30 archivos presentes y SHA físicos comprobados; 20 ausentes; 0 adjudicados.**
[Inventario completo con hashes y fichas](INVENTORY.md). El manifiesto, bytes y
sellos históricos no se regeneran ni modifican; QA-01/02 permanecen fuera del banco.
[Continuación de adquisición R45](ACQUISITION.md) documenta avances y límites.

La preparación de fichas no realiza la adjudicación humana requerida. R56 §5
propone un estudio diagnóstico futuro independiente: no se implementan sus tamaños,
márgenes o reglas de parada como autorización del laboratorio actual.

## Entrega a revisores

Gemini recibe en este dosier los literales antes ausentes y la conciliación
pendiente del disparador M1, conservando las dos aprobaciones médicas.
Antigravity dispone del diff de la PR, SHA exacto, fuentes, fichas, tests y checks
para la auditoría independiente. Publicar el paquete no acredita recepción,
lectura ni dictamen de ninguno de los dos. No se atribuye una auditoría independiente
a la autorrevisión técnica de Codex.

Se mantiene **YELLOW · CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE**.
R5-1 ABIERTO, R5-2 PENDIENTE, G05 BLOQUEADO. Sin estudio humano, pacientes,
congelación, reclutamiento, liberación ni fusión de ramas protegidas.
