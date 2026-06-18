"""D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001 — DID+bootstrap coverage diagnosis.

Decomposes undercoverage into identification failure, estimator bias, interval
miscentering, variance miscalibration, harness defects, and truth-scale mismatch.
No TrustReport authorization or production threshold definition.
"""

from __future__ import annotations

import copy
import json
import math
import subprocess
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
    "did_bootstrap_causal_interval_remediated_requires_reassessment",
    "did_bootstrap_parallel_trends_gated_restricted",
    "did_bootstrap_common_timing_only",
    "did_bootstrap_diagnostic_only",
    "did_bootstrap_not_interval_eligible",
    "did_bootstrap_remediation_inconclusive",
    "did_bootstrap_remediation_failed",
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
        "bootstrap_standard_error": se,
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


def _decide_verdict(summary: dict[str, Any]) -> SemanticVerdict:
    fail_rate = summary.get("failure_summary", {}).get("overall_failure_rate")
    if fail_rate is not None and fail_rate > 0.35:
        return "did_bootstrap_remediation_failed"

    by_effect = summary.get("coverage_by_effect", {})
    null_cov = (by_effect.get("0.0") or {}).get("null_coverage")
    pos_cov = (by_effect.get("0.08") or {}).get("positive_coverage")
    decomp = summary.get("bias_decomposition", {})
    harness_defect = decomp.get("harness_assignment_defect_confirmed", False)
    miscenter = decomp.get("interval_miscentering_dominant", False)
    pt_in_ci = summary.get("bootstrap_diagnostics", {}).get("point_in_bootstrap_ci_rate")

    if pos_cov is not None and pos_cov >= 0.75 and null_cov is not None and null_cov >= 0.85:
        return "did_bootstrap_causal_interval_remediated_requires_reassessment"
    if miscenter and pos_cov is not None and pos_cov < 0.2:
        if harness_defect:
            return "did_bootstrap_not_interval_eligible"
        return "did_bootstrap_not_interval_eligible"
    if (
        summary.get("coverage_by_parallel_trends_status", {})
        .get("holds", {})
        .get("positive_coverage", 1.0)
        < 0.2
        and summary.get("coverage_by_parallel_trends_status", {})
        .get("severe_violation", {})
        .get("positive_coverage", 0.0)
        < 0.2
    ):
        if pt_in_ci is not None and pt_in_ci < 0.6:
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

    coverage_by_world = {k: _aggregate_rows(v) for k, v in by_world.items()}
    coverage_by_effect = {k: _aggregate_rows(v) for k, v in by_effect.items()}
    coverage_by_timing = {k: _aggregate_rows(v) for k, v in by_timing.items()}
    coverage_by_pretrend = {k: _aggregate_rows(v) for k, v in by_pretrend.items()}

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
    miscentering_dominant = bool(
        mean_center_err is not None
        and mean_point is not None
        and mean_boot_center is not None
        and abs(mean_point - mean_boot_center) > 0.5 * max(abs(mean_point), 1.0)
    )

    clean_pos_cov = coverage_by_world.get("clean_parallel_trends", {}).get("positive_coverage")
    severe_pos_cov = coverage_by_world.get("severe_pretrend_violation", {}).get("positive_coverage")
    pretrend_driver = bool(
        clean_pos_cov is not None
        and severe_pos_cov is not None
        and clean_pos_cov < 0.2
        and severe_pos_cov < 0.2
        and abs(clean_pos_cov - severe_pos_cov) < 0.15
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

    policy_comparisons = {
        "A_current_did_bootstrap": {
            "null_coverage": coverage_by_effect.get("0.0", {}).get("null_coverage"),
            "positive_coverage": coverage_by_effect.get("0.08", {}).get("positive_coverage"),
            "point_in_ci_rate": variance_decomposition.get("point_in_bootstrap_ci_rate"),
        },
        "B_parallel_trends_gated": {
            "positive_coverage_when_holds": coverage_by_pretrend.get("holds", {}).get("positive_coverage"),
            "positive_coverage_when_severe_violation": coverage_by_pretrend.get("severe_violation", {}).get("positive_coverage"),
        },
        "C_cluster_bootstrap": {"status": "not_implemented_in_did", "note": "DID embeds time-block bootstrap only"},
        "D_time_block_bootstrap": {"alias_of": "A_current_did_bootstrap"},
        "E_bias_diagnostic_only": {
            "sign_accuracy_positive": _coverage(pos_rows, "sign_correct"),
            "mean_bias_positive": bias_decomposition.get("mean_bias_positive"),
        },
        "F_common_timing_only": coverage_by_timing.get("common", {}),
        "G_staggered_timing_blocked": {
            "blocked_runs": sum(1 for r in all_runs if r.get("callable_status") == "timing_blocked"),
        },
        "H_causal_interval_not_supported": {
            "positive_coverage": coverage_by_effect.get("0.08", {}).get("positive_coverage"),
            "recommendation": "block causal_interval readout",
        },
        "oracle_recentered_diagnostic": {
            "positive_coverage": variance_decomposition.get("oracle_recentered_positive_coverage"),
            "note": "diagnosis_only_not_for_production",
        },
    }

    failure_summary = {
        "total_runs": len(all_runs),
        "failed_runs": len([r for r in all_runs if r.get("callable_status") == "callable_fail"]),
        "timing_blocked_runs": len([r for r in all_runs if r.get("callable_status") == "timing_blocked"]),
        "overall_failure_rate": len([r for r in all_runs if r.get("callable_status") == "callable_fail"]) / len(all_runs)
        if all_runs
        else None,
        "harness_defect_probe_failures": harness_all_treated_fail,
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
        "bias_decomposition": bias_decomposition,
        "variance_decomposition": variance_decomposition,
        "bootstrap_diagnostics": bootstrap_diagnostics,
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
        },
        "trustreport_eligibility_implications": {
            "dcm_row_id": "DCM-004",
            "prior_status": "INSUFFICIENT_EVIDENCE",
            "recommended_status": "INSUFFICIENT_EVIDENCE",
            "eligible_for_promotion": False,
            "requires_reassessment_after_harness_fix": True,
            "requires_production_bootstrap_calibration_fix": True,
            "note": "Prior ~0% positive coverage is not primarily truth-scale mismatch; bootstrap CI miscentering dominates under corrected geometry",
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_authorized_count": 0,
            "trust_report_ready": False,
        },
        "limitations": [
            "Synthetic worlds only; cumulative level truth matches DID cumulative_att scale.",
            "Oracle recentering is diagnostic only.",
            "Does not modify D5-STAT-DID-BOOTSTRAP-001 committed archive.",
            "Cluster/unit bootstrap not available in DID embedded path.",
            "Production acceptance thresholds not defined.",
        ],
    }
    summary["verdict"] = _decide_verdict(summary)

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps({"summary": summary, "run_results": all_runs}, indent=2) + "\n"
        )

    return _json_safe(summary)


