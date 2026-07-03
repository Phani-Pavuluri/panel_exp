"""READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001 deterministic evidence runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from panel_exp.validation.readout_diagnostics_sensitivity_contract_001 import (
    DIAGNOSTIC_STATUSES,
    EVIDENCE_SUFFICIENCY_STATUSES,
    RETRY_CATEGORIES,
    SENSITIVITY_STATUSES,
)
from panel_exp.validation.readout_did_diagnostics_002 import (
    evaluate_did_coverage_diagnostic,
    is_governed_did_diagnostic_type,
    to_provided_diagnostic_result,
)
from panel_exp.validation.estimator_inference_did_executor_003 import GOVERNED_DID_INSTRUMENT_IDS

_ARTIFACT_ID = "READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "readout_diagnostics_sensitivity_runtime_implemented_evidence_planning_and_sufficiency_only_"
    "no_diagnostic_or_sensitivity_execution"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/READOUT_DIAGNOSTICS_AND_SENSITIVITY_RUNTIME_001_summary.json"
)

SCOPE = "runtime_evidence_planning_and_sufficiency_only_no_diagnostic_or_sensitivity_execution"
RECOMMENDED_NEXT_ARTIFACT = "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_003_FIRST_GOVERNED_EXECUTOR"
ALTERNATIVE_NEXT_ARTIFACT = "CLAIM_AUTHORIZATION_CONTRACT_001"

DEPENDS_ON = (
    "READOUT_DIAGNOSTICS_AND_SENSITIVITY_CONTRACT_001",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_002_GOVERNED_EXECUTOR_ADAPTERS",
    "ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001",
    "READOUT_PLAN_RUNTIME_001",
    "METHOD_SUITABILITY_RUNTIME_001",
    "DESIGN_ASSIGNMENT_RUNTIME_001",
)

DIAGNOSTIC_REQUIRED_NOT_PLANNED = "DIAGNOSTIC_REQUIRED_NOT_PLANNED"
DIAGNOSTIC_PLANNED_NOT_RUN = "DIAGNOSTIC_PLANNED_NOT_RUN"
DIAGNOSTIC_NOT_APPLICABLE = "DIAGNOSTIC_NOT_APPLICABLE"
DIAGNOSTIC_BLOCKED = "DIAGNOSTIC_BLOCKED"
DIAGNOSTIC_FAILED = "DIAGNOSTIC_FAILED"
DIAGNOSTIC_PASSED = "DIAGNOSTIC_PASSED"
DIAGNOSTIC_PASSED_WITH_WARNINGS = "DIAGNOSTIC_PASSED_WITH_WARNINGS"
DIAGNOSTIC_INCONCLUSIVE = "DIAGNOSTIC_INCONCLUSIVE"
DIAGNOSTIC_NOT_EVALUATED = "DIAGNOSTIC_NOT_EVALUATED"

SENSITIVITY_REQUIRED_NOT_PLANNED = "SENSITIVITY_REQUIRED_NOT_PLANNED"
SENSITIVITY_PLANNED_NOT_RUN = "SENSITIVITY_PLANNED_NOT_RUN"
SENSITIVITY_NOT_APPLICABLE = "SENSITIVITY_NOT_APPLICABLE"
SENSITIVITY_BLOCKED = "SENSITIVITY_BLOCKED"
SENSITIVITY_FAILED = "SENSITIVITY_FAILED"
SENSITIVITY_PASSED = "SENSITIVITY_PASSED"
SENSITIVITY_PASSED_WITH_WARNINGS = "SENSITIVITY_PASSED_WITH_WARNINGS"
SENSITIVITY_INCONCLUSIVE = "SENSITIVITY_INCONCLUSIVE"
SENSITIVITY_NOT_EVALUATED = "SENSITIVITY_NOT_EVALUATED"

EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW = "EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW"
EVIDENCE_SUFFICIENT_WITH_WARNINGS = "EVIDENCE_SUFFICIENT_WITH_WARNINGS"
EVIDENCE_PROVISIONAL = "EVIDENCE_PROVISIONAL"
EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS = "EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS"
EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY = "EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY"
EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS = "EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS"
EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY = "EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY"
EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED = "EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED"
EVIDENCE_BLOCKED_BY_GOVERNANCE = "EVIDENCE_BLOCKED_BY_GOVERNANCE"
EVIDENCE_NOT_EVALUATED = "EVIDENCE_NOT_EVALUATED"

INSTRUMENT_EXECUTION_COMPLETED = "INSTRUMENT_EXECUTION_COMPLETED"
DIAGNOSTIC_EXECUTION_CANDIDATE = "DIAGNOSTIC_EXECUTION_CANDIDATE"

_EVIDENCE_PRIORITY = {
    EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED: 1,
    EVIDENCE_BLOCKED_BY_GOVERNANCE: 2,
    EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS: 3,
    EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY: 4,
    EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS: 5,
    EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY: 6,
    EVIDENCE_PROVISIONAL: 7,
    EVIDENCE_SUFFICIENT_WITH_WARNINGS: 8,
    EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW: 9,
    EVIDENCE_NOT_EVALUATED: 10,
}

_AUTH_FALSE_FLAGS = {
    "diagnostic_check_executed": False,
    "sensitivity_check_executed": False,
    "diagnostic_result_computed": False,
    "sensitivity_result_computed": False,
    "diagnostic_pass_fail_computed": False,
    "sensitivity_pass_fail_computed": False,
    "estimator_execution_implemented": False,
    "inference_execution_implemented": False,
    "effect_estimate_computed": False,
    "lift_computed": False,
    "roi_computed": False,
    "p_value_computed": False,
    "confidence_interval_computed": False,
    "uncertainty_computed": False,
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
class ReadoutDiagnosticsSensitivityRuntimeConfig:
    require_execution_completed: bool = True
    block_on_missing_diagnostic_requirements: bool = True
    block_on_missing_sensitivity_requirements: bool = True
    block_on_missing_required_diagnostic_results: bool = True
    block_on_missing_required_sensitivity_results: bool = True
    block_on_failed_blocking_diagnostics: bool = True
    block_on_failed_blocking_sensitivity: bool = True
    block_on_inconclusive_blocking_evidence: bool = False
    allow_diagnostic_only_for_production_claim: bool = False
    enable_governed_did_coverage_diagnostic: bool = False
    enable_statistical_parallel_trends: bool = False
    enable_p_value_computation: bool = False
    enable_confidence_interval_computation: bool = False


@dataclass(frozen=True)
class ReadoutDiagnosticsSensitivityRuntimeIssue:
    code: str
    message: str
    severity: str
    field: str | None = None
    requirement_id: str | None = None


@dataclass(frozen=True)
class ReadoutDiagnosticsSensitivityRuntimeSingleReport:
    artifact_id: str
    design_id: str
    evidence_sufficiency_status: str
    diagnostic_plans: tuple[dict[str, Any], ...]
    sensitivity_plans: tuple[dict[str, Any], ...]
    diagnostic_evidence_packets: tuple[dict[str, Any], ...]
    sensitivity_evidence_packets: tuple[dict[str, Any], ...]
    diagnostic_failure_packets: tuple[dict[str, Any], ...]
    sensitivity_failure_packets: tuple[dict[str, Any], ...]
    evidence_aggregation_report: dict[str, Any]
    evidence_sufficiency_report: dict[str, Any]
    claim_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    issues: tuple[ReadoutDiagnosticsSensitivityRuntimeIssue, ...]


@dataclass(frozen=True)
class ReadoutDiagnosticsSensitivityRuntimeReport:
    artifact_id: str
    design_id: str | None
    evidence_sufficiency_status: str | None
    diagnostic_plans: tuple[dict[str, Any], ...]
    sensitivity_plans: tuple[dict[str, Any], ...]
    diagnostic_evidence_packets: tuple[dict[str, Any], ...]
    sensitivity_evidence_packets: tuple[dict[str, Any], ...]
    diagnostic_failure_packets: tuple[dict[str, Any], ...]
    sensitivity_failure_packets: tuple[dict[str, Any], ...]
    evidence_aggregation_report: dict[str, Any]
    evidence_sufficiency_report: dict[str, Any]
    claim_boundary_report: dict[str, Any]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    issues: tuple[ReadoutDiagnosticsSensitivityRuntimeIssue, ...]
    design_reports: tuple[ReadoutDiagnosticsSensitivityRuntimeSingleReport, ...] = ()
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


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_str_list(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(v for v in values if v))


def _execution_completed(
    execution_status: str,
    execution_artifacts: dict[str, Any],
    instrument_results: list[dict[str, Any]],
) -> bool:
    if _token(execution_status) in ("EXECUTION_COMPLETED", "INSTRUMENT_EXECUTION_COMPLETED"):
        return True
    if execution_artifacts.get("execution_completed") is True:
        return True
    if instrument_results and all(
        _token(r.get("instrument_execution_status")) == INSTRUMENT_EXECUTION_COMPLETED
        for r in instrument_results
    ):
        return True
    return False


def _result_index(results: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in results:
        rid = str(row.get(key) or row.get("requirement_id") or "")
        if rid:
            indexed[rid] = row
    return indexed


def _build_failure_packet(
    *,
    failure_id: str,
    requirement_id: str,
    plan_id: str,
    instrument_id: str,
    execution_artifact_id: str,
    failure_status: str,
    missing_inputs: list[str],
    blocked_requirements: list[str],
    failed_requirements: list[str],
    inconclusive_requirements: list[str],
    governance_failures: list[str],
    claim_boundary_report: dict[str, Any],
    is_diagnostic: bool,
) -> dict[str, Any]:
    retry: list[str] = []
    if missing_inputs:
        retry.append("FIX_DIAGNOSTIC_INPUTS" if is_diagnostic else "FIX_SENSITIVITY_INPUTS")
    if blocked_requirements or failed_requirements:
        retry.append("ADD_REQUIRED_DIAGNOSTIC_PLAN" if is_diagnostic else "ADD_REQUIRED_SENSITIVITY_PLAN")
    if governance_failures:
        retry.extend(["CHANGE_READOUT_PLAN", "BLOCK_INSTRUMENT"])
    if not retry:
        retry.append("RERUN_EXECUTION_WITH_REQUIRED_TRACE")
    retry = [x for x in RETRY_CATEGORIES if x in retry]
    return {
        "failure_id": failure_id,
        "requirement_id": requirement_id,
        "plan_id": plan_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "failure_status": failure_status,
        "missing_inputs": sorted(set(missing_inputs)),
        "blocked_requirements": sorted(set(blocked_requirements)),
        "failed_requirements": sorted(set(failed_requirements)),
        "inconclusive_requirements": sorted(set(inconclusive_requirements)),
        "governance_failures": sorted(set(governance_failures)),
        "suggested_retry_categories": retry,
        "claim_boundary_report": claim_boundary_report,
    }


def _evaluate_diagnostic_requirement(
    req: dict[str, Any],
    *,
    design_id: str,
    execution_artifact_id: str,
    provided_result: dict[str, Any] | None,
    claim_scope: dict[str, Any],
    cfg: ReadoutDiagnosticsSensitivityRuntimeConfig,
    claim_boundary: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None, str]:
    requirement_id = str(req.get("requirement_id") or "diagnostic_requirement_unspecified")
    instrument_id = str(req.get("applies_to_instrument_id") or "instrument_unspecified")
    plan_id = f"diag_plan::{design_id}::{requirement_id}"
    warnings: list[str] = []
    governance_failures: list[str] = []
    evidence_status = EVIDENCE_NOT_EVALUATED

    role = _token(req.get("applies_to_execution_role"))
    required_for_production = bool(req.get("required_for_production"))
    claim_type = _token(claim_scope.get("claim_type") or claim_scope.get("required_claim_type"))
    if (
        not cfg.allow_diagnostic_only_for_production_claim
        and required_for_production
        and role == DIAGNOSTIC_EXECUTION_CANDIDATE
        and claim_type in ("PRODUCTION", "CAUSAL", "INCREMENTAL_LIFT")
    ):
        governance_failures.append("diagnostic-only evidence cannot support production claim")
        evidence_status = EVIDENCE_BLOCKED_BY_GOVERNANCE

    planned_status = DIAGNOSTIC_PLANNED_NOT_RUN
    if provided_result:
        result_status = str(provided_result.get("result_status") or DIAGNOSTIC_NOT_EVALUATED)
    else:
        result_status = DIAGNOSTIC_PLANNED_NOT_RUN

    blocking_if_missing = bool(req.get("blocking_if_missing", True))
    blocking_if_failed = bool(req.get("blocking_if_failed", True))

    if provided_result:
        if governance_failures:
            evidence_status = EVIDENCE_BLOCKED_BY_GOVERNANCE
        elif result_status == DIAGNOSTIC_PASSED:
            evidence_status = EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW
        elif result_status == DIAGNOSTIC_PASSED_WITH_WARNINGS:
            evidence_status = EVIDENCE_SUFFICIENT_WITH_WARNINGS
            warnings.append("diagnostic passed with warnings")
        elif result_status == DIAGNOSTIC_FAILED:
            if blocking_if_failed and cfg.block_on_failed_blocking_diagnostics:
                evidence_status = EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS
            else:
                evidence_status = EVIDENCE_PROVISIONAL
                warnings.append("nonblocking diagnostic failure produces provisional evidence")
        elif result_status == DIAGNOSTIC_INCONCLUSIVE:
            if cfg.block_on_inconclusive_blocking_evidence:
                evidence_status = EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS
            else:
                evidence_status = EVIDENCE_PROVISIONAL
                warnings.append("inconclusive diagnostic produces provisional evidence")
        elif result_status == DIAGNOSTIC_BLOCKED:
            evidence_status = EVIDENCE_BLOCKED_BY_GOVERNANCE
    else:
        if blocking_if_missing and cfg.block_on_missing_required_diagnostic_results:
            evidence_status = EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS
        else:
            evidence_status = EVIDENCE_PROVISIONAL
            warnings.append("missing diagnostic result treated as provisional")

    plan = {
        "plan_id": plan_id,
        "requirement_id": requirement_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "planned_check_type": str(req.get("requirement_type") or "DIAGNOSTIC"),
        "planned_input_artifacts": _as_list_of_str(req.get("planned_input_artifacts")),
        "planned_output_artifacts": ["diagnostic_evidence_packet"],
        "planned_threshold_policy": req.get("threshold_policy"),
        "planned_execution_mode": "not_run",
        "planned_status": planned_status,
        "blocking_policy": "block_if_missing_or_failed" if blocking_if_missing or blocking_if_failed else "warn_only",
        "warnings": list(_safe_str_list(warnings)),
    }

    packet = {
        "requirement_id": requirement_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "requirement_type": str(req.get("requirement_type") or "DIAGNOSTIC"),
        "planned_status": planned_status,
        "result_status": result_status,
        "evidence_status": evidence_status,
        "blocking_result": evidence_status
        in (
            EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS,
            EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS,
            EVIDENCE_BLOCKED_BY_GOVERNANCE,
        ),
        "evidence_level": provided_result.get("evidence_level") if provided_result else "not_computed",
        "artifact_references": _as_list_of_str(
            provided_result.get("artifact_references") if provided_result else []
        ),
        "warnings": list(_safe_str_list(warnings)),
    }
    if provided_result:
        for key in (
            "result_value",
            "threshold",
            "threshold_direction",
            "passed",
            "interpretation",
            "result_id",
        ):
            if key in provided_result:
                packet[key] = provided_result[key]

    failure_packet = None
    if evidence_status in (
        EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS,
        EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS,
        EVIDENCE_BLOCKED_BY_GOVERNANCE,
        EVIDENCE_PROVISIONAL,
    ):
        failure_packet = _build_failure_packet(
            failure_id=f"diag_failure::{requirement_id}::{evidence_status.lower()}",
            requirement_id=requirement_id,
            plan_id=plan_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            failure_status=evidence_status,
            missing_inputs=[] if provided_result else ["diagnostic_result"],
            blocked_requirements=governance_failures,
            failed_requirements=[requirement_id]
            if evidence_status == EVIDENCE_INSUFFICIENT_FAILED_DIAGNOSTICS
            else [],
            inconclusive_requirements=[requirement_id]
            if result_status == DIAGNOSTIC_INCONCLUSIVE
            else [],
            governance_failures=governance_failures,
            claim_boundary_report=claim_boundary,
            is_diagnostic=True,
        )

    return plan, packet, failure_packet, evidence_status


def _governed_did_diagnostic_config(cfg: ReadoutDiagnosticsSensitivityRuntimeConfig) -> dict[str, Any]:
    return {
        "enable_governed_did_coverage_diagnostic": True,
        "enable_statistical_parallel_trends": cfg.enable_statistical_parallel_trends,
        "enable_p_value_computation": cfg.enable_p_value_computation,
        "enable_confidence_interval_computation": cfg.enable_confidence_interval_computation,
    }


def _maybe_compute_governed_did_diagnostic(
    req_row: dict[str, Any],
    *,
    req: dict[str, Any],
    execution_artifacts: dict[str, Any],
    execution_artifact_id: str,
    cfg: ReadoutDiagnosticsSensitivityRuntimeConfig,
) -> dict[str, Any] | None:
    if not cfg.enable_governed_did_coverage_diagnostic:
        return None
    requirement_type = str(req_row.get("requirement_type") or "")
    instrument_id = str(req_row.get("applies_to_instrument_id") or "")
    if not is_governed_did_diagnostic_type(requirement_type):
        return None
    if instrument_id not in GOVERNED_DID_INSTRUMENT_IDS:
        return None
    panel_data = req.get("panel_data") or execution_artifacts.get("panel_data")
    if panel_data is None:
        return None
    diag_input = {
        "requirement_id": req_row.get("requirement_id"),
        "requirement_type": requirement_type,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "panel_data": panel_data,
        "unit_id_field": req.get("unit_id_field", "geo_id"),
        "time_field": req.get("time_field", "week"),
        "outcome_field": req.get("outcome_field", "sales"),
        "treatment_field": req.get("treatment_field", "treated"),
        "post_period_field": req.get("post_period_field"),
        "pre_period": req.get("pre_period"),
        "test_period": req.get("test_period"),
        "claim_scope": req.get("claim_scope"),
    }
    diag_result = evaluate_did_coverage_diagnostic(
        diag_input,
        config=_governed_did_diagnostic_config(cfg),
    )
    if diag_result.diagnostic_status == DIAGNOSTIC_NOT_EVALUATED:
        return None
    return to_provided_diagnostic_result(diag_result)


def _evaluate_sensitivity_requirement(
    req: dict[str, Any],
    *,
    design_id: str,
    execution_artifact_id: str,
    provided_result: dict[str, Any] | None,
    claim_scope: dict[str, Any],
    cfg: ReadoutDiagnosticsSensitivityRuntimeConfig,
    claim_boundary: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None, str]:
    requirement_id = str(req.get("requirement_id") or "sensitivity_requirement_unspecified")
    instrument_id = str(req.get("applies_to_instrument_id") or "instrument_unspecified")
    plan_id = f"sens_plan::{design_id}::{requirement_id}"
    warnings: list[str] = []
    governance_failures: list[str] = []
    evidence_status = EVIDENCE_NOT_EVALUATED

    role = _token(req.get("applies_to_execution_role"))
    required_for_production = bool(req.get("required_for_production"))
    claim_type = _token(claim_scope.get("claim_type") or claim_scope.get("required_claim_type"))
    if (
        not cfg.allow_diagnostic_only_for_production_claim
        and required_for_production
        and role == DIAGNOSTIC_EXECUTION_CANDIDATE
        and claim_type in ("PRODUCTION", "CAUSAL", "INCREMENTAL_LIFT")
    ):
        governance_failures.append("diagnostic-only evidence cannot support production claim")
        evidence_status = EVIDENCE_BLOCKED_BY_GOVERNANCE

    planned_status = SENSITIVITY_PLANNED_NOT_RUN
    if provided_result:
        result_status = str(provided_result.get("result_status") or SENSITIVITY_NOT_EVALUATED)
    else:
        result_status = SENSITIVITY_PLANNED_NOT_RUN

    blocking_if_missing = bool(req.get("blocking_if_missing", True))
    blocking_if_failed = bool(req.get("blocking_if_failed", True))

    if provided_result:
        if governance_failures:
            evidence_status = EVIDENCE_BLOCKED_BY_GOVERNANCE
        elif result_status == SENSITIVITY_PASSED:
            evidence_status = EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW
        elif result_status == SENSITIVITY_PASSED_WITH_WARNINGS:
            evidence_status = EVIDENCE_SUFFICIENT_WITH_WARNINGS
            warnings.append("sensitivity passed with warnings")
        elif result_status == SENSITIVITY_FAILED:
            if blocking_if_failed and cfg.block_on_failed_blocking_sensitivity:
                evidence_status = EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY
            else:
                evidence_status = EVIDENCE_PROVISIONAL
                warnings.append("nonblocking sensitivity failure produces provisional evidence")
        elif result_status == SENSITIVITY_INCONCLUSIVE:
            if cfg.block_on_inconclusive_blocking_evidence:
                evidence_status = EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY
            else:
                evidence_status = EVIDENCE_PROVISIONAL
                warnings.append("inconclusive sensitivity produces provisional evidence")
        elif result_status == SENSITIVITY_BLOCKED:
            evidence_status = EVIDENCE_BLOCKED_BY_GOVERNANCE
    else:
        if blocking_if_missing and cfg.block_on_missing_required_sensitivity_results:
            evidence_status = EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY
        else:
            evidence_status = EVIDENCE_PROVISIONAL
            warnings.append("missing sensitivity result treated as provisional")

    plan = {
        "plan_id": plan_id,
        "requirement_id": requirement_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "planned_check_type": str(req.get("requirement_type") or "SENSITIVITY"),
        "planned_input_artifacts": _as_list_of_str(req.get("planned_input_artifacts")),
        "planned_output_artifacts": ["sensitivity_evidence_packet"],
        "planned_threshold_policy": req.get("threshold_policy"),
        "planned_execution_mode": "not_run",
        "planned_status": planned_status,
        "blocking_policy": "block_if_missing_or_failed" if blocking_if_missing or blocking_if_failed else "warn_only",
        "warnings": list(_safe_str_list(warnings)),
    }

    packet = {
        "requirement_id": requirement_id,
        "instrument_id": instrument_id,
        "execution_artifact_id": execution_artifact_id,
        "requirement_type": str(req.get("requirement_type") or "SENSITIVITY"),
        "planned_status": planned_status,
        "result_status": result_status,
        "evidence_status": evidence_status,
        "blocking_result": evidence_status
        in (
            EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY,
            EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY,
            EVIDENCE_BLOCKED_BY_GOVERNANCE,
        ),
        "evidence_level": provided_result.get("evidence_level") if provided_result else "not_computed",
        "artifact_references": _as_list_of_str(
            provided_result.get("artifact_references") if provided_result else []
        ),
        "warnings": list(_safe_str_list(warnings)),
    }

    failure_packet = None
    if evidence_status in (
        EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY,
        EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY,
        EVIDENCE_BLOCKED_BY_GOVERNANCE,
        EVIDENCE_PROVISIONAL,
    ):
        failure_packet = _build_failure_packet(
            failure_id=f"sens_failure::{requirement_id}::{evidence_status.lower()}",
            requirement_id=requirement_id,
            plan_id=plan_id,
            instrument_id=instrument_id,
            execution_artifact_id=execution_artifact_id,
            failure_status=evidence_status,
            missing_inputs=[] if provided_result else ["sensitivity_result"],
            blocked_requirements=governance_failures,
            failed_requirements=[requirement_id]
            if evidence_status == EVIDENCE_INSUFFICIENT_FAILED_SENSITIVITY
            else [],
            inconclusive_requirements=[requirement_id]
            if result_status == SENSITIVITY_INCONCLUSIVE
            else [],
            governance_failures=governance_failures,
            claim_boundary_report=claim_boundary,
            is_diagnostic=False,
        )

    return plan, packet, failure_packet, evidence_status


def _evaluate_single_request(
    req: dict[str, Any],
    cfg: ReadoutDiagnosticsSensitivityRuntimeConfig,
) -> ReadoutDiagnosticsSensitivityRuntimeSingleReport:
    design_id = str(req.get("design_id") or "design_unspecified")
    execution_status = str(req.get("execution_status") or EVIDENCE_NOT_EVALUATED)
    execution_artifacts = _to_dict(req.get("execution_artifacts"))
    instrument_results = _as_list_of_dict(req.get("instrument_execution_results"))
    diagnostic_requirements = _as_list_of_dict(req.get("diagnostic_requirements"))
    sensitivity_requirements = _as_list_of_dict(req.get("sensitivity_requirements"))
    diagnostic_results = _as_list_of_dict(req.get("diagnostic_results"))
    sensitivity_results = _as_list_of_dict(req.get("sensitivity_results"))
    claim_scope = _to_dict(req.get("claim_scope"))
    production_governance_config = _to_dict(req.get("production_governance_config"))

    warnings: list[str] = []
    blocking_reasons: list[str] = []
    issues: list[ReadoutDiagnosticsSensitivityRuntimeIssue] = []

    execution_artifact_id = str(
        execution_artifacts.get("execution_id")
        or execution_artifacts.get("artifact_id")
        or f"execution::{design_id}"
    )

    claim_boundary = {
        "diagnostics_sensitivity_runtime_implemented": True,
        "diagnostic_plans_generated": True,
        "sensitivity_plans_generated": True,
        "diagnostic_evidence_packets_generated": True,
        "sensitivity_evidence_packets_generated": True,
        "evidence_sufficiency_evaluated": True,
        "failure_packets_generated": False,
        **_AUTH_FALSE_FLAGS,
    }

    evidence_statuses: list[str] = []

    if not execution_artifacts and cfg.require_execution_completed:
        evidence_statuses.append(EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED)
        blocking_reasons.append("execution artifacts missing")
    elif cfg.require_execution_completed and not _execution_completed(
        execution_status, execution_artifacts, instrument_results
    ):
        evidence_statuses.append(EVIDENCE_INSUFFICIENT_EXECUTION_NOT_COMPLETED)
        blocking_reasons.append("execution not completed")

    if _token(production_governance_config.get("status")) in ("BLOCKED", "UNRESOLVED"):
        evidence_statuses.append(EVIDENCE_BLOCKED_BY_GOVERNANCE)
        blocking_reasons.append("production governance restrictions unresolved")

    if cfg.block_on_missing_diagnostic_requirements and not diagnostic_requirements:
        evidence_statuses.append(EVIDENCE_INSUFFICIENT_MISSING_DIAGNOSTICS)
        blocking_reasons.append("diagnostic requirements missing")

    if cfg.block_on_missing_sensitivity_requirements and not sensitivity_requirements:
        evidence_statuses.append(EVIDENCE_INSUFFICIENT_MISSING_SENSITIVITY)
        blocking_reasons.append("sensitivity requirements missing")

    diag_result_index = _result_index(diagnostic_results, "requirement_id")
    sens_result_index = _result_index(sensitivity_results, "requirement_id")

    diagnostic_plans: list[dict[str, Any]] = []
    sensitivity_plans: list[dict[str, Any]] = []
    diagnostic_packets: list[dict[str, Any]] = []
    sensitivity_packets: list[dict[str, Any]] = []
    diagnostic_failures: list[dict[str, Any]] = []
    sensitivity_failures: list[dict[str, Any]] = []
    governed_diagnostic_computed = False

    for req_row in diagnostic_requirements:
        requirement_id = str(req_row.get("requirement_id") or "")
        provided_result = diag_result_index.get(requirement_id)
        computed_result = _maybe_compute_governed_did_diagnostic(
            req_row,
            req=req,
            execution_artifacts=execution_artifacts,
            execution_artifact_id=execution_artifact_id,
            cfg=cfg,
        )
        if computed_result is not None:
            provided_result = computed_result
            governed_diagnostic_computed = True
        plan, packet, failure, status = _evaluate_diagnostic_requirement(
            req_row,
            design_id=design_id,
            execution_artifact_id=execution_artifact_id,
            provided_result=provided_result,
            claim_scope=claim_scope,
            cfg=cfg,
            claim_boundary=claim_boundary,
        )
        if computed_result is not None:
            plan = {
                **plan,
                "planned_execution_mode": "governed_diagnostic",
                "planned_status": computed_result.get("result_status", plan["planned_status"]),
            }
        diagnostic_plans.append(plan)
        diagnostic_packets.append(packet)
        evidence_statuses.append(status)
        warnings.extend(packet.get("warnings", []))
        if failure:
            diagnostic_failures.append(failure)

    for req_row in sensitivity_requirements:
        plan, packet, failure, status = _evaluate_sensitivity_requirement(
            req_row,
            design_id=design_id,
            execution_artifact_id=execution_artifact_id,
            provided_result=sens_result_index.get(str(req_row.get("requirement_id") or "")),
            claim_scope=claim_scope,
            cfg=cfg,
            claim_boundary=claim_boundary,
        )
        sensitivity_plans.append(plan)
        sensitivity_packets.append(packet)
        evidence_statuses.append(status)
        warnings.extend(packet.get("warnings", []))
        if failure:
            sensitivity_failures.append(failure)

    if evidence_statuses:
        evidence_sufficiency_status = min(
            evidence_statuses, key=lambda x: _EVIDENCE_PRIORITY.get(x, 99)
        )
        if (
            evidence_sufficiency_status == EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW
            and any(w for w in warnings)
        ):
            evidence_sufficiency_status = EVIDENCE_SUFFICIENT_WITH_WARNINGS
    else:
        evidence_sufficiency_status = EVIDENCE_NOT_EVALUATED

    claim_boundary = {
        **claim_boundary,
        "failure_packets_generated": bool(diagnostic_failures or sensitivity_failures),
        "first_governed_diagnostic_implemented": bool(cfg.enable_governed_did_coverage_diagnostic),
        "did_coverage_diagnostic_implemented": bool(cfg.enable_governed_did_coverage_diagnostic),
        "did_coverage_diagnostic_runtime_integrated": bool(cfg.enable_governed_did_coverage_diagnostic),
        "diagnostic_result_computed": governed_diagnostic_computed,
        "diagnostic_pass_fail_computed": governed_diagnostic_computed,
    }

    evidence_aggregation_report = {
        "design_id": design_id,
        "execution_artifact_id": execution_artifact_id,
        "diagnostic_requirement_count": len(diagnostic_requirements),
        "sensitivity_requirement_count": len(sensitivity_requirements),
        "diagnostic_plan_count": len(diagnostic_plans),
        "sensitivity_plan_count": len(sensitivity_plans),
        "diagnostic_evidence_packet_count": len(diagnostic_packets),
        "sensitivity_evidence_packet_count": len(sensitivity_packets),
        "diagnostic_failure_packet_count": len(diagnostic_failures),
        "sensitivity_failure_packet_count": len(sensitivity_failures),
        "evidence_status_counts": {
            status: evidence_statuses.count(status) for status in sorted(set(evidence_statuses))
        },
    }

    evidence_sufficiency_report = {
        "design_id": design_id,
        "evidence_sufficiency_status": evidence_sufficiency_status,
        "claim_review_eligible": evidence_sufficiency_status
        in (
            EVIDENCE_SUFFICIENT_FOR_CLAIM_REVIEW,
            EVIDENCE_SUFFICIENT_WITH_WARNINGS,
            EVIDENCE_PROVISIONAL,
        ),
        "claim_authorized": False,
        "production_readout_authorized": False,
        "blocking_reasons": list(_safe_str_list(blocking_reasons)),
        "warnings": list(_safe_str_list(warnings)),
    }

    return ReadoutDiagnosticsSensitivityRuntimeSingleReport(
        artifact_id=_ARTIFACT_ID,
        design_id=design_id,
        evidence_sufficiency_status=evidence_sufficiency_status,
        diagnostic_plans=tuple(diagnostic_plans),
        sensitivity_plans=tuple(sensitivity_plans),
        diagnostic_evidence_packets=tuple(diagnostic_packets),
        sensitivity_evidence_packets=tuple(sensitivity_packets),
        diagnostic_failure_packets=tuple(diagnostic_failures),
        sensitivity_failure_packets=tuple(sensitivity_failures),
        evidence_aggregation_report=evidence_aggregation_report,
        evidence_sufficiency_report=evidence_sufficiency_report,
        claim_boundary_report=claim_boundary,
        warnings=_safe_str_list(warnings),
        blocking_reasons=_safe_str_list(blocking_reasons),
        issues=tuple(issues),
    )


def evaluate_readout_diagnostics_sensitivity(
    input_data: Any,
    config: ReadoutDiagnosticsSensitivityRuntimeConfig | None = None,
) -> ReadoutDiagnosticsSensitivityRuntimeReport:
    """Evaluate diagnostic/sensitivity evidence planning and sufficiency without executing checks."""
    cfg = config or ReadoutDiagnosticsSensitivityRuntimeConfig()
    requests = _normalize_requests(input_data)
    reports = [_evaluate_single_request(r, cfg) for r in requests]

    if len(reports) == 1:
        r = reports[0]
        return ReadoutDiagnosticsSensitivityRuntimeReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            evidence_sufficiency_status=r.evidence_sufficiency_status,
            diagnostic_plans=r.diagnostic_plans,
            sensitivity_plans=r.sensitivity_plans,
            diagnostic_evidence_packets=r.diagnostic_evidence_packets,
            sensitivity_evidence_packets=r.sensitivity_evidence_packets,
            diagnostic_failure_packets=r.diagnostic_failure_packets,
            sensitivity_failure_packets=r.sensitivity_failure_packets,
            evidence_aggregation_report=r.evidence_aggregation_report,
            evidence_sufficiency_report=r.evidence_sufficiency_report,
            claim_boundary_report=r.claim_boundary_report,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
            issues=r.issues,
            design_reports=(r,),
        )

    all_warnings: list[str] = []
    all_blocking: list[str] = []
    all_issues: list[ReadoutDiagnosticsSensitivityRuntimeIssue] = []
    for r in reports:
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)
        all_issues.extend(r.issues)

    return ReadoutDiagnosticsSensitivityRuntimeReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        evidence_sufficiency_status=None,
        diagnostic_plans=(),
        sensitivity_plans=(),
        diagnostic_evidence_packets=(),
        sensitivity_evidence_packets=(),
        diagnostic_failure_packets=(),
        sensitivity_failure_packets=(),
        evidence_aggregation_report={},
        evidence_sufficiency_report={},
        claim_boundary_report={
            "diagnostics_sensitivity_runtime_implemented": True,
            "diagnostic_plans_generated": True,
            "sensitivity_plans_generated": True,
            "diagnostic_evidence_packets_generated": True,
            "sensitivity_evidence_packets_generated": True,
            "evidence_sufficiency_evaluated": True,
            "failure_packets_generated": True,
            **_AUTH_FALSE_FLAGS,
        },
        warnings=_safe_str_list(all_warnings),
        blocking_reasons=_safe_str_list(all_blocking),
        issues=tuple(all_issues),
        design_reports=tuple(reports),
        aggregate_summary=f"Evaluated {len(reports)} evidence requests without ranking",
    )


evaluate_diagnostics_sensitivity_evidence = evaluate_readout_diagnostics_sensitivity


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    smoke = {
        "design_id": "design_evidence_smoke",
        "execution_status": "INSTRUMENT_EXECUTION_COMPLETED",
        "execution_artifacts": {"execution_id": "execution_smoke", "execution_completed": True},
        "instrument_execution_results": [
            {"instrument_id": "DID_BOOTSTRAP", "instrument_execution_status": "INSTRUMENT_EXECUTION_COMPLETED"}
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
    report = evaluate_readout_diagnostics_sensitivity(smoke)
    failed: list[str] = []
    if not report.claim_boundary_report["diagnostics_sensitivity_runtime_implemented"]:
        failed.append("runtime_not_implemented_flag")
    if report.claim_boundary_report["diagnostic_check_executed"]:
        failed.append("diagnostic_check_executed_flag_violation")
    if not report.diagnostic_plans:
        failed.append("missing_diagnostic_plans")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "readout_diagnostics_sensitivity_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": SCOPE,
        "depends_on": list(DEPENDS_ON),
        "public_api": "evaluate_readout_diagnostics_sensitivity",
        "diagnostics_sensitivity_runtime_implemented": True,
        "diagnostic_plans_generated": True,
        "sensitivity_plans_generated": True,
        "diagnostic_evidence_packets_generated": True,
        "sensitivity_evidence_packets_generated": True,
        "evidence_sufficiency_evaluated": True,
        "failure_packets_generated": bool(
            report.diagnostic_failure_packets or report.sensitivity_failure_packets
        ),
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
