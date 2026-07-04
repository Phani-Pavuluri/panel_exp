"""Tests for TRUSTED_READOUT_REPORT_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.trusted_readout_report_contract_001 import (
    CAVEAT_CODES,
    CLAIM_BINDING_POLICY_RULES,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    EVIDENCE_BUNDLE_REQUIREMENTS,
    FAILURE_PACKET_FIELDS,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_RUNTIME_TESTS,
    REDACTION_RULES,
    REPORT_PACKET_FIELDS,
    REPORT_SECTION_TYPES,
    RETRY_CATEGORIES,
    SECTION_EVIDENCE_REQUIREMENTS,
    SECTION_FIELDS,
    SECTION_STATUSES,
    TRUSTED_REPORT_STATUSES,
    _ALTERNATIVE_NEXT,
    _AUTH_FLAGS,
    _RECOMMENDED_NEXT,
    _VERDICT,
    build_scenarios,
    build_trusted_readout_report_contract,
    get_trusted_readout_report_contract_metadata,
    list_trusted_readout_report_evidence_requirements,
    list_trusted_readout_report_future_tests,
    list_trusted_readout_report_sections,
    list_trusted_readout_report_statuses,
    run_validation,
    validate_trusted_readout_report_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TRUSTED_READOUT_REPORT_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/TRUSTED_READOUT_REPORT_CONTRACT_001_REPORT.md"


def test_contract_metadata_exposes_artifact_id() -> None:
    meta = get_trusted_readout_report_contract_metadata()
    assert meta["artifact_id"] == "TRUSTED_READOUT_REPORT_CONTRACT_001"
    assert meta["trusted_readout_report_contract_defined"] is True


def test_all_report_statuses_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.trusted_report_statuses == TRUSTED_REPORT_STATUSES
    assert len(TRUSTED_REPORT_STATUSES) >= 10
    assert "TRUSTED_REPORT_CONTRACT_ONLY" in TRUSTED_REPORT_STATUSES
    assert list_trusted_readout_report_statuses() == TRUSTED_REPORT_STATUSES


def test_all_section_types_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.report_section_types == REPORT_SECTION_TYPES
    assert len(REPORT_SECTION_TYPES) >= 18
    assert "RECOMMENDATION_SECTION" in REPORT_SECTION_TYPES
    assert "UNCERTAINTY_SUMMARY" in REPORT_SECTION_TYPES
    assert "EXECUTIVE_SUMMARY" in REPORT_SECTION_TYPES
    assert list_trusted_readout_report_sections() == REPORT_SECTION_TYPES


def test_section_statuses_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.section_statuses == SECTION_STATUSES
    assert "SECTION_REDACTED" in SECTION_STATUSES


def test_all_required_evidence_concepts_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.evidence_bundle_requirements == EVIDENCE_BUNDLE_REQUIREMENTS
    assert "claim_authorization_report" in contract.evidence_bundle_requirements
    reqs = list_trusted_readout_report_evidence_requirements()
    assert "POINT_ESTIMATE_SUMMARY" in reqs
    assert "claim_authorization_report" in reqs["POINT_ESTIMATE_SUMMARY"]
    assert "UNCERTAINTY_SUMMARY" in reqs
    assert "RECOMMENDATION_SECTION" in reqs
    assert contract.section_evidence_requirements == SECTION_EVIDENCE_REQUIREMENTS


def test_claim_binding_policy_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.trusted_report_claim_binding_policy_defined
    assert contract.claim_binding_policy_rules == CLAIM_BINDING_POLICY_RULES
    assert "each_report_statement_binds_to_claim_authorization_record" in contract.claim_binding_policy_rules


def test_redaction_and_caveat_policy_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.trusted_report_redaction_policy_defined
    assert contract.trusted_report_caveat_policy_defined
    assert contract.redaction_rules == REDACTION_RULES
    assert contract.caveat_codes == CAVEAT_CODES
    assert "no_causal_language_without_causal_claim_authorization" in contract.redaction_rules
    assert "POINT_ESTIMATE_ONLY" in contract.caveat_codes


def test_failure_packet_semantics_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.trusted_report_failure_packet_semantics_defined
    assert contract.failure_packet_fields == FAILURE_PACKET_FIELDS
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "ADD_CLAIM_AUTHORIZATION_REPORT" in contract.retry_categories


def test_report_packet_and_section_fields_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.report_packet_fields == REPORT_PACKET_FIELDS
    assert contract.section_fields == SECTION_FIELDS
    assert "provenance_hash" in contract.report_packet_fields
    assert "bound_claim_authorization_ids" in contract.section_fields


def test_future_runtime_tests_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.trusted_report_future_runtime_tests_documented
    assert contract.future_runtime_tests == FUTURE_RUNTIME_TESTS
    assert list_trusted_readout_report_future_tests() == FUTURE_RUNTIME_TESTS
    assert len(FUTURE_RUNTIME_TESTS) >= 10
    scenarios = build_scenarios()
    for test_id in FUTURE_RUNTIME_TESTS:
        assert any(s["scenario_id"] == f"future_test_{test_id}" for s in scenarios)


def test_future_contract_concepts_documented() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert "TrustedReadoutReportPacket" in contract.future_contract_concepts


def test_authorization_flags_false() -> None:
    contract = build_trusted_readout_report_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected
    assert not contract.authorization_flags["trusted_readout_report_runtime_implemented"]
    assert not contract.authorization_flags["trusted_readout_report_generated"]
    assert not contract.authorization_flags["production_authorization_granted"]


def test_contract_positive_flags_true() -> None:
    contract = build_trusted_readout_report_contract()
    for key, val in CONTRACT_POSITIVE_FLAGS.items():
        assert getattr(contract, key) is val


def test_contract_validation_passes() -> None:
    contract = build_trusted_readout_report_contract()
    result = validate_trusted_readout_report_contract(contract)
    assert result["valid"]
    assert result["issues"] == []


def test_depends_on_includes_claim_authorization_runtime() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.depends_on == DEPENDS_ON
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in contract.depends_on


def test_recommended_next_artifact() -> None:
    contract = build_trusted_readout_report_contract()
    assert contract.recommended_next_artifact == _RECOMMENDED_NEXT
    assert contract.alternative_next_artifact == _ALTERNATIVE_NEXT
    assert contract.final_verdict == _VERDICT


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["trusted_readout_report_contract_defined"] is True
    assert summary["trusted_readout_report_runtime_implemented"] is False
    assert summary["trusted_readout_report_generated"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
