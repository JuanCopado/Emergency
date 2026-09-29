# Syndrome router

Use the smallest relevant module set.
Resolve every selected ID through `module-index.md`. Combine modules only when
each changes immediate decisions; do not load an entire category.

## Clinical images
- uploaded clinical photograph, radiograph, ultrasound frame/clip, CT/MRI screenshot or ECG image -> clinical-image-interpretation
- musculoskeletal radiograph -> clinical-image-interpretation + musculoskeletal-xray
- chest radiograph -> clinical-image-interpretation + chest-xray
- ultrasound / POCUS image or clip -> clinical-image-interpretation + pocus-image
- ECG photograph / tracing -> clinical-image-interpretation + ecg-image
- blood-gas analyzer printout, photograph or report screenshot -> clinical-image-interpretation + blood-gas-image + acid-base-emergencies; add diabetic-ketoacidosis-hhs when supported
- skin, wound or mucosal photograph -> clinical-image-interpretation + skin-wound-image
- CT or MRI screenshot -> clinical-image-interpretation + ct-mri-screenshot
- eye image -> clinical-image-interpretation + ophthalmology-image
- clinical image outside supported modalities -> clinical-image-interpretation + other-clinical-image
- Add the relevant syndrome module if symptoms or findings imply a clinical emergency; do not substitute image review for stabilization.

## Cardiovascular
- chest pain / ACS -> acute-coronary-syndrome + non-coronary-chest-pain
- undifferentiated shock (adult) -> undifferentiated-shock + ecg-pocus-integration; add only cause-supported modules (sepsis-shock, cardiogenic-shock, trauma-major-hemorrhage, anaphylaxis, pulmonary-embolism, tension-pneumothorax, cardiac-tamponade-pericardial-emergency, adrenal-crisis, obstetric-emergencies)
- septic shock / suspected infection with hypoperfusion -> sepsis-shock + empiric-antibiotics + ecg-pocus-integration
- low-output shock, acute MI/heart-failure shock, cold hypoperfusion or escalating vasoactive requirement -> cardiogenic-shock + ecg-pocus-integration + medication-selection-safety; add acute-coronary-syndrome, critical-valvular-disease or arrhythmias-cardiac-arrest according to cause
- abrupt chest/back pain, pulse/pressure asymmetry, acute aortic regurgitation, malperfusion or unexplained shock -> acute-aortic-syndrome + medication-selection-safety + ecg-pocus-integration
- pericardial effusion with obstructive physiology, unexplained PEA or suspected tamponade -> cardiac-tamponade-pericardial-emergency + pocus + emergency-procedures + medication-selection-safety; add acute-aortic-syndrome or trauma-major-hemorrhage when relevant
- adult arrhythmia with pulse -> arrhythmias-cardiac-arrest + adult-arrhythmias
- adult cardiac arrest -> arrhythmias-cardiac-arrest + adult-cardiac-arrest
- pediatric arrhythmia with pulse -> pediatric-emergencies + pediatric-arrhythmias
- pediatric cardiac arrest beyond birth transition -> pediatric-emergencies + pediatric-cardiac-arrest
- vasopressor or inotrope infusion (norepinephrine, vasopressin, epinephrine, dopamine, dobutamine, milrinone, levosimendan, phenylephrine, angiotensin II): dose, dilution, mL/h, titration, peripheral line, extravasation or weaning -> vasoactive-inotrope-infusions + medication-selection-safety + the phenotype module (sepsis-shock, cardiogenic-shock, undifferentiated-shock or acute-heart-failure)
- heart failure -> acute-heart-failure
- valve emergency -> critical-valvular-disease
- endocarditis -> infective-endocarditis
- DVT/PE -> dvt + pulmonary-embolism
- severe hypertension with acute organ injury -> hypertensive-emergencies + iv-antihypertensive-selection + medication-selection-safety
- IV antihypertensive choice, unavailable nicardipine or antihypertensive infusion preparation -> iv-antihypertensive-selection + medication-selection-safety; add the organ-injury syndrome module
- pacemaker/ICD/LVAD problem -> device-complications + ecg-pocus-integration

