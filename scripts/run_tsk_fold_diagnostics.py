"""
Run TSKFold fold diagnostics for TBRRidge and AugSynthCVXPY.

Saves TimeSeriesKFold_{estimator}_fold_diagnostics.csv to estimators_inference_grid_v1/.
"""
import json
import pickle
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REDDIT_DIR_CONFIG = Path("/Users/ppavuluri/Desktop/FY26/Q1/Reddit/estimators_inference_grid_v2")
DATASETS_PKL = REDDIT_DIR_CONFIG   / "mmt_datasets.pkl"
CONFIG_JSON  = REDDIT_DIR_CONFIG / "mmt_config.json"
OUTPUT_DIR   = REDDIT_DIR_CONFIG

PANEL_EXP_ROOT = Path("/Users/ppavuluri/Desktop/latest_pxp/panel_exp")
if str(PANEL_EXP_ROOT) not in sys.path:
    sys.path.insert(0, str(PANEL_EXP_ROOT))

from panel_exp.methods.tbr import TBR, TBRRidge
from panel_exp.methods.scm import AugSynthCVXPY
from panel_exp.methods.bayesian_regression import BayesianTBR, BayesianTBRHorseShoe
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.inference.k_fold import _create_blocks, _compute_tsk_fold_diagnostics

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

# Apply exclude_date_ranges from config
exclude_ranges = cfg.get("exclude_date_ranges", [])
keep_cols = wide.columns
for start_str, end_str in exclude_ranges:
    start_ts = pd.Timestamp(start_str)
    end_ts   = pd.Timestamp(end_str)
    keep_cols = keep_cols[(keep_cols < start_ts) | (keep_cols > end_ts)]
wide = wide.loc[:, keep_cols]

test_start = pd.Timestamp(cfg["test_start_dates"]["Reddit"])
test_end   = pd.Timestamp(cfg["test_end_dates"]["Reddit"])

print(f"Data loaded : {wide.shape[0]} units x {wide.shape[1]} periods")
print(f"Date range  : {wide.columns[0].date()} → {wide.columns[-1].date()}")
print(f"Treated DMAs: {len(treated_units)}   Control DMAs: {len(control_units)}")
print(f"Test period : {test_start.date()} → {test_end.date()}")

# ---------------------------------------------------------------------------
# Build PanelDataset
# ---------------------------------------------------------------------------
treated_periods = [
    TimePeriod(start=test_start, end=test_end)
    for _ in treated_units
]
pds = PanelDataset(
    wide_data=wide,
    treated_periods=treated_periods,
    treated_units=treated_units,
)

print(f"\nPanelDataset times: {len(pds.times)} periods")
print(f"Pre-period length : {pds.treated_start_idxs[0]}")
print(f"Test period length: {len(pds.times) - pds.treated_start_idxs[0]}")

# ---------------------------------------------------------------------------
# Create blocks (same as panel_timeseries_kfold defaults: k=5, holdout=4)
# ---------------------------------------------------------------------------
K       = 5
HOLDOUT = 4
BLOCK_SCHEME = "expanding"

pre_t_wide_data = pds.wide_data.iloc[:, :pds.treated_start_idxs[0]]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    blocks = _create_blocks(
        pre_t_wide_data=pre_t_wide_data,
        k=K,
        holdout=HOLDOUT,
        block_scheme=BLOCK_SCHEME,
    )

print(f"\nBlocks created: {len(blocks)}")
for i, b in enumerate(blocks):
    print(f"  Block {i+1}: {len(b)} periods  "
          f"[{b[0] if hasattr(b[0], 'date') else b[0]} → "
          f"{b[-1] if hasattr(b[-1], 'date') else b[-1]}]")

# ---------------------------------------------------------------------------
# Pre-aggregate treated units for TBRRidge
# TBRRidge expects a single pre-aggregated treated unit. fit_data() calls
# y[:treated_start_idx] which, with multiple treated units flattened, picks
# only the first unit's data. Pre-aggregate to __treated__ exactly as
# _tbr_kfold_fit_predict does in the pseudo-test script.
# ---------------------------------------------------------------------------
treated_agg_series = (
    pds.wide_data.loc[pds.treated_units]
    .sum(axis=0)
    .to_frame("__treated__")
    .T
)
ctrl_data = pds.wide_data.drop(index=pds.treated_units)
agg_wide = pd.concat([treated_agg_series, ctrl_data])
agg_pds = PanelDataset(
    wide_data=agg_wide,
    treated_periods=[pds.treated_periods[0]],
    treated_units=["__treated__"],
)
pre_t_agg = agg_pds.wide_data.iloc[:, :agg_pds.treated_start_idxs[0]]
blocks_agg = _create_blocks(pre_t_wide_data=pre_t_agg, k=K, holdout=HOLDOUT, block_scheme=BLOCK_SCHEME)

print(f"\nPre-aggregated PDS: {agg_pds.wide_data.shape[0]} units (1 treated + {ctrl_data.shape[0]} controls)")

# ---------------------------------------------------------------------------
# Fully aggregated PanelDataset for TBR / BayesianTBR
# Both treated and control collapsed to single aggregate units.
# ---------------------------------------------------------------------------
ctrl_agg_series = (
    pds.wide_data.loc[control_units]
    .sum(axis=0)
    .to_frame("__control__")
    .T
)
fully_agg_wide = pd.concat([treated_agg_series, ctrl_agg_series])
fully_agg_pds = PanelDataset(
    wide_data=fully_agg_wide,
    treated_periods=[pds.treated_periods[0]],
    treated_units=["__treated__"],
)
pre_t_fully_agg = fully_agg_pds.wide_data.iloc[:, :fully_agg_pds.treated_start_idxs[0]]
blocks_fully_agg = _create_blocks(pre_t_wide_data=pre_t_fully_agg, k=K, holdout=HOLDOUT, block_scheme=BLOCK_SCHEME)

print(f"Fully-aggregated PDS: {fully_agg_pds.wide_data.shape[0]} units (1 treated + 1 control)")

# ---------------------------------------------------------------------------
# Run fold diagnostics for each estimator
# ---------------------------------------------------------------------------
# Aggregation rules:
#   TBR, BayesianTBR         → fully_agg_pds (treated + control both aggregated)
#   TBRRidge, BayesianTBRHorseShoe → agg_pds (treated aggregated, control unit-level)
#   AugSynthCVXPY             → pds (unit-level)
ESTIMATORS = [
    ("TBRRidge",            TBRRidge,            agg_pds,        blocks_agg),
    ("AugSynthCVXPY",       AugSynthCVXPY,       pds,            blocks),
    ("TBR",                 TBR,                 fully_agg_pds,  blocks_fully_agg),
    ("BayesianTBR",         BayesianTBR,         fully_agg_pds,  blocks_fully_agg),
    ("BayesianTBRHorseShoe",BayesianTBRHorseShoe,agg_pds,        blocks_agg),
]

for estimator_name, estimator_cls, diag_pds, diag_blocks in ESTIMATORS:
    print(f"\n{'='*60}")
    print(f"Computing TSKFold diagnostics: {estimator_name}")
    print(f"{'='*60}")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        diag_df = _compute_tsk_fold_diagnostics(diag_pds, estimator_cls, diag_blocks)

    out_path = OUTPUT_DIR / f"TimeSeriesKFold_{estimator_name}_fold_diagnostics.csv"
    diag_df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(diag_df.to_string(index=False))

print("\nDone.")
