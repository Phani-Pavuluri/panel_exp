"""D5-STAT-MCELL-PERCELL-001 — Level B per-cell multi-cell execution characterization.

Independent per-cell SCM-JK and AugSynth point only. No pooled causal claims.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.methods.scm import AugSynthCVXPY, SyntheticControlCVXPY
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001e import _assign, _test_cell_keys

_REPO_ROOT = Path(__file__).resolve().parents[2]

OverallVerdict = Literal[
    "characterization_pass_with_caveats",
    "characterization_mixed_requires_followup",
    "characterization_fail_requires_fix",
]

REQUIRED_WORLD_IDS = (
    "two_cell_clean_null",
    "two_cell_mixed_effect",
    "three_cell_heterogeneous_effect",
    "one_bad_cell",
    "post_shock_one_cell",
)

METHOD_COMBINATIONS = (
    "MCELL-PERCELL-SCM-JK",
    "MCELL-AUGSYNTH-POINT",
)

# Per D5-STAT-DID-BOOTSTRAP JSON + METHOD_COMBINATION_VALIDATION_MATRIX queue.
NEXT_RECOMMENDED = ["D5-STAT-TBRRIDGE-INF-001"]

GEOMETRY = "multi_cell_per_cell_only"


@dataclass(frozen=True)
class WorldSpec:
    world_id: str
    n_test_grps: int = 2
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    cell_effects: dict[str, float] = field(default_factory=dict)
    n_geos: int = 16
    n_periods: int = 44
    treatment_probability: float = 0.35
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    shock_cell: str | None = None
    shock_magnitude: float = 0.0
    notes: str = ""


@dataclass(frozen=True)
class D5StatMcellPercell001Config:
    n_replicates: int = 12
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260610
    min_control_units: int = 4


WORLD_SPECS: tuple[WorldSpec, ...] = (
    WorldSpec(
        "two_cell_clean_null",
        n_test_grps=2,
        percent_effect=0.0,
        notes="two independent cells, null",
    ),
    WorldSpec(
        "two_cell_mixed_effect",
        n_test_grps=2,
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        notes="cell_0 lift, cell_1 null",
    ),
    WorldSpec(
        "three_cell_heterogeneous_effect",
        n_test_grps=3,
        cell_effects={"test_0": 0.08, "test_1": 0.04, "test_2": 0.0},
        notes="heterogeneous known effects",
    ),
    WorldSpec(
        "one_bad_cell",
        n_test_grps=2,
        n_geos=12,
        treatment_probability=0.42,
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        notes="one cell stressed pre-fit / weak support",
    ),
    WorldSpec(
        "post_shock_one_cell",
        n_test_grps=2,
        shock_cell="test_1",
        shock_magnitude=18.0,
        percent_effect=0.0,
        notes="idiosyncratic shock in one cell only",
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
        "pooled_causal_claim_allowed": False,
        "pooled_interval_allowed": False,
        "cross_cell_shrinkage_allowed": False,
        "portfolio_effect_allowed": False,
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


def _cell_percent(spec: WorldSpec, cell_id: str) -> float:
    if spec.cell_effects:
        return float(spec.cell_effects.get(cell_id, spec.percent_effect))
    return float(spec.percent_effect)


def _build_wide(spec: WorldSpec, cfg: D5StatMcellPercell001Config, *, seed: int) -> Any:
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
    return SyntheticWorld.generate(scenario).to_panel_dataset().wide_data


def _build_cell_panel(
    wide: Any,
    assignment: dict[str, list[str]],
    cell_id: str,
    cfg: D5StatMcellPercell001Config,
) -> PanelDataset:
    control = list(assignment.get("control") or [])
    treated = list(assignment.get(cell_id) or [])
    end = cfg.train_length + cfg.test_length
    if not treated:
        raise ValueError(f"empty cell {cell_id}")
    other_test = {
        u
        for k, units in assignment.items()
        if k.startswith("test_") and k != cell_id
        for u in units
    }
    if other_test & set(treated):
        raise ValueError("cell_identity_violation_other_test_units_in_treated")
    readout_units = control + treated
    if other_test & set(readout_units):
        raise ValueError("cell_identity_violation_other_test_units_in_panel")
    return PanelDataset(
        wide.loc[readout_units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
    )


def _mean_treated_baseline(panel: PanelDataset) -> np.ndarray:
    return panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)


def _inject_percent_effect(
    panel: PanelDataset,
    percent_effect: float,
    mean_value: np.ndarray,
) -> tuple[PanelDataset, float]:
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
        return mod, delta
    value_effect = percent_effect * mean_value
    mask = np.zeros((n_treated, mod.wide_data.shape[1]), dtype=bool)
    mask[:, start : start + treated_len] = True
    treated_block = mod.wide_data.loc[mod.treated_units].to_numpy(dtype=float)
    treated_block = np.where(mask, treated_block + value_effect.reshape(-1, 1), treated_block)
    mod.wide_data.loc[mod.treated_units] = treated_block
    injected = float(np.mean(value_effect)) if percent_effect != 0.0 else 0.0
    return mod, injected


def _apply_cell_shock(
    panel: PanelDataset,
    *,
    magnitude: float,
    train_length: int,
    test_length: int,
) -> PanelDataset:
    mod = copy.deepcopy(panel)
    start = train_length
    end = train_length + test_length
    times = list(mod.times[start:end])
    mod.wide_data.loc[mod.treated_units, times] += float(magnitude)
    return mod


def _prefit_rmse(results: dict[str, Any], train_length: int) -> float | None:
    y = np.asarray(results.get("y"), dtype=float).reshape(-1)
    y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
    if y.size == 0 or y_hat.size == 0 or train_length <= 0:
        return None
    pre = slice(0, min(train_length, y.size, y_hat.size))
    diff = y[pre] - y_hat[pre]
    if not np.any(np.isfinite(diff)):
        return None
    return float(math.sqrt(np.nanmean(diff**2)))


def _readout_point_and_interval(
    results: dict[str, Any],
    *,
    test_length: int,
    has_interval: bool,
) -> dict[str, Any]:
    sl = slice(-test_length, None)
    y = np.asarray(results.get("y"), dtype=float).reshape(-1)
    y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
    effect = y[sl] - y_hat[sl]
    point_estimate = float(np.nanmean(effect)) if effect.size else float("nan")
    out: dict[str, Any] = {
        "point_estimate": point_estimate,
        "interval_lower": None,
        "interval_upper": None,
        "interval_width": None,
        "interval_contains_truth": None,
        "interval_orientation_valid": None,
        "negative_half_width_detected": None,
    }
    if not has_interval:
        return out
    y_lo = np.asarray(results.get("y_lower"), dtype=float).reshape(-1)
    y_hi = np.asarray(results.get("y_upper"), dtype=float).reshape(-1)
    lo = y_lo[sl]
    hi = y_hi[sl]
    eff_lo = y[sl] - hi
    eff_hi = y[sl] - lo
    interval_lower = float(np.nanmean(eff_lo)) if eff_lo.size else None
    interval_upper = float(np.nanmean(eff_hi)) if eff_hi.size else None
    orient = bool(np.all(lo <= hi)) if lo.size and hi.size else False
    mid = 0.5 * (lo + hi)
    neg_hw = bool(np.any((hi - mid) < 0)) if lo.size else False
    width = None
    if interval_lower is not None and interval_upper is not None:
        width = float(interval_upper - interval_lower)
    out.update(
        {
            "interval_lower": interval_lower,
            "interval_upper": interval_upper,
            "interval_width": width,
            "interval_orientation_valid": orient,
            "negative_half_width_detected": neg_hw,
        }
    )
    return out


def _run_cell_method(
    method_combination: str,
    panel: PanelDataset,
    *,
    percent_effect: float,
    cfg: D5StatMcellPercell001Config,
) -> tuple[dict[str, Any], str, bool]:
    """Return readout dict, estimator class name, cell_identity_ok."""
    mean_value = _mean_treated_baseline(panel)
    pds, injected_level = _inject_percent_effect(panel, percent_effect, mean_value)
    if method_combination == "MCELL-PERCELL-SCM-JK":
        est = SyntheticControlCVXPY(inference="UnitJackKnife", alpha=cfg.alpha)
        has_interval = True
        expected_class = "SyntheticControlCVXPY"
    elif method_combination == "MCELL-AUGSYNTH-POINT":
        est = AugSynthCVXPY(inference=None)
        has_interval = False
        expected_class = "AugSynthCVXPY"
    else:
        raise ValueError(f"unsupported method {method_combination}")

    est.run_analysis(pds)
    identity_ok = est.__class__.__name__ == expected_class
    results = getattr(est, "results", {}) or {}
    readout = _readout_point_and_interval(
        results, test_length=cfg.test_length, has_interval=has_interval
    )
    true_effect = float(injected_level)
    pe = readout["point_estimate"]
    bias = pe - true_effect
    abs_err = abs(bias)
    is_null = abs(true_effect) < 1e-12
    if is_null:
        sign_correct = bool(
            readout.get("interval_contains_truth")
            if readout.get("interval_contains_truth") is not None
            else abs(pe) < 1.0
        )
    else:
        sign_correct = bool(np.isfinite(pe) and np.sign(pe) == np.sign(true_effect))

    if readout["interval_lower"] is not None and readout["interval_upper"] is not None:
        readout["interval_contains_truth"] = bool(
            readout["interval_lower"] <= true_effect <= readout["interval_upper"]
        )

    sl = slice(-cfg.test_length, None)
    y = np.asarray(results.get("y"), dtype=float).reshape(-1)
    y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
    finite = (
        np.isfinite(pe)
        and y.size > 0
        and y_hat.size > 0
        and np.all(np.isfinite(y[sl]))
        and np.all(np.isfinite(y_hat[sl]))
    )
    if has_interval:
        y_lo = np.asarray(results.get("y_lower"), dtype=float).reshape(-1)
        y_hi = np.asarray(results.get("y_upper"), dtype=float).reshape(-1)
        finite = finite and np.all(np.isfinite(y_lo[sl])) and np.all(np.isfinite(y_hi[sl]))

    readout.update(
        {
            "true_effect": true_effect,
            "bias": float(bias),
            "absolute_error": float(abs_err),
            "squared_error": float(bias**2),
            "sign_correct": sign_correct,
            "finite_outputs": bool(finite),
            "prefit_rmse": _prefit_rmse(results, cfg.train_length),
            "donor_count": int(pds.num_control_units),
            "estimator_class": est.__class__.__name__,
        }
    )
    return readout, est.__class__.__name__, identity_ok


def _run_replicate(
    spec: WorldSpec,
    cfg: D5StatMcellPercell001Config,
    *,
    replicate_id: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cell_keys = [f"test_{i}" for i in range(spec.n_test_grps)]
    pooling_flags = {
        "pooled_effect_emitted": False,
        "pooled_interval_emitted": False,
        "silent_pooling_detected": False,
        "cross_cell_shrinkage_detected": False,
    }
    per_cell_rows: list[dict[str, Any]] = []

    try:
        wide = _build_wide(spec, cfg, seed=seed)
        assignment = _assign(
            "greedy_match_markets",
            wide,
            train_length=cfg.train_length,
            seed=seed,
            treatment_probability=spec.treatment_probability,
            n_test_grps=spec.n_test_grps,
            rerandomization_max_iter=200,
        )
        keys = _test_cell_keys(assignment, spec.n_test_grps)
        if keys != cell_keys:
            raise ValueError("unexpected_cell_keys")

        for cell_id in cell_keys:
            panel = _build_cell_panel(wide, assignment, cell_id, cfg)
            if spec.shock_cell == cell_id and spec.shock_magnitude:
                panel = _apply_cell_shock(
                    panel,
                    magnitude=spec.shock_magnitude,
                    train_length=cfg.train_length,
                    test_length=cfg.test_length,
                )
            pct = _cell_percent(spec, cell_id)
            for method in METHOD_COMBINATIONS:
                base = {
                    "world_id": spec.world_id,
                    "cell_id": cell_id,
                    "replicate_id": replicate_id,
                    "seed": seed,
                    "method_combination": method,
                    "cell_identity_preserved": True,
                    "method_identity_preserved": None,
                }
                try:
                    readout, est_class, identity_ok = _run_cell_method(
                        method, panel, percent_effect=pct, cfg=cfg
                    )
                    row = {
                        **base,
                        "callable_status": "callable_pass"
                        if readout["finite_outputs"]
                        else "callable_fail",
                        "method_identity_preserved": identity_ok,
                        "estimator_class": est_class,
                        "exception_type": None,
                        "exception_message": None,
                        **readout,
                    }
                except Exception as exc:
                    row = {
                        **base,
                        "callable_status": "callable_fail",
                        "method_identity_preserved": False,
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
                        "finite_outputs": False,
                        "prefit_rmse": None,
                        "donor_count": None,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc)[:300],
                    }
                per_cell_rows.append(row)

        expected = len(cell_keys) * len(METHOD_COMBINATIONS)
        observed = len(per_cell_rows)
        if observed < expected:
            pooling_flags["silent_pooling_detected"] = True

        return per_cell_rows, pooling_flags
    except Exception as exc:
        for cell_id in cell_keys:
            for method in METHOD_COMBINATIONS:
                per_cell_rows.append(
                    {
                        "world_id": spec.world_id,
                        "cell_id": cell_id,
                        "replicate_id": replicate_id,
                        "seed": seed,
                        "method_combination": method,
                        "callable_status": "callable_fail",
                        "cell_identity_preserved": False,
                        "method_identity_preserved": False,
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
                        "finite_outputs": False,
                        "prefit_rmse": None,
                        "donor_count": None,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc)[:300],
                    }
                )
        pooling_flags["silent_pooling_detected"] = False
        return per_cell_rows, pooling_flags


def _aggregate_world(
    all_rows: list[dict[str, Any]],
    spec: WorldSpec,
    pooling_accum: list[dict[str, Any]],
) -> dict[str, Any]:
    n_cells = spec.n_test_grps
    n_methods = len(METHOD_COMBINATIONS)
    n_reps = len({r["replicate_id"] for r in all_rows})
    expected = n_reps * n_cells * n_methods
    observed = len(all_rows)
    missing_rate = max(0.0, (expected - observed) / max(expected, 1))

    ok = [r for r in all_rows if r.get("callable_status") == "callable_pass"]
    failed = [r for r in all_rows if r.get("callable_status") != "callable_pass"]

    def _by_method(metric: str) -> dict[str, float | None]:
        out: dict[str, float | None] = {}
        for method in METHOD_COMBINATIONS:
            vals = [
                r[metric]
                for r in ok
                if r.get("method_combination") == method
                and r.get(metric) is not None
                and np.isfinite(r[metric])
            ]
            out[method] = float(np.mean(vals)) if vals else None
        return out

    def _rmse_by_method() -> dict[str, float | None]:
        out: dict[str, float | None] = {}
        for method in METHOD_COMBINATIONS:
            biases = [
                r["bias"]
                for r in ok
                if r.get("method_combination") == method
                and r.get("bias") is not None
                and np.isfinite(r["bias"])
            ]
            out[method] = float(math.sqrt(np.mean(np.array(biases) ** 2))) if biases else None
        return out

    def _sign_err_by_method() -> dict[str, float | None]:
        out: dict[str, float | None] = {}
        for method in METHOD_COMBINATIONS:
            rows_m = [r for r in ok if r.get("method_combination") == method]
            if not rows_m:
                out[method] = None
                continue
            out[method] = float(np.mean([not r.get("sign_correct", False) for r in rows_m]))
        return out

    identity_cell = [
        r for r in all_rows if r.get("cell_identity_preserved") is True
    ]
    identity_method = [r for r in all_rows if r.get("method_identity_preserved") is True]

    pooled_effect = any(p.get("pooled_effect_emitted") for p in pooling_accum)
    pooled_interval = any(p.get("pooled_interval_emitted") for p in pooling_accum)
    silent_pool = any(p.get("silent_pooling_detected") for p in pooling_accum)
    shrinkage = any(p.get("cross_cell_shrinkage_detected") for p in pooling_accum)

    non_finite = [r for r in ok if not r.get("finite_outputs")]

    return {
        "world_id": spec.world_id,
        "n_replicates": n_reps,
        "n_cells": n_cells,
        "expected_cell_results": expected,
        "observed_cell_results": observed,
        "missing_cell_result_rate": missing_rate,
        "feasible_cell_runs": len(ok),
        "failed_cell_runs": len(failed),
        "callable_failure_rate": len(failed) / max(observed, 1),
        "non_finite_output_rate": len(non_finite) / max(len(ok), 1),
        "mean_absolute_error_by_method": _by_method("absolute_error"),
        "rmse_by_method": _rmse_by_method(),
        "sign_error_rate_by_method": _sign_err_by_method(),
        "cell_identity_preserved_rate": len(identity_cell) / max(observed, 1),
        "method_identity_preserved_rate": len(identity_method) / max(observed, 1),
        "silent_pooling_detected": silent_pool,
        "pooled_effect_emitted": pooled_effect,
        "pooled_interval_emitted": pooled_interval,
        "cross_cell_shrinkage_detected": shrinkage,
        "metadata_summary_only": True,
        "notes": spec.notes,
    }


def _decide_overall(aggregate: dict[str, dict[str, Any]]) -> OverallVerdict:
    for m in aggregate.values():
        if m.get("pooled_effect_emitted"):
            return "characterization_fail_requires_fix"
        if m.get("pooled_interval_emitted"):
            return "characterization_fail_requires_fix"
        if m.get("cell_identity_preserved_rate", 1.0) < 1.0:
            return "characterization_fail_requires_fix"
        if m.get("method_identity_preserved_rate", 1.0) < 1.0:
            return "characterization_fail_requires_fix"
        if m.get("missing_cell_result_rate", 0) > 0:
            return "characterization_fail_requires_fix"
        if m.get("silent_pooling_detected"):
            return "characterization_fail_requires_fix"

    mixed = False
    if aggregate.get("one_bad_cell", {}).get("callable_failure_rate", 0) > 0.25:
        mixed = True
    if aggregate.get("post_shock_one_cell", {}).get("callable_failure_rate", 0) > 0.2:
        mixed = True
    clean = aggregate.get("two_cell_clean_null", {})
    if clean.get("callable_failure_rate", 0) > 0.15:
        mixed = True

    if mixed:
        return "characterization_mixed_requires_followup"
    return "characterization_pass_with_caveats"


def asdict_world(spec: WorldSpec) -> dict[str, Any]:
    return {
        "world_id": spec.world_id,
        "n_test_grps": spec.n_test_grps,
        "scenario_name": spec.scenario_name,
        "percent_effect": spec.percent_effect,
        "cell_effects": dict(spec.cell_effects),
        "n_geos": spec.n_geos,
        "notes": spec.notes,
    }


def _guardrails_list() -> list[str]:
    return [
        "multi_cell_per_cell_only",
        "no_pooled_causal_claim",
        "no_pooled_interval",
        "no_portfolio_effect",
        "level_b_characterization_only",
    ]


def build_d5_stat_mcell_percell_001(
    cfg: D5StatMcellPercell001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5StatMcellPercell001Config()
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return _json_safe(
            {
                "artifact_id": "D5-STAT-MCELL-PERCELL-001",
                "artifact_type": "level_b_characterization",
                "method_combination": "multi_cell_per_cell_execution",
                "geometry": GEOMETRY,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
                "source_scm_jk_artifact": "D5-STAT-SCM-JK-001",
                "source_augsynth_point_artifact": "D5-STAT-AUGSYNTH-POINT-001",
                "source_tbr_agg_artifact": "D5-STAT-TBR-AGG-001",
                "source_did_bootstrap_artifact": "D5-STAT-DID-BOOTSTRAP-001",
                "overall_verdict": "characterization_fail_requires_fix",
                "summary": {"blocked_reason": skip},
                "worlds": [asdict_world(w) for w in WORLD_SPECS],
                "per_cell_results": [],
                "aggregate_metrics": {},
                "failure_register": [{"reason": skip}],
                "forbidden_flags": _forbidden_flags(),
                "next_recommended_artifacts": NEXT_RECOMMENDED,
                "guardrails": _guardrails_list(),
            }
        )

    per_cell_results: list[dict[str, Any]] = []
    failure_register: list[dict[str, Any]] = []
    aggregate_metrics: dict[str, dict[str, Any]] = {}
    pooling_by_world: dict[str, list[dict[str, Any]]] = {
        w.world_id: [] for w in WORLD_SPECS
    }

    for widx, spec in enumerate(WORLD_SPECS):
        world_rows: list[dict[str, Any]] = []
        for rep in range(cfg.n_replicates):
            seed = cfg.random_state_base + widx * 1000 + rep * 17
            row_bundle, pool_flags = _run_replicate(
                spec, cfg, replicate_id=rep, seed=seed
            )
            world_rows.extend(row_bundle)
            per_cell_results.extend(row_bundle)
            pooling_by_world[spec.world_id].append(pool_flags)
            for r in row_bundle:
                if r.get("callable_status") != "callable_pass":
                    failure_register.append(
                        {
                            "world_id": spec.world_id,
                            "cell_id": r.get("cell_id"),
                            "replicate_id": rep,
                            "method_combination": r.get("method_combination"),
                            "exception_type": r.get("exception_type"),
                            "exception_message": r.get("exception_message"),
                        }
                    )

        aggregate_metrics[spec.world_id] = _aggregate_world(
            world_rows, spec, pooling_by_world[spec.world_id]
        )

    overall = _decide_overall(aggregate_metrics)
    return _json_safe(
        {
            "artifact_id": "D5-STAT-MCELL-PERCELL-001",
            "artifact_type": "level_b_characterization",
            "method_combination": "multi_cell_per_cell_execution",
            "geometry": GEOMETRY,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_smoke_artifact": "D5-STAT-SMOKE-CALLABLE-001",
            "source_scm_jk_artifact": "D5-STAT-SCM-JK-001",
            "source_augsynth_point_artifact": "D5-STAT-AUGSYNTH-POINT-001",
            "source_tbr_agg_artifact": "D5-STAT-TBR-AGG-001",
            "source_did_bootstrap_artifact": "D5-STAT-DID-BOOTSTRAP-001",
            "overall_verdict": overall,
            "summary": {
                "n_worlds": len(WORLD_SPECS),
                "n_replicates_per_world": cfg.n_replicates,
                "method_combinations": list(METHOD_COMBINATIONS),
                "total_per_cell_results": len(per_cell_results),
                "total_failures": len(failure_register),
                "characterization_only": True,
                "metadata_summary_non_causal": True,
            },
            "worlds": [asdict_world(w) for w in WORLD_SPECS],
            "per_cell_results": per_cell_results,
            "aggregate_metrics": aggregate_metrics,
            "failure_register": failure_register,
            "forbidden_flags": _forbidden_flags(),
            "next_recommended_artifacts": NEXT_RECOMMENDED,
            "guardrails": _guardrails_list(),
        }
    )


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5StatMcellPercell001Config | None = None,
) -> Path:
    payload = build_d5_stat_mcell_percell_001(cfg)
    if path is None:
        path = _REPO_ROOT / "docs/track_d/archives/D5_STAT_MCELL_PERCELL_001_results.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    cfg = D5StatMcellPercell001Config()
    out = write_artifact(cfg=cfg)
    p = build_d5_stat_mcell_percell_001(cfg)
    print(
        f"Wrote {out} — {p['overall_verdict']} "
        f"({p['summary'].get('total_per_cell_results', 0)} per-cell results)"
    )


if __name__ == "__main__":
    main()
