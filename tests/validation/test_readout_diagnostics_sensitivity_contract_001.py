"""Tests for READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.readout_diagnostics_sensitivity_contract_001 import (
    ALTERNATIVE_NEXT_ARTIFACT,
    CONTRACT_EXAMPLES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    DIAGNOSTIC_STATUSES,
    DIAGNOSTIC_TYPES,
    EVIDENCE_GATES,
    EVIDENCE_SUFFICIENCY_STATUSES,
    FAILURE_PACKET_FIELDS,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    INPUT_DEPENDENCIES,
    PLAN_FIELDS,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIREMENT_FIELDS,
    RESULT_FIELDS,
    RETRY_CATEGORIES,
    SENSITIVITY_STATUSES,
    SENSITIVITY_TYPES,
    _AUTH_FLAGS,
    build_readout_diagnostics_sensitivity_contract,
    build_scenarios,
    run_validation,
    validate_readout_diagnostics_sensitivity_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001_REPORT.md"


def test_diagnostic_types_defined() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.diagnostic_types == DIAGNOSTIC_TYPES
    assert "PARALLEL_TREND_DIAGNOSTIC" in contract.diagnostic_types
    assert "DONOR_SUPPORT_DIAGNOSTIC" in contract.diagnostic_types


def test_sensitivity_types_defined() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.sensitivity_types == SENSITIVITY_TYPES
    assert "BOOTSTRAP_SENSITIVITY" in contract.sensitivity_types
    assert "JACKKNIFE_SENSITIVITY" in contract.sensitivity_types


def test_diagnostic_statuses_defined() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.diagnostic_statuses == DIAGNOSTIC_STATUSES
    assert "DIAGNOSTIC_PASSED" in contract.diagnostic_statuses
    assert "DIAGNOSTIC_FAILED" in contract.diagnostic_statuses


def test_sensitivity_statuses_defined() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.sensitivity_statuses == SENSITIVITY_STATUSES
    assert "SENSITIVITY_PASSED" in contract.sensitivity_statuses
    assert "SENSITIVITY_INCONCLUSIVE" in contract.sensitivity_statuses


def test_evidence_sufficiency_statuses_defined() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.evidence_sufficiency_statuses == EVIDENCE_SUFFICIENCY_STATUSES
    assert "EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW" in contract.evidence_sufficiency_statuses
    assert "EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED" in contract.evidence_sufficiency_statuses


def test_requirement_plan_result_fields() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.requirement_fields == REQUIREMENT_FIELDS
    assert contract.plan_fields == PLAN_FIELDS
    assert contract.result_fields == RESULT_FIELDS
    assert "blocking_if_failed" in contract.requirement_fields
    assert "result_value" in contract.result_fields


def test_evidence_gates_order() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.evidence_gates == EVIDENCE_GATES
    assert len(contract.evidence_gates) == 11
    assert contract.evidence_gates[0] == "execution_artifact_presence_gate"
    assert contract.evidence_gates[-1] == "claim_review_handoff_gate"


def test_contract_semantics() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.diagnostics_sensitivity_contract_defined
    assert contract.diagnostic_requirement_contract_defined
    assert contract.sensitivity_requirement_contract_defined
    assert CONTRACT_POSITIVE_FLAGS["claim_boundaries_defined"]


def test_authorization_flags_all_false() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["diagnostics_sensitivity_runtime_implemented"]
    assert not contract.authorization_flags["diagnostic_check_executed"]
    assert not contract.authorization_flags["causal_claim_authorized"]
    assert not contract.authorization_flags["production_readout_authorized"]


def test_contract_validation_passes() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    result = validate_readout_diagnostics_sensitivity_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_future_contract_concepts() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert "ReadoutDiagnosticPlan" in contract.future_contract_concepts
    assert "ReadoutEvidenceSufficiencyReport" in contract.future_contract_concepts


def test_contract_examples_count() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.contract_examples == CONTRACT_EXAMPLES
    assert len(contract.contract_examples) == 10


def test_retry_categories() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "ADD_REQUIRED_DIAGNOSTIC_PLAN" in contract.retry_categories


def test_failure_packet_fields() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.failure_packet_fields == FAILURE_PACKET_FIELDS
    assert "suggested_retry_categories" in contract.failure_packet_fields


def test_future_implementation_tests_documented() -> None:
    scenarios = build_scenarios()
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_depends_on_includes_executor_adapters() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS" in contract.depends_on
    assert "READOUT_PLAN_RUNTIME_001" in contract.depends_on


def test_input_dependencies_include_execution_artifacts() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.input_dependencies == INPUT_DEPENDENCIES
    assert "instrument_execution_results" in contract.input_dependencies
    assert "estimator_inference_execution_report" in contract.input_dependencies


def test_recommended_next_artifact() -> None:
    contract = build_readout_diagnostics_sensitivity_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "readout_diagnostics_sensitivity_contract_defined_no_diagnostic_or_sensitivity_execution"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["diagnostics_sensitivity_contract_defined"] is True
    assert summary["diagnostic_check_executed"] is False
    assert summary["sensitivity_check_executed"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
