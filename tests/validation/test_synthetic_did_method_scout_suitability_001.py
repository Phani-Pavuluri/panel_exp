"""Tests for SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.synthetic_did_method_scout_suitability_001 import (
    MIN_SCOUT_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_COMPONENTS,
    REQUIRED_STATUSES,
    ScoutStatus,
    SyntheticDidComponent,
    _AUTH_FLAGS,
    _SCOUT_FLAGS,
    build_scenarios,
    build_synthetic_did_method_scout_suitability,
    filter_synthetic_did_method_scout_suitability,
    run_validation,
    summarize_synthetic_did_method_scout_suitability,
    validate_synthetic_did_method_scout_suitability,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_summary.json"
_REPORT = _REPO / "docs/track_d/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_REPORT.md"


def test_scout_rows_build_and_minimum_count() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    assert len(rows) >= MIN_SCOUT_ROW_COUNT
    assert len({r.scout_id for r in rows}) == len(rows)


def test_all_components_and_statuses_represented() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    validation = validate_synthetic_did_method_scout_suitability(rows)
    assert validation["valid"]
    assert validation["all_required_paths_covered"]
    assert validation["all_statuses_represented"]


def test_summary_flags() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    summary = summarize_synthetic_did_method_scout_suitability(rows)
    for flag, expected in _SCOUT_FLAGS.items():
        assert summary[flag] is expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "synthetic_did_method_scout_and_suitability_completed_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    summary = summarize_synthetic_did_method_scout_suitability(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    assert summary["synthetic_did_production_inference_authorized"] is False
    assert summary["synthetic_did_production_p_value_authorized"] is False
    assert summary["synthetic_did_causal_ci_authorized"] is False


def test_filter_helpers() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    point = filter_synthetic_did_method_scout_suitability(
        rows, synthetic_did_component=SyntheticDidComponent.POINT_ESTIMATE
    )
    assert point
    blocked = filter_synthetic_did_method_scout_suitability(rows, current_status=ScoutStatus.BLOCKED)
    assert len(blocked) >= 5
    scm_cmp = filter_synthetic_did_method_scout_suitability(rows, comparison_method="scm")
    assert scm_cmp
    vs_did = filter_synthetic_did_method_scout_suitability(
        rows, synthetic_did_component=SyntheticDidComponent.VS_DID
    )
    assert vs_did


def test_required_fields_nonempty() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    for row in rows:
        assert row.required_design_conditions
        assert row.required_observed_diagnostics
        assert row.required_dgp_coverage
        assert row.required_failure_registry_checks
        assert row.promotion_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_synthetic_did_method_scout_suitability()
    summary = summarize_synthetic_did_method_scout_suitability(rows)
    validation = validate_synthetic_did_method_scout_suitability(rows)
    assert summary["scout_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["component_counts"] == validation["component_counts"]
    assert summary["comparison_method_counts"] == validation["comparison_method_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001"
    assert data["failed_scenarios"] == []
    assert data["scout_row_count"] >= MIN_SCOUT_ROW_COUNT
    assert data["all_required_paths_covered"] is True
    for component in REQUIRED_COMPONENTS:
        assert data["component_counts"].get(component.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not implement Synthetic DID" in text
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
