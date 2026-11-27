# Auditoría primaria focal — cinco anclajes

Fecha del cotejo: 27/11/2026. Ejecutor: Codex, contraste separado de la entrega Gemini `9fc3a430f5c9115e`. Se verifican únicamente afirmaciones concretas; no se atribuyen lecturas integrales, revisión legal general ni validación clínica. No se cambian runtime, dosis, producto, estados o `last_checked`. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

| Fuente primaria | Localizador y acceso observado | Resultado documental admisible | Límite o discrepancia |
|---|---|---|---|
| [Baxter / emc, producto 1861](https://www.medicines.org.uk/emc/product/1861/smpc) | SmPC §4.2; texto revisado junio 2023, página emc actualizada 10/03/2025. HTML obtenido. | La pauta de tratamiento del producto para adultos, mayores y adolescentes corresponde a 7–10 mmol/h con control ECG; el máximo de la ficha aparece como intervalo 15–20 mmol/h. | No convertir «10 habitual» en regla universal ni seleccionar 20. Es KCl 0,15 % con NaCl 0,9 %, no cualquier preparación. Conserva contexto renal, acceso y monitorización. |
| [NICE NG38](https://www.nice.org.uk/guidance/ng38/chapter/recommendations) | §1.2.3. HTML y PDF oficiales devolvieron 403; fragmento indexado del dominio NICE obtenido. | El fragmento apoya considerar MRI como imagen inicial ante sospecha de fractura de escafoides tras exploración clínica completa. | Verificación provisional del fragmento; no lectura de la página ni PDF. «Considerar» no equivale a obligación universal ni autoriza extender otras reglas. |
| [AAO-HNSF 2020 / PMID 31910111](https://pubmed.ncbi.nlm.nih.gov/31910111/) | Abstract: población y KAS 2, 3a, 3b, 11. PubMed directo sin contenido útil; abstract primario indexado y fragmento editorial coincidente obtenidos. DOI 10.1177/0194599819890327. | Confirma población ≥3 años, compresión mantenida ≥5 min, taponamiento cuando no se identifica foco pese a compresión, material reabsorbible ante riesgo hemorrágico y tratamiento inicial antes de reversión si no hay hemorragia vital. | Aceptación limitada al abstract/KAS indexados; no lectura integral ni suspensión automática de antitrombóticos. |
| [EAU, Urological Infections](https://uroweb.org/guidelines/urological-infections/chapter/the-guideline) | §3.13.5; HTML obtenido. [Cita oficial](https://uroweb.org/guidelines/urological-infections/chapter/citation-information): edición Congreso Londres 2026, ISBN 978-94-92671-32-5. | La recomendación fuerte respalda iniciar desbridamientos repetidos de Fournier dentro de las primeras 24 h de presentación. | No establece repetirlos cada 24 h ni permite esperar hasta completar ese plazo. No se importan antibióticos ni dosis de la tabla adyacente. |
| [EMA Fasturtec](https://www.ema.europa.eu/en/medicines/human/EPAR/fasturtec) y [Product Information oficial](https://www.ema.europa.eu/en/documents/product-information/fasturtec-epar-product-information_en.pdf) | PDF público, 30 páginas; Anexo I §4.3, página impresa 3; §6.6, página impresa 9. Página EMA: actualización del archivo 12/08/2024. | §4.3 confirma la contraindicación en déficit G6PD. §6.6 documenta el manejo preanalítico específico descrito debajo. | Metadato de actualización del archivo no se presenta como fecha de revisión del SmPC. No acredita lectura de BSH TLS 2025 ni protocolo operativo local. |

## Laguna preanalítica de Fasturtec

El procedimiento queda localizado en §6.6, «Sample handling», página impresa 9. Los pasos se resumen en `sample_handling_summary` del JSON; cierran esa laguna documental del producto sin acreditar implantación local ni revisar BSH TLS 2025.

## Acceso y derechos

Se usaron páginas primarias públicas, resultados indexados identificados y el PDF público servido por EMA. No se cargaron textos prestados/restringidos ni se sortearon bloqueos. Se conservan solamente localizadores, metadatos y paráfrasis breves; acceso público no equivale a licencia de redistribución o procesamiento irrestricto. NICE y AAO-HNSF permanecen marcados como cotejo de fragmentos indexados. La revisión integral y cualquier reutilización extensa siguen fuera del alcance.

La matriz JSON diferencia fuente obtenida, acceso bloqueado, alcance aceptable y cambio no autorizado. No se ejecutaron pruebas, suites ni CI.


## Coordinación: acceso directo posterior

El navegador Chrome de la coordinación permitió leer directamente NICE NG38 §1.2.3 y el abstract primario PubMed31910111, población y KAS2/3a/3b/11. Se conserva como histórico el límite previo de acceso indexado. El JSON distingue ambas etapas. Son cinco anclajes focales directos; no cinco guías leídas íntegramente. No cambian runtime, dosis ni last_checked.
