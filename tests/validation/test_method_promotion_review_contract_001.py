"""Tests for METHOD_PROMOTION_REVIEW_CONTRACT_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.method_promotion_review_contract_001 import (
    CANDIDATE_VERDICTS,
    CONTRACT_POSITIVE_FLAGS,
    DEPENDS_ON,
    EVIDENCE_BUNDLE_REQUIREMENTS,
    FAILURE_CODES,
    FAILURE_PACKET_FIELDS,
    FUTURE_CONTRACT_CONCEPTS,
    FUTURE_RUNTIME_TESTS,
    PROMOTION_BOUNDARY_RULES,
    PROMOTION_REVIEW_STATUSES,
    PROHIBITED_SURFACES,
    RETRY_CATEGORIES,
    REVIEW_PACKET_FIELDS,
    SCOPE_EVIDENCE_REQUIREMENTS,
    _ALTERNATIVE_NEXT,
    _AUTH_FLAGS,
    _RECOMMENDED_NEXT,
    _VERDICT,
    build_method_promotion_review_contract,
    build_scenarios,
    get_method_promotion_review_contract_metadata,
    list_method_promotion_review_evidence_requirements,
    list_method_promotion_review_future_tests,
    list_method_promotion_review_statuses,
    list_method_promotion_review_verdicts,
    run_validation,
    validate_method_promotion_review_contract,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_REVIEW_CONTRACT_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_PROMOTION_REVIEW_CONTRACT_001_REPORT.md"


def test_contract_metadata_exposes_artifact_id() -> None:
    meta = get_method_promotion_review_contract_metadata()
    assert meta["artifact_id"] == "METHOD_PROMOTION_REVIEW_CONTRACT_001"
    assert meta["method_promotion_review_contract_defined"] is True


def test_status_taxonomy_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.promotion_review_statuses == PROMOTION_REVIEW_STATUSES
    assert len(PROMOTION_REVIEW_STATUSES) >= 10
    assert "PROMOTION_REVIEW_REQUIRES_HUMAN_GOVERNANCE" in PROMOTION_REVIEW_STATUSES
    assert list_method_promotion_review_statuses() == PROMOTION_REVIEW_STATUSES


def test_candidate_verdict_taxonomy_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.candidate_verdicts == CANDIDATE_VERDICTS
    assert "ELIGIBLE_FOR_PRODUCTION_REVIEW" in CANDIDATE_VERDICTS
    assert "PRODUCTION_APPROVED" not in CANDIDATE_VERDICTS
    assert "METHOD_PROMOTED" not in CANDIDATE_VERDICTS
    assert list_method_promotion_review_verdicts() == CANDIDATE_VERDICTS


def test_evidence_requirements_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.evidence_bundle_requirements == EVIDENCE_BUNDLE_REQUIREMENTS
    assert "method_suitability_report" in contract.evidence_bundle_requirements
    assert "trusted_readout_report_packet" in contract.evidence_bundle_requirements
    assert "statistical_promotion_report" in contract.evidence_bundle_requirements
    reqs = list_method_promotion_review_evidence_requirements()
    assert "PRODUCTION_REVIEW" in reqs
    assert "RESTRICTED_USE_REVIEW" in reqs
    assert contract.scope_evidence_requirements == SCOPE_EVIDENCE_REQUIREMENTS


def test_packet_fields_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.review_packet_fields == REVIEW_PACKET_FIELDS
    assert "review_id" in contract.review_packet_fields
    assert "candidate_verdict" in contract.review_packet_fields
    assert "failure_packet" in contract.review_packet_fields
    assert "prohibited_surfaces" in contract.review_packet_fields


def test_failure_packet_semantics_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.promotion_review_failure_packet_semantics_defined
    assert contract.failure_packet_fields == FAILURE_PACKET_FIELDS
    assert contract.failure_codes == FAILURE_CODES
    assert contract.retry_categories == RETRY_CATEGORIES
    assert "REQUIRE_HUMAN_GOVERNANCE_REVIEW" in contract.retry_categories


def test_promotion_boundary_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.production_authorization_boundary_defined
    assert contract.promotion_boundary_rules == PROMOTION_BOUNDARY_RULES
    assert contract.prohibited_surfaces == PROHIBITED_SURFACES
    assert "no_production_authorization_from_review_verdict" in contract.promotion_boundary_rules
    assert "PRODUCTION_SAFE" in contract.prohibited_surfaces


def test_future_runtime_tests_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.promotion_review_future_runtime_tests_documented
    assert contract.future_runtime_tests == FUTURE_RUNTIME_TESTS
    assert list_method_promotion_review_future_tests() == FUTURE_RUNTIME_TESTS
    assert "promotion_review_never_promotes_method_directly" in contract.future_runtime_tests


def test_all_forbidden_flags_false() -> None:
    contract = build_method_promotion_review_contract()
    for flag, expected in _AUTH_FLAGS.items():
        assert contract.authorization_flags[flag] is expected, flag
    meta = get_method_promotion_review_contract_metadata()
    assert meta["method_promoted"] is False
    assert meta["method_unblocked"] is False
    assert meta["production_catalog_unblocked"] is False
    assert meta["production_authorization_granted"] is False
    assert meta["estimator_implemented"] is False
    assert meta["inference_implemented"] is False
    assert meta["p_value_computed"] is False
    assert meta["uncertainty_computed"] is False


def test_contract_positive_flags_true() -> None:
    contract = build_method_promotion_review_contract()
    for key, expected in CONTRACT_POSITIVE_FLAGS.items():
        assert getattr(contract, key) is expected


def test_validate_contract_passes() -> None:
    contract = build_method_promotion_review_contract()
    result = validate_method_promotion_review_contract(contract)
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
    contract = build_method_promotion_review_contract()
    assert contract.recommended_next_artifact == _RECOMMENDED_NEXT
    assert contract.alternative_next_artifact == _ALTERNATIVE_NEXT
    assert _RECOMMENDED_NEXT == "METHOD_PROMOTION_REVIEW_RUNTIME_001"


def test_depends_on_includes_trusted_readout_runtime() -> None:
    assert "TRUSTED_READOUT_REPORT_RUNTIME_001" in DEPENDS_ON
    assert "STATISTICAL_PROMOTION_THRESHOLD_ENFORCEMENT_001" in DEPENDS_ON


def test_future_contract_concepts_documented() -> None:
    contract = build_method_promotion_review_contract()
    assert contract.future_contract_concepts == FUTURE_CONTRACT_CONCEPTS
    assert "MethodPromotionReviewPacket" in contract.future_contract_concepts


def test_report_file_exists() -> None:
    assert _REPORT.exists()


def test_summary_json_matches_contract() -> None:
    run_validation(write_summary=True)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert data["artifact_id"] == "METHOD_PROMOTION_REVIEW_CONTRACT_001"
    assert data["final_verdict"] == _VERDICT
    assert data["method_promotion_review_contract_defined"] is True
    assert data["method_promoted"] is False
    assert data["production_authorization_granted"] is False
    assert data["failed_scenarios"] == []