## Neurologic
- acute focal neurologic deficit / suspected ischemic stroke -> acute-ischemic-stroke
- spontaneous intraparenchymal hemorrhage, hemorrhagic stroke, intraventricular hemorrhage or nontraumatic cerebellar hemorrhage -> spontaneous-intracerebral-hemorrhage + anticoagulation-reversal + medication-selection-safety; add clinical-image modules when an image is supplied
- convulsive status epilepticus in a child aged 1 month–18 years -> pediatric-status-epilepticus + status-epilepticus + pediatric-emergencies + medication-selection-safety; neonates <1 month use neonatal seizure pathway
- seizure/status (adult or child where no pediatric-specific route applies) -> status-epilepticus
- altered consciousness -> altered-consciousness; add toxicology, electrolytes, stroke or CNS infection only when supported by context
- headache/SAH -> headache-sah
- meningitis/encephalitis -> cns-infection
- traumatic intracranial hemorrhage, extra-axial hematoma, mass effect, midline shift or suspected herniation -> traumatic-intracranial-mass-effect; add trauma-major-hemorrhage, anticoagulation-reversal and clinical-image modules when applicable
- new spinal cord deficit, sensory level, malignant spinal cord compression, spinal epidural abscess or spinal epidural hematoma -> acute-spinal-cord-compression + medication-selection-safety; add anticoagulation-reversal, trauma-major-hemorrhage or empiric-antibiotics according to cause
- urinary retention/dysfunction with saddle symptoms, bilateral radicular deficit or suspected cauda equina/conus compression -> cauda-equina-conus-emergency + acute-spinal-cord-compression; add medication-selection-safety only when a drug or infusion decision is requested

## Respiratory
- acute asthma, status asthmaticus, silent chest or severe bronchospasm -> acute-severe-asthma + oxygen-therapy-emergency + medication-selection-safety; add acute-respiratory-failure and airway-rsi when fatigue or ventilatory failure is present
- acute COPD exacerbation, CO2 retention or hypercapnic acidosis -> copd-exacerbation + oxygen-therapy-emergency + medication-selection-safety; add noninvasive-ventilation for acidosis/distress and empiric-antibiotics only when bacterial criteria are present
- major, massive or life-threatening hemoptysis -> life-threatening-hemoptysis + airway-rsi + anticoagulation-reversal + emergency-procedures; add clinical-image-interpretation + chest-xray only when an image is supplied
- supplemental oxygen, nasal cannula, oxygen mask, Venturi or reservoir mask -> oxygen-therapy-emergency; add acute-respiratory-failure when hypoxemia, hypercapnia, increased work of breathing or deterioration is present
- high-flow nasal oxygen, HFNO/HFNC or ROX index -> high-flow-nasal-oxygen + oxygen-therapy-emergency + acute-respiratory-failure
- CPAP, BiPAP, bilevel or noninvasive ventilation -> noninvasive-ventilation + oxygen-therapy-emergency + acute-respiratory-failure
- respiratory failure -> acute-respiratory-failure + oxygen-therapy-emergency; add high-flow-nasal-oxygen or noninvasive-ventilation only when the corresponding support is being considered or used
- sudden dyspnea/chest pain with hypotension and unilateral reduced breath sounds, or suspected tension pneumothorax -> tension-pneumothorax + pocus + emergency-procedures
- emergency airway, failed oxygenation/ventilation, reduced consciousness requiring airway protection or intubation request -> airway-rsi + medication-selection-safety
- drowning/environmental -> environmental-emergencies

## Infection
- sepsis -> sepsis-shock
- anaphylaxis -> anaphylaxis
- antibiotic selection -> empiric-antibiotics
- febrile neutropenia -> hematology-oncology
- soft tissue -> soft-tissue-infections
- infectious syndromes -> emergency-infectious-diseases
- severe rash / mucosal or systemic involvement -> dermatology-severe

## Trauma / surgery
- thermal, chemical or electrical burn -> major-burns + medication-selection-safety; add pediatric-emergencies for children
- enclosed-space fire, smoke inhalation, carbon monoxide or cyanide concern -> smoke-inhalation-toxic-injury + toxicology + oxygen-therapy-emergency + medication-selection-safety; add major-burns for cutaneous burns and airway-rsi for airway compromise
- trauma / bleeding -> trauma-major-hemorrhage
- abdominal pain -> acute-abdomen
- hematemesis, melena or suspected upper GI bleeding -> upper-gi-bleeding
- hematochezia or suspected lower GI bleeding -> lower-gi-bleeding; add upper-gi-bleeding when an upper source is plausible, especially with instability
- disproportionate abdominal pain, suspected mesenteric ischemia or unexplained abdominal deterioration during shock -> acute-mesenteric-ischemia + acute-abdomen + empiric-antibiotics + medication-selection-safety
- pancreatitis -> pancreatitis
- orthopedic injury -> orthopedic-emergencies
- procedure -> emergency-procedures
- suspected symptomatic or ruptured abdominal aortic aneurysm -> abdominal-aortic-aneurysm + trauma-major-hemorrhage + pocus; add anticoagulation-reversal when applicable

