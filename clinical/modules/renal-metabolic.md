# Renal, metabolic and toxicology modules

Shared gate: obtain glucose, ECG, electrolytes, acid-base status, renal function,
medications/toxins and volume/perfusion assessment. Repeat critical values and
verify whether results are affected by sampling error.

## electrolytes

- Treat symptomatic or ECG-threatening abnormalities before complete diagnostic workup; confirm unexpected results without delaying life-saving therapy.
- For sodium disorders, determine acuity and symptoms, calculate correction explicitly and prevent overcorrection with frequent monitoring and a rescue plan.
- For potassium, calcium and magnesium disorders, integrate ECG, renal function and causative drugs; verify IV concentrations, rates and monitoring requirements.
- Route the named ion to `sodium-emergencies`, `potassium-emergencies` or `calcium-magnesium-emergencies`; do not use a generic replacement plan.

## sodium-emergencies

- Confirm glucose, measured serum osmolality, volume status, urine osmolality, urine sodium, urine potassium, hourly urine volume, renal function, medications and relevant adrenal/thyroid context. Distinguish true hypotonic hyponatraemia from hyperglycaemic/translocational hyponatraemia and pseudohyponatraemia before applying a correction algorithm.
- Calculate serum osmolality and effective tonicity when inputs are available. With mmol/L units: `calculated osmolality = 2 x serum Na + glucose + urea`; `effective tonicity = 2 x serum Na + glucose`. With mg/dL units use `2 x serum Na + glucose/18 + BUN/2.8`. Calculate `osmolal gap = measured osmolality - calculated osmolality`. Urine osmolality and urine sodium are measured values, not derivable from serum sodium alone.
- Interpret urine osmolality with urine volume: >800 mOsm/kg usually indicates appropriate concentration; <300 mOsm/kg with polyuria suggests diabetes insipidus; 300--800 mOsm/kg is indeterminate and includes partial DI, osmotic diuresis and renal dysfunction. Interpret urine sodium in context of volume status, diuretics and kidney disease.
- When urine sodium, urine potassium and hourly urine volume are supplied, calculate electrolyte-free water clearance: `CeH2O = urine volume x [1 - (urine Na + urine K) / serum Na]`. Add stool/insensible losses separately. Use `scripts/sodium_water_balance.py` for deterministic arithmetic.
- **Severe or moderately severe neurologic symptoms attributable to hyponatraemia:** European guidance supports **150 mL sodium chloride 3% IV over 20 min**, then reassess symptoms and sodium. Repeat boluses according to the current protocol until clinical improvement or approximately a **5 mmol/L initial rise** is achieved. Treat the symptomatic emergency, not the sodium number in isolation.
- After the initial response, stop routine hypertonic boluses and prevent overcorrection. Avoid a rise greater than 10 mmol/L in the first 24 hours and greater than 8 mmol/L in each subsequent 24 hours; use a stricter ceiling (generally <=8 mmol/L/24 h) when osmotic-demeylination risk is high (e.g. very low sodium, alcoholism, malnutrition, advanced liver disease or hypokalaemia). Check sodium frequently during active correction and watch urine output for sudden water diuresis.
- If sodium is rising too fast, stop sodium-raising therapy and initiate an urgent specialist-directed relowering strategy with electrolyte-free water and/or desmopressin according to the actual trajectory and urine output. Do not use a fixed desmopressin schedule blindly.
- **Hypernatraemia:** restore shock first with appropriate isotonic crystalloid, then replace free-water deficit enterally or with IV electrolyte-free water while accounting for ongoing losses. Determine whether the disorder is acute versus chronic/unknown before selecting a correction rate. Chronic/unknown-duration hypernatraemia generally requires slower correction and serial sodium checks; there is no single correction rate appropriate to every adult.
- Explicitly document: symptoms, acuity, target sodium change, current sodium trajectory, urine output, ongoing losses, and stop/relowering thresholds.

## potassium-emergencies

- Obtain an immediate 12-lead ECG and continuous monitoring for severe potassium disturbance. Repeat an unexpected non-urgent value from a non-hemolyzed sample, but do not delay treatment for severe hyperkalemia, compatible ECG change, weakness or peri-arrest physiology.
- For hyperkalemic ECG toxicity outside cardiac arrest, give calcium gluconate 10% 30 mL IV over 10 minutes; in cardiac arrest/peri-arrest, give calcium chloride 10% 10 mL IV over 5 minutes. Reassess the ECG and repeat calcium according to response/protocol. Calcium stabilizes myocardium but does not lower potassium.
- Shift potassium with soluble insulin 10 units IV plus glucose 25 g over 5--15 minutes. State the available glucose concentration and volume: 50 mL of 50%, 125 mL of 20%, or 250 mL of 10% each provides 25 g. If pretreatment glucose is below 7 mmol/L, UKKA recommends glucose 10% at 50 mL/h for 5 hours after the initial regimen. Monitor glucose for at least 6 hours and potassium for rebound.
- Add nebulized salbutamol 10--20 mg for moderate/severe hyperkalemia, but never use it as monotherapy. Remove potassium with dialysis when indicated and consider a current potassium binder as an adjunct; bicarbonate is not routine unless a separate acid-base indication exists.
- For hypokalemia, identify symptoms, ECG change, magnesium deficiency, renal function and ongoing losses. Prefer oral replacement when safe. For IV potassium, use a ready-prepared solution when possible; a usual monitored rate is 10 mmol/h and a short emergency rate up to 20 mmol/h requires continuous ECG, a controlled pump and protocol-approved concentration/access. Never IV-push potassium and never write potassium only in mL without mmol and final concentration.

## calcium-magnesium-emergencies

