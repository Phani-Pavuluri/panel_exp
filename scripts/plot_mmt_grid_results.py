"""
Generate report visualizations from MMT grid output files.

Reads the pickle and CSV files produced by run_mmt_estimator_inference_grid.py
and creates:
  1. Distribution of Results (density + method lines + family summary table)
  2. Estimator Effects by Inference (one plot per inference: Y=estimators, X=effect, point + CI band)
  3. TBR Family Effects by Inference (one plot: Y=TBR family, X=effect, columns=inferences)
  4. DID Estimate (conceptual chart with counterfactual + estimate table)
  4. TBR Family of Estimators (time-series with CIs + table)
  5. SCM Family of Estimators (time-series with CIs + table)

Uses mmt_config.json (saved by the grid script) for: kpi, datasets, test/control geos,
test_start_dates, test_end_dates. Fallbacks: KPI_COL, DID_* constants.

Usage:
  python plot_mmt_grid_results.py
  python plot_mmt_grid_results.py --base-dir /path/to/sme_conversions  # infers SME_CONVERSIONS from path
  python plot_mmt_grid_results.py --base-dir /path/to/output --kpi-col SME_CONVERSIONS  # explicit when config has multiple datasets
  python plot_mmt_grid_results.py --exclude-inference UnitJackKnife  # exclude UnitJackKnife from all plots
"""

from __future__ import annotations

import argparse
import inspect
import warnings
import glob
import json
import os
import pickle
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Config (must match dir used by run_mmt_estimator_inference_grid.py)
# -----------------------------------------------------------------------------
# New DID upgrade outputs
BASE_OUTPUT_DIR = "/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v2"
ACTUAL_EFFECT_REFERENCE = None
# Number of weeks to keep prior to test start in family timeseries plots (TBR, SCM, inference). None = show all.
PRE_PERIOD_WEEKS: int | None = 20
# KPI column (value col in data). Single value = run for that KPI. List = run for all KPIs in list.
# Examples: ["DME_CONVERSIONS","DME_WEB_ORDERS"][1] → DME_WEB_ORDERS only
#           ["DME_CONVERSIONS","DME_WEB_ORDERS"]     → run for both
KPI_COL = ["DME_CONVERSIONS"]
FIGURES_DIR = None  # Set per KPI when running
# DMA GeoJSON for geo map. Community-hosted Nielsen DMA boundaries (simzou/nielsen-dma).
DMA_GEOJSON_URL = "https://raw.githubusercontent.com/simzou/nielsen-dma/master/nielsen-mkt-map_simplified.json"
# Long-format data path for DID. If None, uses mmt_config.kpi_to_input_path or mmt_datasets.pkl.
DID_INPUT_LONG_PATH = None
DID_TREATMENT_START_DATE = "2026-01-24"  # Fallback when mmt_config.json missing
DID_DIAGNOSTICS_PATH = None  # If None, script looks for {inference}_DID_did_diagnostics.json in BASE_OUTPUT_DIR

# Fallbacks when mmt_config.json is missing or incomplete
_MMT_CONFIG_CACHE: dict[str, dict] = {}
# Family groupings for distribution_family_summary.csv
FAMILY_ESTIMATORS = {
    "TBR Ridge": ["TBRRidge"],
    "AUG SCM": ["AugSynthCVXPY"],
}

# Estimators to exclude from distribution (known to produce extreme outliers when buggy)
ESTIMATORS_EXCLUDED_FROM_DISTRIBUTION = frozenset({"DID","SyntheticDID","Trop"})

# Inference methods to exclude from all plots (e.g. UnitJackKnife). Set via --exclude-inference.
EXCLUDE_INFERENCE_FROM_PLOTS: frozenset[str] = frozenset({"UnitJackKnife","Conformal"})

# Explicit allowed (inference, estimator) pairs for family plots. Only these are plotted (lines, CIs, legend, table).
# Excludes TimeSeriesKfold (TSK), Conformal, UnitJackKnife and any other globally excluded inference.
TBR_FAMILY_ALLOWED_PAIRS: frozenset[tuple[str, str]] = frozenset({
    ("self", "Bayesian_TBR"),
    ("self", "Bayesian_TBR_HorseShoe"),
    ("Kfold", "TBR"), ("BlockResidualBootstrap", "TBR"), 
    ("Kfold", "TBRRidge"), ("Placebo", "TBRRidge"), ("BlockResidualBootstrap", "TBRRidge")
})
SCM_FAMILY_ALLOWED_PAIRS: frozenset[tuple[str, str]] = frozenset({
    ("Kfold", "AugSynthCVXPY"), ("BlockResidualBootstrap", "AugSynthCVXPY")
})


def _load_mmt_config(base_dir: str | None = None) -> dict:
    """Load mmt_config.json from base_dir (or BASE_OUTPUT_DIR). Cached per directory."""
    dir_path = base_dir or BASE_OUTPUT_DIR
    if dir_path in _MMT_CONFIG_CACHE:
        return _MMT_CONFIG_CACHE[dir_path]
    path = Path(dir_path) / "mmt_config.json"
    cfg = {}
    if path.exists():
        try:
            with open(path) as f:
                cfg = json.load(f)
        except Exception:
            pass
    _MMT_CONFIG_CACHE[dir_path] = cfg
    return cfg


def _get_value_col(base_dir: str | None = None) -> str:
    """Value column for DID/data loading. Prefers KPI_COL when it's a valid key in mmt_config.kpi."""
    cfg = _load_mmt_config(base_dir)
    kpi = cfg.get("kpi")
    if isinstance(kpi, dict) and kpi:
        # Prefer KPI_COL when it's a valid dataset key (e.g. --kpi-col SME_CONVERSIONS)
        if KPI_COL and KPI_COL in kpi:
            return kpi[KPI_COL]
        return next(iter(kpi.values()), KPI_COL)
    return KPI_COL


def _get_dataset_filter(base_dir: str | None = None) -> str | None:
    """Dataset filter for matching pickle keys and Cloud column. Prefers KPI_COL when it's a valid key in mmt_config.kpi."""
    cfg = _load_mmt_config(base_dir)
    kpi = cfg.get("kpi")
    if isinstance(kpi, dict) and kpi:
        # Prefer KPI_COL when it's a valid dataset key (e.g. --kpi-col SME_CONVERSIONS)
        if KPI_COL and KPI_COL in kpi:
            return KPI_COL
        return next(iter(kpi.keys()), None)
    return KPI_COL


def _get_control_geos(base_dir: str | None = None) -> list[str]:
    """Control geos. From mmt_config.control_groups"""
    cfg = _load_mmt_config(base_dir)
    cg = cfg.get("control_groups")
    if isinstance(cg, dict) and cg:
        seen = set()
        out = []
        for v in cg.values():
            if isinstance(v, (list, tuple)):
                for g in v:
                    gs = str(g).strip()
                    if gs and gs not in seen:
                        seen.add(gs)
                        out.append(gs)
        if out:
            return out


def _get_treated_geos(base_dir: str | None = None) -> list[str]:
    """Treated geos. From mmt_config.test_groups"""
    cfg = _load_mmt_config(base_dir)
    tg = cfg.get("test_groups")
    if isinstance(tg, dict) and tg:
        seen = set()
        out = []
        for v in tg.values():
            if isinstance(v, (list, tuple)):
                for g in v:
                    gs = str(g).strip()
                    if gs and gs not in seen:
                        seen.add(gs)
                        out.append(gs)
        if out:
            return out


