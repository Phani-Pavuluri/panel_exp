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
    FUTURE_CONTRAST_SPECIFIC_ROLES,
    FUTURE_CONTRAST_TYPES,
    FUTURE_DESIGN_STRUCTURE_TYPES,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_MANIPULATION_POLICIES,
    FUTURE_OUTPUT_CONCEPTS,
    FUTURE_SCENARIO_STATUSES,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    ALTERNATIVE_NEXT_ARTIFACT,
    SCENARIO_RESOLUTION_OPTIONS,
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


def test_assignment_and_scenario_statuses_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.future_assignment_statuses == FUTURE_ASSIGNMENT_STATUSES
    assert contract.future_scenario_statuses == FUTURE_SCENARIO_STATUSES
    assert "DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT" in contract.future_assignment_statuses
    assert "DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK" in contract.future_assignment_statuses
    assert "SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT" in contract.future_scenario_statuses


def test_contrast_types_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.future_contrast_types == FUTURE_CONTRAST_TYPES
    assert "GO_DARK_VS_BAU" in contract.future_contrast_types
    assert "MULTI_CELL_COMMON_CONTROL_CONTRAST" in contract.future_contrast_types


def test_design_structure_types_include_split_control() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "MULTI_CELL_SPLIT_CONTROL" in contract.future_design_structure_types


def test_cell_and_contrast_roles_defined() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "COMMON_REFERENCE_CELL" in contract.future_cell_roles
    assert contract.future_contrast_specific_roles == FUTURE_CONTRAST_SPECIFIC_ROLES
    assert "BAU_CONTROL_FOR_CONTRAST" in contract.future_contrast_specific_roles
    assert "LOW_POLICY_ANCHOR_FOR_CONTRAST" in contract.future_contrast_specific_roles


def test_scenario_planner_contract_semantics() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.contrast_structure_contract_defined
    assert contract.scenario_policy_plan_contract_defined
    assert contract.shared_control_dependency_contract_defined
    assert contract.cross_contrast_conflict_contract_defined
    assert contract.scenario_resolution_contract_defined
    assert contract.contrast_specific_role_semantics_defined
    assert contract.four_cell_common_control_scenario_documented
    assert contract.split_common_control_redesign_recheck_defined


def test_readiness_gates_include_scenario_gates() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "contrast_structure_gate" in contract.readiness_gates
    assert "scenario_policy_plan_gate" in contract.readiness_gates
    assert "shared_control_dependency_gate" in contract.readiness_gates
    assert len(contract.readiness_gates) == 13


def test_constraint_categories_include_scenario_constraints() -> None:
    assert "SHARED_CONTROL_DEPENDENCY_CONSTRAINT" in ASSIGNMENT_CONSTRAINT_CATEGORIES
    assert "SCENARIO_POLICY_COMPATIBILITY_CONSTRAINT" in ASSIGNMENT_CONSTRAINT_CATEGORIES
    assert "REDESIGN_RECHECK_CONSTRAINT" in ASSIGNMENT_CONSTRAINT_CATEGORIES
    assert "split_common_control" in SCENARIO_RESOLUTION_OPTIONS


def test_future_contract_concepts_include_scenario_types() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "DesignContrastSpec" in contract.future_contract_concepts
    assert "DesignScenarioSpec" in contract.future_contract_concepts
    assert "CrossContrastConflict" in contract.future_contract_concepts
    assert "SharedControlDependency" in contract.future_contract_concepts
    assert "CrossContrastConflictReport" in contract.future_output_concepts
    assert "ScenarioResolutionReport" in contract.future_output_concepts


def test_assignment_boundary_and_treatments() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.design_cell_structure_contract_defined
    assert contract.assignment_boundary_defined
    assert contract.standard_go_dark_structure_defined
    assert contract.business_as_usual_control_required_for_standard_go_dark


def test_depends_on_power_mde_runtime() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert "POWER_MDE_DIAGNOSTICS_RUNTIME_001" in contract.depends_on
    assert contract.depends_on == DEPENDS_ON


def test_all_authorization_flags_false() -> None:
    contract = build_design_cell_structure_assignment_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["runtime_scenario_planner_implemented"]


def test_validate_contract() -> None:
    contract = build_design_cell_structure_assignment_contract()
    result = validate_design_cell_structure_assignment_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_include_scenario_planner_cases() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 22
    assert "missing_contrast_specs_blocks_scenario_feasibility" in FUTURE_IMPLEMENTATION_TESTS
    assert "split_common_control_emits_redesign_recheck_requirement" in FUTURE_IMPLEMENTATION_TESTS
    assert "raising_common_control_helps_go_dark_weakens_heavy_up" in FUTURE_IMPLEMENTATION_TESTS


def test_recommended_next_artifact() -> None:
    contract = build_design_cell_structure_assignment_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001"
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["contrast_structure_contract_defined"] is True
    assert data["scenario_policy_plan_contract_defined"] is True
    assert data["four_cell_common_control_scenario_documented"] is True
    assert data["runtime_scenario_planner_implemented"] is False
    assert data["final_verdict"] == (
        "design_cell_contrast_and_scenario_contract_defined_no_runtime_assignment_or_scenario_optimization"
    )


def test_report_covers_scenario_planner() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "Scenario A" in text
    assert "Scenario E" in text
    assert "cross-contrast" in text.lower() or "CrossContrastConflict" in text
    assert "split common control" in text.lower()
    assert "contrast-specific" in text.lower()
