#!/usr/bin/env python3

import sys
import unittest
import tempfile
from pathlib import Path


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from infusion_calculator import infusion_ml_h, fixed_dose_ml_h, weight_per_hour_ml_h
from load_module import load
from validate_modules import validate
from weight_based_dose import weight_based_dose
from context_validator import validate_inputs
from evaluate_image_cases import evaluate
from sodium_water_balance import calculate as sodium_water_balance
from acid_base_hyperglycemia import calculate as acid_base_hyperglycemia
from respiratory_support import calculate as respiratory_support
from validate_clinical_cases import validate as validate_clinical_cases
from audit_evidence_coverage import audit as audit_evidence_coverage
from validate_real_image_cases import validate as validate_real_image_cases


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
        self.assertIn('normal PT/INR does not exclude', reversal)

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
        self.assertEqual(len(manifest), 106)
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
            '>50--75 ng/mL',
            '30 ng/mL',
            'idarucizumab 5 g IV',
            '400 mg IV bolus',
            '4 mg/min for 120 min',
            '800 mg IV bolus',
            '8 mg/min for 120 min',
            '25--50 IU/kg',
            '2,000 IU',
            '5--10 mg IV vitamin K',
            'does not exclude clinically relevant apixaban/rivaroxaban effect'
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
            'GI decontamination is not routine',
            'within about **1 hour**',
            'airway is intact/protected',
            'objective opioid-associated hypoventilation',
            '4 mg IV',
            '8 mg intranasal',
            'prolonged resuscitation',
            'poison centre'
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

    def test_fixed_dose_calculator_rejects_zero_concentration(self):
        with self.assertRaises(ValueError):
            fixed_dose_ml_h(1, 0)

if __name__ == "__main__":
    unittest.main()
