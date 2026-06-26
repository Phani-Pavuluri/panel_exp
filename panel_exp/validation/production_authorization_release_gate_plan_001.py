"""PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "production_authorization_release_gate_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001",
)

MIN_PLAN_ROW_COUNT = 70

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
    "data_driven_selection_gate_implementation_authorized": False,
    "selector_implementation_authorized": False,
    "production_selection_router_authorized": False,
    "scm_production_inference_authorized": False,
    "augsynth_production_inference_authorized": False,
    "did_production_inference_authorized": False,
    "synthetic_did_production_inference_authorized": False,
    "multicell_production_claim_authorized": False,
    "package_side_agents_authorized": False,
}

_GATE_FLAGS = {
    "production_authorization_release_gate_implemented": False,
    "production_authorization_granted": False,
}

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "open_investigations_consulted": True,
    "production_readiness_backlog_consulted": True,
    "selection_gate_implementation_plan_consulted": True,
    "retire_replace_execution_consulted": True,
    "package_side_agents_deferred": True,
    "release_gate_mandatory_before_authorization": True,
    "authorization_must_be_scoped_not_global": True,
    "method_family_separate_from_estimator_inference": True,
    "point_estimate_separate_from_causal_uncertainty": True,
    "production_p_value_separate_from_causal_ci": True,
    "multicell_requires_separate_authorization": True,
    "selector_router_requires_separate_authorization": True,
    "downstream_mip_requires_separate_authorization": True,
    "authorization_revocable": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "release_gate_plan_only_no_runtime_gate": True,
    "downstream_work_paused": True,
}

DECISION_RECORD_CONTRACT = "ProductionAuthorizationDecision"

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

DECISION_VALUES = (
    "not_authorized",
    "not_eligible",
    "eligible_for_review",
    "conditionally_authorized_after_validation",
    "authorized_for_shadow_mode_only",
    "authorized_for_limited_production",
    "authorized_for_general_production",
    "revoked",
    "blocked",
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

DECISION_RECORD_FIELDS = (
    "decision_id",
    "artifact_id",
    "decision_date",
    "decision_scope",
    "authorization_domain",
    "method_family",
    "design_id",
    "estimator_id",
    "inference_id",
    "kpi_scope",
    "population_scope",
    "cell_scope",
    "time_window_scope",
    "evidence_artifacts",
    "diagnostic_artifacts",
    "open_investigation_state",
    "production_readiness_backlog_state",
    "release_gate_status",
    "authorization_flags",
    "allowed_use",
    "forbidden_use",
    "conditions",
    "expiration_or_review_date",
    "revocation_triggers",
    "reviewers",
    "audit_references",
    "final_decision",
)

STAGES = (
    "stage_0_release_gate_contract",
    "stage_1_authorization_domain_registry",
    "stage_2_evidence_prerequisite_matrix",
    "stage_3_decision_record_schema",
    "stage_4_shadow_review_process",
    "stage_5_limited_authorization_pilot",
    "stage_6_revocation_and_monitoring_process",
    "stage_7_general_production_authorization_candidate",
)

STAGE_ASPECTS = ("purpose", "inputs", "outputs", "acceptance_criteria", "non_goals", "authorization_boundary")

DEPENDENCIES_RECONCILED = (
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",
)

NON_GOALS = (
    "no_release_gate_runtime",
    "no_production_authorization_granted",
    "no_production_inference_p_values_or_causal_cis",
    "no_selector_router_production_use",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_package_side_agent_authorization",
    "no_global_authorization",
    "no_automatic_authorization_from_resolved_plans",
    "no_skipping_evidence_prerequisites",
    "no_irrevocable_authorization",
    "no_method_family_production_promotion_by_this_plan",
)

NON_GOALS_EXTRA = NON_GOALS

DOMAIN_PROFILES: dict[str, dict[str, Any]] = {
    "method_family_authorization": {
        "artifacts": ("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001", "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"),
        "evidence": ("family_validation_plan_complete",),
        "diagnostics": ("method_governance_state",),
        "governance": ("retire_replace_respected", "open_investigations_consulted"),
        "blocked": "retire_replace_incomplete OR family_validation_missing",
        "revocation": "validation_failure OR retire_replace_violation",
        "current": "not_authorized",
    },
    "estimator_authorization": {
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "evidence": ("estimator_suitability_validation",),
        "diagnostics": ("OPD_router_inputs",),
        "governance": ("design_estimator_separated",),
        "blocked": "design_ineligible OR diagnostics_fail",
        "revocation": "diagnostic_regression OR design_invalid",
        "current": "not_authorized",
    },
    "inference_authorization": {
        "artifacts": ("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
        "evidence": ("null_calibration_where_applicable",),
        "diagnostics": ("inference_suitability",),
        "governance": ("estimator_allowed_not_inference_allowed",),
        "blocked": "adapter_missing OR null_calibration_fail",
        "revocation": "null_fpr_regression OR adapter_break",
        "current": "not_authorized",
    },
    "causal_uncertainty_authorization": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "evidence": ("causal_uncertainty_validation",),
        "diagnostics": ("interval_semantics_contract",),
        "governance": ("point_estimate_not_causal_uncertainty",),
        "blocked": "posterior_ci_requested OR adapter_unvalidated",
        "revocation": "interval_misorientation OR calibration_fail",
        "current": "not_authorized",
    },
    "production_p_value_authorization": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "evidence": ("null_fpr_gate", "placebo_calibration"),
        "diagnostics": ("p_value_contract_valid",),
        "governance": ("explicit_p_value_authorization_required",),
        "blocked": "null_calibration_incomplete OR placebo_missing",
        "revocation": "fpr_exceeds_threshold",
        "current": "not_authorized",
    },
    "multicell_claim_authorization": {
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "evidence": ("dependence_multiplicity_validation_implementation",),
        "diagnostics": ("shared_control_dependence", "multiplicity_state"),
        "governance": ("multicell_separate_authorization",),
        "blocked": "naive_per_cell_p_value OR dependence_unresolved",
        "revocation": "multiplicity_violation OR dependence_break",
        "current": "blocked",
    },
    "selector_router_authorization": {
        "artifacts": ("DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",),
        "evidence": ("selector_shadow_validation",),
        "diagnostics": ("ExperimentSelectionDecision_audit",),
        "governance": ("release_gate_before_router_production",),
        "blocked": "implementation_plan_only OR shadow_incomplete",
        "revocation": "routing_regression OR blocked_reason_missing",
        "current": "not_authorized",
    },
    "trustreport_authorization": {
        "artifacts": ("FULL_TRUSTREPORT_ELIGIBILITY_REASSESSMENT_001",),
        "evidence": ("trustreport_dcm_eligibility",),
        "diagnostics": ("trustreport_role_scope",),
        "governance": ("mip_handoff_boundary",),
        "blocked": "global_trustreport_false OR dcm_ineligible",
        "revocation": "eligibility_regression",
        "current": "not_authorized",
    },
    "calibration_signal_authorization": {
        "artifacts": ("CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",),
        "evidence": ("calibration_signal_mapping",),
        "diagnostics": ("calibration_replay",),
        "governance": ("downstream_paused",),
        "blocked": "method_gate_incomplete OR ingestion_unmapped",
        "revocation": "calibration_drift",
        "current": "not_authorized",
    },
    "mmm_ingestion_authorization": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "evidence": ("mmm_ingestion_contract",),
        "diagnostics": ("mmm_schema_compatibility",),
        "governance": ("downstream_paused",),
        "blocked": "backlog_item_open OR schema_incomplete",
        "revocation": "schema_break OR governance_revoke",
        "current": "not_authorized",
    },
    "llm_decisioning_authorization": {
        "artifacts": ("FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",),
        "evidence": ("agent_contracts_deferred",),
        "diagnostics": (),
        "governance": ("agents_deferred", "no_llm_design_authority"),
        "blocked": "agents_not_implemented OR manifest_incomplete",
        "revocation": "agent_boundary_violation",
        "current": "blocked",
    },
    "live_api_authorization": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "evidence": ("api_contract_validation",),
        "diagnostics": ("api_access_control",),
        "governance": ("mip_owns_user_facing_routing",),
        "blocked": "api_backlog_open OR access_control_missing",
        "revocation": "security_incident OR contract_break",
        "current": "not_authorized",
    },
    "scheduler_authorization": {
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "evidence": ("scheduler_safety_validation",),
        "diagnostics": ("scheduler_role_scope",),
        "governance": ("downstream_paused",),
        "blocked": "scheduler_backlog_open",
        "revocation": "runaway_job OR governance_revoke",
        "current": "not_authorized",
    },
    "budget_optimization_authorization": {
        "artifacts": ("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
        "evidence": ("budget_optimization_blocked_by_trop_boundary",),
        "diagnostics": (),
        "governance": ("trop_research_only", "no_budget_from_unvalidated_methods"),
        "blocked": "trop_research_only OR method_unvalidated",
        "revocation": "optimization_overclaim",
        "current": "blocked",
    },
    "package_side_agent_authorization": {
        "artifacts": ("FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",),
        "evidence": ("typed_manifests_and_failure_packets",),
        "diagnostics": ("agent_allowed_blocked_actions",),
        "governance": ("agents_deferred",),
        "blocked": "prerequisites_incomplete OR agent_runtime_missing",
        "revocation": "agent_overreach OR contract_violation",
        "current": "blocked",
    },
}


class PlanSection(str, Enum):
    RELEASE_GATE_DOMAIN = "release_gate_domain"
    EVIDENCE_PREREQUISITE = "evidence_prerequisite"
    DECISION_RECORD_FIELD = "decision_record_field"
    STAGE_DEFINITION = "stage_definition"
    NON_GOAL = "non_goal"


REQUIRED_PLAN_SECTIONS = frozenset(PlanSection)


@dataclass(frozen=True)
class ReleaseGatePlanRow:
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
    current_decision_value: str = "not_authorized"
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
    current_decision_value: str = "not_authorized",
    implementation_stage: str | None = None,
    notes: str = "",
) -> ReleaseGatePlanRow:
    return ReleaseGatePlanRow(
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
        current_decision_value=current_decision_value,
        implementation_stage=implementation_stage,
        notes=notes,
    )


def _domain_rows() -> list[ReleaseGatePlanRow]:
    rows: list[ReleaseGatePlanRow] = []
    for idx, domain in enumerate(RELEASE_GATE_DOMAINS, start=1):
        profile = DOMAIN_PROFILES[domain]
        current = profile["current"]
        rows.append(
            _row(
                f"DOM-{idx:03d}",
                PlanSection.RELEASE_GATE_DOMAIN,
                domain,
                f"Release-gate domain: {domain}; scoped authorization separate from other domains.",
                f"Evidence prerequisites + domain-specific validation state for {domain}.",
                f"ProductionAuthorizationDecision.final_decision for {domain}; authorization_flags update.",
                "Domain contract documented; current state not_authorized or blocked; revocation triggers defined.",
                "no_production_authorization_granted",
                f"{domain}_metadata_only",
                required_prior_artifacts=profile["artifacts"],
                current_decision_value=current,
                notes=(
                    f"evidence={profile['evidence']}; diagnostics={profile['diagnostics']}; "
                    f"governance={profile['governance']}; blocked={profile['blocked']}; "
                    f"revocation={profile['revocation']}"
                ),
            )
        )
    return rows


def _evidence_rows() -> list[ReleaseGatePlanRow]:
    rows: list[ReleaseGatePlanRow] = []
    for idx, prereq in enumerate(EVIDENCE_PREREQUISITES, start=1):
        rows.append(
            _row(
                f"EVD-{idx:03d}",
                PlanSection.EVIDENCE_PREREQUISITE,
                prereq,
                f"Evidence prerequisite {prereq} required before authorization review.",
                "Package validation artifacts, diagnostics, governance state.",
                f"Prerequisite satisfied flag on release-gate review checklist.",
                f"{prereq} documented with supplier and acceptance criteria.",
                "no_automatic_authorization",
                "evidence_prerequisite_metadata_only",
                required_prior_artifacts=("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",),
            )
        )
    return rows


def _decision_record_rows() -> list[ReleaseGatePlanRow]:
    rows: list[ReleaseGatePlanRow] = []
    for idx, field in enumerate(DECISION_RECORD_FIELDS, start=1):
        rows.append(
            _row(
                f"REC-{idx:03d}",
                PlanSection.DECISION_RECORD_FIELD,
                field,
                f"Planned {DECISION_RECORD_CONTRACT}.{field} for auditable authorization decisions.",
                "Release-gate review inputs and domain evaluation state.",
                f"Serialized {field} on {DECISION_RECORD_CONTRACT}.",
                f"{field} schema documented; scoped and revocable.",
                "no_runtime_decision_record",
                "decision_record_contract_metadata_only",
                required_prior_artifacts=(_ARTIFACT_ID,),
            )
        )
    return rows


def _stage_rows() -> list[ReleaseGatePlanRow]:
    stage_purposes = {
        "stage_0_release_gate_contract": "Define ProductionAuthorizationDecision and domain vocabulary.",
        "stage_1_authorization_domain_registry": "Metadata registry for 15 authorization domains.",
        "stage_2_evidence_prerequisite_matrix": "Matrix mapping prerequisites to domains.",
        "stage_3_decision_record_schema": "Typed decision record schema and flag bindings.",
        "stage_4_shadow_review_process": "Human governance review in shadow mode only.",
        "stage_5_limited_authorization_pilot": "Scoped limited production authorization pilot.",
        "stage_6_revocation_and_monitoring_process": "Revocation triggers and monitoring hooks.",
        "stage_7_general_production_authorization_candidate": "Candidate for general production (not granted by plan).",
    }
    rows: list[ReleaseGatePlanRow] = []
    row_num = 1
    for stage in STAGES:
        for aspect in STAGE_ASPECTS:
            rows.append(
                _row(
                    f"STG-{row_num:03d}",
                    PlanSection.STAGE_DEFINITION,
                    f"{stage}.{aspect}",
                    stage_purposes[stage] if aspect == "purpose" else f"{stage} {aspect}.",
                    "Prior stage outputs and governance consult flags.",
                    f"Stage artifact for {stage}.",
                    f"{aspect} documented; authorization flags remain false until explicit future decision.",
                    "no_runtime_release_gate",
                    f"{stage}_plan_only",
                    required_prior_artifacts=(_ARTIFACT_ID,),
                    implementation_stage=stage,
                )
            )
            row_num += 1
    return rows


def _non_goal_rows() -> list[ReleaseGatePlanRow]:
    rows: list[ReleaseGatePlanRow] = []
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
            )
        )
    return rows


def build_production_authorization_release_gate_plan() -> tuple[ReleaseGatePlanRow, ...]:
    """Return metadata-only production authorization release-gate plan rows."""
    rows: list[ReleaseGatePlanRow] = []
    rows.extend(_domain_rows())
    rows.extend(_evidence_rows())
    rows.extend(_decision_record_rows())
    rows.extend(_stage_rows())
    rows.extend(_non_goal_rows())
    return tuple(rows)


def filter_production_authorization_release_gate_plan(
    rows: tuple[ReleaseGatePlanRow, ...],
    *,
    plan_section: PlanSection | None = None,
    implementation_stage: str | None = None,
) -> tuple[ReleaseGatePlanRow, ...]:
    """Filter release-gate plan rows by optional criteria."""
    result: list[ReleaseGatePlanRow] = []
    for row in rows:
        if plan_section is not None and row.plan_section != plan_section:
            continue
        if implementation_stage is not None and row.implementation_stage != implementation_stage:
            continue
        result.append(row)
    return tuple(result)


def validate_production_authorization_release_gate_plan(
    rows: tuple[ReleaseGatePlanRow, ...],
) -> dict[str, Any]:
    """Validate release-gate plan registry thresholds and coverage."""
    issues: list[str] = []
    plan_ids = [r.plan_id for r in rows]

    if len(rows) < MIN_PLAN_ROW_COUNT:
        issues.append(f"plan_row_count {len(rows)} < {MIN_PLAN_ROW_COUNT}")
    if len(plan_ids) != len(set(plan_ids)):
        issues.append("duplicate plan_id values")

    section_counts = Counter(r.plan_section.value for r in rows)
    domain_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.RELEASE_GATE_DOMAIN}
    evidence_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.EVIDENCE_PREREQUISITE}
    record_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.DECISION_RECORD_FIELD}
    stage_counts = Counter(r.implementation_stage for r in rows if r.implementation_stage)

    for section in REQUIRED_PLAN_SECTIONS:
        if section_counts.get(section.value, 0) == 0:
            issues.append(f"missing plan_section: {section.value}")

    for domain in RELEASE_GATE_DOMAINS:
        if domain not in domain_components:
            issues.append(f"missing release_gate_domain: {domain}")

    for prereq in EVIDENCE_PREREQUISITES:
        if prereq not in evidence_components:
            issues.append(f"missing evidence_prerequisite: {prereq}")

    for field in DECISION_RECORD_FIELDS:
        if field not in record_components:
            issues.append(f"missing decision_record_field: {field}")

    for stage in STAGES:
        if stage_counts.get(stage, 0) == 0:
            issues.append(f"missing implementation stage: {stage}")

    unauthorized_domains = [
        r.field_or_component
        for r in rows
        if r.plan_section == PlanSection.RELEASE_GATE_DOMAIN
        and r.current_decision_value
        not in ("not_authorized", "blocked")
    ]
    if unauthorized_domains:
        issues.append(f"domains not in not_authorized/blocked state: {unauthorized_domains}")

    return {
        "valid": not issues,
        "plan_row_count": len(rows),
        "unique_plan_ids": len(plan_ids) == len(set(plan_ids)),
        "plan_section_counts": dict(section_counts),
        "release_gate_domain_count": len(domain_components),
        "evidence_prerequisite_count": len(evidence_components),
        "decision_record_field_count": len(record_components),
        "stage_counts": dict(stage_counts),
        "all_release_gate_domains_covered": all(d in domain_components for d in RELEASE_GATE_DOMAINS),
        "all_evidence_prerequisites_covered": all(p in evidence_components for p in EVIDENCE_PREREQUISITES),
        "all_decision_record_fields_covered": all(f in record_components for f in DECISION_RECORD_FIELDS),
        "all_stages_present": all(stage_counts.get(s, 0) > 0 for s in STAGES),
        "issues": issues,
    }


def summarize_production_authorization_release_gate_plan(
    rows: tuple[ReleaseGatePlanRow, ...],
) -> dict[str, Any]:
    """Serialize release-gate plan summary for archives."""
    validation = validate_production_authorization_release_gate_plan(rows)
    domain_states = {
        r.field_or_component: r.current_decision_value
        for r in rows
        if r.plan_section == PlanSection.RELEASE_GATE_DOMAIN
    }
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "release_gate_plan_metadata_only",
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "plan_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "release_gate_domains": list(RELEASE_GATE_DOMAINS),
        "release_gate_domain_current_states": domain_states,
        "evidence_prerequisites": list(EVIDENCE_PREREQUISITES),
        "decision_record_contract": DECISION_RECORD_CONTRACT,
        "decision_values": list(DECISION_VALUES),
        "stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "plan_section_counts": validation["plan_section_counts"],
        "all_release_gate_domains_covered": validation["all_release_gate_domains_covered"],
        "all_evidence_prerequisites_covered": validation["all_evidence_prerequisites_covered"],
        "all_decision_record_fields_covered": validation["all_decision_record_fields_covered"],
        "all_stages_present": validation["all_stages_present"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_BOUNDARY_FLAGS,
        **_GATE_FLAGS,
        **_AUTH_FLAGS,
        "authorization_flags": dict(_AUTH_FLAGS),
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
    rows = build_production_authorization_release_gate_plan()
    validation = validate_production_authorization_release_gate_plan(rows)
    summary = summarize_production_authorization_release_gate_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("plan_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("plan_row_count_at_least_70", len(rows) >= MIN_PLAN_ROW_COUNT))
    scenarios.append(_scenario("plan_ids_unique", validation["unique_plan_ids"]))

    for section in REQUIRED_PLAN_SECTIONS:
        count = sum(1 for r in rows if r.plan_section == section)
        scenarios.append(_scenario(f"plan_section_{section.value}_represented", count > 0))

    for domain in RELEASE_GATE_DOMAINS:
        present = any(
            r.plan_section == PlanSection.RELEASE_GATE_DOMAIN and r.field_or_component == domain
            for r in rows
        )
        scenarios.append(_scenario(f"release_gate_domain_{domain}_defined", present))
        state = summary["release_gate_domain_current_states"].get(domain)
        scenarios.append(_scenario(
            f"domain_{domain}_not_authorized_or_blocked",
            state in ("not_authorized", "blocked"),
        ))

    for prereq in EVIDENCE_PREREQUISITES:
        present = any(
            r.plan_section == PlanSection.EVIDENCE_PREREQUISITE and r.field_or_component == prereq
            for r in rows
        )
        scenarios.append(_scenario(f"evidence_prerequisite_{prereq}_defined", present))

    for field in DECISION_RECORD_FIELDS:
        present = any(
            r.plan_section == PlanSection.DECISION_RECORD_FIELD and r.field_or_component == field
            for r in rows
        )
        scenarios.append(_scenario(f"decision_record_field_{field}_defined", present))

    for stage in STAGES:
        count = sum(1 for r in rows if r.implementation_stage == stage)
        scenarios.append(_scenario(f"stage_{stage}_defined", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _GATE_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_scm_validation_implementation",
        summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))
    scenarios.append(_scenario(
        "decision_record_contract_production_authorization_decision",
        summary["decision_record_contract"] == DECISION_RECORD_CONTRACT,
    ))
    scenarios.append(_scenario("release_gate_plan_only_no_runtime_gate", summary["release_gate_plan_only_no_runtime_gate"]))
    scenarios.append(_scenario("production_authorization_not_granted", not summary["production_authorization_granted"]))
    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_production_authorization_release_gate_plan()
    validation = validate_production_authorization_release_gate_plan(rows)
    summary = summarize_production_authorization_release_gate_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "release_gate_plan_metadata_only",
        "artifact_version": _ARTIFACT_VERSION,
        "base_commit": _git_commit(),
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "plan_row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        "release_gate_domains": list(RELEASE_GATE_DOMAINS),
        "release_gate_domain_current_states": summary["release_gate_domain_current_states"],
        "evidence_prerequisites": list(EVIDENCE_PREREQUISITES),
        "decision_record_contract": DECISION_RECORD_CONTRACT,
        "decision_values": list(DECISION_VALUES),
        "stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "production_authorization_release_gate_implemented": False,
        "production_authorization_granted": False,
        "authorization_flags": summary["authorization_flags"],
        **{k: summary[k] for k in summary if k not in ("failed_scenarios", "valid", "authorization_flags")},
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
