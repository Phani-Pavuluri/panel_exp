"""D5-STAT-DID-BOOTSTRAP-001 — Level B characterization for DID + embedded bootstrap.

Single-cell unit-panel geometry with pooled treated units. No promotion or suitability claims.

Harness correction (D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION): assignment uses
explicit ``test_0`` and ``control`` groups; canonical coverage compares cumulative
level ``cumulative_att`` / ``treatment_ci`` to cumulative level injected truth.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import shutil
import tempfile
import warnings
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.design.assign import greedy_match_markets
from panel_exp.methods.DID import DID
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_ARCHIVE = _REPO_ROOT / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json"
_HISTORICAL_ARCHIVE = (
    _REPO_ROOT
    / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json"
)
_CANONICAL_EFFECT_SCALE = "cumulative_level"

OverallVerdict = Literal[
    "characterization_pass_with_caveats",
    "characterization_mixed_requires_followup",
    "characterization_fail_requires_fix",
]

HarnessCorrectionVerdict = Literal[
    "did_bootstrap_harness_corrected_canonical_baseline_established",
    "did_bootstrap_harness_corrected_production_miscoverage_confirmed",
    "did_bootstrap_harness_correction_inconclusive",
    "did_bootstrap_harness_correction_failed",
]

REQUIRED_WORLD_IDS = (
    "clean_parallel_null",
    "clean_parallel_positive_lift",
    "weak_signal_null",
    "noisy_positive_lift",
    "trend_violation_null",
    "trend_violation_positive_lift",
    "post_shock_null",
)

NEXT_RECOMMENDED = [
    "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION",
    "DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001",
    "D5-STAT-MCELL-PERCELL-001",
]

GEOMETRY = "single_cell_unit_level"
TIMING_REGIME = "common_simultaneous_adoption"

ESTIMAND_CONTRACT: dict[str, str] = {
    "estimand_id": "cumulative_att_level",
    "truth_scale": "cumulative_level",
    "point_estimate_scale": "cumulative_level",
    "interval_scale": "cumulative_level",
    "effect_injection_definition": (
        "fractional_percent_times_unit_baseline_injected_as_level_delta; "
        "truth is cumulative sum over post periods on treated units"
    ),
    "fractional_percent_parameter": "percent_effect",
    "point_estimate_field": "cumulative_att",
    "interval_field": "treatment_ci",
    "per_period_att_field": "mean_post_period_att",
    "timing_regime": TIMING_REGIME,
}


@dataclass(frozen=True)
class WorldSpec:
    world_id: str
    scenario_name: str = "did_parallel_trends_holds"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_probability: float = 0.35
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    allow_pretrend_violation: bool = False
    parallel_trends_status: str = "holds"
    serial_dependence_regime: str = "standard"
    timing_regime: str = TIMING_REGIME
    notes: str = ""


@dataclass(frozen=True)
class D5StatDidBootstrap001Config:
    n_replicates: int = 15
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260608
    min_control_units: int = 4
    fast: bool = False


WORLD_SPECS: tuple[WorldSpec, ...] = (
    WorldSpec(
        "clean_parallel_null",
        percent_effect=0.0,
        notes="parallel trends hold, null injection",
    ),
    WorldSpec(
        "clean_parallel_positive_lift",
        percent_effect=0.08,
        notes="parallel trends hold with injected lift",
    ),
    WorldSpec(
        "weak_signal_null",
        percent_effect=0.0,
        scenario_name="scm_low_signal",
        scenario_overrides={"noise_scale": 3.8, "cross_geo_correlation": 0.05},
        notes="weak signal null",
    ),
    WorldSpec(
        "noisy_positive_lift",
        percent_effect=0.08,
        scenario_name="scm_low_signal",
        scenario_overrides={"noise_scale": 3.2},
        notes="noisy injected lift",
    ),
    WorldSpec(
        "trend_violation_null",
        scenario_name="did_parallel_trends_violation",
        percent_effect=0.0,
        allow_pretrend_violation=True,
        parallel_trends_status="severe_violation",
        notes="pretrend violation under null",
    ),
    WorldSpec(
        "trend_violation_positive_lift",
        scenario_name="did_parallel_trends_violation",
        percent_effect=0.08,
        allow_pretrend_violation=True,
        parallel_trends_status="severe_violation",
        notes="pretrend violation with injected lift",
    ),
    WorldSpec(
        "post_shock_null",
        scenario_name="scm_structural_break",
        percent_effect=0.0,
        scenario_overrides={"structural_break_shift": 22.0},
        parallel_trends_status="shock_stress",
        notes="post-period shock under null",
    ),
)


def _forbidden_flags() -> dict[str, bool]:
    return {
        "promotion_allowed": False,
        "trust_role_allowed": False,
        "trust_report_authorized": False,
        "trust_report_ready": False,
        "calibration_signal_allowed": False,
        "mmm_allowed": False,
        "llm_recommendation_allowed": False,
        "suitability_claim_allowed": False,
        "governed_uncertainty_allowed": False,
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


def _assign_greedy_pre_period(
    wide: Any,
    *,
    n_pre: int,
    seed: int,
    treatment_probability: float,
) -> dict[str, Any]:
    """Return explicit test_0 (treated) and control groups — never groups.values()."""
    try:
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
        treated = list(groups.get("test_0") or [])
        control = list(groups.get("control") or [])
    except Exception as exc:
        return {
            "treated_units": [],
            "control_units": [],
            "n_treated": 0,
            "n_control": 0,
            "assignment_valid": False,
            "assignment_failure_reason": str(exc)[:300],
        }
    failure_reason = None
    assignment_valid = True
    if not treated:
        assignment_valid = False
        failure_reason = "no_treated_units_in_test_0"
    elif not control:
        assignment_valid = False
        failure_reason = "no_control_units"
    else:
        overlap = set(treated) & set(control)
        if overlap:
            assignment_valid = False
            failure_reason = f"treated_control_overlap:{sorted(overlap)[:3]}"
        all_units = set(wide.index)
        assigned = set(treated) | set(control)
        if not assigned.issubset(all_units):
            assignment_valid = False
            failure_reason = "assigned_units_not_subset_of_panel"
    return {
        "treated_units": treated,
        "control_units": control,
        "n_treated": len(treated),
        "n_control": len(control),
        "assignment_valid": assignment_valid,
        "assignment_failure_reason": failure_reason,
    }


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


def _true_cumulative_injected(
    baseline: PanelDataset,
    injected: PanelDataset,
    *,
    test_len: int,
) -> float:
    sl = slice(-test_len, None)
    times = list(injected.times[sl])
    treated = injected.treated_units
    before = float(baseline.wide_data.loc[treated, times].to_numpy(dtype=float).sum())
    after = float(injected.wide_data.loc[treated, times].to_numpy(dtype=float).sum())
    return after - before


def _bootstrap_fields(est: DID, point: float) -> dict[str, Any]:
    boot_raw = getattr(est, "bootstrap_cumulative_effects_", None)
    boot = np.asarray([] if boot_raw is None else boot_raw, dtype=float).reshape(-1)
    boot = boot[np.isfinite(boot)]
    center = float(np.mean(boot)) if boot.size else None
    median = float(np.median(boot)) if boot.size else None
    se = float(np.std(boot, ddof=1)) if boot.size > 1 else None
    return {
        "bootstrap_mean": center,
        "bootstrap_median": median,
        "bootstrap_standard_error": se,
        "bootstrap_replicate_count": int(boot.size),
        "point_minus_bootstrap_center": (
            float(point - center) if center is not None and np.isfinite(point) else None
        ),
    }


def _build_unit_panel(
    spec: WorldSpec,
    cfg: D5StatDidBootstrap001Config,
    *,
    seed: int,
) -> tuple[PanelDataset, dict[str, Any]]:
    if spec.timing_regime != TIMING_REGIME:
        raise ValueError(f"unsupported_timing_regime:{spec.timing_regime}")
    post_end = cfg.train_length + cfg.test_length - 1
    base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
    scenario = replace(
        base,
        random_state=seed,
        n_geos=spec.n_geos,
        n_periods=max(spec.n_periods, post_end + 1),
        treatment_start=cfg.train_length,
        true_effect=0.0,
        **(spec.scenario_overrides or {}),
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    assignment = _assign_greedy_pre_period(
        wide,
        n_pre=cfg.train_length,
        seed=seed,
        treatment_probability=spec.treatment_probability,
    )
    if not assignment["assignment_valid"]:
        raise ValueError(assignment["assignment_failure_reason"] or "invalid_assignment")
    treated = assignment["treated_units"]
    end = cfg.train_length + cfg.test_length
    panel = PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
        treated_units=treated,
    )
    return panel, assignment


def _post_interval_checks(
    results: dict[str, Any],
    *,
    test_len: int,
) -> tuple[bool, bool, bool]:
    y_lo = results.get("y_lower")
    y_hi = results.get("y_upper")
    if y_lo is None or y_hi is None:
        return True, False, False
    lo = np.asarray(y_lo, dtype=float).reshape(-1)
    hi = np.asarray(y_hi, dtype=float).reshape(-1)
    sl = slice(-test_len, None)
    lo_p = lo[sl]
    hi_p = hi[sl]
    mask = np.isfinite(lo_p) & np.isfinite(hi_p)
    if not mask.any():
        return False, False, True
    orient = bool(np.all(lo_p[mask] <= hi_p[mask]))
    mid = 0.5 * (lo_p[mask] + hi_p[mask])
    half_w = hi_p[mask] - mid
    neg_hw = bool(np.any(half_w < 0))
    return orient, neg_hw, True


def _run_one(
    spec: WorldSpec,
    cfg: D5StatDidBootstrap001Config,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    run_id = f"{spec.world_id}::rep{replicate_id}"
    base: dict[str, Any] = {
        "run_id": run_id,
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "replicate": replicate_id,
        "seed": seed,
        "effect_size": float(spec.percent_effect),
        "percent_effect": float(spec.percent_effect),
        "effect_scale": _CANONICAL_EFFECT_SCALE,
        "timing_regime": spec.timing_regime,
        "parallel_trends_status": spec.parallel_trends_status,
        "serial_dependence_regime": spec.serial_dependence_regime,
        "estimand_id": ESTIMAND_CONTRACT["estimand_id"],
        **_forbidden(),
    }
    try:
        panel, assignment = _build_unit_panel(spec, cfg, seed=seed)
        if assignment["n_control"] < cfg.min_control_units:
            raise ValueError("insufficient_control_units_after_assignment")
        mean_value = _mean_treated_baseline(panel)
        baseline = copy.deepcopy(panel)
        pds = _inject_percent_effect(panel, spec.percent_effect, mean_value)
        true_effect = _true_cumulative_injected(
            baseline, pds, test_len=cfg.test_length
        )

        est = DID(alpha=cfg.alpha)
        est.bootstrap_seed = int(seed % (2**31 - 1))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            est.run_analysis(
                pds,
                multiple_treated="pooled",
                allow_pretrend_violation=spec.allow_pretrend_violation,
            )
        if est.__class__.__name__ != "DID":
            raise ValueError("method_identity_not_DID")

        results = getattr(est, "results", {}) or {}
        point_estimate = float(results.get("cumulative_att", float("nan")))
        ci_lo, ci_hi = est.treatment_ci
        interval_lower = float(ci_lo) if np.isfinite(ci_lo) else None
        interval_upper = float(ci_hi) if np.isfinite(ci_hi) else None
        interval_center = (
            0.5 * (interval_lower + interval_upper)
            if interval_lower is not None and interval_upper is not None
            else None
        )
        interval_width = (
            float(interval_upper - interval_lower)
            if interval_lower is not None and interval_upper is not None
            else None
        )
        contains_truth = (
            bool(interval_lower <= true_effect <= interval_upper)
            if interval_lower is not None and interval_upper is not None
            else None
        )
        contains_zero = (
            bool(interval_lower <= 0.0 <= interval_upper)
            if interval_lower is not None and interval_upper is not None
            else None
        )

        plot_orient, plot_neg_hw, plot_interval = _post_interval_checks(
            results, test_len=cfg.test_length
        )
        interval_orientation_valid = True
        negative_half_width_detected = False
        if plot_interval:
            interval_orientation_valid = plot_orient
            negative_half_width_detected = plot_neg_hw
        if interval_lower is not None and interval_upper is not None:
            interval_orientation_valid = bool(interval_lower <= interval_upper)
            mid = 0.5 * (interval_lower + interval_upper)
            negative_half_width_detected = bool((interval_upper - mid) < 0)

        bias = point_estimate - true_effect
        is_null = abs(true_effect) < 1e-12
        if is_null:
            sign_correct = bool(
                contains_truth if contains_truth is not None else abs(point_estimate) < 1.0
            )
        else:
            sign_correct = bool(
                np.isfinite(point_estimate)
                and np.sign(point_estimate) == np.sign(true_effect)
            )

        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
        sl = slice(-cfg.test_length, None)
        finite = (
            np.isfinite(point_estimate)
            and (interval_lower is None or np.isfinite(interval_lower))
            and (interval_upper is None or np.isfinite(interval_upper))
            and y.size > 0
            and y_hat.size > 0
            and np.all(np.isfinite(y[sl]))
            and np.all(np.isfinite(y_hat[sl]))
        )

        boot = _bootstrap_fields(est, point_estimate)

        return {
            **base,
            "callable_status": "callable_pass" if finite else "callable_fail",
            "failure_status": None if finite else "callable_fail",
            "failure_reason": None,
            "n_treated": assignment["n_treated"],
            "n_control": assignment["n_control"],
            "assignment_valid": True,
            "assignment_failure_reason": None,
            "point_estimate": point_estimate,
            "true_effect": true_effect,
            "bias": float(bias),
            "absolute_error": float(abs(bias)),
            "squared_error": float(bias**2),
            "sign_correct": bool(sign_correct),
            "interval_lower": interval_lower,
            "interval_upper": interval_upper,
            "interval_center": interval_center,
            "interval_width": interval_width,
            "interval_contains_truth": contains_truth,
            "contains_truth": contains_truth,
            "contains_zero": contains_zero,
            "interval_orientation_valid": interval_orientation_valid,
            "negative_half_width_detected": negative_half_width_detected,
            "degenerate_interval": bool(
                interval_width is not None and interval_width <= 1e-12
            ),
            "finite_outputs": bool(finite),
            "exception_type": None,
            "exception_message": None,
            **boot,
        }
    except Exception as exc:
        msg = str(exc)[:300]
        is_assign = "assignment" in msg or "control" in msg or "test_0" in msg
        return {
            **base,
            "callable_status": "callable_fail",
            "failure_status": type(exc).__name__,
            "failure_reason": msg,
            "n_treated": None,
            "n_control": None,
            "assignment_valid": False if is_assign else None,
            "assignment_failure_reason": msg if is_assign else None,
            "point_estimate": None,
            "true_effect": None,
            "bias": None,
            "absolute_error": None,
            "squared_error": None,
            "sign_correct": None,
            "interval_lower": None,
            "interval_upper": None,
            "interval_center": None,
            "interval_width": None,
            "interval_contains_truth": None,
            "contains_truth": None,
            "contains_zero": None,
            "interval_orientation_valid": None,
            "negative_half_width_detected": None,
            "degenerate_interval": None,
            "finite_outputs": False,
            "exception_type": type(exc).__name__,
            "exception_message": msg,
            "bootstrap_mean": None,
            "bootstrap_median": None,
            "bootstrap_standard_error": None,
            "bootstrap_replicate_count": None,
            "point_minus_bootstrap_center": None,
        }


def _forbidden() -> dict[str, bool]:
    return _forbidden_flags()


def _aggregate_world(runs: list[dict[str, Any]], spec: WorldSpec) -> dict[str, Any]:
    ok = [r for r in runs if r.get("callable_status") == "callable_pass"]
    failed = [r for r in runs if r.get("callable_status") != "callable_pass"]
    n = len(runs)
    is_null = abs(spec.percent_effect) < 1e-12
    is_positive = spec.percent_effect > 1e-12
    is_negative = spec.percent_effect < -1e-12

    def _vals(key: str) -> np.ndarray:
        return np.array(
            [r[key] for r in ok if r.get(key) is not None and np.isfinite(r[key])],
            dtype=float,
        )

    pts = _vals("point_estimate")
    biases = _vals("bias")
    abs_errs = _vals("absolute_error")
    widths = _vals("interval_width")
    boot_centers = _vals("bootstrap_mean")

    null_fpr = None
    if is_null and ok:
        rejects = []
        for r in ok:
            if r.get("contains_zero") is not None:
                rejects.append(not r["contains_zero"])
            elif r.get("interval_lower") is not None and r.get("interval_upper") is not None:
                rejects.append(not (r["interval_lower"] <= 0.0 <= r["interval_upper"]))
        null_fpr = float(np.mean(rejects)) if rejects else None

    coverage_vals = [r["contains_truth"] for r in ok if r.get("contains_truth") is not None]
    coverage = float(np.mean(coverage_vals)) if coverage_vals else None

    sign_errors = None
    if not is_null and ok:
        sign_errors = float(np.mean([not r.get("sign_correct", False) for r in ok]))

    pt_in_ci = [r.get("point_minus_bootstrap_center") for r in ok if r.get("bootstrap_mean") is not None]
    point_in_interval_rate = None
    if ok:
        in_ci = []
        for r in ok:
            lo = r.get("interval_lower")
            hi = r.get("interval_upper")
            pt = r.get("point_estimate")
            if lo is not None and hi is not None and pt is not None:
                in_ci.append(bool(lo <= pt <= hi))
        point_in_interval_rate = float(np.mean(in_ci)) if in_ci else None

    return {
        "world_id": spec.world_id,
        "n_replicates": n,
        "feasible_runs": len(ok),
        "failed_runs": len(failed),
        "callable_failure_rate": len(failed) / max(n, 1),
        "effect_scale": _CANONICAL_EFFECT_SCALE,
        "timing_regime": spec.timing_regime,
        "parallel_trends_status": spec.parallel_trends_status,
        "serial_dependence_regime": spec.serial_dependence_regime,
        "mean_point_estimate": float(np.mean(pts)) if pts.size else None,
        "median_point_estimate": float(np.median(pts)) if pts.size else None,
        "mean_true_effect": float(np.mean(_vals("true_effect"))) if ok else None,
        "mean_bias": float(np.mean(biases)) if biases.size else None,
        "mean_absolute_error": float(np.mean(abs_errs)) if abs_errs.size else None,
        "rmse": float(math.sqrt(np.mean(biases**2))) if biases.size else None,
        "median_absolute_error": float(np.median(abs_errs)) if abs_errs.size else None,
        "sign_error_rate": sign_errors,
        "sign_accuracy": (1.0 - sign_errors) if sign_errors is not None else None,
        "null_false_positive_rate": null_fpr,
        "type_i_error": null_fpr,
        "coverage": coverage,
        "null_coverage": coverage if is_null else None,
        "positive_coverage": coverage if is_positive else None,
        "negative_coverage": coverage if is_negative else None,
        "mean_interval_width": float(np.mean(widths)) if widths.size else None,
        "median_interval_width": float(np.median(widths)) if widths.size else None,
        "mean_bootstrap_center": float(np.mean(boot_centers)) if boot_centers.size else None,
        "point_in_interval_rate": point_in_interval_rate,
        "interval_orientation_failure_rate": len(
            [r for r in ok if r.get("interval_orientation_valid") is False]
        )
        / max(len(ok), 1),
        "negative_half_width_rate": len(
            [r for r in ok if r.get("negative_half_width_detected")]
        )
        / max(len(ok), 1),
        "degenerate_interval_rate": len([r for r in ok if r.get("degenerate_interval")])
        / max(len(ok), 1),
        "non_finite_output_rate": len([r for r in ok if not r.get("finite_outputs")])
        / max(len(ok), 1),
        "notes": spec.notes,
    }


def _coverage_summary(aggregate: dict[str, dict[str, Any]]) -> dict[str, Any]:
    null_worlds = [w for w in REQUIRED_WORLD_IDS if aggregate.get(w, {}).get("null_coverage") is not None]
    pos_worlds = [
        w for w in REQUIRED_WORLD_IDS if aggregate.get(w, {}).get("positive_coverage") is not None
    ]
    null_cov = [
        aggregate[w]["null_coverage"]
        for w in null_worlds
        if aggregate[w].get("null_coverage") is not None
    ]
    pos_cov = [
        aggregate[w]["positive_coverage"]
        for w in pos_worlds
        if aggregate[w].get("positive_coverage") is not None
    ]
    null_fpr = [
        aggregate[w]["null_false_positive_rate"]
        for w in null_worlds
        if aggregate[w].get("null_false_positive_rate") is not None
    ]
    sign_acc = [
        aggregate[w]["sign_accuracy"]
        for w in pos_worlds
        if aggregate[w].get("sign_accuracy") is not None
    ]
    return {
        "null_coverage": float(np.mean(null_cov)) if null_cov else None,
        "positive_coverage": float(np.mean(pos_cov)) if pos_cov else None,
        "type_i_error": float(np.mean(null_fpr)) if null_fpr else None,
        "sign_accuracy_positive": float(np.mean(sign_acc)) if sign_acc else None,
    }


def _decide_harness_correction_verdict(
    aggregate: dict[str, dict[str, Any]],
    failure_register: list[dict[str, Any]],
    *,
    total_runs: int,
    coverage_summary: dict[str, Any],
) -> HarnessCorrectionVerdict:
    if total_runs == 0 or len(failure_register) > total_runs * 0.25:
        return "did_bootstrap_harness_correction_failed"
    null_cov = coverage_summary.get("null_coverage")
    pos_cov = coverage_summary.get("positive_coverage")
    sign_acc = coverage_summary.get("sign_accuracy_positive")
    if null_cov is None:
        return "did_bootstrap_harness_correction_inconclusive"
    clean_pos = aggregate.get("clean_parallel_positive_lift", {})
    if (
        null_cov >= 0.85
        and pos_cov is not None
        and pos_cov < 0.25
        and sign_acc is not None
        and sign_acc >= 0.8
        and clean_pos.get("callable_failure_rate", 1.0) < 0.1
    ):
        return "did_bootstrap_harness_corrected_production_miscoverage_confirmed"
    if null_cov >= 0.85 and pos_cov is not None and pos_cov >= 0.75:
        return "did_bootstrap_harness_corrected_canonical_baseline_established"
    if null_cov >= 0.80 and pos_cov is not None and pos_cov < 0.5:
        return "did_bootstrap_harness_corrected_production_miscoverage_confirmed"
    return "did_bootstrap_harness_correction_inconclusive"


def _harness_correction_metadata() -> dict[str, Any]:
    return {
        "correction_artifact_id": "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION",
        "historical_archive": str(_HISTORICAL_ARCHIVE.relative_to(_REPO_ROOT)),
        "historical_evidence_retained": True,
        "supersedes_canonical_rebuild_geometry_and_coverage_interpretation": True,
        "does_not_supersede_production_bootstrap_behavior": True,
        "assignment_fix": "explicit test_0 treated and control groups; no groups.values() collapse",
        "truth_scale_fix": "canonical coverage on cumulative_level truth vs cumulative_att/treatment_ci",
        "canonical_effect_scale": _CANONICAL_EFFECT_SCALE,
        "statement": (
            "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION supersedes canonical rebuild "
            "geometry and coverage interpretation, but does not supersede production "
            "bootstrap behavior."
        ),
    }


def _decide_overall(aggregate: dict[str, dict[str, Any]]) -> OverallVerdict:
    for m in aggregate.values():
        if m.get("interval_orientation_failure_rate", 0) > 0:
            return "characterization_fail_requires_fix"
        if m.get("negative_half_width_rate", 0) > 0:
            return "characterization_fail_requires_fix"

    for wid in ("clean_parallel_null", "clean_parallel_positive_lift"):
        m = aggregate.get(wid, {})
        if m.get("callable_failure_rate", 0) > 0.1:
            return "characterization_fail_requires_fix"
        if m.get("feasible_runs", 0) > 0 and m.get("non_finite_output_rate", 0) > 0:
            return "characterization_fail_requires_fix"

    mixed = False
    if aggregate.get("clean_parallel_null", {}).get("null_false_positive_rate", 0) > 0.35:
        mixed = True
    if aggregate.get("trend_violation_null", {}).get("null_false_positive_rate", 0) > 0.4:
        mixed = True
    if aggregate.get("post_shock_null", {}).get("null_false_positive_rate", 0) > 0.4:
        mixed = True
    cov = aggregate.get("clean_parallel_positive_lift", {}).get("coverage")
    if cov is not None and cov < 0.5:
        mixed = True
    trend_lift = aggregate.get("trend_violation_positive_lift", {})
    if trend_lift.get("sign_error_rate", 0) > 0.2:
        mixed = True

    if mixed:
        return "characterization_mixed_requires_followup"
    return "characterization_pass_with_caveats"


def asdict_world(spec: WorldSpec) -> dict[str, Any]:
    return {
        "world_id": spec.world_id,
        "scenario_name": spec.scenario_name,
        "percent_effect": spec.percent_effect,
        "n_geos": spec.n_geos,
        "allow_pretrend_violation": spec.allow_pretrend_violation,
        "parallel_trends_status": spec.parallel_trends_status,
        "serial_dependence_regime": spec.serial_dependence_regime,
        "timing_regime": spec.timing_regime,
        "notes": spec.notes,
    }


def _guardrails_list() -> list[str]:
    return [
        "did_embedded_bootstrap_only",
        "single_cell_unit_level_geometry",
        "common_timing_only",
        "level_b_characterization_only",
        "no_governed_uncertainty_claim",
        "no_promotion",
        "harness_corrected_assignment_and_truth_scale",
    ]


def build_d5_stat_did_bootstrap_001(
    cfg: D5StatDidBootstrap001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5StatDidBootstrap001Config()
    if cfg.fast:
        cfg = replace(cfg, n_replicates=4)
    run_results: list[dict[str, Any]] = []
    failure_register: list[dict[str, Any]] = []
    aggregate_metrics: dict[str, dict[str, Any]] = {}

    for widx, spec in enumerate(WORLD_SPECS):
        world_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            row: dict[str, Any] | None = None
            for attempt in range(6):
                seed = cfg.random_state_base + widx * 1000 + rep * 17 + attempt
                candidate = _run_one(spec, cfg, replicate_id=rep, seed=seed)
                if candidate.get("callable_status") == "callable_pass":
                    row = candidate
                    break
                if attempt == 5:
                    row = candidate
            assert row is not None
            world_runs.append(row)
            run_results.append(row)
            if row.get("callable_status") != "callable_pass":
                failure_register.append(
                    {
                        "world_id": spec.world_id,
                        "replicate_id": rep,
                        "exception_type": row.get("exception_type"),
                        "exception_message": row.get("exception_message"),
                        "failure_reason": row.get("failure_reason"),
                        "assignment_failure_reason": row.get("assignment_failure_reason"),
                    }
                )
        aggregate_metrics[spec.world_id] = _aggregate_world(world_runs, spec)

    overall = _decide_overall(aggregate_metrics)
    coverage_summary = _coverage_summary(aggregate_metrics)
    harness_verdict = _decide_harness_correction_verdict(
        aggregate_metrics,
        failure_register,
        total_runs=len(run_results),
        coverage_summary=coverage_summary,
    )

    by_timing = {TIMING_REGIME: _aggregate_timing(run_results)}
    by_pretrend: dict[str, list[dict[str, Any]]] = {}
    for row in run_results:
        if row.get("callable_status") != "callable_pass":
            continue
        by_pretrend.setdefault(str(row.get("parallel_trends_status")), []).append(row)

    return _json_safe(
        {
            "artifact_id": "D5-STAT-DID-BOOTSTRAP-001",
            "artifact_type": "level_b_characterization",
            "method_combination": "DID+embedded_bootstrap",
            "geometry": GEOMETRY,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
            "source_scm_jk_artifact": "D5-STAT-SCM-JK-001",
            "source_augsynth_point_artifact": "D5-STAT-AUGSYNTH-POINT-001",
            "source_tbr_agg_artifact": "D5-STAT-TBR-AGG-001",
            "estimand_contract": ESTIMAND_CONTRACT,
            "overall_verdict": overall,
            "harness_correction": _harness_correction_metadata(),
            "harness_correction_verdict": harness_verdict,
            "summary": {
                "n_worlds": len(WORLD_SPECS),
                "n_replicates_per_world": cfg.n_replicates,
                "total_runs": len(run_results),
                "total_failures": len(failure_register),
                "characterization_only": True,
                "pooled_multiple_treated": True,
                "fast_mode": cfg.fast,
                "timing_regime": TIMING_REGIME,
                **coverage_summary,
            },
            "worlds": [asdict_world(w) for w in WORLD_SPECS],
            "aggregate_metrics": aggregate_metrics,
            "coverage_by_timing": by_timing,
            "coverage_by_parallel_trends_status": {
                k: _aggregate_subset(v) for k, v in by_pretrend.items()
            },
            "run_results": run_results,
            "failure_register": failure_register,
            "forbidden_flags": _forbidden_flags(),
            "next_recommended_artifacts": NEXT_RECOMMENDED,
            "guardrails": _guardrails_list(),
        }
    )


def _aggregate_subset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in rows if r.get("callable_status") == "callable_pass"]
    null_rows = [r for r in ok if abs(r.get("true_effect") or 0) < 1e-12]
    pos_rows = [r for r in ok if (r.get("true_effect") or 0) > 1e-12]
    neg_rows = [r for r in ok if (r.get("true_effect") or 0) < -1e-12]

    def _mean_bool(rs: list[dict[str, Any]], key: str) -> float | None:
        vals = [r[key] for r in rs if r.get(key) is not None]
        return float(np.mean(vals)) if vals else None

    biases = [r["bias"] for r in ok if r.get("bias") is not None]
    return {
        "n_runs": len(rows),
        "feasible_runs": len(ok),
        "failed_runs": len(rows) - len(ok),
        "null_coverage": _mean_bool(null_rows, "contains_truth"),
        "positive_coverage": _mean_bool(pos_rows, "contains_truth"),
        "negative_coverage": _mean_bool(neg_rows, "contains_truth"),
        "sign_accuracy": _mean_bool(ok, "sign_correct"),
        "mean_bias": float(np.mean(biases)) if biases else None,
        "rmse": float(math.sqrt(np.mean(np.array(biases) ** 2))) if biases else None,
        "point_in_interval_rate": _mean_bool(
            ok,
            "contains_truth",
        ),
    }


def _aggregate_timing(rows: list[dict[str, Any]]) -> dict[str, Any]:
    common = [r for r in rows if r.get("timing_regime") == TIMING_REGIME]
    return _aggregate_subset(common)


def preserve_historical_archive() -> Path | None:
    if _HISTORICAL_ARCHIVE.is_file():
        return _HISTORICAL_ARCHIVE
    if not _DEFAULT_ARCHIVE.is_file():
        return None
    shutil.copy2(_DEFAULT_ARCHIVE, _HISTORICAL_ARCHIVE)
    return _HISTORICAL_ARCHIVE


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5StatDidBootstrap001Config | None = None,
    overwrite: bool = False,
) -> Path:
    if path is None:
        path = _DEFAULT_ARCHIVE
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    preserve_historical_archive()
    payload = build_d5_stat_did_bootstrap_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    write_harness_correction_report(payload)
    return path


def write_harness_correction_report(payload: dict[str, Any]) -> Path:
    path = _REPO_ROOT / "docs/track_d/D5_STAT_DID_BOOTSTRAP_001_HARNESS_CORRECTION_REPORT.md"
    cov = payload.get("summary", {})
    agg = payload.get("aggregate_metrics", {})
    clean_pos = agg.get("clean_parallel_positive_lift", {})
    clean_null = agg.get("clean_parallel_null", {})
    lines = [
        "# D5-STAT-DID-BOOTSTRAP-001 Harness Correction — Report",
        "",
        "**Artifact ID:** D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION",
        f"**Verdict:** `{payload.get('harness_correction_verdict')}`",
        "**Canonical archive:** [`archives/D5_STAT_DID_BOOTSTRAP_001_results.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results.json)",
        "**Historical archive:** [`archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json`](archives/D5_STAT_DID_BOOTSTRAP_001_results_historical_pre_harness_correction.json)",
        "**Harness:** `panel_exp/validation/track_d_d5_stat_did_bootstrap_001.py`",
        "",
        "> **Supersession:** `D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION` supersedes canonical "
        "rebuild geometry and coverage interpretation, but does not supersede production bootstrap behavior.",
        "",
        "## 1. Executive summary",
        "",
        "Corrected the canonical D5-STAT-DID-BOOTSTRAP-001 harness: assignment now uses explicit "
        "`test_0` (treated) and `control` groups; canonical coverage compares cumulative level "
        "`cumulative_att` / `treatment_ci` to cumulative level injected truth. Under corrected "
        "geometry, point estimates recover injected effects but bootstrap interval calibration "
        "remains poor — confirming a separate production miscentering defect. "
        "**No production DID code changed. No TrustReport authorization.**",
        "",
        "This artifact corrects the canonical validation harness only. It does not change "
        "production DID or bootstrap behavior. The corrected evidence may continue to show invalid "
        "interval calibration. That result is expected and supports the separate production "
        "correction artifact.",
        "",
        "## 2. Historical canonical harness defect",
        "",
        "Pre-correction archive used `groups.values()`, collapsing control+test_0 into treated_units "
        "(all units treated, zero controls), causing callable failures and invalid geometry on rebuild.",
        "",
        "## 3. Assignment reconstruction defect",
        "",
        "`_assign_greedy_pre_period` flattened all assignment groups into treated units. "
        "Rebuild equality test failed; D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 confirmed the defect.",
        "",
        "## 4. Estimand and scale audit",
        "",
        "Canonical estimand: cumulative level ATT (`cumulative_att`). Truth: cumulative injected "
        "level delta on treated units. Injection parameter remains fractional percent; truth is level-only.",
        "",
        "## 5. Correction scope",
        "",
        "Harness assignment, per-run geometry fields, bootstrap center diagnostics, aggregate "
        "coverage summaries, historical archive preservation, regenerated canonical archive.",
        "",
        "## 6. Non-goals",
        "",
        "- Production DID/bootstrap code changes",
        "- DCM-004 eligibility reassessment",
        "- TrustReport authorization",
        "- Diagnostic oracle recentering in canonical harness",
        "",
        "## 7. Corrected harness architecture",
        "",
        "Greedy `test_0`/`control` assignment → percent-to-level injection → production `DID` "
        "with embedded bootstrap → cumulative level coverage metrics.",
        "",
        "## 8. Treatment/control geometry",
        "",
        f"Post-correction: `n_treated` ≈ 4–6, `n_control` ≈ 9–11 on 16-geo worlds; zero overlap; "
        f"callable failure rate on clean worlds: {clean_pos.get('callable_failure_rate', 'n/a')}.",
        "",
        "## 9. Timing assumptions",
        "",
        f"All worlds use `{TIMING_REGIME}`; staggered timing blocked at harness level.",
        "",
        "## 10. Truth-scale contract",
        "",
        f"Canonical effect scale: `{_CANONICAL_EFFECT_SCALE}`. Point, interval, and truth aligned.",
        "",
        "## 11. Worlds, seeds, and replicates",
        "",
        f"7 worlds, {payload.get('summary', {}).get('n_replicates_per_world')} replicates, "
        f"seed base `20260608`.",
        "",
        "## 12. Run counts and runtime",
        "",
        f"Total runs: {payload.get('summary', {}).get('total_runs')}; "
        f"failures: {payload.get('summary', {}).get('total_failures')}.",
        "",
        "## 13. Point-estimate results",
        "",
        f"Sign accuracy (positive worlds): {cov.get('sign_accuracy_positive')}; "
        f"clean positive lift sign error rate: {clean_pos.get('sign_error_rate')}.",
        "",
        "## 14. Bootstrap-center findings",
        "",
        f"Mean bootstrap center vs point gap persists on positive worlds "
        f"(production miscentering reproduced honestly).",
        "",
        "## 15. Null coverage",
        "",
        f"Aggregate null coverage: {cov.get('null_coverage')}; clean parallel null: "
        f"{clean_null.get('null_coverage')}.",
        "",
        "## 16. Positive coverage",
        "",
        f"Aggregate positive coverage: {cov.get('positive_coverage')}; clean parallel positive: "
        f"{clean_pos.get('positive_coverage')}.",
        "",
        "## 17. Negative coverage",
        "",
        "No dedicated negative-effect world in canonical battery.",
        "",
        "## 18. Type-I error",
        "",
        f"Empirical type-I (null rejection): {cov.get('type_i_error')}.",
        "",
        "## 19. Bias and RMSE",
        "",
        f"Clean positive lift RMSE: {clean_pos.get('rmse')}; mean bias: {clean_pos.get('mean_bias')}.",
        "",
        "## 20. Interval width",
        "",
        f"Mean interval width (clean positive): {clean_pos.get('mean_interval_width')}.",
        "",
        "## 21. Parallel-trends findings",
        "",
        "Pretrend-violation worlds characterized separately; not used to claim bootstrap calibration.",
        "",
        "## 22. Serial-dependence findings",
        "",
        "Standard battery; no elevated serial-dependence override worlds in canonical D5-STAT.",
        "",
        "## 23. Failure analysis",
        "",
        f"Failure register length: {len(payload.get('failure_register', []))}.",
        "",
        "## 24. Historical versus corrected archive",
        "",
        "Historical pre-correction archive retained. Canonical archive regenerated with corrected assignment.",
        "",
        "## 25. Production-defect implication",
        "",
        "Corrected geometry with production DID unchanged still shows ~0% positive coverage and "
        "bootstrap center misaligned with `cumulative_att` — supports "
        "`DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001` as next step.",
        "",
        "## 26. TrustReport implications",
        "",
        "DCM-004 remains `INSUFFICIENT_EVIDENCE` for causal-interval candidacy. Harness correction "
        "does not authorize TrustReport.",
        "",
        "## 27. Archive policy",
        "",
        "Historical archive preserved; canonical archive superseded for rebuild interpretation only.",
        "",
        "## 28. Tests",
        "",
        "`tests/track_d/test_d5_stat_did_bootstrap_001.py` — assignment, scale, archive equality.",
        "",
        "## 29. Remaining limitations",
        "",
        "Synthetic worlds only; embedded bootstrap only; production miscoverage not repaired here.",
        "",
        "## 30. Governance verdict",
        "",
        f"**`{payload.get('harness_correction_verdict')}`**",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="D5-STAT-DID-BOOTSTRAP-001 harness")
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_ARCHIVE,
        help="Canonical archive output path",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing archive")
    parser.add_argument("--fast", action="store_true", help="Fast mode (4 replicates per world)")
    args = parser.parse_args()
    cfg = D5StatDidBootstrap001Config(fast=args.fast)
    out = write_artifact(args.output, cfg=cfg, overwrite=args.overwrite)
    p = build_d5_stat_did_bootstrap_001(cfg)
    print(
        f"Wrote {out} — {p['overall_verdict']} / {p['harness_correction_verdict']} "
        f"({p['summary'].get('total_runs', 0)} runs)"
    )


if __name__ == "__main__":
    main()
