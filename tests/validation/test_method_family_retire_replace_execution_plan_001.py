"""Tests for METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_family_retire_replace_execution_plan_001 import (
    MIN_EXECUTION_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_EXECUTION_AREAS,
    REQUIRED_EXECUTION_DECISIONS,
    REQUIRED_METHOD_FAMILIES,
    REQUIRED_STATUSES,
    ExecutionArea,
    ExecutionDecision,
    ExecutionStatus,
    MethodFamily,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_method_family_retire_replace_execution_plan,
    build_scenarios,
    filter_method_family_retire_replace_execution_plan,
    run_validation,
    summarize_method_family_retire_replace_execution_plan,
    validate_method_family_retire_replace_execution_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_REPORT.md"


def test_execution_rows_build_and_minimum_count() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    assert len(rows) >= MIN_EXECUTION_ROW_COUNT
    assert len({r.execution_id for r in rows}) == len(rows)


def test_all_families_areas_decisions_and_statuses_represented() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    validation = validate_method_family_retire_replace_execution_plan(rows)
    assert validation["valid"]
    assert validation["all_required_method_families_covered"]
    assert validation["all_required_execution_areas_covered"]
    assert validation["all_required_execution_decisions_covered"]
    assert validation["all_required_statuses_covered"]


def test_summary_flags() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    summary = summarize_method_family_retire_replace_execution_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "method_family_retire_replace_execution_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    summary = summarize_method_family_retire_replace_execution_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    scm = filter_method_family_retire_replace_execution_plan(rows, method_family=MethodFamily.SCM)
    assert scm
    retire = filter_method_family_retire_replace_execution_plan(
        rows, execution_decision=ExecutionDecision.RETIRE_OVERCLAIM_PATH
    )
    assert retire
    blocked = filter_method_family_retire_replace_execution_plan(
        rows, current_status=ExecutionStatus.BLOCKED
    )
    assert blocked
    labeling = filter_method_family_retire_replace_execution_plan(
        rows, execution_area=ExecutionArea.CODE_PATH_LABELING
    )
    assert labeling


def test_required_fields_nonempty() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    for row in rows:
        assert row.required_code_action
        assert row.required_doc_action
        assert row.required_test_action
        assert row.required_governance_action
        assert row.blocking_reason
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_method_family_retire_replace_execution_plan()
    summary = summarize_method_family_retire_replace_execution_plan(rows)
    validation = validate_method_family_retire_replace_execution_plan(rows)
    assert summary["execution_row_count"] == len(rows)
    assert summary["method_family_counts"] == validation["method_family_counts"]
    assert summary["execution_area_counts"] == validation["execution_area_counts"]
    assert summary["execution_decision_counts"] == validation["execution_decision_counts"]
    assert summary["status_counts"] == validation["status_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["execution_row_count"] >= MIN_EXECUTION_ROW_COUNT
    assert data["all_required_method_families_covered"] is True
    for family in REQUIRED_METHOD_FAMILIES:
        assert data["method_family_counts"].get(family.value, 0) > 0
    for area in REQUIRED_EXECUTION_AREAS:
        assert data["execution_area_counts"].get(area.value, 0) > 0
    for decision in REQUIRED_EXECUTION_DECISIONS:
        assert data["execution_decision_counts"].get(decision.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not delete code" in text
    assert "does not implement replacements" in text
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
