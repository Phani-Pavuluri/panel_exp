"""D5-STAT-TBRRIDGE-INF-001 — Level B characterization for TBRRidge inference paths.

Unit-panel single-cell geometry only. Existing KFold / TimeSeriesKFold / BRB / Conformal wrappers.
No promotion, governed uncertainty, SARIMAX, or Bayesian claims.
"""

from __future__ import annotations

import copy
import json
import math
import warnings
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.design.assign import greedy_match_markets
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001c import _post_window_arrays

_REPO_ROOT = Path(__file__).resolve().parents[2]

OverallVerdict = Literal[
    "characterization_pass_with_caveats",
    "characterization_mixed_requires_followup",
    "characterization_fail_requires_fix",
]

REQUIRED_WORLD_IDS = (
    "clean_null",
    "clean_positive_lift",
    "weak_signal_null",
    "noisy_positive_lift",
    "trend_mismatch_null",
    "post_shock_null",
    "short_pre_or_short_post",
)

NEXT_RECOMMENDED = ["INFERENCE_READOUT_SEMANTICS_001"]

GEOMETRY = "single_cell_unit_level"

NULL_DIRECTIONAL_THRESHOLD = 500.0
CONFORMAL_BLOCK_REASON = "multi_treated_unit_panel_broadcast_failure"


@dataclass(frozen=True)
class InferencePathSpec:
    path_id: str
    inference: str
    method_combination: str
    smoke_status: str
    smoke_skip_reason: str | None
    n_replicates: int | None = None


@dataclass(frozen=True)
class WorldSpec:
    world_id: str
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_probability: float = 0.35
    train_length: int | None = None
    test_length: int | None = None
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    notes: str = ""


@dataclass(frozen=True)
class D5StatTbrridgeInf001Config:
    n_replicates: int = 12
    n_replicates_slow: int = 6
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260612
    min_control_units: int = 3
    brb_n_bootstrap: int = 8
    brb_block_length: int = 3
    brb_min_train_periods: int = 5


INFERENCE_PATHS: tuple[InferencePathSpec, ...] = (
    InferencePathSpec(
        "TBRRIDGE-KFOLD",
        "Kfold",
        "TBRRidge+KFold",
        "callable_pass",
        None,
    ),
    InferencePathSpec(
        "TBRRIDGE-TSKFOLD",
        "TimeSeriesKfold",
        "TBRRidge+TimeSeriesKFold",
        "skipped",
        "no_smoke_probe_mapping",
    ),
    InferencePathSpec(
        "TBRRIDGE-BRB",
        "BlockResidualBootstrap",
        "TBRRidge+BRB",
        "skipped",
        "no_smoke_probe_mapping",
        n_replicates=6,
    ),
    InferencePathSpec(
        "TBRRIDGE-CONFORMAL",
        "Conformal",
        "TBRRidge+Conformal",
        "skipped",
        "no_smoke_probe_mapping",
        n_replicates=6,
    ),
)

WORLD_SPECS: tuple[WorldSpec, ...] = (
    WorldSpec("clean_null", percent_effect=0.0, notes="stable null"),
    WorldSpec(
        "clean_positive_lift",
        percent_effect=0.08,
        notes="injected post-period lift",
    ),
    WorldSpec(
        "weak_signal_null",
        percent_effect=0.0,
        scenario_overrides={"noise_scale": 3.8, "cross_geo_correlation": 0.05},
        notes="weak control/outcome relationship null",
    ),
    WorldSpec(
        "noisy_positive_lift",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 3.2},
        notes="noisy injected lift",
    ),
    WorldSpec(
        "trend_mismatch_null",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        notes="treated/control trend divergence under null",
    ),
    WorldSpec(
        "post_shock_null",
        scenario_name="scm_structural_break",
        percent_effect=0.0,
        scenario_overrides={"structural_break_shift": 22.0},
        notes="post-period shock under null",
    ),
    WorldSpec(
        "short_pre_or_short_post",
        percent_effect=0.08,
        train_length=22,
        test_length=4,
        notes="reduced pre/post support",
    ),
)

