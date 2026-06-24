"""MULTICELL_MAX_T_RESEARCH_SCOUT_001 validation harness."""

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

_ARTIFACT_ID = "MULTICELL_MAX_T_RESEARCH_SCOUT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "multicell_max_t_research_scout_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/MULTICELL_MAX_T_RESEARCH_SCOUT_001_summary.json"

RECOMMENDED_NEXT_ARTIFACTS = (
    "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
    "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",
    "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",
)

MIN_SCOUT_ROW_COUNT = 50

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

_SCOUT_FLAGS = {
    "multicell_shared_control_is_cross_cutting_blocker": True,
    "naive_per_cell_p_values_blocked": True,
    "pooled_global_inference_blocked": True,
    "max_t_stepdown_research_candidate_only": True,
    "shared_control_dependence_requires_handling": True,
    "winner_selection_risk_identified": True,
    "multiple_kpi_horizon_risk_identified": True,
    "estimator_specific_promotion_gates_must_wait": True,
    "future_simulation_required": True,
    "future_adapter_required": True,
    "future_null_calibration_required": True,
    "downstream_work_paused": True,
}


class MultiplicityPath(str, Enum):
    SINGLE_STEP_MAX_T = "single_step_max_t"
    WESTFALL_YOUNG_MAX_T = "westfall_young_max_t"
    STEPDOWN_MAX_T = "stepdown_max_t"
    MIN_P_ADJUSTED = "min_p_adjusted"
    BONFERRONI_HOLM = "bonferroni_holm"
    SHARED_CONTROL_COVARIANCE = "shared_control_covariance"
    CELL_WISE_PLACEBO = "cell_wise_placebo"
    TREATED_SET_PLACEBO = "treated_set_placebo"
    LEAVE_ONE_TREATED_OUT = "leave_one_treated_out"
    PER_CELL_MARGINAL = "per_cell_marginal"
    POOLED_GLOBAL = "pooled_global"
    WINNER_SELECTION = "winner_selection"
    MULTIPLE_KPI_HORIZON = "multiple_kpi_horizon"
    SCM_MULTICELL = "scm_multicell"
    AUGSYNTH_MULTICELL = "augsynth_multicell"
    DID_MULTICELL = "did_multicell"
    TBRRIDGE_MULTICELL = "tbrridge_multicell"
    SYNTHETIC_DID_MULTICELL = "synthetic_did_multicell"


class MethodFamily(str, Enum):
    SCM = "scm"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    DID = "did"
    SYNTHETIC_DID = "synthetic_did"
    TBRRIDGE = "tbrridge"
    MULTICELL = "multicell"
    ALL = "all"


class ScoutStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BASELINE_CONTROL_ONLY = "baseline_control_only"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    REMEDIATION_REQUIRED = "remediation_required"


REQUIRED_PATHS = frozenset(MultiplicityPath)
REQUIRED_STATUSES = frozenset(ScoutStatus)
REQUIRED_METHOD_FAMILIES = frozenset({
    MethodFamily.SCM,
    MethodFamily.AUGSYNTH_CVXPY,
    MethodFamily.DID,
    MethodFamily.SYNTHETIC_DID,
    MethodFamily.TBRRIDGE,
})


@dataclass(frozen=True)
class MulticellResearchScoutRow:
    scout_id: str
    name: str
    method_family: MethodFamily
    multiplicity_path: MultiplicityPath
    dependence_issue: str
    current_status: ScoutStatus
    required_design_conditions: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    failure_registry_links: tuple[str, ...]
    candidate_future_artifacts: tuple[str, ...]
    promotion_evidence_required: tuple[str, ...]
    blocked_failure_modes: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    notes: str


def _row(
    scout_id: str,
    name: str,
    method_family: MethodFamily,
    multiplicity_path: MultiplicityPath,
    dependence_issue: str,
    current_status: ScoutStatus,
    notes: str,
    *,
    required_design_conditions: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    failure_registry_links: tuple[str, ...],
    candidate_future_artifacts: tuple[str, ...],
    promotion_evidence_required: tuple[str, ...],
    blocked_failure_modes: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
) -> MulticellResearchScoutRow:
    return MulticellResearchScoutRow(
        scout_id=scout_id,
        name=name,
        method_family=method_family,
        multiplicity_path=multiplicity_path,
        dependence_issue=dependence_issue,
        current_status=current_status,
        required_design_conditions=required_design_conditions,
        required_diagnostics=required_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        failure_registry_links=failure_registry_links,
        candidate_future_artifacts=candidate_future_artifacts,
        promotion_evidence_required=promotion_evidence_required,
        blocked_failure_modes=blocked_failure_modes,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        notes=notes,
    )


_ALL_M = (MethodFamily.ALL,)
_PROMO = ("null_calibration", "dgp_coverage", "failure_registry_consult")
_FORBID_PROD = ("production_p_value", "causal_ci", "trustreport")


