"""Tests for SIMULATION_DGP_COVERAGE_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.simulation_dgp_coverage_plan_001 import (
    MIN_CATEGORY_COUNTS,
    MIN_COVERAGE_PURPOSE_COUNTS,
    RECOMMENDED_NEXT_ARTIFACTS,
    CoveragePurpose,
    DgpCategory,
    DgpSeverity,
    InferenceFamily,
    MethodFamily,
    _AUTH_FLAGS,
    build_scenarios,
    build_simulation_dgp_coverage_plan,
    filter_simulation_dgp_requirements,
    run_validation,
    summarize_simulation_dgp_coverage_plan,
    validate_simulation_dgp_coverage_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SIMULATION_DGP_COVERAGE_PLAN_001_summary.json"
_REPORT = _REPO / "docs/track_d/SIMULATION_DGP_COVERAGE_PLAN_001_REPORT.md"


def test_dgp_plan_build_and_minimum_count() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    assert len(requirements) >= 90
    assert len({r.dgp_id for r in requirements}) == len(requirements)


def test_category_thresholds() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    validation = validate_simulation_dgp_coverage_plan(requirements)
    assert validation["valid"]
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        assert validation["category_counts"][cat.value] >= minimum


def test_coverage_purpose_thresholds() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    for purpose, minimum in MIN_COVERAGE_PURPOSE_COUNTS.items():
        count = len(filter_simulation_dgp_requirements(requirements, coverage_purpose=purpose))
        assert count >= minimum


def test_all_method_and_inference_families_represented() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    for family in MethodFamily:
        assert any(family in r.affected_method_families for r in requirements)
    for inf in InferenceFamily:
        assert any(inf in r.affected_inference_families for r in requirements)


def test_summary_flags() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    summary = summarize_simulation_dgp_coverage_plan(requirements)
    assert summary["shared_dgp_universe_required"] is True
    assert summary["observed_diagnostics_mapped_to_dgps"] is True
    assert summary["null_calibration_alone_sufficient"] is False
    assert summary["dgp_coverage_blocks_future_promotion"] is True
    assert summary["multicell_and_interference_require_research_handling"] is True
    assert summary["sparse_count_binary_outcomes_require_coverage"] is True
    assert summary["downstream_work_paused"] is True
    assert summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0]


def test_no_downstream_authorization() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    summary = summarize_simulation_dgp_coverage_plan(requirements)
    for flag in _AUTH_FLAGS:
        assert summary[flag] is False


def test_filter_helpers() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    null_rows = filter_simulation_dgp_requirements(requirements, category=DgpCategory.NULL_BASELINE)
    assert len(null_rows) >= MIN_CATEGORY_COUNTS[DgpCategory.NULL_BASELINE]
    blockers = [r for r in requirements if r.blocks_promotion_if_missing]
    assert blockers
    research = filter_simulation_dgp_requirements(requirements, severity=DgpSeverity.RESEARCH_EXTENSION)
    assert research
    scm = filter_simulation_dgp_requirements(requirements, method_family=MethodFamily.SCM)
    assert scm
    placebo = filter_simulation_dgp_requirements(requirements, inference_family=InferenceFamily.PLACEBO_RANK)
    assert placebo
    null_cal = filter_simulation_dgp_requirements(requirements, coverage_purpose=CoveragePurpose.NULL_CALIBRATION)
    assert len(null_cal) >= MIN_COVERAGE_PURPOSE_COUNTS[CoveragePurpose.NULL_CALIBRATION]


def test_required_fields_nonempty() -> None:
    requirements = build_simulation_dgp_coverage_plan()
    for req in requirements:
        assert req.covered_observed_diagnostics
        assert req.affected_method_families
        assert req.affected_inference_families
        assert req.coverage_purposes


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report_exist() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SIMULATION_DGP_COVERAGE_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["dgp_count"] >= 90