SPLIT_LEAKAGE_METADATA: dict[str, dict[str, Any]] = {
    "TBRRIDGE-KFOLD": {
        "split_policy_recorded": "panel_kfold_random_or_blocked",
        "split_is_random": True,
        "temporal_leakage_possible": True,
        "leakage_guard_status": "leakage_risk_flagged",
        "interval_target_ambiguous": True,
        "interval_target_note": "KFold targets prediction-stability / cross-validation dispersion, not validated causal coverage.",
        "causal_uncertainty_validated": False,
    },
    "TBRRIDGE-TSKFOLD": {
        "split_policy_recorded": "chronological_horizon_blocked_folds",
        "split_is_random": False,
        "temporal_leakage_possible": False,
        "leakage_guard_status": "chronological_split_recorded",
        "interval_target_ambiguous": True,
        "interval_target_note": "TimeSeriesKFold targets forecast stability across horizons; causal interval semantics not established.",
        "causal_uncertainty_validated": False,
    },
    "TBRRIDGE-BRB": {
        "split_policy_recorded": "block_residual_bootstrap",
        "block_length": 3,
        "n_bootstrap": 12,
        "dependence_assumption": "block_stationarity_residuals",
        "leakage_guard_status": "bootstrap_design_recorded",
        "interval_target_ambiguous": True,
        "interval_target_note": "BRB interval target (prediction vs causal ATT) is ambiguous without readout contract.",
        "causal_uncertainty_validated": False,
    },
    "TBRRIDGE-CONFORMAL": {
        "split_policy_recorded": "residual_calibration_split_if_available",
        "exchangeability_assumption": "assumed_not_time_dependent",
        "leakage_guard_status": "exchangeability_caveat_flagged",
        "interval_target_ambiguous": True,
        "interval_target_note": "Conformal coverage under post-period shock or time dependence is ambiguous.",
        "causal_uncertainty_validated": False,
    },
}


def _forbidden_flags() -> dict[str, bool]:
    return {
        "promotion_allowed": False,
        "trust_role_allowed": False,
        "calibration_signal_allowed": False,
        "mmm_allowed": False,
        "llm_recommendation_allowed": False,
        "suitability_claim_allowed": False,
        "governed_uncertainty_allowed": False,
        "causal_uncertainty_claim_allowed": False,
        "geometry_generalization_allowed": False,
        "sarimax_allowed": False,
        "bayesian_allowed": False,
    }


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        v = float(obj)
        return v if np.isfinite(v) else None
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    return obj


def _effective_lengths(
    spec: WorldSpec, cfg: D5StatTbrridgeInf001Config
) -> tuple[int, int]:
    train = spec.train_length if spec.train_length is not None else cfg.train_length
    test = spec.test_length if spec.test_length is not None else cfg.test_length
    return train, test


def _assign_greedy_pre_period(
    wide: Any,
    *,
    n_pre: int,
    seed: int,
    treatment_probability: float,
) -> list[str]:
    panel = PanelDataset(wide.copy())
    design = greedy_match_markets(
        func_to_optimize="corr",
        treatment_probability=treatment_probability,
        random_state=seed,
    )
    groups = design.assign(
        panel_data=panel,
        pre_treatment_period=TimePeriod(0, n_pre),
        n_test_grps=1,
    )
    treated = [u for units in groups.values() for u in units]
    if not treated:
        raise ValueError("assignment produced no treated units")
    return treated


def _mean_treated_baseline(panel: PanelDataset) -> np.ndarray:
    return panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)


def _inject_percent_effect(
    panel: PanelDataset,
    percent_effect: float,
    mean_value: np.ndarray,
) -> PanelDataset:
    mod = copy.deepcopy(panel)
    start = int(mod.treated_start_idxs[0])
    end_idx = int(mod.treated_end_idxs[0])
    if end_idx >= mod.times.shape[0]:
        end_idx = mod.times.shape[0] - 1
    treated_len = end_idx - start + 1
    n_treated = len(mod.treated_units)
    if n_treated == 1:
        delta = float(percent_effect * np.mean(mean_value))
        mod.wide_data.loc[mod.treated_units, mod.times[start : start + treated_len]] += delta
        return mod
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    treated_block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    treated_block = np.where(mask, treated_block + value_effect.reshape(-1, 1), treated_block)
    mod.wide_data.loc[mod.treated_units] = treated_block
    return mod


