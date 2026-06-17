"""DESIGN-COMBINATION-VALIDATION-EXECUTION-001 — design × estimator × inference execution.

Executes governed matrix rows against corrected tier-1 design baseline evidence.
Characterization only — no production promotion or downstream authorization.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import subprocess
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.methods.DID import DID
from panel_exp.methods.scm import AugSynthCVXPY, SyntheticControlCVXPY
from panel_exp.methods.tbr import TBR
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.utils.optional_deps import cvxpy_osqp_skip_reason
from panel_exp.validation.design_contract_builder_001 import _treated_units
from panel_exp.validation.track_d_d5_des_stat_tier1_001 import (
    ALL_WORLD_IDS,
    D5DesStatTier1Config,
    _world_context,
)
from panel_exp.validation.track_d_d5_des_stat_tier1_recharacterization_001 import (
    CORRECTED_DESIGNS,
    MULTICELL_DESIGNS,
    RecharConfig,
    _run_assignment,
    run_single_multicell,
    synthesize_panel,
    write_artifact_atomic,
)
from panel_exp.validation.track_d_d5_stat_tbr_agg_001 import _verify_aggregate_geometry

ARTIFACT_ID = "DESIGN-COMBINATION-VALIDATION-EXECUTION-001"
ARTIFACT_VERSION = "001"

CombinationStatus = Literal[
    "allowed_for_future_validation",
    "restricted_requires_contract_fields",
    "restricted_requires_statistical_validation",
    "adapter_required",
    "bridge_required",
    "blocked_due_to_geometry_mismatch",
    "blocked_due_to_readout_mismatch",
    "blocked_due_to_missing_contract_fields",
    "blocked_due_to_implementation_ambiguity",
    "blocked_for_pooled_claim",
    "helper_not_matrix_candidate",
    "not_evaluated",
    "characterized_no_promotion",
    "characterized_with_restrictions",
    "empirically_blocked",
    "compatible_point_only",
    "compatible_null_monitor_only",
    "compatible_per_cell_only",
    "inference_not_validated",
]

ExecutionVerdict = Literal[
    "design_combinations_characterized_no_promotion",
    "design_combinations_mixed_with_method_specific_restrictions",
    "design_combinations_partially_validated_remaining_blocks",
    "design_combinations_empirically_blocked",
    "design_combination_execution_inconclusive",
    "design_combination_execution_failed",
]

FORBIDDEN_FLAGS: dict[str, bool] = {
    "promotion_allowed": False,
    "trust_role_allowed": False,
    "calibration_signal_allowed": False,
    "mmm_allowed": False,
    "llm_allowed": False,
    "suitability_claim_allowed": False,
    "pooled_multicell_claim_allowed": False,
}

PROVISIONAL_THRESHOLDS: dict[str, Any] = {
    "coverage_deviation_max": 0.15,
    "type_i_error_tolerance": 0.10,
    "rmse_degradation_ratio_max": 2.0,
    "failure_rate_max": 0.35,
    "min_control_units": 3,
    "interval_width_inflation_max": 3.0,
    "note": "provisional_for_characterization_only",
}

DCM_ROWS: tuple[dict[str, Any], ...] = (
    {
        "combination_id": "DCM-001",
        "design_scope": "tier-1 corrected (DES-001–006)",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "SCM + UnitJackknife",
        "matrix_status_prior": "restricted_requires_contract_fields",
        "execution_lane": "A",
    },
    {
        "combination_id": "DCM-002",
        "design_scope": "tier-1 corrected",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "AugSynth point-only",
        "matrix_status_prior": "restricted_requires_contract_fields",
        "execution_lane": "A",
    },
    {
        "combination_id": "DCM-003",
        "design_scope": "tier-1 corrected",
        "geometry": "aggregate_two_row",
        "estimator_inference": "TBR aggregate point",
        "matrix_status_prior": "blocked_due_to_geometry_mismatch",
        "execution_lane": "B",
    },
    {
        "combination_id": "DCM-004",
        "design_scope": "tier-1 corrected",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "DID bootstrap",
        "matrix_status_prior": "blocked_due_to_geometry_mismatch",
        "execution_lane": "B",
    },
    {
        "combination_id": "DCM-005",
        "design_scope": "tier-1 corrected",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "TBRRidge KFold/BRB",
        "matrix_status_prior": "restricted_requires_statistical_validation",
        "execution_lane": "A",
        "optional_dep": True,
    },
    {
        "combination_id": "DCM-006",
        "design_scope": "DES-011 multicell corrected",
        "geometry": "multi_cell_per_cell",
        "estimator_inference": "MCELL per-cell SCM-JK",
        "matrix_status_prior": "restricted_requires_statistical_validation",
        "execution_lane": "D",
    },
    {
        "combination_id": "DCM-007",
        "design_scope": "DES-011 multicell",
        "geometry": "pooled_multi_cell",
        "estimator_inference": "Pooled SCM-JK / lift",
        "matrix_status_prior": "blocked_for_pooled_claim",
        "execution_lane": "D",
    },
    {
        "combination_id": "DCM-008",
        "design_scope": "DES-004 stratified corrected",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "SCM-JK (stratified lane)",
        "matrix_status_prior": "restricted_requires_contract_fields",
        "execution_lane": "A",
        "design_filter": "stratified_corrected",
    },
    {
        "combination_id": "DCM-009",
        "design_scope": "QuickBlock / MatchedPair",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "Block-aware inference",
        "matrix_status_prior": "adapter_required",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-010",
        "design_scope": "QuickBlock / MatchedPair",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "Unadjusted bootstrap",
        "matrix_status_prior": "blocked_due_to_readout_mismatch",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-011",
        "design_scope": "DES-009 TrimmedMatch",
        "geometry": "trimmed_geometry",
        "estimator_inference": "Trimmed-scope readout",
        "matrix_status_prior": "bridge_required",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-012",
        "design_scope": "DES-009 TrimmedMatch",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "Full-population SCM-JK",
        "matrix_status_prior": "bridge_required",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-013",
        "design_scope": "DES-010 Supergeo",
        "geometry": "supergeo",
        "estimator_inference": "Supergeo-scope readout",
        "matrix_status_prior": "bridge_required",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-014",
        "design_scope": "DES-010 Supergeo",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "Original-geo SCM-JK",
        "matrix_status_prior": "blocked_due_to_geometry_mismatch",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-015",
        "design_scope": "DES-014 Power/MDE",
        "geometry": "planning",
        "estimator_inference": "Experiment planning rank",
        "matrix_status_prior": "restricted_requires_contract_fields",
        "execution_lane": "E",
        "planning_only": True,
    },
    {
        "combination_id": "DCM-016",
        "design_scope": "DES-005 Thinning",
        "geometry": "unit_panel_single_cell",
        "estimator_inference": "SCM-JK",
        "matrix_status_prior": "blocked_due_to_implementation_ambiguity",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-017",
        "design_scope": "Bayesian future",
        "geometry": "TBD",
        "estimator_inference": "Posterior readout",
        "matrix_status_prior": "not_evaluated",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-018",
        "design_scope": "TROP future",
        "geometry": "TBD",
        "estimator_inference": "Triply robust",
        "matrix_status_prior": "not_evaluated",
        "execution_lane": "E",
    },
    {
        "combination_id": "DCM-019",
        "design_scope": "SARIMAX future",
        "geometry": "time_series_operator_geometry",
        "estimator_inference": "Forecast interval",
        "matrix_status_prior": "blocked_due_to_readout_mismatch",
        "execution_lane": "E",
    },
)

READOUT_MISMATCH_CASES: tuple[dict[str, str], ...] = (
    {
        "case_id": "readout_point_as_interval",
        "readout_semantics": "point_only",
        "claim_type": "causal_interval",
        "expected_block": "blocked_due_to_readout_mismatch",
    },
    {
        "case_id": "readout_forecast_as_causal",
        "readout_semantics": "forecast_interval",
        "claim_type": "causal_interval",
        "expected_block": "blocked_due_to_readout_mismatch",
    },
    {
        "case_id": "readout_directional_as_significance",
        "readout_semantics": "directional_sign",
        "claim_type": "significance_test",
        "expected_block": "blocked_due_to_readout_mismatch",
    },
    {
        "case_id": "readout_null_monitor_as_causal",
        "readout_semantics": "null_monitor",
        "claim_type": "causal_inference",
        "expected_block": "blocked_due_to_readout_mismatch",
    },
)


@dataclass
class DCVExecutionConfig:
    fast: bool = False
    train_length: int = 30
    test_length: int = 10
    alpha: float = 0.10
    min_control_units: int = 3
    percent_effects: tuple[float, ...] = (0.0, 0.08)
    seeds: tuple[int, ...] = (101, 202)
    replicates: int = 2
    include_contract_guardrail: bool = True
    baseline_design_label: str = "complete_randomization"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_head() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_repo_root(), text=True)
            .strip()
        )
    except Exception:
        return "unknown"


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


def _forbidden_flags() -> dict[str, bool]:
    return dict(FORBIDDEN_FLAGS)


def _world_ids(cfg: DCVExecutionConfig) -> tuple[str, ...]:
    if cfg.fast:
        return (
            "balanced_markets",
            "weak_donor_pool",
            "stratification_poor_strata_world",
            "rerandomization_selection_effect_world",
        )
    return ALL_WORLD_IDS


def _seeds(cfg: DCVExecutionConfig) -> tuple[int, ...]:
    return (101, 202) if cfg.fast else cfg.seeds


def _replicates(cfg: DCVExecutionConfig) -> int:
    return 1 if cfg.fast else cfg.replicates


def _percent_effects(cfg: DCVExecutionConfig) -> tuple[float, ...]:
    return (0.08,) if cfg.fast else cfg.percent_effects


def panel_from_assignment(
    wide: Any,
    assignment: dict[str, list[str]],
    *,
    n_pre: int,
    n_post: int,
) -> PanelDataset:
    treated = _treated_units(assignment)
    if not treated:
        raise ValueError("no_treated_units")
    all_units: list[str] = []
    for units in assignment.values():
        all_units.extend(units)
    all_units = sorted(set(all_units))
    end = n_pre + n_post
    return PanelDataset(
        wide.loc[all_units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(n_pre, end - 1) for _ in treated],
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


def evaluate_readout_compatibility(
    readout_semantics: str,
    claim_type: str,
) -> tuple[str, list[str]]:
    """Return (status, reason_codes)."""
    reasons: list[str] = []
    if readout_semantics == "point_only" and claim_type in ("causal_interval", "significance_test"):
        reasons.append("point_only_cannot_authorize_uncertainty")
        return "blocked_due_to_readout_mismatch", reasons
    if readout_semantics == "forecast_interval" and claim_type == "causal_interval":
        reasons.append("forecast_interval_not_causal")
        return "blocked_due_to_readout_mismatch", reasons
    if readout_semantics == "directional_sign" and claim_type == "significance_test":
        reasons.append("directional_sign_not_significance")
        return "blocked_due_to_readout_mismatch", reasons
    if readout_semantics == "null_monitor" and claim_type == "causal_inference":
        reasons.append("null_monitor_not_causal")
        return "blocked_due_to_readout_mismatch", reasons
    if claim_type == "pooled_multicell_causal":
        reasons.append("pooled_multicell_blocked")
        return "blocked_for_pooled_claim", reasons
    return "compatible_with_restrictions", reasons


def _geometry_id_for_assignment(assignment: dict[str, list[str]], n_test_grps: int) -> str:
    cell_keys = [k for k in assignment if k.startswith("test_")]
    if len(cell_keys) > 1 or n_test_grps > 1:
        return "multi_cell_per_cell"
    return "unit_panel_single_cell"


def _run_scm_jk(
    panel: PanelDataset,
    *,
    percent_effect: float,
    train_length: int,
    test_length: int,
    alpha: float,
) -> dict[str, Any]:
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {
            "estimator": "SCM+UnitJackknife",
            "callable_status": "skipped_optional_dep",
            "mechanical_success": False,
            "reason_codes": ["optional_dep_missing"],
            "exception_type": "optional_dep_missing",
            "exception_message": skip,
        }
    try:
        mean_value = _mean_treated_baseline(panel)
        injected = _inject_percent_effect(panel, percent_effect, mean_value)
        est = SyntheticControlCVXPY(inference="UnitJackKnife", alpha=alpha)
        est.run_analysis(injected)
        results = getattr(est, "results", {}) or {}
        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
        y_lo = np.asarray(results.get("y_lower"), dtype=float).reshape(-1)
        y_hi = np.asarray(results.get("y_upper"), dtype=float).reshape(-1)
        sl = slice(-test_length, None)
        effect = y[sl] - y_hat[sl]
        point = float(np.nanmean(effect)) if effect.size else float("nan")
        bias = point - percent_effect
        interval_present = y_lo.size > 0 and y_hi.size > 0
        contains = None
        if interval_present and np.all(np.isfinite(y_lo[sl])) and np.all(np.isfinite(y_hi[sl])):
            eff_lo = y[sl] - y_hi[sl]
            eff_hi = y[sl] - y_lo[sl]
            lo_m = float(np.nanmean(eff_lo))
            hi_m = float(np.nanmean(eff_hi))
            contains = bool(lo_m <= percent_effect <= hi_m)
        finite = y.size > 0 and np.all(np.isfinite(y[sl])) and np.all(np.isfinite(y_hat[sl]))
        return {
            "estimator": "SCM+UnitJackknife",
            "callable_status": "callable_pass" if finite else "callable_fail",
            "mechanical_success": bool(finite),
            "point_estimate": point,
            "bias": float(bias),
            "absolute_error": float(abs(bias)),
            "interval_present": interval_present,
            "interval_contains_truth": contains,
            "donor_count": int(injected.num_control_units),
            "readout_semantics": "causal_interval" if interval_present else "point_only",
            "reason_codes": [],
            "exception_type": None,
            "exception_message": None,
        }
    except Exception as exc:
        return {
            "estimator": "SCM+UnitJackknife",
            "callable_status": "callable_fail",
            "mechanical_success": False,
            "reason_codes": ["estimator_exception"],
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:500],
        }


def _run_augsynth_point(
    panel: PanelDataset,
    *,
    percent_effect: float,
    train_length: int,
    test_length: int,
) -> dict[str, Any]:
    skip = cvxpy_osqp_skip_reason()
    if skip:
        return {
            "estimator": "AugSynth point-only",
            "callable_status": "skipped_optional_dep",
            "mechanical_success": False,
            "reason_codes": ["optional_dep_missing"],
            "exception_type": "optional_dep_missing",
            "exception_message": skip,
        }
    try:
        mean_value = _mean_treated_baseline(panel)
        injected = _inject_percent_effect(panel, percent_effect, mean_value)
        est = AugSynthCVXPY()
        est.run_analysis(injected)
        results = getattr(est, "results", {}) or {}
        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        y_hat = np.asarray(results.get("y_hat"), dtype=float).reshape(-1)
        sl = slice(-test_length, None)
        effect = y[sl] - y_hat[sl]
        point = float(np.nanmean(effect)) if effect.size else float("nan")
        bias = point - percent_effect
        finite = y.size > 0 and np.all(np.isfinite(y[sl])) and np.all(np.isfinite(y_hat[sl]))
        claim_interval = evaluate_readout_compatibility("point_only", "causal_interval")
        return {
            "estimator": "AugSynth point-only",
            "callable_status": "callable_pass" if finite else "callable_fail",
            "mechanical_success": bool(finite),
            "point_estimate": point,
            "bias": float(bias),
            "absolute_error": float(abs(bias)),
            "interval_present": False,
            "readout_semantics": "point_only",
            "uncertainty_claim_blocked": claim_interval[0] == "blocked_due_to_readout_mismatch",
            "reason_codes": claim_interval[1] if not finite else [],
            "exception_type": None,
            "exception_message": None,
        }
    except Exception as exc:
        return {
            "estimator": "AugSynth point-only",
            "callable_status": "callable_fail",
            "mechanical_success": False,
            "reason_codes": ["estimator_exception"],
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:500],
        }


def _run_tbr_aggregate_check(panel: PanelDataset, *, test_length: int) -> dict[str, Any]:
    geometry_ok = _verify_aggregate_geometry(panel)
    if not geometry_ok:
        return {
            "estimator": "TBR aggregate point",
            "callable_status": "blocked_geometry",
            "mechanical_success": False,
            "geometry_compatible": False,
            "combination_status": "blocked_due_to_geometry_mismatch",
            "reason_codes": ["unit_panel_not_aggregate_two_row"],
        }
    try:
        est = TBR()
        est.run_analysis(panel)
        results = getattr(est, "results", {}) or {}
        y = np.asarray(results.get("y"), dtype=float).reshape(-1)
        finite = y.size > 0 and np.all(np.isfinite(y[-test_length:]))
        return {
            "estimator": "TBR aggregate point",
            "callable_status": "callable_pass" if finite else "callable_fail",
            "mechanical_success": bool(finite),
            "geometry_compatible": True,
            "combination_status": "characterized_with_restrictions",
            "reason_codes": [],
        }
    except Exception as exc:
        return {
            "estimator": "TBR aggregate point",
            "callable_status": "callable_fail",
            "mechanical_success": False,
            "geometry_compatible": True,
            "reason_codes": ["estimator_exception"],
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:500],
        }


def _run_did_bootstrap(
    panel: PanelDataset,
    *,
    percent_effect: float,
    train_length: int,
    test_length: int,
) -> dict[str, Any]:
    try:
        mean_value = _mean_treated_baseline(panel)
        injected = _inject_percent_effect(panel, percent_effect, mean_value)
        est = DID(inference="bootstrap")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            est.run_analysis(injected)
        results = getattr(est, "results", {}) or {}
        y_lo = results.get("y_lower")
        y_hi = results.get("y_upper")
        interval_present = y_lo is not None and y_hi is not None
        point = results.get("average_treatment_effect") or results.get("mean_post_period_att")
        point_f = float(point) if point is not None else float("nan")
        bias = point_f - percent_effect if np.isfinite(point_f) else float("nan")
        return {
            "estimator": "DID bootstrap",
            "callable_status": "callable_pass" if np.isfinite(point_f) else "callable_fail",
            "mechanical_success": bool(np.isfinite(point_f)),
            "geometry_compatible": True,
            "point_estimate": point_f,
            "bias": float(bias) if np.isfinite(bias) else None,
            "interval_present": interval_present,
            "readout_semantics": "causal_interval" if interval_present else "point_only",
            "combination_status": "characterized_with_restrictions",
            "reason_codes": ["did_unit_panel_mechanical_compat"],
        }
    except Exception as exc:
        return {
            "estimator": "DID bootstrap",
            "callable_status": "callable_fail",
            "mechanical_success": False,
            "geometry_compatible": False,
            "combination_status": "empirically_blocked",
            "reason_codes": ["estimator_exception"],
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)[:500],
        }


def _resolve_combination_status(
    dcm_id: str,
    *,
    design_ok: bool,
    geometry_compatible: bool | None,
    readout_blocked: bool,
    mechanical_success: bool,
    matrix_prior: str,
    lane: str,
    pooled_attempt: bool = False,
) -> str:
    if pooled_attempt:
        return "blocked_for_pooled_claim"
    if lane == "E":
        return matrix_prior
    if not design_ok:
        return "empirically_blocked"
    if geometry_compatible is False:
        return "blocked_due_to_geometry_mismatch"
    if readout_blocked:
        return "blocked_due_to_readout_mismatch"
    if not mechanical_success:
        return "inference_not_validated"
    if dcm_id == "DCM-002":
        return "compatible_point_only"
    if dcm_id == "DCM-006":
        return "compatible_per_cell_only"
    if dcm_id in ("DCM-001", "DCM-008"):
        return "characterized_with_restrictions"
    if dcm_id == "DCM-004":
        return "characterized_with_restrictions"
    if dcm_id == "DCM-003":
        return "blocked_due_to_geometry_mismatch"
    return "characterized_with_restrictions"


def _run_design_estimator_combo(
    *,
    dcm_id: str,
    design_spec: Any,
    world_id: str,
    seed: int,
    replicate: int,
    percent_effect: float,
    estimator: str,
    cfg: DCVExecutionConfig,
    tier1_cfg: D5DesStatTier1Config,
    rechar: RecharConfig,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "combination_id": dcm_id,
        "design_inventory_id": design_spec.design_inventory_id,
        "design_label": design_spec.label,
        "world_id": world_id,
        "seed": seed,
        "replicate": replicate,
        "percent_effect": percent_effect,
        "estimator_path": estimator,
        "lane": "A",
        **_forbidden_flags(),
    }
    world_ctx = _world_context(world_id, tier1_cfg)
    wide = synthesize_panel(world_ctx, seed + replicate)
    assignment, diag = _run_assignment(
        design_spec,
        wide,
        seed=seed + replicate,
        n_pre=world_ctx.n_pre,
        treatment_probability=world_ctx.treatment_probability,
        constraint_kwargs=world_ctx.constraint_kwargs,
        world_params=world_ctx.world_params,
        cfg=tier1_cfg,
    )
    if assignment is None:
        return {
            **base,
            "assignment_status": "failed",
            "combination_status": "empirically_blocked",
            "reason_codes": ["design_assignment_failed", diag.get("assignment_error", "unknown")],
            "mechanical_success": False,
        }
    geometry_id = _geometry_id_for_assignment(assignment, design_spec.n_test_grps)
    try:
        panel = panel_from_assignment(
            wide, assignment, n_pre=world_ctx.n_pre, n_post=world_ctx.n_post
        )
    except Exception as exc:
        return {
            **base,
            "assignment_status": "success",
            "geometry_id": geometry_id,
            "combination_status": "empirically_blocked",
            "reason_codes": ["panel_build_failed"],
            "exception_type": type(exc).__name__,
            "mechanical_success": False,
        }
    if panel.num_control_units < cfg.min_control_units:
        return {
            **base,
            "assignment_status": "success",
            "geometry_id": geometry_id,
            "combination_status": "empirically_blocked",
            "reason_codes": ["insufficient_control_units"],
            "mechanical_success": False,
            "donor_count": int(panel.num_control_units),
        }
    est_result: dict[str, Any]
    if estimator == "scm_jk":
        est_result = _run_scm_jk(
            panel,
            percent_effect=percent_effect,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
            alpha=cfg.alpha,
        )
    elif estimator == "augsynth_point":
        est_result = _run_augsynth_point(
            panel,
            percent_effect=percent_effect,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
        )
    elif estimator == "tbr_aggregate":
        est_result = _run_tbr_aggregate_check(panel, test_length=cfg.test_length)
    elif estimator == "did_bootstrap":
        est_result = _run_did_bootstrap(
            panel,
            percent_effect=percent_effect,
            train_length=cfg.train_length,
            test_length=cfg.test_length,
        )
    else:
        est_result = {
            "mechanical_success": False,
            "reason_codes": ["unknown_estimator"],
        }
    readout_blocked = False
    if dcm_id == "DCM-002" and est_result.get("uncertainty_claim_blocked"):
        readout_blocked = False  # point-only path: uncertainty claims blocked separately in lane C
    geometry_compatible = est_result.get("geometry_compatible")
    if geometry_compatible is None:
        geometry_compatible = geometry_id == "unit_panel_single_cell" or estimator != "tbr_aggregate"
    matrix_prior = next(r["matrix_status_prior"] for r in DCM_ROWS if r["combination_id"] == dcm_id)
    combo_status = _resolve_combination_status(
        dcm_id,
        design_ok=True,
        geometry_compatible=geometry_compatible if estimator == "tbr_aggregate" else True,
        readout_blocked=readout_blocked,
        mechanical_success=bool(est_result.get("mechanical_success")),
        matrix_prior=matrix_prior,
        lane="B" if estimator in ("tbr_aggregate", "did_bootstrap") else "A",
    )
    if estimator == "tbr_aggregate" and not est_result.get("geometry_compatible", True):
        combo_status = "blocked_due_to_geometry_mismatch"
    return {
        **base,
        "assignment_status": "success",
        "geometry_id": geometry_id,
        "design_diagnostics": {k: diag.get(k) for k in ("max_absolute_smd", "rerandomization_accepted")},
        "combination_status": combo_status,
        "mechanical_success": est_result.get("mechanical_success"),
        "estimator_result": est_result,
        "reason_codes": est_result.get("reason_codes", []),
    }


def _run_readout_controls() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in READOUT_MISMATCH_CASES:
        status, reasons = evaluate_readout_compatibility(
            case["readout_semantics"], case["claim_type"]
        )
        blocked = status == case["expected_block"]
        records.append(
            {
                "case_id": case["case_id"],
                "readout_semantics": case["readout_semantics"],
                "claim_type": case["claim_type"],
                "observed_status": status,
                "expected_status": case["expected_block"],
                "block_enforced": blocked,
                "reason_codes": reasons,
                "lane": "C",
            }
        )
    pooled_status, pooled_reasons = evaluate_readout_compatibility(
        "causal_interval", "pooled_multicell_causal"
    )
    records.append(
        {
            "case_id": "pooled_multicell_causal_claim",
            "readout_semantics": "causal_interval",
            "claim_type": "pooled_multicell_causal",
            "observed_status": pooled_status,
            "expected_status": "blocked_for_pooled_claim",
            "block_enforced": pooled_status == "blocked_for_pooled_claim",
            "reason_codes": pooled_reasons,
            "lane": "C",
        }
    )
    return records


def _run_lane_e_classifications() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in DCM_ROWS:
        if row["execution_lane"] != "E":
            continue
        status = row["matrix_status_prior"]
        if row.get("planning_only"):
            status = "restricted_requires_contract_fields"
        records.append(
            {
                "combination_id": row["combination_id"],
                "lane": "E",
                "execution_attempted": False,
                "combination_status": status,
                "reason_codes": ["prerequisite_not_met_lane_e_classification_only"],
                **_forbidden_flags(),
            }
        )
    return records


def _run_multicell_lane(cfg: DCVExecutionConfig, rechar: RecharConfig) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    mc_spec = next(
        s for s in MULTICELL_DESIGNS if s.label == "multicell_corrected" and s.lane == "multicell_per_cell_only"
    )
    worlds = ("balanced_three_cell",) if cfg.fast else ("balanced_three_cell", "shared_control_overload_world")
    for world_id in worlds:
        for n_units in (18, 20) if not cfg.fast else (18,):
            for rep in range(_replicates(cfg)):
                for seed in _seeds(cfg):
                    design_run = run_single_multicell(
                        mc_spec,
                        world_id=world_id,
                        n_units=n_units,
                        tp=0.35,
                        seed=seed,
                        replicate=rep,
                        rechar=rechar,
                    )
                    pooled_block = evaluate_readout_compatibility(
                        "causal_interval", "pooled_multicell_causal"
                    )
                    records.append(
                        {
                            "combination_id": "DCM-006",
                            "lane": "D",
                            "design_label": mc_spec.label,
                            "world_id": world_id,
                            "seed": seed,
                            "replicate": rep,
                            "assignment_status": design_run.get("assignment_status"),
                            "per_cell_only": True,
                            "combination_status": "compatible_per_cell_only",
                            "shared_control_burden": design_run.get("metrics", {}).get("n_control"),
                            "pooled_claim_blocked": pooled_block[0] == "blocked_for_pooled_claim",
                            **_forbidden_flags(),
                        }
                    )
                    records.append(
                        {
                            "combination_id": "DCM-007",
                            "lane": "D",
                            "design_label": mc_spec.label,
                            "world_id": world_id,
                            "seed": seed,
                            "replicate": rep,
                            "pooled_claim_attempt": True,
                            "combination_status": pooled_block[0],
                            "block_enforced": pooled_block[0] == "blocked_for_pooled_claim",
                            "reason_codes": pooled_block[1],
                            **_forbidden_flags(),
                        }
                    )
    return records


def _pairwise_comparisons(
    records: list[dict[str, Any]], *, baseline_label: str
) -> list[dict[str, Any]]:
    comparisons: list[dict[str, Any]] = []
    scm = [
        r
        for r in records
        if r.get("estimator_path") == "scm_jk"
        and r.get("assignment_status") == "success"
        and r.get("mechanical_success")
    ]
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for r in scm:
        key = (
            r["design_label"],
            r["world_id"],
            r.get("seed", 0),
            r.get("replicate", 0),
            r.get("percent_effect", 0.0),
        )
        by_key[key] = r
    designs = sorted({r["design_label"] for r in scm})
    if baseline_label not in designs:
        baseline_label = designs[0] if designs else baseline_label
    for other in designs:
        if other == baseline_label:
            continue
        deltas: list[float] = []
        for r in scm:
            if r["design_label"] != other:
                continue
            bkey = (baseline_label, r["world_id"], r["seed"], r["replicate"], r["percent_effect"])
            alt_key = (other, r["world_id"], r["seed"], r["replicate"], r["percent_effect"])
            base_rec = by_key.get(bkey)
            alt_rec = by_key.get(alt_key)
            if not base_rec or not alt_rec:
                continue
            b_err = (base_rec.get("estimator_result") or {}).get("absolute_error")
            a_err = (alt_rec.get("estimator_result") or {}).get("absolute_error")
            if b_err is not None and a_err is not None:
                deltas.append(float(a_err) - float(b_err))
        if deltas:
            comparisons.append(
                {
                    "comparison": f"{baseline_label}_vs_{other}",
                    "estimator": "SCM+UnitJackknife",
                    "paired_worlds": len(deltas),
                    "mean_absolute_error_delta": float(np.mean(deltas)),
                    "median_absolute_error_delta": float(np.median(deltas)),
                }
            )
    return comparisons


def execute_combination_validation(cfg: DCVExecutionConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    t0 = time.perf_counter()
    tier1_cfg = D5DesStatTier1Config(fast=cfg.fast)
    rechar = RecharConfig(fast=cfg.fast, include_contract_guardrail=cfg.include_contract_guardrail)
    records: list[dict[str, Any]] = []
    worlds = _world_ids(cfg)
    seeds = _seeds(cfg)
    reps = _replicates(cfg)
    effects = _percent_effects(cfg)

    for design_spec in CORRECTED_DESIGNS:
        if design_spec.lane != "single_cell_tier1":
            continue
        for world_id in worlds:
            for pe in effects:
                for rep in range(reps):
                    for seed in seeds:
                        combos: list[tuple[str, str]] = [("DCM-001", "scm_jk"), ("DCM-002", "augsynth_point")]
                        if design_spec.label == "stratified_corrected":
                            combos.append(("DCM-008", "scm_jk"))
                        for dcm_id, est in combos:
                            records.append(
                                _run_design_estimator_combo(
                                    dcm_id=dcm_id,
                                    design_spec=design_spec,
                                    world_id=world_id,
                                    seed=seed,
                                    replicate=rep,
                                    percent_effect=pe,
                                    estimator=est,
                                    cfg=cfg,
                                    tier1_cfg=tier1_cfg,
                                    rechar=rechar,
                                )
                            )

    # Lane B geometry controls — one design, subset of worlds
    b_worlds = worlds[:2] if cfg.fast else worlds[:6]
    ref_design = next(s for s in CORRECTED_DESIGNS if s.label == "complete_randomization")
    for world_id in b_worlds:
        for rep in range(reps):
            for seed in seeds:
                for dcm_id, est in (("DCM-003", "tbr_aggregate"), ("DCM-004", "did_bootstrap")):
                    records.append(
                        _run_design_estimator_combo(
                            dcm_id=dcm_id,
                            design_spec=ref_design,
                            world_id=world_id,
                            seed=seed,
                            replicate=rep,
                            percent_effect=effects[0],
                            estimator=est,
                            cfg=cfg,
                            tier1_cfg=tier1_cfg,
                            rechar=rechar,
                        )
                    )

    records.extend(_run_readout_controls())
    records.extend(_run_multicell_lane(cfg, rechar))
    records.extend(_run_lane_e_classifications())

    elapsed = time.perf_counter() - t0
    runtime = {
        "total_records": len(records),
        "elapsed_seconds": round(elapsed, 3),
        "fast_mode": cfg.fast,
        "worlds": list(worlds),
        "seeds": list(seeds),
        "replicates": reps,
        "percent_effects": list(effects),
    }
    return records, runtime


def _aggregate_combination_results(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for row in DCM_ROWS:
        cid = row["combination_id"]
        subset = [r for r in records if r.get("combination_id") == cid]
        if not subset:
            continue
        mech = [r for r in subset if r.get("mechanical_success") is True]
        blocked = [r for r in subset if str(r.get("combination_status", "")).startswith("blocked")]
        statuses = sorted({str(r.get("combination_status")) for r in subset})
        out[cid] = {
            "n_records": len(subset),
            "n_mechanical_success": len(mech),
            "n_blocked": len(blocked),
            "failure_rate": round(1 - len(mech) / max(len(subset), 1), 4),
            "observed_statuses": statuses,
            "matrix_status_prior": row["matrix_status_prior"],
            "execution_lane": row["execution_lane"],
        }
    return out


def _failure_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [
        r
        for r in records
        if r.get("assignment_status") == "failed"
        or r.get("mechanical_success") is False
        or str(r.get("combination_status", "")).startswith("blocked")
    ]
    reason_counts: dict[str, int] = {}
    for r in failed:
        for code in r.get("reason_codes") or []:
            reason_counts[str(code)] = reason_counts.get(str(code), 0) + 1
    return {
        "n_failed_or_blocked": len(failed),
        "reason_code_counts": reason_counts,
        "preserved_failed_runs": True,
    }


def derive_verdict(aggregate: dict[str, Any], readout: list[dict[str, Any]]) -> ExecutionVerdict:
    dcm001 = aggregate.get("DCM-001", {})
    if not dcm001:
        return "design_combination_execution_inconclusive"
    if dcm001.get("n_mechanical_success", 0) == 0:
        return "design_combination_execution_failed"
    readout_ok = all(r.get("block_enforced") for r in readout if "block_enforced" in r)
    if not readout_ok:
        return "design_combination_execution_inconclusive"
    dcm003 = aggregate.get("DCM-003", {})
    if dcm003.get("n_blocked", 0) == dcm003.get("n_records", 0) and dcm001.get("n_mechanical_success", 0) > 0:
        return "design_combinations_mixed_with_method_specific_restrictions"
    blocked_remaining = sum(
        1
        for v in aggregate.values()
        if any(s.startswith("blocked") for s in v.get("observed_statuses", []))
    )
    if blocked_remaining >= 8:
        return "design_combinations_partially_validated_remaining_blocks"
    return "design_combinations_mixed_with_method_specific_restrictions"


def build_payload(cfg: DCVExecutionConfig) -> dict[str, Any]:
    records, runtime = execute_combination_validation(cfg)
    readout_records = [r for r in records if r.get("lane") == "C"]
    aggregate = _aggregate_combination_results(records)
    pairwise = _pairwise_comparisons(records, baseline_label=cfg.baseline_design_label)
    verdict = derive_verdict(aggregate, readout_records)
    return {
        "artifact_id": ARTIFACT_ID,
        "artifact_version": ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_head(),
        "config": {
            "fast": cfg.fast,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "provisional_thresholds": PROVISIONAL_THRESHOLDS,
            "baseline_design": cfg.baseline_design_label,
            "design_baseline_artifact": "D5-DES-STAT-TIER1-RECHARACTERIZATION-001",
            "legacy_tier1_not_default": True,
        },
        "matrix_rows": [dict(r) for r in DCM_ROWS],
        "designs": [s.label for s in CORRECTED_DESIGNS if s.lane == "single_cell_tier1"],
        "estimators": ["SCM+UnitJackknife", "AugSynth point-only", "TBR aggregate", "DID bootstrap"],
        "inference_paths": ["UnitJackknife", "point_only", "bootstrap", "blocked_geometry"],
        "worlds": list(_world_ids(cfg)),
        "run_counts": runtime,
        "run_records": records,
        "aggregate_results": aggregate,
        "combination_results": aggregate,
        "geometry_results": [r for r in records if r.get("estimator_path") in ("tbr_aggregate", "did_bootstrap")],
        "readout_results": readout_records,
        "pairwise_comparisons": pairwise,
        "failure_summary": _failure_summary(records),
        "reason_code_summary": _failure_summary(records)["reason_code_counts"],
        "contract_guardrail_summary": {
            "contract_fields_evaluated": cfg.include_contract_guardrail,
            "downstream_authorization": False,
        },
        "multicell_summary": {
            "per_cell_lane_separated": True,
            "pooled_claims_blocked": all(
                r.get("block_enforced") or r.get("pooled_claim_blocked")
                for r in records
                if r.get("combination_id") in ("DCM-006", "DCM-007")
            ),
            "legacy_baseline_not_default": True,
        },
        "promotion_summary": {**FORBIDDEN_FLAGS, "production_ready": False},
        "verdict": verdict,
        "limitations": [
            "characterization_only_no_promotion",
            "provisional_thresholds_not_production",
            "inference_coverage_not_fully_validated",
            "rerandomization_selection_effects_restricted",
            "pooled_multicell_causal_claims_blocked",
        ],
    }


def build_summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact committed summary — excludes per-run records."""
    return {
        "artifact_id": payload["artifact_id"],
        "artifact_version": payload["artifact_version"],
        "generated_at": payload["generated_at"],
        "git_commit": payload["git_commit"],
        "config": payload["config"],
        "matrix_rows": payload["matrix_rows"],
        "designs": payload["designs"],
        "estimators": payload["estimators"],
        "inference_paths": payload["inference_paths"],
        "worlds": payload["worlds"],
        "run_counts": payload["run_counts"],
        "aggregate_results": payload["aggregate_results"],
        "combination_results": payload["combination_results"],
        "geometry_results": [
            {
                "combination_id": r.get("combination_id"),
                "design_label": r.get("design_label"),
                "world_id": r.get("world_id"),
                "combination_status": r.get("combination_status"),
                "geometry_id": r.get("geometry_id"),
            }
            for r in payload["geometry_results"][:50]
        ],
        "readout_results": payload["readout_results"],
        "pairwise_comparisons": payload["pairwise_comparisons"],
        "failure_summary": payload["failure_summary"],
        "reason_code_summary": payload["reason_code_summary"],
        "contract_guardrail_summary": payload["contract_guardrail_summary"],
        "multicell_summary": payload["multicell_summary"],
        "promotion_summary": payload["promotion_summary"],
        "verdict": payload["verdict"],
        "limitations": payload["limitations"],
        "matrix_row_updates": _matrix_row_updates(payload["aggregate_results"]),
    }


