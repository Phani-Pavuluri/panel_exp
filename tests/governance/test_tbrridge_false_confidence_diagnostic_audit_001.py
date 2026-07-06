"""Tests for TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_READINESS_TAXONOMY = (
    "TBRRIDGE_DIAGNOSTIC_BLOCKED",
    "TBRRIDGE_RESEARCH_SANDBOX",
    "TBRRIDGE_DIAGNOSTIC_ONLY",
    "TBRRIDGE_POINT_ESTIMATE_REVIEW_ONLY",
    "TBRRIDGE_UNCERTAINTY_EVIDENCE_BUILDING",
    "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW",
)

_FORBIDDEN_TRUE_FLAGS = (
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "multiplicity_correction_computed",
    "covariance_computed",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "method_promoted",
    "method_unblocked",
    "production_catalog_unblocked",
    "production_authorization_granted",
    "production_readout_authorized",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001" in text
    assert "tbrridge_false_confidence_risks_audited_no_inference_or_promotion" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_tbrridge_brb_kfold_placebo_covered() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRidge + BRB" in text or "TBRRidge_BlockResidualBootstrap" in text
    assert "KFold" in text or "Kfold" in text
    assert "Placebo" in text


def test_tbr_aggregate_pooled_risk_covered() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "aggregate" in text.lower() and "pooled" in text.lower()
    data = _load_summary()
    assert data["pooled_aggregate_risk_documented"] is True


def test_diagnostic_readiness_taxonomy_present() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for status in _READINESS_TAXONOMY:
        assert status in text


def test_regularization_sensitivity_risk_documented() -> None:
    data = _load_summary()
    assert data["regularization_sensitivity_risk_documented"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "regularization" in text.lower()


def test_fold_leakage_risk_documented() -> None:
    data = _load_summary()
    assert data["fold_leakage_risk_documented"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "leakage" in text.lower()


def test_placebo_calibration_risk_documented() -> None:
    data = _load_summary()
    assert data["placebo_calibration_risk_documented"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "placebo calibration" in text.lower() or "Placebo calibration" in text


def test_extrapolation_risk_documented() -> None:
    data = _load_summary()
    assert data["extrapolation_risk_documented"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "extrapolation" in text.lower()


def test_coverage_gap_documented() -> None:
    data = _load_summary()
    assert data["coverage_gap_documented"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "coverage" in text.lower()


def test_recommended_next_artifact_present() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_CONTRACT_001"
    assert data["alternative_next_artifact"] == "AUGSYNTH_JK_COVERAGE_VALIDATION_AUDIT_001"


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert data["final_verdict"] == "tbrridge_false_confidence_risks_audited_no_inference_or_promotion"
    assert data["scope"] == data["final_verdict"]


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data[flag] is False, flag


def test_capability_flags_true() -> None:
    data = _load_summary()
    assert data["tbrridge_inventory_completed"] is True
    assert data["false_confidence_risks_documented"] is True
    assert data["next_smallest_artifact_recommended"] is True


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-FALSE-CONFIDENCE-DIAGNOSTIC-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-FALSE-CONFIDENCE-DIAGNOSTIC-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-FALSE-CONFIDENCE-DIAGNOSTIC-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001"
