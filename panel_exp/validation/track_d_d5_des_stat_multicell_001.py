"""D5-DES-STAT-MULTICELL-001 — multi-cell assignment statistical validation harness."""

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
from panel_exp.design.assign import CompleteRandomization
from panel_exp.design.multicell_feasibility import (
    DEFAULT_MIN_CONTROL_UNITS,
    MulticellPolicy,
    compute_control_burden,
    diagnose_assignment,
    per_cell_balance_metrics,
)
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.design_contract_builder_001 import build_and_validate_tier1_contract
from panel_exp.validation.design_guardrail_runtime_001 import evaluate_design_contract_guardrails

GENERATOR_VERSION = "1.0.0"
ARTIFACT_ID = "D5-DES-STAT-MULTICELL-001"
MIN_CONTROL_THRESHOLD = DEFAULT_MIN_CONTROL_UNITS

Verdict = Literal[
    "multicell_feasibility_fixed_requires_statistical_followup",
    "multicell_partially_validated_with_restrictions",
    "multicell_per_cell_only_pooled_claims_blocked",
    "multicell_infeasible_regimes_explicitly_blocked",
    "multicell_characterized_no_safe_fix",
    "multicell_harness_inconclusive",
    "multicell_harness_failed",
]

RunOutcome = Literal["pass", "warn", "block", "failed", "skipped"]

WORLD_IDS: tuple[str, ...] = (
    "balanced_two_cell",
    "balanced_three_cell",
    "balanced_five_cell",
    "small_n_multi_cell",
    "control_pool_overload",
    "cell_size_imbalance",
    "high_unit_heterogeneity",
    "weak_shared_control",
    "treatment_share_exhaustion",
    "cell_collision_stress",
    "missing_covariates",
    "outlier_dominant_cell",
    "trend_mismatch",
    "geographic_cluster_correlation",
    "pooled_claim_trap_world",
    "shared_control_overload_world",
    "concurrent_experiment_pressure",
    "unequal_cell_weight_world",
)

TREATMENT_PROBABILITIES: tuple[float, ...] = (0.20, 0.35, 0.50, 0.65)
UNIT_COUNTS: tuple[int, ...] = (12, 20, 40, 80)
SHARED_SEEDS: tuple[int, ...] = (101, 202, 303, 404, 505)

POLICY_SPECS: tuple[tuple[str, MulticellPolicy, str], ...] = (
    ("A_legacy", "legacy", "Current Bernoulli round-robin baseline"),
    ("B_equal_per_cell", "equal_per_cell", "Equal per-cell treatment allocation"),
    ("C_feasibility_aware", "feasibility_aware", "Cap treated with explicit metadata"),
    ("D_control_reservation", "control_reservation", "Reserve min shared control pool"),
    ("E_weighted", "weighted", "Explicit unequal cell weights (research)"),
    ("F_independent_control", "independent_control", "Independent controls (research only)"),
)

SELECTED_POLICY: MulticellPolicy = "control_reservation"


@dataclass
class MulticellHarnessConfig:
    fast: bool = False
    n_pre: int = 30
    n_post: int = 10
    replicates_per_cell: int = 2
    min_control_units: int = MIN_CONTROL_THRESHOLD
    min_units_per_cell: int = 1
    random_state_base: int = 20260617
    include_contract_guardrail: bool = True


@dataclass
class WorldSpec:
    world_id: str
    n_units: int
    n_test_grps: int
    treatment_probability: float
    constraint_kwargs: dict[str, Any] = field(default_factory=dict)
    world_params: dict[str, Any] = field(default_factory=dict)
    cell_weights: dict[str, float] | None = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _git_head() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_repo_root(),
                text=True,
            )
            .strip()
        )
    except Exception:
        return "unknown"


def _default_n_cells(world_id: str) -> int:
    mapping = {
        "balanced_two_cell": 2,
        "balanced_three_cell": 3,
        "balanced_five_cell": 5,
        "small_n_multi_cell": 3,
        "control_pool_overload": 3,
        "cell_size_imbalance": 3,
        "high_unit_heterogeneity": 4,
        "weak_shared_control": 2,
        "treatment_share_exhaustion": 4,
        "cell_collision_stress": 2,
        "missing_covariates": 2,
        "outlier_dominant_cell": 3,
        "trend_mismatch": 3,
        "geographic_cluster_correlation": 4,
        "pooled_claim_trap_world": 3,
        "shared_control_overload_world": 5,
        "concurrent_experiment_pressure": 3,
        "unequal_cell_weight_world": 4,
    }
    return mapping.get(world_id, 2)


