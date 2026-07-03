"""Tests for READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED,
    EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS,
    EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS,
    EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY,
    EVIDENCE_PROVISIONAL,
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
    EVIDENCE_SUFFICIENT_WITH_WARNINGS,
    ReadoutDiagnosticsSensitivityRuntimeConfig,
    evaluate_diagnostics_sensitivity_evidence,
    evaluate_readout_diagnostics_sensitivity,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001_summary.json"
_REPORT = _REPO / "docs/track_d/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001_REPORT.md"


def _base_request(**extra: object) -> dict:
    req = {
        "design_id": "design_evidence_test",
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
        "execution_artifacts": {
            "execution_id": "execution_001",
            "artifact_id": "execution_001",
            "execution_completed": True,
        },
        "instrument_execution_results": [
            {
                "instrument_id": "DID_BOOTSTRAP",
                "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
                "execution_role": "PRIMARY_EXECUTION_CANDIDATE",
            }
        ],
        "diagnostic_requirements": [
            {
                "requirement_id": "diag_parallel_trend",
                "requirement_type": "PARALLEL_TREND_DIAGNOSTIC",
                "applies_to_instrument_id": "DID_BOOTSTRAP",
                "applies_to_execution_role": "PRIMARY_EXECUTION_CANDIDATE",
                "required_for_production": True,
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        "sensitivity_requirements": [
            {
                "requirement_id": "sens_bootstrap_stability",
                "requirement_type": "BOOTSTRAP_SENSITIVITY",
                "applies_to_instrument_id": "DID_BOOTSTRAP",
                "applies_to_execution_role": "PRIMARY_EXECUTION_CANDIDATE",
                "required_for_production": True,
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        "diagnostic_results": [
            {
                "requirement_id": "diag_parallel_trend",
                "result_status": "DIAGNOSTIC_PASSED",
                "evidence_level": "provided_not_computed",
            }
        ],
        "sensitivity_results": [
            {
                "requirement_id": "sens_bootstrap_stability",
                "result_status": "SENSITIVITY_PASSED",
                "evidence_level": "provided_not_computed",
            }
        ],
        "claim_scope": {"claim_type": "CAUSAL"},
        "production_governance_config": {"blocked_roles": ["production"]},
    }
    req.update(extra)
    return req


def test_public_api_exists() -> None:
    report = evaluate_readout_diagnostics_sensitivity(_base_request())
    assert report.artifact_id == "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001"
    assert (
        evaluate_diagnostics_sensitivity_evidence(_base_request()).artifact_id == report.artifact_id
    )


def test_missing_execution_artifact_blocks_evidence_sufficiency() -> None:
    req = _base_request()
    req.pop("execution_artifacts")
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED


def test_execution_not_completed_blocks_by_default() -> None:
    req = _base_request(
        execution_status="INSTRUMENT_EXECUTION_NOT_RUN",
        execution_artifacts={"execution_id": "execution_001", "execution_completed": False},
        instrument_execution_results=[
            {
                "instrument_id": "DID_BOOTSTRAP",
                "instrument_execution_status": "INSTRUMENT_EXECUTION_NOT_RUN",
            }
        ],
    )
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED


def test_diagnostic_requirements_generate_plans() -> None:
    report = evaluate_readout_diagnostics_sensitivity(_base_request())
    assert len(report.diagnostic_plans) == 1
    assert report.diagnostic_plans[0]["planned_status"] == "DIAGNOSTIC_PLANNED_NOT_RUN"


def test_sensitivity_requirements_generate_plans() -> None:
    report = evaluate_readout_diagnostics_sensitivity(_base_request())
    assert len(report.sensitivity_plans) == 1
    assert report.sensitivity_plans[0]["planned_execution_mode"] == "not_run"


def test_missing_required_diagnostic_result_blocks() -> None:
    req = _base_request(diagnostic_results=[])
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS


def test_missing_required_sensitivity_result_blocks() -> None:
    req = _base_request(sensitivity_results=[])
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY


def test_passed_diagnostic_supports_sufficient_evidence() -> None:
    report = evaluate_readout_diagnostics_sensitivity(_base_request())
    assert report.evidence_sufficiency_status == EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW


def test_passed_sensitivity_supports_sufficient_evidence() -> None:
    report = evaluate_readout_diagnostics_sensitivity(_base_request())
    assert report.diagnostic_evidence_packets[0]["result_status"] == "DIAGNOSTIC_PASSED"
    assert report.sensitivity_evidence_packets[0]["result_status"] == "SENSITIVITY_PASSED"


def test_failed_blocking_diagnostic_blocks_claim_review() -> None:
    req = _base_request()
    req["diagnostic_results"] = [
        {"requirement_id": "diag_parallel_trend", "result_status": "DIAGNOSTIC_FAILED"}
    ]
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS


def test_failed_nonblocking_diagnostic_produces_provisional() -> None:
    req = _base_request()
    req["diagnostic_requirements"][0]["blocking_if_failed"] = False
    req["diagnostic_results"] = [
        {"requirement_id": "diag_parallel_trend", "result_status": "DIAGNOSTIC_FAILED"}
    ]
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_PROVISIONAL


def test_inconclusive_sensitivity_produces_provisional() -> None:
    req = _base_request()
    req["sensitivity_results"] = [
        {"requirement_id": "sens_bootstrap_stability", "result_status": "SENSITIVITY_INCONCLUSIVE"}
    ]
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.evidence_sufficiency_status == EVIDENCE_PROVISIONAL


def test_diagnostic_only_cannot_support_production_claim() -> None:
    req = _base_request(
        claim_scope={"claim_type": "PRODUCTION"},
        diagnostic_requirements=[
            {
                "requirement_id": "diag_placebo",
                "requirement_type": "PLACEBO_DIAGNOSTIC",
                "applies_to_instrument_id": "SCM_PLACEBO",
                "applies_to_execution_role": "DIAGNOSTIC_EXECUTION_CANDIDATE",
                "required_for_production": True,
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        sensitivity_requirements=[],
        diagnostic_results=[
            {"requirement_id": "diag_placebo", "result_status": "DIAGNOSTIC_PASSED"}
        ],
        sensitivity_results=[],
    )
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.diagnostic_evidence_packets[0]["evidence_status"] == "EVIDENCE_BLOCKED_BY_GOVERNANCE"


def test_failure_packets_include_retry_categories() -> None:
    req = _base_request(diagnostic_results=[], sensitivity_results=[])
    report = evaluate_readout_diagnostics_sensitivity(req)
    assert report.diagnostic_failure_packets
    assert any(
        "FIX_DIAGNOSTIC_INPUTS" in fp["suggested_retry_categories"]
        for fp in report.diagnostic_failure_packets
    )


def test_multiple_requests_return_multiple_reports_without_ranking() -> None:
    r1 = _base_request(design_id="d1")
    r2 = _base_request(design_id="d2")
    report = evaluate_readout_diagnostics_sensitivity([r1, r2])
    assert report.design_id is None
    assert len(report.design_reports) == 2
    assert report.aggregate_summary is not None


def test_claim_boundary_flags_remain_false_for_authorization() -> None:
    report = evaluate_readout_diagnostics_sensitivity(_base_request())
    cb = report.claim_boundary_report
    assert cb["diagnostics_sensitivity_runtime_implemented"] is True
    assert cb["diagnostic_check_executed"] is False
    assert cb["sensitivity_check_executed"] is False
    assert cb["causal_claim_authorized"] is False
    assert cb["production_authorization_granted"] is False


def test_missing_diagnostic_nonblocking_provisionalizes() -> None:
    cfg = ReadoutDiagnosticsSensitivityRuntimeConfig(
        block_on_missing_required_diagnostic_results=False
    )
    req = _base_request(diagnostic_results=[])
    report = evaluate_readout_diagnostics_sensitivity(req, config=cfg)
    assert report.evidence_sufficiency_status == EVIDENCE_PROVISIONAL


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["verdict"] == (
        "readout_diagnostics_sensitivity_runtime_implemented_evidence_planning_and_sufficiency_only_"
        "no_diagnostic_or_sensitivity_execution"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["diagnostics_sensitivity_runtime_implemented"] is True
    assert summary["diagnostic_check_executed"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
