"""DESIGN_ASSIGNMENT_RUNTIME_001 deterministic explicit-pool assignment generation."""

from __future__ import annotations

from panel_exp.validation.governed_randomization_runtime_001 import (
    GOVERNED_RANDOMIZATION_BLOCKED,
    GOVERNED_RANDOMIZATION_COMPLETED,
    GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS,
    generate_governed_randomization,
)
import hashlib
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_ASSIGNMENT_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "design_assignment_runtime_implemented_deterministic_explicit_pool_assignment_only_no_matching_or_randomization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_RUNTIME_001_summary.json"
RECOMMENDED_NEXT_ARTIFACT = "READOUT_METHOD_GOVERNANCE_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "READOUT_PLAN_CONTRACT_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "NOT_EVALUATED"})
_READY_TOKENS = frozenset({"PASS", "READY", "READY_FOR_DOWNSTREAM", "COMPLETE", "COMPLETED"})
_SUPPORTED_DETERMINISTIC_ALGORITHMS = frozenset({
    "DETERMINISTIC_RULE_ASSIGNMENT",
    "EXPLICIT_POOL_ASSIGNMENT",
    "DECLARED_POOL_ASSIGNMENT",
})
_UNSUPPORTED_ALGORITHMS = frozenset({
    "MATCHED_PAIR_ASSIGNMENT",
    "BLOCKED_ASSIGNMENT",
    "RERANDOMIZED_ASSIGNMENT",
    "THINNING_ASSIGNMENT",
    "RANDOMIZED_ASSIGNMENT",
    "UNKNOWN_ASSIGNMENT_ALGORITHM",
})
_DEFAULT_CONSTRAINTS = {
    "unique_unit_assignment_required": True,
    "respect_allowed_unit_ids": True,
    "respect_blocked_unit_ids": True,
    "respect_eligible_cell_ids": True,
    "respect_exclusion_flags": True,
    "preserve_declared_cell_roles": True,
}
_RETRY_CATEGORIES = (
    "RELAX_CONSTRAINTS_WITH_APPROVAL",
    "REDUCE_CELL_COUNT",
    "INCREASE_ELIGIBLE_UNIT_POOL",
    "SPLIT_OR_MERGE_CELLS",
    "CHANGE_ASSIGNMENT_ALGORITHM",
    "RERUN_FEASIBILITY_DIAGNOSTICS",
    "RERUN_POWER_MDE_DIAGNOSTICS",
    "RERUN_METHOD_SUITABILITY",
    "BLOCK_DESIGN",
)


class AssignmentRuntimeStatus(str, Enum):
    ASSIGNMENT_RUNTIME_READY_TO_GENERATE = "ASSIGNMENT_RUNTIME_READY_TO_GENERATE"
    ASSIGNMENT_RUNTIME_READY_WITH_WARNINGS = "ASSIGNMENT_RUNTIME_READY_WITH_WARNINGS"
    ASSIGNMENT_RUNTIME_PROVISIONAL = "ASSIGNMENT_RUNTIME_PROVISIONAL"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_DATA_READINESS = "ASSIGNMENT_RUNTIME_BLOCKED_BY_DATA_READINESS"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_GEO_FEASIBILITY = "ASSIGNMENT_RUNTIME_BLOCKED_BY_GEO_FEASIBILITY"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_DESIGN_STRUCTURE = "ASSIGNMENT_RUNTIME_BLOCKED_BY_DESIGN_STRUCTURE"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_SCENARIO_POLICY = "ASSIGNMENT_RUNTIME_BLOCKED_BY_SCENARIO_POLICY"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_ASSIGNMENT_FEASIBILITY = "ASSIGNMENT_RUNTIME_BLOCKED_BY_ASSIGNMENT_FEASIBILITY"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY = "ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_POWER_MDE_READINESS = "ASSIGNMENT_RUNTIME_BLOCKED_BY_POWER_MDE_READINESS"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_UNIT_UNIVERSE = "ASSIGNMENT_RUNTIME_BLOCKED_BY_UNIT_UNIVERSE"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS = "ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS"
    ASSIGNMENT_RUNTIME_BLOCKED_BY_REPRODUCIBILITY_REQUIREMENTS = (
        "ASSIGNMENT_RUNTIME_BLOCKED_BY_REPRODUCIBILITY_REQUIREMENTS"
    )
    ASSIGNMENT_RUNTIME_REQUIRES_REDESIGN_RECHECK = "ASSIGNMENT_RUNTIME_REQUIRES_REDESIGN_RECHECK"
    ASSIGNMENT_RUNTIME_NOT_EVALUATED = "ASSIGNMENT_RUNTIME_NOT_EVALUATED"


class AssignmentCandidateStatus(str, Enum):
    ASSIGNMENT_CANDIDATE_GENERATED = "ASSIGNMENT_CANDIDATE_GENERATED"
    ASSIGNMENT_CANDIDATE_GENERATED_WITH_WARNINGS = "ASSIGNMENT_CANDIDATE_GENERATED_WITH_WARNINGS"
    ASSIGNMENT_CANDIDATE_REJECTED_BY_CONSTRAINTS = "ASSIGNMENT_CANDIDATE_REJECTED_BY_CONSTRAINTS"
    ASSIGNMENT_CANDIDATE_REJECTED_BY_BALANCE = "ASSIGNMENT_CANDIDATE_REJECTED_BY_BALANCE"
    ASSIGNMENT_CANDIDATE_REJECTED_BY_INTERFERENCE_RISK = "ASSIGNMENT_CANDIDATE_REJECTED_BY_INTERFERENCE_RISK"
    ASSIGNMENT_CANDIDATE_REQUIRES_REVIEW = "ASSIGNMENT_CANDIDATE_REQUIRES_REVIEW"
    ASSIGNMENT_CANDIDATE_NOT_GENERATED = "ASSIGNMENT_CANDIDATE_NOT_GENERATED"


class AssignmentIssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class DesignAssignmentRuntimeConfig:
    allow_partial_candidate: bool = False
    deterministic_sort_key: str = "unit_id"
    block_on_unmet_cell_requirement: bool = True
    block_on_duplicate_unit_assignment: bool = True
    block_on_missing_reproducibility_config: bool = True
    block_on_missing_artifact_registry_config: bool = False
    block_on_method_suitability_all_blocked: bool = True
    block_scenario_policy_blocked: bool = True
    block_on_missing_constraints: bool = True
    enable_governed_randomization: bool = True


@dataclass(frozen=True)
class AssignmentIssue:
    code: str
    message: str
    severity: AssignmentIssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class AssignmentRuntimeReadinessReport:
    data_readiness_gate: str
    geo_feasibility_gate: str
    spend_feasibility_gate: str
    power_mde_readiness_gate: str
    design_structure_gate: str
    scenario_policy_gate: str
    assignment_feasibility_gate: str
    method_suitability_gate: str
    unit_universe_gate: str
    cell_requirement_gate: str
    constraint_gate: str
    algorithm_spec_gate: str
    reproducibility_config_gate: str
    artifact_registry_gate: str
    all_hard_gates_pass: bool


@dataclass(frozen=True)
class ExclusionTraceEntry:
    excluded_unit_id: str
    reason: str
    source: str
    cell_id_if_applicable: str | None = None
    constraint_id_if_applicable: str | None = None


@dataclass(frozen=True)
class AssignmentConstraintTrace:
    constraints_checked: tuple[str, ...]
    constraints_passed: tuple[str, ...]
    constraints_failed: tuple[str, ...]
    binding_constraints: tuple[str, ...]
    per_unit_constraint_trace: tuple[dict[str, Any], ...]
    constraint_relaxation_used: bool = False