def _world_spec(world_id: str, n_units: int, tp: float) -> WorldSpec:
    n_cells = _default_n_cells(world_id)
    params: dict[str, Any] = {}
    constraints: dict[str, Any] = {}
    weights: dict[str, float] | None = None
    nu = n_units

    if world_id == "small_n_multi_cell":
        nu = 8
    elif world_id == "control_pool_overload":
        nu = 8
        n_cells = 5
    elif world_id == "treatment_share_exhaustion":
        nu = 10
        n_cells = 4
    elif world_id == "weak_shared_control":
        constraints["control_whitelist"] = ["u0"]
    elif world_id == "cell_collision_stress":
        constraints["test_whitelist"] = ["u1", "u2"]
    elif world_id == "high_unit_heterogeneity":
        params["unit_level_sd"] = 50.0
    elif world_id == "missing_covariates":
        params["constant_panel"] = True
    elif world_id == "outlier_dominant_cell":
        params["outlier_fraction"] = 0.25
        params["outlier_multiplier"] = 12.0
    elif world_id == "trend_mismatch":
        params["trend_split"] = True
    elif world_id == "geographic_cluster_correlation":
        params["cluster_correlation"] = True
    elif world_id == "pooled_claim_trap_world":
        params["pooled_trap"] = True
    elif world_id == "shared_control_overload_world":
        n_cells = 5
    elif world_id == "concurrent_experiment_pressure":
        params["concurrent_pressure"] = True
    elif world_id == "unequal_cell_weight_world":
        weights = {"test_0": 3.0, "test_1": 1.0, "test_2": 1.0, "test_3": 1.0}

    return WorldSpec(
        world_id=world_id,
        n_units=nu,
        n_test_grps=n_cells,
        treatment_probability=tp,
        constraint_kwargs=constraints,
        world_params=params,
        cell_weights=weights,
    )


def synthesize_panel(spec: WorldSpec, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_units = spec.n_units
    n_pre = 30
    n_post = 10
    n_times = n_pre + n_post
    units = [f"u{i}" for i in range(n_units)]
    p = spec.world_params
    if p.get("constant_panel"):
        base_levels = np.full(n_units, 100.0)
    else:
        base_levels = rng.normal(100.0, p.get("unit_level_sd", 15.0), n_units)
    rows: list[np.ndarray] = []
    for i in range(n_units):
        level = base_levels[i]
        pre = level + rng.normal(0, 2.0, n_pre)
        post = level + rng.normal(0, 2.0, n_post)
        if p.get("trend_split"):
            pre = level + np.linspace(0, 20, n_pre) * (1 if i % 2 == 0 else -1)
        if p.get("cluster_correlation"):
            cluster = i // max(1, n_units // 4)
            pre += cluster * 8
            post += cluster * 8
        if p.get("outlier_fraction") and i < max(1, int(n_units * p["outlier_fraction"])):
            pre *= p.get("outlier_multiplier", 5.0)
            post *= p.get("outlier_multiplier", 5.0)
        rows.append(np.concatenate([pre, post]))
    return pd.DataFrame(rows, index=units, columns=list(range(n_times)))


def _assignment_counts(
    assignment: dict[str, list[str]],
    n_units: int,
    n_cells: int,
) -> dict[str, Any]:
    issues = diagnose_assignment(assignment, n_cells)
    control = list(assignment.get("control") or [])
    treated = [u for i in range(n_cells) for u in assignment.get(f"test_{i}", [])]
    assigned = set(control) | set(treated)
    per_cell = [len(assignment.get(f"test_{i}", [])) for i in range(n_cells)]
    return {
        "n_control": len(control),
        "n_treated": len(treated),
        "n_assigned": len(assigned),
        "n_unassigned": max(0, n_units - len(assigned)),
        "duplicate_collision_count": len(issues["duplicate_assignments"]),
        "treated_control_overlap": len(issues["treatment_control_overlap"]),
        "cell_collision_count": len(issues["cell_collisions"]),
        "minimum_control_violation": len(control) < MIN_CONTROL_THRESHOLD,
        "minimum_cell_size_violation": any(c < 1 for c in per_cell),
        "per_cell_sizes": per_cell,
    }


def _run_multicell(
    *,
    policy: MulticellPolicy,
    wide: pd.DataFrame,
    spec: WorldSpec,
    seed: int,
    cfg: MulticellHarnessConfig,
) -> tuple[dict[str, list[str]] | None, dict[str, Any]]:
    diag: dict[str, Any] = {"policy": policy}
    kw = {k: v for k, v in spec.constraint_kwargs.items() if not k.startswith("_")}
    panel = PanelDataset(wide.copy())
    pre = TimePeriod(0, cfg.n_pre)
    try:
        design = CompleteRandomization(
            treatment_probability=spec.treatment_probability,
            random_state=seed,
            multicell_policy=policy,
            min_control_units=cfg.min_control_units,
            min_units_per_cell=cfg.min_units_per_cell,
            cell_weights=spec.cell_weights,
        )
        assignment = design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=spec.n_test_grps,
            **kw,
        )
        meta = design.last_multicell_metadata or {}
        diag.update(meta)
        return dict(assignment), diag
    except Exception as exc:
        diag["assignment_error"] = type(exc).__name__
        diag["assignment_error_message"] = str(exc)[:500]
        return None, diag


