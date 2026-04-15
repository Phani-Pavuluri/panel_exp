"""
Run MMT analysis for a grid of (estimator, inference) combinations and save results.
Intended to be run from the notebook after the MMT config cell: %run run_mmt_estimator_inference_grid.py

Requires in scope: mmt (MMTAnalysis instance), MMTAnalysis.
Uses mmt.config (and mmt.alpha, mmt.mlflow_run_name) to build each run; only model_selection and inference vary.
On failure for a combination, logs and continues to the next.

BRB (BlockResidualBootstrap): model-conditional moving-block residual bootstrap. The estimator is not
re-fit inside each bootstrap draw; cumulative bounds are the primary aggregate uncertainty object.
"""

from __future__ import annotations

import json
import os
import pickle
import time
import traceback
import warnings
from typing import Any, Optional
from pathlib import Path

import numpy as np
import pandas as pd

# Explicit public API only (no wildcard). Optional: grid still loads if submodule missing.
try:
    from panel_exp.utils.counterfactual_stability_tests import (
        run_counterfactual_stability_tests,
        compare_estimator_stability,
        check_AugSynthCVXPY_weight_health,
        build_pseudo_test_paneldataset,
    )
except ImportError:  # pragma: no cover - optional in minimal envs
    run_counterfactual_stability_tests = None  # type: ignore[misc, assignment]
    compare_estimator_stability = None  # type: ignore[misc, assignment]
    check_AugSynthCVXPY_weight_health = None  # type: ignore[misc, assignment]
    build_pseudo_test_paneldataset = None  # type: ignore[misc, assignment]

# Estimators that require control (and treated) units to be pre-aggregated (panel_aggregation_config='yes')
ESTIMATORS_REQUIRING_AGGREGATION = ("TBR","BayesianTBR")
# Estimators that aggregate treated only; control stays unit-level (panel_aggregation_config='no')
ESTIMATORS_AGGREGATE_TREATED_ONLY = ("TBRRidge","AugSynthCVXPY", "SyntheticControlCVXPY")
# Estimators that require no aggregation; keep unit-level panel (panel_aggregation_config='none')
ESTIMATORS_REQUIRING_AGGREGATION_NONE = ("Trop",)
# AugSynthCVXPY and SyntheticControlCVXPY + BRB: use unaggregated treated units; residuals at unit level, aggregate after bootstrap
ESTIMATORS_BRB_UNAGGREGATED_TREATED = ()

# -----------------------------------------------------------------------------
# Config (override base path if needed)
# -----------------------------------------------------------------------------
# New outputs go to _did_upgrade folder; old v1 outputs remain untouched
BASE_OUTPUT_DIR = "/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v2"

# Restrict to these datasets when running grid. None = use all from mmt.config.
# Use this when mmt has more datasets (e.g. CC_WEB_ORDERS) than you want to run.
RUN_ONLY_DATASETS = ["DME_CONVERSIONS"]
# When True, run only TBR/TBRRidge/AugSynthCVXPY/SyntheticControlCVXPY + BlockResidualBootstrap (BRB test sweep)
RUN_BRB_ONLY = False
# BRB: when True, re-fit estimator inside each bootstrap draw (includes estimator uncertainty; slower)
REFIT_IN_BOOTSTRAP = True
# BRB: "post_only" (default) or "pre_bootstrap". post_only=perturb post-period; pre_bootstrap=bootstrap pre-period for coefficient uncertainty
BRB_REFIT_MODE = ["pre_bootstrap","post_only"][1]
# BRB: "percentile" (default) or "bca" for cumulative CI
BRB_CI_METHOD = ["percentile","bca"][1]
# BRB: "block" (default) or "wild" for bootstrap type (wild is experimental)
BRB_BOOTSTRAP_TYPE = ["block","wild"][0]
# BRB: block length for moving-block residual bootstrap
BRB_BLOCK_LENGTH = 4
RUN_ONLY_INDICES = None  # None = run all; [16] = run only index 16
START_FROM_INDEX = 0
END_AT_INDEX = None  # None = run to the end

# Exclude specific date ranges from input datasets before any estimator runs.
# For sensitivity checks, e.g. excluding market-wide shock weeks before treatment.
# Example: [("2026-01-10", "2026-01-17")]
# Example: [("2024-12-14","2025-04-05"),("2024-12-14","2025-02-15")]
EXCLUDE_DATE_RANGES: list[tuple[str, str]] = [("2024-09-28","2025-04-12")] # leave empty for no exclusions

# -----------------------------------------------------------------------------
# Counterfactual stability diagnostics (run before estimator grid)
# -----------------------------------------------------------------------------
# These diagnostics test whether the treated series / treated-control mapping is
# structurally stable enough for counterfactual estimators to be trusted in the
# planned analysis window. Default estimator is TBRRidge only (fast); add AugSynthCVXPY
# explicitly if you need augmented SCM on the same panel (slower).
RUN_STABILITY_TESTS = True
STABILITY_OUTPUT_SUBDIR = "stability_tests"
# Set these before enabling RUN_STABILITY_TESTS. Each can be either:
# - None (disabled / required field not set)
# - a scalar label usable against the panel columns (e.g. "2025-12-13")
# - a dict keyed by dataset name and/or test_group name
STABILITY_TRAIN_END = "2025-12-06"
STABILITY_BREAK_START = "2025-12-13"
STABILITY_PSEUDO_TEST_START = "2025-12-13"
STABILITY_PSEUDO_TEST_END = "2026-01-17"
STABILITY_ESTIMATORS = ("TBRRidge", "AugSynthCVXPY")
# Optional: also run AugSynthCVXPY, e.g. ("TBRRidge", "AugSynthCVXPY")
STABILITY_ALPHA = 0.05

# -----------------------------------------------------------------------------
# AugSynth SCM donor pool configuration
# These constants are read by MMTAnalysis._setup_model_selection() when
# constructing AugSynthCVXPY. Tune threshold and lambda here without touching
# model code.
#   donor_correlation_threshold: drop donors whose pre-period correlation with
#     the treated series is below this value. 0.0 = no filtering (backward
#     compatible). Recommended for geo panels: 0.5–0.7.
#   min_donors: minimum donors to keep regardless of threshold (fallback).
#   lambda_reg: L2 regularisation on SCM weights. 0.0 = no regularisation.
#     Higher values spread weight across more donors. Recommended: 0.01–0.1.
# -----------------------------------------------------------------------------
AUGSYNTH_DONOR_CORRELATION_THRESHOLD = 0.5
AUGSYNTH_MIN_DONORS = 5
AUGSYNTH_LAMBDA_REG = 0.01
STABILITY_CONTROL_TRANSFORM = "auto"   # "aggregate", "pca", or "auto"
# Set to False if you want to skip heterogeneity check for speed
# and use STABILITY_CONTROL_TRANSFORM directly without auto-selection
STABILITY_RUN_HETEROGENEITY_CHECK = True
STABILITY_N_CONTROL_PCS = 3
STABILITY_TIME_COLUMN = "date"
STABILITY_GEO_COLUMN_CANDIDATES = (
    "geo", "dma", "gma", "state", "region", "market", "geo_id", "dma_name"
)

# Readout notebook (always use this for MMT analysis)
READOUT_NOTEBOOK_PATH = "/Users/ppavuluri/Desktop/test_readout.ipynb"

# Columns to export to CSV (only existing columns are used)
# DID: Absolute Effect = cumulative ATT; 95 CI, Effect Lower/Upper = cumulative. att_per_period = per-period (informational).



def _apply_date_exclusions(
    df: pd.DataFrame,
    exclude_date_ranges: list[tuple[str, str]],
    date_col: str = "date",
) -> pd.DataFrame:
    """Drop rows in given date ranges (inclusive). For sensitivity checks, e.g. excluding shock weeks.
    Returns df unchanged if exclude_date_ranges is empty."""
    if not exclude_date_ranges:
        return df
    if date_col not in df.columns:
        raise ValueError(f"Date column '{date_col}' not found in dataframe (columns: {list(df.columns)})")
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    for start_date, end_date in exclude_date_ranges:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        mask = (out[date_col] >= start_dt) & (out[date_col] <= end_dt)
        out = out.loc[~mask].copy()
    return out


# -----------------------------------------------------------------------------
# Counterfactual stability test helpers
# -----------------------------------------------------------------------------

def _normalize_group_units(units: Any) -> list[str]:
    if units is None:
        return []
    if isinstance(units, str):
        return [units]
    if isinstance(units, (list, tuple, set, np.ndarray, pd.Series)):
        return [str(x) for x in units]
    return [str(units)]


def _resolve_stability_value(value: Any, dataset_name: str, test_group: str) -> Any:
    """Resolve scalar or dict-valued stability config.

    Lookup order for dicts:
      1. (dataset_name, test_group) tuple key
      2. dataset_name
      3. test_group
      4. "default"
    """
    if not isinstance(value, dict):
        return value
    if (dataset_name, test_group) in value:
        return value[(dataset_name, test_group)]
    if dataset_name in value:
        return value[dataset_name]
    if test_group in value:
        return value[test_group]
    return value.get("default")


def _infer_geo_column(df: pd.DataFrame) -> str:
    for col in STABILITY_GEO_COLUMN_CANDIDATES:
        if col in df.columns:
            return col
    raise ValueError(
        "Could not infer geo column for stability diagnostics. "
        f"Expected one of {STABILITY_GEO_COLUMN_CANDIDATES}, found columns={list(df.columns)}"
    )


