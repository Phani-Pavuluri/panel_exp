"""DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001 validation harness."""

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

_ARTIFACT_ID = "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "data_driven_selection_gate_requirements_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO
    / "docs/track_d/archives/DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001",
)

MIN_REQUIREMENTS_ROW_COUNT = 70

_AUTH_FLAGS = {
    "data_driven_selection_gate_implementation_authorized": False,
    "production_selection_router_authorized": False,
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
    "method_family_promotion_matrix_consulted": True,
    "observed_diagnostics_requirements_consulted": True,
    "failure_registry_consulted": True,
    "dgp_coverage_plan_consulted": True,
    "assignment_stress_plan_consulted": True,
    "multicell_validation_plan_consulted": True,
    "design_estimator_inference_separated": True,
    "estimator_allowed_does_not_imply_inference_allowed": True,
    "point_estimate_allowed_does_not_imply_causal_uncertainty_allowed": True,
    "resolved_artifacts_do_not_mean_production_ready": True,
    "selector_requires_release_gate_before_authorization": True,
    "selector_returns_blocked_reasons": True,
    "selector_returns_next_best_alternatives": True,
}

_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "production_routing",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
    "production_decisioning",
)

_NEXT = "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001"


class SelectionLayer(str, Enum):
    DATA_INTAKE = "data_intake"
    EXPERIMENT_METADATA = "experiment_metadata"
    ASSIGNMENT_MECHANISM = "assignment_mechanism"
    DESIGN_ELIGIBILITY = "design_eligibility"
    ESTIMATOR_ELIGIBILITY = "estimator_eligibility"
    INFERENCE_ELIGIBILITY = "inference_eligibility"
    OUTCOME_KPI_COMPATIBILITY = "outcome_kpi_compatibility"
    OBSERVED_DIAGNOSTICS = "observed_diagnostics"
    SIMULATION_DGP_COVERAGE = "simulation_dgp_coverage"
    FAILURE_REGISTRY = "failure_registry"
    MULTICELL_DEPENDENCE_MULTIPLICITY = "multicell_dependence_multiplicity"
    METHOD_FAMILY_PROMOTION_STATUS = "method_family_promotion_status"
    RELEASE_GATE = "release_gate"
    DOWNSTREAM_BOUNDARY = "downstream_boundary"


class DecisionTarget(str, Enum):
    DESIGN = "design"
    ESTIMATOR = "estimator"
    INFERENCE = "inference"
    DESIGN_ESTIMATOR_PAIR = "design_estimator_pair"
    ESTIMATOR_INFERENCE_PAIR = "estimator_inference_pair"
    FULL_TUPLE = "full_design_estimator_inference_tuple"
    METHOD_FAMILY = "method_family"
    DOWNSTREAM_AUTHORIZATION = "downstream_authorization"


class RouteStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_AFTER_WARNING = "eligible_after_warning"
    CANDIDATE_AFTER_VALIDATION = "candidate_after_validation"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"
    RELEASE_GATE_REQUIRED = "release_gate_required"


REQUIRED_SELECTION_LAYERS = frozenset(SelectionLayer)
REQUIRED_DECISION_TARGETS = frozenset(DecisionTarget)
REQUIRED_ROUTE_STATUSES = frozenset(RouteStatus)

REQUIRED_ROUTING_EXAMPLE_IDS = frozenset({
    "routing_scm_point_estimate_gated",
    "routing_scm_production_inference_blocked",
    "routing_scm_treated_set_placebo_adapter",
    "routing_did_conditional_candidate",
    "routing_augsynth_remediation_candidate",
    "routing_synthetic_did_readiness_scout",
    "routing_tbrridge_diagnostic_only",
    "routing_classic_tbr_retire_replace_blocked",
    "routing_bayesian_tbr_posterior_diagnostic_only",
    "routing_trop_research_only",
    "routing_multicell_blocked_research_only",
    "routing_unknown_assignment_blocks_inference",
    "routing_degenerate_assignment_blocks_rank_inference",
    "routing_sparse_outcome_scale_check",
    "routing_multiplicity_before_inferential_claims",
    "routing_downstream_authorization_blocked",
})


