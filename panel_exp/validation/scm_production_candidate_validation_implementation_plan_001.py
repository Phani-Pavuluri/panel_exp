"""SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_validation_implementation_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
)

MIN_PLAN_ROW_COUNT = 70
METHOD_FAMILY = "SCM"
METHOD_FAMILY_STATUS = "production_candidate_gated"

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
    "scm_validation_implementation_authorized": False,
    "scm_production_inference_authorized": False,
}

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "scm_remains_gated_production_candidate": True,
    "scm_point_estimate_not_causal_uncertainty": True,
    "placebo_null_not_auto_p_value_authorization": True,
    "jackknife_not_auto_causal_ci_authorization": True,
    "donor_support_convex_hull_extrapolation_required": True,
    "assignment_design_validity_required_before_review": True,
    "multicell_scm_claims_blocked": True,
    "selector_shadow_only_until_authorized": True,
    "release_gate_mandatory_before_scm_authorization": True,
    "package_side_agents_deferred": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "implementation_plan_only_no_validation_runtime": True,
    "downstream_work_paused": True,
}

INPUT_CONTRACT = "SCMValidationInput"
EVIDENCE_CONTRACT = "SCMValidationEvidence"

INPUT_FIELDS = (
    "panel_metadata",
    "treated_units",
    "donor_units",
    "time_index",
    "pre_period",
    "post_period",
    "outcome_metadata",
    "kpi_metadata",
    "estimand_metadata",
    "assignment_metadata",
    "design_diagnostics",
    "observed_panel_diagnostics",
    "donor_pool_metadata",
    "method_governance_state",
    "failure_registry_state",
    "simulation_dgp_evidence_state",
    "multicell_validation_state",
    "release_gate_state",
    "audit_context",
)

EVIDENCE_FIELDS = (
    "input_contract_status",
    "donor_support_status",
    "geometry_status",
    "pre_period_fit_status",
    "trend_stability_status",
    "placebo_status",
    "null_calibration_status",
    "jackknife_sensitivity_status",
    "assignment_design_status",
    "outcome_kpi_status",
    "statistic_adapter_status",
    "failure_registry_status",
    "dgp_coverage_status",
    "multicell_status",
    "release_gate_status",
    "allowed_current_use",
    "forbidden_current_use",
    "blocked_reasons",
    "warnings",
    "required_followups",
    "audit_references",
    "authorization_flags",
)

VALIDATION_AREAS = (
    "scm_input_contract",
    "panel_balance_and_time_index",
    "treated_unit_definition",
    "donor_pool_definition",
    "donor_pool_size",
    "donor_support_overlap",
    "convex_hull_support",
    "extrapolation_risk",
    "pre_period_length",
    "pre_period_fit_quality",
    "pre_period_trend_stability",
    "post_period_window_definition",
    "outcome_scale_compatibility",
    "kpi_estimand_compatibility",
    "assignment_design_validity",
    "randomization_compatibility",
    "geographic_interference_risk",
    "spillover_exclusion_or_flagging",
    "placebo_unit_generation",
    "placebo_distribution_quality",
    "null_calibration",
    "jackknife_unit_sensitivity",
    "donor_weight_stability",
    "treated_set_sensitivity",
    "statistic_adapter_contract",
    "effect_scale_contract",
    "uncertainty_boundary",
    "failure_registry_mapping",
    "simulation_dgp_coverage",
    "multicell_shared_control_blocker",
    "release_gate_dependency",
)

ROUTE_STATUSES = (
    "eligible",
    "eligible_after_warning",
    "candidate_after_validation",
    "diagnostic_only",
    "research_only",
    "blocked",
    "release_gate_required",
    "not_applicable",
)

STAGES = (
    "stage_0_contract_and_registry",
    "stage_1_data_and_panel_diagnostics",
    "stage_2_donor_support_and_geometry_diagnostics",
    "stage_3_pre_period_fit_and_trend_diagnostics",
    "stage_4_placebo_and_null_calibration_diagnostics",
    "stage_5_jackknife_and_sensitivity_diagnostics",
    "stage_6_assignment_outcome_and_estimand_compatibility",
    "stage_7_failure_registry_and_dgp_integration",
    "stage_8_selector_shadow_integration",
    "stage_9_release_gate_candidate_review",
)

STAGE_ASPECTS = ("purpose", "inputs", "outputs", "acceptance_criteria", "non_goals", "authorization_boundary")

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
    "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",
    "FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",
)

NON_GOALS = (
    "no_scm_validation_runtime",
    "no_scm_production_inference_authorization",
    "no_production_p_values_or_causal_cis",
    "no_selector_router_production_use",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_package_side_agent_authorization",
    "no_multicell_scm_production_claims",
    "no_scm_production_safe_promotion",
    "no_skipping_release_gate",
    "no_automatic_authorization_from_diagnostics",
    "no_method_promotion_beyond_gated_candidate",
)

AREA_PROFILES: dict[str, dict[str, Any]] = {
    "scm_input_contract": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "input_contract_metadata_only",
    },
    "panel_balance_and_time_index": {
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "panel_balance_required",
    },
    "treated_unit_definition": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "treated_unit_explicit",
    },
    "donor_pool_definition": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "donor_pool_explicit",
    },
    "donor_pool_size": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "donor_pool_size_gate",
    },
    "donor_support_overlap": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "donor_support_required",
    },
    "convex_hull_support": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "convex_hull_required",
    },
    "extrapolation_risk": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "blocked",
        "boundary": "extrapolation_blocks_promotion",
    },
    "pre_period_length": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "pre_period_length_gate",
    },
    "pre_period_fit_quality": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "pre_period_fit_required",
    },
    "pre_period_trend_stability": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "trend_stability_required",
    },
    "post_period_window_definition": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "post_period_explicit",
    },
    "outcome_scale_compatibility": {
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "outcome_scale_gate",
    },
    "kpi_estimand_compatibility": {
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "estimand_compatibility_required",
    },
    "assignment_design_validity": {
        "artifacts": ("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "assignment_validity_before_review",
    },
    "randomization_compatibility": {
        "artifacts": ("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "randomization_for_inference_family",
    },
    "geographic_interference_risk": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "interference_flagged",
    },
    "spillover_exclusion_or_flagging": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "spillover_handled",
    },
    "placebo_unit_generation": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_INTEGRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "placebo_not_auto_p_value",
    },
    "placebo_distribution_quality": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "placebo_quality_diagnostic",
    },
    "null_calibration": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "null_calibration_not_auto_authorization",
    },
    "jackknife_unit_sensitivity": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "diagnostic_only",
        "boundary": "jackknife_not_auto_causal_ci",
    },
    "donor_weight_stability": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "weight_stability_gate",
    },
    "treated_set_sensitivity": {
        "artifacts": ("MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",),
        "planned_status": "research_only",
        "boundary": "multi_treated_research_handling",
    },
    "statistic_adapter_contract": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "adapter_required_for_inference",
    },
    "effect_scale_contract": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "effect_scale_explicit",
    },
    "uncertainty_boundary": {
        "artifacts": ("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
        "planned_status": "blocked",
        "boundary": "point_estimate_not_causal_uncertainty",
    },
    "failure_registry_mapping": {
        "artifacts": ("METHOD_FAILURE_MODE_REGISTRY_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "failure_modes_block_unresolved",
    },
    "simulation_dgp_coverage": {
        "artifacts": ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "dgp_evidence_required",
    },
    "multicell_shared_control_blocker": {
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "planned_status": "blocked",
        "boundary": "multicell_scm_blocked",
    },
    "release_gate_dependency": {
        "artifacts": ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",),
        "planned_status": "release_gate_required",
        "boundary": "release_gate_before_authorization",
    },
}


class PlanSection(str, Enum):
    VALIDATION_AREA = "validation_area"
    INPUT_CONTRACT = "input_contract"
    EVIDENCE_CONTRACT = "evidence_contract"
    STAGE_DEFINITION = "stage_definition"
    NON_GOAL = "non_goal"


REQUIRED_PLAN_SECTIONS = frozenset(PlanSection)


@dataclass(frozen=True)
class SCMImplementationPlanRow:
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
    planned_status: str = "candidate_after_validation"
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
    planned_status: str = "candidate_after_validation",
    implementation_stage: str | None = None,
    notes: str = "",
) -> SCMImplementationPlanRow:
    return SCMImplementationPlanRow(
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
        planned_status=planned_status,
        implementation_stage=implementation_stage,
        notes=notes,
    )


def _validation_area_rows() -> list[SCMImplementationPlanRow]:
    rows: list[SCMImplementationPlanRow] = []
    for idx, area in enumerate(VALIDATION_AREAS, start=1):
        profile = AREA_PROFILES[area]
        rows.append(
            _row(
                f"VAL-{idx:03d}",
                PlanSection.VALIDATION_AREA,
                area,
                f"Future SCM validation implementation for {area}.",
                f"SCMValidationInput fields relevant to {area}.",
                f"SCMValidationEvidence status for {area}.",
                f"{area} harness rows and tests defined; no production authorization.",
                "no_scm_validation_runtime",
                profile["boundary"],
                required_prior_artifacts=profile["artifacts"],
                planned_status=profile["planned_status"],
                notes=f"planned_status={profile['planned_status']}",
            )
        )
    return rows


def _input_contract_rows() -> list[SCMImplementationPlanRow]:
    rows: list[SCMImplementationPlanRow] = []
    for idx, field in enumerate(INPUT_FIELDS, start=1):
        rows.append(
            _row(
                f"INP-{idx:03d}",
                PlanSection.INPUT_CONTRACT,
                field,
                f"Planned {INPUT_CONTRACT}.{field} for SCM validation.",
                f"Typed {field} from panel, design, or governance state.",
                f"Validated {field} consumed by SCM validation harness.",
                f"{field} schema documented.",
                "no_validation_runtime",
                "input_contract_metadata_only",
                required_prior_artifacts=("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
            )
        )
    return rows


def _evidence_contract_rows() -> list[SCMImplementationPlanRow]:
    rows: list[SCMImplementationPlanRow] = []
    for idx, field in enumerate(EVIDENCE_FIELDS, start=1):
        rows.append(
            _row(
                f"EVD-{idx:03d}",
                PlanSection.EVIDENCE_CONTRACT,
                field,
                f"Planned {EVIDENCE_CONTRACT}.{field} output from SCM validation.",
                "SCM validation area evaluation state.",
                f"Serialized {field} on {EVIDENCE_CONTRACT}.",
                f"{field} documented; authorization_flags remain false.",
                "no_production_authorization",
                "evidence_contract_metadata_only",
                required_prior_artifacts=(_ARTIFACT_ID,),
            )
        )
    return rows


def _stage_rows() -> list[SCMImplementationPlanRow]:
    stage_purposes = {
        "stage_0_contract_and_registry": "Define SCMValidationInput/Evidence schemas and area registry.",
        "stage_1_data_and_panel_diagnostics": "Panel balance, time index, input contract validation.",
        "stage_2_donor_support_and_geometry_diagnostics": "Donor pool, support, convex hull, extrapolation.",
        "stage_3_pre_period_fit_and_trend_diagnostics": "Pre-period fit and trend stability harness.",
        "stage_4_placebo_and_null_calibration_diagnostics": "Placebo generation and null calibration (diagnostic).",
        "stage_5_jackknife_and_sensitivity_diagnostics": "Jackknife and sensitivity (diagnostic only).",
        "stage_6_assignment_outcome_and_estimand_compatibility": "Assignment, outcome, KPI, estimand gates.",
        "stage_7_failure_registry_and_dgp_integration": "Failure registry and DGP coverage integration.",
        "stage_8_selector_shadow_integration": "Supply SCMValidationEvidence to selector shadow mode.",
        "stage_9_release_gate_candidate_review": "Release-gate candidate review only; not authorization.",
    }
    rows: list[SCMImplementationPlanRow] = []
    row_num = 1
    for stage in STAGES:
        for aspect in STAGE_ASPECTS:
            rows.append(
                _row(
                    f"STG-{row_num:03d}",
                    PlanSection.STAGE_DEFINITION,
                    f"{stage}.{aspect}",
                    stage_purposes[stage] if aspect == "purpose" else f"{stage} {aspect}.",
                    "Prior stage outputs and SCMValidationInput subsets.",
                    f"Stage artifact for {stage}.",
                    f"{aspect} documented; scm_production_inference_authorized remains false.",
                    "no_scm_production_authorization",
                    f"{stage}_plan_only",
                    required_prior_artifacts=(_ARTIFACT_ID,),
                    implementation_stage=stage,
                )
            )
            row_num += 1
    return rows


def _non_goal_rows() -> list[SCMImplementationPlanRow]:
    rows: list[SCMImplementationPlanRow] = []
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


def build_scm_production_candidate_validation_implementation_plan() -> tuple[SCMImplementationPlanRow, ...]:
    """Return metadata-only SCM validation implementation plan rows."""
    rows: list[SCMImplementationPlanRow] = []
    rows.extend(_validation_area_rows())
    rows.extend(_input_contract_rows())
    rows.extend(_evidence_contract_rows())
    rows.extend(_stage_rows())
    rows.extend(_non_goal_rows())
    return tuple(rows)


def filter_scm_production_candidate_validation_implementation_plan(
    rows: tuple[SCMImplementationPlanRow, ...],
    *,
    plan_section: PlanSection | None = None,
    implementation_stage: str | None = None,
) -> tuple[SCMImplementationPlanRow, ...]:
    """Filter SCM implementation plan rows by optional criteria."""
    result: list[SCMImplementationPlanRow] = []
    for row in rows:
        if plan_section is not None and row.plan_section != plan_section:
            continue
        if implementation_stage is not None and row.implementation_stage != implementation_stage:
            continue
        result.append(row)
    return tuple(result)


def validate_scm_production_candidate_validation_implementation_plan(
    rows: tuple[SCMImplementationPlanRow, ...],
) -> dict[str, Any]:
    """Validate SCM implementation plan registry thresholds and coverage."""
    issues: list[str] = []
    plan_ids = [r.plan_id for r in rows]

    if len(rows) < MIN_PLAN_ROW_COUNT:
        issues.append(f"plan_row_count {len(rows)} < {MIN_PLAN_ROW_COUNT}")
    if len(plan_ids) != len(set(plan_ids)):
        issues.append("duplicate plan_id values")

    section_counts = Counter(r.plan_section.value for r in rows)
    area_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.VALIDATION_AREA}
    input_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.INPUT_CONTRACT}
    evidence_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.EVIDENCE_CONTRACT}
    stage_counts = Counter(r.implementation_stage for r in rows if r.implementation_stage)

    for section in REQUIRED_PLAN_SECTIONS:
        if section_counts.get(section.value, 0) == 0:
            issues.append(f"missing plan_section: {section.value}")

    for area in VALIDATION_AREAS:
        if area not in area_components:
            issues.append(f"missing validation_area: {area}")

    for field in INPUT_FIELDS:
        if field not in input_components:
            issues.append(f"missing input field: {field}")

    for field in EVIDENCE_FIELDS:
        if field not in evidence_components:
            issues.append(f"missing evidence field: {field}")

    for stage in STAGES:
        if stage_counts.get(stage, 0) == 0:
            issues.append(f"missing stage: {stage}")

    return {
        "valid": not issues,
        "plan_row_count": len(rows),
        "unique_plan_ids": len(plan_ids) == len(set(plan_ids)),
        "plan_section_counts": dict(section_counts),
        "validation_area_count": len(area_components),
        "input_field_count": len(input_components),
        "evidence_field_count": len(evidence_components),
        "stage_counts": dict(stage_counts),
        "all_validation_areas_covered": all(a in area_components for a in VALIDATION_AREAS),
        "all_input_fields_covered": all(f in input_components for f in INPUT_FIELDS),
        "all_evidence_fields_covered": all(f in evidence_components for f in EVIDENCE_FIELDS),
        "all_stages_present": all(stage_counts.get(s, 0) > 0 for s in STAGES),
        "issues": issues,
    }


def summarize_scm_production_candidate_validation_implementation_plan(
    rows: tuple[SCMImplementationPlanRow, ...],
) -> dict[str, Any]:
    """Serialize SCM implementation plan summary for archives."""
    validation = validate_scm_production_candidate_validation_implementation_plan(rows)
    area_statuses = {
        r.field_or_component: r.planned_status
        for r in rows
        if r.plan_section == PlanSection.VALIDATION_AREA
    }
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_validation_implementation_plan_metadata_only",
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "plan_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "validation_areas": list(VALIDATION_AREAS),
        "validation_area_planned_statuses": area_statuses,
        "planned_input_contract": INPUT_CONTRACT,
        "planned_evidence_contract": EVIDENCE_CONTRACT,
        "stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "plan_section_counts": validation["plan_section_counts"],
        "all_validation_areas_covered": validation["all_validation_areas_covered"],
        "all_input_fields_covered": validation["all_input_fields_covered"],
        "all_evidence_fields_covered": validation["all_evidence_fields_covered"],
        "all_stages_present": validation["all_stages_present"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_BOUNDARY_FLAGS,
        **_SCM_FLAGS,
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
    rows = build_scm_production_candidate_validation_implementation_plan()
    validation = validate_scm_production_candidate_validation_implementation_plan(rows)
    summary = summarize_scm_production_candidate_validation_implementation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("plan_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("plan_row_count_at_least_70", len(rows) >= MIN_PLAN_ROW_COUNT))
    scenarios.append(_scenario("plan_ids_unique", validation["unique_plan_ids"]))

    for section in REQUIRED_PLAN_SECTIONS:
        count = sum(1 for r in rows if r.plan_section == section)
        scenarios.append(_scenario(f"plan_section_{section.value}_represented", count > 0))

    for area in VALIDATION_AREAS:
        present = any(
            r.plan_section == PlanSection.VALIDATION_AREA and r.field_or_component == area for r in rows
        )
        scenarios.append(_scenario(f"validation_area_{area}_defined", present))

    for field in INPUT_FIELDS:
        present = any(
            r.plan_section == PlanSection.INPUT_CONTRACT and r.field_or_component == field for r in rows
        )
        scenarios.append(_scenario(f"input_field_{field}_defined", present))

    for field in EVIDENCE_FIELDS:
        present = any(
            r.plan_section == PlanSection.EVIDENCE_CONTRACT and r.field_or_component == field for r in rows
        )
        scenarios.append(_scenario(f"evidence_field_{field}_defined", present))

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
        "method_family_scm_production_candidate_gated",
        summary["method_family"] == METHOD_FAMILY
        and summary["method_family_status"] == METHOD_FAMILY_STATUS,
    ))
    scenarios.append(_scenario(
        "recommended_next_artifact_scm_validation_implementation",
        summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))
    scenarios.append(_scenario(
        "scm_remains_gated_production_candidate",
        summary["scm_remains_gated_production_candidate"] is True,
    ))
    scenarios.append(_scenario("implementation_plan_only_no_validation_runtime", summary["implementation_plan_only_no_validation_runtime"]))
    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_scm_production_candidate_validation_implementation_plan()
    validation = validate_scm_production_candidate_validation_implementation_plan(rows)
    summary = summarize_scm_production_candidate_validation_implementation_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_validation_implementation_plan_metadata_only",
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
        "validation_areas": list(VALIDATION_AREAS),
        "validation_area_planned_statuses": summary["validation_area_planned_statuses"],
        "planned_input_contract": INPUT_CONTRACT,
        "planned_evidence_contract": EVIDENCE_CONTRACT,
        "stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_validation_implementation_authorized": False,
        "scm_production_inference_authorized": False,
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
