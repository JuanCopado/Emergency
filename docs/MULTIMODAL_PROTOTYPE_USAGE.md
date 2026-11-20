# Prototipo multimodal local

Ejecutar desde la raíz del repositorio con Python 3.12+ en modo UTF-8. Instalar
`clinical/requirements-multimodal.txt` y disponer de `ffmpeg`/`ffprobe` locales
para vídeos. La demo usa el codificador `mpeg4`; no instala herramientas.

```powershell
$env:PYTHONUTF8 = '1'
python clinical/scripts/multimodal_prototype.py demo C:/workspace/emergency-multimodal-demo
python clinical/scripts/multimodal_prototype.py validate-bank C:/workspace/emergency-multimodal-demo/bank.private.json
python clinical/scripts/multimodal_prototype.py admit C:/workspace/emergency-multimodal-demo/bank.private.json --split development
python clinical/scripts/multimodal_prototype.py export-blind C:/workspace/emergency-multimodal-demo/bank.private.json
python -m unittest discover -s clinical/tests -p test_multimodal_prototype.py -v
```

La carpeta de demo debe ser nueva y quedar fuera del repositorio. No se incluye
ningún banco ni medio guardado: el comando `demo`, si se ejecuta expresamente,
genera cuatro imágenes geométricas y un vídeo de patrón de prueba; **cero casos diagnósticos**. El export
ciego devuelve una lista vacía porque ningún caso sintético es admisible al examen.
`technical-report.json` incluye ese bloqueo esperado, no un fallo de la demo.

## Contratos y custodia

El catálogo privado sigue `clinical/schemas/multimodal-bank.schema.json` y las
guardas de `multimodal/bank.py`. Cada archivo exige SHA-256/tamaño, autorización
para el destino y revisión humana ligada a esos mismos bytes. Los identificadores
no deben contener datos personales. La procedencia documental se conserva bajo
`rights.authorization_ref` y en el registro de fuentes existente; esos documentos
deben ser verificados por el custodio. Las declaraciones JSON no son firmas.

Docencia, desarrollo y examen no pueden compartir paciente, estudio, grupo de
fuente o linaje declarado. Los binarios duplicados se rechazan incluso dentro de
la misma partición para evitar inflar el número de casos. Recortes/recompresiones
no idénticos requieren linaje común y revisión: no hay detector perceptual de
casi duplicados ni prueba contra contaminación de preentrenamiento.

Cada activo declara `derivative` como booleano. Si es derivado, exige
`parent_sha256` conocido en el banco y un `lineage_group_id` compartido; hereda
paciente, estudio, fuente y partición del padre. Se rechazan padres ausentes,
ciclos y cruces. La trazabilidad depende de que el custodio declare todos los
derivados realmente existentes; no puede descubrir parentescos ocultados.

`export-blind` devuelve exclusivamente IDs neutros y campos técnicos permitidos.
«Neutro» exige un formato de ID, no garantiza que el identificador o el orden
no codifiquen la clase. La salida conserva el orden del banco para mantener
la identidad del recibo congelado. El custodio debe asignar IDs independientes
del diagnóstico y fijar el orden de evaluación antes de congelar; este prototipo
no aporta aleatorización secreta ni demuestra ausencia de pistas por orden.
No copia archivos ni concede al intérprete acceso a la carpeta privada. Un futuro
ejecutor debe resolver IDs a copias desidentificadas en un almacén separado y
proteger referencias y fuentes con permisos del SO. **Esta entrega no implementa
ese aislamiento de acceso ni ejecuta una inferencia ciega.** No pasar el banco
privado, rutas originales ni respuestas al modelo o a recuperación de ejemplos.

El examen de imágenes bloquea material con metadatos adicionales, fragmentos o
segmentos no permitidos y bytes posteriores al final del contenedor. La inspección
estructural se aplica a la copia exacta verificada, además de la decodificación;
no se eliminan datos silenciosamente. Crear un derivado limpio exige registrar
su nuevo hash/linaje y repetir la revisión humana. Esto no desidentifica píxeles:
necesitan inspección humana. Una miniatura o un hash no demuestra desidentificación.

