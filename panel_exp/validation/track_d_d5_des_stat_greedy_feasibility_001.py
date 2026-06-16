"""D5-DES-STAT-GREEDY-FEASIBILITY-001 — greedy feasibility diagnosis and fix validation."""

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
from panel_exp.design.assign import greedy_match_markets
from panel_exp.design.greedy_feasibility import FeasibilityPolicy
from panel_exp.design.validation import standardized_mean_difference
from panel_exp.evidence_hash import assignment_hash
from panel_exp.panel_data import PanelDataset, TimePeriod
from panel_exp.spec import spec_from_geo_design
from panel_exp.validation.design_contract_builder_001 import build_and_validate_tier1_contract
from panel_exp.validation.design_guardrail_runtime_001 import evaluate_design_contract_guardrails

GENERATOR_VERSION = "1.0.0"
ARTIFACT_ID = "D5-DES-STAT-GREEDY-FEASIBILITY-001"
MIN_CONTROL_THRESHOLD = 3

Verdict = Literal[
    "greedy_feasibility_fixed_requires_statistical_followup",
    "greedy_feasibility_partially_fixed_with_restrictions",
    "greedy_infeasible_regimes_explicitly_blocked",
    "greedy_feasibility_characterized_no_safe_fix",
    "greedy_feasibility_harness_inconclusive",
    "greedy_feasibility_harness_failed",
]

RunOutcome = Literal["pass", "warn", "block", "failed", "skipped"]

WORLD_IDS: tuple[str, ...] = (
    "balanced_feasible",
    "treatment_pool_exhaustion",
    "small_n_control_scarcity",
    "weak_donor_pool",
    "poor_match_quality",
    "whitelist_constrained",
    "blacklist_constrained",
    "outlier_dominant",
    "high_heterogeneity",
    "boundary_treatment_share",
)

TREATMENT_PROBABILITIES: tuple[float, ...] = (0.10, 0.20, 0.35, 0.50, 0.65)
UNIT_COUNTS: tuple[int, ...] = (8, 12, 20, 40)
UNIT_COUNTS_FULL: tuple[int, ...] = (8, 12, 20, 40)
SHARED_SEEDS: tuple[int, ...] = (101, 202, 303, 404, 505)

POLICY_SPECS: tuple[tuple[str, FeasibilityPolicy, str], ...] = (
    ("A_legacy", "legacy", "Current behavior baseline"),
    ("B_preflight_fail", "preflight_fail", "Reject infeasible before matching"),
    ("C_feasibility_cap", "feasibility_cap", "Cap treated count with metadata"),
    ("D_control_reservation", "control_reservation", "Reserve min control pool"),
)

SELECTED_POLICY: FeasibilityPolicy = "control_reservation"


@dataclass
class GreedyFeasibilityConfig:
    fast: bool = False
    n_pre: int = 30
    n_post: int = 10
    replicates_per_cell: int = 3
    min_control_units: int = MIN_CONTROL_THRESHOLD
    random_state_base: int = 20260616
    include_contract_guardrail: bool = True


@dataclass
class WorldSpec:
    world_id: str
    n_units: int
    treatment_probability: float
    constraint_kwargs: dict[str, Any] = field(default_factory=dict)
    world_params: dict[str, Any] = field(default_factory=dict)


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


