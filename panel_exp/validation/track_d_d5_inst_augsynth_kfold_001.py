"""D5-INST-AUGSYNTH-KFOLD-001 — AugSynthCVXPY + KFold OC (research).

Characterizes AugSynthCVXPY + Kfold on 001e/MCELL windows. SCM+JK and AugSynth+JK
are diagnostic context only. No promotion, no CalibrationSignal ingress.
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
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_pow_001b import (
    _inject_percent_effect,
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

GeometryMode = Literal["single_cell", "multi_cell_k2_per_cell"]
OverallVerdict = Literal[
    "remain_restricted_diagnostic_comparator",
    "restricted_with_caveats",
    "blocked_low_feasibility",
]


@dataclass(frozen=True)
class D5InstAugsynthKfold001Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260620
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.04, 0.08)
    include_multi_cell_k2: bool = True
    min_donors_augsynth: int = 5
    kfold_random_state: int = 0
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    min_feasibility_rate: float = 0.7
    kfold_seed_sensitivity_replicates: int = 3


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


def _post_window_arrays(
    results: dict, test_length: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    y = np.asarray(results["y"], dtype=float)
    y_hat = np.asarray(results["y_hat"], dtype=float)
    y_lo = np.asarray(results.get("y_lower", y), dtype=float)
    y_hi = np.asarray(results.get("y_upper", y), dtype=float)
    if y.ndim == 2:
        y = np.nanmean(y, axis=1)
    if y_hat.ndim == 2:
        y_hat = np.nanmean(y_hat, axis=1)
    if y_lo.ndim == 2:
        y_lo = np.nanmean(y_lo, axis=1)
    if y_hi.ndim == 2:
        y_hi = np.nanmean(y_hi, axis=1)
    sl = slice(-test_length, None)
    return y[sl], y_hat[sl], y_lo[sl], y_hi[sl]


def _augsynth_readout_metrics(
    panel: PanelDataset,
    *,
    inference: str,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
    instrument_id: str,
    random_state: int | None = None,
) -> dict[str, Any]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    n_control = len(pds.control_units)
    n_treated = len(pds.treated_units)
    out: dict[str, Any] = {
        "instrument_id": instrument_id,
        "percent_effect": float(percent_effect),
        "n_control_donors": n_control,
        "n_treated_units": n_treated,
        "feasible": 0.0,
        "fit_success": 0.0,
        "has_point": 0.0,
        "has_interval": 0.0,
        "blocked_reason": None,
        "error_type": None,
        "wall_time_s": float("nan"),
    }

    if n_control < min_donors:
        out["blocked_reason"] = f"insufficient_donors_need_{min_donors}_got_{n_control}"
        return out

    skip = cvxpy_osqp_skip_reason()
    if skip:
        out["blocked_reason"] = skip
        return out

    t0 = time.perf_counter()
    try:
        est = AugSynthCVXPY(
            inference=inference,
            alpha=alpha,
            min_donors=min_donors,
        )
        kwargs: dict[str, Any] = {}
        if inference in ("Kfold", "kfold") and random_state is not None:
            kwargs["random_state"] = random_state
        est.run_analysis(pds, **kwargs)
        out["fit_success"] = 1.0
        out["feasible"] = 1.0
    except Exception as exc:
        out["error_type"] = type(exc).__name__
        out["blocked_reason"] = str(exc)[:240]
        out["wall_time_s"] = time.perf_counter() - t0
        return out

    out["wall_time_s"] = time.perf_counter() - t0
    results = est.results or {}
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length)
    if not (np.any(np.isfinite(y)) and np.any(np.isfinite(y_hat))):
        out["blocked_reason"] = "non_finite_y_or_y_hat"
        return out

    out["has_point"] = 1.0
    effect = y - y_hat
    effect_lo = y - y_hi
    effect_hi = y - y_lo
    point_mean = float(np.mean(effect))

    has_interval = inference not in (None, "point_estimate")
    out["has_interval"] = float(has_interval)
    covers_zero = float(np.nan)
    detected = float(np.nan)
    mean_hw = float(np.nan)
    if has_interval and np.any(np.isfinite(y_lo)) and np.any(np.isfinite(y_hi)):
        covers_zero = float(np.mean(effect_lo) <= 0.0 <= np.mean(effect_hi))
        detected = float(not covers_zero)
        mean_hw = float(np.mean((y_hi - y_lo) / 2.0))

    ir = getattr(est, "inference_result", None)
    path_it = None
    if ir is not None:
        pit = getattr(ir, "path_interval_type", None)
        path_it = getattr(pit, "value", pit)

    out.update(
        {
            "mean_point_effect": point_mean,
            "covers_zero_correct": covers_zero,
            "detected_interval_excludes_zero": detected,
            "mean_interval_halfwidth": mean_hw,
            "path_interval_type": path_it,
            "directional_recovery": float(
                abs(percent_effect) < 1e-12
                or (np.isfinite(point_mean) and np.sign(point_mean) == np.sign(percent_effect))
            ),
        }
    )
    return out


def _run_replicate(
    cfg: D5InstAugsynthKfold001Config,
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
    n_test_grps = 2 if geometry_mode == "multi_cell_k2_per_cell" else 1
    assignment = _assign(
        cfg.reference_design_method,
        wide,
        train_length=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
        n_test_grps=n_test_grps,
        rerandomization_max_iter=500,
    )

    cell_keys = ("test_0", "test_1") if geometry_mode == "multi_cell_k2_per_cell" else ("test_0",)
    cells_out: list[dict[str, Any]] = []
    kfold_null_points: list[float] = []

    for ck in cell_keys:
        panel = _build_unit_panel(
            wide,
            assignment,
            cell_key=ck,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
        )
        mean_value = _mean_treated_baseline(panel)
        instruments: dict[str, dict[float, dict[str, Any]]] = {
            "scm_jk_reference": {},
            "augsynth_cvxpy_jk": {},
            "augsynth_cvxpy_kfold": {},
        }

        for prc in cfg.effect_grid:
            instruments["scm_jk_reference"][float(prc)] = _scm_jk_readout_metrics(
                panel,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
            )
            instruments["augsynth_cvxpy_jk"][float(prc)] = _augsynth_readout_metrics(
                panel,
                inference="UnitJackKnife",
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                instrument_id="AugSynthCVXPY_UnitJackKnife",
            )
            instruments["augsynth_cvxpy_kfold"][float(prc)] = _augsynth_readout_metrics(
                panel,
                inference="Kfold",
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                instrument_id="AugSynthCVXPY_Kfold",
                random_state=cfg.kfold_random_state,
            )

        null_kf = instruments["augsynth_cvxpy_kfold"].get(0.0, {})
        null_jk = instruments["augsynth_cvxpy_jk"].get(0.0, {})
        null_scm = instruments["scm_jk_reference"].get(0.0, {})
        if null_kf.get("feasible") and "mean_point_effect" in null_kf:
            kfold_null_points.append(float(null_kf["mean_point_effect"]))

        cells_out.append(
            {
                "cell_key": ck,
                "n_treated": len(panel.treated_units),
                "n_control": len(panel.control_units),
                "instruments": instruments,
                "context_at_null": {
                    "kfold_vs_jk_detection_disagreement": float(
                        null_kf.get("detected_interval_excludes_zero", float("nan"))
                        != null_jk.get("detected_interval_excludes_zero", float("nan"))
                        if null_kf.get("has_interval") and null_jk.get("has_interval")
                        else float("nan")
                    ),
                    "kfold_vs_scm_jk_detection_disagreement": float(
                        null_kf.get("detected_interval_excludes_zero", float("nan"))
                        != null_scm.get("detected_correct", float("nan"))
                        if null_kf.get("has_interval")
                        else float("nan")
                    ),
                    "point_scale_gap_kfold_minus_scm_jk": float(
                        null_kf.get("mean_point_effect", float("nan"))
                        - null_scm.get("mean_point_effect", float("nan"))
                        if null_kf.get("feasible") and "mean_point_effect" in null_scm
                        else float("nan")
                    ),
                },
            }
        )

    seed_sensitivity: list[float] = []
    if geometry_mode == "single_cell" and cells_out:
        panel0 = _build_unit_panel(
            wide,
            assignment,
            cell_key="test_0",
            train_length=cfg.train_length,
            test_length=cfg.test_length,
        )
        mean_value = _mean_treated_baseline(panel0)
        for rs in range(cfg.kfold_seed_sensitivity_replicates):
            m = _augsynth_readout_metrics(
                panel0,
                inference="Kfold",
                percent_effect=0.0,
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                instrument_id="AugSynthCVXPY_Kfold",
                random_state=cfg.kfold_random_state + rs * 17,
            )
            if m.get("feasible") and "mean_point_effect" in m:
                seed_sensitivity.append(float(m["mean_point_effect"]))

    return {
        "seed": seed,
        "geometry_mode": geometry_mode,
        "n_test_grps": n_test_grps,
        "cells": cells_out,
        "kfold_null_point_spread": float(np.std(seed_sensitivity)) if len(seed_sensitivity) > 1 else 0.0,
    }


def _aggregate_instrument(
    replicates: list[dict[str, Any]],
    instrument_key: str,
    *,
    effect: float,
    geometry_mode: str,
) -> dict[str, Any]:
    vals_feasible: list[float] = []
    vals_fit: list[float] = []
    vals_point: list[float] = []
    vals_fpr: list[float] = []
    vals_hw: list[float] = []
    vals_wall: list[float] = []
    vals_path_it: list[str] = []
    errors: dict[str, int] = {}

    for rep in replicates:
        if rep["geometry_mode"] != geometry_mode:
            continue
        for cell in rep["cells"]:
            inst = cell["instruments"].get(instrument_key, {}).get(float(effect), {})
            if inst.get("blocked_reason"):
                key = str(inst.get("error_type") or inst["blocked_reason"])[:60]
                errors[key] = errors.get(key, 0) + 1
            ok = bool(inst.get("feasible")) or "mean_point_effect" in inst
            if not ok:
                continue
            vals_feasible.append(1.0)
            vals_fit.append(float(inst.get("fit_success", inst.get("feasible", 1))))
            if "mean_point_effect" in inst:
                vals_point.append(float(inst["mean_point_effect"]))
            det = inst.get("detected_interval_excludes_zero")
            if det is None and "detected_correct" in inst:
                det = inst.get("detected_correct")
            if det is not None and np.isfinite(det):
                vals_fpr.append(float(det))
            hw = inst.get("mean_interval_halfwidth")
            if hw is not None and np.isfinite(hw):
                vals_hw.append(float(hw))
            wt = inst.get("wall_time_s")
            if wt is not None and np.isfinite(wt):
                vals_wall.append(float(wt))
            pit = inst.get("path_interval_type")
            if pit:
                vals_path_it.append(str(pit))

    return {
        "instrument": instrument_key,
        "geometry_mode": geometry_mode,
        "effect": effect,
        "feasibility_rate": float(np.mean(vals_feasible)) if vals_feasible else 0.0,
        "fit_success_rate": float(np.mean(vals_fit)) if vals_fit else 0.0,
        "mean_point_effect": _summarize(vals_point),
        "null_interval_exclusion_fpr": _summarize(vals_fpr),
        "mean_interval_halfwidth": _summarize(vals_hw),
        "mean_wall_time_s": _summarize(vals_wall),
        "path_interval_type_mode": max(set(vals_path_it), key=vals_path_it.count) if vals_path_it else None,
        "failure_counts": errors,
    }


def _decide_verdict(
    kfold_single: dict[str, Any],
    kfold_multi: dict[str, Any] | None,
    scm_null: dict[str, Any],
    jk_null: dict[str, Any],
    *,
    cfg: D5InstAugsynthKfold001Config,
) -> dict[str, Any]:
    feas = kfold_single["feasibility_rate"]
    kf_fpr = kfold_single["null_interval_exclusion_fpr"]["mean"]
    scm_fpr = scm_null["null_interval_exclusion_fpr"]["mean"]
    jk_fpr = jk_null["null_interval_exclusion_fpr"]["mean"]

    if feas < cfg.min_feasibility_rate:
        overall: OverallVerdict = "blocked_low_feasibility"
        rationale = (
            f"AugSynthCVXPY+Kfold feasibility {feas:.2f} below {cfg.min_feasibility_rate}; "
            "do not export as governed comparator."
        )
        track_e = "blocked"
    elif np.isfinite(kf_fpr) and kf_fpr > cfg.null_fpr_concerning_max:
        overall = "restricted_with_caveats"
        rationale = (
            f"Null interval-exclusion FPR {kf_fpr:.3f} exceeds concern threshold "
            f"({cfg.null_fpr_concerning_max}); restricted diagnostic only."
        )
        track_e = "restricted"
    elif np.isfinite(kf_fpr) and kf_fpr > cfg.null_fpr_acceptable_max:
        overall = "restricted_with_caveats"
        rationale = "Elevated null FPR vs SCM+JK null-monitor; not lift evidence."
        track_e = "restricted"
    elif np.isfinite(scm_fpr) and np.isfinite(kf_fpr) and kf_fpr > scm_fpr + 0.1:
        overall = "restricted_with_caveats"
        rationale = "Kfold more anti-conservative than SCM+JK at null on this battery."
        track_e = "restricted"
    else:
        overall = "remain_restricted_diagnostic_comparator"
        rationale = (
            "Feasible on 001e windows; interval semantics are confidence_interval not null-monitor. "
            "Valid diagnostic comparator for triangulation — not CalibrationSignal or estimand-equivalent to SCM+JK."
        )
        track_e = "restricted"

    multi_feas = kfold_multi["feasibility_rate"] if kfold_multi else float("nan")
    multi_note = "per_cell_only"
    if kfold_multi and multi_feas < cfg.min_feasibility_rate:
        multi_note = "per_cell_degraded_thin_donors"

    return {
        "primary_instrument": "AugSynthCVXPY_Kfold",
        "overall_verdict": overall,
        "rationale": rationale,
        "track_e_inst_004_kfold": track_e,
        "calibration_signal_ingress": False,
        "mmm_ingress": False,
        "estimand_equivalence_claim": False,
        "feasibility_single_cell": feas,
        "feasibility_multi_cell_k2_per_cell": multi_feas,
        "null_fpr_kfold": kf_fpr,
        "null_fpr_augsynth_jk": jk_fpr,
        "null_fpr_scm_jk": scm_fpr,
        "multi_cell_policy": multi_note,
        "combo_audit_status_update": "valid_candidate → characterized_restricted",
    }


def build_d5_inst_augsynth_kfold_001(
    cfg: D5InstAugsynthKfold001Config | None = None,
) -> dict[str, Any]:
    cfg = cfg or D5InstAugsynthKfold001Config()
    replicates: list[dict[str, Any]] = []
    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + i
        replicates.append(_run_replicate(cfg, seed=seed, geometry_mode="single_cell"))
        if cfg.include_multi_cell_k2:
            replicates.append(
                _run_replicate(cfg, seed=seed + 50_000, geometry_mode="multi_cell_k2_per_cell")
            )

    single = [r for r in replicates if r["geometry_mode"] == "single_cell"]
    multi = [r for r in replicates if r["geometry_mode"] == "multi_cell_k2_per_cell"]

    null_keys = ("scm_jk_reference", "augsynth_cvxpy_jk", "augsynth_cvxpy_kfold")
    summaries_null_single = [
        _aggregate_instrument(single, k, effect=0.0, geometry_mode="single_cell") for k in null_keys
    ]
    summaries_injected = [
        _aggregate_instrument(single, "augsynth_cvxpy_kfold", effect=0.08, geometry_mode="single_cell"),
        _aggregate_instrument(single, "augsynth_cvxpy_jk", effect=0.08, geometry_mode="single_cell"),
    ]

    multi_null_kfold = None
    multi_null_jk = None
    if cfg.include_multi_cell_k2:
        multi_null_kfold = _aggregate_instrument(
            multi, "augsynth_cvxpy_kfold", effect=0.0, geometry_mode="multi_cell_k2_per_cell"
        )
        multi_null_jk = _aggregate_instrument(
            multi, "augsynth_cvxpy_jk", effect=0.0, geometry_mode="multi_cell_k2_per_cell"
        )

    kfold_single = next(s for s in summaries_null_single if s["instrument"] == "augsynth_cvxpy_kfold")
    scm_null = next(s for s in summaries_null_single if s["instrument"] == "scm_jk_reference")
    jk_null = next(s for s in summaries_null_single if s["instrument"] == "augsynth_cvxpy_jk")
    status = _decide_verdict(kfold_single, multi_null_kfold, scm_null, jk_null, cfg=cfg)

    det_disagree_kf_jk = []
    det_disagree_kf_scm = []
    for rep in single:
        for cell in rep["cells"]:
            ctx = cell.get("context_at_null", {})
            if np.isfinite(ctx.get("kfold_vs_jk_detection_disagreement", float("nan"))):
                det_disagree_kf_jk.append(float(ctx["kfold_vs_jk_detection_disagreement"]))
            if np.isfinite(ctx.get("kfold_vs_scm_jk_detection_disagreement", float("nan"))):
                det_disagree_kf_scm.append(float(ctx["kfold_vs_scm_jk_detection_disagreement"]))

    kfold_spread = _summarize([r["kfold_null_point_spread"] for r in single])

    return {
        "artifact_id": "D5-INST-AUGSYNTH-KFOLD-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "D5_INST_COMBO_AUDIT_001",
            "D5_INST_AUGSYNTH_001",
            "TRACK_D_CONCEPTUAL_VALIDITY_AUDIT_001",
            "TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001",
        ],
        "governance": {
            "estimator": "AugSynthCVXPY",
            "inference": "Kfold",
            "no_base_augsynth": True,
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_mmm": True,
            "no_estimand_equivalence": True,
            "context_only": ["SCM_UnitJackKnife", "AugSynthCVXPY_UnitJackKnife"],
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "reference_design_method": cfg.reference_design_method,
            "effect_grid": list(cfg.effect_grid),
            "include_multi_cell_k2": cfg.include_multi_cell_k2,
            "min_donors_augsynth": cfg.min_donors_augsynth,
            "kfold_random_state": cfg.kfold_random_state,
        },
        "instrument_summaries_null_single_cell": summaries_null_single,
        "instrument_summaries_injected_8pct_single_cell": summaries_injected,
        "instrument_summaries_null_multi_cell_k2": {
            "augsynth_cvxpy_kfold": multi_null_kfold,
            "augsynth_cvxpy_jk": multi_null_jk,
        },
        "instrument_status": status,
        "context_comparison": {
            "null_detection_disagreement_kfold_vs_jk_rate": _summarize(det_disagree_kf_jk),
            "null_detection_disagreement_kfold_vs_scm_jk_rate": _summarize(det_disagree_kf_scm),
            "kfold_null_point_seed_sensitivity_std": kfold_spread,
            "note": "Context comparisons are not estimand-equivalence tests.",
        },
        "findings": [
            {
                "id": "D5-ASKF-FIND-001",
                "summary": "AugSynthCVXPY+Kfold runs on 001e single-cell panels when donors >= min_donors.",
            },
            {
                "id": "D5-ASKF-FIND-002",
                "summary": "Kfold path_interval_type is confidence_interval — distinct from JK null-monitor semantics.",
            },
            {
                "id": "D5-ASKF-FIND-003",
                "summary": "Multi-cell k=2 per-cell Kfold follows MCELL thin-donor blocking pattern.",
            },
            {
                "id": "D5-ASKF-FIND-004",
                "summary": "No CalibrationSignal or MMM ingress; remain restricted diagnostic comparator.",
            },
        ],
        "overall_verdict": status["overall_verdict"],
        "user_facing_warnings": [
            "Kfold CI is not interchangeable with SCM+JK null-monitor intervals.",
            "Do not claim direct estimand equivalence between AugSynth Kfold and SCM+JK.",
            "Compare JK/Kfold/SCM+JK as triangulation context only on this battery.",
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_changes": True,
            "no_inference_changes": True,
            "no_trust_report_changes": True,
        },
    }


def write_artifact(
    path: Path | None = None,
    *,
    cfg: D5InstAugsynthKfold001Config | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUGSYNTH_KFOLD_001_results.json"
    )
    payload = build_d5_inst_augsynth_kfold_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