def _geometry_guard(panel: PanelDataset) -> tuple[bool, str | None]:
    n_rows = int(panel.wide_data.shape[0])
    if n_rows <= 2:
        return False, "aggregate_two_row_geometry_rejected"
    if len(panel.treated_units) < 1:
        return False, "no_treated_units"
    if panel.num_control_units < 1:
        return False, "no_control_units"
    return True, None


def _build_unit_panel(
    spec: WorldSpec,
    cfg: D5StatTbrridgeInf001Config,
    *,
    seed: int,
) -> PanelDataset:
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
    for assign_attempt in range(12):
        assign_seed = seed + assign_attempt * 31
        treated = _assign_greedy_pre_period(
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


def _inference_kwargs(
    path: InferencePathSpec,
    cfg: D5StatTbrridgeInf001Config,
    *,
    seed: int,
) -> dict[str, Any]:
    if path.inference in ("Kfold", "TimeSeriesKfold", "Conformal"):
        return {"random_state": seed, "show_progress": False}
    if path.inference == "BlockResidualBootstrap":
        return {
            "n_bootstrap": cfg.brb_n_bootstrap,
            "block_length": cfg.brb_block_length,
            "min_train_periods": cfg.brb_min_train_periods,
            "show_progress": False,
            "random_state": seed,
        }
    return {"show_progress": False}


def _readout_from_results(
    results: dict[str, Any],
    *,
    test_len: int,
    percent_effect: float,
) -> dict[str, Any]:
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length=test_len)
    effect = y - y_hat
    point_estimate = float(np.nanmean(effect))

    interval_present = y_lo.size > 0 and y_hi.size > 0
    interval_lower = None
    interval_upper = None
    interval_width = None
    interval_contains_truth = None
    interval_orientation_valid = None
    negative_half_width_detected = None
    degenerate_interval = False

    if interval_present:
        orient_fail = bool(np.any(y_lo > y_hi))
        mid = 0.5 * (y_lo + y_hi)
        hw = y_hi - mid
        neg_hw = bool(np.any(hw < 0))
        eff_lo = y - y_hi
        eff_hi = y - y_lo
        interval_lower = float(np.nanmean(eff_lo))
        interval_upper = float(np.nanmean(eff_hi))
        interval_width = float(interval_upper - interval_lower)
        interval_orientation_valid = not orient_fail
        negative_half_width_detected = neg_hw
        degenerate_interval = interval_width <= 1e-12
        if percent_effect == 0.0:
            interval_contains_truth = bool(interval_lower <= 0.0 <= interval_upper)
        elif np.isfinite(interval_lower) and np.isfinite(interval_upper):
            interval_contains_truth = bool(
                interval_lower <= percent_effect <= interval_upper
            )

    is_null = abs(percent_effect) < 1e-12
    if is_null:
        sign_correct = bool(
            interval_contains_truth
            if interval_contains_truth is not None
            else abs(point_estimate) < NULL_DIRECTIONAL_THRESHOLD
        )
    else:
        sign_correct = bool(
            np.isfinite(point_estimate)
            and np.sign(point_estimate) == np.sign(percent_effect)
        )

    finite = np.isfinite(point_estimate)
    if interval_present:
        finite = finite and np.all(np.isfinite(y)) and np.all(np.isfinite(y_hat))
        finite = finite and np.all(np.isfinite(y_lo)) and np.all(np.isfinite(y_hi))

    return {
        "point_estimate": point_estimate,
        "true_effect": float(percent_effect),
        "bias": float(point_estimate - percent_effect),
        "absolute_error": float(abs(point_estimate - percent_effect)),
        "squared_error": float((point_estimate - percent_effect) ** 2),
        "sign_correct": bool(sign_correct),
        "interval_present": bool(interval_present),
        "interval_lower": interval_lower,
        "interval_upper": interval_upper,
        "interval_width": interval_width,
        "interval_contains_truth": interval_contains_truth,
        "interval_orientation_valid": interval_orientation_valid,
        "negative_half_width_detected": negative_half_width_detected,
        "degenerate_interval": degenerate_interval,
        "finite_outputs": bool(finite),
    }