def plot_geo_map(base_dir: str | None = None, save_dir: str | None = None) -> bool:
    """Plot test vs control geos on a US DMA map. Saves geo_map.png to save_dir (or base_dir).
    Uses GeoPandas + community Nielsen DMA GeoJSON. Returns True if saved."""
    base_dir = base_dir or BASE_OUTPUT_DIR
    out_dir = save_dir or base_dir
    try:
        import geopandas as gpd
    except ImportError:
        print("  [geo_map] Skipping: geopandas not installed. pip install geopandas")
        return False
    control_geos = _get_control_geos(base_dir)
    treated_geos = _get_treated_geos(base_dir)
    if not control_geos or not treated_geos:
        print("  [geo_map] Skipping: no test/control geos in config.")
        return False
    try:
        dma_gdf = gpd.read_file(DMA_GEOJSON_URL)
    except Exception as e:
        print(f"  [geo_map] Skipping: could not load DMA GeoJSON: {e}")
        return False
    id_col = "dma_code" if "dma_code" in dma_gdf.columns else "dma"
    if id_col not in dma_gdf.columns:
        print(f"  [geo_map] Skipping: GeoJSON has no {id_col} column.")
        return False
    geo_to_role = {}
    for g in control_geos:
        try:
            geo_to_role[int(g)] = "control"
        except ValueError:
            pass
    for g in treated_geos:
        try:
            geo_to_role[int(g)] = "test"
        except ValueError:
            pass
    if not geo_to_role:
        print("  [geo_map] Skipping: no valid numeric geo IDs.")
        return False
    def _role_for_dma(x):
        try:
            return geo_to_role.get(int(x), "rest") if pd.notna(x) else "rest"
        except (ValueError, TypeError):
            return "rest"

    dma_gdf["role"] = dma_gdf[id_col].map(_role_for_dma)
    merged = dma_gdf
    from matplotlib.patches import Patch

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    for role, color, label in [("control", "#1f77b4", "Geo Control"), ("test", "#ff7f0e", "Geo Test"), ("rest", "#e0e0e0", "Rest")]:
        subset = merged[merged["role"] == role]
        if not subset.empty:
            subset.plot(ax=ax, color=color, edgecolor="black", linewidth=0.3)
    legend_handles = [
        Patch(facecolor="#ff7f0e", edgecolor="black", label="Geo Test"),
        Patch(facecolor="#1f77b4", edgecolor="black", label="Geo Control"),
        Patch(facecolor="#e0e0e0", edgecolor="black", label="Rest"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", fontsize=11)
    ax.set_title("Test vs Control DMAs")
    ax.set_axis_off()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "geo_map.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [geo_map] Saved: {out_path}")
    return True


def _get_treatment_start_date(base_dir: str | None = None) -> str | None:
    """Treatment start date. From mmt_config.test_start_dates"""
    cfg = _load_mmt_config(base_dir)
    ts = cfg.get("test_start_dates")
    if isinstance(ts, dict) and ts:
        v = next(iter(ts.values()), None)
        return str(v) if v else None


def _get_treatment_end_date(base_dir: str | None = None) -> str | None:
    """Treatment end date. From mmt_config.test_end_dates or None."""
    cfg = _load_mmt_config(base_dir)
    te = cfg.get("test_end_dates")
    if isinstance(te, dict) and te:
        v = next(iter(te.values()), None)
        return str(v) if v else None
    return None


def _get_did_input_path(base_dir: str | None = None) -> str | None:
    """Resolve DID long-format data path. Uses DID_INPUT_LONG_PATH or mmt_config.kpi_to_input_path."""
    if DID_INPUT_LONG_PATH:
        return DID_INPUT_LONG_PATH
    dir_path = base_dir or BASE_OUTPUT_DIR
    cfg = _load_mmt_config(dir_path)
    kpi_map = cfg.get("kpi_to_input_path") or {}
    if not isinstance(kpi_map, dict) or not kpi_map:
        return None
    dataset_filter = _get_dataset_filter(dir_path)
    rel = kpi_map.get(dataset_filter) or kpi_map.get(_get_value_col(dir_path))
    if rel:
        return os.path.join(dir_path, rel) if not os.path.isabs(rel) else rel
    return None

# Inference methods to compare (Kfold vs TimeSeriesKfold vs Conformal vs BlockResidualBootstrap)
# BRB (-BRB): model-conditional moving-block residual bootstrap; cumulative bounds are the primary
# aggregate uncertainty object. Estimator is not re-fit per bootstrap draw (conditional uncertainty).
INFERENCE_GROUPS = ["Kfold", "TimeSeriesKfold", "Conformal", "Placebo", "BlockResidualBootstrap"]

# Display names for distribution legend (method label on plot)
METHOD_DISPLAY_NAMES = {
    ("Kfold", "TBR"): "TBR-K",
    ("TimeSeriesKfold", "TBR"): "TBR-TSK",
    ("Conformal", "TBR"): "TBR-C",
    ("Placebo", "TBR"): "TBR-P",
    ("BlockResidualBootstrap", "TBR"): "TBR-BRB",
    ("Kfold", "TBRRidge"): "TBRRidge-K",
    ("TimeSeriesKfold", "TBRRidge"): "TBRRidge-TSK",
    ("Conformal", "TBRRidge"): "TBRRidge-C",
    ("Placebo", "TBRRidge"): "TBRRidge-P",
    ("BlockResidualBootstrap", "TBRRidge"): "TBRRidge-BRB",
    ("UnitJackKnife", "TBRRidge"): "TBRRidge-UJK",
    ("self", "Bayesian_TBR"): "Bayesian TBR",
    ("Kfold", "AugSynthCVXPY"): "AugSynthCVXPY-K",
    ("TimeSeriesKfold", "AugSynthCVXPY"): "AugSynthCVXPY-TSK",
    ("Conformal", "AugSynthCVXPY"): "AugSynthCVXPY-C",
    ("Placebo", "AugSynthCVXPY"): "AugSynthCVXPY-P",
    ("BlockResidualBootstrap", "AugSynthCVXPY"): "AugSynthCVXPY-BRB",
    ("UnitJackKnife", "AugSynthCVXPY"): "AugSynthCVXPY-UJK",
    ("self", "DID"): "DID",
    ("Kfold", "SyntheticControlCVXPY"): "SyntheticControlCVXPY-K",
    ("TimeSeriesKfold", "SyntheticControlCVXPY"): "SyntheticControlCVXPY-TSK",
    ("Conformal", "SyntheticControlCVXPY"): "SyntheticControlCVXPY-C",
    ("Placebo", "SyntheticControlCVXPY"): "SyntheticControlCVXPY-P",
    ("BlockResidualBootstrap", "SyntheticControlCVXPY"): "SyntheticControlCVXPY-BRB",
    ("UnitJackKnife", "SyntheticControlCVXPY"): "SyntheticControlCVXPY-UJK",
    ("self", "Bayesian_TBR_HorseShoe"): "Bayesian TBR HorseShoe",
    # ("Kfold", "TBRAutoSARIMAX"): "TBRAutoSARIMAX-K",
    # ("Conformal", "TBRAutoSARIMAX"): "TBRAutoSARIMAX-C",
    # ("Placebo", "TBRAutoSARIMAX"): "TBRAutoSARIMAX-P",
    ("self", "SyntheticDID"): "SyntheticDID",
}


def discover_results(base_dir: str) -> tuple[dict, dict]:
    """Find all *_weekly_trends_dct.pickle and *_summary_stats_df.csv; return keyed by (inference, estimator)."""
    base = Path(base_dir)
    pickles = {}
    csvs = {}
    for path in base.glob("*_weekly_trends_dct.pickle"):
        name = path.stem.replace("_weekly_trends_dct", "")
        parts = name.split("_", 1)
        if len(parts) == 2:
            inf, est = parts[0], parts[1]
            pickles[(inf, est)] = path
    for path in base.glob("*_summary_stats_df.csv"):
        name = path.stem.replace("_summary_stats_df", "")
        parts = name.split("_", 1)
        if len(parts) == 2:
            inf, est = parts[0], parts[1]
            csvs[(inf, est)] = path
    return pickles, csvs

def discover_stability_results(base_dir: str) -> tuple[pd.DataFrame, list[Path]]:
    """Load counterfactual stability diagnostics saved by run_mmt_estimator_inference_grid.py."""
    stability_dir = Path(base_dir) / "stability_tests"
    if not stability_dir.exists():
        return pd.DataFrame(), []

    summary_path = stability_dir / "counterfactual_stability_summary.csv"
    source_paths: list[Path] = []
    if summary_path.exists():
        try:
            df = pd.read_csv(summary_path)
            source_paths.append(summary_path)
            return df, source_paths
        except Exception:
            pass

    frames: list[pd.DataFrame] = []
    for path in sorted(stability_dir.glob("*__counterfactual_stability.csv")):
        try:
            frame = pd.read_csv(path)
            frames.append(frame)
            source_paths.append(path)
        except Exception:
            continue
    if frames:
        return pd.concat(frames, ignore_index=True), source_paths
    return pd.DataFrame(), source_paths


def _filter_stability_df(
    stability_df: pd.DataFrame,
    dataset_filter: str | None = None,
) -> pd.DataFrame:
    if stability_df is None or stability_df.empty:
        return pd.DataFrame()
    df = stability_df.copy()
    if dataset_filter and "dataset" in df.columns:
        matched = df[df["dataset"].astype(str).str.upper() == str(dataset_filter).upper()]
        if not matched.empty:
            df = matched
    return df.reset_index(drop=True)


def plot_counterfactual_stability_diagnostics(
    base_dir: str,
    save_dir: str,
    dataset_filter: str | None = None,
) -> None:
    """Plot saved counterfactual stability diagnostics (break tests + residual drift tests)."""
    os.makedirs(save_dir, exist_ok=True)
    stability_df, stability_sources = discover_stability_results(base_dir)
    if stability_df.empty:
        print("  [stability plots] No counterfactual stability CSV found under stability_tests/; skipping.")
        return
    if stability_sources:
        print(f"  [stability plots] Loaded stability data from: {stability_sources[0]}")

    df = _filter_stability_df(stability_df, dataset_filter)
    if df.empty:
        return

    filtered_csv = os.path.join(save_dir, "counterfactual_stability_summary_filtered.csv")
    df.to_csv(filtered_csv, index=False)
    print(f"  Saved: {filtered_csv}")

    if "result_type" in df.columns:
        break_df = df[df["result_type"].astype(str) == "break_test"].copy()
    else:
        break_df = pd.DataFrame()
    if not break_df.empty and {"test_name", "p_value"}.issubset(break_df.columns):
        if "dataset" not in break_df.columns:
            break_df["dataset"] = "unknown"
        else:
            break_df["dataset"] = break_df["dataset"].astype(str)

        if "test_group" not in break_df.columns:
            break_df["test_group"] = "unknown"
        else:
            break_df["test_group"] = break_df["test_group"].astype(str)

        break_df["test_name"] = break_df["test_name"].astype(str)
        break_df["label"] = break_df["dataset"] + " | " + break_df["test_group"] + " | " + break_df["test_name"]
        break_df["p_value_num"] = pd.to_numeric(break_df["p_value"], errors="coerce")
        break_df["neg_log10_p"] = -np.log10(np.clip(break_df["p_value_num"], 1e-12, None))
        break_df = break_df.sort_values(["dataset", "test_group", "test_name"]).reset_index(drop=True)

        fig_h = max(4, 0.45 * len(break_df))
        fig, ax = plt.subplots(figsize=(12, fig_h))
        y = np.arange(len(break_df))
        colors = np.where(break_df["p_value_num"].values < 0.05, "#c0392b", "#2980b9")
        ax.barh(y, break_df["neg_log10_p"].values, color=colors, alpha=0.85)
        ax.axvline(-np.log10(0.05), color="black", ls="--", lw=1.5, label="p = 0.05")
        ax.set_yticks(y)
        ax.set_yticklabels(break_df["label"].tolist(), fontsize=9)
        ax.set_xlabel("-log10(p-value)")
        ax.set_title("Counterfactual stability — break tests")
        ax.grid(True, axis="x", alpha=0.35)
        ax.legend(loc="lower right", fontsize=10)
        fig.tight_layout()
        out_path = os.path.join(save_dir, "counterfactual_stability_break_tests.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {out_path}")

    if "result_type" in df.columns:
        resid_df = df[df["result_type"].astype(str) == "residual_drift_test"].copy()
    else:
        resid_df = pd.DataFrame()
    required_cols = {"estimator", "residual_mean", "residual_mean_p_value", "residual_slope_p_value"}
    if not resid_df.empty and required_cols.issubset(resid_df.columns):
        if "dataset" not in resid_df.columns:
            resid_df["dataset"] = "unknown"
        else:
            resid_df["dataset"] = resid_df["dataset"].astype(str)

        if "test_group" not in resid_df.columns:
            resid_df["test_group"] = "unknown"
        else:
            resid_df["test_group"] = resid_df["test_group"].astype(str)

        resid_df["estimator"] = resid_df["estimator"].astype(str)
        resid_df["label"] = resid_df["dataset"] + " | " + resid_df["test_group"] + " | " + resid_df["estimator"]
        resid_df["residual_mean_num"] = pd.to_numeric(resid_df["residual_mean"], errors="coerce")
        resid_df["residual_rmse_num"] = pd.to_numeric(resid_df.get("residual_rmse", np.nan), errors="coerce")
        resid_df["residual_mean_p_num"] = pd.to_numeric(resid_df["residual_mean_p_value"], errors="coerce")
        resid_df["residual_slope_p_num"] = pd.to_numeric(resid_df["residual_slope_p_value"], errors="coerce")

        if "residual_centered_flag" not in resid_df.columns:
            resid_df["residual_centered_flag"] = False
        else:
            resid_df["residual_centered_flag"] = resid_df["residual_centered_flag"].astype(bool)

        if "residual_drift_flag" not in resid_df.columns:
            resid_df["residual_drift_flag"] = False
        else:
            resid_df["residual_drift_flag"] = resid_df["residual_drift_flag"].astype(bool)

        resid_df = resid_df.sort_values(["dataset", "test_group", "estimator"]).reset_index(drop=True)

        fig_h = max(4, 0.5 * len(resid_df))
        fig, ax = plt.subplots(figsize=(12, fig_h))
        y = np.arange(len(resid_df))
        colors = []
        for _, row in resid_df.iterrows():
            if bool(row.get("residual_drift_flag", False)):
                colors.append("#c0392b")
            elif bool(row.get("residual_centered_flag", False)):
                colors.append("#1e8449")
            else:
                colors.append("#b9770e")
        ax.axvline(0, color="black", ls="--", lw=1.2)
        ax.scatter(resid_df["residual_mean_num"].values, y, s=60, c=colors, zorder=3)
        if resid_df["residual_rmse_num"].notna().any():
            xerr = resid_df["residual_rmse_num"].fillna(0).values
            ax.errorbar(
                resid_df["residual_mean_num"].values,
                y,
                xerr=xerr,
                fmt="none",
                ecolor="#7f8c8d",
                elinewidth=1.2,
                alpha=0.7,
                zorder=2,
            )
        ax.set_yticks(y)
        ax.set_yticklabels(resid_df["label"].tolist(), fontsize=9)
        ax.set_xlabel("Residual mean (± RMSE)")
        ax.set_title("Counterfactual stability — residual drift tests")
        ax.grid(True, axis="x", alpha=0.35)

        x_vals = resid_df["residual_mean_num"].values.astype(float)
        rmse_vals = resid_df["residual_rmse_num"].fillna(0).values.astype(float)
        x_pad = max(np.nanmax(np.abs(x_vals)) if len(x_vals) else 0.0, np.nanmax(rmse_vals) if len(rmse_vals) else 0.0) * 0.03 + 1e-6
        for i, (_, row) in enumerate(resid_df.iterrows()):
            text = f"mean p={row['residual_mean_p_num']:.3g}, slope p={row['residual_slope_p_num']:.3g}"
            ax.text(float(row["residual_mean_num"]) + x_pad, i, text, va="center", fontsize=8, color="#2c3e50")

        fig.tight_layout()
        out_path = os.path.join(save_dir, "counterfactual_stability_residual_drift.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {out_path}")


def _filter_by_excluded_inference(pickles: dict, csvs: dict) -> tuple[dict, dict]:
    """Return copies of pickles and csvs with excluded inference methods removed."""
    if not EXCLUDE_INFERENCE_FROM_PLOTS:
        return pickles, csvs
    pickles = {k: v for k, v in pickles.items() if k[0] not in EXCLUDE_INFERENCE_FROM_PLOTS}
    csvs = {k: v for k, v in csvs.items() if k[0] not in EXCLUDE_INFERENCE_FROM_PLOTS}
    return pickles, csvs


def _get_att_from_pickle(
    pickles: dict,
    estimator: str,
    dataset_filter: str | None = None,
    base_dir: str | None = None,
) -> float | None:
    """DID/SyntheticDID: return post-period effect for distribution.
    DID: constant ATT per week; mean = any value.
    SDID: weekly effect = y - y_hat; mean(post-period effect) = aggregate ATT."""
    key = None
    for (inf, est) in pickles:
        if est == estimator:
            key = (inf, est)
            break
    if key is None or key not in pickles:
        return None
    weekly_dct = load_weekly_dct(pickles[key])
    df = get_first_weekly_series(weekly_dct, dataset_filter)
    if df is None or "dt" not in df.columns:
        return None
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    start_str = _get_treatment_start_date(base_dir)
    treatment_start_dt = pd.to_datetime(start_str) if start_str else df["dt"].iloc[max(0, len(df) // 2)]
    post = df["dt"] >= treatment_start_dt
    if "effect" in df.columns and post.any():
        eff_vals = pd.to_numeric(df.loc[post, "effect"], errors="coerce").dropna()
        if len(eff_vals):
            return float(eff_vals.mean())
    if "effect" in df.columns and df["effect"].notna().any():
        df_sorted = df.sort_values("dt")
        return float(df_sorted.loc[df_sorted["effect"].notna(), "effect"].iloc[-1])
    return None


def load_summary_estimates(
    csvs: dict,
    pickles: dict | None = None,
    dataset_filter: str | None = None,
    base_dir: str | None = None,
) -> dict[tuple, float]:
    """For each (inference, estimator) load CSV and return mean Absolute Effect. For DID, use single ATT from pickle (post-period effect; duplicated per week in pickle)."""
    out = {}
    for (inf, est), path in csvs.items():
        if est in ESTIMATORS_EXCLUDED_FROM_DISTRIBUTION:
            continue
        if est in ("DID", "SyntheticDID") and pickles:
            att = _get_att_from_pickle(pickles, est, dataset_filter, base_dir)
            if att is not None:
                out[(inf, est)] = att
                continue
        df = pd.read_csv(path)
        if dataset_filter is not None and "Cloud" in df.columns:
            df = df[df["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
        if "Absolute Effect" in df.columns:
            vals = pd.to_numeric(df["Absolute Effect"], errors="coerce").dropna()
            out[(inf, est)] = float(vals.mean()) if len(vals) else np.nan
    return out


def plot_distribution_of_results(estimates: dict, actual_ref: float | None, save_dir: str) -> None:
    """Distribution of Results: binned histogram (weighted by obs count) + vertical lines per method + family table."""
    os.makedirs(save_dir, exist_ok=True)
    # AugSynthCVXPY: BRB, K, P | TBRRidge: BRB, K, P | Bayesian HorseShoe
    allowed_pairs = frozenset({
        ("BlockResidualBootstrap", "AugSynthCVXPY"), ("Kfold", "AugSynthCVXPY"),
        ("BlockResidualBootstrap", "TBRRidge"), ("Kfold", "TBRRidge")
    })
    values = np.array([v for k, v in estimates.items() if np.isfinite(v) and k in allowed_pairs])
    if len(values) == 0:
        return
    mean_val = float(np.mean(values))
    std_val = float(np.std(values)) if len(values) > 1 else max(abs(mean_val) * 0.3, 100)
    pad = max(3.5 * std_val, 200)
    x_min = min(values.min(), mean_val - pad)
    x_max = max(values.max(), mean_val + pad)
    # Solarize_Light2-style: cream/off-white background for contrast (not pure white)
    _bg = "#fdf6e3"  # Solarized Light base3
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=_bg)
    ax.set_facecolor(_bg)
    for spine in ax.spines.values():
        spine.set_color("#586e75")
        spine.set_linewidth(0.8)
    ax.tick_params(colors="#586e75")
    ax.grid(True, alpha=0.4, color="#93a1a1", linestyle="-")

    # Simple, stable binning: use Freedman–Diaconis when possible, with reasonable caps.
    # This keeps the chart readable without over-optimizing bins around clustered method lines.
    n_vals = len(values)
    if n_vals >= 2:
        q75, q25 = np.percentile(values, [75, 25])
        iqr = float(q75 - q25)
        if iqr > 1e-10:
            bin_width = 2.0 * iqr / (n_vals ** (1.0 / 3.0))
            if bin_width > 1e-10:
                n_bins = int(np.ceil((x_max - x_min) / bin_width))
            else:
                n_bins = int(np.sqrt(n_vals))
        else:
            n_bins = int(np.sqrt(n_vals))
    else:
        n_bins = 10
    n_bins = int(np.clip(n_bins, 12, 40))
    counts, bin_edges = np.histogram(values, bins=n_bins, range=(x_min, x_max), density=True)
    counts_actual, _ = np.histogram(values, bins=n_bins, range=(x_min, x_max), density=False)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    kde = None
    try:
        from scipy import stats as scipy_stats
        kde = scipy_stats.gaussian_kde(values)
        kde.set_bandwidth(kde.factor * 1.25)
    except Exception:
        pass

    bar_heights = counts
    if kde is not None:
        x = np.linspace(x_min, x_max, 300)
        kde_vals = kde(x)
        kde_max = float(np.max(kde_vals))
        counts_max = float(np.max(counts)) if len(counts) > 0 else 1.0
        if counts_max > 1e-10 and kde_max > 1e-10:
            bar_heights = counts * (kde_max / counts_max)

    # Color palette: white bg, teal/navy for density, contrasting accents
    _bar_color = "#5dade2"  # light teal
    _kde_color = "#1a5276"  # deep navy
    _median_color = "#e67e22"  # amber
    _actual_color = "#c0392b"  # crimson
    _method_colors = [
        "#e74c3c", "#3498db", "#2ecc71", "#9b59b6", "#f39c12",
        "#1abc9c", "#e91e63", "#34495e"  # red, blue, green, purple, orange, teal, magenta, dark gray
    ]

    ax.bar(
        bin_edges[:-1],
        bar_heights,
        width=bin_width,
        align="edge",
        alpha=0.35,
        color=_bar_color,
        edgecolor="#f5eed9",
        linewidth=0.5,
        zorder=0,
        label="Weight (obs per bin)",
    )
    if kde is not None:
        x = np.linspace(x_min, x_max, 300)
        ax.plot(x, kde(x), color=_kde_color, lw=2.5, label="Density", zorder=3)
    ax.set_ylim(bottom=0)
    total_count = float(np.sum(counts_actual))
    weighted_mean_val = float(np.average(bin_centers, weights=counts_actual)) if total_count > 0 else float(np.mean(values))
    ax.axvline(weighted_mean_val, color=_median_color, ls="-.", lw=4, label=f"Weighted mean ({weighted_mean_val:.0f})", zorder=5)
    if actual_ref is not None:
        ax.axvline(actual_ref, color=_actual_color, ls="-", lw=2, label="Actual", zorder=5)
    colors = _method_colors
    sorted_items = sorted(
        ((k, v) for k, v in estimates.items() if np.isfinite(v) and k in allowed_pairs),
        key=lambda x: METHOD_DISPLAY_NAMES.get(x[0], f"{x[0][1]} ({x[0][0]})"),
    )
    for i, ((inf, est), val) in enumerate(sorted_items):
        label = METHOD_DISPLAY_NAMES.get((inf, est), f"{est} ({inf})")
        if est == "Trop":
            ax.axvline(val, color="black", ls=":", lw=2, label=label, zorder=5)
        else:
            ax.axvline(val, color=colors[i % len(colors)], ls="--", lw=1.5, label=label, zorder=5)
    dsf = _get_dataset_filter()
    ax.set_xlabel("Incremental Conversions" if not dsf else f"Effect ({dsf})", color="#333333")
    ax.set_ylabel("Probability Density", color="#333333")
    ax.set_title("Comparison of Estimators", color="#222222")
    ax.legend(loc="upper left", fontsize=11)
    ax.set_xlim(x_min, x_max)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, "distribution_of_results.png"), dpi=150, bbox_inches="tight", facecolor=_bg)
    plt.close(fig)

    def _weighted_mean_binned(vals: list, edges: np.ndarray, cnt: np.ndarray) -> float:
        if not vals or not np.any(cnt):
            return float(np.mean(vals)) if vals else np.nan
        vals_arr = np.array(vals)
        idx = np.digitize(vals_arr, edges) - 1
        idx = np.clip(idx, 0, len(cnt) - 1)
        weights = cnt[idx]
        if np.sum(weights) <= 0:
            return float(np.mean(vals_arr))
        return float(np.average(vals_arr, weights=weights))

    rows = []
    for family_name, estimator_keys in sorted(FAMILY_ESTIMATORS.items(), key=lambda x: x[0]):
        fam_vals = [v for (inf, est), v in estimates.items() if est in estimator_keys and np.isfinite(v)]
        if fam_vals:
            wmean = _weighted_mean_binned(fam_vals, bin_edges, counts_actual)
            rows.append({
                "Grouping": family_name,
                "N": len(fam_vals),
                "Mean": round(np.mean(fam_vals)),
                "Median": round(np.median(fam_vals)),
                "Weighted mean": round(wmean),
            })
    if rows:
        tbl = pd.DataFrame(rows)
        tbl.to_csv(os.path.join(save_dir, "distribution_family_summary.csv"), index=False)
        print(f"  Saved: {save_dir}/distribution_of_results.png, distribution_family_summary.csv")


def plot_inference_comparison(
    estimates: dict,
    actual_ref: float | None,
    save_dir: str,
) -> None:
    """Inference comparison: distribution (box/violin) + summary table for Kfold vs TimeSeriesKfold vs Conformal."""
    os.makedirs(save_dir, exist_ok=True)
    # Group estimates by inference
    groups: dict[str, list[float]] = {inf: [] for inf in INFERENCE_GROUPS}
    for (inf, est), val in estimates.items():
        if inf in INFERENCE_GROUPS and np.isfinite(val):
            groups[inf].append(val)

    # Remove TimeSeriesKfold inference and SCM estimators (SyntheticControlCVXPY)
    filtered_groups = {}
    for inf, vals in groups.items():
        if inf == "TimeSeriesKfold":
            continue
        # keep only values coming from non-SCM estimators
        filtered_vals = [
            val for (inf_k, est_k), val in estimates.items()
            if inf_k == inf and est_k not in {"SyntheticControlCVXPY","SyntheticControl"} and np.isfinite(val)
        ]
        if filtered_vals:
            filtered_groups[inf] = filtered_vals

    groups = filtered_groups

    if not groups:
        return

    # Build summary table (sorted by inference name)
    rows = []
    for inf in sorted(groups.keys()):
        vals = groups[inf]
        rows.append({
            "Inference": inf,
            "N": len(vals),
            "Mean": round(np.mean(vals)),
            "Median": round(np.median(vals)),
        })
    if rows:
        tbl = pd.DataFrame(rows)
        tbl.to_csv(os.path.join(save_dir, "inference_comparison_summary.csv"), index=False)

    # Distribution plot: box plot per inference
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axhline(0, color="#586e75", ls="-", lw=1.5, alpha=0.9, zorder=0)
    if actual_ref is not None and actual_ref != 0:
        ax.axhline(actual_ref, color="red", ls="-", lw=1.5, label="Actual", zorder=0)
    labels = sorted(groups.keys())
    data = [groups[l] for l in labels]
    boxplot_kw = {"tick_labels": labels} if "tick_labels" in inspect.signature(ax.boxplot).parameters else {"labels": labels}
    bp = ax.boxplot(data, patch_artist=True, **boxplot_kw)
    colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))
    placebo_color = "#f8b4c4"  # light pink for contrast
    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(placebo_color if labels[i] == "Placebo" else colors[i])
    for line in bp["medians"]:
        line.set_linewidth(2.5)
    ax.set_ylabel("Effect")
    ax.set_xlabel("Inference Method")
    ax.set_title("Inference comparison")
    if actual_ref is not None:
        ax.legend(loc="upper left", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, "inference_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {save_dir}/inference_comparison.png, inference_comparison_summary.csv")


