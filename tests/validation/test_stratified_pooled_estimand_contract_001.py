"""Tests for STRATIFIED_POOLED_ESTIMAND_CONTRACT_001 harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.stratified_pooled_estimand_contract_001 import (
    run_stratified_pooled_estimand_contract_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json"


def test_harness_no_failed_scenarios() -> None:
    summary = run_stratified_pooled_estimand_contract_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_harness_verdict() -> None:
    summary = run_stratified_pooled_estimand_contract_validation()
    assert summary["verdict"] == (
        "stratified_pooled_estimand_contract_defined_no_downstream_authorization"
    )


def test_harness_authorization_flags_false() -> None:
    summary = run_stratified_pooled_estimand_contract_validation()
    for key in (
        "trustreport_authorized",
        "calibration_signal_allowed",
        "mmm_ingestion_allowed",
        "llm_decisioning_allowed",
        "production_decisioning_allowed",
        "live_api_authorized",
        "scheduler_authorized",
        "budget_optimization_allowed",
        "pooled_effect_authorized",
        "global_summary_allowed",
        "winner_selection_allowed",
    ):
        assert summary[key] is False


def test_harness_minimum_scenario_count() -> None:
    summary = run_stratified_pooled_estimand_contract_validation()
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
        "pooled_effect_authorized",
        "global_summary_allowed",
        "winner_selection_allowed",
    ):
        assert data[key] is False
