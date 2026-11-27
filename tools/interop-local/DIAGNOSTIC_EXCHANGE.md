# Reconciliación de intercambio sintético y visor local

Base: PR131, SHA `3cc5139b149feef390e6ceaa7358e2425d92620a`.
Rama de tarea: `codex/interop-mcp-increment-20261127`.
Copia aislada: `C:/Users/juanc/ChatGPT_Trabajo/INTEROP_MCP_INCREMENT_20261127`.

## Déficit y comportamiento añadido

Las fases previas validan FHIR y HL7 individualmente. Dos archivos independientes pueden ser válidos y, aun así, describir resultados distintos. La nueva API explícita `interop_exchange.reconcile(fhir_raw, hl7_raw)` comprueba el contrato optativo `same-synthetic-exchange-exact-v1`: el operador declara que ambos son representaciones del **mismo intercambio sintético** y exige fijación de precisión léxica.

Se reutilizan `phase3.decode_fhir` y `phase3.receive_hl7`. Solo tras pasar sus guardas se compara la representación JSON canónica del Bundle completo, incluidas las referencias Patient/Specimen/Observation/DiagnosticReport, códigos, unidades, estados, instante fijo y valor numérico. Se ignoran el orden de claves y los espacios JSON. Se distingue `100` de `100.0` porque el nuevo contrato exacto fija también el lexema; **no cambia los validadores base ni impone esta equivalencia a intercambios independientes**.

Una discordancia o entrada malformada produce un error fijo, sin texto de entrada. El CLI usa las guardas de archivos locales/tamaño/junction existentes, crea un recibo nuevo exclusivamente y no sobrescribe. Una pareja rechazada no crea el recibo de salida. No convierte unidades ni interpreta resultados o diagnósticos. La igualdad no acredita por sí sola un origen o episodio real común; no se inventa una correlación clínica a partir del contenido.

## Visor usado por el PACS de laboratorio

`interop_phase2.secure_view`, reutilizado por `SyntheticGateway`, añade un grupo nativo de radios para escala1:1,4× y8×. Tiene leyenda, etiquetas vinculadas, ayuda textual y estilo de foco visible. CSS selecciona la vista sin JavaScript, formularios ni conexión. Las tres imágenes contienen exactamente el PNG registrado original; solo cambia el tamaño de presentación, con nearest-neighbour. SHA del DICOM, píxeles, dimensiones fuente y `pixel_transform:false` se conservan.

Las escalas son tamaños CSS nominales y pueden reducirse para ajustarse al viewport; no se acredita calibración física de pantalla ni correspondencia entre píxeles CSS y píxeles del dispositivo.

La CSP mantiene `default-src 'none'`, imagen data URI y CSS autorizado por hash calculado del estilo real. No se añaden scripts, recursos externos, control de ventana o contraste, lectura de otro DICOM ni rutas a un PACS real. Roles, credenciales, TTL y límites de la pasarela previa siguen vigentes.

**Visual: NOT_EXECUTED_POLICY_BLOCKED.** No se abrió el HTML ni se hizo navegación/captura con navegador, localhost, CDP u otra superficie. Las comprobaciones HTMLParser/DOM/CSP y PNG son técnicas: no acreditan revisión visual, uso real de teclado/lector de pantalla ni conformidad WCAG completa.

## Uso local

```powershell
python tools/interop-local/interop_exchange.py --fhir C:/nuevo/bundle.json --hl7 C:/nuevo/input.hl7 --output C:/nuevo/receipt.json
python -B -X utf8 -m unittest discover -s tools/interop-local -p test_interop_exchange.py -v
python -B -X utf8 -m unittest discover -s clinical/tests -p test_interop_exchange_suite.py -v
```

El puente de pruebas entra en el descubrimiento QA existente. No se añaden dependencias, reglas clínicas, funciones de escritura clínica, permisos, conexiones de red, datos identificables ni prescripción. La evidencia se guarda en `DESARROLLO_MCP_20261127/INTEROP`; no se envía a servicios externos.

Emergency MCP se utilizó para una lectura focal de `get_project_state`, distinta de las pruebas nuevas de interoperabilidad; no se repitió su instalación ni su suite.

CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