def plot_estimator_effects_by_inference(
    csvs: dict,
    pickles: dict,
    dataset_filter: str | None,
    save_dir: str,
    base_dir: str | None = None,
) -> None:
    """One plot per inference: Y=estimators, X=effect scale, each estimator has point + confidence band."""
    os.makedirs(save_dir, exist_ok=True)
    # Group (inf, est) by inference
    by_inference: dict[str, list[tuple[str, str]]] = {}
    for (inf, est), path in csvs.items():
        if inf not in by_inference:
            by_inference[inf] = []
        by_inference[inf].append((inf, est))

    _bg = "#fdf6e3"
    _method_colors = [
        "#7d3c98", "#2874a6", "#d35400", "#1e8449", "#8e44ad",
        "#148f77", "#b9770e", "#1a5276", "#c0392b",
    ]

    for inf in sorted(by_inference.keys()):
        if inf == "TimeSeriesKfold":
            continue  # Exclude TSK from all TBR/SCM plots
        keys = by_inference[inf]
        rows_data: list[tuple[str, float, float, float]] = []
        for (_, est) in sorted(keys, key=lambda x: x[1]):
            path = csvs.get((inf, est))
            if not path:
                continue
            df = pd.read_csv(path)
            if dataset_filter and "Cloud" in df.columns:
                df_filtered = df[df["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
                if not df_filtered.empty:
                    df = df_filtered
            if df.empty or "Absolute Effect" not in df.columns:
                continue
            eff = pd.to_numeric(df["Absolute Effect"], errors="coerce").dropna()
            lo = pd.to_numeric(df["Effect Lower"], errors="coerce").dropna() if "Effect Lower" in df.columns else eff
            hi = pd.to_numeric(df["Effect Upper"], errors="coerce").dropna() if "Effect Upper" in df.columns else eff
            if len(eff) == 0:
                continue
            e_val = float(eff.iloc[0])
            lo_val = float(lo.iloc[0]) if len(lo) else e_val
            hi_val = float(hi.iloc[0]) if len(hi) else e_val
            rows_data.append((est, e_val, lo_val, hi_val))

        if not rows_data:
            continue

        estimators = [r[0] for r in rows_data]
        effects = [r[1] for r in rows_data]
        lows = [r[2] for r in rows_data]
        highs = [r[3] for r in rows_data]

        x_min = min(min(lows), min(effects), 0) - 500
        x_max = max(max(highs), max(effects), 0) + 500

        fig, ax = plt.subplots(figsize=(10, max(4, len(estimators) * 0.5)), facecolor=_bg)
        ax.set_facecolor(_bg)
        for spine in ax.spines.values():
            spine.set_color("#586e75")
        ax.tick_params(colors="#586e75")
        ax.grid(True, alpha=0.4, color="#93a1a1", axis="x")
        ax.axvline(0, color="#586e75", ls="-", lw=2.5, alpha=0.9)

        y_pos = np.arange(len(estimators))
        for i, (est, e, lo, hi) in enumerate(rows_data):
            color = _method_colors[i % len(_method_colors)]
            lo, hi = min(lo, hi), max(lo, hi)
            ax.fill_betweenx([i - 0.35, i + 0.35], lo, hi, color=color, alpha=0.25, zorder=0)
            ax.hlines(i, lo, hi, color=color, lw=2, zorder=1)
            ax.scatter([e], [i], color=color, s=60, zorder=2, edgecolors="#073642", linewidths=1)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(estimators, fontsize=9)
        ax.set_xlim(x_min, x_max)
        ax.set_xlabel("Effect" + (f" ({dataset_filter})" if dataset_filter else ""), color="#586e75")
        ax.set_ylabel("Estimator", color="#586e75", fontweight="bold")
        ax.set_title(f"Inference: {inf}" + (f" — {dataset_filter}" if dataset_filter else ""), color="#073642")
        fig.tight_layout()
        plt.setp(ax.get_yticklabels(), fontweight="bold")
        safe_inf = inf.replace(" ", "_")
        out_path = os.path.join(save_dir, f"estimator_effects_{safe_inf}.png")
        fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=_bg)
        plt.close(fig)
        print(f"  Saved: {out_path}")


def plot_tbr_family_effects_by_inference(
    csvs: dict,
    pickles: dict,
    dataset_filter: str | None,
    save_dir: str,
    base_dir: str | None = None,
) -> None:
    """Single plot: TBR family estimators (Y) vs effect (X), one column per inference."""
    os.makedirs(save_dir, exist_ok=True)
    tbr_estimators = frozenset({"TBR", "TBRRidge", "Bayesian_TBR", "Bayesian_TBR_HorseShoe"})
    tbr_order = ("TBR", "TBRRidge", "Bayesian_TBR", "Bayesian_TBR_HorseShoe")

    # Collect by iterating over csvs keys (ensures we find all TBR family entries)
    by_inf: dict[str, list[tuple[str, float, float, float]]] = {}
    for (inf, est), path in csvs.items():
        if est not in tbr_estimators:
            continue
        df = pd.read_csv(str(path))
        if dataset_filter and "Cloud" in df.columns:
            df_filtered = df[df["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            df = df_filtered if not df_filtered.empty else df
        if df.empty or "Absolute Effect" not in df.columns:
            continue
        eff = pd.to_numeric(df["Absolute Effect"], errors="coerce").dropna()
        lo = pd.to_numeric(df["Effect Lower"], errors="coerce").dropna() if "Effect Lower" in df.columns else eff
        hi = pd.to_numeric(df["Effect Upper"], errors="coerce").dropna() if "Effect Upper" in df.columns else eff
        if len(eff) == 0:
            continue
        e_val = float(eff.iloc[0])
        lo_val = float(lo.iloc[0]) if len(lo) else e_val
        hi_val = float(hi.iloc[0]) if len(hi) else e_val
        if inf not in by_inf:
            by_inf[inf] = []
        by_inf[inf].append((est, e_val, lo_val, hi_val))

    # Sort rows within each inference by tbr_order
    for inf in by_inf:
        by_inf[inf] = sorted(by_inf[inf], key=lambda r: (tbr_order.index(r[0]) if r[0] in tbr_order else 999, r[0]))

    # Exclude TSK from TBR family plots
    by_inf = {k: v for k, v in by_inf.items() if k != "TimeSeriesKfold"}

    if not by_inf:
        return

    inferences = sorted(by_inf.keys())
    n_cols = len(inferences)
    n_rows_est = max(len(by_inf[inf]) for inf in inferences)
    fig_h = max(5, n_rows_est * 1.5)
    fig_w = max(5, n_cols * 4)

    _bg = "#fdf6e3"
    _method_colors = [
        "#7d3c98", "#2874a6", "#d35400", "#1e8449", "#8e44ad",
        "#148f77", "#b9770e", "#1a5276", "#c0392b",
    ]

    # Shared x-axis scale
    all_vals: list[float] = [0]
    for rows in by_inf.values():
        for _, e, lo, hi in rows:
            all_vals.extend([e, lo, hi])
    x_min = min(all_vals) - 500
    x_max = max(all_vals) + 500

    fig, axes = plt.subplots(1, n_cols, figsize=(fig_w, fig_h), facecolor=_bg, sharey=False)
    if n_cols == 1:
        axes = [axes]
    for col, inf in enumerate(inferences):
        ax = axes[col]
        rows = by_inf[inf]
        ax.set_facecolor(_bg)
        for spine in ax.spines.values():
            spine.set_color("#586e75")
        ax.tick_params(colors="#586e75")
        ax.grid(True, alpha=0.4, color="#93a1a1", axis="x")
        ax.axvline(0, color="#586e75", ls="-", lw=2.5, alpha=0.9)
        ax.set_xlim(x_min, x_max)

        for i, (est, e, lo, hi) in enumerate(rows):
            color = _method_colors[tbr_order.index(est) % len(_method_colors)] if est in tbr_order else _method_colors[i % len(_method_colors)]
            lo, hi = min(lo, hi), max(lo, hi)
            ax.fill_betweenx([i - 0.35, i + 0.35], lo, hi, color=color, alpha=0.25, zorder=0)
            ax.hlines(i, lo, hi, color=color, lw=2, zorder=1)
            ax.scatter([e], [i], color=color, s=60, zorder=2, edgecolors="#073642", linewidths=1)

        ax.set_yticks(np.arange(len(rows)))
        ax.set_yticklabels([r[0] for r in rows], fontsize=16)
        ax.set_xlabel("Effect" + (f" ({dataset_filter})" if dataset_filter else ""), color="#586e75", fontweight="bold")
        ax.set_title(inf, color="#073642", fontweight="bold")
        if col == 0:
            ax.set_ylabel("Estimator", color="#586e75", fontweight="bold")

    fig.suptitle("TBR Family by Inference", fontsize=14, fontweight="bold", color="#073642", y=1.02)
    fig.tight_layout()
    for ax in axes:
        plt.setp(ax.get_yticklabels(), fontsize=13, fontweight="bold")
    out_path = os.path.join(save_dir, "tbr_family_effects_by_inference.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=_bg)
    plt.close(fig)
    print(f"  Saved: {out_path}")


def plot_scm_family_effects_by_inference(
    csvs: dict,
    pickles: dict,
    dataset_filter: str | None,
    save_dir: str,
    base_dir: str | None = None,
) -> None:
    """Single plot: SCM family estimators (Y) vs effect (X), one column per inference."""
    os.makedirs(save_dir, exist_ok=True)
    scm_estimators = frozenset({"AugSynthCVXPY", "SyntheticControlCVXPY"})
    scm_order = ("AugSynthCVXPY", "SyntheticControlCVXPY")

    # Collect by iterating over csvs keys, filtering by SCM_FAMILY_ALLOWED_PAIRS
    by_inf: dict[str, list[tuple[str, float, float, float]]] = {}
    for (inf, est), path in csvs.items():
        if est not in scm_estimators or (inf, est) not in SCM_FAMILY_ALLOWED_PAIRS:
            continue
        df = pd.read_csv(str(path))
        if dataset_filter and "Cloud" in df.columns:
            df_filtered = df[df["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            df = df_filtered if not df_filtered.empty else df
        if df.empty or "Absolute Effect" not in df.columns:
            continue
        eff = pd.to_numeric(df["Absolute Effect"], errors="coerce").dropna()
        lo = pd.to_numeric(df["Effect Lower"], errors="coerce").dropna() if "Effect Lower" in df.columns else eff
        hi = pd.to_numeric(df["Effect Upper"], errors="coerce").dropna() if "Effect Upper" in df.columns else eff
        if len(eff) == 0:
            continue
        e_val = float(eff.iloc[0])
        lo_val = float(lo.iloc[0]) if len(lo) else e_val
        hi_val = float(hi.iloc[0]) if len(hi) else e_val
        if inf not in by_inf:
            by_inf[inf] = []
        by_inf[inf].append((est, e_val, lo_val, hi_val))

    # Sort rows within each inference by scm_order
    for inf in by_inf:
        by_inf[inf] = sorted(by_inf[inf], key=lambda r: (scm_order.index(r[0]) if r[0] in scm_order else 999, r[0]))

    if not by_inf:
        return

    inferences = sorted(by_inf.keys())
    n_cols = len(inferences)
    n_rows_est = max(len(by_inf[inf]) for inf in inferences)
    fig_h = max(5, n_rows_est * 1.5)
    fig_w = max(5, n_cols * 4)

    _bg = "#fdf6e3"
    _method_colors = [
        "#27ae60", "#8e44ad", "#d35400", "#2980b9", "#1e8449",
        "#c0392b", "#148f77", "#b9770e", "#1a5276",
    ]
    _scm_colors = {
        ("BlockResidualBootstrap", "AugSynthCVXPY"): "#27ae60",
        ("BlockResidualBootstrap", "SyntheticControlCVXPY"): "#8e44ad",
        ("Placebo", "SyntheticControlCVXPY"): "black",
    }

    # Shared x-axis scale
    all_vals: list[float] = [0]
    for rows in by_inf.values():
        for _, e, lo, hi in rows:
            all_vals.extend([e, lo, hi])
    x_min = min(all_vals) - 500
    x_max = max(all_vals) + 500

    fig, axes = plt.subplots(1, n_cols, figsize=(fig_w, fig_h), facecolor=_bg, sharey=False)
    if n_cols == 1:
        axes = [axes]
    for col, inf in enumerate(inferences):
        ax = axes[col]
        rows = by_inf[inf]
        ax.set_facecolor(_bg)
        for spine in ax.spines.values():
            spine.set_color("#586e75")
        ax.tick_params(colors="#586e75")
        ax.grid(True, alpha=0.4, color="#93a1a1", axis="x")
        ax.axvline(0, color="#586e75", ls="-", lw=2.5, alpha=0.9)
        ax.set_xlim(x_min, x_max)

        for i, (est, e, lo, hi) in enumerate(rows):
            color = _scm_colors.get((inf, est), _method_colors[scm_order.index(est) % len(_method_colors)] if est in scm_order else _method_colors[i % len(_method_colors)])
            lo, hi = min(lo, hi), max(lo, hi)
            ax.fill_betweenx([i - 0.35, i + 0.35], lo, hi, color=color, alpha=0.25, zorder=0)
            ax.hlines(i, lo, hi, color=color, lw=2, zorder=1)
            ax.scatter([e], [i], color=color, s=60, zorder=2, edgecolors="#073642", linewidths=1)

        ax.set_yticks(np.arange(len(rows)))
        ax.set_yticklabels([r[0] for r in rows], fontsize=16)
        ax.set_xlabel("Effect" + (f" ({dataset_filter})" if dataset_filter else ""), color="#586e75", fontweight="bold")
        ax.set_title(inf, color="#073642", fontweight="bold")
        if col == 0:
            ax.set_ylabel("Estimator", color="#586e75", fontweight="bold")

    fig.suptitle("SCM Family by Inference", fontsize=14, fontweight="bold", color="#073642", y=1.02)
    fig.tight_layout()
    for ax in axes:
        plt.setp(ax.get_yticklabels(), fontsize=13, fontweight="bold")
    out_path = os.path.join(save_dir, "scm_family_effects_by_inference.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=_bg)
    plt.close(fig)
    print(f"  Saved: {out_path}")


def load_weekly_dct(pickle_path: Path) -> dict:
    """Load weekly_trends_dct from pickle."""
    with open(pickle_path, "rb") as f:
        return pickle.load(f)


def _load_did_dataset_from_mmt_config(
    base_dir: str,
    value_col: str,
    date_col: str = "date",
    geo_col: str = "geo",
    dataset_filter: str | None = None,
) -> pd.DataFrame | None:
    """Load dataset from mmt_datasets.pkl (saved by grid). Prefers dataset matching dataset_filter when config available.
    Tries base_dir first, then parent dir if pkl not found (handles KPI subfolders)."""
    path = Path(base_dir) / "mmt_datasets.pkl"
    if not path.exists():
        path = Path(base_dir).parent / "mmt_datasets.pkl"
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            datasets = pickle.load(f)
        if not isinstance(datasets, dict):
            return None
        config_dir = str(path.parent)
        cfg = _load_mmt_config(config_dir)
        kpi_map = cfg.get("kpi") or {}
        # Prefer dataset that matches dataset_filter and has value_col
        if dataset_filter and dataset_filter in datasets:
            raw = datasets[dataset_filter]
            col = kpi_map.get(dataset_filter) or value_col
            if isinstance(raw, pd.DataFrame) and col in raw.columns:
                df = raw.copy()
                dc = date_col if date_col in df.columns else next((c for c in ["date", "Date", "dt"] if c in df.columns), None)
                gc = geo_col if geo_col in df.columns else next((c for c in ["geo", "Geo", "region"] if c in df.columns), None)
                if dc and gc:
                    return df.rename(columns={dc: date_col, gc: geo_col}) if dc != date_col or gc != geo_col else df
        for _k, raw in datasets.items():
            if not isinstance(raw, pd.DataFrame) or value_col not in raw.columns:
                continue
            df = raw.copy()
            dc = date_col if date_col in df.columns else next((c for c in ["date", "Date", "dt"] if c in df.columns), None)
            gc = geo_col if geo_col in df.columns else next((c for c in ["geo", "Geo", "region"] if c in df.columns), None)
            if dc and gc:
                return df.rename(columns={dc: date_col, gc: geo_col}) if dc != date_col or gc != geo_col else df
        return None
    except Exception:
        return None


def load_did_aggregated_series(
    long_path: str | Path | pd.DataFrame,
    dts: pd.Series,
    geos: list[str],
    value_col: str,
    date_col: str = "date",
    geo_col: str = "geo",
) -> pd.Series | None:
    """Build aggregated series from long-format (date, geo, value): sum across geos per date.
    long_path can be a file path or a DataFrame. Returns series aligned to dts.
    Uses exact bucketed aggregation to weekly periods (no nearest-neighbor alignment).
    Weekly convention: pandas to_period("W-SUN"), explicitly anchoring weeks to Sunday."""
    if not geos or not value_col:
        return None
    try:
        if isinstance(long_path, pd.DataFrame):
            raw = long_path
        else:
            long_path = Path(long_path)
            if not long_path.exists():
                return None
            if long_path.suffix.lower() == ".csv":
                raw = pd.read_csv(long_path)
            else:
                with open(long_path, "rb") as f:
                    raw = pickle.load(f)
        if not isinstance(raw, pd.DataFrame) or value_col not in raw.columns:
            return None
        df = raw.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df[geo_col] = df[geo_col].astype(str)
        subset = df[df[geo_col].isin(geos)]
        if subset.empty:
            return None
        agg = subset.groupby(date_col)[value_col].sum()
        agg.index = pd.to_datetime(agg.index)
        # Bucket source data into weekly periods (no nearest-neighbor)
        agg_by_week = agg.groupby(agg.index.to_period("W-SUN")).sum()
        dts_dt = pd.to_datetime(dts)
        week_periods_dts = dts_dt.to_period("W-SUN")
        aligned_values = [agg_by_week.get(p, np.nan) for p in week_periods_dts]
        return pd.Series(aligned_values, index=dts.index)
    except Exception:
        return None


def _compute_control_endpoints(
    base_dir: str,
    treatment_start_dt: pd.Timestamp,
    treatment_end_dt: pd.Timestamp,
    value_col: str,
    control_geos: list[str],
    dataset_filter: str | None,
) -> tuple[float, float]:
    """Load DID data and compute control pre/post means (B, D). Returns (np.nan, np.nan) on failure."""
    B = D = np.nan
    if not control_geos or not value_col:
        return (B, D)
    data = _load_did_dataset_from_mmt_config(base_dir, value_col, dataset_filter=dataset_filter)
    if data is None:
        path_str = _get_did_input_path(base_dir)
        if path_str:
            try:
                p = Path(path_str)
                if p.exists():
                    data = pd.read_csv(p) if p.suffix.lower() == ".csv" else pickle.load(open(p, "rb"))
            except Exception:
                pass
    if not isinstance(data, pd.DataFrame) or value_col not in data.columns:
        return (B, D)
    df = data.copy()
    dc = next((c for c in ["date", "Date", "dt"] if c in df.columns), None)
    gc = next((c for c in ["geo", "Geo", "region"] if c in df.columns), None)
    if not dc or not gc:
        return (B, D)
    df["date"] = pd.to_datetime(df[dc])
    df["geo"] = df[gc].astype(str)
    df = df[df["date"] <= treatment_end_dt]
    subset = df[df["geo"].isin(control_geos)]
    if subset.empty:
        return (B, D)
    agg = subset.groupby("date")[value_col].sum()
    agg.index = pd.to_datetime(agg.index)
    pre = agg[agg.index < treatment_start_dt]
    post = agg[agg.index >= treatment_start_dt]
    if len(pre) and len(post):
        B = float(pre.mean())
        D = float(post.mean())
    return (B, D)


def _get_did_diagnostics_path(
    base_dir: str,
    did_pickle_path: Path | None,
    dataset_filter: str | None = None,
) -> Path:
    """Return path to DID diagnostics JSON. Per-dataset when dataset_filter is set."""
    path = DID_DIAGNOSTICS_PATH
    if path is None and did_pickle_path is not None:
        stem = did_pickle_path.name.replace("_weekly_trends_dct.pickle", "")
        if dataset_filter:
            path = os.path.join(base_dir, f"{stem}_{dataset_filter}_did_diagnostics.json")
        else:
            path = os.path.join(base_dir, f"{stem}_did_diagnostics.json")
    if path is None:
        stem = "self_DID"
        if dataset_filter:
            path = os.path.join(base_dir, f"{stem}_{dataset_filter}_did_diagnostics.json")
        else:
            path = os.path.join(base_dir, f"{stem}_did_diagnostics.json")
    return Path(path)


def _to_json_serializable(v):
    """Convert numpy types to JSON-serializable."""
    if isinstance(v, np.ndarray):
        if v.size == 1:
            return float(v.item())
        return [_to_json_serializable(x) for x in v]
    if hasattr(v, "item") and callable(getattr(v, "item")):
        try:
            return float(v.item())
        except ValueError:
            return v
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (list, tuple)):
        return [_to_json_serializable(x) for x in v]
    if isinstance(v, dict):
        return {k: _to_json_serializable(x) for k, x in v.items()}
    return v


def _generate_did_diagnostics(
    base_dir: str,
    diagnostics_path: Path,
    treatment_start_dt: pd.Timestamp,
    treatment_end_dt: pd.Timestamp,
    dataset_filter: str | None = None,
) -> bool:
    """Run DID model on input data and save diagnostics JSON. Returns True if saved."""
    control_geos = _get_control_geos(base_dir)
    treated_geos = _get_treated_geos(base_dir)
    if not control_geos or not treated_geos:
        return False
    value_col = _get_value_col(base_dir)
    if dataset_filter is None:
        dataset_filter = _get_dataset_filter(base_dir)
    data = _load_did_dataset_from_mmt_config(base_dir, value_col, dataset_filter=dataset_filter)
    if data is None:
        long_path_str = _get_did_input_path(base_dir)
        if not long_path_str:
            return False
        long_path = Path(long_path_str)
        if not long_path.exists():
            return False
        try:
            if long_path.suffix.lower() == ".csv":
                data = pd.read_csv(long_path)
            else:
                with open(long_path, "rb") as f:
                    data = pickle.load(f)
        except Exception:
            return False
    if not isinstance(data, pd.DataFrame) or value_col not in data.columns:
        return False
    df = data.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["geo"] = df["geo"].astype(str)
    df = df[df["date"] <= treatment_end_dt]
    control_df = df[df["geo"].isin(control_geos)]
    treated_df = df[df["geo"].isin(treated_geos)]
    control_agg = control_df.groupby("date")[value_col].sum()
    treated_agg = treated_df.groupby("date")[value_col].sum()
    wide = pd.DataFrame({"control": control_agg, "treated": treated_agg}).fillna(0)
    wide.index = pd.to_datetime(wide.index)
    wide = wide.sort_index()
    try:
        from panel_exp.panel_data import PanelDataset, TimePeriod
        from panel_exp.methods.DID import DID
    except ImportError:
        return False
    pds = PanelDataset(
        wide.T,
        treated_units=["treated"],
        treated_periods=[TimePeriod(treatment_start_dt, treatment_end_dt)],
    )
    model = DID()
    model.run_analysis(pds)
    raw = model.get_detailed_results()
    out = {}
    for key in ("parallel_trends_test", "placebo_test"):
        val = raw.get(key)
        if isinstance(val, dict) and "error" not in val:
            out[key] = {k: _to_json_serializable(v) for k, v in val.items()}
    # Path-based primary: cumulative_att, cumulative_ci
    out["cumulative_att"] = _to_json_serializable(raw.get("cumulative_att"))
    out["mean_post_period_att"] = _to_json_serializable(raw.get("mean_post_period_att"))
    out["n_post"] = _to_json_serializable(raw.get("n_post"))
    out["treatment_effect"] = _to_json_serializable(
        raw.get("treatment_effect_aggregate") or raw.get("treatment_effect")
    )
    out["p_value"] = _to_json_serializable(raw.get("p_value"))
    cum_ci = raw.get("cumulative_ci") or raw.get("treatment_ci_aggregate") or raw.get("treatment_ci")
    if cum_ci is not None and isinstance(cum_ci, (list, tuple)) and len(cum_ci) >= 2:
        out["treatment_ci_aggregate"] = [_to_json_serializable(cum_ci[0]), _to_json_serializable(cum_ci[1])]
        out["cumulative_ci"] = out["treatment_ci_aggregate"]
    # DID upgrade: save richer diagnostics for plot annotations
    for k in (
        "primary_inference_method", "parallel_trends_joint_pvalue", "parallel_trends_violated",
        "parallel_trends_test_type", "largest_pretrend_deviation", "largest_pretrend_period",
        "bootstrap_n", "model_based_se", "model_based_pvalue",
        "pretrend_binning_used", "n_pre_periods_original", "n_pre_bins_used",
        "parallel_trends_joint_pvalue_method", "fallback_reason",
    ):
        v = raw.get(k)
        if v is not None:
            out[k] = _to_json_serializable(v)

    # Control endpoints for plot (B=pre, D=post) when control_series unavailable in plot
    ctrl_idx = control_agg.index
    pre_ctrl = control_agg[ctrl_idx < treatment_start_dt]
    post_ctrl = control_agg[ctrl_idx >= treatment_start_dt]
    if len(pre_ctrl) and len(post_ctrl):
        out["control_pre_mean"] = _to_json_serializable(float(pre_ctrl.mean()))
        out["control_post_mean"] = _to_json_serializable(float(post_ctrl.mean()))

    # Placebo treatment timing: run DID with fake treatment start 8, 12, 20 weeks earlier.
    # If placebo ATT ≈ 0 → experiment valid. If large → estimate unreliable.
    placebo_offsets = [8, 12, 20]
    placebo_out = {}
    cols = pd.DatetimeIndex(wide.index)
    for offset in placebo_offsets:
        try:
            placebo_start = treatment_start_dt - pd.Timedelta(weeks=offset)
            placebo_end = treatment_start_dt
            if placebo_start < cols.min() or placebo_end > cols.max():
                continue
            p_start = placebo_start if placebo_start in cols else (cols[cols >= placebo_start].min() if (cols >= placebo_start).any() else None)
            p_end = placebo_end if placebo_end in cols else (cols[cols <= placebo_end].max() if (cols <= placebo_end).any() else None)
            if pd.isna(p_start) or pd.isna(p_end) or p_start >= p_end:
                continue
            pds_placebo = PanelDataset(
                wide.T,
                treated_units=["treated"],
                treated_periods=[TimePeriod(p_start, p_end)],
            )
            model_placebo = DID()
            model_placebo.run_analysis(pds_placebo)
            raw_p = model_placebo.get_detailed_results()
            att = raw_p.get("cumulative_att")
            if att is None:
                att = raw_p.get("treatment_effect_aggregate") or raw_p.get("treatment_effect")
            placebo_out[f"att_{offset}w_earlier"] = _to_json_serializable(att)
        except Exception:
            pass
    if placebo_out:
        out["placebo_treatment_timing"] = placebo_out

    # Effect scale: we use aggregated wide (control + treated), so n_treated_units_in_panel=1 → aggregate
    out["effect_scale"] = "aggregate"
    out["n_treated_units_in_panel"] = 1

    os.makedirs(base_dir, exist_ok=True)
    with open(diagnostics_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    return True


def _generate_sdid_diagnostics(
    base_dir: str,
    diagnostics_path: Path,
    treatment_start_dt: pd.Timestamp,
    treatment_end_dt: pd.Timestamp,
    dataset_filter: str | None = None,
) -> bool:
    """Run SyntheticDID on donor matrix (one row per control geo) and save diagnostics.
    Uses true donor structure: control geos as separate units, treated aggregated.
    Returns True if saved."""
    control_geos = _get_control_geos(base_dir)
    treated_geos = _get_treated_geos(base_dir)
    if not control_geos or not treated_geos:
        return False
    value_col = _get_value_col(base_dir)
    if dataset_filter is None:
        dataset_filter = _get_dataset_filter(base_dir)
    data = _load_did_dataset_from_mmt_config(base_dir, value_col, dataset_filter=dataset_filter)
    if data is None:
        long_path_str = _get_did_input_path(base_dir)
        if not long_path_str:
            return False
        long_path = Path(long_path_str)
        if not long_path.exists():
            return False
        try:
            if long_path.suffix.lower() == ".csv":
                data = pd.read_csv(long_path)
            else:
                with open(long_path, "rb") as f:
                    data = pickle.load(f)
        except Exception:
            return False
    if not isinstance(data, pd.DataFrame) or value_col not in data.columns:
        return False
    df = data.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["geo"] = df["geo"].astype(str)
    df = df[df["date"] <= treatment_end_dt]
    control_df = df[df["geo"].isin(control_geos)]
    treated_df = df[df["geo"].isin(treated_geos)]
    if control_df.empty or treated_df.empty:
        return False
    # Build donor matrix: one row per control geo, one row for treated (aggregated)
    control_wide = control_df.pivot(index="geo", columns="date", values=value_col).fillna(0)
    treated_agg = treated_df.groupby("date")[value_col].sum()
    all_dates = control_wide.columns.union(treated_agg.index)
    all_dates = pd.to_datetime(all_dates).sort_values()
    control_wide = control_wide.reindex(columns=all_dates).fillna(0)
    treated_row = pd.DataFrame(
        treated_agg.reindex(all_dates).fillna(0).values.reshape(1, -1),
        index=["treated"],
        columns=all_dates,
    )
    wide = pd.concat([control_wide, treated_row])
    wide = wide.fillna(0)
    # PanelDataset requires treatment dates to exist in columns; use nearest if exact match missing
    cols = pd.DatetimeIndex(wide.columns)
    t_start = treatment_start_dt if treatment_start_dt in cols else (cols[cols >= treatment_start_dt].min() if (cols >= treatment_start_dt).any() else cols.max())
    t_end = treatment_end_dt if treatment_end_dt in cols else (cols[cols <= treatment_end_dt].max() if (cols <= treatment_end_dt).any() else cols.max())
    if pd.isna(t_start) or pd.isna(t_end):
        return False
    try:
        from panel_exp.panel_data import PanelDataset, TimePeriod
        from panel_exp.methods.synthetic_did import SyntheticDID
    except ImportError:
        return False
    pds = PanelDataset(
        wide,
        treated_units=["treated"],
        treated_periods=[TimePeriod(t_start, t_end)],
    )
    model = SyntheticDID()
    model.run_analysis(pds)
    raw = model.get_detailed_results()
    out = {"approximate_diagnostics": False}
    for key in ("parallel_trends_test", "placebo_test"):
        val = raw.get(key)
        if isinstance(val, dict) and "error" not in val:
            out[key] = {k: _to_json_serializable(v) for k, v in val.items()}
    out["treatment_effect"] = _to_json_serializable(
        raw.get("treatment_effect_aggregate") or raw.get("treatment_effect")
    )
    out["p_value"] = _to_json_serializable(raw.get("p_value"))
    # Donor weights for synthetic control quality: N_eff = 1/sum(weights^2)
    omega = getattr(model, "omega", getattr(model, "_omega", None))
    if omega is not None:
        omega = np.asarray(omega).ravel()
        control_names = [str(x) for x in wide.index if str(x) != "treated"]
        if len(control_names) == len(omega):
            out["donor_weights"] = omega.tolist()
            out["donor_names"] = control_names
        out["eff_n_omega"] = _to_json_serializable(
            float(getattr(model, "sdid_diagnostics", {}).get("eff_n_omega", 1.0 / (np.sum(omega ** 2) + 1e-12)))
        )

    # Placebo treatment timing: run SDID with fake treatment start 8, 12, 20 weeks earlier.
    placebo_offsets = [8, 12, 20]
    placebo_out = {}
    for offset in placebo_offsets:
        try:
            placebo_start = treatment_start_dt - pd.Timedelta(weeks=offset)
            placebo_end = treatment_start_dt
            if placebo_start < cols.min() or placebo_end > cols.max():
                continue
            p_start = placebo_start if placebo_start in cols else (cols[cols >= placebo_start].min() if (cols >= placebo_start).any() else None)
            p_end = placebo_end if placebo_end in cols else (cols[cols <= placebo_end].max() if (cols <= placebo_end).any() else None)
            if pd.isna(p_start) or pd.isna(p_end) or p_start >= p_end:
                continue
            pds_placebo = PanelDataset(
                wide,
                treated_units=["treated"],
                treated_periods=[TimePeriod(p_start, p_end)],
            )
            model_placebo = SyntheticDID()
            model_placebo.run_analysis(pds_placebo)
            raw_p = model_placebo.get_detailed_results()
            att = raw_p.get("treatment_effect_aggregate") or raw_p.get("treatment_effect")
            placebo_out[f"att_{offset}w_earlier"] = _to_json_serializable(att)
        except Exception:
            pass
    if placebo_out:
        out["placebo_treatment_timing"] = placebo_out

    # Effect scale: donor matrix has control geos + one aggregated treated row → aggregate
    out["effect_scale"] = "aggregate"
    out["n_treated_units_in_panel"] = 1

    os.makedirs(base_dir, exist_ok=True)
    with open(diagnostics_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    return True


def _load_did_diagnostics(
    base_dir: str,
    did_pickle_path: Path | None,
    dataset_filter: str | None = None,
) -> dict | None:
    """Load DID diagnostics JSON. Expects parallel_trends_test (interaction_pvalue, parallel_trends_violated)."""
    path = _get_did_diagnostics_path(base_dir, did_pickle_path, dataset_filter)
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _dataset_key_matches(key: tuple, dataset_filter: str) -> bool:
    """Check if key's cloud/dataset part matches filter. Handles (tg, cloud) or (tg, cloud, kpi). Uses exact match to avoid wrong dataset (e.g. DME matching DME_WEB_ORDERS)."""
    if len(key) < 2:
        return False
    cloud = str(key[1]).upper()
    filter_upper = str(dataset_filter).upper()
    return cloud == filter_upper


def get_first_weekly_series(
    weekly_dct: dict,
    dataset_filter: str | None = None,
) -> pd.DataFrame | None:
    """Get first matching (test_group, dataset) weekly DataFrame; has dt, y, y_hat, effect, optionally y_lower, y_upper.
    When dataset_filter is set, returns a df that matches. Fallback: if exactly one key, use it (single-dataset pickle)."""
    if not weekly_dct:
        return None
    if dataset_filter:
        for key, df in weekly_dct.items():
            if _dataset_key_matches(key, dataset_filter):
                return df
        if len(weekly_dct) == 1:
            return next(iter(weekly_dct.values()))
        return None
    return next(iter(weekly_dct.values()))


def plot_did_estimate(
    pickles: dict,
    csvs: dict,
    save_dir: str,
    dataset_filter: str | None = None,
) -> None:
    """DID/SDID Estimate charts with aggregate ATT (per period) and per-geo ATE.

    DID: classic A/B/C/D endpoint schematic (parallel trends), control B->D, treated A->C,
    counterfactual A->CF. β1/β2/β3 annotations. Requires control data for pure schematic.

    SyntheticDID: actual y and y_hat time-series paths (no endpoint decomposition).
    Optional control as faint reference. y_lower/y_upper band assumes outcome-scale bounds."""
    for estimator in ("DID", "SyntheticDID"):
        key = None
        for (inf, est) in pickles:
            if est == estimator:
                key = (inf, est)
                break
        if key is None or key not in pickles:
            continue
        _plot_did_estimate_single(pickles, csvs, save_dir, dataset_filter, key, estimator)
        _plot_did_gap_diagnostic(pickles, csvs, save_dir, dataset_filter, key, estimator)
        if estimator == "DID":
            _plot_did_preperiod_fit(pickles, save_dir, dataset_filter, key, estimator)
        _plot_event_study(pickles, save_dir, dataset_filter, key, estimator)


def _plot_event_study(
    pickles: dict,
    save_dir: str,
    dataset_filter: str | None,
    key: tuple,
    estimator: str,
) -> None:
    """Event study: weekly treatment effects relative to treatment start.

    Verifies pre-treatment effects ≈ 0 (parallel trends), no upward drift before treatment,
    and that treatment effect emerges only after intervention."""
    weekly_dct = load_weekly_dct(pickles[key])
    df = get_first_weekly_series(weekly_dct, dataset_filter)
    if df is None or "dt" not in df.columns:
        return
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    did_pickle_path = Path(pickles[key])
    base_dir = str(did_pickle_path.parent)
    start_str = _get_treatment_start_date(base_dir)
    treatment_start_dt = pd.to_datetime(start_str) if start_str else df["dt"].iloc[max(0, len(df) // 2)]

    # Step 1: event_time = (dt - treatment_start_date) in weeks
    df["event_time"] = ((df["dt"] - treatment_start_dt).dt.days // 7).astype(int)

    # Step 2: effect = y - y_hat
    if "effect" not in df.columns and "y" in df.columns and "y_hat" in df.columns:
        df["effect"] = pd.to_numeric(df["y"], errors="coerce") - pd.to_numeric(df["y_hat"], errors="coerce")
    if "effect" not in df.columns:
        return
    df["effect"] = pd.to_numeric(df["effect"], errors="coerce")

    # Step 3: aggregate by event_time
    agg = df.groupby("event_time")["effect"].mean()
    if agg.empty:
        return
    has_ci = "y_lower" in df.columns and "y_upper" in df.columns and "y" in df.columns
    if has_ci:
        df["eff_lower"] = pd.to_numeric(df["y"], errors="coerce") - pd.to_numeric(df["y_upper"], errors="coerce")
        df["eff_upper"] = pd.to_numeric(df["y"], errors="coerce") - pd.to_numeric(df["y_lower"], errors="coerce")
        lower_agg = df.groupby("event_time")["eff_lower"].mean()
        upper_agg = df.groupby("event_time")["eff_upper"].mean()

    # Pre-period diagnostics
    pre_mask = agg.index < 0
    mean_pre_effect = float(agg.loc[pre_mask].mean()) if pre_mask.any() else np.nan
    max_pre_effect = np.nan
    if pre_mask.any():
        max_pre_effect = float(np.nanmax(np.abs(agg.loc[pre_mask].values)))
    pre_slope = np.nan
    if pre_mask.any() and pre_mask.sum() >= 2:
        et_pre = agg.index[pre_mask].values.astype(float)
        eff_pre = agg.loc[pre_mask].values
        valid = ~np.isnan(eff_pre)
        if valid.sum() >= 2:
            slope, _ = np.polyfit(et_pre[valid], eff_pre[valid], 1)
            pre_slope = float(slope)

    # Step 4–7: plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhline(0, color="black", ls="--", lw=0.8, zorder=0)
    ax.axvline(0, color="gray", ls="--", lw=1.5, label="Treatment start", zorder=1)

    event_times = agg.index.values
    effects = agg.values
    pre_mask_plot = event_times < 0
    post_mask_plot = event_times >= 0

    if pre_mask_plot.any():
        ax.plot(event_times[pre_mask_plot], effects[pre_mask_plot], "o-", color="gray", lw=2, markersize=6,
                label="Pre-period", zorder=2)
    if post_mask_plot.any():
        ax.plot(event_times[post_mask_plot], effects[post_mask_plot], "o-", color="steelblue", lw=2, markersize=6,
                label="Post-period", zorder=2)

    if has_ci:
        lower_vals = lower_agg.reindex(agg.index).values
        upper_vals = upper_agg.reindex(agg.index).values
        lower_vals, upper_vals = np.minimum(lower_vals, upper_vals), np.maximum(lower_vals, upper_vals)
        valid_ci = ~np.isnan(lower_vals) & ~np.isnan(upper_vals)
        # CI shading only during treatment period (event_time >= 0)
        post_ci_mask = post_mask_plot & valid_ci
        if post_ci_mask.any():
            ax.fill_between(agg.index[post_ci_mask], lower_vals[post_ci_mask], upper_vals[post_ci_mask], color="steelblue", alpha=0.2, zorder=0)

    # Textbox: mean pre-period effect, pre-period slope, max pre-period deviation
    lines = []
    if np.isfinite(mean_pre_effect):
        lines.append(f"Mean pre-period effect: {mean_pre_effect:,.0f}")
    if np.isfinite(pre_slope):
        lines.append(f"Pre-period trend slope: {pre_slope:,.2f}")
    if np.isfinite(max_pre_effect):
        lines.append(f"Max pre-period deviation: {max_pre_effect:,.0f}")
    if lines:
        ax.text(0.02, 0.98, "\n".join(lines), transform=ax.transAxes, fontsize=8, va="top", ha="left",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9))

    ax.set_xlabel("Event time (weeks from treatment start)")
    ax.set_ylabel("Treatment effect")
    dataset_name = dataset_filter or (str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else "unknown")
    ax.set_title(f"Event Study — {estimator} — {dataset_name}")
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.4)

    # Step 8: save
    safe_dataset = re.sub(r"[^\w\-]", "_", str(dataset_name))
    base_name = f"event_study_{estimator}_{safe_dataset}"
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, f"{base_name}.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {save_dir}/{base_name}.png")


def _plot_did_gap_diagnostic(
    pickles: dict,
    csvs: dict,
    save_dir: str,
    dataset_filter: str | None,
    key: tuple,
    estimator: str,
) -> None:
    """DID gap diagnostic: gap(t) = treated − counterfactual over time.

    For SDID: uses centered gap = gap(t) − mean(pre-period gap) to remove level offset.
    If centered gap still trends upward in pre, SDID is mis-specified.
    Shows: hline at 0, vline at treatment start, shaded CI band for ATT, mean post-period ATT."""
    weekly_dct = load_weekly_dct(pickles[key])
    df = get_first_weekly_series(weekly_dct, dataset_filter)
    if df is None or "dt" not in df.columns:
        return
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt").reset_index(drop=True)
    dts = df["dt"]
    did_pickle_path = Path(pickles[key])
    base_dir = str(did_pickle_path.parent)
    start_str = _get_treatment_start_date(base_dir)
    treatment_start_dt = pd.to_datetime(start_str) if start_str else dts.iloc[max(0, len(dts) // 2)]
    post_mask = df["dt"] >= treatment_start_dt

    # gap(t) = treated − counterfactual = effect (or y - y_hat)
    if "effect" in df.columns:
        gap = pd.to_numeric(df["effect"], errors="coerce")
    elif "y" in df.columns and "y_hat" in df.columns:
        gap = pd.to_numeric(df["y"], errors="coerce") - pd.to_numeric(df["y_hat"], errors="coerce")
    else:
        return
    if not gap.notna().any():
        return

    # SDID: use centered gap to remove level offset. gap_centered(t) = gap(t) − mean(pre-period gap).
    # If centered gap still trends upward in pre, SDID is mis-specified.
    pre_mask = df["dt"] < treatment_start_dt
    mean_pre_gap = float(gap.loc[pre_mask].mean()) if pre_mask.any() else 0.0
    if estimator == "SyntheticDID" and pre_mask.any():
        gap = gap - mean_pre_gap
        gap_label = "Cumulative centered gap (treated − synthetic − pre mean)"
    else:
        gap_label = "Cumulative gap (treated − counterfactual)"

    cumulative_gap = gap.cumsum()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhline(0, color="black", ls="-", lw=0.8, zorder=0)
    ax.axvline(treatment_start_dt, color="gray", ls="--", lw=1.5, label="Treatment start", zorder=1)
    ax.plot(dts, cumulative_gap, color="steelblue", lw=2, label=gap_label, zorder=2)

    # Mean ATT CI as horizontal band in post. Never derive from y_lower/y_upper (outcome-space bounds).
    # CI priority: CSV Effect Lower/Upper, then CSV Absolute Effect ± 95CI/2, then diagnostics.
    att_ci_lb = att_ci_ub = np.nan
    if key in csvs:
        sdf = pd.read_csv(csvs[key])
        if dataset_filter and "Cloud" in sdf.columns:
            sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
        if "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns:
            att_ci_lb = pd.to_numeric(sdf["Effect Lower"], errors="coerce").mean()
            att_ci_ub = pd.to_numeric(sdf["Effect Upper"], errors="coerce").mean()
        elif "Absolute Effect" in sdf.columns and "95 CI" in sdf.columns:
            est = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
            half = pd.to_numeric(sdf["95 CI"], errors="coerce").mean() / 2
            att_ci_lb = est - half
            att_ci_ub = est + half
    if not np.isfinite(att_ci_lb) or not np.isfinite(att_ci_ub):
        # Optional diagnostics fallback. TROP: cumulative_ci only (no legacy treatment_ci_aggregate).
        if estimator != "DID":
            diag = _load_did_diagnostics(base_dir, did_pickle_path, dataset_filter)
            if diag:
                if estimator == "Trop":
                    ci = diag.get("cumulative_ci")
                else:
                    ci = diag.get("cumulative_ci") or diag.get("treatment_ci_aggregate")
                if isinstance(ci, (list, tuple)) and len(ci) >= 2:
                    att_ci_lb = float(ci[0]) if ci[0] is not None else np.nan
                    att_ci_ub = float(ci[1]) if ci[1] is not None else np.nan
    if np.isfinite(att_ci_lb) and np.isfinite(att_ci_ub) and post_mask.any():
        if estimator == "SyntheticDID" and pre_mask.any():
            att_ci_lb = att_ci_lb - mean_pre_gap
            att_ci_ub = att_ci_ub - mean_pre_gap
        post_dts = dts[post_mask]
        ax.fill_between(post_dts, att_ci_lb, att_ci_ub, color="steelblue", alpha=0.2, zorder=0)

    # Cumulative ATT label (final cumulative value at end of post-period)
    cumulative_att_post = np.nan
    if post_mask.any():
        cumulative_att_post = float(gap.loc[post_mask].sum())
    if np.isfinite(cumulative_att_post):
        ax.text(0.98, 0.98, f"Cumulative ATT: {cumulative_att_post:,.0f}", transform=ax.transAxes,
                fontsize=9, fontweight="bold", va="top", ha="right",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.9))

    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative centered gap" if estimator == "SyntheticDID" else "Cumulative gap (treated − counterfactual)")
    title_suffix = f" ({estimator})" + (f" — {dataset_filter}" if dataset_filter else "")
    ax.set_title("DID Gap Diagnostic" + title_suffix)
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    base_name = "did_gap_diagnostic_sdid" if estimator == "SyntheticDID" else "did_gap_diagnostic"
    fig.savefig(os.path.join(save_dir, f"{base_name}.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {save_dir}/{base_name}.png")


def _plot_did_preperiod_fit(
    pickles: dict,
    save_dir: str,
    dataset_filter: str | None,
    key: tuple,
    estimator: str,
) -> None:
    """Pre-period fit diagnostic for DID only. Shows whether the DID counterfactual tracks treated well before treatment.

    Canonical pre-period fit plot should use experiment outputs (pickle), not regenerated diagnostics.
    For DID, this is a pre-period predictive-fit diagnostic only. DID identification still relies on
    parallel trends, not exact level matching."""
    if estimator != "DID":
        return
    weekly_dct = load_weekly_dct(pickles[key])
    df = get_first_weekly_series(weekly_dct, dataset_filter)
    if df is None or "dt" not in df.columns or "y" not in df.columns or "y_hat" not in df.columns:
        return
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt").reset_index(drop=True)
    did_pickle_path = Path(pickles[key])
    base_dir = str(did_pickle_path.parent)
    start_str = _get_treatment_start_date(base_dir)
    treatment_start_dt = pd.to_datetime(start_str) if start_str else df["dt"].iloc[max(0, len(df) // 2)]

    # Pre-period: all rows where dt < treatment_start_date
    pre_mask = df["dt"] < treatment_start_dt
    if pre_mask.sum() < 5:
        warnings.warn(
            f"Pre-period fit plot skipped: {pre_mask.sum()} pre-period observations ({estimator} {dataset_filter or 'unknown'})",
            stacklevel=2,
        )
        return

    pre_df = df.loc[pre_mask].copy()
    dts_pre = pre_df["dt"]
    y_pre = pd.to_numeric(pre_df["y"], errors="coerce")
    y_hat_pre = pd.to_numeric(pre_df["y_hat"], errors="coerce")
    valid = y_pre.notna() & y_hat_pre.notna()
    if not valid.any():
        return
    y_pre = y_pre[valid]
    y_hat_pre = y_hat_pre[valid]
    dts_pre = dts_pre[valid]

    # Fit diagnostics (pre-period only)
    gap_pre = y_pre.values - y_hat_pre.values
    mean_pre_gap = float(np.nanmean(gap_pre))
    pre_rmse = float(np.sqrt(np.nanmean(gap_pre ** 2)))
    mean_y_pre = float(np.nanmean(y_pre.values))
    pre_rmse_pct = (pre_rmse / mean_y_pre * 100) if mean_y_pre > 0 and np.isfinite(pre_rmse) else np.nan
    var_y_pre = float(np.nanvar(y_pre.values))
    var_resid = float(np.nanvar(gap_pre))
    pre_r2 = (1.0 - var_resid / var_y_pre) if var_y_pre > 0 else np.nan
    max_pre_gap = float(np.nanmax(np.abs(gap_pre)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dts_pre, y_pre.values, color="red", lw=2.5, label="Treated (actual)", zorder=2)
    ax.plot(dts_pre, y_hat_pre.values, color="green", ls="--", lw=2, label="DID counterfactual", zorder=2)
    # Optional: light shaded area for pre-period gap
    ax.fill_between(dts_pre, y_pre.values, y_hat_pre.values, color="gray", alpha=0.2, zorder=0)

    lines = [
        f"Mean pre-gap: {mean_pre_gap:,.0f}",
        f"Pre-fit RMSE: {pre_rmse:,.0f}",
        f"Pre-fit RMSE %: {pre_rmse_pct:.1f}%" if np.isfinite(pre_rmse_pct) else "Pre-fit RMSE %: n/a",
        f"Pre-fit R²: {pre_r2:.2f}" if np.isfinite(pre_r2) else "Pre-fit R²: n/a",
        f"Max pre-gap: {max_pre_gap:,.0f}",
    ]
    ax.text(0.02, 0.98, "\n".join(lines), transform=ax.transAxes, fontsize=8, va="top", ha="left",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9))

    ax.set_xlabel("Time")
    ax.set_ylabel("Outcome")
    dataset_label = dataset_filter or (str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else "unknown")
    ax.set_title(f"Pre-period fit — DID — {dataset_label}")
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.4)
    fig.tight_layout()
    base_name = f"did_preperiod_fit_{dataset_label}"
    out_path = os.path.join(save_dir, f"{base_name}.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_path}")


def _plot_did_estimate_single(
    pickles: dict,
    csvs: dict,
    save_dir: str,
    dataset_filter: str | None,
    key: tuple,
    estimator: str,
) -> None:
    """Generate one DID conceptual chart for the given estimator (DID or SyntheticDID)."""
    did_pickle_path = Path(pickles[key])
    base_dir = str(did_pickle_path.parent)
    weekly_dct = load_weekly_dct(pickles[key])
    df = get_first_weekly_series(weekly_dct, dataset_filter)
    if df is None or "dt" not in df.columns:
        return
    os.makedirs(save_dir, exist_ok=True)
    df = df.copy()
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.sort_values("dt").reset_index(drop=True)
    dts = df["dt"]
    start_str = _get_treatment_start_date(base_dir)
    end_str = _get_treatment_end_date(base_dir)
    treatment_start_dt = pd.to_datetime(start_str) if start_str else dts.iloc[max(0, len(dts) // 2)]
    treatment_end_dt = pd.to_datetime(end_str) if end_str else pd.to_datetime(df["dt"]).max()
    value_col = _get_value_col(base_dir)
    control_geos = _get_control_geos(base_dir)
    treated_geos = _get_treated_geos(base_dir)
    did_data = _load_did_dataset_from_mmt_config(base_dir, value_col, dataset_filter=dataset_filter) if base_dir else None
    if did_data is None:
        did_data = _get_did_input_path(base_dir)
    has_did_data = did_data is not None and (not isinstance(did_data, pd.DataFrame) or not did_data.empty)
    control_series = load_did_aggregated_series(did_data, dts, control_geos, value_col) if has_did_data and control_geos else None
    # Control from did_data; treated (y) and counterfactual (y_hat) from pickle only
    diagnostics_path = _get_did_diagnostics_path(base_dir, did_pickle_path, dataset_filter)
    if not diagnostics_path.exists():
        if estimator == "DID":
            _generate_did_diagnostics(base_dir, diagnostics_path, treatment_start_dt, treatment_end_dt, dataset_filter)
        elif estimator == "SyntheticDID":
            _generate_sdid_diagnostics(base_dir, diagnostics_path, treatment_start_dt, treatment_end_dt, dataset_filter)
    diag = _load_did_diagnostics(base_dir, did_pickle_path, dataset_filter)
    # Regenerate DID diagnostics if missing control endpoints or missing DID upgrade fields (needed for plot)
    _needs_regenerate = (
        estimator == "DID"
        and diag is not None
        and (
            "control_pre_mean" not in diag
            or diag.get("primary_inference_method") is None  # DID upgrade field
        )
    )
    if _needs_regenerate:
        _generate_did_diagnostics(base_dir, diagnostics_path, treatment_start_dt, treatment_end_dt, dataset_filter)
        diag = _load_did_diagnostics(base_dir, did_pickle_path, dataset_filter)
    post_mask = df["dt"] >= treatment_start_dt
    post_period_count = int(post_mask.sum()) if post_mask.any() else 0
    mean_post_period_att = np.nan
    cumulative_att = np.nan
    # DID: Phase 1 — use pickle effect as source of truth; CI from CSV (path-based).
    if estimator == "DID":
        if post_period_count <= 0:
            print(f"DID: n_post={post_period_count} — skipping plot.")
            return
        # Phase 1: cumulative_att = sum(effect[post_mask]), mean_att = mean(effect[post_mask])
        if "effect" in df.columns and post_mask.any():
            eff_vals = pd.to_numeric(df.loc[post_mask, "effect"], errors="coerce").dropna()
            if len(eff_vals) > 0:
                cumulative_att = float(eff_vals.sum())
                mean_post_period_att = float(eff_vals.mean())
                print(f"DID plot: n_post (pickle)={post_period_count} cumulative_att={cumulative_att:,.0f} mean_att={mean_post_period_att:,.0f}")
        if not np.isfinite(cumulative_att):
            print("DID: could not compute cumulative_att from pickle or diagnostics — skipping plot.")
            return
    # Non-DID: pickle, then CSV
    if estimator != "DID" and np.isnan(mean_post_period_att) and "effect" in df.columns and post_mask.any():
        eff_vals = pd.to_numeric(df.loc[post_mask, "effect"], errors="coerce").dropna()
        if len(eff_vals):
            mean_post_period_att = float(eff_vals.mean())
            cumulative_att = mean_post_period_att * post_period_count if post_period_count > 0 else np.nan
    if estimator != "DID" and np.isnan(mean_post_period_att) and key in csvs:
        sdf = pd.read_csv(csvs[key])
        if dataset_filter and "Cloud" in sdf.columns:
            sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
        if "Absolute Effect" in sdf.columns:
            mean_post_period_att = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
            if np.isfinite(mean_post_period_att) and post_period_count > 0:
                cumulative_att = mean_post_period_att * post_period_count
    if np.isnan(mean_post_period_att) and diag:
        eff = diag.get("treatment_effect_aggregate") or diag.get("treatment_effect")
        if eff is not None:
            try:
                mean_post_period_att = float(eff)
                if np.isfinite(mean_post_period_att) and post_period_count > 0:
                    cumulative_att = mean_post_period_att * post_period_count
            except (TypeError, ValueError):
                pass
    # Fallback: when we have mean but no post count from df, use mean as-is (cumulative unknown)
    if np.isfinite(mean_post_period_att) and not np.isfinite(cumulative_att) and post_period_count > 0:
        cumulative_att = mean_post_period_att * post_period_count
    # Legacy alias for downstream code that expects total_effect
    total_effect = mean_post_period_att
    # Mismatch warning: skip for DID — regression-based ATT from diagnostics is primary; pickle/CSV may differ.
    if estimator != "DID":
        diag_att = np.nan
        if diag:
            eff = diag.get("treatment_effect_aggregate") or diag.get("treatment_effect")
            if eff is not None:
                try:
                    diag_att = float(eff)
                except (TypeError, ValueError):
                    pass
        if np.isfinite(mean_post_period_att) and np.isfinite(diag_att):
            diff = abs(mean_post_period_att - diag_att)
            tol = 1e-4 * max(abs(mean_post_period_att), 1.0)
            if diff > tol:
                warnings.warn(
                    f"ATT mismatch: {estimator} {dataset_filter or 'unknown'}: canonical mean ATT={mean_post_period_att:,.0f}, "
                    f"diagnostics={diag_att:,.0f}, diff={diff:,.0f}",
                    stacklevel=2,
                )
    n_treated = len(treated_geos) if treated_geos else 1
    ate_val = mean_post_period_att / n_treated if np.isfinite(mean_post_period_att) else np.nan

    # SyntheticDID: Treated vs synthetic time series
    if estimator == "SyntheticDID":
        fig, ax1 = plt.subplots(figsize=(10, 6))
        title_suffix = f" ({estimator})" + (f" — {dataset_filter}" if dataset_filter else "")

        ax1.axvline(treatment_start_dt, color="gray", ls="--", lw=1.5, label="Treatment start", zorder=1)
        y_vals = pd.to_numeric(df["y"], errors="coerce") if "y" in df.columns else pd.Series(dtype=float)
        y_hat_vals = pd.to_numeric(df["y_hat"], errors="coerce") if "y_hat" in df.columns else pd.Series(dtype=float)
        if y_vals.notna().any():
            ax1.plot(dts, y_vals, color="red", lw=2.5, label="Treated (actual)", zorder=2)
        if y_hat_vals.notna().any():
            ax1.plot(dts, y_hat_vals, color="green", ls="--", lw=2, label="Synthetic counterfactual", zorder=2)
        if control_series is not None and control_series.notna().any():
            ax1.plot(dts, control_series.values, color="gray", lw=1, alpha=0.5, label="Control (reference)", zorder=0)
        ax1.set_title("Synthetic DID" + title_suffix)
        ax1.legend(loc="best", fontsize=11)

        # SDID diagnostics: single source, use diagnostics from model (donor weights) when available.
        # R2_pre: primary pre-fit quality diagnostic. effective_donors: donor concentration (not fit quality).
        # Weak R2_pre + high effective_donors = synthetic control is broad but not matching treated dynamics well.
        r2_pre = np.nan
        pre_rmse = np.nan
        pre_rmse_pct = np.nan
        pre_mask = df["dt"] < treatment_start_dt
        if pre_mask.sum() >= 5 and "y" in df.columns and "y_hat" in df.columns:
            y_pre = pd.to_numeric(df.loc[pre_mask, "y"], errors="coerce").values
            y_hat_pre = pd.to_numeric(df.loc[pre_mask, "y_hat"], errors="coerce").values
            var_y = float(np.nanvar(y_pre))
            mean_y_pre = float(np.nanmean(y_pre))
            if var_y > 0:
                resid = y_pre - y_hat_pre
                var_resid = float(np.nanvar(resid))
                r2_pre = 1.0 - var_resid / var_y
                pre_rmse = float(np.sqrt(var_resid))
            if mean_y_pre > 0 and np.isfinite(pre_rmse):
                pre_rmse_pct = pre_rmse / mean_y_pre

        # Donor weights from diagnostics (eff_n_omega = 1/sum(weights^2))
        eff_n_omega = np.nan
        donor_weights = []
        donor_names = []
        if diag and "eff_n_omega" in diag:
            eff_n_omega = float(diag["eff_n_omega"])
        if diag and "donor_weights" in diag and "donor_names" in diag:
            donor_weights = diag.get("donor_weights", [])
            donor_names = diag.get("donor_names", [])
            if len(donor_weights) != len(donor_names):
                donor_weights, donor_names = [], []

        # ATT CI: CSV first, diagnostics last. Never derive from y_lower/y_upper (outcome-space bounds).
        att_ci_lb = att_ci_ub = np.nan
        if key in csvs:
            sdf = pd.read_csv(csvs[key])
            if dataset_filter and "Cloud" in sdf.columns:
                sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            if "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns:
                att_ci_lb = pd.to_numeric(sdf["Effect Lower"], errors="coerce").mean()
                att_ci_ub = pd.to_numeric(sdf["Effect Upper"], errors="coerce").mean()
            elif "Absolute Effect" in sdf.columns and "95 CI" in sdf.columns:
                est = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
                half = pd.to_numeric(sdf["95 CI"], errors="coerce").mean() / 2
                att_ci_lb = est - half
                att_ci_ub = est + half
        if (not np.isfinite(att_ci_lb) or not np.isfinite(att_ci_ub)) and diag:
            ci = diag.get("cumulative_ci") or diag.get("treatment_ci_aggregate") or diag.get("treatment_ci")
            if ci is not None and isinstance(ci, (list, tuple)) and len(ci) >= 2:
                att_ci_lb = float(ci[0]) if ci[0] is not None else np.nan
                att_ci_ub = float(ci[1]) if ci[1] is not None else np.nan

        # SDID: compact diagnostics box (left center). 3–4 high-value metrics only.
        # Donor weights, pre-RMSE, placebo details → console/table, not on figure.
        # Primary: Cumulative ATT. Secondary: Mean post-period ATT.
        lines = []
        if np.isfinite(cumulative_att):
            lines.append(f"Cumulative ATT: {cumulative_att:,.0f}")
        if np.isfinite(mean_post_period_att) and (not np.isfinite(cumulative_att) or post_period_count > 1):
            lines.append(f"Mean post-period ATT: {mean_post_period_att:,.0f}")
        if np.isfinite(att_ci_lb) and np.isfinite(att_ci_ub):
            lines.append(f"ATT 95% CI (per period): [{att_ci_lb:,.0f}, {att_ci_ub:,.0f}]")
            if np.isfinite(mean_post_period_att) and (mean_post_period_att < att_ci_lb or mean_post_period_att > att_ci_ub):
                warnings.warn("ATT outside CI bounds — CI source mismatch", stacklevel=2)
        if np.isfinite(r2_pre):
            lines.append(f"Pre-fit R²: {r2_pre:.2f}")
        if np.isfinite(eff_n_omega):
            lines.append(f"Effective donors: {eff_n_omega:.1f}")
        pt_timing = diag.get("placebo_treatment_timing") or {}
        if lines:
            ax1.text(0.5, 0.03, "\n".join(lines), transform=ax1.transAxes, fontsize=11, va="bottom", ha="center",
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="wheat", alpha=0.9))

        fig.tight_layout()
        base_name = "did_estimate_sdid"
        fig.savefig(os.path.join(save_dir, f"{base_name}.png"), dpi=150, bbox_inches="tight")
        plt.close(fig)
        pv = np.nan
        if key in csvs:
            sdf = pd.read_csv(csvs[key])
            if dataset_filter and "Cloud" in sdf.columns:
                sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            pv_col = next((c for c in ["p-value", "P-Value"] if c in sdf.columns), None)
            pv = pd.to_numeric(sdf[pv_col], errors="coerce").mean() if pv_col and pv_col in sdf.columns else np.nan
        if np.isfinite(cumulative_att) or np.isfinite(mean_post_period_att):
            row = {"ATE": round(ate_val), "Cumulative ATT": round(cumulative_att) if np.isfinite(cumulative_att) else "", "Mean post-period ATT": round(mean_post_period_att) if np.isfinite(mean_post_period_att) else "", "P-Value": round(pv, 4) if np.isfinite(pv) else ""}
            pd.DataFrame([row]).to_csv(os.path.join(save_dir, f"{base_name}_table.csv"), index=False)
        dataset_key = dataset_filter or (str(key[1]) if isinstance(key, (list, tuple)) and len(key) > 1 else str(key))
        r2_str = f"{r2_pre:.2f}" if np.isfinite(r2_pre) else "n/a"
        eff_str = f"{eff_n_omega:.1f}" if np.isfinite(eff_n_omega) else "n/a"
        parts = [f"dataset={dataset_key}", f"R2_pre={r2_str}", f"effective_donors={eff_str}"]
        if pt_timing:
            pts = ",".join(f"{k.replace('att_', '').replace('_earlier', '')}={v}" for k, v in pt_timing.items())
            parts.append(f"placebo_ATT({pts})")
        if np.isfinite(pre_rmse_pct):
            parts.append(f"pre_rmse_pct={pre_rmse_pct:.2%}")
        elif np.isfinite(pre_rmse):
            parts.append(f"pre_rmse={pre_rmse:.1f}")
        if donor_weights and donor_names:
            sorted_pairs = sorted(zip(donor_weights, donor_names), key=lambda x: -x[0])[:5]
            top_str = ",".join(f"{str(n)[:10]}:{w:.2f}" for w, n in sorted_pairs)
            parts.append(f"top_donors=[{top_str}]")
        print(f"  SyntheticDID diagnostics: {', '.join(parts)}")
        print(f"  Saved: {save_dir}/{base_name}.png (+ table if CSV present)")
        return

    # Classic DID diagram: conceptual x-axis (no dates), A,B,C,D,CF
    # A=pre treated, B=pre control, C=post treated actual, D=post control, CF=post counterfactual
    pre_mask = ~post_mask

    # Key points: A=pre treated, B=pre control, C=post treated, D=post control, CF=post counterfactual
    # DID: CF = A + (D - B) (classic parallel trends). SDID: use model's y_hat (synthetic counterfactual).
    A = B = C = D = CF = np.nan
    if "y" in df.columns and df["y"].notna().any():
        y_vals = pd.to_numeric(df["y"], errors="coerce")
        if pre_mask.any():
            A = float(y_vals.loc[pre_mask].mean())
        if post_mask.any():
            C = float(y_vals.loc[post_mask].mean())  # post treated actual
    if control_series is not None and control_series.notna().any():
        if pre_mask.any():
            B = float(control_series.loc[pre_mask].mean())
        if post_mask.any():
            D = float(control_series.loc[post_mask].mean())
    # Fallback 1: use control endpoints from diagnostics when control_series unavailable
    if (not np.isfinite(B) or not np.isfinite(D)) and diag:
        b_diag = diag.get("control_pre_mean")
        d_diag = diag.get("control_post_mean")
        if b_diag is not None:
            B = float(b_diag)
        if d_diag is not None:
            D = float(d_diag)
    # Fallback 2: load DID data and compute B, D directly (works when diagnostics lack control or data path differs)
    if (not np.isfinite(B) or not np.isfinite(D)) and control_geos and estimator == "DID":
        B_fb, D_fb = _compute_control_endpoints(
            base_dir, treatment_start_dt, treatment_end_dt, value_col, control_geos, dataset_filter
        )
        if np.isfinite(B_fb):
            B = B_fb
        if np.isfinite(D_fb):
            D = D_fb
    # SyntheticDID: use model's y_hat so visual gap = model estimate
    if estimator == "SyntheticDID" and "y_hat" in df.columns and post_mask.any():
        y_hat_vals = pd.to_numeric(df.loc[post_mask, "y_hat"], errors="coerce").dropna()
        if len(y_hat_vals):
            CF = float(y_hat_vals.mean())
    # DID counterfactual constructed via parallel trends assumption: treated_pre + (control_post - control_pre)
    if not np.isfinite(CF) and np.isfinite(A) and np.isfinite(B) and np.isfinite(D):
        CF = float(A + (D - B))
    # Fallback when control data missing: CF = mean post y_hat. Chart is no longer pure A/B/C/D schematic.
    if not np.isfinite(CF) and "y_hat" in df.columns and post_mask.any():
        y_hat_vals = pd.to_numeric(df.loc[post_mask, "y_hat"], errors="coerce").dropna()
        if len(y_hat_vals):
            CF = float(y_hat_vals.mean())

    # Conceptual x-axis: 0=pre, 0.5=intervention, 1=post (no dates)
    x_pre, x_int, x_post = 0.0, 0.5, 1.0

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axvline(x_int, color="steelblue", ls="-", lw=2, zorder=1)

    # Treated (red): A -> C
    if np.isfinite(A) and np.isfinite(C):
        ax.plot([x_pre, x_post], [A, C], color="red", lw=2.5, label="Treated (actual)", zorder=2)
        ax.plot(x_pre, A, "o", color="steelblue", markersize=10, zorder=3)
        ax.plot(x_post, C, "o", color="steelblue", markersize=10, zorder=3)
        ax.annotate("A", (x_pre, A), xytext=(5, 5), textcoords="offset points", fontsize=10, fontweight="bold")
        ax.annotate("C", (x_post, C), xytext=(5, 5), textcoords="offset points", fontsize=10, fontweight="bold")

    # Control (green): B -> D (from control_series or diagnostics)
    if np.isfinite(B) and np.isfinite(D):
        ax.plot([x_pre, x_post], [B, D], color="green", lw=2.5, label="Control trend (aggregated)", zorder=2)
        ax.plot(x_pre, B, "o", color="steelblue", markersize=10, zorder=3)
        ax.plot(x_post, D, "o", color="steelblue", markersize=10, zorder=3)
        ax.annotate("B", (x_pre, B), xytext=(5, -10), textcoords="offset points", fontsize=10, fontweight="bold")
        ax.annotate("D", (x_post, D), xytext=(5, -10), textcoords="offset points", fontsize=10, fontweight="bold")

    # Counterfactual (dotted): DID uses parallel trends A->CF; SDID uses synthetic counterfactual (no A->CF line interpretation)
    cf_label = "Synthetic counterfactual" if estimator == "SyntheticDID" else "Treated counterfactual"
    if np.isfinite(A) and np.isfinite(CF):
        ax.plot([x_pre, x_post], [A, CF], color="green", ls="--", lw=2, label=cf_label, zorder=2)
        ax.plot(x_post, CF, "o", color="white", markeredgecolor="steelblue", markersize=10, markeredgewidth=2, zorder=3)
        ax.annotate("CF", (x_post, CF), xytext=(5, 5), textcoords="offset points", fontsize=10, fontweight="bold")

    # β annotations: DID parallel-trends decomposition only (not applicable to SyntheticDID)
    if estimator == "DID":
        if np.isfinite(B) and np.isfinite(D):
            ax.plot([x_post, x_post], [B, D], "k--", lw=1.5, alpha=0.7, label=r"$\beta_1$: change in control")
            ax.annotate(r"$\beta_1$", (x_post, (B + D) / 2), xytext=(8, 0), textcoords="offset points", fontsize=9)
            ax.plot([x_pre, x_post], [B, B], "k:", lw=1.5, alpha=0.6)
        if np.isfinite(A) and np.isfinite(B):
            ax.plot([x_pre, x_pre], [B, A], "k--", lw=1.5, alpha=0.7, label=r"$\beta_2$: baseline diff")
            ax.annotate(r"$\beta_2$", (x_pre, (A + B) / 2), xytext=(8, 0), textcoords="offset points", fontsize=9)
        if np.isfinite(CF) and np.isfinite(C):
            ax.plot([x_post, x_post], [CF, C], "k--", lw=1.5, alpha=0.7, label=r"$\beta_3$: weekly ATE")
            ax.annotate(r"$\beta_3$", (x_post, (CF + C) / 2), xytext=(8, 0), textcoords="offset points", fontsize=9)

    ax.set_xlim(-0.05, 1.05)
    ax.set_xticks([0.25, 0.75])
    ax.set_xticklabels(["Pre-intervention", "Post-intervention"])
    ax.set_ylabel("Outcome (weekly average)")
    title_suffix = f" ({estimator})" + (f" — {dataset_filter}" if dataset_filter else "")
    main_title = "Synthetic DID" if estimator == "SyntheticDID" else "Difference-in-Differences"
    ax.set_title(main_title + title_suffix)
    ax.legend(loc="best", fontsize=11)  # Called after β annotations so legend includes β1/β2/β3
    # DID: single gold annotation box (left). 3 lines max: Cumulative ATT, 95% CI, Pre-trends.
    # Values from top-level DID outputs: cumulative_att, treatment_ci_aggregate, parallel_trends_violated.
    lines = []
    pt_violated = False
    if estimator == "DID" and diag is not None:
        pt_violated = bool(diag.get("parallel_trends_violated") or
                          (diag.get("parallel_trends_test") or {}).get("parallel_trends_violated", False))

    # CI: Phase 7 — DID uses CSV only (path-based); no treatment_ci_aggregate from diagnostics.
    att_ci_lb = att_ci_ub = np.nan
    if estimator == "DID":
        # DID: use CSV Effect Lower/Upper (path-based, cumulative). Phase 7: require cumulative CI when n_post > 1.
        if key in csvs:
            sdf = pd.read_csv(csvs[key])
            if dataset_filter and "Cloud" in sdf.columns:
                sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            if "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns and len(sdf) > 0:
                att_ci_lb = pd.to_numeric(sdf["Effect Lower"], errors="coerce").mean()
                att_ci_ub = pd.to_numeric(sdf["Effect Upper"], errors="coerce").mean()
                ci_scale = str(sdf["ci_scale"].iloc[0]).strip().lower() if "ci_scale" in sdf.columns else ""
                if np.isfinite(att_ci_lb) and np.isfinite(att_ci_ub) and post_period_count > 1 and ci_scale != "cumulative":
                    warnings.warn(
                        f"DID plot: CI exists but ci_scale='{ci_scale}' (expected 'cumulative') for n_post={post_period_count}. Skipping CI display.",
                        stacklevel=2,
                    )
                    att_ci_lb = att_ci_ub = np.nan
            elif "Absolute Effect" in sdf.columns and "95 CI" in sdf.columns:
                est = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
                half = pd.to_numeric(sdf["95 CI"], errors="coerce").mean() / 2
                att_ci_lb = est - half
                att_ci_ub = est + half
    else:
        effect_scale = (diag or {}).get("effect_scale", "aggregate")
        n_panel = (diag or {}).get("n_treated_units_in_panel", 1)
        scale_ci_to_aggregate = effect_scale == "per_geo" and n_panel > 1
        if diag:
            # Prefer path-based cumulative_ci; avoid mis-scaling per-period aggregates for TROP-like outputs.
            ci = diag.get("cumulative_ci") or diag.get("treatment_ci_aggregate") or diag.get("treatment_ci")
            if ci is not None and isinstance(ci, (list, tuple)) and len(ci) >= 2:
                att_ci_lb = float(ci[0]) if ci[0] is not None else np.nan
                att_ci_ub = float(ci[1]) if ci[1] is not None else np.nan
                if scale_ci_to_aggregate:
                    att_ci_lb = att_ci_lb * n_panel
                    att_ci_ub = att_ci_ub * n_panel
        if (not np.isfinite(att_ci_lb) or not np.isfinite(att_ci_ub)) and key in csvs:
            sdf = pd.read_csv(csvs[key])
            if dataset_filter and "Cloud" in sdf.columns:
                sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            if "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns:
                att_ci_lb = pd.to_numeric(sdf["Effect Lower"], errors="coerce").mean()
                att_ci_ub = pd.to_numeric(sdf["Effect Upper"], errors="coerce").mean()
            elif "Absolute Effect" in sdf.columns and "95 CI" in sdf.columns:
                est = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
                half = pd.to_numeric(sdf["95 CI"], errors="coerce").mean() / 2
                att_ci_lb = est - half
                att_ci_ub = est + half
        # Legacy: scale per-period diagnostic CI to cumulative when n_post>1. Skip if cumulative_ci is present.
        # Never apply × n_post for TROP (bootstrap CI is already cumulative).
        if (
            estimator != "Trop"
            and np.isfinite(att_ci_lb)
            and np.isfinite(att_ci_ub)
            and np.isfinite(cumulative_att)
            and post_period_count > 1
            and diag
            and (diag.get("treatment_ci_aggregate") or diag.get("treatment_ci"))
            and not diag.get("cumulative_ci")
        ):
            att_ci_lb = att_ci_lb * post_period_count
            att_ci_ub = att_ci_ub * post_period_count

    # DID gold box: weekly ATE (= β₃, what the diagram shows) + cumulative ATT (total test-period effect).
    lines.append(f"Weekly ATE (β₃): {mean_post_period_att:,.0f}" if np.isfinite(mean_post_period_att) else "Weekly ATE: N/A")
    lines.append(f"Cumulative ATT (total test period): {cumulative_att:,.0f}" if np.isfinite(cumulative_att) else "Cumulative ATT: N/A")
    if np.isfinite(att_ci_lb) and np.isfinite(att_ci_ub):
        lines.append(f"95% CI (cumulative): [{att_ci_lb:,.0f}, {att_ci_ub:,.0f}]")
    else:
        lines.append("95% CI: N/A")
    pt_label = "violated" if pt_violated else "pass"
    pt_color = "red" if pt_violated else "black"

    if lines:
        # Main box: Cumulative ATT and 95% CI only (standard text bbox, auto-sizes)
        main_text = "\n".join(lines)
        ax.text(0.02, 0.62, main_text, transform=ax.transAxes, fontsize=10, va="top", ha="left",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.9))
        # Parallel trends: one line directly below, red when violated / dark when pass (no bbox)
        ax.text(0.02, 0.52, f"Parallel trends: {pt_label}", transform=ax.transAxes, fontsize=10, va="top", ha="left",
                color=pt_color)
    fig.tight_layout()
    base_name = "did_estimate_sdid" if estimator == "SyntheticDID" else "did_estimate"
    fig.savefig(os.path.join(save_dir, f"{base_name}.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    pv = np.nan
    if key in csvs:
        sdf = pd.read_csv(csvs[key])
        if dataset_filter and "Cloud" in sdf.columns:
            sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
        pv_col = next((c for c in ["p-value", "P-Value"] if c in sdf.columns), None)
        pv = pd.to_numeric(sdf[pv_col], errors="coerce").mean() if pv_col and pv_col in sdf.columns else np.nan
    if np.isfinite(cumulative_att) or np.isfinite(mean_post_period_att):
        row = {"ATE": round(ate_val), "Cumulative ATT": round(cumulative_att) if np.isfinite(cumulative_att) else "", "Mean post-period ATT": round(mean_post_period_att) if np.isfinite(mean_post_period_att) else "", "P-Value": round(pv, 4) if np.isfinite(pv) else ""}
        table_path = os.path.join(save_dir, f"{base_name}_table.csv")
        pd.DataFrame([row]).to_csv(table_path, index=False)
        # Phase 6: validate did_estimate_table vs summary_stats_df
        if estimator == "DID" and key in csvs:
            try:
                sdf = pd.read_csv(csvs[key])
                if dataset_filter and "Cloud" in sdf.columns:
                    sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
                csv_att = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean() if "Absolute Effect" in sdf.columns else np.nan
                if np.isfinite(cumulative_att) and np.isfinite(csv_att) and abs(float(cumulative_att) - float(csv_att)) > 0.5:
                    print(f"  WARNING: did_estimate ATT ({cumulative_att:,.0f}) != summary_stats_df ATT ({csv_att:,.0f})")
            except Exception:
                pass
    print(f"  Saved: {save_dir}/{base_name}.png (+ table if CSV present)")


def _plot_family_timeseries(
    pickles: dict,
    csvs: dict,
    estimators: list[str],
    title: str,
    filename: str,
    save_dir: str,
    dataset_filter: str | None = None,
    treatment_start_date: str | None = None,
    treatment_end_date: str | None = None,
    pre_period_weeks: int | None = None,
    legend_loc: str = "best",
    legend_font_weight: str = "bold",
    exclude_pairs: set[tuple[str, str]] | None = None,
    allow_pairs: frozenset[tuple[str, str]] | None = None,
    color_overrides: dict[tuple[str, str], str] | None = None,
) -> None:
    """One time-series plot: multiple lines (one per inference x estimator in list), with CIs; plus summary table.
    When allow_pairs is set, only (inf, est) in that set are plotted (lines, CIs, legend, table).
    Otherwise uses estimators + exclude_pairs. Ensures every CI band has a corresponding line and legend entry."""
    os.makedirs(save_dir, exist_ok=True)
    _bg = "#EAEAF2"  # Seaborn darkgrid-style axes background (light purple-grey)
    fig, ax = plt.subplots(figsize=(10, 5), facecolor="white")
    ax.set_facecolor(_bg)
    ax.grid(True, axis="both", color="white", alpha=0.35, linestyle="-")
    ax.axhline(0, color="black", ls="--", lw=0.8)
    table_rows = []
    added_keys: set[tuple] = set()
    treatment_start_dt: pd.Timestamp | None = None
    treatment_end_dt: pd.Timestamp | None = None

    def _bounds_from_csv(sdf: pd.DataFrame) -> tuple[float, float]:
        """Get (lb, ub) from CSV: prefer Effect Lower/Upper; else derive from Absolute Effect and 95 CI (full width).
        Always returns ordered (lower, upper) with lower <= upper."""
        lb = ub = np.nan
        if "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns:
            lb = pd.to_numeric(sdf["Effect Lower"], errors="coerce").mean()
            ub = pd.to_numeric(sdf["Effect Upper"], errors="coerce").mean()
        elif "Absolute Effect" in sdf.columns and "95 CI" in sdf.columns:
            est = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
            ci = pd.to_numeric(sdf["95 CI"], errors="coerce").iloc[0] if len(sdf) else np.nan
            if np.isfinite(est) and np.isfinite(ci):
                half = ci / 2.0
                lb, ub = est - half, est + half
        lb, ub = float(lb) if np.isfinite(lb) else np.nan, float(ub) if np.isfinite(ub) else np.nan
        if np.isfinite(lb) and np.isfinite(ub):
            lb, ub = min(lb, ub), max(lb, ub)
        return lb, ub

    def _add_from_csv(inf: str, est: str) -> bool:
        """Add row from CSV when pickle has no weekly data. Returns True if added.
        CSV Absolute Effect and Effect Lower/Upper are cumulative for TBR/SCM family (from readout notebook)."""
        if (inf, est) not in csvs:
            return False
        sdf = pd.read_csv(csvs[(inf, est)])
        if dataset_filter and "Cloud" in sdf.columns:
            sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
        if "Absolute Effect" not in sdf.columns:
            return False
        est_sum = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
        lb, ub = _bounds_from_csv(sdf)
        if np.isfinite(lb) and np.isfinite(ub) and lb > ub:
            lb, ub = ub, lb
        label = METHOD_DISPLAY_NAMES.get((inf, est), f"{est} ({inf})")
        if inf == "Placebo":
            bnd_src = "effect_ci_inversion" if ("Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns) else "derived_95ci"
            valid = np.isfinite(est_sum) and np.isfinite(lb) and np.isfinite(ub) and lb <= est_sum <= ub
            print(f"  Placebo table {label} (from CSV): est={round(est_sum) if np.isfinite(est_sum) else 'nan'}, "
                  f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                  f"lb<=est<=ub={valid}, est_src=csv_cumulative, bnd_src={bnd_src} (scale=cumulative)")
        elif inf == "TimeSeriesKfold":
            scale = "cumulative_tsk_direct" if ("Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns) else "weekly_sum_fallback"
            valid = np.isfinite(est_sum) and np.isfinite(lb) and np.isfinite(ub) and lb <= est_sum <= ub
            print(f"  TSK table {label} (from CSV): est={round(est_sum) if np.isfinite(est_sum) else 'nan'}, "
                  f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                  f"lb<=est<=ub={valid}, scale={scale}")
        elif inf == "BlockResidualBootstrap":
            scale = "cumulative_brb_direct" if ("Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns) else "weekly_sum_fallback"
            valid = np.isfinite(est_sum) and np.isfinite(lb) and np.isfinite(ub) and lb <= est_sum <= ub
            print(f"  BRB table {label} (from CSV): est={round(est_sum) if np.isfinite(est_sum) else 'nan'}, "
                  f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                  f"lb<=est<=ub={valid}, scale={scale}")
        table_rows.append({
            "Model": label,
            "Estimate": round(est_sum),
            "Lower Bound": round(lb) if np.isfinite(lb) else "",
            "Upper Bound": round(ub) if np.isfinite(ub) else "",
        })
        return True

    def _sort_key(item):
        (inf, est) = item[0]
        return METHOD_DISPLAY_NAMES.get((inf, est), f"{est} ({inf})")

    # Filter before any plotting: use allow_pairs (explicit whitelist) or estimators + exclude_pairs
    if allow_pairs:
        pickle_items = [(k, v) for k, v in pickles.items() if k in allow_pairs]
    else:
        excluded = exclude_pairs or set()
        pickle_items = [(k, v) for k, v in pickles.items() if k[1] in estimators and k not in excluded]
    pickle_items.sort(key=_sort_key)
    colors = plt.cm.tab10(np.linspace(0, 1, 12))
    # BRB-specific colors (unique, not reused by tab10) for visual dominance
    _brb_colors = {
        "TBR-BRB": "#c0392b",
        "TBRRidge-BRB": "#2980b9",
        "AugSynthCVXPY-BRB": "#27ae60",
        "SyntheticControlCVXPY-BRB": "#8e44ad",
    }
    labels_plotted: list[str] = []
    labels_with_ci: list[str] = []
    plot_items: list[dict] = []  # collect for two-pass draw: CIs first, lines after

    for item_idx, ((inf, est), path) in enumerate(pickle_items):
        weekly_dct = load_weekly_dct(path)
        df = get_first_weekly_series(weekly_dct, dataset_filter)
        if df is None or "dt" not in df.columns:
            if inf == "BlockResidualBootstrap" and df is None and dataset_filter and weekly_dct:
                keys_preview = list(weekly_dct.keys())[:5]
                print(f"  [BRB skip] {inf}_{est}: no key matches dataset_filter={dataset_filter!r}; keys={keys_preview}")
            if _add_from_csv(inf, est):
                added_keys.add((inf, est))
            continue
        df = df.copy()
        df["dt"] = pd.to_datetime(df["dt"])
        df = df.sort_values("dt").reset_index(drop=True)
        if treatment_start_dt is None:
            treatment_start_dt = (
                pd.to_datetime(treatment_start_date)
                if treatment_start_date
                else df["dt"].iloc[max(0, len(df) // 2)]
            )
        if treatment_end_dt is None and treatment_end_date:
            treatment_end_dt = pd.to_datetime(treatment_end_date)
        if pre_period_weeks is not None and treatment_start_dt is not None:
            pre_start = treatment_start_dt - pd.Timedelta(weeks=pre_period_weeks)
            df = df[df["dt"] >= pre_start].copy()
            if df.empty:
                continue
        if "effect" in df.columns:
            eff_vals = df["effect"].values
        else:
            eff_vals = (df["y"] - df["y_hat"]).values if "y_hat" in df.columns else np.zeros(len(df))
        label = METHOD_DISPLAY_NAMES.get((inf, est), f"{est} ({inf})")
        is_placebo = label.endswith("-P")
        is_brb = label.endswith("-BRB")
        color = (color_overrides or {}).get((inf, est)) or _brb_colors.get(label) or colors[item_idx % len(colors)]
        has_ci = "y_lower" in df.columns and "y_upper" in df.columns and df["y_lower"].notna().any()
        eff_lower = eff_upper = None
        post_mask = np.zeros(len(df), dtype=bool)
        dts_post = np.array([])
        if has_ci:
            y_vals = pd.to_numeric(df["y"], errors="coerce").values
            y_lower_vals = pd.to_numeric(df["y_lower"], errors="coerce").values
            y_upper_vals = pd.to_numeric(df["y_upper"], errors="coerce").values
            eff_lower_raw = y_vals - np.nan_to_num(y_upper_vals, nan=0.0)
            eff_upper_raw = y_vals - np.nan_to_num(y_lower_vals, nan=0.0)
            eff_lower = np.minimum(eff_lower_raw, eff_upper_raw)
            eff_upper = np.maximum(eff_lower_raw, eff_upper_raw)
            post_mask = (df["dt"] >= treatment_start_dt).values if treatment_start_dt is not None else np.ones(len(df), dtype=bool)
            if post_mask.any():
                dts_post = df["dt"].values[post_mask]
        plot_items.append({
            "df": df, "label": label, "color": color, "eff_vals": eff_vals,
            "is_brb": is_brb, "has_ci": has_ci and post_mask.any(),
            "eff_lower": eff_lower, "eff_upper": eff_upper, "post_mask": post_mask, "dts_post": dts_post,
            "inf": inf, "est": est,
        })
        labels_plotted.append(label)
        if has_ci and post_mask.any():
            labels_with_ci.append(label)
        added_keys.add((inf, est))
        # Table: cumulative effect over treatment window only (sum, not mean)
        # (uses df, eff_vals, inf, est, label, is_placebo from current iteration)
        # Placebo: always use CSV for estimate and bounds (cumulative inversion CI); never derive from pickle weekly bounds
        est_sum = np.nan
        lb = ub = np.nan
        placebo_bnd_src = "none"
        if is_placebo and (inf, est) in csvs:
            sdf = pd.read_csv(csvs[(inf, est)])
            if dataset_filter and "Cloud" in sdf.columns:
                sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
            if "Absolute Effect" in sdf.columns:
                est_sum = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
            lb, ub = _bounds_from_csv(sdf)
            placebo_bnd_src = "effect_ci_inversion" if ("Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns) else "derived_95ci"
        elif is_placebo:
            # Placebo without CSV: use pickle sum for estimate only; no valid CI without inversion fields
            post_mask = (df["dt"] >= treatment_start_dt).values if treatment_start_dt is not None else np.ones(len(df), dtype=bool)
            if treatment_end_dt is not None:
                post_mask = post_mask & (df["dt"] <= treatment_end_dt).values
            eff_post = np.nan_to_num(eff_vals, nan=0.0)[post_mask] if post_mask.any() else np.array([0.0])
            est_sum = float(np.sum(eff_post))
        else:
            is_tsk = label.endswith("-TSK")
            is_brb = label.endswith("-BRB")
            # TSK: prefer CSV with direct cumulative TSK fields over summed weekly pickle bounds
            if is_tsk and (inf, est) in csvs:
                sdf = pd.read_csv(csvs[(inf, est)])
                if dataset_filter and "Cloud" in sdf.columns:
                    sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
                if "Absolute Effect" in sdf.columns and "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns:
                    est_sum = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
                    lb, ub = _bounds_from_csv(sdf)
                    scale = "cumulative_tsk_direct"
                else:
                    post_mask = (df["dt"] >= treatment_start_dt).values if treatment_start_dt is not None else np.ones(len(df), dtype=bool)
                    if treatment_end_dt is not None:
                        post_mask = post_mask & (df["dt"] <= treatment_end_dt).values
                    eff_post = np.nan_to_num(eff_vals, nan=0.0)[post_mask] if post_mask.any() else np.array([0.0])
                    est_sum = float(np.sum(eff_post))
                    lb, ub = np.nan, np.nan
                    if "y_lower" in df.columns and "y_upper" in df.columns and treatment_start_dt is not None:
                        post_mask_ci = (df["dt"] >= treatment_start_dt).values
                        if treatment_end_dt is not None:
                            post_mask_ci = post_mask_ci & (df["dt"] <= treatment_end_dt).values
                        if post_mask_ci.any():
                            y_vals = pd.to_numeric(df.loc[post_mask_ci, "y"], errors="coerce").values
                            y_l = pd.to_numeric(df.loc[post_mask_ci, "y_lower"], errors="coerce").values
                            y_u = pd.to_numeric(df.loc[post_mask_ci, "y_upper"], errors="coerce").values
                            el_raw = y_vals - np.nan_to_num(y_u, nan=0.0)
                            eu_raw = y_vals - np.nan_to_num(y_l, nan=0.0)
                            lb = float(np.nansum(np.minimum(el_raw, eu_raw)))
                            ub = float(np.nansum(np.maximum(el_raw, eu_raw)))
                    scale = "weekly_sum_fallback"
                valid = np.isfinite(lb) and np.isfinite(ub) and lb <= est_sum <= ub
                print(f"  TSK table {label}: est={round(est_sum) if np.isfinite(est_sum) else 'nan'}, "
                      f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                      f"lb<=est<=ub={valid}, scale={scale}")
            # BRB: prefer CSV with direct cumulative BRB fields over summed weekly pickle bounds
            elif is_brb and (inf, est) in csvs:
                sdf = pd.read_csv(csvs[(inf, est)])
                if dataset_filter and "Cloud" in sdf.columns:
                    sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
                if "Absolute Effect" in sdf.columns and "Effect Lower" in sdf.columns and "Effect Upper" in sdf.columns:
                    est_sum = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
                    lb, ub = _bounds_from_csv(sdf)
                    scale = "cumulative_brb_direct"
                else:
                    post_mask = (df["dt"] >= treatment_start_dt).values if treatment_start_dt is not None else np.ones(len(df), dtype=bool)
                    if treatment_end_dt is not None:
                        post_mask = post_mask & (df["dt"] <= treatment_end_dt).values
                    eff_post = np.nan_to_num(eff_vals, nan=0.0)[post_mask] if post_mask.any() else np.array([0.0])
                    est_sum = float(np.sum(eff_post))
                    lb, ub = np.nan, np.nan
                    if "y_lower" in df.columns and "y_upper" in df.columns and treatment_start_dt is not None:
                        post_mask_ci = (df["dt"] >= treatment_start_dt).values
                        if treatment_end_dt is not None:
                            post_mask_ci = post_mask_ci & (df["dt"] <= treatment_end_dt).values
                        if post_mask_ci.any():
                            y_vals = pd.to_numeric(df.loc[post_mask_ci, "y"], errors="coerce").values
                            y_l = pd.to_numeric(df.loc[post_mask_ci, "y_lower"], errors="coerce").values
                            y_u = pd.to_numeric(df.loc[post_mask_ci, "y_upper"], errors="coerce").values
                            el_raw = y_vals - np.nan_to_num(y_u, nan=0.0)
                            eu_raw = y_vals - np.nan_to_num(y_l, nan=0.0)
                            lb = float(np.nansum(np.minimum(el_raw, eu_raw)))
                            ub = float(np.nansum(np.maximum(el_raw, eu_raw)))
                    scale = "weekly_sum_fallback"
                valid = np.isfinite(lb) and np.isfinite(ub) and lb <= est_sum <= ub
                print(f"  BRB table {label}: est={round(est_sum) if np.isfinite(est_sum) else 'nan'}, "
                      f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                      f"lb<=est<=ub={valid}, scale={scale}")
            else:
                post_mask = (df["dt"] >= treatment_start_dt).values if treatment_start_dt is not None else np.ones(len(df), dtype=bool)
                if treatment_end_dt is not None:
                    post_mask = post_mask & (df["dt"] <= treatment_end_dt).values
                eff_post = np.nan_to_num(eff_vals, nan=0.0)[post_mask] if post_mask.any() else np.array([0.0])
                est_sum = float(np.sum(eff_post))
                lb = ub = np.nan
                # Bounds: prefer direct cumulative CI from CSV; else sum pointwise bounds over treatment window (approximation)
                if "y_lower" in df.columns and "y_upper" in df.columns and treatment_start_dt is not None:
                    post_mask_ci = (df["dt"] >= treatment_start_dt).values
                    if treatment_end_dt is not None:
                        post_mask_ci = post_mask_ci & (df["dt"] <= treatment_end_dt).values
                    if post_mask_ci.any():
                        y_vals = pd.to_numeric(df.loc[post_mask_ci, "y"], errors="coerce").values
                        y_l = pd.to_numeric(df.loc[post_mask_ci, "y_lower"], errors="coerce").values
                        y_u = pd.to_numeric(df.loc[post_mask_ci, "y_upper"], errors="coerce").values
                        el_raw = y_vals - np.nan_to_num(y_u, nan=0.0)
                        eu_raw = y_vals - np.nan_to_num(y_l, nan=0.0)
                        # Sum pointwise bounds (approximation; weekly intervals may be correlated)
                        lb = float(np.nansum(np.minimum(el_raw, eu_raw)))
                        ub = float(np.nansum(np.maximum(el_raw, eu_raw)))
                if not (np.isfinite(lb) and np.isfinite(ub)) and (inf, est) in csvs:
                    sdf = pd.read_csv(csvs[(inf, est)])
                    if dataset_filter and "Cloud" in sdf.columns:
                        sdf = sdf[sdf["Cloud"].astype(str).str.upper() == str(dataset_filter).upper()]
                    # CSV Absolute Effect and Effect Lower/Upper are cumulative for TBR/SCM family (from readout notebook)
                    if "Absolute Effect" in sdf.columns:
                        est_sum = pd.to_numeric(sdf["Absolute Effect"], errors="coerce").mean()
                    lb, ub = _bounds_from_csv(sdf)
        # Placebo: enforce lb <= ub, then validate and log
        if np.isfinite(lb) and np.isfinite(ub) and lb > ub:
            lb, ub = ub, lb
        if is_placebo:
            est_src = "csv_cumulative" if (inf, est) in csvs else "pickle_sum_fallback"
            bnd_src = placebo_bnd_src if is_placebo else "n/a"
            valid = np.isfinite(est_sum) and np.isfinite(lb) and np.isfinite(ub) and lb <= est_sum <= ub
            print(f"  Placebo table {label}: est={round(est_sum) if np.isfinite(est_sum) else 'nan'}, "
                  f"lb={round(lb) if np.isfinite(lb) else 'nan'}, ub={round(ub) if np.isfinite(ub) else 'nan'}, "
                  f"lb<=est<=ub={valid}, est_src={est_src}, bnd_src={bnd_src} (scale=cumulative)")
        table_rows.append({
            "Model": label,
            "Estimate": round(est_sum),
            "Lower Bound": round(lb) if np.isfinite(lb) else "",
            "Upper Bound": round(ub) if np.isfinite(ub) else "",
        })

    # Validation: compare K vs P effect values for same estimator (e.g. AugSynthCVXPY-K vs AugSynthCVXPY-P)
    for base in ("AugSynthCVXPY", "SyntheticControlCVXPY", "TBRRidge"):
        k_item = next((p for p in plot_items if p["label"] == f"{base}-K"), None)
        p_item = next((p for p in plot_items if p["label"] == f"{base}-P"), None)
        if k_item and p_item:
            k_sum = float(np.nansum(np.nan_to_num(k_item["eff_vals"], nan=0.0)))
            p_sum = float(np.nansum(np.nan_to_num(p_item["eff_vals"], nan=0.0)))
            diff = abs(k_sum - p_sum)
            same = np.allclose(k_item["eff_vals"], p_item["eff_vals"], equal_nan=True)
            print(f"  [validate K vs P] {base}-K: sum={k_sum:.1f}, {base}-P: sum={p_sum:.1f}, diff={diff:.1f}, identical={same}")
    # Two-pass draw: CIs first (lower alpha), then lines (BRB visually dominant)
    for item in plot_items:
        if item["has_ci"]:
            alpha = 0.06 if not item["is_brb"] else 0.10
            ax.fill_between(
                item["dts_post"],
                item["eff_lower"][item["post_mask"]],
                item["eff_upper"][item["post_mask"]],
                alpha=alpha, color=item["color"], zorder=1,
            )
    # Draw non-Placebo first, then Placebo on top (higher zorder) so both are visible when values differ
    for item in plot_items:
        lw = 1.5
        is_placebo = item["label"].endswith("-P")
        z = 12 if is_placebo else (10 if item["is_brb"] else 5)  # Placebo on top
        ls = (0, (4, 2)) if is_placebo else "-"  # dashed for Placebo (more visible than "--")
        ax.plot(item["df"]["dt"], item["eff_vals"], color=item["color"], lw=lw, ls=ls, label=item["label"], zorder=z)

    # Debug: print labels that receive line plot vs fill_between
    print(f"  [family plot] Line plot labels: {labels_plotted}")
    print(f"  [family plot] Fill_between labels: {labels_with_ci}")
    brb_in_lines = [l for l in labels_plotted if l.endswith("-BRB")]
    if brb_in_lines:
        print(f"  [family plot] BRB in line list: {brb_in_lines}")

    # Invariant: CI bands must equal plotted estimators that have CIs
    ci_only = set(labels_with_ci) - set(labels_plotted)
    if ci_only:
        print(f"  [TBR/SCM family] WARNING: CI shading for labels not in legend: {ci_only}")

    # Add estimators that have CSV but no usable pickle (e.g. empty weekly_dct)
    if allow_pairs:
        csv_items = [(k, v) for k, v in csvs.items() if k in allow_pairs and k not in added_keys]
    else:
        excluded = exclude_pairs or set()
        csv_items = [(k, v) for k, v in csvs.items() if k[1] in estimators and k not in added_keys and k not in excluded]
    csv_items.sort(key=_sort_key)
    for (inf, est), _ in csv_items:
        _add_from_csv(inf, est)
    if not table_rows:
        return
    if treatment_start_dt is not None:
        ax.axvline(treatment_start_dt, color="gray", ls="--", lw=1)
    if treatment_end_dt is not None:
        ax.axvline(treatment_end_dt, color="gray", ls="--", lw=1)
    ax.set_xlabel("Time")
    ax.set_ylabel("Effect")
    ax.set_title(title)
    ax.legend(loc=legend_loc, prop=fm.FontProperties(size=11, weight=legend_font_weight))
    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, filename), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    pd.DataFrame(table_rows).to_csv(os.path.join(save_dir, filename.replace(".png", "_table.csv")), index=False)
    print(f"  Saved: {save_dir}/{filename} and table")


def plot_tbr_family(
    pickles: dict,
    csvs: dict,
    save_dir: str,
    dataset_filter: str | None = None,
    base_dir: str | None = None,
    pre_period_weeks: int | None = None,
) -> None:
    """TBR Family of Estimators: time-series + table. Uses explicit allow list (no TSK, Conformal, etc)."""
    _plot_family_timeseries(
        pickles, csvs,
        estimators=["TBR", "TBRRidge", "Bayesian_TBR", "Bayesian_TBR_HorseShoe"],
        title="TBR Family of Estimators",
        filename="tbr_family_estimators.png",
        save_dir=save_dir,
        dataset_filter=dataset_filter,
        treatment_start_date=_get_treatment_start_date(base_dir),
        treatment_end_date=_get_treatment_end_date(base_dir),
        pre_period_weeks=pre_period_weeks,
        legend_font_weight="normal",
        allow_pairs=TBR_FAMILY_ALLOWED_PAIRS,
        color_overrides={("self", "Bayesian_TBR_HorseShoe"): "#8e44ad"},  # purple, distinct from Bayesian TBR
    )


def plot_scm_family(
    pickles: dict,
    csvs: dict,
    save_dir: str,
    dataset_filter: str | None = None,
    base_dir: str | None = None,
    pre_period_weeks: int | None = None,
) -> None:
    """SCM Family of Estimators: time-series + table. Uses explicit allow list (no TSK, Conformal, etc)."""
    _plot_family_timeseries(
        pickles, csvs,
        estimators=["AugSynthCVXPY"],
        title="SCM Family of Estimators",
        filename="scm_family_estimators.png",
        save_dir=save_dir,
        dataset_filter=dataset_filter,
        treatment_start_date=_get_treatment_start_date(base_dir),
        pre_period_weeks=pre_period_weeks,
        legend_font_weight="normal",
        allow_pairs=SCM_FAMILY_ALLOWED_PAIRS,
        color_overrides={
            ("BlockResidualBootstrap", "AugSynthCVXPY"): "#27ae60",  # green, distinct from SCM-BRB
            ("BlockResidualBootstrap", "SyntheticControlCVXPY"): "#8e44ad",  # purple, distinct from AugSynthCVXPY-BRB
            ("Placebo", "SyntheticControlCVXPY"): "black",  # SCM-P in black
        },
    )


def plot_inference_family(
    pickles: dict,
    csvs: dict,
    save_dir: str,
    dataset_filter: str | None = None,
    base_dir: str | None = None,
    pre_period_weeks: int | None = None,
) -> None:
    """Inference comparison: time-series of all Kfold, TimeSeriesKfold, Conformal methods + table."""
    # Include estimators that have inference-based variants (excludes Bayesian, DID, SDID which use 'self')
    # Exclude TSK from all TBR/SCM plots
    estimators = ["TBR", "TBRRidge", "AugSynthCVXPY"]
    _tsk_exclude = {
        ("TimeSeriesKfold", "TBR"), ("TimeSeriesKfold", "TBRRidge"),
        ("TimeSeriesKfold", "AugSynthCVXPY"), ("TimeSeriesKfold", "SyntheticControlCVXPY"),
    }
    _plot_family_timeseries(
        pickles, csvs,
        estimators=estimators,
        title="Inference Comparison: Kfold vs TimeSeriesKfold vs Conformal",
        filename="inference_family_estimators.png",
        save_dir=save_dir,
        dataset_filter=dataset_filter,
        treatment_start_date=_get_treatment_start_date(base_dir),
        pre_period_weeks=pre_period_weeks,
        legend_loc="upper left",
        exclude_pairs=_tsk_exclude,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MMT grid report visualizations")
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Base output dir (where mmt_config.json and pickles live). Default: BASE_OUTPUT_DIR.",
    )
    parser.add_argument(
        "--kpi-col",
        type=str,
        default=None,
        help="Override KPI/value column (comma-separated for multiple). When not set, uses KPI_COL from script.",
    )
    parser.add_argument(
        "--did-input-path",
        type=str,
        default=None,
        help="Override path to long-format data for DID. When not set, uses mmt_datasets.pkl or mmt_config.kpi_to_input_path.",
    )
    parser.add_argument(
        "--exclude-inference",
        type=str,
        default=None,
        help="Comma-separated inference methods to exclude from all plots (e.g. UnitJackKnife,JKP).",
    )
    parser.add_argument(
        "--pre-period-weeks",
        type=int,
        default=None,
        help="Number of weeks to keep prior to test start in family timeseries plots (TBR, SCM, inference).",
    )
    args = parser.parse_args()

    global KPI_COL, DID_INPUT_LONG_PATH, BASE_OUTPUT_DIR, FIGURES_DIR, _MMT_CONFIG_CACHE, EXCLUDE_INFERENCE_FROM_PLOTS
    if args.base_dir:
        BASE_OUTPUT_DIR = args.base_dir
        _MMT_CONFIG_CACHE.clear()
    if args.kpi_col:
        parts = [p.strip() for p in args.kpi_col.split(",") if p.strip()]
        KPI_COL = parts[0] if len(parts) == 1 else parts
    else:
        # Infer KPI from base dir when path clearly indicates dataset
        base_lower = BASE_OUTPUT_DIR.lower()
        if "sme_conversions" in base_lower or "sme_conversion" in base_lower:
            KPI_COL = "SME_CONVERSIONS"
        elif "dme_web_orders" in base_lower or "dme_web_order" in base_lower:
            KPI_COL = "DME_WEB_ORDERS"
    if args.did_input_path:
        DID_INPUT_LONG_PATH = args.did_input_path
    if args.exclude_inference:
        EXCLUDE_INFERENCE_FROM_PLOTS = frozenset(
            s.strip() for s in args.exclude_inference.split(",") if s.strip()
        )
        if EXCLUDE_INFERENCE_FROM_PLOTS:
            print(f"Excluding inference from plots: {', '.join(sorted(EXCLUDE_INFERENCE_FROM_PLOTS))}")

    # Normalize to list: single KPI -> [kpi], list -> use as-is
    kpis_to_run = [KPI_COL] if isinstance(KPI_COL, str) else list(KPI_COL)

    print("Loading results from:", BASE_OUTPUT_DIR)
    pickles, csvs = discover_results(BASE_OUTPUT_DIR)
    if not pickles and not csvs:
        print("No *_weekly_trends_dct.pickle or *_summary_stats_df.csv found. Run the grid script first.")
        return
    print(f"Found {len(pickles)} pickle(s), {len(csvs)} CSV(s)")
    pickles, csvs = _filter_by_excluded_inference(pickles, csvs)

    for kpi in kpis_to_run:
        KPI_COL = kpi
        FIGURES_DIR = os.path.join(BASE_OUTPUT_DIR, f"{kpi}", "figures")
        save_dir = FIGURES_DIR
        dataset_filter = kpi
        print(f"\n--- KPI: {kpi} ---")
        os.makedirs(save_dir, exist_ok=True)
        estimates = load_summary_estimates(csvs, pickles, dataset_filter, base_dir=BASE_OUTPUT_DIR)
        plot_distribution_of_results(estimates, ACTUAL_EFFECT_REFERENCE, save_dir)
        plot_inference_comparison(estimates, ACTUAL_EFFECT_REFERENCE, save_dir)
        plot_geo_map(base_dir=BASE_OUTPUT_DIR, save_dir=BASE_OUTPUT_DIR)
        plot_counterfactual_stability_diagnostics(
            base_dir=BASE_OUTPUT_DIR,
            save_dir=FIGURES_DIR,
            dataset_filter=_get_dataset_filter(BASE_OUTPUT_DIR),
        )
        plot_estimator_effects_by_inference(csvs, pickles, dataset_filter, save_dir, base_dir=BASE_OUTPUT_DIR)
        plot_tbr_family_effects_by_inference(csvs, pickles, dataset_filter, save_dir, base_dir=BASE_OUTPUT_DIR)
        plot_scm_family_effects_by_inference(csvs, pickles, dataset_filter, save_dir, base_dir=BASE_OUTPUT_DIR)
        plot_did_estimate(pickles, csvs, save_dir, dataset_filter)
        pre_period = args.pre_period_weeks if args.pre_period_weeks is not None else PRE_PERIOD_WEEKS
        plot_tbr_family(pickles, csvs, save_dir, dataset_filter, base_dir=BASE_OUTPUT_DIR, pre_period_weeks=pre_period)
        plot_scm_family(pickles, csvs, save_dir, dataset_filter, base_dir=BASE_OUTPUT_DIR, pre_period_weeks=pre_period)
        plot_inference_family(pickles, csvs, save_dir, dataset_filter, base_dir=BASE_OUTPUT_DIR, pre_period_weeks=pre_period)
    print("Done.")


if __name__ == "__main__":
    main()