def _build_stability_wide_panel(
    dataset_obj: Any,
    dataset_name: str,
    kpi_col: str,
    treated_units: list[str],
    control_units: list[str],
    time_col: str = STABILITY_TIME_COLUMN,
) -> pd.DataFrame:
    """Convert dataset to wide unit x time matrix for stability diagnostics.

    Supports:
      - long DataFrame with [time_col, geo_col, kpi_col]
      - wide DataFrame already indexed by geo with time columns
      - PanelDataset
    """
    try:
        from panel_exp.panel_data import PanelDataset
    except Exception:  # pragma: no cover
        PanelDataset = None

    allowed_units = set(map(str, treated_units + control_units))
    if not allowed_units:
        raise ValueError(f"No treated/control units supplied for dataset={dataset_name}")

    if PanelDataset is not None and isinstance(dataset_obj, PanelDataset):
        wide = dataset_obj.wide_data.copy()
        wide.index = wide.index.map(str)
        keep = [u for u in wide.index if u in allowed_units]
        if not keep:
            raise ValueError(
                f"No treated/control units found in PanelDataset for dataset={dataset_name}; "
                f"allowed_units={sorted(allowed_units)}"
            )
        wide = wide.loc[keep].sort_index(axis=0).sort_index(axis=1)
        if not wide.columns.is_unique:
            raise ValueError(
                f"PanelDataset wide_data has duplicate time columns for dataset={dataset_name} "
                f"(first columns: {list(wide.columns[:8])!r})."
            )
        wide = wide.apply(pd.to_numeric, errors="coerce")
        if wide.isna().any().any():
            n_nan = int(wide.isna().sum().sum())
            raise ValueError(
                f"PanelDataset wide panel has NaN for dataset={dataset_name} (n_nan={n_nan}). "
                "Stability tests require fully numeric cells."
            )
        return wide.astype(np.float64)

    if not isinstance(dataset_obj, pd.DataFrame):
        raise TypeError(
            f"Unsupported dataset type for stability diagnostics: {type(dataset_obj)} (dataset={dataset_name})"
        )

    df = dataset_obj.copy()

    # Long-form path: full geo × date grid; missing (geo, date) treated as KPI=0 (count outcome).
    if time_col in df.columns and kpi_col and kpi_col in df.columns:
        geo_col = _infer_geo_column(df)
        n_treated_units = len(treated_units)
        n_control_units = len(control_units)
        df[geo_col] = df[geo_col].astype(str)
        df = df[df[geo_col].isin(allowed_units)].copy()
        if len(df) == 0:
            raise ValueError(
                "_build_stability_wide_panel: no rows left after filtering to treated/control geos "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units}, geo_col={geo_col!r}, "
                f"allowed_units={sorted(allowed_units)!r})."
            )
        df[time_col] = pd.to_datetime(df[time_col])
        unique_dates = pd.Index(df[time_col].unique()).sort_values()
        n_dates = int(len(unique_dates))
        if n_dates == 0:
            raise ValueError(
                "_build_stability_wide_panel: no dates in filtered slice "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units})."
            )

        kpi_num = pd.to_numeric(df[kpi_col], errors="coerce")
        if kpi_num.isna().any():
            n_bad = int(kpi_num.isna().sum())
            raise ValueError(
                "_build_stability_wide_panel: non-numeric KPI values (cannot coerce to float) "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units}, n_dates_in_slice={n_dates}, "
                f"n_non_numeric_kpi_rows={n_bad})."
            )
        df = df.assign(**{kpi_col: kpi_num})

        key_cols = [geo_col, time_col]
        dup_sizes = df.groupby(key_cols, sort=False).size()
        n_dup_keys = int((dup_sizes > 1).sum())
        if n_dup_keys > 0:
            warnings.warn(
                f"[STABILITY] dataset={dataset_name!r} kpi={kpi_col!r}: {n_dup_keys} (geo, date) key(s) "
                "have duplicate long-form rows; summing KPI before building the balanced grid.",
                UserWarning,
                stacklevel=2,
            )
            df_long = df.groupby(key_cols, as_index=False, sort=False)[kpi_col].sum()
        else:
            df_long = df[key_cols + [kpi_col]].copy()

        units_for_panel = sorted(allowed_units)
        full_index = pd.MultiIndex.from_product(
            [units_for_panel, unique_dates],
            names=key_cols,
        )
        df_indexed = df_long.set_index(key_cols)
        balanced = df_indexed.reindex(full_index)
        balanced[kpi_col] = balanced[kpi_col].fillna(0.0)

        if balanced[kpi_col].isna().any():
            n_nan = int(balanced[kpi_col].isna().sum())
            raise ValueError(
                "_build_stability_wide_panel: remaining NaN in KPI after zero-fill (unexpected) "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units}, n_dates={n_dates}, n_nan_kpi={n_nan})."
            )

        wide = balanced[kpi_col].unstack(level=time_col)
        wide = wide.sort_index(axis=0).sort_index(axis=1)
        if not wide.columns.is_unique:
            raise ValueError(
                "_build_stability_wide_panel: duplicate time columns after pivot "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units}, n_dates={n_dates}, "
                f"first columns={list(wide.columns[:8])!r})."
            )
        wide = wide.apply(pd.to_numeric, errors="coerce")
        if wide.isna().any().any():
            n_nan = int(wide.isna().sum().sum())
            raise ValueError(
                "_build_stability_wide_panel: remaining NaN after pivot/numeric coercion "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units}, n_dates={n_dates}, n_nan_cells={n_nan})."
            )
        arr = wide.to_numpy(dtype=np.float64, copy=False)
        if not np.isfinite(arr).all():
            n_bad = int(np.sum(~np.isfinite(arr)))
            raise ValueError(
                "_build_stability_wide_panel: non-finite values in wide panel "
                f"(dataset={dataset_name!r}, kpi_col={kpi_col!r}, n_treated_units={n_treated_units}, "
                f"n_control_units={n_control_units}, n_dates={n_dates}, n_non_finite_cells={n_bad})."
            )
        return wide.astype(np.float64)

    # Assume already wide (rows = geos, columns = time periods)
    wide = df.copy()
    wide.index = wide.index.map(str)
    if not wide.columns.is_unique:
        raise ValueError(
            f"Wide dataframe has duplicate column labels for dataset={dataset_name} "
            f"(first columns: {list(wide.columns[:8])!r})."
        )
    keep = [u for u in wide.index if u in allowed_units]
    if not keep:
        raise ValueError(
            f"Could not match treated/control units to wide dataframe index for dataset={dataset_name}; "
            f"allowed_units={sorted(allowed_units)}"
        )
    wide = wide.loc[keep].sort_index(axis=0).sort_index(axis=1)
    wide = wide.apply(pd.to_numeric, errors="coerce")
    if wide.isna().any().any():
        n_nan = int(wide.isna().sum().sum())
        raise ValueError(
            f"Wide panel has NaN after coercion for dataset={dataset_name} (n_nan={n_nan}). "
            "Stability tests require fully numeric cells."
        )
    return wide.astype(np.float64)


def _save_counterfactual_stability_outputs(
    summary: Any,
    output_dir: str,
    dataset_name: str,
    test_group: str,
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    safe_dataset = str(dataset_name).replace("/", "_")
    safe_group = str(test_group).replace("/", "_")
    stem = f"{safe_dataset}__{safe_group}__counterfactual_stability"

    frame = summary.to_frame() if hasattr(summary, "to_frame") else pd.DataFrame(summary)
    csv_path = os.path.join(output_dir, f"{stem}.csv")
    frame.to_csv(csv_path, index=False)

    payload = summary.to_dict() if hasattr(summary, "to_dict") else {"results": frame.to_dict(orient="records")}
    json_path = os.path.join(output_dir, f"{stem}.json")
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"  Saved stability diagnostics: {csv_path}")
    print(f"  Saved stability diagnostics: {json_path}")


def _run_and_save_counterfactual_stability_tests(mmt: Any, base_dir: str) -> None:
    """Run structural-break + residual-drift diagnostics before estimator grid.

    This is optional and guarded by RUN_STABILITY_TESTS. Diagnostics are saved as
    dataset/test_group-level CSV/JSON artifacts under BASE_OUTPUT_DIR/stability_tests.
    """
    if not RUN_STABILITY_TESTS:
        return

    if run_counterfactual_stability_tests is None:
        warnings.warn(
            "RUN_STABILITY_TESTS=True but panel_exp.utils.counterfactual_stability_tests could not be imported. "
            "Skipping stability diagnostics.",
            UserWarning,
        )
        return

    required = {
        "STABILITY_BREAK_START": STABILITY_BREAK_START,
        "STABILITY_TRAIN_END": STABILITY_TRAIN_END,
        "STABILITY_PSEUDO_TEST_START": STABILITY_PSEUDO_TEST_START,
        "STABILITY_PSEUDO_TEST_END": STABILITY_PSEUDO_TEST_END,
    }
    missing = [name for name, value in required.items() if value is None]
    if missing:
        warnings.warn(
            "RUN_STABILITY_TESTS=True but required stability window configs are unset: "
            f"{missing}. Skipping stability diagnostics.",
            UserWarning,
        )
        return

    print("[STABILITY] Starting counterfactual stability diagnostics (runs before estimator grid).")

    datasets = getattr(mmt.config, "datasets", None) or {}
    kpi_map = getattr(mmt.config, "kpi", None) or {}
    test_groups = getattr(mmt.config, "test_groups", None) or {}
    control_groups = getattr(mmt.config, "control_groups", None) or {}

    if RUN_ONLY_DATASETS is not None:
        allowed = set(RUN_ONLY_DATASETS)
        datasets = {k: v for k, v in datasets.items() if k in allowed}

    out_dir = os.path.join(base_dir, STABILITY_OUTPUT_SUBDIR)
    aggregate_rows: list[pd.DataFrame] = []

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        warnings.filterwarnings("ignore", message="divide by zero encountered.*", category=RuntimeWarning)
        warnings.filterwarnings("ignore", message="invalid value encountered.*", category=RuntimeWarning)
        warnings.filterwarnings("ignore", message=".*LAPACK.*", category=RuntimeWarning)

        for dataset_name, dataset_obj in datasets.items():
            kpi_col = kpi_map.get(dataset_name)
            if not isinstance(kpi_col, str) and isinstance(dataset_obj, pd.DataFrame):
                # If dataset is already wide or no KPI mapping is needed, keep going.
                kpi_col = kpi_col if isinstance(kpi_col, str) else ""

            for test_group, treated in test_groups.items():
                treated_units = _normalize_group_units(treated)
                control_units = _normalize_group_units(control_groups.get(test_group))
                if not treated_units or not control_units:
                    warnings.warn(
                        f"Skipping stability diagnostics for dataset={dataset_name}, test_group={test_group}: "
                        "treated/control groups are missing.",
                        UserWarning,
                    )
                    continue

                break_start = _resolve_stability_value(STABILITY_BREAK_START, dataset_name, test_group)
                train_end = _resolve_stability_value(STABILITY_TRAIN_END, dataset_name, test_group)
                pseudo_start = _resolve_stability_value(STABILITY_PSEUDO_TEST_START, dataset_name, test_group)
                pseudo_end = _resolve_stability_value(STABILITY_PSEUDO_TEST_END, dataset_name, test_group)
                if None in (break_start, train_end, pseudo_start, pseudo_end):
                    warnings.warn(
                        f"Skipping stability diagnostics for dataset={dataset_name}, test_group={test_group}: "
                        "break/train/pseudo-test window is not fully configured.",
                        UserWarning,
                    )
                    continue

                print(
                    f"[STABILITY] Running dataset={dataset_name!r} test_group={test_group!r} "
                    f"(break={break_start!r}, train_end={train_end!r}, pseudo=[{pseudo_start!r}..{pseudo_end!r}])"
                )
                try:
                    t_block0 = time.perf_counter()
                    wide = _build_stability_wide_panel(
                        dataset_obj=dataset_obj,
                        dataset_name=str(dataset_name),
                        kpi_col=str(kpi_col),
                        treated_units=treated_units,
                        control_units=control_units,
                        time_col=STABILITY_TIME_COLUMN,
                    )
                    t_after_wide = time.perf_counter()
                    _stability_key = f"{dataset_name}/{test_group}"
                    print(f"[STABILITY_PERF] {_stability_key} wide_panel_build_elapsed_s={t_after_wide - t_block0:.3f}")
                    summary = run_counterfactual_stability_tests(
                        data=wide,
                        treated_units=treated_units,
                        break_start=break_start,
                        train_end=train_end,
                        pseudo_test_start=pseudo_start,
                        pseudo_test_end=pseudo_end,
                        control_units=control_units,
                        estimators=STABILITY_ESTIMATORS,
                        alpha=STABILITY_ALPHA,
                        control_transform=STABILITY_CONTROL_TRANSFORM,
                        n_control_pcs=STABILITY_N_CONTROL_PCS,
                        log_label=_stability_key,
                        run_heterogeneity_check=STABILITY_RUN_HETEROGENEITY_CHECK,
                    )
                    t_after_stab = time.perf_counter()
                    print(
                        f"[STABILITY_PERF] {_stability_key} counterfactual_stability_tests_elapsed_s="
                        f"{t_after_stab - t_after_wide:.3f} total_elapsed_s={t_after_stab - t_block0:.3f}"
                    )
                    _save_counterfactual_stability_outputs(summary, out_dir, str(dataset_name), str(test_group))

                    # Estimator agreement check
                    if compare_estimator_stability is not None and len(summary.residual_drift_tests) > 1:
                        comparison = compare_estimator_stability(summary.residual_drift_tests)
                        print(f"[STABILITY] Estimator agreement: {comparison['agreement']}")
                        print(f"[STABILITY] {comparison['interpretation']}")

                    # AugSynthCVXPY weight health check
                    if (
                        check_AugSynthCVXPY_weight_health is not None
                        and build_pseudo_test_paneldataset is not None
                        and "AugSynthCVXPY" in STABILITY_ESTIMATORS
                    ):
                        try:
                            _pds_for_health = build_pseudo_test_paneldataset(
                                data=wide,
                                treated_units=treated_units,
                                train_end=train_end,
                                pseudo_test_start=pseudo_start,
                                pseudo_test_end=pseudo_end,
                            )
                            weight_health = check_AugSynthCVXPY_weight_health(_pds_for_health)
                            print(f"[STABILITY] AugSynthCVXPY weight verdict: {weight_health['verdict']}")
                            print(f"[STABILITY] {weight_health['notes']}")
                        except Exception as _wh_exc:
                            warnings.warn(
                                f"[STABILITY] AugSynthCVXPY weight health check failed (non-fatal): {_wh_exc}",
                                UserWarning,
                            )

                    frame = summary.to_frame() if hasattr(summary, "to_frame") else pd.DataFrame(summary)
                    if len(frame) > 0:
                        frame = frame.copy()
                        frame.insert(0, "dataset", str(dataset_name))
                        frame.insert(1, "test_group", str(test_group))
                        aggregate_rows.append(frame)
                    print(
                        f"[STABILITY] Finished dataset={dataset_name!r} test_group={test_group!r} OK."
                    )
                except Exception as exc:
                    warnings.warn(
                        f"Counterfactual stability diagnostics failed for dataset={dataset_name}, "
                        f"test_group={test_group}: {exc}",
                        UserWarning,
                    )

    if aggregate_rows:
        aggregate_df = pd.concat(aggregate_rows, ignore_index=True)
        aggregate_path = os.path.join(out_dir, "counterfactual_stability_summary.csv")
        aggregate_df.to_csv(aggregate_path, index=False)
        print(f"  Saved stability diagnostics summary: {aggregate_path}")

    print("[STABILITY] Counterfactual stability diagnostics pass complete.")


