"""Tests for BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.bayesian_tbr_and_tbr_retirement_boundary_audit_001 import (
    MIN_BOUNDARY_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_PATHS,
    REQUIRED_STATUSES,
    BoundaryStatus,
    MethodFamily,
    PathType,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_bayesian_tbr_and_tbr_retirement_boundary_audit,
    build_scenarios,
    filter_bayesian_tbr_and_tbr_retirement_boundary_audit,
    run_validation,
    summarize_bayesian_tbr_and_tbr_retirement_boundary_audit,
    validate_bayesian_tbr_and_tbr_retirement_boundary_audit,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_summary.json"
_REPORT = _REPO / "docs/track_d/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_REPORT.md"


def test_boundary_rows_build_and_minimum_count() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    assert len(rows) >= MIN_BOUNDARY_ROW_COUNT
    assert len({r.boundary_id for r in rows}) == len(rows)


def test_all_paths_and_statuses_represented() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    validation = validate_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    assert validation["valid"]
    assert validation["all_required_paths_covered"]
    assert validation["all_statuses_represented"]
    assert validation["retire_or_replace_paths_defined"]


def test_summary_flags() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    summary = summarize_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] is expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "bayesian_tbr_and_tbr_retirement_boundary_audit_completed_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    summary = summarize_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False
    assert summary["bayesian_tbr_production_inference_authorized"] is False
    assert summary["classic_tbr_production_inference_authorized"] is False


def test_filter_helpers() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    classic = filter_bayesian_tbr_and_tbr_retirement_boundary_audit(
        rows, method_family=MethodFamily.CLASSIC_TBR
    )
    assert classic
    blocked = filter_bayesian_tbr_and_tbr_retirement_boundary_audit(
        rows, current_status=BoundaryStatus.BLOCKED
    )
    assert len(blocked) >= 5
    retire = filter_bayesian_tbr_and_tbr_retirement_boundary_audit(
        rows, retire_or_replace_candidate=True
    )
    assert retire
    vs_tbrridge = filter_bayesian_tbr_and_tbr_retirement_boundary_audit(
        rows, path_type=PathType.VS_TBRRIDGE
    )
    assert vs_tbrridge


def test_required_fields_nonempty() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    for row in rows:
        assert row.known_blockers
        assert row.required_diagnostics
        assert row.required_dgp_coverage
        assert row.required_failure_registry_checks
        assert row.promotion_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    summary = summarize_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    validation = validate_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    assert summary["boundary_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["method_family_counts"] == validation["method_family_counts"]
    assert summary["path_type_counts"] == validation["path_type_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001"
    assert data["failed_scenarios"] == []
    assert data["boundary_row_count"] >= MIN_BOUNDARY_ROW_COUNT
    assert data["all_required_paths_covered"] is True
    for path in REQUIRED_PATHS:
        assert data["path_type_counts"].get(path.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