El vídeo no se admite en `blind_test`: una tarea de vídeo o un activo con sufijo
MP4/WebM devuelve `blind_video_not_supported` antes de abrir el códec, aunque se
declare revisado y sin etiquetas o la tarea esté clasificada como imagen. Un
vídeo renombrado como PNG/JPEG falla por firma/extensión antes del códec. MP4/WebM y
sus fotogramas siguen disponibles para docencia/desarrollo con revisión completa
del vídeo; no existe en esta entrega un procedimiento para habilitar vídeo ciego.
La admisión ciega solo permite sufijos exactos PNG/JPG/JPEG, sin puntos o espacios
finales: el resto devuelve `blind_image_format_required` antes de la inspección.
Así no se confía en la posible normalización de nombres de archivo por Windows.

La lista estructural sin metadatos se restringe a chunks PNG de imagen
(`IHDR/PLTE/IDAT/IEND`) y a marcadores de codificación JPEG con JFIF mínimo;
el resto de segmentos, miniaturas y bytes posteriores al final se señalan como
metadatos. La revisión visual y la custodia siguen siendo necesarias.
`metadata_present=false` no certifica ausencia de datos ocultos: la inspección no
reconoce cargas añadidas dentro del flujo IDAT ni dentro del escaneo comprimido
JPEG antes de EOI. Esos bytes pueden sobrevivir a un visor de metadatos y a la
revisión visual. Se necesita un proceso externo controlado de producción y
verificación del derivado para un examen real; esta entrega no lo implementa ni
autoriza la admisión de archivos hostiles. No se recodifica automáticamente.
Esta limitación también acompaña cada entrada exportada en `limitations` por la
CLI. El cambio de ese texto cambia el hash de las entradas, como cualquier cambio
de límites del contrato; no se renuevan recibos previos automáticamente.
Symlinks, junctions/reparse points y archivos con varios enlaces duros declarados
por el filesystem se rechazan. Esto no demuestra ausencia de toda carrera de I/O.
FFmpeg/ffprobe se resuelven como ejecutables desde entradas absolutas de PATH,
excluyendo el directorio actual y launchers de script. PATH sigue siendo una
frontera de confianza del operador, no un sandbox del SO. La demo comprueba las
herramientas antes de crear el destino; un fallo posterior puede dejar una salida
parcial, que se conserva y no se sobrescribe al reintentar.

`requirements-multimodal.txt` fija la versión directa, no las transitivas. Para
reproducir el entorno completo con hashes se usa `security/requirements-ci.txt`
(incluye Pillow 13.0.0) y, cuando se pruebe T05, también
`security/requirements-blood-gas-ci.txt`; no se han cambiado esos locks.

## Adaptadores y formatos

| Adaptador | Entrada | Límite |
|---|---|---|
| ECG | PNG/JPEG y calibración declarada | Sin digitalización de señal ni medición automática validada |
| POCUS | PNG/JPEG, MP4/WebM | Clips/fotogramas solo como navegación; sin signos dinámicos validados |
| Radiografía | PNG/JPEG, vista/lateralidad declaradas | Revisión humana de proyecciones y campo completo |
| TC/RM | Captura PNG/JPEG o vídeo renderizado | No estudio DICOM completo, geometría ni valores HU |

Los DICOM se rechazan aquí. Reutilizar `render_rsna_ich_dicom.py` y protocolos
canónicos cuando existan acceso autorizado, desidentificación y revisión de
series/geometría. No se afirma que un adaptador técnico reconozca patologías.

