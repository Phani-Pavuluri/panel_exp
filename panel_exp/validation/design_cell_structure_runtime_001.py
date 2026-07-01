"""DESIGN_CELL_STRUCTURE_RUNTIME_001 conservative declared-structure validation."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "DESIGN_CELL_STRUCTURE_RUNTIME_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = (
    "design_cell_structure_runtime_implemented_for_declared_structures_no_assignment_or_scenario_feasibility_computation"
)
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/DESIGN_CELL_STRUCTURE_RUNTIME_001_summary.json"
RECOMMENDED_NEXT_ARTIFACT = "DESIGN_ASSIGNMENT_FEASIBILITY_CONTRACT_001"
ALTERNATIVE_NEXT_ARTIFACT = "METHOD_SUITABILITY_HANDOFF_CONTRACT_001"

_BLOCKED_TOKENS = frozenset({"BLOCKED", "NOT_EVALUATED"})
_READY_TOKENS = frozenset({"PASS", "READY", "READY_FOR_DOWNSTREAM", "COMPLETE", "COMPLETED"})

_BAU_POLICIES = frozenset({"BAU", "BUSINESS_AS_USUAL", "BUSINESS_AS_USUAL_CONTROL"})
_BAU_ROLES = frozenset({"BUSINESS_AS_USUAL_CONTROL", "COMMON_CONTROL", "COMMON_REFERENCE_CELL", "CONTROL"})
_TREATMENT_ROLES = frozenset({"TEST_CELL", "TREATMENT", "GO_LIVE_CELL", "HIGH_DOSAGE"})
_COMMON_CONTROL_ROLES = frozenset({"COMMON_CONTROL", "COMMON_REFERENCE_CELL"})

DESIGN_STRUCTURE_TYPES = frozenset({
    "SINGLE_TREATMENT_CONTROL", "MULTI_CELL_COMMON_CONTROL", "MULTI_CELL_SPLIT_CONTROL",
    "MATCHED_PAIR", "RERANDOMIZED_BLOCK", "THINNING_DESIGN", "QUICK_BLOCK",
    "DOSAGE_CONTRAST", "DIFFERENCE_IN_POLICY", "BUDGET_REALLOCATION", "GO_LIVE", "UNKNOWN",
})
CELL_ROLES = frozenset({
    "TEST_CELL", "TREATMENT", "CONTROL", "COMMON_CONTROL", "COMMON_REFERENCE_CELL",
    "BUSINESS_AS_USUAL_CONTROL", "LOW_DOSAGE", "MEDIUM_DOSAGE", "HIGH_DOSAGE",
    "SOURCE_REDUCTION", "DESTINATION_INCREASE", "GO_LIVE_CELL", "HOLDOUT", "EXCLUDED", "UNKNOWN",
})
CONTRAST_TYPES = frozenset({
    "GO_DARK_VS_BAU", "HEAVY_UP_VS_BAU", "GO_LIVE_VS_NO_OR_LOW_SPEND", "DOSAGE_LOW_VS_HIGH",
    "DIFFERENCE_IN_POLICY", "BUDGET_REALLOCATION_SOURCE_VS_DESTINATION",
    "MULTI_CELL_COMMON_CONTROL_CONTRAST", "UNKNOWN",
})
CONTRAST_SPECIFIC_ROLES = frozenset({
    "TREATMENT_FOR_CONTRAST", "COMPARISON_FOR_CONTRAST", "BAU_CONTROL_FOR_CONTRAST",
    "LOW_POLICY_ANCHOR_FOR_CONTRAST", "HIGH_POLICY_CELL_FOR_CONTRAST",
    "SOURCE_CELL_FOR_REALLOCATION_CONTRAST", "DESTINATION_CELL_FOR_REALLOCATION_CONTRAST",
    "EXCLUDED_FROM_CONTRAST", "UNKNOWN",
})
MANIPULATION_POLICIES = frozenset({
    "BUSINESS_AS_USUAL", "GO_DARK", "HEAVY_UP", "GO_LIVE", "BUDGET_REALLOCATION_SOURCE",
    "BUDGET_REALLOCATION_DESTINATION", "LOW_SPEND_POLICY", "HIGH_SPEND_POLICY",
    "DOSAGE_POLICY", "DIFFERENCE_IN_POLICY", "UNKNOWN",
})


class DesignStructureStatus(str, Enum):
    DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY = "DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY"
    DESIGN_CELL_STRUCTURE_READY_WITH_WARNINGS = "DESIGN_CELL_STRUCTURE_READY_WITH_WARNINGS"
    DESIGN_CELL_STRUCTURE_PROVISIONAL = "DESIGN_CELL_STRUCTURE_PROVISIONAL"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_DATA_READINESS = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_DATA_READINESS"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_GEO_FEASIBILITY = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_GEO_FEASIBILITY"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_SPEND_FEASIBILITY = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_SPEND_FEASIBILITY"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_POWER_MDE_READINESS = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_POWER_MDE_READINESS"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CELLS = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CELLS"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CELL_ROLES = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CELL_ROLES"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CONTRASTS = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CONTRASTS"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS"
    DESIGN_CELL_STRUCTURE_BLOCKED_BY_SHARED_CONTROL_AMBIGUITY = "DESIGN_CELL_STRUCTURE_BLOCKED_BY_SHARED_CONTROL_AMBIGUITY"
    DESIGN_CELL_STRUCTURE_REQUIRES_DOSAGE_ESTIMAND_REVIEW = "DESIGN_CELL_STRUCTURE_REQUIRES_DOSAGE_ESTIMAND_REVIEW"
    DESIGN_CELL_STRUCTURE_REQUIRES_METHOD_SUITABILITY_REVIEW = "DESIGN_CELL_STRUCTURE_REQUIRES_METHOD_SUITABILITY_REVIEW"
    DESIGN_CELL_STRUCTURE_NOT_EVALUATED = "DESIGN_CELL_STRUCTURE_NOT_EVALUATED"


class AssignmentReadinessStatus(str, Enum):
    DESIGN_ASSIGNMENT_READY_FOR_RUNTIME = "DESIGN_ASSIGNMENT_READY_FOR_RUNTIME"
    DESIGN_ASSIGNMENT_READY_WITH_WARNINGS = "DESIGN_ASSIGNMENT_READY_WITH_WARNINGS"
    DESIGN_ASSIGNMENT_PROVISIONAL = "DESIGN_ASSIGNMENT_PROVISIONAL"
    DESIGN_ASSIGNMENT_BLOCKED_BY_DATA_READINESS = "DESIGN_ASSIGNMENT_BLOCKED_BY_DATA_READINESS"
    DESIGN_ASSIGNMENT_BLOCKED_BY_GEO_FEASIBILITY = "DESIGN_ASSIGNMENT_BLOCKED_BY_GEO_FEASIBILITY"
    DESIGN_ASSIGNMENT_BLOCKED_BY_SPEND_FEASIBILITY = "DESIGN_ASSIGNMENT_BLOCKED_BY_SPEND_FEASIBILITY"
    DESIGN_ASSIGNMENT_BLOCKED_BY_POWER_MDE_READINESS = "DESIGN_ASSIGNMENT_BLOCKED_BY_POWER_MDE_READINESS"
    DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE = "DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE"
    DESIGN_ASSIGNMENT_BLOCKED_BY_CONTRAST_STRUCTURE = "DESIGN_ASSIGNMENT_BLOCKED_BY_CONTRAST_STRUCTURE"
    DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT = "DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT"
    DESIGN_ASSIGNMENT_BLOCKED_BY_CONSTRAINTS = "DESIGN_ASSIGNMENT_BLOCKED_BY_CONSTRAINTS"
    DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW = "DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW"
    DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW = "DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW"
    DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK = "DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK"
    DESIGN_ASSIGNMENT_NOT_EVALUATED = "DESIGN_ASSIGNMENT_NOT_EVALUATED"


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
class DesignCellStructureConfig:
    unknown_cell_role_is_blocking: bool = False
    unknown_contrast_type_is_blocking: bool = True
    missing_shared_control_dependency_is_blocking: bool = False
    require_bau_policy_for_bau_control: bool = True
    require_contrast_specific_roles: bool = True
    require_scenario_policy_plan_for_handoff: bool = False
    allow_assignment_readiness_with_warnings: bool = True


@dataclass(frozen=True)
class StructureIssue:
    code: str
    message: str
    severity: IssueSeverity
    field: str | None = None


@dataclass(frozen=True)
class DesignCellReadinessReport:
    profiler_gate: GateStatus
    geo_unit_market_feasibility_gate: GateStatus
    spend_feasibility_gate: GateStatus
    power_mde_readiness_gate: GateStatus
    design_cell_declaration_gate: GateStatus
    contrast_declaration_gate: GateStatus
    shared_control_declaration_gate: GateStatus
    scenario_feasibility_handoff_gate: GateStatus
    issues: tuple[StructureIssue, ...] = ()


@dataclass(frozen=True)
class DesignCellRoleReport:
    cell_count: int
    unique_cell_ids: tuple[str, ...]
    duplicate_cell_ids: tuple[str, ...]
    valid_cell_roles: tuple[str, ...]
    unknown_cell_roles: tuple[str, ...]
    common_control_cells: tuple[str, ...]
    bau_control_cells: tuple[str, ...]
    test_cells: tuple[str, ...]
    excluded_cells: tuple[str, ...]
    assignment_eligible_cells: tuple[str, ...]


@dataclass(frozen=True)
class DesignContrastStructureReport:
    contrast_count: int
    valid_contrast_types: tuple[str, ...]
    unknown_contrast_types: tuple[str, ...]
    missing_cell_references: tuple[str, ...]
    valid_cell_references: tuple[str, ...]
    contrast_specific_roles_present: bool
    bau_control_required_contrasts: tuple[str, ...]
    dosage_contrasts: tuple[str, ...]
    difference_in_policy_contrasts: tuple[str, ...]
    budget_reallocation_contrasts: tuple[str, ...]
    method_suitability_required_contrasts: tuple[str, ...]
    blocked_contrast_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContrastSpecificRoleEntry:
    contrast_id: str
    cell_id: str
    contrast_specific_role: str
    compatible_with_contrast_type: bool
    role_conflicts: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContrastSpecificRoleReport:
    entries: tuple[ContrastSpecificRoleEntry, ...]
    contradictory_contrast_ids: tuple[str, ...]


@dataclass(frozen=True)
class ManipulationPolicyEntry:
    cell_id: str
    cell_role: str | None
    manipulation_policy: str | None
    policy_compatible_with_role: bool
    policy_conflicts: tuple[str, ...] = ()


@dataclass(frozen=True)
class ManipulationPolicyCompatibilityReport:
    entries: tuple[ManipulationPolicyEntry, ...]
    incompatible_cell_ids: tuple[str, ...]


@dataclass(frozen=True)
class SharedControlDependencyEntry:
    shared_cell_id: str
    dependent_contrast_ids: tuple[str, ...]
    shared_cell_declared: bool
    dependent_contrasts_exist: bool
    shared_policy_required: str | None
    role_by_contrast_present: bool
    ambiguity_detected: bool
    bau_control_preservation_required: bool


@dataclass(frozen=True)
class SharedControlDependencyReport:
    entries: tuple[SharedControlDependencyEntry, ...]
    implied_shared_cells: tuple[str, ...]
    missing_dependency_declarations: tuple[str, ...]
    ambiguity_detected: bool


@dataclass(frozen=True)
class EstimandRequirementReport:
    standard_go_dark_allowed: bool
    standard_heavy_up_allowed: bool
    dosage_contrast_estimand_required: bool
    difference_in_policy_required: bool
    budget_reallocation_estimand_required: bool
    bau_control_not_preserved: bool
    control_contamination_flags: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioFeasibilityHandoffReport:
    handoff_ready: bool
    required_fields_present: bool
    cells_ready: bool
    contrasts_ready: bool
    policies_ready: bool
    shared_control_dependencies_ready: bool
    missing_handoff_fields: tuple[str, ...]


@dataclass(frozen=True)
class AssignmentReadinessReport:
    assignment_readiness_status: AssignmentReadinessStatus
    eligible_cells_declared: bool
    minimum_structure_requirements_met: bool
    blocked_by_cell_structure: bool
    blocked_by_contrast_structure: bool
    blocked_by_scenario_conflict: bool
    requires_recheck: bool


@dataclass(frozen=True)
class MethodSuitabilityRequirementReport:
    method_suitability_review_required: bool
    dosage_estimand_review_required: bool
    contrast_ids_requiring_review: tuple[str, ...]


@dataclass(frozen=True)
class DesignCellClaimBoundaryReport:
    runtime_design_cell_structure_validation_implemented: bool = True
    cell_role_validation_implemented: bool = True
    contrast_structure_validation_implemented: bool = True
    shared_control_dependency_validation_implemented: bool = True
    scenario_feasibility_handoff_readiness_implemented: bool = True
    assignment_readiness_validation_implemented: bool = True
    scenario_policy_feasibility_computed: bool = False
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
class DesignStructureRuntimeReport:
    design_id: str
    design_structure_status: DesignStructureStatus
    assignment_readiness_status: AssignmentReadinessStatus
    scenario_feasibility_handoff_ready: bool
    structure_type: str | None
    readiness_report: DesignCellReadinessReport
    cell_report: DesignCellRoleReport
    contrast_report: DesignContrastStructureReport
    contrast_specific_role_report: ContrastSpecificRoleReport
    shared_control_dependency_report: SharedControlDependencyReport
    manipulation_policy_report: ManipulationPolicyCompatibilityReport
    estimand_requirement_report: EstimandRequirementReport
    scenario_feasibility_handoff_report: ScenarioFeasibilityHandoffReport
    assignment_readiness_report: AssignmentReadinessReport
    method_suitability_requirement_report: MethodSuitabilityRequirementReport
    claim_boundary_report: DesignCellClaimBoundaryReport
    issues: tuple[StructureIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True)
class DesignCellStructureRuntimeReport:
    artifact_id: str
    design_id: str | None
    design_structure_status: DesignStructureStatus | None
    assignment_readiness_status: AssignmentReadinessStatus | None
    scenario_feasibility_handoff_ready: bool
    structure_type: str | None
    design_reports: tuple[DesignStructureRuntimeReport, ...]
    aggregate_summary: str | None
    cell_report: DesignCellRoleReport | None
    contrast_report: DesignContrastStructureReport | None
    contrast_specific_role_report: ContrastSpecificRoleReport | None
    shared_control_dependency_report: SharedControlDependencyReport | None
    manipulation_policy_report: ManipulationPolicyCompatibilityReport | None
    estimand_requirement_report: EstimandRequirementReport | None
    method_suitability_requirement_report: MethodSuitabilityRequirementReport | None
    claim_boundary_report: DesignCellClaimBoundaryReport
    issues: tuple[StructureIssue, ...]
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
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


def _is_bau_policy(policy: str | None, is_bau_flag: bool = False) -> bool:
    pol_ok = _token(policy) in _BAU_POLICIES or ("BAU" in _token(policy) and _token(policy) != "")
    if policy and pol_ok:
        return True
    if policy and not pol_ok:
        return False
    return is_bau_flag


def _contrast_cell_ids(contrast: dict[str, Any]) -> tuple[str | None, str | None]:
    t = contrast.get("treatment_cell_id") or contrast.get("left_cell_id")
    c = contrast.get("comparison_cell_id") or contrast.get("right_cell_id")
    return (str(t) if t is not None else None, str(c) if c is not None else None)


def _normalize_structures(input_data: Any) -> list[dict[str, Any]]:
    if isinstance(input_data, list):
        if input_data and all(isinstance(x, dict) for x in input_data):
            if "design_id" in input_data[0] or "cells" in input_data[0]:
                return [dict(x) for x in input_data]
    data = _to_dict(input_data)
    if "designs" in data and isinstance(data["designs"], list):
        return [dict(d) for d in data["designs"] if isinstance(d, dict)]
    if "cells" in data or "design_id" in data:
        return [data]
    return [data] if data else [{"design_id": "design_unspecified"}]


def _build_readiness(
    design: dict[str, Any],
    cells: list[dict[str, Any]],
    contrasts: list[dict[str, Any]],
    deps: list[dict[str, Any]],
    cfg: DesignCellStructureConfig,
) -> DesignCellReadinessReport:
    upstream = design.get("upstream_statuses") or {}
    if not isinstance(upstream, dict):
        upstream = {}
    issues: list[StructureIssue] = []

    def gate_status(key: str) -> GateStatus:
        val = upstream.get(key)
        if val is None:
            return GateStatus.NOT_EVALUATED
        if _is_blocked(val):
            return GateStatus.BLOCKED
        if _is_ready(val):
            return GateStatus.PASS
        return GateStatus.WARNING

    profiler = gate_status("profiler_status")
    geo = gate_status("geo_feasibility_status")
    spend = gate_status("spend_feasibility_status")
    power = gate_status("power_mde_status")

    cell_gate = GateStatus.PASS if cells else GateStatus.BLOCKED
    contrast_gate = GateStatus.PASS if contrasts else GateStatus.BLOCKED
    shared_gate = GateStatus.PASS if deps or not contrasts else GateStatus.WARNING
    handoff_gate = GateStatus.NOT_EVALUATED

    if profiler == GateStatus.BLOCKED:
        issues.append(StructureIssue("PROFILER_BLOCKED", "Profiler gate blocked", IssueSeverity.BLOCKING))
    if geo == GateStatus.BLOCKED:
        issues.append(StructureIssue("GEO_BLOCKED", "Geo feasibility blocked", IssueSeverity.BLOCKING))
    if spend == GateStatus.BLOCKED:
        issues.append(StructureIssue("SPEND_BLOCKED", "Spend feasibility blocked", IssueSeverity.BLOCKING))
    if not cells:
        issues.append(StructureIssue("MISSING_CELLS", "No cells declared", IssueSeverity.BLOCKING))
    if not contrasts:
        issues.append(StructureIssue("MISSING_CONTRASTS", "No contrasts declared", IssueSeverity.BLOCKING))

    return DesignCellReadinessReport(
        profiler_gate=profiler,
        geo_unit_market_feasibility_gate=geo,
        spend_feasibility_gate=spend,
        power_mde_readiness_gate=power,
        design_cell_declaration_gate=cell_gate,
        contrast_declaration_gate=contrast_gate,
        shared_control_declaration_gate=shared_gate,
        scenario_feasibility_handoff_gate=handoff_gate,
        issues=tuple(issues),
    )


def _validate_cells(
    cells: list[dict[str, Any]],
    structure_type: str | None,
    cfg: DesignCellStructureConfig,
    issues: list[StructureIssue],
    *,
    split_control_redesign_marker: bool = False,
) -> DesignCellRoleReport:
    ids = [str(c.get("cell_id", "")) for c in cells]
    seen: dict[str, int] = {}
    for cid in ids:
        seen[cid] = seen.get(cid, 0) + 1
    duplicates = tuple(cid for cid, n in seen.items() if n > 1 and cid)

    valid_roles: list[str] = []
    unknown_roles: list[str] = []
    common: list[str] = []
    bau: list[str] = []
    test: list[str] = []
    excluded: list[str] = []
    eligible: list[str] = []

    for cell in cells:
        cid = str(cell.get("cell_id", ""))
        role = _token(cell.get("cell_role"))
        if role in CELL_ROLES and role != "UNKNOWN":
            valid_roles.append(role)
        else:
            unknown_roles.append(role or "MISSING")
            sev = IssueSeverity.BLOCKING if cfg.unknown_cell_role_is_blocking else IssueSeverity.WARNING
            issues.append(StructureIssue("UNKNOWN_CELL_ROLE", f"Unknown cell role for {cid}", sev, "cell_role"))
        if role in _COMMON_CONTROL_ROLES or cell.get("is_common_control"):
            common.append(cid)
        if role in _BAU_ROLES or cell.get("is_bau_policy"):
            bau.append(cid)
        if role in _TREATMENT_ROLES or role == "TEST_CELL":
            test.append(cid)
        if role == "EXCLUDED":
            excluded.append(cid)
        if cell.get("eligible_for_assignment", True) and role != "EXCLUDED":
            eligible.append(cid)

    if duplicates:
        issues.append(
            StructureIssue(
                "DUPLICATE_CELL_IDS",
                f"Duplicate cell IDs: {', '.join(duplicates)}",
                IssueSeverity.BLOCKING,
            )
        )

    st = _token(structure_type)
    if st == "MULTI_CELL_COMMON_CONTROL" and not common:
        sev = IssueSeverity.BLOCKING if cfg.missing_shared_control_dependency_is_blocking else IssueSeverity.WARNING
        issues.append(StructureIssue("MISSING_COMMON_CONTROL", "Common-control design lacks common control cell", sev))
    if st == "SINGLE_TREATMENT_CONTROL":
        if not test:
            issues.append(StructureIssue("MISSING_TREATMENT", "Single treatment/control design lacks treatment cell", IssueSeverity.BLOCKING))
        if not bau:
            issues.append(StructureIssue("MISSING_CONTROL", "Single treatment/control design lacks control cell", IssueSeverity.BLOCKING))
    if st == "MULTI_CELL_SPLIT_CONTROL" and not split_control_redesign_marker and len(bau) < 2:
        issues.append(
            StructureIssue(
                "SPLIT_CONTROL_REQUIRES_SEPARATE_CONTROLS",
                "Split-control design requires separate controls or redesign marker",
                IssueSeverity.BLOCKING,
            )
        )

    return DesignCellRoleReport(
        cell_count=len(cells),
        unique_cell_ids=tuple(dict.fromkeys(ids)),
        duplicate_cell_ids=duplicates,
        valid_cell_roles=tuple(valid_roles),
        unknown_cell_roles=tuple(unknown_roles),
        common_control_cells=tuple(common),
        bau_control_cells=tuple(bau),
        test_cells=tuple(test),
        excluded_cells=tuple(excluded),
        assignment_eligible_cells=tuple(eligible),
    )


def _validate_contrasts(
    contrasts: list[dict[str, Any]],
    cell_ids: set[str],
    cfg: DesignCellStructureConfig,
    issues: list[StructureIssue],
) -> DesignContrastStructureReport:
    valid_types: list[str] = []
    unknown_types: list[str] = []
    missing_refs: list[str] = []
    valid_refs: list[str] = []
    bau_req: list[str] = []
    dosage: list[str] = []
    diff_policy: list[str] = []
    budget: list[str] = []
    method_review: list[str] = []
    blocked: list[str] = []
    roles_present = True

    for contrast in contrasts:
        cid = str(contrast.get("contrast_id", ""))
        ctype = _token(contrast.get("contrast_type"))
        t_id, c_id = _contrast_cell_ids(contrast)

        if ctype in CONTRAST_TYPES and ctype != "UNKNOWN":
            valid_types.append(ctype)
        else:
            unknown_types.append(ctype or "MISSING")
            sev = IssueSeverity.BLOCKING if cfg.unknown_contrast_type_is_blocking else IssueSeverity.WARNING
            issues.append(StructureIssue("UNKNOWN_CONTRAST_TYPE", f"Unknown contrast type for {cid}", sev))
            blocked.append(cid)

        for ref_id, label in ((t_id, "treatment"), (c_id, "comparison")):
            if ref_id is None:
                missing_refs.append(f"{cid}:{label}")
                issues.append(StructureIssue("MISSING_CELL_REF", f"Contrast {cid} missing {label} cell", IssueSeverity.BLOCKING))
                blocked.append(cid)
            elif ref_id not in cell_ids:
                missing_refs.append(f"{cid}:{ref_id}")
                issues.append(StructureIssue("UNDECLARED_CELL_REF", f"Contrast {cid} references undeclared cell {ref_id}", IssueSeverity.BLOCKING))
                blocked.append(cid)
            else:
                valid_refs.append(ref_id)

        if cfg.require_contrast_specific_roles and not contrast.get("contrast_specific_roles"):
            roles_present = False
            issues.append(StructureIssue("MISSING_CONTRAST_ROLES", f"Contrast {cid} missing contrast_specific_roles", IssueSeverity.WARNING))

        if contrast.get("bau_control_required") or ctype in {"GO_DARK_VS_BAU", "HEAVY_UP_VS_BAU", "MULTI_CELL_COMMON_CONTROL_CONTRAST"}:
            bau_req.append(cid)
        if ctype == "DOSAGE_LOW_VS_HIGH" or contrast.get("dosage_contrast_estimand_required"):
            dosage.append(cid)
        if ctype == "DIFFERENCE_IN_POLICY" or contrast.get("difference_in_policy_required"):
            diff_policy.append(cid)
        if ctype == "BUDGET_REALLOCATION_SOURCE_VS_DESTINATION":
            budget.append(cid)
        if contrast.get("method_suitability_review_required"):
            method_review.append(cid)

    return DesignContrastStructureReport(
        contrast_count=len(contrasts),
        valid_contrast_types=tuple(valid_types),
        unknown_contrast_types=tuple(unknown_types),
        missing_cell_references=tuple(missing_refs),
        valid_cell_references=tuple(valid_refs),
        contrast_specific_roles_present=roles_present,
        bau_control_required_contrasts=tuple(bau_req),
        dosage_contrasts=tuple(dosage),
        difference_in_policy_contrasts=tuple(diff_policy),
        budget_reallocation_contrasts=tuple(budget),
        method_suitability_required_contrasts=tuple(method_review),
        blocked_contrast_ids=tuple(dict.fromkeys(blocked)),
    )


def _validate_contrast_specific_roles(
    contrasts: list[dict[str, Any]],
    cells_by_id: dict[str, dict[str, Any]],
    cfg: DesignCellStructureConfig,
    issues: list[StructureIssue],
) -> ContrastSpecificRoleReport:
    entries: list[ContrastSpecificRoleEntry] = []
    contradictory: list[str] = []

    for contrast in contrasts:
        cid = str(contrast.get("contrast_id", ""))
        ctype = _token(contrast.get("contrast_type"))
        roles_map = contrast.get("contrast_specific_roles") or {}
        if not isinstance(roles_map, dict):
            continue

        role_values: list[str] = []
        for cell_id, role in roles_map.items():
            r = _token(role)
            role_values.append(r)
            compatible = r in CONTRAST_SPECIFIC_ROLES and r != "UNKNOWN"
            conflicts: list[str] = []

            cell = cells_by_id.get(str(cell_id), {})
            policy = _token(cell.get("manipulation_policy"))

            if r == "BAU_CONTROL_FOR_CONTRAST" and not _is_bau_policy(policy, bool(cell.get("is_bau_policy"))):
                conflicts.append("BAU_CONTROL_REQUIRES_BAU_POLICY")
                issues.append(StructureIssue("BAU_ROLE_POLICY_MISMATCH", f"Cell {cell_id} is BAU_CONTROL_FOR_CONTRAST without BAU policy", IssueSeverity.BLOCKING))

            if r == "LOW_POLICY_ANCHOR_FOR_CONTRAST" and ctype not in {"DOSAGE_LOW_VS_HIGH", "DIFFERENCE_IN_POLICY"}:
                conflicts.append("LOW_ANCHOR_REQUIRES_DOSAGE_OR_DIFF_POLICY")
                issues.append(StructureIssue("LOW_ANCHOR_INCOMPATIBLE", f"Cell {cell_id} LOW_POLICY_ANCHOR incompatible with {ctype}", IssueSeverity.WARNING))

            if ctype == "GO_DARK_VS_BAU" and r == "TREATMENT_FOR_CONTRAST" and policy not in {"GO_DARK", ""} and policy != "UNKNOWN":
                if policy not in {"GO_DARK"}:
                    conflicts.append("GO_DARK_ROLE_EXPECTED")

            entries.append(
                ContrastSpecificRoleEntry(
                    contrast_id=cid,
                    cell_id=str(cell_id),
                    contrast_specific_role=r,
                    compatible_with_contrast_type=compatible and not conflicts,
                    role_conflicts=tuple(conflicts),
                )
            )

        t_id, c_id = _contrast_cell_ids(contrast)
        if t_id and c_id and t_id == c_id:
            contradictory.append(cid)
            issues.append(
                StructureIssue(
                    "CONTRADICTORY_ROLES",
                    f"Contrast {cid} uses same cell for treatment and comparison",
                    IssueSeverity.BLOCKING,
                )
            )

        if "TREATMENT_FOR_CONTRAST" in role_values and "COMPARISON_FOR_CONTRAST" in role_values:
            t_cells = [k for k, v in roles_map.items() if _token(v) == "TREATMENT_FOR_CONTRAST"]
            c_cells = [k for k, v in roles_map.items() if _token(v) == "COMPARISON_FOR_CONTRAST"]
            if t_cells and c_cells and t_cells[0] == c_cells[0]:
                contradictory.append(cid)
                issues.append(StructureIssue("CONTRADICTORY_ROLES", f"Contradictory roles in contrast {cid}", IssueSeverity.BLOCKING))

        if ctype in {"GO_DARK_VS_BAU", "HEAVY_UP_VS_BAU"}:
            has_bau = any(_token(v) == "BAU_CONTROL_FOR_CONTRAST" for v in roles_map.values())
            if not has_bau and contrast.get("bau_control_required", True):
                issues.append(StructureIssue("MISSING_BAU_CONTROL_ROLE", f"Contrast {cid} requires BAU control role", IssueSeverity.BLOCKING))

        if ctype == "DOSAGE_LOW_VS_HIGH":
            has_low = any(_token(v) == "LOW_POLICY_ANCHOR_FOR_CONTRAST" for v in roles_map.values())
            has_high = any(_token(v) == "HIGH_POLICY_CELL_FOR_CONTRAST" for v in roles_map.values())
            if not (has_low or has_high or contrast.get("dosage_contrast_estimand_required")):
                issues.append(StructureIssue("MISSING_DOSAGE_ROLES", f"Dosage contrast {cid} missing low/high roles", IssueSeverity.BLOCKING))

        if ctype == "BUDGET_REALLOCATION_SOURCE_VS_DESTINATION":
            has_src = any(_token(v) == "SOURCE_CELL_FOR_REALLOCATION_CONTRAST" for v in roles_map.values())
            has_dst = any(_token(v) == "DESTINATION_CELL_FOR_REALLOCATION_CONTRAST" for v in roles_map.values())
            if not has_src or not has_dst:
                issues.append(StructureIssue("MISSING_REALLOCATION_ROLES", f"Budget reallocation {cid} missing source/destination roles", IssueSeverity.BLOCKING))

    return ContrastSpecificRoleReport(entries=tuple(entries), contradictory_contrast_ids=tuple(contradictory))


def _validate_manipulation_policies(
    cells: list[dict[str, Any]],
    cfg: DesignCellStructureConfig,
    issues: list[StructureIssue],
) -> ManipulationPolicyCompatibilityReport:
    entries: list[ManipulationPolicyEntry] = []
    incompatible: list[str] = []

    for cell in cells:
        cid = str(cell.get("cell_id", ""))
        role = _token(cell.get("cell_role"))
        policy = _token(cell.get("manipulation_policy"))
        conflicts: list[str] = []
        compatible = True

        if role in {"BUSINESS_AS_USUAL_CONTROL"} or cell.get("is_bau_policy"):
            if cfg.require_bau_policy_for_bau_control and not _is_bau_policy(policy, bool(cell.get("is_bau_policy"))):
                conflicts.append("BAU_CONTROL_REQUIRES_BAU_POLICY")
                compatible = False
                issues.append(StructureIssue("BAU_POLICY_MISMATCH", f"BAU control {cid} has non-BAU policy", IssueSeverity.BLOCKING))

        if policy == "GO_DARK" and role in _BAU_ROLES:
            conflicts.append("GO_DARK_ON_BAU_CONTROL")
            compatible = False
            issues.append(StructureIssue("GO_DARK_ON_CONTROL", f"GO_DARK policy on BAU control {cid}", IssueSeverity.BLOCKING))

        if policy == "HEAVY_UP" and role in _BAU_ROLES and policy != "DIFFERENCE_IN_POLICY":
            conflicts.append("HEAVY_UP_ON_BAU_REQUIRES_REFRAME")
            compatible = False
            issues.append(StructureIssue("HEAVY_UP_ON_BAU", f"HEAVY_UP on BAU control {cid} requires difference-in-policy", IssueSeverity.BLOCKING))

        if policy == "BUDGET_REALLOCATION_SOURCE" and role not in {"SOURCE_REDUCTION"} | {"UNKNOWN"}:
            if role != "SOURCE_REDUCTION":
                conflicts.append("SOURCE_POLICY_ROLE_MISMATCH")
                compatible = False

        if policy == "BUDGET_REALLOCATION_DESTINATION" and role != "DESTINATION_INCREASE":
            conflicts.append("DESTINATION_POLICY_ROLE_MISMATCH")
            compatible = False

        if policy == "GO_LIVE" and role not in {"GO_LIVE_CELL", "TEST_CELL", "TREATMENT"}:
            conflicts.append("GO_LIVE_ROLE_MISMATCH")
            compatible = False

        if not compatible:
            incompatible.append(cid)

        entries.append(
            ManipulationPolicyEntry(
                cell_id=cid,
                cell_role=role or None,
                manipulation_policy=policy or None,
                policy_compatible_with_role=compatible,
                policy_conflicts=tuple(conflicts),
            )
        )

    return ManipulationPolicyCompatibilityReport(entries=tuple(entries), incompatible_cell_ids=tuple(incompatible))


def _validate_shared_control_dependencies(
    design: dict[str, Any],
    contrasts: list[dict[str, Any]],
    cells_by_id: dict[str, dict[str, Any]],
    contrast_ids: set[str],
    cfg: DesignCellStructureConfig,
    issues: list[StructureIssue],
) -> SharedControlDependencyReport:
    deps_raw = design.get("shared_control_dependencies") or []
    if not isinstance(deps_raw, list):
        deps_raw = []

    cell_usage: dict[str, list[str]] = {}
    for contrast in contrasts:
        cid = str(contrast.get("contrast_id", ""))
        t_id, c_id = _contrast_cell_ids(contrast)
        for ref in (t_id, c_id):
            if ref:
                cell_usage.setdefault(ref, []).append(cid)

    implied_shared = tuple(cid for cid, users in cell_usage.items() if len(set(users)) > 1)
    declared_ids = {str(d.get("shared_cell_id") or d.get("control_cell_id", "")) for d in deps_raw if isinstance(d, dict)}
    missing_decl = tuple(cid for cid in implied_shared if cid not in declared_ids)

    if missing_decl:
        sev = IssueSeverity.BLOCKING if cfg.missing_shared_control_dependency_is_blocking else IssueSeverity.WARNING
        issues.append(
            StructureIssue(
                "MISSING_SHARED_CONTROL_DEP",
                f"Implied shared cells missing dependency declaration: {', '.join(missing_decl)}",
                sev,
            )
        )

    entries: list[SharedControlDependencyEntry] = []
    ambiguity = False

    for dep in deps_raw:
        if not isinstance(dep, dict):
            continue
        sid = str(dep.get("shared_cell_id") or dep.get("control_cell_id", ""))
        dep_contrasts = dep.get("dependent_contrast_ids") or []
        if isinstance(dep_contrasts, list):
            dep_ids = tuple(str(x) for x in dep_contrasts)
        else:
            dep_ids = ()
        role_by = dep.get("role_by_contrast")
        role_present = isinstance(role_by, dict) and bool(role_by)
        required_policy = dep.get("required_policy")
        if isinstance(required_policy, str):
            req_pol = required_policy
        else:
            req_pol = None

        cell = cells_by_id.get(sid, {})
        bau_required = _token(req_pol) == "BUSINESS_AS_USUAL" or dep.get("bau_control_preservation_required")
        if bau_required and not _is_bau_policy(_token(cell.get("manipulation_policy")), bool(cell.get("is_bau_policy"))):
            issues.append(StructureIssue("SHARED_BAU_NOT_PRESERVED", f"Shared cell {sid} requires BAU but policy is not BAU", IssueSeverity.BLOCKING))

        amb = False
        if role_by and isinstance(role_by, dict):
            roles = set(_token(v) for v in role_by.values())
            if "BAU_CONTROL_FOR_CONTRAST" in roles and "LOW_POLICY_ANCHOR_FOR_CONTRAST" in roles:
                amb = True
                ambiguity = True
                issues.append(StructureIssue("SHARED_CONTROL_AMBIGUITY", f"Ambiguous roles for shared cell {sid}", IssueSeverity.BLOCKING))

        entries.append(
            SharedControlDependencyEntry(
                shared_cell_id=sid,
                dependent_contrast_ids=dep_ids,
                shared_cell_declared=sid in cells_by_id,
                dependent_contrasts_exist=all(d in contrast_ids for d in dep_ids),
                shared_policy_required=req_pol,
                role_by_contrast_present=role_present,
                ambiguity_detected=amb,
                bau_control_preservation_required=bool(bau_required),
            )
        )

    return SharedControlDependencyReport(
        entries=tuple(entries),
        implied_shared_cells=implied_shared,
        missing_dependency_declarations=missing_decl,
        ambiguity_detected=ambiguity,
    )


def _build_estimand_report(
    contrast_report: DesignContrastStructureReport,
    manipulation_report: ManipulationPolicyCompatibilityReport,
    shared_report: SharedControlDependencyReport,
    cells: list[dict[str, Any]],
) -> EstimandRequirementReport:
    bau_not_preserved = any(
        not _is_bau_policy(_token(c.get("manipulation_policy")), bool(c.get("is_bau_policy")))
        for c in cells
        if c.get("is_bau_policy") or _token(c.get("cell_role")) in _BAU_ROLES
    )
    contamination: list[str] = []
    for e in manipulation_report.entries:
        if e.policy_conflicts:
            contamination.extend(e.policy_conflicts)

    std_go_dark = not bau_not_preserved and not contrast_report.dosage_contrasts
    std_heavy_up = not bau_not_preserved and not contrast_report.difference_in_policy_contrasts

    return EstimandRequirementReport(
        standard_go_dark_allowed=std_go_dark and bool(contrast_report.bau_control_required_contrasts),
        standard_heavy_up_allowed=std_heavy_up and bool(contrast_report.bau_control_required_contrasts),
        dosage_contrast_estimand_required=bool(contrast_report.dosage_contrasts),
        difference_in_policy_required=bool(contrast_report.difference_in_policy_contrasts),
        budget_reallocation_estimand_required=bool(contrast_report.budget_reallocation_contrasts),
        bau_control_not_preserved=bau_not_preserved or shared_report.ambiguity_detected,
        control_contamination_flags=tuple(dict.fromkeys(contamination)),
    )


def _build_handoff_report(
    design: dict[str, Any],
    cell_report: DesignCellRoleReport,
    contrast_report: DesignContrastStructureReport,
    manipulation_report: ManipulationPolicyCompatibilityReport,
    shared_report: SharedControlDependencyReport,
    issues: list[StructureIssue],
    cfg: DesignCellStructureConfig,
) -> ScenarioFeasibilityHandoffReport:
    missing: list[str] = []
    if cell_report.cell_count == 0:
        missing.append("cells")
    if contrast_report.contrast_count == 0:
        missing.append("contrasts")
    if not contrast_report.contrast_specific_roles_present and cfg.require_contrast_specific_roles:
        missing.append("contrast_specific_roles")
    if manipulation_report.incompatible_cell_ids:
        missing.append("compatible_policies")
    if shared_report.missing_dependency_declarations and cfg.missing_shared_control_dependency_is_blocking:
        missing.append("shared_control_dependencies")
    if cfg.require_scenario_policy_plan_for_handoff and not design.get("scenario_policy_plan_available"):
        missing.append("scenario_policy_plan")

    cells_ready = cell_report.cell_count > 0 and not cell_report.duplicate_cell_ids
    contrasts_ready = contrast_report.contrast_count > 0 and not contrast_report.blocked_contrast_ids
    policies_ready = not manipulation_report.incompatible_cell_ids
    deps_ready = not shared_report.missing_dependency_declarations or not cfg.missing_shared_control_dependency_is_blocking
    fields_ok = not missing

    blocking = [i for i in issues if i.severity == IssueSeverity.BLOCKING]
    handoff_ready = cells_ready and contrasts_ready and policies_ready and deps_ready and fields_ok and not blocking

    return ScenarioFeasibilityHandoffReport(
        handoff_ready=handoff_ready,
        required_fields_present=fields_ok,
        cells_ready=cells_ready,
        contrasts_ready=contrasts_ready,
        policies_ready=policies_ready,
        shared_control_dependencies_ready=deps_ready,
        missing_handoff_fields=tuple(missing),
    )


def _select_design_status(
    readiness: DesignCellReadinessReport,
    cell_report: DesignCellRoleReport,
    contrast_report: DesignContrastStructureReport,
    shared_report: SharedControlDependencyReport,
    estimand: EstimandRequirementReport,
    method_report: MethodSuitabilityRequirementReport,
    issues: list[StructureIssue],
    warnings: list[str],
) -> DesignStructureStatus:
    if readiness.profiler_gate == GateStatus.BLOCKED:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_DATA_READINESS
    if readiness.geo_unit_market_feasibility_gate == GateStatus.BLOCKED:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_GEO_FEASIBILITY
    if readiness.spend_feasibility_gate == GateStatus.BLOCKED:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_SPEND_FEASIBILITY
    if readiness.power_mde_readiness_gate == GateStatus.BLOCKED:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_POWER_MDE_READINESS
    if cell_report.cell_count == 0:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CELLS
    if cell_report.duplicate_cell_ids:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CELL_ROLES
    if contrast_report.contrast_count == 0:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CONTRASTS
    if contrast_report.blocked_contrast_ids or contrast_report.missing_cell_references:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS
    if shared_report.ambiguity_detected:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_SHARED_CONTROL_AMBIGUITY
    if method_report.dosage_estimand_review_required:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_REQUIRES_DOSAGE_ESTIMAND_REVIEW
    if method_report.method_suitability_review_required:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_REQUIRES_METHOD_SUITABILITY_REVIEW
    if warnings and not [i for i in issues if i.severity == IssueSeverity.BLOCKING]:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_READY_WITH_WARNINGS
    if [i for i in issues if i.severity == IssueSeverity.BLOCKING]:
        return DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS
    return DesignStructureStatus.DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY


def _select_assignment_status(
    design_status: DesignStructureStatus,
    design: dict[str, Any],
    handoff: ScenarioFeasibilityHandoffReport,
    method_report: MethodSuitabilityRequirementReport,
    readiness: DesignCellReadinessReport,
    contrast_report: DesignContrastStructureReport,
    cfg: DesignCellStructureConfig,
    warnings: list[str],
) -> AssignmentReadinessStatus:
    if readiness.profiler_gate == GateStatus.BLOCKED:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_DATA_READINESS
    if readiness.geo_unit_market_feasibility_gate == GateStatus.BLOCKED:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_GEO_FEASIBILITY
    if readiness.spend_feasibility_gate == GateStatus.BLOCKED:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_SPEND_FEASIBILITY
    if readiness.power_mde_readiness_gate == GateStatus.BLOCKED:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_POWER_MDE_READINESS

    blocked_structure = {
        DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CELLS,
        DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CELL_ROLES,
        DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_SHARED_CONTROL_AMBIGUITY,
    }
    if design_status in blocked_structure:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE
    if design_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_INVALID_CONTRASTS:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_CONTRAST_STRUCTURE
    if design_status == DesignStructureStatus.DESIGN_CELL_STRUCTURE_BLOCKED_BY_MISSING_CONTRASTS:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_CONTRAST_STRUCTURE

    upstream = design.get("upstream_statuses") or {}
    spf = _token(upstream.get("scenario_policy_feasibility_status")) if isinstance(upstream, dict) else ""
    if spf and (_is_blocked(spf) or "CONFLICT" in spf or "BLOCKED" in spf):
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT
    if spf and "PROVISIONAL" in spf:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_PROVISIONAL

    if design.get("split_control_redesign_marker"):
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK
    if method_report.method_suitability_review_required:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_REQUIRES_METHOD_SUITABILITY_REVIEW
    if method_report.dosage_estimand_review_required:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_REQUIRES_DOSAGE_ESTIMAND_REVIEW

    if not handoff.handoff_ready:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE

    if warnings and cfg.allow_assignment_readiness_with_warnings:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_READY_WITH_WARNINGS
    if warnings:
        return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_PROVISIONAL

    return AssignmentReadinessStatus.DESIGN_ASSIGNMENT_READY_FOR_RUNTIME


def _evaluate_single_structure(
    design: dict[str, Any],
    cfg: DesignCellStructureConfig,
) -> DesignStructureRuntimeReport:
    design_id = str(design.get("design_id") or "design_unspecified")
    structure_type = design.get("design_structure_type")
    cells_raw = design.get("cells") or []
    contrasts_raw = design.get("contrasts") or []
    deps_raw = design.get("shared_control_dependencies") or []
    cells = [c for c in cells_raw if isinstance(c, dict)]
    contrasts = [c for c in contrasts_raw if isinstance(c, dict)]
    deps = [d for d in deps_raw if isinstance(d, dict)]
    cells_by_id = {str(c.get("cell_id")): c for c in cells if c.get("cell_id") is not None}
    cell_ids = set(cells_by_id.keys())
    contrast_ids = {str(c.get("contrast_id", "")) for c in contrasts}

    issues: list[StructureIssue] = []
    warnings: list[str] = []

    readiness = _build_readiness(design, cells, contrasts, deps, cfg)
    cell_report = _validate_cells(
        cells,
        str(structure_type) if structure_type else None,
        cfg,
        issues,
        split_control_redesign_marker=bool(design.get("split_control_redesign_marker")),
    )
    contrast_report = _validate_contrasts(contrasts, cell_ids, cfg, issues)
    role_report = _validate_contrast_specific_roles(contrasts, cells_by_id, cfg, issues)
    manipulation_report = _validate_manipulation_policies(cells, cfg, issues)
    shared_report = _validate_shared_control_dependencies(design, contrasts, cells_by_id, contrast_ids, cfg, issues)
    estimand_report = _build_estimand_report(contrast_report, manipulation_report, shared_report, cells)

    method_ids = contrast_report.method_suitability_required_contrasts
    if estimand_report.dosage_contrast_estimand_required:
        method_ids = tuple(dict.fromkeys((*method_ids, *contrast_report.dosage_contrasts)))
    method_report = MethodSuitabilityRequirementReport(
        method_suitability_review_required=bool(method_ids) or estimand_report.difference_in_policy_required,
        dosage_estimand_review_required=estimand_report.dosage_contrast_estimand_required,
        contrast_ids_requiring_review=method_ids,
    )

    handoff_report = _build_handoff_report(
        design, cell_report, contrast_report, manipulation_report, shared_report, issues, cfg
    )

    for i in issues:
        if i.severity == IssueSeverity.WARNING:
            warnings.append(i.message)

    design_status = _select_design_status(
        readiness, cell_report, contrast_report, shared_report, estimand_report, method_report, issues, warnings
    )
    assignment_status = _select_assignment_status(
        design_status, design, handoff_report, method_report, readiness, contrast_report, cfg, warnings
    )

    assignment_report = AssignmentReadinessReport(
        assignment_readiness_status=assignment_status,
        eligible_cells_declared=bool(cell_report.assignment_eligible_cells),
        minimum_structure_requirements_met=handoff_report.cells_ready and handoff_report.contrasts_ready,
        blocked_by_cell_structure=assignment_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_CELL_STRUCTURE,
        blocked_by_contrast_structure=assignment_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_CONTRAST_STRUCTURE,
        blocked_by_scenario_conflict=assignment_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_BLOCKED_BY_SCENARIO_CONFLICT,
        requires_recheck=assignment_status == AssignmentReadinessStatus.DESIGN_ASSIGNMENT_REQUIRES_REDESIGN_RECHECK,
    )

    blocking_reasons = tuple(i.message for i in issues if i.severity == IssueSeverity.BLOCKING)

    return DesignStructureRuntimeReport(
        design_id=design_id,
        design_structure_status=design_status,
        assignment_readiness_status=assignment_status,
        scenario_feasibility_handoff_ready=handoff_report.handoff_ready,
        structure_type=str(structure_type) if structure_type else None,
        readiness_report=readiness,
        cell_report=cell_report,
        contrast_report=contrast_report,
        contrast_specific_role_report=role_report,
        shared_control_dependency_report=shared_report,
        manipulation_policy_report=manipulation_report,
        estimand_requirement_report=estimand_report,
        scenario_feasibility_handoff_report=handoff_report,
        assignment_readiness_report=assignment_report,
        method_suitability_requirement_report=method_report,
        claim_boundary_report=DesignCellClaimBoundaryReport(),
        issues=tuple(issues),
        warnings=tuple(warnings),
        blocking_reasons=blocking_reasons,
    )


def evaluate_design_cell_structure(
    input_data: Any,
    config: DesignCellStructureConfig | None = None,
) -> DesignCellStructureRuntimeReport:
    """Validate declared design-cell structure. Does not compute scenario policy feasibility."""
    cfg = config or DesignCellStructureConfig()
    designs = _normalize_structures(input_data)
    reports = [_evaluate_single_structure(d, cfg) for d in designs]

    all_issues: list[StructureIssue] = []
    all_warnings: list[str] = []
    all_blocking: list[str] = []
    for r in reports:
        all_issues.extend(r.issues)
        all_warnings.extend(r.warnings)
        all_blocking.extend(r.blocking_reasons)

    if len(reports) == 1:
        r = reports[0]
        return DesignCellStructureRuntimeReport(
            artifact_id=_ARTIFACT_ID,
            design_id=r.design_id,
            design_structure_status=r.design_structure_status,
            assignment_readiness_status=r.assignment_readiness_status,
            scenario_feasibility_handoff_ready=r.scenario_feasibility_handoff_ready,
            structure_type=r.structure_type,
            design_reports=(r,),
            aggregate_summary=None,
            cell_report=r.cell_report,
            contrast_report=r.contrast_report,
            contrast_specific_role_report=r.contrast_specific_role_report,
            shared_control_dependency_report=r.shared_control_dependency_report,
            manipulation_policy_report=r.manipulation_policy_report,
            estimand_requirement_report=r.estimand_requirement_report,
            method_suitability_requirement_report=r.method_suitability_requirement_report,
            claim_boundary_report=r.claim_boundary_report,
            issues=r.issues,
            warnings=r.warnings,
            blocking_reasons=r.blocking_reasons,
        )

    return DesignCellStructureRuntimeReport(
        artifact_id=_ARTIFACT_ID,
        design_id=None,
        design_structure_status=None,
        assignment_readiness_status=None,
        scenario_feasibility_handoff_ready=all(r.scenario_feasibility_handoff_ready for r in reports),
        structure_type=None,
        design_reports=tuple(reports),
        aggregate_summary=f"Validated {len(reports)} declared structures without ranking",
        cell_report=None,
        contrast_report=None,
        contrast_specific_role_report=None,
        shared_control_dependency_report=None,
        manipulation_policy_report=None,
        estimand_requirement_report=None,
        method_suitability_requirement_report=None,
        claim_boundary_report=DesignCellClaimBoundaryReport(),
        issues=tuple(all_issues),
        warnings=tuple(all_warnings),
        blocking_reasons=tuple(dict.fromkeys(all_blocking)),
    )


validate_design_cell_structure = evaluate_design_cell_structure


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    design = {
        "design_id": "smoke_multi_cell_common_control",
        "design_structure_type": "MULTI_CELL_COMMON_CONTROL",
        "upstream_statuses": {
            "profiler_status": "PASS",
            "geo_feasibility_status": "PASS",
            "spend_feasibility_status": "PASS",
            "power_mde_status": "PASS",
        },
        "cells": [
            {"cell_id": "C0", "cell_role": "COMMON_CONTROL", "manipulation_policy": "BUSINESS_AS_USUAL", "is_common_control": True, "is_bau_policy": True, "eligible_for_assignment": True},
            {"cell_id": "T1", "cell_role": "TEST_CELL", "manipulation_policy": "GO_DARK", "eligible_for_assignment": True},
            {"cell_id": "T2", "cell_role": "TEST_CELL", "manipulation_policy": "HEAVY_UP", "eligible_for_assignment": True},
        ],
        "contrasts": [
            {
                "contrast_id": "T1_vs_C0",
                "contrast_type": "GO_DARK_VS_BAU",
                "treatment_cell_id": "T1",
                "comparison_cell_id": "C0",
                "bau_control_required": True,
                "contrast_specific_roles": {"T1": "TREATMENT_FOR_CONTRAST", "C0": "BAU_CONTROL_FOR_CONTRAST"},
            },
            {
                "contrast_id": "T2_vs_C0",
                "contrast_type": "HEAVY_UP_VS_BAU",
                "treatment_cell_id": "T2",
                "comparison_cell_id": "C0",
                "bau_control_required": True,
                "contrast_specific_roles": {"T2": "TREATMENT_FOR_CONTRAST", "C0": "BAU_CONTROL_FOR_CONTRAST"},
            },
        ],
        "shared_control_dependencies": [
            {"shared_cell_id": "C0", "dependent_contrast_ids": ["T1_vs_C0", "T2_vs_C0"], "required_policy": "BUSINESS_AS_USUAL", "role_by_contrast": {"T1_vs_C0": "BAU_CONTROL_FOR_CONTRAST", "T2_vs_C0": "BAU_CONTROL_FOR_CONTRAST"}},
        ],
    }
    report = evaluate_design_cell_structure(design)
    failed: list[str] = []
    if report.design_structure_status != DesignStructureStatus.DESIGN_CELL_STRUCTURE_READY_FOR_SCENARIO_FEASIBILITY:
        failed.append("smoke_status")
    if not report.scenario_feasibility_handoff_ready:
        failed.append("smoke_handoff")
    if report.claim_boundary_report.scenario_policy_feasibility_computed:
        failed.append("smoke_no_scenario_feasibility")

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "design_cell_structure_runtime",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "scope": "runtime_validates_declared_structures_no_assignment_or_scenario_feasibility_computation",
        "depends_on": [
            "GEO_KPI_SPEND_DATA_PROFILER_001",
            "GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001",
            "SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001",
            "POWER_MDE_DIAGNOSTICS_RUNTIME_001",
            "DESIGN_CELL_STRUCTURE_AND_ASSIGNMENT_CONTRACT_001",
            "DESIGN_SCENARIO_POLICY_FEASIBILITY_RUNTIME_001",
        ],
        "public_api": "evaluate_design_cell_structure",
        "runtime_design_cell_structure_validation_implemented": True,
        "cell_role_validation_implemented": True,
        "contrast_structure_validation_implemented": True,
        "contrast_specific_role_validation_implemented": True,
        "manipulation_policy_compatibility_implemented": True,
        "shared_control_dependency_validation_implemented": True,
        "estimand_requirement_detection_implemented": True,
        "scenario_feasibility_handoff_readiness_implemented": True,
        "assignment_readiness_validation_implemented": True,
        "scenario_policy_feasibility_computed": False,
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
        "smoke_design_status": report.design_structure_status.value if report.design_structure_status else None,
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
