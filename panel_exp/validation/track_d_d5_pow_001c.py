"""D5-POW-001c — Design-readout geometry: unit panel vs 2-row aggregation (research).

Holds market-selection assignment fixed (greedy pre-period matching) and compares
governed unit-level SCM+UnitJackKnife readout to geo-default 2-row aggregated panel
with TBRRidge+Kfold. Records design method and geometry metadata as first-class inputs.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Sequence

import numpy as np
import pandas as pd

from panel_exp.design.assign import greedy_match_markets
from panel_exp.methods.scm import SyntheticControl
from panel_exp.methods.tbr import TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

AggregationProxyVerdict = Literal[
    "acceptable",
    "optimistic",
    "conservative",
    "invalid",
    "narrow_diagnostics_only",
]

# Tiered design methods for Track E / D5-POW-001e (not exhaustively audited here).
DESIGN_METHODS_FOR_001E: tuple[dict[str, Any], ...] = (
    {
        "design_method_id": "greedy_match_markets",
        "tier": "tier_1_production_geo",
        "balance_objective": "corr",
        "pre_period_assignment": True,
        "in_d5_pow_001c": True,
        "in_d5_pow_001e_recommended": True,
        "notes": "Default geo pre-period matching; baseline for 001c.",
    },
    {
        "design_method_id": "rerandomization",
        "tier": "tier_1_production_geo",
        "balance_objective": "constraint_satisfaction",
        "pre_period_assignment": True,
        "in_d5_pow_001c": False,
        "in_d5_pow_001e_recommended": True,
        "notes": "DES-010 wrapper; scale null FPR in 001e.",
    },
    {
        "design_method_id": "complete_randomization",
        "tier": "tier_2_exposed_not_default",
        "pre_period_assignment": False,
        "in_d5_pow_001c": False,
        "in_d5_pow_001e_recommended": True,
        "notes": "Include if exposed in geo_runner registry.",
    },
    {
        "design_method_id": "stratified_randomization",
        "tier": "tier_2_exposed_not_default",
        "pre_period_assignment": False,
        "in_d5_pow_001c": False,
        "in_d5_pow_001e_recommended": False,
        "notes": "Add to 001e only if active in production path.",
    },
    {
        "design_method_id": "supergeo_construction",
        "tier": "tier_1_production_geo",
        "pre_period_assignment": False,
        "in_d5_pow_001c": False,
        "in_d5_pow_001e_recommended": True,
        "notes": "Aggregation/supermarket geometry; pair with 001c-style agg checks.",
    },
    {
        "design_method_id": "multi_cell_multi_treated",
        "tier": "tier_1_if_active",
        "pre_period_assignment": True,
        "in_d5_pow_001c": False,
        "in_d5_pow_001e_recommended": True,
        "notes": "Multi test-group path when n_test_grps>1 in production.",
    },
    {
        "design_method_id": "trimmed_match_design",
        "tier": "tier_2_adjacent_product",
        "pre_period_assignment": False,
        "in_d5_pow_001c": False,
        "in_d5_pow_001e_recommended": False,
        "notes": "Separate power semantics (classical CI); not geo PowerAnalysis.",
    },
)


@dataclass(frozen=True)
class D5Pow001cConfig:
    n_mc: int = 28
    n_geos: int = 16
    n_periods: int = 44
    treatment_start: int = 32
    test_length: int = 8
    train_length: int = 28
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260603
    scenario_name: str = "scm_low_signal"
    min_control_units: int = 2
    effect_grid: tuple[float, ...] = (
        0.0,
        0.04,
        0.08,
        0.12,
    )


def _design_context(
    cfg: D5Pow001cConfig,
    *,
    treated_units: list[str],
    n_geos: int,
) -> dict[str, Any]:
    end = cfg.train_length + cfg.test_length
    n_control = n_geos - len(treated_units)
    return {
        "design_method_id": "greedy_match_markets",
        "design_method_tier": "tier_1_production_geo",
        "balance_objective": "corr",
        "assignment_constraints": {
            "pre_treatment_period_only": True,
            "n_test_groups": 1,
            "treatment_probability": cfg.treatment_probability,
            "func_to_optimize": "corr",
        },
        "pre_period_window": {"start": 0, "end": cfg.train_length - 1},
        "post_period_window": {"start": cfg.train_length, "end": end - 1},
        "test_length": cfg.test_length,
        "train_length": cfg.train_length,
        "n_geos": n_geos,
        "n_treated_markets": len(treated_units),
        "n_control_markets": n_control,
        "test_control_ratio": float(len(treated_units) / n_control) if n_control else float("nan"),
        "aggregation_geometry": {
            "unit_panel": "market_level_preserving_assignment",
            "power_panel": "sum_treated_sum_control_two_row",
            "markets_preserved_in_power_panel": False,
            "row_count_unit": n_geos,
            "row_count_aggregated": 2,
        },
        "readout_paths": {
            "governed": "unit_panel + SyntheticControl + UnitJackKnife",
            "geo_power_default": "aggregated_two_row + TBRRidge + Kfold",
            "geometry_stress": "aggregated_two_row + SyntheticControl + UnitJackKnife",
        },
    }


def _assign_greedy_pre_period(
    wide: pd.DataFrame,
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
    if len(treated) < 1:
        raise ValueError("assignment produced no treated units")
    return treated


def _aggregated_two_row_panel(
    wide: pd.DataFrame,
    treated_units: list[str],
    *,
    train_length: int,
    post_end: int,
) -> PanelDataset:
    control_units = [u for u in wide.index if u not in treated_units]
    treated_series = wide.loc[treated_units].sum(axis=0)
    control_series = wide.loc[control_units].sum(axis=0)
    agg = pd.DataFrame({"treated": treated_series, "control": control_series}).T
    return PanelDataset(
        agg.iloc[:, : post_end + 1],
        treated_units=["treated"],
        treated_periods=[TimePeriod(train_length, post_end)],
    )


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


def _post_window_arrays(
    results: dict,
    *,
    test_length: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(results["y"], dtype=float)
    y_hat = np.asarray(results["y_hat"], dtype=float)
    y_lo = np.asarray(results["y_lower"], dtype=float)
    y_hi = np.asarray(results["y_upper"], dtype=float)
    sl = slice(-test_length, None)
    return y[sl], y_hat[sl], y_lo[sl], y_hi[sl]


def _readout_metrics(
    results: dict,
    *,
    test_length: int,
    percent_effect: float,
) -> dict[str, float]:
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length=test_length)
    effect = y - y_hat
    effect_lo = y - y_hi
    effect_hi = y - y_lo
    point_mean = float(np.mean(effect))
    covers_zero = float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
    cell_covers = (effect_lo <= 0.0) & (0.0 <= effect_hi)
    injected_sign = float(np.sign(percent_effect)) if abs(percent_effect) > 1e-12 else 0.0
    sign_ok = float(
        injected_sign == 0.0 or (np.isfinite(point_mean) and np.sign(point_mean) == injected_sign)
    )
    jk_hw = (y_hi - y_lo) / 2.0
    return {
        "mean_point_effect": point_mean,
        "covers_zero": covers_zero,
        "detected_interval_excludes_zero": float(not covers_zero),
        "cell_covers_zero_rate": float(np.mean(cell_covers)),
        "cell_detected_rate": float(np.mean(~cell_covers)),
        "mean_jk_or_interval_halfwidth": float(np.mean(jk_hw)),
        "directional_recovery": sign_ok,
    }


def _run_unit_scm_jk(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
) -> dict[str, float]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = SyntheticControl(inference="UnitJackKnife", alpha=alpha)
    est.run_analysis(pds)
    out = _readout_metrics(est.results, test_length=test_length, percent_effect=percent_effect)
    out["path"] = "unit_scm_unit_jk"
    return out


def _run_agg_tbr_kfold(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    seed: int,
) -> dict[str, float]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    est = TBRRidge(inference="Kfold", alpha=alpha)
    est.run_analysis(pds, random_state=seed)
    out = _readout_metrics(est.results, test_length=test_length, percent_effect=percent_effect)
    out["path"] = "agg2_tbr_kfold"
    return out


def _run_agg_scm_jk(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
) -> dict[str, float]:
    """Stress path: SCM+JK on 2-row panel (typically infeasible — one control row)."""
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    try:
        est = SyntheticControl(inference="UnitJackKnife", alpha=alpha)
        est.run_analysis(pds)
        out = _readout_metrics(est.results, test_length=test_length, percent_effect=percent_effect)
        out["jk_feasible"] = 1.0
    except ValueError:
        out = {
            "path": "agg2_scm_unit_jk",
            "jk_feasible": 0.0,
            "mean_point_effect": float("nan"),
            "detected_interval_excludes_zero": float("nan"),
            "directional_recovery": float("nan"),
        }
    out["path"] = "agg2_scm_unit_jk"
    return out


def _geometry_loss(
    wide: pd.DataFrame,
    treated_units: list[str],
    *,
    train_length: int,
    test_length: int,
) -> dict[str, float]:
    end = train_length + test_length
    sl = slice(train_length, end)
    unit_treated_post = wide.loc[treated_units].iloc[:, sl].to_numpy(dtype=float)
    unit_control_post = wide.drop(treated_units).iloc[:, sl].to_numpy(dtype=float)
    agg_treated = unit_treated_post.sum(axis=0)
    agg_control = unit_control_post.sum(axis=0)
    unit_mean_treated = unit_treated_post.mean()
    return {
        "level_ratio_agg_sum_over_unit_mean": float(agg_treated.mean() / unit_mean_treated)
        if unit_mean_treated > 1e-12
        else float("nan"),
        "n_markets_collapsed": float(len(wide.index) - 2),
        "treated_market_count": float(len(treated_units)),
        "control_market_count": float(len(wide.index) - len(treated_units)),
        "agg2_scm_jk_control_units": 1.0,
        "agg2_scm_jk_feasible": 0.0,
    }


def _effect_grid_corr(curve: dict[float, dict[str, float]], field: str) -> float:
    keys = sorted(curve.keys())
    if len(keys) < 2:
        return float("nan")
    inj = np.array(keys, dtype=float)
    pts = np.array([curve[k][field] for k in keys], dtype=float)
    if np.std(inj) < 1e-12 or np.std(pts) < 1e-12:
        return float("nan")
    return float(np.corrcoef(inj, pts)[0, 1])


def run_one_replicate(cfg: D5Pow001cConfig, *, seed: int) -> dict[str, Any]:
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
    treated = _assign_greedy_pre_period(
        wide,
        n_pre=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
    )
    end = cfg.train_length + cfg.test_length
    post_end = end - 1
    unit_panel = PanelDataset(
        wide.iloc[:, :end].copy(),
        treated_periods=[TimePeriod(cfg.train_length, post_end) for _ in treated],
        treated_units=treated,
    )
    agg_panel = _aggregated_two_row_panel(
        wide, treated, train_length=cfg.train_length, post_end=post_end
    )
    mean_value = _mean_treated_baseline(unit_panel)
    agg_mean_scalar = np.array([float(np.sum(mean_value))])

    unit_curve: dict[float, dict] = {}
    agg_tbr_curve: dict[float, dict] = {}
    agg_scm_curve: dict[float, dict] = {}
    for prc in cfg.effect_grid:
        prc_f = float(prc)
        unit_curve[prc_f] = _run_unit_scm_jk(
            unit_panel,
            percent_effect=prc_f,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )
        agg_tbr_curve[prc_f] = _run_agg_tbr_kfold(
            agg_panel,
            percent_effect=prc_f,
            mean_value=agg_mean_scalar,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            seed=seed + int(prc_f * 1000),
        )
        agg_scm_curve[prc_f] = _run_agg_scm_jk(
            agg_panel,
            percent_effect=prc_f,
            mean_value=agg_mean_scalar,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )

    null_u = unit_curve[0.0]
    null_t = agg_tbr_curve[0.0]
    pt_08_u = unit_curve.get(0.08, null_u)
    pt_08_t = agg_tbr_curve.get(0.08, null_t)

    cross_corr = float("nan")
    keys = sorted(cfg.effect_grid)
    if len(keys) >= 2:
        u_pts = [unit_curve[float(k)]["mean_point_effect"] for k in keys]
        t_pts = [agg_tbr_curve[float(k)]["mean_point_effect"] for k in keys]
        if np.std(u_pts) > 1e-12 and np.std(t_pts) > 1e-12:
            cross_corr = float(np.corrcoef(u_pts, t_pts)[0, 1])

    geom = _geometry_loss(
        wide, treated, train_length=cfg.train_length, test_length=cfg.test_length
    )
    agg_jk_feasible = float(agg_scm_curve[0.0].get("jk_feasible", 0.0))

    return {
        "seed": seed,
        "design_context": _design_context(cfg, treated_units=treated, n_geos=cfg.n_geos),
        "geometry_loss": {**geom, "agg2_scm_jk_feasible": agg_jk_feasible},
        "unit_scm_jk": unit_curve,
        "agg2_tbr_kfold": agg_tbr_curve,
        "agg2_scm_unit_jk": agg_scm_curve,
        "null_fpr_unit_scm": null_u["detected_interval_excludes_zero"],
        "null_fpr_agg_tbr": null_t["detected_interval_excludes_zero"],
        "effect_response_8pct_unit": float(pt_08_u["mean_point_effect"] - null_u["mean_point_effect"]),
        "effect_response_8pct_agg_tbr": float(pt_08_t["mean_point_effect"] - null_t["mean_point_effect"]),
        "cross_path_point_corr": cross_corr,
        "unit_grid_corr": _effect_grid_corr(unit_curve, "mean_point_effect"),
        "agg_tbr_grid_corr": _effect_grid_corr(agg_tbr_curve, "mean_point_effect"),
    }


def _summarize(samples: list[float]) -> dict[str, float]:
    arr = np.array([x for x in samples if np.isfinite(x)], dtype=float)
    if arr.size == 0:
        return {"mean": float("nan"), "std": float("nan"), "p95": float("nan")}
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "p95": float(np.percentile(arr, 95)),
    }


def _pool_curves(
    rows: list[dict[str, Any]],
    path_key: str,
    field: str,
) -> dict[str, float]:
    effects = sorted({float(e) for r in rows for e in r[path_key]})
    out: dict[str, float] = {}
    for e in effects:
        vals = [float(r[path_key][e][field]) for r in rows if e in r[path_key]]
        out[str(e)] = float(np.mean(vals)) if vals else float("nan")
    return out


def _decide_aggregation_proxy(
    *,
    null_fpr_unit: float,
    null_fpr_agg: float,
    cross_corr: float,
    response_ratio: float,
    unit_grid_corr: float,
    agg_grid_corr: float,
) -> tuple[AggregationProxyVerdict, str]:
    if not np.isfinite(cross_corr) or cross_corr < 0.3:
        return (
            "invalid",
            "2-row aggregated TBRRidge+Kfold point effects do not track unit-level "
            "SCM+JK injection response on the same assignment; aggregation is not a "
            "valid proxy for governed design-readout behavior. SCM+JK cannot run on the "
            "2-row panel (single control row).",
        )

    fpr_delta = null_fpr_agg - null_fpr_unit
    if fpr_delta > 0.25:
        return (
            "optimistic",
            "Aggregated geo path has higher null interval-exclusion rate than unit SCM+JK "
            "(more false positives / easier 'detection').",
        )
    if fpr_delta < -0.25:
        return (
            "conservative",
            "Aggregated path is less likely to exclude zero at null than unit SCM+JK.",
        )

    if np.isfinite(response_ratio) and (response_ratio > 2.5 or response_ratio < 0.4):
        return (
            "narrow_diagnostics_only",
            "Point-effect magnitudes differ materially between geometries; use aggregated "
            "panels only for coarse diagnostics, not SCM readout feasibility.",
        )

    if cross_corr >= 0.75 and unit_grid_corr > 0.5 and agg_grid_corr > 0.5:
        return (
            "narrow_diagnostics_only",
            "Injection grid correlates on both paths but estimators and row geometry differ; "
            "2-row sum aggregation is not interchangeable with unit-level governed readout.",
        )

    return (
        "invalid",
        "Insufficient alignment between unit-level and aggregated readout on this battery.",
    )


def run_d5_pow_001c(config: D5Pow001cConfig | None = None) -> dict[str, Any]:
    from dataclasses import replace

    cfg = config or D5Pow001cConfig()
    rows: list[dict[str, Any]] = []
    attempts = 0
    while len(rows) < cfg.n_mc and attempts < cfg.n_mc * 3:
        seed = cfg.random_state_base + attempts
        attempts += 1
        try:
            scenario = replace(
                RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
                random_state=seed,
                n_geos=cfg.n_geos,
                n_periods=cfg.n_periods,
                treatment_start=cfg.treatment_start,
            )
            wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
            treated = _assign_greedy_pre_period(
                wide,
                n_pre=cfg.train_length,
                seed=seed,
                treatment_probability=cfg.treatment_probability,
            )
            if len([u for u in wide.index if u not in treated]) < cfg.min_control_units:
                continue
            rows.append(run_one_replicate(cfg, seed=seed))
        except ValueError:
            continue
    if not rows:
        raise RuntimeError("D5-POW-001c: no valid replicates")

    null_unit = [r["null_fpr_unit_scm"] for r in rows]
    null_agg = [r["null_fpr_agg_tbr"] for r in rows]
    cross = [r["cross_path_point_corr"] for r in rows]
    resp_u = [r["effect_response_8pct_unit"] for r in rows]
    resp_t = [r["effect_response_8pct_agg_tbr"] for r in rows]
    resp_ratio = [
        r["effect_response_8pct_agg_tbr"] / r["effect_response_8pct_unit"]
        for r in rows
        if abs(r["effect_response_8pct_unit"]) > 1e-6
    ]

    mean_null_u = _summarize(null_unit)["mean"]
    mean_null_t = _summarize(null_agg)["mean"]
    mean_cross = _summarize(cross)["mean"]
    mean_resp_ratio = _summarize(resp_ratio)["mean"]

    verdict, rationale = _decide_aggregation_proxy(
        null_fpr_unit=mean_null_u,
        null_fpr_agg=mean_null_t,
        cross_corr=mean_cross,
        response_ratio=mean_resp_ratio,
        unit_grid_corr=_summarize([r["unit_grid_corr"] for r in rows])["mean"],
        agg_grid_corr=_summarize([r["agg_tbr_grid_corr"] for r in rows])["mean"],
    )

    return {
        "artifact_id": "D5-POW-001c",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "lane": "research",
        "investigation_id": "D4-FIND-002",
        "prior_artifacts": [
            "docs/track_d/archives/D5_POW_001a_results.json",
            "docs/track_d/archives/D5_POW_001b_results.json",
        ],
        "config": asdict(cfg),
        "design_context_reference": rows[0]["design_context"] if rows else {},
        "design_methods_for_001e": list(DESIGN_METHODS_FOR_001E),
        "hypothesis": (
            "2-row sum aggregation (geo power panel) may distort unit-level "
            "design-readout behavior while preserving market assignment."
        ),
        "primary_metrics": {
            "null_fpr_unit_scm_jk": _summarize(null_unit),
            "null_fpr_agg2_tbr_kfold": _summarize(null_agg),
            "cross_path_point_effect_corr": _summarize(cross),
            "effect_response_8pct_unit_scm": _summarize(resp_u),
            "effect_response_8pct_agg_tbr": _summarize(resp_t),
            "effect_response_ratio_agg_over_unit": _summarize(resp_ratio),
            "geometry_loss_level_ratio": _summarize(
                [r["geometry_loss"]["level_ratio_agg_sum_over_unit_mean"] for r in rows]
            ),
        },
        "pooled_by_effect": {
            "unit_scm_jk_detected": _pool_curves(rows, "unit_scm_jk", "detected_interval_excludes_zero"),
            "agg2_tbr_kfold_detected": _pool_curves(rows, "agg2_tbr_kfold", "detected_interval_excludes_zero"),
            "unit_scm_jk_point": _pool_curves(rows, "unit_scm_jk", "mean_point_effect"),
            "agg2_tbr_kfold_point": _pool_curves(rows, "agg2_tbr_kfold", "mean_point_effect"),
            "agg2_scm_jk_point": _pool_curves(rows, "agg2_scm_unit_jk", "mean_point_effect"),
        },
        "n_replicates": len(rows),
        "aggregation_proxy_verdict": verdict,
        "rationale": rationale,
        "pow_003_status_recommendation": "restricted" if verdict in ("invalid", "optimistic") else "characterization_required",
        "d4_find_002_update": verdict,
        "calibration_eligibility_changed": False,
        "notes": [
            "Assignment fixed: greedy_match_markets on pre-period only (INV-D1-001 aligned).",
            "Governed readout: unit panel + SCM+UnitJackKnife.",
            "Geo power default: 2-row sum + TBRRidge+Kfold.",
            "SCM+UnitJackKnife on 2-row panel is infeasible (requires >=2 control units).",
            "Interval exclusion uses correct effect_lo/hi semantics (post D5-POW-001b).",
            "Do not promote 2-row aggregation to SCM feasibility or MMM planning.",
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
