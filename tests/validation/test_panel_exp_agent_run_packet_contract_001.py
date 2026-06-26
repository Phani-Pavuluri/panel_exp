"""Tests for PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.panel_exp_agent_run_packet_contract_001 import (
    ALLOWED_ACTIONS,
    BLOCKED_ACTIONS,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_CONTRACTS,
    REVISED_ROADMAP_SEQUENCE,
    SCENARIO_TESTS,
    _AUTH_FLAGS,
    build_panel_exp_agent_run_packet_contract,
    build_scenarios,
    run_validation,
    validate_panel_exp_agent_run_packet_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001_REPORT.md"


def test_packet_first_principles() -> None:
    contract = build_panel_exp_agent_run_packet_contract()
    assert contract.packet_first_agent_second
    assert contract.tool_first_explanation_second
    assert contract.no_packet_no_agent_run
    assert contract.no_manifest_no_agent_execution_claim
    assert contract.no_artifact_reference_no_report_claim
    assert contract.no_validation_report_no_validation_pass_claim
    assert contract.no_failure_packet_no_hidden_failure


def test_required_contracts() -> None:
    contract = build_panel_exp_agent_run_packet_contract()
    assert contract.required_contracts == REQUIRED_CONTRACTS
    assert "PanelExpAgentInputPacket" in contract.required_contracts
    assert "PanelExpAgentRunManifest" in contract.required_contracts
    assert "PanelExpAgentFailurePacket" in contract.required_contracts


def test_allowed_and_blocked_actions() -> None:
    contract = build_panel_exp_agent_run_packet_contract()
    assert contract.allowed_actions == ALLOWED_ACTIONS
    assert contract.blocked_actions == BLOCKED_ACTIONS
    assert "authorize_production_design" in contract.blocked_actions
    assert "authorize_p_value" in contract.blocked_actions
    assert "run_diagnostic" in contract.allowed_actions


def test_revised_roadmap_sequence() -> None:
    contract = build_panel_exp_agent_run_packet_contract()
    assert contract.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001")
    assert contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT


def test_all_authorization_flags_false() -> None:
    contract = build_panel_exp_agent_run_packet_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_panel_exp_agent_run_packet_contract()
    result = validate_panel_exp_agent_run_packet_contract(contract)
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
    assert data["artifact_id"] == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["packet_first_agent_second"] is True
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["final_verdict"] == "panel_exp_agent_run_packet_contract_defined_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "packet-first" in text.lower() or "packet first" in text.lower()
    assert "run manifest" in text.lower()
    assert len(SCENARIO_TESTS) >= 20
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
