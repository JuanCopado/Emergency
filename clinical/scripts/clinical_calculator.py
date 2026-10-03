#!/usr/bin/env python3
"""Deterministic central medical calculator engine.

Safety boundary:
- formulas perform arithmetic only;
- component-sum scales accept already-scored explicit components only;
- criteria/rule/official-table/nomogram tools are never reverse-engineered or inferred
  from free text unless a dedicated, source-validated implementation exists.
"""
import json
import math
from pathlib import Path

from core_scores_block1 import calculate_gcs, calculate_nihss, calculate_news2, calculate_sofa1
from core_scores_block2 import calculate_heart, prepare_grace2, calculate_cha2ds2_vasc, calculate_cha2ds2_va
from core_scores_block3 import calculate_wells_pe, calculate_perc, calculate_years
from core_scores_block4 import calculate_glasgow_blatchford, calculate_curb65, calculate_phoenix_sepsis
from core_score_sofa2 import calculate_sofa2
from core_scores_block5 import calculate_oakland, calculate_obstetric_shock_index, calculate_revised_baux
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
from core_scores_block14_adult_remaining import classify_duke_iscvid, classify_tokyo_biliary, calculate_four_at, classify_cam, calculate_rass, calculate_cpot, calculate_mascc, official_wrapper

REGISTRY_PATH = Path(__file__).parents[1] / "calculators" / "registry.json"


def require(d, *keys):
    missing=[k for k in keys if d.get(k) is None]
    if missing:
        raise ValueError("missing: "+", ".join(missing))


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return float(value)


def _fraction(value, name):
    value=_positive(value,name)
    if value > 1:
        raise ValueError(f"{name} must be a fraction between 0 and 1")
    return value


def _sex(value):
    x=str(value).strip().lower()
    if x in {"f","female","mujer","femenino"}: return "female"
    if x in {"m","male","hombre","masculino"}: return "male"
    raise ValueError("sex must be male/female")


