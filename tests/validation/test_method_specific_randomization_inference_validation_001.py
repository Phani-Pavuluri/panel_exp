"""Tests for METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001 harness."""

from __future__ import annotations

import json

from panel_exp.validation.method_specific_randomization_inference_validation_001 import (
    run_method_specific_randomization_inference_validation,
    run_validation,
)


def test_harness_no_failed_scenarios():
    summary = run_method_specific_randomization_inference_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_authorization_flags_false():
    summary = run_method_specific_randomization_inference_validation()
    assert summary["trustreport_authorized"] is False
    assert summary["calibration_signal_allowed"] is False
    assert summary["mmm_ingestion_allowed"] is False
    assert summary["llm_decisioning_allowed"] is False
    assert summary["production_decisioning_allowed"] is False
    assert summary["live_api_authorized"] is False
    assert summary["scheduler_authorized"] is False
    assert summary["budget_optimization_allowed"] is False


def test_verdict_and_scenario_count():
    summary = run_method_specific_randomization_inference_validation()
    assert summary["verdict"] == (
        "method_specific_randomization_inference_validated_no_downstream_authorization"
    )
    assert summary["scenario_count"] >= 27


def test_method_readiness_counts_populated():
    summary = run_method_specific_randomization_inference_validation()
    counts = summary["method_readiness_counts"]
    assert counts["design_based_randomization_candidate"] >= 1
    assert counts["blocked"] >= 1


def test_strict_validation():
    summary = run_validation(strict=False)
    assert summary["next_artifact"] == "SCM_TREATED_SET_PLACEBO_INTEGRATION_001"


def test_summary_json_roundtrip():
    summary = run_method_specific_randomization_inference_validation()
    decoded = json.loads(json.dumps(summary))
    assert len(decoded["method_families_classified"]) == 9
