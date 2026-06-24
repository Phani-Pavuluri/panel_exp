"""Tests for MULTICELL_MAX_T_RESEARCH_SCOUT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.multicell_max_t_research_scout_001 import (
    MIN_SCOUT_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_METHOD_FAMILIES,
    REQUIRED_PATHS,
    REQUIRED_STATUSES,
    MethodFamily,
    MultiplicityPath,
    ScoutStatus,
    _AUTH_FLAGS,
    _SCOUT_FLAGS,
    build_multicell_max_t_research_scout,
    build_scenarios,
    filter_multicell_max_t_research_scout,
    run_validation,
    summarize_multicell_max_t_research_scout,
    validate_multicell_max_t_research_scout,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/MULTICELL_MAX_T_RESEARCH_SCOUT_001_summary.json"
_REPORT = _REPO / "docs/track_d/MULTICELL_MAX_T_RESEARCH_SCOUT_001_REPORT.md"


def test_scout_rows_build_and_minimum_count() -> None:
    rows = build_multicell_max_t_research_scout()
    assert len(rows) >= MIN_SCOUT_ROW_COUNT
    assert len({r.scout_id for r in rows}) == len(rows)


def test_all_paths_statuses_and_families_represented() -> None:
    rows = build_multicell_max_t_research_scout()
    validation = validate_multicell_max_t_research_scout(rows)
    assert validation["valid"]
    assert validation["all_required_paths_covered"]
    assert validation["all_statuses_represented"]
    assert validation["all_required_method_families_represented"]


def test_summary_flags() -> None:
    rows = build_multicell_max_t_research_scout()
    summary = summarize_multicell_max_t_research_scout(rows)
    for flag, expected in _SCOUT_FLAGS.items():
        assert summary[flag] is expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == "multicell_max_t_research_scout_completed_no_downstream_authorization"


def test_no_downstream_authorization() -> None:
    rows = build_multicell_max_t_research_scout()
    summary = summarize_multicell_max_t_research_scout(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_multicell_max_t_research_scout()
    max_t = filter_multicell_max_t_research_scout(
        rows, multiplicity_path=MultiplicityPath.SINGLE_STEP_MAX_T
    )
    assert max_t
    blocked = filter_multicell_max_t_research_scout(rows, current_status=ScoutStatus.BLOCKED)
    assert len(blocked) >= 5
    scm = filter_multicell_max_t_research_scout(rows, method_family=MethodFamily.SCM)
    assert scm
    pooled = filter_multicell_max_t_research_scout(
        rows, multiplicity_path=MultiplicityPath.POOLED_GLOBAL
    )
    assert pooled


def test_required_fields_nonempty() -> None:
    rows = build_multicell_max_t_research_scout()
    for row in rows:
        assert row.required_design_conditions
        assert row.required_diagnostics
        assert row.required_dgp_coverage
        assert row.failure_registry_links
        assert row.promotion_evidence_required
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_multicell_max_t_research_scout()
    summary = summarize_multicell_max_t_research_scout(rows)
    validation = validate_multicell_max_t_research_scout(rows)
    assert summary["scout_row_count"] == len(rows)
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["method_family_counts"] == validation["method_family_counts"]
    assert summary["multiplicity_path_counts"] == validation["multiplicity_path_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "MULTICELL_MAX_T_RESEARCH_SCOUT_001"
    assert data["failed_scenarios"] == []
    assert data["scout_row_count"] >= MIN_SCOUT_ROW_COUNT
    assert data["all_required_paths_covered"] is True
    for path in REQUIRED_PATHS:
        assert data["multiplicity_path_counts"].get(path.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0
    for family in REQUIRED_METHOD_FAMILIES:
        assert data["method_family_counts"].get(family.value, 0) > 0


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
