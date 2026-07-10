"""Governance tests for TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001_summary.json"
)
_RUNTIME = _REPO / "panel_exp/validation/tbrridge_promotion_review_decision_runtime_001.py"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
_VERDICT = "tbrridge_promotion_review_decision_runtime_implemented_no_promotion_no_claim_authorization"

_FORBIDDEN_TRUE_FLAGS = (
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
    "raw_evidence_quality_scored",
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
)

_REQUIRED_TRUE_FLAGS = (
    "review_decision_runtime_implemented",
    "decision_mapping_rules_implemented",
    "packet_status_consumed",
    "promotion_review_eligibility_consumed",
    "missing_evidence_preserved",
    "blockers_preserved",
    "allowed_next_actions_emitted",
    "prohibited_next_actions_emitted",
    "fixed_non_authorization_statuses_emitted",
    "claim_authorization_relationship_preserved",
    "catalog_governance_relationship_preserved",
    "production_compatibility_relationship_preserved",
    "lane_b_relationship_preserved",
    "evidence_quality_boundary_preserved",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "tbrridge_promotion_review_decision_runtime"


def test_runtime_module_exists() -> None:
    assert _RUNTIME.exists()
    text = _RUNTIME.read_text(encoding="utf-8")
    assert "decide_tbrridge_promotion_review" in text
    assert "TBRRidgePromotionReviewDecision" in text


def test_import_api_works() -> None:
    from panel_exp.validation.tbrridge_promotion_review_decision_runtime_001 import (
        TBRRidgePromotionReviewDecision,
        TBRRidgePromotionReviewDecisionInput,
        TBRRidgePromotionReviewDecisionStatus,
        decide_tbrridge_promotion_review,
    )

    assert TBRRidgePromotionReviewDecisionStatus.APPROVE_RESTRICTED_REVIEW_CONTINUATION
    assert TBRRidgePromotionReviewDecisionInput
    assert TBRRidgePromotionReviewDecision
    assert decide_tbrridge_promotion_review


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_decision_mapping_implemented() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert "REQUEST_ADDITIONAL_EVIDENCE" in text
    assert _load_summary()["decision_mapping_rules_implemented"] is True


def test_fixed_non_authorization_statuses_emitted() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "NOT_AUTHORIZED_BY_THIS_DECISION" in text
    assert "NOT_UNBLOCKED_BY_THIS_DECISION" in text
    assert "NOT_PROMOTED_BY_THIS_DECISION" in text
    assert _load_summary()["fixed_non_authorization_statuses_emitted"] is True


def test_evidence_quality_boundary_preserved() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "evidence quality" in text.lower() or "Do not score" in text
    assert _load_summary()["evidence_quality_boundary_preserved"] is True


def test_exact_instrument_scope() -> None:
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert _INSTRUMENT in text
    assert _load_summary()["instrument_identity"] == _INSTRUMENT


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001"


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "TBRRIDGE-PROMOTION-REVIEW-DECISION-RUNTIME-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001"
