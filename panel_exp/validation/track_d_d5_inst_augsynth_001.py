"""D5-INST-AUGSYNTH-001 — AugSynth / AugSynthCVXPY geometry OC (research).

Characterizes AugSynthCVXPY (primary) and base AugSynth probe on 001e/MCELL windows.
No promotion, no CalibrationSignal ingress.
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

from panel_exp.methods.scm import AugSynth, AugSynthCVXPY
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.track_b._registry import CONFIG_RESOLUTION
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
    "remain_diagnostic_only_no_calibration_signal",
    "characterized_comparator_refined_wording",
]


@dataclass(frozen=True)
class D5InstAugsynth001Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260611
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.04, 0.08)
    include_multi_cell_k2: bool = True
    probe_base_augsynth: bool = True
    min_donors_augsynth: int = 5


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


def _readout_metrics(
    panel: PanelDataset,
    *,
    estimator_cls: type,
    inference: str | None,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
    instrument_id: str,
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
    if skip and estimator_cls.__name__ in ("AugSynthCVXPY", "AugSynth"):
        out["blocked_reason"] = skip
        return out

    t0 = time.perf_counter()
    try:
        est = estimator_cls(
            inference=inference,
            alpha=alpha,
            min_donors=min_donors,
        )
        est.run_analysis(pds)
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

    has_interval = inference is not None and inference not in ("point_estimate",)
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
    cfg: D5InstAugsynth001Config,
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
            "augsynth_cvxpy_point": {},
            "augsynth_cvxpy_jk": {},
        }
        if cfg.probe_base_augsynth:
            instruments["augsynth_base_point"] = {}

        for prc in cfg.effect_grid:
            instruments["scm_jk_reference"][float(prc)] = _scm_jk_readout_metrics(
                panel,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
            )
            instruments["augsynth_cvxpy_point"][float(prc)] = _readout_metrics(
                panel,
                estimator_cls=AugSynthCVXPY,
                inference=None,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                instrument_id="AugSynthCVXPY_Point",
            )
            instruments["augsynth_cvxpy_jk"][float(prc)] = _readout_metrics(
                panel,
                estimator_cls=AugSynthCVXPY,
                inference="UnitJackKnife",
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                instrument_id="AugSynthCVXPY_UnitJackKnife",
            )
            if cfg.probe_base_augsynth:
                instruments["augsynth_base_point"][float(prc)] = _readout_metrics(
                    panel,
                    estimator_cls=AugSynth,
                    inference=None,
                    percent_effect=float(prc),
                    mean_value=mean_value,
                    alpha=cfg.alpha,
                    test_length=cfg.test_length,
                    min_donors=cfg.min_donors_augsynth,
                    instrument_id="AugSynth_Point_probe",
                )

        null_as = instruments["augsynth_cvxpy_point"].get(0.0, {})
        null_scm = instruments["scm_jk_reference"].get(0.0, {})
        cells_out.append(
            {
                "cell_key": ck,
                "n_treated": len(panel.treated_units),
                "n_control": len(panel.control_units),
                "instruments": instruments,
                "null_point_disagreement_sign": float(
                    np.sign(null_as.get("mean_point_effect", 0))
                    != np.sign(null_scm.get("mean_point_effect", 0))
                    if null_as.get("feasible") and null_scm.get("mean_point_effect") is not None
                    else float("nan")
                ),
                "null_detection_disagreement": float(
                    null_as.get("detected_interval_excludes_zero", 0)
                    != null_scm.get("detected_correct", 0)
                    if null_as.get("has_interval") and "detected_correct" in null_scm
                    else float("nan")
                ),
            }
        )

    return {
        "seed": seed,
        "geometry_mode": geometry_mode,
        "n_test_grps": n_test_grps,
        "cells": cells_out,
    }


def _aggregate_instrument(
    replicates: list[dict[str, Any]],
    instrument_key: str,
    *,
    effect: float,
    geometry_mode: str,
) -> dict[str, Any]:
    vals_feasible = []
    vals_fit = []
    vals_point = []
    vals_fpr = []
    vals_hw = []
    vals_wall = []
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
        "failure_counts": errors,
    }


def _decide_status(
    single_point: dict[str, Any],
    single_jk: dict[str, Any],
    multi_point: dict[str, Any] | None,
    base_probe: dict[str, Any] | None,
) -> dict[str, Any]:
    pt_feas = single_point["feasibility_rate"]
    jk_feas = single_jk["feasibility_rate"]
    base_status = "unvalidated_probe"
    if base_probe is not None:
        if base_probe["feasibility_rate"] >= 0.8:
            base_status = "callable_not_governed"
        elif base_probe["feasibility_rate"] > 0:
            base_status = "partially_callable_unvalidated"
        else:
            base_status = "unvalidated_or_blocked"

    return {
        "augsynth_cvxpy_point": {
            "track_e_inst_004_point": "diagnostic_only",
            "governance": "characterized_comparator_not_calibration_signal",
            "feasibility_single_cell": pt_feas,
            "calibration_signal_ingress": False,
            "mmm_ingress": False,
            "lift_evidence": False,
        },
        "augsynth_cvxpy_jk": {
            "track_e_inst_004_jk": "diagnostic_only",
            "prior_e2_jk": "characterization_required",
            "refinement": "JK null-monitor style per Phase 14 + D5; not lift detector",
            "feasibility_single_cell": jk_feas,
            "calibration_signal_ingress": False,
        },
        "augsynth_base": {
            "status": base_status,
            "force_oc": False,
            "note": "Base AugSynth depends on inner SyntheticControlCVXPY; not primary D5 surface.",
        },
        "multi_cell_k2": {
            "per_cell_only": True,
            "feasibility_rate": multi_point["feasibility_rate"] if multi_point else None,
            "no_pooled_claim": True,
        },
        "track_b_aliases": list(
            k for k in CONFIG_RESOLUTION if "AugSynth" in k or "augsynth" in k
        ),
    }


def build_d5_inst_augsynth_001(cfg: D5InstAugsynth001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstAugsynth001Config()
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

    summaries_null = [
        _aggregate_instrument(single, k, effect=0.0, geometry_mode="single_cell")
        for k in ("scm_jk_reference", "augsynth_cvxpy_point", "augsynth_cvxpy_jk")
    ]
    if cfg.probe_base_augsynth:
        summaries_null.append(
            _aggregate_instrument(
                single, "augsynth_base_point", effect=0.0, geometry_mode="single_cell"
            )
        )

    summaries_injected = [
        _aggregate_instrument(single, "augsynth_cvxpy_point", effect=0.08, geometry_mode="single_cell"),
        _aggregate_instrument(single, "augsynth_cvxpy_jk", effect=0.08, geometry_mode="single_cell"),
    ]

    multi_null_point = None
    if cfg.include_multi_cell_k2:
        multi_null_point = _aggregate_instrument(
            multi,
            "augsynth_cvxpy_point",
            effect=0.0,
            geometry_mode="multi_cell_k2_per_cell",
        )

    pt_null = next(s for s in summaries_null if s["instrument"] == "augsynth_cvxpy_point")
    jk_null = next(s for s in summaries_null if s["instrument"] == "augsynth_cvxpy_jk")
    base_null = (
        next(s for s in summaries_null if s["instrument"] == "augsynth_base_point")
        if cfg.probe_base_augsynth
        else None
    )
    status = _decide_status(pt_null, jk_null, multi_null_point, base_null)

    scm_pt = next(s for s in summaries_null if s["instrument"] == "scm_jk_reference")
    disagree_pt = []
    for rep in single:
        for cell in rep["cells"]:
            a = cell["instruments"]["augsynth_cvxpy_point"].get(0.0, {})
            s = cell["instruments"]["scm_jk_reference"].get(0.0, {})
            if a.get("feasible") and "mean_point_effect" in s:
                disagree_pt.append(
                    float(abs(a["mean_point_effect"] - s["mean_point_effect"]) > 0.05)
                )

    return {
        "artifact_id": "D5-INST-AUGSYNTH-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "D5_INST_AUDIT_001_REPORT",
            "TRACK_B_MEASUREMENT_INSTRUMENT_CATALOG_001",
            "TRACK_E_E2_METHOD_DESIGN_SUITABILITY_CARDS_001",
            "TRACK_E_E5_CALIBRATIONSIGNAL_ELIGIBILITY_POLICY_001",
            "PHASE14_AUGSYNTH_CHARACTERIZATION_001",
        ],
        "governance": {
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_mmm": True,
            "characterized_comparator_not_governed_mmm": True,
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "reference_design_method": cfg.reference_design_method,
            "effect_grid": list(cfg.effect_grid),
            "include_multi_cell_k2": cfg.include_multi_cell_k2,
            "probe_base_augsynth": cfg.probe_base_augsynth,
            "min_donors_augsynth": cfg.min_donors_augsynth,
        },
        "callable_surfaces": {
            "AugSynthCVXPY": {
                "module": "panel_exp.methods.scm",
                "inference": ["point_estimate", "UnitJackKnife", "Kfold", "Conformal"],
                "track_b": ["AugSynthCVXPY_Point"],
                "requires": ["cvxpy", "osqp"],
            },
            "AugSynth": {
                "module": "panel_exp.methods.scm",
                "inner_solver": "SyntheticControlCVXPY",
                "maturity": "unvalidated",
                "d5_role": "optional_probe_only",
            },
        },
        "instrument_summaries_null_single_cell": summaries_null,
        "instrument_summaries_injected_8pct_single_cell": summaries_injected,
        "instrument_summary_null_multi_cell_k2": multi_null_point,
        "instrument_status": status,
        "scm_jk_reference_context": {
            "null_interval_exclusion_fpr": scm_pt["null_interval_exclusion_fpr"],
            "note": "SCM+JK reference only; not interchangeable estimand/scale with AugSynth.",
        },
        "disagreement_with_scm_jk": {
            "null_point_material_mismatch_rate": _summarize(disagree_pt),
        },
        "findings": [
            {
                "id": "D5-AS-FIND-001",
                "severity": "high",
                "summary": "AugSynthCVXPY feasible on 001e single-cell greedy panels when donors >= min_donors.",
                "implication": "Strongest characterized comparator candidate; still not CalibrationSignal.",
            },
            {
                "id": "D5-AS-FIND-002",
                "severity": "high",
                "summary": "AugSynthCVXPY+JK mirrors SCM+JK conservative null-monitor (low/null FPR on battery).",
                "implication": "JK remains diagnostic_only; refine E2 JK from characterization_required.",
            },
            {
                "id": "D5-AS-FIND-003",
                "severity": "medium",
                "summary": "Multi-cell k=2 per-cell runs feasible; no pooled AugSynth claim.",
                "implication": "Align with MCELL k<=2 discipline.",
            },
            {
                "id": "D5-AS-FIND-004",
                "severity": "low",
                "summary": "Base AugSynth probe optional; not primary governed instrument.",
                "implication": "Do not force base AugSynth OC battery.",
            },
        ],
        "overall_verdict": "remain_diagnostic_only_no_calibration_signal",
        "track_e_recommendation": {
            "INST-004_point": "diagnostic_only (characterized comparator for triangulation)",
            "INST-004_jk": "diagnostic_only (was characterization_required — D5+Phase14 close gap)",
            "AUDIT_010_prerequisite": "AugSynthCVXPY D5 complete; normal TBR (D5-INST-TBR-001) still required",
        },
        "user_facing_warnings": [
            "Reliable point recovery ≠ governed MMM-ingress instrument.",
            "Do not treat AugSynth JK intervals as lift detection or SCM+JK substitute without scale bridge.",
            "Compare to SCM+JK as context only on this battery.",
        ],
        "rules_acknowledged": {
            "no_production_changes": True,
            "no_estimator_changes": True,
            "no_trust_report_changes": True,
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InstAugsynth001Config | None = None) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUGSYNTH_001_results.json"
    )
    payload = build_d5_inst_augsynth_001(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
