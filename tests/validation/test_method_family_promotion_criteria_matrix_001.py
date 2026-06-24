"""Tests for METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_family_promotion_criteria_matrix_001 import (
    MIN_CRITERIA_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_CRITERIA_DIMENSIONS,
    REQUIRED_METHOD_FAMILIES,
    REQUIRED_STATUSES,
    CriteriaDimension,
    CriteriaStatus,
    MethodFamily,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_method_family_promotion_criteria_matrix,
    build_scenarios,
    filter_method_family_promotion_criteria_matrix,
    run_validation,
    summarize_method_family_promotion_criteria_matrix,
    validate_method_family_promotion_criteria_matrix,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_REPORT.md"


def test_criteria_rows_build_and_minimum_count() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    assert len(rows) >= MIN_CRITERIA_ROW_COUNT
    assert len({r.criteria_id for r in rows}) == len(rows)


def test_all_families_dimensions_and_statuses_represented() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    validation = validate_method_family_promotion_criteria_matrix(rows)
    assert validation["valid"]
    assert validation["all_required_method_families_covered"]
    assert validation["all_required_criteria_dimensions_covered"]
    assert validation["all_statuses_represented"]
    assert validation["retire_or_replace_criteria_defined"]


def test_summary_flags() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    summary = summarize_method_family_promotion_criteria_matrix(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] is expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "method_family_promotion_criteria_matrix_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    summary = summarize_method_family_promotion_criteria_matrix(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    scm = filter_method_family_promotion_criteria_matrix(rows, method_family=MethodFamily.SCM)
    assert scm
    gated = filter_method_family_promotion_criteria_matrix(
        rows, current_status=CriteriaStatus.PRODUCTION_CANDIDATE_GATED
    )
    assert gated
    retire = filter_method_family_promotion_criteria_matrix(rows, has_retirement_criteria=True)
    assert retire
    diag = filter_method_family_promotion_criteria_matrix(
        rows, criteria_dimension=CriteriaDimension.OBSERVED_PANEL_DIAGNOSTICS
    )
    assert diag


def test_required_fields_nonempty() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    for row in rows:
        assert row.required_conditions
        assert row.required_artifacts
        assert row.blocking_failure_modes
        assert row.promotion_evidence_required
        assert row.forbidden_current_use
        assert row.downstream_authorization_status == "paused"


def test_summary_count_consistency() -> None:
    rows = build_method_family_promotion_criteria_matrix()
    summary = summarize_method_family_promotion_criteria_matrix(rows)
    validation = validate_method_family_promotion_criteria_matrix(rows)
    assert summary["criteria_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["method_family_counts"] == validation["method_family_counts"]
    assert summary["criteria_dimension_counts"] == validation["criteria_dimension_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
    assert data["failed_scenarios"] == []
    assert data["criteria_row_count"] >= MIN_CRITERIA_ROW_COUNT
    assert data["all_required_method_families_covered"] is True
    assert data["all_required_criteria_dimensions_covered"] is True
    for family in REQUIRED_METHOD_FAMILIES:
        assert data["method_family_counts"].get(family.value, 0) > 0
    for dimension in REQUIRED_CRITERIA_DIMENSIONS:
        assert data["criteria_dimension_counts"].get(dimension.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
