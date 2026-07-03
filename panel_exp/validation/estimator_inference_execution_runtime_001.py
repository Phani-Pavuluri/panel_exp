"""ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001 deterministic execution shell runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.validation.estimator_inference_did_executor_003 import (
    EFFECT_ESTIMATE_COMPUTED_POINT_ONLY,
    execute_did_point_estimate,
)
from panel_exp.validation.estimator_inference_executor_adapters_002 import (
    EXECUTOR_AVAILABLE_FOR_DRY_RUN,
    EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION,
    EXECUTOR_BLOCKED_BY_GOVERNANCE,
    EXECUTOR_NOT_IMPLEMENTED,
    build_governed_executor_result,
    get_governed_executor_registry,
)

_ARTIFACT_ID = "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "estimator_inference_execution_runtime_implemented_readiness_and_execution_packets_only_"
    "no_estimator_or_inference_execution"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001_summary.json"
)

SCOPE = "runtime_readiness_and_execution_packets_only_no_estimator_or_inference_execution"
RECOMMENDED_NEXT_ARTIFACT = "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001"

DEPENDS_ON = (
    "ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001",
    "READOUT_PLAN_RUNTIME_001",
    "READOUT_PLAN_CONTRACT_001",
    "READOUT_METHOD_GOVERNANCE_CONTRACT_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_RUNTIME_001",
)

EXECUTION_READY_FOR_RUNTIME = "EXECUTION_READY_FOR_RUNTIME"
EXECUTION_READY_WITH_WARNINGS = "EXECUTION_READY_WITH_WARNINGS"
EXECUTION_PROVISIONAL = "EXECUTION_PROVISIONAL"
EXECUTION_BLOCKED_BY_READOUT_PLAN = "EXECUTION_BLOCKED_BY_READOUT_PLAN"
EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT = "EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT"
EXECUTION_BLOCKED_BY_DATA_CONTRACT = "EXECUTION_BLOCKED_BY_DATA_CONTRACT"
EXECUTION_BLOCKED_BY_ESTIMAND = "EXECUTION_BLOCKED_BY_ESTIMAND"
EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC = "EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC"
EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS = "EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS"
EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA = "EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA"
EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS = "EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS"
EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS = "EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS"
EXECUTION_BLOCKED_BY_GOVERNANCE = "EXECUTION_BLOCKED_BY_GOVERNANCE"
EXECUTION_NOT_EVALUATED = "EXECUTION_NOT_EVALUATED"

INSTRUMENT_EXECUTION_READY = "INSTRUMENT_EXECUTION_READY"
INSTRUMENT_EXECUTION_READY_WITH_WARNINGS = "INSTRUMENT_EXECUTION_READY_WITH_WARNINGS"
INSTRUMENT_EXECUTION_PROVISIONAL = "INSTRUMENT_EXECUTION_PROVISIONAL"
INSTRUMENT_EXECUTION_BLOCKED = "INSTRUMENT_EXECUTION_BLOCKED"
INSTRUMENT_EXECUTION_FAILED = "INSTRUMENT_EXECUTION_FAILED"
INSTRUMENT_EXECUTION_NOT_RUN = "INSTRUMENT_EXECUTION_NOT_RUN"
INSTRUMENT_EXECUTION_COMPLETED = "INSTRUMENT_EXECUTION_COMPLETED"

PRIMARY_EXECUTION_CANDIDATE = "PRIMARY_EXECUTION_CANDIDATE"
SENSITIVITY_EXECUTION_CANDIDATE = "SENSITIVITY_EXECUTION_CANDIDATE"
DIAGNOSTIC_EXECUTION_CANDIDATE = "DIAGNOSTIC_EXECUTION_CANDIDATE"
REFERENCE_ONLY_EXECUTION_CANDIDATE = "REFERENCE_ONLY_EXECUTION_CANDIDATE"
BLOCKED_EXECUTION_CANDIDATE = "BLOCKED_EXECUTION_CANDIDATE"
NOT_EVALUATED_EXECUTION_CANDIDATE = "NOT_EVALUATED_EXECUTION_CANDIDATE"

RETRY_CATEGORIES = (
    "FIX_INPUT_DATA_CONTRACT",
    "FIX_ASSIGNMENT_ARTIFACT",
    "FIX_ESTIMAND_SPEC",
    "FIX_INSTRUMENT_SPEC",
    "FIX_UNCERTAINTY_SEMANTICS",
    "ADD_REQUIRED_DIAGNOSTICS",
    "ADD_REQUIRED_SENSITIVITY_CHECKS",
    "CHANGE_READOUT_PLAN",
    "BLOCK_INSTRUMENT",
    "BLOCK_DESIGN",
)

_STATUS_PRIORITY = {
    EXECUTION_BLOCKED_BY_READOUT_PLAN: 1,
    EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT: 2,
    EXECUTION_BLOCKED_BY_DATA_CONTRACT: 3,
    EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA: 4,
    EXECUTION_BLOCKED_BY_ESTIMAND: 5,
    EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC: 6,
    EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS: 7,
    EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS: 8,
    EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS: 9,
    EXECUTION_BLOCKED_BY_GOVERNANCE: 10,
    EXECUTION_PROVISIONAL: 11,
    EXECUTION_READY_WITH_WARNINGS: 12,
    EXECUTION_READY_FOR_RUNTIME: 13,
    EXECUTION_NOT_EVALUATED: 14,
}

_AUTH_FALSE_FLAGS = {
    "instrument_execution_completed": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "lift_computed": False,
    "roi_computed": False,
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

_ADAPTER_POSITIVE_FLAGS = {
    "governed_executor_adapter_registry_implemented": True,
    "executor_lookup_implemented": True,
    "executor_availability_evaluated": True,
    "executor_request_envelopes_generated": True,
}


@dataclass(frozen=True)
class EstimatorInferenceExecutionRuntimeConfig:
    block_on_readout_plan_blocked: bool = True
    block_on_missing_assignment_artifact: bool = True
    block_on_missing_reproducibility_manifest: bool = True
    block_on_missing_execution_data_contract: bool = True
    block_on_missing_required_columns: bool = True
    block_on_missing_treatment_assignment_join: bool = True
    block_on_missing_estimand: bool = True
    block_on_missing_uncertainty_semantics: bool = True
    block_on_missing_diagnostic_prerequisites: bool = False
    block_on_missing_sensitivity_prerequisites: bool = False
    allow_execution_without_governed_executor: bool = False
    enable_governed_executor_registry: bool = True
    allow_governed_executor_execution: bool = False
    allow_governed_did_point_estimate_execution: bool = False
    allow_dry_run_adapters: bool = True
    block_when_executor_not_implemented: bool = False


@dataclass(frozen=True)
class EstimatorInferenceExecutionRuntimeIssue:
    code: str
    message: str
    severity: str
    field: str | None = None
    instrument_id: str | None = None


@dataclass(frozen=True)
class InstrumentExecutionResult:
    instrument_id: str
    estimator_family: str | None
    inference_family: str | None
    execution_role: str
    instrument_execution_status: str
    execution_readiness_status: str
    input_data_contract_status: str
    assignment_artifact_status: str
    estimand_status: str
    uncertainty_semantics_status: str
    diagnostic_prerequisite_status: str
    sensitivity_prerequisite_status: str
    governance_status: str
    effect_estimate_report: dict[str, Any] | None
    uncertainty_report: dict[str, Any] | None
    inference_diagnostic_report: dict[str, Any] | None
    execution_trace: dict[str, Any]
    failure_packet: dict[str, Any] | None
    executor_lookup_status: str
    executor_adapter_name: str | None
    executor_adapter_version: str | None
    executor_available: bool
    executor_supports_dry_run: bool
    executor_supports_execution: bool
    executor_request: dict[str, Any] | None
    executor_result: dict[str, Any] | None
    executor_trace: dict[str, Any] | None
    executor_failure_packet: dict[str, Any] | None
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class EstimatorInferenceExecutionRuntimeSingleReport:
    artifact_id: str
    design_id: str
    execution_status: str
    execution_packet: dict[str, Any]
    instrument_execution_results: tuple[InstrumentExecutionResult, ...]
    primary_execution_candidates: tuple[str, ...]
    sensitivity_execution_candidates: tuple[str, ...]
    diagnostic_execution_candidates: tuple[str, ...]
    blocked_execution_candidates: tuple[str, ...]
    not_evaluated_execution_candidates: tuple[str, ...]
    execution_input_data_contract_report: dict[str, Any]
    assignment_artifact_reference: dict[str, Any]
    estimand_reference: dict[str, Any]
    uncertainty_reference: dict[str, Any]
    execution_trace: dict[str, Any]
    execution_provenance_manifest: dict[str, Any]
    execution_artifact_manifest: dict[str, Any]
    failure_packets: tuple[dict[str, Any], ...]
    executor_registry_summary: dict[str, Any]
    executor_lookup_results: tuple[dict[str, Any], ...]
    executor_availability_counts: dict[str, int]
    claim_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    issues: tuple[EstimatorInferenceExecutionRuntimeIssue, ...]


@dataclass(frozen=True)
class EstimatorInferenceExecutionRuntimeReport:
    artifact_id: str
    design_id: str | None
    execution_status: str | None
    execution_packet: dict[str, Any] | None
    instrument_execution_results: tuple[InstrumentExecutionResult, ...]
    primary_execution_candidates: tuple[str, ...]
    sensitivity_execution_candidates: tuple[str, ...]
    diagnostic_execution_candidates: tuple[str, ...]
    blocked_execution_candidates: tuple[str, ...]
    not_evaluated_execution_candidates: tuple[str, ...]
    execution_input_data_contract_report: dict[str, Any]
    assignment_artifact_reference: dict[str, Any]
    estimand_reference: dict[str, Any]
    uncertainty_reference: dict[str, Any]
    execution_trace: dict[str, Any]
    execution_provenance_manifest: dict[str, Any]
    execution_artifact_manifest: dict[str, Any]
    failure_packets: tuple[dict[str, Any], ...]
    executor_registry_summary: dict[str, Any]
    executor_lookup_results: tuple[dict[str, Any], ...]
    executor_availability_counts: dict[str, int]
    claim_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    issues: tuple[EstimatorInferenceExecutionRuntimeIssue, ...]
    design_reports: tuple[EstimatorInferenceExecutionRuntimeSingleReport, ...] = ()
    aggregate_summary: str | None = None
    final_verdict: str = _VERDICT


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _normalize_requests(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        return [dict(x) for x in input_data if isinstance(x, dict)]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [dict(x) for x in data["requests"] if isinstance(x, dict)]
    if data:
        return [data]
    return [{}]


def _as_list_of_dict(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(x) for x in value if isinstance(x, dict)]
    return []


def _as_list_of_str(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    return []


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _is_blocked(value: Any) -> bool:
    t = _token(value)
    if not t:
        return False
    return (
        "BLOCKED" in t
        or "NOT_EVALUATED" in t
        or t.startswith("FAIL")
        or "_FAILED" in t
        or "_MISSING" in t
    )


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _extract_instruments(req: dict[str, Any]) -> dict[str, dict[str, Any]]:
    instruments: dict[str, dict[str, Any]] = {}

    def _upsert(rows: list[dict[str, Any]], role: str) -> None:
        for row in rows:
            instrument_id = str(row.get("instrument_id") or "").strip()
            if not instrument_id:
                continue
            merged = dict(instruments.get(instrument_id, {}))
            merged.update(row)
            merged["instrument_id"] = instrument_id
            merged.setdefault("execution_role", role)
            instruments[instrument_id] = merged

    _upsert(_as_list_of_dict(req.get("planned_primary_candidates")), PRIMARY_EXECUTION_CANDIDATE)
    _upsert(
        _as_list_of_dict(req.get("planned_sensitivity_candidates")),
        SENSITIVITY_EXECUTION_CANDIDATE,
    )
    _upsert(
        _as_list_of_dict(req.get("planned_diagnostic_candidates")),
        DIAGNOSTIC_EXECUTION_CANDIDATE,
    )
    _upsert(_as_list_of_dict(req.get("blocked_instruments")), BLOCKED_EXECUTION_CANDIDATE)
    _upsert(_as_list_of_dict(req.get("not_evaluated_instruments")), NOT_EVALUATED_EXECUTION_CANDIDATE)
    return instruments


def _placeholder_effect_report(instrument: dict[str, Any], estimand_scope: dict[str, Any]) -> dict[str, Any]:
    return {
        "effect_estimate_report_status": "NOT_COMPUTED",
        "instrument_id": instrument.get("instrument_id"),
        "estimand": estimand_scope.get("estimand") or estimand_scope.get("estimand_type"),
        "metric_name": instrument.get("metric_name"),
        "effect_scale": instrument.get("effect_scale", "descriptive_only"),
        "unit_scope": estimand_scope.get("unit_scope"),
        "population_scope": estimand_scope.get("population_scope"),
        "time_window": estimand_scope.get("time_window"),
        "cell_contrast": estimand_scope.get("cell_contrast"),
    }


def _placeholder_uncertainty_report(instrument: dict[str, Any]) -> dict[str, Any]:
    return {
        "uncertainty_report_status": "NOT_COMPUTED",
        "instrument_id": instrument.get("instrument_id"),
        "uncertainty_semantics": instrument.get("uncertainty_semantics"),
        "interval_type": instrument.get("interval_type"),
        "p_value_semantics": instrument.get("p_value_semantics"),
    }


def _placeholder_diag_report(instrument: dict[str, Any]) -> dict[str, Any]:
    return {
        "inference_diagnostic_report_status": "NOT_COMPUTED",
        "instrument_id": instrument.get("instrument_id"),
    }


def _build_failure_packet(
    *,
    execution_id: str,
    instrument_id: str,
    execution_status: str,
    blocking_gates: list[str],
    missing_inputs: list[str],
    data_contract_failures: list[str],
    assignment_artifact_failures: list[str],
    estimand_failures: list[str],
    uncertainty_semantics_failures: list[str],
    diagnostic_prerequisite_failures: list[str],
    sensitivity_prerequisite_failures: list[str],
    governance_failures: list[str],
    claim_boundary_report: dict[str, Any],
) -> dict[str, Any]:
    retry: list[str] = []
    if data_contract_failures or "execution_data_contract" in missing_inputs:
        retry.append("FIX_INPUT_DATA_CONTRACT")
    if assignment_artifact_failures:
        retry.append("FIX_ASSIGNMENT_ARTIFACT")
    if estimand_failures:
        retry.append("FIX_ESTIMAND_SPEC")
    if uncertainty_semantics_failures:
        retry.append("FIX_UNCERTAINTY_SEMANTICS")
    if diagnostic_prerequisite_failures:
        retry.append("ADD_REQUIRED_DIAGNOSTICS")
    if sensitivity_prerequisite_failures:
        retry.append("ADD_REQUIRED_SENSITIVITY_CHECKS")
    if governance_failures:
        retry.extend(["CHANGE_READOUT_PLAN", "BLOCK_INSTRUMENT"])
    if not retry:
        retry.append("FIX_INSTRUMENT_SPEC")
    retry = [x for x in RETRY_CATEGORIES if x in retry]

    return {
        "failure_id": f"failure::{instrument_id}::{execution_status.lower()}",
        "execution_id": execution_id,
        "instrument_id": instrument_id,
        "execution_status": execution_status,
        "blocking_gates": blocking_gates,
        "missing_inputs": missing_inputs,
        "data_contract_failures": data_contract_failures,
        "assignment_artifact_failures": assignment_artifact_failures,
        "estimand_failures": estimand_failures,
        "uncertainty_semantics_failures": uncertainty_semantics_failures,
        "diagnostic_prerequisite_failures": diagnostic_prerequisite_failures,
        "sensitivity_prerequisite_failures": sensitivity_prerequisite_failures,
        "governance_failures": governance_failures,
        "suggested_retry_categories": retry,
        "claim_boundary_report": claim_boundary_report,
    }


def _evaluate_single_request(
    req: dict[str, Any],
    cfg: EstimatorInferenceExecutionRuntimeConfig,
) -> EstimatorInferenceExecutionRuntimeSingleReport:
    design_id = str(req.get("design_id") or "design_unspecified")
    execution_id = f"execution::{design_id}::{_hash_payload(req)[:12]}"
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    issues: list[EstimatorInferenceExecutionRuntimeIssue] = []
    failure_packets: list[dict[str, Any]] = []

    readout_plan_status = str(req.get("readout_plan_status") or EXECUTION_NOT_EVALUATED)
    assignment_artifact = _to_dict(req.get("assignment_artifact"))
    assignment_candidate = _to_dict(req.get("assignment_candidate"))
    reproducibility_manifest = _to_dict(req.get("reproducibility_manifest"))
    assignment_artifact_id = str(
        req.get("assignment_artifact_id")
        or assignment_artifact.get("artifact_id")
        or assignment_candidate.get("candidate_id")
        or ""
    )
    execution_data_contract = _to_dict(req.get("execution_data_contract"))
    estimand_scope = _to_dict(req.get("estimand_scope"))
    uncertainty_scope = _to_dict(req.get("uncertainty_scope"))
    diagnostic_prerequisites = _as_list_of_str(req.get("diagnostic_prerequisites"))
    sensitivity_prerequisites = _as_list_of_str(req.get("sensitivity_prerequisites"))
    production_governance_config = _to_dict(req.get("production_governance_config"))
    readout_plan_packet = _to_dict(req.get("readout_plan_packet"))

    instruments = _extract_instruments(req)
    if not instruments:
        issues.append(
            EstimatorInferenceExecutionRuntimeIssue(
                code="NO_PLANNED_INSTRUMENTS",
                message="No planned instruments supplied to execution runtime",
                severity="ERROR",
                field="planned_primary_candidates",
            )
        )

    global_status = EXECUTION_READY_FOR_RUNTIME
    if _is_blocked(readout_plan_status) and cfg.block_on_readout_plan_blocked:
        global_status = EXECUTION_BLOCKED_BY_READOUT_PLAN
        blocking_reasons.append("readout plan status blocked")

    assignment_missing = not (assignment_artifact or assignment_candidate or assignment_artifact_id)
    if assignment_missing and cfg.block_on_missing_assignment_artifact:
        global_status = EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT
        blocking_reasons.append("assignment artifact missing")
    if not reproducibility_manifest and cfg.block_on_missing_reproducibility_manifest:
        global_status = EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT
        blocking_reasons.append("reproducibility manifest missing")
    if not execution_data_contract and cfg.block_on_missing_execution_data_contract:
        global_status = EXECUTION_BLOCKED_BY_DATA_CONTRACT
        blocking_reasons.append("execution data contract missing")

    if not estimand_scope and cfg.block_on_missing_estimand:
        global_status = EXECUTION_BLOCKED_BY_ESTIMAND
        blocking_reasons.append("estimand scope missing")
    if not uncertainty_scope and cfg.block_on_missing_uncertainty_semantics:
        global_status = EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS
        blocking_reasons.append("uncertainty scope missing")

    blocked_roles = {_token(x) for x in _as_list_of_str(production_governance_config.get("blocked_roles"))}
    if "PRODUCTION" in blocked_roles:
        warnings.append("production governance restrictions remain in effect")

    input_data_contract_report = {
        "data_contract_present": bool(execution_data_contract),
        "panel_data_reference": execution_data_contract.get("panel_data_reference"),
        "required_columns": _as_list_of_str(execution_data_contract.get("required_columns")),
        "available_columns": _as_list_of_str(execution_data_contract.get("available_columns")),
        "required_grain": execution_data_contract.get("required_grain"),
        "actual_grain": execution_data_contract.get("actual_grain"),
        "required_treatment_assignment_join": execution_data_contract.get(
            "required_treatment_assignment_join"
        ),
        "treatment_assignment_join_available": execution_data_contract.get(
            "treatment_assignment_join_available"
        ),
        "data_version": execution_data_contract.get("data_version"),
        "data_hash": execution_data_contract.get("data_hash"),
        "validation_status": "PASS" if execution_data_contract else "MISSING",
    }

    results: list[InstrumentExecutionResult] = []
    lookup_results: list[dict[str, Any]] = []
    availability_counts: dict[str, int] = {}
    primary_candidates: list[str] = []
    sensitivity_candidates: list[str] = []
    diagnostic_candidates: list[str] = []
    blocked_candidates: list[str] = []
    not_evaluated_candidates: list[str] = []
    registry = get_governed_executor_registry() if cfg.enable_governed_executor_registry else None
    registry_summary = {
        "registry_enabled": bool(cfg.enable_governed_executor_registry),
        "registry_artifact_id": registry.artifact_id if registry else None,
        "known_instrument_count": len(registry.specs) if registry else 0,
    }

    for instrument in instruments.values():
        instrument_id = str(instrument.get("instrument_id") or "instrument_unspecified")
        role = str(instrument.get("execution_role") or REFERENCE_ONLY_EXECUTION_CANDIDATE)
        local_warnings: list[str] = _as_list_of_str(instrument.get("warnings"))
        local_blocking: list[str] = _as_list_of_str(instrument.get("blocking_reasons"))
        blocking_gates: list[str] = []
        missing_inputs: list[str] = []
        data_contract_failures: list[str] = []
        assignment_failures: list[str] = []
        estimand_failures: list[str] = []
        uncertainty_failures: list[str] = []
        diag_failures: list[str] = []
        sens_failures: list[str] = []
        gov_failures: list[str] = []

        readiness_status = global_status
        input_data_contract_status = "PASS"
        assignment_artifact_status = "PASS"
        estimand_status = "PASS"
        uncertainty_semantics_status = "PASS"
        diagnostic_prerequisite_status = "PASS"
        sensitivity_prerequisite_status = "PASS"
        governance_status = str(instrument.get("governance_status") or "NOT_EVALUATED")

        if role == PRIMARY_EXECUTION_CANDIDATE:
            primary_candidates.append(instrument_id)
        elif role == SENSITIVITY_EXECUTION_CANDIDATE:
            sensitivity_candidates.append(instrument_id)
        elif role == DIAGNOSTIC_EXECUTION_CANDIDATE:
            diagnostic_candidates.append(instrument_id)
        elif role == BLOCKED_EXECUTION_CANDIDATE:
            blocked_candidates.append(instrument_id)
        elif role == NOT_EVALUATED_EXECUTION_CANDIDATE:
            not_evaluated_candidates.append(instrument_id)

        if role in (BLOCKED_EXECUTION_CANDIDATE, NOT_EVALUATED_EXECUTION_CANDIDATE):
            readiness_status = EXECUTION_BLOCKED_BY_READOUT_PLAN
            local_blocking.append("planned instrument is blocked or not evaluated")
            blocking_gates.append("readout_plan_gate")

        if assignment_missing:
            assignment_artifact_status = "MISSING"
            assignment_failures.append("assignment artifact missing")
            missing_inputs.append("assignment_artifact")
            readiness_status = EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT
            blocking_gates.append("assignment_artifact_gate")
        elif not assignment_artifact_id:
            assignment_artifact_status = "MISSING_INSTRUMENT_REFERENCE"
            assignment_failures.append("instrument assignment_artifact_id missing")
            missing_inputs.append("assignment_artifact_id")
            readiness_status = EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT
            blocking_gates.append("assignment_artifact_gate")
        elif instrument.get("assignment_artifact_id") and (
            str(instrument.get("assignment_artifact_id")) != assignment_artifact_id
        ):
            assignment_artifact_status = "MISMATCH"
            assignment_failures.append("instrument assignment_artifact_id mismatches request")
            readiness_status = EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT
            blocking_gates.append("assignment_artifact_gate")

        if not reproducibility_manifest:
            assignment_failures.append("reproducibility manifest missing")
            missing_inputs.append("reproducibility_manifest")
            readiness_status = EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT
            blocking_gates.append("provenance_trace_gate")

        required_columns = _as_list_of_str(execution_data_contract.get("required_columns"))
        available_columns = set(_as_list_of_str(execution_data_contract.get("available_columns")))
        missing_required = [c for c in required_columns if c not in available_columns]
        if not execution_data_contract:
            input_data_contract_status = "MISSING"
            data_contract_failures.append("execution data contract missing")
            missing_inputs.append("execution_data_contract")
            readiness_status = EXECUTION_BLOCKED_BY_DATA_CONTRACT
            blocking_gates.append("data_contract_gate")
        elif missing_required and cfg.block_on_missing_required_columns:
            input_data_contract_status = "MISSING_REQUIRED_COLUMNS"
            data_contract_failures.append(f"missing required columns: {missing_required}")
            missing_inputs.extend(missing_required)
            readiness_status = EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA
            blocking_gates.append("data_contract_gate")

        if execution_data_contract and execution_data_contract.get("required_treatment_assignment_join"):
            join_available = bool(execution_data_contract.get("treatment_assignment_join_available"))
            if not join_available and cfg.block_on_missing_treatment_assignment_join:
                input_data_contract_status = "MISSING_TREATMENT_ASSIGNMENT_JOIN"
                data_contract_failures.append("treatment-assignment join unavailable")
                readiness_status = EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA
                blocking_gates.append("data_contract_gate")

        if execution_data_contract and execution_data_contract.get("required_metric_availability"):
            if not bool(execution_data_contract.get("metric_available")):
                input_data_contract_status = "METRIC_UNAVAILABLE"
                data_contract_failures.append("required metric unavailable")
                readiness_status = EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA
                blocking_gates.append("data_contract_gate")

        estimand_type = str(instrument.get("estimand_type") or "")
        if not estimand_scope and cfg.block_on_missing_estimand:
            estimand_status = "MISSING"
            estimand_failures.append("estimand scope missing")
            missing_inputs.append("estimand_scope")
            readiness_status = EXECUTION_BLOCKED_BY_ESTIMAND
            blocking_gates.append("estimand_compatibility_gate")
        elif estimand_type and estimand_scope.get("estimand_type") and (
            _token(estimand_type) != _token(estimand_scope.get("estimand_type"))
        ):
            estimand_status = "INCOMPATIBLE"
            estimand_failures.append("instrument estimand_type incompatible with request estimand_scope")
            readiness_status = EXECUTION_BLOCKED_BY_ESTIMAND
            blocking_gates.append("estimand_compatibility_gate")

        uncertainty_semantics = str(instrument.get("uncertainty_semantics") or "")
        if not uncertainty_semantics and cfg.block_on_missing_uncertainty_semantics:
            uncertainty_semantics_status = "MISSING"
            uncertainty_failures.append("instrument uncertainty_semantics missing")
            missing_inputs.append("uncertainty_semantics")
            readiness_status = EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS
            blocking_gates.append("uncertainty_semantics_gate")
        elif uncertainty_scope.get("semantics") and uncertainty_semantics:
            if _token(uncertainty_scope.get("semantics")) not in _token(uncertainty_semantics):
                uncertainty_semantics_status = "INCOMPATIBLE"
                uncertainty_failures.append("instrument uncertainty semantics incompatible with scope")
                readiness_status = EXECUTION_PROVISIONAL
                blocking_gates.append("uncertainty_semantics_gate")

        req_diag = _as_list_of_str(instrument.get("diagnostic_requirements"))
        missing_diag = [d for d in req_diag if d not in set(diagnostic_prerequisites)]
        if missing_diag:
            diagnostic_prerequisite_status = "MISSING"
            diag_failures.append(f"missing diagnostic prerequisites: {missing_diag}")
            if cfg.block_on_missing_diagnostic_prerequisites:
                readiness_status = EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS
            else:
                readiness_status = EXECUTION_PROVISIONAL
            blocking_gates.append("diagnostics_prerequisite_gate")

        req_sens = _as_list_of_str(instrument.get("sensitivity_requirements"))
        missing_sens = [s for s in req_sens if s not in set(sensitivity_prerequisites)]
        if missing_sens:
            sensitivity_prerequisite_status = "MISSING"
            sens_failures.append(f"missing sensitivity prerequisites: {missing_sens}")
            if cfg.block_on_missing_sensitivity_prerequisites:
                readiness_status = EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS
            else:
                readiness_status = EXECUTION_PROVISIONAL
            blocking_gates.append("sensitivity_prerequisite_gate")

        restrictions = _as_list_of_str(instrument.get("governance_restrictions"))
        gov_token = _token(governance_status)
        if (
            "UNRESOLVED" in gov_token
            or "BLOCKED" in gov_token
            or any("UNRESOLVED" in _token(x) for x in restrictions)
        ):
            gov_failures.append("governance restrictions unresolved")
            readiness_status = EXECUTION_BLOCKED_BY_GOVERNANCE
            blocking_gates.append("governance_restriction_gate")
        if role == DIAGNOSTIC_EXECUTION_CANDIDATE and PRIMARY_EXECUTION_CANDIDATE in _token(
            instrument.get("planning_category")
        ):
            gov_failures.append("diagnostic-only instruments cannot be promoted to primary")
            readiness_status = EXECUTION_BLOCKED_BY_GOVERNANCE
            blocking_gates.append("governance_restriction_gate")

        if readiness_status in (
            EXECUTION_READY_FOR_RUNTIME,
            EXECUTION_READY_WITH_WARNINGS,
        ) and local_warnings:
            readiness_status = EXECUTION_READY_WITH_WARNINGS

        if readiness_status in (
            EXECUTION_BLOCKED_BY_READOUT_PLAN,
            EXECUTION_BLOCKED_BY_ASSIGNMENT_ARTIFACT,
            EXECUTION_BLOCKED_BY_DATA_CONTRACT,
            EXECUTION_BLOCKED_BY_ESTIMAND,
            EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC,
            EXECUTION_BLOCKED_BY_UNCERTAINTY_SEMANTICS,
            EXECUTION_BLOCKED_BY_MISSING_INPUT_DATA,
            EXECUTION_BLOCKED_BY_DIAGNOSTIC_REQUIREMENTS,
            EXECUTION_BLOCKED_BY_SENSITIVITY_REQUIREMENTS,
            EXECUTION_BLOCKED_BY_GOVERNANCE,
        ):
            instrument_execution_status = INSTRUMENT_EXECUTION_BLOCKED
        elif readiness_status == EXECUTION_PROVISIONAL:
            instrument_execution_status = INSTRUMENT_EXECUTION_PROVISIONAL
        elif cfg.allow_execution_without_governed_executor:
            instrument_execution_status = INSTRUMENT_EXECUTION_READY
        else:
            instrument_execution_status = INSTRUMENT_EXECUTION_NOT_RUN
            local_warnings.append("no governed executor configured; execution not run")

        executor_lookup_status = EXECUTOR_NOT_IMPLEMENTED
        executor_adapter_name = None
        executor_adapter_version = None
        executor_available = False
        executor_supports_dry_run = False
        executor_supports_execution = False
        executor_request: dict[str, Any] | None = None
        executor_result: dict[str, Any] | None = None
        executor_trace: dict[str, Any] | None = None
        executor_failure_packet: dict[str, Any] | None = None
        effect_report: dict[str, Any] = _placeholder_effect_report(instrument, estimand_scope)
        uncertainty_report: dict[str, Any] = _placeholder_uncertainty_report(instrument)
        diagnostic_report: dict[str, Any] = _placeholder_diag_report(instrument)
        did_point_estimate_computed = False
        if cfg.enable_governed_executor_registry:
            adapter_config = {
                "allow_governed_did_point_estimate_execution": cfg.allow_governed_did_point_estimate_execution,
            }
            context = {
                "assignment_artifact_id": assignment_artifact_id,
                "execution_data_contract": execution_data_contract,
                "estimand_scope": estimand_scope,
                "uncertainty_scope": uncertainty_scope,
            }
            lookup, request, adapter_result = build_governed_executor_result(
                instrument, context, config=adapter_config
            )
            executor_lookup_status = lookup.availability_status
            executor_adapter_name = lookup.adapter_name
            executor_adapter_version = lookup.adapter_version
            executor_available = lookup.executor_available
            executor_supports_dry_run = lookup.supports_dry_run
            executor_supports_execution = lookup.supports_execution
            executor_request = {
                "instrument_id": request.instrument_id,
                "adapter_name": request.adapter_name,
                "adapter_version": request.adapter_version,
                "dry_run": request.dry_run,
            }
            executor_result = {
                "instrument_id": adapter_result.instrument_id,
                "availability_status": adapter_result.availability_status,
                "execution_status": adapter_result.execution_status,
                "completed": adapter_result.completed,
                "effect_estimate_report_status": adapter_result.effect_estimate_report_status,
                "uncertainty_report_status": adapter_result.uncertainty_report_status,
                "claim_authorized": adapter_result.claim_authorized,
            }
            executor_trace = adapter_result.trace.__dict__
            executor_failure_packet = (
                adapter_result.failure_packet.__dict__ if adapter_result.failure_packet else None
            )
            lookup_results.append(
                {
                    "instrument_id": lookup.instrument_id,
                    "availability_status": lookup.availability_status,
                    "adapter_name": lookup.adapter_name,
                    "adapter_version": lookup.adapter_version,
                    "supports_dry_run": lookup.supports_dry_run,
                    "supports_execution": lookup.supports_execution,
                }
            )
            availability_counts[lookup.availability_status] = (
                availability_counts.get(lookup.availability_status, 0) + 1
            )
            if (
                executor_lookup_status == EXECUTOR_NOT_IMPLEMENTED
                and cfg.block_when_executor_not_implemented
            ):
                readiness_status = EXECUTION_BLOCKED_BY_INSTRUMENT_SPEC
                instrument_execution_status = INSTRUMENT_EXECUTION_BLOCKED
                local_blocking.append("executor adapter not implemented")
                blocking_gates.append("execution_packet_gate")
            elif executor_lookup_status == EXECUTOR_BLOCKED_BY_GOVERNANCE:
                readiness_status = EXECUTION_BLOCKED_BY_GOVERNANCE
                instrument_execution_status = INSTRUMENT_EXECUTION_BLOCKED
                local_blocking.append("executor adapter blocked by governance")
                blocking_gates.append("governance_restriction_gate")
            elif executor_lookup_status == EXECUTOR_AVAILABLE_FOR_DRY_RUN and cfg.allow_dry_run_adapters:
                if instrument_execution_status == INSTRUMENT_EXECUTION_READY:
                    instrument_execution_status = INSTRUMENT_EXECUTION_NOT_RUN
                local_warnings.append("governed executor dry-run envelope generated; execution not run")
            elif (
                instrument_id == "DID_BOOTSTRAP"
                and executor_lookup_status == EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
                and cfg.allow_governed_did_point_estimate_execution
                and readiness_status in (EXECUTION_READY_FOR_RUNTIME, EXECUTION_READY_WITH_WARNINGS)
            ):
                panel_data = (
                    req.get("panel_data")
                    or execution_data_contract.get("panel_data")
                    or instrument.get("panel_data")
                )
                did_input = {
                    "instrument_id": instrument_id,
                    "estimator_family": instrument.get("estimator_family"),
                    "inference_family": instrument.get("inference_family"),
                    "panel_data": panel_data,
                    "unit_id_field": instrument.get("unit_id_field", "geo_id"),
                    "time_field": instrument.get("time_field", "week"),
                    "outcome_field": instrument.get("outcome_field", "sales"),
                    "treatment_field": instrument.get("treatment_field", "treated"),
                    "post_period_field": instrument.get("post_period_field"),
                    "pre_period": instrument.get("pre_period"),
                    "test_period": instrument.get("test_period"),
                    "assignment_artifact_id": assignment_artifact_id or instrument.get("assignment_artifact_id"),
                    "estimand": estimand_scope.get("estimand") or estimand_scope.get("estimand_type"),
                    "metric_name": instrument.get("metric_name"),
                }
                did_result = execute_did_point_estimate(
                    did_input,
                    config={"allow_governed_did_point_estimate_execution": True},
                )
                if did_result.did_point_estimate_computed:
                    instrument_execution_status = INSTRUMENT_EXECUTION_COMPLETED
                    did_point_estimate_computed = True
                    effect_report = did_result.effect_estimate_report or effect_report
                    uncertainty_report = did_result.uncertainty_report
                    diagnostic_report = did_result.inference_diagnostic_report
                    local_warnings.append("governed DID point estimate computed; inference not run")
                else:
                    instrument_execution_status = INSTRUMENT_EXECUTION_BLOCKED
                    local_blocking.extend(did_result.blocking_reasons)
                    if did_result.failure_packet:
                        failure_packets.append(did_result.failure_packet)
            elif (
                executor_lookup_status == EXECUTOR_AVAILABLE_FOR_GOVERNED_EXECUTION
                and cfg.allow_governed_executor_execution
            ):
                instrument_execution_status = INSTRUMENT_EXECUTION_NOT_RUN
                local_warnings.append("governed executor execution disabled in runtime_002 conservative mode")

        trace = {
            "execution_id": execution_id,
            "instrument_id": instrument_id,
            "readout_plan_artifact_id": readout_plan_packet.get("artifact_id", "READOUT_PLAN_RUNTIME_001"),
            "assignment_artifact_id": assignment_artifact_id or instrument.get("assignment_artifact_id"),
            "data_artifact_id": execution_data_contract.get("panel_data_reference"),
            "algorithm_version": _ARTIFACT_VERSION,
            "code_version": "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001",
            "config_hash": _hash_payload(cfg.__dict__),
            "data_hash": execution_data_contract.get("data_hash"),
            "input_hash": _hash_payload({"request": req, "instrument_id": instrument_id}),
            "output_hash": _hash_payload({"status": instrument_execution_status, "role": role}),
            "runtime_environment": "deterministic_local_runtime",
            "execution_timestamp_policy": "deterministic_no_wall_clock_required",
            "did_point_estimate_computed": did_point_estimate_computed,
        }

        claim_boundary = {
            "estimator_inference_execution_runtime_implemented": True,
            "execution_readiness_evaluated": True,
            "instrument_execution_requests_generated": True,
            "instrument_execution_results_generated": True,
            "execution_failure_packets_generated": bool(
                blocking_gates or instrument_execution_status == INSTRUMENT_EXECUTION_NOT_RUN
            ),
            "execution_trace_generated": True,
            "execution_artifact_manifest_generated": True,
            "governed_executor_adapter_registry_implemented": bool(
                cfg.enable_governed_executor_registry
            ),
            "executor_lookup_implemented": bool(cfg.enable_governed_executor_registry),
            "executor_availability_evaluated": bool(cfg.enable_governed_executor_registry),
            "executor_request_envelopes_generated": bool(cfg.enable_governed_executor_registry),
            "executor_dry_run_envelopes_generated": bool(
                cfg.enable_governed_executor_registry and executor_supports_dry_run
            ),
            "first_governed_executor_implemented": bool(cfg.allow_governed_did_point_estimate_execution),
            "did_point_estimate_executor_implemented": bool(cfg.allow_governed_did_point_estimate_execution),
            "did_point_estimate_computed": did_point_estimate_computed,
            "effect_estimate_computed": did_point_estimate_computed,
            **_AUTH_FALSE_FLAGS,
        }

        failure_packet: dict[str, Any] | None = None
        if blocking_gates or instrument_execution_status == INSTRUMENT_EXECUTION_NOT_RUN:
            failure_packet = _build_failure_packet(
                execution_id=execution_id,
                instrument_id=instrument_id,
                execution_status=readiness_status,
                blocking_gates=sorted(set(blocking_gates)),
                missing_inputs=sorted(set(missing_inputs)),
                data_contract_failures=sorted(set(data_contract_failures)),
                assignment_artifact_failures=sorted(set(assignment_failures)),
                estimand_failures=sorted(set(estimand_failures)),
                uncertainty_semantics_failures=sorted(set(uncertainty_failures)),
                diagnostic_prerequisite_failures=sorted(set(diag_failures)),
                sensitivity_prerequisite_failures=sorted(set(sens_failures)),
                governance_failures=sorted(set(gov_failures)),
                claim_boundary_report=claim_boundary,
            )
            failure_packets.append(failure_packet)

        results.append(
            InstrumentExecutionResult(
                instrument_id=instrument_id,
                estimator_family=(
                    str(instrument["estimator_family"]) if instrument.get("estimator_family") else None
                ),
                inference_family=(
                    str(instrument["inference_family"]) if instrument.get("inference_family") else None
                ),
                execution_role=role,
                instrument_execution_status=instrument_execution_status,
                execution_readiness_status=readiness_status,
                input_data_contract_status=input_data_contract_status,
                assignment_artifact_status=assignment_artifact_status,
                estimand_status=estimand_status,
                uncertainty_semantics_status=uncertainty_semantics_status,
                diagnostic_prerequisite_status=diagnostic_prerequisite_status,
                sensitivity_prerequisite_status=sensitivity_prerequisite_status,
                governance_status=governance_status,
                effect_estimate_report=effect_report,
                uncertainty_report=uncertainty_report,
                inference_diagnostic_report=diagnostic_report,
                execution_trace=trace,
                failure_packet=failure_packet,
                executor_lookup_status=executor_lookup_status,
                executor_adapter_name=executor_adapter_name,
                executor_adapter_version=executor_adapter_version,
                executor_available=executor_available,
                executor_supports_dry_run=executor_supports_dry_run,
                executor_supports_execution=executor_supports_execution,
                executor_request=executor_request,
                executor_result=executor_result,
                executor_trace=executor_trace,
                executor_failure_packet=executor_failure_packet,
                warnings=_safe_str_list(local_warnings),
                blocking_reasons=_safe_str_list(local_blocking),
            )
        )

    execution_status = global_status
    if results:
        statuses = [global_status, *[r.execution_readiness_status for r in results]]
        execution_status = min(statuses, key=lambda x: _STATUS_PRIORITY.get(x, 99))
        if execution_status == EXECUTION_READY_FOR_RUNTIME and any(r.warnings for r in results):
            execution_status = EXECUTION_READY_WITH_WARNINGS

    did_point_estimate_computed = any(
        r.instrument_id == "DID_BOOTSTRAP"
        and r.instrument_execution_status == INSTRUMENT_EXECUTION_COMPLETED
        and (r.effect_estimate_report or {}).get("estimation_status") == EFFECT_ESTIMATE_COMPUTED_POINT_ONLY
        for r in results
    )

    claim_boundary_report = {
        "estimator_inference_execution_runtime_implemented": True,
        "execution_readiness_evaluated": True,
        "instrument_execution_requests_generated": bool(instruments),
        "instrument_execution_results_generated": True,
        "execution_failure_packets_generated": bool(failure_packets),
        "execution_trace_generated": True,
        "execution_artifact_manifest_generated": True,
        "governed_executor_adapter_registry_implemented": bool(cfg.enable_governed_executor_registry),
        "executor_lookup_implemented": bool(cfg.enable_governed_executor_registry),
        "executor_availability_evaluated": bool(cfg.enable_governed_executor_registry),
        "executor_request_envelopes_generated": bool(cfg.enable_governed_executor_registry),
        "executor_dry_run_envelopes_generated": bool(
            cfg.enable_governed_executor_registry
            and any(x.get("supports_dry_run") for x in lookup_results)
        ),
        "first_governed_executor_implemented": bool(cfg.allow_governed_did_point_estimate_execution),
        "did_point_estimate_executor_implemented": bool(cfg.allow_governed_did_point_estimate_execution),
        "did_point_estimate_computed": did_point_estimate_computed,
        "effect_estimate_computed": did_point_estimate_computed,
        **_AUTH_FALSE_FLAGS,
    }

    execution_trace = {
        "execution_id": execution_id,
        "readout_plan_artifact_id": readout_plan_packet.get("artifact_id", "READOUT_PLAN_RUNTIME_001"),
        "assignment_artifact_id": assignment_artifact_id or "assignment_artifact_unspecified",
        "data_artifact_id": execution_data_contract.get("panel_data_reference"),
        "algorithm_version": _ARTIFACT_VERSION,
        "code_version": "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001",
        "config_hash": _hash_payload(cfg.__dict__),
        "data_hash": execution_data_contract.get("data_hash"),
        "input_hash": _hash_payload(req),
        "output_hash": _hash_payload(
            {
                "execution_status": execution_status,
                "instrument_statuses": [r.instrument_execution_status for r in results],
            }
        ),
        "runtime_environment": "deterministic_local_runtime",
        "execution_timestamp_policy": "deterministic_no_wall_clock_required",
    }
    provenance_manifest = {
        "execution_id": execution_id,
        "data_version": execution_data_contract.get("data_version"),
        "data_hash": execution_data_contract.get("data_hash"),
        "config_hash": execution_trace["config_hash"],
        "input_hash": execution_trace["input_hash"],
        "output_hash": execution_trace["output_hash"],
        "readout_plan_artifact_id": execution_trace["readout_plan_artifact_id"],
        "assignment_artifact_id": execution_trace["assignment_artifact_id"],
    }
    artifact_manifest = {
        "execution_id": execution_id,
        "artifact_ids": [
            _ARTIFACT_ID,
            "execution_packet",
            "instrument_execution_results",
            "execution_trace",
            "execution_provenance_manifest",
            "execution_failure_packets" if failure_packets else "execution_failure_packets_empty",
        ],
        "effect_estimate_reports_computed": did_point_estimate_computed,
        "uncertainty_reports_computed": False,
        "inference_diagnostic_reports_computed": False,
    }

    execution_packet = {
        "artifact_id": _ARTIFACT_ID,
        "design_id": design_id,
        "execution_id": execution_id,
        "execution_status": execution_status,
        "execution_requests": [
            {
                "instrument_id": r.instrument_id,
                "execution_role": r.execution_role,
                "execution_readiness_status": r.execution_readiness_status,
            }
            for r in results
        ],
        "warnings": list(_safe_str_list(warnings)),
        "blocking_reasons": list(_safe_str_list(blocking_reasons)),
    }

    return EstimatorInferenceExecutionRuntimeSingleReport(
        artifact_id=_ARTIFACT_ID,
        design_id=design_id,
        execution_status=execution_status,
        execution_packet=execution_packet,
        instrument_execution_results=tuple(results),
        primary_execution_candidates=_safe_str_list(primary_candidates),
        sensitivity_execution_candidates=_safe_str_list(sensitivity_candidates),
        diagnostic_execution_candidates=_safe_str_list(diagnostic_candidates),
        blocked_execution_candidates=_safe_str_list(blocked_candidates),
        not_evaluated_execution_candidates=_safe_str_list(not_evaluated_candidates),
        execution_input_data_contract_report=input_data_contract_report,
        assignment_artifact_reference={
            "assignment_artifact_id": assignment_artifact_id or None,
            "assignment_artifact_present": bool(assignment_artifact),
            "assignment_candidate_present": bool(assignment_candidate),
            "reproducibility_manifest_present": bool(reproducibility_manifest),
        },
        estimand_reference=estimand_scope,
        uncertainty_reference=uncertainty_scope,
        execution_trace=execution_trace,
        execution_provenance_manifest=provenance_manifest,
        execution_artifact_manifest=artifact_manifest,
        failure_packets=tuple(failure_packets),
        executor_registry_summary=registry_summary,
        executor_lookup_results=tuple(lookup_results),
        executor_availability_counts=availability_counts,
        claim_boundary_report=claim_boundary_report,
        warnings=_safe_str_list(warnings),
        blocking_reasons=_safe_str_list(blocking_reasons),
        issues=tuple(issues),
    )


def execute_estimator_inference(
    input_data: Any,
    config: EstimatorInferenceExecutionRuntimeConfig | None = None,
) -> EstimatorInferenceExecutionRuntimeReport:
    """Evaluate execution readiness and emit typed execution packets without estimator execution."""
    cfg = config or EstimatorInferenceExecutionRuntimeConfig()
    requests = _normalize_requests(input_data)
    reports = [_evaluate_single_request(r, cfg) for r in requests]

    if len(reports) == 1:
        r = reports[0]
        return EstimatorInferenceExecutionRuntimeReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            execution_status=r.execution_status,
            execution_packet=r.execution_packet,
            instrument_execution_results=r.instrument_execution_results,
            primary_execution_candidates=r.primary_execution_candidates,
            sensitivity_execution_candidates=r.sensitivity_execution_candidates,
            diagnostic_execution_candidates=r.diagnostic_execution_candidates,
            blocked_execution_candidates=r.blocked_execution_candidates,
            not_evaluated_execution_candidates=r.not_evaluated_execution_candidates,
            execution_input_data_contract_report=r.execution_input_data_contract_report,
            assignment_artifact_reference=r.assignment_artifact_reference,
            estimand_reference=r.estimand_reference,
            uncertainty_reference=r.uncertainty_reference,
            execution_trace=r.execution_trace,
            execution_provenance_manifest=r.execution_provenance_manifest,
            execution_artifact_manifest=r.execution_artifact_manifest,
            failure_packets=r.failure_packets,
            executor_registry_summary=r.executor_registry_summary,
            executor_lookup_results=r.executor_lookup_results,
            executor_availability_counts=r.executor_availability_counts,
            claim_boundary_report=r.claim_boundary_report,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
            issues=r.issues,
            design_reports=(r,),
        )

    all_warnings: list[str] = []
    all_blocking: list[str] = []
    all_issues: list[EstimatorInferenceExecutionRuntimeIssue] = []
    for r in reports:
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)
        all_issues.extend(r.issues)

    return EstimatorInferenceExecutionRuntimeReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        execution_status=None,
        execution_packet=None,
        instrument_execution_results=(),
        primary_execution_candidates=(),
        sensitivity_execution_candidates=(),
        diagnostic_execution_candidates=(),
        blocked_execution_candidates=(),
        not_evaluated_execution_candidates=(),
        execution_input_data_contract_report={},
        assignment_artifact_reference={},
        estimand_reference={},
        uncertainty_reference={},
        execution_trace={},
        execution_provenance_manifest={},
        execution_artifact_manifest={},
        failure_packets=(),
        executor_registry_summary={},
        executor_lookup_results=(),
        executor_availability_counts={},
        claim_boundary_report={
            "estimator_inference_execution_runtime_implemented": True,
            "execution_readiness_evaluated": True,
            "instrument_execution_requests_generated": True,
            "instrument_execution_results_generated": True,
            "execution_failure_packets_generated": True,
            "execution_trace_generated": True,
            "execution_artifact_manifest_generated": True,
            **_ADAPTER_POSITIVE_FLAGS,
            "executor_dry_run_envelopes_generated": True,
            **_AUTH_FALSE_FLAGS,
        },
        warnings=_safe_str_list(all_warnings),
        blocking_reasons=_safe_str_list(all_blocking),
        issues=tuple(all_issues),
        design_reports=tuple(reports),
        aggregate_summary=f"Evaluated {len(reports)} execution requests without ranking",
    )


execute_readout_instruments = execute_estimator_inference
run_estimator_inference_execution = execute_estimator_inference


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    smoke = {
        "design_id": "design_execution_smoke",
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
                "time_field": "date",
                "outcome_field": "sales",
                "treatment_field": "is_treated",
                "cell_id_field": "cell_id",
                "assignment_artifact_id": "assignment_artifact_smoke",
                "required_input_grain": "geo_week",
                "uncertainty_semantics": "bootstrap",
                "interval_type": "percentile",
                "p_value_semantics": "two_sided",
                "diagnostic_requirements": ["placebo_check"],
                "sensitivity_requirements": ["donor_pool_sensitivity"],
                "governance_restrictions": ["no_production_authorization"],
            }
        ],
        "planned_sensitivity_candidates": [],
        "planned_diagnostic_candidates": [],
        "blocked_instruments": [],
        "assignment_artifact": {"artifact_id": "assignment_artifact_smoke"},
        "assignment_artifact_id": "assignment_artifact_smoke",
        "assignment_candidate": {"candidate_id": "candidate_smoke"},
        "reproducibility_manifest": {"seed_policy": "deterministic"},
        "execution_data_contract": {
            "panel_data_reference": "panel_data_v1",
            "required_columns": ["geo_id", "date", "sales", "is_treated"],
            "available_columns": ["geo_id", "date", "sales", "is_treated"],
            "required_grain": "geo_week",
            "actual_grain": "geo_week",
            "required_treatment_assignment_join": True,
            "treatment_assignment_join_available": True,
            "required_metric_availability": True,
            "metric_available": True,
            "required_covariate_availability": False,
            "covariates_available": True,
            "required_spend_availability": False,
            "spend_available": True,
            "data_version": "v1",
            "data_hash": "hash_v1",
        },
        "estimand_scope": {
            "estimand_type": "STANDARD_INCREMENTALITY",
            "estimand": "STANDARD_INCREMENTALITY",
            "metric_name": "sales",
        },
        "uncertainty_scope": {"semantics": "bootstrap"},
        "diagnostic_prerequisites": ["placebo_check"],
        "sensitivity_prerequisites": ["donor_pool_sensitivity"],
        "production_governance_config": {"blocked_roles": ["production"]},
    }
    report = execute_estimator_inference(smoke)
    failed: list[str] = []
    if not report.claim_boundary_report["estimator_inference_execution_runtime_implemented"]:
        failed.append("runtime_not_implemented_flag")
    if report.claim_boundary_report["instrument_execution_completed"]:
        failed.append("instrument_execution_completed_flag_violation")
    if not report.instrument_execution_results:
        failed.append("missing_instrument_results")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "estimator_inference_execution_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "public_api": "execute_estimator_inference",
        "estimator_inference_execution_runtime_implemented": True,
        "execution_readiness_evaluated": True,
        "instrument_execution_requests_generated": True,
        "instrument_execution_results_generated": True,
        "execution_failure_packets_generated": bool(report.failure_packets),
        "execution_trace_generated": True,
        "execution_artifact_manifest_generated": True,
        **_AUTH_FALSE_FLAGS,
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "alternative_next_artifact": ALTERNATIVE_NEXT_ARTIFACT,
        "final_verdict": _VERDICT,
        "verdict": _VERDICT,
        "failed_scenarios": failed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {"verdict": _VERDICT, "failed_scenarios": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