def calculate(fid, d):
    if fid=="map":
        require(d,"SBP","DBP"); return ((d["SBP"]+2*d["DBP"])/3,"mmHg")
    if fid in ("shock-index-formula","shock-index"):
        require(d,"HR","SBP"); return (d["HR"]/_positive(d["SBP"],"SBP"),"ratio")
    if fid=="modified-shock-index-formula":
        require(d,"HR","MAP"); return (d["HR"]/_positive(d["MAP"],"MAP"),"ratio")
    if fid=="anion-gap":
        require(d,"Na","Cl","HCO3"); return (d["Na"]-(d["Cl"]+d["HCO3"]),"mmol/L")
    if fid=="albumin-corrected-anion-gap":
        require(d,"AG","albumin_g_dL"); return (d["AG"]+2.5*(4-d["albumin_g_dL"]),"mmol/L")
    if fid=="delta-ratio":
        require(d,"AGcorr","HCO3")
        denominator=24-d["HCO3"]
        if denominator==0: raise ValueError("delta-ratio denominator is zero")
        return ((d["AGcorr"]-12)/denominator,"ratio")
    if fid=="winter-pco2":
        require(d,"HCO3"); return (1.5*d["HCO3"]+8,"mmHg (expected ±2)")
    if fid=="calculated-osmolality":
        require(d,"Na","glucose_mg_dL","BUN_mg_dL")
        return (2*d["Na"]+d["glucose_mg_dL"]/18+d["BUN_mg_dL"]/2.8,"mOsm/kg")
    if fid=="effective-osmolality":
        require(d,"Na","glucose_mg_dL"); return (2*d["Na"]+d["glucose_mg_dL"]/18,"mOsm/kg")
    if fid=="free-water-deficit":
        require(d,"TBW_L","Na"); return (d["TBW_L"]*(d["Na"]/140-1),"L")
    if fid=="corrected-calcium":
        require(d,"Ca_mg_dL","albumin_g_dL"); return (d["Ca_mg_dL"]+0.8*(4-d["albumin_g_dL"]),"mg/dL")
    if fid=="corrected-sodium-glucose":
        require(d,"Na","glucose_mg_dL")
        factor=d.get("factor",1.6)
        return (d["Na"]+factor*((d["glucose_mg_dL"]-100)/100),"mmol/L")
    if fid=="cockcroft-gault":
        require(d,"age","weight_kg","Scr_mg_dL","sex")
        scr=_positive(d["Scr_mg_dL"],"Scr_mg_dL")
        sf=0.85 if _sex(d["sex"])=="female" else 1.0
        return (((140-d["age"])*d["weight_kg"])/(72*scr)*sf,"mL/min")
    if fid=="ckd-epi-2021":
        require(d,"age","Scr_mg_dL","sex")
        age=float(d["age"])
        if age < 18: raise ValueError("ckd-epi-2021 is an adult equation (age >=18)")
        scr=_positive(d["Scr_mg_dL"],"Scr_mg_dL")
        sex=_sex(d["sex"])
        kappa=0.7 if sex=="female" else 0.9
        alpha=-0.241 if sex=="female" else -0.302
        ratio=scr/kappa
        sex_factor=1.012 if sex=="female" else 1.0
        egfr=142*(min(ratio,1)**alpha)*(max(ratio,1)**-1.200)*(0.9938**age)*sex_factor
        return (egfr,"mL/min/1.73m2")
    if fid=="bedside-schwartz":
        require(d,"height_cm","Scr_mg_dL")
        return (0.413*d["height_cm"]/_positive(d["Scr_mg_dL"],"Scr_mg_dL"),"mL/min/1.73m2")
    if fid=="fena":
        require(d,"UNa","PCr","PNa","UCr")
        denominator=d["PNa"]*d["UCr"]
        if denominator==0: raise ValueError("fena denominator is zero")
        return (100*(d["UNa"]*d["PCr"])/denominator,"percent")
    if fid=="feurea":
        require(d,"UUrea","PCr","PUrea","UCr")
        denominator=d["PUrea"]*d["UCr"]
        if denominator==0: raise ValueError("feurea denominator is zero")
        return (100*(d["UUrea"]*d["PCr"])/denominator,"percent")
    if fid=="pao2-fio2":
        require(d,"PaO2_mmHg","FiO2_fraction")
        return (d["PaO2_mmHg"]/_fraction(d["FiO2_fraction"],"FiO2_fraction"),"mmHg")
    if fid=="spo2-fio2":
        require(d,"SpO2_percent","FiO2_fraction")
        return (d["SpO2_percent"]/_fraction(d["FiO2_fraction"],"FiO2_fraction"),"ratio")
    if fid in ("rox","rox-index"):
        require(d,"SpO2_percent","FiO2_fraction","RR")
        fio2=_fraction(d["FiO2_fraction"],"FiO2_fraction")
        rr=_positive(d["RR"],"RR")
        return ((d["SpO2_percent"]/fio2)/rr,"ratio")
    if fid=="alveolar-o2":
        require(d,"FiO2_fraction","PaCO2_mmHg")
        fio2=_fraction(d["FiO2_fraction"],"FiO2_fraction")
        patm=_positive(d.get("Patm_mmHg",760),"Patm_mmHg")
        ph2o=float(d.get("PH2O_mmHg",47))
        rq=_positive(d.get("RQ",0.8),"RQ")
        if ph2o >= patm: raise ValueError("PH2O_mmHg must be below Patm_mmHg")
        return (fio2*(patm-ph2o)-d["PaCO2_mmHg"]/rq,"mmHg")
    if fid=="aa-gradient":
        require(d,"PaO2_mmHg")
        if d.get("PAO2_mmHg") is not None:
            pao2=float(d["PAO2_mmHg"])
        else:
            pao2,_=calculate("alveolar-o2",d)
        return (pao2-d["PaO2_mmHg"],"mmHg")
    if fid=="static-compliance":
        require(d,"VT_mL","Pplat","PEEP")
        denominator=d["Pplat"]-d["PEEP"]
        if denominator<=0: raise ValueError("Pplat must be greater than PEEP")
        return (d["VT_mL"]/denominator,"mL/cmH2O")
    if fid=="driving-pressure":
        require(d,"Pplat","PEEP"); return (d["Pplat"]-d["PEEP"],"cmH2O")
    if fid=="minute-ventilation":
        require(d,"VT_L","RR"); return (d["VT_L"]*d["RR"],"L/min")
    if fid=="bsa-mosteller":
        require(d,"height_cm","weight_kg")
        return (math.sqrt(d["height_cm"]*d["weight_kg"]/3600),"m2")
    if fid=="bmi":
        require(d,"weight_kg","height_m")
        h=_positive(d["height_m"],"height_m")
        return (d["weight_kg"]/(h**2),"kg/m2")
    if fid=="ibw-devine":
        require(d,"height_cm","sex")
        height_in=_positive(d["height_cm"],"height_cm")/2.54
        base=45.5 if _sex(d["sex"])=="female" else 50.0
        return (base+2.3*(height_in-60),"kg")
    if fid=="holliday-segar":
        require(d,"weight_kg"); w=d["weight_kg"]
        total=100*min(w,10)+50*min(max(w-10,0),10)+20*max(w-20,0)
        return (total,"mL/day")
    if fid=="four-two-one":
        require(d,"weight_kg"); w=d["weight_kg"]
        rate=4*min(w,10)+2*min(max(w-10,0),10)+1*max(w-20,0)
        return (rate,"mL/h")
    if fid=="dehydration-deficit":
        require(d,"weight_kg","dehydration_fraction")
        return (d["weight_kg"]*d["dehydration_fraction"]*1000,"mL")
    if fid=="parkland":
        require(d,"weight_kg","TBSA_percent")
        return (4*d["weight_kg"]*d["TBSA_percent"],"mL/24h starting estimate")
    if fid=="mgkg-dose":
        require(d,"mg_per_kg","weight_kg"); return (d["mg_per_kg"]*d["weight_kg"],"mg")
    if fid=="final-concentration":
        require(d,"drug_amount","final_volume_mL")
        volume=_positive(d["final_volume_mL"],"final_volume_mL")
        unit=str(d.get("amount_unit","amount")).strip() or "amount"
        return (d["drug_amount"]/volume,f"{unit}/mL")
    if fid=="mcgkgmin-to-mlh":
        require(d,"dose_mcg_kg_min","weight_kg","concentration_mcg_mL")
        concentration=_positive(d["concentration_mcg_mL"],"concentration_mcg_mL")
        return (d["dose_mcg_kg_min"]*d["weight_kg"]*60/concentration,"mL/h")
    if fid=="mgkgh-to-mlh":
        require(d,"dose_mg_kg_h","weight_kg","concentration_mg_mL")
        concentration=_positive(d["concentration_mg_mL"],"concentration_mg_mL")
        return (d["dose_mg_kg_h"]*d["weight_kg"]/concentration,"mL/h")
    if fid=="unitskgh-to-mlh":
        require(d,"dose_units_kg_h","weight_kg","concentration_units_mL")
        concentration=_positive(d["concentration_units_mL"],"concentration_units_mL")
        return (d["dose_units_kg_h"]*d["weight_kg"]/concentration,"mL/h")
    if fid=="qtc-bazett":
        require(d,"QT_s","RR_s")
        return (d["QT_s"]/math.sqrt(_positive(d["RR_s"],"RR_s")),"s")
    if fid=="qtc-fridericia":
        require(d,"QT_s","RR_s")
        return (d["QT_s"]/(_positive(d["RR_s"],"RR_s")**(1/3)),"s")
    if fid=="cao2":
        require(d,"Hb","SaO2_fraction","PaO2")
        return (1.34*d["Hb"]*d["SaO2_fraction"]+0.0031*d["PaO2"],"mL O2/dL")
    if fid=="do2":
        require(d,"CO_L_min","CaO2_mL_dL")
        return (d["CO_L_min"]*d["CaO2_mL_dL"]*10,"mL O2/min")
    if fid=="cardiac-index":
        require(d,"CO_L_min","BSA_m2")
        return (d["CO_L_min"]/_positive(d["BSA_m2"],"BSA_m2"),"L/min/m2")
    if fid=="svr":
        require(d,"MAP","CVP","CO_L_min")
        return (80*(d["MAP"]-d["CVP"])/_positive(d["CO_L_min"],"CO_L_min"),"dyn*s/cm5")
    if fid=="maddrey-formula":
        require(d,"PT_patient","PT_control","bilirubin_mg_dL")
        return (4.6*(d["PT_patient"]-d["PT_control"])+d["bilirubin_mg_dL"],"points")
    if fid=="meld-na-formula":
        require(d,"bilirubin_mg_dL","INR","creatinine_mg_dL","sodium_mmol_L")
        if d.get("legacy_meld_na_acknowledged") is not True:
            raise ValueError("meld-na-formula is the legacy MELD-Na equation; current OPTN uses MELD 3.0. Set legacy_meld_na_acknowledged=true to calculate it explicitly.")
        bilirubin=max(1.0,float(d["bilirubin_mg_dL"]))
        inr=max(1.0,float(d["INR"]))
        creatinine=max(1.0,float(d["creatinine_mg_dL"]))
        if d.get("dialysis_twice_last_7_days") is True or d.get("cvvhd_24h_last_7_days") is True:
            creatinine=4.0
        creatinine=min(creatinine,4.0)
        sodium=min(max(float(d["sodium_mmol_L"]),125.0),137.0)
        meld_i=3.78*math.log(bilirubin)+11.2*math.log(inr)+9.57*math.log(creatinine)+6.43
        meld_i=min(max(meld_i,6.0),40.0)
        score=meld_i+1.32*(137-sodium)-0.033*meld_i*(137-sodium)
        return (min(max(round(score),6),40),"points (legacy MELD-Na; not current OPTN MELD 3.0)")
    raise ValueError("formula not implemented: "+fid)