CSV_COLUMNS = [
    "Test_Group",
    "Cloud",
    "Cumulative ATT",
    "Mean post-period ATT",
    "Absolute Effect",
    "Effect Lower",
    "Effect Upper",
    "Relative Effect (%)",
    "95 CI",
    "p-value",
    "L3M_AOV",
    "Pre-test R² (forward OOS)",
    "Pre-test forward OOS overfitting flag",
    "DID Treatment Effect",
    "DID Treatment Effect (per geo)",
    "att_per_period",
    "DID Standard Error",
    "DID P-value",
    "DID Significant",
    "Parallel Trends Valid",
    "Pre-trend Joint P-value",
    "Pre-trend Test Type",
    "Largest Pre-trend Deviation",
    "Largest Pre-trend Period",
    "Inference Method",
    "Bootstrap N",
    "Model-Based SE",
    "Model-Based P-value",
    "Placebo Test Passed",
    "BRB block_length",
    "BRB bootstrap_std",
    "BRB residual_pool_size",
    "BRB residual_pool_to_block_ratio",
    "BRB bootstrap_std_conditional",
    "BRB brb_valid_flag",
    "BRB brb_diagnostic_status",
    "BRB brb_to_kfold_ci_width_ratio",
    "BRB ci_method",
    "BRB bootstrap_skew",
    "BRB estimator_variance_fraction",
    "BRB bootstrap_failure_rate",
    "ci_scale",
]

# (model_selection key, inference value for constructor, inference display name, estimator display name)
# NOTE: Notebook must have these keys in _setup_model_selection: BayesianTBRHorseShoe, TBRAutoSARIMAX
COMBINATIONS = [
    # TBR + Placebo excluded: TBR requires aggregated control (1 unit), placebo-in-space needs >=5 controls
    ("TBR", "BlockResidualBootstrap", "BlockResidualBootstrap", "TBR"),
    ("TBRRidge", "BlockResidualBootstrap", "BlockResidualBootstrap", "TBRRidge"),
    ("AugSynthCVXPY", "BlockResidualBootstrap", "BlockResidualBootstrap", "AugSynthCVXPY"),
    # ("SyntheticControlCVXPY", "BlockResidualBootstrap", "BlockResidualBootstrap", "SyntheticControlCVXPY"),
    ("TBR", "TimeSeriesKfold", "TimeSeriesKfold", "TBR"),
    ("TBRRidge", "TimeSeriesKfold", "TimeSeriesKfold", "TBRRidge"),
    ("AugSynthCVXPY", "TimeSeriesKfold", "TimeSeriesKfold", "AugSynthCVXPY"),
    # ("SyntheticControlCVXPY", "TimeSeriesKfold", "TimeSeriesKfold", "SyntheticControlCVXPY"),
    # ("TBRRidge", "Placebo", "Placebo", "TBRRidge"),
    # ("AugSynthCVXPY", "Placebo", "Placebo", "AugSynthCVXPY"),
    # ("SyntheticControlCVXPY", "Placebo", "Placebo", "SyntheticControlCVXPY"),
    # ("TBR", "Conformal", "Conformal", "TBR"),
    # ("TBRRidge", "Conformal", "Conformal", "TBRRidge"),
    # ("AugSynthCVXPY", "Conformal", "Conformal", "AugSynthCVXPY"),
    # ("SyntheticControlCVXPY", "Conformal", "Conformal", "SyntheticControlCVXPY"),
    # ("TBRRidge", "UnitJackKnife", "UnitJackKnife", "TBRRidge"),
    # ("AugSynthCVXPY", "UnitJackKnife", "UnitJackKnife", "AugSynthCVXPY"),
    # ("SyntheticControlCVXPY", "UnitJackKnife", "UnitJackKnife", "SyntheticControlCVXPY"),
    ("TBR", "Kfold", "Kfold", "TBR"),
    ("TBRRidge", "Kfold", "Kfold", "TBRRidge"),
    ("AugSynthCVXPY", "Kfold", "Kfold", "AugSynthCVXPY"),  
    # ("SyntheticControlCVXPY", "Kfold", "Kfold", "SyntheticControlCVXPY"), 
    ("BayesianTBR", None, "self", "Bayesian_TBR"),
    ("BayesianTBRHorseShoe", None, "self", "Bayesian_TBR_HorseShoe"),
    # ("TBRAutoSARIMAX", "Kfold", "Kfold", "TBRAutoSARIMAX"),
    # ("TBRAutoSARIMAX", "Conformal", "Conformal", "TBRAutoSARIMAX"),
    # ("DID", None, "self", "DID"),
    # ("SyntheticDID", None, "self", "SyntheticDID"),
    # ("Trop", None, "self", "Trop"),
]


def _get_mmt_kwargs(mmt: Any) -> dict:
    """Build MMTAnalysis constructor kwargs from existing mmt (same config, no model/inference)."""
    datasets = mmt.config.datasets
    kpi = mmt.config.kpi
    if RUN_ONLY_DATASETS is not None:
        allowed = set(RUN_ONLY_DATASETS)
        datasets = {k: v for k, v in datasets.items() if k in allowed}
        kpi = {k: v for k, v in kpi.items() if k in allowed}
    return {
        "test_groups": mmt.config.test_groups,
        "control_groups": mmt.config.control_groups,
        "datasets": datasets,
        "kpi": kpi,
        "test_start_dates": mmt.config.test_start_dates,
        "test_end_dates": mmt.config.test_end_dates,
        "panel_aggregation_config": mmt.config.aggregation,
        "mlflow_run_name": getattr(mmt, "mlflow_run_name", "mmt_results"),
        "alpha": getattr(mmt, "alpha", 0.1),
    }


# Threshold for invalid numerical values (y_hat, y_lower, y_upper explosion from DID/SyntheticDID)
_INVALID_VALUE_THRESHOLD = 1e10

# Tolerance for effect = y - y_hat consistency check
_EFFECT_CONSISTENCY_TOL = 1e-6

# Tolerance for mean(post_period effect) ≈ aggregate_ATT sanity check
_ATT_CONSISTENCY_TOL = 1e-4


def _validate_att_consistency(
    weekly_trends_dct: dict,
    summary_stats_df: Any,
    estimator_display: str,
    config: Any,
) -> None:
    """Warn if mean(post_period(y - y_hat)) differs from aggregate ATT (would have caught original SDID bug).

    Complements _validate_weekly_effect_consistency: that checks pointwise effect == y - y_hat;
    this checks aggregate post-period consistency mean(post(y - y_hat)) == aggregate_ATT.

    Expected by design: If Absolute Effect is cumulative (sum over post period), then
    mean(post_period(y - y_hat)) != Absolute Effect — one is per-period mean, the other is
    cumulative total. No warning in that case.
    If Absolute Effect is mean per-period ATT, they should match; mismatch triggers a warning."""
    if not weekly_trends_dct or summary_stats_df is None:
        return
    is_did_or_sdid = "DID" in estimator_display or "SyntheticDID" in estimator_display or "SDID" in estimator_display
    if not is_did_or_sdid:
        return
    if not isinstance(summary_stats_df, pd.DataFrame) or "Absolute Effect" not in summary_stats_df.columns:
        return
    sdf = summary_stats_df.copy()
    sdf["Absolute Effect"] = pd.to_numeric(sdf["Absolute Effect"], errors="coerce")
    for key, df in weekly_trends_dct.items():
        if not isinstance(df, pd.DataFrame):
            continue
        if not all(c in df.columns for c in ("y", "y_hat", "dt")):
            continue
        test_group = key[0] if isinstance(key, (list, tuple)) else None
        dataset = str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else None
        treatment_start = None
        if test_group and config and getattr(config, "test_start_dates", None):
            treatment_start = pd.to_datetime(config.test_start_dates.get(test_group, ""), errors="coerce")
        if pd.isna(treatment_start):
            continue
        post_mask = (pd.to_datetime(df["dt"]) >= treatment_start).values
        if not np.any(post_mask):
            continue
        y = pd.to_numeric(df["y"], errors="coerce").values
        y_hat = pd.to_numeric(df["y_hat"], errors="coerce").values
        mean_post = float(np.nanmean((y - y_hat)[post_mask]))
        agg_att = None
        if "Test_Group" in sdf.columns and "Cloud" in sdf.columns:
            mask = sdf["Test_Group"].astype(str) == str(test_group)
            if dataset:
                mask = mask & (sdf["Cloud"].astype(str) == str(dataset))
            match = sdf.loc[mask, "Absolute Effect"].dropna()
            if len(match):
                agg_att = float(match.iloc[0])
        if agg_att is None and len(sdf) == 1:
            agg_att = float(sdf["Absolute Effect"].iloc[0])
        if agg_att is None or not np.isfinite(agg_att):
            continue
        n_post = int(np.sum(post_mask))
        diff_mean = abs(mean_post - agg_att)
        # For DID: regression-based aggregate ATT is primary; descriptive path gap (mean_post) may differ by design.
        # Do not treat this as an error — skip warning for DID.
        if "DID" in estimator_display and "SyntheticDID" not in estimator_display:
            continue
        # If Absolute Effect is cumulative, mean_post != agg_att by design — skip warning
        diff_cumulative = abs(mean_post * n_post - agg_att) if n_post > 0 else np.inf
        rel_tol = _ATT_CONSISTENCY_TOL * max(abs(agg_att), 1.0)
        is_likely_cumulative = n_post > 1 and diff_cumulative < rel_tol
        if is_likely_cumulative:
            continue  # Expected: one is per-period mean, the other is cumulative total
        if diff_mean > rel_tol:
            warnings.warn(
                f"{estimator_display} (dataset={dataset or key}): mean(post_period(y - y_hat))={mean_post:.4f} "
                f"!= aggregate_ATT={agg_att:.4f} (diff={diff_mean:.4e}). "
                f"If Absolute Effect is cumulative, this is expected. Otherwise check estimator exported effect path.",
                UserWarning,
                stacklevel=2,
            )


