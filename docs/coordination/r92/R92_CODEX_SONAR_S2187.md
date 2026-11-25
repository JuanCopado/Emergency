# R92 · Sonar javascript:S2187

Estado: **NOT_VERIFIED** para el reanálisis remoto al publicar este corte.
Estado de la corrección y de sus pruebas locales: **PASS**.

PR105 comprobada: `7017c7d9abd282e65643313f55b77c7e2d988b85`.
Se conserva íntegramente su corrección en
`app/src/test/route-identity.test.mjs`: un test Vitest explícito y descubrible
por análisis estático, además de los seis casos compartidos que ya ejecutaban
Node y Vitest. No se sustituye `registerTests(test)` ni se elimina ningún negativo.

La prueba explícita presenta encabezado pediátrico correcto, dos controles
visibles y HTTP 404. Exige `HTTP_ERROR` en la salida real de `identityProblems`.
Es significativa: desactivar solo la guarda HTTP en una copia temporal del
helper hace fallar exactamente ese test; la copia se elimina y el test original
vuelve a pasar. No se muta el producto ni se confunde este fallo esperado con un
fallo del candidato.

Comandos reproducibles desde `app/`:

```bash
node --test scripts/route-identity.node-test.mjs
npx vitest run src/test/route-identity.test.mjs src/test/pediatric-outpatient.test.tsx --maxWorkers=2
```

Resultado local: Node 6 PASS; Vitest route-identity 7 PASS y pediatría 10 PASS.
Logs entregados: `identity-node.log`, `focal.log`, `s2187-mutation.log`.
Los resultados de `7d1833d` no acreditan `7017c7d` ni el candidato combinado.

Checks del SHA PR105:
[App UI QA](https://github.com/JuanCopado/Emergency/actions/runs/45576894021),
[Clinical QA](https://github.com/JuanCopado/Emergency/actions/runs/45576894162),
[Security and quality](https://github.com/JuanCopado/Emergency/actions/runs/45576893998).
El recibo final de la PR candidata identifica su conclusión, gate, número de
incidencias nuevas y vigencia de S2187. No se declara desaparición de la regla
por ejecutar únicamente pruebas locales. Si persiste, obtener regla, archivo,
línea y mensaje antes de un parche.

Sin NOSONAR, exclusiones, supresiones, cambios de umbral ni modificación de
estados de incidencias. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
