"""Governance tests for TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_CANDIDATE_INTERVAL_MEANINGS = (
    "diagnostic uncertainty band",
    "KFold variability summary",
    "empirical stability band",
    "model sensitivity band",
    "prediction interval",
    "confidence interval",
    "credible interval",
    "causal effect uncertainty interval",
    "production reporting interval",
)

_ALLOWED_LANGUAGE = (
    "diagnostic uncertainty summary",
    "review-only interval diagnostic",
    "KFold variability diagnostic",
    "sensitivity/stability summary",
    "evidence input for future validation",
)

_PROHIBITED_LANGUAGE = (
    "confidence interval",
    "credible interval",
    "statistically significant",
    "p-value support",
    "calibrated causal uncertainty",
    "production uncertainty estimate",
    "approved lift interval",
    "ROI interval",
    "claim-ready interval",
)

_STRONGER_EVIDENCE_REQUIREMENTS = (
    "nominal-vs-empirical coverage validation",
    "null-control false-positive validation",
    "directional-error validation",
    "positive-control recovery validation",
    "regime sensitivity validation",
    "fold geometry sensitivity validation",
    "metric/estimand alignment",
    "aggregate/pooled geometry blocker",
    "claim authorization boundary",
)

_FORBIDDEN_TRUE_FLAGS = (
    "interval_computed",
    "coverage_computed",
    "confidence_interval_authorized",
    "credible_interval_authorized",
    "calibrated_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "uncertainty_authorized",
    "uncertainty_candidate_approved",
    "method_promoted",
    "method_unblocked",
    "method_promotion_authorized",
    "production_catalog_unblocked",
    "production_compatibility_authorized",
    "production_authorization_granted",
    "production_readout_authorized",
    "kfold_inference_implemented",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
    "p_value_computed",
    "confidence_interval_computed",
    "uncertainty_computed",
    "effect_estimate_computed_new",
    "lift_computed_new",
    "roi_computed_new",
    "mmm_runtime_calls_implemented",
    "llm_decisioning_authorized",
)

_POSITIVE_FLAGS = (
    "tbrridge_interval_semantics_audit_completed",
    "interval_semantics_reviewed",
    "allowed_interval_language_defined",
    "prohibited_interval_language_defined",
    "stronger_interval_authorization_requirements_defined",
    "runtime_packet_integration_target_defined",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001" in text
    assert "tbrridge_interval_semantics_audited_no_interval_computation_or_authorization" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_current_tbrridge_posture_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "RANK_0" in text
    assert "BLOCKED" in text
    assert "STAGE_2_DIAGNOSTIC_ONLY" in text


def test_candidate_interval_meanings_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Candidate interval meanings reviewed" in text
    for meaning in _CANDIDATE_INTERVAL_MEANINGS:
        assert meaning in text


def test_allowed_interval_language_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Allowed interval language" in text
    for phrase in _ALLOWED_LANGUAGE:
        assert phrase in text
    data = _load_summary()
    assert data["allowed_interval_language_defined"] is True


def test_prohibited_interval_language_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Prohibited interval language" in text
    for phrase in _PROHIBITED_LANGUAGE:
        assert phrase in text
    data = _load_summary()
    assert data["prohibited_interval_language_defined"] is True


def test_stronger_interval_authorization_requirements_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence required before interval authorization" in text
    for req in _STRONGER_EVIDENCE_REQUIREMENTS:
        assert req in text
    data = _load_summary()
    assert data["stronger_interval_authorization_requirements_defined"] is True


def test_runtime_packet_integration_target_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Runtime packet integration target" in text
    assert "interval_semantics_report" in text
    assert "generate_tbrridge_method_promotion_review" in text
    data = _load_summary()
    assert data["runtime_packet_integration_target_defined"] is True


def test_recommended_next_artifact() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001"
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_NULL_CONTROL_FALSE_POSITIVE_AUDIT_001" in text


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data.get(flag) is False, flag


def test_positive_flags_true() -> None:
    data = _load_summary()
    for flag in _POSITIVE_FLAGS:
        assert data[flag] is True, flag


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "tbrridge_interval_semantics_audited_no_interval_computation_or_authorization"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-INTERVAL-SEMANTICS-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-INTERVAL-SEMANTICS-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-INTERVAL-SEMANTICS-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_INTERVAL_SEMANTICS_AUDIT_001"
