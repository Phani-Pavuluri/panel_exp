"""Tests for TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.tbrridge_uncertainty_candidate_review_contract_001 import (
    ALLOWED_SURFACES,
    CONTRACT_POSITIVE_FLAGS,
    EVIDENCE_CHAIN_REQUIREMENTS,
    FAILURE_CODES,
    FUTURE_RUNTIME_TESTS,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    REVIEW_RISK_TYPES,
    REVIEW_STATUSES,
    _AUTH_FLAGS,
    _VERDICT,
    build_scenarios,
    build_tbrridge_uncertainty_candidate_review_contract,
    evaluate_uncertainty_candidate_review,
    get_tbrridge_uncertainty_candidate_review_contract_metadata,
    list_future_runtime_tests,
    list_review_risk_types,
    list_review_statuses,
    run_validation,
    validate_tbrridge_uncertainty_candidate_review_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001_REPORT.md"


def _full_evidence() -> dict[str, bool]:
    return {req: True for req in REQUIRED_EVIDENCE}


def test_contract_metadata_exists() -> None:
    meta = get_tbrridge_uncertainty_candidate_review_contract_metadata()
    assert meta["artifact_id"] == "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001"
    assert meta["uncertainty_candidate_review_contract_defined"] is True


def test_review_statuses_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert contract.review_statuses == REVIEW_STATUSES
    assert list_review_statuses() == REVIEW_STATUSES
    assert "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC" in contract.review_statuses


def test_review_risk_taxonomy_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert contract.review_risk_types == REVIEW_RISK_TYPES
    assert list_review_risk_types() == REVIEW_RISK_TYPES
    assert "LEAKAGE_DIAGNOSTIC_BLOCKING" in contract.review_risk_types


def test_required_evidence_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert "false_confidence_audit_report" in contract.required_evidence
    assert contract.required_evidence == REQUIRED_EVIDENCE
    assert len(contract.required_evidence) == 18


def test_evidence_chain_requirements_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert contract.evidence_chain_requirements == EVIDENCE_CHAIN_REQUIREMENTS
    assert contract.evidence_chain_requirements_defined is True


def test_allowed_prohibited_surfaces_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "UNCERTAINTY_APPROVAL_NOTICE" in contract.prohibited_surfaces


def test_failure_packet_semantics_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert contract.failure_packet_semantics_defined
    assert contract.failure_codes == FAILURE_CODES
    result = evaluate_uncertainty_candidate_review(evidence={})
    packet = result.to_failure_packet()
    assert packet is not None
    assert "failure_code" in packet


def test_future_runtime_tests_documented() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert contract.future_runtime_tests_documented
    assert list_future_runtime_tests() == FUTURE_RUNTIME_TESTS
    assert "blocks_without_false_confidence_audit_report" in contract.future_runtime_tests


def test_summary_json_matches_contract() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    assert data["artifact_id"] == contract.artifact_id
    assert data["final_verdict"] == contract.final_verdict
    assert data["recommended_next_artifact"] == contract.recommended_next_artifact


def test_forbidden_flags_false() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_tbrridge_uncertainty_candidate_review_contract_metadata()
    assert meta["uncertainty_candidate_approved"] is False
    assert meta["uncertainty_authorized"] is False


def test_evaluate_blocks_missing_false_confidence_audit() -> None:
    result = evaluate_uncertainty_candidate_review(evidence={})
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    assert result.failure_code == "MISSING_FALSE_CONFIDENCE_AUDIT"


def test_evaluate_blocks_blocking_leakage() -> None:
    result = evaluate_uncertainty_candidate_review(
        evidence={"false_confidence_audit_report": True, "kfold_leakage_diagnostic_report": True},
        leakage_diagnostic_status="KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_LEAKAGE_DIAGNOSTIC"
    assert result.failure_code == "LEAKAGE_DIAGNOSTIC_BLOCKING"


def test_evaluate_blocks_blocking_placebo() -> None:
    evidence = {
        "false_confidence_audit_report": True,
        "kfold_leakage_diagnostic_report": True,
        "placebo_calibration_diagnostic_report": True,
    }
    result = evaluate_uncertainty_candidate_review(
        evidence=evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_PLACEBO_CALIBRATION"
    assert result.failure_code == "PLACEBO_CALIBRATION_BLOCKING"


def test_evaluate_blocks_missing_coverage_validation() -> None:
    evidence = {
        "false_confidence_audit_report": True,
        "kfold_leakage_diagnostic_report": True,
        "placebo_calibration_diagnostic_report": True,
    }
    result = evaluate_uncertainty_candidate_review(
        evidence=evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_MISSING_EVIDENCE_CHAIN"
    assert result.failure_code == "MISSING_COVERAGE_VALIDATION_REPORT"


def test_evaluate_blocks_interval_semantics() -> None:
    evidence = {
        "false_confidence_audit_report": True,
        "kfold_leakage_diagnostic_report": True,
        "placebo_calibration_diagnostic_report": True,
        "coverage_validation_report": True,
    }
    result = evaluate_uncertainty_candidate_review(
        evidence=evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_INTERVAL_SEMANTICS"
    assert result.failure_code == "INTERVAL_SEMANTICS_INCOMPLETE"


def test_evaluate_blocks_metric_estimand_mismatch() -> None:
    result = evaluate_uncertainty_candidate_review(
        evidence=_full_evidence(),
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
        metric_estimand_mismatch=True,
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_BLOCKED_BY_METRIC_ESTIMAND_MISMATCH"
    assert result.failure_code == "METRIC_ESTIMAND_MISMATCH"


def test_evaluate_ready_for_restricted_review() -> None:
    result = evaluate_uncertainty_candidate_review(
        evidence=_full_evidence(),
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_FOR_RESTRICTED_REVIEW"
    assert result.authorized_for_review_summary is True


def test_evaluate_ready_with_restrictions() -> None:
    result = evaluate_uncertainty_candidate_review(
        evidence=_full_evidence(),
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_WITH_RESTRICTIONS",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_READY_WITH_RESTRICTIONS"
    assert result.authorized_for_review_summary is True


def test_evaluate_blocks_uncertainty_approval_surface() -> None:
    result = evaluate_uncertainty_candidate_review(
        evidence=_full_evidence(),
        requested_surface="UNCERTAINTY_APPROVAL_NOTICE",
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
        coverage_validation_status="COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW",
    )
    assert result.review_status == "UNCERTAINTY_CANDIDATE_REVIEW_REQUIRES_METHOD_REVIEW"
    assert result.failure_code == "UNCERTAINTY_APPROVAL_SURFACE_BLOCKED"


def test_contract_validation_passes() -> None:
    contract = build_tbrridge_uncertainty_candidate_review_contract()
    validation = validate_tbrridge_uncertainty_candidate_review_contract(contract)
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
    assert "TBRRIDGE_UNCERTAINTY_CANDIDATE_REVIEW_CONTRACT_001" in text
    assert _VERDICT in text


def test_positive_contract_flags() -> None:
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        contract = build_tbrridge_uncertainty_candidate_review_contract()
        assert getattr(contract, key) is expected
