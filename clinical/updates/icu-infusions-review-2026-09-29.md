# Perfusiones continuas UCI/Urgencias (adulto) — revisión 29/09/2026

Borrador v1.35. **No es validación clínica.** Requiere revisión humana (UCI, cardiología, farmacia hospitalaria) y cotejo local Portugal/Azores antes de cualquier uso asistencial.

## Resultado del índice real
v1.34 tenía 104 IDs. No existía un módulo dedicado a perfusiones continuas vasoactivas ni a sedoanalgesia continua de UCI: `cardiogenic-shock` contenía ejemplos de noradrenalina/dobutamina y `sepsis-shock` la posición de noradrenalina; `sedoanalgesia` cubre solo sedación procedimental. Se añaden dos IDs (total 106), sin duplicar contenido de rutas:

- `vasoactive-inotrope-infusions` (`modules/cardiovascular.md`)
- `icu-sedation-analgesia-infusions` (`modules/procedures-pharmacology.md`); se añadió una línea de remisión en `sedoanalgesia`.

## Fuentes accedidas (fecha de acceso 29/09/2026)
Vasoactivos:
- SCCM, Surviving Sepsis Campaign 2026 (Prescott et al., Crit Care Med 2026, doi:10.1097/CCM.0000000000007075), página oficial con recomendaciones: https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock-2026
- Resumen secundario de SSC 2026 (numeración, práctica NE 0,3 al añadir vasopresina): https://clinical-database.com/icu/guidelines/surviving-sepsis-campaign-2026/ssc-2026-part-3-hemodynamic-management/ y https://www.guidelinecentral.com/insights/mar-2026-sccmesicm-sepsis-guideline-spotlight/ y https://emcrit.org/emcrit/ssc-2026-sepsis-guidelines/ (solo apoyo; no fuente primaria).
- SCCM, SSC 2021 (Evans et al., Crit Care Med 2021;49:e1063-e1143): https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-guidelines-2021 ; resumen UIC: https://dig.pharmacy.uic.edu/faqs/2022-2/march-2022-faqs/update-what-are-the-2021-pharmacotherapy-updates-to-the-surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock/
- Noradrenalina, ficha FDA (premezcla, 2026): https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/214313s008lbl.pdf ; monografía AHFS: https://www.drugs.com/monograph/norepinephrine-bitartrate.html ; SmPC UK 1 mg/mL: https://www.medicines.org.uk/emc/product/5353/smpc
- Vasostrict (vasopresina), DailyMed: https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=b1147beb-743e-4c62-8927-91192447f8b8
- Adrenalina, ficha FDA: https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/209359s012lbl.pdf
- Dopamina en dextrosa, Pfizer (ficha EE. UU.): https://www.pfizermedical.com/dopamine-0/dosage-admin
- Dobutamina, Drugs.com dosage (derivado de ficha): https://www.drugs.com/dosage/dobutamine.html
- Milrinona, Pfizer (ficha EE. UU.): https://www.pfizermedical.com/milrinone-lactate/dosage-admin
- Levosimendán, SmPC Simdax: https://www.simdax.com/siteassets/simdax-spc.pdf
- Fenilefrina, DailyMed: https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=6d59ee85-08e5-452d-a09a-35fcc2a82b75&type=display
- Angiotensina II (Giapreza), DailyMed: https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c265d69a-3efe-4107-9a9e-e6fd3d531c48
- ESC HF 2021 (vía comentario EHJ-CVP sobre dosis de noradrenalina): https://academic.oup.com/ehjcvp/article/8/3/E11/6464132 ; resumen ACC: https://www.acc.org/latest-in-cardiology/ten-points-to-remember/2021/08/29/18/05/2021-esc-guidelines-for-hf-esc-2021

Sedoanalgesia:
- SCCM PADIS 2018 (Devlin et al., Crit Care Med 2018;46:e825-e873), página oficial: https://www.sccm.org/clinical-resources/guidelines/guidelines/guidelines-for-the-prevention-and-management-of-pa ; hoja del autor: https://nyschp.memberclicks.net/assets/docs/2019AA/Presentations/John%20Devlin%20Handout.pdf
- SCCM PADIS 2025 focused update (Lewis et al., Crit Care Med 2025;53:e711-e727): https://sccm.org/clinical-resources/guidelines/guidelines/focused-update-padis-guideline ; https://www.aacn.org/blog/key-takeaways-2025-update-padis-guidelines
- Propofol (Diprivan), DailyMed: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=d1ae9e26-ffd6-43df-bbd6-869cdede6afe
- Dexmedetomidina (Dexdor), EMA: https://www.ema.europa.eu/en/documents/product-information/dexdor-epar-product-information_en.pdf
- Remifentanilo, SmPC UK: https://www.medicines.org.uk/emc/product/794/smpc
- Midazolam 5 mg/mL, SmPC UK: https://www.medicines.org.uk/emc/product/15365/smpc
- Fentanilo 50 µg/mL, SmPC UK: https://www.medicines.org.uk/emc/product/6617/smpc
- Ketamina (Ketalar), SmPC UK: https://www.medicines.org.uk/emc/product/2231/smpc
- KSCCM 2021 PADIS (Seo et al., Acute Crit Care 2022;37:1-25): https://www.accjournal.org/journal/view.php?doi=10.4266%2Facc.2022.00094

