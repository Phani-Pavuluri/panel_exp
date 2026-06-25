"""Tests for DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.data_driven_selection_gate_implementation_plan_001 import (
    INPUT_CONTRACT,
    INPUT_FIELDS,
    MIN_PLAN_ROW_COUNT,
    OUTPUT_CONTRACT,
    OUTPUT_FIELDS,
    RECOMMENDED_NEXT_ARTIFACTS,
    RULE_ORDERING,
    STAGES,
    MethodFamily,
    PlanSection,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_data_driven_selection_gate_implementation_plan,
    build_scenarios,
    filter_data_driven_selection_gate_implementation_plan,
    run_validation,
    summarize_data_driven_selection_gate_implementation_plan,
    validate_data_driven_selection_gate_implementation_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_REPORT.md"


def test_plan_rows_build_and_minimum_count() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    assert len(rows) >= MIN_PLAN_ROW_COUNT
    assert len({r.plan_id for r in rows}) == len(rows)


def test_all_sections_families_layers_and_stages_represented() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    validation = validate_data_driven_selection_gate_implementation_plan(rows)
    assert validation["valid"]
    assert validation["all_required_plan_sections_covered"]
    assert validation["all_method_families_routed"]
    assert validation["all_rule_layers_present"]
    assert validation["all_stages_present"]


def test_summary_flags() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    summary = summarize_data_driven_selection_gate_implementation_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    assert summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["final_verdict"] == (
        "data_driven_selection_gate_implementation_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    summary = summarize_data_driven_selection_gate_implementation_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    for flag in summary["authorization_flags"].values():
        assert flag is False


def test_contract_fields_defined() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    input_rows = filter_data_driven_selection_gate_implementation_plan(
        rows, plan_section=PlanSection.INPUT_CONTRACT
    )
    output_rows = filter_data_driven_selection_gate_implementation_plan(
        rows, plan_section=PlanSection.OUTPUT_CONTRACT
    )
    assert {r.field_or_component for r in input_rows} == set(INPUT_FIELDS)
    assert {r.field_or_component for r in output_rows} == set(OUTPUT_FIELDS)
    summary = summarize_data_driven_selection_gate_implementation_plan(rows)
    assert summary["planned_input_contract"] == INPUT_CONTRACT
    assert summary["planned_output_contract"] == OUTPUT_CONTRACT


def test_filter_helpers() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    scm = filter_data_driven_selection_gate_implementation_plan(
        rows, method_family=MethodFamily.SCM
    )
    assert scm
    rule = filter_data_driven_selection_gate_implementation_plan(
        rows, plan_section=PlanSection.RULE_ORDERING
    )
    assert len(rule) == len(RULE_ORDERING)
    stage = filter_data_driven_selection_gate_implementation_plan(
        rows, implementation_stage=STAGES[0]
    )
    assert stage


def test_required_fields_nonempty() -> None:
    rows = build_data_driven_selection_gate_implementation_plan()
    for row in rows:
        assert row.purpose
        assert row.authorization_boundary
        assert row.required_prior_artifacts


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == (
        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
    )
    assert data["failed_scenarios"] == []
    assert data["plan_row_count"] >= MIN_PLAN_ROW_COUNT
    assert data["planned_input_contract"] == INPUT_CONTRACT
    assert data["planned_output_contract"] == OUTPUT_CONTRACT
    assert data["rule_ordering"] == list(RULE_ORDERING)
    assert data["stages"] == list(STAGES)
    assert data["selector_implementation_authorized"] is False
    assert data["production_selection_router_authorized"] is False
    assert data["package_side_agents_authorized"] is False


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "implementation plan only" in text.lower()
    assert "no runtime selector" in text.lower() or "no runtime selector/router" in text.lower()
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "release gate remains required" in text.lower()
    assert "resolved planning artifacts do not imply production readiness" in text.lower()
