"""Governance tests for METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_FRAMEWORK = _REPO / "docs/track_d/METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_PILOT = "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
_VERDICT = "method_promotion_review_framework_generalized_docs_only_no_runtime_no_promotion"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "generic_runtime_implemented",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "statistical_claim_authorized",
    "confidence_interval_claim_authorized",
    "p_value_claim_authorized",
    "significance_claim_authorized",
    "causal_lift_claim_authorized",
    "business_lift_claim_authorized",
    "roi_roas_claim_authorized",
    "decision_recommendation_authorized",
    "estimator_implemented",
    "inference_implemented",
    "new_validation_experiments_run",
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
)

_REQUIRED_TRUE_FLAGS = (
    "framework_generalization_completed",
    "pilot_pattern_extracted",
    "generic_instrument_identity_schema_defined",
    "generic_evidence_category_registry_defined",
    "generic_packet_readiness_statuses_defined",
    "generic_review_decision_statuses_defined",
    "decision_mapping_framework_defined",
    "claim_catalog_production_boundaries_defined",
    "reusable_vs_instrument_specific_split_defined",
    "candidate_next_instruments_listed",
    "future_generic_runtime_plan_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_framework_doc_exists() -> None:
    assert _FRAMEWORK.exists()
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_review_framework_generalization"


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_framework_generalization_completed() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "reusable governance pattern" in text.lower() or "reusable promotion" in text.lower()
    assert _load_summary()["framework_generalization_completed"] is True


def test_pilot_pattern_extracted() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "Evidence packet contract" in text
    assert "Review decision runtime" in text
    assert _PILOT in text
    assert _load_summary()["pilot_pattern_extracted"] is True


def test_generic_instrument_identity_schema_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "estimator_family" in text
    assert "inference_family" in text
    assert "exact-instrument scoped" in text.lower() or "exact-instrument" in text.lower()
    assert _load_summary()["generic_instrument_identity_schema_defined"] is True


def test_generic_evidence_category_registry_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "null_control_false_positive" in text
    assert "catalog_classification" in text
    assert _load_summary()["generic_evidence_category_registry_defined"] is True


def test_generic_packet_readiness_statuses_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_REVIEW_INPUT" in text
    assert "PACKET_BLOCKED_CROSS_ESTIMAND" in text
    assert _load_summary()["generic_packet_readiness_statuses_defined"] is True


def test_generic_review_decision_statuses_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert "REJECT_FOR_CROSS_ESTIMAND" in text
    assert _load_summary()["generic_review_decision_statuses_defined"] is True


def test_decision_mapping_framework_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW" in text
    assert "NO_DECISION_PACKET_NOT_READY" in text
    assert _load_summary()["decision_mapping_framework_defined"] is True


def test_claim_catalog_production_boundaries_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert "NOT_UNBLOCKED_BY_THIS_DECISION" in text
    assert _load_summary()["claim_catalog_production_boundaries_defined"] is True


def test_reusable_vs_instrument_specific_split_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "### Reusable" in text
    assert "### Instrument-specific" in text
    assert _load_summary()["reusable_vs_instrument_specific_split_defined"] is True


def test_candidate_next_instruments_listed() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "geo.tbrridge.brb.single_cell" in text
    assert "geo.augsynth.jackknife" in text
    assert _load_summary()["candidate_next_instruments_listed"] is True


def test_future_generic_runtime_plan_defined() -> None:
    text = _FRAMEWORK.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_REVIEW_FRAMEWORK_RUNTIME_CONTRACT_001" in text
    assert _load_summary()["future_generic_runtime_plan_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001"


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-REVIEW-FRAMEWORK-GENERALIZATION-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001"
