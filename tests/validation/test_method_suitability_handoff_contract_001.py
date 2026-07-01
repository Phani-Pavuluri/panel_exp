"""Tests for METHOD_SUITABILITY_HANDOFF_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_suitability_handoff_contract_001 import (
    ALTERNATIVE_NEXT_ARTIFACT,
    CONTRACT_EXAMPLES,
    DEPENDS_ON,
    FUTURE_HANDOFF_STATUSES,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_METHOD_FAMILY_REVIEW_TARGETS,
    FUTURE_REVIEW_REQUIREMENT_TYPES,
    HANDOFF_PACKET_FIELDS,
    INPUT_DEPENDENCIES,
    READINESS_GATES,
    RECOMMENDED_NEXT_ARTIFACT,
    _AUTH_FLAGS,
    build_method_suitability_handoff_contract,
    build_scenarios,
    run_validation,
    validate_method_suitability_handoff_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_SUITABILITY_HANDOFF_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_SUITABILITY_HANDOFF_CONTRACT_001_REPORT.md"


def test_handoff_statuses_defined() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.future_handoff_statuses == FUTURE_HANDOFF_STATUSES
    assert "METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW" in contract.future_handoff_statuses
    assert "METHOD_HANDOFF_BLOCKED_BY_MISSING_ESTIMAND" in contract.future_handoff_statuses


def test_review_requirement_types_defined() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.future_review_requirement_types == FUTURE_REVIEW_REQUIREMENT_TYPES
    assert "DOSAGE_CONTRAST_REVIEW" in contract.future_review_requirement_types
    assert "DIFFERENCE_IN_POLICY_REVIEW" in contract.future_review_requirement_types
    assert "BUDGET_REALLOCATION_REVIEW" in contract.future_review_requirement_types


def test_method_family_review_targets_defined() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.future_method_family_review_targets == FUTURE_METHOD_FAMILY_REVIEW_TARGETS
    assert "SCM_FAMILY" in contract.future_method_family_review_targets
    assert "TBR_RIDGE_FAMILY" in contract.future_method_family_review_targets
    assert "UNKNOWN_METHOD_FAMILY" in contract.future_method_family_review_targets


def test_contract_semantics() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.method_suitability_handoff_contract_defined
    assert contract.method_handoff_packet_defined
    assert contract.estimand_handoff_defined
    assert contract.design_summary_handoff_defined
    assert contract.scenario_summary_handoff_defined
    assert contract.assignment_summary_handoff_defined
    assert contract.power_mde_summary_handoff_defined
    assert contract.spend_summary_handoff_defined
    assert contract.governance_summary_handoff_defined
    assert contract.review_requirement_types_defined
    assert contract.method_family_review_targets_defined


def test_readiness_gates_count() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 11
    assert contract.readiness_gates[0] == "profiler_data_readiness_gate"
    assert contract.readiness_gates[-1] == "method_suitability_handoff_packet_gate"


def test_handoff_packet_fields() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.handoff_packet_fields == HANDOFF_PACKET_FIELDS
    assert "handoff_status" in contract.handoff_packet_fields
    assert "candidate_method_family_review_targets" in contract.handoff_packet_fields
    assert "review_requirements" in contract.handoff_packet_fields


def test_input_dependencies_include_assignment_runtime() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.input_dependencies == INPUT_DEPENDENCIES
    assert "design_assignment_feasibility_report" in contract.input_dependencies
    assert "estimand_labels" in contract.input_dependencies
    assert contract.depends_on == DEPENDS_ON
    assert "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001" in contract.depends_on


def test_contract_examples_count() -> None:
    contract = build_method_suitability_handoff_contract()
    assert len(contract.contract_examples) == 8
    assert contract.contract_examples == CONTRACT_EXAMPLES


def test_all_authorization_flags_false() -> None:
    contract = build_method_suitability_handoff_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["method_family_selected"]
    assert not contract.authorization_flags["estimator_selected"]
    assert not contract.authorization_flags["runtime_method_suitability_implemented"]


def test_validate_contract() -> None:
    contract = build_method_suitability_handoff_contract()
    result = validate_method_suitability_handoff_contract(contract)
    assert result["valid"]


def test_harness_scenarios_pass() -> None:
    scenarios = build_scenarios()
    failed = [s for s in scenarios if not s["passed"]]
    assert not failed, failed


def test_future_tests_include_method_handoff_cases() -> None:
    assert len(FUTURE_IMPLEMENTATION_TESTS) >= 20
    assert "method_family_review_targets_not_selected_methods" in FUTURE_IMPLEMENTATION_TESTS
    assert "assignment_ready_does_not_mean_method_ready" in FUTURE_IMPLEMENTATION_TESTS
    assert "no_estimator_inference_authorization" in FUTURE_IMPLEMENTATION_TESTS


def test_recommended_next_artifact() -> None:
    contract = build_method_suitability_handoff_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "METHOD_SUITABILITY_RUNTIME_001"
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT


def test_summary_json_and_report() -> None:
    if not _SUMMARY.is_file():
        run_validation(write_summary=True, summary_path=_SUMMARY)
    assert _REPORT.is_file()
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"
    assert data["failed_scenarios"] == []
    assert data["method_suitability_handoff_contract_defined"] is True
    assert data["runtime_method_suitability_implemented"] is False
    assert data["method_family_selected"] is False
    assert data["final_verdict"] == (
        "method_suitability_handoff_contract_defined_no_method_selection_or_inference_authorization"
    )


def test_report_covers_examples_and_boundaries() -> None:
    text = _REPORT.read_text(encoding="utf-8")
    assert "Example 1" in text
    assert "Example 8" in text
    assert "dosage" in text.lower() or "Dosage" in text
    assert "difference-in-policy" in text.lower() or "Difference-in-policy" in text
    assert "METHOD_HANDOFF_READY_FOR_SUITABILITY_REVIEW" in text
    assert "SCM_FAMILY" in text or "method-family" in text.lower()
