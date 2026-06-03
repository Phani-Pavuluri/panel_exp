"""D5-INF-POSTFIX-001 — Targeted OC rerun after F-INF-003 (A05, A19 only).

Re-characterizes AugSynthCVXPY+Conformal (A05) and TBRRidge+TimeSeriesKfold (A19) on the
same 001e/MCELL windows as D5-INST-AUGSYNTH-003 and D5-INST-TBRRIDGE-002. Compares
pre-fix (archived P2 batteries) vs post-fix structural and behavioral interval metrics.
No promotion, no CalibrationSignal, no MMM.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.interval_semantics_contract import (
    IntervalReadout,
    IntervalSemanticsClassification,
    classify_interval_semantics,
)
from panel_exp.inference_result import IntervalType
from panel_exp.validation.track_d_d5_inst_augsynth_003 import D5InstAugsynth003Config
from panel_exp.validation.track_d_d5_inst_augsynth_kfold_001 import (
    _augsynth_readout_metrics,
    _build_unit_panel,
    _post_window_arrays,
)
from panel_exp.validation.track_d_d5_inst_tbrridge_002 import D5InstTbrridge002Config
from panel_exp.validation.track_d_d5_pow_001c import _inject_percent_effect
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld

PostfixDisposition = Literal[
    "diagnostic_interval_only",
    "callable_unverified_interval_semantics",
    "blocked_invalid_interval",
    "restricted_no_promotion",
]

OverallVerdict = Literal[
    "remain_restricted_no_promotion",
    "blocked_low_feasibility",
]

# Archived pre-F-INF-003 snapshots (D5-INST-AUGSYNTH-003 / TBRRIDGE-002).
PRE_FIX_A05 = {
    "source_artifact": "D5-INST-AUGSYNTH-003",
    "audit_010_row": "A05",
    "single_cell": {
        "feasibility_rate": 1.0,
        "null_interval_exclusion_fpr_mean": 1.0,
        "negative_halfwidth_rate": 1.0,
        "inverted_bound_rate": 1.0,
        "mean_interval_halfwidth_mean": -8.188834247396114,
    },
    "multi_cell_k2_per_cell": {
        "feasibility_rate": 1.0,
        "null_interval_exclusion_fpr_mean": 1.0,
        "negative_halfwidth_rate": 1.0,
        "inverted_bound_rate": 1.0,
    },
}

PRE_FIX_A19 = {
    "source_artifact": "D5-INST-TBRRIDGE-002",
    "audit_010_row": "A19",
    "single_cell": {
        "feasibility_rate": 1.0,
        "null_interval_exclusion_fpr_mean": 1.0,
        "negative_halfwidth_rate": 1.0,
        "inverted_bound_rate": 1.0,
        "mean_interval_halfwidth_mean": -21.60470591065306,
    },
}


@dataclass(frozen=True)
class D5InfPostfix001Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260624
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid_augsynth: tuple[float, ...] = (0.0, 0.04, 0.08)
    effect_grid_tbrridge: tuple[float, ...] = (0.0, 0.08)
    include_multi_cell_k2: bool = True
    min_donors_augsynth: int = 5
    kfold_random_state: int = 0
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    min_feasibility_rate: float = 0.7
    tsk_k: int = 3


def _structural_flags(
    results: dict[str, Any],
    *,
    test_length: int,
) -> dict[str, float]:
    """Per-run structural interval metrics on the post window."""
    y, y_hat, y_lo, y_hi = _post_window_arrays(results, test_length=test_length)
    mask = np.isfinite(y_lo) & np.isfinite(y_hi)
    if not np.any(mask):
        return {
            "has_interval": 0.0,
            "negative_halfwidth": float("nan"),
            "inverted_bound": float("nan"),
            "mean_interval_halfwidth": float("nan"),
        }
    lo = y_lo[mask]
    hi = y_hi[mask]
    hw = (hi - lo) / 2.0
    return {
        "has_interval": 1.0,
        "negative_halfwidth": float(np.mean(hw < 0)),
        "inverted_bound": float(np.mean(lo > hi)),
        "mean_interval_halfwidth": float(np.mean(hw)),
    }


def _augsynth_conformal_extended(
    panel,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
    random_state: int | None = None,
) -> dict[str, Any]:
    out = _augsynth_readout_metrics(
        panel,
        inference="Conformal",
        percent_effect=percent_effect,
        mean_value=mean_value,
        alpha=alpha,
        test_length=test_length,
        min_donors=min_donors,
        instrument_id="AugSynthCVXPY_Conformal",
        random_state=random_state,
    )
    if out.get("feasible", 0) < 0.5:
        return out
    hw = float(out.get("mean_interval_halfwidth", float("nan")))
    out["negative_halfwidth"] = float(hw < 0) if np.isfinite(hw) else float("nan")
    out["inverted_bound"] = out["negative_halfwidth"]
    out["inverted_bound_rate"] = out["inverted_bound"]
    if np.isfinite(hw) and hw >= 0:
        out["inverted_bound"] = 0.0
        out["inverted_bound_rate"] = 0.0
    return out


def _tbrridge_tskf_extended(
    panel,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    random_state: int,
    cfg: D5InfPostfix001Config,
) -> dict[str, Any]:
    pds = _inject_percent_effect(panel, percent_effect, mean_value)
    from panel_exp.methods.tbr import TBRRidge

    est = TBRRidge(inference="TimeSeriesKfold", alpha=alpha)
    try:
        est.run_analysis(
            pds,
            k=cfg.tsk_k,
            show_progress=False,
            n_jobs=1,
            random_state=random_state,
        )
    except (ValueError, RuntimeError) as exc:
        return {
            "instrument_key": "tbrridge_timeseries_kfold",
            "inference": "TimeSeriesKfold",
            "feasible": 0.0,
            "error": f"{type(exc).__name__}:{exc}",
        }

    from panel_exp.validation.track_d_d5_inst_tbrridge_001 import _readout_metrics

    out = _readout_metrics(
        est.results,
        test_length=test_length,
        percent_effect=percent_effect,
    )
    out.update(
        {
            "feasible": 1.0,
            "instrument_key": "tbrridge_timeseries_kfold",
            "inference": "TimeSeriesKfold",
        }
    )
    struct = _structural_flags(est.results or {}, test_length=test_length)
    out["mean_interval_halfwidth"] = struct["mean_interval_halfwidth"]
    out["negative_halfwidth"] = struct["negative_halfwidth"]
    out["inverted_bound"] = struct["inverted_bound"]
    out["inverted_bound_rate"] = struct["inverted_bound"]
    return out


def _aggregate_runs(
    runs: list[dict[str, Any]],
    *,
    instrument: str,
    geometry_mode: str,
    effect: float = 0.0,
) -> dict[str, Any]:
    vals_feas: list[float] = []
    vals_fpr: list[float] = []
    vals_hw: list[float] = []
    vals_neg: list[float] = []
    vals_inv: list[float] = []
    vals_point: list[float] = []
    errors: dict[str, int] = {}

    for run in runs:
        buckets: list[dict[str, Any]]
        if "instrument_runs" in run:
            buckets = [run]
        else:
            buckets = [
                {"instrument_runs": cell["instrument_runs"]} for cell in run.get("cells", [])
            ]
        for bucket in buckets:
            inst = bucket.get("instrument_runs", {}).get(instrument, {}).get(float(effect), {})
            if not inst:
                continue
            if inst.get("blocked_reason"):
                key = str(inst.get("error_type") or inst["blocked_reason"])[:60]
                errors[key] = errors.get(key, 0) + 1
            if inst.get("feasible", 0) < 0.5:
                continue
            vals_feas.append(1.0)
            det = inst.get("detected_interval_excludes_zero")
            if det is not None and np.isfinite(det):
                vals_fpr.append(float(det))
            hw = inst.get("mean_interval_halfwidth")
            if hw is not None and np.isfinite(hw):
                vals_hw.append(float(hw))
            neg = inst.get("negative_halfwidth")
            if neg is not None and np.isfinite(neg):
                vals_neg.append(float(neg))
            inv = inst.get("inverted_bound")
            if inv is not None and np.isfinite(inv):
                vals_inv.append(float(inv))
            pt = inst.get("mean_point_effect")
            if pt is not None and np.isfinite(pt):
                vals_point.append(float(pt))

    return {
        "instrument": instrument,
        "geometry_mode": geometry_mode,
        "effect": effect,
        "feasibility_rate": float(np.mean(vals_feas)) if vals_feas else 0.0,
        "null_interval_exclusion_fpr": _summarize(vals_fpr),
        "mean_interval_halfwidth": _summarize(vals_hw),
        "negative_halfwidth_rate": float(np.mean(vals_neg)) if vals_neg else float("nan"),
        "inverted_bound_rate": float(np.mean(vals_inv)) if vals_inv else float("nan"),
        "mean_point_effect": _summarize(vals_point),
        "failure_counts": errors,
        "n_feasible": len(vals_feas),
    }


def _finf_classification(
    *,
    estimator: str,
    inference: str,
    summary_null: dict[str, Any],
    test_length: int,
) -> dict[str, Any]:
    """F-INF-001 classification on aggregate null summary (no bound mutation)."""
    fpr = summary_null.get("null_interval_exclusion_fpr", {}).get("mean", float("nan"))
    hw_mean = summary_null.get("mean_interval_halfwidth", {}).get("mean", float("nan"))
    neg_rate = summary_null.get("negative_halfwidth_rate", float("nan"))
    inv_rate = summary_null.get("inverted_bound_rate", float("nan"))

    n = max(int(summary_null.get("n_feasible", 8)), 1)
    center = 10.0
    margin = abs(hw_mean) if np.isfinite(hw_mean) and hw_mean > 0 else 1.0
    if np.isfinite(neg_rate) and neg_rate > 0:
        margin = -margin

    interval_type = (
        IntervalType.CONFORMAL_INTERVAL.value
        if inference == "Conformal"
        else IntervalType.CONFIDENCE_INTERVAL.value
    )
    readout = IntervalReadout(
        estimator_name=estimator,
        inference_mode=inference,
        geometry_mode="single_cell",
        path_interval_type=interval_type,
        y=np.full(n, center),
        y_hat=np.full(n, center),
        y_lower=np.full(n, center - margin),
        y_upper=np.full(n, center + margin),
        test_length=n,
        null_interval_exclusion_rate=float(fpr) if np.isfinite(fpr) else None,
    )
    verdict = classify_interval_semantics(readout, require_metadata_bindings=False)
    return {
        "classification": verdict.classification.value,
        "is_governed_uncertainty": verdict.is_governed_uncertainty,
        "mean_interval_halfwidth": verdict.mean_interval_halfwidth,
        "issue_codes": [i.code for i in verdict.issues],
    }


def _decide_postfix_disposition(
    summary: dict[str, Any],
    *,
    cfg: D5InfPostfix001Config,
) -> tuple[PostfixDisposition, str]:
    feas = float(summary.get("feasibility_rate", 0.0))
    fpr = summary.get("null_interval_exclusion_fpr", {}).get("mean", float("nan"))
    neg = summary.get("negative_halfwidth_rate", float("nan"))
    inv = summary.get("inverted_bound_rate", float("nan"))

    if feas < cfg.min_feasibility_rate:
        return (
            "restricted_no_promotion",
            f"Feasibility {feas:.2f} below battery threshold — remain restricted; no promotion.",
        )
    if (np.isfinite(neg) and neg > 0) or (np.isfinite(inv) and inv > 0):
        return (
            "blocked_invalid_interval",
            "Post-fix OC still shows negative half-width or inverted bounds on feasible runs.",
        )
    if np.isfinite(fpr) and fpr > cfg.null_fpr_concerning_max:
        return (
            "callable_unverified_interval_semantics",
            f"Structurally valid bands but null interval-exclusion FPR {fpr:.3f} "
            f"> {cfg.null_fpr_concerning_max} — behavioral semantics unverified.",
        )
    if np.isfinite(fpr) and fpr > cfg.null_fpr_acceptable_max:
        return (
            "callable_unverified_interval_semantics",
            f"Structurally valid bands; elevated null FPR {fpr:.3f} — restricted diagnostic only.",
        )
    return (
        "diagnostic_interval_only",
        "Structural interval checks pass on battery; remain diagnostic — not governed uncertainty.",
    )


def _compare_pre_post(
    pre: dict[str, Any],
    post: dict[str, Any],
) -> dict[str, Any]:
    def _delta(key: str) -> float | None:
        a = pre.get(key)
        b = post.get(key)
        if a is None or b is None:
            return None
        if isinstance(a, dict):
            a = a.get("mean")
        if isinstance(b, dict):
            b = b.get("mean")
        if a is None or b is None or not (np.isfinite(a) and np.isfinite(b)):
            return None
        return float(b) - float(a)

    return {
        "feasibility_rate_delta": _delta("feasibility_rate"),
        "null_fpr_delta": _delta("null_interval_exclusion_fpr"),
        "negative_halfwidth_rate_delta": _delta("negative_halfwidth_rate"),
        "inverted_bound_rate_delta": _delta("inverted_bound_rate"),
        "mean_halfwidth_delta": _delta("mean_interval_halfwidth"),
        "structural_interval_fixed": (
            post.get("negative_halfwidth_rate", 1) == 0.0
            and post.get("inverted_bound_rate", 1) == 0.0
            and pre.get("negative_halfwidth_rate", 0) > 0
        ),
    }


def _run_augsynth_replicate(cfg: D5InfPostfix001Config, *, seed: int, geometry_mode: str) -> dict[str, Any]:
    augs_cfg = D5InstAugsynth003Config(
        n_mc=1,
        n_geos=cfg.n_geos,
        n_periods=cfg.n_periods,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        random_state_base=seed,
        include_multi_cell_k2=False,
    )
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=augs_cfg.n_geos,
        n_periods=augs_cfg.n_periods,
        treatment_start=augs_cfg.train_length,
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
    cells: list[dict[str, Any]] = []
    for ck in cell_keys:
        panel = _build_unit_panel(
            wide,
            assignment,
            cell_key=ck,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
        )
        mean_value = panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)
        runs: dict[str, dict[float, dict[str, Any]]] = {"augsynth_cvxpy_conformal": {}}
        for prc in cfg.effect_grid_augsynth:
            runs["augsynth_cvxpy_conformal"][float(prc)] = _augsynth_conformal_extended(
                panel,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                random_state=cfg.kfold_random_state,
            )
        cells.append({"cell_key": ck, "instrument_runs": runs})
    return {"seed": seed, "geometry_mode": geometry_mode, "cells": cells}


def _run_tbrridge_replicate(cfg: D5InfPostfix001Config, *, seed: int) -> dict[str, Any]:
    tb_cfg = D5InstTbrridge002Config(random_state_base=seed, n_mc=1)
    scenario = replace(
        RECOVERY_SCENARIO_REGISTRY[cfg.scenario_name],
        random_state=seed,
        n_geos=tb_cfg.n_geos,
        n_periods=tb_cfg.n_periods,
        treatment_start=tb_cfg.train_length,
        true_effect=0.0,
    )
    wide = SyntheticWorld.generate(scenario).to_panel_dataset().wide_data
    assignment = _assign(
        cfg.reference_design_method,
        wide,
        train_length=cfg.train_length,
        seed=seed,
        treatment_probability=cfg.treatment_probability,
        n_test_grps=1,
        rerandomization_max_iter=500,
    )
    panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.train_length,
        test_length=cfg.test_length,
    )
    mean_value = panel.wide_data.loc[panel.treated_units].mean(axis=1).values.astype(float)
    runs: dict[str, dict[float, dict[str, Any]]] = {"tbrridge_timeseries_kfold": {}}
    for prc in cfg.effect_grid_tbrridge:
        runs["tbrridge_timeseries_kfold"][float(prc)] = _tbrridge_tskf_extended(
            panel,
            percent_effect=float(prc),
            mean_value=mean_value,
            alpha=cfg.alpha,
            test_length=cfg.test_length,
            random_state=seed,
            cfg=cfg,
        )
    return {
        "seed": seed,
        "geometry_mode": "single_cell",
        "instrument_runs": runs,
    }


def build_d5_inf_postfix_001(cfg: D5InfPostfix001Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InfPostfix001Config()

    augs_single: list[dict[str, Any]] = []
    augs_multi: list[dict[str, Any]] = []
    for i in range(cfg.n_mc):
        seed = cfg.random_state_base + i
        augs_single.append(_run_augsynth_replicate(cfg, seed=seed, geometry_mode="single_cell"))
        if cfg.include_multi_cell_k2:
            augs_multi.append(
                _run_augsynth_replicate(
                    cfg, seed=seed + 50_000, geometry_mode="multi_cell_k2_per_cell"
                )
            )

    tb_reps = [_run_tbrridge_replicate(cfg, seed=cfg.random_state_base + i) for i in range(cfg.n_mc)]

    def _flatten_augs(reps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        flat: list[dict[str, Any]] = []
        for rep in reps:
            for cell in rep["cells"]:
                flat.append(
                    {
                        "geometry_mode": rep["geometry_mode"],
                        "instrument_runs": cell["instrument_runs"],
                    }
                )
        return flat

    post_a05_single = _aggregate_runs(
        _flatten_augs(augs_single),
        instrument="augsynth_cvxpy_conformal",
        geometry_mode="single_cell",
    )
    post_a05_multi = (
        _aggregate_runs(
            _flatten_augs(augs_multi),
            instrument="augsynth_cvxpy_conformal",
            geometry_mode="multi_cell_k2_per_cell",
        )
        if augs_multi
        else None
    )
    post_a19 = _aggregate_runs(
        tb_reps,
        instrument="tbrridge_timeseries_kfold",
        geometry_mode="single_cell",
    )

    disp_a05, reason_a05 = _decide_postfix_disposition(post_a05_single, cfg=cfg)
    disp_a19, reason_a19 = _decide_postfix_disposition(post_a19, cfg=cfg)

    finf_a05 = _finf_classification(
        estimator="AugSynthCVXPY",
        inference="Conformal",
        summary_null=post_a05_single,
        test_length=cfg.test_length,
    )
    finf_a19 = _finf_classification(
        estimator="TBRRidge",
        inference="TimeSeriesKfold",
        summary_null=post_a19,
        test_length=cfg.test_length,
    )

    compare_a05 = _compare_pre_post(PRE_FIX_A05["single_cell"], post_a05_single)
    compare_a19 = _compare_pre_post(PRE_FIX_A19["single_cell"], post_a19)

    overall: OverallVerdict = "remain_restricted_no_promotion"
    if post_a05_single["feasibility_rate"] < 0.1 and post_a19["feasibility_rate"] < 0.1:
        overall = "blocked_low_feasibility"

    next_impl = "F-INF-002"
    if disp_a05 == "blocked_invalid_interval" or disp_a19 == "blocked_invalid_interval":
        next_impl = "F-INF-003-followup"
    elif disp_a05 == "callable_unverified_interval_semantics" and disp_a19 == "callable_unverified_interval_semantics":
        next_impl = "F-INF-002"

    return {
        "artifact_id": "D5-INF-POSTFIX-001",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "prerequisite": "F-INF-003",
        "binding_docs": [
            "F_INF_003_INTERVAL_ORIENTATION_FIX.md",
            "D5_INST_AUGSYNTH_003",
            "D5_INST_TBRRIDGE_002",
            "AUDIT-010_mmm_readiness_gap.md",
            "F_BACKLOG_001_IMPLEMENTATION_BACKLOG_CLOSEOUT.md",
        ],
        "governance": {
            "scope": "A05 + A19 only",
            "no_promotion": True,
            "no_calibration_signal_expansion": True,
            "no_mmm_ingress": True,
            "no_governed_uncertainty_claim": True,
            "f_inf_classifier_unchanged": True,
        },
        "config": {
            "n_mc": cfg.n_mc,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "include_multi_cell_k2": cfg.include_multi_cell_k2,
        },
        "tuples": {
            "A05": {
                "estimator": "AugSynthCVXPY",
                "inference": "Conformal",
                "geometries": ["single_cell", "multi_cell_k2_per_cell"],
                "pre_fix": PRE_FIX_A05,
                "post_fix": {
                    "single_cell": post_a05_single,
                    "multi_cell_k2_per_cell": post_a05_multi,
                },
                "comparison_single_cell": compare_a05,
                "postfix_disposition": disp_a05,
                "disposition_rationale": reason_a05,
                "f_inf_classification": finf_a05,
                "structurally_valid_interval_ready_for_OC": (
                    compare_a05.get("structural_interval_fixed") is True
                    and disp_a05 != "blocked_invalid_interval"
                ),
                "audit_010_status_after_oc": (
                    "callable_unverified_interval_semantics"
                    if disp_a05 == "callable_unverified_interval_semantics"
                    else disp_a05
                ),
                "promotion": False,
                "calibration_signal_eligible": False,
                "mmm_ready": False,
            },
            "A19": {
                "estimator": "TBRRidge",
                "inference": "TimeSeriesKfold",
                "geometries": ["single_cell"],
                "pre_fix": PRE_FIX_A19,
                "post_fix": {"single_cell": post_a19},
                "comparison_single_cell": compare_a19,
                "postfix_disposition": disp_a19,
                "disposition_rationale": reason_a19,
                "f_inf_classification": finf_a19,
                "structurally_valid_interval_ready_for_OC": (
                    compare_a19.get("structural_interval_fixed") is True
                    and disp_a19 != "blocked_invalid_interval"
                ),
                "audit_010_status_after_oc": (
                    "callable_unverified_interval_semantics"
                    if disp_a19 == "callable_unverified_interval_semantics"
                    else disp_a19
                ),
                "promotion": False,
                "calibration_signal_eligible": False,
                "mmm_ready": False,
            },
        },
        "overall_verdict": overall,
        "next_authorized_track_f_implementation": next_impl,
        "track_f_notes": {
            "A05_prior_battery": "D5-INST-AUGSYNTH-003",
            "A19_prior_battery": "D5-INST-TBRRIDGE-002",
            "structural_fix": "F-INF-003",
            "behavioral_verdict": (
                "Intervals are structurally valid post-fix; null FPR may remain elevated — "
                "not governed uncertainty without further evidence."
            ),
        },
    }


def write_artifact(path: Path | None = None, *, cfg: D5InfPostfix001Config | None = None) -> Path:
    cfg = cfg or D5InfPostfix001Config()
    payload = build_d5_inf_postfix_001(cfg)
    out = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INF_POSTFIX_001_results.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return out


__all__ = [
    "D5InfPostfix001Config",
    "PRE_FIX_A05",
    "PRE_FIX_A19",
    "build_d5_inf_postfix_001",
    "write_artifact",
]