@dataclass(frozen=True)
class AssignmentConstraintReport:
    constraints_checked: tuple[str, ...]
    constraints_passed: tuple[str, ...]
    constraints_failed: tuple[str, ...]
    binding_constraints: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class AssignmentUnitAllocation:
    unit_id: str
    geo_id: str | None
    assigned_cell_id: str
    assigned_cell_role: str | None
    assignment_reason: str
    assignment_algorithm: str
    eligible_at_assignment_time: bool
    exclusion_flags: tuple[str, ...]
    constraint_flags: tuple[str, ...]
    prior_assignment_flags: tuple[str, ...]
    audit_trace: str


@dataclass(frozen=True)
class AssignmentCellAllocation:
    cell_id: str
    cell_role: str | None
    required_unit_count: int
    allocated_unit_count: int
    allocated_unit_ids: tuple[str, ...]
    unmet_requirement_count: int
    cell_status: str
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class AssignmentReproducibilityManifest:
    algorithm_version: str
    algorithm_category: str
    seed_policy: str
    seed: str
    input_artifact_ids: tuple[str, ...]
    constraint_version: str
    config_hash: str
    unit_universe_hash: str
    eligible_pool_hash: str
    cell_requirement_hash: str
    output_artifact_id: str
    output_hash: str
    deterministic_sort_key: str
    generated_at_policy: str


@dataclass(frozen=True)
class AssignmentClaimBoundaryReport:
    runtime_assignment_generation_implemented: bool = True
    deterministic_explicit_pool_assignment_implemented: bool = True
    assignment_plan_generated: bool = False
    assignment_candidate_generated: bool = False
    unit_allocation_generated: bool = False
    geo_assignment_computed: bool = False
    assignment_candidate_selected: bool = False
    matched_pairs_generated: bool = False
    blocks_generated: bool = False
    randomization_computed: bool = False
    rerandomization_computed: bool = False
    thinning_design_generated: bool = False
    matching_optimization_computed: bool = False
    balance_optimization_computed: bool = False
    balance_diagnostics_computed: bool = False
    interference_adjustment_computed: bool = False
    scenario_policy_feasibility_computed: bool = False
    assignment_feasibility_computed: bool = False
    method_suitability_computed: bool = False
    method_family_selected: bool = False
    estimator_selected: bool = False
    inference_method_selected: bool = False
    method_promotion_authorized: bool = False
    method_production_compatibility_authorized: bool = False
    power_computed: bool = False
    mde_computed: bool = False
    p_value_computed: bool = False
    confidence_interval_computed: bool = False
    lift_computed: bool = False
    roi_computed: bool = False
    budget_optimization_authorized: bool = False
    candidate_design_authorized: bool = False
    treatment_control_assignment_authorized: bool = False
    estimator_inference_authorized: bool = False
    mmm_runtime_calls_implemented: bool = False
    mmm_calibration_authorized: bool = False
    production_authorization_granted: bool = False
    llm_decisioning_authorized: bool = False


@dataclass(frozen=True)
class AssignmentPlan:
    artifact_id: str
    design_id: str
    assignment_runtime_status: AssignmentRuntimeStatus
    assignment_algorithm_category: str
    assignment_algorithm_spec: dict[str, Any]
    assignment_seed_policy: str
    unit_universe_summary: dict[str, Any]
    cell_requirements: tuple[dict[str, Any], ...]
    constraint_summary: dict[str, Any]
    exclusion_trace_summary: dict[str, Any]
    method_suitability_handoff_summary: dict[str, Any]
    balance_requirement_summary: dict[str, Any]
    interference_risk_summary: dict[str, Any]
    reproducibility_manifest: AssignmentReproducibilityManifest | None
    candidate_assignment_count: int
    selected_candidate_id: str | None
    claim_boundary_report: AssignmentClaimBoundaryReport


@dataclass(frozen=True)
class AssignmentCandidate:
    candidate_id: str
    design_id: str
    algorithm_category: str
    seed: str
    cell_allocations: tuple[AssignmentCellAllocation, ...]
    unit_allocations: tuple[AssignmentUnitAllocation, ...]
    constraint_report: AssignmentConstraintReport
    balance_diagnostics: dict[str, Any]
    interference_risk_flags: tuple[str, ...]
    exclusion_trace: tuple[ExclusionTraceEntry, ...]
    candidate_status: AssignmentCandidateStatus
    rejection_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    artifact_registry_entry: dict[str, Any] | None


@dataclass(frozen=True)
class AssignmentFailurePacket:
    failure_id: str
    design_id: str
    assignment_runtime_status: AssignmentRuntimeStatus
    blocking_gates: tuple[str, ...]
    failed_constraints: tuple[str, ...]
    insufficient_units: tuple[dict[str, Any], ...]
    conflicting_cell_requirements: tuple[str, ...]
    missing_reproducibility_config: bool
    method_suitability_blockers: tuple[str, ...]
    suggested_retry_categories: tuple[str, ...]
    warnings: tuple[str, ...]
    claim_boundary_report: AssignmentClaimBoundaryReport


