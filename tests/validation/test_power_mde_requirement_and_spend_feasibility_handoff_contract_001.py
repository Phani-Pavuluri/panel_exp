"""Tests for POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.power_mde_requirement_and_spend_feasibility_handoff_contract_001 import (
    DEPENDS_ON,
    FUTURE_HANDOFF_STATUSES,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONTRACTS,
    RECOMMENDED_NEXT_ARTIFACT,
    RESPONSE_BRIDGE_FLAGS_TO_PRESERVE,
    RESPONSE_BRIDGE_SOURCES,
    _AUTH_FLAGS,
    build_power_mde_spend_feasibility_handoff_contract,
    build_scenarios,
    run_validation,
    validate_power_mde_spend_feasibility_handoff_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001_REPORT.md"


def test_handoff_statuses_defined() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    assert contract.future_handoff_statuses == FUTURE_HANDOFF_STATUSES
    assert "SPEND_HANDOFF_READY_FOR_POWER_DIAGNOSTICS" in contract.future_handoff_statuses
    assert "SPEND_HANDOFF_REQUIRES_DOSAGE_ESTIMAND_REVIEW" in contract.future_handoff_statuses


def test_spend_to_power_boundary() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    assert contract.handoff_contract_defined
    assert contract.spend_to_power_boundary_defined
    assert contract.kpi_mde_units_preserved
    assert contract.required_spend_delta_source_preserved


def test_response_bridge_provenance() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    assert contract.response_bridge_provenance_required
    assert contract.business_response_risk_preserved
    assert "MMM_RESPONSE_CURVE" in RESPONSE_BRIDGE_SOURCES
    assert "BUSINESS_RESPONSE_RISK" in RESPONSE_BRIDGE_FLAGS_TO_PRESERVE


def test_dosage_and_control_handoff() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    assert contract.dosage_handoff_boundary_defined
    assert contract.control_contamination_flags_preserved
    assert contract.method_suitability_review_required_for_dosage


def test_future_output_contracts() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    assert contract.future_output_contracts == FUTURE_OUTPUT_CONTRACTS
    assert "PowerMdeSpendFeasibilityHandoffReport" in contract.future_output_contracts


def test_depends_on_spend_diagnostics() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    assert "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001" in contract.depends_on
    assert contract.depends_on == DEPENDS_ON


def test_all_authorization_flags_false() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_power_mde_spend_feasibility_handoff_contract()
    result = validate_power_mde_spend_feasibility_handoff_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_listed() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 12
    assert "ready_handoff_does_not_set_powered_design_roi_production_flags" in FUTURE_IMPLEMENTATION_TESTS


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["handoff_contract_defined"] is True
    assert data["runtime_power_diagnostics_implemented"] is False
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["final_verdict"] == (
        "power_mde_requirement_spend_feasibility_handoff_contract_defined_no_power_mde_or_production_authorization"
    )


def test_report_covers_handoff_boundary() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "ready_for_downstream_power_diagnostics" in text.lower()
    assert "does not mean powered" in text.lower() or "not powered" in text.lower()
    assert "dosage" in text.lower()
    assert "business-response risk" in text.lower() or "business_response_risk" in text.lower()
