"""Governance tests for METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_VERDICT = "generic_runtime_contract_defined_no_runtime_no_promotion"
_NEXT = "METHOD_PROMOTION_GENERIC_RUNTIME_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "generic_runtime_implemented",
    "generic_dataclasses_implemented",
    "adapter_profile_implemented",
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
    "generic_runtime_contract_defined",
    "runtime_design_principle_defined",
    "future_runtime_entry_points_defined",
    "packet_summary_contract_defined",
    "decision_summary_contract_defined",
    "governance_summary_contract_defined",
    "adapter_profile_contract_defined",
    "adapter_blockers_defined",
    "generic_status_mapping_requirements_defined",
    "boundary_preservation_requirements_defined",
    "source_of_truth_rules_defined",
    "mip_facing_summary_boundary_defined",
    "future_runtime_validation_requirements_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_generic_runtime_contract"


def test_generic_runtime_contract_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "adapter/summarizer only" in text.lower() or "adapter" in text.lower()
    assert _load_summary()["generic_runtime_contract_defined"] is True


def test_runtime_design_principle_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "source of truth" in text.lower()
    assert _load_summary()["runtime_design_principle_defined"] is True


def test_future_runtime_entry_points_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "adapt_method_promotion_packet_to_generic_summary" in text
    assert "adapt_method_promotion_decision_to_generic_summary" in text
    assert "build_method_promotion_governance_summary" in text
    assert _load_summary()["future_runtime_entry_points_defined"] is True


def test_packet_summary_contract_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MethodPromotionEvidencePacketSummary" in text
    assert "generic_packet_readiness_status" in text
    assert _load_summary()["packet_summary_contract_defined"] is True


def test_decision_summary_contract_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MethodPromotionReviewDecisionSummary" in text
    assert "generic_decision_status" in text
    assert _load_summary()["decision_summary_contract_defined"] is True


def test_governance_summary_contract_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MethodPromotionGovernanceSummary" in text
    assert _load_summary()["governance_summary_contract_defined"] is True


def test_adapter_profile_contract_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MethodPromotionInstrumentAdapterProfile" in text
    assert "packet_status_mapping" in text
    assert _load_summary()["adapter_profile_contract_defined"] is True


def test_adapter_blockers_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "GENERIC_ADAPTER_BLOCKED_MISSING_SOURCE_PACKET" in text
    assert "GENERIC_ADAPTER_BLOCKED_UNMAPPED_DECISION_STATUS" in text
    assert _load_summary()["adapter_blockers_defined"] is True


def test_generic_status_mapping_requirements_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT" in text
    assert "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT" in text
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION" in text
    assert _load_summary()["generic_status_mapping_requirements_defined"] is True


def test_boundary_preservation_requirements_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "boundary_status_incomplete" in text
    assert "GENERIC_ADAPTER_BLOCKED_MISSING_BOUNDARY_STATUS" in text
    assert _load_summary()["boundary_preservation_requirements_defined"] is True


def test_source_of_truth_rules_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "authoritative" in text.lower()
    assert "cannot convert" in text.lower()
    assert _load_summary()["source_of_truth_rules_defined"] is True


def test_mip_facing_summary_boundary_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "MIP DecisionSurface" in text
    assert "TrustReport" in text
    assert _load_summary()["mip_facing_summary_boundary_defined"] is True


def test_future_runtime_validation_requirements_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_001" in text
    assert "TBRRidge packet adaptation" in text
    assert _load_summary()["future_runtime_validation_requirements_defined"] is True


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
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-GENERIC-RUNTIME-CONTRACT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
