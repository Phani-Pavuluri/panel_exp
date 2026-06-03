"""D5-INST-AUGSYNTH-ASCM-002 — AugSynth/ASCM vs A26 OC battery (research).

Stratified known-DGP worlds (weak SCM fit, donor-hull stress, sparse/rich pools)
per AUGSYNTH-ASCM-STRENGTHENING-001. No promotion, no CalibrationSignal ingress.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp.methods.scm import AugSynthCVXPY, SyntheticControl
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inst_augsynth_001 import (
    _build_unit_panel,
    _readout_metrics,
)
from panel_exp.validation.track_d_d5_inst_augsynth_kfold_001 import (
    _augsynth_readout_metrics,
)
from panel_exp.validation.track_d_d5_inst_augsynth_003 import (
    _augsynth_conformal_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001b import (
    _inject_percent_effect,
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

OverallVerdict = Literal[
    "remain_diagnostic_comparator",
    "strengthening_partial_weak_fit_gain",
    "strengthening_no_beat_a26",
    "blocked_low_feasibility",
]

INSTRUMENT_ARMS: tuple[str, ...] = (
    "a26_scm_unit_jackknife",
    "augsynth_cvxpy_point",
    "augsynth_cvxpy_unit_jackknife",
    "augsynth_cvxpy_conformal",
    "augsynth_cvxpy_kfold",
)


@dataclass(frozen=True)
class AscmWorldSpec:
    world_id: str
    charter_label: str
    scenario_name: str
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    n_geos: int = 16
    treatment_probability: float = 0.35
    n_test_grps: int = 1
    fit_class: str = "baseline"
    use_scenario_treated_units: bool = False
    effect_grid: tuple[float, ...] = (0.0, 0.08)


WORLD_REGISTRY: tuple[AscmWorldSpec, ...] = (
    AscmWorldSpec(
        "W0_baseline_reference",
        "baseline / reference (001e-style)",
        "scm_low_signal",
        fit_class="baseline",
    ),
    AscmWorldSpec(
        "W1_strong_scm_fit_inside_hull",
        "strong SCM fit / inside donor hull",
        "scm_low_signal",
        scenario_overrides={"cross_geo_correlation": 0.45, "noise_scale": 1.2},
        fit_class="strong_fit",
    ),
    AscmWorldSpec(
        "W2_weak_scm_fit_inside_hull",
        "weak SCM fit / inside hull",
        "scm_trend_mismatch",
        fit_class="weak_fit",
    ),
    AscmWorldSpec(
        "W3_weak_scm_fit_outside_hull",
        "weak SCM fit / outside donor hull (extrapolation stress)",
        "scm_low_signal",
        scenario_overrides={"cross_geo_correlation": 0.05, "noise_scale": 3.2},
        fit_class="weak_fit_outside_hull",
    ),
    AscmWorldSpec(
        "W4_sparse_donor_pool",
        "sparse donor pool",
        "scm_low_signal",
        n_geos=11,
        treatment_probability=0.4,
        fit_class="sparse_donors",
    ),
    AscmWorldSpec(
        "W5_rich_donor_pool",
        "rich donor pool",
        "scm_low_signal",
        n_geos=24,
        scenario_overrides={"cross_geo_correlation": 0.5},
        fit_class="rich_donors",
    ),
    AscmWorldSpec(
        "W6_null_treatment",
        "null treatment effect",
        "scm_low_signal",
        effect_grid=(0.0,),
        fit_class="null_effect",
    ),
    AscmWorldSpec(
        "W7_treatment_effect_present",
        "treatment effect present",
        "scm_low_signal",
        effect_grid=(0.0, 0.08),
        fit_class="effect_present",
    ),
    AscmWorldSpec(
        "W8_post_period_shock",
        "post-period shock",
        "scm_structural_break",
        fit_class="post_shock",
    ),
    AscmWorldSpec(
        "W9_noisy_donor",
        "noisy donor",
        "scm_low_signal",
        scenario_overrides={"noise_scale": 3.5},
        fit_class="noisy_donor",
    ),
    AscmWorldSpec(
        "W10_outlier_market",
        "outlier market",
        "scm_low_signal",
        scenario_overrides={"outlier_probability": 0.07},
        fit_class="outlier_market",
    ),
    AscmWorldSpec(
        "W11_multi_treated_unit_panel",
        "multi-treated unit panel",
        "scm_multi_treated",
        n_geos=20,
        use_scenario_treated_units=True,
        fit_class="multi_treated",
    ),
)


@dataclass(frozen=True)
class D5InstAugsynthAscm002Config:
    n_mc: int = 8
    train_length: int = 28
    test_length: int = 8
    n_periods: int = 44
    alpha: float = 0.05
    random_state_base: int = 20260701
    reference_design_method: str = "greedy_match_markets"
    min_donors_augsynth: int = 5
    kfold_random_state: int = 0
    worlds: tuple[AscmWorldSpec, ...] = WORLD_REGISTRY
    material_point_mismatch_threshold: float = 0.05
    weak_fit_world_ids: tuple[str, ...] = (
        "W2_weak_scm_fit_inside_hull",
        "W3_weak_scm_fit_outside_hull",
    )


def _pre_period_rmse(results: dict[str, Any], train_length: int) -> float:
    y = np.asarray(results["y"], dtype=float)
    y_hat = np.asarray(results["y_hat"], dtype=float)
    if y.ndim == 2:
        y = np.nanmean(y, axis=1)
        y_hat = np.nanmean(y_hat, axis=1)
    pre = slice(0, min(train_length, y.shape[0]))
    err = y[pre] - y_hat[pre]
    if not np.any(np.isfinite(err)):
        return float("nan")
    return float(np.sqrt(np.nanmean(err**2)))


def _hull_extrapolation_z(panel: PanelDataset, train_length: int) -> float:
    if not panel.treated_units or not panel.control_units:
        return float("nan")
    wide = panel.wide_data
    pre_cols = list(panel.times[:train_length])
    treated = panel.treated_units[0]
    yt = wide.loc[treated, pre_cols].values.astype(float)
    X = wide.loc[controls, pre_cols].values.astype(float) if (controls := panel.control_units) else np.empty((0, len(pre_cols)))
    if X.shape[0] == 0:
        return float("nan")
    mu = np.nanmean(X, axis=0)
    sd = np.nanstd(X, axis=0) + 1e-9
    z_t = (yt - mu) / sd
    z_c = (X - mu) / sd
    dists = [float(np.linalg.norm(z_t - z_c[i])) for i in range(X.shape[0])]
    return float(min(dists)) if dists else float("nan")


def _weight_diagnostics(est: AugSynthCVXPY) -> dict[str, float]:
    scm = getattr(est, "scm", None)
    model = getattr(scm, "model", None) if scm is not None else None
    weights = getattr(model, "weights", None)
    if weights is None:
        return {
            "weight_herfindahl": float("nan"),
            "max_weight": float("nan"),
            "n_negative_weights": float("nan"),
        }
    arr = np.asarray(weights, dtype=float).reshape(-1)
    neg = int(np.sum(arr < -1e-9))
    abs_arr = np.abs(arr)
    pos = abs_arr[abs_arr > 1e-12]
    if pos.size == 0:
        return {
            "weight_herfindahl": float("nan"),
            "max_weight": float("nan"),
            "n_negative_weights": float(neg),
        }
    p = pos / pos.sum()
    return {
        "weight_herfindahl": float(np.sum(p**2)),
        "max_weight": float(np.max(p)),
        "n_negative_weights": float(neg),
    }


def _panel_strengthening_diagnostics(
    panel: PanelDataset,
    *,
    train_length: int,
    test_length: int,
    min_donors: int,
    alpha: float,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "scm_pre_rmse": float("nan"),
        "augsynth_pre_rmse": float("nan"),
        "fit_improvement_rmse": float("nan"),
        "donor_sparsity_n_control": float(len(panel.control_units)),
        "hull_min_donor_z_distance": _hull_extrapolation_z(panel, train_length),
        "weight_herfindahl": float("nan"),
        "max_weight": float("nan"),
        "n_negative_weights": float("nan"),
        "diagnostics_feasible": 0.0,
    }
    if len(panel.control_units) < min_donors:
        out["blocked_reason"] = f"insufficient_donors_need_{min_donors}"
        return out
    skip = cvxpy_osqp_skip_reason()
    if skip:
        out["blocked_reason"] = skip
        return out

    pds = _inject_percent_effect(panel, 0.0, _mean_treated_baseline(panel))
    try:
        scm = SyntheticControl(inference=None, alpha=alpha)
        scm.run_analysis(pds)
        out["scm_pre_rmse"] = _pre_period_rmse(scm.results or {}, train_length)
    except Exception as exc:
        out["scm_fit_error"] = type(exc).__name__
        return out

    try:
        aug = AugSynthCVXPY(inference=None, alpha=alpha, min_donors=min_donors)
        aug.run_analysis(pds)
        out["augsynth_pre_rmse"] = _pre_period_rmse(aug.results or {}, train_length)
        out.update(_weight_diagnostics(aug))
        if np.isfinite(out["scm_pre_rmse"]) and np.isfinite(out["augsynth_pre_rmse"]):
            out["fit_improvement_rmse"] = float(out["scm_pre_rmse"] - out["augsynth_pre_rmse"])
        out["diagnostics_feasible"] = 1.0
    except Exception as exc:
        out["augsynth_fit_error"] = type(exc).__name__
    return out


def _recovery_metrics(
    inst: dict[str, Any],
    *,
    percent_effect: float,
) -> dict[str, float]:
    point = float(inst.get("mean_point_effect", float("nan")))
    bias = float("nan")
    mae = float("nan")
    if np.isfinite(point):
        bias = point - percent_effect
        mae = abs(bias)
    return {
        "effect_recovery_bias": bias,
        "effect_recovery_mae": mae,
        "directional_recovery": float(inst.get("directional_recovery", float("nan"))),
    }


def _false_confidence_flag(
    inst: dict[str, Any],
    diagnostics: dict[str, Any],
    *,
    scm_rmse_weak_threshold: float = 1.0,
    hull_stress_threshold: float = 2.5,
) -> float:
    point = abs(float(inst.get("mean_point_effect", 0.0)))
    scm_rmse = float(diagnostics.get("scm_pre_rmse", float("nan")))
    hull_z = float(diagnostics.get("hull_min_donor_z_distance", float("nan")))
    if not np.isfinite(point) or point < 0.03:
        return 0.0
    poor_scm = np.isfinite(scm_rmse) and scm_rmse >= scm_rmse_weak_threshold
    hull_stress = np.isfinite(hull_z) and hull_z >= hull_stress_threshold
    return float(poor_scm and hull_stress and bool(inst.get("feasible")))


def _run_instrument_arm(
    panel: PanelDataset,
    arm: str,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    cfg: D5InstAugsynthAscm002Config,
) -> dict[str, Any]:
    tl = cfg.test_length
    md = cfg.min_donors_augsynth
    if arm == "a26_scm_unit_jackknife":
        raw = _scm_jk_readout_metrics(
            panel,
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=tl,
        )
        raw["feasible"] = 1.0
        raw["instrument_id"] = "A26_SCM_UnitJackKnife"
        raw["detected_interval_excludes_zero"] = raw.get("detected_correct")
        raw["mean_interval_halfwidth"] = raw.get("mean_jk_halfwidth")
        return raw
    if arm == "augsynth_cvxpy_point":
        return _readout_metrics(
            panel,
            estimator_cls=AugSynthCVXPY,
            inference=None,
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=tl,
            min_donors=md,
            instrument_id="AugSynthCVXPY_Point",
        )
    if arm == "augsynth_cvxpy_unit_jackknife":
        return _readout_metrics(
            panel,
            estimator_cls=AugSynthCVXPY,
            inference="UnitJackKnife",
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=tl,
            min_donors=md,
            instrument_id="AugSynthCVXPY_UnitJackKnife",
        )
    if arm == "augsynth_cvxpy_conformal":
        return _augsynth_conformal_readout_metrics(
            panel,
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=tl,
            min_donors=md,
        )
    if arm == "augsynth_cvxpy_kfold":
        return _augsynth_readout_metrics(
            panel,
            inference="Kfold",
            percent_effect=percent_effect,
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=tl,
            min_donors=md,
            instrument_id="AugSynthCVXPY_Kfold",
            random_state=cfg.kfold_random_state,
        )
    raise ValueError(f"unknown arm: {arm}")


def _run_world_replicate(
    world: AscmWorldSpec,
    cfg: D5InstAugsynthAscm002Config,
    *,
    seed: int,
) -> dict[str, Any]:
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[world.scenario_name],
        random_state=seed,
        n_geos=world.n_geos,
        n_periods=cfg.n_periods,
        treatment_start=cfg.train_length,
        true_effect=0.0,
        **world.scenario_overrides,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data

    if world.use_scenario_treated_units and scenario.treated_units:
        treated = [u for u in scenario.treated_units if u in wide.index]
        control = [u for u in wide.index if u not in treated]
        assignment = {"control": control, "test_0": treated}
        n_test_grps = 1
    else:
        n_test_grps = world.n_test_grps
        assignment = _assign(
            cfg.reference_design_method,
            wide,
            train_length=cfg.train_length,
            seed=seed,
            treatment_probability=world.treatment_probability,
            n_test_grps=n_test_grps,
            rerandomization_max_iter=500,
        )

    panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.train_length,
        test_length=cfg.test_length,
    )
    mean_value = _mean_treated_baseline(panel)
    diagnostics = _panel_strengthening_diagnostics(
        panel,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        min_donors=cfg.min_donors_augsynth,
        alpha=cfg.alpha,
    )

    instruments: dict[str, dict[float, dict[str, Any]]] = {
        arm: {} for arm in INSTRUMENT_ARMS
    }
    for arm in INSTRUMENT_ARMS:
        for prc in world.effect_grid:
            inst = _run_instrument_arm(
                panel,
                arm,
                percent_effect=float(prc),
                mean_value=mean_value,
                cfg=cfg,
            )
            inst.update(_recovery_metrics(inst, percent_effect=float(prc)))
            inst["false_confidence_flag"] = _false_confidence_flag(inst, diagnostics)
            instruments[arm][float(prc)] = inst

    null_a26 = instruments["a26_scm_unit_jackknife"].get(0.0, {})
    null_aug = instruments["augsynth_cvxpy_point"].get(0.0, {})
    sign_disagree = float(
        np.sign(null_aug.get("mean_point_effect", 0))
        != np.sign(null_a26.get("mean_point_effect", 0))
        if null_aug.get("feasible") and "mean_point_effect" in null_a26
        else float("nan")
    )
    material_mismatch = float(
        abs(null_aug.get("mean_point_effect", 0) - null_a26.get("mean_point_effect", 0))
        > cfg.material_point_mismatch_threshold
        if null_aug.get("feasible") and "mean_point_effect" in null_a26
        else float("nan")
    )

    return {
        "seed": seed,
        "world_id": world.world_id,
        "fit_class": world.fit_class,
        "charter_label": world.charter_label,
        "scenario_name": world.scenario_name,
        "n_control": len(panel.control_units),
        "n_treated": len(panel.treated_units),
        "diagnostics": diagnostics,
        "instruments": instruments,
        "conflict_vs_a26": {
            "null_sign_disagreement": sign_disagree,
            "null_material_point_mismatch": material_mismatch,
        },
    }


def _aggregate_arm_world(
    replicates: list[dict[str, Any]],
    *,
    world_id: str,
    arm: str,
    effect: float,
) -> dict[str, Any]:
    vals_fpr = []
    vals_bias = []
    vals_mae = []
    vals_hw = []
    vals_feasible = []
    vals_point = []
    vals_false_conf = []
    vals_scm_rmse = []
    vals_aug_rmse = []
    vals_fit_imp = []
    vals_hull = []
    errors: dict[str, int] = {}

    for rep in replicates:
        if rep["world_id"] != world_id:
            continue
        inst = rep["instruments"].get(arm, {}).get(float(effect), {})
        diag = rep.get("diagnostics", {})
        if inst.get("blocked_reason"):
            key = str(inst.get("error_type") or inst["blocked_reason"])[:60]
            errors[key] = errors.get(key, 0) + 1
        if inst.get("feasible") or "mean_point_effect" in inst:
            vals_feasible.append(float(inst.get("feasible", 1.0)))
            if "mean_point_effect" in inst:
                vals_point.append(float(inst["mean_point_effect"]))
            det = inst.get("detected_interval_excludes_zero")
            if det is None:
                det = inst.get("detected_correct")
            if det is not None and np.isfinite(det):
                vals_fpr.append(float(det))
            bias = inst.get("effect_recovery_bias")
            if bias is not None and np.isfinite(bias):
                vals_bias.append(float(bias))
            mae = inst.get("effect_recovery_mae")
            if mae is not None and np.isfinite(mae):
                vals_mae.append(float(mae))
            hw = inst.get("mean_interval_halfwidth")
            if hw is not None and np.isfinite(hw):
                vals_hw.append(float(hw))
            fc = inst.get("false_confidence_flag")
            if fc is not None and np.isfinite(fc):
                vals_false_conf.append(float(fc))
        if effect == 0.0 and diag.get("diagnostics_feasible"):
            for key, bucket in (
                ("scm_pre_rmse", vals_scm_rmse),
                ("augsynth_pre_rmse", vals_aug_rmse),
                ("fit_improvement_rmse", vals_fit_imp),
                ("hull_min_donor_z_distance", vals_hull),
            ):
                v = diag.get(key)
                if v is not None and np.isfinite(v):
                    bucket.append(float(v))

    return {
        "world_id": world_id,
        "instrument": arm,
        "effect": effect,
        "feasibility_rate": float(np.mean(vals_feasible)) if vals_feasible else 0.0,
        "mean_point_effect": _summarize(vals_point),
        "null_interval_exclusion_fpr": _summarize(vals_fpr),
        "effect_recovery_bias": _summarize(vals_bias),
        "effect_recovery_mae": _summarize(vals_mae),
        "mean_interval_halfwidth": _summarize(vals_hw),
        "false_confidence_rate": _summarize(vals_false_conf),
        "scm_pre_rmse": _summarize(vals_scm_rmse),
        "augsynth_pre_rmse": _summarize(vals_aug_rmse),
        "fit_improvement_rmse": _summarize(vals_fit_imp),
        "hull_min_donor_z_distance": _summarize(vals_hull),
        "failure_counts": errors,
    }


def _compare_weak_fit_vs_a26(
    summaries: list[dict[str, Any]],
    *,
    weak_world_ids: tuple[str, ...],
) -> dict[str, Any]:
    rows = []
    for wid in weak_world_ids:
        a26_inj = next(
            (
                s
                for s in summaries
                if s["world_id"] == wid
                and s["instrument"] == "a26_scm_unit_jackknife"
                and s["effect"] == 0.08
            ),
            None,
        )
        aug_inj = next(
            (
                s
                for s in summaries
                if s["world_id"] == wid
                and s["instrument"] == "augsynth_cvxpy_point"
                and s["effect"] == 0.08
            ),
            None,
        )
        a26_null = next(
            (
                s
                for s in summaries
                if s["world_id"] == wid
                and s["instrument"] == "a26_scm_unit_jackknife"
                and s["effect"] == 0.0
            ),
            None,
        )
        aug_null = next(
            (
                s
                for s in summaries
                if s["world_id"] == wid
                and s["instrument"] == "augsynth_cvxpy_point"
                and s["effect"] == 0.0
            ),
            None,
        )
        if not a26_inj or not aug_inj:
            continue
        a26_mae = (a26_inj.get("effect_recovery_mae") or {}).get("mean")
        aug_mae = (aug_inj.get("effect_recovery_mae") or {}).get("mean")
        a26_fpr = (
            (a26_null.get("null_interval_exclusion_fpr") or {}).get("mean")
            if a26_null
            else None
        )
        aug_fpr_null = (
            (aug_null.get("null_interval_exclusion_fpr") or {}).get("mean")
            if aug_null
            else None
        )
        aug_jk_null = next(
            (
                s
                for s in summaries
                if s["world_id"] == wid
                and s["instrument"] == "augsynth_cvxpy_unit_jackknife"
                and s["effect"] == 0.0
            ),
            None,
        )
        aug_jk_fpr = (
            (aug_jk_null.get("null_interval_exclusion_fpr") or {}).get("mean")
            if aug_jk_null
            else None
        )
        rows.append(
            {
                "world_id": wid,
                "a26_mae_at_8pct": a26_mae,
                "augsynth_mae_at_8pct": aug_mae,
                "augsynth_beats_a26_mae": bool(
                    np.isfinite(a26_mae)
                    and np.isfinite(aug_mae)
                    and aug_mae < a26_mae
                ),
                "a26_jk_null_fpr": a26_fpr,
                "augsynth_jk_null_fpr": aug_jk_fpr,
                "augsynth_point_has_interval_at_null": aug_fpr_null,
            }
        )
    beat_count = sum(1 for r in rows if r.get("augsynth_beats_a26_mae"))
    unsafe_null = any(
        np.isfinite(r.get("augsynth_jk_null_fpr") or float("nan"))
        and (r.get("augsynth_jk_null_fpr") or 0) > 0.15
        for r in rows
    )
    return {
        "weak_fit_comparisons": rows,
        "augsynth_beats_a26_weak_fit_world_count": beat_count,
        "weak_fit_world_count": len(rows),
        "augsynth_point_elevated_null_fpr": unsafe_null,
    }


def _decide_overall(
    summaries: list[dict[str, Any]],
    weak_compare: dict[str, Any],
    *,
    cfg: D5InstAugsynthAscm002Config,
) -> tuple[OverallVerdict, list[dict[str, Any]]]:
    pt_feas = [
        s["feasibility_rate"]
        for s in summaries
        if s["instrument"] == "augsynth_cvxpy_point" and s["effect"] == 0.0
    ]
    if not pt_feas or float(np.mean(pt_feas)) < 0.5:
        return "blocked_low_feasibility", [
            {
                "id": "D5-ASCM2-FIND-001",
                "summary": "AugSynthCVXPY feasibility below threshold across worlds.",
            }
        ]

    cf_null_fpr = [
        (s.get("null_interval_exclusion_fpr") or {}).get("mean", float("nan"))
        for s in summaries
        if s["instrument"] == "augsynth_cvxpy_conformal" and s["effect"] == 0.0
    ]
    conformal_unsafe = any(np.isfinite(x) and x > 0.5 for x in cf_null_fpr)

    beat = int(weak_compare.get("augsynth_beats_a26_weak_fit_world_count", 0))
    n_weak = int(weak_compare.get("weak_fit_world_count", 0))
    findings: list[dict[str, Any]] = [
        {
            "id": "D5-ASCM2-FIND-002",
            "summary": "Stratified weak-fit / hull worlds executed; prior D5 batteries did not.",
            "implication": "Enables promotion-audit evidence scoping only.",
        },
        {
            "id": "D5-ASCM2-FIND-003",
            "summary": f"AugSynth point beats A26 MAE on {beat}/{n_weak} weak-fit worlds @ 8% injection.",
            "implication": "Partial recovery evidence; not promotion.",
        },
    ]
    if conformal_unsafe:
        findings.append(
            {
                "id": "D5-ASCM2-FIND-004",
                "severity": "high",
                "summary": "AugSynth+Conformal retains high null interval-exclusion FPR (consistent with D5-003).",
                "implication": "Do not nominate Conformal for null-monitor; inference ADR required.",
            }
        )

    if beat >= max(1, n_weak) and not weak_compare.get("augsynth_point_elevated_null_fpr"):
        return "strengthening_partial_weak_fit_gain", findings
    if beat == 0:
        return "strengthening_no_beat_a26", findings
    return "remain_diagnostic_comparator", findings


def build_d5_inst_augsynth_ascm_002(
    cfg: D5InstAugsynthAscm002Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5InstAugsynthAscm002Config()
    replicates: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for i in range(cfg.n_mc):
            seed = cfg.random_state_base + (hash(world.world_id) % 10_000) + i * 17
            replicates.append(_run_world_replicate(world, cfg, seed=seed))

    summaries: list[dict[str, Any]] = []
    for world in cfg.worlds:
        for arm in INSTRUMENT_ARMS:
            for effect in world.effect_grid:
                summaries.append(
                    _aggregate_arm_world(
                        replicates,
                        world_id=world.world_id,
                        arm=arm,
                        effect=float(effect),
                    )
                )

    weak_compare = _compare_weak_fit_vs_a26(
        summaries, weak_world_ids=cfg.weak_fit_world_ids
    )
    overall, findings = _decide_overall(summaries, weak_compare, cfg=cfg)

    return {
        "artifact_id": "D5-INST-AUGSYNTH-ASCM-002",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "AUGSYNTH_ASCM_STRENGTHENING_001",
            "METHOD_STRENGTHENING_LANES_001",
            "METHOD_SELECTION_AND_PROMOTION_FRAMEWORK_001",
            "D5_INST_AUGSYNTH_001_REPORT",
            "D5_INST_AUGSYNTH_003_REPORT",
        ],
        "governance": {
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_mmm": True,
            "no_governed_uncertainty_allowlist_change": True,
            "no_trust_report_change": True,
            "no_f_decision_change": True,
            "a26_remains_baseline": True,
            "augsynth_not_primary": True,
            "primary_inference_not_selected": True,
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "world_ids": [w.world_id for w in cfg.worlds],
            "instrument_arms": list(INSTRUMENT_ARMS),
            "min_donors_augsynth": cfg.min_donors_augsynth,
        },
        "world_registry": [
            {
                "world_id": w.world_id,
                "charter_label": w.charter_label,
                "scenario_name": w.scenario_name,
                "fit_class": w.fit_class,
                "effect_grid": list(w.effect_grid),
            }
            for w in cfg.worlds
        ],
        "replicates": replicates,
        "summaries_by_world_arm_effect": summaries,
        "weak_fit_vs_a26": weak_compare,
        "overall_verdict": overall,
        "exit_recommendation": (
            "proceed_to_inference_pairing_ADR"
            if overall == "strengthening_partial_weak_fit_gain"
            else "remain_diagnostic_comparator"
        ),
        "findings": findings,
        "promotion_audit_eligible": False,
    }


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5InstAugsynthAscm002Config | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUGSYNTH_ASCM_002_results.json"
    )
    payload = build_d5_inst_augsynth_ascm_002(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


def write_report(
    results_path: Path | None = None,
    report_path: Path | None = None,
) -> Path:
    results_path = results_path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUGSYNTH_ASCM_002_results.json"
    )
    report_path = report_path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "D5_INST_AUGSYNTH_ASCM_002_REPORT.md"
    )
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    weak = payload.get("weak_fit_vs_a26", {})
    lines = [
        "# D5-INST-AUGSYNTH-ASCM-002 — AugSynth/ASCM vs A26 stratified OC",
        "",
        f"**Artifact:** [`archives/D5_INST_AUGSYNTH_ASCM_002_results.json`](archives/D5_INST_AUGSYNTH_ASCM_002_results.json)  ",
        f"**Harness:** `panel_exp/validation/track_d_d5_inst_augsynth_ascm_002.py`  ",
        f"**Charter:** [`../AUGSYNTH_ASCM_STRENGTHENING_001.md`](../AUGSYNTH_ASCM_STRENGTHENING_001.md)  ",
        "",
        "## Summary",
        "",
        f"**Overall verdict:** `{payload.get('overall_verdict')}`  ",
        f"**Exit recommendation:** `{payload.get('exit_recommendation')}`  ",
        f"**Promotion audit eligible:** `{payload.get('promotion_audit_eligible')}`",
        "",
        "Compares **A26 SCM+UnitJackKnife** to **AugSynthCVXPY** arms across "
        f"{len(payload.get('world_registry', []))} charter worlds (weak SCM fit / hull stress stratified).",
        "",
        "## Weak-fit vs A26 (@ 8% injection)",
        "",
        f"- AugSynth point beats A26 MAE on "
        f"**{weak.get('augsynth_beats_a26_weak_fit_world_count', 0)}/"
        f"{weak.get('weak_fit_world_count', 0)}** weak-fit worlds.",
        "",
        "## Governance",
        "",
        "| Flag | Value |",
        "|------|-------|",
        f"| Promotion | **No** |",
        f"| CalibrationSignal | **No** |",
        f"| MMM | **No** |",
        f"| A26 baseline | **Unchanged** |",
        f"| Primary inference selected | **No** |",
        "",
        "## Findings",
        "",
    ]
    for f in payload.get("findings", []):
        sev = f.get("severity")
        prefix = f" ({sev})" if sev else ""
        lines.append(f"- **{f.get('id', 'FIND')}**{prefix}: {f.get('summary')}")
    lines.extend(
        [
            "",
            "## Weak-fit comparison detail",
            "",
            "| world | AugSynth beats A26 MAE @ 8% | A26 JK null FPR | AugSynth JK null FPR |",
            "|-------|------------------------------|-----------------|----------------------|",
        ]
    )
    for row in weak.get("weak_fit_comparisons", []):
        lines.append(
            f"| `{row.get('world_id')}` | {row.get('augsynth_beats_a26_mae')} | "
            f"{row.get('a26_jk_null_fpr')} | {row.get('augsynth_jk_null_fpr')} |"
        )
    lines.extend(["", "## Worlds", "", "| world_id | fit_class |", "|----------|-----------|"])
    for w in payload.get("world_registry", []):
        lines.append(f"| `{w['world_id']}` | {w['fit_class']} |")
    lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


if __name__ == "__main__":
    out = write_artifact()
    rep = write_report()
    print(f"Wrote {out}")
    print(f"Wrote {rep}")
