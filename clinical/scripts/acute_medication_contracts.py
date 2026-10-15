"""Reviewed, source-bound acute medication contracts. No frontend dosing rules."""


def field(key, label, kind='boolean', **rules):
    return {'key': key, 'label': label, 'kind': kind, **rules}


def common(route='IV', population='adult'):
    return [
        field('population', 'Población', 'choice', options=['adult', 'pediatric'], expected=population),
        field('route', 'Vía', 'choice', options=['IV', 'IM', 'SC', 'PO'], expected=route),
        field('indication_confirmed', 'Indicación y fase confirmadas por el profesional', expected=True),
        field('allergy_contraindication_present', 'Alergia o contraindicación para esta opción', expected=False),
        field('interaction_reviewed', 'Interacciones, función renal/hepática y embarazo revisados', expected=True),
        field('monitoring_ready', 'Monitorización y medios de rescate disponibles', expected=True),
        field('local_protocol_verified', 'Protocolo local y contexto de uso verificados', expected=True),
    ]


AMIODARONE = [
    {'id': 'amiodarone-arrest-third', 'label': 'FV/TV sin pulso — después de tres descargas',
     'module': 'adult-cardiac-arrest', 'dose': 300,
     'anchors': ['300 mg IV after a total of three shocks'],
     'fields': [field('shock_count', 'Número de descargas completadas', 'number', expected=3)],
     'administration': '300 mg IV después de un total de tres descargas; seguir ALS y continuar RCP.'},
    {'id': 'amiodarone-arrest-fifth', 'label': 'FV/TV sin pulso — dosis adicional después de cinco descargas',
     'module': 'adult-cardiac-arrest', 'dose': 150,
     'anchors': ['a further 150 mg IV after a total of five shocks'],
     'fields': [field('shock_count', 'Número de descargas completadas', 'number', expected=5),
                field('prior_300mg_given', 'Dosis previa de 300 mg de este algoritmo confirmada', expected=True)],
     'administration': '150 mg IV adicionales después de un total de cinco descargas; continuar ALS.'},
    {'id': 'amiodarone-failed-cardioversion', 'label': 'Con pulso — cardioversión fallida e inestabilidad persistente',
     'module': 'adult-arrhythmias', 'dose': 300,
     'anchors': ['amiodarone 300 mg IV over 10--20 min'],
     'fields': [field('failed_cardioversion_unstable', 'Cardioversión fallida con inestabilidad persistente', expected=True),
                field('duration_min', 'Duración seleccionada (min)', 'number', minimum=10, maximum=20)],
     'administration': '300 mg IV en 10–20 min según protocolo local; volver a intentar cardioversión.'},
    {'id': 'amiodarone-maintenance', 'label': 'Mantenimiento asociado a la carga del circuito de cardioversión',
     'module': 'adult-arrhythmias', 'dose': 900,
     'anchors': ['amiodarone may be followed by 900 mg over 24 h'],
     'fields': [field('loading_pathway_confirmed', 'Carga previa y continuación de este circuito confirmadas', expected=True)],
     'duration_min': 1440,
     'administration': '900 mg durante 24 h en el contexto de continuación descrito; no aplicar a otra indicación.'},
]


def regimens():
    rows = []
    for item in AMIODARONE:
        rows.append({
            **item, 'group': 'amiodarone', 'group_label': 'Amiodarona', 'drug': 'Amiodarona',
            'route': 'IV', 'dose_unit': 'mg', 'model': 'fixed',
            'bundle': 'cardiovascular.md', 'concentration': {'value': 50, 'unit': 'mg/mL', 'role': 'stock'},
            'localization_drug': 'amiodarone',
            'product_anchor': '50 mg/mL; ampoule 3 mL',
            'fields': common() + [field('concentration', 'Concentración del producto (mg/mL; no dilución final)', 'number', expected=50, positive=True),
                                  field('product_verified', 'Presentación exacta y concentración del producto comprobadas', expected=True)] + item['fields'],
            'preparation': None, 'compatibility': None, 'stability': None, 'maximum': None,
            'limitations': ['Diluyente, concentración final, estabilidad y acceso local no especificados en el registro.',
                            'mL extraídos del producto no equivalen a mL de administración ni a mL/h de bomba.',
                            'No hay pauta independiente de FA estable ni de 600 mg/24 h en este contrato.'],
        })
    return rows + insulin_regimens()


