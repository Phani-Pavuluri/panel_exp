"""Governance tests for METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001.md"
_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_CANDIDATE_IDENTITY = (
    "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
)
_VERDICT = "proceed_with_narrowed_augsynth_scope_before_evidence_packet_contract"
_DECISION = "PROCEED_WITH_NARROWED_AUGSYNTH_SCOPE"
_NEXT_AUDIT = "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001"
_LANE_A_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "augsynth_runtime_implemented",
    "augsynth_evidence_packet_contract_implemented",
    "augsynth_decision_contract_implemented",
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
    "proceed_to_unrestricted_augsynth",
)

_REQUIRED_TRUE_FLAGS = (
    "augsynth_readiness_audit_completed",
    "candidate_instrument_identity_defined",
    "readiness_criteria_defined",
    "evidence_inventory_completed",
    "readiness_assessment_completed",
    "narrowed_scope_defined",
    "required_future_evidence_categories_defined",
    "blockers_defined",
    "warnings_defined",
    "generic_framework_compatibility_assessed",
    "proceed_with_narrowed_scope",
    "augsynth_evidence_packet_contract_recommended",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_augsynth_readiness_audit"


def test_readiness_audit_completed() -> None:
    assert _load_summary()["augsynth_readiness_audit_completed"] is True


def test_candidate_identity_defined() -> None:
    data = _load_summary()
    assert data["candidate_instrument_identity_defined"] is True
    assert data["candidate_instrument_identity"] == _CANDIDATE_IDENTITY
    assert _CANDIDATE_IDENTITY in _AUDIT.read_text(encoding="utf-8")


def test_readiness_criteria_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "READY" in text and "PARTIAL" in text
    assert _load_summary()["readiness_criteria_defined"] is True


def test_evidence_inventory_completed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence inventory" in text
    assert "AUGSYNTH_ASCM_DEVELOPMENT_ROADMAP_001" in text
    assert _load_summary()["evidence_inventory_completed"] is True


def test_readiness_assessment_completed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Readiness assessment table" in text
    assert _load_summary()["readiness_assessment_completed"] is True


def test_narrowed_scope_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Proposed narrowed scope" in text
    assert "restricted_review" in text
    assert _load_summary()["narrowed_scope_defined"] is True


def test_required_future_evidence_categories_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "augmentation_component_diagnostics" in text
    assert "jackknife_stability" in text
    assert _load_summary()["required_future_evidence_categories_defined"] is True


def test_blockers_and_warnings_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "BLOCKED_MISSING_CLAIM_BOUNDARY" in text
    assert "SCM null-monitor evidence cannot substitute" in text
    data = _load_summary()
    assert data["blockers_defined"] is True
    assert data["warnings_defined"] is True


def test_generic_framework_compatibility_assessed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Generic framework compatibility" in text
    assert "METHOD_PROMOTION_GENERIC_RUNTIME_001" in text
    assert _load_summary()["generic_framework_compatibility_assessed"] is True


def test_decision_is_proceed_with_narrowed_scope() -> None:
    data = _load_summary()
    assert data["decision"] == _DECISION
    assert "PROCEED_WITH_NARROWED_AUGSYNTH_SCOPE" in _AUDIT.read_text(encoding="utf-8")


def test_unrestricted_augsynth_not_approved() -> None:
    data = _load_summary()
    assert data["proceed_to_unrestricted_augsynth"] is False
    text = _AUDIT.read_text(encoding="utf-8")
    assert "proceed_to_unrestricted_augsynth" in text or "not approved" in text.lower()


def test_evidence_packet_contract_recommended() -> None:
    data = _load_summary()
    assert data["augsynth_evidence_packet_contract_recommended"] is True
    assert data["recommended_next_artifact"] == _NEXT_AUDIT


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
    assert data["recommended_next_artifact"] == _NEXT_AUDIT
    assert "AUGSYNTH_JACKKNIFE_PROMOTION_EVIDENCE_PACKET_CONTRACT_001" in _AUDIT.read_text(
        encoding="utf-8"
    )


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-AUGSYNTH-READINESS-AUDIT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_AUGSYNTH_READINESS_AUDIT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
