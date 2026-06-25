"""Tests for SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.synthetic_did_implementation_readiness_plan_001 import (
    MIN_READINESS_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_READINESS_AREAS,
    REQUIRED_READINESS_TYPES,
    REQUIRED_STATUSES,
    ReadinessArea,
    ReadinessStatus,
    ReadinessType,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_scenarios,
    build_synthetic_did_implementation_readiness_plan,
    filter_synthetic_did_implementation_readiness_plan,
    run_validation,
    summarize_synthetic_did_implementation_readiness_plan,
    validate_synthetic_did_implementation_readiness_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001_REPORT.md"


def test_readiness_rows_build_and_minimum_count() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    assert len(rows) >= MIN_READINESS_ROW_COUNT
    assert len({r.readiness_id for r in rows}) == len(rows)


def test_all_areas_statuses_and_readiness_types_represented() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    validation = validate_synthetic_did_implementation_readiness_plan(rows)
    assert validation["valid"]
    assert validation["all_required_readiness_areas_covered"]
    assert validation["all_required_statuses_covered"]
    assert validation["all_required_readiness_types_covered"]


def test_summary_flags() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    summary = summarize_synthetic_did_implementation_readiness_plan(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "synthetic_did_implementation_readiness_plan_defined_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    summary = summarize_synthetic_did_implementation_readiness_plan(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    assert summary["synthetic_did_production_inference_authorized"] is False
    assert summary["synthetic_did_production_p_value_authorized"] is False
    assert summary["synthetic_did_causal_ci_authorized"] is False


def test_filter_helpers() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    unit_weight = filter_synthetic_did_implementation_readiness_plan(
        rows, readiness_area=ReadinessArea.UNIT_WEIGHT
    )
    assert unit_weight
    blocked = filter_synthetic_did_implementation_readiness_plan(
        rows, current_status=ReadinessStatus.BLOCKED
    )
    assert blocked
    adapter = filter_synthetic_did_implementation_readiness_plan(rows, requires_adapter=True)
    assert adapter
    null_cal = filter_synthetic_did_implementation_readiness_plan(
        rows, requires_null_calibration=True
    )
    assert null_cal
    component = filter_synthetic_did_implementation_readiness_plan(
        rows, readiness_type=ReadinessType.ESTIMATOR_COMPONENT_REQUIREMENT
    )
    assert component


def test_required_fields_nonempty() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    for row in rows:
        assert row.required_inputs
        assert row.required_diagnostics
        assert row.required_implementation_components
        assert row.required_failure_registry_checks
        assert row.passing_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_synthetic_did_implementation_readiness_plan()
    summary = summarize_synthetic_did_implementation_readiness_plan(rows)
    validation = validate_synthetic_did_implementation_readiness_plan(rows)
    assert summary["readiness_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["readiness_area_counts"] == validation["readiness_area_counts"]
    assert summary["readiness_type_counts"] == validation["readiness_type_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["readiness_row_count"] >= MIN_READINESS_ROW_COUNT
    assert data["all_required_readiness_areas_covered"] is True
    for area in REQUIRED_READINESS_AREAS:
        assert data["readiness_area_counts"].get(area.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0
    for rtype in REQUIRED_READINESS_TYPES:
        assert data["readiness_type_counts"].get(rtype.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not implement Synthetic DID" in text
    assert "does not authorize Synthetic DID production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
