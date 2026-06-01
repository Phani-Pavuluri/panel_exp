"""D5-POW-001e — Design-method × geometry null FPR under SCM+JK reference readout (research).

Fixed-window unit-level SyntheticControl+UnitJackKnife null-monitor checks across six
confirmed design methods and single-cell / limited multi-cell geometry modes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    Rerandomization,
    StratifiedRandomization,
    ThinningDesign,
    greedy_match_markets,
)
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001b import (
    _inject_percent_effect,
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)

GeometryMode = Literal["single_cell", "multi_cell"]
NullBehaviorVerdict = Literal[
    "acceptable",
    "concerning",
    "blocked",
    "skipped",
    "uncharacterized",
]
Pow001eOverallVerdict = Literal[
    "acceptable_with_caveats",
    "mixed_methods",
    "concerning_null_behavior",
    "insufficient_coverage",
]

CONFIRMED_METHOD_IDS: tuple[str, ...] = (
    "greedy_match_markets",
    "rerandomization_wrapper",
    "completerandomization",
    "balancedrandomization",
    "stratifiedrandomization",
    "thinningdesign",
)

EXCLUDED_FROM_001E: tuple[str, ...] = (
    "supergeos",
    "trimmedmatch",
    "quickblock",
    "matchedpair",
)


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    entrypoint: str
    supports_multi_cell: bool = True


METHOD_SPECS: tuple[MethodSpec, ...] = (
    MethodSpec(
        method_id="greedy_match_markets",
        entrypoint="greedy_match_markets(...).assign(pre_treatment_period=TimePeriod(0, train_length))",
    ),
    MethodSpec(
        method_id="rerandomization_wrapper",
        entrypoint="Rerandomization(base_randomizer_cls=greedy_match_markets, ...).assign(...)",
    ),
    MethodSpec(
        method_id="completerandomization",
        entrypoint="CompleteRandomization(...).assign(...)",
    ),
    MethodSpec(
        method_id="balancedrandomization",
        entrypoint="BalancedRandomization(...).assign(...)",
    ),
    MethodSpec(
        method_id="stratifiedrandomization",
        entrypoint="StratifiedRandomization(...).assign(...)",
    ),
    MethodSpec(
        method_id="thinningdesign",
        entrypoint="ThinningDesign(...).assign(...)",
    ),
)


@dataclass(frozen=True)
class D5Pow001eConfig:
    n_mc: int = 28
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260605
    scenario_name: str = "scm_low_signal"
    min_control_units: int = 2
    n_test_grps_multi: int = 2
    rerandomization_max_iter: int = 500
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    geometry_modes: tuple[GeometryMode, ...] = ("single_cell", "multi_cell")
    readout_instrument: str = "SyntheticControl+UnitJackKnife"


def _n_test_grps_for_mode(geometry_mode: GeometryMode, cfg: D5Pow001eConfig) -> int:
    return 1 if geometry_mode == "single_cell" else cfg.n_test_grps_multi


def _assign(
    method_id: str,
    wide: pd.DataFrame,
    *,
    train_length: int,
    seed: int,
    treatment_probability: float,
    n_test_grps: int,
    rerandomization_max_iter: int,
) -> dict[str, list[str]]:
    panel = PanelDataset(wide.copy())
    pre = TimePeriod(0, train_length)

    if method_id == "greedy_match_markets":
        design = greedy_match_markets(
            func_to_optimize="corr",
            treatment_probability=treatment_probability,
            random_state=seed,
        )
        return design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=n_test_grps,
        )

    if method_id == "rerandomization_wrapper":
        design = Rerandomization(
            treatment_probability=treatment_probability,
            max_iter=rerandomization_max_iter,
            base_randomizer_cls=greedy_match_markets,
            func_to_optimize="corr",
            random_state=seed,
        )
        return design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=n_test_grps,
        )

    if method_id == "completerandomization":
        design = CompleteRandomization(
            treatment_probability=treatment_probability,
            random_state=seed,
        )
        return design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=n_test_grps,
        )

    if method_id == "balancedrandomization":
        design = BalancedRandomization(
            treatment_probability=treatment_probability,
            random_state=seed,
        )
        return design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=n_test_grps,
        )

    if method_id == "stratifiedrandomization":
        design = StratifiedRandomization(
            treatment_probability=treatment_probability,
            random_state=seed,
        )
        return design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=n_test_grps,
        )

    if method_id == "thinningdesign":
        design = ThinningDesign(
            treatment_probability=treatment_probability,
            random_state=seed,
        )
        return design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=n_test_grps,
        )

    raise ValueError(f"unsupported method_id: {method_id}")


def _test_cell_keys(assignment: dict[str, list], n_test_grps: int) -> list[str]:
    return [f"test_{i}" for i in range(n_test_grps)]


def _pre_period_balance(
    wide: pd.DataFrame,
    control: list[str],
    test_units: list[str],
    *,
    train_length: int,
) -> dict[str, float]:
    pre = wide.iloc[:, :train_length]
    if not control or not test_units:
        return {"pre_balance_corr": float("nan"), "pre_balance_mean_rel_diff": float("nan")}
    t_sum = pre.loc[test_units].sum(axis=0).values.astype(float)
    c_sum = pre.loc[control].sum(axis=0).values.astype(float)
    if np.std(t_sum) < 1e-12 or np.std(c_sum) < 1e-12:
        corr = float("nan")
    else:
        corr = float(np.corrcoef(t_sum, c_sum)[0, 1])
    rel_diff = float(np.mean(np.abs(t_sum - c_sum) / (np.abs(c_sum) + 1e-6)))
    return {"pre_balance_corr": corr, "pre_balance_mean_rel_diff": rel_diff}


def _shared_control_adequacy(
    control: list[str],
    test_counts: dict[str, int],
    *,
    min_control_units: int,
    n_test_grps: int,
) -> dict[str, Any]:
    n_control = len(control)
    min_test = min(test_counts.values()) if test_counts else 0
    min_viable = min_control_units * max(1, n_test_grps)
    return {
        "n_control": n_control,
        "min_test_units_per_cell": min_test,
        "min_control_units_required": min_control_units,
        "min_viable_controls_heuristic": min_viable,
        "shared_control_adequate": bool(n_control >= min_control_units),
        "shared_control_stressed": bool(
            n_control >= min_control_units and n_control < min_viable
        ),
    }


def _treatment_cell_conflict(point_drifts: dict[str, float]) -> dict[str, Any]:
    vals = [v for v in point_drifts.values() if np.isfinite(v)]
    if len(vals) < 2:
        return {
            "treatment_cell_conflict": False,
            "max_abs_point_null_drift_spread": float("nan"),
        }
    spread = float(max(vals) - min(vals))
    signs = {int(np.sign(v)) if abs(v) > 1e-6 else 0 for v in vals}
    conflict = len(signs - {0}) > 1 and spread > 1.0
    return {
        "treatment_cell_conflict": conflict,
        "max_abs_point_null_drift_spread": spread,
    }


def _evaluate_cell(
    wide: pd.DataFrame,
    assignment: dict[str, list],
    cell_key: str,
    *,
    cfg: D5Pow001eConfig,
) -> dict[str, Any]:
    control = list(assignment.get("control") or [])
    treated = list(assignment.get(cell_key) or [])
    end = cfg.train_length + cfg.test_length

    row: dict[str, Any] = {
        "cell_id": cell_key,
        "n_treated": len(treated),
        "n_control_donors": len(control),
        "unit_jackknife_feasible": len(control) >= cfg.min_control_units and len(treated) >= 1,
        "skip_reason": None,
    }

    if not row["unit_jackknife_feasible"]:
        row["skip_reason"] = (
            "insufficient_control_units_for_unit_jackknife"
            if len(control) < cfg.min_control_units
            else "empty_test_cell"
        )
        return row

    # Shared-control readout: donors are control arm only (exclude other test cells).
    readout_units = control + treated
    panel = PanelDataset(
        wide.loc[readout_units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
    )
    balance = _pre_period_balance(wide, control, treated, train_length=cfg.train_length)
    row.update(balance)

    try:
        mean_value = _mean_treated_baseline(panel)
        metrics = _scm_jk_readout_metrics(
            panel,
            percent_effect=0.0,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )
    except (ValueError, RuntimeError) as exc:
        row["unit_jackknife_feasible"] = False
        row["skip_reason"] = f"scm_jk_failed:{type(exc).__name__}"
        return row

    row.update(
        {
            "null_interval_exclusion_fpr": metrics["detected_correct"],
            "null_monitor_cell_coverage": metrics["cell_covers_zero_rate"],
            "point_null_drift": metrics["mean_point_effect"],
            "mean_jk_halfwidth": metrics["mean_jk_halfwidth"],
        }
    )
    return row


def _evaluate_method_geometry(
    wide: pd.DataFrame,
    *,
    method_id: str,
    geometry_mode: GeometryMode,
    seed: int,
    cfg: D5Pow001eConfig,
) -> dict[str, Any]:
    spec = next(s for s in METHOD_SPECS if s.method_id == method_id)
    n_test_grps = _n_test_grps_for_mode(geometry_mode, cfg)
    entrypoint = spec.entrypoint

    base_row: dict[str, Any] = {
        "method_id": method_id,
        "entrypoint": entrypoint,
        "geometry_mode": geometry_mode,
        "n_test_grps": n_test_grps,
        "assignment_geometry": "unit_level_markets",
        "pre_period_window": {"start": 0, "end": cfg.train_length - 1},
        "post_period_window": {
            "start": cfg.train_length,
            "end": cfg.train_length + cfg.test_length - 1,
        },
        "pre_treatment_period": {"start": 0, "end_exclusive": cfg.train_length},
        "readout_instrument": cfg.readout_instrument,
        "skip_reason": None,
        "per_cell": [],
    }

    if geometry_mode == "multi_cell" and not spec.supports_multi_cell:
        base_row["skip_reason"] = "multi_cell_not_supported_for_method"
        return base_row

    try:
        assignment = _assign(
            method_id,
            wide,
            train_length=cfg.train_length,
            seed=seed,
            treatment_probability=cfg.treatment_probability,
            n_test_grps=n_test_grps,
            rerandomization_max_iter=cfg.rerandomization_max_iter,
        )
    except (ValueError, RuntimeError) as exc:
        base_row["skip_reason"] = f"assignment_failed:{type(exc).__name__}"
        return base_row

    control = list(assignment.get("control") or [])
    cell_keys = _test_cell_keys(assignment, n_test_grps)
    test_counts = {k: len(assignment.get(k) or []) for k in cell_keys}

    base_row["control_count"] = len(control)
    base_row["test_count_per_cell"] = test_counts
    base_row["shared_control_adequacy"] = _shared_control_adequacy(
        control,
        test_counts,
        min_control_units=cfg.min_control_units,
        n_test_grps=n_test_grps,
    )

    per_cell = [_evaluate_cell(wide, assignment, k, cfg=cfg) for k in cell_keys]
    base_row["per_cell"] = per_cell

    drifts = {
        c["cell_id"]: c.get("point_null_drift", float("nan"))
        for c in per_cell
        if c.get("point_null_drift") is not None
    }
    base_row["treatment_cell_conflict"] = _treatment_cell_conflict(drifts)
    base_row["multiple_comparison_warning"] = bool(
        n_test_grps > 1 and any(c.get("null_interval_exclusion_fpr", 0) > cfg.null_fpr_concerning_max for c in per_cell if c.get("null_interval_exclusion_fpr") is not None)
    )

    feasible_cells = [c for c in per_cell if c.get("unit_jackknife_feasible")]
    if not feasible_cells:
        base_row["skip_reason"] = base_row["skip_reason"] or "no_feasible_cells"
    return base_row


def run_one_replicate(cfg: D5Pow001eConfig, *, seed: int) -> dict[str, Any]:
    from dataclasses import replace

    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.treatment_start,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    if cfg.train_length + cfg.test_length > wide.shape[1]:
        raise ValueError("fixed window exceeds panel length")

    rows: list[dict[str, Any]] = []
    for spec in METHOD_SPECS:
        for geometry_mode in cfg.geometry_modes:
            rows.append(
                _evaluate_method_geometry(
                    wide,
                    method_id=spec.method_id,
                    geometry_mode=geometry_mode,
                    seed=seed,
                    cfg=cfg,
                )
            )
    return {"seed": seed, "method_geometry_rows": rows}


def _summarize(vals: list[float]) -> dict[str, float]:
    arr = np.array([v for v in vals if np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "p95": float("nan"), "n": 0}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "p95": float(np.percentile(arr, 95)),
        "n": int(arr.size),
    }


def _aggregate_method_geometry(
    replicates: list[dict[str, Any]],
    *,
    method_id: str,
    geometry_mode: GeometryMode,
    cfg: D5Pow001eConfig,
) -> dict[str, Any]:
    samples = [
        r
        for rep in replicates
        for r in rep["method_geometry_rows"]
        if r["method_id"] == method_id and r["geometry_mode"] == geometry_mode
    ]
    if not samples:
        return {
            "method_id": method_id,
            "geometry_mode": geometry_mode,
            "null_behavior_verdict": "uncharacterized",
            "rationale": "no samples",
        }

    skipped = [s for s in samples if s.get("skip_reason")]
    valid = [s for s in samples if not s.get("skip_reason")]

    cell_ids = sorted(
        {
            c["cell_id"]
            for s in valid
            for c in s.get("per_cell", [])
        }
    )
    per_cell_agg: dict[str, Any] = {}
    for cell_id in cell_ids:
        fprs = [
            float(c["null_interval_exclusion_fpr"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
            and c.get("null_interval_exclusion_fpr") is not None
            and c.get("unit_jackknife_feasible")
        ]
        coverages = [
            float(c["null_monitor_cell_coverage"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
            and c.get("null_monitor_cell_coverage") is not None
            and c.get("unit_jackknife_feasible")
        ]
        drifts = [
            float(c["point_null_drift"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id
            and c.get("point_null_drift") is not None
            and c.get("unit_jackknife_feasible")
        ]
        balances = [
            float(c["pre_balance_corr"])
            for s in valid
            for c in s.get("per_cell", [])
            if c.get("cell_id") == cell_id and np.isfinite(c.get("pre_balance_corr", float("nan")))
        ]
        per_cell_agg[cell_id] = {
            "null_interval_exclusion_fpr": _summarize(fprs),
            "null_monitor_cell_coverage": _summarize(coverages),
            "point_null_drift": _summarize(drifts),
            "pre_period_balance_corr": _summarize(balances),
        }

    all_fprs = [
        float(c["null_interval_exclusion_fpr"])
        for s in valid
        for c in s.get("per_cell", [])
        if c.get("unit_jackknife_feasible")
        and c.get("null_interval_exclusion_fpr") is not None
    ]
    mean_fpr = _summarize(all_fprs)["mean"]

    shared_ok_rate = float(
        np.mean(
            [
                1.0
                if s.get("shared_control_adequacy", {}).get("shared_control_adequate")
                else 0.0
                for s in valid
            ]
        )
    ) if valid else float("nan")

    conflict_rate = float(
        np.mean(
            [
                1.0
                if s.get("treatment_cell_conflict", {}).get("treatment_cell_conflict")
                else 0.0
                for s in valid
            ]
        )
    ) if valid else float("nan")

    mc_warn_rate = float(
        np.mean([1.0 if s.get("multiple_comparison_warning") else 0.0 for s in valid])
    ) if valid else float("nan")

    verdict, rationale, track_e_flags = _decide_null_behavior(
        mean_null_fpr=mean_fpr,
        n_valid=len(valid),
        n_total=len(samples),
        n_skipped=len(skipped),
        geometry_mode=geometry_mode,
        per_cell_agg=per_cell_agg,
        shared_ok_rate=shared_ok_rate,
        conflict_rate=conflict_rate,
        cfg=cfg,
    )

    fpr_by_cell = {
        k: v["null_interval_exclusion_fpr"]["mean"] for k, v in per_cell_agg.items()
    }
    multi_cell_degradation = _multi_cell_degradation(fpr_by_cell, geometry_mode)

    return {
        "method_id": method_id,
        "geometry_mode": geometry_mode,
        "entrypoint": samples[0].get("entrypoint"),
        "n_replicates": len(samples),
        "n_valid": len(valid),
        "n_skipped": len(skipped),
        "skip_reasons": sorted({s["skip_reason"] for s in skipped if s.get("skip_reason")}),
        "null_interval_exclusion_fpr_pooled_across_cells": None,
        "per_cell_summary": per_cell_agg,
        "shared_control_adequacy_rate": shared_ok_rate,
        "treatment_cell_conflict_rate": conflict_rate,
        "multiple_comparison_warning_rate": mc_warn_rate,
        "multi_cell_degradation": multi_cell_degradation,
        "null_behavior_verdict": verdict,
        "rationale": rationale,
        "track_e_candidate_flags": track_e_flags,
    }


def _multi_cell_degradation(
    fpr_by_cell: dict[str, float],
    geometry_mode: GeometryMode,
) -> dict[str, Any]:
    if geometry_mode != "multi_cell" or len(fpr_by_cell) < 2:
        return {"applies": False}
    vals = [v for v in fpr_by_cell.values() if np.isfinite(v)]
    if len(vals) < 2:
        return {"applies": True, "feasibility_warning": True, "per_cell_fpr_spread": float("nan")}
    spread = float(max(vals) - min(vals))
    return {
        "applies": True,
        "per_cell_fpr_spread": spread,
        "feasibility_warning": spread > 0.2 or max(vals) > 0.35,
        "per_cell_fpr": fpr_by_cell,
    }


def _decide_null_behavior(
    *,
    mean_null_fpr: float,
    n_valid: int,
    n_total: int,
    n_skipped: int,
    geometry_mode: GeometryMode,
    per_cell_agg: dict[str, Any],
    shared_ok_rate: float,
    conflict_rate: float,
    cfg: D5Pow001eConfig,
) -> tuple[NullBehaviorVerdict, str, list[str]]:
    flags: list[str] = []

    if n_valid == 0:
        return "skipped", "All replicates skipped (assignment or SCM+JK infeasible).", ["E-DES-MCELL-002" if geometry_mode == "multi_cell" else "assignment_or_readout_skip"]

    if n_valid < max(3, n_total // 4):
        return (
            "uncharacterized",
            f"Only {n_valid}/{n_total} valid replicates; insufficient for OC summary.",
            ["low_replicate_coverage"],
        )

    if not np.isfinite(mean_null_fpr):
        return "blocked", "No finite null FPR across feasible cells.", ["scm_jk_infeasible"]

    if shared_ok_rate < 0.9:
        flags.append("E-DES-MCELL-004")

    if geometry_mode == "multi_cell":
        flags.append("E-DES-MCELL-007")
        if conflict_rate > 0.1:
            flags.append("E-DES-MCELL-008")
        spreads = [
            per_cell_agg[c]["null_interval_exclusion_fpr"]["mean"]
            for c in per_cell_agg
            if np.isfinite(per_cell_agg[c]["null_interval_exclusion_fpr"]["mean"])
        ]
        if len(spreads) >= 2 and (max(spreads) - min(spreads)) > 0.2:
            flags.append("E-DES-MCELL-003")

    if mean_null_fpr > cfg.null_fpr_concerning_max:
        flags.append("E-DES-WIN-003")
        return (
            "concerning",
            f"Mean per-cell null interval-exclusion FPR {mean_null_fpr:.3f} exceeds "
            f"concerning threshold {cfg.null_fpr_concerning_max}.",
            flags,
        )

    if mean_null_fpr > cfg.null_fpr_acceptable_max:
        flags.append("E-DES-WIN-003")
        return (
            "concerning",
            f"Mean per-cell null FPR {mean_null_fpr:.3f} elevated but below hard concern "
            f"threshold; monitor via Track E null-monitor diagnostics.",
            flags,
        )

    if shared_ok_rate < 1.0 and geometry_mode == "multi_cell":
        return (
            "acceptable",
            "Null FPR acceptable under SCM+JK reference; shared-control adequacy sometimes "
            "stressed in multi-cell geometry.",
            flags + ["E-DES-MCELL-004"],
        )

    return (
        "acceptable",
        f"Mean per-cell null FPR {mean_null_fpr:.3f} within acceptable band for "
        "null-monitor reference readout.",
        flags,
    )


def _greedy_vs_rerandomization(summary: list[dict[str, Any]]) -> dict[str, Any]:
    def _row(mid: str, geo: str) -> dict[str, Any] | None:
        for s in summary:
            if s["method_id"] == mid and s["geometry_mode"] == geo:
                return s
        return None

    out: dict[str, Any] = {}
    for geo in ("single_cell", "multi_cell"):
        g = _row("greedy_match_markets", geo)
        r = _row("rerandomization_wrapper", geo)
        if g and r:
            gf = g["per_cell_summary"].get("test_0", {}).get("null_interval_exclusion_fpr", {})
            rf = r["per_cell_summary"].get("test_0", {}).get("null_interval_exclusion_fpr", {})
            out[geo] = {
                "greedy_mean_null_fpr": gf.get("mean"),
                "rerandomization_mean_null_fpr": rf.get("mean"),
                "delta_rerandomization_minus_greedy": (
                    float(rf.get("mean", float("nan")) - gf.get("mean", float("nan")))
                    if np.isfinite(rf.get("mean", float("nan"))) and np.isfinite(gf.get("mean", float("nan")))
                    else float("nan")
                ),
                "greedy_verdict": g.get("null_behavior_verdict"),
                "rerandomization_verdict": r.get("null_behavior_verdict"),
            }
    return out


def _overall_verdict(summary: list[dict[str, Any]]) -> tuple[Pow001eOverallVerdict, str]:
    single = [s for s in summary if s["geometry_mode"] == "single_cell"]
    verdicts = {s["null_behavior_verdict"] for s in single}
    if not single or all(v == "skipped" for v in verdicts):
        return "insufficient_coverage", "No characterized single-cell design methods."
    if any(v == "concerning" for v in verdicts):
        return (
            "concerning_null_behavior",
            "At least one confirmed design method shows elevated null interval-exclusion "
            "FPR under SCM+JK reference readout.",
        )
    if any(v in {"uncharacterized", "blocked"} for v in verdicts):
        return (
            "mixed_methods",
            "Methods differ in coverage or feasibility; see per-method rows.",
        )
    multi = [s for s in summary if s["geometry_mode"] == "multi_cell"]
    if any(m.get("multi_cell_degradation", {}).get("feasibility_warning") for m in multi):
        return (
            "acceptable_with_caveats",
            "Single-cell null behavior generally acceptable; multi-cell shows per-cell "
            "degradation or feasibility warnings — flow E-DES-MCELL-* to Track E.",
        )
    return (
        "acceptable_with_caveats",
        "Confirmed design methods characterized under SCM+JK null-monitor reference; "
        "not platform power validation.",
    )


def run_d5_pow_001e(config: D5Pow001eConfig | None = None) -> dict[str, Any]:
    cfg = config or D5Pow001eConfig()
    replicates: list[dict[str, Any]] = []
    attempts = 0
    while len(replicates) < cfg.n_mc and attempts < cfg.n_mc * 4:
        seed = cfg.random_state_base + attempts
        attempts += 1
        try:
            replicates.append(run_one_replicate(cfg, seed=seed))
        except ValueError:
            continue
    if not replicates:
        raise RuntimeError("D5-POW-001e: no valid replicates")

    summary: list[dict[str, Any]] = []
    for spec in METHOD_SPECS:
        for geometry_mode in cfg.geometry_modes:
            summary.append(
                _aggregate_method_geometry(
                    replicates,
                    method_id=spec.method_id,
                    geometry_mode=geometry_mode,
                    cfg=cfg,
                )
            )

    overall, overall_rationale = _overall_verdict(summary)
    track_e_flow = sorted(
        {
            f
            for s in summary
            for f in s.get("track_e_candidate_flags", [])
        }
    )
    if any(s.get("geometry_mode") == "multi_cell" for s in summary):
        track_e_flow.extend(
            f for f in ("E-DES-MCELL-001", "E-DES-MCELL-011") if f not in track_e_flow
        )

    return {
        "artifact_id": "D5-POW-001e",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "D5-POW-001e",
        "prior_artifacts": [
            "docs/track_d/archives/D5_POW_001b_results.json",
            "docs/track_d/archives/D5_POW_001c_results.json",
            "docs/track_d/archives/D5_POW_001d_results.json",
            "docs/track_d/archives/DESIGN_INVENTORY_001_results.json",
        ],
        "governance": {
            "readout_branch": "SCM+UnitJackKnife_reference_null_monitor_only",
            "not_platform_power_validation": True,
            "not_mde_promotion": True,
            "not_lift_detection": True,
            "no_pooled_multi_cell_claim": True,
            "excluded_methods": list(EXCLUDED_FROM_001E),
        },
        "config": {
            **asdict(cfg),
            "confirmed_methods": list(CONFIRMED_METHOD_IDS),
        },
        "hypothesis": (
            "Under fixed-window unit-level SCM+JK reference readout, confirmed design "
            "methods and geometry modes differ in null-monitor false-positive rate."
        ),
        "method_geometry_summary": summary,
        "greedy_vs_rerandomization_wrapper": _greedy_vs_rerandomization(summary),
        "overall_verdict": overall,
        "overall_rationale": overall_rationale,
        "track_e_diagnostics_for_e1_e2": track_e_flow,
        "n_replicates": len(replicates),
        "scm_unit_jackknife_governance": "calibration_eligible_null_monitor_only",
        "calibration_eligibility_changed": False,
        "notes": [
            "Fixed pre/post windows (D5-POW-001d); correct effect interval semantics (001b).",
            "Unit-level geometry (001c); per-cell metrics only for multi_cell; no pooling.",
            "Bare greedy_match_markets vs Rerandomization(greedy) compared explicitly.",
            "supergeos, trimmedmatch, quickblock, matchedpair excluded per ROADMAP-DESIGN-READOUT-UPDATE-001.",
            "No production, TrustReport, Track B, or MMM changes.",
        ],
    }


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, float):
        return None if not np.isfinite(obj) else obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    return obj


def write_artifact(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_safe(payload), indent=2) + "\n",
        encoding="utf-8",
    )
    return path
