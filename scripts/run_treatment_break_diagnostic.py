"""
Treatment-period structural break diagnostic — Reddit DME_CONVERSIONS FY26 Q1

Tests whether the TREATMENT itself (Jan 24 → Feb 21, 2026) shows up as a
structural break. At Jan 24:
  - Test DMAs go dark (Reddit spend removed)
  - Control DMAs get heavy-up (Reddit spend increased)

This is a treatment-validity check: if Test 2 FAILS at Jan 24, the
treated-control relationship broke at treatment start — meaning controls
are not valid counterfactuals during the experiment window.

Two break candidates always tested:
  A. CUSUM auto-detected break (scanned over FULL dataset, Dec 2024 → Feb 2026)
  B. Jan 24, 2026 (treatment start) — forced regardless of CUSUM score

Three tests per candidate:
  Test 1: level/slope break in TREATED series (Chow F-test on treated aggregate)
  Test 2: treated-CONTROL relationship break (Chow F-test on treated~controls mapping)
  Test 3: residual drift — does model trained on pre-break extrapolate cleanly?

Usage:
    cd /Users/ppavuluri/Desktop/FY26/Q1/Reddit
    python run_treatment_break_diagnostic.py
"""
import json
import pickle
import sys
import warnings
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REDDIT_DIR_DATA   = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid")
REDDIT_DIR_CONFIG = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v1")
DATASETS_PKL = REDDIT_DIR_DATA   / "mmt_datasets.pkl"
CONFIG_JSON  = REDDIT_DIR_CONFIG / "mmt_config.json"
OUTPUT_TXT   = REDDIT_DIR_CONFIG / "treatment_break_diagnostic_output.txt"

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

all_geos = list(treated_units) + list(control_units)
wide = wide.loc[all_geos].fillna(0)

cols = wide.columns
out.print("=" * 70)
out.print("TREATMENT BREAK DIAGNOSTIC — Reddit DME_CONVERSIONS FY26 Q1")
out.print("=" * 70)
out.print(f"Data loaded  : {wide.shape[0]} units × {wide.shape[1]} periods")
out.print(f"Date range   : {cols[0].date()} → {cols[-1].date()}")
out.print(f"Treated DMAs : {len(treated_units)}")
out.print(f"Control DMAs : {len(control_units)}")
out.print(f"Treatment    : Jan 24, 2026 → Feb 21, 2026 (go-dark treated, heavy-up controls)")


# ---------------------------------------------------------------------------
# Helper: per-estimator drift reporting
# ---------------------------------------------------------------------------
def _mixed_fit_predict(estimator: str, pds: PanelDataset) -> dict:
    """TBRRidge uses KFold (aggregated treated); AugSynth uses default (inference=None)."""
    if estimator == "TBRRidge":
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
            out.print("      Consistent with treatment effect (go-dark) or confounding event.")
        else:
            out.print("    → No significant shift in the TREATED series at this date.")
    elif test_num == 2:
        if r.reject_null:
            out.print("    → *** TREATED-CONTROL RELATIONSHIP BROKE at this date. ***")
            out.print("      Controls are NOT valid counterfactuals across this break.")
            out.print("      If this is the treatment start, the experiment design is contaminated.")
        else:
            out.print("    → Treated-control relationship INTACT at this date.")
            out.print("      Controls remain valid donors across this break.")


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
# STEP 1: CUSUM scan over FULL dataset (Dec 2024 → Feb 28, 2026)
# ---------------------------------------------------------------------------
out.print("\n\n" + "=" * 70)
out.print("STEP 1: CUSUM SCAN — FULL DATASET (Dec 2024 → Feb 28, 2026)")
out.print("=" * 70)
out.print("(cusum_residual returns the single strongest break only)")

# Scan over full dataset — no end truncation
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cusum_cands_full = detect_break_candidates(
        data=wide,
        treated_units=treated_units,
        control_units=control_units,
        method="cusum_residual",
        n_bai_perron_breaks=1,
        end=None,   # NO truncation — scan full dataset
    )

if not cusum_cands_full:
    out.print("  No break detected above CUSUM threshold (3.0) in full dataset.")
else:
    for c in cusum_cands_full:
        out.print(
            f"  Auto-detected break: {c.get('break_label')}  "
            f"CUSUM={c.get('cusum_stat', 'N/A'):.2f}  "
            f"direction={c.get('direction')}"
        )

