"""Tests for PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.panel_exp_golden_path_acceptance_tests_001 import (
    BLOCKED_PROVISIONAL_SCENARIOS,
    GOLDEN_PATH_SCENARIOS,
    RECOMMENDED_NEXT_ARTIFACT,
    REQUIRED_CONTRACTS,
    REQUIRED_OUTPUT_ARTIFACT_CATEGORIES,
    REVISED_ROADMAP_SEQUENCE,
    SCENARIO_TESTS,
    _AUTH_FLAGS,
    build_panel_exp_golden_path_acceptance_tests_contract,
    build_scenarios,
    run_validation,
    validate_panel_exp_golden_path_acceptance_tests_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001_summary.json"
_REPORT = _REPO / "docs/track_d/PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001_REPORT.md"


def test_golden_path_principles() -> None:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    assert contract.golden_paths_before_demos
    assert contract.blocked_paths_before_production_claims
    assert contract.happy_paths_require_paired_failure_or_provisional_paths
    assert not contract.production_authorization_from_golden_paths
    assert not contract.fixtures_define_product_branches
    assert not contract.report_builders_may_perform_hidden_inference
    assert not contract.llm_may_infer_from_raw_fixture_or_raw_data


def test_required_contracts() -> None:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    assert contract.required_contracts == REQUIRED_CONTRACTS
    assert "PanelExpGoldenPathScenario" in contract.required_contracts
    assert "PanelExpGoldenPathRegressionSuite" in contract.required_contracts
    assert "PanelExpReportBuilderBoundary" in contract.required_contracts


def test_golden_and_blocked_scenarios() -> None:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    assert contract.golden_path_scenarios == GOLDEN_PATH_SCENARIOS
    assert contract.blocked_provisional_scenarios == BLOCKED_PROVISIONAL_SCENARIOS
    assert len(contract.golden_path_scenarios) == 8
    assert len(contract.blocked_provisional_scenarios) == 18
    assert contract.required_output_artifact_categories == REQUIRED_OUTPUT_ARTIFACT_CATEGORIES


def test_revised_roadmap_sequence() -> None:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    assert contract.revised_roadmap_sequence == REVISED_ROADMAP_SEQUENCE
    idx = contract.revised_roadmap_sequence.index("PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001")
    assert contract.revised_roadmap_sequence[idx + 1] == RECOMMENDED_NEXT_ARTIFACT


def test_all_authorization_flags_false() -> None:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected


def test_validate_contract() -> None:
    contract = build_panel_exp_golden_path_acceptance_tests_contract()
    result = validate_panel_exp_golden_path_acceptance_tests_contract(contract)
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
    assert data["artifact_id"] == "PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001"
    assert data["failed_scenarios"] == []
    assert data["golden_paths_before_demos"] is True
    assert data["recommended_next_artifact"] == RECOMMENDED_NEXT_ARTIFACT
    assert data["final_verdict"] == "panel_exp_golden_path_acceptance_tests_defined_no_runtime_authorization"


def test_report_states_no_runtime_authorization() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "golden path" in text.lower() or "golden-path" in text.lower()
    assert "anti-pattern" in text.lower()
    assert len(SCENARIO_TESTS) >= 20
    assert "no runtime authorization" in text.lower() or "no runtime" in text.lower()
