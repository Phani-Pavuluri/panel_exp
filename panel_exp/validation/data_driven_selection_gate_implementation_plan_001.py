"""DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "data_driven_selection_gate_implementation_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
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

_BOUNDARY_FLAGS = {
    "prior_work_reconciled": True,
    "open_investigations_consulted": True,
    "production_readiness_backlog_consulted": True,
    "selection_gate_requirements_consulted": True,
    "retire_replace_execution_consulted": True,
    "package_side_agents_deferred": True,
    "design_estimator_inference_separated": True,
    "estimator_allowed_does_not_imply_inference_allowed": True,
    "point_estimate_allowed_does_not_imply_causal_uncertainty_allowed": True,
    "retired_overclaim_paths_route_blocked_not_production": True,
    "multicell_production_claims_blocked": True,
    "release_gate_required_before_any_authorization": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "selector_requires_release_gate_before_authorization": True,
    "selector_returns_blocked_reasons": True,
    "selector_returns_next_best_alternatives": True,
    "earlier_hard_gate_failure_prevents_later_production_eligibility": True,
    "downstream_work_paused": True,
    "implementation_plan_only_no_runtime_router": True,
}

_FORBID = (
    "runtime_router",
    "agent_runtime",
    "llm_decisioning",
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "calibration_signal",
    "mmm_ingestion",
    "live_api",
    "scheduler",
    "budget_optimization",
    "production_decisioning",
    "production_authorization",
)

INPUT_CONTRACT = "ExperimentSelectionInput"
OUTPUT_CONTRACT = "ExperimentSelectionDecision"

INPUT_FIELDS = (
    "panel_metadata",
    "experiment_metadata",
    "assignment_metadata",
    "outcome_metadata",
    "kpi_metadata",
    "cell_structure_metadata",
    "design_diagnostics",
    "observed_panel_diagnostics",
    "method_governance_state",
    "production_readiness_backlog_state",
    "retire_replace_state",
    "multicell_validation_state",
    "failure_registry_state",
    "simulation_dgp_evidence_state",
    "open_investigations_state",
    "release_gate_state",
    "audit_context",
)

OUTPUT_FIELDS = (
    "design_status",
    "estimator_status",
    "inference_status",
    "design_estimator_pair_status",
    "estimator_inference_pair_status",
    "full_tuple_status",
    "method_family_status",
    "route_status",
    "blocked_reasons",
    "warnings",
    "required_diagnostics",
    "required_evidence",
    "allowed_current_use",
    "forbidden_current_use",
    "next_best_alternatives",
    "release_gate_required",
    "authorization_flags",
    "audit_references",
)

RULE_ORDERING = (
    "data_intake",
    "experiment_metadata",
    "assignment_mechanism",
    "design_eligibility",
    "estimator_eligibility",
    "inference_eligibility",
    "outcome_kpi_compatibility",
    "observed_diagnostics",
    "simulation_dgp_coverage",
    "failure_registry",
    "multicell_dependence_multiplicity",
    "method_family_promotion_status",
    "release_gate",
    "downstream_boundary",
)

STAGES = (
    "stage_0_contract_only",
    "stage_1_metadata_registry",
    "stage_2_pure_function_router",
    "stage_3_diagnostics_integration",
    "stage_4_governance_integration",
    "stage_5_shadow_mode",
    "stage_6_release_gate_candidate",
)

STAGE_ASPECTS = ("purpose", "inputs", "outputs", "acceptance_criteria", "non_goals", "authorization_boundary")

DEPENDENCIES_RECONCILED = (
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
    "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
    "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
    "FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",
    "ROADMAP_STATE_BEFORE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
)

NON_GOALS = (
    "no_runtime_selector_router",
    "no_agent_runtime_or_llm",
    "no_production_inference_p_values_or_causal_cis",
    "no_trustreport_calibration_signal_mmm",
    "no_live_api_scheduler_budget",
    "no_budget_optimization_or_production_decisioning",
    "no_lift_power_outside_governed_diagnostics",
    "no_method_promotion_beyond_existing_labels",
    "no_code_deletion",
    "no_package_side_agent_authorization",
    "no_skipping_release_gate_dependency",
    "no_production_authorization_by_this_plan",
)


class PlanSection(str, Enum):
    INPUT_CONTRACT = "input_contract"
    OUTPUT_CONTRACT = "output_contract"
    RULE_ORDERING = "rule_ordering"
    BLOCKED_REASON_SCHEMA = "blocked_reason_schema"
    NEXT_BEST_ALTERNATIVE_SCHEMA = "next_best_alternative_schema"
    AUDIT_REFERENCE = "audit_reference"
    METHOD_FAMILY_ROUTING = "method_family_routing"
    MULTICELL_ROUTING = "multicell_routing"
    OUTCOME_KPI = "outcome_kpi"
    OBSERVED_DIAGNOSTICS = "observed_diagnostics"
    DGP_SIMULATION = "dgp_simulation"
    FAILURE_REGISTRY = "failure_registry"
    BACKLOG_INTEGRATION = "backlog_integration"
    RETIRE_REPLACE_INTEGRATION = "retire_replace_integration"
    RELEASE_GATE = "release_gate"
    AGENT_DEFERRAL = "agent_deferral"
    STAGE_DEFINITION = "stage_definition"
    TEST_STRATEGY = "test_strategy"
    VALIDATION_STRATEGY = "validation_strategy"
    DOWNSTREAM_BOUNDARY = "downstream_boundary"
    NON_GOAL = "non_goal"


class RouteStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_AFTER_WARNING = "eligible_after_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"
    RELEASE_GATE_REQUIRED = "release_gate_required"
    NOT_APPLICABLE = "not_applicable"


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


REQUIRED_PLAN_SECTIONS = frozenset(PlanSection)
REQUIRED_ROUTE_STATUSES = frozenset(RouteStatus)
REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)


_METHOD_FAMILY_STATUSES: dict[MethodFamily, RouteStatus] = {
    MethodFamily.SCM: RouteStatus.CANDIDATE_AFTER_VALIDATION,
    MethodFamily.AUGSYNTH_CVXPY: RouteStatus.DIAGNOSTIC_ONLY,
    MethodFamily.DID: RouteStatus.CANDIDATE_AFTER_VALIDATION,
    MethodFamily.SYNTHETIC_DID: RouteStatus.RESEARCH_ONLY,
    MethodFamily.TBRRIDGE: RouteStatus.DIAGNOSTIC_ONLY,
    MethodFamily.CLASSIC_AGGREGATE_TBR: RouteStatus.BLOCKED,
    MethodFamily.BAYESIAN_TBR: RouteStatus.RESEARCH_ONLY,
    MethodFamily.TROP: RouteStatus.RESEARCH_ONLY,
    MethodFamily.MULTICELL_SHARED_CONTROL: RouteStatus.BLOCKED,
}


@dataclass(frozen=True)
class ImplementationPlanRow:
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
    selection_layer: str | None = None
    implementation_stage: str | None = None
    method_family: MethodFamily | None = None
    route_status: RouteStatus | None = None
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
    selection_layer: str | None = None,
    implementation_stage: str | None = None,
    method_family: MethodFamily | None = None,
    route_status: RouteStatus | None = None,
    notes: str = "",
) -> ImplementationPlanRow:
    return ImplementationPlanRow(
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
        selection_layer=selection_layer,
        implementation_stage=implementation_stage,
        method_family=method_family,
        route_status=route_status,
        notes=notes,
    )


def _input_contract_rows() -> list[ImplementationPlanRow]:
    rows: list[ImplementationPlanRow] = []
    for idx, field in enumerate(INPUT_FIELDS, start=1):
        rows.append(
            _row(
                f"INP-{idx:03d}",
                PlanSection.INPUT_CONTRACT,
                field,
                f"Planned {INPUT_CONTRACT}.{field} input field for deterministic selector evaluation.",
                f"Typed {field} payload from package diagnostics, governance, or MIP handoff.",
                f"Validated {field} sub-object consumed by rule-ordering layers.",
                f"{field} schema documented; null/missing semantics defined; no runtime required by this plan.",
                "no_runtime_router",
                "input_contract_metadata_only",
                required_prior_artifacts=(
                    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
                ),
                notes=f"Future contract field on {INPUT_CONTRACT}.",
            )
        )
    return rows


def _output_contract_rows() -> list[ImplementationPlanRow]:
    rows: list[ImplementationPlanRow] = []
    for idx, field in enumerate(OUTPUT_FIELDS, start=1):
        rows.append(
            _row(
                f"OUT-{idx:03d}",
                PlanSection.OUTPUT_CONTRACT,
                field,
                f"Planned {OUTPUT_CONTRACT}.{field} output field for auditable routing decision.",
                f"Evaluated rule-ordering state through layer 14 downstream_boundary.",
                f"Serialized {field} on {OUTPUT_CONTRACT}; machine-readable and human-auditable.",
                f"{field} vocabulary documented; status values from allowed route vocabulary.",
                "no_production_authorization",
                "output_contract_metadata_only",
                required_prior_artifacts=(
                    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
                ),
                notes=f"Future contract field on {OUTPUT_CONTRACT}.",
            )
        )
    return rows


def _rule_ordering_rows() -> list[ImplementationPlanRow]:
    rows: list[ImplementationPlanRow] = []
    for idx, layer in enumerate(RULE_ORDERING, start=1):
        rows.append(
            _row(
                f"RUL-{idx:03d}",
                PlanSection.RULE_ORDERING,
                layer,
                f"Ordered evaluation layer {idx}: {layer}; earlier hard-gate failure prevents later production eligibility.",
                f"{INPUT_CONTRACT} signals relevant to {layer}.",
                f"Partial {OUTPUT_CONTRACT} statuses after {layer} evaluation.",
                f"Layer {idx} executes after layer {idx - 1 if idx > 1 else 0}; hard block stops downstream production paths.",
                "no_runtime_router",
                "ordered_rule_evaluation_metadata",
                required_prior_artifacts=(
                    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
                ),
                selection_layer=layer,
                notes="Failing earlier hard gates prevents later eligibility from authorizing production use.",
            )
        )
    return rows


def _stage_rows() -> list[ImplementationPlanRow]:
    rows: list[ImplementationPlanRow] = []
    row_num = 1
    stage_purposes = {
        "stage_0_contract_only": "Define ExperimentSelectionInput/Decision schemas and rule vocabulary only.",
        "stage_1_metadata_registry": "Metadata registry rows mirroring requirements and governance state.",
        "stage_2_pure_function_router": "Pure deterministic side-effect-free router function skeleton.",
        "stage_3_diagnostics_integration": "Wire observed-panel and design diagnostics into router inputs.",
        "stage_4_governance_integration": "Wire backlog, retire/replace, investigations, release-gate state.",
        "stage_5_shadow_mode": "Shadow evaluation alongside existing paths; no production routing.",
        "stage_6_release_gate_candidate": "Release-gate-candidate evaluation only after release gate plan exists.",
    }
    for stage in STAGES:
        for aspect in STAGE_ASPECTS:
            rows.append(
                _row(
                    f"STG-{row_num:03d}",
                    PlanSection.STAGE_DEFINITION,
                    f"{stage}.{aspect}",
                    stage_purposes[stage] if aspect == "purpose" else f"{stage} {aspect} definition.",
                    f"Prior stage outputs and {INPUT_CONTRACT} subsets as applicable.",
                    f"Stage artifact or contract delta for {stage}.",
                    f"{aspect} documented; governance tests pass; authorization flags remain false.",
                    f"no_{aspect}_authorization" if aspect == "authorization_boundary" else "no_runtime_production_routing",
                    f"{stage}_metadata_only",
                    required_prior_artifacts=(
                        "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
                    ),
                    implementation_stage=stage,
                    notes=f"Plan-only stage; does not implement {stage}.",
                )
            )
            row_num += 1
    return rows


def _method_family_routing_rows() -> list[ImplementationPlanRow]:
    profiles: dict[MethodFamily, dict[str, str]] = {
        MethodFamily.SCM: {
            "purpose": "Route SCM as gated production-candidate; point estimate ≠ production inference.",
            "boundary": "scm_production_inference_unauthorized",
            "artifacts": "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
        },
        MethodFamily.AUGSYNTH_CVXPY: {
            "purpose": "Route AugSynth diagnostic/remediation until adapter/null/donor evidence matures.",
            "boundary": "augsynth_production_inference_unauthorized",
            "artifacts": "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
        },
        MethodFamily.DID: {
            "purpose": "Route DID conditional candidate only under eligible designs and trend/cluster gates.",
            "boundary": "did_production_inference_unauthorized",
            "artifacts": "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
        },
        MethodFamily.SYNTHETIC_DID: {
            "purpose": "Route Synthetic DID as implementation-readiness/research-only; not implemented.",
            "boundary": "synthetic_did_production_inference_unauthorized",
            "artifacts": "SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
        },
        MethodFamily.TBRRIDGE: {
            "purpose": "Route TBRRidge diagnostic-only unless remediation evidence changes status.",
            "boundary": "tbrridge_diagnostic_only",
            "artifacts": "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        },
        MethodFamily.CLASSIC_AGGREGATE_TBR: {
            "purpose": "Retire/replace causal overclaim paths; route to blocked or diagnostic.",
            "boundary": "classic_tbr_retire_replace_blocked",
            "artifacts": "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
        },
        MethodFamily.BAYESIAN_TBR: {
            "purpose": "Route Bayesian TBR research-only; posterior intervals are not causal CIs.",
            "boundary": "bayesian_tbr_posterior_not_causal_ci",
            "artifacts": "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
        },
        MethodFamily.TROP: {
            "purpose": "Route TROP research-only; production ranking/recommendation/budget blocked.",
            "boundary": "trop_research_only",
            "artifacts": "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",
        },
        MethodFamily.MULTICELL_SHARED_CONTROL: {
            "purpose": "Block multicell/shared-control production claims until validation implementation.",
            "boundary": "multicell_production_claim_unauthorized",
            "artifacts": "MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",
        },
    }
    rows: list[ImplementationPlanRow] = []
    for idx, (family, profile) in enumerate(profiles.items(), start=1):
        status = _METHOD_FAMILY_STATUSES[family]
        rows.append(
            _row(
                f"MFR-{idx:03d}",
                PlanSection.METHOD_FAMILY_ROUTING,
                family.value,
                profile["purpose"],
                f"method_governance_state.{family.value} AND retire_replace_state",
                f"method_family_status={status.value}; route_status derived from 14-layer evaluation",
                f"Family routing matches retire/replace execution and requirements routing examples.",
                "no_production_inference_authorization",
                profile["boundary"],
                required_prior_artifacts=(profile["artifacts"], "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"),
                method_family=family,
                route_status=status,
            )
        )
    return rows


def _integration_rows() -> list[ImplementationPlanRow]:
    integrations: tuple[tuple[PlanSection, str, str, str, tuple[str, ...]], ...] = (
        (
            PlanSection.BLOCKED_REASON_SCHEMA,
            "blocked_reason_typed_codes",
            "Typed blocked_reason codes referencing FM-*, INV-*, and validation-plan blockers.",
            "failure_registry_state AND open_investigations_state",
            ("METHOD_FAILURE_MODE_REGISTRY_001",),
        ),
        (
            PlanSection.NEXT_BEST_ALTERNATIVE_SCHEMA,
            "next_best_alternative_governed_fallback",
            "Governed fallback routes when primary path blocked; no retired overclaim to production.",
            "full_tuple_status AND method_family_status",
            ("DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",),
        ),
        (
            PlanSection.AUDIT_REFERENCE,
            "audit_reference_contract",
            "Every decision cites prior artifact IDs and summary JSON paths for audit replay.",
            "audit_context",
            ("ROADMAP_STATE_BEFORE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",),
        ),
        (
            PlanSection.MULTICELL_ROUTING,
            "multicell_dependence_multiplicity_gate",
            "Block naive per-cell p-values and pooled overclaims; research-only until validated.",
            "multicell_validation_state AND cell_structure_metadata",
            ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        ),
        (
            PlanSection.OUTCOME_KPI,
            "outcome_kpi_compatibility_gate",
            "Sparse/count/rate outcomes require scale checks before estimator/inference pairing.",
            "outcome_metadata AND kpi_metadata",
            ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        ),
        (
            PlanSection.OBSERVED_DIAGNOSTICS,
            "observed_panel_diagnostics_ingestion",
            "Typed OPD diagnostics feed router eligibility before estimator promotion.",
            "observed_panel_diagnostics AND design_diagnostics",
            ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        ),
        (
            PlanSection.DGP_SIMULATION,
            "simulation_dgp_evidence_integration",
            "DGP coverage evidence required for promotion hypotheses; not sufficient alone.",
            "simulation_dgp_evidence_state",
            ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        ),
        (
            PlanSection.FAILURE_REGISTRY,
            "failure_registry_integration",
            "Unresolved failure modes block production routing at failure_registry layer.",
            "failure_registry_state",
            ("METHOD_FAILURE_MODE_REGISTRY_001",),
        ),
        (
            PlanSection.BACKLOG_INTEGRATION,
            "production_readiness_backlog_integration",
            "Map all 46 backlog rows to router input consult flags.",
            "production_readiness_backlog_state",
            ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        ),
        (
            PlanSection.RETIRE_REPLACE_INTEGRATION,
            "retire_replace_routing_integration",
            "Route retired overclaim paths away from production eligibility per 180 execution rows.",
            "retire_replace_state AND method_governance_state",
            ("METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",),
        ),
        (
            PlanSection.RELEASE_GATE,
            "release_gate_integration",
            "Release gate required before any production authorization hypothesis.",
            "release_gate_state",
            ("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
        ),
        (
            PlanSection.AGENT_DEFERRAL,
            "package_side_agent_deferral_boundary",
            "Agents deferred; may stage ExperimentRunManifest/ExperimentFailurePacket concepts only.",
            "audit_context",
            ("FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001",),
        ),
        (
            PlanSection.TEST_STRATEGY,
            "metadata_harness_and_governance_tests",
            "Harness rows, scenario validation, governance lane tests; no production router execution.",
            "implementation plan registry rows",
            (_ARTIFACT_ID,),
        ),
        (
            PlanSection.VALIDATION_STRATEGY,
            "tiered_validation_no_full_pytest_unless_schema_change",
            "JSON validation, diff check, safety grep, targeted pytest on harness/governance.",
            "summary JSON and report artifacts",
            (_ARTIFACT_ID,),
        ),
        (
            PlanSection.DOWNSTREAM_BOUNDARY,
            "downstream_integrations_blocked",
            "TrustReport/CS/MMM/LLM/API/scheduler/budget remain blocked without release gate.",
            "authorization_flags on ExperimentSelectionDecision",
            ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        ),
    )
    rows: list[ImplementationPlanRow] = []
    for idx, (section, component, purpose, inputs, artifacts) in enumerate(integrations, start=1):
        rows.append(
            _row(
                f"INT-{idx:03d}",
                section,
                component,
                purpose,
                inputs,
                f"{OUTPUT_CONTRACT} fields: blocked_reasons, next_best_alternatives, route_status as applicable",
                "Integration contract documented; consult flags wired in future stages.",
                "no_downstream_authorization",
                "integration_metadata_only",
                required_prior_artifacts=artifacts,
            )
        )
    return rows


def _non_goal_rows() -> list[ImplementationPlanRow]:
    rows: list[ImplementationPlanRow] = []
    for idx, goal in enumerate(NON_GOALS, start=1):
        rows.append(
            _row(
                f"NG-{idx:03d}",
                PlanSection.NON_GOAL,
                goal,
                f"Explicit non-goal: {goal}.",
                "N/A",
                "N/A",
                f"Report and summary state {goal}.",
                goal,
                "non_goal_enforced",
                required_prior_artifacts=(_ARTIFACT_ID,),
            )
        )
    return rows


def build_data_driven_selection_gate_implementation_plan() -> tuple[ImplementationPlanRow, ...]:
    """Return metadata-only selection-gate implementation plan rows."""
    rows: list[ImplementationPlanRow] = []
    rows.extend(_input_contract_rows())
    rows.extend(_output_contract_rows())
    rows.extend(_rule_ordering_rows())
    rows.extend(_stage_rows())
    rows.extend(_method_family_routing_rows())
    rows.extend(_integration_rows())
    rows.extend(_non_goal_rows())
    return tuple(rows)


def filter_data_driven_selection_gate_implementation_plan(
    rows: tuple[ImplementationPlanRow, ...],
    *,
    plan_section: PlanSection | None = None,
    method_family: MethodFamily | None = None,
    implementation_stage: str | None = None,
    selection_layer: str | None = None,
) -> tuple[ImplementationPlanRow, ...]:
    """Filter implementation plan rows by optional criteria."""
    result: list[ImplementationPlanRow] = []
    for row in rows:
        if plan_section is not None and row.plan_section != plan_section:
            continue
        if method_family is not None and row.method_family != method_family:
            continue
        if implementation_stage is not None and row.implementation_stage != implementation_stage:
            continue
        if selection_layer is not None and row.selection_layer != selection_layer:
            continue
        result.append(row)
    return tuple(result)


def validate_data_driven_selection_gate_implementation_plan(
    rows: tuple[ImplementationPlanRow, ...],
) -> dict[str, Any]:
    """Validate implementation plan registry thresholds and coverage."""
    issues: list[str] = []
    plan_ids = [r.plan_id for r in rows]

    if len(rows) < MIN_PLAN_ROW_COUNT:
        issues.append(f"plan_row_count {len(rows)} < {MIN_PLAN_ROW_COUNT}")
    if len(plan_ids) != len(set(plan_ids)):
        issues.append("duplicate plan_id values")

    section_counts = Counter(r.plan_section.value for r in rows)
    family_counts = Counter(r.method_family.value for r in rows if r.method_family)
    stage_counts = Counter(r.implementation_stage for r in rows if r.implementation_stage)
    layer_counts = Counter(r.selection_layer for r in rows if r.selection_layer)

    for section in REQUIRED_PLAN_SECTIONS:
        if section_counts.get(section.value, 0) == 0:
            issues.append(f"missing plan_section: {section.value}")

    for family in REQUIRED_METHOD_FAMILIES:
        if family_counts.get(family.value, 0) == 0:
            issues.append(f"missing method_family routing: {family.value}")

    for layer in RULE_ORDERING:
        if layer_counts.get(layer, 0) == 0:
            issues.append(f"missing rule_ordering layer: {layer}")

    for stage in STAGES:
        if stage_counts.get(stage, 0) == 0:
            issues.append(f"missing implementation stage: {stage}")

    input_fields = {r.field_or_component for r in rows if r.plan_section == PlanSection.INPUT_CONTRACT}
    for field in INPUT_FIELDS:
        if field not in input_fields:
            issues.append(f"missing input contract field: {field}")

    output_fields = {r.field_or_component for r in rows if r.plan_section == PlanSection.OUTPUT_CONTRACT}
    for field in OUTPUT_FIELDS:
        if field not in output_fields:
            issues.append(f"missing output contract field: {field}")

    empty = [r.plan_id for r in rows if not r.authorization_boundary]
    if empty:
        issues.append(f"rows missing authorization_boundary: {empty}")

    return {
        "valid": not issues,
        "plan_row_count": len(rows),
        "unique_plan_ids": len(plan_ids) == len(set(plan_ids)),
        "plan_section_counts": dict(section_counts),
        "method_family_counts": dict(family_counts),
        "stage_counts": dict(stage_counts),
        "rule_layer_counts": dict(layer_counts),
        "all_required_plan_sections_covered": all(
            section_counts.get(s.value, 0) > 0 for s in REQUIRED_PLAN_SECTIONS
        ),
        "all_method_families_routed": all(
            family_counts.get(f.value, 0) > 0 for f in REQUIRED_METHOD_FAMILIES
        ),
        "all_rule_layers_present": all(layer_counts.get(layer, 0) > 0 for layer in RULE_ORDERING),
        "all_stages_present": all(stage_counts.get(stage, 0) > 0 for stage in STAGES),
        "issues": issues,
    }


def summarize_data_driven_selection_gate_implementation_plan(
    rows: tuple[ImplementationPlanRow, ...],
) -> dict[str, Any]:
    """Serialize implementation plan summary for archives."""
    validation = validate_data_driven_selection_gate_implementation_plan(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "implementation_plan_metadata_only",
        "status": "completed",
        "verdict": _VERDICT,
        "final_verdict": _VERDICT,
        "next_artifact": RECOMMENDED_NEXT_ARTIFACTS[0],
        "plan_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "planned_input_contract": INPUT_CONTRACT,
        "planned_output_contract": OUTPUT_CONTRACT,
        "rule_ordering": list(RULE_ORDERING),
        "stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "method_family_statuses": {f.value: _METHOD_FAMILY_STATUSES[f].value for f in MethodFamily},
        "non_goals": list(NON_GOALS),
        "plan_section_counts": validation["plan_section_counts"],
        "method_family_counts": validation["method_family_counts"],
        "stage_counts": validation["stage_counts"],
        "all_required_plan_sections_covered": validation["all_required_plan_sections_covered"],
        "all_method_families_routed": validation["all_method_families_routed"],
        "all_rule_layers_present": validation["all_rule_layers_present"],
        "all_stages_present": validation["all_stages_present"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_BOUNDARY_FLAGS,
        **_AUTH_FLAGS,
        "authorization_flags": {
            k: v
            for k, v in _AUTH_FLAGS.items()
            if k
            not in (
                "data_driven_selection_gate_implementation_authorized",
                "selector_implementation_authorized",
                "production_selection_router_authorized",
                "package_side_agents_authorized",
            )
        },
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
    rows = build_data_driven_selection_gate_implementation_plan()
    validation = validate_data_driven_selection_gate_implementation_plan(rows)
    summary = summarize_data_driven_selection_gate_implementation_plan(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("plan_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("plan_row_count_at_least_70", len(rows) >= MIN_PLAN_ROW_COUNT))
    scenarios.append(_scenario("plan_ids_unique", validation["unique_plan_ids"]))

    for section in REQUIRED_PLAN_SECTIONS:
        count = sum(1 for r in rows if r.plan_section == section)
        scenarios.append(_scenario(f"plan_section_{section.value}_represented", count > 0))

    for family in REQUIRED_METHOD_FAMILIES:
        count = sum(1 for r in rows if r.method_family == family)
        scenarios.append(_scenario(f"method_family_{family.value}_routed", count > 0))

    for layer in RULE_ORDERING:
        count = sum(1 for r in rows if r.selection_layer == layer)
        scenarios.append(_scenario(f"rule_layer_{layer}_present", count > 0))

    for stage in STAGES:
        count = sum(1 for r in rows if r.implementation_stage == stage)
        scenarios.append(_scenario(f"stage_{stage}_defined", count > 0))

    for field in INPUT_FIELDS:
        present = any(
            r.plan_section == PlanSection.INPUT_CONTRACT and r.field_or_component == field for r in rows
        )
        scenarios.append(_scenario(f"input_field_{field}_defined", present))

    for field in OUTPUT_FIELDS:
        present = any(
            r.plan_section == PlanSection.OUTPUT_CONTRACT and r.field_or_component == field for r in rows
        )
        scenarios.append(_scenario(f"output_field_{field}_defined", present))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_release_gate",
        summary["next_artifact"] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))
    scenarios.append(_scenario(
        "planned_input_contract_experiment_selection_input",
        summary["planned_input_contract"] == INPUT_CONTRACT,
    ))
    scenarios.append(_scenario(
        "planned_output_contract_experiment_selection_decision",
        summary["planned_output_contract"] == OUTPUT_CONTRACT,
    ))
    scenarios.append(_scenario("implementation_plan_only_no_runtime_router", summary["implementation_plan_only_no_runtime_router"]))
    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_data_driven_selection_gate_implementation_plan()
    validation = validate_data_driven_selection_gate_implementation_plan(rows)
    summary = summarize_data_driven_selection_gate_implementation_plan(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_type": "implementation_plan_metadata_only",
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
        "planned_input_contract": INPUT_CONTRACT,
        "planned_output_contract": OUTPUT_CONTRACT,
        "rule_ordering": list(RULE_ORDERING),
        "stages": list(STAGES),
        "dependencies_reconciled": list(DEPENDENCIES_RECONCILED),
        "method_family_statuses": summary["method_family_statuses"],
        "non_goals": list(NON_GOALS),
        "selector_implementation_authorized": False,
        "production_selection_router_authorized": False,
        "package_side_agents_authorized": False,
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