def _validate_weekly_effect_consistency(
    weekly_trends_dct: dict,
    estimator_display: str,
    config: Any,
) -> None:
    """Warn if effect != y - y_hat for DID/SDID (catches SDID bug where post-period effect was constant)."""
    if not weekly_trends_dct:
        return
    is_did_or_sdid = "DID" in estimator_display or "SyntheticDID" in estimator_display or "SDID" in estimator_display
    if not is_did_or_sdid:
        return
    for key, df in weekly_trends_dct.items():
        if not isinstance(df, pd.DataFrame):
            continue
        if not all(c in df.columns for c in ("y", "y_hat", "effect")):
            continue
        y = pd.to_numeric(df["y"], errors="coerce").values
        y_hat = pd.to_numeric(df["y_hat"], errors="coerce").values
        effect = pd.to_numeric(df["effect"], errors="coerce").values
        residual = (y - y_hat) - effect
        max_resid = float(np.nanmax(np.abs(residual)))
        if max_resid > _EFFECT_CONSISTENCY_TOL:
            import warnings
            dataset_str = str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else str(key)
            warnings.warn(
                f"{estimator_display} (dataset={dataset_str}): effect != y - y_hat in weekly output "
                f"(max |residual|={max_resid:.2e}). Key={key}. Fix estimator exported effect path.",
                UserWarning,
                stacklevel=2,
            )


def _sanitize_weekly_trends(weekly_trends_dct: dict) -> dict:
    """Replace absurd y_hat, y_lower, y_upper (e.g. 1e13 from numerical explosion) with NaN."""
    out = {}
    for key, df in weekly_trends_dct.items():
        if not isinstance(df, pd.DataFrame):
            out[key] = df
            continue
        df = df.copy()
        for col in ("y_hat", "y_lower", "y_upper"):
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce")
                bad = (vals.abs() > _INVALID_VALUE_THRESHOLD) | np.isinf(vals)
                if bad.any():
                    df[col] = vals.where(~bad, np.nan)
        out[key] = df
    return out


def _diagnose_did_sdid_csv_row(
    df: pd.DataFrame,
    estimator_display: str,
    n_post_series: pd.Series,
    base_dir: str,
    weekly_trends_dct: Any = None,
    config: Any = None,
) -> None:
    """Print CSV consistency diagnostic for first DID/SDID row. Phase 6: n_post and cum_att from pickle (effect column)."""
    if len(df) == 0:
        return
    is_did = "DID" in estimator_display and "SyntheticDID" not in estimator_display
    row = df.iloc[0]
    cloud = str(row.get("Cloud", "?"))
    if is_did:
        diag_path = os.path.join(base_dir, "self_DID_did_diagnostics.json")
        diag = None
        if os.path.exists(diag_path):
            try:
                with open(diag_path) as f:
                    diag = json.load(f)
            except Exception:
                pass
        cum_ci = (diag.get("cumulative_ci") or diag.get("treatment_ci_aggregate") or diag.get("treatment_ci")) if diag else None
        # Phase 6: recompute n_post from pickle (effect column), not from CSV
        cum_att_from_pickle = None
        n_post_from_pickle = 0
        if weekly_trends_dct and config:
            test_start = getattr(config, "test_start_dates", None) or {}
            tg = str(row.get("Test_Group", ""))
            treatment_start = pd.to_datetime(test_start.get(str(tg), ""), errors="coerce") if tg else pd.NaT
            for key, wdf in weekly_trends_dct.items():
                if not isinstance(wdf, pd.DataFrame) or "dt" not in wdf.columns or "effect" not in wdf.columns:
                    continue
                k_tg = key[0] if isinstance(key, (list, tuple)) and len(key) > 0 else None
                k_cloud = str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else ""
                if str(k_tg) != tg or (k_cloud and str(k_cloud) != cloud):
                    continue
                post_mask = pd.to_datetime(wdf["dt"]) >= treatment_start
                n_post_from_pickle = int(post_mask.sum())
                if post_mask.any():
                    eff_vals = pd.to_numeric(wdf.loc[post_mask, "effect"], errors="coerce").dropna()
                    if len(eff_vals) > 0:
                        cum_att_from_pickle = float(eff_vals.sum())
                break
        n_post = n_post_from_pickle
        # cumulative_ci is already cumulative; no scaling
        exp_lower = float(cum_ci[0]) if (cum_ci and len(cum_ci) >= 2) else None
        exp_upper = float(cum_ci[1]) if (cum_ci and len(cum_ci) >= 2) else None
        cum_att = cum_att_from_pickle  # path-based only; no treatment_effect_aggregate fallback
        abs_eff = pd.to_numeric(row.get("Absolute Effect"), errors="coerce")
        eff_lo = pd.to_numeric(row.get("Effect Lower"), errors="coerce")
        eff_hi = pd.to_numeric(row.get("Effect Upper"), errors="coerce")
        rel_eff = pd.to_numeric(row.get("Relative Effect (%)"), errors="coerce")
        post_sum = pd.to_numeric(row.get("actual"), errors="coerce")
        inc = []
        if cum_att is not None and np.isfinite(abs_eff) and abs(float(abs_eff) - cum_att) > 0.5:
            inc.append(f"Absolute Effect ({abs_eff}) != cumulative_att ({cum_att})")
        if exp_lower is not None and np.isfinite(eff_lo) and abs(float(eff_lo) - exp_lower) > 0.5:
            inc.append(f"Effect Lower ({eff_lo}) != expected ({exp_lower})")
        if exp_upper is not None and np.isfinite(eff_hi) and abs(float(eff_hi) - exp_upper) > 0.5:
            inc.append(f"Effect Upper ({eff_hi}) != expected ({exp_upper})")
        if post_sum and post_sum > 0 and cum_att is not None and np.isfinite(rel_eff):
            exp_rel = cum_att / float(post_sum) * 100
            if abs(float(rel_eff) - exp_rel) > 0.01:
                inc.append(f"Relative Effect ({rel_eff}%) != expected ({exp_rel:.2f}%)")
        print(f"  [DID CSV diagnostic] {cloud}: n_post={n_post} cum_att_from_pickle={cum_att_from_pickle} "
              f"csv_Absolute_Effect={abs_eff} csv_Effect_Lower={eff_lo} csv_Effect_Upper={eff_hi} "
              f"post_actual_sum={post_sum}")
        # Phase 7: strict validation (path-based)
        if cum_att_from_pickle is not None and diag and n_post > 0:
            mean_from_pickle = cum_att_from_pickle / n_post
            diag_cum = diag.get("cumulative_att")
            diag_mean = diag.get("mean_post_period_att")
            diag_ci = diag.get("cumulative_ci") or diag.get("treatment_ci_aggregate")
            print(f"  [DID validation] sum(effect_post)={cum_att_from_pickle:.0f} mean(effect_post)={mean_from_pickle:.0f} "
                  f"n_post={n_post} | diag cumulative_att={diag_cum} mean_post_period_att={diag_mean} cumulative_ci={diag_ci}")
            if np.isfinite(cum_att_from_pickle) and diag_cum is not None and abs(float(cum_att_from_pickle) - float(diag_cum)) > 0.5:
                print(f"  [DID ERROR] cumulative_att mismatch: pickle={cum_att_from_pickle} != diag={diag_cum}")
            if np.isfinite(mean_from_pickle) and diag_mean is not None and abs(float(mean_from_pickle) - float(diag_mean)) > 0.5:
                print(f"  [DID ERROR] mean_post_period_att mismatch: pickle={mean_from_pickle} != diag={diag_mean}")
        if inc:
            print(f"    INCONSISTENCIES: {inc}")
    else:
        # SyntheticDID: Absolute Effect = per-period, Cumulative = abs_eff * n_post (n_post from pickle via n_post_series)
        n_post = int(n_post_series.iloc[0]) if len(n_post_series) else 0
        abs_eff = pd.to_numeric(row.get("Absolute Effect"), errors="coerce")
        cum_att = pd.to_numeric(row.get("Cumulative ATT"), errors="coerce")
        exp_cum = float(abs_eff) * n_post if (np.isfinite(abs_eff) and n_post > 0) else None
        inc = []
        if exp_cum is not None and np.isfinite(cum_att) and abs(float(cum_att) - exp_cum) > 0.5:
            inc.append(f"Cumulative ATT ({cum_att}) != Absolute Effect * n_post ({exp_cum})")
        print(f"  [SyntheticDID CSV diagnostic] {cloud}: n_post={n_post} csv_Absolute_Effect={abs_eff} "
              f"csv_Cumulative_ATT={cum_att} expected_Cumulative={exp_cum}")
        if inc:
            print(f"    INCONSISTENCIES: {inc}")


