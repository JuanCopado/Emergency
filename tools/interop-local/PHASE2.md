# Interoperabilidad sintética · segundo incremento

Base `a3ae85412a868c105c64ca8b491e1cb3a1df065c`; rama aislada
`codex/interop-phase2-synthetic-20261127`. PR129 y su worktree permanecen intactos.

## Intercambio materializado

- FHIR R4 4.0.1 `Bundle/collection`: un Patient fijo sin nombres/demografía,
  una o dos Observations numéricas de los dos códigos LOINC ya presentes, y un
  DiagnosticReport con referencias locales exactas a todas ellas. No se admite
  texto narrativo, conclusiones diagnósticas, referencias externas, duplicados,
  mezcla de sujetos ni recursos de tratamiento.
- HL7 v2.5.1: un panel local de laboratorio con una o dos OBX NM finales, ACK
  trazable al mensaje sintético, códigos/unidades/nombres oficiales comprobados
  mediante el parser anterior. No hay conversiones de unidad ni interpretación
  de resultados. El control de precisión previo se reutiliza: 100.0 permanece
  100.0 y 13.20 se rechaza porque no puede emitirse idéntico en el subconjunto.
- DICOM: mismo P10/fantoma procedural registrado y mismo PNG; vista nativa1:1 y
  ampliada con nearest neighbour declarada, responsive, detalles semánticos y
  advertencia permanente. No windowing ni transformación de píxeles fuente.
  CSP con hash de estilo, sin JavaScript, enlaces, clientes de red ni recursos
  externos. El PNG se incluye como data URI.

Se reutilizan las URI canónicas UCUM/LOINC, atribución y Long Common Names de
[LOINC_short_license.txt](LOINC_short_license.txt). El código de panel es local
`urn:emergency:lab:report-code`, no se inventa un código clínico universal.

## Autorización y retención: límites implementados

`LocalLabAdapter` solo puede utilizarse por un proceso local de confianza.
Cada instancia concede un objeto capability no serializable a otra instancia,
con permisos reductibles y caducidad de1a300segundos; al expirar o cerrar se
revoca. Esto **no autentica a una persona**, no implementa OAuth/OIDC ni aísla
procesos hostiles. El CLI lo usa dentro del proceso técnico local; no expone
el objeto ni crea credenciales persistentes.

El contrato `POLICY` fija los tres permisos de lectura/render sintéticos y
mantiene explícitamente no aprobadas la autenticación institucional, los
permisos operativos, la retención operativa y las conexiones. Alterar esos
controles a true o añadir permisos no habilita una conexión: se rechaza.
`connect_operational` siempre falla cerrado y no llama a transporte alguno.

El adaptador no guarda payloads ni mantiene caché. Los archivos producidos por
el demo son evidencia sintética bajo custodia del propietario; **no se afirma
borrado automático o seguro de memoria/disco**. El vencimiento del capability
revoca el permiso, no borra artefactos del usuario.

Antes de cualquier conexión operativa futura harán falta, además de una
autorización específica del sistema y del responsable:

1. Identidad institucional verificable, flujo de autenticación aprobado y
   autorización de mínimo privilegio por sujeto/operación/organización.
2. Destinos permitidos, transporte TLS autenticado y validado, gestión de
   secretos, controles de tamaño/tasa/repetición y un contrato de errores/ACK.
3. Finalidad y campos autorizados, evaluación de privacidad, derechos de
   píxeles y revisión de PHI/burned-in fuera del fantoma registrado.
4. Retención aprobada por tipo de dato, custodia, accesos, auditoría minimizada,
   respuesta a incidentes y eliminación verificable.
5. Auditoría independiente y aceptación de perfiles, unidades y semántica de
   intercambio del sistema concreto. Pruebas sintéticas no sustituyen esta labor.

Estos requisitos se definen para impedir una activación por configuración;
no se declaran satisfechos.

## Ejecución y prueba

Python3.12+ estándar, sin instalación ni servidor:

```powershell
python tools/interop-local/interop_phase2.py C:/ruta/nueva/phase2-demo
python -m unittest discover -s tools/interop-local -p test_interop_phase2.py -v
python -m unittest discover -s clinical/tests -p test_interop_phase2_suite.py -v
```

El destino debe ser nuevo. El demo materializa panel HL7, Bundle JSON, ACK,
DICOM sintético, PNG, visor, política y recibo SHA-256. La apertura del visor
es local y opcional; no conecta a un PACS. El bridge propio incluye las pruebas
reales en el QA y cobertura existentes. No se cambia ningún umbral o exclusión.

Fuentes primarias consultadas: [FHIR R4 DiagnosticReport](https://hl7.org/fhir/R4/diagnosticreport.html),
[Patient](https://hl7.org/fhir/R4/patient.html),
[Observation](https://hl7.org/fhir/R4/observation.html).
Las versiones HL7/DICOM y sus límites se conservan del
[primer incremento](README.md). No es un validador FHIR general, un perfil HL7
completo, un PACS ni una certificación institucional.

CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
