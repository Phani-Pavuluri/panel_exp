"""Tests for DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.data_driven_design_estimator_inference_selection_gate_requirements_001 import (
    MIN_REQUIREMENTS_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_DECISION_TARGETS,
    REQUIRED_ROUTING_EXAMPLE_IDS,
    REQUIRED_ROUTE_STATUSES,
    REQUIRED_SELECTION_LAYERS,
    DecisionTarget,
    RouteStatus,
    SelectionLayer,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_data_driven_design_estimator_inference_selection_gate_requirements,
    build_scenarios,
    filter_data_driven_design_estimator_inference_selection_gate_requirements,
    run_validation,
    summarize_data_driven_design_estimator_inference_selection_gate_requirements,
    validate_data_driven_design_estimator_inference_selection_gate_requirements,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_summary.json"
)
_REPORT = (
    _REPO
    / "docs/track_d/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_REPORT.md"
)


def test_requirements_rows_build_and_minimum_count() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    assert len(rows) >= MIN_REQUIREMENTS_ROW_COUNT
    assert len({r.requirement_id for r in rows}) == len(rows)


def test_all_layers_targets_statuses_and_examples_covered() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    validation = validate_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    assert validation["valid"]
    assert validation["all_required_selection_layers_covered"]
    assert validation["all_required_decision_targets_covered"]
    assert validation["all_required_route_statuses_covered"]
    assert validation["all_required_routing_examples_covered"]


def test_summary_flags() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    summary = summarize_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "data_driven_selection_gate_requirements_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    summary = summarize_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    design = filter_data_driven_design_estimator_inference_selection_gate_requirements(
        rows, selection_layer=SelectionLayer.DESIGN_ELIGIBILITY
    )
    assert design
    blocked = filter_data_driven_design_estimator_inference_selection_gate_requirements(
        rows, route_status=RouteStatus.BLOCKED
    )
    assert blocked
    examples = filter_data_driven_design_estimator_inference_selection_gate_requirements(
        rows, routing_example=True
    )
    assert len(examples) == len(REQUIRED_ROUTING_EXAMPLE_IDS)
    inference = filter_data_driven_design_estimator_inference_selection_gate_requirements(
        rows, decision_target=DecisionTarget.INFERENCE
    )
    assert inference


def test_required_fields_nonempty() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    for row in rows:
        assert row.required_prior_artifacts
        assert row.authorization_boundary
        assert row.eligible_when
        assert row.blocked_when


def test_summary_count_consistency() -> None:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    summary = summarize_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    validation = validate_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    assert summary["requirements_row_count"] == len(rows)
    assert summary["selection_layer_counts"] == validation["selection_layer_counts"]
    assert summary["decision_target_counts"] == validation["decision_target_counts"]
    assert summary["route_status_counts"] == validation["route_status_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
    assert data["failed_scenarios"] == []
    assert data["requirements_row_count"] >= MIN_REQUIREMENTS_ROW_COUNT
    assert data["all_required_selection_layers_covered"] is True
    assert data["all_required_routing_examples_covered"] is True
    for layer in REQUIRED_SELECTION_LAYERS:
        assert data["selection_layer_counts"].get(layer.value, 0) > 0
    for target in REQUIRED_DECISION_TARGETS:
        assert data["decision_target_counts"].get(target.value, 0) > 0
    for status in REQUIRED_ROUTE_STATUSES:
        assert data["route_status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not implement the production selector" in text
    assert "does not authorize production routing" in text
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "TrustReport" in text
