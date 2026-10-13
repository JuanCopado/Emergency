"""Form contract only. All score arithmetic/interpretation stays in the canonical engine."""
import hashlib
import json
import math
from pathlib import Path
from clinical_calculator import load_registry, calculate_scale
from core_scores_block1 import NIHSS_ITEM_MAX, GCS_EYE, GCS_VERBAL, GCS_MOTOR
from core_scores_block8_tev import WELLS_DVT_POSITIVE_KEYS

ROOT = Path(__file__).resolve().parents[1]


def number(key, label, unit='', minimum=0, maximum=None, integer=False, optional=False):
    return dict(key=key, label=label, type='number', unit=unit, minimum=minimum,
                maximum=maximum, integer=integer, optional=optional)


def choice(key, label, values, optional=False):
    return dict(key=key, label=label, type='choice', options=[{'value': v, 'label': str(t)} for v, t in values], optional=optional)


def boolean(key, label, optional=False):
    return choice(key, label, [(True, 'Sí'), (False, 'No')], optional)


def flags(pairs):
    return [boolean(k, label) for k, label in pairs]


AGE = number('age', 'Edad', 'años')
HR = number('heart_rate_bpm', 'Frecuencia cardíaca', 'lpm')
PULSE = number('pulse_bpm', 'Pulso', 'lpm')
SBP = number('systolic_bp_mmHg', 'Presión sistólica', 'mmHg')
RR = number('respiratory_rate', 'Frecuencia respiratoria', '/min')
SPO2 = number('spo2_percent', 'SpO₂', '%', maximum=100)
CREAT = number('creatinine_mg_dL', 'Creatinina', 'mg/dL')
PF = number('pao2_fio2_mmHg', 'PaO₂/FiO₂', 'mmHg')
PLATELETS = number('platelets_10e3_uL', 'Plaquetas', '10³/µL')
BILI = number('bilirubin_mg_dL', 'Bilirrubina', 'mg/dL')
MAP = number('map_mmHg', 'Presión arterial media', 'mmHg')
GCS = number('gcs', 'GCS', 'puntos', minimum=3, maximum=15, integer=True)
UREA = number('urea_mmol_L', 'Urea', 'mmol/L')
DVT = boolean('clinical_signs_dvt', 'Signos clínicos de TVP')
HEMOPTYSIS = boolean('hemoptysis', 'Hemoptisis')
PREVIOUS = boolean('previous_dvt_pe', 'TVP/TEP previo')

