"""Governance tests for METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CHECKPOINT = (
    _REPO
    / "docs/track_d/METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001.md"
)
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001_summary.json"
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
_FRAMEWORK_HEALTH = "STABLE_FOR_CURRENT_THREE_PROFILES_WITH_BOUNDARY_GUARDS"
_DECISION = "PAUSE_NEW_PROFILE_REGISTRATION_AND_ASSESS_NEXT_LANE"
_VERDICT = "pause_new_profile_registration_and_assess_next_lane"
_NEXT = "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_READINESS_AUDIT_001"
_LANE_A_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "generic_runtime_changed",
    "new_profile_registered",
    "packet_runtime_changed",
    "decision_runtime_changed",
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
    "checkpoint_completed",
    "supported_profile_inventory_completed",
    "cross_profile_consistency_assessed",
    "profile_specific_findings_completed",
    "framework_health_assessed",
    "source_of_truth_boundary_preserved",
    "generic_adapter_summarizer_only_preserved",
    "boundary_statuses_preserved",
    "prohibited_actions_preserved",
    "positive_decision_semantics_remain_weak",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_checkpoint_doc_exists() -> None:
    assert _CHECKPOINT.exists()
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001" in text
    assert _FRAMEWORK_HEALTH in text
    assert _DECISION in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_generic_adapter_profile_application_checkpoint"


def test_supported_profile_count_is_three() -> None:
    data = _load_summary()
    assert data["supported_profile_count"] == 3
    assert "Supported profile count" in _CHECKPOINT.read_text(encoding="utf-8")


def test_all_three_profile_ids_listed() -> None:
    data = _load_summary()
    text = _CHECKPOINT.read_text(encoding="utf-8")
    for profile_id in _PROFILES:
        assert profile_id in data["supported_profiles_reviewed"]
        assert profile_id in text


def test_supported_profile_inventory_completed() -> None:
    assert _load_summary()["supported_profile_inventory_completed"] is True
    assert "Supported profile inventory" in _CHECKPOINT.read_text(encoding="utf-8")


def test_cross_profile_consistency_assessed() -> None:
    assert _load_summary()["cross_profile_consistency_assessed"] is True
    assert "Cross-profile consistency assessment" in _CHECKPOINT.read_text(encoding="utf-8")


def test_profile_specific_findings_completed() -> None:
    assert _load_summary()["profile_specific_findings_completed"] is True
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "TBRRidge" in text
    assert "SCM" in text
    assert "AugSynth" in text


def test_framework_health_assessed() -> None:
    data = _load_summary()
    assert data["framework_health_assessed"] is True
    assert data["framework_health"] == _FRAMEWORK_HEALTH


def test_source_of_truth_boundary_preserved() -> None:
    assert _load_summary()["source_of_truth_boundary_preserved"] is True
    assert "source-of-truth" in _CHECKPOINT.read_text(encoding="utf-8").lower()


def test_generic_adapter_summarizer_only_preserved() -> None:
    assert _load_summary()["generic_adapter_summarizer_only_preserved"] is True
    assert "summarizer" in _CHECKPOINT.read_text(encoding="utf-8").lower()


def test_boundary_and_prohibited_actions_preserved() -> None:
    data = _load_summary()
    assert data["boundary_statuses_preserved"] is True
    assert data["prohibited_actions_preserved"] is True


def test_positive_decision_semantics_remain_weak() -> None:
    assert _load_summary()["positive_decision_semantics_remain_weak"] is True
    assert "APPROVE_REVIEW_CONTINUATION" in _CHECKPOINT.read_text(encoding="utf-8")


def test_decision_exact_value() -> None:
    assert _load_summary()["decision"] == _DECISION


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
    assert _NEXT in _CHECKPOINT.read_text(encoding="utf-8")


def test_roadmap_references_artifact() -> None:
    assert "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001" in _ROADMAP.read_text(
        encoding="utf-8"
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert (
        "METHOD-PROMOTION-GENERIC-ADAPTER-PROFILE-APPLICATION-CHECKPOINT-001"
        in _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    )


def test_method_soundness_references_artifact() -> None:
    assert (
        "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001"
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
