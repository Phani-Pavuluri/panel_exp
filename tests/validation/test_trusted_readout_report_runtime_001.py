"""Tests for TRUSTED_READOUT_REPORT_RUNTIME_001."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
)
from panel_exp.validation.claim_authorization_runtime_001 import (
    CLAIM_AUTHORIZED_WITH_RESTRICTIONS,
    CLAIM_BLOCKED,
    authorize_readout_claims,
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
    SRM_BALANCE_DIAGNOSTIC_PASSED,
)
from panel_exp.validation.statistical_promotion_thresholds_001 import (
    STATISTICAL_PROMOTION_PASSED,
)
from panel_exp.validation.trusted_readout_report_runtime_001 import (
    TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION,
    TRUSTED_REPORT_READY,
    TRUSTED_REPORT_READY_WITH_REDACTIONS,
    TrustedReadoutReportRuntimeReport,
    build_trusted_readout_report,
    create_trusted_readout_packet,
    generate_trusted_readout_report,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/TRUSTED_READOUT_REPORT_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/TRUSTED_READOUT_REPORT_RUNTIME_001_REPORT.md"


def _claim_scope() -> dict:
    return {
        "estimand": "STANDARD_INCREMENTALITY",
        "population_scope": "eligible_dma",
        "time_window": "post_period",
        "metric_kpi": "sales",
    }


def _integrity(**extra: object) -> dict:
    return {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED, "artifact_id": "integrity_001", **extra}


def _srm(**extra: object) -> dict:
    return {"status": SRM_BALANCE_DIAGNOSTIC_PASSED, "artifact_id": "srm_001", **extra}


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


def _claim_requests(*claim_types: str) -> list[dict]:
    return [{"claim_type": ct, "claim_scope": _claim_scope()} for ct in claim_types]


def _base_request(**extra: object) -> dict:
    payload = {
        "request_id": "trusted_report_test_001",
        "design_id": "design_trusted_001",
        "claim_scope": _claim_scope(),
        "claim_requests": _claim_requests("POINT_ESTIMATE_DESCRIPTION"),
        "assignment_panel_integrity_report": _integrity(),
        "srm_balance_diagnostic_report": _srm(),
        "diagnostics_sensitivity_report": {
            "evidence_sufficiency_status": EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
            "artifact_id": "diag_001",
        },
        "statistical_promotion_report": {"status": STATISTICAL_PROMOTION_PASSED, "artifact_id": "promo_001"},
        "governed_randomization_report": {"status": GOVERNED_RANDOMIZATION_COMPLETED, "artifact_id": "rand_001"},
        "production_catalog_report": {"status": "PRODUCTION_CATALOG_RESEARCH_ONLY", "artifact_id": "catalog_001"},
        "method_suitability_report": {"artifact_id": "method_001"},
        "instrument_execution_results": _execution_results(),
        "execution_result": {"execution_status": "INSTRUMENT_EXECUTION_COMPLETED", "artifact_id": "exec_001"},
        "execution_artifact_manifest": {"artifact_id": "manifest_001"},
        "evidence_sources": {"execution": "exec_001"},
        "lineage_manifest": {"artifact_id": "lineage_001", "seed_policy": "fixed"},
    }
    payload.update(extra)
    return payload


def _section(report: TrustedReadoutReportRuntimeReport, section_type: str):
    return next(s for s in report.sections if s.section_type == section_type)


def test_public_api_exists() -> None:
    report = generate_trusted_readout_report(_base_request())
    assert isinstance(report, TrustedReadoutReportRuntimeReport)
    assert build_trusted_readout_report(_base_request()).report_id == report.report_id
    assert create_trusted_readout_packet(_base_request()).request_id == "trusted_report_test_001"


def test_blocks_claim_bearing_sections_when_claim_authorization_missing() -> None:
    report = generate_trusted_readout_report({"request_id": "no_auth"})
    assert report.report_status == TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION
    assert "AUTHORIZED_CLAIMS" in report.blocked_sections or "EXECUTIVE_SUMMARY" in report.blocked_sections
    assert report.failure_packet is not None
    assert report.failure_packet["failure_code"] == "MISSING_CLAIM_AUTHORIZATION_REPORT"


def test_builds_restricted_point_estimate_section_with_caveats() -> None:
    report = generate_trusted_readout_report(_base_request())
    pe = _section(report, "POINT_ESTIMATE_SUMMARY")
    assert pe.section_status == "SECTION_ALLOWED_WITH_RESTRICTIONS"
    assert "POINT_ESTIMATE_ONLY" in pe.required_caveats or any(
        "POINT_ESTIMATE_ONLY" in str(s) for s in pe.allowed_surface
    )
    assert pe.bound_claim_authorization_ids


def test_redacts_uncertainty_section_when_uncertainty_missing() -> None:
    report = generate_trusted_readout_report(
        _base_request(claim_requests=_claim_requests("POINT_ESTIMATE_DESCRIPTION", "CONFIDENCE_INTERVAL_CLAIM"))
    )
    unc = _section(report, "UNCERTAINTY_SUMMARY")
    assert unc.section_status in {"SECTION_REDACTED", "SECTION_BLOCKED"}
    assert "UNCERTAINTY_SUMMARY" in report.redacted_sections or "UNCERTAINTY_SUMMARY" in report.blocked_sections


def test_redacts_significance_surface_when_claims_blocked() -> None:
    report = generate_trusted_readout_report(
        _base_request(claim_requests=_claim_requests("STATISTICAL_SIGNIFICANCE_CLAIM"))
    )
    unc = _section(report, "UNCERTAINTY_SUMMARY")
    assert unc.section_status in {"SECTION_REDACTED", "SECTION_BLOCKED"}
    blocked = [s for s in report.sections if s.blocked_surface]
    assert blocked or unc.redaction_reason


def test_renders_roi_claim_only_as_blocked_summary() -> None:
    report = generate_trusted_readout_report(_base_request(claim_requests=_claim_requests("ROI_CLAIM")))
    blocked_section = _section(report, "BLOCKED_CLAIMS")
    assert blocked_section.section_status in {"SECTION_ALLOWED", "SECTION_NOT_EVALUATED"}
    assert report.blocked_claim_summaries
    assert report.blocked_claim_summaries[0]["status"] == "NOT_AUTHORIZED"
    assert report.claim_boundary_report["roi_claim_authorized"] is False


def test_blocks_recommendation_section_without_trusted_authorization() -> None:
    report = generate_trusted_readout_report(
        _base_request(
            claim_requests=_claim_requests("TRUSTED_BUSINESS_RECOMMENDATION"),
            trusted_surface_policy={"allow_recommendation_section": True},
        )
    )
    rec = _section(report, "RECOMMENDATION_SECTION")
    assert rec.section_status == "SECTION_BLOCKED"
    assert report.claim_boundary_report["trusted_business_recommendation_authorized"] is False


def test_includes_assignment_integrity_section_when_evidence_exists() -> None:
    report = generate_trusted_readout_report(_base_request())
    sec = _section(report, "ASSIGNMENT_INTEGRITY_SUMMARY")
    assert sec.section_status == "SECTION_ALLOWED"
    assert sec.bound_evidence_ids


def test_includes_randomization_section_when_evidence_exists() -> None:
    report = generate_trusted_readout_report(_base_request())
    sec = _section(report, "RANDOMIZATION_SUMMARY")
    assert sec.section_status == "SECTION_ALLOWED"


def test_includes_srm_balance_section_when_evidence_exists() -> None:
    report = generate_trusted_readout_report(_base_request())
    sec = _section(report, "SRM_BALANCE_SUMMARY")
    assert sec.section_status == "SECTION_ALLOWED"


def test_includes_statistical_promotion_section_when_evidence_exists() -> None:
    report = generate_trusted_readout_report(_base_request())
    sec = _section(report, "STATISTICAL_PROMOTION_SUMMARY")
    assert sec.section_status == "SECTION_ALLOWED"


def test_includes_production_catalog_status_without_production_approval() -> None:
    report = generate_trusted_readout_report(_base_request())
    sec = _section(report, "PRODUCTION_CATALOG_STATUS")
    assert sec.section_status == "SECTION_ALLOWED"
    assert "NO_PRODUCTION_AUTHORIZATION" in sec.required_caveats
    assert report.claim_boundary_report["production_authorization_granted"] is False


def test_propagates_required_caveats_from_claim_authorization() -> None:
    report = generate_trusted_readout_report(_base_request())
    assert report.required_caveats
    caveats_sec = _section(report, "CAVEATS_AND_LIMITATIONS")
    assert caveats_sec.section_status == "SECTION_ALLOWED"
    assert caveats_sec.required_caveats


def test_binds_non_empty_sections_to_claim_or_evidence_ids() -> None:
    report = generate_trusted_readout_report(_base_request())
    for sec in report.sections:
        if sec.section_status in {"SECTION_ALLOWED", "SECTION_ALLOWED_WITH_RESTRICTIONS"}:
            assert sec.bound_claim_authorization_ids or sec.bound_evidence_ids


def test_preserves_blocked_claims_only_as_not_authorized_summaries() -> None:
    report = generate_trusted_readout_report(_base_request(claim_requests=_claim_requests("ROI_CLAIM", "POINT_ESTIMATE_DESCRIPTION")))
    for summary in report.blocked_claim_summaries:
        assert summary["status"] == "NOT_AUTHORIZED"
    blocked = _section(report, "BLOCKED_CLAIMS")
    for surface in blocked.blocked_surface:
        assert surface["surface_type"] == "BLOCKED_CLAIM_NOTICE"


def test_list_input_returns_multiple_reports_without_ranking() -> None:
    reports = generate_trusted_readout_report(
        [_base_request(request_id="a"), _base_request(request_id="b")]
    )
    assert len(reports) == 2
    assert {r.request_id for r in reports} == {"a", "b"}


@dataclass
class _TrustedInput:
    request_id: str
    claim_requests: list[dict]
    claim_scope: dict
    assignment_panel_integrity_report: dict
    instrument_execution_results: list[dict]
    execution_result: dict


def test_dataclass_like_input_supported() -> None:
    report = generate_trusted_readout_report(
        _TrustedInput(
            request_id="dc_001",
            claim_requests=_claim_requests("POINT_ESTIMATE_DESCRIPTION"),
            claim_scope=_claim_scope(),
            assignment_panel_integrity_report=_integrity(),
            instrument_execution_results=_execution_results(),
            execution_result={"execution_status": "INSTRUMENT_EXECUTION_COMPLETED"},
        )
    )
    assert report.report_status in {
        TRUSTED_REPORT_READY,
        TRUSTED_REPORT_READY_WITH_REDACTIONS,
        TRUSTED_REPORT_BLOCKED_BY_CLAIM_AUTHORIZATION,
    }


def test_deterministic_report_id_and_provenance_hash() -> None:
    req = _base_request()
    first = generate_trusted_readout_report(req)
    second = generate_trusted_readout_report(req)
    assert first.report_id == second.report_id
    assert first.provenance_hash == second.provenance_hash


def test_execution_runtime_attaches_trusted_report_when_requested() -> None:
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
        "design_id": "exec_trusted_report",
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
        "execution_data_contract": {"panel_data": panel, "data_hash": "hash_001"},
        "panel_data": panel,
        "unit_allocations": allocs,
        "assignment_artifact": {"artifact_id": "assignment_artifact_001", "unit_allocations": allocs},
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "point_estimate_only"},
        "claim_requests": [{"claim_type": "POINT_ESTIMATE_DESCRIPTION", "claim_scope": _claim_scope()}],
        "claim_scope": _claim_scope(),
        "assignment_panel_integrity_report": _integrity(),
        "srm_balance_diagnostic_report": _srm(),
        "generate_trusted_report": True,
    }
    cfg = EstimatorInferenceExecutionRuntimeConfig(allow_governed_did_point_estimate_execution=True)
    report = execute_estimator_inference(req, config=cfg)
    assert "trusted_readout_report" in report.execution_packet
    assert report.execution_packet["trusted_readout_report"]["report_id"]


def test_readout_plan_adds_trusted_report_prerequisite_when_enabled() -> None:
    req = {
        "design_id": "design_trusted_plan",
        "readout_method_governance_status": "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING",
        "assignment_artifact_status": "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE",
        "assignment_plan": {"artifact_id": "assignment_plan_001"},
        "assignment_candidate": {"candidate_id": "assignment_candidate_001"},
        "reproducibility_manifest": {"seed_policy": "NOT_APPLICABLE"},
        "instrument_suitability_matrix": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "estimator_family": "DID_FAMILY",
                "inference_family": "POINT_ESTIMATE_ONLY",
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
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "point_estimate_only"},
        "required_diagnostics": ["did_coverage"],
        "required_sensitivity_checks": ["leave_one_out"],
    }
    cfg = ReadoutPlanRuntimeConfig(add_trusted_readout_report_prerequisites=True)
    plan = build_readout_plan(req, config=cfg)
    assert "trusted_readout_report_required" in plan.readout_plan_packet["execution_prerequisites"]


def test_all_forbidden_authorization_flags_false() -> None:
    report = generate_trusted_readout_report(_base_request())
    cb = report.claim_boundary_report
    assert cb["trusted_readout_report_runtime_implemented"] is True
    assert cb["trusted_readout_report_packet_generated"] is True
    assert cb["production_authorization_granted"] is False
    assert cb["production_readout_authorized"] is False
    assert cb["authorized_claim_text_generated"] is False
    assert cb["polished_narrative_generated"] is False
    assert cb["causal_claim_authorized"] is False
    assert cb["roi_claim_authorized"] is False
    assert cb["estimator_implemented"] is False
    assert cb["uncertainty_computed"] is False


def test_report_file_exists() -> None:
    assert _REPORT.exists()