def sum_components(values, minimum=None, maximum=None):
    if not isinstance(values, dict) or not values:
        raise ValueError("components required")
    if any(v is None for v in values.values()):
        raise ValueError("all components must be explicit")
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in values.values()):
        raise ValueError("components must be explicit finite numeric point values")
    total=sum(values.values())
    if minimum is not None and total<minimum: raise ValueError("score below valid range")
    if maximum is not None and total>maximum: raise ValueError("score above valid range")
    return total


def load_registry(path=REGISTRY_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_scale(scale_id, registry=None):
    registry=registry or load_registry()
    for item in registry.get("scales",[]):
        if item.get("id")==scale_id:
            return item
    raise ValueError(f"unknown scale: {scale_id}")


def calculate_scale(scale_id, data, registry=None):
    """Execute only what is encoded safely.

    For component_sum tools, callers must supply already-scored point components.
    The engine does not infer NIHSS/HEART/SOFA/etc. component points from raw
    clinical findings until their source tables are separately encoded/validated.
    Non-component tools remain fail-closed unless an explicit result and provenance
    are supplied by a dedicated validated workflow.
    """
    meta=get_scale(scale_id,registry)

    score_formula_aliases = {
        "shock-index": "shock-index-formula",
        "modified-shock-index": "modified-shock-index-formula",
        "rox-index": "rox",
        "meld-na": "meld-na-formula",
        "maddrey": "maddrey-formula",
    }
    if scale_id in score_formula_aliases:
        value, unit = calculate(score_formula_aliases[scale_id], data)
        return {
            "id": scale_id,
            "registry_id": scale_id,
            "status": "complete",
            "value": value,
            "unit": unit,
            "formula_alias": score_formula_aliases[scale_id],
            "warning": "Derived from the central formula engine; use as a clinical adjunct, not a stand-alone diagnosis or treatment rule.",
        }

    dedicated = {
        "nihss": calculate_nihss,
        "glasgow-coma": calculate_gcs,
        "news2": calculate_news2,
        "sofa": calculate_sofa1,
        "sofa-2": calculate_sofa2,
        "heart": calculate_heart,
        "grace-2": prepare_grace2,
        "cha2ds2-vasc": calculate_cha2ds2_vasc,
        "cha2ds2-va": calculate_cha2ds2_va,
        "wells-pe": calculate_wells_pe,
        "perc": calculate_perc,
        "years-pe": calculate_years,
        "glasgow-blatchford": calculate_glasgow_blatchford,
        "curb65": calculate_curb65,
        "phoenix-sepsis": calculate_phoenix_sepsis,
        "abcd2": calculate_abcd2,
        "aspects": calculate_aspects,
        "modified-rankin": calculate_modified_rankin,
        "ich-score": calculate_ich_score,
        "modified-fisher": calculate_modified_fisher,
        "cincinnati-stroke": calculate_cincinnati,
        "race-stroke": calculate_race,
        "fast-ed": calculate_fast_ed,
        "avpu": calculate_avpu,
        "pediatric-gcs": calculate_pediatric_gcs,
        "timi-ua-nstemi": calculate_timi_ua_nstemi,
        "has-bled": calculate_has_bled,
        "canadian-syncope": calculate_canadian_syncope,
        "killip-kimball": calculate_killip_kimball,
        "scai-shock": calculate_scai_shock,
        "revised-geneva": calculate_revised_geneva,
        "pesi": calculate_pesi,
        "spesi": calculate_spesi,
        "hestia": calculate_hestia,
        "wells-dvt": calculate_wells_dvt,
        "crb65": calculate_crb65,
        "psi-port": calculate_psi_port,
        "decaf": calculate_decaf,
        "berlin-ards": classify_berlin_ards,
        "rts": calculate_rts,
        "iss": calculate_iss,
        "abc-massive-transfusion": calculate_abc_massive_transfusion,
        "canadian-ct-head": calculate_canadian_ct_head,
        "canadian-cspine": calculate_canadian_cspine,
        "nexus-cspine": calculate_nexus_cspine,
        "aims65": calculate_aims65,
        "bisap": calculate_bisap,
        "child-pugh": calculate_child_pugh,
        "kings-college": calculate_kings_college,
        "qsofa": calculate_qsofa,
        "isth-dic": calculate_isth_dic,
        "kdigo-aki": classify_kdigo_aki,
        "mcmahon-rhabdo": calculate_mcmahon,
        "alvarado": calculate_alvarado,
        "air-appendicitis": calculate_air,
        "rumack-matthew": evaluate_rumack_matthew,
        "hunter-serotonin": evaluate_hunter_serotonin,
        "ciwa-ar": calculate_ciwa_ar,
        "cows": calculate_cows,
        "duke-iscvid": classify_duke_iscvid,
        "tokyo-biliary": classify_tokyo_biliary,
        "four-at": calculate_four_at,
        "cam": lambda data: classify_cam(data, False),
        "cam-icu": lambda data: classify_cam(data, True),
        "rass": calculate_rass,
        "cpot": calculate_cpot,
        "mascc": calculate_mascc,
        "oakland": calculate_oakland,
        "obstetric-shock-index": calculate_obstetric_shock_index,
        "revised-baux": calculate_revised_baux,
        "clinical-frailty": lambda data: official_wrapper("clinical-frailty", data),
        "cssrs": lambda data: official_wrapper("cssrs", data),
    }
    if scale_id in dedicated:
        result = dedicated[scale_id](data)
        result["registry_id"] = scale_id
        return result

    calc_type=meta.get("calc_type")
    base={
        "id":scale_id,
        "name":meta.get("name"),
        "calc_type":calc_type,
        "tier":meta.get("tier"),
        "measures":meta.get("measures"),
        "use":meta.get("use"),
    }
    if calc_type=="component_sum":
        components=data.get("components")
        total=sum_components(components)
        return {**base,"status":"complete_from_explicit_scored_components",
                "value":total,"components":components,
                "warning":"Component point values must come from the validated source definition; this generic engine does not infer them from raw clinical text."}

    if data.get("explicit_result") is not None:
        provenance=data.get("provenance")
        if not provenance:
            raise ValueError("provenance required for explicit non-component result")
        return {**base,"status":"explicit_result_from_validated_external_rule",
                "value_or_category":data["explicit_result"],"provenance":provenance}

    return {**base,"status":"source_rule_not_yet_encoded",
            "required":"dedicated source-validated implementation or explicit_result+provenance"}
