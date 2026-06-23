"""Tests for AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001 harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.augsynth_point_randomization_integration_001 import (
    run_augsynth_point_randomization_integration_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json"


def test_harness_no_failed_scenarios() -> None:
    summary = run_augsynth_point_randomization_integration_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_harness_verdict() -> None:
    summary = run_augsynth_point_randomization_integration_validation()
    assert summary["verdict"] == (
        "augsynth_point_randomization_integration_defined_no_downstream_authorization"
    )


def test_harness_authorization_flags_false() -> None:
    summary = run_augsynth_point_randomization_integration_validation()
    for key in (
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
        "augsynth_jk_authorized",
    ):
        assert summary[key] is False


def test_harness_minimum_scenario_count() -> None:
    summary = run_augsynth_point_randomization_integration_validation()
    assert summary["scenario_count"] >= 34


def test_summary_json_authorization_flags_false() -> None:
    if not _SUMMARY.exists():
        return
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in (
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
        "augsynth_jk_authorized",
    ):
        assert data[key] is False
