"""Tests for SRM_BALANCE_READOUT_DIAGNOSTIC_001."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from panel_exp.validation.assignment_panel_integrity_runtime_001 import (
    ASSIGNMENT_PANEL_INTEGRITY_FAILED,
    ASSIGNMENT_PANEL_INTEGRITY_PASSED,
)
from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    ReadoutDiagnosticsSensitivityRuntimeConfig,
    evaluate_readout_diagnostics_sensitivity,
)
from panel_exp.validation.readout_plan_runtime_001 import (
    ReadoutPlanRuntimeConfig,
    build_readout_plan,
)
from panel_exp.validation.srm_balance_readout_diagnostic_001 import (
    ISSUE_COVARIATE_NON_NUMERIC,
    SRM_BALANCE_DIAGNOSTIC_BLOCKED,
    SRM_BALANCE_DIAGNOSTIC_FAILED,
    SRM_BALANCE_DIAGNOSTIC_PASSED,
    SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS,
    SRMBalanceReadoutDiagnosticReport,
    check_srm_balance_readiness,
    evaluate_srm_balance_diagnostic,
    evaluate_srm_balance_readout_diagnostic,
    run_validation,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/SRM_BALANCE_READOUT_DIAGNOSTIC_001_summary.json"
_REPORT = _REPO / "docs/track_d/SRM_BALANCE_READOUT_DIAGNOSTIC_001_REPORT.md"


def _allocations() -> list[dict]:
    return [
        {"unit_id": "u1", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL", "treated": 0},
        {"unit_id": "u2", "assigned_cell_id": "C0", "assigned_cell_role": "CONTROL", "treated": 0},
        {"unit_id": "u3", "assigned_cell_id": "T1", "assigned_cell_role": "TREATMENT", "treated": 1},
        {"unit_id": "u4", "assigned_cell_id": "T1", "assigned_cell_role": "TREATMENT", "treated": 1},
    ]


def _panel(**overrides: object) -> list[dict]:
    rows = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 10.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 10.1},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 10.05},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 10.15},
    ]
    if overrides:
        rows = [dict(rows[0], **overrides)] + rows[1:]
    return rows


def _base_request(**extra: object) -> dict:
    payload = {
        "request_id": "srm_test_001",
        "assignment_artifact": {"artifact_id": "assign_001", "assignment_hash": "hash_001"},
        "assignment_artifact_id": "assign_001",
        "unit_allocations": _allocations(),
        "panel_records": _panel(),
        "assignment_panel_integrity_report": {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
    }
    payload.update(extra)
    return payload


def test_public_api_exists() -> None:
    report = evaluate_srm_balance_readout_diagnostic(_base_request())
    assert isinstance(report, SRMBalanceReadoutDiagnosticReport)
    alias = evaluate_srm_balance_diagnostic(_base_request())
    assert alias.status == SRM_BALANCE_DIAGNOSTIC_PASSED
    assert check_srm_balance_readiness(_base_request()).can_support_claim_review is True


def test_passes_when_expected_and_realized_cell_counts_match() -> None:
    report = evaluate_srm_balance_readout_diagnostic(_base_request())
    assert report.status == SRM_BALANCE_DIAGNOSTIC_PASSED
    assert report.expected_cell_counts == {"C0": 2, "T1": 2}
    assert report.realized_cell_counts == {"C0": 2, "T1": 2}
    assert report.max_sample_ratio_deviation == 0.0


def test_fails_when_sample_ratio_deviation_exceeds_threshold() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0},
        {"unit_id": "u3", "cell_id": "C0", "treated": 0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1},
    ]
    report = evaluate_srm_balance_readout_diagnostic(_base_request(panel_records=panel))
    assert report.status == SRM_BALANCE_DIAGNOSTIC_FAILED
    assert report.max_sample_ratio_deviation is not None
    assert report.max_sample_ratio_deviation > 0.05


def test_fails_when_assigned_units_missing_from_panel() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, production_context="PRODUCTION")
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_FAILED
    assert "u2" in report.missing_assigned_units


def test_fails_when_extra_panel_units_exceed_threshold() -> None:
    panel = _panel() + [{"unit_id": "u9", "cell_id": "T1", "treated": 1}]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, production_context="PRODUCTION")
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_FAILED
    assert "u9" in report.extra_panel_units


def test_fails_when_treated_or_control_realized_missing() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1},
    ]
    for row in panel:
        row["treated"] = 1
    report = evaluate_srm_balance_readout_diagnostic(_base_request(panel_records=panel))
    assert report.status == SRM_BALANCE_DIAGNOSTIC_FAILED


def test_blocks_when_assignment_panel_integrity_failed() -> None:
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(
            assignment_panel_integrity_report={"status": ASSIGNMENT_PANEL_INTEGRITY_FAILED},
        )
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_BLOCKED
    assert report.is_blocking is True


def test_passes_covariate_balance_when_smd_under_threshold() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 10.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 10.0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 10.0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 10.0},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, covariate_fields=["baseline_spend"])
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_PASSED
    assert report.covariate_balance_results[0].standardized_mean_difference == 0.0


def test_fails_covariate_balance_when_smd_exceeds_threshold() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 1.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 1.0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 100.0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 100.0},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, covariate_fields=["baseline_spend"], production_context="PRODUCTION")
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_FAILED


def test_handles_zero_pooled_standard_deviation() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 5.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 5.0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 5.0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 5.0},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, covariate_fields=["baseline_spend"])
    )
    assert report.covariate_balance_results[0].standardized_mean_difference == 0.0


def test_reports_nonnumeric_covariate_field() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "region": "west"},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "region": "east"},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "region": "west"},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "region": "east"},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, covariate_fields=["region"])
    )
    assert ISSUE_COVARIATE_NON_NUMERIC in report.issues


def test_computes_baseline_pre_period_outcome_balance() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "sales": 10.0, "week": "2025w01"},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "sales": 11.0, "week": "2025w01"},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "sales": 10.5, "week": "2025w01"},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "sales": 10.2, "week": "2025w01"},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(
            panel_records=panel,
            panel_outcome_field="sales",
            panel_time_field="week",
            pre_period_values=["2025w01"],
        )
    )
    assert report.baseline_outcome_balance_result is not None
    assert report.claim_boundary_report["baseline_outcome_balance_evaluated"] is True


def test_production_context_makes_failed_srm_blocking() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0},
        {"unit_id": "u3", "cell_id": "C0", "treated": 0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, production_context="PRODUCTION")
    )
    assert report.is_blocking is True


def test_research_context_downgrades_balance_failure_to_warning() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 1.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 1.0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 100.0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 100.0},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(
            panel_records=panel,
            covariate_fields=["baseline_spend"],
            production_context="RESEARCH",
        ),
        config={"block_on_failed_balance_research": False},
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_PASSED_WITH_WARNINGS
    assert report.is_blocking is False


def test_diagnostics_runtime_integrates_srm_requirement_when_enabled() -> None:
    req = {
        "design_id": "design_srm_integration",
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
        "execution_artifacts": {
            "execution_id": "execution_001",
            "artifact_id": "execution_001",
            "execution_completed": True,
            "unit_allocations": _allocations(),
            "assignment_artifact": {"artifact_id": "assign_001"},
        },
        "panel_data": _panel(),
        "instrument_execution_results": [
            {
                "instrument_id": "DID_2X2_POINT_ESTIMATE",
                "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
            }
        ],
        "diagnostic_requirements": [
            {
                "requirement_id": "diag_srm",
                "requirement_type": "SRM_DIAGNOSTIC",
                "applies_to_instrument_id": "DID_2X2_POINT_ESTIMATE",
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        "sensitivity_requirements": [],
        "diagnostic_results": [],
        "sensitivity_results": [],
        "assignment_panel_integrity_report": {"status": ASSIGNMENT_PANEL_INTEGRITY_PASSED},
    }
    cfg = ReadoutDiagnosticsSensitivityRuntimeConfig(
        block_on_missing_sensitivity_requirements=False,
        enable_srm_balance_readout_diagnostic=True,
    )
    report = evaluate_readout_diagnostics_sensitivity(req, config=cfg)
    assert report.diagnostic_evidence_packets[0]["result_status"] == "DIAGNOSTIC_PASSED"
    assert report.claim_boundary_report["diagnostic_result_computed"] is True


def test_readout_plan_includes_srm_balance_prerequisite_for_randomized_assignment() -> None:
    req = {
        "design_id": "design_randomized",
        "readout_method_governance_status": "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING",
        "assignment_artifact_status": "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE",
        "assignment_plan": {
            "artifact_id": "assignment_plan_001",
            "assignment_algorithm_category": "RANDOMIZED_ASSIGNMENT",
        },
        "assignment_candidate": {"candidate_id": "assignment_candidate_001"},
        "reproducibility_manifest": {"seed_policy": "GOVERNED_RANDOMIZATION"},
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
        "uncertainty_scope": {"semantics": "causal_interval_candidate_requires_validation"},
        "required_diagnostics": ["placebo_check"],
        "required_sensitivity_checks": ["donor_pool_sensitivity"],
        "claim_scope": {"estimand": "STANDARD_INCREMENTALITY"},
    }
    report = build_readout_plan(req, config=ReadoutPlanRuntimeConfig())
    assert "srm_balance_readout_diagnostic" in report.required_diagnostics
    assert "srm_balance_readout_diagnostic_required" in report.execution_prerequisites


def test_list_input_returns_multiple_reports_without_ranking() -> None:
    reports = evaluate_srm_balance_readout_diagnostic(
        [_base_request(request_id="a"), _base_request(request_id="b")]
    )
    assert len(reports) == 2
    assert {r.request_id for r in reports} == {"a", "b"}


@dataclass
class _SRMInput:
    request_id: str
    assignment_artifact_id: str
    unit_allocations: list[dict]
    panel_records: list[dict]


def test_dataclass_like_input_supported() -> None:
    report = evaluate_srm_balance_readout_diagnostic(
        _SRMInput(
            request_id="dc_001",
            assignment_artifact_id="assign_dc",
            unit_allocations=_allocations(),
            panel_records=_panel(),
        ),
        config={"require_assignment_panel_integrity_pass": False},
    )
    assert report.status == SRM_BALANCE_DIAGNOSTIC_PASSED


def test_deterministic_trace_provenance_hash() -> None:
    first = evaluate_srm_balance_readout_diagnostic(_base_request())
    second = evaluate_srm_balance_readout_diagnostic(_base_request())
    assert first.diagnostic_trace["integrity_hash"] == second.diagnostic_trace["integrity_hash"]
    assert first.provenance["integrity_hash"] == second.provenance["integrity_hash"]


def test_all_claim_production_authorization_flags_false() -> None:
    report = evaluate_srm_balance_readout_diagnostic(_base_request())
    cb = report.claim_boundary_report
    assert cb["srm_balance_diagnostic_runtime_implemented"] is True
    assert cb["effect_estimate_computed"] is False
    assert cb["lift_computed"] is False
    assert cb["claim_authorized"] is False
    assert cb["production_readout_authorized"] is False
    assert cb["causal_claim_authorized"] is False
    assert report.can_support_production_readout is False


def test_zero_pooled_sd_with_different_means_marks_nonfinite() -> None:
    panel = [
        {"unit_id": "u1", "cell_id": "C0", "treated": 0, "baseline_spend": 1.0},
        {"unit_id": "u2", "cell_id": "C0", "treated": 0, "baseline_spend": 1.0},
        {"unit_id": "u3", "cell_id": "T1", "treated": 1, "baseline_spend": 2.0},
        {"unit_id": "u4", "cell_id": "T1", "treated": 1, "baseline_spend": 2.0},
    ]
    report = evaluate_srm_balance_readout_diagnostic(
        _base_request(panel_records=panel, covariate_fields=["baseline_spend"])
    )
    smd = report.covariate_balance_results[0].standardized_mean_difference
    assert smd is not None and math.isnan(smd)


def test_run_validation_and_summary() -> None:
    result = run_validation(write_summary=True)
    assert result["final_verdict"] == (
        "srm_balance_readout_diagnostic_implemented_no_inference_or_claim_authorization"
    )
    assert result["failed_scenarios"] == []
    assert _SUMMARY.exists()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["srm_balance_diagnostic_runtime_implemented"] is True
    assert summary["effect_estimate_computed"] is False


def test_report_exists() -> None:
    assert _REPORT.exists()
