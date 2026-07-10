"""Tests for SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001."""

from __future__ import annotations

from panel_exp.validation.scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001 import (
    CANONICAL_INSTRUMENT_IDENTITY,
    CATALOG_ALIAS,
    SCMJackknifeNullMonitorEvidenceReference,
    SCMJackknifeNullMonitorPacketReadinessStatus,
    SCMJackknifeNullMonitorPromotionEvidencePacket,
    SCMJackknifeNullMonitorPromotionEvidencePacketInput,
    SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
    assemble_scm_jackknife_null_monitor_promotion_evidence_packet,
)
from panel_exp.validation.scm_jackknife_null_monitor_review_decision_runtime_001 import (
    SCMJackknifeNullMonitorReviewDecisionInput,
    SCMJackknifeNullMonitorReviewDecisionStatus,
    decide_scm_jackknife_null_monitor_review,
    run_validation,
)

_PROHIBITED = (
    "scm_promotion",
    "scm_jackknife_promotion",
    "catalog_unblock",
    "claim_authorization_runtime_bypass",
    "trust_report_bypass",
)

_REQUIRED_CATEGORIES = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "jackknife_stability",
    "directional_error",
    "donor_pool_diagnostics",
    "pre_period_fit_diagnostics",
    "sensitivity",
    "readout_compatibility",
)


def _ref(category: str) -> SCMJackknifeNullMonitorEvidenceReference:
    return SCMJackknifeNullMonitorEvidenceReference(
        evidence_id=f"{category}_001",
        evidence_category=category,
        artifact_ref=f"docs/track_d/{category.upper()}_001.md",
    )


def _full_evidence() -> list[SCMJackknifeNullMonitorEvidenceReference]:
    return [_ref(cat) for cat in _REQUIRED_CATEGORIES]


def _ready_packet(**overrides: object) -> SCMJackknifeNullMonitorPromotionEvidencePacket:
    payload = {
        "packet_id": "test_packet",
        "catalog_alias": CATALOG_ALIAS,
        "evidence_refs": _full_evidence(),
        "lineage": {"source": "unit_test"},
        "warnings": ["packet_warning"],
    }
    payload.update(overrides)
    return assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(**payload)
    )


def _packet_dict(
    *,
    readiness: SCMJackknifeNullMonitorPacketReadinessStatus,
    eligibility: SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
    **extra: object,
) -> dict:
    base = {
        "packet_id": "dict_packet",
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "catalog_alias": CATALOG_ALIAS,
        "packet_readiness_status": readiness.value,
        "promotion_review_eligibility_status": eligibility.value,
        "missing_evidence": [],
        "blockers": [],
        "warnings": ["dict_warning"],
        "lineage": {"packet": "dict"},
        "evidence_by_category": {},
    }
    base.update(extra)
    return base


def _decide(
    packet: SCMJackknifeNullMonitorPromotionEvidencePacket | dict | None,
    *,
    surface: str = "null_monitor",
    **kwargs: object,
) -> object:
    return decide_scm_jackknife_null_monitor_review(
        SCMJackknifeNullMonitorReviewDecisionInput(
            decision_id="test_decision",
            packet=packet or {},
            requested_decision_surface=surface,
            warnings=["input_warning"],
            lineage={"decision": "unit_test"},
            **kwargs,
        )
    )


def test_ready_eligible_null_monitor_approves_continuation() -> None:
    packet = _ready_packet()
    decision = _decide(packet)
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.APPROVE_NULL_MONITOR_REVIEW_CONTINUATION
    )
    assert "continue_null_monitor_diagnostics" in decision.allowed_next_actions
    assert decision.instrument_identity == CANONICAL_INSTRUMENT_IDENTITY
    assert decision.catalog_alias == CATALOG_ALIAS


def test_approval_emits_fixed_non_authorization_statuses() -> None:
    decision = _decide(_ready_packet())
    assert decision.claim_authorization_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.catalog_status == "NOT_UNBLOCKED_BY_THIS_DECISION"
    assert decision.production_compatibility_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.method_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert decision.instrument_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert decision.null_monitor_scope_status == "NULL_MONITOR_ONLY"


def test_production_surface_defers() -> None:
    decision = _decide(_ready_packet(), surface="production")
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW
    )


def test_catalog_surface_defers() -> None:
    decision = _decide(_ready_packet(), surface="catalog_unblock")
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW
    )


def test_no_packet_not_ready() -> None:
    decision = _decide(None)
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY
    )
    assert "assemble_valid_scm_null_monitor_packet_first" in decision.required_followups


def test_packet_not_requested_not_ready() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_NOT_REQUESTED,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY
    )


def test_identity_mismatch_rejected() -> None:
    packet = _ready_packet(
        instrument_identity="geo.scm.placebo.single_cell.delta_mu.null_monitor"
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_IDENTITY_MISMATCH
    )


def test_cross_inference_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CROSS_INFERENCE_FAMILY,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CROSS_INFERENCE_FAMILY
    )


def test_cross_geometry_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CROSS_GEOMETRY,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CROSS_GEOMETRY
    )


def test_cross_estimand_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CROSS_ESTIMAND,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CROSS_ESTIMAND
    )


def test_claim_boundary_missing_rejected() -> None:
    refs = [r for r in _full_evidence() if r.evidence_category != "claim_boundary"]
    decision = _decide(_ready_packet(evidence_refs=refs))
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_CLAIM_BOUNDARY_VIOLATION
    )


def test_null_monitor_scope_violation_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION
    )


def test_method_validity_blocker_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT,
            blockers=["failed_jackknife_stability_evidence"],
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_METHOD_VALIDITY
    )


def test_missing_evidence_requests_additional() -> None:
    refs = [r for r in _full_evidence() if r.evidence_category != "sensitivity"]
    decision = _decide(_ready_packet(evidence_refs=refs))
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE
    )
    assert "sensitivity" in decision.missing_evidence


def test_partial_diagnostic_requests_additional() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
            missing_evidence=["jackknife_stability"],
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE
    )


def test_unsupported_surface_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
            eligibility=SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == SCMJackknifeNullMonitorReviewDecisionStatus.REJECT_FOR_UNSUPPORTED_SURFACE
    )


def test_blockers_missing_evidence_warnings_lineage_preserved() -> None:
    packet = _ready_packet()
    decision = _decide(packet)
    assert decision.lineage.get("source") == "unit_test"
    assert decision.lineage.get("decision") == "unit_test"
    assert "input_warning" in decision.warnings
    assert "packet_warning" in decision.warnings


def test_prohibited_actions_always_present() -> None:
    decision = _decide(_ready_packet())
    for action in _PROHIBITED:
        assert action in decision.prohibited_next_actions


def test_no_raw_evidence_quality_scoring() -> None:
    decision = _decide(_ready_packet())
    payload = decision.to_dict()
    forbidden = (
        "evidence_quality_score",
        "raw_evidence_quality_scored",
        "quality_score",
        "evidence_score",
    )
    for key in forbidden:
        assert key not in payload


def test_run_validation_approves_sample() -> None:
    summary = run_validation(write_summary=False)
    assert summary["review_decision_runtime_implemented"] is True
    assert summary["runtime_implemented"] is True
    assert summary["scm_promoted"] is False
    assert summary["recommended_next_artifact"] == "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001"