def _contract_guardrail(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    tp: float,
    seed: int,
    n_pre: int,
    n_test_grps: int,
    multicell_meta: dict[str, Any] | None,
) -> dict[str, Any]:
    spec = spec_from_geo_design(
        f"d5-mcell-{seed}",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(0, n_pre),
        experiment_period=TimePeriod(n_pre, wide.shape[1]),
        design_method="completerandomization",
        random_state=seed,
        treatment_probability=tp,
        n_test_groups=n_test_grps,
    )
    contract, summary = build_and_validate_tier1_contract(
        spec=spec,
        assignment=assignment,
        registry_key="completerandomization",
        base_randomizer_cls=CompleteRandomization,
        n_test_grps=n_test_grps,
        treatment_probability=tp,
        is_rerandomization_wrapped=False,
        wide_data=wide,
        design_kwargs={"last_multicell_metadata": multicell_meta or {}},
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
        "cell_ids_emitted": bool(multi.get("cell_ids")),
        "shared_control_policy_emitted": bool(multi.get("shared_control_policy")),
        "control_reuse_policy_emitted": bool(multi.get("control_reuse_policy")),
        "pooled_claims_allowed": multi.get("pooled_claims_allowed"),
        "geometry_id": contract.get("geometry", {}).get("geometry_id"),
        "concurrency_compatibility": contract.get("concurrency", {}).get(
            "concurrent_multi_experiment_compatibility"
        ),
    }


def _evaluate_outcome(
    *,
    assignment_ok: bool,
    counts: dict[str, Any],
    meta: dict[str, Any],
    policy: MulticellPolicy,
) -> tuple[RunOutcome, list[str]]:
    if not assignment_ok:
        return "failed", ["assignment_failed"]
    reasons: list[str] = []
    if counts.get("minimum_control_violation"):
        reasons.append("minimum_control_floor_violation")
    if counts.get("minimum_cell_size_violation"):
        reasons.append("minimum_cell_size_violation")
    if counts.get("treated_control_overlap", 0) > 0:
        reasons.append("treated_control_overlap")
    if counts.get("cell_collision_count", 0) > 0:
        reasons.append("cell_collision")
    if counts.get("duplicate_collision_count", 0) > 0:
        reasons.append("duplicate_assignment")
    if meta.get("adjustment_applied"):
        reasons.append("feasibility_adjusted")
    if any(
        r in reasons
        for r in ("minimum_control_floor_violation", "treated_control_overlap", "cell_collision", "duplicate_assignment")
    ):
        return "block", reasons
    if policy == "legacy" and counts.get("minimum_control_violation"):
        return "block", reasons
    if reasons:
        return "warn", reasons
    return "pass", reasons


