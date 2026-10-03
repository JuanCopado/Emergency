#!/usr/bin/env python3
"""Deterministic central medical formula engine.
It performs arithmetic only. It does not select diagnoses or treatments.
"""
import math

def require(d, *keys):
    missing=[k for k in keys if d.get(k) is None]
    if missing:
        raise ValueError("missing: "+", ".join(missing))

def calculate(fid, d):
    if fid=="map":
        require(d,"SBP","DBP"); return ((d["SBP"]+2*d["DBP"])/3,"mmHg")
    if fid in ("shock-index-formula","shock-index"):
        require(d,"HR","SBP"); return (d["HR"]/d["SBP"],"ratio")
    if fid=="modified-shock-index-formula":
        require(d,"HR","MAP"); return (d["HR"]/d["MAP"],"ratio")
    if fid=="anion-gap":
        require(d,"Na","Cl","HCO3"); return (d["Na"]-(d["Cl"]+d["HCO3"]),"mmol/L")
    if fid=="albumin-corrected-anion-gap":
        require(d,"AG","albumin_g_dL"); return (d["AG"]+2.5*(4-d["albumin_g_dL"]),"mmol/L")
    if fid=="delta-ratio":
        require(d,"AGcorr","HCO3"); return ((d["AGcorr"]-12)/(24-d["HCO3"]),"ratio")
    if fid=="winter-pco2":
        require(d,"HCO3"); return (1.5*d["HCO3"]+8,"mmHg (expected ±2)")
    if fid=="calculated-osmolality":
        require(d,"Na","glucose_mg_dL","BUN_mg_dL"); return (2*d["Na"]+d["glucose_mg_dL"]/18+d["BUN_mg_dL"]/2.8,"mOsm/kg")
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
        sf=0.85 if str(d["sex"]).lower() in ("f","female","mujer") else 1.0
        return (((140-d["age"])*d["weight_kg"])/(72*d["Scr_mg_dL"])*sf,"mL/min")
    if fid=="bedside-schwartz":
        require(d,"height_cm","Scr_mg_dL"); return (0.413*d["height_cm"]/d["Scr_mg_dL"],"mL/min/1.73m2")
    if fid=="fena":
        require(d,"UNa","PCr","PNa","UCr"); return (100*(d["UNa"]*d["PCr"])/(d["PNa"]*d["UCr"]),"percent")
    if fid=="feurea":
        require(d,"UUrea","PCr","PUrea","UCr"); return (100*(d["UUrea"]*d["PCr"])/(d["PUrea"]*d["UCr"]),"percent")
    if fid=="pao2-fio2":
        require(d,"PaO2_mmHg","FiO2_fraction"); return (d["PaO2_mmHg"]/d["FiO2_fraction"],"mmHg")
    if fid=="spo2-fio2":
        require(d,"SpO2_percent","FiO2_fraction"); return (d["SpO2_percent"]/d["FiO2_fraction"],"ratio")
    if fid in ("rox","rox-index"):
        require(d,"SpO2_percent","FiO2_fraction","RR"); return ((d["SpO2_percent"]/d["FiO2_fraction"])/d["RR"],"ratio")
    if fid=="static-compliance":
        require(d,"VT_mL","Pplat","PEEP"); return (d["VT_mL"]/(d["Pplat"]-d["PEEP"]),"mL/cmH2O")
    if fid=="driving-pressure":
        require(d,"Pplat","PEEP"); return (d["Pplat"]-d["PEEP"],"cmH2O")
    if fid=="minute-ventilation":
        require(d,"VT_L","RR"); return (d["VT_L"]*d["RR"],"L/min")
    if fid=="bsa-mosteller":
        require(d,"height_cm","weight_kg"); return (math.sqrt(d["height_cm"]*d["weight_kg"]/3600),"m2")
    if fid=="bmi":
        require(d,"weight_kg","height_m"); return (d["weight_kg"]/(d["height_m"]**2),"kg/m2")
    if fid=="holliday-segar":
        require(d,"weight_kg"); w=d["weight_kg"]
        total=100*min(w,10)+50*min(max(w-10,0),10)+20*max(w-20,0)
        return (total,"mL/day")
    if fid=="four-two-one":
        require(d,"weight_kg"); w=d["weight_kg"]
        rate=4*min(w,10)+2*min(max(w-10,0),10)+1*max(w-20,0)
        return (rate,"mL/h")
    if fid=="dehydration-deficit":
        require(d,"weight_kg","dehydration_fraction"); return (d["weight_kg"]*d["dehydration_fraction"]*1000,"mL")
    if fid=="parkland":
        require(d,"weight_kg","TBSA_percent"); return (4*d["weight_kg"]*d["TBSA_percent"],"mL/24h starting estimate")
    if fid=="mgkg-dose":
        require(d,"mg_per_kg","weight_kg"); return (d["mg_per_kg"]*d["weight_kg"],"mg")
    if fid=="mcgkgmin-to-mlh":
        require(d,"dose_mcg_kg_min","weight_kg","concentration_mcg_mL")
        return (d["dose_mcg_kg_min"]*d["weight_kg"]*60/d["concentration_mcg_mL"],"mL/h")
    if fid=="mgkgh-to-mlh":
        require(d,"dose_mg_kg_h","weight_kg","concentration_mg_mL")
        return (d["dose_mg_kg_h"]*d["weight_kg"]/d["concentration_mg_mL"],"mL/h")
    if fid=="unitskgh-to-mlh":
        require(d,"dose_units_kg_h","weight_kg","concentration_units_mL")
        return (d["dose_units_kg_h"]*d["weight_kg"]/d["concentration_units_mL"],"mL/h")
    if fid=="qtc-bazett":
        require(d,"QT_s","RR_s"); return (d["QT_s"]/math.sqrt(d["RR_s"]),"s")
    if fid=="qtc-fridericia":
        require(d,"QT_s","RR_s"); return (d["QT_s"]/(d["RR_s"]**(1/3)),"s")
    if fid=="cao2":
        require(d,"Hb","SaO2_fraction","PaO2"); return (1.34*d["Hb"]*d["SaO2_fraction"]+0.0031*d["PaO2"],"mL O2/dL")
    if fid=="cardiac-index":
        require(d,"CO_L_min","BSA_m2"); return (d["CO_L_min"]/d["BSA_m2"],"L/min/m2")
    if fid=="svr":
        require(d,"MAP","CVP","CO_L_min"); return (80*(d["MAP"]-d["CVP"])/d["CO_L_min"],"dyn*s/cm5")
    if fid=="maddrey-formula":
        require(d,"PT_patient","PT_control","bilirubin_mg_dL"); return (4.6*(d["PT_patient"]-d["PT_control"])+d["bilirubin_mg_dL"],"points")
    raise ValueError("formula not implemented: "+fid)

def sum_components(values, minimum=None, maximum=None):
    if not isinstance(values, dict) or not values:
        raise ValueError("components required")
    if any(v is None for v in values.values()):
        raise ValueError("all components must be explicit")
    total=sum(values.values())
    if minimum is not None and total<minimum: raise ValueError("score below valid range")
    if maximum is not None and total>maximum: raise ValueError("score above valid range")
    return total
