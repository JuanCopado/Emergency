"""OPTIONAL GEE reference analysis for Stage 1 (laboratory only; NOT part of the product and not a replacement for the stdlib tool).

statsmodels is NOT a dependency of the repository. If it is missing, every function reports NOT_IMPLEMENTED instead of failing silently.
GLMM is NOT implemented: no GLMM library is verified here (statsmodels' BinomialBayesMixedGLM is a variational/Bayesian
approximation and is not offered as a GLMM). Specification for a future GLMM: logit(P(event)) = b0 + b1*prototype + b2*period
+ b3*platform + u_participant, u ~ N(0, s^2), fitted by an independently validated library and checked against a reference dataset.
"""
import importlib.util

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import human_factors_tools as hf  # noqa: E402

GLMM_STATUS = "NOT_IMPLEMENTED"


def available():
    return all(importlib.util.find_spec(m) is not None for m in ("statsmodels", "numpy", "pandas"))


def status():
    return {"gee": "AVAILABLE_OPTIONAL" if available() else "NOT_IMPLEMENTED", "glmm": GLMM_STATUS,
            "reason": None if available() else "statsmodels/numpy/pandas not installed"}


def design(records, metric):
    """Trial-level rows for one error metric: y (event), prototype (0/1), period2 (0/1), mobile (0/1), participant. Denominators as in the tool."""
    hf.validate_records(records)
    numerator, denominator = hf.METRICS[metric]
    rows = []
    for r in records:
        f = hf.flags(r)
        if not f[denominator]:
            continue
        rows.append({"y": int(bool(f[numerator])), "prototype": int(r["condition"] == "prototype"), "period2": int(r["period"] == 2),
                     "mobile": int(r["platform"] == "mobile"), "participant": r["participant"]})
    return rows


def fit_gee(records, metric, structure="exchangeable"):
    if not available():
        return {"status": "NOT_IMPLEMENTED", "reason": "statsmodels/numpy/pandas not installed"}
    import pandas as pd
    import statsmodels.api as sm
    rows = design(records, metric)
    if not rows:
        return {"status": "NOT_ESTIMABLE", "reason": "no eligible trials for this metric"}
    frame = pd.DataFrame(rows)
    if frame["y"].nunique() < 2:
        return {"status": "NOT_ESTIMABLE", "reason": "all outcomes are identical (zero-event or all-event); report the exact descriptive bound instead"}
    for column in ("prototype", "period2", "mobile"):
        for level in (0, 1):
            subset = frame.loc[frame[column] == level, "y"]
            if len(subset) and (subset.sum() == 0 or subset.sum() == len(subset)):
                return {"status": "NOT_ESTIMABLE", "reason": f"(quasi-)complete separation: {column}={level} has only {'zero' if subset.sum() == 0 else 'all'} events; the coefficient diverges, report exact descriptive bounds"}
    exog = sm.add_constant(frame[["prototype", "period2", "mobile"]].astype(float), has_constant="add")
    import numpy as np
    if np.linalg.matrix_rank(exog.to_numpy()) < exog.shape[1]:
        return {"status": "NOT_ESTIMABLE", "reason": "design matrix is rank-deficient (collinear covariates, e.g. platform fully confounded with period)"}
    groups = pd.factorize(frame["participant"])[0]
    cov = {"exchangeable": sm.cov_struct.Exchangeable(), "independence": sm.cov_struct.Independence()}[structure]
    result = sm.GEE(frame["y"], exog, groups=groups, family=sm.families.Binomial(), cov_struct=cov).fit()
    ci = result.conf_int()
    names = list(exog.columns)
    return {"status": "ESTIMATED", "model": f"GEE-logit/{structure}", "clusters": int(len(set(groups))), "trials": int(len(frame)),
            "warning": "Small-cluster sandwich standard errors are anti-conservative; read with the participant count.",
            "coefficients": {n: {"log_odds": float(result.params[n]), "robust_se": float(result.bse[n]),
                                 "ci95": [float(ci.loc[n, 0]), float(ci.loc[n, 1])]} for n in names}}


def models_status():
    """Honest, machine-readable status of the Stage 2 models. Resolves the 'implemented vs not implemented' discrepancy by level:
    the audited core tool (stdlib) implements NONE of them; this optional lab module offers an UNCORRECTED-sandwich GEE only when
    statsmodels is installed. GEE with small-sample correction, GLMM and the device x arm interaction are NOT implemented anywhere."""
    return {"core_tool_human_factors_tools": "NOT_IMPLEMENTED_STDLIB_ONLY",
            "gee_robust_uncorrected_lab_optional": "AVAILABLE_OPTIONAL_STATSMODELS" if available() else "NOT_AVAILABLE_STATSMODELS_MISSING",
            "GEE_SMALL_SAMPLE": "NOT_IMPLEMENTED (Mancl-DeRouen / Kauermann-Carroll corrections absent)",
            "GLMM": GLMM_STATUS, "DEVICE_ARM_INTERACTION": "NOT_IMPLEMENTED",
            "reproducibility": "GEE tests run only where statsmodels is installed (see requirements-lab.txt); they are skipped in the CI of the repository"}
