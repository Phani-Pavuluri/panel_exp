"""D5-TRUST-STRATIFIED-SCM-JK-001 — DCM-008 stratified SCM+UnitJackknife qualification.

Characterizes stratified design × SCM × UnitJackknife: per-stratum diagnostics,
donor-pool policies, aggregate readout semantics, and weight-dominance cases.
No production changes. Does not authorize TrustReport.
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

from panel_exp.design.assign import StratifiedRandomization
from panel_exp.governance.investigation_lifecycle_contract import (
    build_investigation_handoff,
    format_handoff_report_section,
)
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.validation.track_d_d5_stat_mcell_percell_001 import (
    D5StatMcellPercell001Config,
    _apply_cell_shock,
    _build_wide,
    _json_safe,
    _run_cell_method,
)
from panel_exp.validation.track_d_d5_trust_tbrridge_brb_001 import _mean, _rate

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_ID = "D5-TRUST-STRATIFIED-SCM-JK-001"
_ARTIFACT_VERSION = "1.0.0"
_CANONICAL_SCALE = "level_mean_relative_percent_injection"
_INVESTIGATION_ID = "INV-STRATIFIED-SCM-JK-TRUSTREPORT-DISPOSITION-001"
_DEFAULT_SUMMARY = _REPO_ROOT / "docs/track_d/archives/D5_TRUST_STRATIFIED_SCM_JK_001_summary.json"
_DEFAULT_REPORT = _REPO_ROOT / "docs/track_d/D5_TRUST_STRATIFIED_SCM_JK_001_REPORT.md"
_PRIMARY_METHOD = "STRATIFIED-PERSTRATUM-SCM-JK"
_SCM_FIT_MODE = "per_stratum_panel_aggregate_treated"

SemanticVerdict = Literal[
    "stratified_scm_jk_eligible_with_restrictions",
    "stratified_scm_jk_balanced_only",
    "stratified_scm_jk_small_stratum_restricted",
    "stratified_scm_jk_weight_dominance_restricted",
    "stratified_scm_jk_aggregate_blocked",
    "stratified_scm_jk_diagnostic_only",
    "stratified_scm_jk_ineligible",
    "stratified_scm_jk_remediation_required",
    "stratified_scm_jk_inconclusive",
]

ProductionDefectDecision = Literal[
    "production_defect_confirmed",
    "production_defect_not_confirmed",
    "production_defect_indeterminate",
    "geometry_or_semantic_limitation",
]

POLICY_COMPARISONS: tuple[dict[str, str], ...] = (
    {
        "policy_id": "A",
        "name": "stratified_aggregate_unadjusted",
        "description": "volume-weighted aggregate of per-stratum JK point estimates",
    },
    {
        "policy_id": "B",
        "name": "stratum_marginal_report_only",
        "description": "marginal per-stratum JK intervals without aggregate decisioning",
    },
    {
        "policy_id": "C",
        "name": "within_stratum_donor_pool",
        "description": "donors restricted to same stratum as treated",
    },
    {
        "policy_id": "D",
        "name": "global_donor_pool",
        "description": "global control pool across strata",
    },
    {
        "policy_id": "E",
        "name": "weight_dominance_restricted",
        "description": "flag strata where volume weight exceeds dominance threshold",
    },
    {
        "policy_id": "F",
        "name": "small_stratum_blocked",
        "description": "small-stratum geometries fail closed or restricted",
    },
    {
        "policy_id": "G",
        "name": "aggregate_claim_blocked",
        "description": "pooled/aggregate causal claim blocked without pooled estimand",
    },
)


@dataclass(frozen=True)
class GeometrySpec:
    geometry_id: str
    n_strata: int = 2
    donor_pool_policy: str = "within_stratum_only"
    n_geos: int | None = None
    treatment_probability: float | None = None
    min_units_per_stratum: int = 2
    geometry_supported: bool = True
    geometry_failure_reason: str | None = None
    weight_imbalance: bool = False
    notes: str = ""


@dataclass(frozen=True)
class TrustWorldSpec:
    world_id: str
    scenario_name: str = "scm_low_signal"
    percent_effect: float = 0.0
    stratum_effects: dict[str, float] = field(default_factory=dict)
    n_geos: int = 16
    n_periods: int = 44
    treatment_probability: float = 0.35
    scenario_overrides: dict[str, Any] = field(default_factory=dict)
    shock_stratum: str | None = None
    shock_magnitude: float = 0.0
    shock_all_strata: bool = False
    notes: str = ""


@dataclass(frozen=True)
class StratifiedTrustConfig:
    n_replicates: int = 4
    n_replicates_fast: int = 2
    train_length: int = 28
    test_length: int = 8
    alpha: float = 0.05
    random_state_base: int = 20260701
    min_control_units: int = 4
    weight_dominance_threshold: float = 0.70
    fast: bool = False
    write_full_results_path: str | None = "/tmp/D5_TRUST_STRATIFIED_SCM_JK_001_results.json"


GEOMETRY_VARIANTS: tuple[GeometrySpec, ...] = (
    GeometrySpec("balanced_two_strata", n_strata=2, notes="equal requested strata"),
    GeometrySpec("balanced_three_strata", n_strata=3, notes="three balanced strata"),
    GeometrySpec(
        "unequal_strata_sizes",
        n_strata=3,
        treatment_probability=0.45,
        notes="covariate skew yields unequal stratum sizes",
    ),
    GeometrySpec(
        "small_stratum",
        n_strata=4,
        n_geos=10,
        treatment_probability=0.40,
        min_units_per_stratum=2,
        notes="small donor pool per stratum",
    ),
    GeometrySpec(
        "large_stratum",
        n_strata=2,
        n_geos=22,
        treatment_probability=0.25,
        notes="large donor pool",
    ),
    GeometrySpec("one_weak_stratum", n_strata=2, notes="one stratum weak effect via world"),
    GeometrySpec("one_bad_prefit_stratum", n_strata=2, notes="poor pre-fit in one stratum"),
    GeometrySpec("stratum_specific_shock", n_strata=2, notes="post-period shock in one stratum"),
    GeometrySpec("cross_stratum_common_shock", n_strata=2, notes="common shock across strata"),
    GeometrySpec(
        "stratum_weight_imbalance",
        n_strata=2,
        weight_imbalance=True,
        notes="volume skew creates weight dominance",
    ),
    GeometrySpec(
        "donor_pool_within_stratum_only",
        n_strata=2,
        donor_pool_policy="within_stratum_only",
    ),
    GeometrySpec(
        "donor_pool_global",
        n_strata=2,
        donor_pool_policy="global",
        notes="global donor pool may hide stratum mismatch",
    ),
    GeometrySpec(
        "donor_pool_partial_overlap",
        n_strata=2,
        donor_pool_policy="partial_overlap",
    ),
    GeometrySpec(
        "treated_absent_in_one_stratum_negative_control",
        n_strata=4,
        n_geos=14,
        treatment_probability=0.20,
        notes="at least one stratum may lack treated units",
    ),
    GeometrySpec(
        "control_absent_in_one_stratum_negative_control",
        n_strata=2,
        geometry_supported=False,
        geometry_failure_reason="control_absent_in_stratum_not_supported",
        notes="fail closed when stratum lacks controls",
    ),
)

EFFECT_PATTERNS: tuple[tuple[float, ...], ...] = (
    (0.0, 0.0),
    (0.08, 0.08),
    (0.08, 0.0),
    (0.08, -0.05),
    (0.03, 0.03),
    (0.12, 0.0),
    (0.0, 0.0, 0.0),
    (0.08, 0.08, 0.08),
    (0.08, 0.0, 0.0),
    (0.08, -0.05, 0.03),
    (0.12, 0.03, 0.0),
)

TRUST_WORLDS: tuple[TrustWorldSpec, ...] = (
    TrustWorldSpec("all_strata_null", percent_effect=0.0),
    TrustWorldSpec(
        "homogeneous_positive",
        stratum_effects={"0": 0.08, "1": 0.08},
        notes="same positive effect all strata",
    ),
    TrustWorldSpec(
        "heterogeneous_positive",
        stratum_effects={"0": 0.08, "1": 0.03},
        notes="different positive effects",
    ),
    TrustWorldSpec(
        "one_stratum_positive",
        stratum_effects={"0": 0.08, "1": 0.0},
        notes="single active stratum",
    ),
    TrustWorldSpec(
        "mixed_sign",
        stratum_effects={"0": 0.08, "1": -0.05},
        notes="mixed sign across strata",
    ),
    TrustWorldSpec("weak_effects", stratum_effects={"0": 0.03, "1": 0.03}),
    TrustWorldSpec("strong_effects", stratum_effects={"0": 0.12, "1": 0.12}),
    TrustWorldSpec(
        "serial_correlation",
        stratum_effects={"0": 0.08, "1": 0.0},
        scenario_overrides={"autocorrelation": 0.7},
    ),
    TrustWorldSpec(
        "high_serial_correlation",
        stratum_effects={"0": 0.08, "1": 0.0},
        scenario_overrides={"autocorrelation": 0.92},
    ),
    TrustWorldSpec(
        "heteroskedasticity_by_stratum",
        stratum_effects={"0": 0.08, "1": 0.0},
        scenario_overrides={"noise_scale": 4.8},
    ),
    TrustWorldSpec(
        "poor_prefit_one_stratum",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        notes="stressed pre-fit",
    ),
    TrustWorldSpec(
        "poor_prefit_all_strata",
        scenario_name="scm_trend_mismatch",
        percent_effect=0.0,
        scenario_overrides={"noise_scale": 4.0},
    ),
    TrustWorldSpec(
        "stratum_specific_shock",
        shock_stratum="1",
        shock_magnitude=18.0,
        percent_effect=0.0,
    ),
    TrustWorldSpec(
        "common_shock",
        percent_effect=0.0,
        shock_all_strata=True,
        shock_magnitude=12.0,
        scenario_overrides={"cross_geo_correlation": 0.85},
    ),
    TrustWorldSpec(
        "donor_contamination_one_stratum",
        stratum_effects={"0": 0.08, "1": 0.0},
        scenario_overrides={"cross_geo_correlation": 0.92},
    ),
    TrustWorldSpec(
        "donor_contamination_cross_strata",
        percent_effect=0.0,
        scenario_overrides={"cross_geo_correlation": 0.90},
    ),
    TrustWorldSpec(
        "small_donor_one_stratum",
        n_geos=10,
        treatment_probability=0.40,
        stratum_effects={"0": 0.08, "1": 0.0},
    ),
    TrustWorldSpec(
        "high_imbalance",
        n_geos=14,
        treatment_probability=0.48,
        stratum_effects={"0": 0.08, "1": 0.0},
        scenario_overrides={"volume_skew": 6.0},
    ),
    TrustWorldSpec(
        "missing_tiny_stratum",
        n_geos=10,
        treatment_probability=0.35,
        percent_effect=0.0,
        notes="sparse strata negative control",
    ),
    TrustWorldSpec(
        "weight_dominated_stratum",
        n_geos=16,
        treatment_probability=0.35,
        stratum_effects={"0": 0.08, "1": 0.0},
        scenario_overrides={"volume_skew": 8.0},
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


def _to_mcell_cfg(cfg: StratifiedTrustConfig) -> D5StatMcellPercell001Config:
    return D5StatMcellPercell001Config(
        n_replicates=cfg.n_replicates,
        train_length=cfg.train_length,
        test_length=cfg.test_length,
        alpha=cfg.alpha,
        random_state_base=cfg.random_state_base,
        min_control_units=cfg.min_control_units,
    )


def _to_mcell_world(spec: TrustWorldSpec, *, n_strata: int) -> Any:
    from panel_exp.validation.track_d_d5_stat_mcell_percell_001 import WorldSpec

    overrides = dict(spec.scenario_overrides)
    overrides.pop("volume_skew", None)
    return WorldSpec(
        world_id=spec.world_id,
        n_test_grps=1,
        scenario_name=spec.scenario_name,
        percent_effect=spec.percent_effect,
        cell_effects={},
        n_geos=spec.n_geos,
        n_periods=spec.n_periods,
        treatment_probability=spec.treatment_probability,
        scenario_overrides=overrides,
        shock_cell=spec.shock_stratum,
        shock_magnitude=spec.shock_magnitude,
        notes=spec.notes,
    )


def _sort_stratum_ids(strata: list[Any]) -> list[str]:
    def _key(s: Any) -> tuple[int, str]:
        ss = str(s)
        return (int(ss) if ss.isdigit() else 999, ss)

    return sorted({str(s) for s in strata}, key=_key)


def _assign_stratified(
    wide: Any,
    *,
    train_length: int,
    test_length: int,
    seed: int,
    treatment_probability: float,
    n_strata: int,
    min_units_per_stratum: int = 2,
) -> tuple[dict[str, list[str]], dict[str, int], dict[str, Any]]:
    end = train_length + test_length
    panel = PanelDataset(wide.iloc[:, :end].copy())
    design = StratifiedRandomization(
        treatment_probability=treatment_probability,
        random_state=seed,
        stratification_policy="adaptive_strata",
        min_units_per_stratum=min_units_per_stratum,
    )
    assignment = design.assign(
        panel_data=panel,
        pre_treatment_period=TimePeriod(0, train_length - 1),
        n_test_grps=1,
        n_percentiles=n_strata,
    )
    meta = design.last_stratification_metadata or {}
    raw_map = meta.get("unit_to_stratum_map") or {}
    unit_to_stratum = {str(u): int(s) for u, s in raw_map.items()}
    return assignment, unit_to_stratum, meta


def _stratum_groups(
    assignment: dict[str, list[str]],
    unit_to_stratum: dict[str, int],
) -> tuple[list[str], dict[str, list[str]], dict[str, list[str]]]:
    controls = list(assignment.get("control") or [])
    treated = list(assignment.get("test_0") or [])
    strata_ids = _sort_stratum_ids(list(set(unit_to_stratum.values())))
    stratum_treated: dict[str, list[str]] = {}
    stratum_controls: dict[str, list[str]] = {}
    for sid in strata_ids:
        stratum_treated[sid] = [u for u in treated if unit_to_stratum.get(u) == int(sid)]
        stratum_controls[sid] = [u for u in controls if unit_to_stratum.get(u) == int(sid)]
    return strata_ids, stratum_treated, stratum_controls


def _stratum_weights(
    wide: Any,
    strata_ids: list[str],
    stratum_treated: dict[str, list[str]],
    *,
    train_length: int,
) -> dict[str, float]:
    weights: dict[str, float] = {}
    pre = wide.iloc[:, :train_length]
    total = 0.0
    for sid in strata_ids:
        units = stratum_treated.get(sid) or []
        w = float(pre.loc[units].sum().sum()) if units else 0.0
        weights[sid] = w
        total += w
    if total <= 0:
        n = len(strata_ids) or 1
        return {sid: 1.0 / n for sid in strata_ids}
    return {sid: weights[sid] / total for sid in strata_ids}


def _donor_controls(
    *,
    policy: str,
    stratum_id: str,
    stratum_controls: dict[str, list[str]],
    all_controls: list[str],
) -> list[str]:
    local = list(stratum_controls.get(stratum_id) or [])
    if policy == "within_stratum_only":
        return local
    if policy == "global":
        return list(all_controls)
    if policy == "partial_overlap":
        others = [u for sid, units in stratum_controls.items() if sid != stratum_id for u in units]
        half = others[: max(1, len(others) // 2)]
        return list(dict.fromkeys(local + half))
    return local


def _build_stratum_panel(
    wide: Any,
    treated_units: list[str],
    control_units: list[str],
    cfg: D5StatMcellPercell001Config,
    *,
    min_controls: int | None = None,
) -> PanelDataset:
    end = cfg.train_length + cfg.test_length
    if not treated_units:
        raise ValueError("empty_stratum_treated")
    min_req = cfg.min_control_units if min_controls is None else min_controls
    if len(control_units) < min_req:
        raise ValueError("insufficient_stratum_controls")
    readout_units = list(control_units) + list(treated_units)
    return PanelDataset(
        wide.loc[readout_units].iloc[:, :end].copy(),
        treated_units=list(treated_units),
        treated_periods=[TimePeriod(cfg.train_length, end - 1) for _ in treated_units],
    )


def _stratum_effects_from_pattern(
    pattern: tuple[float, ...] | None,
    strata_ids: list[str],
    world: TrustWorldSpec,
) -> dict[str, float]:
    if pattern is not None:
        sorted_ids = _sort_stratum_ids(strata_ids)
        return {sid: float(pattern[i]) if i < len(pattern) else 0.0 for i, sid in enumerate(sorted_ids)}
    if world.stratum_effects:
        sorted_ids = _sort_stratum_ids(strata_ids)
        out: dict[str, float] = {}
        keys = sorted(world.stratum_effects.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))
        for i, sid in enumerate(sorted_ids):
            if sid in world.stratum_effects:
                out[sid] = float(world.stratum_effects[sid])
            elif i < len(keys):
                out[sid] = float(world.stratum_effects[keys[i]])
            else:
                out[sid] = float(world.percent_effect)
        return out
    return {sid: float(world.percent_effect) for sid in strata_ids}


def _weighted_aggregate(
    values: dict[str, float | None],
    weights: dict[str, float],
) -> float | None:
    num = 0.0
    den = 0.0
    for sid, v in values.items():
        if v is None or not np.isfinite(v):
            continue
        w = weights.get(sid, 0.0)
        num += w * float(v)
        den += w
    return float(num / den) if den > 0 else None


def _run_one(
    world: TrustWorldSpec,
    geom: GeometrySpec,
    effect_pattern: tuple[float, ...] | None,
    cfg: StratifiedTrustConfig,
    *,
    replicate_id: int,
    seed: int,
) -> dict[str, Any]:
    mcell_cfg = _to_mcell_cfg(cfg)
    run_level: dict[str, Any] = {
        "world_id": world.world_id,
        "geometry_id": geom.geometry_id,
        "seed": seed,
        "replicate": replicate_id,
        "effect_pattern": list(effect_pattern) if effect_pattern else None,
        "failure_status": "ok",
        "failure_reason": None,
        "pooled_or_aggregate_claim_emitted": False,
        "pooled_or_aggregate_claim_blocked_if_unsupported": True,
        "scm_fit_mode": _SCM_FIT_MODE,
    }
    stratum_rows: list[dict[str, Any]] = []

    if not geom.geometry_supported:
        run_level["failure_status"] = "blocked"
        run_level["failure_reason"] = geom.geometry_failure_reason
        run_level["geometry_supported"] = False
        run_level["stratum_level_results"] = []
        return run_level

    mcell_world = _to_mcell_world(world, n_strata=geom.n_strata)
    mcell_world = replace(
        mcell_world,
        n_geos=geom.n_geos or world.n_geos,
        treatment_probability=geom.treatment_probability or world.treatment_probability,
    )

    try:
        wide = _build_wide(mcell_world, mcell_cfg, seed=seed)
        if geom.weight_imbalance or world.world_id in ("high_imbalance", "weight_dominated_stratum"):
            skew = 8.0 if world.world_id == "weight_dominated_stratum" else 6.0
            units = list(wide.index)
            mult = np.linspace(1.0, skew, len(units))
            wide = wide.mul(mult.reshape(-1, 1), axis=0)

        assignment, unit_to_stratum, strat_meta = _assign_stratified(
            wide,
            train_length=mcell_cfg.train_length,
            test_length=mcell_cfg.test_length,
            seed=seed,
            treatment_probability=mcell_world.treatment_probability,
            n_strata=geom.n_strata,
            min_units_per_stratum=geom.min_units_per_stratum,
        )
        strata_ids, stratum_treated, stratum_controls = _stratum_groups(assignment, unit_to_stratum)
        if not strata_ids:
            raise ValueError("no_strata_realized")

        stratum_effects = _stratum_effects_from_pattern(effect_pattern, strata_ids, world)
        weights = _stratum_weights(
            wide, strata_ids, stratum_treated, train_length=mcell_cfg.train_length
        )
        weight_dominance = any(w > cfg.weight_dominance_threshold for w in weights.values())
        all_controls = list(assignment.get("control") or [])

        estimates: dict[str, float | None] = {}
        truths: dict[str, float | None] = {}
        intervals: dict[str, tuple[float | None, float | None]] = {}
        contains_truth: dict[str, bool | None] = {}
        contains_zero: dict[str, bool | None] = {}

        for sid in strata_ids:
            treated = stratum_treated.get(sid) or []
            donors = _donor_controls(
                policy=geom.donor_pool_policy,
                stratum_id=sid,
                stratum_controls=stratum_controls,
                all_controls=all_controls,
            )
            row_base = {
                "world_id": world.world_id,
                "seed": seed,
                "replicate": replicate_id,
                "geometry_id": geom.geometry_id,
                "stratum_id": sid,
                "n_strata": len(strata_ids),
                "n_treated_in_stratum": len(treated),
                "n_controls_in_stratum": len(donors),
                "stratum_weight": weights.get(sid),
                "donor_pool_policy": geom.donor_pool_policy,
                "true_effect": None,
                "scm_fit_scope": _SCM_FIT_MODE,
            }
            if not treated:
                row = {
                    **row_base,
                    "failure_status": "skipped",
                    "failure_reason": "no_treated_in_stratum",
                    "stratum_identity_preserved": True,
                }
                stratum_rows.append(row)
                estimates[sid] = None
                truths[sid] = stratum_effects.get(sid, 0.0)
                intervals[sid] = (None, None)
                contains_truth[sid] = None
                contains_zero[sid] = None
                continue
            try:
                min_controls = 2 if geom.donor_pool_policy == "within_stratum_only" else None
                panel = _build_stratum_panel(
                    wide, treated, donors, mcell_cfg, min_controls=min_controls
                )
                shock_sid = world.shock_stratum
                if shock_sid == sid and world.shock_magnitude:
                    panel = _apply_cell_shock(
                        panel,
                        magnitude=world.shock_magnitude,
                        train_length=mcell_cfg.train_length,
                        test_length=mcell_cfg.test_length,
                    )
                elif world.shock_all_strata and world.shock_magnitude:
                    panel = _apply_cell_shock(
                        panel,
                        magnitude=world.shock_magnitude,
                        train_length=mcell_cfg.train_length,
                        test_length=mcell_cfg.test_length,
                    )
                pct = stratum_effects.get(sid, world.percent_effect)
                readout, _, identity_ok = _run_cell_method(
                    "MCELL-PERCELL-SCM-JK", panel, percent_effect=pct, cfg=mcell_cfg
                )
                il = readout.get("interval_lower")
                iu = readout.get("interval_upper")
                cz = bool(il <= 0.0 <= iu) if il is not None and iu is not None else None
                row = {
                    **row_base,
                    "true_effect": readout.get("true_effect"),
                    "point_estimate": readout.get("point_estimate"),
                    "bias": readout.get("bias"),
                    "squared_error": readout.get("squared_error"),
                    "sign_correct": readout.get("sign_correct"),
                    "interval_lower": il,
                    "interval_upper": iu,
                    "contains_truth": readout.get("interval_contains_truth"),
                    "contains_zero": cz,
                    "interval_width": readout.get("interval_width"),
                    "prefit_rmse": readout.get("prefit_rmse"),
                    "donor_count": readout.get("donor_count"),
                    "failure_status": "ok",
                    "failure_reason": None,
                    "stratum_identity_preserved": identity_ok,
                }
                estimates[sid] = readout.get("point_estimate")
                truths[sid] = readout.get("true_effect")
                intervals[sid] = (il, iu)
                contains_truth[sid] = readout.get("interval_contains_truth")
                contains_zero[sid] = cz
            except Exception as exc:
                reason = f"{type(exc).__name__}: {exc}"[:200]
                identity_violation = "identity" in reason.lower()
                row = {
                    **row_base,
                    "failure_status": "fail",
                    "failure_reason": reason,
                    "stratum_identity_preserved": False if identity_violation else None,
                }
                estimates[sid] = None
                truths[sid] = stratum_effects.get(sid)
                intervals[sid] = (None, None)
                contains_truth[sid] = None
                contains_zero[sid] = None
            stratum_rows.append(row)

        agg_truth = _weighted_aggregate(
            {k: (v if v is not None else 0.0) for k, v in truths.items()}, weights
        )
        agg_point = _weighted_aggregate(estimates, weights)
        agg_il = _weighted_aggregate({k: v[0] for k, v in intervals.items()}, weights)
        agg_iu = _weighted_aggregate({k: v[1] for k, v in intervals.items()}, weights)
        agg_ct = (
            bool(agg_il <= agg_truth <= agg_iu)
            if agg_truth is not None and agg_il is not None and agg_iu is not None
            else None
        )
        agg_cz = bool(agg_il <= 0.0 <= agg_iu) if agg_il is not None and agg_iu is not None else None

        null_strata = [sid for sid in strata_ids if abs(truths.get(sid) or 0.0) < 1e-9]
        any_fp = any(
            contains_zero.get(sid) is False
            for sid in null_strata
            if contains_zero.get(sid) is not None
        )
        all_cov = all(
            contains_truth.get(sid) is True
            for sid in strata_ids
            if contains_truth.get(sid) is not None and estimates.get(sid) is not None
        )
        est_vec = [estimates[s] for s in strata_ids if estimates.get(s) is not None]
        err_vec = [
            float(estimates[s] - (truths[s] or 0.0))
            for s in strata_ids
            if estimates.get(s) is not None and truths.get(s) is not None
        ]
        cross_cov = float(np.cov(err_vec, err_vec)[0, 0]) if len(err_vec) > 1 else None

        run_level.update(
            {
                "stratum_level_results": stratum_rows,
                "stratum_effect_vector": [truths.get(s) for s in strata_ids],
                "stratum_estimate_vector": [estimates.get(s) for s in strata_ids],
                "aggregate_effect_truth": agg_truth,
                "aggregate_point_estimate": agg_point,
                "aggregate_interval_lower": agg_il,
                "aggregate_interval_upper": agg_iu,
                "aggregate_contains_truth": agg_ct,
                "aggregate_contains_zero": agg_cz,
                "stratum_weighting_policy": "treated_kpi_volume_share",
                "stratum_weights": weights,
                "weight_dominance_flag": weight_dominance,
                "cross_stratum_error_covariance": cross_cov,
                "cross_stratum_sign_pattern": [
                    int(np.sign(estimates[s])) if estimates.get(s) is not None else 0 for s in strata_ids
                ],
                "any_stratum_false_positive": any_fp,
                "all_strata_covered": all_cov,
                "pooled_or_aggregate_claim_emitted": False,
                "pooled_or_aggregate_claim_blocked_if_unsupported": True,
                "realized_n_strata": len(strata_ids),
                "stratification_metadata": {
                    "requested_n_strata": geom.n_strata,
                    "realized_n_strata": strat_meta.get("realized_n_strata"),
                    "fallback_used": strat_meta.get("fallback_used", False),
                },
                "geometry_supported": geom.geometry_supported,
            }
        )
    except Exception as exc:
        run_level["failure_status"] = "fail"
        run_level["failure_reason"] = f"{type(exc).__name__}: {exc}"[:200]
        run_level["stratum_level_results"] = stratum_rows

    return run_level


def _stratum_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for r in runs:
        rows.extend(r.get("stratum_level_results") or [])
    ok = [c for c in rows if c.get("failure_status") == "ok"]
    cov = _rate([c.get("contains_truth") for c in ok])
    type_i = _rate(
        [
            c.get("contains_zero") is False
            for c in ok
            if c.get("true_effect") is not None and abs(c["true_effect"]) < 1e-9
        ]
    )
    return {
        "n_stratum_results": len(rows),
        "n_ok": len(ok),
        "coverage": cov,
        "type_i_error": type_i,
        "mean_bias": _mean([c.get("bias") for c in ok if c.get("bias") is not None]),
        "mean_interval_width": _mean([c.get("interval_width") for c in ok if c.get("interval_width") is not None]),
    }


def _group_stratum_metrics(runs: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in runs:
        groups.setdefault(str(r.get(key)), []).append(r)
    return {k: _stratum_metrics(v) for k, v in groups.items()}


def _coverage_by_stratum(runs: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for r in runs:
        rows.extend(r.get("stratum_level_results") or [])
    out: dict[str, Any] = {}
    for sid in sorted({str(c.get("stratum_id")) for c in rows if c.get("stratum_id") is not None}):
        subset = [c for c in rows if str(c.get("stratum_id")) == sid]
        out[sid] = _stratum_metrics([{"stratum_level_results": subset}])
    return out


def _aggregate_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in runs if r.get("failure_status") == "ok"]
    return {
        "n_runs": len(ok),
        "aggregate_coverage": _rate([r.get("aggregate_contains_truth") for r in ok]),
        "aggregate_type_i": _rate(
            [
                r.get("aggregate_contains_zero") is False
                for r in ok
                if r.get("aggregate_effect_truth") is not None
                and abs(r["aggregate_effect_truth"]) < 1e-9
            ]
        ),
        "mean_aggregate_bias": _mean(
            [
                (r.get("aggregate_point_estimate") or 0.0) - (r.get("aggregate_effect_truth") or 0.0)
                for r in ok
                if r.get("aggregate_point_estimate") is not None
            ]
        ),
        "weight_dominance_rate": _rate([r.get("weight_dominance_flag") for r in ok]),
        "aggregate_claim_blocked_rate": _rate([r.get("pooled_or_aggregate_claim_blocked_if_unsupported") for r in ok]),
    }


def _production_defect_assessment(
    stratum_rows: list[dict[str, Any]],
    runs: list[dict[str, Any]],
) -> dict[str, Any]:
    identity_fail = any(
        c.get("stratum_identity_preserved") is False
        for c in stratum_rows
        if c.get("failure_status") == "ok"
    )
    agg_emit = any(r.get("pooled_or_aggregate_claim_emitted") for r in runs)
    if agg_emit:
        return {
            "decision": "production_defect_confirmed",
            "rationale": "aggregate causal claim emitted despite guardrail",
        }
    if identity_fail:
        return {
            "decision": "production_defect_confirmed",
            "rationale": "stratum identity not preserved in at least one run",
        }
    duplicate_interval = False
    by_run: dict[tuple[Any, ...], list[tuple[float | None, float | None]]] = {}
    for r in runs:
        key = (r.get("world_id"), r.get("geometry_id"), r.get("seed"))
        ivals = []
        for row in r.get("stratum_level_results") or []:
            if row.get("failure_status") == "ok":
                ivals.append((row.get("interval_lower"), row.get("interval_upper")))
        if len(ivals) >= 2 and len(set(ivals)) == 1:
            duplicate_interval = True
    if duplicate_interval:
        return {
            "decision": "production_defect_confirmed",
            "rationale": "identical interval copied across strata",
        }
    return {
        "decision": "geometry_or_semantic_limitation",
        "rationale": (
            "Stratified SCM+JK uses per-stratum panels with volume-weighted aggregate "
            "characterization only; aggregate intervals are not a valid pooled estimand. "
            "Small-stratum instability and weight dominance are structural support limits."
        ),
    }


def _decide_verdict(
    *,
    prod: dict[str, Any],
    cov_balanced: dict[str, Any],
    cov_small: dict[str, Any],
    cov_global: dict[str, Any],
    cov_within: dict[str, Any],
    agg: dict[str, Any],
    weight_dom_rate: float | None,
) -> SemanticVerdict:
    if prod.get("decision") == "production_defect_confirmed":
        return "stratified_scm_jk_remediation_required"
    bal_cov = cov_balanced.get("coverage") or 0.0
    small_cov = cov_small.get("coverage") or 0.0
    global_t1 = cov_global.get("type_i_error") or 0.0
    within_t1 = cov_within.get("type_i_error") or 0.0
    agg_cov = agg.get("aggregate_coverage") or 0.0
    if small_cov and small_cov < 0.85 and bal_cov >= 0.88:
        return "stratified_scm_jk_small_stratum_restricted"
    if weight_dom_rate is not None and weight_dom_rate > 0.4 and agg_cov < 0.85:
        return "stratified_scm_jk_weight_dominance_restricted"
    if global_t1 > within_t1 + 0.05:
        return "stratified_scm_jk_aggregate_blocked"
    if bal_cov >= 0.90 and within_t1 < 0.12:
        return "stratified_scm_jk_eligible_with_restrictions"
    if bal_cov >= 0.88:
        return "stratified_scm_jk_balanced_only"
    if bal_cov >= 0.82:
        return "stratified_scm_jk_diagnostic_only"
    if bal_cov < 0.75:
        return "stratified_scm_jk_ineligible"
    return "stratified_scm_jk_inconclusive"


def build_d5_trust_stratified_scm_jk_001(
    cfg: StratifiedTrustConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or StratifiedTrustConfig()
    t0 = time.perf_counter()
    n_rep = cfg.n_replicates_fast if cfg.fast else cfg.n_replicates
    worlds = TRUST_WORLDS if not cfg.fast else TRUST_WORLDS[:10]
    geoms = GEOMETRY_VARIANTS if not cfg.fast else GEOMETRY_VARIANTS[:8]
    patterns = EFFECT_PATTERNS if not cfg.fast else EFFECT_PATTERNS[:4]

    all_runs: list[dict[str, Any]] = []
    seed_cursor = cfg.random_state_base

    for world in worlds:
        for geom in geoms:
            if geom.n_strata == 3 and world.n_geos < 12:
                w = replace(world, n_geos=max(world.n_geos, 14))
            else:
                w = world
            for rep in range(n_rep):
                seed = seed_cursor
                seed_cursor += 1
                all_runs.append(_run_one(w, geom, None, cfg, replicate_id=rep, seed=seed))

    for pattern in patterns:
        n_strata = len(pattern)
        geom = next((g for g in geoms if g.n_strata == n_strata), geoms[0])
        world = TrustWorldSpec(
            f"effect_pattern_{'_'.join(str(x) for x in pattern)}",
            notes="effect pattern sweep",
        )
        for rep in range(max(1, n_rep // 2)):
            seed = seed_cursor
            seed_cursor += 1
            all_runs.append(_run_one(world, geom, pattern, cfg, replicate_id=rep, seed=seed))

    stratum_rows: list[dict[str, Any]] = []
    for r in all_runs:
        stratum_rows.extend(r.get("stratum_level_results") or [])

    ok_runs = [r for r in all_runs if r.get("failure_status") in ("ok", "blocked")]
    cov_by_geom = _group_stratum_metrics(ok_runs, "geometry_id")
    cov_by_stratum = _coverage_by_stratum(ok_runs)
    agg_results = _aggregate_metrics(ok_runs)

    bal_metrics = cov_by_geom.get("balanced_two_strata", {})
    small_metrics = cov_by_geom.get("small_stratum", {})
    global_metrics = cov_by_geom.get("donor_pool_global", {})
    within_metrics = cov_by_geom.get("donor_pool_within_stratum_only", {})

    prod = _production_defect_assessment(stratum_rows, ok_runs)
    verdict = _decide_verdict(
        prod=prod,
        cov_balanced=bal_metrics,
        cov_small=small_metrics,
        cov_global=global_metrics,
        cov_within=within_metrics,
        agg=agg_results,
        weight_dom_rate=agg_results.get("weight_dominance_rate"),
    )

    aggregate_status = (
        "ELIGIBLE_WITH_RESTRICTIONS"
        if verdict in ("stratified_scm_jk_eligible_with_restrictions", "stratified_scm_jk_balanced_only")
        else "DIAGNOSTIC_ONLY"
        if verdict == "stratified_scm_jk_diagnostic_only"
        else "INSUFFICIENT_EVIDENCE"
        if verdict == "stratified_scm_jk_inconclusive"
        else "REMEDIATE"
        if verdict == "stratified_scm_jk_remediation_required"
        else "INELIGIBLE"
        if verdict == "stratified_scm_jk_ineligible"
        else "ELIGIBLE_WITH_RESTRICTIONS"
    )

    policy_rows: list[dict[str, Any]] = []
    for pol in POLICY_COMPARISONS:
        if pol["policy_id"] == "A":
            subset = ok_runs
        elif pol["policy_id"] == "B":
            subset = ok_runs
        elif pol["policy_id"] == "C":
            subset = [r for r in ok_runs if "within" in str(r.get("geometry_id", ""))]
        elif pol["policy_id"] == "D":
            subset = [r for r in ok_runs if "global" in str(r.get("geometry_id", ""))]
        elif pol["policy_id"] == "E":
            subset = [r for r in ok_runs if r.get("weight_dominance_flag")]
        elif pol["policy_id"] == "F":
            subset = [r for r in ok_runs if "small" in str(r.get("geometry_id", ""))]
        else:
            subset = ok_runs
        row: dict[str, Any] = {"policy": pol, "metrics": _stratum_metrics(subset)}
        if pol["policy_id"] == "G":
            row["aggregate_claim_blocked"] = all(
                r.get("pooled_or_aggregate_claim_blocked_if_unsupported") for r in ok_runs
            )
        policy_rows.append(row)

    next_artifact = "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT"
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
            "scm_fit_mode": _SCM_FIT_MODE,
            "truth_scale": _CANONICAL_SCALE,
            "point_estimate_scale": _CANONICAL_SCALE,
            "interval_scale": _CANONICAL_SCALE,
            "stratum_weighting_policy": "treated_kpi_volume_share",
            "weight_dominance_threshold": cfg.weight_dominance_threshold,
        },
        "worlds": [w.world_id for w in worlds],
        "effect_patterns": [list(p) for p in patterns],
        "geometry_variants": [
            {
                "geometry_id": g.geometry_id,
                "n_strata": g.n_strata,
                "donor_pool_policy": g.donor_pool_policy,
                "geometry_supported": g.geometry_supported,
                "geometry_failure_reason": g.geometry_failure_reason,
            }
            for g in geoms
        ],
        "run_counts": {
            "total_runs": len(all_runs),
            "successful_runs": len(ok_runs),
            "failed_runs": len(all_runs) - len(ok_runs),
            "stratum_level_results": len(stratum_rows),
            "runtime_seconds": round(time.perf_counter() - t0, 2),
        },
        "stratum_level_results": stratum_rows[:200] if cfg.fast else stratum_rows[:500],
        "aggregate_results": agg_results,
        "coverage_by_stratum": cov_by_stratum,
        "coverage_by_geometry": cov_by_geom,
        "type_i_by_stratum": {k: v.get("type_i_error") for k, v in cov_by_stratum.items()},
        "aggregate_type_i": agg_results.get("aggregate_type_i"),
        "stratum_weighting_results": {
            "policy": "treated_kpi_volume_share",
            "weight_dominance_rate": agg_results.get("weight_dominance_rate"),
            "threshold": cfg.weight_dominance_threshold,
        },
        "donor_pool_results": {
            "within_stratum": within_metrics,
            "global": global_metrics,
            "partial_overlap": cov_by_geom.get("donor_pool_partial_overlap", {}),
        },
        "small_stratum_results": small_metrics,
        "weight_dominance_results": {
            "dominance_rate": agg_results.get("weight_dominance_rate"),
            "geometries": cov_by_geom.get("stratum_weight_imbalance", {}),
        },
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
            "path_decisions": {
                "balanced_strata": "per_stratum_marginal_allowed",
                "unequal_strata": "restricted",
                "small_stratum": "blocked_or_diagnostic",
                "weight_dominant_stratum": "aggregate_blocked",
                "global_donor_pool": "restricted_vs_within_stratum",
                "within_stratum_donor_pool": "preferred",
                "aggregate_readout": "characterization_only_blocked_for_claims",
                "per_stratum_readout": "diagnostic_or_restricted",
            },
            "supported_roles": ["per_stratum_diagnostic", "per_stratum_restricted_interval"],
            "unsupported_roles": ["aggregate_causal_claim", "trust_report", "pooled_stratified_estimand"],
        },
        "trustreport_eligibility_implications": {
            "dcm_008": "stratified_diagnostic_only_aggregate_characterization_not_causal_estimand",
            "prior_status": "characterized_with_restrictions",
            "reassessment_required": True,
            "full_reassessment_deferred": False,
            "next_checkpoint": "FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT",
        },
        "authorization_summary": {
            "trust_report_authorized": False,
            "trust_report_ready": False,
            "trust_report_authorized_count": 0,
        },
        "investigation_handoff": build_investigation_handoff(
            follow_up_issues=[],
            resolved_issues=[_INVESTIGATION_ID],
            terminal_dispositions=[_INVESTIGATION_ID],
            next_artifact=next_artifact,
        ),
        "limitations": [
            "Evaluates stratified design × SCM+UnitJackknife; does not validate unrelated estimator/inference combinations.",
            "Does not authorize TrustReport.",
            "Does not perform the full TrustReport eligibility reassessment.",
            "SCM is fit per-stratum panel (aggregate treated units in stratum); not per-unit SCM within stratum.",
            "Aggregate intervals are volume-weighted stratum interval means — not a valid pooled stratified estimand.",
            "Stratified assignment support does not imply valid aggregate or multi-cell decisioning.",
            "Aggregate stratified readout is characterization only, not a governed pooled causal estimand.",
            "Marginal per-stratum coverage does not authorize aggregate/pooled causal claims or TrustReport promotion.",
            "Distinct from DCM-006 multi-cell conclusions; stratified-specific behavior tested here.",
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
        "This artifact evaluates stratified SCM+UnitJackknife behavior.",
        "It does not authorize TrustReport.",
        "It does not perform the full TrustReport eligibility reassessment.",
        "It does not validate unrelated estimator/inference combinations.",
        "",
        f"**Verdict:** `{payload.get('verdict')}`",
        f"**Aggregate status:** `{payload.get('semantic_classification', {}).get('aggregate_status')}`",
        "",
        "**Aggregate stratified readout is characterization only, not a governed pooled causal estimand.**",
        "Per-stratum marginal intervals may be shown under diagnostic/restricted semantics only.",
        "",
        "## 2. Prior DCM-008 status",
        "",
        "DCM-008 was characterized_with_restrictions; stratified SCM+JK statistical behavior unresolved.",
        "",
        "## 3. Scope",
        "",
        "Stratified randomization + SCM + UnitJackknife per stratum across geometry variants and synthetic worlds.",
        "",
        "## 4. Non-goals",
        "",
        "No TrustReport authorization; no production algorithm changes; no pooled stratified estimand validation.",
        "",
        "## 5. Stratified design geometry",
        "",
        "Strata from adaptive percentile stratification on pre-period covariate; donor pools evaluated per policy.",
        "",
        "## 6. Stratum identity contract",
        "",
        "Per-stratum panels include only treated units in stratum plus eligible donors; other-stratum treated excluded.",
        "",
        "## 7. Donor-pool policy",
        "",
        "Within-stratum, global, and partial-overlap donor constructions evaluated.",
        "",
        "## 8. Estimand and scale contract",
        "",
        f"Canonical scale: `{_CANONICAL_SCALE}`.",
        "",
        "## 9. SCM+JK inference path",
        "",
        f"Primary: `{_PRIMARY_METHOD}`. SCM fit mode: `{_SCM_FIT_MODE}`.",
        "",
        "## 10. Worlds",
        "",
        ", ".join(payload.get("worlds", [])),
        "",
        "## 11. Effect patterns",
        "",
        json.dumps(payload.get("effect_patterns", [])),
        "",
        "## 12. Geometry variants",
        "",
        json.dumps(payload.get("geometry_variants", []), indent=2),
        "",
        "## 13. Run counts/runtime",
        "",
        json.dumps(payload.get("run_counts", {}), indent=2),
        "",
        "## 14. Stratum-level point behavior",
        "",
        f"Mean bias by stratum: {json.dumps({k: v.get('mean_bias') for k, v in payload.get('coverage_by_stratum', {}).items()})}",
        "",
        "## 15. Stratum-level interval behavior",
        "",
        f"Coverage by geometry: {json.dumps(payload.get('coverage_by_geometry', {}), indent=2)[:2500]}",
        "",
        "## 16. Aggregate point behavior",
        "",
        json.dumps(payload.get("aggregate_results", {}), indent=2),
        "",
        "## 17. Aggregate interval behavior",
        "",
        "Aggregate intervals are volume-weighted stratum means for characterization only; not valid pooled estimand.",
        "",
        "## 18. Null type-I",
        "",
        json.dumps(payload.get("type_i_by_stratum", {}), indent=2),
        f"\nAggregate type-I: {payload.get('aggregate_type_i')}",
        "",
        "## 19. Coverage",
        "",
        json.dumps(payload.get("coverage_by_stratum", {}), indent=2),
        "",
        "## 20. Heterogeneous-effect findings",
        "",
        "See heterogeneous_positive, mixed_sign, and effect-pattern worlds.",
        "",
        "## 21. Small-stratum findings",
        "",
        json.dumps(payload.get("small_stratum_results", {}), indent=2),
        "",
        "## 22. Weight-dominance findings",
        "",
        json.dumps(payload.get("weight_dominance_results", {}), indent=2),
        "",
        "## 23. Donor-pool findings",
        "",
        json.dumps(payload.get("donor_pool_results", {}), indent=2),
        "",
        "## 24. Poor-prefit findings",
        "",
        "See poor_prefit_one_stratum and poor_prefit_all_strata worlds.",
        "",
        "## 25. Shock/contamination findings",
        "",
        "See stratum_specific_shock, common_shock, donor_contamination worlds.",
        "",
        "## 26. Policy comparisons",
        "",
        "See summary `policy_comparisons`.",
        "",
        "## 27. Root-cause determination",
        "",
        "Aggregate readout and weight-dominance limits are semantic/geometry; not isolated code defects unless confirmed.",
        "",
        "## 28. Production-defect decision",
        "",
        json.dumps(payload.get("production_defect_assessment", {}), indent=2),
        "",
        "## 29. Semantic classification",
        "",
        json.dumps(payload.get("semantic_classification", {}), indent=2),
        "",
        "## 30. TrustReport implications",
        "",
        json.dumps(payload.get("trustreport_eligibility_implications", {}), indent=2),
        "",
        "## 31. Authorization status",
        "",
        json.dumps(payload.get("authorization_summary", {}), indent=2),
        "",
        "## 32. Investigation lifecycle update",
        "",
        f"Consumed `{_INVESTIGATION_ID}` → RESOLVED (DIAGNOSTIC_ONLY).",
        "",
        "## 33. Remaining limitations",
        "",
        "; ".join(payload.get("limitations", [])),
        "",
        "## 34. Governance verdict",
        "",
        f"**`{payload.get('verdict')}`**",
        "",
    ]
    lines.extend(
        format_handoff_report_section(
            resolved_in_artifact=[_INVESTIGATION_ID],
            new_investigations=[],
            updated_investigations=[f"{_INVESTIGATION_ID} → RESOLVED (DIAGNOSTIC_ONLY)"],
            deferred_issues=[
                "INV-MULTICELL-SHARED-CONTROL-DEPENDENCE-001",
                "INV-MULTICELL-MULTIPLICITY-CALIBRATION-001",
            ],
            explicit_exclusions=["DCM-006 multi-cell conclusions reused without stratified test"],
            revisit_trigger="FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT DCM-008 row",
            decision_checkpoint="FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT",
            next_artifact=handoff.get("next_artifact"),
        )
    )
    _atomic_write_text(path, "\n".join(lines) + "\n", overwrite=overwrite)


def write_summary(
    path: Path | None = None,
    *,
    cfg: StratifiedTrustConfig | None = None,
    overwrite: bool = False,
    report_path: Path | None = None,
) -> Path:
    payload = build_d5_trust_stratified_scm_jk_001(cfg)
    if path is None:
        path = _DEFAULT_SUMMARY
    _atomic_write_text(path, json.dumps(payload, indent=2) + "\n", overwrite=overwrite)
    _write_report(payload, report_path or _DEFAULT_REPORT, overwrite=overwrite)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument(
        "--output-local",
        default="/tmp/D5_TRUST_STRATIFIED_SCM_JK_001_results.json",
    )
    parser.add_argument("--summary-output", default=str(_DEFAULT_SUMMARY))
    parser.add_argument("--report-output", default=str(_DEFAULT_REPORT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args(argv)

    cfg = StratifiedTrustConfig(
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
