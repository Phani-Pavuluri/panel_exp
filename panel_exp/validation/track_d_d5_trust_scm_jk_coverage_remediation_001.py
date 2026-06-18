"""D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001 — SCM+UnitJackknife coverage diagnosis.

Separates estimator bias, interval centering, variance calibration, geometry/support,
and semantic mismatch. No TrustReport authorization or promotion.
"""

from __future__ import annotations

import copy
import json
import math
import subprocess
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.design.assign import greedy_match_markets
from panel_exp.inference.unit_jackknife import unit_jk
from panel_exp.methods.scm import SyntheticControlCVXPY
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_VERSION = "1.0.0"
_THRESHOLD_LABEL = "provisional_for_remediation_characterization_only"

SemanticVerdict = Literal[
    "scm_jk_causal_interval_remediated_requires_reassessment",
    "scm_jk_eligible_as_null_monitor_only",
    "scm_jk_diagnostic_only_not_interval_eligible",
    "scm_jk_support_gated_restricted",
    "scm_jk_remediation_inconclusive",
    "scm_jk_remediation_failed",
]


@dataclass(frozen=True)
class DiagnosticWorldSpec:
    world_id: str
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    treatment_probability: float = 0.35
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    donor_regime: str = "moderate"
    notes: str = ""


@dataclass(frozen=True)
class RemediationConfig:
    n_replicates: int = 6
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260617
    min_control_units: int = 4
    fast: bool = False
    effect_sizes: tuple[float, ...] = (0.0, 0.03, 0.08, 0.12, -0.05)
    write_full_results_path: str | None = "/tmp/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_results.json"


DIAGNOSTIC_WORLDS: tuple[DiagnosticWorldSpec, ...] = (
    DiagnosticWorldSpec("clean_balanced", percent_effect=0.08, donor_regime="strong", notes="clean balanced SCM"),
    DiagnosticWorldSpec("weak_donor_pool", percent_effect=0.08, n_geos=14, treatment_probability=0.42, donor_regime="weak", notes="weak donor pool"),
    DiagnosticWorldSpec("poor_prefit", scenario_name="scm_trend_mismatch", percent_effect=0.08, donor_regime="moderate", notes="poor pre-fit"),
    DiagnosticWorldSpec("latent_factor_mismatch", scenario_name="scm_high_collinearity", percent_effect=0.08, notes="latent-factor mismatch"),
    DiagnosticWorldSpec("high_heterogeneity", percent_effect=0.08, scenario_overrides={"heterogeneous_effects": True}, notes="effect heterogeneity"),
    DiagnosticWorldSpec("serial_correlation", percent_effect=0.08, scenario_overrides={"autocorrelation": 0.85}, notes="serial correlation"),
    DiagnosticWorldSpec("heteroskedasticity", percent_effect=0.08, scenario_overrides={"noise_scale": 4.5}, notes="heteroskedastic noise"),
    DiagnosticWorldSpec("outlier_donor", scenario_name="scm_low_signal", percent_effect=0.08, scenario_overrides={"outlier_probability": 0.15}, notes="outlier donor"),
    DiagnosticWorldSpec("donor_contamination", scenario_name="scm_donor_contamination", percent_effect=0.08, donor_regime="contaminated", notes="donor contamination"),
    DiagnosticWorldSpec("trend_mismatch", scenario_name="scm_trend_mismatch", percent_effect=0.0, notes="trend mismatch null"),
    DiagnosticWorldSpec("level_shift", scenario_name="scm_structural_break", percent_effect=0.0, scenario_overrides={"structural_break_shift": 18.0}, notes="level shift null"),
    DiagnosticWorldSpec("delayed_effect", percent_effect=0.08, scenario_overrides={"spillover_strength": 0.0}, treatment_start=34, notes="shorter post window"),
    DiagnosticWorldSpec("carryover_effect", percent_effect=0.08, scenario_overrides={"spillover_strength": 0.25}, notes="carryover/spillover"),
    DiagnosticWorldSpec("effect_heterogeneity", percent_effect=0.08, scenario_overrides={"heterogeneous_effects": True}, notes="heterogeneous treatment effects"),
    DiagnosticWorldSpec("small_donor_pool", percent_effect=0.08, n_geos=12, treatment_probability=0.45, donor_regime="small_pool", notes="small donor pool"),
    DiagnosticWorldSpec("unstable_pre_period", percent_effect=0.08, scenario_overrides={"noise_scale": 2.5, "autocorrelation": 0.1}, notes="unstable pre-period"),
    DiagnosticWorldSpec("geographic_correlation", percent_effect=0.08, scenario_overrides={"cross_geo_correlation": 0.9}, notes="high geo correlation"),
    DiagnosticWorldSpec("placebo_null", percent_effect=0.0, notes="placebo null"),
)