- Interpret calcium using **ionized calcium when available** or corrected/albumin-context total calcium; obtain magnesium, phosphate, renal function, ECG/QTc and likely causative drugs. Treat tetany, seizure, laryngospasm, hypotension or dysrhythmia immediately rather than waiting for a complete etiologic work-up.
- **Severe symptomatic hypocalcaemia:** Society for Endocrinology emergency guidance supports **10--20 mL of 10% calcium gluconate IV**, diluted in **50--100 mL** of glucose 5% or sodium chloride 0.9%, given over about **10 min** with ECG monitoring; repeat if symptoms persist, then continue a pharmacy/protocol-verified calcium infusion while treating the cause.
- Calcium chloride contains substantially more elemental calcium than calcium gluconate and is more damaging with extravasation. RCUK equipment guidance notes **10 mL 10% calcium chloride ≈ 6.8 mmol Ca2+** versus **10 mL 10% calcium gluconate ≈ 2.26 mmol Ca2+**. Do not substitute equal volumes as though they were equivalent.
- **Torsades de pointes / severe symptomatic hypomagnesaemia:** use magnesium sulfate 2 g IV over 10--15 minutes (RCUK notes 2 g ≈ 8 mmol) when not in arrest, with ECG and blood-pressure monitoring. In cardiac arrest or recurrent torsades follow the current resuscitation algorithm rather than an arbitrary maintenance infusion.
- Reduce or avoid repeated magnesium in significant renal failure and monitor respiration, reflexes, blood pressure and magnesium concentration when repeated dosing/infusion is used.
- **Symptomatic hypermagnesaemia:** stop magnesium, support airway/ventilation/circulation, give calcium gluconate 10% **10--20 mL IV** for membrane stabilization, and obtain urgent renal/dialysis input when severe or clearance is impaired.
- **Severe hypercalcaemia:** restore intravascular volume with isotonic crystalloid while avoiding overload. Society for Endocrinology emergency guidance uses substantial saline rehydration in suitable patients and advises that loop diuretics are **not routine calcium-lowering therapy**; reserve them for fluid overload. Add bisphosphonate/calcitonin only after cause, renal function and current specialist/local protocol are verified.
- Before any continuous calcium or magnesium infusion, document the exact salt, concentration, diluent, final volume, access type and pump rate. Portugal/Azores presentation, compatibility/stability and local infusion concentration remain QA localization gates.

## toxicology

### Entrada y seguridad
- Estabilizar **ABCDE, glucemia, temperatura, convulsiones y ECG** antes de perseguir el tóxico. Registrar agente/formulación, dosis estimada, hora, vía, coingestas, liberación prolongada, función renal/hepática, embarazo y medicación habitual. En exposición desconocida buscar toxidrome, QRS/QTc, gasometría, anion gap/osmol gap, lactato y niveles dirigidos que cambien conducta.
- Contactar precozmente CIAV/centro toxicológico o toxicólogo en toxicidad grave, agente desconocido, formulación retardada, indicación de antídoto, posible depuración extracorpórea, recurrencia o intoxicación pediátrica. En parada tóxica aplicar ALS y tratar simultáneamente la causa; puede requerirse reanimación prolongada, ECTR o VA-ECMO.
- **Carbón activado no rutinario**: considerar dosis única tras ingesta potencialmente tóxica de sustancia adsorbible, sobre todo precozmente, solo con vía aérea segura. No usar por reflejo en cáusticos, hidrocarburos de alta aspiración, metales/alcoholes no adsorbibles o cuando el riesgo de aspiración supera el beneficio.
- Ninguna tabla sustituye la verificación del producto local, concentración, peso, función renal/hepática ni consulta toxicológica. Antivenenos, antitoxinas y quelantes son especialmente producto/protocolo dependientes.

### Drogas recreativas y toxidromes
- **Cocaína / crack:** no existe antídoto específico. Para agitación, hipertermia, hipertensión, taquicardia o convulsiones usar benzodiacepinas tituladas y enfriamiento activo. Tratar síndrome coronario según fisiología; si QRS ancho/arritmia por bloqueo de sodio, **bicarbonato sódico 1–2 mEq/kg IV**, repetir guiado por QRS, perfusión y gasometría. Evitar beta-bloqueo aislado no titulado en toxicidad aguda grave; seleccionar control cardiovascular con toxicología/cardiología.
- **Anfetamina, metanfetamina, MDMA, mefedrona y otras catinonas sintéticas:** sin antídoto específico. Benzodiacepinas, enfriamiento rápido en hipertermia, fluidos/electrolitos según estado, tratar hiponatremia, rabdomiólisis, convulsiones y fallo multiorgánico. No normalizar sodio rápidamente por protocolo genérico.
- **Opioides (heroína, fentanilo y análogos, metadona, oxicodona, etc.):** soporte ventilatorio primero. **Naloxona** titulada para recuperar ventilación eficaz; en dependencia conocida pueden emplearse incrementos IV pequeños (p. ej. 0.04–0.4 mg), repitiendo/escalando según respuesta; vías IN/IM son alternativas cuando no hay IV. Si recurre tras opioide de larga duración, considerar perfusión de naloxona basada en la dosis efectiva previa bajo protocolo local.
- **Benzodiacepinas / Z-drugs:** soporte. **Flumazenilo** solo en casos muy seleccionados (iatrogenia o exposición aislada en paciente no dependiente, sin proconvulsivantes/QRS ancho); referencia adulta: 0.2 mg IV lenta, repetir 0.2 mg aproximadamente cada minuto hasta respuesta, habitualmente máximo 1 mg inicial. Evitar en sobredosis mixta, dependencia, epilepsia o riesgo de abstinencia/convulsión.
- **GHB/GBL:** sin antídoto específico; vía aérea/ventilación y vigilancia. La recuperación puede ser brusca.
- **Cannabis y cannabinoides sintéticos:** sin antídoto; soporte, benzodiacepina si agitación/convulsión, evaluar isquemia, arritmia, lesión renal y coingestas en sintéticos.
- **PCP, ketamina, LSD y alucinógenos:** sin antídoto específico; ambiente controlado, benzodiacepinas para agitación/convulsiones, enfriamiento si hipertermia y tratamiento de trauma/rabdomiólisis.
- **Serotoninérgicos (ISRS/IRSN/IMAO, MDMA, tramadol, linezolid y combinaciones):** retirar agentes, benzodiacepinas, enfriamiento y soporte. En síndrome serotoninérgico moderado-grave considerar **ciproheptadina 12 mg VO/NG**, luego 2 mg cada 2 h hasta respuesta; mantenimiento habitual 8 mg cada 6 h. No existe formulación IV.
- **Anticolinérgicos (antihistamínicos, tricíclicos, atropínicos, plantas):** soporte, benzodiacepinas. **Fisostigmina** puede considerarse para delirium antimuscarínico puro tras ECG y consulta toxicológica; adulto 0.5–1 mg IV muy lento, repetir según respuesta hasta 2 mg. Evitar con QRS ancho, sospecha de tricíclicos/bloqueo de sodio, bradicardia o trastorno de conducción.
- **Alcohol etílico:** soporte, glucosa si hipoglucemia; tiamina en riesgo de déficit antes o junto a carbohidratos cuando sea factible. No existe antídoto para la intoxicación etílica aguda.

