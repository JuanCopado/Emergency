# C12 · protección de la rama internacional (PROPUESTA, sin aplicar)

Estado: `BLOCKED_ADMIN`. Esta sesión no tiene herramienta administrativa de protección; **nada de lo de abajo está aplicado**. C12 no se cierra sin comprobación remota.

## Lectura remota (23/11/2026, durante R26)
- `codex/v144-international-scope-20261116`: `protected: false` (listado de ramas de la API de GitHub).
- `main`: `protected: false` en la misma lectura. **No se ha modificado.** Debe revisarlo el administrador.

## Qué aplicar (Settings → Rules → Rulesets → New branch ruleset, o API)
Fichero: `docs/coordination/C12_RULESET_PROPUESTO_20261123.json`.
```bash
gh api -X POST repos/JuanCopado/Emergency/rulesets --input docs/coordination/C12_RULESET_PROPUESTO_20261123.json
```
- Sin `bypass_actors`: ninguna excepción permanente.
- Impide eliminación y force-push; exige PR, resolución de conversaciones y las 6 comprobaciones (semgrep, trivy, real-test-coverage, T05 Windows, T06 Ubuntu, sonarqube) con la rama al día.
- `Clinical QA` y `App UI QA` no se exigen como obligatorias porque tienen filtros de ruta: un workflow omitido por rutas quedaría pendiente y bloquearía entregas documentales (criterio de la auditoría R25).

## Decisión del propietario antes de aplicar
`required_approving_review_count: 1` impide al propietario fusionar sus propias PR (GitHub no permite autoaprobación) si es el único colaborador con escritura. Opciones sin crear bypass permanente: (a) un segundo revisor con permiso de escritura; (b) `0` aprobaciones manteniendo PR + comprobaciones + sin force-push. Es una decisión de gobernanza, no técnica; no se ha asumido.

## Verificación de cierre (obligatoria)
1. `gh api repos/JuanCopado/Emergency/rulesets` lista el ruleset `active` y registra su id.
2. `gh api repos/JuanCopado/Emergency/branches/codex%2Fv144-international-scope-20261116` devuelve `"protected": true`.
3. Un push directo de prueba a una rama de ensayo con la misma regla es rechazado (no probar sobre la rama real).
4. Registrar ids y SHA en `docs/coordination/C12_CIERRE_<fecha>.md` y avisar a Antigravity.
