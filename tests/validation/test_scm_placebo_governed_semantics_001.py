"""Tests for SCM_PLACEBO_GOVERNED_SEMANTICS_001 validation harness."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_placebo_governed_semantics_001 import (
    run_scm_placebo_governed_semantics_validation,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]


def test_validation_no_failed_scenarios():
    summary = run_scm_placebo_governed_semantics_validation()
    assert summary["failed_scenarios"] == []
    assert summary["passed_scenarios"] == summary["scenario_count"]


def test_summary_authorization_flags_false():
    summary = run_scm_placebo_governed_semantics_validation()
    assert summary["trustreport_authorized"] is False
    assert summary["calibration_signal_allowed"] is False
    assert summary["production_decisioning_allowed"] is False
    assert summary["live_api_authorized"] is False
    assert summary["scheduler_authorized"] is False
    assert summary["budget_optimization_allowed"] is False


def test_summary_required_keys():
    summary = run_scm_placebo_governed_semantics_validation()
    assert summary["artifact_id"] == "SCM_PLACEBO_GOVERNED_SEMANTICS_001"
    assert summary["verdict"] == "scm_placebo_governed_semantics_defined_no_authorization"
    assert len(summary["roadmap_spine"]) == 5
    assert summary["scenario_count"] >= 15


def test_strict_validation_passes():
    summary = run_validation(strict=False)
    assert summary["status"] == "completed"


def test_summary_json_roundtrip():
    summary = run_scm_placebo_governed_semantics_validation()
    decoded = json.loads(json.dumps(summary))
    assert decoded["scm_placebo_roles"]
    assert decoded["blocked_overclaims"]
