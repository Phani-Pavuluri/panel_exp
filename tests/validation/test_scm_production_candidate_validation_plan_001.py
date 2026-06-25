"""Tests for SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_validation_plan_001 import (
    MIN_VALIDATION_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_STATUSES,
    REQUIRED_VALIDATION_AREAS,
    ValidationArea,
    ValidationStatus,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_scenarios,
    build_scm_production_candidate_validation_plan,
    filter_scm_production_candidate_validation_plan,
    run_validation,
    summarize_scm_production_candidate_validation_plan,
    validate_scm_production_candidate_validation_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_summary.json"
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001_REPORT.md"


def test_validation_rows_build_and_minimum_count() -> None:
    rows = build_scm_production_candidate_validation_plan()
    assert len(rows) >= MIN_VALIDATION_ROW_COUNT
    assert len({r.validation_id for r in rows}) == len(rows)


def test_all_areas_and_statuses_represented() -> None:
    rows = build_scm_production_candidate_validation_plan()
    validation = validate_scm_production_candidate_validation_plan(rows)
    assert validation["valid"]
    assert validation["all_required_validation_areas_covered"]
    assert validation["all_statuses_represented"]


def test_summary_flags() -> None:
    rows = build_scm_production_candidate_validation_plan()
    summary = summarize_scm_production_candidate_validation_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] is expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "scm_production_candidate_validation_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_scm_production_candidate_validation_plan()
    summary = summarize_scm_production_candidate_validation_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    assert summary["scm_production_inference_authorized"] is False
    assert summary["scm_production_p_value_authorized"] is False
    assert summary["scm_causal_ci_authorized"] is False


def test_filter_helpers() -> None:
    rows = build_scm_production_candidate_validation_plan()
    donor = filter_scm_production_candidate_validation_plan(
        rows, validation_area=ValidationArea.DONOR_SUPPORT_CONVEX_HULL
    )
    assert donor
    blocked = filter_scm_production_candidate_validation_plan(
        rows, current_status=ValidationStatus.BLOCKED
    )
    assert blocked
    adapter = filter_scm_production_candidate_validation_plan(rows, requires_adapter=True)
    assert adapter
    null_cal = filter_scm_production_candidate_validation_plan(rows, requires_null_calibration=True)
    assert null_cal


def test_required_fields_nonempty() -> None:
    rows = build_scm_production_candidate_validation_plan()
    for row in rows:
        assert row.required_inputs
        assert row.required_diagnostics
        assert row.required_dgp_coverage
        assert row.required_failure_registry_checks
        assert row.passing_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_scm_production_candidate_validation_plan()
    summary = summarize_scm_production_candidate_validation_plan(rows)
    validation = validate_scm_production_candidate_validation_plan(rows)
    assert summary["validation_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["validation_area_counts"] == validation["validation_area_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["validation_row_count"] >= MIN_VALIDATION_ROW_COUNT
    assert data["all_required_validation_areas_covered"] is True
    for area in REQUIRED_VALIDATION_AREAS:
        assert data["validation_area_counts"].get(area.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
