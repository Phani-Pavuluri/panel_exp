"""Tests for METHOD_FAILURE_MODE_REGISTRY_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_failure_mode_registry_001 import (
    MIN_ACTION_COUNTS,
    MIN_CATEGORY_COUNTS,
    MIN_SEVERITY_COUNTS,
    RECOMMENDED_NEXT_ARTIFACTS,
    DesignFamily,
    FailureModeCategory,
    FailureSeverity,
    InferenceFamily,
    MethodFamily,
    RequiredAction,
    _AUTH_FLAGS,
    build_method_failure_mode_registry,
    build_scenarios,
    filter_method_failure_modes,
    run_validation,
    summarize_method_failure_mode_registry,
    validate_method_failure_mode_registry,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_FAILURE_MODE_REGISTRY_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_FAILURE_MODE_REGISTRY_001_REPORT.md"


def test_registry_build_and_minimum_count() -> None:
    modes = build_method_failure_mode_registry()
    assert len(modes) >= 95
    assert len({m.failure_id for m in modes}) == len(modes)


def test_category_thresholds() -> None:
    modes = build_method_failure_mode_registry()
    validation = validate_method_failure_mode_registry(modes)
    assert validation["valid"]
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        assert validation["category_counts"][cat.value] >= minimum


def test_severity_and_action_thresholds() -> None:
    modes = build_method_failure_mode_registry()
    action_counts: dict[RequiredAction, int] = {}
    for action in RequiredAction:
        action_counts[action] = len(filter_method_failure_modes(modes, action=action))
    for action, minimum in MIN_ACTION_COUNTS.items():
        assert action_counts[action] >= minimum
    severity_counts = {s: len(filter_method_failure_modes(modes, severity=s)) for s in FailureSeverity}
    for sev, minimum in MIN_SEVERITY_COUNTS.items():
        assert severity_counts[sev] >= minimum


def test_all_families_represented() -> None:
    modes = build_method_failure_mode_registry()
    for design in DesignFamily:
        assert any(design in m.affected_design_families for m in modes)
    for method in MethodFamily:
        assert any(method in m.affected_method_families for m in modes)
    for inf in InferenceFamily:
        assert any(inf in m.affected_inference_families for m in modes)


def test_summary_flags() -> None:
    modes = build_method_failure_mode_registry()
    summary = summarize_method_failure_mode_registry(modes)
    assert summary["central_failure_mode_registry_required"] is True
    assert summary["hard_blockers_defined"] is True
    assert summary["diagnostic_only_paths_defined"] is True
    assert summary["sensitivity_only_paths_defined"] is True
    assert summary["remediation_paths_defined"] is True
    assert summary["retire_or_replace_paths_defined"] is True
    assert summary["future_promotion_must_consult_registry"] is True
    assert summary["observed_diagnostics_linked"] is True
    assert summary["dgp_triggers_linked"] is True
    assert summary["promotion_blockers_defined"] is True
    assert summary["downstream_work_paused"] is True
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]


def test_no_downstream_authorization() -> None:
    modes = build_method_failure_mode_registry()
    summary = summarize_method_failure_mode_registry(modes)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    modes = build_method_failure_mode_registry()
    design = filter_method_failure_modes(modes, category=FailureModeCategory.DESIGN_ASSIGNMENT)
    assert len(design) >= MIN_CATEGORY_COUNTS[FailureModeCategory.DESIGN_ASSIGNMENT]
    blockers = filter_method_failure_modes(modes, promotion_blocking=True)
    assert blockers
    downstream = filter_method_failure_modes(modes, downstream_blocking=True)
    assert downstream
    scm = filter_method_failure_modes(modes, method_family=MethodFamily.SCM)
    assert scm
    retire = filter_method_failure_modes(modes, action=RequiredAction.RETIRE_OR_REPLACE)
    assert retire
    scout = filter_method_failure_modes(modes, action=RequiredAction.SCOUT_NEW_METHOD)
    assert scout


def test_required_fields_nonempty() -> None:
    modes = build_method_failure_mode_registry()
    for mode in modes:
        assert mode.observed_diagnostic_triggers
        assert mode.dgp_triggers
        assert mode.affected_design_families
        assert mode.affected_method_families
        assert mode.affected_inference_families
        assert mode.required_actions


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_FAILURE_MODE_REGISTRY_001"
    assert data["failed_scenarios"] == []
    assert data["failure_mode_count"] >= 95
