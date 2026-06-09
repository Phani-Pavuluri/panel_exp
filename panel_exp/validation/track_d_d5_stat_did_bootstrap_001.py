"""D5-STAT-DID-BOOTSTRAP-001 — Level B characterization for DID + embedded bootstrap.

Single-cell unit-panel geometry with pooled treated units. No promotion or suitability claims.
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
from panel_exp.methods.DID import DID
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

_REPO_ROOT = Path(__file__).resolve().parents[2]

OverallVerdict = Literal[
    "characterization_pass_with_caveats",
    "characterization_mixed_requires_followup",
    "characterization_fail_requires_fix",
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

NEXT_RECOMMENDED = ["D5-STAT-MCELL-PERCELL-001", "D5-STAT-TBRRIDGE-INF-001"]

GEOMETRY = "single_cell_unit_level"


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
    notes: str = ""


@dataclass(frozen=True)
class D5StatDidBootstrap001Config:
    n_replicates: int = 15
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260608
    min_control_units: int = 4


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
        notes="pretrend violation under null",
    ),
    WorldSpec(
        "trend_violation_positive_lift",
        scenario_name="did_parallel_trends_violation",
        percent_effect=0.08,
        allow_pretrend_violation=True,
        notes="pretrend violation with injected lift",
    ),
    WorldSpec(
        "post_shock_null",
        scenario_name="scm_structural_break",
        percent_effect=0.0,
        scenario_overrides={"structural_break_shift": 22.0},
        notes="post-period shock under null",
    ),
)


def _forbidden_flags() -> dict[str, bool]:
    return {
        "promotion_allowed": False,
        "trust_role_allowed": False,
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


def _build_unit_panel(
    spec: WorldSpec,
    cfg: D5StatDidBootstrap001Config,
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
        treatment_start=cfg.train_length,
        true_effect=0.0,
        **(spec.scenario_overrides or {}),
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    treated = _assign_greedy_pre_period(
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


def _post_interval_checks(
    results: dict[str, Any],
    *,
    test_len: int,
) -> tuple[bool, bool, bool]:
    """Return (orientation_valid, negative_half_width, interval_present)."""
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
    base: dict[str, Any] = {
        "world_id": spec.world_id,
        "replicate_id": replicate_id,
        "seed": seed,
        "percent_effect": float(spec.percent_effect),
    }
    try:
        panel = _build_unit_panel(spec, cfg, seed=seed)
        if panel.num_control_units < cfg.min_control_units:
            raise ValueError("insufficient control units after assignment")
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
        interval_width = None
        interval_contains_truth = None
        interval_orientation_valid = None
        negative_half_width_detected = None
        degenerate_interval = False

        if interval_lower is not None and interval_upper is not None:
            interval_width = float(interval_upper - interval_lower)
            interval_orientation_valid = bool(interval_lower <= interval_upper)
            mid = 0.5 * (interval_lower + interval_upper)
            negative_half_width_detected = bool((interval_upper - mid) < 0)
            interval_contains_truth = bool(
                interval_lower <= true_effect <= interval_upper
            )
            degenerate_interval = interval_width <= 1e-12

        plot_orient, plot_neg_hw, plot_interval = _post_interval_checks(
            results, test_len=cfg.test_length
        )
        if plot_interval:
            if not plot_orient:
                interval_orientation_valid = False
            if plot_neg_hw:
                negative_half_width_detected = True

        bias = point_estimate - true_effect
        abs_err = abs(bias)
        is_null = abs(true_effect) < 1e-12
        if is_null:
            sign_correct = bool(
                interval_contains_truth
                if interval_contains_truth is not None
                else abs(point_estimate) < 1.0
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

        return {
            **base,
            "callable_status": "callable_pass" if finite else "callable_fail",
            "point_estimate": point_estimate,
            "true_effect": true_effect,
            "bias": float(bias),
            "absolute_error": float(abs_err),
            "squared_error": float(bias**2),
            "sign_correct": bool(sign_correct),
            "interval_lower": interval_lower,
            "interval_upper": interval_upper,
            "interval_width": interval_width,
            "interval_contains_truth": interval_contains_truth,
            "interval_orientation_valid": interval_orientation_valid,
            "negative_half_width_detected": negative_half_width_detected,
            "degenerate_interval": degenerate_interval,
            "finite_outputs": bool(finite),
            "exception_type": None,
            "exception_message": None,
        }
    except Exception as exc:
        return {
            **base,
            "callable_status": "callable_fail",
            "point_estimate": None,
            "true_effect": None,
            "bias": None,
            "absolute_error": None,
            "squared_error": None,
            "sign_correct": None,
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


def _aggregate_world(runs: list[dict[str, Any]], spec: WorldSpec) -> dict[str, Any]:
    ok = [r for r in runs if r.get("callable_status") == "callable_pass"]
    failed = [r for r in runs if r.get("callable_status") != "callable_pass"]
    n = len(runs)
    is_null = abs(spec.percent_effect) < 1e-12

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
    if is_null and ok:
        rejects = []
        for r in ok:
            lo = r.get("interval_lower")
            hi = r.get("interval_upper")
            if lo is not None and hi is not None:
                rejects.append(not (lo <= 0.0 <= hi))
            elif r.get("point_estimate") is not None:
                rejects.append(abs(r["point_estimate"]) > 1.0)
        null_fpr = float(np.mean(rejects)) if rejects else None

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
        "world_id": spec.world_id,
        "n_replicates": n,
        "feasible_runs": len(ok),
        "failed_runs": len(failed),
        "callable_failure_rate": len(failed) / max(n, 1),
        "mean_point_estimate": float(np.mean(pts)) if pts.size else None,
        "median_point_estimate": float(np.median(pts)) if pts.size else None,
        "mean_true_effect": float(np.mean(_vals("true_effect"))) if ok else None,
        "mean_bias": float(np.mean(biases)) if biases.size else None,
        "mean_absolute_error": float(np.mean(abs_errs)) if abs_errs.size else None,
        "rmse": float(math.sqrt(np.mean(biases**2))) if biases.size else None,
        "median_absolute_error": float(np.median(abs_errs)) if abs_errs.size else None,
        "sign_error_rate": sign_errors,
        "null_false_positive_rate": null_fpr,
        "coverage": coverage,
        "mean_interval_width": float(np.mean(widths)) if widths.size else None,
        "median_interval_width": float(np.median(widths)) if widths.size else None,
        "interval_orientation_failure_rate": len(orient_fail) / max(len(ok), 1),
        "negative_half_width_rate": len(neg_hw) / max(len(ok), 1),
        "degenerate_interval_rate": len(degenerate) / max(len(ok), 1),
        "non_finite_output_rate": len(non_finite) / max(len(ok), 1),
        "notes": spec.notes,
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
        "notes": spec.notes,
    }


def _guardrails_list() -> list[str]:
    return [
        "did_embedded_bootstrap_only",
        "single_cell_unit_level_geometry",
        "level_b_characterization_only",
        "no_governed_uncertainty_claim",
        "no_promotion",
    ]


def build_d5_stat_did_bootstrap_001(
    cfg: D5StatDidBootstrap001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5StatDidBootstrap001Config()
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
                    }
                )
        aggregate_metrics[spec.world_id] = _aggregate_world(world_runs, spec)

    overall = _decide_overall(aggregate_metrics)
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
            "overall_verdict": overall,
            "summary": {
                "n_worlds": len(WORLD_SPECS),
                "n_replicates_per_world": cfg.n_replicates,
                "total_runs": len(run_results),
                "total_failures": len(failure_register),
                "characterization_only": True,
                "pooled_multiple_treated": True,
            },
            "worlds": [asdict_world(w) for w in WORLD_SPECS],
            "aggregate_metrics": aggregate_metrics,
            "run_results": run_results,
            "failure_register": failure_register,
            "forbidden_flags": _forbidden_flags(),
            "next_recommended_artifacts": NEXT_RECOMMENDED,
            "guardrails": _guardrails_list(),
        }
    )


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5StatDidBootstrap001Config | None = None,
) -> Path:
    payload = build_d5_stat_did_bootstrap_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_STAT_DID_BOOTSTRAP_001_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    cfg = D5StatDidBootstrap001Config()
    out = write_artifact(cfg=cfg)
    p = build_d5_stat_did_bootstrap_001(cfg)
    print(
        f"Wrote {out} — {p['overall_verdict']} "
        f"({p['summary'].get('total_runs', 0)} runs)"
    )


if __name__ == "__main__":
    main()
