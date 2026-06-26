"""Tests for EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.experiment_portfolio_planner_agent_tooling_contract_001 import (
    AGENT_TOOLING,
    ANSWERABILITY_MATRIX,
    CORE_PRINCIPLE,
    PLANNED_AGENTS,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_READINESS_GATES,
    REQUIRED_REPORT_TYPES,
    REVISED_ROADMAP_SEQUENCE,
    SCENARIO_TESTS_REQUIRED,
    _AUTH_FLAGS,
    build_experiment_portfolio_planner_agent_tooling_contract,
    build_scenarios,
    run_validation,
    validate_experiment_portfolio_planner_agent_tooling_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001_REPORT.md"


def test_tool_first_agent_second() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.core_principle == CORE_PRINCIPLE


def test_no_tool_no_claim_rule() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.no_tool_no_claim_rule
    assert contract.llm_may_explain_but_not_invent_diagnostics


def test_all_planned_agents_and_tooling() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.planned_agents == PLANNED_AGENTS
    for agent in PLANNED_AGENTS:
        assert agent in AGENT_TOOLING


def test_required_report_types() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.required_report_types == REQUIRED_REPORT_TYPES
    assert "PortfolioFeasibilityReport" in contract.required_report_types
    assert "ClaimBoundaryReport" in contract.required_report_types


def test_answerability_matrix_and_readiness_gates() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.answerability_matrix_defined
    assert len(ANSWERABILITY_MATRIX) >= 9
    assert contract.required_readiness_gates == REQUIRED_READINESS_GATES


def test_scenario_tests_listed() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.scenario_tests_required
    assert len(SCENARIO_TESTS_REQUIRED) >= 16


def test_revised_roadmap_sequence() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    assert contract.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001")
    assert contract.revised_roadmap_sequence[idx + 1] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"


def test_all_authorization_flags_false() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_experiment_portfolio_planner_agent_tooling_contract()
    result = validate_experiment_portfolio_planner_agent_tooling_contract(contract)
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
    assert data["artifact_id"] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_TOOLING_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["core_principle"] == "tool_first_agent_second"
    assert data["no_tool_no_claim_rule"] is True
    assert data["recommended_next_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
    assert data["final_verdict"] == "experiment_portfolio_planner_agent_tooling_contract_defined_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "tool-first" in text.lower() or "tool first" in text.lower()
    assert "no-tool-no-claim" in text.lower() or "no tool" in text.lower()
    assert "answerability" in text.lower()
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
