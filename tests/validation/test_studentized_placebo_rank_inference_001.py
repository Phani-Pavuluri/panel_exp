"""Tests for STUDENTIZED_PLACEBO_RANK_INFERENCE_001 harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.studentized_placebo_rank_inference_001 import (
    run_studentized_placebo_rank_inference_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/STUDENTIZED_PLACEBO_RANK_INFERENCE_001_summary.json"


def test_harness_no_failed_scenarios() -> None:
    summary = run_studentized_placebo_rank_inference_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_harness_verdict() -> None:
    summary = run_studentized_placebo_rank_inference_validation()
    assert summary["verdict"] == (
        "studentized_placebo_rank_inference_defined_no_downstream_authorization"
    )


def test_harness_authorization_flags_false() -> None:
    summary = run_studentized_placebo_rank_inference_validation()
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


def test_harness_minimum_scenario_count() -> None:
    summary = run_studentized_placebo_rank_inference_validation()
    assert summary["scenario_count"] >= 28


def test_studentized_statistic_contract_in_summary() -> None:
    summary = run_studentized_placebo_rank_inference_validation()
    contract = summary["studentized_statistic_contract"]
    assert contract["formula"] == "(effect - null_value) / scale"
    assert "two_sided" in contract["supported_directions"]
