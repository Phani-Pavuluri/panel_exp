"""Tests for TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.tbrridge_method_promotion_review_contract_001 import (
    ALLOWED_SURFACES,
    CONTRACT_POSITIVE_FLAGS,
    FAILURE_CODES,
    FUTURE_RUNTIME_TESTS,
    PROHIBITED_SURFACES,
    PROMOTION_RISK_TYPES,
    PROMOTION_REVIEW_STATUSES,
    REQUIRED_EVIDENCE,
    _AUTH_FLAGS,
    _VERDICT,
    build_scenarios,
    build_tbrridge_method_promotion_review_contract,
    evaluate_method_promotion_review,
    get_tbrridge_method_promotion_review_contract_metadata,
    list_future_runtime_tests,
    list_promotion_review_statuses,
    list_promotion_risk_types,
    run_validation,
    validate_tbrridge_method_promotion_review_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md"


def _full_evidence() -> dict[str, bool]:
    return {req: True for req in REQUIRED_EVIDENCE}


def test_contract_metadata_exists() -> None:
    meta = get_tbrridge_method_promotion_review_contract_metadata()
    assert meta["artifact_id"] == "TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001"
    assert meta["tbrridge_method_promotion_review_contract_defined"] is True


def test_promotion_review_statuses_documented() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    assert contract.promotion_review_statuses == PROMOTION_REVIEW_STATUSES
    assert list_promotion_review_statuses() == PROMOTION_REVIEW_STATUSES
    assert "METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW" in contract.promotion_review_statuses


def test_promotion_risk_taxonomy_documented() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    assert contract.promotion_risk_types == PROMOTION_RISK_TYPES
    assert list_promotion_risk_types() == PROMOTION_RISK_TYPES
    assert "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING" in contract.promotion_risk_types


def test_required_evidence_documented() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    assert "method_promotion_evidence_audit_report" in contract.required_evidence
    assert contract.required_evidence == REQUIRED_EVIDENCE
    assert len(contract.required_evidence) == 22


def test_allowed_prohibited_surfaces_documented() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "METHOD_PROMOTION_NOTICE" in contract.prohibited_surfaces


def test_failure_packet_semantics_documented() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    assert contract.promotion_failure_packet_semantics_defined
    assert contract.failure_codes == FAILURE_CODES
    result = evaluate_method_promotion_review(evidence={})
    packet = result.to_failure_packet()
    assert packet is not None
    assert "failure_code" in packet


def test_future_runtime_tests_documented() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    assert contract.promotion_future_runtime_tests_documented
    assert list_future_runtime_tests() == FUTURE_RUNTIME_TESTS
    assert "blocks_without_method_promotion_evidence_audit" in contract.future_runtime_tests


def test_summary_json_matches_contract() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    contract = build_tbrridge_method_promotion_review_contract()
    assert data["artifact_id"] == contract.artifact_id
    assert data["final_verdict"] == contract.final_verdict
    assert data["recommended_next_artifact"] == contract.recommended_next_artifact


def test_forbidden_flags_false() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_tbrridge_method_promotion_review_contract_metadata()
    assert meta["method_promoted"] is False
    assert meta["method_promotion_authorized"] is False


def test_evaluate_blocks_missing_audit() -> None:
    result = evaluate_method_promotion_review(evidence={})
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    assert result.failure_code == "MISSING_METHOD_PROMOTION_EVIDENCE_AUDIT"


def test_evaluate_blocks_blocking_uncertainty_review() -> None:
    result = evaluate_method_promotion_review(
        evidence={
            "method_promotion_evidence_audit_report": True,
            "uncertainty_candidate_review_packet": True,
        },
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC",
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_UNCERTAINTY_CANDIDATE_REVIEW"
    assert result.failure_code == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKING"


def test_evaluate_blocks_interval_semantics() -> None:
    evidence = {
        "method_promotion_evidence_audit_report": True,
        "uncertainty_candidate_review_packet": True,
        "false_confidence_audit_report": True,
        "leakage_diagnostic_report": True,
        "placebo_calibration_diagnostic_report": True,
        "coverage_validation_report": True,
    }
    result = evaluate_method_promotion_review(
        evidence=evidence,
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    assert result.failure_code == "INTERVAL_SEMANTICS_INCOMPLETE"


def test_evaluate_blocks_false_positive_evidence() -> None:
    evidence = _full_evidence()
    del evidence["null_control_false_positive_report"]
    result = evaluate_method_promotion_review(
        evidence=evidence,
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_FALSE_POSITIVE_EVIDENCE"
    assert result.failure_code == "NULL_CONTROL_FALSE_POSITIVE_INCOMPLETE"


def test_evaluate_blocks_metric_estimand_mismatch() -> None:
    result = evaluate_method_promotion_review(
        evidence=_full_evidence(),
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        production_compatibility_reviewed=True,
        metric_estimand_mismatch=True,
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH"
    assert result.failure_code == "METRIC_ESTIMAND_MISMATCH"


def test_evaluate_blocks_aggregate_pooled_geometry() -> None:
    result = evaluate_method_promotion_review(
        evidence=_full_evidence(),
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        production_compatibility_reviewed=True,
        aggregate_pooled_unsupported=True,
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_AGGREGATE_POOLED_GEOMETRY"
    assert result.failure_code == "AGGREGATE_POOLED_GEOMETRY_UNSUPPORTED"


def test_evaluate_ready_for_restricted_review() -> None:
    result = evaluate_method_promotion_review(
        evidence=_full_evidence(),
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
        production_compatibility_reviewed=True,
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_READY_FOR_RESTRICTED_REVIEW"
    assert result.authorized_for_promotion_summary is True


def test_evaluate_ready_with_restrictions() -> None:
    result = evaluate_method_promotion_review(
        evidence=_full_evidence(),
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS",
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_READY_WITH_RESTRICTIONS"
    assert result.authorized_for_promotion_summary is True


def test_evaluate_blocks_method_promotion_surface() -> None:
    result = evaluate_method_promotion_review(
        evidence=_full_evidence(),
        requested_surface="METHOD_PROMOTION_NOTICE",
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_BLOCKED_BY_CLAIM_AUTHORIZATION_BOUNDARY"
    assert result.failure_code == "METHOD_PROMOTION_SURFACE_BLOCKED"


def test_evaluate_requires_production_compatibility_review() -> None:
    result = evaluate_method_promotion_review(
        evidence=_full_evidence(),
        requested_surface="PRODUCTION_COMPATIBILITY_NOTICE",
        uncertainty_candidate_review_status="UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW",
    )
    assert result.review_status == "METHOD_PROMOTION_REVIEW_REQUIRES_PRODUCTION_COMPATIBILITY_REVIEW"
    assert result.failure_code == "PRODUCTION_COMPATIBILITY_NOT_REVIEWED"


def test_contract_validation_passes() -> None:
    contract = build_tbrridge_method_promotion_review_contract()
    validation = validate_tbrridge_method_promotion_review_contract(contract)
    assert validation["valid"] is True
    assert validation["issues"] == []


def test_build_scenarios_all_pass() -> None:
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    assert failed == []


def test_run_validation_verdict() -> None:
    result = run_validation()
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "TBRRIDGE_METHOD_PROMOTION_REVIEW_CONTRACT_001" in text
    assert _VERDICT in text


def test_positive_contract_flags() -> None:
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        contract = build_tbrridge_method_promotion_review_contract()
        assert getattr(contract, key) is expected
