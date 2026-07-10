"""Governance tests for SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CONTRACT = (
    _REPO / "docs/track_d/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001.md"
)
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
_VERDICT = "scm_jackknife_null_monitor_evidence_packet_contract_defined_no_runtime_no_promotion"
_NEXT_RUNTIME = "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_RUNTIME_001"

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
    "estimator_implemented",
    "inference_implemented",
    "new_validation_experiments_run",
    "lane_b_runtime_changed",
    "mip_decisioning_authorized",
    "trust_report_bypassed",
)

_REQUIRED_TRUE_FLAGS = (
    "evidence_packet_contract_completed",
    "exact_instrument_identity_defined",
    "null_monitor_scope_defined",
    "required_evidence_categories_defined",
    "scm_specific_evidence_categories_defined",
    "packet_readiness_statuses_defined",
    "promotion_review_eligibility_defined",
    "evidence_completeness_rules_defined",
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
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "scm_jackknife_null_monitor_promotion_evidence_packet_contract"


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
    assert "single_cell" in text
    assert "null_monitor" in text
    assert "jackknife" in text
    assert _load_summary()["instrument_identity"] == _INSTRUMENT


def test_null_monitor_scope_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "NULL_MONITOR_STATUS_SUMMARY" in text
    assert "FALSE_POSITIVE_DIAGNOSTIC_SUMMARY" in text
    assert "not a causal lift readout" in text.lower() or "not:" in text.lower()
    assert _load_summary()["null_monitor_scope_defined"] is True


def test_required_evidence_categories_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "BLOCKED_MISSING_NULL_CONTROL_EVIDENCE" in text
    assert "BLOCKED_MISSING_JACKKNIFE_STABILITY_EVIDENCE" in text
    assert "BLOCKED_MISSING_DONOR_POOL_DIAGNOSTICS" in text
    assert "BLOCKED_MISSING_PRE_PERIOD_FIT_DIAGNOSTICS" in text
    assert _load_summary()["required_evidence_categories_defined"] is True


def test_scm_specific_evidence_categories_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "jackknife_stability" in text
    assert "donor_pool_diagnostics" in text
    assert "pre_period_fit_diagnostics" in text
    assert _load_summary()["scm_specific_evidence_categories_defined"] is True


def test_packet_readiness_statuses_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_NULL_MONITOR_REVIEW_INPUT" in text
    assert "PACKET_BLOCKED_NULL_MONITOR_SCOPE_VIOLATION" in text
    assert _load_summary()["packet_readiness_statuses_defined"] is True


def test_promotion_review_eligibility_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "ELIGIBLE_AS_NULL_MONITOR_REVIEW_INPUT" in text
    assert "NOT_ELIGIBLE_FOR_CATALOG_UNBLOCK" in text
    assert _load_summary()["promotion_review_eligibility_defined"] is True


def test_evidence_completeness_rules_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Null-control evidence cannot substitute for donor-pool diagnostics" in text
    assert "TBRRidge pilot evidence cannot satisfy SCM evidence categories" in text
    assert _load_summary()["evidence_completeness_rules_defined"] is True


def test_framework_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_REVIEW_FRAMEWORK_GENERALIZATION_001" in text
    assert "not TBRRidge-specific" in text
    assert _load_summary()["framework_relationship_defined"] is True


def test_claim_authorization_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in text
    assert _load_summary()["claim_authorization_relationship_defined"] is True


def test_catalog_production_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "catalog remains blocked" in text.lower() or "Catalog remains blocked" in text
    assert "production compatibility is out of scope" in text.lower()
    assert _load_summary()["catalog_production_relationship_defined"] is True


def test_lane_b_mip_relationship_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert "Lane B" in text
    assert "MIP" in text
    assert "orthogonal" in text.lower()
    assert _load_summary()["lane_b_mip_relationship_defined"] is True


def test_future_runtime_defined() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    assert _NEXT_RUNTIME in text
    assert "SCMJackknifeNullMonitorPromotionEvidencePacket" in text
    assert _load_summary()["future_runtime_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == _NEXT_RUNTIME


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "SCM-JACKKNIFE-NULL-MONITOR-PROMOTION-EVIDENCE-PACKET-CONTRACT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001"
