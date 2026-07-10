"""Governance tests for METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CHECKPOINT = (
    _REPO
    / "docs/track_d/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001.md"
)
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_PROFILES = (
    "tbrridge_restricted_review_v1",
    "scm_jackknife_null_monitor_v1",
    "augsynth_jackknife_restricted_review_v1",
)
_DECISION = "PROCEED_TO_MIP_INTEGRATION_PLANNING_CONTRACT_NOT_RUNTIME_INTEGRATION"
_VERDICT = (
    "package_side_handoff_runtime_stable_for_mip_integration_planning_not_runtime_integration"
)
_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"
_NEXT_REPO = "/Users/phani/Desktop/marketing_intelligence_platform"
_LANE_A_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_behavior_changed",
    "package_runtime_behavior_changed",
    "generic_runtime_changed",
    "new_profile_registered",
    "mip_runtime_implemented",
    "mip_integration_implemented",
    "decision_surface_authorized",
    "trust_report_bypassed",
    "recommendation_contract_authorized",
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
    "ready_for_mip_runtime_integration",
    "ready_for_decision_surface_construction",
    "ready_for_trust_report_bypass",
    "ready_for_recommendation_contract_generation",
    "ready_for_catalog_claim_production_authorization",
    "ready_for_budget_spend_roi_recommendation",
)

_REQUIRED_TRUE_FLAGS = (
    "runtime_application_checkpoint_completed",
    "handoff_object_reviewed",
    "handoff_builder_reviewed",
    "handoff_serializer_reviewed",
    "contract_conformance_assessed",
    "boundary_preservation_assessed",
    "generic_decision_semantics_assessed",
    "supported_profile_application_assessed",
    "blocked_handoff_behavior_assessed",
    "mip_integration_planning_readiness_assessed",
    "required_mip_side_prerequisites_defined",
    "source_of_truth_boundary_preserved",
    "generic_approve_review_continuation_preserved_as_weak_context",
    "ready_for_mip_integration_planning",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_checkpoint_doc_exists() -> None:
    assert _CHECKPOINT.exists()
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001" in text
    assert _DECISION in text
    assert _VERDICT in text
    assert "MethodPromotionGenericAdapterMIPHandoff" in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert (
        data["artifact_id"]
        == "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
    )
    assert data["status"] == "completed"
    assert (
        data["artifact_type"]
        == "method_promotion_generic_adapter_mip_handoff_runtime_application_checkpoint"
    )
    assert (
        data["scope"]
        == "runtime_application_checkpoint_docs_tests_only_no_mip_integration_no_runtime_behavior_change"
    )


def test_runtime_checkpoint_completed_and_behavior_unchanged() -> None:
    data = _load_summary()
    assert data["runtime_application_checkpoint_completed"] is True
    assert data["runtime_behavior_changed"] is False
    assert data["package_runtime_behavior_changed"] is False


def test_handoff_surfaces_reviewed() -> None:
    data = _load_summary()
    assert data["handoff_object_reviewed"] is True
    assert data["handoff_builder_reviewed"] is True
    assert data["handoff_serializer_reviewed"] is True


def test_assessments_completed() -> None:
    data = _load_summary()
    assert data["contract_conformance_assessed"] is True
    assert data["boundary_preservation_assessed"] is True
    assert data["generic_decision_semantics_assessed"] is True
    assert data["supported_profile_application_assessed"] is True
    assert data["blocked_handoff_behavior_assessed"] is True
    assert data["mip_integration_planning_readiness_assessed"] is True
    assert data["required_mip_side_prerequisites_defined"] is True


def test_mip_planning_readiness() -> None:
    data = _load_summary()
    assert data["ready_for_mip_integration_planning"] is True
    assert data["ready_for_mip_runtime_integration"] is False
    assert data["ready_for_decision_surface_construction"] is False
    assert data["ready_for_trust_report_bypass"] is False
    assert data["ready_for_recommendation_contract_generation"] is False
    assert data["ready_for_catalog_claim_production_authorization"] is False
    assert data["ready_for_budget_spend_roi_recommendation"] is False


def test_supported_profiles() -> None:
    data = _load_summary()
    assert data["supported_profile_count"] == 3
    for profile_id in _PROFILES:
        assert profile_id in data["supported_profiles"]
        assert profile_id in _CHECKPOINT.read_text(encoding="utf-8")


def test_decision_and_verdict() -> None:
    data = _load_summary()
    assert data["decision"] == _DECISION
    assert data["final_verdict"] == _VERDICT


def test_required_true_flags() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_recommended_next_artifact_and_repo() -> None:
    data = _load_summary()
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert data["recommended_next_artifact"] == _NEXT
    assert data["recommended_next_repo"] == _NEXT_REPO
    assert _NEXT in text
    assert _NEXT_REPO in text


def test_roadmap_references_artifact() -> None:
    assert (
        "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
        in _ROADMAP.read_text(encoding="utf-8")
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert (
        "METHOD-PROMOTION-GENERIC-ADAPTER-MIP-HANDOFF-RUNTIME-APPLICATION-CHECKPOINT-001"
        in _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    )


def test_method_soundness_references_artifact() -> None:
    assert (
        "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
        in _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    )


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
