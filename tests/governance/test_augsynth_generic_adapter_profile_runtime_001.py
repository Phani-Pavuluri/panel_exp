"""Governance tests for AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_RUNTIME_DOC = _REPO / "docs/track_d/AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001_summary.json"
)
_GENERIC_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_GENERIC_RUNTIME_001_summary.json"
_GENERIC_RUNTIME = _REPO / "panel_exp/validation/method_promotion_generic_runtime_001.py"
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

_PROFILE_ID = "augsynth_jackknife_restricted_review_v1"
_INSTRUMENT = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_ALIAS = "geo.augsynth.jackknife.single_cell.delta_mu.research_interval.research_only"
_VERDICT = (
    "augsynth_generic_adapter_profile_registered_summarizer_only_no_promotion_no_claim_authorization"
)
_NEXT = "METHOD_PROMOTION_GENERIC_ADAPTER_PROFILE_APPLICATION_CHECKPOINT_001"
_LANE_A_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"

_FORBIDDEN_TRUE_FLAGS = (
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
    "generic_runtime_changed",
    "generic_adapter_profile_for_augsynth_implemented",
    "augsynth_profile_registered",
    "packet_status_mapping_implemented",
    "eligibility_status_mapping_implemented",
    "decision_status_mapping_implemented",
    "alias_research_only_substitution_blocked",
    "source_of_truth_boundary_preserved",
    "generic_adapter_summarizer_only_preserved",
    "boundary_statuses_preserved",
    "prohibited_actions_preserved",
    "approval_maps_to_generic_review_continuation_only",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_runtime_doc_exists() -> None:
    assert _RUNTIME_DOC.exists()
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001" in text
    assert _PROFILE_ID in text
    assert _VERDICT in text


def test_summary_json_validates() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "augsynth_generic_adapter_profile_runtime"


def test_generic_runtime_summary_includes_augsynth_profile() -> None:
    data = json.loads(_GENERIC_SUMMARY.read_text(encoding="utf-8"))
    assert data["augsynth_profile_supported"] is True
    assert data["augsynth_profile_registered"] is True
    assert data["supported_profile_count"] == 3
    assert _INSTRUMENT in data["supported_profiles"]


def test_profile_id_defined() -> None:
    data = _load_summary()
    assert data["profile_id"] == _PROFILE_ID
    assert _PROFILE_ID in _GENERIC_RUNTIME.read_text(encoding="utf-8")


def test_status_mappings_implemented() -> None:
    data = _load_summary()
    assert data["packet_status_mapping_implemented"] is True
    assert data["eligibility_status_mapping_implemented"] is True
    assert data["decision_status_mapping_implemented"] is True
    text = _RUNTIME_DOC.read_text(encoding="utf-8")
    assert "PACKET_READY_FOR_REVIEW_INPUT" in text
    assert "APPROVE_REVIEW_CONTINUATION" in text


def test_source_of_truth_boundary_preserved() -> None:
    data = _load_summary()
    assert data["source_of_truth_boundary_preserved"] is True
    assert data["packet_runtime_changed"] is False
    assert data["decision_runtime_changed"] is False
    assert "source-of-truth" in _RUNTIME_DOC.read_text(encoding="utf-8").lower()


def test_generic_adapter_summarizer_only() -> None:
    data = _load_summary()
    assert data["generic_adapter_summarizer_only_preserved"] is True
    assert "summarizer" in _RUNTIME_DOC.read_text(encoding="utf-8").lower()


def test_boundary_and_prohibited_actions_preserved() -> None:
    data = _load_summary()
    assert data["boundary_statuses_preserved"] is True
    assert data["prohibited_actions_preserved"] is True
    assert data["alias_research_only_substitution_blocked"] is True


def test_approval_maps_to_generic_review_continuation_only() -> None:
    data = _load_summary()
    assert data["approval_maps_to_generic_review_continuation_only"] is True
    assert data["decision_scope"] == "restricted_review"


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


def test_roadmap_references_artifact() -> None:
    assert "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001" in _ROADMAP.read_text(encoding="utf-8")


def test_mip_audit_registry_references_artifact() -> None:
    assert "AUGSYNTH-GENERIC-ADAPTER-PROFILE-RUNTIME-001" in _MIP_AUDIT_REGISTRY.read_text(
        encoding="utf-8"
    )


def test_method_soundness_references_artifact() -> None:
    assert "AUGSYNTH_GENERIC_ADAPTER_PROFILE_RUNTIME_001" in _METHOD_SOUNDNESS.read_text(
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


def test_packet_and_decision_runtimes_unchanged() -> None:
    assert _PACKET_RUNTIME.exists()
    assert _DECISION_RUNTIME.exists()
    assert _load_summary()["packet_runtime_changed"] is False
    assert _load_summary()["decision_runtime_changed"] is False
