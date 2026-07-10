"""Governance tests for AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001_summary.json"
)
_PACKET_RUNTIME = (
    _REPO / "panel_exp/validation/augsynth_jackknife_promotion_evidence_packet_runtime_001.py"
)
_DECISION_RUNTIME = (
    _REPO / "panel_exp/validation/augsynth_jackknife_review_decision_runtime_001.py"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_INSTRUMENT = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_ALIAS = "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
_PROFILE_ID = "augsynth_jackknife_restricted_review_v1"
_VERDICT = "proceed_to_augsynth_generic_adapter_profile_contract_or_runtime_update"
_DECISION = "PROCEED_TO_AUGSYNTH_GENERIC_ADAPTER_PROFILE_CONTRACT_OR_RUNTIME_UPDATE"
_NEXT_RUNTIME = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001"
_LANE_A_NEXT = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001"

_FORBIDDEN_TRUE_FLAGS = (
    "generic_runtime_changed",
    "generic_adapter_profile_for_augsynth_implemented",
    "augsynth_profile_registered",
    "packet_runtime_changed",
    "decision_runtime_changed",
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
    "readiness_audit_completed",
    "packet_runtime_exists",
    "decision_runtime_exists",
    "packet_status_mapping_defined",
    "eligibility_status_mapping_defined",
    "decision_status_mapping_defined",
    "decision_scope_defined",
    "boundary_statuses_complete",
    "prohibited_actions_complete",
    "alias_research_only_substitution_blocked",
    "source_of_truth_boundary_preserved",
    "generic_adapter_summarizer_only_preserved",
    "augsynth_profile_id_defined",
    "proceed_to_generic_adapter_profile_registration_task",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001" in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "augsynth_generic_adapter_profile_readiness_audit"


def test_packet_and_decision_runtime_exist() -> None:
    assert _PACKET_RUNTIME.exists()
    assert _DECISION_RUNTIME.exists()
    data = _load_summary()
    assert data["packet_runtime_exists"] is True
    assert data["decision_runtime_exists"] is True


def test_profile_id_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert _PROFILE_ID in text
    data = _load_summary()
    assert data["augsynth_profile_id_defined"] is True
    assert data["augsynth_profile_id"] == _PROFILE_ID


def test_status_mappings_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_PROMOTION_REVIEW_INPUT" in text
    assert "ELIGIBLE_AS_RESTRICTED_REVIEW_INPUT" in text
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert "APPROVE_REVIEW_CONTINUATION" in text
    data = _load_summary()
    assert data["packet_status_mapping_defined"] is True
    assert data["eligibility_status_mapping_defined"] is True
    assert data["decision_status_mapping_defined"] is True


def test_decision_scope_and_boundaries() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "restricted_review" in text
    assert "NOT_REGISTERED_BY_THIS_DECISION" in text or "boundary_statuses" in text
    data = _load_summary()
    assert data["decision_scope_defined"] is True
    assert data["boundary_statuses_complete"] is True


def test_prohibited_actions_and_alias_blocking() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "generic adapter attempts promotion" in text.lower() or "promotion" in text.lower()
    assert _ALIAS in text
    data = _load_summary()
    assert data["prohibited_actions_complete"] is True
    assert data["alias_research_only_substitution_blocked"] is True


def test_source_of_truth_and_summarizer_boundary() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "source-of-truth" in text.lower() or "source of truth" in text.lower()
    assert "summarizer" in text.lower()
    data = _load_summary()
    assert data["source_of_truth_boundary_preserved"] is True
    assert data["generic_adapter_summarizer_only_preserved"] is True


def test_overall_readiness_and_proceed_flag() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "READY_FOR_GENERIC_ADAPTER_PROFILE_REGISTRATION_TASK" in text
    assert _DECISION in text
    data = _load_summary()
    assert data["overall_readiness"] == "READY_FOR_GENERIC_ADAPTER_PROFILE_REGISTRATION_TASK"
    assert data["proceed_to_generic_adapter_profile_registration_task"] is True


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
    assert data["recommended_next_artifact"] == _NEXT_RUNTIME
    assert _NEXT_RUNTIME in _AUDIT.read_text(encoding="utf-8")


def test_roadmap_references_artifact() -> None:
    assert "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001" in _ROADMAP.read_text(
        encoding="utf-8"
    )


def test_mip_audit_registry_references_artifact() -> None:
    assert (
        "AUGSYNTH-GENERIC-ADAPTER-PROFILE-READINESS-AUDIT-001"
        in _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    )


def test_method_soundness_references_artifact() -> None:
    assert (
        "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001"
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
