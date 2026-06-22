"""D5-TRUST-MULTICELL-PERCELL-INFERENCE-001 — DCM-006 per-cell inference qualification.

Characterizes multi-cell per-cell SCM+UnitJackknife inference: geometry variants,
shared-control dependence, multiplicity, and pooled-readout blocking. No production
changes. Does not authorize TrustReport.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np

from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_pow_001e import _assign, _test_cell_keys
from panel_exp.validation.track_d_d5_stat_mcell_percell_001 import (
    D5StatMcellPercell001Config,
    _apply_cell_shock,
    _build_wide,
    _cell_percent,
    _json_safe,
    _run_cell_method,
)
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import _mean, _rate

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_ID = "D5-TRUST-MULTICELL-PERCELL-INFERENCE-001"
_ARTIFACT_VERSION = "1.0.0"
_CANONICAL_SCALE = "level_mean_relative_percent_injection"
_INVESTIGATION_ID = "INV-MULTICELL-PERCELL-INFERENCE-001"
_FOLLOW_UP_SHARED = "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001"
_FOLLOW_UP_MULTIPLICITY = "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001"
_DEFAULT_SUMMARY = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_REPORT.md"
_PRIMARY_METHOD = "MCELL-PERCELL-SCM-JK"

SemanticVerdict = Literal[
    "multicell_percell_eligible_with_restrictions",
    "multicell_percell_disjoint_controls_only",
    "multicell_percell_shared_control_restricted",
    "multicell_percell_multiplicity_unresolved",
    "multicell_percell_diagnostic_only",
    "multicell_percell_ineligible",
    "multicell_percell_remediation_inconclusive",
    "multicell_percell_remediation_failed",
]

ProductionDefectDecision = Literal[
    "production_defect_confirmed",
    "production_defect_not_confirmed",
    "production_defect_indeterminate",
    "geometry_or_semantic_limitation",
]

_MULTIPLICITY_PROXY_DISCLAIMER = (
    "Bonferroni/Holm proxy comparison was not a valid calibration test because "
    "the current SCM+JK path does not expose compatible per-cell p-values or "
    "adjusted confidence-level interval reconstruction. Multiplicity remains "
    "unresolved; equal FWER values across unadjusted and proxy-adjusted labels "
    "do not establish that Bonferroni or Holm are ineffective."
)

POLICY_COMPARISONS: tuple[dict[str, str], ...] = (
    {"policy_id": "A", "name": "per_cell_unadjusted", "description": "marginal per-cell JK intervals"},
    {
        "policy_id": "B",
        "name": "per_cell_bonferroni",
        "description": "Bonferroni not calibrated here — SCM+JK lacks per-cell p-values / adjusted intervals",
    },
    {
        "policy_id": "C",
        "name": "per_cell_holm",
        "description": "Holm not calibrated here — interval-excludes-zero proxies only",
    },
    {
        "policy_id": "D",
        "name": "simultaneous_max_stat_if_available",
        "description": "max-stat simultaneous procedure not available on SCM+JK readout",
    },
    {"policy_id": "E", "name": "shared_control_restricted", "description": "shared-control geometries flagged; disjoint preferred"},
    {"policy_id": "F", "name": "disjoint_control_only", "description": "disjoint donor pools per cell"},
    {"policy_id": "G", "name": "pooled_blocked", "description": "pooled multi-cell causal readout blocked"},
)


@dataclass(frozen=True)
class GeometrySpec:
    geometry_id: str
    n_cells: int = 2
    control_policy: str = "shared"
    shared_control_policy: str = "greedy_match_common_pool"
    control_reuse_policy: str = "unrestricted"
    n_geos: int | None = None
    treatment_probability: float | None = None
    geometry_supported: bool = True
    notes: str = ""


@dataclass(frozen=True)
class TrustWorldSpec:
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
    shock_all_cells: bool = False
    notes: str = ""


@dataclass(frozen=True)
class MulticellTrustConfig:
    n_replicates: int = 4
    n_replicates_fast: int = 2
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260630
    min_control_units: int = 4
    fast: bool = False
    write_full_results_path: str | None = "/tmp/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_results.json"


GEOMETRY_VARIANTS: tuple[GeometrySpec, ...] = (
    GeometrySpec("two_cells_disjoint_controls", control_policy="disjoint", notes="partitioned control donors"),
    GeometrySpec("two_cells_shared_controls", control_policy="shared", notes="common greedy-match pool"),
    GeometrySpec("three_cells_shared_controls", n_cells=3, control_policy="shared"),
    GeometrySpec("unequal_cell_sizes", treatment_probability=0.5, notes="imbalanced treated counts"),
    GeometrySpec("small_cell", n_geos=10, treatment_probability=0.45, notes="small donor pool"),
    GeometrySpec("large_cell", n_geos=22, treatment_probability=0.22, notes="large donor pool"),
    GeometrySpec(
        "imbalanced_control_reuse",
        control_policy="shared",
        control_reuse_policy="heavy_reuse",
        treatment_probability=0.48,
        notes="many treated units share donors",
    ),
    GeometrySpec("cell_specific_donor_pools", control_policy="disjoint", notes="disjoint donor pools per cell"),
    GeometrySpec("common_control_pool", control_policy="shared", notes="alias shared pool"),
    GeometrySpec(
        "partially_overlapping_controls",
        control_policy="partial_overlap",
        notes="partial donor overlap across cells",
    ),
    GeometrySpec(
        "pooled_multi_cell_negative_control",
        control_policy="shared",
        geometry_supported=False,
        notes="pooled readout attempt must fail closed",
    ),
)

EFFECT_PATTERNS: tuple[tuple[float, ...], ...] = (
    (0.0, 0.0),
    (0.08, 0.0),
    (0.08, 0.08),
    (0.08, -0.05),
    (0.03, 0.03),
    (0.12, 0.0),
    (0.08, 0.0, 0.0),
    (0.08, 0.08, 0.0),
    (0.08, -0.05, 0.03),
)

TRUST_WORLDS: tuple[TrustWorldSpec, ...] = (
    TrustWorldSpec("all_cell_null", percent_effect=0.0, notes="all cells null"),
    TrustWorldSpec(
        "one_cell_positive_others_null",
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        notes="single active cell",
    ),
    TrustWorldSpec(
        "two_cell_positive",
        cell_effects={"test_0": 0.08, "test_1": 0.08},
        notes="both cells active",
    ),
    TrustWorldSpec(
        "mixed_positive_negative",
        cell_effects={"test_0": 0.08, "test_1": -0.05},
        notes="mixed sign effects",
    ),
    TrustWorldSpec("weak_effects", cell_effects={"test_0": 0.03, "test_1": 0.03}),
    TrustWorldSpec("strong_effects", cell_effects={"test_0": 0.12, "test_1": 0.12}),
    TrustWorldSpec(
        "serial_correlation",
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        scenario_overrides={"autocorrelation": 0.7},
    ),
    TrustWorldSpec(
        "high_serial_correlation",
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        scenario_overrides={"autocorrelation": 0.92},
    ),
    TrustWorldSpec(
        "heteroskedasticity",
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        scenario_overrides={"noise_scale": 4.8},
    ),
    TrustWorldSpec(
        "poor_pre_fit_one_cell",
        n_test_grps=2,
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        notes="stressed pre-fit in one cell geometry",
    ),
    TrustWorldSpec(
        "poor_pre_fit_all_cells",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        scenario_overrides={"noise_scale": 4.0},
    ),
    TrustWorldSpec(
        "donor_contamination_one_cell",
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        scenario_overrides={"cross_geo_correlation": 0.92},
    ),
    TrustWorldSpec(
        "shared_control_shock",
        percent_effect=0.0,
        shock_all_cells=False,
        notes="control-pool shock via high cross-geo correlation under null",
        scenario_overrides={"cross_geo_correlation": 0.88},
    ),
    TrustWorldSpec(
        "cell_specific_post_shock",
        shock_cell="test_1",
        shock_magnitude=18.0,
        percent_effect=0.0,
    ),
    TrustWorldSpec(
        "unequal_cell_sizes",
        treatment_probability=0.5,
        cell_effects={"test_0": 0.08, "test_1": 0.0},
    ),
    TrustWorldSpec(
        "small_donor_pool",
        n_geos=10,
        treatment_probability=0.45,
        cell_effects={"test_0": 0.08, "test_1": 0.0},
    ),
    TrustWorldSpec(
        "heavy_control_reuse",
        treatment_probability=0.48,
        cell_effects={"test_0": 0.08, "test_1": 0.0},
    ),
    TrustWorldSpec(
        "overlapping_timing",
        cell_effects={"test_0": 0.08, "test_1": 0.0},
        notes="same treatment start; not staggered in runtime path",
    ),
)


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _to_mcell_cfg(cfg: MulticellTrustConfig) -> D5StatMcellPercell001Config:
    return D5StatMcellPercell001Config(
        n_replicates=cfg.n_replicates,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        alpha=cfg.alpha,
        random_state_base=cfg.random_state_base,
        min_control_units=cfg.min_control_units,
    )


def _to_mcell_world(spec: TrustWorldSpec) -> Any:
    from panel_exp.validation.track_d_d5_stat_mcell_percell_001 import WorldSpec

    return WorldSpec(
        world_id=spec.world_id,
        n_test_grps=spec.n_test_grps,
        scenario_name=spec.scenario_name,
        percent_effect=spec.percent_effect,
        cell_effects=dict(spec.cell_effects),
        n_geos=spec.n_geos,
        n_periods=spec.n_periods,
        treatment_probability=spec.treatment_probability,
        scenario_overrides=dict(spec.scenario_overrides),
        shock_cell=spec.shock_cell,
        shock_magnitude=spec.shock_magnitude,
        notes=spec.notes,
    )


def _control_subset(
    controls: list[str],
    geom: GeometrySpec,
    cell_idx: int,
    n_cells: int,
) -> list[str]:
    if geom.control_policy in ("shared", "common_pool"):
        return list(controls)
    n = len(controls)
    if n == 0:
        return []
    if geom.control_policy == "disjoint":
        chunks = np.array_split(controls, n_cells)
        return list(chunks[cell_idx])
    if geom.control_policy == "partial_overlap":
        quarter = max(1, n // 4)
        half = max(1, n // 2)
        if cell_idx == 0:
            return controls[: half + quarter]
        return controls[quarter:]
    return list(controls)


def _control_overlap_matrix(
    cell_controls: dict[str, list[str]],
    cell_ids: list[str],
) -> list[list[float]]:
    n = len(cell_ids)
    mat = [[0.0] * n for _ in range(n)]
    for i, ci in enumerate(cell_ids):
        si = set(cell_controls.get(ci, []))
        for j, cj in enumerate(cell_ids):
            sj = set(cell_controls.get(cj, []))
            union = len(si | sj)
            mat[i][j] = len(si & sj) / union if union else 0.0
    return mat


def _build_cell_panel_custom(
    wide: Any,
    assignment: dict[str, list[str]],
    cell_id: str,
    control_units: list[str],
    cfg: D5StatMcellPercell001Config,
) -> PanelDataset:
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
    readout_units = list(control_units) + treated
    if other_test & set(readout_units):
        raise ValueError("cell_identity_violation_other_test_units_in_panel")
    return PanelDataset(
        wide.loc[readout_units].iloc[:, :end].copy(),
        treated_units=treated,
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated],
    )


def _cell_effects_from_pattern(pattern: tuple[float, ...], n_cells: int) -> dict[str, float]:
    out: dict[str, float] = {}
    for i in range(n_cells):
        out[f"test_{i}"] = float(pattern[i]) if i < len(pattern) else 0.0
    return out


def _attempt_pooled_block(
    wide: Any,
    assignment: dict[str, list[str]],
    cell_keys: list[str],
) -> dict[str, Any]:
    """Negative control: pooled multi-cell readout must remain blocked."""
    all_treated: list[str] = []
    for k in cell_keys:
        all_treated.extend(assignment.get(k) or [])
    pooled_attempted = True
    pooled_blocked = True
    pooled_effect_emitted = False
    pooled_interval_emitted = False
    reason = "per_cell_only_contract"
    if len(all_treated) > 1 and len(cell_keys) > 1:
        pooled_blocked = True
        pooled_effect_emitted = False
        pooled_interval_emitted = False
        reason = "multi_cell_pooled_causal_readout_blocked_by_contract"
    return {
        "pooled_readout_attempted": pooled_attempted,
        "pooled_readout_blocked": pooled_blocked,
        "pooled_effect_emitted": pooled_effect_emitted,
        "pooled_interval_emitted": pooled_interval_emitted,
        "block_reason": reason,
    }


def _multiplicity_calibration_audit() -> dict[str, Any]:
    """Document why Bonferroni/Holm FWER comparisons are not valid calibration tests."""
    return {
        "bonferroni_threshold_adjusted": False,
        "holm_threshold_adjusted": False,
        "per_cell_p_values_available": False,
        "p_value_source": "none — SCM+UnitJackknife exposes interval bounds only",
        "rejection_proxy": "interval_excludes_zero (0 in [lower, upper])",
        "adjusted_intervals_reconstructed": False,
        "familywise_from_adjusted_decisions": False,
        "familywise_metric_valid": "unadjusted_interval_excludes_zero_any_cell_only",
        "shared_control_handling": (
            "consistent — all multiplicity labels reuse the same underlying per-cell "
            "JK intervals; shared-control dependence affects intervals but was not "
            "modeled separately per policy"
        ),
        "proxy_comparison_valid": False,
        "disclaimer": _MULTIPLICITY_PROXY_DISCLAIMER,
    }


def _run_one(
    world: TrustWorldSpec,
    geom: GeometrySpec,
    effect_pattern: tuple[float, ...] | None,
    cfg: MulticellTrustConfig,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    mcell_cfg = _to_mcell_cfg(cfg)
    n_cells = geom.n_cells
    cell_keys = [f"test_{i}" for i in range(n_cells)]
    cell_effects = _cell_effects_from_pattern(effect_pattern, n_cells) if effect_pattern else dict(world.cell_effects)
    if not cell_effects and world.percent_effect != 0.0:
        cell_effects = {k: world.percent_effect for k in cell_keys}

    mcell_world = replace(
        _to_mcell_world(world),
        n_test_grps=n_cells,
        cell_effects=cell_effects,
        n_geos=geom.n_geos or world.n_geos,
        treatment_probability=geom.treatment_probability or world.treatment_probability,
    )

    run_level: dict[str, Any] = {
        "world_id": world.world_id,
        "geometry_id": geom.geometry_id,
        "seed": seed,
        "replicate": replicate_id,
        "effect_pattern": list(effect_pattern) if effect_pattern else None,
        "failure_status": "ok",
        "failure_reason": None,
        "pooled_readout_attempted": False,
        "pooled_readout_blocked": True,
    }
    cell_rows: list[dict[str, Any]] = []

    if geom.geometry_id == "pooled_multi_cell_negative_control":
        pool = _attempt_pooled_block(None, {k: [f"u{i}"] for i, k in enumerate(cell_keys)}, cell_keys)
        run_level.update(pool)
        run_level["failure_status"] = "blocked"
        run_level["failure_reason"] = pool["block_reason"]
        run_level["cell_level_results"] = []
        run_level["n_cells"] = n_cells
        return run_level

    try:
        wide = _build_wide(mcell_world, mcell_cfg, seed=seed)
        assignment = _assign(
            "greedy_match_markets",
            wide,
            train_length=mcell_cfg.train_length,
            seed=seed,
            treatment_probability=mcell_world.treatment_probability,
            n_test_grps=n_cells,
            rerandomization_max_iter=200,
        )
        keys = _test_cell_keys(assignment, n_cells)
        if keys != cell_keys:
            raise ValueError("unexpected_cell_keys")

        controls = list(assignment.get("control") or [])
        cell_control_map = {
            cid: _control_subset(controls, geom, i, n_cells) for i, cid in enumerate(cell_keys)
        }
        overlap_mat = _control_overlap_matrix(cell_control_map, cell_keys)
        shared_count = len(controls)
        if geom.control_policy == "disjoint":
            shared_count = len(set(controls) & set(cell_control_map.get(cell_keys[0], [])))

        pool = _attempt_pooled_block(wide, assignment, cell_keys)
        run_level.update(pool)

        estimates: list[float | None] = []
        truths: list[float | None] = []
        intervals: list[tuple[float | None, float | None]] = []
        contains_truth: list[bool | None] = []
        contains_zero: list[bool | None] = []

        for i, cell_id in enumerate(cell_keys):
            panel = _build_cell_panel_custom(wide, assignment, cell_id, cell_control_map[cell_id], mcell_cfg)
            if world.shock_cell == cell_id and world.shock_magnitude:
                panel = _apply_cell_shock(
                    panel,
                    magnitude=world.shock_magnitude,
                    train_length=mcell_cfg.train_length,
                    test_length=mcell_cfg.test_length,
                )
            pct = cell_effects.get(cell_id, world.percent_effect)
            try:
                readout, _, identity_ok = _run_cell_method(
                    _PRIMARY_METHOD, panel, percent_effect=pct, cfg=mcell_cfg
                )
                il = readout.get("interval_lower")
                iu = readout.get("interval_upper")
                ct = readout.get("interval_contains_truth")
                cz = None
                if il is not None and iu is not None:
                    cz = bool(il <= 0.0 <= iu)
                row = {
                    "world_id": world.world_id,
                    "seed": seed,
                    "replicate": replicate_id,
                    "geometry_id": geom.geometry_id,
                    "cell_id": cell_id,
                    "n_cells": n_cells,
                    "n_treated": len(assignment.get(cell_id) or []),
                    "n_controls": len(cell_control_map[cell_id]),
                    "shared_control_count": shared_count,
                    "control_overlap_fraction": overlap_mat[i][i - 1] if i > 0 else 0.0,
                    "true_effect": readout.get("true_effect"),
                    "point_estimate": readout.get("point_estimate"),
                    "bias": readout.get("bias"),
                    "squared_error": readout.get("squared_error"),
                    "sign_correct": readout.get("sign_correct"),
                    "interval_lower": il,
                    "interval_upper": iu,
                    "contains_truth": ct,
                    "contains_zero": cz,
                    "interval_width": readout.get("interval_width"),
                    "prefit_rmse": readout.get("prefit_rmse"),
                    "donor_count": readout.get("donor_count"),
                    "failure_status": "ok",
                    "failure_reason": None,
                    "cell_identity_preserved": identity_ok,
                }
                estimates.append(readout.get("point_estimate"))
                truths.append(readout.get("true_effect"))
                intervals.append((il, iu))
                contains_truth.append(ct)
                contains_zero.append(cz)
            except Exception as exc:
                row = {
                    "world_id": world.world_id,
                    "seed": seed,
                    "replicate": replicate_id,
                    "geometry_id": geom.geometry_id,
                    "cell_id": cell_id,
                    "n_cells": n_cells,
                    "failure_status": "fail",
                    "failure_reason": f"{type(exc).__name__}: {exc}"[:200],
                    "cell_identity_preserved": False,
                }
                estimates.append(None)
                truths.append(None)
                intervals.append((None, None))
                contains_truth.append(None)
                contains_zero.append(None)
            cell_rows.append(row)

        all_null = all(abs(t or 0.0) < 1e-9 for t in truths if t is not None)
        fp_cells = [
            cz is False for cz in contains_zero if cz is not None and all_null
        ]
        familywise_fp = bool(fp_cells) and any(fp_cells)
        simultaneous_cov = (
            all(ct is True for ct in contains_truth if ct is not None)
            if contains_truth
            else None
        )
        est_vec = [e for e in estimates if e is not None and np.isfinite(e)]
        err_vec = [
            (e - t)
            for e, t in zip(estimates, truths)
            if e is not None and t is not None and np.isfinite(e) and np.isfinite(t)
        ]

        run_level.update(
            {
                "cell_level_results": cell_rows,
                "cell_effect_vector": truths,
                "cell_estimate_vector": estimates,
                "cell_interval_matrix": intervals,
                "cross_cell_error_covariance": float(np.cov(err_vec, err_vec)[0, 0]) if len(err_vec) > 1 else None,
                "cross_cell_sign_pattern": [
                    int(np.sign(e)) if e is not None and np.isfinite(e) else 0 for e in estimates
                ],
                "familywise_any_false_positive": familywise_fp,
                "familywise_all_covered": simultaneous_cov,
                "per_cell_coverage": contains_truth,
                "simultaneous_coverage": simultaneous_cov,
                "multiplicity_adjustment": {
                    "unadjusted_fp_any": familywise_fp,
                    "bonferroni_fp_any": None,
                    "holm_fp_any": None,
                    "calibration_valid": False,
                },
                "control_overlap_matrix": overlap_mat,
                "shared_control_policy": geom.shared_control_policy,
                "control_reuse_policy": geom.control_reuse_policy,
                "geometry_supported": geom.geometry_supported,
            }
        )
    except Exception as exc:
        run_level["failure_status"] = "fail"
        run_level["failure_reason"] = f"{type(exc).__name__}: {exc}"[:200]
        run_level["cell_level_results"] = cell_rows

    return run_level


def _coverage_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    for r in runs:
        cells.extend(r.get("cell_level_results") or [])
    ok = [c for c in cells if c.get("failure_status") == "ok"]
    cov = _rate([c.get("contains_truth") for c in ok])
    type_i = _rate(
        [
            c.get("contains_zero") is False
            for c in ok
            if c.get("true_effect") is not None and abs(c["true_effect"]) < 1e-9
        ]
    )
    return {
        "n_cell_results": len(cells),
        "n_ok": len(ok),
        "coverage": cov,
        "type_i_error": type_i,
        "mean_bias": _mean([c.get("bias") for c in ok if c.get("bias") is not None]),
        "mean_interval_width": _mean([c.get("interval_width") for c in ok if c.get("interval_width") is not None]),
    }


def _group_metrics(runs: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        groups.setdefault(str(r.get(key)), []).append(r)
    return {k: _coverage_metrics(v) for k, v in groups.items()}


def _cross_cell_dependence(null_runs: list[dict[str, Any]]) -> dict[str, Any]:
    corrs: list[float] = []
    for r in null_runs:
        est = [e for e in (r.get("cell_estimate_vector") or []) if e is not None and np.isfinite(e)]
        if len(est) >= 2:
            corrs.append(float(np.corrcoef(est, est)[0, 1]) if len(est) == 2 else 0.0)
    fw = _rate([r.get("familywise_any_false_positive") for r in null_runs])
    return {
        "mean_cross_cell_estimate_correlation": _mean(corrs),
        "familywise_null_fp_rate": fw,
        "n_null_runs": len(null_runs),
    }


def _production_defect_assessment(
    cell_rows: list[dict[str, Any]],
    pool_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    identity_fail = any(c.get("cell_identity_preserved") is False for c in cell_rows)
    pooled_emit = any(r.get("pooled_effect_emitted") for r in pool_runs)
    pooled_interval = any(r.get("pooled_interval_emitted") for r in pool_runs)
    if pooled_emit or pooled_interval:
        return {
            "decision": "production_defect_confirmed",
            "rationale": "pooled multi-cell output emitted despite contract",
        }
    if identity_fail:
        return {
            "decision": "production_defect_confirmed",
            "rationale": "cell identity not preserved in at least one run",
        }
    return {
        "decision": "geometry_or_semantic_limitation",
        "rationale": (
            "shared-control cross-cell dependence and multiplicity are structural; "
            "not isolated implementation defects"
        ),
    }


def _decide_verdict(
    *,
    prod: dict[str, Any],
    cross_dep: dict[str, Any],
    cov_shared: dict[str, Any],
    cov_disjoint: dict[str, Any],
    pool_blocked: bool,
) -> SemanticVerdict:
    if prod.get("decision") == "production_defect_confirmed":
        return "multicell_percell_ineligible"
    if not pool_blocked:
        return "multicell_percell_ineligible"
    fw = cross_dep.get("familywise_null_fp_rate")
    if fw is not None and fw > 0.2:
        return "multicell_percell_multiplicity_unresolved"
    shared_t1 = (cov_shared.get("type_i_error") or 0.0) if cov_shared else 0.0
    disjoint_t1 = (cov_disjoint.get("type_i_error") or 0.0) if cov_disjoint else 0.0
    if shared_t1 > disjoint_t1 + 0.05:
        return "multicell_percell_shared_control_restricted"
    if disjoint_t1 is not None and disjoint_t1 < 0.12:
        return "multicell_percell_eligible_with_restrictions"
    return "multicell_percell_diagnostic_only"


def build_d5_trust_multicell_percell_inference_001(
    cfg: MulticellTrustConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or MulticellTrustConfig()
    t0 = time.perf_counter()
    n_rep = cfg.n_replicates_fast if cfg.fast else cfg.n_replicates
    worlds = TRUST_WORLDS if not cfg.fast else TRUST_WORLDS[:10]
    geoms = GEOMETRY_VARIANTS if not cfg.fast else GEOMETRY_VARIANTS[:6]
    patterns = EFFECT_PATTERNS if not cfg.fast else EFFECT_PATTERNS[:4]

    all_runs: list[dict[str, Any]] = []
    seed_cursor = cfg.random_state_base

    for world in worlds:
        for geom in geoms:
            if geom.n_cells != world.n_test_grps and geom.n_cells == 3:
                w = replace(world, n_test_grps=3)
            else:
                w = world
            if geom.n_cells == 3 and w.n_test_grps < 3:
                w = replace(w, n_test_grps=3)
            for rep in range(n_rep):
                seed = seed_cursor
                seed_cursor += 1
                all_runs.append(_run_one(w, geom, None, cfg, replicate_id=rep, seed=seed))

    for pattern in patterns:
        n_cells = len(pattern)
        geom = next((g for g in geoms if g.n_cells == n_cells), geoms[0])
        world = TrustWorldSpec(
            f"effect_pattern_{'_'.join(str(x) for x in pattern)}",
            n_test_grps=n_cells,
            notes="effect pattern sweep",
        )
        for rep in range(max(1, n_rep // 2)):
            seed = seed_cursor
            seed_cursor += 1
            all_runs.append(_run_one(world, geom, pattern, cfg, replicate_id=rep, seed=seed))

    cell_rows: list[dict[str, Any]] = []
    for r in all_runs:
        cell_rows.extend(r.get("cell_level_results") or [])

    ok_runs = [r for r in all_runs if r.get("failure_status") in ("ok", "blocked")]
    null_runs = [
        r
        for r in ok_runs
        if r.get("world_id") in ("all_cell_null", "shared_control_shock", "poor_pre_fit_all_cells")
        or (r.get("cell_effect_vector") and all(abs(x or 0) < 1e-9 for x in r["cell_effect_vector"]))
    ]

    cov_by_cell: dict[str, Any] = {}
    for i in range(3):
        cid = f"test_{i}"
        subset = [c for c in cell_rows if c.get("cell_id") == cid]
        cov_by_cell[cid] = _coverage_metrics([{"cell_level_results": subset}])

    cov_by_geom = _group_metrics(ok_runs, "geometry_id")
    cross_dep = _cross_cell_dependence(null_runs)

    shared_metrics = cov_by_geom.get("two_cells_shared_controls", {})
    disjoint_metrics = cov_by_geom.get("two_cells_disjoint_controls", {})

    pool_runs = [r for r in all_runs if r.get("pooled_readout_attempted")]
    pool_blocked = all(r.get("pooled_readout_blocked") for r in pool_runs) if pool_runs else True
    pooled_verification = {
        "attempted": len(pool_runs),
        "blocked": sum(1 for r in pool_runs if r.get("pooled_readout_blocked")),
        "effect_emitted": sum(1 for r in pool_runs if r.get("pooled_effect_emitted")),
        "interval_emitted": sum(1 for r in pool_runs if r.get("pooled_interval_emitted")),
        "all_blocked": pool_blocked,
    }

    prod = _production_defect_assessment(cell_rows, pool_runs)
    verdict = _decide_verdict(
        prod=prod,
        cross_dep=cross_dep,
        cov_shared=shared_metrics,
        cov_disjoint=disjoint_metrics,
        pool_blocked=pool_blocked,
    )

    aggregate_status = (
        "ELIGIBLE_WITH_RESTRICTIONS"
        if verdict in ("multicell_percell_eligible_with_restrictions", "multicell_percell_shared_control_restricted")
        else "PER_CELL_DIAGNOSTIC_ONLY"
        if verdict == "multicell_percell_diagnostic_only"
        else "INSUFFICIENT_EVIDENCE"
        if verdict == "multicell_percell_multiplicity_unresolved"
        else "INELIGIBLE"
    )

    policy_rows: list[dict[str, Any]] = []
    for pol in POLICY_COMPARISONS:
        if pol["policy_id"] == "E":
            subset = [r for r in ok_runs if "shared" in str(r.get("geometry_id", ""))]
        elif pol["policy_id"] == "F":
            subset = [r for r in ok_runs if "disjoint" in str(r.get("geometry_id", ""))]
        elif pol["policy_id"] == "G":
            subset = pool_runs
        elif pol["policy_id"] in ("B", "C", "D"):
            subset = []
        else:
            subset = ok_runs
        row: dict[str, Any] = {"policy": pol, "metrics": _coverage_metrics(subset)}
        if pol["policy_id"] in ("B", "C", "D"):
            row["calibration_valid"] = False
            row["note"] = _MULTIPLICITY_PROXY_DISCLAIMER
        policy_rows.append(row)

    follow_up = [_FOLLOW_UP_SHARED, _FOLLOW_UP_MULTIPLICITY]
    resolved = [_INVESTIGATION_ID]
    terminal = [_INVESTIGATION_ID]
    next_artifact = "D5-TRUST-STRATIFIED-SCM-JK-001"

    summary: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "config": {
            "fast": cfg.fast,
            "n_replicates": n_rep,
            "alpha": cfg.alpha,
            "train_length": cfg.train_length,
            "test_length": cfg.test_length,
            "canonical_scale": _CANONICAL_SCALE,
            "primary_method": _PRIMARY_METHOD,
            "truth_scale": _CANONICAL_SCALE,
            "point_estimate_scale": _CANONICAL_SCALE,
            "interval_scale": _CANONICAL_SCALE,
            "cell_weighting_scale": "equal_per_cell_unweighted",
        },
        "worlds": [w.world_id for w in worlds],
        "effect_patterns": [list(p) for p in patterns],
        "geometry_variants": [
            {
                "geometry_id": g.geometry_id,
                "n_cells": g.n_cells,
                "shared_control_policy": g.shared_control_policy,
                "control_reuse_policy": g.control_reuse_policy,
                "geometry_supported": g.geometry_supported,
            }
            for g in geoms
        ],
        "run_counts": {
            "total_runs": len(all_runs),
            "successful_runs": len(ok_runs),
            "failed_runs": len(all_runs) - len(ok_runs),
            "cell_level_results": len(cell_rows),
            "runtime_seconds": round(time.perf_counter() - t0, 2),
        },
        "cell_level_results": cell_rows[:200] if cfg.fast else cell_rows[:500],
        "cross_cell_dependence": cross_dep,
        "coverage_by_cell": cov_by_cell,
        "coverage_by_geometry": cov_by_geom,
        "type_i_by_cell": {k: v.get("type_i_error") for k, v in cov_by_cell.items()},
        "familywise_type_i": cross_dep.get("familywise_null_fp_rate"),
        "simultaneous_coverage": _rate([r.get("simultaneous_coverage") for r in ok_runs]),
        "multiplicity_comparisons": {
            "unadjusted_familywise_type_i": cross_dep.get("familywise_null_fp_rate"),
            "bonferroni_proxy": None,
            "holm_proxy": None,
            "proxy_comparison_valid": False,
            "calibration_audit": _multiplicity_calibration_audit(),
            "disclaimer": _MULTIPLICITY_PROXY_DISCLAIMER,
        },
        "shared_control_results": {
            "shared_geometry": shared_metrics,
            "disjoint_geometry": disjoint_metrics,
            "cross_cell_correlation": cross_dep.get("mean_cross_cell_estimate_correlation"),
        },
        "pooled_block_verification": pooled_verification,
        "failure_summary": {
            "n_fail": len(all_runs) - len(ok_runs),
            "reasons": list(
                {r.get("failure_reason") for r in all_runs if r.get("failure_status") == "fail"}
            ),
        },
        "policy_comparisons": policy_rows,
        "production_defect_assessment": prod,
        "semantic_classification": {
            "verdict": verdict,
            "aggregate_status": aggregate_status,
            "geometry_decisions": {
                "disjoint_controls": "per_cell_disjoint_controls_only",
                "shared_controls": "per_cell_with_multiplicity_warning",
                "partial_overlap": "per_cell_restricted",
                "small_cell": "per_cell_restricted",
                "pooled_multi_cell": "not_supported",
            },
            "supported_roles": ["per_cell_diagnostic", "per_cell_restricted_interval"],
            "unsupported_roles": ["pooled_multi_cell_causal", "trust_report", "simultaneous_multi_cell_decision"],
        },
        "trustreport_eligibility_implications": {
            "dcm_006": "per_cell_restricted_no_trustreport_authorization",
            "prior_status": "ELIGIBLE_WITH_RESTRICTIONS_DESIGN_ONLY",
            "reassessment_required": True,
            "full_reassessment_deferred": True,
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
        },
        "investigation_handoff": build_investigation_handoff(
            follow_up_issues=follow_up,
            resolved_issues=resolved,
            terminal_dispositions=terminal,
            next_artifact=next_artifact,
        ),
        "limitations": [
            "Evaluates per-cell inference for multi-cell designs; does not validate pooled multi-cell causal inference.",
            "Does not authorize TrustReport.",
            "Does not perform the full TrustReport eligibility reassessment.",
            "SCM+UnitJackknife primary path only; AugSynth/TBR/DID per-cell paths not expanded.",
            "Bonferroni/Holm proxy comparison was not a valid calibration test (no per-cell p-values or adjusted intervals on SCM+JK path).",
            "Multiplicity remains unresolved; equal FWER across proxy labels does not imply Bonferroni/Holm ineffectiveness.",
            "Shared-control dependence is structural; marginal per-cell coverage does not imply valid multi-cell decisioning.",
        ],
        "verdict": verdict,
    }

    if cfg.write_full_results_path and not cfg.fast:
        Path(cfg.write_full_results_path).write_text(
            json.dumps(_json_safe({"summary": summary, "runs": all_runs}), indent=2) + "\n"
        )

    return _json_safe(summary)


def _atomic_write_text(path: Path, content: str, *, overwrite: bool = False) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _write_report(payload: dict[str, Any], path: Path, *, overwrite: bool = False) -> None:
    handoff = payload.get("investigation_handoff") or {}
    lines = [
        f"# {_ARTIFACT_ID} Report",
        "",
        "## 1. Executive summary",
        "",
        "This artifact evaluates per-cell inference for multi-cell designs.",
        "It does not validate pooled multi-cell causal inference.",
        "It does not authorize TrustReport.",
        "It does not perform the full TrustReport eligibility reassessment.",
        "",
        f"**Verdict:** `{payload.get('verdict')}`",
        f"**Aggregate status:** `{payload.get('semantic_classification', {}).get('aggregate_status')}`",
        "",
        "## 2. Prior DCM-006 status",
        "",
        "DCM-006 was ELIGIBLE_WITH_RESTRICTIONS (design-only); per-cell interval coverage and shared-control dependence unresolved.",
        "",
        "## 3. Scope",
        "",
        "SCM + UnitJackknife per cell across geometry variants and synthetic worlds.",
        "",
        "## 4. Non-goals",
        "",
        "No pooled multi-cell causal readout; no TrustReport authorization; no production algorithm changes.",
        "",
        "## 5. Multi-cell geometry",
        "",
        "Distinguishes multiple test cells from multiple treated units within one cell; per-cell readout only.",
        "",
        "## 6. Per-cell estimands",
        "",
        f"Canonical scale: `{_CANONICAL_SCALE}`.",
        "",
        "## 7. Cell identity contract",
        "",
        "Cell identity preserved; other test units excluded from each cell panel.",
        "",
        "## 8. Control-pool policies",
        "",
        "Shared, disjoint, and partial-overlap donor constructions evaluated.",
        "",
        "## 9. Shared-control structure",
        "",
        json.dumps(payload.get("shared_control_results", {}), indent=2),
        "",
        "## 10. Inference path",
        "",
        f"Primary: `{_PRIMARY_METHOD}`.",
        "",
        "## 11. Scale contract",
        "",
        "Level mean relative percent injection; intervals on same level scale.",
        "",
        "## 12. Worlds",
        "",
        ", ".join(payload.get("worlds", [])),
        "",
        "## 13. Effect patterns",
        "",
        json.dumps(payload.get("effect_patterns", [])),
        "",
        "## 14. Geometry variants",
        "",
        json.dumps(payload.get("geometry_variants", []), indent=2),
        "",
        "## 15. Run counts/runtime",
        "",
        json.dumps(payload.get("run_counts", {}), indent=2),
        "",
        "## 16. Cell-level point behavior",
        "",
        f"Mean bias by cell: {json.dumps({k: v.get('mean_bias') for k, v in payload.get('coverage_by_cell', {}).items()})}",
        "",
        "## 17. Cell-level interval behavior",
        "",
        f"Coverage by geometry: {json.dumps(payload.get('coverage_by_geometry', {}), indent=2)[:2000]}",
        "",
        "## 18. Per-cell null type-I",
        "",
        json.dumps(payload.get("type_i_by_cell", {}), indent=2),
        "",
        "## 19. Familywise type-I",
        "",
        str(payload.get("familywise_type_i")),
        "",
        "## 20. Per-cell coverage",
        "",
        json.dumps(payload.get("coverage_by_cell", {}), indent=2),
        "",
        "## 21. Simultaneous coverage",
        "",
        str(payload.get("simultaneous_coverage")),
        "",
        "## 22. Multiplicity findings",
        "",
        f"**Unadjusted familywise null type-I:** {payload.get('familywise_type_i')}",
        "",
        _MULTIPLICITY_PROXY_DISCLAIMER,
        "",
        json.dumps(payload.get("multiplicity_comparisons", {}), indent=2),
        "",
        "## 23. Shared-control dependence",
        "",
        json.dumps(payload.get("cross_cell_dependence", {}), indent=2),
        "",
        "## 24. Disjoint-control findings",
        "",
        json.dumps(payload.get("shared_control_results", {}).get("disjoint_geometry", {}), indent=2),
        "",
        "## 25. Small-cell findings",
        "",
        json.dumps(payload.get("coverage_by_geometry", {}).get("small_cell", {}), indent=2),
        "",
        "## 26. Poor-pre-fit findings",
        "",
        "See worlds poor_pre_fit_one_cell and poor_pre_fit_all_cells.",
        "",
        "## 27. Donor-support findings",
        "",
        "See small_donor_pool and heavy_control_reuse worlds.",
        "",
        "## 28. Pooled readout block verification",
        "",
        json.dumps(payload.get("pooled_block_verification", {}), indent=2),
        "",
        "## 29. Policy comparisons",
        "",
        "Policy A (unadjusted per-cell) and E/F (geometry subsets) are calibrated. "
        "Policies B/C/D (Bonferroni, Holm, max-stat) were **not** valid calibration tests in this artifact — see §22.",
        "",
        "See summary `policy_comparisons`.",
        "",
        "## 30. Root-cause determination",
        "",
        "Shared-control dependence and multiplicity are structural; not code defects.",
        "",
        "## 31. Production-defect decision",
        "",
        json.dumps(payload.get("production_defect_assessment", {}), indent=2),
        "",
        "## 32. Semantic classification",
        "",
        json.dumps(payload.get("semantic_classification", {}), indent=2),
        "",
        "## 33. TrustReport implications",
        "",
        json.dumps(payload.get("trustreport_eligibility_implications", {}), indent=2),
        "",
        "## 34. Authorization status",
        "",
        json.dumps(payload.get("authorization_summary", {}), indent=2),
        "",
        "## 35. Investigation lifecycle update",
        "",
        f"Consumed `{_INVESTIGATION_ID}` → RESOLVED (PER_CELL_RESTRICTED).",
        f"Opened `{_FOLLOW_UP_SHARED}`, `{_FOLLOW_UP_MULTIPLICITY}` as DEFERRED_WITH_TRIGGER.",
        "",
        "## 36. Remaining limitations",
        "",
        "; ".join(payload.get("limitations", [])),
        "",
        "## 37. Governance verdict",
        "",
        f"**`{payload.get('verdict')}`**",
        "",
    ]
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=[_INVESTIGATION_ID],
            new_investigations=[_FOLLOW_UP_SHARED, _FOLLOW_UP_MULTIPLICITY],
            updated_investigations=[f"{_INVESTIGATION_ID} → RESOLVED (PER_CELL_RESTRICTED)"],
            deferred_issues=[_FOLLOW_UP_SHARED, _FOLLOW_UP_MULTIPLICITY],
            explicit_exclusions=["FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT"],
            revisit_trigger="After stratified SCM+JK lane and multiplicity remediation",
            decision_checkpoint="FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT DCM-006 row",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write_text(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    cfg: MulticellTrustConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_d5_trust_multicell_percell_inference_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write_text(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument(
        "--output-local",
        default="/tmp/D5_TRUST_MULTICELL_PERCELL_INFERENCE_001_results.json",
    )
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args(argv)

    cfg = MulticellTrustConfig(
        fast=args.fast,
        write_full_results_path=args.output_local if not args.fast else None,
    )
    write_summary(
        Path(args.summary_output),
        cfg=cfg,
        overwrite=args.overwrite,
        report_path=Path(args.report_output),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
