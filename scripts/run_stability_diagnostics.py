"""
Standalone counterfactual stability diagnostic script.
Reddit DME_CONVERSIONS panel — FY26 Q1

Usage:
    cd /Users/ppavuluri/Desktop/FY26/Q1/Reddit
    python run_stability_diagnostics.py
"""
import sys
import json
import pickle
import warnings
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REDDIT_DIR_CONFIG = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v1")
DATASETS_PKL  = REDDIT_DIR_CONFIG / "mmt_datasets.pkl"
CONFIG_JSON   = REDDIT_DIR_CONFIG / "mmt_config.json"
OUTPUT_TXT    = REDDIT_DIR_CONFIG / "stability_diagnostics_output.txt"

# ---------------------------------------------------------------------------
# Experiment windows
# ---------------------------------------------------------------------------
TRAIN_END         = "2025-12-06"
PSEUDO_TEST_START = "2025-12-13"
PSEUDO_TEST_END   = "2026-01-17"

# ---------------------------------------------------------------------------
# Stability test settings
# ---------------------------------------------------------------------------
ESTIMATORS = ("TBRRidge", "AugSynthCVXPY")

# ---------------------------------------------------------------------------
# Panel-exp import
# ---------------------------------------------------------------------------
PANEL_EXP_ROOT = Path("/Users/ppavuluri/Desktop/latest_pxp/panel_exp")
if str(PANEL_EXP_ROOT) not in sys.path:
    sys.path.insert(0, str(PANEL_EXP_ROOT))

