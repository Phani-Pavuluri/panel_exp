"""Tests for SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.spend_requirement_and_manipulation_feasibility_contract_001 import (
    AMENDS_OR_SUPERSEDES,
    BASELINE_INVENTORY_FIELDS,
    CONTROL_CONTAMINATION_FLAGS,
    FUTURE_IMPLEMENTATION_TESTS,
    RECOMMENDED_NEXT_ARTIFACT,
    RESPONSE_BRIDGE_SOURCES,
    SUBREPORTS,
    SUPPORTED_MANIPULATION_OPTIONS,
    _AUTH_FLAGS,
    build_scenarios,
    build_spend_requirement_and_manipulation_feasibility_contract,
    run_validation,
    validate_spend_requirement_and_manipulation_feasibility_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO / "docs/track_d/archives/SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001_REPORT.md"


def test_five_subreports_defined() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert contract.subreports == SUBREPORTS
    assert "BaselineSpendInventoryReport" in contract.subreports
    assert "ResponseBridgeReport" in contract.subreports


def test_manipulation_options_include_dosage() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert "DOSAGE_CONTRAST" in contract.supported_manipulation_options
    assert "DIFFERENCE_IN_POLICY" in contract.supported_manipulation_options
    assert contract.dosage_contrast_first_class_option


def test_response_bridge_sources() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert contract.response_bridge_sources == RESPONSE_BRIDGE_SOURCES
    assert "MMM_RESPONSE_CURVE" in contract.response_bridge_sources
    assert "BACK_OF_NAPKIN_USER_ASSUMPTION" in contract.response_bridge_sources


def test_two_spend_concepts_and_advisory_only() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert contract.two_required_spend_concepts_defined
    assert contract.kpi_mde_to_spend_bridge_advisory_only
    assert contract.mmm_proxy_use_advisory_only


def test_baseline_and_historical_support() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert contract.baseline_spend_derivation_defined
    assert contract.required_heavy_up_multiplier_defined
    assert contract.historical_support_check_defined
    assert "max_reducible_spend" in BASELINE_INVENTORY_FIELDS


def test_control_contamination_and_estimand_shift() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert contract.control_contamination_warning_defined
    assert contract.estimand_shift_flag_defined
    assert "ESTIMAND_SHIFT_REQUIRED" in CONTROL_CONTAMINATION_FLAGS


def test_amends_prior_contract() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    assert contract.amends_or_supersedes == AMENDS_OR_SUPERSEDES


def test_all_authorization_flags_false() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_spend_requirement_and_manipulation_feasibility_contract()
    result = validate_spend_requirement_and_manipulation_feasibility_contract(contract)
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
    assert data["artifact_id"] == "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["amends_or_supersedes"] == AMENDS_OR_SUPERSEDES
    assert data["dosage_contrast_first_class_option"] is True
    assert data["runtime_spend_diagnostics_implemented"] is False
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert (
        data["final_verdict"]
        == "spend_requirement_and_manipulation_feasibility_contract_defined_no_runtime_diagnostics_or_production_authorization"
    )


def test_future_tests_listed() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 20
    assert "mmm_out_of_support_flagged" in FUTURE_IMPLEMENTATION_TESTS


def test_report_covers_expanded_scope() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "dosage" in text.lower()
    assert "response bridge" in text.lower() or "responsebridge" in text.lower().replace(" ", "")
    assert "baseline" in text.lower()
    assert "no runtime" in text.lower() or "contract only" in text.lower()