### Analgésicos y fármacos frecuentes
- **Paracetamol/acetaminofén:** usar nomograma solo para ingesta aguda única con tiempo fiable y concentración obtenida a partir de 4 h. Iniciar **N-acetilcisteína (NAC)** si nivel en/sobre línea de tratamiento, en lesión hepática compatible o si retrasar el nivel haría iniciar >8 h tras una ingesta claramente tóxica. Usar un régimen IV/VO validado que aporte **al menos 300 mg/kg en las primeras 20–24 h**; si se usa el régimen IV clásico: 150 mg/kg en ≥1 h, 50 mg/kg en 4 h, 100 mg/kg en 16 h. No suspender por reloj: exigir criterios de parada (paracetamol bajo/indetectable, AST/ALT e INR en evolución favorable y paciente clínicamente estable).
- **Salicilatos:** no existe antídoto molecular. Alcalinizar suero/orina con bicarbonato y potasio según gasometría/electrolitos; evitar intubación si puede mantenerse ventilación espontánea. Hemodiálisis en toxicidad grave, especialmente alteración mental, hipoxemia, fracaso del tratamiento, acidosis grave o niveles altos según EXTRIP.
- **Tricíclicos y otros bloqueadores de canal de sodio (incluye difenhidramina grave, flecainida, propafenona y cocaína):** **bicarbonato sódico 1–2 mEq/kg IV** ante QRS ancho, hipotensión o arritmia ventricular, repetir guiado por respuesta y pH; evitar sobrealcalinización/hipernatremia. Lidocaína puede ser rescate especializado en arritmia ventricular persistente.
- **Bupropión:** sin antídoto; benzodiacepinas para convulsiones, soporte hemodinámico, considerar bicarbonato solo si existe bloqueo de sodio documentado (puede responder poco), ILE/ECMO en colapso refractario con toxicología.
- **Litio:** sin antídoto. Suspender, corregir volumen/electrolitos cuidadosamente y usar hemodiálisis según EXTRIP (síntomas neurológicos graves/arritmia, deterioro renal con nivel elevado o cinética de eliminación desfavorable).
- **Valproato:** soporte; considerar **L-carnitina 100 mg/kg IV (máx. 6 g) de carga, luego 15 mg/kg IV cada 4 h** en hiperamonemia, hepatotoxicidad, encefalopatía o intoxicación grave; considerar ECTR en toxicidad extrema según toxicología/EXTRIP.
- **Isoniazida:** convulsiones/acidosis refractarias requieren **piridoxina (vitamina B6) gramo por gramo de isoniazida ingerida**; si cantidad desconocida, referencia adulta **5 g IV**, administrada rápidamente junto con benzodiacepinas y soporte.
- **Sulfonilureas:** dextrosa para hipoglucemia + **octreótido 50–100 microgramos SC/IV cada 6–12 h** en adulto para prevenir recurrencia; monitorización prolongada. En pediatría usar protocolo por peso/centro toxicológico.
- **Insulina:** no antídoto específico; dextrosa titulada (bolos + perfusión) y potasio/magnesio/fosfato seriados; evitar sobrecorrección de potasio.
- **Metformina:** no antídoto; soporte y hemodiálisis precoz en acidosis láctica grave (EXTRIP: umbral fuerte con lactato >20 mmol/L, pH ≤7.0 o fracaso de soporte; umbral menor si shock/IRA/fallo hepático).
- **Metotrexato a dosis altas con eliminación retardada/IRA:** **glucarpidasa 50 unidades/kg IV una vez** cuando cumpla criterios específicos; leucovorina debe continuar pero separada temporalmente según ficha/protocolo. No usar glucarpidasa de forma empírica para toda sobredosis oral.
- **Colchicina:** no antídoto universalmente disponible; descontaminación precoz seleccionada, soporte intensivo y toxicología. Anticuerpos Fab específicos no son tratamiento rutinariamente disponible.
- **Digoxina y glucósidos cardiacos:** **fragmentos Fab antidigoxina** para arritmia amenazante, hiperpotasemia significativa o toxicidad grave. Dosificar por cantidad ingerida o concentración estable cuando sea posible; si no puede calcularse y existe inestabilidad vital, usar el esquema empírico del producto/centro toxicológico. No interpretar digoxinemia tras Fab con inmunoensayos convencionales como concentración libre.

