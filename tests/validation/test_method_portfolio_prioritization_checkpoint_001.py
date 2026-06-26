"""Tests for METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_portfolio_prioritization_checkpoint_001 import (
    FIRST_POST_SCM_METHOD_LANE,
    METHOD_STANCES,
    PRIORITY_ORDER,
    RECOMMENDED_NEXT_SCM_ARTIFACT,
    SEPARATED_AUTHORIZATION_MODEL,
    _AUTH_FLAGS,
    build_method_portfolio_prioritization_checkpoint,
    build_scenarios,
    run_validation,
    validate_method_portfolio_prioritization_checkpoint,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001_REPORT.md"


def test_priority_order_present() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    assert cp.priority_order == PRIORITY_ORDER
    assert len(cp.priority_order) == 6


def test_scm_reference_not_primary_focus() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    assert cp.method_stances["SCM"] == "reference_candidate_not_primary_focus"
    assert not cp.scm_production_approval_recommended


def test_augsynth_next_primary_lane() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    assert cp.method_stances["AugSynth_ASCM"] == "next_primary_candidate_lane"
    assert cp.first_post_scm_method_lane == FIRST_POST_SCM_METHOD_LANE


def test_tbrridge_bayesian_trop_stances() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    assert cp.method_stances["TBRRidge"] == "later_practical_point_estimate_lane"
    assert cp.method_stances["Bayesian_TBR"] == "governed_prior_research_calibration_lane"
    assert cp.method_stances["TROP"] == "deferred_research_decisioning_lane"


def test_separated_authorization_model() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    assert cp.separated_authorization_model == SEPARATED_AUTHORIZATION_MODEL
    assert all(cp.separated_authorization_model.values())


def test_all_authorization_flags_false() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    for flag, expected in _AUTH_FLAGS.items():
        assert cp.authorization_flags[flag] is expected


def test_recommended_next_scm_artifact() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    assert cp.recommended_next_artifact == RECOMMENDED_NEXT_SCM_ARTIFACT
    assert cp.post_scm_handoff_artifact == RECOMMENDED_NEXT_SCM_ARTIFACT


def test_validate_checkpoint() -> None:
    cp = build_method_portfolio_prioritization_checkpoint()
    result = validate_method_portfolio_prioritization_checkpoint(cp)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_PORTFOLIO_PRIORITIZATION_CHECKPOINT_001"
    assert data["failed_scenarios"] == []
    assert data["strategic_decision"] == "shift_primary_method_focus_from_scm_to_augsynth_ascm_after_scm_closeout"
    assert data["scm_production_approval_recommended"] is False
    assert data["method_stances"] == METHOD_STANCES
    assert data["first_post_scm_method_lane"] == "AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001"
    assert data["final_verdict"] == "method_portfolio_prioritization_checkpoint_logged_no_production_authorization"


def test_report_states_no_production_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "reference candidate" in text.lower()
    assert "augsynth" in text.lower()
    assert "not production-approved" in text.lower() or "no production approval" in text.lower()
    assert "separate" in text.lower()
