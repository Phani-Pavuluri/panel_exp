"""Tests for EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.experiment_portfolio_intake_contract_001 import (
    DATA_REQUEST_ORDER,
    NEW_CROSS_CUTTING_CONTRACTS,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_OUTPUT_CONTRACTS,
    REVISED_ROADMAP_SEQUENCE,
    SCENARIO_TESTS,
    SUPPORTED_INTAKE_BRANCHES,
    _AUTH_FLAGS,
    build_experiment_portfolio_intake_contract,
    build_scenarios,
    run_validation,
    validate_experiment_portfolio_intake_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001_REPORT.md"


def test_adaptive_intake_no_static_questionnaire() -> None:
    contract = build_experiment_portfolio_intake_contract()
    assert contract.adaptive_intake
    assert not contract.static_questionnaire_allowed


def test_supported_branches_and_output_contracts() -> None:
    contract = build_experiment_portfolio_intake_contract()
    assert contract.supported_intake_branches == SUPPORTED_INTAKE_BRANCHES
    assert contract.required_output_contracts == REQUIRED_OUTPUT_CONTRACTS
    assert "ExperimentPortfolioPlanningIntent" in contract.required_output_contracts
    assert "IntakeRoutingDecision" in contract.required_output_contracts


def test_data_request_order() -> None:
    contract = build_experiment_portfolio_intake_contract()
    assert contract.data_request_order == DATA_REQUEST_ORDER
    assert contract.data_request_order[0] == "full_geo_kpi_spend_panel"


def test_no_feasibility_or_inference_from_intake() -> None:
    contract = build_experiment_portfolio_intake_contract()
    assert not contract.design_feasibility_authorized_from_intake
    assert not contract.p_values_or_cis_authorized_from_intake


def test_cross_cutting_contracts_in_roadmap() -> None:
    contract = build_experiment_portfolio_intake_contract()
    assert contract.new_cross_cutting_contracts_added_to_roadmap == NEW_CROSS_CUTTING_CONTRACTS
    idx = contract.revised_roadmap_sequence.index("EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001")
    assert contract.revised_roadmap_sequence[idx + 1] == "PANEL_EXP_AGENT_RUN_PACKET_CONTRACT_001"


def test_revised_roadmap_sequence() -> None:
    contract = build_experiment_portfolio_intake_contract()
    assert contract.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    assert len(contract.revised_roadmap_sequence) == 24


def test_all_authorization_flags_false() -> None:
    contract = build_experiment_portfolio_intake_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_experiment_portfolio_intake_contract()
    result = validate_experiment_portfolio_intake_contract(contract)
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
    assert data["artifact_id"] == "EXPERIMENT_PORTFOLIO_INTAKE_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["static_questionnaire_allowed"] is False
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["final_verdict"] == "experiment_portfolio_intake_contract_defined_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "adaptive" in text.lower()
    assert "ballpark" in text.lower()
    assert len(SCENARIO_TESTS) >= 15
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