def build_multicell_max_t_research_scout() -> tuple[MulticellResearchScoutRow, ...]:
    """Return metadata-only multicell max-T research scout rows."""
    return (
        # Max-T / stepdown / baseline multiplicity
        _row(
            "MC-SCT-001", "single_step_max_t_research", MethodFamily.MULTICELL,
            MultiplicityPath.SINGLE_STEP_MAX_T, "correlated_cell_test_statistics",
            ScoutStatus.RESEARCH_ONLY,
            "Single-step max-T is research candidate only; not production FWER.",
            required_design_conditions=("cell_structure_documented", "test_statistic_defined"),
            required_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002", "DGP-INF-011"),
            failure_registry_links=("FM-INF-009",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-010",),
            allowed_current_use=("labeled_research_calibration",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-002", "westfall_young_max_t_simulation", MethodFamily.MULTICELL,
            MultiplicityPath.WESTFALL_YOUNG_MAX_T, "exchangeability_under_null",
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Westfall-Young max-T requires simulation DGP with shared-control dependence.",
            required_design_conditions=("valid_null_exchangeability",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002", "DGP-MC-007"),
            failure_registry_links=("FM-INF-009", "FM-DA-009"),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("simulation_fwer_calibration",) + _PROMO,
            blocked_failure_modes=("FM-CP-002",),
            allowed_current_use=("research_simulation_harness",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-003", "stepdown_max_t_null_calibration", MethodFamily.MULTICELL,
            MultiplicityPath.STEPDOWN_MAX_T, "stepdown_dependence_on_ordering",
            ScoutStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Stepdown max-T requires null calibration before any promotion.",
            required_design_conditions=("stepdown_ordering_documented",),
            required_diagnostics=("OPD-MC-004", "OPD-IR-009"),
            required_dgp_coverage=("DGP-INF-012",),
            failure_registry_links=("FM-INF-010",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("null_fwer_calibration",) + _PROMO,
            blocked_failure_modes=("FM-CP-001",),
            allowed_current_use=("research_null_monitor",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-004", "min_p_adjusted_research", MethodFamily.MULTICELL,
            MultiplicityPath.MIN_P_ADJUSTED, "adjusted_p_not_production_without_calibration",
            ScoutStatus.RESEARCH_ONLY,
            "Min-P/adjusted p-value paths are research-only.",
            required_design_conditions=("multiplicity_adjustment_documented",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-INF-011",),
            failure_registry_links=("FM-INF-009",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DB-009",),
            allowed_current_use=("diagnostic_rank_monitor",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-005", "bonferroni_holm_baseline_control", MethodFamily.MULTICELL,
            MultiplicityPath.BONFERRONI_HOLM, "conservative_baseline_under_dependence",
            ScoutStatus.BASELINE_CONTROL_ONLY,
            "Bonferroni/Holm are baseline controls only, not promotion targets.",
            required_design_conditions=("cell_count_known",),
            required_diagnostics=("OPD-MC-002",),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-INF-009",),
            candidate_future_artifacts=(),
            promotion_evidence_required=("baseline_fwer_upper_bound",),
            blocked_failure_modes=(),
            allowed_current_use=("conservative_sensitivity_bound",),
            forbidden_current_use=("production_p_value", "winner_selection"),
        ),
        _row(
            "MC-SCT-006", "closed_testing_research", MethodFamily.MULTICELL,
            MultiplicityPath.STEPDOWN_MAX_T, "closed_testing_family_definition",
            ScoutStatus.RESEARCH_ONLY,
            "Closed testing families under multicell require explicit hypothesis family.",
            required_design_conditions=("hypothesis_family_pre_specified",),
            required_diagnostics=("OPD-MC-005",),
            required_dgp_coverage=("DGP-MC-005",),
            failure_registry_links=("FM-DA-010",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-010",),
            allowed_current_use=("research_hypothesis_family_exploration",),
            forbidden_current_use=_FORBID_PROD,
        ),
        # Shared-control dependence
        _row(
            "MC-SCT-010", "shared_control_covariance_handling", MethodFamily.MULTICELL,
            MultiplicityPath.SHARED_CONTROL_COVARIANCE, "shared_control_correlation",
            ScoutStatus.REMEDIATION_REQUIRED,
            "Shared-control covariance/dependence must be modeled or calibrated.",
            required_design_conditions=("dependence_model_specified",),
            required_diagnostics=("OPD-MC-001", "OPD-AD-008"),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-DA-009",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("dependence_calibration",) + _PROMO,
            blocked_failure_modes=("FM-DA-009",),
            allowed_current_use=("dependence_diagnostic",),
            forbidden_current_use=("independent_cell_assumption",),
        ),
        _row(
            "MC-SCT-011", "shared_control_ignored_blocked", MethodFamily.MULTICELL,
            MultiplicityPath.SHARED_CONTROL_COVARIANCE, "dependence_ignored",
            ScoutStatus.BLOCKED,
            "Ignoring shared-control dependence blocks multicell inference promotion.",
            required_design_conditions=("dependence_acknowledged",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-DA-009",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-009", "FM-INF-011"),
            allowed_current_use=(),
            forbidden_current_use=_FORBID_PROD + ("pooled_inference",),
        ),
        _row(
            "MC-SCT-012", "cross_cell_contamination_blocked", MethodFamily.MULTICELL,
            MultiplicityPath.SHARED_CONTROL_COVARIANCE, "cross_cell_contamination",
            ScoutStatus.BLOCKED,
            "Cross-cell contamination invalidates independent multiplicity adjustments.",
            required_design_conditions=("cell_isolation_documented",),
            required_diagnostics=("OPD-TE-005", "OPD-MC-001"),
            required_dgp_coverage=("DGP-TE-005",),
            failure_registry_links=("FM-TE-005",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-TE-005",),
            allowed_current_use=("contamination_diagnostic",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-013", "independent_cell_assumption_blocked", MethodFamily.MULTICELL,
            MultiplicityPath.SHARED_CONTROL_COVARIANCE, "invalid_independence_assumption",
            ScoutStatus.BLOCKED,
            "Independent-cell assumption blocked when shared controls present.",
            required_design_conditions=("shared_control_declared",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-DA-009",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-009",),
            allowed_current_use=(),
            forbidden_current_use=("independent_cell_inference",),
        ),
        # Placebo paths
        _row(
            "MC-SCT-020", "cell_wise_placebo_dependence_warning", MethodFamily.SCM,
            MultiplicityPath.CELL_WISE_PLACEBO, "cell_placebo_correlation",
            ScoutStatus.DIAGNOSTIC_ONLY,
            "Cell-wise placebo rank with dependence warning is diagnostic-only.",
            required_design_conditions=("placebo_support_per_cell",),
            required_diagnostics=("OPD-IR-002", "OPD-MC-001"),
            required_dgp_coverage=("DGP-INF-003", "DGP-MC-002"),
            failure_registry_links=("FM-INF-001", "FM-DA-009"),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-001",),
            allowed_current_use=("null_monitor_per_cell",),
            forbidden_current_use=("production_p_value",),
        ),
        _row(
            "MC-SCT-021", "treated_set_placebo_multicell", MethodFamily.SCM,
            MultiplicityPath.TREATED_SET_PLACEBO, "treated_set_overlap_multicell",
            ScoutStatus.RESEARCH_ONLY,
            "Treated-set placebo under multicell is research-only.",
            required_design_conditions=("treated_set_size_preserved",),
            required_diagnostics=("OPD-MC-002",),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-INF-001",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-008",),
            allowed_current_use=("research_placebo_enumeration",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-022", "leave_one_treated_out_multicell", MethodFamily.SCM,
            MultiplicityPath.LEAVE_ONE_TREATED_OUT, "leave_one_treated_geometry",
            ScoutStatus.RESEARCH_ONLY,
            "Leave-one-treated-out under multicell is research-only.",
            required_design_conditions=("leave_one_feasible",),
            required_diagnostics=("OPD-MC-002",),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-INF-001",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-007",),
            allowed_current_use=("research_sensitivity",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-023", "placebo_rank_dependence_diagnostic", MethodFamily.MULTICELL,
            MultiplicityPath.CELL_WISE_PLACEBO, "rank_correlation_across_cells",
            ScoutStatus.DIAGNOSTIC_ONLY,
            "Placebo ranks correlated across cells; diagnostic null-monitor only.",
            required_design_conditions=("governed_placebo_semantics",),
            required_diagnostics=("OPD-IR-002", "OPD-MC-004"),
            required_dgp_coverage=("DGP-INF-003",),
            failure_registry_links=("FM-INF-001", "FM-INF-009"),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-001",),
            allowed_current_use=("diagnostic_rank",),
            forbidden_current_use=("family_level_p_value",),
        ),
        _row(
            "MC-SCT-024", "multicell_randomization_research", MethodFamily.DID,
            MultiplicityPath.PER_CELL_MARGINAL, "randomization_with_multiplicity",
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Multicell randomization requires simulation before promotion.",
            required_design_conditions=("known_assignment_per_cell",),
            required_diagnostics=("OPD-AD-001", "OPD-MC-002"),
            required_dgp_coverage=("DGP-INF-001", "DGP-MC-002"),
            failure_registry_links=("FM-DA-001", "FM-INF-009"),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("simulation_fwer_calibration",) + _PROMO,
            blocked_failure_modes=("FM-DA-009",),
            allowed_current_use=("research_randomization",),
            forbidden_current_use=_FORBID_PROD,
        ),
        # Per-cell / pooled / global
        _row(
            "MC-SCT-030", "per_cell_marginal_diagnostic", MethodFamily.MULTICELL,
            MultiplicityPath.PER_CELL_MARGINAL, "marginal_without_multiplicity",
            ScoutStatus.DIAGNOSTIC_ONLY,
            "Per-cell marginal inference is diagnostic-only without multiplicity control.",
            required_design_conditions=("per_cell_estimand_labeled",),
            required_diagnostics=("OPD-MC-002",),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-INF-009",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-010",),
            allowed_current_use=("per_cell_diagnostic_readout",),
            forbidden_current_use=("family_level_claim",),
        ),
        _row(
            "MC-SCT-031", "naive_per_cell_pvalue_blocked", MethodFamily.MULTICELL,
            MultiplicityPath.PER_CELL_MARGINAL, "naive_multiplicity",
            ScoutStatus.BLOCKED,
            "Naive per-cell p-values are not production-valid family-level evidence.",
            required_design_conditions=("multiplicity_control_required",),
            required_diagnostics=("OPD-MC-004", "OPD-IR-009"),
            required_dgp_coverage=("DGP-INF-011",),
            failure_registry_links=("FM-INF-009", "FM-DA-010"),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DB-009", "FM-DA-010"),
            allowed_current_use=(),
            forbidden_current_use=("production_p_value", "winner_selection"),
        ),
        _row(
            "MC-SCT-032", "pooled_global_inference_blocked", MethodFamily.MULTICELL,
            MultiplicityPath.POOLED_GLOBAL, "pooled_estimand_ambiguity",
            ScoutStatus.BLOCKED,
            "Pooled/global multicell inference blocked until future artifact validates.",
            required_design_conditions=("global_estimand_pre_specified",),
            required_diagnostics=("OPD-MC-005", "OPD-ER-006"),
            required_dgp_coverage=("DGP-MC-005", "DGP-ES-009"),
            failure_registry_links=("FM-ES-007", "FM-DA-010"),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("global_estimand_validation",) + _PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=("labeled_sensitivity_only",),
            forbidden_current_use=("production_global_claim", "trustreport"),
        ),
        _row(
            "MC-SCT-033", "global_estimand_overclaim_blocked", MethodFamily.TBRRIDGE,
            MultiplicityPath.POOLED_GLOBAL, "aggregate_geometry_mismatch",
            ScoutStatus.BLOCKED,
            "Global TBRRidge multicell overclaim remains blocked.",
            required_design_conditions=("cell_structure_explicit",),
            required_diagnostics=("OPD-ER-006", "OPD-MC-005"),
            required_dgp_coverage=("DGP-ES-009",),
            failure_registry_links=("FM-ES-007",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=(),
            forbidden_current_use=("aggregate_production_inference",),
        ),
        # Winner / KPI / horizon
        _row(
            "MC-SCT-040", "winner_selection_risk", MethodFamily.MULTICELL,
            MultiplicityPath.WINNER_SELECTION, "best_cell_selection",
            ScoutStatus.BLOCKED,
            "Winner-selection/best-cell selection risk must be explicitly controlled.",
            required_design_conditions=("pre_registered_primary_cell",),
            required_diagnostics=("OPD-MC-003",),
            required_dgp_coverage=("DGP-MC-004",),
            failure_registry_links=("FM-DA-010",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("multiplicity_adjustment",) + _PROMO,
            blocked_failure_modes=("FM-DA-010",),
            allowed_current_use=("exploratory_ranking_labeled",),
            forbidden_current_use=("winner_production_decision",),
        ),
        _row(
            "MC-SCT-041", "multiple_kpi_horizon_risk", MethodFamily.MULTICELL,
            MultiplicityPath.MULTIPLE_KPI_HORIZON, "multiple_testing_across_kpis",
            ScoutStatus.BLOCKED,
            "Multiple KPI/horizon risks require explicit multiplicity control.",
            required_design_conditions=("primary_kpi_pre_registered",),
            required_diagnostics=("OPD-OM-009", "OPD-MC-004"),
            required_dgp_coverage=("DGP-OM-009",),
            failure_registry_links=("FM-INF-009",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("kpi_family_definition",) + _PROMO,
            blocked_failure_modes=("FM-DA-010",),
            allowed_current_use=("secondary_kpi_sensitivity",),
            forbidden_current_use=("unadjusted_multi_kpi_promotion",),
        ),
        _row(
            "MC-SCT-042", "best_cell_post_hoc_blocked", MethodFamily.MULTICELL,
            MultiplicityPath.WINNER_SELECTION, "post_hoc_cell_selection",
            ScoutStatus.BLOCKED,
            "Post-hoc best-cell selection without multiplicity is blocked.",
            required_design_conditions=("no_post_hoc_winner",),
            required_diagnostics=("OPD-MC-003",),
            required_dgp_coverage=("DGP-MC-004",),
            failure_registry_links=("FM-DA-010",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-010", "FM-DB-005"),
            allowed_current_use=(),
            forbidden_current_use=("production_winner_selection",),
        ),
        _row(
            "MC-SCT-043", "fwer_calibration_required", MethodFamily.MULTICELL,
            MultiplicityPath.SINGLE_STEP_MAX_T, "fwer_under_dependence",
            ScoutStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "FWER calibration under dependence required before max-T promotion.",
            required_design_conditions=("null_hypothesis_family_defined",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-INF-011", "DGP-CP-001"),
            failure_registry_links=("FM-CP-001", "FM-INF-009"),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("null_fwer_calibration",),
            blocked_failure_modes=("FM-CP-001",),
            allowed_current_use=("calibration_harness",),
            forbidden_current_use=_FORBID_PROD,
        ),
        # SCM multicell
        _row(
            "MC-SCT-050", "scm_multicell_per_cell_placebo", MethodFamily.SCM,
            MultiplicityPath.SCM_MULTICELL, "scm_shared_control",
            ScoutStatus.DIAGNOSTIC_ONLY,
            "SCM multicell per-cell placebo is diagnostic-only.",
            required_design_conditions=("donor_support_per_cell",),
            required_diagnostics=("OPD-DS-006", "OPD-MC-001"),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-ES-002", "FM-DA-009"),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-001",),
            allowed_current_use=("scm_diagnostic_per_cell",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-051", "scm_multicell_pooled_blocked", MethodFamily.SCM,
            MultiplicityPath.SCM_MULTICELL, "scm_pooled_overclaim",
            ScoutStatus.BLOCKED,
            "SCM pooled multicell inference blocked.",
            required_design_conditions=("per_cell_estimand_preferred",),
            required_diagnostics=("OPD-MC-005",),
            required_dgp_coverage=("DGP-MC-005",),
            failure_registry_links=("FM-ES-007",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=(),
            forbidden_current_use=("pooled_scm_production",),
        ),
        _row(
            "MC-SCT-052", "scm_multicell_max_t_adapter", MethodFamily.SCM,
            MultiplicityPath.SCM_MULTICELL, "scm_statistic_adapter_multiplicity",
            ScoutStatus.CANDIDATE_AFTER_ADAPTER,
            "SCM multicell max-T requires studentized adapter before promotion.",
            required_design_conditions=("studentized_adapter_contract",),
            required_diagnostics=("OPD-IR-003", "OPD-MC-004"),
            required_dgp_coverage=("DGP-INF-004",),
            failure_registry_links=("FM-INF-002", "FM-CP-006"),
            candidate_future_artifacts=(
                "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
                "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",
            ),
            promotion_evidence_required=("adapter_contract", "null_calibration"),
            blocked_failure_modes=("FM-INF-002",),
            allowed_current_use=("adapter_research",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-053", "scm_multicell_promotion_gate_wait", MethodFamily.SCM,
            MultiplicityPath.SCM_MULTICELL, "estimator_promotion_before_scout",
            ScoutStatus.REMEDIATION_REQUIRED,
            "SCM promotion gates must wait for this scout outcome.",
            required_design_conditions=("scout_consumed",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-CP-004",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-CP-007",),
            allowed_current_use=("diagnostic_point",),
            forbidden_current_use=("premature_promotion",),
        ),
        # AugSynth multicell
        _row(
            "MC-SCT-060", "augsynth_multicell_point_diagnostic", MethodFamily.AUGSYNTH_CVXPY,
            MultiplicityPath.AUGSYNTH_MULTICELL, "augsynth_multicell_inference_gap",
            ScoutStatus.DIAGNOSTIC_ONLY,
            "AugSynth multicell point estimates diagnostic-only.",
            required_design_conditions=("augmentation_stable_per_cell",),
            required_diagnostics=("OPD-DS-007", "OPD-MC-002"),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-ES-004",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-003",),
            allowed_current_use=("point_diagnostic",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-061", "augsynth_multicell_jk_blocked", MethodFamily.AUGSYNTH_CVXPY,
            MultiplicityPath.AUGSYNTH_MULTICELL, "jackknife_multicell",
            ScoutStatus.BLOCKED,
            "AugSynth jackknife multicell paths blocked.",
            required_design_conditions=("inference_path_valid",),
            required_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007",),
            failure_registry_links=("FM-INF-005",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-005",),
            allowed_current_use=(),
            forbidden_current_use=("jackknife_ci",),
        ),
        _row(
            "MC-SCT-062", "augsynth_multicell_adapter_candidate", MethodFamily.AUGSYNTH_CVXPY,
            MultiplicityPath.AUGSYNTH_MULTICELL, "adapter_required_multicell",
            ScoutStatus.CANDIDATE_AFTER_ADAPTER,
            "AugSynth multicell inference candidate after adapter contract.",
            required_design_conditions=("adapter_contract_met",),
            required_diagnostics=("OPD-IR-003",),
            required_dgp_coverage=("DGP-INF-004",),
            failure_registry_links=("FM-CP-006",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=("adapter_contract",) + _PROMO,
            blocked_failure_modes=("FM-INF-002",),
            allowed_current_use=("adapter_research",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-063", "augsynth_multicell_pooled_blocked", MethodFamily.AUGSYNTH_CVXPY,
            MultiplicityPath.POOLED_GLOBAL, "augsynth_pooled_multicell",
            ScoutStatus.BLOCKED,
            "AugSynth pooled multicell inference blocked.",
            required_design_conditions=("per_cell_preferred",),
            required_diagnostics=("OPD-MC-005",),
            required_dgp_coverage=("DGP-MC-005",),
            failure_registry_links=("FM-ES-007",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=(),
            forbidden_current_use=("pooled_production",),
        ),
        # DID multicell
        _row(
            "MC-SCT-070", "did_multicell_per_cell_research", MethodFamily.DID,
            MultiplicityPath.DID_MULTICELL, "did_cell_heterogeneity",
            ScoutStatus.RESEARCH_ONLY,
            "DID multicell per-cell paths are research-only pending multiplicity.",
            required_design_conditions=("parallel_trends_per_cell",),
            required_diagnostics=("OPD-PF-003", "OPD-MC-002"),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-ES-005", "FM-INF-009"),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-PF-003",),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-071", "did_multicell_pooled_blocked", MethodFamily.DID,
            MultiplicityPath.DID_MULTICELL, "did_pooled_multicell",
            ScoutStatus.BLOCKED,
            "DID pooled multicell inference blocked.",
            required_design_conditions=("stratum_specific_estimands",),
            required_diagnostics=("OPD-MC-005",),
            required_dgp_coverage=("DGP-MC-005",),
            failure_registry_links=("FM-DA-006",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=(),
            forbidden_current_use=("pooled_did_production",),
        ),
        _row(
            "MC-SCT-072", "did_multicell_cluster_multiplicity", MethodFamily.DID,
            MultiplicityPath.DID_MULTICELL, "few_clusters_multicell",
            ScoutStatus.BLOCKED,
            "DID multicell with few clusters blocked for promotion.",
            required_design_conditions=("adequate_cluster_count",),
            required_diagnostics=("OPD-IR-006",),
            required_dgp_coverage=("DGP-INF-008",),
            failure_registry_links=("FM-INF-006",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-006",),
            allowed_current_use=("cluster_diagnostic",),
            forbidden_current_use=("cluster_production_ci",),
        ),
        _row(
            "MC-SCT-073", "did_multicell_stepdown_candidate", MethodFamily.DID,
            MultiplicityPath.STEPDOWN_MAX_T, "did_stepdown_multicell",
            ScoutStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "DID multicell stepdown candidate after null calibration.",
            required_design_conditions=("multiplicity_family_defined",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-INF-012",),
            failure_registry_links=("FM-INF-010",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("null_calibration",),
            blocked_failure_modes=("FM-CP-001",),
            allowed_current_use=("research_stepdown",),
            forbidden_current_use=_FORBID_PROD,
        ),
        # TBRRidge multicell
        _row(
            "MC-SCT-080", "tbrridge_multicell_diagnostic", MethodFamily.TBRRIDGE,
            MultiplicityPath.TBRRIDGE_MULTICELL, "tbrridge_per_cell_only",
            ScoutStatus.DIAGNOSTIC_ONLY,
            "TBRRidge multicell diagnostic per-cell only.",
            required_design_conditions=("per_cell_labeled",),
            required_diagnostics=("OPD-MC-002",),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-ES-006",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-011",),
            allowed_current_use=("diagnostic_point",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-081", "tbrridge_multicell_aggregate_blocked", MethodFamily.TBRRIDGE,
            MultiplicityPath.TBRRIDGE_MULTICELL, "tbrridge_aggregate_multicell",
            ScoutStatus.BLOCKED,
            "TBRRidge aggregate multicell paths blocked.",
            required_design_conditions=("no_aggregate_claim",),
            required_diagnostics=("OPD-ER-006",),
            required_dgp_coverage=("DGP-ES-009",),
            failure_registry_links=("FM-ES-007",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=(),
            forbidden_current_use=("aggregate_inference",),
        ),
        _row(
            "MC-SCT-082", "tbrridge_multicell_brb_blocked", MethodFamily.TBRRIDGE,
            MultiplicityPath.TBRRIDGE_MULTICELL, "brb_multicell_dependence",
            ScoutStatus.BLOCKED,
            "TBRRidge BRB multicell not production-valid.",
            required_design_conditions=("dependence_handled",),
            required_diagnostics=("OPD-MC-001", "OPD-IR-004"),
            required_dgp_coverage=("DGP-INF-006",),
            failure_registry_links=("FM-INF-004",),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-004",),
            allowed_current_use=("diagnostic_brb",),
            forbidden_current_use=("production_brb",),
        ),
        _row(
            "MC-SCT-083", "tbrridge_multicell_max_t_research", MethodFamily.TBRRIDGE,
            MultiplicityPath.SINGLE_STEP_MAX_T, "tbrridge_max_t_multicell",
            ScoutStatus.RESEARCH_ONLY,
            "TBRRidge multicell max-T research-only.",
            required_design_conditions=("multiplicity_research_complete",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-INF-011",),
            failure_registry_links=("FM-INF-009",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-011",),
            allowed_current_use=("research_max_t",),
            forbidden_current_use=_FORBID_PROD,
        ),
        # Synthetic DID multicell
        _row(
            "MC-SCT-090", "synthetic_did_multicell_scout", MethodFamily.SYNTHETIC_DID,
            MultiplicityPath.SYNTHETIC_DID_MULTICELL, "sdid_multicell_research",
            ScoutStatus.RESEARCH_ONLY,
            "Synthetic DID multicell is research/scout candidate only.",
            required_design_conditions=("balance_stress_per_cell",),
            required_diagnostics=("OPD-MC-002",),
            required_dgp_coverage=("DGP-MC-003",),
            failure_registry_links=("FM-ES-009",),
            candidate_future_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-CP-005",),
            allowed_current_use=("scout_calibration",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-091", "synthetic_did_multicell_staggered", MethodFamily.SYNTHETIC_DID,
            MultiplicityPath.SYNTHETIC_DID_MULTICELL, "sdid_staggered_multicell",
            ScoutStatus.RESEARCH_ONLY,
            "Synthetic DID staggered multicell requires scout before promotion.",
            required_design_conditions=("staggered_estimand_clarity",),
            required_diagnostics=("OPD-TE-004",),
            required_dgp_coverage=("DGP-TE-004",),
            failure_registry_links=("FM-TE-004",),
            candidate_future_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-TE-004",),
            allowed_current_use=("research_scout",),
            forbidden_current_use=("production_inference",),
        ),
        _row(
            "MC-SCT-092", "synthetic_did_multicell_pooled_blocked", MethodFamily.SYNTHETIC_DID,
            MultiplicityPath.POOLED_GLOBAL, "sdid_pooled_multicell",
            ScoutStatus.BLOCKED,
            "Synthetic DID pooled multicell inference blocked.",
            required_design_conditions=("per_cell_estimand",),
            required_diagnostics=("OPD-MC-005",),
            required_dgp_coverage=("DGP-MC-005",),
            failure_registry_links=("FM-ES-007",),
            candidate_future_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-ES-007",),
            allowed_current_use=(),
            forbidden_current_use=("pooled_production",),
        ),
        # Cross-cutting governance
        _row(
            "MC-SCT-100", "multicell_cross_cutting_blocker", _ALL_M[0],
            MultiplicityPath.SHARED_CONTROL_COVARIANCE, "cross_cutting_dependence",
            ScoutStatus.REMEDIATION_REQUIRED,
            "Multicell/shared-control is a cross-cutting blocker for all families.",
            required_design_conditions=("dependence_acknowledged",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-DA-009", "FM-CP-004"),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DA-009",),
            allowed_current_use=("cross_family_diagnostic",),
            forbidden_current_use=("family_promotion_before_scout",),
        ),
        _row(
            "MC-SCT-101", "estimator_promotion_gates_must_wait", _ALL_M[0],
            MultiplicityPath.SCM_MULTICELL, "premature_estimator_promotion",
            ScoutStatus.BLOCKED,
            "Estimator-specific promotion gates must wait for scout outcome.",
            required_design_conditions=("scout_artifact_consumed",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-MC-007",),
            failure_registry_links=("FM-CP-007", "FM-CP-004"),
            candidate_future_artifacts=(
                "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
                "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",
            ),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-CP-007",),
            allowed_current_use=(),
            forbidden_current_use=("premature_trustreport", "production_promotion"),
        ),
        _row(
            "MC-SCT-102", "future_simulation_required_multicell", _ALL_M[0],
            MultiplicityPath.WESTFALL_YOUNG_MAX_T, "simulation_gap",
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Future simulation required for multicell multiplicity candidates.",
            required_design_conditions=("dgp_grid_available",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-CP-002", "DGP-MC-002"),
            failure_registry_links=("FM-CP-002",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("simulation_fwer",),
            blocked_failure_modes=("FM-CP-002",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-103", "future_null_calibration_required", _ALL_M[0],
            MultiplicityPath.STEPDOWN_MAX_T, "null_calibration_gap",
            ScoutStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Future null calibration required for stepdown/max-T promotion.",
            required_design_conditions=("null_harness_available",),
            required_diagnostics=("OPD-IR-009",),
            required_dgp_coverage=("DGP-CP-001",),
            failure_registry_links=("FM-CP-001",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=("null_calibration",),
            blocked_failure_modes=("FM-CP-001",),
            allowed_current_use=("null_calibration_research",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-104", "downstream_authorization_blocked", _ALL_M[0],
            MultiplicityPath.POOLED_GLOBAL, "downstream_boundary",
            ScoutStatus.BLOCKED,
            "No downstream production authorization from this scout.",
            required_design_conditions=("downstream_paused",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            failure_registry_links=("FM-DB-001", "FM-DB-009", "FM-DB-010"),
            candidate_future_artifacts=(),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-DB-005",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID_PROD + ("calibration_signal", "mmm", "scheduler"),
        ),
        _row(
            "MC-SCT-105", "holm_stepdown_baseline_combo", MethodFamily.MULTICELL,
            MultiplicityPath.BONFERRONI_HOLM, "holm_stepdown_sensitivity",
            ScoutStatus.BASELINE_CONTROL_ONLY,
            "Holm/stepdown combo usable as conservative baseline control only.",
            required_design_conditions=("hypothesis_count_known",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-INF-012",),
            failure_registry_links=("FM-INF-010",),
            candidate_future_artifacts=(),
            promotion_evidence_required=("baseline_bound",),
            blocked_failure_modes=(),
            allowed_current_use=("sensitivity_upper_bound",),
            forbidden_current_use=("production_promotion",),
        ),
        _row(
            "MC-SCT-106", "roman_holm_stepdown_research", MethodFamily.MULTICELL,
            MultiplicityPath.STEPDOWN_MAX_T, "stepdown_under_positive_dependence",
            ScoutStatus.RESEARCH_ONLY,
            "Romano-style stepdown under positive dependence remains research-only.",
            required_design_conditions=("dependence_structure_documented",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002",),
            failure_registry_links=("FM-INF-010",),
            candidate_future_artifacts=("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-INF-009",),
            allowed_current_use=("research_stepdown",),
            forbidden_current_use=_FORBID_PROD,
        ),
        _row(
            "MC-SCT-107", "donor_contamination_multicell_blocked", MethodFamily.SCM,
            MultiplicityPath.SHARED_CONTROL_COVARIANCE, "donor_contamination_multicell",
            ScoutStatus.BLOCKED,
            "Donor contamination across multicell units blocks valid multiplicity.",
            required_design_conditions=("donor_eligibility_per_cell",),
            required_diagnostics=("OPD-TE-006", "OPD-MC-001"),
            required_dgp_coverage=("DGP-TE-006",),
            failure_registry_links=("FM-TE-006",),
            candidate_future_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            promotion_evidence_required=_PROMO,
            blocked_failure_modes=("FM-TE-006",),
            allowed_current_use=("contamination_diagnostic",),
            forbidden_current_use=_FORBID_PROD,
        ),
    )


def filter_multicell_max_t_research_scout(
    rows: tuple[MulticellResearchScoutRow, ...],
    *,
    multiplicity_path: MultiplicityPath | None = None,
    current_status: ScoutStatus | None = None,
    method_family: MethodFamily | None = None,
) -> tuple[MulticellResearchScoutRow, ...]:
    """Filter scout rows by optional criteria."""
    result: list[MulticellResearchScoutRow] = []
    for row in rows:
        if multiplicity_path is not None and row.multiplicity_path != multiplicity_path:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if method_family is not None and row.method_family != method_family:
            continue
        result.append(row)
    return tuple(result)


def validate_multicell_max_t_research_scout(
    rows: tuple[MulticellResearchScoutRow, ...],
) -> dict[str, Any]:
    """Validate scout registry thresholds and coverage."""
    issues: list[str] = []
    scout_ids = [r.scout_id for r in rows]

    if len(rows) < MIN_SCOUT_ROW_COUNT:
        issues.append(f"scout_row_count {len(rows)} < {MIN_SCOUT_ROW_COUNT}")
    if len(scout_ids) != len(set(scout_ids)):
        issues.append("duplicate scout_id values")

    status_counts = Counter(r.current_status for r in rows)
    method_counts = Counter(r.method_family.value for r in rows)
    path_counts = Counter(r.multiplicity_path.value for r in rows)

    for path in REQUIRED_PATHS:
        if not any(r.multiplicity_path == path for r in rows):
            issues.append(f"missing multiplicity path: {path.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for family in REQUIRED_METHOD_FAMILIES:
        if not any(r.method_family == family for r in rows):
            issues.append(f"missing method family: {family.value}")

    blocked_naive = any(
        r.scout_id == "MC-SCT-031" and r.current_status == ScoutStatus.BLOCKED
        for r in rows
    )
    blocked_pooled = any(
        r.multiplicity_path == MultiplicityPath.POOLED_GLOBAL
        and r.current_status == ScoutStatus.BLOCKED
        for r in rows
    )
    if not blocked_naive:
        issues.append("naive per-cell p-value blocker missing")
    if not blocked_pooled:
        issues.append("pooled/global blocker missing")

    unlinked = [r.scout_id for r in rows if not r.failure_registry_links]
    if unlinked:
        issues.append(f"rows missing failure_registry_links: {unlinked}")

    return {
        "valid": not issues,
        "scout_row_count": len(rows),
        "unique_scout_ids": len(scout_ids) == len(set(scout_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ScoutStatus},
        "method_family_counts": dict(method_counts),
        "multiplicity_path_counts": dict(path_counts),
        "all_required_paths_covered": all(
            any(r.multiplicity_path == p for r in rows) for p in REQUIRED_PATHS
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "all_required_method_families_represented": all(
            any(r.method_family == f for r in rows) for f in REQUIRED_METHOD_FAMILIES
        ),
        "issues": issues,
    }


def summarize_multicell_max_t_research_scout(
    rows: tuple[MulticellResearchScoutRow, ...],
) -> dict[str, Any]:
    """Serialize multicell scout summary for archives."""
    validation = validate_multicell_max_t_research_scout(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "scout_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "method_family_counts": validation["method_family_counts"],
        "multiplicity_path_counts": validation["multiplicity_path_counts"],
        "all_required_paths_covered": validation["all_required_paths_covered"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_SCOUT_FLAGS,
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
    rows = build_multicell_max_t_research_scout()
    validation = validate_multicell_max_t_research_scout(rows)
    summary = summarize_multicell_max_t_research_scout(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("scout_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("scout_row_count_at_least_50", len(rows) >= MIN_SCOUT_ROW_COUNT))
    scenarios.append(_scenario("scout_ids_unique", validation["unique_scout_ids"]))

    for path in REQUIRED_PATHS:
        present = any(r.multiplicity_path == path for r in rows)
        scenarios.append(_scenario(f"multiplicity_path_{path.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(r.method_family == family for r in rows)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    for flag, expected in _SCOUT_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_scm_augsynth_inference_promotion_gate_audit_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_multicell_max_t_research_scout()
    validation = validate_multicell_max_t_research_scout(rows)
    summary = summarize_multicell_max_t_research_scout(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "scout_row_count": len(rows),
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
