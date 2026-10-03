# Toxicology high-risk clinical QA — 2026-10-03

Branch: `v1.36-consolidation`
Scope: existing IDs `toxicology` and `anticoagulation-reversal`.

This is a **structured clinical regression bank**, not prospective validation and not a substitute for poison-centre, hematology or pharmacy review. PASS means the module contains the expected safe route and does not provide a contraindicated default.

| # | Stress case | Expected critical response | Result |
|---|---|---|---|
| 1 | Cocaine, severe agitation, hyperthermia, HTN/tachycardia | Benzodiazepine-centred sedation + active cooling/support; no fictional antidote | PASS |
| 2 | Cocaine with wide QRS/ventricular dysrhythmia | ALS + sodium bicarbonate for sodium-channel blockade | PASS |
| 3 | TCA overdose, hypotension + QRS widening | Sodium bicarbonate; ECG/pH-guided repetition; avoid physostigmine | PASS |
| 4 | Digoxin toxicity, malignant dysrhythmia/hyperkalaemia | Digoxin-specific Fab; calculate from burden/level if feasible | PASS |
| 5 | Organophosphate, bronchorrhoea + bradycardia + fasciculation | Rapidly titrated atropine to pulmonary/physiologic endpoints + pralidoxime | PASS |
| 6 | Acute acetaminophen ingestion, treatment decision delayed beyond 8 h | Start NAC when indicated; nomogram only for valid acute timing; >=300 mg/kg/20–24 h regimen and stopping criteria | PASS |
| 7 | Repeated supratherapeutic acetaminophen >24 h | Do not use Rumack-Matthew as if single acute ingestion; use level/LFT-driven pathway | PASS |
| 8 | Methanol with high-gap acidosis/visual symptoms | Fomepizole + cofactor/support + EXTRIP haemodialysis escalation | PASS |
| 9 | Ethylene glycol with severe acidosis/AKI | Fomepizole + cofactor/support + ECTR criteria | PASS |
| 10 | Beta-blocker shock refractory to basic support | Early high-dose insulin pathway + glucose/K monitoring; glucagon as selected adjunct | PASS |
| 11 | Calcium-channel blocker shock | Calcium + early high-dose insulin + vasopressor phenotype; rescue ILE/ECMO when refractory | PASS |
| 12 | Cyanide suspected after smoke exposure with severe lactic acidosis/shock | Treat before confirmatory test; hydroxocobalamin preferred | PASS |
| 13 | Life-threatening dabigatran bleed | Idarucizumab 5 g IV (2 x 2.5 g); consider dialysis in selected high-burden/renal cases | PASS |
| 14 | Apixaban 10 mg taken 3 h ago + life-threatening bleed | EMA high-dose andexanet (800 mg bolus + 8 mg/min x120 min) if selected/available | PASS |
| 15 | Rivaroxaban 10 mg taken 3 h ago + life-threatening bleed | EMA low-dose andexanet (400 mg + 4 mg/min x120 min) if selected/available | PASS |
| 16 | UFH infusion stopped after major bleed | Protamine based on recent UFH exposure, approximately 1 mg/100 U; slow IV/max safeguards | PASS |
| 17 | Enoxaparin major bleed 4 h after last dose | Partial reversal with protamine 1 mg per 1 mg enoxaparin; repeat 0.5 mg/mg if indicated | PASS |
| 18 | Fondaparinux major bleed | Explicitly no specific antidote; protamine ineffective; expert nonspecific haemostatic rescue only | PASS |
| 19 | Edoxaban major bleed | Do not falsely label EMA andexanet indication; nonspecific PCC/hematology pathway | PASS |
| 20 | Argatroban/bivalirudin severe bleed | No specific antidote; stop drug, source control/support; account for organ-dependent half-life | PASS |
| 21 | Superwarfarin rodenticide coagulopathy | Vitamin K1 guided by INR for prolonged duration; PCC reserved for severe bleeding | PASS |
| 22 | Warfarin ICH/life-threatening bleed | IV vitamin K + 4F-PCC, product/INR/weight-specific dosing | PASS |
| 23 | Benzodiazepine overdose with chronic dependence/unknown coingestion | Supportive care; flumazenil NOT default because seizure/withdrawal risk | PASS |
| 24 | Sulfonylurea recurrent hypoglycaemia | Dextrose + octreotide and prolonged monitoring | PASS |

## Evidence anchors checked
- AHA 2023 focused poisoning update: high-dose insulin for life-threatening beta-blocker/CCB poisoning; sodium bicarbonate for life-threatening cocaine/sodium-channel-blocker dysrhythmias; immediate cyanide antidote; digoxin Fab; 20% lipid emulsion for severe local-anaesthetic toxicity.
- 2023 US/Canada acetaminophen consensus: treatment nomogram restrictions, early NAC when delay would exceed 8 h, >=300 mg/kg over first 20–24 h, and explicit stopping criteria rather than automatic cessation at 20–21 h.
- EMA Praxbind: idarucizumab 5 g IV as two consecutive 2.5 g administrations.
- EMA Ondexxya: low/high dosing tables for apixaban and rivaroxaban; no dose recommendation when last dose or interval is unknown.

## QA interpretation
- **24/24 structured stress cases PASS.**
- No new module IDs created.
- This does **not** upgrade `toxicology` or `anticoagulation-reversal` to green: exact local antidote stock, product-specific PCC dosing, CIAV workflow, INFARMED/formulary reconciliation and human toxicology/hematology/pharmacy review remain release gates.
- No claim is made that these 24 cases were executed by the repository's Python unit suite. They are documented clinical regression cases.
