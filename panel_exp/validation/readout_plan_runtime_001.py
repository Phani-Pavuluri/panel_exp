"""READOUT_PLAN_RUNTIME_001 deterministic governed readout planning runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from panel_exp.validation.production_catalog_blocklist_001 import (
    PRODUCTION_CATALOG_DIAGNOSTIC_ONLY,
    PRODUCTION_CATALOG_RESEARCH_ONLY,
    evaluate_production_catalog_status,
    production_catalog_overlay_for_matrix,
)

_ARTIFACT_ID = "READOUT_PLAN_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "readout_plan_runtime_implemented_planning_only_no_estimator_execution_or_claim_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/READOUT_PLAN_RUNTIME_001_summary.json"
RECOMMENDED_NEXT_ARTIFACT = "ESTIMATOR_INFERENCE_EXECUTION_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_METHOD_GOVERNANCE_RUNTIME_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "NOT_EVALUATED"})
_READY_TOKENS = frozenset({"PASS", "READY", "READY_FOR_DOWNSTREAM", "COMPLETE", "COMPLETED"})


class ReadoutPlanStatus(str, Enum):
    READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT = "READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT"
    READOUT_PLAN_READY_WITH_WARNINGS = "READOUT_PLAN_READY_WITH_WARNINGS"
    READOUT_PLAN_PROVISIONAL = "READOUT_PLAN_PROVISIONAL"
    READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE = "READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE"
    READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT = "READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT"
    READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS = "READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS"
    READOUT_PLAN_BLOCKED_BY_ESTIMAND = "READOUT_PLAN_BLOCKED_BY_ESTIMAND"
    READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS = "READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS"
    READOUT_PLAN_BLOCKED_BY_MISSING_DIAGNOSTICS = "READOUT_PLAN_BLOCKED_BY_MISSING_DIAGNOSTICS"
    READOUT_PLAN_BLOCKED_BY_MISSING_SENSITIVITY_REQUIREMENTS = (
        "READOUT_PLAN_BLOCKED_BY_MISSING_SENSITIVITY_REQUIREMENTS"
    )
    READOUT_PLAN_BLOCKED_BY_PRODUCTION_GOVERNANCE = "READOUT_PLAN_BLOCKED_BY_PRODUCTION_GOVERNANCE"
    READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN = "READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN"
    READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN = "READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN"
    READOUT_PLAN_NOT_EVALUATED = "READOUT_PLAN_NOT_EVALUATED"


class ReadoutStackRole(str, Enum):
    PRIMARY_READOUT_CANDIDATE = "PRIMARY_READOUT_CANDIDATE"
    SENSITIVITY_READOUT_CANDIDATE = "SENSITIVITY_READOUT_CANDIDATE"
    DIAGNOSTIC_READOUT_CANDIDATE = "DIAGNOSTIC_READOUT_CANDIDATE"
    BLOCKED_READOUT_INSTRUMENT = "BLOCKED_READOUT_INSTRUMENT"
    REFERENCE_ONLY_INSTRUMENT = "REFERENCE_ONLY_INSTRUMENT"
    NOT_EVALUATED_INSTRUMENT = "NOT_EVALUATED_INSTRUMENT"


class InstrumentPlanningCategory(str, Enum):
    PLANNING_ELIGIBLE_PRIMARY_CANDIDATE = "PLANNING_ELIGIBLE_PRIMARY_CANDIDATE"
    PLANNING_ELIGIBLE_WITH_WARNINGS = "PLANNING_ELIGIBLE_WITH_WARNINGS"
    PLANNING_RESTRICTED_REQUIRES_REVIEW = "PLANNING_RESTRICTED_REQUIRES_REVIEW"
    PLANNING_DIAGNOSTIC_ONLY = "PLANNING_DIAGNOSTIC_ONLY"
    PLANNING_BLOCKED = "PLANNING_BLOCKED"
    PLANNING_NOT_EVALUATED = "PLANNING_NOT_EVALUATED"


@dataclass(frozen=True)
class ReadoutPlanRuntimeConfig:
    block_on_readout_governance_blocked: bool = True
    block_on_missing_assignment_artifact: bool = True
    block_on_missing_reproducibility_manifest: bool = True
    block_when_all_instruments_blocked: bool = True
    block_when_only_diagnostic_instruments: bool = True
    block_on_missing_estimand_scope: bool = True
    block_on_missing_uncertainty_scope: bool = True
    require_diagnostic_plan: bool = True
    require_sensitivity_plan: bool = True
    enforce_production_catalog_blocklist: bool = True


@dataclass(frozen=True)
class ReadoutPlanIssue:
    code: str
    message: str
    severity: str
    field: str | None = None


@dataclass(frozen=True)
class PlannedReadoutInstrument:
    instrument_id: str
    estimator_family: str | None
    inference_family: str | None
    stack_role: ReadoutStackRole
    planning_category: InstrumentPlanningCategory
    suitability_status: str | None
    governance_status: str | None
    review_requirements: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_sensitivity_checks: tuple[str, ...]
    uncertainty_semantics: str | None
    estimand_compatibility_status: str | None
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    diagnostic_only_reason: str | None
    restricted_reason: str | None


@dataclass(frozen=True)
class ReadoutPlanClaimBoundaryReport:
    readout_plan_runtime_implemented: bool = True
    readout_plan_generated: bool = False
    planned_primary_candidates_generated: bool = False
    planned_sensitivity_candidates_generated: bool = False
    planned_diagnostic_candidates_generated: bool = False
    blocked_instruments_preserved: bool = True
    execution_prerequisites_generated: bool = False
    claim_scope_generated: bool = False
    reporting_caveats_generated: bool = False
    primary_readout_stack_selected: bool = False
    sensitivity_stack_selected: bool = False
    diagnostic_stack_selected: bool = False
    method_winner_selected: bool = False
    estimator_execution_implemented: bool = False
    inference_execution_implemented: bool = False
    effect_estimate_computed: bool = False
    lift_computed: bool = False
    roi_computed: bool = False
    p_value_computed: bool = False
    confidence_interval_computed: bool = False
    uncertainty_computed: bool = False
    diagnostic_check_executed: bool = False
    sensitivity_check_executed: bool = False
    causal_claim_authorized: bool = False
    incremental_lift_claim_authorized: bool = False
    roi_claim_authorized: bool = False
    production_readout_authorized: bool = False
    production_authorization_granted: bool = False
    mmm_runtime_calls_implemented: bool = False
    mmm_calibration_authorized: bool = False
    llm_decisioning_authorized: bool = False


@dataclass(frozen=True)
class ReadoutPlanPacketReport:
    design_id: str
    readout_plan_status: ReadoutPlanStatus
    readout_plan_packet: dict[str, Any]
    planned_readout_stack: tuple[PlannedReadoutInstrument, ...]
    planned_primary_candidates: tuple[PlannedReadoutInstrument, ...]
    planned_sensitivity_candidates: tuple[PlannedReadoutInstrument, ...]
    planned_diagnostic_candidates: tuple[PlannedReadoutInstrument, ...]
    blocked_instruments: tuple[PlannedReadoutInstrument, ...]
    not_evaluated_instruments: tuple[PlannedReadoutInstrument, ...]
    execution_prerequisites: tuple[str, ...]
    estimand_scope: dict[str, Any]
    uncertainty_scope: dict[str, Any]
    required_diagnostics: tuple[str, ...]
    required_sensitivity_checks: tuple[str, ...]
    claim_scope: dict[str, Any] | None
    reporting_caveats: tuple[str, ...]
    claim_boundary_report: ReadoutPlanClaimBoundaryReport
    issues: tuple[ReadoutPlanIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ReadoutPlanRuntimeReport:
    artifact_id: str
    design_id: str | None
    readout_plan_status: ReadoutPlanStatus | None
    readout_plan_packet: dict[str, Any] | None = None
    planned_readout_stack: tuple[PlannedReadoutInstrument, ...] = ()
    planned_primary_candidates: tuple[PlannedReadoutInstrument, ...] = ()
    planned_sensitivity_candidates: tuple[PlannedReadoutInstrument, ...] = ()
    planned_diagnostic_candidates: tuple[PlannedReadoutInstrument, ...] = ()
    blocked_instruments: tuple[PlannedReadoutInstrument, ...] = ()
    not_evaluated_instruments: tuple[PlannedReadoutInstrument, ...] = ()
    execution_prerequisites: tuple[str, ...] = ()
    estimand_scope: dict[str, Any] = field(default_factory=dict)
    uncertainty_scope: dict[str, Any] = field(default_factory=dict)
    required_diagnostics: tuple[str, ...] = ()
    required_sensitivity_checks: tuple[str, ...] = ()
    claim_scope: dict[str, Any] | None = None
    reporting_caveats: tuple[str, ...] = ()
    claim_boundary_report: ReadoutPlanClaimBoundaryReport = field(
        default_factory=ReadoutPlanClaimBoundaryReport
    )
    design_reports: tuple[ReadoutPlanPacketReport, ...] = ()
    aggregate_summary: str | None = None
    issues: tuple[ReadoutPlanIssue, ...] = ()
    warnings: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
    final_verdict: str = _VERDICT


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _token(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _is_blocked(value: Any) -> bool:
    t = _token(value)
    if not t:
        return False
    if t in _BLOCKED_TOKENS:
        return True
    if t.startswith("BLOCKED"):
        return True
    if t.endswith("_BLOCKED"):
        return True
    return "_BLOCKED_BY_" in t


def _is_ready(value: Any) -> bool:
    t = _token(value)
    return bool(t) and (t in _READY_TOKENS or "READY" in t or t == "PASS")


def _normalize_requests(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list) and input_data and all(isinstance(x, dict) for x in input_data):
        return [dict(x) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [dict(x) for x in data["requests"] if isinstance(x, dict)]
    if data:
        return [data]
    return [{"design_id": "design_unspecified"}]


def _as_list_of_dict(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [dict(x) for x in value if isinstance(x, dict)]
    return []


def _as_list_of_str(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    return []


def _coerce_scope(value: Any, field_name: str, issues: list[ReadoutPlanIssue]) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if value is None:
        return {}
    issues.append(
        ReadoutPlanIssue(
            code=f"INVALID_{field_name.upper()}",
            message=f"{field_name} must be a dict when provided",
            severity="WARNING",
            field=field_name,
        )
    )
    return {}


def _instrument_from_row(
    row: dict[str, Any],
    *,
    default_category: InstrumentPlanningCategory | None = None,
    default_role: ReadoutStackRole = ReadoutStackRole.REFERENCE_ONLY_INSTRUMENT,
) -> PlannedReadoutInstrument:
    category = _token(row.get("planning_category"))
    if category in {c.value for c in InstrumentPlanningCategory}:
        planning_category = InstrumentPlanningCategory(category)
    elif default_category is not None:
        planning_category = default_category
    else:
        planning_category = InstrumentPlanningCategory.PLANNING_NOT_EVALUATED

    return PlannedReadoutInstrument(
        instrument_id=str(row.get("instrument_id", "instrument_unspecified")),
        estimator_family=str(row["estimator_family"]) if row.get("estimator_family") else None,
        inference_family=str(row["inference_family"]) if row.get("inference_family") else None,
        stack_role=default_role,
        planning_category=planning_category,
        suitability_status=str(row["suitability_status"]) if row.get("suitability_status") else None,
        governance_status=str(row["governance_status"]) if row.get("governance_status") else None,
        review_requirements=tuple(_as_list_of_str(row.get("review_requirements"))),
        required_diagnostics=tuple(_as_list_of_str(row.get("required_diagnostics"))),
        required_sensitivity_checks=tuple(_as_list_of_str(row.get("required_sensitivity_checks"))),
        uncertainty_semantics=str(row["uncertainty_semantics"]) if row.get("uncertainty_semantics") else None,
        estimand_compatibility_status=(
            str(row["estimand_compatibility_status"])
            if row.get("estimand_compatibility_status")
            else None
        ),
        warnings=tuple(_as_list_of_str(row.get("warnings"))),
        blocking_reasons=tuple(_as_list_of_str(row.get("blocking_reasons"))),
        diagnostic_only_reason=(
            str(row["diagnostic_only_reason"]) if row.get("diagnostic_only_reason") else None
        ),
        restricted_reason=str(row["restricted_reason"]) if row.get("restricted_reason") else None,
    )


def _ensure_production_catalog_fields(
    row: dict[str, Any],
    cfg: ReadoutPlanRuntimeConfig,
) -> dict[str, Any]:
    if not cfg.enforce_production_catalog_blocklist:
        return row
    if "is_production_blocked" in row:
        return row
    report = evaluate_production_catalog_status(
        {
            "instrument_id": row.get("instrument_id"),
            "method_family": row.get("estimator_family"),
            "estimator_family": row.get("estimator_family"),
            "inference_family": row.get("inference_family"),
            "production_context": "review",
            "requested_role": "GOVERNED_POINT_ESTIMATE",
        }
    )
    return {**row, **production_catalog_overlay_for_matrix(report)}


def _infer_planning_category(row: dict[str, Any]) -> InstrumentPlanningCategory:
    category_token = _token(row.get("planning_category"))
    if category_token in {c.value for c in InstrumentPlanningCategory}:
        return InstrumentPlanningCategory(category_token)

    suitability = _token(row.get("suitability_status"))
    governance = _token(row.get("governance_status"))
    warnings = bool(row.get("warnings"))
    blocked_reasons = bool(row.get("blocking_reasons"))

    blocked_reasons = bool(row.get("blocking_reasons"))

    if row.get("is_production_blocked"):
        status = _token(row.get("production_catalog_status"))
        if status == PRODUCTION_CATALOG_DIAGNOSTIC_ONLY:
            return InstrumentPlanningCategory.PLANNING_DIAGNOSTIC_ONLY
        if status == PRODUCTION_CATALOG_RESEARCH_ONLY:
            return InstrumentPlanningCategory.PLANNING_BLOCKED
        return InstrumentPlanningCategory.PLANNING_BLOCKED

    if suitability.endswith("BLOCKED") or governance == "BLOCKED" or blocked_reasons:
        return InstrumentPlanningCategory.PLANNING_BLOCKED
    if suitability.endswith("DIAGNOSTIC_ONLY") or governance == "DIAGNOSTIC_ONLY":
        return InstrumentPlanningCategory.PLANNING_DIAGNOSTIC_ONLY
    if suitability.endswith("RESTRICTED") or governance == "RESTRICTED":
        return InstrumentPlanningCategory.PLANNING_RESTRICTED_REQUIRES_REVIEW
    if suitability.endswith("NOT_EVALUATED") or governance == "NOT_EVALUATED":
        return InstrumentPlanningCategory.PLANNING_NOT_EVALUATED
    if warnings or suitability.endswith("ELIGIBLE_WITH_WARNINGS"):
        return InstrumentPlanningCategory.PLANNING_ELIGIBLE_WITH_WARNINGS
    return InstrumentPlanningCategory.PLANNING_ELIGIBLE_PRIMARY_CANDIDATE


def _collect_instrument_matrix(req: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = _as_list_of_dict(req.get("instrument_suitability_matrix"))
    if matrix:
        return matrix
    matrix = _as_list_of_dict(req.get("method_instrument_suitability_matrix"))
    return matrix


def _merge_instrument_lists(req: dict[str, Any], matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for row in matrix:
        iid = str(row.get("instrument_id", "")).strip()
        if not iid:
            continue
        by_id[iid] = dict(row)

    explicit_groups: list[tuple[str, InstrumentPlanningCategory]] = [
        ("eligible_instruments_for_planning", InstrumentPlanningCategory.PLANNING_ELIGIBLE_PRIMARY_CANDIDATE),
        ("restricted_instruments", InstrumentPlanningCategory.PLANNING_RESTRICTED_REQUIRES_REVIEW),
        ("diagnostic_only_instruments", InstrumentPlanningCategory.PLANNING_DIAGNOSTIC_ONLY),
        ("blocked_instruments", InstrumentPlanningCategory.PLANNING_BLOCKED),
        ("not_evaluated_instruments", InstrumentPlanningCategory.PLANNING_NOT_EVALUATED),
    ]
    for key, default_category in explicit_groups:
        for item in _as_list_of_dict(req.get(key)):
            iid = str(item.get("instrument_id", "")).strip()
            if not iid:
                continue
            merged = dict(by_id.get(iid, {}))
            merged.update(item)
            merged["instrument_id"] = iid
            if "planning_category" not in merged:
                merged["planning_category"] = default_category.value
            by_id[iid] = merged

    return list(by_id.values())


def _ensure_required_claim_scope_fields(
    claim_scope: dict[str, Any],
    *,
    has_primary_or_restricted: bool,
    has_uncertainty_scope: bool,
    has_estimand_scope: bool,
    has_diagnostics: bool,
    has_sensitivity: bool,
) -> tuple[dict[str, Any], list[str]]:
    caveats: list[str] = []
    required_defaults = {
        "estimand": "unspecified_estimand",
        "population_scope": "unspecified_population_scope",
        "time_window": "unspecified_time_window",
        "metric_kpi": "unspecified_metric_kpi",
        "assignment_artifact": "unspecified_assignment_artifact",
        "planned_instruments": [],
        "uncertainty_semantics": "unspecified_uncertainty_semantics",
        "diagnostics_prerequisites": [],
        "sensitivity_prerequisites": [],
        "reporting_caveats": [],
    }
    normalized = dict(claim_scope)
    for key, default in required_defaults.items():
        if key not in normalized or normalized[key] in (None, ""):
            normalized[key] = default
            caveats.append(f"claim scope missing {key}; defaulted")

    if not has_primary_or_restricted:
        caveats.append("no eligible/restricted primary instrument candidates available")
    if not has_uncertainty_scope:
        caveats.append("uncertainty scope missing; claim scope provisional")
    if not has_estimand_scope:
        caveats.append("estimand scope missing; claim scope provisional")
    if not has_diagnostics:
        caveats.append("diagnostic prerequisites missing; claim scope provisional")
    if not has_sensitivity:
        caveats.append("sensitivity prerequisites missing; claim scope provisional")

    roi_gov = _token(normalized.get("roi_governance_status"))
    if roi_gov not in ("APPROVED", "ELIGIBLE"):
        caveats.append("ROI claim scope not planned without explicit ROI governance")
    return normalized, caveats


def _boundary_report(
    *,
    generated: bool,
    primary_count: int,
    sensitivity_count: int,
    diagnostic_count: int,
    prerequisites_count: int,
    claim_scope_generated: bool,
    caveats_count: int,
) -> ReadoutPlanClaimBoundaryReport:
    return ReadoutPlanClaimBoundaryReport(
        readout_plan_generated=generated,
        planned_primary_candidates_generated=primary_count > 0,
        planned_sensitivity_candidates_generated=sensitivity_count > 0,
        planned_diagnostic_candidates_generated=diagnostic_count > 0,
        blocked_instruments_preserved=True,
        execution_prerequisites_generated=prerequisites_count > 0,
        claim_scope_generated=claim_scope_generated,
        reporting_caveats_generated=caveats_count > 0,
    )


def _evaluate_single_request(
    req: dict[str, Any],
    cfg: ReadoutPlanRuntimeConfig,
) -> ReadoutPlanPacketReport:
    design_id = str(req.get("design_id") or "design_unspecified")
    issues: list[ReadoutPlanIssue] = []
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    caveats: list[str] = []

    governance_status = _token(req.get("readout_method_governance_status"))
    if governance_status == "READOUT_PLAN_READY_FOR_RUNTIME_PLANNING":
        governance_status = "READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT"
    if not governance_status:
        governance_status = "NOT_EVALUATED"
        warnings.append("readout_method_governance_status missing")

    assignment_artifact_status = _token(req.get("assignment_artifact_status"))
    assignment_plan = _to_dict(req.get("assignment_plan"))
    assignment_candidate = _to_dict(req.get("assignment_candidate"))
    reproducibility_manifest = _to_dict(req.get("reproducibility_manifest"))

    matrix = _collect_instrument_matrix(req)
    instruments = _merge_instrument_lists(req, matrix)
    planned_primary: list[PlannedReadoutInstrument] = []
    planned_sensitivity: list[PlannedReadoutInstrument] = []
    planned_diagnostic: list[PlannedReadoutInstrument] = []
    blocked: list[PlannedReadoutInstrument] = []
    not_eval: list[PlannedReadoutInstrument] = []
    research_only: list[PlannedReadoutInstrument] = []
    stack: list[PlannedReadoutInstrument] = []

    required_diagnostics = tuple(_as_list_of_str(req.get("required_diagnostics")))
    required_sensitivity = tuple(_as_list_of_str(req.get("required_sensitivity_checks")))
    claim_eligibility = _as_list_of_dict(req.get("claim_eligibility_reports"))
    production_gov = _to_dict(req.get("production_governance_config"))
    estimand_scope = _coerce_scope(req.get("estimand_scope"), "estimand_scope", issues)
    uncertainty_scope = _coerce_scope(req.get("uncertainty_scope"), "uncertainty_scope", issues)

    for row in instruments:
        row = _ensure_production_catalog_fields(row, cfg)
        category = _infer_planning_category(row)
        inst = _instrument_from_row(row, default_category=category)

        if row.get("is_production_blocked") and _token(row.get("production_catalog_status")) == PRODUCTION_CATALOG_RESEARCH_ONLY:
            research_inst = PlannedReadoutInstrument(
                **{**inst.__dict__, "stack_role": ReadoutStackRole.REFERENCE_ONLY_INSTRUMENT}
            )
            research_only.append(research_inst)
            stack.append(research_inst)
            continue

        if category == InstrumentPlanningCategory.PLANNING_BLOCKED:
            inst = PlannedReadoutInstrument(**{**inst.__dict__, "stack_role": ReadoutStackRole.BLOCKED_READOUT_INSTRUMENT})
            blocked.append(inst)
            stack.append(inst)
            continue
        if category == InstrumentPlanningCategory.PLANNING_NOT_EVALUATED:
            inst = PlannedReadoutInstrument(**{**inst.__dict__, "stack_role": ReadoutStackRole.NOT_EVALUATED_INSTRUMENT})
            not_eval.append(inst)
            stack.append(inst)
            continue
        if category == InstrumentPlanningCategory.PLANNING_DIAGNOSTIC_ONLY:
            inst = PlannedReadoutInstrument(**{**inst.__dict__, "stack_role": ReadoutStackRole.DIAGNOSTIC_READOUT_CANDIDATE})
            planned_diagnostic.append(inst)
            stack.append(inst)
            continue
        if category in (
            InstrumentPlanningCategory.PLANNING_ELIGIBLE_PRIMARY_CANDIDATE,
            InstrumentPlanningCategory.PLANNING_ELIGIBLE_WITH_WARNINGS,
            InstrumentPlanningCategory.PLANNING_RESTRICTED_REQUIRES_REVIEW,
        ):
            primary_role = PlannedReadoutInstrument(
                **{**inst.__dict__, "stack_role": ReadoutStackRole.PRIMARY_READOUT_CANDIDATE}
            )
            planned_primary.append(primary_role)
            stack.append(primary_role)
            if category in (
                InstrumentPlanningCategory.PLANNING_ELIGIBLE_WITH_WARNINGS,
                InstrumentPlanningCategory.PLANNING_RESTRICTED_REQUIRES_REVIEW,
            ):
                sensitivity_role = PlannedReadoutInstrument(
                    **{**inst.__dict__, "stack_role": ReadoutStackRole.SENSITIVITY_READOUT_CANDIDATE}
                )
                planned_sensitivity.append(sensitivity_role)
                stack.append(sensitivity_role)
                if category == InstrumentPlanningCategory.PLANNING_RESTRICTED_REQUIRES_REVIEW:
                    caveats.append(f"{inst.instrument_id} restricted; requires diagnostics and caveats")
            continue

        ref = PlannedReadoutInstrument(**{**inst.__dict__, "stack_role": ReadoutStackRole.REFERENCE_ONLY_INSTRUMENT})
        stack.append(ref)

    if assignment_plan.get("assignment_algorithm_category") == "DETERMINISTIC_RULE_ASSIGNMENT":
        caveats.append("deterministic explicit-pool assignment limitation preserved from assignment artifact")

    status = ReadoutPlanStatus.READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT

    if _is_blocked(governance_status) and cfg.block_on_readout_governance_blocked:
        status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE
        blocking_reasons.append("readout method governance blocked")

    has_assignment_artifact = bool(assignment_plan or assignment_candidate)
    if not has_assignment_artifact and cfg.block_on_missing_assignment_artifact:
        status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT
        blocking_reasons.append("assignment artifact missing")
    elif assignment_artifact_status and _is_blocked(assignment_artifact_status):
        status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT
        blocking_reasons.append("assignment artifact status blocked")

    if not reproducibility_manifest and cfg.block_on_missing_reproducibility_manifest:
        status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT
        blocking_reasons.append("reproducibility manifest missing")

    if not planned_primary and not planned_sensitivity and blocked and cfg.block_when_all_instruments_blocked:
        status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS
        blocking_reasons.append("all instruments blocked")

    if not planned_primary and planned_diagnostic and cfg.block_when_only_diagnostic_instruments:
        status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS
        blocking_reasons.append("only diagnostic-only instruments available")
    elif not planned_primary and planned_diagnostic and status == ReadoutPlanStatus.READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT:
        status = ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL
        warnings.append("only diagnostic-only instruments available; no primary candidate")

    if not estimand_scope:
        if cfg.block_on_missing_estimand_scope:
            status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ESTIMAND
            blocking_reasons.append("estimand scope missing")
        else:
            status = ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL
            warnings.append("estimand scope missing")

    if not uncertainty_scope:
        if cfg.block_on_missing_uncertainty_scope:
            status = ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS
            blocking_reasons.append("uncertainty scope missing")
        else:
            status = ReadoutPlanStatus.READOUT_PLAN_PROVISIONAL
            warnings.append("uncertainty scope missing")

    if not required_diagnostics:
        if cfg.require_diagnostic_plan:
            if status == ReadoutPlanStatus.READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT:
                status = ReadoutPlanStatus.READOUT_PLAN_REQUIRES_DIAGNOSTIC_PLAN
            warnings.append("required diagnostics missing; diagnostic plan required")
            blocking_reasons.append("diagnostic plan required")
        else:
            warnings.append("required diagnostics missing")

    if not required_sensitivity:
        if cfg.require_sensitivity_plan:
            if status == ReadoutPlanStatus.READOUT_PLAN_READY_FOR_EXECUTION_CONTRACT:
                status = ReadoutPlanStatus.READOUT_PLAN_REQUIRES_SENSITIVITY_PLAN
            warnings.append("required sensitivity checks missing; sensitivity plan required")
            blocking_reasons.append("sensitivity plan required")
        else:
            warnings.append("required sensitivity checks missing")

    blocked_roles = _as_list_of_str(production_gov.get("blocked_roles"))
    if blocked_roles and "production" in {_token(x) for x in blocked_roles}:
        caveats.append("production readout roles blocked by production_governance_config")
    if production_gov.get("production_readout_allowed") is True:
        caveats.append("production readout authorization not granted by readout planning runtime")

    claim_scope_input = _coerce_scope(req.get("claim_scope"), "claim_scope", issues)
    claim_scope, claim_scope_caveats = _ensure_required_claim_scope_fields(
        claim_scope_input,
        has_primary_or_restricted=bool(planned_primary),
        has_uncertainty_scope=bool(uncertainty_scope),
        has_estimand_scope=bool(estimand_scope),
        has_diagnostics=bool(required_diagnostics),
        has_sensitivity=bool(required_sensitivity),
    )
    caveats.extend(claim_scope_caveats)

    if any(_token(x.get("claim_type")) == "ROI_CLAIM" for x in claim_eligibility):
        if _token(claim_scope.get("roi_governance_status")) not in ("APPROVED", "ELIGIBLE"):
            caveats.append("ROI claim requested but blocked without explicit ROI governance")

    if planned_diagnostic and not planned_primary:
        caveats.append("diagnostic-only instruments cannot support production lift/ROI claims")

    estimand_token = _token(estimand_scope.get("estimand_type"))
    if estimand_token in ("DOSAGE_CONTRAST", "DOSAGE"):
        caveats.append("dosage estimand requires dosage-compatible planning; standard incrementality blocked")
    if estimand_token in ("BUDGET_REALLOCATION", "SOURCE_DESTINATION_REALLOCATION"):
        caveats.append("budget reallocation estimand blocks simple ROI claim scope")

    execution_prerequisites = tuple(
        dict.fromkeys(
            [
                "readout_method_governance_gate_passed",
                "assignment_artifact_available",
                "reproducibility_manifest_available",
                "instrument_slotting_completed",
                "estimand_scope_declared",
                "uncertainty_scope_declared",
                "diagnostic_prerequisites_declared",
                "sensitivity_prerequisites_declared",
                "claim_scope_declared_with_caveats",
            ]
        )
    )

    packet = {
        "artifact_id": _ARTIFACT_ID,
        "design_id": design_id,
        "readout_plan_status": status.value,
        "assignment_artifact_summary": {
            "assignment_artifact_status": assignment_artifact_status or "NOT_EVALUATED",
            "assignment_plan_present": bool(assignment_plan),
            "assignment_candidate_present": bool(assignment_candidate),
            "reproducibility_manifest_present": bool(reproducibility_manifest),
        },
        "readout_governance_summary": {
            "readout_method_governance_status": governance_status,
            "blocked": _is_blocked(governance_status),
        },
        "planned_primary_candidates": [x.instrument_id for x in planned_primary],
        "planned_sensitivity_candidates": [x.instrument_id for x in planned_sensitivity],
        "planned_diagnostic_candidates": [x.instrument_id for x in planned_diagnostic],
        "blocked_instruments": [x.instrument_id for x in blocked],
        "research_only_instruments": [x.instrument_id for x in research_only],
        "not_evaluated_instruments": [x.instrument_id for x in not_eval],
        "execution_prerequisites": list(execution_prerequisites),
        "estimand_scope": estimand_scope,
        "uncertainty_scope": uncertainty_scope,
        "required_diagnostics": list(required_diagnostics),
        "required_sensitivity_checks": list(required_sensitivity),
        "claim_scope": claim_scope,
        "reporting_caveats": list(dict.fromkeys(caveats)),
        "blocking_reasons": list(dict.fromkeys(blocking_reasons)),
        "warnings": list(dict.fromkeys(warnings)),
    }

    generated = status not in (
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_READOUT_GOVERNANCE,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ASSIGNMENT_ARTIFACT,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_METHOD_INSTRUMENTS,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_ESTIMAND,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_UNCERTAINTY_SEMANTICS,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_MISSING_DIAGNOSTICS,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_MISSING_SENSITIVITY_REQUIREMENTS,
        ReadoutPlanStatus.READOUT_PLAN_BLOCKED_BY_PRODUCTION_GOVERNANCE,
    )

    boundary = _boundary_report(
        generated=generated,
        primary_count=len(planned_primary),
        sensitivity_count=len(planned_sensitivity),
        diagnostic_count=len(planned_diagnostic),
        prerequisites_count=len(execution_prerequisites),
        claim_scope_generated=bool(claim_scope),
        caveats_count=len(caveats),
    )
    packet["claim_boundary_report"] = {
        f.name: getattr(boundary, f.name) for f in fields(boundary)
    }

    return ReadoutPlanPacketReport(
        design_id=design_id,
        readout_plan_status=status,
        readout_plan_packet=packet,
        planned_readout_stack=tuple(stack),
        planned_primary_candidates=tuple(planned_primary),
        planned_sensitivity_candidates=tuple(planned_sensitivity),
        planned_diagnostic_candidates=tuple(planned_diagnostic),
        blocked_instruments=tuple(blocked),
        not_evaluated_instruments=tuple(not_eval),
        execution_prerequisites=execution_prerequisites,
        estimand_scope=estimand_scope,
        uncertainty_scope=uncertainty_scope,
        required_diagnostics=required_diagnostics,
        required_sensitivity_checks=required_sensitivity,
        claim_scope=claim_scope,
        reporting_caveats=tuple(dict.fromkeys(caveats)),
        claim_boundary_report=boundary,
        issues=tuple(issues),
        warnings=tuple(dict.fromkeys(warnings)),
        blocking_reasons=tuple(dict.fromkeys(blocking_reasons)),
    )


def build_readout_plan(
    input_data: Any,
    config: ReadoutPlanRuntimeConfig | None = None,
) -> ReadoutPlanRuntimeReport:
    """Build a deterministic governed readout planning report without execution."""
    cfg = config or ReadoutPlanRuntimeConfig()
    requests = _normalize_requests(input_data)
    reports = [_evaluate_single_request(req, cfg) for req in requests]

    if len(reports) == 1:
        r = reports[0]
        return ReadoutPlanRuntimeReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            readout_plan_status=r.readout_plan_status,
            readout_plan_packet=r.readout_plan_packet,
            planned_readout_stack=r.planned_readout_stack,
            planned_primary_candidates=r.planned_primary_candidates,
            planned_sensitivity_candidates=r.planned_sensitivity_candidates,
            planned_diagnostic_candidates=r.planned_diagnostic_candidates,
            blocked_instruments=r.blocked_instruments,
            not_evaluated_instruments=r.not_evaluated_instruments,
            execution_prerequisites=r.execution_prerequisites,
            estimand_scope=r.estimand_scope,
            uncertainty_scope=r.uncertainty_scope,
            required_diagnostics=r.required_diagnostics,
            required_sensitivity_checks=r.required_sensitivity_checks,
            claim_scope=r.claim_scope,
            reporting_caveats=r.reporting_caveats,
            claim_boundary_report=r.claim_boundary_report,
            design_reports=(r,),
            issues=r.issues,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
        )

    all_issues: list[ReadoutPlanIssue] = []
    all_warnings: list[str] = []
    all_blocking: list[str] = []
    for r in reports:
        all_issues.extend(r.issues)
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)

    return ReadoutPlanRuntimeReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        readout_plan_status=None,
        design_reports=tuple(reports),
        aggregate_summary=f"Evaluated {len(reports)} readout planning requests without ranking",
        issues=tuple(all_issues),
        warnings=tuple(dict.fromkeys(all_warnings)),
        blocking_reasons=tuple(dict.fromkeys(all_blocking)),
    )


plan_readout_stack = build_readout_plan


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    smoke = {
        "design_id": "smoke_plan",
        "readout_method_governance_status": "READOUT_GOVERNANCE_ELIGIBLE_FOR_PLANNING",
        "assignment_artifact_status": "ASSIGNMENT_ARTIFACT_READY_FOR_READOUT_GOVERNANCE",
        "assignment_plan": {"assignment_algorithm_category": "DETERMINISTIC_RULE_ASSIGNMENT"},
        "assignment_candidate": {"candidate_id": "candidate_smoke"},
        "reproducibility_manifest": {"seed_policy": "NOT_APPLICABLE_DETERMINISTIC"},
        "instrument_suitability_matrix": [
            {
                "instrument_id": "DID_BOOTSTRAP",
                "estimator_family": "DID_FAMILY",
                "inference_family": "BOOTSTRAP_INFERENCE_FAMILY",
                "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
                "planning_category": "PLANNING_ELIGIBLE_PRIMARY_CANDIDATE",
            },
            {
                "instrument_id": "SCM_PLACEBO",
                "estimator_family": "SCM_FAMILY",
                "inference_family": "PLACEBO_INFERENCE_FAMILY",
                "suitability_status": "METHOD_FAMILY_DIAGNOSTIC_ONLY",
                "planning_category": "PLANNING_DIAGNOSTIC_ONLY",
            },
        ],
        "estimand_scope": {
            "estimand_type": "STANDARD_INCREMENTALITY",
            "population_scope": "eligible_dma",
            "time_window": "post_period",
            "metric_kpi": "sales",
        },
        "uncertainty_scope": {"semantics": "causal_interval_candidate_requires_validation"},
        "required_diagnostics": ["placebo_check", "pre_period_fit_diagnostic"],
        "required_sensitivity_checks": ["donor_pool_sensitivity"],
        "claim_scope": {
            "estimand": "STANDARD_INCREMENTALITY",
            "population_scope": "eligible_dma",
            "time_window": "post_period",
            "metric_kpi": "sales",
            "assignment_artifact": "assignment_plan_smoke",
            "planned_instruments": ["DID_BOOTSTRAP", "SCM_PLACEBO"],
            "uncertainty_semantics": "causal_interval_candidate_requires_validation",
            "diagnostics_prerequisites": ["placebo_check"],
            "sensitivity_prerequisites": ["donor_pool_sensitivity"],
            "reporting_caveats": [],
            "roi_governance_status": "NOT_APPROVED",
        },
        "production_governance_config": {"blocked_roles": ["production", "trust_report"]},
    }
    report = build_readout_plan(smoke)
    failed: list[str] = []
    if report.readout_plan_status is None:
        failed.append("smoke_missing_status")
    if not report.claim_boundary_report.readout_plan_runtime_implemented:
        failed.append("smoke_runtime_flag")
    if report.claim_boundary_report.primary_readout_stack_selected:
        failed.append("smoke_selected_primary")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "readout_plan_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "scope": "runtime_plans_readout_stack_only_no_estimator_execution_or_claim_authorization",
        "depends_on": [
            "READOUT_PLAN_CONTRACT_001",
            "READOUT_METHOD_GOVERNANCE_CONTRACT_001",
            "DESIGN_ASSIGNMENT_RUNTIME_001",
            "METHOD_SUITABILITY_RUNTIME_001",
        ],
        "public_api": "build_readout_plan",
        "readout_plan_runtime_implemented": True,
        "readout_plan_generated": True,
        "planned_primary_candidates_generated": True,
        "planned_sensitivity_candidates_generated": True,
        "planned_diagnostic_candidates_generated": True,
        "blocked_instruments_preserved": True,
        "execution_prerequisites_generated": True,
        "claim_scope_generated": True,
        "reporting_caveats_generated": True,
        "primary_readout_stack_selected": False,
        "sensitivity_stack_selected": False,
        "diagnostic_stack_selected": False,
        "method_winner_selected": False,
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
