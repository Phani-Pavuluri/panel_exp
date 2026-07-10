"""Governance tests for AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_ALIAS = "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
_VERDICT = "augsynth_jackknife_review_decision_contract_defined_no_runtime_no_promotion"
_NEXT_DECISION_RUNTIME = "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_RUNTIME_001"
_LANE_A_NEXT = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "augsynth_decision_runtime_implemented",
    "generic_runtime_changed",
    "generic_adapter_profile_for_augsynth_implemented",
    "method_promoted",
    "instrument_promoted",
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
    "review_decision_contract_defined",
    "decision_input_contract_defined",
    "decision_output_contract_defined",
    "decision_statuses_defined",
    "decision_mapping_defined",
    "decision_precedence_defined",
    "positive_decision_semantics_defined",
    "allowed_next_actions_defined",
    "prohibited_actions_defined",
    "fixed_non_authorization_statuses_defined",
    "evidence_quality_boundary_defined",
    "generic_framework_compatibility_defined",
    "alias_research_only_rejects_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "augsynth_jackknife_review_decision_contract"


def test_decision_input_output_contracts_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "AugSynthJackknifeReviewDecisionInput" in text
    assert "AugSynthJackknifeReviewDecision" in text
    assert "AugSynthJackknifePromotionEvidencePacket" in text
    data = _load_summary()
    assert data["decision_input_contract_defined"] is True
    assert data["decision_output_contract_defined"] is True


def test_decision_statuses_mapping_precedence_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert "REJECT_FOR_RESEARCH_ONLY_SUBSTITUTION" in text
    assert "REJECT_FOR_ALIAS_SUBSTITUTION" in text
    assert "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT" in text
    assert "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT" in text
    assert "Decision precedence" in text
    data = _load_summary()
    assert data["decision_statuses_defined"] is True
    assert data["decision_mapping_defined"] is True
    assert data["decision_precedence_defined"] is True


def test_positive_decision_semantics_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "restricted-review governance input" in text.lower()
    assert "does not mean" in text.lower()
    data = _load_summary()
    assert data["positive_decision_semantics_defined"] is True


def test_allowed_prohibited_actions_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "continue_augsynth_restricted_review_diagnostics" in text
    assert "augsynth_promotion" in text
    assert "trust_report_bypass" in text
    data = _load_summary()
    assert data["allowed_next_actions_defined"] is True
    assert data["prohibited_actions_defined"] is True


def test_fixed_non_authorization_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "NOT_AUTHORIZED_BY_THIS_DECISION" in text
    assert "NOT_UNBLOCKED_BY_THIS_DECISION" in text
    assert "NOT_PROMOTED_BY_THIS_DECISION" in text
    assert _load_summary()["fixed_non_authorization_statuses_defined"] is True


def test_evidence_quality_boundary_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "may not" in text.lower()
    assert "score evidence quality" in text.lower()
    assert _load_summary()["evidence_quality_boundary_defined"] is True


def test_generic_framework_compatibility_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "APPROVE_REVIEW_CONTINUATION" in text
    assert "generic runtime" in text.lower()
    assert _load_summary()["generic_framework_compatibility_defined"] is True


def test_alias_research_only_rejects_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert _ALIAS in text
    assert _INSTRUMENT in text
    assert "research_only cannot substitute" in text.lower() or "cannot substitute" in text.lower()
    assert _load_summary()["alias_research_only_rejects_defined"] is True


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
    assert data["recommended_next_artifact"] == _NEXT_DECISION_RUNTIME
    assert _NEXT_DECISION_RUNTIME in _CONTRACT.read_text(encoding="utf-8")


def test_roadmap_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001" in _ROADMAP.read_text(
        encoding="utf-8"
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert "AUGSYNTH-JACKKNIFE-REVIEW-DECISION-CONTRACT-001" in _MIP_AUDIT_REGISTRY.read_text(
        encoding="utf-8"
    )


def test_method_soundness_references_artifact() -> None:
    assert "AUGSYNTH_JACKKNIFE_REVIEW_DECISION_CONTRACT_001" in _METHOD_SOUNDNESS.read_text(
        encoding="utf-8"
    )


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