### Cardiovasculares
- **Beta-bloqueadores:** soporte + vasopresores según fenotipo. **Insulina euglucémica a dosis altas**: referencia inicial 1 U/kg IV y luego 1 U/kg/h, con dextrosa para euglucemia y monitorización intensiva de glucosa/potasio; titular bajo protocolo toxicológico. **Glucagón 5–10 mg IV** puede probarse, seguido si responde de perfusión 1–5 mg/h; náuseas/vómitos frecuentes.
- **Calcioantagonistas:** calcio IV + **insulina euglucémica a dosis altas** precoz (1 U/kg IV, luego 1 U/kg/h y titulación), dextrosa, vasopresores; considerar ILE/ECMO en shock refractario. Calcio: usar concentración/producto local y monitorizar calcio ionizado; no intercambiar cloruro y gluconato mg por mg.
- **Clonidina/agonistas alfa-2:** soporte; naloxona puede ensayarse en casos seleccionados, especialmente pediatría, pero respuesta inconsistente.
- **Nitratos/nitritos:** si metahemoglobinemia significativa, tratar como metahemoglobinemia.
- **Antiarrítmicos clase I:** tratar bloqueo de sodio con bicarbonato; considerar lidocaína/ILE/ECMO según agente y toxicología.

### Tóxicos celulares, gases y metahemoglobina
- **Cianuro:** tratar inmediatamente si sospecha clínica grave. **Hidroxocobalamina 5 g IV** en adulto, habitualmente durante ~15 min; puede repetirse una segunda dosis de 5 g según gravedad/respuesta. Alternativa/adyuvante según disponibilidad: nitrito sódico + tiosulfato sódico bajo protocolo específico. No esperar confirmación analítica.
- **Monóxido de carbono:** **100% O2**; no existe antídoto farmacológico específico. Consultar medicina hiperbárica para pérdida de conciencia, síntomas neurológicos/cardiacos, acidosis grave, embarazo con exposición significativa u otros criterios locales.
- **Metahemoglobinemia:** **azul de metileno 1–2 mg/kg IV** de solución 1% durante ~5 min; puede repetirse una dosis menor si persiste tras 30–60 min. Evitar dosis acumuladas altas; precaución/alternativas en deficiencia G6PD y con fármacos serotoninérgicos.
- **Sulfuro de hidrógeno:** rescate seguro, O2/ventilación y soporte; no existe antídoto universal de eficacia establecida. Nitritos se han usado, pero no deben retrasar soporte y requieren toxicología.
- **Humos de incendio:** evaluar simultáneamente CO y cianuro; no asumir que una COHb baja excluye cianuro.

### Alcoholes tóxicos y solventes
- **Metanol / etilenglicol:** **fomepizol 15 mg/kg IV de carga, luego 10 mg/kg cada 12 h por 4 dosis y después 15 mg/kg cada 12 h** hasta criterios de suspensión; aumentar frecuencia durante hemodiálisis según ficha/protocolo. Añadir folato/ácido folínico en metanol y tiamina/piridoxina en etilenglicol según protocolo. Hemodiálisis según EXTRIP por acidosis/daño de órgano/nivel/cinética.
- **Isopropanol:** no usar fomepizol de rutina; soporte. Hemodiálisis solo en casos excepcionales graves.
- **Dietilenglicol/propilenglicol:** soporte, toxicología; bloqueo de alcohol-deshidrogenasa y ECTR pueden ser considerados según agente y gravedad, sin extrapolar automáticamente el protocolo de metanol.

### Pesticidas, plantas y toxinas
- **Organofosforados/carbamatos:** descontaminación del personal/paciente, vía aérea y **atropina IV titulada rápidamente hasta secar secreciones bronquiales y mejorar ventilación/perfusión**; en adulto puede iniciarse 1–2 mg IV y duplicar cada 3–5 min si persiste síndrome muscarínico grave. **Pralidoxima** en organofosforados: referencia adulta 1–2 g IV en 15–30 min, seguida de perfusión/dosis repetidas según protocolo. Las necesidades de atropina pueden ser muy altas.
- **Rodenticidas anticoagulantes (warfarina/superwarfarinas):** vitamina K1 según INR y sangrado; las superwarfarinas pueden requerir cursos prolongados de vitamina K guiados por INR y toxicología. Hemorragia vital: seguir ruta VKA con 4F-PCC + vitamina K IV.
- **Paraquat/diquat:** no antídoto específico. Evitar hiperoxia innecesaria salvo hipoxemia; descontaminación precoz seleccionada, soporte y toxicología.
- **Estricnina:** sin antídoto; control agresivo de estímulos, benzodiacepinas y ventilación/parálisis si precisa.
- **Amanita phalloides:** soporte, NAC y silibinina IV cuando esté disponible según toxicología/hepatología; derivación precoz a centro de trasplante si insuficiencia hepática. No existe un único régimen universal.
- **Toxinas marinas (tetrodotoxina, saxitoxina, ciguatera):** predominantemente soporte; no existe antídoto específico validado para tetrodotoxina/saxitoxina. Ciguatera: tratamiento sintomático; manitol no es antídoto demostrado.
- **Mordeduras de serpiente / arañas / escorpiones:** usar **antiveneno específico del producto y especie/síndrome**, nunca una dosis genérica. Manejar coagulopatía, neurotoxicidad y shock según protocolo regional.
- **Botulismo:** antitoxina botulínica heptavalente para casos no infantiles tan pronto como sea posible tras consulta de salud pública/toxicología; la dosis es la presentación completa del producto vigente, no convertir a mg/kg. Lactantes: inmunoglobulina botulínica específica donde esté disponible.

