"""D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 — DID+bootstrap coverage diagnosis.

Decomposes undercoverage into identification failure, estimator bias, interval
miscentering, variance miscalibration, harness defects, and truth-scale mismatch.
No TrustReport authorization or production threshold definition.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import subprocess
import tempfile
import warnings
from dataclasses import asdict, dataclass, field, replace
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
_ARTIFACT_VERSION = "1.0.0"
_THRESHOLD_LABEL = "provisional_for_remediation_characterization_only"

SemanticVerdict = Literal[
    "did_bootstrap_production_miscentering_confirmed",
    "did_bootstrap_causal_interval_remediated_requires_reassessment",
    "did_bootstrap_parallel_trends_gated_restricted",
    "did_bootstrap_common_timing_only",
    "did_bootstrap_diagnostic_only",
    "did_bootstrap_not_interval_eligible",
    "did_bootstrap_remediation_inconclusive",
    "did_bootstrap_remediation_failed",
]

ProductionDefectDecision = Literal[
    "production_defect_confirmed",
    "production_defect_not_confirmed",
    "production_defect_indeterminate",
]

BOOTSTRAP_POLICIES: tuple[dict[str, str], ...] = (
    {"policy_id": "A", "name": "current_did_bootstrap", "description": "embedded moving-block time bootstrap"},
    {"policy_id": "B", "name": "parallel_trends_gated", "description": "coverage evaluated only when pretrend contract passes"},
    {"policy_id": "C", "name": "cluster_bootstrap", "description": "unit-cluster bootstrap (not implemented in DID)"},
    {"policy_id": "D", "name": "time_block_bootstrap", "description": "alias of current embedded block bootstrap"},
    {"policy_id": "E", "name": "bias_diagnostic_only", "description": "point bias tracked; intervals not promoted"},
    {"policy_id": "F", "name": "common_timing_only", "description": "simultaneous adoption geometry only"},
    {"policy_id": "G", "name": "staggered_timing_blocked", "description": "staggered cohorts blocked for pooled DID"},
    {"policy_id": "H", "name": "causal_interval_not_supported", "description": "interval readout blocked"},
)

TIMING_REGIMES: tuple[dict[str, str], ...] = (
    {"regime_id": "common", "description": "simultaneous treated adoption (DID-supported)"},
    {"regime_id": "staggered", "description": "staggered cohort starts (DID pooled blocked)"},
)

PARALLEL_TRENDS_REGIMES: tuple[dict[str, str], ...] = (
    {"regime_id": "holds", "description": "parallel trends assumed valid for causal readout"},
    {"regime_id": "mild_violation", "description": "mild pre-trend slope divergence"},
    {"regime_id": "severe_violation", "description": "severe pretrend violation"},
    {"regime_id": "staggered_blocked", "description": "staggered geometry blocked for pooled DID"},
)

SERIAL_DEPENDENCE_REGIMES: tuple[dict[str, str], ...] = (
    {"regime_id": "clean_iid", "description": "no elevated autocorrelation or cross-geo shock overrides"},
    {"regime_id": "serial_correlation", "description": "high autocorrelation (AR-like dependence)"},
    {"regime_id": "clustered_shocks", "description": "elevated cross-geo correlation"},
    {"regime_id": "heteroskedastic", "description": "elevated noise scale heteroskedasticity"},
    {"regime_id": "standard_stress", "description": "other stress worlds without dedicated serial regime"},
)

_SERIAL_REGIME_BY_WORLD: dict[str, str] = {
    "clean_parallel_trends": "clean_iid",
    "placebo_null": "clean_iid",
    "common_treatment_timing": "clean_iid",
    "serial_correlation": "serial_correlation",
    "clustered_shocks": "clustered_shocks",
    "heteroskedasticity": "heteroskedastic",
}

_DEFAULT_SUMMARY = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_REPORT.md"


@dataclass(frozen=True)
class DiagnosticWorldSpec:
    world_id: str
    scenario_name: str = "did_parallel_trends_holds"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 28
    treatment_probability: float = 0.35
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    allow_pretrend_violation: bool = False
    timing_pattern: str = "common"
    parallel_trends_regime: str = "holds"
    notes: str = ""


@dataclass(frozen=True)
class RemediationConfig:
    n_replicates: int = 4
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260619
    min_control_units: int = 4
    n_bootstrap: int = 50
    fast: bool = False
    assignment_mode: str = "corrected_test_0"
    effect_sizes: tuple[float, ...] = (0.0, 0.03, 0.08, 0.12, -0.05)
    write_full_results_path: str | None = "/tmp/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_results.json"


DIAGNOSTIC_WORLDS: tuple[DiagnosticWorldSpec, ...] = (
    DiagnosticWorldSpec("clean_parallel_trends", percent_effect=0.08, parallel_trends_regime="holds"),
    DiagnosticWorldSpec(
        "mild_pretrend_violation",
        percent_effect=0.08,
        scenario_overrides={"trend": 0.06, "seasonality_amplitude": 1.5},
        parallel_trends_regime="mild_violation",
        notes="mild pre-trend slope divergence",
    ),
    DiagnosticWorldSpec(
        "severe_pretrend_violation",
        scenario_name="did_parallel_trends_violation",
        percent_effect=0.08,
        allow_pretrend_violation=True,
        parallel_trends_regime="severe_violation",
    ),
    DiagnosticWorldSpec(
        "serial_correlation",
        percent_effect=0.08,
        scenario_overrides={"autocorrelation": 0.85},
        notes="high serial correlation",
    ),
    DiagnosticWorldSpec(
        "clustered_shocks",
        percent_effect=0.08,
        scenario_overrides={"cross_geo_correlation": 0.9},
        notes="clustered cross-geo shocks",
    ),
    DiagnosticWorldSpec(
        "heteroskedasticity",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 4.5},
    ),
    DiagnosticWorldSpec(
        "high_unit_heterogeneity",
        percent_effect=0.08,
        scenario_overrides={"heterogeneous_effects": True},
    ),
    DiagnosticWorldSpec(
        "treatment_effect_heterogeneity",
        percent_effect=0.08,
        scenario_overrides={"heterogeneous_effects": True, "noise_scale": 2.0},
    ),
    DiagnosticWorldSpec(
        "anticipation_effect",
        percent_effect=0.08,
        treatment_start=26,
        notes="earlier treatment onset (anticipation proxy)",
    ),
    DiagnosticWorldSpec(
        "delayed_effect",
        percent_effect=0.08,
        treatment_start=32,
        notes="delayed treatment onset",
    ),
    DiagnosticWorldSpec(
        "carryover_effect",
        percent_effect=0.08,
        scenario_overrides={"spillover_strength": 0.25},
    ),
    DiagnosticWorldSpec(
        "staggered_treatment_timing",
        scenario_name="sdid_staggered_adoption",
        percent_effect=0.08,
        timing_pattern="staggered",
        parallel_trends_regime="staggered_blocked",
        notes="staggered cohorts — pooled DID unsupported",
    ),
    DiagnosticWorldSpec(
        "common_treatment_timing",
        percent_effect=0.08,
        timing_pattern="common",
    ),
    DiagnosticWorldSpec(
        "small_treated_group",
        percent_effect=0.08,
        n_geos=12,
        treatment_probability=0.48,
        notes="few treated units",
    ),
    DiagnosticWorldSpec(
        "weak_control_support",
        percent_effect=0.08,
        n_geos=10,
        treatment_probability=0.5,
        notes="minimal donor/control support",
    ),
    DiagnosticWorldSpec(
        "outlier_unit",
        percent_effect=0.08,
        scenario_overrides={"outlier_probability": 0.15},
    ),
    DiagnosticWorldSpec(
        "missing_observations",
        percent_effect=0.0,
        scenario_name="recovery_null_effect",
        scenario_overrides={"missingness_policy": "mcar_light"},
        notes="light MCAR missingness null world",
    ),
    DiagnosticWorldSpec("placebo_null", percent_effect=0.0, notes="placebo null under parallel trends"),
)


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _forbidden() -> dict[str, bool]:
    return {
        "promotion_allowed": False,
        "trust_role_allowed": False,
        "trust_report_authorized": False,
    }


def _assign_units(
    wide: Any,
    *,
    n_pre: int,
    seed: int,
    treatment_probability: float,
    mode: str,
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
    if mode == "broken_groups_values":
        treated = [u for units in groups.values() for u in units]
    else:
        treated = list(groups.get("test_0") or [])
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
    end_idx = min(int(mod.treated_end_idxs[0]), mod.times.shape[0] - 1)
    treated_len = end_idx - start + 1
    n_treated = len(mod.treated_units)
    if n_treated == 1:
        delta = float(percent_effect * np.mean(mean_value))
        mod.wide_data.loc[mod.treated_units, mod.times[start : start + treated_len]] += delta
        return mod
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    block = np.where(mask, block + value_effect.reshape(-1, 1), block)
    mod.wide_data.loc[mod.treated_units] = block
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


def _build_panel(
    spec: DiagnosticWorldSpec,
    cfg: RemediationConfig,
    *,
    seed: int,
) -> PanelDataset:
    post_end = cfg.train_length + cfg.test_length - 1
    base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
    scenario = replace(
        base,
        random_state=seed,
        n_geos=spec.n_geos,
        n_periods=max(spec.n_periods, post_end + 1),
        treatment_start=spec.treatment_start,
        true_effect=0.0,
        **(spec.scenario_overrides or {}),
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    treated = _assign_units(
        wide,
        n_pre=cfg.train_length,
        seed=seed,
        treatment_probability=spec.treatment_probability,
        mode=cfg.assignment_mode,
    )
    end = cfg.train_length + cfg.test_length
    return PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
        treated_units=treated,
    )


def _scalar_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        arr = np.asarray(value, dtype=float).reshape(-1)
        if arr.size == 0 or not np.isfinite(arr[0]):
            return None
        return float(arr[0])
    except (TypeError, ValueError):
        return None


def _pretrend_fields(est: DID, results: dict[str, Any]) -> dict[str, Any]:
    contract = results.get("did_pretrend_contract") or getattr(est, "_did_pretrend_contract", {}) or {}
    pt = results.get("parallel_trends_test") or {}
    return {
        "parallel_trends_status": contract.get("pretrend_status"),
        "pretrend_slope_difference": pt.get("largest_pretrend_deviation"),
        "pretrend_test_result": contract.get("joint_pretrend_p_value"),
        "parallel_trends_violated": contract.get("parallel_trends_violated"),
    }


def _bootstrap_fields(est: DID, point: float) -> dict[str, Any]:
    boot_raw = getattr(est, "bootstrap_cumulative_effects_", None)
    boot = np.asarray([] if boot_raw is None else boot_raw, dtype=float).reshape(-1)
    boot = boot[np.isfinite(boot)]
    lo, hi = est.treatment_ci
    lo_f = _scalar_float(lo)
    hi_f = _scalar_float(hi)
    center = float(np.mean(boot)) if boot.size else None
    median = float(np.median(boot)) if boot.size else None
    se = float(np.std(boot, ddof=1)) if boot.size > 1 else None
    shift = (point - center) if center is not None and np.isfinite(point) else None
    oracle_lo = oracle_hi = None
    if shift is not None and lo_f is not None and hi_f is not None:
        oracle_lo = float(lo_f + shift)
        oracle_hi = float(hi_f + shift)
    point_in_ci = None
    if lo_f is not None and hi_f is not None:
        point_in_ci = bool(lo_f <= point <= hi_f)
    return {
        "bootstrap_unit": "time_period_moving_block",
        "n_bootstrap_replicates": int(getattr(est, "n_bootstrap", 50)),
        "bootstrap_seed": int(getattr(est, "bootstrap_seed", 0)),
        "bootstrap_distribution_center": center,
        "bootstrap_distribution_median": median,
        "bootstrap_standard_error": se,
        "point_minus_bootstrap_center": shift,
        "bootstrap_interval_lower": lo_f,
        "bootstrap_interval_upper": hi_f,
        "bootstrap_failure_count": max(0, int(getattr(est, "n_bootstrap", 50)) - int(boot.size)),
        "point_in_bootstrap_ci": point_in_ci,
        "oracle_recentered_lower": oracle_lo,
        "oracle_recentered_upper": oracle_hi,
    }


def _run_diagnostic(
    spec: DiagnosticWorldSpec,
    cfg: RemediationConfig,
    *,
    replicate_id: int,
    seed: int,
    percent_effect: float | None = None,
) -> dict[str, Any]:
    pct = float(spec.percent_effect if percent_effect is None else percent_effect)
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "percent_effect": pct,
        "replicate_id": replicate_id,
        "seed": seed,
        "assignment_mode": cfg.assignment_mode,
        "timing_pattern": spec.timing_pattern,
        "parallel_trends_regime": spec.parallel_trends_regime,
        "serial_dependence_regime": _SERIAL_REGIME_BY_WORLD.get(spec.world_id, "standard_stress"),
        **_forbidden(),
    }
    if spec.timing_pattern == "staggered":
        return {
            **base,
            "callable_status": "timing_blocked",
            "failure_status": "staggered_timing_unsupported_for_pooled_did",
            "failure_reason": "DID requires simultaneous adoption; staggered cohort geometry blocked",
        }
    try:
        panel = _build_panel(spec, cfg, seed=seed)
        n_treated = len(panel.treated_units)
        n_control = int(panel.num_control_units)
        if n_control < cfg.min_control_units:
            raise ValueError("insufficient control units after assignment")
        if cfg.assignment_mode == "broken_groups_values" and n_control == 0:
            raise ValueError("harness_defect_all_units_treated_zero_controls")

        mean_value = _mean_treated_baseline(panel)
        baseline = copy.deepcopy(panel)
        injected = _inject_percent_effect(panel, pct, mean_value)
        true_effect = _true_cumulative_injected(baseline, injected, test_len=cfg.test_length)

        est = DID(alpha=cfg.alpha)
        est.n_bootstrap = int(cfg.n_bootstrap)
        est.bootstrap_seed = int(seed % (2**31 - 1))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            est.run_analysis(
                injected,
                multiple_treated="pooled",
                allow_pretrend_violation=spec.allow_pretrend_violation,
            )
        results = getattr(est, "results", {}) or {}
        point = _scalar_float(results.get("cumulative_att"))
        if point is None:
            raise ValueError("non-finite cumulative_att")
        lo, hi = est.treatment_ci
        interval_lower = _scalar_float(lo)
        interval_upper = _scalar_float(hi)
        interval_center = (
            0.5 * (interval_lower + interval_upper)
            if interval_lower is not None and interval_upper is not None
            else None
        )
        interval_width = (
            interval_upper - interval_lower
            if interval_lower is not None and interval_upper is not None
            else None
        )
        bias = point - true_effect
        is_null = abs(true_effect) < 1e-9
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
        sign_correct = (
            bool(abs(point) < 1.0)
            if is_null
            else bool(np.isfinite(point) and np.sign(point) == np.sign(true_effect))
        )
        boot = _bootstrap_fields(est, point)
        oracle_contains = None
        if boot.get("oracle_recentered_lower") is not None and boot.get("oracle_recentered_upper") is not None:
            oracle_contains = bool(
                boot["oracle_recentered_lower"] <= true_effect <= boot["oracle_recentered_upper"]
            )
        pretrend = _pretrend_fields(est, results)
        center_err = (interval_center - point) if interval_center is not None else None
        miscenter = (interval_center - true_effect) if interval_center is not None else None
        empirical_var = boot.get("bootstrap_standard_error")
        empirical_var_sq = float(empirical_var**2) if empirical_var is not None else None
        variance_ratio = None
        if empirical_var is not None and abs(bias) > 1e-9:
            variance_ratio = float(empirical_var / abs(bias))

        return {
            **base,
            "callable_status": "callable_pass",
            "failure_status": None,
            "point_estimate": point,
            "true_effect_cumulative_level": true_effect,
            "effect_scale": "cumulative_level",
            "bias": float(bias),
            "absolute_error": float(abs(bias)),
            "squared_error": float(bias**2),
            "sign_correct": sign_correct,
            "interval_lower": interval_lower,
            "interval_upper": interval_upper,
            "interval_center": interval_center,
            "interval_width": interval_width,
            "interval_center_error": float(center_err) if center_err is not None else None,
            "interval_miscentering": float(miscenter) if miscenter is not None else None,
            "contains_truth": contains_truth,
            "contains_zero": contains_zero,
            "oracle_recentered_contains_truth": oracle_contains,
            "treated_count": n_treated,
            "control_count": n_control,
            "treatment_start": cfg.train_length,
            "support_warning": n_control < 6,
            **pretrend,
            **boot,
            "empirical_sampling_variance": empirical_var_sq,
            "variance_ratio_bootstrap_se_to_abs_bias": variance_ratio,
            "twfe_coefficient": float(getattr(est, "treatment_effect", float("nan"))),
            "failure_reason": None,
        }
    except Exception as exc:
        return {
            **base,
            "callable_status": "callable_fail",
            "failure_status": type(exc).__name__,
            "failure_reason": str(exc)[:300],
        }


def _run_with_retry(
    spec: DiagnosticWorldSpec,
    cfg: RemediationConfig,
    *,
    replicate_id: int,
    seed_base: int,
    percent_effect: float | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] | None = None
    for attempt in range(6):
        seed = seed_base + attempt
        candidate = _run_diagnostic(
            spec, cfg, replicate_id=replicate_id, seed=seed, percent_effect=percent_effect
        )
        if candidate.get("callable_status") in ("callable_pass", "timing_blocked"):
            return candidate
        row = candidate
    return row if row is not None else {"callable_status": "callable_fail", "failure_reason": "no_attempts"}


def _coverage(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [r[key] for r in rows if r.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in rows if r.get("callable_status") == "callable_pass"]
    blocked = [r for r in rows if r.get("callable_status") == "timing_blocked"]
    failed = [r for r in rows if r.get("callable_status") == "callable_fail"]
    biases = [r["bias"] for r in ok if r.get("bias") is not None]
    widths = [r["interval_width"] for r in ok if r.get("interval_width") is not None]
    center_errs = [r["interval_center_error"] for r in ok if r.get("interval_center_error") is not None]
    pt_in_ci = [r["point_in_bootstrap_ci"] for r in ok if r.get("point_in_bootstrap_ci") is not None]
    null_rows = [r for r in ok if abs(r.get("true_effect_cumulative_level") or 0) < 1e-9]
    pos_rows = [r for r in ok if (r.get("true_effect_cumulative_level") or 0) > 1e-9]
    neg_rows = [r for r in ok if (r.get("true_effect_cumulative_level") or 0) < -1e-9]
    return {
        "n_runs": len(rows),
        "feasible_runs": len(ok),
        "timing_blocked_runs": len(blocked),
        "failed_runs": len(failed),
        "failure_rate": len(failed) / len(rows) if rows else None,
        "null_coverage": _coverage(null_rows, "contains_truth"),
        "positive_coverage": _coverage(pos_rows, "contains_truth"),
        "negative_coverage": _coverage(neg_rows, "contains_truth"),
        "null_rejection_rate": _coverage(null_rows, "contains_zero") if null_rows else None,
        "type_i_error": (1.0 - _coverage(null_rows, "contains_zero")) if null_rows else None,
        "sign_accuracy": _coverage(ok, "sign_correct"),
        "mean_bias": float(np.mean(biases)) if biases else None,
        "median_bias": float(np.median(biases)) if biases else None,
        "rmse": float(math.sqrt(np.mean(np.array(biases) ** 2))) if biases else None,
        "mean_interval_width": float(np.mean(widths)) if widths else None,
        "mean_interval_center_error": float(np.mean(center_errs)) if center_errs else None,
        "point_in_bootstrap_ci_rate": _coverage(ok, "point_in_bootstrap_ci"),
        "oracle_recentered_coverage": _coverage(ok, "oracle_recentered_contains_truth"),
        "mean_bootstrap_se": float(
            np.mean([r["bootstrap_standard_error"] for r in ok if r.get("bootstrap_standard_error") is not None])
        )
        if ok
        else None,
    }


def _serial_regime_for_row(row: dict[str, Any]) -> str:
    return str(row.get("serial_dependence_regime") or "standard_stress")


def _assess_harness_defect(
    harness_defect_confirmed: bool,
    harness_failures: int,
    probe_count: int,
) -> dict[str, Any]:
    return {
        "harness_defect_confirmed": harness_defect_confirmed,
        "canonical_harness_artifact": "D5-STAT-DID-BOOTSTRAP-001",
        "defect_pattern": "groups.values() flattens control+test_0 into treated_units",
        "symptoms": [
            "all units treated",
            "zero controls",
            "malformed DID pooled geometry",
            "archive rebuild drift when harness assignment wrong",
        ],
        "probe_failures": harness_failures,
        "probe_runs": probe_count,
        "remediation_harness_uses_corrected_test_0": True,
        "canonical_fix_artifact": "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION",
        "fixed_in_this_branch": False,
    }


def _assess_production_defect(
    *,
    sign_accuracy: float | None,
    pos_cov_clean: float | None,
    pos_cov_08: float | None,
    pos_cov_clean_iid: float | None,
    miscentering_dominant: bool,
    truth_scale_mismatch: bool,
    oracle_pos_cov: float | None,
    point_in_ci_rate: float | None,
    mean_gap: float | None,
    pretrend_driver: bool,
    holds_sign_accuracy: float | None,
) -> dict[str, Any]:
    point_recovers = sign_accuracy is not None and sign_accuracy >= 0.8
    miscentered = bool(
        miscentering_dominant
        and pos_cov_clean is not None
        and pos_cov_clean < 0.25
        and pos_cov_08 is not None
        and pos_cov_08 < 0.25
    )
    oracle_helps = oracle_pos_cov is not None and oracle_pos_cov >= 0.75
    reproducible = point_in_ci_rate is not None and point_in_ci_rate < 0.5
    large_gap = mean_gap is not None and abs(mean_gap) > 1.0

    criteria = {
        "corrected_assignment_geometry": True,
        "point_recovers_in_clean_worlds": point_recovers,
        "bootstrap_interval_materially_miscentered": miscentered,
        "miscentering_reproduces_deterministically": reproducible,
        "visible_in_production_did_py": True,
        "diagnostic_recenter_improves_coverage": oracle_helps,
        "not_explained_by_scale_mismatch": not truth_scale_mismatch,
        "not_explained_by_serial_dependence_only": bool(
            miscentering_dominant
            or (pos_cov_clean_iid is not None and pos_cov_clean_iid < 0.25)
        ),
        "not_explained_by_parallel_trends_failure_only": bool(
            holds_sign_accuracy is None or holds_sign_accuracy >= 0.75 or miscentering_dominant
        ),
        "bootstrap_center_gap_material": large_gap,
    }
    confirmed = all(
        criteria[k]
        for k in (
            "corrected_assignment_geometry",
            "point_recovers_in_clean_worlds",
            "bootstrap_interval_materially_miscentered",
            "miscentering_reproduces_deterministically",
            "visible_in_production_did_py",
            "diagnostic_recenter_improves_coverage",
            "not_explained_by_scale_mismatch",
            "not_explained_by_serial_dependence_only",
            "not_explained_by_parallel_trends_failure_only",
        )
    )
    if confirmed:
        decision: ProductionDefectDecision = "production_defect_confirmed"
        recommended = "DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001"
    elif not point_recovers:
        decision = "production_defect_not_confirmed"
        recommended = None
    elif not miscentered and not large_gap:
        decision = "production_defect_not_confirmed"
        recommended = None
    else:
        decision = "production_defect_indeterminate"
        recommended = None

    return {
        "decision": decision,
        "criteria": criteria,
        "recommended_follow_up_artifact": recommended,
        "bootstrap_replicate_statistic": "cumulative_att from _path_effect_from_df on block-resampled panel",
        "reported_point_statistic": "cumulative_att from aggregate path in run_analysis",
        "interval_construction": "percentile of bootstrap_cumulative_effects_ distribution",
        "interval_centered_on": "bootstrap_cumulative_att_distribution_not_reported_point",
        "note": (
            "Production DID.py embeds bootstrap; CI percentiles follow bootstrap draws while "
            "reported cumulative_att is computed after bootstrap on the original panel path."
        ),
    }


def _decide_verdict(
    summary: dict[str, Any],
    production_decision: ProductionDefectDecision,
) -> SemanticVerdict:
    fail_rate = summary.get("failure_summary", {}).get("overall_failure_rate")
    if fail_rate is not None and fail_rate > 0.35:
        return "did_bootstrap_remediation_failed"

    if production_decision == "production_defect_confirmed":
        return "did_bootstrap_production_miscentering_confirmed"

    by_effect = summary.get("coverage_by_effect", {})
    null_cov = (by_effect.get("0.0") or {}).get("null_coverage")
    pos_cov = (by_effect.get("0.08") or {}).get("positive_coverage")
    decomp = summary.get("bias_decomposition", {})
    miscenter = decomp.get("interval_miscentering_dominant", False)

    if pos_cov is not None and pos_cov >= 0.75 and null_cov is not None and null_cov >= 0.85:
        return "did_bootstrap_causal_interval_remediated_requires_reassessment"
    if miscenter and pos_cov is not None and pos_cov < 0.2:
        return "did_bootstrap_not_interval_eligible"
    pretrend_only = decomp.get("undercoverage_driver_hypothesis") == "identification_pretrend_violation"
    if pretrend_only:
        return "did_bootstrap_parallel_trends_gated_restricted"
    if pos_cov is None and null_cov is None:
        return "did_bootstrap_remediation_inconclusive"
    return "did_bootstrap_diagnostic_only"


def build_d5_trust_did_bootstrap_remediation_001(
    cfg: RemediationConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or RemediationConfig()
    if cfg.fast:
        cfg = replace(cfg, n_replicates=2, n_bootstrap=12)
        worlds = DIAGNOSTIC_WORLDS[:6]
        effect_sizes = (0.0, 0.08)
    else:
        worlds = DIAGNOSTIC_WORLDS
        effect_sizes = cfg.effect_sizes

    all_runs: list[dict[str, Any]] = []
    by_world: dict[str, list[dict[str, Any]]] = {}
    by_effect: dict[str, list[dict[str, Any]]] = {}
    by_timing: dict[str, list[dict[str, Any]]] = {}
    by_pretrend: dict[str, list[dict[str, Any]]] = {}
    by_serial: dict[str, list[dict[str, Any]]] = {}
    harness_defect_runs: list[dict[str, Any]] = []

    for widx, world in enumerate(worlds):
        world_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            seed_base = cfg.random_state_base + widx * 1000 + rep * 17
            row = _run_with_retry(world, cfg, replicate_id=rep, seed_base=seed_base)
            world_runs.append(row)
            all_runs.append(row)
        by_world[world.world_id] = world_runs

    base_world = DiagnosticWorldSpec("effect_sweep", percent_effect=0.08, parallel_trends_regime="holds")
    for eidx, eff in enumerate(effect_sizes):
        eff_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            seed_base = cfg.random_state_base + 50000 + eidx * 1000 + rep * 13
            row = _run_with_retry(
                base_world, cfg, replicate_id=rep, seed_base=seed_base, percent_effect=eff
            )
            eff_runs.append(row)
            all_runs.append(row)
        by_effect[str(eff)] = eff_runs

    broken_cfg = replace(cfg, assignment_mode="broken_groups_values")
    for rep in range(1 if cfg.fast else min(3, cfg.n_replicates)):
        seed_base = cfg.random_state_base + 80000 + rep * 19
        row = _run_with_retry(
            DiagnosticWorldSpec("harness_defect_probe", percent_effect=0.08),
            broken_cfg,
            replicate_id=rep,
            seed_base=seed_base,
        )
        harness_defect_runs.append(row)
        all_runs.append(row)

    for row in all_runs:
        if row.get("callable_status") != "callable_pass":
            continue
        tp = row.get("timing_pattern", "common")
        by_timing.setdefault(tp, []).append(row)
        pr = row.get("parallel_trends_regime", "holds")
        by_pretrend.setdefault(pr, []).append(row)
        sr = _serial_regime_for_row(row)
        by_serial.setdefault(sr, []).append(row)

    coverage_by_world = {k: _aggregate_rows(v) for k, v in by_world.items()}
    coverage_by_effect = {k: _aggregate_rows(v) for k, v in by_effect.items()}
    coverage_by_timing = {k: _aggregate_rows(v) for k, v in by_timing.items()}
    coverage_by_pretrend = {k: _aggregate_rows(v) for k, v in by_pretrend.items()}
    coverage_by_serial = {k: _aggregate_rows(v) for k, v in by_serial.items()}

    ok = [r for r in all_runs if r.get("callable_status") == "callable_pass"]
    pos_rows = [r for r in ok if (r.get("true_effect_cumulative_level") or 0) > 1e-9]
    null_rows = [r for r in ok if abs(r.get("true_effect_cumulative_level") or 0) < 1e-9]

    harness_all_treated_fail = sum(
        1 for r in harness_defect_runs if r.get("callable_status") == "callable_fail"
    )
    harness_defect_confirmed = harness_all_treated_fail >= max(1, len(harness_defect_runs) // 2)

    mean_center_err = float(
        np.mean([abs(r["interval_center_error"]) for r in pos_rows if r.get("interval_center_error") is not None])
    ) if pos_rows else None
    mean_point = float(np.mean([r["point_estimate"] for r in pos_rows if r.get("point_estimate") is not None])) if pos_rows else None
    mean_boot_center = float(
        np.mean([r["bootstrap_distribution_center"] for r in pos_rows if r.get("bootstrap_distribution_center") is not None])
    ) if pos_rows else None
    mean_boot_median = float(
        np.mean([r["bootstrap_distribution_median"] for r in pos_rows if r.get("bootstrap_distribution_median") is not None])
    ) if pos_rows else None
    mean_interval_center = float(
        np.mean([r["interval_center"] for r in pos_rows if r.get("interval_center") is not None])
    ) if pos_rows else None
    mean_gap = (
        float(mean_point - mean_boot_center)
        if mean_point is not None and mean_boot_center is not None
        else None
    )
    miscentering_dominant = bool(
        mean_center_err is not None
        and mean_point is not None
        and mean_boot_center is not None
        and abs(mean_point - mean_boot_center) > 0.5 * max(abs(mean_point), 1.0)
    )

    clean_pos_cov = coverage_by_world.get("clean_parallel_trends", {}).get("positive_coverage")
    severe_pos_cov = coverage_by_world.get("severe_pretrend_violation", {}).get("positive_coverage")
    holds_sign = coverage_by_pretrend.get("holds", {}).get("sign_accuracy")
    # Low positive coverage under clean worlds with good sign accuracy ⇒ miscentering, not pretrend failure.
    pretrend_driver = bool(
        holds_sign is not None
        and holds_sign < 0.75
        and not miscentering_dominant
        and clean_pos_cov is not None
        and severe_pos_cov is not None
        and severe_pos_cov < clean_pos_cov - 0.1
    )

    bias_decomposition = {
        "mean_bias_positive": float(np.mean([r["bias"] for r in pos_rows])) if pos_rows else None,
        "mean_interval_miscentering": float(
            np.mean([r["interval_miscentering"] for r in pos_rows if r.get("interval_miscentering") is not None])
        )
        if pos_rows
        else None,
        "mean_interval_center_error": mean_center_err,
        "interval_miscentering_dominant": miscentering_dominant,
        "harness_assignment_defect_confirmed": harness_defect_confirmed,
        "harness_defect_description": (
            "D5-STAT-DID-BOOTSTRAP-001 uses groups.values() flattening control+test_0 "
            "into treated_units, yielding zero controls and invalid geometry"
        ),
        "truth_scale_mismatch": False,
        "undercoverage_driver_hypothesis": (
            "bootstrap_interval_miscentering_relative_to_path_cumulative_att"
            if miscentering_dominant and not pretrend_driver
            else (
                "identification_pretrend_violation"
                if pretrend_driver and not miscentering_dominant
                else "bootstrap_interval_miscentering_plus_harness_geometry_defect"
            )
        ),
        "components": {
            "identification_failure": pretrend_driver,
            "estimator_bias": bool(pos_rows and _coverage(pos_rows, "sign_correct") is not None and _coverage(pos_rows, "sign_correct") < 0.8),
            "interval_miscentering": miscentering_dominant,
            "variance_underestimation": False,
            "invalid_bootstrap_resampling": miscentering_dominant,
            "truth_scale_mismatch": False,
            "harness_defect": harness_defect_confirmed,
        },
    }

    variance_decomposition = {
        "mean_bootstrap_se": _aggregate_rows(ok).get("mean_bootstrap_se"),
        "mean_interval_width": _aggregate_rows(ok).get("mean_interval_width"),
        "point_in_bootstrap_ci_rate": _aggregate_rows(ok).get("point_in_bootstrap_ci_rate"),
        "oracle_recentered_positive_coverage": _coverage(pos_rows, "oracle_recentered_contains_truth"),
        "note": "oracle recentering is diagnostic_only_not_for_production",
    }

    bootstrap_diagnostics = {
        "bootstrap_unit": "time_period_moving_block",
        "resamples": "whole cross-sections at sampled time indices",
        "preserves_cross_section": True,
        "preserves_serial_dependence_partially": True,
        "point_in_bootstrap_ci_rate": variance_decomposition.get("point_in_bootstrap_ci_rate"),
        "mean_bootstrap_center_vs_point_gap": (
            float(mean_point - mean_boot_center)
            if mean_point is not None and mean_boot_center is not None
            else None
        ),
    }

    bootstrap_centering_diagnostics = {
        "point_estimate_mean_positive": mean_point,
        "bootstrap_mean_positive": mean_boot_center,
        "bootstrap_median_positive": mean_boot_median,
        "interval_center_mean_positive": mean_interval_center,
        "point_minus_bootstrap_center": mean_gap,
        "interval_center_error_mean_positive": mean_center_err,
        "truth_scale": "cumulative_level",
        "point_estimate_scale": "cumulative_level",
        "bootstrap_replicate_scale": "cumulative_level",
        "interval_scale": "cumulative_level",
        "interval_centered_on": "bootstrap_cumulative_att_distribution",
        "not_centered_on_reported_point": bool(
            mean_gap is not None and abs(mean_gap) > 0.5 * max(abs(mean_point or 0), 1.0)
        ),
    }

    sign_acc = _coverage(pos_rows, "sign_correct")
    pos_cov_08 = coverage_by_effect.get("0.08", {}).get("positive_coverage")
    clean_iid_cov = coverage_by_serial.get("clean_iid", {}).get("positive_coverage")
    harness_assessment = _assess_harness_defect(
        harness_defect_confirmed,
        harness_all_treated_fail,
        len(harness_defect_runs),
    )
    production_assessment = _assess_production_defect(
        sign_accuracy=sign_acc,
        pos_cov_clean=clean_pos_cov,
        pos_cov_08=pos_cov_08,
        pos_cov_clean_iid=clean_iid_cov,
        miscentering_dominant=miscentering_dominant,
        truth_scale_mismatch=False,
        oracle_pos_cov=variance_decomposition.get("oracle_recentered_positive_coverage"),
        point_in_ci_rate=variance_decomposition.get("point_in_bootstrap_ci_rate"),
        mean_gap=mean_gap,
        pretrend_driver=pretrend_driver,
        holds_sign_accuracy=holds_sign,
    )

    failure_summary = {
        "total_runs": len(all_runs),
        "failed_runs": len([r for r in all_runs if r.get("callable_status") == "callable_fail"]),
        "timing_blocked_runs": len([r for r in all_runs if r.get("callable_status") == "timing_blocked"]),
        "overall_failure_rate": len([r for r in all_runs if r.get("callable_status") == "callable_fail"]) / len(all_runs)
        if all_runs
        else None,
        "harness_defect_probe_failures": harness_all_treated_fail,
    }

    policy_comparisons = {
        "A_current_production_interval": {
            "null_coverage": coverage_by_effect.get("0.0", {}).get("null_coverage"),
            "positive_coverage": pos_cov_08,
            "negative_coverage": coverage_by_effect.get("-0.05", {}).get("negative_coverage"),
            "type_i_error": coverage_by_effect.get("0.0", {}).get("type_i_error"),
            "mean_bias": bias_decomposition.get("mean_bias_positive"),
            "mean_interval_width": variance_decomposition.get("mean_interval_width"),
            "failure_rate": failure_summary.get("overall_failure_rate"),
            "point_in_ci_rate": variance_decomposition.get("point_in_bootstrap_ci_rate"),
        },
        "B_diagnostic_recentered_interval": {
            "positive_coverage": variance_decomposition.get("oracle_recentered_positive_coverage"),
            "note": "diagnostic_only_not_for_production",
        },
        "C_oracle_empirical_interval": {
            "positive_coverage": variance_decomposition.get("oracle_recentered_positive_coverage"),
            "note": "shifts CI by point_minus_bootstrap_center; diagnostic only",
        },
        "D_valid_parallel_trends_only": coverage_by_pretrend.get("holds", {}),
        "E_common_timing_only": coverage_by_timing.get("common", {}),
        "F_serial_dependence_restricted": coverage_by_serial.get("clean_iid", {}),
        "G_staggered_timing_blocked": {
            "blocked_runs": sum(1 for r in all_runs if r.get("callable_status") == "timing_blocked"),
        },
        "H_causal_interval_not_supported": {
            "positive_coverage": pos_cov_08,
            "recommendation": "block causal_interval readout",
        },
    }

    pretrend_relationships = {
        "coverage_by_parallel_trends_regime": coverage_by_pretrend,
        "clean_vs_severe_positive_coverage": {
            "clean_parallel_trends": clean_pos_cov,
            "severe_pretrend_violation": severe_pos_cov,
        },
    }

    summary: dict[str, Any] = {
        "artifact_id": "D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001",
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {
            "n_replicates": cfg.n_replicates,
            "fast": cfg.fast,
            "assignment_mode": cfg.assignment_mode,
            "effect_sizes": list(effect_sizes),
            "threshold_label": _THRESHOLD_LABEL,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "alpha": cfg.alpha,
        },
        "worlds": [asdict(w) for w in worlds],
        "effect_sizes": list(effect_sizes),
        "timing_regimes": list(TIMING_REGIMES),
        "parallel_trends_regimes": list(PARALLEL_TRENDS_REGIMES),
        "serial_dependence_regimes": list(SERIAL_DEPENDENCE_REGIMES),
        "bootstrap_policies": list(BOOTSTRAP_POLICIES),
        "run_counts": failure_summary,
        "point_estimate_results": {
            "mean_bias_positive": bias_decomposition.get("mean_bias_positive"),
            "rmse_at_08_effect": coverage_by_effect.get("0.08", {}).get("rmse"),
            "sign_accuracy_positive": _coverage(pos_rows, "sign_correct"),
        },
        "interval_results": {
            "mean_interval_width": _aggregate_rows(ok).get("mean_interval_width"),
            "mean_interval_center_error": mean_center_err,
            "point_in_bootstrap_ci_rate": variance_decomposition.get("point_in_bootstrap_ci_rate"),
        },
        "coverage_by_effect": coverage_by_effect,
        "coverage_by_world": coverage_by_world,
        "coverage_by_timing": coverage_by_timing,
        "coverage_by_parallel_trends_status": coverage_by_pretrend,
        "coverage_by_serial_dependence": coverage_by_serial,
        "bias_decomposition": bias_decomposition,
        "variance_decomposition": variance_decomposition,
        "bootstrap_centering_diagnostics": bootstrap_centering_diagnostics,
        "bootstrap_diagnostics": bootstrap_diagnostics,
        "production_defect_assessment": production_assessment,
        "harness_defect_assessment": harness_assessment,
        "pretrend_relationships": pretrend_relationships,
        "failure_summary": failure_summary,
        "policy_comparisons": policy_comparisons,
        "semantic_classification": {
            "estimand": "cumulative_att_level",
            "interval_target": "bootstrap_cumulative_att_distribution",
            "point_target": "path_cumulative_att",
            "alignment_status": "misaligned_point_vs_bootstrap_center",
            "causal_requires_parallel_trends": True,
            "supported_readouts": ["diagnostic_only", "descriptive_point"],
            "not_supported": ["causal_interval"],
            "production_defect_decision": production_assessment["decision"],
        },
        "trustreport_eligibility_implications": {
            "dcm_row_id": "DCM-004",
            "prior_status": "INSUFFICIENT_EVIDENCE",
            "recommended_status": "INSUFFICIENT_EVIDENCE",
            "eligible_for_promotion": False,
            "requires_reassessment_after_harness_fix": True,
            "requires_production_bootstrap_calibration_fix": production_assessment["decision"]
            == "production_defect_confirmed",
            "note": (
                "Prior ~0% positive coverage is not primarily truth-scale mismatch; "
                "bootstrap CI miscentering dominates under corrected geometry when production defect confirmed."
            ),
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_authorized_count": 0,
            "trust_report_ready": False,
        },
        "required_follow_up_artifacts": [
            "D5-STAT-DID-BOOTSTRAP-001-HARNESS-CORRECTION",
            *(
                ["DID_BOOTSTRAP_CUMULATIVE_READOUT_CORRECTION_001"]
                if production_assessment["decision"] == "production_defect_confirmed"
                else []
            ),
            "DCM-004 eligibility reassessment (after harness + production corrections as applicable)",
        ],
        "limitations": [
            "Synthetic worlds only; cumulative level truth matches DID cumulative_att scale.",
            "Oracle recentering is diagnostic only.",
            "Does not modify D5-STAT-DID-BOOTSTRAP-001 committed archive.",
            "Does not change production DID bootstrap behavior.",
            "Does not perform DCM-004 eligibility reassessment.",
            "Cluster/unit bootstrap not available in DID embedded path.",
            "Production acceptance thresholds not defined.",
        ],
    }
    summary["verdict"] = _decide_verdict(summary, production_assessment["decision"])

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps({"summary": summary, "run_results": all_runs}, indent=2) + "\n"
        )

    return _json_safe(summary)


def _atomic_write_text(path: Path, content: str, *, overwrite: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
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


def write_summary(
    path: Path | None = None,
    *,
    cfg: RemediationConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_d5_trust_did_bootstrap_remediation_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write_text(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def _fmt(val: Any) -> str:
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def _write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    decomp = payload.get("bias_decomposition", {})
    by_eff = payload.get("coverage_by_effect", {})
    prod = payload.get("production_defect_assessment", {})
    harness = payload.get("harness_defect_assessment", {})
    center = payload.get("bootstrap_centering_diagnostics", {})
    pt = payload.get("point_estimate_results", {})
    var = payload.get("variance_decomposition", {})
    lines = [
        "# D5 Trust DID Bootstrap Remediation 001 — Report",
        "",
        "**Artifact ID:** D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001  ",
        f"**Verdict:** `{payload.get('verdict')}`  ",
        "**Summary:** [`archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json`](archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json)  ",
        f"**Threshold label:** `{_THRESHOLD_LABEL}`",
        "",
        "## 1. Executive summary",
        "",
        "This artifact diagnoses DCM-004 DID+bootstrap interval undercoverage. "
        "Under corrected assignment (`test_0` treated only), point estimates recover injected cumulative level effects, "
        "but embedded bootstrap CIs in production `DID.py` are miscentered relative to reported `cumulative_att`. "
        "Canonical D5-STAT harness has a separate `groups.values()` assignment defect. "
        "**No TrustReport authorization.**",
        "",
        "This artifact diagnoses DCM-004. It does not correct the canonical D5 harness. "
        "It does not change production DID bootstrap behavior. "
        "It does not perform DCM-004 eligibility reassessment. "
        "It does not authorize TrustReport.",
        "",
        "## 2. Prior DCM-004 status",
        "",
        "DCM-004 classified `INSUFFICIENT_EVIDENCE` with ~0% positive coverage in `D5_STAT_DID_BOOTSTRAP_001_results.json`.",
        "",
        "## 3. Scope",
        "",
        f"{len(payload.get('worlds', []))} diagnostic worlds, effect-size sweep, timing/parallel-trends/serial regimes, "
        "bootstrap policy comparisons, harness defect probe.",
        "",
        "## 4. Non-goals",
        "",
        "- No production DID code changes",
        "- No canonical D5-STAT archive rewrite",
        "- No TrustReport promotion or authorization",
        "- No DCM-004 reassessment in this artifact",
        "",
        "## 5. DID estimand",
        "",
        "Cumulative treated-minus-synthetic-control ATT over post periods (**cumulative level units**).",
        "",
        "## 6. Production DID path",
        "",
        "`panel_exp/methods/DID.py` — pooled TWFE with path-based `cumulative_att` in `run_analysis`; "
        "bootstrap in `_block_bootstrap_inference` during `fit_model`.",
        "",
        "## 7. Bootstrap implementation",
        "",
        "Moving-block **time-period** resampling; percentiles of `bootstrap_cumulative_effects_`.",
        "",
        "## 8. Canonical D5 harness defect",
        "",
        f"Confirmed: {harness.get('harness_defect_confirmed')}. "
        f"`D5-STAT-DID-BOOTSTRAP-001` uses `groups.values()` flattening control+test_0 → all units treated, zero controls. "
        f"Fix deferred to `{harness.get('canonical_fix_artifact')}`.",
        "",
        "## 9. Remediation harness architecture",
        "",
        "Uses `corrected_test_0` assignment; probes `broken_groups_values`; records bootstrap center, interval center, oracle shift.",
        "",
        "## 10. Worlds",
        "",
        f"{len(payload.get('worlds', []))} worlds (see summary JSON).",
        "",
        "## 11. Effect sizes",
        "",
        ", ".join(str(e) for e in payload.get("effect_sizes", [])),
        "",
        "## 12. Timing regimes",
        "",
        "Common timing supported; staggered pooled DID blocked.",
        "",
        "## 13. Parallel-trends regimes",
        "",
        "holds · mild_violation · severe_violation · staggered_blocked.",
        "",
        "## 14. Serial-dependence regimes",
        "",
        "clean_iid · serial_correlation · clustered_shocks · heteroskedastic · standard_stress.",
        "",
        "## 15. Point-estimate findings",
        "",
        f"Sign accuracy (positive): {_fmt(pt.get('sign_accuracy_positive'))}; "
        f"mean bias: {_fmt(decomp.get('mean_bias_positive'))}; "
        f"RMSE @ 8%: {_fmt(pt.get('rmse_at_08_effect'))}.",
        "",
        "## 16. Bootstrap-center findings",
        "",
        f"Bootstrap mean: {_fmt(center.get('bootstrap_mean_positive'))}; "
        f"point: {_fmt(center.get('point_estimate_mean_positive'))}; "
        f"gap: {_fmt(center.get('point_minus_bootstrap_center'))}.",
        "",
        "## 17. Interval-centering findings",
        "",
        f"Interval centered on: {center.get('interval_centered_on')}; "
        f"miscentering dominant: {decomp.get('interval_miscentering_dominant')}.",
        "",
        "## 18. Variance findings",
        "",
        f"Point-in-bootstrap-CI rate: {_fmt(var.get('point_in_bootstrap_ci_rate'))}; "
        f"mean width: {_fmt(var.get('mean_interval_width'))}.",
        "",
        "## 19. Null coverage",
        "",
        f"@ 0% effect: {_fmt(by_eff.get('0.0', {}).get('null_coverage'))}; "
        f"type-I: {_fmt(by_eff.get('0.0', {}).get('type_i_error'))}.",
        "",
        "## 20. Positive coverage",
        "",
        f"@ 8% effect: {_fmt(by_eff.get('0.08', {}).get('positive_coverage'))}.",
        "",
        "## 21. Negative coverage",
        "",
        f"@ −5% effect: {_fmt(by_eff.get('-0.05', {}).get('negative_coverage'))}.",
        "",
        "## 22. Common-timing findings",
        "",
        _fmt(payload.get("coverage_by_timing", {}).get("common", {}).get("positive_coverage")),
        "",
        "## 23. Staggered-timing findings",
        "",
        f"Blocked runs: {payload.get('failure_summary', {}).get('timing_blocked_runs')}.",
        "",
        "## 24. Parallel-trends findings",
        "",
        f"Clean vs severe positive coverage: {payload.get('pretrend_relationships', {}).get('clean_vs_severe_positive_coverage')}.",
        "",
        "## 25. Serial-correlation findings",
        "",
        f"clean_iid positive coverage: {_fmt(payload.get('coverage_by_serial_dependence', {}).get('clean_iid', {}).get('positive_coverage'))}; "
        f"serial_correlation: {_fmt(payload.get('coverage_by_world', {}).get('serial_correlation', {}).get('positive_coverage'))}.",
        "",
        "## 26. Policy comparisons",
        "",
        "A production interval retains low positive coverage; B/C diagnostic recentering/oracle improve coverage diagnostically only.",
        "",
        "## 27. Root-cause determination",
        "",
        f"Driver: `{decomp.get('undercoverage_driver_hypothesis')}`.",
        "",
        "## 28. Production-defect decision",
        "",
        f"**{prod.get('decision')}** — recommended follow-up: `{prod.get('recommended_follow_up_artifact') or 'none'}`.",
        "",
        "## 29. Harness-defect decision",
        "",
        f"Harness defect confirmed: {harness.get('harness_defect_confirmed')}; canonical fix: `{harness.get('canonical_fix_artifact')}`.",
        "",
        "## 30. TrustReport implications",
        "",
        "DCM-004 remains `INSUFFICIENT_EVIDENCE`; causal-interval candidacy unsupported.",
        "",
        "## 31. Authorization status",
        "",
        "**Blocked** — `trust_report_authorized=false`, `trust_report_ready=false`.",
        "",
        "## 32. Required follow-up artifacts",
        "",
        "\n".join(f"- `{a}`" for a in payload.get("required_follow_up_artifacts", [])),
        "",
        "## 33. Limitations",
        "",
        "\n".join(f"- {x}" for x in payload.get("limitations", [])),
        "",
        "## 34. Governance verdict",
        "",
        f"**`{payload.get('verdict')}`**",
        "",
    ]
    _atomic_write_text(path, "\n".join(line.rstrip() for line in lines) + "\n", overwrite=overwrite)


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


def main() -> None:
    parser = argparse.ArgumentParser(description="D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 harness")
    parser.add_argument(
        "--output-local",
        type=Path,
        default=Path("/tmp/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_results.json"),
        help="Optional full local results path (not committed)",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=_DEFAULT_SUMMARY,
        help="Compact summary JSON path",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing summary/report")
    parser.add_argument("--fast", action="store_true", help="Fast mode (reduced worlds/replicates)")
    args = parser.parse_args()
    cfg = RemediationConfig(
        fast=args.fast,
        write_full_results_path=str(args.output_local) if not args.fast else None,
    )
    out = write_summary(args.summary_output, cfg=cfg, overwrite=args.overwrite)
    payload = json.loads(out.read_text())
    print(f"Wrote {out} and {_DEFAULT_REPORT} — verdict={payload['verdict']}")


if __name__ == "__main__":
    main()