@dataclass(frozen=True)
class SelectionGateRequirementRow:
    requirement_id: str
    name: str
    selection_layer: SelectionLayer
    input_signal: str
    decision_target: DecisionTarget
    route_status: RouteStatus
    eligible_when: str
    diagnostic_only_when: str
    research_only_when: str
    blocked_when: str
    required_prior_artifacts: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_validation_evidence: tuple[str, ...]
    failure_modes_checked: tuple[str, ...]
    authorization_boundary: str
    recommended_next_artifact: str | None
    notes: str


def _row(
    requirement_id: str,
    name: str,
    selection_layer: SelectionLayer,
    input_signal: str,
    decision_target: DecisionTarget,
    route_status: RouteStatus,
    eligible_when: str,
    diagnostic_only_when: str,
    research_only_when: str,
    blocked_when: str,
    *,
    required_prior_artifacts: tuple[str, ...],
    required_diagnostics: tuple[str, ...] = (),
    required_validation_evidence: tuple[str, ...] = (),
    failure_modes_checked: tuple[str, ...] = (),
    authorization_boundary: str,
    recommended_next_artifact: str | None = None,
    notes: str = "",
) -> SelectionGateRequirementRow:
    return SelectionGateRequirementRow(
        requirement_id=requirement_id,
        name=name,
        selection_layer=selection_layer,
        input_signal=input_signal,
        decision_target=decision_target,
        route_status=route_status,
        eligible_when=eligible_when,
        diagnostic_only_when=diagnostic_only_when,
        research_only_when=research_only_when,
        blocked_when=blocked_when,
        required_prior_artifacts=required_prior_artifacts,
        required_diagnostics=required_diagnostics,
        required_validation_evidence=required_validation_evidence,
        failure_modes_checked=failure_modes_checked,
        authorization_boundary=authorization_boundary,
        recommended_next_artifact=recommended_next_artifact or _NEXT,
        notes=notes,
    )