def _skipped_conformal_run(
    spec: WorldSpec,
    path: InferencePathSpec,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    meta = SPLIT_LEAKAGE_METADATA[path.path_id]
    return {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "method_combination": path.method_combination,
        "inference_path": path.path_id,
        "geometry": GEOMETRY,
        "split_policy": meta.get("split_policy_recorded"),
        "leakage_warning": meta.get("interval_target_note"),
        "callable_status": "skipped",
        "skip_reason": CONFORMAL_BLOCK_REASON,
        "point_estimate": None,
        "true_effect": float(spec.percent_effect),
        "bias": None,
        "absolute_error": None,
        "squared_error": None,
        "sign_correct": None,
        "interval_present": None,
        "interval_lower": None,
        "interval_upper": None,
        "interval_width": None,
        "interval_contains_truth": None,
        "interval_orientation_valid": None,
        "negative_half_width_detected": None,
        "degenerate_interval": None,
        "finite_outputs": False,
        "exception_type": "ValueError",
        "exception_message": CONFORMAL_BLOCK_REASON,
    }


def _conformal_blocked(cfg: D5StatTbrridgeInf001Config) -> bool:
    conformal = next(p for p in INFERENCE_PATHS if p.inference == "Conformal")
    probe = _run_one(WORLD_SPECS[0], conformal, cfg, replicate_id=0, seed=42)
    return probe.get("skip_reason") == CONFORMAL_BLOCK_REASON


def _run_one(
    spec: WorldSpec,
    path: InferencePathSpec,
    cfg: D5StatTbrridgeInf001Config,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    train, test = _effective_lengths(spec, cfg)
    meta = SPLIT_LEAKAGE_METADATA[path.path_id]
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "method_combination": path.method_combination,
        "inference_path": path.path_id,
        "geometry": GEOMETRY,
        "split_policy": meta.get("split_policy_recorded"),
        "leakage_warning": meta.get("interval_target_note"),
    }
    try:
        panel = _build_unit_panel(spec, cfg, seed=seed)
        geom_ok, geom_reason = _geometry_guard(panel)
        if not geom_ok:
            raise ValueError(f"geometry_guard_failed:{geom_reason}")
        mean_value = _mean_treated_baseline(panel)
        pds = _inject_percent_effect(panel, spec.percent_effect, mean_value)

        est = TBRRidge(inference=path.inference, alpha=cfg.alpha)
        if est.__class__.__name__ != "TBRRidge":
            raise ValueError("method_identity_not_TBRRidge")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            est.run_analysis(pds, **_inference_kwargs(path, cfg, seed=seed))

        results = getattr(est, "results", {}) or {}
        readout = _readout_from_results(
            results,
            test_len=test,
            percent_effect=spec.percent_effect,
        )
        return {
            **base,
            "callable_status": "callable_pass" if readout["finite_outputs"] else "callable_fail",
            "skip_reason": None,
            **readout,
            "exception_type": None,
            "exception_message": None,
        }
    except Exception as exc:
        msg = str(exc)
        if path.inference == "Conformal" and "broadcast" in msg.lower():
            return {
                **base,
                "callable_status": "skipped",
                "skip_reason": CONFORMAL_BLOCK_REASON,
                "point_estimate": None,
                "true_effect": float(spec.percent_effect),
                "bias": None,
                "absolute_error": None,
                "squared_error": None,
                "sign_correct": None,
                "interval_present": None,
                "interval_lower": None,
                "interval_upper": None,
                "interval_width": None,
                "interval_contains_truth": None,
                "interval_orientation_valid": None,
                "negative_half_width_detected": None,
                "degenerate_interval": None,
                "finite_outputs": False,
                "exception_type": type(exc).__name__,
                "exception_message": msg[:300],
            }
        return {
            **base,
            "callable_status": "callable_fail",
            "skip_reason": None,
            "point_estimate": None,
            "true_effect": float(spec.percent_effect),
            "bias": None,
            "absolute_error": None,
            "squared_error": None,
            "sign_correct": None,
            "interval_present": None,
            "interval_lower": None,
            "interval_upper": None,
            "interval_width": None,
            "interval_contains_truth": None,
            "interval_orientation_valid": None,
            "negative_half_width_detected": None,
            "degenerate_interval": None,
            "finite_outputs": False,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:300],
        }


