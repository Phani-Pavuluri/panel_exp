"""Tests for PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.production_compatibility_promotion_review_contract_001 import (
    ALLOWED_SURFACES,
    CANDIDATE_VERDICTS,
    COMPATIBILITY_BOUNDARY_RULES,
    COMPATIBILITY_PACKET_FIELDS,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    EVIDENCE_BUNDLE_REQUIREMENTS,
    FAILURE_CODES,
    FAILURE_PACKET_FIELDS,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_RUNTIME_TESTS,
    HARD_BLOCKERS,
    PRODUCTION_COMPATIBILITY_STATUSES,
    PROHIBITED_SURFACES,
    RETRY_CATEGORIES,
    SCOPE_EVIDENCE_REQUIREMENTS,
    _ALTERNATIVE_NEXT,
    _AUTH_FLAGS,
    _RECOMMENDED_NEXT,
    _VERDICT,
    build_production_compatibility_promotion_review_contract,
    build_scenarios,
    get_production_compatibility_promotion_review_contract_metadata,
    list_production_compatibility_evidence_requirements,
    list_production_compatibility_future_tests,
    list_production_compatibility_statuses,
    list_production_compatibility_verdicts,
    run_validation,
    validate_production_compatibility_promotion_review_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = (
    _REPO
    / "docs/track_d/archives/PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001_summary.json"
)
_REPORT = _REPO / "docs/track_d/PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001_REPORT.md"


def test_contract_metadata_exposes_artifact_id() -> None:
    meta = get_production_compatibility_promotion_review_contract_metadata()
    assert meta["artifact_id"] == "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001"
    assert meta["production_compatibility_promotion_review_contract_defined"] is True


def test_status_taxonomy_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.production_compatibility_statuses == PRODUCTION_COMPATIBILITY_STATUSES
    assert len(PRODUCTION_COMPATIBILITY_STATUSES) >= 12
    assert "PRODUCTION_COMPATIBILITY_REQUIRES_HUMAN_APPROVAL" in PRODUCTION_COMPATIBILITY_STATUSES
    assert list_production_compatibility_statuses() == PRODUCTION_COMPATIBILITY_STATUSES


def test_verdict_taxonomy_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.candidate_verdicts == CANDIDATE_VERDICTS
    assert "ELIGIBLE_FOR_PRODUCTION_COMPATIBILITY_REVIEW" in CANDIDATE_VERDICTS
    assert "PRODUCTION_APPROVED" not in CANDIDATE_VERDICTS
    assert "METHOD_PROMOTED" not in CANDIDATE_VERDICTS
    assert list_production_compatibility_verdicts() == CANDIDATE_VERDICTS


def test_evidence_requirements_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.evidence_bundle_requirements == EVIDENCE_BUNDLE_REQUIREMENTS
    assert "method_promotion_review_report" in contract.evidence_bundle_requirements
    assert "trusted_readout_report" in contract.evidence_bundle_requirements
    assert "human_governance_requirement_record" in contract.evidence_bundle_requirements
    reqs = list_production_compatibility_evidence_requirements()
    assert "PRODUCTION_COMPATIBILITY_REVIEW" in reqs
    assert "RESTRICTED_PRODUCTION_COMPATIBILITY_REVIEW" in reqs
    assert contract.scope_evidence_requirements == SCOPE_EVIDENCE_REQUIREMENTS


def test_packet_fields_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.compatibility_packet_fields == COMPATIBILITY_PACKET_FIELDS
    assert "compatibility_review_id" in contract.compatibility_packet_fields
    assert "upstream_method_promotion_review_id" in contract.compatibility_packet_fields
    assert "required_human_governance_gates" in contract.compatibility_packet_fields
    assert "authorization_boundary_report" in contract.compatibility_packet_fields


def test_hard_blockers_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.production_compatibility_blockers_defined
    assert contract.hard_blockers == HARD_BLOCKERS
    assert "method_promotion_review_missing" in contract.hard_blockers
    assert "human_governance_gate_missing" in contract.hard_blockers


def test_allowed_and_prohibited_surfaces_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.allowed_surfaces == ALLOWED_SURFACES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "PRODUCTION_COMPATIBILITY_CANDIDATE_REVIEW" in contract.allowed_surfaces
    assert "PRODUCTION_APPROVAL" in contract.prohibited_surfaces
    assert "CATALOG_UNBLOCK_NOTICE" in contract.prohibited_surfaces


def test_failure_packet_semantics_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.production_compatibility_failure_packet_semantics_defined
    assert contract.failure_packet_fields == FAILURE_PACKET_FIELDS
    assert contract.failure_codes == FAILURE_CODES
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "MISSING_METHOD_PROMOTION_REVIEW" in contract.failure_codes
    assert "REQUIRE_HUMAN_GOVERNANCE_REVIEW" in contract.retry_categories


def test_compatibility_boundary_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.production_authorization_boundary_defined
    assert contract.compatibility_boundary_rules == COMPATIBILITY_BOUNDARY_RULES
    assert (
        "production_compatibility_stricter_than_method_promotion_eligibility"
        in contract.compatibility_boundary_rules
    )
    assert "no_production_approval_from_compatibility_verdict" in contract.compatibility_boundary_rules


def test_future_runtime_tests_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.production_compatibility_future_runtime_tests_documented
    assert contract.future_runtime_tests == FUTURE_RUNTIME_TESTS
    assert list_production_compatibility_future_tests() == FUTURE_RUNTIME_TESTS
    assert "production_compatibility_emits_eligibility_only_not_production_authorization" in (
        contract.future_runtime_tests
    )


def test_all_forbidden_flags_false() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_production_compatibility_promotion_review_contract_metadata()
    assert meta["production_compatibility_runtime_implemented"] is False
    assert meta["production_compatibility_packet_generated"] is False
    assert meta["method_promoted"] is False
    assert meta["production_catalog_unblocked"] is False
    assert meta["production_authorization_granted"] is False
    assert meta["estimator_implemented"] is False
    assert meta["p_value_computed"] is False
    assert meta["uncertainty_computed"] is False


def test_contract_positive_flags_true() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        assert getattr(contract, key) is expected


def test_validate_contract_passes() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    result = validate_production_compatibility_promotion_review_contract(contract)
    assert result["valid"] is True
    assert result["issues"] == []


def test_build_scenarios_all_pass() -> None:
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]
    assert failed == []


def test_run_validation() -> None:
    result = run_validation(write_summary=False)
    assert result["verdict"] == _VERDICT
    assert result["failed_scenarios"] == []
    assert result["validation"]["valid"] is True


def test_recommended_next_artifacts() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.recommended_next_artifact == _RECOMMENDED_NEXT
    assert contract.alternative_next_artifact == _ALTERNATIVE_NEXT
    assert _RECOMMENDED_NEXT == "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_RUNTIME_001"


def test_depends_on_includes_method_promotion_review_runtime() -> None:
    assert "METHOD_PROMOTION_REVIEW_RUNTIME_001" in DEPENDS_ON
    assert "TRUSTED_READOUT_REPORT_RUNTIME_001" in DEPENDS_ON
    assert "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001" in DEPENDS_ON


def test_future_contract_concepts_documented() -> None:
    contract = build_production_compatibility_promotion_review_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert "ProductionCompatibilityReviewPacket" in contract.future_contract_concepts


def test_report_file_exists() -> None:
    assert _REPORT.exists()


def test_summary_json_matches_contract() -> None:
    run_validation(write_summary=True)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "PRODUCTION_COMPATIBILITY_PROMOTION_REVIEW_CONTRACT_001"
    assert data["final_verdict"] == _VERDICT
    assert data["production_compatibility_promotion_review_contract_defined"] is True
    assert data["production_compatibility_runtime_implemented"] is False
    assert data["production_authorization_granted"] is False
    assert data["method_promoted"] is False
    assert data["failed_scenarios"] == []