def contract(rid, label, group, group_label, drug, bundle, module, anchors, fields,
             route='IV', population='adult', **values):
    """Absent clinical values remain absent; callers supply all numeric rules."""
    return {'id': rid, 'label': label, 'group': group, 'group_label': group_label,
            'drug': drug, 'bundle': bundle, 'module': module, 'anchors': anchors,
            'route': route, 'fields': common(route, population) + fields,
            'model': 'fixed', 'dose': None, 'dose_unit': None, 'concentration': None,
            'preparation': None, 'compatibility': None, 'stability': None, 'maximum': None,
            'administration': '', 'limitations': ['Revisión clínica y conciliación local pendientes.'], **values}


def insulin_regimens():
    rows = []
    for suffix, label, key, extra in [
        ('dka', 'DKA — fase inicial', 'dka_or_mixed_initial', [field('dka_or_mixed_confirmed', 'DKA confirmada; no HHS aislado', expected=True), field('glucose_mg_dl', 'Glucosa (mg/dL)', 'number', minimum=250)]),
        ('mixed', 'DKA/HHS mixto — fase inicial', 'dka_or_mixed_initial', [field('dka_or_mixed_confirmed', 'DKA/HHS mixto confirmado', expected=True), field('glucose_mg_dl', 'Glucosa (mg/dL)', 'number', minimum=250)]),
        ('dextrose', 'DKA — glucosa inferior a 250 mg/dL / euglucémica', 'dka_after_glucose_below_250', [field('dka_or_mixed_confirmed', 'DKA o DKA/HHS mixto confirmado', expected=True), field('glucose_mg_dl', 'Glucosa (mg/dL)', 'number', positive=True, exclusive_maximum=250), field('dextrose_started', 'Dextrosa 5–10% y plan de continuación hasta resolución establecidos', expected=True)]),
        ('hhs', 'HHS sin cetosis/acidosis significativa', 'hhs_without_significant_ketosis', [field('hhs_without_ketosis_acidosis', 'HHS confirmado sin cetosis/acidosis significativa', expected=True), field('fluid_osmolality_plan', 'Fluidos iniciales y control seriado de osmolalidad establecidos', expected=True), field('glucose_mg_dl', 'Glucosa actual (mg/dL)', 'number', positive=True)]),
    ]:
        rows.append(contract('insulin-' + suffix, label, 'insulin', 'Insulina / DKA', 'Insulina soluble/regular',
            'renal-metabolic.md', 'diabetic-ketoacidosis-hhs',
            ['0.1 units/kg/h', '0.05 units/kg/h', '100 units in a final volume of 100 mL', 'potassium is above 3.5 mmol/L'],
            [field('weight_kg', 'Peso verificado (kg)', 'number', positive=True),
             field('potassium_mmol_l', 'Potasio previo a insulina (mmol/L)', 'number', exclusive_minimum=3.5),
             field('concentration', 'Concentración final verificada (units/mL)', 'number', expected=1),
             field('preparation_verified', '100 unidades en volumen FINAL de 100 mL de NaCl 0,9%; producto y cebado local verificados', expected=True)] + extra,
            model='insulin', insulin_key=key, dose_unit='units/h',
            concentration={'value': 1, 'unit': 'units/mL', 'role': 'final'},
            preparation='Insulina soluble/regular: 100 unidades en volumen FINAL de 100 mL de NaCl 0,9%; 1 unidad/mL. Cebado según protocolo local.',
            administration='Perfusión IV continua mediante bomba. No es un bolo. Vigilar glucosa, potasio, cetonas, pH, fluidos y osmolalidad según el módulo completo.',
            limitations=['K = 3,5 mmol/L se bloquea conservadoramente: la fuente exige superar 3,5 para iniciar/reanudar; requiere revisión profesional.',
                         'No calcula reposición de potasio ni dosis subcutánea de transición. No suspender por normalización aislada de glucosa.',
                         'Diagnóstico y fase requieren confirmación profesional; no se diagnostican automáticamente con estos campos.']))
    return rows
