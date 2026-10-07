# Modality-specific clinical image modules

Shared gate: load `clinical-image-interpretation` first. Inspect the actual pixels,
apply `references/image-intake.md`, distinguish observed/inferred/not assessable,
and use `references/image-output-schema.json`. These are focused decision-support
checklists, not replacements for original DICOM/series, formal reporting or specialist
review. Do not force a classification when required views or clinical data are absent.

## musculoskeletal-xray

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

## chest-xray

- Identify AP/PA, upright/supine, rotation, inspiration, exposure and field coverage.
- Review airway, lungs, pleura, hila, cardiomediastinal contour, diaphragms, bones and devices.
- State whether focal opacity, interstitial/alveolar pattern, pleural air/fluid, volume loss,
  edema pattern or device malposition is directly visible; avoid unsupported etiologic certainty.
- Account for AP/supine magnification and occult pneumothorax limitations. A normal film does
  not exclude PE, ACS, early infection or acute aortic disease.
- Urgently flag a possible tension pneumothorax, major device malposition, large effusion,
  marked edema or other immediately actionable finding, but integrate physiology and escalate.

## pocus-image

- Identify organ, plane, probe/setting when known, orientation marker, depth, gain, focus,
  Doppler settings and whether the input is a still, cine or compression sequence.
- Describe visible echogenicity, borders, fluid, artifacts, shadowing/enhancement and calipers.
- A still cannot prove lung sliding, compressibility, respiratory variation, valve motion,
  ejection fraction or dynamic response. One color-Doppler frame cannot establish absent flow.
- For a binary focused question, list the minimum required views/dynamic manoeuvre and say
  whether they were supplied. A technically limited POCUS does not exclude a high-risk syndrome.
- Preserve saved images/clips and seek expert or comprehensive imaging when the decision exceeds
  focused ultrasound scope.

## ecg-image

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
  - **Peñaloza–Tranchesi sign (historical eponym):** prominent/deep S waves in the left precordial leads, especially V5–V6, as a supportive sign of right-ventricular hypertrophy/overload. Do not diagnose RV hypertrophy from this sign alone; integrate right-axis deviation, R/S morphology in V1–V2, strain pattern, echocardiography and clinical context.


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

- Record body region, distribution, number, morphology, borders, surface, color, drainage,
  surrounding change and scale only if a reliable reference is present.
- State that warmth, tenderness, fluctuance, crepitus, depth and pain out of proportion are not
  assessable from a photograph. Lighting, white balance and skin tone affect apparent color.
- Do not label a lesion benign or exclude necrotizing infection from appearance alone. Escalate
  systemic toxicity, rapid progression, severe pain, bullae, necrosis or mucosal involvement.
- For pigmented lesions, provide descriptive concern and appropriate examination/referral rather
  than definitive melanoma exclusion or diagnosis from a casual photograph.

## ct-mri-screenshot

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
