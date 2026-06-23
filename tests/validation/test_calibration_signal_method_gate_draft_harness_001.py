"""Tests for CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001 harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.calibration_signal_method_gate_draft_001 import (
    run_calibration_signal_method_gate_draft_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001_summary.json"


def test_harness_no_failed_scenarios() -> None:
    summary = run_calibration_signal_method_gate_draft_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_harness_verdict() -> None:
    summary = run_calibration_signal_method_gate_draft_validation()
    assert summary["verdict"] == "calibration_signal_method_gate_draft_defined_no_authorization"


def test_harness_row_counts() -> None:
    summary = run_calibration_signal_method_gate_draft_validation()
    assert summary["row_count"] == 25
    assert summary["source_row_count"] == 25
    assert summary["method_ids_match_source_matrix"] is True
    assert summary["unique_method_ids"] is True


def test_harness_authorization_flags_false() -> None:
    summary = run_calibration_signal_method_gate_draft_validation()
    for key in (
        "calibration_signal_allowed",
        "calibration_signal_authorized",
        "trustreport_authorized",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    ):
        assert summary[key] is False


def test_harness_minimum_scenario_count() -> None:
    summary = run_calibration_signal_method_gate_draft_validation()
    assert summary["scenario_count"] >= 35


def test_summary_json_authorization_flags_false() -> None:
    if not _SUMMARY.exists():
        return
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in (
        "calibration_signal_allowed",
        "calibration_signal_authorized",
        "trustreport_authorized",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
    ):
        assert data[key] is False