# Also scan with end=Jan 17 (training only) to compare
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cusum_cands_train = detect_break_candidates(
        data=wide,
        treated_units=treated_units,
        control_units=control_units,
        method="cusum_residual",
        n_bai_perron_breaks=1,
        end="2026-01-17",
    )

out.print("\n  Same scan truncated to training window (end=Jan 17, 2026):")
if not cusum_cands_train:
    out.print("  No break detected above CUSUM threshold in training window.")
else:
    for c in cusum_cands_train:
        out.print(
            f"  Training-only break: {c.get('break_label')}  "
            f"CUSUM={c.get('cusum_stat', 'N/A'):.2f}  "
            f"direction={c.get('direction')}"
        )


# ---------------------------------------------------------------------------
# STEP 2: Build candidate list (CUSUM auto + Jan 24 forced)
# ---------------------------------------------------------------------------
# Always test Jan 24 explicitly since cusum_residual can only return 1 break
# and Feb 15 likely dominates the scan statistic.
jan24_candidate = {
    "break_label": "2026-01-24",
    "method": "forced_explicit",
    "direction": "down",  # go-dark → treated should drop
    "cusum_stat": float("nan"),
}

# Build test list: CUSUM auto-detected + Jan 24 (deduplicated)
candidates_to_test = []
auto_labels = set()
for c in cusum_cands_full:
    lb = c.get("break_label")
    if lb:
        auto_labels.add(str(lb)[:10])
        candidates_to_test.append((c, "cusum_auto"))

if "2026-01-24" not in auto_labels:
    candidates_to_test.append((jan24_candidate, "forced"))
    out.print("\n  Jan 24, 2026 NOT auto-detected by CUSUM — added as forced candidate.")
else:
    out.print("\n  Jan 24, 2026 WAS auto-detected by CUSUM.")

out.print(f"\n  Total candidates to test: {len(candidates_to_test)}")


# ---------------------------------------------------------------------------
# STEP 3: Run full test battery for each candidate
# ---------------------------------------------------------------------------
TRAIN_END      = "2026-01-17"
PSEUDO_START   = "2026-01-24"
PSEUDO_END     = "2026-02-21"   # last week of experiment

summary_rows = []

