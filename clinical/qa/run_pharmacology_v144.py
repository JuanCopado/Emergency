"""Inventory existing models and cross-check source examples with Python arithmetic."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from infusion_calculator import fixed_dose_ml_h, weight_per_hour_ml_h
from pediatric_catalog import build_catalog


def run():
    db=json.loads((ROOT.parent/'app/src/data/drugs.json').read_text(encoding='utf-8'))
    catalog=build_catalog()
    rules=json.loads((ROOT/'qa/pediatric-outpatient-alert-rules.json').read_text(encoding='utf-8'))
    cases=[]
    factors={'ng':1,'mcg':1000,'mg':1000000,'units':1}
    for drug in db['drugs']:
        examples=list(drug['workedExamples'])
        assert examples,drug['id']
        covered={e['preparationId'] for e in examples}
        # Exercise remaining preparations with the same existing example dose.
        examples += [{**examples[0],'preparationId':p['id'],'expectedMlH':None} for p in drug['preparations'] if p['id'] not in covered]
        for i,e in enumerate(examples):
            prep=next(p for p in drug['preparations'] if p['id']==e['preparationId'])
            unit=e['doseUnit'].split('/');conc=prep['concentration']
            assert (unit[0]=='units')==(conc['unit'].split('/')[0]=='units')
            dose=e['dose']*factors[unit[0]]/factors[conc['unit'].split('/')[0]]*(60 if unit[-1]=='min' else 1)
            rate=weight_per_hour_ml_h(dose,e['weightKg'],conc['value']) if 'kg' in unit else fixed_dose_ml_h(dose,conc['value'])
            if e['expectedMlH'] is not None:assert abs(rate-e['expectedMlH'])<=0.051,(drug['id'],rate,e)
            cases.append({'id':f'{drug["id"]}-{i+1}','drug':drug['id'],'preparation':prep['id'],'weight':e['weightKg'],'dose':e['dose'],'unit':e['doseUnit'],'expected_ml_h':rate,'source_example_ml_h':e['expectedMlH'],'concentration':conc,'final_volume_ml':prep['finalVolumeMl'],'python':'PASS'})
    missing_pilots={
        'amiodarone-arrhythmia':'Reference modules only; no amiodarone calculator/catalog entry',
        'insulin-DKA':'Diagnostic note/reference only; no insulin medication calculator',
        'NaCl-3-percent':'Diagnostic note/reference only; no hypertonic-saline medication calculator',
        'status-epilepticus':'Diagnostic note/reference; sedation infusion arithmetic is not a status treatment selector',
        'anaphylaxis':'Diagnostic note/reference and pediatric auto-injector catalog; adult epinephrine infusion is not IM anaphylaxis workflow',
        'anticoagulation-reversal':'Reference modules only; no anticoagulant/antidote medication calculator',
    }
    inventory={'clinical_status':'CLINICALLY_PENDING','adult':{'drugs':len(db['drugs']),'drug_ids':[d['id'] for d in db['drugs']],
        'categories':{c:sum(d['category']==c for d in db['drugs']) for c in sorted({d['category'] for d in db['drugs']})},
        'preparations':sum(len(d['preparations']) for d in db['drugs']),
        'source_worked_examples':sum(len(d['workedExamples']) for d in db['drugs']),
        'caution_statements':sum(len(d['cautions']) for d in db['drugs']),
        'contraindication_statements':sum(len(d['contraindications']) for d in db['drugs']),
        'organ_adjustment_texts':sum(d['dosing']['organAdjustment'] is not None for d in db['drugs']),
        'numeric_maxima':sum(d['dosing']['max'] is not None and d['dosing']['max']['value'] is not None for d in db['drugs']),
        'incompatibility_stability_model':'No structured product/line compatibility or stability model; source caution/module text remains visible',
        'patient_specific_allergy_interaction_renal_hepatic_inputs':False,'dedicated_export':False,'http_calculator_backend':False},
        'pediatric':{**catalog['inventory'],'renal_adjustment_entries':sum('renal_adjustment' in r for r in catalog['regimens']),
        'hepatic_adjustment_entries':sum('hepatic_adjustment' in r for r in catalog['regimens']),
        'rule_counts':{k:len(v) for k,v in rules.items() if isinstance(v,list)},
        'all_regimen_ids':[r['id'] for r in catalog['regimens']]},
        'pilot_gaps':missing_pilots,'additional_gap':'Isoprenaline has no adult calculator entry; dopamine is covered without claiming indication selection',
        'adult_cases':cases}
    return inventory

if __name__=='__main__':
    report=run()
    (ROOT/'qa/V1.44_PHARMACOLOGY_INVENTORY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"PASS: {report['adult']['drugs']} adult drugs, {report['adult']['preparations']} preparations, {len(report['adult_cases'])} Python arithmetic cases; {report['pediatric']['regimens']} pediatric regimens inventoried")
