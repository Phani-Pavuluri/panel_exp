"""Tests for ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.estimator_inference_execution_contract_001 import (
    ALTERNATIVE_NEXT_ARTIFACT,
    CONTRACT_EXAMPLES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    EFFECT_ESTIMATE_REPORT_FIELDS,
    EXECUTION_ROLES,
    EXECUTION_STATUSES,
    EXECUTION_TRACE_FIELDS,
    FAILURE_PACKET_FIELDS,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    INPUT_DATA_CONTRACT_FIELDS,
    INPUT_DEPENDENCIES,
    INFERENCE_DIAGNOSTIC_REPORT_FIELDS,
    INSTRUMENT_EXECUTION_STATUSES,
    INSTRUMENT_SPEC_FIELDS,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    RETRY_CATEGORIES,
    UNCERTAINTY_REPORT_FIELDS,
    _AUTH_FLAGS,
    build_estimator_inference_execution_contract,
    build_scenarios,
    run_validation,
    validate_estimator_inference_execution_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001_REPORT.md"


def test_execution_statuses_defined() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.execution_statuses == EXECUTION_STATUSES
    assert "EXECUTION_READY_FOR_RUNTIME" in contract.execution_statuses
    assert "EXECUTION_BLOCKED_BY_READOUT_PLAN" in contract.execution_statuses


def test_instrument_execution_statuses_defined() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.instrument_execution_statuses == INSTRUMENT_EXECUTION_STATUSES
    assert "INSTRUMENT_EXECUTION_COMPLETED" in contract.instrument_execution_statuses
    assert "INSTRUMENT_EXECUTION_NOT_RUN" in contract.instrument_execution_statuses


def test_execution_roles_defined() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.execution_roles == EXECUTION_ROLES
    assert "PRIMARY_EXECUTION_CANDIDATE" in contract.execution_roles
    assert "BLOCKED_EXECUTION_CANDIDATE" in contract.execution_roles


def test_instrument_spec_fields() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.instrument_spec_fields == INSTRUMENT_SPEC_FIELDS
    assert "uncertainty_semantics" in contract.instrument_spec_fields
    assert "governance_restrictions" in contract.instrument_spec_fields


def test_input_data_contract_fields() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.input_data_contract_fields == INPUT_DATA_CONTRACT_FIELDS
    assert "data_hash" in contract.input_data_contract_fields
    assert "panel_data_reference" in contract.input_data_contract_fields


def test_readiness_gates_order() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 11
    assert contract.readiness_gates[0] == "readout_plan_gate"
    assert contract.readiness_gates[-1] == "execution_packet_gate"


def test_future_output_schemas() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.effect_estimate_report_fields == EFFECT_ESTIMATE_REPORT_FIELDS
    assert contract.uncertainty_report_fields == UNCERTAINTY_REPORT_FIELDS
    assert contract.inference_diagnostic_report_fields == INFERENCE_DIAGNOSTIC_REPORT_FIELDS
    assert contract.execution_trace_fields == EXECUTION_TRACE_FIELDS
    assert contract.failure_packet_fields == FAILURE_PACKET_FIELDS


def test_contract_semantics() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.estimator_inference_execution_contract_defined
    assert contract.execution_input_contract_defined
    assert contract.instrument_execution_request_contract_defined
    assert CONTRACT_POSITIVE_FLAGS["claim_boundaries_defined"]


def test_authorization_flags_all_false() -> None:
    contract = build_estimator_inference_execution_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["estimator_inference_execution_runtime_implemented"]
    assert not contract.authorization_flags["instrument_execution_completed"]
    assert not contract.authorization_flags["causal_claim_authorized"]
    assert not contract.authorization_flags["production_readout_authorized"]


def test_contract_validation_passes() -> None:
    contract = build_estimator_inference_execution_contract()
    result = validate_estimator_inference_execution_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_future_contract_concepts() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert "EstimatorInferenceExecutionPacket" in contract.future_contract_concepts
    assert "ExecutionFailurePacket" in contract.future_contract_concepts


def test_contract_examples_count() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.contract_examples == CONTRACT_EXAMPLES
    assert len(contract.contract_examples) == 10


def test_retry_categories() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "FIX_INPUT_DATA_CONTRACT" in contract.retry_categories


def test_future_implementation_tests_documented() -> None:
    scenarios = build_scenarios()
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_depends_on_includes_readout_plan_runtime() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "READOUT_PLAN_RUNTIME_001" in contract.depends_on
    assert "DESIGN_ASSIGNMENT_RUNTIME_001" in contract.depends_on


def test_input_dependencies_include_readout_plan() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.input_dependencies == INPUT_DEPENDENCIES
    assert "readout_plan_packet" in contract.input_dependencies
    assert "execution_input_data_contract" in contract.input_dependencies


def test_recommended_next_artifact() -> None:
    contract = build_estimator_inference_execution_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001"


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "estimator_inference_execution_contract_defined_no_estimator_or_inference_execution"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["estimator_inference_execution_contract_defined"] is True
    assert summary["estimator_inference_execution_runtime_implemented"] is False
    assert summary["instrument_execution_completed"] is False
    assert summary["production_readout_authorized"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert (
        "estimator_inference_execution_contract_defined_no_estimator_or_inference_execution" in text
    )
    assert "Planned role treatment" in text
    assert "Instrument family treatment" in text
