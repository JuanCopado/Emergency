"""Hypothetical cost arithmetic from dated, separately documented primary tariffs."""
from decimal import Decimal as D
from pathlib import Path
import json

def value(n):
    return float(n)

scenarios=[]
for users in (10,100,1000):
    requests=D(users)*20*20
    cpu=requests*D('0.2')
    memory=requests*D('0.1')
    compute_gross=cpu*D('0.00001')+memory*D('0.000002')
    compute_after_free=max(D(0),cpu-200000)*D('0.00001')+max(D(0),memory-400000)*D('0.000002')
    db_dev=D('0.0156')*730+20*D('0.0993')+60*D('0.03')
    db_pro=D('0.11')*730+20*D('0.0993')+60*D('0.03')
    objects=10*D('0.01606')
    object_egress=max(D(0),D(users)*D('0.06')-75)*D('0.01')
    scenarios.append({
        'active_physicians':users,'active_days_per_month':20,'remote_requests_per_active_day_per_user':20,
        'requests_month':int(requests),'vcpu_seconds':value(cpu),'memory_gb_seconds':value(memory),
        'peak_simultaneous_users_assumption':max(1,users//10),
        'compute_eur_without_free_allowance':value(compute_gross),
        'compute_eur_after_documented_account_allowance_if_unused_elsewhere':value(compute_after_free),
        'database_dev_illustrative_subtotal_eur':value(db_dev),
        'database_pro_illustrative_subtotal_eur':value(db_pro),
        'object_storage_eur':value(objects),'object_egress_assumption_gb':value(D(users)*D('0.06')),
        'object_egress_eur':value(object_egress),
        'known_technical_subtotal_dev_eur_excluding_identity_and_other_charges':value(db_dev+objects+object_egress+compute_after_free),
        'known_technical_subtotal_pro_eur_excluding_identity_and_other_charges':value(db_pro+objects+object_egress+compute_after_free),
        'zitadel_illustrative_plan':'Free' if users<=100 else 'Pro',
        'zitadel_base_usd':0 if users<=100 else 100,
        'zitadel_usage_unit_contract_clarification_pending':True,
        'measured_load_or_cost':False,
    })

out={'schema':'emergency.implementation.cost-hypotheses.v1','observed_date':'2026-11-27',
     'author':'Work/Codex; not Claude','provider_selected':False,'purchases_or_resources_created':False,
     'not_tco':True,'not_regional_quote_for_google':True,
     'excluded':['tax','exchange_rates','support','SLA','domain','transactional_email','MFA_SMS',
                 'logs_metrics_traces','CI_registry_scanners','AI_tokens','operator_labor','HA_additional_nodes',
                 'cold_start_or_idle_instances','network_not_covered_by_object_storage_tariff'],
     'scenarios':scenarios}
Path(__file__).with_name('COSTES_ESCENARIOS_WORK.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'scenarios':len(scenarios),'not_tco':True,'compute_gross_eur':[s['compute_eur_without_free_allowance'] for s in scenarios]}))
