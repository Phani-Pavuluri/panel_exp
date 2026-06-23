"""SCM_TREATED_SET_PLACEBO_INTEGRATION_001 — SCM treated-set placebo integration layer.

Connects design-aware pseudo-assignments, precomputed SCM statistics, treated-set placebo
rank/tail diagnostics, SCM placebo governed semantics, and method-specific randomization
readiness. Statistic-first: accepts precomputed observed and pseudo SCM statistics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.method_specific_randomization import (
    MINIMUM_VALID_PSEUDO_ASSIGNMENTS,
    MethodFamily,
    MethodGeometry,
    MethodRandomizationValidationSpec,
    MethodStatisticKind,
    summarize_method_randomization_result,
    validate_method_randomization_inference,
)
from panel_exp.inference.scm_placebo_semantics import (
    SCMPlaceboSemanticsSpec,
    SCMPlaceboUseCase,
    classify_scm_placebo_semantics,
    summarize_scm_placebo_semantics_result,
)
from panel_exp.inference.treated_set_placebo import (
    PlaceboSemanticRole,
    TestStatisticKind,
    compute_placebo_rank,
)

CANDIDATE_WARNING = (
    "Framework-level design-based randomization candidate only — empirical tail fraction "
    "is not a final production p-value and no causal confidence interval is authorized."
)

FALSIFICATION_WARNING = (
    "Not design-based causal inference — falsification/null-monitor diagnostic only; "
    "empirical tail fraction is not a final production p-value."
)

SINGLE_TREATED_WARNING = (
    "SCM single-treated placebo is null-monitor/falsification only — not multi-treated "
    "treated-set placebo inference."
)

SUPPORTED_STATISTIC_KINDS = frozenset(
    {
        "absolute_effect",
        "relative_effect",
        "studentized_effect",
        "signed_effect",
        "rank_statistic",
    }
)

SUPPORTED_EFFECT_DIRECTIONS = frozenset({"greater", "less", "two_sided"})


class SCMTreatedSetIntegrationDecision(str, Enum):
    SCM_TREATED_SET_RANDOMIZATION_CANDIDATE = "scm_treated_set_randomization_candidate"
    SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC = "scm_treated_set_falsification_diagnostic"
    SCM_TREATED_SET_SENSITIVITY_ONLY = "scm_treated_set_sensitivity_only"
    SCM_TREATED_SET_BLOCKED = "scm_treated_set_blocked"


class SCMStatisticSource(str, Enum):
    PRECOMPUTED = "precomputed"
    ESTIMATOR_ADAPTER = "estimator_adapter"
    UNKNOWN = "unknown"


class SCMStatisticCompatibility(str, Enum):
    COMPARABLE = "comparable"
    MISSING_OBSERVED = "missing_observed"
    MISSING_PSEUDO = "missing_pseudo"
    MISMATCHED_STATISTIC_KIND = "mismatched_statistic_kind"
    NON_NUMERIC_STATISTIC = "non_numeric_statistic"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SCMStatisticContract:
    statistic_kind: str
    effect_direction: str
    statistic_source: SCMStatisticSource
    observed_statistic: float | None
    pseudo_statistic_by_assignment: Mapping[str, float]
    observed_statistic_label: str = "observed_scm_treated_set_statistic"
    pseudo_statistic_label: str = "pseudo_scm_treated_set_statistic"
    same_statistic_observed_and_pseudo: bool = True


@dataclass(frozen=True)
class SCMTreatedSetPlaceboIntegrationSpec:
    num_treated_units: int
    assignment_role: str
    assignment_family: str | None
    num_valid_pseudo_assignments: int
    statistic_contract: SCMStatisticContract
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
class SCMTreatedSetPlaceboIntegrationResult:
    decision: SCMTreatedSetIntegrationDecision
    statistic_compatibility: SCMStatisticCompatibility
    treated_set_placebo_summary: Mapping[str, object]
    scm_semantics_summary: Mapping[str, object]
    method_randomization_summary: Mapping[str, object]
    empirical_tail_fraction: float | None
    placebo_rank: int | None
    num_placebo_sets: int
    is_candidate: bool
    is_falsification_only: bool
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


def _is_finite_numeric(value: float | None) -> bool:
    if value is None:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _blocked_result(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
    *,
    compatibility: SCMStatisticCompatibility,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    scm_semantics_summary: Mapping[str, object] | None = None,
    method_randomization_summary: Mapping[str, object] | None = None,
    placebo_rank: int | None = None,
    empirical_tail_fraction: float | None = None,
    num_placebo_sets: int = 0,
) -> SCMTreatedSetPlaceboIntegrationResult:
    return SCMTreatedSetPlaceboIntegrationResult(
        decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_BLOCKED,
        statistic_compatibility=compatibility,
        treated_set_placebo_summary={
            "semantic_role": PlaceboSemanticRole.BLOCKED.value,
            "placebo_rank": placebo_rank,
            "empirical_tail_fraction": empirical_tail_fraction,
            "num_valid_placebo_sets": num_placebo_sets,
            "framework_tail_fraction_label": "not_production_p_value",
        },
        scm_semantics_summary=dict(scm_semantics_summary or {}),
        method_randomization_summary=dict(method_randomization_summary or {}),
        empirical_tail_fraction=empirical_tail_fraction,
        placebo_rank=placebo_rank,
        num_placebo_sets=num_placebo_sets,
        is_candidate=False,
        is_falsification_only=False,
        is_blocked=True,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def _platform_overclaim_block(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
) -> SCMTreatedSetPlaceboIntegrationResult | None:
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
            return _blocked_result(
                spec,
                compatibility=SCMStatisticCompatibility.BLOCKED,
                reasons=(msg,),
            )
    return None


def _inference_overclaim_block(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
) -> SCMTreatedSetPlaceboIntegrationResult | None:
    reasons: list[str] = []
    if spec.requested_final_p_value:
        reasons.append("final production p-value semantics are blocked")
    if spec.requested_causal_interval:
        reasons.append("causal confidence interval semantics are blocked")
    if reasons:
        return _blocked_result(
            spec,
            compatibility=SCMStatisticCompatibility.BLOCKED,
            reasons=tuple(reasons),
        )
    return None


def _method_statistic_kind(statistic_kind: str) -> MethodStatisticKind:
    try:
        return MethodStatisticKind(statistic_kind)
    except ValueError:
        return MethodStatisticKind.UNKNOWN


def _test_statistic_kind(statistic_kind: str) -> TestStatisticKind:
    try:
        return TestStatisticKind(statistic_kind)
    except ValueError:
        return TestStatisticKind.SIGNED_EFFECT


def validate_scm_statistic_contract(contract: SCMStatisticContract) -> SCMStatisticCompatibility:
    """Validate SCM observed/pseudo statistic contract for treated-set placebo integration."""
    if contract.statistic_kind not in SUPPORTED_STATISTIC_KINDS:
        return SCMStatisticCompatibility.MISMATCHED_STATISTIC_KIND

    if contract.effect_direction.lower() not in SUPPORTED_EFFECT_DIRECTIONS:
        return SCMStatisticCompatibility.BLOCKED

    if not contract.same_statistic_observed_and_pseudo:
        return SCMStatisticCompatibility.MISMATCHED_STATISTIC_KIND

    if contract.observed_statistic is None:
        return SCMStatisticCompatibility.MISSING_OBSERVED

    if not _is_finite_numeric(contract.observed_statistic):
        return SCMStatisticCompatibility.NON_NUMERIC_STATISTIC

    pseudo_map = contract.pseudo_statistic_by_assignment
    if not pseudo_map:
        return SCMStatisticCompatibility.MISSING_PSEUDO

    if len(pseudo_map) < MINIMUM_VALID_PSEUDO_ASSIGNMENTS:
        return SCMStatisticCompatibility.MISSING_PSEUDO

    for value in pseudo_map.values():
        if not _is_finite_numeric(value):
            return SCMStatisticCompatibility.NON_NUMERIC_STATISTIC

    return SCMStatisticCompatibility.COMPARABLE


def _build_scm_semantics_spec(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
    *,
    use_case: SCMPlaceboUseCase,
    has_valid_pseudo: bool,
) -> SCMPlaceboSemanticsSpec:
    return SCMPlaceboSemanticsSpec(
        use_case=use_case,
        num_treated_units=spec.num_treated_units,
        assignment_role=spec.assignment_role,
        assignment_family=spec.assignment_family,
        has_valid_pseudo_assignments=has_valid_pseudo,
        num_valid_pseudo_assignments=spec.num_valid_pseudo_assignments,
        requested_as_final_p_value=spec.requested_final_p_value,
        requested_as_causal_interval=spec.requested_causal_interval,
        requested_as_trustreport_authorization=spec.requested_trustreport_authorization,
        requested_as_calibration_signal=spec.requested_calibration_signal,
        requested_as_production_decisioning=spec.requested_production_decisioning,
        requested_as_live_api=spec.requested_live_api,
        requested_as_scheduler=spec.requested_scheduler,
        requested_as_budget_optimization=spec.requested_budget_optimization,
        notes=spec.notes,
    )


def _build_method_randomization_spec(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
    *,
    compatibility: SCMStatisticCompatibility,
    geometry: MethodGeometry,
) -> MethodRandomizationValidationSpec:
    contract = spec.statistic_contract
    has_observed = compatibility != SCMStatisticCompatibility.MISSING_OBSERVED
    has_pseudo = compatibility not in {
        SCMStatisticCompatibility.MISSING_PSEUDO,
        SCMStatisticCompatibility.MISSING_OBSERVED,
    }
    return MethodRandomizationValidationSpec(
        method_family=MethodFamily.SCM,
        statistic_kind=_method_statistic_kind(contract.statistic_kind),
        geometry=geometry,
        assignment_role=spec.assignment_role,
        num_treated_units=spec.num_treated_units,
        num_valid_pseudo_assignments=spec.num_valid_pseudo_assignments,
        has_observed_statistic=has_observed,
        has_pseudo_statistics=has_pseudo and bool(contract.pseudo_statistic_by_assignment),
        uses_same_statistic_observed_and_pseudo=contract.same_statistic_observed_and_pseudo,
        requested_final_p_value=spec.requested_final_p_value,
        requested_causal_interval=spec.requested_causal_interval,
        requested_trustreport_authorization=spec.requested_trustreport_authorization,
        requested_calibration_signal=spec.requested_calibration_signal,
        requested_mmm_ingestion=spec.requested_mmm_ingestion,
        requested_llm_decisioning=spec.requested_llm_decisioning,
        requested_production_decisioning=spec.requested_production_decisioning,
        requested_live_api=spec.requested_live_api,
        requested_scheduler=spec.requested_scheduler,
        requested_budget_optimization=spec.requested_budget_optimization,
        notes=spec.notes,
    )


def _compute_placebo_diagnostics(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
) -> tuple[int | None, float | None, int]:
    contract = spec.statistic_contract
    pseudo_stats = [float(v) for v in contract.pseudo_statistic_by_assignment.values()]
    rank, tail = compute_placebo_rank(
        float(contract.observed_statistic),  # type: ignore[arg-type]
        pseudo_stats,
        contract.effect_direction,
    )
    return rank, tail, len(pseudo_stats)


def _placebo_semantic_role(assignment_role: str) -> PlaceboSemanticRole:
    if assignment_role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value:
        return PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    if assignment_role == AssignmentRole.FALSIFICATION_ONLY.value:
        return PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    return PlaceboSemanticRole.BLOCKED


def evaluate_scm_treated_set_placebo_integration(
    spec: SCMTreatedSetPlaceboIntegrationSpec,
) -> SCMTreatedSetPlaceboIntegrationResult:
    """Evaluate SCM treated-set placebo integration across framework layers."""
    platform_block = _platform_overclaim_block(spec)
    if platform_block is not None:
        return platform_block

    inference_block = _inference_overclaim_block(spec)
    if inference_block is not None:
        return inference_block

    compatibility = validate_scm_statistic_contract(spec.statistic_contract)
    if compatibility != SCMStatisticCompatibility.COMPARABLE:
        return _blocked_result(
            spec,
            compatibility=compatibility,
            reasons=(f"statistic contract not comparable: {compatibility.value}",),
        )

    if spec.num_valid_pseudo_assignments < MINIMUM_VALID_PSEUDO_ASSIGNMENTS:
        return _blocked_result(
            spec,
            compatibility=SCMStatisticCompatibility.MISSING_PSEUDO,
            reasons=(
                f"insufficient pseudo assignments: {spec.num_valid_pseudo_assignments} "
                f"< {MINIMUM_VALID_PSEUDO_ASSIGNMENTS}",
            ),
        )

    if spec.assignment_role == AssignmentRole.BLOCKED.value or spec.assignment_role not in {
        AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
        AssignmentRole.FALSIFICATION_ONLY.value,
    }:
        return _blocked_result(
            spec,
            compatibility=SCMStatisticCompatibility.BLOCKED,
            reasons=(f"assignment role blocked or unknown: {spec.assignment_role}",),
        )

    geometry = (
        MethodGeometry.SINGLE_TREATED
        if spec.num_treated_units == 1
        else MethodGeometry.MULTI_TREATED_SET
    )

    use_case = (
        SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO
        if spec.num_treated_units == 1
        else SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO
    )

    scm_semantics = classify_scm_placebo_semantics(
        _build_scm_semantics_spec(
            spec,
            use_case=use_case,
            has_valid_pseudo=spec.num_valid_pseudo_assignments >= MINIMUM_VALID_PSEUDO_ASSIGNMENTS,
        )
    )
    scm_summary = summarize_scm_placebo_semantics_result(scm_semantics)

    method_result = validate_method_randomization_inference(
        _build_method_randomization_spec(spec, compatibility=compatibility, geometry=geometry)
    )
    method_summary = summarize_method_randomization_result(method_result)

    rank, tail, num_placebo_sets = _compute_placebo_diagnostics(spec)
    placebo_role = _placebo_semantic_role(spec.assignment_role)

    treated_set_summary: dict[str, object] = {
        "semantic_role": placebo_role.value,
        "statistic_kind": spec.statistic_contract.statistic_kind,
        "effect_direction": spec.statistic_contract.effect_direction,
        "observed_statistic": spec.statistic_contract.observed_statistic,
        "pseudo_statistics_count": num_placebo_sets,
        "placebo_rank": rank,
        "empirical_tail_fraction": tail,
        "num_valid_placebo_sets": num_placebo_sets,
        "framework_tail_fraction_label": "not_production_p_value",
        "assignment_role": spec.assignment_role,
    }

    if scm_semantics.is_blocked or method_result.is_blocked:
        reasons = tuple(scm_semantics.blocked_reasons) + tuple(method_result.blocked_reasons)
        if not reasons:
            reasons = ("SCM semantics or method-specific validation blocked integration",)
        return _blocked_result(
            spec,
            compatibility=SCMStatisticCompatibility.BLOCKED,
            reasons=reasons,
            warnings=scm_semantics.warnings + method_result.warnings,
            scm_semantics_summary=scm_summary,
            method_randomization_summary=method_summary,
            placebo_rank=rank,
            empirical_tail_fraction=tail,
            num_placebo_sets=num_placebo_sets,
        )

    if spec.num_treated_units == 1:
        warnings = (SINGLE_TREATED_WARNING, FALSIFICATION_WARNING)
        return SCMTreatedSetPlaceboIntegrationResult(
            decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC,
            statistic_compatibility=compatibility,
            treated_set_placebo_summary=treated_set_summary,
            scm_semantics_summary=scm_summary,
            method_randomization_summary=method_summary,
            empirical_tail_fraction=tail,
            placebo_rank=rank,
            num_placebo_sets=num_placebo_sets,
            is_candidate=False,
            is_falsification_only=True,
            is_blocked=False,
            warnings=warnings,
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if spec.assignment_role == AssignmentRole.FALSIFICATION_ONLY.value:
        warnings = (FALSIFICATION_WARNING,)
        return SCMTreatedSetPlaceboIntegrationResult(
            decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_FALSIFICATION_DIAGNOSTIC,
            statistic_compatibility=compatibility,
            treated_set_placebo_summary=treated_set_summary,
            scm_semantics_summary=scm_summary,
            method_randomization_summary=method_summary,
            empirical_tail_fraction=tail,
            placebo_rank=rank,
            num_placebo_sets=num_placebo_sets,
            is_candidate=False,
            is_falsification_only=True,
            is_blocked=False,
            warnings=warnings,
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if (
        spec.num_treated_units >= 2
        and spec.assignment_role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
        and scm_semantics.is_design_based_candidate
        and method_result.is_candidate
    ):
        warnings = (CANDIDATE_WARNING,)
        return SCMTreatedSetPlaceboIntegrationResult(
            decision=SCMTreatedSetIntegrationDecision.SCM_TREATED_SET_RANDOMIZATION_CANDIDATE,
            statistic_compatibility=compatibility,
            treated_set_placebo_summary=treated_set_summary,
            scm_semantics_summary=scm_summary,
            method_randomization_summary=method_summary,
            empirical_tail_fraction=tail,
            placebo_rank=rank,
            num_placebo_sets=num_placebo_sets,
            is_candidate=True,
            is_falsification_only=False,
            is_blocked=False,
            warnings=warnings,
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    return _blocked_result(
        spec,
        compatibility=SCMStatisticCompatibility.BLOCKED,
        reasons=("unable to classify SCM treated-set placebo integration decision",),
        scm_semantics_summary=scm_summary,
        method_randomization_summary=method_summary,
        placebo_rank=rank,
        empirical_tail_fraction=tail,
        num_placebo_sets=num_placebo_sets,
    )


def summarize_scm_treated_set_placebo_integration_result(
    result: SCMTreatedSetPlaceboIntegrationResult,
) -> dict[str, Any]:
    """Serialize SCM treated-set placebo integration result for validation archives."""
    return {
        "decision": result.decision.value,
        "statistic_compatibility": result.statistic_compatibility.value,
        "treated_set_placebo_summary": dict(result.treated_set_placebo_summary),
        "scm_semantics_summary": dict(result.scm_semantics_summary),
        "method_randomization_summary": dict(result.method_randomization_summary),
        "empirical_tail_fraction": result.empirical_tail_fraction,
        "placebo_rank": result.placebo_rank,
        "num_placebo_sets": result.num_placebo_sets,
        "is_candidate": result.is_candidate,
        "is_falsification_only": result.is_falsification_only,
        "is_blocked": result.is_blocked,
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


def build_scm_treated_set_placebo_readiness_examples() -> list[dict[str, Any]]:
    """Return illustrative SCM treated-set placebo integration readiness examples."""
    design = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
    falsification = AssignmentRole.FALSIFICATION_ONLY.value
    pseudo = {f"p{i}": 0.1 * i for i in range(1, 6)}

    def _example(
        label: str,
        integration_spec: SCMTreatedSetPlaceboIntegrationSpec,
    ) -> dict[str, Any]:
        result = evaluate_scm_treated_set_placebo_integration(integration_spec)
        return {
            "label": label,
            "decision": result.decision.value,
            "statistic_compatibility": result.statistic_compatibility.value,
            "is_candidate": result.is_candidate,
            "is_falsification_only": result.is_falsification_only,
            "is_blocked": result.is_blocked,
        }

    base_contract = SCMStatisticContract(
        statistic_kind="signed_effect",
        effect_direction="greater",
        statistic_source=SCMStatisticSource.PRECOMPUTED,
        observed_statistic=0.42,
        pseudo_statistic_by_assignment=pseudo,
    )
    return [
        _example(
            "multi_treated_design_based_candidate",
            SCMTreatedSetPlaceboIntegrationSpec(
                num_treated_units=3,
                assignment_role=design,
                assignment_family="complete_randomized_set",
                num_valid_pseudo_assignments=5,
                statistic_contract=base_contract,
            ),
        ),
        _example(
            "falsification_only_diagnostic",
            SCMTreatedSetPlaceboIntegrationSpec(
                num_treated_units=3,
                assignment_role=falsification,
                assignment_family="greedy_matched_market_falsification",
                num_valid_pseudo_assignments=5,
                statistic_contract=base_contract,
            ),
        ),
        _example(
            "single_treated_falsification",
            SCMTreatedSetPlaceboIntegrationSpec(
                num_treated_units=1,
                assignment_role=falsification,
                assignment_family="greedy_matched_market_falsification",
                num_valid_pseudo_assignments=5,
                statistic_contract=base_contract,
            ),
        ),
    ]


__all__ = [
    "CANDIDATE_WARNING",
    "FALSIFICATION_WARNING",
    "SCMStatisticCompatibility",
    "SCMStatisticContract",
    "SCMStatisticSource",
    "SCMTreatedSetIntegrationDecision",
    "SCMTreatedSetPlaceboIntegrationResult",
    "SCMTreatedSetPlaceboIntegrationSpec",
    "build_scm_treated_set_placebo_readiness_examples",
    "evaluate_scm_treated_set_placebo_integration",
    "summarize_scm_treated_set_placebo_integration_result",
    "validate_scm_statistic_contract",
]
