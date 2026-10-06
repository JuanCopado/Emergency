#!/usr/bin/env python3

import base64
import json
import sys
import unittest
import tempfile
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pediatric_outpatient_calculator import calculate as calculate_pediatric_outpatient, load_registry as load_pediatric_outpatient_registry, preflight as pediatric_outpatient_preflight, MedicationSafetyStop
from pediatric_outpatient_alert_engine import evaluate as evaluate_pediatric_alerts
from clinical_note_support import (
    new_note as new_clinical_note,
    route_attachment as route_clinical_attachment,
    add_report as add_clinical_report,
    scan_privacy as scan_clinical_note_privacy,
    validate_for_export as validate_clinical_note_export,
    diagnostic_support_contract as clinical_note_diagnostic_contract,
)
from clinical_note_exporter import export_docx as export_clinical_note_docx, export_pdf as export_clinical_note_pdf
from clinical_note_api import (
    prepare_upload as prepare_clinical_upload,
    accept_prepared_upload as accept_clinical_upload,
    run_diagnostic_support as run_clinical_note_api_diagnostic,
    export_note_bytes as export_clinical_note_bytes,
)
from final_human_review_gate import build_review_queue as build_final_human_review_queue
from run_clinical_note_synthetic_cases import run as run_clinical_note_synthetic_cases
from run_clinical_note_diagnostic_cases import run as run_clinical_note_diagnostic_cases
from run_clinical_note_pediatric_routing_cases import run as run_clinical_note_pediatric_routing_cases
from run_clinical_note_diagnostic_closure_cases import run as run_clinical_note_diagnostic_closure_cases
from audit_clinical_note_diagnostic_coverage import audit as audit_clinical_note_diagnostic_coverage

from infusion_calculator import infusion_ml_h, fixed_dose_ml_h, weight_per_hour_ml_h
from load_module import load
from validate_modules import validate
from weight_based_dose import weight_based_dose
from context_validator import validate_inputs
from evaluate_image_cases import evaluate
from sodium_water_balance import calculate as sodium_water_balance
from acid_base_hyperglycemia import calculate as acid_base_hyperglycemia
from respiratory_support import calculate as respiratory_support
from pediatric_pump_table import pump_table as pediatric_pump_table
from pediatric_bolus_calculator import calculate as pediatric_bolus_calculate, calculate_with_selected_concentration as pediatric_bolus_with_concentration
from pediatric_antibiotic_calculator import calculate as pediatric_antibiotic_calculate
from pediatric_blood_product_calculator import (
    trauma_rbc_ml as pediatric_trauma_rbc_ml,
    stable_rbc_ml as pediatric_stable_rbc_ml,
    stable_rbc_rate_ml_h as pediatric_stable_rbc_rate_ml_h,
    platelets_ml as pediatric_platelets_ml,
    ffp_range_ml as pediatric_ffp_range_ml,
    cryoprecipitate_range_ml as pediatric_cryo_range_ml,
)
from pediatric_fluid_calculator import (
    maintenance_ml_day as pediatric_fluid_maintenance_ml_day,
    maintenance_ml_h as pediatric_fluid_maintenance_ml_h,
    shock_bolus as pediatric_fluid_shock_bolus,
    ors_rehydration as pediatric_ors_rehydration,
    dehydration_deficit_ml as pediatric_dehydration_deficit_ml,
    generic_deficit_48h_plan as pediatric_generic_deficit_48h_plan,
    gastroenteritis_iv_deficit as pediatric_gastroenteritis_iv_deficit,
    hypernatremia_deficit_rate as pediatric_hypernatremia_deficit_rate,
    symptomatic_hyponatremia_bolus as pediatric_symptomatic_hyponatremia_bolus,
)
from pediatric_emergency_calculator import (
    weight_based_total as pediatric_weight_based_total,
    volume_for_dose as pediatric_volume_for_dose,
    infusion_per_kg_min_ml_h as pediatric_infusion_per_kg_min_ml_h,
    fluid_bolus_ml as pediatric_fluid_bolus_ml,
    maintenance_ml_day as pediatric_maintenance_ml_day,
    maintenance_ml_h as pediatric_maintenance_ml_h,
    gastroenteritis_deficit_ml as pediatric_gastroenteritis_deficit_ml,
)
from pediatric_respiratory_support import hfno_flow_l_min as pediatric_hfno_flow_l_min, ventilation_rate_reference as pediatric_ventilation_rate_reference
from pediatric_dka_calculator import corrected_sodium as pediatric_dka_corrected_sodium, insulin_ml_h as pediatric_dka_insulin_ml_h, cerebral_injury_rescue as pediatric_dka_cerebral_rescue
from pediatric_burn_calculator import burn_plan as pediatric_burn_plan
from pediatric_hypertension_calculator import labetalol_ml_h as pediatric_labetalol_ml_h, hydralazine_ml_h as pediatric_hydralazine_ml_h
from validate_clinical_cases import validate as validate_clinical_cases
from audit_evidence_coverage import audit as audit_evidence_coverage
from validate_real_image_cases import validate as validate_real_image_cases
from validate_blinded_image_dataset import validate as validate_blinded_image_dataset
from calculate_blinded_image_metrics import calculate as calculate_blinded_image_metrics
from create_blinded_image_dataset import build as build_blinded_image_dataset
from prepare_ptbxl_blinded_cohort import prepare as prepare_ptbxl_blinded_cohort
from finalize_blinded_image_dataset import finalize as finalize_blinded_image_dataset
from merge_blinded_prediction_shards import merge as merge_blinded_prediction_shards
from predict_ptbxl_afib_image_baseline import classify_features as classify_ptbxl_afib_baseline
from render_rsna_ich_dicom import window_hu_scalar as rsna_window_hu_scalar, slice_position as rsna_slice_position
from prepare_echonet_visual_input import frame_indices as echonet_frame_indices
from prepare_rsna_ich_blinded_cohort import prepare as prepare_rsna_ich_blinded_cohort
from prepare_chexpert_expert_blinded_cohort import prepare as prepare_chexpert_expert_blinded_cohort
from prepare_echonet_dynamic_blinded_cohort import prepare as prepare_echonet_dynamic_blinded_cohort
from prepare_mimic_cxr_curated_blinded_cohort import prepare as prepare_mimic_cxr_curated_blinded_cohort
from create_blinded_prediction_template import build as build_blinded_prediction_template
from shard_blinded_image_manifest import shard as shard_blinded_image_manifest
from clinical_calculator import calculate as central_calculate, calculate_scale as central_calculate_scale, load_registry as central_load_registry
from core_scores_block1 import calculate_gcs, calculate_nihss, calculate_news2, calculate_sofa1
from core_scores_block2 import calculate_heart, prepare_grace2, calculate_cha2ds2_vasc, calculate_cha2ds2_va
from core_scores_block3 import calculate_wells_pe, calculate_perc, calculate_years
from core_scores_block4 import calculate_glasgow_blatchford, calculate_curb65, calculate_phoenix_sepsis
from core_score_sofa2 import calculate_sofa2
from core_scores_block5 import calculate_oakland, calculate_obstetric_shock_index, calculate_revised_baux
from core_scores_block6 import calculate_bishop, calculate_meows_nnuh_v7, calculate_rule_of_nines, calculate_lund_browder
from core_scores_block7 import calculate_bedside_pews, calculate_pediatric_trauma_score, calculate_sipa, calculate_flacc, prepare_wong_baker, calculate_pram, calculate_westley_croup, calculate_clinical_dehydration, calculate_pediatric_appendicitis, classify_pecarn_head_injury
from core_scores_block8 import classify_pecarn_febrile_infant, classify_step_by_step, calculate_apgar
from specialist_scores_block1 import calculate_canadian_tia, calculate_pc_aspects, calculate_four_score, classify_hunt_hess, calculate_wfns_sah, calculate_stess, calculate_bacterial_meningitis_score
from specialist_scores_block2 import calculate_edacs, calculate_orbit, calculate_tisdale, calculate_bova, calculate_sic, calculate_mews, calculate_sirs
from specialist_scores_block3 import calculate_apache2, prepare_saps3, calculate_bps, calculate_age_shock_index, calculate_smart_cop, calculate_mmrc, calculate_hacor, calculate_niss, calculate_triss, calculate_nexus_head_ct
from specialist_scores_block4 import calculate_rockall, calculate_ranson, calculate_meld3, calculate_lille, classify_poisoning_severity, calculate_pawss
from specialist_scores_block5 import calculate_phq9, calculate_gad7, calculate_cisne, calculate_lrinec, calculate_puqe24, calculate_fullpiers
from specialist_scores_block6 import calculate_psofa, calculate_pelod2, calculate_parc, calculate_charlson, calculate_barthel
from core_scores_block5_neuro import calculate_abcd2, calculate_aspects, calculate_modified_rankin, calculate_ich_score, calculate_modified_fisher, calculate_cincinnati, calculate_race, calculate_fast_ed
from core_scores_block6_transversal import calculate_avpu
from core_score_pediatric_gcs import calculate_pediatric_gcs
from core_scores_block7_cardiology import calculate_timi_ua_nstemi, calculate_has_bled, calculate_canadian_syncope, calculate_killip_kimball, calculate_scai_shock
from core_scores_block8_tev import calculate_revised_geneva, calculate_pesi, calculate_spesi, calculate_hestia, calculate_wells_dvt
from core_scores_block9_respiratory import calculate_crb65, calculate_psi_port, calculate_decaf, classify_berlin_ards
from core_scores_block10_trauma import calculate_rts, calculate_iss, calculate_abc_massive_transfusion, calculate_canadian_ct_head, calculate_canadian_cspine, calculate_nexus_cspine
from core_scores_block11_digestive_hepatology import calculate_aims65, calculate_bisap, calculate_child_pugh, calculate_kings_college
from core_scores_block12_mixed import calculate_qsofa, calculate_isth_dic, classify_kdigo_aki, calculate_mcmahon, calculate_alvarado, calculate_air
from core_scores_block13_toxicology import evaluate_rumack_matthew, evaluate_hunter_serotonin, calculate_ciwa_ar, calculate_cows


