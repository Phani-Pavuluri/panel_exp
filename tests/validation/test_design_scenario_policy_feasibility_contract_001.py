"""Tests for DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_scenario_policy_feasibility_contract_001 import (
    DEPENDS_ON,
    FUTURE_CONTRAST_STATUSES,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONCEPTS,
    FUTURE_POLICY_SUPPORT_STATUSES,
    FUTURE_SCENARIO_STATUSES,
    FUTURE_SHARED_CONTROL_CONFLICT_TYPES,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    ALTERNATIVE_NEXT_ARTIFACT,
    REPORT_FIELDS,
    RESOLUTION_OPTION_TYPES,
    _AUTH_FLAGS,
    build_design_scenario_policy_feasibility_contract,
    build_scenarios,
    run_validation,
    validate_design_scenario_policy_feasibility_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001_REPORT.md"


def test_scenario_and_contrast_statuses_defined() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.future_scenario_statuses == FUTURE_SCENARIO_STATUSES
    assert contract.future_contrast_statuses == FUTURE_CONTRAST_STATUSES
    assert "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE" in contract.future_scenario_statuses
    assert "CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL" in contract.future_contrast_statuses


def test_policy_support_and_conflict_types_defined() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.future_policy_support_statuses == FUTURE_POLICY_SUPPORT_STATUSES
    assert contract.future_shared_control_conflict_types == FUTURE_SHARED_CONTROL_CONFLICT_TYPES
    assert "POLICY_OUT_OF_HISTORICAL_SUPPORT" in contract.future_policy_support_statuses
    assert "COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER" in (
        contract.future_shared_control_conflict_types
    )


def test_resolution_option_types_defined() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.resolution_option_types == RESOLUTION_OPTION_TYPES
    assert "SPLIT_COMMON_CONTROL" in contract.resolution_option_types
    assert "REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY" in contract.resolution_option_types


def test_scenario_policy_feasibility_contract_semantics() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.scenario_policy_feasibility_contract_defined
    assert contract.required_vs_achieved_spend_contrast_defined
    assert contract.historical_support_contract_defined
    assert contract.shared_control_conflict_contract_defined
    assert contract.split_control_redesign_recheck_defined
    assert contract.scenario_resolution_options_defined
    assert contract.four_cell_common_control_example_defined


def test_readiness_gates_count_and_order() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 13
    assert contract.readiness_gates[0] == "profiler_gate"
    assert contract.readiness_gates[-1] == "method_suitability_precheck_gate"


def test_future_contract_and_output_concepts() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert "DesignScenarioPolicyFeasibilityReport" in contract.future_contract_concepts
    assert "RequiredVsAchievedSpendContrastReport" in contract.future_output_concepts
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert contract.future_output_concepts == FUTURE_OUTPUT_CONCEPTS


def test_report_fields_defined() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.report_fields == REPORT_FIELDS
    assert "required_vs_achieved_spend_contrast_by_contrast" in contract.report_fields
    assert "shared_control_conflicts" in contract.report_fields


def test_depends_on_design_cell_contract() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001" in contract.depends_on
    assert contract.depends_on == DEPENDS_ON


def test_all_authorization_flags_false() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    result = validate_design_scenario_policy_feasibility_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_include_scenario_policy_cases() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 18
    assert "raising_common_control_helps_go_dark_weakens_heavy_up" in FUTURE_IMPLEMENTATION_TESTS
    assert "split_common_control_emits_redesign_recheck_requirement" in FUTURE_IMPLEMENTATION_TESTS
    assert "achieved_spend_below_required_marks_contrast_insufficient" in FUTURE_IMPLEMENTATION_TESTS


def test_recommended_next_artifact() -> None:
    contract = build_design_scenario_policy_feasibility_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["scenario_policy_feasibility_contract_defined"] is True
    assert data["four_cell_common_control_example_defined"] is True
    assert data["runtime_scenario_feasibility_implemented"] is False
    assert data["final_verdict"] == (
        "design_scenario_policy_feasibility_contract_defined_no_runtime_scenario_planner_or_optimization"
    )


def test_report_covers_four_cell_example() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "Scenario A" in text
    assert "Scenario E" in text
    assert "CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL" in text
    assert "split common control" in text.lower() or "SPLIT_COMMON_CONTROL" in text
    assert "required vs achieved" in text.lower() or "Required vs achieved" in text
