"""AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001 — AugSynth point randomization integration.

Connects precomputed AugSynth point statistics to design-aware assignment roles,
treated-set placebo rank/tail diagnostics, and method-specific randomization readiness.
Statistic-first — no AugSynth fitting. AugSynth JK remains diagnostic-only.
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
from panel_exp.inference.treated_set_placebo import (
    PlaceboSemanticRole,
    compute_placebo_rank,
)

CANDIDATE_WARNING = (
    "AugSynth point randomization framework-level candidate only — empirical tail fraction "
    "is not a final production p-value and no causal confidence interval is authorized."
)

JK_DIAGNOSTIC_WARNING = (
    "AugSynth JK remains diagnostic-only / characterized-only — not production inference."
)

JK_NOT_AUTHORIZED_WARNING = (
    "AugSynth point randomization does not authorize AugSynth JK production inference."
)

FALSIFICATION_WARNING = (
    "Not design-based causal inference — falsification diagnostic only; "
    "empirical tail fraction is not a final production p-value."
)


class AugSynthStatisticKind(str, Enum):
    POINT_EFFECT = "point_effect"
    RELATIVE_POINT_EFFECT = "relative_point_effect"
    STUDENTIZED_POINT_EFFECT = "studentized_point_effect"
    JACKKNIFE_EFFECT = "jackknife_effect"
    UNKNOWN = "unknown"


class AugSynthInferenceMode(str, Enum):
    POINT_ONLY = "point_only"
    JACKKNIFE = "jackknife"
    PLACEBO_RANK = "placebo_rank"
    STUDENTIZED_PLACEBO_RANK = "studentized_placebo_rank"
    UNKNOWN = "unknown"


class AugSynthRandomizationDecision(str, Enum):
    AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE = "augsynth_point_randomization_candidate"
    AUGSYNTH_POINT_DIAGNOSTIC_ONLY = "augsynth_point_diagnostic_only"
    AUGSYNTH_JK_DIAGNOSTIC_ONLY = "augsynth_jk_diagnostic_only"
    AUGSYNTH_RANDOMIZATION_BLOCKED = "augsynth_randomization_blocked"


class AugSynthCompatibility(str, Enum):
    COMPATIBLE = "compatible"
    MISSING_OBSERVED_STATISTIC = "missing_observed_statistic"
    MISSING_PSEUDO_STATISTICS = "missing_pseudo_statistics"
    STATISTIC_KIND_BLOCKED = "statistic_kind_blocked"
    STATISTIC_DEFINITION_MISMATCH = "statistic_definition_mismatch"
    ESTIMAND_MISMATCH = "estimand_mismatch"
    OUTCOME_SCALE_MISMATCH = "outcome_scale_mismatch"
    TIME_WINDOW_MISMATCH = "time_window_mismatch"
    DONOR_ELIGIBILITY_MISMATCH = "donor_eligibility_mismatch"
    AUGMENTATION_CONFIG_MISMATCH = "augmentation_config_mismatch"
    NON_NUMERIC_STATISTIC = "non_numeric_statistic"
    INSUFFICIENT_PSEUDO_ASSIGNMENTS = "insufficient_pseudo_assignments"
    BLOCKED = "blocked"


SUPPORTED_STATISTIC_KINDS = frozenset(
    {
        AugSynthStatisticKind.POINT_EFFECT,
        AugSynthStatisticKind.RELATIVE_POINT_EFFECT,
        AugSynthStatisticKind.STUDENTIZED_POINT_EFFECT,
    }
)

SUPPORTED_INFERENCE_MODES = frozenset(
    {
        AugSynthInferenceMode.POINT_ONLY,
        AugSynthInferenceMode.PLACEBO_RANK,
        AugSynthInferenceMode.STUDENTIZED_PLACEBO_RANK,
    }
)

SUPPORTED_EFFECT_DIRECTIONS = frozenset({"greater", "less", "two_sided"})


@dataclass(frozen=True)
class AugSynthPointStatisticContract:
    observed_statistic: float | None
    pseudo_statistic_by_assignment: Mapping[str, float]
    statistic_kind: AugSynthStatisticKind
    inference_mode: AugSynthInferenceMode
    effect_direction: str
    estimand_id: str
    outcome_scale: str
    pre_period_id: str
    post_period_id: str
    donor_eligibility_rule_id: str
    augmentation_config_id: str
    same_statistic_definition_observed_and_pseudo: bool = True
    same_estimand_observed_and_pseudo: bool = True
    same_outcome_scale_observed_and_pseudo: bool = True
    same_time_window_observed_and_pseudo: bool = True
    same_donor_eligibility_observed_and_pseudo: bool = True
    same_augmentation_config_observed_and_pseudo: bool = True


@dataclass(frozen=True)
class AugSynthPointRandomizationSpec:
    assignment_role: str
    assignment_family: str | None
    num_treated_units: int
    num_valid_pseudo_assignments: int
    statistic_contract: AugSynthPointStatisticContract
    min_pseudo_assignments: int = 10
    requested_final_p_value: bool = False
    requested_causal_interval: bool = False
    requested_jackknife_production_inference: bool = False
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
class AugSynthPointRandomizationResult:
    decision: AugSynthRandomizationDecision
    compatibility: AugSynthCompatibility
    treated_set_placebo_summary: Mapping[str, object]
    method_randomization_summary: Mapping[str, object]
    observed_statistic: float | None
    pseudo_statistic_by_assignment: Mapping[str, float]
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
        "augsynth_jk_authorized": False,
    }


def _is_finite_numeric(value: float | None) -> bool:
    if value is None:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _method_statistic_kind(kind: AugSynthStatisticKind) -> MethodStatisticKind:
    mapping = {
        AugSynthStatisticKind.POINT_EFFECT: MethodStatisticKind.ABSOLUTE_EFFECT,
        AugSynthStatisticKind.RELATIVE_POINT_EFFECT: MethodStatisticKind.RELATIVE_EFFECT,
        AugSynthStatisticKind.STUDENTIZED_POINT_EFFECT: MethodStatisticKind.STUDENTIZED_EFFECT,
        AugSynthStatisticKind.JACKKNIFE_EFFECT: MethodStatisticKind.JACKKNIFE_INTERVAL,
    }
    return mapping.get(kind, MethodStatisticKind.UNKNOWN)


def _placebo_semantic_role(assignment_role: str) -> PlaceboSemanticRole:
    if assignment_role == AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value:
        return PlaceboSemanticRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE
    if assignment_role == AssignmentRole.FALSIFICATION_ONLY.value:
        return PlaceboSemanticRole.FALSIFICATION_DIAGNOSTIC
    return PlaceboSemanticRole.BLOCKED


def _blocked_result(
    spec: AugSynthPointRandomizationSpec,
    *,
    compatibility: AugSynthCompatibility,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    method_randomization_summary: Mapping[str, object] | None = None,
    placebo_rank: int | None = None,
    empirical_tail_fraction: float | None = None,
    num_placebo_sets: int = 0,
) -> AugSynthPointRandomizationResult:
    contract = spec.statistic_contract
    return AugSynthPointRandomizationResult(
        decision=AugSynthRandomizationDecision.AUGSYNTH_RANDOMIZATION_BLOCKED,
        compatibility=compatibility,
        treated_set_placebo_summary={
            "semantic_role": _placebo_semantic_role(spec.assignment_role).value,
            "placebo_rank": placebo_rank,
            "empirical_tail_fraction": empirical_tail_fraction,
            "num_valid_placebo_sets": num_placebo_sets,
            "framework_tail_fraction_label": "not_production_p_value",
        },
        method_randomization_summary=dict(method_randomization_summary or {}),
        observed_statistic=contract.observed_statistic,
        pseudo_statistic_by_assignment=dict(contract.pseudo_statistic_by_assignment),
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


def validate_augsynth_point_statistic_contract(
    contract: AugSynthPointStatisticContract,
    min_pseudo_assignments: int = 10,
) -> AugSynthCompatibility:
    """Validate AugSynth observed/pseudo point statistic contract."""
    if contract.statistic_kind in {
        AugSynthStatisticKind.JACKKNIFE_EFFECT,
        AugSynthStatisticKind.UNKNOWN,
    }:
        return AugSynthCompatibility.STATISTIC_KIND_BLOCKED

    if contract.inference_mode == AugSynthInferenceMode.UNKNOWN:
        return AugSynthCompatibility.BLOCKED

    if not contract.same_statistic_definition_observed_and_pseudo:
        return AugSynthCompatibility.STATISTIC_DEFINITION_MISMATCH

    if not contract.same_estimand_observed_and_pseudo:
        return AugSynthCompatibility.ESTIMAND_MISMATCH

    if not contract.same_outcome_scale_observed_and_pseudo:
        return AugSynthCompatibility.OUTCOME_SCALE_MISMATCH

    if not contract.same_time_window_observed_and_pseudo:
        return AugSynthCompatibility.TIME_WINDOW_MISMATCH

    if not contract.same_donor_eligibility_observed_and_pseudo:
        return AugSynthCompatibility.DONOR_ELIGIBILITY_MISMATCH

    if not contract.same_augmentation_config_observed_and_pseudo:
        return AugSynthCompatibility.AUGMENTATION_CONFIG_MISMATCH

    if contract.observed_statistic is None:
        return AugSynthCompatibility.MISSING_OBSERVED_STATISTIC

    if not _is_finite_numeric(contract.observed_statistic):
        return AugSynthCompatibility.NON_NUMERIC_STATISTIC

    pseudo_map = contract.pseudo_statistic_by_assignment
    if not pseudo_map:
        return AugSynthCompatibility.MISSING_PSEUDO_STATISTICS

    if len(pseudo_map) < min_pseudo_assignments:
        return AugSynthCompatibility.INSUFFICIENT_PSEUDO_ASSIGNMENTS

    for value in pseudo_map.values():
        if not _is_finite_numeric(value):
            return AugSynthCompatibility.NON_NUMERIC_STATISTIC

    return AugSynthCompatibility.COMPATIBLE


def _platform_overclaim_block(
    spec: AugSynthPointRandomizationSpec,
) -> AugSynthPointRandomizationResult | None:
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
                compatibility=AugSynthCompatibility.BLOCKED,
                reasons=(msg,),
            )
    return None


def _inference_overclaim_block(
    spec: AugSynthPointRandomizationSpec,
) -> AugSynthPointRandomizationResult | None:
    reasons: list[str] = []
    if spec.requested_final_p_value:
        reasons.append("final production p-value semantics are blocked")
    if spec.requested_causal_interval:
        reasons.append("causal confidence interval semantics are blocked")
    if reasons:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.BLOCKED,
            reasons=tuple(reasons),
        )
    return None


def _build_method_randomization_spec(
    spec: AugSynthPointRandomizationSpec,
    *,
    compatibility: AugSynthCompatibility,
) -> MethodRandomizationValidationSpec:
    contract = spec.statistic_contract
    geometry = (
        MethodGeometry.SINGLE_TREATED
        if spec.num_treated_units == 1
        else MethodGeometry.MULTI_TREATED_SET
    )
    has_observed = compatibility != AugSynthCompatibility.MISSING_OBSERVED_STATISTIC
    has_pseudo = compatibility not in {
        AugSynthCompatibility.MISSING_PSEUDO_STATISTICS,
        AugSynthCompatibility.MISSING_OBSERVED_STATISTIC,
        AugSynthCompatibility.INSUFFICIENT_PSEUDO_ASSIGNMENTS,
    }
    return MethodRandomizationValidationSpec(
        method_family=MethodFamily.AUGSYNTH_CVXPY,
        statistic_kind=_method_statistic_kind(contract.statistic_kind),
        geometry=geometry,
        assignment_role=spec.assignment_role,
        num_treated_units=spec.num_treated_units,
        num_valid_pseudo_assignments=spec.num_valid_pseudo_assignments,
        has_observed_statistic=has_observed,
        has_pseudo_statistics=has_pseudo and bool(contract.pseudo_statistic_by_assignment),
        uses_same_statistic_observed_and_pseudo=contract.same_statistic_definition_observed_and_pseudo,
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
    spec: AugSynthPointRandomizationSpec,
) -> tuple[int | None, float | None, int]:
    contract = spec.statistic_contract
    pseudo_stats = [float(v) for v in contract.pseudo_statistic_by_assignment.values()]
    rank, tail = compute_placebo_rank(
        float(contract.observed_statistic),  # type: ignore[arg-type]
        pseudo_stats,
        contract.effect_direction,
    )
    return rank, tail, len(pseudo_stats)


def evaluate_augsynth_point_randomization(
    spec: AugSynthPointRandomizationSpec,
) -> AugSynthPointRandomizationResult:
    """Evaluate AugSynth point randomization integration across framework layers."""
    platform_block = _platform_overclaim_block(spec)
    if platform_block is not None:
        return platform_block

    inference_block = _inference_overclaim_block(spec)
    if inference_block is not None:
        return inference_block

    contract = spec.statistic_contract

    if spec.requested_jackknife_production_inference:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.STATISTIC_KIND_BLOCKED,
            reasons=("AugSynth JK production inference is not authorized",),
            warnings=(JK_DIAGNOSTIC_WARNING,),
        )

    if (
        contract.statistic_kind == AugSynthStatisticKind.JACKKNIFE_EFFECT
        or contract.inference_mode == AugSynthInferenceMode.JACKKNIFE
    ):
        method_summary = summarize_method_randomization_result(
            validate_method_randomization_inference(
                _build_method_randomization_spec(
                    spec,
                    compatibility=AugSynthCompatibility.STATISTIC_KIND_BLOCKED,
                )
            )
        )
        return AugSynthPointRandomizationResult(
            decision=AugSynthRandomizationDecision.AUGSYNTH_JK_DIAGNOSTIC_ONLY,
            compatibility=AugSynthCompatibility.STATISTIC_KIND_BLOCKED,
            treated_set_placebo_summary={
                "semantic_role": _placebo_semantic_role(spec.assignment_role).value,
                "framework_tail_fraction_label": "not_production_p_value",
            },
            method_randomization_summary=method_summary,
            observed_statistic=contract.observed_statistic,
            pseudo_statistic_by_assignment=dict(contract.pseudo_statistic_by_assignment),
            placebo_rank=None,
            empirical_tail_fraction=None,
            num_placebo_sets=len(contract.pseudo_statistic_by_assignment),
            is_candidate=False,
            is_diagnostic_only=True,
            is_blocked=False,
            warnings=(JK_DIAGNOSTIC_WARNING, JK_NOT_AUTHORIZED_WARNING),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if spec.assignment_role == AssignmentRole.BLOCKED.value or not spec.assignment_role:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.BLOCKED,
            reasons=(f"assignment role blocked: {spec.assignment_role}",),
        )

    if contract.inference_mode not in SUPPORTED_INFERENCE_MODES:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.BLOCKED,
            reasons=(f"unsupported inference mode: {contract.inference_mode.value}",),
        )

    if contract.statistic_kind not in SUPPORTED_STATISTIC_KINDS:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.STATISTIC_KIND_BLOCKED,
            reasons=(f"unsupported statistic kind: {contract.statistic_kind.value}",),
        )

    compatibility = validate_augsynth_point_statistic_contract(
        contract,
        min_pseudo_assignments=spec.min_pseudo_assignments,
    )
    if compatibility != AugSynthCompatibility.COMPATIBLE:
        return _blocked_result(
            spec,
            compatibility=compatibility,
            reasons=(f"statistic contract not compatible: {compatibility.value}",),
        )

    if contract.effect_direction.lower() not in SUPPORTED_EFFECT_DIRECTIONS:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.BLOCKED,
            reasons=(f"invalid effect direction: {contract.effect_direction}",),
        )

    if spec.num_treated_units < 1:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.BLOCKED,
            reasons=("num_treated_units must be >= 1",),
        )

    if spec.num_valid_pseudo_assignments < spec.min_pseudo_assignments:
        return _blocked_result(
            spec,
            compatibility=AugSynthCompatibility.INSUFFICIENT_PSEUDO_ASSIGNMENTS,
            reasons=(
                f"insufficient valid pseudo assignments: {spec.num_valid_pseudo_assignments} "
                f"< {spec.min_pseudo_assignments}",
            ),
        )

    placebo_rank, empirical_tail_fraction, num_placebo_sets = _compute_placebo_diagnostics(spec)
    method_result = validate_method_randomization_inference(
        _build_method_randomization_spec(spec, compatibility=compatibility)
    )
    method_summary = summarize_method_randomization_result(method_result)

    placebo_summary = {
        "semantic_role": _placebo_semantic_role(spec.assignment_role).value,
        "placebo_rank": placebo_rank,
        "empirical_tail_fraction": empirical_tail_fraction,
        "num_valid_placebo_sets": num_placebo_sets,
        "framework_tail_fraction_label": "not_production_p_value",
    }

    if spec.assignment_role == AssignmentRole.FALSIFICATION_ONLY.value:
        return AugSynthPointRandomizationResult(
            decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_DIAGNOSTIC_ONLY,
            compatibility=compatibility,
            treated_set_placebo_summary=placebo_summary,
            method_randomization_summary=method_summary,
            observed_statistic=contract.observed_statistic,
            pseudo_statistic_by_assignment=dict(contract.pseudo_statistic_by_assignment),
            placebo_rank=placebo_rank,
            empirical_tail_fraction=empirical_tail_fraction,
            num_placebo_sets=num_placebo_sets,
            is_candidate=False,
            is_diagnostic_only=True,
            is_blocked=False,
            warnings=(FALSIFICATION_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    return AugSynthPointRandomizationResult(
        decision=AugSynthRandomizationDecision.AUGSYNTH_POINT_RANDOMIZATION_CANDIDATE,
        compatibility=compatibility,
        treated_set_placebo_summary=placebo_summary,
        method_randomization_summary=method_summary,
        observed_statistic=contract.observed_statistic,
        pseudo_statistic_by_assignment=dict(contract.pseudo_statistic_by_assignment),
        placebo_rank=placebo_rank,
        empirical_tail_fraction=empirical_tail_fraction,
        num_placebo_sets=num_placebo_sets,
        is_candidate=True,
        is_diagnostic_only=False,
        is_blocked=False,
        warnings=(CANDIDATE_WARNING, JK_NOT_AUTHORIZED_WARNING),
        blocked_reasons=(),
        governance_flags=_governance_flags(),
    )


def summarize_augsynth_point_randomization_result(
    result: AugSynthPointRandomizationResult,
) -> dict[str, Any]:
    """Serialize AugSynth point randomization result for validation archives."""
    return {
        "decision": result.decision.value,
        "compatibility": result.compatibility.value,
        "treated_set_placebo_summary": dict(result.treated_set_placebo_summary),
        "method_randomization_summary": dict(result.method_randomization_summary),
        "observed_statistic": result.observed_statistic,
        "pseudo_statistic_by_assignment": dict(result.pseudo_statistic_by_assignment),
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


def build_augsynth_point_randomization_readiness_matrix() -> list[dict[str, Any]]:
    """Return illustrative AugSynth point randomization readiness matrix entries."""
    pseudo = {f"p{i}": 0.05 * i for i in range(1, 12)}
    base_contract = AugSynthPointStatisticContract(
        observed_statistic=0.42,
        pseudo_statistic_by_assignment=pseudo,
        statistic_kind=AugSynthStatisticKind.POINT_EFFECT,
        inference_mode=AugSynthInferenceMode.POINT_ONLY,
        effect_direction="greater",
        estimand_id="ate",
        outcome_scale="absolute",
        pre_period_id="pre",
        post_period_id="post",
        donor_eligibility_rule_id="default",
        augmentation_config_id="ridge_v1",
    )
    rows: list[dict[str, Any]] = []
    for kind in AugSynthStatisticKind:
        contract = AugSynthPointStatisticContract(
            observed_statistic=base_contract.observed_statistic,
            pseudo_statistic_by_assignment=base_contract.pseudo_statistic_by_assignment,
            statistic_kind=kind,
            inference_mode=base_contract.inference_mode,
            effect_direction=base_contract.effect_direction,
            estimand_id=base_contract.estimand_id,
            outcome_scale=base_contract.outcome_scale,
            pre_period_id=base_contract.pre_period_id,
            post_period_id=base_contract.post_period_id,
            donor_eligibility_rule_id=base_contract.donor_eligibility_rule_id,
            augmentation_config_id=base_contract.augmentation_config_id,
        )
        spec = AugSynthPointRandomizationSpec(
            assignment_role=AssignmentRole.DESIGN_BASED_RANDOMIZATION_CANDIDATE.value,
            assignment_family="complete_randomized_set",
            num_treated_units=2,
            num_valid_pseudo_assignments=11,
            statistic_contract=contract,
        )
        result = evaluate_augsynth_point_randomization(spec)
        rows.append(
            {
                "statistic_kind": kind.value,
                "decision": result.decision.value,
                "is_candidate": result.is_candidate,
                "is_blocked": result.is_blocked,
            }
        )
    return rows


__all__ = [
    "AugSynthCompatibility",
    "AugSynthInferenceMode",
    "AugSynthPointRandomizationResult",
    "AugSynthPointRandomizationSpec",
    "AugSynthPointStatisticContract",
    "AugSynthRandomizationDecision",
    "AugSynthStatisticKind",
    "build_augsynth_point_randomization_readiness_matrix",
    "evaluate_augsynth_point_randomization",
    "summarize_augsynth_point_randomization_result",
    "validate_augsynth_point_statistic_contract",
]
