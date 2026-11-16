# EMERGENCY — Procedimiento local de selección de agujas IM: revisión de seguridad

**Fecha:** 2026-11-16. **Procedencia:** tabla comunicada por el propietario del proyecto, clasificada `OWNER_REPORTED_LOCAL_PROTOCOL`. **No representa firma independiente ni resultados de ensayos físicos.**

## 1. Tabla de selección aportada por el propietario

| Población | Longitud comunicada | Calibre/color habitual comunicado | Aplicación al contrato 3 |
|---|---|---|---|
| Neonatos y prematuros (<28 días o <3 kg, según tabla local) | 16 mm | 25 G, naranja | **Dentro**, pero adaptar a anatomía, no usar edad/peso como sustituto de evaluación |
| Lactantes 1–12 meses | 25 mm | 23 G azul o 25 G naranja | **Solo de 1 a <6 meses**; 16 mm también candidato en prematuros ≤2 meses/muy pequeños |
| Niños 1–5 años | 25 mm | 23 G azul o 25 G naranja | **Fuera del contrato 3**; futura conciliación pediátrica |
| Escolares/adolescentes 6–18 años y <60 kg | 25 mm | 22 G negro o 23 G azul | **Fuera del contrato 3**; futura conciliación pediátrica |
| Adolescentes con obesidad o panículo adiposo grueso | 38 mm | 21 G verde o 22 G negro | **Fuera del contrato 3**; longitud debe seleccionarse por constitución, no solo por umbral de 60–70 kg |

**El color de una aguja no garantiza su longitud ni calibre; verificar ambos en el envase.** No crear selección automática por edad/peso sin revisión clínica de la técnica y del producto concreto.

## 2. Revisión crítica frente a fuentes oficiales

- [RCUK Emergency Treatment of Anaphylaxis (2021), apéndice 2](https://www.resus.org.uk/media/337/download) describe 25 mm habitual, 16 mm para prematuros/lactantes muy pequeños, 38 mm en algunos adultos. Aclara que la elección técnica toma como referencia recomendaciones de vacunación y que no existe evidencia específica para una única técnica de anafilaxia IM.
- [CDC, Vaccine Administration: During Vaccination](https://www.cdc.gov/vaccines/hcp/administration/during.html) recomienda a neonatos ≤28 días 16 mm/22–25 G y a lactantes 1–12 meses 25 mm/22–25 G, siempre con selección individual; técnica IM perpendicular y vasto lateral del muslo. **Referencia anatómica extrapolada de vacunación**.
- [Australian Immunisation Handbook](https://immunisationhandbook.health.gov.au/resources/tables/table-recommended-needle-size-length-and-angle-for-administering-vaccines) reconoce 16 mm/23–25 G para prematuros hasta dos meses y/o muy pequeños; 25 mm/22–25 G como pauta general. También procede de vacunación.
- [CDC, vaccine administration best practices](https://www.cdc.gov/vaccines/hcp/imz-best-practices/vaccine-administration.html) desaconseja aspiración rutinaria en vacunación IM; el principio no sustituye un procedimiento local específico de adrenalina aprobado por el equipo clínico.

## 3. Decisiones de software que sí deben respetarse

1. **Contrato 3 exclusivamente:** edad cronológica <6 meses, adrenalina 1 mg/mL **sin diluir**, 0,01 mg/kg **IM**, tercio medio anterolateral del muslo; **no** exportar órdenes mientras no supere control de precisión, revisión y QA.
2. **No aceptar como regla universal** que 25 mm siempre alcance el músculo, que 12,7 mm sea clínicamente inviable en todo paciente/indicación, ni que cualquier aguja de 23–25 G garantice menor espacio muerto.
3. **Restricción local declarada:** no utilizar para adrenalina IM del contrato 3 dispositivos premontados de insulina con aguja SC de 12,7 mm; el hecho de tener bajo espacio muerto no certifica su idoneidad anatómica.
4. **No fijar inyección en 1–2 segundos** como requisito: falta evidencia directa que respalde esa cifra universal; el tratamiento no debe demorarse y la técnica corresponde a profesionales competentes.
5. **No hacer cálculo automático de aguja** ni reducir la dosis para adaptarse a la graduación; exigir selección profesional de aguja adecuada y volumen realmente entregado, verificando el conjunto jeringa+aguja.
6. **No extrapolar recomendaciones de mayores de 6 meses o adultos** al contrato 3; revisar esas filas en los protocolos específicos cuando corresponda.

## 4. Controles y evidencias faltantes

- Referencias exactas y lotes de BD Plastipak, ZARYS dicoTUBER y Terumo disponibles, junto a aguja realmente seleccionada para IM neonatal/lactante.
- Ensayo físico de precisión de 0,025; 0,032; 0,050; 0,076 mL con producto sustituto y dispositivos reales, con límites definidos por Farmacia antes del ensayo, registro de espacio muerto, pérdidas y error entre operadores.
- Atestaciones trazables de Farmacia, Enfermería y revisión pediátrica/urgencias para la técnica y alcance de <6 meses.
- QA de código integrado, interfaz, regresiones, negativas de concentración/vía y exportaciones; política de STOP si no puede medirse el microvolumen.

**Estado:** procedimiento declarado y revisado documentalmente; **NO_VALIDATED_FOR_PRODUCTION**; contrato 3 **BLOCKED**, global **CLINICALLY_PENDING**, sin cambios en `main` ni en otros contratos.
