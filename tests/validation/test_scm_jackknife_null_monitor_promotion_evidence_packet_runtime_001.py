"""Tests for SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001."""

from __future__ import annotations

import pytest

from panel_exp.validation.scm_jackknife_null_monitor_promotion_evidence_packet_runtime_001 import (
    CANONICAL_INSTRUMENT_IDENTITY,
    CATALOG_ALIAS,
    SCMJackknifeNullMonitorEvidenceReference,
    SCMJackknifeNullMonitorPacketReadinessStatus,
    SCMJackknifeNullMonitorPromotionEvidencePacketInput,
    SCMJackknifeNullMonitorPromotionReviewEligibilityStatus,
    assemble_scm_jackknife_null_monitor_promotion_evidence_packet,
    run_validation,
)

_REQUIRED = (
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

_BLOCKER_BY_CATEGORY = {
    "instrument_identity": "BLOCKED_MISSING_INSTRUMENT_IDENTITY",
    "claim_boundary": "BLOCKED_MISSING_CLAIM_BOUNDARY",
    "metric_estimand_alignment": "BLOCKED_MISSING_METRIC_ESTIMAND_ALIGNMENT",
    "null_control_false_positive": "BLOCKED_MISSING_NULL_CONTROL_EVIDENCE",
    "jackknife_stability": "BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE",
    "directional_error": "BLOCKED_MISSING_DIRECTIONAL_ERROR_EVIDENCE",
    "donor_pool_diagnostics": "BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS",
    "pre_period_fit_diagnostics": "BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS",
    "sensitivity": "BLOCKED_MISSING_SENSITIVITY_EVIDENCE",
    "readout_compatibility": "BLOCKED_MISSING_READOUT_COMPATIBILITY",
}


def _ref(category: str, suffix: str = "001", **kwargs: object) -> SCMJackknifeNullMonitorEvidenceReference:
    return SCMJackknifeNullMonitorEvidenceReference(
        evidence_id=f"{category}_{suffix}",
        evidence_category=category,
        artifact_ref=f"docs/track_d/{category.upper()}_{suffix}.md",
        **kwargs,
    )


def _full_evidence() -> list[SCMJackknifeNullMonitorEvidenceReference]:
    return [_ref(cat) for cat in _REQUIRED]


def _base_input(**overrides: object) -> SCMJackknifeNullMonitorPromotionEvidencePacketInput:
    payload = {
        "packet_id": "test_packet",
        "instrument_identity": CANONICAL_INSTRUMENT_IDENTITY,
        "evidence_refs": _full_evidence(),
        "lineage": {"source": "unit_test"},
        "warnings": ["input_warning"],
    }
    payload.update(overrides)
    return SCMJackknifeNullMonitorPromotionEvidencePacketInput(**payload)


def test_all_required_evidence_ready_and_eligible() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(_base_input())
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT
    )
    assert packet.instrument_identity == CANONICAL_INSTRUMENT_IDENTITY
    assert packet.estimator_family == "scm"
    assert packet.inference_family == "jackknife"
    assert packet.geometry == "single_cell"
    assert packet.estimand == "delta_mu"
    assert packet.surface == "null_monitor"
    assert packet.interval_semantics == "not_applicable_for_null_monitor"
    assert packet.missing_evidence == ()
    assert packet.blockers == ()


def test_output_identity_canonical_when_alias_present() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(catalog_alias=CATALOG_ALIAS)
    )
    assert packet.instrument_identity == CANONICAL_INSTRUMENT_IDENTITY
    assert packet.catalog_alias == CATALOG_ALIAS


def test_alias_only_ref_preserves_canonical_output_identity() -> None:
    refs = _full_evidence()
    refs[0] = _ref(
        "instrument_identity",
        catalog_alias=CATALOG_ALIAS,
        instrument_identity=None,
    )
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs, catalog_alias=CATALOG_ALIAS)
    )
    assert packet.instrument_identity == CANONICAL_INSTRUMENT_IDENTITY
    assert packet.catalog_alias == CATALOG_ALIAS


def test_missing_claim_boundary_blocked() -> None:
    refs = [r for r in _full_evidence() if r.evidence_category != "claim_boundary"]
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING
    )
    assert "claim_boundary" in packet.missing_evidence
    assert "BLOCKED_MISSING_CLAIM_BOUNDARY" in packet.blockers


@pytest.mark.parametrize("missing_category", _REQUIRED)
def test_missing_each_required_category(missing_category: str) -> None:
    refs = [r for r in _full_evidence() if r.evidence_category != missing_category]
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert missing_category in packet.missing_evidence
    assert _BLOCKER_BY_CATEGORY[missing_category] in packet.blockers
    if missing_category == "claim_boundary":
        assert (
            packet.packet_readiness_status
            == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING
        )
    else:
        assert packet.packet_readiness_status in {
            SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE,
            SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY,
        }


def test_partial_diagnostic_only_when_some_evidence_present() -> None:
    refs = _full_evidence()[:3]
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_PARTIAL_DIAGNOSTIC_ONLY
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE
    )


