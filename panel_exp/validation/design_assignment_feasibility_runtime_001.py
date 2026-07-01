"""DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001 conservative assignment-feasibility evaluation."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "design_assignment_feasibility_runtime_implemented_no_assignment_or_matching"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_ASSIGNMENT_FEASIBILITY_RUNTIME_001_summary.json"
)
RECOMMENDED_NEXT_ARTIFACT = "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_RUNTIME_CONTRACT_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "NOT_EVALUATED"})
_READY_TOKENS = frozenset({"PASS", "READY", "READY_FOR_DOWNSTREAM", "COMPLETE", "COMPLETED"})
_SCENARIO_BLOCKED_TOKENS = frozenset({"SCENARIO_BLOCKED", "BLOCKED"})
_SCENARIO_CONFLICT_TOKENS = frozenset({
    "SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT",
    "SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION",
    "CONTRAST_BLOCKED_BY_SHARED_CONTROL_CONFLICT",
    "COMMON_CONTROL_SPLIT_REQUIRED_FOR_CLEAN_ESTIMANDS",
})


class AssignmentFeasibilityStatus(str, Enum):
    ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME = "ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME"
    ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS = "ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS"
    ASSIGNMENT_FEASIBILITY_PROVISIONAL = "ASSIGNMENT_FEASIBILITY_PROVISIONAL"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DATA_READINESS = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DATA_READINESS"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_GEO_FEASIBILITY = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_GEO_FEASIBILITY"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DESIGN_STRUCTURE = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DESIGN_STRUCTURE"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_SCENARIO_POLICY = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_SCENARIO_POLICY"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_POWER_MDE_READINESS = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_POWER_MDE_READINESS"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS = (
        "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS"
    )
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY"
    ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CONSTRAINTS = "ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CONSTRAINTS"
    ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK = "ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK"
    ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW = (
        "ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW"
    )
    ASSIGNMENT_FEASIBILITY_NOT_EVALUATED = "ASSIGNMENT_FEASIBILITY_NOT_EVALUATED"


class AssignmentConstraintStatus(str, Enum):
    ASSIGNMENT_CONSTRAINT_SATISFIED = "ASSIGNMENT_CONSTRAINT_SATISFIED"
    ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS = "ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS"
    ASSIGNMENT_CONSTRAINT_PROVISIONAL = "ASSIGNMENT_CONSTRAINT_PROVISIONAL"
    ASSIGNMENT_CONSTRAINT_BLOCKING = "ASSIGNMENT_CONSTRAINT_BLOCKING"
    ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN = "ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN"
    ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT = "ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT"
    ASSIGNMENT_CONSTRAINT_NOT_EVALUATED = "ASSIGNMENT_CONSTRAINT_NOT_EVALUATED"


class AssignmentIssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"
    REQUIRES_USER_INPUT = "REQUIRES_USER_INPUT"
    REQUIRES_REDESIGN = "REQUIRES_REDESIGN"


@dataclass(frozen=True)
class DesignAssignmentFeasibilityConfig:
    block_power_mde_blocked: bool = False
    block_scenario_policy_blocked: bool = True
    missing_hierarchy_requires_user_input: bool = True
    missing_balance_covariates_requires_user_input: bool = False
    high_interference_is_blocking: bool = False
    unknown_interference_is_warning: bool = True
    allow_global_pool_for_cell_capacity: bool = True
    target_shortfall_is_blocking: bool = False
    prior_assignment_unavailable_by_default: bool = True


@dataclass(frozen=True)
class AssignmentIssue:
    code: str
    message: str
    severity: AssignmentIssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class AssignmentConstraintReport:
    category: str
    status: AssignmentConstraintStatus
    message: str
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class AssignmentReadinessReport:
    profiler_gate: str
    geo_feasibility_gate: str
    design_cell_structure_gate: str
    scenario_policy_feasibility_gate: str
    power_mde_readiness_gate: str
    assignment_unit_universe_gate: str
    cell_requirement_gate: str
    all_hard_gates_pass: bool
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentEligibilityReport:
    total_unit_count: int
    eligible_unit_count: int
    excluded_unit_count: int
    available_unit_count: int
    excluded_units: tuple[str, ...]
    unavailable_units: tuple[str, ...]
    eligible_units_without_required_metadata: tuple[str, ...]
    missing_unit_id_count: int


@dataclass(frozen=True)
class CellCapacityEntry:
    cell_id: str
    cell_role: str | None
    minimum_units: int | None
    maximum_units: int | None
    target_units: int | None
    eligible_unit_pool_count: int
    available_unit_pool_count: int
    capacity_status: AssignmentConstraintStatus
    capacity_gap: int | None
    capacity_warning: str | None


@dataclass(frozen=True)
class AssignmentCellCapacityReport:
    entries: tuple[CellCapacityEntry, ...]
    total_minimum_units_required: int
    any_capacity_blocking: bool
    used_global_pool_fallback: bool


@dataclass(frozen=True)
class AssignmentMutualExclusivityReport:
    mutual_exclusivity_required: bool
    declaration_present: bool
    status: AssignmentConstraintStatus
    prior_assigned_units: tuple[str, ...]
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentSharedControlReport:
    common_control_required: bool
    common_control_cells: tuple[str, ...]
    missing_cell_requirements: tuple[str, ...]
    capacity_met: bool
    scenario_shared_control_conflict: bool
    status: AssignmentConstraintStatus
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentSplitControlReport:
    split_control_required: bool
    scenario_recheck_required: bool
    status: AssignmentConstraintStatus
    control_cell_ids: tuple[str, ...]
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentHierarchyReport:
    geo_hierarchy_required: bool
    hierarchy_metadata_complete: bool
    status: AssignmentConstraintStatus
    units_missing_hierarchy: tuple[str, ...]
    business_unit_constraints: tuple[str, ...]
    region_country_constraints: tuple[str, ...]
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentMarketExclusionReport:
    market_exclusions_declared: bool
    excluded_markets: tuple[str, ...]
    excluded_unit_count: int
    status: AssignmentConstraintStatus
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentBalanceReadinessReport:
    balance_covariates_required: bool
    balance_covariates_present: bool
    covariates_available: tuple[str, ...]
    status: AssignmentConstraintStatus
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentInterferenceRiskReport:
    interference_risk_status: str | None
    high_risk_detected: bool
    unknown_risk_detected: bool
    status: AssignmentConstraintStatus
    issues: tuple[AssignmentIssue, ...] = ()


@dataclass(frozen=True)
class AssignmentScenarioHandoffReport:
    scenario_policy_feasibility_status: str | None
    scenario_blocked: bool
    scenario_shared_control_conflict: bool
    split_control_required: bool
    scenario_recheck_required: bool
    method_suitability_review_required: bool
    status: AssignmentConstraintStatus
    preserved_status: str | None


@dataclass(frozen=True)
class AssignmentPowerMdeHandoffReport:
    power_mde_status: str | None
    power_mde_blocked: bool
    power_ready_claim_allowed: bool
    preserved_status: str | None


@dataclass(frozen=True)
class AssignmentMethodSuitabilityHandoffReport:
    method_suitability_review_required: bool
    estimator_inference_ready: bool
    status: AssignmentConstraintStatus


@dataclass(frozen=True)
class AssignmentClaimBoundaryReport:
    runtime_assignment_feasibility_implemented: bool = True
    eligible_unit_counting_implemented: bool = True
    cell_capacity_evaluation_implemented: bool = True
    assignment_constraint_evaluation_implemented: bool = True
    common_control_capacity_check_implemented: bool = True
    split_control_recheck_detection_implemented: bool = True
    balance_readiness_reporting_implemented: bool = True
    interference_risk_reporting_implemented: bool = True
    geo_assignment_computed: bool = False
    matched_pairs_generated: bool = False
    blocks_generated: bool = False
    randomization_computed: bool = False
    rerandomization_computed: bool = False
    thinning_design_generated: bool = False
    matching_optimization_computed: bool = False
    balance_optimization_computed: bool = False
    interference_adjustment_computed: bool = False
    scenario_policy_feasibility_computed: bool = False
    runtime_scenario_enumeration_implemented: bool = False
    runtime_scenario_optimization_implemented: bool = False
    runtime_design_generation_implemented: bool = False
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
class DesignAssignmentFeasibilityCandidateReport:
    design_id: str
    assignment_feasibility_status: AssignmentFeasibilityStatus
    secondary_statuses: tuple[AssignmentFeasibilityStatus, ...]
    assignment_readiness_summary: str
    eligible_unit_count: int
    excluded_unit_count: int
    available_unit_count: int
    required_cell_count: int
    readiness_report: AssignmentReadinessReport
    eligibility_report: AssignmentEligibilityReport
    cell_capacity_reports: AssignmentCellCapacityReport
    constraint_reports: tuple[AssignmentConstraintReport, ...]
    mutual_exclusivity_report: AssignmentMutualExclusivityReport
    shared_control_report: AssignmentSharedControlReport
    split_control_report: AssignmentSplitControlReport
    hierarchy_report: AssignmentHierarchyReport
    market_exclusion_report: AssignmentMarketExclusionReport
    balance_readiness_report: AssignmentBalanceReadinessReport
    interference_risk_report: AssignmentInterferenceRiskReport
    scenario_handoff_report: AssignmentScenarioHandoffReport
    power_mde_handoff_report: AssignmentPowerMdeHandoffReport
    method_suitability_handoff_report: AssignmentMethodSuitabilityHandoffReport
    claim_boundary_report: AssignmentClaimBoundaryReport
    issues: tuple[AssignmentIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class DesignAssignmentFeasibilityReport:
    artifact_id: str
    design_id: str | None
    assignment_feasibility_status: AssignmentFeasibilityStatus | None
    secondary_statuses: tuple[AssignmentFeasibilityStatus, ...] = ()
    assignment_readiness_summary: str | None = None
    eligible_unit_count: int | None = None
    excluded_unit_count: int | None = None
    available_unit_count: int | None = None
    required_cell_count: int | None = None
    design_reports: tuple[DesignAssignmentFeasibilityCandidateReport, ...] = ()
    aggregate_summary: str | None = None
    cell_capacity_reports: AssignmentCellCapacityReport | None = None
    constraint_reports: tuple[AssignmentConstraintReport, ...] = ()
    mutual_exclusivity_report: AssignmentMutualExclusivityReport | None = None
    shared_control_report: AssignmentSharedControlReport | None = None
    split_control_report: AssignmentSplitControlReport | None = None
    hierarchy_report: AssignmentHierarchyReport | None = None
    market_exclusion_report: AssignmentMarketExclusionReport | None = None
    balance_readiness_report: AssignmentBalanceReadinessReport | None = None
    interference_risk_report: AssignmentInterferenceRiskReport | None = None
    scenario_handoff_report: AssignmentScenarioHandoffReport | None = None
    power_mde_handoff_report: AssignmentPowerMdeHandoffReport | None = None
    method_suitability_handoff_report: AssignmentMethodSuitabilityHandoffReport | None = None
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
    return bool(t) and (t in _BLOCKED_TOKENS or t.startswith("BLOCKED"))


def _is_ready(value: Any) -> bool:
    t = _token(value)
    return bool(t) and (t in _READY_TOKENS or "READY" in t or t == "PASS")


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_candidates(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        if input_data and all(isinstance(x, dict) for x in input_data):
            if "design_id" in input_data[0] or "assignment_units" in input_data[0]:
                return [dict(x) for x in input_data]
    data = _to_dict(input_data)
    if "candidates" in data and isinstance(data["candidates"], list):
        return [dict(c) for c in data["candidates"] if isinstance(c, dict)]
    if "assignment_units" in data or "design_id" in data:
        return [data]
    return [data] if data else [{"design_id": "design_unspecified"}]


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


def _unit_id(unit: dict[str, Any]) -> str | None:
    uid = unit.get("unit_id")
    return str(uid) if uid is not None else None


def _is_available_unit(unit: dict[str, Any], cfg: DesignAssignmentFeasibilityConfig) -> bool:
    if not unit.get("eligible", True):
        return False
    if not unit.get("available_for_assignment", True):
        return False
    if cfg.prior_assignment_unavailable_by_default and unit.get("prior_assignment_cell"):
        return False
    return _unit_id(unit) is not None


def _evaluate_eligibility(
    units: list[dict[str, Any]],
    cfg: DesignAssignmentFeasibilityConfig,
    issues: list[AssignmentIssue],
) -> AssignmentEligibilityReport:
    excluded: list[str] = []
    unavailable: list[str] = []
    missing_meta: list[str] = []
    missing_id_count = 0
    eligible_count = 0
    available_count = 0

    for unit in units:
        uid = _unit_id(unit)
        if uid is None:
            missing_id_count += 1
            issues.append(
                AssignmentIssue(
                    code="MISSING_UNIT_ID",
                    message="Assignment unit missing unit_id",
                    severity=AssignmentIssueSeverity.BLOCKING,
                    field="unit_id",
                )
            )
            continue

        if not unit.get("eligible", True):
            excluded.append(uid)
            continue

        eligible_count += 1

        if not unit.get("available_for_assignment", True):
            unavailable.append(uid)
            continue

        if cfg.prior_assignment_unavailable_by_default and unit.get("prior_assignment_cell"):
            unavailable.append(uid)
            continue

        available_count += 1

        if unit.get("eligible", True) and not unit.get("region") and not unit.get("hierarchy_path"):
            missing_meta.append(uid)

    return AssignmentEligibilityReport(
        total_unit_count=len(units),
        eligible_unit_count=eligible_count,
        excluded_unit_count=len(excluded),
        available_unit_count=available_count,
        excluded_units=tuple(excluded),
        unavailable_units=tuple(unavailable),
        eligible_units_without_required_metadata=tuple(missing_meta),
        missing_unit_id_count=missing_id_count,
    )


def _pool_for_cell(
    cell_req: dict[str, Any],
    units: list[dict[str, Any]],
    available_ids: set[str],
    global_available: int,
    cfg: DesignAssignmentFeasibilityConfig,
    warnings: list[str],
) -> tuple[int, int, bool]:
    pool = cell_req.get("eligible_unit_pool")
    if isinstance(pool, list) and pool:
        pool_ids = {str(u) for u in pool}
        eligible_pool = len(pool_ids)
        available_pool = len(pool_ids & available_ids)
        return eligible_pool, available_pool, False

    blocked = cell_req.get("blocked_unit_pool")
    if isinstance(blocked, list) and blocked:
        blocked_ids = {str(u) for u in blocked}
        available_pool = len(available_ids - blocked_ids)
        return len(available_ids), available_pool, False

    if cfg.allow_global_pool_for_cell_capacity:
        return global_available, global_available, True

    return 0, 0, False


def _evaluate_cell_capacity(
    cell_requirements: list[dict[str, Any]],
    units: list[dict[str, Any]],
    available_count: int,
    cfg: DesignAssignmentFeasibilityConfig,
    issues: list[AssignmentIssue],
    warnings: list[str],
) -> AssignmentCellCapacityReport:
    available_ids = {_unit_id(u) for u in units if _is_available_unit(u, cfg)}
    available_ids.discard(None)

    entries: list[CellCapacityEntry] = []
    total_min = 0
    any_blocking = False
    used_global_fallback = False

    for cell_req in cell_requirements:
        cell_id = str(cell_req.get("cell_id", "unknown"))
        minimum = _int_or_none(cell_req.get("minimum_units"))
        maximum = _int_or_none(cell_req.get("maximum_units"))
        target = _int_or_none(cell_req.get("target_units"))

        if minimum is not None:
            total_min += minimum

        elig_pool, avail_pool, global_fb = _pool_for_cell(
            cell_req, units, available_ids, available_count, cfg, warnings
        )
        if global_fb:
            used_global_fallback = True

        gap = (minimum - avail_pool) if minimum is not None else None
        cap_warning: str | None = None
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

        if maximum is not None and minimum is not None and maximum < minimum:
            any_blocking = True
            issues.append(
                AssignmentIssue(
                    code="CELL_MAX_BELOW_MIN",
                    message=f"Cell {cell_id}: maximum_units < minimum_units",
                    severity=AssignmentIssueSeverity.BLOCKING,
                    field="maximum_units",
                )
            )
            status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
            cap_warning = "maximum below minimum"
        elif minimum is not None and avail_pool < minimum:
            any_blocking = True
            status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
            issues.append(
                AssignmentIssue(
                    code="CELL_CAPACITY_BELOW_MINIMUM",
                    message=f"Cell {cell_id}: available pool {avail_pool} < minimum {minimum}",
                    severity=AssignmentIssueSeverity.BLOCKING,
                    field="minimum_units",
                )
            )
        elif target is not None and avail_pool < target:
            cap_warning = f"target_units {target} exceeds available pool {avail_pool}"
            if cfg.target_shortfall_is_blocking:
                any_blocking = True
                status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
                issues.append(
                    AssignmentIssue(
                        code="CELL_TARGET_SHORTFALL",
                        message=f"Cell {cell_id}: {cap_warning}",
                        severity=AssignmentIssueSeverity.BLOCKING,
                        field="target_units",
                    )
                )
            else:
                status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS
                warnings.append(cap_warning)

        entries.append(
            CellCapacityEntry(
                cell_id=cell_id,
                cell_role=str(cell_req.get("cell_role")) if cell_req.get("cell_role") else None,
                minimum_units=minimum,
                maximum_units=maximum,
                target_units=target,
                eligible_unit_pool_count=elig_pool,
                available_unit_pool_count=avail_pool,
                capacity_status=status,
                capacity_gap=gap,
                capacity_warning=cap_warning,
            )
        )

    if used_global_fallback:
        warnings.append("Using global available unit pool for cell capacity checks")

    return AssignmentCellCapacityReport(
        entries=tuple(entries),
        total_minimum_units_required=total_min,
        any_capacity_blocking=any_blocking,
        used_global_pool_fallback=used_global_fallback,
    )


def _evaluate_readiness(
    candidate: dict[str, Any],
    eligibility: AssignmentEligibilityReport,
    cell_count: int,
    issues: list[AssignmentIssue],
) -> AssignmentReadinessReport:
    upstream = candidate.get("upstream_statuses") or {}
    if not isinstance(upstream, dict):
        upstream = {}

    profiler = _gate_status(upstream.get("profiler_status"))
    geo = _gate_status(upstream.get("geo_feasibility_status"))
    design = _gate_status(upstream.get("design_cell_structure_status"))
    scenario = _gate_status(upstream.get("scenario_policy_feasibility_status"))
    power = _gate_status(upstream.get("power_mde_status"))

    units = candidate.get("assignment_units")
    if units is None:
        universe_gate = "BLOCKED"
        issues.append(
            AssignmentIssue(
                code="MISSING_ASSIGNMENT_UNIT_UNIVERSE",
                message="assignment_units universe is missing",
                severity=AssignmentIssueSeverity.BLOCKING,
                field="assignment_units",
            )
        )
    elif not isinstance(units, list) or len(units) == 0:
        universe_gate = "BLOCKED"
        issues.append(
            AssignmentIssue(
                code="EMPTY_ASSIGNMENT_UNIT_UNIVERSE",
                message="assignment_units universe is empty",
                severity=AssignmentIssueSeverity.BLOCKING,
                field="assignment_units",
            )
        )
    else:
        universe_gate = "PASS"

    cell_reqs = candidate.get("cell_requirements")
    if cell_reqs is None or (isinstance(cell_reqs, list) and len(cell_reqs) == 0):
        cell_gate = "BLOCKED"
        issues.append(
            AssignmentIssue(
                code="MISSING_CELL_REQUIREMENTS",
                message="cell_requirements are missing",
                severity=AssignmentIssueSeverity.BLOCKING,
                field="cell_requirements",
            )
        )
    else:
        cell_gate = "PASS"

    hard_pass = all(
        g == "PASS"
        for g in (profiler, geo, design, scenario, power, universe_gate, cell_gate)
        if g != "NOT_EVALUATED"
    ) and universe_gate == "PASS" and cell_gate == "PASS"

    return AssignmentReadinessReport(
        profiler_gate=profiler,
        geo_feasibility_gate=geo,
        design_cell_structure_gate=design,
        scenario_policy_feasibility_gate=scenario,
        power_mde_readiness_gate=power,
        assignment_unit_universe_gate=universe_gate,
        cell_requirement_gate=cell_gate,
        all_hard_gates_pass=hard_pass,
        issues=tuple(issues),
    )


def _evaluate_mutual_exclusivity(
    constraints: dict[str, Any],
    units: list[dict[str, Any]],
    cfg: DesignAssignmentFeasibilityConfig,
    issues: list[AssignmentIssue],
) -> AssignmentMutualExclusivityReport:
    required = bool(constraints.get("mutual_exclusivity_required", False))
    declared = bool(constraints.get("mutual_exclusivity_declared", False))
    prior_assigned = tuple(
        _unit_id(u) for u in units
        if u.get("prior_assignment_cell") and _unit_id(u)
    )

    if required and not declared:
        issues.append(
            AssignmentIssue(
                code="MUTUAL_EXCLUSIVITY_NOT_DECLARED",
                message="mutual exclusivity required but not declared",
                severity=AssignmentIssueSeverity.REQUIRES_USER_INPUT,
                field="mutual_exclusivity_required",
            )
        )
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT
    elif prior_assigned and cfg.prior_assignment_unavailable_by_default:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS
    else:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    return AssignmentMutualExclusivityReport(
        mutual_exclusivity_required=required,
        declaration_present=declared or not required,
        status=status,
        prior_assigned_units=prior_assigned,
        issues=tuple(i for i in issues if i.code.startswith("MUTUAL")),
    )


def _evaluate_shared_control(
    cell_requirements: list[dict[str, Any]],
    capacity: AssignmentCellCapacityReport,
    scenario_status: str | None,
    scenario_conflict: bool,
    issues: list[AssignmentIssue],
) -> AssignmentSharedControlReport:
    common_cells: list[str] = []
    missing_reqs: list[str] = []
    capacity_met = True

    cell_ids_with_req = {str(c.get("cell_id")) for c in cell_requirements if c.get("cell_id")}

    for cell_req in cell_requirements:
        if cell_req.get("requires_common_control") or cell_req.get("requires_bau_control"):
            cid = str(cell_req.get("cell_id", ""))
            common_cells.append(cid)

    for entry in capacity.entries:
        cell_req = next(
            (c for c in cell_requirements if str(c.get("cell_id")) == entry.cell_id),
            None,
        )
        if cell_req and (
            cell_req.get("requires_common_control") or cell_req.get("requires_bau_control")
        ):
            if entry.capacity_status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING:
                capacity_met = False

    for cid in common_cells:
        if cid not in cell_ids_with_req:
            missing_reqs.append(cid)

    if missing_reqs:
        issues.append(
            AssignmentIssue(
                code="COMMON_CONTROL_CELL_REQUIREMENT_MISSING",
                message=f"common control cell requirements missing: {', '.join(missing_reqs)}",
                severity=AssignmentIssueSeverity.WARNING,
            )
        )

    if scenario_conflict:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
    elif not capacity_met:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
    elif missing_reqs:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS
    else:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    return AssignmentSharedControlReport(
        common_control_required=bool(common_cells),
        common_control_cells=tuple(common_cells),
        missing_cell_requirements=tuple(missing_reqs),
        capacity_met=capacity_met,
        scenario_shared_control_conflict=scenario_conflict,
        status=status,
        issues=tuple(i for i in issues if "COMMON_CONTROL" in i.code),
    )


def _evaluate_split_control(
    upstream: dict[str, Any],
    cell_requirements: list[dict[str, Any]],
    issues: list[AssignmentIssue],
) -> AssignmentSplitControlReport:
    split_required = bool(upstream.get("split_control_required", False))
    recheck_required = bool(upstream.get("scenario_recheck_required", False))

    control_cells = tuple(
        str(c.get("cell_id"))
        for c in cell_requirements
        if c.get("requires_split_control") or c.get("cell_role") in (
            "CONTROL", "BUSINESS_AS_USUAL_CONTROL", "COMMON_CONTROL"
        )
    )

    if split_required or recheck_required:
        issues.append(
            AssignmentIssue(
                code="SPLIT_CONTROL_REDESIGN_REQUIRED",
                message="split-control redesign or scenario recheck required before assignment",
                severity=AssignmentIssueSeverity.REQUIRES_REDESIGN,
            )
        )
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN
    else:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    return AssignmentSplitControlReport(
        split_control_required=split_required,
        scenario_recheck_required=recheck_required,
        status=status,
        control_cell_ids=control_cells,
        issues=tuple(i for i in issues if i.code == "SPLIT_CONTROL_REDESIGN_REQUIRED"),
    )


def _evaluate_hierarchy_exclusion(
    constraints: dict[str, Any],
    units: list[dict[str, Any]],
    eligibility: AssignmentEligibilityReport,
    cfg: DesignAssignmentFeasibilityConfig,
    issues: list[AssignmentIssue],
) -> tuple[AssignmentHierarchyReport, AssignmentMarketExclusionReport]:
    hierarchy_required = bool(constraints.get("geo_hierarchy_required", False))
    missing_hierarchy: list[str] = []

    if hierarchy_required:
        for unit in units:
            uid = _unit_id(unit)
            if not uid or not unit.get("eligible", True):
                continue
            if not unit.get("hierarchy_path") and not unit.get("region"):
                missing_hierarchy.append(uid)

    if hierarchy_required and missing_hierarchy:
        sev = (
            AssignmentIssueSeverity.REQUIRES_USER_INPUT
            if cfg.missing_hierarchy_requires_user_input
            else AssignmentIssueSeverity.WARNING
        )
        issues.append(
            AssignmentIssue(
                code="MISSING_HIERARCHY_METADATA",
                message=f"hierarchy metadata missing for {len(missing_hierarchy)} units",
                severity=sev,
                field="hierarchy_path",
            )
        )
        hier_status = (
            AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT
            if cfg.missing_hierarchy_requires_user_input
            else AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
        )
    else:
        hier_status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    bu_constraints = constraints.get("business_unit_constraints")
    rc_constraints = constraints.get("region_country_constraints")
    bu_tuple = tuple(str(x) for x in bu_constraints) if isinstance(bu_constraints, list) else ()
    rc_tuple = tuple(str(x) for x in rc_constraints) if isinstance(rc_constraints, list) else ()

    hierarchy_report = AssignmentHierarchyReport(
        geo_hierarchy_required=hierarchy_required,
        hierarchy_metadata_complete=not missing_hierarchy,
        status=hier_status,
        units_missing_hierarchy=tuple(missing_hierarchy),
        business_unit_constraints=bu_tuple,
        region_country_constraints=rc_tuple,
        issues=tuple(i for i in issues if i.code == "MISSING_HIERARCHY_METADATA"),
    )

    exclusions = constraints.get("market_exclusions")
    excluded_markets: tuple[str, ...] = ()
    if isinstance(exclusions, list):
        excluded_markets = tuple(str(x) for x in exclusions)

    market_report = AssignmentMarketExclusionReport(
        market_exclusions_declared=bool(excluded_markets),
        excluded_markets=excluded_markets,
        excluded_unit_count=eligibility.excluded_unit_count,
        status=AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED,
        issues=(),
    )

    return hierarchy_report, market_report


def _evaluate_balance_readiness(
    candidate: dict[str, Any],
    constraints: dict[str, Any],
    cfg: DesignAssignmentFeasibilityConfig,
    issues: list[AssignmentIssue],
) -> AssignmentBalanceReadinessReport:
    required = bool(constraints.get("balance_covariates_required", False))
    covariates = candidate.get("balance_covariates")
    present = isinstance(covariates, list) and len(covariates) > 0
    cov_tuple = tuple(str(c) for c in covariates) if present else ()

    if required and not present:
        sev = (
            AssignmentIssueSeverity.REQUIRES_USER_INPUT
            if cfg.missing_balance_covariates_requires_user_input
            else AssignmentIssueSeverity.WARNING
        )
        issues.append(
            AssignmentIssue(
                code="MISSING_BALANCE_COVARIATES",
                message="balance covariates required but not provided",
                severity=sev,
                field="balance_covariates",
            )
        )
        status = (
            AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT
            if cfg.missing_balance_covariates_requires_user_input
            else AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
        )
    elif present:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED
    else:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    return AssignmentBalanceReadinessReport(
        balance_covariates_required=required,
        balance_covariates_present=present,
        covariates_available=cov_tuple,
        status=status,
        issues=tuple(i for i in issues if i.code == "MISSING_BALANCE_COVARIATES"),
    )


def _evaluate_interference_risk(
    candidate: dict[str, Any],
    constraints: dict[str, Any],
    cfg: DesignAssignmentFeasibilityConfig,
    issues: list[AssignmentIssue],
) -> AssignmentInterferenceRiskReport:
    risk_status = constraints.get("interference_risk_status")
    risks = candidate.get("interference_risks")
    token = _token(risk_status)

    high = token in ("HIGH", "BLOCKING", "SEVERE")
    unknown = token in ("UNKNOWN", "UNCHARACTERIZED") and not risks

    if high:
        sev = (
            AssignmentIssueSeverity.BLOCKING
            if cfg.high_interference_is_blocking
            else AssignmentIssueSeverity.WARNING
        )
        issues.append(
            AssignmentIssue(
                code="HIGH_INTERFERENCE_RISK",
                message="high interference risk flagged",
                severity=sev,
                field="interference_risk_status",
            )
        )
        status = (
            AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
            if cfg.high_interference_is_blocking
            else AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED_WITH_WARNINGS
        )
    elif unknown and cfg.unknown_interference_is_warning:
        issues.append(
            AssignmentIssue(
                code="UNKNOWN_INTERFERENCE_RISK",
                message="interference risk unknown or uncharacterized",
                severity=AssignmentIssueSeverity.WARNING,
                field="interference_risk_status",
            )
        )
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
    else:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    return AssignmentInterferenceRiskReport(
        interference_risk_status=str(risk_status) if risk_status else None,
        high_risk_detected=high,
        unknown_risk_detected=unknown,
        status=status,
        issues=tuple(
            i for i in issues if i.code in ("HIGH_INTERFERENCE_RISK", "UNKNOWN_INTERFERENCE_RISK")
        ),
    )


def _scenario_conflict(scenario_status: str | None) -> bool:
    t = _token(scenario_status)
    return t in _SCENARIO_BLOCKED_TOKENS or t in _SCENARIO_CONFLICT_TOKENS or "SHARED_CONTROL" in t


def _evaluate_scenario_handoff(
    upstream: dict[str, Any],
    candidate: dict[str, Any],
) -> AssignmentScenarioHandoffReport:
    scenario_status = upstream.get("scenario_policy_feasibility_status")
    if scenario_status is None:
        scenario_status = candidate.get("scenario_policy_status")

    t = _token(scenario_status)
    blocked = t in _SCENARIO_BLOCKED_TOKENS or t == "SCENARIO_BLOCKED"
    conflict = _scenario_conflict(str(scenario_status) if scenario_status else None)
    split_required = bool(upstream.get("split_control_required", False))
    recheck = bool(upstream.get("scenario_recheck_required", False))
    method_review = bool(
        upstream.get("method_suitability_review_required")
        or candidate.get("method_suitability_review_required", False)
    )

    if blocked:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
    elif conflict or split_required or recheck:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN
    else:
        status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED

    return AssignmentScenarioHandoffReport(
        scenario_policy_feasibility_status=str(scenario_status) if scenario_status else None,
        scenario_blocked=blocked,
        scenario_shared_control_conflict=conflict,
        split_control_required=split_required,
        scenario_recheck_required=recheck,
        method_suitability_review_required=method_review,
        status=status,
        preserved_status=str(scenario_status) if scenario_status else None,
    )


def _evaluate_power_mde_handoff(
    upstream: dict[str, Any],
    cfg: DesignAssignmentFeasibilityConfig,
) -> AssignmentPowerMdeHandoffReport:
    power_status = upstream.get("power_mde_status")
    blocked = _is_blocked(power_status)
    power_ready = not blocked or not cfg.block_power_mde_blocked

    return AssignmentPowerMdeHandoffReport(
        power_mde_status=str(power_status) if power_status else None,
        power_mde_blocked=blocked,
        power_ready_claim_allowed=power_ready,
        preserved_status=str(power_status) if power_status else None,
    )


def _evaluate_method_suitability_handoff(
    upstream: dict[str, Any],
    candidate: dict[str, Any],
) -> AssignmentMethodSuitabilityHandoffReport:
    required = bool(
        upstream.get("method_suitability_review_required")
        or candidate.get("method_suitability_review_required", False)
    )
    return AssignmentMethodSuitabilityHandoffReport(
        method_suitability_review_required=required,
        estimator_inference_ready=not required,
        status=AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED,
    )


def _select_status(
    readiness: AssignmentReadinessReport,
    eligibility: AssignmentEligibilityReport,
    capacity: AssignmentCellCapacityReport,
    scenario_handoff: AssignmentScenarioHandoffReport,
    power_handoff: AssignmentPowerMdeHandoffReport,
    split_control: AssignmentSplitControlReport,
    method_handoff: AssignmentMethodSuitabilityHandoffReport,
    hierarchy: AssignmentHierarchyReport,
    balance: AssignmentBalanceReadinessReport,
    interference: AssignmentInterferenceRiskReport,
    mutual: AssignmentMutualExclusivityReport,
    shared: AssignmentSharedControlReport,
    constraint_reports: list[AssignmentConstraintReport],
    issues: list[AssignmentIssue],
    warnings: list[str],
    cfg: DesignAssignmentFeasibilityConfig,
) -> tuple[AssignmentFeasibilityStatus, tuple[AssignmentFeasibilityStatus, ...], str]:
    secondary: list[AssignmentFeasibilityStatus] = []

    if readiness.profiler_gate == "BLOCKED":
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DATA_READINESS,
            (),
            "Blocked by profiler/data readiness",
        )

    if readiness.geo_feasibility_gate == "BLOCKED":
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_GEO_FEASIBILITY,
            (),
            "Blocked by geo unit/market feasibility",
        )

    if readiness.design_cell_structure_gate == "BLOCKED":
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_DESIGN_STRUCTURE,
            (),
            "Blocked by design cell structure",
        )

    if scenario_handoff.scenario_blocked:
        if cfg.block_scenario_policy_blocked:
            return (
                AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_SCENARIO_POLICY,
                (),
                "Blocked by scenario policy feasibility",
            )
        secondary.append(AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_PROVISIONAL)

    if power_handoff.power_mde_blocked and cfg.block_power_mde_blocked:
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_POWER_MDE_READINESS,
            tuple(secondary),
            "Blocked by power/MDE readiness",
        )
    if power_handoff.power_mde_blocked:
        secondary.append(AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_PROVISIONAL)

    if readiness.assignment_unit_universe_gate == "BLOCKED":
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS,
            tuple(secondary),
            "Blocked: missing or empty assignment unit universe",
        )

    if eligibility.available_unit_count == 0:
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS,
            tuple(secondary),
            "Blocked: no available eligible units",
        )

    if (
        capacity.total_minimum_units_required > 0
        and eligibility.available_unit_count < capacity.total_minimum_units_required
    ):
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_INSUFFICIENT_ELIGIBLE_UNITS,
            tuple(secondary),
            f"Blocked: {eligibility.available_unit_count} available units < {capacity.total_minimum_units_required} required minimum",
        )

    if capacity.any_capacity_blocking:
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CELL_CAPACITY,
            tuple(secondary),
            "Blocked by cell capacity requirements",
        )

    blocking_constraints = [
        r for r in constraint_reports
        if r.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
    ]
    if blocking_constraints or interference.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING:
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_BLOCKED_BY_CONSTRAINTS,
            tuple(secondary),
            "Blocked by assignment constraints",
        )

    if (
        split_control.split_control_required
        or split_control.scenario_recheck_required
        or split_control.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_REDESIGN
        or scenario_handoff.split_control_required
        or scenario_handoff.scenario_recheck_required
    ):
        sec = AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_REQUIRES_REDESIGN_RECHECK
        secondary.append(sec)
        return (
            sec,
            tuple(s for s in secondary if s != sec),
            "Requires split-control redesign or scenario recheck",
        )

    has_user_input = any(
        r.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT
        for r in constraint_reports
    ) or mutual.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_REQUIRES_USER_INPUT
    has_provisional = any(
        r.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
        for r in constraint_reports
    ) or hierarchy.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
    has_provisional = has_provisional or balance.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
    has_provisional = has_provisional or interference.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
    has_provisional = has_provisional or shared.status == AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
    has_warnings = bool(warnings) or any(
        i.severity in (AssignmentIssueSeverity.WARNING, AssignmentIssueSeverity.INFO)
        for i in issues
    )

    if method_handoff.method_suitability_review_required:
        sec = AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_REQUIRES_METHOD_SUITABILITY_REVIEW
        if not has_user_input and not has_provisional:
            return (
                sec,
                tuple(secondary),
                "Structurally feasible; method-suitability review required",
            )
        secondary.append(sec)

    if has_user_input or has_provisional:
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_PROVISIONAL,
            tuple(secondary),
            "Provisional: user input or incomplete constraint clarity",
        )

    if has_warnings or secondary:
        return (
            AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS,
            tuple(secondary),
            "Ready for future assignment runtime with warnings",
        )

    return (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME,
        tuple(secondary),
        "Ready for future assignment runtime",
    )


def _build_constraint_reports(
    hierarchy: AssignmentHierarchyReport,
    market: AssignmentMarketExclusionReport,
    balance: AssignmentBalanceReadinessReport,
    interference: AssignmentInterferenceRiskReport,
    mutual: AssignmentMutualExclusivityReport,
    shared: AssignmentSharedControlReport,
    split_control: AssignmentSplitControlReport,
    scenario: AssignmentScenarioHandoffReport,
    power: AssignmentPowerMdeHandoffReport,
    method: AssignmentMethodSuitabilityHandoffReport,
    capacity: AssignmentCellCapacityReport,
    cfg: DesignAssignmentFeasibilityConfig,
) -> tuple[AssignmentConstraintReport, ...]:
    scenario_status = scenario.status
    if scenario.scenario_blocked and not cfg.block_scenario_policy_blocked:
        scenario_status = AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL

    power_status = (
        AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING
        if power.power_mde_blocked and cfg.block_power_mde_blocked
        else (
            AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_PROVISIONAL
            if power.power_mde_blocked
            else AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED
        )
    )

    method_status = (
        AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_SATISFIED
        if method.method_suitability_review_required
        else method.status
    )

    reports = [
        AssignmentConstraintReport("GEO_HIERARCHY_CONSTRAINT", hierarchy.status, "geo hierarchy readiness"),
        AssignmentConstraintReport("MARKET_EXCLUSION_CONSTRAINT", market.status, "market exclusion preservation"),
        AssignmentConstraintReport("BALANCE_READINESS_CONSTRAINT", balance.status, "balance covariate readiness"),
        AssignmentConstraintReport("INTERFERENCE_RISK_CONSTRAINT", interference.status, "interference risk flag"),
        AssignmentConstraintReport("MUTUAL_EXCLUSIVITY_CONSTRAINT", mutual.status, "mutual exclusivity declaration"),
        AssignmentConstraintReport("COMMON_CONTROL_CONSTRAINT", shared.status, "common-control capacity"),
        AssignmentConstraintReport("SPLIT_CONTROL_REDESIGN_CONSTRAINT", split_control.status, "split-control redesign"),
        AssignmentConstraintReport("SCENARIO_POLICY_CONSTRAINT", scenario_status, "scenario policy handoff"),
        AssignmentConstraintReport("POWER_MDE_READINESS_CONSTRAINT", power_status, "power/MDE readiness handoff"),
        AssignmentConstraintReport("METHOD_SUITABILITY_CONSTRAINT", method_status, "method suitability handoff"),
    ]
    if capacity.any_capacity_blocking:
        reports.append(
            AssignmentConstraintReport(
                "CELL_CAPACITY_CONSTRAINT",
                AssignmentConstraintStatus.ASSIGNMENT_CONSTRAINT_BLOCKING,
                "cell capacity below minimum",
            )
        )
    return tuple(reports)


def _evaluate_single_candidate(
    candidate: dict[str, Any],
    cfg: DesignAssignmentFeasibilityConfig,
) -> DesignAssignmentFeasibilityCandidateReport:
    design_id = str(candidate.get("design_id", "design_unspecified"))
    issues: list[AssignmentIssue] = []
    warnings: list[str] = []

    upstream = candidate.get("upstream_statuses") or {}
    if not isinstance(upstream, dict):
        upstream = {}

    constraints = candidate.get("constraints") or {}
    if not isinstance(constraints, dict):
        constraints = {}

    units_raw = candidate.get("assignment_units")
    units: list[dict[str, Any]] = (
        [dict(u) for u in units_raw if isinstance(u, dict)] if isinstance(units_raw, list) else []
    )

    cell_reqs_raw = candidate.get("cell_requirements")
    cell_requirements: list[dict[str, Any]] = (
        [dict(c) for c in cell_reqs_raw if isinstance(c, dict)]
        if isinstance(cell_reqs_raw, list)
        else []
    )

    readiness_issues: list[AssignmentIssue] = []
    readiness = _evaluate_readiness(candidate, AssignmentEligibilityReport(
        0, 0, 0, 0, (), (), (), 0
    ), len(cell_requirements), readiness_issues)
    issues.extend(readiness_issues)

    eligibility = _evaluate_eligibility(units, cfg, issues)
    capacity = _evaluate_cell_capacity(
        cell_requirements, units, eligibility.available_unit_count, cfg, issues, warnings
    )

    mutual = _evaluate_mutual_exclusivity(constraints, units, cfg, issues)
    scenario_handoff = _evaluate_scenario_handoff(upstream, candidate)
    power_handoff = _evaluate_power_mde_handoff(upstream, cfg)
    split_control = _evaluate_split_control(upstream, cell_requirements, issues)
    hierarchy, market = _evaluate_hierarchy_exclusion(constraints, units, eligibility, cfg, issues)
    balance = _evaluate_balance_readiness(candidate, constraints, cfg, issues)
    interference = _evaluate_interference_risk(candidate, constraints, cfg, issues)
    shared = _evaluate_shared_control(
        cell_requirements, capacity, scenario_handoff.scenario_policy_feasibility_status,
        scenario_handoff.scenario_shared_control_conflict, issues,
    )
    method_handoff = _evaluate_method_suitability_handoff(upstream, candidate)

    constraint_reports = list(_build_constraint_reports(
        hierarchy, market, balance, interference, mutual, shared, split_control,
        scenario_handoff, power_handoff, method_handoff, capacity, cfg,
    ))

    status, secondary, summary = _select_status(
        readiness, eligibility, capacity, scenario_handoff, power_handoff,
        split_control, method_handoff, hierarchy, balance, interference,
        mutual, shared, constraint_reports, issues, warnings, cfg,
    )

    blocking_reasons = tuple(
        i.message for i in issues
        if i.severity in (AssignmentIssueSeverity.BLOCKING, AssignmentIssueSeverity.REQUIRES_REDESIGN)
    )

    return DesignAssignmentFeasibilityCandidateReport(
        design_id=design_id,
        assignment_feasibility_status=status,
        secondary_statuses=secondary,
        assignment_readiness_summary=summary,
        eligible_unit_count=eligibility.eligible_unit_count,
        excluded_unit_count=eligibility.excluded_unit_count,
        available_unit_count=eligibility.available_unit_count,
        required_cell_count=len(cell_requirements),
        readiness_report=readiness,
        eligibility_report=eligibility,
        cell_capacity_reports=capacity,
        constraint_reports=tuple(constraint_reports),
        mutual_exclusivity_report=mutual,
        shared_control_report=shared,
        split_control_report=split_control,
        hierarchy_report=hierarchy,
        market_exclusion_report=market,
        balance_readiness_report=balance,
        interference_risk_report=interference,
        scenario_handoff_report=scenario_handoff,
        power_mde_handoff_report=power_handoff,
        method_suitability_handoff_report=method_handoff,
        claim_boundary_report=AssignmentClaimBoundaryReport(),
        issues=tuple(issues),
        warnings=tuple(dict.fromkeys(warnings)),
        blocking_reasons=blocking_reasons,
    )


def evaluate_design_assignment_feasibility(
    input_data: Any,
    config: DesignAssignmentFeasibilityConfig | None = None,
) -> DesignAssignmentFeasibilityReport:
    """Evaluate assignment feasibility. Does not assign units or compute scenario policy feasibility."""
    cfg = config or DesignAssignmentFeasibilityConfig()
    candidates = _normalize_candidates(input_data)
    reports = [_evaluate_single_candidate(c, cfg) for c in candidates]

    all_issues: list[AssignmentIssue] = []
    all_warnings: list[str] = []
    all_blocking: list[str] = []
    for r in reports:
        all_issues.extend(r.issues)
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)

    if len(reports) == 1:
        r = reports[0]
        return DesignAssignmentFeasibilityReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            assignment_feasibility_status=r.assignment_feasibility_status,
            secondary_statuses=r.secondary_statuses,
            assignment_readiness_summary=r.assignment_readiness_summary,
            eligible_unit_count=r.eligible_unit_count,
            excluded_unit_count=r.excluded_unit_count,
            available_unit_count=r.available_unit_count,
            required_cell_count=r.required_cell_count,
            design_reports=(r,),
            aggregate_summary=None,
            cell_capacity_reports=r.cell_capacity_reports,
            constraint_reports=r.constraint_reports,
            mutual_exclusivity_report=r.mutual_exclusivity_report,
            shared_control_report=r.shared_control_report,
            split_control_report=r.split_control_report,
            hierarchy_report=r.hierarchy_report,
            market_exclusion_report=r.market_exclusion_report,
            balance_readiness_report=r.balance_readiness_report,
            interference_risk_report=r.interference_risk_report,
            scenario_handoff_report=r.scenario_handoff_report,
            power_mde_handoff_report=r.power_mde_handoff_report,
            method_suitability_handoff_report=r.method_suitability_handoff_report,
            claim_boundary_report=r.claim_boundary_report,
            issues=r.issues,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
        )

    return DesignAssignmentFeasibilityReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        assignment_feasibility_status=None,
        design_reports=tuple(reports),
        aggregate_summary=f"Evaluated {len(reports)} assignment-feasibility candidates without ranking",
        claim_boundary_report=AssignmentClaimBoundaryReport(),
        issues=tuple(all_issues),
        warnings=tuple(dict.fromkeys(all_warnings)),
        blocking_reasons=tuple(dict.fromkeys(all_blocking)),
    )


evaluate_assignment_feasibility = evaluate_design_assignment_feasibility


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    candidate = {
        "design_id": "smoke_two_cell",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "design_cell_structure_status": "PASS",
            "scenario_policy_feasibility_status": "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE",
            "power_mde_status": "PASS",
        },
        "assignment_units": [
            {"unit_id": f"U{i}", "geo_id": f"G{i}", "eligible": True, "available_for_assignment": True}
            for i in range(30)
        ],
        "cell_requirements": [
            {"cell_id": "T1", "cell_role": "TEST_CELL", "minimum_units": 10, "maximum_units": 20},
            {"cell_id": "C0", "cell_role": "BUSINESS_AS_USUAL_CONTROL", "minimum_units": 10, "maximum_units": 20},
        ],
        "constraints": {"mutual_exclusivity_required": True, "mutual_exclusivity_declared": True},
        "balance_covariates": ["spend", "kpi"],
    }
    report = evaluate_design_assignment_feasibility(candidate)
    failed: list[str] = []
    if report.assignment_feasibility_status not in (
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_FOR_RUNTIME,
        AssignmentFeasibilityStatus.ASSIGNMENT_FEASIBILITY_READY_WITH_WARNINGS,
    ):
        failed.append("smoke_status")
    if report.claim_boundary_report.geo_assignment_computed:
        failed.append("smoke_no_geo_assignment")
    if report.claim_boundary_report.scenario_policy_feasibility_computed:
        failed.append("smoke_no_scenario_feasibility")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_assignment_feasibility_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "runtime_evaluates_assignment_feasibility_no_assignment_or_matching",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
            "DESIGN_CELL_STRUCTURE_RUNTIME_001",
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
            "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001",
        ],
        "public_api": "evaluate_design_assignment_feasibility",
        "runtime_assignment_feasibility_implemented": True,
        "eligible_unit_counting_implemented": True,
        "cell_capacity_evaluation_implemented": True,
        "assignment_constraint_evaluation_implemented": True,
        "common_control_capacity_check_implemented": True,
        "split_control_recheck_detection_implemented": True,
        "balance_readiness_reporting_implemented": True,
        "interference_risk_reporting_implemented": True,
        "geo_assignment_computed": False,
        "matched_pairs_generated": False,
        "blocks_generated": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "thinning_design_generated": False,
        "matching_optimization_computed": False,
        "balance_optimization_computed": False,
        "interference_adjustment_computed": False,
        "scenario_policy_feasibility_computed": False,
        "runtime_scenario_enumeration_implemented": False,
        "runtime_scenario_optimization_implemented": False,
        "runtime_design_generation_implemented": False,
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
        "smoke_assignment_feasibility_status": (
            report.assignment_feasibility_status.value if report.assignment_feasibility_status else None
        ),
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