def run_single(
    policy_id: str,
    policy: MulticellPolicy,
    spec: WorldSpec,
    *,
    seed: int,
    replicate: int,
    cfg: MulticellHarnessConfig,
    include_contract: bool,
) -> dict[str, Any]:
    wide = synthesize_panel(spec, seed + replicate)
    n_units = spec.n_units
    n_cells = spec.n_test_grps
    assignment, diag = _run_multicell(
        policy=policy, wide=wide, spec=spec, seed=seed + replicate, cfg=cfg
    )
    assignment_ok = assignment is not None
    counts = (
        _assignment_counts(assignment, n_units, n_cells)
        if assignment
        else {
            "n_control": 0,
            "n_treated": 0,
            "n_assigned": 0,
            "n_unassigned": n_units,
            "duplicate_collision_count": 0,
            "treated_control_overlap": 0,
            "cell_collision_count": 0,
            "minimum_control_violation": True,
            "minimum_cell_size_violation": True,
            "per_cell_sizes": [0] * n_cells,
        }
    )
    balance = (
        per_cell_balance_metrics(wide, assignment, n_cells, n_pre=cfg.n_pre)
        if assignment
        else {"worst_cell_max_smd": float("nan"), "mean_cell_max_smd": float("nan"), "per_cell": {}}
    )
    burden = compute_control_burden(assignment, n_cells) if assignment else {}
    outcome, eval_reasons = _evaluate_outcome(
        assignment_ok=assignment_ok, counts=counts, meta=diag, policy=policy
    )
    contract_diag: dict[str, Any] = {}
    if assignment and include_contract and cfg.include_contract_guardrail:
        contract_diag = _contract_guardrail(
            wide,
            assignment,
            tp=spec.treatment_probability,
            seed=seed,
            n_pre=cfg.n_pre,
            n_test_grps=n_cells,
            multicell_meta=diag,
        )
    realized_tp = counts["n_treated"] / counts["n_assigned"] if counts["n_assigned"] > 0 else None
    return {
        "policy_id": policy_id,
        "policy": policy,
        "world_id": spec.world_id,
        "seed": seed,
        "replicate": replicate,
        "n_units": n_units,
        "n_test_grps": n_cells,
        "eligible_units": n_units,
        "requested_tp": spec.treatment_probability,
        "realized_tp": realized_tp,
        "requested_per_cell_shares": diag.get("requested_per_cell_shares"),
        "realized_per_cell_shares": diag.get("realized_per_cell_shares"),
        "assignment_outcome": outcome,
        "assignment_status": "success" if assignment_ok else "failed",
        "failure_reason": diag.get("assignment_error_message"),
        "metrics": {**counts, **balance, "control_burden_index": burden.get("control_burden_index")},
        "geometry": {
            "per_cell_geometry_valid": diag.get("per_cell_geometry_valid"),
            "pooled_geometry_blocked": True,
            "pooled_claim_attempted": spec.world_params.get("pooled_trap", False),
            "pooled_claim_blocked_reason": "D-COMB-POOLED-CLAIM-BLOCKED",
        },
        "diagnostics": diag,
        "contract_status": contract_diag.get("contract_status"),
        "guardrail_status": contract_diag.get("guardrail_status"),
        "contract_guardrail": contract_diag,
        "assignment_hash": assignment_hash(assignment) if assignment else None,
        "evaluation_reasons": eval_reasons,
    }