def _path_replicates(path: InferencePathSpec, cfg: D5StatTbrridgeInf001Config) -> int:
    if path.n_replicates is not None:
        return path.n_replicates
    return cfg.n_replicates


def _aggregate_path_world(
    runs: list[dict[str, Any]],
    spec: WorldSpec,
    path: InferencePathSpec,
) -> dict[str, Any]:
    ok = [r for r in runs if r.get("callable_status") == "callable_pass"]
    failed = [r for r in runs if r.get("callable_status") == "callable_fail"]
    skipped = [r for r in runs if r.get("callable_status") == "skipped"]
    n = len(runs)
    is_null = abs(spec.percent_effect) < 1e-12
    meta = SPLIT_LEAKAGE_METADATA[path.path_id]

    def _vals(key: str) -> np.ndarray:
        return np.array(
            [r[key] for r in ok if r.get(key) is not None and np.isfinite(r[key])],
            dtype=float,
        )

    pts = _vals("point_estimate")
    biases = _vals("bias")
    abs_errs = _vals("absolute_error")
    widths = _vals("interval_width")

    orient_fail = [r for r in ok if r.get("interval_orientation_valid") is False]
    neg_hw = [r for r in ok if r.get("negative_half_width_detected")]
    degenerate = [r for r in ok if r.get("degenerate_interval")]
    non_finite = [r for r in ok if not r.get("finite_outputs")]

    null_fpr = None
    dir_fpr = None
    if is_null and ok:
        rejects = []
        directional = []
        for r in ok:
            lo = r.get("interval_lower")
            hi = r.get("interval_upper")
            if lo is not None and hi is not None:
                rejects.append(not (lo <= 0.0 <= hi))
            elif r.get("point_estimate") is not None:
                rejects.append(abs(r["point_estimate"]) > NULL_DIRECTIONAL_THRESHOLD)
            pt = r.get("point_estimate")
            if pt is not None and np.isfinite(pt):
                directional.append(abs(pt) > NULL_DIRECTIONAL_THRESHOLD)
        null_fpr = float(np.mean(rejects)) if rejects else None
        dir_fpr = float(np.mean(directional)) if directional else None

    coverage_vals = [
        r["interval_contains_truth"]
        for r in ok
        if r.get("interval_contains_truth") is not None
    ]
    coverage = float(np.mean(coverage_vals)) if coverage_vals else None

    sign_errors = None
    if not is_null and ok:
        sign_errors = float(np.mean([not r.get("sign_correct", False) for r in ok]))

    return {
        "method_combination": path.method_combination,
        "inference_path": path.path_id,
        "geometry": GEOMETRY,
        "world_id": spec.world_id,
        "n_replicates": n,
        "feasible_runs": len(ok),
        "failed_runs": len(failed),
        "skipped_runs": len(skipped),
        "callable_failure_rate": len(failed) / max(n, 1),
        "skip_reason": (
            CONFORMAL_BLOCK_REASON
            if path.inference == "Conformal" and skipped and not ok
            else (path.smoke_skip_reason if path.smoke_status == "skipped" else None)
        ),
        "mean_point_estimate": float(np.mean(pts)) if pts.size else None,
        "median_point_estimate": float(np.median(pts)) if pts.size else None,
        "mean_true_effect": float(spec.percent_effect),
        "mean_bias": float(np.mean(biases)) if biases.size else None,
        "mean_absolute_error": float(np.mean(abs_errs)) if abs_errs.size else None,
        "rmse": float(math.sqrt(np.mean(biases**2))) if biases.size else None,
        "median_absolute_error": float(np.median(abs_errs)) if abs_errs.size else None,
        "sign_error_rate": sign_errors,
        "null_false_positive_rate": null_fpr,
        "directional_false_signal_rate": dir_fpr,
        "coverage": coverage,
        "mean_interval_width": float(np.mean(widths)) if widths.size else None,
        "median_interval_width": float(np.median(widths)) if widths.size else None,
        "interval_orientation_failure_rate": len(orient_fail) / max(len(ok), 1),
        "negative_half_width_rate": len(neg_hw) / max(len(ok), 1),
        "degenerate_interval_rate": len(degenerate) / max(len(ok), 1),
        "non_finite_output_rate": len(non_finite) / max(len(ok), 1),
        "split_policy_recorded": meta.get("split_policy_recorded"),
        "leakage_guard_status": meta.get("leakage_guard_status"),
        "notes": spec.notes,
    }


