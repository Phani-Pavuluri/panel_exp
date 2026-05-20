"""
Assignment constraint preparation and validation.

Whitelist/blacklist enforcement for geo design randomizers returning
{"control": [...], "test_0": ..., ...} dictionaries.

Semantics
---------
- Whitelisted units are pinned to the declared arm before randomization.
- Blacklisted units are excluded from assignment entirely.
- ``control_test_blacklist`` excludes a unit from both arms.
- Conflicting or impossible constraints raise ``ValueError`` before assignment.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd


Unit = str

LEGACY_ASSIGNMENT_GROUP_LABELS = ("control",)  # test_0, test_1, ... appended per n_test_grps


@dataclass
class ConstraintContext:
    all_units: List[Unit]
    excluded: Set[Unit]
    pinned_control: List[Unit]
    pinned_test: Dict[str, List[Unit]]
    free_units: List[Unit]
    n_test_grps: int
    treatment_probability: float


def freeze_constraint_lists(
    control_whitelist: Optional[List] = None,
    test_whitelist: Optional[List] = None,
    control_blacklist: Optional[List] = None,
    test_blacklist: Optional[List] = None,
    control_test_blacklist: Optional[List] = None,
) -> Tuple[List, List, List, List, List]:
    """Return copies of constraint lists so callers are not mutated."""
    return (
        list(control_whitelist or []),
        list(test_whitelist or []),
        list(control_blacklist or []),
        list(test_blacklist or []),
        list(control_test_blacklist or []),
    )


def freeze_assignment(assignment: Dict[str, List]) -> Dict[str, List]:
    """Deep-copy assignment group lists (output schema unchanged)."""
    return {k: list(v) for k, v in assignment.items()}


def _normalize_lists(
    control_whitelist: Optional[List],
    test_whitelist: Optional[List],
    control_blacklist: Optional[List],
    test_blacklist: Optional[List],
    control_test_blacklist: Optional[List],
    n_test_grps: int,
) -> Tuple[List, List, List, List, List]:
    cw, tw, cb, tb, ctb = freeze_constraint_lists(
        control_whitelist, test_whitelist, control_blacklist, test_blacklist, control_test_blacklist
    )
    if len(tw) > n_test_grps:
        raise ValueError(
            f"test_whitelist has {len(tw)} units but only {n_test_grps} test group(s)."
        )
    overlap = set(cw) & set(tw)
    if overlap:
        raise ValueError(f"Units on both control and test whitelist: {sorted(overlap)}")
    bl_overlap = set(cb) & set(tb)
    if bl_overlap:
        raise ValueError(f"Units on both control and test blacklist: {sorted(bl_overlap)}")
    wl_bl = (set(cw) & set(cb)) | (set(tw) & set(tb)) | (set(cw) & set(ctb)) | (set(tw) & set(ctb))
    if wl_bl:
        raise ValueError(f"Unit on both whitelist and blacklist: {sorted(wl_bl)}")
    return cw, tw, cb, tb, ctb


def prepare_constraint_context(
    wide_data: pd.DataFrame,
    treatment_probability: float,
    n_test_grps: int,
    control_whitelist: Optional[List] = None,
    test_whitelist: Optional[List] = None,
    control_blacklist: Optional[List] = None,
    test_blacklist: Optional[List] = None,
    control_test_blacklist: Optional[List] = None,
) -> ConstraintContext:
    """Resolve pinned units and feasible pool; fail if constraints are impossible."""
    cw, tw, cb, tb, ctb = _normalize_lists(
        control_whitelist,
        test_whitelist,
        control_blacklist,
        test_blacklist,
        control_test_blacklist,
        n_test_grps,
    )
    all_units = [str(u) for u in wide_data.index.tolist()]
    unit_set = set(all_units)

    for label, units in (
        ("control_whitelist", cw),
        ("test_whitelist", tw),
        ("control_blacklist", cb),
        ("test_blacklist", tb),
        ("control_test_blacklist", ctb),
    ):
        unknown = set(units) - unit_set
        if unknown:
            raise ValueError(f"{label} references unknown units: {sorted(unknown)}")

    excluded = set(ctb) | set(cb) | set(tb)
    pinned_control = [u for u in cw if u not in excluded]
    pinned_test: Dict[str, List[Unit]] = {f"test_{i}": [] for i in range(n_test_grps)}
    for i, u in enumerate(tw):
        if u not in excluded:
            pinned_test[f"test_{i}"].append(u)

    pinned_all = set(pinned_control) | set().union(*pinned_test.values())
    if pinned_all & excluded:
        raise ValueError("Whitelisted unit is also excluded via blacklist.")

    for u in pinned_control:
        if u in tb:
            raise ValueError(f"control_whitelist unit {u!r} is on test_blacklist.")
    for grp, units in pinned_test.items():
        for u in units:
            if u in cb:
                raise ValueError(f"test_whitelist unit {u!r} is on control_blacklist.")

    assignable = [u for u in all_units if u not in excluded]
    if len(assignable) < max(2, 1 + n_test_grps):
        raise ValueError(
            "Too many units excluded via blacklist; not enough geos remain assignable."
        )

    free_units = [
        u
        for u in all_units
        if u not in excluded and u not in pinned_all and u not in cb and u not in tb
    ]

    n_pinned_test = sum(len(v) for v in pinned_test.values())
    if len(pinned_control) + n_pinned_test > len(assignable):
        raise ValueError(
            "Whitelisted units exceed assignable pool after blacklist exclusions."
        )
    max_treated_units = max(0, floor(treatment_probability * len(assignable)))
    if n_pinned_test > max_treated_units:
        raise ValueError(
            f"test_whitelist pins {n_pinned_test} unit(s) but at most "
            f"{max_treated_units} can be treated at treatment_probability="
            f"{treatment_probability}."
        )
    max_control_units = len(assignable) - n_pinned_test
    if len(pinned_control) > max_control_units:
        raise ValueError(
            f"control_whitelist pins {len(pinned_control)} unit(s) but at most "
            f"{max_control_units} can be in control given test whitelist pins."
        )

    if len(pinned_control) == 0 and len(free_units) == 0:
        raise ValueError("No units available for control after constraints.")
    if n_pinned_test == 0 and n_test_grps > 0 and len(free_units) == 0:
        raise ValueError("Not enough free units to populate test groups after constraints.")

    return ConstraintContext(
        all_units=all_units,
        excluded=excluded,
        pinned_control=pinned_control,
        pinned_test=pinned_test,
        free_units=free_units,
        n_test_grps=n_test_grps,
        treatment_probability=treatment_probability,
    )


def validate_assignment_dict(
    assignment: Dict[str, List],
    ctx: ConstraintContext,
    control_whitelist: Optional[List] = None,
    test_whitelist: Optional[List] = None,
    control_blacklist: Optional[List] = None,
    test_blacklist: Optional[List] = None,
    control_test_blacklist: Optional[List] = None,
) -> None:
    """Raise ValueError if assignment violates constraints."""
    cw, tw, cb, tb, ctb = _normalize_lists(
        control_whitelist,
        test_whitelist,
        control_blacklist,
        test_blacklist,
        control_test_blacklist,
        ctx.n_test_grps,
    )
    control = [str(u) for u in assignment.get("control", [])]
    test_keys = [f"test_{i}" for i in range(ctx.n_test_grps)]
    tests = {k: [str(u) for u in assignment.get(k, [])] for k in test_keys}

    unit_set = set(ctx.all_units)
    assigned = set()
    for u in control:
        if u not in unit_set:
            raise ValueError(f"Assigned unknown unit {u!r} in control.")
        if u in assigned:
            raise ValueError(f"Duplicate assignment for unit {u!r}.")
        assigned.add(u)
    for k in test_keys:
        for u in tests[k]:
            if u not in unit_set:
                raise ValueError(f"Assigned unknown unit {u!r} in {k}.")
            if u in assigned:
                raise ValueError(f"Unit assigned to control and {k}: {u}")
            assigned.add(u)

    for u in ctb:
        if u in assigned:
            raise ValueError(f"Excluded unit {u!r} was assigned.")
    for u in cb:
        if u in control:
            raise ValueError(f"control_blacklist unit {u!r} in control.")
    for u in tb:
        for k in test_keys:
            if u in tests[k]:
                raise ValueError(f"test_blacklist unit {u!r} in {k}.")
    for u in cw:
        if u not in control:
            raise ValueError(f"control_whitelist unit {u!r} not in control.")
    for i, u in enumerate(tw):
        if u not in tests[f"test_{i}"]:
            raise ValueError(f"test_whitelist unit {u!r} not in test_{i}.")


def balanced_volume_assign(
    wide_data: pd.DataFrame,
    ctx: ConstraintContext,
    rng: np.random.Generator,
) -> Dict[str, List]:
    """
    Volume-balancing heuristic (formerly mislabeled complete randomization).

    Greedily assigns free units to the group furthest below KPI volume target.
    """
    control_group = list(ctx.pinned_control)
    test_groups = {f"test_{i}": list(ctx.pinned_test[f"test_{i}"]) for i in range(ctx.n_test_grps)}

    total_volume = float(wide_data.sum().sum())
    if total_volume <= 0:
        raise ValueError("Total KPI volume must be positive for balanced assignment.")

    group_shares = {"control": 0.0}
    for i in range(ctx.n_test_grps):
        key = f"test_{i}"
        group_shares[key] = sum(
            float(wide_data.loc[u].sum()) / total_volume for u in test_groups[key]
        )
    group_shares["control"] = sum(
        float(wide_data.loc[u].sum()) / total_volume for u in control_group
    )

    target_shares = {
        "control": 1.0 - ctx.treatment_probability,
        **{
            f"test_{i}": ctx.treatment_probability / ctx.n_test_grps
            for i in range(ctx.n_test_grps)
        },
    }

    free_units = list(ctx.free_units)
    rng.shuffle(free_units)

    for unit in free_units:
        unit_share = float(wide_data.loc[unit].sum()) / total_volume
        share_gaps = {g: target_shares[g] - group_shares[g] for g in target_shares}
        best_group = max(share_gaps, key=share_gaps.get)
        if best_group == "control":
            control_group.append(unit)
        else:
            test_groups[best_group].append(unit)
        group_shares[best_group] += unit_share

    return freeze_assignment({"control": control_group, **test_groups})


def bernoulli_complete_assign(
    wide_data: pd.DataFrame,
    ctx: ConstraintContext,
    rng: np.random.Generator,
) -> Dict[str, List]:
    """True complete randomization: random assignment of free units with constraint pins."""
    control_group = list(ctx.pinned_control)
    test_groups = {f"test_{i}": list(ctx.pinned_test[f"test_{i}"]) for i in range(ctx.n_test_grps)}

    free = list(ctx.free_units)
    rng.shuffle(free)

    n_free = len(free)
    if n_free == 0:
        return freeze_assignment({"control": control_group, **test_groups})

    n_pinned_test = sum(len(test_groups[f"test_{i}"]) for i in range(ctx.n_test_grps))
    total_units_after = len(control_group) + n_pinned_test + n_free
    target_treated = floor(ctx.treatment_probability * total_units_after) - n_pinned_test
    target_treated = max(0, min(target_treated, n_free))

    treated_free = list(rng.choice(free, size=target_treated, replace=False)) if target_treated else []
    remaining_free = [u for u in free if u not in treated_free]

    for i, u in enumerate(treated_free):
        test_groups[f"test_{i % ctx.n_test_grps}"].append(u)

    control_group.extend(remaining_free)
    return freeze_assignment({"control": control_group, **test_groups})
