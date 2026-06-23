"""Tests for MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001 validation harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.multitreated_treated_set_placebo_framework_001 import (
    build_summary,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]


def test_build_summary_governance_invariants():
    summary = build_summary()
    assert summary["artifact_id"] == "MULTITREATED-TREATED-SET-PLACEBO-FRAMEWORK-001"
    assert summary["governance_verdict"] == (
        "multitreated_treated_set_placebo_framework_defined_no_inference_authorization"
    )
    assert summary["trustreport_authorized"] is False
    assert summary["calibration_signal_allowed"] is False
    assert summary["production_decisioning_allowed"] is False
    assert summary["live_api_authorized"] is False
    assert summary["scheduler_authorized"] is False
    assert summary["budget_optimization_allowed"] is False
    assert summary["next_artifact"] == "SCM_PLACEBO_GOVERNED_SEMANTICS_001"


def test_all_scenarios_pass():
    summary = build_summary()
    failed = [s["scenario_id"] for s in summary["scenario_results"] if not s["passed"]]
    assert not failed, failed


def test_positive_and_blocked_partitions():
    summary = build_summary()
    assert len(summary["positive_scenarios"]) == 5
    assert len(summary["falsification_only_scenarios"]) == 4
    assert len(summary["blocked_scenarios"]) >= 8


def test_run_validation_strict():
    summary = run_validation(strict=False)
    assert summary["leave_one_treated_out_decision"] == "leave_one_treated_out_rejected_as_placebo"
    assert summary["multicell_global_claim_decision"] == "multicell_global_claim_blocked"


def test_summary_json_roundtrip():
    summary = build_summary()
    encoded = json.dumps(summary)
    decoded = json.loads(encoded)
    assert decoded["assignment_generator_dependency"]["module"] == (
        "panel_exp.design.assignment_generators"
    )