FORMS = {
    'news2': [RR, SPO2, boolean('supplemental_oxygen', 'Oxígeno suplementario'), SBP, PULSE,
              choice('consciousness', 'Consciencia', [('alert', 'Alerta'), ('new_confusion', 'Confusión nueva'), ('voice', 'Respuesta a voz'), ('pain', 'Respuesta al dolor'), ('unresponsive', 'Sin respuesta')]),
              number('temperature_c', 'Temperatura', '°C', minimum=None),
              choice('spo2_scale', 'Escala SpO₂', [(1, '1'), (2, '2')]),
              boolean('scale2_authorized_hypercapnic_failure', 'Escala 2 autorizada por insuficiencia hipercápnica confirmada', optional=True)],
    'sofa': [PF, boolean('respiratory_support', 'Soporte respiratorio'), PLATELETS, BILI, MAP,
             *[number('vasoactive_mcg_kg_min.'+k, label, 'mcg/kg/min') for k, label in [('dopamine','Dopamina'),('epinephrine','Adrenalina'),('norepinephrine','Noradrenalina')]],
             boolean('vasoactive_mcg_kg_min.dobutamine_any_dose', 'Dobutamina a cualquier dosis'), GCS, CREAT,
             number('urine_output_mL_day', 'Diuresis', 'mL/día', optional=True),
             number('baseline_sofa', 'SOFA basal', 'puntos', maximum=24, integer=True, optional=True)],
    'sofa-2': [GCS, boolean('delirium_drug_required', 'Delirium que requiere tratamiento farmacológico'), PF,
               boolean('advanced_ventilatory_support', 'Soporte ventilatorio avanzado'), boolean('ecmo', 'ECMO'), MAP,
               number('norepinephrine_mcg_kg_min', 'Noradrenalina', 'mcg/kg/min'), number('epinephrine_mcg_kg_min', 'Adrenalina', 'mcg/kg/min'),
               *flags([('other_vasopressor_or_inotrope','Otro vasopresor o inotrópico'),('mechanical_circulatory_support','Soporte circulatorio mecánico')]), BILI, CREAT,
               *flags([('urine_lt_0_5_ml_kg_h_6_12h','Diuresis <0.5 mL/kg/h durante 6–12 h'),('urine_lt_0_5_ml_kg_h_ge12h','Diuresis <0.5 mL/kg/h durante ≥12 h'),('urine_lt_0_3_ml_kg_h_ge24h','Diuresis <0.3 mL/kg/h durante ≥24 h'),('anuria_ge12h','Anuria ≥12 h'),('receiving_or_meets_rrt_criteria','Recibe o cumple criterios de reemplazo renal')]), PLATELETS],
    'heart': [choice('history', 'Historia — valoración clínica', [('slightly_suspicious','Poco sospechosa'),('moderately_suspicious','Moderadamente sospechosa'),('highly_suspicious','Muy sospechosa')]),
              choice('ecg', 'ECG — valoración clínica', [('normal','Normal'),('nonspecific_repolarization','Repolarización inespecífica'),('significant_st_depression','Depresión significativa del ST')]),
              AGE, number('risk_factor_count','Número de factores de riesgo', integer=True), boolean('known_atherosclerotic_disease','Enfermedad aterosclerótica conocida'), number('troponin_multiple_uln','Troponina / límite superior local','× ULN')],
    'grace-2': [AGE, HR, SBP, {**CREAT, 'optional': True}, number('killip_class','Clase Killip','I–IV',minimum=1,maximum=4,integer=True,optional=True),
                *flags([('cardiac_arrest_at_admission','Parada cardíaca al ingreso'),('st_segment_deviation','Desviación del ST'),('elevated_cardiac_biomarkers','Biomarcadores cardíacos elevados')])],
    'wells-pe': [DVT, boolean('pe_more_likely_than_alternative','TEP más probable que alternativa'), HR,
                 boolean('immobilization_ge3d_or_surgery_4w','Inmovilización ≥3 días o cirugía en 4 semanas'), PREVIOUS, HEMOPTYSIS, boolean('active_cancer','Cáncer activo')],
    'wells-dvt': flags(list(zip(WELLS_DVT_POSITIVE_KEYS, ['Cáncer activo','Parálisis, paresia o inmovilización reciente con yeso','Encamado ≥3 días o cirugía mayor en 12 semanas','Dolor localizado del trayecto venoso profundo','Toda la pierna hinchada','Aumento de perímetro de pantorrilla ≥3 cm','Edema con fóvea en pierna sintomática','Venas superficiales colaterales no varicosas','TVP previa'])) + [('alternative_diagnosis_at_least_as_likely','Diagnóstico alternativo al menos igual de probable')]),
    'perc': [boolean('low_pretest_probability','Probabilidad pretest baja confirmada'), AGE, HR, SPO2, HEMOPTYSIS, boolean('estrogen_use','Uso de estrógenos'), PREVIOUS, boolean('unilateral_leg_swelling','Hinchazón unilateral de pierna'), boolean('recent_surgery_or_trauma_requiring_hospitalization_4w','Cirugía o trauma con hospitalización en 4 semanas')],
    'years-pe': [DVT, HEMOPTYSIS, boolean('pe_most_likely','TEP como diagnóstico más probable'), number('d_dimer_ng_mL_feu','Dímero D','ng/mL FEU')],
    'glasgow-blatchford': [{**UREA,'optional':True}, number('bun_mg_dL','BUN — usar BUN o urea, no ambos','mg/dL',optional=True), number('hemoglobin_g_dL','Hemoglobina','g/dL'), choice('sex','Sexo para tabla canónica',[('male','Masculino'),('female','Femenino')]), SBP, PULSE, *flags([('melena','Melena'),('syncope','Síncope'),('hepatic_disease','Enfermedad hepática'),('heart_failure','Insuficiencia cardíaca')])],
    'curb65': [boolean('confusion','Confusión'), UREA, RR, SBP, number('diastolic_bp_mmHg','Presión diastólica','mmHg'), AGE],
    'nihss': [choice('items.'+k, label, [(i,str(i)) for i in range(NIHSS_ITEM_MAX[k]+1)]+[('UN','No evaluable (UN)')]) for k,label in zip(NIHSS_ITEM_MAX, ['1a. Nivel de consciencia','1b. Preguntas','1c. Órdenes','2. Mirada','3. Campos visuales','4. Paresia facial','5a. Brazo izquierdo','5b. Brazo derecho','6a. Pierna izquierda','6b. Pierna derecha','7. Ataxia','8. Sensibilidad','9. Lenguaje','10. Disartria','11. Extinción/inatención'])],
    'glasgow-coma': [choice(k,label,[(v,f'{v} · {name.replace("_"," ")}') for name,v in mapping.items()]+[('NT','No evaluable (NT)')]) for k,label,mapping in [('eye','Apertura ocular',GCS_EYE),('verbal','Respuesta verbal',GCS_VERBAL),('motor','Respuesta motora',GCS_MOTOR)]],
}


