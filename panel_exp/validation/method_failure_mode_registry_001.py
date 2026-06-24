"""METHOD_FAILURE_MODE_REGISTRY_001 validation harness."""

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

_ARTIFACT_ID = "METHOD_FAILURE_MODE_REGISTRY_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "method_failure_mode_registry_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/METHOD_FAILURE_MODE_REGISTRY_001_summary.json"

RECOMMENDED_NEXT_ARTIFACTS = (
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


class FailureModeCategory(str, Enum):
    DESIGN_ASSIGNMENT = "design_assignment"
    PANEL_STRUCTURE = "panel_structure"
    DONOR_SUPPORT = "donor_support"
    PRE_PERIOD_FIT_TRENDS = "pre_period_fit_trends"
    TEMPORAL_DEPENDENCE_SHOCKS = "temporal_dependence_shocks"
    OUTCOME_METRIC = "outcome_metric"
    TREATMENT_EXPOSURE_INTERFERENCE = "treatment_exposure_interference"
    ESTIMATOR_SPECIFIC = "estimator_specific"
    INFERENCE_SPECIFIC = "inference_specific"
    CALIBRATION_PROMOTION = "calibration_promotion"
    DOWNSTREAM_BOUNDARY = "downstream_boundary"


MIN_CATEGORY_COUNTS = {
    FailureModeCategory.DESIGN_ASSIGNMENT: 10,
    FailureModeCategory.PANEL_STRUCTURE: 9,
    FailureModeCategory.DONOR_SUPPORT: 8,
    FailureModeCategory.PRE_PERIOD_FIT_TRENDS: 7,
    FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS: 7,
    FailureModeCategory.OUTCOME_METRIC: 9,
    FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE: 8,
    FailureModeCategory.ESTIMATOR_SPECIFIC: 10,
    FailureModeCategory.INFERENCE_SPECIFIC: 11,
    FailureModeCategory.CALIBRATION_PROMOTION: 8,
    FailureModeCategory.DOWNSTREAM_BOUNDARY: 8,
}


class FailureSeverity(str, Enum):
    HARD_BLOCKER = "hard_blocker"
    RESTRICTED_RESEARCH = "restricted_research"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    REMEDIATION_REQUIRED = "remediation_required"
    RETIRE_OR_REPLACE = "retire_or_replace"


MIN_SEVERITY_COUNTS = {
    FailureSeverity.HARD_BLOCKER: 20,
    FailureSeverity.RESTRICTED_RESEARCH: 8,
    FailureSeverity.DIAGNOSTIC_ONLY: 8,
    FailureSeverity.SENSITIVITY_ONLY: 6,
    FailureSeverity.REMEDIATION_REQUIRED: 10,
    FailureSeverity.RETIRE_OR_REPLACE: 4,
}


class RequiredAction(str, Enum):
    BLOCK = "block"
    KEEP_RESEARCH_ONLY = "keep_research_only"
    MARK_DIAGNOSTIC_ONLY = "mark_diagnostic_only"
    MARK_SENSITIVITY_ONLY = "mark_sensitivity_only"
    REQUIRE_NULL_CALIBRATION = "require_null_calibration"
    REQUIRE_DGP_COVERAGE = "require_dgp_coverage"
    REQUIRE_OBSERVED_DIAGNOSTICS = "require_observed_diagnostics"
    REQUIRE_DESIGN_STRESS_TEST = "require_design_stress_test"
    REQUIRE_METHOD_ADAPTER = "require_method_adapter"
    REQUIRE_LITERATURE_ALIGNMENT = "require_literature_alignment"
    REMEDIATE = "remediate"
    RETIRE_OR_REPLACE = "retire_or_replace"
    SCOUT_NEW_METHOD = "scout_new_method"


MIN_ACTION_COUNTS = {
    RequiredAction.BLOCK: 20,
    RequiredAction.KEEP_RESEARCH_ONLY: 8,
    RequiredAction.MARK_DIAGNOSTIC_ONLY: 8,
    RequiredAction.MARK_SENSITIVITY_ONLY: 6,
    RequiredAction.REQUIRE_NULL_CALIBRATION: 8,
    RequiredAction.REQUIRE_DGP_COVERAGE: 10,
    RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS: 10,
    RequiredAction.REQUIRE_DESIGN_STRESS_TEST: 5,
    RequiredAction.REQUIRE_METHOD_ADAPTER: 3,
    RequiredAction.REQUIRE_LITERATURE_ALIGNMENT: 4,
    RequiredAction.REMEDIATE: 8,
    RequiredAction.RETIRE_OR_REPLACE: 4,
    RequiredAction.SCOUT_NEW_METHOD: 3,
}


class DesignFamily(str, Enum):
    SINGLE_TREATED_GEO = "single_treated_geo"
    MULTI_TREATED_GEO = "multi_treated_geo"
    MATCHED_PAIR = "matched_pair"
    MATCHED_BLOCK = "matched_block"
    STRATIFIED = "stratified"
    RERANDOMIZED = "rerandomized"
    GREEDY_MATCHED_MARKET = "greedy_matched_market"
    KERNEL_THINNING = "kernel_thinning"
    FIXED_DETERMINISTIC = "fixed_deterministic"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    MULTICELL_INDEPENDENT_CELLS = "multicell_independent_cells"
    UNKNOWN_ASSIGNMENT = "unknown_assignment"
    ALL = "all"


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


class InferenceFamily(str, Enum):
    RANDOMIZATION = "randomization"
    PERMUTATION = "permutation"
    PLACEBO_RANK = "placebo_rank"
    STUDENTIZED_PLACEBO_RANK = "studentized_placebo_rank"
    BOOTSTRAP = "bootstrap"
    BLOCK_RESIDUAL_BOOTSTRAP = "block_residual_bootstrap"
    JACKKNIFE = "jackknife"
    CLUSTER_ROBUST = "cluster_robust"
    CONFORMAL = "conformal"
    BAYESIAN_POSTERIOR_DIAGNOSTIC = "bayesian_posterior_diagnostic"
    MAX_T = "max_t"
    STEPDOWN = "stepdown"
    NO_VALID_INFERENCE = "no_valid_inference"
    ALL = "all"


REQUIRED_DESIGN_FAMILIES = frozenset(DesignFamily)
REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)
REQUIRED_INFERENCE_FAMILIES = frozenset(InferenceFamily)


@dataclass(frozen=True)
class MethodFailureMode:
    failure_id: str
    name: str
    category: FailureModeCategory
    severity: FailureSeverity
    description: str
    observed_diagnostic_triggers: tuple[str, ...]
    dgp_triggers: tuple[str, ...]
    affected_design_families: tuple[DesignFamily, ...]
    affected_method_families: tuple[MethodFamily, ...]
    affected_inference_families: tuple[InferenceFamily, ...]
    required_actions: tuple[RequiredAction, ...]
    promotion_blocking: bool
    downstream_blocking: bool
    recommended_next_artifact: str | None
    notes: str


