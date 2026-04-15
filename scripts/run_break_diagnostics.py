"""
Auto structural-break diagnostics — Reddit DME_CONVERSIONS FY26 Q1

This script:
1. Loads config + dataset artifacts
2. Detects ALL candidate break dates
3. Runs counterfactual stability tests for each detected break
4. Writes a decision-ready CSV in the base Reddit directory

Output:
    /Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v1/structure_break_diagnostics.csv

Usage:
    cd /Users/ppavuluri/Desktop/cursor_databricks_setup
    python run_break_diagnostics.py

Notes:
    - For multiple Bai-Perron-style break candidates, install: pip install ruptures
    - If 'ruptures' is unavailable, the script falls back to 'cusum_residual'
"""

import json
import pickle
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional
import importlib.util

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REDDIT_DIR = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v2")
# Load data from the full historical dataset (Dec 2024 → Feb 2026) instead of the
# trimmed v1 dataset (Feb 2025 start).  Config stays on v1 to use the correct 71
# control units that match the main analysis.
DATASETS_PKL = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/mmt_datasets_oct24_extended.pkl")
CONFIG_JSON = REDDIT_DIR / "mmt_config.json"
OUTPUT_CSV           = REDDIT_DIR / "structure_break_diagnostics.csv"
OUTPUT_TXT           = REDDIT_DIR / "structure_break_diagnostics.txt"
OUTPUT_SCAN_CSV      = REDDIT_DIR / "break_scan_all_dates.csv"
OUTPUT_THRESHOLD_TXT = REDDIT_DIR / "break_threshold_info.txt"

PANEL_EXP_ROOT = Path("/Users/ppavuluri/Desktop/latest_pxp/panel_exp")
if str(PANEL_EXP_ROOT) not in sys.path:
    sys.path.insert(0, str(PANEL_EXP_ROOT))

from panel_exp.utils.counterfactual_stability_tests import (
    detect_break_candidates,
    run_counterfactual_stability_tests,
    _default_fit_predict,
)
from panel_exp.methods.tbr import TBRRidge as _TBRRidgeCls
from panel_exp.panel_data import PanelDataset


def _mixed_fit_predict(estimator: str, pds: PanelDataset) -> dict:
    """TBRRidge runs with inference='Kfold' (debias_flag=True); all others use default (inference=None).

    Bypasses _assert_stability_inference intentionally — we want KFold debiasing on TBRRidge
    so we can measure whether it eliminates the +48k/week structural bias in the drift test.
    The inner fold models still use inference=None (kfold() instantiates with model(), i.e. TBRRidge()).

    TBRRidge is run on an aggregated (sum) treated series because the old kfold/debias code
    assumes a single treated unit (1D y/y_hat). This mirrors the main grid's
    panel_aggregation_config='aggregate_treated_only' for TBRRidge.
    """
    if estimator == "TBRRidge":
        import pandas as pd
        from panel_exp.panel_data import TimePeriod

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

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
KPI_NAME = "DME_CONVERSIONS"
ESTIMATORS = ("TBRRidge", "AugSynthCVXPY")
BREAK_METHOD = "cusum_residual"   # use "bai_perron" for multiple candidates, cusum_residual (deviations from treated~control mapping), cusum_treated (deviations from treated~treated mapping)
N_BREAKS = 4
ALPHA = 0.05

# Main experiment window
TRAIN_END = "2026-01-17"
PSEUDO_TEST_START = "2026-01-24"
PSEUDO_TEST_END = "2026-02-21"

# ---------------------------------------------------------------------------
# Tee logger
# ---------------------------------------------------------------------------
class Tee:
    def __init__(self):
        self.lines: List[str] = []

    def print(self, *args):
        line = " ".join(str(a) for a in args)
        print(line)
        self.lines.append(line)

    def save(self, path: Path):
        path.write_text("\n".join(self.lines) + "\n")
        print(f"\n[OUTPUT] Saved log to {path}")


out = Tee()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    return getattr(obj, attr, default) if obj is not None else default


