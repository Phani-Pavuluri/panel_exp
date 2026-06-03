"""D5-INST-TBR-001 — Class TBR aggregate two-series OC (research).

Characterizes normal ``TBR`` (not TBRRidge) on aggregate 1×1 panels only.
SCM+JK / AugSynth are diagnostic context — not estimand equivalence.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.methods.scm import AugSynthCVXPY
from panel_exp.methods.tbr import TBR, TBRRidge
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001b import (
    _inject_percent_effect,
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001c import (
    _aggregated_two_row_panel,
    _post_window_arrays,
    _readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

GeometryMode = Literal["single_cell_agg2", "multi_cell_k2_per_cell_agg2"]
OverallVerdict = Literal[
    "remain_restricted_aggregate_diagnostic",
    "restricted_with_caveats",
    "blocked_low_feasibility",
]

TBR_INFERENCE_MODES: tuple[str | None, ...] = (
    None,
    "UnitJackKnife",
    "JKP",
    "Kfold",
)


@dataclass(frozen=True)
class D5InstTbr001Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260621
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.04, 0.08)
    include_multi_cell_k2: bool = True
    kfold_random_state: int = 0
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    min_feasibility_rate: float = 0.85
    include_augsynth_context: bool = True


def _build_unit_panel(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    cell_key: str,
    train_length: int,
    test_length: int,
) -> PanelDataset:
    control = list(assignment.get("control") or [])
    treated = list(assignment.get(cell_key) or [])
    end = train_length + test_length
    units = control + treated
    return PanelDataset(
        wide.loc[units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(train_length, end - 1) for _ in treated],
    )


def _aggregated_per_cell_panel(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    cell_key: str,
    train_length: int,
    test_length: int,
) -> PanelDataset:
    """Aggregate treated units in one cell vs shared control only (MCELL discipline)."""
    treated_units = list(assignment.get(cell_key) or [])
    control_units = list(assignment.get("control") or [])
    post_end = train_length + test_length - 1
    sub = wide.loc[control_units + treated_units].iloc[:, : post_end + 1]
    treated_series = sub.loc[treated_units].sum(axis=0)
    control_series = sub.loc[control_units].sum(axis=0)
    agg = pd.DataFrame({"treated": treated_series, "control": control_series}).T
    return PanelDataset(
        agg,
        treated_units=["treated"],
        treated_periods=[TimePeriod(train_length, post_end)],
    )


def _expected_injected_delta(panel: PanelDataset, percent_effect: float) -> float:
    mean_value = _mean_treated_baseline(panel)
    return float(percent_effect * np.mean(mean_value))


def _run_class_tbr(
    panel: PanelDataset,
    *,
    inference: str | None,
    percent_effect: float,
    alpha: float,
    test_length: int,
    random_state: int,
    instrument_key: str,
) -> dict[str, Any]:
    mean_value = _mean_treated_baseline(panel)
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    out: dict[str, Any] = {
        "instrument_key": instrument_key,
        "inference": inference or "point_estimate",
        "percent_effect": float(percent_effect),
        "feasible": 0.0,
        "blocked_reason": None,
        "error_type": None,
        "wall_time_s": float("nan"),
        "expected_injected_delta": _expected_injected_delta(panel, percent_effect),
        "estimator_class": "TBR",
    }
    t0 = time.perf_counter()
    try:
        est = TBR(inference=inference, alpha=alpha)
        kwargs: dict[str, Any] = {}
        if inference in ("Kfold", "kfold"):
            kwargs["random_state"] = random_state
        est.run_analysis(pds, **kwargs)
        out["feasible"] = 1.0
        out["fit_success"] = 1.0
    except Exception as exc:
        out["error_type"] = type(exc).__name__
        out["blocked_reason"] = str(exc)[:240]
        out["wall_time_s"] = time.perf_counter() - t0
        return out

    out["wall_time_s"] = time.perf_counter() - t0
    results = est.results or {}
    y, y_hat, y_lo, y_hi = _post_window_arrays(
        {
            **results,
            "y_lower": results.get("y_lower", results.get("y")),
            "y_upper": results.get("y_upper", results.get("y")),
        },
        test_length=test_length,
    )
    effect = y - y_hat
    effect_lo = y - y_hi
    effect_hi = y - y_lo
    point_mean = float(np.mean(effect))
    has_interval = inference not in (None, "point_estimate")
    covers_zero = float(np.nan)
    detected = float(np.nan)
    if has_interval and np.any(np.isfinite(y_lo)) and np.any(np.isfinite(y_hi)):
        covers_zero = float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
        detected = float(not covers_zero)
    injected_sign = float(np.sign(percent_effect)) if abs(percent_effect) > 1e-12 else 0.0
    sign_ok = float(
        injected_sign == 0.0
        or (np.isfinite(point_mean) and np.sign(point_mean) == injected_sign)
    )
    out.update(
        {
            "mean_point_effect": point_mean,
            "covers_zero": covers_zero,
            "detected_interval_excludes_zero": detected,
            "mean_interval_halfwidth": float(np.mean((y_hi - y_lo) / 2.0))
            if has_interval
            else float("nan"),
            "directional_recovery": sign_ok,
            "has_interval": float(has_interval),
        }
    )
    exp = out["expected_injected_delta"]
    if abs(exp) > 1e-12 and np.isfinite(out.get("mean_point_effect", float("nan"))):
        out["point_to_injected_ratio"] = float(out["mean_point_effect"] / exp)
    else:
        out["point_to_injected_ratio"] = float("nan")

    ir = getattr(est, "inference_result", None)
    if ir is not None:
        pit = getattr(ir, "path_interval_type", None)
        out["path_interval_type"] = getattr(pit, "value", pit)

    return out


def _probe_blocked_geometries(unit_panel: PanelDataset, agg_panel: PanelDataset) -> dict[str, Any]:
    probes: dict[str, Any] = {}

    try:
        TBR(inference=None).fit_data(unit_panel)
        probes["unit_panel_class_tbr"] = {"status": "unexpected_success"}
    except AssertionError as exc:
        probes["unit_panel_class_tbr"] = {
            "status": "blocked",
            "reason": str(exc)[:200],
            "geometry": "single_cell_unit_level",
        }

    try:
        TBR(inference="Placebo").run_analysis(agg_panel)
        probes["placebo_on_agg2"] = {"status": "unexpected_success"}
    except Exception as exc:
        probes["placebo_on_agg2"] = {
            "status": "blocked",
            "error_type": type(exc).__name__,
            "reason": str(exc)[:200],
        }

    probes["pooled_multi_cell_agg"] = {
        "status": "blocked",
        "reason": "No governed pooling rule for cross-cell aggregate treated series.",
    }

    return probes


def _run_tbrridge_kfold_context(
    agg_panel: PanelDataset,
    *,
    percent_effect: float,
    alpha: float,
    test_length: int,
    random_state: int,
) -> dict[str, Any]:
    """NOT class TBR — documents TBRRidge vs TBR conflation risk on same agg panel."""
    mean_value = _mean_treated_baseline(agg_panel)
    pds = _inject_percent_effect(agg_panel, percent_effect, mean_value)
    try:
        est = TBRRidge(inference="Kfold", alpha=alpha)
        est.run_analysis(pds, random_state=random_state)
        m = _readout_metrics(est.results, test_length=test_length, percent_effect=percent_effect)
        m["feasible"] = 1.0
        m["estimator_class"] = "TBRRidge"
        m["note"] = "Geo PowerAnalysis path uses TBRRidge — not class TBR"
        return m
    except Exception as exc:
        return {
            "feasible": 0.0,
            "estimator_class": "TBRRidge",
            "error_type": type(exc).__name__,
            "blocked_reason": str(exc)[:200],
        }


def _run_augsynth_point_context(
    unit_panel: PanelDataset,
    *,
    percent_effect: float,
    alpha: float,
    test_length: int,
) -> dict[str, Any]:
    if cvxpy_osqp_skip_reason():
        return {"feasible": 0.0, "blocked_reason": cvxpy_osqp_skip_reason()}
    mean_value = _mean_treated_baseline(unit_panel)
    pds = _inject_percent_effect(unit_panel, percent_effect, mean_value)
    try:
        est = AugSynthCVXPY(inference=None, alpha=alpha, min_donors=5)
        est.run_analysis(pds)
        y, y_hat, _, _ = _post_window_arrays(est.results or {}, test_length=test_length)
        return {
            "feasible": 1.0,
            "mean_point_effect": float(np.mean(y - y_hat)),
            "geometry": "unit_single_cell",
            "note": "context only — not aggregate TBR estimand",
        }
    except Exception as exc:
        return {"feasible": 0.0, "error_type": type(exc).__name__, "blocked_reason": str(exc)[:200]}


def _run_replicate(
    cfg: D5InstTbr001Config,
    *,
    seed: int,
    geometry_mode: GeometryMode,
) -> dict[str, Any]:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.train_length,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    n_test_grps = 2 if geometry_mode == "multi_cell_k2_per_cell_agg2" else 1
    assignment = _assign(
        cfg.reference_design_method,
        wide,
        train_length=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
        n_test_grps=n_test_grps,
        rerandomization_max_iter=500,
    )

    post_end = cfg.train_length + cfg.test_length - 1
    unit_panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.train_length,
        test_length=cfg.test_length,
    )

    if geometry_mode == "single_cell_agg2":
        agg_panel = _aggregated_two_row_panel(
            wide,
            list(assignment.get("test_0") or []),
            train_length=cfg.train_length,
            post_end=post_end,
        )
        cell_runs = [("test_0", agg_panel)]
    else:
        cell_runs = []
        for ck in ("test_0", "test_1"):
            cell_runs.append(
                (
                    ck,
                    _aggregated_per_cell_panel(
                        wide,
                        assignment,
                        cell_key=ck,
                        train_length=cfg.train_length,
                        test_length=cfg.test_length,
                    ),
                )
            )

    blocked = _probe_blocked_geometries(unit_panel, cell_runs[0][1])

    cells_out: list[dict[str, Any]] = []
    for cell_key, agg_panel in cell_runs:
        instruments: dict[str, dict[float, dict[str, Any]]] = {
            "tbr_point": {},
            "tbr_jk": {},
            "tbr_jkp": {},
            "tbr_kfold": {},
        }
        for prc in cfg.effect_grid:
            instruments["tbr_point"][float(prc)] = _run_class_tbr(
                agg_panel,
                inference=None,
                percent_effect=float(prc),
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                random_state=cfg.kfold_random_state,
                instrument_key="class_TBR_point",
            )
            instruments["tbr_jk"][float(prc)] = _run_class_tbr(
                agg_panel,
                inference="UnitJackKnife",
                percent_effect=float(prc),
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                random_state=cfg.kfold_random_state,
                instrument_key="class_TBR_UnitJackKnife",
            )
            instruments["tbr_jkp"][float(prc)] = _run_class_tbr(
                agg_panel,
                inference="JKP",
                percent_effect=float(prc),
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                random_state=cfg.kfold_random_state,
                instrument_key="class_TBR_JKP",
            )
            instruments["tbr_kfold"][float(prc)] = _run_class_tbr(
                agg_panel,
                inference="Kfold",
                percent_effect=float(prc),
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                random_state=cfg.kfold_random_state,
                instrument_key="class_TBR_Kfold",
            )

        cells_out.append(
            {
                "cell_key": cell_key,
                "n_agg_treated_rows": 1,
                "n_agg_control_rows": 1,
                "n_unit_treated": len(assignment.get(cell_key) or []),
                "n_unit_control": len(assignment.get("control") or []),
                "instruments": instruments,
            }
        )

    context: dict[str, Any] = {
        "scm_jk_unit_null": _scm_jk_readout_metrics(
            unit_panel,
            percent_effect=0.0,
            mean_value=_mean_treated_baseline(unit_panel),
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        ),
        "tbrridge_kfold_agg2_null": _run_tbrridge_kfold_context(
            cell_runs[0][1],
            percent_effect=0.0,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=cfg.kfold_random_state,
        ),
    }
    if cfg.include_augsynth_context:
        context["augsynth_point_unit_null"] = _run_augsynth_point_context(
            unit_panel,
            percent_effect=0.0,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
        )

    null_tbr = cells_out[0]["instruments"]["tbr_point"][0.0]
    context["scale_note"] = {
        "tbr_agg_null_point": null_tbr.get("mean_point_effect"),
        "scm_jk_unit_null_point": context["scm_jk_unit_null"].get("mean_point_effect"),
        "not_equivalent_estimand": True,
    }

    return {
        "seed": seed,
        "geometry_mode": geometry_mode,
        "n_test_grps": n_test_grps,
        "blocked_geometry_probes": blocked,
        "cells": cells_out,
        "context": context,
    }


def _aggregate_instrument(
    replicates: list[dict[str, Any]],
    instrument_key: str,
    *,
    effect: float,
    geometry_mode: str,
) -> dict[str, Any]:
    feasible: list[float] = []
    points: list[float] = []
    fprs: list[float] = []
    hw: list[float] = []
    ratios: list[float] = []
    errors: dict[str, int] = {}

    for rep in replicates:
        if rep["geometry_mode"] != geometry_mode:
            continue
        for cell in rep["cells"]:
            inst = cell["instruments"].get(instrument_key, {}).get(float(effect), {})
            if inst.get("blocked_reason"):
                key = str(inst.get("error_type") or inst["blocked_reason"])[:60]
                errors[key] = errors.get(key, 0) + 1
            if not inst.get("feasible"):
                continue
            feasible.append(1.0)
            if "mean_point_effect" in inst:
                points.append(float(inst["mean_point_effect"]))
            det = inst.get("detected_interval_excludes_zero")
            if det is not None and np.isfinite(det):
                fprs.append(float(det))
            hwv = inst.get("mean_interval_halfwidth")
            if hwv is not None and np.isfinite(hwv):
                hw.append(float(hwv))
            r = inst.get("point_to_injected_ratio")
            if r is not None and np.isfinite(r):
                ratios.append(float(r))

    return {
        "instrument": instrument_key,
        "geometry_mode": geometry_mode,
        "effect": effect,
        "feasibility_rate": float(np.mean(feasible)) if feasible else 0.0,
        "mean_point_effect": _summarize(points),
        "null_interval_exclusion_fpr": _summarize(fprs),
        "mean_interval_halfwidth": _summarize(hw),
        "point_to_injected_ratio": _summarize(ratios),
        "failure_counts": errors,
    }


def _decide_verdict(
    point_agg: dict[str, Any],
    jk_agg: dict[str, Any],
    jkp_agg: dict[str, Any],
    kfold_agg: dict[str, Any],
    multi_point: dict[str, Any] | None,
    blocked: dict[str, Any],
    *,
    cfg: D5InstTbr001Config,
) -> dict[str, Any]:
    pt_feas = point_agg["feasibility_rate"]
    jk_feas = jk_agg["feasibility_rate"]
    jkp_feas = jkp_agg["feasibility_rate"]
    kf_feas = kfold_agg["feasibility_rate"]

    callable_modes: dict[str, str] = {
        "point_estimate": "callable" if pt_feas >= cfg.min_feasibility_rate else "degraded",
        "Kfold": "callable" if kf_feas >= cfg.min_feasibility_rate else "degraded",
        "UnitJackKnife": "blocked_on_agg2"
        if jk_feas < 0.01
        else ("callable" if jk_feas >= cfg.min_feasibility_rate else "degraded"),
    }
    jkp_fpr = jkp_agg["null_interval_exclusion_fpr"]["mean"]
    if jkp_feas >= cfg.min_feasibility_rate and np.isfinite(jkp_fpr) and jkp_fpr >= 0.9:
        callable_modes["JKP"] = "callable_unverified_interval_semantics"
    elif jkp_feas >= cfg.min_feasibility_rate:
        callable_modes["JKP"] = "callable"
    else:
        callable_modes["JKP"] = "degraded"

    if pt_feas < cfg.min_feasibility_rate:
        overall: OverallVerdict = "blocked_low_feasibility"
        rationale = f"Class TBR point feasibility {pt_feas:.2f} below threshold."
    else:
        kf_fpr = kfold_agg["null_interval_exclusion_fpr"]["mean"]
        if np.isfinite(kf_fpr) and kf_fpr > cfg.null_fpr_concerning_max:
            overall = "restricted_with_caveats"
            rationale = "Elevated Kfold null FPR on aggregate battery."
        else:
            overall = "remain_restricted_aggregate_diagnostic"
            rationale = (
                "Class TBR point/Kfold feasible on aggregate 1×1. "
                "JKP runs but null interval semantics unverified (100% exclude-zero at null). "
                "UnitJackKnife blocked (1 control row). Not geo.relative_att_post; not MMM-eligible."
            )

    return {
        "overall_verdict": overall,
        "rationale": rationale,
        "callable_inference_modes": callable_modes,
        "blocked_geometries": {
            "unit_panel_multi_control": blocked.get("unit_panel_class_tbr", {}),
            "placebo": blocked.get("placebo_on_agg2", {}),
            "pooled_multi_cell": blocked.get("pooled_multi_cell_agg", {}),
        },
        "calibration_signal_ingress": False,
        "mmm_ingress": False,
        "geo_relative_att_post_claim": False,
        "tbrridge_conflation_risk": "Geo PowerAnalysis uses TBRRidge on agg2 — not class TBR",
        "audit_010_prerequisites_met": False,
        "audit_010_remaining": [
            "F-P0-002 recovery_runner TBR factory label",
            "F-P0-001 full_model SCM/AugSynth export guard",
            "Track B alias for class TBR aggregate readout (if any)",
            "AUDIT-010 MMM readiness/gap execution",
        ],
        "feasibility_single_cell_agg2": {
            "point": pt_feas,
            "jk": jk_feas,
            "jkp": jkp_feas,
            "kfold": kf_feas,
        },
        "feasibility_multi_cell_k2_per_cell_agg2": (
            multi_point["feasibility_rate"] if multi_point else float("nan")
        ),
    }


def build_d5_inst_tbr_001(cfg: D5InstTbr001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstTbr001Config()
    replicates: list[dict[str, Any]] = []
    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + i
        replicates.append(_run_replicate(cfg, seed=seed, geometry_mode="single_cell_agg2"))
        if cfg.include_multi_cell_k2:
            replicates.append(
                _run_replicate(cfg, seed=seed + 50_000, geometry_mode="multi_cell_k2_per_cell_agg2")
            )

    single = [r for r in replicates if r["geometry_mode"] == "single_cell_agg2"]
    multi = [r for r in replicates if r["geometry_mode"] == "multi_cell_k2_per_cell_agg2"]

    keys = ("tbr_point", "tbr_jk", "tbr_jkp", "tbr_kfold")
    null_single = [_aggregate_instrument(single, k, effect=0.0, geometry_mode="single_cell_agg2") for k in keys]
    inj_single = [
        _aggregate_instrument(single, "tbr_point", effect=0.08, geometry_mode="single_cell_agg2"),
        _aggregate_instrument(single, "tbr_kfold", effect=0.08, geometry_mode="single_cell_agg2"),
    ]

    multi_null_point = None
    if cfg.include_multi_cell_k2:
        multi_null_point = _aggregate_instrument(
            multi, "tbr_point", effect=0.0, geometry_mode="multi_cell_k2_per_cell_agg2"
        )

    pt = next(s for s in null_single if s["instrument"] == "tbr_point")
    jk = next(s for s in null_single if s["instrument"] == "tbr_jk")
    jkp = next(s for s in null_single if s["instrument"] == "tbr_jkp")
    kf = next(s for s in null_single if s["instrument"] == "tbr_kfold")
    blocked_sample = single[0]["blocked_geometry_probes"] if single else {}
    status = _decide_verdict(pt, jk, jkp, kf, multi_null_point, blocked_sample, cfg=cfg)

    tbr_vs_ridge = []
    for rep in single:
        ctx = rep["context"]
        tbr_p = rep["cells"][0]["instruments"]["tbr_point"][0.0].get("mean_point_effect", float("nan"))
        ridge_p = ctx.get("tbrridge_kfold_agg2_null", {}).get("mean_point_effect", float("nan"))
        if np.isfinite(tbr_p) and np.isfinite(ridge_p) and abs(ridge_p) > 1e-9:
            tbr_vs_ridge.append(float(tbr_p / ridge_p))

    return {
        "artifact_id": "D5-INST-TBR-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "D5_INST_AUDIT_001",
            "D5_INST_COMBO_AUDIT_001",
            "TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001",
            "AUDIT-010A_roadmap_consistency_pre_mmm_gate",
            "TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001",
        ],
        "governance": {
            "estimator": "TBR",
            "not_tbrridge": True,
            "geometry": "aggregate_two_series_only",
            "no_promotion": True,
            "no_calibration_signal": True,
            "no_mmm": True,
            "no_unit_level_claim": True,
            "no_geo_relative_att_default": True,
        },
        "tbr_call_path": {
            "class": "panel_exp.methods.tbr.TBR",
            "fit_data_asserts": [
                "len(treated_units) == 1",
                "num_control_units == 1",
            ],
            "fit_model": "LinearRegression on pre-period (default full_model=False)",
            "estimand": "aggregate treated vs control level contrast (y - y_hat)",
            "not": ["TBRRidge multi-control unit path", "geo.relative_att_post unit SCM"],
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "reference_design_method": cfg.reference_design_method,
            "effect_grid": list(cfg.effect_grid),
            "include_multi_cell_k2": cfg.include_multi_cell_k2,
        },
        "instrument_summaries_null_single_cell_agg2": null_single,
        "instrument_summaries_injected_8pct_single_cell_agg2": inj_single,
        "instrument_summary_null_multi_cell_k2_agg2": multi_null_point,
        "instrument_status": status,
        "blocked_geometry_probes_sample": blocked_sample,
        "context_comparison": {
            "tbr_vs_tbrridge_kfold_null_point_ratio": _summarize(tbr_vs_ridge),
            "note": "TBRRidge shown for conflation check only.",
        },
        "findings": [
            {
                "id": "D5-TBR-FIND-001",
                "summary": "Class TBR point/JKP/Kfold feasible on aggregate 1×1 panels.",
            },
            {
                "id": "D5-TBR-FIND-002",
                "summary": "UnitJackKnife fails on agg2 (requires >=2 control units for LOO).",
            },
            {
                "id": "D5-TBR-FIND-003",
                "summary": "Unit-panel and placebo paths blocked by asserts / impl.",
            },
            {
                "id": "D5-TBR-FIND-004",
                "summary": "Aggregate point scale differs from unit SCM+JK — not interchangeable.",
            },
            {
                "id": "D5-TBR-FIND-005",
                "summary": "Remain restricted diagnostic; AUDIT-010 still required before MMM.",
            },
            {
                "id": "D5-TBR-FIND-006",
                "summary": "JKP on agg2: 100% null interval-exclusion — not governed; verify semantics before any TrustReport use.",
            },
        ],
        "overall_verdict": status["overall_verdict"],
        "user_facing_warnings": [
            "Class TBR is not TBRRidge and not geo PowerAnalysis default.",
            "Do not claim unit-level or geo.relative_att_post without estimand bridge.",
            "JK on aggregate 1×1 is not callable despite catalog listing.",
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_changes": True,
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InstTbr001Config | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_TBR_001_results.json"
    )
    payload = build_d5_inst_tbr_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
