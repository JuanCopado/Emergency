# Revisión de nueve módulos seleccionados —14/11/2026

**Analizados9; cierre parcial:2GREEN/7YELLOW.** Registro actual112GREEN/19YELLOW.
La petición de pasar a verde queda registrada; los datos que faltan no se dan
por comprobados por esa autorización. No se solicitan otra vez los responsables
ni las decisiones locales que el propietario ya aportó.

| Módulo | Resultado | Motivo / siguiente comprobación concreta |
|---|---|---|
| 1. Selector arritmias/parada | 🟡 | Comprobar8 enlaces en navegador operativo; Chromium abortó por socket EPERM antes de navegar. Los4 destinos ya sonGREEN; nota antigua corregida. |
| 3. Sodio | 🟡 | Vincular concentrado real/RCM con recipiente, volumen final, acceso y condiciones de uso. Receta y preparación por enfermería ya registradas; no se vuelven a pedir. |
| 4. Ácido-base | 🟢 | Marco fisiológico/cálculo manual con unidades explícitas revisado. El perfil del analizador local sigue sin confirmar; no se aplica su intervalo automáticamente. |
| 11. Ortopedia | 🟢 | NICE NG37/NG38: fractura abierta, compromiso vascular/compartimental, imagen y alta revisados. No se validan por ello todos los procedimientos ni interpretación de imágenes. |
| 16. Vasoactivos/inotrópicos | 🟡 | Cerrar estabilidad/sistema de las mezclas candidatas por producto. Nombres, recetas y decisiones de uso inmediato/recambio ya conservados. |
| 17. Sedoanalgesia UCI | 🟡 | Cerrar correspondencia producto-concentración-recipiente/tiempo/compatibilidad; se mantienen límites Lipuro y decisiones locales. |
| 18. Escalas/calculadoras | 🟡 | 135 escalas completas en implementación;45 fórmulas. Cerrar matriz fuente/versión/población y trazabilidad individual de fórmulas; inventario no es nueva validación integral. |
| 19. Medicación pediátrica ambulatoria | 🟡 | 89/89 pautas inventariadas;45 URLs. Cerrar revisión por pauta y correspondencia producto/RCM portugués, sin exigir stock físico en Azores. |
| 20. Apoyo diagnóstico en notas | 🟡 | Validación clínica del uso previsto y revisión de privacidad/despliegue;92 reglas/60 casos sintéticos no prueban exactitud prospectiva ni conformidad legal. |

## Trabajo completado

Corregidas notas obsoletas del selector y el inventario de escalas. Añadidas
precauciones de fractura abierta, compartimentos e imagen oculta. Separado el
marco general ácido-base del perfil analítico local aún no verificado. Confirmado
que el documento EDPB recuperado es versión1 para consulta, sin certificar un
estado final por el cierre de comentarios. Conservados los bloqueos farmacológicos.

El inventario adjunto contiene las135 escalas,45 fórmulas,89 pautas pediátricas y
17 fichas con su trazabilidad/pediente real. Las45 fórmulas no tienen campoURL
individual; esto no demuestra que carezcan de respaldo en fuentes compartidas.
No se afirma nueva auditoría externa integral de todas esas entradas.

## Comprobaciones

PASS:704 Python,434 frontend,4 guías y7 controles globales;6 nuevas regresiones.
313 archivos protegidos y19 contratos bloqueados conservados. Navegador:
**BLOCKED**,0/8 casos ejecutados; se entrega el script repetible
`app/scripts/check-resuscitation-router.mjs`. No se modificó la configuración
global ni se eludió la restricción del entorno. Sin merge/push.

GREEN es referencia revisada, no calibración de equipo ni validación prospectiva.
CLINICALLY_PENDING global. No se incorporan datos identificables de pacientes
al inventario ni a las pruebas; los ejemplos de cálculo son sintéticos.

## Fuentes y registros

- NICE NG37: https://www.nice.org.uk/guidance/ng37/chapter/recommendations
- NICE NG38: https://www.nice.org.uk/guidance/ng38/chapter/recommendations
- ATS ABG physiology: https://site.thoracic.org/assemblies/cc/clinical-education/interpretation-of-abgs
- SfE published emergency hyponatraemia2022: https://www.endocrinology.org/media/xhrhxhxm/emergency-management-of-severe-and-moderately-severely-symptomatic-hyponatraemia-in-adult-patients-2022.pdf
- ESE/ERA draft for review: https://www.ese-hormones.org/media/nfca3mga/hyponatraemia-joint-guideline-draft-for-review.pdf
- EDPB01/2025 v1 consultation version: https://www.edpb.europa.eu/documents/guideline/guidelines-012025-on-pseudonymisation_en
- RCUK2025 PLS: https://www.resus.org.uk/professional-library/2025-resuscitation-guidelines/paediatric-basic-life-support-guidelines
- SSC adult2026: https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock-2026

- Matriz estructurada: `NINE_SELECTED_MODULES_REVIEW_2026-11-14.json`.
- Inventario completo: `NINE_SELECTED_MODULES_REVIEW_2026-11-14_INVENTORY.json`.
- QA: `NINE_SELECTED_MODULES_REVIEW_2026-11-14_QA.json`.
- Navegador: `RESUSCITATION_ROUTER_BROWSER_2026-11-14.json`.
