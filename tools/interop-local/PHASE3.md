# Interoperabilidad sintética · tercer incremento

Base auditada `f32d211eed6a7baa7c42aadae583f6726e9e7e9b` de PR130.
Rama aislada `codex/interop-phase3-synthetic-20261127`.
No modifica recursos, código ni estados clínicos canónicos; no integra ninguna PR.

## Comportamiento implementado

El contrato local R4 4.0.1 añade un `Specimen` fijo sintético a Patient,
1–2 Observation y DiagnosticReport ya admitidos. El sujeto y todas las
referencias al espécimen deben coincidir exactamente. No admite identificadores
externos, texto libre, narrativas, demografía, recursos de tratamiento ni
campos extra. El espécimen es una construcción explícita del laboratorio,
no una afirmación de recogida o disponibilidad de una muestra real ni una
inferencia de SPM/SPT ausentes en los mensajes. No se atribuye un tipo biológico.

Se reciben los dos formatos ORU_R01 v2.5.1 ya documentados, individual y panel,
bajo una entrada común. Se conservan el ACK válido y su control ID sintético,
LOINC, UCUM y precisión de origen. El parser numérico rechaza representaciones
que no podrían emitirse sin pérdida; no convierte unidades. Los errores se
entregan como un `OperationOutcome` técnico cerrado. No se refleja el payload,
texto libre, ID arbitrario ni mensajes de excepción; un mensaje malformado no
produce un ACK con contenido tomado de la entrada. No es un motor HL7 general.

El adaptador PACS de laboratorio registra **una única instancia en memoria**:
el fantoma DICOM procedural ya registrado. Cada escritura valida el archivo
completo y su SHA; una escritura inválida conserva la instancia previa. No hay
dicomweb, DIMSE, sockets, endpoint, puerto ni cliente HTTP. La recuperación
devuelve el visor estático previo, con la misma imagen y SHA, sin interpretación
diagnóstica ni alteración de píxeles. Esto prepara una interfaz local store/read;
no constituye un PACS interoperable con terceros.

## Autenticación local y autorización

Un arnés de confianza emite una credencial efímera de 256 bits con `secrets`.
Sólo se conserva su digest en la sesión; la comprobación usa comparación de
tiempo constante. No se escribe ni se incluye en recibos, errores o auditoría.
El rol reviewer permite validar FHIR/HL7, leer el fantoma y consultar auditoría;
technician añade almacenamiento. No existen permisos clínicos ni operativos.
No se aceptan roles desconocidos ni duraciones fuera de 1–120 segundos.

La rotación revoca la credencial anterior y vacía la instancia previa. Expirar
la sesión revoca el token y elimina la referencia al payload. Cerrar impide
emitir otra credencial en la misma instancia. Se limitan a 40 los intentos por
sesión, incluidos los de token inválido. La API de emisión es para un proceso
local de confianza: **no autentica a una persona, no implementa SSO/OIDC ni
protege contra un proceso local hostil con acceso a la memoria**. Este límite
no se presenta como autenticación institucional aprobada.

## Auditoría y retención comprobables

La instancia DICOM vence a los 30 segundos y los eventos a los 60 segundos,
medidos con reloj monotónico. Se purga al recibir una operación o al invocar
`retention_status`; no se promete un temporizador de borrado en segundo plano.
La auditoría mantiene como máximo 32 eventos en memoria con secuencia, instante
monotónico, operación de una lista fija y resultado. No contiene payloads,
hashes de entradas rechazadas, tokens ni texto suministrado por el llamante.
Los fallos not-found se registran como tales. El cierre elimina las referencias
de sesión, instancia y eventos. No se garantiza borrado seguro físico o de
memoria, persistencia, integridad frente a un administrador hostil ni entrega
a un SIEM. El registro interno no se anuncia como un recurso AuditEvent FHIR
conforme ni como cumplimiento ATNA.

Los archivos del demo son evidencia sintética deliberadamente persistida por
el propietario. El TTL del adaptador **no elimina esos archivos**. La auditoría
exportada es una instantánea previa al evento de su propia consulta.

Antes de conexión institucional siguen pendientes identidad, permisos y
finalidad autorizados, TLS mutuo/validación de destino, gestión de secretos,
retención/aprobación institucional, privacidad de metadatos y píxeles, perfiles
reales, auditoría durable y respuesta a incidentes. `connect_operational`
rechaza siempre. Ninguna configuración los activa.

## Comprobaciones y limitaciones

```powershell
python -B -X utf8 -m unittest discover -s tools/interop-local -p test_interop_phase3.py -v
python -B -X utf8 -m unittest discover -s clinical/tests -p test_interop_phase3_suite.py -v
python -B -X utf8 tools/interop-local/interop_phase3.py C:/ruta/nueva/phase3-demo
```

El demo genera Bundle, ACK, recibo PACS, visor, PNG, OperationOutcome, auditoría,
política y SHA-256; no exporta credenciales. Rechaza un destino existente.
Las regresiones previas se ejecutan sólo para comprobar la nueva composición
de validadores y la ausencia de cambios en DICOM/precisión/códigos.

**Revisión visual: NOT_EXECUTED_POLICY_BLOCKED.** La herramienta de navegador
rechazó `file://` y prohibió explícitamente vías equivalentes. No se intenta
localhost, otra aplicación o una ruta alternativa para eludirlo. Preparar HTML
y verificar estáticamente CSP/píxeles no acredita haberlo visto en navegador.

Fuentes primarias: [FHIR R4 Specimen](https://hl7.org/fhir/R4/specimen.html),
[OperationOutcome](https://hl7.org/fhir/R4/operationoutcome.html),
[AuditEvent (referencia de límites, no recurso implementado)](https://hl7.org/fhir/R4/auditevent.html).
La documentación permanente fija R4; no se declara compatibilidad automática
con versiones posteriores. Se conserva la licencia y URI LOINC previas.

CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
