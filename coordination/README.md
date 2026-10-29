# Coordinación Emergency v1.44

PLAN_ID `1a10fda3a5b8295125a4b82088710a9ac31cc7361a32272f4e948d86eb3e0597`. Plan Maestro **v1.1.1-reconstruction-draft**, sin firma: publicar el registro no equivale a publicar/aprobar el plan completo. Estado del registro vigente: **PUBLISHED_DOCUMENTARY**. Estado clínico: **CLINICALLY_PENDING**.

## Publicación y revisión local

D-001C/R1 completó la preparación histórica sin commit ni publicación. D-001D creó/publicó el registro en `coordination/v144-control`, commit `37c9c7c003d43fc1992ae353ee45190483651ca3`; resultado PUBLISHED_PASS respaldado por su informe y SHA remoto verificado. Esta copia D-001E contiene correcciones **locales, no confirmadas ni publicadas**. El estado publicado se refiere al commit citado, no a los cambios de esta copia.

MASTER_LEDGER.csv es la única tabla de tareas; DECISIONS.csv registra decisiones y resultados asociados sin cambiar las aprobaciones históricas. CURRENT_STATE.md resume su significado; PLAN_MANIFEST.json conserva cronología, evidencia y alcance. Los informes no son otro ledger.

## Autoridad D-000 y límites

El propietario decide alcance y autorizaciones. D-001D autorizó solo un commit documental y push normal; no agentes reales, G0-B, D-006A/B ni I02. D-001E no autoriza commit/push/PR/merge/rebase. Cuatro P1 abiertos, 19 contratos bloqueados y GREEN sin renovar. No copiar contenido clínico ni datos de pacientes a coordinación.

La autorización permanente permanece **PENDING_EVIDENCE_LINK**. Las referencias `local_only:` se resuelven desde la raíz del clon y solo identifican copias externas temporales; no estarán disponibles automáticamente en GitHub. Hash de un texto no es firma. Un enlace duradero de autorización solo se incorporará al disponer de fuente real y autorización del propietario; no se inventan URLs o identificadores de conversación.

## Lectura de tablas

Ledger mantiene 12 columnas explícitas: AGENT es ejecutor o UNKNOWN; ENVIRONMENT es entorno o UNKNOWN; STATUS contiene el resultado. BASE_SHA/RESULT_SHA vacíos significan no acreditados/no aplicables, no ceros ni SHAs inferidos. OWNER es un rol declarado o UNKNOWN, no identidad institucional verificada. UPDATED_AT indica actualización documental, no fecha de ejecución. No hubo desplazamiento sintáctico en las filas originales; se corrigen AGENT semánticamente inválido y la atribución de resultados a H.

DECISIONS añade RESULT, RESULT_SHA, RESULT_EVIDENCE_REF y RESULT_EVIDENCE_SHA256 para separar aprobación de resultado. Los campos originales de las ocho decisiones previas permanecen idénticos. D-001D aparece una vez. El hash de autorización corresponde al texto local del mandato; el hash de resultado corresponde al informe D-001D disponible, no al ZIP PT-1D.

PT-1D/T0 y T1 tienen PASS limitado **declarado**, sin ejecución directa de Codex. PT-1D/H identifica el intento histórico BLOCKED por ausencia del ledger; su incorporación posterior no convierte ese intento en PASS. AGENT/entorno/fecha original no se inventan. Las fuentes de F/G y el ZIP no están disponibles; el informe documental antiguo de H sí está en Git, pero no es un reporte original de ejecución. Ver adenda en reports/TASK_REPORT_PT1D_H.md. PT-1 GLOBAL: NOT_VERIFIED.

## Cronología y evidencias

Preparación: 2026-10-29T13:50:48-05:00. Revisión documental: 2026-10-29T13:57:58-05:00; informe R1 emitido 2026-10-29T13:59:52-05:00. Commit de publicación: 2026-10-29T19:08:06Z; publicación constatada por el informe D-001D de 2026-10-29T14:10:28-05:00. La hora exacta del push no consta; no se iguala a la del commit. Corte operativo de esta revisión local: 2026-10-29T14:24:40-05:00. PLAN_MANIFEST conserva ambos cortes históricos y las marcas nuevas con significados separados.

## Consulta del registro

El commit publicado citado puede consultarse sin inferir nuevos permisos. Un lector debe verificar repositorio/rama/SHA y PLAN_ID, y leer estado, decisiones, ledger y norma de informes antes de actuar. La nueva revisión y su manifiesto de hashes solo podrán usarse como publicación después de auditoría y autorización posterior. Ninguna lectura autoriza ejecución, acceso adicional ni integración.

## Integridad reproducible, sin circularidad

Desde la raíz del repositorio, finalizar primero todos los documentos. Rechazar symlinks. Generar en orden lexicográfico de bytes:

```sh
find coordination -type f ! -path coordination/SHA256SUMS.txt -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > coordination/SHA256SUMS.txt
sha256sum --check coordination/SHA256SUMS.txt
```

Se incluyen todos los archivos regulares bajo coordination/, excluyendo **solo** SHA256SUMS.txt. No se normalizan bytes ni saltos de línea. Este archivo se referencia por nombre/alcance, nunca por un digest embebido en documentos cubiertos: así no hay dependencia circular. Tras cualquier edición, regenerarlo y verificar también la cobertura exacta. Los hashes nuevos son locales, no publicados.