def _routing_example_rows() -> list[SelectionGateRequirementRow]:
    """Explicit routing requirement examples from prior-work reconciliation."""
    return [
        _row(
            "routing_scm_point_estimate_gated",
            "SCM point estimate gated on donor support, fit, scale, assignment",
            SelectionLayer.ESTIMATOR_ELIGIBILITY,
            "scm_estimator_request",
            DecisionTarget.ESTIMATOR,
            RouteStatus.ELIGIBLE_AFTER_WARNING,
            "donor_support_ok AND convex_hull_ok AND preperiod_fit_ok AND outcome_scale_ok AND assignment_valid",
            "any_diagnostic_warning_present",
            "multicell_or_multi_treated_research_path",
            "donor_support_fail OR convex_hull_fail OR preperiod_fit_fail OR outcome_scale_fail OR assignment_invalid",
            required_prior_artifacts=(
                "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
                "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",
            ),
            required_diagnostics=("OPD-DONOR-001", "OPD-DS-005", "OPD-PF-001", "OPD-PF-002"),
            required_validation_evidence=("scm_point_estimate_gate",),
            failure_modes_checked=("FM-ES-001", "FM-CP-003"),
            authorization_boundary="point_estimate_not_production_inference",
            notes="Point estimate allowed does not imply causal uncertainty allowed.",
        ),
        _row(
            "routing_scm_production_inference_blocked",
            "SCM production inference blocked until adapter/null calibration/release gate",
            SelectionLayer.INFERENCE_ELIGIBILITY,
            "scm_inference_request",
            DecisionTarget.INFERENCE,
            RouteStatus.BLOCKED,
            "release_gate_authorized AND adapter_ready AND null_calibration_pass",
            "placebo_rank_diagnostic_only",
            "studentized_adapter_candidate",
            "adapter_missing OR null_calibration_fail OR release_gate_open",
            required_prior_artifacts=(
                "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
                "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
            ),
            required_validation_evidence=("null_fpr_gate", "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001"),
            authorization_boundary="scm_production_inference_unauthorized",
        ),
        _row(
            "routing_scm_treated_set_placebo_adapter",
            "SCM treated-set placebo requires statistic adapter and null calibration",
            SelectionLayer.INFERENCE_ELIGIBILITY,
            "scm_treated_set_placebo_request",
            DecisionTarget.ESTIMATOR_INFERENCE_PAIR,
            RouteStatus.CANDIDATE_AFTER_VALIDATION,
            "adapter_contract_ready AND null_calibration_pass",
            "adapter_partial_maturity",
            "adapter_research_path",
            "adapter_missing OR null_calibration_fail",
            required_prior_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            required_validation_evidence=("treated_set_placebo_integration",),
            authorization_boundary="adapter_and_null_required",
        ),
        _row(
            "routing_did_conditional_candidate",
            "DID conditional candidate when design/trend/cluster/bootstrap suitable",
            SelectionLayer.ESTIMATOR_ELIGIBILITY,
            "did_estimator_request",
            DecisionTarget.DESIGN_ESTIMATOR_PAIR,
            RouteStatus.CANDIDATE_AFTER_VALIDATION,
            "assignment_valid AND parallel_trends_ok AND cluster_eligible AND bootstrap_suitable",
            "conditional_design_warning",
            "did_research_exploration",
            "assignment_invalid OR parallel_trends_fail OR cluster_ineligible OR bootstrap_unsuitable",
            required_prior_artifacts=("DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",),
            failure_modes_checked=("FM-CP-004",),
            authorization_boundary="did_conditional_designs_only",
            recommended_next_artifact="DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
        ),
        _row(
            "routing_augsynth_remediation_candidate",
            "AugSynth diagnostic/remediation candidate until adapter/null/donor/DGP mature",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "augsynth_route_request",
            DecisionTarget.METHOD_FAMILY,
            RouteStatus.DIAGNOSTIC_ONLY,
            "adapter_ready AND null_calibration_pass AND donor_support_ok AND dgp_covered",
            "adapter_or_null_partial",
            "augsynth_remediation_research",
            "production_inference_requested OR adapter_missing",
            required_prior_artifacts=(
                "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
                "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
            ),
            authorization_boundary="augsynth_production_blocked_until_remediated",
        ),
        _row(
            "routing_synthetic_did_readiness_scout",
            "Synthetic DID readiness/scout until implementation and suitability validation",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "synthetic_did_route_request",
            DecisionTarget.METHOD_FAMILY,
            RouteStatus.RESEARCH_ONLY,
            "implementation_readiness_pass AND suitability_validation_pass",
            "scout_diagnostic_readout",
            "synthetic_did_scout_exploration",
            "production_inference_requested OR implementation_readiness_missing",
            required_prior_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            authorization_boundary="synthetic_did_production_unauthorized",
            recommended_next_artifact="SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
        ),
        _row(
            "routing_tbrridge_diagnostic_only",
            "TBRRidge diagnostic unless remediation plan proves otherwise",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "tbrridge_route_request",
            DecisionTarget.METHOD_FAMILY,
            RouteStatus.DIAGNOSTIC_ONLY,
            "remediation_plan_complete AND remediation_evidence_pass",
            "tbrridge_diagnostic_readout",
            "tbrridge_remediation_research",
            "production_inference_requested OR remediation_unresolved",
            required_prior_artifacts=("TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",),
            authorization_boundary="tbrridge_diagnostic_unless_remediated",
        ),
        _row(
            "routing_classic_tbr_retire_replace_blocked",
            "Classic/Aggregate TBR overclaim paths retire/replace or blocked",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "classic_tbr_route_request",
            DecisionTarget.METHOD_FAMILY,
            RouteStatus.BLOCKED,
            "retire_replace_complete AND replacement_path_validated",
            "retire_replace_planning",
            "classic_tbr_research_audit",
            "production_overclaim OR retire_replace_incomplete",
            required_prior_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            authorization_boundary="classic_tbr_retire_replace_priority",
            recommended_next_artifact="METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
        ),
        _row(
            "routing_bayesian_tbr_posterior_diagnostic_only",
            "Bayesian TBR posterior intervals posterior diagnostic only, not causal CI",
            SelectionLayer.INFERENCE_ELIGIBILITY,
            "bayesian_tbr_inference_request",
            DecisionTarget.INFERENCE,
            RouteStatus.DIAGNOSTIC_ONLY,
            "calibration_replay_pass AND posterior_contract_valid",
            "posterior_diagnostic_readout",
            "calibration_replay_research",
            "causal_ci_requested OR calibration_replay_missing",
            required_prior_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            authorization_boundary="posterior_not_causal_ci",
        ),
        _row(
            "routing_trop_research_only",
            "TROP research-only; production recommendations/budget/decisioning blocked",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "trop_route_request",
            DecisionTarget.METHOD_FAMILY,
            RouteStatus.RESEARCH_ONLY,
            "future_evidence_changes_status",
            "trop_evidence_scout_diagnostic",
            "trop_research_exploration",
            "production_recommendation OR budget_optimization OR production_decisioning",
            required_prior_artifacts=("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
            authorization_boundary="trop_research_only_unless_future_evidence",
        ),
        _row(
            "routing_multicell_blocked_research_only",
            "Multicell/shared-control blocked/research-only without dependence/multiplicity/release gate",
            SelectionLayer.MULTICELL_DEPENDENCE_MULTIPLICITY,
            "multicell_route_request",
            DecisionTarget.FULL_TUPLE,
            RouteStatus.BLOCKED,
            "dependence_validated AND multiplicity_validated AND release_gate_authorized",
            "per_cell_marginal_diagnostic",
            "multicell_research_exploration",
            "shared_control_unresolved OR multiplicity_unresolved OR naive_per_cell_p_value",
            required_prior_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
            authorization_boundary="multicell_production_claim_unauthorized",
        ),
        _row(
            "routing_unknown_assignment_blocks_inference",
            "Unknown/deterministic assignment blocks design-based inference",
            SelectionLayer.ASSIGNMENT_MECHANISM,
            "assignment_mechanism_signal",
            DecisionTarget.INFERENCE,
            RouteStatus.BLOCKED,
            "randomization_or_placebo_contract_valid",
            "assignment_diagnostic_review",
            "assignment_research_audit",
            "assignment_unknown OR assignment_deterministic_without_stress",
            required_prior_artifacts=("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
            failure_modes_checked=("FM-INF-009",),
            authorization_boundary="design_based_inference_requires_valid_assignment",
        ),
        _row(
            "routing_degenerate_assignment_blocks_rank_inference",
            "Small/degenerate assignment support blocks rank/randomization inference",
            SelectionLayer.ASSIGNMENT_MECHANISM,
            "assignment_support_signal",
            DecisionTarget.INFERENCE,
            RouteStatus.BLOCKED,
            "assignment_support_adequate AND rank_inference_valid",
            "rank_diagnostic_exploration",
            "assignment_stress_research",
            "assignment_support_degenerate OR small_cell_count",
            required_prior_artifacts=("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
            authorization_boundary="rank_inference_requires_support",
        ),
        _row(
            "routing_sparse_outcome_scale_check",
            "Sparse/count/rate outcomes require outcome-scale checks before route",
            SelectionLayer.OUTCOME_KPI_COMPATIBILITY,
            "outcome_scale_signal",
            DecisionTarget.ESTIMATOR_INFERENCE_PAIR,
            RouteStatus.ELIGIBLE_AFTER_WARNING,
            "outcome_scale_compatible AND sparse_outcome_dgp_covered",
            "outcome_scale_warning_present",
            "sparse_outcome_research_path",
            "outcome_scale_incompatible OR sparse_without_dgp",
            required_prior_artifacts=("SIMULATION_DGP_COVERAGE_PLAN_001", "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"),
            authorization_boundary="outcome_scale_gate_required",
        ),
        _row(
            "routing_multiplicity_before_inferential_claims",
            "Multiple KPIs/cells require multiplicity handling before inferential claims",
            SelectionLayer.MULTICELL_DEPENDENCE_MULTIPLICITY,
            "multiplicity_signal",
            DecisionTarget.INFERENCE,
            RouteStatus.BLOCKED,
            "multiplicity_handled AND claim_scope_validated",
            "marginal_per_cell_diagnostic",
            "multiplicity_research_candidate",
            "simultaneous_inferential_claim_without_multiplicity",
            required_prior_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
            authorization_boundary="multiplicity_required_for_inferential_claims",
        ),
        _row(
            "routing_downstream_authorization_blocked",
            "No route may authorize TrustReport/CalibrationSignal/MMM/LLM/API/scheduler/budget",
            SelectionLayer.DOWNSTREAM_BOUNDARY,
            "downstream_authorization_request",
            DecisionTarget.DOWNSTREAM_AUTHORIZATION,
            RouteStatus.RELEASE_GATE_REQUIRED,
            "release_gate_authorized AND downstream_role_explicitly_allowed",
            "downstream_diagnostic_contract_only",
            "downstream_research_boundary_review",
            "any_downstream_production_role_without_release_gate",
            required_prior_artifacts=(
                "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",
                "PRODUCTION_READINESS_BACKLOG_LEDGER_001",
            ),
            authorization_boundary="downstream_unauthorized_without_release_gate",
        ),
    ]


_LAYER_DEFAULTS: dict[SelectionLayer, dict[str, Any]] = {
    SelectionLayer.DATA_INTAKE: {
        "input_signal": "panel_data_frame",
        "decision_target": DecisionTarget.FULL_TUPLE,
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "diagnostics": ("panel_schema_valid",),
        "boundary": "data_intake_contract_required",
    },
    SelectionLayer.EXPERIMENT_METADATA: {
        "input_signal": "experiment_metadata",
        "decision_target": DecisionTarget.DESIGN,
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "diagnostics": ("experiment_id_present", "cell_structure_declared"),
        "boundary": "experiment_metadata_contract_required",
    },
    SelectionLayer.ASSIGNMENT_MECHANISM: {
        "input_signal": "assignment_mechanism_metadata",
        "decision_target": DecisionTarget.DESIGN,
        "artifacts": ("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
        "diagnostics": ("assignment_mechanism_declared",),
        "boundary": "assignment_mechanism_must_be_declared",
    },
    SelectionLayer.DESIGN_ELIGIBILITY: {
        "input_signal": "design_eligibility_request",
        "decision_target": DecisionTarget.DESIGN,
        "artifacts": ("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
        "diagnostics": ("ST-AD-001",),
        "boundary": "design_eligibility_separate_from_estimator",
    },
    SelectionLayer.ESTIMATOR_ELIGIBILITY: {
        "input_signal": "estimator_eligibility_request",
        "decision_target": DecisionTarget.ESTIMATOR,
        "artifacts": ("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
        "diagnostics": ("method_family_suitability",),
        "boundary": "estimator_allowed_does_not_imply_inference_allowed",
    },
    SelectionLayer.INFERENCE_ELIGIBILITY: {
        "input_signal": "inference_eligibility_request",
        "decision_target": DecisionTarget.INFERENCE,
        "artifacts": ("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
        "diagnostics": ("null_calibration_readiness",),
        "boundary": "inference_eligibility_separate_from_estimator",
    },
    SelectionLayer.OUTCOME_KPI_COMPATIBILITY: {
        "input_signal": "outcome_kpi_metadata",
        "decision_target": DecisionTarget.ESTIMATOR_INFERENCE_PAIR,
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "diagnostics": ("outcome_scale_check",),
        "boundary": "outcome_kpi_compatibility_required",
    },
    SelectionLayer.OBSERVED_DIAGNOSTICS: {
        "input_signal": "observed_panel_diagnostics",
        "decision_target": DecisionTarget.FULL_TUPLE,
        "artifacts": ("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
        "diagnostics": ("OPD_router_inputs",),
        "boundary": "diagnostics_feed_router_eligibility",
    },
    SelectionLayer.SIMULATION_DGP_COVERAGE: {
        "input_signal": "dgp_coverage_state",
        "decision_target": DecisionTarget.ESTIMATOR,
        "artifacts": ("SIMULATION_DGP_COVERAGE_PLAN_001",),
        "diagnostics": ("dgp_world_coverage",),
        "boundary": "dgp_evidence_required_for_promotion_hypothesis",
    },
    SelectionLayer.FAILURE_REGISTRY: {
        "input_signal": "failure_registry_state",
        "decision_target": DecisionTarget.FULL_TUPLE,
        "artifacts": ("METHOD_FAILURE_MODE_REGISTRY_001",),
        "diagnostics": (),
        "failure_modes": ("FM-ES-001", "FM-CP-003", "FM-CP-004", "FM-INF-009"),
        "boundary": "failure_registry_blocks_unresolved_modes",
    },
    SelectionLayer.MULTICELL_DEPENDENCE_MULTIPLICITY: {
        "input_signal": "multicell_geometry_signal",
        "decision_target": DecisionTarget.FULL_TUPLE,
        "artifacts": ("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
        "diagnostics": ("shared_control_dependence", "multiplicity_state"),
        "boundary": "multicell_cross_family_blocker",
    },
    SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS: {
        "input_signal": "method_family_promotion_state",
        "decision_target": DecisionTarget.METHOD_FAMILY,
        "artifacts": ("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001", "PRODUCTION_READINESS_BACKLOG_LEDGER_001"),
        "diagnostics": ("promotion_criteria_status",),
        "boundary": "resolved_plan_not_production_ready",
    },
    SelectionLayer.RELEASE_GATE: {
        "input_signal": "release_gate_state",
        "decision_target": DecisionTarget.DOWNSTREAM_AUTHORIZATION,
        "artifacts": ("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
        "diagnostics": ("release_gate_checklist",),
        "boundary": "release_gate_required_before_authorization",
    },
    SelectionLayer.DOWNSTREAM_BOUNDARY: {
        "input_signal": "downstream_role_request",
        "decision_target": DecisionTarget.DOWNSTREAM_AUTHORIZATION,
        "artifacts": ("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
        "diagnostics": (),
        "boundary": "downstream_roles_blocked",
    },
}


_LAYER_VARIANTS: tuple[tuple[str, RouteStatus, str], ...] = (
    ("gate", RouteStatus.ELIGIBLE, "Primary eligibility gate for this selection layer."),
    ("warning", RouteStatus.ELIGIBLE_AFTER_WARNING, "Eligible with warnings; not sufficient for production."),
    ("diagnostic", RouteStatus.DIAGNOSTIC_ONLY, "Diagnostic-only route at this layer."),
    ("blocked", RouteStatus.BLOCKED, "Route blocked at this layer."),
    ("research", RouteStatus.RESEARCH_ONLY, "Research-only route at this layer."),
)


def _layer_variant_rows() -> list[SelectionGateRequirementRow]:
    rows: list[SelectionGateRequirementRow] = []
    targets = list(DecisionTarget)
    for layer in SelectionLayer:
        defaults = _LAYER_DEFAULTS[layer]
        for idx, (suffix, status, note) in enumerate(_LAYER_VARIANTS):
            target = targets[idx % len(targets)]
            if layer in (SelectionLayer.RELEASE_GATE, SelectionLayer.DOWNSTREAM_BOUNDARY):
                target = DecisionTarget.DOWNSTREAM_AUTHORIZATION
            elif layer == SelectionLayer.DESIGN_ELIGIBILITY:
                target = DecisionTarget.DESIGN
            elif layer == SelectionLayer.ESTIMATOR_ELIGIBILITY:
                target = DecisionTarget.ESTIMATOR
            elif layer == SelectionLayer.INFERENCE_ELIGIBILITY:
                target = DecisionTarget.INFERENCE
            rows.append(
                _row(
                    f"{layer.value}_{suffix}",
                    f"{layer.value.replace('_', ' ').title()} {suffix}",
                    layer,
                    defaults["input_signal"],
                    target,
                    status,
                    f"prior_artifacts_satisfied AND {layer.value}_criteria_met",
                    f"{layer.value}_diagnostic_warning",
                    f"{layer.value}_research_exploration",
                    f"{layer.value}_criteria_fail OR unresolved_blocker",
                    required_prior_artifacts=defaults["artifacts"],
                    required_diagnostics=defaults.get("diagnostics", ()),
                    required_validation_evidence=(f"{layer.value}_validation",),
                    failure_modes_checked=defaults.get("failure_modes", ()),
                    authorization_boundary=defaults["boundary"],
                    notes=note,
                )
            )
    return rows


def _extra_coverage_rows() -> list[SelectionGateRequirementRow]:
    """Additional rows to ensure all route statuses and decision targets are represented."""
    return [
        _row(
            "open_investigations_consultation",
            "Open investigations consultation requirement",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "open_investigations_state",
            DecisionTarget.FULL_TUPLE,
            RouteStatus.CANDIDATE_AFTER_VALIDATION,
            "no_blocking_open_investigation",
            "investigation_warning_present",
            "investigation_research_followup",
            "blocking_open_investigation_unresolved",
            required_prior_artifacts=("OPEN_INVESTIGATIONS_001", "PRODUCTION_READINESS_BACKLOG_LEDGER_001"),
            authorization_boundary="open_investigations_must_be_consulted",
        ),
        _row(
            "backlog_ledger_consultation",
            "Production readiness backlog consultation requirement",
            SelectionLayer.METHOD_FAMILY_PROMOTION_STATUS,
            "backlog_ledger_state",
            DecisionTarget.FULL_TUPLE,
            RouteStatus.CANDIDATE_AFTER_VALIDATION,
            "backlog_item_resolved_or_tracked",
            "backlog_warning_item",
            "backlog_research_item",
            "untracked_backlog_blocker",
            required_prior_artifacts=("PRODUCTION_READINESS_BACKLOG_LEDGER_001",),
            authorization_boundary="backlog_must_be_consulted",
        ),
        _row(
            "blocked_reason_payload",
            "Selector must return blocked reasons",
            SelectionLayer.DOWNSTREAM_BOUNDARY,
            "route_decision_output",
            DecisionTarget.FULL_TUPLE,
            RouteStatus.BLOCKED,
            "never_for_blocked_route",
            "diagnostic_with_reason",
            "research_with_reason",
            "blocked_without_reason_code",
            required_prior_artifacts=(_ARTIFACT_ID,),
            authorization_boundary="blocked_reason_required",
        ),
        _row(
            "next_best_alternative_payload",
            "Selector must return next-best diagnostic/research alternatives",
            SelectionLayer.DOWNSTREAM_BOUNDARY,
            "route_decision_output",
            DecisionTarget.FULL_TUPLE,
            RouteStatus.DIAGNOSTIC_ONLY,
            "primary_route_blocked_with_alternative",
            "diagnostic_alternative_offered",
            "research_alternative_offered",
            "blocked_without_alternative",
            required_prior_artifacts=(_ARTIFACT_ID,),
            authorization_boundary="next_best_alternative_required",
        ),
        _row(
            "release_gate_candidate_status",
            "Release gate required route status",
            SelectionLayer.RELEASE_GATE,
            "production_authorization_request",
            DecisionTarget.DOWNSTREAM_AUTHORIZATION,
            RouteStatus.RELEASE_GATE_REQUIRED,
            "release_gate_plan_complete AND all_lanes_satisfied",
            "release_gate_planning",
            "authorization_research_audit",
            "release_gate_incomplete",
            required_prior_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            recommended_next_artifact="PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
            authorization_boundary="release_gate_required",
        ),
    ]


def build_data_driven_design_estimator_inference_selection_gate_requirements() -> tuple[
    SelectionGateRequirementRow, ...
]:
    """Build the selection gate requirements registry."""
    rows: list[SelectionGateRequirementRow] = []
    rows.extend(_routing_example_rows())
    rows.extend(_layer_variant_rows())
    rows.extend(_extra_coverage_rows())
    return tuple(rows)


def filter_data_driven_design_estimator_inference_selection_gate_requirements(
    rows: tuple[SelectionGateRequirementRow, ...],
    *,
    selection_layer: SelectionLayer | None = None,
    decision_target: DecisionTarget | None = None,
    route_status: RouteStatus | None = None,
    routing_example: bool | None = None,
) -> tuple[SelectionGateRequirementRow, ...]:
    """Filter selection gate requirement rows by optional criteria."""
    result: list[SelectionGateRequirementRow] = []
    for row in rows:
        if selection_layer is not None and row.selection_layer != selection_layer:
            continue
        if decision_target is not None and row.decision_target != decision_target:
            continue
        if route_status is not None and row.route_status != route_status:
            continue
        if routing_example is not None:
            is_example = row.requirement_id in REQUIRED_ROUTING_EXAMPLE_IDS
            if routing_example != is_example:
                continue
        result.append(row)
    return tuple(result)


def validate_data_driven_design_estimator_inference_selection_gate_requirements(
    rows: tuple[SelectionGateRequirementRow, ...],
) -> dict[str, Any]:
    """Validate selection gate requirements registry thresholds and coverage."""
    issues: list[str] = []
    requirement_ids = [r.requirement_id for r in rows]

    if len(rows) < MIN_REQUIREMENTS_ROW_COUNT:
        issues.append(f"requirements_row_count {len(rows)} < {MIN_REQUIREMENTS_ROW_COUNT}")
    if len(requirement_ids) != len(set(requirement_ids)):
        issues.append("duplicate requirement_id values")

    layer_counts = Counter(r.selection_layer.value for r in rows)
    target_counts = Counter(r.decision_target.value for r in rows)
    status_counts = Counter(r.route_status.value for r in rows)

    for layer in REQUIRED_SELECTION_LAYERS:
        if not any(r.selection_layer == layer for r in rows):
            issues.append(f"missing selection_layer: {layer.value}")

    for target in REQUIRED_DECISION_TARGETS:
        if not any(r.decision_target == target for r in rows):
            issues.append(f"missing decision_target: {target.value}")

    for status in REQUIRED_ROUTE_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing route_status: {status.value}")

    for example_id in REQUIRED_ROUTING_EXAMPLE_IDS:
        if example_id not in requirement_ids:
            issues.append(f"missing routing example: {example_id}")

    estimator_inference_sep = any(
        r.selection_layer == SelectionLayer.ESTIMATOR_ELIGIBILITY for r in rows
    ) and any(r.selection_layer == SelectionLayer.INFERENCE_ELIGIBILITY for r in rows)
    if not estimator_inference_sep:
        issues.append("design/estimator/inference separation missing")

    return {
        "valid": not issues,
        "requirements_row_count": len(rows),
        "unique_requirement_ids": len(requirement_ids) == len(set(requirement_ids)),
        "selection_layer_counts": dict(layer_counts),
        "decision_target_counts": dict(target_counts),
        "route_status_counts": {s.value: status_counts.get(s, 0) for s in RouteStatus},
        "all_required_selection_layers_covered": all(
            any(r.selection_layer == layer for r in rows) for layer in REQUIRED_SELECTION_LAYERS
        ),
        "all_required_decision_targets_covered": all(
            any(r.decision_target == t for r in rows) for t in REQUIRED_DECISION_TARGETS
        ),
        "all_required_route_statuses_covered": all(
            status_counts.get(s, 0) > 0 for s in REQUIRED_ROUTE_STATUSES
        ),
        "all_required_routing_examples_covered": all(
            e in requirement_ids for e in REQUIRED_ROUTING_EXAMPLE_IDS
        ),
        "issues": issues,
    }


def summarize_data_driven_design_estimator_inference_selection_gate_requirements(
    rows: tuple[SelectionGateRequirementRow, ...],
) -> dict[str, Any]:
    """Serialize selection gate requirements summary for archives."""
    validation = validate_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "requirements_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "selection_layer_counts": validation["selection_layer_counts"],
        "decision_target_counts": validation["decision_target_counts"],
        "route_status_counts": validation["route_status_counts"],
        "all_required_selection_layers_covered": validation["all_required_selection_layers_covered"],
        "all_required_decision_targets_covered": validation["all_required_decision_targets_covered"],
        "all_required_route_statuses_covered": validation["all_required_route_statuses_covered"],
        "all_required_routing_examples_covered": validation["all_required_routing_examples_covered"],
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
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    validation = validate_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    summary = summarize_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("requirements_rows_build_successfully", len(rows) > 0))
    scenarios.append(
        _scenario("requirements_row_count_at_least_70", len(rows) >= MIN_REQUIREMENTS_ROW_COUNT)
    )
    scenarios.append(_scenario("requirement_ids_unique", validation["unique_requirement_ids"]))

    for layer in REQUIRED_SELECTION_LAYERS:
        present = any(r.selection_layer == layer for r in rows)
        scenarios.append(_scenario(f"selection_layer_{layer.value}_represented", present))

    for target in REQUIRED_DECISION_TARGETS:
        present = any(r.decision_target == target for r in rows)
        scenarios.append(_scenario(f"decision_target_{target.value}_represented", present))

    for status in REQUIRED_ROUTE_STATUSES:
        count = sum(1 for r in rows if r.route_status == status)
        scenarios.append(_scenario(f"route_status_{status.value}_represented", count > 0))

    for example_id in REQUIRED_ROUTING_EXAMPLE_IDS:
        present = any(r.requirement_id == example_id for r in rows)
        scenarios.append(_scenario(f"routing_example_{example_id}_represented", present))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_augsynth_remediation",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_data_driven_design_estimator_inference_selection_gate_requirements()
    validation = validate_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    summary = summarize_data_driven_design_estimator_inference_selection_gate_requirements(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "requirements_row_count": len(rows),
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
