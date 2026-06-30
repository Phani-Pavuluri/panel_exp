"""Tests for POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.power_mde_diagnostics_lane_contract_001 import (
    DEPENDS_ON,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_INPUT_CONTRACTS,
    FUTURE_OUTPUT_CONTRACTS,
    FUTURE_RUNTIME_MODES,
    FUTURE_STATUSES,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    RESPONSE_BRIDGE_FLAGS_TO_PRESERVE,
    _AUTH_FLAGS,
    build_power_mde_diagnostics_lane_contract,
    build_scenarios,
    run_validation,
    validate_power_mde_diagnostics_lane_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001_REPORT.md"


def test_future_statuses_defined() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.future_statuses == FUTURE_STATUSES
    assert "POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME" in contract.future_statuses
    assert "POWER_MDE_BLOCKED_BY_SPEND_HANDOFF" in contract.future_statuses


def test_runtime_modes_defined() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.future_runtime_modes == FUTURE_RUNTIME_MODES
    assert "KPI_ONLY_SENSITIVITY" in contract.future_runtime_modes
    assert "DOSAGE_CONTRAST_SENSITIVITY" in contract.future_runtime_modes


def test_readiness_gates_defined() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert "profiler_gate" in contract.readiness_gates
    assert "spend_handoff_gate" in contract.readiness_gates


def test_lane_boundary_and_mde_representation() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.power_mde_lane_contract_defined
    assert contract.spend_handoff_dependency_defined
    assert contract.kpi_mde_representation_defined
    assert contract.absolute_relative_mde_separation_defined
    assert contract.cell_aggregate_mde_separation_defined


def test_noise_cell_structure_and_dosage() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.noise_history_requirements_defined
    assert contract.cell_structure_requirements_defined
    assert contract.dosage_sensitivity_mode_defined
    assert contract.control_contamination_preservation_defined


def test_response_bridge_and_business_risk() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.response_bridge_provenance_preservation_defined
    assert contract.business_response_risk_preservation_defined
    assert "BUSINESS_RESPONSE_RISK" in RESPONSE_BRIDGE_FLAGS_TO_PRESERVE


def test_future_input_output_contracts() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert contract.future_input_contracts == FUTURE_INPUT_CONTRACTS
    assert contract.future_output_contracts == FUTURE_OUTPUT_CONTRACTS
    assert "PowerMdeDiagnosticsInput" in contract.future_input_contracts
    assert "PowerMdeReadinessReport" in contract.future_output_contracts


def test_depends_on_handoff_contract() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    assert "POWER_MDE_REQUIREMENT_AND_SPEND_FEASIBILITY_HANDOFF_CONTRACT_001" in contract.depends_on
    assert contract.depends_on == DEPENDS_ON


def test_all_authorization_flags_false() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_power_mde_diagnostics_lane_contract()
    result = validate_power_mde_diagnostics_lane_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_listed() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 14
    assert "ready_for_runtime_status_does_not_set_powered_design_roi_production_flags" in FUTURE_IMPLEMENTATION_TESTS


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "POWER_MDE_DIAGNOSTICS_LANE_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["power_mde_lane_contract_defined"] is True
    assert data["runtime_power_mde_diagnostics_implemented"] is False
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["final_verdict"] == (
        "power_mde_diagnostics_lane_contract_defined_no_runtime_power_mde_or_production_authorization"
    )


def test_report_covers_lane_boundary() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "POWER_MDE_READY_FOR_DIAGNOSTIC_RUNTIME" in text
    assert "does not mean powered" in text.lower() or "not powered" in text.lower()
    assert "dosage" in text.lower()
    assert "KPI_ONLY_SENSITIVITY" in text
    assert "profiler gate" in text.lower() or "profiler_gate" in text.lower()
