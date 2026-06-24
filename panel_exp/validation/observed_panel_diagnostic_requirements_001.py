"""OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001 validation harness."""

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

_ARTIFACT_ID = "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "observed_panel_diagnostic_requirements_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SIMULATION_DGP_COVERAGE_PLAN_001",
    "METHOD_FAILURE_MODE_REGISTRY_001",
    "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
    "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
    "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
    "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
)

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

MIN_CATEGORY_COUNTS: dict[DiagnosticCategory, int] = {}  # populated after enum definition


class DiagnosticCategory(str, Enum):
    PANEL_STRUCTURE = "panel_structure"
    ASSIGNMENT_DESIGN_VALIDITY = "assignment_design_validity"
    DONOR_SUPPORT_OVERLAP = "donor_support_overlap"
    PRE_PERIOD_FIT_TRENDS = "pre_period_fit_trends"
    TEMPORAL_DEPENDENCE_SHOCKS = "temporal_dependence_shocks"
    OUTCOME_METRIC = "outcome_metric"
    TREATMENT_EXPOSURE = "treatment_exposure"
    MULTICELL_MULTIPLICITY = "multicell_multiplicity"
    ESTIMATOR_ROUTING = "estimator_routing"
    INFERENCE_ROUTING = "inference_routing"


MIN_CATEGORY_COUNTS = {
    DiagnosticCategory.PANEL_STRUCTURE: 10,
    DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY: 8,
    DiagnosticCategory.DONOR_SUPPORT_OVERLAP: 7,
    DiagnosticCategory.PRE_PERIOD_FIT_TRENDS: 7,
    DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS: 7,
    DiagnosticCategory.OUTCOME_METRIC: 9,
    DiagnosticCategory.TREATMENT_EXPOSURE: 6,
    DiagnosticCategory.MULTICELL_MULTIPLICITY: 6,
    DiagnosticCategory.ESTIMATOR_ROUTING: 8,
    DiagnosticCategory.INFERENCE_ROUTING: 8,
}

MIN_ROUTING_IMPACT_COUNTS: dict[RoutingImpact, int] = {}  # populated after enum


class DiagnosticSeverity(str, Enum):
    REQUIRED_BLOCKER = "required_blocker"
    REQUIRED_WARNING = "required_warning"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_FLAG = "research_flag"


class MethodFamily(str, Enum):
    SCM = "scm"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    DID = "did"
    TBRRIDGE = "tbrridge"
    TBR = "tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    SYNTHETIC_DID = "synthetic_did"
    TROP = "trop"
    MULTICELL = "multicell"
    ALL = "all"


class RoutingImpact(str, Enum):
    ALLOW_CANDIDATE_REVIEW = "allow_candidate_review"
    REQUIRE_ADAPTER = "require_adapter"
    REQUIRE_NULL_CALIBRATION = "require_null_calibration"
    REQUIRE_DESIGN_STRESS_TEST = "require_design_stress_test"
    REQUIRE_DGP_COVERAGE = "require_dgp_coverage"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    RESEARCH_REQUIRED = "research_required"
    BLOCK_METHOD_SELECTION = "block_method_selection"
    SCOUT_NEW_METHOD = "scout_new_method"


MIN_ROUTING_IMPACT_COUNTS = {
    RoutingImpact.BLOCK_METHOD_SELECTION: 8,
    RoutingImpact.REQUIRE_NULL_CALIBRATION: 5,
    RoutingImpact.REQUIRE_DESIGN_STRESS_TEST: 3,
    RoutingImpact.REQUIRE_DGP_COVERAGE: 5,
    RoutingImpact.DIAGNOSTIC_ONLY: 5,
    RoutingImpact.RESEARCH_REQUIRED: 5,
    RoutingImpact.SCOUT_NEW_METHOD: 2,
}

REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)


@dataclass(frozen=True)
class ObservedPanelDiagnosticRequirement:
    requirement_id: str
    name: str
    category: DiagnosticCategory
    severity: DiagnosticSeverity
    description: str
    required_inputs: tuple[str, ...]
    affected_method_families: tuple[MethodFamily, ...]
    routing_impacts: tuple[RoutingImpact, ...]
    blocker_condition: str
    warning_condition: str
    recommended_next_artifact: str | None
    notes: str


