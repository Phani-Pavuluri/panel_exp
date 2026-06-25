"""Tests for PRODUCTION_READINESS_BACKLOG_LEDGER_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.production_readiness_backlog_ledger_001 import (
    MIN_LEDGER_ROW_COUNT,
    RECOMMENDED_NEXT_ARTIFACTS,
    REQUIRED_BACKLOG_ITEM_IDS,
    REQUIRED_DOMAINS,
    REQUIRED_METHOD_FAMILIES,
    REQUIRED_PRIORITIES,
    REQUIRED_STATUSES,
    Domain,
    MethodFamily,
    Priority,
    BacklogStatus,
    _AUTH_FLAGS,
    _BOUNDARY_FLAGS,
    build_production_readiness_backlog_ledger,
    build_scenarios,
    filter_production_readiness_backlog_ledger,
    run_validation,
    summarize_production_readiness_backlog_ledger,
    validate_production_readiness_backlog_ledger,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PRODUCTION_READINESS_BACKLOG_LEDGER_001_summary.json"
_REPORT = _REPO / "docs/track_d/PRODUCTION_READINESS_BACKLOG_LEDGER_001_REPORT.md"


def test_ledger_rows_build_and_minimum_count() -> None:
    rows = build_production_readiness_backlog_ledger()
    assert len(rows) >= MIN_LEDGER_ROW_COUNT
    assert len({r.item_id for r in rows}) == len(rows)
    assert all(not r.production_ready for r in rows)


def test_all_domains_priorities_statuses_and_families_represented() -> None:
    rows = build_production_readiness_backlog_ledger()
    validation = validate_production_readiness_backlog_ledger(rows)
    assert validation["valid"]
    assert validation["all_required_domains_covered"]
    assert validation["all_required_priorities_covered"]
    assert validation["all_required_statuses_covered"]
    assert validation["all_required_method_families_covered"]
    assert validation["all_required_backlog_items_covered"]


def test_summary_flags() -> None:
    rows = build_production_readiness_backlog_ledger()
    summary = summarize_production_readiness_backlog_ledger(rows)
    for flag, expected in _BOUNDARY_FLAGS.items():
        assert summary[flag] == expected
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]
    assert summary["verdict"] == (
        "production_readiness_backlog_ledger_created_no_downstream_authorization"
    )


def test_no_downstream_authorization() -> None:
    rows = build_production_readiness_backlog_ledger()
    summary = summarize_production_readiness_backlog_ledger(rows)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    rows = build_production_readiness_backlog_ledger()
    scm = filter_production_readiness_backlog_ledger(rows, method_family=MethodFamily.SCM)
    assert scm
    p1 = filter_production_readiness_backlog_ledger(rows, priority=Priority.P1_FIRST_CANDIDATE_BLOCKER)
    assert p1
    blocked = filter_production_readiness_backlog_ledger(rows, current_status=BacklogStatus.BLOCKED)
    assert blocked
    router = filter_production_readiness_backlog_ledger(
        rows, domain=Domain.DATA_DRIVEN_ROUTER
    )
    assert router


def test_required_fields_nonempty() -> None:
    rows = build_production_readiness_backlog_ledger()
    for row in rows:
        assert row.required_evidence
        assert row.dependency_artifacts
        assert row.blocking_reason
        assert row.exit_condition
        assert row.authorization_boundary
        assert row.forbidden_current_use


def test_summary_count_consistency() -> None:
    rows = build_production_readiness_backlog_ledger()
    summary = summarize_production_readiness_backlog_ledger(rows)
    validation = validate_production_readiness_backlog_ledger(rows)
    assert summary["ledger_row_count"] == len(rows)
    assert summary["domain_counts"] == validation["domain_counts"]
    assert summary["priority_counts"] == validation["priority_counts"]
    assert summary["status_counts"] == validation["status_counts"]
    assert summary["method_family_counts"] == validation["method_family_counts"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "PRODUCTION_READINESS_BACKLOG_LEDGER_001"
    assert data["failed_scenarios"] == []
    assert data["ledger_row_count"] >= MIN_LEDGER_ROW_COUNT
    assert data["all_required_domains_covered"] is True
    assert data["all_required_backlog_items_covered"] is True
    for domain in REQUIRED_DOMAINS:
        assert data["domain_counts"].get(domain.value, 0) > 0
    for priority in REQUIRED_PRIORITIES:
        assert data["priority_counts"].get(priority.value, 0) > 0
    for status in REQUIRED_STATUSES:
        assert data["status_counts"].get(status.value, 0) > 0
    for family in REQUIRED_METHOD_FAMILIES:
        assert data["method_family_counts"].get(family.value, 0) > 0
    for item_id in REQUIRED_BACKLOG_ITEM_IDS:
        assert data["all_required_backlog_items_covered"] is True
        assert item_id in {
            s["scenario_id"].replace("backlog_item_", "").replace("_represented", "")
            for s in data.get("scenario_results", [])
            if s.get("passed")
        }


def test_report_states_no_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "Resolved means the audit/plan artifact is complete" in text
    assert "does not authorize production inference" in text
    assert "does not authorize production p-values" in text
    assert "does not authorize causal confidence intervals" in text
    assert "TrustReport" in text