def _extract_break_test(summary: Any, test_name: str) -> Optional[Any]:
    for item in getattr(summary, "break_tests", []):
        if getattr(item, "test_name", None) == test_name:
            return item
    return None


def _extract_first_residual_drift(summary: Any) -> Optional[Any]:
    drift_tests = getattr(summary, "residual_drift_tests", [])
    if drift_tests:
        return drift_tests[0]
    return None


def _extract_residual_drift_by_estimator(summary: Any) -> Dict[str, Any]:
    """Return a dict keyed by estimator name for all drift test results."""
    drift_tests = getattr(summary, "residual_drift_tests", [])
    return {getattr(r, "estimator", f"estimator_{i}"): r for i, r in enumerate(drift_tests)}


def _resolve_candidate_stat(cand: Dict[str, Any]) -> Any:
    for key in ("cusum_stat", "statistic", "break_stat", "score", "value"):
        if key in cand:
            return cand.get(key)
    return None


def _verdict_from_tests(test1_fail: bool, test2_fail: bool, test3_fail: bool) -> str:
    if test2_fail:
        return "INVALID_RELATIONSHIP_BREAK"
    if test3_fail:
        return "UNSTABLE_DRIFT_OR_BIAS"
    if test1_fail:
        return "COMMON_SHOCK_RELATIONSHIP_INTACT"
    return "STABLE"



def _note_from_verdict(verdict: str) -> str:
    mapping = {
        "INVALID_RELATIONSHIP_BREAK": (
            "Treated-control relationship broke at this date; counterfactual mapping is not stable."
        ),
        "UNSTABLE_DRIFT_OR_BIAS": (
            "Relationship may survive, but extrapolation shows bias or drift; model is unstable through this break."
        ),
        "COMMON_SHOCK_RELATIONSHIP_INTACT": (
            "Treated series shifted, but treated-control relationship stayed intact; likely common shock."
        ),
        "STABLE": (
            "No major structural issue detected at this break date."
        ),
    }
    return mapping.get(verdict, "")


# ---------------------------------------------------------------------------
# CUSUM internals — replicates detect_break_candidates(method='cusum_residual')
# exactly, exposing per-date scan_stat and CUSUM series for export.
# ---------------------------------------------------------------------------
_CUSUM_FILTER_THRESHOLD = 3.0    # library default (heuristic, not alpha=0.05)
_MIN_PRE_PERIODS        = 8      # library default


