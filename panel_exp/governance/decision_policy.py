"""
F-DECISION-001 — Method eligibility resolver and evidence decision policy.

Consumes F-INF / F-GEO / F-CAT / AUDIT-010 governance outputs and assigns safe
decision roles. Does not re-validate estimator math or mutate intervals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Sequence, Tuple

import numpy as np

from panel_exp.governance.catalog_contract import (
    CALIBRATION_SIGNAL_GOVERNED_ALIASES,
    MMM_READINESS_GOVERNED_ALIASES,
    track_b_alias_governance,
)
from panel_exp.governance.geometry_adapter_contract import (
    GeometryAdapterVerdict,
    GeometryClassification,
    GeometryReadoutRequest,
    GeometryType,
    classify_geometry_support,
)
from panel_exp.governance.instrument_contract import (
    is_placebo_inference_mode,
    registry_bayesian_production_block_reason,
)
from panel_exp.governance.interval_semantics_contract import (
    GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST,
    IntervalReadout,
    IntervalSemanticsClassification,
    IntervalSemanticsVerdict,
    assert_not_governed_uncertainty,
    classify_interval_semantics,
)

# AUDIT-010 Appendix A primary buckets for post-checkpoint tuples (do not weaken OC).
AUDIT_010_DECISION_BUCKETS: dict[Tuple[str, str, str], str] = {
    ("AugSynthCVXPY", "Conformal", "single_cell"): "characterized_restricted",
    ("TBRRidge", "Conformal", "single_cell"): "characterized_restricted",
    ("TBRRidge", "TimeSeriesKfold", "single_cell"): "characterized_restricted",
    ("TBRRidge", "UnitJackKnife", "single_cell"): "callable_unverified_interval_semantics",
    ("TBRRidge", "JKP", "single_cell"): "callable_unverified_interval_semantics",
    ("SyntheticControl", "UnitJackKnife", "single_cell"): "already_characterized",
    ("SCM", "UnitJackKnife", "single_cell"): "already_characterized",
}

RESEARCH_ONLY_ESTIMATORS = frozenset({"TROP", "BayesianTBR", "BayesianTBRHorseShoe"})

MMM_DEFAULT_STATUS = "not_ready_continue_track_f"


class DecisionRole(str, Enum):
    PRIMARY_NULL_MONITOR = "primary_null_monitor"
    DIAGNOSTIC_COMPARATOR = "diagnostic_comparator"
    FALSIFICATION_CHECK = "falsification_check"
    SENSITIVITY_CHECK = "sensitivity_check"
    EXCLUDED = "excluded"
    BLOCKED = "blocked"
    RESEARCH_ONLY = "research_only"


class RunnableStatus(str, Enum):
    RUNNABLE = "runnable"
    NOT_RUNNABLE = "not_runnable"
    BLOCKED_BY_POLICY = "blocked_by_policy"


class AgreementStatus(str, Enum):
    EVIDENCE_ALIGNED_LOW_CONCERN = "evidence_aligned_low_concern"
    EVIDENCE_ALIGNED_POSITIVE_WITH_CAVEATS = "evidence_aligned_positive_with_caveats"
    DIAGNOSTIC_DISAGREEMENT = "diagnostic_disagreement"
    FALSIFICATION_FAILURE = "falsification_failure"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    INSUFFICIENT_VALID_EVIDENCE = "insufficient_valid_evidence"
    BLOCKED_FOR_DECISION_USE = "blocked_for_decision_use"


class DecisionPosture(str, Enum):
    PROCEED_WITH_CONFIDENCE = "proceed_with_confidence"
    PROCEED_WITH_CAVEATS = "proceed_with_caveats"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    INCONCLUSIVE = "inconclusive"
    TRUST_REPORT_ONLY = "trust_report_only"
    BLOCKED_FOR_DECISION_USE = "blocked_for_decision_use"
    RERUN_OR_REDESIGN_REQUIRED = "rerun_or_redesign_required"
    NEEDS_MORE_POWER = "needs_more_power"
    NEEDS_BETTER_CONTROLS = "needs_better_controls"


class CalibrationSignalAction(str, Enum):
    EXPORT_CALIBRATION_SIGNAL = "export_calibration_signal"
    TRUST_REPORT_ONLY = "trust_report_only"
    DIAGNOSTIC_CONTEXT_ONLY = "diagnostic_context_only"
    NO_ACTION = "no_action"


class TrustReportAction(str, Enum):
    TRUST_REPORT_ONLY = "trust_report_only"
    DIAGNOSTIC_CONTEXT_ONLY = "diagnostic_context_only"
    EMIT_WARNING = "emit_warning"
    BLOCK_DECISION_EXPORT = "block_decision_export"
    NO_ACTION = "no_action"


class MmmAction(str, Enum):
    EXCLUDE_FROM_MMM = "exclude_from_mmm"
    NOT_READY_CONTINUE_TRACK_F = "not_ready_continue_track_f"


@dataclass(frozen=True)
class DesignProfile:
    design_method_id: str = "unknown"
    track_b_allows_primary_null_monitor: bool = True
    pooling_rule_id: Optional[str] = None


@dataclass(frozen=True)
class DataProfile:
    n_treated: int = 1
    n_control: int = 1
    n_test_grps: int = 1


@dataclass(frozen=True)
class GeometryProfile:
    geometry_type: GeometryType
    supergeo_adapter_id: Optional[str] = None
    trim_estimand_bridge_id: Optional[str] = None
    pooled_claim: bool = False
    single_treated_geometry: bool = False


@dataclass(frozen=True)
class EstimandProfile:
    target_estimand: str = "unit_level_att"


@dataclass
class CandidateReadout:
    """One estimator × inference candidate before role assignment."""

    estimator_name: str
    inference_mode: str
    geometry_mode: Optional[str] = None
    interval_readout: Optional[IntervalReadout] = None
    callable: bool = True
    audit_010_primary_bucket: Optional[str] = None
    point_effect: Optional[float] = None
    falsification_passed: Optional[bool] = None
    track_b_config_alias: Optional[str] = None
    research_only: bool = False


@dataclass(frozen=True)
class EligibleReadoutProfile:
    estimator: str
    inference: str
    geometry_type: str
    estimand: str
    runnable_status: RunnableStatus
    geometry_status: str
    interval_status: str
    catalog_status: str
    governance_bucket: str
    assigned_role: DecisionRole
    allowed_uses: Tuple[str, ...]
    forbidden_uses: Tuple[str, ...]
    required_warnings: Tuple[str, ...] = ()
    exclusion_reason: Optional[str] = None
    is_governed_uncertainty: bool = False
    calibration_signal_eligible: bool = False
    mmm_ready: bool = False


@dataclass
class EvidenceDecisionProfile:
    primary_readout: Optional[EligibleReadoutProfile] = None
    diagnostic_comparators: list[EligibleReadoutProfile] = field(default_factory=list)
    falsification_checks: list[EligibleReadoutProfile] = field(default_factory=list)
    sensitivity_checks: list[EligibleReadoutProfile] = field(default_factory=list)
    excluded_readouts: list[EligibleReadoutProfile] = field(default_factory=list)
    agreement_status: AgreementStatus = AgreementStatus.INSUFFICIENT_VALID_EVIDENCE
    conflict_status: Optional[str] = None
    final_decision_posture: DecisionPosture = DecisionPosture.INCONCLUSIVE
    calibration_signal_action: CalibrationSignalAction = CalibrationSignalAction.NO_ACTION
    trust_report_action: TrustReportAction = TrustReportAction.TRUST_REPORT_ONLY
    mmm_action: MmmAction = MmmAction.EXCLUDE_FROM_MMM
    mmm_status: str = MMM_DEFAULT_STATUS
    required_warnings: list[str] = field(default_factory=list)
    recommended_next_action: str = "no_decision"


def _normalize_estimator(name: str) -> str:
    aliases = {"SCM": "SyntheticControl", "class TBR": "TBR"}
    return aliases.get(name, name)


def _geometry_mode_key(geometry_type: GeometryType, geometry_mode: Optional[str]) -> str:
    if geometry_mode:
        gm = geometry_mode.strip().lower()
        if gm in ("single_cell", "single_cell_unit", "unit_panel"):
            return "single_cell"
        if "aggregate" in gm:
            return "aggregate_two_series"
        return gm
    mapping = {
        GeometryType.UNIT_PANEL: "single_cell",
        GeometryType.AGGREGATE_TWO_SERIES_1X1: "aggregate_two_series",
        GeometryType.AGGREGATE_TWO_SERIES_PER_CELL: "aggregate_two_series",
        GeometryType.MULTI_CELL_PER_CELL: "multi_cell",
        GeometryType.POOLED_MULTI_CELL: "pooled_multi_cell",
        GeometryType.SUPERGEO_UNIT: "supergeo",
        GeometryType.TRIMMED_POPULATION: "trimmed",
    }
    return mapping.get(geometry_type, geometry_type.value)


def _governance_bucket(
    candidate: CandidateReadout,
    *,
    geometry_type: GeometryType,
    interval_verdict: Optional[IntervalSemanticsVerdict],
) -> str:
    if candidate.audit_010_primary_bucket:
        return candidate.audit_010_primary_bucket
    est = _normalize_estimator(candidate.estimator_name)
    geo_key = _geometry_mode_key(geometry_type, candidate.geometry_mode)
    key = (est, candidate.inference_mode, geo_key)
    if key in AUDIT_010_DECISION_BUCKETS:
        return AUDIT_010_DECISION_BUCKETS[key]
    if interval_verdict is not None:
        if interval_verdict.classification == IntervalSemanticsClassification.BLOCKED_INTERFACE:
            return "blocked_interface"
        if interval_verdict.classification == IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL:
            return "blocked_invalid_interval"
        if interval_verdict.classification == IntervalSemanticsClassification.CALLABLE_UNVERIFIED_INTERVAL_SEMANTICS:
            return "callable_unverified_interval_semantics"
        if interval_verdict.classification == IntervalSemanticsClassification.DIAGNOSTIC_INTERVAL_ONLY:
            return "characterized_restricted"
    return "implemented_but_unvalidated"


def _catalog_status(candidate: CandidateReadout) -> Tuple[str, bool, bool]:
    alias = candidate.track_b_config_alias
    if alias:
        gov = track_b_alias_governance(alias)
        return (
            "governed" if gov["calibration_signal_eligible"] else "metadata_only",
            bool(gov["calibration_signal_eligible"]),
            bool(gov["mmm_ready"]),
        )
    est = _normalize_estimator(candidate.estimator_name)
    inf = candidate.inference_mode
    if is_placebo_inference_mode(inf):
        return ("inference_falsification_layer", False, False)
    if est in RESEARCH_ONLY_ESTIMATORS or candidate.research_only:
        return ("research_only", False, False)
    prod_block = registry_bayesian_production_block_reason(est, inf)
    if prod_block:
        return (prod_block, False, False)
    return ("catalog_ok", False, False)


def _is_primary_null_monitor_candidate(
    candidate: CandidateReadout,
    *,
    geometry_type: GeometryType,
    design: DesignProfile,
) -> bool:
    est = _normalize_estimator(candidate.estimator_name)
    if candidate.inference_mode != "UnitJackKnife":
        return False
    if geometry_type != GeometryType.UNIT_PANEL:
        return False
    if est != "SyntheticControl":
        return False
    if not design.track_b_allows_primary_null_monitor:
        return False
    alias = candidate.track_b_config_alias or "SCM_UnitJackKnife"
    return alias in CALIBRATION_SIGNAL_GOVERNED_ALIASES


def _assign_role(
    candidate: CandidateReadout,
    *,
    geometry_verdict: GeometryAdapterVerdict,
    interval_verdict: Optional[IntervalSemanticsVerdict],
    governance_bucket: str,
    geometry_type: GeometryType,
    design: DesignProfile,
    allow_sensitivity_in_comparison: bool,
) -> Tuple[DecisionRole, Optional[str], Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    est = _normalize_estimator(candidate.estimator_name)
    inf = candidate.inference_mode

    if candidate.research_only or est in RESEARCH_ONLY_ESTIMATORS:
        return (
            DecisionRole.RESEARCH_ONLY,
            "research_only_estimator",
            (),
            ("production_decision", "mmm_ingress", "calibration_signal"),
            ("Research-only path — no production decision posture.",),
        )

    if is_placebo_inference_mode(inf):
        return (
            DecisionRole.FALSIFICATION_CHECK,
            None,
            ("falsification", "trust_report_context"),
            ("primary_estimator", "diagnostic_comparator", "governed_uncertainty"),
            ("Placebo is falsification/inference — not an estimator readout.",),
        )

    if geometry_verdict.classification in (
        GeometryClassification.BLOCKED_GEOMETRY,
        GeometryClassification.BLOCKED_MISSING_POOLING_RULE,
        GeometryClassification.BLOCKED_MISSING_ESTIMAND_BRIDGE,
        GeometryClassification.BLOCKED_MISSING_ADAPTER,
        GeometryClassification.BLOCKED_UNSUPPORTED_INFERENCE_GEOMETRY,
        GeometryClassification.BLOCKED_INTERFACE,
    ):
        reason = geometry_verdict.issues[0].message if geometry_verdict.issues else "geometry_blocked"
        return (
            DecisionRole.BLOCKED,
            reason,
            (),
            ("decision_primary", "diagnostic_comparison", "mmm_ingress"),
            (reason,),
        )

    if interval_verdict is not None:
        if interval_verdict.classification in (
            IntervalSemanticsClassification.BLOCKED_INTERFACE,
            IntervalSemanticsClassification.BLOCKED_INVALID_INTERVAL,
        ):
            msg = interval_verdict.policy_note or interval_verdict.classification.value
            return (
                DecisionRole.EXCLUDED,
                msg,
                (),
                ("decision_primary", "diagnostic_comparison"),
                (msg,),
            )

    if not candidate.callable:
        return (
            DecisionRole.EXCLUDED,
            "not_callable",
            (),
            ("decision_use",),
            ("Candidate did not complete — excluded from comparison.",),
        )

    if _is_primary_null_monitor_candidate(candidate, geometry_type=geometry_type, design=design):
        return (
            DecisionRole.PRIMARY_NULL_MONITOR,
            None,
            ("null_monitor", "trust_report_primary"),
            ("mmm_lift", "governed_uncertainty_export"),
            ("Primary null-monitor only — not MMM lift (E5).",),
        )

    if governance_bucket == "characterized_restricted":
        return (
            DecisionRole.DIAGNOSTIC_COMPARATOR,
            None,
            ("diagnostic_comparison", "trust_report_context"),
            ("decision_primary", "calibration_signal", "mmm_ingress", "governed_uncertainty"),
            ("Characterized restricted diagnostic — not governed uncertainty.",),
        )

    if governance_bucket == "callable_unverified_interval_semantics":
        if allow_sensitivity_in_comparison:
            return (
                DecisionRole.SENSITIVITY_CHECK,
                None,
                ("sensitivity_context",),
                ("decision_primary", "diagnostic_comparator", "calibration_signal"),
                ("Callable with unverified interval semantics — sensitivity only.",),
            )
        return (
            DecisionRole.EXCLUDED,
            "callable_unverified_interval_semantics",
            (),
            ("decision_primary", "diagnostic_comparator", "governed_uncertainty"),
            (
                "Excluded from comparison — interval semantics unverified "
                "(e.g. elevated null FPR on battery).",
            ),
        )

    if governance_bucket in ("blocked", "blocked_interface", "invalid_by_interface", "invalid_by_geometry"):
        return (
            DecisionRole.BLOCKED,
            governance_bucket,
            (),
            ("decision_use",),
            (f"Governance bucket {governance_bucket}.",),
        )

    if governance_bucket == "already_characterized" and inf == "UnitJackKnife":
        return (
            DecisionRole.PRIMARY_NULL_MONITOR,
            None,
            ("null_monitor", "trust_report_primary"),
            ("mmm_lift",),
            ("Already characterized SCM+JK — null monitor path when policy allows.",),
        )

    return (
        DecisionRole.DIAGNOSTIC_COMPARATOR,
        None,
        ("diagnostic_context",),
        ("decision_primary", "calibration_signal", "mmm_ingress"),
        ("Default restricted diagnostic context — not promotion.",),
    )


def resolve_eligible_readout(
    candidate: CandidateReadout,
    *,
    design: DesignProfile,
    data: DataProfile,
    geometry: GeometryProfile,
    estimand: EstimandProfile,
    allow_sensitivity_in_comparison: bool = False,
) -> EligibleReadoutProfile:
    """Resolve one candidate to an ``EligibleReadoutProfile`` via F-GEO then F-INF."""
    est = _normalize_estimator(candidate.estimator_name)
    inf = candidate.inference_mode
    geo_type = geometry.geometry_type

    geometry_request = GeometryReadoutRequest(
        estimator_name=est,
        inference_mode=inf,
        geometry_type=geo_type,
        n_treated=data.n_treated,
        n_control=data.n_control,
        n_test_grps=data.n_test_grps,
        pooling_rule_id=design.pooling_rule_id,
        pooled_claim=geometry.pooled_claim,
        supergeo_adapter_id=geometry.supergeo_adapter_id,
        trim_estimand_bridge_id=geometry.trim_estimand_bridge_id,
        single_treated_geometry=geometry.single_treated_geometry,
        callable=candidate.callable,
    )

    geometry_verdict = classify_geometry_support(geometry_request)

    interval_verdict: Optional[IntervalSemanticsVerdict] = None
    if candidate.interval_readout is not None:
        interval_verdict = classify_interval_semantics(
            candidate.interval_readout,
            require_metadata_bindings=False,
        )
        assert_not_governed_uncertainty(interval_verdict, context=f"{est}+{inf}")

    governance_bucket = _governance_bucket(
        candidate, geometry_type=geo_type, interval_verdict=interval_verdict
    )
    catalog_st, cs_eligible, mmm_ready = _catalog_status(candidate)

    role, exclusion, allowed, forbidden, warnings = _assign_role(
        candidate,
        geometry_verdict=geometry_verdict,
        interval_verdict=interval_verdict,
        governance_bucket=governance_bucket,
        geometry_type=geo_type,
        design=design,
        allow_sensitivity_in_comparison=allow_sensitivity_in_comparison,
    )

    runnable = RunnableStatus.RUNNABLE if candidate.callable and role not in (
        DecisionRole.BLOCKED,
        DecisionRole.RESEARCH_ONLY,
    ) else RunnableStatus.BLOCKED_BY_POLICY
    if not candidate.callable:
        runnable = RunnableStatus.NOT_RUNNABLE

    interval_status = (
        interval_verdict.classification.value if interval_verdict else "not_evaluated"
    )

    combo_key = (
        est,
        inf,
        _geometry_mode_key(geo_type, candidate.geometry_mode),
    )
    is_governed = combo_key in GOVERNED_UNCERTAINTY_EXPORT_ALLOWLIST

    return EligibleReadoutProfile(
        estimator=est,
        inference=inf,
        geometry_type=geo_type.value,
        estimand=estimand.target_estimand,
        runnable_status=runnable,
        geometry_status=geometry_verdict.classification.value,
        interval_status=interval_status,
        catalog_status=catalog_st,
        governance_bucket=governance_bucket,
        assigned_role=role,
        allowed_uses=allowed,
        forbidden_uses=forbidden,
        required_warnings=warnings,
        exclusion_reason=exclusion,
        is_governed_uncertainty=is_governed,
        calibration_signal_eligible=cs_eligible and role == DecisionRole.PRIMARY_NULL_MONITOR,
        mmm_ready=mmm_ready,
    )


def resolve_eligible_readouts(
    candidates: Sequence[CandidateReadout],
    *,
    design: DesignProfile,
    data: DataProfile,
    geometry: GeometryProfile,
    estimand: EstimandProfile,
    allow_sensitivity_in_comparison: bool = False,
) -> list[EligibleReadoutProfile]:
    return [
        resolve_eligible_readout(
            c,
            design=design,
            data=data,
            geometry=geometry,
            estimand=estimand,
            allow_sensitivity_in_comparison=allow_sensitivity_in_comparison,
        )
        for c in candidates
    ]


def _sign(x: float) -> int:
    if not np.isfinite(x) or abs(x) < 1e-12:
        return 0
    return 1 if x > 0 else -1


def build_evidence_decision(
    profiles: Sequence[EligibleReadoutProfile],
    *,
    point_effects: Optional[dict[Tuple[str, str], float]] = None,
    falsification_outcomes: Optional[dict[Tuple[str, str], bool]] = None,
    mmm_status: str = MMM_DEFAULT_STATUS,
    effect_tolerance: float = 1e-9,
) -> EvidenceDecisionProfile:
    """
  Compare role-eligible readouts and emit decision posture.

  No silent averaging — compares directions only.
    """
    point_effects = point_effects or {}
    falsification_outcomes = falsification_outcomes or {}

    primary = [p for p in profiles if p.assigned_role == DecisionRole.PRIMARY_NULL_MONITOR]
    diagnostics = [p for p in profiles if p.assigned_role == DecisionRole.DIAGNOSTIC_COMPARATOR]
    falsification = [p for p in profiles if p.assigned_role == DecisionRole.FALSIFICATION_CHECK]
    sensitivity = [p for p in profiles if p.assigned_role == DecisionRole.SENSITIVITY_CHECK]
    excluded = [
        p
        for p in profiles
        if p.assigned_role in (DecisionRole.EXCLUDED, DecisionRole.BLOCKED, DecisionRole.RESEARCH_ONLY)
    ]

    out = EvidenceDecisionProfile(
        diagnostic_comparators=list(diagnostics),
        falsification_checks=list(falsification),
        sensitivity_checks=list(sensitivity),
        excluded_readouts=list(excluded),
        mmm_status=mmm_status,
        mmm_action=MmmAction.EXCLUDE_FROM_MMM,
    )

    warnings: list[str] = list(
        w for p in profiles for w in p.required_warnings
    )

    # Falsification failures first
    fals_failures = []
    for p in falsification:
        key = (p.estimator, p.inference)
        passed = falsification_outcomes.get(key)
        if passed is False:
            fals_failures.append(p)

    if fals_failures:
        out.falsification_checks = list(falsification)
        out.agreement_status = AgreementStatus.FALSIFICATION_FAILURE
        out.conflict_status = "placebo_or_falsification_rejected"
        out.final_decision_posture = DecisionPosture.BLOCKED_FOR_DECISION_USE
        out.trust_report_action = TrustReportAction.EMIT_WARNING
        out.calibration_signal_action = CalibrationSignalAction.DIAGNOSTIC_CONTEXT_ONLY
        out.required_warnings = warnings + ["Falsification check failed — downgrade decision posture."]
        out.recommended_next_action = "recommend_follow_up_experiment"
        return out

    if not primary:
        out.agreement_status = AgreementStatus.INSUFFICIENT_VALID_EVIDENCE
        out.final_decision_posture = DecisionPosture.INCONCLUSIVE
        out.trust_report_action = TrustReportAction.TRUST_REPORT_ONLY
        out.recommended_next_action = "no_decision"
        out.required_warnings = warnings
        if diagnostics:
            out.final_decision_posture = DecisionPosture.DIAGNOSTIC_ONLY
        return out

    if len(primary) > 1:
        warnings.append("Multiple primary_null_monitor candidates — using first per policy (no averaging).")

    out.primary_readout = primary[0]
    p_key = (out.primary_readout.estimator, out.primary_readout.inference)
    p_effect = point_effects.get(p_key)
    p_sign = _sign(p_effect) if p_effect is not None else None

    disagreeing: list[EligibleReadoutProfile] = []
    aligned: list[EligibleReadoutProfile] = []

    for d in diagnostics:
        d_key = (d.estimator, d.inference)
        d_effect = point_effects.get(d_key)
        if p_sign is None or d_effect is None or not np.isfinite(d_effect):
            continue
        d_sign = _sign(d_effect)
        if d_sign == 0 or p_sign == 0:
            continue
        if d_sign != p_sign:
            disagreeing.append(d)
        else:
            aligned.append(d)

    if disagreeing:
        out.agreement_status = AgreementStatus.DIAGNOSTIC_DISAGREEMENT
        out.conflict_status = "primary_vs_diagnostic_sign_mismatch"
        out.final_decision_posture = DecisionPosture.PROCEED_WITH_CAVEATS
        out.trust_report_action = TrustReportAction.EMIT_WARNING
        out.calibration_signal_action = CalibrationSignalAction.TRUST_REPORT_ONLY
        out.required_warnings = warnings + [
            "Diagnostic comparator(s) disagree with primary direction — no silent averaging.",
        ]
        out.recommended_next_action = "trust_report_only"
        return out

    if p_sign is not None and p_sign > 0 and aligned:
        out.agreement_status = AgreementStatus.EVIDENCE_ALIGNED_POSITIVE_WITH_CAVEATS
        out.final_decision_posture = DecisionPosture.PROCEED_WITH_CAVEATS
    elif p_sign is not None and aligned:
        out.agreement_status = AgreementStatus.EVIDENCE_ALIGNED_LOW_CONCERN
        out.final_decision_posture = DecisionPosture.PROCEED_WITH_CONFIDENCE
    elif diagnostics:
        out.agreement_status = AgreementStatus.EVIDENCE_ALIGNED_LOW_CONCERN
        out.final_decision_posture = DecisionPosture.DIAGNOSTIC_ONLY
    else:
        out.agreement_status = AgreementStatus.EVIDENCE_ALIGNED_LOW_CONCERN
        out.final_decision_posture = DecisionPosture.TRUST_REPORT_ONLY

    out.trust_report_action = TrustReportAction.TRUST_REPORT_ONLY
    if out.primary_readout.calibration_signal_eligible:
        out.calibration_signal_action = CalibrationSignalAction.EXPORT_CALIBRATION_SIGNAL
    else:
        out.calibration_signal_action = CalibrationSignalAction.TRUST_REPORT_ONLY

    out.mmm_action = MmmAction.EXCLUDE_FROM_MMM
    out.mmm_status = mmm_status
    out.required_warnings = warnings
    out.recommended_next_action = "no_decision"
    return out


__all__ = [
    "AUDIT_010_DECISION_BUCKETS",
    "AgreementStatus",
    "CalibrationSignalAction",
    "CandidateReadout",
    "DecisionPosture",
    "DecisionRole",
    "DesignProfile",
    "DataProfile",
    "EligibleReadoutProfile",
    "EstimandProfile",
    "EvidenceDecisionProfile",
    "GeometryProfile",
    "MmmAction",
    "MMM_DEFAULT_STATUS",
    "RunnableStatus",
    "TrustReportAction",
    "build_evidence_decision",
    "resolve_eligible_readout",
    "resolve_eligible_readouts",
]
