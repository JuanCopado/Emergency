import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from clinical_scores_api import catalog, calculate_request, FORMS
from clinical_calculator import calculate_scale

CASES=json.loads((ROOT/'qa/V1.44_SCORE_CASES.json').read_text(encoding='utf-8'))['cases']

def flat(data, prefix=''):
    out={}
    for key,value in data.items():
        key=prefix+key
        if isinstance(value,dict):out.update(flat(value,key+'.'))
        else:out[key]=value
    return out

class ScoresApiTests(unittest.TestCase):
    def test_inventory_and_sources(self):
        c=catalog()
        self.assertEqual((c['total_scales'],c['total_formulas'],len(c['scores'])),(135,45,13))
        self.assertEqual(len(c['backlog']),122)
        self.assertEqual(set(FORMS),{x['id'] for x in CASES})
        for s in c['scores']:
            self.assertTrue(s['source_url'].startswith('https://'))
            self.assertEqual(len(s['fields']),len({f['key'] for f in s['fields']}))

    def test_stale_revision_and_unknown_score_rejected(self):
        with self.assertRaisesRegex(ValueError,'reload'):calculate_request({'revision':'stale'})
        with self.assertRaisesRegex(ValueError,'Unsupported'):calculate_request({'revision':catalog()['revision'],'score_id':[]})

def scenario(case, variant):
    def test(self):
        payload={'revision':catalog()['revision'],'score_id':case['id'],'values':flat(case['normal' if variant in ('missing','invalid') else variant])}
        if variant in ('missing','invalid'):
            field=next(f for f in FORMS[case['id']] if not f['optional'])
            if variant=='missing':del payload['values'][field['key']]
            else:payload['values'][field['key']]={'unexpected':'type'}
            with self.assertRaises(ValueError):calculate_request(payload)
            return
        result=calculate_request(deepcopy(payload))
        self.assertEqual(result['result'],calculate_scale(case['id'],case[variant]))
        for key,value in case['expected_'+variant].items():self.assertEqual(result['result'][key],value)
        self.assertEqual(result['clinical_status'],'CLINICALLY_PENDING')
        json.dumps(result,allow_nan=False)
    return test

for case in CASES:
    for variant in ('normal','boundary','invalid','missing'):
        setattr(ScoresApiTests,'test_'+case['id'].replace('-','_')+'_'+variant,scenario(case,variant))