def _req(
    requirement_id: str,
    name: str,
    category: DiagnosticCategory,
    severity: DiagnosticSeverity,
    description: str,
    *,
    required_inputs: tuple[str, ...],
    affected_method_families: tuple[MethodFamily, ...],
    routing_impacts: tuple[RoutingImpact, ...],
    blocker_condition: str,
    warning_condition: str,
    recommended_next_artifact: str | None = None,
    notes: str = "",
) -> ObservedPanelDiagnosticRequirement:
    return ObservedPanelDiagnosticRequirement(
        requirement_id=requirement_id,
        name=name,
        category=category,
        severity=severity,
        description=description,
        required_inputs=required_inputs,
        affected_method_families=affected_method_families,
        routing_impacts=routing_impacts,
        blocker_condition=blocker_condition,
        warning_condition=warning_condition,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


def _panel_structure_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    all_f = (MethodFamily.ALL,)
    return (
        _req(
            "OPD-PS-001",
            "panel_index_uniqueness",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Unit-time-metric index must be unique before any method routing.",
            required_inputs=("unit_id", "time_id", "metric_id"),
            affected_method_families=all_f,
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="duplicate (unit, time, metric) keys detected",
            warning_condition="near-duplicate keys after deduplication heuristics",
            recommended_next_artifact=None,
        ),
        _req(
            "OPD-PS-002",
            "required_columns_present",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Required unit, time, metric, and treatment/exposure columns must exist.",
            required_inputs=("unit_id", "time_id", "metric_id", "treatment_indicator"),
            affected_method_families=all_f,
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="any required schema column missing",
            warning_condition="optional covariate columns missing for planned estimators",
        ),
        _req(
            "OPD-PS-003",
            "balanced_vs_unbalanced_panel",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Balanced vs unbalanced panel structure affects jackknife and bootstrap routing.",
            required_inputs=("unit_id", "time_id", "metric_value"),
            affected_method_families=(MethodFamily.ALL, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="unbalanced panel with >40% unit-time holes and no imputation contract",
            warning_condition="moderate missingness with imputable gaps",
        ),
        _req(
            "OPD-PS-004",
            "missingness_rate",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Aggregate missingness rate gates sparse-metric and AugSynth paths.",
            required_inputs=("metric_value",),
            affected_method_families=(MethodFamily.AUGSYNTH_CVXPY, MethodFamily.SCM, MethodFamily.ALL),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="missingness >50% in treated or donor windows",
            warning_condition="missingness 15-50% localized to subsets",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-PS-005",
            "duplicate_rows",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Duplicate rows distort weights, placebo pools, and bootstrap resampling.",
            required_inputs=("unit_id", "time_id", "metric_id", "metric_value"),
            affected_method_families=all_f,
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="exact duplicate rows present after index check",
            warning_condition="duplicates resolved only by last-wins rule without audit",
        ),
        _req(
            "OPD-PS-006",
            "pre_period_length",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Pre-period length gates trend-based and synthetic-control methods.",
            required_inputs=("time_id", "treatment_start_time"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.SYNTHETIC_DID, MethodFamily.ALL),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="pre-period < minimum design-specific threshold (e.g., <8 periods)",
            warning_condition="pre-period marginal but above hard minimum",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-PS-007",
            "post_period_length",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Short post-period limits power and bootstrap stability.",
            required_inputs=("time_id", "treatment_start_time"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="post-period < 2 periods for any aggregate inference claim",
            warning_condition="post-period 2-4 periods with high variance",
        ),
        _req(
            "OPD-PS-008",
            "number_of_treated_units",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Treated-unit count affects placebo design and multicell routing.",
            required_inputs=("unit_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.MULTICELL, MethodFamily.ALL),
            routing_impacts=(RoutingImpact.REQUIRE_DESIGN_STRESS_TEST, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="zero treated units in analysis window",
            warning_condition="single treated unit with multi-treated placebo planned",
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _req(
            "OPD-PS-009",
            "number_of_control_units",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Donor/control pool size gates SCM/AugSynth and randomization support.",
            required_inputs=("unit_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.SCOUT_NEW_METHOD),
            blocker_condition="control pool < 3 eligible donors",
            warning_condition="control pool small but non-degenerate",
        ),
        _req(
            "OPD-PS-010",
            "number_of_time_periods",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Total periods inform autocorrelation and seasonality diagnostics.",
            required_inputs=("time_id",),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE,),
            blocker_condition="total periods < 4",
            warning_condition="total periods < 12 with seasonal claims",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-PS-011",
            "small_n_panel_flag",
            DiagnosticCategory.PANEL_STRUCTURE,
            DiagnosticSeverity.RESEARCH_FLAG,
            "Small-N geo panels require restricted inference and research flags.",
            required_inputs=("unit_id", "number_of_treated_units", "number_of_control_units"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="N_units < 5 with production inference requested",
            warning_condition="N_units 5-15 with asymptotic inference planned",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
    )


def _assignment_design_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-AD-001",
            "assignment_mechanism_known",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Unknown assignment blocks design-based randomization and placebo validity claims.",
            required_inputs=("assignment_mechanism", "treatment_indicator"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="assignment mechanism unknown or undocumented",
            warning_condition="assignment documented but not verified against design artifact",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-AD-002",
            "randomized_vs_deterministic",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Deterministic assignment invalidates randomization inference without explicit falsification contract.",
            required_inputs=("assignment_mechanism", "design_family"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="deterministic assignment with randomization inference selected",
            warning_condition="greedy/kernel assignment used as if randomized",
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _req(
            "OPD-AD-003",
            "matched_pair_integrity",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Matched-pair designs require 1:1 pair integrity before pair-based inference.",
            required_inputs=("pair_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_DESIGN_STRESS_TEST),
            blocker_condition="pairs not 1:1 treated/control or orphan units",
            warning_condition="pair covariate imbalance above tolerance",
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _req(
            "OPD-AD-004",
            "matched_block_integrity",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Matched-block designs require block completeness and within-block support.",
            required_inputs=("block_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.REQUIRE_DESIGN_STRESS_TEST, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="blocks with zero treated or zero control",
            warning_condition="blocks with highly unequal treated/control counts",
        ),
        _req(
            "OPD-AD-005",
            "stratification_integrity",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Stratified designs require stratum-level balance and estimand clarity.",
            required_inputs=("stratum_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="empty strata or pooled estimand without stratum contract",
            warning_condition="stratum size imbalance >3:1",
        ),
        _req(
            "OPD-AD-006",
            "rerandomization_rule_known",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Rerandomized designs require documented balance criterion and draw count.",
            required_inputs=("assignment_mechanism", "rerandomization_rule"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION,),
            blocker_condition="rerandomization claimed without rule or seed policy",
            warning_condition="rerandomization rule present but not linked to inference null",
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _req(
            "OPD-AD-007",
            "treatment_timing_consistency",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Inconsistent treatment timing breaks staggered-DID and event-study routing.",
            required_inputs=("unit_id", "time_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="treatment switch-on/off reversals without stagger contract",
            warning_condition="minor timing jitter within same calendar week",
        ),
        _req(
            "OPD-AD-008",
            "shared_control_multicell_structure",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Shared-control multicell requires explicit cell geometry and dependence contract.",
            required_inputs=("cell_id", "treatment_indicator", "control_pool_id"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="shared control with undocumented cross-cell exposure",
            warning_condition="shared control documented but dependence unmodeled",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _req(
            "OPD-AD-009",
            "assignment_support_size",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Randomization support size must be large enough for placebo enumeration.",
            required_inputs=("assignment_support", "treatment_indicator"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="support size < 20 for claimed exact randomization inference",
            warning_condition="support size marginal for studentized placebo",
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _req(
            "OPD-AD-010",
            "pseudo_assignment_feasibility",
            DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "Falsification-only pseudo-assignments require explicit diagnostic boundary.",
            required_inputs=("design_family", "assignment_mechanism"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY,),
            blocker_condition="pseudo-assignment used for production decisioning",
            warning_condition="pseudo-assignment used without falsification label",
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
    )


def _donor_support_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-DS-001",
            "donor_pool_size",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Donor pool size gates SCM weight stability and placebo richness.",
            required_inputs=("unit_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.SCOUT_NEW_METHOD),
            blocker_condition="eligible donors < 3",
            warning_condition="donors 3-8 with high leverage concentration",
        ),
        _req(
            "OPD-DS-002",
            "donor_eligibility",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Ineligible donors (never-treated controls with policy violations) must be excluded.",
            required_inputs=("unit_id", "donor_eligibility_flag"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="ineligible units in donor pool",
            warning_condition="eligibility rules implicit or unaudited",
        ),
        _req(
            "OPD-DS-003",
            "donor_hull_support",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Treated units must lie within donor convex hull for SCM/AugSynth support.",
            required_inputs=("pre_period_metrics", "unit_id"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.SCOUT_NEW_METHOD),
            blocker_condition="treated pre-period path outside donor hull",
            warning_condition="hull marginally satisfied with extrapolation",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-DS-004",
            "pre_period_covariate_overlap",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Covariate overlap required for balancing estimators and DID parallel trends.",
            required_inputs=("covariates", "treatment_indicator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE, MethodFamily.SCM),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="zero overlap in key covariate support",
            warning_condition="thin overlap with standardized mean diff > 0.5",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-DS-005",
            "treated_control_metric_overlap",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Outcome-scale overlap between treated and controls informs support mismatch.",
            required_inputs=("metric_value", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="disjoint outcome supports in pre-period",
            warning_condition="overlap present but scale mismatch >2x",
        ),
        _req(
            "OPD-DS-006",
            "scm_donor_weight_degeneracy",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "SCM donor-weight degeneracy (single-donor dominance) blocks stable inference.",
            required_inputs=("scm_weights", "donor_pool_size"),
            affected_method_families=(MethodFamily.SCM,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="max donor weight > 0.95 or effective donors < 2",
            warning_condition="max donor weight 0.8-0.95",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-DS-007",
            "augsynth_extrapolation_risk",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_WARNING,
            "AugSynth extrapolation beyond donor hull elevates placebo miscalibration risk.",
            required_inputs=("augsynth_weights", "pre_period_metrics"),
            affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="AugSynth active extrapolation with undocumented penalty",
            warning_condition="ridge penalty near boundary with weak support",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-DS-008",
            "support_mismatch_blocker",
            DiagnosticCategory.DONOR_SUPPORT_OVERLAP,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Hard support mismatch blocks SCM/AugSynth candidate promotion.",
            required_inputs=("pre_period_metrics", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="support mismatch score above hard threshold",
            warning_condition="support mismatch moderate with sensitivity plan",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
    )


def _pre_period_fit_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-PF-001",
            "pre_period_fit_quality",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Poor pre-period fit blocks SCM/AugSynth and synthetic counterfactual claims.",
            required_inputs=("actual_pre", "synthetic_pre"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY, MethodFamily.SYNTHETIC_DID),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="pre-period RMSPE ratio > 2.0 vs best donor benchmark",
            warning_condition="RMSPE ratio 1.5-2.0",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-PF-002",
            "pre_period_residual_bias",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Systematic pre-period residual bias signals misspecification.",
            required_inputs=("pre_period_residuals",),
            affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="significant pre-period residual trend (p<0.01 on placebo scale)",
            warning_condition="mild residual drift within tolerance",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-PF-003",
            "parallel_trend_plausibility",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "DID and synthetic-DID require plausible parallel trends in pre-period.",
            required_inputs=("treated_pre_trend", "control_pre_trend"),
            affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="pre-period trend divergence significant at hard threshold",
            warning_condition="divergence marginal; event-study sensitivity required",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-PF-004",
            "trend_break_detection",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Pre-period trend breaks undermine counterfactual extrapolation.",
            required_inputs=("time_id", "metric_value", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="structural break in last 25% of pre-period",
            warning_condition="minor break with documented shock annotation",
        ),
        _req(
            "OPD-PF-005",
            "baseline_nonstationarity",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Nonstationary baselines require detrending or restricted inference.",
            required_inputs=("metric_value", "time_id"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="unit root or explosive pre-trend without adjustment",
            warning_condition="slow drift with partial differencing candidate",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-PF-006",
            "pre_period_shock_sensitivity",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Pre-period shocks (promos, outages) require leave-one-period stability checks.",
            required_inputs=("time_id", "metric_value", "shock_annotations"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="single pre-period shock drives >50% of fit improvement",
            warning_condition="shock present but bounded influence",
        ),
        _req(
            "OPD-PF-007",
            "leave_last_pre_period_stability",
            DiagnosticCategory.PRE_PERIOD_FIT_TRENDS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Stability when dropping last pre-period week gates short-pre designs.",
            required_inputs=("pre_period_metrics",),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="fit or weights unstable when dropping last pre period",
            warning_condition="moderate instability within documented tolerance",
        ),
    )


def _temporal_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-TD-001",
            "autocorrelation",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Autocorrelation affects bootstrap, jackknife, and randomization calibration.",
            required_inputs=("metric_value", "time_id"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="strong AR(p) with invalid IID null assumed",
            warning_condition="mild autocorrelation; block bootstrap candidate",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-TD-002",
            "seasonality",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Seasonality must be diagnosed before trend and placebo inference.",
            required_inputs=("time_id", "metric_value"),
            affected_method_families=(MethodFamily.DID, MethodFamily.SCM, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="seasonality ignored in DID with <1 yearly cycle pre-period",
            warning_condition="seasonality present with partial adjustment",
        ),
        _req(
            "OPD-TD-003",
            "holiday_promo_shocks",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Holiday and promo shocks can masquerade as treatment effects.",
            required_inputs=("time_id", "shock_calendar"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="untreated shock coincident with treatment without adjustment",
            warning_condition="shocks documented and partially adjusted",
        ),
        _req(
            "OPD-TD-004",
            "outlier_weeks",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Outlier weeks distort weights, placebos, and bootstrap draws.",
            required_inputs=("time_id", "metric_value"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE, MethodFamily.TBR),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="single outlier drives entire post-period claim",
            warning_condition="isolated outliers with robustness check planned",
        ),
        _req(
            "OPD-TD-005",
            "level_shifts",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Undiagnosed level shifts break parallel trends and synthetic fit.",
            required_inputs=("time_id", "metric_value"),
            affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="level shift in pre-period untreated series",
            warning_condition="shift at treatment boundary with ambiguity",
        ),
        _req(
            "OPD-TD-006",
            "time_varying_variance",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Heteroskedasticity over time affects studentized statistics.",
            required_inputs=("metric_value", "time_id"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="variance ratio pre/post > 5 without adjustment",
            warning_condition="moderate heteroskedasticity",
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _req(
            "OPD-TD-007",
            "metric_delay_lag_mismatch",
            DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Metric delay/lag mismatch between treatment and outcome timing.",
            required_inputs=("time_id", "treatment_indicator", "metric_id"),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_ADAPTER),
            blocker_condition="treatment-on metric read before plausible lag",
            warning_condition="lag uncertainty spans multiple periods",
        ),
    )


def _outcome_metric_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-OM-001",
            "metric_sparsity",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Sparse conversion metrics restrict asymptotic inference.",
            required_inputs=("metric_value",),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE, RoutingImpact.SCOUT_NEW_METHOD),
            blocker_condition=">80% zeros in treated post-period with Gaussian inference",
            warning_condition="30-80% sparsity with count-aware path needed",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-OM-002",
            "zero_inflation",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Zero inflation requires count/binary-aware estimators or scouts.",
            required_inputs=("metric_value",),
            affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR, MethodFamily.SCM),
            routing_impacts=(RoutingImpact.SCOUT_NEW_METHOD, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="zero inflation >60% with log-Gaussian model",
            warning_condition="moderate zero inflation",
        ),
        _req(
            "OPD-OM-003",
            "count_outcome_flag",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Count outcomes block Gaussian default inference paths.",
            required_inputs=("metric_value", "metric_type"),
            affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
            routing_impacts=(RoutingImpact.SCOUT_NEW_METHOD, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="count outcome with homoskedastic Gaussian CI",
            warning_condition="count outcome with quasi-Poisson plan undocumented",
        ),
        _req(
            "OPD-OM-004",
            "binary_binomial_outcome",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Binary/binomial outcomes require proportion-scale diagnostics.",
            required_inputs=("metric_value", "denominator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="binomial outcome analyzed as continuous without denominator",
            warning_condition="bounded [0,1] with moderate counts",
        ),
        _req(
            "OPD-OM-005",
            "heavy_tailed_outcome",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Heavy tails invalidate mean-based estimands without robust summaries.",
            required_inputs=("metric_value",),
            affected_method_families=(MethodFamily.TBR, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="kurtosis > 10 with mean estimand and no winsor plan",
            warning_condition="moderate heavy tails",
        ),
        _req(
            "OPD-OM-006",
            "variance_instability",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Outcome variance instability across units affects weighting.",
            required_inputs=("metric_value", "unit_id"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION,),
            blocker_condition="unit variance spread > 100x without scale normalization",
            warning_condition="moderate variance heterogeneity",
        ),
        _req(
            "OPD-OM-007",
            "scale_compatibility",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Scale compatibility across units/metrics required for pooled panels.",
            required_inputs=("metric_value", "metric_id", "unit_id"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_ADAPTER),
            blocker_condition="incompatible scales pooled without transform contract",
            warning_condition="scale differences with documented normalization",
        ),
        _req(
            "OPD-OM-008",
            "negative_values_log_transform",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Negative or zero values block log-response models.",
            required_inputs=("metric_value",),
            affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR, MethodFamily.BAYESIAN_TBR),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="log transform requested with non-positive values",
            warning_condition="zeros present with ad-hoc offset only",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-OM-009",
            "denominator_availability",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Rate metrics require denominator availability and consistency.",
            required_inputs=("numerator", "denominator"),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="rate metric without denominator column",
            warning_condition="denominator sparse or lagged inconsistently",
        ),
        _req(
            "OPD-OM-010",
            "rate_metric_consistency",
            DiagnosticCategory.OUTCOME_METRIC,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Rate metric construction must be consistent across pre/post windows.",
            required_inputs=("numerator", "denominator", "time_id"),
            affected_method_families=(MethodFamily.DID,),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="denominator definition changes at treatment",
            warning_condition="minor denominator revisions documented",
        ),
    )


def _treatment_exposure_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-TE-001",
            "treatment_intensity_variation",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Treatment intensity variation affects dose-response routing.",
            required_inputs=("treatment_intensity",),
            affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            routing_impacts=(RoutingImpact.SENSITIVITY_ONLY, RoutingImpact.REQUIRE_ADAPTER),
            blocker_condition="binary treatment assumed with continuous intensity",
            warning_condition="intensity variation with binary collapse undocumented",
        ),
        _req(
            "OPD-TE-002",
            "dose_exposure_availability",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Dose/exposure data availability gates continuous treatment models.",
            required_inputs=("treatment_intensity", "time_id"),
            affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.DID),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY,),
            blocker_condition="dose model selected without exposure column",
            warning_condition="proxy exposure used without validation",
        ),
        _req(
            "OPD-TE-003",
            "on_off_consistency",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "On/off treatment consistency required for sharp designs.",
            required_inputs=("treatment_indicator", "time_id"),
            affected_method_families=(MethodFamily.DID, MethodFamily.ALL),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="treatment turns off in post-period without protocol",
            warning_condition="brief gaps in treatment exposure",
        ),
        _req(
            "OPD-TE-004",
            "partial_compliance",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Partial compliance requires estimand and inference adjustment.",
            required_inputs=("assigned_treatment", "actual_treatment"),
            affected_method_families=(MethodFamily.DID, MethodFamily.ALL),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.SENSITIVITY_ONLY),
            blocker_condition="ITT vs TOT estimand ambiguous with compliance <50%",
            warning_condition="moderate compliance deviation",
        ),
        _req(
            "OPD-TE-005",
            "staggered_activation",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Staggered activation requires event-study or cohort routing.",
            required_inputs=("unit_id", "treatment_start_time"),
            affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="staggered rollout with single-cohort DID",
            warning_condition="staggered with documented cohort plan",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-TE-006",
            "contamination_risk",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Control contamination invalidates clean comparison estimands.",
            required_inputs=("unit_id", "treatment_indicator", "exposure_map"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="controls receive treatment spillover above threshold",
            warning_condition="possible contamination with sensitivity bounds",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-TE-007",
            "spillover_interference_risk",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Spillover/interference risk blocks naive geo causal claims.",
            required_inputs=("geo_adjacency", "treatment_indicator"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.MULTICELL),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.SCOUT_NEW_METHOD),
            blocker_condition="spatial interference likely without buffer or model",
            warning_condition="mild spillover with buffer zones",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _req(
            "OPD-TE-008",
            "cross_cell_exposure_leakage",
            DiagnosticCategory.TREATMENT_EXPOSURE,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Cross-cell exposure leakage breaks multicell independence.",
            required_inputs=("cell_id", "treatment_indicator"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="units exposed to multiple cells simultaneously",
            warning_condition="leakage risk with partial overlap",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
    )


def _multicell_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-MC-001",
            "shared_control_dependence",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Shared-control dependence blocks naive independent-cell inference.",
            required_inputs=("cell_id", "control_pool_id"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="shared control with independent-cell max-T not modeled",
            warning_condition="dependence documented but unadjusted",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _req(
            "OPD-MC-002",
            "multiple_arms",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Multiple arms require arm-level estimand and routing clarity.",
            required_inputs=("cell_id", "arm_id"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition=">3 arms with uncorrected winner selection",
            warning_condition="2-3 arms with per-cell restricted readouts",
        ),
        _req(
            "OPD-MC-003",
            "winner_selection_risk",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Winner selection without multiplicity control inflates false positives.",
            required_inputs=("cell_id", "test_statistics"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="best-cell selection without max-T/stepdown",
            warning_condition="informal best-cell highlight only",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _req(
            "OPD-MC-004",
            "familywise_error_risk",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Familywise error risk must be diagnosed before simultaneous claims.",
            required_inputs=("cell_id", "number_of_tests"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="familywise decisioning without calibration evidence",
            warning_condition="per-cell marginal only with multiplicity warning",
        ),
        _req(
            "OPD-MC-005",
            "cell_level_independence",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Cell-level independence assumption must be validated.",
            required_inputs=("cell_id", "unit_id"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.REQUIRE_DGP_COVERAGE, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="units span multiple cells without blocking",
            warning_condition="partial overlap with cluster adjustment plan",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-MC-006",
            "cell_specific_estimand_clarity",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Each cell must have explicit estimand before method selection.",
            required_inputs=("cell_id", "estimand_spec"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION,),
            blocker_condition="cell estimand undefined or pooled by default",
            warning_condition="estimand documented but geometry ambiguous",
        ),
        _req(
            "OPD-MC-007",
            "pooled_global_estimand_ambiguity",
            DiagnosticCategory.MULTICELL_MULTIPLICITY,
            DiagnosticSeverity.RESEARCH_FLAG,
            "Pooled/global multicell estimands require research-level scrutiny.",
            required_inputs=("cell_id", "estimand_spec"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="global pooled estimand with heterogeneous cells",
            warning_condition="pooled estimand with homogeneity untested",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
    )


def _estimator_routing_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-ER-001",
            "scm_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "SCM suitability requires support, fit, and donor-weight diagnostics pass.",
            required_inputs=("donor_hull_support", "pre_period_fit_quality", "scm_weights"),
            affected_method_families=(MethodFamily.SCM,),
            routing_impacts=(RoutingImpact.ALLOW_CANDIDATE_REVIEW, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="any SCM hard blocker diagnostic failed",
            warning_condition="SCM warnings present with sensitivity plan",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-ER-002",
            "augsynth_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "AugSynth suitability requires hull, penalty, and extrapolation diagnostics.",
            required_inputs=("augsynth_weights", "augsynth_extrapolation_risk"),
            affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
            routing_impacts=(RoutingImpact.ALLOW_CANDIDATE_REVIEW, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="AugSynth extrapolation or support blocker",
            warning_condition="ridge penalty at boundary",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-ER-003",
            "did_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "DID suitability requires parallel trends and assignment validity.",
            required_inputs=("parallel_trend_plausibility", "assignment_mechanism_known"),
            affected_method_families=(MethodFamily.DID,),
            routing_impacts=(RoutingImpact.ALLOW_CANDIDATE_REVIEW, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="parallel trend or assignment blocker",
            warning_condition="DID warnings with event-study backup",
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _req(
            "OPD-ER-004",
            "tbrridge_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "TBRRidge suitability requires geometry, scale, and BRB diagnostic gates.",
            required_inputs=("scale_compatibility", "negative_values_log_transform"),
            affected_method_families=(MethodFamily.TBRRIDGE,),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="TBRRidge hard blockers or BRB variance failures",
            warning_condition="TBRRidge restricted diagnostic-only path",
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        _req(
            "OPD-ER-005",
            "tbr_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "TBR suitability remains diagnostic-only pending aggregate geometry fix.",
            required_inputs=("scale_compatibility", "outlier_weeks"),
            affected_method_families=(MethodFamily.TBR,),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY, RoutingImpact.BLOCK_METHOD_SELECTION),
            blocker_condition="TBR selected for production inference",
            warning_condition="TBR exploratory only with geometry mismatch noted",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-ER-006",
            "bayesian_tbr_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "Bayesian TBR suitability is posterior diagnostic-only boundary.",
            required_inputs=("scale_compatibility", "prior_spec"),
            affected_method_families=(MethodFamily.BAYESIAN_TBR,),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY,),
            blocker_condition="Bayesian TBR used for production decisioning",
            warning_condition="posterior intervals without predictive check",
        ),
        _req(
            "OPD-ER-007",
            "synthetic_did_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.RESEARCH_FLAG,
            "Synthetic DID suitability requires trend, support, and research scout.",
            required_inputs=("parallel_trend_plausibility", "donor_hull_support"),
            affected_method_families=(MethodFamily.SYNTHETIC_DID,),
            routing_impacts=(RoutingImpact.SCOUT_NEW_METHOD, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="SDID promoted without DGP coverage",
            warning_condition="SDID candidate with partial diagnostics",
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
        ),
        _req(
            "OPD-ER-008",
            "trop_suitability",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.RESEARCH_FLAG,
            "TROP suitability is research/scout stage only.",
            required_inputs=("pre_period_fit_quality", "panel_structure"),
            affected_method_families=(MethodFamily.TROP,),
            routing_impacts=(RoutingImpact.SCOUT_NEW_METHOD, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="TROP selected without research scout artifact",
            warning_condition="TROP exploratory with incomplete diagnostics",
        ),
        _req(
            "OPD-ER-009",
            "new_method_scout_trigger",
            DiagnosticCategory.ESTIMATOR_ROUTING,
            DiagnosticSeverity.RESEARCH_FLAG,
            "Trigger new method scout when all incumbent families fail diagnostics.",
            required_inputs=("estimator_routing_summary",),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.SCOUT_NEW_METHOD, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="no estimator passes with production inference requested",
            warning_condition="multiple estimators blocked; scout warranted",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
    )


def _inference_routing_rows() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    return (
        _req(
            "OPD-IR-001",
            "randomization_inference_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Randomization inference requires known randomized assignment and support.",
            required_inputs=("assignment_mechanism_known", "assignment_support_size"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.REQUIRE_NULL_CALIBRATION),
            blocker_condition="unknown or deterministic assignment with RI selected",
            warning_condition="support size marginal for exact RI",
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _req(
            "OPD-IR-002",
            "placebo_rank_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Placebo rank requires treated-set design and pre-fit quality.",
            required_inputs=("number_of_treated_units", "pre_period_fit_quality"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="multi-treated placebo without design-aware contract",
            warning_condition="single-treated placebo with marginal fit",
        ),
        _req(
            "OPD-IR-003",
            "studentized_statistic_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Studentized statistics require variance stability diagnostics.",
            required_inputs=("time_varying_variance", "metric_sparsity"),
            affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION,),
            blocker_condition="heavy heteroskedasticity without studentization contract",
            warning_condition="studentization planned but uncalibrated",
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _req(
            "OPD-IR-004",
            "bootstrap_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Bootstrap feasibility depends on panel balance and temporal dependence.",
            required_inputs=("balanced_vs_unbalanced_panel", "autocorrelation"),
            affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.DID),
            routing_impacts=(RoutingImpact.REQUIRE_NULL_CALIBRATION, RoutingImpact.REQUIRE_DGP_COVERAGE),
            blocker_condition="IID bootstrap with strong autocorrelation",
            warning_condition="block bootstrap candidate with partial calibration",
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        _req(
            "OPD-IR-005",
            "jackknife_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Unit jackknife requires sufficient units and balanced support.",
            required_inputs=("number_of_treated_units", "number_of_control_units"),
            affected_method_families=(MethodFamily.AUGSYNTH_CVXPY, MethodFamily.SCM),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY, RoutingImpact.BLOCK_METHOD_SELECTION),
            blocker_condition="jackknife with <5 units or known AugSynth retire path",
            warning_condition="jackknife with heterogeneity warnings",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
        _req(
            "OPD-IR-006",
            "cluster_robust_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_WARNING,
            "Cluster-robust analytic inference requires cluster count and structure.",
            required_inputs=("cluster_id", "number_of_clusters"),
            affected_method_families=(MethodFamily.DID,),
            routing_impacts=(RoutingImpact.RESEARCH_REQUIRED, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="<10 clusters with cluster-robust production CI",
            warning_condition="marginal cluster count with CRVE planned",
        ),
        _req(
            "OPD-IR-007",
            "conformal_feasibility",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.RESEARCH_FLAG,
            "Conformal panel inference remains research/scout only.",
            required_inputs=("panel_structure", "autocorrelation"),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.SCOUT_NEW_METHOD, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="conformal promoted without panel exchangeability review",
            warning_condition="conformal exploratory with dependence ignored",
        ),
        _req(
            "OPD-IR-008",
            "posterior_diagnostic_only_boundary",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.DIAGNOSTIC_ONLY,
            "Bayesian posterior routes are diagnostic-only until governance promotion.",
            required_inputs=("prior_spec", "posterior_predictive_check"),
            affected_method_families=(MethodFamily.BAYESIAN_TBR,),
            routing_impacts=(RoutingImpact.DIAGNOSTIC_ONLY,),
            blocker_condition="posterior interval used for production decisioning",
            warning_condition="PPC incomplete",
        ),
        _req(
            "OPD-IR-009",
            "max_t_stepdown_need",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "Max-T/stepdown required for simultaneous multicell inference.",
            required_inputs=("multiple_arms", "familywise_error_risk"),
            affected_method_families=(MethodFamily.MULTICELL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.RESEARCH_REQUIRED),
            blocker_condition="simultaneous multicell claim without multiplicity procedure",
            warning_condition="per-cell only with multiplicity deferred",
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _req(
            "OPD-IR-010",
            "no_valid_inference_blocker",
            DiagnosticCategory.INFERENCE_ROUTING,
            DiagnosticSeverity.REQUIRED_BLOCKER,
            "No valid inference path when all inference diagnostics fail.",
            required_inputs=("inference_routing_summary",),
            affected_method_families=(MethodFamily.ALL,),
            routing_impacts=(RoutingImpact.BLOCK_METHOD_SELECTION, RoutingImpact.DIAGNOSTIC_ONLY),
            blocker_condition="all inference families blocked for panel",
            warning_condition="only sensitivity/diagnostic routes remain",
            recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001",
        ),
    )


def build_observed_panel_diagnostic_requirements() -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    """Build the full observed-panel diagnostic requirements registry."""
    return (
        *_panel_structure_rows(),
        *_assignment_design_rows(),
        *_donor_support_rows(),
        *_pre_period_fit_rows(),
        *_temporal_rows(),
        *_outcome_metric_rows(),
        *_treatment_exposure_rows(),
        *_multicell_rows(),
        *_estimator_routing_rows(),
        *_inference_routing_rows(),
    )


def filter_observed_panel_diagnostic_requirements(
    requirements: tuple[ObservedPanelDiagnosticRequirement, ...],
    *,
    category: DiagnosticCategory | None = None,
    severity: DiagnosticSeverity | None = None,
    method_family: MethodFamily | None = None,
    routing_impact: RoutingImpact | None = None,
) -> tuple[ObservedPanelDiagnosticRequirement, ...]:
    """Filter requirements by optional predicates."""
    filtered: list[ObservedPanelDiagnosticRequirement] = []
    for req in requirements:
        if category is not None and req.category != category:
            continue
        if severity is not None and req.severity != severity:
            continue
        if method_family is not None and method_family not in req.affected_method_families:
            continue
        if routing_impact is not None and routing_impact not in req.routing_impacts:
            continue
        filtered.append(req)
    return tuple(filtered)


def validate_observed_panel_diagnostic_requirements(
    requirements: tuple[ObservedPanelDiagnosticRequirement, ...],
) -> dict[str, Any]:
    """Validate requirement invariants and return structured validation summary."""
    issues: list[str] = []
    req_ids = [r.requirement_id for r in requirements]

    if len(req_ids) != len(set(req_ids)):
        issues.append("duplicate requirement_id detected")
    if len(requirements) < 70:
        issues.append(f"requirement_count {len(requirements)} < 70")

    category_counts = Counter(r.category for r in requirements)
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        if category_counts.get(cat, 0) < minimum:
            issues.append(f"category {cat.value} count {category_counts.get(cat, 0)} < {minimum}")

    routing_counts = Counter(impact for r in requirements for impact in r.routing_impacts)
    for impact, minimum in MIN_ROUTING_IMPACT_COUNTS.items():
        if routing_counts.get(impact, 0) < minimum:
            issues.append(f"routing impact {impact.value} count {routing_counts.get(impact, 0)} < {minimum}")

    method_families_present: set[MethodFamily] = set()
    for req in requirements:
        method_families_present.update(req.affected_method_families)
    missing_methods = sorted(REQUIRED_METHOD_FAMILIES - method_families_present, key=lambda m: m.value)
    if missing_methods:
        issues.append(f"missing method families: {[m.value for m in missing_methods]}")

    for req in requirements:
        if not req.blocker_condition.strip():
            issues.append(f"{req.requirement_id} empty blocker_condition")
        if not req.warning_condition.strip():
            issues.append(f"{req.requirement_id} empty warning_condition")
        if not req.affected_method_families:
            issues.append(f"{req.requirement_id} empty affected_method_families")

    blockers = [r for r in requirements if r.severity == DiagnosticSeverity.REQUIRED_BLOCKER]
    warnings = [r for r in requirements if r.severity == DiagnosticSeverity.REQUIRED_WARNING]
    if not blockers:
        issues.append("no hard blockers defined")
    if not warnings:
        issues.append("no warnings defined")

    artifacts = {r.recommended_next_artifact for r in requirements if r.recommended_next_artifact}
    route_checks = {
        "routes_to_simulation_dgp_coverage_plan": "SIMULATION_DGP_COVERAGE_PLAN_001" in artifacts,
        "routes_to_failure_mode_registry": "METHOD_FAILURE_MODE_REGISTRY_001" in artifacts,
        "routes_to_design_stress_tests": "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001" in artifacts,
        "routes_to_multicell_research": "MULTICELL_MAX_T_RESEARCH_SCOUT_001" in artifacts,
    }
    for label, ok in route_checks.items():
        if not ok:
            issues.append(f"{label} not satisfied")

    return {
        "valid": not issues,
        "requirement_count": len(requirements),
        "unique_requirement_ids": len(req_ids) == len(set(req_ids)),
        "category_counts": {cat.value: category_counts.get(cat, 0) for cat in DiagnosticCategory},
        "panel_structure_covered": category_counts.get(DiagnosticCategory.PANEL_STRUCTURE, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.PANEL_STRUCTURE],
        "assignment_design_validity_covered": category_counts.get(DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.ASSIGNMENT_DESIGN_VALIDITY],
        "donor_support_overlap_covered": category_counts.get(DiagnosticCategory.DONOR_SUPPORT_OVERLAP, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.DONOR_SUPPORT_OVERLAP],
        "pre_period_fit_trends_covered": category_counts.get(DiagnosticCategory.PRE_PERIOD_FIT_TRENDS, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.PRE_PERIOD_FIT_TRENDS],
        "temporal_dependence_shocks_covered": category_counts.get(DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.TEMPORAL_DEPENDENCE_SHOCKS],
        "outcome_metric_covered": category_counts.get(DiagnosticCategory.OUTCOME_METRIC, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.OUTCOME_METRIC],
        "treatment_exposure_covered": category_counts.get(DiagnosticCategory.TREATMENT_EXPOSURE, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.TREATMENT_EXPOSURE],
        "multicell_multiplicity_covered": category_counts.get(DiagnosticCategory.MULTICELL_MULTIPLICITY, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.MULTICELL_MULTIPLICITY],
        "estimator_routing_covered": category_counts.get(DiagnosticCategory.ESTIMATOR_ROUTING, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.ESTIMATOR_ROUTING],
        "inference_routing_covered": category_counts.get(DiagnosticCategory.INFERENCE_ROUTING, 0) >= MIN_CATEGORY_COUNTS[DiagnosticCategory.INFERENCE_ROUTING],
        "hard_blockers_defined": bool(blockers),
        "warnings_defined": bool(warnings),
        **route_checks,
        "issues": issues,
    }


def summarize_observed_panel_diagnostic_requirements(
    requirements: tuple[ObservedPanelDiagnosticRequirement, ...],
) -> dict[str, Any]:
    """Serialize observed-panel diagnostic requirements summary for archives."""
    validation = validate_observed_panel_diagnostic_requirements(requirements)
    severity_counts = Counter(r.severity.value for r in requirements)
    routing_impact_counts = Counter(impact.value for r in requirements for impact in r.routing_impacts)
    method_family_counts: Counter[str] = Counter()
    for req in requirements:
        for family in req.affected_method_families:
            method_family_counts[family.value] += 1

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "requirement_count": len(requirements),
        "failed_scenarios": validation.get("issues", []),
        "category_counts": validation["category_counts"],
        "severity_counts": dict(severity_counts),
        "routing_impact_counts": dict(routing_impact_counts),
        "method_family_counts": dict(method_family_counts),
        "panel_structure_covered": validation["panel_structure_covered"],
        "assignment_design_validity_covered": validation["assignment_design_validity_covered"],
        "donor_support_overlap_covered": validation["donor_support_overlap_covered"],
        "pre_period_fit_trends_covered": validation["pre_period_fit_trends_covered"],
        "temporal_dependence_shocks_covered": validation["temporal_dependence_shocks_covered"],
        "outcome_metric_covered": validation["outcome_metric_covered"],
        "treatment_exposure_covered": validation["treatment_exposure_covered"],
        "multicell_multiplicity_covered": validation["multicell_multiplicity_covered"],
        "estimator_routing_covered": validation["estimator_routing_covered"],
        "inference_routing_covered": validation["inference_routing_covered"],
        "method_selection_requires_observed_panel_diagnostics": True,
        "hard_blockers_defined": validation["hard_blockers_defined"],
        "warnings_defined": validation["warnings_defined"],
        "routes_to_simulation_dgp_coverage_plan": validation["routes_to_simulation_dgp_coverage_plan"],
        "routes_to_failure_mode_registry": validation["routes_to_failure_mode_registry"],
        "routes_to_design_stress_tests": validation["routes_to_design_stress_tests"],
        "routes_to_multicell_research": validation["routes_to_multicell_research"],
        "downstream_work_paused": True,
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
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
    requirements = build_observed_panel_diagnostic_requirements()
    validation = validate_observed_panel_diagnostic_requirements(requirements)
    summary = summarize_observed_panel_diagnostic_requirements(requirements)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("requirements_build_successfully", len(requirements) > 0))
    scenarios.append(_scenario("requirement_count_at_least_70", len(requirements) >= 70))
    scenarios.append(_scenario("requirement_ids_unique", validation["unique_requirement_ids"]))

    for cat in DiagnosticCategory:
        key = f"category_{cat.value}_covered"
        scenarios.append(_scenario(key, validation.get(f"{cat.value}_covered", validation["category_counts"].get(cat.value, 0) >= MIN_CATEGORY_COUNTS[cat])))

    coverage_keys = [
        "panel_structure_covered",
        "assignment_design_validity_covered",
        "donor_support_overlap_covered",
        "pre_period_fit_trends_covered",
        "temporal_dependence_shocks_covered",
        "outcome_metric_covered",
        "treatment_exposure_covered",
        "multicell_multiplicity_covered",
        "estimator_routing_covered",
        "inference_routing_covered",
    ]
    for key in coverage_keys:
        scenarios.append(_scenario(key, validation[key]))

    for impact, minimum in MIN_ROUTING_IMPACT_COUNTS.items():
        count = sum(1 for r in requirements for i in r.routing_impacts if i == impact)
        scenarios.append(_scenario(f"routing_impact_{impact.value}_at_least_{minimum}", count >= minimum))

    scenarios.append(_scenario("hard_blockers_defined", summary["hard_blockers_defined"] is True))
    scenarios.append(_scenario("warnings_defined", summary["warnings_defined"] is True))
    scenarios.append(_scenario("method_selection_requires_observed_panel_diagnostics", summary["method_selection_requires_observed_panel_diagnostics"] is True))
    scenarios.append(_scenario("routes_to_simulation_dgp_coverage_plan", summary["routes_to_simulation_dgp_coverage_plan"] is True))
    scenarios.append(_scenario("routes_to_failure_mode_registry", summary["routes_to_failure_mode_registry"] is True))
    scenarios.append(_scenario("routes_to_design_stress_tests", summary["routes_to_design_stress_tests"] is True))
    scenarios.append(_scenario("routes_to_multicell_research", summary["routes_to_multicell_research"] is True))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_simulation_dgp_coverage_plan_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(family in r.affected_method_families for r in requirements)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    requirements = build_observed_panel_diagnostic_requirements()
    validation = validate_observed_panel_diagnostic_requirements(requirements)
    summary = summarize_observed_panel_diagnostic_requirements(requirements)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "requirement_count": len(requirements),
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
