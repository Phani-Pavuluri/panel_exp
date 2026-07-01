"""DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001 conservative provided-scenario evaluation."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "design_scenario_policy_feasibility_runtime_implemented_for_provided_scenarios_no_enumeration_or_optimization"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001_summary.json"
)
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_CELL_STRUCTURE_RUNTIME_001"
ALTERNATIVE_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "NOT_EVALUATED"})
_READY_TOKENS = frozenset({"PASS", "READY", "READY_FOR_DOWNSTREAM", "COMPLETE", "COMPLETED"})

_BAU_POLICIES = frozenset(
    {
        "BAU",
        "BUSINESS_AS_USUAL",
        "BUSINESS_AS_USUAL_CONTROL",
    }
)


class ScenarioFeasibilityStatus(str, Enum):
    SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE = "SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE"
    SCENARIO_PARTIALLY_FEASIBLE = "SCENARIO_PARTIALLY_FEASIBLE"
    SCENARIO_REQUIRES_ESTIMAND_SHIFT = "SCENARIO_REQUIRES_ESTIMAND_SHIFT"
    SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION = "SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION"
    SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT = "SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT"
    SCENARIO_REQUIRES_POWER_MDE_RECHECK = "SCENARIO_REQUIRES_POWER_MDE_RECHECK"
    SCENARIO_REQUIRES_ASSIGNMENT_RECHECK = "SCENARIO_REQUIRES_ASSIGNMENT_RECHECK"
    SCENARIO_REQUIRES_METHOD_SUITABILITY_REVIEW = "SCENARIO_REQUIRES_METHOD_SUITABILITY_REVIEW"
    SCENARIO_OUT_OF_HISTORICAL_SUPPORT = "SCENARIO_OUT_OF_HISTORICAL_SUPPORT"
    SCENARIO_BLOCKED = "SCENARIO_BLOCKED"
    SCENARIO_NOT_EVALUATED = "SCENARIO_NOT_EVALUATED"


class ContrastFeasibilityStatus(str, Enum):
    CONTRAST_FEASIBLE = "CONTRAST_FEASIBLE"
    CONTRAST_PARTIALLY_FEASIBLE = "CONTRAST_PARTIALLY_FEASIBLE"
    CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL = "CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL"
    CONTRAST_OUT_OF_HISTORICAL_SUPPORT = "CONTRAST_OUT_OF_HISTORICAL_SUPPORT"
    CONTRAST_REQUIRES_ESTIMAND_SHIFT = "CONTRAST_REQUIRES_ESTIMAND_SHIFT"
    CONTRAST_BLOCKED_BY_SHARED_CONTROL_CONFLICT = "CONTRAST_BLOCKED_BY_SHARED_CONTROL_CONFLICT"
    CONTRAST_REQUIRES_POWER_MDE_RECHECK = "CONTRAST_REQUIRES_POWER_MDE_RECHECK"
    CONTRAST_REQUIRES_ASSIGNMENT_RECHECK = "CONTRAST_REQUIRES_ASSIGNMENT_RECHECK"
    CONTRAST_REQUIRES_METHOD_SUITABILITY_REVIEW = "CONTRAST_REQUIRES_METHOD_SUITABILITY_REVIEW"
    CONTRAST_BLOCKED = "CONTRAST_BLOCKED"
    CONTRAST_NOT_EVALUATED = "CONTRAST_NOT_EVALUATED"


class PolicySupportStatus(str, Enum):
    POLICY_WITHIN_HISTORICAL_SUPPORT = "POLICY_WITHIN_HISTORICAL_SUPPORT"
    POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY = "POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY"
    POLICY_OUT_OF_HISTORICAL_SUPPORT = "POLICY_OUT_OF_HISTORICAL_SUPPORT"
    POLICY_BELOW_HISTORICAL_SUPPORT = "POLICY_BELOW_HISTORICAL_SUPPORT"
    POLICY_REQUIRES_BUSINESS_OVERRIDE = "POLICY_REQUIRES_BUSINESS_OVERRIDE"
    POLICY_SUPPORT_UNKNOWN = "POLICY_SUPPORT_UNKNOWN"
    POLICY_NOT_EVALUATED = "POLICY_NOT_EVALUATED"


class SharedControlConflictType(str, Enum):
    NO_SHARED_CONTROL_CONFLICT = "NO_SHARED_CONTROL_CONFLICT"
    COMMON_CONTROL_MANIPULATED = "COMMON_CONTROL_MANIPULATED"
    BAU_CONTROL_NOT_PRESERVED = "BAU_CONTROL_NOT_PRESERVED"
    COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER = (
        "COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER"
    )
    COMMON_CONTROL_INSUFFICIENT_FOR_ONE_OR_MORE_CONTRASTS = (
        "COMMON_CONTROL_INSUFFICIENT_FOR_ONE_OR_MORE_CONTRASTS"
    )
    COMMON_CONTROL_OUT_OF_HISTORICAL_SUPPORT = "COMMON_CONTROL_OUT_OF_HISTORICAL_SUPPORT"
    COMMON_CONTROL_SPLIT_REQUIRED_FOR_CLEAN_ESTIMANDS = (
        "COMMON_CONTROL_SPLIT_REQUIRED_FOR_CLEAN_ESTIMANDS"
    )
    COMMON_CONTROL_ROLE_AMBIGUOUS = "COMMON_CONTROL_ROLE_AMBIGUOUS"


class ResolutionOptionType(str, Enum):
    EXTEND_DURATION = "EXTEND_DURATION"
    RELAX_MDE_TARGET = "RELAX_MDE_TARGET"
    CHANGE_TEST_POLICY_TO_HEAVY_UP = "CHANGE_TEST_POLICY_TO_HEAVY_UP"
    CHANGE_TEST_POLICY_TO_GO_DARK = "CHANGE_TEST_POLICY_TO_GO_DARK"
    REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY = "REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY"
    CAP_SPEND_WITHIN_HISTORICAL_SUPPORT = "CAP_SPEND_WITHIN_HISTORICAL_SUPPORT"
    SPLIT_COMMON_CONTROL = "SPLIT_COMMON_CONTROL"
    ADD_OR_REALLOCATE_CELLS = "ADD_OR_REALLOCATE_CELLS"
    DROP_CONTRAST = "DROP_CONTRAST"
    SEQUENCE_TESTS = "SEQUENCE_TESTS"
    RERUN_POWER_MDE = "RERUN_POWER_MDE"
    RERUN_ASSIGNMENT_FEASIBILITY = "RERUN_ASSIGNMENT_FEASIBILITY"
    REQUIRE_METHOD_SUITABILITY_REVIEW = "REQUIRE_METHOD_SUITABILITY_REVIEW"
    BUSINESS_OVERRIDE_REQUIRED = "BUSINESS_OVERRIDE_REQUIRED"
    BLOCK_SCENARIO = "BLOCK_SCENARIO"


class GateStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    NOT_EVALUATED = "NOT_EVALUATED"
    PROVISIONAL = "PROVISIONAL"


class IssueSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class DesignScenarioPolicyFeasibilityConfig:
    near_historical_boundary_ratio: float = 0.95
    block_out_of_support: bool = False
    require_business_override_for_out_of_support: bool = True
    bau_spend_tolerance: float = 0.0
    block_when_none_feasible: bool = False


@dataclass(frozen=True)
class ScenarioIssue:
    code: str
    message: str
    severity: IssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class ScenarioReadinessReport:
    profiler_gate: GateStatus
    geo_unit_market_feasibility_gate: GateStatus
    spend_feasibility_gate: GateStatus
    power_mde_readiness_gate: GateStatus
    design_cell_structure_gate: GateStatus
    contrast_requirement_gate: GateStatus
    scenario_policy_plan_gate: GateStatus
    spend_compatible_feasibility_allowed: bool
    power_ready_feasibility_allowed: bool
    issues: tuple[ScenarioIssue, ...] = ()


@dataclass(frozen=True)
class CellPolicyReport:
    cell_id: str
    cell_role: str | None
    baseline_spend: float | None
    proposed_spend: float | None
    policy: str | None
    is_common_control: bool
    is_bau_policy: bool


@dataclass(frozen=True)
class ScenarioPolicyPlanReport:
    cells: tuple[CellPolicyReport, ...]


@dataclass(frozen=True)
class ContrastFeasibilityReport:
    contrast_id: str
    contrast_type: str | None
    treatment_cell_id: str | None
    comparison_cell_id: str | None
    required_spend_contrast: float | None
    achieved_spend_contrast: float | None
    spend_contrast_gap: float | None
    contrast_status: ContrastFeasibilityStatus
    bau_control_required: bool
    bau_control_preserved: bool | None
    response_bridge_source: str | None
    business_response_risk: bool
    method_suitability_review_required: bool
    issues: tuple[ScenarioIssue, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequiredVsAchievedSpendContrastEntry:
    contrast_id: str
    required_spend_contrast: float | None
    achieved_spend_contrast: float | None
    spend_contrast_gap: float | None
    meets_required: bool | None


@dataclass(frozen=True)
class HistoricalSupportCellReport:
    cell_id: str
    baseline_spend: float | None
    proposed_spend: float | None
    historical_p90: float | None
    historical_p95: float | None
    historical_max: float | None
    support_status: PolicySupportStatus
    distance_to_historical_max: float | None
    support_warning: str | None


@dataclass(frozen=True)
class SharedControlConflictEntry:
    conflict_type: SharedControlConflictType
    control_cell_id: str | None
    contrast_ids: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class EstimandShiftReport:
    estimand_shift_required: bool
    bau_control_preserved: bool | None
    dosage_contrast_required: bool
    difference_in_policy_required: bool
    method_suitability_review_required: bool
    flags: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResolutionOption:
    option_type: ResolutionOptionType
    category: str
    message: str
    requires_recheck: bool = False


@dataclass(frozen=True)
class ScenarioRecheckRequirement:
    requirement_type: str
    message: str


@dataclass(frozen=True)
class ScenarioClaimBoundaryReport:
    runtime_scenario_feasibility_implemented: bool = True
    provided_scenario_evaluation_implemented: bool = True
    required_vs_achieved_spend_contrast_implemented: bool = True
    shared_control_conflict_detection_implemented: bool = True
    historical_support_evaluation_implemented: bool = True
    resolution_option_emission_implemented: bool = True
    runtime_scenario_enumeration_implemented: bool = False
    runtime_scenario_optimization_implemented: bool = False
    runtime_design_generation_implemented: bool = False
    geo_assignment_computed: bool = False
    randomization_computed: bool = False
    rerandomization_computed: bool = False
    matching_optimization_computed: bool = False
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
class ScenarioFeasibilityReport:
    scenario_id: str
    scenario_status: ScenarioFeasibilityStatus
    secondary_statuses: tuple[ScenarioFeasibilityStatus, ...]
    overall_feasibility_summary: str
    readiness_report: ScenarioReadinessReport
    cell_policy_plan: ScenarioPolicyPlanReport
    contrast_feasibility_reports: tuple[ContrastFeasibilityReport, ...]
    required_vs_achieved_spend_contrast_by_contrast: tuple[RequiredVsAchievedSpendContrastEntry, ...]
    historical_support_by_cell: tuple[HistoricalSupportCellReport, ...]
    shared_control_conflicts: tuple[SharedControlConflictEntry, ...]
    estimand_shift_report: EstimandShiftReport
    resolution_options: tuple[ScenarioResolutionOption, ...]
    recheck_requirements: tuple[ScenarioRecheckRequirement, ...]
    claim_boundary_report: ScenarioClaimBoundaryReport
    issues: tuple[ScenarioIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class DesignScenarioPolicyFeasibilityReport:
    artifact_id: str
    scenario_id: str | None
    scenario_status: ScenarioFeasibilityStatus | None
    secondary_statuses: tuple[ScenarioFeasibilityStatus, ...]
    overall_feasibility_summary: str
    scenario_reports: tuple[ScenarioFeasibilityReport, ...]
    aggregate_summary: str | None
    cell_policy_plan: ScenarioPolicyPlanReport | None
    contrast_feasibility_reports: tuple[ContrastFeasibilityReport, ...]
    required_vs_achieved_spend_contrast_by_contrast: tuple[RequiredVsAchievedSpendContrastEntry, ...]
    historical_support_by_cell: tuple[HistoricalSupportCellReport, ...]
    shared_control_conflicts: tuple[SharedControlConflictEntry, ...]
    estimand_shift_flags: tuple[str, ...]
    estimand_shift_report: EstimandShiftReport | None
    resolution_options: tuple[ScenarioResolutionOption, ...]
    recheck_requirements: tuple[ScenarioRecheckRequirement, ...]
    claim_boundary_report: ScenarioClaimBoundaryReport
    issues: tuple[ScenarioIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    final_verdict: str = _VERDICT


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: getattr(obj, f.name) for f in fields(obj)}
    return {}


def _status_token(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _is_blocked_status(value: str | None) -> bool:
    token = _status_token(value)
    if not token:
        return False
    if token in _BLOCKED_TOKENS:
        return True
    return token.startswith("BLOCKED")


def _is_ready_status(value: str | None) -> bool:
    token = _status_token(value)
    if not token:
        return False
    if token in _READY_TOKENS:
        return True
    return "READY" in token or token == "PASS"


def _num(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def _is_bau_policy(policy: str | None, is_bau_flag: bool) -> bool:
    if is_bau_flag:
        return True
    if policy is None:
        return False
    return policy.strip().upper() in _BAU_POLICIES or "BAU" in policy.strip().upper()


def _bau_preserved(
    baseline: float | None,
    proposed: float | None,
    policy: str | None,
    is_bau_flag: bool,
    tolerance: float,
) -> bool | None:
    if baseline is None or proposed is None:
        return None
    if not _is_bau_policy(policy, is_bau_flag):
        return False
    return abs(proposed - baseline) <= tolerance


def _cell_index(cells: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for cell in cells:
        cid = cell.get("cell_id")
        if cid is not None:
            out[str(cid)] = cell
    return out


def _contrast_cell_ids(contrast: dict[str, Any]) -> tuple[str | None, str | None]:
    treatment = contrast.get("treatment_cell_id") or contrast.get("left_cell_id")
    comparison = contrast.get("comparison_cell_id") or contrast.get("right_cell_id")
    return (
        str(treatment) if treatment is not None else None,
        str(comparison) if comparison is not None else None,
    )


def _compute_achieved_contrast(
    contrast_type: str | None,
    treatment: dict[str, Any] | None,
    comparison: dict[str, Any] | None,
) -> float | None:
    if treatment is None or comparison is None:
        return None
    t_spend = _num(treatment.get("proposed_spend"))
    c_spend = _num(comparison.get("proposed_spend"))
    if t_spend is None or c_spend is None:
        return None
    ctype = (contrast_type or "UNKNOWN").upper()
    if ctype in {"GO_DARK_VS_BAU", "GO_DARK"}:
        return c_spend - t_spend
    if ctype in {"HEAVY_UP_VS_BAU", "HEAVY_UP", "MULTI_CELL_COMMON_CONTROL_CONTRAST"}:
        return t_spend - c_spend
    if ctype in {"DOSAGE_LOW_VS_HIGH", "DOSAGE_CONTRAST"}:
        low = min(t_spend, c_spend)
        high = max(t_spend, c_spend)
        return high - low
    if ctype in {"DIFFERENCE_IN_POLICY", "DIFFERENCE_IN_POLICY_CONTRAST"}:
        return abs(t_spend - c_spend)
    if ctype in {"BUDGET_REALLOCATION_SOURCE_VS_DESTINATION", "BUDGET_REALLOCATION"}:
        source_policy = str(treatment.get("policy") or "").upper()
        dest_policy = str(comparison.get("policy") or "").upper()
        if "SOURCE" in source_policy or "REDUCTION" in source_policy:
            return c_spend - t_spend
        if "DESTINATION" in dest_policy or "INCREASE" in dest_policy:
            return c_spend - t_spend
        return abs(t_spend - c_spend)
    if ctype == "GO_LIVE_VS_NO_OR_LOW_SPEND":
        return t_spend - c_spend
    if ctype == "UNKNOWN":
        return None
    return abs(t_spend - c_spend)


def _evaluate_historical_support(
    cell: dict[str, Any],
    cfg: DesignScenarioPolicyFeasibilityConfig,
) -> HistoricalSupportCellReport:
    cid = str(cell.get("cell_id", ""))
    baseline = _num(cell.get("baseline_spend"))
    proposed = _num(cell.get("proposed_spend"))
    p90 = _num(cell.get("historical_p90"))
    p95 = _num(cell.get("historical_p95"))
    hmax = _num(cell.get("historical_max"))
    distance: float | None = None
    warning: str | None = None

    if proposed is None:
        status = PolicySupportStatus.POLICY_NOT_EVALUATED
    elif hmax is None and p95 is None and p90 is None:
        status = PolicySupportStatus.POLICY_SUPPORT_UNKNOWN
    else:
        ref_max = hmax if hmax is not None else (p95 if p95 is not None else p90)
        assert ref_max is not None
        distance = proposed - ref_max
        boundary_threshold = ref_max * cfg.near_historical_boundary_ratio
        if proposed > ref_max:
            status = PolicySupportStatus.POLICY_OUT_OF_HISTORICAL_SUPPORT
            warning = f"Proposed spend {proposed} exceeds historical max {ref_max}"
            if cfg.require_business_override_for_out_of_support:
                status = PolicySupportStatus.POLICY_REQUIRES_BUSINESS_OVERRIDE
        elif proposed >= boundary_threshold:
            status = PolicySupportStatus.POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY
            warning = f"Proposed spend {proposed} near historical boundary {ref_max}"
        else:
            status = PolicySupportStatus.POLICY_WITHIN_HISTORICAL_SUPPORT

    return HistoricalSupportCellReport(
        cell_id=cid,
        baseline_spend=baseline,
        proposed_spend=proposed,
        historical_p90=p90,
        historical_p95=p95,
        historical_max=hmax,
        support_status=status,
        distance_to_historical_max=distance,
        support_warning=warning,
    )


def _build_readiness(
    scenario: dict[str, Any],
    cells: list[dict[str, Any]],
    contrasts: list[dict[str, Any]],
) -> ScenarioReadinessReport:
    upstream = scenario.get("upstream_statuses") or {}
    if not isinstance(upstream, dict):
        upstream = {}

    def gate(key: str, required: bool = True) -> GateStatus:
        val = upstream.get(key)
        if val is None:
            return GateStatus.NOT_EVALUATED if required else GateStatus.PASS
        if _is_blocked_status(str(val)):
            return GateStatus.BLOCKED
        if _is_ready_status(str(val)):
            return GateStatus.PASS
        return GateStatus.WARNING

    profiler = gate("profiler_status")
    geo = gate("geo_feasibility_status")
    spend = gate("spend_feasibility_status")
    power = gate("power_mde_status")
    design = gate("design_cell_structure_status")
    contrast_req = (
        GateStatus.PASS
        if contrasts and all(c.get("required_spend_contrast") is not None for c in contrasts)
        else GateStatus.NOT_EVALUATED
        if not contrasts
        else GateStatus.WARNING
    )
    plan = (
        GateStatus.PASS
        if cells and all(c.get("proposed_spend") is not None for c in cells)
        else GateStatus.BLOCKED
        if not cells
        else GateStatus.WARNING
    )

    issues: list[ScenarioIssue] = []
    if profiler == GateStatus.BLOCKED:
        issues.append(
            ScenarioIssue("PROFILER_BLOCKED", "Profiler gate blocked", IssueSeverity.BLOCKING)
        )
    if geo == GateStatus.BLOCKED:
        issues.append(
            ScenarioIssue("GEO_BLOCKED", "Geo feasibility gate blocked", IssueSeverity.BLOCKING)
        )
    if spend == GateStatus.BLOCKED:
        issues.append(
            ScenarioIssue(
                "SPEND_BLOCKED",
                "Spend feasibility gate blocked",
                IssueSeverity.BLOCKING,
            )
        )
    if design == GateStatus.BLOCKED:
        issues.append(
            ScenarioIssue(
                "DESIGN_STRUCTURE_BLOCKED",
                "Design cell structure gate blocked",
                IssueSeverity.BLOCKING,
            )
        )
    if plan == GateStatus.BLOCKED:
        issues.append(
            ScenarioIssue(
                "MISSING_POLICY_PLAN",
                "Scenario policy plan missing",
                IssueSeverity.BLOCKING,
            )
        )

    spend_ok = spend != GateStatus.BLOCKED
    power_ok = power != GateStatus.BLOCKED

    return ScenarioReadinessReport(
        profiler_gate=profiler,
        geo_unit_market_feasibility_gate=geo,
        spend_feasibility_gate=spend,
        power_mde_readiness_gate=power,
        design_cell_structure_gate=design,
        contrast_requirement_gate=contrast_req,
        scenario_policy_plan_gate=plan,
        spend_compatible_feasibility_allowed=spend_ok,
        power_ready_feasibility_allowed=power_ok,
        issues=tuple(issues),
    )


def _detect_shared_control_conflicts(
    scenario: dict[str, Any],
    cells: list[dict[str, Any]],
    contrasts: list[dict[str, Any]],
    contrast_reports: list[ContrastFeasibilityReport],
    historical: list[HistoricalSupportCellReport],
    cfg: DesignScenarioPolicyFeasibilityConfig,
) -> list[SharedControlConflictEntry]:
    conflicts: list[SharedControlConflictEntry] = []
    cell_by_id = _cell_index(cells)
    deps = scenario.get("shared_control_dependencies") or []
    if not isinstance(deps, list):
        deps = []

    common_ids: set[str] = set()
    for cell in cells:
        if cell.get("is_common_control"):
            common_ids.add(str(cell.get("cell_id")))

    for dep in deps:
        if isinstance(dep, dict) and dep.get("control_cell_id"):
            common_ids.add(str(dep["control_cell_id"]))

    hist_by_cell = {h.cell_id: h for h in historical}
    any_manipulated = False
    any_bau_not_preserved = False

    for cid in common_ids:
        cell = cell_by_id.get(cid)
        if cell is None:
            conflicts.append(
                SharedControlConflictEntry(
                    conflict_type=SharedControlConflictType.COMMON_CONTROL_ROLE_AMBIGUOUS,
                    control_cell_id=cid,
                    contrast_ids=(),
                    message=f"Common control cell {cid} referenced but not in plan",
                )
            )
            continue

        baseline = _num(cell.get("baseline_spend"))
        proposed = _num(cell.get("proposed_spend"))
        policy = cell.get("policy")
        is_bau = bool(cell.get("is_bau_policy"))
        preserved = _bau_preserved(baseline, proposed, str(policy) if policy else None, is_bau, cfg.bau_spend_tolerance)

        related_contrast_ids = tuple(
            cr.contrast_id
            for cr in contrast_reports
            if cr.comparison_cell_id == cid or cr.treatment_cell_id == cid
        )

        if preserved is False:
            any_manipulated = True
            conflicts.append(
                SharedControlConflictEntry(
                    conflict_type=SharedControlConflictType.COMMON_CONTROL_MANIPULATED,
                    control_cell_id=cid,
                    contrast_ids=related_contrast_ids,
                    message=f"Common control {cid} spend manipulated from BAU baseline",
                )
            )
            bau_required = any(
                bool(c.get("bau_control_required"))
                for c in contrasts
                if str(c.get("comparison_cell_id") or c.get("right_cell_id")) == cid
                or str(c.get("treatment_cell_id") or c.get("left_cell_id")) == cid
            )
            if bau_required:
                any_bau_not_preserved = True
                conflicts.append(
                    SharedControlConflictEntry(
                        conflict_type=SharedControlConflictType.BAU_CONTROL_NOT_PRESERVED,
                        control_cell_id=cid,
                        contrast_ids=related_contrast_ids,
                        message=f"BAU control not preserved for common control {cid}",
                    )
                )

        hist = hist_by_cell.get(cid)
        if hist and hist.support_status in {
            PolicySupportStatus.POLICY_OUT_OF_HISTORICAL_SUPPORT,
            PolicySupportStatus.POLICY_REQUIRES_BUSINESS_OVERRIDE,
        }:
            conflicts.append(
                SharedControlConflictEntry(
                    conflict_type=SharedControlConflictType.COMMON_CONTROL_OUT_OF_HISTORICAL_SUPPORT,
                    control_cell_id=cid,
                    contrast_ids=related_contrast_ids,
                    message=f"Common control {cid} proposed spend out of historical support",
                )
            )

    if common_ids:
        meets: list[str] = []
        fails: list[str] = []
        for cr in contrast_reports:
            if cr.achieved_spend_contrast is None or cr.required_spend_contrast is None:
                continue
            if cr.achieved_spend_contrast >= cr.required_spend_contrast:
                meets.append(cr.contrast_id)
            else:
                fails.append(cr.contrast_id)
        if any_manipulated and meets and fails:
            conflicts.append(
                SharedControlConflictEntry(
                    conflict_type=SharedControlConflictType.COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER,
                    control_cell_id=next(iter(common_ids), None),
                    contrast_ids=tuple(meets + fails),
                    message="Common control manipulation helps some contrasts and harms others",
                )
            )
        elif fails and not any_manipulated:
            conflicts.append(
                SharedControlConflictEntry(
                    conflict_type=SharedControlConflictType.COMMON_CONTROL_INSUFFICIENT_FOR_ONE_OR_MORE_CONTRASTS,
                    control_cell_id=next(iter(common_ids), None),
                    contrast_ids=tuple(fails),
                    message="Common control BAU preserved but one or more contrasts insufficient",
                )
            )

    if scenario.get("split_control_proposal"):
        conflicts.append(
            SharedControlConflictEntry(
                conflict_type=SharedControlConflictType.COMMON_CONTROL_SPLIT_REQUIRED_FOR_CLEAN_ESTIMANDS,
                control_cell_id=next(iter(common_ids), None) if common_ids else None,
                contrast_ids=tuple(cr.contrast_id for cr in contrast_reports),
                message="Split common control redesign proposed",
            )
        )

    if not conflicts:
        conflicts.append(
            SharedControlConflictEntry(
                conflict_type=SharedControlConflictType.NO_SHARED_CONTROL_CONFLICT,
                control_cell_id=None,
                contrast_ids=(),
                message="No shared-control conflict detected",
            )
        )
    return conflicts


def _emit_resolution_options(
    contrast_reports: list[ContrastFeasibilityReport],
    historical: list[HistoricalSupportCellReport],
    conflicts: list[SharedControlConflictEntry],
    estimand: EstimandShiftReport,
    readiness: ScenarioReadinessReport,
    scenario: dict[str, Any],
) -> list[ScenarioResolutionOption]:
    options: dict[ResolutionOptionType, ScenarioResolutionOption] = {}

    def add(
        opt: ResolutionOptionType,
        category: str,
        message: str,
        *,
        requires_recheck: bool = False,
    ) -> None:
        if opt not in options:
            options[opt] = ScenarioResolutionOption(
                option_type=opt,
                category=category,
                message=message,
                requires_recheck=requires_recheck,
            )

    for cr in contrast_reports:
        if cr.contrast_status == ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL:
            add(ResolutionOptionType.EXTEND_DURATION, "direct_scenario_adjustment", "Extend duration", requires_recheck=True)
            add(ResolutionOptionType.RELAX_MDE_TARGET, "direct_scenario_adjustment", "Relax MDE target")
            add(
                ResolutionOptionType.REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY,
                "estimand_reframing",
                "Reframe as dosage or difference-in-policy",
                requires_recheck=True,
            )
            add(ResolutionOptionType.SPLIT_COMMON_CONTROL, "redesign_recheck_proposal", "Split common control", requires_recheck=True)
            add(ResolutionOptionType.DROP_CONTRAST, "direct_scenario_adjustment", f"Drop contrast {cr.contrast_id}")
            add(ResolutionOptionType.SEQUENCE_TESTS, "direct_scenario_adjustment", "Sequence tests")

    for h in historical:
        if h.support_status in {
            PolicySupportStatus.POLICY_OUT_OF_HISTORICAL_SUPPORT,
            PolicySupportStatus.POLICY_REQUIRES_BUSINESS_OVERRIDE,
            PolicySupportStatus.POLICY_NEAR_HISTORICAL_SUPPORT_BOUNDARY,
        }:
            add(
                ResolutionOptionType.CAP_SPEND_WITHIN_HISTORICAL_SUPPORT,
                "direct_scenario_adjustment",
                f"Cap spend for cell {h.cell_id} within historical support",
            )
            add(
                ResolutionOptionType.BUSINESS_OVERRIDE_REQUIRED,
                "business_override",
                f"Business override required for cell {h.cell_id}",
            )
            add(ResolutionOptionType.EXTEND_DURATION, "direct_scenario_adjustment", "Extend duration", requires_recheck=True)
            add(ResolutionOptionType.RELAX_MDE_TARGET, "direct_scenario_adjustment", "Relax MDE target")

    for c in conflicts:
        if c.conflict_type == SharedControlConflictType.BAU_CONTROL_NOT_PRESERVED:
            add(
                ResolutionOptionType.REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY,
                "estimand_reframing",
                "Reframe estimand due to BAU control not preserved",
                requires_recheck=True,
            )
            add(ResolutionOptionType.SPLIT_COMMON_CONTROL, "redesign_recheck_proposal", "Split common control", requires_recheck=True)
            add(
                ResolutionOptionType.REQUIRE_METHOD_SUITABILITY_REVIEW,
                "estimand_reframing",
                "Method suitability review required",
            )
        if c.conflict_type == SharedControlConflictType.COMMON_CONTROL_CHANGE_HELPS_ONE_CONTRAST_HARMS_ANOTHER:
            add(
                ResolutionOptionType.REFRAME_AS_DOSAGE_OR_DIFFERENCE_IN_POLICY,
                "estimand_reframing",
                "Reframe due to cross-contrast shared-control tradeoff",
                requires_recheck=True,
            )
            add(ResolutionOptionType.CAP_SPEND_WITHIN_HISTORICAL_SUPPORT, "direct_scenario_adjustment", "Cap spend within historical support")
            add(ResolutionOptionType.SPLIT_COMMON_CONTROL, "redesign_recheck_proposal", "Split common control", requires_recheck=True)
            add(ResolutionOptionType.RERUN_POWER_MDE, "redesign_recheck_proposal", "Rerun power/MDE", requires_recheck=True)
            add(
                ResolutionOptionType.RERUN_ASSIGNMENT_FEASIBILITY,
                "redesign_recheck_proposal",
                "Rerun assignment feasibility",
                requires_recheck=True,
            )

    if scenario.get("split_control_proposal"):
        add(ResolutionOptionType.RERUN_POWER_MDE, "redesign_recheck_proposal", "Rerun power/MDE after split", requires_recheck=True)
        add(
            ResolutionOptionType.RERUN_ASSIGNMENT_FEASIBILITY,
            "redesign_recheck_proposal",
            "Rerun assignment feasibility after split",
            requires_recheck=True,
        )
        add(
            ResolutionOptionType.REQUIRE_METHOD_SUITABILITY_REVIEW,
            "estimand_reframing",
            "Method suitability review after split",
        )

    if estimand.method_suitability_review_required:
        add(
            ResolutionOptionType.REQUIRE_METHOD_SUITABILITY_REVIEW,
            "estimand_reframing",
            "Method suitability review required",
        )

    if readiness.power_mde_readiness_gate == GateStatus.BLOCKED:
        add(ResolutionOptionType.RERUN_POWER_MDE, "redesign_recheck_proposal", "Rerun power/MDE", requires_recheck=True)

    if readiness.profiler_gate == GateStatus.BLOCKED:
        add(ResolutionOptionType.BLOCK_SCENARIO, "blocking_recommendation", "Scenario blocked by upstream gates")

    return list(options.values())


def _aggregate_scenario_status(
    readiness: ScenarioReadinessReport,
    contrast_reports: list[ContrastFeasibilityReport],
    historical: list[HistoricalSupportCellReport],
    conflicts: list[SharedControlConflictEntry],
    estimand: EstimandShiftReport,
    scenario: dict[str, Any],
    cfg: DesignScenarioPolicyFeasibilityConfig,
) -> tuple[ScenarioFeasibilityStatus, tuple[ScenarioFeasibilityStatus, ...]]:
    secondary: list[ScenarioFeasibilityStatus] = []

    if readiness.profiler_gate == GateStatus.BLOCKED or readiness.geo_unit_market_feasibility_gate == GateStatus.BLOCKED:
        return ScenarioFeasibilityStatus.SCENARIO_BLOCKED, tuple(secondary)

    if readiness.design_cell_structure_gate == GateStatus.BLOCKED:
        return ScenarioFeasibilityStatus.SCENARIO_BLOCKED, tuple(secondary)

    if readiness.scenario_policy_plan_gate == GateStatus.BLOCKED:
        return ScenarioFeasibilityStatus.SCENARIO_BLOCKED, tuple(secondary)

    if not contrast_reports and readiness.contrast_requirement_gate != GateStatus.PASS:
        return ScenarioFeasibilityStatus.SCENARIO_NOT_EVALUATED, tuple(secondary)

    if scenario.get("split_control_proposal"):
        secondary.extend(
            [
                ScenarioFeasibilityStatus.SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT,
                ScenarioFeasibilityStatus.SCENARIO_REQUIRES_POWER_MDE_RECHECK,
                ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ASSIGNMENT_RECHECK,
            ]
        )
        return ScenarioFeasibilityStatus.SCENARIO_REQUIRES_COMMON_CONTROL_SPLIT, tuple(secondary)

    oos = any(
        h.support_status
        in {
            PolicySupportStatus.POLICY_OUT_OF_HISTORICAL_SUPPORT,
            PolicySupportStatus.POLICY_REQUIRES_BUSINESS_OVERRIDE,
        }
        for h in historical
    )
    if oos:
        secondary.append(ScenarioFeasibilityStatus.SCENARIO_OUT_OF_HISTORICAL_SUPPORT)

    if estimand.estimand_shift_required:
        secondary.append(ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT)

    if any(
        c.conflict_type == SharedControlConflictType.COMMON_CONTROL_MANIPULATED for c in conflicts
    ):
        secondary.append(ScenarioFeasibilityStatus.SCENARIO_REQUIRES_COMMON_CONTROL_MANIPULATION)

    if estimand.method_suitability_review_required:
        secondary.append(ScenarioFeasibilityStatus.SCENARIO_REQUIRES_METHOD_SUITABILITY_REVIEW)

    if readiness.power_mde_readiness_gate == GateStatus.BLOCKED:
        secondary.append(ScenarioFeasibilityStatus.SCENARIO_REQUIRES_POWER_MDE_RECHECK)

    if not readiness.spend_compatible_feasibility_allowed:
        if contrast_reports:
            pass  # still evaluate but cannot claim full spend-compatible

    evaluated = [
        cr
        for cr in contrast_reports
        if cr.contrast_status
        not in {
            ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED,
            ContrastFeasibilityStatus.CONTRAST_BLOCKED,
        }
    ]
    feasible = [
        cr
        for cr in evaluated
        if cr.contrast_status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
    ]
    insufficient = [
        cr
        for cr in evaluated
        if cr.contrast_status
        in {
            ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL,
            ContrastFeasibilityStatus.CONTRAST_REQUIRES_ESTIMAND_SHIFT,
        }
    ]

    if evaluated and len(feasible) == len(evaluated) and not secondary:
        return ScenarioFeasibilityStatus.SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE, tuple(secondary)

    if feasible and insufficient:
        primary = ScenarioFeasibilityStatus.SCENARIO_PARTIALLY_FEASIBLE
        if ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT in secondary:
            primary = ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT
        return primary, tuple(secondary)

    if feasible and not insufficient and secondary:
        return ScenarioFeasibilityStatus.SCENARIO_FEASIBLE_UNDER_CURRENT_STRUCTURE, tuple(secondary)

    if insufficient and not feasible:
        if cfg.block_when_none_feasible:
            return ScenarioFeasibilityStatus.SCENARIO_BLOCKED, tuple(secondary)
        primary = ScenarioFeasibilityStatus.SCENARIO_PARTIALLY_FEASIBLE
        if ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT in secondary:
            primary = ScenarioFeasibilityStatus.SCENARIO_REQUIRES_ESTIMAND_SHIFT
        return primary, tuple(secondary)

    return ScenarioFeasibilityStatus.SCENARIO_NOT_EVALUATED, tuple(secondary)


def _evaluate_single_scenario(
    scenario: dict[str, Any],
    cfg: DesignScenarioPolicyFeasibilityConfig,
) -> ScenarioFeasibilityReport:
    scenario_id = str(scenario.get("scenario_id") or "scenario_unspecified")
    cells_raw = scenario.get("cells") or []
    contrasts_raw = scenario.get("contrasts") or []
    cells = [c for c in cells_raw if isinstance(c, dict)]
    contrasts = [c for c in contrasts_raw if isinstance(c, dict)]
    cell_by_id = _cell_index(cells)

    readiness = _build_readiness(scenario, cells, contrasts)
    hard_blocked = (
        readiness.profiler_gate == GateStatus.BLOCKED
        or readiness.geo_unit_market_feasibility_gate == GateStatus.BLOCKED
        or readiness.design_cell_structure_gate == GateStatus.BLOCKED
        or readiness.scenario_policy_plan_gate == GateStatus.BLOCKED
    )

    cell_plan = ScenarioPolicyPlanReport(
        cells=tuple(
            CellPolicyReport(
                cell_id=str(c.get("cell_id", "")),
                cell_role=str(c.get("cell_role")) if c.get("cell_role") is not None else None,
                baseline_spend=_num(c.get("baseline_spend")),
                proposed_spend=_num(c.get("proposed_spend")),
                policy=str(c.get("policy")) if c.get("policy") is not None else None,
                is_common_control=bool(c.get("is_common_control")),
                is_bau_policy=bool(c.get("is_bau_policy")),
            )
            for c in cells
        )
    )

    historical = [_evaluate_historical_support(c, cfg) for c in cells]

    contrast_reports: list[ContrastFeasibilityReport] = []
    rvsa_entries: list[RequiredVsAchievedSpendContrastEntry] = []
    issues: list[ScenarioIssue] = list(readiness.issues)
    warnings: list[str] = []

    can_compare = (
        not hard_blocked
        and readiness.contrast_requirement_gate != GateStatus.NOT_EVALUATED
        and readiness.scenario_policy_plan_gate == GateStatus.PASS
    )

    if scenario.get("split_control_proposal"):
        can_compare = False

    for contrast in contrasts:
        cid = str(contrast.get("contrast_id") or "")
        ctype = str(contrast.get("contrast_type")) if contrast.get("contrast_type") else None
        t_id, c_id = _contrast_cell_ids(contrast)
        treatment = cell_by_id.get(t_id) if t_id else None
        comparison = cell_by_id.get(c_id) if c_id else None
        required = _num(contrast.get("required_spend_contrast"))
        bau_required = bool(contrast.get("bau_control_required"))
        method_review = bool(contrast.get("method_suitability_review_required"))
        bridge = contrast.get("response_bridge_source")
        biz_risk = bool(contrast.get("business_response_risk"))

        cr_issues: list[ScenarioIssue] = []
        cr_warnings: list[str] = []

        if hard_blocked:
            status = ContrastFeasibilityStatus.CONTRAST_BLOCKED
            achieved = None
            gap = None
        elif not can_compare:
            status = ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED
            achieved = None
            gap = None
        elif ctype is None or ctype.upper() == "UNKNOWN":
            status = ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED
            achieved = None
            gap = None
            cr_issues.append(
                ScenarioIssue("UNKNOWN_CONTRAST_TYPE", f"Unknown contrast type for {cid}", IssueSeverity.WARNING)
            )
        elif required is None:
            status = ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED
            achieved = None
            gap = None
        else:
            achieved = _compute_achieved_contrast(ctype, treatment, comparison)
            if achieved is None:
                status = ContrastFeasibilityStatus.CONTRAST_NOT_EVALUATED
                gap = None
                cr_issues.append(
                    ScenarioIssue(
                        "MISSING_CELL_POLICY",
                        f"Missing cell policy for contrast {cid}",
                        IssueSeverity.WARNING,
                    )
                )
            else:
                gap = required - achieved
                bau_preserved: bool | None = None
                if bau_required and comparison is not None:
                    bau_preserved = _bau_preserved(
                        _num(comparison.get("baseline_spend")),
                        _num(comparison.get("proposed_spend")),
                        str(comparison.get("policy")) if comparison.get("policy") else None,
                        bool(comparison.get("is_bau_policy")),
                        cfg.bau_spend_tolerance,
                    )

                if bau_required and bau_preserved is False and achieved >= required:
                    ctype_upper = (ctype or "").upper()
                    if ctype_upper in {"GO_DARK_VS_BAU", "GO_DARK"}:
                        status = ContrastFeasibilityStatus.CONTRAST_REQUIRES_ESTIMAND_SHIFT
                        cr_warnings.append("Spend differential met but BAU estimand invalid")
                    else:
                        status = ContrastFeasibilityStatus.CONTRAST_FEASIBLE
                elif achieved >= required:
                    status = ContrastFeasibilityStatus.CONTRAST_FEASIBLE
                else:
                    status = ContrastFeasibilityStatus.CONTRAST_INSUFFICIENT_SPEND_DIFFERENTIAL

                if not readiness.spend_compatible_feasibility_allowed and status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE:
                    cr_warnings.append("Spend feasibility gate blocked; spend-compatible claim withheld")

                if not readiness.power_ready_feasibility_allowed:
                    cr_warnings.append("Power/MDE readiness gate blocked")

        bau_preserved_val: bool | None = None
        if bau_required and comparison is not None:
            bau_preserved_val = _bau_preserved(
                _num(comparison.get("baseline_spend")),
                _num(comparison.get("proposed_spend")),
                str(comparison.get("policy")) if comparison.get("policy") else None,
                bool(comparison.get("is_bau_policy")),
                cfg.bau_spend_tolerance,
            )

        if hard_blocked and status != ContrastFeasibilityStatus.CONTRAST_BLOCKED:
            status = ContrastFeasibilityStatus.CONTRAST_BLOCKED

        meets = (
            achieved is not None
            and required is not None
            and achieved >= required
            and status == ContrastFeasibilityStatus.CONTRAST_FEASIBLE
        )

        cfr = ContrastFeasibilityReport(
            contrast_id=cid,
            contrast_type=ctype,
            treatment_cell_id=t_id,
            comparison_cell_id=c_id,
            required_spend_contrast=required,
            achieved_spend_contrast=achieved if can_compare or achieved is not None else None,
            spend_contrast_gap=gap,
            contrast_status=status,
            bau_control_required=bau_required,
            bau_control_preserved=bau_preserved_val,
            response_bridge_source=str(bridge) if bridge is not None else None,
            business_response_risk=biz_risk,
            method_suitability_review_required=method_review,
            issues=tuple(cr_issues),
            warnings=tuple(cr_warnings),
        )
        contrast_reports.append(cfr)
        rvsa_entries.append(
            RequiredVsAchievedSpendContrastEntry(
                contrast_id=cid,
                required_spend_contrast=required,
                achieved_spend_contrast=achieved,
                spend_contrast_gap=gap,
                meets_required=meets if can_compare else None,
            )
        )
        warnings.extend(cr_warnings)

    conflicts = _detect_shared_control_conflicts(
        scenario, cells, contrasts, contrast_reports, historical, cfg
    )

    bau_preserved_scenario: bool | None = None
    for cell in cells:
        if cell.get("is_common_control"):
            bau_preserved_scenario = _bau_preserved(
                _num(cell.get("baseline_spend")),
                _num(cell.get("proposed_spend")),
                str(cell.get("policy")) if cell.get("policy") else None,
                bool(cell.get("is_bau_policy")),
                cfg.bau_spend_tolerance,
            )
            break

    dosage_required = any(
        str(c.get("contrast_type", "")).upper() in {"DOSAGE_LOW_VS_HIGH", "DOSAGE_CONTRAST"}
        for c in contrasts
    ) or bool(scenario.get("dosage_contrast_estimand_required"))
    diff_policy = any(
        str(c.get("contrast_type", "")).upper() in {"DIFFERENCE_IN_POLICY"}
        for c in contrasts
    ) or bool(scenario.get("difference_in_policy_required"))

    estimand_flags: list[str] = []
    estimand_shift = False
    if bau_preserved_scenario is False:
        estimand_shift = True
        estimand_flags.append("BAU_CONTROL_NOT_PRESERVED")
    if dosage_required:
        estimand_flags.append("DOSAGE_CONTRAST_ESTIMAND")
    if diff_policy:
        estimand_flags.append("DIFFERENCE_IN_POLICY_ESTIMAND")
    method_review = any(cr.method_suitability_review_required for cr in contrast_reports) or dosage_required or diff_policy

    estimand = EstimandShiftReport(
        estimand_shift_required=estimand_shift,
        bau_control_preserved=bau_preserved_scenario,
        dosage_contrast_required=dosage_required,
        difference_in_policy_required=diff_policy,
        method_suitability_review_required=method_review,
        flags=tuple(estimand_flags),
    )

    resolution = _emit_resolution_options(
        contrast_reports, historical, conflicts, estimand, readiness, scenario
    )

    rechecks: list[ScenarioRecheckRequirement] = []
    if scenario.get("split_control_proposal"):
        rechecks.extend(
            [
                ScenarioRecheckRequirement("POWER_MDE_RECHECK", "Rerun power/MDE after split-control redesign"),
                ScenarioRecheckRequirement(
                    "ASSIGNMENT_RECHECK",
                    "Rerun assignment feasibility after split-control redesign",
                ),
            ]
        )
    if readiness.power_mde_readiness_gate == GateStatus.BLOCKED:
        rechecks.append(
            ScenarioRecheckRequirement("POWER_MDE_RECHECK", "Power/MDE readiness gate blocked")
        )

    primary, secondary = _aggregate_scenario_status(
        readiness, contrast_reports, historical, conflicts, estimand, scenario, cfg
    )

    summary_parts = [f"Scenario {scenario_id}: {primary.value}"]
    if secondary:
        summary_parts.append("secondary=" + ",".join(s.value for s in secondary))

    blocking_reasons = tuple(i.message for i in issues if i.severity == IssueSeverity.BLOCKING)

    return ScenarioFeasibilityReport(
        scenario_id=scenario_id,
        scenario_status=primary,
        secondary_statuses=secondary,
        overall_feasibility_summary="; ".join(summary_parts),
        readiness_report=readiness,
        cell_policy_plan=cell_plan,
        contrast_feasibility_reports=tuple(contrast_reports),
        required_vs_achieved_spend_contrast_by_contrast=tuple(rvsa_entries),
        historical_support_by_cell=tuple(historical),
        shared_control_conflicts=tuple(conflicts),
        estimand_shift_report=estimand,
        resolution_options=tuple(resolution),
        recheck_requirements=tuple(rechecks),
        claim_boundary_report=ScenarioClaimBoundaryReport(),
        issues=tuple(issues),
        warnings=tuple(warnings),
        blocking_reasons=blocking_reasons,
    )


def _normalize_scenarios(
    input_data: Any,
) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        if input_data and all(isinstance(x, dict) for x in input_data):
            if "scenario_id" in input_data[0] or "cells" in input_data[0]:
                return [dict(x) for x in input_data]
        return [{"scenario_id": "scenario_0", "cells": [], "contrasts": []}]
    data = _to_dict(input_data)
    if "scenarios" in data and isinstance(data["scenarios"], list):
        return [dict(s) for s in data["scenarios"] if isinstance(s, dict)]
    if "cells" in data or "scenario_id" in data:
        return [data]
    return [{"scenario_id": "scenario_0", **data}]


def evaluate_design_scenario_policy_feasibility(
    input_data: Any,
    config: DesignScenarioPolicyFeasibilityConfig | None = None,
) -> DesignScenarioPolicyFeasibilityReport:
    """Evaluate conservative scenario-policy feasibility for provided scenarios only."""
    cfg = config or DesignScenarioPolicyFeasibilityConfig()
    scenarios = _normalize_scenarios(input_data)
    reports = [_evaluate_single_scenario(s, cfg) for s in scenarios]

    all_issues: list[ScenarioIssue] = []
    all_warnings: list[str] = []
    all_blocking: list[str] = []
    all_resolutions: list[ScenarioResolutionOption] = []
    all_rechecks: list[ScenarioRecheckRequirement] = []
    all_conflicts: list[SharedControlConflictEntry] = []
    all_historical: list[HistoricalSupportCellReport] = []
    all_contrasts: list[ContrastFeasibilityReport] = []
    all_rvsa: list[RequiredVsAchievedSpendContrastEntry] = []
    all_flags: list[str] = []

    for r in reports:
        all_issues.extend(r.issues)
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)
        all_resolutions.extend(r.resolution_options)
        all_rechecks.extend(r.recheck_requirements)
        all_conflicts.extend(r.shared_control_conflicts)
        all_historical.extend(r.historical_support_by_cell)
        all_contrasts.extend(r.contrast_feasibility_reports)
        all_rvsa.extend(r.required_vs_achieved_spend_contrast_by_contrast)
        all_flags.extend(r.estimand_shift_report.flags)

    dedupe_resolutions = {o.option_type: o for o in all_resolutions}
    dedupe_rechecks = {r.requirement_type: r for r in all_rechecks}

    if len(reports) == 1:
        r = reports[0]
        return DesignScenarioPolicyFeasibilityReport(
            artifact_id=_ARTIFACT_ID,
            scenario_id=r.scenario_id,
            scenario_status=r.scenario_status,
            secondary_statuses=r.secondary_statuses,
            overall_feasibility_summary=r.overall_feasibility_summary,
            scenario_reports=(r,),
            aggregate_summary=None,
            cell_policy_plan=r.cell_policy_plan,
            contrast_feasibility_reports=r.contrast_feasibility_reports,
            required_vs_achieved_spend_contrast_by_contrast=r.required_vs_achieved_spend_contrast_by_contrast,
            historical_support_by_cell=r.historical_support_by_cell,
            shared_control_conflicts=r.shared_control_conflicts,
            estimand_shift_flags=r.estimand_shift_report.flags,
            estimand_shift_report=r.estimand_shift_report,
            resolution_options=r.resolution_options,
            recheck_requirements=r.recheck_requirements,
            claim_boundary_report=r.claim_boundary_report,
            issues=r.issues,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
        )

    aggregate = f"Evaluated {len(reports)} provided scenarios without ranking"
    return DesignScenarioPolicyFeasibilityReport(
        artifact_id=_ARTIFACT_ID,
        scenario_id=None,
        scenario_status=None,
        secondary_statuses=(),
        overall_feasibility_summary=aggregate,
        scenario_reports=tuple(reports),
        aggregate_summary=aggregate,
        cell_policy_plan=None,
        contrast_feasibility_reports=tuple(all_contrasts),
        required_vs_achieved_spend_contrast_by_contrast=tuple(all_rvsa),
        historical_support_by_cell=tuple(all_historical),
        shared_control_conflicts=tuple(all_conflicts),
        estimand_shift_flags=tuple(dict.fromkeys(all_flags)),
        estimand_shift_report=None,
        resolution_options=tuple(dedupe_resolutions.values()),
        recheck_requirements=tuple(dedupe_rechecks.values()),
        claim_boundary_report=ScenarioClaimBoundaryReport(),
        issues=tuple(all_issues),
        warnings=tuple(all_warnings),
        blocking_reasons=tuple(dict.fromkeys(all_blocking)),
    )


evaluate_scenario_policy_feasibility = evaluate_design_scenario_policy_feasibility


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    scenario = {
        "scenario_id": "smoke_scenario_a",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
            "design_cell_structure_status": "PASS",
        },
        "cells": [
            {"cell_id": "C0", "baseline_spend": 100_000, "proposed_spend": 100_000, "policy": "BAU", "is_common_control": True, "is_bau_policy": True, "historical_max": 130_000},
            {"cell_id": "T1", "baseline_spend": 80_000, "proposed_spend": 0, "policy": "GO_DARK", "historical_max": 120_000},
            {"cell_id": "T2", "baseline_spend": 120_000, "proposed_spend": 220_000, "policy": "HEAVY_UP", "historical_max": 250_000},
            {"cell_id": "T3", "baseline_spend": 100_000, "proposed_spend": 160_000, "policy": "HEAVY_UP", "historical_max": 180_000},
        ],
        "contrasts": [
            {"contrast_id": "T1_vs_C0", "contrast_type": "GO_DARK_VS_BAU", "treatment_cell_id": "T1", "comparison_cell_id": "C0", "required_spend_contrast": 150_000, "bau_control_required": True},
            {"contrast_id": "T2_vs_C0", "contrast_type": "HEAVY_UP_VS_BAU", "treatment_cell_id": "T2", "comparison_cell_id": "C0", "required_spend_contrast": 100_000, "bau_control_required": True},
            {"contrast_id": "T3_vs_C0", "contrast_type": "HEAVY_UP_VS_BAU", "treatment_cell_id": "T3", "comparison_cell_id": "C0", "required_spend_contrast": 60_000, "bau_control_required": True},
        ],
        "shared_control_dependencies": [{"control_cell_id": "C0", "contrast_ids": ["T1_vs_C0", "T2_vs_C0", "T3_vs_C0"]}],
    }
    report = evaluate_design_scenario_policy_feasibility(scenario)
    failed: list[str] = []
    if report.scenario_status != ScenarioFeasibilityStatus.SCENARIO_PARTIALLY_FEASIBLE:
        failed.append("smoke_status")
    if report.claim_boundary_report.runtime_scenario_enumeration_implemented:
        failed.append("smoke_no_enumeration")
    if report.claim_boundary_report.power_computed:
        failed.append("smoke_no_power")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_scenario_policy_feasibility_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "runtime_evaluates_provided_scenarios_no_enumeration_or_optimization",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
            "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001",
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_CONTRACT_001",
        ],
        "public_api": "evaluate_design_scenario_policy_feasibility",
        "runtime_scenario_feasibility_implemented": True,
        "provided_scenario_evaluation_implemented": True,
        "required_vs_achieved_spend_contrast_implemented": True,
        "historical_support_evaluation_implemented": True,
        "shared_control_conflict_detection_implemented": True,
        "estimand_shift_detection_implemented": True,
        "split_control_recheck_detection_implemented": True,
        "resolution_option_emission_implemented": True,
        "multiple_provided_scenarios_supported": True,
        "runtime_scenario_enumeration_implemented": False,
        "runtime_scenario_optimization_implemented": False,
        "runtime_design_generation_implemented": False,
        "geo_assignment_computed": False,
        "randomization_computed": False,
        "rerandomization_computed": False,
        "matching_optimization_computed": False,
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
        "smoke_scenario_status": report.scenario_status.value if report.scenario_status else None,
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
