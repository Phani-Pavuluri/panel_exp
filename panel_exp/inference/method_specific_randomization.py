"""METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001 — method-specific readiness classification.

This artifact validates method-specific randomization inference readiness only.
It does not produce final production p-values or confidence intervals.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from panel_exp.design.assignment_generators import AssignmentRole

MINIMUM_VALID_PSEUDO_ASSIGNMENTS = 2

LOTO_SENSITIVITY_NOTE = "leave_one_treated_out_sensitivity"
MULTICELL_GLOBAL_NOTE = "multicell_global_claim"
DCM_ADAPTER_NOTE = "dcm_adapter_qualification"

CANDIDATE_WARNING = (
    "Framework-level design-based randomization candidate only — not a final "
    "production p-value or causal confidence interval."
)

FALSIFICATION_WARNING = (
    "Pseudo-assignments are falsification-only; this is not design-based causal inference."
)

TBRRIDGE_REPLACEMENT_EVIDENCE = "tbrridge_replacement_inference_required"


class MethodFamily(str, Enum):
    SCM = "scm"
    DID = "did"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    TBRRIDGE = "tbrridge"
    TBR = "tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    SYNTHETIC_DID = "synthetic_did"
    TROP = "trop"
    UNKNOWN = "unknown"


class MethodStatisticKind(str, Enum):
    ABSOLUTE_EFFECT = "absolute_effect"
    RELATIVE_EFFECT = "relative_effect"
    STUDENTIZED_EFFECT = "studentized_effect"
    SIGNED_EFFECT = "signed_effect"
    RANK_STATISTIC = "rank_statistic"
    PLACEBO_TAIL_FRACTION = "placebo_tail_fraction"
    BOOTSTRAP_INTERVAL = "bootstrap_interval"
    JACKKNIFE_INTERVAL = "jackknife_interval"
    POSTERIOR_INTERVAL = "posterior_interval"
    UNKNOWN = "unknown"


class MethodGeometry(str, Enum):
    SINGLE_TREATED = "single_treated"
    MULTI_TREATED_SET = "multi_treated_set"
    MATCHED_PAIR = "matched_pair"
    STRATIFIED = "stratified"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    AGGREGATE = "aggregate"
    UNKNOWN = "unknown"


class RandomizationValidationRole(str, Enum):
    DESIGN_BASED_RANDOMIZATION_CANDIDATE = "design_based_randomization_candidate"
    FALSIFICATION_DIAGNOSTIC = "falsification_diagnostic"
    SENSITIVITY_ONLY = "sensitivity_only"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_DEFERRED = "research_deferred"
    BLOCKED = "blocked"


class MethodSpecificDecision(str, Enum):
    METHOD_RANDOMIZATION_CANDIDATE = "method_randomization_candidate"
    METHOD_FALSIFICATION_DIAGNOSTIC_ONLY = "method_falsification_diagnostic_only"
    METHOD_SENSITIVITY_ONLY = "method_sensitivity_only"
    METHOD_DIAGNOSTIC_ONLY = "method_diagnostic_only"
    METHOD_RESEARCH_DEFERRED = "method_research_deferred"
    METHOD_BLOCKED = "method_blocked"


@dataclass(frozen=True)
class MethodRandomizationValidationSpec:
    method_family: MethodFamily
    statistic_kind: MethodStatisticKind
    geometry: MethodGeometry
    assignment_role: str | None = None
    num_treated_units: int | None = None
    num_valid_pseudo_assignments: int = 0
    has_observed_statistic: bool = False
    has_pseudo_statistics: bool = False
    uses_same_statistic_observed_and_pseudo: bool = False
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
class MethodRandomizationValidationResult:
    role: RandomizationValidationRole
    decision: MethodSpecificDecision
    method_family: MethodFamily
    statistic_kind: MethodStatisticKind
    geometry: MethodGeometry
    is_candidate: bool
    is_diagnostic_only: bool
    is_blocked: bool
    required_next_evidence: tuple[str, ...]
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


def _result(
    spec: MethodRandomizationValidationSpec,
    *,
    role: RandomizationValidationRole,
    decision: MethodSpecificDecision,
    warnings: tuple[str, ...] = (),
    blocked_reasons: tuple[str, ...] = (),
    required_next_evidence: tuple[str, ...] = (),
) -> MethodRandomizationValidationResult:
    return MethodRandomizationValidationResult(
        role=role,
        decision=decision,
        method_family=spec.method_family,
        statistic_kind=spec.statistic_kind,
        geometry=spec.geometry,
        is_candidate=role == RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
        is_diagnostic_only=role
        in {
            RandomizationValidationRole.DIAGNOSTIC_ONLY,
            RandomizationValidationRole.FALSIFICATION_DIAGNOSTIC,
        },
        is_blocked=role == RandomizationValidationRole.BLOCKED,
        required_next_evidence=required_next_evidence,
        warnings=warnings,
        blocked_reasons=blocked_reasons,
        governance_flags=_governance_flags(),
    )


def _blocked(
    spec: MethodRandomizationValidationSpec,
    *,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
) -> MethodRandomizationValidationResult:
    return _result(
        spec,
        role=RandomizationValidationRole.BLOCKED,
        decision=MethodSpecificDecision.METHOD_BLOCKED,
        warnings=warnings,
        blocked_reasons=reasons,
    )


def _platform_block(spec: MethodRandomizationValidationSpec) -> MethodRandomizationValidationResult | None:
    checks: list[tuple[bool, str]] = [
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
            return _blocked(spec, reasons=(msg,))
    if MULTICELL_GLOBAL_NOTE in spec.notes:
        return _blocked(
            spec,
            reasons=("multiplicity_or_shared_control_dependence_unresolved",),
        )
    if DCM_ADAPTER_NOTE in spec.notes:
        return _blocked(spec, reasons=("DCM-009-019 adapter qualification not authorized",))
    return None


def _semantic_overclaim_block(
    spec: MethodRandomizationValidationSpec,
) -> MethodRandomizationValidationResult | None:
    reasons: list[str] = []
    if spec.requested_final_p_value:
        reasons.append("final production p-value semantics are blocked")
    if spec.requested_causal_interval:
        reasons.append("causal confidence interval semantics are blocked")
    if reasons:
        return _blocked(spec, reasons=tuple(reasons), warnings=tuple(reasons))
    return None


def _is_design_based(role: str | None) -> bool:
    return role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value


def _is_falsification(role: str | None) -> bool:
    return role == AssignmentRole.FALSIFICATION_ONLY.value


def _is_blocked_role(role: str | None) -> bool:
    return role == AssignmentRole.BLOCKED.value or role is None


def _candidate_ready(spec: MethodRandomizationValidationSpec) -> bool:
    return (
        _is_design_based(spec.assignment_role)
        and spec.num_valid_pseudo_assignments >= MINIMUM_VALID_PSEUDO_ASSIGNMENTS
        and spec.has_observed_statistic
        and spec.has_pseudo_statistics
        and spec.uses_same_statistic_observed_and_pseudo
    )


def _tbrridge_terminal(
    spec: MethodRandomizationValidationSpec,
) -> MethodRandomizationValidationResult | None:
    if spec.method_family != MethodFamily.TBRRIDGE:
        return None
    if spec.statistic_kind == MethodStatisticKind.JACKKNIFE_INTERVAL:
        return _result(
            spec,
            role=RandomizationValidationRole.BLOCKED,
            decision=MethodSpecificDecision.METHOD_BLOCKED,
            blocked_reasons=("TBRRidge JK known_failure_mode — not randomization candidate",),
            required_next_evidence=(TBRRIDGE_REPLACEMENT_EVIDENCE,),
        )
    if spec.statistic_kind in {
        MethodStatisticKind.BOOTSTRAP_INTERVAL,
        MethodStatisticKind.PLACEBO_TAIL_FRACTION,
        MethodStatisticKind.JACKKNIFE_INTERVAL,
    }:
        return _result(
            spec,
            role=RandomizationValidationRole.DIAGNOSTIC_ONLY,
            decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
            warnings=("TBRRidge BRB/KFold/Placebo paths are diagnostic-only — replacement inference required",),
            required_next_evidence=(TBRRIDGE_REPLACEMENT_EVIDENCE,),
        )
    return _result(
        spec,
        role=RandomizationValidationRole.DIAGNOSTIC_ONLY,
        decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
        required_next_evidence=(TBRRIDGE_REPLACEMENT_EVIDENCE,),
    )


def _method_terminal_rules(
    spec: MethodRandomizationValidationSpec,
) -> MethodRandomizationValidationResult | None:
    tbrridge = _tbrridge_terminal(spec)
    if tbrridge is not None:
        return tbrridge

    if spec.method_family == MethodFamily.TBR and spec.geometry == MethodGeometry.AGGREGATE:
        return _blocked(spec, reasons=("geometry_mismatch",))

    if spec.method_family == MethodFamily.BAYESIAN_TBR:
        return _result(
            spec,
            role=RandomizationValidationRole.RESEARCH_DEFERRED,
            decision=MethodSpecificDecision.METHOD_RESEARCH_DEFERRED,
            warnings=("BayesianTBR lacks method-specific randomization validation evidence",),
            required_next_evidence=("bayesian_tbr_method_validation",),
        )

    if spec.method_family in {MethodFamily.SYNTHETIC_DID, MethodFamily.TROP}:
        return _result(
            spec,
            role=RandomizationValidationRole.RESEARCH_DEFERRED,
            decision=MethodSpecificDecision.METHOD_RESEARCH_DEFERRED,
            warnings=("insufficient package validation evidence for adapter methods",),
            required_next_evidence=("dcm_adapter_qualification_evidence",),
        )

    if spec.method_family == MethodFamily.UNKNOWN:
        return _blocked(spec, reasons=("unknown method family",))

    if spec.method_family == MethodFamily.AUGSYNTH_CVXPY:
        if spec.statistic_kind == MethodStatisticKind.JACKKNIFE_INTERVAL:
            return _result(
                spec,
                role=RandomizationValidationRole.DIAGNOSTIC_ONLY,
                decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
                warnings=(
                    "AugSynth JK interval is diagnostic-only — distinct from point-statistic randomization candidate",
                ),
                required_next_evidence=("augsynth_estimand_scale_bridge",),
            )

    return None


def validate_method_randomization_inference(
    spec: MethodRandomizationValidationSpec,
) -> MethodRandomizationValidationResult:
    """Classify method-specific randomization inference readiness."""
    platform = _platform_block(spec)
    if platform is not None:
        return platform

    overclaim = _semantic_overclaim_block(spec)
    if overclaim is not None:
        return overclaim

    terminal = _method_terminal_rules(spec)
    if terminal is not None:
        return terminal

    if LOTO_SENSITIVITY_NOTE in spec.notes:
        return _result(
            spec,
            role=RandomizationValidationRole.SENSITIVITY_ONLY,
            decision=MethodSpecificDecision.METHOD_SENSITIVITY_ONLY,
            warnings=("Leave-one-treated-out is sensitivity analysis only — not placebo inference",),
        )

    if _is_blocked_role(spec.assignment_role):
        return _blocked(spec, reasons=(f"assignment role blocked: {spec.assignment_role}",))

    if _is_falsification(spec.assignment_role):
        return _result(
            spec,
            role=RandomizationValidationRole.FALSIFICATION_DIAGNOSTIC,
            decision=MethodSpecificDecision.METHOD_FALSIFICATION_DIAGNOSTIC_ONLY,
            warnings=(FALSIFICATION_WARNING,),
        )

    # SCM single-treated placebo
    if (
        spec.method_family == MethodFamily.SCM
        and spec.geometry == MethodGeometry.SINGLE_TREATED
        and spec.statistic_kind
        in {MethodStatisticKind.PLACEBO_TAIL_FRACTION, MethodStatisticKind.RANK_STATISTIC}
    ):
        return _result(
            spec,
            role=RandomizationValidationRole.FALSIFICATION_DIAGNOSTIC,
            decision=MethodSpecificDecision.METHOD_FALSIFICATION_DIAGNOSTIC_ONLY,
            warnings=("SCM single-treated placebo is null-monitor/falsification only", CANDIDATE_WARNING),
        )

    # DID bootstrap-only without comparable pseudo point statistics
    if (
        spec.method_family == MethodFamily.DID
        and spec.statistic_kind == MethodStatisticKind.BOOTSTRAP_INTERVAL
        and not spec.uses_same_statistic_observed_and_pseudo
    ):
        return _result(
            spec,
            role=RandomizationValidationRole.DIAGNOSTIC_ONLY,
            decision=MethodSpecificDecision.METHOD_DIAGNOSTIC_ONLY,
            warnings=(
                "DID bootstrap interval does not imply design-based randomization validity",
            ),
        )

    # Statistic contract failures
    if not spec.has_observed_statistic or not spec.has_pseudo_statistics:
        return _blocked(
            spec,
            reasons=("missing observed or pseudo statistics",),
        )
    if not spec.uses_same_statistic_observed_and_pseudo:
        return _blocked(
            spec,
            reasons=("observed and pseudo statistics use incompatible definitions",),
        )
    if spec.num_valid_pseudo_assignments < MINIMUM_VALID_PSEUDO_ASSIGNMENTS:
        return _blocked(
            spec,
            reasons=(
                f"insufficient pseudo assignments: {spec.num_valid_pseudo_assignments} "
                f"< {MINIMUM_VALID_PSEUDO_ASSIGNMENTS}",
            ),
        )

    if _candidate_ready(spec):
        compatible_geometries = {
            MethodGeometry.MULTI_TREATED_SET,
            MethodGeometry.MATCHED_PAIR,
            MethodGeometry.STRATIFIED,
            MethodGeometry.SINGLE_TREATED,
            MethodGeometry.MULTICELL_SHARED_CONTROL,
        }
        if spec.geometry not in compatible_geometries:
            return _blocked(spec, reasons=(f"geometry incompatible: {spec.geometry.value}",))
        if (
            spec.geometry == MethodGeometry.MULTICELL_SHARED_CONTROL
            and MULTICELL_GLOBAL_NOTE in spec.notes
        ):
            return _blocked(
                spec,
                reasons=("multiplicity_or_shared_control_dependence_unresolved",),
            )
        return _result(
            spec,
            role=RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE,
            decision=MethodSpecificDecision.METHOD_RANDOMIZATION_CANDIDATE,
            warnings=(CANDIDATE_WARNING,),
        )

    return _blocked(spec, reasons=("method randomization candidate conditions not satisfied",))


def classify_method_from_scm_semantics(
    *,
    method_family: MethodFamily,
    statistic_kind: MethodStatisticKind,
    geometry: MethodGeometry,
    scm_semantic_role: str,
    num_valid_pseudo_assignments: int = 0,
    has_observed_statistic: bool = True,
    has_pseudo_statistics: bool = True,
) -> MethodRandomizationValidationResult:
    """Bridge SCM placebo semantics roles into method-specific validation."""
    role_map = {
        "design_based_randomization_candidate": AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
        "falsification_diagnostic": AssignmentRole.FALSIFICATION_ONLY.value,
        "null_monitor_only": AssignmentRole.FALSIFICATION_ONLY.value,
        "sensitivity_only": AssignmentRole.FALSIFICATION_ONLY.value,
        "blocked": AssignmentRole.BLOCKED.value,
    }
    notes: tuple[str, ...] = ()
    if scm_semantic_role == "sensitivity_only":
        notes = (LOTO_SENSITIVITY_NOTE,)
    spec = MethodRandomizationValidationSpec(
        method_family=method_family,
        statistic_kind=statistic_kind,
        geometry=geometry,
        assignment_role=role_map.get(scm_semantic_role, AssignmentRole.BLOCKED.value),
        num_valid_pseudo_assignments=num_valid_pseudo_assignments,
        has_observed_statistic=has_observed_statistic,
        has_pseudo_statistics=has_pseudo_statistics,
        uses_same_statistic_observed_and_pseudo=True,
        notes=notes,
    )
    return validate_method_randomization_inference(spec)


def build_method_randomization_readiness_matrix() -> list[dict[str, Any]]:
    """Static method-family readiness matrix from governed repo evidence."""
    return [
        {
            "method_family": MethodFamily.SCM.value,
            "statistic_kind": MethodStatisticKind.SIGNED_EFFECT.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
            "note": "candidate when assignment and statistic contract satisfied",
        },
        {
            "method_family": MethodFamily.SCM.value,
            "statistic_kind": MethodStatisticKind.PLACEBO_TAIL_FRACTION.value,
            "geometry": MethodGeometry.SINGLE_TREATED.value,
            "default_role": RandomizationValidationRole.FALSIFICATION_DIAGNOSTIC.value,
        },
        {
            "method_family": MethodFamily.DID.value,
            "statistic_kind": MethodStatisticKind.SIGNED_EFFECT.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
            "note": "not production authorization",
        },
        {
            "method_family": MethodFamily.DID.value,
            "statistic_kind": MethodStatisticKind.BOOTSTRAP_INTERVAL.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.DIAGNOSTIC_ONLY.value,
        },
        {
            "method_family": MethodFamily.AUGSYNTH_CVXPY.value,
            "statistic_kind": MethodStatisticKind.SIGNED_EFFECT.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
        },
        {
            "method_family": MethodFamily.AUGSYNTH_CVXPY.value,
            "statistic_kind": MethodStatisticKind.JACKKNIFE_INTERVAL.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.DIAGNOSTIC_ONLY.value,
        },
        {
            "method_family": MethodFamily.TBRRIDGE.value,
            "statistic_kind": MethodStatisticKind.BOOTSTRAP_INTERVAL.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.DIAGNOSTIC_ONLY.value,
        },
        {
            "method_family": MethodFamily.TBR.value,
            "statistic_kind": MethodStatisticKind.SIGNED_EFFECT.value,
            "geometry": MethodGeometry.AGGREGATE.value,
            "default_role": RandomizationValidationRole.BLOCKED.value,
            "blocked_reason": "geometry_mismatch",
        },
        {
            "method_family": MethodFamily.BAYESIAN_TBR.value,
            "statistic_kind": MethodStatisticKind.POSTERIOR_INTERVAL.value,
            "geometry": MethodGeometry.MULTI_TREATED_SET.value,
            "default_role": RandomizationValidationRole.RESEARCH_DEFERRED.value,
        },
        {
            "method_family": MethodFamily.SYNTHETIC_DID.value,
            "statistic_kind": MethodStatisticKind.UNKNOWN.value,
            "geometry": MethodGeometry.UNKNOWN.value,
            "default_role": RandomizationValidationRole.RESEARCH_DEFERRED.value,
        },
        {
            "method_family": MethodFamily.TROP.value,
            "statistic_kind": MethodStatisticKind.UNKNOWN.value,
            "geometry": MethodGeometry.UNKNOWN.value,
            "default_role": RandomizationValidationRole.RESEARCH_DEFERRED.value,
        },
    ]


def summarize_method_randomization_result(
    result: MethodRandomizationValidationResult,
) -> dict[str, Any]:
    """Serialize a method randomization validation result."""
    return {
        "role": result.role.value,
        "decision": result.decision.value,
        "method_family": result.method_family.value,
        "statistic_kind": result.statistic_kind.value,
        "geometry": result.geometry.value,
        "is_candidate": result.is_candidate,
        "is_diagnostic_only": result.is_diagnostic_only,
        "is_blocked": result.is_blocked,
        "required_next_evidence": list(result.required_next_evidence),
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


__all__ = [
    "LOTO_SENSITIVITY_NOTE",
    "MULTICELL_GLOBAL_NOTE",
    "MINIMUM_VALID_PSEUDO_ASSIGNMENTS",
    "MethodFamily",
    "MethodGeometry",
    "MethodRandomizationValidationResult",
    "MethodRandomizationValidationSpec",
    "MethodSpecificDecision",
    "MethodStatisticKind",
    "RandomizationValidationRole",
    "build_method_randomization_readiness_matrix",
    "classify_method_from_scm_semantics",
    "summarize_method_randomization_result",
    "validate_method_randomization_inference",
]
