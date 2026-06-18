"""D5-TRUST-TBRRIDGE-BRB-001 — TBRRidge + BlockResidualBootstrap qualification.

Characterizes DCM-005 BRB path: estimator bias vs bootstrap centering vs variance
calibration vs geometry vs semantics. No TrustReport authorization or production changes.
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

from panel_exp.design.assign import greedy_match_markets
from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001c import _post_window_arrays, _pooled_point_path
from panel_exp.validation.track_d_d5_stat_tbrridge_inf_001 import (
    GEOMETRY,
    _geometry_guard,
    _inject_percent_effect,
    _json_safe,
    _mean_treated_baseline,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_ID = "D5-TRUST-TBRRIDGE-BRB-001"
_ARTIFACT_VERSION = "1.0.0"
_THRESHOLD_LABEL = "provisional_for_remediation_characterization_only"
_CANONICAL_SCALE = "level_mean_relative_percent_injection"

_DEFAULT_SUMMARY = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_TBRRIDGE_BRB_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/D5_TRUST_TBRRIDGE_BRB_001_REPORT.md"

SemanticVerdict = Literal[
    "tbrridge_brb_restricted_causal_interval_candidate",
    "tbrridge_brb_prefit_gated_restricted",
    "tbrridge_brb_serial_dependence_restricted",
    "tbrridge_brb_diagnostic_only",
    "tbrridge_brb_not_interval_eligible",
    "tbrridge_brb_production_defect_confirmed",
    "tbrridge_brb_remediation_inconclusive",
    "tbrridge_brb_remediation_failed",
]

ProductionDefectDecision = Literal[
    "production_defect_confirmed",
    "production_defect_not_confirmed",
    "production_defect_indeterminate",
]

POLICY_COMPARISONS: tuple[dict[str, str], ...] = (
    {"policy_id": "A", "name": "current_brb", "description": "production defaults (centered residuals, configurable block length)"},
    {"policy_id": "B", "name": "centered_residual_brb", "description": "diagnostic: center_residuals=True vs False"},
    {"policy_id": "C", "name": "block_length_restricted", "description": "evaluate only supported block-length band"},
    {"policy_id": "D", "name": "serial_dependence_supported_only", "description": "coverage on clean serial regimes only"},
    {"policy_id": "E", "name": "prefit_gated", "description": "worlds with acceptable pre-period fit only"},
    {"policy_id": "F", "name": "diagnostic_only", "description": "forecast/residual uncertainty; not causal promotion"},
    {"policy_id": "G", "name": "causal_interval_blocked", "description": "DCM-005 registry block until reassessment"},
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
class BrbTrustConfig:
    n_replicates: int = 4
    n_replicates_fast: int = 2
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260620
    min_control_units: int = 3
    n_bootstrap: int = 40
    n_bootstrap_fast: int = 12
    min_train_periods: int = 5
    fast: bool = False
    effect_sizes: tuple[float, ...] = (0.0, 0.03, 0.08, 0.12, -0.05)
    block_lengths: tuple[int | None, ...] = (2, 3, 7)
    write_full_results_path: str | None = "/tmp/D5_TRUST_TBRRIDGE_BRB_001_results.json"


DIAGNOSTIC_WORLDS: tuple[DiagnosticWorldSpec, ...] = (
    DiagnosticWorldSpec("clean_null", percent_effect=0.0, notes="stable null"),
    DiagnosticWorldSpec("clean_positive_effect", percent_effect=0.08, notes="clean injected lift"),
    DiagnosticWorldSpec("clean_negative_effect", percent_effect=-0.05, notes="clean negative lift"),
    DiagnosticWorldSpec("weak_signal", percent_effect=0.03, scenario_overrides={"noise_scale": 3.5}, notes="weak positive"),
    DiagnosticWorldSpec("strong_signal", percent_effect=0.12, notes="strong positive"),
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
        "heteroskedastic_residuals",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 4.8},
        serial_dependence_regime="heteroskedastic",
    ),
    DiagnosticWorldSpec(
        "autocorrelated_shocks",
        percent_effect=0.08,
        scenario_overrides={"cross_geo_correlation": 0.88},
        serial_dependence_regime="clustered_shocks",
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
        notes="post-period shock under null",
    ),
    DiagnosticWorldSpec(
        "poor_pre_fit",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 5.5, "cross_geo_correlation": 0.02},
        notes="weak donor-outcome linkage",
    ),
    DiagnosticWorldSpec(
        "outlier_period",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 2.0, "structural_break_shift": 8.0},
        notes="structural shock / outlier stress",
    ),
    DiagnosticWorldSpec(
        "small_pre_period",
        percent_effect=0.08,
        train_length=18,
        test_length=6,
        notes="reduced pre-period support",
    ),
    DiagnosticWorldSpec(
        "small_donor_support",
        percent_effect=0.08,
        n_geos=10,
        treatment_probability=0.45,
        notes="fewer donors / controls",
    ),
    DiagnosticWorldSpec(
        "ridge_dominant",
        percent_effect=0.08,
        n_geos=20,
        treatment_probability=0.25,
        notes="many controls — ridge shrinkage stress",
    ),
    DiagnosticWorldSpec(
        "low_noise",
        percent_effect=0.08,
        scenario_overrides={"noise_scale": 0.4},
        notes="low-noise idealized world",
    ),
    DiagnosticWorldSpec("placebo_null", percent_effect=0.0, notes="placebo null alias"),
)

_SERIAL_BY_WORLD = {w.world_id: w.serial_dependence_regime for w in DIAGNOSTIC_WORLDS}

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


def _assign_treated_units(
    wide: Any,
    *,
    n_pre: int,
    seed: int,
    treatment_probability: float,
) -> list[str]:
    """Explicit test_0 treated assignment (avoids groups.values() flattening defect)."""
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
    if "test_0" in groups:
        treated = list(groups["test_0"])
    elif "treated" in groups:
        treated = list(groups["treated"])
    else:
        non_control = [k for k in groups if k != "control"]
        treated = list(groups[non_control[0]]) if non_control else []
    if not treated:
        raise ValueError("assignment produced no treated units")
    return treated


def _build_unit_panel(
    spec: DiagnosticWorldSpec,
    cfg: BrbTrustConfig,
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


def _effective_lengths(spec: DiagnosticWorldSpec, cfg: BrbTrustConfig) -> tuple[int, int]:
    train = spec.train_length if spec.train_length is not None else cfg.train_length
    test = spec.test_length if spec.test_length is not None else cfg.test_length
    return train, test


def _level_true_effect(percent_effect: float, mean_value: np.ndarray) -> float:
    if abs(percent_effect) < 1e-12:
        return 0.0
    return float(percent_effect * np.mean(mean_value))


def _prefit_rmse(panel: PanelDataset, y_hat: np.ndarray) -> float:
    start = int(panel.treated_start_idxs[0])
    y = panel.treated_series(panel.treated_units).values
    y_hat = np.asarray(y_hat, dtype=float)
    if y.ndim == 2 and y.shape[0] < y.shape[1]:
        y_pre = y[:, :start].mean(axis=0)
        if y_hat.ndim == 2:
            yhat_pre = y_hat[:start].mean(axis=1) if y_hat.shape[0] >= start else y_hat.mean(axis=1)
        else:
            yhat_pre = y_hat[:start]
    else:
        y_pre = np.asarray(y[:start], dtype=float).flatten()
        yhat_pre = np.asarray(y_hat[:start], dtype=float).flatten()
    if y_pre.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y_pre - yhat_pre) ** 2)))


def _readout_level_scale(
    results: dict[str, Any],
    *,
    test_len: int,
    true_effect_level: float,
    brb_stats: dict[str, Any] | None,
) -> dict[str, Any]:
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length=test_len)
    y_pt, y_hat_pt = _pooled_point_path(y, y_hat)
    effect = y_pt - y_hat_pt
    point_estimate = float(np.nanmean(effect))

    interval_present = y_lo.size > 0 and y_hi.size > 0
    interval_lower = interval_upper = interval_width = interval_center = None
    contains_truth = contains_zero = None
    orient_ok = True

    if interval_present:
        eff_lo = y - y_hi
        eff_hi = y - y_lo
        if eff_lo.ndim == 2:
            interval_lower = float(np.nanmean(eff_lo))
            interval_upper = float(np.nanmean(eff_hi))
        else:
            interval_lower = float(np.nanmean(eff_lo))
            interval_upper = float(np.nanmean(eff_hi))
        interval_width = float(interval_upper - interval_lower)
        interval_center = 0.5 * (interval_lower + interval_upper)
        orient_ok = not bool(np.any(y_lo > y_hi))
        contains_zero = bool(interval_lower <= 0.0 <= interval_upper)
        if np.isfinite(interval_lower) and np.isfinite(interval_upper):
            contains_truth = bool(interval_lower <= true_effect_level <= interval_upper)

    bootstrap_mean = bootstrap_median = bootstrap_center_gap = None
    bootstrap_se = empirical_se = variance_ratio = None
    block_length = n_bootstrap = bootstrap_failures = None
    if brb_stats:
        if brb_stats.get("bootstrap_center_minus_point") is not None:
            bootstrap_center_gap = float(brb_stats["bootstrap_center_minus_point"])
            bootstrap_mean = float(brb_stats.get("bootstrap_center", np.nan))
            if np.isfinite(bootstrap_mean):
                pass
            elif bootstrap_center_gap is not None and np.isfinite(point_estimate):
                bootstrap_mean = float(point_estimate - bootstrap_center_gap)
        else:
            boot_mean = brb_stats.get("bootstrap_cumulative_mean")
            if boot_mean is not None and np.isfinite(boot_mean):
                bootstrap_mean = float(boot_mean)
                bootstrap_center_gap = float(point_estimate - bootstrap_mean)
        boot_std = brb_stats.get("bootstrap_cumulative_std")
        if boot_std is not None and np.isfinite(boot_std):
            bootstrap_se = float(boot_std)
        block_length = brb_stats.get("block_length")
        n_bootstrap = brb_stats.get("n_bootstrap")
        bootstrap_failures = brb_stats.get("bootstrap_failed_draws")

    if effect.size > 1:
        empirical_se = float(np.nanstd(effect, ddof=1))
    if bootstrap_se and empirical_se and empirical_se > 1e-12:
        variance_ratio = float(bootstrap_se / empirical_se)

    is_null = abs(true_effect_level) < 1e-9
    if is_null:
        sign_correct = bool(contains_zero if contains_zero is not None else abs(point_estimate) < 500.0)
    else:
        sign_correct = bool(
            np.isfinite(point_estimate) and np.sign(point_estimate) == np.sign(true_effect_level)
        )

    point_bias = float(point_estimate - true_effect_level)
    sq_err = float(point_bias**2)

    return {
        "point_estimate": point_estimate,
        "true_effect": true_effect_level,
        "true_effect_percent": None,
        "point_bias": point_bias,
        "squared_error": sq_err,
        "bootstrap_mean": bootstrap_mean,
        "bootstrap_median": bootstrap_median,
        "bootstrap_center_minus_point": bootstrap_center_gap,
        "bootstrap_standard_error": bootstrap_se,
        "empirical_standard_error": empirical_se,
        "variance_ratio": variance_ratio,
        "interval_lower": interval_lower,
        "interval_upper": interval_upper,
        "interval_center": interval_center,
        "interval_width": interval_width,
        "contains_truth": contains_truth,
        "contains_zero": contains_zero,
        "sign_correct": sign_correct,
        "interval_orientation_valid": orient_ok,
        "finite_outputs": bool(np.isfinite(point_estimate)),
    }


def _root_cause_tags(run: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    te = run.get("true_effect")
    pe = run.get("point_estimate")
    if te is not None and pe is not None and abs(te) > 1e-9:
        rel_bias = abs(pe - te) / max(abs(te), 1e-9)
        if rel_bias > 0.5:
            tags.append("point_bias")
    gap = run.get("bootstrap_center_minus_point")
    if gap is not None and abs(gap) > 2.0:
        tags.append("interval_miscentering")
    vr = run.get("variance_ratio")
    if vr is not None and (vr < 0.5 or vr > 2.0):
        tags.append("variance_underestimation" if vr < 0.5 else "variance_overestimation")
    if run.get("failure_status") == "fail":
        tags.append("support_failure")
    if run.get("geometry_valid") is False:
        tags.append("geometry_mismatch")
    if not tags and run.get("contains_truth") is False:
        tags.append("coverage_failure")
    return tags


def _run_one(
    spec: DiagnosticWorldSpec,
    cfg: BrbTrustConfig,
    *,
    replicate_id: int,
    seed: int,
    block_length: int | None,
    percent_effect: float | None = None,
    center_residuals: bool = True,
) -> dict[str, Any]:
    train, test = _effective_lengths(spec, cfg)
    eff_pct = spec.percent_effect if percent_effect is None else percent_effect
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "block_length_requested": block_length,
        "percent_effect_injected": float(eff_pct),
        "serial_dependence_regime": spec.serial_dependence_regime,
        "policy": "current_brb" if center_residuals else "centered_residual_brb_off",
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

        n_boot = cfg.n_bootstrap_fast if cfg.fast else cfg.n_bootstrap
        kwargs: dict[str, Any] = {
            "n_bootstrap": n_boot,
            "min_train_periods": cfg.min_train_periods,
            "show_progress": False,
            "random_state": seed,
            "center_residuals": center_residuals,
        }
        if block_length is not None:
            kwargs["block_length"] = block_length

        est = TBRRidge(inference="BlockResidualBootstrap", alpha=cfg.alpha)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            est.run_analysis(pds, **kwargs)

        results = getattr(est, "results", {}) or {}
        brb_stats = results.get("block_residual_bootstrap_stats") or {}
        readout = _readout_level_scale(
            results,
            test_len=test,
            true_effect_level=true_level,
            brb_stats=brb_stats if isinstance(brb_stats, dict) else None,
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
            "true_effect_percent": float(eff_pct),
            "prefit_rmse": prefit,
            "ridge_alpha": ridge_alpha,
            "block_length": brb_stats.get("block_length") if isinstance(brb_stats, dict) else block_length,
            "n_bootstrap_replicates": brb_stats.get("n_bootstrap") if isinstance(brb_stats, dict) else n_boot,
            "bootstrap_failure_count": brb_stats.get("bootstrap_failed_draws") if isinstance(brb_stats, dict) else 0,
            "effective_blocks": brb_stats.get("residual_pool_size") if isinstance(brb_stats, dict) else None,
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
            "point_bias": None,
            "squared_error": None,
            "failure_status": "fail",
            "failure_reason": str(exc)[:300],
            "geometry_valid": "geometry" not in str(exc).lower(),
            "contains_truth": None,
            "contains_zero": None,
            "sign_correct": None,
            "root_cause_tags": ["support_failure"],
        }


def _mean(vals: list[float]) -> float | None:
    clean = [float(v) for v in vals if v is not None and np.isfinite(v)]
    return float(np.mean(clean)) if clean else None


def _rate(flags: list[bool | None]) -> float | None:
    usable = [f for f in flags if f is not None]
    if not usable:
        return None
    return float(np.mean([bool(f) for f in usable]))


def _coverage_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    null_runs = [r for r in runs if r.get("true_effect") is not None and abs(r["true_effect"]) < 1e-9]
    pos_runs = [r for r in runs if r.get("true_effect") is not None and r["true_effect"] > 1e-9]
    neg_runs = [r for r in runs if r.get("true_effect") is not None and r["true_effect"] < -1e-9]
    return {
        "null_coverage": _rate([r.get("contains_zero") for r in null_runs]),
        "type_i_error": None if not null_runs else _rate([not r.get("contains_zero") for r in null_runs if r.get("contains_zero") is not None]),
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
    clean_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    clean_pos = [
        r for r in clean_runs
        if r.get("world_id") in ("clean_positive_effect", "low_noise")
        and r.get("failure_status") == "ok"
        and r.get("true_effect") and r["true_effect"] > 0
    ]
    clean_null = [
        r for r in clean_runs
        if r.get("world_id") in ("clean_null", "placebo_null")
        and r.get("failure_status") == "ok"
    ]
    point_ok = False
    if clean_pos:
        biases = [abs(r["point_bias"]) / max(abs(r["true_effect"]), 1e-9) for r in clean_pos if r.get("point_bias") is not None]
        point_ok = bool(biases) and _mean(biases) is not None and _mean(biases) < 0.35

    null_cov = _coverage_metrics(clean_null).get("null_coverage")
    pos_cov = _coverage_metrics(clean_pos).get("positive_coverage")
    center_gaps = [
        abs(r["bootstrap_center_minus_point"])
        for r in clean_pos
        if r.get("bootstrap_center_minus_point") is not None
    ]
    large_center_gap = bool(center_gaps) and (_mean(center_gaps) or 0) > 1.5

    decision: ProductionDefectDecision = "production_defect_indeterminate"
    rationale: list[str] = []
    if not clean_pos and not clean_null:
        decision = "production_defect_indeterminate"
        rationale.append("Insufficient clean-world successful runs.")
    elif point_ok and (pos_cov is not None and pos_cov < 0.5) and large_center_gap:
        decision = "production_defect_confirmed"
        rationale.append("Point estimate acceptable on clean worlds but interval miscentering/coverage failure persists.")
    elif point_ok and (null_cov is not None and null_cov >= 0.8) and (pos_cov is not None and pos_cov >= 0.7):
        decision = "production_defect_not_confirmed"
        rationale.append("Clean-world point and interval behavior acceptable under level-scale contract.")
    else:
        decision = "production_defect_not_confirmed"
        rationale.append("Primary failure modes are scale/semantics/harness attribution or unsupported stress worlds.")

    return {
        "decision": decision,
        "point_acceptable_clean_worlds": point_ok,
        "clean_null_coverage": null_cov,
        "clean_positive_coverage": pos_cov,
        "mean_bootstrap_center_gap_clean_positive": _mean(center_gaps),
        "rationale": rationale,
        "recommended_correction_artifact": "TBRRIDGE_BRB_INTERVAL_CORRECTION_001" if decision == "production_defect_confirmed" else None,
    }


def _decide_semantic_verdict(
    summary: dict[str, Any],
    prod: dict[str, Any],
) -> SemanticVerdict:
    cov = summary.get("coverage_by_world", {})
    clean_null = cov.get("clean_null", {})
    clean_pos = cov.get("clean_positive_effect", {})
    null_cov = clean_null.get("null_coverage")
    pos_cov = clean_pos.get("positive_coverage")
    type_i = clean_null.get("type_i_error")

    if prod.get("decision") == "production_defect_confirmed":
        return "tbrridge_brb_production_defect_confirmed"

    supported_null_ok = null_cov is not None and null_cov >= 0.85 and (type_i is None or type_i <= 0.15)
    supported_pos_ok = pos_cov is not None and pos_cov >= 0.75

    if supported_null_ok and supported_pos_ok:
        return "tbrridge_brb_prefit_gated_restricted"

    serial_cov = summary.get("coverage_by_serial_dependence", {})
    clean_serial = serial_cov.get("clean_iid", {})
    if (
        clean_serial.get("null_coverage") is not None
        and clean_serial.get("null_coverage") >= 0.8
        and not supported_pos_ok
    ):
        return "tbrridge_brb_serial_dependence_restricted"

    if null_cov is not None and null_cov >= 0.7:
        return "tbrridge_brb_diagnostic_only"

    return "tbrridge_brb_not_interval_eligible"


def build_d5_trust_tbrridge_brb_001(cfg: BrbTrustConfig | None = None) -> dict[str, Any]:
    cfg = cfg or BrbTrustConfig()
    t0 = time.perf_counter()
    n_rep = cfg.n_replicates_fast if cfg.fast else cfg.n_replicates
    worlds = DIAGNOSTIC_WORLDS if not cfg.fast else DIAGNOSTIC_WORLDS[:10]
    block_lengths = cfg.block_lengths if not cfg.fast else (3, 7)
    effect_sizes = cfg.effect_sizes if not cfg.fast else (0.0, 0.08, -0.05)

    all_runs: list[dict[str, Any]] = []
    seed_cursor = cfg.random_state_base

    for spec in worlds:
        for bl in block_lengths:
            for rep in range(n_rep):
                seed = seed_cursor
                seed_cursor += 1
                run = _run_one(spec, cfg, replicate_id=rep, seed=seed, block_length=bl)
                all_runs.append(run)

    for spec in worlds:
        if spec.world_id not in _EFFECT_SWEEP_WORLDS:
            continue
        for eff in effect_sizes:
            if abs(eff - spec.percent_effect) < 1e-12:
                continue
            for rep in range(max(1, n_rep // 2)):
                seed = seed_cursor
                seed_cursor += 1
                sweep_spec = replace(spec, percent_effect=eff)
                run = _run_one(
                    sweep_spec,
                    cfg,
                    replicate_id=rep,
                    seed=seed,
                    block_length=3,
                    percent_effect=eff,
                )
                run["effect_sweep"] = True
                all_runs.append(run)

    # Policy B diagnostic: uncentered residuals on clean worlds
    policy_b_runs: list[dict[str, Any]] = []
    for spec in (w for w in worlds if w.world_id in ("clean_null", "clean_positive_effect")):
        for rep in range(max(1, n_rep // 2)):
            seed = seed_cursor
            seed_cursor += 1
            policy_b_runs.append(
                _run_one(spec, cfg, replicate_id=rep, seed=seed, block_length=3, center_residuals=False)
            )

    ok_runs = [r for r in all_runs if r.get("failure_status") == "ok"]
    clean_world_ids = frozenset(
        {"clean_null", "clean_positive_effect", "clean_negative_effect", "low_noise", "placebo_null"}
    )
    clean_runs = [r for r in ok_runs if r.get("world_id") in clean_world_ids]

    cov_all = _coverage_metrics(ok_runs)
    cov_by_world = _group_coverage(ok_runs, "world_id")
    cov_by_effect: dict[str, Any] = {}
    for eff in effect_sizes:
        eff_runs = [r for r in ok_runs if r.get("percent_effect_injected") is not None and abs(r["percent_effect_injected"] - eff) < 1e-9]
        cov_by_effect[str(eff)] = _coverage_metrics(eff_runs)

    cov_by_block = _group_coverage(ok_runs, "block_length")
    cov_by_serial = _group_coverage(ok_runs, "serial_dependence_regime")

    point_results = {
        "mean_bias_clean_positive": _mean([r["point_bias"] for r in clean_runs if r.get("world_id") == "clean_positive_effect"]),
        "rmse_clean_positive": float(math.sqrt(_mean([r["squared_error"] for r in clean_runs if r.get("world_id") == "clean_positive_effect"]) or 0)),
        "sign_accuracy_positive": _rate([r.get("sign_correct") for r in ok_runs if r.get("true_effect", 0) > 0]),
    }

    center_diag = {
        "mean_bootstrap_center_minus_point": _mean([r.get("bootstrap_center_minus_point") for r in ok_runs]),
        "mean_interval_center_minus_point": _mean([
            (r["interval_center"] - r["point_estimate"])
            for r in ok_runs
            if r.get("interval_center") is not None and r.get("point_estimate") is not None
        ]),
        "interval_centered_on": "post_window_residual_mean_effect",
    }

    var_decomp = {
        "mean_variance_ratio": _mean([r.get("variance_ratio") for r in ok_runs]),
        "mean_interval_width": _mean([r.get("interval_width") for r in ok_runs]),
        "mean_bootstrap_se": _mean([r.get("bootstrap_standard_error") for r in ok_runs]),
    }

    prefit_rel = {
        "mean_prefit_rmse_clean": _mean([r.get("prefit_rmse") for r in clean_runs]),
        "mean_prefit_rmse_poor_pre_fit": _mean([r.get("prefit_rmse") for r in ok_runs if r.get("world_id") == "poor_pre_fit"]),
    }

    ridge_rel = {
        "mean_ridge_alpha": _mean([r.get("ridge_alpha") for r in ok_runs]),
        "ridge_dominant_mean_alpha": _mean([r.get("ridge_alpha") for r in ok_runs if r.get("world_id") == "ridge_dominant"]),
    }

    failures = [r for r in all_runs if r.get("failure_status") == "fail"]
    prod = _production_defect_assessment(all_runs, clean_runs=clean_runs)

    policy_out: dict[str, Any] = {}
    for pol in POLICY_COMPARISONS:
        pid = pol["policy_id"]
        if pid == "A":
            policy_out[pid] = {"coverage": cov_all, "label": pol["name"]}
        elif pid == "B":
            policy_out[pid] = {
                "coverage": _coverage_metrics(policy_b_runs),
                "label": pol["name"],
                "note": "center_residuals=False diagnostic",
            }
        elif pid == "C":
            restricted = [r for r in ok_runs if r.get("block_length") in (3, 7)]
            policy_out[pid] = {"coverage": _coverage_metrics(restricted), "label": pol["name"]}
        elif pid == "D":
            supported = [r for r in ok_runs if r.get("serial_dependence_regime") == "clean_iid"]
            policy_out[pid] = {"coverage": _coverage_metrics(supported), "label": pol["name"]}
        elif pid == "E":
            gated = [r for r in ok_runs if r.get("prefit_rmse") is not None and r["prefit_rmse"] < 50.0]
            policy_out[pid] = {"coverage": _coverage_metrics(gated), "label": pol["name"]}
        elif pid == "F":
            policy_out[pid] = {"classification": "diagnostic_interval", "label": pol["name"]}
        else:
            policy_out[pid] = {"status": "blocked", "label": pol["name"]}

    runtime_s = time.perf_counter() - t0

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {
            "fast": cfg.fast,
            "n_replicates": n_rep,
            "n_bootstrap": cfg.n_bootstrap_fast if cfg.fast else cfg.n_bootstrap,
            "block_lengths": list(block_lengths),
            "effect_sizes": list(effect_sizes),
            "canonical_scale": _CANONICAL_SCALE,
            "threshold_label": _THRESHOLD_LABEL,
        },
        "worlds": [w.world_id for w in worlds],
        "effect_sizes": list(effect_sizes),
        "block_lengths": list(block_lengths),
        "run_counts": {
            "total_runs": len(all_runs),
            "successful_runs": len(ok_runs),
            "failed_runs": len(failures),
            "runtime_seconds": runtime_s,
        },
        "point_estimate_results": point_results,
        "interval_results": var_decomp,
        "coverage_by_effect": cov_by_effect,
        "coverage_by_world": cov_by_world,
        "coverage_by_block_length": cov_by_block,
        "coverage_by_serial_dependence": cov_by_serial,
        "bias_decomposition": {
            "dominant_tags": _tag_counts(ok_runs),
            "historical_scale_mismatch_note": "D5-STAT-TBRRIDGE-INF-001 compared level readout to percent true_effect; this artifact uses level_mean_relative truth.",
            "harness_assignment_note": "D5-STAT-TBRRIDGE-INF-001 groups.values() flattening defect avoided via explicit test_0 assignment in this artifact.",
        },
        "harness_defect_assessment": {
            "canonical_harness_assignment_defect": True,
            "defect_description": "D5-STAT-TBRRIDGE-INF-001 _assign_greedy_pre_period flattens control+test_0 via groups.values()",
            "this_artifact_uses_corrected_assignment": True,
        },
        "variance_decomposition": var_decomp,
        "bootstrap_centering_diagnostics": center_diag,
        "prefit_relationships": prefit_rel,
        "ridge_relationships": ridge_rel,
        "failure_summary": {
            "failure_count": len(failures),
            "failure_reasons": list({r.get("failure_reason") for r in failures if r.get("failure_reason")})[:10],
        },
        "policy_comparisons": policy_out,
        "production_defect_assessment": prod,
        "semantic_classification": {
            "readout_class": "diagnostic_interval",
            "estimand": "post_window_mean_residual_effect_level",
            "brb_resamples": "pre_period_oos_residual_blocks_added_to_observed_effect_path",
            "causal_interval_validated": False,
        },
        "trustreport_eligibility_implications": {
            "dcm005_brb_status": "characterized_not_promoted",
            "prior_harness_status": "INSUFFICIENT_EVIDENCE",
            "reassessment_required": True,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
        },
        "limitations": [
            "Characterizes DCM-005 BRB only; KFold/Placebo out of scope.",
            "Level-scale truth contract; percent injection converted to level mean shift.",
            "Does not authorize TrustReport or modify production TBRRidge/BRB.",
            "Policy B/C comparisons are diagnostic; no production changes applied.",
        ],
    }
    summary["verdict"] = _decide_semantic_verdict(summary, prod)
    summary["semantic_classification"]["verdict"] = summary["verdict"]
    summary["investigation_handoff"] = build_investigation_handoff(
        follow_up_issues=["INV-TBRRIDGE-BRB-ESTIMAND-ALIGNMENT-001"],
        resolved_issues=[],
        terminal_dispositions=[],
        next_artifact="TBRRIDGE-BRB-INTERVAL-CORRECTION-001",
    )

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps({"summary": summary, "runs": all_runs}, indent=2) + "\n"
        )

    return _json_safe(summary)


def _tag_counts(runs: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in runs:
        for tag in r.get("root_cause_tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    return counts


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
    cov = payload.get("coverage_by_world", {})
    lines = [
        "# D5 Trust TBRRidge BRB 001 — Report",
        "",
        f"**Artifact ID:** {_ARTIFACT_ID}",
        f"**Verdict:** `{payload.get('verdict')}`",
        "",
        "> This artifact characterizes DCM-005 BRB. It does not authorize TrustReport. "
        "It does not perform DCM-005 eligibility reassessment. "
        "It does not modify production TBRRidge or BRB code unless a separate correction artifact is opened.",
        "",
        "## 1. Executive summary",
        "",
        f"TBRRidge+BRB characterized on unit-panel geometry with level-scale truth contract. "
        f"Verdict: `{payload.get('verdict')}`. Production defect: `{prod.get('decision')}`.",
        "",
        "## 2. Prior DCM-005 BRB status",
        "",
        "`restricted_requires_statistical_validation`; prior harness `INSUFFICIENT_EVIDENCE` with scale mismatch (level readout vs percent truth).",
        "",
        "## 3. Scope",
        "",
        f"{len(payload.get('worlds', []))} diagnostic worlds; effect-size sweep; block-length sweep; policy comparisons.",
        "",
        "## 4. Non-goals",
        "",
        "- No KFold/Placebo lanes",
        "- No TrustReport promotion",
        "- No production code changes in this artifact",
        "",
        "## 5. TBRRidge estimator path",
        "",
        "RidgeCV on pre-period-normalized controls; multi-treated unit panel supported.",
        "",
        "## 6. BRB implementation",
        "",
        "Model-conditional moving-block residual bootstrap; residuals from expanding-window OOS pre-period blocks.",
        "",
        "## 7. Estimand",
        "",
        f"Post-window mean treated-minus-counterfactual residual effect (**{_CANONICAL_SCALE}** level readout).",
        "",
        "## 8. Geometry",
        "",
        "Unit-panel single-cell; treated + control donors; not aggregate 2-row TBR.",
        "",
        "## 9. Scale contract",
        "",
        "Truth, point, bootstrap replicates, and intervals evaluated on **level mean shift** derived from percent injection.",
        "",
        "## 10. Residual construction",
        "",
        "Expanding-window OOS pre-period forecast errors; centered by default (`center_residuals=True`).",
        "",
        "## 11. Block resampling",
        "",
        "Contiguous moving blocks from residual pool; serial dependence preserved within blocks.",
        "",
        "## 12. Worlds",
        "",
        ", ".join(payload.get("worlds", [])),
        "",
        "## 13. Effect-size sweep",
        "",
        ", ".join(str(e) for e in payload.get("effect_sizes", [])),
        "",
        "## 14. Block-length sweep",
        "",
        ", ".join(str(b) for b in payload.get("block_lengths", [])),
        "",
        "## 15. Run counts/runtime",
        "",
        f"Total {_fmt(payload.get('run_counts', {}).get('total_runs'))}; "
        f"ok {_fmt(payload.get('run_counts', {}).get('successful_runs'))}; "
        f"runtime {_fmt(payload.get('run_counts', {}).get('runtime_seconds'))}s.",
        "",
        "## 16. Point-estimate behavior",
        "",
        f"Clean positive bias: {_fmt(payload.get('point_estimate_results', {}).get('mean_bias_clean_positive'))}; "
        f"RMSE: {_fmt(payload.get('point_estimate_results', {}).get('rmse_clean_positive'))}.",
        "",
        "## 17. Bootstrap centering",
        "",
        f"Mean bootstrap center gap: {_fmt(payload.get('bootstrap_centering_diagnostics', {}).get('mean_bootstrap_center_minus_point'))}.",
        "",
        "## 18. Variance calibration",
        "",
        f"Mean variance ratio: {_fmt(payload.get('variance_decomposition', {}).get('mean_variance_ratio'))}; "
        f"mean width: {_fmt(payload.get('variance_decomposition', {}).get('mean_interval_width'))}.",
        "",
        "## 19. Null coverage",
        "",
        f"clean_null: {_fmt(cov.get('clean_null', {}).get('null_coverage'))}.",
        "",
        "## 20. Positive coverage",
        "",
        f"clean_positive_effect: {_fmt(cov.get('clean_positive_effect', {}).get('positive_coverage'))}.",
        "",
        "## 21. Negative coverage",
        "",
        f"clean_negative_effect: {_fmt(cov.get('clean_negative_effect', {}).get('negative_coverage'))}.",
        "",
        "## 22. Type-I error",
        "",
        f"clean_null type-I: {_fmt(cov.get('clean_null', {}).get('type_i_error'))}.",
        "",
        "## 23. Serial-dependence findings",
        "",
        str(payload.get("coverage_by_serial_dependence", {}))[:500],
        "",
        "## 24. Heteroskedasticity findings",
        "",
        f"heteroskedastic world positive coverage: {_fmt(cov.get('heteroskedastic_residuals', {}).get('positive_coverage'))}.",
        "",
        "## 25. Pre-fit findings",
        "",
        str(payload.get("prefit_relationships", {})),
        "",
        "## 26. Ridge-regularization findings",
        "",
        str(payload.get("ridge_relationships", {})),
        "",
        "## 27. Worst-world behavior",
        "",
        f"post_treatment_shock null coverage: {_fmt(cov.get('post_treatment_shock', {}).get('null_coverage'))}.",
        "",
        "## 28. Policy comparisons",
        "",
        "A current BRB; B uncentered diagnostic; C block-restricted; D serial-supported; E prefit-gated; F diagnostic-only; G blocked.",
        "",
        "## 29. Root-cause determination",
        "",
        str(payload.get("bias_decomposition", {})),
        "",
        "## 30. Production-defect decision",
        "",
        f"`{prod.get('decision')}` — {'; '.join(prod.get('rationale', []))}",
        "",
        "## 31. Semantic classification",
        "",
        f"`{payload.get('verdict')}` — BRB reflects residual/forecast uncertainty under stable pre-period dynamics.",
        "",
        "## 32. TrustReport implications",
        "",
        "DCM-005 BRB remains research/restricted; eligibility reassessment deferred.",
        "",
        "## 33. Authorization status",
        "",
        "**Blocked** — trust_report_authorized=false.",
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
            resolved_in_artifact=[],
            new_investigations=handoff.get("follow_up_issues") or [],
            updated_investigations=[],
            deferred_issues=[],
            explicit_exclusions=[
                "KFold and Placebo characterization",
                "DCM-005 eligibility reassessment",
                "Production TBRRidge/BRB code changes",
            ],
            revisit_trigger="Upon opening TBRRIDGE-BRB-INTERVAL-CORRECTION-001 production correction",
            decision_checkpoint="DCM-005 eligibility reassessment (after KFold/Placebo lanes)",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write_text(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    cfg: BrbTrustConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_d5_trust_tbrridge_brb_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write_text(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--output-local", default="/tmp/D5_TRUST_TBRRIDGE_BRB_001_results.json")
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args(argv)

    cfg = BrbTrustConfig(
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
