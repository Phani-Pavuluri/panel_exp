"""MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001 — governed multi-treated placebo evaluation.

Leave-one-treated-out over observed treated units is not multi-treated placebo inference.
It is a treated-unit sensitivity diagnostic. Multi-treated placebo requires replacing
the full treated set with pseudo-treated sets generated under the original assignment
design or a declared falsification design.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from panel_exp.design.assignment_generators import (
    AssignmentDesignSpec,
    AssignmentFamily,
    AssignmentRole,
    PseudoAssignment,
    ValidityStatus,
    generate_pseudo_assignments,
)


class PlaceboSemanticRole(str, Enum):
    DESIGN_BASED_RANDOMIZATION_CANDIDATE = "design_based_randomization_candidate"
    FALSIFICATION_DIAGNOSTIC = "falsification_diagnostic"
    BLOCKED = "blocked"


class PlaceboDecision(str, Enum):
    PLACEBO_FRAMEWORK_SUPPORTED = "placebo_framework_supported"
    PLACEBO_FRAMEWORK_FALSIFICATION_ONLY = "placebo_framework_falsification_only"
    PLACEBO_FRAMEWORK_BLOCKED = "placebo_framework_blocked"
    LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO = "leave_one_treated_out_rejected_as_placebo"
    TOO_FEW_VALID_PSEUDO_ASSIGNMENTS = "too_few_valid_pseudo_assignments"
    UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED = "unknown_assignment_design_blocked"
    MULTICELL_GLOBAL_CLAIM_BLOCKED = "multicell_global_claim_blocked"


class TestStatisticKind(str, Enum):
    ABSOLUTE_EFFECT = "absolute_effect"
    RELATIVE_EFFECT = "relative_effect"
    STUDENTIZED_EFFECT = "studentized_effect"
    SIGNED_EFFECT = "signed_effect"
    RANK_STATISTIC = "rank_statistic"


FALSIFICATION_WARNING = (
    "Pseudo-assignments are falsification-only because the original assignment mechanism "
    "is deterministic, design-search-based, or not known to be randomized."
)

LOTO_REJECTION_MESSAGE = (
    "Leave-one-treated-out is retained as sensitivity analysis only and cannot substitute "
    "for full treated-set placebo."
)


@dataclass(frozen=True)
class TreatedSetPlaceboSpec:
    design_spec: AssignmentDesignSpec
    observed_statistic: float
    pseudo_statistic_by_assignment: Mapping[str, float] | None = None
    statistic_kind: TestStatisticKind = TestStatisticKind.SIGNED_EFFECT
    effect_direction: str = "two_sided"
    minimum_valid_placebo_sets: int = 20
    requested_semantic_role: PlaceboSemanticRole | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class TreatedSetPlaceboResult:
    decision: PlaceboDecision
    semantic_role: PlaceboSemanticRole
    observed_statistic: float
    pseudo_statistics: tuple[float, ...]
    placebo_rank: int | None
    empirical_tail_fraction: float | None
    num_valid_placebo_sets: int
    minimum_valid_placebo_sets: int
    assignment_role_counts: Mapping[str, int]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    metadata: Mapping[str, Any]


def _meta(spec: TreatedSetPlaceboSpec) -> dict[str, Any]:
    return dict(spec.metadata or {})


def _blocked_result(
    spec: TreatedSetPlaceboSpec,
    *,
    decision: PlaceboDecision,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> TreatedSetPlaceboResult:
    return TreatedSetPlaceboResult(
        decision=decision,
        semantic_role=PlaceboSemanticRole.BLOCKED,
        observed_statistic=spec.observed_statistic,
        pseudo_statistics=(),
        placebo_rank=None,
        empirical_tail_fraction=None,
        num_valid_placebo_sets=0,
        minimum_valid_placebo_sets=spec.minimum_valid_placebo_sets,
        assignment_role_counts={},
        blocked_reasons=reasons,
        warnings=warnings,
        metadata=dict(metadata or _meta(spec)),
    )


def reject_leave_one_treated_out_as_placebo(
    spec: TreatedSetPlaceboSpec,
    *,
    reason: str | None = None,
) -> TreatedSetPlaceboResult:
    """Reject leave-one-treated-out as a substitute for full treated-set placebo."""
    msg = reason or LOTO_REJECTION_MESSAGE
    return _blocked_result(
        spec,
        decision=PlaceboDecision.LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO,
        reasons=(msg,),
        warnings=("framework_only_not_production_inference",),
    )


def classify_placebo_semantics(assignments: Sequence[PseudoAssignment]) -> PlaceboSemanticRole:
    """Classify placebo semantic role from generated pseudo-assignments."""
    if not assignments:
        return PlaceboSemanticRole.BLOCKED
    roles = {a.role for a in assignments}
    if AssignmentRole.BLOCKED in roles:
        return PlaceboSemanticRole.BLOCKED
    if roles == {AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE}:
        return PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    if AssignmentRole.FALSIFICATION_ONLY in roles:
        return PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    if AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE in roles:
        return PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    return PlaceboSemanticRole.BLOCKED


def compute_placebo_rank(
    observed: float,
    pseudo_stats: Sequence[float],
    effect_direction: str,
) -> tuple[int | None, float | None]:
    """Compute inclusive placebo rank and empirical tail fraction (framework-only)."""
    if not pseudo_stats:
        return None, None
    direction = effect_direction.lower()
    if direction == "greater":
        rank = sum(1 for p in pseudo_stats if p >= observed)
    elif direction == "less":
        rank = sum(1 for p in pseudo_stats if p <= observed)
    else:
        rank = sum(1 for p in pseudo_stats if abs(p) >= abs(observed))
    return rank, rank / len(pseudo_stats)


def _role_counts(assignments: Sequence[PseudoAssignment]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in assignments:
        counts[a.role.value] = counts.get(a.role.value, 0) + 1
    return counts


def _check_platform_blocks(spec: TreatedSetPlaceboSpec) -> TreatedSetPlaceboResult | None:
    meta = _meta(spec)
    if meta.get("leave_one_treated_out_requested"):
        return reject_leave_one_treated_out_as_placebo(spec)
    if meta.get("multicell_global_claim_requested"):
        return _blocked_result(
            spec,
            decision=PlaceboDecision.MULTICELL_GLOBAL_CLAIM_BLOCKED,
            reasons=("multicell global/winner/pooled claims are not supported by treated-set placebo framework",),
        )
    blocked_flags = (
        ("trustreport_authorization_requested", "TrustReport authorization is not supported"),
        ("calibration_signal_requested", "CalibrationSignal export is not supported"),
        ("production_decisioning_requested", "production decisioning is not supported"),
        ("budget_optimization_requested", "budget optimization is not supported"),
        ("live_api_requested", "live API authorization is not supported"),
        ("scheduler_requested", "scheduler authorization is not supported"),
    )
    for key, msg in blocked_flags:
        if meta.get(key):
            return _blocked_result(
                spec,
                decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
                reasons=(msg,),
            )
    return None


def _valid_assignments(
    assignments: Sequence[PseudoAssignment],
) -> list[PseudoAssignment]:
    return [
        a
        for a in assignments
        if a.validity_status != ValidityStatus.ASSIGNMENT_GENERATION_INVALID.value
        and a.role != AssignmentRole.BLOCKED
    ]


def evaluate_treated_set_placebo(spec: TreatedSetPlaceboSpec) -> TreatedSetPlaceboResult:
    """Evaluate observed treated-set statistic against design-valid pseudo-treated sets."""
    platform_block = _check_platform_blocks(spec)
    if platform_block is not None:
        return platform_block

    if spec.design_spec.family == AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED:
        return _blocked_result(
            spec,
            decision=PlaceboDecision.UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED,
            reasons=("UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED",),
        )

    if (
        spec.requested_semantic_role == PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
        and spec.design_spec.family
        in {
            AssignmentFamily.GREEDY_MATCHED_MARKET_FALSIFICATION,
            AssignmentFamily.KERNEL_THINNING_FALSIFICATION,
            AssignmentFamily.FIXED_DETERMINISTIC_FALSIFICATION,
        }
    ):
        return _blocked_result(
            spec,
            decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
            reasons=("invalid requested semantic role for falsification-only design family",),
        )

    design = replace(
        spec.design_spec,
        min_assignments=spec.minimum_valid_placebo_sets,
    )
    assignments = generate_pseudo_assignments(design)
    valid = _valid_assignments(assignments)
    role_counts = _role_counts(valid)
    semantic_role = classify_placebo_semantics(valid)

    if not valid:
        if spec.design_spec.family == AssignmentFamily.UNKNOWN_ASSIGNMENT_BLOCKED:
            decision = PlaceboDecision.UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED
        else:
            decision = PlaceboDecision.TOO_FEW_VALID_PSEUDO_ASSIGNMENTS
        return _blocked_result(
            spec,
            decision=decision,
            reasons=("no valid pseudo-treated assignments generated",),
            metadata={"assignment_role_counts": role_counts},
        )

    if len(valid) < spec.minimum_valid_placebo_sets:
        return _blocked_result(
            spec,
            decision=PlaceboDecision.TOO_FEW_VALID_PSEUDO_ASSIGNMENTS,
            reasons=(
                f"valid placebo sets {len(valid)} < minimum {spec.minimum_valid_placebo_sets}",
            ),
            metadata={"assignment_role_counts": role_counts},
        )

    stats_map = spec.pseudo_statistic_by_assignment or {}
    pseudo_stats: list[float] = []
    missing_ids: list[str] = []
    for assignment in valid:
        if assignment.assignment_id not in stats_map:
            missing_ids.append(assignment.assignment_id)
            continue
        pseudo_stats.append(float(stats_map[assignment.assignment_id]))

    strict_missing = _meta(spec).get("strict_missing_stats", True)
    if missing_ids:
        if strict_missing:
            return _blocked_result(
                spec,
                decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
                reasons=(f"missing pseudo statistics for assignments: {', '.join(missing_ids[:3])}",),
                metadata={"assignment_role_counts": role_counts, "missing_count": len(missing_ids)},
            )
        warnings = (f"missing pseudo statistics for {len(missing_ids)} assignments",)
    else:
        warnings = ()

    extra_ids = set(stats_map) - {a.assignment_id for a in valid}
    if extra_ids:
        return _blocked_result(
            spec,
            decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
            reasons=("pseudo statistic assignment_id mismatch",),
            metadata={"extra_assignment_ids": sorted(extra_ids)},
        )

    if not pseudo_stats:
        return _blocked_result(
            spec,
            decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
            reasons=("no pseudo statistics available after alignment",),
        )

    rank, tail = compute_placebo_rank(
        spec.observed_statistic,
        pseudo_stats,
        spec.effect_direction,
    )

    result_warnings: list[str] = list(warnings)
    if semantic_role == PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE:
        decision = PlaceboDecision.PLACEBO_FRAMEWORK_SUPPORTED
        result_warnings.append("empirical_tail_fraction_is_framework_only_not_production_p_value")
    elif semantic_role == PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC:
        decision = PlaceboDecision.PLACEBO_FRAMEWORK_FALSIFICATION_ONLY
        result_warnings.append(FALSIFICATION_WARNING)
        result_warnings.append("empirical_tail_fraction_is_framework_only_not_production_p_value")
    else:
        return _blocked_result(
            spec,
            decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
            reasons=("unable to classify placebo semantics for generated assignments",),
            metadata={"assignment_role_counts": role_counts},
        )

    if (
        spec.requested_semantic_role == PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
        and semantic_role != PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    ):
        return _blocked_result(
            spec,
            decision=PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
            reasons=("requested design-based semantic role not satisfied by generated assignments",),
            metadata={"assignment_role_counts": role_counts},
        )

    return TreatedSetPlaceboResult(
        decision=decision,
        semantic_role=semantic_role,
        observed_statistic=spec.observed_statistic,
        pseudo_statistics=tuple(pseudo_stats),
        placebo_rank=rank,
        empirical_tail_fraction=tail,
        num_valid_placebo_sets=len(pseudo_stats),
        minimum_valid_placebo_sets=spec.minimum_valid_placebo_sets,
        assignment_role_counts=role_counts,
        blocked_reasons=(),
        warnings=tuple(result_warnings),
        metadata={
            **_meta(spec),
            "statistic_kind": spec.statistic_kind.value,
            "effect_direction": spec.effect_direction,
            "framework_tail_fraction_label": "not_production_p_value",
        },
    )


def summarize_treated_set_placebo_result(result: TreatedSetPlaceboResult) -> dict[str, Any]:
    """Serialize a treated-set placebo result for validation archives."""
    return {
        "decision": result.decision.value,
        "semantic_role": result.semantic_role.value,
        "observed_statistic": result.observed_statistic,
        "pseudo_statistics_count": len(result.pseudo_statistics),
        "placebo_rank": result.placebo_rank,
        "empirical_tail_fraction": result.empirical_tail_fraction,
        "num_valid_placebo_sets": result.num_valid_placebo_sets,
        "minimum_valid_placebo_sets": result.minimum_valid_placebo_sets,
        "assignment_role_counts": dict(result.assignment_role_counts),
        "blocked_reasons": list(result.blocked_reasons),
        "warnings": list(result.warnings),
        "metadata": dict(result.metadata),
    }


__all__ = [
    "LOTO_REJECTION_MESSAGE",
    "PlaceboDecision",
    "PlaceboSemanticRole",
    "TestStatisticKind",
    "TreatedSetPlaceboResult",
    "TreatedSetPlaceboSpec",
    "classify_placebo_semantics",
    "compute_placebo_rank",
    "evaluate_treated_set_placebo",
    "reject_leave_one_treated_out_as_placebo",
    "summarize_treated_set_placebo_result",
]