## No accesibles (no se inventó contenido)
- Texto completo SSC 2026 en Springer (HTTP 429, rechazado por el proxy) y PMC (reCAPTCHA); SSC 2021 en PMC (sin permiso de acceso).
- ESC HF 2021 texto completo/tabla de inotrópicos (Wiley 403; PMC reCAPTCHA; PDF de PASCAR sin la tabla). Actualización focal ESC 2023 (PubMed reCAPTCHA): no se verificó si modifica inotrópicos/vasopresores.
- Fichas técnicas portuguesas (INFARMED/Infomed) y normas DGS: no consultadas en esta sesión; antecedente de 403 en DGS.
- Ficha EE. UU. de dexmedetomidina (Precedex) y monografías Drugs.com de vasopresina, dopamina, milrinona, fenilefrina y angiotensina II: sin permiso de acceso; se usaron fichas alternativas listadas arriba.

## Adoptado
- Posiciones SSC 2026: NE primera línea (fuerte, alta certeza frente a dopamina); añadir vasopresina con NE en escalada (condicional, moderada); adrenalina como tercer fármaco (condicional, muy baja); NE o adrenalina en disfunción cardiaca (nueva, muy baja); dobutamina+NE o adrenalina sola en hipoperfusión con disfunción cardiaca; en contra de levosimendán en shock séptico; inicio periférico antes que retrasar (condicional, muy baja); PAM 65 y 60–65 mm Hg ≥65 años.
- Dosis/diluciones de ficha técnica para cada vasoactivo y sedante; ejemplos a 70 kg con aritmética y prueba unitaria (`tests/test_skill.py`, funciones nuevas `fixed_dose_ml_h` y `weight_per_hour_ml_h`).
- PADIS 2018: analgesia primero, CPOT/BPS, sedación ligera (RASS −2 a +1), DSI o protocolo enfermero, propofol/dexmedetomidina sobre benzodiacepinas, ketamina 0,5 mg/kg + 1–2 µg/kg/min como adyuvante posquirúrgico. PADIS 2025: dexmedetomidina sobre propofol cuando priman sedación ligera/delirium; sin recomendación para benzodiacepinas en ansiedad ni antipsicóticos en delirium; movilización y melatonina.

## Discrepancias abiertas
1. Vasopresina: ficha EE. UU. inicia en shock séptico a 0,01 U/min (máx. 0,07), mientras práctica/ensayos usan 0,03 U/min fija. Se presentan ambas.
2. Noradrenalina: dosis inicial varía (ficha EE. UU. 8–12 µg/min; SmPC UK 0,4–0,8 mg/h base; ESC 2021 0,2 µg/kg/min, criticada; AHA citada 0,05 µg/kg/min). Borrador 0,05–0,1 µg/kg/min, individualizado.
3. **Noradrenalina base vs tartrato**: el SmPC UK expresa base; 8 mg de tartrato ≈ 4 mg base. Verificar etiqueta del producto portugués antes de fijar concentración.
4. Vía periférica: SSC la sugiere (2021: breve, vena en o proximal a fosa antecubital); SmPC UK exige vía central; ficha EE. UU. «vena grande». Se deja a política local con controles.
5. Diluyente de noradrenalina/adrenalina: fichas EE. UU. usan dextrosa; SmPC UK permite glucosa 5 %, NaCl 0,9 % o glucosalino.
6. Dexmedetomidina: SmPC UE sin bolo y máx. 1,4 µg/kg/h; la ficha EE. UU. (no reverificada) difiere. Advertencia SmPC de mortalidad en ≤65 años.
7. Opioides en perfusión UCI (fentanilo 0,7–10 µg/kg/h, morfina 2–30 mg/h, hidromorfona 0,5–3 mg/h) proceden de la tabla KSCCM 2021; el SmPC de fentanilo solo da pauta anestésica. En el resumen KSCCM el rango de dexmedetomidina «0,5–15 µg/kg/h» parece erróneo y **no** se adoptó.
8. Volúmenes: levosimendán (500 mL), dopamina premezclada (250 mL) y fenilefrina (500 mL, 20 µg/mL) siguen la ficha; no se forzó 100/200 mL sin compatibilidad verificada.
9. Umbral de triglicéridos para propofol: no verificado; no se fijó cifra.
10. Angiotensina II y levosimendán: autorización/comercialización y stock en Portugal/Azores no verificados.

## Pendientes locales Portugal/Azores
- RCM INFARMED de cada presentación (concentración, expresión base/sal, diluyentes, estabilidad), formulario del hospital/Azores y concentraciones estándar de bomba/biblioteca de fármacos.
- Política local de vasopresor periférico, extravasación (disponibilidad de fentolamina) y protocolo de sedación/analgesia de UCI (escalas, SAT/SBT).
- Normas DGS pertinentes (sépsis) — portal DGS previamente 403.
- Siguiente paso: perfusiones pediátricas (fuera de alcance de esta tarea).