def catalog():
    registry = load_registry()
    evidence = json.loads((ROOT/'references/evidence-registry.json').read_text(encoding='utf-8'))['modules']['clinical-scores-calculators']
    scores = [{**next(s for s in registry['scales'] if s['id']==sid), 'fields':fields} for sid, fields in FORMS.items()]
    digest = hashlib.sha256(json.dumps(scores, sort_keys=True).encode())
    for name in sorted({s['engine'] for s in scores} | {'scripts/clinical_calculator.py'}):
        digest.update((ROOT/name).read_bytes())
    return {'revision':digest.hexdigest(), 'scores':scores, 'total_scales':len(registry['scales']),
            'total_formulas':len(registry['formulas']), 'backlog':[s for s in registry['scales'] if s['id'] not in FORMS],
            'evidence':evidence, 'clinical_status':'CLINICALLY_PENDING'}


def calculate_request(payload):
    if not isinstance(payload, dict):
        raise ValueError('request must be an object')
    cat = catalog()
    if payload.get('revision') != cat['revision']:
        raise ValueError('Score catalog changed; reload the form')
    sid = payload.get('score_id')
    if not isinstance(sid,str) or sid not in FORMS:
        raise ValueError('Unsupported interactive score')
    values = payload.get('values')
    if not isinstance(values,dict):
        raise ValueError('values must be an object')
    known = {f['key'] for f in FORMS[sid]}
    if set(values)-known:
        raise ValueError('Unknown input field')
    inputs = {}
    for f in FORMS[sid]:
        value = values.get(f['key'])
        if value is None:
            if f['optional']:
                continue
            raise ValueError(f"{f['label']}: required")
        if f['type']=='number':
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                raise ValueError(f"{f['label']}: finite number required")
            if f['integer'] and not float(value).is_integer():
                raise ValueError(f"{f['label']}: integer required")
            if (f['minimum'] is not None and value<f['minimum']) or (f['maximum'] is not None and value>f['maximum']):
                raise ValueError(f"{f['label']}: out of range")
        elif not any(type(value) is type(o['value']) and value==o['value'] for o in f['options']):
            raise ValueError(f"{f['label']}: unsupported value")
        parts = f['key'].split('.')
        target = inputs
        for part in parts[:-1]:
            target = target.setdefault(part,{})
        target[parts[-1]] = value
    result = calculate_scale(sid,inputs)
    json.dumps(result, allow_nan=False)
    return {'score_id':sid, 'inputs':inputs, 'result':result, 'revision':cat['revision'],
            'evidence':cat['evidence'], 'clinical_status':'CLINICALLY_PENDING'}