def _save_results(
    weekly_trends_dct: Any,
    summary_stats_df: Any,
    inference_display: str,
    estimator_display: str,
    base_dir: str,
    csv_columns: list[str],
    config: Any = None,
) -> None:
    """Save pickle and CSV with inference and estimator in filenames."""
    os.makedirs(base_dir, exist_ok=True)
    safe_inf = inference_display.replace("/", "_")
    safe_est = estimator_display.replace("/", "_")

    weekly_trends_dct = _sanitize_weekly_trends(weekly_trends_dct)
    pickle_path = os.path.join(base_dir, f"{safe_inf}_{safe_est}_weekly_trends_dct.pickle")
    with open(pickle_path, "wb") as f:
        pickle.dump(weekly_trends_dct, f, pickle.HIGHEST_PROTOCOL)
    print(f"  Saved: {pickle_path}")

    # Derive Effect Lower/Upper from Absolute Effect and 95 CI if not already present.
    # Placebo rows should have Effect Lower/Upper from effect_ci_*_inversion (notebook); do not overwrite.
    df = summary_stats_df.copy()
    # DID: Absolute Effect is already cumulative. SyntheticDID: Absolute Effect is per-period.
    is_did = "DID" in estimator_display and "SyntheticDID" not in estimator_display and "SDID" not in estimator_display
    is_did_sdid = "DID" in estimator_display or "SyntheticDID" in estimator_display or "SDID" in estimator_display

    # DID: path-based only. No regression-based validation; notebook provides path-based rows.

    if is_did_sdid and "Absolute Effect" in df.columns and weekly_trends_dct and config and len(df) > 0:
        abs_eff = pd.to_numeric(df["Absolute Effect"], errors="coerce")
        test_start = getattr(config, "test_start_dates", None) or {}
        key_to_n_post = {}
        for key, wdf in weekly_trends_dct.items():
            if not isinstance(wdf, pd.DataFrame) or "dt" not in wdf.columns:
                continue
            tg = key[0] if isinstance(key, (list, tuple)) and len(key) > 0 else None
            treatment_start = pd.to_datetime(test_start.get(str(tg), ""), errors="coerce") if tg else pd.NaT
            if pd.isna(treatment_start):
                continue
            post_mask = pd.to_datetime(wdf["dt"]) >= treatment_start
            n_post = int(post_mask.sum())
            k = (str(tg), str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else "")
            key_to_n_post[k] = n_post
        n_post_per_row = []
        for idx in range(len(df)):
            tg = str(df.loc[df.index[idx], "Test_Group"]) if "Test_Group" in df.columns else ""
            cloud = str(df.loc[df.index[idx], "Cloud"]) if "Cloud" in df.columns else ""
            n_post = key_to_n_post.get((tg, cloud), key_to_n_post.get((tg, ""), 0))
            if n_post == 0 and len(key_to_n_post) == 1:
                n_post = next(iter(key_to_n_post.values()), 0)
            n_post_per_row.append(n_post)
        n_post_series = pd.Series(n_post_per_row, index=df.index)
        if is_did:
            # DID: drop rows with n_post <= 0 (strict validation)
            bad = n_post_series <= 0
            if bad.any():
                for idx in df.index[bad]:
                    row = df.loc[idx]
                    tg = row.get("Test_Group", "?")
                    cloud = row.get("Cloud", "?")
                    n_post = int(n_post_series.loc[idx])
                    print(
                        f"DID row validation failed — skipping (n_post={n_post}). "
                        f"Test_Group={tg}, Cloud={cloud}"
                    )
                keep = ~bad
                df = df.loc[keep].copy()
                n_post_series = n_post_series.loc[keep]
                abs_eff = abs_eff.loc[keep]
            if len(df) == 0:
                print("DID: all rows dropped (n_post <= 0). Skipping CSV write.")
            else:
                print(f"n_post (computed): {n_post_series.tolist()}")
            # DID: Absolute Effect = cumulative ATT; Mean post-period = cumulative / n_post
            if len(df) > 0:
                df["Cumulative ATT"] = abs_eff
                df["Mean post-period ATT"] = np.where(
                    abs_eff.notna() & (n_post_series > 0),
                    abs_eff / n_post_series,
                    np.nan,
                )
        else:
            # SyntheticDID: Absolute Effect = per-period; Cumulative = abs_eff * n_post
            df["Mean post-period ATT"] = abs_eff
            df["Cumulative ATT"] = np.where(
                abs_eff.notna() & (n_post_series > 0),
                abs_eff * n_post_series,
                np.nan,
            )
        # DID/SDID CSV diagnostic (first row only); Phase 3: n_post debug
        if is_did and len(df) > 0:
            n_post_csv = int(n_post_series.iloc[0]) if len(n_post_series) else 0
            n_post_pickle = next(iter(key_to_n_post.values()), 0) if key_to_n_post else 0
            print(f"  [DID n_post] pickle post_mask count={n_post_pickle} CSV n_post={n_post_csv} match={n_post_pickle == n_post_csv}")
        _diagnose_did_sdid_csv_row(df, estimator_display, n_post_series, base_dir, weekly_trends_dct, config)
    derived_bounds = False
    if "Effect Lower" not in df.columns and "Absolute Effect" in df.columns and "95 CI" in df.columns:
        eff = pd.to_numeric(df["Absolute Effect"], errors="coerce")
        ci = pd.to_numeric(df["95 CI"], errors="coerce")
        half = np.where(ci.notna(), ci / 2.0, np.nan)
        df["Effect Lower"] = np.where(eff.notna(), eff - half, np.nan)
        df["Effect Upper"] = np.where(eff.notna(), eff + half, np.nan)
        derived_bounds = True

    # TROP: single scale — cumulative ATT, cumulative CI; 95 CI width = upper − lower (no n_post scaling).
    is_trop = "Trop" in estimator_display or safe_est == "Trop"
    if is_trop and len(df) > 0 and "Effect Lower" in df.columns and "Effect Upper" in df.columns:
        lb_col = pd.to_numeric(df["Effect Lower"], errors="coerce")
        ub_col = pd.to_numeric(df["Effect Upper"], errors="coerce")
        df["95 CI"] = ub_col - lb_col
        eff_col = pd.to_numeric(df["Absolute Effect"], errors="coerce") if "Absolute Effect" in df.columns else pd.Series(dtype=float)
        for idx in range(len(df)):
            est = eff_col.iloc[idx] if idx < len(eff_col) else np.nan
            lb = lb_col.iloc[idx] if idx < len(lb_col) else np.nan
            ub = ub_col.iloc[idx] if idx < len(ub_col) else np.nan
            w = ub - lb if np.isfinite(lb) and np.isfinite(ub) else np.nan
            cloud = df.loc[df.index[idx], "Cloud"] if "Cloud" in df.columns else "?"
            valid = np.isfinite(est) and np.isfinite(lb) and np.isfinite(ub) and lb <= ub
            print(
                f"  TROP CSV {safe_est} ({cloud}): cumulative est={round(est) if np.isfinite(est) else 'nan'}, "
                f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                f"95_CI_width={round(w) if np.isfinite(w) else 'nan'}, bounds_ok={valid} (diagnostics=cumulative)"
            )

    # TimeSeriesKfold: validate and log when direct cumulative TSK fields are used
    is_tsk = inference_display == "TimeSeriesKfold"
    if is_tsk and "Absolute Effect" in df.columns:
        eff_col = pd.to_numeric(df["Absolute Effect"], errors="coerce")
        lb_col = pd.to_numeric(df["Effect Lower"], errors="coerce") if "Effect Lower" in df.columns else pd.Series(dtype=float)
        ub_col = pd.to_numeric(df["Effect Upper"], errors="coerce") if "Effect Upper" in df.columns else pd.Series(dtype=float)
        for idx in range(len(df)):
            est = eff_col.iloc[idx] if idx < len(eff_col) else np.nan
            lb = lb_col.iloc[idx] if "Effect Lower" in df.columns and idx < len(lb_col) else np.nan
            ub = ub_col.iloc[idx] if "Effect Upper" in df.columns and idx < len(ub_col) else np.nan
            valid = np.isfinite(lb) and np.isfinite(ub) and lb <= est <= ub
            cloud = df.loc[df.index[idx], "Cloud"] if "Cloud" in df.columns else "?"
            scale = "cumulative_tsk_direct" if ("Effect Lower" in df.columns and "Effect Upper" in df.columns) else "weekly_sum_fallback"
            print(f"  TSK CSV {safe_est} ({cloud}): est={round(est) if np.isfinite(est) else 'nan'}, "
                  f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                  f"lb<=est<=ub={valid}, scale={scale}")

    # BlockResidualBootstrap: validate and log when direct cumulative BRB fields are used
    global _BRB_DIRECT_COUNT, _BRB_FALLBACK_COUNT
    is_brb = inference_display == "BlockResidualBootstrap"
    if is_brb and "Absolute Effect" in df.columns:
        eff_col = pd.to_numeric(df["Absolute Effect"], errors="coerce")
        lb_col = pd.to_numeric(df["Effect Lower"], errors="coerce") if "Effect Lower" in df.columns else pd.Series(dtype=float)
        ub_col = pd.to_numeric(df["Effect Upper"], errors="coerce") if "Effect Upper" in df.columns else pd.Series(dtype=float)
        scale = "cumulative_brb_direct" if ("Effect Lower" in df.columns and "Effect Upper" in df.columns) else "weekly_sum_fallback"
        for idx in range(len(df)):
            est = eff_col.iloc[idx] if idx < len(eff_col) else np.nan
            lb = lb_col.iloc[idx] if "Effect Lower" in df.columns and idx < len(lb_col) else np.nan
            ub = ub_col.iloc[idx] if "Effect Upper" in df.columns and idx < len(ub_col) else np.nan
            valid = np.isfinite(lb) and np.isfinite(ub) and lb <= est <= ub
            cloud = df.loc[df.index[idx], "Cloud"] if "Cloud" in df.columns else "?"
            if scale == "cumulative_brb_direct":
                _BRB_DIRECT_COUNT += 1
            else:
                _BRB_FALLBACK_COUNT += 1
            blk = df.loc[df.index[idx], "BRB block_length"] if "BRB block_length" in df.columns else None
            bstd = df.loc[df.index[idx], "BRB bootstrap_std"] if "BRB bootstrap_std" in df.columns else None
            rps = df.loc[df.index[idx], "BRB residual_pool_size"] if "BRB residual_pool_size" in df.columns else None
            label = f"{safe_est}-BRB"
            print(f"  BRB validate {label}: est={round(est) if np.isfinite(est) else 'nan'}, lb={round(lb) if np.isfinite(lb) else 'nan'}, "
                  f"ub={round(ub) if np.isfinite(ub) else 'nan'}, inv_ok={valid}, src={scale}, "
                  f"block_length={blk}, boot_std={bstd}, residual_pool_size={rps}")

        # Add BRB trust diagnostics to df for CSV export
        if "BRB residual_pool_size" in df.columns and "BRB block_length" in df.columns:
            pool_col = pd.to_numeric(df["BRB residual_pool_size"], errors="coerce")
            blk_col = pd.to_numeric(df["BRB block_length"], errors="coerce")
            bstd_col = pd.to_numeric(df["BRB bootstrap_std"], errors="coerce") if "BRB bootstrap_std" in df.columns else pd.Series(dtype=float)
            eff_col = pd.to_numeric(df["Absolute Effect"], errors="coerce") if "Absolute Effect" in df.columns else pd.Series(dtype=float)
            lb_col = pd.to_numeric(df["Effect Lower"], errors="coerce") if "Effect Lower" in df.columns else pd.Series(dtype=float)
            ub_col = pd.to_numeric(df["Effect Upper"], errors="coerce") if "Effect Upper" in df.columns else pd.Series(dtype=float)
            ci_width_col = ub_col - lb_col
            csv_cols_to_add = ["residual_pool_to_block_ratio", "brb_valid_flag", "brb_diagnostic_status"]
            for c in csv_cols_to_add:
                if f"BRB {c}" not in df.columns:
                    df[f"BRB {c}"] = np.nan
            for idx in range(len(df)):
                pool = pool_col.iloc[idx] if idx < len(pool_col) else None
                blk = blk_col.iloc[idx] if idx < len(blk_col) else None
                bstd_val = bstd_col.iloc[idx] if idx < len(bstd_col) else None
                eff = float(eff_col.iloc[idx]) if idx < len(eff_col) and np.isfinite(eff_col.iloc[idx]) else 0.0
                cw = ci_width_col.iloc[idx] if idx < len(ci_width_col) else None
                pool = int(pool) if pool is not None and np.isfinite(pool) else None
                blk = int(blk) if blk is not None and np.isfinite(blk) else None
                bstd_val = float(bstd_val) if bstd_val is not None and np.isfinite(bstd_val) else None
                cw = float(cw) if cw is not None and np.isfinite(cw) else None
                rec = {}
                _compute_brb_trust_diagnostics(rec, pool, blk, bstd_val, eff, cw)
                for c in csv_cols_to_add:
                    df.loc[df.index[idx], f"BRB {c}"] = rec.get(c)

    # Placebo: enforce lower <= upper and validate each row (all must be cumulative total effect scale)
    if inference_display == "Placebo" and "Absolute Effect" in df.columns:
        eff_col = pd.to_numeric(df["Absolute Effect"], errors="coerce")
        lb_col = pd.to_numeric(df["Effect Lower"], errors="coerce") if "Effect Lower" in df.columns else pd.Series(dtype=float)
        ub_col = pd.to_numeric(df["Effect Upper"], errors="coerce") if "Effect Upper" in df.columns else pd.Series(dtype=float)
        for idx in range(len(df)):
            est = eff_col.iloc[idx] if idx < len(eff_col) else np.nan
            lb = lb_col.iloc[idx] if "Effect Lower" in df.columns and idx < len(lb_col) else np.nan
            ub = ub_col.iloc[idx] if "Effect Upper" in df.columns and idx < len(ub_col) else np.nan
            if np.isfinite(lb) and np.isfinite(ub) and lb > ub:
                df.loc[df.index[idx], "Effect Lower"] = ub
                df.loc[df.index[idx], "Effect Upper"] = lb
                lb, ub = ub, lb
            valid = np.isfinite(est) and np.isfinite(lb) and np.isfinite(ub) and lb <= est <= ub
            cloud = df.loc[df.index[idx], "Cloud"] if "Cloud" in df.columns else "?"
            est_src = "csv_cumulative"
            bnd_src = "derived_95ci" if derived_bounds else "effect_ci_inversion"
            print(f"  Placebo CSV {safe_est} ({cloud}): est={round(est) if np.isfinite(est) else 'nan'}, "
                  f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                  f"lb<=est<=ub={valid}, est_src={est_src}, bnd_src={bnd_src} (scale=cumulative)")

    existing = [c for c in csv_columns if c in df.columns]
    if existing:
        csv_path = os.path.join(base_dir, f"{safe_inf}_{safe_est}_summary_stats_df.csv")
        df[existing].to_csv(csv_path, index=False)
        print(f"  Saved: {csv_path}")
    else:
        print(f"  Skipped CSV (none of {csv_columns} in summary_stats_df)")


# BRB trust diagnostic thresholds (auditable)
_DEGENERATE_BOOTSTRAP_STD_THRESHOLD = 1e-8
_DEGENERATE_CI_WIDTH_THRESHOLD = 1e-8
_LOW_RESIDUAL_POOL_THRESHOLD_MULTIPLIER = 3
_RELATIVE_EFFECT_EPS = 1e-10
_BRB_KFOLD_TIGHTNESS_THRESHOLD = 0.25


