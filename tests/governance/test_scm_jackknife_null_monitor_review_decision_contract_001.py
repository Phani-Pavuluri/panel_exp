"""Governance tests for SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = _REPO / "docs/track_d/SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
_CATALOG_ALIAS = "geo.scm.jackknife.null_monitor.delta_mu.delete_one_diagnostic.restricted_review"
_VERDICT = "scm_jackknife_null_monitor_review_decision_contract_defined_no_runtime_no_promotion"
_NEXT_DECISION_RUNTIME = "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001"
_NEXT_CHECKPOINT = "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001"
_NEXT_GENERIC = "METHOD_PROMOTION_GENERIC_CONTRACTS_001"
_NEXT_RUNTIME_CONTRACT = "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001"
_LANE_A_NEXT = "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "scm_promoted",
    "scm_jackknife_promoted",
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
    "review_decision_contract_completed",
    "exact_instrument_identity_defined",
    "catalog_alias_preserved_without_substitution",
    "input_object_defined",
    "output_decision_object_defined",
    "decision_statuses_defined",
    "decision_mapping_rules_defined",
    "precedence_rules_defined",
    "allowed_next_actions_defined",
    "prohibited_next_actions_defined",
    "fixed_non_authorization_statuses_defined",
    "null_monitor_continuation_semantics_defined",
    "framework_relationship_defined",
    "claim_authorization_relationship_defined",
    "catalog_production_relationship_defined",
    "lane_b_mip_relationship_defined",
    "future_runtime_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_contract_doc_exists() -> None:
    assert _CONTRACT.exists()
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "scm_jackknife_null_monitor_review_decision_contract"


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_exact_instrument_identity_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert _INSTRUMENT in text
    assert _load_summary()["instrument_identity"] == _INSTRUMENT


def test_catalog_alias_preserved_without_substitution() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert _CATALOG_ALIAS in text
    assert "cannot substitute" in text.lower() or "cannot substitute canonical" in text.lower()
    assert _load_summary()["catalog_alias_preserved_without_substitution"] is True


def test_input_object_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "SCMJackknifeNullMonitorReviewDecisionInput" in text
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001" in text
    assert _load_summary()["input_object_defined"] is True


def test_output_decision_object_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "SCMJackknifeNullMonitorReviewDecision" in text
    assert _load_summary()["output_decision_object_defined"] is True


def test_decision_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION" in text
    assert "REJECT_FOR_NULL_MONITOR_SCOPE_VIOLATION" in text
    assert "NO_DECISION_PACKET_NOT_READY" in text
    assert _load_summary()["decision_statuses_defined"] is True


def test_decision_mapping_rules_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT" in text
    assert "REQUEST_ADDITIONAL_EVIDENCE" in text
    assert "REJECT_FOR_METHOD_VALIDITY" in text
    assert _load_summary()["decision_mapping_rules_defined"] is True


def test_precedence_rules_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Precedence" in text
    assert _load_summary()["precedence_rules_defined"] is True


def test_allowed_prohibited_next_actions_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "continue_null_monitor_diagnostics" in text
    assert "scm_promotion" in text
    assert "trust_report_bypass" in text
    data = _load_summary()
    assert data["allowed_next_actions_defined"] is True
    assert data["prohibited_next_actions_defined"] is True


def test_fixed_non_authorization_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "NOT_AUTHORIZED_BY_THIS_DECISION" in text
    assert "NOT_UNBLOCKED_BY_THIS_DECISION" in text
    assert "NULL_MONITOR_ONLY" in text
    assert _load_summary()["fixed_non_authorization_statuses_defined"] is True


def test_null_monitor_continuation_semantics_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION" in text
    assert "null-monitor continuation" in text.lower() or "null monitor continuation" in text.lower()
    assert _load_summary()["null_monitor_continuation_semantics_defined"] is True


def test_framework_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001" in text
    assert _load_summary()["framework_relationship_defined"] is True


def test_claim_authorization_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert _load_summary()["claim_authorization_relationship_defined"] is True


def test_catalog_production_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "catalog remains" in text.lower() or "Catalog remains" in text
    assert "production compatibility is out of scope" in text.lower()
    assert _load_summary()["catalog_production_relationship_defined"] is True


def test_lane_b_mip_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Lane B" in text
    assert "MIP" in text
    assert _load_summary()["lane_b_mip_relationship_defined"] is True


def test_future_runtime_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert _NEXT_DECISION_RUNTIME in text
    assert _load_summary()["future_runtime_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT_DECISION_RUNTIME


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "SCM-JACKKNIFE-NULL-MONITOR-REVIEW-DECISION-CONTRACT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_CONTRACT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
