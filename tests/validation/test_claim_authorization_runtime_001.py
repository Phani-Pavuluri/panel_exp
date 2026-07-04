"""Tests for CLAIM_AUTHORIZATION_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
)
from panel_exp.validation.claim_authorization_runtime_001 import (
    CLAIM_AUTHORIZATION_BLOCKED,
    CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS,
    CLAIM_AUTHORIZATION_INSUFFICIENT_EVIDENCE,
    CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
    CLAIM_BLOCKED,
    CLAIM_INSUFFICIENT_EVIDENCE,
    BLOCKER_EFFECT_ESTIMATE_MISSING,
    BLOCKER_INFERENCE_NOT_IMPLEMENTED,
    BLOCKER_TRUSTED_REPORT_RUNTIME_MISSING,
    ClaimAuthorizationRuntimeReport,
    authorize_claims,
    authorize_readout_claims,
    evaluate_claim_authorization,
    run_validation,
)
from panel_exp.validation.estimator_inference_did_executor_003 import (
    EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
)
from panel_exp.validation.estimator_inference_execution_runtime_001 import (
    EstimatorInferenceExecutionRuntimeConfig,
    execute_estimator_inference,
)
from panel_exp.validation.governed_randomization_runtime_001 import (
    GOVERNED_RANDOMIZATION_COMPLETED,
)
from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
)
from panel_exp.validation.readout_plan_runtime_001 import (
    ReadoutPlanRuntimeConfig,
    build_readout_plan,
)
from panel_exp.validation.srm_balance_readout_diagnostic_001 import (
    SRM_BALANCE_DIAGNOSTIC_FAILED,
    SRM_BALANCE_DIAGNOSTIC_PASSED,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    STATISTICAL_PROMOTION_FAILED,
    STATISTICAL_PROMOTION_PASSED,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/CLAIM_AUTHORIZATION_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/CLAIM_AUTHORIZATION_RUNTIME_001_REPORT.md"


def _claim_scope() -> dict:
    return {
        "estimand": "STANDARD_INCREMENTALITY",
        "population_scope": "eligible_dma",
        "time_window": "post_period",
        "metric_kpi": "sales",
    }


def _integrity(**extra: object) -> dict:
    return {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED, **extra}


def _srm(**extra: object) -> dict:
    return {"status": SRM_BALANCE_DIAGNOSTIC_PASSED, **extra}


def _effect(point: float = 9.0) -> dict:
    return {
        "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "effect_estimate_report_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "point_estimate": point,
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
    }


def _execution_results(effect: dict | None = None) -> list[dict]:
    eff = effect or _effect()
    return [
        {
            "instrument_id": "DID_2X2_POINT_ESTIMATE",
            "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
            "effect_estimate_report": eff,
            "uncertainty_report": {"uncertainty_report_status": "NOT_COMPUTED"},
        }
    ]


def _base_request(**extra: object) -> dict:
    payload = {
        "request_id": "claim_auth_test_001",
        "claim_scope": _claim_scope(),
        "assignment_panel_integrity_report": _integrity(),
        "srm_balance_diagnostic_report": _srm(),
        "diagnostics_sensitivity_report": {"evidence_sufficiency_status": EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW},
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED},
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
        "instrument_execution_results": _execution_results(),
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
    }
    payload.update(extra)
    return payload


def _authorize(claim_type: str, **extra: object) -> ClaimAuthorizationRuntimeReport:
    req = _base_request(**extra)
    req["claim_requests"] = [{"claim_type": claim_type, "claim_scope": req["claim_scope"]}]
    return authorize_readout_claims(req)


def test_public_api_exists() -> None:
    report = authorize_readout_claims(_base_request(claim_requests=[]))
    assert isinstance(report, ClaimAuthorizationRuntimeReport)
    alias = evaluate_claim_authorization(_base_request(claim_requests=[]))
    assert alias.overall_status
    assert authorize_claims(_base_request(claim_requests=[])).request_id == "claim_auth_test_001"


def test_assignment_integrity_description_authorized_with_restrictions() -> None:
    report = _authorize("ASSIGNMENT_INTEGRITY_DESCRIPTION")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS
    assert "DESCRIPTIVE_ONLY" in decision.caveat_codes


def test_srm_balance_diagnostic_description_authorized_with_restrictions() -> None:
    report = _authorize("SRM_BALANCE_DIAGNOSTIC_DESCRIPTION")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS
    assert "DIAGNOSTIC_ONLY" in decision.caveat_codes


def test_point_estimate_description_authorized_with_restrictions() -> None:
    report = _authorize("POINT_ESTIMATE_DESCRIPTION")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS
    assert "POINT_ESTIMATE_ONLY" in decision.caveat_codes
    assert "NO_CAUSAL_CLAIM" in decision.caveat_codes


def test_point_estimate_description_blocks_when_effect_missing() -> None:
    report = _authorize(
        "POINT_ESTIMATE_DESCRIPTION",
        instrument_execution_results=[],
        effect_estimate_report=None,
    )
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_INSUFFICIENT_EVIDENCE
    assert BLOCKER_EFFECT_ESTIMATE_MISSING in decision.blockers


def test_directional_result_description_restricted_when_evidence_passes() -> None:
    report = _authorize("DIRECTIONAL_RESULT_DESCRIPTION")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS
    assert "directional_sign_only" in decision.allowed_surface


def test_causal_lift_claim_blocked_without_governed_uncertainty() -> None:
    report = _authorize("CAUSAL_LIFT_CLAIM")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_BLOCKED
    assert BLOCKER_INFERENCE_NOT_IMPLEMENTED in decision.blockers


def test_incremental_conversions_claim_blocked_without_full_evidence() -> None:
    report = _authorize("INCREMENTAL_CONVERSIONS_CLAIM")
    assert report.claim_authorizations[0].authorization_status == CLAIM_BLOCKED


def test_roi_claim_blocked_without_roi_evidence() -> None:
    report = _authorize("ROI_CLAIM")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_BLOCKED
    assert "roi_evidence" in decision.missing_evidence


def test_statistical_significance_claim_blocked_without_inference() -> None:
    report = _authorize("STATISTICAL_SIGNIFICANCE_CLAIM")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_BLOCKED
    assert BLOCKER_INFERENCE_NOT_IMPLEMENTED in decision.blockers


def test_confidence_interval_claim_blocked_without_ci() -> None:
    report = _authorize("CONFIDENCE_INTERVAL_CLAIM")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_BLOCKED


def test_production_readout_claim_blocked_without_trusted_report_runtime() -> None:
    report = _authorize("PRODUCTION_READOUT_CLAIM")
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_BLOCKED
    assert BLOCKER_TRUSTED_REPORT_RUNTIME_MISSING in decision.blockers


def test_trusted_business_recommendation_blocked_without_trusted_report_runtime() -> None:
    report = _authorize("TRUSTED_BUSINESS_RECOMMENDATION")
    assert report.claim_authorizations[0].authorization_status == CLAIM_BLOCKED


def test_production_catalog_blocked_instrument_blocks_production_claim() -> None:
    report = _authorize(
        "CAUSAL_LIFT_CLAIM",
        production_context="PRODUCTION",
        instrument_id="SyntheticDID",
        production_catalog_report={"production_catalog_status": "PRODUCTION_CATALOG_RESEARCH_ONLY"},
    )
    assert report.claim_authorizations[0].authorization_status == CLAIM_BLOCKED


def test_assignment_panel_integrity_failure_blocks_causal_claim() -> None:
    report = _authorize(
        "CAUSAL_LIFT_CLAIM",
        assignment_panel_integrity_report={"status": ASSIGNMENT_PANEL_INTEGRITY_FAILED},
    )
    decision = report.claim_authorizations[0]
    assert decision.authorization_status == CLAIM_BLOCKED


def test_srm_balance_failure_blocks_causal_claim() -> None:
    report = _authorize(
        "CAUSAL_LIFT_CLAIM",
        srm_balance_diagnostic_report={"status": SRM_BALANCE_DIAGNOSTIC_FAILED},
    )
    assert report.claim_authorizations[0].authorization_status == CLAIM_BLOCKED


def test_statistical_promotion_failure_blocks_production_claim() -> None:
    report = _authorize(
        "CAUSAL_LIFT_CLAIM",
        production_context="PRODUCTION",
        statistical_promotion_report={"status": STATISTICAL_PROMOTION_FAILED},
    )
    assert report.claim_authorizations[0].authorization_status == CLAIM_BLOCKED


def test_did_2x2_supports_restricted_point_estimate_not_bootstrap() -> None:
    report = _authorize("POINT_ESTIMATE_DESCRIPTION", instrument_id="DID_2X2_POINT_ESTIMATE")
    assert report.claim_authorizations[0].authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS


def test_did_bootstrap_inference_blocks_point_estimate_claim() -> None:
    report = _authorize(
        "POINT_ESTIMATE_DESCRIPTION",
        instrument_id="DID_BOOTSTRAP",
        instrument_execution_results=[
            {
                "instrument_id": "DID_BOOTSTRAP",
                "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
                "effect_estimate_report": _effect(),
            }
        ],
    )
    assert report.claim_authorizations[0].authorization_status == CLAIM_BLOCKED


def test_randomization_artifact_description_authorized_with_restrictions() -> None:
    report = _authorize(
        "RANDOMIZATION_ARTIFACT_DESCRIPTION",
        governed_randomization_report={"status": GOVERNED_RANDOMIZATION_COMPLETED},
    )
    assert report.claim_authorizations[0].authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS


def test_list_input_returns_multiple_reports_without_ranking() -> None:
    reports = authorize_readout_claims(
        [_base_request(request_id="a"), _base_request(request_id="b")]
    )
    assert len(reports) == 2
    assert {r.request_id for r in reports} == {"a", "b"}


@dataclass
class _ClaimInput:
    request_id: str
    claim_requests: list[dict]
    claim_scope: dict
    assignment_panel_integrity_report: dict


def test_dataclass_like_input_supported() -> None:
    report = authorize_readout_claims(
        _ClaimInput(
            request_id="dc_001",
            claim_requests=[{"claim_type": "ASSIGNMENT_INTEGRITY_DESCRIPTION", "claim_scope": _claim_scope()}],
            claim_scope=_claim_scope(),
            assignment_panel_integrity_report=_integrity(),
        )
    )
    assert report.claim_authorizations[0].authorization_status == CLAIM_AUTHORIZED_WITH_RESTRICTIONS


def test_deterministic_trace_provenance_hash() -> None:
    req = _base_request(
        claim_requests=[{"claim_type": "ASSIGNMENT_INTEGRITY_DESCRIPTION", "claim_scope": _claim_scope()}]
    )
    first = authorize_readout_claims(req)
    second = authorize_readout_claims(req)
    assert first.evidence_trace["integrity_hash"] == second.evidence_trace["integrity_hash"]
    assert first.provenance["integrity_hash"] == second.provenance["integrity_hash"]


def test_all_forbidden_authorization_flags_false() -> None:
    report = _authorize("POINT_ESTIMATE_DESCRIPTION")
    cb = report.claim_boundary_report
    assert cb["claim_authorization_runtime_implemented"] is True
    assert cb["causal_claim_authorized"] is False
    assert cb["production_readout_authorized"] is False
    assert cb["authorized_claim_text_generated"] is False
    assert cb["production_authorization_granted"] is False


def test_execution_runtime_attaches_claim_authorization_when_claim_requests_supplied() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1, "cell_id": "T1"},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1, "cell_id": "T1"},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0, "cell_id": "C0"},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0, "cell_id": "C0"},
    ]
    allocs = [
        {"geo_id": "g1", "assigned_cell_id": "T1", "assigned_cell_role": "TREATMENT"},
        {"geo_id": "g2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]
    req = {
        "design_id": "exec_claim_auth",
        "readout_plan_status": "READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT",
        "readout_plan_packet": {"artifact_id": "READOUT_PLAN_RUNTIME_001"},
        "planned_primary_candidates": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "estimator_family": "DID_FAMILY",
                "inference_family": "POINT_ESTIMATE_ONLY",
                "execution_role": "PRIMARY_EXECUTION_CANDIDATE",
                "planning_category": "PLANNING_ELIGIBLE_PRIMARY_CANDIDATE",
                "governance_status": "GOVERNED",
                "estimand_type": "STANDARD_INCREMENTALITY",
                "metric_name": "sales",
                "unit_id_field": "geo_id",
                "time_field": "week",
                "outcome_field": "sales",
                "treatment_field": "treated",
                "cell_id_field": "cell_id",
                "assignment_artifact_id": "assignment_artifact_001",
                "pre_period": ["2025w01"],
                "test_period": ["2025w13"],
                "required_input_grain": "geo_week",
                "uncertainty_semantics": "point_estimate_only",
            }
        ],
        "execution_data_contract": {
            "panel_data": panel,
            "data_hash": "hash_001",
            "panel_data_reference": "panel_ref_001",
        },
        "panel_data": panel,
        "unit_allocations": allocs,
        "assignment_artifact": {"artifact_id": "assignment_artifact_001", "unit_allocations": allocs},
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "point_estimate_only"},
        "claim_requests": [
            {"claim_type": "POINT_ESTIMATE_DESCRIPTION", "claim_scope": _claim_scope()},
        ],
        "claim_scope": _claim_scope(),
        "assignment_panel_integrity_report": _integrity(),
        "srm_balance_diagnostic_report": _srm(),
    }
    cfg = EstimatorInferenceExecutionRuntimeConfig(allow_governed_did_point_estimate_execution=True)
    report = execute_estimator_inference(req, config=cfg)
    assert "claim_authorization_report" in report.execution_packet
    assert report.execution_packet["claim_authorization_report"]["overall_status"] in {
        CLAIM_AUTHORIZATION_COMPLETED_WITH_RESTRICTIONS,
        CLAIM_AUTHORIZATION_BLOCKED,
        CLAIM_AUTHORIZATION_INSUFFICIENT_EVIDENCE,
    }


def test_readout_plan_includes_claim_authorization_prerequisite_when_enabled() -> None:
    req = {
        "design_id": "design_claim_auth_plan",
        "readout_method_governance_status": "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING",
        "assignment_artifact_status": "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE",
        "assignment_plan": {"artifact_id": "assignment_plan_001"},
        "assignment_candidate": {"candidate_id": "assignment_candidate_001"},
        "reproducibility_manifest": {"seed_policy": "NOT_APPLICABLE"},
        "instrument_suitability_matrix": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "estimator_family": "DID_FAMILY",
                "governance_status": "GOVERNED",
                "planning_category": "PLANNING_ELIGIBLE_PRIMARY_CANDIDATE",
                "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
            }
        ],
        "estimand_scope": {
            "estimand_type": "STANDARD_INCREMENTALITY",
            "population_scope": "eligible_dma",
            "time_window": "post_period",
            "metric_kpi": "sales",
        },
        "uncertainty_scope": {"semantics": "point_estimate_only"},
        "required_diagnostics": ["placebo_check"],
        "required_sensitivity_checks": ["donor_pool_sensitivity"],
        "claim_scope": _claim_scope(),
    }
    report = build_readout_plan(req, config=ReadoutPlanRuntimeConfig())
    assert "claim_authorization_required" in report.execution_prerequisites


def test_overall_status_blocked_when_any_causal_claim_blocked() -> None:
    report = authorize_readout_claims(
        _base_request(
            claim_requests=[
                {"claim_type": "ASSIGNMENT_INTEGRITY_DESCRIPTION", "claim_scope": _claim_scope()},
                {"claim_type": "CAUSAL_LIFT_CLAIM", "claim_scope": _claim_scope()},
            ]
        )
    )
    assert report.overall_status == CLAIM_AUTHORIZATION_BLOCKED
    assert "CAUSAL_LIFT_CLAIM" in report.blocked_claims


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["final_verdict"] == (
        "claim_authorization_runtime_implemented_no_trusted_report_or_production_authorization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["claim_authorization_runtime_implemented"] is True
    assert summary["causal_claim_authorized"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
