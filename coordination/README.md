# Coordinación Emergency v1.44

Candidato local al centro compartido de coordinación para ChatGPT, Codex y Claude Code. PLAN_ID `1a10fda3a5b8295125a4b82088710a9ac31cc7361a32272f4e948d86eb3e0597`; Plan v1.1.1-reconstruction-draft. **No publicado. CLINICALLY_PENDING.**

## Autoridad D-000 y registro único

El propietario decide alcance, aprobaciones y publicación. MASTER_LEDGER.csv es el ledger previsto de tareas; DECISIONS.csv separa decisiones, estados y límites; CURRENT_STATE.md resume el corte; PLAN_MANIFEST.json identifica el borrador y evidencia; REPORTING_STANDARD.md define EMERGENCY-REPORT-001. Los reports solo acreditan lo realmente comprobado en su alcance.

Esta copia no sustituye automáticamente un registro publicado ni autoriza agentes reales, G0-B, D-006A/B o I02. Mantener cuatro P1 abiertos, 19 contratos bloqueados y GREEN sin renovar. No trasladar código ni contenido clínico a coordinación.

## Reglas de modificación

Solo mediante encargo del propietario, sobre una base verificada, sin tocar ramas ajenas. Una propuesta debe etiquetarse pendiente; APPROVED solo con instrucción trazable de la autoridad. Identificar PLAN_ID, tarea, agente/entorno y SHAs aplicables. RESULT_SHA queda vacío cuando no hay commit de resultado. Evidencias externas se referencian por nombre/hash; no añadir ZIP sanitizado ni datos sensibles a Git. No interpretar procedencia documental como firma.

En D-001C solo se preparan archivos y diff: **sin commit, push, PR ni merge**. El informe de entrega está fuera del clon, en la carpeta temporal autorizada, por lo que el delta del repositorio permanece exclusivamente bajo coordination/.

## Consulta futura por Claude Code

Después de una publicación autorizada por separado, el propietario comunicará repositorio/rama y SHA exacto del registro. El agente deberá comprobar esos identificadores y leer README, PLAN_MANIFEST, CURRENT_STATE, DECISIONS, MASTER_LEDGER y REPORTING_STANDARD en ese SHA antes de actuar. Si el PLAN_ID, la autoridad o la tarea no coinciden, registrar bloqueo y no asumir permisos. Consultar el registro no equivale a estar autorizado para ejecutar tareas, cambiar decisiones o iniciar integración. El procedimiento no afirma que la rama exista hoy en GitHub.

## Evidencia y límites

La fuente permanente del mandato está **PENDING_EVIDENCE_LINK**. El manifiesto conserva por separado el hash calculado del texto local y su ubicación temporal fuera de Git; esa ruta no será accesible automáticamente al publicar y no es una autorización duradera ni una firma.

**Propuesta, no ejecutada:** el propietario puede aportar una decisión/documento de autorización sanitizado en una ubicación duradera acordada. Si se elige GitHub, después de la autorización separada y la existencia real del documento/commit, registrar su enlace permanente al commit y archivo efectivos, fecha, alcance y hash. Antes de ello no generar URL, SHA de publicación, firma ni identificador de conversación. Sustituir PENDING_EVIDENCE_LINK solo tras comprobar la referencia y su correspondencia con el alcance autorizado. No añadir ahora otro registro o archivo de autorización.

PT-1D tiene hash y PASS limitado declarados por el propietario. No se ha aportado informe identificable de un verificador tercero; esa verificación no se declara acreditada. Codex no dispone del ZIP, no recomputó su hash ni repitió el ensayo. Una comprobación documentada de tercero y una comprobación directa de Codex son categorías distintas y deben citar sus propias evidencias. PT-1 GLOBAL sigue NOT_VERIFIED. No se ejecutan herramientas del repositorio, tests clínicos o instalaciones para preparar estos documentos.
