"""Tests for EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.experiment_portfolio_planner_agent_roadmap_001 import (
    DESIGN_OPTIONS,
    FIRST_PLANNER_LANE_ARTIFACT,
    PLANNED_AGENTS,
    PRODUCT_PRINCIPLE,
    READOUT_TIERS,
    RECOMMENDED_NEXT_ARTIFACT,
    REVISED_ROADMAP_SEQUENCE,
    SPEND_MANIPULATION_TYPES,
    _AUTH_FLAGS,
    build_experiment_portfolio_planner_agent_roadmap,
    build_scenarios,
    run_validation,
    validate_experiment_portfolio_planner_agent_roadmap,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001_summary.json"
_REPORT = _REPO / "docs/track_d/EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001_REPORT.md"


def test_product_principle_present() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.product_principle == PRODUCT_PRINCIPLE


def test_adaptive_intake_and_data_first() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.adaptive_intake_not_static_questionnaire
    assert roadmap.data_first_planning


def test_all_planned_agents_present() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.planned_agents == PLANNED_AGENTS
    assert len(roadmap.planned_agents) == 9


def test_readout_tiers_and_design_options() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.readout_tiers == READOUT_TIERS
    assert roadmap.design_options == DESIGN_OPTIONS
    assert "shared_control_multi_arm_design" in roadmap.design_options
    assert "mutually_exclusive_multi_arm_design" in roadmap.design_options
    assert "rotating_staggered_design_restricted" in roadmap.design_options


def test_spend_manipulation_types() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.spend_manipulation_types == SPEND_MANIPULATION_TYPES


def test_revised_roadmap_sequence() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    assert roadmap.revised_roadmap_sequence[3] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"
    assert roadmap.revised_roadmap_sequence[-1] == "AUGSYNTH_ASCM_REMEDIATION_IMPLEMENTATION_001"


def test_design_selection_before_estimator() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.design_selection_before_estimator_selection


def test_all_authorization_flags_false() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    for flag, expected in _AUTH_FLAGS.items():
        assert roadmap.authorization_flags[flag] is expected


def test_recommended_next_and_planner_lane() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    assert roadmap.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert roadmap.first_planner_lane_artifact == FIRST_PLANNER_LANE_ARTIFACT


def test_validate_roadmap() -> None:
    roadmap = build_experiment_portfolio_planner_agent_roadmap()
    result = validate_experiment_portfolio_planner_agent_roadmap(roadmap)
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
    assert data["artifact_id"] == "EXPERIMENT_PORTFOLIO_PLANNER_AGENT_ROADMAP_001"
    assert data["failed_scenarios"] == []
    assert data["product_principle"] == PRODUCT_PRINCIPLE
    assert data["first_planner_lane_artifact"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
    assert data["final_verdict"] == "experiment_portfolio_planner_agent_roadmap_defined_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "design selection" in text.lower() or "design selection comes before" in text.lower()
    assert "adaptive" in text.lower()
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
    assert "mutually exclusive" in text.lower()
    assert "shared-control" in text.lower() or "shared control" in text.lower()
