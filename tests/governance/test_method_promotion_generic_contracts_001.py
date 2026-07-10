"""Governance tests for METHOD_PROMOTION_GENERIC_CONTRACTS_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACTS = _REPO / "docs/track_d/METHOD_PROMOTION_GENERIC_CONTRACTS_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_CONTRACTS_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_VERDICT = "generic_method_promotion_contracts_defined_no_runtime_no_promotion"
_NEXT = "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001"
_LANE_A_NEXT = "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "generic_runtime_implemented",
    "generic_dataclasses_implemented",
    "method_promoted",
    "instrument_promoted",
    "tbrridge_promoted",
    "scm_promoted",
    "augsynth_promoted",
    "did_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "statistical_claim_authorized",
    "confidence_interval_claim_authorized",
    "p_value_claim_authorized",
    "significance_claim_authorized",
    "statistical_power_claim_authorized",
    "causal_lift_claim_authorized",
    "business_lift_claim_authorized",
    "roi_roas_claim_authorized",
    "decision_recommendation_authorized",
    "production_readout_authorized",
    "estimator_implemented",
    "inference_implemented",
    "new_validation_experiments_run",
    "raw_evidence_quality_scored",
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
)

_REQUIRED_TRUE_FLAGS = (
    "generic_contracts_defined",
    "instrument_identity_contract_defined",
    "evidence_reference_contract_defined",
    "evidence_packet_contract_defined",
    "packet_readiness_status_family_defined",
    "review_eligibility_status_family_defined",
    "review_decision_contract_defined",
    "review_decision_status_family_defined",
    "boundary_status_contract_defined",
    "allowed_action_contract_defined",
    "prohibited_action_contract_defined",
    "generic_precedence_rules_defined",
    "evidence_quality_boundary_defined",
    "completed_applications_mapped_to_generic_contracts",
    "future_artifact_compatibility_requirements_defined",
    "claim_catalog_production_lane_b_mip_boundaries_preserved",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contracts_doc_exists() -> None:
    assert _CONTRACTS.exists()
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_CONTRACTS_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_GENERIC_CONTRACTS_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_generic_contracts"


def test_generic_contracts_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "MethodPromotionInstrumentIdentity" in text
    assert "MethodPromotionEvidencePacket" in text
    assert "MethodPromotionReviewDecision" in text
    assert _load_summary()["generic_contracts_defined"] is True


def test_instrument_identity_contract_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "canonical_identity_string" in text
    assert _load_summary()["instrument_identity_contract_defined"] is True


def test_evidence_reference_contract_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "MethodPromotionEvidenceReference" in text
    assert "artifact_ref" in text
    assert _load_summary()["evidence_reference_contract_defined"] is True


def test_evidence_packet_contract_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "evidence_by_category" in text
    assert _load_summary()["evidence_packet_contract_defined"] is True


def test_packet_readiness_status_family_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_REVIEW_INPUT" in text
    assert _load_summary()["packet_readiness_status_family_defined"] is True


def test_review_eligibility_status_family_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "ELIGIBLE_AS_REVIEW_INPUT" in text
    assert _load_summary()["review_eligibility_status_family_defined"] is True


def test_review_decision_contract_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "MethodPromotionReviewDecision" in text
    assert _load_summary()["review_decision_contract_defined"] is True


def test_review_decision_status_family_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "APPROVE_REVIEW_CONTINUATION" in text
    assert _load_summary()["review_decision_status_family_defined"] is True


def test_boundary_status_contract_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "MethodPromotionBoundaryStatus" in text
    assert "NOT_AUTHORIZED_BY_THIS_DECISION" in text
    assert _load_summary()["boundary_status_contract_defined"] is True


def test_allowed_prohibited_action_contracts_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "MethodPromotionAllowedAction" in text
    assert "MethodPromotionProhibitedAction" in text
    assert "claim_authorization_runtime_bypass" in text
    assert _load_summary()["allowed_action_contract_defined"] is True
    assert _load_summary()["prohibited_action_contract_defined"] is True


def test_generic_precedence_rules_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "Generic precedence rules" in text
    assert _load_summary()["generic_precedence_rules_defined"] is True


def test_evidence_quality_boundary_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "evidence quality boundary" in text.lower()
    assert "must not" in text.lower()
    assert _load_summary()["evidence_quality_boundary_defined"] is True


def test_completed_applications_mapped() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "TBRRidgePromotionEvidencePacket" in text
    assert "SCMJackknifeNullMonitorPromotionEvidencePacket" in text
    assert _load_summary()["completed_applications_mapped_to_generic_contracts"] is True


def test_future_artifact_compatibility_requirements_defined() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "Required compatibility for future instrument-specific artifacts" in text
    assert _load_summary()["future_artifact_compatibility_requirements_defined"] is True


def test_claim_catalog_production_lane_b_mip_boundaries_preserved() -> None:
    text = _CONTRACTS.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert "Lane B" in text
    assert "MIP" in text
    assert _load_summary()["claim_catalog_production_lane_b_mip_boundaries_preserved"] is True


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_CONTRACTS_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-GENERIC-CONTRACTS-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_CONTRACTS_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
