"""Tests for DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_assignment_feasibility_contract_001 import (
    ASSIGNMENT_CONSTRAINT_CATEGORIES,
    ASSIGNMENT_UNIT_FIELDS,
    CELL_REQUIREMENT_FIELDS,
    CONTRACT_EXAMPLES,
    DEPENDS_ON,
    FUTURE_ASSIGNMENT_CONSTRAINT_STATUSES,
    FUTURE_ASSIGNMENT_FEASIBILITY_STATUSES,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONCEPTS,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    ALTERNATIVE_NEXT_ARTIFACT,
    REPORT_FIELDS,
    _AUTH_FLAGS,
    build_design_assignment_feasibility_contract,
    build_scenarios,
    run_validation,
    validate_design_assignment_feasibility_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001_REPORT.md"


def test_assignment_feasibility_statuses_defined() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.future_assignment_feasibility_statuses == FUTURE_ASSIGNMENT_FEASIBILITY_STATUSES
    assert "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME" in contract.future_assignment_feasibility_statuses
    assert "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS" in (
        contract.future_assignment_feasibility_statuses
    )


def test_assignment_constraint_statuses_defined() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.future_assignment_constraint_statuses == FUTURE_ASSIGNMENT_CONSTRAINT_STATUSES
    assert "ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN" in contract.future_assignment_constraint_statuses


def test_constraint_categories_include_common_control_and_split() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.assignment_constraint_categories == ASSIGNMENT_CONSTRAINT_CATEGORIES
    assert "COMMON_CONTROL_CONSTRAINT" in contract.assignment_constraint_categories
    assert "SPLIT_CONTROL_REDESIGN_CONSTRAINT" in contract.assignment_constraint_categories
    assert "MATCHED_PAIR_REQUIREMENT_CONSTRAINT" in contract.assignment_constraint_categories
    assert "BALANCE_READINESS_CONSTRAINT" in contract.assignment_constraint_categories


def test_assignment_unit_and_cell_requirement_fields() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert "unit_id" in contract.assignment_unit_fields
    assert "eligible" in contract.assignment_unit_fields
    assert "minimum_units" in contract.cell_requirement_fields
    assert "requires_common_control" in contract.cell_requirement_fields


def test_contract_semantics() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.assignment_feasibility_contract_defined
    assert contract.eligible_unit_contract_defined
    assert contract.cell_capacity_contract_defined
    assert contract.common_control_assignment_boundary_defined
    assert contract.split_control_redesign_boundary_defined
    assert contract.matched_pair_block_boundary_defined
    assert contract.hierarchy_exclusion_boundary_defined
    assert contract.balance_readiness_boundary_defined
    assert contract.interference_risk_boundary_defined


def test_readiness_gates_count() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 15
    assert contract.readiness_gates[0] == "profiler_data_readiness_gate"
    assert contract.readiness_gates[-1] == "method_suitability_precheck_gate"


def test_future_contract_and_output_concepts() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert "DesignAssignmentFeasibilityReport" in contract.future_contract_concepts
    assert "AssignmentCellCapacityReport" in contract.future_output_concepts
    assert len(contract.contract_examples) == 8


def test_report_fields_defined() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.report_fields == REPORT_FIELDS
    assert "cell_capacity_reports" in contract.report_fields
    assert "method_suitability_handoff_report" in contract.report_fields


def test_depends_on_cell_structure_and_scenario_runtimes() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert "DESIGN_CELL_STRUCTURE_RUNTIME_001" in contract.depends_on
    assert "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001" in contract.depends_on
    assert contract.depends_on == DEPENDS_ON


def test_all_authorization_flags_false() -> None:
    contract = build_design_assignment_feasibility_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_design_assignment_feasibility_contract()
    result = validate_design_assignment_feasibility_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_include_assignment_cases() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 22
    assert "common_control_capacity_checked" in FUTURE_IMPLEMENTATION_TESTS
    assert "split_control_redesign_requires_recheck" in FUTURE_IMPLEMENTATION_TESTS
    assert "assignment_feasible_does_not_assign_units" in FUTURE_IMPLEMENTATION_TESTS


def test_recommended_next_artifact() -> None:
    contract = build_design_assignment_feasibility_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["assignment_feasibility_contract_defined"] is True
    assert data["runtime_assignment_feasibility_implemented"] is False
    assert data["final_verdict"] == (
        "design_assignment_feasibility_contract_defined_no_runtime_assignment_or_matching"
    )


def test_report_covers_examples_and_boundaries() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "Example 1" in text
    assert "Example 8" in text
    assert "common-control" in text.lower() or "Common-control" in text
    assert "split-control" in text.lower() or "Split control" in text
    assert "matched-pair" in text.lower() or "Matched-pair" in text
    assert "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME" in text