def _compute_brb_trust_diagnostics(
    record: dict,
    pool: Optional[int],
    block_len: Optional[int],
    boot_std: Optional[float],
    effect: float,
    ci_width_abs: Optional[float],
) -> None:
    """Augment record in-place with BRB trust diagnostics. Keeps all existing fields."""
    eps = _RELATIVE_EFFECT_EPS
    abs_effect = max(abs(effect), eps)

    # Store thresholds used
    record["degenerate_bootstrap_std_threshold"] = _DEGENERATE_BOOTSTRAP_STD_THRESHOLD
    record["degenerate_ci_width_threshold"] = _DEGENERATE_CI_WIDTH_THRESHOLD
    record["low_residual_pool_threshold_multiplier"] = _LOW_RESIDUAL_POOL_THRESHOLD_MULTIPLIER
    record["relative_effect_eps"] = _RELATIVE_EFFECT_EPS
    record["brb_kfold_tightness_threshold"] = _BRB_KFOLD_TIGHTNESS_THRESHOLD

    # Core BRB trust diagnostics
    if pool is not None and block_len is not None and block_len > 0:
        record["residual_pool_to_block_ratio"] = pool / block_len
        record["effective_block_count"] = pool / block_len
    else:
        record["residual_pool_to_block_ratio"] = None
        record["effective_block_count"] = None

    if boot_std is not None:
        record["bootstrap_std_relative_to_abs_effect"] = boot_std / abs_effect
    else:
        record["bootstrap_std_relative_to_abs_effect"] = None

    if ci_width_abs is not None:
        record["bootstrap_ci_width_relative_to_abs_effect"] = ci_width_abs / abs_effect
        record["bootstrap_ci_width_absolute"] = ci_width_abs
    else:
        record["bootstrap_ci_width_relative_to_abs_effect"] = None
        record["bootstrap_ci_width_absolute"] = None

    # Degeneracy flags
    degenerate_std = boot_std is not None and boot_std < _DEGENERATE_BOOTSTRAP_STD_THRESHOLD
    degenerate_ci = ci_width_abs is not None and ci_width_abs < _DEGENERATE_CI_WIDTH_THRESHOLD
    low_pool = (
        pool is not None
        and block_len is not None
        and pool < _LOW_RESIDUAL_POOL_THRESHOLD_MULTIPLIER * block_len
    )
    low_effect = abs(effect) < eps

    record["degenerate_bootstrap_std_flag"] = degenerate_std
    record["degenerate_ci_width_flag"] = degenerate_ci
    record["low_residual_pool_flag"] = low_pool
    record["low_effect_signal_flag"] = low_effect

    # Summary status
    warnings_list = []
    if low_pool:
        warnings_list.append("low_residual_pool")
    if degenerate_std:
        warnings_list.append("degenerate_bootstrap_std")
    if degenerate_ci:
        warnings_list.append("degenerate_ci_width")
    if low_effect:
        warnings_list.append("low_effect_signal")

    if len(warnings_list) == 0:
        record["brb_diagnostic_status"] = "ok"
    elif len(warnings_list) == 1:
        record["brb_diagnostic_status"] = warnings_list[0]
    else:
        record["brb_diagnostic_status"] = "multiple_warnings"

    # Validity flag and reason
    invalid_reasons = []
    if low_pool:
        invalid_reasons.append("low_residual_pool")
    if degenerate_std:
        invalid_reasons.append("degenerate_bootstrap_std")
    if degenerate_ci:
        invalid_reasons.append("degenerate_ci_width")

    if invalid_reasons:
        record["brb_valid_flag"] = False
        record["brb_validity_reason"] = "; ".join(invalid_reasons)
    else:
        record["brb_valid_flag"] = True
        record["brb_validity_reason"] = "ok"


def _get_kfold_or_placebo_row(
    base_dir: str,
    estimator_display: str,
    inference_for_csv: str,
    dataset: str,
    test_group: str,
) -> dict | None:
    """Load CSV for Kfold/Placebo/TimeSeriesKfold and return matching row. Returns None if not found."""
    safe_est = estimator_display.replace("/", "_")
    safe_inf = inference_for_csv.replace("/", "_")
    csv_path = os.path.join(base_dir, f"{safe_inf}_{safe_est}_summary_stats_df.csv")
    if not os.path.isfile(csv_path):
        return None
    try:
        df = pd.read_csv(csv_path)
        if "Cloud" not in df.columns or "Test_Group" not in df.columns:
            return None
        mask = (df["Cloud"].astype(str) == str(dataset)) & (df["Test_Group"].astype(str) == str(test_group))
        if not mask.any():
            return None
        row = df.loc[mask].iloc[0].to_dict()
        return row
    except Exception:
        return None


def _save_brb_diagnostics(
    mmt: Any,
    estimator_display: str,
    inference_display: str,
    base_dir: str,
) -> None:
    """Append BlockResidualBootstrap diagnostics to brb_diagnostics.jsonl. One record per dataset x estimator.
    Reads from mmt._brb_diagnostics (populated by notebook's _process_aggregation when inference is BlockResidualBootstrap).
    Adds trust diagnostics (residual richness, degeneracy flags, validity) and KFold/Placebo comparisons when available.
    Does not modify summary CSV; failures do not stop the grid run."""
    if inference_display != "BlockResidualBootstrap":
        return
    brb_list = getattr(mmt, "_brb_diagnostics", None)
    if not brb_list:
        return
    diagnostics_path = os.path.join(base_dir, "brb_diagnostics.jsonl")
    try:
        os.makedirs(base_dir, exist_ok=True)
        for rec in brb_list:
            brb = rec.get("brb_stats") or {}
            dataset = rec.get("dataset", "")
            test_group = rec.get("test_group", "")
            est = brb.get("effect_cumulative_brb")
            lb = brb.get("effect_ci_lower_cumulative_brb")
            ub = brb.get("effect_ci_upper_cumulative_brb")
            ci_width = (float(ub) - float(lb)) if (lb is not None and ub is not None and np.isfinite(lb) and np.isfinite(ub)) else None
            boot_std = brb.get("bootstrap_std_conditional") or brb.get("bootstrap_std_refit") or brb.get("bootstrap_cumulative_std")
            effect = float(est) if est is not None and np.isfinite(est) else 0.0
            pool = brb.get("residual_pool_size")
            block_len = brb.get("block_length")

            record = {
                "estimator": estimator_display,
                "inference": inference_display,
                "dataset": dataset,
                "test_group": test_group,
                "estimate": float(est) if est is not None and np.isfinite(est) else None,
                "lower_bound": float(lb) if lb is not None and np.isfinite(lb) else None,
                "upper_bound": float(ub) if ub is not None and np.isfinite(ub) else None,
                "ci_width": float(ci_width) if ci_width is not None and np.isfinite(ci_width) else None,
                "ci_method": brb.get("ci_method"),
                "bootstrap_type": brb.get("bootstrap_type"),
                "refit_in_bootstrap": brb.get("refit_in_bootstrap"),
                "refit_mode": brb.get("refit_mode"),
                "pre_bootstrap_enabled": brb.get("pre_bootstrap_enabled"),
                "pre_bootstrap_length": brb.get("pre_bootstrap_length"),
                "pre_bootstrap_successful_draws": brb.get("pre_bootstrap_successful_draws"),
                "pre_bootstrap_failed_draws": brb.get("pre_bootstrap_failed_draws"),
                "block_length": block_len,
                "min_train_periods": brb.get("min_train_periods"),
                "residual_pool_size": pool,
                "bootstrap_n_series": brb.get("bootstrap_n_series"),
                "bootstrap_cumulative_mean": brb.get("bootstrap_cumulative_mean"),
                "bootstrap_cumulative_std": boot_std,
                "bootstrap_cumulative_min": brb.get("bootstrap_cumulative_min"),
                "bootstrap_cumulative_max": brb.get("bootstrap_cumulative_max"),
                "bootstrap_skew": brb.get("bootstrap_skew"),
                "bootstrap_kurtosis": brb.get("bootstrap_kurtosis"),
                "bootstrap_quantile_10": brb.get("bootstrap_quantile_10"),
                "bootstrap_quantile_90": brb.get("bootstrap_quantile_90"),
                "bootstrap_failed_draws": brb.get("bootstrap_failed_draws"),
                "bootstrap_successful_draws": brb.get("bootstrap_successful_draws"),
                "bootstrap_failure_rate": brb.get("bootstrap_failure_rate"),
                "bootstrap_failure_warning": brb.get("bootstrap_failure_warning"),
                "bootstrap_std_conditional": brb.get("bootstrap_std_conditional"),
                "bootstrap_std_refit": brb.get("bootstrap_std_refit"),
                "estimator_variance_fraction": brb.get("estimator_variance_fraction"),
                "bca_bias_correction": brb.get("bca_bias_correction"),
                "bca_acceleration": brb.get("bca_acceleration"),
            }

            # Add trust diagnostics
            _compute_brb_trust_diagnostics(
                record, pool, block_len, boot_std, effect, ci_width
            )

            # KFold comparison (try Kfold then TimeSeriesKfold)
            kfold_row = _get_kfold_or_placebo_row(base_dir, estimator_display, "Kfold", dataset, test_group)
            if kfold_row is None:
                kfold_row = _get_kfold_or_placebo_row(base_dir, estimator_display, "TimeSeriesKfold", dataset, test_group)
            if kfold_row is not None and record.get("ci_width") is not None:
                kf_eff = kfold_row.get("Absolute Effect")
                kf_ci = kfold_row.get("95 CI")
                if kf_eff is not None and kf_ci is not None:
                    kf_eff = pd.to_numeric(kf_eff, errors="coerce")
                    kf_ci = pd.to_numeric(kf_ci, errors="coerce")
                    if np.isfinite(kf_ci) and kf_ci > 0:
                        record["brb_to_kfold_ci_width_ratio"] = record["ci_width"] / float(kf_ci)
                        record["brb_suspiciously_tighter_than_kfold_flag"] = record["brb_to_kfold_ci_width_ratio"] < _BRB_KFOLD_TIGHTNESS_THRESHOLD
                    else:
                        record["brb_to_kfold_ci_width_ratio"] = None
                        record["brb_suspiciously_tighter_than_kfold_flag"] = None
                    if np.isfinite(kf_eff):
                        abs_kf = max(abs(float(kf_eff)), _RELATIVE_EFFECT_EPS)
                        record["brb_to_kfold_abs_estimate_ratio"] = abs(effect) / abs_kf
                    else:
                        record["brb_to_kfold_abs_estimate_ratio"] = None
                    brb_sign = 1 if effect > 0 else (-1 if effect < 0 else 0)
                    kf_sign = 1 if float(kf_eff) > 0 else (-1 if float(kf_eff) < 0 else 0)
                    record["brb_kfold_sign_match"] = brb_sign == kf_sign
                else:
                    record["brb_to_kfold_ci_width_ratio"] = None
                    record["brb_to_kfold_abs_estimate_ratio"] = None
                    record["brb_kfold_sign_match"] = None
                    record["brb_suspiciously_tighter_than_kfold_flag"] = None
            else:
                record["brb_to_kfold_ci_width_ratio"] = None
                record["brb_to_kfold_abs_estimate_ratio"] = None
                record["brb_kfold_sign_match"] = None
                record["brb_suspiciously_tighter_than_kfold_flag"] = None

            # Placebo comparison
            placebo_row = _get_kfold_or_placebo_row(base_dir, estimator_display, "Placebo", dataset, test_group)
            if placebo_row is not None and record.get("ci_width") is not None:
                pl_eff = placebo_row.get("Absolute Effect")
                pl_ci = placebo_row.get("95 CI")
                if pl_eff is not None and pl_ci is not None:
                    pl_eff = pd.to_numeric(pl_eff, errors="coerce")
                    pl_ci = pd.to_numeric(pl_ci, errors="coerce")
                    if np.isfinite(pl_ci) and pl_ci > 0:
                        record["brb_to_placebo_ci_width_ratio"] = record["ci_width"] / float(pl_ci)
                    else:
                        record["brb_to_placebo_ci_width_ratio"] = None
                    if np.isfinite(pl_eff):
                        abs_pl = max(abs(float(pl_eff)), _RELATIVE_EFFECT_EPS)
                        record["brb_to_placebo_abs_estimate_ratio"] = abs(effect) / abs_pl
                    else:
                        record["brb_to_placebo_abs_estimate_ratio"] = None
                    brb_sign = 1 if effect > 0 else (-1 if effect < 0 else 0)
                    pl_sign = 1 if float(pl_eff) > 0 else (-1 if float(pl_eff) < 0 else 0)
                    record["brb_placebo_sign_match"] = brb_sign == pl_sign
                else:
                    record["brb_to_placebo_ci_width_ratio"] = None
                    record["brb_to_placebo_abs_estimate_ratio"] = None
                    record["brb_placebo_sign_match"] = None
            else:
                record["brb_to_placebo_ci_width_ratio"] = None
                record["brb_to_placebo_abs_estimate_ratio"] = None
                record["brb_placebo_sign_match"] = None

            # Only omit fields that are truly unavailable (None); keep False, 0, etc.
            record = {k: v for k, v in record.items() if v is not None or k in (
                "estimate", "lower_bound", "upper_bound", "ci_width",
                "bca_bias_correction", "bca_acceleration", "bootstrap_std_refit", "estimator_variance_fraction",
                "degenerate_bootstrap_std_flag", "degenerate_ci_width_flag", "low_residual_pool_flag",
                "low_effect_signal_flag", "brb_valid_flag",
            )}
            with open(diagnostics_path, "a") as f:
                f.write(json.dumps(record, default=str) + "\n")
            print(f"  BRB diagnostics saved for {estimator_display}-{dataset}")
    except Exception as e:
        warnings.warn(f"BRB diagnostics write failed: {e}", UserWarning)


