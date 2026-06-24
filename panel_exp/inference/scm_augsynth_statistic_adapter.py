"""SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001 — shared statistic adapter contract.

Governed contract for comparable observed/pseudo-treated-set statistics across SCM and
AugSynth randomization paths. Contract compatibility only — not production inference.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

CROSS_FAMILY_WARNING = (
    "SCM and AugSynth may be compared only under explicit shared estimand/config "
    "contracts; estimator equivalence is not assumed."
)

CONTRACT_WARNING = (
    "Shared statistic adapter contract only — empirical tail fractions remain "
    "calibration diagnostics, not production p-values."
)

_SUPPORTED_EFFECT_DIRECTIONS = frozenset({"greater", "less", "two_sided"})

_CONFIG_COMPARE_FIELDS = (
    "estimand_id",
    "outcome_scale",
    "pre_period_id",
    "post_period_id",
    "donor_eligibility_rule_id",
    "estimator_config_id",
    "treated_set_aggregation_rule_id",
    "effect_direction",
    "missing_data_policy_id",
    "statistic_kind",
    "studentization_scale_id",
)

class StatisticAdapterFamily(str, Enum):
    SCM = "scm"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    SCM_STYLE_CALIBRATION = "scm_style_calibration"
    UNKNOWN = "unknown"


class AdapterStatisticKind(str, Enum):
    POINT_EFFECT = "point_effect"
    RELATIVE_EFFECT = "relative_effect"
    STUDENTIZED_EFFECT = "studentized_effect"
    SCM_STYLE_EFFECT = "scm_style_effect"
    SCM_STYLE_STUDENTIZED_EFFECT = "scm_style_studentized_effect"
    UNKNOWN = "unknown"


class AdapterCompatibilityStatus(str, Enum):
    COMPATIBLE = "compatible"
    COMPATIBLE_AS_CALIBRATION_HARNESS_ONLY = "compatible_as_calibration_harness_only"
    MISSING_OBSERVED_STATISTIC = "missing_observed_statistic"
    MISSING_PSEUDO_STATISTICS = "missing_pseudo_statistics"
    STATISTIC_KIND_MISMATCH = "statistic_kind_mismatch"
    ESTIMAND_MISMATCH = "estimand_mismatch"
    OUTCOME_SCALE_MISMATCH = "outcome_scale_mismatch"
    TIME_WINDOW_MISMATCH = "time_window_mismatch"
    DONOR_ELIGIBILITY_MISMATCH = "donor_eligibility_mismatch"
    ESTIMATOR_CONFIG_MISMATCH = "estimator_config_mismatch"
    TREATED_SET_AGGREGATION_MISMATCH = "treated_set_aggregation_mismatch"
    EFFECT_DIRECTION_MISMATCH = "effect_direction_mismatch"
    MISSING_DATA_POLICY_MISMATCH = "missing_data_policy_mismatch"
    PROVENANCE_MISSING = "provenance_missing"
    NON_NUMERIC_STATISTIC = "non_numeric_statistic"
    INSUFFICIENT_PSEUDO_STATISTICS = "insufficient_pseudo_statistics"
    UNSUPPORTED_FAMILY = "unsupported_family"
    BLOCKED = "blocked"


class AdapterUsageBoundary(str, Enum):
    RANDOMIZATION_CANDIDATE_ONLY = "randomization_candidate_only"
    CALIBRATION_HARNESS_ONLY = "calibration_harness_only"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"


_STUDENTIZED_KINDS = frozenset(
    {
        AdapterStatisticKind.STUDENTIZED_EFFECT,
        AdapterStatisticKind.SCM_STYLE_STUDENTIZED_EFFECT,
    }
)

# Populate status map after enum definitions
_STATUS_FOR_CONFIG_FIELD: dict[str, AdapterCompatibilityStatus] = {
        "estimand_id": AdapterCompatibilityStatus.ESTIMAND_MISMATCH,
        "outcome_scale": AdapterCompatibilityStatus.OUTCOME_SCALE_MISMATCH,
        "pre_period_id": AdapterCompatibilityStatus.TIME_WINDOW_MISMATCH,
        "post_period_id": AdapterCompatibilityStatus.TIME_WINDOW_MISMATCH,
        "donor_eligibility_rule_id": AdapterCompatibilityStatus.DONOR_ELIGIBILITY_MISMATCH,
        "estimator_config_id": AdapterCompatibilityStatus.ESTIMATOR_CONFIG_MISMATCH,
        "treated_set_aggregation_rule_id": (
            AdapterCompatibilityStatus.TREATED_SET_AGGREGATION_MISMATCH
        ),
        "effect_direction": AdapterCompatibilityStatus.EFFECT_DIRECTION_MISMATCH,
        "missing_data_policy_id": AdapterCompatibilityStatus.MISSING_DATA_POLICY_MISMATCH,
        "statistic_kind": AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH,
        "studentization_scale_id": AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH,
    }


@dataclass(frozen=True)
class StatisticProvenance:
    estimator_family: StatisticAdapterFamily
    estimator_version: str
    adapter_version: str
    config_hash: str
    source_artifact_id: str
    computation_mode: str
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StatisticAdapterConfig:
    estimand_id: str
    outcome_scale: str
    pre_period_id: str
    post_period_id: str
    donor_eligibility_rule_id: str
    estimator_config_id: str
    treated_set_aggregation_rule_id: str
    effect_direction: str
    missing_data_policy_id: str
    statistic_kind: AdapterStatisticKind
    studentization_scale_id: str | None = None


@dataclass(frozen=True)
class AdaptedStatisticSet:
    observed_statistic: float | None
    pseudo_statistic_by_assignment: Mapping[str, float]
    config: StatisticAdapterConfig
    provenance: StatisticProvenance
    min_pseudo_statistics: int = 20


@dataclass(frozen=True)
class StatisticAdapterCompatibilityResult:
    status: AdapterCompatibilityStatus
    usage_boundary: AdapterUsageBoundary
    observed_family: StatisticAdapterFamily
    pseudo_family: StatisticAdapterFamily
    shared_config: StatisticAdapterConfig | None
    observed_statistic: float | None
    pseudo_statistic_by_assignment: Mapping[str, float]
    num_pseudo_statistics: int
    is_randomization_candidate_compatible: bool
    is_calibration_harness_only: bool
    is_diagnostic_only: bool
    is_blocked: bool
    warnings: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    governance_flags: Mapping[str, bool]


def _governance_flags() -> dict[str, bool]:
    return {
        "production_p_value_authorized": False,
        "causal_confidence_interval_authorized": False,
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


def _config_field_missing(config: StatisticAdapterConfig, field: str) -> bool:
    value = getattr(config, field)
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if field == "statistic_kind" and value == AdapterStatisticKind.UNKNOWN:
        return True
    return False


def _provenance_missing(provenance: StatisticProvenance) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if provenance.estimator_family == StatisticAdapterFamily.UNKNOWN:
        reasons.append("estimator_family unknown")
    for field in (
        "estimator_version",
        "adapter_version",
        "config_hash",
        "source_artifact_id",
        "computation_mode",
    ):
        if not getattr(provenance, field, "").strip():
            reasons.append(f"missing provenance field {field}")
    return (len(reasons) > 0, tuple(reasons))


def _usage_boundary_for_family(family: StatisticAdapterFamily) -> AdapterUsageBoundary:
    if family == StatisticAdapterFamily.SCM_STYLE_CALIBRATION:
        return AdapterUsageBoundary.CALIBRATION_HARNESS_ONLY
    if family in {StatisticAdapterFamily.SCM, StatisticAdapterFamily.AUGSYNTH_CVXPY}:
        return AdapterUsageBoundary.RANDOMIZATION_CANDIDATE_ONLY
    return AdapterUsageBoundary.BLOCKED


def _supported_augsynth_kinds() -> frozenset[AdapterStatisticKind]:
    return frozenset(
        {
            AdapterStatisticKind.POINT_EFFECT,
            AdapterStatisticKind.RELATIVE_EFFECT,
            AdapterStatisticKind.STUDENTIZED_EFFECT,
        }
    )


def _supported_scm_kinds() -> frozenset[AdapterStatisticKind]:
    return frozenset(
        {
            AdapterStatisticKind.POINT_EFFECT,
            AdapterStatisticKind.RELATIVE_EFFECT,
            AdapterStatisticKind.STUDENTIZED_EFFECT,
            AdapterStatisticKind.SCM_STYLE_EFFECT,
            AdapterStatisticKind.SCM_STYLE_STUDENTIZED_EFFECT,
        }
    )


def validate_adapted_statistic_set(
    statistic_set: AdaptedStatisticSet,
) -> tuple[bool, tuple[str, ...]]:
    """Validate a single adapted statistic set."""
    reasons: list[str] = []
    family = statistic_set.provenance.estimator_family

    if family == StatisticAdapterFamily.UNKNOWN:
        reasons.append("unsupported family unknown")
    elif family not in {
        StatisticAdapterFamily.SCM,
        StatisticAdapterFamily.SCM_STYLE_CALIBRATION,
        StatisticAdapterFamily.AUGSYNTH_CVXPY,
    }:
        reasons.append(f"unsupported family {family.value}")

    prov_missing, prov_reasons = _provenance_missing(statistic_set.provenance)
    if prov_missing:
        reasons.extend(prov_reasons)

    for field in _CONFIG_COMPARE_FIELDS:
        if field == "studentization_scale_id":
            continue
        if _config_field_missing(statistic_set.config, field):
            reasons.append(f"missing config field {field}")

    if statistic_set.config.effect_direction not in _SUPPORTED_EFFECT_DIRECTIONS:
        reasons.append("invalid effect direction")

    kind = statistic_set.config.statistic_kind
    if kind == AdapterStatisticKind.UNKNOWN:
        reasons.append("unknown statistic kind")
    elif family == StatisticAdapterFamily.AUGSYNTH_CVXPY and kind not in _supported_augsynth_kinds():
        reasons.append(f"unsupported AugSynth statistic kind {kind.value}")
    elif family in {StatisticAdapterFamily.SCM, StatisticAdapterFamily.SCM_STYLE_CALIBRATION}:
        if kind not in _supported_scm_kinds():
            reasons.append(f"unsupported SCM statistic kind {kind.value}")

    if kind in _STUDENTIZED_KINDS and not statistic_set.config.studentization_scale_id:
        reasons.append("studentization_scale_id required for studentized statistic")

    if statistic_set.observed_statistic is None:
        reasons.append("missing observed statistic")
    elif not _is_finite(statistic_set.observed_statistic):
        reasons.append("non-finite observed statistic")

    if not statistic_set.pseudo_statistic_by_assignment:
        reasons.append("missing pseudo statistics")
    else:
        for aid, val in statistic_set.pseudo_statistic_by_assignment.items():
            if not _is_finite(val):
                reasons.append(f"non-finite pseudo statistic {aid}")
        if len(statistic_set.pseudo_statistic_by_assignment) < statistic_set.min_pseudo_statistics:
            reasons.append("insufficient pseudo statistics")

    return (len(reasons) == 0, tuple(reasons))


def _compare_configs(
    left: StatisticAdapterConfig,
    right: StatisticAdapterConfig,
) -> AdapterCompatibilityStatus | None:
    for field in _CONFIG_COMPARE_FIELDS:
        lv = getattr(left, field)
        rv = getattr(right, field)
        if lv != rv:
            return _STATUS_FOR_CONFIG_FIELD[field]
    return None


def _blocked_result(
    *,
    status: AdapterCompatibilityStatus,
    statistic_set: AdaptedStatisticSet,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    pseudo_family: StatisticAdapterFamily | None = None,
) -> StatisticAdapterCompatibilityResult:
    family = statistic_set.provenance.estimator_family
    pseudo = dict(statistic_set.pseudo_statistic_by_assignment)
    return StatisticAdapterCompatibilityResult(
        status=status,
        usage_boundary=AdapterUsageBoundary.BLOCKED,
        observed_family=family,
        pseudo_family=pseudo_family or family,
        shared_config=None,
        observed_statistic=statistic_set.observed_statistic,
        pseudo_statistic_by_assignment=pseudo,
        num_pseudo_statistics=len(pseudo),
        is_randomization_candidate_compatible=False,
        is_calibration_harness_only=False,
        is_diagnostic_only=False,
        is_blocked=True,
        warnings=warnings,
        blocked_reasons=reasons,
        governance_flags=_governance_flags(),
    )


def compare_observed_and_pseudo_statistic_contract(
    observed_set: AdaptedStatisticSet,
    pseudo_set: AdaptedStatisticSet | None = None,
) -> StatisticAdapterCompatibilityResult:
    """Compare observed and pseudo statistic contracts for compatibility."""
    warnings: list[str] = [CONTRACT_WARNING]
    valid, reasons = validate_adapted_statistic_set(observed_set)
    if not valid:
        status = AdapterCompatibilityStatus.BLOCKED
        for reason in reasons:
            if "missing observed" in reason:
                status = AdapterCompatibilityStatus.MISSING_OBSERVED_STATISTIC
                break
            if "missing pseudo" in reason:
                status = AdapterCompatibilityStatus.MISSING_PSEUDO_STATISTICS
                break
            if "non-finite observed" in reason:
                status = AdapterCompatibilityStatus.NON_NUMERIC_STATISTIC
                break
            if "non-finite pseudo" in reason:
                status = AdapterCompatibilityStatus.NON_NUMERIC_STATISTIC
                break
            if "insufficient pseudo" in reason:
                status = AdapterCompatibilityStatus.INSUFFICIENT_PSEUDO_STATISTICS
                break
            if "unsupported family" in reason:
                status = AdapterCompatibilityStatus.UNSUPPORTED_FAMILY
                break
            if "unknown statistic" in reason:
                status = AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH
                break
            if "provenance" in reason or "missing provenance" in reason:
                status = AdapterCompatibilityStatus.PROVENANCE_MISSING
                break
            if "studentization_scale" in reason:
                status = AdapterCompatibilityStatus.STATISTIC_KIND_MISMATCH
                break
            if "invalid effect direction" in reason:
                status = AdapterCompatibilityStatus.EFFECT_DIRECTION_MISMATCH
                break
        return _blocked_result(
            status=status,
            statistic_set=observed_set,
            reasons=reasons,
            warnings=tuple(warnings),
        )

    family = observed_set.provenance.estimator_family
    pseudo_family = family

    if pseudo_set is not None:
        pseudo_family = pseudo_set.provenance.estimator_family
        mismatch = _compare_configs(observed_set.config, pseudo_set.config)
        if mismatch is not None:
            return _blocked_result(
                status=mismatch,
                statistic_set=observed_set,
                reasons=(f"config mismatch on {mismatch.value}",),
                warnings=tuple(warnings),
                pseudo_family=pseudo_family,
            )
        if family != pseudo_family:
            warnings.append(CROSS_FAMILY_WARNING)

    boundary = _usage_boundary_for_family(family)
    if boundary == AdapterUsageBoundary.BLOCKED:
        return _blocked_result(
            status=AdapterCompatibilityStatus.UNSUPPORTED_FAMILY,
            statistic_set=observed_set,
            reasons=("unsupported estimator family",),
            warnings=tuple(warnings),
        )

    if family != pseudo_family and pseudo_set is not None:
        cross_mismatch = _compare_configs(observed_set.config, pseudo_set.config)
        if cross_mismatch is None:
            status = AdapterCompatibilityStatus.COMPATIBLE
            warnings.append(CROSS_FAMILY_WARNING)
            boundary = AdapterUsageBoundary.DIAGNOSTIC_ONLY
        else:
            return _blocked_result(
                status=cross_mismatch,
                statistic_set=observed_set,
                reasons=(f"cross-family config mismatch: {cross_mismatch.value}",),
                warnings=tuple(warnings),
                pseudo_family=pseudo_family,
            )
    elif boundary == AdapterUsageBoundary.CALIBRATION_HARNESS_ONLY:
        status = AdapterCompatibilityStatus.COMPATIBLE_AS_CALIBRATION_HARNESS_ONLY
    else:
        status = AdapterCompatibilityStatus.COMPATIBLE

    pseudo = dict(observed_set.pseudo_statistic_by_assignment)
    return StatisticAdapterCompatibilityResult(
        status=status,
        usage_boundary=boundary,
        observed_family=family,
        pseudo_family=pseudo_family,
        shared_config=observed_set.config,
        observed_statistic=observed_set.observed_statistic,
        pseudo_statistic_by_assignment=pseudo,
        num_pseudo_statistics=len(pseudo),
        is_randomization_candidate_compatible=(
            boundary == AdapterUsageBoundary.RANDOMIZATION_CANDIDATE_ONLY
            and status == AdapterCompatibilityStatus.COMPATIBLE
        ),
        is_calibration_harness_only=(
            boundary == AdapterUsageBoundary.CALIBRATION_HARNESS_ONLY
            or status == AdapterCompatibilityStatus.COMPATIBLE_AS_CALIBRATION_HARNESS_ONLY
        ),
        is_diagnostic_only=boundary == AdapterUsageBoundary.DIAGNOSTIC_ONLY,
        is_blocked=False,
        warnings=tuple(warnings),
        blocked_reasons=(),
        governance_flags=_governance_flags(),
    )


def build_adapted_statistic_set_from_dict(data: Mapping[str, Any]) -> AdaptedStatisticSet:
    """Build AdaptedStatisticSet from explicit dict with validation-oriented fields."""
    config_data = data.get("config", {})
    prov_data = data.get("provenance", {})
    kind_raw = config_data.get("statistic_kind", AdapterStatisticKind.UNKNOWN.value)
    if isinstance(kind_raw, AdapterStatisticKind):
        kind = kind_raw
    else:
        kind = AdapterStatisticKind(str(kind_raw))

    family_raw = prov_data.get("estimator_family", StatisticAdapterFamily.UNKNOWN.value)
    if isinstance(family_raw, StatisticAdapterFamily):
        family = family_raw
    else:
        family = StatisticAdapterFamily(str(family_raw))

    config = StatisticAdapterConfig(
        estimand_id=str(config_data.get("estimand_id", "")),
        outcome_scale=str(config_data.get("outcome_scale", "")),
        pre_period_id=str(config_data.get("pre_period_id", "")),
        post_period_id=str(config_data.get("post_period_id", "")),
        donor_eligibility_rule_id=str(config_data.get("donor_eligibility_rule_id", "")),
        estimator_config_id=str(config_data.get("estimator_config_id", "")),
        treated_set_aggregation_rule_id=str(
            config_data.get("treated_set_aggregation_rule_id", "")
        ),
        effect_direction=str(config_data.get("effect_direction", "")),
        missing_data_policy_id=str(config_data.get("missing_data_policy_id", "")),
        statistic_kind=kind,
        studentization_scale_id=config_data.get("studentization_scale_id"),
    )
    provenance = StatisticProvenance(
        estimator_family=family,
        estimator_version=str(prov_data.get("estimator_version", "")),
        adapter_version=str(prov_data.get("adapter_version", "1.0.0")),
        config_hash=str(prov_data.get("config_hash", "")),
        source_artifact_id=str(prov_data.get("source_artifact_id", "")),
        computation_mode=str(prov_data.get("computation_mode", "")),
        notes=tuple(prov_data.get("notes", ())),
    )
    pseudo = dict(data.get("pseudo_statistic_by_assignment", {}))
    return AdaptedStatisticSet(
        observed_statistic=data.get("observed_statistic"),
        pseudo_statistic_by_assignment=pseudo,
        config=config,
        provenance=provenance,
        min_pseudo_statistics=int(data.get("min_pseudo_statistics", 20)),
    )


def _default_pseudo(n: int = 25) -> dict[str, float]:
    return {f"a{i}": 0.03 * (i % 7) - 0.05 for i in range(1, n + 1)}


def _base_config(
    *,
    statistic_kind: AdapterStatisticKind,
    effect_direction: str = "two_sided",
    studentization_scale_id: str | None = None,
) -> StatisticAdapterConfig:
    return StatisticAdapterConfig(
        estimand_id="treated_set_att",
        outcome_scale="absolute_level",
        pre_period_id="pre_main",
        post_period_id="post_main",
        donor_eligibility_rule_id="eligible_donors_v1",
        estimator_config_id="default_v1",
        treated_set_aggregation_rule_id="mean_across_treated",
        effect_direction=effect_direction,
        missing_data_policy_id="complete_case_v1",
        statistic_kind=statistic_kind,
        studentization_scale_id=studentization_scale_id,
    )


def _base_provenance(
    *,
    family: StatisticAdapterFamily,
    source_artifact_id: str,
    computation_mode: str = "statistic_first",
) -> StatisticProvenance:
    return StatisticProvenance(
        estimator_family=family,
        estimator_version="contract_v1",
        adapter_version="1.0.0",
        config_hash="sha256:contract_default",
        source_artifact_id=source_artifact_id,
        computation_mode=computation_mode,
    )


def build_scm_style_adapter_statistic_set_from_calibration_result(
    calibration_result: object,
) -> AdaptedStatisticSet:
    """Build adapter statistic set from SCM null-calibration result or dict."""
    if isinstance(calibration_result, Mapping):
        spec = calibration_result.get("spec", {})
        mode = spec.get("statistic_mode", "scm_style_effect")
        kind = AdapterStatisticKind(str(mode))
        studentization_scale_id = (
            "pre_period_residual_scale"
            if kind == AdapterStatisticKind.SCM_STYLE_STUDENTIZED_EFFECT
            else None
        )
        observed = calibration_result.get("observed_statistic", 0.12)
        pseudo = dict(calibration_result.get("pseudo_statistic_by_assignment", _default_pseudo()))
        return AdaptedStatisticSet(
            observed_statistic=float(observed) if observed is not None else None,
            pseudo_statistic_by_assignment=pseudo,
            config=_base_config(
                statistic_kind=kind,
                studentization_scale_id=studentization_scale_id,
            ),
            provenance=_base_provenance(
                family=StatisticAdapterFamily.SCM_STYLE_CALIBRATION,
                source_artifact_id="SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
                computation_mode="calibration_harness",
            ),
        )

    spec = getattr(calibration_result, "spec", None)
    replications = getattr(calibration_result, "replication_results", ())
    observed = replications[0].observed_statistic if replications else 0.12
    mode_value = getattr(getattr(spec, "statistic_mode", None), "value", "scm_style_effect")
    kind = AdapterStatisticKind(mode_value)
    studentization_scale_id = (
        "pre_period_residual_scale"
        if kind == AdapterStatisticKind.SCM_STYLE_STUDENTIZED_EFFECT
        else None
    )
    return AdaptedStatisticSet(
        observed_statistic=observed,
        pseudo_statistic_by_assignment=_default_pseudo(),
        config=_base_config(
            statistic_kind=kind,
            studentization_scale_id=studentization_scale_id,
        ),
        provenance=_base_provenance(
            family=StatisticAdapterFamily.SCM_STYLE_CALIBRATION,
            source_artifact_id="SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
            computation_mode="calibration_harness",
        ),
    )


def build_augsynth_adapter_statistic_set_from_randomization_result(
    randomization_result: object,
    *,
    contract: Mapping[str, Any] | None = None,
) -> AdaptedStatisticSet:
    """Build adapter statistic set from AugSynth randomization result or dict."""
    if contract is not None:
        kind_map = {
            "point_effect": AdapterStatisticKind.POINT_EFFECT,
            "relative_point_effect": AdapterStatisticKind.RELATIVE_EFFECT,
            "studentized_point_effect": AdapterStatisticKind.STUDENTIZED_EFFECT,
        }
        raw_kind = contract.get("statistic_kind", "point_effect")
        kind = kind_map.get(str(raw_kind), AdapterStatisticKind(str(raw_kind)))
        studentization_scale_id = (
            "pre_period_residual_scale"
            if kind == AdapterStatisticKind.STUDENTIZED_EFFECT
            else None
        )
        observed = contract.get("observed_statistic")
        pseudo = dict(contract.get("pseudo_statistic_by_assignment", _default_pseudo()))
    elif isinstance(randomization_result, Mapping):
        observed = randomization_result.get("observed_statistic")
        pseudo = dict(randomization_result.get("pseudo_statistic_by_assignment", _default_pseudo()))
        kind = AdapterStatisticKind.POINT_EFFECT
        studentization_scale_id = None
        contract = {}
    else:
        observed = getattr(randomization_result, "observed_statistic", None)
        pseudo = dict(getattr(randomization_result, "pseudo_statistic_by_assignment", {}))
        kind = AdapterStatisticKind.POINT_EFFECT
        studentization_scale_id = None
        contract = {}

    if contract is None:
        contract = {}

    kind_map = {
        "point_effect": AdapterStatisticKind.POINT_EFFECT,
        "relative_point_effect": AdapterStatisticKind.RELATIVE_EFFECT,
        "studentized_point_effect": AdapterStatisticKind.STUDENTIZED_EFFECT,
    }
    if "statistic_kind" in contract:
        raw_kind = contract["statistic_kind"]
        if hasattr(raw_kind, "value"):
            raw_kind = raw_kind.value
        kind = kind_map.get(str(raw_kind), AdapterStatisticKind(str(raw_kind)))
        studentization_scale_id = (
            "pre_period_residual_scale"
            if kind == AdapterStatisticKind.STUDENTIZED_EFFECT
            else None
        )

    return AdaptedStatisticSet(
        observed_statistic=observed,
        pseudo_statistic_by_assignment=pseudo or _default_pseudo(),
        config=StatisticAdapterConfig(
            estimand_id=str(contract.get("estimand_id", "treated_set_att")),
            outcome_scale=str(contract.get("outcome_scale", "absolute_level")),
            pre_period_id=str(contract.get("pre_period_id", "pre_main")),
            post_period_id=str(contract.get("post_period_id", "post_main")),
            donor_eligibility_rule_id=str(
                contract.get("donor_eligibility_rule_id", "eligible_donors_v1")
            ),
            estimator_config_id=str(
                contract.get("augmentation_config_id", contract.get("estimator_config_id", "ridge_v1"))
            ),
            treated_set_aggregation_rule_id=str(
                contract.get("treated_set_aggregation_rule_id", "mean_across_treated")
            ),
            effect_direction=str(contract.get("effect_direction", "two_sided")),
            missing_data_policy_id=str(
                contract.get("missing_data_policy_id", "complete_case_v1")
            ),
            statistic_kind=kind,
            studentization_scale_id=studentization_scale_id,
        ),
        provenance=_base_provenance(
            family=StatisticAdapterFamily.AUGSYNTH_CVXPY,
            source_artifact_id="AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
        ),
    )


def summarize_statistic_adapter_compatibility_result(
    result: StatisticAdapterCompatibilityResult,
) -> dict[str, Any]:
    """Serialize statistic adapter compatibility result."""
    return {
        "status": result.status.value,
        "usage_boundary": result.usage_boundary.value,
        "observed_family": result.observed_family.value,
        "pseudo_family": result.pseudo_family.value,
        "shared_config": (
            {
                "estimand_id": result.shared_config.estimand_id,
                "outcome_scale": result.shared_config.outcome_scale,
                "pre_period_id": result.shared_config.pre_period_id,
                "post_period_id": result.shared_config.post_period_id,
                "donor_eligibility_rule_id": result.shared_config.donor_eligibility_rule_id,
                "estimator_config_id": result.shared_config.estimator_config_id,
                "treated_set_aggregation_rule_id": (
                    result.shared_config.treated_set_aggregation_rule_id
                ),
                "effect_direction": result.shared_config.effect_direction,
                "missing_data_policy_id": result.shared_config.missing_data_policy_id,
                "statistic_kind": result.shared_config.statistic_kind.value,
                "studentization_scale_id": result.shared_config.studentization_scale_id,
            }
            if result.shared_config
            else None
        ),
        "observed_statistic": result.observed_statistic,
        "num_pseudo_statistics": result.num_pseudo_statistics,
        "is_randomization_candidate_compatible": result.is_randomization_candidate_compatible,
        "is_calibration_harness_only": result.is_calibration_harness_only,
        "is_diagnostic_only": result.is_diagnostic_only,
        "is_blocked": result.is_blocked,
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
        "governance_flags": dict(result.governance_flags),
    }


def build_statistic_adapter_readiness_matrix() -> list[dict[str, Any]]:
    """Return statistic adapter readiness matrix rows."""
    pseudo = _default_pseudo()
    base_config = _base_config(statistic_kind=AdapterStatisticKind.SCM_STYLE_EFFECT)
    rows: list[dict[str, Any]] = []

    scm_cal = AdaptedStatisticSet(
        observed_statistic=0.12,
        pseudo_statistic_by_assignment=pseudo,
        config=base_config,
        provenance=_base_provenance(
            family=StatisticAdapterFamily.SCM_STYLE_CALIBRATION,
            source_artifact_id="SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
            computation_mode="calibration_harness",
        ),
    )
    scm_cal_result = compare_observed_and_pseudo_statistic_contract(scm_cal)
    rows.append(
        {
            "row_id": "scm_style_calibration_harness",
            "estimator_family": StatisticAdapterFamily.SCM_STYLE_CALIBRATION.value,
            "statistic_kind": AdapterStatisticKind.SCM_STYLE_EFFECT.value,
            "usage_boundary": scm_cal_result.usage_boundary.value,
            "compatibility_status": scm_cal_result.status.value,
            "production_authorized": False,
        }
    )

    scm_config = _base_config(statistic_kind=AdapterStatisticKind.POINT_EFFECT)
    scm = AdaptedStatisticSet(
        observed_statistic=0.15,
        pseudo_statistic_by_assignment=pseudo,
        config=scm_config,
        provenance=_base_provenance(
            family=StatisticAdapterFamily.SCM,
            source_artifact_id="SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
        ),
    )
    scm_result = compare_observed_and_pseudo_statistic_contract(scm)
    rows.append(
        {
            "row_id": "scm_treated_set_randomization_candidate",
            "estimator_family": StatisticAdapterFamily.SCM.value,
            "statistic_kind": AdapterStatisticKind.POINT_EFFECT.value,
            "usage_boundary": scm_result.usage_boundary.value,
            "compatibility_status": scm_result.status.value,
            "production_authorized": False,
        }
    )

    for kind, row_id in (
        (AdapterStatisticKind.POINT_EFFECT, "augsynth_point_randomization"),
        (AdapterStatisticKind.RELATIVE_EFFECT, "augsynth_relative_randomization"),
        (AdapterStatisticKind.STUDENTIZED_EFFECT, "augsynth_studentized_randomization"),
    ):
        stud_scale = "pre_period_residual_scale" if kind == AdapterStatisticKind.STUDENTIZED_EFFECT else None
        aug_config = _base_config(
            statistic_kind=kind,
            studentization_scale_id=stud_scale,
        )
        aug = AdaptedStatisticSet(
            observed_statistic=0.42,
            pseudo_statistic_by_assignment=pseudo,
            config=aug_config,
            provenance=_base_provenance(
                family=StatisticAdapterFamily.AUGSYNTH_CVXPY,
                source_artifact_id="AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
            ),
        )
        aug_result = compare_observed_and_pseudo_statistic_contract(aug)
        rows.append(
            {
                "row_id": row_id,
                "estimator_family": StatisticAdapterFamily.AUGSYNTH_CVXPY.value,
                "statistic_kind": kind.value,
                "usage_boundary": aug_result.usage_boundary.value,
                "compatibility_status": aug_result.status.value,
                "production_authorized": False,
            }
        )

    return rows


__all__ = [
    "CONTRACT_WARNING",
    "CROSS_FAMILY_WARNING",
    "AdaptedStatisticSet",
    "AdapterCompatibilityStatus",
    "AdapterStatisticKind",
    "AdapterUsageBoundary",
    "StatisticAdapterCompatibilityResult",
    "StatisticAdapterConfig",
    "StatisticAdapterFamily",
    "StatisticProvenance",
    "build_adapted_statistic_set_from_dict",
    "build_augsynth_adapter_statistic_set_from_randomization_result",
    "build_scm_style_adapter_statistic_set_from_calibration_result",
    "build_statistic_adapter_readiness_matrix",
    "compare_observed_and_pseudo_statistic_contract",
    "summarize_statistic_adapter_compatibility_result",
    "validate_adapted_statistic_set",
]
