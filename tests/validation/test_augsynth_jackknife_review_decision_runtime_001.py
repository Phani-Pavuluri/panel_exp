"""Tests for AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001."""

from __future__ import annotations

from panel_exp.validation.augsynth_jackknife_promotion_evidence_packet_runtime_001 import (
    ALIAS_RELATED_RESEARCH_IDENTITY,
    CANONICAL_INSTRUMENT_IDENTITY,
    AugSynthJackknifeEvidenceReference,
    AugSynthJackknifePacketReadinessStatus,
    AugSynthJackknifePromotionEvidencePacket,
    AugSynthJackknifePromotionEvidencePacketInput,
    AugSynthJackknifePromotionReviewEligibilityStatus,
    assemble_augsynth_jackknife_promotion_evidence_packet,
)
from panel_exp.validation.augsynth_jackknife_review_decision_runtime_001 import (
    AugSynthJackknifeReviewDecisionInput,
    AugSynthJackknifeReviewDecisionStatus,
    decide_augsynth_jackknife_review,
    run_validation,
)

_REQUIRED = (
    "instrument_identity",
    "claim_boundary",
    "metric_estimand_alignment",
    "null_control_false_positive",
    "directional_error",
    "positive_control_recovery",
    "sensitivity",
    "readout_compatibility",
    "donor_pool_diagnostics",
    "pre_period_fit_diagnostics",
    "augmentation_component_diagnostics",
    "synthetic_weight_diagnostics",
    "regularization_or_model_component_diagnostics",
    "jackknife_stability",
    "method_disagreement_or_scm_bridge",
    "support_overlap_or_donor_hull_stress",
)

_PROHIBITED = (
    "augsynth_promotion",
    "method_promotion",
    "catalog_unblock",
    "generic_adapter_profile_for_augsynth_registration",
    "claim_authorization_runtime_bypass",
    "trust_report_bypass",
)


def _ref(category: str) -> AugSynthJackknifeEvidenceReference:
    return AugSynthJackknifeEvidenceReference(
        evidence_id=f"{category}_001",
        evidence_category=category,
        artifact_ref=f"docs/track_d/{category.upper()}_001.md",
    )


def _full_evidence() -> list[AugSynthJackknifeEvidenceReference]:
    return [_ref(cat) for cat in _REQUIRED]


def _ready_packet(**overrides: object) -> AugSynthJackknifePromotionEvidencePacket:
    payload = {
        "packet_id": "test_packet",
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "evidence_references": _full_evidence(),
        "lineage": {"source": "unit_test"},
        "warnings": ["packet_warning"],
    }
    payload.update(overrides)
    return assemble_augsynth_jackknife_promotion_evidence_packet(
        AugSynthJackknifePromotionEvidencePacketInput(**payload)
    )


def _packet_dict(
    *,
    readiness: AugSynthJackknifePacketReadinessStatus,
    eligibility: AugSynthJackknifePromotionReviewEligibilityStatus,
    **extra: object,
) -> dict:
    base = {
        "packet_id": "dict_packet",
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "alias_related_identity": ALIAS_RELATED_RESEARCH_IDENTITY,
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
    packet: AugSynthJackknifePromotionEvidencePacket | dict | None,
    *,
    surface: str = "restricted_review",
    **kwargs: object,
) -> object:
    return decide_augsynth_jackknife_review(
        AugSynthJackknifeReviewDecisionInput(
            decision_id="test_decision",
            packet=packet or {},
            requested_decision_surface=surface,
            warnings=["input_warning"],
            lineage={"decision": "unit_test"},
            **kwargs,
        )
    )


def test_ready_eligible_restricted_review_approves_continuation() -> None:
    packet = _ready_packet()
    decision = _decide(packet)
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
    )
    assert "continue_augsynth_restricted_review_diagnostics" in decision.allowed_next_actions
    assert decision.instrument_identity == CANONICAL_INSTRUMENT_IDENTITY
    assert decision.alias_related_identity == ALIAS_RELATED_RESEARCH_IDENTITY


def test_approval_emits_fixed_non_authorization_statuses() -> None:
    decision = _decide(_ready_packet())
    assert decision.claim_authorization_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.catalog_status == "NOT_UNBLOCKED_BY_THIS_DECISION"
    assert decision.production_compatibility_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.method_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert decision.instrument_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert decision.generic_adapter_status == "NOT_REGISTERED_BY_THIS_DECISION"
    assert decision.mip_decisioning_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.trust_report_bypass_status == "NOT_BYPASSED_BY_THIS_DECISION"


