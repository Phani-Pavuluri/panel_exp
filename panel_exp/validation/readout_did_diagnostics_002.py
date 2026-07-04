"""READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002 first governed DID coverage diagnostic."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from panel_exp.validation.did_instrument_estimand_registry_001 import (
    DID_2X2_POINT_ESTIMATE,
    is_did_bootstrap_inference_instrument,
    is_governed_did_point_estimate_instrument,
)

_ARTIFACT_ID = "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_002_FIRST_GOVERNED_DIAGNOSTIC"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "first_governed_did_coverage_diagnostic_implemented_no_inference_or_claim_authorization"

DIAGNOSTIC_BLOCKED = "DIAGNOSTIC_BLOCKED"
DIAGNOSTIC_FAILED = "DIAGNOSTIC_FAILED"
DIAGNOSTIC_PASSED = "DIAGNOSTIC_PASSED"
DIAGNOSTIC_PASSED_WITH_WARNINGS = "DIAGNOSTIC_PASSED_WITH_WARNINGS"
DIAGNOSTIC_INCONCLUSIVE = "DIAGNOSTIC_INCONCLUSIVE"
DIAGNOSTIC_NOT_EVALUATED = "DIAGNOSTIC_NOT_EVALUATED"

DID_COVERAGE_DIAGNOSTIC = "DID_COVERAGE_DIAGNOSTIC"
PRE_PERIOD_FIT_DIAGNOSTIC = "PRE_PERIOD_FIT_DIAGNOSTIC"

GOVERNED_DID_DIAGNOSTIC_TYPES = frozenset(
    {
        DID_COVERAGE_DIAGNOSTIC,
        PRE_PERIOD_FIT_DIAGNOSTIC,
        "COVARIATE_BALANCE_DIAGNOSTIC",
        "DID_PREPOST_COVERAGE_DIAGNOSTIC",
    }
)

RETRY_CATEGORIES = (
    "FIX_DIAGNOSTIC_INPUTS",
    "FIX_INPUT_DATA_CONTRACT",
    "RERUN_EXECUTION_WITH_REQUIRED_TRACE",
    "CHANGE_READOUT_PLAN",
    "ADD_REQUIRED_DIAGNOSTIC_PLAN",
    "BLOCK_CLAIM",
    "BLOCK_INSTRUMENT",
)

_AUTH_FALSE_FLAGS = {
    "statistical_parallel_trends_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
    "sensitivity_check_executed": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "lift_computed": False,
    "roi_computed": False,
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
class DIDCoverageDiagnosticConfig:
    enable_governed_did_coverage_diagnostic: bool = False
    enable_statistical_parallel_trends: bool = False
    enable_p_value_computation: bool = False
    enable_confidence_interval_computation: bool = False
    allow_claim_authorization: bool = False
    minimum_cell_count: int = 1
    max_abs_normalized_pre_period_gap: float | None = None
    fail_on_pre_period_gap_threshold: bool = False
    warn_on_large_pre_period_gap: bool = True
    inconclusive_on_zero_control_pre_mean: bool = False
    require_execution_artifact_id: bool = True
    compute_normalized_pre_period_gap: bool = False


@dataclass(frozen=True)
class DIDCoverageDiagnosticResult:
    diagnostic_id: str
    requirement_id: str
    instrument_id: str
    execution_artifact_id: str
    diagnostic_type: str
    diagnostic_status: str
    result_value: dict[str, Any]
    threshold: dict[str, Any] | None
    threshold_direction: str | None
    passed: bool
    blocking_result: bool
    interpretation: str
    evidence_level: str
    sample_size_summary: dict[str, Any]
    pre_period_summary: dict[str, Any]
    coverage_summary: dict[str, Any]
    artifact_references: tuple[str, ...]
    diagnostic_trace: dict[str, Any]
    failure_packet: dict[str, Any] | None
    claim_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    diagnostic_result_computed: bool = False
    diagnostic_pass_fail_computed: bool = False


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
    if result != result:
        return None
    return result


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _resolve_config(config: DIDCoverageDiagnosticConfig | dict[str, Any] | None) -> DIDCoverageDiagnosticConfig:
    if config is None:
        return DIDCoverageDiagnosticConfig()
    if isinstance(config, DIDCoverageDiagnosticConfig):
        return config
    base = DIDCoverageDiagnosticConfig()
    merged = {**base.__dict__, **{k: v for k, v in config.items() if k in base.__dict__}}
    return DIDCoverageDiagnosticConfig(**merged)


def _claim_boundary(*, computed: bool, passed: bool) -> dict[str, Any]:
    return {
        "first_governed_diagnostic_implemented": True,
        "did_coverage_diagnostic_implemented": True,
        "did_preperiod_baseline_diagnostic_implemented": True,
        "did_coverage_diagnostic_runtime_integrated": True,
        "diagnostic_result_computed": computed,
        "diagnostic_pass_fail_computed": computed,
        "assignment_panel_integrity_status_propagated_to_diagnostics": True,
        **_AUTH_FALSE_FLAGS,
    }


def _resolve_post_indicator(
    row: dict[str, Any],
    post_field: str | None,
    pre_period: set[Any],
    post_values: set[Any],
    time_field: str,
) -> int | None:
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


def _failure_packet(
    *,
    failure_id: str,
    requirement_id: str,
    instrument_id: str,
    execution_artifact_id: str,
    failure_status: str,
    missing_inputs: list[str],
    blocked_requirements: list[str],
    suggested_retry_categories: list[str],
    claim_boundary_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "failure_id": failure_id,
        "requirement_id": requirement_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "failure_status": failure_status,
        "missing_inputs": sorted(set(missing_inputs)),
        "blocked_requirements": sorted(set(blocked_requirements)),
        "failed_requirements": [],
        "inconclusive_requirements": [],
        "governance_failures": [],
        "suggested_retry_categories": sorted(set(suggested_retry_categories)),
        "claim_boundary_report": claim_boundary_report,
    }


def is_governed_did_diagnostic_type(requirement_type: str | None) -> bool:
    return str(requirement_type or "").strip().upper() in GOVERNED_DID_DIAGNOSTIC_TYPES


def to_provided_diagnostic_result(result: DIDCoverageDiagnosticResult) -> dict[str, Any]:
    return {
        "requirement_id": result.requirement_id,
        "result_id": result.diagnostic_id,
        "result_status": result.diagnostic_status,
        "result_value": result.result_value,
        "threshold": result.threshold,
        "threshold_direction": result.threshold_direction,
        "passed": result.passed,
        "blocking_result": result.blocking_result,
        "interpretation": result.interpretation,
        "evidence_level": result.evidence_level,
        "artifact_references": list(result.artifact_references),
        "warnings": list(result.warnings),
    }


def evaluate_did_coverage_diagnostic(
    input_data: dict[str, Any] | Any,
    config: DIDCoverageDiagnosticConfig | dict[str, Any] | None = None,
) -> DIDCoverageDiagnosticResult:
    """Evaluate governed DID coverage and pre-period baseline diagnostic only."""
    cfg = _resolve_config(config)
    data = _to_dict(input_data)
    warnings: list[str] = []
    blocking: list[str] = []
    missing_inputs: list[str] = []
    retry: list[str] = []

    requirement_id = str(data.get("requirement_id") or "diagnostic_requirement_unspecified")
    instrument_id = str(data.get("instrument_id") or data.get("applies_to_instrument_id") or DID_2X2_POINT_ESTIMATE)
    execution_artifact_id = str(data.get("execution_artifact_id") or "")
    requirement_type = str(data.get("requirement_type") or PRE_PERIOD_FIT_DIAGNOSTIC).upper()
    diagnostic_type = (
        DID_COVERAGE_DIAGNOSTIC
        if requirement_type == DID_COVERAGE_DIAGNOSTIC
        else PRE_PERIOD_FIT_DIAGNOSTIC
    )

    unit_id_field = str(data.get("unit_id_field") or "unit_id")
    time_field = str(data.get("time_field") or "time")
    outcome_field = str(data.get("outcome_field") or "outcome")
    treatment_field = str(data.get("treatment_field") or "treated")
    post_field = data.get("post_period_field") or data.get("post_field")
    if post_field is not None:
        post_field = str(post_field)

    pre_period = set(data.get("pre_period") or [])
    post_values = set(data.get("test_period") or data.get("post_period_values") or [])

    diagnostic_id = _hash_payload({"requirement_id": requirement_id, "input": data})[:16]
    claim_boundary = _claim_boundary(computed=False, passed=False)

    def _blocked(status: str, reason: str, *, retry_cats: list[str] | None = None) -> DIDCoverageDiagnosticResult:
        blocking.append(reason)
        fp = _failure_packet(
            failure_id=diagnostic_id,
            requirement_id=requirement_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            failure_status=status,
            missing_inputs=missing_inputs,
            blocked_requirements=blocking,
            suggested_retry_categories=retry_cats or retry,
            claim_boundary_report=claim_boundary,
        )
        trace = {
            "artifact_id": _ARTIFACT_ID,
            "diagnostic_id": diagnostic_id,
            "requirement_id": requirement_id,
            "diagnostic_status": status,
            "input_hash": _hash_payload(data),
            "config_hash": _hash_payload(cfg.__dict__),
        }
        return DIDCoverageDiagnosticResult(
            diagnostic_id=diagnostic_id,
            requirement_id=requirement_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            diagnostic_type=diagnostic_type,
            diagnostic_status=status,
            result_value={},
            threshold=None,
            threshold_direction=None,
            passed=False,
            blocking_result=True,
            interpretation=reason,
            evidence_level="not_computed",
            sample_size_summary={},
            pre_period_summary={},
            coverage_summary={},
            artifact_references=(),
            diagnostic_trace=trace,
            failure_packet=fp,
            claim_boundary_report=claim_boundary,
            warnings=_safe_str_list(warnings),
            blocking_reasons=_safe_str_list(blocking),
            diagnostic_result_computed=False,
            diagnostic_pass_fail_computed=False,
        )

    if not cfg.enable_governed_did_coverage_diagnostic:
        blocking.append("governed DID coverage diagnostic disabled by config")
        retry.append("ADD_REQUIRED_DIAGNOSTIC_PLAN")
        return _blocked(DIAGNOSTIC_NOT_EVALUATED, "governed DID coverage diagnostic disabled")

    if cfg.enable_statistical_parallel_trends:
        blocking.append("statistical parallel trends not governed in runtime_002")
        retry.append("CHANGE_READOUT_PLAN")
        return _blocked(DIAGNOSTIC_BLOCKED, "statistical parallel trends not governed")

    if cfg.enable_p_value_computation or cfg.enable_confidence_interval_computation:
        blocking.append("inference diagnostics not governed in runtime_002")
        retry.append("CHANGE_READOUT_PLAN")
        return _blocked(DIAGNOSTIC_BLOCKED, "p-value or CI computation not governed")

    if not requirement_id or requirement_id == "diagnostic_requirement_unspecified":
        missing_inputs.append("requirement_id")
        retry.append("ADD_REQUIRED_DIAGNOSTIC_PLAN")
        return _blocked(DIAGNOSTIC_BLOCKED, "requirement id missing")

    if cfg.require_execution_artifact_id and not execution_artifact_id:
        missing_inputs.append("execution_artifact_id")
        retry.append("RERUN_EXECUTION_WITH_REQUIRED_TRACE")
        return _blocked(DIAGNOSTIC_BLOCKED, "execution artifact id missing")

    execution_artifacts = _to_dict(data.get("execution_artifacts"))
    integrity_report = _to_dict(
        data.get("assignment_panel_integrity_report")
        or execution_artifacts.get("assignment_panel_integrity_report")
    )
    integrity_status = str(integrity_report.get("status") or "")
    if integrity_status.endswith("_FAILED") or integrity_status.endswith("_BLOCKED"):
        blocking.append("assignment-panel integrity failed upstream")
        retry.append("FIX_ASSIGNMENT_PANEL_JOIN")
        return _blocked(DIAGNOSTIC_BLOCKED, "assignment-panel integrity failed")

    if is_did_bootstrap_inference_instrument(instrument_id):
        blocking.append("DID_BOOTSTRAP is bootstrap inference; use DID_2X2_POINT_ESTIMATE for governed diagnostic")
        retry.append("FIX_INSTRUMENT_SPEC")
        return _blocked(DIAGNOSTIC_BLOCKED, "misleading instrument id for governed DID diagnostic")

    if not is_governed_did_point_estimate_instrument(instrument_id):
        blocking.append("unsupported instrument for governed DID diagnostic")
        retry.append("BLOCK_INSTRUMENT")
        return _blocked(DIAGNOSTIC_BLOCKED, "unsupported instrument")

    if not is_governed_did_diagnostic_type(requirement_type):
        blocking.append("unsupported diagnostic type for governed DID diagnostic")
        retry.append("ADD_REQUIRED_DIAGNOSTIC_PLAN")
        return _blocked(DIAGNOSTIC_BLOCKED, "unsupported diagnostic type")

    panel_data = data.get("panel_data")
    if not isinstance(panel_data, list) or not panel_data:
        missing_inputs.append("panel_data")
        retry.append("FIX_INPUT_DATA_CONTRACT")
        return _blocked(DIAGNOSTIC_BLOCKED, "panel data missing or empty")

    required_columns = {unit_id_field, time_field, outcome_field, treatment_field}
    if post_field:
        required_columns.add(post_field)
    for col in sorted(required_columns):
        if not any(isinstance(row, dict) and col in row for row in panel_data):
            missing_inputs.append(col)
    if missing_inputs:
        retry.append("FIX_DIAGNOSTIC_INPUTS")
        return _blocked(DIAGNOSTIC_BLOCKED, "required panel columns missing")

    treated_pre: list[float] = []
    treated_post: list[float] = []
    control_pre: list[float] = []
    control_post: list[float] = []

    for row in panel_data:
        if not isinstance(row, dict):
            retry.append("FIX_INPUT_DATA_CONTRACT")
            return _blocked(DIAGNOSTIC_BLOCKED, "panel row is not a dict")

        outcome = _as_float(row.get(outcome_field))
        if outcome is None:
            retry.append("FIX_DIAGNOSTIC_INPUTS")
            return _blocked(DIAGNOSTIC_BLOCKED, "non-numeric or missing outcome value")

        treatment = _resolve_treatment(row, treatment_field)
        if treatment is None:
            retry.append("FIX_DIAGNOSTIC_INPUTS")
            return _blocked(DIAGNOSTIC_BLOCKED, "invalid treatment indicator")

        post = _resolve_post_indicator(row, post_field, pre_period, post_values, time_field)
        if post is None:
            retry.append("FIX_DIAGNOSTIC_INPUTS")
            return _blocked(DIAGNOSTIC_BLOCKED, "cannot map row to pre/post period")

        if treatment == 1 and post == 0:
            treated_pre.append(outcome)
        elif treatment == 1 and post == 1:
            treated_post.append(outcome)
        elif treatment == 0 and post == 0:
            control_pre.append(outcome)
        elif treatment == 0 and post == 1:
            control_post.append(outcome)

    coverage_summary = {
        "treated_pre_count": len(treated_pre),
        "treated_post_count": len(treated_post),
        "control_pre_count": len(control_pre),
        "control_post_count": len(control_post),
    }
    sample_size_summary = dict(coverage_summary)

    min_count = max(int(cfg.minimum_cell_count), 1)
    failed_cells = [
        name
        for name, count in coverage_summary.items()
        if count < min_count
    ]
    if failed_cells:
        retry.append("FIX_DIAGNOSTIC_INPUTS")
        claim_boundary = _claim_boundary(computed=True, passed=False)
        trace = {
            "artifact_id": _ARTIFACT_ID,
            "diagnostic_id": diagnostic_id,
            "requirement_id": requirement_id,
            "diagnostic_status": DIAGNOSTIC_FAILED,
            "input_hash": _hash_payload(data),
            "config_hash": _hash_payload(cfg.__dict__),
        }
        fp = _failure_packet(
            failure_id=diagnostic_id,
            requirement_id=requirement_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            failure_status=DIAGNOSTIC_FAILED,
            missing_inputs=missing_inputs,
            blocked_requirements=[f"cell coverage below minimum: {failed_cells}"],
            suggested_retry_categories=retry,
            claim_boundary_report=claim_boundary,
        )
        return DIDCoverageDiagnosticResult(
            diagnostic_id=diagnostic_id,
            requirement_id=requirement_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            diagnostic_type=diagnostic_type,
            diagnostic_status=DIAGNOSTIC_FAILED,
            result_value=coverage_summary,
            threshold={"minimum_cell_count": min_count},
            threshold_direction="greater_than_or_equal",
            passed=False,
            blocking_result=True,
            interpretation=f"required cell coverage below minimum_cell_count={min_count}",
            evidence_level="computed_point_only",
            sample_size_summary=sample_size_summary,
            pre_period_summary={},
            coverage_summary=coverage_summary,
            artifact_references=(execution_artifact_id,) if execution_artifact_id else (),
            diagnostic_trace=trace,
            failure_packet=fp,
            claim_boundary_report=claim_boundary,
            warnings=_safe_str_list(warnings),
            blocking_reasons=(f"cell coverage below minimum: {failed_cells}",),
            diagnostic_result_computed=True,
            diagnostic_pass_fail_computed=True,
        )

    treated_pre_mean = _mean(treated_pre)
    control_pre_mean = _mean(control_pre)
    assert treated_pre_mean is not None
    assert control_pre_mean is not None
    pre_period_baseline_difference = treated_pre_mean - control_pre_mean

    normalized_pre_period_gap = None
    if cfg.compute_normalized_pre_period_gap:
        if control_pre_mean == 0:
            if cfg.inconclusive_on_zero_control_pre_mean:
                status = DIAGNOSTIC_INCONCLUSIVE
                interpretation = "normalized pre-period gap undefined due to zero control pre mean"
                passed = False
                blocking_result = False
                warnings.append(interpretation)
            else:
                warnings.append("normalized pre-period gap not computed: control pre mean is zero")
                status = DIAGNOSTIC_PASSED_WITH_WARNINGS
                interpretation = "coverage satisfied; normalized pre-period gap not computed"
                passed = True
                blocking_result = False
        else:
            normalized_pre_period_gap = pre_period_baseline_difference / abs(control_pre_mean)

    pre_period_summary = {
        "treated_pre_mean": treated_pre_mean,
        "control_pre_mean": control_pre_mean,
        "pre_period_baseline_difference": pre_period_baseline_difference,
        "normalized_pre_period_gap": normalized_pre_period_gap,
    }

    threshold = {
        "minimum_cell_count": min_count,
        "max_abs_normalized_pre_period_gap": cfg.max_abs_normalized_pre_period_gap,
    }
    threshold_direction = "abs_less_than_or_equal"

    status = DIAGNOSTIC_PASSED
    interpretation = "DID coverage and pre-period baseline diagnostic passed"
    passed = True
    blocking_result = False

    if normalized_pre_period_gap is not None and cfg.max_abs_normalized_pre_period_gap is not None:
        if abs(normalized_pre_period_gap) > cfg.max_abs_normalized_pre_period_gap:
            if cfg.fail_on_pre_period_gap_threshold:
                status = DIAGNOSTIC_FAILED
                passed = False
                blocking_result = True
                interpretation = "normalized pre-period gap exceeds configured threshold"
            elif cfg.warn_on_large_pre_period_gap:
                status = DIAGNOSTIC_PASSED_WITH_WARNINGS
                passed = True
                blocking_result = False
                interpretation = "coverage satisfied with large pre-period gap warning"
                warnings.append("normalized pre-period gap exceeds warning threshold")

    result_value = {
        **coverage_summary,
        **pre_period_summary,
    }
    claim_boundary = _claim_boundary(computed=True, passed=passed)
    trace = {
        "artifact_id": _ARTIFACT_ID,
        "diagnostic_id": diagnostic_id,
        "requirement_id": requirement_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "diagnostic_status": status,
        "algorithm_version": _ARTIFACT_VERSION,
        "input_hash": _hash_payload(data),
        "config_hash": _hash_payload(cfg.__dict__),
        "output_hash": _hash_payload(result_value),
        "runtime_environment": "deterministic_local_runtime",
    }

    failure_packet = None
    if status in (DIAGNOSTIC_FAILED, DIAGNOSTIC_BLOCKED):
        failure_packet = _failure_packet(
            failure_id=diagnostic_id,
            requirement_id=requirement_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            failure_status=status,
            missing_inputs=missing_inputs,
            blocked_requirements=blocking,
            suggested_retry_categories=retry or ["FIX_DIAGNOSTIC_INPUTS"],
            claim_boundary_report=claim_boundary,
        )

    return DIDCoverageDiagnosticResult(
        diagnostic_id=diagnostic_id,
        requirement_id=requirement_id,
        instrument_id=instrument_id,
        execution_artifact_id=execution_artifact_id,
        diagnostic_type=diagnostic_type,
        diagnostic_status=status,
        result_value=result_value,
        threshold=threshold,
        threshold_direction=threshold_direction,
        passed=passed,
        blocking_result=blocking_result,
        interpretation=interpretation,
        evidence_level="computed_point_only",
        sample_size_summary=sample_size_summary,
        pre_period_summary=pre_period_summary,
        coverage_summary=coverage_summary,
        artifact_references=(execution_artifact_id,) if execution_artifact_id else (),
        diagnostic_trace=trace,
        failure_packet=failure_packet,
        claim_boundary_report=claim_boundary,
        warnings=_safe_str_list(warnings),
        blocking_reasons=_safe_str_list(blocking),
        diagnostic_result_computed=True,
        diagnostic_pass_fail_computed=True,
    )


evaluate_governed_did_diagnostic = evaluate_did_coverage_diagnostic
