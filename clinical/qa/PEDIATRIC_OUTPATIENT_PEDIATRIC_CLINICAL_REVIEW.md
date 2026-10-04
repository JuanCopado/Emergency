# PEDIATRIC OUTPATIENT — PEDIATRIC CLINICAL REVIEW

Date: 2026-10-04
Branch: `v1.38-pediatric-outpatient-medications`
Module: `pediatric-outpatient-medications`

## Review status
AI-assisted pediatric clinical audit of **89/89 diagnosis-specific outpatient regimens** completed.

This is **not** a human pediatrician sign-off and does not promote the module to green.

Outcomes:
- PASS: **41**
- PASS_AFTER_CORRECTION: **40**
- PASS_WITH_NONCRITICAL_NOTE: **8**
- CHANGE_REQUIRED unresolved: **0**

Individual outcomes: `qa/PEDIATRIC_OUTPATIENT_PEDIATRIC_CLINICAL_REVIEW.json`.

## Review dimensions
Each regimen was reviewed for:
- indication/diagnostic fit;
- age and source scope;
- outpatient/discharge suitability;
- red flags and escalation;
- follow-up requirements;
- separation of hospital-only/step-down regimens from routine outpatient treatment;
- source alignment.

Dose arithmetic, concentration and pharmacy safety remain separately covered by the pharmacy review/calculator QA.

## Clinically important corrections applied

### Infection / antibiotics
- **Bites:** 5-day amoxicillin/clavulanate is now restricted to prophylaxis of a high-risk, clinically uninfected bite. Established infection is blocked from this regimen.
- **Orbital cellulitis:** amoxicillin/clavulanate 22.5 mg/kg BID is now explicitly an oral step-down regimen after initial IV/specialist treatment, not a routine mild preseptal regimen.
- **Pyelonephritis:** RCH high-dose cefalexin entries are explicitly source-specific oral step-down/high-dose pathways; they require confirmation and a urine sample before antibiotics.
- **Lower UTI:** urine sample before antibiotics is required whenever clinically feasible.
- **General RCH antimicrobial scope:** generic outpatient regimens no longer extrapolate to neonates unless the source specifically supports neonatal use.
- **Infected eczema:** oral cefalexin requires a systemically well child and blocks suspected eczema herpeticum.

### Respiratory
- **CAP:** outpatient amoxicillin requires explicit outpatient criteria.
- **Asthma:** salbutamol discharge and all outpatient systemic steroid regimens require asthma discharge criteria.
- **Prednisolone <2 years:** additionally requires an explicit pediatric/ED discharge plan.
- **Croup:** dexamethasone outpatient use requires croup discharge criteria.

### Gastrointestinal / hydration
- **NICE ORS 50 mL/kg/4 h and 5 mL/kg after watery stool:** exact entries are now source-scoped to children under 5 years.
- **Ondansetron gastroenteritis:** requires exclusion of gastroenteritis red flags/alternative diagnoses before use.
- **Constipation:** laxative pathways are explicitly for functional/idiopathic constipation and block suspected obstruction/organic red flags.

### Neurology / eye
- **Migraine:** rizatriptan and migraine ondansetron require secondary-headache red flags to be excluded.
- **Conjunctivitis:** bacterial/allergic outpatient treatment requires sight-threatening red-eye features to be excluded.
- **Neonatal conjunctivitis:** excluded from the generic chloramphenicol outpatient pathway.

### Antivirals / allergy
- **Varicella aciclovir:** routine treatment of otherwise healthy uncomplicated varicella is blocked; a guideline-supported antiviral indication must be confirmed. Severe/disseminated disease is excluded.
- **HSV aciclovir:** neonatal and severe/immunocompromised HSV are excluded from the generic oral outpatient regimen.
- **Oseltamivir:** requires confirmation that antiviral treatment is clinically indicated.
- **Anaphylaxis:** auto-injector discharge support requires clinical discharge/observation/education criteria.

### Analgesia
- **Home paracetamol:** requires explicit home-treatment suitability. Fever in infants <3 months remains an age-specific febrile-infant problem and cannot be reduced to dose calculation.

## Noncritical notes retained
- GINA AIR/MART regimens remain age/step/device-specific; no silent extrapolation to different devices or Step 5 strategies.
- Rizatriptan exact 40-kg source boundary remains fail-closed.
- NICE 3-day and SmPC 7-day nitrofurantoin strategies remain separate.
- Praziquantel age scope remains conservative for this individual-treatment entry.
- Ivermectin <15 kg / Loa loa boundaries remain explicit.
- Product-specific and organ-function restrictions from the pharmacy review remain active.

## Validation
Dedicated boundary tests now verify:
- bite prophylaxis vs established infection;
- orbital-cellulitis step-down;
- pyelonephritis step-down;
- under-5 ORS source scope;
- varicella/HSV escalation;
- UTI urine-sample gate;
- oseltamivir indication;
- gastroenteritis red flags;
- eczema herpeticum exclusion;
- home paracetamol suitability;
- asthma/croup discharge criteria.

## Promotion rule
Module remains **yellow**. Green promotion still requires independent human pediatric and pharmacy review plus passing Clinical QA after any resulting changes.