def test_production_surface_defers() -> None:
    decision = _decide(_ready_packet(), surface="production")
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW
    )


def test_catalog_surface_defers() -> None:
    decision = _decide(_ready_packet(), surface="catalog_unblock")
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW
    )


def test_no_packet_not_ready() -> None:
    decision = _decide(None)
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY
    )
    assert "assemble_valid_augsynth_jackknife_packet_first" in decision.required_followups


def test_packet_not_requested_not_ready() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_NOT_REQUESTED,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY
    )


def test_research_only_substitution_rejected() -> None:
    packet = _ready_packet(instrument_identity=ALIAS_RELATED_RESEARCH_IDENTITY)
    decision = _decide(packet)
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION
    )


def test_alias_substitution_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_ALIAS_SUBSTITUTION_ATTEMPT,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_ALIAS_SUBSTITUTION,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_ALIAS_SUBSTITUTION
    )


def test_identity_mismatch_rejected() -> None:
    packet = _ready_packet(
        instrument_identity="geo.augsynth.placebo.single_cell.delta_mu.diagnostic_interval.restricted_review"
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_IDENTITY_MISMATCH
    )


def test_cross_inference_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_CROSS_INFERENCE_FAMILY,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_CROSS_INFERENCE_FAMILY
    )


def test_cross_geometry_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_CROSS_GEOMETRY,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_CROSS_GEOMETRY
    )


def test_cross_estimand_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_CROSS_ESTIMAND,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_CROSS_ESTIMAND
    )


def test_claim_boundary_missing_rejected() -> None:
    refs = [_ref(cat) for cat in _REQUIRED if cat != "claim_boundary"]
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        AugSynthJackknifePromotionEvidencePacketInput(
            packet_id="missing_claim",
            evidence_references=refs,
        )
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_CLAIM_BOUNDARY_VIOLATION
    )


def test_scope_violation_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_SCOPE_VIOLATION,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_SCOPE_VIOLATION,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_SCOPE_VIOLATION
    )


def test_method_validity_blocker_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT,
            blockers=["failed_jackknife_stability"],
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_METHOD_VALIDITY
    )


def test_missing_evidence_requests_additional() -> None:
    refs = [_ref(cat) for cat in _REQUIRED if cat != "jackknife_stability"]
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        AugSynthJackknifePromotionEvidencePacketInput(
            packet_id="missing_jk",
            evidence_references=refs,
        )
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE
    )
    assert "jackknife_stability" in decision.missing_evidence


def test_partial_diagnostic_requests_additional() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
            missing_evidence=["donor_pool_diagnostics"],
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE
    )


def test_unsupported_surface_rejected() -> None:
    decision = _decide(
        _packet_dict(
            readiness=AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE,
            eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CLAIM_REVIEW,
        )
    )
    assert (
        decision.decision_status
        == AugSynthJackknifeReviewDecisionStatus.REJECT_FOR_UNSUPPORTED_SURFACE
    )


def test_blockers_missing_evidence_warnings_lineage_preserved() -> None:
    packet = _packet_dict(
        readiness=AugSynthJackknifePacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY,
        eligibility=AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        missing_evidence=["sensitivity"],
        blockers=["AUGSYNTH_PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE"],
        warnings=["preserve_me"],
        lineage={"artifact": "packet"},
    )
    decision = _decide(packet)
    assert "sensitivity" in decision.missing_evidence
    assert "AUGSYNTH_PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE" in decision.blockers
    assert "preserve_me" in decision.warnings
    assert "input_warning" in decision.warnings
    assert decision.lineage.get("artifact") == "packet"
    assert decision.lineage.get("decision") == "unit_test"


def test_prohibited_actions_always_present() -> None:
    decision = _decide(_ready_packet())
    for action in _PROHIBITED:
        assert action in decision.prohibited_next_actions


def test_generic_adapter_registration_prohibited() -> None:
    decision = _decide(_ready_packet())
    assert "generic_adapter_profile_for_augsynth_registration" in decision.prohibited_next_actions


def test_no_raw_evidence_quality_scoring_fields() -> None:
    decision = _decide(_ready_packet())
    payload = decision.to_dict()
    for key in payload:
        assert "quality_score" not in key.lower()
        assert "evidence_quality" not in key.lower()


def test_run_validation_sample() -> None:
    summary = run_validation(write_summary=False)
    assert summary["runtime_implemented"] is True
    assert summary["augsynth_decision_runtime_implemented"] is True
    assert (
        summary["validation_sample_decision_status"]
        == AugSynthJackknifeReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION.value
    )
