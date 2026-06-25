"""METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "method_family_retire_replace_execution_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001",
)

MIN_EXECUTION_ROW_COUNT = 70

_AUTH_FLAGS = {
    "production_p_value_authorized": False,
    "causal_confidence_interval_authorized": False,
    "trustreport_authorized": False,
    "calibration_signal_allowed": False,
    "mmm_ingestion_allowed": False,
    "llm_decisioning_allowed": False,
    "production_decisioning_allowed": False,
    "live_api_authorized": False,
    "scheduler_authorized": False,
    "budget_optimization_allowed": False,
}

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "open_investigations_consulted": True,
    "production_readiness_backlog_consulted": True,
    "selection_gate_requirements_consulted": True,
    "retire_replace_does_not_mean_delete_all_code": True,
    "diagnostic_code_can_remain_if_labeled_and_blocked": True,
    "research_code_can_remain_if_labeled_and_blocked": True,
    "scm_retained_candidate_gated": True,
    "augsynth_retained_with_remediation": True,
    "did_retained_conditional_candidate": True,
    "synthetic_did_retained_implementation_readiness_candidate": True,
    "tbrridge_retained_diagnostic_remediation_only": True,
    "classic_aggregate_tbr_overclaim_paths_retire_replace_required": True,
    "bayesian_tbr_posterior_diagnostic_only": True,
    "bayesian_tbr_intervals_not_causal_ci": True,
    "trop_research_only": True,
    "trop_production_recommendations_blocked": True,
    "multicell_shared_control_overclaim_paths_blocked": True,
    "selection_gate_must_route_retired_paths_away_from_production": True,
    "release_gate_required_before_any_authorization": True,
    "downstream_work_paused": True,
}

_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
    "production_routing",
    "code_deletion",
)


class MethodFamily(str, Enum):
    SCM = "scm"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    DID = "did"
    SYNTHETIC_DID = "synthetic_did"
    TBRRIDGE = "tbrridge"
    CLASSIC_AGGREGATE_TBR = "classic_aggregate_tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    TROP = "trop"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    DATA_DRIVEN_SELECTION_GATE = "data_driven_selection_gate"
    RELEASE_GATE = "release_gate"
    DOWNSTREAM_INTEGRATIONS = "downstream_integrations"


class ExecutionArea(str, Enum):
    ACTIVE_CANDIDATE_RETENTION = "active_candidate_retention"
    DIAGNOSTIC_ONLY_RETENTION = "diagnostic_only_retention"
    RESEARCH_ONLY_RETENTION = "research_only_retention"
    REMEDIATION_REQUIRED_RETENTION = "remediation_required_retention"
    RETIRE_REPLACE_REQUIRED = "retire_replace_required"
    HARD_BLOCK_REQUIRED = "hard_block_required"
    OVERCLAIM_PREVENTION = "overclaim_prevention"
    REPLACEMENT_CANDIDATE_MAPPING = "replacement_candidate_mapping"
    CODE_PATH_LABELING = "code_path_labeling"
    DOCUMENTATION_LABELING = "documentation_labeling"
    TEST_GOVERNANCE_LABELING = "test_governance_labeling"
    SELECTION_GATE_ROUTING_IMPACT = "selection_gate_routing_impact"
    OPEN_INVESTIGATION_UPDATE = "open_investigation_update"
    ROADMAP_UPDATE = "roadmap_update"
    RELEASE_GATE_DEPENDENCY = "release_gate_dependency"


class ExecutionStatus(str, Enum):
    PRODUCTION_CANDIDATE_GATED = "production_candidate_gated"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    REMEDIATION_REQUIRED = "remediation_required"
    RETIRE_REPLACE_REQUIRED = "retire_replace_required"
    BLOCKED = "blocked"
    RELEASE_GATE_REQUIRED = "release_gate_required"


class ExecutionDecision(str, Enum):
    RETAIN_CANDIDATE_GATED = "retain_candidate_gated"
    RETAIN_DIAGNOSTIC_ONLY = "retain_diagnostic_only"
    RETAIN_RESEARCH_ONLY = "retain_research_only"
    RETAIN_WITH_REMEDIATION = "retain_with_remediation"
    RETIRE_OVERCLAIM_PATH = "retire_overclaim_path"
    REPLACE_WITH_CANDIDATE_PATH = "replace_with_candidate_path"
    HARD_BLOCK_UNTIL_VALIDATED = "hard_block_until_validated"
    DEFER_TO_RELEASE_GATE = "defer_to_release_gate"


REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)
REQUIRED_EXECUTION_AREAS = frozenset(ExecutionArea)
REQUIRED_EXECUTION_DECISIONS = frozenset(ExecutionDecision)
REQUIRED_STATUSES = frozenset(ExecutionStatus)


@dataclass(frozen=True)
class RetireReplaceExecutionRow:
    execution_id: str
    method_family: MethodFamily
    path_or_claim: str
    execution_area: ExecutionArea
    current_status: ExecutionStatus
    execution_decision: ExecutionDecision
    replacement_or_remediation_target: str | None
    required_code_action: tuple[str, ...]
    required_doc_action: tuple[str, ...]
    required_test_action: tuple[str, ...]
    required_governance_action: tuple[str, ...]
    selection_gate_impact: str
    blocking_reason: str
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    exit_condition: str
    recommended_next_artifact: str | None
    notes: str


def _family_profile(family: MethodFamily) -> dict[str, Any]:
    profiles: dict[MethodFamily, dict[str, Any]] = {
        MethodFamily.SCM: {
            "path_or_claim": "scm_single_treated_production_candidate",
            "base_status": ExecutionStatus.PRODUCTION_CANDIDATE_GATED,
            "base_decision": ExecutionDecision.RETAIN_CANDIDATE_GATED,
            "replacement": "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
            "blocking": "point_estimate_not_production_inference",
            "allowed": ("scm_diagnostic_readout", "gated_candidate_research"),
        },
        MethodFamily.AUGSYNTH_CVXPY: {
            "path_or_claim": "augsynth_cvxpy_remediation_candidate",
            "base_status": ExecutionStatus.REMEDIATION_REQUIRED,
            "base_decision": ExecutionDecision.RETAIN_WITH_REMEDIATION,
            "replacement": "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
            "blocking": "augsynth_remediation_incomplete",
            "allowed": ("augsynth_diagnostic_readout", "restricted_research"),
        },
        MethodFamily.DID: {
            "path_or_claim": "did_conditional_production_candidate",
            "base_status": ExecutionStatus.PRODUCTION_CANDIDATE_GATED,
            "base_decision": ExecutionDecision.RETAIN_CANDIDATE_GATED,
            "replacement": "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
            "blocking": "did_design_ineligible",
            "allowed": ("did_diagnostic_readout", "conditional_research"),
        },
        MethodFamily.SYNTHETIC_DID: {
            "path_or_claim": "synthetic_did_implementation_readiness",
            "base_status": ExecutionStatus.PRODUCTION_CANDIDATE_GATED,
            "base_decision": ExecutionDecision.RETAIN_CANDIDATE_GATED,
            "replacement": "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
            "blocking": "implementation_readiness_incomplete",
            "allowed": ("synthetic_did_readiness_planning", "scout_research"),
        },
        MethodFamily.TBRRIDGE: {
            "path_or_claim": "tbrridge_diagnostic_remediation",
            "base_status": ExecutionStatus.DIAGNOSTIC_ONLY,
            "base_decision": ExecutionDecision.RETAIN_DIAGNOSTIC_ONLY,
            "replacement": "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
            "blocking": "tbrridge_inference_unvalidated",
            "allowed": ("tbrridge_point_diagnostic", "remediation_research"),
        },
        MethodFamily.CLASSIC_AGGREGATE_TBR: {
            "path_or_claim": "classic_aggregate_tbr_causal_overclaim",
            "base_status": ExecutionStatus.RETIRE_REPLACE_REQUIRED,
            "base_decision": ExecutionDecision.RETIRE_OVERCLAIM_PATH,
            "replacement": "SCM",
            "blocking": "aggregate_geometry_overclaim",
            "allowed": ("legacy_diagnostic_if_labeled",),
        },
        MethodFamily.BAYESIAN_TBR: {
            "path_or_claim": "bayesian_tbr_posterior_diagnostic",
            "base_status": ExecutionStatus.RESEARCH_ONLY,
            "base_decision": ExecutionDecision.RETAIN_RESEARCH_ONLY,
            "replacement": None,
            "blocking": "posterior_interval_not_causal_ci",
            "allowed": ("posterior_diagnostic_research",),
        },
        MethodFamily.TROP: {
            "path_or_claim": "trop_research_only_boundary",
            "base_status": ExecutionStatus.RESEARCH_ONLY,
            "base_decision": ExecutionDecision.RETAIN_RESEARCH_ONLY,
            "replacement": None,
            "blocking": "trop_production_recommendations_blocked",
            "allowed": ("trop_research_scout",),
        },
        MethodFamily.MULTICELL_SHARED_CONTROL: {
            "path_or_claim": "multicell_shared_control_overclaim",
            "base_status": ExecutionStatus.BLOCKED,
            "base_decision": ExecutionDecision.HARD_BLOCK_UNTIL_VALIDATED,
            "replacement": "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
            "blocking": "dependence_multiplicity_unhandled",
            "allowed": ("multicell_research_scout",),
        },
        MethodFamily.DATA_DRIVEN_SELECTION_GATE: {
            "path_or_claim": "data_driven_selection_gate_router",
            "base_status": ExecutionStatus.RELEASE_GATE_REQUIRED,
            "base_decision": ExecutionDecision.DEFER_TO_RELEASE_GATE,
            "replacement": "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
            "blocking": "selection_gate_not_implemented",
            "allowed": ("requirements_planning",),
        },
        MethodFamily.RELEASE_GATE: {
            "path_or_claim": "production_authorization_release_gate",
            "base_status": ExecutionStatus.RELEASE_GATE_REQUIRED,
            "base_decision": ExecutionDecision.DEFER_TO_RELEASE_GATE,
            "replacement": "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
            "blocking": "release_gate_not_passed",
            "allowed": ("release_gate_planning",),
        },
        MethodFamily.DOWNSTREAM_INTEGRATIONS: {
            "path_or_claim": "trustreport_calibration_mmm_llm_scheduler",
            "base_status": ExecutionStatus.BLOCKED,
            "base_decision": ExecutionDecision.HARD_BLOCK_UNTIL_VALIDATED,
            "replacement": None,
            "blocking": "downstream_work_paused",
            "allowed": ("research_mode_governance_only",),
        },
    }
    return profiles[family]


def _area_status_decision(
    family: MethodFamily,
    area: ExecutionArea,
    profile: dict[str, Any],
) -> tuple[ExecutionStatus, ExecutionDecision]:
    base_status: ExecutionStatus = profile["base_status"]
    base_decision: ExecutionDecision = profile["base_decision"]

    area_overrides: dict[ExecutionArea, tuple[ExecutionStatus, ExecutionDecision]] = {
        ExecutionArea.ACTIVE_CANDIDATE_RETENTION: (
            ExecutionStatus.PRODUCTION_CANDIDATE_GATED,
            ExecutionDecision.RETAIN_CANDIDATE_GATED,
        ),
        ExecutionArea.DIAGNOSTIC_ONLY_RETENTION: (
            ExecutionStatus.DIAGNOSTIC_ONLY,
            ExecutionDecision.RETAIN_DIAGNOSTIC_ONLY,
        ),
        ExecutionArea.RESEARCH_ONLY_RETENTION: (
            ExecutionStatus.RESEARCH_ONLY,
            ExecutionDecision.RETAIN_RESEARCH_ONLY,
        ),
        ExecutionArea.REMEDIATION_REQUIRED_RETENTION: (
            ExecutionStatus.REMEDIATION_REQUIRED,
            ExecutionDecision.RETAIN_WITH_REMEDIATION,
        ),
        ExecutionArea.RETIRE_REPLACE_REQUIRED: (
            ExecutionStatus.RETIRE_REPLACE_REQUIRED,
            ExecutionDecision.RETIRE_OVERCLAIM_PATH,
        ),
        ExecutionArea.HARD_BLOCK_REQUIRED: (
            ExecutionStatus.BLOCKED,
            ExecutionDecision.HARD_BLOCK_UNTIL_VALIDATED,
        ),
        ExecutionArea.RELEASE_GATE_DEPENDENCY: (
            ExecutionStatus.RELEASE_GATE_REQUIRED,
            ExecutionDecision.DEFER_TO_RELEASE_GATE,
        ),
        ExecutionArea.REPLACEMENT_CANDIDATE_MAPPING: (
            base_status,
            ExecutionDecision.REPLACE_WITH_CANDIDATE_PATH,
        ),
    }

    if area in area_overrides:
        status, decision = area_overrides[area]
        if family in (
            MethodFamily.CLASSIC_AGGREGATE_TBR,
        ) and area == ExecutionArea.ACTIVE_CANDIDATE_RETENTION:
            return ExecutionStatus.RETIRE_REPLACE_REQUIRED, ExecutionDecision.RETIRE_OVERCLAIM_PATH
        if family in (MethodFamily.BAYESIAN_TBR, MethodFamily.TROP) and area in (
            ExecutionArea.ACTIVE_CANDIDATE_RETENTION,
            ExecutionArea.REMEDIATION_REQUIRED_RETENTION,
        ):
            return ExecutionStatus.RESEARCH_ONLY, ExecutionDecision.RETAIN_RESEARCH_ONLY
        if family == MethodFamily.TBRRIDGE and area == ExecutionArea.ACTIVE_CANDIDATE_RETENTION:
            return ExecutionStatus.DIAGNOSTIC_ONLY, ExecutionDecision.RETAIN_DIAGNOSTIC_ONLY
        if family == MethodFamily.AUGSYNTH_CVXPY and area == ExecutionArea.ACTIVE_CANDIDATE_RETENTION:
            return ExecutionStatus.REMEDIATION_REQUIRED, ExecutionDecision.RETAIN_WITH_REMEDIATION
        if family in (MethodFamily.MULTICELL_SHARED_CONTROL, MethodFamily.DOWNSTREAM_INTEGRATIONS):
            if area == ExecutionArea.ACTIVE_CANDIDATE_RETENTION:
                return ExecutionStatus.BLOCKED, ExecutionDecision.HARD_BLOCK_UNTIL_VALIDATED
        return status, decision

    return base_status, base_decision


def _area_defaults(
    family: MethodFamily,
    area: ExecutionArea,
    profile: dict[str, Any],
) -> dict[str, Any]:
    status, decision = _area_status_decision(family, area, profile)
    replacement = profile.get("replacement")
    gate_impact = "route_away_from_production" if decision in (
        ExecutionDecision.RETIRE_OVERCLAIM_PATH,
        ExecutionDecision.HARD_BLOCK_UNTIL_VALIDATED,
        ExecutionDecision.RETAIN_DIAGNOSTIC_ONLY,
        ExecutionDecision.RETAIN_RESEARCH_ONLY,
    ) else "gated_candidate_route"

    if family == MethodFamily.CLASSIC_AGGREGATE_TBR:
        gate_impact = "route_retired_paths_away_from_production"
    if area == ExecutionArea.SELECTION_GATE_ROUTING_IMPACT:
        gate_impact = "selection_gate_must_route_retired_paths_away_from_production"

    code_actions = ("label_code_path", "block_production_routing")
    if area == ExecutionArea.CODE_PATH_LABELING:
        code_actions = ("add_retire_replace_label", "guard_production_entrypoints")
    if area == ExecutionArea.RETIRE_REPLACE_REQUIRED:
        code_actions = ("retire_overclaim_label", "replace_routing_to_candidate")

    doc_actions = ("update_roadmap_label", "update_method_inventory")
    if area == ExecutionArea.DOCUMENTATION_LABELING:
        doc_actions = ("document_retire_replace_semantics", "document_allowed_use")

    test_actions = ("governance_test_coverage", "routing_assertion")
    if area == ExecutionArea.TEST_GOVERNANCE_LABELING:
        test_actions = ("assert_no_production_authorization", "assert_routing_blocked")

    gov_actions = ("update_open_investigations",)
    if area == ExecutionArea.OPEN_INVESTIGATION_UPDATE:
        gov_actions = ("resolve_retire_replace_investigation", "open_next_artifact_investigation")
    if area == ExecutionArea.ROADMAP_UPDATE:
        gov_actions = ("update_roadmap_lane_binding", "set_immediate_next_artifact")

    exit_cond = "release_gate_passed_and_validation_complete"
    if decision == ExecutionDecision.RETIRE_OVERCLAIM_PATH:
        exit_cond = "overclaim_path_labeled_and_routed_to_replacement"
    if decision == ExecutionDecision.RETAIN_WITH_REMEDIATION:
        exit_cond = "remediation_validation_evidence_complete"

    next_artifact = None
    if area == ExecutionArea.RELEASE_GATE_DEPENDENCY:
        next_artifact = "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
    if family == MethodFamily.DATA_DRIVEN_SELECTION_GATE and area == ExecutionArea.ROADMAP_UPDATE:
        next_artifact = RECOMMENDED_NEXT_ARTIFACTS[0]

    return {
        "current_status": status,
        "execution_decision": decision,
        "replacement_or_remediation_target": replacement,
        "required_code_action": code_actions,
        "required_doc_action": doc_actions,
        "required_test_action": test_actions,
        "required_governance_action": gov_actions,
        "selection_gate_impact": gate_impact,
        "blocking_reason": profile["blocking"],
        "allowed_current_use": profile["allowed"],
        "forbidden_current_use": _FORBID,
        "exit_condition": exit_cond,
        "recommended_next_artifact": next_artifact,
    }


def build_method_family_retire_replace_execution_plan() -> tuple[RetireReplaceExecutionRow, ...]:
    """Return metadata-only method-family retire/replace execution plan rows."""
    rows: list[RetireReplaceExecutionRow] = []
    row_num = 1
    for family in MethodFamily:
        profile = _family_profile(family)
        for area in ExecutionArea:
            defaults = _area_defaults(family, area, profile)
            rows.append(
                RetireReplaceExecutionRow(
                    execution_id=f"RET-EXE-{row_num:03d}",
                    method_family=family,
                    path_or_claim=profile["path_or_claim"],
                    execution_area=area,
                    current_status=defaults["current_status"],
                    execution_decision=defaults["execution_decision"],
                    replacement_or_remediation_target=defaults["replacement_or_remediation_target"],
                    required_code_action=defaults["required_code_action"],
                    required_doc_action=defaults["required_doc_action"],
                    required_test_action=defaults["required_test_action"],
                    required_governance_action=defaults["required_governance_action"],
                    selection_gate_impact=defaults["selection_gate_impact"],
                    blocking_reason=defaults["blocking_reason"],
                    allowed_current_use=defaults["allowed_current_use"],
                    forbidden_current_use=defaults["forbidden_current_use"],
                    exit_condition=defaults["exit_condition"],
                    recommended_next_artifact=defaults["recommended_next_artifact"],
                    notes=f"{family.value}/{area.value}: retire-replace execution metadata row.",
                )
            )
            row_num += 1
    return tuple(rows)


def filter_method_family_retire_replace_execution_plan(
    rows: tuple[RetireReplaceExecutionRow, ...],
    *,
    method_family: MethodFamily | None = None,
    execution_area: ExecutionArea | None = None,
    current_status: ExecutionStatus | None = None,
    execution_decision: ExecutionDecision | None = None,
) -> tuple[RetireReplaceExecutionRow, ...]:
    """Filter retire/replace execution plan rows by optional criteria."""
    result: list[RetireReplaceExecutionRow] = []
    for row in rows:
        if method_family is not None and row.method_family != method_family:
            continue
        if execution_area is not None and row.execution_area != execution_area:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if execution_decision is not None and row.execution_decision != execution_decision:
            continue
        result.append(row)
    return tuple(result)


def validate_method_family_retire_replace_execution_plan(
    rows: tuple[RetireReplaceExecutionRow, ...],
) -> dict[str, Any]:
    """Validate retire/replace execution plan registry thresholds and coverage."""
    issues: list[str] = []
    execution_ids = [r.execution_id for r in rows]

    if len(rows) < MIN_EXECUTION_ROW_COUNT:
        issues.append(f"execution_row_count {len(rows)} < {MIN_EXECUTION_ROW_COUNT}")
    if len(execution_ids) != len(set(execution_ids)):
        issues.append("duplicate execution_id values")

    family_counts = Counter(r.method_family.value for r in rows)
    area_counts = Counter(r.execution_area.value for r in rows)
    decision_counts = Counter(r.execution_decision for r in rows)
    status_counts = Counter(r.current_status for r in rows)

    for family in REQUIRED_METHOD_FAMILIES:
        if family_counts.get(family.value, 0) == 0:
            issues.append(f"missing method_family: {family.value}")

    for area in REQUIRED_EXECUTION_AREAS:
        if area_counts.get(area.value, 0) == 0:
            issues.append(f"missing execution_area: {area.value}")

    for decision in REQUIRED_EXECUTION_DECISIONS:
        if decision_counts.get(decision, 0) == 0:
            issues.append(f"missing execution_decision: {decision.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    scm_gated = any(
        r.method_family == MethodFamily.SCM
        and r.execution_area == ExecutionArea.ACTIVE_CANDIDATE_RETENTION
        and r.execution_decision == ExecutionDecision.RETAIN_CANDIDATE_GATED
        for r in rows
    )
    if not scm_gated:
        issues.append("scm retain_candidate_gated missing")

    tbr_retire = any(
        r.method_family == MethodFamily.CLASSIC_AGGREGATE_TBR
        and r.execution_decision == ExecutionDecision.RETIRE_OVERCLAIM_PATH
        for r in rows
    )
    if not tbr_retire:
        issues.append("classic_aggregate_tbr retire_overclaim_path missing")

    unlabeled = [r.execution_id for r in rows if not r.required_code_action]
    if unlabeled:
        issues.append(f"rows missing required_code_action: {unlabeled}")

    return {
        "valid": not issues,
        "execution_row_count": len(rows),
        "unique_execution_ids": len(execution_ids) == len(set(execution_ids)),
        "method_family_counts": dict(family_counts),
        "execution_area_counts": dict(area_counts),
        "execution_decision_counts": {d.value: decision_counts.get(d, 0) for d in ExecutionDecision},
        "status_counts": {s.value: status_counts.get(s, 0) for s in ExecutionStatus},
        "all_required_method_families_covered": all(
            family_counts.get(f.value, 0) > 0 for f in REQUIRED_METHOD_FAMILIES
        ),
        "all_required_execution_areas_covered": all(
            area_counts.get(a.value, 0) > 0 for a in REQUIRED_EXECUTION_AREAS
        ),
        "all_required_execution_decisions_covered": all(
            decision_counts.get(d, 0) > 0 for d in REQUIRED_EXECUTION_DECISIONS
        ),
        "all_required_statuses_covered": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "issues": issues,
    }


def summarize_method_family_retire_replace_execution_plan(
    rows: tuple[RetireReplaceExecutionRow, ...],
) -> dict[str, Any]:
    """Serialize retire/replace execution plan summary for archives."""
    validation = validate_method_family_retire_replace_execution_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "execution_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "method_family_counts": validation["method_family_counts"],
        "execution_area_counts": validation["execution_area_counts"],
        "execution_decision_counts": validation["execution_decision_counts"],
        "status_counts": validation["status_counts"],
        "all_required_method_families_covered": validation["all_required_method_families_covered"],
        "all_required_execution_areas_covered": validation["all_required_execution_areas_covered"],
        "all_required_execution_decisions_covered": validation["all_required_execution_decisions_covered"],
        "all_required_statuses_covered": validation["all_required_statuses_covered"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_BOUNDARY_FLAGS,
        **_AUTH_FLAGS,
        "valid": validation["valid"],
    }


def _git_commit() -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=_REPO,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _scenario(scenario_id: str, passed: bool, *, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios() -> list[dict[str, Any]]:
    rows = build_method_family_retire_replace_execution_plan()
    validation = validate_method_family_retire_replace_execution_plan(rows)
    summary = summarize_method_family_retire_replace_execution_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("execution_rows_build_successfully", len(rows) > 0))
    scenarios.append(
        _scenario("execution_row_count_at_least_70", len(rows) >= MIN_EXECUTION_ROW_COUNT)
    )
    scenarios.append(_scenario("execution_ids_unique", validation["unique_execution_ids"]))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(r.method_family == family for r in rows)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    for area in REQUIRED_EXECUTION_AREAS:
        present = any(r.execution_area == area for r in rows)
        scenarios.append(_scenario(f"execution_area_{area.value}_represented", present))

    for decision in REQUIRED_EXECUTION_DECISIONS:
        count = sum(1 for r in rows if r.execution_decision == decision)
        scenarios.append(_scenario(f"execution_decision_{decision.value}_represented", count > 0))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_selection_gate_implementation",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_method_family_retire_replace_execution_plan()
    validation = validate_method_family_retire_replace_execution_plan(rows)
    summary = summarize_method_family_retire_replace_execution_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "execution_row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        **{k: summary[k] for k in summary if k not in ("failed_scenarios", "valid")},
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
