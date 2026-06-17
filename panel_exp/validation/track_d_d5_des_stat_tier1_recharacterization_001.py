"""D5-DES-STAT-TIER1-RECHARACTERIZATION-001 — post-fix tier-1 baseline refresh."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from math import floor
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from panel_exp import evidence as evidence_module
from panel_exp.design.assign import (
    BalancedRandomization,
    CompleteRandomization,
    Rerandomization,
    StratifiedRandomization,
    greedy_match_markets,
)
from panel_exp.design.multicell_feasibility import (
    compute_control_burden,
    diagnose_assignment,
    per_cell_balance_metrics,
)
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.design_contract_builder_001 import build_and_validate_tier1_contract
from panel_exp.validation.design_guardrail_runtime_001 import evaluate_design_contract_guardrails
from panel_exp.validation.track_d_d5_des_stat_tier1_001 import (
    ALL_WORLD_IDS,
    GREEDY_TREATMENT_PROBABILITIES,
    MIN_CONTROL_THRESHOLD,
    SHARED_SEEDS,
    D5DesStatTier1Config,
    DesignFamilySpec,
    WorldContext,
    _TrackedRerandomization,
    _assignment_counts,
    _balance_metrics,
    _evaluate_run,
    _realized_treatment_share,
    _world_context,
    synthesize_panel,
)
from panel_exp.validation.track_d_d5_des_stat_multicell_001 import (
    _world_spec as _multicell_world_spec,
    synthesize_panel as synthesize_multicell_panel,
)

GENERATOR_VERSION = "1.0.0"
ARTIFACT_ID = "D5-DES-STAT-TIER1-RECHARACTERIZATION-001"
HISTORICAL_ARTIFACT_ID = "D5-DES-STAT-TIER1-001"

Lane = Literal["single_cell_tier1", "legacy_reference", "multicell_per_cell_only"]

Verdict = Literal[
    "tier1_recharacterized_corrected_defaults_no_promotion",
    "tier1_recharacterized_mixed_method_specific_restrictions",
    "tier1_recharacterized_with_remaining_blocking_failures",
    "tier1_recharacterization_inconclusive",
    "tier1_recharacterization_failed",
]

MULTICELL_WORLD_IDS: tuple[str, ...] = (
    "balanced_two_cell",
    "balanced_three_cell",
    "shared_control_overload_world",
    "pooled_claim_trap_world",
    "cell_size_imbalance",
    "concurrent_experiment_pressure",
)


@dataclass
class RecharConfig:
    fast: bool = False
    n_pre: int = 30
    n_post: int = 10
    n_units: int = 18
    replicates_single_cell: int = 10
    replicates_legacy: int = 5
    replicates_multicell: int = 5
    treatment_probability_default: float = 0.35
    rerandomization_max_iter: int = 200
    rerandomization_target_imbalance: float = 0.01
    random_state_base: int = 20260618
    include_contract_guardrail: bool = True


@dataclass
class DesignLaneSpec:
    design_inventory_id: str
    lane: Lane
    label: str
    registry_key: str
    base_randomizer_cls: type
    is_rerandomization_wrapper: bool = False
    design_kwargs: dict[str, Any] = field(default_factory=dict)
    n_test_grps: int = 1


def _tier1_cfg(rechar: RecharConfig) -> D5DesStatTier1Config:
    return D5DesStatTier1Config(
        fast=rechar.fast,
        n_pre=rechar.n_pre,
        n_post=rechar.n_post,
        n_units=rechar.n_units,
        replicates_per_cell=2 if rechar.fast else rechar.replicates_single_cell,
        replicates_exhaustion=3,
        treatment_probability_default=rechar.treatment_probability_default,
        rerandomization_max_iter=rechar.rerandomization_max_iter,
        rerandomization_target_imbalance=rechar.rerandomization_target_imbalance,
        random_state_base=rechar.random_state_base,
    )


def expected_run_matrix_size(cfg: RecharConfig) -> dict[str, int]:
    """Deterministic run-count model: designs × worlds × treatment_points × replicates × seeds."""
    seeds = SHARED_SEEDS[:2] if cfg.fast else SHARED_SEEDS
    worlds = list(ALL_WORLD_IDS[:4] if cfg.fast else ALL_WORLD_IDS)
    rep_sc = 1 if cfg.fast else cfg.replicates_single_cell
    rep_legacy = 1 if cfg.fast else cfg.replicates_legacy
    rep_mc = 1 if cfg.fast else cfg.replicates_multicell
    n_seeds = len(seeds)

    lane_a = 0
    for spec in CORRECTED_DESIGNS:
        for world_id in worlds:
            tp_list = [cfg.treatment_probability_default]
            if spec.design_inventory_id == "DES-001" and world_id in (
                "treatment_pool_exhaustion_world",
                "balanced_markets",
            ):
                tp_list = list(
                    GREEDY_TREATMENT_PROBABILITIES[:2] if cfg.fast else GREEDY_TREATMENT_PROBABILITIES
                )
            lane_a += len(tp_list) * rep_sc * n_seeds

    lane_b = 0
    for spec in LEGACY_DESIGNS:
        if spec.lane == "legacy_reference" and spec.design_inventory_id == "DES-011":
            continue
        lane_b += len(worlds) * rep_legacy * n_seeds

    mc_worlds = list(MULTICELL_WORLD_IDS[:2] if cfg.fast else MULTICELL_WORLD_IDS)
    mc_unit_counts = [18, 20] if cfg.fast else [12, 18, 20]
    lane_c = len(MULTICELL_DESIGNS) * len(mc_worlds) * len(mc_unit_counts) * rep_mc * n_seeds

    return {
        "single_cell_tier1": lane_a,
        "legacy_reference": lane_b,
        "multicell_per_cell_only": lane_c,
        "total": lane_a + lane_b + lane_c,
    }


CORRECTED_DESIGNS: tuple[DesignLaneSpec, ...] = (
    DesignLaneSpec(
        "DES-001",
        "single_cell_tier1",
        "greedy_corrected",
        "greedy_match_markets",
        greedy_match_markets,
        design_kwargs={"feasibility_policy": "control_reservation", "min_control_units": MIN_CONTROL_THRESHOLD},
    ),
    DesignLaneSpec(
        "DES-002",
        "single_cell_tier1",
        "complete_randomization",
        "completerandomization",
        CompleteRandomization,
    ),
    DesignLaneSpec(
        "DES-003",
        "single_cell_tier1",
        "balanced_randomization",
        "balancedrandomization",
        BalancedRandomization,
    ),
    DesignLaneSpec(
        "DES-004",
        "single_cell_tier1",
        "stratified_corrected",
        "stratifiedrandomization",
        StratifiedRandomization,
        design_kwargs={"stratification_policy": "adaptive_strata"},
    ),
    DesignLaneSpec(
        "DES-006",
        "single_cell_tier1",
        "rerandomization",
        "completerandomization",
        CompleteRandomization,
        is_rerandomization_wrapper=True,
    ),
)

LEGACY_DESIGNS: tuple[DesignLaneSpec, ...] = (
    DesignLaneSpec(
        "DES-001",
        "legacy_reference",
        "greedy_legacy",
        "greedy_match_markets",
        greedy_match_markets,
        design_kwargs={"feasibility_policy": "legacy", "min_control_units": MIN_CONTROL_THRESHOLD},
    ),
    DesignLaneSpec(
        "DES-004",
        "legacy_reference",
        "stratified_legacy",
        "stratifiedrandomization",
        StratifiedRandomization,
        design_kwargs={"stratification_policy": "legacy"},
    ),
    DesignLaneSpec(
        "DES-011",
        "legacy_reference",
        "multicell_legacy",
        "completerandomization",
        CompleteRandomization,
        design_kwargs={"multicell_policy": "legacy", "min_control_units": MIN_CONTROL_THRESHOLD},
        n_test_grps=2,
    ),
)

MULTICELL_DESIGNS: tuple[DesignLaneSpec, ...] = (
    DesignLaneSpec(
        "DES-011",
        "multicell_per_cell_only",
        "multicell_corrected",
        "completerandomization",
        CompleteRandomization,
        design_kwargs={"multicell_policy": "control_reservation", "min_control_units": MIN_CONTROL_THRESHOLD},
        n_test_grps=2,
    ),
    DesignLaneSpec(
        "DES-011",
        "multicell_per_cell_only",
        "multicell_legacy",
        "completerandomization",
        CompleteRandomization,
        design_kwargs={"multicell_policy": "legacy", "min_control_units": MIN_CONTROL_THRESHOLD},
        n_test_grps=2,
    ),
)


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


def _run_assignment(
    spec: DesignLaneSpec,
    wide: pd.DataFrame,
    *,
    seed: int,
    n_pre: int,
    treatment_probability: float,
    constraint_kwargs: dict[str, Any],
    world_params: dict[str, Any],
    cfg: D5DesStatTier1Config,
) -> tuple[dict[str, list[str]] | None, dict[str, Any]]:
    import pandas as pd  # noqa: F811 — local for type clarity

    panel = PanelDataset(wide.copy())
    pre = TimePeriod(0, n_pre)
    diag: dict[str, Any] = {"design_label": spec.label, "lane": spec.lane}
    kw: dict[str, Any] = {}
    if constraint_kwargs.get("_excluded_units"):
        kw["control_test_blacklist"] = list(constraint_kwargs["_excluded_units"])
    for key in (
        "control_whitelist",
        "test_whitelist",
        "control_blacklist",
        "test_blacklist",
        "control_test_blacklist",
    ):
        if key in constraint_kwargs:
            kw[key] = constraint_kwargs[key]
    kwargs = dict(spec.design_kwargs)
    n_test_grps = spec.n_test_grps
    try:
        if spec.is_rerandomization_wrapper:
            design: Any = _TrackedRerandomization(
                treatment_probability=treatment_probability,
                max_iter=cfg.rerandomization_max_iter,
                target_imbalance=cfg.rerandomization_target_imbalance,
                base_randomizer_cls=CompleteRandomization,
                random_state=seed,
            )
            assignment = design.assign(
                panel_data=panel, pre_treatment_period=pre, n_test_grps=1, **kw
            )
            diag["rerandomization_attempts"] = design.last_attempts
            diag["rerandomization_accepted"] = design.accepted
        elif spec.design_inventory_id == "DES-001":
            design = greedy_match_markets(
                func_to_optimize="corr",
                treatment_probability=treatment_probability,
                random_state=seed,
                **kwargs,
            )
            assignment = design.assign(
                panel_data=panel, pre_treatment_period=pre, n_test_grps=1, **kw
            )
            if getattr(design, "last_feasibility_metadata", None):
                diag.update(design.last_feasibility_metadata)
        elif spec.base_randomizer_cls is CompleteRandomization:
            design = CompleteRandomization(
                treatment_probability=treatment_probability,
                random_state=seed,
                **kwargs,
            )
            assignment = design.assign(
                panel_data=panel, pre_treatment_period=pre, n_test_grps=n_test_grps, **kw
            )
            if getattr(design, "last_multicell_metadata", None):
                diag.update(design.last_multicell_metadata)
        elif spec.base_randomizer_cls is BalancedRandomization:
            design = BalancedRandomization(
                treatment_probability=treatment_probability, random_state=seed
            )
            assignment = design.assign(
                panel_data=panel, pre_treatment_period=pre, n_test_grps=1, **kw
            )
        elif spec.base_randomizer_cls is StratifiedRandomization:
            n_percentiles = int(world_params.get("n_strata") or 10)
            design = StratifiedRandomization(
                treatment_probability=treatment_probability,
                random_state=seed,
                **kwargs,
            )
            assignment = design.assign(
                panel_data=panel,
                pre_treatment_period=pre,
                n_test_grps=1,
                n_percentiles=n_percentiles,
                **kw,
            )
            if getattr(design, "last_stratification_metadata", None):
                diag.update(design.last_stratification_metadata)
        else:
            raise ValueError(f"unsupported design {spec.design_inventory_id}")
    except Exception as exc:
        diag["assignment_error"] = type(exc).__name__
        diag["assignment_error_message"] = str(exc)[:500]
        return None, diag
    return dict(assignment), diag


def _contract_summary(
    spec: DesignLaneSpec,
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    n_pre: int,
    tp: float,
    seed: int,
    diag: dict[str, Any],
) -> dict[str, Any]:
    design_method = (
        "Rerandomization" if spec.is_rerandomization_wrapper else spec.base_randomizer_cls.__name__
    )
    geo_spec = spec_from_geo_design(
        f"rechar-{spec.label}-{seed}",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(0, n_pre),
        experiment_period=TimePeriod(n_pre, wide.shape[1]),
        design_method=design_method,
        random_state=seed,
        treatment_probability=tp,
        n_test_groups=spec.n_test_grps,
    )
    design_kwargs: dict[str, Any] = {}
    if diag.get("cell_ids"):
        design_kwargs["last_multicell_metadata"] = diag
    contract, summary = build_and_validate_tier1_contract(
        spec=geo_spec,
        assignment=assignment,
        registry_key=spec.registry_key,
        base_randomizer_cls=spec.base_randomizer_cls,
        n_test_grps=spec.n_test_grps,
        treatment_probability=tp,
        is_rerandomization_wrapped=spec.is_rerandomization_wrapper,
        wide_data=wide,
        design_kwargs=design_kwargs,
        package_version=evidence_module.__version__,
    )
    guardrail = evaluate_design_contract_guardrails(
        {"design_contract": contract, "contract_validation": summary}
    )
    multi = contract.get("multi_cell", {})
    return {
        "contract_status": summary.get("status"),
        "contract_complete_allowed": summary.get("contract_complete_allowed"),
        "guardrail_status": guardrail.status,
        "downstream_authorization_status": contract.get("governance", {}).get(
            "downstream_authorization_status"
        ),
        "pooled_claims_allowed": multi.get("pooled_claims_allowed"),
        "geometry_id": contract.get("geometry", {}).get("geometry_id"),
    }


def run_single_single_cell(
    spec: DesignLaneSpec,
    world_ctx: WorldContext,
    *,
    seed: int,
    replicate: int,
    cfg: D5DesStatTier1Config,
    rechar: RecharConfig,
    include_contract: bool,
) -> dict[str, Any]:
    wide = synthesize_panel(world_ctx, seed + replicate)
    n_units = wide.shape[0]
    assignment, diag = _run_assignment(
        spec,
        wide,
        seed=seed + replicate,
        n_pre=world_ctx.n_pre,
        treatment_probability=world_ctx.treatment_probability,
        constraint_kwargs=world_ctx.constraint_kwargs,
        world_params=world_ctx.world_params,
        cfg=cfg,
    )
    ok = assignment is not None
    counts = (
        _assignment_counts(assignment, n_units)
        if assignment
        else {
            "n_control": 0,
            "n_treated": 0,
            "n_assigned": 0,
            "n_unassigned": n_units,
            "duplicate_collision_count": 0,
            "minimum_control_violation": True,
        }
    )
    balance = (
        _balance_metrics(wide, assignment, world_ctx.n_pre)
        if assignment
        else {"max_absolute_smd": float("nan")}
    )
    tp_realized = _realized_treatment_share(counts, n_units)
    outcome, reasons = _evaluate_run(
        counts,
        balance,
        assignment_ok=ok,
        treatment_probability_requested=world_ctx.treatment_probability,
        treatment_probability_realized=tp_realized,
    )
    contract_diag: dict[str, Any] = {}
    if ok and include_contract and rechar.include_contract_guardrail:
        contract_diag = _contract_summary(
            spec, wide, assignment, n_pre=world_ctx.n_pre, tp=world_ctx.treatment_probability,
            seed=seed, diag=diag,
        )
    return {
        "lane": spec.lane,
        "design_inventory_id": spec.design_inventory_id,
        "design_label": spec.label,
        "world_id": world_ctx.world_id,
        "seed": seed,
        "replicate": replicate,
        "n_units": n_units,
        "n_test_grps": 1,
        "assignment_status": "success" if ok else "failed",
        "run_outcome": outcome,
        "evaluation_reasons": reasons,
        "metrics": {**counts, **balance},
        "diagnostics": {**diag, **contract_diag},
        "assignment_hash": assignment_hash(assignment) if assignment else None,
    }


def run_single_multicell(
    spec: DesignLaneSpec,
    *,
    world_id: str,
    n_units: int,
    tp: float,
    seed: int,
    replicate: int,
    rechar: RecharConfig,
) -> dict[str, Any]:
    mspec = _multicell_world_spec(world_id, n_units, tp)
    n_cells = 3 if world_id == "balanced_three_cell" else mspec.n_test_grps
    wide = synthesize_multicell_panel(mspec, seed + replicate)
    cfg = _tier1_cfg(rechar)
    mc_spec = DesignLaneSpec(
        spec.design_inventory_id,
        spec.lane,
        spec.label,
        spec.registry_key,
        spec.base_randomizer_cls,
        spec.is_rerandomization_wrapper,
        spec.design_kwargs,
        n_test_grps=n_cells,
    )
    assignment, diag = _run_assignment(
        mc_spec,
        wide,
        seed=seed + replicate,
        n_pre=rechar.n_pre,
        treatment_probability=tp,
        constraint_kwargs=mspec.constraint_kwargs,
        world_params=mspec.world_params,
        cfg=cfg,
    )
    ok = assignment is not None
    issues = diagnose_assignment(assignment, n_cells) if assignment else {}
    balance = (
        per_cell_balance_metrics(wide, assignment, n_cells, n_pre=rechar.n_pre)
        if assignment
        else {}
    )
    burden = compute_control_burden(assignment, n_cells) if assignment else {}
    control = assignment.get("control", []) if assignment else []
    counts = _assignment_counts(assignment, wide.shape[0]) if assignment else {}
    if assignment:
        counts["cell_collision_count"] = len(issues.get("cell_collisions", []))
        counts["minimum_control_violation"] = len(control) < MIN_CONTROL_THRESHOLD
    return {
        "lane": spec.lane,
        "design_inventory_id": spec.design_inventory_id,
        "design_label": spec.label,
        "world_id": world_id,
        "seed": seed,
        "replicate": replicate,
        "n_units": wide.shape[0],
        "n_test_grps": n_cells,
        "assignment_status": "success" if ok else "failed",
        "run_outcome": "pass" if ok and not issues.get("cell_collisions") else "warn",
        "metrics": {**counts, **balance, "control_burden_index": burden.get("control_burden_index")},
        "diagnostics": {
            **diag,
            "pooled_claims_allowed": False,
            "pooled_geometry_blocked": True,
        },
        "assignment_hash": assignment_hash(assignment) if assignment else None,
    }


def _run_matrix(cfg: RecharConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    t0 = time.perf_counter()
    records: list[dict[str, Any]] = []
    tier1_cfg = _tier1_cfg(cfg)
    seeds = SHARED_SEEDS[:2] if cfg.fast else SHARED_SEEDS
    worlds = list(ALL_WORLD_IDS[:4] if cfg.fast else ALL_WORLD_IDS)
    rep_sc = 1 if cfg.fast else cfg.replicates_single_cell
    rep_legacy = 1 if cfg.fast else cfg.replicates_legacy
    rep_mc = 1 if cfg.fast else cfg.replicates_multicell
    contract_seen: set[str] = set()
    attempted = 0

    for spec in CORRECTED_DESIGNS:
        for world_id in worlds:
            tp_list = [cfg.treatment_probability_default]
            if spec.design_inventory_id == "DES-001" and world_id in (
                "treatment_pool_exhaustion_world",
                "balanced_markets",
            ):
                tp_list = list(GREEDY_TREATMENT_PROBABILITIES[:2] if cfg.fast else GREEDY_TREATMENT_PROBABILITIES)
            for tp in tp_list:
                world_ctx = _world_context(world_id, tier1_cfg, treatment_probability=tp)
                for rep in range(rep_sc):
                    for seed in seeds:
                        attempted += 1
                        include = cfg.fast and spec.design_inventory_id not in contract_seen
                        if include:
                            contract_seen.add(spec.design_inventory_id)
                        records.append(
                            run_single_single_cell(
                                spec,
                                world_ctx,
                                seed=seed,
                                replicate=rep,
                                cfg=tier1_cfg,
                                rechar=cfg,
                                include_contract=include,
                            )
                        )

    for spec in LEGACY_DESIGNS:
        if spec.lane == "legacy_reference" and spec.design_inventory_id == "DES-011":
            continue
        for world_id in worlds:
            world_ctx = _world_context(world_id, tier1_cfg)
            for rep in range(rep_legacy):
                for seed in seeds:
                    attempted += 1
                    records.append(
                        run_single_single_cell(
                            spec,
                            world_ctx,
                            seed=seed,
                            replicate=rep,
                            cfg=tier1_cfg,
                            rechar=cfg,
                            include_contract=False,
                        )
                    )

    mc_worlds = list(MULTICELL_WORLD_IDS[:2] if cfg.fast else MULTICELL_WORLD_IDS)
    mc_unit_counts = [18, 20] if cfg.fast else [12, 18, 20]
    for spec in MULTICELL_DESIGNS:
        for world_id in mc_worlds:
            for n_units in mc_unit_counts:
                for rep in range(rep_mc):
                    for seed in seeds:
                        attempted += 1
                        records.append(
                            run_single_multicell(
                                spec,
                                world_id=world_id,
                                n_units=n_units,
                                tp=cfg.treatment_probability_default,
                                seed=seed,
                                replicate=rep,
                                rechar=cfg,
                            )
                        )

    elapsed = time.perf_counter() - t0
    expected = expected_run_matrix_size(cfg)
    runtime = {
        "total_attempted_runs": attempted,
        "expected_attempted_runs": expected["total"],
        "completed_runs": sum(1 for r in records if r["assignment_status"] == "success"),
        "failed_runs": sum(1 for r in records if r["assignment_status"] == "failed"),
        "skipped_runs": 0,
        "elapsed_seconds": round(elapsed, 3),
        "per_lane_counts": {
            lane: sum(1 for r in records if r["lane"] == lane)
            for lane in ("single_cell_tier1", "legacy_reference", "multicell_per_cell_only")
        },
        "expected_per_lane_counts": expected,
        "replicate_semantics": (
            "replicates × seeds independent (matches D5-DES-STAT-TIER1-001); "
            "not replicates divided across seeds"
        ),
    }
    assert attempted == expected["total"], (
        f"run matrix size mismatch: attempted={attempted} expected={expected['total']}"
    )
    return records, runtime


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for spec in (*CORRECTED_DESIGNS, *LEGACY_DESIGNS, *MULTICELL_DESIGNS):
        key = f"{spec.lane}:{spec.label}"
        subset = [r for r in records if r["design_label"] == spec.label and r["lane"] == spec.lane]
        if not subset:
            continue
        ok = [r for r in subset if r["assignment_status"] == "success"]
        out[key] = {
            "design_inventory_id": spec.design_inventory_id,
            "lane": spec.lane,
            "label": spec.label,
            "n_runs": len(subset),
            "assignment_success_rate": len(ok) / len(subset),
            "control_violation_rate": sum(
                1 for r in ok if r["metrics"].get("minimum_control_violation")
            )
            / max(1, len(ok)),
            "block_rate": sum(1 for r in subset if r.get("run_outcome") == "block") / len(subset),
            "mean_max_smd": float(
                np.nanmedian(
                    [r["metrics"].get("max_absolute_smd", r["metrics"].get("worst_cell_max_smd"))
                     for r in ok]
                )
            )
            if ok
            else float("nan"),
        }
    return out


def _legacy_vs_corrected(records: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [
        ("greedy_legacy", "greedy_corrected", "DES-001"),
        ("stratified_legacy", "stratified_corrected", "DES-004"),
        ("multicell_legacy", "multicell_corrected", "DES-011"),
    ]
    out: dict[str, Any] = {}
    for legacy_label, corrected_label, des_id in pairs:
        leg = [r for r in records if r["design_label"] == legacy_label and r["assignment_status"] == "success"]
        fix = [r for r in records if r["design_label"] == corrected_label and r["assignment_status"] == "success"]
        if not leg or not fix:
            continue
        key_fn = lambda r: (r["world_id"], r["seed"], r.get("replicate", 0))
        keyed_l = {key_fn(r): r for r in leg}
        keyed_f = {key_fn(r): r for r in fix}
        keys = sorted(set(keyed_l) & set(keyed_f))
        if not keys:
            continue
        smd_key = "worst_cell_max_smd" if des_id == "DES-011" else "max_absolute_smd"
        smd_delta = [
            keyed_f[k]["metrics"].get(smd_key, float("nan"))
            - keyed_l[k]["metrics"].get(smd_key, float("nan"))
            for k in keys
        ]
        viol_l = sum(1 for k in keys if keyed_l[k]["metrics"].get("minimum_control_violation"))
        viol_f = sum(1 for k in keys if keyed_f[k]["metrics"].get("minimum_control_violation"))
        out[des_id] = {
            "legacy_label": legacy_label,
            "corrected_label": corrected_label,
            "n_paired": len(keys),
            "median_smd_change_corrected_minus_legacy": float(np.nanmedian(smd_delta)),
            "control_violations_legacy": viol_l,
            "control_violations_corrected": viol_f,
            "high_smd_blocks_legacy": sum(
                1
                for k in keys
                if (keyed_l[k]["metrics"].get("max_absolute_smd") or 0) > 0.5
            ),
            "high_smd_blocks_corrected": sum(
                1
                for k in keys
                if (keyed_f[k]["metrics"].get("max_absolute_smd") or 0) > 0.5
            ),
        }
    return out


def _pairwise_comparisons(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sc = [r for r in records if r["lane"] == "single_cell_tier1" and r["assignment_status"] == "success"]
    pairs = [
        ("complete_randomization", "balanced_randomization", "complete_vs_balanced"),
        ("complete_randomization", "stratified_corrected", "complete_vs_stratified_corrected"),
        ("complete_randomization", "rerandomization", "complete_vs_rerandomization"),
        ("greedy_corrected", "complete_randomization", "greedy_corrected_vs_complete"),
    ]
    comparisons: list[dict[str, Any]] = []
    for a, b, cid in pairs:
        a_smds = [
            r["metrics"]["max_absolute_smd"]
            for r in sc
            if r["design_label"] == a and np.isfinite(r["metrics"].get("max_absolute_smd", float("nan")))
        ]
        b_smds = [
            r["metrics"]["max_absolute_smd"]
            for r in sc
            if r["design_label"] == b and np.isfinite(r["metrics"].get("max_absolute_smd", float("nan")))
        ]
        comparisons.append(
            {
                "comparison_id": cid,
                "median_smd_a": float(np.median(a_smds)) if a_smds else None,
                "median_smd_b": float(np.median(b_smds)) if b_smds else None,
                "median_smd_change_a_minus_b": (
                    float(np.median(a_smds) - np.median(b_smds))
                    if a_smds and b_smds
                    else None
                ),
                "note": "single_cell_tier1 lane only",
            }
        )
    return comparisons


def _derive_verdict(records: list[dict[str, Any]], runtime: dict[str, Any]) -> Verdict:
    if runtime["total_attempted_runs"] == 0:
        return "tier1_recharacterization_failed"
    blocks = sum(1 for r in records if r.get("run_outcome") == "block")
    if blocks > len(records) * 0.25:
        return "tier1_recharacterized_with_remaining_blocking_failures"
    greedy_ok = [
        r
        for r in records
        if r["design_label"] == "greedy_corrected"
        and r["assignment_status"] == "success"
    ]
    greedy_viol = sum(1 for r in greedy_ok if r["metrics"].get("minimum_control_violation"))
    if greedy_viol == 0 and blocks < len(records) * 0.1:
        return "tier1_recharacterized_mixed_method_specific_restrictions"
    return "tier1_recharacterized_mixed_method_specific_restrictions"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        fv = float(value)
        return fv if np.isfinite(fv) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return value


def write_artifact_atomic(path: Path, payload: dict[str, Any], *, overwrite: bool = False) -> Path:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(_json_safe(payload), indent=2, sort_keys=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
    return path


def build_summary_payload(full: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": full["artifact_id"],
        "artifact_version": full["artifact_version"],
        "generated_at": full["generated_at"],
        "git_commit": full["git_commit"],
        "config": full["config"],
        "lanes": full["lanes"],
        "designs": full["designs"],
        "worlds": full["worlds"],
        "aggregate_results": full["aggregate_results"],
        "legacy_vs_corrected": full["legacy_vs_corrected"],
        "pairwise_comparisons": full["pairwise_comparisons"],
        "failure_summary": full["failure_summary"],
        "balance_summary": full["balance_summary"],
        "multicell_summary": full["multicell_summary"],
        "contract_guardrail_summary": full["contract_guardrail_summary"],
        "supersession": full["supersession"],
        "verdict": full["verdict"],
        "limitations": full["limitations"],
        "runtime": full["runtime"],
    }


def build_d5_des_stat_tier1_recharacterization_001(
    cfg: RecharConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or RecharConfig()
    records, runtime = _run_matrix(cfg)
    aggregate = _aggregate(records)
    legacy_cmp = _legacy_vs_corrected(records)
    sc_records = [r for r in records if r["lane"] == "single_cell_tier1"]
    mc_records = [r for r in records if r["lane"] == "multicell_per_cell_only"]
    return {
        "artifact_id": ARTIFACT_ID,
        "artifact_version": GENERATOR_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_head(),
        "config": {**asdict(cfg), "min_control_threshold": MIN_CONTROL_THRESHOLD},
        "lanes": ["single_cell_tier1", "legacy_reference", "multicell_per_cell_only"],
        "designs": [
            {
                "design_inventory_id": d.design_inventory_id,
                "lane": d.lane,
                "label": d.label,
                "registry_key": d.registry_key,
                "base_randomizer_cls": d.base_randomizer_cls.__name__,
                "is_rerandomization_wrapper": d.is_rerandomization_wrapper,
                "design_kwargs": d.design_kwargs,
                "n_test_grps": d.n_test_grps,
            }
            for d in (*CORRECTED_DESIGNS, *LEGACY_DESIGNS, *MULTICELL_DESIGNS)
        ],
        "worlds": {
            "single_cell": list(ALL_WORLD_IDS),
            "multicell": list(MULTICELL_WORLD_IDS),
        },
        "run_records": records,
        "aggregate_results": aggregate,
        "legacy_vs_corrected": legacy_cmp,
        "pairwise_comparisons": _pairwise_comparisons(records),
        "failure_summary": {
            "n_assignment_failures": sum(1 for r in records if r["assignment_status"] == "failed"),
            "n_blocks": sum(1 for r in records if r.get("run_outcome") == "block"),
            "greedy_corrected_control_violations": sum(
                1
                for r in sc_records
                if r["design_label"] == "greedy_corrected"
                and r["metrics"].get("minimum_control_violation")
            ),
            "greedy_legacy_control_violations": sum(
                1
                for r in records
                if r["design_label"] == "greedy_legacy"
                and r["metrics"].get("minimum_control_violation")
            ),
            "stratified_poor_strata_high_smd_legacy": sum(
                1
                for r in records
                if r["design_label"] == "stratified_legacy"
                and r["world_id"] == "stratification_poor_strata_world"
                and (r["metrics"].get("max_absolute_smd") or 0) > 0.5
            ),
            "stratified_poor_strata_high_smd_corrected": sum(
                1
                for r in sc_records
                if r["design_label"] == "stratified_corrected"
                and r["world_id"] == "stratification_poor_strata_world"
                and (r["metrics"].get("max_absolute_smd") or 0) > 0.5
            ),
        },
        "balance_summary": {
            "corrected_mean_max_smd_by_design": {
                k: v.get("mean_max_smd")
                for k, v in aggregate.items()
                if k.startswith("single_cell_tier1:")
            }
        },
        "multicell_summary": {
            "pooled_claims_blocked": True,
            "cell_collision_rate": sum(
                1 for r in mc_records if r["metrics"].get("cell_collision_count", 0) > 0
            )
            / max(1, len(mc_records)),
            "mean_worst_cell_smd_corrected": aggregate.get(
                "multicell_per_cell_only:multicell_corrected", {}
            ).get("mean_max_smd"),
        },
        "contract_guardrail_summary": {
            "downstream_may_proceed": False,
            "contract_complete_allowed": False,
            "pooled_claims_allowed": False,
        },
        "supersession": {
            "historical_artifact_id": HISTORICAL_ARTIFACT_ID,
            "historical_report": "docs/track_d/D5_DES_STAT_TIER1_001_REPORT.md",
            "supersedes_default_comparisons_for": ["DES-001", "DES-004", "DES-011"],
            "historical_evidence_retained": True,
            "note": (
                "Original tier-1 archive remains historical; greedy/stratified/multicell "
                "default comparisons in that report are superseded for corrected-default policy."
            ),
            "historical_baseline_notes": {
                "greedy_legacy_control_floor_rate_approx": 0.28,
                "stratified_legacy_high_smd_reduction_approx": 0.82,
                "multicell_pooled_claims_blocked": True,
            },
        },
        "runtime": runtime,
        "limitations": [
            "Design-only recharacterization; no promotion or downstream authorization.",
            "Multi-cell lane excluded from single-cell rankings.",
            "Legacy lanes are reference-only, not supported defaults.",
        ],
        "verdict": _derive_verdict(records, runtime),
    }


def generate_report_markdown(payload: dict[str, Any]) -> str:
    rt = payload["runtime"]
    fs = payload["failure_summary"]
    lvc = payload["legacy_vs_corrected"]
    lines = [
        f"# {ARTIFACT_ID} Report",
        "",
        f"**Verdict:** `{payload['verdict']}`",
        "",
        "> **Supersession:** This report supersedes corrected-default comparisons in "
        "[D5_DES_STAT_TIER1_001_REPORT.md](D5_DES_STAT_TIER1_001_REPORT.md). "
        "The original tier-1 archive remains historical evidence.",
        "",
        "Full archive (local only):",
        "",
        "```bash",
        "poetry run python -m panel_exp.validation.track_d_d5_des_stat_tier1_recharacterization_001 \\",
        "  --output-local /tmp/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_results.json \\",
        "  --summary-output docs/track_d/archives/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_summary.json \\",
        "  --overwrite",
        "```",
        "",
        "## 1. Executive summary",
        "",
        "Post-fix tier-1 recharacterization across corrected defaults, legacy references, "
        "and a separate multi-cell per-cell-only lane. **No promotion.**",
        "",
        "## 2. Why recharacterization was required",
        "",
        "Greedy, stratified, and multi-cell defaults changed after D5-DES-STAT-TIER1-001.",
        "",
        "## 3. Historical tier-1 baseline",
        "",
        f"See `{HISTORICAL_ARTIFACT_ID}` archive and report (retained as historical).",
        "",
        "## 4. Corrected implementations",
        "",
        "- DES-001: `control_reservation`",
        "- DES-004: `adaptive_strata`",
        "- DES-011: `control_reservation` (separate lane)",
        "",
        "## 5. Scope and lanes",
        "",
        str(payload["lanes"]),
        "",
        "## 6. Worlds and configuration",
        "",
        str(payload["worlds"]),
        "",
        "## 7. Metrics",
        "",
        "Feasibility, balance/SMD, greedy/stratified/multicell diagnostics, contract/guardrail.",
        "",
        "## 8. Runtime and run counts",
        "",
        "Matrix: `designs × worlds × treatment_points × replicates × seeds` "
        "(replicates and seeds are independent, matching tier-1 harness).",
        "",
        f"Attempted: {rt['total_attempted_runs']} · Expected: {rt.get('expected_attempted_runs')} · "
        f"Failed: {rt['failed_runs']} · Elapsed: {rt['elapsed_seconds']}s",
        f"Per-lane actual: {rt.get('per_lane_counts')} · Expected: {rt.get('expected_per_lane_counts')}",
        "",
        "## 9. Current-default aggregate results",
        "",
        str(payload["aggregate_results"]),
        "",
        "## 10. Greedy corrected findings",
        "",
        f"Corrected control violations: {fs.get('greedy_corrected_control_violations')}",
        "",
        "## 11. Stratified corrected findings",
        "",
        f"Poor-strata high-SMD legacy: {fs.get('stratified_poor_strata_high_smd_legacy')} · "
        f"corrected: {fs.get('stratified_poor_strata_high_smd_corrected')}",
        "",
        "## 12. Complete-randomization benchmark",
        "",
        "DES-002 reference in single_cell_tier1 lane.",
        "",
        "## 13. Balanced-randomization findings",
        "",
        "See pairwise complete_vs_balanced.",
        "",
        "## 14. Rerandomization findings",
        "",
        "DES-006 wrapper with attempt diagnostics.",
        "",
        "## 15. Legacy versus corrected greedy",
        "",
        str(lvc.get("DES-001", {})),
        "",
        "## 16. Legacy versus corrected stratified",
        "",
        str(lvc.get("DES-004", {})),
        "",
        "## 17. Multi-cell per-cell-only findings",
        "",
        str(payload["multicell_summary"]),
        "",
        "## 18. Pairwise comparisons",
        "",
        str(payload["pairwise_comparisons"]),
        "",
        "## 19. Feasibility findings",
        "",
        str(fs),
        "",
        "## 20. Balance findings",
        "",
        str(payload["balance_summary"]),
        "",
        "## 21. Worst-case behavior",
        "",
        "Captured via block_rate and high-SMD counts per design.",
        "",
        "## 22. Contract and guardrail findings",
        "",
        str(payload["contract_guardrail_summary"]),
        "",
        "## 23. Supersession statement",
        "",
        str(payload["supersession"]),
        "",
        "## 24. Suitability implications",
        "",
        "0 downstream suitable; statistical validation still required per design.",
        "",
        "## 25. Combination-matrix implications",
        "",
        "Corrected-default evidence updates DCM rows; pooled multi-cell remains blocked.",
        "",
        "## 26. Remaining limitations",
        "",
        "\n".join(f"- {x}" for x in payload["limitations"]),
        "",
        "## 27. Recommended next work",
        "",
        "DESIGN_GUARDRAIL_ENFORCEMENT_001 or DESIGN_COMBINATION_VALIDATION_EXECUTION_001.",
        "",
        "## 28. Governance verdict",
        "",
        f"**{payload['verdict']}** — no production promotion.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=ARTIFACT_ID)
    parser.add_argument(
        "--output-local",
        type=Path,
        default=Path("/tmp/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_results.json"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=_repo_root()
        / "docs/track_d/archives/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_summary.json",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    cfg = RecharConfig(fast=args.fast)
    payload = build_d5_des_stat_tier1_recharacterization_001(cfg)
    write_artifact_atomic(args.output_local, payload, overwrite=args.overwrite)
    summary = build_summary_payload(payload)
    write_artifact_atomic(args.summary_output, summary, overwrite=args.overwrite)
    report_path = args.report or (
        _repo_root() / "docs/track_d/D5_DES_STAT_TIER1_RECHARACTERIZATION_001_REPORT.md"
    )
    report_path.write_text(generate_report_markdown(payload), encoding="utf-8")
    print(f"Wrote local archive: {args.output_local}")
    print(f"Wrote summary: {args.summary_output}")
    print(f"Verdict: {payload['verdict']}")


if __name__ == "__main__":
    main()