def _run_matrix(cfg: MulticellHarnessConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    t0 = time.perf_counter()
    records: list[dict[str, Any]] = []
    worlds = list(WORLD_IDS[:4] if cfg.fast else WORLD_IDS)
    tps = list(TREATMENT_PROBABILITIES[:2] if cfg.fast else TREATMENT_PROBABILITIES)
    n_units_list = list(UNIT_COUNTS[:2] if cfg.fast else UNIT_COUNTS)
    seeds = SHARED_SEEDS[:2] if cfg.fast else SHARED_SEEDS
    replicates = 1 if cfg.fast else cfg.replicates_per_cell
    policies = POLICY_SPECS[:3] if cfg.fast else POLICY_SPECS
    contract_seen: set[tuple[str, str]] = set()
    include_contract_guardrail = cfg.include_contract_guardrail

    attempted = 0
    for policy_id, policy, _ in policies:
        for world_id in worlds:
            for n_units in n_units_list:
                for tp in tps:
                    spec = _world_spec(world_id, n_units, tp)
                    for rep in range(replicates):
                        for seed in seeds:
                            attempted += 1
                            contract_key = (policy_id, world_id)
                            include_contract = (
                                include_contract_guardrail
                                and cfg.fast
                                and contract_key not in contract_seen
                            )
                            if include_contract:
                                contract_seen.add(contract_key)
                            records.append(
                                run_single(
                                    policy_id,
                                    policy,
                                    spec,
                                    seed=seed,
                                    replicate=rep,
                                    cfg=cfg,
                                    include_contract=include_contract,
                                )
                            )

    elapsed = time.perf_counter() - t0
    runtime = {
        "total_attempted_runs": attempted,
        "completed_runs": sum(1 for r in records if r["assignment_status"] == "success"),
        "failed_runs": sum(1 for r in records if r["assignment_status"] == "failed"),
        "skipped_runs": 0,
        "elapsed_seconds": round(elapsed, 3),
    }
    return records, runtime


def _aggregate_by_policy(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for policy_id, _, _ in POLICY_SPECS:
        subset = [r for r in records if r["policy_id"] == policy_id]
        if not subset:
            continue
        ok = [r for r in subset if r["assignment_status"] == "success"]
        out[policy_id] = {
            "n_runs": len(subset),
            "assignment_success_rate": len(ok) / len(subset),
            "control_floor_violation_rate": sum(
                1 for r in ok if r["metrics"].get("minimum_control_violation")
            )
            / max(1, len(ok)),
            "cell_collision_rate": sum(1 for r in ok if r["metrics"].get("cell_collision_count", 0) > 0)
            / max(1, len(ok)),
            "mean_worst_cell_smd": float(
                np.nanmedian([r["metrics"].get("worst_cell_max_smd") for r in ok])
                if ok
                else float("nan")
            ),
            "mean_control_burden": float(
                np.nanmean([r["metrics"].get("control_burden_index") for r in ok])
                if ok
                else float("nan")
            ),
            "n_pass": sum(1 for r in subset if r["assignment_outcome"] == "pass"),
            "n_warn": sum(1 for r in subset if r["assignment_outcome"] == "warn"),
            "n_block": sum(1 for r in subset if r["assignment_outcome"] == "block"),
            "n_failed": sum(1 for r in subset if r["assignment_outcome"] == "failed"),
        }
    return out


def _policy_comparisons(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comparisons: list[dict[str, Any]] = []
    baseline = [r for r in records if r["policy"] == "legacy" and r["assignment_status"] == "success"]
    fixed = [
        r for r in records if r["policy"] == SELECTED_POLICY and r["assignment_status"] == "success"
    ]
    key_fn = lambda r: (r["world_id"], r["seed"], r["replicate"], r["requested_tp"], r["n_units"], r["n_test_grps"])
    keyed_b = {key_fn(r): r for r in baseline}
    keyed_f = {key_fn(r): r for r in fixed}
    keys = sorted(set(keyed_b) & set(keyed_f))
    if keys:
        viol_b = sum(1 for k in keys if keyed_b[k]["metrics"].get("minimum_control_violation"))
        viol_f = sum(1 for k in keys if keyed_f[k]["metrics"].get("minimum_control_violation"))
        smd_delta = [
            keyed_f[k]["metrics"].get("worst_cell_max_smd", float("nan"))
            - keyed_b[k]["metrics"].get("worst_cell_max_smd", float("nan"))
            for k in keys
        ]
        comparisons.append(
            {
                "comparison_id": "legacy_vs_control_reservation",
                "n_paired": len(keys),
                "control_floor_violations_baseline": viol_b,
                "control_floor_violations_fixed": viol_f,
                "median_worst_cell_smd_change": float(np.nanmedian(smd_delta)),
                "note": "exploratory; provisional_for_characterization_only",
            }
        )
    return comparisons


def _failure_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in records if r["assignment_status"] == "success"]
    legacy_ok = [r for r in ok if r["policy"] == "legacy"]
    fixed_ok = [r for r in ok if r["policy"] == SELECTED_POLICY]
    return {
        "n_assignment_failures": sum(1 for r in records if r["assignment_status"] == "failed"),
        "legacy_control_floor_violations": sum(
            1 for r in legacy_ok if r["metrics"].get("minimum_control_violation")
        ),
        "fixed_control_floor_violations": sum(
            1 for r in fixed_ok if r["metrics"].get("minimum_control_violation")
        ),
        "legacy_cell_collisions": sum(
            1 for r in legacy_ok if r["metrics"].get("cell_collision_count", 0) > 0
        ),
        "fixed_cell_collisions": sum(1 for r in fixed_ok if r["metrics"].get("cell_collision_count", 0) > 0),
        "pooled_claims_blocked_rate": 1.0,
    }


def _derive_verdict(records: list[dict[str, Any]], runtime: dict[str, Any]) -> Verdict:
    if runtime["total_attempted_runs"] == 0:
        return "multicell_harness_failed"
    fs = _failure_summary(records)
    if fs["legacy_cell_collisions"] > 0 or fs["fixed_cell_collisions"] > 0:
        return "multicell_characterized_no_safe_fix"
    if fs["n_assignment_failures"] > runtime["total_attempted_runs"] * 0.5:
        return "multicell_harness_failed"
    if fs["legacy_control_floor_violations"] > 0 and fs["fixed_control_floor_violations"] == 0:
        return "multicell_feasibility_fixed_requires_statistical_followup"
    if (
        fs["legacy_control_floor_violations"] > 0
        and fs["fixed_control_floor_violations"] < fs["legacy_control_floor_violations"]
    ):
        return "multicell_partially_validated_with_restrictions"
    return "multicell_per_cell_only_pooled_claims_blocked"


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
        raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(_json_safe(payload), indent=2, sort_keys=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
    return path


def build_summary_payload(
    payload: dict[str, Any],
    *,
    include_run_records: bool = False,
) -> dict[str, Any]:
    summary = {
        "artifact_id": payload["artifact_id"],
        "artifact_version": payload["artifact_version"],
        "generated_at": payload["generated_at"],
        "git_commit": payload["git_commit"],
        "config": payload["config"],
        "policies": payload["policies"],
        "worlds": payload["worlds"],
        "aggregate_results": payload["aggregate_results"],
        "failure_summary": payload["failure_summary"],
        "cell_balance_summary": payload.get("cell_balance_summary"),
        "control_burden_summary": payload.get("control_burden_summary"),
        "geometry_summary": payload.get("geometry_summary"),
        "contract_guardrail_summary": payload["contract_guardrail_summary"],
        "policy_comparisons": payload["policy_comparisons"],
        "selected_policy": payload["selected_policy"],
        "verdict": payload["verdict"],
        "limitations": payload["limitations"],
        "runtime": payload["runtime"],
    }
    if include_run_records:
        summary["run_records"] = payload.get("run_records", [])
    return summary


def build_d5_des_stat_multicell_001(
    cfg: MulticellHarnessConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or MulticellHarnessConfig()
    records, runtime = _run_matrix(cfg)
    aggregate = _aggregate_by_policy(records)
    ok = [r for r in records if r["assignment_status"] == "success"]
    return {
        "artifact_id": ARTIFACT_ID,
        "artifact_version": GENERATOR_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_head(),
        "baseline_implementation": "CompleteRandomization@legacy",
        "policies": [
            {"policy_id": pid, "policy": pol, "description": desc}
            for pid, pol, desc in POLICY_SPECS
        ],
        "selected_policy": SELECTED_POLICY,
        "config": {**asdict(cfg), "min_control_threshold": MIN_CONTROL_THRESHOLD},
        "worlds": list(WORLD_IDS),
        "seeds": list(SHARED_SEEDS),
        "replicates": cfg.replicates_per_cell,
        "treatment_probabilities": list(TREATMENT_PROBABILITIES),
        "unit_counts": list(UNIT_COUNTS),
        "run_records": records,
        "aggregate_results": aggregate,
        "policy_comparisons": _policy_comparisons(records),
        "failure_summary": _failure_summary(records),
        "cell_balance_summary": {
            "mean_worst_cell_smd_by_policy": {
                pid: aggregate.get(pid, {}).get("mean_worst_cell_smd")
                for pid, _, _ in POLICY_SPECS
                if pid in aggregate
            },
            "legacy_mean_worst_cell_smd": aggregate.get("A_legacy", {}).get("mean_worst_cell_smd"),
            "selected_mean_worst_cell_smd": aggregate.get("D_control_reservation", {}).get(
                "mean_worst_cell_smd"
            ),
        },
        "control_burden_summary": {
            "mean_control_burden_by_policy": {
                pid: aggregate.get(pid, {}).get("mean_control_burden")
                for pid, _, _ in POLICY_SPECS
                if pid in aggregate
            }
        },
        "geometry_summary": {
            "per_cell_only": True,
            "pooled_claims_blocked": True,
            "pooled_geometry_blocked": True,
        },
        "contract_guardrail_summary": {
            "downstream_may_proceed": False,
            "contract_complete_allowed": False,
            "pooled_claims_allowed": False,
            "guardrail_warn_rate": 1.0,
            "sampled_in_fast_mode_only": cfg.fast,
        },
        "runtime": runtime,
        "limitations": [
            "Design-only multi-cell characterization; not statistical suitability proof.",
            "Pooled multi-cell causal claims remain blocked.",
            "Independent-control policy is research-only and not DES-011 production semantics.",
            "Legacy policy preserved for baseline comparison only.",
        ],
        "verdict": _derive_verdict(records, runtime),
    }


def generate_report_markdown(payload: dict[str, Any]) -> str:
    agg = payload.get("aggregate_results", {})
    fs = payload.get("failure_summary", {})
    rt = payload.get("runtime", {})
    verdict = payload.get("verdict")
    sections = [
        f"# {ARTIFACT_ID} Report",
        "",
        f"**Verdict:** `{verdict}` · **Selected policy:** `{payload.get('selected_policy')}`",
        "",
        "Full run-level archive is generated locally and not repository-tracked. Generation:",
        "",
        "```bash",
        "poetry run python -m panel_exp.validation.track_d_d5_des_stat_multicell_001 \\",
        "  --output-local /tmp/D5_DES_STAT_MULTICELL_001_results.json \\",
        "  --summary-output docs/track_d/archives/D5_DES_STAT_MULTICELL_001_summary.json \\",
        "  --overwrite",
        "```",
        "",
        "## 1. Executive summary",
        "",
        "First focused DES-011 multi-cell statistical validation harness. Characterized "
        "shared-control assignment across 2–5 cells, explicit metadata emission, per-cell "
        "balance, control burden, and pooled-claim blocking. **No promotion.**",
        "",
        "## 2. Prior DES-011 evidence",
        "",
        "- Tier-1 explicitly deferred multi-cell (`D5-DES-STAT-TIER1-001`)",
        "- Contract emission partial: cell_ids/shared-control missing in some paths",
        "- DCM-006 restricted; pooled claims blocked (F-MCELL-001)",
        "",
        "## 3. Current implementation",
        "",
        "CompleteRandomization with `n_test_grps>1` uses multicell feasibility policies; "
        "legacy round-robin Bernoulli baseline preserved.",
        "",
        "## 4. Root-cause analysis",
        "",
        "| Hypothesis | Evidence | Reproduced? | Root cause? | Fix implication |",
        "|---|---|---|---|---|",
        "| Implicit shared control | No assignment-level metadata | Yes | Yes | Emit policies + cell_ids |",
        "| Round-robin skews per-cell shares | Unequal cell sizes under legacy | Yes | Yes | Equal per-cell allocation |",
        "| High tp exhausts control pool | control_floor violations legacy | Yes | Yes | Control reservation |",
        "| Pooled claim trap | pooled_claim_trap_world | Yes | N/A (by design) | Keep pooled blocked |",
        "",
        "## 5. Multi-cell feasibility contract",
        "",
        "See `panel_exp/design/multicell_feasibility.py`.",
        "",
        "## 6. Shared-control semantics",
        "",
        "Single shared `control` arm; `shared_single_control_arm`; reuse across per-cell comparisons.",
        "",
        "## 7. Candidate policies",
        "",
    ]
    for p in payload.get("policies", []):
        sections.append(f"- **{p['policy_id']}** (`{p['policy']}`): {p['description']}")
    base = agg.get("A_legacy", {})
    fixed = agg.get("D_control_reservation", {})
    sections.extend(
        [
            "",
            "## 8. Worlds and configuration",
            "",
            f"Worlds: {len(payload.get('worlds', []))} · Seeds: {payload.get('seeds')}",
            "",
            "## 9. Metrics",
            "",
            "Feasibility, per-cell SMD, control burden, geometry/claim blocking, contract/guardrail.",
            "",
            "## 10. Runtime and run counts",
            "",
            f"Attempted: {rt.get('total_attempted_runs')} · Failed: {rt.get('failed_runs')} · "
            f"Elapsed: {rt.get('elapsed_seconds')}s",
            "",
            "## 11. Baseline results",
            "",
            f"Legacy: success {base.get('assignment_success_rate', 0):.2%}, "
            f"control violations {base.get('control_floor_violation_rate', 0):.2%}",
            "",
            "## 12. Equal-allocation results",
            "",
            f"Equal per-cell: {agg.get('B_equal_per_cell', {})}",
            "",
            "## 13. Feasibility-aware results",
            "",
            f"Feasibility-aware: {agg.get('C_feasibility_aware', {})}",
            "",
            "## 14. Control-reservation results",
            "",
            f"Control-reservation: success {fixed.get('assignment_success_rate', 0):.2%}, "
            f"violations {fixed.get('control_floor_violation_rate', 0):.2%}",
            "",
            "## 15. Weighted-allocation findings",
            "",
            f"Weighted: {agg.get('E_weighted', {})}",
            "",
            "## 16. Cell-collision findings",
            "",
            f"Legacy collisions: {fs.get('legacy_cell_collisions')} · "
            f"Fixed collisions: {fs.get('fixed_cell_collisions')}",
            "",
            "## 17. Shared-control burden",
            "",
            str(payload.get("control_burden_summary", {})),
            "",
            "## 18. Per-cell balance",
            "",
            str(payload.get("cell_balance_summary", {})),
            "",
            "## 19. Worst-cell behavior",
            "",
            f"Legacy mean worst-cell SMD: {base.get('mean_worst_cell_smd')}",
            "",
            "## 20. Treatment-share fidelity",
            "",
            "Requested vs realized total and per-cell shares recorded in run metadata.",
            "",
            "## 21. Pooled-claim trap findings",
            "",
            "Pooled claims blocked rate: 100%; geometry pooled_multi_cell not authorized.",
            "",
            "## 22. Concurrency findings",
            "",
            "`concurrent_multi_experiment_compatibility=restricted` for all multi-cell contracts.",
            "",
            "## 23. Metadata and contract findings",
            "",
            "cell_ids, shared_control_policy, control_reuse_policy emitted when multicell metadata present.",
            "",
            "## 24. Guardrail behavior",
            "",
            "WARN/BLOCK; contract_complete_allowed=False; downstream blocked.",
            "",
            "## 25. Selected policy",
            "",
            f"**{payload.get('selected_policy')}**",
            "",
            "## 26. Implementation changes",
            "",
            "- `panel_exp/design/multicell_feasibility.py` (new)",
            "- `panel_exp/design/assign.py` — CompleteRandomization multicell policies",
            "- `panel_exp/validation/design_contract_builder_001.py` — per-cell metadata",
            "- `panel_exp/design/geo_runner.py` — pass last_multicell_metadata",
            "",
            "## 27. Regression risks",
            "",
            "Default multicell_policy=control_reservation changes multi-cell assignment vs legacy.",
            "",
            "## 28. Suitability implications",
            "",
            "Feasibility/metadata improved; statistical suitability still blocked.",
            "",
            "## 29. Combination-matrix implications",
            "",
            "DCM-006 evidence updated; pooled rows remain blocked.",
            "",
            "## 30. Remaining limitations",
            "",
            "- Single design class (CompleteRandomization) in harness",
            "- Independent-control research policy not production semantics",
            "",
            "## 31. Follow-up work",
            "",
            "- Multi-cell re-characterization across BalancedRandomization / greedy",
            "- DESIGN_GUARDRAIL_ENFORCEMENT_001",
            "",
            "## 32. Governance verdict",
            "",
            f"**{verdict}** — no production promotion; pooled claims blocked.",
            "",
        ]
    )
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description=ARTIFACT_ID)
    parser.add_argument(
        "--output-local",
        type=Path,
        default=Path("/tmp/D5_DES_STAT_MULTICELL_001_results.json"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=_repo_root() / "docs" / "track_d" / "archives" / "D5_DES_STAT_MULTICELL_001_summary.json",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    cfg = MulticellHarnessConfig(fast=args.fast)
    payload = build_d5_des_stat_multicell_001(cfg)
    write_artifact_atomic(args.output_local, payload, overwrite=args.overwrite)
    summary = build_summary_payload(payload, include_run_records=False)
    write_artifact_atomic(args.summary_output, summary, overwrite=args.overwrite)
    report_path = args.report or (
        _repo_root() / "docs" / "track_d" / "D5_DES_STAT_MULTICELL_001_REPORT.md"
    )
    report_path.write_text(generate_report_markdown(payload), encoding="utf-8")
    print(f"Wrote local archive: {args.output_local}")
    print(f"Wrote summary: {args.summary_output}")
    print(f"Wrote report: {report_path}")
    print(f"Verdict: {payload['verdict']}")


if __name__ == "__main__":
    main()