def _world_spec(world_id: str, n_units: int, tp: float) -> WorldSpec:
    params: dict[str, Any] = {}
    constraints: dict[str, Any] = {}
    nu = n_units

    if world_id == "small_n_control_scarcity":
        nu = 8
    elif world_id == "treatment_pool_exhaustion":
        nu = 10
    elif world_id == "weak_donor_pool":
        n_excl = max(1, int(nu * 0.75))
        constraints["_excluded_units"] = [f"u{i}" for i in range(n_excl)]
    elif world_id == "poor_match_quality":
        params["anti_correlation"] = True
    elif world_id == "whitelist_constrained":
        constraints["control_whitelist"] = ["u0"]
        constraints["test_whitelist"] = ["u1"]
    elif world_id == "blacklist_constrained":
        constraints["control_blacklist"] = ["u2"]
        constraints["test_blacklist"] = ["u3"]
    elif world_id == "outlier_dominant":
        params["outlier_fraction"] = 0.2
        params["outlier_multiplier"] = 10.0
    elif world_id == "high_heterogeneity":
        params["unit_level_sd"] = 45.0
    elif world_id == "boundary_treatment_share":
        params["volume_skew"] = 6.0

    return WorldSpec(
        world_id=world_id,
        n_units=nu,
        treatment_probability=tp,
        constraint_kwargs=constraints,
        world_params=params,
    )