def _save_mmt_config(mmt: Any, base_dir: str) -> None:
    """Save mmt config (kpi, kpi_to_input_path, datasets, test/control geos, start/end dates) for plot script.
    Set mmt.kpi_to_input_path = {"DME_CONVERSIONS": "us_conversions_l12m.pkl"} before running to enable path lookup when mmt_datasets.pkl is missing."""
    try:
        os.makedirs(base_dir, exist_ok=True)
        import json
        kpi = getattr(mmt.config, "kpi", None)
        datasets = getattr(mmt.config, "datasets", None)
        if RUN_ONLY_DATASETS is not None and isinstance(kpi, dict) and isinstance(datasets, dict):
            allowed = set(RUN_ONLY_DATASETS)
            kpi = {k: v for k, v in kpi.items() if k in allowed}
            datasets = {k: v for k, v in datasets.items() if k in allowed}
        cfg = {
            "kpi": kpi,
            "kpi_to_input_path": getattr(mmt.config, "kpi_to_input_path", None) or getattr(mmt, "kpi_to_input_path", None),
            "test_start_dates": getattr(mmt.config, "test_start_dates", {}),
            "test_end_dates": getattr(mmt.config, "test_end_dates", {}),
            "test_groups": getattr(mmt.config, "test_groups", {}),
            "control_groups": getattr(mmt.config, "control_groups", {}),
            "exclude_date_ranges": EXCLUDE_DATE_RANGES if EXCLUDE_DATE_RANGES else None,
        }
        cfg = {k: v for k, v in cfg.items() if v is not None and v != {} and v != []}
        if cfg:
            path = os.path.join(base_dir, "mmt_config.json")
            with open(path, "w") as f:
                json.dump(cfg, f, indent=2, default=str)
            print(f"  Saved: {path}")
        if datasets and isinstance(datasets, dict):
            ds_path = os.path.join(base_dir, "mmt_datasets.pkl")
            with open(ds_path, "wb") as f:
                pickle.dump(datasets, f, pickle.HIGHEST_PROTOCOL)
            print(f"  Saved: {ds_path}")
    except Exception:
        pass


def run_grid() -> None:
    """Run MMT for each (estimator, inference) combination and save results."""
    # When run via %run from Jupyter, script's globals may be the script's own namespace.
    # Notebook variables (mmt, MMTAnalysis) live in the IPython user namespace.
    mmt = None
    MMTAnalysis = None
    try:
        ip = get_ipython()  # type: ignore[name-defined]
        if ip is not None:
            user_ns = ip.user_ns
            mmt = user_ns.get("mmt")
            MMTAnalysis = user_ns.get("MMTAnalysis")
    except Exception:
        pass
    if mmt is None or MMTAnalysis is None:
        # Fallback: try script globals and locals (in case %run shares namespace)
        for g in (globals(), locals()):
            if mmt is None:
                mmt = g.get("mmt")
            if MMTAnalysis is None:
                MMTAnalysis = g.get("MMTAnalysis")
    if mmt is None or MMTAnalysis is None:
        print("mmt and MMTAnalysis not found.")
        print("")
        print("This script must run inside the notebook (it needs your existing mmt and MMTAnalysis).")
        print("")
        print("How to run:")
        print(f"  1. Open the readout notebook: {READOUT_NOTEBOOK_PATH}")
        print("  2. Run all cells up to and including the one that creates mmt (mmt = MMTAnalysis(...)).")
        print("  3. In a new cell, run:")
        print("       %run run_mmt_estimator_inference_grid.py")
        print("     or use the full path to the script if needed.")
        print("")
        print("Do not use 'Run Python File' / F5 in the editor — that runs in a separate process without mmt.")
        return

    global _BRB_DIRECT_COUNT, _BRB_FALLBACK_COUNT
    _BRB_DIRECT_COUNT = 0
    _BRB_FALLBACK_COUNT = 0
    # Apply date exclusions before any estimator runs (sensitivity checks, e.g. shock weeks)
    if EXCLUDE_DATE_RANGES:
        datasets = getattr(mmt.config, "datasets", None)
        if datasets and isinstance(datasets, dict):
            for name, df in list(datasets.items()):
                if isinstance(df, pd.DataFrame):
                    n_before = len(df)
                    filtered = _apply_date_exclusions(df, EXCLUDE_DATE_RANGES, date_col="date")
                    n_removed = n_before - len(filtered)
                    mmt.config.datasets[name] = filtered
                    print(f"[DATE EXCLUDE] {name}: removed {n_removed} rows across {len(EXCLUDE_DATE_RANGES)} date range(s)")
                else:
                    print(f"[DATE EXCLUDE] {name}: removed 0 rows")
        else:
            print("[DATE EXCLUDE] No datasets to filter")
    _run_and_save_counterfactual_stability_tests(mmt, BASE_OUTPUT_DIR)
    _save_mmt_config(mmt, BASE_OUTPUT_DIR)
    base_kwargs = _get_mmt_kwargs(mmt)
    n = len(COMBINATIONS)
    # Suppress sklearn "fitted without feature names" warning (noise when running grid)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X has feature names, but.*was fitted without feature names",
            category=UserWarning,
            module="sklearn",
        )
        if RUN_ONLY_INDICES is not None:
            combinations_to_run = [COMBINATIONS[i] for i in RUN_ONLY_INDICES]
            n = len(combinations_to_run)
            start_offset = 0
        else:
            end = END_AT_INDEX if END_AT_INDEX is not None else len(COMBINATIONS)
            combinations_to_run = COMBINATIONS[START_FROM_INDEX:end]
            if RUN_BRB_ONLY:
                combinations_to_run = [
                    c for c in combinations_to_run
                    if c[1] == "BlockResidualBootstrap"
                    and c[0] in ("TBR", "TBRRidge", "AugSynthCVXPY", "SyntheticControlCVXPY")
                ]
            n = len(combinations_to_run)
            start_offset = 0
        # TBR + Placebo excluded: TBR requires aggregated control (1 unit), placebo-in-space needs >=5
        combinations_to_run = [c for c in combinations_to_run if not (c[0] == "TBR" and c[1] == "Placebo")]
        n = len(combinations_to_run)
        _run_grid_loop(mmt, MMTAnalysis, base_kwargs, combinations_to_run, n, start_offset)
    # BRB fallback rate summary
    total_brb = _BRB_DIRECT_COUNT + _BRB_FALLBACK_COUNT
    if total_brb > 0:
        pct_direct = 100.0 * _BRB_DIRECT_COUNT / total_brb
        print(f"\nBRB fallback summary: {_BRB_DIRECT_COUNT} cumulative_brb_direct, {_BRB_FALLBACK_COUNT} weekly_sum_fallback "
              f"({pct_direct:.0f}% direct). Expect almost all on direct.")
    print("\nGrid run finished.")
    _run_post_hoc_diagnostics(BASE_OUTPUT_DIR)


# BRB fallback tracking: cumulative_brb_direct vs weekly_sum_fallback
_BRB_DIRECT_COUNT = 0
_BRB_FALLBACK_COUNT = 0
_BRB_MODULE_PATHS_PRINTED = False


def _run_grid_loop(
    mmt: Any, MMTAnalysis: type, base_kwargs: dict, combinations: list, n: int, start_offset: int = 0
) -> None:
    """Inner loop so warnings filter wraps all runs."""
    global _BRB_MODULE_PATHS_PRINTED
    for idx, (estimator_key, inference_value, inference_display, estimator_display) in enumerate(combinations):
        i = start_offset + idx + 1
        print(f"\n[{i}/{n}] {estimator_display} + {inference_display}")
        # Print BRB/impact module paths once to confirm upstream (not stale local copy)
        if inference_display == "BlockResidualBootstrap" and not _BRB_MODULE_PATHS_PRINTED:
            try:
                import panel_exp.inference.block_residual_bootstrap as _brb_mod
                import panel_exp.impact as _impact_mod
                print(f"  [BRB] block_residual_bootstrap: {getattr(_brb_mod, '__file__', '?')}")
                print(f"  [BRB] impact: {getattr(_impact_mod, '__file__', '?')}")
                _BRB_MODULE_PATHS_PRINTED = True
            except Exception as ex:
                print(f"  [BRB] Could not resolve module paths: {ex}")
        kwargs = {**base_kwargs, "model_selection": estimator_key}
        # TBR (and similar) require control/treated to be pre-aggregated
        if estimator_key in ESTIMATORS_REQUIRING_AGGREGATION:
            kwargs["panel_aggregation_config"] = "yes"
        elif estimator_key in ESTIMATORS_AGGREGATE_TREATED_ONLY:
            kwargs["panel_aggregation_config"] = "no"
        elif estimator_key in ESTIMATORS_REQUIRING_AGGREGATION_NONE:
            kwargs["panel_aggregation_config"] = "none"
        elif (estimator_key in ESTIMATORS_BRB_UNAGGREGATED_TREATED
              and inference_value == "BlockResidualBootstrap"):
            # AugSynthCVXPY / SyntheticControlCVXPY + BRB: unaggregated treated; residuals at unit level, aggregate after bootstrap
            kwargs["panel_aggregation_config"] = "none"
        if inference_value is not None:
            kwargs["inference"] = inference_value
        else:
            # BayesianTBR, BayesianTBRHorseShoe: use own posterior (MCMC per dataset), not Kfold
            kwargs["inference"] = "Bayesian"
        kwargs["skip_pre_test_r2"] = False  # skip slow forward OOS R² when running grid
        # BRB options: always pass to MMTAnalysis; MMTAnalysis forwards to model.run_analysis
        if inference_value == "BlockResidualBootstrap":
            kwargs["refit_in_bootstrap"] = REFIT_IN_BOOTSTRAP
            kwargs["refit_mode"] = BRB_REFIT_MODE
            kwargs["ci_method"] = BRB_CI_METHOD
            kwargs["bootstrap_type"] = BRB_BOOTSTRAP_TYPE
            kwargs["block_length"] = BRB_BLOCK_LENGTH
        # TSKFold: save per-fold diagnostics alongside regular output
        _tsk_diagnostics_path = None
        if inference_value == "TimeSeriesKfold":
            _tsk_diag_name = f"TimeSeriesKFold_{estimator_display}_fold_diagnostics.csv"
            _tsk_diagnostics_path = Path(BASE_OUTPUT_DIR) / _tsk_diag_name
        try:
            mmt_i = MMTAnalysis(**kwargs)
            # So DID diagnostics can be saved next to the pickle (see NOTE_DID_diagnostics_in_MMT.md)
            mmt_i.base_output_dir = BASE_OUTPUT_DIR
            # TSKFold diagnostics path: set as attribute so impact.py reads it during run_analysis
            if _tsk_diagnostics_path is not None:
                mmt_i.tsk_diagnostics_path = _tsk_diagnostics_path
            summary_stats_df, weekly_trends_dct = mmt_i.run()
            _validate_weekly_effect_consistency(
                weekly_trends_dct, estimator_display, getattr(mmt_i, "config", None)
            )
            _validate_att_consistency(
                weekly_trends_dct,
                summary_stats_df,
                estimator_display,
                getattr(mmt_i, "config", None),
            )
            _save_results(
                weekly_trends_dct,
                summary_stats_df,
                inference_display,
                estimator_display,
                BASE_OUTPUT_DIR,
                CSV_COLUMNS,
                config=getattr(mmt_i, "config", None),
            )
            _save_brb_diagnostics(
                mmt_i,
                estimator_display,
                inference_display,
                BASE_OUTPUT_DIR,
            )
            print(f"  OK: {estimator_display} + {inference_display}")
        except Exception as e:
            print(f"  FAILED: {e}")
            traceback.print_exc()
            continue


