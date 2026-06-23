"""MULTICELL_SHARED_CONTROL_MULTIPLICITY_001 — governed multi-cell multiplicity boundaries.

Defines why global/winner/pooled multi-cell decisions remain blocked unless multiplicity
and shared-control dependence are explicitly handled. Framework-level safety only — not
production authorization.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

PER_CELL_MARGINAL_WARNING = (
    "Per-cell marginal readout only — no global, winner, or pooled multi-cell conclusion. "
    "Multiplicity applies if multiple cells are interpreted as one decision family."
)

FWER_PROXY_WARNING = (
    "Independent familywise false-positive risk is a proxy only and does not authorize "
    "shared-control global, winner, or pooled inference."
)

SHARED_CONTROL_WARNING = (
    "Shared-control comparisons require a dependence model; independent FWER is insufficient."
)

SHARED_CONTROL_EVIDENCE = (
    "joint_null_distribution",
    "shared_control_dependence_model",
    "max_t_or_closed_testing_validation",
    "pre_registered_hypothesis_family",
)


class MultiCellDecisionUseCase(str, Enum):
    PER_CELL_MARGINAL = "per_cell_marginal"
    MULTIPLE_CELL_FAMILY = "multiple_cell_family"
    GLOBAL_DECISION = "global_decision"
    WINNER_SELECTION = "winner_selection"
    POOLED_EFFECT = "pooled_effect"
    SHARED_CONTROL_FAMILY = "shared_control_family"
    UNKNOWN = "unknown"


class MultiCellDependenceStructure(str, Enum):
    INDEPENDENT_APPROXIMATION = "independent_approximation"
    SHARED_CONTROL = "shared_control"
    CORRELATED_CELLS = "correlated_cells"
    UNKNOWN = "unknown"


class MultiplicityAdjustmentKind(str, Enum):
    NONE = "none"
    BONFERRONI = "bonferroni"
    HOLM = "holm"
    BENJAMINI_HOCHBERG_DIAGNOSTIC = "benjamini_hochberg_diagnostic"
    MAX_T_RESAMPLING_REQUIRED = "max_t_resampling_required"
    CLOSED_TESTING_REQUIRED = "closed_testing_required"
    UNKNOWN = "unknown"


class MultiCellMultiplicityRole(str, Enum):
    PER_CELL_MARGINAL_ONLY = "per_cell_marginal_only"
    MULTIPLICITY_ADJUSTMENT_REQUIRED = "multiplicity_adjustment_required"
    SHARED_CONTROL_DEPENDENCE_UNRESOLVED = "shared_control_dependence_unresolved"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_DEFERRED = "research_deferred"
    BLOCKED = "blocked"


class MultiCellMultiplicityDecision(str, Enum):
    MULTICELL_PER_CELL_MARGINAL_ALLOWED_AS_SEPARATE_READOUT = (
        "multicell_per_cell_marginal_allowed_as_separate_readout"
    )
    MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT = (
        "multicell_family_requires_multiplicity_adjustment"
    )
    MULTICELL_SHARED_CONTROL_REQUIRES_DEPENDENCE_MODEL = (
        "multicell_shared_control_requires_dependence_model"
    )
    MULTICELL_GLOBAL_DECISION_BLOCKED = "multicell_global_decision_blocked"
    MULTICELL_WINNER_SELECTION_BLOCKED = "multicell_winner_selection_blocked"
    MULTICELL_POOLED_EFFECT_BLOCKED = "multicell_pooled_effect_blocked"
    MULTICELL_RESEARCH_DEFERRED = "multicell_research_deferred"
    MULTICELL_BLOCKED = "multicell_blocked"


@dataclass(frozen=True)
class MultiCellMultiplicitySpec:
    use_case: MultiCellDecisionUseCase
    num_cells: int
    nominal_alpha: float
    dependence_structure: MultiCellDependenceStructure
    adjustment_kind: MultiplicityAdjustmentKind = MultiplicityAdjustmentKind.NONE
    has_valid_joint_null_distribution: bool = False
    has_shared_control_dependence_model: bool = False
    has_pre_registered_family: bool = False
    has_cell_level_estimand_contracts: bool = False
    has_pooled_estimand_contract: bool = False
    requested_global_decision: bool = False
    requested_winner_selection: bool = False
    requested_pooled_effect: bool = False
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
class MultiCellMultiplicityResult:
    role: MultiCellMultiplicityRole
    decision: MultiCellMultiplicityDecision
    independent_familywise_false_positive_risk: float | None
    adjusted_alpha_bonferroni: float | None
    num_cells: int
    nominal_alpha: float
    is_per_cell_marginal_only: bool
    is_adjustment_required: bool
    is_shared_control_unresolved: bool
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
        "global_multicell_decision_allowed": False,
        "winner_selection_allowed": False,
        "pooled_multicell_effect_allowed": False,
    }


def compute_independent_familywise_false_positive_risk(
    nominal_alpha: float,
    num_cells: int,
) -> float:
    """Compute independent FWER proxy: 1 - (1 - alpha)^m."""
    return 1.0 - (1.0 - nominal_alpha) ** num_cells


def compute_bonferroni_alpha(nominal_alpha: float, num_cells: int) -> float:
    """Compute Bonferroni-adjusted per-comparison alpha: alpha / m."""
    return nominal_alpha / num_cells


def _blocked(
    spec: MultiCellMultiplicitySpec,
    *,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    role: MultiCellMultiplicityRole = MultiCellMultiplicityRole.BLOCKED,
    decision: MultiCellMultiplicityDecision = MultiCellMultiplicityDecision.MULTICELL_BLOCKED,
    required_next_evidence: tuple[str, ...] = (),
    fwer: float | None = None,
    bonferroni: float | None = None,
) -> MultiCellMultiplicityResult:
    if fwer is None and spec.num_cells > 0 and 0 < spec.nominal_alpha < 1:
        fwer = compute_independent_familywise_false_positive_risk(
            spec.nominal_alpha, spec.num_cells
        )
        bonferroni = compute_bonferroni_alpha(spec.nominal_alpha, spec.num_cells)
    return MultiCellMultiplicityResult(
        role=role,
        decision=decision,
        independent_familywise_false_positive_risk=fwer,
        adjusted_alpha_bonferroni=bonferroni,
        num_cells=spec.num_cells,
        nominal_alpha=spec.nominal_alpha,
        is_per_cell_marginal_only=False,
        is_adjustment_required=False,
        is_shared_control_unresolved=role
        == MultiCellMultiplicityRole.SHARED_CONTROL_DEPENDENCE_UNRESOLVED,
        is_blocked=True,
        required_next_evidence=required_next_evidence,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def _platform_block(spec: MultiCellMultiplicitySpec) -> MultiCellMultiplicityResult | None:
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
    return None


def _invalid_params_block(spec: MultiCellMultiplicitySpec) -> MultiCellMultiplicityResult | None:
    if spec.num_cells <= 0:
        return _blocked(spec, reasons=("num_cells must be positive",))
    if spec.nominal_alpha <= 0 or spec.nominal_alpha >= 1:
        return _blocked(spec, reasons=("nominal_alpha must be in (0, 1)",))
    return None


def _fwer_bonferroni(spec: MultiCellMultiplicitySpec) -> tuple[float, float]:
    fwer = compute_independent_familywise_false_positive_risk(
        spec.nominal_alpha, spec.num_cells
    )
    bonferroni = compute_bonferroni_alpha(spec.nominal_alpha, spec.num_cells)
    return fwer, bonferroni


def _family_adjustment_result(
    spec: MultiCellMultiplicitySpec,
    *,
    warnings: tuple[str, ...],
) -> MultiCellMultiplicityResult:
    fwer, bonferroni = _fwer_bonferroni(spec)
    extra_warnings = list(warnings) + [FWER_PROXY_WARNING]
    if spec.adjustment_kind in {
        MultiplicityAdjustmentKind.BONFERRONI,
        MultiplicityAdjustmentKind.HOLM,
    }:
        extra_warnings.append(
            "Bonferroni/Holm adjustment does not authorize global multi-cell decisions "
            "under shared-control dependence"
        )
    return MultiCellMultiplicityResult(
        role=MultiCellMultiplicityRole.MULTIPLICITY_ADJUSTMENT_REQUIRED,
        decision=MultiCellMultiplicityDecision.MULTICELL_FAMILY_REQUIRES_MULTIPLICITY_ADJUSTMENT,
        independent_familywise_false_positive_risk=fwer,
        adjusted_alpha_bonferroni=bonferroni,
        num_cells=spec.num_cells,
        nominal_alpha=spec.nominal_alpha,
        is_per_cell_marginal_only=False,
        is_adjustment_required=True,
        is_shared_control_unresolved=False,
        is_blocked=False,
        required_next_evidence=(),
        warnings=tuple(extra_warnings),
        blocked_reasons=(),
        governance_flags=_governance_flags(),
    )


def validate_multicell_multiplicity(
    spec: MultiCellMultiplicitySpec,
) -> MultiCellMultiplicityResult:
    """Validate multi-cell multiplicity and shared-control dependence boundaries."""
    platform = _platform_block(spec)
    if platform is not None:
        return platform

    invalid = _invalid_params_block(spec)
    if invalid is not None:
        return invalid

    # Global / winner / pooled requests — always blocked in this artifact
    if spec.use_case == MultiCellDecisionUseCase.GLOBAL_DECISION or spec.requested_global_decision:
        return _blocked(
            spec,
            reasons=("global multi-cell decision requires joint null, dependence model, and pre-registered family",),
            decision=MultiCellMultiplicityDecision.MULTICELL_GLOBAL_DECISION_BLOCKED,
        )

    if spec.use_case == MultiCellDecisionUseCase.WINNER_SELECTION or spec.requested_winner_selection:
        return _blocked(
            spec,
            reasons=("winner_selection_requires_selection_adjusted_inference",),
            decision=MultiCellMultiplicityDecision.MULTICELL_WINNER_SELECTION_BLOCKED,
        )

    if spec.use_case == MultiCellDecisionUseCase.POOLED_EFFECT or spec.requested_pooled_effect:
        reason = "pooled_effect_requires_pooled_estimand_and_dependence_aware_inference"
        if not spec.has_pooled_estimand_contract:
            return _blocked(
                spec,
                reasons=(reason, "missing pooled estimand contract"),
                decision=MultiCellMultiplicityDecision.MULTICELL_POOLED_EFFECT_BLOCKED,
            )
        return _blocked(
            spec,
            reasons=(reason,),
            decision=MultiCellMultiplicityDecision.MULTICELL_POOLED_EFFECT_BLOCKED,
        )

    if spec.use_case == MultiCellDecisionUseCase.UNKNOWN:
        return _blocked(
            spec,
            role=MultiCellMultiplicityRole.RESEARCH_DEFERRED,
            decision=MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED,
            reasons=("unknown multi-cell decision use case",),
        )

    if spec.dependence_structure == MultiCellDependenceStructure.UNKNOWN:
        return _blocked(
            spec,
            role=MultiCellMultiplicityRole.RESEARCH_DEFERRED,
            decision=MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED,
            reasons=("unknown dependence structure",),
        )

    if spec.use_case == MultiCellDecisionUseCase.PER_CELL_MARGINAL:
        if not spec.has_cell_level_estimand_contracts:
            return _blocked(
                spec,
                reasons=("missing cell-level estimand contracts for per-cell marginal readout",),
            )
        return MultiCellMultiplicityResult(
            role=MultiCellMultiplicityRole.PER_CELL_MARGINAL_ONLY,
            decision=MultiCellMultiplicityDecision.MULTICELL_PER_CELL_MARGINAL_ALLOWED_AS_SEPARATE_READOUT,
            independent_familywise_false_positive_risk=None,
            adjusted_alpha_bonferroni=None,
            num_cells=spec.num_cells,
            nominal_alpha=spec.nominal_alpha,
            is_per_cell_marginal_only=True,
            is_adjustment_required=False,
            is_shared_control_unresolved=False,
            is_blocked=False,
            required_next_evidence=(),
            warnings=(PER_CELL_MARGINAL_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    if spec.use_case == MultiCellDecisionUseCase.MULTIPLE_CELL_FAMILY:
        if spec.num_cells <= 1:
            return _blocked(spec, reasons=("multiple-cell family requires num_cells > 1",))
        if spec.adjustment_kind == MultiplicityAdjustmentKind.NONE:
            return _family_adjustment_result(
                spec,
                warnings=("no multiplicity adjustment declared for multi-cell family",),
            )
        return _family_adjustment_result(
            spec,
            warnings=(f"multiplicity adjustment {spec.adjustment_kind.value} declared — diagnostic only",),
        )

    if spec.use_case == MultiCellDecisionUseCase.SHARED_CONTROL_FAMILY:
        if not spec.has_shared_control_dependence_model:
            fwer, bonferroni = _fwer_bonferroni(spec)
            return MultiCellMultiplicityResult(
                role=MultiCellMultiplicityRole.SHARED_CONTROL_DEPENDENCE_UNRESOLVED,
                decision=MultiCellMultiplicityDecision.MULTICELL_SHARED_CONTROL_REQUIRES_DEPENDENCE_MODEL,
                independent_familywise_false_positive_risk=fwer,
                adjusted_alpha_bonferroni=bonferroni,
                num_cells=spec.num_cells,
                nominal_alpha=spec.nominal_alpha,
                is_per_cell_marginal_only=False,
                is_adjustment_required=True,
                is_shared_control_unresolved=True,
                is_blocked=True,
                required_next_evidence=SHARED_CONTROL_EVIDENCE,
                warnings=(SHARED_CONTROL_WARNING, FWER_PROXY_WARNING),
                blocked_reasons=("shared-control dependence model not available",),
                governance_flags=_governance_flags(),
            )
        if not spec.has_valid_joint_null_distribution:
            return _blocked(
                spec,
                role=MultiCellMultiplicityRole.RESEARCH_DEFERRED,
                decision=MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED,
                reasons=("dependence model present but joint null distribution not validated",),
                required_next_evidence=SHARED_CONTROL_EVIDENCE,
                warnings=(SHARED_CONTROL_WARNING,),
            )
        return _blocked(
            spec,
            role=MultiCellMultiplicityRole.RESEARCH_DEFERRED,
            decision=MultiCellMultiplicityDecision.MULTICELL_RESEARCH_DEFERRED,
            reasons=(
                "shared-control dependence evidence incomplete for promotion beyond diagnostic boundaries",
            ),
            required_next_evidence=SHARED_CONTROL_EVIDENCE,
            warnings=(SHARED_CONTROL_WARNING, FWER_PROXY_WARNING),
        )

    return _blocked(spec, reasons=(f"unsupported or unhandled use case: {spec.use_case.value}",))


def summarize_multicell_multiplicity_result(
    result: MultiCellMultiplicityResult,
) -> dict[str, Any]:
    """Serialize multi-cell multiplicity result for validation archives."""
    return {
        "role": result.role.value,
        "decision": result.decision.value,
        "independent_familywise_false_positive_risk": result.independent_familywise_false_positive_risk,
        "adjusted_alpha_bonferroni": result.adjusted_alpha_bonferroni,
        "num_cells": result.num_cells,
        "nominal_alpha": result.nominal_alpha,
        "is_per_cell_marginal_only": result.is_per_cell_marginal_only,
        "is_adjustment_required": result.is_adjustment_required,
        "is_shared_control_unresolved": result.is_shared_control_unresolved,
        "is_blocked": result.is_blocked,
        "required_next_evidence": list(result.required_next_evidence),
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


def build_multicell_multiplicity_readiness_matrix() -> list[dict[str, Any]]:
    """Return illustrative multi-cell multiplicity readiness matrix entries."""
    rows: list[dict[str, Any]] = []
    for use_case in MultiCellDecisionUseCase:
        spec = MultiCellMultiplicitySpec(
            use_case=use_case,
            num_cells=3,
            nominal_alpha=0.10,
            dependence_structure=MultiCellDependenceStructure.INDEPENDENT_APPROXIMATION,
            has_cell_level_estimand_contracts=use_case == MultiCellDecisionUseCase.PER_CELL_MARGINAL,
            has_pooled_estimand_contract=use_case == MultiCellDecisionUseCase.POOLED_EFFECT,
        )
        if use_case == MultiCellDecisionUseCase.SHARED_CONTROL_FAMILY:
            spec = MultiCellMultiplicitySpec(
                use_case=use_case,
                num_cells=3,
                nominal_alpha=0.10,
                dependence_structure=MultiCellDependenceStructure.SHARED_CONTROL,
            )
        result = validate_multicell_multiplicity(spec)
        rows.append(
            {
                "use_case": use_case.value,
                "role": result.role.value,
                "decision": result.decision.value,
                "is_blocked": result.is_blocked,
            }
        )
    return rows


__all__ = [
    "FWER_PROXY_WARNING",
    "PER_CELL_MARGINAL_WARNING",
    "SHARED_CONTROL_EVIDENCE",
    "MultiCellDecisionUseCase",
    "MultiCellDependenceStructure",
    "MultiCellMultiplicityDecision",
    "MultiCellMultiplicityResult",
    "MultiCellMultiplicityRole",
    "MultiCellMultiplicitySpec",
    "MultiplicityAdjustmentKind",
    "build_multicell_multiplicity_readiness_matrix",
    "compute_bonferroni_alpha",
    "compute_independent_familywise_false_positive_risk",
    "summarize_multicell_multiplicity_result",
    "validate_multicell_multiplicity",
]
