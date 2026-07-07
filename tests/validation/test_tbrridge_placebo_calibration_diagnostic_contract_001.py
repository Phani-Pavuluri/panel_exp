"""Tests for TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.tbrridge_placebo_calibration_diagnostic_contract_001 import (
    ALLOWED_SURFACES,
    CONTRACT_POSITIVE_FLAGS,
    DIAGNOSTIC_STATUSES,
    DIRECTIONAL_INSTABILITY_RULES,
    FAILURE_CODES,
    FUTURE_RUNTIME_TESTS,
    NULL_CONSTRUCTION_RULES,
    PLACEBO_CONTAMINATION_RULES,
    PLACEBO_RANK_TAIL_RULES,
    PLACEBO_RISK_TYPES,
    PROHIBITED_SURFACES,
    REQUIRED_EVIDENCE,
    _AUTH_FLAGS,
    _VERDICT,
    build_scenarios,
    build_tbrridge_placebo_calibration_diagnostic_contract,
    evaluate_placebo_calibration_diagnostic,
    get_tbrridge_placebo_calibration_diagnostic_contract_metadata,
    list_diagnostic_statuses,
    list_future_runtime_tests,
    list_placebo_risk_types,
    run_validation,
    validate_tbrridge_placebo_calibration_diagnostic_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001_REPORT.md"


def test_contract_metadata_exists() -> None:
    meta = get_tbrridge_placebo_calibration_diagnostic_contract_metadata()
    assert meta["artifact_id"] == "TBRRIDGE_PLACEBO_CALIBRATION_DIAGNOSTIC_CONTRACT_001"
    assert meta["placebo_calibration_diagnostic_contract_defined"] is True


def test_diagnostic_statuses_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.diagnostic_statuses == DIAGNOSTIC_STATUSES
    assert list_diagnostic_statuses() == DIAGNOSTIC_STATUSES
    assert "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION" in contract.diagnostic_statuses


def test_placebo_risk_taxonomy_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.placebo_risk_types == PLACEBO_RISK_TYPES
    assert list_placebo_risk_types() == PLACEBO_RISK_TYPES
    assert "INVALID_NULL_PERIOD" in contract.placebo_risk_types


def test_required_evidence_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert "placebo_assignment_manifest" in contract.required_evidence
    assert contract.required_evidence == REQUIRED_EVIDENCE


def test_null_construction_rules_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.null_construction_rules == NULL_CONSTRUCTION_RULES
    assert contract.null_construction_rules_defined is True


def test_placebo_contamination_rules_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.placebo_contamination_rules == PLACEBO_CONTAMINATION_RULES


def test_placebo_rank_tail_rules_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.placebo_rank_tail_rules == PLACEBO_RANK_TAIL_RULES


def test_directional_instability_rules_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.directional_instability_rules == DIRECTIONAL_INSTABILITY_RULES


def test_allowed_prohibited_surfaces_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "PLACEBO_P_VALUE_CLAIM" in contract.prohibited_surfaces


def test_failure_packet_semantics_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.failure_packet_semantics_defined
    assert contract.failure_codes == FAILURE_CODES
    result = evaluate_placebo_calibration_diagnostic(evidence={})
    packet = result.to_failure_packet()
    assert packet is not None
    assert "failure_code" in packet


def test_future_runtime_tests_documented() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert contract.future_runtime_tests_documented
    assert list_future_runtime_tests() == FUTURE_RUNTIME_TESTS
    assert "blocks_placebo_p_value_ci_significance_coverage_surfaces" in contract.future_runtime_tests


def test_summary_json_matches_contract() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert data["artifact_id"] == contract.artifact_id
    assert data["final_verdict"] == contract.final_verdict
    assert data["recommended_next_artifact"] == contract.recommended_next_artifact


def test_forbidden_flags_false() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_tbrridge_placebo_calibration_diagnostic_contract_metadata()
    assert meta["placebo_inference_implemented"] is False
    assert meta["coverage_computed"] is False


def test_evaluate_blocks_invalid_null_construction() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_placebo_calibration_diagnostic(
        evidence=evidence,
        detected_risks=("INVALID_NULL_PERIOD",),
    )
    assert result.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_INVALID_NULL_CONSTRUCTION"
    assert result.failure_code == "INVALID_NULL_CONSTRUCTION"


def test_evaluate_blocks_placebo_contamination() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_placebo_calibration_diagnostic(
        evidence=evidence,
        detected_risks=("PLACEBO_DONOR_OVERLAP",),
    )
    assert result.diagnostic_status == "PLACEBO_CALIBRATION_BLOCKED_BY_PLACEBO_CONTAMINATION"
    assert result.failure_code == "PLACEBO_CONTAMINATION_DETECTED"


def test_evaluate_blocks_placebo_p_value_surface() -> None:
    evidence = {req: True for req in REQUIRED_EVIDENCE}
    result = evaluate_placebo_calibration_diagnostic(
        evidence=evidence,
        requested_surface="PLACEBO_P_VALUE_CLAIM",
    )
    assert result.failure_code == "PLACEBO_INFERENCE_SURFACE_BLOCKED"


def test_contract_validation_and_scenarios_pass() -> None:
    contract = build_tbrridge_placebo_calibration_diagnostic_contract()
    assert validate_tbrridge_placebo_calibration_diagnostic_contract(contract)["valid"] is True
    failed = [s["scenario_id"] for s in build_scenarios() if not s["passed"]]
    assert failed == []


def test_positive_flags_true() -> None:
    for key, val in CONTRACT_POSITIVE_FLAGS.items():
        assert val is True


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "PLACEBO_SEMANTICS_UNGOVERNED" in text or "placebo" in text.lower()


def test_run_validation_verdict() -> None:
    result = run_validation(write_summary=False)
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []
