# Interoperabilidad e internacionalización · estado verificado · 26/11/2026

CLINICALLY_PENDING. No se activó ninguna función clínica.

## Interoperabilidad realmente implementada
| Estándar | Estado | Evidencia |
|---|---|---|
| FHIR | NO implementado | 0 coincidencias en `app/src` (TS/TSX) y `clinical/**/*.py`, `*.md` |
| HL7 v2 | NO implementado | ídem |
| DICOM / PACS | NO implementado. Reconocimiento mínimo | `imageReview.ts:58` marca `pdf`/`dicom` como contenedor excluido del envío; `clinical-images.md` declara «no añade visor ni integración DICOM/PACS» |
| Exportación de la nota | Existe `/api/clinical-note/export`; el catálogo de formatos no se auditó aquí | NO VERIFICADO |
Preparación técnica para FHIR/HL7/DICOM: inexistente en código. Hacerlo exige alcance, mapeo de campos y privacidad previos. No se crearon proyectos paralelos.

## Selector de país y separación de capas
- 14 países; los 14 con `product_review_status = NOT_PRODUCT_VERIFIED`.
- Idioma (`LANG_STORAGE_KEY`) y contexto de referencia (`emergency.reference-context.v1`) se guardan por separado. El esquema es estricto, sin país por defecto en modo internacional y sin organizaciones reales (`synthetic-a/b`).
- El contexto es solo metadato: «This schema cannot select or activate clinical regimens». Pruebas en `reference-context.test.ts`.
- Los nombres de país se localizan con `Intl.DisplayNames`, con el español como último recurso.
- Producto farmacológico y evidencia clínica no se derivan del idioma ni del país en este código.

## Traducciones
| Hallazgo | Estado |
|---|---|
| `Informe oficial / extraído` idéntica al español en `pt.clinical.json` línea 212 (debería ser «Relatório oficial / extraído») | **Defecto demostrado.** No corregido: `pt.clinical.json` es archivo de PR115 (Codex). Se pasa a Codex como hallazgo; una prueba que detecte cadenas largas idénticas al español está redactada en este expediente, no aplicada |
| `en.json` sin 5 claves y `zh.json` sin 10 (`*_many`, `*_one`) | **No es defecto:** son formas plurales CLDR inexistentes en inglés (`one/other`) y chino (`other`) |
| `pt` UI y `pt.clinical` con las mismas claves que `es` | Paridad completa |
| Textos clínicos pendientes de revisión humana | Sin cambio; la traducción técnica no equivale a revisión clínica |

Prueba propuesta para PR115 (no aplicada):
```ts
const ALLOWED = new Set(['Valores máximos permitidos','{{count}} de {{total}} módulos']);
it.each(['en','pt','zh'] as const)('%s has no long string identical to Spanish', lang => {
  expect(Object.entries(resources[lang]).filter(([k,v]) => v===es[k] && v.length>25 && !ALLOWED.has(v))).toEqual([]);
});
```
(Con la corrección de `pt` la prueba pasa; sin ella falla: comprobado localmente antes de revertir.)

## PTBR-PIX
Paquete de acceso a píxeles en pt-BR, **BLOQUEADO** hasta especificación literal completa (R43 lo excluyó del delta). No hay texto aprobado, por lo que no se redactó ni se activó ninguno. Contrato técnico preparado: ningún camino de código lo consume; cualquier texto pt-BR futuro debe entrar por `lab_locale=pt-BR` con la verificación `canonical-r27-v1.2` ya existente.