## Renal / metabolic
- adrenal insufficiency, steroid withdrawal with shock or suspected adrenal crisis -> adrenal-crisis + medication-selection-safety
- thyrotoxic multisystem decompensation or thyroid storm -> thyroid-storm + medication-selection-safety; add cardiogenic-shock for low-output physiology
- severe hypothyroidism with altered consciousness, hypothermia or hypoventilation -> myxedema-coma + medication-selection-safety; add adrenal-crisis, sodium-emergencies or airway-rsi as indicated
- AKI -> aki-nephrology
- rhabdomyolysis -> rhabdomyolysis
- undifferentiated electrolyte disorder -> electrolytes
- hyponatremia or hypernatremia -> sodium-emergencies + medication-selection-safety
- hyperkalemia or hypokalemia -> potassium-emergencies + medication-selection-safety
- calcium or magnesium emergency -> calcium-magnesium-emergencies + medication-selection-safety
- DKA, euglycemic DKA, HHS or mixed DKA/HHS -> diabetic-ketoacidosis-hhs + acid-base-emergencies + medication-selection-safety
- blood gas or acid-base disorder -> acid-base-emergencies; add diabetic-ketoacidosis-hhs, toxicology, sepsis-shock, acute-respiratory-failure or aki-nephrology only when supported
- poisoning / overdose -> toxicology; add altered-consciousness when mental status is impaired
- alcohol withdrawal -> alcohol-withdrawal

## Special populations
- infant ≤90 days with fever ≥38.0°C or unexplained hypothermia -> febrile-infant-0-90-days + pediatric-emergencies + empiric-antibiotics; if ill-appearing add sepsis-shock and urgent neonatal/pediatric escalation
- infant/child <2 years with typical first-episode bronchiolitis -> bronchiolitis + pediatric-emergencies; add acute-respiratory-failure for respiratory failure
- barky cough/stridor consistent with croup -> croup + pediatric-emergencies; add airway-rsi only for airway intervention
- pediatric dehydration, gastroenteritis with dehydration, or hypovolemic/undifferentiated shock in a child -> pediatric-dehydration-shock + pediatric-emergencies; add sepsis-shock, diabetic-ketoacidosis-hhs, major-hemorrhage or cardiogenic-shock when supported
- pediatrics -> pediatric-emergencies
- pregnancy -> obstetric-emergencies
- frail older adult -> geriatric-emergencies
- psychiatric/agitation -> psychiatric-emergencies
- suicide risk -> suicide-risk
- observation or discharge decision -> observation-discharge

## Cross-cutting additions

- Add `medication-selection-safety` for any medication choice, dose, route,
  dilution or infusion question; combine it with the syndrome module rather than
  treating the drug name as the diagnosis.
- Add `pediatric-emergencies` for any child; add the age/syndrome-specific pediatric route when applicable. Add `geriatric-emergencies` when frailty, atypical presentation or baseline function changes decisions.
- Add `obstetric-emergencies` for pregnancy/postpartum emergencies.
- Add `ecg-pocus-integration` only when both modalities materially inform the syndrome; use `pocus` for a focused ultrasound-only question.
- Add `anticoagulation-reversal` for major bleeding or urgent procedure in an anticoagulated patient.
- Add `sedoanalgesia` and `medication-selection-safety` when procedural sedation or high-risk analgesia is requested.
- Continuous ICU analgesia/sedation of an intubated or ventilated adult (fentanyl, remifentanil, morphine, hydromorphone, propofol, dexmedetomidine, midazolam, ketamine infusion; RASS/CPOT/BPS targets, PRIS, daily interruption) -> icu-sedation-analgesia-infusions + medication-selection-safety; add delirium or airway-rsi when relevant. Pediatric infusions are not covered.