### Metales, cáusticos y otros
- **Hierro:** **deferoxamina 15 mg/kg/h IV** en toxicidad sistémica grave, shock, acidosis o niveles indicativos; titular/duración con toxicología y vigilar hipotensión/ARDS. Evitar cursos prolongados innecesarios.
- **Plomo:** quelación según nivel/síntomas. En encefalopatía grave se emplean esquemas con dimercaprol + CaNa2EDTA; en cuadros no encefalopáticos puede usarse succímero. Dosis dependen de gravedad/edad/producto: confirmar con toxicología antes de prescribir.
- **Arsénico/mercurio:** dimercaprol o succímero según especie química, gravedad y función renal; no existe una pauta única segura para todas las formas.
- **Talio:** **azul de Prusia** es el antídoto/quelante de elección; toxicología temprana y considerar ECTR en casos graves según EXTRIP.
- **Ácido fluorhídrico/fluoruros:** irrigación inmediata; **gel de gluconato cálcico 2.5%** para exposición cutánea y calcio IV/local según toxicidad, ECG y electrolitos. Las técnicas de infiltración/intraarterial requieren protocolo experto.
- **Cáusticos:** no neutralizar, no inducir vómito y no dar carbón por rutina. Evaluar vía aérea y endoscopia/imagen según lesión; manejo quirúrgico/GI temprano.
- **Hidrocarburos:** soporte respiratorio; evitar emesis/carbón rutinario por aspiración. Tratar arritmias y neumonitis según fisiología.

### Antídotos/rescates de alta prioridad — referencia rápida
| Tóxico/síndrome | Antídoto/rescate | Dosis adulta de referencia / nota |
|---|---|---|
| Opioides | Naloxona | Titular IV desde 0.04–0.4 mg en dependencia; escalar/repetir hasta ventilación eficaz; IN/IM si no IV |
| Benzodiacepina aislada seleccionada | Flumazenilo | 0.2 mg IV lenta; repetir 0.2 mg cada ~1 min; habitual máx. inicial 1 mg |
| Paracetamol | NAC | Régimen validado ≥300 mg/kg en 20–24 h; clásico IV 150 + 50 + 100 mg/kg |
| Metanol/etilenglicol | Fomepizol | 15 mg/kg carga; 10 mg/kg q12 h x4; después 15 mg/kg q12 h; ajustar en HD |
| Cianuro | Hidroxocobalamina | 5 g IV; puede repetirse 5 g |
| Metahemoglobinemia | Azul de metileno | 1–2 mg/kg IV ~5 min; reevaluar 30–60 min |
| Digoxina | Fab antidigoxina | Calcular por carga/nivel; esquema empírico solo si amenaza vital y según producto/toxicología |
| Organofosforado | Atropina | 1–2 mg IV inicial adulto, duplicar q3–5 min hasta objetivos clínicos |
| Organofosforado | Pralidoxima | 1–2 g IV en 15–30 min; después infusión/repetición según protocolo |
| Sulfonilurea | Octreótido | 50–100 mcg SC/IV q6–12 h + dextrosa |
| Isoniazida | Piridoxina | Gramo por gramo ingerido; si desconocido, 5 g IV adulto |
| Hierro | Deferoxamina | 15 mg/kg/h IV en toxicidad sistémica grave |
| Síndrome serotoninérgico | Ciproheptadina | 12 mg VO/NG; 2 mg q2 h hasta respuesta; luego 8 mg q6 h |
| Anticolinérgico puro seleccionado | Fisostigmina | 0.5–1 mg IV muy lenta; repetir hasta 2 mg con ECG/contraindicaciones |
| LAST | Emulsión lipídica 20% | <70 kg: 1.5 mL/kg bolo + 0.25 mL/kg/min; máximo total 12 mL/kg |
| Beta-bloqueador/CCB | Insulina dosis alta | 1 U/kg IV + 1 U/kg/h, dextrosa y monitorización; titular por protocolo |
| Beta-bloqueador | Glucagón | 5–10 mg IV; si responde, 1–5 mg/h |
| Bloqueo de canal de sodio | Bicarbonato sódico | 1–2 mEq/kg IV, repetir guiado por QRS/pH |
| Metotrexato alta dosis + IRA | Glucarpidasa | 50 U/kg IV una vez cuando cumpla criterios |
| Talio | Azul de Prusia | Dosis según producto/toxicología; no extrapolar entre formulaciones |
| HF/fluoruro | Gluconato cálcico | Gel 2.5% cutáneo; terapia IV/local según ECG, Ca/Mg/K y experto |

### Sustancias sin antídoto específico que deben estar explícitamente reconocidas
- Cocaína, anfetaminas/metanfetamina/MDMA/catinonas, GHB, cannabis/sintéticos, PCP/LSD/ketamina.
- Salicilatos (bicarbonato/diálisis son tratamientos fisiológicos, no antídoto molecular), litio, metformina, colchicina, bupropión.
- Monóxido de carbono (O2/HBO), sulfuro de hidrógeno, isopropanol, paraquat/diquat, estricnina, tetrodotoxina/saxitoxina.
- La ausencia de antídoto **no** significa ausencia de tratamiento: definir soporte, descontaminación selectiva, ECTR/ECMO y criterios de escalada.

### Reversión de anticoagulantes e hipocoagulantes
- Ruta detallada en `anticoagulation-reversal`. Toxicología debe reconocer: VKA/warfarina y superwarfarinas; heparina no fraccionada; HBPM; fondaparinux; dabigatrán; apixabán/rivaroxabán/edoxabán; argatrobán/bivalirudina; y anticoagulantes de uso infrecuente. Diferenciar antídoto específico, reversión parcial e inespecífica.
- Portugal/Azores: antes de uso clínico confirmar stock/formulario de CIAV/INFARMED, presentación exacta, concentraciones, criterios locales de liberación, disponibilidad de 4F-PCC/idarucizumab/andexanet/Fab/hidroxocobalamina/fomepizol/azul de metileno/ILE y capacidad de hemodiálisis/ECMO.

## urologic-emergencies

- Threats: infected obstruction, torsion, retention with complications, Fournier gangrene, priapism and major hematuria with clot retention.
- Obtain urinalysis/culture, renal function, pregnancy test and targeted ultrasound/CT. Analgesia must not delay torsion or source-control pathways.
- Infected obstruction requires antibiotics, resuscitation and urgent drainage consultation; discharge only uncomplicated stable disease with follow-up and return precautions.

## endocrine-metabolic

