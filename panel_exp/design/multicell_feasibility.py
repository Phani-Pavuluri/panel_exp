"""Feasibility contract and assignment policies for DES-011 multi-cell designs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import floor
from typing import Any, Literal

import numpy as np

from .constraints import ConstraintContext, freeze_assignment

MulticellPolicy = Literal[
    "legacy",
    "equal_per_cell",
    "feasibility_aware",
    "control_reservation",
    "weighted",
    "independent_control",
]

DEFAULT_MIN_CONTROL_UNITS = 3
DEFAULT_MIN_UNITS_PER_CELL = 1
SHARED_CONTROL_POLICY = "shared_single_control_arm"
CONTROL_REUSE_POLICY = "shared_donor_pool_across_cells"
PER_CELL_GEOMETRY = "multi_cell_per_cell"
POOLED_GEOMETRY = "pooled_multi_cell"
CONCURRENCY_COMPATIBILITY = "restricted"


@dataclass(frozen=True)
class MulticellFeasibilityContract:
    n_eligible: int
    requested_treatment_probability: float
    n_treatment_cells: int
    requested_total_treated: int
    requested_per_cell_share: tuple[float, ...]
    min_control_units: int
    min_units_per_cell: int
    shared_control_policy: str
    control_reuse_policy: str
    treatment_cell_exclusivity: bool
    pooled_claims_allowed: bool
    per_cell_geometry: str
    pooled_geometry: str
    concurrency_compatibility: str
    max_feasible_total_treated: int
    max_feasible_per_cell: int
    feasible: bool
    feasibility_reason: str | None
    policy: MulticellPolicy

    def to_metadata(self) -> dict[str, Any]:
        return asdict(self)


def _equal_shares(n_cells: int) -> tuple[float, ...]:
    share = 1.0 / n_cells
    return tuple(share for _ in range(n_cells))


def _normalize_weights(n_cells: int, weights: dict[str, float] | None) -> tuple[float, ...]:
    if not weights:
        return _equal_shares(n_cells)
    raw = [max(0.0, float(weights.get(f"test_{i}", 1.0))) for i in range(n_cells)]
    total = sum(raw) or float(n_cells)
    return tuple(v / total for v in raw)


def compute_multicell_feasibility(
    *,
    n_eligible: int,
    treatment_probability: float,
    n_treatment_cells: int,
    pinned_control: int = 0,
    pinned_test: int = 0,
    min_control_units: int = DEFAULT_MIN_CONTROL_UNITS,
    min_units_per_cell: int = DEFAULT_MIN_UNITS_PER_CELL,
    cell_weights: dict[str, float] | None = None,
    policy: MulticellPolicy = "control_reservation",
) -> MulticellFeasibilityContract:
    n_cells = max(1, int(n_treatment_cells))
    min_control = max(1, int(min_control_units))
    min_per_cell = max(1, int(min_units_per_cell))
    requested_total = max(0, floor(treatment_probability * n_eligible))
    requested_total = max(requested_total, pinned_test)
    per_cell_shares = _normalize_weights(n_cells, cell_weights)
    min_treated_for_cells = min_per_cell * n_cells
    max_feasible_total = max(0, n_eligible - min_control)

    feasible = True
    reason: str | None = None
    if n_eligible < min_control + min_treated_for_cells:
        feasible = False
        reason = "insufficient_units_for_min_control_and_cell_sizes"
    elif pinned_test > max_feasible_total:
        feasible = False
        reason = "pinned_test_exceeds_max_feasible_treated"
    elif pinned_control > max(0, n_eligible - min_treated_for_cells):
        feasible = False
        reason = "pinned_control_exceeds_feasible_pool"
    elif requested_total > max_feasible_total and policy in (
        "feasibility_aware",
        "control_reservation",
        "equal_per_cell",
        "weighted",
    ):
        reason = "requested_treated_will_be_capped"

    return MulticellFeasibilityContract(
        n_eligible=n_eligible,
        requested_treatment_probability=treatment_probability,
        n_treatment_cells=n_cells,
        requested_total_treated=requested_total,
        requested_per_cell_share=per_cell_shares,
        min_control_units=min_control,
        min_units_per_cell=min_per_cell,
        shared_control_policy=SHARED_CONTROL_POLICY,
        control_reuse_policy=CONTROL_REUSE_POLICY,
        treatment_cell_exclusivity=True,
        pooled_claims_allowed=False,
        per_cell_geometry=PER_CELL_GEOMETRY,
        pooled_geometry=POOLED_GEOMETRY,
        concurrency_compatibility=CONCURRENCY_COMPATIBILITY,
        max_feasible_total_treated=max_feasible_total,
        max_feasible_per_cell=max(0, (n_eligible - min_control) // n_cells),
        feasible=feasible,
        feasibility_reason=reason,
        policy=policy,
    )


def _legacy_round_robin_targets(total_treated: int, n_cells: int) -> list[int]:
    base = [0] * n_cells
    for i in range(total_treated):
        base[i % n_cells] += 1
    return base


def _proportional_targets(
    total_treated: int,
    shares: tuple[float, ...],
    *,
    min_per_cell: int,
    pinned: list[int],
) -> list[int]:
    n_cells = len(shares)
    if total_treated <= 0:
        return list(pinned)
    raw = [total_treated * s for s in shares]
    ints = [int(floor(x)) for x in raw]
    assigned = sum(ints)
    remainder = total_treated - assigned
    order = sorted(range(n_cells), key=lambda i: raw[i] - ints[i], reverse=True)
    for j in range(remainder):
        ints[order[j % n_cells]] += 1
    return [pinned[i] + max(min_per_cell, ints[i]) if pinned[i] == 0 else pinned[i] + ints[i] for i in range(n_cells)]


def assign_multicell(
    ctx: ConstraintContext,
    rng: np.random.Generator,
    *,
    feasibility: MulticellFeasibilityContract,
    policy: MulticellPolicy,
    cell_weights: dict[str, float] | None = None,
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    """Assign free units across shared control and disjoint treatment cells."""
    if policy == "independent_control":
        return _assign_independent_control(ctx, rng, feasibility)

    n_cells = ctx.n_test_grps
    control_group = list(ctx.pinned_control)
    test_groups = {f"test_{i}": list(ctx.pinned_test[f"test_{i}"]) for i in range(n_cells)}
    pinned_per_cell = [len(test_groups[f"test_{i}"]) for i in range(n_cells)]
    pinned_test = sum(pinned_per_cell)
    free = list(ctx.free_units)
    rng.shuffle(free)
    n_assignable = len(control_group) + pinned_test + len(free)

    if policy == "legacy":
        target_total = max(
            0,
            min(len(free), floor(ctx.treatment_probability * n_assignable) - pinned_test),
        )
        treated_free = (
            list(rng.choice(free, size=target_total, replace=False)) if target_total else []
        )
        remaining_free = [u for u in free if u not in treated_free]
        for i, u in enumerate(treated_free):
            test_groups[f"test_{i % n_cells}"].append(u)
        control_group.extend(remaining_free)
        assignment = freeze_assignment({"control": control_group, **test_groups})
        metadata = build_multicell_metadata(
            feasibility,
            assignment,
            n_assignable=n_assignable,
            adjustment_applied=False,
            fallback_used=False,
            fallback_reason=None,
            policy=policy,
        )
        return assignment, metadata

    target_total = max(
        0,
        min(
            len(free),
            floor(ctx.treatment_probability * n_assignable) - pinned_test,
            feasibility.max_feasible_total_treated - pinned_test,
        ),
    )
    if policy == "equal_per_cell":
        base = target_total // n_cells
        extra = target_total % n_cells
        cell_add_targets = [
            pinned_per_cell[i] + base + (1 if i < extra else 0) for i in range(n_cells)
        ]
    else:
        shares = _normalize_weights(n_cells, cell_weights if policy == "weighted" else None)
        cell_add_targets = _proportional_targets(
            target_total,
            shares,
            min_per_cell=feasibility.min_units_per_cell,
            pinned=pinned_per_cell,
        )

    treated_free = (
        list(rng.choice(free, size=target_total, replace=False)) if target_total else []
    )
    remaining_free = [u for u in free if u not in treated_free]
    pool = list(treated_free)
    rng.shuffle(pool)
    offset = 0
    for i in range(n_cells):
        need = max(0, cell_add_targets[i] - pinned_per_cell[i])
        need = min(need, len(pool) - offset)
        test_groups[f"test_{i}"].extend(pool[offset : offset + need])
        offset += need
    if offset < len(pool):
        for u in pool[offset:]:
            smallest = min(range(n_cells), key=lambda j: len(test_groups[f"test_{j}"]))
            test_groups[f"test_{smallest}"].append(u)

    control_group.extend(remaining_free)
    if policy in ("control_reservation", "feasibility_aware"):
        deficit = feasibility.min_control_units - len(control_group)
        for i in range(n_cells):
            while deficit > 0 and test_groups[f"test_{i}"]:
                u = test_groups[f"test_{i}"].pop()
                if u not in control_group:
                    control_group.append(u)
                    deficit -= 1
            if deficit <= 0:
                break

    assignment = freeze_assignment({"control": control_group, **test_groups})
    metadata = build_multicell_metadata(
        feasibility,
        assignment,
        n_assignable=n_assignable,
        adjustment_applied=bool(feasibility.feasibility_reason),
        fallback_used=False,
        fallback_reason=None,
        policy=policy,
    )
    return assignment, metadata


def _assign_independent_control(
    ctx: ConstraintContext,
    rng: np.random.Generator,
    feasibility: MulticellFeasibilityContract,
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    """Research-only: disjoint control pools per cell (not shared-control DES-011)."""
    n_cells = ctx.n_test_grps
    free = list(ctx.free_units)
    rng.shuffle(free)
    per_cell = max(1, len(free) // (n_cells * 2)) if free else 0
    test_groups = {f"test_{i}": list(ctx.pinned_test[f"test_{i}"]) for i in range(n_cells)}
    control_units: list[str] = list(ctx.pinned_control)
    idx = 0
    for i in range(n_cells):
        need = max(0, per_cell - len(test_groups[f"test_{i}"]))
        take = free[idx : idx + need]
        test_groups[f"test_{i}"].extend(take)
        idx += len(take)
    control_units.extend(free[idx:])
    assignment = freeze_assignment({"control": control_units, **test_groups})
    meta = build_multicell_metadata(
        feasibility,
        assignment,
        n_assignable=len(ctx.all_units) - len(ctx.excluded),
        adjustment_applied=True,
        fallback_used=False,
        fallback_reason=None,
        policy="independent_control",
        shared_control_policy="independent_per_cell_research_only",
        control_reuse_policy="no_reuse_across_cells",
    )
    return assignment, meta


def build_multicell_metadata(
    feasibility: MulticellFeasibilityContract,
    assignment: dict[str, list[str]],
    *,
    n_assignable: int,
    adjustment_applied: bool,
    fallback_used: bool,
    fallback_reason: str | None,
    policy: MulticellPolicy,
    shared_control_policy: str | None = None,
    control_reuse_policy: str | None = None,
) -> dict[str, Any]:
    n_cells = feasibility.n_treatment_cells
    cell_ids = [f"test_{i}" for i in range(n_cells)]
    per_cell_counts = [len(assignment.get(f"test_{i}", [])) for i in range(n_cells)]
    n_control = len(assignment.get("control", []))
    n_assigned = n_control + sum(per_cell_counts)
    realized_total_tp = sum(per_cell_counts) / n_assigned if n_assigned else None
    realized_per_cell = [
        (c / n_assigned if n_assigned else 0.0) for c in per_cell_counts
    ]
    requested_per_cell = list(feasibility.requested_per_cell_share)
    issues = diagnose_assignment(assignment, n_cells)
    burden = compute_control_burden(assignment, n_cells)
    return {
        **feasibility.to_metadata(),
        "cell_ids": cell_ids,
        "requested_total_treatment_share": feasibility.requested_treatment_probability,
        "realized_total_treatment_share": realized_total_tp,
        "requested_per_cell_shares": requested_per_cell,
        "realized_per_cell_shares": realized_per_cell,
        "per_cell_unit_counts": per_cell_counts,
        "realized_n_control": n_control,
        "realized_n_treated": sum(per_cell_counts),
        "shared_control_policy": shared_control_policy or feasibility.shared_control_policy,
        "control_reuse_policy": control_reuse_policy or feasibility.control_reuse_policy,
        "pooled_claims_allowed": False,
        "pooled_geometry_blocked": True,
        "per_cell_geometry_valid": not issues["cell_collisions"] and not issues["duplicate_assignments"],
        "concurrency_compatibility": feasibility.concurrency_compatibility,
        "adjustment_applied": adjustment_applied,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "policy": policy,
        "diagnostics": issues,
        "control_burden": burden,
    }


def diagnose_assignment(assignment: dict[str, list[str]], n_cells: int) -> dict[str, Any]:
    control = [str(u) for u in assignment.get("control", [])]
    tests = {f"test_{i}": [str(u) for u in assignment.get(f"test_{i}", [])] for i in range(n_cells)}
    seen: set[str] = set()
    duplicates: list[str] = []
    control_test_overlap: list[str] = []
    cell_collisions: list[str] = []
    for u in control:
        if u in seen:
            duplicates.append(u)
        seen.add(u)
    unit_to_cells: dict[str, list[str]] = {}
    for key, units in tests.items():
        for u in units:
            if u in seen and u not in duplicates:
                if u in control:
                    control_test_overlap.append(u)
                else:
                    cell_collisions.append(u)
            if u in unit_to_cells:
                cell_collisions.append(u)
                unit_to_cells[u].append(key)
            else:
                unit_to_cells[u] = [key]
            seen.add(u)
            if u in duplicates:
                duplicates.append(u)
    all_units = set(control) | {u for units in tests.values() for u in units}
    return {
        "duplicate_assignments": sorted(set(duplicates)),
        "treatment_control_overlap": sorted(set(control_test_overlap)),
        "cell_collisions": sorted(set(cell_collisions)),
        "treatment_cell_overlap_rate": len(cell_collisions) / max(1, sum(len(v) for v in tests.values())),
        "n_assigned": len(all_units),
        "unassigned_units": [],
    }


def compute_control_burden(assignment: dict[str, list[str]], n_cells: int) -> dict[str, Any]:
    n_control = len(assignment.get("control", []))
    per_cell = [len(assignment.get(f"test_{i}", [])) for i in range(n_cells)]
    comparisons = sum(n_control * c for c in per_cell if c > 0)
    return {
        "control_reuse_count": n_control,
        "n_comparisons_per_control_unit": (
            sum(per_cell) / n_control if n_control else float("inf")
        ),
        "effective_shared_control_support": n_control,
        "control_burden_index": comparisons / max(1, n_control),
        "n_cells_with_treatment": sum(1 for c in per_cell if c > 0),
    }


def per_cell_balance_metrics(
    wide: pd.DataFrame,
    assignment: dict[str, list[str]],
    n_cells: int,
    *,
    n_pre: int | None = None,
) -> dict[str, Any]:
    from panel_exp.design.validation import standardized_mean_difference

    if n_pre is not None and wide.shape[1] > n_pre:
        cov = wide.iloc[:, :n_pre].mean(axis=1)
    else:
        cov = wide.mean(axis=1)
    control = assignment.get("control", [])
    if not control:
        return {"worst_cell_max_smd": float("nan"), "mean_cell_max_smd": float("nan"), "per_cell": {}}
    ctrl_vals = cov.loc[control].values.astype(float)
    per_cell: dict[str, Any] = {}
    smds: list[float] = []
    for i in range(n_cells):
        key = f"test_{i}"
        treated = assignment.get(key, [])
        if not treated:
            per_cell[key] = {"max_absolute_smd": float("nan"), "n_treated": 0}
            continue
        trt_vals = cov.loc[treated].values.astype(float)
        smd = abs(standardized_mean_difference(trt_vals, ctrl_vals))
        smds.append(smd)
        per_cell[key] = {
            "max_absolute_smd": smd,
            "n_treated": len(treated),
            "group_size_ratio": len(treated) / max(1, len(control)),
        }
    return {
        "worst_cell_max_smd": max(smds) if smds else float("nan"),
        "mean_cell_max_smd": float(np.mean(smds)) if smds else float("nan"),
        "per_cell": per_cell,
    }
