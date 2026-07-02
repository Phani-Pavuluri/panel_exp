"""Tests for DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_assignment_runtime_contract_001 import (
    ASSIGNMENT_ALGORITHM_CATEGORIES,
    ASSIGNMENT_CANDIDATE_FIELDS,
    ASSIGNMENT_PLAN_FIELDS,
    CONTRACT_EXAMPLES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    FUTURE_ASSIGNMENT_CANDIDATE_STATUSES,
    FUTURE_ASSIGNMENT_RUNTIME_STATUSES,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONCEPTS,
    INPUT_DEPENDENCIES,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    ALTERNATIVE_NEXT_ARTIFACT,
    RETRY_CATEGORIES,
    UNIT_ALLOCATION_FIELDS,
    _AUTH_FLAGS,
    build_design_assignment_runtime_contract,
    build_scenarios,
    run_validation,
    validate_design_assignment_runtime_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001_REPORT.md"


def test_assignment_runtime_statuses_defined() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.future_assignment_runtime_statuses == FUTURE_ASSIGNMENT_RUNTIME_STATUSES
    assert "ASSIGNMENT_RUNTIME_READY_TO_GENERATE" in contract.future_assignment_runtime_statuses
    assert "ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY" in contract.future_assignment_runtime_statuses


def test_assignment_candidate_statuses_defined() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.future_assignment_candidate_statuses == FUTURE_ASSIGNMENT_CANDIDATE_STATUSES
    assert "ASSIGNMENT_CANDIDATE_NOT_GENERATED" in contract.future_assignment_candidate_statuses


def test_algorithm_categories_include_common_and_split() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.assignment_algorithm_categories == ASSIGNMENT_ALGORITHM_CATEGORIES
    assert "COMMON_CONTROL_ASSIGNMENT" in contract.assignment_algorithm_categories
    assert "SPLIT_CONTROL_ASSIGNMENT" in contract.assignment_algorithm_categories
    assert "RERANDOMIZED_ASSIGNMENT" in contract.assignment_algorithm_categories


def test_assignment_plan_and_candidate_fields() -> None:
    contract = build_design_assignment_runtime_contract()
    assert "selected_candidate_id" in contract.assignment_plan_fields
    assert "reproducibility_manifest" in contract.assignment_plan_fields
    assert "artifact_registry_entry" in contract.assignment_candidate_fields
    assert "audit_trace" in contract.unit_allocation_fields


def test_contract_semantics() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.design_assignment_runtime_contract_defined
    assert contract.assignment_plan_contract_defined
    assert contract.reproducibility_manifest_contract_defined
    assert contract.assignment_failure_packet_contract_defined
    assert CONTRACT_POSITIVE_FLAGS["claim_boundaries_defined"]


def test_readiness_gates_count() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 14
    assert "method_suitability_gate" in contract.readiness_gates
    assert "reproducibility_config_gate" in contract.readiness_gates


def test_input_dependencies_include_method_suitability() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.input_dependencies == INPUT_DEPENDENCIES
    assert "method_suitability_report" in contract.input_dependencies
    assert "method_instrument_suitability_matrix" in contract.input_dependencies


def test_retry_categories_defined() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "RERUN_METHOD_SUITABILITY" in contract.retry_categories


def test_authorization_flags_all_false() -> None:
    contract = build_design_assignment_runtime_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["runtime_assignment_generation_implemented"]
    assert not contract.authorization_flags["assignment_candidate_selected"]


def test_contract_validation_passes() -> None:
    contract = build_design_assignment_runtime_contract()
    result = validate_design_assignment_runtime_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_future_contract_and_output_concepts() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert contract.future_output_concepts == FUTURE_OUTPUT_CONCEPTS
    assert "AssignmentReproducibilityManifest" in contract.future_contract_concepts
    assert "AssignmentFailurePacket" in contract.future_output_concepts


def test_contract_examples_count() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.contract_examples == CONTRACT_EXAMPLES
    assert len(contract.contract_examples) == 8


def test_future_implementation_tests_documented() -> None:
    contract = build_design_assignment_runtime_contract()
    scenarios = build_scenarios()
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_depends_on_includes_method_suitability_runtime() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "METHOD_SUITABILITY_RUNTIME_001" in contract.depends_on


def test_recommended_next_artifact() -> None:
    contract = build_design_assignment_runtime_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "DESIGN_ASSIGNMENT_RUNTIME_001"


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "design_assignment_runtime_contract_defined_no_assignment_generation_or_randomization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["design_assignment_runtime_contract_defined"] is True
    assert summary["runtime_assignment_generation_implemented"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "design_assignment_runtime_contract_defined_no_assignment_generation_or_randomization" in text
    assert "Reproducibility requirements" in text
