"""Tests for SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001 harness."""

from __future__ import annotations

from panel_exp.validation.scm_studentized_treated_set_placebo_integration_001 import (
    run_scm_studentized_treated_set_placebo_integration_validation,
)


def test_harness_no_failed_scenarios() -> None:
    summary = run_scm_studentized_treated_set_placebo_integration_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_harness_verdict() -> None:
    summary = run_scm_studentized_treated_set_placebo_integration_validation()
    assert summary["verdict"] == (
        "scm_studentized_treated_set_placebo_integration_defined_no_downstream_authorization"
    )


def test_harness_authorization_flags_false() -> None:
    summary = run_scm_studentized_treated_set_placebo_integration_validation()
    for key in (
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    ):
        assert summary[key] is False


def test_harness_integration_layers() -> None:
    summary = run_scm_studentized_treated_set_placebo_integration_validation()
    assert "studentized_placebo_rank" in summary["integration_layers"]


def test_harness_minimum_scenario_count() -> None:
    summary = run_scm_studentized_treated_set_placebo_integration_validation()
    assert summary["scenario_count"] >= 34