@dataclass(frozen=True)
class DesignAssignmentPacketReport:
    design_id: str
    assignment_runtime_status: AssignmentRuntimeStatus
    assignment_plan: AssignmentPlan | None
    assignment_candidates: tuple[AssignmentCandidate, ...]
    unit_allocation_report: tuple[AssignmentUnitAllocation, ...]
    cell_allocation_report: tuple[AssignmentCellAllocation, ...]
    constraint_report: AssignmentConstraintReport | None
    constraint_trace: AssignmentConstraintTrace | None
    exclusion_trace: tuple[ExclusionTraceEntry, ...]
    reproducibility_manifest: AssignmentReproducibilityManifest | None
    failure_packet: AssignmentFailurePacket | None
    readiness_report: AssignmentRuntimeReadinessReport
    claim_boundary_report: AssignmentClaimBoundaryReport
    issues: tuple[AssignmentIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class DesignAssignmentRuntimeReport:
    artifact_id: str
    design_id: str | None
    assignment_runtime_status: AssignmentRuntimeStatus | None
    assignment_plan: AssignmentPlan | None = None
    assignment_candidates: tuple[AssignmentCandidate, ...] = ()
    unit_allocation_report: tuple[AssignmentUnitAllocation, ...] = ()
    cell_allocation_report: tuple[AssignmentCellAllocation, ...] = ()
    constraint_report: AssignmentConstraintReport | None = None
    constraint_trace: AssignmentConstraintTrace | None = None
    exclusion_trace: tuple[ExclusionTraceEntry, ...] = ()
    reproducibility_manifest: AssignmentReproducibilityManifest | None = None
    failure_packet: AssignmentFailurePacket | None = None
    design_reports: tuple[DesignAssignmentPacketReport, ...] = ()
    aggregate_summary: str | None = None
    readiness_report: AssignmentRuntimeReadinessReport | None = None
    claim_boundary_report: AssignmentClaimBoundaryReport = field(
        default_factory=AssignmentClaimBoundaryReport
    )
    issues: tuple[AssignmentIssue, ...] = ()
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
    return bool(t) and (t in _READY_TOKENS or "READY" in t or t == "PASS" or "FEASIBLE" in t)


def _gate_status(value: Any) -> str:
    if _is_blocked(value):
        return "BLOCKED"
    if _is_ready(value):
        return "PASS"
    t = _token(value)
    if t in ("WARNING", "PROVISIONAL"):
        return t
    if not t:
        return "NOT_EVALUATED"
    return "PASS" if "READY" in t or "FEASIBLE" in t else t


def _stable_hash(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _normalize_requests(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        if input_data and all(isinstance(x, dict) for x in input_data):
            if "design_id" in input_data[0] or "assignment_unit_universe" in input_data[0]:
                return [dict(x) for x in input_data]
    data = _to_dict(input_data)
    if "requests" in data and isinstance(data["requests"], list):
        return [dict(r) for r in data["requests"] if isinstance(r, dict)]
    if "design_id" in data or "assignment_unit_universe" in data:
        return [data]
    return [data] if data else [{"design_id": "design_unspecified"}]


def _upstream(req: dict[str, Any]) -> dict[str, Any]:
    up = req.get("upstream_statuses") or {}
    if isinstance(up, dict):
        return dict(up)
    return {}


def _status_field(req: dict[str, Any], upstream: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in req and req[key] is not None:
            return req[key]
        if key in upstream:
            return upstream[key]
    return None


def _unit_universe(req: dict[str, Any]) -> list[dict[str, Any]]:
    raw = req.get("assignment_unit_universe") or req.get("assignment_units") or []
    if isinstance(raw, list):
        return [dict(u) for u in raw if isinstance(u, dict)]
    return []


def _cell_requirements(req: dict[str, Any]) -> list[dict[str, Any]]:
    raw = req.get("cell_requirements") or []
    if isinstance(raw, list):
        return [dict(c) for c in raw if isinstance(c, dict)]
    return []


def _eligible_pools(req: dict[str, Any]) -> dict[str, list[str]]:
    raw = req.get("eligible_unit_pools") or {}
    if not isinstance(raw, dict):
        return {}
    pools: dict[str, list[str]] = {}
    for key, val in raw.items():
        if isinstance(val, list):
            pools[str(key)] = [str(u) for u in val]
    return pools


def _constraints(req: dict[str, Any]) -> dict[str, bool]:
    raw = req.get("assignment_constraints") or {}
    if not isinstance(raw, dict):
        raw = {}
    merged = dict(_DEFAULT_CONSTRAINTS)
    for k, v in raw.items():
        if k in merged:
            merged[k] = bool(v)
    return merged


def _algorithm_spec(req: dict[str, Any]) -> dict[str, Any]:
    spec = req.get("assignment_algorithm_spec") or {}
    return dict(spec) if isinstance(spec, dict) else {}


def _algorithm_category(spec: dict[str, Any]) -> str:
    return _token(spec.get("algorithm_category") or spec.get("category") or "DETERMINISTIC_RULE_ASSIGNMENT")


def _reproducibility_config(req: dict[str, Any]) -> dict[str, Any]:
    cfg = req.get("reproducibility_config") or {}
    return dict(cfg) if isinstance(cfg, dict) else {}


def _artifact_registry_config(req: dict[str, Any]) -> dict[str, Any]:
    cfg = req.get("artifact_registry_config") or {}
    return dict(cfg) if isinstance(cfg, dict) else {}


def _instrument_matrix(req: dict[str, Any]) -> list[dict[str, Any]]:
    raw = req.get("method_instrument_suitability_matrix") or []
    if isinstance(raw, list):
        return [dict(x) for x in raw if isinstance(x, dict)]
    return []


def _method_suitability_summary(matrix: list[dict[str, Any]]) -> dict[str, Any]:
    if not matrix:
        return {"instrument_count": 0, "all_blocked": False, "only_diagnostic": False}
    statuses = [_token(x.get("suitability_status")) for x in matrix]
    eligible_like = {
        "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
        "METHOD_FAMILY_ELIGIBLE_WITH_WARNINGS",
        "METHOD_FAMILY_RESTRICTED",
    }
    blocked = all(s == "METHOD_FAMILY_BLOCKED" for s in statuses if s)
    only_diag = bool(statuses) and all(
        s in ("METHOD_FAMILY_DIAGNOSTIC_ONLY", "METHOD_FAMILY_NOT_EVALUATED") for s in statuses
    )
    has_eligible = any(s in eligible_like for s in statuses)
    return {
        "instrument_count": len(matrix),
        "all_blocked": blocked and bool(statuses),
        "only_diagnostic": only_diag and not has_eligible,
        "has_eligible_or_restricted": has_eligible,
    }


def _validate_reproducibility(cfg: dict[str, Any], allow_runtime_hash: bool = True) -> tuple[bool, list[str]]:
    missing: list[str] = []
    required = ("algorithm_version", "constraint_version", "seed_policy")
    for key in required:
        if not cfg.get(key):
            missing.append(key)
    if not cfg.get("config_hash") and not cfg.get("deterministic_config_repr"):
        missing.append("config_hash_or_deterministic_config_repr")
    if not cfg.get("unit_universe_hash") and not allow_runtime_hash:
        missing.append("unit_universe_hash")
    if not cfg.get("output_artifact_id") and not allow_runtime_hash:
        missing.append("output_artifact_id")
    return len(missing) == 0, missing


def _evaluate_readiness(
    req: dict[str, Any],
    cfg: DesignAssignmentRuntimeConfig,
) -> tuple[AssignmentRuntimeReadinessReport, list[str], list[str], list[AssignmentIssue]]:
    upstream = _upstream(req)
    issues: list[AssignmentIssue] = []
    warnings: list[str] = []
    blocking: list[str] = []

    data = _gate_status(_status_field(req, upstream, "profiler_status", "data_readiness_status"))
    geo = _gate_status(_status_field(req, upstream, "geo_feasibility_status"))
    spend = _gate_status(_status_field(req, upstream, "spend_feasibility_status"))
    power = _gate_status(_status_field(req, upstream, "power_mde_status"))
    design = _gate_status(_status_field(req, upstream, "design_structure_status", "design_cell_structure_status"))
    scenario = _gate_status(_status_field(req, upstream, "scenario_policy_status", "scenario_policy_feasibility_status"))
    assign_feas = _gate_status(
        _status_field(req, upstream, "assignment_feasibility_status")
    )
    method_suit = _gate_status(_status_field(req, upstream, "method_suitability_status"))

    universe = _unit_universe(req)
    unit_gate = "PASS" if universe else "BLOCKED"
    cells = _cell_requirements(req)
    cell_gate = "PASS" if cells else "BLOCKED"

    constraints = req.get("assignment_constraints")
    if constraints is None or (isinstance(constraints, dict) and not constraints):
        constraint_gate = "BLOCKED" if cfg.block_on_missing_constraints else "PROVISIONAL"
    else:
        constraint_gate = "PASS"

    spec = _algorithm_spec(req)
    cat = _algorithm_category(spec)
    if cat in _UNSUPPORTED_ALGORITHMS:
        if cat == "RANDOMIZED_ASSIGNMENT" and cfg.enable_governed_randomization:
            algo_gate = "PASS"
        else:
            algo_gate = "BLOCKED"
    elif cat in _SUPPORTED_DETERMINISTIC_ALGORITHMS or cat in (
        "COMMON_CONTROL_ASSIGNMENT", "SPLIT_CONTROL_ASSIGNMENT",
    ):
        algo_gate = "PASS"
    else:
        algo_gate = "BLOCKED"

    repro = _reproducibility_config(req)
    repro_ok, repro_missing = _validate_reproducibility(repro)
    repro_gate = "PASS" if repro_ok else ("BLOCKED" if cfg.block_on_missing_reproducibility_config else "PROVISIONAL")

    registry = _artifact_registry_config(req)
    registry_gate = "PASS" if registry else (
        "BLOCKED" if cfg.block_on_missing_artifact_registry_config else "PROVISIONAL"
    )

    matrix = _instrument_matrix(req)
    ms_summary = _method_suitability_summary(matrix)
    if ms_summary["all_blocked"]:
        method_gate = "BLOCKED"
    elif ms_summary["only_diagnostic"]:
        method_gate = "PROVISIONAL"
        warnings.append("only diagnostic-only method instruments available")
    elif method_suit == "BLOCKED":
        method_gate = "BLOCKED"
    else:
        method_gate = "PASS" if matrix or method_suit == "PASS" else "PROVISIONAL"

    redesign = _token(_status_field(req, upstream, "redesign_recheck_required"))
    if redesign in ("TRUE", "1", "YES") or "REDESIGN" in _token(assign_feas) or "RECHECK" in _token(assign_feas):
        if cat == "SPLIT_CONTROL_ASSIGNMENT":
            algo_gate = "BLOCKED"
            blocking.append("split-control requires redesign recheck")

    hard_pass = all(
        g == "PASS"
        for g in (data, geo, design, unit_gate, cell_gate, algo_gate, repro_gate)
    ) and constraint_gate != "BLOCKED" and method_gate != "BLOCKED"

    readiness = AssignmentRuntimeReadinessReport(
        data_readiness_gate=data,
        geo_feasibility_gate=geo,
        spend_feasibility_gate=spend,
        power_mde_readiness_gate=power,
        design_structure_gate=design,
        scenario_policy_gate=scenario,
        assignment_feasibility_gate=assign_feas,
        method_suitability_gate=method_gate,
        unit_universe_gate=unit_gate,
        cell_requirement_gate=cell_gate,
        constraint_gate=constraint_gate,
        algorithm_spec_gate=algo_gate,
        reproducibility_config_gate=repro_gate,
        artifact_registry_gate=registry_gate,
        all_hard_gates_pass=hard_pass,
    )
    return readiness, warnings, blocking, issues


def _select_runtime_status(
    readiness: AssignmentRuntimeReadinessReport,
    warnings: list[str],
    cfg: DesignAssignmentRuntimeConfig,
    ms_summary: dict[str, Any],
) -> AssignmentRuntimeStatus:
    r = readiness
    if r.data_readiness_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_DATA_READINESS
    if r.geo_feasibility_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_GEO_FEASIBILITY
    if r.design_structure_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_DESIGN_STRUCTURE
    if r.scenario_policy_gate == "BLOCKED" and cfg.block_scenario_policy_blocked:
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_SCENARIO_POLICY
    if _is_blocked(r.assignment_feasibility_gate):
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_ASSIGNMENT_FEASIBILITY
    if r.power_mde_readiness_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_POWER_MDE_READINESS
    if ms_summary.get("all_blocked") and cfg.block_on_method_suitability_all_blocked:
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY
    if r.method_suitability_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_METHOD_SUITABILITY
    if r.unit_universe_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_UNIT_UNIVERSE
    if r.cell_requirement_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS
    if r.constraint_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS
    if r.algorithm_spec_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS
    if r.reproducibility_config_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_REPRODUCIBILITY_REQUIREMENTS
    if r.scenario_policy_gate == "BLOCKED":
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_PROVISIONAL
    if r.method_suitability_gate == "PROVISIONAL" or ms_summary.get("only_diagnostic"):
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_PROVISIONAL
    if warnings:
        return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_READY_WITH_WARNINGS
    return AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_READY_TO_GENERATE


def _runtime_is_blocked(status: AssignmentRuntimeStatus) -> bool:
    return status.value.startswith("ASSIGNMENT_RUNTIME_BLOCKED_")


def _resolve_pool_for_cell(
    cell_id: str,
    cell_role: str | None,
    pools: dict[str, list[str]],
) -> list[str]:
    if cell_id in pools:
        return list(pools[cell_id])
    if cell_role and cell_role in pools:
        return list(pools[cell_role])
    role_token = _token(cell_role)
    if role_token == "CONTROL" and "control" in {k.lower() for k in pools}:
        for k, v in pools.items():
            if k.lower() == "control":
                return list(v)
    if role_token in ("TREATMENT", "TEST") and "treatment" in {k.lower() for k in pools}:
        for k, v in pools.items():
            if k.lower() == "treatment":
                return list(v)
    return []


def _unit_sort_key(unit: dict[str, Any], sort_field: str) -> str:
    val = unit.get(sort_field) or unit.get("unit_id")
    return str(val) if val is not None else ""


def _governed_randomization_input(req: dict[str, Any]) -> dict[str, Any]:
    universe = _unit_universe(req)
    eligible = req.get("eligible_units")
    if not eligible:
        eligible = [{"unit_id": str(u.get("unit_id")), **u} for u in universe if u.get("unit_id")]
    repro = _reproducibility_config(req)
    spec = _algorithm_spec(req)
    return {
        "request_id": req.get("request_id") or req.get("design_id"),
        "design_id": req.get("design_id"),
        "randomization_type": spec.get("randomization_type") or "TWO_CELL_COMPLETE_RANDOMIZATION",
        "eligible_units": eligible,
        "excluded_units": req.get("excluded_units") or [],
        "cells": req.get("cells") or _cell_requirements(req),
        "allocation_ratio": req.get("allocation_ratio") or spec.get("allocation_ratio"),
        "seed": req.get("seed") or repro.get("seed"),
        "seed_policy": req.get("seed_policy") or repro.get("seed_policy"),
        "strata_field": req.get("strata_field") or spec.get("strata_field"),
        "block_field": req.get("block_field") or spec.get("block_field"),
        "common_control_cell_id": req.get("common_control_cell_id") or spec.get("common_control_cell_id"),
        "production_context": req.get("production_context"),
        "assignment_feasibility_status": _status_field(req, _upstream(req), "assignment_feasibility_status"),
        "method_suitability_status": _status_field(req, _upstream(req), "method_suitability_status"),
    }


def _convert_governed_allocations(
    rows: tuple[dict[str, Any], ...],
    algorithm_category: str,
) -> tuple[AssignmentUnitAllocation, ...]:
    converted: list[AssignmentUnitAllocation] = []
    for row in rows:
        converted.append(AssignmentUnitAllocation(
            unit_id=str(row.get("unit_id")),
            geo_id=str(row.get("geo_id")) if row.get("geo_id") else None,
            assigned_cell_id=str(row.get("assigned_cell_id") or row.get("cell_id")),
            assigned_cell_role=str(row.get("assigned_cell_role") or row.get("cell_role")) if row.get("assigned_cell_role") or row.get("cell_role") else None,
            assignment_reason="governed_randomization",
            assignment_algorithm=algorithm_category,
            eligible_at_assignment_time=True,
            exclusion_flags=(),
            constraint_flags=(),
            prior_assignment_flags=(),
            audit_trace=str(row.get("assignment_source") or "GOVERNED_RANDOMIZATION_RUNTIME_001"),
        ))
    return tuple(converted)


def _cell_allocs_from_governed(
    cells: list[dict[str, Any]],
    unit_allocs: tuple[AssignmentUnitAllocation, ...],
) -> tuple[AssignmentCellAllocation, ...]:
    counts: dict[str, list[str]] = {}
    roles: dict[str, str | None] = {}
    for cell in cells:
        cid = str(cell.get("cell_id"))
        roles[cid] = str(cell.get("role") or cell.get("cell_role")) if cell.get("role") or cell.get("cell_role") else None
        counts[cid] = []
    for alloc in unit_allocs:
        counts.setdefault(alloc.assigned_cell_id, []).append(alloc.unit_id)
    result: list[AssignmentCellAllocation] = []
    for cell in cells:
        cid = str(cell.get("cell_id"))
        required = int(cell.get("required_unit_count") or cell.get("target_size") or 0)
        allocated = counts.get(cid, [])
        result.append(AssignmentCellAllocation(
            cell_id=cid,
            cell_role=roles.get(cid),
            required_unit_count=required,
            allocated_unit_count=len(allocated),
            allocated_unit_ids=tuple(allocated),
            unmet_requirement_count=max(0, required - len(allocated)),
            cell_status="SATISFIED" if len(allocated) >= required or required == 0 else "PARTIAL",
            warnings=(),
            blocking_reasons=(),
        ))
    return tuple(result)


def _deterministic_allocate(
    req: dict[str, Any],
    cfg: DesignAssignmentRuntimeConfig,
    algorithm_category: str,
) -> tuple[
    tuple[AssignmentUnitAllocation, ...],
    tuple[AssignmentCellAllocation, ...],
    tuple[ExclusionTraceEntry, ...],
    AssignmentConstraintReport,
    AssignmentConstraintTrace,
    list[str],
    list[str],
    list[dict[str, Any]],
]:
    universe = _unit_universe(req)
    universe_by_id = {str(u.get("unit_id")): u for u in universe if u.get("unit_id") is not None}
    cells = sorted(_cell_requirements(req), key=lambda c: str(c.get("cell_id", "")))
    pools = _eligible_pools(req)
    constraints = _constraints(req)
    excluded_raw = req.get("excluded_units") or []
    excluded_set = {str(u) for u in excluded_raw} if isinstance(excluded_raw, list) else set()

    exclusion_trace: list[ExclusionTraceEntry] = []
    unit_allocations: list[AssignmentUnitAllocation] = []
    cell_allocations: list[AssignmentCellAllocation] = []
    warnings: list[str] = []
    blocking: list[str] = []
    insufficient: list[dict[str, Any]] = []
    assigned_units: set[str] = set()

    constraints_checked = list(_DEFAULT_CONSTRAINTS.keys())
    constraints_passed: list[str] = []
    constraints_failed: list[str] = []
    per_unit_trace: list[dict[str, Any]] = []

    for uid in sorted(excluded_set):
        exclusion_trace.append(ExclusionTraceEntry(
            excluded_unit_id=uid,
            reason="declared excluded",
            source="excluded_units",
        ))

    for cell in cells:
        cell_id = str(cell.get("cell_id", ""))
        cell_role = str(cell.get("cell_role")) if cell.get("cell_role") else None
        required = int(cell.get("required_unit_count") or cell.get("min_unit_count") or 0)
        max_units = cell.get("max_unit_count")
        allowed = {str(x) for x in (cell.get("allowed_unit_ids") or [])}
        blocked_ids = {str(x) for x in (cell.get("blocked_unit_ids") or [])}

        pool_ids = _resolve_pool_for_cell(cell_id, cell_role, pools)
        if not pool_ids and not required:
            cell_allocations.append(AssignmentCellAllocation(
                cell_id=cell_id,
                cell_role=cell_role,
                required_unit_count=0,
                allocated_unit_count=0,
                allocated_unit_ids=(),
                unmet_requirement_count=0,
                cell_status="SATISFIED",
                warnings=(),
                blocking_reasons=(),
            ))
            continue

        candidates: list[dict[str, Any]] = []
        for uid in pool_ids:
            unit = universe_by_id.get(uid)
            trace_reasons: list[str] = []

            if unit is None:
                exclusion_trace.append(ExclusionTraceEntry(
                    excluded_unit_id=uid,
                    reason="unit not in universe",
                    source="eligible_pool",
                    cell_id_if_applicable=cell_id,
                ))
                continue

            if not unit.get("eligible", True):
                exclusion_trace.append(ExclusionTraceEntry(
                    excluded_unit_id=uid,
                    reason="unit not eligible",
                    source="universe",
                    cell_id_if_applicable=cell_id,
                ))
                continue

            if constraints.get("respect_exclusion_flags") and unit.get("exclusion_flags"):
                flags = unit.get("exclusion_flags")
                if isinstance(flags, list) and flags:
                    exclusion_trace.append(ExclusionTraceEntry(
                        excluded_unit_id=uid,
                        reason=f"exclusion flags: {flags}",
                        source="exclusion_flags",
                        cell_id_if_applicable=cell_id,
                    ))
                    continue

            if uid in excluded_set:
                continue

            if constraints.get("unique_unit_assignment_required") and uid in assigned_units:
                msg = f"unit {uid} already assigned to another cell"
                if cfg.block_on_duplicate_unit_assignment:
                    blocking.append(msg)
                    constraints_failed.append("unique_unit_assignment_required")
                exclusion_trace.append(ExclusionTraceEntry(
                    excluded_unit_id=uid,
                    reason=msg,
                    source="unique_assignment",
                    cell_id_if_applicable=cell_id,
                    constraint_id_if_applicable="unique_unit_assignment_required",
                ))
                continue

            if constraints.get("respect_blocked_unit_ids") and uid in blocked_ids:
                exclusion_trace.append(ExclusionTraceEntry(
                    excluded_unit_id=uid,
                    reason="blocked for cell",
                    source="blocked_unit_ids",
                    cell_id_if_applicable=cell_id,
                ))
                continue

            if constraints.get("respect_allowed_unit_ids") and allowed and uid not in allowed:
                exclusion_trace.append(ExclusionTraceEntry(
                    excluded_unit_id=uid,
                    reason="not in allowed_unit_ids",
                    source="allowed_unit_ids",
                    cell_id_if_applicable=cell_id,
                ))
                continue

            eligible_cells = unit.get("eligible_cell_ids")
            if constraints.get("respect_eligible_cell_ids") and eligible_cells:
                ec = {_token(c) for c in eligible_cells}
                if _token(cell_id) not in ec and cell_role and _token(cell_role) not in ec:
                    exclusion_trace.append(ExclusionTraceEntry(
                        excluded_unit_id=uid,
                        reason="not eligible for cell",
                        source="eligible_cell_ids",
                        cell_id_if_applicable=cell_id,
                    ))
                    continue

            candidates.append(unit)
            per_unit_trace.append({"unit_id": uid, "cell_id": cell_id, "eligible": True, "trace_reasons": trace_reasons})

        sort_field = cfg.deterministic_sort_key
        candidates.sort(key=lambda u: _unit_sort_key(u, sort_field))

        take = required
        if max_units is not None:
            take = min(take, int(max_units))

        selected = candidates[:take]
        allocated_ids: list[str] = []
        for unit in selected:
            uid = str(unit["unit_id"])
            assigned_units.add(uid)
            allocated_ids.append(uid)
            unit_allocations.append(AssignmentUnitAllocation(
                unit_id=uid,
                geo_id=str(unit.get("geo_id")) if unit.get("geo_id") else None,
                assigned_cell_id=cell_id,
                assigned_cell_role=cell_role,
                assignment_reason="deterministic explicit pool allocation",
                assignment_algorithm=algorithm_category,
                eligible_at_assignment_time=bool(unit.get("eligible", True)),
                exclusion_flags=tuple(str(x) for x in (unit.get("exclusion_flags") or [])),
                constraint_flags=tuple(str(x) for x in (unit.get("constraint_flags") or [])),
                prior_assignment_flags=tuple(str(x) for x in (unit.get("prior_assignment_flags") or [])),
                audit_trace=f"allocated to {cell_id} via sorted explicit pool",
            ))

        unmet = max(0, required - len(selected))
        cell_status = "SATISFIED" if unmet == 0 else "UNMET"
        cell_blocking: list[str] = []
        if unmet > 0:
            insufficient.append({"cell_id": cell_id, "required": required, "allocated": len(selected), "unmet": unmet})
            cell_blocking.append(f"unmet requirement: need {required}, got {len(selected)}")
            if cfg.block_on_unmet_cell_requirement:
                blocking.append(f"cell {cell_id} unmet requirement")

        cell_allocations.append(AssignmentCellAllocation(
            cell_id=cell_id,
            cell_role=cell_role,
            required_unit_count=required,
            allocated_unit_count=len(selected),
            allocated_unit_ids=tuple(allocated_ids),
            unmet_requirement_count=unmet,
            cell_status=cell_status,
            warnings=tuple(warnings),
            blocking_reasons=tuple(cell_blocking),
        ))

    for cname, passed in [
        ("unique_unit_assignment_required", "unique_unit_assignment_required" not in constraints_failed),
        ("respect_allowed_unit_ids", True),
        ("respect_blocked_unit_ids", True),
        ("respect_eligible_cell_ids", True),
        ("respect_exclusion_flags", True),
        ("preserve_declared_cell_roles", True),
    ]:
        if passed:
            constraints_passed.append(cname)
        else:
            constraints_failed.append(cname)

    constraint_report = AssignmentConstraintReport(
        constraints_checked=tuple(constraints_checked),
        constraints_passed=tuple(constraints_passed),
        constraints_failed=tuple(dict.fromkeys(constraints_failed)),
        binding_constraints=tuple(dict.fromkeys(constraints_failed)),
        status="FAILED" if constraints_failed or blocking else "PASSED",
    )
    constraint_trace = AssignmentConstraintTrace(
        constraints_checked=tuple(constraints_checked),
        constraints_passed=tuple(constraints_passed),
        constraints_failed=tuple(dict.fromkeys(constraints_failed)),
        binding_constraints=tuple(dict.fromkeys(constraints_failed)),
        per_unit_constraint_trace=tuple(per_unit_trace),
        constraint_relaxation_used=False,
    )
    return (
        tuple(unit_allocations),
        tuple(cell_allocations),
        tuple(exclusion_trace),
        constraint_report,
        constraint_trace,
        warnings,
        blocking,
        insufficient,
    )


def _build_reproducibility_manifest(
    req: dict[str, Any],
    cfg: DesignAssignmentRuntimeConfig,
    algorithm_category: str,
    unit_allocations: tuple[AssignmentUnitAllocation, ...],
    repro_cfg: dict[str, Any],
) -> AssignmentReproducibilityManifest:
    universe = _unit_universe(req)
    pools = _eligible_pools(req)
    cells = _cell_requirements(req)
    output_ids = [a.unit_id for a in unit_allocations]
    output_hash = _stable_hash(output_ids)

    return AssignmentReproducibilityManifest(
        algorithm_version=str(repro_cfg.get("algorithm_version", "1.0.0")),
        algorithm_category=algorithm_category,
        seed_policy=str(repro_cfg.get("seed_policy", "NOT_APPLICABLE_DETERMINISTIC")),
        seed=str(repro_cfg.get("seed", "NOT_APPLICABLE_DETERMINISTIC")),
        input_artifact_ids=tuple(str(x) for x in (repro_cfg.get("input_artifact_ids") or [])),
        constraint_version=str(repro_cfg.get("constraint_version", "1.0.0")),
        config_hash=str(repro_cfg.get("config_hash") or _stable_hash(repro_cfg.get("deterministic_config_repr") or {})),
        unit_universe_hash=str(repro_cfg.get("unit_universe_hash") or _stable_hash(universe)),
        eligible_pool_hash=_stable_hash(pools),
        cell_requirement_hash=_stable_hash(cells),
        output_artifact_id=str(repro_cfg.get("output_artifact_id") or f"assignment_{_stable_hash(output_ids)}"),
        output_hash=output_hash,
        deterministic_sort_key=cfg.deterministic_sort_key,
        generated_at_policy="not_recorded_runtime_is_deterministic",
    )


def _failure_packet(
    design_id: str,
    status: AssignmentRuntimeStatus,
    readiness: AssignmentRuntimeReadinessReport,
    blocking: list[str],
    failed_constraints: tuple[str, ...],
    insufficient: tuple[dict[str, Any], ...],
    missing_repro: bool,
    ms_blockers: tuple[str, ...],
    warnings: list[str],
) -> AssignmentFailurePacket:
    gates: list[str] = []
    r = readiness
    for name, gate in (
        ("data_readiness", r.data_readiness_gate),
        ("geo_feasibility", r.geo_feasibility_gate),
        ("design_structure", r.design_structure_gate),
        ("scenario_policy", r.scenario_policy_gate),
        ("assignment_feasibility", r.assignment_feasibility_gate),
        ("method_suitability", r.method_suitability_gate),
        ("unit_universe", r.unit_universe_gate),
        ("constraints", r.constraint_gate),
        ("algorithm_spec", r.algorithm_spec_gate),
        ("reproducibility", r.reproducibility_config_gate),
    ):
        if gate == "BLOCKED":
            gates.append(name)

    retries: list[str] = []
    if insufficient:
        retries.append("INCREASE_ELIGIBLE_UNIT_POOL")
    if failed_constraints:
        retries.append("RELAX_CONSTRAINTS_WITH_APPROVAL")
    if r.algorithm_spec_gate == "BLOCKED":
        retries.append("CHANGE_ASSIGNMENT_ALGORITHM")
    if r.assignment_feasibility_gate == "BLOCKED":
        retries.append("RERUN_FEASIBILITY_DIAGNOSTICS")
    if r.method_suitability_gate == "BLOCKED":
        retries.append("RERUN_METHOD_SUITABILITY")

    return AssignmentFailurePacket(
        failure_id=f"failure_{design_id}_{status.value}",
        design_id=design_id,
        assignment_runtime_status=status,
        blocking_gates=tuple(gates),
        failed_constraints=failed_constraints,
        insufficient_units=insufficient,
        conflicting_cell_requirements=(),
        missing_reproducibility_config=missing_repro,
        method_suitability_blockers=ms_blockers,
        suggested_retry_categories=tuple(dict.fromkeys(retries)) or _RETRY_CATEGORIES[:1],
        warnings=tuple(warnings),
        claim_boundary_report=AssignmentClaimBoundaryReport(),
    )


def _claim_boundary(generated: bool) -> AssignmentClaimBoundaryReport:
    return AssignmentClaimBoundaryReport(
        assignment_plan_generated=generated,
        assignment_candidate_generated=generated,
        unit_allocation_generated=generated,
        geo_assignment_computed=generated,
    )


def _evaluate_single_request(
    req: dict[str, Any],
    cfg: DesignAssignmentRuntimeConfig,
) -> DesignAssignmentPacketReport:
    design_id = str(req.get("design_id", "design_unspecified"))
    issues: list[AssignmentIssue] = []
    readiness, warnings, blocking, _ = _evaluate_readiness(req, cfg)
    matrix = _instrument_matrix(req)
    ms_summary = _method_suitability_summary(matrix)
    runtime_status = _select_runtime_status(readiness, warnings, cfg, ms_summary)

    repro_cfg = _reproducibility_config(req)
    spec = _algorithm_spec(req)
    algorithm_category = _algorithm_category(spec)

    if algorithm_category == "RANDOMIZED_ASSIGNMENT" and cfg.enable_governed_randomization:
        gov_report = generate_governed_randomization(_governed_randomization_input(req))
        if gov_report.status in {
            GOVERNED_RANDOMIZATION_COMPLETED,
            GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS,
        } and gov_report.assignment_artifact_generated:
            unit_allocs = _convert_governed_allocations(gov_report.unit_allocations, algorithm_category)
            cell_allocs = _cell_allocs_from_governed(_cell_requirements(req) or list(req.get("cells") or []), unit_allocs)
            constraint_report = AssignmentConstraintReport(
                constraints_checked=("governed_randomization",),
                constraints_passed=("governed_randomization",),
                constraints_failed=(),
                binding_constraints=(),
                status="PASS",
            )
            constraint_trace = AssignmentConstraintTrace(
                constraints_checked=("governed_randomization",),
                constraints_passed=("governed_randomization",),
                constraints_failed=(),
                binding_constraints=(),
                per_unit_constraint_trace=(),
            )
            repro_manifest = AssignmentReproducibilityManifest(
                algorithm_version=str((gov_report.reproducibility_manifest or {}).get("algorithm_version", "1.0.0")),
                algorithm_category=algorithm_category,
                seed_policy=str(gov_report.seed_policy or "GOVERNED_RANDOMIZATION"),
                seed=str(gov_report.seed or ""),
                input_artifact_ids=tuple(str(x) for x in (repro_cfg.get("input_artifact_ids") or [])),
                constraint_version=str(repro_cfg.get("constraint_version", "1.0.0")),
                config_hash=str((gov_report.reproducibility_manifest or {}).get("config_hash", "")),
                unit_universe_hash=str((gov_report.reproducibility_manifest or {}).get("eligible_pool_hash", "")),
                eligible_pool_hash=str((gov_report.reproducibility_manifest or {}).get("eligible_pool_hash", "")),
                cell_requirement_hash=_stable_hash(_cell_requirements(req)),
                output_artifact_id=str(gov_report.assignment_artifact_id or ""),
                output_hash=str(gov_report.assignment_hash or ""),
                deterministic_sort_key=cfg.deterministic_sort_key,
                generated_at_policy="DETERMINISTIC_NO_WALL_CLOCK",
            )
            candidate_status = AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED
            if gov_report.status == GOVERNED_RANDOMIZATION_COMPLETED_WITH_WARNINGS:
                candidate_status = AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED_WITH_WARNINGS
            candidate = AssignmentCandidate(
                candidate_id=str(gov_report.assignment_candidate_id or f"candidate_{design_id}"),
                design_id=design_id,
                algorithm_category=algorithm_category,
                seed=str(gov_report.seed or ""),
                cell_allocations=cell_allocs,
                unit_allocations=unit_allocs,
                constraint_report=constraint_report,
                balance_diagnostics={"status": "not_computed"},
                interference_risk_flags=(),
                exclusion_trace=(),
                candidate_status=candidate_status,
                rejection_reasons=(),
                warnings=gov_report.warnings,
                artifact_registry_entry=None,
            )
            plan = AssignmentPlan(
                artifact_id=f"plan_{design_id}",
                design_id=design_id,
                assignment_runtime_status=runtime_status,
                assignment_algorithm_category=algorithm_category,
                assignment_algorithm_spec=spec,
                assignment_seed_policy=str(gov_report.seed_policy or ""),
                unit_universe_summary={"total_units": len(_unit_universe(req)), "allocated_units": len(unit_allocs)},
                cell_requirements=tuple(_cell_requirements(req)),
                constraint_summary={"constraints": _constraints(req), "status": "PASS"},
                exclusion_trace_summary={"excluded_count": gov_report.excluded_unit_count},
                method_suitability_handoff_summary=ms_summary,
                balance_requirement_summary={"status": "not_computed"},
                interference_risk_summary={"status": "preserved_not_adjusted"},
                reproducibility_manifest=repro_manifest,
                candidate_assignment_count=1,
                selected_candidate_id=candidate.candidate_id,
                claim_boundary_report=AssignmentClaimBoundaryReport(),
            )
            return DesignAssignmentPacketReport(
                design_id=design_id,
                assignment_runtime_status=runtime_status,
                assignment_plan=plan,
                assignment_candidates=(candidate,),
                unit_allocation_report=unit_allocs,
                cell_allocation_report=cell_allocs,
                constraint_report=constraint_report,
                constraint_trace=constraint_trace,
                exclusion_trace=(),
                reproducibility_manifest=repro_manifest,
                failure_packet=None,
                readiness_report=readiness,
                claim_boundary_report=AssignmentClaimBoundaryReport(),
                issues=tuple(issues),
                warnings=tuple(warnings),
                blocking_reasons=(),
            )
        warnings.extend(gov_report.warnings)
        blocking.extend(gov_report.blocking_reasons)
        runtime_status = AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS
        if gov_report.status == GOVERNED_RANDOMIZATION_BLOCKED:
            runtime_status = AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_REQUIRES_REDESIGN_RECHECK
        fp = _failure_packet(
            design_id,
            runtime_status,
            readiness,
            blocking,
            (),
            (),
            False,
            (),
            warnings,
        )
        return DesignAssignmentPacketReport(
            design_id=design_id,
            assignment_runtime_status=runtime_status,
            assignment_plan=None,
            assignment_candidates=(),
            unit_allocation_report=(),
            cell_allocation_report=(),
            constraint_report=None,
            constraint_trace=None,
            exclusion_trace=(),
            reproducibility_manifest=None,
            failure_packet=fp,
            readiness_report=readiness,
            claim_boundary_report=AssignmentClaimBoundaryReport(),
            issues=tuple(issues),
            warnings=tuple(warnings),
            blocking_reasons=tuple(blocking),
        )

    if _runtime_is_blocked(runtime_status):
        repro_ok, repro_missing = _validate_reproducibility(repro_cfg)
        fp = _failure_packet(
            design_id,
            runtime_status,
            readiness,
            blocking,
            (),
            (),
            not repro_ok,
            ("all instruments blocked",) if ms_summary.get("all_blocked") else (),
            warnings,
        )
        return DesignAssignmentPacketReport(
            design_id=design_id,
            assignment_runtime_status=runtime_status,
            assignment_plan=None,
            assignment_candidates=(),
            unit_allocation_report=(),
            cell_allocation_report=(),
            constraint_report=None,
            constraint_trace=None,
            exclusion_trace=(),
            reproducibility_manifest=None,
            failure_packet=fp,
            readiness_report=readiness,
            claim_boundary_report=AssignmentClaimBoundaryReport(),
            issues=tuple(issues),
            warnings=tuple(warnings),
            blocking_reasons=tuple(blocking),
        )

    (
        unit_allocs,
        cell_allocs,
        exclusion_trace,
        constraint_report,
        constraint_trace,
        alloc_warnings,
        alloc_blocking,
        insufficient,
    ) = _deterministic_allocate(req, cfg, algorithm_category)

    warnings.extend(alloc_warnings)
    blocking.extend(alloc_blocking)

    candidate_status = AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED
    if alloc_blocking or insufficient:
        if cfg.block_on_unmet_cell_requirement and insufficient:
            runtime_status = AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS
            candidate_status = AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_REJECTED_BY_CONSTRAINTS
        elif alloc_blocking:
            candidate_status = AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_REJECTED_BY_CONSTRAINTS
    elif warnings:
        candidate_status = AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED_WITH_WARNINGS

    generated = candidate_status in (
        AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED,
        AssignmentCandidateStatus.ASSIGNMENT_CANDIDATE_GENERATED_WITH_WARNINGS,
    ) and not alloc_blocking and not (insufficient and cfg.block_on_unmet_cell_requirement)

    if not generated:
        fp = _failure_packet(
            design_id,
            runtime_status if _runtime_is_blocked(runtime_status) else AssignmentRuntimeStatus.ASSIGNMENT_RUNTIME_BLOCKED_BY_CONSTRAINTS,
            readiness,
            blocking,
            constraint_report.constraints_failed,
            tuple(insufficient),
            False,
            (),
            warnings,
        )
        return DesignAssignmentPacketReport(
            design_id=design_id,
            assignment_runtime_status=fp.assignment_runtime_status,
            assignment_plan=None,
            assignment_candidates=(),
            unit_allocation_report=unit_allocs,
            cell_allocation_report=cell_allocs,
            constraint_report=constraint_report,
            constraint_trace=constraint_trace,
            exclusion_trace=exclusion_trace,
            reproducibility_manifest=None,
            failure_packet=fp,
            readiness_report=readiness,
            claim_boundary_report=AssignmentClaimBoundaryReport(),
            issues=tuple(issues),
            warnings=tuple(warnings),
            blocking_reasons=tuple(blocking),
        )

    repro_manifest = _build_reproducibility_manifest(req, cfg, algorithm_category, unit_allocs, repro_cfg)
    registry = _artifact_registry_config(req)
    candidate_id = f"candidate_{design_id}_deterministic_001"

    candidate = AssignmentCandidate(
        candidate_id=candidate_id,
        design_id=design_id,
        algorithm_category=algorithm_category,
        seed=str(repro_cfg.get("seed", "NOT_APPLICABLE_DETERMINISTIC")),
        cell_allocations=cell_allocs,
        unit_allocations=unit_allocs,
        constraint_report=constraint_report,
        balance_diagnostics={"status": "not_computed"},
        interference_risk_flags=(),
        exclusion_trace=exclusion_trace,
        candidate_status=candidate_status,
        rejection_reasons=(),
        warnings=tuple(warnings),
        artifact_registry_entry=dict(registry) if registry else None,
    )

    plan = AssignmentPlan(
        artifact_id=f"plan_{design_id}",
        design_id=design_id,
        assignment_runtime_status=runtime_status,
        assignment_algorithm_category=algorithm_category,
        assignment_algorithm_spec=spec,
        assignment_seed_policy=str(repro_cfg.get("seed_policy", "NOT_APPLICABLE_DETERMINISTIC")),
        unit_universe_summary={
            "total_units": len(_unit_universe(req)),
            "allocated_units": len(unit_allocs),
        },
        cell_requirements=tuple(_cell_requirements(req)),
        constraint_summary={"constraints": _constraints(req), "status": constraint_report.status},
        exclusion_trace_summary={"excluded_count": len(exclusion_trace)},
        method_suitability_handoff_summary=ms_summary,
        balance_requirement_summary={"status": "not_computed"},
        interference_risk_summary={"status": "preserved_not_adjusted"},
        reproducibility_manifest=repro_manifest,
        candidate_assignment_count=1,
        selected_candidate_id=None,
        claim_boundary_report=_claim_boundary(True),
    )

    return DesignAssignmentPacketReport(
        design_id=design_id,
        assignment_runtime_status=runtime_status,
        assignment_plan=plan,
        assignment_candidates=(candidate,),
        unit_allocation_report=unit_allocs,
        cell_allocation_report=cell_allocs,
        constraint_report=constraint_report,
        constraint_trace=constraint_trace,
        exclusion_trace=exclusion_trace,
        reproducibility_manifest=repro_manifest,
        failure_packet=None,
        readiness_report=readiness,
        claim_boundary_report=_claim_boundary(True),
        issues=tuple(issues),
        warnings=tuple(warnings),
        blocking_reasons=(),
    )


def generate_design_assignment(
    input_data: Any,
    config: DesignAssignmentRuntimeConfig | None = None,
) -> DesignAssignmentRuntimeReport:
    """Generate deterministic assignment artifacts from explicit eligible pools."""
    cfg = config or DesignAssignmentRuntimeConfig()
    requests = _normalize_requests(input_data)
    reports = [_evaluate_single_request(r, cfg) for r in requests]

    all_issues: list[AssignmentIssue] = []
    all_warnings: list[str] = []
    all_blocking: list[str] = []
    for r in reports:
        all_issues.extend(r.issues)
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)

    if len(reports) == 1:
        r = reports[0]
        return DesignAssignmentRuntimeReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            assignment_runtime_status=r.assignment_runtime_status,
            assignment_plan=r.assignment_plan,
            assignment_candidates=r.assignment_candidates,
            unit_allocation_report=r.unit_allocation_report,
            cell_allocation_report=r.cell_allocation_report,
            constraint_report=r.constraint_report,
            constraint_trace=r.constraint_trace,
            exclusion_trace=r.exclusion_trace,
            reproducibility_manifest=r.reproducibility_manifest,
            failure_packet=r.failure_packet,
            design_reports=(r,),
            readiness_report=r.readiness_report,
            claim_boundary_report=r.claim_boundary_report,
            issues=r.issues,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
        )

    return DesignAssignmentRuntimeReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        assignment_runtime_status=None,
        design_reports=tuple(reports),
        aggregate_summary=f"Evaluated {len(reports)} assignment requests without ranking",
        claim_boundary_report=AssignmentClaimBoundaryReport(),
        issues=tuple(all_issues),
        warnings=tuple(dict.fromkeys(all_warnings)),
        blocking_reasons=tuple(dict.fromkeys(all_blocking)),
    )


generate_assignment_candidate = generate_design_assignment


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    smoke = {
        "design_id": "smoke_two_cell",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
            "design_cell_structure_status": "PASS",
            "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
            "assignment_feasibility_status": "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME",
            "method_suitability_status": "PASS",
        },
        "method_instrument_suitability_matrix": [{
            "instrument_id": "TBR_RIDGE_BRB",
            "suitability_status": "METHOD_FAMILY_ELIGIBLE_FOR_REVIEW",
        }],
        "assignment_unit_universe": [
            {"unit_id": "DMA_001", "geo_id": "G001", "eligible": True},
            {"unit_id": "DMA_002", "geo_id": "G002", "eligible": True},
            {"unit_id": "DMA_003", "geo_id": "G003", "eligible": True},
            {"unit_id": "DMA_004", "geo_id": "G004", "eligible": True},
        ],
        "eligible_unit_pools": {
            "C0": ["DMA_001", "DMA_002"],
            "T1": ["DMA_003", "DMA_004"],
        },
        "cell_requirements": [
            {"cell_id": "C0", "cell_role": "CONTROL", "required_unit_count": 2},
            {"cell_id": "T1", "cell_role": "TREATMENT", "required_unit_count": 2},
        ],
        "assignment_constraints": dict(_DEFAULT_CONSTRAINTS),
        "assignment_algorithm_spec": {"algorithm_category": "DETERMINISTIC_RULE_ASSIGNMENT"},
        "reproducibility_config": {
            "algorithm_version": "1.0.0",
            "constraint_version": "1.0.0",
            "seed_policy": "NOT_APPLICABLE_DETERMINISTIC",
            "config_hash": "smoke_config",
            "input_artifact_ids": ["SMOKE_INPUT"],
        },
    }
    report = generate_design_assignment(smoke)
    failed: list[str] = []
    if not report.assignment_candidates:
        failed.append("smoke_no_candidate")
    if report.claim_boundary_report.assignment_candidate_selected:
        failed.append("smoke_candidate_selected")
    if report.claim_boundary_report.matched_pairs_generated:
        failed.append("smoke_matched_pairs")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_assignment_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "deterministic_explicit_pool_assignment_only_no_matching_or_randomization",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
            "DESIGN_CELL_STRUCTURE_RUNTIME_001",
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
            "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001",
            "METHOD_SUITABILITY_RUNTIME_001",
            "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001",
        ],
        "public_api": "generate_design_assignment",
        "runtime_assignment_generation_implemented": True,
        "deterministic_explicit_pool_assignment_implemented": True,
        "assignment_plan_generated": True,
        "assignment_candidate_generated": True,
        "unit_allocation_generated": True,
        "geo_assignment_computed": True,
        "assignment_candidate_selected": False,
        "matched_pairs_generated": False,
        "blocks_generated": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "thinning_design_generated": False,
        "matching_optimization_computed": False,
        "balance_optimization_computed": False,
        "balance_diagnostics_computed": False,
        "interference_adjustment_computed": False,
        "scenario_policy_feasibility_computed": False,
        "assignment_feasibility_computed": False,
        "method_suitability_computed": False,
        "method_family_selected": False,
        "estimator_selected": False,
        "inference_method_selected": False,
        "method_promotion_authorized": False,
        "method_production_compatibility_authorized": False,
        "power_computed": False,
        "mde_computed": False,
        "p_value_computed": False,
        "confidence_interval_computed": False,
        "lift_computed": False,
        "roi_computed": False,
        "budget_optimization_authorized": False,
        "candidate_design_authorized": False,
        "treatment_control_assignment_authorized": False,
        "estimator_inference_authorized": False,
        "mmm_runtime_calls_implemented": False,
        "mmm_calibration_authorized": False,
        "production_authorization_granted": False,
        "llm_decisioning_authorized": False,
        "recommended_next_artifact": RECOMMENDED_NEXT_ARTIFACT,
        "alternative_next_artifact": ALTERNATIVE_NEXT_ARTIFACT,
        "failed_scenarios": failed,
        "smoke_runtime_status": report.assignment_runtime_status.value if report.assignment_runtime_status else None,
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