def _fm(
    failure_id: str,
    name: str,
    category: FailureModeCategory,
    severity: FailureSeverity,
    description: str,
    *,
    observed_diagnostic_triggers: tuple[str, ...],
    dgp_triggers: tuple[str, ...],
    affected_design_families: tuple[DesignFamily, ...],
    affected_method_families: tuple[MethodFamily, ...],
    affected_inference_families: tuple[InferenceFamily, ...],
    required_actions: tuple[RequiredAction, ...],
    promotion_blocking: bool = False,
    downstream_blocking: bool = False,
    recommended_next_artifact: str | None = None,
    notes: str = "",
) -> MethodFailureMode:
    return MethodFailureMode(
        failure_id=failure_id,
        name=name,
        category=category,
        severity=severity,
        description=description,
        observed_diagnostic_triggers=observed_diagnostic_triggers,
        dgp_triggers=dgp_triggers,
        affected_design_families=affected_design_families,
        affected_method_families=affected_method_families,
        affected_inference_families=affected_inference_families,
        required_actions=required_actions,
        promotion_blocking=promotion_blocking,
        downstream_blocking=downstream_blocking,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_ALL_D = (DesignFamily.ALL,)
_ALL_M = (MethodFamily.ALL,)
_ALL_I = (InferenceFamily.ALL,)
_BLK = (RequiredAction.BLOCK,)

def _design_assignment_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-DA-001", "unknown_assignment_mechanism", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.HARD_BLOCKER,
            "Unknown assignment blocks design-based randomization and placebo validity.",
            observed_diagnostic_triggers=("OPD-AD-001",), dgp_triggers=("DGP-AD-009", "DGP-INF-002"),
            affected_design_families=(DesignFamily.UNKNOWN_ASSIGNMENT,), affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DA-002", "deterministic_assignment_as_randomized", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.HARD_BLOCKER,
            "Deterministic assignment invalidates randomization inference without falsification contract.",
            observed_diagnostic_triggers=("OPD-AD-002",), dgp_triggers=("DGP-AD-008",),
            affected_design_families=(DesignFamily.FIXED_DETERMINISTIC,), affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DESIGN_STRESS_TEST),
            promotion_blocking=True),
        _fm("FM-DA-003", "missing_rerandomization_acceptance_rule", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Rerandomization without documented acceptance rule breaks null enumeration.",
            observed_diagnostic_triggers=("OPD-AD-006",), dgp_triggers=("DGP-AD-005",),
            affected_design_families=(DesignFamily.RERANDOMIZED,), affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.PERMUTATION),
            required_actions=(
                RequiredAction.REQUIRE_NULL_CALIBRATION,
                RequiredAction.REQUIRE_DESIGN_STRESS_TEST,
                RequiredAction.REQUIRE_METHOD_ADAPTER,
            ),
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"),
        _fm("FM-DA-004", "matched_pair_integrity_failure", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.HARD_BLOCKER,
            "Matched-pair integrity failure blocks pair-based inference.",
            observed_diagnostic_triggers=("OPD-AD-003",), dgp_triggers=("DGP-AD-002",),
            affected_design_families=(DesignFamily.MATCHED_PAIR,), affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.RANDOMIZATION,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DESIGN_STRESS_TEST),
            promotion_blocking=True,
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"),
        _fm("FM-DA-005", "matched_block_integrity_failure", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.HARD_BLOCKER,
            "Matched-block integrity failure undermines block randomization.",
            observed_diagnostic_triggers=("OPD-AD-004",), dgp_triggers=("DGP-AD-003",),
            affected_design_families=(DesignFamily.MATCHED_BLOCK,), affected_method_families=(MethodFamily.DID,),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.CLUSTER_ROBUST),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DESIGN_STRESS_TEST),
            promotion_blocking=True),
        _fm("FM-DA-006", "stratification_integrity_failure", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.SENSITIVITY_ONLY,
            "Stratification integrity failure requires sensitivity or stratum-specific analysis.",
            observed_diagnostic_triggers=("OPD-AD-005",), dgp_triggers=("DGP-AD-004",),
            affected_design_families=(DesignFamily.STRATIFIED,), affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
            affected_inference_families=(InferenceFamily.RANDOMIZATION,),
            required_actions=(RequiredAction.MARK_SENSITIVITY_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-DA-007", "small_assignment_support", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Small randomization support limits exact inference and placebo richness.",
            observed_diagnostic_triggers=("OPD-AD-009",), dgp_triggers=("DGP-AD-010",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(
                InferenceFamily.RANDOMIZATION,
                InferenceFamily.PERMUTATION,
                InferenceFamily.PLACEBO_RANK,
            ),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION),
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"),
        _fm("FM-DA-008", "degenerate_pseudo_assignment_support", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Degenerate pseudo-assignment support is falsification-only.",
            observed_diagnostic_triggers=("OPD-AD-010",), dgp_triggers=("DGP-AD-011",),
            affected_design_families=(DesignFamily.GREEDY_MATCHED_MARKET, DesignFamily.KERNEL_THINNING),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_DESIGN_STRESS_TEST),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"),
        _fm("FM-DA-009", "shared_control_dependence_ignored", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.HARD_BLOCKER,
            "Shared-control dependence ignored in multicell inference.",
            observed_diagnostic_triggers=("OPD-AD-008", "OPD-MC-001"), dgp_triggers=("DGP-MC-002",),
            affected_design_families=(DesignFamily.MULTICELL_SHARED_CONTROL,),
            affected_method_families=(MethodFamily.MULTICELL,),
            affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.SCOUT_NEW_METHOD),
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _fm("FM-DA-010", "multicell_winner_selection_risk_ignored", FailureModeCategory.DESIGN_ASSIGNMENT,
            FailureSeverity.HARD_BLOCKER,
            "Multicell winner-selection multiplicity risk ignored.",
            observed_diagnostic_triggers=("OPD-MC-003",), dgp_triggers=("DGP-MC-005",),
            affected_design_families=(DesignFamily.MULTICELL_SHARED_CONTROL, DesignFamily.MULTICELL_INDEPENDENT_CELLS),
            affected_method_families=(MethodFamily.MULTICELL,),
            affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT),
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
    )


def _panel_structure_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-PS-001", "duplicate_panel_rows", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.HARD_BLOCKER,
            "Duplicate panel rows break index integrity and inference validity.",
            observed_diagnostic_triggers=("OPD-PS-005",), dgp_triggers=("DGP-SS-008",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-PS-002", "missing_required_panel_keys", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.HARD_BLOCKER,
            "Missing unit/time/treatment/metric keys block all routing.",
            observed_diagnostic_triggers=("OPD-PS-002",), dgp_triggers=("DGP-SS-008",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-PS-003", "unbalanced_panel_without_handling", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Unbalanced panel without explicit handling risks biased bootstrap paths.",
            observed_diagnostic_triggers=("OPD-PS-003",), dgp_triggers=("DGP-SS-006",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE,),
            affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-PS-004", "short_pre_period", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.HARD_BLOCKER,
            "Short pre-period blocks SCM/DID pre-fit and trend diagnostics.",
            observed_diagnostic_triggers=("OPD-PS-006",), dgp_triggers=("DGP-SS-004",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-PS-005", "short_post_period", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.SENSITIVITY_ONLY,
            "Short post-period limits power and bootstrap stability.",
            observed_diagnostic_triggers=("OPD-PS-007",), dgp_triggers=("DGP-SS-005",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.MARK_SENSITIVITY_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-PS-006", "too_few_treated_units", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Too few treated units restricts placebo and multicell routing.",
            observed_diagnostic_triggers=("OPD-PS-008",), dgp_triggers=("DGP-SS-002",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO, DesignFamily.MULTI_TREATED_GEO),
            affected_method_families=(MethodFamily.SCM, MethodFamily.MULTICELL),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.MAX_T),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_DESIGN_STRESS_TEST),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"),
        _fm("FM-PS-007", "too_few_donor_control_units", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.HARD_BLOCKER,
            "Too few donor/control units blocks SCM/AugSynth support.",
            observed_diagnostic_triggers=("OPD-PS-009",), dgp_triggers=("DGP-SS-003",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.SCOUT_NEW_METHOD),
            promotion_blocking=True),
        _fm("FM-PS-008", "small_n_panel_overclaim", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Small-N panel overclaim risks asymptotic inference misuse.",
            observed_diagnostic_triggers=("OPD-PS-011",), dgp_triggers=("DGP-SS-001",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE),
            recommended_next_artifact="SIMULATION_DGP_COVERAGE_PLAN_001"),
        _fm("FM-PS-009", "high_missingness", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.REMEDIATION_REQUIRED,
            "High panel missingness without imputation contract risks biased estimates.",
            observed_diagnostic_triggers=("OPD-PS-004",), dgp_triggers=("DGP-SS-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.AUGSYNTH_CVXPY, MethodFamily.SCM),
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS)),
        _fm("FM-PS-010", "panel_index_leakage", FailureModeCategory.PANEL_STRUCTURE,
            FailureSeverity.HARD_BLOCKER,
            "Panel index leakage from duplicate or non-unique keys corrupts inference.",
            observed_diagnostic_triggers=("OPD-PS-001",), dgp_triggers=("DGP-SS-008",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True, downstream_blocking=True),
    )


def _donor_support_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-DS-001", "donor_pool_too_small", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.HARD_BLOCKER,
            "Donor pool too small for stable SCM weights and placebo richness.",
            observed_diagnostic_triggers=("OPD-DS-001",), dgp_triggers=("DGP-DS-001",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.SCOUT_NEW_METHOD),
            promotion_blocking=True),
        _fm("FM-DS-002", "donor_eligibility_invalid", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.HARD_BLOCKER,
            "Ineligible donors in pool corrupt counterfactual support.",
            observed_diagnostic_triggers=("OPD-DS-002",), dgp_triggers=("DGP-DS-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-DS-003", "treated_outside_donor_range", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.HARD_BLOCKER,
            "Treated unit outside donor range blocks SCM extrapolation.",
            observed_diagnostic_triggers=("OPD-DS-003", "OPD-DS-008"), dgp_triggers=("DGP-DS-004",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM,),
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-DS-004", "donor_hull_violation", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.HARD_BLOCKER,
            "Donor convex hull violation blocks SCM/AugSynth promotion.",
            observed_diagnostic_triggers=("OPD-DS-003",), dgp_triggers=("DGP-DS-003",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_NULL_CALIBRATION),
            promotion_blocking=True),
        _fm("FM-DS-005", "weak_pre_period_overlap", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.SENSITIVITY_ONLY,
            "Weak pre-period covariate overlap requires sensitivity analysis.",
            observed_diagnostic_triggers=("OPD-DS-004", "OPD-DS-005"), dgp_triggers=("DGP-DS-002",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.RANDOMIZATION),
            required_actions=(RequiredAction.MARK_SENSITIVITY_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-DS-006", "scm_donor_weight_degeneracy", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.HARD_BLOCKER,
            "SCM donor weight degeneracy blocks stable inference.",
            observed_diagnostic_triggers=("OPD-DS-006",), dgp_triggers=("DGP-DS-005",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM,),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_NULL_CALIBRATION),
            promotion_blocking=True),
        _fm("FM-DS-007", "augsynth_extrapolation_instability", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.REMEDIATION_REQUIRED,
            "AugSynth extrapolation beyond donor hull elevates miscalibration risk.",
            observed_diagnostic_triggers=("OPD-DS-007",), dgp_triggers=("DGP-DS-006", "DGP-ES-004"),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.JACKKNIFE),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-DS-008", "support_mismatch_ignored", FailureModeCategory.DONOR_SUPPORT,
            FailureSeverity.HARD_BLOCKER,
            "Support mismatch ignored for SCM/AugSynth promotion.",
            observed_diagnostic_triggers=("OPD-DS-008",), dgp_triggers=("DGP-DS-007",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
    )


def _pre_period_fit_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-PF-001", "poor_pre_period_fit", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.HARD_BLOCKER,
            "Poor pre-period fit blocks SCM/AugSynth counterfactual claims.",
            observed_diagnostic_triggers=("OPD-PF-001",), dgp_triggers=("DGP-ES-002",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY, MethodFamily.SYNTHETIC_DID),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_NULL_CALIBRATION),
            promotion_blocking=True),
        _fm("FM-PF-002", "pre_period_residual_bias", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.SENSITIVITY_ONLY,
            "Pre-period residual bias signals misspecification requiring sensitivity.",
            observed_diagnostic_triggers=("OPD-PF-002",), dgp_triggers=("DGP-TS-004",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.TBRRIDGE),
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.MARK_SENSITIVITY_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-PF-003", "parallel_trends_violation", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.HARD_BLOCKER,
            "Parallel trends violation blocks DID and synthetic-DID promotion.",
            observed_diagnostic_triggers=("OPD-PF-003",), dgp_triggers=("DGP-ES-006",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-PF-004", "trend_break_near_treatment", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Trend break near treatment undermines counterfactual extrapolation.",
            observed_diagnostic_triggers=("OPD-PF-004",), dgp_triggers=("DGP-TS-004",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID, MethodFamily.TBRRIDGE),
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-PF-005", "baseline_nonstationarity", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.SENSITIVITY_ONLY,
            "Nonstationary baseline requires detrending or restricted inference.",
            observed_diagnostic_triggers=("OPD-PF-005",), dgp_triggers=("DGP-TS-005",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.MARK_SENSITIVITY_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-PF-006", "pre_period_shock_sensitivity", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Pre-period shock sensitivity requires leave-one-period stability checks.",
            observed_diagnostic_triggers=("OPD-PF-006",), dgp_triggers=("DGP-TS-002",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS)),
        _fm("FM-PF-007", "leave_last_pre_period_instability", FailureModeCategory.PRE_PERIOD_FIT_TRENDS,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Leave-last-pre-period instability gates short-pre designs.",
            observed_diagnostic_triggers=("OPD-PF-007",), dgp_triggers=("DGP-SS-004",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION)),
    )


def _temporal_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-TD-001", "autocorrelation_ignored", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Autocorrelation ignored invalidates IID bootstrap nulls.",
            observed_diagnostic_triggers=("OPD-TD-001",), dgp_triggers=("DGP-NV-005", "DGP-INF-006"),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.ALL),
            affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _fm("FM-TD-002", "seasonality_ignored", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.SENSITIVITY_ONLY,
            "Seasonality ignored without calendar adjustment stress.",
            observed_diagnostic_triggers=("OPD-TD-002",), dgp_triggers=("DGP-TS-001",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.MARK_SENSITIVITY_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-TD-003", "holiday_promo_shock_ignored", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Holiday/promo shocks require explicit shock annotation and sensitivity.",
            observed_diagnostic_triggers=("OPD-TD-003",), dgp_triggers=("DGP-TS-002",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.RANDOMIZATION),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS)),
        _fm("FM-TD-004", "outlier_week_drives_result", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Outlier week driving result requires robustness diagnostics.",
            observed_diagnostic_triggers=("OPD-TD-004",), dgp_triggers=("DGP-NV-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-TD-005", "level_shift_misclassified_as_treatment", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.HARD_BLOCKER,
            "Level shift misclassified as treatment effect inflates false positives.",
            observed_diagnostic_triggers=("OPD-TD-005",), dgp_triggers=("DGP-TS-003",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.PLACEBO_RANK),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-TD-006", "time_varying_variance_ignored", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Time-varying variance ignored undermines studentized statistics.",
            observed_diagnostic_triggers=("OPD-TD-006",), dgp_triggers=("DGP-NV-003",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.STUDENTIZED_PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-TD-007", "metric_lag_delay_mismatch", FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Metric lag/delay mismatch between treatment and outcome read.",
            observed_diagnostic_triggers=("OPD-TD-007",), dgp_triggers=("DGP-TS-007", "DGP-TE-006"),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.RANDOMIZATION,),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_DESIGN_STRESS_TEST)),
    )


