"""Tests for CLAIM_AUTHORIZATION_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.claim_authorization_contract_001 import (
    BLOCKER_CATEGORIES,
    CLAIM_DECISION_FIELDS,
    CLAIM_GATES,
    CLAIM_REQUEST_FIELDS,
    CLAIM_STATUSES,
    CLAIM_TYPES,
    CONTRACT_EXAMPLES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    EVIDENCE_BUNDLE_FIELDS,
    FAILURE_PACKET_FIELDS,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_IMPLEMENTATION_TESTS,
    RETRY_CATEGORIES,
    _ALTERNATIVE_NEXT,
    _AUTH_FLAGS,
    _RECOMMENDED_NEXT,
    _VERDICT,
    build_claim_authorization_contract,
    build_scenarios,
    run_validation,
    validate_claim_authorization_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/CLAIM_AUTHORIZATION_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/CLAIM_AUTHORIZATION_CONTRACT_001_REPORT.md"


def test_claim_types_defined() -> None:
    contract = build_claim_authorization_contract()
    assert contract.claim_types == CLAIM_TYPES
    assert "POINT_ESTIMATE_CLAIM" in contract.claim_types
    assert "INSUFFICIENT_EVIDENCE_CLAIM" in contract.claim_types


def test_claim_statuses_defined() -> None:
    contract = build_claim_authorization_contract()
    assert contract.claim_statuses == CLAIM_STATUSES
    assert "CLAIM_REVIEW_ELIGIBLE" in contract.claim_statuses
    assert "CLAIM_BLOCKED_BY_MISSING_UNCERTAINTY" in contract.claim_statuses


def test_claim_gates_order() -> None:
    contract = build_claim_authorization_contract()
    assert contract.claim_gates == CLAIM_GATES
    assert len(contract.claim_gates) == 14
    assert contract.claim_gates[0] == "claim_request_schema_gate"
    assert contract.claim_gates[-1] == "trusted_readout_handoff_gate"


def test_contract_semantics() -> None:
    contract = build_claim_authorization_contract()
    assert contract.claim_authorization_contract_defined
    assert contract.claim_request_contract_defined
    assert CONTRACT_POSITIVE_FLAGS["claim_boundaries_defined"]


def test_authorization_flags_all_false() -> None:
    contract = build_claim_authorization_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["claim_authorized"]
    assert not contract.authorization_flags["production_readout_authorized"]


def test_contract_validation_passes() -> None:
    contract = build_claim_authorization_contract()
    result = validate_claim_authorization_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_future_contract_concepts() -> None:
    contract = build_claim_authorization_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert "ClaimRequest" in contract.future_contract_concepts
    assert "TrustedReadoutHandoffPacket" in contract.future_contract_concepts


def test_claim_request_and_evidence_fields() -> None:
    contract = build_claim_authorization_contract()
    assert contract.claim_request_fields == CLAIM_REQUEST_FIELDS
    assert contract.evidence_bundle_fields == EVIDENCE_BUNDLE_FIELDS
    assert contract.claim_decision_fields == CLAIM_DECISION_FIELDS
    assert "requires_causal_language" in contract.claim_request_fields
    assert "effect_estimate_report" in contract.evidence_bundle_fields
    assert "authorized_claim_text" in contract.claim_decision_fields


def test_blocker_categories() -> None:
    contract = build_claim_authorization_contract()
    assert contract.blocker_categories == BLOCKER_CATEGORIES
    assert "DIAGNOSTIC_ONLY_INSTRUMENT" in contract.blocker_categories


def test_contract_examples_count() -> None:
    contract = build_claim_authorization_contract()
    assert contract.contract_examples == CONTRACT_EXAMPLES
    assert len(contract.contract_examples) == 10


def test_failure_packet_and_retry_categories() -> None:
    contract = build_claim_authorization_contract()
    assert contract.failure_packet_fields == FAILURE_PACKET_FIELDS
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "RESTRICT_TO_POINT_ESTIMATE_CLAIM" in contract.retry_categories


def test_future_implementation_tests_documented() -> None:
    scenarios = build_scenarios()
    for test_id in FUTURE_IMPLEMENTATION_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_depends_on_includes_did_artifacts() -> None:
    contract = build_claim_authorization_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR" in contract.depends_on
    assert "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC" in contract.depends_on


def test_recommended_next_artifact() -> None:
    contract = build_claim_authorization_contract()
    assert contract.recommended_next_artifact == _RECOMMENDED_NEXT
    assert contract.alternative_next_artifact == _ALTERNATIVE_NEXT


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["claim_authorization_contract_defined"] is True
    assert summary["claim_authorized"] is False
    assert summary["production_readout_authorized"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
