# Modality-specific clinical image modules

Shared gate: load `clinical-image-interpretation` first. Inspect the actual pixels,
apply `references/image-intake.md`, distinguish observed/inferred/not assessable,
and use `references/image-output-schema.json`. These are focused decision-support
checklists, not replacements for original DICOM/series, formal reporting or specialist
review. Do not force a classification when required views or clinical data are absent.

No system output alone excludes urgent pathology. Integrate the clinical history,
direct examination and appropriate complete investigations; escalate persistent
clinical concern even when an image interpretation appears reassuring.

## musculoskeletal-xray

- Use as adjunctive support; never replace the definitive radiology reading.
  The clinician should interpret the radiograph before reviewing assisted output
  to reduce automation bias and omission of non-fracture findings. NICE HTG739
  evaluates specific fracture products in the NHS; it does not validate this module
  or justify a blanket exclusion of pediatric use.
- Identify region, supplied views, projection, laterality marker, skeletal maturity,
  image coverage, exposure, rotation and whether this is an original export or screen photo.
- Review alignment, cortices, trabeculae, joint congruity/spaces and soft tissues.
- If a fracture is visible, describe bone/segment, orientation, articular extension,
  displacement/translation, angulation, shortening, comminution and associated dislocation
  only to the extent actually supported. Do not report millimetres/degrees without valid scale.
- Use named classifications (for example Weber, Salter-Harris or Garden) only when their
  defining features are visible. State `provisional` and list the missing view or examination
  that determines stability or treatment.
- Check for open injury, skin threat, compartment syndrome and neurovascular compromise
  clinically. Recommend orthogonal views or appropriate advanced imaging when a single
  projection cannot exclude occult/associated injury.
- For ankle images specifically: assess mortise congruity, medial clear space qualitatively,
  fibular fracture level, visible posterior/medial malleolus and syndesmotic concern. Do not
  declare stability or surgical indication from an unstressed single view.
- A negative radiograph does not exclude an occult fracture when symptoms/examination remain suspicious. For suspected scaphoid fracture after thorough clinical examination, NICE NG38 advises considering first-line MRI. For suspected hip fracture despite adequate negative X-rays, NICE CG124 recommends MRI; consider CT if MRI is unavailable within 24 hours or contraindicated. Persistent suspicion after inconclusive imaging needs protection, reassessment and specialist-directed further imaging rather than unrestricted discharge.
- Select an appropriate radiographic series and advanced imaging with the clinical question, age, examination and validated site-specific rules; do not apply an adult classification or one-view exclusion rule to a child's physis. Limb threat, open injury, dislocation, suspected septic joint or compartment syndrome requires immediate clinical/orthopedic assessment, not waiting for a complete image report. Route to `orthopedic-emergencies` and `acute-musculoskeletal-pain` for management and neurovascular reassessment.
- Record supplied views, image limitations, provisional interpretation, uncertain classification and the next action; reconcile with the formal radiology report and assign ownership for discrepant or pending findings. A bibliographically reviewed reading framework does not establish diagnostic accuracy. No new patient images or independently adjudicated image cases were assessed in this review; do not report sensitivity, specificity or validated exclusion performance.

## chest-xray

- Use as adjunctive support; never replace the definitive radiology reading.
  The clinician should interpret the radiograph before reviewing assisted output.
  NICE HTG696 concerns primary-care referrals for suspected lung cancer; it does
  not establish performance for acute emergency chest radiographs or this module.
- Identify AP/PA, upright/supine, rotation, inspiration, exposure and field coverage.
- Review airway, lungs, pleura, hila, cardiomediastinal contour, diaphragms, bones and devices.
- State whether focal opacity, interstitial/alveolar pattern, pleural air/fluid, volume loss,
  edema pattern or device malposition is directly visible; avoid unsupported etiologic certainty.
- Account for AP/supine magnification and occult pneumothorax limitations. A normal film does
  not exclude PE, ACS, early infection or acute aortic disease.
- Urgently flag a possible tension pneumothorax, major device malposition, large effusion,
  marked edema or other immediately actionable finding, but integrate physiology and escalate.

## pocus-image

- Isolated static POCUS images do not exclude acute pathology.
- POCUS is a dynamic, operator-dependent bedside examination, often following a
  rule-in philosophy (ACEP 2023; IFEM 2021). Still images can document a supported
  focal finding or be archived for QA. An isolated still without real-time
  acquisition, complete required windows and clinical correlation cannot exclude
  acute pathology or replace a complete dynamic POCUS examination.
- Identify organ, plane, probe/setting when known, orientation marker, depth, gain, focus,
  Doppler settings and whether the input is a still, cine or compression sequence.