def _outcome_metric_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-OM-001", "invalid_log_transform", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.HARD_BLOCKER,
            "Invalid log transform on non-positive outcomes blocks log-scale models.",
            observed_diagnostic_triggers=("OPD-OM-008",), dgp_triggers=("DGP-OS-009",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-OM-002", "negative_outcome_under_log_model", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.HARD_BLOCKER,
            "Negative outcome values under log model invalidate inference.",
            observed_diagnostic_triggers=("OPD-OM-008",), dgp_triggers=("DGP-OS-009",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
            affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-OM-003", "sparse_count_as_gaussian", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.HARD_BLOCKER,
            "Sparse count treated as Gaussian without appropriate diagnostics.",
            observed_diagnostic_triggers=("OPD-OM-001", "OPD-OM-003"), dgp_triggers=("DGP-OS-004",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.CONFORMAL),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-OM-004", "zero_inflation_ignored", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Zero inflation ignored on count/conversion metrics.",
            observed_diagnostic_triggers=("OPD-OM-002",), dgp_triggers=("DGP-OS-005",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-OM-005", "binary_binomial_as_continuous", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.HARD_BLOCKER,
            "Binary/binomial outcome treated as continuous without diagnostic.",
            observed_diagnostic_triggers=("OPD-OM-004",), dgp_triggers=("DGP-OS-006",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID,),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-OM-006", "rate_denominator_missing", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.HARD_BLOCKER,
            "Rate metric denominator missing invalidates rate estimand.",
            observed_diagnostic_triggers=("OPD-OM-009", "OPD-OM-010"), dgp_triggers=("DGP-OS-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID,),
            affected_inference_families=(InferenceFamily.RANDOMIZATION,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-OM-007", "heavy_tailed_revenue_not_stress_tested", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Heavy-tailed revenue outcome not stress tested before promotion.",
            observed_diagnostic_triggers=("OPD-OM-005",), dgp_triggers=("DGP-OS-008",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBR, MethodFamily.TBRRIDGE),
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-OM-008", "scale_estimand_mismatch", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Scale/estimand mismatch between outcome and estimator routing.",
            observed_diagnostic_triggers=("OPD-OM-007",), dgp_triggers=("DGP-TE-003",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT)),
        _fm("FM-OM-009", "metric_definition_drift", FailureModeCategory.OUTCOME_METRIC,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Metric definition drift across pre/post periods undermines comparability.",
            observed_diagnostic_triggers=("OPD-OM-007",), dgp_triggers=("DGP-OS-001",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS)),
    )


def _treatment_exposure_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-TE-001", "treatment_timing_inconsistent", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.HARD_BLOCKER,
            "Inconsistent treatment timing breaks staggered-DID routing.",
            observed_diagnostic_triggers=("OPD-AD-007",), dgp_triggers=("DGP-TE-008",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
            affected_inference_families=(InferenceFamily.RANDOMIZATION,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-TE-002", "partial_compliance_ignored", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Partial compliance ignored creates estimand ambiguity.",
            observed_diagnostic_triggers=("OPD-TE-004",), dgp_triggers=("DGP-TE-009",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID,),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT)),
        _fm("FM-TE-003", "dose_variation_ignored", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Dose variation ignored when dose-response estimand claimed.",
            observed_diagnostic_triggers=("OPD-TE-001", "OPD-TE-002"), dgp_triggers=("DGP-TE-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE,),
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-TE-004", "staggered_activation_ignored", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Staggered activation ignored in DID event-study routing.",
            observed_diagnostic_triggers=("OPD-TE-005",), dgp_triggers=("DGP-TE-008",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.CLUSTER_ROBUST),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-TE-005", "cross_cell_contamination", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.HARD_BLOCKER,
            "Cross-cell contamination invalidates per-cell causal claims.",
            observed_diagnostic_triggers=("OPD-TE-008", "OPD-TE-006"), dgp_triggers=("DGP-IS-003",),
            affected_design_families=(DesignFamily.MULTICELL_SHARED_CONTROL,),
            affected_method_families=(MethodFamily.MULTICELL,),
            affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.SCOUT_NEW_METHOD),
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _fm("FM-TE-006", "donor_contamination", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Donor contamination from treated spillover biases SCM counterfactual.",
            observed_diagnostic_triggers=("OPD-TE-006",), dgp_triggers=("DGP-IS-005",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-TE-007", "national_media_spillover", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.RESTRICTED_RESEARCH,
            "National media spillover requires research-scout handling.",
            observed_diagnostic_triggers=("OPD-TE-007",), dgp_triggers=("DGP-IS-004",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.SCOUT_NEW_METHOD)),
        _fm("FM-TE-008", "neighbor_spillover", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.HARD_BLOCKER,
            "Neighbor spillover violates no-interference for geo causal claims.",
            observed_diagnostic_triggers=("OPD-TE-007",), dgp_triggers=("DGP-IS-002",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-TE-009", "exposure_leakage", FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Partial exposure leakage requires diagnostic boundary labeling.",
            observed_diagnostic_triggers=("OPD-TE-008",), dgp_triggers=("DGP-IS-006",),
            affected_design_families=(DesignFamily.MULTICELL_SHARED_CONTROL,),
            affected_method_families=(MethodFamily.MULTICELL,),
            affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS)),
    )


def _estimator_specific_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-ES-001", "scm_promoted_despite_poor_support", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.HARD_BLOCKER,
            "SCM promoted despite poor donor support and pre-fit.",
            observed_diagnostic_triggers=("OPD-DS-008", "OPD-PF-001"), dgp_triggers=("DGP-ES-002",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM,),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_NULL_CALIBRATION),
            promotion_blocking=True),
        _fm("FM-ES-002", "scm_placebo_rank_overinterpreted", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "SCM placebo rank overinterpreted as production p-value.",
            observed_diagnostic_triggers=("OPD-IR-002",), dgp_triggers=("DGP-INF-003",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM,),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-ES-003", "augsynth_point_without_calibrated_inference", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "AugSynth point estimate promoted without calibrated inference.",
            observed_diagnostic_triggers=("OPD-ER-002",), dgp_triggers=("DGP-ES-003",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.JACKKNIFE),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_METHOD_ADAPTER)),
        _fm("FM-ES-004", "augsynth_augmentation_unstable", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.RETIRE_OR_REPLACE,
            "AugSynth augmentation unstable; jackknife path diagnostic/retire.",
            observed_diagnostic_triggers=("OPD-DS-007",), dgp_triggers=("DGP-ES-004",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
            affected_inference_families=(InferenceFamily.JACKKNIFE, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.RETIRE_OR_REPLACE, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-ES-005", "did_despite_trend_violation", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.HARD_BLOCKER,
            "DID used despite parallel trends violation.",
            observed_diagnostic_triggers=("OPD-PF-003",), dgp_triggers=("DGP-ES-006",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.DID,),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-ES-006", "tbrridge_regularization_masks_instability", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "TBRRidge regularization masks underlying relation instability.",
            observed_diagnostic_triggers=("OPD-ER-004",), dgp_triggers=("DGP-ES-008",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE,),
            affected_inference_families=(InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP, InferenceFamily.BOOTSTRAP),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_NULL_CALIBRATION),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _fm("FM-ES-007", "tbr_aggregate_overclaim", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.RETIRE_OR_REPLACE,
            "TBR aggregate geometry overclaim blocked by combination guardrails.",
            observed_diagnostic_triggers=("OPD-ER-005",), dgp_triggers=("DGP-OS-002",),
            affected_design_families=(DesignFamily.MULTI_TREATED_GEO,), affected_method_families=(MethodFamily.TBR,),
            affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.NO_VALID_INFERENCE),
            required_actions=(RequiredAction.RETIRE_OR_REPLACE, RequiredAction.BLOCK),
            promotion_blocking=True),
        _fm("FM-ES-008", "bayesian_tbr_posterior_as_causal_ci", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.HARD_BLOCKER,
            "Bayesian TBR posterior interval treated as causal confidence interval.",
            observed_diagnostic_triggers=("OPD-ER-006", "OPD-IR-008"), dgp_triggers=("DGP-ES-009", "DGP-INF-010"),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.BAYESIAN_TBR,),
            affected_inference_families=(InferenceFamily.BAYESIAN_POSTERIOR_DIAGNOSTIC,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.MARK_DIAGNOSTIC_ONLY),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-ES-009", "synthetic_did_missing_balance_stress", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Synthetic DID missing balance stress before promotion.",
            observed_diagnostic_triggers=("OPD-ER-007",), dgp_triggers=("DGP-ES-010",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SYNTHETIC_DID,),
            affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE)),
        _fm("FM-ES-010", "trop_research_as_production", FailureModeCategory.ESTIMATOR_SPECIFIC,
            FailureSeverity.RETIRE_OR_REPLACE,
            "TROP research path treated as production candidate.",
            observed_diagnostic_triggers=("OPD-ER-008",), dgp_triggers=("DGP-ES-011",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TROP,),
            affected_inference_families=(InferenceFamily.CONFORMAL,),
            required_actions=(RequiredAction.RETIRE_OR_REPLACE, RequiredAction.KEEP_RESEARCH_ONLY)),
    )


