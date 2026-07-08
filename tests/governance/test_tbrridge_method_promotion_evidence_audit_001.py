"""Governance tests for TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_AUDIT = _REPO / "docs/track_d/TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001.md"
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001_summary.json"
_OPEN_INVESTIGATIONS = _REPO / "docs/governance/OPEN_INVESTIGATIONS_001.json"

_READINESS_STATUSES = (
    "METHOD_PROMOTION_EVIDENCE_NOT_REVIEWED",
    "METHOD_PROMOTION_EVIDENCE_BLOCKED_BY_MISSING_CHAIN",
    "METHOD_PROMOTION_EVIDENCE_BLOCKED_BY_UNCERTAINTY_REVIEW",
    "METHOD_PROMOTION_EVIDENCE_BLOCKED_BY_INTERVAL_SEMANTICS",
    "METHOD_PROMOTION_EVIDENCE_BLOCKED_BY_VALIDATION_GAPS",
    "METHOD_PROMOTION_EVIDENCE_BLOCKED_BY_CLAIM_BOUNDARY",
    "METHOD_PROMOTION_EVIDENCE_BUILDING",
    "METHOD_PROMOTION_EVIDENCE_READY_FOR_CONTRACT",
    "METHOD_PROMOTION_EVIDENCE_DEFERRED",
)

_EVIDENCE_COMPONENTS = (
    "False-confidence diagnostic evidence",
    "Leakage diagnostic evidence",
    "Placebo calibration evidence",
    "Coverage validation evidence",
    "Uncertainty candidate review evidence",
    "Interval semantics evidence",
    "Null-control false-positive behavior",
    "Directional-error behavior",
    "Positive-control recovery",
    "Regime sensitivity",
    "Donor-pool sensitivity",
    "Regularization sensitivity",
    "Outlier sensitivity",
    "Fold geometry sensitivity",
    "Metric/estimand alignment",
    "Aggregate/pooled geometry blocker",
    "Claim authorization boundary",
    "Production catalog status",
    "Production compatibility evidence",
    "Downstream readout safety",
)

_ALLOWED_SURFACES = (
    "DIAGNOSTIC_ONLY",
    "RESEARCH_OR_REVIEW_ONLY",
    "METHOD_PROMOTION_EVIDENCE_SUMMARY",
    "METHOD_PROMOTION_READINESS_SUMMARY",
    "REMAINING_BLOCKERS_SUMMARY",
    "FUTURE_PROMOTION_CONTRACT_INPUT",
)

_PROHIBITED_SURFACES = (
    "METHOD_PROMOTION_NOTICE",
    "PRODUCTION_COMPATIBILITY_NOTICE",
    "CATALOG_UNBLOCK_NOTICE",
    "UNCERTAINTY_APPROVAL_NOTICE",
    "CONFIDENCE_INTERVAL_CLAIM",
    "P_VALUE_CLAIM",
    "STATISTICAL_SIGNIFICANCE_CLAIM",
    "CAUSAL_LIFT_CLAIM",
    "ROI_CLAIM",
    "PRODUCTION_READOUT",
)

_FORBIDDEN_TRUE_FLAGS = (
    "method_promotion_runtime_implemented",
    "method_promoted",
    "method_unblocked",
    "method_promotion_authorized",
    "production_catalog_unblocked",
    "production_compatibility_authorized",
    "production_authorization_granted",
    "production_readout_authorized",
    "uncertainty_candidate_approved",
    "uncertainty_authorized",
    "confidence_interval_authorized",
    "p_value_authorized",
    "statistical_significance_authorized",
    "coverage_approval_authorized",
    "coverage_computed",
    "interval_computed",
    "kfold_inference_implemented",
    "placebo_inference_implemented",
    "estimator_implemented",
    "inference_implemented",
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
    "tbrridge_method_promotion_evidence_audit_completed",
    "evidence_chain_reviewed",
    "uncertainty_candidate_review_runtime_reviewed",
    "promotion_evidence_sufficiency_matrix_defined",
    "promotion_stop_go_criteria_defined",
    "future_method_promotion_review_contract_recommended",
)


def _load_summary() -> dict:
    return json.loads(_SUMMARY.read_text(encoding="utf-8"))


def _load_registry() -> dict:
    return json.loads(_OPEN_INVESTIGATIONS.read_text(encoding="utf-8"))


def test_audit_doc_exists() -> None:
    assert _AUDIT.exists()
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001" in text
    assert "tbrridge_method_promotion_evidence_audited_no_method_promotion_or_catalog_unblock" in text


def test_summary_json_exists_and_valid() -> None:
    data = _load_summary()
    assert data["artifact_id"] == "TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001"
    assert data["status"] == "completed"
    assert data["failed_scenarios"] == []


def test_evidence_chain_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Evidence chain reviewed" in text
    assert "TBRRIDGE_FALSE_CONFIDENCE_DIAGNOSTIC_AUDIT_001" in text
    assert "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001" in text
    data = _load_summary()
    assert data["evidence_chain_reviewed"] is True


def test_uncertainty_candidate_review_runtime_reviewed() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Uncertainty-candidate review runtime summary" in text
    assert "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_RUNTIME_001" in text
    data = _load_summary()
    assert data["uncertainty_candidate_review_runtime_reviewed"] is True


def test_promotion_evidence_sufficiency_matrix_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Promotion evidence sufficiency matrix" in text
    for component in _EVIDENCE_COMPONENTS:
        assert component in text
    data = _load_summary()
    assert data["promotion_evidence_sufficiency_matrix_defined"] is True


def test_readiness_statuses_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for status in _READINESS_STATUSES:
        assert status in text


def test_go_criteria_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Go criteria" in text
    assert "interval semantics" in text.lower()
    assert "aggregate/pooled" in text.lower()
    assert "production compatibility kept separate" in text.lower()


def test_stop_criteria_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    assert "Stop criteria" in text
    assert "metric/estimand mismatch" in text.lower()
    assert "positive-control recovery failure" in text.lower()


def test_allowed_prohibited_surfaces_documented() -> None:
    text = _AUDIT.read_text(encoding="utf-8")
    for surface in _ALLOWED_SURFACES:
        assert surface in text
    for surface in _PROHIBITED_SURFACES:
        assert surface in text


def test_future_method_promotion_review_contract_recommended() -> None:
    data = _load_summary()
    assert data["recommended_next_artifact"] == "TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001"
    assert data["future_method_promotion_review_contract_recommended"] is True
    text = _AUDIT.read_text(encoding="utf-8")
    assert "TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001" in text


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
        == "tbrridge_method_promotion_evidence_audited_no_method_promotion_or_catalog_unblock"
    )
    assert data["scope"] == data["final_verdict"]


def test_governance_registry_references_artifact() -> None:
    reg = _load_registry()
    inv_ids = {inv["investigation_id"] for inv in reg["investigations"]}
    assert "INV-TBRRIDGE-METHOD-PROMOTION-EVIDENCE-AUDIT-001" in inv_ids
    lane_ids = {lane["lane_id"] for lane in reg["roadmap_lane_bindings"]}
    assert "TBRRIDGE-METHOD-PROMOTION-EVIDENCE-AUDIT-001" in lane_ids
    inv = next(
        i for i in reg["investigations"]
        if i["investigation_id"] == "INV-TBRRIDGE-METHOD-PROMOTION-EVIDENCE-AUDIT-001"
    )
    assert inv["status"] == "RESOLVED"
    assert inv["resolution_artifact"] == "TBRRIDGE_METHOD_PROMOTION_EVIDENCE_AUDIT_001"
