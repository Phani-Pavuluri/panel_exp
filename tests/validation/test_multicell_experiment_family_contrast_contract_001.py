"""Tests for MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.multicell_experiment_family_contrast_contract_001 import (
    ALLOWED_SURFACES,
    CONDITIONAL_SURFACES,
    CONTRACT_POSITIVE_FLAGS,
    CONTRAST_TYPES,
    EXPERIMENT_FAMILY_TYPES,
    FAILURE_CODES,
    FUTURE_RUNTIME_TESTS,
    PROHIBITED_SURFACES_UNLESS_GOVERNED,
    _AUTH_FLAGS,
    _VERDICT,
    build_multicell_experiment_family_contrast_contract,
    build_scenarios,
    evaluate_readout_surface,
    get_multicell_experiment_family_contrast_contract_metadata,
    list_contrast_types,
    list_experiment_family_types,
    list_future_runtime_tests,
    run_validation,
    validate_multicell_experiment_family_contrast_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001_REPORT.md"


def test_contract_metadata_exists() -> None:
    meta = get_multicell_experiment_family_contrast_contract_metadata()
    assert meta["artifact_id"] == "MULTICELL_EXPERIMENT_FAMILY_AND_CONTRAST_CONTRACT_001"
    assert meta["experiment_family_taxonomy_defined"] is True


def test_experiment_family_taxonomy_includes_independent_and_related() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert "INDEPENDENT_EXPERIMENTS" in contract.experiment_family_types
    assert "RELATED_PARALLEL_ARMS" in contract.experiment_family_types
    assert "SHARED_CONTROL_MULTI_ARM" in contract.experiment_family_types
    assert list_experiment_family_types() == EXPERIMENT_FAMILY_TYPES


def test_independent_experiment_exemption_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.independent_experiment_exemption_defined is True
    rules = contract.family_applicability_rules["INDEPENDENT_EXPERIMENTS"]
    assert rules["multiplicity_required"] is False
    assert rules["shared_covariance_required"] is False
    result = evaluate_readout_surface(
        "INDEPENDENT_EXPERIMENTS",
        "STANDALONE_ARM_READOUT",
        evidence={
            "arm_identity": True,
            "estimand_definition": True,
            "execution_readout_evidence": True,
        },
    )
    assert result.authorized is True


def test_contrast_taxonomy_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.contrast_taxonomy_defined is True
    assert "ARM_VS_CONTROL" in contract.contrast_types
    assert "PORTFOLIO_RANKING" in contract.contrast_types
    assert list_contrast_types() == CONTRAST_TYPES


def test_applicability_rules_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.multiplicity_applicability_rules_defined is True
    assert contract.family_applicability_rules["RELATED_PARALLEL_ARMS"]["multiplicity_required"] is True
    assert contract.family_applicability_rules["POOLED_AGGREGATE_FAMILY"]["standalone_readout_allowed"] is False


def test_shared_control_covariance_requirements_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.shared_control_covariance_requirements_defined is True
    blocked = evaluate_readout_surface(
        "SHARED_CONTROL_MULTI_ARM",
        "ARM_COMPARISON",
        evidence={
            "contrast_definition": True,
            "shared_experiment_family": True,
            "comparable_metrics": True,
            "multiplicity_policy": True,
        },
    )
    assert blocked.authorized is False
    assert "shared_control_covariance_semantics" in blocked.missing_evidence


def test_pooled_global_surface_rules_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.pooled_global_surface_rules_defined is True
    blocked = evaluate_readout_surface(
        "RELATED_PARALLEL_ARMS",
        "POOLED_EFFECT_SUMMARY",
        evidence={"pooling_weights": True},
    )
    assert blocked.authorized is False


def test_winner_scale_claim_blocking_rules_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.winner_claim_blocking_rules_defined is True
    assert "WINNER_CLAIM" in contract.prohibited_surfaces_unless_governed
    winner = evaluate_readout_surface("RELATED_PARALLEL_ARMS", "WINNER_CLAIM")
    assert winner.authorized is False
    assert winner.failure_code == "WINNER_CLAIM_BLOCKED"
    budget = evaluate_readout_surface("PORTFOLIO_DECISION_FAMILY", "SCALE_BUDGET_CLAIM")
    assert budget.authorized is False
    assert budget.failure_code == "BUDGET_SCALE_CLAIM_BLOCKED"


def test_future_runtime_tests_documented() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.future_runtime_tests_documented is True
    assert list_future_runtime_tests() == FUTURE_RUNTIME_TESTS
    assert "preserves_standalone_readout_eligibility_for_independent_experiments" in contract.future_runtime_tests


def test_summary_json_matches_contract() -> None:
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    contract = build_multicell_experiment_family_contrast_contract()
    assert data["artifact_id"] == contract.artifact_id
    assert data["final_verdict"] == contract.final_verdict
    assert data["failed_scenarios"] == []
    assert data["recommended_next_artifact"] == contract.recommended_next_artifact


def test_forbidden_computation_authorization_flags_false() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_multicell_experiment_family_contrast_contract_metadata()
    assert meta["runtime_implemented"] is False
    assert meta["winner_claim_authorized"] is False


def test_contract_validation_passes() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    result = validate_multicell_experiment_family_contrast_contract(contract)
    assert result["valid"] is True
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    assert failed == []


def test_report_doc_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert "independent experiments are exempt" in text.lower()
    assert "INDEPENDENT_EXPERIMENTS" in text


def test_run_validation_verdict() -> None:
    result = run_validation(write_summary=False)
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []


def test_allowed_and_conditional_surfaces_complete() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.conditional_surfaces == CONDITIONAL_SURFACES
    assert contract.prohibited_surfaces_unless_governed == PROHIBITED_SURFACES_UNLESS_GOVERNED


def test_failure_codes_complete() -> None:
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.failure_codes == FAILURE_CODES
    assert "UNKNOWN_EXPERIMENT_FAMILY" in contract.failure_codes


def test_positive_flags_true() -> None:
    for key, val in CONTRACT_POSITIVE_FLAGS.items():
        assert val is True
    contract = build_multicell_experiment_family_contrast_contract()
    assert contract.experiment_family_taxonomy_defined is True
