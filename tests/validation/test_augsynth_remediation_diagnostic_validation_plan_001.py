"""Tests for AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.augsynth_remediation_diagnostic_validation_plan_001 import (
    MIN_VALIDATION_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_REMEDIATION_TYPES,
    REQUIRED_STATUSES,
    REQUIRED_VALIDATION_AREAS,
    RemediationType,
    ValidationArea,
    ValidationStatus,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_augsynth_remediation_diagnostic_validation_plan,
    build_scenarios,
    filter_augsynth_remediation_diagnostic_validation_plan,
    run_validation,
    summarize_augsynth_remediation_diagnostic_validation_plan,
    validate_augsynth_remediation_diagnostic_validation_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001_REPORT.md"


def test_validation_rows_build_and_minimum_count() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    assert len(rows) >= MIN_VALIDATION_ROW_COUNT
    assert len({r.validation_id for r in rows}) == len(rows)


def test_all_areas_statuses_and_remediation_types_represented() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    validation = validate_augsynth_remediation_diagnostic_validation_plan(rows)
    assert validation["valid"]
    assert validation["all_required_validation_areas_covered"]
    assert validation["all_required_statuses_covered"]
    assert validation["all_required_remediation_types_covered"]


def test_summary_flags() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    summary = summarize_augsynth_remediation_diagnostic_validation_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "augsynth_remediation_and_diagnostic_validation_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    summary = summarize_augsynth_remediation_diagnostic_validation_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    assert summary["augsynth_production_inference_authorized"] is False
    assert summary["augsynth_production_p_value_authorized"] is False
    assert summary["augsynth_causal_ci_authorized"] is False


def test_filter_helpers() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    solver = filter_augsynth_remediation_diagnostic_validation_plan(
        rows, validation_area=ValidationArea.CVXPY_SOLVER_AVAILABILITY
    )
    assert solver
    blocked = filter_augsynth_remediation_diagnostic_validation_plan(
        rows, current_status=ValidationStatus.BLOCKED
    )
    assert blocked
    adapter = filter_augsynth_remediation_diagnostic_validation_plan(rows, requires_adapter=True)
    assert adapter
    null_cal = filter_augsynth_remediation_diagnostic_validation_plan(
        rows, requires_null_calibration=True
    )
    assert null_cal
    donor = filter_augsynth_remediation_diagnostic_validation_plan(
        rows, remediation_type=RemediationType.DONOR_SUPPORT_VALIDATION
    )
    assert donor


def test_required_fields_nonempty() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    for row in rows:
        assert row.required_inputs
        assert row.required_diagnostics
        assert row.required_dgp_coverage
        assert row.required_failure_registry_checks
        assert row.passing_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_augsynth_remediation_diagnostic_validation_plan()
    summary = summarize_augsynth_remediation_diagnostic_validation_plan(rows)
    validation = validate_augsynth_remediation_diagnostic_validation_plan(rows)
    assert summary["validation_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["validation_area_counts"] == validation["validation_area_counts"]
    assert summary["remediation_type_counts"] == validation["remediation_type_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["validation_row_count"] >= MIN_VALIDATION_ROW_COUNT
    assert data["all_required_validation_areas_covered"] is True
    for area in REQUIRED_VALIDATION_AREAS:
        assert data["validation_area_counts"].get(area.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0
    for rtype in REQUIRED_REMEDIATION_TYPES:
        assert data["remediation_type_counts"].get(rtype.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize AugSynth production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
