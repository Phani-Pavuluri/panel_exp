"""SCM_PLACEBO_GOVERNED_SEMANTICS_001 — governed SCM placebo semantic classification.

SCM single-treated placebo remains falsification/null-monitor only.
Leave-one-treated-out is sensitivity analysis, not placebo inference.
Treated-set placebo can only become a design-based randomization candidate when
pseudo-assignment generators preserve the original assignment constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.treated_set_placebo import (
    PlaceboDecision,
    PlaceboSemanticRole,
    TreatedSetPlaceboResult,
)

MINIMUM_VALID_PSEUDO_ASSIGNMENTS = 2

LOTO_AS_PLACEBO_NOTE = "requested_as_placebo_inference"

LOTO_REJECTION_MESSAGE = (
    "Leave-one-treated-out is sensitivity analysis only and is not placebo inference. "
    "It checks treated-unit dependence, not assignment-null behavior."
)

SINGLE_TREATED_WARNING = (
    "SCM single-treated placebo is null-monitor/falsification only — not a final "
    "production p-value or causal confidence interval."
)

DESIGN_BASED_CANDIDATE_WARNING = (
    "Framework-level design-based randomization candidate only — not a final "
    "production p-value or causal confidence interval."
)

FALSIFICATION_WARNING = (
    "Pseudo-assignments are falsification-only; this is not design-based causal inference."
)


class SCMPlaceboUseCase(str, Enum):
    SINGLE_TREATED_PLACEBO = "single_treated_placebo"
    MULTI_TREATED_SET_PLACEBO = "multi_treated_set_placebo"
    LEAVE_ONE_TREATED_OUT_SENSITIVITY = "leave_one_treated_out_sensitivity"
    DESIGN_AWARE_PSEUDO_ASSIGNMENT_PLACEBO = "design_aware_pseudo_assignment_placebo"
    UNKNOWN = "unknown"


class SCMPlaceboSemanticRole(str, Enum):
    NULL_MONITOR_ONLY = "null_monitor_only"
    FALSIFICATION_DIAGNOSTIC = "falsification_diagnostic"
    DESIGN_BASED_RANDOMIZATION_CANDIDATE = "design_based_randomization_candidate"
    SENSITIVITY_ONLY = "sensitivity_only"
    BLOCKED = "blocked"


class SCMPlaceboDecision(str, Enum):
    SCM_PLACEBO_SINGLE_TREATED_FALSIFICATION_ONLY = "scm_placebo_single_treated_falsification_only"
    SCM_PLACEBO_TREATED_SET_FRAMEWORK_SUPPORTED = "scm_placebo_treated_set_framework_supported"
    SCM_PLACEBO_DESIGN_BASED_CANDIDATE = "scm_placebo_design_based_candidate"
    SCM_PLACEBO_FALSIFICATION_ONLY = "scm_placebo_falsification_only"
    SCM_LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO = "scm_leave_one_treated_out_rejected_as_placebo"
    SCM_PLACEBO_BLOCKED = "scm_placebo_blocked"


@dataclass(frozen=True)
class SCMPlaceboSemanticsSpec:
    use_case: SCMPlaceboUseCase
    num_treated_units: int
    assignment_role: str | None = None
    assignment_family: str | None = None
    has_valid_pseudo_assignments: bool = False
    num_valid_pseudo_assignments: int = 0
    requested_as_causal_interval: bool = False
    requested_as_final_p_value: bool = False
    requested_as_trustreport_authorization: bool = False
    requested_as_calibration_signal: bool = False
    requested_as_production_decisioning: bool = False
    requested_as_live_api: bool = False
    requested_as_scheduler: bool = False
    requested_as_budget_optimization: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SCMPlaceboSemanticsResult:
    semantic_role: SCMPlaceboSemanticRole
    decision: SCMPlaceboDecision
    is_design_based_candidate: bool
    is_falsification_only: bool
    is_sensitivity_only: bool
    is_blocked: bool
    warnings: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    governance_flags: Mapping[str, bool]


def _governance_flags() -> dict[str, bool]:
    return {
        "trustreport_authorized": False,
        "calibration_signal_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
    }


def _blocked(
    spec: SCMPlaceboSemanticsSpec,
    *,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
) -> SCMPlaceboSemanticsResult:
    return SCMPlaceboSemanticsResult(
        semantic_role=SCMPlaceboSemanticRole.BLOCKED,
        decision=SCMPlaceboDecision.SCM_PLACEBO_BLOCKED,
        is_design_based_candidate=False,
        is_falsification_only=False,
        is_sensitivity_only=False,
        is_blocked=True,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def _overclaim_block(spec: SCMPlaceboSemanticsSpec) -> SCMPlaceboSemanticsResult | None:
    checks: list[tuple[bool, str]] = [
        (spec.requested_as_trustreport_authorization, "TrustReport authorization is not supported"),
        (spec.requested_as_calibration_signal, "CalibrationSignal export is not supported"),
        (spec.requested_as_production_decisioning, "production decisioning is not supported"),
        (spec.requested_as_live_api, "live API authorization is not supported"),
        (spec.requested_as_scheduler, "scheduler authorization is not supported"),
        (spec.requested_as_budget_optimization, "budget optimization is not supported"),
    ]
    for flag, msg in checks:
        if flag:
            return _blocked(spec, reasons=(msg,))
    return None


def _semantic_overclaim_block(spec: SCMPlaceboSemanticsSpec) -> SCMPlaceboSemanticsResult | None:
    warnings: list[str] = []
    if spec.requested_as_final_p_value:
        warnings.append("final production p-value semantics are blocked")
    if spec.requested_as_causal_interval:
        warnings.append("causal confidence interval semantics are blocked")
    if warnings:
        return _blocked(spec, reasons=tuple(warnings), warnings=tuple(warnings))
    return None


def reject_scm_leave_one_treated_out_as_placebo(
    spec: SCMPlaceboSemanticsSpec,
) -> SCMPlaceboSemanticsResult:
    """Reject leave-one-treated-out when used as placebo inference."""
    return SCMPlaceboSemanticsResult(
        semantic_role=SCMPlaceboSemanticRole.SENSITIVITY_ONLY,
        decision=SCMPlaceboDecision.SCM_LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO,
        is_design_based_candidate=False,
        is_falsification_only=False,
        is_sensitivity_only=True,
        is_blocked=True,
        warnings=(LOTO_REJECTION_MESSAGE,),
        blocked_reasons=(LOTO_REJECTION_MESSAGE,),
        governance_flags=_governance_flags(),
    )


def _role_from_assignment(assignment_role: str | None) -> SCMPlaceboSemanticRole:
    if assignment_role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value:
        return SCMPlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    if assignment_role == AssignmentRole.FALSIFICATION_ONLY.value:
        return SCMPlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    return SCMPlaceboSemanticRole.BLOCKED


def _treated_set_insufficient(spec: SCMPlaceboSemanticsSpec) -> bool:
    if not spec.has_valid_pseudo_assignments:
        return True
    return spec.num_valid_pseudo_assignments < MINIMUM_VALID_PSEUDO_ASSIGNMENTS


def classify_scm_placebo_semantics(spec: SCMPlaceboSemanticsSpec) -> SCMPlaceboSemanticsResult:
    """Classify governed SCM placebo semantics for a use case and assignment context."""
    platform_block = _overclaim_block(spec)
    if platform_block is not None:
        return platform_block

    if spec.use_case == SCMPlaceboUseCase.UNKNOWN:
        return _blocked(spec, reasons=("unknown SCM placebo use case",))

    if spec.num_treated_units <= 0:
        return _blocked(spec, reasons=("num_treated_units must be positive",))

    overclaim = _semantic_overclaim_block(spec)
    if overclaim is not None:
        return overclaim

    if spec.use_case == SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO:
        if spec.num_treated_units != 1:
            return _blocked(
                spec,
                reasons=(
                    f"single-treated SCM placebo requires num_treated_units == 1, got {spec.num_treated_units}",
                ),
            )
        return SCMPlaceboSemanticsResult(
            semantic_role=SCMPlaceboSemanticRole.NULL_MONITOR_ONLY,
            decision=SCMPlaceboDecision.SCM_PLACEBO_SINGLE_TREATED_FALSIFICATION_ONLY,
            is_design_based_candidate=False,
            is_falsification_only=True,
            is_sensitivity_only=False,
            is_blocked=False,
            warnings=(SINGLE_TREATED_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if spec.use_case == SCMPlaceboUseCase.LEAVE_ONE_TREATED_OUT_SENSITIVITY:
        if LOTO_AS_PLACEBO_NOTE in spec.notes:
            return reject_scm_leave_one_treated_out_as_placebo(spec)
        return SCMPlaceboSemanticsResult(
            semantic_role=SCMPlaceboSemanticRole.SENSITIVITY_ONLY,
            decision=SCMPlaceboDecision.SCM_PLACEBO_FALSIFICATION_ONLY,
            is_design_based_candidate=False,
            is_falsification_only=False,
            is_sensitivity_only=True,
            is_blocked=False,
            warnings=(
                "Leave-one-treated-out is robustness/sensitivity analysis only — not placebo inference.",
            ),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if spec.use_case in {
        SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
        SCMPlaceboUseCase.DESIGN_AWARE_PSEUDO_ASSIGNMENT_PLACEBO,
    }:
        if spec.num_treated_units < 2 and spec.use_case == SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO:
            return _blocked(
                spec,
                reasons=(
                    f"multi-treated SCM placebo requires num_treated_units >= 2, got {spec.num_treated_units}",
                ),
            )
        if _treated_set_insufficient(spec):
            return _blocked(
                spec,
                reasons=("no valid or insufficient pseudo-assignments for treated-set placebo",),
            )
        role = _role_from_assignment(spec.assignment_role)
        if role == SCMPlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE:
            decision = (
                SCMPlaceboDecision.SCM_PLACEBO_TREATED_SET_FRAMEWORK_SUPPORTED
                if spec.use_case == SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO
                else SCMPlaceboDecision.SCM_PLACEBO_DESIGN_BASED_CANDIDATE
            )
            return SCMPlaceboSemanticsResult(
                semantic_role=role,
                decision=decision,
                is_design_based_candidate=True,
                is_falsification_only=False,
                is_sensitivity_only=False,
                is_blocked=False,
                warnings=(DESIGN_BASED_CANDIDATE_WARNING,),
                blocked_reasons=(),
                governance_flags=_governance_flags(),
            )
        if role == SCMPlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC:
            return SCMPlaceboSemanticsResult(
                semantic_role=role,
                decision=SCMPlaceboDecision.SCM_PLACEBO_FALSIFICATION_ONLY,
                is_design_based_candidate=False,
                is_falsification_only=True,
                is_sensitivity_only=False,
                is_blocked=False,
                warnings=(FALSIFICATION_WARNING,),
                blocked_reasons=(),
                governance_flags=_governance_flags(),
            )
        return _blocked(
            spec,
            reasons=(f"assignment role blocked or unknown: {spec.assignment_role}",),
        )

    return _blocked(spec, reasons=(f"unsupported use case: {spec.use_case.value}",))


def classify_from_treated_set_placebo_result(
    *,
    num_treated_units: int,
    placebo_result: TreatedSetPlaceboResult,
    requested_as_final_p_value: bool = False,
    requested_as_causal_interval: bool = False,
) -> SCMPlaceboSemanticsResult:
    """Map a treated-set placebo framework result into SCM placebo semantics."""
    role_map = {
        PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value: (
            AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
        ),
        PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC.value: AssignmentRole.FALSIFICATION_ONLY.value,
        PlaceboSemanticRole.BLOCKED.value: AssignmentRole.BLOCKED.value,
    }
    assignment_role = role_map.get(placebo_result.semantic_role.value, AssignmentRole.BLOCKED.value)
    has_valid = placebo_result.num_valid_placebo_sets > 0 and not placebo_result.blocked_reasons
    spec = SCMPlaceboSemanticsSpec(
        use_case=SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO,
        num_treated_units=num_treated_units,
        assignment_role=assignment_role,
        has_valid_pseudo_assignments=has_valid,
        num_valid_pseudo_assignments=placebo_result.num_valid_placebo_sets,
        requested_as_final_p_value=requested_as_final_p_value,
        requested_as_causal_interval=requested_as_causal_interval,
    )
    if placebo_result.decision == PlaceboDecision.LEAVE_ONE_TREATED_OUT_REJECTED_AS_PLACEBO:
        return reject_scm_leave_one_treated_out_as_placebo(
            SCMPlaceboSemanticsSpec(
                use_case=SCMPlaceboUseCase.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
                num_treated_units=num_treated_units,
                notes=(LOTO_AS_PLACEBO_NOTE,),
            )
        )
    if placebo_result.decision in {
        PlaceboDecision.PLACEBO_FRAMEWORK_BLOCKED,
        PlaceboDecision.TOO_FEW_VALID_PSEUDO_ASSIGNMENTS,
        PlaceboDecision.UNKNOWN_ASSIGNMENT_DESIGN_BLOCKED,
        PlaceboDecision.MULTICELL_GLOBAL_CLAIM_BLOCKED,
    }:
        return _blocked(
            spec,
            reasons=tuple(placebo_result.blocked_reasons) or (placebo_result.decision.value,),
        )
    return classify_scm_placebo_semantics(spec)


def summarize_scm_placebo_semantics_result(result: SCMPlaceboSemanticsResult) -> dict[str, Any]:
    """Serialize SCM placebo semantics for validation archives."""
    return {
        "semantic_role": result.semantic_role.value,
        "decision": result.decision.value,
        "is_design_based_candidate": result.is_design_based_candidate,
        "is_falsification_only": result.is_falsification_only,
        "is_sensitivity_only": result.is_sensitivity_only,
        "is_blocked": result.is_blocked,
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


__all__ = [
    "LOTO_AS_PLACEBO_NOTE",
    "MINIMUM_VALID_PSEUDO_ASSIGNMENTS",
    "SCMPlaceboDecision",
    "SCMPlaceboSemanticRole",
    "SCMPlaceboSemanticsResult",
    "SCMPlaceboSemanticsSpec",
    "SCMPlaceboUseCase",
    "classify_from_treated_set_placebo_result",
    "classify_scm_placebo_semantics",
    "reject_scm_leave_one_treated_out_as_placebo",
    "summarize_scm_placebo_semantics_result",
]