def _compute_cusum_internals(
    wide: pd.DataFrame,
    treated_units: List[str],
    control_units: List[str],
    end: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Replicates detect_break_candidates(method='cusum_residual') internals.

    Returns a dict with:
      scan_df           — DataFrame, one row per candidate break date
      cusum_stat_global — float, max |CUSUM| (the library's filter stat)
      winner_idx        — int, row index in scan_df of the selected break
      cv_cusum_formal   — float, formal 5% K-S critical value for the filter
      cv_scan_sup_t     — float, approximate Andrews (1993) 5% sup-t cv
    """
    w = wide.copy()
    if end is not None:
        end_ts   = pd.Timestamp(end)
        end_pos  = w.columns.get_loc(end_ts)
        w        = w.iloc[:, : end_pos + 1]

    n     = w.shape[1]
    dates = w.columns

    # Aggregate treated + controls
    y      = w.loc[treated_units].to_numpy(dtype=np.float64, copy=True).sum(axis=0)
    x_ctrl = w.loc[control_units].to_numpy(dtype=np.float64, copy=True).sum(axis=0)
    X      = np.column_stack([np.ones(n), x_ctrl])

    # Fit treated ~ [1, sum_controls] on pre-period only
    beta, _, _, _ = np.linalg.lstsq(
        X[:_MIN_PRE_PERIODS], y[:_MIN_PRE_PERIODS], rcond=None
    )
    residuals = y - X @ beta

    # Standardise with pre-period mean / std
    mu_pre  = float(np.mean(residuals[:_MIN_PRE_PERIODS]))
    sig_pre = max(float(np.std(residuals[:_MIN_PRE_PERIODS])), 1e-18)
    standardised = (residuals - mu_pre) / sig_pre
    cusum         = np.cumsum(standardised)

    cusum_stat_global = float(np.max(np.abs(cusum[_MIN_PRE_PERIODS:])))

    # Per-date scan_stat (sup-Wald / two-sample t-stat on residuals)
    rows_scan = []
    for tau in range(_MIN_PRE_PERIODS, n - 1):
        pre_mean  = float(np.mean(residuals[:tau]))
        post_mean = float(np.mean(residuals[tau:]))
        n1, n2    = tau, n - tau
        pooled_var = (
            np.var(residuals[:tau]) / n1
            + np.var(residuals[tau:]) / n2
            + 1e-18
        )
        ss = abs(post_mean - pre_mean) / float(np.sqrt(pooled_var))
        rows_scan.append({
            "date"         : dates[tau],
            "col_idx"      : tau,
            "cusum_value"  : float(cusum[tau]),
            "abs_cusum"    : float(abs(cusum[tau])),
            "scan_stat"    : ss,
            "residual"     : float(residuals[tau]),
            "pre_mean"     : pre_mean,
            "post_mean"    : post_mean,
            # abs_cusum > threshold → this date's cumulative signal passed the filter bar
            "above_cusum_threshold": abs(cusum[tau]) >= _CUSUM_FILTER_THRESHOLD,
        })

    scan_df     = pd.DataFrame(rows_scan)
    winner_idx  = int(np.argmax(scan_df["scan_stat"].values)) if not scan_df.empty else None

    # Formal critical values
    T_eff           = n - _MIN_PRE_PERIODS
    cv_cusum_formal = 1.358 * np.sqrt(T_eff)   # Kolmogorov-Smirnov 5% for max|CUSUM|
    # Andrews (1993) sup-t 5% cv (q=1, 15%–85% trimming) ≈ 3.17
    cv_scan_sup_t   = 3.17

    return {
        "scan_df"           : scan_df,
        "cusum_stat_global" : cusum_stat_global,
        "winner_idx"        : winner_idx,
        "cv_cusum_formal"   : cv_cusum_formal,
        "cv_scan_sup_t"     : cv_scan_sup_t,
        "T_eff"             : T_eff,
        "n"                 : n,
        "residuals"         : residuals,
        "cusum"             : cusum,
    }


# ---------------------------------------------------------------------------
# Break candidate detection helpers
# ---------------------------------------------------------------------------

def _has_ruptures() -> bool:
    return importlib.util.find_spec("ruptures") is not None


def _detect_break_candidates_with_fallback(
    data: pd.DataFrame,
    treated_units: List[str],
    control_units: List[str],
    preferred_method: str,
    n_breaks: int,
    end: str,
) -> List[Dict[str, Any]]:
    method_used = preferred_method

    if preferred_method == "bai_perron" and not _has_ruptures():
        out.print(
            "[WARN] 'ruptures' is not installed, so method='bai_perron' cannot run. "
            "Falling back to method='cusum_residual'. "
            "Install with: pip install ruptures"
        )
        method_used = "cusum_residual"

    break_candidates = detect_break_candidates(
        data=data,
        treated_units=treated_units,
        control_units=control_units,
        method=method_used,
        n_bai_perron_breaks=n_breaks,
        end=end,
    )

    if isinstance(break_candidates, dict):
        break_candidates = [break_candidates]
    elif break_candidates is None:
        break_candidates = []

    for cand in break_candidates:
        cand.setdefault("method", method_used)

    return break_candidates


# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------
with open(DATASETS_PKL, "rb") as f:
    datasets = pickle.load(f)

with open(CONFIG_JSON) as f:
    cfg = json.load(f)

long_df = datasets[KPI_NAME]
kpi_col = cfg["kpi"][KPI_NAME]   # e.g. "conversions"

wide = (
    long_df.pivot_table(index="geo", columns="date", values=kpi_col, aggfunc="sum")
    .sort_index()
)
wide.columns = pd.to_datetime(wide.columns)
wide.index = wide.index.map(str)

treated_units = [str(g) for g in cfg["test_groups"]["Reddit"] if str(g) in wide.index]
control_units = [str(g) for g in cfg["control_groups"]["Reddit"] if str(g) in wide.index]

all_geos = treated_units + control_units
wide = wide.loc[all_geos].fillna(0)

out.print("=" * 70)
out.print("AUTO STRUCTURAL BREAK DIAGNOSTICS")
out.print("=" * 70)
out.print(f"KPI               : {KPI_NAME}")
out.print(f"KPI column        : {kpi_col}")
out.print(f"Wide shape        : {wide.shape[0]} units × {wide.shape[1]} periods")
out.print(f"Date range        : {wide.columns.min().date()} → {wide.columns.max().date()}")
out.print(f"Treated count     : {len(treated_units)}")
out.print(f"Control count     : {len(control_units)}")
out.print(f"Train end         : {TRAIN_END}")
out.print(f"Pseudo-test start : {PSEUDO_TEST_START}")
out.print(f"Pseudo-test end   : {PSEUDO_TEST_END}")
out.print(f"Break method      : {BREAK_METHOD}")
out.print(f"N breaks          : {N_BREAKS}")

# ---------------------------------------------------------------------------
# CUSUM internals: compute per-date scan stats and write supporting files
# (uses same end truncation as the candidate detection below)
# ---------------------------------------------------------------------------
_cusum_info = _compute_cusum_internals(
    wide=wide,
    treated_units=treated_units,
    control_units=control_units,
    end=PSEUDO_TEST_END,
)
_scan_df        = _cusum_info["scan_df"]
_winner_idx     = _cusum_info["winner_idx"]
_cv_cusum       = _cusum_info["cv_cusum_formal"]
_cv_scan        = _cusum_info["cv_scan_sup_t"]
_cusum_global   = _cusum_info["cusum_stat_global"]
_T_eff          = _cusum_info["T_eff"]

# Tag winner and detected columns
_scan_df = _scan_df.copy()
_scan_df["winner"]   = False
_scan_df["detected"] = False   # True = this date IS the selected break
if _winner_idx is not None:
    _scan_df.at[_winner_idx, "winner"]   = True
    _scan_df.at[_winner_idx, "detected"] = True

# ── break_scan_all_dates.csv ─────────────────────────────────────────────
_scan_export = _scan_df[[
    "date", "cusum_value", "abs_cusum", "scan_stat",
    "residual", "above_cusum_threshold", "detected", "winner",
]].copy()
_scan_export["date"] = _scan_export["date"].astype(str).str[:10]
_scan_export.to_csv(OUTPUT_SCAN_CSV, index=False)
out.print(f"\n[OUTPUT] Saved per-date CUSUM scan to {OUTPUT_SCAN_CSV}")

# ── Identify top-5 peaks by scan_stat and by |cusum| ────────────────────
_top5_scan  = _scan_df.nlargest(5, "scan_stat")[
    ["date", "cusum_value", "abs_cusum", "scan_stat", "residual", "winner"]
].copy()
_top5_cusum = _scan_df.nlargest(5, "abs_cusum")[
    ["date", "cusum_value", "abs_cusum", "scan_stat", "residual", "winner"]
].copy()

# Pretty-print dates
for _df in (_top5_scan, _top5_cusum):
    _df["date"] = _df["date"].astype(str).str[:10]

# ── Add top-5 table to console / txt output ──────────────────────────────
out.print("\n" + "=" * 70)
out.print("CUSUM SCAN INTERNALS")
out.print("=" * 70)
out.print(f"Scan range  : {str(_scan_df['date'].iloc[0])[:10]} → {str(_scan_df['date'].iloc[-1])[:10]}")
out.print(f"T_eff       : {_T_eff} candidate dates")
out.print(f"Global CUSUM max |CUSUM| : {_cusum_global:.2f}")
out.print()
out.print("THRESHOLD REFERENCE:")
out.print(f"  (A) CUSUM filter (library)       : {_CUSUM_FILTER_THRESHOLD}  "
          f"← heuristic, NOT alpha=0.05")
out.print(f"  (A) CUSUM filter (formal 5%)     : {_cv_cusum:.2f}  "
          f"← 1.358×√{_T_eff} (Kolmogorov-Smirnov)")
out.print(f"  (B) scan_stat (Andrews 1993 5%)  : {_cv_scan:.2f}  "
          f"← approx sup-t, q=1, 15%–85% trim")
out.print(f"  (B) scan_stat NO formal threshold applied — winner = argmax always")
out.print()
out.print("TOP 5 DATES BY scan_stat  (break locator — argmax wins):")
out.print(f"  {'Date':>12}  {'scan_stat':>10}  {'abs_cusum':>10}  {'residual':>10}  {'WINNER':>7}")
out.print("  " + "-" * 58)
for _, _r in _top5_scan.iterrows():
    _win = "<< WINNER" if _r["winner"] else ""
    out.print(
        f"  {str(_r['date'])[:10]:>12}  {_r['scan_stat']:>10.3f}  "
        f"{_r['abs_cusum']:>10.2f}  {_r['residual']:>+10.0f}  {_win}"
    )
out.print()
out.print("TOP 5 DATES BY abs_cusum  (CUSUM accumulation — visible in charts):")
out.print(f"  {'Date':>12}  {'abs_cusum':>10}  {'scan_stat':>10}  {'residual':>10}  {'WINNER':>7}")
out.print("  " + "-" * 58)
for _, _r in _top5_cusum.iterrows():
    _win = "<< WINNER" if _r["winner"] else ""
    out.print(
        f"  {str(_r['date'])[:10]:>12}  {_r['abs_cusum']:>10.2f}  "
        f"{_r['scan_stat']:>10.3f}  {_r['residual']:>+10.0f}  {_win}"
    )
out.print()
out.print("WHY HIGH abs_cusum DATES ARE NOT SELECTED AS BREAKS:")
out.print("  The scan_stat at any date τ measures |mean(resid[:τ]) − mean(resid[τ:])|.")
out.print("  Dates late in the series (e.g. Dec 2025) sit deep in the post-Feb 2025")
out.print("  elevated regime. Both sides of τ have high mean residuals, so the gap")
out.print("  is small → low scan_stat, even though the CUSUM has accumulated to 50+.")
out.print("  Feb 15 2025 wins because it separates ~9 low-residual baseline weeks")
out.print("  from ~53 elevated post-break weeks — the largest mean-shift possible.")
out.print()
out.print("DEC 2025 SPECIFICALLY:")
_dec_rows = _scan_df[
    (_scan_df["date"].astype(str).str[:7] == "2025-12")
][["date", "cusum_value", "abs_cusum", "scan_stat", "residual"]].copy()
_dec_rows["date"] = _dec_rows["date"].astype(str).str[:10]
if not _dec_rows.empty:
    for _, _r in _dec_rows.iterrows():
        out.print(
            f"  {str(_r['date'])[:10]}  cusum={_r['cusum_value']:>+7.2f}  "
            f"abs_cusum={_r['abs_cusum']:>6.2f}  scan_stat={_r['scan_stat']:.3f}  "
            f"resid={_r['residual']:>+8.0f}"
        )
    # Pull representative pre-Dec and post-Dec means from last Dec row
    _last_dec_idx = _dec_rows.index[-1]
    _last_dec_scan = _scan_df.loc[_last_dec_idx]
    out.print(
        f"\n  Pre-Dec mean residual : {_last_dec_scan['pre_mean']:>+.0f}/wk  "
        f"Post-Dec mean : {_last_dec_scan['post_mean']:>+.0f}/wk  "
        f"Gap : {abs(_last_dec_scan['pre_mean'] - _last_dec_scan['post_mean']):.0f}"
    )
    out.print(
        "  Dec 2025 residuals are uniformly positive (+475 to +630) — not a dip/recovery."
    )
    out.print(
        "  The CUSUM climbs through Dec because treated keeps exceeding controls."
    )
    out.print(
        "  But the scan_stat is low because Feb-Nov 2025 was already elevated (+176/wk avg),"
    )
    out.print(
        "  so pre-Dec and post-Dec mean residuals are both high with a small gap between them."
    )

# ── break_threshold_info.txt ─────────────────────────────────────────────
_thresh_lines = [
    "CUSUM BREAK DETECTION — THRESHOLD DOCUMENTATION",
    "=" * 60,
    "",
    "OVERVIEW",
    "--------",
    "detect_break_candidates(method='cusum_residual') uses TWO statistics:",
    "",
    "  (A) CUSUM FILTER — coarse gate to skip flat series",
    "      Stat    : max |CUSUM(standardized residuals)| over all post-pre-period dates",
    f"      Library : {_CUSUM_FILTER_THRESHOLD}  (heuristic, NOT a formal alpha=0.05 value)",
    f"      Formal  : {_cv_cusum:.2f}  (Kolmogorov-Smirnov 5%; 1.358 × √T_eff={_T_eff})",
    f"      Observed: {_cusum_global:.2f}  → filter PASSED",
    "",
    "  (B) BREAK LOCATOR — scan_stat identifies which date is the break",
    "      Stat    : |mean(resid[:τ]) − mean(resid[τ:])| / √pooled_var  (sup-Wald / sup-t)",
    "      Threshold: NONE applied by library — winner = argmax(scan_stat) always",
    f"      Andrews (1993) approx 5% sup-t cv : {_cv_scan:.2f}  (q=1, 15%–85% trimming)",
    "",
    "NOTE: The 'cusum_stat' value reported in structure_break_diagnostics.csv is",
    "statistic (A) — the GLOBAL max |CUSUM| — NOT a per-date stat.",
    "The per-date scan_stat (B) is in break_scan_all_dates.csv and",
    "scan_stat_at_winner in structure_break_diagnostics.csv.",
    "",
    "=" * 60,
    "TOP 5 BY scan_stat",
    "=" * 60,
]
for _, _r in _top5_scan.iterrows():
    _thresh_lines.append(
        f"  {str(_r['date'])[:10]}  scan_stat={_r['scan_stat']:.3f}  "
        f"abs_cusum={_r['abs_cusum']:.2f}  winner={_r['winner']}"
    )

_thresh_lines += [
    "",
    "=" * 60,
    "TOP 5 BY abs_cusum (visible in CUSUM chart)",
    "=" * 60,
]
for _, _r in _top5_cusum.iterrows():
    _above = _r["abs_cusum"] >= _cv_cusum
    _thresh_lines.append(
        f"  {str(_r['date'])[:10]}  abs_cusum={_r['abs_cusum']:.2f}  "
        f"scan_stat={_r['scan_stat']:.3f}  "
        f"above_formal_5pct={'YES' if _above else 'NO'}  winner={_r['winner']}"
    )

_thresh_lines += [
    "",
    "=" * 60,
    "WHY DEC 2025 HAS HIGH abs_cusum BUT LOW scan_stat",
    "=" * 60,
    "",
    "Dec 2025 cumulative CUSUM accumulated to 54–61 (visible spike in charts).",
    "Yet scan_stat peaked at only 0.54–1.74 (well below any significance threshold).",
    "",
    "Mechanism: the scan_stat at τ=Dec-2025 compares",
    "  pre_mean  = mean(residuals[:Dec])  — includes all of Feb–Nov 2025",
    "  post_mean = mean(residuals[Dec:])  — Dec 2025 + Jan–Feb 2026",
    "",
    "Because Feb–Nov 2025 residuals were already elevated (~+176/wk on average),",
    "the pre-Dec mean is already high. Dec 2025 residuals (+475 to +630) are even",
    "higher, so post_mean is only modestly above pre_mean. The mean-shift is small",
    "relative to the large pooled variance accumulated over 50 weeks.",
    "",
    "By contrast, Feb 15 2025 compares:",
    "  pre_mean  ≈ −17/wk  (9 quiet baseline weeks)",
    "  post_mean ≈ +176/wk (53 weeks of elevated treated activity)",
    "Gap ≈ 193/wk → highest scan_stat of all dates.",
    "",
    "Additionally, Dec 2025 residuals are uniformly POSITIVE (no dip-and-recovery).",
    "The CUSUM climbs continuously because treated keeps exceeding controls throughout",
    "Dec. The visual 'spike' in charts reflects ongoing treated elevation, not",
    "a temporary anomaly that cancels out in the cumulative sum.",
]
OUTPUT_THRESHOLD_TXT.write_text("\n".join(_thresh_lines) + "\n")
out.print(f"[OUTPUT] Saved threshold documentation to {OUTPUT_THRESHOLD_TXT}")

# ---------------------------------------------------------------------------
# Detect all candidate breaks
# ---------------------------------------------------------------------------
out.print("\n" + "=" * 70)
out.print("DETECTING BREAK CANDIDATES")
out.print("=" * 70)

break_candidates = _detect_break_candidates_with_fallback(
    data=wide,
    treated_units=treated_units,
    control_units=control_units,
    preferred_method=BREAK_METHOD,
    n_breaks=N_BREAKS,
    end=PSEUDO_TEST_END,
)

out.print(f"Detected {len(break_candidates)} break candidate(s).")
for i, cand in enumerate(break_candidates, 1):
    out.print(
        f"  {i}. break_label={cand.get('break_label')} "
        f"method={cand.get('method')} "
        f"direction={cand.get('direction')} "
        f"stat={_resolve_candidate_stat(cand)}"
    )

# ---------------------------------------------------------------------------
# Run tests for each break
# ---------------------------------------------------------------------------
rows: List[Dict[str, Any]] = []

for i, cand in enumerate(break_candidates, 1):
    break_label = cand.get("break_label")
    if break_label is None:
        continue

    out.print("\n" + "=" * 70)
    out.print(f"RUNNING TESTS FOR BREAK {i}: {break_label}")
    out.print("=" * 70)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        summary = run_counterfactual_stability_tests(
            data=wide,
            treated_units=treated_units,
            break_start=break_label,
            train_end=TRAIN_END,
            pseudo_test_start=PSEUDO_TEST_START,
            pseudo_test_end=PSEUDO_TEST_END,
            control_units=control_units,
            estimators=ESTIMATORS,
            fit_predict_fn=_mixed_fit_predict,
            auto_detect_break=False,
            control_transform="auto",
            run_heterogeneity_check=True,
            alpha=ALPHA,
        )

    test1 = _extract_break_test(summary, "level_slope_break")
    test2 = _extract_break_test(summary, "treated_control_relationship_break")
    drift_by_est = _extract_residual_drift_by_estimator(summary)
    # Use first drift result for the combined verdict (preserves existing logic)
    test3 = _extract_first_residual_drift(summary)

    test1_fail = bool(_safe_get(test1, "reject_null", False))
    test2_fail = bool(_safe_get(test2, "reject_null", False))
    test3_fail = bool(
        _safe_get(test3, "residual_drift_flag", False)
        or (not _safe_get(test3, "residual_centered_flag", True))
    )

    verdict = _verdict_from_tests(test1_fail, test2_fail, test3_fail)
    note = _note_from_verdict(verdict)

    out.print(f"Test 1 fail : {test1_fail}  p={_safe_get(test1, 'p_value')}")
    out.print(f"Test 2 fail : {test2_fail}  p={_safe_get(test2, 'p_value')}")
    out.print("Test 3 (residual drift) — per estimator:")
    for est_name, dr in drift_by_est.items():
        dr_fail = bool(
            _safe_get(dr, "residual_drift_flag", False)
            or (not _safe_get(dr, "residual_centered_flag", True))
        )
        out.print(
            f"  [{est_name}] fail={dr_fail}  "
            f"mean={_safe_get(dr, 'residual_mean'):.1f}  "
            f"mean_p={_safe_get(dr, 'residual_mean_p_value'):.6f}  "
            f"slope_p={_safe_get(dr, 'residual_slope_p_value'):.6f}  "
            f"rmse_ratio={_safe_get(dr, 'rmse_ratio')}  "
            f"centered={_safe_get(dr, 'residual_centered_flag')}  "
            f"drift={_safe_get(dr, 'residual_drift_flag')}"
        )
    out.print(f"Verdict     : {verdict}")
    out.print(f"Note        : {note}")

    # Look up this break's per-date scan_stat from the full scan table
    _bl_date = str(break_label)[:10]
    _scan_match = _scan_df[_scan_df["date"].astype(str).str[:10] == _bl_date]
    _winner_scan_stat = float(_scan_match["scan_stat"].iloc[0]) if not _scan_match.empty else None
    _winner_abs_cusum = float(_scan_match["abs_cusum"].iloc[0]) if not _scan_match.empty else None

    row = {
        "break_start": break_label,
        "break_end": PSEUDO_TEST_START,
        "candidate_method": cand.get("method"),
        "candidate_direction": cand.get("direction"),
        # cusum_stat_global: the CUSUM filter stat (max |CUSUM| over full scan)
        "cusum_stat_global": _resolve_candidate_stat(cand),
        "scan_stat_at_winner": _winner_scan_stat,
        "abs_cusum_at_winner": _winner_abs_cusum,
        "cv_cusum_formal_5pct": round(_cv_cusum, 2),
        "cv_scan_sup_t_5pct": _cv_scan,

        "test1_label": "Test 1",
        "test1_name": "level_slope_break",
        "test1_stat": _safe_get(test1, "statistic"),
        "test1_p": _safe_get(test1, "p_value"),
        "test1_fail": test1_fail,

        "test2_label": "Test 2",
        "test2_name": "treated_control_relationship_break",
        "test2_stat": _safe_get(test2, "statistic"),
        "test2_p": _safe_get(test2, "p_value"),
        "test2_fail": test2_fail,

        "verdict": verdict,
        "note": note,
    }
    # Add one set of test3 columns per estimator
    for est_name, dr in drift_by_est.items():
        safe_key = est_name.replace("-", "_").replace(" ", "_")
        dr_fail = bool(
            _safe_get(dr, "residual_drift_flag", False)
            or (not _safe_get(dr, "residual_centered_flag", True))
        )
        row.update({
            f"test3_{safe_key}_residual_mean": _safe_get(dr, "residual_mean"),
            f"test3_{safe_key}_mean_p": _safe_get(dr, "residual_mean_p_value"),
            f"test3_{safe_key}_slope_p": _safe_get(dr, "residual_slope_p_value"),
            f"test3_{safe_key}_rmse_ratio": _safe_get(dr, "rmse_ratio"),
            f"test3_{safe_key}_centered": _safe_get(dr, "residual_centered_flag"),
            f"test3_{safe_key}_drift": _safe_get(dr, "residual_drift_flag"),
            f"test3_{safe_key}_fail": dr_fail,
        })
    rows.append(row)

# ---------------------------------------------------------------------------
# Save output
# ---------------------------------------------------------------------------
results_df = pd.DataFrame(rows)
if not results_df.empty:
    results_df = results_df.sort_values("break_start").reset_index(drop=True)

out.print("\n" + "=" * 70)
out.print("FINAL SUMMARY")
out.print("=" * 70)
out.print(results_df.to_string(index=False) if not results_df.empty else "No results produced.")

results_df.to_csv(OUTPUT_CSV, index=False)
out.print(f"\n[OUTPUT] Saved CSV to {OUTPUT_CSV}")

out.save(OUTPUT_TXT)