DONOR_REGIMES: tuple[dict[str, Any], ...] = (
    {"regime_id": "strong", "n_geos": 16, "treatment_probability": 0.35},
    {"regime_id": "moderate", "n_geos": 14, "treatment_probability": 0.38},
    {"regime_id": "weak", "n_geos": 12, "treatment_probability": 0.45},
    {"regime_id": "contaminated", "scenario_name": "scm_donor_contamination", "n_geos": 16},
    {"regime_id": "small_pool", "n_geos": 10, "treatment_probability": 0.48},
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


def _assign_greedy(wide: Any, *, n_pre: int, seed: int, treatment_probability: float) -> list[str]:
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
    if not treated:
        raise ValueError("assignment produced no treated units")
    return treated


def _mean_treated_baseline(panel: PanelDataset) -> np.ndarray:
    return panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)


def _inject_effect(panel: PanelDataset, percent_effect: float, mean_value: np.ndarray) -> tuple[PanelDataset, float]:
    """Return (modified panel, true_effect_level)."""
    mod = copy.deepcopy(panel)
    start = int(mod.treated_start_idxs[0])
    end_idx = min(int(mod.treated_end_idxs[0]), mod.times.shape[0] - 1)
    treated_len = end_idx - start + 1
    n_treated = len(mod.treated_units)
    if n_treated == 1:
        delta = float(percent_effect * np.mean(mean_value))
        mod.wide_data.loc[mod.treated_units, mod.times[start : start + treated_len]] += delta
        return mod, delta
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    block = np.where(mask, block + value_effect.reshape(-1, 1), block)
    mod.wide_data.loc[mod.treated_units] = block
    return mod, float(np.mean(value_effect))


def _build_panel(spec: DiagnosticWorldSpec, cfg: RemediationConfig, *, seed: int) -> PanelDataset:
    base = RECOVERY_SCENARIO_REGISTRY[spec.scenario_name]
    scenario = replace(
        base,
        random_state=seed,
        n_geos=spec.n_geos,
        n_periods=spec.n_periods,
        treatment_start=spec.treatment_start,
        true_effect=0.0,
        **spec.scenario_overrides,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    treated = _assign_greedy(
        wide,
        n_pre=cfg.train_length,
        seed=seed,
        treatment_probability=spec.treatment_probability,
    )
    end = cfg.train_length + cfg.test_length
    return PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
        treated_units=treated,
    )


def _prefit_rmse(results: dict[str, Any], train_length: int) -> float | None:
    y = np.asarray(results.get("y"), dtype=float)
    y_hat = np.asarray(results.get("y_hat"), dtype=float)
    if y.size == 0 or y_hat.size == 0:
        return None
    pre = slice(0, min(train_length, y.size, y_hat.size))
    diff = y[pre] - y_hat[pre]
    if not np.any(np.isfinite(diff)):
        return None
    return float(math.sqrt(np.nanmean(diff**2)))


def _donor_weight_stats(est: SyntheticControlCVXPY) -> dict[str, float | None]:
    w = getattr(est, "weights", None)
    if w is None:
        inner = getattr(getattr(est, "scm", None), "model", None)
        w = getattr(inner, "weights", None) if inner else None
    if w is None:
        return {
            "max_donor_weight": None,
            "effective_donor_count": None,
            "weight_concentration": None,
        }
    arr = np.asarray(w, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr) & (arr > 0)]
    if arr.size == 0:
        return {
            "max_donor_weight": None,
            "effective_donor_count": None,
            "weight_concentration": None,
        }
    arr = arr / arr.sum()
    hhi = float(np.sum(arr**2))
    return {
        "max_donor_weight": float(np.max(arr)),
        "effective_donor_count": float(1.0 / hhi) if hhi > 0 else None,
        "weight_concentration": hhi,
    }


