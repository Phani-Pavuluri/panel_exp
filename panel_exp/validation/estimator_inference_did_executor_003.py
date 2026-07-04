"""ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003 first governed DID point-estimate executor."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any

_ARTIFACT_ID = "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "first_governed_did_point_estimate_executor_implemented_no_inference_or_claim_authorization"

from panel_exp.validation.did_instrument_estimand_registry_001 import (
    DID_2X2_POINT_ESTIMATE,
    DID_GOVERNED_POINT_ESTIMATE,
    governed_point_estimate_instrument_ids,
    is_did_bootstrap_inference_instrument,
    is_governed_did_point_estimate_instrument,
    resolve_did_instrument_id,
    validate_did_instrument_for_execution,
)

GOVERNED_DID_INSTRUMENT_IDS = governed_point_estimate_instrument_ids()

EXECUTION_COMPLETED = "INSTRUMENT_EXECUTION_COMPLETED"
EXECUTION_FAILED = "INSTRUMENT_EXECUTION_FAILED"
EXECUTION_BLOCKED = "INSTRUMENT_EXECUTION_BLOCKED"
EXECUTION_NOT_RUN = "INSTRUMENT_EXECUTION_NOT_RUN"

EFFECT_ESTIMATE_COMPUTED_POINT_ONLY = "EFFECT_ESTIMATE_COMPUTED_POINT_ONLY"
NOT_COMPUTED = "NOT_COMPUTED"

RETRY_CATEGORIES = (
    "FIX_INPUT_DATA_CONTRACT",
    "FIX_ASSIGNMENT_ARTIFACT",
    "FIX_ESTIMAND_SPEC",
    "FIX_INSTRUMENT_SPEC",
    "DISABLE_UNGOVERNED_INFERENCE",
    "ADD_GOVERNED_BOOTSTRAP_ADAPTER",
    "CHANGE_READOUT_PLAN",
    "BLOCK_INSTRUMENT",
)

_AUTH_FALSE_FLAGS = {
    "bootstrap_inference_executed": False,
    "inference_execution_implemented": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "diagnostic_check_executed": False,
    "sensitivity_check_executed": False,
    "causal_claim_authorized": False,
    "incremental_lift_claim_authorized": False,
    "roi_claim_authorized": False,
    "production_readout_authorized": False,
    "production_authorization_granted": False,
    "mmm_runtime_calls_implemented": False,
    "mmm_calibration_authorized": False,
    "llm_decisioning_authorized": False,
}


@dataclass(frozen=True)
class DIDPointEstimateExecutorConfig:
    allow_governed_did_point_estimate_execution: bool = False
    allow_legacy_did_bootstrap_for_point_estimate: bool = False
    allow_bootstrap_inference_execution: bool = False
    allow_confidence_interval_computation: bool = False
    allow_p_value_computation: bool = False
    allow_claim_authorization: bool = False
    compute_relative_lift: bool = False
    relative_lift_baseline: str = "control_post_mean"


@dataclass(frozen=True)
class DIDPointEstimateExecutionResult:
    instrument_id: str
    estimator_family: str
    inference_family: str
    execution_status: str
    effect_estimate_report: dict[str, Any] | None
    uncertainty_report: dict[str, Any]
    inference_diagnostic_report: dict[str, Any]
    execution_trace: dict[str, Any]
    provenance_manifest: dict[str, Any]
    failure_packet: dict[str, Any] | None
    claim_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    did_point_estimate_computed: bool = False


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:  # NaN
        return None
    return result


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _resolve_config(config: DIDPointEstimateExecutorConfig | dict[str, Any] | None) -> DIDPointEstimateExecutorConfig:
    if config is None:
        return DIDPointEstimateExecutorConfig()
    if isinstance(config, DIDPointEstimateExecutorConfig):
        return config
    base = DIDPointEstimateExecutorConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return DIDPointEstimateExecutorConfig(**merged)


def _failure_packet(
    *,
    failure_id: str,
    instrument_id: str,
    failure_status: str,
    missing_inputs: list[str],
    blocked_requirements: list[str],
    governance_failures: list[str],
    suggested_retry_categories: list[str],
    claim_boundary_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "failure_id": failure_id,
        "requirement_id": instrument_id,
        "instrument_id": instrument_id,
        "failure_status": failure_status,
        "missing_inputs": sorted(set(missing_inputs)),
        "blocked_requirements": sorted(set(blocked_requirements)),
        "failed_requirements": [],
        "inconclusive_requirements": [],
        "governance_failures": sorted(set(governance_failures)),
        "suggested_retry_categories": sorted(set(suggested_retry_categories)),
        "claim_boundary_report": claim_boundary_report,
    }


def _claim_boundary(*, did_computed: bool) -> dict[str, Any]:
    return {
        "first_governed_executor_implemented": True,
        "did_point_estimate_executor_implemented": True,
        "did_point_estimate_computed": did_computed,
        "effect_estimate_computed": did_computed,
        **_AUTH_FALSE_FLAGS,
    }


def _resolve_post_indicator(row: dict[str, Any], post_field: str | None, pre_period: set[Any], post_values: set[Any], time_field: str) -> int | None:
    if post_field and post_field in row:
        val = row.get(post_field)
        if val in (0, 1, True, False):
            return int(bool(val))
        token = str(val).strip().lower()
        if token in ("0", "false", "pre", "pre_period"):
            return 0
        if token in ("1", "true", "post", "post_period"):
            return 1
        return None
    time_val = row.get(time_field)
    if time_val in post_values:
        return 1
    if time_val in pre_period:
        return 0
    return None


def _resolve_treatment(row: dict[str, Any], treatment_field: str) -> int | None:
    val = row.get(treatment_field)
    if val in (0, 1, True, False):
        return int(bool(val))
    token = str(val).strip().lower()
    if token in ("0", "false", "control"):
        return 0
    if token in ("1", "true", "treated", "treatment"):
        return 1
    return None


def execute_did_point_estimate(
    input_data: dict[str, Any] | Any,
    config: DIDPointEstimateExecutorConfig | dict[str, Any] | None = None,
) -> DIDPointEstimateExecutionResult:
    """Execute governed DID point-estimate only; no inference or claim authorization."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)
    warnings: list[str] = []
    blocking: list[str] = []
    missing_inputs: list[str] = []
    governance_failures: list[str] = []
    retry: list[str] = []

    instrument_id = str(data.get("instrument_id") or DID_2X2_POINT_ESTIMATE).strip()
    resolution = resolve_did_instrument_id(instrument_id)
    canonical_id = resolution.canonical_instrument_id
    estimator_family = str(data.get("estimator_family") or "DID_FAMILY")
    inference_family = str(data.get("inference_family") or "POINT_ESTIMATE_ONLY")
    assignment_artifact_id = str(data.get("assignment_artifact_id") or "").strip()
    estimand = data.get("estimand") or data.get("estimand_type")
    metric_name = data.get("metric_name")

    unit_id_field = str(data.get("unit_id_field") or "unit_id")
    time_field = str(data.get("time_field") or "time")
    outcome_field = str(data.get("outcome_field") or "outcome")
    treatment_field = str(data.get("treatment_field") or "treated")
    post_field = data.get("post_period_field") or data.get("post_field")
    if post_field is not None:
        post_field = str(post_field)

    pre_period = set(data.get("pre_period") or [])
    post_values = set(data.get("test_period") or data.get("post_period_values") or [])

    claim_boundary = _claim_boundary(did_computed=False)
    failure_id = _hash_payload({"instrument_id": instrument_id, "input": data})[:16]

    def _blocked(status: str, reason: str, *, retry_cats: list[str] | None = None) -> DIDPointEstimateExecutionResult:
        blocking.append(reason)
        fp = _failure_packet(
            failure_id=failure_id,
            instrument_id=instrument_id,
            failure_status=status,
            missing_inputs=missing_inputs,
            blocked_requirements=blocking,
            governance_failures=governance_failures,
            suggested_retry_categories=retry_cats or retry,
            claim_boundary_report=claim_boundary,
        )
        trace = {
            "artifact_id": _ARTIFACT_ID,
            "instrument_id": instrument_id,
            "execution_status": status,
            "algorithm_version": _ARTIFACT_VERSION,
            "input_hash": _hash_payload(data),
            "config_hash": _hash_payload(cfg.__dict__),
        }
        return DIDPointEstimateExecutionResult(
            instrument_id=instrument_id,
            estimator_family=estimator_family,
            inference_family=inference_family,
            execution_status=status,
            effect_estimate_report=None,
            uncertainty_report={"uncertainty_report_status": NOT_COMPUTED},
            inference_diagnostic_report={"inference_diagnostic_report_status": NOT_COMPUTED},
            execution_trace=trace,
            provenance_manifest={"input_hash": trace["input_hash"], "config_hash": trace["config_hash"]},
            failure_packet=fp,
            claim_boundary_report=claim_boundary,
            warnings=_safe_str_list(warnings),
            blocking_reasons=_safe_str_list(blocking),
            did_point_estimate_computed=False,
        )

    if not cfg.allow_governed_did_point_estimate_execution:
        governance_failures.append("governed DID point-estimate execution disabled by config")
        retry.append("BLOCK_INSTRUMENT")
        return _blocked(EXECUTION_NOT_RUN, "governed DID point-estimate execution disabled")

    if is_did_bootstrap_inference_instrument(instrument_id) and not cfg.allow_legacy_did_bootstrap_for_point_estimate:
        governance_failures.append("DID_BOOTSTRAP is bootstrap inference alias, not governed point estimate")
        blocking.append("MISLEADING_INSTRUMENT_ID")
        blocking.append("INFERENCE_NOT_IMPLEMENTED")
        blocking.append("USE_DID_2X2_POINT_ESTIMATE_FOR_POINT_ONLY_EXECUTION")
        retry.extend(["FIX_INSTRUMENT_SPEC", "ADD_GOVERNED_BOOTSTRAP_ADAPTER"])
        return _blocked(
            EXECUTION_BLOCKED,
            "DID_BOOTSTRAP refers to bootstrap inference; use DID_2X2_POINT_ESTIMATE for point-only execution",
            retry_cats=retry,
        )

    if not is_governed_did_point_estimate_instrument(instrument_id) and not (
        is_did_bootstrap_inference_instrument(instrument_id) and cfg.allow_legacy_did_bootstrap_for_point_estimate
    ):
        missing_inputs.append("instrument_id")
        retry.append("FIX_INSTRUMENT_SPEC")
        return _blocked(EXECUTION_BLOCKED, "unsupported instrument for governed DID point-estimate executor")

    effective_id = DID_2X2_POINT_ESTIMATE if (
        is_did_bootstrap_inference_instrument(instrument_id) and cfg.allow_legacy_did_bootstrap_for_point_estimate
    ) else canonical_id
    if effective_id not in GOVERNED_DID_INSTRUMENT_IDS:
        missing_inputs.append("instrument_id")
        retry.append("FIX_INSTRUMENT_SPEC")
        return _blocked(EXECUTION_BLOCKED, "unsupported instrument for governed DID executor")

    instrument_id = effective_id

    if cfg.allow_bootstrap_inference_execution:
        governance_failures.append("bootstrap inference execution not governed in runtime_003")
        retry.extend(["DISABLE_UNGOVERNED_INFERENCE", "ADD_GOVERNED_BOOTSTRAP_ADAPTER"])
        return _blocked(EXECUTION_BLOCKED, "bootstrap inference requested but not governed")

    if cfg.allow_confidence_interval_computation:
        governance_failures.append("confidence interval computation not governed in runtime_003")
        retry.append("DISABLE_UNGOVERNED_INFERENCE")
        return _blocked(EXECUTION_BLOCKED, "confidence interval requested but not governed")

    if cfg.allow_p_value_computation:
        governance_failures.append("p-value computation not governed in runtime_003")
        retry.append("DISABLE_UNGOVERNED_INFERENCE")
        return _blocked(EXECUTION_BLOCKED, "p-value requested but not governed")

    if not assignment_artifact_id:
        missing_inputs.append("assignment_artifact_id")
        retry.append("FIX_ASSIGNMENT_ARTIFACT")
        return _blocked(EXECUTION_BLOCKED, "assignment artifact id missing")

    if not estimand:
        missing_inputs.append("estimand")
        retry.append("FIX_ESTIMAND_SPEC")
        return _blocked(EXECUTION_BLOCKED, "estimand missing")

    if not metric_name:
        missing_inputs.append("metric_name")
        retry.append("FIX_INSTRUMENT_SPEC")
        return _blocked(EXECUTION_BLOCKED, "metric name missing")

    panel_data = data.get("panel_data")
    if not isinstance(panel_data, list) or not panel_data:
        missing_inputs.append("panel_data")
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(EXECUTION_BLOCKED, "panel data missing or empty")

    required_columns = {unit_id_field, time_field, outcome_field, treatment_field}
    if post_field:
        required_columns.add(post_field)

    for col in sorted(required_columns):
        if not any(isinstance(row, dict) and col in row for row in panel_data):
            missing_inputs.append(col)
    if missing_inputs:
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(EXECUTION_BLOCKED, "required panel columns missing")

    treated_pre: list[float] = []
    treated_post: list[float] = []
    control_pre: list[float] = []
    control_post: list[float] = []

    for row in panel_data:
        if not isinstance(row, dict):
            retry.append("FIX_INPUT_DATA_CONTRACT")
            return _blocked(EXECUTION_BLOCKED, "panel row is not a dict")

        outcome = _as_float(row.get(outcome_field))
        if outcome is None:
            retry.append("FIX_INPUT_DATA_CONTRACT")
            return _blocked(EXECUTION_BLOCKED, "non-numeric or missing outcome value")

        treatment = _resolve_treatment(row, treatment_field)
        if treatment is None:
            retry.append("FIX_INPUT_DATA_CONTRACT")
            return _blocked(EXECUTION_BLOCKED, "invalid treatment indicator")

        post = _resolve_post_indicator(row, post_field, pre_period, post_values, time_field)
        if post is None:
            retry.append("FIX_INPUT_DATA_CONTRACT")
            return _blocked(EXECUTION_BLOCKED, "cannot map row to pre/post period")

        if treatment == 1 and post == 0:
            treated_pre.append(outcome)
        elif treatment == 1 and post == 1:
            treated_post.append(outcome)
        elif treatment == 0 and post == 0:
            control_pre.append(outcome)
        elif treatment == 0 and post == 1:
            control_post.append(outcome)

    if not treated_pre:
        blocking.append("no treated pre-period observations")
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(EXECUTION_BLOCKED, "no treated pre-period observations")
    if not treated_post:
        blocking.append("no treated post-period observations")
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(EXECUTION_BLOCKED, "no treated post-period observations")
    if not control_pre:
        blocking.append("no control pre-period observations")
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(EXECUTION_BLOCKED, "no control pre-period observations")
    if not control_post:
        blocking.append("no control post-period observations")
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(EXECUTION_BLOCKED, "no control post-period observations")

    treated_pre_mean = _mean(treated_pre)
    treated_post_mean = _mean(treated_post)
    control_pre_mean = _mean(control_pre)
    control_post_mean = _mean(control_post)
    assert treated_pre_mean is not None
    assert treated_post_mean is not None
    assert control_pre_mean is not None
    assert control_post_mean is not None

    did_point = (treated_post_mean - treated_pre_mean) - (control_post_mean - control_pre_mean)
    absolute_lift = did_point
    relative_lift = None
    baseline_reference = None

    if cfg.compute_relative_lift:
        if cfg.relative_lift_baseline == "treated_pre_mean":
            baseline_reference = treated_pre_mean
        else:
            baseline_reference = control_post_mean
        if baseline_reference == 0:
            warnings.append("relative lift not computed: baseline denominator is zero")
        else:
            relative_lift = did_point / baseline_reference

    effect_estimate_id = _hash_payload(
        {
            "instrument_id": instrument_id,
            "assignment_artifact_id": assignment_artifact_id,
            "did_point": did_point,
        }
    )[:16]

    effect_report = {
        "effect_estimate_id": effect_estimate_id,
        "instrument_id": instrument_id,
        "estimand": estimand,
        "metric_name": metric_name,
        "effect_scale": "absolute",
        "point_estimate": did_point,
        "baseline_reference": baseline_reference,
        "relative_lift": relative_lift,
        "absolute_lift": absolute_lift,
        "unit_scope": data.get("unit_scope"),
        "population_scope": data.get("population_scope"),
        "time_window": data.get("time_window"),
        "cell_contrast": data.get("cell_contrast"),
        "sample_size_summary": {
            "treated_pre_n": len(treated_pre),
            "treated_post_n": len(treated_post),
            "control_pre_n": len(control_pre),
            "control_post_n": len(control_post),
        },
        "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "effect_estimate_report_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
        "warnings": list(warnings),
        "did_components": {
            "treated_pre_mean": treated_pre_mean,
            "treated_post_mean": treated_post_mean,
            "control_pre_mean": control_pre_mean,
            "control_post_mean": control_post_mean,
        },
    }

    claim_boundary = _claim_boundary(did_computed=True)
    input_hash = _hash_payload(data)
    config_hash = _hash_payload(cfg.__dict__)
    output_hash = _hash_payload(effect_report)
    trace = {
        "artifact_id": _ARTIFACT_ID,
        "instrument_id": instrument_id,
        "assignment_artifact_id": assignment_artifact_id,
        "execution_status": EXECUTION_COMPLETED,
        "algorithm_version": _ARTIFACT_VERSION,
        "code_version": _ARTIFACT_ID,
        "input_hash": input_hash,
        "config_hash": config_hash,
        "output_hash": output_hash,
        "runtime_environment": "deterministic_local_runtime",
        "execution_timestamp_policy": "deterministic_no_wall_clock_required",
        "did_formula": "(treated_post_mean - treated_pre_mean) - (control_post_mean - control_pre_mean)",
    }
    provenance = {
        "artifact_id": _ARTIFACT_ID,
        "instrument_id": instrument_id,
        "assignment_artifact_id": assignment_artifact_id,
        "input_hash": input_hash,
        "config_hash": config_hash,
        "output_hash": output_hash,
        "estimation_status": EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
    }

    return DIDPointEstimateExecutionResult(
        instrument_id=instrument_id,
        estimator_family=estimator_family,
        inference_family=inference_family,
        execution_status=EXECUTION_COMPLETED,
        effect_estimate_report=effect_report,
        uncertainty_report={"uncertainty_report_status": NOT_COMPUTED, "instrument_id": instrument_id},
        inference_diagnostic_report={
            "inference_diagnostic_report_status": NOT_COMPUTED,
            "instrument_id": instrument_id,
        },
        execution_trace=trace,
        provenance_manifest=provenance,
        failure_packet=None,
        claim_boundary_report=claim_boundary,
        warnings=_safe_str_list(warnings),
        blocking_reasons=(),
        did_point_estimate_computed=True,
    )


execute_governed_did = execute_did_point_estimate