- Describe visible echogenicity, borders, fluid, artifacts, shadowing/enhancement and calipers.
- A single static B-mode frame cannot establish lung sliding, compressibility, respiratory
  variation, valve motion, ejection fraction or dynamic response. An M-mode tracing of the
  pleural line contains temporal information along the sampled line; assess only the
  acquisition, location and recorded interval actually shown, with an identifiable time
  axis. It does not establish that a complete cine or compression sequence has been
  reviewed. One color-Doppler frame cannot establish absent flow.
- For a binary focused question, list the minimum required views/dynamic manoeuvre and say
  whether they were supplied. A technically limited POCUS does not exclude a high-risk syndrome.
- Preserve saved images/clips and seek expert or comprehensive imaging when the decision exceeds
  focused ultrasound scope.

## ecg-image

- Every algorithmic output or alert is provisional and requires direct medical
  reading, clinical correlation and verification of tracing quality and calibration.
- Confirm the complete 12-lead tracing is visible and record calibration, paper speed,
  lead labels, baseline quality and distortion/perspective.
- Assess rhythm, approximate rate, axis, conduction, intervals and ST-T morphology only as
  supported. Do not invent precise intervals or QTc from a cropped, blurred or uncalibrated photo.
- Check lead consistency and possible reversal/artifact before interpreting abnormalities.
- Treat ischemic patterns, malignant arrhythmia, high-grade block and hyperkalemic patterns as
  time-sensitive clinical findings. A nondiagnostic ECG does not exclude ACS or arrhythmia.
- Explicitly screen for high-risk/eponymous ECG patterns when the tracing and clinical context support them:
  - **de Winter pattern:** typically 1–3 mm upsloping ST-segment depression at the J point in V1–V6 that continues into tall, positive, symmetric T waves; often associated with proximal LAD occlusion/severe stenosis and should trigger an acute coronary occlusion pathway rather than reassurance from absent classic ST elevation.
  - **Wellens pattern:** in a compatible recent-angina/pain-free context, biphasic T waves in V2–V3 (type A) or deep, symmetric T-wave inversion in V2–V3 (type B), sometimes extending to adjacent precordial leads, with an isoelectric or minimally elevated ST segment; this suggests critical proximal LAD disease and requires urgent cardiology evaluation. Do not perform stress testing when Wellens syndrome is suspected.
  - **Peñaloza–Tranchesi sign (historical, indirect finding):** low-amplitude QRS in V1 with a marked amplitude increase in V2, described as an indirect sign of right atrial enlargement. It is nonspecific and does not establish chamber enlargement alone; correlate with lead placement, the full ECG and echocardiography.


## blood-gas-image

- Identify whether the input is an analyzer printout, electronic report screenshot or photograph. Confirm that pH, PCO2, PO2, bicarbonate/base excess, lactate, electrolytes, glucose, units, reference ranges and analyzer flags are actually visible; do not infer cropped values.
- Record the displayed sample type (arterial, venous or capillary), collection time and FiO2/oxygen device. If the report does not label the specimen, call it an unlabeled blood gas rather than an arterial gas. Do not interpret PO2 as arterial oxygenation from an unlabeled or venous sample.
- Transcribe each value with its unit and visually verify every digit, decimal sign and inequality. Flag glare, blur, truncation, OCR uncertainty, implausible internal inconsistency or values outside the analyzer's reportable range. Never silently repair a suspected digit.
- Separate displayed/measured values from analyzer-calculated values such as bicarbonate and base excess. If pH and PCO2 are legible, compare calculated bicarbonate using Henderson--Hasselbalch as a consistency check, not as proof that the transcription is correct.
- For a labelled arterial sample with a visible FiO2, calculate `PaO2/FiO2` after normalizing FiO2 to a fraction. If barometric pressure is known, optionally calculate alveolar PO2 and the A--a gradient with the stated respiratory quotient. Do not assume sea level or a fixed FiO2 from an oxygen-device label. A low P/F ratio quantifies oxygenation failure but does not by itself diagnose ARDS: require timing, imaging, edema-origin assessment and the applicable PEEP/respiratory-support criterion.
- Perform a second danger pass over ionized calcium, potassium, sodium, glucose, lactate and hemoglobin/hematocrit. Do not let a near-normal pH hide critical oxygenation or electrolyte abnormalities; repeat an unexpected critical value from a clean sample while treating immediately when symptoms, ECG changes or instability make delay unsafe.
- After transcription is confirmed, route to `acid-base-emergencies`; add `diabetic-ketoacidosis-hhs` when glucose/ketones or the clinical context suggests a hyperglycemic crisis. Use `scripts/acid_base_hyperglycemia.py` only on verified values.
- Lead with immediate danger when visible: profound acidemia/alkalemia, severe hypercapnia, critical lactate, potassium abnormality or incompatible oxygenation. A single gas does not establish cause, chronicity or trajectory; compare prior/subsequent samples and the patient.