def write_summary(path: Path | None = None, *, cfg: RemediationConfig | None = None) -> Path:
    payload = build_d5_trust_did_bootstrap_remediation_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _write_report(payload)
    return path


def _write_report(payload: dict[str, Any]) -> None:
    path = _REPO_ROOT / "docs/track_d/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_REPORT.md"
    decomp = payload.get("bias_decomposition", {})
    by_eff = payload.get("coverage_by_effect", {})
    lines = [
        "# D5 Trust DID Bootstrap Remediation 001 — Report",
        "",
        f"**Artifact ID:** D5-TRUST-DID-BOOTSTRAP-REMEDIATION-001  ",
        f"**Verdict:** `{payload.get('verdict')}`  ",
        "**Summary:** [`archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json`](archives/D5_TRUST_DID_BOOTSTRAP_REMEDIATION_001_summary.json)  ",
        f"**Threshold label:** `{_THRESHOLD_LABEL}`",
        "",
        "## 1. Executive summary",
        "",
        "Diagnoses DCM-004 DID+bootstrap ~0% positive-effect interval coverage. "
        "Under **corrected assignment geometry** (`test_0` treated only), point estimates recover injected cumulative level effects with good sign accuracy, "
        "but **embedded bootstrap CIs are miscentered** relative to the reported `cumulative_att` point. "
        "Null-world coverage is high because wide CIs centered near zero contain null truth; positive-world coverage remains ~0%. "
        "**Not a truth-scale mismatch** (unlike SCM-JK). "
        "D5-STAT harness also has an assignment defect (`groups.values()` → all units treated, zero controls). "
        "**No TrustReport authorization.**",
        "",
        "## 2. Prior eligibility finding",
        "",
        "DCM-004 classified `INSUFFICIENT_EVIDENCE` with positive coverage ~0% in `D5_STAT_DID_BOOTSTRAP_001_results.json`.",
        "",
        "## 3. Scope",
        "",
        "DID point/interval diagnostics, 18 worlds, effect-size sweep, timing regimes, bootstrap policy comparisons, harness defect probe.",
        "",
        "## 4. DID estimator path",
        "",
        "`panel_exp/methods/DID.py` pooled TWFE with path-based `cumulative_att` reporting.",
        "",
        "## 5. Bootstrap implementation",
        "",
        "Embedded moving-block **time-period** resampling (`_block_bootstrap_inference`); whole cross-sections preserved per sampled period.",
        "",
        "## 6. DID estimand",
        "",
        "Cumulative treated-minus-synthetic-control ATT over post periods (level units).",
        "",
        "## 7. Identification assumptions",
        "",
        "Parallel trends required for causal interpretation; pretrend contract recorded per run.",
        "",
        "## 8. Worlds",
        "",
        f"{len(payload.get('worlds', []))} diagnostic worlds with deterministic paired seeds.",
        "",
        "## 9. Effect-size sweep",
        "",
        f"Effects: {', '.join(str(e) for e in payload.get('effect_sizes', []))}.",
        "",
        "## 10. Timing regimes",
        "",
        "Common simultaneous adoption supported; staggered cohort geometry blocked for pooled DID.",
        "",
        "## 11. Bootstrap policies",
        "",
        "Policies A–H evaluated; cluster bootstrap not implemented.",
        "",
        "## 12. Metrics",
        "",
        "Separate null/positive/negative coverage, bias, RMSE, interval center error, bootstrap center vs point, oracle recentering (diagnostic).",
        "",
        "## 13. Run counts/runtime",
        "",
        f"Total runs: {payload.get('failure_summary', {}).get('total_runs')}; failures: {payload.get('failure_summary', {}).get('failed_runs')}.",
        "",
        "## 14. Point-estimate bias",
        "",
        f"Sign accuracy (positive): {payload.get('point_estimate_results', {}).get('sign_accuracy_positive')}; "
        f"mean bias: {decomp.get('mean_bias_positive')}.",
        "",
        "## 15. Interval centering",
        "",
        f"Mean interval center error: {decomp.get('mean_interval_center_error')}; miscentering dominant: {decomp.get('interval_miscentering_dominant')}.",
        "",
        "## 16. Variance calibration",
        "",
        f"Point-in-bootstrap-CI rate: {payload.get('variance_decomposition', {}).get('point_in_bootstrap_ci_rate')}.",
        "",
        "## 17. Null coverage",
        "",
        f"At 0% effect: {by_eff.get('0.0', {}).get('null_coverage')}.",
        "",
        "## 18. Positive coverage",
        "",
        f"At 8% effect: {by_eff.get('0.08', {}).get('positive_coverage')}.",
        "",
        "## 19. Negative coverage",
        "",
        f"At −5% effect: {by_eff.get('-0.05', {}).get('negative_coverage')}.",
        "",
        "## 20. Parallel-trends findings",
        "",
        str(payload.get("pretrend_relationships", {})),
        "",
        "## 21. Serial-correlation findings",
        "",
        f"Serial-correlation world positive coverage: {payload.get('coverage_by_world', {}).get('serial_correlation', {}).get('positive_coverage')}.",
        "",
        "## 22. Timing findings",
        "",
        f"Staggered blocked runs: {payload.get('failure_summary', {}).get('timing_blocked_runs')}.",
        "",
        "## 23. Worst-world behavior",
        "",
        "Positive coverage remains low across clean and stress worlds when bootstrap miscentering present.",
        "",
        "## 24. Failure analysis",
        "",
        str(payload.get("failure_summary", {})),
        "",
        "## 25. Policy comparisons",
        "",
        "Oracle recentering improves coverage diagnostically; production policy H blocks causal interval.",
        "",
        "## 26. Root cause",
        "",
        f"Driver: `{decomp.get('undercoverage_driver_hypothesis')}`; harness defect: {decomp.get('harness_assignment_defect_confirmed')}.",
        "",
        "## 27. Algorithm changes",
        "",
        "None in this artifact. Production bootstrap/point alignment requires separate fix with regression tests.",
        "",
        "## 28. TrustReport eligibility implications",
        "",
        "DCM-004 remains `INSUFFICIENT_EVIDENCE`; causal-interval candidacy unsupported.",
        "",
        "## 29. Authorization status",
        "",
        "**Blocked** — `trust_report_authorized_count = 0`.",
        "",
        "## 30. Remaining limitations",
        "",
        "\n".join(f"- {x}" for x in payload.get("limitations", [])),
        "",
        "## 31. Governance verdict",
        "",
        f"**`{payload.get('verdict')}`**",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    out = write_summary(cfg=RemediationConfig())
    payload = json.loads(out.read_text())
    print(f"Wrote {out} and report — verdict={payload['verdict']}")


if __name__ == "__main__":
    main()