Los vídeos no entran al proveedor de fotografías. La extracción guarda índices,
tiempos de presentación reales, orden, hash del padre y hash de cada derivado.
Todos los derivados heredan partición y agrupación del caso. No registrar un
fotograma como otro paciente. No se hacen afirmaciones sobre movimiento continuo.

Límites predeterminados de ingeniería: 64 MiB/archivo, 16 millones de píxeles,
60 segundos/vídeo, 3600 fotogramas y 30 segundos por proceso. No son estándares
clínicos. Archivos con audio, múltiples streams o adjuntos quedan bloqueados.
Firmas, extensión, hash, decodificación y límites deben pasar conjuntamente.
Se procesan copias temporales verificadas; no se conservan errores crudos del
códec ni metadatos libres en la salida.

Esto es una CLI para material sintético o autorizado previamente revisado. No es
un servicio de recepción de archivos hostiles: antes de ese uso se requieren
aislamiento de códecs, cuotas del SO, política de retención/borrado y revisión de
seguridad de dependencias. No se configura proveedor, entrenamiento ni red.

## Evaluación cuando existan casos válidos

```powershell
python clinical/scripts/multimodal_prototype.py evaluate bank.private.json finalized-evaluation.private.json --freeze-sha256 SHA256_CUSTODIADO_ANTES_DEL_REVELADO
```

Usar el flujo canónico de preparación/congelación/revelado existente. El puente
exige el conjunto completo de casos reales de la partición, una única tarea
estática y paciente independiente por caso, referencia booleana y revisor,
versiones de modelo/prompt/preprocesado, hash del protocolo y timestamps con zona
horaria en orden predicción ≤ congelación < revelado. Requiere adjudicación de
errores críticos de **todos** los casos con rúbrica identificada, no solo de las
discrepancias. Nunca rellenar campos pendientes con conformidades inventadas.

Reutiliza `calculate_blinded_image_metrics.py` sin modificarlo: sensibilidad,
especificidad e IC Wilson cuando sean calculables; si hay abstención o no
diagnóstico, suprime métricas binarias y conserva cobertura y recuentos. Añade
recuento/tasa de errores críticos adjudicados. No mezcla modalidades/tareas ni
calcula intervalos ingenuos con varios estudios de un paciente. La congelación
inmutable y la independencia efectiva necesitan custodia externa al JSON.

Además, `freeze_receipt_file` debe resolver dentro de la raíz del banco a un
recibo JSON cuyo hash coincida con el ancla suministrada por separado. El recibo
contiene `schema_version=1.0`, `run` idéntico, `frozen_at`, `protocol_file`,
`inputs_sha256` y `predictions=[{"id":...,"prediction":...}]` completos y en
el orden congelado. `inputs_sha256` es SHA-256 del JSON de `blinded_inputs`
serializado con `sort_keys=True,separators=(',', ':')` y UTF-8. Se comparan los
bytes del protocolo, los hashes/contextos de entrada, respuestas y versiones.
Si cambia cualquiera de ellos, no hay métricas. El ancla debe conservarse antes
del revelado por un custodio independiente (p. ej., registro firmado o commit
aprobado); suministrar un hash calculado después no demuestra cegamiento.

Banco, dataset y recibo se leen mediante una única frontera JSON UTF-8 acotada
a 8 MiB: claves duplicadas a cualquier profundidad, NaN/Infinity y números que
se desbordan o pierden a cero se rechazan. El hash se verifica sobre los mismos
bytes que se analizan, sin volver a abrir el recibo después de comprobarlo.
El hash de entradas incluye los textos de `limitations` y el estado de liberación:
si cambia una frase, el recibo anterior deja de corresponder al nuevo contrato.
Hay que versionar y congelar otro run, no reutilizar ni debilitar el ancla antigua.

No hay casos reales ciegos admisibles ni predicciones clínicas nuevas en esta
entrega. Las métricas de las pruebas unitarias son comprobaciones aritméticas
sintéticas; no son resultados de Emergency. `CLINICALLY_PENDING` se mantiene.