def test_input_identity_mismatch_blocked() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(instrument_identity="geo.scm.placebo.single_cell.delta_mu.null_monitor")
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_IDENTITY_MISMATCH
    )
    assert "BLOCKED_INSTRUMENT_IDENTITY_MISMATCH" in packet.blockers


def test_evidence_ref_identity_mismatch_blocked() -> None:
    refs = _full_evidence()
    refs[0] = _ref("instrument_identity", instrument_identity="geo.did.bootstrap.single_cell.delta_mu.null_monitor")
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_INSTRUMENT_IDENTITY_MISMATCH
    )
    assert "BLOCKED_INSTRUMENT_IDENTITY_MISMATCH" in packet.blockers


def test_production_surface_blocked() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(requested_surface="production")
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_PRODUCTION_REVIEW
    )
    assert "BLOCKED_PRODUCTION_COMPATIBILITY_REQUIRED" in packet.blockers


def test_catalog_unblock_surface_blocked() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(requested_surface="catalog_unblock")
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_UNSUPPORTED_SURFACE
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK
    )
    assert "BLOCKED_CATALOG_UNBLOCK_REQUESTED" in packet.blockers


@pytest.mark.parametrize(
    "surface",
    ["causal_lift", "business_lift", "p_value", "significance", "roi", "decision_recommendation"],
)
def test_causal_claim_surface_blocked(surface: str) -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(requested_surface=surface)
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION
    )
    assert (
        packet.promotion_review_eligibility_status
        == SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_FOR_CAUSAL_CLAIM_REVIEW
    )
    assert "BLOCKED_CAUSAL_CLAIM_REQUESTED" in packet.blockers


def test_empty_artifact_ref_does_not_count() -> None:
    refs = _full_evidence()
    refs[4] = SCMJackknifeNullMonitorEvidenceReference(
        evidence_id="jackknife_stability_empty",
        evidence_category="jackknife_stability",
        artifact_ref="",
    )
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert "jackknife_stability" in packet.missing_evidence
    assert "BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE" in packet.blockers


def test_duplicate_refs_preserved() -> None:
    dup = _ref("sensitivity", "dup")
    refs = _full_evidence() + [dup]
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert len(packet.evidence_by_category["sensitivity"]) == 2


def test_lineage_and_warnings_preserved() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(_base_input())
    assert packet.lineage == {"source": "unit_test"}
    assert "input_warning" in packet.warnings


def test_tbrridge_metadata_cannot_satisfy_scm_categories() -> None:
    refs = [
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="tbr_null",
            evidence_category="null_control_false_positive",
            artifact_ref="docs/track_d/TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001.md",
            metadata={"source_family": "tbrridge"},
        )
    ]
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert "null_control_false_positive" in packet.missing_evidence
    assert any("TBRIDGE_EVIDENCE_CANNOT_SATISFY_SCM" in b for b in packet.blockers)


def test_lane_b_metadata_cannot_satisfy_method_validity() -> None:
    refs = [
        SCMJackknifeNullMonitorEvidenceReference(
            evidence_id="lane_b_metric",
            evidence_category="metric_estimand_alignment",
            artifact_ref="docs/track_d/GEOX_EFFICIENCY_METRIC_READINESS_MAPPER_CONTRACT_001.md",
            metadata={"source_lane": "lane_b"},
        )
    ]
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        _base_input(evidence_refs=refs)
    )
    assert "metric_estimand_alignment" in packet.missing_evidence
    assert any("LANE_B_EVIDENCE_NOT_METHOD_VALIDITY" in b for b in packet.blockers)


def test_no_raw_evidence_quality_scoring_field() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(_base_input())
    payload = packet.to_dict()
    forbidden = (
        "evidence_quality_score",
        "raw_evidence_quality_scored",
        "quality_score",
        "evidence_score",
    )
    for key in forbidden:
        assert key not in payload


def test_not_requested_when_empty_refs_and_no_surface() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(
            packet_id="empty",
            evidence_refs=[],
            requested_surface=None,
        )
    )
    assert (
        packet.packet_readiness_status
        == SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_NOT_REQUESTED
    )


def test_empty_refs_with_default_surface_missing_evidence() -> None:
    packet = assemble_scm_jackknife_null_monitor_promotion_evidence_packet(
        SCMJackknifeNullMonitorPromotionEvidencePacketInput(
            packet_id="empty_default_surface",
            evidence_refs=[],
            requested_surface="null_monitor",
        )
    )
    assert packet.packet_readiness_status in {
        SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_MISSING_REQUIRED_EVIDENCE,
        SCMJackknifeNullMonitorPacketReadinessStatus.PACKET_BLOCKED_CLAIM_BOUNDARY_MISSING,
    }
    assert packet.promotion_review_eligibility_status in {
        SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_MISSING_EVIDENCE,
        SCMJackknifeNullMonitorPromotionReviewEligibilityStatus.NOT_ELIGIBLE_CLAIM_BOUNDARY_MISSING,
    }


def test_run_validation_produces_ready_sample() -> None:
    summary = run_validation(write_summary=False)
    assert summary["evidence_packet_runtime_implemented"] is True
    assert summary["runtime_implemented"] is True
    assert summary["scm_promoted"] is False
    assert summary["recommended_next_artifact"] == "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001"
