"""SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_release_gate_review_plan_defined_no_authorization_granted"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_RELEASE_GATE_REVIEW_PACKET_001",
)

MIN_PLAN_ROW_COUNT = 70
METHOD_FAMILY = "SCM"
METHOD_FAMILY_STATUS = "production_candidate_gated"

INPUT_CONTRACT = "SCMReleaseGateReviewInput"
DECISION_CONTRACT = "SCMReleaseGateReviewDecision"

_AUTH_FLAGS = {
    "scm_production_p_value_authorized": False,
    "scm_causal_confidence_interval_authorized": False,
    "production_authorization_granted": False,
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
    "data_driven_selection_gate_implementation_authorized": False,
    "selector_implementation_authorized": False,
    "production_selection_router_authorized": False,
    "scm_production_inference_authorized": False,
    "multicell_production_claim_authorized": False,
    "package_side_agents_authorized": False,
}

_SCM_FLAGS = {
    "scm_release_gate_review_plan_completed": False,
    "scm_release_gate_approval_granted": False,
    "scm_production_inference_authorized": False,
}

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "scm_remains_gated_production_candidate": True,
    "review_plan_not_release_gate_approval": True,
    "evidence_stack_metadata_only": True,
    "validation_metadata_not_production_valid": True,
    "null_calibration_metadata_not_p_value_authorization": True,
    "jackknife_metadata_not_causal_ci_authorization": True,
    "multicell_boundary_separate": True,
    "selector_shadow_only_until_authorized": True,
    "human_governance_review_required": True,
    "revocation_expiration_rollback_required_before_authorization": True,
    "package_side_agents_deferred": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "review_plan_only_no_release_gate_runtime": True,
    "downstream_work_paused": True,
}

RELEASE_GATE_DOMAINS = (
    "method_family_authorization",
    "estimator_authorization",
    "inference_authorization",
    "causal_uncertainty_authorization",
    "production_p_value_authorization",
    "multicell_claim_authorization",
    "selector_router_authorization",
    "trustreport_authorization",
    "calibration_signal_authorization",
    "mmm_ingestion_authorization",
    "llm_decisioning_authorization",
    "live_api_authorization",
    "scheduler_authorization",
    "budget_optimization_authorization",
    "package_side_agent_authorization",
)

EVIDENCE_PREREQUISITES = (
    "estimand_contract_complete",
    "observed_panel_diagnostics_complete",
    "assignment_design_validity_complete",
    "method_family_validation_complete",
    "simulation_dgp_coverage_complete",
    "failure_registry_review_complete",
    "null_calibration_complete_where_applicable",
    "multicell_dependence_multiplicity_validation_complete_where_applicable",
    "selector_router_shadow_validation_complete_where_applicable",
    "production_readiness_backlog_closed_or_waived",
    "open_investigations_closed_or_explicitly_deferred",
    "retire_replace_state_respected",
    "audit_references_complete",
    "human_governance_review_complete",
    "rollback_or_revocation_path_defined",
)

REVIEW_STATUSES = (
    "metadata_scaffold_present",
    "review_required",
    "eligible_for_review",
    "blocked",
    "not_authorized",
    "release_gate_required",
    "not_applicable",
)

INPUT_FIELDS = (
    "scm_validation_evidence",
    "scm_null_calibration_evidence",
    "scm_jackknife_sensitivity_evidence",
    "method_family_status",
    "estimator_status",
    "inference_status",
    "causal_uncertainty_status",
    "p_value_status",
    "multicell_status",
    "selector_router_status",
    "production_readiness_backlog_state",
    "open_investigations_state",
    "retire_replace_state",
    "simulation_dgp_evidence_state",
    "failure_registry_state",
    "audit_references",
    "human_review_state",
    "rollback_revocation_plan",
    "review_scope",
    "review_date",
    "audit_context",
)

DECISION_FIELDS = (
    "review_status",
    "release_gate_status",
    "method_family_authorization_status",
    "estimator_authorization_status",
    "inference_authorization_status",
    "p_value_authorization_status",
    "causal_ci_authorization_status",
    "multicell_authorization_status",
    "selector_router_authorization_status",
    "downstream_authorization_status",
    "evidence_prerequisite_statuses",
    "satisfied_prerequisites",
    "blocked_prerequisites",
    "warnings",
    "required_followups",
    "allowed_current_use",
    "forbidden_current_use",
    "conditions",
    "expiration_or_review_date",
    "revocation_triggers",
    "human_review_required",
    "audit_references",
    "authorization_flags",
)

STAGES = (
    "stage_0_review_scope_and_packet_definition",
    "stage_1_evidence_stack_inventory",
    "stage_2_prerequisite_status_review",
    "stage_3_method_family_and_estimator_review",
    "stage_4_inference_pvalue_causal_ci_boundary_review",
    "stage_5_multicell_selector_downstream_boundary_review",
    "stage_6_human_governance_review_requirements",
    "stage_7_revocation_expiration_and_rollback_plan",
    "stage_8_release_gate_review_packet_preparation",
    "stage_9_future_release_gate_decision_artifact",
)

STAGE_ASPECTS = ("purpose", "inputs", "outputs", "acceptance_criteria", "non_goals", "authorization_boundary")

SCM_EVIDENCE_STACK = (
    "scm_validation_metadata_scaffold",
    "scm_null_calibration_metadata_scaffold",
    "scm_jackknife_sensitivity_metadata_scaffold",
)

REQUIRED_FOLLOWUPS = (
    "SCM-RG-RF-VALIDATION-STATISTICAL-COMPLETE",
    "SCM-RG-RF-NULL-CALIBRATION-STATISTICAL-COMPLETE",
    "SCM-RG-RF-JACKKNIFE-STATISTICAL-COMPLETE",
    "SCM-RG-RF-DGP-COVERAGE",
    "SCM-RG-RF-FAILURE-REGISTRY",
    "SCM-RG-RF-MULTICELL-VALIDATION",
    "SCM-RG-RF-SELECTOR-SHADOW",
    "SCM-RG-RF-PRODUCTION-READINESS-BACKLOG",
    "SCM-RG-RF-HUMAN-GOVERNANCE-REVIEW",
    "SCM-RG-RF-ROLLBACK-REVOCATION-PLAN",
    "SCM-RG-RF-RELEASE-GATE-REVIEW-PACKET",
    "SCM-RG-RF-FUTURE-RELEASE-GATE-DECISION",
)

DEPENDENCIES_RECONCILED = (
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",
)

NON_GOALS = (
    "no_release_gate_approval_granted",
    "no_release_gate_runtime",
    "no_scm_production_inference_authorization",
    "no_production_p_values_or_causal_cis",
    "no_selector_router_production_use",
    "no_multicell_scm_production_claims",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_package_side_agent_authorization",
    "no_automatic_authorization_from_metadata_scaffolds",
    "no_skipping_human_governance_review",
    "no_skipping_evidence_prerequisites",
)

DOMAIN_PROFILES: dict[str, dict[str, Any]] = {
    "method_family_authorization": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "scm_evidence": ("scm_validation_metadata_scaffold",),
        "review_status": "review_required",
        "current": "not_authorized",
    },
    "estimator_authorization": {
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "scm_evidence": ("scm_validation_metadata_scaffold",),
        "review_status": "review_required",
        "current": "not_authorized",
    },
    "inference_authorization": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",),
        "scm_evidence": ("scm_null_calibration_metadata_scaffold",),
        "review_status": "review_required",
        "current": "not_authorized",
    },
    "causal_uncertainty_authorization": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",),
        "scm_evidence": ("scm_jackknife_sensitivity_metadata_scaffold",),
        "review_status": "review_required",
        "current": "not_authorized",
    },
    "production_p_value_authorization": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",),
        "scm_evidence": ("scm_null_calibration_metadata_scaffold",),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "multicell_claim_authorization": {
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "blocked",
    },
    "selector_router_authorization": {
        "artifacts": ("DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",),
        "scm_evidence": ("scm_validation_metadata_scaffold",),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "trustreport_authorization": {
        "artifacts": ("FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "calibration_signal_authorization": {
        "artifacts": ("CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "mmm_ingestion_authorization": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "llm_decisioning_authorization": {
        "artifacts": ("FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "blocked",
    },
    "live_api_authorization": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "scheduler_authorization": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "not_authorized",
    },
    "budget_optimization_authorization": {
        "artifacts": ("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "blocked",
    },
    "package_side_agent_authorization": {
        "artifacts": ("FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",),
        "scm_evidence": (),
        "review_status": "blocked",
        "current": "blocked",
    },
}

PREREQUISITE_PROFILES: dict[str, dict[str, Any]] = {
    "estimand_contract_complete": {
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "scm_status": "review_required",
    },
    "observed_panel_diagnostics_complete": {
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "scm_status": "review_required",
    },
    "assignment_design_validity_complete": {
        "artifacts": ("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
        "scm_status": "review_required",
    },
    "method_family_validation_complete": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "scm_status": "metadata_scaffold_present",
    },
    "simulation_dgp_coverage_complete": {
        "artifacts": ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        "scm_status": "review_required",
    },
    "failure_registry_review_complete": {
        "artifacts": ("METHOD_FAILURE_MODE_REGISTRY_001",),
        "scm_status": "review_required",
    },
    "null_calibration_complete_where_applicable": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",),
        "scm_status": "metadata_scaffold_present",
    },
    "multicell_dependence_multiplicity_validation_complete_where_applicable": {
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "scm_status": "blocked",
    },
    "selector_router_shadow_validation_complete_where_applicable": {
        "artifacts": ("DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",),
        "scm_status": "review_required",
    },
    "production_readiness_backlog_closed_or_waived": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "scm_status": "review_required",
    },
    "open_investigations_closed_or_explicitly_deferred": {
        "artifacts": ("OPEN_INVESTIGATIONS_001",),
        "scm_status": "review_required",
    },
    "retire_replace_state_respected": {
        "artifacts": ("METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",),
        "scm_status": "review_required",
    },
    "audit_references_complete": {
        "artifacts": (_ARTIFACT_ID,),
        "scm_status": "metadata_scaffold_present",
    },
    "human_governance_review_complete": {
        "artifacts": ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",),
        "scm_status": "review_required",
    },
    "rollback_or_revocation_path_defined": {
        "artifacts": ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",),
        "scm_status": "metadata_scaffold_present",
    },
}

SCM_EVIDENCE_PROFILES: dict[str, dict[str, Any]] = {
    "scm_validation_metadata_scaffold": {
        "artifact": "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
        "registry_rows": 31,
        "status": "metadata_scaffold_present",
        "authorizes": "none",
    },
    "scm_null_calibration_metadata_scaffold": {
        "artifact": "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
        "registry_rows": 30,
        "status": "metadata_scaffold_present",
        "authorizes": "none",
    },
    "scm_jackknife_sensitivity_metadata_scaffold": {
        "artifact": "SCM_PRODUCTION_CANDIDATE_JACKKNIFE_SENSITIVITY_IMPLEMENTATION_001",
        "registry_rows": 37,
        "status": "metadata_scaffold_present",
        "authorizes": "none",
    },
}


class PlanSection(str, Enum):
    RELEASE_GATE_DOMAIN = "release_gate_domain"
    EVIDENCE_PREREQUISITE = "evidence_prerequisite"
    INPUT_CONTRACT = "input_contract"
    DECISION_CONTRACT = "decision_contract"
    SCM_EVIDENCE_STACK = "scm_evidence_stack"
    STAGE_DEFINITION = "stage_definition"
    NON_GOAL = "non_goal"


REQUIRED_PLAN_SECTIONS = frozenset(PlanSection)


@dataclass(frozen=True)
class SCMReleaseGateReviewPlanRow:
    plan_id: str
    plan_section: PlanSection
    field_or_component: str
    purpose: str
    planned_inputs: str
    planned_outputs: str
    acceptance_criteria: str
    non_goals: str
    authorization_boundary: str
    required_prior_artifacts: tuple[str, ...]
    audit_references: tuple[str, ...]
    review_status: str = "review_required"
    implementation_stage: str | None = None
    notes: str = ""


def _row(
    plan_id: str,
    plan_section: PlanSection,
    field_or_component: str,
    purpose: str,
    planned_inputs: str,
    planned_outputs: str,
    acceptance_criteria: str,
    non_goals: str,
    authorization_boundary: str,
    *,
    required_prior_artifacts: tuple[str, ...],
    audit_references: tuple[str, ...] = (),
    review_status: str = "review_required",
    implementation_stage: str | None = None,
    notes: str = "",
) -> SCMReleaseGateReviewPlanRow:
    return SCMReleaseGateReviewPlanRow(
        plan_id=plan_id,
        plan_section=plan_section,
        field_or_component=field_or_component,
        purpose=purpose,
        planned_inputs=planned_inputs,
        planned_outputs=planned_outputs,
        acceptance_criteria=acceptance_criteria,
        non_goals=non_goals,
        authorization_boundary=authorization_boundary,
        required_prior_artifacts=required_prior_artifacts,
        audit_references=audit_references or required_prior_artifacts,
        review_status=review_status,
        implementation_stage=implementation_stage,
        notes=notes,
    )


def _domain_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    for idx, domain in enumerate(RELEASE_GATE_DOMAINS, start=1):
        profile = DOMAIN_PROFILES[domain]
        rows.append(
            _row(
                f"DOM-{idx:03d}",
                PlanSection.RELEASE_GATE_DOMAIN,
                domain,
                f"SCM release-gate review domain: {domain}; reconcile metadata stack vs authorization.",
                f"SCM evidence stack + {domain} prerequisite state from PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001.",
                f"Review classification for {domain}; current state remains {profile['current']}.",
                "Domain review plan documented; no authorization granted by this plan.",
                "no_release_gate_approval_granted",
                f"{domain}_review_planned_not_authorized",
                required_prior_artifacts=profile["artifacts"],
                review_status=profile["review_status"],
                notes=f"current={profile['current']}; scm_evidence={profile['scm_evidence']}",
            )
        )
    return rows


def _prerequisite_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    for idx, prereq in enumerate(EVIDENCE_PREREQUISITES, start=1):
        profile = PREREQUISITE_PROFILES[prereq]
        rows.append(
            _row(
                f"PRE-{idx:03d}",
                PlanSection.EVIDENCE_PREREQUISITE,
                prereq,
                f"Evidence prerequisite review: {prereq} for SCM release-gate candidacy.",
                f"Prior artifacts + SCM metadata evidence state for {prereq}.",
                f"Prerequisite status classification; SCM current: {profile['scm_status']}.",
                "Prerequisite review criteria defined; not marked complete_for_authorization unless explicit.",
                "no_skipping_evidence_prerequisites",
                "prerequisite_review_metadata_only",
                required_prior_artifacts=profile["artifacts"],
                review_status=profile["scm_status"],
            )
        )
    return rows


def _input_contract_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    for idx, field in enumerate(INPUT_FIELDS, start=1):
        rows.append(
            _row(
                f"INP-{idx:03d}",
                PlanSection.INPUT_CONTRACT,
                field,
                f"Planned SCMReleaseGateReviewInput field: {field}.",
                f"Metadata state for {field} at review time.",
                f"Typed {field} slot in future SCMReleaseGateReviewInput contract.",
                f"Field documented in planned input contract; no runtime approval logic.",
                "no_release_gate_runtime",
                "input_contract_metadata_only",
                required_prior_artifacts=(_ARTIFACT_ID,),
                review_status="metadata_scaffold_present",
            )
        )
    return rows


def _decision_contract_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    for idx, field in enumerate(DECISION_FIELDS, start=1):
        status = "not_authorized" if "authorization" in field else "review_required"
        rows.append(
            _row(
                f"DEC-{idx:03d}",
                PlanSection.DECISION_CONTRACT,
                field,
                f"Planned SCMReleaseGateReviewDecision field: {field}.",
                f"Review inputs and prerequisite statuses for {field}.",
                f"Typed {field} slot in future SCMReleaseGateReviewDecision contract.",
                f"Field documented; current authorization flags remain false.",
                "no_release_gate_approval_granted",
                "decision_contract_metadata_only",
                required_prior_artifacts=(_ARTIFACT_ID,),
                review_status=status,
            )
        )
    return rows


def _scm_evidence_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    for idx, key in enumerate(SCM_EVIDENCE_STACK, start=1):
        profile = SCM_EVIDENCE_PROFILES[key]
        rows.append(
            _row(
                f"EVD-{idx:03d}",
                PlanSection.SCM_EVIDENCE_STACK,
                key,
                f"SCM evidence stack item: {key} from {profile['artifact']}.",
                f"Summary JSON and evidence builder output from {profile['artifact']}.",
                f"Inventory row for release-gate review packet; status={profile['status']}.",
                "Evidence scaffold inventoried; not treated as production-valid inference.",
                "no_automatic_authorization_from_metadata_scaffolds",
                "evidence_stack_non_authorizing",
                required_prior_artifacts=(profile["artifact"],),
                review_status=profile["status"],
                notes=f"registry_rows={profile['registry_rows']}; authorizes={profile['authorizes']}",
            )
        )
    return rows


def _stage_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    stage_purposes = {
        "stage_0_review_scope_and_packet_definition": "Define SCM release-gate review scope and packet outline.",
        "stage_1_evidence_stack_inventory": "Inventory SCM validation/null-calibration/jackknife metadata scaffolds.",
        "stage_2_prerequisite_status_review": "Classify evidence prerequisites as metadata_scaffold_present or review_required.",
        "stage_3_method_family_and_estimator_review": "Review SCM method-family and estimator authorization boundaries.",
        "stage_4_inference_pvalue_causal_ci_boundary_review": "Review inference, p-value, and causal CI boundaries separately.",
        "stage_5_multicell_selector_downstream_boundary_review": "Review multicell, selector/router, and downstream boundaries.",
        "stage_6_human_governance_review_requirements": "Define human governance review requirements before any authorization.",
        "stage_7_revocation_expiration_and_rollback_plan": "Define expiration, review-date, and revocation triggers.",
        "stage_8_release_gate_review_packet_preparation": "Assemble future SCM release-gate review packet artifact inputs.",
        "stage_9_future_release_gate_decision_artifact": "Plan future release-gate decision artifact (not this plan).",
    }
    for idx, stage in enumerate(STAGES, start=1):
        purpose = stage_purposes[stage]
        rows.append(
            _row(
                f"STG-{idx:03d}",
                PlanSection.STAGE_DEFINITION,
                stage,
                purpose,
                f"Inputs: SCM evidence stack, prerequisites, domain states, audit context.",
                f"Outputs: stage review notes for {stage}; no authorization granted.",
                f"Stage {stage} acceptance criteria documented; authorization boundary enforced.",
                "no_release_gate_approval_granted",
                "stage_review_plan_only",
                required_prior_artifacts=(_ARTIFACT_ID, "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"),
                review_status="review_required",
                implementation_stage=stage,
            )
        )
    return rows


def _non_goal_rows() -> list[SCMReleaseGateReviewPlanRow]:
    rows: list[SCMReleaseGateReviewPlanRow] = []
    for idx, goal in enumerate(NON_GOALS, start=1):
        rows.append(
            _row(
                f"NG-{idx:03d}",
                PlanSection.NON_GOAL,
                goal,
                f"Explicit non-goal: {goal}.",
                "N/A",
                "N/A",
                f"Report states {goal}.",
                goal,
                "non_goal_enforced",
                required_prior_artifacts=(_ARTIFACT_ID,),
                review_status="not_applicable",
            )
        )
    return rows


def build_scm_production_candidate_release_gate_review_plan() -> tuple[SCMReleaseGateReviewPlanRow, ...]:
    """Return metadata-only SCM release-gate review plan rows."""
    rows: list[SCMReleaseGateReviewPlanRow] = []
    rows.extend(_domain_rows())
    rows.extend(_prerequisite_rows())
    rows.extend(_input_contract_rows())
    rows.extend(_decision_contract_rows())
    rows.extend(_scm_evidence_rows())
    rows.extend(_stage_rows())
    rows.extend(_non_goal_rows())
    return tuple(rows)


def filter_scm_production_candidate_release_gate_review_plan(
    rows: tuple[SCMReleaseGateReviewPlanRow, ...],
    *,
    plan_section: PlanSection | None = None,
    implementation_stage: str | None = None,
) -> tuple[SCMReleaseGateReviewPlanRow, ...]:
    """Filter SCM release-gate review plan rows by optional criteria."""
    result: list[SCMReleaseGateReviewPlanRow] = []
    for row in rows:
        if plan_section is not None and row.plan_section != plan_section:
            continue
        if implementation_stage is not None and row.implementation_stage != implementation_stage:
            continue
        result.append(row)
    return tuple(result)


def validate_scm_production_candidate_release_gate_review_plan(
    rows: tuple[SCMReleaseGateReviewPlanRow, ...],
) -> dict[str, Any]:
    """Validate SCM release-gate review plan registry thresholds and coverage."""
    issues: list[str] = []
    plan_ids = [r.plan_id for r in rows]

    if len(rows) < MIN_PLAN_ROW_COUNT:
        issues.append(f"plan_row_count {len(rows)} < {MIN_PLAN_ROW_COUNT}")
    if len(plan_ids) != len(set(plan_ids)):
        issues.append("duplicate plan_id values")

    section_counts = Counter(r.plan_section.value for r in rows)
    domain_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.RELEASE_GATE_DOMAIN}
    prereq_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.EVIDENCE_PREREQUISITE}
    input_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.INPUT_CONTRACT}
    decision_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.DECISION_CONTRACT}
    stage_counts = Counter(r.implementation_stage for r in rows if r.implementation_stage)

    for section in REQUIRED_PLAN_SECTIONS:
        if section_counts.get(section.value, 0) == 0:
            issues.append(f"missing plan_section: {section.value}")

    for domain in RELEASE_GATE_DOMAINS:
        if domain not in domain_components:
            issues.append(f"missing release_gate_domain: {domain}")

    for prereq in EVIDENCE_PREREQUISITES:
        if prereq not in prereq_components:
            issues.append(f"missing evidence_prerequisite: {prereq}")

    for field in INPUT_FIELDS:
        if field not in input_components:
            issues.append(f"missing input field: {field}")

    for field in DECISION_FIELDS:
        if field not in decision_components:
            issues.append(f"missing decision field: {field}")

    for stage in STAGES:
        if stage_counts.get(stage, 0) == 0:
            issues.append(f"missing stage: {stage}")

    return {
        "valid": not issues,
        "plan_row_count": len(rows),
        "unique_plan_ids": len(plan_ids) == len(set(plan_ids)),
        "plan_section_counts": dict(section_counts),
        "release_gate_domain_count": len(domain_components),
        "evidence_prerequisite_count": len(prereq_components),
        "input_field_count": len(input_components),
        "decision_field_count": len(decision_components),
        "stage_counts": dict(stage_counts),
        "all_release_gate_domains_covered": all(d in domain_components for d in RELEASE_GATE_DOMAINS),
        "all_evidence_prerequisites_covered": all(p in prereq_components for p in EVIDENCE_PREREQUISITES),
        "all_input_fields_covered": all(f in input_components for f in INPUT_FIELDS),
        "all_decision_fields_covered": all(f in decision_components for f in DECISION_FIELDS),
        "all_stages_present": all(stage_counts.get(s, 0) > 0 for s in STAGES),
        "issues": issues,
    }


def summarize_scm_production_candidate_release_gate_review_plan(
    rows: tuple[SCMReleaseGateReviewPlanRow, ...],
) -> dict[str, Any]:
    """Serialize SCM release-gate review plan summary for archives."""
    validation = validate_scm_production_candidate_release_gate_review_plan(rows)
    domain_states = {
        r.field_or_component: DOMAIN_PROFILES[r.field_or_component]["current"]
        for r in rows
        if r.plan_section == PlanSection.RELEASE_GATE_DOMAIN
    }
    prereq_statuses = {
        r.field_or_component: PREREQUISITE_PROFILES[r.field_or_component]["scm_status"]
        for r in rows
        if r.plan_section == PlanSection.EVIDENCE_PREREQUISITE
    }
    blocked_domains = [
        d for d, state in domain_states.items() if state in ("blocked", "not_authorized")
    ]
    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "plan_row_count": len(rows),
        "validation": validation,
        "planned_input_contract": INPUT_CONTRACT,
        "planned_decision_contract": DECISION_CONTRACT,
        "review_domains": list(RELEASE_GATE_DOMAINS),
        "evidence_prerequisites": list(EVIDENCE_PREREQUISITES),
        "planned_stages": list(STAGES),
        "review_status_vocabulary": list(REVIEW_STATUSES),
        "scm_evidence_stack": list(SCM_EVIDENCE_STACK),
        "release_gate_domain_current_states": domain_states,
        "evidence_prerequisite_scm_statuses": prereq_statuses,
        "blocked_authorization_domains": blocked_domains,
        "required_followups": list(REQUIRED_FOLLOWUPS),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
    }
    payload.update(_BOUNDARY_FLAGS)
    payload.update(_SCM_FLAGS)
    payload.update(_AUTH_FLAGS)
    payload["authorization_flags"] = dict(_AUTH_FLAGS)
    return payload


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _scenario(scenario_id: str, passed: bool, detail: str = "") -> dict[str, Any]:
    return {"scenario_id": scenario_id, "passed": passed, "detail": detail}


def build_scenarios() -> list[dict[str, Any]]:
    rows = build_scm_production_candidate_release_gate_review_plan()
    validation = validate_scm_production_candidate_release_gate_review_plan(rows)
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("plan_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("plan_row_count_at_least_70", len(rows) >= MIN_PLAN_ROW_COUNT))
    scenarios.append(_scenario("plan_ids_unique", validation["unique_plan_ids"]))

    for domain in RELEASE_GATE_DOMAINS:
        present = any(
            r.plan_section == PlanSection.RELEASE_GATE_DOMAIN and r.field_or_component == domain
            for r in rows
        )
        scenarios.append(_scenario(f"release_gate_domain_{domain}_defined", present))

    for prereq in EVIDENCE_PREREQUISITES:
        present = any(
            r.plan_section == PlanSection.EVIDENCE_PREREQUISITE and r.field_or_component == prereq
            for r in rows
        )
        scenarios.append(_scenario(f"evidence_prerequisite_{prereq}_defined", present))

    for field in INPUT_FIELDS:
        present = any(
            r.plan_section == PlanSection.INPUT_CONTRACT and r.field_or_component == field for r in rows
        )
        scenarios.append(_scenario(f"input_field_{field}_defined", present))

    for field in DECISION_FIELDS:
        present = any(
            r.plan_section == PlanSection.DECISION_CONTRACT and r.field_or_component == field
            for r in rows
        )
        scenarios.append(_scenario(f"decision_field_{field}_defined", present))

    for stage in STAGES:
        count = sum(1 for r in rows if r.implementation_stage == stage)
        scenarios.append(_scenario(f"stage_{stage}_defined", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _SCM_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "release_gate_approval_not_granted",
        summary["scm_release_gate_approval_granted"] is False,
    ))
    scenarios.append(_scenario(
        "scm_production_inference_unauthorized",
        summary["scm_production_inference_authorized"] is False,
    ))
    scenarios.append(_scenario(
        "p_value_authorization_false",
        not summary["scm_production_p_value_authorized"],
    ))
    scenarios.append(_scenario(
        "causal_ci_authorization_false",
        not summary["scm_causal_confidence_interval_authorized"],
    ))
    scenarios.append(_scenario(
        "selector_router_unauthorized",
        not summary["selector_implementation_authorized"]
        and not summary["production_selection_router_authorized"],
    ))
    scenarios.append(_scenario(
        "multicell_claim_unauthorized",
        not summary["multicell_production_claim_authorized"],
    ))
    scenarios.append(_scenario(
        "downstream_unauthorized",
        not summary["trustreport_authorized"]
        and not summary["package_side_agents_authorized"],
    ))
    scenarios.append(_scenario(
        "recommended_next_artifact_release_gate_review_packet",
        summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))
    scenarios.append(_scenario(
        "review_plan_only_no_release_gate_runtime",
        summary["review_plan_only_no_release_gate_runtime"] is True,
    ))
    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_scm_production_candidate_release_gate_review_plan()
    validation = validate_scm_production_candidate_release_gate_review_plan(rows)
    summary = summarize_scm_production_candidate_release_gate_review_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_release_gate_review_plan_metadata_only",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "plan_row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "planned_input_contract": INPUT_CONTRACT,
        "planned_decision_contract": DECISION_CONTRACT,
        "review_domains": list(RELEASE_GATE_DOMAINS),
        "evidence_prerequisites": list(EVIDENCE_PREREQUISITES),
        "planned_stages": list(STAGES),
        "blocked_authorization_domains": summary["blocked_authorization_domains"],
        "required_followups": list(REQUIRED_FOLLOWUPS),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_release_gate_review_plan_completed": False,
        "scm_release_gate_approval_granted": False,
        "scm_production_inference_authorized": False,
        "authorization_flags": dict(_AUTH_FLAGS),
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
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
