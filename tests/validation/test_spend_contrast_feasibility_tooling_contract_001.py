"""Tests for SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.spend_contrast_feasibility_tooling_contract_001 import (
    CLAIM_BOUNDARIES,
    DEPENDS_ON,
    FAILURE_PROVISIONAL_MODES,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONTRACTS,
    RECOMMENDED_NEXT_ARTIFACT,
    SPEND_CONTRAST_QUALITIES,
    SPEND_CONTRAST_STATUSES,
    SUPPORTED_MANIPULATION_TYPES,
    ZERO_MISSING_RULES,
    _AUTH_FLAGS,
    build_scenarios,
    build_spend_contrast_feasibility_tooling_contract,
    run_validation,
    validate_spend_contrast_feasibility_tooling_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001_REPORT.md"


def test_supported_manipulation_types() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    assert contract.supported_manipulation_types == SUPPORTED_MANIPULATION_TYPES
    assert "GO_DARK" in contract.supported_manipulation_types
    assert "BUDGET_REALLOCATION" in contract.supported_manipulation_types


def test_distinctions_defined() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    assert contract.spend_coverage_vs_contrast_distinction_defined
    assert contract.planned_vs_observed_spend_distinction_defined
    assert contract.zero_vs_missing_spend_rules_defined


def test_future_output_contracts() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    assert contract.future_output_contracts == FUTURE_OUTPUT_CONTRACTS
    assert "SpendContrastFeasibilityReport" in contract.future_output_contracts


def test_status_and_quality_taxonomy() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    assert contract.spend_contrast_statuses == SPEND_CONTRAST_STATUSES
    assert contract.spend_contrast_qualities == SPEND_CONTRAST_QUALITIES
    assert contract.claim_boundaries == CLAIM_BOUNDARIES


def test_claim_boundaries_no_runtime() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    assert not contract.sample_schema_mode_final_contrast_readiness_allowed
    assert not contract.ballpark_mode_final_contrast_readiness_allowed
    assert contract.llm_explanation_boundary_defined
    assert contract.report_builder_boundary_defined


def test_failure_modes_listed() -> None:
    assert len(FAILURE_PROVISIONAL_MODES) >= 10
    assert "missing_spend_column_when_contrast_requested" in FAILURE_PROVISIONAL_MODES
    assert "ballpark_mode_overclaim" in FAILURE_PROVISIONAL_MODES


def test_future_implementation_tests_listed() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 15
    assert "go_dark_directionally_compatible_contrast" in FUTURE_IMPLEMENTATION_TESTS
    assert "no_fixture_specific_branching" in FUTURE_IMPLEMENTATION_TESTS


def test_all_authorization_flags_false() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_spend_contrast_feasibility_tooling_contract()
    result = validate_spend_contrast_feasibility_tooling_contract(contract)
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
    assert data["artifact_id"] == "SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["runtime_spend_diagnostics_implemented"] is False
    assert data["budget_reallocation_engine_implemented"] is False
    assert data["depends_on"] == list(DEPENDS_ON)
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert (
        data["final_verdict"]
        == "spend_contrast_feasibility_tooling_contract_defined_no_runtime_diagnostics_or_production_authorization"
    )


def test_report_states_no_runtime_diagnostics() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "go-dark" in text.lower() or "go_dark" in text.lower()
    assert "spend coverage" in text.lower()
    assert "no runtime" in text.lower() or "contract only" in text.lower()
    assert "control-plane" in text.lower() or "llm" in text.lower()
