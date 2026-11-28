# PR143 — decisión de integración preparada, no ejecutada

**Propuesta técnica: FAVORABLE para consideración y autorización específica del propietario, limitada al delta FAST manual + NOTE.** No es GO_RELEASE, aprobación médica ni permiso de fusión ya recibido. La PR permanece en borrador.

## Identidades y alcance exactos

- PR143: `a4fe1e2c509c188111c6216b31d6b592f8c4baa6`.
- Árbol: `b3cff20e8334e46c042c946ff584ea67f27b91a6`.
- Receptor: `codex/v144-international-scope-20261116` en `d3f8a792ca1cd43d022509caa5b43f38856af3ae`.
- Merge virtual GitHub: `35bc504489db419e2728da6ec9e2488c9bb8c0c2`, mismo árbol y padresd3f8+a4fe. Es simulación de GitHub, no fusión ejecutada.
- Cuatro archivos,88inserciones/14eliminaciones: Home, FreeTextWorkspace y sus dos tests. No motores, fórmulas/dosis, contenido clínico, exportadores, persistencia ni paquetesE/H.

FAST reutiliza búsqueda por nombre y mueve acceso a calculadora. NOTE respeta IME, impide aplicar/generar propuesta obsoleta, identifica edición y versiona feedback asíncrono. Copiar borrador y acceder a exportación canónica continúan disponibles; las ediciones libres no se exportan automáticamente.

## Evidencia existente reutilizada y control LIVE

| Control | Resultado y límite |
|---|---|
| CI por SHA |9/9checks,3/3workflows,8/8jobsSUCCESS, intento1; consultaLIVE conserva9checksSUCCESS. Cero reruns por esta continuación. |
| Sonar | Job141023777414: QUALITYGATEPASSED15:26:16UTC y EXECUTIONSUCCESS15:26:17UTC28/11. Fuentesapp cubiertas; exclusiones de tools no se convierten en validación del instalador, que no cambió. |
| Seguridad | Trivy0findings y Semgrep0findings en sus recibos; advertencias originales conservadas. |
| QA |44focales locales/3archivos, typecheck/lintPASS; AppUI remota1244/70archivosPASS. Tres negativos baseline y fallos de entorno/arnés se conservan separados; no se reinterpretan como PASS. |
| Navegador | DevToolsMCP real, sintético, a512y1024 observados; búsqueda/copia/edición/stale/retorno/exporttab. Sin prueba390, PDF/Word generado, WCAGglobal o cicloE/H. |
| Independiente | Antigravity exacta4fe SIN_BLOQUEO_CONFIRMADO, revisión estática/0suitesUI. Claude fue consulta de plan concurrente, no auditoría delSHA. «No regresiones» no se consume como garantía universal. |
| Receptor | LIVEd3f8 protegido, ruleset27994721 ACTIVE, seischecks requeridos strictApp15368, sinbypass, sinforce/delete. Los seis contextos están presentes ySUCCESS. |
| Revisión GitHub |0reviews y0comentarios inline en el corte; regla exige resolver hilos y0aprobaciones requeridas. Esto no sustituye la auditoría independiente ya registrada. Revalidar antes de una ejecución autorizada. |
| Estado | PR143open/drafttrue/mergedfalse, head/base exactos. No se retargeteó ni fusionó otraPR. |

Recibos privados ya custodiados: [CI exacta](https://drive.google.com/file/d/11IO-BHKFVv4zKI9epIReFDWlmlcSzpjK/view), [auditoría](https://drive.google.com/file/d/1h2p-KTjcOgTriTpfpVxMuZT_TyD7UGMk/view) y [expediente](https://drive.google.com/file/d/1EsVqP3pA7pznPg1aWi_1KZFdTDyQXVuY/view). No se repiten estos ensayos por modificar documentación.

## Autorización concreta preparada para presentar por el coordinador único

Texto propuesto, **no consentimiento recibido**:

> Autorizar únicamente la fusión mediante merge commit de PR143, HEAD a4fe1e2c509c188111c6216b31d6b592f8c4baa6, hacia codex/v144-international-scope-20261116 en d3f8a792ca1cd43d022509caa5b43f38856af3ae. Revalidar identidades, C12, hilos y controles; retirar borrador sólo dentro de esa ejecución autorizada. Detener ante deriva deSHA o fallo decontrol, sinbypass/force/rerun para ocultarlo. Verificar laCIposterior real. No fusionar adicionalmentePR142 u otrasPR, no tocar main/RC1, no desplegar ni reconstruir/refirmarE/H automáticamente. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

La respuesta a presentar sería SÍ/NO sobre esa operación técnica; no un nuevo voto clínico. Esta preparación no envía una pregunta duplicada ni modifica PR143. El coordinador único la presentará cuando corresponda.

Los tres residuales científicos, dosYELLOW y nueve contextos de privacidad no se declaran cerrados. Su falta de evidencia no se convierte en requisito hospitalario universal para este cambio de interacción sin algoritmo clínico nuevo. La integración técnica tampoco los resuelve ni permite uso asistencial.
