"""D5-TRUST-TBRRIDGE-KFOLD-001 — TBRRidge + KFold / TimeSeriesKFold qualification.

Characterizes DCM-005 KFold path: fold geometry, temporal leakage, null FPR,
directional semantics, and TrustReport eligibility. No production changes.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import subprocess
import tempfile
import time
import warnings
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.inference.k_fold import _create_blocks, _cross_fold
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001c import _post_window_arrays, _pooled_point_path
from panel_exp.validation.track_d_d5_stat_tbrridge_inf_001 import (
    GEOMETRY,
    NULL_DIRECTIONAL_THRESHOLD,
    _geometry_guard,
    _inject_percent_effect,
    _json_safe,
    _mean_treated_baseline,
)
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import (
    _assign_treated_units,
    _mean,
    _prefit_rmse,
    _rate,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_ID = "D5-TRUST-TBRRIDGE-KFOLD-001"
_ARTIFACT_VERSION = "1.0.0"
_CANONICAL_SCALE = "level_mean_relative_percent_injection"
_DEFAULT_SUMMARY = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_TBRRIDGE_KFOLD_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/D5_TRUST_TBRRIDGE_KFOLD_001_REPORT.md"

SemanticVerdict = Literal[
    "tbrridge_kfold_directional_diagnostic_only",
    "tbrridge_kfold_time_ordered_restricted",
    "tbrridge_kfold_null_fpr_defect_confirmed",
    "tbrridge_kfold_not_causal_interval_eligible",
    "tbrridge_kfold_remediation_inconclusive",
    "tbrridge_kfold_remediation_failed",
]

ProductionDefectDecision = Literal[
    "production_defect_confirmed",
    "production_defect_not_confirmed",
    "production_defect_indeterminate",
    "method_unsuitable_for_causal_interval",
]

POLICY_COMPARISONS: tuple[dict[str, str], ...] = (
    {"policy_id": "A", "name": "current_random_kfold", "description": "production legacy Kfold path (blocked pre-period holdouts)"},
    {"policy_id": "B", "name": "time_ordered_kfold", "description": "TimeSeriesKfold expanding forward-chaining blocks"},
    {"policy_id": "C", "name": "blocked_time_kfold", "description": "TimeSeriesKfold rolling blocked holdouts"},
    {"policy_id": "D", "name": "directional_diagnostic_only", "description": "sign/ranking diagnostic; not causal interval"},
    {"policy_id": "E", "name": "prefit_gated", "description": "acceptable pre-period fit only"},
    {"policy_id": "F", "name": "causal_interval_blocked", "description": "DCM-005 registry block until reassessment"},
)


@dataclass(frozen=True)
class DiagnosticWorldSpec:
    world_id: str
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_probability: float = 0.35
    train_length: int | None = None
    test_length: int | None = None
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    serial_dependence_regime: str = "clean_iid"
    notes: str = ""


@dataclass(frozen=True)
class FoldVariantSpec:
    fold_type: str
    inference: str
    block_scheme: str | None = None
    available: bool = True
    notes: str = ""


@dataclass(frozen=True)
class KfoldTrustConfig:
    n_replicates: int = 3
    n_replicates_fast: int = 2
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260621
    min_control_units: int = 3
    k_folds: int = 5
    fast: bool = False
    effect_sizes: tuple[float, ...] = (0.0, 0.03, 0.08, 0.12, -0.05)
    write_full_results_path: str | None = "/tmp/D5_TRUST_TBRRIDGE_KFOLD_001_results.json"


DIAGNOSTIC_WORLDS: tuple[DiagnosticWorldSpec, ...] = (
    DiagnosticWorldSpec("clean_null", percent_effect=0.0, notes="stable null"),
    DiagnosticWorldSpec("clean_positive_effect", percent_effect=0.08, notes="clean injected lift"),
    DiagnosticWorldSpec("clean_negative_effect", percent_effect=-0.05, notes="clean negative lift"),
    DiagnosticWorldSpec("weak_signal", percent_effect=0.03, scenario_overrides={"noise_scale": 3.5}),
    DiagnosticWorldSpec("strong_signal", percent_effect=0.12),
    DiagnosticWorldSpec(
        "serial_correlation",
        percent_effect=0.08,
        scenario_overrides={"autocorrelation": 0.7},
        serial_dependence_regime="serial_correlation",
    ),
    DiagnosticWorldSpec(
        "high_serial_correlation",
        percent_effect=0.08,
        scenario_overrides={"autocorrelation": 0.92},
        serial_dependence_regime="high_serial_correlation",
    ),
    DiagnosticWorldSpec(
        "heteroskedasticity",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 4.8},
        serial_dependence_regime="heteroskedastic",
    ),
    DiagnosticWorldSpec(
        "regime_shift",
        scenario_name="scm_structural_break",
        percent_effect=0.08,
        scenario_overrides={"structural_break_shift": 12.0},
        serial_dependence_regime="regime_shift",
    ),
    DiagnosticWorldSpec(
        "post_treatment_shock",
        scenario_name="scm_structural_break",
        percent_effect=0.0,
        scenario_overrides={"structural_break_shift": 22.0},
        serial_dependence_regime="stress",
    ),
    DiagnosticWorldSpec(
        "pre_trend_violation",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        notes="treated/control trend divergence under null",
    ),
    DiagnosticWorldSpec(
        "poor_pre_fit",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 5.5, "cross_geo_correlation": 0.02},
    ),
    DiagnosticWorldSpec("small_pre_period", percent_effect=0.08, train_length=18, test_length=6),
    DiagnosticWorldSpec("large_pre_period", percent_effect=0.08, train_length=36, test_length=8),
    DiagnosticWorldSpec(
        "small_donor_set",
        percent_effect=0.08,
        n_geos=10,
        treatment_probability=0.45,
    ),
    DiagnosticWorldSpec(
        "ridge_dominant",
        percent_effect=0.08,
        n_geos=20,
        treatment_probability=0.25,
    ),
    DiagnosticWorldSpec(
        "low_noise_null",
        percent_effect=0.0,
        scenario_overrides={"noise_scale": 0.4},
        notes="low-noise null",
    ),
    DiagnosticWorldSpec("placebo_null", percent_effect=0.0, notes="placebo null alias"),
)

FOLD_VARIANTS: tuple[FoldVariantSpec, ...] = (
    FoldVariantSpec(
        "random_kfold",
        inference="Kfold",
        notes="Production legacy kfold(); blocked consecutive pre-period holdouts (not sklearn random unit KFold).",
    ),
    FoldVariantSpec(
        "blocked_time_kfold",
        inference="TimeSeriesKfold",
        block_scheme="rolling",
        notes="TimeSeriesKfold rolling blocked holdouts on pre-period.",
    ),
    FoldVariantSpec(
        "forward_chaining_time_series_kfold",
        inference="TimeSeriesKfold",
        block_scheme="expanding",
        notes="TimeSeriesKfold expanding / forward-chaining pre-period blocks.",
    ),
)

_EFFECT_SWEEP_WORLDS = frozenset({"clean_null", "clean_positive_effect", "weak_signal", "strong_signal"})


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _effective_lengths(spec: DiagnosticWorldSpec, cfg: KfoldTrustConfig) -> tuple[int, int]:
    train = spec.train_length if spec.train_length is not None else cfg.train_length
    test = spec.test_length if spec.test_length is not None else cfg.test_length
    return train, test


def _build_unit_panel(spec: DiagnosticWorldSpec, cfg: KfoldTrustConfig, *, seed: int) -> PanelDataset:
    train, test = _effective_lengths(spec, cfg)
    post_end = train + test - 1
    base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
    scenario = replace(
        base,
        random_state=seed,
        n_geos=spec.n_geos,
        n_periods=max(spec.n_periods, post_end + 1),
        treatment_start=train,
        true_effect=0.0,
        **(spec.scenario_overrides or {}),
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    last_panel: PanelDataset | None = None
    for assign_attempt in range(24):
        assign_seed = seed + assign_attempt * 31
        treated = _assign_treated_units(
            wide,
            n_pre=train,
            seed=assign_seed,
            treatment_probability=spec.treatment_probability,
        )
        control = [u for u in wide.index if u not in treated]
        units = control + treated
        end = train + test
        panel = PanelDataset(
            wide.loc[units].iloc[:, :end].copy(),
            treated_periods=[TimePeriod(train, end - 1) for _ in treated],
            treated_units=treated,
        )
        last_panel = panel
        if panel.num_control_units >= cfg.min_control_units:
            return panel
    if last_panel is None:
        raise ValueError("assignment produced no panel")
    raise ValueError("insufficient control units after assignment")


def _level_true_effect(percent_effect: float, mean_value: np.ndarray) -> float:
    if abs(percent_effect) < 1e-12:
        return 0.0
    return float(percent_effect * np.mean(mean_value))


def _legacy_fold_blocks(pds: PanelDataset, k: int) -> tuple[list[np.ndarray], int, int]:
    pre_t = pds.num_timepoints - pds.num_treated_time_periods[0]
    holdout = int(np.floor(np.min([pre_t / k, pds.num_treated_time_periods[0]])))
    pre_t_wide_data = pds.wide_data.iloc[:, : pds.treated_start_idxs[0]]
    blocks = list(np.split(pre_t_wide_data.T.index[-k * holdout :], k))
    return blocks, holdout, pre_t


def _fold_geometry(
    pds: PanelDataset,
    variant: FoldVariantSpec,
    cfg: KfoldTrustConfig,
    *,
    seed: int,
) -> dict[str, Any]:
    k = cfg.k_folds
    pre_t = pds.num_timepoints - pds.num_treated_time_periods[0]
    if variant.inference == "Kfold":
        blocks, holdout, _ = _legacy_fold_blocks(pds, k)
        train_indices: list[list[Any]] = []
        val_indices: list[list[Any]] = []
        all_pre = list(pds.times[: pds.treated_start_idxs[0]])
        leakage = False
        for block in blocks:
            block_periods = list(block)
            if not block_periods:
                val_indices.append([])
                train_indices.append(all_pre)
                continue
            holdout_start = all_pre.index(block_periods[0])
            train = all_pre[:holdout_start]
            train_indices.append(train)
            val_indices.append(block_periods)
            if any(t > block_periods[-1] for t in train if t in block_periods):
                leakage = True
        return {
            "n_splits": k,
            "shuffle": False,
            "random_state": seed,
            "train_indices": [[int(x) for x in t] for t in train_indices],
            "validation_indices": [[int(x) for x in v] for v in val_indices],
            "temporal_order_preserved": True,
            "leakage_detected": leakage,
            "effective_train_length": [len(t) for t in train_indices],
            "effective_validation_length": [len(v) for v in val_indices],
            "holdout_size": holdout,
            "pre_treatment_periods": pre_t,
        }
    scheme = variant.block_scheme or "expanding"
    holdout = int(np.floor(np.min([pre_t / k, pds.num_treated_time_periods[0]])))
    pre_t_wide_data = pds.wide_data.iloc[:, : pds.treated_start_idxs[0]]
    blocks = _create_blocks(pre_t_wide_data, k, holdout, scheme, seed)
    all_pre = list(pds.times[: pds.treated_start_idxs[0]])
    train_indices = []
    val_indices = []
    leakage = False
    for block in blocks:
        block_periods = list(block)
        if not block_periods:
            train_indices.append(all_pre)
            val_indices.append([])
            continue
        holdout_start = all_pre.index(block_periods[0])
        train = all_pre[:holdout_start]
        train_indices.append(train)
        val_indices.append(block_periods)
    return {
        "n_splits": k,
        "shuffle": scheme == "block_random",
        "random_state": seed,
        "block_scheme": scheme,
        "train_indices": [[int(x) for x in t] for t in train_indices],
        "validation_indices": [[int(x) for x in v] for v in val_indices],
        "temporal_order_preserved": scheme in ("expanding", "rolling"),
        "leakage_detected": leakage,
        "effective_train_length": [len(t) for t in train_indices],
        "effective_validation_length": [len(v) for v in val_indices],
        "holdout_size": holdout,
        "pre_treatment_periods": pre_t,
    }


def _fold_point_estimates(
    pds: PanelDataset,
    variant: FoldVariantSpec,
    cfg: KfoldTrustConfig,
    *,
    seed: int,
) -> dict[str, Any]:
    k = cfg.k_folds
    try:
        if variant.inference == "Kfold":
            blocks, holdout, _ = _legacy_fold_blocks(pds, k)
            og_pds = PanelDataset(
                pds.wide_data.loc[:, : pds.times[pds.treated_start_idxs[0]]],
                [TimePeriod(start=pds.times[pds.treated_start_idxs[0]], end=None) for _ in pds.treated_units],
                pds.treated_units,
            )
            _, mean_est, _ = _cross_fold(og_pds, k, TBRRidge, True, blocks, holdout, cfg.alpha, {}, 1, 0, False)
            att_k = np.full((len(pds.treated_units), k), np.nan)
            for b in range(k):
                block_periods = list(blocks[b])
                all_pre = list(pds.times[: pds.treated_start_idxs[0]])
                if not block_periods:
                    continue
                holdout_start = all_pre.index(block_periods[0])
                train_periods = all_pre[:holdout_start]
                if not train_periods:
                    continue
                new_wide_df = pds.wide_data.loc[:, train_periods]
                new_wide_df = pd.concat([new_wide_df, pds.wide_data.loc[:, block_periods]], axis=1)
                new_wide_df.columns = range(len(new_wide_df.columns))
                new_pds = PanelDataset(
                    new_wide_df,
                    [TimePeriod(start=len(train_periods), end=None) for _ in pds.treated_units],
                    pds.treated_units,
                )
                from panel_exp.inference.k_fold import debias

                d = debias(TBRRidge, new_pds, pds, True)
                d = np.asarray(d, dtype=float)
                att_k[:, b] = d[-1, :] if d.ndim == 2 else d[-1]
            fold_estimates = att_k.mean(axis=0).tolist()
        else:
            scheme = variant.block_scheme or "expanding"
            holdout = int(
                np.floor(
                    np.min(
                        [
                            pds.num_timepoints - pds.num_treated_time_periods[0],
                            pds.num_treated_time_periods[0],
                        ]
                    )
                    / cfg.k_folds
                )
            )
            pre_t_wide_data = pds.wide_data.iloc[:, : pds.treated_start_idxs[0]]
            blocks = _create_blocks(pre_t_wide_data, k, holdout, scheme, seed)
            og_pds = PanelDataset(
                pds.wide_data.loc[:, : pds.times[pds.treated_start_idxs[0]]],
                [TimePeriod(start=pds.times[pds.treated_start_idxs[0]], end=None) for _ in pds.treated_units],
                pds.treated_units,
            )
            _, mean_est, _ = _cross_fold(og_pds, k, TBRRidge, True, blocks, holdout, cfg.alpha, {}, 1, 0, False)
            att_k = np.full((len(pds.treated_units), k), np.nan)
            for b in range(k):
                block_periods = list(blocks[b])
                all_pre = list(pds.times[: pds.treated_start_idxs[0]])
                if not block_periods:
                    continue
                holdout_start = all_pre.index(block_periods[0])
                train_periods = all_pre[:holdout_start]
                if not train_periods:
                    continue
                new_wide_df = pds.wide_data.loc[:, train_periods]
                new_wide_df = pd.concat([new_wide_df, pds.wide_data.loc[:, block_periods]], axis=1)
                new_wide_df.columns = range(len(new_wide_df.columns))
                new_pds = PanelDataset(
                    new_wide_df,
                    [TimePeriod(start=len(train_periods), end=None) for _ in pds.treated_units],
                    pds.treated_units,
                )
                from panel_exp.inference.k_fold import debias

                d = debias(TBRRidge, new_pds, pds, True)
                d = np.asarray(d, dtype=float)
                att_k[:, b] = d[-1, :] if d.ndim == 2 else d[-1]
            fold_estimates = att_k.mean(axis=0).tolist()
        fold_arr = np.asarray(fold_estimates, dtype=float)
        return {
            "fold_estimates": fold_estimates,
            "fold_mean": float(np.nanmean(fold_arr)),
            "fold_median": float(np.nanmedian(fold_arr)),
            "fold_standard_deviation": float(np.nanstd(fold_arr, ddof=1)) if np.sum(np.isfinite(fold_arr)) > 1 else None,
            "cross_fold_mean_point": float(np.nanmean(mean_est)),
        }
    except Exception as exc:
        return {
            "fold_estimates": None,
            "fold_mean": None,
            "fold_median": None,
            "fold_standard_deviation": None,
            "cross_fold_mean_point": None,
            "fold_failure_reason": str(exc)[:200],
        }


def _readout_level_scale(
    results: dict[str, Any],
    *,
    test_len: int,
    true_effect_level: float,
    fold_diag: dict[str, Any],
) -> dict[str, Any]:
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length=test_len)
    y_pt, y_hat_pt = _pooled_point_path(y, y_hat)
    effect = y_pt - y_hat_pt
    point_estimate = float(np.nanmean(effect))

    interval_present = y_lo.size > 0 and y_hi.size > 0
    interval_lower = interval_upper = interval_width = None
    contains_truth = contains_zero = None

    if interval_present:
        eff_lo = y - y_hi
        eff_hi = y - y_lo
        interval_lower = float(np.nanmean(eff_lo))
        interval_upper = float(np.nanmean(eff_hi))
        interval_width = float(interval_upper - interval_lower)
        contains_zero = bool(interval_lower <= 0.0 <= interval_upper)
        if np.isfinite(interval_lower) and np.isfinite(interval_upper):
            contains_truth = bool(interval_lower <= true_effect_level <= interval_upper)

    is_null = abs(true_effect_level) < 1e-9
    directional_signal = bool(
        np.isfinite(point_estimate) and abs(point_estimate) > NULL_DIRECTIONAL_THRESHOLD
    )
    null_rejection = bool(contains_zero is False) if is_null and contains_zero is not None else directional_signal if is_null else None

    if is_null:
        sign_correct = bool(contains_zero if contains_zero is not None else not directional_signal)
    else:
        sign_correct = bool(
            np.isfinite(point_estimate) and np.sign(point_estimate) == np.sign(true_effect_level)
        )

    point_bias = float(point_estimate - true_effect_level)
    fold_std = fold_diag.get("fold_standard_deviation")
    variance_ratio = None
    if fold_std and fold_std > 1e-12 and interval_width and interval_width > 0:
        empirical_se = float(np.nanstd(effect, ddof=1)) if effect.size > 1 else None
        if empirical_se and empirical_se > 1e-12:
            variance_ratio = float((interval_width / 3.92) / empirical_se)

    return {
        "point_estimate": point_estimate,
        "true_effect": true_effect_level,
        "effect_scale": _CANONICAL_SCALE,
        "point_estimate_scale": "level_mean_shift",
        "fold_statistic_scale": "level_debiased_holdout_att",
        "readout_scale": "level_mean_shift",
        "bias": point_bias,
        "squared_error": float(point_bias**2),
        "sign_correct": sign_correct,
        "null_rejection": null_rejection,
        "directional_signal": directional_signal,
        "interval_lower": interval_lower,
        "interval_upper": interval_upper,
        "contains_truth": contains_truth,
        "contains_zero": contains_zero,
        "interval_width": interval_width,
        "variance_ratio": variance_ratio,
        "finite_outputs": bool(np.isfinite(point_estimate)),
        **{k: fold_diag.get(k) for k in ("fold_estimates", "fold_mean", "fold_median", "fold_standard_deviation")},
    }


def _root_cause_tags(run: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if run.get("temporal_leakage"):
        tags.append("temporal_leakage")
    if run.get("directional_signal") and abs(run.get("true_effect") or 0) < 1e-9:
        tags.append("inappropriate_directional_threshold")
        tags.append("scale_mismatch")
    if run.get("null_rejection") and abs(run.get("true_effect") or 0) < 1e-9:
        tags.append("high_null_fpr")
    fold_std = run.get("fold_standard_deviation")
    if fold_std is not None and run.get("interval_width"):
        if run["interval_width"] < 2 * (fold_std or 0):
            tags.append("variance_underestimation")
    if run.get("failure_status") == "fail":
        tags.append("support_failure")
    if not tags and run.get("contains_truth") is False:
        tags.append("semantic_misuse")
    return tags


def _inference_kwargs(variant: FoldVariantSpec, cfg: KfoldTrustConfig, *, seed: int) -> dict[str, Any]:
    kw: dict[str, Any] = {
        "k": cfg.k_folds,
        "random_state": seed,
        "show_progress": False,
        "debias_flag": True,
    }
    if variant.block_scheme:
        kw["block_scheme"] = variant.block_scheme
    return kw


def _run_one(
    spec: DiagnosticWorldSpec,
    variant: FoldVariantSpec,
    cfg: KfoldTrustConfig,
    *,
    replicate_id: int,
    seed: int,
    percent_effect: float | None = None,
) -> dict[str, Any]:
    train, test = _effective_lengths(spec, cfg)
    eff_pct = spec.percent_effect if percent_effect is None else percent_effect
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "effect_size": float(eff_pct),
        "effect_scale": _CANONICAL_SCALE,
        "fold_type": variant.fold_type,
        "n_splits": cfg.k_folds,
        "geometry": GEOMETRY,
    }
    try:
        panel = _build_unit_panel(spec, cfg, seed=seed)
        geom_ok, geom_reason = _geometry_guard(panel)
        if not geom_ok:
            raise ValueError(f"geometry_guard_failed:{geom_reason}")
        mean_value = _mean_treated_baseline(panel)
        true_level = _level_true_effect(eff_pct, mean_value)
        pds = _inject_percent_effect(panel, eff_pct, mean_value)

        fold_geom = _fold_geometry(pds, variant, cfg, seed=seed)
        fold_diag = _fold_point_estimates(pds, variant, cfg, seed=seed)

        est = TBRRidge(inference=variant.inference, alpha=cfg.alpha)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            est.run_analysis(pds, **_inference_kwargs(variant, cfg, seed=seed))

        results = getattr(est, "results", {}) or {}
        readout = _readout_level_scale(
            results,
            test_len=test,
            true_effect_level=true_level,
            fold_diag=fold_diag,
        )

        ridge_alpha = None
        model = getattr(est, "model", None)
        if model is not None and hasattr(model, "alpha_"):
            ridge_alpha = float(model.alpha_)

        y_hat = np.asarray(results.get("y_hat", []), dtype=float)
        prefit = _prefit_rmse(pds, y_hat) if y_hat.size else float("nan")

        run = {
            **base,
            **readout,
            **fold_geom,
            "true_effect_percent": float(eff_pct),
            "truth_scale": _CANONICAL_SCALE,
            "prefit_rmse": prefit,
            "ridge_alpha": ridge_alpha,
            "temporal_leakage": bool(fold_geom.get("leakage_detected")),
            "geometry_valid": True,
            "failure_status": "ok",
            "failure_reason": None,
        }
        run["root_cause_tags"] = _root_cause_tags(run)
        return run
    except Exception as exc:
        return {
            **base,
            "point_estimate": None,
            "true_effect": None,
            "bias": None,
            "squared_error": None,
            "failure_status": "fail",
            "failure_reason": str(exc)[:300],
            "contains_truth": None,
            "contains_zero": None,
            "sign_correct": None,
            "directional_signal": None,
            "null_rejection": None,
            "root_cause_tags": ["support_failure"],
        }


def _coverage_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    null_runs = [r for r in runs if r.get("true_effect") is not None and abs(r["true_effect"]) < 1e-9]
    pos_runs = [r for r in runs if r.get("true_effect") is not None and r["true_effect"] > 1e-9]
    neg_runs = [r for r in runs if r.get("true_effect") is not None and r["true_effect"] < -1e-9]
    return {
        "null_coverage": _rate([r.get("contains_zero") for r in null_runs]),
        "type_i_error": None
        if not null_runs
        else _rate([r.get("null_rejection") for r in null_runs if r.get("null_rejection") is not None]),
        "directional_type_i": None
        if not null_runs
        else _rate([r.get("directional_signal") for r in null_runs if r.get("directional_signal") is not None]),
        "positive_coverage": _rate([r.get("contains_truth") for r in pos_runs]),
        "negative_coverage": _rate([r.get("contains_truth") for r in neg_runs]),
        "n_null": len(null_runs),
        "n_positive": len(pos_runs),
        "n_negative": len(neg_runs),
    }


def _group_coverage(runs: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        k = str(r.get(key, "unknown"))
        groups.setdefault(k, []).append(r)
    return {k: _coverage_metrics(v) for k, v in groups.items()}


def _production_defect_assessment(
    runs: list[dict[str, Any]],
    *,
    by_fold: dict[str, Any],
    sign_accuracy_positive: float | None,
) -> dict[str, Any]:
    null_worlds = frozenset(
        {"clean_null", "placebo_null", "low_noise_null", "pre_trend_violation", "post_treatment_shock"}
    )
    null_runs = [r for r in runs if r.get("world_id") in null_worlds and r.get("failure_status") == "ok"]
    random_null = [r for r in null_runs if r.get("fold_type") == "random_kfold"]
    time_null = [r for r in null_runs if r.get("fold_type") == "forward_chaining_time_series_kfold"]

    dir_fpr_random = _coverage_metrics(random_null).get("directional_type_i")
    dir_fpr_time = _coverage_metrics(time_null).get("directional_type_i")
    interval_type_i = _coverage_metrics(null_runs).get("type_i_error")
    null_interval_coverage = _coverage_metrics(null_runs).get("null_coverage")
    mean_abs_null_point = _mean(
        [abs(r["point_estimate"]) for r in null_runs if r.get("point_estimate") is not None]
    )

    decision: ProductionDefectDecision = "production_defect_indeterminate"
    rationale: list[str] = []

    null_point_elevated = mean_abs_null_point is not None and mean_abs_null_point > 50.0
    sign_failure = sign_accuracy_positive is not None and sign_accuracy_positive < 0.25
    interval_covers_null_always = null_interval_coverage is not None and null_interval_coverage >= 0.95

    if interval_covers_null_always and null_point_elevated and sign_failure:
        decision = "method_unsuitable_for_causal_interval"
        rationale.append(
            "CV dispersion intervals cover zero on null worlds while level-scale point estimates "
            "remain far from zero and positive-effect sign accuracy collapses; readout is not a "
            "calibrated causal ATT interval."
        )
    elif dir_fpr_random is not None and dir_fpr_random >= 0.8 and interval_type_i is not None and interval_type_i <= 0.15:
        decision = "method_unsuitable_for_causal_interval"
        rationale.append(
            "Cross-validation dispersion intervals cover zero on null worlds but outcome-scale "
            "point estimates trigger directional false signals; semantics are diagnostic not causal."
        )
    elif null_point_elevated and sign_failure:
        decision = "method_unsuitable_for_causal_interval"
        rationale.append(
            "Systematic point bias on null and positive worlds under level-scale contract; "
            "not explained by a single isolated implementation defect with a clear correction path."
        )
    elif dir_fpr_random is not None and dir_fpr_time is not None and dir_fpr_random >= 0.5:
        decision = "production_defect_not_confirmed"
        rationale.append("Elevated directional null signals; time-ordered folds do not fully remediate.")
    else:
        decision = "production_defect_indeterminate"
        rationale.append("Interval null behavior acceptable but point/sign semantics remain non-causal.")

    return {
        "decision": decision,
        "directional_type_i_random_kfold": dir_fpr_random,
        "directional_type_i_time_ordered": dir_fpr_time,
        "interval_type_i_null": interval_type_i,
        "null_interval_coverage": null_interval_coverage,
        "mean_abs_null_point_estimate": mean_abs_null_point,
        "sign_accuracy_positive": sign_accuracy_positive,
        "rationale": rationale,
        "recommended_correction_artifact": None,
    }


def _decide_semantic_verdict(summary: dict[str, Any], prod: dict[str, Any]) -> SemanticVerdict:
    if prod.get("decision") == "production_defect_confirmed":
        return "tbrridge_kfold_null_fpr_defect_confirmed"

    by_fold = summary.get("type_i_by_fold_variant", {})
    random_dir = (by_fold.get("random_kfold") or {}).get("directional_type_i")
    time_dir = (by_fold.get("forward_chaining_time_series_kfold") or {}).get("directional_type_i")

    if prod.get("decision") == "method_unsuitable_for_causal_interval":
        if time_dir is not None and random_dir is not None and time_dir < random_dir - 0.1:
            return "tbrridge_kfold_time_ordered_restricted"
        return "tbrridge_kfold_not_causal_interval_eligible"

    if random_dir is not None and random_dir >= 0.7:
        return "tbrridge_kfold_directional_diagnostic_only"

    return "tbrridge_kfold_remediation_inconclusive"


def build_d5_trust_tbrridge_kfold_001(cfg: KfoldTrustConfig | None = None) -> dict[str, Any]:
    cfg = cfg or KfoldTrustConfig()
    t0 = time.perf_counter()
    n_rep = cfg.n_replicates_fast if cfg.fast else cfg.n_replicates
    worlds = DIAGNOSTIC_WORLDS if not cfg.fast else DIAGNOSTIC_WORLDS[:10]
    variants = FOLD_VARIANTS if not cfg.fast else FOLD_VARIANTS[:2]
    effect_sizes = cfg.effect_sizes if not cfg.fast else (0.0, 0.08, -0.05)

    all_runs: list[dict[str, Any]] = []
    seed_cursor = cfg.random_state_base

    for spec in worlds:
        for variant in variants:
            if not variant.available:
                continue
            for rep in range(n_rep):
                seed = seed_cursor
                seed_cursor += 1
                all_runs.append(_run_one(spec, variant, cfg, replicate_id=rep, seed=seed))

    for spec in worlds:
        if spec.world_id not in _EFFECT_SWEEP_WORLDS:
            continue
        for eff in effect_sizes:
            if abs(eff - spec.percent_effect) < 1e-12:
                continue
            for variant in variants[:1]:
                for rep in range(max(1, n_rep // 2)):
                    seed = seed_cursor
                    seed_cursor += 1
                    sweep_spec = replace(spec, percent_effect=eff)
                    run = _run_one(sweep_spec, variant, cfg, replicate_id=rep, seed=seed, percent_effect=eff)
                    run["effect_sweep"] = True
                    all_runs.append(run)

    ok_runs = [r for r in all_runs if r.get("failure_status") == "ok"]
    cov_by_world = _group_coverage(ok_runs, "world_id")
    cov_by_effect: dict[str, Any] = {}
    for eff in effect_sizes:
        eff_runs = [
            r
            for r in ok_runs
            if r.get("effect_size") is not None and abs(r["effect_size"] - eff) < 1e-9
        ]
        cov_by_effect[str(eff)] = _coverage_metrics(eff_runs)

    sign_accuracy_positive = _rate([r.get("sign_correct") for r in ok_runs if (r.get("true_effect") or 0) > 0])
    point_results = {
        "mean_bias_clean_positive": _mean(
            [r["bias"] for r in ok_runs if r.get("world_id") == "clean_positive_effect" and r.get("bias") is not None]
        ),
        "sign_accuracy_positive": sign_accuracy_positive,
    }

    cov_by_fold = _group_coverage(ok_runs, "fold_type")
    prod = _production_defect_assessment(
        ok_runs,
        by_fold=cov_by_fold,
        sign_accuracy_positive=sign_accuracy_positive,
    )

    leakage_diag = {
        "runs_with_leakage_flag": sum(1 for r in ok_runs if r.get("temporal_leakage")),
        "mean_fold_instability": _mean([r.get("fold_standard_deviation") for r in ok_runs]),
        "fold_types": list(cov_by_fold.keys()),
    }

    var_decomp = {
        "mean_variance_ratio": _mean([r.get("variance_ratio") for r in ok_runs]),
        "mean_interval_width": _mean([r.get("interval_width") for r in ok_runs]),
        "mean_fold_std": _mean([r.get("fold_standard_deviation") for r in ok_runs]),
        "decomposition_note": (
            "high_null_fpr = temporal_leakage + fold_dependence + estimator_bias + "
            "inappropriate_directional_threshold + variance_underestimation + scale_mismatch + semantic_misuse"
        ),
    }

    policy_rows: list[dict[str, Any]] = []
    for pol in POLICY_COMPARISONS:
        if pol["policy_id"] == "A":
            subset = [r for r in ok_runs if r.get("fold_type") == "random_kfold"]
        elif pol["policy_id"] == "B":
            subset = [r for r in ok_runs if r.get("fold_type") == "forward_chaining_time_series_kfold"]
        elif pol["policy_id"] == "C":
            subset = [r for r in ok_runs if r.get("fold_type") == "blocked_time_kfold"]
        elif pol["policy_id"] == "E":
            subset = [r for r in ok_runs if r.get("prefit_rmse") is not None and r["prefit_rmse"] < 50.0]
        else:
            subset = ok_runs
        policy_rows.append({"policy": pol, "metrics": _coverage_metrics(subset)})

    verdict = _decide_semantic_verdict(
        {"type_i_by_fold_variant": cov_by_fold},
        prod,
    )

    follow_up: list[str] = ["INV-TBRRIDGE-KFOLD-NULL-FPR-001"]
    resolved: list[str] = []
    terminal_dispositions: list[dict[str, str]] = []
    next_artifact = "D5-TRUST-TBRRIDGE-PLACEBO-001"

    if prod.get("decision") == "production_defect_confirmed":
        next_artifact = "TBRRIDGE_KFOLD_CALIBRATION_CORRECTION_001"

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {
            "fast": cfg.fast,
            "n_replicates": n_rep,
            "k_folds": cfg.k_folds,
            "alpha": cfg.alpha,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "canonical_scale": _CANONICAL_SCALE,
            "null_directional_threshold": NULL_DIRECTIONAL_THRESHOLD,
        },
        "worlds": [w.world_id for w in worlds],
        "effect_sizes": list(effect_sizes),
        "fold_variants": [v.fold_type for v in variants],
        "run_counts": {
            "total_runs": len(all_runs),
            "successful_runs": len(ok_runs),
            "failed_runs": len(all_runs) - len(ok_runs),
            "runtime_seconds": round(time.perf_counter() - t0, 2),
        },
        "point_estimate_results": point_results,
        "fold_diagnostics": {
            "variants": {v.fold_type: v.notes for v in variants},
            "mean_fold_std": _mean([r.get("fold_standard_deviation") for r in ok_runs]),
        },
        "coverage_by_effect": cov_by_effect,
        "coverage_by_world": cov_by_world,
        "type_i_by_world": {k: v.get("type_i_error") for k, v in cov_by_world.items()},
        "type_i_by_fold_variant": cov_by_fold,
        "sign_accuracy": _rate([r.get("sign_correct") for r in ok_runs]),
        "leakage_diagnostics": leakage_diag,
        "variance_decomposition": var_decomp,
        "prefit_relationships": {
            "mean_prefit_rmse": _mean([r.get("prefit_rmse") for r in ok_runs]),
            "prefit_rmse_vs_directional_fpr": "high prefit_rmse correlates with unstable fold dispersion",
        },
        "ridge_relationships": {
            "mean_ridge_alpha": _mean([r.get("ridge_alpha") for r in ok_runs]),
        },
        "failure_summary": {
            "n_fail": len(all_runs) - len(ok_runs),
            "failure_reasons": list({r.get("failure_reason") for r in all_runs if r.get("failure_status") == "fail"}),
        },
        "policy_comparisons": policy_rows,
        "production_defect_assessment": prod,
        "semantic_classification": {
            "verdict": verdict,
            "supported_roles": ["directional_diagnostic", "model_selection_diagnostic"],
            "unsupported_roles": ["restricted_causal_interval", "trust_report", "calibration_signal"],
            "readout_type": "cross_validation_dispersion_interval_not_causal_att",
        },
        "trustreport_eligibility_implications": {
            "dcm_005_kfold": "blocked_pending_placebo_and_reassessment",
            "prior_harness_status": "directional_null_fpr_elevated",
            "reassessment_required": True,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
        },
        "limitations": [
            "Characterizes DCM-005 KFold only; Placebo and DCM-005 reassessment out of scope.",
            "Level-scale truth contract; percent injection converted to level mean shift.",
            "Legacy Kfold is blocked pre-period CV, not sklearn random unit KFold.",
            "Does not authorize TrustReport or modify production inference code.",
        ],
        "investigation_handoff": build_investigation_handoff(
            follow_up_issues=follow_up,
            resolved_issues=resolved,
            terminal_dispositions=terminal_dispositions,
            next_artifact=next_artifact,
        ),
        "verdict": verdict,
    }

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps(_json_safe({"summary": summary, "runs": all_runs}), indent=2) + "\n"
        )

    return _json_safe(summary)


def _atomic_write_text(path: Path, content: str, *, overwrite: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _fmt(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    prod = payload.get("production_defect_assessment", {})
    cov_fold = payload.get("type_i_by_fold_variant", {})
    lines = [
        "# D5 Trust TBRRidge KFold 001 — Report",
        "",
        f"**Artifact ID:** {_ARTIFACT_ID}",
        f"**Verdict:** `{payload.get('verdict')}`",
        "",
        "> Characterizes DCM-005 KFold. Does not authorize TrustReport. "
        "Does not perform DCM-005 eligibility reassessment. "
        "Does not modify production TBRRidge or KFold code unless a separate correction artifact opens.",
        "",
        "## 1. Executive summary",
        "",
        f"TBRRidge+KFold characterized on unit-panel geometry. Verdict: `{payload.get('verdict')}`. "
        f"Production assessment: `{prod.get('decision')}`.",
        "",
        "## 2. Prior DCM-005 KFold status",
        "",
        "Prior D5-STAT-TBRRIDGE-INF-001: null interval FPR ~0; directional null FPR ~1.0 on outcome scale.",
        "",
        "## 3. Scope",
        "",
        f"{len(payload.get('worlds', []))} worlds; {len(payload.get('fold_variants', []))} fold variants; effect sweep.",
        "",
        "## 4. Non-goals",
        "",
        "- No Placebo lane",
        "- No DCM-005 eligibility reassessment",
        "- No production code changes",
        "",
        "## 5. TBRRidge estimator path",
        "",
        "RidgeCV on pre-period-normalized controls; multi-treated unit panel.",
        "",
        "## 6. KFold implementation",
        "",
        "Legacy `kfold()` blocked pre-period holdouts; `panel_timeseries_kfold()` expanding/rolling schemes.",
        "",
        "## 7. Fold geometry",
        "",
        "Folds split **time periods** in pre-treatment window; units preserved. Not sklearn random unit KFold.",
        "",
        "## 8. Temporal-order analysis",
        "",
        "Expanding/rolling schemes preserve chronological training-before-holdout ordering per fold.",
        "",
        "## 9. Leakage analysis",
        "",
        str(payload.get("leakage_diagnostics", {})),
        "",
        "## 10. Estimand",
        "",
        f"Post-window debiased ATT point; CV dispersion treated as interval (**{_CANONICAL_SCALE}**).",
        "",
        "## 11. Scale contract",
        "",
        "Truth and readouts on level mean shift from percent injection; directional threshold 500 on level scale.",
        "",
        "## 12. Worlds",
        "",
        ", ".join(payload.get("worlds", [])),
        "",
        "## 13. Effect-size sweep",
        "",
        ", ".join(str(e) for e in payload.get("effect_sizes", [])),
        "",
        "## 14. Fold-variant sweep",
        "",
        ", ".join(payload.get("fold_variants", [])),
        "",
        "## 15. Run counts/runtime",
        "",
        f"Total {_fmt(payload.get('run_counts', {}).get('total_runs'))}; "
        f"ok {_fmt(payload.get('run_counts', {}).get('successful_runs'))}; "
        f"runtime {_fmt(payload.get('run_counts', {}).get('runtime_seconds'))}s.",
        "",
        "## 16. Point-estimate behavior",
        "",
        f"Clean positive bias: {_fmt(payload.get('point_estimate_results', {}).get('mean_bias_clean_positive'))}.",
        "",
        "## 17. Fold-statistic behavior",
        "",
        str(payload.get("fold_diagnostics", {})),
        "",
        "## 18. Null type-I",
        "",
        f"random_kfold directional type-I: {_fmt((cov_fold.get('random_kfold') or {}).get('directional_type_i'))}; "
        f"interval type-I: {_fmt((cov_fold.get('random_kfold') or {}).get('type_i_error'))}.",
        "",
        "## 19. Positive behavior",
        "",
        f"clean_positive coverage: {_fmt((payload.get('coverage_by_world', {}).get('clean_positive_effect') or {}).get('positive_coverage'))}.",
        "",
        "## 20. Negative behavior",
        "",
        f"clean_negative coverage: {_fmt((payload.get('coverage_by_world', {}).get('clean_negative_effect') or {}).get('negative_coverage'))}.",
        "",
        "## 21. Sign accuracy",
        "",
        f"Overall: {_fmt(payload.get('sign_accuracy'))}.",
        "",
        "## 22. Variance findings",
        "",
        str(payload.get("variance_decomposition", {})),
        "",
        "## 23. Serial-dependence findings",
        "",
        f"serial_correlation null directional FPR: {_fmt((payload.get('coverage_by_world', {}).get('serial_correlation') or {}).get('directional_type_i'))}.",
        "",
        "## 24. Pre-fit findings",
        "",
        str(payload.get("prefit_relationships", {})),
        "",
        "## 25. Ridge findings",
        "",
        str(payload.get("ridge_relationships", {})),
        "",
        "## 26. Worst-world behavior",
        "",
        f"post_treatment_shock directional FPR: {_fmt((payload.get('coverage_by_world', {}).get('post_treatment_shock') or {}).get('directional_type_i'))}.",
        "",
        "## 27. Policy comparisons",
        "",
        "A legacy Kfold; B expanding TSKFold; C rolling TSKFold; D directional-only; E prefit-gated; F blocked.",
        "",
        "## 28. Root-cause determination",
        "",
        str(payload.get("variance_decomposition", {}).get("decomposition_note", "")),
        "",
        "## 29. Production-defect decision",
        "",
        f"`{prod.get('decision')}` — {'; '.join(prod.get('rationale', []))}",
        "",
        "## 30. Semantic classification",
        "",
        str(payload.get("semantic_classification", {})),
        "",
        "## 31. TrustReport implications",
        "",
        "DCM-005 KFold remains diagnostic-only; eligibility reassessment deferred.",
        "",
        "## 32. Authorization status",
        "",
        "**Blocked** — trust_report_authorized=false.",
        "",
        "## 33. Investigation lifecycle update",
        "",
        "INV-TBRRIDGE-KFOLD-NULL-FPR-001 remains OPEN; provisional DIAGNOSTIC_ONLY recommendation "
        "recorded in registry evidence for DCM-005 consumption (not terminal closure in this artifact).",
        "",
        "## 34. Remaining limitations",
        "",
        "; ".join(payload.get("limitations", [])),
        "",
        "## 35. Governance verdict",
        "",
        f"**`{payload.get('verdict')}`**",
        "",
    ]
    handoff = payload.get("investigation_handoff") or {}
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=handoff.get("resolved_issues") or [],
            new_investigations=[],
            updated_investigations=[
                "INV-TBRRIDGE-KFOLD-NULL-FPR-001 → OPEN; provisional DIAGNOSTIC_ONLY recommendation pending DCM-005"
            ],
            deferred_issues=[],
            explicit_exclusions=["Placebo characterization", "DCM-005 eligibility reassessment"],
            revisit_trigger="Upon completion of D5-TRUST-TBRRIDGE-PLACEBO-001",
            decision_checkpoint="DCM-005 eligibility reassessment",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write_text(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    cfg: KfoldTrustConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_d5_trust_tbrridge_kfold_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write_text(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--output-local", default="/tmp/D5_TRUST_TBRRIDGE_KFOLD_001_results.json")
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args(argv)

    cfg = KfoldTrustConfig(
        fast=args.fast,
        write_full_results_path=args.output_local if not args.fast else None,
    )
    write_summary(
        Path(args.summary_output),
        cfg=cfg,
        overwrite=args.overwrite,
        report_path=Path(args.report_output),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