# ---------------------------------------------------------------------------
# Post-hoc diagnostics summary
# ---------------------------------------------------------------------------

def _parse_float(val) -> Optional[float]:
    """Safely coerce a value to float; return None on failure."""
    if val is None:
        return None
    try:
        v = float(val)
        return None if not np.isfinite(v) else v
    except (TypeError, ValueError):
        return None


def _get_test_start_date(base_dir: Path) -> Optional[pd.Timestamp]:
    """Read test_start_dates from mmt_config.json in base_dir."""
    cfg_path = base_dir / "mmt_config.json"
    if not cfg_path.exists():
        return None
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
        dates = cfg.get("test_start_dates", {})
        if dates:
            return pd.Timestamp(next(iter(dates.values())))
    except Exception:
        pass
    return None


def _run_post_hoc_diagnostics(base_dir: str) -> None:
    """
    Load all saved results and compute cross-estimator diagnostics summary.

    Diagnostics computed per estimator+inference combination:
      1. Stat sig            — CI excludes 0
      2. Weekly ATT stability — CV of post-period weekly effects; flag if CV > 1.5 (outlier-driven)
      3. Pre-period placebo   — mean pre-period residual vs post-period effect; flag if ratio > 0.3
      4. Noise floor check    — |effect| / TSKFold fold-5 RMSE; flag if ratio < 2
      5. Inference agreement  — within estimator, do all inference methods agree on stat sig?
      6. Cross-estimator direction — do all estimators agree on effect sign?
      7. Overall flag         — composite diagnostic verdict

    Output: {base_dir}/estimator_diagnostics_summary.csv
    """
    base = Path(base_dir)

    # Map filename stem → (estimator_display, inference_display) from active COMBINATIONS
    combo_map: dict[str, tuple[str, str]] = {}
    for (_, _, inference_display, estimator_display) in COMBINATIONS:
        safe_inf = inference_display.replace("/", "_")
        safe_est = estimator_display.replace("/", "_")
        combo_map[f"{safe_inf}_{safe_est}"] = (estimator_display, inference_display)

    # TSKFold fold-5 metrics (noise floor + extrapolation validity) keyed by estimator_display
    tsk_noise_floor: dict[str, float] = {}
    tsk_fold5_valid: dict[str, bool] = {}   # False if fold-5 fails stable_flag or centered_flag
    for tsk_path in base.glob("TimeSeriesKFold_*_fold_diagnostics.csv"):
        try:
            est_name = tsk_path.stem.replace("TimeSeriesKFold_", "").replace("_fold_diagnostics", "")
            tsk_df = pd.read_csv(tsk_path)
            fold5 = tsk_df[tsk_df["fold_id"] == tsk_df["fold_id"].max()]
            if not fold5.empty:
                if "holdout_rmse" in fold5.columns:
                    tsk_noise_floor[est_name] = float(fold5["holdout_rmse"].iloc[0])
                stable   = bool(fold5["stable_flag"].iloc[0])   if "stable_flag"   in fold5.columns else True
                centered = bool(fold5["centered_flag"].iloc[0]) if "centered_flag" in fold5.columns else True
                tsk_fold5_valid[est_name] = stable and centered
        except Exception:
            pass

    test_start = _get_test_start_date(base)

    rows = []
    for csv_path in sorted(base.glob("*_summary_stats_df.csv")):
        stem = csv_path.stem.replace("_summary_stats_df", "")
        if stem not in combo_map:
            continue
        estimator_display, inference_display = combo_map[stem]

        try:
            sdf = pd.read_csv(csv_path)
            if sdf.empty:
                continue
            r = sdf.iloc[0].to_dict()
        except Exception:
            continue

        effect    = _parse_float(r.get("Absolute Effect"))
        eff_lower = _parse_float(r.get("Effect Lower"))
        eff_upper = _parse_float(r.get("Effect Upper"))
        p_value   = _parse_float(r.get("p-value"))
        pre_r2    = _parse_float(r.get("Pre-test R² (forward OOS)"))

        stat_sig = False
        if eff_lower is not None and eff_upper is not None:
            stat_sig = (eff_lower > 0) or (eff_upper < 0)

        effect_direction = ("positive" if effect > 0 else "negative") if effect is not None else None

        # ---- Weekly trends analysis -------------------------------------------
        weekly_att_cv = None
        weekly_att_outlier_driven = None
        pre_resid_mean = None
        pre_resid_std  = None
        pre_period_contamination_flag = None

        pickle_path = base / f"{stem}_weekly_trends_dct.pickle"
        if pickle_path.exists():
            try:
                with open(pickle_path, "rb") as f:
                    wtd = pickle.load(f)
                for wdf in wtd.values():
                    if not isinstance(wdf, pd.DataFrame):
                        continue
                    if not all(c in wdf.columns for c in ("y", "y_hat", "dt")):
                        continue
                    wdf = wdf.copy()
                    wdf["dt"] = pd.to_datetime(wdf["dt"])
                    wdf["residual"] = wdf["y"] - wdf["y_hat"]

                    if test_start is not None:
                        post_mask = wdf["dt"] >= test_start
                        pre_mask  = wdf["dt"] < test_start
                    else:
                        mid = len(wdf) // 2
                        post_mask = pd.Series([False] * len(wdf), index=wdf.index)
                        post_mask.iloc[mid:] = True
                        pre_mask = ~post_mask

                    post_fx   = wdf.loc[post_mask, "residual"].dropna()
                    pre_resids = wdf.loc[pre_mask, "residual"].dropna()

                    if len(post_fx) > 1 and abs(post_fx.mean()) > 1e-6:
                        weekly_att_cv = float(post_fx.std() / abs(post_fx.mean()))
                        weekly_att_outlier_driven = weekly_att_cv > 1.5

                    if len(pre_resids) > 0:
                        pre_resid_mean = float(pre_resids.mean())
                        pre_resid_std  = float(pre_resids.std())
                        if effect is not None and abs(effect) > 1e-6:
                            pre_period_contamination_flag = (
                                abs(pre_resid_mean) / abs(effect)
                            ) > 0.3
                    break
            except Exception:
                pass

        # ---- Noise floor -------------------------------------------------------
        tsk_rmse = tsk_noise_floor.get(estimator_display)
        effect_to_noise_ratio = None
        detectable_above_noise = None
        if tsk_rmse is not None and tsk_rmse > 0 and effect is not None:
            effect_to_noise_ratio = abs(effect) / tsk_rmse
            detectable_above_noise = effect_to_noise_ratio > 2.0

        # TSKFold extrapolation validity for this estimator
        tsk_valid = tsk_fold5_valid.get(estimator_display, None)
        tsk_extrapolation_invalid = (
            inference_display == "TimeSeriesKfold" and tsk_valid is False
        )

        rows.append({
            "estimator":                    estimator_display,
            "inference":                    inference_display,
            "effect":                       effect,
            "effect_lower":                 eff_lower,
            "effect_upper":                 eff_upper,
            "stat_sig":                     stat_sig,
            "effect_direction":             effect_direction,
            "p_value":                      p_value,
            "pre_test_r2":                  pre_r2,
            "weekly_att_cv":                weekly_att_cv,
            "weekly_att_outlier_driven":    weekly_att_outlier_driven,
            "pre_period_residual_mean":     pre_resid_mean,
            "pre_period_residual_std":      pre_resid_std,
            "pre_period_contamination_flag":pre_period_contamination_flag,
            "tsk_fold5_rmse":               tsk_rmse,
            "tsk_fold5_valid":              tsk_valid,
            "tsk_extrapolation_invalid":    tsk_extrapolation_invalid,
            "effect_to_noise_ratio":        effect_to_noise_ratio,
            "detectable_above_noise":       detectable_above_noise,
        })

    if not rows:
        print("[DIAGNOSTICS] No results found — skipping.")
        return

    diag_df = pd.DataFrame(rows)

    # ---- Inference agreement within estimator ----------------------------------
    for estimator, grp in diag_df.groupby("estimator"):
        sig_vals = grp["stat_sig"].dropna()
        agrees   = len(sig_vals.unique()) <= 1
        diag_df.loc[diag_df["estimator"] == estimator, "inference_method_agreement"] = agrees

    # ---- Cross-estimator direction consistency ----------------------------------
    dirs = diag_df["effect_direction"].dropna().unique()
    direction_consistent = len(dirs) <= 1
    diag_df["cross_estimator_direction_consistent"] = direction_consistent
    diag_df["majority_effect_direction"] = (
        diag_df["effect_direction"].value_counts().index[0]
        if len(diag_df["effect_direction"].dropna()) > 0 else None
    )

    # ---- Overall diagnostic flag -----------------------------------------------
    def _flag(row) -> str:
        concerns = []
        if row.get("tsk_extrapolation_invalid"):
            concerns.append("TSK_EXTRAPOLATION_INVALID")
        if row.get("stat_sig") and not row.get("inference_method_agreement"):
            concerns.append("FRAGILE_INFERENCE")
        if row.get("stat_sig") and not row.get("cross_estimator_direction_consistent"):
            concerns.append("DIRECTION_INCONSISTENT")
        if row.get("weekly_att_outlier_driven"):
            concerns.append("OUTLIER_DRIVEN")
        if row.get("pre_period_contamination_flag"):
            concerns.append("PRE_PERIOD_CONTAMINATION")
        if row.get("detectable_above_noise") is False:
            concerns.append("BELOW_NOISE_FLOOR")
        if not concerns:
            return "PASS" if row.get("stat_sig") else "NOT_SIG"
        return "|".join(concerns)

    diag_df["diagnostic_flag"] = diag_df.apply(_flag, axis=1)

    # ---- Save ------------------------------------------------------------------
    out_path = base / "estimator_diagnostics_summary.csv"
    diag_df.to_csv(out_path, index=False)
    print(f"\n[DIAGNOSTICS] Summary saved: {out_path}")

    display_cols = [
        "estimator", "inference", "effect", "stat_sig",
        "tsk_extrapolation_invalid",
        "inference_method_agreement", "cross_estimator_direction_consistent",
        "detectable_above_noise", "weekly_att_outlier_driven",
        "pre_period_contamination_flag", "diagnostic_flag",
    ]
    print(diag_df[[c for c in display_cols if c in diag_df.columns]].to_string(index=False))


if __name__ == "__main__":
    run_grid()
