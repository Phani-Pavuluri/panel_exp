"""Governance tests for TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_READINESS_STATUSES = (
    "UNCERTAINTY_CANDIDATE_REVIEW_NOT_STARTED",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_DIAGNOSTICS",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_RISK",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_MISCALIBRATION",
    "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_COVERAGE_VALIDATION_GAPS",
    "UNCERTAINTY_CANDIDATE_REVIEW_EVIDENCE_BUILDING",
    "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_CONTRACT",
    "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW",
    "UNCERTAINTY_CANDIDATE_REVIEW_DEFERRED",
)

_EVIDENCE_COMPONENTS = (
    "False-confidence audit",
    "KFold leakage diagnostic contract/runtime",
    "Placebo calibration diagnostic contract/runtime",
    "Coverage validation audit/contract/runtime",
    "Interval semantics evidence",
    "Null-control evidence",
    "Positive-control evidence",
    "Regime sensitivity evidence",
    "Regularization sensitivity evidence",
    "Donor-pool sensitivity evidence",
    "Outlier sensitivity evidence",
    "Aggregate/pooled misuse blocker",
    "Metric/estimand alignment",
    "Statistical promotion threshold evidence",
    "Production catalog status",
    "Trusted readout / claim authorization",
    "Method promotion review boundaries",
)

_ALLOWED_SURFACES = (
    "DIAGNOSTIC_ONLY",
    "RESEARCH_OR_REVIEW_ONLY",
    "UNCERTAINTY_CANDIDATE_REVIEW_READINESS_SUMMARY",
    "EVIDENCE_SUFFICIENCY_SUMMARY",
    "REMAINING_BLOCKERS_SUMMARY",
    "METHOD_REVIEW_INPUT_PACKET_DESCRIPTION",
)

_PROHIBITED_SURFACES = (
    "UNCERTAINTY_APPROVAL_NOTICE",
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
    "METHOD_PROMOTION_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
)

_FORBIDDEN_TRUE_FLAGS = (
    "uncertainty_candidate_review_runtime_implemented",
    "uncertainty_candidate_approved",
    "uncertainty_authorized",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "coverage_runtime_implemented_new",
    "coverage_computed",
    "interval_computed",
    "kfold_inference_implemented",
    "placebo_inference_implemented",
    "estimator_implemented",
    "inference_implemented",
    "bootstrap_inference_implemented",
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

_POSITIVE_FLAGS = (
    "uncertainty_candidate_review_audit_completed",
    "evidence_chain_reviewed",
    "leakage_gate_reviewed",
    "placebo_gate_reviewed",
    "coverage_gate_reviewed",
    "evidence_sufficiency_matrix_defined",
    "stop_go_criteria_defined",
    "future_candidate_review_contract_recommended",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001" in text
    assert "tbrridge_uncertainty_candidate_review_audited_no_uncertainty_approval_or_promotion" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_evidence_chain_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence chain reviewed" in text
    assert "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001" in text
    assert "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001" in text
    data = _load_summary()
    assert data["evidence_chain_reviewed"] is True


def test_kfold_leakage_gate_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "KFold leakage gate review" in text
    assert "TBRRIDGE_KFOLD_LEAKAGE_DIAGNOSTIC_RUNTIME_001" in text
    data = _load_summary()
    assert data["leakage_gate_reviewed"] is True


def test_placebo_calibration_gate_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Placebo calibration gate review" in text
    assert "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_RUNTIME_001" in text
    data = _load_summary()
    assert data["placebo_gate_reviewed"] is True


def test_coverage_validation_gate_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Coverage validation gate review" in text
    assert "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_RUNTIME_001" in text
    data = _load_summary()
    assert data["coverage_gate_reviewed"] is True


def test_evidence_sufficiency_matrix_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence sufficiency matrix" in text
    for component in _EVIDENCE_COMPONENTS:
        assert component in text
    data = _load_summary()
    assert data["evidence_sufficiency_matrix_defined"] is True


def test_candidate_review_readiness_statuses_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for status in _READINESS_STATUSES:
        assert status in text


def test_go_criteria_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Go criteria" in text
    assert "leakage diagnostic" in text.lower()
    assert "interval semantics" in text.lower()
    assert "aggregate/pooled" in text.lower()


def test_stop_criteria_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Stop criteria" in text
    assert "metric/estimand mismatch" in text.lower()


def test_allowed_prohibited_surfaces_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for surface in _ALLOWED_SURFACES:
        assert surface in text
    for surface in _PROHIBITED_SURFACES:
        assert surface in text


def test_future_candidate_review_contract_recommended() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001"
    assert data["future_candidate_review_contract_recommended"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001" in text


def test_forbidden_flags_false() -> None:
    data = _load_summary()
    for flag in _FORBIDDEN_TRUE_FLAGS:
        assert data[flag] is False, flag


def test_positive_flags_true() -> None:
    data = _load_summary()
    for flag in _POSITIVE_FLAGS:
        assert data[flag] is True, flag


def test_final_verdict_correct() -> None:
    data = _load_summary()
    assert (
        data["final_verdict"]
        == "tbrridge_uncertainty_candidate_review_audited_no_uncertainty_approval_or_promotion"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-UNCERTAINTY-CANDIDATE-REVIEW-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-UNCERTAINTY-CANDIDATE-REVIEW-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-UNCERTAINTY-CANDIDATE-REVIEW-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_AUDIT_001"
