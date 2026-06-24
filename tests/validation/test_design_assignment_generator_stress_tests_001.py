"""Tests for DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.design_assignment_generator_stress_tests_001 import (
    MIN_ACTION_COUNTS,
    MIN_CATEGORY_COUNTS,
    MIN_SEVERITY_COUNTS,
    RECOMMENDED_NEXT_ARTIFACTS,
    AssignmentFamily,
    InferencePath,
    StressAction,
    StressSeverity,
    StressTestCategory,
    _AUTH_FLAGS,
    build_design_assignment_generator_stress_tests,
    build_scenarios,
    filter_design_assignment_generator_stress_tests,
    run_validation,
    summarize_design_assignment_generator_stress_tests,
    validate_design_assignment_generator_stress_tests,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_summary.json"
_REPORT = _REPO / "docs/track_d/DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001_REPORT.md"


def test_stress_tests_build_and_minimum_count() -> None:
    tests = build_design_assignment_generator_stress_tests()
    assert len(tests) >= 85
    assert len({t.stress_id for t in tests}) == len(tests)


def test_category_thresholds() -> None:
    tests = build_design_assignment_generator_stress_tests()
    validation = validate_design_assignment_generator_stress_tests(tests)
    assert validation["valid"]
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        assert validation["category_counts"][cat.value] >= minimum


def test_severity_and_action_thresholds() -> None:
    tests = build_design_assignment_generator_stress_tests()
    for sev, minimum in MIN_SEVERITY_COUNTS.items():
        count = len(filter_design_assignment_generator_stress_tests(tests, severity=sev))
        assert count >= minimum
    for action, minimum in MIN_ACTION_COUNTS.items():
        count = len(filter_design_assignment_generator_stress_tests(tests, action=action))
        assert count >= minimum


def test_all_assignment_and_inference_paths_represented() -> None:
    tests = build_design_assignment_generator_stress_tests()
    for family in AssignmentFamily:
        assert any(family in t.affected_assignment_families for t in tests)
    for path in InferencePath:
        assert any(path in t.affected_inference_paths for t in tests)


def test_summary_flags() -> None:
    tests = build_design_assignment_generator_stress_tests()
    summary = summarize_design_assignment_generator_stress_tests(tests)
    assert summary["assignment_generators_not_inference_engines"] is True
    assert summary["unknown_and_deterministic_assignment_block_design_based_inference"] is True
    assert summary["small_or_degenerate_support_blocks_rank_inference"] is True
    assert summary["multicell_shared_control_requires_dependence_handling"] is True
    assert summary["studentized_adapters_and_null_calibration_required"] is True
    assert summary["stress_failures_link_to_failure_registry"] is True
    assert summary["inference_authorized"] is False
    assert summary["downstream_work_paused"] is True
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]


def test_no_downstream_authorization() -> None:
    tests = build_design_assignment_generator_stress_tests()
    summary = summarize_design_assignment_generator_stress_tests(tests)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    tests = build_design_assignment_generator_stress_tests()
    support = filter_design_assignment_generator_stress_tests(
        tests, category=StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY
    )
    assert len(support) >= MIN_CATEGORY_COUNTS[StressTestCategory.ASSIGNMENT_SUPPORT_INTEGRITY]
    blocked = filter_design_assignment_generator_stress_tests(tests, blocks_inference_if_failed=True)
    assert blocked
    promotion = filter_design_assignment_generator_stress_tests(tests, promotion_blocking=True)
    assert promotion
    unknown = filter_design_assignment_generator_stress_tests(
        tests, assignment_family=AssignmentFamily.UNKNOWN_ASSIGNMENT
    )
    assert unknown
    deterministic = filter_design_assignment_generator_stress_tests(
        tests, assignment_family=AssignmentFamily.FIXED_DETERMINISTIC
    )
    assert deterministic
    studentized = filter_design_assignment_generator_stress_tests(
        tests, action=StressAction.REQUIRE_STUDENTIZED_ADAPTER
    )
    assert studentized


def test_required_fields_nonempty() -> None:
    tests = build_design_assignment_generator_stress_tests()
    for test in tests:
        assert test.required_inputs
        assert test.failure_registry_links
        assert test.observed_diagnostic_links
        assert test.dgp_links
        assert test.affected_assignment_families
        assert test.affected_inference_paths
        assert test.required_actions


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"
    assert data["failed_scenarios"] == []
    assert data["stress_test_count"] >= 85