def _matrix_row_updates(aggregate: dict[str, Any]) -> dict[str, dict[str, str]]:
    updates: dict[str, dict[str, str]] = {}
    for cid, agg in aggregate.items():
        prior = agg.get("matrix_status_prior", "")
        if agg.get("n_mechanical_success", 0) > 0 and prior == "restricted_requires_statistical_validation":
            updates[cid] = {
                "prior_status": prior,
                "executed_status": "characterized_with_restrictions",
                "evidence": ARTIFACT_ID,
            }
        elif agg.get("n_blocked", 0) == agg.get("n_records", 0) and agg.get("n_records", 0) > 0:
            updates[cid] = {
                "prior_status": prior,
                "executed_status": "empirically_blocked",
                "evidence": ARTIFACT_ID,
            }
        elif agg.get("n_mechanical_success", 0) > 0:
            updates[cid] = {
                "prior_status": prior,
                "executed_status": "characterized_with_restrictions",
                "evidence": ARTIFACT_ID,
            }
    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description=ARTIFACT_ID)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument(
        "--output-local",
        type=Path,
        default=Path("/tmp/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_results.json"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=_repo_root()
        / "docs/track_d/archives/DESIGN_COMBINATION_VALIDATION_EXECUTION_001_summary.json",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    cfg = DCVExecutionConfig(fast=args.fast)
    payload = build_payload(cfg)
    summary = build_summary_payload(payload)
    write_artifact_atomic(args.output_local, _json_safe(payload), overwrite=args.overwrite)
    write_artifact_atomic(args.summary_output, _json_safe(summary), overwrite=args.overwrite)
    print(json.dumps({"verdict": payload["verdict"], "records": payload["run_counts"]["total_records"]}))


if __name__ == "__main__":
    main()
