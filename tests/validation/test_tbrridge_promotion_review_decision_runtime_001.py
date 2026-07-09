"""Tests for TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001."""

from __future__ import annotations

from panel_exp.validation.tbrridge_promotion_evidence_packet_assembly_runtime_001 import (
    EXACT_INSTRUMENT_IDENTITY,
    TBRRidgeEvidenceReference,
    TBRRidgePacketReadinessStatus,
    TBRRidgePromotionEvidencePacket,
    TBRRidgePromotionEvidencePacketInput,
    TBRRidgePromotionReviewEligibilityStatus,
    assemble_tbrridge_promotion_evidence_packet,
)
from panel_exp.validation.tbrridge_promotion_review_decision_runtime_001 import (
    TBRRidgePromotionReviewDecisionInput,
    TBRRidgePromotionReviewDecisionStatus,
    decide_tbrridge_promotion_review,
    run_validation,
)

_PROHIBITED = (
    "method_promotion",
    "instrument_promotion",
    "catalog_unblock",
    "claim_authorization_runtime_bypass",
    "trust_report_bypass",
)


def _ref(category: str) -> TBRRidgeEvidenceReference:
    return TBRRidgeEvidenceReference(
        evidence_category=category,
        artifact_id=f"ARTIFACT_{category.upper()}",
        artifact_ref=f"docs/track_d/ARTIFACT_{category.upper()}.md",
    )


def _full_evidence() -> tuple[TBRRidgeEvidenceReference, ...]:
    return (
        _ref("instrument_identity"),
        _ref("claim_boundary"),
        _ref("metric_estimand_alignment"),
        _ref("null_control_false_positive"),
        _ref("directional_error"),
        _ref("positive_control_recovery"),
        _ref("sensitivity"),
        _ref("readout_compatibility"),
    )


def _ready_packet(**overrides: object) -> TBRRidgePromotionEvidencePacket:
    payload = {
        "packet_id": "test_packet",
        "instrument_identity": EXACT_INSTRUMENT_IDENTITY,
        "evidence_references": _full_evidence(),
        "lineage": {"source": "unit_test"},
        "warnings": ("packet_warning",),
    }
    payload.update(overrides)
    return assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(**payload)
    )


def _decide(
    packet: TBRRidgePromotionEvidencePacket | dict,
    *,
    surface: str = "restricted_review",
    **kwargs: object,
) -> object:
    return decide_tbrridge_promotion_review(
        TBRRidgePromotionReviewDecisionInput(
            decision_id="test_decision",
            packet=packet,
            requested_decision_surface=surface,
            warnings=("input_warning",),
            lineage={"decision": "unit_test"},
            **kwargs,
        )
    )


def test_ready_eligible_restricted_review_approves_continuation() -> None:
    packet = _ready_packet()
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
    )
    assert "continue_restricted_review_diagnostics" in decision.allowed_next_actions


def test_approval_emits_fixed_non_authorization_statuses() -> None:
    decision = _decide(_ready_packet())
    assert decision.claim_authorization_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.catalog_status == "NOT_UNBLOCKED_BY_THIS_DECISION"
    assert decision.production_compatibility_status == "NOT_AUTHORIZED_BY_THIS_DECISION"
    assert decision.method_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"
    assert decision.instrument_promotion_status == "NOT_PROMOTED_BY_THIS_DECISION"


def test_missing_evidence_requests_additional_evidence() -> None:
    refs = tuple(r for r in _full_evidence() if r.evidence_category != "sensitivity")
    packet = _ready_packet(evidence_references=refs)
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REQUEST_ADDITIONAL_EVIDENCE
    )
    assert "collect_missing_evidence_refs" in decision.required_followups
    assert "sensitivity" in decision.missing_evidence


def test_identity_mismatch_rejected() -> None:
    packet = _ready_packet(
        instrument_identity="geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.production"
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_IDENTITY_MISMATCH
    )