- Consider DKA/HHS, adrenal crisis, thyroid storm, myxedema coma, severe hypoglycemia and pituitary emergencies.
- Treat airway/shock/glucose first; obtain ketones, electrolytes, osmolality and acid-base data as relevant.
- For insulin and electrolyte replacement, verify weight, potassium, renal function, concentration and monitoring frequency; show calculations and avoid insulin when unsafe due to potassium.

## adrenal-crisis

- Suspect adrenal crisis with unexplained shock, vomiting, weakness, hypoglycemia or hyponatremia, especially after steroid interruption or with known adrenal/pituitary disease. Hyperkalemia may be absent in secondary adrenal insufficiency. Draw cortisol/ACTH if immediately feasible; do not delay treatment for sampling or results.
- Adult treatment: hydrocortisone 100 mg IV immediately (IM if IV access is delayed), then 200 mg over 24 hours or 50 mg IV/IM every 6 hours. If pharmacy confirms the product/diluent and stability, 200 mg to a final 100 mL = 2 mg/mL, delivering 8.33 mg/h at 4.17 mL/h; 200 mg/200 mL = 1 mg/mL at 8.33 mL/h. Confirm bag replacement interval; never assume 24-hour stability from this arithmetic.
- Restore circulation with isotonic saline; an adult without fluid-overload risk commonly receives 1 L in the first hour, then reassessment. Use smaller reassessed aliquots in cardiac/renal disease. Treat hypoglycemia promptly, monitor sodium correction, glucose, potassium, urine output and perfusion, and treat the precipitant.
- The intermittent hydrocortisone regimen is an alternative when a pump is unavailable. If hydrocortisone itself is unavailable, urgently obtain an endocrinology/pharmacy-verified parenteral glucocorticoid alternative; do not substitute milligram-for-milligram or assume equal mineralocorticoid effect. Admit, taper after recovery with endocrinology and provide sick-day education.

## thyroid-storm

- Suspect clinical thyrotoxic decompensation with fever, marked tachycardia/arrhythmia, CNS disturbance, heart failure or GI/hepatic dysfunction. Scores support diagnosis but should not delay ICU/endocrine treatment. Obtain thyroid tests, glucose, electrolytes, liver tests, ECG, cultures and cardiac assessment while treating the precipitant.
- Control hormone synthesis when due to hyperfunction: ATA adult reference regimens are propylthiouracil 500--1,000 mg enteral loading then 250 mg every 4 hours, OR methimazole/thiamazole 60--80 mg/day in divided enteral doses. Select around hepatic injury, pregnancy, contraindications and actual availability; do not combine automatically. Thyroiditis/exogenous hormone requires a different strategy.
- Under the ATA sequence, give iodine at least 1 hour after the thionamide. Verify iodine concentration and formulation before converting to drops; products are not interchangeable. Other guideline sequences require explicit specialist reconciliation.
- Give stress-dose glucocorticoid using one verified storm protocol. The 2026 ETA/BTA/Society for Endocrinology/Welsh Endocrine and Diabetes Society consensus proposes hydrocortisone 100 mg IV once, then 50 mg IV every 6 hours (or 200 mg over 24 hours by syringe driver in HDU/ICU). ATA 2016 lists a different regimen (300 mg IV loading, then 100 mg every 8 hours); do not combine or silently interchange regimens—follow the current specialist/local protocol. Monitor potassium after glucocorticoids, especially when thyrotoxic periodic paralysis is plausible. Do not confuse storm treatment with adrenal-crisis dosing. Provide external cooling and suitable antipyresis; avoid aspirin/salicylates. Manage fluids and oxygen according to cardiac status.
- Assess shock and ventricular function BEFORE beta-blockade. Decompensated low-output failure can collapse after propranolol or even esmolol. In a well-perfused patient, select/titrate a verified beta-blocker regimen with continuous monitoring. If esmolol is appropriate, use the existing preparation/calculation in `acute-aortic-syndrome`, but do not copy its aortic BP/HR targets. Avoid automatic loading in tenuous circulation; stop for worsening perfusion, bradycardia, block or bronchospasm. Diltiazem is not automatically safe in systolic failure either.
- If significant hepatic dysfunction is present (e.g. transaminases around >3 times the upper limit of normal or rising bilirubin), the 2026 consensus favours considering methimazole/carbimazole over PTU because of PTU hepatotoxicity risk, except where patient-specific factors such as first-trimester pregnancy alter selection. Observational data have not shown a clear mortality advantage for PTU. Once clinically improving, reduce thionamide dosing as directed by endocrinology. If not clinically stabilising within 24–48 hours, reassess precipitant, absorption, cardiac dysfunction and need for rescue. Cholestyramine, lithium, plasma exchange or thyroidectomy are specialist adjunct/rescue options, not automatic steps. If thionamides are unavailable/contraindicated or treatment fails, obtain urgent specialist rescue planning; do not replace them with an unrelated antihypertensive. Verify Portuguese products via the localization workflow.

## myxedema-coma

