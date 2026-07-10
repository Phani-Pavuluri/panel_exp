"""Tests for AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001."""

from __future__ import annotations

import pytest

from panel_exp.validation.augsynth_jackknife_promotion_evidence_packet_runtime_001 import (
    ALIAS_RELATED_RESEARCH_IDENTITY,
    CANONICAL_INSTRUMENT_IDENTITY,
    AugSynthJackknifeEvidenceReference,
    AugSynthJackknifePacketReadinessStatus,
    AugSynthJackknifePromotionEvidencePacketInput,
    AugSynthJackknifePromotionReviewEligibilityStatus,
    assemble_augsynth_jackknife_promotion_evidence_packet,
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

_ALWAYS_WARNINGS = (
    "AUGSYNTH_WARNING_DIAGNOSTIC_INTERVAL_NOT_PRODUCTION_CI",
    "AUGSYNTH_WARNING_RESTRICTED_REVIEW_NOT_PROMOTION",
    "AUGSYNTH_WARNING_GENERIC_ADAPTER_PROFILE_NOT_AVAILABLE_YET",
)


def _ref(category: str, suffix: str = "001", **kwargs: object) -> AugSynthJackknifeEvidenceReference:
    return AugSynthJackknifeEvidenceReference(
        evidence_id=f"{category}_{suffix}",
        evidence_category=category,
        artifact_ref=f"docs/track_d/{category.upper()}_{suffix}.md",
        **kwargs,
    )


def _full_evidence() -> list[AugSynthJackknifeEvidenceReference]:
    return [_ref(cat) for cat in _REQUIRED]


def _base_input(**overrides: object) -> AugSynthJackknifePromotionEvidencePacketInput:
    payload = {
        "packet_id": "test_packet",
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "evidence_references": _full_evidence(),
        "lineage": {"source": "unit_test"},
        "warnings": ["input_warning"],
    }
    payload.update(overrides)
    return AugSynthJackknifePromotionEvidencePacketInput(**payload)


def test_all_required_evidence_ready_and_eligible() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(_base_input())
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT
    )
    assert packet.instrument_identity == CANONICAL_INSTRUMENT_IDENTITY
    assert packet.alias_related_identity == ALIAS_RELATED_RESEARCH_IDENTITY
    assert packet.missing_evidence == ()
    assert len(packet.evidence_by_category) == len(_REQUIRED)


def test_missing_claim_boundary_blocked() -> None:
    refs = [r for r in _full_evidence() if r.evidence_category != "claim_boundary"]
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING
    )
    assert "claim_boundary" in packet.missing_evidence


def test_missing_other_required_evidence_partial_or_blocked() -> None:
    refs = [r for r in _full_evidence() if r.evidence_category != "sensitivity"]
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert "sensitivity" in packet.missing_evidence
    assert packet.packet_readiness_status in {
        AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE,
        AugSynthJackknifePacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY,
    }


def test_partial_diagnostic_when_some_refs_present() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=_full_evidence()[:4])
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY
    )


def test_no_refs_and_no_surface_not_requested() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        AugSynthJackknifePromotionEvidencePacketInput(
            packet_id="empty",
            instrument_identity=CANONICAL_INSTRUMENT_IDENTITY,
            requested_surface="",
            evidence_references=[],
        )
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_NOT_REQUESTED
    )


def test_non_canonical_identity_mismatch() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(instrument_identity="geo.unknown.method")
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    )


def test_research_only_identity_substitution() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(instrument_identity=ALIAS_RELATED_RESEARCH_IDENTITY)
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_RESEARCH_ONLY_SUBSTITUTION
    )


def test_research_only_surface_substitution() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(requested_surface="research_only_as_promotion_substitute")
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_RESEARCH_ONLY_SUBSTITUTION_ATTEMPT
    )


def test_production_surface_blocked() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(requested_surface="production")
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW
    )


def test_catalog_surface_blocked() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(requested_surface="catalog_unblock")
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK
    )


