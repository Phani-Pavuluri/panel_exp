"""Tests for METHOD_PROMOTION_REVIEW_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_BLOCKED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
)
from panel_exp.validation.claim_authorization_runtime_001 import CLAIM_AUTHORIZATION_BLOCKED
from panel_exp.validation.production_catalog_blocklist_001 import PRODUCTION_CATALOG_BLOCKED
from panel_exp.validation.srm_balance_readout_diagnostic_001 import (
    SRM_BALANCE_DIAGNOSTIC_BLOCKED,
    SRM_BALANCE_DIAGNOSTIC_PASSED,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    STATISTICAL_PROMOTION_FAILED,
    STATISTICAL_PROMOTION_PASSED,
)
from panel_exp.validation.method_promotion_review_runtime_001 import (
    MethodPromotionReviewRuntimeReport,
    _AUTH_FALSE,
    _POSITIVE_FLAGS,
    build_method_promotion_review,
    create_method_promotion_review_packet,
    generate_method_promotion_review,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/METHOD_PROMOTION_REVIEW_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/METHOD_PROMOTION_REVIEW_RUNTIME_001_REPORT.md"


def _restricted_base(**extra: object) -> dict:
    payload = {
        "request_id": "mpr_test_001",
        "method_id": "DID_2X2",
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
        "estimator_family": "DID",
        "inference_family": "POINT_ESTIMATE",
        "current_catalog_status": "PRODUCTION_CATALOG_RESEARCH_ONLY",
        "requested_promotion_scope": "RESTRICTED_USE_REVIEW",
        "method_suitability_report": {"suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW"},
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED},
        "trusted_readout_report": {"report_status": "TRUSTED_REPORT_READY"},
        "claim_authorization_report": {"overall_status": "CLAIM_AUTHORIZATION_COMPLETED"},
        "known_limitations": ["point_estimate_only"],
    }
    payload.update(extra)
    return payload


def _production_base(**extra: object) -> dict:
    payload = _restricted_base(
        requested_promotion_scope="PRODUCTION_REVIEW",
        production_catalog_report={"status": "PRODUCTION_CATALOG_RESEARCH_ONLY"},
        assignment_panel_integrity_report={"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
        srm_balance_diagnostic_report={"status": SRM_BALANCE_DIAGNOSTIC_PASSED},
        diagnostics_sensitivity_report={"evidence_sufficiency_status": "EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW"},
        governed_randomization_report={"status": "GOVERNED_RANDOMIZATION_COMPLETED"},
        execution_result={"execution_status": "INSTRUMENT_EXECUTION_COMPLETED"},
        readout_plan_report={"status": "READOUT_PLAN_READY"},
        audit_registry_refs=["MIP_AUDIT_REGISTRY"],
        lineage_manifest={"artifact_id": "lineage_001"},
    )
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    report = generate_method_promotion_review(_restricted_base())
    assert isinstance(report, MethodPromotionReviewRuntimeReport)
    assert build_method_promotion_review(_restricted_base()).review_id == report.review_id
    assert create_method_promotion_review_packet(_restricted_base()).request_id == "mpr_test_001"


def test_missing_evidence_produces_insufficient_evidence_with_failure_packet() -> None:
    report = generate_method_promotion_review({"request_id": "missing_only"})
    assert report.candidate_verdict == "INSUFFICIENT_EVIDENCE"
    assert report.review_status == "PROMOTION_REVIEW_BLOCKED_BY_MISSING_EVIDENCE"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "MISSING_REQUIRED_EVIDENCE"
    assert report.missing_evidence


def test_production_catalog_blocker_produces_blocked_review() -> None:
    report = generate_method_promotion_review(
        _production_base(current_catalog_status=PRODUCTION_CATALOG_BLOCKED)
    )
    assert report.candidate_verdict == "BLOCKED"
    assert report.review_status == "PROMOTION_REVIEW_BLOCKED_BY_PRODUCTION_CATALOG"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "PRODUCTION_CATALOG_BLOCKED"


def test_method_suitability_blocker_produces_blocked_review() -> None:
    report = generate_method_promotion_review(
        _restricted_base(method_suitability_report={"suitability_status": "METHOD_FAMILY_BLOCKED"})
    )
    assert report.candidate_verdict == "BLOCKED"
    assert report.review_status == "PROMOTION_REVIEW_BLOCKED_BY_METHOD_SUITABILITY"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "METHOD_SUITABILITY_BLOCKED"


def test_statistical_promotion_blocker_produces_blocked_review() -> None:
    report = generate_method_promotion_review(
        _restricted_base(statistical_promotion_report={"status": STATISTICAL_PROMOTION_FAILED})
    )
    assert report.candidate_verdict == "BLOCKED"
    assert report.review_status == "PROMOTION_REVIEW_BLOCKED_BY_STATISTICAL_PROMOTION"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "STATISTICAL_PROMOTION_BLOCKED"


def test_assignment_integrity_blocker_produces_blocked_review() -> None:
    report = generate_method_promotion_review(
        _production_base(
            assignment_panel_integrity_report={"status": ASSIGNMENT_PANEL_INTEGRITY_BLOCKED},
        )
    )
    assert report.candidate_verdict == "BLOCKED"
    assert report.review_status == "PROMOTION_REVIEW_BLOCKED_BY_ASSIGNMENT_INTEGRITY"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "ASSIGNMENT_INTEGRITY_BLOCKED"


def test_srm_balance_blocker_produces_blocked_review() -> None:
    report = generate_method_promotion_review(
        _production_base(
            srm_balance_diagnostic_report={"status": SRM_BALANCE_DIAGNOSTIC_BLOCKED},
        )
    )
    assert report.candidate_verdict == "BLOCKED"
    assert report.review_status == "PROMOTION_REVIEW_BLOCKED_BY_SRM_BALANCE"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "SRM_BALANCE_BLOCKED"


def test_trusted_readout_redactions_propagate_restrictions_and_caveats() -> None:
    report = generate_method_promotion_review(
        _restricted_base(
            trusted_readout_report={
                "report_status": "TRUSTED_REPORT_READY_WITH_REDACTIONS",
                "restricted_sections": ["UNCERTAINTY_SUMMARY"],
                "redacted_sections": ["RECOMMENDATION_SECTION"],
                "required_caveats": ["POINT_ESTIMATE_ONLY"],
            }
        )
    )
    assert "UNCERTAINTY_SUMMARY" in report.restrictions
    assert any("REDACTED" in r for r in report.restrictions)
    assert "POINT_ESTIMATE_ONLY" in report.required_caveats
    assert report.candidate_verdict == "REVIEW_REQUIRED"


def test_claim_authorization_blocks_prohibited_surfaces() -> None:
    report = generate_method_promotion_review(
        _restricted_base(
            claim_authorization_report={
                "overall_status": "CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS",
                "blocked_claims": ["CAUSAL_CLAIM", "ROI_CLAIM"],
            }
        )
    )
    assert "CAUSAL_CERTIFIED" in report.prohibited_surfaces
    assert "ROI_CERTIFIED" in report.prohibited_surfaces


def test_claim_authorization_blocked_produces_blocked_review() -> None:
    report = generate_method_promotion_review(
        _restricted_base(
            claim_authorization_report={"overall_status": CLAIM_AUTHORIZATION_BLOCKED},
        )
    )
    assert report.candidate_verdict == "BLOCKED"
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "CLAIM_AUTHORIZATION_BLOCKED"


def test_eligible_restricted_use_review_does_not_promote_method() -> None:
    report = generate_method_promotion_review(_restricted_base())
    assert report.candidate_verdict == "ELIGIBLE_FOR_RESTRICTED_USE_REVIEW"
    assert report.authorization_boundary_report["method_promoted"] is False
    assert report.authorization_boundary_report["production_authorization_granted"] is False
    assert report.candidate_verdict not in {"PROMOTED", "PRODUCTION_APPROVED", "METHOD_UNBLOCKED"}


def test_eligible_production_review_does_not_authorize_production() -> None:
    report = generate_method_promotion_review(_production_base())
    assert report.candidate_verdict == "ELIGIBLE_FOR_PRODUCTION_REVIEW"
    assert report.authorization_boundary_report["production_authorization_granted"] is False
    assert report.authorization_boundary_report["method_promoted"] is False
    assert report.authorization_boundary_report["production_catalog_unblocked"] is False
    assert report.review_status == "PROMOTION_REVIEW_REQUIRES_HUMAN_GOVERNANCE"


def test_current_catalog_status_is_preserved() -> None:
    report = generate_method_promotion_review(
        _production_base(current_catalog_status="PRODUCTION_CATALOG_RESEARCH_ONLY")
    )
    assert report.current_catalog_status == "PRODUCTION_CATALOG_RESEARCH_ONLY"
    assert report.authorization_boundary_report["catalog_status_preserved"] is True


def test_list_input_returns_multiple_independent_reviews_without_ranking() -> None:
    reports = generate_method_promotion_review([
        _restricted_base(request_id="a"),
        _restricted_base(request_id="b", method_id="DID_2X2_B"),
    ])
    assert isinstance(reports, list)
    assert len(reports) == 2
    assert reports[0].request_id == "a"
    assert reports[1].request_id == "b"
    assert reports[0].review_id != reports[1].review_id


@dataclass
class PromotionReviewInput:
    request_id: str
    method_id: str
    instrument_id: str
    requested_promotion_scope: str
    method_suitability_report: dict
    statistical_promotion_report: dict
    trusted_readout_report: dict
    claim_authorization_report: dict
    known_limitations: list[str]


def test_dataclass_like_input_supported() -> None:
    inp = PromotionReviewInput(
        request_id="dc_001",
        method_id="DID_2X2",
        instrument_id="DID_2X2_POINT_ESTIMATE",
        requested_promotion_scope="RESTRICTED_USE_REVIEW",
        method_suitability_report={"suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW"},
        statistical_promotion_report={"status": STATISTICAL_PROMOTION_PASSED},
        trusted_readout_report={"report_status": "TRUSTED_REPORT_READY"},
        claim_authorization_report={"overall_status": "CLAIM_AUTHORIZATION_COMPLETED"},
        known_limitations=["point_estimate_only"],
    )
    report = generate_method_promotion_review(inp)
    assert isinstance(report, MethodPromotionReviewRuntimeReport)
    assert report.request_id == "dc_001"


def test_deterministic_review_id_and_provenance_hash() -> None:
    payload = _restricted_base()
    first = generate_method_promotion_review(payload)
    second = generate_method_promotion_review(payload)
    assert first.review_id == second.review_id
    assert first.provenance_hash == second.provenance_hash
    changed = generate_method_promotion_review(_restricted_base(method_id="OTHER_METHOD"))
    assert changed.review_id != first.review_id


def test_all_forbidden_promotion_flags_false() -> None:
    report = generate_method_promotion_review(_production_base())
    for flag, expected in _AUTH_FALSE.items():
        assert report.authorization_boundary_report[flag] is expected, flag


def test_positive_capability_flags_in_summary() -> None:
    run_validation(write_summary=True)
    data = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key, expected in _POSITIVE_FLAGS.items():
        assert data[key] is expected, key
    for key, expected in _AUTH_FALSE.items():
        assert data[key] is expected, key


def test_run_validation() -> None:
    result = run_validation(write_summary=False)
    assert result["verdict"] == (
        "method_promotion_review_runtime_implemented_no_method_promotion_or_production_authorization"
    )
    assert result["failed_scenarios"] == []