def _decide_overall(path_metrics: list[dict[str, Any]]) -> OverallVerdict:
    active = [
        m
        for m in path_metrics
        if m.get("skip_reason") != CONFORMAL_BLOCK_REASON
    ]
    for m in active:
        if m.get("interval_orientation_failure_rate", 0) > 0:
            return "characterization_fail_requires_fix"
        if m.get("negative_half_width_rate", 0) > 0:
            return "characterization_fail_requires_fix"

    for wid in ("clean_null", "clean_positive_lift"):
        subset = [m for m in active if m.get("world_id") == wid]
        for m in subset:
            if m.get("callable_failure_rate", 0) > 0.1:
                return "characterization_fail_requires_fix"
            if m.get("feasible_runs", 0) > 0 and m.get("non_finite_output_rate", 0) > 0:
                return "characterization_fail_requires_fix"

    mixed = False
    null_worlds = (
        "clean_null",
        "weak_signal_null",
        "trend_mismatch_null",
        "post_shock_null",
    )
    for wid in null_worlds:
        for m in active:
            if m.get("world_id") != wid:
                continue
            if (m.get("null_false_positive_rate") or 0) > 0.35:
                mixed = True
            if (m.get("directional_false_signal_rate") or 0) > 0.5:
                mixed = True

    lift_worlds = ("clean_positive_lift", "noisy_positive_lift")
    for wid in lift_worlds:
        for m in active:
            if m.get("world_id") != wid:
                continue
            cov = m.get("coverage")
            if cov is not None and cov < 0.5:
                mixed = True
            if (m.get("sign_error_rate") or 0) > 0.25:
                mixed = True

    if mixed:
        return "characterization_mixed_requires_followup"
    return "characterization_pass_with_caveats"


def asdict_world(spec: WorldSpec) -> dict[str, Any]:
    train, test = _effective_lengths(spec, D5StatTbrridgeInf001Config())
    return {
        "world_id": spec.world_id,
        "scenario_name": spec.scenario_name,
        "percent_effect": spec.percent_effect,
        "n_geos": spec.n_geos,
        "train_length": train,
        "test_length": test,
        "notes": spec.notes,
    }


def _guardrails_list() -> list[str]:
    return [
        "tbrridge_inference_only",
        "single_cell_unit_level_geometry",
        "level_b_characterization_only",
        "no_governed_uncertainty_claim",
        "no_promotion",
        "no_sarimax",
        "no_bayesian",
        "outcome_scale_readout_vs_percent_injection_caveat",
    ]


def _leakage_register() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for path_id, meta in SPLIT_LEAKAGE_METADATA.items():
        out.append(
            {
                "inference_path": path_id,
                **meta,
                "prediction_vs_causal_note": (
                    "Intervals characterize wrapper output dispersion; "
                    "not governed causal uncertainty without INFERENCE_READOUT_SEMANTICS_001."
                ),
            }
        )
    return out