from panel_exp.utils.counterfactual_stability_tests import (
    run_counterfactual_stability_tests,
    build_pseudo_test_paneldataset,
    compare_estimator_stability,
    check_AugSynthCVXPY_weight_health,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class Tee:
    """Write to both stdout and a buffer so we can save to file at the end."""
    def __init__(self):
        self._buf = StringIO()

    def print(self, *args, **kwargs):
        line = " ".join(str(a) for a in args)
        print(line, **kwargs)
        self._buf.write(line + "\n")

    def save(self, path: Path):
        path.write_text(self._buf.getvalue())
        print(f"\n[OUTPUT] Saved to {path}")


out = Tee()


def section(title):
    bar = "=" * 70
    out.print(f"\n{bar}")
    out.print(f"  {title}")
    out.print(bar)


# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
section("1. Loading data")

with open(DATASETS_PKL, "rb") as f:
    datasets = pickle.load(f)

with open(CONFIG_JSON) as f:
    cfg = json.load(f)

long_df = datasets["DME_CONVERSIONS"]
out.print(f"Long frame shape: {long_df.shape}")
out.print(f"Date range: {long_df['date'].min().date()} → {long_df['date'].max().date()}")

# Pivot to wide format: rows=geo, cols=date
kpi_col = cfg["kpi"]["DME_CONVERSIONS"]   # "conversions"
wide = (
    long_df.pivot_table(index="geo", columns="date", values=kpi_col, aggfunc="sum")
    .sort_index()
)
wide.columns = pd.to_datetime(wide.columns)
out.print(f"Wide frame shape: {wide.shape}  (rows=geos, cols=dates)")

treated_units = cfg["test_groups"]["Reddit"]
control_units = cfg["control_groups"]["Reddit"]

test_start_date = cfg["test_start_dates"]["Reddit"]
test_end_date = cfg["test_end_dates"]["Reddit"]

# Keep only geos present in wide
treated_units = [g for g in treated_units if g in wide.index]
control_units = [g for g in control_units if g in wide.index]
out.print(f"Treated geos: {len(treated_units)}")
out.print(f"Control geos: {len(control_units)}")

# Subset wide to treated + control
all_geos = list(treated_units) + list(control_units)
wide = wide.loc[all_geos].fillna(0)

# ---------------------------------------------------------------------------
# 2. Build pseudo-test PanelDataset
# ---------------------------------------------------------------------------
section("2. Building pseudo-test PanelDataset")

pds = build_pseudo_test_paneldataset(
    data=wide,
    treated_units=treated_units,
    train_end=TRAIN_END,
    pseudo_test_start=PSEUDO_TEST_START,
    pseudo_test_end=PSEUDO_TEST_END,
)
out.print(f"PanelDataset: {pds.wide_data.shape[0]} units × {pds.wide_data.shape[1]} timepoints")
out.print(f"  treated_units={len(pds.treated_units)}, treated_start_idx={pds.treated_start_idxs}")

# ---------------------------------------------------------------------------
# 3. AugSynth weight health
# ---------------------------------------------------------------------------
section("3. AugSynth weight health check")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    weight_health = check_AugSynthCVXPY_weight_health(pds)

out.print(f"Verdict      : {weight_health['verdict']}")
out.print(f"n_effective  : {weight_health['n_effective_donors']} / {weight_health['n_total_donors']}")
out.print(f"max_weight   : {weight_health['max_weight']:.4f}")
out.print(f"top3_share   : {weight_health['top3_weight_share']:.4f}")
out.print(f"weight_entropy: {weight_health['weight_entropy']:.4f}")
out.print(f"Notes        : {weight_health['notes']}")

# Top 5 donors
if weight_health.get("donor_names") and weight_health.get("weights") is not None:
    w = np.asarray(weight_health["weights"])
    names = weight_health["donor_names"]
    if len(names) == len(w):
        top5_idx = np.argsort(w)[::-1][:5]
        out.print("\nTop 5 donors by SCM weight:")
        for rank, idx in enumerate(top5_idx, 1):
            out.print(f"  {rank}. geo={names[idx]}  weight={w[idx]:.4f}")

# ---------------------------------------------------------------------------
# 4. Run counterfactual stability tests (TBRRidge + AugSynth)
# ---------------------------------------------------------------------------
section("4. Counterfactual stability tests")

out.print(f"Estimators: {ESTIMATORS}")
out.print(f"Training window: up to {TRAIN_END}")
out.print(f"Pseudo-test window: {PSEUDO_TEST_START} → {PSEUDO_TEST_END}")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stability = run_counterfactual_stability_tests(
        data=wide,
        treated_units=treated_units,
        train_end=TRAIN_END,
        pseudo_test_start=PSEUDO_TEST_START,
        pseudo_test_end=PSEUDO_TEST_END,
        control_units=control_units,
        estimators=ESTIMATORS,
        auto_detect_break=True,
        break_detection_method="cusum_residual",
        alpha=0.05,
        control_transform="auto",
        run_heterogeneity_check=True,
    )

# Break candidates
out.print(f"\nBreak candidates detected: {len(stability.break_candidates)}")
for bc in stability.break_candidates:
    out.print(f"  {bc}")

# Control heterogeneity
if stability.control_heterogeneity is not None:
    h = stability.control_heterogeneity
    out.print(f"\nControl heterogeneity:")
    out.print(f"  CV spike ratio       : {h.cv_spike_ratio:.3f}")
    out.print(f"  Recommended transform: {h.recommended_transform}")
    out.print(f"  n_correlation_stable : {h.n_correlation_stable}")
    out.print(f"  n_correlation_degraded: {h.n_correlation_degraded}")
    out.print(f"  Notes                : {h.notes}")

# Residual drift results
out.print(f"\nResidual drift results ({len(stability.residual_drift_tests)}):")
for r in stability.residual_drift_tests:
    out.print(f"\n  Estimator           : {r.estimator}")
    out.print(f"  p_value (bias)      : {r.residual_mean_p_value:.4f}  (centered={r.residual_centered_flag})")
    out.print(f"  p_value (drift)     : {r.residual_slope_p_value:.4f}  (no_drift={not r.residual_drift_flag})")
    out.print(f"  residual_mean       : {r.residual_mean:.4f}")
    out.print(f"  residual_rmse       : {r.residual_rmse:.4f}")
    if r.rmse_ratio is not None:
        out.print(f"  rmse_ratio          : {r.rmse_ratio:.3f}  (pseudo_test / training)")
    if r.training_rmse is not None:
        out.print(f"  training_rmse       : {r.training_rmse:.4f}")
    if r.training_resid_mean is not None:
        out.print(f"  training_resid_mean : {r.training_resid_mean:.4f}")
    if r.training_resid_std is not None:
        out.print(f"  training_resid_std  : {r.training_resid_std:.4f}")
    if r.training_resid_max_abs is not None:
        out.print(f"  training_resid_max  : {r.training_resid_max_abs:.4f}")
    out.print(f"  Notes               : {r.notes}")

# ---------------------------------------------------------------------------
# 5. Estimator agreement check
# ---------------------------------------------------------------------------
section("5. Estimator agreement (TBRRidge vs AugSynthCVXPY)")

if len(stability.residual_drift_tests) >= 2:
    agreement = compare_estimator_stability(stability.residual_drift_tests)
    out.print(f"Estimator A       : {agreement.get('estimator_a')}")
    out.print(f"Estimator B       : {agreement.get('estimator_b')}")
    out.print(f"Agreement         : {agreement.get('agreement')}")
    out.print(f"Both centered     : {agreement.get('both_centered')}")
    out.print(f"Bias ratio        : {agreement.get('bias_ratio', float('nan')):.4f}")
    out.print(f"RMSE ratio gap    : {agreement.get('rmse_ratio_gap', float('nan')):.3f}")
    out.print(f"Interpretation    : {agreement.get('interpretation')}")
else:
    out.print("Only one estimator result — skipping agreement check.")
    agreement = {}

# ---------------------------------------------------------------------------
# 6. Final recommendation
# ---------------------------------------------------------------------------
section("6. Final recommendation")

def _any_drift(stability):
    return any(r.residual_drift_flag for r in stability.residual_drift_tests)

def _any_bias(stability):
    return any(not r.residual_centered_flag for r in stability.residual_drift_tests)

def _model_degraded(stability):
    return any(
        (r.rmse_ratio or 0) > 2.0 for r in stability.residual_drift_tests
    )

has_drift  = _any_drift(stability)
has_bias   = _any_bias(stability)
degraded   = _model_degraded(stability)
estimator_disagree = agreement.get("agreement") == "disagree"
weight_degenerate  = weight_health["is_degenerate"]

if not has_drift and not has_bias and not degraded:
    branch = "A"
    rec = (
        "BRANCH A — Stable. No significant residual drift or bias detected. "
        "Proceed with live inference using both TBRRidge and AugSynth."
    )
elif has_drift and not has_bias and not degraded:
    branch = "B"
    rec = (
        "BRANCH B — Drift detected but no bias. Possible non-stationarity in "
        "the control pool around the pseudo-test window. Inspect break candidates "
        "and consider restricting the training window or using TBRRidge only."
    )
elif has_bias and not degraded:
    branch = "C"
    rec = (
        "BRANCH C — Bias detected. Residuals are not centred. Check for a "
        "structural level-shift in treated units before the pseudo-test window. "
        "Consider using AugSynthCVXPY (which corrects for bias) or extending training data."
    )
elif degraded:
    if weight_degenerate:
        branch = "D"
        rec = (
            "BRANCH D — Model accuracy degraded AND AugSynth weights are degenerate. "
            "AugSynth is over-fitting to a single donor. Use TBRRidge for live inference. "
            "Investigate whether training RMSE near-zero reflects unit scale mismatch."
        )
    else:
        branch = "D2"
        rec = (
            "BRANCH D2 — Model accuracy degraded but weight distribution looks OK. "
            "High rmse_ratio may reflect a genuine regime change in the pseudo-test window. "
            "Cross-check with break candidates. Prefer TBRRidge if AugSynthCVXPY rmse_ratio > 3."
        )
elif estimator_disagree:
    branch = "E"
    rec = (
        "BRANCH E — Estimators disagree on bias. One estimator detects bias while the "
        "other does not. Investigate which estimator's residuals are more reliable given "
        "the control heterogeneity result. Default to TBRRidge for robustness."
    )
else:
    branch = "F"
    rec = (
        "BRANCH F — Mixed signals. Review detailed outputs above and use expert judgement."
    )

out.print(f"\nBranch: {branch}")
out.print(f"\n{rec}")

# Summary flags
out.print(f"\nSummary flags:")
out.print(f"  has_drift          = {has_drift}")
out.print(f"  has_bias           = {has_bias}")
out.print(f"  model_degraded     = {degraded}")
out.print(f"  estimator_disagree = {estimator_disagree}")
out.print(f"  weight_degenerate  = {weight_degenerate}")

# Save
out.save(OUTPUT_TXT)
