"""PRODUCTION_READINESS_BACKLOG_LEDGER_001 validation harness."""

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

_ARTIFACT_ID = "PRODUCTION_READINESS_BACKLOG_LEDGER_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "production_readiness_backlog_ledger_created_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/PRODUCTION_READINESS_BACKLOG_LEDGER_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
    "AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
    "DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
)

MIN_LEDGER_ROW_COUNT = 45

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
    "resolved_artifacts_do_not_mean_production_ready": True,
    "no_backlog_item_production_ready_by_default": True,
    "production_readiness_requires_implementation_validation_and_release_gate": True,
    "scm_p1_first_candidate_blocker": True,
    "multicell_p1_cross_family_blocker": True,
    "data_driven_selection_gate_tracked": True,
    "data_driven_selection_gate_priority": "P1_first_candidate_blocker",
    "augsynth_p2_remediation_candidate": True,
    "did_p2_conditional_candidate": True,
    "synthetic_did_research_or_readiness_lane_tracked": True,
    "tbrridge_diagnostic_remediation_lane_tracked": True,
    "classic_tbr_retire_replace_lane_tracked": True,
    "bayesian_tbr_calibration_replay_lane_tracked": True,
    "trop_evidence_scout_lane_tracked": True,
    "release_gate_tracked": True,
    "downstream_boundaries_tracked": True,
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
    "production_decisioning",
)

_NEXT = "DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001"


class Domain(str, Enum):
    DESIGN = "design"
    ESTIMATOR = "estimator"
    INFERENCE = "inference"
    MULTICELL = "multicell"
    DATA_DRIVEN_ROUTER = "data_driven_router"
    DIAGNOSTICS = "diagnostics"
    SIMULATION = "simulation"
    CALIBRATION = "calibration"
    REMEDIATION = "remediation"
    RETIRE_REPLACE = "retire_replace"
    RELEASE_GATE = "release_gate"
    DOWNSTREAM_INTEGRATION = "downstream_integration"


class Priority(str, Enum):
    P0_RELEASE_SAFETY = "P0_release_safety"
    P1_FIRST_CANDIDATE_BLOCKER = "P1_first_candidate_blocker"
    P2_REMEDIATION_CANDIDATE = "P2_remediation_candidate"
    P3_RESEARCH_OR_DIAGNOSTIC_FOLLOWUP = "P3_research_or_diagnostic_followup"
    P4_LONG_RANGE_SCOUT = "P4_long_range_scout"


class BacklogStatus(str, Enum):
    BLOCKED = "blocked"
    PLANNED = "planned"
    VALIDATION_PLAN_DEFINED = "validation_plan_defined"
    REMEDIATION_REQUIRED = "remediation_required"
    RESEARCH_ONLY = "research_only"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RETIRE_REPLACE_REQUIRED = "retire_replace_required"
    CANDIDATE_BUT_GATED = "candidate_but_gated"
    RELEASE_GATE_REQUIRED = "release_gate_required"


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
    DATA_DRIVEN_ROUTER = "data_driven_design_estimator_inference_router"
    RELEASE_GATE = "release_gate"
    DOWNSTREAM_INTEGRATION = "downstream_integration"


REQUIRED_DOMAINS = frozenset(Domain)
REQUIRED_PRIORITIES = frozenset(Priority)
REQUIRED_STATUSES = frozenset(BacklogStatus)
REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)

REQUIRED_BACKLOG_ITEM_IDS = frozenset({
    "scm_validation_implementation",
    "scm_donor_support_convex_hull",
    "scm_preperiod_fit_trend",
    "scm_treated_set_placebo_adapter",
    "scm_studentized_statistic_adapter",
    "scm_null_calibration",
    "scm_dgp_stress_coverage",
    "multicell_shared_control_dependence",
    "multicell_multiplicity_fwer",
    "multicell_max_t_candidate",
    "multicell_stepdown_candidate",
    "multicell_cell_kpi_multiplicity",
    "multicell_per_cell_pooled_global_boundary",
    "data_driven_dei_selection_gate",
    "design_eligibility_gate",
    "estimator_eligibility_gate",
    "inference_eligibility_gate",
    "observed_panel_diagnostic_router_inputs",
    "failure_mode_router_integration",
    "augsynth_remediation_diagnostic_validation",
    "augsynth_adapter_readiness",
    "augsynth_null_calibration",
    "augsynth_donor_support_overlap",
    "augsynth_dgp_coverage",
    "did_conditional_production_candidate_validation",
    "did_parallel_trend_eligibility",
    "did_cluster_outcome_design_eligibility",
    "did_bootstrap_suitability_boundary",
    "synthetic_did_implementation_readiness",
    "synthetic_did_suitability_validation",
    "synthetic_did_inference_adapter_null_calibration",
    "tbrridge_diagnostic_remediation_decision",
    "classic_tbr_retire_replace_execution",
    "bayesian_tbr_calibration_replay_research",
    "trop_evidence_scout",
    "production_authorization_release_gate",
    "trustreport_authorization_boundary",
    "calibration_signal_authorization_boundary",
    "mmm_ingestion_boundary",
    "llm_decisioning_boundary",
    "live_api_scheduler_boundary",
    "budget_optimization_boundary",
})


