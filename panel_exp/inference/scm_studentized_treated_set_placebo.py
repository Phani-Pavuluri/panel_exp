"""SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001 — SCM studentized treated-set placebo integration.

Connects SCM effect/scale contracts to studentized placebo-rank inference, SCM treated-set
placebo integration, SCM placebo semantics, and method-specific randomization readiness.
Framework-level candidate / diagnostic only — not production inference.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from panel_exp.design.assignment_generators import AssignmentRole
from panel_exp.inference.method_specific_randomization import (
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
from panel_exp.inference.scm_treated_set_placebo import (
    SCMStatisticContract,
    SCMStatisticSource,
    SCMTreatedSetPlaceboIntegrationSpec,
    evaluate_scm_treated_set_placebo_integration,
    summarize_scm_treated_set_placebo_integration_result,
)
from panel_exp.inference.studentized_placebo_rank import (
    ScaleSource,
    StudentizedEffectDirection,
    StudentizedPlaceboRankSpec,
    evaluate_studentized_placebo_rank,
    summarize_studentized_placebo_rank_result,
)

CANDIDATE_WARNING = (
    "Framework-level SCM studentized treated-set candidate only — studentized empirical "
    "tail fraction is not a final production p-value and no causal confidence interval "
    "is authorized."
)

FALSIFICATION_WARNING = (
    "Not design-based causal inference — SCM studentized placebo rank is diagnostic only; "
    "studentized empirical tail fraction is not a final production p-value."
)

SINGLE_TREATED_WARNING = (
    "SCM single-treated placebo is null-monitor/falsification only — not multi-treated "
    "studentized treated-set inference."
)

SUPPORTED_DIRECTIONS = frozenset({"greater", "less", "two_sided"})

DESIGN_ROLE = AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value
FALSIFICATION_ROLE = AssignmentRole.FALSIFICATION_ONLY.value


class SCMStudentizedIntegrationDecision(str, Enum):
    SCM_STUDENTIZED_TREATED_SET_CANDIDATE = "scm_studentized_treated_set_candidate"
    SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY = "scm_studentized_treated_set_diagnostic_only"
    SCM_STUDENTIZED_TREATED_SET_BLOCKED = "scm_studentized_treated_set_blocked"


class SCMStudentizedStatisticSource(str, Enum):
    PRECOMPUTED = "precomputed"
    SCM_ADAPTER_OUTPUT = "scm_adapter_output"
    UNKNOWN = "unknown"


class SCMStudentizedCompatibility(str, Enum):
    COMPATIBLE = "compatible"
    MISSING_EFFECT = "missing_effect"
    MISSING_SCALE = "missing_scale"
    MISSING_PSEUDO_EFFECTS = "missing_pseudo_effects"
    MISSING_PSEUDO_SCALES = "missing_pseudo_scales"
    EFFECT_SCALE_ASSIGNMENT_MISMATCH = "effect_scale_assignment_mismatch"
    NON_NUMERIC_EFFECT = "non_numeric_effect"
    NON_NUMERIC_SCALE = "non_numeric_scale"
    NON_POSITIVE_SCALE = "non_positive_scale"
    STATISTIC_CONTRACT_MISMATCH = "statistic_contract_mismatch"
    INSUFFICIENT_PLACEBO_SETS = "insufficient_placebo_sets"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SCMStudentizedStatisticContract:
    observed_effect: float | None
    pseudo_effect_by_assignment: Mapping[str, float]
    observed_scale: float | None
    pseudo_scale_by_assignment: Mapping[str, float]
    effect_direction: str
    scale_source: str
    statistic_source: SCMStudentizedStatisticSource
    null_value: float = 0.0
    statistic_kind: str = "studentized_effect"
    same_effect_definition_observed_and_pseudo: bool = True
    same_scale_definition_observed_and_pseudo: bool = True


@dataclass(frozen=True)
class SCMStudentizedTreatedSetPlaceboSpec:
    num_treated_units: int
    assignment_role: str
    assignment_family: str | None
    num_valid_pseudo_assignments: int
    statistic_contract: SCMStudentizedStatisticContract
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
class SCMStudentizedTreatedSetPlaceboResult:
    decision: SCMStudentizedIntegrationDecision
    compatibility: SCMStudentizedCompatibility
    studentized_rank_summary: Mapping[str, object]
    scm_treated_set_summary: Mapping[str, object]
    scm_semantics_summary: Mapping[str, object]
    method_randomization_summary: Mapping[str, object]
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


def _map_scale_source(scale_source: str) -> ScaleSource:
    mapping = {
        "provided_standard_error": ScaleSource.PROVIDED_STANDARD_ERROR,
        "provided_standard_deviation": ScaleSource.PROVIDED_STANDARD_DEVIATION,
        "provided_dispersion": ScaleSource.PROVIDED_DISPERSION,
        "placebo_dispersion": ScaleSource.PLACEBO_DISPERSION,
    }
    return mapping.get(scale_source.lower(), ScaleSource.PROVIDED_STANDARD_ERROR)


def _map_effect_direction(direction: str) -> StudentizedEffectDirection | None:
    try:
        return StudentizedEffectDirection(direction.lower())
    except ValueError:
        return None


def _blocked_result(
    spec: SCMStudentizedTreatedSetPlaceboSpec,
    *,
    compatibility: SCMStudentizedCompatibility,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    studentized_summary: Mapping[str, object] | None = None,
    scm_treated_set_summary: Mapping[str, object] | None = None,
    scm_semantics_summary: Mapping[str, object] | None = None,
    method_randomization_summary: Mapping[str, object] | None = None,
    observed_studentized: float | None = None,
    pseudo_studentized: Mapping[str, float] | None = None,
    placebo_rank: int | None = None,
    empirical_tail_fraction: float | None = None,
    num_placebo_sets: int = 0,
) -> SCMStudentizedTreatedSetPlaceboResult:
    return SCMStudentizedTreatedSetPlaceboResult(
        decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_BLOCKED,
        compatibility=compatibility,
        studentized_rank_summary=dict(studentized_summary or {}),
        scm_treated_set_summary=dict(scm_treated_set_summary or {}),
        scm_semantics_summary=dict(scm_semantics_summary or {}),
        method_randomization_summary=dict(method_randomization_summary or {}),
        observed_studentized_statistic=observed_studentized,
        pseudo_studentized_statistic_by_assignment=dict(pseudo_studentized or {}),
        placebo_rank=placebo_rank,
        empirical_tail_fraction=empirical_tail_fraction,
        num_placebo_sets=num_placebo_sets,
        is_candidate=False,
        is_diagnostic_only=False,
        is_blocked=True,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def _platform_overclaim_block(
    spec: SCMStudentizedTreatedSetPlaceboSpec,
) -> SCMStudentizedTreatedSetPlaceboResult | None:
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
            return _blocked_result(spec, compatibility=SCMStudentizedCompatibility.BLOCKED, reasons=(msg,))
    return None


def validate_scm_studentized_statistic_contract(
    contract: SCMStudentizedStatisticContract,
    min_placebo_sets: int = 10,
) -> SCMStudentizedCompatibility:
    """Validate SCM effect/scale contract for studentized treated-set placebo integration."""
    if contract.effect_direction.lower() not in SUPPORTED_DIRECTIONS:
        return SCMStudentizedCompatibility.STATISTIC_CONTRACT_MISMATCH

    if not contract.same_effect_definition_observed_and_pseudo:
        return SCMStudentizedCompatibility.STATISTIC_CONTRACT_MISMATCH

    if not contract.same_scale_definition_observed_and_pseudo:
        return SCMStudentizedCompatibility.STATISTIC_CONTRACT_MISMATCH

    if contract.observed_effect is None:
        return SCMStudentizedCompatibility.MISSING_EFFECT

    if not _is_finite(contract.observed_effect):
        return SCMStudentizedCompatibility.NON_NUMERIC_EFFECT

    if contract.observed_scale is None:
        return SCMStudentizedCompatibility.MISSING_SCALE

    if not _is_finite(contract.observed_scale):
        return SCMStudentizedCompatibility.NON_NUMERIC_SCALE

    if float(contract.observed_scale) <= 0:
        return SCMStudentizedCompatibility.NON_POSITIVE_SCALE

    pseudo_effects = contract.pseudo_effect_by_assignment
    pseudo_scales = contract.pseudo_scale_by_assignment

    if not pseudo_effects:
        return SCMStudentizedCompatibility.MISSING_PSEUDO_EFFECTS

    if not pseudo_scales:
        return SCMStudentizedCompatibility.MISSING_PSEUDO_SCALES

    if set(pseudo_effects) != set(pseudo_scales):
        return SCMStudentizedCompatibility.EFFECT_SCALE_ASSIGNMENT_MISMATCH

    if len(pseudo_effects) < min_placebo_sets:
        return SCMStudentizedCompatibility.INSUFFICIENT_PLACEBO_SETS

    for assignment_id in pseudo_effects:
        effect = pseudo_effects[assignment_id]
        scale = pseudo_scales.get(assignment_id)
        if not _is_finite(effect):
            return SCMStudentizedCompatibility.NON_NUMERIC_EFFECT
        if scale is None:
            return SCMStudentizedCompatibility.MISSING_PSEUDO_SCALES
        if not _is_finite(scale):
            return SCMStudentizedCompatibility.NON_NUMERIC_SCALE
        if float(scale) <= 0:
            return SCMStudentizedCompatibility.NON_POSITIVE_SCALE

    return SCMStudentizedCompatibility.COMPATIBLE


def _build_studentized_spec(spec: SCMStudentizedTreatedSetPlaceboSpec) -> StudentizedPlaceboRankSpec:
    contract = spec.statistic_contract
    direction = _map_effect_direction(contract.effect_direction)
    assert direction is not None
    return StudentizedPlaceboRankSpec(
        observed_effect=float(contract.observed_effect),  # type: ignore[arg-type]
        pseudo_effect_by_assignment=dict(contract.pseudo_effect_by_assignment),
        observed_scale=contract.observed_scale,
        pseudo_scale_by_assignment=dict(contract.pseudo_scale_by_assignment),
        effect_direction=direction,
        scale_source=_map_scale_source(contract.scale_source),
        null_value=contract.null_value,
        assignment_role=spec.assignment_role,
        min_placebo_sets=spec.min_placebo_sets,
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


def _build_scm_treated_set_spec(spec: SCMStudentizedTreatedSetPlaceboSpec) -> SCMTreatedSetPlaceboIntegrationSpec:
    contract = spec.statistic_contract
    raw_contract = SCMStatisticContract(
        statistic_kind="signed_effect",
        effect_direction=contract.effect_direction,
        statistic_source=SCMStatisticSource.PRECOMPUTED,
        observed_statistic=contract.observed_effect,
        pseudo_statistic_by_assignment=dict(contract.pseudo_effect_by_assignment),
        same_statistic_observed_and_pseudo=contract.same_effect_definition_observed_and_pseudo,
    )
    return SCMTreatedSetPlaceboIntegrationSpec(
        num_treated_units=spec.num_treated_units,
        assignment_role=spec.assignment_role,
        assignment_family=spec.assignment_family,
        num_valid_pseudo_assignments=spec.num_valid_pseudo_assignments,
        statistic_contract=raw_contract,
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


def _build_scm_semantics_spec(spec: SCMStudentizedTreatedSetPlaceboSpec) -> SCMPlaceboSemanticsSpec:
    use_case = (
        SCMPlaceboUseCase.SINGLE_TREATED_PLACEBO
        if spec.num_treated_units == 1
        else SCMPlaceboUseCase.MULTI_TREATED_SET_PLACEBO
    )
    return SCMPlaceboSemanticsSpec(
        use_case=use_case,
        num_treated_units=spec.num_treated_units,
        assignment_role=spec.assignment_role,
        assignment_family=spec.assignment_family,
        has_valid_pseudo_assignments=spec.num_valid_pseudo_assignments >= spec.min_placebo_sets,
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
    spec: SCMStudentizedTreatedSetPlaceboSpec,
    *,
    compatibility: SCMStudentizedCompatibility,
) -> MethodRandomizationValidationSpec:
    contract = spec.statistic_contract
    geometry = (
        MethodGeometry.SINGLE_TREATED
        if spec.num_treated_units == 1
        else MethodGeometry.MULTI_TREATED_SET
    )
    has_observed = compatibility != SCMStudentizedCompatibility.MISSING_EFFECT
    has_pseudo = compatibility not in {
        SCMStudentizedCompatibility.MISSING_PSEUDO_EFFECTS,
        SCMStudentizedCompatibility.MISSING_EFFECT,
    }
    return MethodRandomizationValidationSpec(
        method_family=MethodFamily.SCM,
        statistic_kind=MethodStatisticKind.STUDENTIZED_EFFECT,
        geometry=geometry,
        assignment_role=spec.assignment_role,
        num_treated_units=spec.num_treated_units,
        num_valid_pseudo_assignments=spec.num_valid_pseudo_assignments,
        has_observed_statistic=has_observed,
        has_pseudo_statistics=has_pseudo and bool(contract.pseudo_effect_by_assignment),
        uses_same_statistic_observed_and_pseudo=contract.same_effect_definition_observed_and_pseudo,
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


def evaluate_scm_studentized_treated_set_placebo(
    spec: SCMStudentizedTreatedSetPlaceboSpec,
) -> SCMStudentizedTreatedSetPlaceboResult:
    """Evaluate SCM studentized treated-set placebo integration across framework layers."""
    platform_block = _platform_overclaim_block(spec)
    if platform_block is not None:
        return platform_block

    if spec.assignment_role == AssignmentRole.BLOCKED.value or spec.assignment_role not in {
        DESIGN_ROLE,
        FALSIFICATION_ROLE,
    }:
        return _blocked_result(
            spec,
            compatibility=SCMStudentizedCompatibility.BLOCKED,
            reasons=(f"assignment role blocked or unknown: {spec.assignment_role}",),
        )

    compatibility = validate_scm_studentized_statistic_contract(
        spec.statistic_contract,
        min_placebo_sets=spec.min_placebo_sets,
    )
    if compatibility != SCMStudentizedCompatibility.COMPATIBLE:
        return _blocked_result(
            spec,
            compatibility=compatibility,
            reasons=(f"SCM studentized contract not compatible: {compatibility.value}",),
        )

    if spec.num_valid_pseudo_assignments < spec.min_placebo_sets:
        return _blocked_result(
            spec,
            compatibility=SCMStudentizedCompatibility.INSUFFICIENT_PLACEBO_SETS,
            reasons=(
                f"insufficient pseudo assignments: {spec.num_valid_pseudo_assignments} "
                f"< {spec.min_placebo_sets}",
            ),
        )

    studentized_result = evaluate_studentized_placebo_rank(_build_studentized_spec(spec))
    studentized_summary = summarize_studentized_placebo_rank_result(studentized_result)

    scm_treated_set_result = evaluate_scm_treated_set_placebo_integration(
        _build_scm_treated_set_spec(spec)
    )
    scm_treated_set_summary = summarize_scm_treated_set_placebo_integration_result(
        scm_treated_set_result
    )

    scm_semantics = classify_scm_placebo_semantics(_build_scm_semantics_spec(spec))
    scm_semantics_summary = summarize_scm_placebo_semantics_result(scm_semantics)

    method_result = validate_method_randomization_inference(
        _build_method_randomization_spec(spec, compatibility=compatibility)
    )
    method_summary = summarize_method_randomization_result(method_result)

    if studentized_result.is_blocked:
        return _blocked_result(
            spec,
            compatibility=SCMStudentizedCompatibility.BLOCKED,
            reasons=tuple(studentized_result.blocked_reasons)
            or ("studentized placebo-rank evaluation blocked",),
            warnings=studentized_result.warnings,
            studentized_summary=studentized_summary,
            scm_treated_set_summary=scm_treated_set_summary,
            scm_semantics_summary=scm_semantics_summary,
            method_randomization_summary=method_summary,
            observed_studentized=studentized_result.observed_studentized_statistic,
            pseudo_studentized=studentized_result.pseudo_studentized_statistic_by_assignment,
            placebo_rank=studentized_result.placebo_rank,
            empirical_tail_fraction=studentized_result.empirical_tail_fraction,
            num_placebo_sets=studentized_result.num_placebo_sets,
        )

    if scm_semantics.is_blocked or scm_treated_set_result.is_blocked:
        reasons = tuple(scm_semantics.blocked_reasons) + tuple(scm_treated_set_result.blocked_reasons)
        if not reasons:
            reasons = ("SCM semantics or treated-set integration blocked studentized path",)
        return _blocked_result(
            spec,
            compatibility=SCMStudentizedCompatibility.BLOCKED,
            reasons=reasons,
            warnings=scm_semantics.warnings + scm_treated_set_result.warnings,
            studentized_summary=studentized_summary,
            scm_treated_set_summary=scm_treated_set_summary,
            scm_semantics_summary=scm_semantics_summary,
            method_randomization_summary=method_summary,
            observed_studentized=studentized_result.observed_studentized_statistic,
            pseudo_studentized=studentized_result.pseudo_studentized_statistic_by_assignment,
            placebo_rank=studentized_result.placebo_rank,
            empirical_tail_fraction=studentized_result.empirical_tail_fraction,
            num_placebo_sets=studentized_result.num_placebo_sets,
        )

    base_fields = dict(
        compatibility=compatibility,
        studentized_rank_summary=studentized_summary,
        scm_treated_set_summary=scm_treated_set_summary,
        scm_semantics_summary=scm_semantics_summary,
        method_randomization_summary=method_summary,
        observed_studentized_statistic=studentized_result.observed_studentized_statistic,
        pseudo_studentized_statistic_by_assignment=studentized_result.pseudo_studentized_statistic_by_assignment,
        placebo_rank=studentized_result.placebo_rank,
        empirical_tail_fraction=studentized_result.empirical_tail_fraction,
        num_placebo_sets=studentized_result.num_placebo_sets,
        governance_flags=_governance_flags(),
        blocked_reasons=(),
    )

    if spec.num_treated_units == 1:
        return SCMStudentizedTreatedSetPlaceboResult(
            decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY,
            is_candidate=False,
            is_diagnostic_only=True,
            is_blocked=False,
            warnings=(SINGLE_TREATED_WARNING, FALSIFICATION_WARNING),
            **base_fields,
        )

    if spec.assignment_role == FALSIFICATION_ROLE:
        return SCMStudentizedTreatedSetPlaceboResult(
            decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_DIAGNOSTIC_ONLY,
            is_candidate=False,
            is_diagnostic_only=True,
            is_blocked=False,
            warnings=(FALSIFICATION_WARNING,),
            **base_fields,
        )

    if (
        spec.num_treated_units >= 2
        and spec.assignment_role == DESIGN_ROLE
        and studentized_result.is_candidate
        and scm_semantics.is_design_based_candidate
        and method_result.is_candidate
    ):
        return SCMStudentizedTreatedSetPlaceboResult(
            decision=SCMStudentizedIntegrationDecision.SCM_STUDENTIZED_TREATED_SET_CANDIDATE,
            is_candidate=True,
            is_diagnostic_only=False,
            is_blocked=False,
            warnings=(CANDIDATE_WARNING,),
            **base_fields,
        )

    return _blocked_result(
        spec,
        compatibility=SCMStudentizedCompatibility.BLOCKED,
        reasons=("unable to classify SCM studentized treated-set placebo decision",),
        studentized_summary=studentized_summary,
        scm_treated_set_summary=scm_treated_set_summary,
        scm_semantics_summary=scm_semantics_summary,
        method_randomization_summary=method_summary,
        observed_studentized=studentized_result.observed_studentized_statistic,
        pseudo_studentized=studentized_result.pseudo_studentized_statistic_by_assignment,
        placebo_rank=studentized_result.placebo_rank,
        empirical_tail_fraction=studentized_result.empirical_tail_fraction,
        num_placebo_sets=studentized_result.num_placebo_sets,
    )


def summarize_scm_studentized_treated_set_placebo_result(
    result: SCMStudentizedTreatedSetPlaceboResult,
) -> dict[str, Any]:
    """Serialize SCM studentized treated-set placebo result for validation archives."""
    return {
        "decision": result.decision.value,
        "compatibility": result.compatibility.value,
        "studentized_rank_summary": dict(result.studentized_rank_summary),
        "scm_treated_set_summary": dict(result.scm_treated_set_summary),
        "scm_semantics_summary": dict(result.scm_semantics_summary),
        "method_randomization_summary": dict(result.method_randomization_summary),
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


def build_scm_studentized_readiness_examples() -> list[dict[str, Any]]:
    """Return illustrative SCM studentized treated-set placebo readiness examples."""
    effects = {f"p{i}": 0.1 * i for i in range(1, 11)}
    scales = {k: 1.0 for k in effects}

    def _example(label: str, integration_spec: SCMStudentizedTreatedSetPlaceboSpec) -> dict[str, Any]:
        result = evaluate_scm_studentized_treated_set_placebo(integration_spec)
        return {
            "label": label,
            "decision": result.decision.value,
            "compatibility": result.compatibility.value,
            "is_candidate": result.is_candidate,
            "is_diagnostic_only": result.is_diagnostic_only,
            "is_blocked": result.is_blocked,
        }

    base_contract = SCMStudentizedStatisticContract(
        observed_effect=1.05,
        pseudo_effect_by_assignment=effects,
        observed_scale=1.0,
        pseudo_scale_by_assignment=scales,
        effect_direction="greater",
        scale_source="provided_standard_error",
        statistic_source=SCMStudentizedStatisticSource.PRECOMPUTED,
    )
    return [
        _example(
            "multi_treated_design_based_candidate",
            SCMStudentizedTreatedSetPlaceboSpec(
                num_treated_units=3,
                assignment_role=DESIGN_ROLE,
                assignment_family="complete_randomized_set",
                num_valid_pseudo_assignments=10,
                statistic_contract=base_contract,
            ),
        ),
        _example(
            "falsification_only_diagnostic",
            SCMStudentizedTreatedSetPlaceboSpec(
                num_treated_units=3,
                assignment_role=FALSIFICATION_ROLE,
                assignment_family="greedy_matched_market_falsification",
                num_valid_pseudo_assignments=10,
                statistic_contract=base_contract,
            ),
        ),
    ]


__all__ = [
    "CANDIDATE_WARNING",
    "FALSIFICATION_WARNING",
    "SCMStudentizedCompatibility",
    "SCMStudentizedIntegrationDecision",
    "SCMStudentizedStatisticContract",
    "SCMStudentizedStatisticSource",
    "SCMStudentizedTreatedSetPlaceboResult",
    "SCMStudentizedTreatedSetPlaceboSpec",
    "build_scm_studentized_readiness_examples",
    "evaluate_scm_studentized_treated_set_placebo",
    "summarize_scm_studentized_treated_set_placebo_result",
    "validate_scm_studentized_statistic_contract",
]
