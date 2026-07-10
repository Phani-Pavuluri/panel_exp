"""Governance tests for METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_PRIMARY = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
_SECONDARY = "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review"
_VERDICT = "next_instrument_selected_for_framework_application_no_runtime_no_promotion"

_CANDIDATES = (
    "geo.tbrridge.brb.single_cell.delta_mu.diagnostic_interval.restricted_review",
    "geo.tbrridge.placebo.single_cell.delta_mu.diagnostic_interval.restricted_review",
    "geo.augsynth.jackknife.single_cell.delta_mu.diagnostic_interval.restricted_review",
    "geo.scm.jackknife.single_cell.delta_mu.null_monitor",
    "geo.did.bootstrap.single_cell.delta_mu.diagnostic_interval.restricted_review",
)

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
    "next_instrument_selection_audit_completed",
    "selection_criteria_defined",
    "candidate_set_evaluated",
    "candidate_scores_recorded",
    "candidate_specific_notes_recorded",
    "primary_recommendation_selected",
    "secondary_candidate_recorded",
    "deferred_candidates_recorded",
    "recommended_next_artifact_defined",
    "framework_application_not_tbr_specific",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_next_instrument_selection_audit"


def test_required_true_flags_present() -> None:
    data = _load_summary()
    for flag in _REQUIRED_TRUE_FLAGS:
        assert data.get(flag) is True, flag


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_selection_criteria_defined() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence availability" in text
    assert "Framework fit" in text
    assert _load_summary()["selection_criteria_defined"] is True


def test_all_five_candidates_evaluated() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for candidate in _CANDIDATES:
        assert candidate in text
    assert _load_summary()["candidate_set_evaluated"] is True


def test_candidate_scores_recorded() -> None:
    data = _load_summary()
    scores = data["candidate_scores"]
    assert len(scores) == 5
    assert scores[_PRIMARY] == 32
    assert _load_summary()["candidate_scores_recorded"] is True


def test_primary_recommendation_selected() -> None:
    data = _load_summary()
    text = _AUDIT.read_text(encoding="utf-8")
    assert data["primary_recommended_instrument"] == _PRIMARY
    assert "Primary recommendation" in text
    assert data["primary_recommendation_selected"] is True


def test_secondary_candidate_recorded() -> None:
    data = _load_summary()
    assert data["secondary_candidate_instrument"] == _SECONDARY
    assert _load_summary()["secondary_candidate_recorded"] is True


def test_deferred_candidates_recorded() -> None:
    data = _load_summary()
    assert len(data["deferred_candidate_instruments"]) >= 3
    assert _load_summary()["deferred_candidates_recorded"] is True


def test_recommended_next_artifact_defined() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "SCM_JACKKNIFE_NULL_MONITOR_PROMOTION_EVIDENCE_PACKET_CONTRACT_001"
    assert _load_summary()["recommended_next_artifact_defined"] is True


def test_framework_application_not_tbr_specific() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "not TBRRidge-specific" in text or "not TBR-specific" in text
    assert _load_summary()["framework_application_not_tbr_specific"] is True


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-NEXT-INSTRUMENT-SELECTION-AUDIT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_NEXT_INSTRUMENT_SELECTION_AUDIT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001"