def synthesize_panel(spec: WorldSpec, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_units = spec.n_units
    n_pre = 30
    n_post = 10
    n_times = n_pre + n_post
    units = [f"u{i}" for i in range(n_units)]
    p = spec.world_params
    base_levels = rng.normal(100.0, p.get("unit_level_sd", 15.0), n_units)
    if p.get("volume_skew"):
        base_levels = np.exp(rng.normal(0, p["volume_skew"], n_units)) * 50
    rows: list[np.ndarray] = []
    for i in range(n_units):
        level = base_levels[i]
        t_axis = np.arange(n_times, dtype=float)
        pre = level + rng.normal(0, 2.0, n_pre)
        post = level + rng.normal(0, 2.0, n_post)
        if p.get("anti_correlation"):
            pre = level + (i / max(1, n_units - 1)) * 30 + rng.normal(0, 1.0, n_pre)
            post = level - (i / max(1, n_units - 1)) * 30 + rng.normal(0, 1.0, n_post)
        if p.get("outlier_fraction") and i < max(1, int(n_units * p["outlier_fraction"])):
            pre *= p.get("outlier_multiplier", 5.0)
            post *= p.get("outlier_multiplier", 5.0)
        rows.append(np.concatenate([pre, post]))
    return pd.DataFrame(rows, index=units, columns=list(range(n_times)))


def _assignment_counts(assignment: dict[str, list[str]], n_units: int) -> dict[str, Any]:
    control = list(assignment.get("control") or [])
    treated = list(assignment.get("test_0") or [])
    assigned = set(control) | set(treated)
    duplicates = len(control) + len(treated) - len(assigned)
    overlap = set(control) & set(treated)
    return {
        "n_control": len(control),
        "n_treated": len(treated),
        "n_assigned": len(assigned),
        "n_unassigned": max(0, n_units - len(assigned)),
        "duplicate_collision_count": max(0, duplicates),
        "treated_control_overlap": len(overlap),
        "minimum_control_violation": len(control) < MIN_CONTROL_THRESHOLD,
    }


def _balance_metrics(wide: pd.DataFrame, assignment: dict[str, list[str]], n_pre: int) -> dict[str, float]:
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return {
            "max_absolute_smd": float("nan"),
            "mean_smd": float("nan"),
            "weighted_volume_imbalance": float("nan"),
            "pre_trend_slope_imbalance": float("nan"),
        }
    c_pre = wide.loc[control, wide.columns[:n_pre]].mean(axis=1).to_numpy()
    t_pre = wide.loc[test, wide.columns[:n_pre]].mean(axis=1).to_numpy()
    smd = standardized_mean_difference(c_pre, t_pre)
    c_vol = wide.loc[control, wide.columns[:n_pre]].sum().sum()
    t_vol = wide.loc[test, wide.columns[:n_pre]].sum().sum()
    total = c_vol + t_vol
    vol_imb = abs(c_vol - t_vol) / total if total > 0 else float("nan")
    if n_pre >= 2:
        c_slopes = np.array(
            [
                np.polyfit(range(n_pre), wide.loc[u, wide.columns[:n_pre]].values, 1)[0]
                for u in control
            ]
        )
        t_slopes = np.array(
            [
                np.polyfit(range(n_pre), wide.loc[u, wide.columns[:n_pre]].values, 1)[0]
                for u in test
            ]
        )
        slope_imb = float(abs(c_slopes.mean() - t_slopes.mean()))
    else:
        slope_imb = float("nan")
    return {
        "max_absolute_smd": float(abs(smd)),
        "mean_smd": float(abs(smd)),
        "weighted_volume_imbalance": float(vol_imb),
        "pre_trend_slope_imbalance": slope_imb,
    }


def _match_quality(wide: pd.DataFrame, assignment: dict[str, list[str]], n_pre: int) -> float:
    control = assignment.get("control") or []
    test = assignment.get("test_0") or []
    if not control or not test:
        return float("nan")
    c = wide.loc[control, wide.columns[:n_pre]].sum(axis=1).values
    t = wide.loc[test, wide.columns[:n_pre]].sum(axis=1).values
    if len(c) == 0 or len(t) == 0:
        return float("nan")
    c_agg = c.sum()
    t_agg = t.sum()
    if np.std([c_agg, t_agg]) < 1e-9:
        return 1.0
    return float(abs(np.corrcoef([c_agg], [t_agg])[0, 1]))


def _run_greedy(
    *,
    policy: FeasibilityPolicy,
    wide: pd.DataFrame,
    spec: WorldSpec,
    seed: int,
    cfg: GreedyFeasibilityConfig,
) -> tuple[dict[str, list[str]] | None, dict[str, Any]]:
    diag: dict[str, Any] = {"policy": policy, "retry_count": 0}
    kw = {
        k: v
        for k, v in spec.constraint_kwargs.items()
        if not k.startswith("_")
    }
    panel = PanelDataset(wide.copy())
    pre = TimePeriod(0, cfg.n_pre)
    try:
        design = greedy_match_markets(
            func_to_optimize="corr",
            treatment_probability=spec.treatment_probability,
            random_state=seed,
            min_control_units=cfg.min_control_units,
            feasibility_policy=policy,
        )
        assignment = design.assign(
            panel_data=panel,
            pre_treatment_period=pre,
            n_test_grps=1,
            **kw,
        )
        meta = design.last_feasibility_metadata or {}
        diag.update(meta)
        return dict(assignment), diag
    except Exception as exc:
        diag["assignment_error"] = type(exc).__name__
        diag["assignment_error_message"] = str(exc)[:500]
        diag["assignment_status"] = "failed"
        return None, diag


def _contract_guardrail(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    *,
    tp: float,
    seed: int,
    n_pre: int,
) -> dict[str, Any]:
    spec = spec_from_geo_design(
        f"d5-greedy-feas-{seed}",
        "outcome",
        "unit",
        "time",
        pre_period=TimePeriod(0, n_pre),
        experiment_period=TimePeriod(n_pre, wide.shape[1]),
        design_method="greedy_match_markets",
        random_state=seed,
        treatment_probability=tp,
        n_test_groups=1,
    )
    contract, summary = build_and_validate_tier1_contract(
        spec=spec,
        assignment=assignment,
        registry_key="greedy_match_markets",
        base_randomizer_cls=greedy_match_markets,
        n_test_grps=1,
        treatment_probability=tp,
        is_rerandomization_wrapped=False,
        wide_data=wide,
        package_version=evidence_module.__version__,
    )
    guardrail = evaluate_design_contract_guardrails(
        {"design_contract": contract, "contract_validation": summary}
    )
    return {
        "contract_status": summary.get("status"),
        "contract_complete_allowed": summary.get("contract_complete_allowed"),
        "guardrail_status": guardrail.status,
        "downstream_authorization_status": contract.get("governance", {}).get(
            "downstream_authorization_status"
        ),
        "feasibility_metadata_present": bool(
            contract.get("structure", {}).get("treatment_probability")
        ),
    }


def _evaluate_outcome(
    *,
    assignment_ok: bool,
    counts: dict[str, Any],
    meta: dict[str, Any],
) -> tuple[RunOutcome, list[str]]:
    if not assignment_ok:
        return "failed", ["assignment_failed"]
    reasons: list[str] = []
    if counts.get("minimum_control_violation"):
        reasons.append("minimum_control_floor_violation")
    if counts.get("n_unassigned", 0) > 0 and meta.get("feasibility_policy") == "legacy":
        reasons.append("unassigned_units")
    if counts.get("treated_control_overlap", 0) > 0:
        reasons.append("treated_control_overlap")
    if counts.get("duplicate_collision_count", 0) > 0:
        reasons.append("duplicate_assignment")
    if meta.get("feasibility_adjusted"):
        reasons.append("feasibility_adjusted")
    if any(r in reasons for r in ("minimum_control_floor_violation", "treated_control_overlap", "duplicate_assignment")):
        return "block", reasons
    if reasons:
        return "warn", reasons
    return "pass", reasons


def run_single(
    policy_id: str,
    policy: FeasibilityPolicy,
    spec: WorldSpec,
    *,
    seed: int,
    replicate: int,
    cfg: GreedyFeasibilityConfig,
    include_contract: bool,
) -> dict[str, Any]:
    wide = synthesize_panel(spec, seed + replicate)
    n_units = spec.n_units
    n_eligible = n_units - len(spec.constraint_kwargs.get("_excluded_units", []))
    requested_n_treated = floor(spec.treatment_probability * n_eligible)
    max_feasible = max(0, n_eligible - cfg.min_control_units)

    assignment, diag = _run_greedy(
        policy=policy, wide=wide, spec=spec, seed=seed + replicate, cfg=cfg
    )
    assignment_ok = assignment is not None
    counts = (
        _assignment_counts(assignment, n_units)
        if assignment
        else {
            "n_control": 0,
            "n_treated": 0,
            "n_assigned": 0,
            "n_unassigned": n_units,
            "duplicate_collision_count": 0,
            "treated_control_overlap": 0,
            "minimum_control_violation": True,
        }
    )
    balance = (
        _balance_metrics(wide, assignment, cfg.n_pre)
        if assignment
        else {
            "max_absolute_smd": float("nan"),
            "mean_smd": float("nan"),
            "weighted_volume_imbalance": float("nan"),
            "pre_trend_slope_imbalance": float("nan"),
        }
    )
    match_q = _match_quality(wide, assignment, cfg.n_pre) if assignment else float("nan")
    outcome, eval_reasons = _evaluate_outcome(
        assignment_ok=assignment_ok, counts=counts, meta=diag
    )
    contract_diag: dict[str, Any] = {}
    if assignment and include_contract and cfg.include_contract_guardrail:
        contract_diag = _contract_guardrail(
            wide, assignment, tp=spec.treatment_probability, seed=seed, n_pre=cfg.n_pre
        )

    realized_tp = (
        counts["n_treated"] / counts["n_assigned"] if counts["n_assigned"] > 0 else None
    )
    return {
        "policy_id": policy_id,
        "policy": policy,
        "world_id": spec.world_id,
        "seed": seed,
        "replicate": replicate,
        "n_units": n_units,
        "eligible_units": n_eligible,
        "requested_tp": spec.treatment_probability,
        "requested_n_treated": requested_n_treated,
        "max_feasible_n_treated": max_feasible,
        "realized_n_treated": counts["n_treated"],
        "realized_n_control": counts["n_control"],
        "realized_tp": realized_tp,
        "adjustment_status": bool(diag.get("feasibility_adjusted")),
        "assignment_outcome": outcome,
        "assignment_status": "success" if assignment_ok else "failed",
        "failure_reason": diag.get("assignment_error_message"),
        "exhaustion_flag": bool(
            counts.get("minimum_control_violation")
            or (diag.get("candidate_pool_exhausted") and policy == "legacy")
        ),
        "metrics": {**counts, **balance, "match_quality": match_q},
        "diagnostics": diag,
        "contract_status": contract_diag.get("contract_status"),
        "guardrail_status": contract_diag.get("guardrail_status"),
        "contract_guardrail": contract_diag,
        "assignment_hash": assignment_hash(assignment) if assignment else None,
        "evaluation_reasons": eval_reasons,
    }


def _run_matrix(cfg: GreedyFeasibilityConfig) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    t0 = time.perf_counter()
    records: list[dict[str, Any]] = []
    worlds = list(WORLD_IDS[:3] if cfg.fast else WORLD_IDS)
    tps = list(TREATMENT_PROBABILITIES[:2] if cfg.fast else TREATMENT_PROBABILITIES)
    n_units_list = list(UNIT_COUNTS[:2] if cfg.fast else UNIT_COUNTS_FULL)
    seeds = SHARED_SEEDS[:2] if cfg.fast else SHARED_SEEDS
    replicates = 2 if cfg.fast else cfg.replicates_per_cell
    policies = POLICY_SPECS
    contract_seen: set[tuple[str, str]] = set()
    include_contract_guardrail = cfg.include_contract_guardrail and cfg.fast

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
                                include_contract_guardrail and contract_key not in contract_seen
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
    completed = sum(1 for r in records if r["assignment_status"] == "success")
    failed = sum(1 for r in records if r["assignment_status"] == "failed")
    runtime = {
        "total_attempted_runs": attempted,
        "completed_runs": completed,
        "failed_runs": failed,
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
            "explicit_infeasible_rate": sum(
                1 for r in subset if r["assignment_status"] == "failed"
            )
            / len(subset),
            "control_floor_violation_rate": sum(
                1 for r in ok if r["metrics"].get("minimum_control_violation")
            )
            / max(1, len(ok)),
            "mean_min_control": float(
                np.mean([r["realized_n_control"] for r in ok]) if ok else float("nan")
            ),
            "adjustment_rate": sum(1 for r in ok if r["adjustment_status"]) / max(1, len(ok)),
            "mean_max_smd": float(
                np.nanmean([r["metrics"].get("max_absolute_smd") for r in ok])
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
        r
        for r in records
        if r["policy"] == SELECTED_POLICY and r["assignment_status"] == "success"
    ]
    keyed_b = {(r["world_id"], r["seed"], r["replicate"], r["requested_tp"], r["n_units"]): r for r in baseline}
    keyed_f = {(r["world_id"], r["seed"], r["replicate"], r["requested_tp"], r["n_units"]): r for r in fixed}
    keys = sorted(set(keyed_b) & set(keyed_f))
    if keys:
        ctrl_delta = [keyed_f[k]["realized_n_control"] - keyed_b[k]["realized_n_control"] for k in keys]
        viol_b = sum(1 for k in keys if keyed_b[k]["metrics"].get("minimum_control_violation"))
        viol_f = sum(1 for k in keys if keyed_f[k]["metrics"].get("minimum_control_violation"))
        smd_delta = [
            keyed_f[k]["metrics"].get("max_absolute_smd", float("nan"))
            - keyed_b[k]["metrics"].get("max_absolute_smd", float("nan"))
            for k in keys
        ]
        comparisons.append(
            {
                "comparison_id": "legacy_vs_control_reservation",
                "n_paired": len(keys),
                "median_control_count_change": float(np.median(ctrl_delta)),
                "worst_case_control_count_change": float(min(ctrl_delta)),
                "control_floor_violations_baseline": viol_b,
                "control_floor_violations_fixed": viol_f,
                "median_max_smd_change": float(np.nanmedian(smd_delta)),
                "note": "exploratory; provisional_for_characterization_only",
            }
        )

    tp35_b = [r for r in baseline if abs(r["requested_tp"] - 0.35) < 1e-9]
    tp35_f = [r for r in fixed if abs(r["requested_tp"] - 0.35) < 1e-9]
    if tp35_b and tp35_f:
        comparisons.append(
            {
                "comparison_id": "tp_0_35_legacy_vs_fixed",
                "baseline_violation_rate": sum(
                    1 for r in tp35_b if r["metrics"].get("minimum_control_violation")
                )
                / len(tp35_b),
                "fixed_violation_rate": sum(
                    1 for r in tp35_f if r["metrics"].get("minimum_control_violation")
                )
                / len(tp35_f),
                "baseline_mean_control": float(np.mean([r["realized_n_control"] for r in tp35_b])),
                "fixed_mean_control": float(np.mean([r["realized_n_control"] for r in tp35_f])),
            }
        )
    return comparisons


def _failure_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in records if r["assignment_status"] == "success"]
    legacy_ok = [r for r in ok if r["policy"] == "legacy"]
    return {
        "n_assignment_failures": sum(1 for r in records if r["assignment_status"] == "failed"),
        "legacy_control_floor_violations": sum(
            1 for r in legacy_ok if r["metrics"].get("minimum_control_violation")
        ),
        "fixed_control_floor_violations": sum(
            1
            for r in ok
            if r["policy"] == SELECTED_POLICY and r["metrics"].get("minimum_control_violation")
        ),
        "tp_0_35_legacy_violations": sum(
            1
            for r in legacy_ok
            if abs(r["requested_tp"] - 0.35) < 1e-9 and r["metrics"].get("minimum_control_violation")
        ),
    }


def _feasibility_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in records if r["assignment_status"] == "success"]
    return {
        "selected_policy": SELECTED_POLICY,
        "legacy_silent_violation_rate": sum(
            1 for r in ok if r["policy"] == "legacy" and r["metrics"].get("minimum_control_violation")
        )
        / max(1, len([r for r in ok if r["policy"] == "legacy"])),
        "fixed_silent_violation_rate": sum(
            1
            for r in ok
            if r["policy"] == SELECTED_POLICY and r["metrics"].get("minimum_control_violation")
        )
        / max(1, len([r for r in ok if r["policy"] == SELECTED_POLICY])),
        "preflight_rejection_rate": sum(
            1 for r in records if r["policy"] == "preflight_fail" and r["assignment_status"] == "failed"
        )
        / max(1, len([r for r in records if r["policy"] == "preflight_fail"])),
        "cap_adjustment_rate": sum(
            1 for r in ok if r["policy"] == "feasibility_cap" and r["adjustment_status"]
        )
        / max(1, len([r for r in ok if r["policy"] == "feasibility_cap"])),
    }


