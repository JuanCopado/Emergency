# Laboratorio local de interoperabilidad

Base: `1f0fed8d731f65168ac338b5ddb18f451fccc6d6`. Rama aislada
`codex/interop-synthetic-local-20261127`. Consumidor: operador técnico local,
datos íntegramente sintéticos. Sin sistemas hospitalarios, sockets ni conexión externa.

## Capacidades nuevas y límites

| Incremento | Función ejecutable | Límite explícito |
|---|---|---|
| FHIR | Recepción y emisión JSON R4 4.0.1: Bundle collection con Patient sintético y Observation numérica; código LOINC, unidad UCUM, referencia local y versión controlados | Contrato cerrado, dos recursos y dos analitos de demostración; no validador FHIR general, API FHIR ni conformidad certificada |
| HL7 | Recepción de archivo ER7 v2.5.1 ORU_R01, validación de MSH/PID/OBR/OBX, transformación a Bundle y generación ACK AA | Un resultado final NM por mensaje, ruta de laboratorio fija, procesamiento T; rechaza otros eventos, datos personales, unidades inferidas y repeticiones. Sin MLLP ni ACK de mensajes rechazados |
| DICOM | Recepción P10 de fantoma procedural registrado, validación estructural y de Transfer Syntax, generación PNG y visor HTML sin scripts ni recursos externos | Solo SC MONOCHROME2 64x64 8bit Explicit VR Little Endian del generador. No acepta imágenes arbitrarias ni interpreta hallazgos; no PACS, DIMSE, C-STORE ni DICOMweb |

La guarda de privacidad DICOM exige que el hash completo coincida con el fantoma
procedural conocido. Marcar una imagen como sintética o BurnedInAnnotation=NO
no demuestra por sí solo ausencia de PHI. Por eso no se amplía la admisión a
otros píxeles ni a imágenes de fuentes públicas.

La referencia de arquitectura previa se reutiliza:
`docs/coordination/supercoord-20261127/architecture/CAPABILITY_DEPENDENCY_MAP.json`.
Se revisaron las guardas de imagen y el renderer RSNA existente. No se reutiliza
su ventana HU ni su ordenamiento CT en este fantoma SC: no corresponde aplicar
una transformación clínica de CT a este incremento. No se duplican fórmulas ni
se altera el renderer, las notas, T05/T06 o la interfaz de producto.

## Ejecución

Python estándar, sin instalar paquetes:

```powershell
python tools/interop-local/interop_lab.py demo C:/ruta/nueva/demo
python tools/interop-local/interop_lab.py hl7 C:/ruta/nueva/recibido-hl7 --input C:/ruta/nueva/demo/synthetic-oru.hl7
python tools/interop-local/interop_lab.py fhir C:/ruta/nueva/recibido-fhir --input C:/ruta/nueva/demo/synthetic-bundle.json
python tools/interop-local/interop_lab.py dicom C:/ruta/nueva/recibido-dicom --input C:/ruta/nueva/demo/synthetic-phantom.dcm
python -m unittest discover -s tools/interop-local -v
```

El destino debe ser nuevo; no se sobrescriben archivos. Las entradas son archivos
locales de tamaño limitado; no se admiten rutas UNC ni enlaces simbólicos.
Los rechazos CLI no imprimen contenido de entrada. El recibo conserva SHA-256
del original y de cada resultado. Abrir `viewer.html` es opcional y no inicia
un servidor. El visor muestra únicamente PNG generado desde el fantoma registrado.

## Referencias oficiales y versionado

- [HL7 FHIR R4 4.0.1 Observation](https://hl7.org/fhir/R4/observation.html)
  y [Bundle](https://hl7.org/fhir/R4/bundle.html): versión de interoperabilidad
  elegida explícitamente; R5 existe y no se acepta por inferencia.
- [HL7 v2.5.1 ORU_R01 y OBX](https://www.hl7.eu/HL7v2x/v251/std251/ch07.html):
  especificación de capítulo en portal HL7 Europa. Consulta indexada disponible,
  recuperación directa bloqueada; se contrastaron campos con la publicación
  institucional del [Implementation Guide ELR 2.5.1](https://www.in.gov/dA/0821ca7dab/HL7_2.5.1_ELR_Implementation_Guide.pdf?language_id=1).
  No se afirma implementar el perfil ELR completo ni un perfil territorial.
- DICOM PS3.10 2026e [archivo P10](https://dicom.nema.org/medical/dicom/current/output/chtml/part10/chapter_7.html),
  PS3.5 2026e [Transfer Syntax](https://dicom.nema.org/medical/dicom/current/output/chtml/part05/chapter_10.html)
  y PS3.3 [Secondary Capture](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.8.html).
  Especificación actual consultada el 27/11/2026; el contrato fija UID
  `1.2.840.10008.1.2.1`. No se afirma conformidad de una aplicación DICOM de red:
  una aplicación DIMSE conforme requiere negociación y otras capacidades ausentes.

Las páginas de normas se consultaron para diseñar el contrato; no se redistribuye
su texto. Los mensajes e imágenes son producción procedural propia sintética,
sin pacientes ni activos de terceros. Los derechos de fuentes clínicas, PTBR-PIX,
retención y responsables operativos siguen pendientes para cualquier consumidor real.
El límite técnico de datos no constituye prueba clínica, estudio o certificación.

**CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.**
