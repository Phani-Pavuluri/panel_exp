"""Tests for READOUT_METHOD_GOVERNANCE_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.readout_method_governance_contract_001 import (
    ALTERNATIVE_NEXT_ARTIFACT,
    ASSIGNMENT_ARTIFACT_GOVERNANCE_STATUSES,
    CLAIM_ELIGIBILITY_STATUSES,
    CONTRACT_EXAMPLES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    DIAGNOSTIC_SENSITIVITY_SLOT_TYPES,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    FUTURE_OUTPUT_CONCEPTS,
    GOVERNANCE_PACKET_FIELDS,
    INPUT_DEPENDENCIES,
    INSTRUMENT_GOVERNANCE_STATUSES,
    PRODUCTION_READOUT_BLOCKER_ROLES,
    READINESS_GATES,
    READOUT_CLAIM_TYPES,
    READOUT_GOVERNANCE_STATUSES,
    RECOMMENDED_NEXT_ARTIFACT,
    UNCERTAINTY_SEMANTICS_CLASSIFICATIONS,
    _AUTH_FLAGS,
    build_readout_method_governance_contract,
    build_scenarios,
    run_validation,
    validate_readout_method_governance_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/READOUT_METHOD_GOVERNANCE_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/READOUT_METHOD_GOVERNANCE_CONTRACT_001_REPORT.md"


def test_readout_governance_statuses_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.readout_governance_statuses == READOUT_GOVERNANCE_STATUSES
    assert "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING" in contract.readout_governance_statuses
    assert "READOUT_GOVERNANCE_BLOCKED_BY_INSTRUMENT_GOVERNANCE" in contract.readout_governance_statuses


def test_instrument_governance_statuses_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.instrument_governance_statuses == INSTRUMENT_GOVERNANCE_STATUSES
    assert "INSTRUMENT_DIAGNOSTIC_ONLY" in contract.instrument_governance_statuses
    assert "INSTRUMENT_BLOCKED" in contract.instrument_governance_statuses


def test_claim_eligibility_statuses_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.claim_eligibility_statuses == CLAIM_ELIGIBILITY_STATUSES
    assert "CLAIM_ELIGIBILITY_ELIGIBLE_FOR_GOVERNED_PLANNING" in contract.claim_eligibility_statuses
    assert "CLAIM_ELIGIBILITY_BLOCKED_BY_PRODUCTION_READOUT_POLICY" in contract.claim_eligibility_statuses


def test_readout_claim_types_include_production_blockers() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.readout_claim_types == READOUT_CLAIM_TYPES
    assert "POOLED_MULTICELL_CLAIM" in contract.readout_claim_types
    assert "PRODUCTION_TRUST_REPORT_CLAIM" in contract.readout_claim_types
    assert "MMM_INGESTION_CLAIM" in contract.readout_claim_types


def test_assignment_artifact_governance_statuses_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.assignment_artifact_governance_statuses == ASSIGNMENT_ARTIFACT_GOVERNANCE_STATUSES
    assert "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE" in contract.assignment_artifact_governance_statuses


def test_uncertainty_semantics_classifications_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.uncertainty_semantics_classifications == UNCERTAINTY_SEMANTICS_CLASSIFICATIONS
    assert "point_only_no_uncertainty" in contract.uncertainty_semantics_classifications
    assert "blocked_due_to_readout_mismatch" in contract.uncertainty_semantics_classifications


def test_diagnostic_sensitivity_slot_types_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.diagnostic_sensitivity_slot_types == DIAGNOSTIC_SENSITIVITY_SLOT_TYPES
    assert "PRIMARY_READOUT_SLOT" in contract.diagnostic_sensitivity_slot_types
    assert "SENSITIVITY_READOUT_SLOT" in contract.diagnostic_sensitivity_slot_types


def test_production_readout_blocker_roles_defined() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.production_readout_blocker_roles == PRODUCTION_READOUT_BLOCKER_ROLES
    assert "trust_report" in contract.production_readout_blocker_roles
    assert "mmm_ingestion" in contract.production_readout_blocker_roles


def test_contract_semantics() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.readout_method_governance_contract_defined
    assert contract.instrument_governance_treatment_defined
    assert contract.estimand_governance_treatment_defined
    assert contract.uncertainty_semantics_treatment_defined
    assert contract.diagnostic_sensitivity_treatment_defined
    assert CONTRACT_POSITIVE_FLAGS["claim_boundaries_defined"]


def test_readiness_gates_count() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.readiness_gates == READINESS_GATES
    assert len(contract.readiness_gates) == 15
    assert "assignment_artifact_gate" in contract.readiness_gates
    assert "uncertainty_semantics_gate" in contract.readiness_gates


def test_input_dependencies_include_assignment_and_instruments() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.input_dependencies == INPUT_DEPENDENCIES
    assert "design_assignment_runtime_report" in contract.input_dependencies
    assert "method_instrument_suitability_matrix" in contract.input_dependencies
    assert "assignment_reproducibility_manifest" in contract.input_dependencies


def test_governance_packet_fields() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.governance_packet_fields == GOVERNANCE_PACKET_FIELDS
    assert "claim_eligibility_reports" in contract.governance_packet_fields
    assert "production_readout_blockers" in contract.governance_packet_fields


def test_authorization_flags_all_false() -> None:
    contract = build_readout_method_governance_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["readout_plan_generated"]
    assert not contract.authorization_flags["estimator_execution_implemented"]
    assert not contract.authorization_flags["causal_claim_authorized"]
    assert not contract.authorization_flags["production_readout_authorization_granted"]


def test_contract_validation_passes() -> None:
    contract = build_readout_method_governance_contract()
    result = validate_readout_method_governance_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_future_contract_and_output_concepts() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert contract.future_output_concepts == FUTURE_OUTPUT_CONCEPTS
    assert "ReadoutClaimEligibilityReport" in contract.future_contract_concepts
    assert "ProductionReadoutBlockerReport" in contract.future_output_concepts


def test_contract_examples_count() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.contract_examples == CONTRACT_EXAMPLES
    assert len(contract.contract_examples) == 8


def test_future_implementation_tests_documented() -> None:
    scenarios = build_scenarios()
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_depends_on_includes_assignment_runtime() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "DESIGN_ASSIGNMENT_RUNTIME_001" in contract.depends_on
    assert "METHOD_SUITABILITY_RUNTIME_001" in contract.depends_on


def test_recommended_next_artifact() -> None:
    contract = build_readout_method_governance_contract()
    assert contract.recommended_next_artifact == RECOMMENDED_NEXT_ARTIFACT
    assert contract.alternative_next_artifact == ALTERNATIVE_NEXT_ARTIFACT
    assert contract.recommended_next_artifact == "READOUT_PLAN_CONTRACT_001"


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "readout_method_governance_contract_defined_no_estimator_execution_or_causal_claim_authorization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["readout_method_governance_contract_defined"] is True
    assert summary["readout_plan_generated"] is False
    assert summary["causal_claim_authorized"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
    text = _REPORT.read_text(encoding="utf-8")
    assert (
        "readout_method_governance_contract_defined_no_estimator_execution_or_causal_claim_authorization"
        in text
    )
    assert "Production-readout blockers" in text