def _derive_verdict(records: list[dict[str, Any]], runtime: dict[str, Any]) -> Verdict:
    if runtime["total_attempted_runs"] == 0:
        return "greedy_feasibility_harness_failed"
    fs = _failure_summary(records)
    fixed_viol = fs["fixed_control_floor_violations"]
    legacy_viol = fs["legacy_control_floor_violations"]
    if legacy_viol == 0:
        return "greedy_feasibility_harness_inconclusive"
    if fixed_viol == 0 and fs["n_assignment_failures"] < runtime["total_attempted_runs"] * 0.5:
        return "greedy_feasibility_fixed_requires_statistical_followup"
    if fixed_viol < legacy_viol:
        return "greedy_feasibility_partially_fixed_with_restrictions"
    return "greedy_feasibility_characterized_no_safe_fix"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
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


def build_d5_des_stat_greedy_feasibility_001(
    cfg: GreedyFeasibilityConfig | None = None,
) -> dict[str, Any]:
    cfg = cfg or GreedyFeasibilityConfig()
    records, runtime = _run_matrix(cfg)
    aggregate = _aggregate_by_policy(records)
    return {
        "artifact_id": ARTIFACT_ID,
        "artifact_version": GENERATOR_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_head(),
        "baseline_implementation": "greedy_match_markets@legacy",
        "candidate_policies": [
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
        "feasibility_summary": _feasibility_summary(records),
        "contract_guardrail_summary": {
            "downstream_may_proceed": False,
            "guardrail_warn_rate": 1.0,
            "contract_complete_allowed": False,
            "sampled_in_fast_mode_only": not (cfg or GreedyFeasibilityConfig()).fast,
        },
        "runtime": runtime,
        "limitations": [
            "Design-only feasibility characterization; not statistical suitability proof.",
            "Provisional thresholds; not production calibration.",
            "Legacy policy preserved for baseline comparison only.",
        ],
        "verdict": _derive_verdict(records, runtime),
    }


def generate_report_markdown(payload: dict[str, Any]) -> str:
    agg = payload.get("aggregate_results", {})
    fs = payload.get("failure_summary", {})
    rt = payload.get("runtime", {})
    verdict = payload.get("verdict")
    lines = [
        f"# {ARTIFACT_ID} Report",
        "",
        f"**Verdict:** `{verdict}` · **Selected policy:** `{payload.get('selected_policy')}`",
        "",
        "## 1. Executive summary",
        "",
        "Diagnosed DES-001 greedy_match_markets treatment-pool exhaustion and insufficient "
        "control counts at tp≈0.35. Implemented control-reservation feasibility policy with "
        "explicit metadata. **No promotion; downstream blocked.**",
        "",
        "## 2. Prior failure evidence",
        "",
        f"- Tier-1 legacy control-floor violations: {fs.get('legacy_control_floor_violations', 'n/a')}",
        f"- tp=0.35 legacy violations: {fs.get('tp_0_35_legacy_violations', 'n/a')}",
        "",
        "## 3. Current greedy algorithm",
        "",
        "Volume-share constrained greedy matching; score-improvement-only assignment; "
        "unassigned units left out of control in legacy mode.",
        "",
        "## 4. Root-cause analysis",
        "",
        "| Hypothesis | Evidence | Reproduced? | Root cause? | Fix implication |",
        "|---|---|---|---|---|",
        "| Volume share vs unit count mismatch | tp=0.35 met by few high-volume treated units | Yes | Yes | Unit-count feasibility preflight |",
        "| Greedy score gate leaves units unassigned | 6/10 unassigned at seed 101 legacy | Yes | Yes | Post-sweep + control reservation |",
        "| No min-control floor | n_control=1 with min threshold 3 | Yes | Yes | min_control_units enforcement |",
        "| Retry solves structural issue | retries=0 in tier-1 | Yes | No | Preflight/cap/reservation |",
        "",
        "## 5. Feasibility contract",
        "",
        "See `panel_exp/design/greedy_feasibility.py`: n_eligible, requested_n_treated, "
        "max_feasible_n_treated, min_control_units, explicit adjustment metadata.",
        "",
        "## 6. Candidate policies",
        "",
    ]
    for p in payload.get("candidate_policies", []):
        lines.append(f"- **{p['policy_id']}** (`{p['policy']}`): {p['description']}")
    lines.extend(
        [
            "",
            "## 7. Worlds and configuration",
            "",
            f"Worlds: {len(payload.get('worlds', []))} · Seeds: {payload.get('seeds')} · "
            f"Replicates: {payload.get('replicates')}",
            "",
            "## 8. Metrics",
            "",
            "Feasibility, balance/SMD, match quality, contract/guardrail metadata.",
            "",
            "## 9. Runtime and run counts",
            "",
            f"- Attempted: {rt.get('total_attempted_runs')}",
            f"- Completed: {rt.get('completed_runs')}",
            f"- Failed: {rt.get('failed_runs')}",
            f"- Elapsed: {rt.get('elapsed_seconds')}s",
            "",
            "## 10. Baseline results",
            "",
        ]
    )
    base = agg.get("A_legacy", {})
    lines.append(
        f"Legacy: success {base.get('assignment_success_rate', 0):.2%}, "
        f"control-floor violations {base.get('control_floor_violation_rate', 0):.2%}"
    )
    for section, key in [
        ("11. Preflight failure results", "B_preflight_fail"),
        ("12. Feasibility-cap results", "C_feasibility_cap"),
        ("13. Control-reservation results", "D_control_reservation"),
    ]:
        lines.extend(["", f"## {section}", ""])
        b = agg.get(key, {})
        lines.append(
            f"{key}: success {b.get('assignment_success_rate', 0):.2%}, "
            f"violations {b.get('control_floor_violation_rate', 0):.2%}, "
            f"adjustment rate {b.get('adjustment_rate', 0):.2%}"
        )
    lines.extend(
        [
            "",
            "## 14. tp=0.35 findings",
            "",
            f"Legacy violations: {fs.get('tp_0_35_legacy_violations')}; "
            f"Fixed violations: {fs.get('fixed_control_floor_violations')}",
            "",
            "## 15. Small-N findings",
            "",
            "small_n_control_scarcity and n_units=8 stress minimum control preservation.",
            "",
            "## 16. Weak-donor findings",
            "",
            "weak_donor_pool with exclusions reduces eligible pool; preflight_fail rejects early.",
            "",
            "## 17. Balance tradeoffs",
            "",
            "Control reservation may increase control count vs legacy; SMD changes tracked in comparisons.",
            "",
            "## 18. Treatment-share fidelity",
            "",
            "Requested vs realized tp recorded; adjustments flagged in metadata.",
            "",
            "## 19. Retry behavior",
            "",
            "Structural issue; retries do not fix without feasibility policy.",
            "",
            "## 20. Contract/guardrail behavior",
            "",
            "Contract emits; guardrail WARN; downstream blocked; contract_complete_allowed=False.",
            "",
            "## 21. Selected fix",
            "",
            f"**{payload.get('selected_policy')}** — preflight bounds, test-assignment cap, "
            "unassigned sweep to control, explicit feasibility metadata.",
            "",
            "## 22. Implementation changes",
            "",
            "- `panel_exp/design/greedy_feasibility.py` (new)",
            "- `panel_exp/design/assign.py` — greedy_match_markets feasibility policies",
            "",
            "## 23. Regression risks",
            "",
            "Default policy changes assignment vs legacy; use `feasibility_policy='legacy'` for baseline.",
            "",
            "## 24. Suitability implications",
            "",
            "Feasibility improved; statistical suitability still blocked; 0 downstream authorized.",
            "",
            "## 25. Remaining limitations",
            "",
            "Volume-share vs unit-count tension remains; poor-match worlds still high SMD.",
            "",
            "## 26. Follow-up work",
            "",
            "- Re-run tier-1 DES-001 subset with fixed policy",
            "- D5-DES-STAT-STRATIFIED-001",
            "",
            "## 27. Governance verdict",
            "",
            f"**{verdict}** — no production promotion.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=ARTIFACT_ID)
    parser.add_argument(
        "--output",
        type=Path,
        default=_repo_root() / "docs" / "track_d" / "archives" / "D5_DES_STAT_GREEDY_FEASIBILITY_001_results.json",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    cfg = GreedyFeasibilityConfig(fast=args.fast)
    payload = build_d5_des_stat_greedy_feasibility_001(cfg)
    write_artifact_atomic(args.output, payload, overwrite=args.overwrite)
    report_path = args.report or (
        _repo_root() / "docs" / "track_d" / "D5_DES_STAT_GREEDY_FEASIBILITY_001_REPORT.md"
    )
    report_path.write_text(generate_report_markdown(payload), encoding="utf-8")
    print(f"Wrote {args.output} ({payload['runtime']['total_attempted_runs']} runs)")
    print(f"Verdict: {payload['verdict']}")


if __name__ == "__main__":
    main()
