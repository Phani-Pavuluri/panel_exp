"""Tests for OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.observed_panel_diagnostic_requirements_001 import (
    MIN_CATEGORY_COUNTS,
    MIN_ROUTING_IMPACT_COUNTS,
    RECOMMENDED_NEXT_ARTIFACTS,
    DiagnosticCategory,
    DiagnosticSeverity,
    MethodFamily,
    RoutingImpact,
    _AUTH_FLAGS,
    build_observed_panel_diagnostic_requirements,
    build_scenarios,
    filter_observed_panel_diagnostic_requirements,
    run_validation,
    summarize_observed_panel_diagnostic_requirements,
    validate_observed_panel_diagnostic_requirements,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_summary.json"
_REPORT = _REPO / "docs/track_d/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_REPORT.md"


def test_requirements_build_and_minimum_count() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    assert len(requirements) >= 70
    assert len({r.requirement_id for r in requirements}) == len(requirements)


def test_category_thresholds() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    validation = validate_observed_panel_diagnostic_requirements(requirements)
    assert validation["valid"]
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        assert validation["category_counts"][cat.value] >= minimum


def test_routing_impact_thresholds() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    impact_counts: dict[RoutingImpact, int] = {}
    for impact in RoutingImpact:
        impact_counts[impact] = len(
            filter_observed_panel_diagnostic_requirements(requirements, routing_impact=impact)
        )
    for impact, minimum in MIN_ROUTING_IMPACT_COUNTS.items():
        assert impact_counts[impact] >= minimum


def test_all_method_families_represented() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    for family in MethodFamily:
        assert any(family in r.affected_method_families for r in requirements)


def test_summary_flags() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    summary = summarize_observed_panel_diagnostic_requirements(requirements)
    assert summary["method_selection_requires_observed_panel_diagnostics"] is True
    assert summary["hard_blockers_defined"] is True
    assert summary["warnings_defined"] is True
    assert summary["routes_to_simulation_dgp_coverage_plan"] is True
    assert summary["routes_to_failure_mode_registry"] is True
    assert summary["routes_to_design_stress_tests"] is True
    assert summary["routes_to_multicell_research"] is True
    assert summary["downstream_work_paused"] is True
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]


def test_no_downstream_authorization() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    summary = summarize_observed_panel_diagnostic_requirements(requirements)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    panel = filter_observed_panel_diagnostic_requirements(
        requirements, category=DiagnosticCategory.PANEL_STRUCTURE
    )
    assert len(panel) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.PANEL_STRUCTURE]
    blockers = filter_observed_panel_diagnostic_requirements(
        requirements, severity=DiagnosticSeverity.REQUIRED_BLOCKER
    )
    assert blockers
    scm = filter_observed_panel_diagnostic_requirements(
        requirements, method_family=MethodFamily.SCM
    )
    assert scm
    blocked = filter_observed_panel_diagnostic_requirements(
        requirements, routing_impact=RoutingImpact.BLOCK_METHOD_SELECTION
    )
    assert len(blocked) >= MIN_ROUTING_IMPACT_COUNTS[RoutingImpact.BLOCK_METHOD_SELECTION]


def test_blocker_warning_fields_nonempty() -> None:
    requirements = build_observed_panel_diagnostic_requirements()
    for req in requirements:
        assert req.blocker_condition.strip()
        assert req.warning_condition.strip()
        assert req.affected_method_families


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"
    assert data["failed_scenarios"] == []
    assert data["requirement_count"] >= 70
