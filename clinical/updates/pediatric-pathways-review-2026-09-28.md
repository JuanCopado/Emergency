# Revisión focal de rutas pediátricas — 2026-09-28

## Comprobación del índice

El manifiesto v1.32 tenía solo el módulo genérico `pediatric-emergencies`; no existían rutas separadas para lactante febril, bronquiolitis, crup, deshidratación/choque o estatus epiléptico pediátrico. Se añadieron cinco IDs al bundle existente `modules/special-populations.md`, se actualizó el router y se conservó el módulo genérico como capa común. El índice pasa de 93 a 98 IDs. No se duplicaron vías clínicas existentes; `status-epilepticus` continúa cubriendo el flujo transversal/no pediátrico y se deriva explícitamente a la vía específica pediátrica cuando aplica.

## Fuentes y decisiones de alcance

1. **Lactante febril ≤90 días** — CPS, *Management of well-appearing febrile young infants aged ≤90 days*, publicado 2023 y actualizado 27/05/2026: https://cps.ca/en/documents/position/management-of-well-appearing-febrile-young-infants-aged-90-days. Temperatura rectal ≥38.0 °C, evaluación por edad 0–28/29–60/61–90 días, riesgo de IBI, cultivo urinario y biomarcadores; la evaluación viral no reemplaza la evaluación bacteriana. El algoritmo se limita a nacido a término, sano y bien aparente. La guía AAP 2021 se limita a 8–60 días, nacido a término y bien aparente: https://doi.org/10.1542/peds.2021-052228.
2. **Bronquiolitis** — NICE NG9, umbrales de oxígeno actualizados en agosto 2021: https://www.nice.org.uk/guidance/ng9; CPS, declaración de bronquiolitis para 1–24 meses: https://cps.ca/en/documents/position/bronchiolitis. Se integra diagnóstico clínico, apoyo de alimentación/oxígeno, estratificación por edad/comorbilidad y no uso rutinario de fármacos/imágenes. Los umbrales NICE para oxígeno persistente en aire ambiente son <90% para la mayoría ≥6 semanas y <92% si <6 semanas o hay condición de riesgo.
3. **Crup** — CPS, *Acute management of croup in the emergency department*: https://cps.ca/en/documents/position/acute-management-of-croup; RCH, *Acute upper airway obstruction*: https://www.rch.org.au/clinicalguide/guideline_index/acute_upper_airway_obstruction/. Dexametasona 0.6 mg/kg dosis única, máximo 16 mg según RCH; adrenalina nebulizada como medida temporal en moderado-grave y observación 2–4 h por recurrencia. Se destacan diagnósticos alternativos y escalada precoz de vía aérea.
4. **Deshidratación/choque pediátrico** — NICE NG254 (sepsis <16 años, 2025): https://www.nice.org.uk/guidance/ng254; NICE NG29 (líquidos IV pediátricos): https://www.nice.org.uk/guidance/ng29; RCH gastroenteritis/deshidratación: https://www.rch.org.au/clinicalguide/guideline_index/Gastroenteritis/ y https://www.rch.org.au/clinicalguide/guideline_index/Dehydration/. Rehidratación oral/NG si no hay shock; en shock sospechado, cristaloide isotónico sin glucosa 10 mL/kg en <10 min y reevaluar; NICE NG254 limita cada bolo en sospecha de sepsis a 250 mL y pide considerar comorbilidad. No se transfieren esos volúmenes a DKA, neonatos, hemorragia, quemaduras o choque cardiogénico.
5. **Estatus epiléptico convulsivo pediátrico** — HSE National Clinical Guideline CDI/0277/1.0/2025, efectiva 15/10/2025 y revisión prevista 2028: https://www2.healthservice.hse.ie/files/584/; NICE NG217: https://www.nice.org.uk/guidance/ng217. Se integra tratamiento desde 5 min, máximo dos dosis totales de benzodiacepina (incluidas prehospitalarias), levetiracetam 40 mg/kg (máx. 3 g) como segunda línea y escalada crítica. El HSE cubre 1 mes–18 años y explícitamente excluye neonatos <1 mes y aumento de crisis en epilepsia conocida; se preserva esa limitación. Dosis de benzodiacepinas del HSE: midazolam bucal 0.3 mg/kg en 1–3 meses (máx. 2.5 mg), bandas de edad en mayores; lorazepam IV 0.1 mg/kg (máx. 4 mg).

## Cambios realizados

- Se añadieron `febrile-infant-0-90-days`, `bronchiolitis`, `croup`, `pediatric-dehydration-shock` y `pediatric-status-epilepticus`.
- Se actualizó el router para derivación específica y se mantuvo `pediatric-emergencies` para todas las consultas pediátricas como capa de evaluación/desarrollo/peso/seguridad.
- Registro de evidencia: cinco módulos nuevos en yellow por necesitar revisión humana, disponibilidad/formulario, rutas locales y validación; `pediatric-emergencies` pasa a yellow porque su cobertura cambió.
- No se añadieron casos de regresión; el test estructural del manifiesto actualiza el recuento esperado de 93 a 98.

## Límites y pendientes

Fuentes internacionales (NICE/CPS/HSE/RCH) no equivalen a aprobación DGS ni a protocolo de hospital portugués/Azores. Verificar con Pediatría, Neonatología, Neurología/Anestesia, farmacia local, concentraciones disponibles, vía de transferencia y soporte de cuidados intensivos. Revisión dirigida documental, no sistemática; no hay validación prospectiva de resultados.
