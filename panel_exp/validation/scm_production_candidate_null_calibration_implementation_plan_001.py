"""SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_production_candidate_null_calibration_implementation_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_PRODUCTION_CANDIDATE_NULL_CALIBRATION_IMPLEMENTATION_001",
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
    "scm_null_calibration_implementation_authorized": False,
    "scm_null_calibration_completed": False,
    "scm_production_inference_authorized": False,
}

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "scm_remains_gated_production_candidate": True,
    "null_calibration_not_implemented": True,
    "null_calibration_not_auto_p_value_authorization": True,
    "null_calibration_not_auto_causal_ci_authorization": True,
    "placebo_conditioned_on_scm_validation": True,
    "multiple_testing_boundary_separate": True,
    "multicell_boundary_separate": True,
    "selector_shadow_only_until_authorized": True,
    "release_gate_mandatory_before_scm_authorization": True,
    "package_side_agents_deferred": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "implementation_plan_only_no_calibration_runtime": True,
    "downstream_work_paused": True,
}

INPUT_CONTRACT = "SCMNullCalibrationInput"
EVIDENCE_CONTRACT = "SCMNullCalibrationEvidence"

INPUT_FIELDS = (
    "scm_validation_evidence",
    "panel_metadata",
    "treated_units",
    "donor_units",
    "time_index",
    "pre_period",
    "post_period",
    "placebo_units",
    "placebo_windows",
    "outcome_metadata",
    "kpi_metadata",
    "estimand_metadata",
    "effect_scale",
    "assignment_metadata",
    "design_diagnostics",
    "donor_support_evidence",
    "pre_period_fit_evidence",
    "simulation_dgp_evidence_state",
    "failure_registry_state",
    "multicell_validation_state",
    "release_gate_state",
    "audit_context",
)

EVIDENCE_FIELDS = (
    "input_contract_status",
    "placebo_generation_status",
    "placebo_distribution_status",
    "null_statistic_status",
    "treated_statistic_status",
    "effect_scale_status",
    "estimand_alignment_status",
    "type_i_error_status",
    "false_positive_rate_status",
    "p_value_calibration_status",
    "null_coverage_status",
    "multiple_testing_status",
    "multicell_status",
    "dgp_coverage_status",
    "failure_registry_status",
    "release_gate_status",
    "allowed_current_use",
    "forbidden_current_use",
    "blocked_reasons",
    "warnings",
    "required_followups",
    "audit_references",
    "authorization_flags",
)

CALIBRATION_AREAS = (
    "null_calibration_input_contract",
    "placebo_unit_generation_contract",
    "placebo_time_window_contract",
    "placebo_statistic_contract",
    "treated_statistic_contract",
    "effect_scale_alignment",
    "estimand_alignment",
    "outcome_kpi_compatibility",
    "pre_period_fit_conditioning",
    "donor_support_conditioning",
    "placebo_distribution_size",
    "placebo_distribution_quality",
    "placebo_rank_stability",
    "tail_resolution",
    "type_i_error_control",
    "false_positive_rate_assessment",
    "p_value_calibration_diagnostic",
    "null_coverage_diagnostic",
    "multiple_testing_boundary",
    "multicell_shared_control_boundary",
    "geographic_interference_boundary",
    "spillover_sensitivity_boundary",
    "simulation_dgp_coverage",
    "failure_registry_mapping",
    "blocked_reason_mapping",
    "required_followup_mapping",
    "release_gate_dependency",
    "audit_reference_contract",
    "selector_shadow_input_contract",
    "production_authorization_boundary",
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
    "stage_1_placebo_generation_contracts",
    "stage_2_null_statistic_contracts",
    "stage_3_distribution_quality_diagnostics",
    "stage_4_type_i_error_and_false_positive_diagnostics",
    "stage_5_p_value_calibration_diagnostics",
    "stage_6_dgp_and_failure_registry_integration",
    "stage_7_scm_validation_evidence_integration",
    "stage_8_selector_shadow_integration",
    "stage_9_release_gate_candidate_review",
)

STAGE_ASPECTS = ("purpose", "inputs", "outputs", "acceptance_criteria", "non_goals", "authorization_boundary")

DEPENDENCIES_RECONCILED = (
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
    "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "SIMULATION_DGP_COVERAGE_PLAN_001",
    "METHOD_FAILURE_MODE_REGISTRY_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
)

NON_GOALS = (
    "no_null_calibration_runtime",
    "no_placebo_inference_computation",
    "no_production_p_values_or_causal_cis",
    "no_scm_production_inference_authorization",
    "no_selector_router_production_use",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_package_side_agent_authorization",
    "no_multicell_scm_production_claims",
    "no_skipping_release_gate",
    "no_automatic_p_value_authorization_from_null_calibration",
    "no_automatic_causal_ci_from_jackknife",
)

AREA_PROFILES: dict[str, dict[str, Any]] = {
    "null_calibration_input_contract": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "input_contract_metadata_only",
    },
    "placebo_unit_generation_contract": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_INTEGRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "placebo_generation_not_auto_p_value",
    },
    "placebo_time_window_contract": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "placebo_window_explicit",
    },
    "placebo_statistic_contract": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "placebo_statistic_adapter_required",
    },
    "treated_statistic_contract": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "treated_statistic_adapter_required",
    },
    "effect_scale_alignment": {
        "artifacts": ("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "effect_scale_explicit",
    },
    "estimand_alignment": {
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "estimand_compatibility_required",
    },
    "outcome_kpi_compatibility": {
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "outcome_kpi_gate",
    },
    "pre_period_fit_conditioning": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "pre_period_fit_required_before_null",
    },
    "donor_support_conditioning": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "donor_support_required_before_null",
    },
    "placebo_distribution_size": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "distribution_size_diagnostic",
    },
    "placebo_distribution_quality": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "distribution_quality_diagnostic",
    },
    "placebo_rank_stability": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "research_only",
        "boundary": "rank_stability_research",
    },
    "tail_resolution": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "tail_resolution_diagnostic",
    },
    "type_i_error_control": {
        "artifacts": ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "type_i_not_auto_authorization",
    },
    "false_positive_rate_assessment": {
        "artifacts": ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "fpr_not_auto_authorization",
    },
    "p_value_calibration_diagnostic": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "p_value_diagnostic_not_authorization",
    },
    "null_coverage_diagnostic": {
        "artifacts": ("SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",),
        "planned_status": "diagnostic_only",
        "boundary": "coverage_not_causal_ci_authorization",
    },
    "multiple_testing_boundary": {
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "planned_status": "blocked",
        "boundary": "multiple_testing_separate_blocker",
    },
    "multicell_shared_control_boundary": {
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "planned_status": "blocked",
        "boundary": "multicell_scm_blocked",
    },
    "geographic_interference_boundary": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "interference_flagged",
    },
    "spillover_sensitivity_boundary": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
        "planned_status": "eligible_after_warning",
        "boundary": "spillover_handled",
    },
    "simulation_dgp_coverage": {
        "artifacts": ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "dgp_evidence_required",
    },
    "failure_registry_mapping": {
        "artifacts": ("METHOD_FAILURE_MODE_REGISTRY_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "failure_modes_block_unresolved",
    },
    "blocked_reason_mapping": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "blocked_reason_codes_mapped",
    },
    "required_followup_mapping": {
        "artifacts": ("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
        "planned_status": "candidate_after_validation",
        "boundary": "followup_codes_mapped",
    },
    "release_gate_dependency": {
        "artifacts": ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",),
        "planned_status": "release_gate_required",
        "boundary": "release_gate_before_p_value_authorization",
    },
    "audit_reference_contract": {
        "artifacts": (_ARTIFACT_ID,),
        "planned_status": "candidate_after_validation",
        "boundary": "audit_references_traceable",
    },
    "selector_shadow_input_contract": {
        "artifacts": ("DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",),
        "planned_status": "diagnostic_only",
        "boundary": "selector_shadow_only",
    },
    "production_authorization_boundary": {
        "artifacts": ("PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",),
        "planned_status": "blocked",
        "boundary": "no_production_authorization_from_null_calibration",
    },
}


class PlanSection(str, Enum):
    CALIBRATION_AREA = "calibration_area"
    INPUT_CONTRACT = "input_contract"
    EVIDENCE_CONTRACT = "evidence_contract"
    STAGE_DEFINITION = "stage_definition"
    NON_GOAL = "non_goal"


REQUIRED_PLAN_SECTIONS = frozenset(PlanSection)


@dataclass(frozen=True)
class SCMNullCalibrationPlanRow:
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
) -> SCMNullCalibrationPlanRow:
    return SCMNullCalibrationPlanRow(
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


def _calibration_area_rows() -> list[SCMNullCalibrationPlanRow]:
    rows: list[SCMNullCalibrationPlanRow] = []
    for idx, area in enumerate(CALIBRATION_AREAS, start=1):
        profile = AREA_PROFILES[area]
        rows.append(
            _row(
                f"CAL-{idx:03d}",
                PlanSection.CALIBRATION_AREA,
                area,
                f"Future SCM null calibration implementation for {area}.",
                f"SCMNullCalibrationInput fields relevant to {area}.",
                f"SCMNullCalibrationEvidence status for {area}.",
                f"{area} harness rows and tests defined; no production authorization.",
                "no_null_calibration_runtime",
                profile["boundary"],
                required_prior_artifacts=profile["artifacts"],
                planned_status=profile["planned_status"],
                notes=f"planned_status={profile['planned_status']}",
            )
        )
    return rows


def _input_contract_rows() -> list[SCMNullCalibrationPlanRow]:
    rows: list[SCMNullCalibrationPlanRow] = []
    for idx, field in enumerate(INPUT_FIELDS, start=1):
        rows.append(
            _row(
                f"INP-{idx:03d}",
                PlanSection.INPUT_CONTRACT,
                field,
                f"Planned {INPUT_CONTRACT}.{field} for SCM null calibration.",
                f"Typed {field} from SCM validation, panel, or governance state.",
                f"Validated {field} consumed by null calibration harness.",
                f"{field} schema documented.",
                "no_calibration_runtime",
                "input_contract_metadata_only",
                required_prior_artifacts=("SCM_PRODUCTION_CANDIDATE_VALIDATION_IMPLEMENTATION_001",),
            )
        )
    return rows


def _evidence_contract_rows() -> list[SCMNullCalibrationPlanRow]:
    rows: list[SCMNullCalibrationPlanRow] = []
    for idx, field in enumerate(EVIDENCE_FIELDS, start=1):
        rows.append(
            _row(
                f"EVD-{idx:03d}",
                PlanSection.EVIDENCE_CONTRACT,
                field,
                f"Planned {EVIDENCE_CONTRACT}.{field} output from null calibration.",
                "SCM null calibration area evaluation state.",
                f"Serialized {field} on {EVIDENCE_CONTRACT}.",
                f"{field} documented; authorization_flags remain false.",
                "no_production_authorization",
                "evidence_contract_metadata_only",
                required_prior_artifacts=(_ARTIFACT_ID,),
            )
        )
    return rows


def _stage_rows() -> list[SCMNullCalibrationPlanRow]:
    stage_purposes = {
        "stage_0_contract_and_registry": "Define SCMNullCalibrationInput/Evidence schemas and area registry.",
        "stage_1_placebo_generation_contracts": "Placebo unit and time-window generation contracts.",
        "stage_2_null_statistic_contracts": "Placebo and treated statistic adapter contracts.",
        "stage_3_distribution_quality_diagnostics": "Placebo distribution size, quality, rank stability.",
        "stage_4_type_i_error_and_false_positive_diagnostics": "Type I error and FPR assessment (diagnostic).",
        "stage_5_p_value_calibration_diagnostics": "P-value and null coverage diagnostics (not authorization).",
        "stage_6_dgp_and_failure_registry_integration": "DGP simulation and failure registry integration.",
        "stage_7_scm_validation_evidence_integration": "Consume SCMValidationEvidence as precondition.",
        "stage_8_selector_shadow_integration": "Supply null calibration evidence to selector shadow mode.",
        "stage_9_release_gate_candidate_review": "Release-gate candidate review only; not authorization.",
    }
    rows: list[SCMNullCalibrationPlanRow] = []
    row_num = 1
    for stage in STAGES:
        for aspect in STAGE_ASPECTS:
            rows.append(
                _row(
                    f"STG-{row_num:03d}",
                    PlanSection.STAGE_DEFINITION,
                    f"{stage}.{aspect}",
                    stage_purposes[stage] if aspect == "purpose" else f"{stage} {aspect}.",
                    "Prior stage outputs and SCMNullCalibrationInput subsets.",
                    f"Stage artifact for {stage}.",
                    f"{aspect} documented; scm_production_p_value_authorized remains false.",
                    "no_scm_production_authorization",
                    f"{stage}_plan_only",
                    required_prior_artifacts=(_ARTIFACT_ID,),
                    implementation_stage=stage,
                )
            )
            row_num += 1
    return rows


def _non_goal_rows() -> list[SCMNullCalibrationPlanRow]:
    rows: list[SCMNullCalibrationPlanRow] = []
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


def build_scm_production_candidate_null_calibration_implementation_plan() -> tuple[SCMNullCalibrationPlanRow, ...]:
    """Return metadata-only SCM null calibration implementation plan rows."""
    rows: list[SCMNullCalibrationPlanRow] = []
    rows.extend(_calibration_area_rows())
    rows.extend(_input_contract_rows())
    rows.extend(_evidence_contract_rows())
    rows.extend(_stage_rows())
    rows.extend(_non_goal_rows())
    return tuple(rows)


def filter_scm_production_candidate_null_calibration_implementation_plan(
    rows: tuple[SCMNullCalibrationPlanRow, ...],
    *,
    plan_section: PlanSection | None = None,
    implementation_stage: str | None = None,
) -> tuple[SCMNullCalibrationPlanRow, ...]:
    """Filter SCM null calibration plan rows by optional criteria."""
    result: list[SCMNullCalibrationPlanRow] = []
    for row in rows:
        if plan_section is not None and row.plan_section != plan_section:
            continue
        if implementation_stage is not None and row.implementation_stage != implementation_stage:
            continue
        result.append(row)
    return tuple(result)


def validate_scm_production_candidate_null_calibration_implementation_plan(
    rows: tuple[SCMNullCalibrationPlanRow, ...],
) -> dict[str, Any]:
    """Validate SCM null calibration plan registry thresholds and coverage."""
    issues: list[str] = []
    plan_ids = [r.plan_id for r in rows]

    if len(rows) < MIN_PLAN_ROW_COUNT:
        issues.append(f"plan_row_count {len(rows)} < {MIN_PLAN_ROW_COUNT}")
    if len(plan_ids) != len(set(plan_ids)):
        issues.append("duplicate plan_id values")

    section_counts = Counter(r.plan_section.value for r in rows)
    area_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.CALIBRATION_AREA}
    input_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.INPUT_CONTRACT}
    evidence_components = {r.field_or_component for r in rows if r.plan_section == PlanSection.EVIDENCE_CONTRACT}
    stage_counts = Counter(r.implementation_stage for r in rows if r.implementation_stage)

    for section in REQUIRED_PLAN_SECTIONS:
        if section_counts.get(section.value, 0) == 0:
            issues.append(f"missing plan_section: {section.value}")

    for area in CALIBRATION_AREAS:
        if area not in area_components:
            issues.append(f"missing calibration_area: {area}")

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
        "calibration_area_count": len(area_components),
        "input_field_count": len(input_components),
        "evidence_field_count": len(evidence_components),
        "stage_counts": dict(stage_counts),
        "all_calibration_areas_covered": all(a in area_components for a in CALIBRATION_AREAS),
        "all_input_fields_covered": all(f in input_components for f in INPUT_FIELDS),
        "all_evidence_fields_covered": all(f in evidence_components for f in EVIDENCE_FIELDS),
        "all_stages_present": all(stage_counts.get(s, 0) > 0 for s in STAGES),
        "issues": issues,
    }


def summarize_scm_production_candidate_null_calibration_implementation_plan(
    rows: tuple[SCMNullCalibrationPlanRow, ...],
) -> dict[str, Any]:
    """Serialize SCM null calibration plan summary for archives."""
    validation = validate_scm_production_candidate_null_calibration_implementation_plan(rows)
    area_statuses = {
        r.field_or_component: r.planned_status
        for r in rows
        if r.plan_section == PlanSection.CALIBRATION_AREA
    }
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_null_calibration_implementation_plan_metadata_only",
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "method_family": METHOD_FAMILY,
        "method_family_status": METHOD_FAMILY_STATUS,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "plan_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "planned_calibration_areas": list(CALIBRATION_AREAS),
        "calibration_area_planned_statuses": area_statuses,
        "planned_input_contract": INPUT_CONTRACT,
        "planned_evidence_contract": EVIDENCE_CONTRACT,
        "planned_stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "plan_section_counts": validation["plan_section_counts"],
        "all_calibration_areas_covered": validation["all_calibration_areas_covered"],
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
    rows = build_scm_production_candidate_null_calibration_implementation_plan()
    validation = validate_scm_production_candidate_null_calibration_implementation_plan(rows)
    summary = summarize_scm_production_candidate_null_calibration_implementation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("plan_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("plan_row_count_at_least_70", len(rows) >= MIN_PLAN_ROW_COUNT))
    scenarios.append(_scenario("plan_ids_unique", validation["unique_plan_ids"]))

    for section in REQUIRED_PLAN_SECTIONS:
        count = sum(1 for r in rows if r.plan_section == section)
        scenarios.append(_scenario(f"plan_section_{section.value}_represented", count > 0))

    for area in CALIBRATION_AREAS:
        present = any(
            r.plan_section == PlanSection.CALIBRATION_AREA and r.field_or_component == area for r in rows
        )
        scenarios.append(_scenario(f"calibration_area_{area}_defined", present))

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
        "recommended_next_artifact_null_calibration_implementation",
        summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))
    scenarios.append(_scenario(
        "scm_remains_gated_production_candidate",
        summary["scm_remains_gated_production_candidate"] is True,
    ))
    scenarios.append(_scenario(
        "null_calibration_not_implemented",
        summary["null_calibration_not_implemented"] is True,
    ))
    scenarios.append(_scenario(
        "p_value_authorization_remains_false",
        not summary["scm_production_p_value_authorized"],
    ))
    scenarios.append(_scenario(
        "causal_ci_authorization_remains_false",
        not summary["scm_causal_confidence_interval_authorized"],
    ))
    scenarios.append(_scenario(
        "release_gate_mandatory",
        summary["release_gate_mandatory_before_scm_authorization"] is True,
    ))
    scenarios.append(_scenario(
        "multicell_boundary_separate",
        summary["multicell_boundary_separate"] is True,
    ))
    scenarios.append(_scenario(
        "implementation_plan_only_no_calibration_runtime",
        summary["implementation_plan_only_no_calibration_runtime"],
    ))
    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_scm_production_candidate_null_calibration_implementation_plan()
    validation = validate_scm_production_candidate_null_calibration_implementation_plan(rows)
    summary = summarize_scm_production_candidate_null_calibration_implementation_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "scm_null_calibration_implementation_plan_metadata_only",
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
        "planned_calibration_areas": list(CALIBRATION_AREAS),
        "calibration_area_planned_statuses": summary["calibration_area_planned_statuses"],
        "planned_input_contract": INPUT_CONTRACT,
        "planned_evidence_contract": EVIDENCE_CONTRACT,
        "planned_stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "non_goals": list(NON_GOALS),
        "scm_null_calibration_implementation_authorized": False,
        "scm_null_calibration_completed": False,
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