def _loo_effect_estimates(
    pds: PanelDataset,
    cfg: RemediationConfig,
    *,
    test_sl: slice,
) -> list[float]:
    """Leave-one-out donor SCM point effects for empirical spread diagnostic."""
    effects: list[float] = []
    controls = [u for u in pds.units if u not in pds.treated_units]
    for unit in controls:
        try:
            cur = pds.drop_units(unit)
            est = SyntheticControlCVXPY(inference="UnitJackKnife", alpha=cfg.alpha)
            est.run_analysis(cur)
            res = est.results or {}
            y = np.asarray(res.get("y"), dtype=float).reshape(-1)
            y_hat = np.asarray(res.get("y_hat"), dtype=float).reshape(-1)
            eff = y[test_sl] - y_hat[test_sl]
            if eff.size:
                effects.append(float(np.nanmean(eff)))
        except Exception:
            continue
    return effects


def _run_diagnostic_with_retry(
    spec: DiagnosticWorldSpec,
    cfg: RemediationConfig,
    *,
    replicate_id: int,
    seed_base: int,
    percent_effect: float | None = None,
    max_attempts: int = 6,
) -> dict[str, Any]:
    row: dict[str, Any] | None = None
    for attempt in range(max_attempts):
        seed = seed_base + attempt
        candidate = _run_diagnostic(
            spec,
            cfg,
            replicate_id=replicate_id,
            seed=seed,
            percent_effect=percent_effect,
        )
        if candidate.get("callable_status") == "callable_pass":
            return candidate
        row = candidate
    return row if row is not None else {
        "callable_status": "callable_fail",
        "failure_reason": "no_attempts",
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
        "donor_regime": spec.donor_regime,
        "percent_effect": pct,
        "replicate_id": replicate_id,
        "seed": seed,
        **_forbidden(),
    }
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {**base, "callable_status": "skipped_optional_dep", "failure_reason": skip}

    try:
        panel = _build_panel(spec, cfg, seed=seed)
        if panel.num_control_units < cfg.min_control_units:
            raise ValueError("insufficient control units")
        mean_val = _mean_treated_baseline(panel)
        pds, true_level = _inject_effect(panel, pct, mean_val)
        est = SyntheticControlCVXPY(inference="UnitJackKnife", alpha=cfg.alpha)
        est.run_analysis(pds)
        results = est.results or {}
        test_len = cfg.test_length
        sl = slice(-test_len, None)
        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
        y_lo = np.asarray(results.get("y_lower"), dtype=float).reshape(-1)
        y_hi = np.asarray(results.get("y_upper"), dtype=float).reshape(-1)

        effect = y[sl] - y_hat[sl]
        point = float(np.nanmean(effect)) if effect.size else float("nan")
        est_err = point - true_level
        pct_err = point - pct

        jk_hw = None
        interval_lower = interval_upper = interval_width = interval_center = None
        contains_level = contains_percent = contains_zero = None
        oracle_contains_level = None
        empirical_hw = None

        if y_lo.size and y_hi.size:
            lo_cf, hi_cf = y_lo[sl], y_hi[sl]
            eff_lo = float(np.nanmean(y[sl] - hi_cf))
            eff_hi = float(np.nanmean(y[sl] - lo_cf))
            interval_lower, interval_upper = eff_lo, eff_hi
            interval_width = eff_hi - eff_lo
            interval_center = 0.5 * (eff_lo + eff_hi)
            jk_hw = 0.5 * interval_width
            contains_level = bool(eff_lo <= true_level <= eff_hi)
            contains_percent = bool(eff_lo <= pct <= eff_hi)
            contains_zero = bool(eff_lo <= 0.0 <= eff_hi)
            oracle_contains_level = bool(
                (point - jk_hw) <= true_level <= (point + jk_hw)
            )

        loo_effects = _loo_effect_estimates(pds, cfg, test_sl=sl)
        if len(loo_effects) >= 2:
            empirical_hw = float(np.std(loo_effects, ddof=1))

        jk_err = unit_jk(pds, SyntheticControlCVXPY, alpha=cfg.alpha)
        jk_dispersion = float(np.nanmean(np.abs(jk_err[sl]))) if np.size(jk_err) else None

        prefit = _prefit_rmse(results, cfg.train_length)
        weights = _donor_weight_stats(est)

        center_err = (interval_center - point) if interval_center is not None else None
        miscentering = (interval_center - true_level) if interval_center is not None else None
        variance_gap = None
        if empirical_hw is not None and jk_hw is not None and empirical_hw > 0:
            variance_gap = float(jk_hw / empirical_hw)

        return {
            **base,
            "callable_status": "callable_pass",
            "true_effect_level": true_level,
            "true_effect_percent": pct,
            "point_estimate": point,
            "estimation_error_level": float(est_err),
            "estimation_error_percent": float(pct_err),
            "interval_lower": interval_lower,
            "interval_upper": interval_upper,
            "interval_center": interval_center,
            "interval_width": interval_width,
            "interval_center_error": float(center_err) if center_err is not None else None,
            "interval_miscentering_level": float(miscentering) if miscentering is not None else None,
            "contains_truth_level": contains_level,
            "contains_truth_percent": contains_percent,
            "contains_zero": contains_zero,
            "oracle_centered_contains_level": oracle_contains_level,
            "jackknife_half_width": jk_hw,
            "jackknife_dispersion": jk_dispersion,
            "empirical_loo_half_width": empirical_hw,
            "variance_ratio_jk_to_empirical": variance_gap,
            "prefit_rmse": prefit,
            "donor_count": int(pds.num_control_units),
            **weights,
            "loo_replicate_count": len(loo_effects),
            "failure_reason": None,
        }
    except Exception as exc:
        return {
            **base,
            "callable_status": "callable_fail",
            "failure_reason": f"{type(exc).__name__}: {exc}"[:300],
        }


