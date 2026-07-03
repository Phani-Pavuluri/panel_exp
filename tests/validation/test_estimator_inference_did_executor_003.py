"""Tests for ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003 first governed DID executor."""

from __future__ import annotations

import json
from pathlib import Path

from panel_exp.validation.estimator_inference_did_executor_003 import (
    EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
    execute_did_point_estimate,
    execute_governed_did,
)
from panel_exp.validation.estimator_inference_execution_runtime_001 import (
    INSTRUMENT_EXECUTION_COMPLETED,
    INSTRUMENT_EXECUTION_NOT_RUN,
    EstimatorInferenceExecutionRuntimeConfig,
    execute_estimator_inference,
)
from panel_exp.validation.estimator_inference_executor_adapters_002 import (
    EXECUTOR_AVAILABLE_FOR_DRY_RUN,
    EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION,
    evaluate_governed_executor_availability,
    get_governed_executor_registry,
    lookup_governed_executor,
)

_REPO = Path(__file__).resolve().parents[2]
_SUMMARY = _REPO / "docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR_summary.json"
_REPORT = _REPO / "docs/track_d/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR_REPORT.md"


def _panel() -> list[dict]:
    return [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]


def _base_input(**extra: object) -> dict:
    payload = {
        "instrument_id": "DID_BOOTSTRAP",
        "estimator_family": "DID_FAMILY",
        "inference_family": "BOOTSTRAP_INFERENCE_FAMILY",
        "panel_data": _panel(),
        "unit_id_field": "geo_id",
        "time_field": "week",
        "outcome_field": "sales",
        "treatment_field": "treated",
        "pre_period": ["2025w01"],
        "test_period": ["2025w13"],
        "assignment_artifact_id": "assignment_001",
        "estimand": "STANDARD_INCREMENTALITY",
        "metric_name": "sales",
    }
    payload.update(extra)
    return payload


def _context() -> dict:
    return {
        "assignment_artifact_id": "assignment_001",
        "execution_data_contract": {
            "required_columns": ["geo_id", "week", "sales", "treated"],
            "available_columns": ["geo_id", "week", "sales", "treated"],
        },
        "estimand_scope": {"estimand_type": "STANDARD_INCREMENTALITY"},
        "uncertainty_scope": {"semantics": "bootstrap"},
    }


def _instrument() -> dict:
    return {
        "instrument_id": "DID_BOOTSTRAP",
        "execution_role": "PRIMARY_EXECUTION_CANDIDATE",
        "governance_status": "GOVERNED",
        "assignment_artifact_id": "assignment_001",
        "estimand_type": "STANDARD_INCREMENTALITY",
        "metric_name": "sales",
        "uncertainty_semantics": "bootstrap",
    }


