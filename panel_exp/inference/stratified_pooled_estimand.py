"""STRATIFIED_POOLED_ESTIMAND_CONTRACT_001 — governed stratified/pooled estimand contract.

Defines when stratified or pooled effects are coherent causal estimands vs invalid aggregations.
Framework-level contract candidate / diagnostic only — not production pooled inference.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

STRATUM_LEVEL_WARNING = (
    "Stratum-level readout only — not pooled or global causal inference; no aggregate causal claim."
)

CONTRACT_CANDIDATE_WARNING = (
    "Pooled estimand contract candidate only — not production pooled inference; "
    "no final p-value or causal confidence interval."
)

DIAGNOSTIC_SUMMARY_WARNING = (
    "Stratified aggregate diagnostic summary only — not production pooled causal effect."
)

HETEROGENEITY_EVIDENCE = (
    "heterogeneity_assessment",
    "pre_specified_heterogeneity_policy",
    "stratum_level_effect_compatibility_review",
)

POOLING_PROMOTION_EVIDENCE = (
    "valid_pooling_inference",
    "multiplicity_or_dependence_resolution",
    "pre_registered_pooled_estimand",
)


class PooledEstimandUseCase(str, Enum):
    STRATUM_LEVEL_READOUT = "stratum_level_readout"
    STRATIFIED_AGGREGATE = "stratified_aggregate"
    POOLED_MULTICELL_EFFECT = "pooled_multicell_effect"
    GLOBAL_SUMMARY = "global_summary"
    WINNER_SELECTED_SUMMARY = "winner_selected_summary"
    UNKNOWN = "unknown"


class PooledEstimandGeometry(str, Enum):
    SINGLE_STRATUM = "single_stratum"
    MULTI_STRATUM = "multi_stratum"
    MULTICELL = "multicell"
    SHARED_CONTROL_MULTICELL = "shared_control_multicell"
    UNKNOWN = "unknown"


class PoolingWeightKind(str, Enum):
    NONE = "none"
    PRE_SPECIFIED_POPULATION = "pre_specified_population"
    PRE_SPECIFIED_SPEND = "pre_specified_spend"
    PRE_SPECIFIED_EXPOSURE = "pre_specified_exposure"
    EQUAL_WEIGHT = "equal_weight"
    POST_HOC_EFFECT_SIZE = "post_hoc_effect_size"
    WINNER_SELECTED = "winner_selected"
    UNKNOWN = "unknown"


class HeterogeneityPolicy(str, Enum):
    NOT_ASSESSED = "not_assessed"
    REPORT_SEPARATELY = "report_separately"
    ALLOW_WITH_PRE_SPECIFIED_POOLING = "allow_with_pre_specified_pooling"
    BLOCK_IF_MATERIAL_HETEROGENEITY = "block_if_material_heterogeneity"
    UNKNOWN = "unknown"


class PooledEstimandRole(str, Enum):
    STRATUM_LEVEL_ONLY = "stratum_level_only"
    POOLED_ESTIMAND_CONTRACT_CANDIDATE = "pooled_estimand_contract_candidate"
    DIAGNOSTIC_SUMMARY_ONLY = "diagnostic_summary_only"
    HETEROGENEITY_REVIEW_REQUIRED = "heterogeneity_review_required"
    MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED = "multiplicity_or_dependence_unresolved"
    BLOCKED = "blocked"


class PooledEstimandDecision(str, Enum):
    STRATUM_LEVEL_READOUT_ALLOWED = "stratum_level_readout_allowed"
    POOLED_ESTIMAND_CONTRACT_CANDIDATE = "pooled_estimand_contract_candidate"
    STRATIFIED_AGGREGATE_DIAGNOSTIC_ONLY = "stratified_aggregate_diagnostic_only"
    HETEROGENEITY_REVIEW_REQUIRED = "heterogeneity_review_required"
    MULTICELL_POOLED_EFFECT_BLOCKED = "multicell_pooled_effect_blocked"
    GLOBAL_SUMMARY_BLOCKED = "global_summary_blocked"
    WINNER_SELECTED_SUMMARY_BLOCKED = "winner_selected_summary_blocked"
    POOLED_ESTIMAND_BLOCKED = "pooled_estimand_blocked"


@dataclass(frozen=True)
class StratumEstimandSpec:
    stratum_id: str
    estimand_id: str
    metric: str
    effect_scale: str
    target_population: str
    time_window: str
    is_compatible: bool = True
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StratifiedPooledEstimandSpec:
    use_case: PooledEstimandUseCase
    geometry: PooledEstimandGeometry
    strata: tuple[StratumEstimandSpec, ...]
    weighting_kind: PoolingWeightKind
    weights_by_stratum: Mapping[str, float] | None = None
    weights_pre_specified: bool = False
    heterogeneity_policy: HeterogeneityPolicy = HeterogeneityPolicy.NOT_ASSESSED
    heterogeneity_assessed: bool = False
    material_heterogeneity_detected: bool = False
    has_common_metric: bool = False
    has_common_effect_scale: bool = False
    has_common_time_window: bool = False
    has_common_target_population: bool = False
    has_valid_pooled_estimand_statement: bool = False
    has_valid_inference_for_pooling: bool = False
    has_multiplicity_adjustment: bool = False
    has_shared_control_dependence_resolution: bool = False
    requested_global_decision: bool = False
    requested_winner_selection: bool = False
    requested_pooled_effect_authorization: bool = False
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
class StratifiedPooledEstimandResult:
    role: PooledEstimandRole
    decision: PooledEstimandDecision
    normalized_weights_by_stratum: Mapping[str, float] | None
    num_strata: int
    is_stratum_level_only: bool
    is_contract_candidate: bool
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
        "pooled_effect_authorized": False,
        "global_summary_allowed": False,
        "winner_selection_allowed": False,
    }


def normalize_pooling_weights(weights_by_stratum: Mapping[str, float]) -> dict[str, float]:
    """Normalize non-negative stratum weights to sum to 1."""
    total = sum(float(v) for v in weights_by_stratum.values())
    if total <= 0:
        return {}
    return {k: float(v) / total for k, v in weights_by_stratum.items()}


def _blocked(
    spec: StratifiedPooledEstimandSpec,
    *,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    role: PooledEstimandRole = PooledEstimandRole.BLOCKED,
    decision: PooledEstimandDecision = PooledEstimandDecision.POOLED_ESTIMAND_BLOCKED,
    required_next_evidence: tuple[str, ...] = (),
    normalized_weights: Mapping[str, float] | None = None,
) -> StratifiedPooledEstimandResult:
    return StratifiedPooledEstimandResult(
        role=role,
        decision=decision,
        normalized_weights_by_stratum=dict(normalized_weights or {}),
        num_strata=len(spec.strata),
        is_stratum_level_only=False,
        is_contract_candidate=False,
        is_diagnostic_only=False,
        is_blocked=True,
        required_next_evidence=required_next_evidence,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def _platform_block(spec: StratifiedPooledEstimandSpec) -> StratifiedPooledEstimandResult | None:
    checks: list[tuple[bool, str]] = [
        (spec.requested_trustreport_authorization, "TrustReport authorization is not supported"),
        (spec.requested_calibration_signal, "CalibrationSignal export is not supported"),
        (spec.requested_mmm_ingestion, "MMM ingestion is not supported"),
        (spec.requested_llm_decisioning, "LLM decisioning is not supported"),
        (spec.requested_production_decisioning, "production decisioning is not supported"),
        (spec.requested_live_api, "live API authorization is not supported"),
        (spec.requested_scheduler, "scheduler authorization is not supported"),
        (spec.requested_budget_optimization, "budget optimization is not supported"),
        (spec.requested_pooled_effect_authorization, "pooled effect authorization is not supported"),
        (spec.requested_global_decision, "global multi-cell decision is not supported"),
        (spec.requested_winner_selection, "winner selection is not supported"),
    ]
    for flag, msg in checks:
        if flag:
            return _blocked(spec, reasons=(msg,))
    return None


def _strata_compatible(spec: StratifiedPooledEstimandSpec) -> tuple[bool, tuple[str, ...]]:
    if not spec.strata:
        return False, ("no strata defined",)
    reasons: list[str] = []
    for s in spec.strata:
        if not s.is_compatible:
            reasons.append(f"stratum {s.stratum_id} marked incompatible")
    if not spec.has_common_metric:
        reasons.append("strata do not share a common metric")
    if not spec.has_common_effect_scale:
        reasons.append("strata do not share a common effect scale")
    if not spec.has_common_time_window:
        reasons.append("strata do not share a common time window")
    if not spec.has_common_target_population:
        reasons.append("strata do not share a common target population")
    metrics = {s.metric for s in spec.strata}
    scales = {s.effect_scale for s in spec.strata}
    windows = {s.time_window for s in spec.strata}
    populations = {s.target_population for s in spec.strata}
    estimands = {s.estimand_id for s in spec.strata}
    if len(metrics) > 1:
        reasons.append("incompatible metrics across strata")
    if len(scales) > 1:
        reasons.append("incompatible effect scales across strata")
    if len(windows) > 1:
        reasons.append("incompatible time windows across strata")
    if len(populations) > 1:
        reasons.append("incompatible target populations across strata")
    if len(estimands) > 1 and not spec.has_valid_pooled_estimand_statement:
        reasons.append("incompatible estimand definitions across strata")
    return not reasons, tuple(reasons)


def _validate_weights(
    spec: StratifiedPooledEstimandSpec,
) -> tuple[bool, dict[str, float] | None, tuple[str, ...]]:
    if spec.weighting_kind in {
        PoolingWeightKind.POST_HOC_EFFECT_SIZE,
        PoolingWeightKind.WINNER_SELECTED,
    }:
        return False, None, (f"blocked weighting rule: {spec.weighting_kind.value}",)

    if spec.use_case in {
        PooledEstimandUseCase.STRATIFIED_AGGREGATE,
        PooledEstimandUseCase.POOLED_MULTICELL_EFFECT,
    }:
        if spec.weights_by_stratum is None or not spec.weights_by_stratum:
            return False, None, ("missing weights for pooling use case",)
        stratum_ids = {s.stratum_id for s in spec.strata}
        weight_ids = set(spec.weights_by_stratum)
        if stratum_ids != weight_ids:
            return False, None, ("weight IDs do not match stratum IDs",)
        for sid, w in spec.weights_by_stratum.items():
            if not math.isfinite(float(w)):
                return False, None, (f"non-finite weight for stratum {sid}",)
            if float(w) < 0:
                return False, None, (f"negative weight for stratum {sid}",)
        normalized = normalize_pooling_weights(spec.weights_by_stratum)
        if not normalized:
            return False, None, ("weights sum to zero",)
        return True, normalized, ()
    return True, None, ()


def _dependence_unresolved(spec: StratifiedPooledEstimandSpec) -> bool:
    if spec.geometry in {
        PooledEstimandGeometry.MULTICELL,
        PooledEstimandGeometry.SHARED_CONTROL_MULTICELL,
    }:
        return not (
            spec.has_multiplicity_adjustment and spec.has_shared_control_dependence_resolution
        )
    if len(spec.strata) > 1 and spec.use_case in {
        PooledEstimandUseCase.STRATIFIED_AGGREGATE,
        PooledEstimandUseCase.POOLED_MULTICELL_EFFECT,
    }:
        return not spec.has_multiplicity_adjustment
    return False


def validate_stratified_pooled_estimand(
    spec: StratifiedPooledEstimandSpec,
) -> StratifiedPooledEstimandResult:
    """Validate stratified/pooled estimand contract boundaries."""
    platform = _platform_block(spec)
    if platform is not None:
        return platform

    if spec.use_case == PooledEstimandUseCase.GLOBAL_SUMMARY:
        return _blocked(
            spec,
            decision=PooledEstimandDecision.GLOBAL_SUMMARY_BLOCKED,
            reasons=("global summary requires unresolved pooled estimand and dependence evidence",),
        )

    if spec.use_case == PooledEstimandUseCase.WINNER_SELECTED_SUMMARY:
        return _blocked(
            spec,
            decision=PooledEstimandDecision.WINNER_SELECTED_SUMMARY_BLOCKED,
            reasons=("winner_selected_summary_requires_selection_adjusted_inference",),
        )

    if spec.use_case == PooledEstimandUseCase.UNKNOWN:
        return _blocked(spec, reasons=("unknown pooled estimand use case",))

    if spec.use_case == PooledEstimandUseCase.POOLED_MULTICELL_EFFECT:
        return _blocked(
            spec,
            role=PooledEstimandRole.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED,
            decision=PooledEstimandDecision.MULTICELL_POOLED_EFFECT_BLOCKED,
            reasons=(
                "pooled_multicell_effect_requires_pooled_estimand_and_dependence_aware_inference",
            ),
            required_next_evidence=POOLING_PROMOTION_EVIDENCE,
        )

    if spec.use_case == PooledEstimandUseCase.STRATUM_LEVEL_READOUT:
        compatible, reasons = _strata_compatible(spec)
        if not compatible and spec.strata:
            return _blocked(spec, reasons=reasons)
        return StratifiedPooledEstimandResult(
            role=PooledEstimandRole.STRATUM_LEVEL_ONLY,
            decision=PooledEstimandDecision.STRATUM_LEVEL_READOUT_ALLOWED,
            normalized_weights_by_stratum=None,
            num_strata=len(spec.strata),
            is_stratum_level_only=True,
            is_contract_candidate=False,
            is_diagnostic_only=False,
            is_blocked=False,
            required_next_evidence=(),
            warnings=(STRATUM_LEVEL_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    # STRATIFIED_AGGREGATE and pooling paths below
    compatible, incompatibility = _strata_compatible(spec)
    if not compatible:
        return _blocked(spec, reasons=incompatibility)

    if not spec.has_valid_pooled_estimand_statement:
        return _blocked(spec, reasons=("missing valid pooled estimand statement",))

    weights_ok, normalized, weight_reasons = _validate_weights(spec)
    if not weights_ok:
        return _blocked(spec, reasons=weight_reasons)

    if not spec.weights_pre_specified:
        return _blocked(spec, reasons=("weights are not pre-specified",))

    if spec.heterogeneity_policy in {
        HeterogeneityPolicy.NOT_ASSESSED,
        HeterogeneityPolicy.UNKNOWN,
    } or not spec.heterogeneity_assessed:
        return StratifiedPooledEstimandResult(
            role=PooledEstimandRole.HETEROGENEITY_REVIEW_REQUIRED,
            decision=PooledEstimandDecision.HETEROGENEITY_REVIEW_REQUIRED,
            normalized_weights_by_stratum=normalized,
            num_strata=len(spec.strata),
            is_stratum_level_only=False,
            is_contract_candidate=False,
            is_diagnostic_only=False,
            is_blocked=True,
            required_next_evidence=HETEROGENEITY_EVIDENCE,
            warnings=("heterogeneity must be assessed before pooling promotion",),
            blocked_reasons=("heterogeneity not assessed",),
            governance_flags=_governance_flags(),
        )

    if spec.material_heterogeneity_detected:
        if spec.heterogeneity_policy == HeterogeneityPolicy.BLOCK_IF_MATERIAL_HETEROGENEITY:
            return _blocked(
                spec,
                reasons=("material_heterogeneity_blocks_pooling",),
                normalized_weights=normalized,
            )
        if spec.heterogeneity_policy == HeterogeneityPolicy.REPORT_SEPARATELY:
            return StratifiedPooledEstimandResult(
                role=PooledEstimandRole.DIAGNOSTIC_SUMMARY_ONLY,
                decision=PooledEstimandDecision.STRATIFIED_AGGREGATE_DIAGNOSTIC_ONLY,
                normalized_weights_by_stratum=normalized,
                num_strata=len(spec.strata),
                is_stratum_level_only=True,
                is_diagnostic_only=True,
                is_contract_candidate=False,
                is_blocked=False,
                required_next_evidence=HETEROGENEITY_EVIDENCE,
                warnings=(
                    STRATUM_LEVEL_WARNING,
                    "Material heterogeneity — report strata separately; no pooled claim.",
                ),
                blocked_reasons=(),
                governance_flags=_governance_flags(),
            )

    if _dependence_unresolved(spec):
        return _blocked(
            spec,
            role=PooledEstimandRole.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED,
            reasons=("multiplicity or shared-control dependence unresolved for pooling",),
            required_next_evidence=POOLING_PROMOTION_EVIDENCE,
            normalized_weights=normalized,
        )

    if spec.has_valid_inference_for_pooling and all(
        [
            spec.has_common_metric,
            spec.has_common_effect_scale,
            spec.has_common_time_window,
            spec.has_common_target_population,
            spec.weights_pre_specified,
            spec.heterogeneity_assessed,
            spec.heterogeneity_policy
            not in {HeterogeneityPolicy.NOT_ASSESSED, HeterogeneityPolicy.UNKNOWN},
        ]
    ):
        return StratifiedPooledEstimandResult(
            role=PooledEstimandRole.POOLED_ESTIMAND_CONTRACT_CANDIDATE,
            decision=PooledEstimandDecision.POOLED_ESTIMAND_CONTRACT_CANDIDATE,
            normalized_weights_by_stratum=normalized,
            num_strata=len(spec.strata),
            is_stratum_level_only=False,
            is_contract_candidate=True,
            is_diagnostic_only=False,
            is_blocked=False,
            required_next_evidence=(),
            warnings=(CONTRACT_CANDIDATE_WARNING,),
            blocked_reasons=(),
            governance_flags=_governance_flags(),
        )

    return StratifiedPooledEstimandResult(
        role=PooledEstimandRole.DIAGNOSTIC_SUMMARY_ONLY,
        decision=PooledEstimandDecision.STRATIFIED_AGGREGATE_DIAGNOSTIC_ONLY,
        normalized_weights_by_stratum=normalized,
        num_strata=len(spec.strata),
        is_stratum_level_only=False,
        is_contract_candidate=False,
        is_diagnostic_only=True,
        is_blocked=False,
        required_next_evidence=("valid_pooling_inference",),
        warnings=(DIAGNOSTIC_SUMMARY_WARNING,),
        blocked_reasons=(),
        governance_flags=_governance_flags(),
    )


def summarize_stratified_pooled_estimand_result(
    result: StratifiedPooledEstimandResult,
) -> dict[str, Any]:
    """Serialize stratified/pooled estimand result for validation archives."""
    return {
        "role": result.role.value,
        "decision": result.decision.value,
        "normalized_weights_by_stratum": dict(result.normalized_weights_by_stratum or {}),
        "num_strata": result.num_strata,
        "is_stratum_level_only": result.is_stratum_level_only,
        "is_contract_candidate": result.is_contract_candidate,
        "is_diagnostic_only": result.is_diagnostic_only,
        "is_blocked": result.is_blocked,
        "required_next_evidence": list(result.required_next_evidence),
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


def build_stratified_pooled_estimand_readiness_matrix() -> list[dict[str, Any]]:
    """Return illustrative stratified/pooled estimand readiness matrix entries."""
    base_stratum = StratumEstimandSpec(
        stratum_id="s1",
        estimand_id="ate",
        metric="revenue",
        effect_scale="absolute",
        target_population="geo",
        time_window="post",
    )
    rows: list[dict[str, Any]] = []
    for use_case in PooledEstimandUseCase:
        spec = StratifiedPooledEstimandSpec(
            use_case=use_case,
            geometry=PooledEstimandGeometry.MULTI_STRATUM,
            strata=(base_stratum,),
            weighting_kind=PoolingWeightKind.NONE,
            has_common_metric=True,
            has_common_effect_scale=True,
            has_common_time_window=True,
            has_common_target_population=True,
        )
        if use_case == PooledEstimandUseCase.POOLED_MULTICELL_EFFECT:
            spec = StratifiedPooledEstimandSpec(
                use_case=use_case,
                geometry=PooledEstimandGeometry.SHARED_CONTROL_MULTICELL,
                strata=(base_stratum,),
                weighting_kind=PoolingWeightKind.PRE_SPECIFIED_POPULATION,
                weights_by_stratum={"s1": 1.0},
            )
        result = validate_stratified_pooled_estimand(spec)
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
    "CONTRACT_CANDIDATE_WARNING",
    "DIAGNOSTIC_SUMMARY_WARNING",
    "HeterogeneityPolicy",
    "PooledEstimandDecision",
    "PooledEstimandGeometry",
    "PooledEstimandRole",
    "PooledEstimandUseCase",
    "PoolingWeightKind",
    "STRATUM_LEVEL_WARNING",
    "StratifiedPooledEstimandResult",
    "StratifiedPooledEstimandSpec",
    "StratumEstimandSpec",
    "build_stratified_pooled_estimand_readiness_matrix",
    "normalize_pooling_weights",
    "summarize_stratified_pooled_estimand_result",
    "validate_stratified_pooled_estimand",
]