for cand, cand_source in candidates_to_test:
    break_label = cand.get("break_label")
    if break_label is None:
        continue

    # For the break test (Test 1, Test 2) we need to know where to split.
    # For Jan 24 break: train ends Jan 17, pseudo_test starts Jan 24.
    # For other breaks (e.g. Feb 15 2025): use the standard window.
    bl_ts = pd.Timestamp(str(break_label)[:10])
    train_end_date = TRAIN_END
    pseudo_start_date = PSEUDO_START
    pseudo_end_date = PSEUDO_END

    # If the break is BEFORE the main training window, keep current window
    # so the drift test still uses the experiment period.
    # If the break IS Jan 24 (treatment start), train up to Jan 17.
    # Either way, keep pseudo_test at the experiment window to measure
    # whether the model extrapolates into the treatment period.

    out.print("\n\n" + "=" * 70)
    out.print(f"CANDIDATE: {break_label}  (source={cand_source})")
    out.print(
        f"  CUSUM stat : {cand.get('cusum_stat', 'N/A') if not (isinstance(cand.get('cusum_stat'), float) and np.isnan(cand.get('cusum_stat'))) else 'N/A (forced)'}"
    )
    out.print(f"  direction  : {cand.get('direction')}")
    out.print(f"  Train end  : {train_end_date}")
    out.print(f"  Pseudo     : {pseudo_start_date} → {pseudo_end_date}")
    out.print("=" * 70)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        summary = run_counterfactual_stability_tests(
            data=wide,
            treated_units=treated_units,
            break_start=break_label,
            train_end=train_end_date,
            pseudo_test_start=pseudo_start_date,
            pseudo_test_end=pseudo_end_date,
            control_units=control_units,
            estimators=("TBRRidge", "AugSynthCVXPY"),
            fit_predict_fn=_mixed_fit_predict,
            auto_detect_break=False,
            control_transform="auto",
            run_heterogeneity_check=False,
            alpha=0.05,
        )

    # Print Test 1 + Test 2
    for i, bt in enumerate(summary.break_tests, 1):
        _print_break_test(bt, i)

    # Print per-estimator drift
    drift_by_est = {
        getattr(r, "estimator", f"est_{i}"): r
        for i, r in enumerate(summary.residual_drift_tests)
    }
    t3_verdicts = {}
    for est_name, dr in drift_by_est.items():
        t3_verdicts[est_name] = _print_drift_test(dr)

    # Extract Test 1 / Test 2 objects
    bt1 = next((bt for bt in summary.break_tests if bt.test_name == "level_slope_break"), None)
    bt2 = next((bt for bt in summary.break_tests if bt.test_name == "treated_control_relationship_break"), None)

    t1_fail = bool(_safe_get(bt1, "reject_null", False))
    t2_fail = bool(_safe_get(bt2, "reject_null", False))

    # Overall verdict uses first drift test
    first_drift = summary.residual_drift_tests[0] if summary.residual_drift_tests else None
    t3_v = t3_verdicts.get(
        getattr(first_drift, "estimator", ""),
        "PASS" if first_drift is None else "FAIL"
    )
    verdict = _verdict_from_tests(t1_fail, t2_fail, t3_v)

    out.print(f"\n  ── OVERALL VERDICT: {verdict} ──")

    if break_label == "2026-01-24":
        out.print("\n  TREATMENT-VALIDITY INTERPRETATION:")
        if t1_fail and t2_fail:
            out.print(
                "  Test 1 FAIL + Test 2 FAIL: The treated series shifted AND the treated-control\n"
                "  relationship broke at treatment start. Controls are not valid counterfactuals\n"
                "  during the experiment. The experiment estimate is unreliable."
            )
        elif t1_fail and not t2_fail:
            out.print(
                "  Test 1 FAIL + Test 2 PASS: Treated series shifted (consistent with a real\n"
                "  treatment effect), but the treated-control relationship remained intact.\n"
                "  Controls are valid donors during the experiment. This is the IDEAL outcome:\n"
                "  treatment moved the treated series while controls remained predictive."
            )
        elif not t1_fail and t2_fail:
            out.print(
                "  Test 1 PASS + Test 2 FAIL: The treated series did NOT show a level/slope\n"
                "  break, but the treated-control RELATIONSHIP broke. The controls changed\n"
                "  structurally relative to treated (heavy-up effect on controls?) without\n"
                "  a corresponding shift in treated. Counterfactual mapping is invalid."
            )
        else:
            out.print(
                "  Test 1 PASS + Test 2 PASS: Neither the treated series nor the relationship\n"
                "  shows a significant break at treatment start. Either the treatment had no\n"
                "  measurable effect at this granularity, or the break is too small to detect\n"
                "  with this test. Check drift results for signal."
            )

    summary_rows.append({
        "break_label"   : break_label,
        "source"        : cand_source,
        "cusum_stat"    : cand.get("cusum_stat"),
        "test1_p"       : _safe_get(bt1, "p_value"),
        "test1_fail"    : t1_fail,
        "test2_p"       : _safe_get(bt2, "p_value"),
        "test2_fail"    : t2_fail,
        "verdict"       : verdict,
        **{
            f"drift_{est.replace('-','_')}_mean" : _safe_get(dr, "residual_mean")
            for est, dr in drift_by_est.items()
        },
        **{
            f"drift_{est.replace('-','_')}_mean_p": _safe_get(dr, "residual_mean_p_value")
            for est, dr in drift_by_est.items()
        },
        **{
            f"drift_{est.replace('-','_')}_verdict": t3_verdicts.get(est, "?")
            for est in drift_by_est
        },
    })


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
out.print("\n\n" + "=" * 70)
out.print("SUMMARY TABLE")
out.print("=" * 70)
df = pd.DataFrame(summary_rows)
if not df.empty:
    out.print(df.to_string(index=False))

out.print("\n\nKEY QUESTION — Is Jan 24, 2026 (treatment start) a structural break?")
jan24_row = [r for r in summary_rows if str(r["break_label"])[:10] == "2026-01-24"]
if jan24_row:
    r = jan24_row[0]
    out.print(f"  Test 1 (treated level/slope break)  : {'FAIL' if r['test1_fail'] else 'PASS'}  (p={r['test1_p']:.4f})")
    out.print(f"  Test 2 (treated-control rel. break) : {'FAIL' if r['test2_fail'] else 'PASS'}  (p={r['test2_p']:.4f})")
    out.print(f"  Overall verdict                     : {r['verdict']}")
    if not r["test2_fail"]:
        out.print(
            "\n  → Controls remain valid counterfactuals during the experiment.\n"
            "    The AugSynth estimate of ~-600/wk is structurally valid."
        )
    else:
        out.print(
            "\n  → *** WARNING: Controls are NOT valid counterfactuals at treatment start.\n"
            "    The experiment design may be contaminated by the heavy-up on controls."
        )

out.save(OUTPUT_TXT)