def test_claim_boundary_missing_rejected() -> None:
    refs = tuple(r for r in _full_evidence() if r.evidence_category != "claim_boundary")
    packet = _ready_packet(evidence_references=refs)
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_CLAIM_BOUNDARY_VIOLATION
    )


def test_unsupported_surface_rejected() -> None:
    packet = _ready_packet()
    decision = _decide(packet, surface="method_promotion")
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_UNSUPPORTED_SURFACE
    )


def test_production_requested_defers() -> None:
    packet = _ready_packet()
    decision = _decide(packet, surface="production")
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW
    )


def test_catalog_requested_defers() -> None:
    packet = _ready_packet()
    decision = _decide(packet, surface="catalog_unblock")
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.DEFER_PENDING_CATALOG_GOVERNANCE_REVIEW
    )


def test_cross_inference_rejected() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="cross_inference",
            instrument_identity=EXACT_INSTRUMENT_IDENTITY,
            evidence_references=_full_evidence(),
            requested_inference_family="bootstrap",
        )
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_CROSS_INFERENCE_FAMILY
    )


def test_cross_geometry_rejected() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(
        TBRRidgePromotionEvidencePacketInput(
            packet_id="cross_geometry",
            instrument_identity=EXACT_INSTRUMENT_IDENTITY,
            evidence_references=_full_evidence(),
            requested_geometry="aggregate_pooled",
        )
    )
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_CROSS_GEOMETRY
    )


def test_packet_not_ready_no_decision() -> None:
    packet = {
        "packet_id": "",
        "instrument_identity": EXACT_INSTRUMENT_IDENTITY,
        "packet_readiness_status": TBRRidgePacketReadinessStatus.PACKET_NOT_REQUESTED.value,
        "promotion_review_eligibility_status": (
            TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE.value
        ),
        "missing_evidence": [],
        "blockers": [],
        "warnings": [],
        "lineage": {},
        "created_from_artifacts": [],
        "evidence_by_category": {},
    }
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.NO_DECISION_PACKET_NOT_READY
    )


def test_method_validity_blocker_rejected() -> None:
    packet = _ready_packet().to_dict()
    packet["blockers"] = ("FAILED_NULL_CONTROL_EVIDENCE",)
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.REJECT_FOR_METHOD_VALIDITY
    )
    assert "repair_or_reject_instrument_validation" in decision.required_followups


def test_blockers_missing_evidence_warnings_lineage_preserved() -> None:
    refs = tuple(r for r in _full_evidence() if r.evidence_category != "directional_error")
    packet = _ready_packet(evidence_references=refs)
    decision = _decide(packet)
    assert "directional_error" in decision.missing_evidence
    assert decision.blockers
    assert "packet_warning" in decision.warnings
    assert "input_warning" in decision.warnings
    assert decision.lineage.get("source") == "unit_test"
    assert decision.lineage.get("decision") == "unit_test"


def test_prohibited_next_actions_always_present() -> None:
    decision = _decide(_ready_packet())
    for action in _PROHIBITED:
        assert action in decision.prohibited_next_actions


def test_dict_packet_input_supported() -> None:
    packet = _ready_packet().to_dict()
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
    )


def test_runtime_does_not_score_raw_evidence() -> None:
    packet = _ready_packet().to_dict()
    packet["evidence_by_category"]["null_control_false_positive"] = [
        {"artifact_id": "X", "artifact_ref": "Y", "quality_score": 0.99}
    ]
    decision = _decide(packet)
    assert (
        decision.decision_status
        == TBRRidgePromotionReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
    )
    assert "quality_score" not in str(decision.evidence_summary)


def test_run_validation_sample() -> None:
    summary = run_validation(write_summary=False)
    assert summary["review_decision_runtime_implemented"] is True
    assert summary["method_promoted"] is False
    assert summary["recommended_next_artifact"] == "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001"
