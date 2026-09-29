#!/usr/bin/env python3
"""Generate reference pump rates with the skill package's own calculator.

Usage: python3 scripts/python_expected.py /path/to/v135 > src/lib/__fixtures__/python-expected.json

Imports scripts/infusion_calculator.py from the v1.35 skill package and evaluates every
worked example in src/data/drugs.json, so the TypeScript engine can be cross-checked
against an independent implementation.
"""
import importlib.util
import json
import pathlib
import sys

skill = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../v135")
spec = importlib.util.spec_from_file_location("ic", skill / "scripts" / "infusion_calculator.py")
ic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ic)

root = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((root / "src" / "data" / "drugs.json").read_text())
MASS = {"ng": 1e-3, "mcg": 1.0, "mg": 1e3}  # in micrograms

out = []
for d in data["drugs"]:
    preps = {p["id"]: p for p in d["preparations"]}
    for ex in d["workedExamples"]:
        p = preps[ex["preparationId"]]
        dose, unit, w = ex["dose"], ex["doseUnit"], ex["weightKg"]
        c_val = p["concentration"]["value"]
        c_amt = p["concentration"]["unit"].split("/")[0]
        amt, *rest = unit.split("/")
        per_kg = "kg" in rest
        per_min = rest[-1] == "min"
        if unit == "mcg/kg/min" and p["amount"] and p["finalVolumeMl"] and c_amt == "mcg":
            method = "infusion_ml_h"
            ml_h = ic.infusion_ml_h(p["amount"]["value"] * (MASS[p["amount"]["unit"]] / 1000.0),
                                    p["finalVolumeMl"], dose, w)["ml_h"]
        else:
            factor = 1.0 if amt == c_amt else MASS[amt] / MASS[c_amt]
            dose_conv = dose * factor * (60.0 if per_min else 1.0)
            if per_kg:
                method = "weight_per_hour_ml_h"
                ml_h = ic.weight_per_hour_ml_h(dose_conv, w, c_val)
            else:
                method = "fixed_dose_ml_h"
                ml_h = ic.fixed_dose_ml_h(dose_conv, c_val)
        out.append({"drug": d["id"], "preparationId": p["id"], "dose": dose, "doseUnit": unit,
                    "weightKg": w, "method": method, "mlPerHour": ml_h})
json.dump({"source": "v1.35 scripts/infusion_calculator.py", "cases": out}, sys.stdout, indent=1)
print()
