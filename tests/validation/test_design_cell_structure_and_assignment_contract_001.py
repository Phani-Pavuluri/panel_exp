"""Tests for DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_cell_structure_and_assignment_contract_001 import (
    ASSIGNMENT_CONSTRAINT_CATEGORIES,
    DEPENDS_ON,
    FUTURE_ASSIGNMENT_STATUSES,
    FUTURE_CELL_ROLES,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_DESIGN_STRUCTURE_TYPES,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_MANIPULATION_POLICIES,
    FUTURE_OUTPUT_CONCEPTS,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    ALTERNATIVE_NEXT_ARTIFACT,
    _AUTH_FLAGS,
    build_design_cell_structure_assignment_contract,
    build_scenarios,
    run_validation,
    validate_design_cell_structure_assignment_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001_REPORT.md"


def test_assignment_statuses_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.future_assignment_statuses == FUTURE_ASSIGNMENT_STATUSES
    assert "DESIGN_ASSIGNMENT_READY_FOR_RUNTIME" in contract.future_assignment_statuses
    assert "DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW" in contract.future_assignment_statuses


def test_design_structure_types_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.future_design_structure_types == FUTURE_DESIGN_STRUCTURE_TYPES
    assert "SINGLE_TREATMENT_CONTROL" in contract.future_design_structure_types
    assert "BUDGET_REALLOCATION" in contract.future_design_structure_types


def test_cell_roles_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.future_cell_roles == FUTURE_CELL_ROLES
    assert "BUSINESS_AS_USUAL_CONTROL" in contract.future_cell_roles
    assert "LOW_DOSAGE" in contract.future_cell_roles


def test_manipulation_policies_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "GO_DARK" in FUTURE_MANIPULATION_POLICIES
    assert "HEAVY_UP" in FUTURE_MANIPULATION_POLICIES
    assert "DIFFERENCE_IN_POLICY" in FUTURE_MANIPULATION_POLICIES


def test_readiness_gates_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert "power_mde_readiness_gate" in contract.readiness_gates
    assert "assignment_constraint_gate" in contract.readiness_gates


def test_assignment_boundary_and_semantics() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.design_cell_structure_contract_defined
    assert contract.assignment_boundary_defined
    assert contract.cell_role_semantics_defined
    assert contract.manipulation_policy_semantics_defined
    assert contract.assignment_constraint_categories_defined


def test_design_structure_treatments() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.standard_go_dark_structure_defined
    assert contract.heavy_up_structure_defined
    assert contract.go_live_structure_defined
    assert contract.budget_reallocation_structure_defined
    assert contract.dosage_design_structure_defined
    assert contract.difference_in_policy_structure_defined
    assert contract.business_as_usual_control_required_for_standard_go_dark


def test_control_contamination_and_method_review() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.control_contamination_preservation_defined
    assert contract.method_suitability_review_required_for_dosage


def test_constraint_categories() -> None:
    assert len(ASSIGNMENT_CONSTRAINT_CATEGORIES) >= 14
    assert "BUSINESS_AS_USUAL_CONTROL_CONSTRAINT" in ASSIGNMENT_CONSTRAINT_CATEGORIES
    assert "BUDGET_REALLOCATION_MAPPING_CONSTRAINT" in ASSIGNMENT_CONSTRAINT_CATEGORIES


def test_future_contract_and_output_concepts() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert contract.future_output_concepts == FUTURE_OUTPUT_CONCEPTS
    assert "DesignCellSpec" in contract.future_contract_concepts
    assert "DesignClaimBoundaryReport" in contract.future_output_concepts


def test_depends_on_power_mde_runtime() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "POWER_MDE_DIAGNOSTICS_RUNTIME_001" in contract.depends_on
    assert contract.depends_on == DEPENDS_ON


def test_all_authorization_flags_false() -> None:
    contract = build_design_cell_structure_assignment_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_design_cell_structure_assignment_contract()
    result = validate_design_cell_structure_assignment_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_listed() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 15
    assert "assignment_ready_does_not_assign_geo_units" in FUTURE_IMPLEMENTATION_TESTS


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["design_cell_structure_contract_defined"] is True
    assert data["runtime_design_generation_implemented"] is False
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["alternative_next_artifact"] == ALTERNATIVE_NEXT_ARTIFACT
    assert data["final_verdict"] == (
        "design_cell_structure_and_assignment_contract_defined_no_runtime_assignment_or_production_authorization"
    )


def test_report_covers_assignment_boundary() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "DESIGN_ASSIGNMENT_READY_FOR_RUNTIME" in text
    assert "does not mean" in text.lower() or "not powered" in text.lower()
    assert "standard go-dark" in text.lower()
    assert "dosage" in text.lower()
    assert "budget reallocation" in text.lower()
