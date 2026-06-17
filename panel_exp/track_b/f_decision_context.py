"""
TRUSTREPORT-F-DECISION-INTEGRATION-001 — TrustReport F-DECISION-001 context builder.

Optional attachment of method eligibility and evidence-decision outputs to
TrustReport. Does not change estimator/inference behavior or promotion gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence, Tuple, Union

from panel_exp.governance.decision_policy import (
    AgreementStatus,
    CalibrationSignalAction,
    CandidateReadout,
    DataProfile,
    DecisionPosture,
    DecisionRole,
    DesignProfile,
    EligibleReadoutProfile,
    EstimandProfile,
    EvidenceDecisionProfile,
    GeometryProfile,
    MmmAction,
    MMM_DEFAULT_STATUS,
    TrustReportAction,
    build_evidence_decision,
    resolve_eligible_readouts,
)
from panel_exp.governance.geometry_adapter_contract import GeometryType
from panel_exp.governance.interval_semantics_contract import (
    GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST,
    IntervalReadout,
)

ReadoutEvidenceSpec = Union[CandidateReadout, Mapping[str, Any]]

_DIAGNOSTIC_ONLY_TUPLES = frozenset(
    {
        ("AugSynthCVXPY", "Conformal"),
        ("TBRRidge", "Conformal"),
        ("TBRRidge", "TimeSeriesKfold"),
    }
)
_EXCLUDED_BY_DEFAULT_TUPLES = frozenset(
    {
        ("TBRRidge", "UnitJackKnife"),
        ("TBRRidge", "JKP"),
    }
)


def _normalize_estimator(name: str) -> str:
    aliases = {"SCM": "SyntheticControl", "class TBR": "TBR"}
    return aliases.get(name, name)


@dataclass(frozen=True)
class TrustReportDecisionInputs:
    """Inputs to build optional F-DECISION context on TrustReport."""

    readout_evidence: Sequence[ReadoutEvidenceSpec] = ()
    design: DesignProfile = field(default_factory=DesignProfile)
    data: DataProfile = field(default_factory=DataProfile)
    geometry: GeometryProfile = field(
        default_factory=lambda: GeometryProfile(geometry_type=GeometryType.UNIT_PANEL)
    )
    estimand: EstimandProfile = field(default_factory=EstimandProfile)
    strict: bool = False
    allow_sensitivity_in_comparison: bool = False
    mmm_status: str = MMM_DEFAULT_STATUS
    extraction_warnings: Tuple[str, ...] = ()
    downstream_authorization: Mapping[str, Any] | None = None
    trustreport_eligibility: Mapping[str, Any] | None = None
    trust_report_promotion_candidate: bool = False
    trust_report_ready: bool = False


@dataclass(frozen=True)
class TrustReportFDecisionContext:
    """Serialized F-DECISION outputs for TrustReport export."""

    eligible_readout_profiles: tuple[dict[str, Any], ...]
    evidence_decision_profile: dict[str, Any]
    primary_readout: Optional[dict[str, Any]]
    diagnostic_comparators: tuple[dict[str, Any], ...]
    falsification_checks: tuple[dict[str, Any], ...]
    sensitivity_checks: tuple[dict[str, Any], ...]
    excluded_readouts: tuple[dict[str, Any], ...]
    blocked_readouts: tuple[dict[str, Any], ...]
    conflict_status: Optional[str]
    agreement_status: str
    final_decision_posture: str
    calibration_signal_action: str
    trust_report_action: str
    mmm_action: str
    mmm_status: str
    required_warnings: tuple[str, ...]
    recommended_next_action: str
    decision_context_complete: bool
    promotion_candidates: tuple[str, ...] = ()


def _coerce_candidate(
    spec: ReadoutEvidenceSpec,
) -> tuple[Optional[CandidateReadout], list[str]]:
    if isinstance(spec, CandidateReadout):
        return spec, []

    warnings: list[str] = []
    est = spec.get("estimator_name")
    inf = spec.get("inference_mode")
    if not est or not inf:
        warnings.append(
            "decision_context_incomplete: missing estimator_name or inference_mode"
        )
        return None, warnings

    interval = spec.get("interval_readout")
    if interval is not None and not isinstance(interval, IntervalReadout):
        warnings.append(
            "decision_context_incomplete: interval_readout must be IntervalReadout when provided"
        )
        interval = None

    return (
        CandidateReadout(
            estimator_name=str(est),
            inference_mode=str(inf),
            geometry_mode=spec.get("geometry_mode"),
            interval_readout=interval,
            callable=bool(spec.get("callable", True)),
            audit_010_primary_bucket=spec.get("audit_010_primary_bucket"),
            point_effect=spec.get("point_effect"),
            falsification_passed=spec.get("falsification_passed"),
            track_b_config_alias=spec.get("track_b_config_alias"),
            research_only=bool(spec.get("research_only", False)),
        ),
        warnings,
    )


def eligible_profile_to_dict(profile: EligibleReadoutProfile) -> dict[str, Any]:
    return {
        "estimator": profile.estimator,
        "inference": profile.inference,
        "geometry_type": profile.geometry_type,
        "estimand": profile.estimand,
        "runnable_status": profile.runnable_status.value,
        "geometry_status": profile.geometry_status,
        "interval_status": profile.interval_status,
        "catalog_status": profile.catalog_status,
        "governance_bucket": profile.governance_bucket,
        "assigned_role": profile.assigned_role.value,
        "allowed_uses": list(profile.allowed_uses),
        "forbidden_uses": list(profile.forbidden_uses),
        "required_warnings": list(profile.required_warnings),
        "exclusion_reason": profile.exclusion_reason,
        "is_governed_uncertainty": profile.is_governed_uncertainty,
        "calibration_signal_eligible": profile.calibration_signal_eligible,
        "mmm_ready": profile.mmm_ready,
    }


def evidence_decision_to_dict(decision: EvidenceDecisionProfile) -> dict[str, Any]:
    return {
        "primary_readout": (
            eligible_profile_to_dict(decision.primary_readout)
            if decision.primary_readout
            else None
        ),
        "diagnostic_comparators": [
            eligible_profile_to_dict(p) for p in decision.diagnostic_comparators
        ],
        "falsification_checks": [
            eligible_profile_to_dict(p) for p in decision.falsification_checks
        ],
        "sensitivity_checks": [
            eligible_profile_to_dict(p) for p in decision.sensitivity_checks
        ],
        "excluded_readouts": [
            eligible_profile_to_dict(p) for p in decision.excluded_readouts
        ],
        "agreement_status": decision.agreement_status.value,
        "conflict_status": decision.conflict_status,
        "final_decision_posture": decision.final_decision_posture.value,
        "calibration_signal_action": decision.calibration_signal_action.value,
        "trust_report_action": decision.trust_report_action.value,
        "mmm_action": decision.mmm_action.value,
        "mmm_status": decision.mmm_status,
        "required_warnings": list(decision.required_warnings),
        "recommended_next_action": decision.recommended_next_action,
    }


def _split_excluded_and_blocked(
  profiles: Sequence[EligibleReadoutProfile],
) -> tuple[list[EligibleReadoutProfile], list[EligibleReadoutProfile]]:
    excluded: list[EligibleReadoutProfile] = []
    blocked: list[EligibleReadoutProfile] = []
    for p in profiles:
        if p.assigned_role == DecisionRole.BLOCKED:
            blocked.append(p)
        elif p.assigned_role in (
            DecisionRole.EXCLUDED,
            DecisionRole.RESEARCH_ONLY,
        ):
            excluded.append(p)
    return excluded, blocked


def assert_trust_report_decision_guardrails(
    *,
    profiles: Sequence[EligibleReadoutProfile],
    decision: EvidenceDecisionProfile,
    context: TrustReportFDecisionContext,
) -> None:
    """Enforce Track F / AUDIT-010 guardrails on built decision context."""
    assert not GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST, (
        "GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST must remain empty"
    )
    assert context.promotion_candidates == (), "promotion_candidates must be empty"
    assert decision.mmm_action == MmmAction.EXCLUDE_FROM_MMM
    assert decision.mmm_status == MMM_DEFAULT_STATUS

    for p in profiles:
        assert not p.is_governed_uncertainty, (
            f"{p.estimator}+{p.inference} must not be governed uncertainty"
        )
        key = (p.estimator, p.inference)
        if key in _DIAGNOSTIC_ONLY_TUPLES:
            assert p.assigned_role == DecisionRole.DIAGNOSTIC_COMPARATOR, key
        if key in _EXCLUDED_BY_DEFAULT_TUPLES:
            assert p.assigned_role == DecisionRole.EXCLUDED, key

    if decision.calibration_signal_action == CalibrationSignalAction.EXPORT_CALIBRATION_SIGNAL:
        assert decision.primary_readout is not None
        assert decision.primary_readout.calibration_signal_eligible
        assert decision.primary_readout.assigned_role == DecisionRole.PRIMARY_NULL_MONITOR

    for p in profiles:
        if p.inference == "Placebo":
            assert p.assigned_role == DecisionRole.FALSIFICATION_CHECK


def build_trust_report_f_decision_context(
    inputs: TrustReportDecisionInputs,
) -> TrustReportFDecisionContext:
    """
    Build F-DECISION eligibility + evidence decision context for TrustReport.

    Does not infer missing scientific facts; incomplete specs emit
    ``decision_context_incomplete`` warnings unless ``strict`` is True.
    """
    build_warnings: list[str] = []
    candidates: list[CandidateReadout] = []

    for spec in inputs.readout_evidence:
        cand, warns = _coerce_candidate(spec)
        build_warnings.extend(warns)
        if cand is None:
            continue
        candidates.append(cand)

    if inputs.strict and build_warnings:
        raise ValueError("; ".join(build_warnings))

    if not candidates and inputs.strict:
        raise ValueError("decision_context_incomplete: no valid readout evidence")

    profiles = resolve_eligible_readouts(
        candidates,
        design=inputs.design,
        data=inputs.data,
        geometry=inputs.geometry,
        estimand=inputs.estimand,
        allow_sensitivity_in_comparison=inputs.allow_sensitivity_in_comparison,
    )

    point_effects: dict[Tuple[str, str], float] = {}
    falsification_outcomes: dict[Tuple[str, str], bool] = {}
    for c in candidates:
        key = (_normalize_estimator(c.estimator_name), c.inference_mode)
        if c.point_effect is not None:
            point_effects[key] = float(c.point_effect)
        if c.falsification_passed is not None:
            falsification_outcomes[key] = bool(c.falsification_passed)

    decision = build_evidence_decision(
        profiles,
        point_effects=point_effects,
        falsification_outcomes=falsification_outcomes,
        mmm_status=inputs.mmm_status,
    )

    excluded_from_decision, blocked_from_decision = _split_excluded_and_blocked(
        decision.excluded_readouts
    )

    all_warnings = (
        tuple(inputs.extraction_warnings)
        + tuple(build_warnings)
        + tuple(decision.required_warnings)
    )
    complete = not any("decision_context_incomplete" in w for w in build_warnings)

    context = TrustReportFDecisionContext(
        eligible_readout_profiles=tuple(eligible_profile_to_dict(p) for p in profiles),
        evidence_decision_profile=evidence_decision_to_dict(decision),
        primary_readout=(
            eligible_profile_to_dict(decision.primary_readout)
            if decision.primary_readout
            else None
        ),
        diagnostic_comparators=tuple(
            eligible_profile_to_dict(p) for p in decision.diagnostic_comparators
        ),
        falsification_checks=tuple(
            eligible_profile_to_dict(p) for p in decision.falsification_checks
        ),
        sensitivity_checks=tuple(
            eligible_profile_to_dict(p) for p in decision.sensitivity_checks
        ),
        excluded_readouts=tuple(eligible_profile_to_dict(p) for p in excluded_from_decision),
        blocked_readouts=tuple(eligible_profile_to_dict(p) for p in blocked_from_decision),
        conflict_status=decision.conflict_status,
        agreement_status=decision.agreement_status.value,
        final_decision_posture=decision.final_decision_posture.value,
        calibration_signal_action=decision.calibration_signal_action.value,
        trust_report_action=decision.trust_report_action.value,
        mmm_action=decision.mmm_action.value,
        mmm_status=decision.mmm_status,
        required_warnings=all_warnings,
        recommended_next_action=decision.recommended_next_action,
        decision_context_complete=complete,
        promotion_candidates=(),
    )

    assert_trust_report_decision_guardrails(
        profiles=profiles,
        decision=decision,
        context=context,
    )
    return context


def f_decision_context_to_dict(ctx: TrustReportFDecisionContext) -> dict[str, Any]:
    return {
        "eligible_readout_profiles": list(ctx.eligible_readout_profiles),
        "evidence_decision_profile": ctx.evidence_decision_profile,
        "primary_readout": ctx.primary_readout,
        "diagnostic_comparators": list(ctx.diagnostic_comparators),
        "falsification_checks": list(ctx.falsification_checks),
        "sensitivity_checks": list(ctx.sensitivity_checks),
        "excluded_readouts": list(ctx.excluded_readouts),
        "blocked_readouts": list(ctx.blocked_readouts),
        "conflict_status": ctx.conflict_status,
        "agreement_status": ctx.agreement_status,
        "final_decision_posture": ctx.final_decision_posture,
        "calibration_signal_action": ctx.calibration_signal_action,
        "trust_report_action": ctx.trust_report_action,
        "mmm_action": ctx.mmm_action,
        "mmm_status": ctx.mmm_status,
        "required_warnings": list(ctx.required_warnings),
        "recommended_next_action": ctx.recommended_next_action,
        "decision_context_complete": ctx.decision_context_complete,
        "promotion_candidates": list(ctx.promotion_candidates),
    }


__all__ = [
    "TrustReportDecisionInputs",
    "TrustReportFDecisionContext",
    "assert_trust_report_decision_guardrails",
    "build_trust_report_f_decision_context",
    "eligible_profile_to_dict",
    "evidence_decision_to_dict",
    "f_decision_context_to_dict",
]