@pytest.mark.parametrize("surface", ("claim_authorization", "mip_decision_surface", "business_recommendation"))
def test_claim_mip_business_surface_blocked(surface: str) -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(requested_surface=surface)
    )
    assert (
        packet.packet_readiness_status
        == AugSynthJackknifePacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE
    )
    assert (
        packet.promotion_review_eligibility_status
        == AugSynthJackknifePromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CLAIM_REVIEW
    )


def test_empty_artifact_ref_does_not_satisfy_category() -> None:
    refs = _full_evidence()
    for i, ref in enumerate(refs):
        if ref.evidence_category == "jackknife_stability":
            refs[i] = AugSynthJackknifeEvidenceReference(
                evidence_id="jackknife_stability_001",
                evidence_category="jackknife_stability",
                artifact_ref="",
            )
            break
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert "jackknife_stability" in packet.missing_evidence


def test_scm_source_family_substitution_blocked() -> None:
    refs = _full_evidence()
    refs[0] = _ref("instrument_identity", source_family="scm")
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert "AUGSYNTH_PACKET_BLOCKED_SCM_EVIDENCE_SUBSTITUTION" in packet.blockers
    assert "AUGSYNTH_WARNING_SCM_BRIDGE_NOT_SUBSTITUTION" in packet.warnings


def test_tbrridge_source_family_substitution_blocked() -> None:
    refs = _full_evidence()
    refs[0] = _ref("instrument_identity", source_family="tbrridge")
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert "AUGSYNTH_PACKET_BLOCKED_TBRRIDGE_EVIDENCE_SUBSTITUTION" in packet.blockers


@pytest.mark.parametrize("family", ("lane_b", "spend", "roi"))
def test_lane_b_source_family_substitution_blocked(family: str) -> None:
    refs = _full_evidence()
    refs[0] = _ref("instrument_identity", source_family=family)
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    assert "AUGSYNTH_PACKET_BLOCKED_LANE_B_EVIDENCE_SUBSTITUTION" in packet.blockers


def test_always_warnings_present() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(_base_input())
    for warning in _ALWAYS_WARNINGS:
        assert warning in packet.warnings


def test_fixed_non_authorization_boundary_statuses() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(_base_input())
    assert packet.boundary_statuses["claim_authorization_status"] == "NOT_AUTHORIZED_BY_THIS_PACKET"
    assert packet.boundary_statuses["catalog_status"] == "NOT_UNBLOCKED_BY_THIS_PACKET"
    assert packet.boundary_statuses["method_promotion_status"] == "NOT_PROMOTED_BY_THIS_PACKET"
    assert packet.boundary_statuses["generic_adapter_status"] == "NOT_REGISTERED_BY_THIS_PACKET"
    assert packet.boundary_statuses["trust_report_bypass_status"] == "NOT_BYPASSED_BY_THIS_PACKET"


def test_evidence_by_category_groups_valid_refs() -> None:
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(_base_input())
    for cat in _REQUIRED:
        assert cat in packet.evidence_by_category
        assert packet.evidence_by_category[cat][0]["artifact_ref"]


def test_no_raw_evidence_quality_scoring_in_output() -> None:
    refs = _full_evidence()
    refs[0] = _ref(
        "instrument_identity",
        metadata={"quality_score": 0.99},
    )
    packet = assemble_augsynth_jackknife_promotion_evidence_packet(
        _base_input(evidence_references=refs)
    )
    payload = packet.to_dict()
    assert "quality_score" not in str(payload.get("packet_readiness_status", ""))
    assert packet.packet_readiness_status == AugSynthJackknifePacketReadinessStatus.PACKET_READY_FOR_PROMOTION_REVIEW_INPUT


def test_run_validation_passes() -> None:
    summary = run_validation(write_summary=False)
    assert summary["runtime_implemented"] is True
    assert summary["augsynth_runtime_implemented"] is True