## skin-wound-image

- Hand wounds require direct neurovascular and tendon examination. A photograph
  cannot establish intact perfusion, sensation or tendon function.
  Document this examination before local anesthesia (WSES/AcEMC 2016).
  A superficial photograph cannot exclude retained foreign bodies or necrotizing
  soft-tissue infection. Do not prescribe antimicrobials or tetanus/rabies schedules
  from the photograph; use vaccination history and applicable clinical protocols.
- Phototypes V–VI require special caution and clinical review. Do not use apparent
  absence of erythema or other color changes as reassurance from a photograph alone.
  Require direct in-person clinical and/or dermoscopic assessment; no system output
  excludes malignancy. Accuracy in Fitzpatrick V–VI cannot be assumed without
  stratified validation. NICE HTG746 concerns DERM in the adult NHS urgent suspected
  skin-cancer pathway; its EVA review requirement is not a universal contraindication
  for every dermatology system (R50; AAD AuI 2019).
- Record body region, distribution, number, morphology, borders, surface, color, drainage,
  surrounding change and scale only if a reliable reference is present.
- State that warmth, tenderness, fluctuance, crepitus, depth and pain out of proportion are not
  assessable from a photograph. Lighting, white balance and skin tone affect apparent color.
- Do not label a lesion benign or exclude necrotizing infection from appearance alone. Escalate
  systemic toxicity, rapid progression, severe pain, bullae, necrosis or mucosal involvement.
- For pigmented lesions, provide descriptive concern and appropriate examination/referral rather
  than definitive melanoma exclusion or diagnosis from a casual photograph.

## ct-mri-screenshot

- Isolated CT/MRI screenshots or incomplete series do not replace a complete evaluation.
- Urgent diagnostic assessment requires intact volumetric DICOM series and specialist
  reading. Isolated slices, compressed screenshots or incomplete series cannot exclude
  intracranial hemorrhage, acute ischemic stroke or other critical pathology. Do not
  apply an unsupported universal hemorrhage-volume threshold. A focal visible finding
  can justify escalation while the complete study is obtained and reviewed.
- Identify stated modality, body region, plane, sequence/window, contrast phase and anatomic level.
- For brain CT/MRI, explicitly review both convexities and extra-axial spaces,
  hemispheric symmetry, sulci, ventricles, basal cisterns, falx/septum/pineal midline,
  mass effect, herniation pattern and visible calvarium before any reassuring claim.
  A crescentic or lentiform compartment must be traced through adjacent slices; compare
  ventricular compression and displacement of midline landmarks, not skull symmetry alone.
- For a photographed or screen-recorded stack, sample the start, middle and end plus
  contiguous frames around any asymmetry at original available quality. Do not use a
  tiled contact sheet as the final diagnostic view. Review orthogonal reconstructions
  when supplied and reconcile them with the axial sequence.
- Assign left/right only from a visible marker, DICOM orientation or confirmed display
  convention. Otherwise describe the image side and state laterality as conditional.
- A negative intracranial study claim requires adequate brain windows and coverage of
  extra-axial spaces, ventricles, cisterns and midline. If any are not assessable, state
  that limitation and avoid excluding hemorrhage or mass effect.
- Describe only findings within supplied pixels. A screenshot is not the study and cannot support
  whole-organ review, staging, vascular exclusion or absence of pathology on unsupplied slices.
- Do not infer Hounsfield units, enhancement kinetics, diffusion restriction or measurements
  without appropriate series/data. Request the full study and formal report for definitive use.
- If the screenshot suggests hemorrhage, mass effect, large-vessel occlusion, PE, dissection or
  another critical process, escalate clinically while confirming with the complete study/expert.
- When hemorrhage and mass effect coexist, state the compartment separately from the danger signs:
  sulcal effacement, ventricular compression, cisternal effacement, midline displacement and any
  visible herniation pattern. Route traumatic extra-axial hemorrhage or suspected herniation to
  `traumatic-intracranial-mass-effect`; do not stop at naming the collection.

## ophthalmology-image

- Identify external photograph, slit-lamp, fluorescein, fundus, OCT or other acquisition and
  whether laterality is confirmed. Describe only the visible structure and quality.
- A photograph cannot replace visual acuity, pupils, fields, pressure (when safe), movements and
  appropriate dilated/slit-lamp examination.
- Urgently escalate suspected open globe, retinal arterial occlusion/detachment, endophthalmitis,
  orbital cellulitis, acute angle closure or chemical injury. Irrigation precedes photography in
  chemical exposure.

## other-clinical-image

- State the modality/organ actually recognized and the limits of familiarity and supplied data.
- Describe secure visible features without silently generalizing to pathology slides, endoscopy,
  specialized nuclear medicine or other domains. Seek the appropriate specialist interpretation.