def _coverage(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [r[key] for r in rows if r.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in rows if r.get("callable_status") == "callable_pass"]
    biases = [r["estimation_error_level"] for r in ok if r.get("estimation_error_level") is not None]
    pct_biases = [r["estimation_error_percent"] for r in ok if r.get("estimation_error_percent") is not None]
    widths = [r["interval_width"] for r in ok if r.get("interval_width") is not None]
    pref = [r["prefit_rmse"] for r in ok if r.get("prefit_rmse") is not None]
    vr = [r["variance_ratio_jk_to_empirical"] for r in ok if r.get("variance_ratio_jk_to_empirical") is not None]
    return {
        "n_runs": len(rows),
        "feasible_runs": len(ok),
        "failure_rate": (len(rows) - len(ok)) / len(rows) if rows else None,
        "coverage_level": _coverage(ok, "contains_truth_level"),
        "coverage_percent_scale": _coverage(ok, "contains_truth_percent"),
        "null_rejection_rate": _coverage(ok, "contains_zero") if ok and ok[0].get("percent_effect") == 0 else None,
        "mean_bias_level": float(np.mean(biases)) if biases else None,
        "mean_bias_percent": float(np.mean(pct_biases)) if pct_biases else None,
        "rmse_level": float(math.sqrt(np.mean(np.array(biases) ** 2))) if biases else None,
        "mean_interval_width": float(np.mean(widths)) if widths else None,
        "mean_prefit_rmse": float(np.mean(pref)) if pref else None,
        "mean_variance_ratio_jk_to_empirical": float(np.mean(vr)) if vr else None,
        "oracle_centered_coverage_level": _coverage(ok, "oracle_centered_contains_level"),
    }


def _decide_verdict(summary: dict[str, Any]) -> SemanticVerdict:
    by_effect = summary.get("coverage_by_effect", {})
    null_cov = (by_effect.get("0.0") or {}).get("coverage_level")
    pos_cov_level = (by_effect.get("0.08") or {}).get("coverage_level")
    pos_cov_pct = (by_effect.get("0.08") or {}).get("coverage_percent_scale")
    decomp = summary.get("bias_decomposition", {})
    pct_mismatch = decomp.get("percent_scale_mismatch_dominant", False)

    if summary.get("failure_summary", {}).get("overall_failure_rate", 1.0) > 0.25:
        return "scm_jk_remediation_failed"
    if (
        pct_mismatch
        and pos_cov_pct is not None
        and pos_cov_pct < 0.2
        and pos_cov_level is not None
        and pos_cov_level >= 0.5
    ):
        return "scm_jk_eligible_as_null_monitor_only"
    if null_cov is not None and null_cov >= 0.85 and pos_cov_level is not None and pos_cov_level >= 0.75:
        return "scm_jk_causal_interval_remediated_requires_reassessment"
    if null_cov is not None and null_cov >= 0.80:
        return "scm_jk_eligible_as_null_monitor_only"
    if null_cov is None and pos_cov_level is None:
        return "scm_jk_remediation_inconclusive"
    return "scm_jk_diagnostic_only_not_interval_eligible"


def build_d5_trust_scm_jk_coverage_remediation_001(
    cfg: RemediationConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or RemediationConfig()
    if cfg.fast:
        cfg = replace(cfg, n_replicates=2)
        worlds = DIAGNOSTIC_WORLDS[:6]
        effect_sizes = (0.0, 0.08)
        donor_regimes = DONOR_REGIMES[:3]
    else:
        worlds = DIAGNOSTIC_WORLDS
        effect_sizes = cfg.effect_sizes
        donor_regimes = DONOR_REGIMES

    all_runs: list[dict[str, Any]] = []
    by_world: dict[str, list[dict[str, Any]]] = {}
    by_effect: dict[str, list[dict[str, Any]]] = {}
    by_donor: dict[str, list[dict[str, Any]]] = {}

    for widx, world in enumerate(worlds):
        world_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            seed_base = cfg.random_state_base + widx * 1000 + rep * 17
            row = _run_diagnostic_with_retry(
                world, cfg, replicate_id=rep, seed_base=seed_base
            )
            world_runs.append(row)
            all_runs.append(row)
        by_world[world.world_id] = world_runs

    base_world = DiagnosticWorldSpec("effect_sweep", percent_effect=0.08, donor_regime="strong")
    for eidx, eff in enumerate(effect_sizes):
        eff_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            seed_base = cfg.random_state_base + 50000 + eidx * 1000 + rep * 13
            row = _run_diagnostic_with_retry(
                base_world,
                cfg,
                replicate_id=rep,
                seed_base=seed_base,
                percent_effect=eff,
            )
            eff_runs.append(row)
            all_runs.append(row)
        by_effect[str(eff)] = eff_runs

    for didx, regime in enumerate(donor_regimes):
        spec = DiagnosticWorldSpec(
            f"donor_{regime['regime_id']}",
            scenario_name=regime.get("scenario_name", "scm_low_signal"),
            percent_effect=0.08,
            n_geos=regime.get("n_geos", 16),
            treatment_probability=regime.get("treatment_probability", 0.35),
            donor_regime=regime["regime_id"],
        )
        regime_runs: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            seed_base = cfg.random_state_base + 90000 + didx * 1000 + rep * 11
            row = _run_diagnostic_with_retry(
                spec, cfg, replicate_id=rep, seed_base=seed_base
            )
            regime_runs.append(row)
            all_runs.append(row)
        by_donor[regime["regime_id"]] = regime_runs

    coverage_by_world = {k: _aggregate_rows(v) for k, v in by_world.items()}
    coverage_by_effect = {k: _aggregate_rows(v) for k, v in by_effect.items()}
    coverage_by_donor = {k: _aggregate_rows(v) for k, v in by_donor.items()}

    ok = [r for r in all_runs if r.get("callable_status") == "callable_pass"]
    pos_level = [r for r in ok if (r.get("percent_effect") or 0) > 0]
    pos_pct_cov = _coverage(pos_level, "contains_truth_percent")
    pos_level_cov = _coverage(pos_level, "contains_truth_level")
    null_rows = [r for r in ok if abs(r.get("percent_effect") or 0) < 1e-12]
    null_cov = _coverage(null_rows, "contains_zero")

    bias_decomposition = {
        "mean_bias_level_positive": float(np.mean([r["estimation_error_level"] for r in pos_level])) if pos_level else None,
        "mean_bias_percent_positive": float(np.mean([r["estimation_error_percent"] for r in pos_level])) if pos_level else None,
        "mean_interval_miscentering_level": float(
            np.mean([r["interval_miscentering_level"] for r in pos_level if r.get("interval_miscentering_level") is not None])
        )
        if pos_level
        else None,
        "percent_scale_mismatch_dominant": bool(
            pos_level_cov is not None
            and pos_pct_cov is not None
            and pos_level_cov - pos_pct_cov > 0.5
        ),
        "undercoverage_driver_hypothesis": (
            "semantic_percent_vs_level_mismatch_in_prior_metrics"
            if pos_level_cov and pos_pct_cov and pos_level_cov - pos_pct_cov > 0.5
            else "estimator_bias_and_or_variance_miscalibration"
        ),
    }

    variance_decomposition = {
        "mean_jk_half_width": float(np.mean([r["jackknife_half_width"] for r in ok if r.get("jackknife_half_width")])) if ok else None,
        "mean_empirical_loo_half_width": float(
            np.mean([r["empirical_loo_half_width"] for r in ok if r.get("empirical_loo_half_width")])
        )
        if ok
        else None,
        "mean_variance_ratio": float(
            np.mean([r["variance_ratio_jk_to_empirical"] for r in ok if r.get("variance_ratio_jk_to_empirical")])
        )
        if ok
        else None,
    }

    policy_comparisons = {
        "A_current_unit_jackknife": {
            "null_coverage_level": null_cov,
            "positive_coverage_level": pos_level_cov,
            "positive_coverage_percent_scale": pos_pct_cov,
        },
        "B_null_monitor_only": {
            "recommended_when": "null_coverage acceptable and positive level coverage insufficient",
            "null_coverage_level": null_cov,
        },
        "oracle_centered_diagnostic": {
            "positive_coverage_level": _coverage(pos_level, "oracle_centered_contains_level"),
            "note": "diagnosis_only_not_for_production",
        },
        "empirical_loo_diagnostic": {
            "mean_empirical_hw": variance_decomposition.get("mean_empirical_loo_half_width"),
            "note": "characterization_only",
        },
    }

    failure_summary = {
        "total_runs": len(all_runs),
        "failed_runs": len(all_runs) - len(ok),
        "overall_failure_rate": (len(all_runs) - len(ok)) / len(all_runs) if all_runs else None,
    }

    pre_fit_relationships = {
        "coverage_vs_prefit": [
            {
                "prefit_rmse": r.get("prefit_rmse"),
                "contains_level": r.get("contains_truth_level"),
                "world_id": r.get("world_id"),
            }
            for r in ok[:50]
        ],
    }

    summary: dict[str, Any] = {
        "artifact_id": "D5-TRUST-SCM-JK-COVERAGE-REMEDIATION-001",
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {
            "n_replicates": cfg.n_replicates,
            "fast": cfg.fast,
            "effect_sizes": list(effect_sizes),
            "threshold_label": _THRESHOLD_LABEL,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "alpha": cfg.alpha,
        },
        "worlds": [asdict(w) for w in worlds],
        "effect_sizes": list(effect_sizes),
        "donor_regimes": list(donor_regimes),
        "run_counts": failure_summary,
        "point_estimate_results": {
            "mean_bias_level": bias_decomposition.get("mean_bias_level_positive"),
            "rmse_level": coverage_by_effect.get("0.08", {}).get("rmse_level"),
        },
        "interval_results": variance_decomposition,
        "coverage_by_effect": coverage_by_effect,
        "coverage_by_world": coverage_by_world,
        "coverage_by_donor_regime": coverage_by_donor,
        "bias_decomposition": bias_decomposition,
        "variance_decomposition": variance_decomposition,
        "pre_fit_relationships": pre_fit_relationships,
        "failure_summary": failure_summary,
        "policy_comparisons": policy_comparisons,
        "semantic_classification": {
            "readout_classes_considered": [
                "descriptive_point",
                "null_monitor",
                "causal_interval",
                "per_cell_restricted",
                "diagnostic_only",
            ],
            "supported_without_overreach": ["null_monitor", "diagnostic_only"],
            "not_supported": ["causal_interval"],
        },
        "trustreport_eligibility_implications": {
            "eligible_for_promotion": False,
            "eligible_candidate": False,
            "restricted_classes": ["null_monitor", "diagnostic_only"],
            "requires_reassessment_artifact": "TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001",
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_authorized_count": 0,
        },
        "limitations": [
            "Synthetic worlds only; percent injection uses level delta on treated mean.",
            "Oracle/empirical intervals are diagnostic only.",
            "Does not modify D5-STAT-SCM-JK-001 committed archive.",
            "Production thresholds not defined.",
        ],
    }
    summary["verdict"] = _decide_verdict(summary)

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps({"summary": summary, "run_results": all_runs}, indent=2) + "\n"
        )

    return _json_safe(summary)


def write_summary(path: Path | None = None, *, cfg: RemediationConfig | None = None) -> Path:
    payload = build_d5_trust_scm_jk_coverage_remediation_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_SCM_JK_COVERAGE_REMEDIATION_001_summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


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
    print(f"Wrote {out} — verdict={payload['verdict']}")


if __name__ == "__main__":
    main()
