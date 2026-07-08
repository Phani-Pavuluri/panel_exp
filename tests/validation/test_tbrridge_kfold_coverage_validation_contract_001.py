"""Tests for TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.tbrridge_kfold_coverage_validation_contract_001 import (
    ALLOWED_SURFACES,
    CONTRACT_POSITIVE_FLAGS,
    COVERAGE_RISK_TYPES,
    COVERAGE_VALIDATION_STATUSES,
    FAILURE_CODES,
    FUTURE_RUNTIME_TESTS,
    INTERVAL_SEMANTICS_REQUIREMENTS,
    NULL_CONTROL_REQUIREMENTS,
    POSITIVE_CONTROL_REQUIREMENTS,
    PROHIBITED_SURFACES,
    REGIME_REQUIREMENTS,
    REQUIRED_EVIDENCE,
    SIMULATION_DESIGN_REQUIREMENTS,
    _AUTH_FLAGS,
    _VERDICT,
    build_scenarios,
    build_tbrridge_kfold_coverage_validation_contract,
    evaluate_coverage_validation,
    get_tbrridge_kfold_coverage_validation_contract_metadata,
    list_coverage_risk_types,
    list_coverage_validation_statuses,
    list_future_runtime_tests,
    run_validation,
    validate_tbrridge_kfold_coverage_validation_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001_REPORT.md"


def test_contract_metadata_exists() -> None:
    meta = get_tbrridge_kfold_coverage_validation_contract_metadata()
    assert meta["artifact_id"] == "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001"
    assert meta["coverage_validation_contract_defined"] is True


def test_coverage_validation_statuses_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.coverage_validation_statuses == COVERAGE_VALIDATION_STATUSES
    assert list_coverage_validation_statuses() == COVERAGE_VALIDATION_STATUSES
    assert "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK" in contract.coverage_validation_statuses


def test_coverage_risk_taxonomy_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.coverage_risk_types == COVERAGE_RISK_TYPES
    assert list_coverage_risk_types() == COVERAGE_RISK_TYPES
    assert "INTERVAL_SEMANTICS_UNDEFINED" in contract.coverage_risk_types


def test_required_evidence_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert "leakage_diagnostic_report" in contract.required_evidence
    assert contract.required_evidence == REQUIRED_EVIDENCE
    assert len(contract.required_evidence) == 18


def test_interval_semantics_requirements_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.interval_semantics_requirements == INTERVAL_SEMANTICS_REQUIREMENTS
    assert contract.interval_semantics_requirements_defined is True


def test_simulation_design_requirements_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.simulation_design_requirements == SIMULATION_DESIGN_REQUIREMENTS
    assert contract.simulation_design_requirements_defined is True


def test_null_control_requirements_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.null_control_requirements == NULL_CONTROL_REQUIREMENTS
    assert contract.null_control_requirements_defined is True


def test_positive_control_requirements_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.positive_control_requirements == POSITIVE_CONTROL_REQUIREMENTS
    assert contract.positive_control_requirements_defined is True


def test_regime_requirements_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.regime_requirements == REGIME_REQUIREMENTS
    assert contract.regime_requirements_defined is True


def test_allowed_prohibited_surfaces_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "COVERAGE_APPROVAL_CLAIM" in contract.prohibited_surfaces


def test_failure_packet_semantics_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.failure_packet_semantics_defined
    assert contract.failure_codes == FAILURE_CODES
    result = evaluate_coverage_validation(evidence={})
    packet = result.to_failure_packet()
    assert packet is not None
    assert "failure_code" in packet


def test_future_runtime_tests_documented() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert contract.future_runtime_tests_documented
    assert list_future_runtime_tests() == FUTURE_RUNTIME_TESTS
    assert "blocks_without_leakage_diagnostic_report" in contract.future_runtime_tests


def test_summary_json_matches_contract() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    contract = build_tbrridge_kfold_coverage_validation_contract()
    assert data["artifact_id"] == contract.artifact_id
    assert data["final_verdict"] == contract.final_verdict
    assert data["recommended_next_artifact"] == contract.recommended_next_artifact


def test_forbidden_flags_false() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_tbrridge_kfold_coverage_validation_contract_metadata()
    assert meta["coverage_runtime_implemented"] is False
    assert meta["coverage_computed"] is False
    assert meta["interval_computed"] is False


def test_evaluate_blocks_missing_leakage_report() -> None:
    result = evaluate_coverage_validation(evidence={})
    assert result.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK"
    assert result.failure_code == "MISSING_LEAKAGE_DIAGNOSTIC_REPORT"


def test_evaluate_blocks_blocking_leakage_status() -> None:
    result = evaluate_coverage_validation(
        evidence={"leakage_diagnostic_report": True},
        leakage_diagnostic_status="KFOLD_LEAKAGE_BLOCKED_BY_TEMPORAL_LEAKAGE",
    )
    assert result.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_LEAKAGE_RISK"
    assert result.failure_code == "LEAKAGE_DIAGNOSTIC_BLOCKING"


def test_evaluate_blocks_missing_interval_semantics() -> None:
    evidence = {
        "leakage_diagnostic_report": True,
        "placebo_calibration_diagnostic_report": True,
    }
    result = evaluate_coverage_validation(
        evidence=evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    assert result.validation_status == "COVERAGE_VALIDATION_BLOCKED_BY_MISSING_INTERVAL_SEMANTICS"
    assert result.failure_code == "MISSING_INTERVAL_SEMANTICS_REPORT"


def test_evaluate_blocks_coverage_approval_surface() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_coverage_validation(
        evidence=evidence,
        requested_surface="COVERAGE_APPROVAL_CLAIM",
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    assert result.validation_status == "COVERAGE_VALIDATION_REQUIRES_METHOD_REVIEW"
    assert result.failure_code == "COVERAGE_APPROVAL_SURFACE_BLOCKED"


def test_evaluate_ready_with_full_evidence() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_coverage_validation(
        evidence=evidence,
        leakage_diagnostic_status="KFOLD_LEAKAGE_DIAGNOSTIC_READY",
        placebo_calibration_status="PLACEBO_CALIBRATION_DIAGNOSTIC_READY",
    )
    assert result.validation_status == "COVERAGE_VALIDATION_READY_FOR_DIAGNOSTIC_REVIEW"
    assert result.authorized_for_diagnostic_summary is True


def test_contract_validation_passes() -> None:
    contract = build_tbrridge_kfold_coverage_validation_contract()
    validation = validate_tbrridge_kfold_coverage_validation_contract(contract)
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
    assert "TBRRIDGE_KFOLD_COVERAGE_VALIDATION_CONTRACT_001" in text
    assert _VERDICT in text


def test_positive_contract_flags() -> None:
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        contract = build_tbrridge_kfold_coverage_validation_contract()
        assert getattr(contract, key) is expected
