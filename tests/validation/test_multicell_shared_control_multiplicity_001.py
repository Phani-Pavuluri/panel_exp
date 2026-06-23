"""Tests for MULTICELL_SHARED_CONTROL_MULTIPLICITY_001 harness."""

from __future__ import annotations

from panel_exp.validation.multicell_shared_control_multiplicity_001 import (
    run_multicell_shared_control_multiplicity_validation,
)


def test_harness_no_failed_scenarios() -> None:
    summary = run_multicell_shared_control_multiplicity_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_harness_verdict() -> None:
    summary = run_multicell_shared_control_multiplicity_validation()
    assert summary["verdict"] == (
        "multicell_shared_control_multiplicity_defined_no_downstream_authorization"
    )


def test_harness_authorization_flags_false() -> None:
    summary = run_multicell_shared_control_multiplicity_validation()
    for key in (
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
        "global_multicell_decision_allowed",
        "winner_selection_allowed",
        "pooled_multicell_effect_allowed",
    ):
        assert summary[key] is False


def test_harness_minimum_scenario_count() -> None:
    summary = run_multicell_shared_control_multiplicity_validation()
    assert summary["scenario_count"] >= 27
