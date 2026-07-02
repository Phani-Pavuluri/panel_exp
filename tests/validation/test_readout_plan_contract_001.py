"""Tests for READOUT_PLAN_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.readout_plan_contract_001 import (
    ALTERNATIVE_NEXT_ARTIFACT,
    CONTRACT_EXAMPLES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONCEPTS,
    INPUT_DEPENDENCIES,
    INSTRUMENT_PLANNING_CATEGORIES,
    READINESS_GATES,
    READOUT_PLAN_PACKET_FIELDS,
    READOUT_PLAN_STATUSES,
    READOUT_STACK_ROLES,
    RECOMMENDED_NEXT_ARTIFACT,
    _AUTH_FLAGS,
    build_readout_plan_contract,
    build_scenarios,
    run_validation,
    validate_readout_plan_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/READOUT_PLAN_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/READOUT_PLAN_CONTRACT_001_REPORT.md"


def test_readout_plan_statuses_defined() -> None:
    contract = build_readout_plan_contract()
    assert contract.readout_plan_statuses == READOUT_PLAN_STATUSES
    assert "READOUT_PLAN_READY_FOR_RUNTIME_PLANNING" in contract.readout_plan_statuses
    assert "READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE" in contract.readout_plan_statuses


def test_readout_stack_roles_defined() -> None:
    contract = build_readout_plan_contract()
    assert contract.readout_stack_roles == READOUT_STACK_ROLES
    assert "PRIMARY_READOUT_CANDIDATE" in contract.readout_stack_roles
    assert "BLOCKED_READOUT_INSTRUMENT" in contract.readout_stack_roles


def test_instrument_planning_categories_defined() -> None:
    contract = build_readout_plan_contract()
    assert contract.instrument_planning_categories == INSTRUMENT_PLANNING_CATEGORIES
    assert "PLANNING_DIAGNOSTIC_ONLY" in contract.instrument_planning_categories
    assert "PLANNING_BLOCKED" in contract.instrument_planning_categories


def test_readout_plan_packet_fields() -> None:
    contract = build_readout_plan_contract()
    assert contract.readout_plan_packet_fields == READOUT_PLAN_PACKET_FIELDS
    assert "planned_primary_candidates" in contract.readout_plan_packet_fields
    assert "claim_scope" in contract.readout_plan_packet_fields
    assert "reporting_caveats" in contract.readout_plan_packet_fields


def test_readiness_gates_order() -> None:
    contract = build_readout_plan_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 13
    assert contract.readiness_gates[0] == "readout_method_governance_gate"
    assert contract.readiness_gates[-1] == "readout_plan_packet_gate"


def test_input_dependencies_include_governance_and_assignment() -> None:
    contract = build_readout_plan_contract()
    assert contract.input_dependencies == INPUT_DEPENDENCIES
    assert "readout_method_governance_packet" in contract.input_dependencies
    assert "instrument_suitability_matrix" in contract.input_dependencies
    assert "reproducibility_manifest" in contract.input_dependencies


def test_contract_semantics() -> None:
    contract = build_readout_plan_contract()
    assert contract.readout_plan_contract_defined
    assert contract.planned_readout_stack_contract_defined
    assert contract.primary_candidate_contract_defined
    assert contract.claim_scope_contract_defined
    assert CONTRACT_POSITIVE_FLAGS["claim_boundaries_defined"]


def test_authorization_flags_all_false() -> None:
    contract = build_readout_plan_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["readout_plan_generated"]
    assert not contract.authorization_flags["estimator_execution_implemented"]
    assert not contract.authorization_flags["causal_claim_authorized"]
    assert not contract.authorization_flags["production_readout_authorized"]


def test_contract_validation_passes() -> None:
    contract = build_readout_plan_contract()
    result = validate_readout_plan_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_future_contract_and_output_concepts() -> None:
    contract = build_readout_plan_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert contract.future_output_concepts == FUTURE_OUTPUT_CONCEPTS
    assert "PlannedReadoutStack" in contract.future_contract_concepts
    assert "ReadoutPlanClaimScopeReport" in contract.future_output_concepts


def test_contract_examples_count() -> None:
    contract = build_readout_plan_contract()
    assert contract.contract_examples == CONTRACT_EXAMPLES
    assert len(contract.contract_examples) == 10


def test_future_implementation_tests_documented() -> None:
    scenarios = build_scenarios()
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_depends_on_includes_readout_method_governance() -> None:
    contract = build_readout_plan_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "READOUT_METHOD_GOVERNANCE_CONTRACT_001" in contract.depends_on
    assert "DESIGN_ASSIGNMENT_RUNTIME_001" in contract.depends_on


def test_recommended_next_artifact() -> None:
    contract = build_readout_plan_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "READOUT_PLAN_RUNTIME_001"


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "readout_plan_contract_defined_no_estimator_execution_or_claim_authorization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["readout_plan_contract_defined"] is True
    assert summary["readout_plan_generated"] is False
    assert summary["production_readout_authorized"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert (
        "readout_plan_contract_defined_no_estimator_execution_or_claim_authorization" in text
    )
    assert "Primary/sensitivity/diagnostic stack treatment" in text
