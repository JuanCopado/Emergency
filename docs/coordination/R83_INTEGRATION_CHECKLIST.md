## R94 · corte vigente de coordinación

PR108 integrada en f67523e con CI postmerge completa PASS. PR104 y PR105 constan
integradas mediante el mismo merge. PR106 actualizada a 52881a6, árbol 1ba2630c,
con C12 seis checks y Clinical QA PASS; pendiente de reverificación independiente.
PR107 conserva su cierre histórico sin merge. Las entradas R83 siguientes
conservan su fecha y alcance. Banco 10/30 físicos, 20 pendientes y 0 adjudicados.
CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

# R83 · Registro de integración · 25/11/2026

**BLOCKED · CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.**

Receptor autorizado: `codex/v144-international-scope-20261116`,
`bba8827bad22b67d8c38cfd83558920a1bb52cd1`.
Núcleo internacional; solo trazabilidad técnica, sin cambios de recomendaciones,
algoritmos, dosis, adjudicaciones ni fechas científicas. Ninguna PR integrada por
este registro. C12 y las protecciones se conservan.

## Identidades y condiciones

| PR | HEAD observado | Dictamen y condición vigente |
| --- | --- | --- |
| [105](https://github.com/JuanCopado/Emergency/pull/105) | `7d1833d46c4381b028356cc5d05ef0c3b9350cbf` | R85 todavía no disponible, confirmado expresamente por el propietario el 25/11. No fusionar hasta satisfacer su condición. R80 registra una incidencia Sonar sin detalle recuperado. |
| [104](https://github.com/JuanCopado/Emergency/pull/104) | `fa376712297cce4297d64e30fc60853952e14bcd` | R84: MERGE_READY solo sobre `bba8827`; borrador. Tras integrar PR105: actualizar, repetir CI y obtener reverificación independiente del nuevo HEAD. |
| [106](https://github.com/JuanCopado/Emergency/pull/106) | `f45975190ba84bc840e11bb07c08e7a9675496a9` | El R84 recibido audita su padre `a24a62c`, no este HEAD. Reverificación independiente requerida; borrador conservado. |

Los [originales R84](r83/source/) se preservan literalmente y sus SHA-256 se
registran en [el manifiesto de fuentes](r83/SOURCES.json). Son evidencia aportada,
no instrucciones que sustituyan el encargo del propietario.

## PR106: condición R84 sobre a24a62c

R84 confirma las tres correcciones y 17 focales PASS en
`a24a62c2fe3c1a0dcf1cdeb180c6145f6ff92774`, árbol
`93ad4c427df3c0d924e54d0c29f8a9c72610065a`. Su condición exige cobertura y Sonar
en success sobre ese SHA y retirar Draft. Resultado definitivo observado:

- [Clinical QA 45559419364](https://github.com/JuanCopado/Emergency/actions/runs/45559419364): success.
- [Security and quality 45559419374](https://github.com/JuanCopado/Emergency/actions/runs/45559419374): cancelled.
- `real-test-coverage`, job `139019251153`: cancelled.
- `sonarqube`, job `139022501686`: cancelled.

**La condición no se cumplió.** Una cancelación no acredita PASS ni un defecto
de código. No reejecutar un SHA histórico para sustituir los controles del HEAD
actual ni trasladar el dictamen al sucesor.

El sucesor `f459751` añade tres pruebas por recibo físico y documentación;
`intake_r68.py` e `image_structure.py` son idénticos a `a24a62c`.
No se repite ni se modifica la corrección ya auditada. La entrega existente
[solicita reauditoría del sucesor](https://github.com/JuanCopado/Emergency/pull/106#issuecomment-7154765351).
La [conciliación R83](https://github.com/JuanCopado/Emergency/pull/106#issuecomment-7154882608)
registra el informe recibido y la identidad correcta. El acuse R78 confirma
20 focales PASS también con Pillow 12.3.0; no equivale al dictamen Antigravity.

Controles del sucesor: [C12 45560384544](https://github.com/JuanCopado/Emergency/actions/runs/45560384544)
y [Clinical QA 45560384502](https://github.com/JuanCopado/Emergency/actions/runs/45560384502).
Sus resultados finales se conservan en el recibo de esta entrega; no se atribuyen
a `a24a62c` ni sustituyen la reverificación independiente.

## PR105: R85 pendiente

La [evidencia R80](https://github.com/JuanCopado/Emergency/pull/105#issuecomment-7154592170)
identifica el check Sonar `138801917451`: gate passed, una incidencia nueva y
una anotación. El [workflow C12](https://github.com/JuanCopado/Emergency/actions/runs/45492160761)
y los workflows UI/Clinical QA terminaron en success para `7d1833d`.
**Gate passed no significa cero incidencias ni completa R85.**

Por instrucción expresa del propietario se intentó:

```bash
gh api repos/JuanCopado/Emergency/check-runs/138801917451/annotations
```

Resultado: exit 1, `Forbidden`. El conector disponible no expone anotaciones.
El navegador no pudo conectarse y la consulta pública de Sonar no resultó
accesible. No se obtuvo la regla, issue key, severidad, ubicación ni causa.
Clasificación e impacto: **NO VERIFICABLES**. No se inventa una incidencia ni
se prepara un parche especulativo. El documento R85 no está disponible y no se
emite MERGE_READY para PR105.

Para resolver: aportar el detalle de la anotación/incidencia o acceso de lectura
funcional; clasificar su impacto y obtener el dictamen correspondiente. Si el
dictamen requiere código, preparar el delta concreto y repetir CI y auditoría
independiente sobre el nuevo SHA. No cambiar umbrales, exclusiones ni estados
de incidencias para eludir esta condición.

## Secuencia exigida y checklist

- [x] Verificar receptor, SHA de PR104/105/106 y originales R84.
- [x] Comprobar resultado definitivo de cobertura/Sonar de `a24a62c`: ambos cancelados.
- [x] Identificar el nuevo HEAD de PR106 y preservar las correcciones existentes.
- [x] Intentar recuperar la anotación PR105 mediante la CLI solicitada y registrar el límite.
- [ ] Completar R85 y habilitar PR105 con dictamen vigente.
- [ ] Obtener dictamen independiente favorable para PR106 sobre su HEAD actual y CI completa.
- [ ] Retirar Draft y fusionar **PR105** con SHA esperado; verificar CI postmerge del receptor exacto.
- [ ] Actualizar **PR104** sobre ese receptor; repetir CI y reverificación independiente del nuevo HEAD.
- [ ] Fusionar PR104 con SHA esperado; verificar CI postmerge antes de seguir.
- [ ] Actualizar **PR106** sobre ese receptor; repetir CI y reverificación independiente del nuevo HEAD.
- [ ] Retirar Draft y fusionar PR106 con SHA esperado; verificar CI postmerge.
- [ ] Registrar SHA, árbol, checks, dictámenes y resultado final de cada integración.

La secuencia **no se ha iniciado**: la condición pendiente de PR105 es un
prerrequisito explícito del propietario. No se cambian ramas dependientes antes
de conocer el receptor integrado, ni se afirma CI postmerge sin un merge real.
Este registro documental va en una rama aislada; no cambia main, producción,
C12, banco, manifiesto, sellos, distribución 8/4/18 ni las 0/30 adjudicaciones.

El cierre técnico de las correcciones existentes se conserva separado del cierre
de integración. R5-1, R5-2 y G05 no se cierran por esta entrega.
