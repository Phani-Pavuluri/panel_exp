"""Governance tests for TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
_VERDICT = "tbrridge_promotion_review_decision_contract_defined_no_runtime_no_promotion"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "method_promoted",
    "instrument_promoted",
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
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
)

_REQUIRED_TRUE_FLAGS = (
    "review_decision_contract_completed",
    "exact_instrument_scope_defined",
    "required_input_packet_defined",
    "review_decision_object_defined",
    "decision_statuses_defined",
    "decision_mapping_rules_defined",
    "allowed_next_actions_defined",
    "prohibited_next_actions_defined",
    "claim_authorization_relationship_defined",
    "catalog_governance_relationship_defined",
    "production_compatibility_relationship_defined",
    "lane_b_relationship_defined",
    "future_runtime_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "tbrridge_promotion_review_decision_contract"


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_exact_instrument_scope_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert _INSTRUMENT in text
    assert "single_cell" in text
    assert "restricted_review" in text
    assert _load_summary()["instrument_identity"] == _INSTRUMENT
    assert _load_summary()["exact_instrument_scope_defined"] is True


def test_required_input_packet_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "TBRRidgePromotionReviewDecisionInput" in text
    assert "TBRRIDGE_PROMOTION_EVIDENCE_PACKET_ASSEMBLY_RUNTIME_001" in text
    assert _load_summary()["required_input_packet_defined"] is True


def test_review_decision_object_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "TBRRidgePromotionReviewDecision" in text
    assert "decision_status" in text
    assert _load_summary()["review_decision_object_defined"] is True


def test_decision_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert "REQUEST_ADDITIONAL_EVIDENCE" in text
    assert "NO_DECISION_PACKET_NOT_READY" in text
    assert _load_summary()["decision_statuses_defined"] is True


def test_decision_mapping_rules_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT" in text
    assert "REJECT_FOR_IDENTITY_MISMATCH" in text
    assert "DEFER_PENDING_PRODUCTION_COMPATIBILITY_REVIEW" in text
    assert _load_summary()["decision_mapping_rules_defined"] is True


def test_allowed_prohibited_next_actions_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Continue restricted-review diagnostics" in text
    assert "Method promotion" in text
    assert "TrustReport bypass" in text
    data = _load_summary()
    assert data["allowed_next_actions_defined"] is True
    assert data["prohibited_next_actions_defined"] is True


def test_claim_authorization_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert "NOT_AUTHORIZED" in text
    assert _load_summary()["claim_authorization_relationship_defined"] is True


def test_catalog_governance_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "does **not** unblock the catalog" in text
    assert _load_summary()["catalog_governance_relationship_defined"] is True


def test_production_compatibility_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "production compatibility" in text.lower()
    assert "out of scope" in text.lower()
    assert _load_summary()["production_compatibility_relationship_defined"] is True


def test_lane_b_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Lane B" in text
    assert "orthogonal" in text.lower()
    assert _load_summary()["lane_b_relationship_defined"] is True


def test_future_runtime_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001" in text
    assert _load_summary()["future_runtime_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001"


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "TBRRIDGE-PROMOTION-REVIEW-DECISION-CONTRACT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_CONTRACT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"
