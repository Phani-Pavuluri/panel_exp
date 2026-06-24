"""Tests for METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_gap_coverage_literature_alignment_audit_001 import (
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_DESIGN_FAMILIES,
    REQUIRED_ESTIMATOR_FAMILIES,
    REQUIRED_INFERENCE_FAMILIES,
    REQUIRED_LITERATURE_BUCKETS,
    REQUIRED_OBSERVED_DATA_CONDITIONS,
    REQUIRED_SIMULATION_DGPS,
    CoverageStatus,
    MethodAction,
    _AUTH_FLAGS,
    build_method_gap_coverage_rows,
    build_scenarios,
    filter_gap_coverage_rows,
    run_validation,
    summarize_method_gap_coverage,
    validate_method_gap_coverage,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_REPORT.md"


def test_rows_build_and_minimum_count() -> None:
    rows = build_method_gap_coverage_rows()
    assert len(rows) >= 60
    assert len({row.row_id for row in rows}) == len(rows)


def test_required_dimensions_covered() -> None:
    rows = build_method_gap_coverage_rows()
    validation = validate_method_gap_coverage(rows)
    assert validation["valid"]
    assert validation["required_designs_covered"]
    assert validation["required_estimators_covered"]
    assert validation["required_inference_families_covered"]
    assert validation["required_observed_data_conditions_covered"]
    assert validation["required_simulation_dgps_covered"]
    assert validation["required_literature_buckets_covered"]


def test_required_sets_match_row_items() -> None:
    rows = build_method_gap_coverage_rows()
    assert {r.item for r in rows if r.dimension == "design_family"} == REQUIRED_DESIGN_FAMILIES
    assert {r.item for r in rows if r.dimension == "estimator_family"} == REQUIRED_ESTIMATOR_FAMILIES
    assert {r.item for r in rows if r.dimension == "inference_family"} == REQUIRED_INFERENCE_FAMILIES
    assert {r.item for r in rows if r.dimension == "observed_data_condition"} == REQUIRED_OBSERVED_DATA_CONDITIONS
    assert {r.item for r in rows if r.dimension == "simulation_dgp_condition"} == REQUIRED_SIMULATION_DGPS
    assert {r.item for r in rows if r.dimension == "literature_alignment_bucket"} == REQUIRED_LITERATURE_BUCKETS


def test_summary_flags_and_counts() -> None:
    rows = build_method_gap_coverage_rows()
    summary = summarize_method_gap_coverage(rows)
    assert summary["suitability_matrix_sufficient_alone"] is False
    assert summary["observed_panel_diagnostics_required"] is True
    assert summary["simulation_dgp_coverage_plan_required"] is True
    assert summary["failure_mode_registry_required"] is True
    assert summary["literature_alignment_required_before_promotion"] is True
    assert summary["new_method_scouts_required"] is True
    assert summary["downstream_work_paused"] is True
    assert summary["coverage_status_counts"]
    assert summary["recommended_action_counts"]
    assert summary["dimension_counts"]


def test_recommended_next_artifacts_order() -> None:
    rows = build_method_gap_coverage_rows()
    summary = summarize_method_gap_coverage(rows)
    assert summary["recommended_next_artifacts"][:3] == list(RECOMMENDED_NEXT_ARTIFACTS[:3])


def test_no_downstream_authorization() -> None:
    rows = build_method_gap_coverage_rows()
    summary = summarize_method_gap_coverage(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_method_gap_coverage_rows()
    design = filter_gap_coverage_rows(rows, dimension="design_family")
    assert len(design) == len(REQUIRED_DESIGN_FAMILIES)
    blocked = filter_gap_coverage_rows(rows, status=CoverageStatus.BLOCKED)
    assert blocked
    repair = filter_gap_coverage_rows(rows, action=MethodAction.REPAIR)
    assert repair


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001"
    assert data["failed_scenarios"] == []
    assert data["row_count"] >= 60
