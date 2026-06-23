"""Tests for STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001 validation harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.studentized_randomization_null_calibration_001 import (
    NEXT_ARTIFACT,
    run_studentized_randomization_null_calibration_harness,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001_summary.json"


def test_harness_no_failed_scenarios() -> None:
    summary = run_studentized_randomization_null_calibration_harness()
    assert summary["failed_scenarios"] == []
    assert summary["verdict"] == (
        "studentized_randomization_null_calibration_completed_no_downstream_authorization"
    )


def test_harness_dgp_coverage() -> None:
    summary = run_studentized_randomization_null_calibration_harness()
    assert all(summary["dgp_coverage"].values())


def test_harness_assignment_family_coverage() -> None:
    summary = run_studentized_randomization_null_calibration_harness()
    assert all(summary["assignment_family_coverage"].values())


def test_harness_statistic_mode_coverage() -> None:
    summary = run_studentized_randomization_null_calibration_harness()
    assert all(summary["statistic_mode_coverage"].values())


def test_harness_authorization_flags_false() -> None:
    summary = run_studentized_randomization_null_calibration_harness()
    for key in (
        "production_p_value_authorized",
        "causal_confidence_interval_authorized",
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


def test_recommended_next_artifact() -> None:
    summary = run_studentized_randomization_null_calibration_harness()
    assert summary["recommended_next_artifact"] == NEXT_ARTIFACT


def test_summary_json_flags_false() -> None:
    if not _SUMMARY.exists():
        return
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in (
        "production_p_value_authorized",
        "trustreport_authorized",
        "calibration_signal_allowed",
    ):
        assert data[key] is False
