"""Tests for ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.estimator_inference_execution_runtime_001 import (
    DIAGNOSTIC_EXECUTION_CANDIDATE,
    EXECUTION_BLOCKED_BY_ASSIGNMENT_PANEL_INTEGRITY,
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
from panel_exp.validation.estimator_inference_executor_adapters_002 import (
    EXECUTOR_AVAILABLE_FOR_DRY_RUN,
    EXECUTOR_NOT_EVALUATED,
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
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "estimator_family": "DID_FAMILY",
                "inference_family": "POINT_ESTIMATE_ONLY",
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
                "uncertainty_semantics": "point_estimate_only",
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
        "uncertainty_scope": {"semantics": "point_estimate_only"},
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
    assert "DID_2X2_POINT_ESTIMATE" in report.primary_execution_candidates
    assert "TBR_RIDGE_BRB" in report.sensitivity_execution_candidates


def test_execution_results_emitted_without_completed_execution() -> None:
    report = execute_estimator_inference(_base_request())
    assert report.instrument_execution_results
    assert all(r.instrument_execution_status != "INSTRUMENT_EXECUTION_COMPLETED" for r in report.instrument_execution_results)
    assert any(r.instrument_execution_status == INSTRUMENT_EXECUTION_NOT_RUN for r in report.instrument_execution_results)


def test_runtime_includes_executor_lookup_fields() -> None:
    report = execute_estimator_inference(_base_request())
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_2X2_POINT_ESTIMATE")
    assert row.executor_lookup_status in (EXECUTOR_AVAILABLE_FOR_DRY_RUN, EXECUTOR_NOT_EVALUATED)
    assert row.executor_supports_execution is False
    assert row.executor_request is not None
    assert row.executor_result is not None
    assert row.executor_trace is not None


def test_runtime_preserves_behavior_when_registry_disabled() -> None:
    cfg = EstimatorInferenceExecutionRuntimeConfig(enable_governed_executor_registry=False)
    report = execute_estimator_inference(_base_request(), config=cfg)
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_2X2_POINT_ESTIMATE")
    assert row.executor_lookup_status == "EXECUTOR_NOT_IMPLEMENTED"
    assert row.executor_request is None
    assert report.executor_registry_summary["registry_enabled"] is False


def test_multiple_instruments_produce_lookup_results() -> None:
    report = execute_estimator_inference(_base_request())
    assert len(report.executor_lookup_results) >= 3
    assert isinstance(report.executor_availability_counts, dict)


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
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_2X2_POINT_ESTIMATE")
    assert row.effect_estimate_report["effect_estimate_report_status"] == "NOT_COMPUTED"


def _did_panel() -> list[dict]:
    return [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1, "cell_id": "T1"},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1, "cell_id": "T1"},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0, "cell_id": "C0"},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0, "cell_id": "C0"},
    ]


def _did_unit_allocations() -> list[dict]:
    return [
        {"geo_id": "g1", "assigned_cell_id": "T1", "assigned_cell_role": "TREATMENT"},
        {"geo_id": "g2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL"},
    ]


def test_did_point_estimate_integrated_when_config_enabled() -> None:
    cfg = EstimatorInferenceExecutionRuntimeConfig(allow_governed_did_point_estimate_execution=True)
    report = execute_estimator_inference(
        _base_request(
            panel_data=_did_panel(),
            unit_allocations=_did_unit_allocations(),
            assignment_artifact={
                "artifact_id": "assignment_artifact_001",
                "unit_allocations": _did_unit_allocations(),
            },
        ),
        config=cfg,
    )
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_2X2_POINT_ESTIMATE")
    assert row.instrument_execution_status == "INSTRUMENT_EXECUTION_COMPLETED"
    assert row.effect_estimate_report["point_estimate"] == 9.0
    assert row.uncertainty_report["uncertainty_report_status"] == "NOT_COMPUTED"
    assert report.claim_boundary_report["did_point_estimate_computed"] is True
    assert report.claim_boundary_report["p_value_computed"] is False
    assert report.claim_boundary_report["assignment_panel_integrity_gate_integrated_with_execution_runtime"] is True


def test_execution_runtime_blocks_when_integrity_fails() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 0, "cell_id": "T1"},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0, "cell_id": "C0"},
    ]
    cfg = EstimatorInferenceExecutionRuntimeConfig(allow_governed_did_point_estimate_execution=True)
    report = execute_estimator_inference(
        _base_request(
            panel_data=panel,
            unit_allocations=_did_unit_allocations(),
        ),
        config=cfg,
    )
    assert report.execution_status == EXECUTION_BLOCKED_BY_ASSIGNMENT_PANEL_INTEGRITY
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_2X2_POINT_ESTIMATE")
    assert row.instrument_execution_status == INSTRUMENT_EXECUTION_BLOCKED


def test_did_dry_run_preserved_when_config_disabled() -> None:
    report = execute_estimator_inference(_base_request())
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_2X2_POINT_ESTIMATE")
    assert row.instrument_execution_status == INSTRUMENT_EXECUTION_NOT_RUN
    assert row.executor_lookup_status == EXECUTOR_AVAILABLE_FOR_DRY_RUN
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


def test_production_catalog_blocklist_blocks_production_context_execution() -> None:
    req = _base_request(
        production_context="production",
        claim_type="INCREMENTAL_LIFT_CLAIM",
    )
    report = execute_estimator_inference(req)
    inst = report.instrument_execution_results[0]
    assert inst.instrument_execution_status == INSTRUMENT_EXECUTION_BLOCKED
    assert any("production catalog" in reason for reason in inst.blocking_reasons)
