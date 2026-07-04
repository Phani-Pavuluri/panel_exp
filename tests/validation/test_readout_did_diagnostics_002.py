"""Tests for READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002 first governed DID diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.readout_did_diagnostics_002 import (
    DIAGNOSTIC_BLOCKED,
    DIAGNOSTIC_FAILED,
    DIAGNOSTIC_PASSED,
    DIAGNOSTIC_PASSED_WITH_WARNINGS,
    evaluate_did_coverage_diagnostic,
    evaluate_governed_did_diagnostic,
)
from panel_exp.validation.readout_diagnostics_sensitivity_runtime_001 import (
    EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS,
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
    ReadoutDiagnosticsSensitivityRuntimeConfig,
    evaluate_readout_diagnostics_sensitivity,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC_summary.json"
_REPORT = _REPO / "docs/track_d/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC_REPORT.md"


def _panel() -> list[dict]:
    return [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]


def _base_input(**extra: object) -> dict:
    payload = {
        "requirement_id": "diag_preperiod_fit",
        "requirement_type": "PRE_PERIOD_FIT_DIAGNOSTIC",
        "instrument_id": "DID_2X2_POINT_ESTIMATE",
        "execution_artifact_id": "execution_001",
        "panel_data": _panel(),
        "unit_id_field": "geo_id",
        "time_field": "week",
        "outcome_field": "sales",
        "treatment_field": "treated",
        "pre_period": ["2025w01"],
        "test_period": ["2025w13"],
    }
    payload.update(extra)
    return payload


def _enabled_config() -> dict:
    return {"enable_governed_did_coverage_diagnostic": True}


def test_public_did_diagnostic_api_exists() -> None:
    result = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    alias = evaluate_governed_did_diagnostic(_base_input(), config=_enabled_config())
    assert result.diagnostic_result_computed is True
    assert alias.diagnostic_status == DIAGNOSTIC_PASSED


def test_valid_did_panel_passes_coverage_diagnostic() -> None:
    result = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    assert result.diagnostic_status == DIAGNOSTIC_PASSED
    assert result.passed is True


def test_counts_are_correct() -> None:
    result = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    assert result.coverage_summary["treated_pre_count"] == 1
    assert result.coverage_summary["treated_post_count"] == 1
    assert result.coverage_summary["control_pre_count"] == 1
    assert result.coverage_summary["control_post_count"] == 1


def test_pre_period_means_and_difference_are_correct() -> None:
    result = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    assert result.pre_period_summary["treated_pre_mean"] == 10.0
    assert result.pre_period_summary["control_pre_mean"] == 8.0
    assert result.pre_period_summary["pre_period_baseline_difference"] == 2.0


def test_normalized_gap_not_computed_by_default() -> None:
    result = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    assert result.pre_period_summary["normalized_pre_period_gap"] is None


def test_normalized_gap_optional_when_enabled() -> None:
    result = evaluate_did_coverage_diagnostic(
        _base_input(),
        config={**_enabled_config(), "compute_normalized_pre_period_gap": True},
    )
    assert result.pre_period_summary["normalized_pre_period_gap"] == 0.25


def test_normalized_gap_not_computed_when_denominator_invalid() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel, pre_period=["2025w01"], test_period=["2025w13"]),
        config={**_enabled_config(), "compute_normalized_pre_period_gap": True},
    )
    assert result.diagnostic_status == DIAGNOSTIC_FAILED


def test_missing_panel_data_blocks_diagnostic() -> None:
    payload = _base_input()
    payload.pop("panel_data")
    result = evaluate_did_coverage_diagnostic(payload, config=_enabled_config())
    assert result.diagnostic_status == DIAGNOSTIC_BLOCKED
    assert result.diagnostic_result_computed is False


def test_missing_required_columns_blocks_diagnostic() -> None:
    panel = [{"geo_id": "g1", "week": "2025w01", "sales": 1.0}]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_BLOCKED


def test_no_treated_pre_observations_fails_diagnostic() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_FAILED


def test_no_treated_post_observations_fails_diagnostic() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_FAILED


def test_no_control_pre_observations_fails_diagnostic() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_FAILED


def test_no_control_post_observations_fails_diagnostic() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
    ]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_FAILED


def test_non_numeric_outcome_blocks_diagnostic() -> None:
    panel = _panel()
    panel[0]["sales"] = "bad"
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_BLOCKED


def test_missing_execution_artifact_id_blocks_when_required() -> None:
    payload = _base_input()
    payload.pop("execution_artifact_id")
    result = evaluate_did_coverage_diagnostic(payload, config=_enabled_config())
    assert result.diagnostic_status == DIAGNOSTIC_BLOCKED


def test_unsupported_instrument_blocks_diagnostic() -> None:
    result = evaluate_did_coverage_diagnostic(
        _base_input(instrument_id="SCM_PLACEBO"),
        config=_enabled_config(),
    )
    assert result.diagnostic_status == DIAGNOSTIC_BLOCKED


def test_no_p_value_ci_uncertainty_or_claim_authorization() -> None:
    result = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    cb = result.claim_boundary_report
    assert cb["p_value_computed"] is False
    assert cb["confidence_interval_computed"] is False
    assert cb["uncertainty_computed"] is False
    assert cb["causal_claim_authorized"] is False
    assert cb["effect_estimate_computed"] is False


def test_runtime_integration_only_when_config_enabled() -> None:
    req = {
        "design_id": "design_diag_runtime",
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
        "execution_artifacts": {"execution_id": "execution_001", "execution_completed": True},
        "instrument_execution_results": [
            {"instrument_id": "DID_2X2_POINT_ESTIMATE", "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED"}
        ],
        "panel_data": _panel(),
        "unit_id_field": "geo_id",
        "time_field": "week",
        "outcome_field": "sales",
        "treatment_field": "treated",
        "pre_period": ["2025w01"],
        "test_period": ["2025w13"],
        "diagnostic_requirements": [
            {
                "requirement_id": "diag_preperiod_fit",
                "requirement_type": "PRE_PERIOD_FIT_DIAGNOSTIC",
                "applies_to_instrument_id": "DID_2X2_POINT_ESTIMATE",
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        "sensitivity_requirements": [],
        "diagnostic_results": [],
        "sensitivity_results": [],
        "claim_scope": {"claim_type": "CAUSAL"},
        "production_governance_config": {"blocked_roles": ["production"]},
    }
    cfg = ReadoutDiagnosticsSensitivityRuntimeConfig(
        block_on_missing_sensitivity_requirements=False,
        enable_governed_did_coverage_diagnostic=True,
    )
    report = evaluate_readout_diagnostics_sensitivity(req, config=cfg)
    packet = report.diagnostic_evidence_packets[0]
    assert packet["result_status"] == DIAGNOSTIC_PASSED
    assert report.claim_boundary_report["diagnostic_result_computed"] is True
    assert report.evidence_sufficiency_status == EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW


def test_runtime_preserves_planned_not_run_when_config_disabled() -> None:
    req = {
        "design_id": "design_diag_runtime",
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
        "execution_artifacts": {"execution_id": "execution_001", "execution_completed": True},
        "instrument_execution_results": [
            {"instrument_id": "DID_2X2_POINT_ESTIMATE", "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED"}
        ],
        "panel_data": _panel(),
        "pre_period": ["2025w01"],
        "test_period": ["2025w13"],
        "diagnostic_requirements": [
            {
                "requirement_id": "diag_preperiod_fit",
                "requirement_type": "PRE_PERIOD_FIT_DIAGNOSTIC",
                "applies_to_instrument_id": "DID_2X2_POINT_ESTIMATE",
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        "sensitivity_requirements": [],
        "diagnostic_results": [],
        "sensitivity_results": [],
        "claim_scope": {"claim_type": "CAUSAL"},
        "production_governance_config": {"blocked_roles": ["production"]},
    }
    cfg = ReadoutDiagnosticsSensitivityRuntimeConfig(block_on_missing_sensitivity_requirements=False)
    report = evaluate_readout_diagnostics_sensitivity(req, config=cfg)
    assert report.diagnostic_plans[0]["planned_status"] == "DIAGNOSTIC_PLANNED_NOT_RUN"


def test_failed_blocking_diagnostic_updates_evidence_insufficiency() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    req = {
        "design_id": "design_diag_failed",
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
        "execution_artifacts": {"execution_id": "execution_001", "execution_completed": True},
        "instrument_execution_results": [
            {"instrument_id": "DID_2X2_POINT_ESTIMATE", "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED"}
        ],
        "panel_data": panel,
        "pre_period": ["2025w01"],
        "test_period": ["2025w13"],
        "diagnostic_requirements": [
            {
                "requirement_id": "diag_preperiod_fit",
                "requirement_type": "PRE_PERIOD_FIT_DIAGNOSTIC",
                "applies_to_instrument_id": "DID_2X2_POINT_ESTIMATE",
                "blocking_if_missing": True,
                "blocking_if_failed": True,
            }
        ],
        "sensitivity_requirements": [],
        "diagnostic_results": [],
        "sensitivity_results": [],
        "claim_scope": {"claim_type": "CAUSAL"},
        "production_governance_config": {"blocked_roles": ["production"]},
    }
    cfg = ReadoutDiagnosticsSensitivityRuntimeConfig(
        block_on_missing_sensitivity_requirements=False,
        enable_governed_did_coverage_diagnostic=True,
    )
    report = evaluate_readout_diagnostics_sensitivity(req, config=cfg)
    assert report.evidence_sufficiency_status == EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS


def test_multiple_requests_unranked() -> None:
    first = evaluate_did_coverage_diagnostic(_base_input(), config=_enabled_config())
    second = evaluate_did_coverage_diagnostic(
        _base_input(requirement_id="diag_other"),
        config=_enabled_config(),
    )
    assert first.requirement_id == "diag_preperiod_fit"
    assert second.requirement_id == "diag_other"


def test_large_pre_period_gap_warning() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 20.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 22.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 1.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 2.0, "treated": 0},
    ]
    result = evaluate_did_coverage_diagnostic(
        _base_input(panel_data=panel),
        config={
            **_enabled_config(),
            "compute_normalized_pre_period_gap": True,
            "max_abs_normalized_pre_period_gap": 1.0,
            "warn_on_large_pre_period_gap": True,
        },
    )
    assert result.diagnostic_status == DIAGNOSTIC_PASSED_WITH_WARNINGS


def test_report_exists() -> None:
    assert _REPORT.is_file()


def test_summary_json_valid() -> None:
    payload = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert payload["artifact_id"] == "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC"
    assert payload["first_governed_diagnostic_implemented"] is True
    assert payload["statistical_parallel_trends_computed"] is False
