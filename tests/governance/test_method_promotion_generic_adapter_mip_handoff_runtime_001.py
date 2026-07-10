"""Governance tests for METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001_summary.json"
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
_VERDICT = (
    "package_side_mip_handoff_runtime_implemented_no_mip_runtime_no_decision_authorization"
)
_NEXT = "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
_LANE_A_NEXT = "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "generic_runtime_changed",
    "new_profile_registered",
    "mip_runtime_implemented",
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
)

_REQUIRED_TRUE_FLAGS = (
    "handoff_runtime_implemented",
    "handoff_builder_implemented",
    "handoff_serializer_implemented",
    "handoff_object_implemented",
    "fixed_mip_non_authorization_statuses_enforced",
    "mip_allowed_uses_enforced",
    "mip_prohibited_uses_enforced",
    "generic_approve_review_continuation_preserved_as_weak_context",
    "source_of_truth_boundary_preserved",
    "raw_evidence_not_inspected",
    "packet_readiness_not_recomputed",
    "decision_status_not_recomputed",
    "missing_evidence_not_repaired",
    "decision_surface_authorization_blocked",
    "trust_report_bypass_blocked",
    "recommendation_authorization_blocked",
    "catalog_authorization_blocked",
    "production_readout_authorization_blocked",
    "production_compatibility_authorization_blocked",
    "claim_authorization_blocked",
    "spend_roi_authorization_blocked",
    "causal_lift_authorization_blocked",
    "statistical_claim_authorization_blocked",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001" in text
    assert _VERDICT in text
    assert "MethodPromotionGenericAdapterMIPHandoff" in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_generic_adapter_mip_handoff_runtime"
    assert data["scope"] == "package_side_handoff_runtime_no_mip_runtime_no_decision_authorization"


def test_runtime_builder_serializer_implemented() -> None:
    data = _load_summary()
    assert data["handoff_runtime_implemented"] is True
    assert data["handoff_builder_implemented"] is True
    assert data["handoff_serializer_implemented"] is True
    assert data["handoff_object_implemented"] is True


def test_fixed_statuses_and_uses_enforced() -> None:
    data = _load_summary()
    assert data["fixed_mip_non_authorization_statuses_enforced"] is True
    assert data["mip_allowed_uses_enforced"] is True
    assert data["mip_prohibited_uses_enforced"] is True
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF" in text
    assert "NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF" in text
    assert "NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF" in text
    assert "governance_context" in text
    assert "decision_surface_approval" in text


def test_source_of_truth_and_non_recompute() -> None:
    data = _load_summary()
    assert data["source_of_truth_boundary_preserved"] is True
    assert data["raw_evidence_not_inspected"] is True
    assert data["packet_readiness_not_recomputed"] is True
    assert data["decision_status_not_recomputed"] is True
    assert data["missing_evidence_not_repaired"] is True


def test_supported_profiles() -> None:
    data = _load_summary()
    assert data["supported_profile_count"] == 3
    for profile_id in _PROFILES:
        assert profile_id in data["supported_profiles"]
        assert profile_id in _RUNTIME_DOC.read_text(encoding="utf-8")


def test_required_true_flags() -> None:
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
    assert _NEXT in _RUNTIME_DOC.read_text(encoding="utf-8")


def test_final_verdict() -> None:
    assert _load_summary()["final_verdict"] == _VERDICT


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    assert (
        "METHOD-PROMOTION-GENERIC-ADAPTER-MIP-HANDOFF-RUNTIME-001"
        in _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    )


def test_method_soundness_references_artifact() -> None:
    assert (
        "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001"
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
