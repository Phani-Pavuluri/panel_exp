"""
Break tests for top-N scan_stat candidates — Reddit DME_CONVERSIONS FY26 Q1

Loads the top-N candidates by scan_stat from break_scan_all_dates.csv and
runs the same three-test battery for each.

Three tests per candidate:
  Test 1: level/slope break in TREATED series (Chow F-test on treated aggregate)
  Test 2: treated-CONTROL relationship break (Chow F-test on treated~controls mapping)
  Test 3: residual drift — does model trained on pre-break data extrapolate cleanly?

Usage:
    cd /Users/ppavuluri/Desktop/FY26/Q1/Reddit
    python run_scanstat_candidates_diagnostics.py            # top 3 (default)
    python run_scanstat_candidates_diagnostics.py --top-n 5  # top 5
"""
import argparse
import json
import pickle
import sys
import warnings
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--top-n", type=int, default=3,
                    help="Number of top scan_stat candidates to test (default: 3)")
args = parser.parse_args()
TOP_N = args.top_n

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REDDIT_DIR_CONFIG = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v2")
DATASETS_PKL = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/mmt_datasets_oct24_extended.pkl")
CONFIG_JSON  = REDDIT_DIR_CONFIG / "mmt_config.json"
SCAN_CSV     = REDDIT_DIR_CONFIG / "break_scan_all_dates.csv"
OUTPUT_TXT   = REDDIT_DIR_CONFIG / "scanstat_candidates_diagnostics_output.txt"

# Pseudo-test window: 20 weeks after break, capped at last pre-test date
PSEUDO_WEEKS = 20
PSEUDO_CAP   = pd.Timestamp("2026-01-17")

PANEL_EXP_ROOT = Path("/Users/ppavuluri/Desktop/latest_pxp/panel_exp")
if str(PANEL_EXP_ROOT) not in sys.path:
    sys.path.insert(0, str(PANEL_EXP_ROOT))

from panel_exp.utils.counterfactual_stability_tests import (
    run_counterfactual_stability_tests,
    _default_fit_predict,
)
from panel_exp.methods.tbr import TBRRidge as _TBRRidgeCls
from panel_exp.panel_data import PanelDataset


# ---------------------------------------------------------------------------
# Tee logger
# ---------------------------------------------------------------------------
class Tee:
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


# ---------------------------------------------------------------------------
# Load top-N candidates from break_scan_all_dates.csv
# ---------------------------------------------------------------------------
scan_df = pd.read_csv(SCAN_CSV)
scan_df["date"] = pd.to_datetime(scan_df["date"])
scan_df = scan_df.sort_values("scan_stat", ascending=False).reset_index(drop=True)
top_candidates = scan_df.head(TOP_N)

CANDIDATES = []
for rank, row in enumerate(top_candidates.itertuples(), start=1):
    break_dt  = pd.Timestamp(row.date)
    train_end = (break_dt - pd.Timedelta(weeks=1)).strftime("%Y-%m-%d")
    ps_start  = break_dt.strftime("%Y-%m-%d")
    ps_end_dt = min(break_dt + pd.Timedelta(weeks=PSEUDO_WEEKS), PSEUDO_CAP)
    ps_end    = ps_end_dt.strftime("%Y-%m-%d")
    CANDIDATES.append({
        "rank"              : rank,
        "break_label"       : ps_start,
        "scan_stat"         : row.scan_stat,
        "train_end"         : train_end,
        "pseudo_test_start" : ps_start,
        "pseudo_test_end"   : ps_end,
    })


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
with open(DATASETS_PKL, "rb") as f:
    datasets = pickle.load(f)
with open(CONFIG_JSON) as f:
    cfg = json.load(f)

long_df = datasets["DME_CONVERSIONS"]
kpi_col = cfg["kpi"]["DME_CONVERSIONS"]

wide = (
    long_df.pivot_table(index="geo", columns="date", values=kpi_col, aggfunc="sum")
    .sort_index()
)
wide.columns = pd.to_datetime(wide.columns)