class ModularCoreTests(unittest.TestCase):
    def test_all_declared_high_risk_modules_have_evidence_records(self):
        result = audit_evidence_coverage(ROOT)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['registered'], result['total_modules'])
        self.assertEqual(result['unregistered'], 0)

    def test_sourced_clinical_regressions_are_traceable(self):
        cases, errors = validate_clinical_cases(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(len(cases), 27)

    def test_published_image_cases_have_provenance_and_leakage_labels(self):
        cases, errors = validate_real_image_cases(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(len(cases), 4)

    def test_skill_does_not_claim_clinical_validation_from_regressions(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('prospective clinical and diagnostic-accuracy validation pending',
                      skill)
        self.assertIn('Do not describe the skill as clinically validated', skill)

    def test_sepsis_2026_timing_and_hemodynamic_gates(self):
        module = ' '.join(load(ROOT, 'sepsis-shock').split())
        for invariant in ('within 1 hour', 'within 3 hours', 'at least 30 mL/kg',
                          'vasopressor and fluid may need to start concurrently',
                          'MAP 65 mm Hg', '60--65 mm Hg'):
            self.assertIn(invariant, module)

    def test_high_risk_audit_corrections_are_preserved(self):
        status = ' '.join(load(ROOT, 'status-epilepticus').split())
        obstetric = ' '.join(load(ROOT, 'obstetric-emergencies').split())
        trauma = ' '.join(load(ROOT, 'trauma-major-hemorrhage').split())
        reversal = ' '.join(load(ROOT, 'anticoagulation-reversal').split())
        self.assertIn('lasting 5 minutes', status)
        self.assertIn('within 30--60 minutes', obstetric)
        self.assertIn('within 3 hours of injury', trauma)
        self.assertIn('PT/INR normal no excluye apixabán/rivaroxabán', reversal)

    def test_cardiovascular_safety_audit_is_preserved(self):
        arrhythmia = ' '.join(load(ROOT, 'arrhythmias-cardiac-arrest').split())
        hypertension = ' '.join(load(ROOT, 'hypertensive-emergencies').split())
        heart_failure = ' '.join(load(ROOT, 'acute-heart-failure').split())
        valve = ' '.join(load(ROOT, 'critical-valvular-disease').split())
        self.assertIn('irregular broad-complex rhythm', arrhythmia)
        self.assertIn('20--25% in the first hour', hypertension)
        self.assertIn('Do not use inotropes routinely', heart_failure)
        self.assertIn('Do not apply one valve strategy to another', valve)

    def test_v118_shock_aortic_and_tamponade_gates(self):
        shock = ' '.join(load(ROOT, 'cardiogenic-shock').split())
        aorta = ' '.join(load(ROOT, 'acute-aortic-syndrome').split())
        tamponade = ' '.join(load(
            ROOT, 'cardiac-tamponade-pericardial-emergency').split())
        for invariant in ('SCAI stage', '8 mg to a final volume of 100 mL = 80 micrograms/mL',
                          '250 mg/100 mL = 2,500 micrograms/mL',
                          'Do not give automatic large fluid boluses',
                          'temporary mechanical circulatory support reflexively'):
            self.assertIn(invariant, shock)
        for invariant in ('HR 60--80/min', 'SBP below 120 mm Hg',
                          '2 g to a final volume of 100 mL = 20 mg/mL',
                          'Never start a pure vasodilator before impulse control',
                          'immediate operative repair'):
            self.assertIn(invariant, aorta)
        for invariant in ('normal BP does not exclude compensated tamponade',
                          'definitive drainage immediately',
                          'Avoid nitrates, diuretics',
                          'Avoid sedation, induction and positive-pressure ventilation',
                          'do not perform routine complete pericardial drainage'):
            self.assertIn(invariant, tamponade)

    def test_v119_critical_respiratory_gates(self):
        asthma = ' '.join(load(ROOT, 'acute-severe-asthma').split())
        copd = ' '.join(load(ROOT, 'copd-exacerbation').split())
        hemoptysis = ' '.join(load(ROOT, 'life-threatening-hemoptysis').split())
        for invariant in ('normal or rising PaCO2',
                          '4--10 puffs of 100 micrograms',
                          'prednisolone/prednisone 40--50 mg',
                          'magnesium sulfate 2 g IV over 20 minutes',
                          'dynamic hyperinflation'):
            self.assertIn(invariant, asthma)
        for invariant in ('SpO2 88--92%',
                          'prednisone/prednisolone 40 mg PO once daily for 5 days',
                          'pH at most 7.35',
                          'HFNO may improve comfort/oxygenation but is not a substitute',
                          'Do not use methylxanthines routinely'):
            self.assertIn(invariant, copd)
        for invariant in ('not by a single volume threshold',
                          'bleeding lung dependent',
                          'at least 8.0--8.5 mm internal diameter',
                          'Do not default to a double-lumen tube',
                          'must never delay bronchoscopy, embolization or surgery'):
            self.assertIn(invariant, hemoptysis)

    def test_v120_neurovascular_and_spinal_emergency_gates(self):
        ich = ' '.join(load(ROOT, 'spontaneous-intracerebral-hemorrhage').split())
        cord = ' '.join(load(ROOT, 'acute-spinal-cord-compression').split())
        cauda = ' '.join(load(ROOT, 'cauda-equina-conus-emergency').split())
        for invariant in ('maintain 130--150 mm Hg',
                          'lowering below 130 mm Hg can be harmful',
                          '20 mg to a final volume of 100 mL = 0.2 mg/mL',
                          'Do not give platelet transfusion routinely',
                          'Do not use corticosteroids to treat elevated ICP'):
            self.assertIn(invariant, ich)
        for invariant in ('dexamethasone 16 mg', 'within 24 hours',
                          '75--80 mm Hg', '90--95 mm Hg', '3--7 days',
                          'Do not use high-dose methylprednisolone routinely'):
            self.assertIn(invariant, cord)
        for invariant in ('within 4 hours of the radiology request',
                          'PVR above 200 mL', 'does not exclude',
                          'Do not use a nominal 48-hour window',
                          'Do not give dexamethasone routinely'):
            self.assertIn(invariant, cauda)

    def test_v121_iv_antihypertensive_alternatives(self):
        selection = ' '.join(load(ROOT, 'iv-antihypertensive-selection').split())
        ich = ' '.join(load(ROOT, 'spontaneous-intracerebral-hemorrhage').split())
        obstetric = ' '.join(load(ROOT, 'obstetric-emergencies').split())
        for invariant in ('Nimodipine is not an alternative IV antihypertensive',
                          '200 mg/200 mL = 1 mg/mL',
                          '0.5 mg/min = 30 mL/h',
                          'ready-to-use 0.5 mg/mL',
                          '2 mg/h = 4 mL/h',
                          'Never start a pure vasodilator first',
                          '20 mg/100 mL or 40 mg/200 mL = 200 micrograms/mL'):
            self.assertIn(invariant, selection)
        self.assertIn('Nimodipine is not a substitute', ich)
        for invariant in ('usual algorithm maximum 220 mg',
                          'immediate-release nifedipine 10 mg PO',
                          'Never give nifedipine sublingually'):
            self.assertIn(invariant, obstetric)

    def test_v117_evidence_audit_corrections_are_preserved(self):
        sah = ' '.join(load(ROOT, 'headache-sah').split())
        meningitis = ' '.join(load(ROOT, 'cns-infection').split())
        endocarditis = ' '.join(load(ROOT, 'infective-endocarditis').split())
        pancreatitis = ' '.join(load(ROOT, 'pancreatitis').split())
        liver = ' '.join(load(ROOT, 'acute-liver-failure').split())
        withdrawal = ' '.join(load(ROOT, 'alcohol-withdrawal').split())
        rhabdo = ' '.join(load(ROOT, 'rhabdomyolysis').split())
        suicide = ' '.join(load(ROOT, 'suicide-risk').split())
        self.assertIn('not a generic treatment', sah)
        self.assertIn('never allow cultures, lumbar puncture or CT to delay', meningitis)
        self.assertIn('at least three appropriately collected blood-culture sets', endocarditis)
        self.assertIn('do not perform urgent ERCP routinely', pancreatitis)
        self.assertIn('transplant-capable liver center at first recognition', liver)
        self.assertIn('only when a reliable validated assessment', withdrawal)
        self.assertIn('Do not use bicarbonate, mannitol or loop diuretics routinely', rhabdo)
        self.assertIn('Do not use a risk scale', suicide)

    def test_every_manifest_module_resolves(self):
        manifest, errors = validate(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(len(manifest), 131)
        for module_id in manifest:
            self.assertIn(f"\n## {module_id}\n", load(ROOT, module_id))

    def test_loader_preserves_preamble_without_other_modules(self):
        # Synthetic bundle isolates the invariant independently of medical wording.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'references').mkdir()
            (root / 'modules').mkdir()
            (root / 'references/module-index.md').write_text(
                '| example-one | `modules/example.md` |\n', encoding='utf-8')
            (root / 'modules/example.md').write_text(
                '# Bundle\nShared safety instruction.\n\n## example-one\nFirst body.\n'
                '\n## example-two\nSecond body.\n', encoding='utf-8')
            result = load(root, 'example-one')
            self.assertIn('Shared safety instruction.', result)
            self.assertIn('First body.', result)
            self.assertNotIn('Second body.', result)

    def test_weight_alone_is_not_complete_context(self):
        result = validate_inputs(weight_kg=80, task='medication')
        for field in ('age', 'allergy', 'renal', 'hepatic', 'pregnancy', 'drug',
                      'indication', 'current_vitals', 'therapeutic_target', 'route'):
            self.assertIn(field, result['missing_high_value_context'])
        self.assertFalse(result['checklist_complete'])

    def test_medication_selection_module_preserves_indication_boundaries(self):
        module = load(ROOT, 'medication-selection-safety')
        self.assertIn('Nimodipine is disease-modifying', module)
        self.assertIn('not a general antihypertensive', module)
        self.assertIn('Nitrates are not default', module)
        self.assertIn('hold/stop condition', module)

    def test_continuous_infusions_require_bedside_ml_per_hour(self):
        module = load(ROOT, 'medication-selection-safety')
        module_flat = ' '.join(module.split())
        for invariant in ('100 mL or 200 mL', 'final concentration', 'mL/h',
                          'titration interval', 'hold/stop thresholds',
                          'do not invent it'):
            self.assertIn(invariant, module_flat)
        self.assertIn('Do not force bolus', module_flat)

    def test_norepinephrine_100_and_200_ml_preparations(self):
        result_100 = infusion_ml_h(8, 100, 0.1, 80)
        result_200 = infusion_ml_h(8, 200, 0.1, 80)
        self.assertAlmostEqual(result_100['ml_h'], 6.0)
        self.assertAlmostEqual(result_200['ml_h'], 12.0)

    def test_tension_pneumothorax_does_not_wait_for_imaging(self):
        module = load(ROOT, 'tension-pneumothorax')
        for invariant in ('relatively normal heart rate', 'do not wait for chest radiography',
                          'does not delay decompression', 'failure/rescue plan',
                          'definitive intercostal drainage'):
            self.assertIn(invariant, module)
        self.assertIn('massive PE', module)
        self.assertIn('tamponade', module)

    def test_tension_pneumothorax_case_routes_to_procedure_and_pocus(self):
        cases = __import__('json').loads(
            (ROOT / 'tests/test-cases.json').read_text(encoding='utf-8'))
        case = next(item for item in cases
                    if item['name'] == 'Bedside respiratory regression - tension pneumothorax')
        self.assertEqual(case['expected_priority_diagnosis'], 'tension-pneumothorax')
        self.assertEqual(set(case['expected_modules']),
                         {'tension-pneumothorax', 'pocus', 'emergency-procedures'})
        self.assertIn('do_not_delay_for_radiography', case['safety_invariants'])

    def test_brain_cross_sectional_imaging_has_mass_effect_safety_pass(self):
        module = load(ROOT, 'ct-mri-screenshot')
        for invariant in ('extra-axial spaces', 'basal cisterns', 'midline',
                          'mass effect', 'original available quality'):
            self.assertIn(invariant, module)
        self.assertIn('avoid excluding hemorrhage or mass effect', module)

    def test_intracranial_mass_effect_preserves_perfusion_and_uses_bolus_hts(self):
        module = load(ROOT, 'traumatic-intracranial-mass-effect')
        module_flat = ' '.join(module.split())
        for invariant in ('immediate neurosurgical emergency',
                          'bridge to definitive evacuation',
                          'not automatic upper BP targets',
                          '3% sodium chloride 5 mL/kg',
                          'over 5--20 minutes',
                          'not as a continuous infusion',
                          '5 mg/h = 50 mL/h'):
            self.assertIn(invariant, module_flat)
        self.assertIn('Do not apply the blood-pressure target for spontaneous', module_flat)

    def test_intracranial_mass_effect_case_routes_with_safety_invariants(self):
        cases = __import__('json').loads(
            (ROOT / 'tests/test-cases.json').read_text(encoding='utf-8'))
        case = next(item for item in cases
                    if item['name'] == 'Bedside neurologic regression - extra-axial mass effect')
        self.assertEqual(case['expected_priority_diagnosis'],
                         'traumatic-intracranial-mass-effect')
        self.assertIn('do_not_apply_spontaneous_ich_bp_target', case['safety_invariants'])
        self.assertIn('hypertonic_saline_is_weight_based_bolus', case['safety_invariants'])

    def test_critical_electrolyte_modules_preserve_key_safety_gates(self):
        sodium = ' '.join(load(ROOT, 'sodium-emergencies').split())
        potassium = ' '.join(load(ROOT, 'potassium-emergencies').split())
        calcium = ' '.join(load(ROOT, 'calcium-magnesium-emergencies').split())
        for invariant in ('150 mL sodium chloride 3%', '5 mmol/L initial rise',
                          '10 mmol/L in the first 24 hours', 'relowering strategy'):
            self.assertIn(invariant, sodium)
        for invariant in ('calcium gluconate 10% 30 mL',
                          'soluble insulin 10 units IV plus glucose 25 g',
                          '50 mL/h for 5 hours', 'Never IV-push potassium'):
            self.assertIn(invariant, potassium)
        self.assertIn('magnesium sulfate 2 g IV over 10--15 minutes', calcium)

    def test_hypernatremia_requires_serum_and_urine_diagnostics(self):
        sodium = ' '.join(load(ROOT, 'sodium-emergencies').split())
        for invariant in ('effective tonicity', 'osmolal gap', 'urine osmolality',
                          'urine sodium', 'urine potassium',
                          'electrolyte-free water clearance',
                          'not derivable from serum sodium alone'):
            self.assertIn(invariant, sodium)

    def test_sodium_water_balance_calculator(self):
        result = sodium_water_balance({
            'serum_na_mmol_l': 155,
            'glucose_mg_dl': 90,
            'bun_mg_dl': 28,
            'measured_serum_osmolality_mosm_kg': 330,
            'urine_osmolality_mosm_kg': 900,
            'urine_na_mmol_l': 10,
            'urine_k_mmol_l': 20,
            'urine_volume_ml_h': 100,
        })
        self.assertAlmostEqual(result['calculated_serum_osmolality_mosm_kg'], 325)
        self.assertAlmostEqual(result['effective_tonicity_mosm_kg'], 315)
        self.assertAlmostEqual(result['osmolal_gap_mosm_kg'], 5)
        self.assertAlmostEqual(result['electrolyte_free_water_clearance_ml_h'],
                               80.645161, places=5)
        self.assertEqual(result['urine_concentration_category'],
                         'concentrated_above_800')

    def test_aaa_sedation_and_rsi_have_rescue_pathways(self):
        aaa = ' '.join(load(ROOT, 'abdominal-aortic-aneurysm').split())
        sedation = ' '.join(load(ROOT, 'sedoanalgesia').split())
        rsi = ' '.join(load(ROOT, 'airway-rsi').split())
        for invariant in ('do not use POCUS to exclude rupture',
                          'permissive hypotension', 'urgent EVAR or open repair'):
            self.assertIn(invariant, aaa)
        for invariant in ('dedicated sedation clinician', 'continuous capnography',
                          'ketamine 1 mg/kg', 'propofol 0.5--1 mg/kg'):
            self.assertIn(invariant, sedation)
        for invariant in ('Plan A/B/C/D', 'first-pass success',
                          'rocuronium 1.2 mg/kg', 'continuous waveform capnography',
                          'Start analgesia/sedation immediately'):
            self.assertIn(invariant, rsi)

    def test_dka_hhs_module_preserves_modern_diagnostic_and_treatment_gates(self):
        module = ' '.join(load(ROOT, 'diabetic-ketoacidosis-hhs').split())
        for invariant in ('beta-hydroxybutyrate at least 3.0 mmol/L',
                          'glucose at least 600 mg/dL',
                          'delay insulin until potassium is above 3.5 mmol/L',
                          '100 units in a final volume of 100 mL',
                          '0.1 units/kg/h', '0.05 units/kg/h',
                          'osmolality fall of 3--8 mOsm/kg/h',
                          'prophylactic-dose low-molecular-weight heparin',
                          'do not escalate automatically to therapeutic anticoagulation',
                          'Do not use anion gap or urine ketones alone'):
            self.assertIn(invariant, module)

    def test_acid_base_calculator_detects_mixed_dka_physiology(self):
        result = acid_base_hyperglycemia({
            'ph': 7.10, 'pco2_mm_hg': 32, 'hco3_mmol_l': 10,
            'sodium_mmol_l': 135, 'chloride_mmol_l': 100,
            'albumin_g_dl': 2.0, 'glucose_mg_dl': 450,
            'bun_mg_dl': 28, 'beta_hydroxybutyrate_mmol_l': 5.0,
            'history_of_diabetes': True, 'weight_kg': 70,
        })
        self.assertAlmostEqual(result['anion_gap_mmol_l'], 25)
        self.assertAlmostEqual(result['albumin_corrected_anion_gap_mmol_l'], 30)
        self.assertAlmostEqual(result['delta_ratio'], 18 / 14)
        self.assertEqual(result['metabolic_acidosis_compensation'],
                         'additional_respiratory_acidosis')
        self.assertTrue(result['dka_criteria']['all_present'])
        self.assertAlmostEqual(result['effective_serum_osmolality_mosm_kg'], 295)
        self.assertAlmostEqual(
            result['insulin_infusion_reference']['dka_or_mixed_initial_ml_h'], 7)
        self.assertAlmostEqual(
            result['insulin_infusion_reference']['dka_after_glucose_below_250_ml_h'], 3.5)

    def test_hhs_calculator_uses_all_four_domains(self):
        result = acid_base_hyperglycemia({
            'ph': 7.36, 'pco2_mm_hg': 40, 'hco3_mmol_l': 22,
            'sodium_mmol_l': 150, 'chloride_mmol_l': 112,
            'glucose_mg_dl': 720, 'bun_mg_dl': 56,
            'beta_hydroxybutyrate_mmol_l': 1.0,
        })
        self.assertTrue(result['hhs_criteria']['all_present'])
        self.assertGreater(result['effective_serum_osmolality_mosm_kg'], 300)
        self.assertGreater(result['total_calculated_osmolality_mosm_kg'], 320)

    def test_hhs_accepts_low_urine_ketones_when_beta_hydroxybutyrate_missing(self):
        result = acid_base_hyperglycemia({
            'ph': 7.38, 'hco3_mmol_l': 23, 'sodium_mmol_l': 150,
            'chloride_mmol_l': 112, 'glucose_mg_dl': 720,
            'bun_mg_dl': 56, 'urine_ketones_plus': 1,
        })
        self.assertTrue(result['hhs_criteria']['all_present'])

    def test_blood_gas_image_requires_sample_and_oxygen_context(self):
        result = validate_inputs(task='clinical-image-interpretation', age=50,
            symptoms='disnea', onset='hoy', body_region='laboratory report',
            laterality='not_applicable', image_available=True,
            image_quality='adequate', modality='blood-gas',
            source_type='screen_photo', images_count=1)
        self.assertIn('sample_type', result['missing_high_value_context'])
        self.assertIn('oxygen_context', result['missing_high_value_context'])
        self.assertTrue(any('digit and unit' in warning for warning in result['warnings']))

    def test_blood_gas_image_module_blocks_unlabeled_arterial_claim(self):
        module = ' '.join(load(ROOT, 'blood-gas-image').split())
        for invariant in ('unlabeled blood gas', 'Do not interpret PO2 as arterial',
                          'visually verify every digit', 'Never silently repair',
                          'Henderson--Hasselbalch', 'PaO2/FiO2',
                          'does not by itself diagnose ARDS',
                          'near-normal pH'):
            self.assertIn(invariant, module)

    def test_blood_gas_oxygenation_calculations_are_explicit_and_guarded(self):
        result = acid_base_hyperglycemia({
            'ph': 7.383, 'pco2_mm_hg': 36.5, 'pao2_mm_hg': 57.8,
            'fio2_fraction': 0.80, 'atmospheric_pressure_mm_hg': 760,
            'hco3_mmol_l': 21.3, 'sodium_mmol_l': 141,
            'chloride_mmol_l': 108.6,
        })
        self.assertAlmostEqual(result['pao2_fio2_ratio_mm_hg'], 72.25)
        self.assertAlmostEqual(
            result['alveolar_o2_equation']['calculated_alveolar_o2_mm_hg'],
            524.775)
        self.assertAlmostEqual(
            result['alveolar_o2_equation']['a_a_gradient_mm_hg'], 466.975)
        self.assertIn('do not diagnose ARDS', result['oxygenation_safety'])

        with self.assertRaisesRegex(ValueError, 'fio2_fraction'):
            acid_base_hyperglycemia({'pao2_mm_hg': 80, 'fio2_fraction': 80})

    def test_emergency_oxygen_module_separates_flow_from_fio2(self):
        module = ' '.join(load(ROOT, 'oxygen-therapy-emergency').split())
        for invariant in ('94--98%', '88--92%', 'Never run below 5 L/min',
                          '15 L/min initially', 'never prescribe by colour alone',
                          '0.21 to 1.0', 'do not delay intubation',
                          'Flow in L/min is not interchangeable with FiO2',
                          'must not be used as an exact denominator for P/F'):
            self.assertIn(invariant, module)

    def test_rox_calculator_preserves_context_and_trend(self):
        result = respiratory_support({'observations': [
            {'hours': 2, 'spo2_percent': 92, 'fio2_fraction': 0.80,
             'respiratory_rate_min': 40},
            {'hours': 6, 'spo2_percent': 95, 'fio2_fraction': 0.60,
             'respiratory_rate_min': 28},
        ]})
        self.assertAlmostEqual(result['observations'][0]['rox'], 2.875)
        self.assertEqual(result['observations'][0][
            'original_pneumonia_cohort_zone'],
            'indeterminate_zone_requires_close_reassessment')
        self.assertGreater(result['observations'][1]['rox'], 4.88)
        self.assertEqual(result['trend']['direction'], 'rising')
        self.assertIn('must not delay intubation', result['safety'])

    def test_rox_calculator_rejects_percent_fio2(self):
        with self.assertRaisesRegex(ValueError, 'fio2_fraction'):
            respiratory_support({'observations': [
                {'hours': 2, 'spo2_percent': 92, 'fio2_fraction': 80,
                 'respiratory_rate_min': 30}
            ]})

    def test_hfno_and_niv_modules_have_failure_gates(self):
        hfno = ' '.join(load(ROOT, 'high-flow-nasal-oxygen').split())
        niv = ' '.join(load(ROOT, 'noninvasive-ventilation').split())
        for invariant in ('ROX = (SpO2 / FiO2) / respiratory rate',
                          'context-limited signals', 'below 2.85 at 2 hours',
                          'must never overrule', 'named escalation plan'):
            self.assertIn(invariant, hfno)
        for invariant in ('pH at most 7.35', 'IPAP 10--15 and EPAP 4',
                          'backup rate 12--16/min', '88--92%',
                          'Repeat gas approximately 1 hour',
                          'pH below 7.25', 'no single number'):
            self.assertIn(invariant, niv)

    def test_unknown_allergy_is_not_a_negative_history(self):
        result = validate_inputs(task='medication', allergy='desconocida')
        self.assertIn('allergy', result['missing_high_value_context'])

    def test_negative_history_is_not_missing(self):
        result = validate_inputs(task='medication', pregnancy=False, allergy=False)
        self.assertNotIn('pregnancy', result['missing_high_value_context'])
        self.assertNotIn('allergy', result['missing_high_value_context'])

    def test_invalid_numeric_values(self):
        for value in (-1, float('nan'), float('inf'), True, '80'):
            with self.subTest(value=value):
                self.assertIn('weight_kg', validate_inputs(
                    task='medication', weight_kg=value)['invalid_values'])

    def test_newborn_age_zero_is_valid(self):
        self.assertNotIn('age', validate_inputs(age=0)['invalid_values'])

    def test_warfarin_requires_inr_and_product(self):
        result = validate_inputs(task='anticoagulation-reversal', anticoagulant='warfarina')
        for field in ('inr', 'last_dose', 'reversal_product', 'hit_history'):
            self.assertIn(field, result['missing_high_value_context'])

    def test_doac_does_not_use_inr_as_clearance(self):
        result = validate_inputs(task='anticoagulation-reversal', anticoagulant='apixaban', inr=1)
        self.assertIn('last_dose', result['missing_high_value_context'])
        self.assertFalse(result['clinical_clearance'])

    def test_missing_image_warns_without_requiring_weight(self):
        result = validate_inputs(task='clinical-image-interpretation', image_available=False)
        self.assertTrue(result['warnings'])
        self.assertNotIn('weight_kg', result['missing_high_value_context'])

    def test_poor_image_warns(self):
        result = validate_inputs(task='clinical-image-interpretation', image_available=True,
                                 image_quality='non-diagnostic')
        self.assertTrue(result['warnings'])
        self.assertFalse(result['checklist_complete'])

    def test_complete_image_context_is_not_diagnostic_clearance(self):
        result = validate_inputs(task='clinical-image-interpretation', age=42,
            symptoms='dolor', onset='ayer', body_region='rodilla', laterality='derecha',
            image_available=True, image_quality='adequate', modality='xray',
            source_type='original_export', images_count=2, views='AP y lateral',
            laterality_marker='R')
        self.assertTrue(result['checklist_complete'])
        self.assertFalse(result['clinical_clearance'])

    def test_xray_context_requires_views_and_marker(self):
        result = validate_inputs(task='clinical-image-interpretation', age=42,
            symptoms='dolor', onset='ayer', body_region='tobillo', laterality='derecha',
            image_available=True, image_quality='adequate', modality='xray',
            source_type='screen_photo', images_count=1)
        self.assertIn('views', result['missing_high_value_context'])
        self.assertIn('laterality_marker', result['missing_high_value_context'])

    def test_image_count_must_be_positive_integer(self):
        for value in (0, -1, 1.5, True, '1'):
            with self.subTest(value=value):
                result = validate_inputs(task='clinical-image-interpretation',
                    images_count=value)
                self.assertIn('images_count', result['invalid_values'])

    def test_ultrasound_requires_dynamic_scope_statement(self):
        result = validate_inputs(task='clinical-image-interpretation', age=42,
            symptoms='disnea', onset='hoy', body_region='torax', laterality='bilateral',
            image_available=True, image_quality='adequate', modality='pocus',
            source_type='original_export', images_count=1)
        self.assertTrue(any('still, cine' in warning for warning in result['warnings']))

    def test_image_output_schema_is_valid_json_with_core_fields(self):
        schema = __import__('json').loads(
            (ROOT / 'references/image-output-schema.json').read_text(encoding='utf-8'))
        required = set(schema['required'])
        self.assertTrue({'image_access', 'quality', 'observed_findings',
                         'leading_impression', 'confidence', 'urgency',
                         'next_actions'}.issubset(required))

    def test_synthetic_image_evaluator_metrics_and_denominators(self):
        data = __import__('json').loads(
            (ROOT / 'tests/image-evaluation-example.json').read_text(encoding='utf-8'))
        result = evaluate(data)
        self.assertEqual(result['counts']['usable_cases'], 2)
        self.assertEqual(result['counts']['excluded_cases'], 1)
        self.assertEqual(result['metrics']['leading_diagnosis_accuracy']['value'], 1.0)
        self.assertEqual(result['metrics']['critical_finding_sensitivity']['denominator'], 1)
        self.assertEqual(result['metrics']['appropriate_abstention_rate']['value'], 1.0)

    def test_image_evaluator_does_not_hide_false_reassurance_or_undertriage(self):
        data = {'cases': [{'id': 'synthetic-miss',
            'reference': {'accepted_diagnoses': ['fractura'], 'diagnostic_quality': 'adequate',
                          'abnormal': True, 'critical': True, 'urgency': 'emergent'},
            'prediction': {'leading_diagnosis': 'normal', 'differential': [],
                           'abstained': False, 'critical_flag': False,
                           'normal_claim': True, 'urgency': 'routine'}}]}
        result = evaluate(data)
        self.assertEqual(result['metrics']['critical_finding_sensitivity']['value'], 0.0)
        self.assertEqual(result['metrics']['false_reassurance_rate']['value'], 1.0)
        self.assertEqual(result['metrics']['undertriage_rate']['value'], 1.0)

    def test_unblinded_or_annotated_real_cases_are_excluded_from_accuracy_metrics(self):
        data = __import__('json').loads(
            (ROOT / 'tests/real-image-cases.json').read_text(encoding='utf-8'))
        result = evaluate(data)
        self.assertEqual(result['counts']['usable_cases'], 0)
        self.assertEqual(result['counts']['teaching_only_cases'], 4)
        self.assertIsNone(result['metrics']['leading_diagnosis_accuracy']['value'])
        self.assertEqual(result['case_results'], [])

    def test_unknown_task_fails(self):
        with self.assertRaises(ValueError):
            validate_inputs(task='misspelled')

    def test_unknown_module_fails_explicitly(self):
        with self.assertRaisesRegex(KeyError, "unknown module"):
            load(ROOT, "not-a-module")

    def test_validated_norepinephrine_calculation(self):
        result = infusion_ml_h(8, 100, 0.1, 80)
        self.assertAlmostEqual(result["ml_h"], 6.0)

    def test_weight_dose_cap(self):
        self.assertEqual(weight_based_dose(90, 1.5, 100), 100)


    def test_v135_vasoactive_worked_examples_70kg(self):
        # Each assertion reproduces a worked mL/h example in vasoactive-inotrope-infusions.
        module = ' '.join(load(ROOT, 'vasoactive-inotrope-infusions').split())
        # Norepinephrine 8 mg/200 mL = 40 mcg/mL; 8 mg/100 mL = 80 mcg/mL
        self.assertAlmostEqual(infusion_ml_h(8, 200, 0.05, 70)['concentration_mcg_ml'], 40)
        self.assertAlmostEqual(infusion_ml_h(8, 200, 0.05, 70)['ml_h'], 5.25)
        self.assertAlmostEqual(infusion_ml_h(8, 100, 0.05, 70)['ml_h'], 2.625)
        self.assertAlmostEqual(infusion_ml_h(8, 200, 0.1, 70)['ml_h'], 10.5)
        for text in ('210 / 40 = 5.25 mL/h', '10.5 mL/h at 40 micrograms/mL'):
            self.assertIn(text, module)
        # Vasopressin 100 units/100 mL = 1 unit/mL; 50 units/500 mL = 0.1 unit/mL
        self.assertAlmostEqual(fixed_dose_ml_h(0.03 * 60, 1.0), 1.8)
        self.assertAlmostEqual(fixed_dose_ml_h(0.01 * 60, 1.0), 0.6)
        self.assertAlmostEqual(fixed_dose_ml_h(0.005 * 60, 1.0), 0.3)
        self.assertAlmostEqual(fixed_dose_ml_h(0.07 * 60, 1.0), 4.2)
        self.assertAlmostEqual(fixed_dose_ml_h(0.03 * 60, 50 / 500), 18.0)
        self.assertIn('1.8 units/h = 1.8 mL/h', module)
        # Epinephrine 4 mg/100 mL = 40 mcg/mL
        self.assertAlmostEqual(infusion_ml_h(4, 100, 0.05, 70)['ml_h'], 5.25)
        # Dopamine 400 mg/250 mL = 1,600 mcg/mL
        self.assertAlmostEqual(infusion_ml_h(400, 250, 5, 70)['ml_h'], 13.125)
        self.assertIn('21,000 / 1,600 = 13.1 mL/h', module)
        # Dobutamine 250 mg/100 mL and 250 mg/200 mL
        self.assertAlmostEqual(infusion_ml_h(250, 100, 2.5, 70)['ml_h'], 4.2)
        self.assertAlmostEqual(infusion_ml_h(250, 200, 2.5, 70)['ml_h'], 8.4)
        # Milrinone 20 mg/100 mL = 200 mcg/mL; load 50 mcg/kg = 17.5 mL
        self.assertAlmostEqual(infusion_ml_h(20, 100, 0.375, 70)['ml_h'], 7.875)
        self.assertAlmostEqual(50 * 70 / 200, 17.5)
        self.assertIn('1,575 / 200 = 7.9 mL/h', module)
        # Levosimendan 12.5 mg/500 mL = 25 mcg/mL
        self.assertAlmostEqual(infusion_ml_h(12.5, 500, 0.1, 70)['ml_h'], 16.8)
        self.assertAlmostEqual((6 * 70 / 25) * 6, 100.8)  # 16.8 mL over 10 min
        # Phenylephrine 10 mg/500 mL = 20 mcg/mL; 20 mcg/min
        self.assertAlmostEqual(fixed_dose_ml_h(20 * 60, 20), 60.0)
        # Angiotensin II 2.5 mg/250 mL = 10,000 ng/mL; 20 ng/kg/min = 0.02 mcg/kg/min
        self.assertAlmostEqual(infusion_ml_h(2.5, 250, 0.02, 70)['ml_h'], 8.4)
        self.assertIn('84,000 / 10,000 = 8.4 mL/h', module)

    def test_v135_vasoactive_positions_and_safety_gates(self):
        module = ' '.join(load(ROOT, 'vasoactive-inotrope-infusions').split())
        for invariant in ('not first-line in septic shock',
                          'Do not use low-dose dopamine as renal protection',
                          'starting vasopressors peripherally',
                          'at or proximal to the antecubital fossa',
                          'phentolamine 5--10 mg',
                          'never infer a base/salt conversion',
                          'suggests against it in septic shock',
                          'VTE prophylaxis', 'Pediatric infusions are out of scope',
                          'does not replace those pathways'):
            self.assertIn(invariant, module)

    def test_v135_icu_sedation_worked_examples_70kg(self):
        module = ' '.join(load(ROOT, 'icu-sedation-analgesia-infusions').split())
        # Propofol 10 mg/mL undiluted (1,000 mg/100 mL)
        self.assertAlmostEqual(infusion_ml_h(1000, 100, 5, 70)['ml_h'], 2.1)
        self.assertAlmostEqual(infusion_ml_h(1000, 100, 25, 70)['ml_h'], 10.5)
        self.assertAlmostEqual(infusion_ml_h(1000, 100, 50, 70)['ml_h'], 21.0)
        self.assertAlmostEqual(weight_per_hour_ml_h(4, 70, 10), 28.0)
        # Dexmedetomidine 400 mcg/100 mL = 4 mcg/mL
        self.assertAlmostEqual(weight_per_hour_ml_h(0.7, 70, 4), 12.25)
        self.assertAlmostEqual(infusion_ml_h(0.4, 100, 0.7 / 60, 70)['ml_h'], 12.25)
        self.assertAlmostEqual(weight_per_hour_ml_h(0.2, 70, 4), 3.5)
        self.assertAlmostEqual(weight_per_hour_ml_h(1.4, 70, 4), 24.5)
        # Midazolam 100 mg/100 mL = 1 mg/mL
        self.assertAlmostEqual(weight_per_hour_ml_h(0.03, 70, 1), 2.1)
        self.assertAlmostEqual(weight_per_hour_ml_h(0.1, 70, 1), 7.0)
        self.assertAlmostEqual(weight_per_hour_ml_h(0.2, 70, 1), 14.0)
        # Fentanyl 1,000 mcg/100 mL = 10 mcg/mL
        self.assertAlmostEqual(weight_per_hour_ml_h(0.7, 70, 10), 4.9)
        self.assertAlmostEqual(weight_per_hour_ml_h(1.5, 70, 10), 10.5)
        # Remifentanil 5 mg/100 mL = 50 mcg/mL
        self.assertAlmostEqual(infusion_ml_h(5, 100, 0.1, 70)['ml_h'], 8.4)
        self.assertAlmostEqual(infusion_ml_h(5, 100, 0.025, 70)['ml_h'], 2.1)
        # Ketamine 100 mg/100 mL = 1 mg/mL
        self.assertAlmostEqual(infusion_ml_h(100, 100, 1, 70)['ml_h'], 4.2)
        self.assertAlmostEqual(infusion_ml_h(100, 100, 2, 70)['ml_h'], 8.4)
        # Morphine 1 mg/mL and hydromorphone 0.1 mg/mL (fixed mg/h)
        self.assertAlmostEqual(fixed_dose_ml_h(2, 1), 2.0)
        self.assertAlmostEqual(fixed_dose_ml_h(0.5, 0.1), 5.0)
        for text in ('21 / 10 = 2.1 mL/h', '49 / 4 = 12.25 mL/h', '49 / 10 = 4.9 mL/h',
                     '420 / 50 = 8.4 mL/h', '4.2 mg/h = 4.2 mL/h', '2.1 mg/h = 2.1 mL/h'):
            self.assertIn(text, module)

    def test_v135_icu_sedation_safety_gates(self):
        module = ' '.join(load(ROOT, 'icu-sedation-analgesia-infusions').split())
        for invariant in ('Analgesia first', 'CPOT or BPS', 'RASS -2 to +1',
                          'propofol or dexmedetomidine over benzodiazepines',
                          'dexmedetomidine over propofol', 'PRIS',
                          'a loading dose is not recommended',
                          'aged 65 years or younger', 'Procedural sedation remains in `sedoanalgesia`'):
            self.assertIn(invariant, module)
        procedural = load(ROOT, 'sedoanalgesia')
        self.assertIn('icu-sedation-analgesia-infusions', procedural)
        self.assertIn('ketamine 1 mg/kg IV over 30--60 seconds', ' '.join(procedural.split()))


    def test_v136_adult_resuscitation_2025_operational_details(self):
        tachy = ' '.join(load(ROOT, 'adult-arrhythmias').split())
        arrest = ' '.join(load(ROOT, 'adult-cardiac-arrest').split())
        for invariant in (
            '70--120 J initially',
            '120--150 J initially',
            'atropine 500 micrograms IV',
            'maximum of 3 mg',
            'isoprenaline starting at 5 micrograms/min',
            'adrenaline 2--10 micrograms/min',
            'high-degree AV block with a wide QRS',
            'transvenous pacing'
        ):
            self.assertIn(invariant, tachy)
        for invariant in (
            'first shock should be at least 150 J',
            '130--150 J',
            'non-shockable arrest: 1 mg IV as soon as possible',
            'shockable VF/pVT: 1 mg after the third shock',
            'Repeat 1 mg every 3--5 min',
            '300 mg IV after a total of three shocks',
            '150 mg IV after a total of five shocks',
            'within two attempts'
        ):
            self.assertIn(invariant, arrest)


    def test_v136_qa_layer_is_present_and_fail_closed(self):
        qa_root = ROOT / 'qa'
        for name in ('QA_POLICY.md', 'QA_MATRIX.md', 'RELEASE_GATES.md',
                     'HIGH_RISK_MODULES.md', 'localization-portugal-azores.json',
                     'qa_runner.py', 'HUMAN_REVIEW_TEMPLATE.md'):
            self.assertTrue((qa_root / name).is_file(), name)
        policy = (qa_root / 'QA_POLICY.md').read_text(encoding='utf-8')
        gates = (qa_root / 'RELEASE_GATES.md').read_text(encoding='utf-8')
        runner = (qa_root / 'qa_runner.py').read_text(encoding='utf-8')
        self.assertIn('High-risk changes require human review', policy)
        self.assertIn('must never auto-promote', gates)
        self.assertIn('Automated QA PASS is not clinical validation', runner)


    def test_v136_pediatric_resuscitation_2025_operational_details(self):
        shock = ' '.join(load(ROOT, 'pediatric-shock').split())
        rhythm = ' '.join(load(ROOT, 'pediatric-arrhythmias').split())
        arrest = ' '.join(load(ROOT, 'pediatric-cardiac-arrest').split())
        for invariant in (
            '10 mL/kg', '40--60 mL/kg in the first hour',
            '5 mL/kg', '3--4 boluses (30--40 mL/kg)',
            'noradrenaline as first-line vasopressor',
            'adrenaline as first-line inotrope',
            'max 20 mL/kg'
        ):
            self.assertIn(invariant, shock)
        for invariant in (
            'HR **<60/min despite adequate respiratory support**',
            '1--2 micrograms/kg IV',
            '20 micrograms/kg IV',
            '0.1--0.2 mg/kg IV',
            '0.3 mg/kg IV',
            '1 J/kg',
            '4 J/kg',
            'amiodarone 5 mg/kg',
            '25--50 mg/kg IV'
        ):
            self.assertIn(invariant, rhythm)
        for invariant in (
            '10 micrograms/kg IV/IO (max 1 mg) as soon as possible',
            'every 4 min',
            'single shock **4 J/kg**',
            '8 J/kg (max 360 J)',
            'amiodarone **5 mg/kg (max 300 mg)**',
            'amiodarone **5 mg/kg (max 150 mg)**',
            'Lidocaine **1 mg/kg IV**'
        ):
            self.assertIn(invariant, arrest)


    def test_v136_pediatric_sepsis_vasoactive_uncertainty_is_explicit(self):
        shock = ' '.join(load(ROOT, 'pediatric-shock').split())
        self.assertIn('SSC 2026 found insufficient evidence', shock)
        self.assertIn('epinephrine versus norepinephrine', shock)
        self.assertIn('do not present one universal septic-shock catecholamine as mandatory', shock)


    def test_v136_pulmonary_embolism_consolidation(self):
        pe = ' '.join(load(ROOT, 'pulmonary-embolism').split())
        for invariant in (
            '2019 ESC/ERS acute PE guideline',
            '2025 ACVC Clinical Decision-Making Toolkit',
            'routine full-dose systemic thrombolysis is not recommended',
            'alteplase **100 mg IV over 2 h**',
            '0.6 mg/kg over 15 min (max 50 mg)',
            '80 IU/kg bolus then 18 IU/kg/h',
            '1 mg/kg SC BID',
            '15 mg BID for 3 weeks then 20 mg daily',
            '10 mg BID for 7 days then 5 mg BID',
            'PRAGUE-26'
        ):
            self.assertIn(invariant, pe)

    def test_v136_anticoagulation_reversal_consolidation(self):
        rev = ' '.join(load(ROOT, 'anticoagulation-reversal').split())
        for invariant in (
            'anti-Xa calibrado específico',
            'idarucizumab 5 g IV',
            '400 mg IV',
            '4 mg/min durante 120 min',
            '800 mg IV',
            '8 mg/min durante 120 min',
            '25–50 IU/kg',
            '2,000 IU',
            'vitamina K1 10 mg IV',
            'PT/INR normal no excluye apixabán/rivaroxabán'
        ):
            self.assertIn(invariant, rev)


    def test_v136_empiric_antibiotic_stewardship_gates(self):
        abx = ' '.join(load(ROOT, 'empiric-antibiotics').split())
        for invariant in (
            'within 1 hour',
            'within 3 hours',
            'MDR coverage',
            'routine empirical antifungal therapy',
            'within **6 hours**',
            'third- or fourth-generation cephalosporin',
            '>=90% susceptibility in septic shock',
            '>=80% in sepsis without shock',
            'current antibiogram'
        ):
            self.assertIn(invariant, abx)

    def test_v136_status_epilepticus_operational_doses(self):
        se = ' '.join(load(ROOT, 'status-epilepticus').split())
        for invariant in (
            '>=5 minutes',
            '0.1 mg/kg IV (max 4 mg)',
            '0.15--0.2 mg/kg IV (max 10 mg)',
            '0.2 mg/kg (max 10 mg when >40 kg)',
            '60 mg/kg IV, max 4,500 mg',
            '20 mg PE/kg IV, max 1,500 mg PE',
            '40 mg/kg IV, max 3,000 mg',
            'non-convulsive status',
            'continuous EEG'
        ):
            self.assertIn(invariant, se)


    def test_v136_sodium_emergency_consolidation(self):
        sodium = ' '.join(load(ROOT, 'sodium-emergencies').split())
        for invariant in (
            '150 mL sodium chloride 3% IV over 20 min',
            '5 mmol/L initial rise',
            'greater than 10 mmol/L in the first 24 hours',
            'greater than 8 mmol/L in each subsequent 24 hours',
            'relowering',
            'electrolyte-free water'
        ):
            self.assertIn(invariant, sodium)

    def test_v136_obstetric_emergency_consolidation(self):
        obs = ' '.join(load(ROOT, 'obstetric-emergencies').split())
        for invariant in (
            'SBP >=160 mm Hg',
            'DBP >=110 mm Hg',
            '15 min',
            '30--60 minutes',
            '4--6 g IV loading',
            '1--2 g/h',
            'calcium gluconate 1 g IV',
            'Never give nifedipine sublingually'
        ):
            self.assertIn(invariant, obs)

    def test_v136_toxicology_framework_consolidation(self):
        tox = ' '.join(load(ROOT, 'toxicology').split())
        for invariant in (
            'Carbón activado no rutinario',
            'sobre todo precozmente',
            'vía aérea segura',
            'soporte ventilatorio primero',
            'Naloxona',
            'reanimación prolongada',
            'centro toxicológico',
            'no existe antídoto'
        ):
            self.assertIn(invariant, tox)

    def test_v136_anaphylaxis_2025_operational_details(self):
        a = ' '.join(load(ROOT, 'anaphylaxis').split())
        for invariant in (
            '1 mg/mL (1:1000)',
            '500 micrograms IM (0.5 mL)',
            'Repeat after **5 min**',
            '6--12 y **300 micrograms**',
            '6 months--6 y **150 micrograms**',
            '500--1000 mL',
            '10 mL/kg',
            '2 appropriate IM adrenaline doses',
            'low-dose IV adrenaline infusion'
        ):
            self.assertIn(invariant, a)


    def test_v136_calcium_magnesium_consolidation(self):
        cm = ' '.join(load(ROOT, 'calcium-magnesium-emergencies').split())
        for invariant in (
            '10--20 mL of 10% calcium gluconate IV',
            '50--100 mL',
            '10 mL 10% calcium chloride ≈ 6.8 mmol Ca2+',
            '10 mL 10% calcium gluconate ≈ 2.26 mmol Ca2+',
            'magnesium sulfate 2 g IV over 10--15 minutes',
            '10--15 min',
            'not routine calcium-lowering therapy',
            'compatibility/stability'
        ):
            self.assertIn(invariant, cm)


    def test_v136_trauma_major_hemorrhage_portugal_reconciliation(self):
        trauma = ' '.join(load(ROOT, 'trauma-major-hemorrhage').split())
        for invariant in (
            'updated **18/07/2017**',
            'do not hard-code the older DGS pack',
            'FFP:pRBC ratio of at least **1:2**',
            '1 g IV over 10 min, followed by 1 g IV over 8 h',
            '<=1.5 g/L',
            '3--4 g fibrinogen concentrate',
            '1.1--1.3 mmol/L',
            '>50 x 10^9/L',
            '>100 x 10^9/L',
            'do **not** use recombinant activated factor VII as first-line therapy',
            'Local release gate (Portugal/Azores/Horta)'
        ):
            self.assertIn(invariant, trauma)


    def test_v136_horta_tbi_local_protocol_reconciliation(self):
        tbi = ' '.join(load(ROOT, 'traumatic-intracranial-mass-effect').split())
        for invariant in (
            'Hospital da Horta local pathway',
            'SpO2 <94% or PaO2 <60 mmHg',
            'SBP <90 mmHg',
            'GCS <=8',
            'observe in ED >=6 h',
            'GCS 15 with >=1 local intracranial-injury risk factor',
            'ED surveillance for >=12 h',
            'GCS 9--12',
            'fall of >=2 GCS points',
            'more CT-intensive',
            'SBP >=100 mmHg',
            '>=110 mmHg',
            'ICP >22 mmHg'
        ):
            self.assertIn(invariant, tbi)


    def test_v136_respiratory_support_consolidation(self):
        arf = ' '.join(load(ROOT, 'acute-respiratory-failure').split())
        niv = ' '.join(load(ROOT, 'noninvasive-ventilation').split())
        for invariant in (
            'oxygenation failure, ventilation failure, or both',
            'conditionally favors HFNO over NIV',
            'P/F ratio <=200 mmHg',
            'Do not use noninvasive support as a delaying maneuver'
        ):
            self.assertIn(invariant, arf)
        for invariant in (
            'pH <=7.35',
            'conditionally favors HFNO over NIV',
            'IPAP 10--15 cmH2O and EPAP 4 cmH2O',
            '5--10 cmH2O',
            '88--92%',
            '1 hour',
            'pH <7.25 despite optimized NIV'
        ):
            self.assertIn(invariant, niv)


    def test_v136_medication_selection_safety_gates(self):
        med = ' '.join(load(ROOT, 'medication-selection-safety').split())
        for invariant in (
            'High-alert medication gate',
            'Unit/concentration safety',
            'never silently convert',
            'leading zero',
            'never a trailing zero',
            'base, salt, equivalent drug amount or units',
            'Independent verification for high-risk infusions',
            'mL/h = dose (mcg/kg/min) × weight (kg) × 60 ÷ concentration (mcg/mL)',
            'Look-alike/sound-alike',
            'Medication reconciliation'
        ):
            self.assertIn(invariant, med)

    def test_v136_pediatric_status_epilepticus_hse_2025(self):
        p = ' '.join(load(ROOT, 'pediatric-status-epilepticus').split())
        for invariant in (
            '<2.6 mmol/L',
            '10% glucose 3 mL/kg',
            '10 min',
            '2 total doses',
            '0.3 mg/kg',
            '0.1 mg/kg (max 4 mg)',
            '0.5 mg/kg (max 20 mg)',
            '40 mg/kg (max 3 g)',
            '50 mg/mL',
            '5 min',
            '20 mg/kg (max 2 g)',
            '20 mg/kg (max 1 g)',
            'lacosamide **10 mg/kg**',
            '20 mg/kg IV (max 3 g)',
            '1 month--18 years'
        ):
            self.assertIn(invariant, p)


    def test_v136_portugal_formulary_reference_does_not_claim_local_stock(self):
        p = ROOT / 'qa' / 'localization-portugal-azores.json'
        data = json.loads(p.read_text(encoding='utf-8'))
        items = {x['drug']: x for x in data['items']}
        expected = {
            'norepinephrine': '1 mg/mL',
            'epinephrine': '1 mg/mL',
            'dopamine': '40 mg/mL',
            'dobutamine': '12.5 mg/mL',
            'amiodarone': '50 mg/mL',
            'isoprenaline': '1 mg/mL'
        }
        for drug, strength in expected.items():
            self.assertIn(strength, items[drug]['product_strength'])
            self.assertEqual(items[drug]['status'], 'portugal_reference_found_local_pending')
            self.assertIn('local Horta stock/RCM not verified', items[drug]['source'])
        self.assertEqual(items['vasopressin']['status'], 'portugal_public_reference_insufficient_local_pending')
        self.assertNotEqual(items['norepinephrine']['status'], 'verified')


    def test_v136_portugal_sedation_formulary_references_do_not_claim_local_stock(self):
        p = ROOT / 'qa' / 'localization-portugal-azores.json'
        data = json.loads(p.read_text(encoding='utf-8'))
        items = {x['drug']: x for x in data['items']}
        expected = {
            'propofol': '10 mg/mL',
            'dexmedetomidine': '100 micrograms/mL',
            'midazolam': '5 mg/mL',
            'remifentanil': '1 mg, 2 mg and 5 mg'
        }
        for drug, strength in expected.items():
            self.assertIn(strength, items[drug]['product_strength'])
            self.assertEqual(items[drug]['status'], 'portugal_reference_found_local_pending')
            self.assertIn('local Horta stock/RCM not verified', items[drug]['source'])
        self.assertEqual(items['fentanyl']['status'], 'portugal_public_reference_insufficient_local_pending')
        self.assertNotEqual(items['propofol']['status'], 'verified')


    def test_v136_horta_formulary_verification_gate_exists(self):
        p = ROOT / 'qa' / 'HORTA_FORMULARY_VERIFICATION.md'
        text = p.read_text(encoding='utf-8')
        for invariant in (
            'No marcar un fármaco como `verified`',
            'Nº de registro / RCM',
            'Concentración final estándar',
            'Farmacéutico revisor',
            'Médico revisor',
            'La promoción local **no cambia automáticamente**'
        ):
            self.assertIn(invariant, text)


    def test_v136_pediatric_emergency_medication_module_is_routable(self):
        module = ' '.join(load(ROOT, 'pediatric-emergency-medications').split())
        for invariant in (
            '10 micrograms/kg IV/IO, max 1 mg',
            '5 mg/kg, max 300 mg after the 3rd shock',
            '5 mg/kg, max 150 mg after the 5th shock',
            '10 mL/kg',
            '5 mL/kg',
            'no more than 20 mL/kg',
            '15--20 mg/kg IV, max 1 g over 10 min',
            '2 mg/kg/h, max 1 g',
            '100 mL/kg/day for the first 10 kg',
            '50 mL/kg/day for the next 10 kg',
            '20 mL/kg/day for each kg above 20 kg',
            '2 mL/kg of 10% glucose',
            '10% glucose 3 mL/kg'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_calculator_weight_caps_and_volume(self):
        dose = pediatric_weight_based_total(10, 20, max_dose=1000)
        self.assertAlmostEqual(dose['total_dose'], 200.0)
        self.assertFalse(dose['capped'])
        self.assertAlmostEqual(pediatric_volume_for_dose(200, 100), 2.0)
        capped = pediatric_weight_based_total(10, 150, max_dose=1000)
        self.assertAlmostEqual(capped['total_dose'], 1000.0)
        self.assertTrue(capped['capped'])

    def test_v136_pediatric_calculator_infusions_and_fluids(self):
        self.assertAlmostEqual(pediatric_infusion_per_kg_min_ml_h(0.1, 20, 20), 6.0)
        self.assertAlmostEqual(pediatric_fluid_bolus_ml(20, 10), 200.0)
        self.assertAlmostEqual(pediatric_maintenance_ml_day(25), 1600.0)
        self.assertAlmostEqual(pediatric_maintenance_ml_h(25), 1600.0 / 24.0)
        self.assertAlmostEqual(pediatric_gastroenteritis_deficit_ml(20, False), 1000.0)
        self.assertAlmostEqual(pediatric_gastroenteritis_deficit_ml(20, True), 2000.0)

    def test_v136_pediatric_calculator_fails_closed_on_invalid_inputs(self):
        for fn, args in (
            (pediatric_weight_based_total, (10, 0)),
            (pediatric_volume_for_dose, (100, 0)),
            (pediatric_infusion_per_kg_min_ml_h, (0.1, 20, 0)),
            (pediatric_fluid_bolus_ml, (-1, 10)),
            (pediatric_maintenance_ml_day, (0,))
        ):
            with self.assertRaises(ValueError):
                fn(*args)


    def test_v136_pediatric_pump_tables_from_source_verified_registry(self):
        epi = pediatric_pump_table('epinephrine', 20)
        nor = pediatric_pump_table('norepinephrine', 20)
        dob = pediatric_pump_table('dobutamine', 20)
        mil = pediatric_pump_table('milrinone', 20)
        fent = pediatric_pump_table('fentanyl', 20)
        mid = pediatric_pump_table('midazolam', 20)

        self.assertAlmostEqual(next(x['ml_h'] for x in epi['rows'] if x['dose'] == 0.1), 1.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in nor['rows'] if x['dose'] == 0.1), 1.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in dob['rows'] if x['dose'] == 5.0), 12.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in mil['rows'] if x['dose'] == 0.5), 3.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in fent['rows'] if x['dose'] == 1.0), 0.4)
        self.assertAlmostEqual(next(x['ml_h'] for x in mid['rows'] if x['dose'] == 0.1), 2.0)

    def test_v136_dopamine_source_restriction_is_enforced(self):
        dopamine = pediatric_pump_table('dopamine', 20)
        self.assertAlmostEqual(next(x['ml_h'] for x in dopamine['rows'] if x['dose'] == 10.0), 1.0)
        with self.assertRaises(ValueError):
            pediatric_pump_table('dopamine', 35)

    def test_v136_pediatric_pump_table_works_with_source_verified_synthetic_registry(self):
        payload = {
            'schema_version': 'test',
            'drugs': [{
                'drug': 'norepinephrine',
                'dose_unit': 'micrograms/kg/min',
                'dose_ladder': [0.05, 0.1, 0.2],
                'preparation_mode': 'fixed_concentration',
                'final_concentration_per_ml': 20,
                'concentration_unit': 'micrograms/mL',
                'status': 'source_verified'
            }]
        }
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'registry.json'
            p.write_text(json.dumps(payload), encoding='utf-8')
            table = pediatric_pump_table('norepinephrine', 20, p)
            self.assertAlmostEqual(table['rows'][0]['ml_h'], 3.0)
            self.assertAlmostEqual(table['rows'][1]['ml_h'], 6.0)
            self.assertAlmostEqual(table['rows'][2]['ml_h'], 12.0)

    def test_v136_off_label_or_product_restricted_pediatric_pumps_fail_closed(self):
        for drug in ('dexmedetomidine', 'propofol'):
            with self.assertRaises(ValueError):
                pediatric_pump_table(drug, 20)

    def test_v136_propofol_guideline_label_conflict_is_preserved(self):
        module = ' '.join(load(ROOT, 'pediatric-emergency-medications').split())
        self.assertIn('PANDEM 2022 allows short-term continuous propofol', module)
        self.assertIn('guideline/product-label conflict', module)
        data = json.loads((ROOT / 'qa' / 'pediatric-infusion-localization.json').read_text(encoding='utf-8'))
        item = next(x for x in data['drugs'] if x['drug'] == 'propofol')
        self.assertEqual(item['status'], 'guideline_supported_product_restricted')

    def test_v136_pediatric_source_hierarchy_is_not_local_dependent(self):
        module = ' '.join(load(ROOT, 'pediatric-emergency-medications').split())
        self.assertIn('ERC/RCUK 2025 as the primary European resuscitation pathway', module)
        self.assertIn('AHA/AAP PALS 2025', module)
        self.assertIn('SSC pediatric sepsis 2026', module)
        self.assertIn('PANDEM 2022', module)
        self.assertNotIn('pharmacy/Horta has not verified it', module)
        data = json.loads((ROOT / 'qa' / 'pediatric-infusion-localization.json').read_text(encoding='utf-8'))
        self.assertIn('Hospital da Horta local protocol is not required', data['rule'])
        for item in data['drugs']:
            self.assertNotEqual(item['status'], 'local_pending')


    def test_v136_pediatric_bolus_registry_core_calculations(self):
        ana = pediatric_bolus_calculate('anaphylaxis-epinephrine-im', 20)
        self.assertAlmostEqual(ana['dose'], 0.2)
        self.assertAlmostEqual(ana['volume_ml'], 0.2)
        hyp = pediatric_bolus_calculate('hypoglycemia-dextrose10', 20)
        self.assertAlmostEqual(hyp['dose'], 4.0)
        self.assertAlmostEqual(hyp['volume_ml'], 40.0)
        hk = pediatric_bolus_calculate('hyperkalemia-arrest-dextrose10', 20)
        self.assertAlmostEqual(hk['volume_ml'], 100.0)
        k = pediatric_bolus_calculate('severe-hypokalemia-potassium', 20)
        self.assertAlmostEqual(k['dose'], 20.0)
        rsi = pediatric_bolus_calculate('rsi-ketamine', 20)
        self.assertEqual(rsi['dose_range'], [20.0, 40.0])

    def test_v136_pediatric_bolus_caps_and_fixed_doses(self):
        ana = pediatric_bolus_calculate('anaphylaxis-epinephrine-im', 80)
        self.assertAlmostEqual(ana['dose'], 0.5)
        self.assertAlmostEqual(ana['volume_ml'], 0.5)
        insulin = pediatric_bolus_calculate('hyperkalemia-arrest-insulin', 150)
        self.assertAlmostEqual(insulin['dose'], 10.0)
        mg = pediatric_bolus_calculate('acute-asthma-magnesium', 60)
        self.assertEqual(mg['dose_range'], [2000.0, 2000.0])
        ipra = pediatric_bolus_calculate('acute-asthma-ipratropium', 18)
        self.assertAlmostEqual(ipra['dose'], 250.0)

    def test_v136_pediatric_bolus_calculator_fails_closed(self):
        with self.assertRaises(ValueError):
            pediatric_bolus_calculate('unknown-entry', 20)
        with self.assertRaises(ValueError):
            pediatric_bolus_calculate('anaphylaxis-epinephrine-im', 0)


    def test_v136_pediatric_analgesia_and_home_dose_registry(self):
        para = pediatric_bolus_calculate('pain-paracetamol-po', 20)
        self.assertAlmostEqual(para['dose'], 300.0)
        ibu = pediatric_bolus_calculate('pain-ibuprofen-po', 20)
        self.assertAlmostEqual(ibu['dose'], 200.0)
        fent = pediatric_bolus_calculate('pain-fentanyl-intranasal', 20)
        self.assertAlmostEqual(fent['dose'], 30.0)
        self.assertAlmostEqual(fent['volume_ml'], 0.6)
        nal = pediatric_bolus_calculate('opioid-toxicity-naloxone-initial', 20)
        self.assertAlmostEqual(nal['dose'], 200.0)
        nal2 = pediatric_bolus_calculate('opioid-toxicity-naloxone-escalation', 30)
        self.assertAlmostEqual(nal2['dose'], 2000.0)

    def test_v136_pediatric_antibiotics_are_syndrome_specific(self):
        module = ' '.join(load(ROOT, 'pediatric-emergency-medications').split())
        self.assertIn('do **not** build a universal weight-based antibiotic table', module)
        self.assertIn('syndrome-specific pathway and current guideline', module)
        self.assertIn('local resistance', module)


    def test_v136_pediatric_antibiotic_syndrome_specific_calculations(self):
        sepsis = pediatric_antibiotic_calculate('sepsis-community-ceftriaxone', 20)
        self.assertAlmostEqual(sepsis['dose'], 1600.0)
        self.assertEqual(sepsis['frequency'], 'once daily')
        pyelo = pediatric_antibiotic_calculate('pyelonephritis-ceftriaxone', 20)
        self.assertEqual(pyelo['dose_range'], [1000.0, 1600.0])
        gent = pediatric_antibiotic_calculate('pyelonephritis-gentamicin-initial', 20)
        self.assertAlmostEqual(gent['dose'], 140.0)
        uti = pediatric_antibiotic_calculate('lower-uti-trimethoprim', 20)
        self.assertAlmostEqual(uti['dose'], 80.0)
        cellulitis = pediatric_antibiotic_calculate('cellulitis-flucloxacillin-iv', 20)
        self.assertEqual(cellulitis['dose_range'], [250.0, 500.0])

    def test_v136_pediatric_antibiotic_caps_and_boundaries(self):
        sepsis = pediatric_antibiotic_calculate('sepsis-community-ceftriaxone', 80)
        self.assertAlmostEqual(sepsis['dose'], 4000.0)
        uti = pediatric_antibiotic_calculate('lower-uti-trimethoprim', 80)
        self.assertAlmostEqual(uti['dose'], 200.0)
        meningitis = pediatric_antibiotic_calculate('meningitis-ceftriaxone-ge2mo', 20)
        self.assertAlmostEqual(meningitis['dose'], 2000.0)
        self.assertEqual(meningitis['frequency'], 'once daily')
        with self.assertRaises(ValueError):
            pediatric_antibiotic_calculate('unknown-antibiotic', 20)

    def test_v136_pediatric_antibiotic_registry_is_not_universal(self):
        module = ' '.join(load(ROOT, 'pediatric-emergency-medications').split())
        self.assertIn('Canonical pediatric antibiotic registry', module)
        self.assertIn('do **not** build a universal weight-based antibiotic table', module)
        data = json.loads((ROOT / 'qa' / 'pediatric-antibiotics.json').read_text(encoding='utf-8'))
        meningitis = next(x for x in data['entries'] if x['id'] == 'meningitis-ceftriaxone-ge2mo')
        self.assertEqual(meningitis['status'], 'source_verified')
        self.assertIn('NICE NG240', meningitis['source'])
        self.assertIn('RCH', meningitis['source'])


    def test_v136_pediatric_discharge_home_use_entries(self):
        sal = pediatric_bolus_calculate('asthma-discharge-salbutamol-pmdi', 18)
        self.assertAlmostEqual(sal['dose'], 2.0)
        croup = pediatric_bolus_calculate('croup-dexamethasone-severe', 20)
        self.assertAlmostEqual(croup['dose'], 12.0)
        ors = pediatric_bolus_calculate('gastroenteritis-ors-rehydration', 12)
        self.assertAlmostEqual(ors['volume_ml'], 600.0)


    def test_v136_pediatric_iv_fluid_module_core_invariants(self):
        module = ' '.join(load(ROOT, 'pediatric-iv-fluid-therapy').split())
        for invariant in (
            'glucose-free isotonic crystalloid with sodium 131--154 mmol/L',
            '10 mL/kg IV/IO over <10 min',
            '10--20 mL/kg per bolus',
            '40--60 mL/kg during the first hour',
            '50 mL/kg over 4 h plus maintenance',
            '100 mL/kg deficit replacement',
            '50 mL/kg deficit replacement',
            'replace the water deficit **over 48 h**',
            '<=0.5 mmol/L/h',
            '2.7% sodium chloride 2 mL/kg, max 100 mL, over 10--15 min',
            '0.9% saline 10--20 mL/kg over 20--30 min',
            '24--48 h',
            '100/50/20 mL/kg/day',
            '50--80% of calculated maintenance'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_fluid_calculator_core_examples(self):
        bolus = pediatric_fluid_shock_bolus(12)
        self.assertAlmostEqual(bolus['volume_ml'], 120.0)
        self.assertAlmostEqual(bolus['equivalent_ml_h'], 720.0)
        ors = pediatric_ors_rehydration(18)
        self.assertAlmostEqual(ors['volume_ml'], 900.0)
        self.assertAlmostEqual(ors['average_ml_h'], 225.0)
        self.assertAlmostEqual(pediatric_fluid_maintenance_ml_day(25), 1600.0)
        self.assertAlmostEqual(pediatric_fluid_maintenance_ml_h(25), 1600.0/24.0)
        self.assertAlmostEqual(pediatric_fluid_maintenance_ml_h(25, 2/3), (1600.0/24.0)*(2/3))

    def test_v136_pediatric_dehydration_deficit_and_special_timing(self):
        self.assertAlmostEqual(pediatric_dehydration_deficit_ml(20, 7), 1400.0)
        plan = pediatric_generic_deficit_48h_plan(20, 7)
        self.assertAlmostEqual(plan['first_24h_deficit_ml'], 1000.0)
        self.assertAlmostEqual(plan['second_24h_deficit_ml'], 400.0)
        self.assertAlmostEqual(pediatric_gastroenteritis_iv_deficit(20, False), 1000.0)
        self.assertAlmostEqual(pediatric_gastroenteritis_iv_deficit(20, True), 2000.0)
        hyper = pediatric_hypernatremia_deficit_rate(20, 7)
        self.assertAlmostEqual(hyper['deficit_ml_h'], 1400.0/48.0)
        hypo = pediatric_symptomatic_hyponatremia_bolus(60)
        self.assertAlmostEqual(hypo['volume_ml'], 100.0)

    def test_v136_pediatric_fluid_calculator_fails_closed(self):
        with self.assertRaises(ValueError):
            pediatric_fluid_shock_bolus(0)
        with self.assertRaises(ValueError):
            pediatric_dehydration_deficit_ml(20, 25)
        with self.assertRaises(ValueError):
            pediatric_fluid_maintenance_ml_h(20, 0)


    def test_v136_pediatric_ketamine_weight_banded_infusion(self):
        k8 = pediatric_pump_table('ketamine', 8)
        self.assertAlmostEqual(k8['concentration_per_ml'], 1.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in k8['rows'] if x['dose'] == 0.2), 1.6)
        k20 = pediatric_pump_table('ketamine', 20)
        self.assertAlmostEqual(k20['concentration_per_ml'], 2.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in k20['rows'] if x['dose'] == 0.2), 2.0)
        k50 = pediatric_pump_table('ketamine', 50)
        self.assertAlmostEqual(k50['concentration_per_ml'], 4.0)
        self.assertAlmostEqual(next(x['ml_h'] for x in k50['rows'] if x['dose'] == 0.2), 2.5)

    def test_v136_pediatric_meningitis_doses_are_age_specific(self):
        cef = pediatric_antibiotic_calculate('meningitis-ceftriaxone-ge2mo', 20)
        self.assertAlmostEqual(cef['dose'], 2000.0)
        cefotax = pediatric_antibiotic_calculate('meningitis-cefotaxime-ge2mo', 20)
        self.assertAlmostEqual(cefotax['dose'], 1000.0)
        dex = pediatric_antibiotic_calculate('meningitis-dexamethasone-ge2mo', 20)
        self.assertAlmostEqual(dex['dose'], 3.0)
        self.assertEqual(dex['frequency'], 'every 6 hours for 4 days')


    def test_v136_pediatric_acute_asthma_module(self):
        module = ' '.join(load(ROOT, 'pediatric-acute-asthma').split())
        for invariant in (
            '4 or more puffs of 100 micrograms/puff',
            '2.5 mg nebulized',
            '4--10 puffs',
            '4 puffs of 20 micrograms',
            '250 micrograms nebulized',
            '1--2 mg/kg/day',
            '20 mg/day if <2 years',
            '30 mg/day if age 2--5 years',
            'max 40 mg/day',
            '0.3--0.6 mg/kg, max 12 mg',
            '40--50 mg/kg IV, max 2 g',
            '20--60 min'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_airway_rsi_module(self):
        module = ' '.join(load(ROOT, 'pediatric-airway-rsi').split())
        for invariant in (
            'ketamine **0.5--2 mg/kg IV**',
            'rocuronium **1.2--1.6 mg/kg IV**',
            'continuous waveform capnography',
            'paralysis can outlast induction',
            'Oxygenation takes priority'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_asthma_steroid_calculations(self):
        p1 = pediatric_bolus_calculate('asthma-prednisolone-lt2', 8)
        self.assertEqual(p1['dose_range'], [8.0, 16.0])
        p2 = pediatric_bolus_calculate('asthma-prednisolone-2to5', 20)
        self.assertEqual(p2['dose_range'], [20.0, 30.0])
        p3 = pediatric_bolus_calculate('asthma-prednisolone-6to11', 30)
        self.assertEqual(p3['dose_range'], [30.0, 40.0])
        dex = pediatric_bolus_calculate('asthma-dexamethasone', 20)
        self.assertEqual(dex['dose_range'], [6.0, 12.0])


    def test_v136_pediatric_electrolyte_emergency_module(self):
        module = ' '.join(load(ROOT, 'pediatric-electrolyte-emergencies').split())
        for invariant in (
            '0.68 mL/kg (0.15 mmol/kg), max 30 mL',
            '0.2 mL/kg (0.14 mmol/kg), max 10 mL',
            'glucose 10% **5 mL/kg IV**',
            'insulin **0.1 unit/kg IV, max 10 units**',
            '2.5 mg if <=25 kg',
            '1--2 mmol/kg/dose, max 20 mmol/dose',
            '0.2 mmol/kg/h for 3 h, max 10 mmol/h',
            '0.4 mmol/kg/h for 1--2 h, max 20 mmol/h',
            '0.1--0.2 mmol/kg, up to 0.4 mmol/kg, max 8 mmol',
            '0.3--0.6 mL/kg IV',
            '2.7% sodium chloride 2 mL/kg, max 100 mL',
            'glucose 10% **2 mL/kg IV/IO**'
        ):
            self.assertIn(invariant, module)


    def test_v136_pediatric_transfusion_major_hemorrhage_module(self):
        module = ' '.join(load(ROOT, 'pediatric-blood-transfusion-major-hemorrhage').split())
        for invariant in (
            'maximum about 20 mL/kg',
            'packed red cells **10 mL/kg**',
            '15--20 mg/kg IV, max 1 g over 10 min',
            'RBC volume (mL) = weight (kg) x 0.5 x desired Hb rise (g/L)',
            '**10 mL/kg**',
            'Fresh frozen plasma',
            '**10--20 mL/kg**',
            'Cryoprecipitate',
            '**5--10 mL/kg**',
            'fibrinogen is **<1.5 g/L**',
            'as fast as clinically indicated'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_blood_product_calculator(self):
        self.assertAlmostEqual(pediatric_trauma_rbc_ml(12), 120.0)
        self.assertAlmostEqual(pediatric_stable_rbc_ml(10, 20), 100.0)
        self.assertAlmostEqual(pediatric_stable_rbc_rate_ml_h(10), 50.0)
        self.assertAlmostEqual(pediatric_platelets_ml(12), 120.0)
        self.assertEqual(pediatric_ffp_range_ml(12), [120.0, 240.0])
        self.assertEqual(pediatric_cryo_range_ml(12), [60.0, 120.0])

    def test_v136_pediatric_blood_product_calculator_boundaries(self):
        with self.assertRaises(ValueError):
            pediatric_stable_rbc_ml(20, 20)
        with self.assertRaises(ValueError):
            pediatric_stable_rbc_ml(10, 25)
        with self.assertRaises(ValueError):
            pediatric_platelets_ml(15)


    def test_v136_pediatric_procedural_sedation_module(self):
        module = ' '.join(load(ROOT, 'pediatric-procedural-sedation').split())
        for invariant in (
            '1--1.5 mg/kg IV over 1--2 min',
            '0.25--0.5 mg/kg IV every 10 min',
            'Maximum cumulative **4.5 mg/kg**',
            '4 mg/kg IM',
            '2 mg/kg IM after 10 min',
            'infants **<3 months**',
            '30--70% nitrous oxide',
            'safe to start at **70%**',
            '1.5 micrograms/kg IN',
            '0.75--1.5 micrograms/kg after 5--10 min',
            'premorbid neurologic baseline'
        ):
            self.assertIn(invariant, module)


    def test_v136_pediatric_acute_respiratory_support_is_registered(self):
        module = ' '.join(load(ROOT, 'pediatric-acute-respiratory-support').split())
        for invariant in (
            'SpO2 94--98%',
            '<=12 kg use 2 L/kg/min',
            'maximum **50 L/min**',
            'no clinical stabilisation within **2 h**',
            'not stabilising within **4 h**',
            '6--8 mL/kg ideal body weight',
            'PEEP 5 cm H2O',
            'Do not import adult NIV settings'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_respiratory_support_calculator(self):
        self.assertAlmostEqual(pediatric_hfno_flow_l_min(10), 20.0)
        self.assertAlmostEqual(pediatric_hfno_flow_l_min(20), 28.0)
        self.assertAlmostEqual(pediatric_hfno_flow_l_min(80), 50.0)
        self.assertEqual(pediatric_ventilation_rate_reference(0.5), 25)
        self.assertEqual(pediatric_ventilation_rate_reference(4), 20)
        self.assertEqual(pediatric_ventilation_rate_reference(10), 15)
        self.assertEqual(pediatric_ventilation_rate_reference(14), 10)

    def test_v136_pediatric_cns_infection_core_regimens(self):
        module = ' '.join(load(ROOT, 'pediatric-cns-infection').split())
        for invariant in (
            'within **30 min of the decision to treat**',
            'within 1 h of hospital arrival',
            'ceftriaxone **100 mg/kg IV every 24 h, max 4 g**',
            'cefotaxime **50 mg/kg IV every 6 h, max 2 g**',
            'vancomycin **15 mg/kg IV every 6 h**',
            '0.15 mg/kg IV every 6 h, max 10 mg',
            '20 mg/kg IV every 8 h',
            '500 mg/m2 IV every 8 h'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_toxicology_core_safety(self):
        module = ' '.join(load(ROOT, 'pediatric-toxicology').split())
        for invariant in (
            'very limited role',
            'within **1--2 h**',
            '>200 mg/kg or >10 g',
            '200 mg/kg over 4 h',
            '100 mg/kg over 16 h',
            'sodium bicarbonate **2 mmol/kg IV**',
            'restoration of adequate ventilation'
        ):
            self.assertIn(invariant, module)

    def test_v136_pediatric_meningitis_antibiotic_registry(self):
        c = pediatric_antibiotic_calculate('meningitis-ceftriaxone-ge2mo', 20)
        self.assertAlmostEqual(c['dose'], 2000.0)
        v = pediatric_antibiotic_calculate('meningitis-vancomycin-pneumococcal-risk', 60)
        self.assertAlmostEqual(v['dose'], 750.0)

    def test_v136_croup_current_rch_maximum(self):
        module = ' '.join(load(ROOT, 'croup').split())
        self.assertIn('maximum 12 mg per current RCH guidance', module)
        self.assertIn('observe at least 3 h after nebulized epinephrine', module)
        self.assertNotIn('maximum 16 mg per RCH guidance', module)

    def test_v136_pediatric_dka_core_safety(self):
        module = ' '.join(load(ROOT, 'pediatric-dka').split())
        for invariant in (
            '10 mL/kg 0.9% sodium chloride over 30 min',
            '1 h of IV rehydration',
            '0.1 units/kg/h',
            '0.05 units/kg/h',
            '40 mmol/L KCl',
            '10% glucose 2 mL/kg IV',
            'mannitol 20% 0.5 g/kg IV over 20 min',
            '3% sodium chloride 3 mL/kg IV over 15 min'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_dka_calculator(self):
        self.assertAlmostEqual(pediatric_dka_corrected_sodium(130, 25), 137.8)
        self.assertAlmostEqual(pediatric_dka_insulin_ml_h(20, 0.1, 1.0), 2.0)
        self.assertAlmostEqual(pediatric_dka_insulin_ml_h(20, 0.1, 0.1), 20.0)
        rescue = pediatric_dka_cerebral_rescue(20)
        self.assertAlmostEqual(rescue['mannitol_20_percent_ml'], 50.0)
        self.assertAlmostEqual(rescue['hypertonic_3_percent_ml'], 60.0)

    def test_v136_pediatric_burns_core(self):
        module = ' '.join(load(ROOT, 'pediatric-burns').split())
        for invariant in (
            '20 min of cool running water within 3 h of injury',
            '>=10% TBSA',
            '3 mL x weight (kg) x %TBSA',
            'half in the first 8 h from injury',
            '1 mL/kg/h'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_burn_calculator(self):
        p = pediatric_burn_plan(20, 15, hours_since_burn=2)
        self.assertAlmostEqual(p['resuscitation_24h_ml'], 900.0)
        self.assertAlmostEqual(p['first_half_ml'], 450.0)
        self.assertAlmostEqual(p['first_phase_rate_ml_h'], 75.0)
        self.assertAlmostEqual(p['second_phase_rate_ml_h'], 28.125)
        self.assertAlmostEqual(p['maintenance_ml_day'], 1500.0)
        self.assertAlmostEqual(p['urine_target_ml_h'], 20.0)

    def test_v136_pediatric_sepsis_current_guidance(self):
        module = ' '.join(load(ROOT, 'pediatric-sepsis').split())
        for invariant in (
            'ideally within 1 h',
            'ideally within 3 h',
            '80 mg/kg IV once daily, max 4 g',
            '10--20 mL/kg per bolus',
            '40--60 mL/kg in the first hour',
            'insufficient evidence to prefer epinephrine over norepinephrine or vice versa universally',
            'do **not** routinely give hydrocortisone'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_adrenal_crisis_doses(self):
        module = ' '.join(load(ROOT, 'pediatric-adrenal-crisis').split())
        for invariant in (
            'birth--6 weeks 25 mg; 6 weeks--2 years 25 mg; 3--12 years 50 mg; >12 years 100 mg',
            '5--10 mg q6h',
            '12.5 mg q6h',
            '25 mg q6h',
            '0.9% sodium chloride 10 mL/kg IV',
            '0.9% sodium chloride + 5% glucose',
            '30 mg/m2/day',
            '20 mg/m2/day'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_head_injury_core(self):
        module = ' '.join(load(ROOT, 'pediatric-head-injury').split())
        for invariant in (
            'GCS <=13',
            'observe for up to **4 h after injury**',
            '30-minutely neurological observations for the first 2 h',
            'persistent **GCS <8**',
            'fall of >2 GCS points',
            'returned to normal consciousness/behaviour for at least 1 h'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_abdominal_surgical_red_flags(self):
        module = ' '.join(load(ROOT, 'pediatric-abdominal-surgical-emergencies').split())
        for invariant in (
            'Ultrasound is the initial study of choice',
            'Do **not** attempt enema reduction with peritonitis, shock, radiological perforation or clinical instability',
            'success >80%',
            'urgent surgical review',
            'within **4--6 h**',
            'bilious vomiting in an infant/child is a surgical emergency until proven otherwise'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_major_trauma_core(self):
        module = ' '.join(load(ROOT, 'pediatric-major-trauma').split())
        for invariant in (
            '**<c>ABCDE**',
            'tourniquet for life-threatening extremity bleeding',
            'rigid/hard collars are not routinely recommended',
            'Do not use flexion-extension radiographs',
            'eFAST has a **limited rule-out role**',
            '0.9% sodium chloride 10 mL/kg',
            'packed red cells **10 mL/kg**',
            '**15 mg/kg IV**',
            'tertiary survey within **24 h**',
            'non-accidental injury'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_hypertensive_emergency_core(self):
        module = ' '.join(load(ROOT, 'pediatric-hypertensive-emergency').split())
        for invariant in (
            'estimated **95th percentile**',
            '**<25% in the first 6--8 h**',
            '0.25--3 mg/kg/h',
            'maximum initial rate **120 mg/h**',
            '0.2--1 mg/kg',
            'maximum **40 mg/dose**',
            '**1 mg/mL** via peripheral IV',
            '**5 mg/mL** via central access',
            '0.1--0.2 mg/kg/dose',
            '**1--6 micrograms/kg/min, max 300 micrograms/min**',
            '400 micrograms/mL'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_hypertension_pump_calculations(self):
        self.assertAlmostEqual(pediatric_labetalol_ml_h(20, 0.5, 1.0), 10.0)
        self.assertAlmostEqual(pediatric_labetalol_ml_h(20, 0.5, 5.0), 2.0)
        self.assertAlmostEqual(pediatric_hydralazine_ml_h(20, 4, 400), 12.0)

    def test_v136_pediatric_foreign_body_time_critical_rules(self):
        module = ' '.join(load(ROOT, 'pediatric-foreign-body-emergencies').split())
        for invariant in (
            'normal chest X-ray does **not** exclude aspiration',
            '**CT is not routinely recommended**',
            'oesophageal button battery requires endoscopic removal within 2 h',
            '**honey 10 mL every 10 min up to 6 doses**',
            '**>1 year**',
            '**within the previous 12 h**',
            'multiple magnets, or a magnet plus a metallic object',
            '>6 cm long and/or >2 cm wide',
            '**not a magnet or battery**'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_drowning_hypothermia_special_rules(self):
        module = ' '.join(load(ROOT, 'pediatric-drowning-hypothermia').split())
        for invariant in (
            '**5 rescue breaths**',
            '**100% oxygen**',
            'not routinely indicated',
            '**<35 °C**',
            '**1 °C/h**',
            '**39--42 °C**',
            '**<30 °C**',
            '**3 defibrillation attempts**',
            'do not give amiodarone until temperature >30 °C',
            'every 8 min',
            'observation for **8 h from the drowning event**',
            '**SpO2 >=95%**'
        ): self.assertIn(invariant, module)

    def test_v136_pediatric_hematology_oncology_emergency_core(self):
        module = ' '.join(load(ROOT, 'pediatric-hematology-oncology-emergencies').split())
        for invariant in (
            'within 30 min when sepsis/systemic compromise is present',
            'within 60 min otherwise',
            '100 mg/kg IV every 6 h, max 4 g/dose',
            '50 mg/kg IV q8h, max 2 g',
            '22.5 mg/kg IV q24h',
            'persistent fever alone in a clinically stable child is not an indication to add vancomycin',
            '125 mL/m2/h or about double maintenance',
            'platelets **>50 x10^9/L**',
            '**5--10 mL/kg**',
            'acute chest syndrome'
        ): self.assertIn(invariant, module)

    def test_v136_febrile_neutropenia_antibiotic_registry(self):
        p = pediatric_antibiotic_calculate('febrile-neutropenia-piptazo', 20)
        self.assertAlmostEqual(p['dose'], 2000.0)
        c = pediatric_antibiotic_calculate('febrile-neutropenia-cefepime', 20)
        self.assertAlmostEqual(c['dose'], 1000.0)
        v = pediatric_antibiotic_calculate('febrile-neutropenia-vancomycin-severe-allergy', 50)
        self.assertAlmostEqual(v['dose'], 500.0)


    def test_v136_pediatric_antibiotic_registry_has_no_duplicate_meningitis_entries(self):
        data = json.loads((ROOT / 'qa' / 'pediatric-antibiotics.json').read_text(encoding='utf-8'))
        ids = [x['id'] for x in data['entries']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn('meningitis-ceftriaxone-ge2m', ids)
        self.assertNotIn('meningitis-cefotaxime-ge2m', ids)

    def test_v136_cellulitis_clarithromycin_oral_does_not_fake_universal_mgkg(self):
        data = json.loads((ROOT / 'qa' / 'pediatric-antibiotics.json').read_text(encoding='utf-8'))
        entry = next(x for x in data['entries'] if x['id'] == 'cellulitis-clarithromycin-po')
        self.assertEqual(entry['status'], 'agent_verified_dose_external')
        self.assertNotIn('dose_per_kg', entry)
        self.assertTrue(entry['weight_band_doses'])
        with self.assertRaises(ValueError):
            pediatric_antibiotic_calculate('cellulitis-clarithromycin-po', 20)

    def test_v136_nice_2025_pediatric_pneumonia_antibiotics(self):
        c1 = pediatric_antibiotic_calculate('cap-severe-coamoxiclav-iv-1to2mo', 5)
        self.assertAlmostEqual(c1['dose'], 150.0)
        self.assertEqual(c1['frequency'], 'twice daily')
        c2 = pediatric_antibiotic_calculate('cap-severe-coamoxiclav-iv-ge3mo', 20)
        self.assertAlmostEqual(c2['dose'], 600.0)
        self.assertEqual(c2['frequency'], 'three times daily')
        mac = pediatric_antibiotic_calculate('cap-severe-clarithromycin-iv-1mto11y', 20)
        self.assertAlmostEqual(mac['dose'], 150.0)
        data = json.loads((ROOT / 'qa' / 'pediatric-antibiotics.json').read_text(encoding='utf-8'))
        oral = next(x for x in data['entries'] if x['id'] == 'cap-nonsevere-amoxicillin-age-bands')
        self.assertEqual(oral['status'], 'age_band_only')
        self.assertEqual(len(oral['age_band_doses']), 5)


    def test_v136_pediatric_urticaria_and_gastroenteritis_discharge_entries(self):
        cet = pediatric_bolus_calculate('urticaria-cetirizine-6to11mo', 8)
        self.assertAlmostEqual(cet['dose'], 2.0)
        ond = pediatric_bolus_calculate('gastroenteritis-ondansetron-single-dose', 20)
        self.assertAlmostEqual(ond['dose'], 3.0)
        capped = pediatric_bolus_calculate('gastroenteritis-ondansetron-single-dose', 80)
        self.assertAlmostEqual(capped['dose'], 8.0)

    def test_v136_pediatric_urticaria_age_bands_are_not_fake_mgkg(self):
        data = json.loads((ROOT / 'qa' / 'pediatric-bolus-medications.json').read_text(encoding='utf-8'))
        bands = next(x for x in data['entries'] if x['id'] == 'urticaria-cetirizine-age-bands')
        self.assertEqual(bands['status'], 'age_band_only')
        self.assertNotIn('dose_per_kg', bands)

    def test_v136_home_medication_safety_boundaries(self):
        module = ' '.join(load(ROOT, 'pediatric-emergency-medications').split())
        self.assertIn('Urticaria with airway/respiratory/cardiovascular/GI involvement is anaphylaxis', module)
        self.assertIn('Ondansetron is an adjunct to rehydration, not a replacement for it', module)
        self.assertIn('bilious vomiting', module)


    def test_v136_pediatric_antibiotics_are_syndrome_specific_and_calculable(self):
        sepsis = pediatric_antibiotic_calculate('sepsis-community-ceftriaxone', 20)
        self.assertAlmostEqual(sepsis['dose'], 1600.0)
        cap = pediatric_antibiotic_calculate('cap-severe-coamoxiclav-iv-ge3mo', 20)
        self.assertAlmostEqual(cap['dose'], 600.0)
        uti = pediatric_antibiotic_calculate('lower-uti-trimethoprim', 20)
        self.assertAlmostEqual(uti['dose'], 80.0)
        pyelo = pediatric_antibiotic_calculate('pyelonephritis-ceftriaxone', 20)
        self.assertEqual(pyelo['dose_range'], [1000.0, 1600.0])
        cellulitis = pediatric_antibiotic_calculate('cellulitis-flucloxacillin-iv', 20)
        self.assertEqual(cellulitis['dose_range'], [250.0, 500.0])

    def test_v136_pediatric_antibiotic_caps_and_external_dose_gate(self):
        sepsis = pediatric_antibiotic_calculate('sepsis-community-ceftriaxone', 80)
        self.assertAlmostEqual(sepsis['dose'], 4000.0)
        cap = pediatric_antibiotic_calculate('cap-severe-coamoxiclav-iv-ge3mo', 60)
        self.assertAlmostEqual(cap['dose'], 1200.0)
        men = pediatric_antibiotic_calculate('meningitis-ceftriaxone-ge2mo', 20)
        self.assertAlmostEqual(men['dose'], 2000.0)
        with self.assertRaises(ValueError):
            pediatric_antibiotic_calculate('unknown-entry', 20)


    def test_v136_home_liquid_volume_requires_selected_product_concentration(self):
        para = pediatric_bolus_with_concentration('pain-paracetamol-po', 20, 40)
        self.assertAlmostEqual(para['dose'], 300.0)
        self.assertAlmostEqual(para['volume_ml'], 7.5)
        ibu = pediatric_bolus_with_concentration('pain-ibuprofen-po', 20, 20)
        self.assertAlmostEqual(ibu['dose'], 200.0)
        self.assertAlmostEqual(ibu['volume_ml'], 10.0)
        with self.assertRaises(ValueError):
            pediatric_bolus_with_concentration('pain-paracetamol-po', 20, 0)


    def test_v136_blinded_image_dataset_gate_accepts_valid_structure(self):
        data = {
            'dataset_class': 'blinded_accuracy',
            'authorized': True,
            'deidentified': True,
            'protocol_prespecified': True,
            'independent_reference': True,
            'modality': 'chest_xray',
            'target_condition': 'target condition',
            'target_question': 'detect target condition',
            'reference_standard': {'type': 'independent expert reference'},
            'patient_grouping_prespecified': True,
            'metrics_requested': True,
            'cases': [
                {
                    'id': 'p1',
                    'patient_uid_hash': 'patient-p1',
                    'study_uid_hash': 'hash-p1',
                    'evaluation': {'mode': 'blinded', 'annotated': False,
                                   'reference_revealed_after_prediction': True,
                                   'prediction_frozen': True,
                                   'prediction_frozen_at': '2026-10-02T12:00:00Z',
                                   'reference_revealed_at': '2026-10-02T12:05:00Z'},
                    'reference': {'target_positive': True},
                    'prediction': {'class': 'positive'}
                },
                {
                    'id': 'n1',
                    'patient_uid_hash': 'patient-n1',
                    'study_uid_hash': 'hash-n1',
                    'evaluation': {'mode': 'blinded', 'annotated': False,
                                   'reference_revealed_after_prediction': True,
                                   'prediction_frozen': True,
                                   'prediction_frozen_at': '2026-10-02T12:01:00Z',
                                   'reference_revealed_at': '2026-10-02T12:06:00Z'},
                    'reference': {'target_positive': False},
                    'prediction': {'class': 'negative'}
                }
            ]
        }
        result = validate_blinded_image_dataset(data)
        self.assertEqual(result['errors'], [])
        self.assertTrue(result['metrics_eligible'])
        self.assertEqual(result['binary_predictions'], 2)

        metrics = calculate_blinded_image_metrics(data)
        self.assertEqual(metrics['errors'], [])
        self.assertTrue(metrics['metrics']['standard_binary_metrics_available'])
        self.assertAlmostEqual(metrics['metrics']['sensitivity'], 1.0)
        self.assertAlmostEqual(metrics['metrics']['specificity'], 1.0)
        self.assertAlmostEqual(metrics['metrics']['coverage'], 1.0)

    def test_v136_image_metrics_fail_closed_for_source_known_or_annotated_cases(self):
        teaching = {
            'dataset_class': 'teaching_source_known',
            'metrics_requested': True,
            'cases': []
        }
        result = validate_blinded_image_dataset(teaching)
        self.assertFalse(result['metrics_eligible'])
        self.assertTrue(result['errors'])

        annotated = {
            'dataset_class': 'blinded_accuracy',
            'authorized': True,
            'deidentified': True,
            'protocol_prespecified': True,
            'independent_reference': True,
            'modality': 'ecg',
            'target_condition': 'target condition',
            'target_question': 'detect target condition',
            'reference_standard': {'type': 'independent expert reference'},
            'patient_grouping_prespecified': True,
            'metrics_requested': False,
            'cases': [{
                'id': 'bad1',
                'patient_uid_hash': 'patient-bad1',
                'study_uid_hash': 'hash-bad1',
                'evaluation': {'mode': 'blinded', 'annotated': True,
                               'reference_revealed_after_prediction': True,
                               'prediction_frozen': True,
                               'prediction_frozen_at': '2026-10-02T12:00:00Z',
                               'reference_revealed_at': '2026-10-02T12:05:00Z'},
                'reference': {'target_positive': True},
                'prediction': {'class': 'positive'}
            }]
        }
        result2 = validate_blinded_image_dataset(annotated)
        self.assertFalse(result2['metrics_eligible'])
        self.assertIn('bad1: annotated must be false', result2['errors'])

    def test_v136_image_freeze_leakage_and_patient_grouping_gates(self):
        data = {
            'dataset_class': 'blinded_accuracy',
            'authorized': True,
            'deidentified': True,
            'protocol_prespecified': True,
            'independent_reference': True,
            'modality': 'ct_mri',
            'target_condition': 'target',
            'target_question': 'target?',
            'reference_standard': {'type': 'independent adjudication'},
            'patient_grouping_prespecified': False,
            'metrics_requested': False,
            'cases': [
                {
                    'id': 'a',
                    'patient_uid_hash': 'same-patient',
                    'study_uid_hash': 'study-a',
                    'evaluation': {'mode':'blinded','annotated':False,
                                   'reference_revealed_after_prediction':True,
                                   'prediction_frozen':True,
                                   'prediction_frozen_at':'2026-10-02T12:10:00Z',
                                   'reference_revealed_at':'2026-10-02T12:05:00Z'},
                    'reference': {'target_positive': True},
                    'prediction': {'class':'positive'}
                },
                {
                    'id': 'b',
                    'patient_uid_hash': 'same-patient',
                    'study_uid_hash': 'study-b',
                    'evaluation': {'mode':'blinded','annotated':False,
                                   'reference_revealed_after_prediction':True,
                                   'prediction_frozen':True,
                                   'prediction_frozen_at':'2026-10-02T12:00:00Z',
                                   'reference_revealed_at':'2026-10-02T12:05:00Z'},
                    'reference': {'target_positive': False},
                    'prediction': {'class':'negative'}
                }
            ]
        }
        result = validate_blinded_image_dataset(data)
        self.assertIn('a: prediction must be frozen before reference reveal', result['errors'])
        self.assertIn('repeated patient_uid_hash requires patient_grouping_prespecified=true', result['errors'])

    def test_v136_abstain_or_nondiagnostic_suppresses_standard_image_metrics(self):
        data = {
            'dataset_class': 'blinded_accuracy',
            'authorized': True,
            'deidentified': True,
            'protocol_prespecified': True,
            'independent_reference': True,
            'modality': 'chest_xray',
            'target_condition': 'target',
            'target_question': 'target?',
            'reference_standard': {'type': 'independent report'},
            'patient_grouping_prespecified': True,
            'metrics_requested': True,
            'cases': [
                {
                    'id':'p','patient_uid_hash':'p','study_uid_hash':'sp',
                    'evaluation':{'mode':'blinded','annotated':False,
                                  'reference_revealed_after_prediction':True,'prediction_frozen':True,
                                  'prediction_frozen_at':'2026-10-02T12:00:00Z',
                                  'reference_revealed_at':'2026-10-02T12:05:00Z'},
                    'reference':{'target_positive':True},
                    'prediction':{'class':'abstain'}
                },
                {
                    'id':'n','patient_uid_hash':'n','study_uid_hash':'sn',
                    'evaluation':{'mode':'blinded','annotated':False,
                                  'reference_revealed_after_prediction':True,'prediction_frozen':True,
                                  'prediction_frozen_at':'2026-10-02T12:00:00Z',
                                  'reference_revealed_at':'2026-10-02T12:05:00Z'},
                    'reference':{'target_positive':False},
                    'prediction':{'class':'negative'}
                }
            ]
        }
        result = calculate_blinded_image_metrics(data)
        self.assertEqual(result['errors'], [])
        self.assertFalse(result['metrics']['standard_binary_metrics_available'])
        self.assertAlmostEqual(result['metrics']['coverage'], 0.5)
        self.assertEqual(result['metrics']['abstain'], 1)
        self.assertIsNone(result['metrics']['sensitivity'])
        self.assertIsNone(result['metrics']['specificity'])


    def test_v136_blinded_image_manifest_generator_starts_fail_closed(self):
        data = build_blinded_image_dataset('ecg', 'target rhythm', 'Is target rhythm present?')
        self.assertFalse(data['authorized'])
        self.assertFalse(data['deidentified'])
        self.assertFalse(data['independent_reference'])
        self.assertEqual(data['modality'], 'ecg')
        result = validate_blinded_image_dataset(data)
        self.assertFalse(result['metrics_eligible'])
        self.assertTrue(result['errors'])

    def test_v136_blinded_image_manifest_generator_rejects_invalid_modality(self):
        with self.assertRaises(ValueError):
            build_blinded_image_dataset('invalid', 'x', 'y')


    def test_v136_image_source_registry_is_fail_closed(self):
        data = json.loads((ROOT / 'qa' / 'image-dataset-source-registry.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data['sources']), 5)
        ids = [x['id'] for x in data['sources']]
        self.assertEqual(len(ids), len(set(ids)))
        for source in data['sources']:
            self.assertIn('official_url', source)
            self.assertIn('license_or_dua_verified', source)
            self.assertIn('reference_strategy_prespecified', source)
            self.assertIn('label_separation_plan', source)
            if source['intake_ready']:
                self.assertTrue(source['license_or_dua_verified'])
                self.assertTrue(source['redistribution_rule_documented'])
                self.assertTrue(source['deidentified_source'])
                self.assertTrue(source['reference_strategy_prespecified'])
                self.assertTrue(source['label_separation_plan'])

    def test_v136_image_source_registry_does_not_overclaim_candidate_readiness(self):
        data = json.loads((ROOT / 'qa' / 'image-dataset-source-registry.json').read_text(encoding='utf-8'))
        items = {x['id']: x for x in data['sources']}
        self.assertEqual(items['ptb-xl']['license_or_dua'], 'CC BY 4.0')
        self.assertTrue(items['ptb-xl']['license_or_dua_verified'])
        self.assertTrue(items['ptb-xl']['reference_strategy_prespecified'])
        self.assertTrue(items['ptb-xl']['label_separation_plan'])
        self.assertTrue(items['ptb-xl']['intake_ready'])
        self.assertTrue(items['rsna-ich-2019']['license_or_dua_verified'])
        self.assertTrue(items['rsna-ich-2019']['intake_ready'])
        self.assertTrue(items['rsna-ich-2019']['reference_strategy_prespecified'])
        self.assertTrue(items['rsna-ich-2019']['label_separation_plan'])
        self.assertFalse(items['chexpert']['license_or_dua_verified'])
        self.assertTrue(items['mimic-cxr-2.1.0']['intake_ready'])
        self.assertFalse(items['mimic-cxr-2.1.0']['actual_access_verified'])
        self.assertTrue(items['mimic-cxr-2.1.0']['reference_strategy_prespecified'])
        self.assertTrue(items['echonet-dynamic']['intake_ready'])
        self.assertFalse(items['echonet-dynamic']['actual_access_verified'])
        self.assertTrue(items['echonet-dynamic']['reference_strategy_prespecified'])

    def test_v136_ptbxl_blinded_cohort_separates_labels_and_hashes_patients(self):
        csv_text = (
            "ecg_id,patient_id,strat_fold,scp_codes\n"
            "1,100,10,\"{'AFIB': 100.0}\"\n"
            "2,100,10,\"{'NORM': 100.0}\"\n"
            "3,200,9,\"{'AFIB': 100.0}\"\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'ptbxl_database.csv'
            p.write_text(csv_text, encoding='utf-8')
            cohort, reference = prepare_ptbxl_blinded_cohort(
                p, 'AFIB', '0123456789abcdef', fold=10
            )
        self.assertEqual(len(cohort['cases']), 2)
        self.assertEqual(reference['positive_reference_cases'], 1)
        self.assertEqual(reference['negative_reference_cases'], 1)
        self.assertTrue(cohort['labels_separated'])
        self.assertTrue(cohort['reference_file_sealed_until_prediction_freeze'])
        self.assertEqual(
            cohort['cases'][0]['patient_uid_hash'],
            cohort['cases'][1]['patient_uid_hash']
        )
        self.assertNotIn('target_positive', cohort['cases'][0])
        self.assertIn('target_positive', reference['references'][0])

    def test_v136_ptbxl_github_intake_keeps_reference_out_of_blinded_artifact(self):
        workflow = (ROOT.parent / '.github' / 'workflows' / 'ptbxl-blinded-intake.yml').read_text(encoding='utf-8')
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('PTBXL_BLINDING_SALT', workflow)
        self.assertIn('openssl rand -hex 32', workflow)
        self.assertIn('PTBXL_RUN_SALT', workflow)
        self.assertIn('--require-ready-source ptb-xl', workflow)
        self.assertIn('ptbxl-blinded-', workflow)
        self.assertIn('ptbxl-sealed-reference-', workflow)
        self.assertIn(
            'test ! -e ptbxl-blinded-artifact/SEALED_REFERENCE_DO_NOT_REVEAL.json',
            workflow
        )
        builder = (ROOT / 'scripts' / 'build_ptbxl_blinded_benchmark.py').read_text(encoding='utf-8')
        self.assertIn('0.04 s / 0.1 mV minor divisions', builder)
        self.assertIn('benchmark_contamination_risk', builder)
        self.assertNotIn('25 mm/s equivalent', builder)

    def test_v136_blinded_finalizer_requires_complete_prediction_set_and_freeze_order(self):
        blinded = {
            'dataset_class':'blinded_accuracy',
            'authorized':True,
            'deidentified':True,
            'protocol_prespecified':True,
            'independent_reference':True,
            'modality':'ecg',
            'target_condition':'AFIB',
            'target_question':'AFIB?',
            'reference_standard':{'type':'sealed independent reference'},
            'patient_grouping_prespecified':True,
            'source_id':'ptb-xl',
            'source_version':'1.0.3',
            'cases':[
                {'id':'a','patient_uid_hash':'pa','study_uid_hash':'sa','image_file':'images/a.png'},
                {'id':'b','patient_uid_hash':'pb','study_uid_hash':'sb','image_file':'images/b.png'}
            ]
        }
        refs = {'references':[
            {'id':'a','study_uid_hash':'sa','target_positive':True},
            {'id':'b','study_uid_hash':'sb','target_positive':False}
        ]}
        incomplete = {'predictions':[
            {'id':'a','class':'positive','prediction_frozen_at':'2026-10-02T17:00:00Z'}
        ]}
        with self.assertRaises(ValueError):
            finalize_blinded_image_dataset(
                blinded, incomplete, refs, '2026-10-02T17:10:00Z'
            )

        late = {'predictions':[
            {'id':'a','class':'positive','prediction_frozen_at':'2026-10-02T17:11:00Z'},
            {'id':'b','class':'negative','prediction_frozen_at':'2026-10-02T17:00:00Z'}
        ]}
        with self.assertRaises(ValueError):
            finalize_blinded_image_dataset(
                blinded, late, refs, '2026-10-02T17:10:00Z'
            )

    def test_v136_blinded_finalizer_builds_policy_v11_manifest_without_source_ids(self):
        blinded = {
            'dataset_class':'blinded_accuracy',
            'authorized':True,
            'deidentified':True,
            'protocol_prespecified':True,
            'independent_reference':True,
            'modality':'ecg',
            'target_condition':'AFIB',
            'target_question':'AFIB?',
            'reference_standard':{'type':'PTB-XL sealed reference'},
            'patient_grouping_prespecified':True,
            'source_id':'ptb-xl',
            'source_version':'1.0.3',
            'benchmark_contamination_risk':'unknown_model_pretraining_exposure',
            'cases':[
                {'id':'a','patient_uid_hash':'pa','study_uid_hash':'sa','image_file':'images/a.png'},
                {'id':'b','patient_uid_hash':'pb','study_uid_hash':'sb','image_file':'images/b.png'}
            ]
        }
        preds = {'predictions':[
            {'id':'a','class':'positive','prediction_frozen_at':'2026-10-02T17:00:00Z'},
            {'id':'b','class':'abstain','prediction_frozen_at':'2026-10-02T17:01:00Z'}
        ]}
        refs = {'references':[
            {'id':'a','study_uid_hash':'sa','target_positive':True,'source_ecg_id':'1'},
            {'id':'b','study_uid_hash':'sb','target_positive':False,'source_ecg_id':'2'}
        ]}
        result = finalize_blinded_image_dataset(
            blinded, preds, refs, '2026-10-02T17:10:00Z'
        )
        self.assertEqual(result['schema_version'], '1.1')
        self.assertEqual(result['cases'][0]['prediction']['class'], 'positive')
        self.assertEqual(result['cases'][1]['prediction']['class'], 'abstain')
        self.assertNotIn('source_ecg_id', json.dumps(result))
        gated = validate_blinded_image_dataset(result)
        self.assertEqual(gated['errors'], [])
        metrics = calculate_blinded_image_metrics(result)
        self.assertFalse(metrics['metrics']['standard_binary_metrics_available'])
        self.assertAlmostEqual(metrics['metrics']['coverage'], 0.5)

    def test_v136_blinded_sharding_preserves_all_cases_and_patient_groups(self):
        blinded = {
            'source_id':'ptb-xl','source_version':'1.0.3',
            'target_condition':'AFIB','target_question':'AFIB?',
            'cases':[
                {'id':'a1','patient_uid_hash':'p1','study_uid_hash':'s1','image_file':'images/a1.png'},
                {'id':'a2','patient_uid_hash':'p1','study_uid_hash':'s2','image_file':'images/a2.png'},
                {'id':'b1','patient_uid_hash':'p2','study_uid_hash':'s3','image_file':'images/b1.png'},
                {'id':'c1','patient_uid_hash':'p3','study_uid_hash':'s4','image_file':'images/c1.png'},
            ]
        }
        shards = shard_blinded_image_manifest(blinded, max_cases=2, keep_patient_groups=True)
        all_ids = [case['id'] for shard in shards for case in shard['cases']]
        self.assertEqual(sorted(all_ids), ['a1','a2','b1','c1'])
        self.assertEqual(len(all_ids), len(set(all_ids)))
        locations = {}
        for shard in shards:
            for case in shard['cases']:
                locations.setdefault(case['patient_uid_hash'], set()).add(shard['shard_index'])
        self.assertEqual(len(locations['p1']), 1)

    def test_v136_prediction_template_and_merge_fail_closed(self):
        shard1 = {
            'target_condition':'AFIB','shard_index':1,'shard_count':2,
            'cases':[{'id':'a'}]
        }
        template = build_blinded_prediction_template(shard1)
        self.assertIsNone(template['predictions'][0]['class'])
        self.assertIsNone(template['predictions'][0]['prediction_frozen_at'])

        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            p1 = d/'p1.json'
            p1.write_text(json.dumps({
                'shard_index':1,'shard_count':2,
                'predictions':[{'id':'a','class':'positive','prediction_frozen_at':'2026-10-02T18:00:00Z'}]
            }), encoding='utf-8')
            with self.assertRaises(ValueError):
                merge_blinded_prediction_shards([p1])

            p2 = d/'p2.json'
            p2.write_text(json.dumps({
                'shard_index':2,'shard_count':2,
                'predictions':[{'id':'b','class':'abstain','prediction_frozen_at':'2026-10-02T18:01:00Z'}]
            }), encoding='utf-8')
            merged = merge_blinded_prediction_shards([p1,p2])
            self.assertEqual(merged['shard_count'], 2)
            self.assertEqual(len(merged['predictions']), 2)

            p2.write_text(json.dumps({
                'shard_index':2,'shard_count':2,
                'predictions':[{'id':'b','class':None,'prediction_frozen_at':None}]
            }), encoding='utf-8')
            with self.assertRaises(ValueError):
                merge_blinded_prediction_shards([p1,p2])

    def test_v136_ptbxl_workflow_packages_blinded_shards_without_reference_leakage(self):
        workflow = (ROOT.parent / '.github' / 'workflows' / 'ptbxl-blinded-intake.yml').read_text(encoding='utf-8')
        self.assertIn('shard_blinded_image_manifest.py', workflow)
        self.assertIn('create_blinded_prediction_template.py', workflow)
        self.assertIn('prediction-templates', workflow)
        self.assertIn("! grep -R -E", workflow)
        self.assertIn('"target_positive"', workflow)
        self.assertIn('"source_ecg_id"', workflow)
        self.assertIn('ptbxl-sealed-artifact', workflow)
        self.assertIn(
            'test ! -e ptbxl-blinded-artifact/SEALED_REFERENCE_DO_NOT_REVEAL.json',
            workflow
        )

    def test_v136_rsna_ich_preparer_accepts_only_verified_multireader_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            images = d / 'images.csv'
            refs = d / 'refs.csv'
            images.write_text(
                'study_id,image_id,dicom_path,patient_id\n'
                's1,i1,/data/i1.dcm,p1\n'
                's1,i2,/data/i2.dcm,p1\n'
                's2,i3,/data/i3.dcm,p2\n',
                encoding='utf-8'
            )
            refs.write_text(
                'study_id,target_positive,reference_type\n'
                's1,true,majority_3_neuroradiologists\n'
                's2,false,senior_neuroradiologist_adjudication\n',
                encoding='utf-8'
            )
            blinded, sealed = prepare_rsna_ich_blinded_cohort(
                images, refs, '0123456789abcdef'
            )
            self.assertEqual(len(blinded['cases']), 2)
            self.assertEqual(sealed['positive_reference_cases'], 1)
            self.assertEqual(sealed['negative_reference_cases'], 1)
            serialized = json.dumps(blinded)
            self.assertNotIn('target_positive', serialized)
            self.assertNotIn('/data/i1.dcm', serialized)
            self.assertEqual(blinded['target_condition'], 'any_acute_ich')

    def test_v136_rsna_ich_preparer_rejects_single_reader_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            images = d / 'images.csv'
            refs = d / 'refs.csv'
            images.write_text(
                'study_id,image_id,dicom_path\n'
                's1,i1,/data/i1.dcm\n'
                's2,i2,/data/i2.dcm\n',
                encoding='utf-8'
            )
            refs.write_text(
                'study_id,target_positive,reference_type\n'
                's1,true,single_reader\n'
                's2,false,majority_3_neuroradiologists\n',
                encoding='utf-8'
            )
            with self.assertRaises(ValueError):
                prepare_rsna_ich_blinded_cohort(
                    images, refs, '0123456789abcdef'
                )

    def test_v136_chexpert_expert_preparer_uses_only_binary_expert_truth(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            images = d / 'images.csv'
            gt = d / 'gt.csv'
            images.write_text(
                'study_id,patient_id,image_path,view\n'
                's1,p1,/img/a.jpg,frontal\n'
                's1,p1,/img/b.jpg,lateral\n'
                's2,p2,/img/c.jpg,frontal\n',
                encoding='utf-8'
            )
            gt.write_text(
                'study_id,Edema\n'
                's1,1\n'
                's2,0\n',
                encoding='utf-8'
            )
            blind, ref = prepare_chexpert_expert_blinded_cohort(
                images, gt, 'Edema', '0123456789abcdef'
            )
            self.assertFalse(blind['authorized'])
            self.assertTrue(blind['independent_reference'])
            self.assertEqual(blind['target_condition'], 'Edema')
            self.assertEqual(ref['positive_reference_cases'], 1)
            self.assertEqual(ref['negative_reference_cases'], 1)
            serialized = json.dumps(blind)
            self.assertNotIn('target_positive', serialized)
            self.assertNotIn('/img/a.jpg', serialized)

    def test_v136_chexpert_expert_preparer_rejects_uncertain_or_unsupported_target(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            images = d / 'images.csv'
            gt = d / 'gt.csv'
            images.write_text(
                'study_id,patient_id,image_path\n'
                's1,p1,/img/a.jpg\n'
                's2,p2,/img/b.jpg\n',
                encoding='utf-8'
            )
            gt.write_text(
                'study_id,Edema\n'
                's1,-1\n'
                's2,0\n',
                encoding='utf-8'
            )
            with self.assertRaises(ValueError):
                prepare_chexpert_expert_blinded_cohort(
                    images, gt, 'Edema', '0123456789abcdef'
                )
            with self.assertRaises(ValueError):
                prepare_chexpert_expert_blinded_cohort(
                    images, gt, 'Pneumothorax', '0123456789abcdef'
                )

    def test_v136_mimic_curated_preparer_excludes_uncertain_and_blank(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            images = d / 'images.csv'
            labels = d / 'labels.csv'
            images.write_text(
                'subject_id,study_id,dicom_id,image_path,ViewPosition\n'
                'p1,s1,d1,/m/a.jpg,PA\n'
                'p2,s2,d2,/m/b.jpg,AP\n'
                'p3,s3,d3,/m/c.jpg,AP\n'
                'p4,s4,d4,/m/d.jpg,PA\n',
                encoding='utf-8'
            )
            labels.write_text(
                'study_id,Pneumothorax\n'
                's1,1.0\n'
                's2,0.0\n'
                's3,-1.0\n'
                's4,\n',
                encoding='utf-8'
            )
            blind, ref = prepare_mimic_cxr_curated_blinded_cohort(
                images, labels, 'Pneumothorax', '0123456789abcdef'
            )
            self.assertFalse(blind['authorized'])
            self.assertEqual(len(blind['cases']), 2)
            self.assertEqual(ref['positive_reference_cases'], 1)
            self.assertEqual(ref['negative_reference_cases'], 1)
            serialized = json.dumps(blind)
            self.assertNotIn('target_positive', serialized)
            self.assertNotIn('/m/a.jpg', serialized)

    def test_v136_echonet_preparer_uses_official_test_split_and_ef_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'FileList.csv'
            p.write_text(
                'FileName,EF,Split\n'
                'a.avi,35,TEST\n'
                'b.avi,55,TEST\n'
                'c.avi,20,TRAIN\n',
                encoding='utf-8'
            )
            blind, ref = prepare_echonet_dynamic_blinded_cohort(
                p, '0123456789abcdef'
            )
            self.assertFalse(blind['authorized'])
            self.assertEqual(blind['target_condition'], 'lvef_below_40_percent')
            self.assertEqual(len(blind['cases']), 2)
            self.assertEqual(ref['positive_reference_cases'], 1)
            self.assertEqual(ref['negative_reference_cases'], 1)
            self.assertNotIn('ejection_fraction', json.dumps(blind))

    def test_v136_ptbxl_builder_does_not_log_prevalence_before_reveal(self):
        builder = (ROOT / 'scripts' / 'build_ptbxl_blinded_benchmark.py').read_text(encoding='utf-8')
        main_block = builder.split('if __name__ == "__main__":', 1)[1]
        print_block = main_block.split('print(json.dumps({', 1)[1].split('}, ensure_ascii=False))', 1)[0]
        self.assertNotIn('positive_reference_cases', print_block)
        self.assertNotIn('negative_reference_cases', print_block)
        self.assertIn('sealed_reference_created', print_block)

    def test_v136_ptbxl_afib_image_baseline_frozen_rules(self):
        self.assertEqual(classify_ptbxl_afib_baseline(10, 0.20, 0.30, 0.10), 'positive')
        self.assertEqual(classify_ptbxl_afib_baseline(10, 0.03, 0.04, 0.02), 'negative')
        self.assertEqual(classify_ptbxl_afib_baseline(10, 0.12, 0.16, 0.06), 'abstain')
        self.assertEqual(classify_ptbxl_afib_baseline(4, 0.30, 0.40, 0.20), 'nondiagnostic')

    def test_v136_ptbxl_afib_freeze_record_integrity(self):
        data = json.loads((ROOT / 'qa' / 'results' / 'PTBXL_NATURAL500_V2_AFIB_BASELINE_V1_FREEZE.json').read_text(encoding='utf-8'))
        self.assertEqual(data['status'], 'PRE_REVEAL_FROZEN')
        self.assertEqual(data['case_count'], 500)
        self.assertEqual(len(data['manifest_order_prediction_sequence']), 500)
        counts = {k: data['manifest_order_prediction_sequence'].count(k) for k in 'PNAD'}
        self.assertEqual(counts, {'P': 46, 'N': 359, 'A': 93, 'D': 2})
        self.assertEqual(
            data['full_predictions_file_sha256'],
            'ae7f25704b9a8a43994346406d2fabb43f786c8a49b7c4987bd40f2df1cd6663'
        )

    def test_v136_rsna_ich_render_window_and_geometry_are_frozen(self):
        self.assertEqual(rsna_window_hu_scalar(0), 0)
        self.assertIn(rsna_window_hu_scalar(40), (127, 128))
        self.assertEqual(rsna_window_hu_scalar(80), 255)
        self.assertAlmostEqual(
            rsna_slice_position([1,0,0,0,1,0], [0,0,12.5]),
            12.5
        )
        with self.assertRaises(ValueError):
            rsna_slice_position([1,0,0], [0,0,1])

    def test_v136_rsna_ich_preparer_declares_frozen_render(self):
        script = (ROOT / 'scripts' / 'prepare_rsna_ich_blinded_cohort.py').read_text(encoding='utf-8')
        self.assertIn('"render_protocol_status": "frozen"', script)
        self.assertIn('RSNA_ICH_DICOM_RENDER_PROTOCOL.md', script)
        self.assertIn('"width_hu": 80', script)
        self.assertIn('"level_hu": 40', script)
        self.assertNotIn('must_be_frozen_before_visual_prediction', script)

    def test_v136_echo_visual_sampling_is_deterministic(self):
        idx = echonet_frame_indices(101, 32)
        self.assertEqual(len(idx), 32)
        self.assertEqual(idx[0], 0)
        self.assertEqual(idx[-1], 100)
        self.assertEqual(idx, sorted(idx))
        with self.assertRaises(ValueError):
            echonet_frame_indices(20, 32)

    def test_v136_visual_protocols_are_bound_to_source_preparers(self):
        chex = (ROOT / 'scripts' / 'prepare_chexpert_expert_blinded_cohort.py').read_text(encoding='utf-8')
        mimic = (ROOT / 'scripts' / 'prepare_mimic_cxr_curated_blinded_cohort.py').read_text(encoding='utf-8')
        echo = (ROOT / 'scripts' / 'prepare_echonet_dynamic_blinded_cohort.py').read_text(encoding='utf-8')
        self.assertIn('CXR_VISUAL_INPUT_PROTOCOL.md', chex)
        self.assertIn('CXR_VISUAL_INPUT_PROTOCOL.md', mimic)
        self.assertIn('ECHONET_VISUAL_INPUT_PROTOCOL.md', echo)

    def test_v136_central_formula_registry_is_fully_implemented(self):
        registry = central_load_registry()
        self.assertEqual(len(registry['scales']), 135)
        self.assertEqual(len(registry['formulas']), 45)
        for formula in registry['formulas']:
            self.assertEqual(formula['implementation_status'], 'deterministic_engine')
            self.assertNotEqual(formula['id'], '')
        self.assertEqual(
            len({item['id'] for item in registry['scales']}),
            len(registry['scales'])
        )
        self.assertEqual(
            len({item['id'] for item in registry['formulas']}),
            len(registry['formulas'])
        )

    def test_v136_central_formula_engine_new_coverage(self):
        value, unit = central_calculate('ckd-epi-2021', {
            'age': 50, 'Scr_mg_dL': 1.0, 'sex': 'male'
        })
        self.assertAlmostEqual(value, 91.6914786, places=5)
        self.assertEqual(unit, 'mL/min/1.73m2')

        pao2, _ = central_calculate('alveolar-o2', {
            'FiO2_fraction': 0.21, 'PaCO2_mmHg': 40
        })
        self.assertAlmostEqual(pao2, 99.73, places=2)
        gradient, _ = central_calculate('aa-gradient', {
            'FiO2_fraction': 0.21, 'PaCO2_mmHg': 40, 'PaO2_mmHg': 80
        })
        self.assertAlmostEqual(gradient, 19.73, places=2)

        ibw, _ = central_calculate('ibw-devine', {
            'height_cm': 180, 'sex': 'male'
        })
        self.assertAlmostEqual(ibw, 74.992126, places=5)

        concentration, unit = central_calculate('final-concentration', {
            'drug_amount': 8, 'final_volume_mL': 100, 'amount_unit': 'mg'
        })
        self.assertAlmostEqual(concentration, 0.08)
        self.assertEqual(unit, 'mg/mL')

        delivery, _ = central_calculate('do2', {
            'CO_L_min': 5, 'CaO2_mL_dL': 20
        })
        self.assertEqual(delivery, 1000)

        with self.assertRaisesRegex(ValueError, 'legacy MELD-Na'):
            central_calculate('meld-na-formula', {
                'bilirubin_mg_dL': 2, 'INR': 1.5,
                'creatinine_mg_dL': 1.2, 'sodium_mmol_L': 130
            })
        meld, unit = central_calculate('meld-na-formula', {
            'bilirubin_mg_dL': 2, 'INR': 1.5,
            'creatinine_mg_dL': 1.2, 'sodium_mmol_L': 130,
            'legacy_meld_na_acknowledged': True
        })
        self.assertEqual(meld, 21)
        self.assertIn('legacy MELD-Na', unit)

    def test_v136_scale_engine_never_invents_component_points(self):
        synthetic_registry = {
            'scales': [
                {
                    'id': 'generic-component',
                    'name': 'Generic Component Sum',
                    'calc_type': 'component_sum',
                    'tier': 'TEST',
                    'measures': 'test',
                    'use': 'test',
                },
                {
                    'id': 'external-rule',
                    'name': 'External Rule',
                    'calc_type': 'official_table',
                    'tier': 'TEST',
                    'measures': 'test',
                    'use': 'test',
                },
            ]
        }
        result = central_calculate_scale(
            'generic-component',
            {'components': {'a': 1, 'b': 2}},
            registry=synthetic_registry,
        )
        self.assertEqual(result['value'], 3)
        self.assertEqual(result['status'], 'complete_from_explicit_scored_components')
        self.assertIn('does not infer', result['warning'])

        pending = central_calculate_scale(
            'external-rule', {}, registry=synthetic_registry
        )
        self.assertEqual(pending['status'], 'source_rule_not_yet_encoded')

        with self.assertRaisesRegex(ValueError, 'provenance'):
            central_calculate_scale(
                'external-rule',
                {'explicit_result': 5},
                registry=synthetic_registry,
            )

        explicit = central_calculate_scale(
            'external-rule',
            {
                'explicit_result': 5,
                'provenance': 'validated external table entry',
            },
            registry=synthetic_registry,
        )
        self.assertEqual(explicit['value_or_category'], 5)

    def test_v137_nihss_source_encoded_boundaries_and_un(self):
        zeros = {key: 0 for key in __import__('core_scores_block1').NIHSS_ITEM_MAX}
        result = calculate_nihss({'items': zeros})
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['range'], [0, 42])

        maxima = dict(__import__('core_scores_block1').NIHSS_ITEM_MAX)
        result = calculate_nihss({'items': maxima})
        self.assertEqual(result['total'], 42)

        untestable = dict(zeros)
        untestable['7_limb_ataxia'] = 'UN'
        result = calculate_nihss({'items': untestable})
        self.assertIsNone(result['total'])
        self.assertEqual(result['status'], 'untestable_item_present')

        invalid = dict(zeros)
        invalid['1a_loc'] = 4
        with self.assertRaises(ValueError):
            calculate_nihss({'items': invalid})

    def test_v137_gcs_source_encoded_and_non_testable(self):
        result = calculate_gcs({
            'eye': 'spontaneous',
            'verbal': 'oriented',
            'motor': 'obeys_commands'
        })
        self.assertEqual(result['total'], 15)
        self.assertEqual(result['display'], 'E4 V5 M6 = 15')

        result = calculate_gcs({'eye': 1, 'verbal': 1, 'motor': 1})
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['head_injury_severity_band'], 'severe_below_9')

        result = calculate_gcs({
            'eye': 'spontaneous',
            'verbal': 'NT',
            'motor': 'obeys_commands'
        })
        self.assertIsNone(result['total'])
        self.assertEqual(result['status'], 'not_testable_component_present')

    def test_v137_news2_source_encoded_scale1_and_scale2(self):
        normal = calculate_news2({
            'respiratory_rate': 16,
            'spo2_percent': 98,
            'supplemental_oxygen': False,
            'systolic_bp_mmHg': 120,
            'pulse_bpm': 70,
            'consciousness': 'alert',
            'temperature_c': 37.0,
        })
        self.assertEqual(normal['total'], 0)
        self.assertEqual(normal['trigger_band'], 'low_0_4')

        severe = calculate_news2({
            'respiratory_rate': 30,
            'spo2_percent': 90,
            'supplemental_oxygen': True,
            'systolic_bp_mmHg': 85,
            'pulse_bpm': 140,
            'consciousness': 'new_confusion',
            'temperature_c': 40.0,
        })
        self.assertEqual(severe['total'], 19)
        self.assertEqual(severe['trigger_band'], 'high_7_or_more')

        with self.assertRaisesRegex(ValueError, 'authorization'):
            calculate_news2({
                'respiratory_rate': 16,
                'spo2_percent': 88,
                'supplemental_oxygen': False,
                'systolic_bp_mmHg': 120,
                'pulse_bpm': 70,
                'consciousness': 'alert',
                'temperature_c': 37.0,
                'spo2_scale': 2,
            })

        scale2 = calculate_news2({
            'respiratory_rate': 16,
            'spo2_percent': 97,
            'supplemental_oxygen': True,
            'systolic_bp_mmHg': 120,
            'pulse_bpm': 70,
            'consciousness': 'alert',
            'temperature_c': 37.0,
            'spo2_scale': 2,
            'scale2_authorized_hypercapnic_failure': True,
        })
        self.assertEqual(scale2['components']['spo2'], 3)
        self.assertEqual(scale2['components']['supplemental_oxygen'], 2)
        self.assertEqual(scale2['total'], 5)

    def test_v137_sofa1_source_encoded_zero_and_max(self):
        normal = calculate_sofa1({
            'pao2_fio2_mmHg': 450,
            'respiratory_support': False,
            'platelets_10e3_uL': 200,
            'bilirubin_mg_dL': 0.8,
            'map_mmHg': 80,
            'vasoactive_mcg_kg_min': {
                'dopamine': 0,
                'epinephrine': 0,
                'norepinephrine': 0,
                'dobutamine_any_dose': False,
            },
            'gcs': 15,
            'creatinine_mg_dL': 0.9,
            'urine_output_mL_day': 1200,
            'baseline_sofa': 0,
        })
        self.assertEqual(normal['total'], 0)
        self.assertEqual(normal['delta_sofa'], 0)

        maximum = calculate_sofa1({
            'pao2_fio2_mmHg': 80,
            'respiratory_support': True,
            'platelets_10e3_uL': 10,
            'bilirubin_mg_dL': 13,
            'map_mmHg': 55,
            'vasoactive_mcg_kg_min': {
                'dopamine': 0,
                'epinephrine': 0,
                'norepinephrine': 0.2,
                'dobutamine_any_dose': False,
            },
            'gcs': 5,
            'creatinine_mg_dL': 6,
            'urine_output_mL_day': 100,
            'baseline_sofa': 0,
        })
        self.assertEqual(maximum['total'], 24)
        self.assertEqual(maximum['delta_sofa'], 24)
        self.assertTrue(maximum['sepsis3_organ_dysfunction_signal'])
        self.assertIn('SOFA-1', maximum['version'])

        unsupported = calculate_sofa1({
            'pao2_fio2_mmHg': 80,
            'respiratory_support': False,
            'platelets_10e3_uL': 200,
            'bilirubin_mg_dL': 0.8,
            'map_mmHg': 80,
            'vasoactive_mcg_kg_min': {
                'dopamine': 0,
                'epinephrine': 0,
                'norepinephrine': 0,
                'dobutamine_any_dose': False,
            },
            'gcs': 15,
            'creatinine_mg_dL': 0.9,
        })
        self.assertEqual(unsupported['components']['respiration'], 2)

    def test_v137_central_dispatch_uses_dedicated_core_rules(self):
        gcs = central_calculate_scale('glasgow-coma', {
            'eye': 'spontaneous', 'verbal': 'oriented', 'motor': 'obeys_commands'
        })
        self.assertEqual(gcs['total'], 15)
        self.assertEqual(gcs['registry_id'], 'glasgow-coma')

        registry = central_load_registry()
        for sid in ('nihss', 'glasgow-coma', 'news2', 'sofa'):
            item = next(x for x in registry['scales'] if x['id'] == sid)
            self.assertEqual(item['implementation_status'], 'dedicated_source_encoded_v1')
            self.assertIn('source_url', item)

    def test_v137_heart_source_encoded_boundaries(self):
        low = calculate_heart({
            'history':'slightly_suspicious','ecg':'normal','age':40,
            'risk_factor_count':0,'known_atherosclerotic_disease':False,
            'troponin_multiple_uln':1.0
        })
        self.assertEqual(low['total'],0)
        self.assertEqual(low['risk_band'],'low_0_3')

        high = calculate_heart({
            'history':'highly_suspicious','ecg':'significant_st_depression','age':70,
            'risk_factor_count':3,'known_atherosclerotic_disease':False,
            'troponin_multiple_uln':3.0
        })
        self.assertEqual(high['total'],10)
        self.assertEqual(high['risk_band'],'high_7_10')

    def test_v137_grace2_routes_to_official_calculator_without_fake_probability(self):
        result = prepare_grace2({
            'age':68,'heart_rate_bpm':95,'systolic_bp_mmHg':110,
            'creatinine_mg_dL':1.3,'killip_class':2,
            'cardiac_arrest_at_admission':False,
            'st_segment_deviation':True,
            'elevated_cardiac_biomarkers':True
        })
        self.assertEqual(result['status'],'official_external_calculator_required')
        self.assertEqual(result['input_mode'],'complete_grace2')
        self.assertIn('gracescore.org',result['official_calculator'])
        self.assertNotIn('probability',result)

        mini = prepare_grace2({
            'age':68,'heart_rate_bpm':95,'systolic_bp_mmHg':110,
            'cardiac_arrest_at_admission':False,
            'st_segment_deviation':True,
            'elevated_cardiac_biomarkers':True
        })
        self.assertEqual(mini['input_mode'],'mini_grace_possible')

    def test_v137_cha2ds2_variants_are_versioned_and_not_mixed(self):
        base = {
            'age':76,
            'heart_failure_or_lvd':True,
            'hypertension':True,
            'diabetes':True,
            'prior_stroke_tia_thromboembolism':True,
            'vascular_disease':True,
        }
        vasc = calculate_cha2ds2_vasc({**base,'sex':'female'})
        self.assertEqual(vasc['total'],9)

        va = calculate_cha2ds2_va(base)
        self.assertEqual(va['total'],8)
        self.assertEqual(va['esc2024_context'],'esc2024_oac_recommended_if_eligible')

        one = calculate_cha2ds2_va({
            'age':66,'heart_failure_or_lvd':False,'hypertension':False,
            'diabetes':False,'prior_stroke_tia_thromboembolism':False,
            'vascular_disease':False,
        })
        self.assertEqual(one['total'],1)
        self.assertEqual(one['esc2024_context'],'esc2024_oac_should_be_considered')

    def test_v137_central_dispatch_cardiology_scores(self):
        registry = central_load_registry()
        expected = {
            'heart':'dedicated_source_encoded_v1',
            'grace-2':'validated_official_external_wrapper',
            'cha2ds2-vasc':'dedicated_source_encoded_v1',
            'cha2ds2-va':'dedicated_source_encoded_v1',
        }
        for sid,status in expected.items():
            item = next(x for x in registry['scales'] if x['id'] == sid)
            self.assertEqual(item['implementation_status'],status)

        result = central_calculate_scale('cha2ds2-va',{
            'age':50,'heart_failure_or_lvd':False,'hypertension':True,
            'diabetes':False,'prior_stroke_tia_thromboembolism':False,
            'vascular_disease':False,
        })
        self.assertEqual(result['total'],1)
        self.assertEqual(result['registry_id'],'cha2ds2-va')

    def test_v137_wells_pe_source_encoded(self):
        low = calculate_wells_pe({
            'clinical_signs_dvt':False,'pe_more_likely_than_alternative':False,
            'heart_rate_bpm':80,'immobilization_ge3d_or_surgery_4w':False,
            'previous_dvt_pe':False,'hemoptysis':False,'active_cancer':False
        })
        self.assertEqual(low['total'],0)
        self.assertEqual(low['standard_three_level'],'low')
        self.assertEqual(low['modified_two_level'],'pe_unlikely')

        high = calculate_wells_pe({
            'clinical_signs_dvt':True,'pe_more_likely_than_alternative':True,
            'heart_rate_bpm':120,'immobilization_ge3d_or_surgery_4w':True,
            'previous_dvt_pe':True,'hemoptysis':True,'active_cancer':True
        })
        self.assertEqual(high['total'],12.5)
        self.assertEqual(high['standard_three_level'],'high')
        self.assertEqual(high['modified_two_level'],'pe_likely')

    def test_v137_perc_requires_low_pretest_probability_and_all_8_negative(self):
        base = {
            'low_pretest_probability':True,'age':40,'heart_rate_bpm':90,
            'spo2_percent':98,'hemoptysis':False,'estrogen_use':False,
            'previous_dvt_pe':False,'unilateral_leg_swelling':False,
            'recent_surgery_or_trauma_requiring_hospitalization_4w':False
        }
        result = calculate_perc(base)
        self.assertTrue(result['perc_negative'])
        self.assertEqual(result['positive_count'],0)

        positive = calculate_perc({**base,'age':50})
        self.assertFalse(positive['perc_negative'])
        self.assertEqual(positive['positive_count'],1)

        with self.assertRaisesRegex(ValueError,'low pretest probability'):
            calculate_perc({**base,'low_pretest_probability':False})

    def test_v137_years_thresholds_are_unit_explicit(self):
        zero_items = calculate_years({
            'clinical_signs_dvt':False,'hemoptysis':False,'pe_most_likely':False,
            'd_dimer_ng_mL_feu':999
        })
        self.assertEqual(zero_items['active_threshold_ng_mL_feu'],1000)
        self.assertTrue(zero_items['pe_excluded_by_years'])

        one_item = calculate_years({
            'clinical_signs_dvt':True,'hemoptysis':False,'pe_most_likely':False,
            'd_dimer_ng_mL_feu':500
        })
        self.assertEqual(one_item['active_threshold_ng_mL_feu'],500)
        self.assertFalse(one_item['pe_excluded_by_years'])
        self.assertIn('FEU',one_item['warning'])

    def test_v137_central_dispatch_pe_rules(self):
        registry = central_load_registry()
        for sid in ('wells-pe','perc','years-pe'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('years-pe',{
            'clinical_signs_dvt':False,'hemoptysis':False,'pe_most_likely':False,
            'd_dimer_ng_mL_feu':400
        })
        self.assertTrue(result['pe_excluded_by_years'])
        self.assertEqual(result['registry_id'],'years-pe')

    def test_v137_glasgow_blatchford_source_encoded(self):
        low = calculate_glasgow_blatchford({
            'urea_mmol_L':5.0,'hemoglobin_g_dL':14,'sex':'male',
            'systolic_bp_mmHg':120,'pulse_bpm':80,'melena':False,
            'syncope':False,'hepatic_disease':False,'heart_failure':False
        })
        self.assertEqual(low['total'],0)
        self.assertTrue(low['very_low_risk_score_0_or_1'])

        high = calculate_glasgow_blatchford({
            'urea_mmol_L':26,'hemoglobin_g_dL':9,'sex':'male',
            'systolic_bp_mmHg':85,'pulse_bpm':110,'melena':True,
            'syncope':True,'hepatic_disease':True,'heart_failure':True
        })
        self.assertEqual(high['total'],23)

        bun = calculate_glasgow_blatchford({
            'bun_mg_dL':18.2,'hemoglobin_g_dL':13.5,'sex':'female',
            'systolic_bp_mmHg':120,'pulse_bpm':80,'melena':False,
            'syncope':False,'hepatic_disease':False,'heart_failure':False
        })
        self.assertEqual(bun['components']['urea'],2)

    def test_v137_curb65_source_encoded(self):
        low = calculate_curb65({
            'confusion':False,'urea_mmol_L':7,'respiratory_rate':20,
            'systolic_bp_mmHg':120,'diastolic_bp_mmHg':70,'age':64
        })
        self.assertEqual(low['total'],0)

        high = calculate_curb65({
            'confusion':True,'urea_mmol_L':8,'respiratory_rate':30,
            'systolic_bp_mmHg':89,'diastolic_bp_mmHg':60,'age':65
        })
        self.assertEqual(high['total'],5)
        self.assertEqual(high['severity_band'],'high_3_5')

    def test_v137_phoenix_sepsis_source_encoded(self):
        normal = calculate_phoenix_sepsis({
            'suspected_or_confirmed_infection':True,'age_months':24,
            'pao2_fio2':450,'any_respiratory_support':False,
            'invasive_mechanical_ventilation':False,
            'vasoactive_medication_count':0,'lactate_mmol_L':2,'map_mmHg':60,
            'platelets_10e3_uL':150,'inr':1.0,'d_dimer_mg_L_feu':1,
            'fibrinogen_mg_dL':200,'gcs':15,'fixed_pupils_bilateral':False
        })
        self.assertEqual(normal['total'],0)
        self.assertFalse(normal['phoenix_sepsis'])

        septic_shock = calculate_phoenix_sepsis({
            'suspected_or_confirmed_infection':True,'age_months':6,
            'pao2_fio2':80,'any_respiratory_support':True,
            'invasive_mechanical_ventilation':True,
            'vasoactive_medication_count':2,'lactate_mmol_L':12,'map_mmHg':20,
            'platelets_10e3_uL':80,'inr':1.5,'d_dimer_mg_L_feu':3,
            'fibrinogen_mg_dL':80,'gcs':8,'fixed_pupils_bilateral':False
        })
        self.assertEqual(septic_shock['components']['respiratory'],3)
        self.assertEqual(septic_shock['components']['cardiovascular'],6)
        self.assertEqual(septic_shock['components']['coagulation'],2)
        self.assertEqual(septic_shock['components']['neurologic'],1)
        self.assertEqual(septic_shock['total'],12)
        self.assertTrue(septic_shock['phoenix_sepsis'])
        self.assertTrue(septic_shock['phoenix_septic_shock'])

        partial = calculate_phoenix_sepsis({
            'suspected_or_confirmed_infection':True,'age_months':120,
            'map_mmHg':40
        })
        self.assertEqual(partial['observed_domains'],['cardiovascular'])
        self.assertIn('unmeasured variables',partial['warning'])

    def test_v137_central_dispatch_gi_pneumonia_pediatric_sepsis(self):
        registry=central_load_registry()
        for sid in ('glasgow-blatchford','curb65','phoenix-sepsis'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('curb65',{
            'confusion':False,'urea_mmol_L':7,'respiratory_rate':20,
            'systolic_bp_mmHg':120,'diastolic_bp_mmHg':70,'age':64
        })
        self.assertEqual(result['total'],0)
        self.assertEqual(result['registry_id'],'curb65')

    def test_v137_sofa2_source_encoded_zero_and_max(self):
        zero = calculate_sofa2({
            'gcs':15,
            'delirium_drug_required':False,
            'pao2_fio2_mmHg':350,
            'advanced_ventilatory_support':False,
            'ecmo':False,
            'map_mmHg':80,
            'norepinephrine_mcg_kg_min':0,
            'epinephrine_mcg_kg_min':0,
            'other_vasopressor_or_inotrope':False,
            'mechanical_circulatory_support':False,
            'bilirubin_mg_dL':1.0,
            'creatinine_mg_dL':1.0,
            'urine_lt_0_5_ml_kg_h_6_12h':False,
            'urine_lt_0_5_ml_kg_h_ge12h':False,
            'urine_lt_0_3_ml_kg_h_ge24h':False,
            'anuria_ge12h':False,
            'receiving_or_meets_rrt_criteria':False,
            'platelets_10e3_uL':200,
        })
        self.assertEqual(zero['total'],0)
        self.assertEqual(zero['version'],'SOFA-2 2025')

        maximum = calculate_sofa2({
            'gcs':3,
            'delirium_drug_required':False,
            'pao2_fio2_mmHg':70,
            'advanced_ventilatory_support':True,
            'ecmo':False,
            'map_mmHg':50,
            'norepinephrine_mcg_kg_min':0.5,
            'epinephrine_mcg_kg_min':0,
            'other_vasopressor_or_inotrope':False,
            'mechanical_circulatory_support':False,
            'bilirubin_mg_dL':13,
            'creatinine_mg_dL':4.0,
            'urine_lt_0_5_ml_kg_h_6_12h':False,
            'urine_lt_0_5_ml_kg_h_ge12h':False,
            'urine_lt_0_3_ml_kg_h_ge24h':False,
            'anuria_ge12h':False,
            'receiving_or_meets_rrt_criteria':True,
            'platelets_10e3_uL':40,
        })
        self.assertEqual(maximum['components'],{
            'brain':4,'respiratory':4,'cardiovascular':4,
            'liver':4,'kidney':4,'hemostasis':4
        })
        self.assertEqual(maximum['total'],24)

    def test_v137_sofa2_contemporary_support_thresholds(self):
        result = calculate_sofa2({
            'gcs':15,
            'delirium_drug_required':True,
            'pao2_fio2_mmHg':140,
            'advanced_ventilatory_support':True,
            'ecmo':False,
            'map_mmHg':75,
            'norepinephrine_mcg_kg_min':0.15,
            'epinephrine_mcg_kg_min':0,
            'other_vasopressor_or_inotrope':True,
            'mechanical_circulatory_support':False,
            'bilirubin_mg_dL':2.0,
            'creatinine_mg_dL':2.5,
            'urine_lt_0_5_ml_kg_h_6_12h':False,
            'urine_lt_0_5_ml_kg_h_ge12h':True,
            'urine_lt_0_3_ml_kg_h_ge24h':False,
            'anuria_ge12h':False,
            'receiving_or_meets_rrt_criteria':False,
            'platelets_10e3_uL':90,
        })
        self.assertEqual(result['components']['brain'],1)
        self.assertEqual(result['components']['respiratory'],3)
        self.assertEqual(result['components']['cardiovascular'],3)
        self.assertEqual(result['components']['liver'],1)
        self.assertEqual(result['components']['kidney'],2)
        self.assertEqual(result['components']['hemostasis'],2)
        self.assertEqual(result['total'],12)

    def test_v137_sofa1_and_sofa2_remain_separate_ids(self):
        registry=central_load_registry()
        sofa1=next(x for x in registry['scales'] if x['id']=='sofa')
        sofa2=next(x for x in registry['scales'] if x['id']=='sofa-2')
        self.assertNotEqual(sofa1['version'],sofa2['version'])
        self.assertEqual(sofa2['implementation_status'],'dedicated_source_encoded_v1')
        self.assertIn('2025',sofa2['version'])

    def test_v137_abcd2_source_encoded_boundaries(self):
        low=calculate_abcd2({
            'age':50,'systolic_bp_mmHg':120,'diastolic_bp_mmHg':70,
            'clinical_feature':'other','duration_minutes':5,'diabetes':False
        })
        self.assertEqual(low['total'],0)
        high=calculate_abcd2({
            'age':70,'systolic_bp_mmHg':150,'diastolic_bp_mmHg':95,
            'clinical_feature':'unilateral_weakness','duration_minutes':90,'diabetes':True
        })
        self.assertEqual(high['total'],7)

    def test_v137_aspects_requires_all_ten_explicit_regions(self):
        regions={k:False for k in ('caudate','lentiform','internal_capsule','insula','m1','m2','m3','m4','m5','m6')}
        normal=calculate_aspects({'early_ischemic_change':regions})
        self.assertEqual(normal['total'],10)
        all_abnormal=calculate_aspects({'early_ischemic_change':{k:True for k in regions}})
        self.assertEqual(all_abnormal['total'],0)
        bad=dict(regions); bad.pop('m6')
        with self.assertRaises(ValueError):
            calculate_aspects({'early_ischemic_change':bad})

    def test_v137_mrs_structured_only(self):
        alive=calculate_modified_rankin({'score':3})
        self.assertEqual(alive['score'],3)
        dead=calculate_modified_rankin({'score':6})
        self.assertEqual(dead['description'],'dead')
        with self.assertRaises(ValueError):
            calculate_modified_rankin({'score':7})

    def test_v137_ich_score_source_encoded(self):
        zero=calculate_ich_score({
            'gcs':15,'age':60,'ich_volume_cm3':10,
            'intraventricular_hemorrhage':False,'infratentorial_origin':False
        })
        self.assertEqual(zero['total'],0)
        high=calculate_ich_score({
            'gcs':3,'age':80,'ich_volume_cm3':30,
            'intraventricular_hemorrhage':True,'infratentorial_origin':True
        })
        self.assertEqual(high['total'],6)

    def test_v137_modified_fisher_source_encoded(self):
        self.assertEqual(calculate_modified_fisher({'sah_thickness':'none','ivh':False})['grade'],0)
        self.assertEqual(calculate_modified_fisher({'sah_thickness':'thin','ivh':False})['grade'],1)
        self.assertEqual(calculate_modified_fisher({'sah_thickness':'thin','ivh':True})['grade'],2)
        self.assertEqual(calculate_modified_fisher({'sah_thickness':'thick','ivh':False})['grade'],3)
        self.assertEqual(calculate_modified_fisher({'sah_thickness':'thick','ivh':True})['grade'],4)

    def test_v137_cincinnati_race_fast_ed(self):
        cpss=calculate_cincinnati({'facial_droop':True,'arm_drift':False,'abnormal_speech':False})
        self.assertTrue(cpss['screen_positive'])
        self.assertEqual(cpss['abnormal_count'],1)

        race=calculate_race({
            'facial_palsy':2,'arm_motor':2,'leg_motor':2,
            'head_gaze_deviation':1,'cortical_item':2
        })
        self.assertEqual(race['total'],9)
        self.assertTrue(race['lvo_screen_positive_ge5'])

        fast=calculate_fast_ed({
            'nihss_facial_palsy':3,'nihss_arm_motor':4,'nihss_language':3,
            'nihss_gaze':2,'nihss_neglect':2
        })
        self.assertEqual(fast['total'],9)
        self.assertTrue(fast['lvo_screen_positive_ge4'])

    def test_v137_central_dispatch_adult_neurology(self):
        registry=central_load_registry()
        for sid in ('abcd2','aspects','modified-rankin','ich-score','modified-fisher','cincinnati-stroke','race-stroke','fast-ed'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('abcd2',{
            'age':70,'systolic_bp_mmHg':150,'diastolic_bp_mmHg':80,
            'clinical_feature':'speech_impairment_without_weakness',
            'duration_minutes':30,'diabetes':False
        })
        self.assertEqual(result['total'],4)
        self.assertEqual(result['registry_id'],'abcd2')

    def test_v137_avpu_source_encoded(self):
        self.assertEqual(calculate_avpu({'state':'A'})['ordinal'],0)
        self.assertEqual(calculate_avpu({'state':'voice'})['ordinal'],1)
        self.assertEqual(calculate_avpu({'state':'pain'})['ordinal'],2)
        self.assertEqual(calculate_avpu({'state':'unresponsive'})['ordinal'],3)
        with self.assertRaises(ValueError):
            calculate_avpu({'state':'confused'})

    def test_v137_shock_index_scale_ids_delegate_to_formula_engine(self):
        si=central_calculate_scale('shock-index',{'HR':120,'SBP':100})
        self.assertAlmostEqual(si['value'],1.2)
        self.assertEqual(si['formula_alias'],'shock-index-formula')

        msi=central_calculate_scale('modified-shock-index',{'HR':120,'MAP':80})
        self.assertAlmostEqual(msi['value'],1.5)
        self.assertEqual(msi['formula_alias'],'modified-shock-index-formula')

    def test_v137_transversal_registry_has_no_duplicate_formula_logic(self):
        registry=central_load_registry()
        expected={
            'avpu':'dedicated_source_encoded_v1',
            'shock-index':'central_formula_alias',
            'modified-shock-index':'central_formula_alias',
        }
        for sid,status in expected.items():
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],status)
        code=(ROOT/'scripts'/'core_scores_block6_transversal.py').read_text(encoding='utf-8')
        self.assertNotIn('HR/SBP',code)
        self.assertNotIn('HR/MAP',code)

    def test_v137_pediatric_gcs_age_specific(self):
        infant=calculate_pediatric_gcs({
            'age_years':1,'eye':'spontaneous',
            'verbal':'alert_babbles_coos_words_usual',
            'motor':'obeys_or_normal_spontaneous'
        })
        self.assertEqual(infant['total'],15)
        self.assertEqual(infant['age_band'],'under_4')

        child=calculate_pediatric_gcs({
            'age_years':8,'eye':'to_voice','verbal':'confused','motor':'localizes_pain'
        })
        self.assertEqual(child['total'],12)
        self.assertEqual(child['age_band'],'4_or_more')

        nt=calculate_pediatric_gcs({
            'age_years':2,'eye':'spontaneous','verbal':'NT','motor':'obeys_or_normal_spontaneous'
        })
        self.assertIsNone(nt['total'])
        self.assertEqual(nt['status'],'not_testable_component_present')

    def test_v137_pediatric_gcs_registry_and_dispatch(self):
        registry=central_load_registry()
        item=next(x for x in registry['scales'] if x['id']=='pediatric-gcs')
        self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('pediatric-gcs',{
            'age_years':5,'eye':'spontaneous','verbal':'oriented','motor':'obeys_or_normal_spontaneous'
        })
        self.assertEqual(result['total'],15)
        self.assertEqual(result['registry_id'],'pediatric-gcs')

    def test_v137_timi_ua_nstemi_source_encoded(self):
        low=calculate_timi_ua_nstemi({
            'age':50,'cad_risk_factor_count':0,'known_coronary_stenosis_ge50':False,
            'st_deviation':False,'severe_angina_ge2_episodes_24h':False,
            'aspirin_last_7d':False,'elevated_cardiac_markers':False
        })
        self.assertEqual(low['total'],0)
        high=calculate_timi_ua_nstemi({
            'age':70,'cad_risk_factor_count':3,'known_coronary_stenosis_ge50':True,
            'st_deviation':True,'severe_angina_ge2_episodes_24h':True,
            'aspirin_last_7d':True,'elevated_cardiac_markers':True
        })
        self.assertEqual(high['total'],7)

    def test_v137_has_bled_explicit_components(self):
        zero=calculate_has_bled({
            'hypertension':False,'abnormal_renal_function':False,'abnormal_liver_function':False,
            'stroke_history':False,'bleeding_history_or_predisposition':False,'labile_inr':False,
            'age_over_65':False,'drugs_predisposing_bleeding':False,'alcohol_use':False
        })
        self.assertEqual(zero['total'],0)
        high=calculate_has_bled({
            'hypertension':True,'abnormal_renal_function':True,'abnormal_liver_function':True,
            'stroke_history':True,'bleeding_history_or_predisposition':True,'labile_inr':True,
            'age_over_65':True,'drugs_predisposing_bleeding':True,'alcohol_use':True
        })
        self.assertEqual(high['total'],9)

    def test_v137_canadian_syncope_source_encoded(self):
        low=calculate_canadian_syncope({
            'predisposition_vasovagal':True,'history_heart_disease':False,
            'any_sbp_below90_or_above180':False,'troponin_above_99pct':False,
            'qrs_axis_deg':0,'qrs_duration_ms':100,'qtc_ms':430,'ed_diagnosis':'vasovagal'
        })
        self.assertEqual(low['total'],-3)
        self.assertEqual(low['risk_band'],'very_low')
        high=calculate_canadian_syncope({
            'predisposition_vasovagal':False,'history_heart_disease':True,
            'any_sbp_below90_or_above180':True,'troponin_above_99pct':True,
            'qrs_axis_deg':120,'qrs_duration_ms':140,'qtc_ms':500,'ed_diagnosis':'cardiac'
        })
        self.assertEqual(high['total'],11)
        self.assertEqual(high['risk_band'],'very_high')

    def test_v137_killip_and_scai_shock_are_structured(self):
        self.assertEqual(calculate_killip_kimball({'state':'no_heart_failure'})['class'],1)
        self.assertEqual(calculate_killip_kimball({'state':'cardiogenic_shock'})['class'],4)

        a=calculate_scai_shock({
            'at_risk_condition':True,'hemodynamic_instability':False,'hypoperfusion':False,
            'initial_support_started':False,'initial_support_failed':False,
            'circulatory_collapse_or_extremis':False
        })
        self.assertEqual(a['stage'],'A')
        b=calculate_scai_shock({
            'at_risk_condition':True,'hemodynamic_instability':True,'hypoperfusion':False,
            'initial_support_started':False,'initial_support_failed':False,
            'circulatory_collapse_or_extremis':False
        })
        self.assertEqual(b['stage'],'B')
        cstage=calculate_scai_shock({
            'at_risk_condition':True,'hemodynamic_instability':True,'hypoperfusion':True,
            'initial_support_started':True,'initial_support_failed':False,
            'circulatory_collapse_or_extremis':False
        })
        self.assertEqual(cstage['stage'],'C')
        dstage=calculate_scai_shock({
            'at_risk_condition':True,'hemodynamic_instability':True,'hypoperfusion':True,
            'initial_support_started':True,'initial_support_failed':True,
            'circulatory_collapse_or_extremis':False
        })
        self.assertEqual(dstage['stage'],'D')
        e=calculate_scai_shock({
            'at_risk_condition':True,'hemodynamic_instability':True,'hypoperfusion':True,
            'initial_support_started':True,'initial_support_failed':True,
            'circulatory_collapse_or_extremis':True
        })
        self.assertEqual(e['stage'],'E')

    def test_v137_central_dispatch_remaining_cardiology(self):
        registry=central_load_registry()
        for sid in ('timi-ua-nstemi','has-bled','canadian-syncope','killip-kimball','scai-shock'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('timi-ua-nstemi',{
            'age':70,'cad_risk_factor_count':3,'known_coronary_stenosis_ge50':True,
            'st_deviation':True,'severe_angina_ge2_episodes_24h':True,
            'aspirin_last_7d':True,'elevated_cardiac_markers':True
        })
        self.assertEqual(result['total'],7)

    def test_v137_revised_geneva_source_encoded(self):
        low=calculate_revised_geneva({
            'age':50,'previous_dvt_pe':False,'surgery_ga_or_lower_limb_fracture_1mo':False,
            'active_cancer':False,'unilateral_lower_limb_pain':False,'hemoptysis':False,
            'heart_rate_bpm':70,'deep_vein_palpation_pain_and_unilateral_edema':False
        })
        self.assertEqual(low['total'],0)
        self.assertEqual(low['risk_group'],'low')
        high=calculate_revised_geneva({
            'age':70,'previous_dvt_pe':True,'surgery_ga_or_lower_limb_fracture_1mo':True,
            'active_cancer':True,'unilateral_lower_limb_pain':True,'hemoptysis':True,
            'heart_rate_bpm':100,'deep_vein_palpation_pain_and_unilateral_edema':True
        })
        self.assertEqual(high['total'],22)
        self.assertEqual(high['risk_group'],'high')

    def test_v137_pesi_and_spesi_source_encoded(self):
        pesi=calculate_pesi({
            'age':50,'sex':'female','cancer':False,'heart_failure':False,
            'chronic_lung_disease':False,'heart_rate_bpm':80,'systolic_bp_mmHg':120,
            'respiratory_rate':20,'temperature_c':37,'altered_mental_status':False,
            'spo2_percent':95
        })
        self.assertEqual(pesi['total'],50)
        self.assertEqual(pesi['class'],'I')

        spesi=calculate_spesi({
            'age':81,'cancer':True,'chronic_cardiopulmonary_disease':True,
            'heart_rate_bpm':110,'systolic_bp_mmHg':99,'spo2_percent':89
        })
        self.assertEqual(spesi['total'],6)
        self.assertFalse(spesi['low_risk'])

    def test_v137_hestia_source_encoded(self):
        all_no={k:False for k in (
            'hemodynamically_unstable','thrombolysis_or_embolectomy_needed',
            'active_bleeding_or_high_bleeding_risk','oxygen_gt24h_to_keep_spo2_gt90',
            'pe_diagnosed_during_anticoagulation','iv_pain_medication_gt24h',
            'medical_or_social_reason_hospital_gt24h','creatinine_clearance_lt30',
            'severe_liver_impairment','pregnant','history_heparin_induced_thrombocytopenia'
        )}
        neg=calculate_hestia(all_no)
        self.assertTrue(neg['hestia_negative'])
        pos=calculate_hestia({**all_no,'creatinine_clearance_lt30':True})
        self.assertFalse(pos['hestia_negative'])
        self.assertEqual(pos['positive_count'],1)

    def test_v137_wells_dvt_source_encoded(self):
        low=calculate_wells_dvt({
            'active_cancer':False,'paralysis_paresis_or_recent_cast':False,
            'bedridden_ge3d_or_major_surgery_12w':False,'localized_deep_vein_tenderness':False,
            'entire_leg_swollen':False,'calf_swelling_ge3cm':False,
            'pitting_edema_symptomatic_leg':False,'collateral_superficial_nonvaricose_veins':False,
            'previous_dvt':False,'alternative_diagnosis_at_least_as_likely':True
        })
        self.assertEqual(low['total'],-2)
        self.assertEqual(low['two_level_probability'],'dvt_unlikely')

        high=calculate_wells_dvt({
            'active_cancer':True,'paralysis_paresis_or_recent_cast':True,
            'bedridden_ge3d_or_major_surgery_12w':True,'localized_deep_vein_tenderness':True,
            'entire_leg_swollen':True,'calf_swelling_ge3cm':True,
            'pitting_edema_symptomatic_leg':True,'collateral_superficial_nonvaricose_veins':True,
            'previous_dvt':True,'alternative_diagnosis_at_least_as_likely':False
        })
        self.assertEqual(high['total'],9)
        self.assertEqual(high['two_level_probability'],'dvt_likely')

    def test_v137_central_dispatch_remaining_tev(self):
        registry=central_load_registry()
        for sid in ('revised-geneva','pesi','spesi','hestia','wells-dvt'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('spesi',{
            'age':50,'cancer':False,'chronic_cardiopulmonary_disease':False,
            'heart_rate_bpm':80,'systolic_bp_mmHg':120,'spo2_percent':95
        })
        self.assertEqual(result['total'],0)

    def test_v137_crb65_source_encoded(self):
        low=calculate_crb65({
            'confusion':False,'respiratory_rate':20,
            'systolic_bp_mmHg':120,'diastolic_bp_mmHg':70,'age':64
        })
        self.assertEqual(low['total'],0)
        high=calculate_crb65({
            'confusion':True,'respiratory_rate':30,
            'systolic_bp_mmHg':89,'diastolic_bp_mmHg':60,'age':65
        })
        self.assertEqual(high['total'],4)

    def test_v137_psi_port_two_step(self):
        class_i=calculate_psi_port({
            'age':45,'sex':'male','nursing_home':False,
            'neoplastic_disease':False,'liver_disease':False,'heart_failure':False,
            'cerebrovascular_disease':False,'renal_disease':False,
            'altered_mental_status':False,'respiratory_rate':20,
            'systolic_bp_mmHg':120,'temperature_c':37,'heart_rate_bpm':80
        })
        self.assertEqual(class_i['risk_class'],'I')
        self.assertTrue(class_i['step1_class_i'])

        class_v=calculate_psi_port({
            'age':90,'sex':'male','nursing_home':True,
            'neoplastic_disease':True,'liver_disease':True,'heart_failure':True,
            'cerebrovascular_disease':True,'renal_disease':True,
            'altered_mental_status':True,'respiratory_rate':35,
            'systolic_bp_mmHg':80,'temperature_c':34,'heart_rate_bpm':130,
            'arterial_ph':7.2,'bun_mg_dL':35,'sodium_mmol_L':125,
            'glucose_mg_dL':300,'hematocrit_percent':25,'pao2_mmHg':50,
            'pleural_effusion':True
        })
        self.assertEqual(class_v['risk_class'],'V')
        self.assertGreater(class_v['score'],130)

    def test_v137_decaf_source_encoded(self):
        low=calculate_decaf({
            'emrcd_category':'below_5a','eosinophils_10e9_L':0.1,
            'consolidation':False,'arterial_ph':7.4,'atrial_fibrillation':False
        })
        self.assertEqual(low['total'],0)
        high=calculate_decaf({
            'emrcd_category':'5b','eosinophils_10e9_L':0.01,
            'consolidation':True,'arterial_ph':7.2,'atrial_fibrillation':True
        })
        self.assertEqual(high['total'],6)
        self.assertEqual(high['risk_band'],'high_3_6')

    def test_v137_berlin_ards_is_explicitly_2012(self):
        mild=classify_berlin_ards({
            'within_1_week':True,
            'bilateral_opacities_not_explained_by_effusions_collapse_nodules':True,
            'respiratory_failure_not_fully_explained_by_cardiac_failure_or_fluid_overload':True,
            'pao2_fio2_mmHg':250,'peep_or_cpap_cmH2O':5
        })
        self.assertTrue(mild['meets_berlin_ards'])
        self.assertEqual(mild['severity'],'mild')
        self.assertEqual(mild['version'],'Berlin 2012')

        no_ards=classify_berlin_ards({
            'within_1_week':True,
            'bilateral_opacities_not_explained_by_effusions_collapse_nodules':True,
            'respiratory_failure_not_fully_explained_by_cardiac_failure_or_fluid_overload':True,
            'pao2_fio2_mmHg':250,'peep_or_cpap_cmH2O':4
        })
        self.assertFalse(no_ards['meets_berlin_ards'])

    def test_v137_rox_scale_aliases_central_formula(self):
        result=central_calculate_scale('rox-index',{
            'SpO2_percent':96,'FiO2_fraction':0.4,'RR':24
        })
        self.assertAlmostEqual(result['value'],10.0)
        self.assertEqual(result['formula_alias'],'rox')
        registry=central_load_registry()
        item=next(x for x in registry['scales'] if x['id']=='rox-index')
        self.assertEqual(item['implementation_status'],'central_formula_alias')

    def test_v137_rts_and_iss_boundaries(self):
        best=calculate_rts({'gcs':15,'systolic_bp_mmHg':120,'respiratory_rate':18})
        self.assertAlmostEqual(best['value'],7.8408,places=4)
        worst=calculate_rts({'gcs':3,'systolic_bp_mmHg':0,'respiratory_rate':0})
        self.assertEqual(worst['value'],0)

        iss0=calculate_iss({'highest_ais_by_region':{
            'head_neck':0,'face':0,'chest':0,'abdomen_pelvic_contents':0,
            'extremities_pelvic_girdle':0,'external':0}})
        self.assertEqual(iss0['total'],0)
        iss75=calculate_iss({'highest_ais_by_region':{
            'head_neck':6,'face':0,'chest':0,'abdomen_pelvic_contents':0,
            'extremities_pelvic_girdle':0,'external':0}})
        self.assertEqual(iss75['total'],75)

    def test_v137_abc_massive_transfusion_boundaries(self):
        low=calculate_abc_massive_transfusion({
            'penetrating_mechanism':False,'positive_fast':False,
            'systolic_bp_mmHg':110,'heart_rate_bpm':90})
        self.assertEqual(low['total'],0)
        high=calculate_abc_massive_transfusion({
            'penetrating_mechanism':True,'positive_fast':True,
            'systolic_bp_mmHg':80,'heart_rate_bpm':130})
        self.assertEqual(high['total'],4)
        self.assertTrue(high['abc_positive_ge2'])

    def test_v137_canadian_ct_head_requires_eligible_population(self):
        with self.assertRaisesRegex(ValueError,'eligible'):
            calculate_canadian_ct_head({
                'eligible_minor_head_injury':False,'age':40,'gcs_at_2h':15,
                'suspected_open_or_depressed_skull_fracture':False,
                'basal_skull_fracture_sign':False,'vomiting_episodes':0,
                'retrograde_amnesia_minutes':0,'dangerous_mechanism':False})
        result=calculate_canadian_ct_head({
            'eligible_minor_head_injury':True,'age':70,'gcs_at_2h':15,
            'suspected_open_or_depressed_skull_fracture':False,
            'basal_skull_fracture_sign':False,'vomiting_episodes':0,
            'retrograde_amnesia_minutes':0,'dangerous_mechanism':False})
        self.assertTrue(result['ct_indicated_by_rule'])
        self.assertTrue(result['high_risk']['age_ge65'])

    def test_v137_canadian_cspine_and_nexus_eligibility(self):
        csp=calculate_canadian_cspine({
            'eligible_alert_stable_gcs15':True,'age':30,'dangerous_mechanism':False,
            'paresthesias_extremities':False,'simple_rear_end_mvc':True,
            'sitting_position_ed':True,'ambulatory_any_time':True,
            'delayed_neck_pain':True,'midline_cspine_tenderness':False,
            'can_rotate_45_left_and_right':True})
        self.assertEqual(csp['decision'],'no_imaging_by_rule')

        nexus=calculate_nexus_cspine({
            'eligible_blunt_cspine_assessment':True,
            'midline_cervical_tenderness':False,'focal_neurologic_deficit':False,
            'normal_alertness':True,'intoxication':False,'painful_distracting_injury':False})
        self.assertTrue(nexus['nexus_low_risk'])
        self.assertFalse(nexus['imaging_indicated_by_rule'])

    def test_v137_central_dispatch_trauma_core(self):
        registry=central_load_registry()
        for sid in ('rts','iss','abc-massive-transfusion','canadian-ct-head','canadian-cspine','nexus-cspine'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('abc-massive-transfusion',{
            'penetrating_mechanism':True,'positive_fast':True,
            'systolic_bp_mmHg':80,'heart_rate_bpm':130})
        self.assertEqual(result['total'],4)

    def test_v137_aims65_and_bisap_boundaries(self):
        aims0=calculate_aims65({
            'albumin_g_dL':3.5,'inr':1.0,'altered_mental_status':False,
            'systolic_bp_mmHg':120,'age':60})
        self.assertEqual(aims0['total'],0)
        aims5=calculate_aims65({
            'albumin_g_dL':2.5,'inr':2.0,'altered_mental_status':True,
            'systolic_bp_mmHg':90,'age':70})
        self.assertEqual(aims5['total'],5)

        bisap0=calculate_bisap({
            'bun_mg_dL':20,'impaired_mental_status':False,'sirs':False,
            'age':50,'pleural_effusion':False})
        self.assertEqual(bisap0['total'],0)
        bisap5=calculate_bisap({
            'bun_mg_dL':30,'impaired_mental_status':True,'sirs':True,
            'age':70,'pleural_effusion':True})
        self.assertEqual(bisap5['total'],5)

    def test_v137_child_pugh_source_encoded(self):
        a=calculate_child_pugh({
            'bilirubin_mg_dL':1.0,'albumin_g_dL':4.0,'inr':1.2,
            'ascites':'none','encephalopathy_grade':0})
        self.assertEqual(a['total'],5)
        self.assertEqual(a['class'],'A')
        cscore=calculate_child_pugh({
            'bilirubin_mg_dL':4.0,'albumin_g_dL':2.5,'inr':2.5,
            'ascites':'moderate_severe_or_refractory','encephalopathy_grade':4})
        self.assertEqual(cscore['total'],15)
        self.assertEqual(cscore['class'],'C')

    def test_v137_kings_college_paracetamol_and_non_paracetamol(self):
        para=calculate_kings_college({
            'paracetamol_related':True,
            'arterial_ph_after_resuscitation':7.25,'hours_since_ingestion':30,
            'lactate_mmol_L_after_resuscitation':2.0,'encephalopathy_grade':2,
            'creatinine_umol_L':150,'inr':2.0})
        self.assertTrue(para['meets_criteria'])
        self.assertTrue(para['criteria']['ph_lt7_3_after_resuscitation_and_gt24h'])

        nonpara=calculate_kings_college({
            'paracetamol_related':False,'inr':4.0,'age':45,
            'unfavorable_etiology':True,'jaundice_to_encephalopathy_days':10,
            'bilirubin_umol_L':350})
        self.assertTrue(nonpara['meets_criteria'])
        self.assertGreaterEqual(nonpara['five_factor_count'],3)

        low=calculate_kings_college({
            'paracetamol_related':False,'inr':2.0,'age':30,
            'unfavorable_etiology':False,'jaundice_to_encephalopathy_days':3,
            'bilirubin_umol_L':100})
        self.assertFalse(low['meets_criteria'])

    def test_v137_hepatology_formula_aliases_no_duplicate_math(self):
        maddrey=central_calculate_scale('maddrey',{
            'PT_patient':20,'PT_control':12,'bilirubin_mg_dL':10})
        self.assertAlmostEqual(maddrey['value'],46.8)
        self.assertEqual(maddrey['formula_alias'],'maddrey-formula')

        with self.assertRaisesRegex(ValueError,'legacy MELD-Na'):
            central_calculate_scale('meld-na',{
                'bilirubin_mg_dL':2,'INR':1.5,'creatinine_mg_dL':1.2,
                'sodium_mmol_L':130})

    def test_v137_central_dispatch_digestive_hepatology(self):
        registry=central_load_registry()
        expected={
            'aims65':'dedicated_source_encoded_v1','bisap':'dedicated_source_encoded_v1',
            'child-pugh':'dedicated_source_encoded_v1','kings-college':'dedicated_source_encoded_v1',
            'meld-na':'central_formula_alias','maddrey':'central_formula_alias'}
        for sid,status in expected.items():
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],status)
        result=central_calculate_scale('child-pugh',{
            'bilirubin_mg_dL':1.0,'albumin_g_dL':4.0,'inr':1.2,
            'ascites':'none','encephalopathy_grade':0})
        self.assertEqual(result['class'],'A')

    def test_v137_qsofa_and_isth_dic(self):
        q=calculate_qsofa({'respiratory_rate':22,'systolic_bp_mmHg':100,'altered_mentation':True})
        self.assertEqual(q['total'],3)
        with self.assertRaisesRegex(ValueError,'DIC-associated'):
            calculate_isth_dic({'dic_associated_disorder':False,'platelets_10e9_L':40,
                'fibrin_marker_multiple_uln':6,'pt_prolongation_seconds':7,'fibrinogen_mg_dL':80})
        dic=calculate_isth_dic({'dic_associated_disorder':True,'platelets_10e9_L':40,
            'fibrin_marker_multiple_uln':6,'pt_prolongation_seconds':7,'fibrinogen_mg_dL':80})
        self.assertEqual(dic['total'],8)
        self.assertTrue(dic['overt_dic_score_ge5'])

    def test_v137_kdigo_aki_stages(self):
        stage0=classify_kdigo_aki({
            'current_creatinine_mg_dL':1.0,'baseline_creatinine_mg_dL':1.0,
            'creatinine_increase_mg_dL_48h':0,'urine_ml_kg_h':1.0,'urine_duration_h':6,
            'rrt_started':False})
        self.assertEqual(stage0['stage'],0)
        stage1=classify_kdigo_aki({
            'current_creatinine_mg_dL':1.3,'baseline_creatinine_mg_dL':1.0,
            'creatinine_increase_mg_dL_48h':0.3,'urine_ml_kg_h':0.4,'urine_duration_h':8,
            'rrt_started':False})
        self.assertEqual(stage1['stage'],1)
        stage3=classify_kdigo_aki({
            'current_creatinine_mg_dL':4.2,'baseline_creatinine_mg_dL':1.0,
            'creatinine_increase_mg_dL_48h':1.0,'urine_ml_kg_h':0.2,'urine_duration_h':24,
            'rrt_started':False})
        self.assertEqual(stage3['stage'],3)

    def test_v137_mcmahon_boundaries(self):
        low=calculate_mcmahon({
            'age':40,'sex':'male','creatinine_mg_dL':1.0,'calcium_mg_dL':9,
            'ck_u_L':10000,'etiology_low_risk_group':True,'phosphate_mg_dL':3,
            'bicarbonate_mEq_L':24})
        self.assertEqual(low['total'],0)
        high=calculate_mcmahon({
            'age':85,'sex':'female','creatinine_mg_dL':3,'calcium_mg_dL':7,
            'ck_u_L':50000,'etiology_low_risk_group':False,'phosphate_mg_dL':6,
            'bicarbonate_mEq_L':15})
        self.assertEqual(high['total'],19)
        self.assertTrue(high['higher_risk_ge6'])

    def test_v137_alvarado_and_air_boundaries(self):
        alv=calculate_alvarado({
            'migration_rlq':True,'anorexia':True,'nausea_or_vomiting':True,
            'rlq_tenderness':True,'rebound_or_percussion_tenderness':True,
            'temperature_c':38,'wbc_10e9_L':12,'neutrophil_left_shift':True})
        self.assertEqual(alv['total'],10)
        self.assertEqual(alv['risk_band'],'high_9_10')

        air=calculate_air({
            'vomiting':True,'right_iliac_fossa_pain':True,
            'guarding_rebound_severity':'strong','temperature_c':39,
            'wbc_10e9_L':16,'neutrophils_percent':90,'crp_mg_L':60})
        self.assertEqual(air['total'],12)
        self.assertEqual(air['risk_band'],'high_9_12')

    def test_v137_central_dispatch_mixed_block(self):
        registry=central_load_registry()
        for sid in ('qsofa','isth-dic','kdigo-aki','mcmahon-rhabdo','alvarado','air-appendicitis'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('qsofa',{
            'respiratory_rate':22,'systolic_bp_mmHg':100,'altered_mentation':True})
        self.assertEqual(result['total'],3)

    def test_v137_toxicology_core_rules(self):
        rumack=evaluate_rumack_matthew({
            'single_acute_ingestion_known_time':True,'hours_since_ingestion':4,
            'acetaminophen_mcg_mL':150,'extended_release_or_delayed_absorption':False})
        self.assertTrue(rumack['at_or_above_treatment_line'])
        with self.assertRaises(ValueError):
            evaluate_rumack_matthew({
                'single_acute_ingestion_known_time':False,'hours_since_ingestion':4,
                'acetaminophen_mcg_mL':150,'extended_release_or_delayed_absorption':False})

        hunter=evaluate_hunter_serotonin({
            'serotonergic_exposure':True,'spontaneous_clonus':False,
            'inducible_clonus':False,'ocular_clonus':False,'agitation':False,
            'diaphoresis':False,'tremor':True,'hyperreflexia':True,
            'hypertonia':False,'temperature_c':37})
        self.assertTrue(hunter['criteria_met'])

    def test_v137_ciwa_ar_and_cows_explicit_items(self):
        ciwa_items={k:0 for k in __import__('core_scores_block13_toxicology').CIWA_MAX}
        ciwa=calculate_ciwa_ar({'items':ciwa_items})
        self.assertEqual(ciwa['total'],0)
        ciwa_max=dict(__import__('core_scores_block13_toxicology').CIWA_MAX)
        self.assertEqual(calculate_ciwa_ar({'items':ciwa_max})['total'],67)

        cows_items={k:min(v) for k,v in __import__('core_scores_block13_toxicology').COWS_ALLOWED.items()}
        self.assertEqual(calculate_cows({'items':cows_items})['total'],0)
        cows_max={k:max(v) for k,v in __import__('core_scores_block13_toxicology').COWS_ALLOWED.items()}
        self.assertEqual(calculate_cows({'items':cows_max})['total'],48)

    def test_v137_central_dispatch_toxicology_core(self):
        registry=central_load_registry()
        for sid in ('rumack-matthew','hunter-serotonin','ciwa-ar','cows'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')
        result=central_calculate_scale('hunter-serotonin',{
            'serotonergic_exposure':True,'spontaneous_clonus':True,
            'inducible_clonus':False,'ocular_clonus':False,'agitation':False,
            'diaphoresis':False,'tremor':False,'hyperreflexia':False,
            'hypertonia':False,'temperature_c':37})
        self.assertTrue(result['criteria_met'])

    def test_v137_oakland_source_encoded_boundaries(self):
        low = calculate_oakland({
            'age':30,'sex':'female','previous_lgib_admission':False,'dre_blood':False,
            'heart_rate_bpm':60,'systolic_bp_mmHg':170,'hemoglobin_g_dL':16
        })
        self.assertEqual(low['total'],0)
        self.assertTrue(low['low_risk_original_threshold_le_8'])

        high = calculate_oakland({
            'age':75,'sex':'male','previous_lgib_admission':True,'dre_blood':True,
            'heart_rate_bpm':120,'systolic_bp_mmHg':80,'hemoglobin_g_dL':5
        })
        self.assertEqual(high['total'],35)
        self.assertFalse(high['low_risk_original_threshold_le_8'])

        with self.assertRaises(ValueError):
            calculate_oakland({
                'age':75,'sex':'male','previous_lgib_admission':True,'dre_blood':True,
                'heart_rate_bpm':120,'systolic_bp_mmHg':40,'hemoglobin_g_dL':5
            })

    def test_v137_revised_baux_and_obstetric_shock_index(self):
        baux = calculate_revised_baux({
            'age':50,'tbsa_percent':30,'inhalation_injury':True
        })
        self.assertEqual(baux['value'],97)

        osi = calculate_obstetric_shock_index({
            'heart_rate_bpm':120,'systolic_bp_mmHg':100
        })
        self.assertAlmostEqual(osi['value'],1.2)
        self.assertIn('not use a single cutoff',osi['warning'])

    def test_v137_formula_alias_scales_reuse_central_engine(self):
        si = central_calculate_scale('shock-index', {'HR':120,'SBP':100})
        self.assertAlmostEqual(si['value'],1.2)
        self.assertEqual(si['formula_alias'],'shock-index-formula')

        msi = central_calculate_scale('modified-shock-index', {'HR':120,'MAP':80})
        self.assertAlmostEqual(msi['value'],1.5)

        rox = central_calculate_scale('rox-index', {
            'SpO2_percent':95,'FiO2_fraction':0.5,'RR':20
        })
        self.assertAlmostEqual(rox['value'],9.5)

        maddrey = central_calculate_scale('maddrey', {
            'PT_patient':20,'PT_control':12,'bilirubin_mg_dL':10
        })
        self.assertAlmostEqual(maddrey['value'],46.8)

        with self.assertRaisesRegex(ValueError,'legacy MELD-Na'):
            central_calculate_scale('meld-na', {
                'bilirubin_mg_dL':2,'INR':1.5,'creatinine_mg_dL':1.2,'sodium_mmol_L':130
            })

    def test_v137_registry_marks_adult_core_block5_implemented(self):
        registry=central_load_registry()
        expected={
            'oakland':'dedicated_source_encoded_v1',
            'obstetric-shock-index':'dedicated_source_encoded_v1',
            'revised-baux':'dedicated_source_encoded_v1',
            'shock-index':'central_formula_alias',
            'modified-shock-index':'central_formula_alias',
            'rox-index':'central_formula_alias',
            'maddrey':'central_formula_alias',
            'meld-na':'central_formula_alias',
        }
        for sid,status in expected.items():
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],status)

    def test_v137_bishop_score_boundaries(self):
        low = calculate_bishop({
            'dilation_cm':0,'effacement_band':'0_30','station':-3,
            'consistency':'firm','position':'posterior'
        })
        self.assertEqual(low['total'],0)

        high = calculate_bishop({
            'dilation_cm':6,'effacement_band':'80_plus','station':2,
            'consistency':'soft','position':'anterior'
        })
        self.assertEqual(high['total'],13)

        with self.assertRaises(ValueError):
            calculate_bishop({
                'dilation_cm':2,'effacement_band':'35','station':-2,
                'consistency':'medium','position':'mid'
            })

    def test_v137_meows_nnuh_v7_boundaries(self):
        normal = calculate_meows_nnuh_v7({
            'temperature_c':36.8,'systolic_bp_mmHg':120,'diastolic_bp_mmHg':70,
            'pulse_bpm':80,'respiratory_rate':16,'spo2_percent':98,
            'avpu':'A','urine_output_mL_h':50
        })
        self.assertEqual(normal['total'],0)
        self.assertEqual(normal['action_band'],'routine_observation')

        severe = calculate_meows_nnuh_v7({
            'temperature_c':39.0,'systolic_bp_mmHg':160,'diastolic_bp_mmHg':110,
            'pulse_bpm':130,'respiratory_rate':30,'spo2_percent':94,
            'avpu':'U','urine_output_mL_h':5
        })
        self.assertEqual(severe['total'],24)
        self.assertTrue(severe['single_parameter_score_3'])
        self.assertEqual(severe['action_band'],'call_out_cascade')

        community = calculate_meows_nnuh_v7({
            'temperature_c':36.8,'systolic_bp_mmHg':120,'diastolic_bp_mmHg':70,
            'pulse_bpm':80,'respiratory_rate':16,'avpu':'A',
            'community_without_spo2':True
        })
        self.assertIsNone(community['components']['spo2'])
        self.assertFalse(community['spo2_measured'])

    def test_v137_rule_of_nines_adult_full_body_equals_100(self):
        fractions = {
            'head_neck':1,'left_upper_limb':1,'right_upper_limb':1,
            'anterior_trunk':1,'posterior_trunk':1,
            'left_lower_limb':1,'right_lower_limb':1,'perineum':1
        }
        result = calculate_rule_of_nines({'fractions':fractions})
        self.assertAlmostEqual(result['tbsa_percent'],100.0)

        partial = calculate_rule_of_nines({'fractions':{'left_upper_limb':0.5}})
        self.assertAlmostEqual(partial['tbsa_percent'],4.5)

    def test_v137_lund_browder_age_adjustment_and_full_body_check(self):
        infant = calculate_lund_browder({
            'age_years':0.5,
            'fractions':{}
        })
        self.assertAlmostEqual(infant['full_body_check_percent'],100.0)

        adult = calculate_lund_browder({
            'age_years':30,
            'fractions':{}
        })
        self.assertAlmostEqual(adult['full_body_check_percent'],100.0)

        head_only = calculate_lund_browder({
            'age_years':0.5,
            'fractions':{'head_anterior':1,'head_posterior':1}
        })
        self.assertAlmostEqual(head_only['tbsa_percent'],19.0)

        adult_head = calculate_lund_browder({
            'age_years':30,
            'fractions':{'head_anterior':1,'head_posterior':1}
        })
        self.assertAlmostEqual(adult_head['tbsa_percent'],9.0)

    def test_v137_central_dispatch_obstetric_burn_tools(self):
        registry=central_load_registry()
        for sid in ('bishop','meows','rule-of-nines','lund-browder'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')

        result=central_calculate_scale('bishop',{
            'dilation_cm':0,'effacement_band':'0_30','station':-3,
            'consistency':'firm','position':'posterior'
        })
        self.assertEqual(result['total'],0)
        self.assertEqual(result['registry_id'],'bishop')

    def test_v137_bedside_pews_zero_and_max(self):
        zero = calculate_bedside_pews({
            'age_months':24,'heart_rate_bpm':100,'systolic_bp_mmHg':100,
            'capillary_refill_seconds':2,'respiratory_rate':30,
            'respiratory_effort':'normal','spo2_percent':98,
            'oxygen_support_level':'room_air'
        })
        self.assertEqual(zero['total'],0)
        self.assertEqual(zero['range'],[0,26])

        maximum = calculate_bedside_pews({
            'age_months':2,'heart_rate_bpm':190,'systolic_bp_mmHg':40,
            'capillary_refill_seconds':3,'respiratory_rate':95,
            'respiratory_effort':'severe','spo2_percent':85,
            'oxygen_support_level':'high'
        })
        self.assertEqual(maximum['total'],26)

    def test_v137_pediatric_trauma_score_boundaries(self):
        maximum = calculate_pediatric_trauma_score({
            'weight_kg':25,'airway':'normal','systolic_bp_mmHg':100,
            'cns':'awake','open_wound':'none','skeletal':'none'
        })
        self.assertEqual(maximum['total'],12)
        self.assertFalse(maximum['high_risk_common_threshold_le_8'])

        minimum = calculate_pediatric_trauma_score({
            'weight_kg':5,'airway':'unmaintainable','systolic_bp_mmHg':40,
            'cns':'coma_or_decerebrate','open_wound':'major_or_penetrating',
            'skeletal':'open_or_multiple_fractures'
        })
        self.assertEqual(minimum['total'],-6)
        self.assertTrue(minimum['high_risk_common_threshold_le_8'])

    def test_v137_sipa_age_adjusted_thresholds(self):
        a = calculate_sipa({'age_years':5,'heart_rate_bpm':123,'systolic_bp_mmHg':100})
        self.assertTrue(a['elevated'])
        self.assertEqual(a['age_adjusted_threshold'],1.22)
        b = calculate_sipa({'age_years':10,'heart_rate_bpm':100,'systolic_bp_mmHg':100})
        self.assertFalse(b['elevated'])
        self.assertEqual(b['age_adjusted_threshold'],1.0)
        c = calculate_sipa({'age_years':14,'heart_rate_bpm':91,'systolic_bp_mmHg':100})
        self.assertTrue(c['elevated'])
        with self.assertRaises(ValueError):
            calculate_sipa({'age_years':3,'heart_rate_bpm':100,'systolic_bp_mmHg':100})

    def test_v137_flacc_wong_baker_pain_tools(self):
        flacc = calculate_flacc({
            'face':'frequent_frown_clenched_jaw','legs':'kicking_or_drawn_up',
            'activity':'arched_rigid_jerking','cry':'steady_cry_screams_sobs',
            'consolability':'difficult_to_console'
        })
        self.assertEqual(flacc['total'],10)
        self.assertEqual(flacc['band'],'severe_7_10')

        wrapper = prepare_wong_baker({'authorized_official_scale_used':False})
        self.assertEqual(wrapper['status'],'official_licensed_scale_required')
        authorized = prepare_wong_baker({
            'authorized_official_scale_used':True,'age_years':5,
            'patient_self_report_capable':True,'patient_selected_score':8
        })
        self.assertEqual(authorized['score'],8)
        with self.assertRaisesRegex(ValueError,'self-assessment'):
            prepare_wong_baker({
                'authorized_official_scale_used':True,'age_years':5,
                'patient_self_report_capable':False,'patient_selected_score':8
            })

    def test_v137_pram_and_westley_boundaries(self):
        pram = calculate_pram({
            'spo2_percent':90,'suprasternal_retraction':True,
            'scalene_contraction':True,'air_entry':'minimal_or_absent',
            'wheezing':'audible_or_silent_chest'
        })
        self.assertEqual(pram['total'],12)
        self.assertEqual(pram['severity_band'],'severe_8_12')

        westley = calculate_westley_croup({
            'stridor':'at_rest','retractions':'severe','air_entry':'markedly_decreased',
            'cyanosis':'at_rest','consciousness':'disoriented'
        })
        self.assertEqual(westley['total'],17)
        self.assertEqual(westley['severity_band'],'impending_respiratory_failure')

    def test_v137_clinical_dehydration_and_pediatric_appendicitis(self):
        cds = calculate_clinical_dehydration({
            'general_appearance':'drowsy_limp_cold_sweaty_comatose',
            'eyes':'very_sunken','mucous_membranes':'dry','tears':'absent'
        })
        self.assertEqual(cds['total'],8)
        self.assertEqual(cds['classification'],'moderate_severe_5_8')

        pas = calculate_pediatric_appendicitis({
            'migration_pain':True,'anorexia':True,'nausea_vomiting':True,'fever':True,
            'rlq_tenderness':True,'cough_percussion_hopping_tenderness':True,
            'leukocytosis':True,'neutrophilia':True
        })
        self.assertEqual(pas['total'],10)

    def test_v137_pecarn_head_injury_age_bands(self):
        infant_low = classify_pecarn_head_injury({
            'age_years':1,'altered_mental_status':False,'gcs':15,'severe_mechanism':False,
            'palpable_skull_fracture':False,'nonfrontal_scalp_hematoma':False,
            'loc_seconds':0,'acting_normally_parent':True
        })
        self.assertEqual(infant_low['classification'],'very_low_risk_ciTBI')

        infant_high = classify_pecarn_head_injury({
            'age_years':1,'altered_mental_status':False,'gcs':15,'severe_mechanism':False,
            'palpable_skull_fracture':True,'nonfrontal_scalp_hematoma':False,
            'loc_seconds':0,'acting_normally_parent':True
        })
        self.assertEqual(infant_high['classification'],'higher_risk_ct_recommended_pathway')

        older_low = classify_pecarn_head_injury({
            'age_years':10,'altered_mental_status':False,'gcs':15,'severe_mechanism':False,
            'basilar_skull_fracture_signs':False,'loss_of_consciousness':False,
            'vomiting':False,'severe_headache':False
        })
        self.assertEqual(older_low['classification'],'very_low_risk_ciTBI')

    def test_v137_febrile_infant_rules_boundaries(self):
        pecarn = classify_pecarn_febrile_infant({
            'age_days':45,'well_appearing':True,'urinalysis_negative':True,
            'anc_per_uL':4090,'procalcitonin_ng_mL':1.71
        })
        self.assertTrue(pecarn['low_risk_sbi'])

        pecarn_not = classify_pecarn_febrile_infant({
            'age_days':45,'well_appearing':True,'urinalysis_negative':True,
            'anc_per_uL':4091,'procalcitonin_ng_mL':1.71
        })
        self.assertFalse(pecarn_not['low_risk_sbi'])

        step_low = classify_step_by_step({
            'age_days':30,'well_appearing':True,'leukocyturia':False,
            'procalcitonin_ng_mL':0.49,'crp_mg_L':20,'anc_per_uL':10000
        })
        self.assertEqual(step_low['classification'],'low_risk')

        step_high = classify_step_by_step({
            'age_days':21,'well_appearing':True,'leukocyturia':False,
            'procalcitonin_ng_mL':0.1,'crp_mg_L':1,'anc_per_uL':1000
        })
        self.assertEqual(step_high['classification'],'high_risk_age_le_21d')

        step_intermediate = classify_step_by_step({
            'age_days':30,'well_appearing':True,'leukocyturia':False,
            'procalcitonin_ng_mL':0.1,'crp_mg_L':21,'anc_per_uL':1000
        })
        self.assertEqual(step_intermediate['classification'],'intermediate_risk')

    def test_v137_apgar_zero_ten_and_repeat_rule(self):
        zero = calculate_apgar({
            'time_minutes':1,'heart_rate_bpm':0,'respiratory_effort':'absent',
            'muscle_tone':'flaccid','reflex_irritability':'no_response','color':'blue_or_pale'
        })
        self.assertEqual(zero['total'],0)

        ten = calculate_apgar({
            'time_minutes':5,'heart_rate_bpm':120,'respiratory_effort':'good_crying',
            'muscle_tone':'active_motion','reflex_irritability':'cry_cough_sneeze_withdrawal',
            'color':'completely_pink'
        })
        self.assertEqual(ten['total'],10)
        self.assertFalse(ten['repeat_every_5_min_to_20_if_5min_below_7'])

        low5 = calculate_apgar({
            'time_minutes':5,'heart_rate_bpm':80,'respiratory_effort':'slow_irregular_gasping',
            'muscle_tone':'some_flexion','reflex_irritability':'grimace',
            'color':'pink_body_blue_extremities'
        })
        self.assertEqual(low5['total'],5)
        self.assertTrue(low5['repeat_every_5_min_to_20_if_5min_below_7'])

    def test_v137_registry_has_no_pending_core_after_pediatric_rollout(self):
        registry=central_load_registry()
        completed={'dedicated_source_encoded_v1','validated_official_external_wrapper','central_formula_alias'}
        pending=[x['id'] for x in registry['scales'] if x['tier']=='CORE' and x['implementation_status'] not in completed]
        self.assertEqual(pending,[])
        self.assertEqual(len([x for x in registry['scales'] if x['tier']=='SPECIALIST']),41)

    def test_v137_specialist_canadian_tia_score_boundaries(self):
        low = calculate_canadian_tia({
            'first_tia':False,'symptoms_ge_10_min':False,'history_carotid_stenosis':False,
            'on_antiplatelet':False,'gait_disturbance':False,'unilateral_weakness':False,
            'vertigo':True,'diastolic_bp_mmHg':80,'dysarthria_or_aphasia':False,
            'af_on_ecg':False,'infarct_on_ct':False,'platelets_10e9_L':200,'glucose_mmol_L':5
        })
        self.assertEqual(low['total'],-3)
        self.assertEqual(low['risk_tier'],'low')
        high = calculate_canadian_tia({
            'first_tia':True,'symptoms_ge_10_min':True,'history_carotid_stenosis':True,
            'on_antiplatelet':True,'gait_disturbance':True,'unilateral_weakness':True,
            'vertigo':False,'diastolic_bp_mmHg':120,'dysarthria_or_aphasia':True,
            'af_on_ecg':True,'infarct_on_ct':True,'platelets_10e9_L':500,'glucose_mmol_L':20
        })
        self.assertEqual(high['total'],23)
        self.assertEqual(high['risk_tier'],'high')

    def test_v137_specialist_pc_aspects_zero_ten(self):
        regions={k:False for k in (
            'left_thalamus','right_thalamus','left_cerebellum','right_cerebellum',
            'left_pca_territory','right_pca_territory','midbrain','pons'
        )}
        normal=calculate_pc_aspects(regions)
        self.assertEqual(normal['score'],10)
        all_bad=calculate_pc_aspects({k:True for k in regions})
        self.assertEqual(all_bad['score'],0)

    def test_v137_specialist_four_score_zero_sixteen(self):
        maximum=calculate_four_score({
            'eye':'tracking_or_blinking_command','motor':'thumbs_fist_peace',
            'brainstem':'pupil_and_corneal_present','respiration':'regular_not_intubated'
        })
        self.assertEqual(maximum['total'],16)
        minimum=calculate_four_score({
            'eye':'closed_with_pain','motor':'no_response_or_myoclonus',
            'brainstem':'pupil_corneal_cough_absent','respiration':'ventilator_rate_or_apnea'
        })
        self.assertEqual(minimum['total'],0)

    def test_v137_specialist_hunt_hess_wfns(self):
        hh=classify_hunt_hess({'clinical_category':'drowsy_confused_or_mild_focal_deficit'})
        self.assertEqual(hh['grade'],3)
        self.assertEqual(calculate_wfns_sah({'gcs':15,'focal_motor_deficit':False})['grade'],1)
        self.assertEqual(calculate_wfns_sah({'gcs':14,'focal_motor_deficit':False})['grade'],2)
        self.assertEqual(calculate_wfns_sah({'gcs':14,'focal_motor_deficit':True})['grade'],3)
        self.assertEqual(calculate_wfns_sah({'gcs':8,'focal_motor_deficit':True})['grade'],4)
        self.assertEqual(calculate_wfns_sah({'gcs':5,'focal_motor_deficit':False})['grade'],5)

    def test_v137_specialist_stess_and_bms_boundaries(self):
        stess=calculate_stess({
            'age':70,'previous_seizures':False,'consciousness':'comatose','worst_seizure_type':'ncse_in_coma'
        })
        self.assertEqual(stess['total'],6)
        bms=calculate_bacterial_meningitis_score({
            'positive_csf_gram_stain':True,'csf_anc_per_uL':1000,'csf_protein_mg_dL':80,
            'peripheral_anc_per_uL':10000,'seizure_with_illness':True
        })
        self.assertEqual(bms['total'],6)
        self.assertFalse(bms['very_low_risk_if_zero'])
        zero=calculate_bacterial_meningitis_score({
            'positive_csf_gram_stain':False,'csf_anc_per_uL':0,'csf_protein_mg_dL':20,
            'peripheral_anc_per_uL':1000,'seizure_with_illness':False
        })
        self.assertTrue(zero['very_low_risk_if_zero'])

    def test_v137_specialist_neuro_registry_status(self):
        registry=central_load_registry()
        for sid in ('canadian-tia-score','pc-aspects','four-score','hunt-hess','wfns-sah','stess','bacterial-meningitis-score'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')

    def test_v137_specialist_edacs_orbit_tisdale(self):
        edacs=calculate_edacs({
            'age':86,'sex':'male','known_cad_or_age18_50_ge3_risk_factors':True,
            'diaphoresis':True,'radiation':True,'pleuritic':False,'palpation_reproduces':False
        })
        self.assertEqual(edacs['total'],38)
        orbit=calculate_orbit({
            'age':80,'sex':'male','hemoglobin_g_dL':10,'bleeding_history':True,
            'egfr_mL_min_1_73m2':40,'antiplatelet':True
        })
        self.assertEqual(orbit['total'],7)
        tisdale=calculate_tisdale({
            'age':70,'female':True,'loop_diuretic':True,'potassium_mmol_L':3.2,
            'baseline_qtc_ms':470,'acute_mi':True,'qt_prolonging_drug_count':2,
            'heart_failure':True,'sepsis':True
        })
        self.assertEqual(tisdale['total'],21)
        self.assertEqual(tisdale['risk_band'],'high_ge11')

    def test_v137_specialist_bova_sic_mews_sirs(self):
        bova=calculate_bova({
            'systolic_bp_mmHg':95,'troponin_elevated':True,'rv_dysfunction':True,'heart_rate_bpm':120
        })
        self.assertEqual(bova['total'],7)
        self.assertEqual(bova['stage'],'III')
        with self.assertRaises(ValueError):
            calculate_bova({'systolic_bp_mmHg':80,'troponin_elevated':True,'rv_dysfunction':True,'heart_rate_bpm':120})

        sic=calculate_sic({'platelets_10e9_L':80,'pt_inr':1.5,'sofa_four_system_score':2})
        self.assertEqual(sic['total'],6)
        self.assertTrue(sic['sic_positive'])

        mews=calculate_mews({
            'systolic_bp_mmHg':65,'heart_rate_bpm':135,'respiratory_rate':35,'temperature_c':34,'avpu':'U'
        })
        self.assertEqual(mews['total'],14)

        sirs=calculate_sirs({
            'temperature_c':39,'heart_rate_bpm':100,'respiratory_rate':25,'paco2_mmHg':40,
            'wbc_per_uL':13000,'bands_percent':0
        })
        self.assertEqual(sirs['positive_count'],4)
        self.assertTrue(sirs['sirs_ge2'])

    def test_v137_specialist_block2_registry_status(self):
        registry=central_load_registry()
        for sid in ('edacs','orbit-bleeding','tisdale-qt','bova','sic','mews','sirs'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')

    def test_v137_specialist_apache2_and_saps3(self):
        apache=calculate_apache2({
            'temperature_c_core':37,'map_mmHg':80,'heart_rate_bpm':80,'respiratory_rate':16,
            'fio2_fraction':0.21,'pao2_mmHg':90,'arterial_ph':7.4,'sodium_mmol_L':140,
            'potassium_mmol_L':4,'creatinine_mg_dL':1,'acute_renal_failure':False,
            'hematocrit_percent':40,'wbc_10e3_uL':8,'gcs':15,'age':40,
            'severe_chronic_health':False,'admission_type':'nonoperative_or_emergency_postop'
        })
        self.assertEqual(apache['total'],0)
        wrapper=prepare_saps3({'saps3_score':50})
        self.assertEqual(wrapper['score'],50)
        self.assertIsNone(wrapper['mortality_probability'])

    def test_v137_specialist_bps_smartcop_hacor(self):
        bps=calculate_bps({'facial':'grimacing','upper_limbs':'permanently_retracted','ventilation':'unable_to_control_ventilation'})
        self.assertEqual(bps['total'],12)
        smart=calculate_smart_cop({
            'age':40,'systolic_bp_mmHg':80,'multilobar_infiltrates':True,'albumin_g_L':30,
            'respiratory_rate':30,'heart_rate_bpm':130,'confusion':True,'arterial_ph':7.2,'spo2_percent':90
        })
        self.assertEqual(smart['total'],11)
        hacor=calculate_hacor({'heart_rate_bpm':130,'arterial_ph':7.2,'gcs':8,'pao2_fio2':80,'respiratory_rate':50})
        self.assertEqual(hacor['total'],25)

    def test_v137_specialist_age_si_niss_triss_nexus(self):
        asi=calculate_age_shock_index({'age':70,'heart_rate_bpm':100,'systolic_bp_mmHg':100})
        self.assertEqual(asi['value'],70)
        niss=calculate_niss({'ais_injury_scores':[5,4,3,2]})
        self.assertEqual(niss['total'],50)
        lethal=calculate_niss({'ais_injury_scores':[6,1]})
        self.assertEqual(lethal['total'],75)
        triss=calculate_triss({'rts':7.84,'iss':10,'age':30,'trauma_type':'blunt'})
        self.assertGreater(triss['probability_survival_legacy_mtos'],0)
        self.assertLess(triss['probability_survival_legacy_mtos'],1)
        nexus=calculate_nexus_head_ct({
            'skull_fracture':False,'scalp_hematoma':False,'neurologic_deficit':False,
            'abnormal_alertness':False,'abnormal_behavior':False,'persistent_vomiting':False,
            'coagulopathy':False,'age':40
        })
        self.assertTrue(nexus['low_risk_all_absent'])

    def test_v137_specialist_mmrc_and_block3_registry(self):
        self.assertEqual(calculate_mmrc({'grade':4})['grade'],4)
        registry=central_load_registry()
        completed={'dedicated_source_encoded_v1','validated_official_external_wrapper'}
        for sid in ('apache2','saps3','bps','age-shock-index','smart-cop','mmrc','hacor','niss','triss','nexus-head-ct'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertIn(item['implementation_status'],completed)

    def test_v137_specialist_rockall_ranson(self):
        rock=calculate_rockall({
            'age':85,'heart_rate_bpm':120,'systolic_bp_mmHg':80,'comorbidity':'liver_failure',
            'endoscopic_diagnosis':'upper_gi_malignancy','stigmata':'blood_clot_visible_or_spurting_vessel'
        })
        self.assertEqual(rock['total'],11)
        ranson=calculate_ranson({
            'etiology':'non_gallstone','age':60,'wbc_per_uL':17000,'glucose_mg_dL':210,
            'ast_IU_L':300,'ldh_IU_L':400,'calcium_mg_dL_48h':7,
            'hematocrit_fall_percent_48h':11,'bun_rise_mg_dL_48h':6,
            'base_deficit_mEq_L_48h':5,'fluid_sequestration_L_48h':7,'pao2_mmHg_48h':50
        })
        self.assertEqual(ranson['total'],11)

    def test_v137_specialist_meld3_lille(self):
        meld=calculate_meld3({'female':True,'bilirubin_mg_dL':3,'inr':2,'creatinine_mg_dL':1.5,
                              'sodium_mmol_L':130,'albumin_g_dL':2.5})
        self.assertGreaterEqual(meld['score'],6)
        self.assertLessEqual(meld['score'],40)
        lille=calculate_lille({'age':50,'albumin_day0_g_L':30,'bilirubin_day0_umol_L':200,
                              'bilirubin_day7_umol_L':150,'pt_seconds':20,'renal_insufficiency':False})
        self.assertGreaterEqual(lille['score'],0)
        self.assertLessEqual(lille['score'],1)

    def test_v137_specialist_poisoning_pawss(self):
        pss=classify_poisoning_severity({'grade':3})
        self.assertEqual(pss['label'],'severe')
        pawss=calculate_pawss({
            'threshold_recent_alcohol_or_positive_bal':True,
            'previous_withdrawal':True,'withdrawal_seizures':True,'delirium_tremens':False,
            'rehab_treatment':False,'blackouts':False,'downers_last_90d':False,
            'other_substances_last_90d':False,'bal_over_200':False,'autonomic_hyperactivity':True
        })
        self.assertEqual(pawss['total'],4)
        self.assertTrue(pawss['high_risk_ge4'])

    def test_v137_specialist_block4_registry_status(self):
        registry=central_load_registry()
        for sid in ('rockall','ranson','meld-3','lille','poisoning-severity','pawss'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertIn(item['implementation_status'],{'dedicated_source_encoded_v1','validated_official_external_wrapper'})

    def test_v137_specialist_phq9_gad7_boundaries(self):
        phq=calculate_phq9({'item_scores':[3]*9})
        self.assertEqual(phq['total'],27)
        self.assertEqual(phq['severity'],'severe_20_27')
        self.assertTrue(phq['self_harm_item_positive'])
        gad=calculate_gad7({'item_scores':[3]*7})
        self.assertEqual(gad['total'],21)
        self.assertEqual(gad['severity'],'severe_15_21')

    def test_v137_specialist_cisne_lrinec(self):
        cisne=calculate_cisne({
            'ecog_ge2':True,'stress_hyperglycemia':True,'copd':True,
            'cardiovascular_disease':True,'mucositis_grade_ge2':True,
            'monocytes_per_uL':100,'clinically_stable':True,'solid_tumor':True
        })
        self.assertEqual(cisne['total'],8)
        self.assertEqual(cisne['class'],'III_high_ge3')
        with self.assertRaises(ValueError):
            calculate_cisne({
                'ecog_ge2':False,'stress_hyperglycemia':False,'copd':False,
                'cardiovascular_disease':False,'mucositis_grade_ge2':False,
                'monocytes_per_uL':300,'clinically_stable':False,'solid_tumor':True
            })
        lr=calculate_lrinec({
            'crp_mg_L':200,'wbc_10e3_uL':30,'hemoglobin_g_dL':10,
            'sodium_mmol_L':130,'creatinine_mg_dL':2,'glucose_mg_dL':200
        })
        self.assertEqual(lr['total'],13)
        self.assertEqual(lr['risk_band'],'high_ge8')
        self.assertIn('never delay',lr['warning'])

    def test_v137_specialist_puqe_fullpiers(self):
        puqe=calculate_puqe24({'nausea_hours':7,'vomiting_count':7,'retching_count':7})
        self.assertEqual(puqe['total'],15)
        self.assertEqual(puqe['severity'],'severe_13_15')
        fp=calculate_fullpiers({
            'gestational_age_weeks':32,'chest_pain_or_dyspnea':True,
            'creatinine_umol_L':100,'platelets_10e9_L':100,'ast_IU_L':100,'spo2_percent':94
        })
        self.assertGreaterEqual(fp['probability_adverse_maternal_outcome_48h'],0)
        self.assertLessEqual(fp['probability_adverse_maternal_outcome_48h'],1)
        self.assertEqual(fp['input_units']['creatinine'],'umol/L')

    def test_v137_specialist_block5_registry_status(self):
        registry=central_load_registry()
        for sid in ('phq9','gad7','cisne','lrinec','puqe','fullpiers'):
            item=next(x for x in registry['scales'] if x['id']==sid)
            self.assertEqual(item['implementation_status'],'dedicated_source_encoded_v1')

    def test_v137_specialist_psofa_zero_and_max(self):
        zero=calculate_psofa({
            'age_months':24,'respiratory_support':False,'pao2_fio2':450,
            'platelets_10e3_uL':200,'bilirubin_mg_dL':0.8,'map_mmHg':80,
            'dopamine_mcg_kg_min':0,'epinephrine_mcg_kg_min':0,'norepinephrine_mcg_kg_min':0,
            'dobutamine_any_dose':False,'gcs':15,'creatinine_mg_dL':0.5
        })
        self.assertEqual(zero['total'],0)
        maximum=calculate_psofa({
            'age_months':24,'respiratory_support':True,'pao2_fio2':80,
            'platelets_10e3_uL':10,'bilirubin_mg_dL':13,'map_mmHg':30,
            'dopamine_mcg_kg_min':20,'epinephrine_mcg_kg_min':0,'norepinephrine_mcg_kg_min':0,
            'dobutamine_any_dose':False,'gcs':3,'creatinine_mg_dL':3
        })
        self.assertEqual(maximum['total'],24)

    def test_v137_specialist_pelod2_zero_and_max(self):
        zero=calculate_pelod2({
            'age_months':24,'gcs':15,'both_pupils_fixed':False,'lactate_mmol_L':2,
            'map_mmHg':70,'creatinine_umol_L':40,'pao2_fio2':100,'paco2_mmHg':40,
            'invasive_ventilation':False,'wbc_10e9_L':5,'platelets_10e9_L':200
        })
        self.assertEqual(zero['total'],0)
        maximum=calculate_pelod2({
            'age_months':24,'gcs':3,'both_pupils_fixed':True,'lactate_mmol_L':12,
            'map_mmHg':20,'creatinine_umol_L':100,'pao2_fio2':50,'paco2_mmHg':100,
            'invasive_ventilation':True,'wbc_10e9_L':1,'platelets_10e9_L':50
        })
        self.assertEqual(maximum['total'],33)

    def test_v137_specialist_parc_probability(self):
        low=calculate_parc({
            'age_years':15,'sex':'female','pain_duration_hours':10,
            'pain_with_walking_hopping_coughing':False,'migration_to_rlq':False,
            'maximal_rlq_tenderness':False,'guarding':False,'anc_10e3_uL':1
        })
        high=calculate_parc({
            'age_years':10,'sex':'male','pain_duration_hours':30,
            'pain_with_walking_hopping_coughing':True,'migration_to_rlq':True,
            'maximal_rlq_tenderness':True,'guarding':True,'anc_10e3_uL':14
        })
        self.assertGreater(high['appendicitis_probability'],low['appendicitis_probability'])
        self.assertGreaterEqual(low['appendicitis_probability'],0)
        self.assertLessEqual(high['appendicitis_probability'],1)

    def test_v137_specialist_charlson_hierarchy(self):
        result=calculate_charlson({'conditions':{
            'cerebrovascular_disease':True,'hemiplegia_or_paraplegia':True,
            'diabetes_uncomplicated':True,'diabetes_with_end_organ_damage':True,
            'mild_liver_disease':True,'moderate_severe_liver_disease':True,
            'malignancy_nonmetastatic':True,'metastatic_solid_tumor':True
        }})
        self.assertEqual(result['components']['cerebrovascular_disease'],0)
        self.assertEqual(result['components']['diabetes_uncomplicated'],0)
        self.assertEqual(result['components']['mild_liver_disease'],0)
        self.assertEqual(result['components']['malignancy_nonmetastatic'],0)
        self.assertEqual(result['total'],13)

    def test_v137_specialist_barthel_zero_hundred_and_allowed_values(self):
        max_points={'feeding':10,'bathing':5,'grooming':5,'dressing':10,'bowels':10,'bladder':10,
                    'toilet':10,'transfers':15,'mobility':15,'stairs':10}
        self.assertEqual(calculate_barthel({'item_points':max_points})['total'],100)
        zero={k:0 for k in max_points}
        self.assertEqual(calculate_barthel({'item_points':zero})['total'],0)
        bad=dict(max_points); bad['bathing']=10
        with self.assertRaises(ValueError):
            calculate_barthel({'item_points':bad})

    def test_v137_all_specialist_registry_complete(self):
        registry=central_load_registry()
        completed={'dedicated_source_encoded_v1','validated_official_external_wrapper','central_formula_alias'}
        pending=[x['id'] for x in registry['scales'] if x['tier']=='SPECIALIST' and x['implementation_status'] not in completed]
        self.assertEqual(pending,[])
        self.assertEqual(len([x for x in registry['scales'] if x['tier']=='SPECIALIST']),41)

    def test_v138_pediatric_outpatient_paracetamol_uses_ideal_weight(self):
        result = calculate_pediatric_outpatient(
            'paracetamol-pain-fever-home',
            {'age_months':120, 'actual_weight_kg':55, 'ideal_weight_kg':35, 'home_analgesia_antipyresis_appropriate':True},
            selected_duration_days=2,
        )
        self.assertEqual(result['weight_basis'], 'ideal')
        self.assertEqual(result['dosing_weight_kg'], 35)
        self.assertEqual(result['dose_mg'], 525)
        self.assertEqual(result['total_doses'], 8)
        self.assertEqual(result['volume_status'], 'concentration_required_for_ml')

        liquid = calculate_pediatric_outpatient(
            'paracetamol-pain-fever-home',
            {'age_months':120, 'actual_weight_kg':55, 'ideal_weight_kg':35, 'home_analgesia_antipyresis_appropriate':True},
            {'concentration_mg_per_ml': 24},
            selected_duration_days=2,
        )
        self.assertAlmostEqual(liquid['volume_per_dose']['exact_ml'], 21.875)
        self.assertEqual(liquid['volume_per_dose']['rounded_0_1_ml'], 21.9)

        with self.assertRaisesRegex(ValueError, 'ideal_weight_kg'):
            calculate_pediatric_outpatient(
                'paracetamol-pain-fever-home',
                {'age_months':120, 'actual_weight_kg':55, 'home_analgesia_antipyresis_appropriate':True},
                selected_duration_days=1,
            )

    def test_v138_pediatric_outpatient_amox_clav_exact_ml_course(self):
        result = calculate_pediatric_outpatient(
            'amox-clav-bite',
            {'age_months':84, 'actual_weight_kg':20},
            {'concentration_mg_per_ml':80},
        )
        self.assertEqual(result['dose_mg'],450)
        self.assertAlmostEqual(result['volume_per_dose']['exact_ml'],5.625)
        self.assertEqual(result['volume_per_dose']['rounded_0_1_ml'],5.6)
        self.assertEqual(result['doses_per_day'],2)
        self.assertEqual(result['duration_days'],5)
        self.assertEqual(result['total_doses'],10)
        self.assertAlmostEqual(result['estimated_total_course_ml'],56.25)
        self.assertIn('start of a meal',result['administration'])

    def test_v138_pediatric_outpatient_rejects_unverified_liquid_concentration(self):
        with self.assertRaisesRegex(ValueError, 'concentration is not in registry'):
            calculate_pediatric_outpatient(
                'amox-clav-bite',
                {'age_months':84, 'actual_weight_kg':20},
                {'concentration_mg_per_ml':50},
            )
        accepted = calculate_pediatric_outpatient(
            'amox-clav-bite',
            {'age_months':84, 'actual_weight_kg':20},
            {'concentration_mg_per_ml':50,'external_concentration_verified':True},
        )
        self.assertAlmostEqual(accepted['volume_per_dose']['exact_ml'],9.0)

    def test_v138_pediatric_outpatient_ibuprofen_daily_cap_and_hard_gates(self):
        result = calculate_pediatric_outpatient(
            'ibuprofen-pain-fever-home',
            {
                'age_months':72,'actual_weight_kg':20,
                'dehydrated':False,'significant_renal_impairment':False,
                'nsaid_hypersensitivity':False,'active_or_recurrent_peptic_ulcer_bleeding':False
            },
            {'concentration_mg_per_ml':20},
            selected_duration_days=2,
        )
        self.assertEqual(result['dose_mg'],200)
        self.assertEqual(result['doses_per_day'],3)
        self.assertEqual(result['volume_per_dose']['exact_ml'],10)
        self.assertIn('with food',result['administration'])

        with self.assertRaisesRegex(ValueError,'dehydration'):
            calculate_pediatric_outpatient(
                'ibuprofen-pain-fever-home',
                {
                    'age_months':72,'actual_weight_kg':20,
                    'dehydrated':True,'significant_renal_impairment':False,
                    'nsaid_hypersensitivity':False,'active_or_recurrent_peptic_ulcer_bleeding':False
                },
                selected_duration_days=1,
            )

    def test_v138_pediatric_outpatient_nitrofurantoin_preserves_source_variants_and_gates(self):
        patient={
            'age_months':120,'actual_weight_kg':20,'egfr_mL_min':90,
            'g6pd_deficiency':False,'acute_porphyria':False,'suspected_pyelonephritis':False,'urine_sample_obtained_before_antibiotic':True
        }
        nice = calculate_pediatric_outpatient(
            'nitrofurantoin-cystitis-nice-3d',patient,{'concentration_mg_per_ml':5}
        )
        smpc = calculate_pediatric_outpatient(
            'nitrofurantoin-cystitis-smpc-7d',patient,{'concentration_mg_per_ml':5}
        )
        self.assertEqual(nice['duration_days'],3)
        self.assertEqual(smpc['duration_days'],7)
        self.assertEqual(nice['dose_mg'],15)
        self.assertEqual(nice['volume_per_dose']['exact_ml'],3)
        self.assertIn('food or milk',nice['administration'])

        bad=dict(patient); bad['egfr_mL_min']=40
        with self.assertRaisesRegex(ValueError,'eGFR'):
            calculate_pediatric_outpatient('nitrofurantoin-cystitis-smpc-7d',bad)

        bad=dict(patient); bad['suspected_pyelonephritis']=True
        with self.assertRaisesRegex(ValueError,'pyelonephritis'):
            calculate_pediatric_outpatient('nitrofurantoin-cystitis-nice-3d',bad)

    def test_v138_pediatric_outpatient_azithromycin_schedule_generates_phase_ml(self):
        result = calculate_pediatric_outpatient(
            'azithromycin-pertussis-ge6mo',
            {'age_months':60,'actual_weight_kg':20,'sight_threatening_red_eye_excluded':True},
            {'concentration_mg_per_ml':40},
        )
        self.assertEqual(result['total_doses'],5)
        self.assertEqual(result['schedule'][0]['dose_mg'],200)
        self.assertEqual(result['schedule'][0]['volume_per_dose']['exact_ml'],5)
        self.assertEqual(result['schedule'][1]['dose_mg'],100)
        self.assertEqual(result['schedule'][1]['volume_per_dose']['exact_ml'],2.5)
        self.assertAlmostEqual(result['estimated_total_course_ml'],15)

    def test_v138_pediatric_outpatient_fixed_bands_ondansetron_cetirizine_oseltamivir(self):
        ond = calculate_pediatric_outpatient(
            'ondansetron-gastroenteritis-initial',
            {'age_months':48,'actual_weight_kg':20,'gastroenteritis_red_flags_excluded':True}
        )
        self.assertEqual(ond['dose_mg'],4)
        self.assertEqual(ond['total_doses'],1)

        cet = calculate_pediatric_outpatient(
            'cetirizine-urticaria-ge1y',
            {'age_months':84,'actual_weight_kg':25},
            {'concentration_mg_per_ml':1},
        )
        self.assertEqual(cet['dose_mg'],5)
        self.assertEqual(cet['doses_per_day'],2)
        self.assertEqual(cet['volume_per_dose']['exact_ml'],5)

        ose = calculate_pediatric_outpatient(
            'oseltamivir-influenza-ge1y',
            {'age_months':96,'actual_weight_kg':20,'influenza_antiviral_indication_confirmed':True},
            {'concentration_mg_per_ml':6},
        )
        self.assertEqual(ose['dose_mg'],45)
        self.assertEqual(ose['volume_per_dose']['exact_ml'],7.5)
        self.assertEqual(ose['total_doses'],10)

    def test_v138_pediatric_outpatient_registry_has_required_safety_fields(self):
        registry=load_pediatric_outpatient_registry()
        self.assertGreaterEqual(len(registry['entries']),89)
        ids=[x['id'] for x in registry['entries']]
        self.assertEqual(len(ids),len(set(ids)))
        for item in registry['entries']:
            for field in ('id','category','drug','diagnosis','dose_model','weight_basis','source','source_url'):
                self.assertIn(field,item)
            self.assertNotEqual(item['source'],'')
            self.assertNotEqual(item['source_url'],'')
        categories={x['category'] for x in registry['entries']}
        for required in ('oral_antibiotic','analgesic_antipyretic','antiemetic','antihistamine','antiasthmatic_systemic_steroid','antiviral'):
            self.assertIn(required,categories)

    def test_v138_blockA_clarithromycin_mixed_weight_bands(self):
        low = calculate_pediatric_outpatient(
            'clarithromycin-aom-penicillin-allergy',
            {'age_months':12,'actual_weight_kg':7},
            {'concentration_mg_per_ml':25},
            selected_duration_days=5,
        )
        self.assertAlmostEqual(low['dose_mg'],52.5)
        self.assertAlmostEqual(low['volume_per_dose']['exact_ml'],2.1)
        self.assertEqual(low['total_doses'],10)

        band = calculate_pediatric_outpatient(
            'clarithromycin-aom-penicillin-allergy',
            {'age_months':48,'actual_weight_kg':15,'gastroenteritis_red_flags_excluded':True},
            {'concentration_mg_per_ml':25},
            selected_duration_days=7,
        )
        self.assertEqual(band['dose_mg'],125)
        self.assertEqual(band['volume_per_dose']['exact_ml'],5)
        self.assertEqual(band['total_doses'],14)

    def test_v138_blockA_antibiotic_indication_separation(self):
        registry=load_pediatric_outpatient_registry()
        ids={x['id'] for x in registry['entries']}
        for sid in (
            'clarithromycin-aom-penicillin-allergy',
            'clarithromycin-sinusitis-penicillin-allergy',
            'clarithromycin-cap-penicillin-allergy',
            'cefalexin-impetigo-extensive',
            'cefalexin-cervical-lymphadenitis-mild',
        ):
            self.assertIn(sid,ids)
        aom=next(x for x in registry['entries'] if x['id']=='clarithromycin-aom-penicillin-allergy')
        cap=next(x for x in registry['entries'] if x['id']=='clarithromycin-cap-penicillin-allergy')
        self.assertNotEqual(aom['diagnosis'],cap['diagnosis'])

    def test_v138_blockA_asthma_controller_age_and_device_gates(self):
        preschool = calculate_pediatric_outpatient(
            'fluticasone-controller-preschool',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
        )
        self.assertIn('50 microgram',preschool['device']['device'])
        self.assertEqual(preschool['device']['puffs_per_dose'],1)

        school = calculate_pediatric_outpatient(
            'budesonide-formoterol-air-mart-6to11-gina2026',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True}
        )
        self.assertEqual(school['device']['maximum_total_inhalations_24h'],8)
        self.assertIn('80/4.5',school['device']['device'])

        teen = calculate_pediatric_outpatient(
            'budesonide-formoterol-air-mart-12to17-gina2026',
            {'age_months':180,'actual_weight_kg':60}
        )
        self.assertEqual(teen['device']['maximum_total_inhalations_24h'],12)

        with self.assertRaisesRegex(ValueError,'minimum age'):
            calculate_pediatric_outpatient(
                'budesonide-formoterol-air-mart-6to11-gina2026',
                {'age_months':60,'actual_weight_kg':20,'sight_threatening_red_eye_excluded':True}
            )

    def test_v138_blockA_montelukast_is_controller_not_reliever(self):
        result=calculate_pediatric_outpatient(
            'montelukast-controller-preschool',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
        )
        self.assertEqual(result['dose_mg'],4)
        self.assertEqual(result['doses_per_day'],1)
        self.assertTrue(any('neuropsychiatric' in x.lower() for x in result['cautions']))

    def test_v138_blockB_dermatology_topical_regimens(self):
        hydro=calculate_pediatric_outpatient(
            'hydrocortisone1-eczema-sensitive-mild',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
        )
        self.assertIn('twice daily',hydro['instructions'])
        self.assertEqual(hydro['weight_basis'],'topical')

        scabies=calculate_pediatric_outpatient(
            'permethrin5-scabies',
            {'age_months':84,'actual_weight_kg':25}
        )
        self.assertIn('8 hours',scabies['instructions'])
        self.assertIn('7 days',scabies['frequency'])

        tinea=calculate_pediatric_outpatient(
            'clotrimazole1-tinea-corporis',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True}
        )
        self.assertIn('2-3 times daily',tinea['instructions'])
        self.assertEqual(tinea['duration_days'],28)

    def test_v138_blockB_ors_weight_volume_and_gate(self):
        ors=calculate_pediatric_outpatient(
            'ors-clinical-dehydration-50mlkg4h',
            {'age_months':24,'actual_weight_kg':12,'shock_or_iv_fluid_indication':False}
        )
        self.assertEqual(ors['total_rehydration_ml'],600)
        self.assertEqual(ors['administration_hours'],4)
        self.assertEqual(ors['target_ml_per_hour'],150)

        with self.assertRaisesRegex(ValueError,'oral-only'):
            calculate_pediatric_outpatient(
                'ors-clinical-dehydration-50mlkg4h',
                {'age_months':24,'actual_weight_kg':12,'shock_or_iv_fluid_indication':True}
            )

    def test_v138_blockB_macrogol_maintenance_and_disimpaction(self):
        maintenance=calculate_pediatric_outpatient(
            'macrogol3350-electrolytes-constipation-maintenance-1to11',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
        )
        self.assertEqual(maintenance['sachets_per_day'],1)
        self.assertEqual(maintenance['dose_unit'],'sachet')

        disimpaction=calculate_pediatric_outpatient(
            'macrogol3350-electrolytes-disimpaction-5to11',
            {'age_months':96,'actual_weight_kg':30}
        )
        self.assertEqual(disimpaction['sachet_schedule'][0]['sachets'],4)
        self.assertEqual(disimpaction['sachet_schedule'][-1]['sachets'],12)
        self.assertEqual(disimpaction['duration_days'],7)

    def test_v138_blockB_lactulose_range_requires_explicit_choice(self):
        with self.assertRaisesRegex(ValueError,'volume selection required'):
            calculate_pediatric_outpatient(
                'lactulose-constipation-1mo18y',
                {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
            )
        result=calculate_pediatric_outpatient(
            'lactulose-constipation-1mo18y',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True},
            selected_volume_ml=7.5
        )
        self.assertEqual(result['volume_per_dose']['exact_ml'],7.5)
        self.assertEqual(result['doses_per_day'],2)
        with self.assertRaisesRegex(ValueError,'outside source range'):
            calculate_pediatric_outpatient(
                'lactulose-constipation-1mo18y',
                {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True},
                selected_volume_ml=12
            )

    def test_v138_blockC_pinworm_repeat_schedules(self):
        alb=calculate_pediatric_outpatient(
            'albendazole-pinworm-ge2y',
            {'age_months':60,'actual_weight_kg':20,'sight_threatening_red_eye_excluded':True},
            {'concentration_mg_per_ml':20}
        )
        self.assertEqual(alb['total_doses'],2)
        self.assertEqual(alb['schedule'][0]['dose_mg'],400)
        self.assertEqual(alb['schedule'][0]['volume_per_dose']['exact_ml'],20)
        self.assertEqual(alb['schedule'][1]['name'],'dose_2_day_15')
        self.assertEqual(alb['estimated_total_course_ml'],40)

        pyr=calculate_pediatric_outpatient(
            'pyrantel-pinworm-ge2y',
            {'age_months':84,'actual_weight_kg':20}
        )
        self.assertEqual(pyr['total_doses'],2)
        self.assertEqual(pyr['schedule'][0]['dose_mg'],220)

    def test_v138_blockC_ivermectin_weight_and_loa_gates(self):
        ok=calculate_pediatric_outpatient(
            'ivermectin-strongyloides-ge15kg',
            {'age_months':120,'actual_weight_kg':20,'suspected_or_confirmed_loa_loa':False},
            selected_duration_days=2
        )
        self.assertEqual(ok['dose_mg'],4)
        self.assertEqual(ok['total_doses'],2)

        with self.assertRaisesRegex(ValueError,'15 kg'):
            calculate_pediatric_outpatient(
                'ivermectin-strongyloides-ge15kg',
                {'age_months':60,'actual_weight_kg':14,'suspected_or_confirmed_loa_loa':False},
                selected_duration_days=1
            )
        with self.assertRaisesRegex(ValueError,'Loa loa'):
            calculate_pediatric_outpatient(
                'ivermectin-strongyloides-ge15kg',
                {'age_months':120,'actual_weight_kg':20,'suspected_or_confirmed_loa_loa':True},
                selected_duration_days=1
            )

    def test_v138_blockC_acyclovir_volume_and_renal_gate(self):
        v40=calculate_pediatric_outpatient(
            'acyclovir-varicella-standard-renal',
            {'age_months':84,'actual_weight_kg':20,'renal_adjustment_required':False,'varicella_oral_antiviral_indication_confirmed':True,'severe_or_disseminated_varicella':False},
            {'concentration_mg_per_ml':40}
        )
        self.assertEqual(v40['dose_mg'],400)
        self.assertEqual(v40['volume_per_dose']['exact_ml'],10)
        self.assertEqual(v40['total_doses'],20)

        v80=calculate_pediatric_outpatient(
            'acyclovir-varicella-standard-renal',
            {'age_months':84,'actual_weight_kg':20,'renal_adjustment_required':False,'varicella_oral_antiviral_indication_confirmed':True,'severe_or_disseminated_varicella':False},
            {'concentration_mg_per_ml':80}
        )
        self.assertEqual(v80['volume_per_dose']['exact_ml'],5)

        with self.assertRaisesRegex(ValueError,'renal'):
            calculate_pediatric_outpatient(
                'acyclovir-varicella-standard-renal',
                {'age_months':84,'actual_weight_kg':20,'renal_adjustment_required':True},
                {'concentration_mg_per_ml':40}
            )

    def test_v138_blockC_ent_eye_regimens(self):
        eye=calculate_pediatric_outpatient(
            'chloramphenicol05-bacterial-conjunctivitis',
            {'age_months':72,'actual_weight_kg':20,'sight_threatening_red_eye_excluded':True},
            selected_duration_days=5
        )
        self.assertEqual(eye['drops_per_dose'],1)
        self.assertEqual(eye['doses_per_day_range'],[4,6])

        ear=calculate_pediatric_outpatient(
            'ciprofloxacin-dexamethasone-aoe-ge1y',
            {'age_months':60,'actual_weight_kg':18}
        )
        self.assertEqual(ear['drops_per_dose'],4)
        self.assertEqual(ear['doses_per_day'],2)
        self.assertEqual(ear['duration_days'],7)

        with self.assertRaisesRegex(ValueError,'perforation'):
            calculate_pediatric_outpatient(
                'phenazone-lidocaine-aom-pain',
                {'age_months':48,'actual_weight_kg':18,'immediate_oral_antibiotic_given':False,'tm_perforation_or_otorrhoea':True}
            )

    def test_v138_blockC_rizatriptan_weight_boundary_is_fail_closed(self):
        low=calculate_pediatric_outpatient(
            'rizatriptan-migraine-rch',
            {'age_months':120,'actual_weight_kg':35,'secondary_headache_red_flags_excluded':True}
        )
        self.assertEqual(low['dose_mg'],5)

        high=calculate_pediatric_outpatient(
            'rizatriptan-migraine-rch',
            {'age_months':180,'actual_weight_kg':41,'secondary_headache_red_flags_excluded':True}
        )
        self.assertEqual(high['dose_mg'],10)

        with self.assertRaisesRegex(ValueError,'no matching'):
            calculate_pediatric_outpatient(
                'rizatriptan-migraine-rch',
                {'age_months':120,'actual_weight_kg':40,'secondary_headache_red_flags_excluded':True}
            )

    def test_v138_blockC_ondansetron_migraine_volume(self):
        ond=calculate_pediatric_outpatient(
            'ondansetron-migraine-vomiting-ed',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            {'concentration_mg_per_ml':0.8}
        )
        self.assertEqual(ond['dose_mg'],4.5)
        self.assertAlmostEqual(ond['volume_per_dose']['exact_ml'],5.625)
        self.assertEqual(ond['total_doses'],1)

    def test_v138_blockD_infected_eczema_antibiotic(self):
        result=calculate_pediatric_outpatient(
            'cefalexin-infected-eczema-bacterial',
            {'age_months':84,'actual_weight_kg':20,'systemically_well':True,'suspected_eczema_herpeticum':False},
            {'concentration_mg_per_ml':50},
            selected_duration_days=7
        )
        self.assertEqual(result['dose_mg'],400)
        self.assertEqual(result['volume_per_dose']['exact_ml'],8)
        self.assertEqual(result['total_doses'],21)
        self.assertTrue(any('herpeticum' in x.lower() for x in result['cautions']))

    def test_v138_blockD_intranasal_age_device_bands(self):
        mom=calculate_pediatric_outpatient(
            'mometasone-nasal-allergic-rhinitis',
            {'age_months':72,'actual_weight_kg':25}
        )
        self.assertEqual(mom['device']['sprays_per_nostril_per_dose'],1)
        self.assertEqual(mom['device']['total_daily_micrograms'],100)

        teen=calculate_pediatric_outpatient(
            'mometasone-nasal-allergic-rhinitis',
            {'age_months':180,'actual_weight_kg':55}
        )
        self.assertEqual(teen['device']['sprays_per_nostril_per_dose'],2)
        self.assertEqual(teen['device']['total_daily_micrograms'],200)

        combo=calculate_pediatric_outpatient(
            'azelastine-fluticasone-nasal-ge12',
            {'age_months':180,'actual_weight_kg':55}
        )
        self.assertEqual(combo['device']['sprays_per_nostril_per_dose'],1)
        self.assertEqual(combo['device']['doses_per_day'],2)
        with self.assertRaisesRegex(ValueError,'minimum age'):
            calculate_pediatric_outpatient(
                'azelastine-fluticasone-nasal-ge12',
                {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True}
            )

    def test_v138_blockD_allergic_eye_drops(self):
        olop=calculate_pediatric_outpatient(
            'olopatadine-allergic-conjunctivitis-ge3',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
        )
        self.assertEqual(olop['drops_per_dose'],1)
        self.assertEqual(olop['doses_per_day'],2)

        keto=calculate_pediatric_outpatient(
            'ketotifen-eye-allergic-conjunctivitis-ge3',
            {'age_months':60,'actual_weight_kg':20,'sight_threatening_red_eye_excluded':True}
        )
        self.assertEqual(keto['drops_per_dose'],1)
        self.assertEqual(keto['doses_per_day'],2)

    def test_v138_blockD_docusate_range_is_explicit(self):
        infant=calculate_pediatric_outpatient(
            'docusate-paediatric-constipation-ge6mo',
            {'age_months':9,'actual_weight_kg':9}
        )
        self.assertEqual(infant['volume_per_dose']['exact_ml'],5)
        self.assertEqual(infant['doses_per_day'],3)

        with self.assertRaisesRegex(ValueError,'volume selection required'):
            calculate_pediatric_outpatient(
                'docusate-paediatric-constipation-ge6mo',
                {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True}
            )
        child=calculate_pediatric_outpatient(
            'docusate-paediatric-constipation-ge6mo',
            {'age_months':48,'actual_weight_kg':18,'sight_threatening_red_eye_excluded':True},
            selected_volume_ml=7.5
        )
        self.assertEqual(child['volume_per_dose']['exact_ml'],7.5)

    def test_v138_blockE_gas_penicillin_and_amoxicillin(self):
        pen=calculate_pediatric_outpatient(
            'phenoxymethylpenicillin-gas-sore-throat',
            {'age_months':120,'actual_weight_kg':20},
            {'concentration_mg_per_ml':50}
        )
        self.assertEqual(pen['dose_mg'],300)
        self.assertEqual(pen['volume_per_dose']['exact_ml'],6)
        self.assertEqual(pen['total_doses'],20)
        self.assertIn('before',pen['administration'].lower())

        amox=calculate_pediatric_outpatient(
            'amoxicillin-gas-sore-throat-adherence',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            {'concentration_mg_per_ml':50}
        )
        self.assertEqual(amox['dose_mg'],1000)
        self.assertEqual(amox['volume_per_dose']['exact_ml'],20)
        self.assertEqual(amox['total_doses'],10)

    def test_v138_blockE_beta_lactam_allergy_pathways_are_separate(self):
        ceph=calculate_pediatric_outpatient(
            'cefalexin-gas-sore-throat-nonimmediate-penicillin-allergy',
            {'age_months':120,'actual_weight_kg':30,'immediate_or_severe_beta_lactam_allergy':False},
            {'concentration_mg_per_ml':50}
        )
        self.assertEqual(ceph['dose_mg'],750)

        with self.assertRaisesRegex(ValueError,'not appropriate'):
            calculate_pediatric_outpatient(
                'cefalexin-gas-sore-throat-nonimmediate-penicillin-allergy',
                {'age_months':120,'actual_weight_kg':30,'immediate_or_severe_beta_lactam_allergy':True},
                {'concentration_mg_per_ml':50}
            )

        azi=calculate_pediatric_outpatient(
            'azithromycin-gas-sore-throat-immediate-beta-lactam-allergy',
            {'age_months':120,'actual_weight_kg':30,'immediate_or_severe_beta_lactam_allergy':True},
            {'concentration_mg_per_ml':40}
        )
        self.assertEqual(azi['dose_mg'],360)
        self.assertEqual(azi['volume_per_dose']['exact_ml'],9)
        self.assertEqual(azi['total_doses'],5)

    def test_v138_blockE_trimethoprim_uti_resistance_and_pyelo_gates(self):
        result=calculate_pediatric_outpatient(
            'trimethoprim-cystitis-low-resistance',
            {
                'age_months':84,'actual_weight_kg':20,
                'low_resistance_risk_or_susceptible':True,
                'suspected_pyelonephritis':False,
                'urine_sample_obtained_before_antibiotic':True
            },
            {'concentration_mg_per_ml':10}
        )
        self.assertEqual(result['dose_mg'],80)
        self.assertEqual(result['volume_per_dose']['exact_ml'],8)
        self.assertEqual(result['total_doses'],6)

        with self.assertRaisesRegex(ValueError,'resistance'):
            calculate_pediatric_outpatient(
                'trimethoprim-cystitis-low-resistance',
                {
                    'age_months':84,'actual_weight_kg':20,
                    'low_resistance_risk_or_susceptible':False,
                    'suspected_pyelonephritis':False,
                    'urine_sample_obtained_before_antibiotic':True
                }
            )
        with self.assertRaisesRegex(ValueError,'pyelonephritis'):
            calculate_pediatric_outpatient(
                'trimethoprim-cystitis-low-resistance',
                {
                    'age_months':84,'actual_weight_kg':20,
                    'low_resistance_risk_or_susceptible':True,
                    'suspected_pyelonephritis':True,
                    'urine_sample_obtained_before_antibiotic':True
                }
            )

    def test_v138_outpatient_registry_expanded_integrity(self):
        registry=load_pediatric_outpatient_registry()
        allowed_weights={'actual','ideal','adjusted','fixed_age_band','fixed_weight_band','device','topical','not_weight_based'}
        allowed_models={'mg_per_kg_per_dose','fixed_age_band','fixed_weight_band','schedule_by_day','fixed_schedule','fixed_dose','fixed_volume_band','volume_ml_per_kg_course','sachet_schedule','device','topical'}
        ids=[]
        for item in registry['entries']:
            ids.append(item['id'])
            self.assertIn(item['weight_basis'],allowed_weights,item['id'])
            self.assertIn(item['dose_model'],allowed_models,item['id'])
            self.assertTrue(item.get('diagnosis'),item['id'])
            self.assertTrue(item.get('source'),item['id'])
            self.assertTrue(item.get('source_url'),item['id'])
            for concentration in item.get('verified_concentrations',[]):
                self.assertGreater(float(concentration['mg_per_ml']),0,item['id'])
            if item.get('max_mg_per_dose') is not None:
                self.assertGreater(float(item['max_mg_per_dose']),0,item['id'])
            if item.get('adult_max_daily_mg') is not None:
                self.assertGreater(float(item['adult_max_daily_mg']),0,item['id'])
        self.assertEqual(len(ids),len(set(ids)))
        self.assertGreaterEqual(len(ids),89)

    def test_v138_outpatient_registry_family_coverage(self):
        registry=load_pediatric_outpatient_registry()
        categories={x['category'] for x in registry['entries']}
        expected={
            'oral_antibiotic','analgesic_antipyretic','antiemetic','antihistamine',
            'antiasthmatic_systemic_steroid','antiasthmatic_relief','asthma_controller_ics',
            'asthma_controller_ics_laba','asthma_controller_ics_formoterol_air_mart',
            'dermatology_topical','dermatology_antifungal_topical','dermatology_antiparasitic_topical',
            'gastrointestinal_rehydration','gastrointestinal_laxative','antiparasitic','antiviral',
            'ent_otologic','ophthalmology_topical','ophthalmology_antiallergic','migraine_abortive',
            'allergic_rhinitis_intranasal'
        }
        self.assertTrue(expected.issubset(categories))

    def test_v138_blockF_amoxicillin_and_coamox_renal_gates(self):
        with self.assertRaisesRegex(ValueError,'below 30'):
            calculate_pediatric_outpatient(
                'amoxicillin-aom',
                {'age_months':60,'actual_weight_kg':20,'known_renal_impairment':True,'egfr_mL_min':20},
                {'concentration_mg_per_ml':50}
            )
        ok=calculate_pediatric_outpatient(
            'amoxicillin-aom',
            {'age_months':60,'actual_weight_kg':20,'known_renal_impairment':True,'egfr_mL_min':60},
            {'concentration_mg_per_ml':50}
        )
        self.assertEqual(ok['dose_mg'],600)

        with self.assertRaisesRegex(ValueError,'7:1'):
            calculate_pediatric_outpatient(
                'amox-clav-bite',
                {'age_months':84,'actual_weight_kg':20,'known_renal_impairment':True,'egfr_mL_min':20},
                {'concentration_mg_per_ml':80}
            )

    def test_v138_blockF_clarithromycin_cetirizine_oseltamivir_renal_gates(self):
        with self.assertRaisesRegex(ValueError,'below creatinine clearance 30'):
            calculate_pediatric_outpatient(
                'clarithromycin-aom-penicillin-allergy',
                {'age_months':48,'actual_weight_kg':15,'known_renal_impairment':True,'egfr_mL_min':20},
                {'concentration_mg_per_ml':25},
                selected_duration_days=5
            )

        with self.assertRaisesRegex(ValueError,'individualized'):
            calculate_pediatric_outpatient(
                'cetirizine-urticaria-ge1y',
                {'age_months':84,'actual_weight_kg':25,'known_renal_impairment':True},
                {'concentration_mg_per_ml':1}
            )

        with self.assertRaisesRegex(ValueError,'oseltamivir'):
            calculate_pediatric_outpatient(
                'oseltamivir-influenza-ge1y',
                {'age_months':96,'actual_weight_kg':20,'known_renal_impairment':True},
                {'concentration_mg_per_ml':6}
            )

    def test_v138_blockF_azithromycin_renal_threshold(self):
        ok=calculate_pediatric_outpatient(
            'azithromycin-pertussis-ge6mo',
            {'age_months':60,'actual_weight_kg':20,'known_renal_impairment':True,'egfr_mL_min':30},
            {'concentration_mg_per_ml':40}
        )
        self.assertEqual(ok['total_doses'],5)
        with self.assertRaisesRegex(ValueError,'GFR 10'):
            calculate_pediatric_outpatient(
                'azithromycin-pertussis-ge6mo',
                {'age_months':60,'actual_weight_kg':20,'known_renal_impairment':True,'egfr_mL_min':5},
                {'concentration_mg_per_ml':40}
            )

    def test_v138_blockF_ondansetron_and_dexamethasone_organ_metadata(self):
        ond=calculate_pediatric_outpatient(
            'ondansetron-migraine-vomiting-ed',
            {'age_months':120,'actual_weight_kg':30,'known_hepatic_impairment':True,'hepatic_severity':'moderate','secondary_headache_red_flags_excluded':True},
            {'concentration_mg_per_ml':0.8}
        )
        self.assertIn('8 mg',ond['hepatic_adjustment']['detail'])

        dex=calculate_pediatric_outpatient(
            'dexamethasone-croup-mild-moderate',
            {'age_months':48,'actual_weight_kg':18,'known_renal_impairment':True,'egfr_mL_min':20,'known_hepatic_impairment':True,'hepatic_severity':'moderate','croup_discharge_criteria_met':True},
            {'concentration_mg_per_ml':0.4}
        )
        self.assertEqual(dex['renal_adjustment']['mode'],'none_required')
        self.assertEqual(dex['hepatic_adjustment']['mode'],'none_required')

    def test_v138_pharmacy_review_ondansetron_15kg_boundary(self):
        result=calculate_pediatric_outpatient(
            'ondansetron-gastroenteritis-initial',
            {'age_months':48,'actual_weight_kg':15,'gastroenteritis_red_flags_excluded':True}
        )
        self.assertEqual(result['dose_mg'],4)
        self.assertEqual(result['total_doses'],1)

    def test_v138_pharmacy_review_prednisolone_under2_requires_explicit_discharge_plan(self):
        with self.assertRaisesRegex(ValueError,'explicit pediatric/ED discharge plan'):
            calculate_pediatric_outpatient(
                'prednisolone-asthma-lt2y',
                {'age_months':18,'actual_weight_kg':11},
                selected_dose_per_kg=1,
                selected_duration_days=3
            )
        ok=calculate_pediatric_outpatient(
            'prednisolone-asthma-lt2y',
            {'age_months':18,'actual_weight_kg':11,'specialist_or_ed_discharge_plan':True,'asthma_discharge_criteria_met':True},
            selected_dose_per_kg=1,
            selected_duration_days=3
        )
        self.assertEqual(ok['dose_mg'],11)
        self.assertEqual(ok['total_doses'],3)

    def test_v138_pharmacy_review_clindamycin_verified_liquid(self):
        result=calculate_pediatric_outpatient(
            'clindamycin-mrsa-skin',
            {'age_months':120,'actual_weight_kg':20},
            {'concentration_mg_per_ml':15}
        )
        self.assertEqual(result['dose_mg'],200)
        self.assertAlmostEqual(result['volume_per_dose']['exact_ml'],13.333333333333334)
        self.assertEqual(result['total_doses'],20)

    def test_v138_pharmacy_review_fexofenadine_pediatric_organ_gate(self):
        with self.assertRaisesRegex(ValueError,'renal impairment'):
            calculate_pediatric_outpatient(
                'fexofenadine-allergic-rhinitis',
                {'age_months':120,'actual_weight_kg':30,'known_renal_impairment':True}
            )
        with self.assertRaisesRegex(ValueError,'hepatic impairment'):
            calculate_pediatric_outpatient(
                'fexofenadine-allergic-rhinitis',
                {'age_months':120,'actual_weight_kg':30,'known_hepatic_impairment':True,'hepatic_severity':'moderate'}
            )

    def test_v138_alert_exact_drug_allergy_blocks(self):
        alert=evaluate_pediatric_alerts(
            'amoxicillin-aom',
            {'age_months':60,'actual_weight_kg':20,'allergies':['amoxicillin']}
        )
        self.assertTrue(alert['blocked'])
        self.assertEqual(alert['highest_severity'],'STOP')
        self.assertTrue(any(x['code']=='ALLERGY_EXACT' for x in alert['alerts']))
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'amoxicillin-aom',
                {'age_months':60,'actual_weight_kg':20,'allergies':['amoxicillin']},
                {'concentration_mg_per_ml':50}
            )

    def test_v138_alert_beta_lactam_severe_vs_nonsevere(self):
        severe=evaluate_pediatric_alerts(
            'cefalexin-cellulitis',
            {'age_months':84,'actual_weight_kg':20,'cellulitis_outpatient_criteria_met':True,'allergies':[{'class':'penicillin','phenotype':'anaphylaxis','severity':'severe'}]}
        )
        self.assertTrue(severe['blocked'])
        self.assertTrue(any(x['severity']=='STOP' for x in severe['alerts']))

        nonsevere=evaluate_pediatric_alerts(
            'cefalexin-cellulitis',
            {'age_months':84,'actual_weight_kg':20,'cellulitis_outpatient_criteria_met':True,'allergies':[{'class':'penicillin','phenotype':'delayed_exanthem','severity':'mild'}]}
        )
        self.assertFalse(nonsevere['blocked'])
        self.assertEqual(nonsevere['highest_severity'],'ALERT')

    def test_v138_alert_clarithromycin_interactions_and_qt(self):
        simva=evaluate_pediatric_alerts(
            'clarithromycin-pertussis-ge1mo',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            active_medications=['simvastatin']
        )
        self.assertTrue(simva['blocked'])
        self.assertTrue(any('clarithromycin-contraindicated' in x['code'] for x in simva['alerts']))

        qt=evaluate_pediatric_alerts(
            'clarithromycin-pertussis-ge1mo',
            {'age_months':120,'actual_weight_kg':30,'known_qt_prolongation_or_ventricular_arrhythmia':True}
        )
        self.assertTrue(qt['blocked'])

    def test_v138_alert_ondansetron_apomorphine_qt_serotonergic(self):
        apo=evaluate_pediatric_alerts(
            'ondansetron-migraine-vomiting-ed',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            active_medications=['apomorphine']
        )
        self.assertTrue(apo['blocked'])

        ser=evaluate_pediatric_alerts(
            'ondansetron-migraine-vomiting-ed',
            {'age_months':120,'actual_weight_kg':30,'hypokalaemia_or_hypomagnesaemia':True,'secondary_headache_red_flags_excluded':True},
            active_medications=['sertraline','azithromycin']
        )
        self.assertFalse(ser['blocked'])
        self.assertGreaterEqual(ser['counts']['ALERT'],1)
        self.assertGreaterEqual(ser['counts']['CAUTION'],1)

    def test_v138_alert_ibuprofen_anticoagulant_and_dehydration(self):
        risk=evaluate_pediatric_alerts(
            'ibuprofen-pain-fever-home',
            {'age_months':120,'actual_weight_kg':30,'dehydrated':False},
            active_medications=['warfarin','enalapril','furosemide']
        )
        self.assertFalse(risk['blocked'])
        self.assertGreaterEqual(risk['counts']['ALERT'],2)

        dry=evaluate_pediatric_alerts(
            'ibuprofen-pain-fever-home',
            {'age_months':120,'actual_weight_kg':30,'dehydrated':True}
        )
        self.assertTrue(dry['blocked'])

    def test_v138_alert_cotrimoxazole_hyperkalaemia_and_methotrexate(self):
        result=evaluate_pediatric_alerts(
            'tmp-smx-mrsa-skin',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            active_medications=['methotrexate','spironolactone','losartan']
        )
        self.assertFalse(result['blocked'])
        self.assertGreaterEqual(result['counts']['ALERT'],2)

    def test_v138_alert_rizatriptan_and_propranolol(self):
        result=evaluate_pediatric_alerts(
            'rizatriptan-migraine-rch',
            {'age_months':180,'actual_weight_kg':50,'secondary_headache_red_flags_excluded':True},
            active_medications=['propranolol']
        )
        self.assertFalse(result['blocked'])
        self.assertEqual(result['highest_severity'],'ALERT')
        self.assertTrue(any('5 mg' in x['action'] for x in result['alerts']))

        blocked=evaluate_pediatric_alerts(
            'rizatriptan-migraine-rch',
            {'age_months':180,'actual_weight_kg':50,'secondary_headache_red_flags_excluded':True},
            active_medications=['sumatriptan']
        )
        self.assertTrue(blocked['blocked'])

    def test_v138_alert_duplicate_ingredient_and_class(self):
        duplicate=evaluate_pediatric_alerts(
            'ibuprofen-pain-fever-home',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            active_medications=[{'name':'ibuprofen','classes':['nsaid']}]
        )
        self.assertFalse(duplicate['blocked'])
        self.assertTrue(any(x['code']=='DUPLICATE_INGREDIENT' for x in duplicate['alerts']))
        self.assertTrue(any(x['code']=='DUPLICATE_CLASS' for x in duplicate['alerts']))

    def test_v138_alert_unverified_concentration_preflight_caution(self):
        result=evaluate_pediatric_alerts(
            'clindamycin-mrsa-skin',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True}
        )
        self.assertIn(result['prescription_status'],{'OK','OK_WITH_CAUTIONS','REVIEW_REQUIRED'})
        calc=calculate_pediatric_outpatient(
            'clindamycin-mrsa-skin',
            {'age_months':120,'actual_weight_kg':30,'secondary_headache_red_flags_excluded':True},
            {'concentration_mg_per_ml':15}
        )
        self.assertIn('medication_safety',calc)
        self.assertEqual(calc['prescription_status'],calc['medication_safety']['prescription_status'])

    def test_v138_alert_missing_safety_context_is_visible(self):
        result=evaluate_pediatric_alerts(
            'amoxicillin-aom',
            {'age_months':60,'actual_weight_kg':20,'sight_threatening_red_eye_excluded':True}
        )
        codes={x['code'] for x in result['alerts']}
        self.assertIn('ALLERGY_STATUS_NOT_DOCUMENTED',codes)
        self.assertIn('MEDICATION_RECONCILIATION_NOT_DOCUMENTED',codes)
        self.assertEqual(result['prescription_status'],'REVIEW_REQUIRED')

    def test_v138_alert_age_weight_and_product_mismatch(self):
        age=evaluate_pediatric_alerts(
            'dexamethasone-asthma-1to11y',
            {'age_months':6,'actual_weight_kg':8,'allergies':[],'active_medications':[]},
            product={'concentration_mg_per_ml':0.4}
        )
        self.assertTrue(age['blocked'])
        self.assertTrue(any(x['code']=='AGE_BELOW_RANGE' for x in age['alerts']))

        weight=evaluate_pediatric_alerts(
            'paracetamol-pain-fever-home',
            {'age_months':120,'actual_weight_kg':40,'allergies':[],'active_medications':[]},
            product={'concentration_mg_per_ml':24}
        )
        self.assertTrue(weight['blocked'])
        self.assertTrue(any(x['code']=='DOSING_WEIGHT_REQUIRED' for x in weight['alerts']))

        conc=evaluate_pediatric_alerts(
            'amox-clav-bite',
            {'age_months':84,'actual_weight_kg':20,'allergies':[],'active_medications':[]},
            product={'concentration_mg_per_ml':50}
        )
        self.assertTrue(conc['blocked'])
        self.assertTrue(any(x['code']=='PRODUCT_CONCENTRATION_MISMATCH' for x in conc['alerts']))

    def test_v138_alert_global_red_flags_block_outpatient_prescription(self):
        for flag in ('clinically_unstable','requires_admission','unable_to_tolerate_oral','suspected_sepsis','significant_hypoxaemia','active_anaphylaxis','surgical_red_flags'):
            patient={'age_months':60,'actual_weight_kg':20,'allergies':[],'active_medications':[],flag:True}
            result=evaluate_pediatric_alerts('amoxicillin-aom',patient,product={'concentration_mg_per_ml':50})
            self.assertTrue(result['blocked'],flag)
            self.assertEqual(result['highest_severity'],'STOP')

    def test_v138_alert_renal_gate_is_structured_before_calculation(self):
        result=evaluate_pediatric_alerts(
            'amoxicillin-aom',
            {'age_months':60,'actual_weight_kg':20,'allergies':[],'active_medications':[],'known_renal_impairment':True,'egfr_mL_min':20},
            product={'concentration_mg_per_ml':50}
        )
        self.assertTrue(result['blocked'])
        self.assertTrue(any(x['code']=='RENAL_THRESHOLD_FAILED' for x in result['alerts']))

    def test_v138_pediatric_clinical_bite_prophylaxis_vs_infection(self):
        ok=calculate_pediatric_outpatient(
            'amox-clav-bite',
            {'age_months':84,'actual_weight_kg':20,'allergies':[],'active_medications':[],'established_bite_infection':False},
            {'concentration_mg_per_ml':80}
        )
        self.assertEqual(ok['duration_days'],5)
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'amox-clav-bite',
                {'age_months':84,'actual_weight_kg':20,'allergies':[],'active_medications':[],'established_bite_infection':True},
                {'concentration_mg_per_ml':80}
            )

    def test_v138_pediatric_clinical_orbital_stepdown_gate(self):
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'amox-clav-preseptal-stepdown',
                {'age_months':120,'actual_weight_kg':30,'allergies':[],'active_medications':[]},
                {'concentration_mg_per_ml':80},
                selected_duration_days=10
            )
        ok=calculate_pediatric_outpatient(
            'amox-clav-preseptal-stepdown',
            {'age_months':120,'actual_weight_kg':30,'allergies':[],'active_medications':[],'orbital_cellulitis_stepdown_after_iv_confirmed':True},
            {'concentration_mg_per_ml':80},
            selected_duration_days=10
        )
        self.assertEqual(ok['dose_mg'],675)

    def test_v138_pediatric_clinical_pyelo_high_dose_stepdown_gate(self):
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'cefalexin-pyelonephritis-ge12mo',
                {'age_months':120,'actual_weight_kg':25,'allergies':[],'active_medications':[]},
                {'concentration_mg_per_ml':50},
                selected_duration_days=7
            )
        ok=calculate_pediatric_outpatient(
            'cefalexin-pyelonephritis-ge12mo',
            {'age_months':120,'actual_weight_kg':25,'allergies':[],'active_medications':[],'rch_pyelo_high_dose_stepdown_confirmed':True,'urine_sample_obtained_before_antibiotic':True},
            {'concentration_mg_per_ml':50},
            selected_duration_days=7
        )
        self.assertEqual(ok['dose_mg'],1125)

    def test_v138_pediatric_clinical_ors_nice_under5_scope(self):
        ok=calculate_pediatric_outpatient(
            'ors-clinical-dehydration-50mlkg4h',
            {'age_months':48,'actual_weight_kg':18,'allergies':[],'active_medications':[],'shock_or_iv_fluid_indication':False}
        )
        self.assertEqual(ok['total_rehydration_ml'],900)
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'ors-clinical-dehydration-50mlkg4h',
                {'age_months':72,'actual_weight_kg':22,'allergies':[],'active_medications':[],'shock_or_iv_fluid_indication':False}
            )

    def test_v138_pediatric_clinical_varicella_requires_indication(self):
        patient={'age_months':156,'actual_weight_kg':45,'allergies':[],'active_medications':[],'renal_adjustment_required':False,'severe_or_disseminated_varicella':False}
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'acyclovir-varicella-standard-renal',patient,{'concentration_mg_per_ml':40}
            )
        patient['varicella_oral_antiviral_indication_confirmed']=True
        ok=calculate_pediatric_outpatient(
            'acyclovir-varicella-standard-renal',patient,{'concentration_mg_per_ml':40}
        )
        self.assertEqual(ok['dose_mg'],800)
        patient['severe_or_disseminated_varicella']=True
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'acyclovir-varicella-standard-renal',patient,{'concentration_mg_per_ml':40}
            )

    def test_v138_pediatric_clinical_hsv_excludes_neonate_and_severe(self):
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'acyclovir-hsv-mucocutaneous-standard-renal',
                {'age_months':0.5,'actual_weight_kg':4,'allergies':[],'active_medications':[],'renal_adjustment_required':False,'severe_or_immunocompromised_hsv':False},
                {'concentration_mg_per_ml':40}
            )
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'acyclovir-hsv-mucocutaneous-standard-renal',
                {'age_months':24,'actual_weight_kg':12,'allergies':[],'active_medications':[],'renal_adjustment_required':False,'severe_or_immunocompromised_hsv':True},
                {'concentration_mg_per_ml':40}
            )

    def test_v138_pediatric_clinical_uti_requires_urine_sample(self):
        base={
            'age_months':84,'actual_weight_kg':20,'allergies':[],'active_medications':[],
            'low_resistance_risk_or_susceptible':True,'suspected_pyelonephritis':False
        }
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'trimethoprim-cystitis-low-resistance',base,{'concentration_mg_per_ml':10}
            )
        base['urine_sample_obtained_before_antibiotic']=True
        ok=calculate_pediatric_outpatient(
            'trimethoprim-cystitis-low-resistance',base,{'concentration_mg_per_ml':10}
        )
        self.assertEqual(ok['dose_mg'],80)

    def test_v138_pediatric_clinical_oseltamivir_requires_indication(self):
        patient={'age_months':96,'actual_weight_kg':20,'allergies':[],'active_medications':[]}
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'oseltamivir-influenza-ge1y',patient,{'concentration_mg_per_ml':6}
            )
        patient['influenza_antiviral_indication_confirmed']=True
        ok=calculate_pediatric_outpatient(
            'oseltamivir-influenza-ge1y',patient,{'concentration_mg_per_ml':6}
        )
        self.assertEqual(ok['dose_mg'],45)

    def test_v138_pediatric_clinical_gastroenteritis_red_flags_gate(self):
        patient={'age_months':48,'actual_weight_kg':15,'allergies':[],'active_medications':[]}
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient('ondansetron-gastroenteritis-initial',patient)
        patient['gastroenteritis_red_flags_excluded']=True
        ok=calculate_pediatric_outpatient('ondansetron-gastroenteritis-initial',patient)
        self.assertEqual(ok['dose_mg'],4)

    def test_v138_pediatric_clinical_infected_eczema_blocks_herpeticum(self):
        patient={
            'age_months':84,'actual_weight_kg':20,'allergies':[],'active_medications':[],
            'systemically_well':True,'suspected_eczema_herpeticum':True
        }
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'cefalexin-infected-eczema-bacterial',patient,
                {'concentration_mg_per_ml':50},selected_duration_days=7
            )
        patient['suspected_eczema_herpeticum']=False
        ok=calculate_pediatric_outpatient(
            'cefalexin-infected-eczema-bacterial',patient,
            {'concentration_mg_per_ml':50},selected_duration_days=7
        )
        self.assertEqual(ok['dose_mg'],400)

    def test_v138_pediatric_clinical_home_paracetamol_requires_suitability(self):
        patient={'age_months':120,'actual_weight_kg':55,'ideal_weight_kg':35,'allergies':[],'active_medications':[]}
        with self.assertRaises(MedicationSafetyStop):
            calculate_pediatric_outpatient(
                'paracetamol-pain-fever-home',patient,
                {'concentration_mg_per_ml':24},selected_duration_days=1
            )
        patient['home_analgesia_antipyresis_appropriate']=True
        ok=calculate_pediatric_outpatient(
            'paracetamol-pain-fever-home',patient,
            {'concentration_mg_per_ml':24},selected_duration_days=1
        )
        self.assertEqual(ok['dose_mg'],525)

    def _clean_note_for_export(self):
        note=new_clinical_note(age_years=72,sex='male',language='pt-PT')
        note['history']['chief_complaint']='Dispneia e tosse com 48 horas de evolução.'
        note['history']['present_illness']='Agravamento progressivo sem identificadores diretos.'
        note['history']['past_medical_history']=['DPOC','HTA']
        note['history']['chronic_medications']=[{'name':'salbutamol','dose':None,'schedule':'SOS','source':'clinician_entry'}]
        note['history']['allergies']=[]
        note['exam']['vitals']=[{'time_label':'admissão','bp':'118/76','hr':88,'rr':22,'spo2':91,'oxygen':'1 L/min','temperature_c':36.3,'gcs':'15','source':'device_measurement'}]
        add_clinical_report(note,'chest_xray','official_report',official_report='Sem derrame pleural. Opacidades bibasais inespecíficas.',privacy_checked=True,burned_in_identifiers_checked=True)
        add_clinical_report(note,'ecg','ai_image_interpretation',ai_interpretation='Ritmo sinusal sem sinais agudos de isquemia.',privacy_checked=True,burned_in_identifiers_checked=True)
        note['assessment']['problem_representation']='Homem de 72 anos com doença respiratória crónica e agravamento agudo de dispneia/tosse.'
        note['assessment']['active_problems']=['Hipoxemia ligeira','Dispneia aguda']
        note['assessment']['likely_diagnoses']=[{'diagnosis':'Exacerbação de doença obstrutiva','confidence':'moderate','evidence_for':['dispneia','tosse'],'evidence_against':[],'missing_discriminating_data':['gasometria completa'],'source_modules':['copd-exacerbation']}]
        note['assessment']['differential_diagnoses']=[{'diagnosis':'Pneumonia','confidence':'low','evidence_for':['tosse'],'evidence_against':['sem febre'],'missing_discriminating_data':['imagem comparativa'],'source_modules':['emergency-infectious-diseases']}]
        note['assessment']['must_not_miss']=[{'diagnosis':'Embolia pulmonar','confidence':'low','evidence_for':[],'evidence_against':[],'missing_discriminating_data':['probabilidade clínica'],'source_modules':['pulmonary-embolism']}]
        note['assessment']['suggested_tests']=[{'action':'Gasometria arterial','priority':'urgent','rationale':'quantificar insuficiência respiratória','source_modules':['blood-gas-image']}]
        note['assessment']['treatment_suggestions']=[{'action':'Oxigénio titulado ao alvo clínico','priority':'immediate','rationale':'corrigir hipoxemia','source_modules':['oxygen-therapy-emergency']}]
        note['assessment']['disposition']=[{'action':'Reavaliar após tratamento inicial','priority':'urgent','rationale':'definir alta versus observação','source_modules':['observation-discharge']}]
        note['clinician_validation']={'reviewed':True,'reviewer_role':'physician','reviewed_at':'relative: after assessment','changes_made':None}
        note['privacy'].update({'direct_identifiers_removed':True,'free_text_screened':True,'source_metadata_checked':True,'burned_in_identifiers_checked':True,'export_allowed':True})
        return note

    def test_v139_clinical_note_attachment_routing(self):
        self.assertEqual(route_clinical_attachment('ecg')['modules'],['ecg-image'])
        self.assertEqual(route_clinical_attachment('chest_xray')['target_section'],'imaging')
        self.assertIn('clinical-scores-calculators',route_clinical_attachment('laboratory_report')['modules'])

    def test_v139_clinical_note_privacy_blocks_direct_identifiers(self):
        note=self._clean_note_for_export()
        note['history']['present_illness']='Nome: João da Silva; dispneia.'
        findings=scan_clinical_note_privacy(note)
        self.assertTrue(any(x['code']=='POSSIBLE_IDENTIFIER_IN_TEXT' for x in findings))
        gate=validate_clinical_note_export(note)
        self.assertTrue(gate['blocked'])

    def test_v139_clinical_note_export_requires_clinician_review(self):
        note=self._clean_note_for_export()
        note['clinician_validation']['reviewed']=False
        gate=validate_clinical_note_export(note)
        self.assertTrue(gate['blocked'])
        self.assertTrue(any(x['code']=='CLINICIAN_REVIEW_REQUIRED' for x in gate['findings']))

    def test_v139_api_text_upload_requires_acceptance_before_persistence(self):
        note = new_clinical_note(age_years=68, sex='male')
        note['history']['chief_complaint'] = 'cefaleia intensa'
        payload = base64.b64encode(
            'TC cranio: sem hemorragia intracraniana aguda.'.encode('utf-8')
        ).decode('ascii')
        prepared = prepare_clinical_upload(
            'tc_report.txt', 'text/plain', payload, explicit_kind='ct'
        )
        self.assertEqual(prepared['privacy']['status'], 'PASS')
        self.assertFalse(prepared['original_retained'])
        self.assertEqual(prepared['route']['target_section'], 'imaging')
        self.assertEqual(note['complementary_tests']['imaging'], [])

        accepted = accept_clinical_upload(
            note, prepared,
            clinician_edit={'official_report': prepared['extracted']['official_report']},
            privacy_checked=True,
            burned_in_identifiers_checked=True,
        )
        self.assertEqual(len(accepted['note']['complementary_tests']['imaging']), 1)
        report = accepted['note']['complementary_tests']['imaging'][0]
        self.assertTrue(report['source_reference'].startswith('sha256:'))
        self.assertEqual(report['routed_modules'], ['ct-mri-screenshot'])
        self.assertFalse(accepted['note']['clinician_validation']['reviewed'])

    def test_v139_api_upload_privacy_stop_blocks_acceptance(self):
        note = new_clinical_note(age_years=55, sex='female')
        payload = base64.b64encode(
            'Nome: Joao da Silva\nECG: ritmo sinusal.'.encode('utf-8')
        ).decode('ascii')
        prepared = prepare_clinical_upload(
            'ecg_report.txt', 'text/plain', payload, explicit_kind='ecg'
        )
        self.assertEqual(prepared['privacy']['status'], 'STOP')
        with self.assertRaises(ValueError):
            accept_clinical_upload(
                note, prepared,
                clinician_edit={'official_report': 'ECG: ritmo sinusal.'},
                privacy_checked=True,
                burned_in_identifiers_checked=True,
            )

    def test_v139_api_binary_upload_is_fail_closed_until_manual_privacy_review(self):
        note = new_clinical_note(age_years=42, sex='male')
        payload = base64.b64encode(b'\x89PNG\r\n\x1a\nnot-a-real-image').decode('ascii')
        prepared = prepare_clinical_upload(
            'rx_torax.png', 'image/png', payload, explicit_kind='xray'
        )
        self.assertEqual(prepared['privacy']['status'], 'REVIEW_REQUIRED')
        self.assertTrue(prepared['privacy']['manual_file_privacy_review_required'])
        self.assertTrue(prepared['privacy']['burned_in_identifier_review_required'])
        self.assertIsNone(prepared['extracted']['official_report'])
        with self.assertRaises(ValueError):
            accept_clinical_upload(
                note, prepared,
                clinician_edit={'ai_interpretation': 'Sem achados agudos evidentes.'},
                privacy_checked=False,
                burned_in_identifiers_checked=False,
            )
        accepted = accept_clinical_upload(
            note, prepared,
            clinician_edit={'ai_interpretation': 'Sem achados agudos evidentes.'},
            privacy_checked=True,
            burned_in_identifiers_checked=True,
        )
        self.assertEqual(len(accepted['note']['complementary_tests']['imaging']), 1)
        self.assertEqual(
            accepted['note']['complementary_tests']['imaging'][0]['provenance'],
            'ai_image_interpretation',
        )

    def test_v139_api_end_to_end_accept_diagnose_review_export(self):
        note = new_clinical_note(age_years=67, sex='male')
        note['history']['chief_complaint'] = 'dor toracica opressiva'
        note['history']['present_illness'] = 'dor toracica com sudorese e nauseas'
        payload = base64.b64encode(
            'ECG: supradesnivel de ST em precordiais anteriores.'.encode('utf-8')
        ).decode('ascii')
        prepared = prepare_clinical_upload(
            'ecg_report.txt', 'text/plain', payload, explicit_kind='ecg'
        )
        accepted = accept_clinical_upload(
            note, prepared,
            clinician_edit={'official_report': prepared['extracted']['official_report']},
            privacy_checked=True,
            burned_in_identifiers_checked=True,
        )
        result = run_clinical_note_api_diagnostic(accepted['note'])
        self.assertFalse(result['blocked'], result.get('issues'))
        self.assertIsNotNone(result['assessment'])
        self.assertIsNotNone(result['note'])
        self.assertFalse(result['note']['clinician_validation']['reviewed'])
        if result['assessment']['treatment_suggestions']:
            self.assertEqual(
                result['medication_safety_gate']['status'], 'REVIEW_REQUIRED'
            )
            self.assertFalse(result['medication_safety_gate']['actionable'])

        reviewed = result['note']
        reviewed['privacy']['direct_identifiers_removed'] = True
        reviewed['privacy']['free_text_screened'] = True
        reviewed['clinician_validation']['reviewed'] = True
        for fmt, magic in (
            ('docx', b'PK'), ('pdf', b'%PDF-1.4'), ('json', b'{')
        ):
            exported = export_clinical_note_bytes(reviewed, fmt)
            self.assertTrue(exported.startswith(magic), fmt)

    def test_v139_clinical_note_diagnostic_contract_and_provenance(self):
        note=self._clean_note_for_export()
        contract=clinical_note_diagnostic_contract(note)
        self.assertFalse(contract['blocked'])
        self.assertIn('likely_diagnoses',contract['required_output'])
        report=note['complementary_tests']['ecg'][0]
        self.assertEqual(report['provenance'],'ai_image_interpretation')
        self.assertEqual(report['routed_modules'],['ecg-image'])

    def test_v139_clinical_note_docx_pdf_export_smoke(self):
        note=self._clean_note_for_export()
        with tempfile.TemporaryDirectory() as directory:
            docx=Path(directory)/'note.docx'
            pdf=Path(directory)/'note.pdf'
            export_clinical_note_docx(note,docx)
            export_clinical_note_pdf(note,pdf)
            self.assertTrue(docx.exists())
            self.assertTrue(pdf.exists())
            self.assertTrue(docx.read_bytes().startswith(b'PK'))
            self.assertTrue(pdf.read_bytes().startswith(b'%PDF-1.4'))
            import zipfile
            with zipfile.ZipFile(docx) as z:
                xml=z.read('word/document.xml').decode('utf-8')
            self.assertIn('Diagnósticos prováveis',xml)
            self.assertNotIn('João da Silva',xml)

    def test_v139_final_human_review_queue_covers_all_yellow(self):
        queue=build_final_human_review_queue(ROOT)
        evidence=json.loads((ROOT/'references/evidence-registry.json').read_text(encoding='utf-8'))
        yellow={mid for mid,e in evidence['modules'].items() if e.get('status')=='yellow'}
        queued={x['module_id'] for x in queue['queue']}
        self.assertEqual(queued,yellow)
        self.assertEqual(queue['yellow_count'],len(yellow))
        self.assertIn('clinical-note-diagnostic-support',queued)
        self.assertIn('final-human-review-gate',queued)

    def test_v139_synthetic_clinical_note_regression_bank(self):
        result=run_clinical_note_synthetic_cases()
        self.assertEqual(result['cases'],12)
        self.assertEqual(result['passed'],12)
        self.assertEqual(result['errors'],[])

    def test_v139_synthetic_diagnostic_reasoning_bank(self):
        result=run_clinical_note_diagnostic_cases()
        self.assertEqual(result['cases'],47)
        self.assertEqual(result['passed'],47,result['errors'])
        self.assertEqual(result['errors'],[])

    def test_v139_pediatric_age_routing_regression_bank(self):
        result=run_clinical_note_pediatric_routing_cases()
        self.assertEqual(result['cases'],5)
        self.assertEqual(result['passed'],5,result['errors'])
        self.assertEqual(result['errors'],[])

    def test_v139_diagnostic_coverage_closure_bank(self):
        result=run_clinical_note_diagnostic_closure_cases()
        self.assertEqual(result['cases'],8)
        self.assertEqual(result['passed'],8,result['errors'])
        self.assertEqual(result['errors'],[])

    def test_v139_diagnostic_coverage_audit(self):
        result=audit_clinical_note_diagnostic_coverage()
        self.assertEqual(result['status'],'PASS',result)
        self.assertEqual(result['module_count'],131)
        self.assertEqual(result['diagnostic_rule_count'],92)
        self.assertEqual(result['covered_or_routed_count'],115)
        self.assertEqual(result['allowed_non_diagnostic_count'],16)
        self.assertEqual(result['unexpected_uncovered'],[])
        self.assertEqual(result['stale_allowed'],[])

    def test_v139_diagnostic_coverage_audit_has_no_unclassified_modules(self):
        modules=(ROOT/'MODULES.md').read_text(encoding='utf-8').splitlines()
        module_ids=[]
        import re
        for line in modules:
            m=re.match(r"\| `([^`]+)`",line)
            if m:
                module_ids.append(m.group(1))
        rules=json.loads((ROOT/'qa'/'clinical-note-diagnostic-rules.json').read_text(encoding='utf-8'))
        audit=json.loads((ROOT/'qa'/'clinical-note-diagnostic-coverage-audit.json').read_text(encoding='utf-8'))
        routed=set()
        for rule in rules['syndromes']:
            routed.add(rule['id'])
            for group in ('suggested_tests','treatment'):
                for item in rule.get(group,[]):
                    routed.update(item.get('source_modules',[]))
            routed.update(rule.get('must_not_miss',[]))
            routed.update(rule.get('differential',[]))
        exempt=set(audit['exempt_non_diagnostic_modules'])
        missing=set(module_ids)-routed-exempt
        self.assertEqual(missing,set(),sorted(missing))
        self.assertEqual(set(module_ids)-routed,exempt)

    def test_fixed_dose_calculator_rejects_zero_concentration(self):
        with self.assertRaises(ValueError):
            fixed_dose_ml_h(1, 0)

if __name__ == "__main__":
    unittest.main()