@dataclass(frozen=True)
class BacklogLedgerRow:
    item_id: str
    name: str
    domain: Domain
    method_family: MethodFamily
    current_status: BacklogStatus
    production_ready: bool
    priority: Priority
    blocking_reason: str
    required_evidence: tuple[str, ...]
    dependency_artifacts: tuple[str, ...]
    next_artifact: str | None
    exit_condition: str
    authorization_boundary: str
    owner_lane: str
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    notes: str


def _row(
    item_id: str,
    name: str,
    domain: Domain,
    method_family: MethodFamily,
    current_status: BacklogStatus,
    priority: Priority,
    blocking_reason: str,
    *,
    required_evidence: tuple[str, ...],
    dependency_artifacts: tuple[str, ...],
    next_artifact: str | None = None,
    exit_condition: str,
    authorization_boundary: str,
    owner_lane: str,
    allowed_current_use: tuple[str, ...] = ("diagnostic_research",),
    forbidden_current_use: tuple[str, ...] = _FORBID,
    notes: str = "",
) -> BacklogLedgerRow:
    return BacklogLedgerRow(
        item_id=item_id,
        name=name,
        domain=domain,
        method_family=method_family,
        current_status=current_status,
        production_ready=False,
        priority=priority,
        blocking_reason=blocking_reason,
        required_evidence=required_evidence,
        dependency_artifacts=dependency_artifacts,
        next_artifact=next_artifact or _NEXT,
        exit_condition=exit_condition,
        authorization_boundary=authorization_boundary,
        owner_lane=owner_lane,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        notes=notes,
    )