- Recognize severe decompensated hypothyroidism with altered consciousness, hypothermia, hypoventilation, bradycardia, hypotension and/or hyponatremia; coma is not required. TSH may not be elevated with central disease. Obtain TSH/free T4, cortisol, gas, glucose/electrolytes and precipitant assessment without delaying treatment.
- Give empiric stress-dose hydrocortisone BEFORE thyroid hormone while adrenal insufficiency is being excluded; the adrenal-crisis module supplies 100 mg IV followed by 200 mg/24 h or 50 mg every 6 hours. Reconcile ongoing doses with the endocrine team.
- Adult ATA reference: levothyroxine 200--400 micrograms IV ONCE as a loading dose, reduced for older/smaller patients, coronary disease or arrhythmia. Subsequent daily IV replacement is approximately 75% of an oral 1.6 micrograms/kg/day reference, individualized with specialist monitoring. Never repeat the loading dose as daily maintenance or confuse micrograms with milligrams.
- If IV levothyroxine is unavailable, arrange urgent endocrine/pharmacy-directed enteral treatment; absorption with ileus is unreliable and oral and IV doses are not equivalent. Liothyronine is a selected specialist adjunct, not a routine substitute; cardiac risk and local availability matter.
- Admit to ICU, support ventilation early if needed, use cautious fluids and passive warming, correct hypoglycemia and sodium safely, and treat infection/other triggers. Avoid aggressive peripheral warming and unnecessary sedatives. Follow consciousness, ventilation, temperature, ECG/perfusion and free hormone trends.
- The 2026 ETA/BTA/Society for Endocrinology/Welsh Endocrine and Diabetes Society joint consensus supports IV levothyroxine loading at 200–400 micrograms, reducing the dose in older/smaller patients and those with ischaemic heart disease or significant arrhythmia, plus empiric IV hydrocortisone 100 mg then 50 mg every 6 hours (or 200 mg/24 hours by syringe driver). This agrees with the module's cautious loading and hydrocortisone schedule. The exact enteral fallback regimen when IV levothyroxine is unavailable still requires source-level and pharmacy/local-protocol confirmation; do not invent an oral/NG loading dose or claim it is dose-equivalent.

## diabetic-ketoacidosis-hhs

- Diagnose adult DKA only when all three domains are present: diabetes/history or glucose at least 200 mg/dL (11.1 mmol/L), ketosis with beta-hydroxybutyrate at least 3.0 mmol/L or urine ketones at least 2+, and metabolic acidosis with pH below 7.3 or bicarbonate below 18 mmol/L. Actively consider euglycemic DKA with SGLT2 inhibitors, pregnancy, fasting or partial insulin treatment; do not exclude DKA from glucose alone.
- Diagnose HHS only when all four domains are present: glucose at least 600 mg/dL (33.3 mmol/L), effective osmolality above 300 mOsm/kg or total calculated osmolality above 320 mOsm/kg, beta-hydroxybutyrate below 3.0 mmol/L or urine ketones below 2+, and pH at least 7.3 with bicarbonate at least 15 mmol/L. Classify significant ketonaemia/acidosis with hyperosmolality as mixed DKA/HHS.
- Obtain glucose, beta-hydroxybutyrate, venous blood gas, sodium, potassium, chloride, bicarbonate, urea/creatinine, magnesium, phosphate, measured osmolality when available, ECG, fluid balance and precipitant evaluation. Calculate anion gap, albumin-corrected gap when albumin is known, effective/total osmolality and corrected sodium. Prefer beta-hydroxybutyrate to urine ketones and use `scripts/acid_base_hyperglycemia.py` for deterministic arithmetic.
- Restore perfusion first. In adults without cardiac or renal compromise, give isotonic saline or a balanced crystalloid at 500--1000 mL/h for the first 2--4 hours, then individualize by hemodynamics, sodium, osmolality and fluid balance. In older adults, pregnancy, heart failure or kidney failure, use smaller aliquots such as 250 mL with frequent reassessment; do not apply a fixed large-volume protocol.
- Check potassium before insulin. If potassium is below 3.5 mmol/L, replace potassium at 10 mmol/h and delay insulin until potassium is above 3.5 mmol/L. One conditional reference preparation is potassium chloride 20 mmol in a compatible final volume of 100 mL = 0.2 mmol/mL, delivered at 50 mL/h = 10 mmol/h; use only when the local protocol permits that concentration for the verified access, with a controlled pump and ECG/electrolyte monitoring. Once potassium falls below 5.0 mmol/L, usually add 20--30 mmol potassium per litre of IV fluid to target 4--5 mmol/L; withhold initial potassium when elevated and monitor closely. Never IV-push potassium.
- For DKA or mixed DKA/HHS, use soluble/regular insulin IV at 0.1 units/kg/h after the potassium safety gate. A practical pump preparation is 100 units in a final volume of 100 mL compatible 0.9% saline = 1 unit/mL: the numeric units/h equals mL/h. Prime tubing according to local protocol. Do not routinely give an insulin bolus when the infusion can start promptly.
- When glucose falls below 250 mg/dL (13.9 mmol/L) in DKA, add 5--10% dextrose and reduce insulin to 0.05 units/kg/h, targeting glucose near 200 mg/dL while continuing insulin until ketoacidosis resolves. In euglycemic DKA, begin dextrose with the insulin pathway rather than withholding insulin because glucose is near normal.
- In HHS without significant ketosis/acidosis, prioritize controlled fluid/osmolality correction and use insulin IV at 0.05 units/kg/h; a fluid-only glucose fall may occur before insulin. Do not exceed a glucose decline of 90--120 mg/dL/h, a sodium fall of 10 mmol/L/24 h or an osmolality fall of 3--8 mOsm/kg/h. An initial sodium rise as glucose falls is expected and alone is not an indication for hypotonic saline.
- Check capillary glucose every 1--2 hours. Repeat electrolytes, creatinine, phosphate, beta-hydroxybutyrate and venous pH every 4 hours; in HHS also repeat osmolality every 4 hours. Recheck potassium 2 hours after insulin starts and at least every 4 hours, more often when unstable or actively replacing.
- Assess bleeding, renal function, weight and venous/arterial thrombosis. Unless thrombosis is suspected or anticoagulation is contraindicated, use prophylactic-dose low-molecular-weight heparin according to the locally available product and renal/weight protocol; do not escalate automatically to therapeutic anticoagulation merely because HHS is prothrombotic.
- Do not give bicarbonate routinely. Consider it only for severe DKA acidosis below pH 7.0 under a current protocol; if used, the 2024 consensus regimen is sodium bicarbonate 100 mmol in 400 mL sterile water every 2 hours until pH exceeds 7.0, with potassium and sodium monitoring. Do not replace phosphate routinely unless phosphate below 1.0 mmol/L is accompanied by respiratory/cardiac muscle weakness or another specific indication.
- Define DKA resolution by beta-hydroxybutyrate below 0.6 mmol/L plus venous pH at least 7.3 or bicarbonate at least 18 mmol/L; ideally glucose is below 200 mg/dL. Do not use anion gap or urine ketones alone because recovery hyperchloremic acidosis and ketone conversion can mislead. Consider HHS resolved when osmolality is below 300 mOsm/kg, cognition and hyperglycemia improve, urine output exceeds 0.5 mL/kg/h and glucose is below 250 mg/dL.
- Continue or initiate an appropriate basal insulin plan and overlap subcutaneous insulin by 1--2 hours before stopping IV insulin. Treat the precipitant, stop SGLT2 inhibitors during the event, and admit severe DKA, HHS, mixed crises, altered consciousness, shock or major comorbidity to a high-acuity setting.

