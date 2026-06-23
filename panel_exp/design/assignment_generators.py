"""DESIGN-AWARE-ASSIGNMENT-GENERATORS-001 — governed pseudo-assignment generation.

Design-aware pseudo-assignment generation is a prerequisite for treated-set placebo,
permutation, and randomization-style inference. A pseudo-assignment that ignores the
original design can produce misleading null distributions and invalid p-values.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence


class AssignmentFamily(str, Enum):
    COMPLETE_RANDOMIZED_SET = "complete_randomized_set"
    MATCHED_PAIR_RANDOMIZED = "matched_pair_randomized"
    MATCHED_BLOCK_RANDOMIZED = "matched_block_randomized"
    STRATIFIED_RANDOMIZED = "stratified_randomized"
    RERANDOMIZED_DESIGN_CANDIDATE = "rerandomized_design_candidate"
    GREEDY_MATCHED_MARKET_FALSIFICATION = "greedy_matched_market_falsification"
    KERNEL_THINNING_FALSIFICATION = "kernel_thinning_falsification"
    FIXED_DETERMINISTIC_FALSIFICATION = "fixed_deterministic_falsification"
    UNKNOWN_ASSIGNMENT_BLOCKED = "unknown_assignment_blocked"


class AssignmentRole(str, Enum):
    DESIGN_BASED_RANDOMIZATION_CANDIDATE = "design_based_randomization_candidate"
    FALSIFICATION_ONLY = "falsification_only"
    BLOCKED = "blocked"


class ValidityStatus(str, Enum):
    ASSIGNMENT_GENERATION_SUPPORTED = "ASSIGNMENT_GENERATION_SUPPORTED"
    ASSIGNMENT_GENERATION_FALSIFICATION_ONLY = "ASSIGNMENT_GENERATION_FALSIFICATION_ONLY"
    ASSIGNMENT_GENERATION_BLOCKED_UNKNOWN_DESIGN = "ASSIGNMENT_GENERATION_BLOCKED_UNKNOWN_DESIGN"
    ASSIGNMENT_GENERATION_BLOCKED_INSUFFICIENT_UNITS = "ASSIGNMENT_GENERATION_BLOCKED_INSUFFICIENT_UNITS"
    ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_BLOCKS = "ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_BLOCKS"
    ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_PAIRS = "ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_PAIRS"
    ASSIGNMENT_GENERATION_BLOCKED_CONSTRAINT_VIOLATION = "ASSIGNMENT_GENERATION_BLOCKED_CONSTRAINT_VIOLATION"
    ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS = (
        "ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS"
    )
    ASSIGNMENT_GENERATION_DOWNGRADED_TO_FALSIFICATION_ONLY = (
        "ASSIGNMENT_GENERATION_DOWNGRADED_TO_FALSIFICATION_ONLY"
    )
    ASSIGNMENT_GENERATION_INVALID = "ASSIGNMENT_GENERATION_INVALID"


@dataclass(frozen=True)
class AssignmentUnit:
    unit_id: str
    block_id: str | None = None
    stratum_id: str | None = None
    pair_id: str | None = None
    eligible: bool = True
    excluded: bool = False
    covariates: Mapping[str, float] | None = None


@dataclass(frozen=True)
class AssignmentDesignSpec:
    family: AssignmentFamily
    units: Sequence[AssignmentUnit]
    observed_treated_unit_ids: Sequence[str]
    constraints: Mapping[str, Any] | None = None
    seed: int = 0
    max_assignments: int = 1000
    min_assignments: int = 20


@dataclass(frozen=True)
class PseudoAssignment:
    assignment_id: str
    pseudo_treated_unit_ids: tuple[str, ...]
    pseudo_control_unit_ids: tuple[str, ...]
    family: AssignmentFamily
    role: AssignmentRole
    validity_status: str
    validity_reasons: tuple[str, ...]
    metadata: Mapping[str, Any]


def _constraints(spec: AssignmentDesignSpec) -> dict[str, Any]:
    return dict(spec.constraints or {})


def _eligible_units(spec: AssignmentDesignSpec) -> list[AssignmentUnit]:
    return [u for u in spec.units if u.eligible and not u.excluded]


def _all_unit_ids(spec: AssignmentDesignSpec) -> set[str]:
    return {u.unit_id for u in spec.units}


def _treated_set_size(spec: AssignmentDesignSpec) -> int:
    return len(tuple(spec.observed_treated_unit_ids))


def _rng(spec: AssignmentDesignSpec) -> random.Random:
    return random.Random(spec.seed)


def _sample_combos(
    combos: Sequence[tuple[str, ...]],
    *,
    rng: random.Random,
    max_assignments: int,
) -> list[tuple[str, ...]]:
    if not combos:
        return []
    if len(combos) <= max_assignments:
        ordered = list(combos)
        rng.shuffle(ordered)
        return ordered
    indices = rng.sample(range(len(combos)), max_assignments)
    return [combos[i] for i in sorted(indices)]


def _build_assignment(
    spec: AssignmentDesignSpec,
    *,
    assignment_index: int,
    treated_ids: Sequence[str],
    role: AssignmentRole,
    validity_status: str,
    validity_reasons: tuple[str, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> PseudoAssignment:
    treated = tuple(sorted(treated_ids))
    eligible_ids = {u.unit_id for u in _eligible_units(spec)}
    control = tuple(sorted(eligible_ids - set(treated)))
    return PseudoAssignment(
        assignment_id=f"{spec.family.value}:{spec.seed}:{assignment_index}",
        pseudo_treated_unit_ids=treated,
        pseudo_control_unit_ids=control,
        family=spec.family,
        role=role,
        validity_status=validity_status,
        validity_reasons=validity_reasons,
        metadata=dict(metadata or {}),
    )


def _blocked_result(
    spec: AssignmentDesignSpec,
    *,
    status: ValidityStatus,
    reason: str,
) -> list[PseudoAssignment]:
    return []


def _generate_complete_randomized(spec: AssignmentDesignSpec) -> list[PseudoAssignment]:
    eligible = _eligible_units(spec)
    k = _treated_set_size(spec)
    if k == 0:
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_INSUFFICIENT_UNITS,
            reason="zero treated-set size",
        )
    if k > len(eligible):
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_INSUFFICIENT_UNITS,
            reason="treated-set size exceeds eligible units",
        )
    eligible_ids = [u.unit_id for u in eligible]
    combos = list(itertools.combinations(eligible_ids, k))
    if len(combos) < spec.min_assignments:
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS,
            reason=f"valid assignment count {len(combos)} < min_assignments {spec.min_assignments}",
        )
    rng = _rng(spec)
    selected = _sample_combos(combos, rng=rng, max_assignments=spec.max_assignments)
    return [
        _build_assignment(
            spec,
            assignment_index=i,
            treated_ids=combo,
            role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
            validity_status=ValidityStatus.ASSIGNMENT_GENERATION_SUPPORTED.value,
        )
        for i, combo in enumerate(selected)
    ]


def _group_by(
    units: Sequence[AssignmentUnit],
    key: str,
) -> dict[str, list[AssignmentUnit]]:
    groups: dict[str, list[AssignmentUnit]] = {}
    for unit in units:
        group_key = getattr(unit, key)
        if group_key is None:
            continue
        groups.setdefault(str(group_key), []).append(unit)
    return groups


def _count_treated_in_group(
    units: Sequence[AssignmentUnit],
    observed_treated: set[str],
) -> int:
    return sum(1 for u in units if u.unit_id in observed_treated)


def _combinations_per_group(
    units: Sequence[AssignmentUnit],
    treated_count: int,
) -> list[tuple[str, ...]]:
    eligible_ids = [u.unit_id for u in units if u.eligible and not u.excluded]
    if treated_count > len(eligible_ids):
        return []
    if treated_count == 0:
        return [tuple()]
    return list(itertools.combinations(eligible_ids, treated_count))


def _cartesian_assignments(group_combos: list[list[tuple[str, ...]]]) -> list[tuple[str, ...]]:
    if not group_combos:
        return []
    if any(not combos for combos in group_combos):
        return []
    merged: list[tuple[str, ...]] = [tuple()]
    for combos in group_combos:
        merged = [a + b for a in merged for b in combos]
    return merged


def _generate_grouped_randomized(
    spec: AssignmentDesignSpec,
    *,
    group_key: str,
    malformed_status: ValidityStatus,
) -> list[PseudoAssignment]:
    observed_treated = set(spec.observed_treated_unit_ids)
    all_units = list(spec.units)
    groups = _group_by(all_units, group_key)
    if not groups:
        return _blocked_result(
            spec,
            status=malformed_status,
            reason=f"missing {group_key} metadata",
        )

    units_with_key = [u for u in all_units if getattr(u, group_key) is not None]
    if len(units_with_key) != sum(len(v) for v in groups.values()):
        return _blocked_result(
            spec,
            status=malformed_status,
            reason=f"duplicate or inconsistent {group_key} membership",
        )

    group_combos: list[list[tuple[str, ...]]] = []
    for group_id, group_units in sorted(groups.items()):
        if group_key == "pair_id" and len(group_units) != 2:
            return _blocked_result(
                spec,
                status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_PAIRS,
                reason=f"pair {group_id} does not contain exactly two units",
            )
        treated_count = _count_treated_in_group(group_units, observed_treated)
        if group_key == "pair_id" and treated_count != 1:
            return _blocked_result(
                spec,
                status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_PAIRS,
                reason=f"pair {group_id} observed treated count is {treated_count}, expected 1",
            )
        combos = _combinations_per_group(group_units, treated_count)
        if not combos:
            status = (
                ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_PAIRS
                if group_key == "pair_id"
                else ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_BLOCKS
            )
            return _blocked_result(
                spec,
                status=status,
                reason=f"group {group_id} cannot produce valid assignments",
            )
        else:
            group_combos.append(list(combos))

    if group_key == "pair_id":
        full_combos = _cartesian_assignments(group_combos)
    else:
        full_combos = _cartesian_assignments(group_combos)

    if len(full_combos) < spec.min_assignments:
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS,
            reason=f"valid assignment count {len(full_combos)} < min_assignments {spec.min_assignments}",
        )

    rng = _rng(spec)
    selected = _sample_combos(full_combos, rng=rng, max_assignments=spec.max_assignments)
    return [
        _build_assignment(
            spec,
            assignment_index=i,
            treated_ids=combo,
            role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
            validity_status=ValidityStatus.ASSIGNMENT_GENERATION_SUPPORTED.value,
            metadata={group_key: "preserved"},
        )
        for i, combo in enumerate(selected)
    ]


def _balance_imbalance(
    treated_ids: Sequence[str],
    units_by_id: dict[str, AssignmentUnit],
    balance_key: str,
) -> float:
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for uid in treated_ids:
        unit = units_by_id[uid]
        cov = unit.covariates or {}
        if balance_key not in cov:
            return float("inf")
        val = float(cov[balance_key])
        totals[balance_key] = totals.get(balance_key, 0.0) + val
        counts[balance_key] = counts.get(balance_key, 0) + 1
    if not counts:
        return float("inf")
    mean = totals[balance_key] / counts[balance_key]
    return abs(mean)


def _generate_rerandomized(spec: AssignmentDesignSpec) -> list[PseudoAssignment]:
    constraints = _constraints(spec)
    acceptance_rule = constraints.get("rerandomization_acceptance_rule")
    balance_key = constraints.get("balance_key")
    max_imbalance = constraints.get("max_imbalance")

    base = _generate_complete_randomized(
        replace(spec, min_assignments=1, max_assignments=spec.max_assignments * 10)
    )
    if not base:
        return []

    if not acceptance_rule and not (balance_key and max_imbalance is not None):
        return [
            replace(
                a,
                role=AssignmentRole.FALSIFICATION_ONLY,
                validity_status=ValidityStatus.ASSIGNMENT_GENERATION_DOWNGRADED_TO_FALSIFICATION_ONLY.value,
                validity_reasons=(
                    "rerandomization acceptance rule unavailable; falsification only",
                ),
            )
            for a in base[: spec.max_assignments]
        ]

    units_by_id = {u.unit_id: u for u in spec.units}
    filtered: list[PseudoAssignment] = []
    for assignment in base:
        if balance_key and max_imbalance is not None:
            imbalance = _balance_imbalance(
                assignment.pseudo_treated_unit_ids,
                units_by_id,
                str(balance_key),
            )
            if imbalance > float(max_imbalance):
                continue
        filtered.append(assignment)

    if len(filtered) < spec.min_assignments:
        return [
            replace(
                a,
                role=AssignmentRole.FALSIFICATION_ONLY,
                validity_status=ValidityStatus.ASSIGNMENT_GENERATION_DOWNGRADED_TO_FALSIFICATION_ONLY.value,
                validity_reasons=("balance filter yielded too few assignments; falsification only",),
            )
            for a in base[: min(spec.max_assignments, len(base))]
        ]

    return [
        replace(
            a,
            role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
            validity_status=ValidityStatus.ASSIGNMENT_GENERATION_SUPPORTED.value,
            validity_reasons=(),
            metadata={**dict(a.metadata), "rerandomization_filtered": True},
        )
        for a in filtered[: spec.max_assignments]
    ]


def _generate_falsification_only(spec: AssignmentDesignSpec) -> list[PseudoAssignment]:
    eligible = _eligible_units(spec)
    k = _treated_set_size(spec)
    if k == 0 or k > len(eligible):
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_INSUFFICIENT_UNITS,
            reason="insufficient eligible units for falsification pseudo-set",
        )
    eligible_ids = [u.unit_id for u in eligible]
    combos = list(itertools.combinations(eligible_ids, k))
    if not combos:
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS,
            reason="no falsification pseudo-assignments available",
        )
    rng = _rng(spec)
    selected = _sample_combos(combos, rng=rng, max_assignments=spec.max_assignments)
    if len(combos) < spec.min_assignments:
        return _blocked_result(
            spec,
            status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_TOO_FEW_VALID_ASSIGNMENTS,
            reason="too few falsification assignments",
        )
    return [
        _build_assignment(
            spec,
            assignment_index=i,
            treated_ids=combo,
            role=AssignmentRole.FALSIFICATION_ONLY,
            validity_status=ValidityStatus.ASSIGNMENT_GENERATION_FALSIFICATION_ONLY.value,
            validity_reasons=("deterministic or design-search family; falsification only",),
        )
        for i, combo in enumerate(selected[: spec.max_assignments])
    ]


def generate_pseudo_assignments(spec: AssignmentDesignSpec) -> list[PseudoAssignment]:
    """Generate deterministic pseudo-treated assignments for a design spec."""
    if spec.family == AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED:
        return []

    generators = {
        AssignmentFamily.COMPLETE_RANDOMIZED_SET: _generate_complete_randomized,
        AssignmentFamily.MATCHED_PAIR_RANDOMIZED: lambda s: _generate_grouped_randomized(
            s,
            group_key="pair_id",
            malformed_status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_PAIRS,
        ),
        AssignmentFamily.MATCHED_BLOCK_RANDOMIZED: lambda s: _generate_grouped_randomized(
            s,
            group_key="block_id",
            malformed_status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_BLOCKS,
        ),
        AssignmentFamily.STRATIFIED_RANDOMIZED: lambda s: _generate_grouped_randomized(
            s,
            group_key="stratum_id",
            malformed_status=ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_MALFORMED_BLOCKS,
        ),
        AssignmentFamily.RERANDOMIZED_DESIGN_CANDIDATE: _generate_rerandomized,
        AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION: _generate_falsification_only,
        AssignmentFamily.KERNEL_THINNING_FALSIFICATION: _generate_falsification_only,
        AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION: _generate_falsification_only,
    }
    generator = generators.get(spec.family)
    if generator is None:
        return []
    assignments = generator(spec)
    return [validate_pseudo_assignment(spec, a) for a in assignments]


def validate_pseudo_assignment(
    spec: AssignmentDesignSpec,
    assignment: PseudoAssignment,
) -> PseudoAssignment:
    """Validate invariants for one pseudo-assignment; return updated record."""
    reasons: list[str] = []
    treated = assignment.pseudo_treated_unit_ids
    control = assignment.pseudo_control_unit_ids
    all_ids = _all_unit_ids(spec)
    units_by_id = {u.unit_id: u for u in spec.units}
    expected_k = _treated_set_size(spec)

    if len(set(treated)) != len(treated):
        reasons.append("duplicate treated units")
    if set(treated) & set(control):
        reasons.append("treated/control overlap")
    if not set(treated).issubset(all_ids):
        reasons.append("treated unit not in design universe")
    for uid in treated:
        unit = units_by_id.get(uid)
        if unit is None:
            reasons.append(f"unknown treated unit {uid}")
            continue
        if not unit.eligible:
            reasons.append(f"ineligible treated unit {uid}")
        if unit.excluded:
            reasons.append(f"excluded treated unit {uid}")
    if expected_k and len(treated) != expected_k:
        reasons.append(f"treated-set size {len(treated)} != observed size {expected_k}")

    if spec.family == AssignmentFamily.MATCHED_PAIR_RANDOMIZED:
        pairs = _group_by(spec.units, "pair_id")
        for pair_id, pair_units in pairs.items():
            pair_treated = [uid for uid in treated if units_by_id[uid].pair_id == pair_id]
            if len(pair_treated) != 1:
                reasons.append(f"pair {pair_id} treated count {len(pair_treated)} != 1")

    if spec.family in {
        AssignmentFamily.MATCHED_BLOCK_RANDOMIZED,
        AssignmentFamily.STRATIFIED_RANDOMIZED,
    }:
        key = "block_id" if spec.family == AssignmentFamily.MATCHED_BLOCK_RANDOMIZED else "stratum_id"
        groups = _group_by(spec.units, key)
        observed = set(spec.observed_treated_unit_ids)
        for group_id, group_units in groups.items():
            expected = _count_treated_in_group(group_units, observed)
            actual = sum(1 for uid in treated if getattr(units_by_id[uid], key) == group_id)
            if actual != expected:
                reasons.append(f"{key} {group_id} treated count {actual} != {expected}")

    if assignment.role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE and spec.family in {
        AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION,
        AssignmentFamily.KERNEL_THINNING_FALSIFICATION,
        AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION,
    }:
        reasons.append("deterministic family cannot be design-based randomization candidate")

    if reasons:
        return replace(
            assignment,
            validity_status=ValidityStatus.ASSIGNMENT_GENERATION_INVALID.value,
            validity_reasons=tuple(reasons),
        )
    return assignment


def summarize_assignment_generation(
    spec: AssignmentDesignSpec,
    assignments: Sequence[PseudoAssignment],
) -> dict[str, Any]:
    """Summarize generation output for validation archives."""
    role_counts: dict[str, int] = {}
    decision_counts: dict[str, int] = {}
    for a in assignments:
        role_counts[a.role.value] = role_counts.get(a.role.value, 0) + 1
        decision_counts[a.validity_status] = decision_counts.get(a.validity_status, 0) + 1

    if spec.family == AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED:
        decision_counts[ValidityStatus.ASSIGNMENT_GENERATION_BLOCKED_UNKNOWN_DESIGN.value] = 1

    return {
        "family": spec.family.value,
        "seed": spec.seed,
        "assignment_count": len(assignments),
        "role_counts": role_counts,
        "decision_counts": decision_counts,
        "observed_treated_count": _treated_set_size(spec),
        "eligible_unit_count": len(_eligible_units(spec)),
        "deterministic_seed": spec.seed,
    }


__all__ = [
    "AssignmentDesignSpec",
    "AssignmentFamily",
    "AssignmentRole",
    "AssignmentUnit",
    "PseudoAssignment",
    "ValidityStatus",
    "generate_pseudo_assignments",
    "summarize_assignment_generation",
    "validate_pseudo_assignment",
]