treated_units = [str(g) for g in cfg["test_groups"]["Reddit"] if str(g) in wide.index]
control_units = [str(g) for g in cfg["control_groups"]["Reddit"] if str(g) in wide.index]

wide = wide.loc[list(treated_units) + list(control_units)].fillna(0)

cols = wide.columns
out.print("=" * 70)
out.print("SCAN_STAT BREAK CANDIDATES DIAGNOSTIC — Reddit DME_CONVERSIONS FY26 Q1")
out.print("=" * 70)
out.print(f"Data loaded  : {wide.shape[0]} units × {wide.shape[1]} periods")
out.print(f"Date range   : {cols[0].date()} → {cols[-1].date()}")
out.print(f"Treated DMAs : {len(treated_units)}")
out.print(f"Control DMAs : {len(control_units)}")
out.print(f"Top-N        : {TOP_N}")
out.print("")
out.print(f"Top {TOP_N} candidates by scan_stat:")
for c in CANDIDATES:
    out.print(f"  Rank {c['rank']}: {c['break_label']}  scan_stat={c['scan_stat']:.3f}"
              f"  pseudo-test: {c['pseudo_test_start']} → {c['pseudo_test_end']}")


# ---------------------------------------------------------------------------
# Helper: TBRRidge pre-aggregates treated units; AugSynth uses per-unit pds
# ---------------------------------------------------------------------------
def _mixed_fit_predict(estimator: str, pds: PanelDataset) -> dict:
    if estimator == "TBRRidge":
        if len(pds.treated_units) > 1:
            treated_agg = (
                pds.wide_data.loc[pds.treated_units]
                .sum(axis=0)
                .to_frame("__treated__")
                .T
            )
            ctrl = pds.wide_data.drop(index=pds.treated_units)
            agg_wide = pd.concat([treated_agg, ctrl])
            agg_pds = PanelDataset(
                wide_data=agg_wide,
                treated_periods=[pds.treated_periods[0]],
                treated_units=["__treated__"],
            )
        else:
            agg_pds = pds
        model = _TBRRidgeCls(inference="Kfold")
        model.run_analysis(agg_pds)
        return {
            "times": model.panel_data.times,
            "y": model.results["y"],
            "y_hat": model.results["y_hat"],
        }
    return _default_fit_predict(estimator, pds)


def _safe_get(obj, attr, default=None):
    return getattr(obj, attr, default) if obj is not None else default


def _print_break_test(r, test_num: int):
    verdict = "PASS" if not r.reject_null else "FAIL"
    out.print(f"\n  Test {test_num} ({r.test_name})")
    out.print(f"    F-statistic : {r.statistic:.4f}")
    out.print(f"    p-value     : {r.p_value:.4f}")
    out.print(f"    reject_null : {r.reject_null}")
    out.print(f"    verdict     : {verdict}")
    if test_num == 1:
        if r.reject_null:
            out.print("    → TREATED series shows a significant level/slope shift at this date.")
        else:
            out.print("    → No significant shift in the TREATED series at this date.")
    elif test_num == 2:
        if r.reject_null:
            out.print("    → *** TREATED-CONTROL RELATIONSHIP BROKE at this date. ***")
            out.print("      Controls are NOT valid counterfactuals across this break.")
        else:
            out.print("    → Treated-control relationship INTACT. Controls remain valid donors.")


def _print_drift_test(r):
    centered = r.residual_centered_flag
    drift    = r.residual_drift_flag
    if centered and not drift:
        verdict = "PASS"
    elif not centered and not drift:
        verdict = "FAIL (biased)"
    elif centered and drift:
        verdict = "FAIL (drift)"
    else:
        verdict = "FAIL (biased+drift)"

    out.print(f"\n  Test 3 drift ({r.estimator}):")
    out.print(f"    residual_mean   : {r.residual_mean:+.1f}")
    out.print(f"    mean_p          : {r.residual_mean_p_value:.4f}  (centered: {r.residual_centered_flag})")
    out.print(f"    slope_p         : {r.residual_slope_p_value:.4f}  (drift: {r.residual_drift_flag})")
    if r.rmse_ratio is not None:
        out.print(f"    rmse_ratio      : {r.rmse_ratio:.3f}  (test/train)")
    out.print(f"    verdict         : {verdict}")
    return verdict


