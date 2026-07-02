"""Tests for ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.estimator_inference_execution_runtime_001 import (
    DIAGNOSTIC_EXECUTION_CANDIDATE,
    INSTRUMENT_EXECUTION_BLOCKED,
    INSTRUMENT_EXECUTION_NOT_RUN,
    NOT_EVALUATED_EXECUTION_CANDIDATE,
    PRIMARY_EXECUTION_CANDIDATE,
    SENSITIVITY_EXECUTION_CANDIDATE,
    EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT,
    EXECUTION_BLOCKED_BY_DATA_CONTRACT,
    EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA,
    EXECUTION_BLOCKED_BY_READOUT_PLAN,
    EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS,
    EXECUTION_PROVISIONAL,
    EstimatorInferenceExecutionRuntimeConfig,
    execute_estimator_inference,
    execute_readout_instruments,
    run_estimator_inference_execution,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001_REPORT.md"


def _base_request(**extra: object) -> dict:
    req = {
        "design_id": "design_execution_test",
        "readout_plan_status": "READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT",
        "readout_plan_packet": {"artifact_id": "READOUT_PLAN_RUNTIME_001"},
        "planned_primary_candidates": [
            {
                "instrument_id": "DID_BOOTSTRAP",
                "estimator_family": "DID_FAMILY",
                "inference_family": "BOOTSTRAP_INFERENCE_FAMILY",
                "execution_role": PRIMARY_EXECUTION_CANDIDATE,
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
                "pre_period": ["2025w01", "2025w12"],
                "test_period": ["2025w13", "2025w20"],
                "covariate_fields": ["baseline_sales"],
                "spend_fields": ["spend"],
                "geo_fields": ["state"],
                "required_input_grain": "geo_week",
                "uncertainty_semantics": "bootstrap",
                "interval_type": "percentile",
                "p_value_semantics": "two_sided",
                "diagnostic_requirements": ["placebo_check"],
                "sensitivity_requirements": ["donor_pool_sensitivity"],
                "governance_restrictions": ["no_production_authorization"],
                "warnings": [],
                "blocking_reasons": [],
            }
        ],
        "planned_sensitivity_candidates": [
            {
                "instrument_id": "TBR_RIDGE_BRB",
                "estimator_family": "TBR_RIDGE_FAMILY",
                "inference_family": "BRB_INFERENCE_FAMILY",
                "execution_role": SENSITIVITY_EXECUTION_CANDIDATE,
                "planning_category": "PLANNING_RESTRICTED_REQUIRES_REVIEW",
                "governance_status": "RESTRICTED",
                "estimand_type": "STANDARD_INCREMENTALITY",
                "metric_name": "sales",
                "assignment_artifact_id": "assignment_artifact_001",
                "uncertainty_semantics": "bootstrap",
                "diagnostic_requirements": [],
                "sensitivity_requirements": [],
                "governance_restrictions": ["restricted_reporting"],
            }
        ],
        "planned_diagnostic_candidates": [
            {
                "instrument_id": "SCM_PLACEBO",
                "estimator_family": "SCM_FAMILY",
                "inference_family": "PLACEBO_INFERENCE_FAMILY",
                "execution_role": DIAGNOSTIC_EXECUTION_CANDIDATE,
                "planning_category": "PLANNING_DIAGNOSTIC_ONLY",
                "governance_status": "DIAGNOSTIC_ONLY",
                "estimand_type": "STANDARD_INCREMENTALITY",
                "metric_name": "sales",
                "assignment_artifact_id": "assignment_artifact_001",
                "uncertainty_semantics": "placebo",
                "diagnostic_requirements": [],
                "sensitivity_requirements": [],
                "governance_restrictions": ["diagnostic_only"],
            }
        ],
        "blocked_instruments": [
            {
                "instrument_id": "AB_STANDARD",
                "execution_role": "BLOCKED_EXECUTION_CANDIDATE",
                "planning_category": "PLANNING_BLOCKED",
                "governance_status": "BLOCKED",
                "blocking_reasons": ["invalid design pairing"],
            }
        ],
        "not_evaluated_instruments": [
            {
                "instrument_id": "UNKNOWN_METHOD",
                "execution_role": NOT_EVALUATED_EXECUTION_CANDIDATE,
                "planning_category": "PLANNING_NOT_EVALUATED",
                "governance_status": "NOT_EVALUATED",
            }
        ],
        "assignment_artifact": {"artifact_id": "assignment_artifact_001"},
        "assignment_artifact_id": "assignment_artifact_001",
        "assignment_candidate": {"candidate_id": "candidate_001"},
        "reproducibility_manifest": {"seed_policy": "deterministic"},
        "execution_data_contract": {
            "panel_data_reference": "panel_data_001",
            "required_columns": ["geo_id", "week", "sales", "treated"],
            "available_columns": ["geo_id", "week", "sales", "treated", "spend"],
            "required_grain": "geo_week",
            "actual_grain": "geo_week",
            "required_time_window": "2025w01-2025w20",
            "available_time_window": "2025w01-2025w20",
            "required_geo_unit_coverage": "full",
            "available_geo_unit_coverage": "full",
            "required_treatment_assignment_join": True,
            "treatment_assignment_join_available": True,
            "required_metric_availability": True,
            "metric_available": True,
            "required_covariate_availability": False,
            "covariates_available": True,
            "required_spend_availability": False,
            "spend_available": True,
            "missingness_policy": "block",
            "duplicate_policy": "block",
            "outlier_policy": "flag",
            "data_version": "v1",
            "data_hash": "hash_001",
        },
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY", "estimand": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "bootstrap"},
        "diagnostic_prerequisites": ["placebo_check"],
        "sensitivity_prerequisites": ["donor_pool_sensitivity"],
        "production_governance_config": {"blocked_roles": ["production"]},
    }
    req.update(extra)
    return req


def test_public_api_exists() -> None:
    report = execute_estimator_inference(_base_request())
    assert report.artifact_id == "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001"
    assert execute_readout_instruments(_base_request()).artifact_id == report.artifact_id
    assert run_estimator_inference_execution(_base_request()).artifact_id == report.artifact_id


def test_blocked_readout_plan_blocks_execution() -> None:
    report = execute_estimator_inference(_base_request(readout_plan_status="READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS"))
    assert report.execution_status == EXECUTION_BLOCKED_BY_READOUT_PLAN


def test_missing_assignment_artifact_blocks_execution() -> None:
    req = _base_request()
    req.pop("assignment_artifact")
    req.pop("assignment_artifact_id")
    req.pop("assignment_candidate")
    report = execute_estimator_inference(req)
    assert report.execution_status == EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT


def test_missing_reproducibility_manifest_blocks_execution() -> None:
    req = _base_request()
    req.pop("reproducibility_manifest")
    report = execute_estimator_inference(req)
    assert report.execution_status == EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT


def test_missing_execution_data_contract_blocks_execution() -> None:
    req = _base_request()
    req.pop("execution_data_contract")
    report = execute_estimator_inference(req)
    assert report.execution_status == EXECUTION_BLOCKED_BY_DATA_CONTRACT


def test_missing_required_columns_blocks_execution() -> None:
    req = _base_request()
    req["execution_data_contract"]["required_columns"] = ["geo_id", "week", "sales", "treated", "missing_col"]
    report = execute_estimator_inference(req)
    assert any(
        r.execution_readiness_status == EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA
        for r in report.instrument_execution_results
    )


def test_missing_treatment_assignment_join_blocks_execution() -> None:
    req = _base_request()
    req["execution_data_contract"]["treatment_assignment_join_available"] = False
    report = execute_estimator_inference(req)
    assert any(
        r.execution_readiness_status == EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA
        for r in report.instrument_execution_results
    )


def test_missing_estimand_blocks_execution() -> None:
    req = _base_request()
    req.pop("estimand_scope")
    report = execute_estimator_inference(req)
    assert any(
        r.execution_readiness_status == "EXECUTION_BLOCKED_BY_ESTIMAND"
        for r in report.instrument_execution_results
    )


def test_missing_uncertainty_semantics_blocks_or_provisionalizes() -> None:
    req = _base_request()
    req["planned_primary_candidates"][0].pop("uncertainty_semantics")
    blocked = execute_estimator_inference(req)
    assert any(
        r.execution_readiness_status == EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS
        for r in blocked.instrument_execution_results
    )
    cfg = EstimatorInferenceExecutionRuntimeConfig(block_on_missing_uncertainty_semantics=False)
    provisional = execute_estimator_inference(req, config=cfg)
    assert any(
        r.execution_readiness_status in (EXECUTION_PROVISIONAL, EXECUTION_BLOCKED_BY_READOUT_PLAN)
        for r in provisional.instrument_execution_results
    )


def test_diagnostic_only_candidate_remains_diagnostic_role() -> None:
    report = execute_estimator_inference(_base_request())
    diag = next(r for r in report.instrument_execution_results if r.instrument_id == "SCM_PLACEBO")
    assert diag.execution_role == DIAGNOSTIC_EXECUTION_CANDIDATE


def test_blocked_instrument_remains_blocked() -> None:
    report = execute_estimator_inference(_base_request())
    blocked = next(r for r in report.instrument_execution_results if r.instrument_id == "AB_STANDARD")
    assert blocked.instrument_execution_status == INSTRUMENT_EXECUTION_BLOCKED


def test_not_evaluated_instrument_remains_not_evaluated() -> None:
    report = execute_estimator_inference(_base_request())
    not_eval = next(r for r in report.instrument_execution_results if r.instrument_id == "UNKNOWN_METHOD")
    assert "NOT_EVALUATED" in not_eval.governance_status


def test_primary_and_sensitivity_candidates_preserved() -> None:
    report = execute_estimator_inference(_base_request())
    assert "DID_BOOTSTRAP" in report.primary_execution_candidates
    assert "TBR_RIDGE_BRB" in report.sensitivity_execution_candidates


def test_execution_results_emitted_without_completed_execution() -> None:
    report = execute_estimator_inference(_base_request())
    assert report.instrument_execution_results
    assert all(r.instrument_execution_status != "INSTRUMENT_EXECUTION_COMPLETED" for r in report.instrument_execution_results)
    assert any(r.instrument_execution_status == INSTRUMENT_EXECUTION_NOT_RUN for r in report.instrument_execution_results)


def test_failure_packet_emitted_for_missing_data_contract() -> None:
    req = _base_request()
    req.pop("execution_data_contract")
    report = execute_estimator_inference(req)
    assert report.failure_packets
    assert any("execution_data_contract" in fp["missing_inputs"] for fp in report.failure_packets)


def test_failure_packet_retry_categories_populated() -> None:
    req = _base_request()
    req.pop("execution_data_contract")
    report = execute_estimator_inference(req)
    assert any("FIX_INPUT_DATA_CONTRACT" in fp["suggested_retry_categories"] for fp in report.failure_packets)


def test_execution_trace_and_provenance_emitted() -> None:
    report = execute_estimator_inference(_base_request())
    assert report.execution_trace["execution_id"]
    assert report.execution_provenance_manifest["data_hash"] == "hash_001"


def test_effect_uncertainty_diagnostic_reports_not_computed() -> None:
    report = execute_estimator_inference(_base_request())
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_BOOTSTRAP")
    assert row.effect_estimate_report["effect_estimate_report_status"] == "NOT_COMPUTED"
    assert row.uncertainty_report["uncertainty_report_status"] == "NOT_COMPUTED"
    assert row.inference_diagnostic_report["inference_diagnostic_report_status"] == "NOT_COMPUTED"


def test_multiple_requests_return_multiple_reports_without_ranking() -> None:
    r1 = _base_request(design_id="d1")
    r2 = _base_request(design_id="d2")
    report = execute_estimator_inference([r1, r2])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert report.aggregate_summary is not None


def test_claim_boundary_flags_remain_false_for_authorization() -> None:
    report = execute_estimator_inference(_base_request())
    cb = report.claim_boundary_report
    assert cb["estimator_inference_execution_runtime_implemented"] is True
    assert cb["execution_readiness_evaluated"] is True
    assert cb["instrument_execution_completed"] is False
    assert cb["causal_claim_authorized"] is False
    assert cb["production_authorization_granted"] is False
    assert cb["mmm_runtime_calls_implemented"] is False


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "estimator_inference_execution_runtime_implemented_readiness_and_execution_packets_only_"
        "no_estimator_or_inference_execution"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["estimator_inference_execution_runtime_implemented"] is True
    assert summary["execution_readiness_evaluated"] is True
    assert summary["instrument_execution_completed"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
