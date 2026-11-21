# R5 · Consolidación técnica y límites · 21/11/2026

Estado **CLINICALLY_PENDING**. Se conservan 131 módulos, 129 GREEN /2 YELLOW /0 RED y todas las aceptaciones previas. La entrega se dirige exclusivamente a `codex/v144-international-scope-20261116`. No autoriza uso asistencial.

## HECHO

Receptor real `95c5f25f755e27628baf8e5f69f60df2b308ea92`, árbol `8dae69dad71b0b917a2caa35b81a286e4bbf5c74`. Se recuperaron las PR55–60; PR60 ya estaba integrada. Las ocho tareas CI del receptor estaban satisfactorias. Esa CI constituye la línea de base, no la comprobación del nuevo candidato.

- [Nota offline](../../clinical/qa/R5_NOTE_SHADOW_EXTENSION_20261121.md). Codex conservó 60 casos históricos y amplió el banco a153. Un revisor independiente reprodujo las153 salidas y sus huellas. La marca autorizada existe exclusivamente en el artefacto de investigación. El ejecutable reproducible y sus salidas se entregan como investigación externa. Su nueva prueba instrumentada agotó90segundos en CI y240segundos en Windows. Se conserva ese fallo y se retiran del candidato ambos ejecutables añadidos; las pruebas y configuración de cobertura previas del producto no se modifican.
- [Seguridad y Claude Code](../../clinical/qa/R5_SECURITY_REVIEW_20261121.md). Corrección mínima de `python:S8786` en el reconocimiento de cercas de Markdown.19/19 pruebas agudas y230 fragmentos equivalentes en Windows.43/43 comprobaciones focales M10. Claude Code web real inspeccionó la base y la propuesta, ejecutó sus propias pruebas y consideró equivalente la corrección, sin P0/P1 en su alcance.
- [Auditoría científica de nota](R5_NOTA_AUDITORIA_CIENTIFICA.md) y [de imágenes](R5_IMAGEN_AUDITORIA_CIENTIFICA.md). Gemini3.8 Flash High realizó11 búsquedas propias y entregó una respuesta original. Work/Codex cotejó las secciones primarias y documentó sus discrepancias. Los registros prueban búsquedas con resúmenes; no una lectura íntegra de todas las fuentes por Gemini.
- [G05](R5_G05_20261121.md). Nuevas19/19 huellas verificadas y pruebas previas reutilizadas para archivos idénticos. El alcance público y los derechos de fuentes quedan separados del laboratorio.
- [Windows](../../clinical/qa/R5_WINDOWS_QA_LIMITATIONS_20261121.md). Evidencia previa identificada por candidato y componentes. Antigravity emitió un plan prospectivo. No se le atribuye una ejecución de QA que no realizó.

## FALLO

La incidencia Sonar de la base seguía abierta pese a su Quality Gate satisfactorio. Se entrega la corrección y su prueba de equivalencia. El cierre requiere que un análisis posterior la dé por resuelta; no se marca aceptada ni se excluye código.

La incertidumbre puede llevar SCA a HIGH. Se observó vocabulario ES/EN incompleto, contradicción no resuelta y cuatro destinos de `must_not_miss` sin regla ejecutable. Son hallazgos clínicos materiales, documentados e inactivos. El filtro de falsa tranquilidad M10 tiene alcance categorial y lingüístico limitado. No se amplía automáticamente a otras modalidades.

## PENDIENTE

| Frente | Estado del trabajo entregado | Condición pendiente |
|---|---|---|
| A | TECHNICALLY_VERIFIED para el observador; CLINICAL_REVIEW_REQUIRED para seguridad diagnóstica | Cohorte autorizada, referencia clínica independiente y márgenes previos; no existe estimación clínica a partir de sintéticos. |
| B | READY_FOR_INTEGRATION para la corrección | CI/Sonar del candidato publicado; P2/P3 residuales y limitaciones en el dictamen. |
| C | TECHNICALLY_VERIFIED como expediente metodológico | Congelar ficha, versión, datos, criterios y referencia antes de evaluar uso real. |
| D | BLOCKED para la nueva QA gráfica y locución literal | Sesión Windows segura sin entrada humana concurrente; imagen pequeña y nuevo guardado nativo del compuesto. |
| E | G05 global BLOCKED; laboratorio TECHNICALLY_VERIFIED | Consumidores futuros, procedencia/derechos, plataforma, privacidad y dictamen del entorno concreto. |

Computer Use detectó entrada humana y bloqueó el control. La revisión automática rechazó iniciar otro perfil Edge desde terminal con «blocked by policy», sin razón adicional. No se eludió el rechazo ni se grabó audio. El PDF nativo previo sigue conservado; no es un guardado nuevo R5. La preparación técnica no alcanza el cierre completo R5 mientras falten estas comprobaciones.

## SIGUIENTE

Publicar el candidato compuesto en PR de desarrollo, verificar su CI, Sonar, Semgrep y Trivy, incorporar únicamente los deltas técnicos aptos y comprobar de nuevo el commit resultante. El recibo final debe identificar por separado el HEAD de PR y el merge. Las salidas y hashes de las ejecuciones se conservan en el expediente externo R5 y los checks de GitHub.

Los módulos padre de nota e imagen permanecen YELLOW. La autorización silenciosa SCA v1 continúa vigente en su alcance original. G05 global abierto y ausencia de evidencia clínica independiente impiden un dictamen de liberación asistencial.

## Seguimiento de QA de PR61

El [registro de QA nativa](../../clinical/qa/PR61_NATIVE_PDF_NARRATOR_QA_20261121.md) incorpora PDF Edge de cuatro páginas y cotejo de Narrador aportado por el usuario sobre b5918ffa. Incluye R2, JSON original, audio, capturas y huellas. Permanecen los límites literales de unidades/comparador y la revisión gráfica pendiente fuera de esos casos. CLINICALLY_PENDING.