def test_public_did_executor_api_exists() -> None:
    result = execute_did_point_estimate(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    alias = execute_governed_did(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    assert result.did_point_estimate_computed is True
    assert alias.did_point_estimate_computed is True


def test_valid_did_panel_computes_expected_absolute_point_estimate() -> None:
    result = execute_did_point_estimate(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    assert result.effect_estimate_report is not None
    assert result.effect_estimate_report["point_estimate"] == 9.0
    assert result.effect_estimate_report["estimation_status"] == EFFECT_ESTIMATE_COMPUTED_POINT_ONLY


def test_relative_lift_not_computed_by_default() -> None:
    result = execute_did_point_estimate(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    assert result.effect_estimate_report is not None
    assert result.effect_estimate_report["relative_lift"] is None


def test_relative_lift_computed_when_enabled_and_denominator_valid() -> None:
    result = execute_did_point_estimate(
        _base_input(),
        config={
            "allow_governed_did_point_estimate_execution": True,
            "compute_relative_lift": True,
            "relative_lift_baseline": "control_post_mean",
        },
    )
    assert result.effect_estimate_report is not None
    assert result.effect_estimate_report["relative_lift"] == 1.0


def test_missing_panel_data_emits_failure_packet() -> None:
    payload = _base_input()
    payload.pop("panel_data")
    result = execute_did_point_estimate(payload, config={"allow_governed_did_point_estimate_execution": True})
    assert result.failure_packet is not None
    assert "panel_data" in result.failure_packet["missing_inputs"]


def test_missing_required_columns_blocks() -> None:
    panel = [{"geo_id": "g1", "week": "2025w01", "sales": 1.0}]
    result = execute_did_point_estimate(
        _base_input(panel_data=panel),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False
    assert result.failure_packet is not None


def test_no_treated_units_blocks() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 0},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    result = execute_did_point_estimate(
        _base_input(panel_data=panel),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False


def test_no_control_units_blocks() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
    ]
    result = execute_did_point_estimate(
        _base_input(panel_data=panel),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False


def test_no_pre_period_blocks() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w13", "sales": 20.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w13", "sales": 9.0, "treated": 0},
    ]
    result = execute_did_point_estimate(
        _base_input(panel_data=panel, pre_period=[], test_period=["2025w13"]),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False


def test_no_post_period_blocks() -> None:
    panel = [
        {"geo_id": "g1", "week": "2025w01", "sales": 10.0, "treated": 1},
        {"geo_id": "g2", "week": "2025w01", "sales": 8.0, "treated": 0},
    ]
    result = execute_did_point_estimate(
        _base_input(panel_data=panel, pre_period=["2025w01"], test_period=[]),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False


def test_non_numeric_outcome_blocks() -> None:
    panel = _panel()
    panel[0]["sales"] = "not_a_number"
    result = execute_did_point_estimate(
        _base_input(panel_data=panel),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert result.did_point_estimate_computed is False


def test_missing_assignment_artifact_blocks() -> None:
    payload = _base_input()
    payload.pop("assignment_artifact_id")
    result = execute_did_point_estimate(payload, config={"allow_governed_did_point_estimate_execution": True})
    assert result.did_point_estimate_computed is False
    assert "assignment_artifact_id" in result.failure_packet["missing_inputs"]


def test_missing_estimand_blocks() -> None:
    payload = _base_input()
    payload.pop("estimand")
    result = execute_did_point_estimate(payload, config={"allow_governed_did_point_estimate_execution": True})
    assert result.did_point_estimate_computed is False


def test_bootstrap_inference_remains_not_implemented() -> None:
    result = execute_did_point_estimate(
        _base_input(),
        config={
            "allow_governed_did_point_estimate_execution": True,
            "allow_bootstrap_inference_execution": True,
        },
    )
    assert result.did_point_estimate_computed is False
    assert result.claim_boundary_report["bootstrap_inference_executed"] is False


def test_p_value_ci_uncertainty_remain_not_computed() -> None:
    result = execute_did_point_estimate(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    assert result.uncertainty_report["uncertainty_report_status"] == "NOT_COMPUTED"
    assert result.claim_boundary_report["p_value_computed"] is False
    assert result.claim_boundary_report["confidence_interval_computed"] is False
    assert result.claim_boundary_report["uncertainty_computed"] is False


def test_claim_authorization_remains_false() -> None:
    result = execute_did_point_estimate(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    assert result.claim_boundary_report["causal_claim_authorized"] is False
    assert result.claim_boundary_report["production_readout_authorized"] is False


def test_adapter_registry_exposes_did_point_estimate_under_config() -> None:
    enabled = lookup_governed_executor(
        "DID_BOOTSTRAP", config={"allow_governed_did_point_estimate_execution": True}
    )
    assert enabled.availability_status == EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
    assert enabled.supports_execution is True


def test_adapter_registry_dry_run_when_config_disabled() -> None:
    lookup = lookup_governed_executor("DID_BOOTSTRAP")
    assert lookup.availability_status == EXECUTOR_AVAILABLE_FOR_DRY_RUN
    assert lookup.supports_execution is False


def test_adapter_registry_does_not_expose_bootstrap_inference() -> None:
    spec = get_governed_executor_registry().specs["DID_BOOTSTRAP"]
    assert spec.supports_bootstrap_inference is False
    assert spec.supports_confidence_interval is False
    assert spec.supports_p_value is False


def test_execution_runtime_integrates_did_when_config_enabled() -> None:
    from tests.validation.test_estimator_inference_execution_runtime_001 import _base_request

    req = _base_request(panel_data=_panel())
    cfg = EstimatorInferenceExecutionRuntimeConfig(allow_governed_did_point_estimate_execution=True)
    report = execute_estimator_inference(req, config=cfg)
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_BOOTSTRAP")
    assert row.instrument_execution_status == INSTRUMENT_EXECUTION_COMPLETED
    assert row.effect_estimate_report is not None
    assert row.effect_estimate_report["point_estimate"] == 9.0


def test_execution_runtime_preserves_dry_run_when_config_disabled() -> None:
    from tests.validation.test_estimator_inference_execution_runtime_001 import _base_request

    req = _base_request(panel_data=_panel())
    report = execute_estimator_inference(req)
    row = next(r for r in report.instrument_execution_results if r.instrument_id == "DID_BOOTSTRAP")
    assert row.instrument_execution_status == INSTRUMENT_EXECUTION_NOT_RUN
    assert row.executor_lookup_status == EXECUTOR_AVAILABLE_FOR_DRY_RUN


def test_diagnostic_only_instrument_not_primary_executor() -> None:
    lookup = evaluate_governed_executor_availability(
        {
            "instrument_id": "SCM_PLACEBO",
            "execution_role": "PRIMARY_EXECUTION_CANDIDATE",
            "governance_status": "DIAGNOSTIC_ONLY",
            "assignment_artifact_id": "assignment_001",
            "uncertainty_semantics": "placebo",
        },
        _context(),
    )
    assert lookup.executor_available is False or lookup.supports_execution is False


def test_multiple_requests_unranked() -> None:
    first = execute_did_point_estimate(_base_input(), config={"allow_governed_did_point_estimate_execution": True})
    second = execute_did_point_estimate(
        _base_input(metric_name="revenue"),
        config={"allow_governed_did_point_estimate_execution": True},
    )
    assert first.effect_estimate_report is not None
    assert second.effect_estimate_report is not None
    assert first.effect_estimate_report["metric_name"] == "sales"
    assert second.effect_estimate_report["metric_name"] == "revenue"


def test_report_exists() -> None:
    assert _REPORT.is_file()


def test_summary_json_valid() -> None:
    payload = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert payload["artifact_id"] == "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR"
    assert payload["did_point_estimate_executor_implemented"] is True
    assert payload["bootstrap_inference_executed"] is False
