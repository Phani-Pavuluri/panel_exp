"""Governance tests for METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_CHECKPOINT = _REPO / "docs/track_d/METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001.md"
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001_summary.json"
)
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"
_MIP_AUDIT_REGISTRY = _REPO / "docs/MIP_AUDIT_REGISTRY.md"
_ROADMAP = _REPO / "docs/ROADMAP_V4.md"
_METHOD_SOUNDNESS = _REPO / "docs/METHOD_SOUNDNESS_AND_GAP_ROADMAP_001.md"

_TBRRIDGE = "geo.tbrridge.kfold.single_cell.delta_mu.diagnostic_interval.restricted_review"
_SCM = "geo.scm.jackknife.single_cell.delta_mu.null_monitor"
_VERDICT = "framework_checkpoint_completed_two_applications_reviewed_no_runtime_no_promotion"
_NEXT = "METHOD_PROMOTION_GENERIC_CONTRACTS_001"
_NEXT_RUNTIME_CONTRACT = "METHOD_PROMOTION_GENERIC_RUNTIME_CONTRACT_001"
_LANE_A_NEXT = "AUGSYNTH_GENERIC_ADAPTER_PROFILE_READINESS_AUDIT_001"

_FORBIDDEN_TRUE_FLAGS = (
    "runtime_implemented",
    "generic_runtime_implemented",
    "generic_contract_runtime_implemented",
    "method_promoted",
    "instrument_promoted",
    "tbrridge_promoted",
    "scm_promoted",
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
    "framework_checkpoint_completed",
    "two_applications_reviewed",
    "tbrridge_application_reviewed",
    "scm_null_monitor_application_reviewed",
    "reusable_patterns_identified",
    "instrument_specific_patterns_identified",
    "framework_gaps_identified",
    "augsynth_did_risk_assessed",
    "pause_new_instrument_lanes_recommended",
    "generic_contracts_recommended",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def test_checkpoint_doc_exists() -> None:
    assert _CHECKPOINT.exists()
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001" in text
    assert _VERDICT in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001"
    assert data["status"] == "completed"
    assert data["artifact_type"] == "method_promotion_framework_application_checkpoint"


def test_two_applications_reviewed() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert _TBRRIDGE in text
    assert _SCM in text
    assert _load_summary()["two_applications_reviewed"] is True


def test_tbrridge_application_reviewed() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "TBRRIDGE_PROMOTION_REVIEW_DECISION_RUNTIME_001" in text
    assert "APPROVE_RESTRICTED_REVIEW_CONTINUATION" in text
    assert _load_summary()["tbrridge_application_reviewed"] is True


def test_scm_null_monitor_application_reviewed() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "SCM_JACKKNIFE_NULL_MONITOR_REVIEW_DECISION_RUNTIME_001" in text
    assert "APPROVE_NULL_MONITOR_REVIEW_CONTINUATION" in text
    assert _load_summary()["scm_null_monitor_application_reviewed"] is True


def test_reusable_patterns_identified() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "What generalized cleanly" in text
    assert "exact instrument identity" in text.lower()
    assert _load_summary()["reusable_patterns_identified"] is True


def test_instrument_specific_patterns_identified() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "What remained instrument-specific" in text
    assert "jackknife_stability" in text
    assert "positive_control_recovery" in text
    assert _load_summary()["instrument_specific_patterns_identified"] is True


def test_framework_gaps_identified() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "Framework gaps discovered" in text
    assert "generic typed framework contract" in text.lower()
    assert _load_summary()["framework_gaps_identified"] is True


def test_augsynth_did_risk_assessed() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "AugSynth" in text
    assert "DID" in text
    assert _load_summary()["augsynth_did_risk_assessed"] is True


def test_pause_new_instrument_lanes_recommended() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert "PAUSE_NEW_INSTRUMENT_LANES_AND_FORMALIZE_GENERIC_CONTRACTS" in text
    assert _load_summary()["pause_new_instrument_lanes_recommended"] is True


def test_generic_contracts_recommended() -> None:
    text = _CHECKPOINT.read_text(encoding="utf-8")
    assert _NEXT in text
    assert "MethodPromotionInstrumentIdentity" in text
    assert _load_summary()["generic_contracts_recommended"] is True


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
    assert data["recommended_next_artifact"] == _NEXT


def test_roadmap_references_artifact() -> None:
    text = _ROADMAP.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001" in text


def test_mip_audit_registry_references_artifact() -> None:
    text = _MIP_AUDIT_REGISTRY.read_text(encoding="utf-8")
    assert "METHOD-PROMOTION-FRAMEWORK-APPLICATION-CHECKPOINT-001" in text


def test_method_soundness_references_artifact() -> None:
    text = _METHOD_SOUNDNESS.read_text(encoding="utf-8")
    assert "METHOD_PROMOTION_FRAMEWORK_APPLICATION_CHECKPOINT_001" in text


def test_open_investigations_lane_a_next() -> None:
    registry = json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))
    lane_a = next(
        item
        for item in registry["roadmap_lane_bindings"]
        if item["lane_id"] == "LANE-A-TBRRIDGE-PROMOTION"
    )
    assert lane_a["next_artifact"] == _LANE_A_NEXT
