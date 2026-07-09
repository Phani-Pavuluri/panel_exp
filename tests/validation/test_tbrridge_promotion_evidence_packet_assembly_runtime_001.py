"""Tests for TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001."""

from __future__ import annotations

from panel_exp.validation.tbrridge_promotion_evidence_packet_assembly_runtime_001 import (
    EXACT_INSTRUMENT_IDENTITY,
    TBRRidgeEvidenceReference,
    TBRRidgePacketReadinessStatus,
    TBRRidgePromotionEvidencePacketInput,
    TBRRidgePromotionReviewEligibilityStatus,
    assemble_tbrridge_promotion_evidence_packet,
    run_validation,
)


def _ref(category: str, suffix: str = "001") -> TBRRidgeEvidenceReference:
    return TBRRidgeEvidenceReference(
        evidence_category=category,
        artifact_id=f"ARTIFACT_{category.upper()}_{suffix}",
        artifact_ref=f"docs/track_d/ARTIFACT_{category.upper()}_{suffix}.md",
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


def _base_input(**overrides: object) -> TBRRidgePromotionEvidencePacketInput:
    payload = {
        "packet_id": "test_packet",
        "instrument_identity": EXACT_INSTRUMENT_IDENTITY,
        "evidence_references": _full_evidence(),
        "lineage": {"source": "unit_test"},
        "warnings": ("input_warning",),
    }
    payload.update(overrides)
    return TBRRidgePromotionEvidencePacketInput(**payload)


def test_all_required_evidence_ready_and_eligible() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(_base_input())
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT
    )
    assert packet.missing_evidence == ()
    assert packet.blockers == ()
    assert packet.estimator_family == "tbrridge"
    assert packet.inference_family == "kfold"
    assert packet.geometry == "single_cell"
    assert packet.estimand == "delta_mu"
    assert packet.interval_semantics == "diagnostic_interval"
    assert packet.surface == "restricted_review"


def test_missing_claim_boundary_blocked() -> None:
    refs = tuple(r for r in _full_evidence() if r.evidence_category != "claim_boundary")
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING
    )
    assert "claim_boundary" in packet.missing_evidence
    assert "BLOCKED_MISSING_CLAIM_BOUNDARY" in packet.blockers


def test_missing_null_control_blocked() -> None:
    refs = tuple(
        r for r in _full_evidence() if r.evidence_category != "null_control_false_positive"
    )
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE
    )
    assert "null_control_false_positive" in packet.missing_evidence
    assert "BLOCKED_MISSING_NULL_CONTROL_EVIDENCE" in packet.blockers


def test_missing_positive_control_blocked() -> None:
    refs = tuple(
        r for r in _full_evidence() if r.evidence_category != "positive_control_recovery"
    )
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE
    )
    assert "positive_control_recovery" in packet.missing_evidence
    assert "BLOCKED_MISSING_POSITIVE_CONTROL_EVIDENCE" in packet.blockers


def test_instrument_identity_mismatch_blocked() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(instrument_identity="geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.production")
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    )
    assert "INSTRUMENT_IDENTITY_MISMATCH" in packet.blockers


def test_cross_inference_family_blocked() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(requested_inference_family="bootstrap")
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CROSS_INFERENCE_FAMILY
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    )
    assert "CROSS_INFERENCE_FAMILY_NOT_ALLOWED" in packet.blockers


def test_cross_geometry_blocked() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(requested_geometry="aggregate_pooled")
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CROSS_GEOMETRY
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    )
    assert "CROSS_GEOMETRY_NOT_ALLOWED" in packet.blockers


def test_production_surface_blocked() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(requested_surface="production")
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE
    )
    assert (
        packet.promotion_review_eligibility_status
        == TBRRidgePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW
    )
    assert "UNSUPPORTED_SURFACE_REQUESTED" in packet.blockers


def test_duplicate_evidence_references_preserved() -> None:
    dup = _ref("sensitivity", "dup")
    refs = _full_evidence() + (dup,)
    packet = assemble_tbrridge_promotion_evidence_packet(_base_input(evidence_references=refs))
    assert len(packet.evidence_by_category["sensitivity"]) == 2


def test_empty_artifact_ref_treated_as_missing() -> None:
    refs = list(_full_evidence())
    refs[2] = TBRRidgeEvidenceReference(
        evidence_category="metric_estimand_alignment",
        artifact_id="METRIC_ESTIMAND",
        artifact_ref="",
    )
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(evidence_references=tuple(refs))
    )
    assert "metric_estimand_alignment" in packet.missing_evidence
    assert "BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT" in packet.blockers


def test_lane_b_evidence_cannot_substitute_method_validity() -> None:
    lane_b_refs = (
        TBRRidgeEvidenceReference(
            evidence_category="post_test_spend",
            artifact_id="GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001",
            artifact_ref="panel_exp/validation/post_test_spend_readiness_adapter_runtime_001.py",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="spend_readiness",
            artifact_id="GEOX_TRUSTED_READOUT_SPEND_READINESS_INTEGRATION_RUNTIME_001",
            artifact_ref="panel_exp/validation/trusted_readout_spend_readiness_integration_runtime_001.py",
        ),
        TBRRidgeEvidenceReference(
            evidence_category="roi_readiness",
            artifact_id="GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001",
            artifact_ref="docs/track_d/GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001.md",
        ),
    )
    packet = assemble_tbrridge_promotion_evidence_packet(
        _base_input(evidence_references=lane_b_refs)
    )
    assert (
        packet.packet_readiness_status
        == TBRRidgePacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
    )
    assert len(packet.missing_evidence) >= 1
    assert any("LANE_B_EVIDENCE_NOT_METHOD_VALIDITY" in b for b in packet.blockers)


def test_lineage_and_warnings_preserved() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(_base_input())
    assert packet.lineage == {"source": "unit_test"}
    assert "input_warning" in packet.warnings


def test_no_promotion_or_authorization_flags_in_output() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(_base_input())
    payload = packet.to_dict()
    forbidden = (
        "method_promoted",
        "instrument_promoted",
        "catalog_unblocked",
        "production_compatibility_authorized",
        "claim_authorization_changed",
        "statistical_claim_authorized",
    )
    for key in forbidden:
        assert key not in payload or payload[key] is not True


def test_prohibited_surfaces_present_on_packet() -> None:
    packet = assemble_tbrridge_promotion_evidence_packet(_base_input())
    assert "CONFIDENCE_INTERVAL_CLAIM" in packet.prohibited_surfaces
    assert "METHOD_PROMOTION_NOTICE" in packet.prohibited_surfaces
    assert "DIAGNOSTIC_STATUS_SUMMARY" in packet.allowed_surfaces


def test_run_validation_produces_ready_sample() -> None:
    summary = run_validation(write_summary=False)
    assert summary["evidence_packet_runtime_implemented"] is True
    assert summary["method_promoted"] is False
    assert summary["recommended_next_artifact"] == "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001"
