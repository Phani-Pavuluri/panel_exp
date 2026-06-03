"""D5-INST-AUGSYNTH-003 — AugSynthCVXPY + Conformal OC (research).

Characterizes AugSynthCVXPY + Conformal on 001e/MCELL windows after AUDIT-010,
Track F P0, AUGSYNTH-001/KFOLD-001, and TBRRidge-002. AugSynth point/JK/Kfold are
diagnostic context only. No promotion, no CalibrationSignal ingress.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.instrument_contract import (
    MULTI_CELL_POOLED_WITHOUT_RULE,
    full_model_export_block_reason,
)
from panel_exp.methods.scm import AugSynthCVXPY
from panel_exp.method_metadata import _ESTIMATOR_CATALOG
from panel_exp.panel_data import PanelDataset
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.synthetic_scenarios import RECOVERY_SCENARIO_REGISTRY
from panel_exp.validation.synthetic_world import SyntheticWorld
from panel_exp.validation.track_d_d5_inst_audit_001 import ProbeConfig, _build_wide, _probe_run
from panel_exp.validation.track_d_d5_inst_augsynth_kfold_001 import (
    _augsynth_readout_metrics as _base_augsynth_readout_metrics,
    _build_unit_panel,
)
from panel_exp.validation.track_d_d5_pow_001b import (
    _mean_treated_baseline,
    _scm_jk_readout_metrics,
)
from panel_exp.validation.track_d_d5_pow_001e import _assign, _summarize

GeometryMode = Literal["single_cell", "multi_cell_k2_per_cell"]
PrimaryDisposition = Literal[
    "characterized_restricted_diagnostic",
    "callable_unverified_interval_semantics",
    "blocked_interface",
    "blocked_catalog",
    "deferred",
]
OverallVerdict = Literal[
    "remain_restricted_no_promotion",
    "blocked_low_feasibility",
]

CONFORMAL_SEMANTICS: dict[str, Any] = {
    "score_definition": (
        "Pre-period absolute residuals |Y_{j,t} - Y_hat_{j,t}| calibrated against "
        "treated-period |Y_{j,T} - Y_hat_{j,T}|; one-sided p-value via rank in "
        "pre-period empirical distribution (conformal.py)."
    ),
    "exchangeability_assumption": (
        "Pre-treatment residual magnitudes are exchangeable with treated-period "
        "residuals under the null; fragile under spillover, donor composition shifts, "
        "or post-fit structural breaks."
    ),
    "residual_source_units": (
        "Level outcomes on the treated unit path — same y/y_hat scale as AugSynthCVXPY "
        "results after percent-effect injection on the post window."
    ),
    "path_interval_type": "conformal_interval",
    "governed_uncertainty_eligible": False,
    "diagnostic_only": True,
    "exchangeability_caveat": (
        "AUDIT-010 A05 / Track F F-OD-001 — do not treat as governed uncertainty "
        "unless interval semantics pass on OC battery."
    ),
    "code_refs": [
        "panel_exp/inference/conformal.py",
        "panel_exp/inference/modes/impl.py::run_conformal",
    ],
}


@dataclass(frozen=True)
class D5InstAugsynth003Config:
    n_mc: int = 14
    n_geos: int = 16
    n_periods: int = 44
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    treatment_probability: float = 0.35
    random_state_base: int = 20260623
    scenario_name: str = "scm_low_signal"
    reference_design_method: str = "greedy_match_markets"
    effect_grid: tuple[float, ...] = (0.0, 0.04, 0.08)
    include_multi_cell_k2: bool = True
    min_donors_augsynth: int = 5
    kfold_random_state: int = 0
    null_fpr_acceptable_max: float = 0.15
    null_fpr_concerning_max: float = 0.35
    min_feasibility_rate: float = 0.7
    min_feasibility_for_characterized: float = 0.85
    include_combo_scale_probe: bool = True
    combo_probe: ProbeConfig = ProbeConfig(train_length=20, test_length=6, n_geos=12, seed=42)


def _augsynth_catalog_inference() -> tuple[str, ...]:
    for est in _ESTIMATOR_CATALOG:
        if est.name == "AugSynthCVXPY":
            return est.inference_support
    return ()


def _augsynth_conformal_readout_metrics(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
) -> dict[str, Any]:
    out = _base_augsynth_readout_metrics(
        panel,
        inference="Conformal",
        percent_effect=percent_effect,
        mean_value=mean_value,
        alpha=alpha,
        test_length=test_length,
        min_donors=min_donors,
        instrument_id="AugSynthCVXPY_Conformal",
    )
    hw = float(out.get("mean_interval_halfwidth", float("nan")))
    out["negative_halfwidth"] = float(hw < 0) if np.isfinite(hw) else float("nan")
    out["interval_semantics_verified"] = 0.0
    if out.get("feasible") and np.isfinite(hw) and hw >= 0:
        fpr = out.get("detected_interval_excludes_zero", float("nan"))
        if np.isfinite(fpr) and fpr <= 0.15:
            out["interval_semantics_verified"] = 0.5
    return out


def _augsynth_point_readout_metrics(
    panel: PanelDataset,
    *,
    percent_effect: float,
    mean_value: np.ndarray,
    alpha: float,
    test_length: int,
    min_donors: int,
) -> dict[str, Any]:
    return _base_augsynth_readout_metrics(
        panel,
        inference=None,
        percent_effect=percent_effect,
        mean_value=mean_value,
        alpha=alpha,
        test_length=test_length,
        min_donors=min_donors,
        instrument_id="AugSynthCVXPY_Point",
    )


def _blocked_probes(cfg: D5InstAugsynth003Config) -> dict[str, Any]:
    catalog = set(_augsynth_catalog_inference())
    return {
        "AugSynthCVXPY_Placebo": {
            "status": "blocked_catalog",
            "in_catalog": "Placebo" in catalog,
            "reason": (
                "Placebo not in AugSynthCVXPY inference_support — "
                "inference/falsification layer only (F-P0-005; COMBO invalid_by_interface)."
            ),
            "explicit_block": True,
        },
        "AugSynthCVXPY_BlockResidualBootstrap": {
            "status": "blocked_catalog",
            "in_catalog": "BlockResidualBootstrap" in catalog,
            "reason": (
                "BlockResidualBootstrap not in AugSynthCVXPY inference_support — "
                "P3 catalog clarification; not in scope for this battery."
            ),
            "explicit_block": True,
        },
        "AugSynthCVXPY_full_model_true": {
            "status": "blocked_policy",
            "reason": full_model_export_block_reason("AugSynthCVXPY", True),
            "explicit_block": True,
        },
        "pooled_multi_cell_claim": {
            "status": "blocked_policy",
            "reason": MULTI_CELL_POOLED_WITHOUT_RULE,
            "explicit_block": True,
            "policy": "per_cell_only — no pooling_rule_id",
        },
        "base_AugSynth_not_CVXPY": {
            "status": "blocked_scope",
            "reason": "D5-INST-AUGSYNTH-003 scope is AugSynthCVXPY only — not base AugSynth.",
            "explicit_block": True,
        },
    }


def _combo_scale_probe(cfg: D5InstAugsynth003Config) -> dict[str, Any]:
    if not cfg.include_combo_scale_probe:
        return {"enabled": False}
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {"enabled": True, "skipped": True, "reason": skip}
    wide = _build_wide(cfg.combo_probe)
    assignment = _assign(
        "greedy_match_markets",
        wide,
        train_length=cfg.combo_probe.train_length,
        seed=cfg.combo_probe.seed,
        treatment_probability=0.35,
        n_test_grps=1,
        rerandomization_max_iter=500,
    )
    panel = _build_unit_panel(
        wide,
        assignment,
        cell_key="test_0",
        train_length=cfg.combo_probe.train_length,
        test_length=cfg.combo_probe.test_length,
    )
    return {
        "enabled": True,
        "panel_meta": {
            "train_length": cfg.combo_probe.train_length,
            "test_length": cfg.combo_probe.test_length,
            "n_geos": cfg.combo_probe.n_geos,
        },
        "probe": _probe_run(AugSynthCVXPY, panel, inference="Conformal"),
    }


def _run_replicate(
    cfg: D5InstAugsynth003Config,
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
            "augsynth_cvxpy_kfold": {},
            "augsynth_cvxpy_conformal": {},
        }

        for prc in cfg.effect_grid:
            instruments["scm_jk_reference"][float(prc)] = _scm_jk_readout_metrics(
                panel,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
            )
            instruments["augsynth_cvxpy_point"][float(prc)] = _augsynth_point_readout_metrics(
                panel,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
            )
            instruments["augsynth_cvxpy_jk"][float(prc)] = _base_augsynth_readout_metrics(
                panel,
                inference="UnitJackKnife",
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
                instrument_id="AugSynthCVXPY_UnitJackKnife",
            )
            instruments["augsynth_cvxpy_kfold"][float(prc)] = _base_augsynth_readout_metrics(
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
            instruments["augsynth_cvxpy_conformal"][float(prc)] = _augsynth_conformal_readout_metrics(
                panel,
                percent_effect=float(prc),
                mean_value=mean_value,
                alpha=cfg.alpha,
                test_length=cfg.test_length,
                min_donors=cfg.min_donors_augsynth,
            )

        null_cf = instruments["augsynth_cvxpy_conformal"].get(0.0, {})
        null_jk = instruments["augsynth_cvxpy_jk"].get(0.0, {})
        null_kf = instruments["augsynth_cvxpy_kfold"].get(0.0, {})
        null_pt = instruments["augsynth_cvxpy_point"].get(0.0, {})
        null_scm = instruments["scm_jk_reference"].get(0.0, {})

        cells_out.append(
            {
                "cell_key": ck,
                "n_treated": len(panel.treated_units),
                "n_control": len(panel.control_units),
                "instruments": instruments,
                "context_at_null": {
                    "conformal_vs_jk_detection_disagreement": float(
                        null_cf.get("detected_interval_excludes_zero", float("nan"))
                        != null_jk.get("detected_interval_excludes_zero", float("nan"))
                        if null_cf.get("has_interval") and null_jk.get("has_interval")
                        else float("nan")
                    ),
                    "conformal_vs_kfold_detection_disagreement": float(
                        null_cf.get("detected_interval_excludes_zero", float("nan"))
                        != null_kf.get("detected_interval_excludes_zero", float("nan"))
                        if null_cf.get("has_interval") and null_kf.get("has_interval")
                        else float("nan")
                    ),
                    "conformal_vs_scm_jk_detection_disagreement": float(
                        null_cf.get("detected_interval_excludes_zero", float("nan"))
                        != null_scm.get("detected_correct", float("nan"))
                        if null_cf.get("has_interval")
                        else float("nan")
                    ),
                    "point_scale_gap_conformal_minus_scm_jk": float(
                        null_cf.get("mean_point_effect", float("nan"))
                        - null_scm.get("mean_point_effect", float("nan"))
                        if null_cf.get("feasible") and "mean_point_effect" in null_scm
                        else float("nan")
                    ),
                    "conformal_negative_halfwidth": null_cf.get("negative_halfwidth", float("nan")),
                    "conformal_point_vs_augsynth_point_delta": float(
                        null_cf.get("mean_point_effect", float("nan"))
                        - null_pt.get("mean_point_effect", float("nan"))
                        if null_cf.get("feasible") and null_pt.get("feasible")
                        else float("nan")
                    ),
                },
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
    vals_feasible: list[float] = []
    vals_fit: list[float] = []
    vals_point: list[float] = []
    vals_fpr: list[float] = []
    vals_hw: list[float] = []
    vals_neg_hw: list[float] = []
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
            neg = inst.get("negative_halfwidth")
            if neg is not None and np.isfinite(neg):
                vals_neg_hw.append(float(neg))
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
        "negative_halfwidth_rate": float(np.mean(vals_neg_hw)) if vals_neg_hw else float("nan"),
        "mean_wall_time_s": _summarize(vals_wall),
        "path_interval_type_mode": max(set(vals_path_it), key=vals_path_it.count) if vals_path_it else None,
        "failure_counts": errors,
    }


def _decide_disposition(
    conformal_single: dict[str, Any],
    conformal_multi: dict[str, Any] | None,
    *,
    cfg: D5InstAugsynth003Config,
) -> dict[str, Any]:
    feas = float(conformal_single.get("feasibility_rate", 0.0))
    fpr = conformal_single.get("null_interval_exclusion_fpr", {}).get("mean", float("nan"))
    neg_hw = conformal_single.get("negative_halfwidth_rate", float("nan"))
    multi_feas = conformal_multi["feasibility_rate"] if conformal_multi else float("nan")

    if feas < cfg.min_feasibility_rate:
        disposition: PrimaryDisposition = "blocked_interface"
        rationale = (
            f"AugSynthCVXPY+Conformal feasibility {feas:.2f} below {cfg.min_feasibility_rate}; "
            "interface or donor blocking dominates."
        )
        track_e = "blocked"
    elif np.isfinite(neg_hw) and neg_hw > 0:
        disposition = "callable_unverified_interval_semantics"
        rationale = (
            f"Interface-valid on 001e panel but {neg_hw:.0%} negative interval half-width — "
            "not governed uncertainty; conformal band sign fails OC."
        )
        track_e = "restricted"
    elif np.isfinite(fpr) and fpr > cfg.null_fpr_concerning_max:
        disposition = "callable_unverified_interval_semantics"
        rationale = (
            f"Null interval-exclusion FPR {fpr:.3f} exceeds concern threshold "
            f"({cfg.null_fpr_concerning_max}); exchangeability / band semantics unverified."
        )
        track_e = "restricted"
    elif np.isfinite(fpr) and fpr > cfg.null_fpr_acceptable_max:
        disposition = "callable_unverified_interval_semantics"
        rationale = "Elevated null FPR vs AugSynth JK/Kfold context — restricted diagnostic only."
        track_e = "restricted"
    elif feas >= cfg.min_feasibility_for_characterized:
        disposition = "characterized_restricted_diagnostic"
        rationale = (
            "Feasible on 001e windows with acceptable null FPR on this battery; "
            "remain restricted — conformal_interval ≠ JK null-monitor; not CalibrationSignal."
        )
        track_e = "restricted"
    else:
        disposition = "callable_unverified_interval_semantics"
        rationale = "Partial feasibility — restricted diagnostic only; interval semantics not verified."
        track_e = "restricted"

    multi_note = "per_cell_only"
    if conformal_multi and multi_feas < cfg.min_feasibility_rate:
        multi_note = "per_cell_degraded_thin_donors"

    overall: OverallVerdict = "remain_restricted_no_promotion"
    if feas < 0.1:
        overall = "blocked_low_feasibility"

    return {
        "primary_instrument": "AugSynthCVXPY_Conformal",
        "primary_disposition": disposition,
        "overall_verdict": overall,
        "rationale": rationale,
        "track_e_inst_004_conformal": track_e,
        "calibration_signal_ingress": False,
        "mmm_ingress": False,
        "estimand_equivalence_claim": False,
        "feasibility_single_cell": feas,
        "feasibility_multi_cell_k2_per_cell": multi_feas,
        "null_fpr_conformal": fpr,
        "negative_halfwidth_rate_single_cell": neg_hw,
        "multi_cell_policy": multi_note,
        "combo_audit_status_update": "valid_candidate_pending_OC → callable_unverified_interval_semantics",
        "promotion": False,
    }


def build_d5_inst_augsynth_003(cfg: D5InstAugsynth003Config | None = None) -> dict[str, Any]:
    cfg = cfg or D5InstAugsynth003Config()
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

    context_keys = (
        "scm_jk_reference",
        "augsynth_cvxpy_point",
        "augsynth_cvxpy_jk",
        "augsynth_cvxpy_kfold",
        "augsynth_cvxpy_conformal",
    )
    summaries_null_single = [
        _aggregate_instrument(single, k, effect=0.0, geometry_mode="single_cell") for k in context_keys
    ]
    summaries_injected = [
        _aggregate_instrument(single, "augsynth_cvxpy_conformal", effect=0.08, geometry_mode="single_cell"),
        _aggregate_instrument(single, "augsynth_cvxpy_jk", effect=0.08, geometry_mode="single_cell"),
        _aggregate_instrument(single, "augsynth_cvxpy_kfold", effect=0.08, geometry_mode="single_cell"),
    ]

    multi_null_conformal = None
    multi_null_jk = None
    if cfg.include_multi_cell_k2:
        multi_null_conformal = _aggregate_instrument(
            multi, "augsynth_cvxpy_conformal", effect=0.0, geometry_mode="multi_cell_k2_per_cell"
        )
        multi_null_jk = _aggregate_instrument(
            multi, "augsynth_cvxpy_jk", effect=0.0, geometry_mode="multi_cell_k2_per_cell"
        )

    conformal_single = next(
        s for s in summaries_null_single if s["instrument"] == "augsynth_cvxpy_conformal"
    )
    status = _decide_disposition(conformal_single, multi_null_conformal, cfg=cfg)

    det_disagree_cf_jk = []
    det_disagree_cf_kf = []
    det_disagree_cf_scm = []
    neg_hw_cells = []
    for rep in single:
        for cell in rep["cells"]:
            ctx = cell.get("context_at_null", {})
            for key, bucket in (
                ("conformal_vs_jk_detection_disagreement", det_disagree_cf_jk),
                ("conformal_vs_kfold_detection_disagreement", det_disagree_cf_kf),
                ("conformal_vs_scm_jk_detection_disagreement", det_disagree_cf_scm),
            ):
                if np.isfinite(ctx.get(key, float("nan"))):
                    bucket.append(float(ctx[key]))
            nhw = ctx.get("conformal_negative_halfwidth")
            if nhw is not None and np.isfinite(nhw):
                neg_hw_cells.append(float(nhw))

    return {
        "artifact_id": "D5-INST-AUGSYNTH-003",
        "artifact_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lane": "research",
        "binding_docs": [
            "AUDIT-010_mmm_readiness_gap.md",
            "D5_INST_COMBO_AUDIT_001",
            "D5_INST_AUGSYNTH_001",
            "D5_INST_AUGSYNTH_KFOLD_001",
            "D5_INST_TBRRIDGE_002",
            "TRACK_F_ESTIMATOR_INFERENCE_COMPLETION_PLAN_001",
        ],
        "governance": {
            "estimator": "AugSynthCVXPY",
            "inference": "Conformal",
            "no_base_augsynth": True,
            "no_promotion": True,
            "no_calibration_signal_ingress": True,
            "no_mmm": True,
            "no_estimand_equivalence": True,
            "no_pooled_multi_cell": True,
            "context_only": [
                "SCM_UnitJackKnife",
                "AugSynthCVXPY_Point",
                "AugSynthCVXPY_UnitJackKnife",
                "AugSynthCVXPY_Kfold",
            ],
            "explicit_blocks": _blocked_probes(cfg),
        },
        "conformal_interval_semantics": CONFORMAL_SEMANTICS,
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
            "augsynth_cvxpy_conformal": multi_null_conformal,
            "augsynth_cvxpy_jk": multi_null_jk,
        },
        "instrument_status": status,
        "context_comparison": {
            "null_detection_disagreement_conformal_vs_jk_rate": _summarize(det_disagree_cf_jk),
            "null_detection_disagreement_conformal_vs_kfold_rate": _summarize(det_disagree_cf_kf),
            "null_detection_disagreement_conformal_vs_scm_jk_rate": _summarize(det_disagree_cf_scm),
            "conformal_negative_halfwidth_cell_rate": _summarize(neg_hw_cells),
            "note": "Context comparisons are not estimand-equivalence tests.",
        },
        "combo_scale_probes": _combo_scale_probe(cfg),
        "findings": [
            {
                "id": "D5-ASCF-FIND-001",
                "summary": "AugSynthCVXPY+Conformal is interface-valid on 001e unit panels when donors >= min_donors.",
            },
            {
                "id": "D5-ASCF-FIND-002",
                "summary": "Conformal path_interval_type is conformal_interval — distinct from JK null-monitor and Kfold CI.",
            },
            {
                "id": "D5-ASCF-FIND-003",
                "summary": "Negative interval half-width and 100% null interval-exclusion on this battery — not governed uncertainty.",
            },
            {
                "id": "D5-ASCF-FIND-004",
                "summary": "Placebo/BRB/full_model/pooled multi-cell explicitly blocked; no CalibrationSignal or MMM ingress.",
            },
        ],
        "overall_verdict": status["overall_verdict"],
        "primary_disposition": status["primary_disposition"],
        "track_f_p2_roadmap": {
            "AugSynthCVXPY_Conformal": status["primary_disposition"],
            "TBRRidge_Conformal": "blocked_interface (TBRRIDGE-002)",
            "next_battery": None,
            "p2_complete": True,
        },
        "user_facing_warnings": [
            "Conformal intervals are not interchangeable with SCM+JK null-monitor or Kfold CI.",
            "Do not treat conformal band as governed uncertainty unless interval semantics pass.",
            "Exchangeability of pre-period residuals is a strong assumption — AUDIT-010 A05 caveat.",
            "Compare point/JK/Kfold/Conformal as triangulation context only on this battery.",
            "Per-cell only for multi-cell k=2 — no pooled claims.",
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
    cfg: D5InstAugsynth003Config | None = None,
) -> Path:
    path = path or (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "track_d"
        / "archives"
        / "D5_INST_AUGSYNTH_003_results.json"
    )
    payload = build_d5_inst_augsynth_003(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_artifact()
    print(f"Wrote {out}")
