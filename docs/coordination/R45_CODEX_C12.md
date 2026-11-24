# R45 · C12, estado efectivo de protección de la rama internacional

**CLINICALLY_PENDING.** Corte remoto del 24/11/2026. Base cotejada `771ed2bbcc9b0457f5bb8ef75089e236fda7c1d2`. Esta rama actualiza [PR92](https://github.com/JuanCopado/Emergency/pull/92), el expediente independiente que ya existía para C12.

| Control | Resultado | Evidencia observada |
| --- | --- | --- |
| Ruleset activo en la rama internacional exacta | PASS | ID `27994721`, target branch, incluye exclusivamente `refs/heads/codex/v144-international-scope-20261116` |
| PR obligatoria, bloqueo de borrado y force push | PASS | Reglas `pull_request`, `deletion`, `non_fast_forward` |
| Seis checks exigidos por GitHub Actions | PASS | `semgrep`, `trivy`, `real-test-coverage`, `sonarqube`, T05 Windows y T06 Ubuntu, todos con `integration_id: 15368` |
| Bypass | PASS | `bypass_actors: []`, `current_user_can_bypass: never` |
| Exigir que la PR esté al día de la base | FAIL | `strict_required_status_checks_policy: false` frente a `true` en la definición propuesta |
| Exigir resolución de conversaciones | FAIL | `required_review_thread_resolution: false` frente a `true` en la propuesta PR92 |
| Cambiar reglas administrativas | BLOCKED | El conector disponible permite leer rulesets y operar en PR. No ofrece escritura de rulesets. |
| Aprobación nativa y revisiones caducadas | Decisión registrada en la configuración efectiva | 0 aprobaciones, sin invalidación automática. La propuesta histórica ofrecía alternativas 0/1. La auditoría independiente sigue siendo condición específica de PR100. |

[Ruleset vigente](https://github.com/JuanCopado/Emergency/rules/27994721) · [Definición histórica](BRANCH_PROTECTION_PENDING_20261122.md) · [Propuesta original de PR92](C12_RULESET_PROPUESTO_20261123.json).

## Aplicación restante

Los dos controles discrepantes corresponderían a una actualización del ruleset existente. El JSON de PR92 se conserva como propuesta histórica y su POST original queda obsoleto. La comprobación administrativa posterior debe volver a leer el ID `27994721` y verificar los dos campos, la rama objetivo, los seis checks y el bypass vacío. `main` queda fuera del alcance. La lectura de API permite verificar configuración y no requiere intentar un borrado, force push o push directo de prueba.

El merge previo de PR99 usó la PR y el SHA candidato verificado después de que los seis checks y Clinical QA aprobaran. El push posterior a `771ed2bb` también quedó en verde. [Security and quality](https://github.com/JuanCopado/Emergency/actions/runs/45429641949) · [Clinical QA](https://github.com/JuanCopado/Emergency/actions/runs/45429641995).