def _verdict_from_tests(t1_fail, t2_fail, t3_verdict):
    t3_fail = t3_verdict != "PASS"
    if t2_fail:
        return "INVALID_RELATIONSHIP_BREAK"
    if t3_fail:
        return "UNSTABLE_DRIFT_OR_BIAS"
    if t1_fail:
        return "COMMON_SHOCK_RELATIONSHIP_INTACT"
    return "STABLE"


# ---------------------------------------------------------------------------
# Run tests for each candidate
# ---------------------------------------------------------------------------
summary_rows = []

for cand in CANDIDATES:
    break_label = cand["break_label"]
    train_end   = cand["train_end"]
    ps_start    = cand["pseudo_test_start"]
    ps_end      = cand["pseudo_test_end"]

    out.print("\n\n" + "=" * 70)
    out.print(f"RANK {cand['rank']} CANDIDATE: {break_label}  scan_stat={cand['scan_stat']:.3f}")
    out.print(f"  Train      : {wide.columns[0].date()} → {train_end}")
    out.print(f"  Pseudo-test: {ps_start} → {ps_end}")
    out.print("=" * 70)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        summary = run_counterfactual_stability_tests(
            data=wide,
            treated_units=treated_units,
            break_start=break_label,
            train_end=train_end,
            pseudo_test_start=ps_start,
            pseudo_test_end=ps_end,
            control_units=control_units,
            estimators=("TBRRidge", "AugSynthCVXPY"),
            fit_predict_fn=_mixed_fit_predict,
            auto_detect_break=False,
            control_transform="auto",
            run_heterogeneity_check=False,
            alpha=0.05,
        )

    for i, bt in enumerate(summary.break_tests, 1):
        _print_break_test(bt, i)

    drift_by_est = {
        getattr(r, "estimator", f"est_{i}"): r
        for i, r in enumerate(summary.residual_drift_tests)
    }
    t3_verdicts = {}
    for est_name, dr in drift_by_est.items():
        t3_verdicts[est_name] = _print_drift_test(dr)

    bt1 = next((bt for bt in summary.break_tests if bt.test_name == "level_slope_break"), None)
    bt2 = next((bt for bt in summary.break_tests if bt.test_name == "treated_control_relationship_break"), None)

    t1_fail = bool(_safe_get(bt1, "reject_null", False))
    t2_fail = bool(_safe_get(bt2, "reject_null", False))

    first_drift = summary.residual_drift_tests[0] if summary.residual_drift_tests else None
    t3_v = t3_verdicts.get(
        getattr(first_drift, "estimator", ""),
        "PASS" if first_drift is None else "FAIL"
    )
    verdict = _verdict_from_tests(t1_fail, t2_fail, t3_v)

    out.print(f"\n  ── OVERALL VERDICT: {verdict} ──")

    summary_rows.append({
        "rank"          : cand["rank"],
        "break_label"   : break_label,
        "scan_stat"     : cand["scan_stat"],
        "train_end"     : train_end,
        "pseudo_end"    : ps_end,
        "test1_p"       : _safe_get(bt1, "p_value"),
        "test1_fail"    : t1_fail,
        "test2_p"       : _safe_get(bt2, "p_value"),
        "test2_fail"    : t2_fail,
        "verdict"       : verdict,
        **{f"drift_{est.replace('-','_')}_mean"   : _safe_get(dr, "residual_mean")
           for est, dr in drift_by_est.items()},
        **{f"drift_{est.replace('-','_')}_mean_p" : _safe_get(dr, "residual_mean_p_value")
           for est, dr in drift_by_est.items()},
        **{f"drift_{est.replace('-','_')}_verdict": t3_verdicts.get(est, "?")
           for est in drift_by_est},
    })


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
out.print("\n\n" + "=" * 70)
out.print(f"SUMMARY TABLE (top {TOP_N} candidates)")
out.print("=" * 70)
df = pd.DataFrame(summary_rows)
if not df.empty:
    out.print(df.to_string(index=False))

out.save(OUTPUT_TXT)