## acid-base-emergencies

- Confirm sample type (arterial, venous or capillary), oxygen delivery/FiO2, collection time and clinical context. Venous pH/bicarbonate are often sufficient for DKA trending, but venous PO2 must not be used to assess arterial oxygenation; use pulse oximetry and an arterial sample when oxygenation or an arterial-venous discrepancy matters.
- Read pH, PCO2 and bicarbonate together. Then obtain sodium, chloride, albumin, lactate, beta-hydroxybutyrate, glucose, urea/creatinine and relevant toxins. A normal pH does not exclude a mixed disorder.
- Calculate anion gap as `Na - (Cl + HCO3)` and, when albumin is known in g/dL, corrected gap as `AG + 2.5 x (4 - albumin)`. For high-gap metabolic acidosis calculate the delta ratio `(corrected AG - 12) / (24 - HCO3)` while treating cutoffs as approximate and context-dependent.
- For metabolic acidosis, calculate Winter compensation: expected PCO2 `1.5 x HCO3 + 8 +/- 2 mmHg`. A measured PCO2 above this range indicates an added respiratory acidosis; below it indicates an added respiratory alkalosis. For metabolic alkalosis use expected PCO2 approximately `40 + 0.7 x (HCO3 - 24) +/- 5`.
- For respiratory disorders, compare acute and chronic expected bicarbonate responses instead of declaring chronicity from one gas: respiratory acidosis raises bicarbonate by about 1 mmol/L per 10 mmHg acute and 3.5--4 chronic; respiratory alkalosis lowers it by about 2 acute and 4--5 chronic.
- Use `scripts/acid_base_hyperglycemia.py` for reproducible calculations. Treat the patient and cause: restore perfusion/oxygenation, address sepsis, DKA, renal failure, diarrhea, vomiting, salicylate/toxic alcohol exposure or ventilatory failure. Do not administer bicarbonate solely because bicarbonate is low.
- In severe metabolic acidosis, avoid unnecessary intubation. If intubation is unavoidable, minimize apnea and match or initially approximate the pre-intubation minute ventilation; an abrupt PCO2 rise can cause profound acidemia and cardiovascular collapse. Obtain an early post-intubation gas and reassess ventilation.

## aki-nephrology

- Determine baseline, perfusion, obstruction, nephrotoxins, urinalysis findings and complications. Use bladder/renal ultrasound when obstruction is plausible.
- Treat shock and cause while avoiding both under-resuscitation and congestion; adjust renally cleared drugs.
- Escalate refractory hyperkalemia, severe acidosis, pulmonary edema, uremic complication or toxin indication for nephrology/dialysis; do not use creatinine alone to decide.

## rhabdomyolysis

- Identify trauma/compression, exertion/heat, seizure, drugs/toxins and ischemia; check CK trend, potassium, calcium, phosphate, renal function and ECG.
- Give goal-directed isotonic crystalloid while tracking urine output, perfusion and congestion; a commonly used adult urine-output target is about 1--3 mL/kg/h (up to roughly 300 mL/h), but stop escalating fluid if oliguria persists with overload risk. Treat hyperkalemia urgently and trend CK until a clear peak/downtrend.
- Do not use bicarbonate, mannitol or loop diuretics routinely to prevent rhabdomyolysis-associated AKI; reserve them for another specific indication or specialist protocol. Do not chase CK with unlimited fluid.
- Evaluate compartment syndrome and dialysis indications; admit significant electrolyte disturbance, AKI, systemic illness or ongoing muscle injury.

## acute-liver-failure

- Recognize acute liver injury with coagulopathy and encephalopathy; assess glucose frequently and seek toxins, viral, ischemic, autoimmune and pregnancy causes.
- Start N-acetylcysteine immediately for suspected acetaminophen toxicity without waiting for a level; discuss early IV N-acetylcysteine for selected non-acetaminophen acute liver failure with a liver/transplant specialist. Obtain an accurate timeline, acetaminophen concentration, toxicology and serial hepatic, renal, glucose, lactate, ammonia and coagulation data.
- Manage cerebral/airway risk and avoid unnecessary correction of INR without bleeding or an invasive-procedure need because INR does not measure the full hemostatic balance and correction can obscure prognosis.
- Contact a transplant-capable liver center at first recognition rather than after deterioration; worsening encephalopathy, lactate, acidosis, hypoglycemia or multiorgan failure requires critical care and urgent transplant assessment.

## alcohol-withdrawal

- Determine last intake, prior seizures/delirium, co-ingestion, trauma, infection, liver disease, glucose and electrolytes.
- Benzodiazepines are first-line. Use symptom-triggered dosing only when a reliable validated assessment can be performed; use fixed or front-loaded treatment for severe/high-risk withdrawal, inability to score reliably or according to monitored protocol. Match agent to liver function and age, verify dose, monitor ventilation and define refractory escalation.
- Phenobarbital may be an alternative or adjunct only in experienced hands with close cardiorespiratory monitoring and a clear cumulative-dose/rescue-airway plan; avoid unstructured stacking with other sedatives.
- Give thiamine and correct metabolic abnormalities without delaying glucose for hypoglycemia. Severe withdrawal, delirium or repeated medication needs requires monitored admission.
