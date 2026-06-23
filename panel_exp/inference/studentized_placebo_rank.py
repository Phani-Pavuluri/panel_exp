"""STUDENTIZED_PLACEBO_RANK_INFERENCE_001 — governed studentized placebo-rank inference primitive.

Compares observed and pseudo-treated-set effects on a studentized scale when a valid
scale/standard-error/dispersion contract is available. Framework-level candidate /
diagnostic only — not production p-values or causal confidence intervals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from panel_exp.design.assignment_generators import AssignmentRole

CANDIDATE_WARNING = (
    "Framework-level studentized placebo-rank candidate only — empirical tail fraction "
    "is not a final production p-value and no causal confidence interval is authorized."
)

FALSIFICATION_WARNING = (
    "Not design-based causal inference — studentized placebo rank is diagnostic only; "
    "empirical tail fraction is not a final production p-value."
)

DESIGN_ROLE = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION_ROLE = AssignmentRole.FALSIFICATION_ONLY.value
BLOCKED_ROLE = AssignmentRole.BLOCKED.value


class StudentizedRankDecision(str, Enum):
    STUDENTIZED_RANK_CANDIDATE = "studentized_rank_candidate"
    STUDENTIZED_RANK_DIAGNOSTIC_ONLY = "studentized_rank_diagnostic_only"
    STUDENTIZED_RANK_BLOCKED = "studentized_rank_blocked"


class ScaleSource(str, Enum):
    PROVIDED_STANDARD_ERROR = "provided_standard_error"
    PROVIDED_STANDARD_DEVIATION = "provided_standard_deviation"
    PROVIDED_DISPERSION = "provided_dispersion"
    PLACEBO_DISPERSION = "placebo_dispersion"
    UNKNOWN = "unknown"


class ScaleValidity(str, Enum):
    VALID = "valid"
    MISSING_OBSERVED_SCALE = "missing_observed_scale"
    MISSING_PSEUDO_SCALE = "missing_pseudo_scale"
    NON_POSITIVE_SCALE = "non_positive_scale"
    NON_FINITE_SCALE = "non_finite_scale"
    MISMATCHED_SCALE_SOURCE = "mismatched_scale_source"
    INSUFFICIENT_PLACEBO_SETS = "insufficient_placebo_sets"
    BLOCKED = "blocked"


class StudentizedEffectDirection(str, Enum):
    GREATER = "greater"
    LESS = "less"
    TWO_SIDED = "two_sided"


@dataclass(frozen=True)
class StudentizedPlaceboRankSpec:
    observed_effect: float
    pseudo_effect_by_assignment: Mapping[str, float]
    observed_scale: float | None
    pseudo_scale_by_assignment: Mapping[str, float]
    effect_direction: StudentizedEffectDirection
    scale_source: ScaleSource
    null_value: float = 0.0
    assignment_role: str | None = None
    require_design_based_assignment: bool = True
    min_placebo_sets: int = 10
    requested_final_p_value: bool = False
    requested_causal_interval: bool = False
    requested_trustreport_authorization: bool = False
    requested_calibration_signal: bool = False
    requested_mmm_ingestion: bool = False
    requested_llm_decisioning: bool = False
    requested_production_decisioning: bool = False
    requested_live_api: bool = False
    requested_scheduler: bool = False
    requested_budget_optimization: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StudentizedPlaceboRankResult:
    decision: StudentizedRankDecision
    scale_validity: ScaleValidity
    observed_studentized_statistic: float | None
    pseudo_studentized_statistic_by_assignment: Mapping[str, float]
    placebo_rank: int | None
    empirical_tail_fraction: float | None
    num_placebo_sets: int
    is_candidate: bool
    is_diagnostic_only: bool
    is_blocked: bool
    warnings: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    governance_flags: Mapping[str, bool]


def _governance_flags() -> dict[str, bool]:
    return {
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "mmm_ingestion_allowed": False,
        "llm_decisioning_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
    }


def _is_finite(value: float | None) -> bool:
    if value is None:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _is_positive_finite(value: float | None) -> bool:
    return _is_finite(value) and float(value) > 0  # type: ignore[arg-type]


def _blocked_result(
    spec: StudentizedPlaceboRankSpec,
    *,
    validity: ScaleValidity,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    observed_studentized: float | None = None,
    pseudo_studentized: Mapping[str, float] | None = None,
    num_placebo_sets: int = 0,
) -> StudentizedPlaceboRankResult:
    return StudentizedPlaceboRankResult(
        decision=StudentizedRankDecision.STUDENTIZED_RANK_BLOCKED,
        scale_validity=validity,
        observed_studentized_statistic=observed_studentized,
        pseudo_studentized_statistic_by_assignment=dict(pseudo_studentized or {}),
        placebo_rank=None,
        empirical_tail_fraction=None,
        num_placebo_sets=num_placebo_sets,
        is_candidate=False,
        is_diagnostic_only=False,
        is_blocked=True,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def _platform_overclaim_block(
    spec: StudentizedPlaceboRankSpec,
) -> StudentizedPlaceboRankResult | None:
    checks: list[tuple[bool, str]] = [
        (spec.requested_final_p_value, "final production p-value semantics are blocked"),
        (spec.requested_causal_interval, "causal confidence interval semantics are blocked"),
        (spec.requested_trustreport_authorization, "TrustReport authorization is not supported"),
        (spec.requested_calibration_signal, "CalibrationSignal export is not supported"),
        (spec.requested_mmm_ingestion, "MMM ingestion is not supported"),
        (spec.requested_llm_decisioning, "LLM decisioning is not supported"),
        (spec.requested_production_decisioning, "production decisioning is not supported"),
        (spec.requested_live_api, "live API authorization is not supported"),
        (spec.requested_scheduler, "scheduler authorization is not supported"),
        (spec.requested_budget_optimization, "budget optimization is not supported"),
    ]
    for flag, msg in checks:
        if flag:
            return _blocked_result(spec, validity=ScaleValidity.BLOCKED, reasons=(msg,))
    return None


def validate_studentized_scale_contract(spec: StudentizedPlaceboRankSpec) -> ScaleValidity:
    """Validate scale and effect inputs for studentized placebo-rank inference."""
    if not _is_finite(spec.observed_effect):
        return ScaleValidity.NON_FINITE_SCALE

    if spec.observed_scale is None:
        return ScaleValidity.MISSING_OBSERVED_SCALE

    if not _is_finite(spec.observed_scale):
        return ScaleValidity.NON_FINITE_SCALE

    if float(spec.observed_scale) <= 0:
        return ScaleValidity.NON_POSITIVE_SCALE

    pseudo_effects = spec.pseudo_effect_by_assignment
    pseudo_scales = spec.pseudo_scale_by_assignment

    if not pseudo_effects:
        return ScaleValidity.INSUFFICIENT_PLACEBO_SETS

    if len(pseudo_effects) < spec.min_placebo_sets:
        return ScaleValidity.INSUFFICIENT_PLACEBO_SETS

    effect_ids = set(pseudo_effects)
    scale_ids = set(pseudo_scales)

    if effect_ids != scale_ids:
        return ScaleValidity.MISSING_PSEUDO_SCALE

    for assignment_id in effect_ids:
        effect = pseudo_effects[assignment_id]
        scale = pseudo_scales[assignment_id]
        if not _is_finite(effect):
            return ScaleValidity.NON_FINITE_SCALE
        if scale is None:
            return ScaleValidity.MISSING_PSEUDO_SCALE
        if not _is_finite(scale):
            return ScaleValidity.NON_FINITE_SCALE
        if float(scale) <= 0:
            return ScaleValidity.NON_POSITIVE_SCALE

    if spec.scale_source == ScaleSource.UNKNOWN:
        return ScaleValidity.MISMATCHED_SCALE_SOURCE

    return ScaleValidity.VALID


def compute_studentized_statistics(
    spec: StudentizedPlaceboRankSpec,
) -> tuple[float, dict[str, float]]:
    """Compute observed and pseudo studentized statistics from effect/scale contract."""
    observed = (float(spec.observed_effect) - spec.null_value) / float(spec.observed_scale)  # type: ignore[arg-type]
    pseudo: dict[str, float] = {}
    for assignment_id, effect in spec.pseudo_effect_by_assignment.items():
        scale = float(spec.pseudo_scale_by_assignment[assignment_id])
        pseudo[assignment_id] = (float(effect) - spec.null_value) / scale
    return observed, pseudo


def compute_studentized_placebo_rank(
    observed_studentized_statistic: float,
    pseudo_studentized_statistic_by_assignment: Mapping[str, float],
    effect_direction: StudentizedEffectDirection,
) -> tuple[int, float]:
    """Compute inclusive placebo rank and empirical tail fraction on studentized scale."""
    pseudo_stats = list(pseudo_studentized_statistic_by_assignment.values())
    if not pseudo_stats:
        return 0, 0.0
    direction = effect_direction.value
    observed = observed_studentized_statistic
    if direction == StudentizedEffectDirection.GREATER.value:
        rank = sum(1 for p in pseudo_stats if p >= observed)
    elif direction == StudentizedEffectDirection.LESS.value:
        rank = sum(1 for p in pseudo_stats if p <= observed)
    else:
        rank = sum(1 for p in pseudo_stats if abs(p) >= abs(observed))
    return rank, rank / len(pseudo_stats)


def evaluate_studentized_placebo_rank(
    spec: StudentizedPlaceboRankSpec,
) -> StudentizedPlaceboRankResult:
    """Evaluate studentized placebo-rank inference under governed semantics."""
    platform_block = _platform_overclaim_block(spec)
    if platform_block is not None:
        return platform_block

    role = spec.assignment_role
    if spec.require_design_based_assignment and role not in {DESIGN_ROLE, FALSIFICATION_ROLE}:
        return _blocked_result(
            spec,
            validity=ScaleValidity.BLOCKED,
            reasons=(f"assignment role blocked or unknown: {role}",),
        )

    validity = validate_studentized_scale_contract(spec)
    if validity != ScaleValidity.VALID:
        return _blocked_result(
            spec,
            validity=validity,
            reasons=(f"scale contract invalid: {validity.value}",),
        )

    observed_studentized, pseudo_studentized = compute_studentized_statistics(spec)
    rank, tail = compute_studentized_placebo_rank(
        observed_studentized,
        pseudo_studentized,
        spec.effect_direction,
    )
    num_placebo_sets = len(pseudo_studentized)

    if role == FALSIFICATION_ROLE:
        return StudentizedPlaceboRankResult(
            decision=StudentizedRankDecision.STUDENTIZED_RANK_DIAGNOSTIC_ONLY,
            scale_validity=validity,
            observed_studentized_statistic=observed_studentized,
            pseudo_studentized_statistic_by_assignment=pseudo_studentized,
            placebo_rank=rank,
            empirical_tail_fraction=tail,
            num_placebo_sets=num_placebo_sets,
            is_candidate=False,
            is_diagnostic_only=True,
            is_blocked=False,
            warnings=(FALSIFICATION_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if role == DESIGN_ROLE:
        return StudentizedPlaceboRankResult(
            decision=StudentizedRankDecision.STUDENTIZED_RANK_CANDIDATE,
            scale_validity=validity,
            observed_studentized_statistic=observed_studentized,
            pseudo_studentized_statistic_by_assignment=pseudo_studentized,
            placebo_rank=rank,
            empirical_tail_fraction=tail,
            num_placebo_sets=num_placebo_sets,
            is_candidate=True,
            is_diagnostic_only=False,
            is_blocked=False,
            warnings=(CANDIDATE_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    return _blocked_result(
        spec,
        validity=ScaleValidity.BLOCKED,
        reasons=("unable to classify studentized placebo-rank decision",),
        observed_studentized=observed_studentized,
        pseudo_studentized=pseudo_studentized,
        num_placebo_sets=num_placebo_sets,
    )


def summarize_studentized_placebo_rank_result(
    result: StudentizedPlaceboRankResult,
) -> dict[str, Any]:
    """Serialize studentized placebo-rank result for validation archives."""
    return {
        "decision": result.decision.value,
        "scale_validity": result.scale_validity.value,
        "observed_studentized_statistic": result.observed_studentized_statistic,
        "pseudo_studentized_statistic_by_assignment": dict(
            result.pseudo_studentized_statistic_by_assignment
        ),
        "placebo_rank": result.placebo_rank,
        "empirical_tail_fraction": result.empirical_tail_fraction,
        "num_placebo_sets": result.num_placebo_sets,
        "is_candidate": result.is_candidate,
        "is_diagnostic_only": result.is_diagnostic_only,
        "is_blocked": result.is_blocked,
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


__all__ = [
    "CANDIDATE_WARNING",
    "FALSIFICATION_WARNING",
    "ScaleSource",
    "ScaleValidity",
    "StudentizedEffectDirection",
    "StudentizedPlaceboRankResult",
    "StudentizedPlaceboRankSpec",
    "StudentizedRankDecision",
    "compute_studentized_placebo_rank",
    "compute_studentized_statistics",
    "evaluate_studentized_placebo_rank",
    "summarize_studentized_placebo_rank_result",
    "validate_studentized_scale_contract",
]
