# R92 · Conciliación PR104 / PR105

Estado: **PASS** para composición, historia y preservación de contenido.
Integración en el receptor: **BLOCKED** hasta auditoría independiente.

Base: `bba8827bad22b67d8c38cfd83558920a1bb52cd1`, rama receptora
`codex/v144-international-scope-20261116`. Candidato aislado:
`codex/r92-combined-navigation-20261125`.

PR105 incorporada mediante merge `998b678`, conservando el commit
`7017c7d9abd282e65643313f55b77c7e2d988b85` y sus padres.
PR104 incorporada mediante merge `96b0ffa`, conservando
`fa376712297cce4297d64e30fc60853952e14bcd` y su historia.
No se ha fusionado ninguna PR en la rama receptora ni se ha usado force-push.
El SHA y árbol exactos del candidato publicado constan en el recibo final.

Comparación de deltas completos: PR104 cambia dos archivos; PR105 cambia trece.
Intersección vacía. Lista completa en [COMBINATION_PROOF.json](COMBINATION_PROOF.json).
PR104 es la única fuente de cambios en `PediatricOutpatient.tsx` y su test React.
R92 solo amplía el arnés de QA existente y la documentación de trazabilidad.

Preservación verificada byte a byte:

- Prefijo completo del componente previo a `export default function PediatricOutpatient`,
  incluido RegimenForm, representación de pautas y solicitud de cálculo, idéntico a la base.
- Catálogo generado y `app/src/pediatrics/catalog.ts`, idénticos a la base.
- Sin delta en clinical/modules, clinical/scripts, clinical/calculators,
  clinical/data ni clinical/references respecto a la base.
- Fixture R55, seis casos negativos compartidos y test S2187, idénticos a PR105.

SHA-256 del catálogo: `c6afd866d617eff564779c107c2fdb1e4234e0047d0cf11b1f217d46ad2f531b`.
No cambia dosis, pauta, fórmula, catálogo, regla asistencial, banco ni adjudicación.
main, RC1, producción y C12 intactos. Núcleo internacional sin selección inferida
de hospital o país. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