def _inference_specific_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-INF-001", "placebo_rank_as_production_pvalue", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Placebo rank treated as production p-value without calibrated semantics.",
            observed_diagnostic_triggers=("OPD-IR-002",), dgp_triggers=("DGP-INF-003",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-INF-002", "studentized_placebo_without_null_calibration", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.DIAGNOSTIC_ONLY,
            "Studentized placebo used without null calibration.",
            observed_diagnostic_triggers=("OPD-IR-003",), dgp_triggers=("DGP-INF-004",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
            affected_inference_families=(InferenceFamily.STUDENTIZED_PLACEBO_RANK,),
            required_actions=(RequiredAction.MARK_DIAGNOSTIC_ONLY, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-INF-003", "bootstrap_under_invalid_dependence", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Bootstrap used under serial dependence without block bootstrap.",
            observed_diagnostic_triggers=("OPD-TD-001", "OPD-IR-004"), dgp_triggers=("DGP-INF-006",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE,),
            affected_inference_families=(InferenceFamily.BOOTSTRAP,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_DGP_COVERAGE),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _fm("FM-INF-004", "block_residual_bootstrap_without_validation", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Block residual bootstrap used without dependence validation.",
            observed_diagnostic_triggers=("OPD-IR-004",), dgp_triggers=("DGP-INF-006",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE,),
            affected_inference_families=(InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_NULL_CALIBRATION)),
        _fm("FM-INF-005", "jackknife_treated_as_causal_ci", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.RETIRE_OR_REPLACE,
            "Jackknife treated as causal confidence interval; TBRRidge JK known failure.",
            observed_diagnostic_triggers=("OPD-IR-005",), dgp_triggers=("DGP-INF-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.JACKKNIFE,),
            required_actions=(RequiredAction.RETIRE_OR_REPLACE, RequiredAction.MARK_SENSITIVITY_ONLY),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _fm("FM-INF-006", "cluster_robust_too_few_clusters", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Cluster-robust inference with too few clusters.",
            observed_diagnostic_triggers=("OPD-IR-006",), dgp_triggers=("DGP-INF-008",),
            affected_design_families=(DesignFamily.MATCHED_BLOCK, DesignFamily.MULTICELL_SHARED_CONTROL),
            affected_method_families=(MethodFamily.DID, MethodFamily.MULTICELL),
            affected_inference_families=(InferenceFamily.CLUSTER_ROBUST,),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT)),
        _fm("FM-INF-007", "conformal_without_panel_validity", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Conformal interval used without panel validity review.",
            observed_diagnostic_triggers=("OPD-IR-007",), dgp_triggers=("DGP-INF-009",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TROP,),
            affected_inference_families=(InferenceFamily.CONFORMAL,),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT)),
        _fm("FM-INF-008", "posterior_diagnostic_as_causal_uncertainty", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.HARD_BLOCKER,
            "Posterior diagnostic treated as causal uncertainty quantification.",
            observed_diagnostic_triggers=("OPD-IR-008",), dgp_triggers=("DGP-INF-010",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.BAYESIAN_TBR,),
            affected_inference_families=(InferenceFamily.BAYESIAN_POSTERIOR_DIAGNOSTIC,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.MARK_DIAGNOSTIC_ONLY),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-INF-009", "max_t_multiplicity_ignored", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.HARD_BLOCKER,
            "Max-T multiplicity correction ignored in multicell settings.",
            observed_diagnostic_triggers=("OPD-IR-009", "OPD-MC-004"), dgp_triggers=("DGP-INF-011", "DGP-MC-007"),
            affected_design_families=(DesignFamily.MULTICELL_SHARED_CONTROL, DesignFamily.MULTICELL_INDEPENDENT_CELLS),
            affected_method_families=(MethodFamily.MULTICELL,),
            affected_inference_families=(InferenceFamily.MAX_T,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.SCOUT_NEW_METHOD),
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _fm("FM-INF-010", "stepdown_multiplicity_ignored", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.RESTRICTED_RESEARCH,
            "Stepdown multiplicity correction ignored for multicell arms.",
            observed_diagnostic_triggers=("OPD-IR-009",), dgp_triggers=("DGP-INF-012",),
            affected_design_families=(DesignFamily.MULTICELL_INDEPENDENT_CELLS,),
            affected_method_families=(MethodFamily.MULTICELL,),
            affected_inference_families=(InferenceFamily.STEPDOWN,),
            required_actions=(RequiredAction.KEEP_RESEARCH_ONLY, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT),
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _fm("FM-INF-011", "no_valid_inference_promoted", FailureModeCategory.INFERENCE_SPECIFIC,
            FailureSeverity.HARD_BLOCKER,
            "No-valid-inference case promoted to production path.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True, downstream_blocking=True),
    )


def _calibration_promotion_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-CP-001", "null_calibration_missing", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Promotion attempted without null calibration evidence.",
            observed_diagnostic_triggers=("OPD-IR-001",), dgp_triggers=("DGP-NB-001", "DGP-TE-001"),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_NULL_CALIBRATION),
            promotion_blocking=True),
        _fm("FM-CP-002", "dgp_coverage_missing", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Promotion attempted without required DGP coverage.",
            observed_diagnostic_triggers=("OPD-PS-010",), dgp_triggers=("DGP-NB-003",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_DGP_COVERAGE),
            promotion_blocking=True),
        _fm("FM-CP-003", "observed_diagnostics_missing", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Method selection without observed-panel diagnostics.",
            observed_diagnostic_triggers=("OPD-PS-002",), dgp_triggers=("DGP-SS-008",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-CP-004", "failure_mode_registry_not_consulted", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Promotion attempted without consulting failure-mode registry.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS),
            promotion_blocking=True),
        _fm("FM-CP-005", "literature_alignment_missing", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Promotion without literature alignment audit.",
            observed_diagnostic_triggers=("OPD-ER-009",), dgp_triggers=("DGP-MC-006",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_LITERATURE_ALIGNMENT)),
        _fm("FM-CP-006", "method_specific_adapter_missing", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.REMEDIATION_REQUIRED,
            "Promotion without method-specific statistic adapter contract.",
            observed_diagnostic_triggers=("OPD-ER-001",), dgp_triggers=("DGP-ES-001",),
            affected_design_families=(DesignFamily.SINGLE_TREATED_GEO,),
            affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.STUDENTIZED_PLACEBO_RANK),
            required_actions=(RequiredAction.REMEDIATE, RequiredAction.REQUIRE_METHOD_ADAPTER)),
        _fm("FM-CP-007", "promotion_with_diagnostic_only_status", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Promotion attempted while path remains diagnostic-only.",
            observed_diagnostic_triggers=("OPD-IR-005",), dgp_triggers=("DGP-INF-007",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
            affected_inference_families=(InferenceFamily.JACKKNIFE,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.MARK_DIAGNOSTIC_ONLY),
            promotion_blocking=True),
        _fm("FM-CP-008", "promotion_with_research_only_status", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Promotion attempted while path remains research-only.",
            observed_diagnostic_triggers=("OPD-PS-011",), dgp_triggers=("DGP-ES-011",),
            affected_design_families=_ALL_D, affected_method_families=(MethodFamily.TROP,),
            affected_inference_families=(InferenceFamily.CONFORMAL,),
            required_actions=(RequiredAction.BLOCK, RequiredAction.KEEP_RESEARCH_ONLY),
            promotion_blocking=True),
        _fm("FM-CP-009", "promotion_with_blocked_status", FailureModeCategory.CALIBRATION_PROMOTION,
            FailureSeverity.HARD_BLOCKER,
            "Promotion attempted while combination status is blocked.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=(DesignFamily.UNKNOWN_ASSIGNMENT,),
            affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
    )


def _downstream_boundary_rows() -> tuple[MethodFailureMode, ...]:
    return (
        _fm("FM-DB-001", "trustreport_authorization_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "TrustReport authorization attempted before method control complete.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-002", "calibration_signal_generation_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "CalibrationSignal generation attempted without promotion gate.",
            observed_diagnostic_triggers=("OPD-IR-001",), dgp_triggers=("DGP-TE-001",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK, RequiredAction.REQUIRE_NULL_CALIBRATION),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-003", "mmm_ingestion_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "MMM ingestion attempted before method validation complete.",
            observed_diagnostic_triggers=("OPD-OM-007",), dgp_triggers=("DGP-OS-001",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-004", "llm_decisioning_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "LLM decisioning attempted on unvalidated causal outputs.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-005", "production_decisioning_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "Production decisioning attempted without control-layer clearance.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-006", "live_api_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "Live API authorization attempted before method lane complete.",
            observed_diagnostic_triggers=("OPD-PS-002",), dgp_triggers=("DGP-SS-008",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-007", "scheduler_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "Scheduler authorization attempted for unvalidated method paths.",
            observed_diagnostic_triggers=("OPD-IR-010",), dgp_triggers=("DGP-INF-013",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-008", "budget_optimization_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "Budget optimization attempted on unvalidated causal estimates.",
            observed_diagnostic_triggers=("OPD-TE-003",), dgp_triggers=("DGP-TE-001",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=_ALL_I,
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-009", "production_pvalue_authorization_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "Production p-value authorization attempted.",
            observed_diagnostic_triggers=("OPD-IR-002",), dgp_triggers=("DGP-INF-003",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.RANDOMIZATION),
            required_actions=(RequiredAction.BLOCK, RequiredAction.MARK_DIAGNOSTIC_ONLY),
            promotion_blocking=True, downstream_blocking=True),
        _fm("FM-DB-010", "causal_ci_authorization_attempted", FailureModeCategory.DOWNSTREAM_BOUNDARY,
            FailureSeverity.HARD_BLOCKER,
            "Causal confidence interval authorization attempted.",
            observed_diagnostic_triggers=("OPD-IR-005",), dgp_triggers=("DGP-INF-007",),
            affected_design_families=_ALL_D, affected_method_families=_ALL_M,
            affected_inference_families=(InferenceFamily.JACKKNIFE, InferenceFamily.BOOTSTRAP),
            required_actions=(RequiredAction.BLOCK,),
            promotion_blocking=True, downstream_blocking=True),
    )


def build_method_failure_mode_registry() -> tuple[MethodFailureMode, ...]:
    """Build the full method failure-mode registry."""
    return (
        *_design_assignment_rows(),
        *_panel_structure_rows(),
        *_donor_support_rows(),
        *_pre_period_fit_rows(),
        *_temporal_rows(),
        *_outcome_metric_rows(),
        *_treatment_exposure_rows(),
        *_estimator_specific_rows(),
        *_inference_specific_rows(),
        *_calibration_promotion_rows(),
        *_downstream_boundary_rows(),
    )


def filter_method_failure_modes(
    failure_modes: tuple[MethodFailureMode, ...],
    *,
    category: FailureModeCategory | None = None,
    severity: FailureSeverity | None = None,
    action: RequiredAction | None = None,
    design_family: DesignFamily | None = None,
    method_family: MethodFamily | None = None,
    inference_family: InferenceFamily | None = None,
    promotion_blocking: bool | None = None,
    downstream_blocking: bool | None = None,
) -> tuple[MethodFailureMode, ...]:
    """Filter failure modes by optional predicates."""
    filtered: list[MethodFailureMode] = []
    for fm in failure_modes:
        if category is not None and fm.category != category:
            continue
        if severity is not None and fm.severity != severity:
            continue
        if action is not None and action not in fm.required_actions:
            continue
        if design_family is not None and design_family not in fm.affected_design_families:
            continue
        if method_family is not None and method_family not in fm.affected_method_families:
            continue
        if inference_family is not None and inference_family not in fm.affected_inference_families:
            continue
        if promotion_blocking is not None and fm.promotion_blocking != promotion_blocking:
            continue
        if downstream_blocking is not None and fm.downstream_blocking != downstream_blocking:
            continue
        filtered.append(fm)
    return tuple(filtered)


def validate_method_failure_mode_registry(
    failure_modes: tuple[MethodFailureMode, ...],
) -> dict[str, Any]:
    """Validate failure-mode registry invariants and return structured validation summary."""
    issues: list[str] = []
    failure_ids = [fm.failure_id for fm in failure_modes]

    if len(failure_ids) != len(set(failure_ids)):
        issues.append("duplicate failure_id detected")
    if len(failure_modes) < 100:
        issues.append(f"failure_mode_count {len(failure_modes)} < 100")

    category_counts = Counter(fm.category for fm in failure_modes)
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        if category_counts.get(cat, 0) < minimum:
            issues.append(f"category {cat.value} count {category_counts.get(cat, 0)} < {minimum}")

    severity_counts = Counter(fm.severity for fm in failure_modes)
    for sev, minimum in MIN_SEVERITY_COUNTS.items():
        if severity_counts.get(sev, 0) < minimum:
            issues.append(f"severity {sev.value} count {severity_counts.get(sev, 0)} < {minimum}")

    action_counts = Counter(action for fm in failure_modes for action in fm.required_actions)
    for action, minimum in MIN_ACTION_COUNTS.items():
        if action_counts.get(action, 0) < minimum:
            issues.append(f"action {action.value} count {action_counts.get(action, 0)} < {minimum}")

    design_present: set[DesignFamily] = set()
    method_present: set[MethodFamily] = set()
    inference_present: set[InferenceFamily] = set()
    for fm in failure_modes:
        design_present.update(fm.affected_design_families)
        method_present.update(fm.affected_method_families)
        inference_present.update(fm.affected_inference_families)

    missing_design = sorted(REQUIRED_DESIGN_FAMILIES - design_present, key=lambda d: d.value)
    if missing_design:
        issues.append(f"missing design families: {[d.value for d in missing_design]}")

    missing_methods = sorted(REQUIRED_METHOD_FAMILIES - method_present, key=lambda m: m.value)
    if missing_methods:
        issues.append(f"missing method families: {[m.value for m in missing_methods]}")

    missing_inference = sorted(REQUIRED_INFERENCE_FAMILIES - inference_present, key=lambda i: i.value)
    if missing_inference:
        issues.append(f"missing inference families: {[i.value for i in missing_inference]}")

    for fm in failure_modes:
        if not fm.observed_diagnostic_triggers:
            issues.append(f"{fm.failure_id} empty observed_diagnostic_triggers")
        if not fm.dgp_triggers:
            issues.append(f"{fm.failure_id} empty dgp_triggers")
        if not fm.affected_design_families:
            issues.append(f"{fm.failure_id} empty affected_design_families")
        if not fm.affected_method_families:
            issues.append(f"{fm.failure_id} empty affected_method_families")
        if not fm.affected_inference_families:
            issues.append(f"{fm.failure_id} empty affected_inference_families")
        if not fm.required_actions:
            issues.append(f"{fm.failure_id} empty required_actions")

    promotion_blockers = [fm for fm in failure_modes if fm.promotion_blocking]
    downstream_blockers = [fm for fm in failure_modes if fm.downstream_blocking]
    hard_blockers = [fm for fm in failure_modes if fm.severity == FailureSeverity.HARD_BLOCKER]
    diagnostic_only = [fm for fm in failure_modes if fm.severity == FailureSeverity.DIAGNOSTIC_ONLY]
    sensitivity_only = [fm for fm in failure_modes if fm.severity == FailureSeverity.SENSITIVITY_ONLY]
    remediation = [fm for fm in failure_modes if fm.severity == FailureSeverity.REMEDIATION_REQUIRED]
    retire = [fm for fm in failure_modes if fm.severity == FailureSeverity.RETIRE_OR_REPLACE]
    scout = [fm for fm in failure_modes if RequiredAction.SCOUT_NEW_METHOD in fm.required_actions]

    if not promotion_blockers:
        issues.append("no promotion blockers defined")
    if not downstream_blockers:
        issues.append("no downstream blockers defined")
    if not hard_blockers:
        issues.append("no hard blockers defined")
    if not diagnostic_only:
        issues.append("no diagnostic-only paths defined")
    if not sensitivity_only:
        issues.append("no sensitivity-only paths defined")
    if not remediation:
        issues.append("no remediation paths defined")
    if not retire:
        issues.append("no retire-or-replace paths defined")
    if not scout:
        issues.append("no scout-new-method paths defined")

    observed_linked = all(fm.observed_diagnostic_triggers for fm in failure_modes)
    dgp_linked = all(fm.dgp_triggers for fm in failure_modes)

    return {
        "valid": not issues,
        "failure_mode_count": len(failure_modes),
        "unique_failure_ids": len(failure_ids) == len(set(failure_ids)),
        "category_counts": {cat.value: category_counts.get(cat, 0) for cat in FailureModeCategory},
        "severity_counts": {sev.value: severity_counts.get(sev, 0) for sev in FailureSeverity},
        "required_action_counts": {act.value: action_counts.get(act, 0) for act in RequiredAction},
        "design_assignment_covered": category_counts.get(FailureModeCategory.DESIGN_ASSIGNMENT, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.DESIGN_ASSIGNMENT],
        "panel_structure_covered": category_counts.get(FailureModeCategory.PANEL_STRUCTURE, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.PANEL_STRUCTURE],
        "donor_support_covered": category_counts.get(FailureModeCategory.DONOR_SUPPORT, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.DONOR_SUPPORT],
        "pre_period_fit_trends_covered": category_counts.get(FailureModeCategory.PRE_PERIOD_FIT_TRENDS, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.PRE_PERIOD_FIT_TRENDS],
        "temporal_dependence_shocks_covered": category_counts.get(FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.TEMPORAL_DEPENDENCE_SHOCKS],
        "outcome_metric_covered": category_counts.get(FailureModeCategory.OUTCOME_METRIC, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.OUTCOME_METRIC],
        "treatment_exposure_interference_covered": category_counts.get(FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.TREATMENT_EXPOSURE_INTERFERENCE],
        "estimator_specific_covered": category_counts.get(FailureModeCategory.ESTIMATOR_SPECIFIC, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.ESTIMATOR_SPECIFIC],
        "inference_specific_covered": category_counts.get(FailureModeCategory.INFERENCE_SPECIFIC, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.INFERENCE_SPECIFIC],
        "calibration_promotion_covered": category_counts.get(FailureModeCategory.CALIBRATION_PROMOTION, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.CALIBRATION_PROMOTION],
        "downstream_boundary_covered": category_counts.get(FailureModeCategory.DOWNSTREAM_BOUNDARY, 0) >= MIN_CATEGORY_COUNTS[FailureModeCategory.DOWNSTREAM_BOUNDARY],
        "hard_blockers_defined": bool(hard_blockers),
        "diagnostic_only_paths_defined": bool(diagnostic_only),
        "sensitivity_only_paths_defined": bool(sensitivity_only),
        "remediation_paths_defined": bool(remediation),
        "retire_or_replace_paths_defined": bool(retire),
        "promotion_blockers_defined": bool(promotion_blockers),
        "downstream_blockers_defined": bool(downstream_blockers),
        "observed_diagnostics_linked": observed_linked,
        "dgp_triggers_linked": dgp_linked,
        "issues": issues,
    }


def summarize_method_failure_mode_registry(
    failure_modes: tuple[MethodFailureMode, ...],
) -> dict[str, Any]:
    """Serialize method failure-mode registry summary for archives."""
    validation = validate_method_failure_mode_registry(failure_modes)
    design_family_counts: Counter[str] = Counter()
    method_family_counts: Counter[str] = Counter()
    inference_family_counts: Counter[str] = Counter()
    for fm in failure_modes:
        for family in fm.affected_design_families:
            design_family_counts[family.value] += 1
        for family in fm.affected_method_families:
            method_family_counts[family.value] += 1
        for inf in fm.affected_inference_families:
            inference_family_counts[inf.value] += 1

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "failure_mode_count": len(failure_modes),
        "failed_scenarios": validation.get("issues", []),
        "category_counts": validation["category_counts"],
        "severity_counts": validation["severity_counts"],
        "required_action_counts": validation["required_action_counts"],
        "design_family_counts": dict(design_family_counts),
        "method_family_counts": dict(method_family_counts),
        "inference_family_counts": dict(inference_family_counts),
        "design_assignment_covered": validation["design_assignment_covered"],
        "panel_structure_covered": validation["panel_structure_covered"],
        "donor_support_covered": validation["donor_support_covered"],
        "pre_period_fit_trends_covered": validation["pre_period_fit_trends_covered"],
        "temporal_dependence_shocks_covered": validation["temporal_dependence_shocks_covered"],
        "outcome_metric_covered": validation["outcome_metric_covered"],
        "treatment_exposure_interference_covered": validation["treatment_exposure_interference_covered"],
        "estimator_specific_covered": validation["estimator_specific_covered"],
        "inference_specific_covered": validation["inference_specific_covered"],
        "calibration_promotion_covered": validation["calibration_promotion_covered"],
        "downstream_boundary_covered": validation["downstream_boundary_covered"],
        "central_failure_mode_registry_required": True,
        "hard_blockers_defined": validation["hard_blockers_defined"],
        "diagnostic_only_paths_defined": validation["diagnostic_only_paths_defined"],
        "sensitivity_only_paths_defined": validation["sensitivity_only_paths_defined"],
        "remediation_paths_defined": validation["remediation_paths_defined"],
        "retire_or_replace_paths_defined": validation["retire_or_replace_paths_defined"],
        "future_promotion_must_consult_registry": True,
        "observed_diagnostics_linked": validation["observed_diagnostics_linked"],
        "dgp_triggers_linked": validation["dgp_triggers_linked"],
        "promotion_blockers_defined": validation["promotion_blockers_defined"],
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
    failure_modes = build_method_failure_mode_registry()
    validation = validate_method_failure_mode_registry(failure_modes)
    summary = summarize_method_failure_mode_registry(failure_modes)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("failure_modes_build_successfully", len(failure_modes) > 0))
    scenarios.append(_scenario("failure_mode_count_at_least_100", len(failure_modes) >= 100))
    scenarios.append(_scenario("failure_ids_unique", validation["unique_failure_ids"]))

    for cat in FailureModeCategory:
        key = f"{cat.value}_covered"
        scenarios.append(_scenario(key, validation.get(key, False)))

    for sev, minimum in MIN_SEVERITY_COUNTS.items():
        count = sum(1 for fm in failure_modes if fm.severity == sev)
        scenarios.append(_scenario(f"severity_{sev.value}_at_least_{minimum}", count >= minimum))

    for action, minimum in MIN_ACTION_COUNTS.items():
        count = sum(1 for fm in failure_modes for a in fm.required_actions if a == action)
        scenarios.append(_scenario(f"action_{action.value}_at_least_{minimum}", count >= minimum))

    scenarios.append(_scenario("central_failure_mode_registry_required", summary["central_failure_mode_registry_required"] is True))
    scenarios.append(_scenario("hard_blockers_defined", summary["hard_blockers_defined"] is True))
    scenarios.append(_scenario("diagnostic_only_paths_defined", summary["diagnostic_only_paths_defined"] is True))
    scenarios.append(_scenario("sensitivity_only_paths_defined", summary["sensitivity_only_paths_defined"] is True))
    scenarios.append(_scenario("remediation_paths_defined", summary["remediation_paths_defined"] is True))
    scenarios.append(_scenario("retire_or_replace_paths_defined", summary["retire_or_replace_paths_defined"] is True))
    scenarios.append(_scenario("future_promotion_must_consult_registry", summary["future_promotion_must_consult_registry"] is True))
    scenarios.append(_scenario("observed_diagnostics_linked", summary["observed_diagnostics_linked"] is True))
    scenarios.append(_scenario("dgp_triggers_linked", summary["dgp_triggers_linked"] is True))
    scenarios.append(_scenario("promotion_blockers_defined", summary["promotion_blockers_defined"] is True))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_design_assignment_generator_stress_tests_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    for family in REQUIRED_DESIGN_FAMILIES:
        present = any(family in fm.affected_design_families for fm in failure_modes)
        scenarios.append(_scenario(f"design_family_{family.value}_represented", present))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(family in fm.affected_method_families for fm in failure_modes)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    for inf in REQUIRED_INFERENCE_FAMILIES:
        present = any(inf in fm.affected_inference_families for fm in failure_modes)
        scenarios.append(_scenario(f"inference_family_{inf.value}_represented", present))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    failure_modes = build_method_failure_mode_registry()
    validation = validate_method_failure_mode_registry(failure_modes)
    summary = summarize_method_failure_mode_registry(failure_modes)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "failure_mode_count": len(failure_modes),
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
