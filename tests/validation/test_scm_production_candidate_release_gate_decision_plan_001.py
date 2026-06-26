"""Tests for SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.scm_production_candidate_release_gate_decision_plan_001 import (
    BLOCKED_APPROVAL_REASONS,
    DECISION_OPTIONS,
    DECISION_PLAN_FIELDS,
    INPUT_CONTRACT,
    INPUT_FIELDS,
    METHOD_PORTFOLIO_HANDOFF_TARGETS,
    RECOMMENDED_DECISION_DIRECTION,
    REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL,
    _AUTH_FLAGS,
    _SCM_FLAGS,
    build_scenarios,
    build_scm_release_gate_decision_plan,
    run_validation,
    validate_scm_release_gate_decision_plan,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001_summary.json"
_REPORT = _REPO / "docs/track_d/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001_REPORT.md"


def test_all_decision_options_present() -> None:
    plan = build_scm_release_gate_decision_plan()
    assert set(plan.planned_decision_options) == set(DECISION_OPTIONS)


def test_recommended_direction_defer() -> None:
    plan = build_scm_release_gate_decision_plan()
    assert plan.recommended_decision_direction == "defer_pending_empirical_validation"
    assert plan.recommended_decision_direction != "approve_limited_production"


def test_closeout_and_portfolio_handoff() -> None:
    plan = build_scm_release_gate_decision_plan()
    assert plan.planned_closeout_direction == "closeout_as_reference_candidate"
    assert plan.portfolio_handoff_recommendation == "handoff_to_method_portfolio"
    assert "AugSynth/ASCM" in plan.method_portfolio_handoff_targets


def test_required_empirical_evidence_and_blocked_reasons() -> None:
    plan = build_scm_release_gate_decision_plan()
    assert set(REQUIRED_EMPIRICAL_EVIDENCE_BEFORE_APPROVAL).issubset(set(plan.required_empirical_evidence))
    for reason in BLOCKED_APPROVAL_REASONS:
        assert reason in plan.blocked_approval_reasons


def test_input_and_decision_contract_fields() -> None:
    plan = build_scm_release_gate_decision_plan()
    for field in DECISION_PLAN_FIELDS:
        assert hasattr(plan, field)
    assert len(INPUT_FIELDS) == 15


def test_no_authorization_granted() -> None:
    plan = build_scm_release_gate_decision_plan()
    assert _SCM_FLAGS["scm_release_gate_approval_granted"] is False
    for flag in _AUTH_FLAGS:
        assert plan.authorization_flags[flag] is False


def test_portfolio_methods_not_authorized() -> None:
    plan = build_scm_release_gate_decision_plan()
    assert plan.authorization_flags["augsynth_production_inference_authorized"] is False
    assert plan.authorization_flags["tbrridge_production_inference_authorized"] is False
    assert plan.authorization_flags["bayesian_tbr_production_inference_authorized"] is False


def test_validate_plan() -> None:
    plan = build_scm_release_gate_decision_plan()
    result = validate_scm_release_gate_decision_plan(plan)
    assert result["valid"]
    assert result["all_decision_options_present"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_DECISION_PLAN_001"
    assert data["failed_scenarios"] == []
    assert data["recommended_decision_direction"] == "defer_pending_empirical_validation"
    assert data["planned_closeout_direction"] == "closeout_as_reference_candidate"
    assert data["portfolio_handoff_recommendation"] == "handoff_to_method_portfolio"
    assert data["scm_release_gate_approval_granted"] is False
    assert data["scm_release_gate_decision_plan_completed"] is False
    assert data["planned_input_contract"] == INPUT_CONTRACT
    assert data["final_verdict"] == "scm_release_gate_decision_plan_defined_defer_no_authorization_granted"
    assert data["next_artifact"] == "SCM_PRODUCTION_CANDIDATE_CLOSEOUT_AND_METHOD_PORTFOLIO_HANDOFF_001"
    assert data["method_portfolio_handoff_targets"] == list(METHOD_PORTFOLIO_HANDOFF_TARGETS)


def test_report_states_decision_plan_not_approval() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "decision plan" in text.lower()
    assert "not a release-gate decision" in text.lower() or "not a release-gate approval" in text.lower()
    assert "defer_pending_empirical_validation" in text.lower() or "defer pending empirical validation" in text.lower()
    assert "reference candidate" in text.lower()
    assert "augsynth" in text.lower()