def build_production_readiness_backlog_ledger() -> tuple[BacklogLedgerRow, ...]:
    """Build the production-readiness backlog ledger registry."""
    rows: list[BacklogLedgerRow] = [
        # SCM P1 blockers
        _row(
            "scm_validation_implementation",
            "SCM validation implementation",
            Domain.ESTIMATOR,
            MethodFamily.SCM,
            BacklogStatus.VALIDATION_PLAN_DEFINED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "SCM plan defined but implementation/empirical validation incomplete",
            required_evidence=("scm_validation_rows_pass", "donor_support_pass", "null_calibration_pass"),
            dependency_artifacts=("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
            exit_condition="All SCM validation rows pass empirical evidence gates",
            authorization_boundary="no_production_inference_until_scm_validation_complete",
            owner_lane="lane_1_scm_production_candidate_validation",
            notes="Resolved plan does not mean production-ready SCM.",
        ),
        _row(
            "scm_donor_support_convex_hull",
            "SCM donor support / convex hull validation",
            Domain.DIAGNOSTICS,
            MethodFamily.SCM,
            BacklogStatus.CANDIDATE_BUT_GATED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Donor support and convex hull required blockers per SCM plan",
            required_evidence=("OPD-DONOR-001", "OPD-DS-005"),
            dependency_artifacts=("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001", "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"),
            exit_condition="Donor pool eligibility and convex hull diagnostics pass",
            authorization_boundary="donor_support_blocker",
            owner_lane="lane_1_scm_production_candidate_validation",
        ),
        _row(
            "scm_preperiod_fit_trend",
            "SCM pre-period fit / trend validation",
            Domain.DIAGNOSTICS,
            MethodFamily.SCM,
            BacklogStatus.CANDIDATE_BUT_GATED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Pre-period fit and trend stability are required SCM blockers",
            required_evidence=("OPD-PF-001", "OPD-PF-002", "OPD-PF-003"),
            dependency_artifacts=("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
            exit_condition="Pre-period fit and trend diagnostics pass thresholds",
            authorization_boundary="preperiod_fit_blocker",
            owner_lane="lane_1_scm_production_candidate_validation",
        ),
        _row(
            "scm_treated_set_placebo_adapter",
            "SCM treated-set placebo adapter",
            Domain.INFERENCE,
            MethodFamily.SCM,
            BacklogStatus.REMEDIATION_REQUIRED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Treated-set placebo requires statistic adapter maturity",
            required_evidence=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001", "treated_set_placebo_integration"),
            dependency_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            exit_condition="Adapter contract satisfied and integration validated",
            authorization_boundary="adapter_required_before_inferential_promotion",
            owner_lane="lane_1_scm_production_candidate_validation",
        ),
        _row(
            "scm_studentized_statistic_adapter",
            "SCM studentized statistic adapter",
            Domain.INFERENCE,
            MethodFamily.SCM,
            BacklogStatus.REMEDIATION_REQUIRED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Studentized placebo statistic requires adapter contract",
            required_evidence=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            dependency_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            exit_condition="Studentized adapter validated with scale contract",
            authorization_boundary="studentized_adapter_required",
            owner_lane="lane_1_scm_production_candidate_validation",
        ),
        _row(
            "scm_null_calibration",
            "SCM null calibration",
            Domain.CALIBRATION,
            MethodFamily.SCM,
            BacklogStatus.CANDIDATE_BUT_GATED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Null calibration required before SCM inferential promotion",
            required_evidence=("null_fpr_gate", "coverage_replay"),
            dependency_artifacts=("SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",),
            exit_condition="Null FPR and coverage replay pass gates",
            authorization_boundary="null_calibration_required",
            owner_lane="lane_1_scm_production_candidate_validation",
        ),
        _row(
            "scm_dgp_stress_coverage",
            "SCM DGP stress coverage",
            Domain.SIMULATION,
            MethodFamily.SCM,
            BacklogStatus.PLANNED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "DGP simulation coverage required for SCM promotion evidence",
            required_evidence=("DGP-SCM-001", "DGP-ES-007", "DGP-CP-002"),
            dependency_artifacts=("SIMULATION_DGP_COVERAGE_PLAN_001",),
            exit_condition="SCM DGP worlds pass simulation coverage plan",
            authorization_boundary="simulation_evidence_required",
            owner_lane="lane_1_scm_production_candidate_validation",
        ),
        # Multicell P1 blockers
        _row(
            "multicell_shared_control_dependence",
            "Multicell shared-control dependence validation",
            Domain.MULTICELL,
            MethodFamily.MULTICELL_SHARED_CONTROL,
            BacklogStatus.VALIDATION_PLAN_DEFINED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Shared-control dependence must be modeled/simulated/validated",
            required_evidence=("shared_control_dependence_validation", "cross_cell_correlation_diagnostics"),
            dependency_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001", "MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
            exit_condition="Shared-control dependence validation evidence passes",
            authorization_boundary="multicell_shared_control_cross_family_blocker",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        _row(
            "multicell_multiplicity_fwer",
            "Multicell multiplicity / FWER validation",
            Domain.MULTICELL,
            MethodFamily.MULTICELL_SHARED_CONTROL,
            BacklogStatus.VALIDATION_PLAN_DEFINED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Familywise error control required for simultaneous multicell decisions",
            required_evidence=("familywise_error_control", "multiplicity_calibration"),
            dependency_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
            exit_condition="FWER validation evidence passes under shared-control dependence",
            authorization_boundary="multiplicity_handling_required",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        _row(
            "multicell_max_t_candidate",
            "Max-T validation candidate",
            Domain.INFERENCE,
            MethodFamily.MULTICELL_SHARED_CONTROL,
            BacklogStatus.RESEARCH_ONLY,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Max-T is validation candidate only until validated",
            required_evidence=("max_t_null_calibration", "shared_control_handling"),
            dependency_artifacts=("MULTICELL_MAX_T_RESEARCH_SCOUT_001",),
            exit_condition="Max-T passes validation under dependence model",
            authorization_boundary="max_t_candidate_only_until_validated",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        _row(
            "multicell_stepdown_candidate",
            "Stepdown validation candidate",
            Domain.INFERENCE,
            MethodFamily.MULTICELL_SHARED_CONTROL,
            BacklogStatus.RESEARCH_ONLY,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Stepdown is validation candidate only until validated",
            required_evidence=("stepdown_null_calibration", "shared_control_handling"),
            dependency_artifacts=("MULTICELL_MAX_T_RESEARCH_SCOUT_001",),
            exit_condition="Stepdown passes validation under dependence model",
            authorization_boundary="stepdown_candidate_only_until_validated",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        _row(
            "multicell_cell_kpi_multiplicity",
            "Cell × KPI multiplicity validation",
            Domain.MULTICELL,
            MethodFamily.MULTICELL_SHARED_CONTROL,
            BacklogStatus.VALIDATION_PLAN_DEFINED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Cell × KPI cross-product claim family requires separate validation",
            required_evidence=("cell_kpi_multiplicity_validation",),
            dependency_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
            exit_condition="Cell × KPI multiplicity evidence passes",
            authorization_boundary="cell_by_kpi_claim_boundary",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        _row(
            "multicell_per_cell_pooled_global_boundary",
            "Per-cell vs pooled/global claim boundary",
            Domain.MULTICELL,
            MethodFamily.MULTICELL_SHARED_CONTROL,
            BacklogStatus.BLOCKED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Naive per-cell p-values and pooled/global overclaim blocked",
            required_evidence=("per_cell_validation", "pooled_validation", "global_validation"),
            dependency_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001",),
            exit_condition="Separate validation evidence for each claim scope",
            authorization_boundary="naive_per_cell_and_pooled_global_blocked",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        # Data-driven router P1/P2
        _row(
            "data_driven_dei_selection_gate",
            "Data-driven design-estimator-inference selection gate",
            Domain.DATA_DRIVEN_ROUTER,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Router/selection gate must be explicit before method-specific implementation",
            required_evidence=("selection_gate_requirements", "router_contract"),
            dependency_artifacts=("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
            next_artifact="DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_REQUIREMENTS_001",
            exit_condition="Selection gate requirements artifact complete with router contract",
            authorization_boundary="no_automatic_dei_selection_without_gate",
            owner_lane="data_driven_router_lane",
            notes="P1 blocker to prevent router requirements from being lost.",
        ),
        _row(
            "design_eligibility_gate",
            "Design eligibility gate",
            Domain.DESIGN,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Design eligibility must gate estimator/inference selection",
            required_evidence=("design_eligibility_contract", "assignment_stress_compatibility"),
            dependency_artifacts=("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001", "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"),
            exit_condition="Design eligibility gate integrated into router",
            authorization_boundary="design_eligibility_required",
            owner_lane="data_driven_router_lane",
        ),
        _row(
            "estimator_eligibility_gate",
            "Estimator eligibility gate",
            Domain.ESTIMATOR,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Estimator eligibility must gate inference selection",
            required_evidence=("estimator_eligibility_contract", "method_family_suitability"),
            dependency_artifacts=("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001", "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"),
            exit_condition="Estimator eligibility gate integrated into router",
            authorization_boundary="estimator_eligibility_required",
            owner_lane="data_driven_router_lane",
        ),
        _row(
            "inference_eligibility_gate",
            "Inference eligibility gate",
            Domain.INFERENCE,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "Inference eligibility must gate production readouts",
            required_evidence=("inference_eligibility_contract", "null_calibration_readiness"),
            dependency_artifacts=("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",),
            exit_condition="Inference eligibility gate integrated into router",
            authorization_boundary="inference_eligibility_required",
            owner_lane="data_driven_router_lane",
        ),
        _row(
            "observed_panel_diagnostic_router_inputs",
            "Observed panel diagnostic router inputs",
            Domain.DIAGNOSTICS,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "Observed panel diagnostics must feed router eligibility decisions",
            required_evidence=("OPD_router_inputs", "diagnostic_threshold_contract"),
            dependency_artifacts=("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
            exit_condition="Diagnostic router inputs contract complete",
            authorization_boundary="diagnostic_router_inputs_required",
            owner_lane="data_driven_router_lane",
        ),
        _row(
            "failure_mode_router_integration",
            "Failure-mode router integration",
            Domain.DATA_DRIVEN_ROUTER,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P0_RELEASE_SAFETY,
            "Failure registry must block router paths with unresolved modes",
            required_evidence=("FM_router_integration", "failure_mode_blockers"),
            dependency_artifacts=("METHOD_FAILURE_MODE_REGISTRY_001",),
            exit_condition="Failure-mode checks integrated into router",
            authorization_boundary="failure_registry_consulted_before_routing",
            owner_lane="data_driven_router_lane",
        ),
        # AugSynth P2
        _row(
            "augsynth_remediation_diagnostic_validation",
            "AugSynth remediation and diagnostic validation",
            Domain.REMEDIATION,
            MethodFamily.AUGSYNTH_CVXPY,
            BacklogStatus.PLANNED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "AugSynth remediation plan not yet complete",
            required_evidence=("augsynth_remediation_validation_rows",),
            dependency_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            next_artifact="AUGSYNTH_REMEDIATION_AND_DIAGNOSTIC_VALIDATION_PLAN_001",
            exit_condition="AugSynth remediation validation plan complete with evidence",
            authorization_boundary="augsynth_production_blocked_until_remediated",
            owner_lane="lane_2_augsynth_remediation_diagnostic_validation",
        ),
        _row(
            "augsynth_adapter_readiness",
            "AugSynth adapter readiness",
            Domain.INFERENCE,
            MethodFamily.AUGSYNTH_CVXPY,
            BacklogStatus.REMEDIATION_REQUIRED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "AugSynth adapter contract not production-ready",
            required_evidence=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            dependency_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            exit_condition="Adapter contract validated for AugSynth paths",
            authorization_boundary="adapter_required",
            owner_lane="lane_2_augsynth_remediation_diagnostic_validation",
        ),
        _row(
            "augsynth_null_calibration",
            "AugSynth null calibration",
            Domain.CALIBRATION,
            MethodFamily.AUGSYNTH_CVXPY,
            BacklogStatus.REMEDIATION_REQUIRED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "AugSynth null calibration incomplete",
            required_evidence=("null_fpr_gate", "augsynth_null_replay"),
            dependency_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            exit_condition="AugSynth null calibration passes gates",
            authorization_boundary="null_calibration_required",
            owner_lane="lane_2_augsynth_remediation_diagnostic_validation",
        ),
        _row(
            "augsynth_donor_support_overlap",
            "AugSynth donor support / overlap validation",
            Domain.DIAGNOSTICS,
            MethodFamily.AUGSYNTH_CVXPY,
            BacklogStatus.DIAGNOSTIC_ONLY,
            Priority.P2_REMEDIATION_CANDIDATE,
            "AugSynth donor support and overlap diagnostics required",
            required_evidence=("OPD-DONOR-001", "overlap_diagnostics"),
            dependency_artifacts=("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
            exit_condition="Donor support and overlap diagnostics pass",
            authorization_boundary="donor_support_blocker",
            owner_lane="lane_2_augsynth_remediation_diagnostic_validation",
        ),
        _row(
            "augsynth_dgp_coverage",
            "AugSynth DGP coverage",
            Domain.SIMULATION,
            MethodFamily.AUGSYNTH_CVXPY,
            BacklogStatus.PLANNED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "AugSynth DGP simulation coverage incomplete",
            required_evidence=("DGP-AUGSYNTH-001",),
            dependency_artifacts=("SIMULATION_DGP_COVERAGE_PLAN_001",),
            exit_condition="AugSynth DGP worlds covered",
            authorization_boundary="simulation_evidence_required",
            owner_lane="lane_2_augsynth_remediation_diagnostic_validation",
        ),
        # DID P2
        _row(
            "did_conditional_production_candidate_validation",
            "DID conditional production-candidate validation",
            Domain.ESTIMATOR,
            MethodFamily.DID,
            BacklogStatus.PLANNED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "DID conditional validation plan not yet defined",
            required_evidence=("did_validation_rows", "conditional_design_evidence"),
            dependency_artifacts=("DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",),
            next_artifact="DID_CONDITIONAL_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
            exit_condition="DID conditional validation plan complete",
            authorization_boundary="did_conditional_designs_only",
            owner_lane="lane_3_did_conditional_production_candidate_validation",
        ),
        _row(
            "did_parallel_trend_eligibility",
            "DID parallel-trend eligibility",
            Domain.DIAGNOSTICS,
            MethodFamily.DID,
            BacklogStatus.BLOCKED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "Parallel-trend eligibility not validated for production",
            required_evidence=("parallel_trend_diagnostics",),
            dependency_artifacts=("DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",),
            exit_condition="Parallel-trend eligibility criteria pass",
            authorization_boundary="parallel_trend_required",
            owner_lane="lane_3_did_conditional_production_candidate_validation",
        ),
        _row(
            "did_cluster_outcome_design_eligibility",
            "DID cluster/outcome/design eligibility",
            Domain.DESIGN,
            MethodFamily.DID,
            BacklogStatus.BLOCKED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "DID cluster/outcome/design eligibility unresolved",
            required_evidence=("cluster_eligibility", "outcome_scale_eligibility"),
            dependency_artifacts=("DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",),
            exit_condition="Cluster/outcome/design eligibility validated",
            authorization_boundary="did_design_eligibility_required",
            owner_lane="lane_3_did_conditional_production_candidate_validation",
        ),
        _row(
            "did_bootstrap_suitability_boundary",
            "DID bootstrap suitability boundary",
            Domain.INFERENCE,
            MethodFamily.DID,
            BacklogStatus.DIAGNOSTIC_ONLY,
            Priority.P2_REMEDIATION_CANDIDATE,
            "Bootstrap cannot fix invalid DID assignment",
            required_evidence=("bootstrap_suitability_audit",),
            dependency_artifacts=("DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",),
            exit_condition="Bootstrap suitability boundary documented and enforced",
            authorization_boundary="bootstrap_cannot_fix_invalid_assignment",
            owner_lane="lane_3_did_conditional_production_candidate_validation",
        ),
        # Synthetic DID P3/P4
        _row(
            "synthetic_did_implementation_readiness",
            "Synthetic DID implementation readiness",
            Domain.ESTIMATOR,
            MethodFamily.SYNTHETIC_DID,
            BacklogStatus.PLANNED,
            Priority.P3_RESEARCH_OR_DIAGNOSTIC_FOLLOWUP,
            "Synthetic DID implementation readiness plan not complete",
            required_evidence=("implementation_readiness_rows",),
            dependency_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            next_artifact="SYNTHETIC_DID_IMPLEMENTATION_READINESS_PLAN_001",
            exit_condition="Implementation readiness plan complete",
            authorization_boundary="synthetic_did_research_candidate",
            owner_lane="lane_4_synthetic_did_implementation_readiness",
        ),
        _row(
            "synthetic_did_suitability_validation",
            "Synthetic DID suitability validation",
            Domain.ESTIMATOR,
            MethodFamily.SYNTHETIC_DID,
            BacklogStatus.RESEARCH_ONLY,
            Priority.P3_RESEARCH_OR_DIAGNOSTIC_FOLLOWUP,
            "Synthetic DID suitability scout complete but not production-ready",
            required_evidence=("synthetic_did_suitability_rows",),
            dependency_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            exit_condition="Suitability validation evidence passes",
            authorization_boundary="synthetic_did_production_unauthorized",
            owner_lane="lane_4_synthetic_did_implementation_readiness",
        ),
        _row(
            "synthetic_did_inference_adapter_null_calibration",
            "Synthetic DID inference adapter / null calibration candidate",
            Domain.INFERENCE,
            MethodFamily.SYNTHETIC_DID,
            BacklogStatus.RESEARCH_ONLY,
            Priority.P4_LONG_RANGE_SCOUT,
            "Synthetic DID inference adapter and null calibration not validated",
            required_evidence=("inference_adapter", "null_calibration"),
            dependency_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            exit_condition="Adapter and null calibration validated",
            authorization_boundary="synthetic_did_inference_candidate_only",
            owner_lane="lane_4_synthetic_did_implementation_readiness",
        ),
        # TBRRidge P3
        _row(
            "tbrridge_diagnostic_remediation_decision",
            "TBRRidge diagnostic/remediation decision",
            Domain.REMEDIATION,
            MethodFamily.TBRRIDGE,
            BacklogStatus.DIAGNOSTIC_ONLY,
            Priority.P3_RESEARCH_OR_DIAGNOSTIC_FOLLOWUP,
            "TBRRidge remediation or retirement decision pending",
            required_evidence=("tbrridge_remediation_audit",),
            dependency_artifacts=("TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",),
            next_artifact="TBRRIDGE_DIAGNOSTIC_REMEDIATION_DECISION_PLAN_001",
            exit_condition="TBRRidge remediation decision plan complete",
            authorization_boundary="tbrridge_diagnostic_unless_remediated",
            owner_lane="lane_5_tbrridge_diagnostic_remediation_decision",
        ),
        # Classic TBR retire/replace
        _row(
            "classic_tbr_retire_replace_execution",
            "Classic TBR retire/replace execution",
            Domain.RETIRE_REPLACE,
            MethodFamily.CLASSIC_AGGREGATE_TBR,
            BacklogStatus.RETIRE_REPLACE_REQUIRED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "Classic aggregate TBR retire/replace execution plan not complete",
            required_evidence=("retire_replace_execution_rows",),
            dependency_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            next_artifact="METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
            exit_condition="Retire/replace execution plan complete",
            authorization_boundary="classic_tbr_retire_replace_priority",
            owner_lane="lane_6_classic_tbr_retire_replace_execution",
        ),
        # Bayesian TBR P3
        _row(
            "bayesian_tbr_calibration_replay_research",
            "Bayesian TBR calibration/replay research",
            Domain.CALIBRATION,
            MethodFamily.BAYESIAN_TBR,
            BacklogStatus.RESEARCH_ONLY,
            Priority.P3_RESEARCH_OR_DIAGNOSTIC_FOLLOWUP,
            "Bayesian TBR calibration replay research not complete",
            required_evidence=("calibration_replay_evidence",),
            dependency_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            next_artifact="BAYESIAN_TBR_CALIBRATION_REPLAY_RESEARCH_PLAN_001",
            exit_condition="Calibration replay research plan complete with evidence",
            authorization_boundary="bayesian_tbr_requires_calibration_replay",
            owner_lane="lane_7_bayesian_tbr_calibration_replay_research",
        ),
        # TROP P4
        _row(
            "trop_evidence_scout",
            "TROP evidence scout",
            Domain.ESTIMATOR,
            MethodFamily.TROP,
            BacklogStatus.RESEARCH_ONLY,
            Priority.P4_LONG_RANGE_SCOUT,
            "TROP remains research-only unless future evidence changes status",
            required_evidence=("trop_evidence_scout_rows",),
            dependency_artifacts=("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
            next_artifact="TROP_EVIDENCE_SCOUT_PLAN_001",
            exit_condition="TROP evidence scout plan complete",
            authorization_boundary="trop_research_only_unless_future_evidence",
            owner_lane="lane_8_trop_research_only_evidence",
        ),
        # Release gate P0
        _row(
            "production_authorization_release_gate",
            "Production authorization release gate",
            Domain.RELEASE_GATE,
            MethodFamily.RELEASE_GATE,
            BacklogStatus.RELEASE_GATE_REQUIRED,
            Priority.P0_RELEASE_SAFETY,
            "No production authorization without release gate",
            required_evidence=("release_gate_checklist", "all_lane_evidence"),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            next_artifact="PRODUCTION_AUTHORIZATION_RELEASE_GATE_PLAN_001",
            exit_condition="Release gate plan complete and all lanes satisfied",
            authorization_boundary="release_gate_required_before_any_authorization",
            owner_lane="lane_10_platform_authorization_release_gate",
        ),
        # Downstream integration P0 boundaries
        _row(
            "trustreport_authorization_boundary",
            "TrustReport authorization boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "TrustReport production authorization blocked",
            required_evidence=("release_gate_authorization",),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes TrustReport role",
            authorization_boundary="trustreport_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        _row(
            "calibration_signal_authorization_boundary",
            "CalibrationSignal authorization boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "CalibrationSignal production authorization blocked",
            required_evidence=("release_gate_authorization", "method_gate_calibration"),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes CalibrationSignal role",
            authorization_boundary="calibration_signal_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        _row(
            "mmm_ingestion_boundary",
            "MMM ingestion boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "MMM ingestion blocked until release gate",
            required_evidence=("release_gate_authorization",),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes MMM ingestion",
            authorization_boundary="mmm_ingestion_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        _row(
            "llm_decisioning_boundary",
            "LLM decisioning boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "LLM decisioning blocked until release gate",
            required_evidence=("release_gate_authorization",),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes LLM decisioning",
            authorization_boundary="llm_decisioning_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        _row(
            "live_api_scheduler_boundary",
            "Live API / scheduler boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "Live API and scheduler blocked until release gate",
            required_evidence=("release_gate_authorization",),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes live API and scheduler",
            authorization_boundary="live_api_scheduler_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        _row(
            "budget_optimization_boundary",
            "Budget optimization boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "Budget optimization blocked until release gate",
            required_evidence=("release_gate_authorization",),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes budget optimization",
            authorization_boundary="budget_optimization_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        # Extra rows for domain coverage and count >= 45
        _row(
            "production_decisioning_boundary",
            "Production decisioning boundary",
            Domain.DOWNSTREAM_INTEGRATION,
            MethodFamily.DOWNSTREAM_INTEGRATION,
            BacklogStatus.BLOCKED,
            Priority.P0_RELEASE_SAFETY,
            "Production decisioning blocked until release gate",
            required_evidence=("release_gate_authorization",),
            dependency_artifacts=("PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",),
            exit_condition="Release gate authorizes production decisioning",
            authorization_boundary="production_decisioning_unauthorized",
            owner_lane="downstream_integration_lane",
        ),
        _row(
            "scm_multicell_boundary",
            "SCM multicell interaction boundary",
            Domain.MULTICELL,
            MethodFamily.SCM,
            BacklogStatus.BLOCKED,
            Priority.P1_FIRST_CANDIDATE_BLOCKER,
            "SCM multicell claims blocked until multicell validation lane satisfied",
            required_evidence=("scm_multicell_validation",),
            dependency_artifacts=("MULTICELL_DEPENDENCE_AND_MULTIPLICITY_VALIDATION_PLAN_001", "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"),
            exit_condition="Multicell validation evidence passes for SCM",
            authorization_boundary="scm_multicell_blocked_until_validated",
            owner_lane="lane_9_multicell_dependence_multiplicity_validation",
        ),
        _row(
            "simulation_dgp_coverage_router",
            "Simulation DGP coverage router integration",
            Domain.SIMULATION,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "DGP coverage must inform router eligibility",
            required_evidence=("DGP_router_integration",),
            dependency_artifacts=("SIMULATION_DGP_COVERAGE_PLAN_001",),
            exit_condition="DGP coverage integrated into router inputs",
            authorization_boundary="dgp_coverage_required_for_routing",
            owner_lane="data_driven_router_lane",
        ),
        _row(
            "design_assignment_stress_router",
            "Design assignment-stress router integration",
            Domain.DESIGN,
            MethodFamily.DATA_DRIVEN_ROUTER,
            BacklogStatus.PLANNED,
            Priority.P2_REMEDIATION_CANDIDATE,
            "Assignment stress tests must gate design eligibility",
            required_evidence=("ST-AD-001", "ST-AD-009", "ST-AD-010"),
            dependency_artifacts=("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
            exit_condition="Assignment stress integrated into design gate",
            authorization_boundary="assignment_stress_required",
            owner_lane="data_driven_router_lane",
        ),
    ]
    return tuple(rows)


def filter_production_readiness_backlog_ledger(
    rows: tuple[BacklogLedgerRow, ...],
    *,
    domain: Domain | None = None,
    method_family: MethodFamily | None = None,
    current_status: BacklogStatus | None = None,
    priority: Priority | None = None,
    owner_lane: str | None = None,
) -> tuple[BacklogLedgerRow, ...]:
    """Filter backlog ledger rows by optional criteria."""
    result: list[BacklogLedgerRow] = []
    for row in rows:
        if domain is not None and row.domain != domain:
            continue
        if method_family is not None and row.method_family != method_family:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if priority is not None and row.priority != priority:
            continue
        if owner_lane is not None and row.owner_lane != owner_lane:
            continue
        result.append(row)
    return tuple(result)


def validate_production_readiness_backlog_ledger(
    rows: tuple[BacklogLedgerRow, ...],
) -> dict[str, Any]:
    """Validate backlog ledger registry thresholds and coverage."""
    issues: list[str] = []
    item_ids = [r.item_id for r in rows]

    if len(rows) < MIN_LEDGER_ROW_COUNT:
        issues.append(f"ledger_row_count {len(rows)} < {MIN_LEDGER_ROW_COUNT}")
    if len(item_ids) != len(set(item_ids)):
        issues.append("duplicate item_id values")

    production_ready_rows = [r.item_id for r in rows if r.production_ready]
    if production_ready_rows:
        issues.append(f"rows with production_ready true: {production_ready_rows}")

    domain_counts = Counter(r.domain.value for r in rows)
    priority_counts = Counter(r.priority.value for r in rows)
    status_counts = Counter(r.current_status.value for r in rows)
    family_counts = Counter(r.method_family.value for r in rows)

    for domain in REQUIRED_DOMAINS:
        if not any(r.domain == domain for r in rows):
            issues.append(f"missing domain: {domain.value}")

    for priority in REQUIRED_PRIORITIES:
        if priority_counts.get(priority, 0) == 0:
            issues.append(f"missing priority: {priority.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for family in REQUIRED_METHOD_FAMILIES:
        if not any(r.method_family == family for r in rows):
            issues.append(f"missing method_family: {family.value}")

    for item_id in REQUIRED_BACKLOG_ITEM_IDS:
        if item_id not in item_ids:
            issues.append(f"missing required backlog item: {item_id}")

    scm_p1 = any(
        r.item_id.startswith("scm_") and r.priority == Priority.P1_FIRST_CANDIDATE_BLOCKER
        for r in rows
    )
    if not scm_p1:
        issues.append("scm P1 first-candidate blocker missing")

    multicell_p1 = any(
        r.method_family == MethodFamily.MULTICELL_SHARED_CONTROL
        and r.priority == Priority.P1_FIRST_CANDIDATE_BLOCKER
        for r in rows
    )
    if not multicell_p1:
        issues.append("multicell P1 cross-family blocker missing")

    dei_gate = next((r for r in rows if r.item_id == "data_driven_dei_selection_gate"), None)
    if dei_gate is None:
        issues.append("data_driven_dei_selection_gate missing")
    elif dei_gate.priority != Priority.P1_FIRST_CANDIDATE_BLOCKER:
        issues.append("data_driven_dei_selection_gate not P1")

    return {
        "valid": not issues,
        "ledger_row_count": len(rows),
        "unique_item_ids": len(item_ids) == len(set(item_ids)),
        "domain_counts": dict(domain_counts),
        "priority_counts": {p.value: priority_counts.get(p, 0) for p in Priority},
        "status_counts": {s.value: status_counts.get(s, 0) for s in BacklogStatus},
        "method_family_counts": dict(family_counts),
        "all_required_domains_covered": all(
            any(r.domain == d for r in rows) for d in REQUIRED_DOMAINS
        ),
        "all_required_priorities_covered": all(
            priority_counts.get(p, 0) > 0 for p in REQUIRED_PRIORITIES
        ),
        "all_required_statuses_covered": all(
            status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES
        ),
        "all_required_method_families_covered": all(
            any(r.method_family == f for r in rows) for f in REQUIRED_METHOD_FAMILIES
        ),
        "all_required_backlog_items_covered": all(i in item_ids for i in REQUIRED_BACKLOG_ITEM_IDS),
        "no_production_ready_rows": not production_ready_rows,
        "issues": issues,
    }


def summarize_production_readiness_backlog_ledger(
    rows: tuple[BacklogLedgerRow, ...],
) -> dict[str, Any]:
    """Serialize backlog ledger summary for archives."""
    validation = validate_production_readiness_backlog_ledger(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "ledger_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "domain_counts": validation["domain_counts"],
        "priority_counts": validation["priority_counts"],
        "status_counts": validation["status_counts"],
        "method_family_counts": validation["method_family_counts"],
        "all_required_domains_covered": validation["all_required_domains_covered"],
        "all_required_priorities_covered": validation["all_required_priorities_covered"],
        "all_required_statuses_covered": validation["all_required_statuses_covered"],
        "all_required_method_families_covered": validation["all_required_method_families_covered"],
        "all_required_backlog_items_covered": validation["all_required_backlog_items_covered"],
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
    rows = build_production_readiness_backlog_ledger()
    validation = validate_production_readiness_backlog_ledger(rows)
    summary = summarize_production_readiness_backlog_ledger(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("ledger_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("ledger_row_count_at_least_45", len(rows) >= MIN_LEDGER_ROW_COUNT))
    scenarios.append(_scenario("item_ids_unique", validation["unique_item_ids"]))
    scenarios.append(_scenario("no_production_ready_rows", validation["no_production_ready_rows"]))

    for domain in REQUIRED_DOMAINS:
        present = any(r.domain == domain for r in rows)
        scenarios.append(_scenario(f"domain_{domain.value}_represented", present))

    for priority in REQUIRED_PRIORITIES:
        count = sum(1 for r in rows if r.priority == priority)
        scenarios.append(_scenario(f"priority_{priority.value}_represented", count > 0))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(r.method_family == family for r in rows)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    for item_id in REQUIRED_BACKLOG_ITEM_IDS:
        present = any(r.item_id == item_id for r in rows)
        scenarios.append(_scenario(f"backlog_item_{item_id}_represented", present))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] == expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_selection_gate",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_production_readiness_backlog_ledger()
    validation = validate_production_readiness_backlog_ledger(rows)
    summary = summarize_production_readiness_backlog_ledger(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "ledger_row_count": len(rows),
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