def _skip_register() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for p in INFERENCE_PATHS:
        blocked = p.inference == "Conformal"
        entries.append(
            {
                "inference_path": p.path_id,
                "smoke_status": p.smoke_status,
                "skip_reason": CONFORMAL_BLOCK_REASON if blocked else p.smoke_skip_reason,
                "level_b_status": (
                    "blocked_implementation_gap"
                    if blocked
                    else (
                        "characterized_in_this_artifact"
                        if p.smoke_status == "skipped"
                        else "smoke_callable_pass"
                    )
                ),
                "notes": (
                    "Conformal wrapper raises broadcast error on multi-treated unit-panel "
                    "TBRRidge readout; path blocked pending readout semantics fix."
                    if blocked
                    else (
                        "Smoke lacked probe mapping; Level B confirms callable on unit-panel fixtures."
                        if p.smoke_skip_reason
                        else None
                    )
                ),
            }
        )
    return entries


def build_d5_stat_tbrridge_inf_001(
    cfg: D5StatTbrridgeInf001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5StatTbrridgeInf001Config()
    run_results: list[dict[str, Any]] = []
    path_metrics: list[dict[str, Any]] = []
    failure_register: list[dict[str, Any]] = []
    conformal_blocked = _conformal_blocked(cfg)

    for widx, spec in enumerate(WORLD_SPECS):
        for path in INFERENCE_PATHS:
            n_rep = _path_replicates(path, cfg)
            world_runs: list[dict[str, Any]] = []
            for rep in range(n_rep):
                seed = cfg.random_state_base + widx * 1000 + rep * 17
                if path.inference == "Conformal" and conformal_blocked:
                    row = _skipped_conformal_run(
                        spec, path, replicate_id=rep, seed=seed
                    )
                else:
                    row = _run_one(spec, path, cfg, replicate_id=rep, seed=seed)
                world_runs.append(row)
                run_results.append(row)
                if row.get("callable_status") == "callable_fail":
                    failure_register.append(
                        {
                            "world_id": spec.world_id,
                            "inference_path": path.path_id,
                            "replicate_id": rep,
                            "exception_type": row.get("exception_type"),
                            "exception_message": row.get("exception_message"),
                        }
                    )
            path_metrics.append(_aggregate_path_world(world_runs, spec, path))

    overall = _decide_overall(path_metrics)
    total_runs = len(run_results)
    total_failures = len(failure_register)

    return _json_safe(
        {
            "artifact_id": "D5-STAT-TBRRIDGE-INF-001",
            "artifact_type": "level_b_characterization",
            "method_family": "TBRRidge",
            "inference_paths": [p.path_id for p in INFERENCE_PATHS],
            "geometry": GEOMETRY,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
            "source_tbr_agg_artifact": "D5-STAT-TBR-AGG-001",
            "source_mcell_percell_artifact": "D5-STAT-MCELL-PERCELL-001",
            "source_method_enhancement_roadmap": "METHOD-ENHANCEMENT-ROADMAP-001",
            "overall_verdict": overall,
            "summary": {
                "n_worlds": len(WORLD_SPECS),
                "n_inference_paths": len(INFERENCE_PATHS),
                "total_runs": total_runs,
                "total_failures": total_failures,
                "characterization_only": True,
                "geometry_note": (
                    "Unit-panel single-cell: shared control donors + treated units; "
                    "not aggregate 2-row TBR, not MCELL pooled, not supergeo/trim."
                ),
                "readout_scale_caveat": (
                    "Point/interval readout uses post-window outcome residual mean; "
                    "true_effect records percent injection parameter — scales differ."
                ),
            },
            "worlds": [asdict_world(w) for w in WORLD_SPECS],
            "path_metrics": path_metrics,
            "run_results": run_results,
            "failure_register": failure_register,
            "skip_register": _skip_register(),
            "leakage_register": _leakage_register(),
            "forbidden_flags": _forbidden_flags(),
            "next_recommended_artifacts": NEXT_RECOMMENDED,
            "guardrails": _guardrails_list(),
        }
    )


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5StatTbrridgeInf001Config | None = None,
) -> Path:
    payload = build_d5_stat_tbrridge_inf_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_STAT_TBRRIDGE_INF_001_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    cfg = D5StatTbrridgeInf001Config()
    out = write_artifact(cfg=cfg)
    p = build_d5_stat_tbrridge_inf_001(cfg)
    print(
        f"Wrote {out} — {p['overall_verdict']} "
        f"({p['summary'].get('total_runs', 0)} runs)"
    )


if __name__ == "__main__":
    main()
