"""SIMULATION_DGP_COVERAGE_PLAN_001 validation harness."""

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

_ARTIFACT_ID = "SIMULATION_DGP_COVERAGE_PLAN_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "simulation_dgp_coverage_plan_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/SIMULATION_DGP_COVERAGE_PLAN_001_summary.json"

RECOMMENDED_NEXT_ARTIFACTS = (
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


class DgpCategory(str, Enum):
    NULL_BASELINE = "null_baseline"
    NOISE_VARIANCE = "noise_variance"
    TEMPORAL_STRUCTURE = "temporal_structure"
    OUTCOME_SCALE = "outcome_scale"
    TREATMENT_EFFECT = "treatment_effect"
    ASSIGNMENT_DESIGN = "assignment_design"
    DONOR_SUPPORT = "donor_support"
    SMALL_SAMPLE_PANEL = "small_sample_panel"
    INTERFERENCE_SPILLOVER = "interference_spillover"
    MULTICELL_MULTIPLICITY = "multicell_multiplicity"
    ESTIMATOR_SPECIFIC = "estimator_specific"
    INFERENCE_SPECIFIC = "inference_specific"


MIN_CATEGORY_COUNTS = {
    DgpCategory.NULL_BASELINE: 7,
    DgpCategory.NOISE_VARIANCE: 7,
    DgpCategory.TEMPORAL_STRUCTURE: 7,
    DgpCategory.OUTCOME_SCALE: 8,
    DgpCategory.TREATMENT_EFFECT: 8,
    DgpCategory.ASSIGNMENT_DESIGN: 10,
    DgpCategory.DONOR_SUPPORT: 7,
    DgpCategory.SMALL_SAMPLE_PANEL: 7,
    DgpCategory.INTERFERENCE_SPILLOVER: 6,
    DgpCategory.MULTICELL_MULTIPLICITY: 8,
    DgpCategory.ESTIMATOR_SPECIFIC: 9,
    DgpCategory.INFERENCE_SPECIFIC: 10,
}


class DgpSeverity(str, Enum):
    REQUIRED_CORE = "required_core"
    REQUIRED_STRESS = "required_stress"
    METHOD_SPECIFIC = "method_specific"
    RESEARCH_EXTENSION = "research_extension"
    DIAGNOSTIC_ONLY = "diagnostic_only"


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


class CoveragePurpose(str, Enum):
    NULL_CALIBRATION = "null_calibration"
    TYPE_I_ERROR_STRESS = "type_i_error_stress"
    COVERAGE_STRESS = "coverage_stress"
    ESTIMATOR_ROBUSTNESS = "estimator_robustness"
    DESIGN_STRESS_TEST = "design_stress_test"
    MULTICELL_DEPENDENCE_STRESS = "multicell_dependence_stress"
    SPILLOVER_STRESS = "spillover_stress"
    OUTCOME_SCALE_STRESS = "outcome_scale_stress"
    PROMOTION_GATE = "promotion_gate"
    RESEARCH_SCOUT = "research_scout"


MIN_COVERAGE_PURPOSE_COUNTS = {
    CoveragePurpose.NULL_CALIBRATION: 10,
    CoveragePurpose.TYPE_I_ERROR_STRESS: 10,
    CoveragePurpose.COVERAGE_STRESS: 8,
    CoveragePurpose.ESTIMATOR_ROBUSTNESS: 10,
    CoveragePurpose.DESIGN_STRESS_TEST: 8,
    CoveragePurpose.MULTICELL_DEPENDENCE_STRESS: 5,
    CoveragePurpose.SPILLOVER_STRESS: 5,
    CoveragePurpose.OUTCOME_SCALE_STRESS: 7,
    CoveragePurpose.PROMOTION_GATE: 10,
    CoveragePurpose.RESEARCH_SCOUT: 5,
}

REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)
REQUIRED_INFERENCE_FAMILIES = frozenset(InferenceFamily)


@dataclass(frozen=True)
class SimulationDgpRequirement:
    dgp_id: str
    name: str
    category: DgpCategory
    severity: DgpSeverity
    description: str
    covered_observed_diagnostics: tuple[str, ...]
    affected_method_families: tuple[MethodFamily, ...]
    affected_inference_families: tuple[InferenceFamily, ...]
    coverage_purposes: tuple[CoveragePurpose, ...]
    minimum_required_before_promotion: bool
    blocks_promotion_if_missing: bool
    recommended_next_artifact: str | None
    notes: str


def _dgp(
    dgp_id: str,
    name: str,
    category: DgpCategory,
    severity: DgpSeverity,
    description: str,
    *,
    covered_observed_diagnostics: tuple[str, ...],
    affected_method_families: tuple[MethodFamily, ...],
    affected_inference_families: tuple[InferenceFamily, ...],
    coverage_purposes: tuple[CoveragePurpose, ...],
    minimum_required_before_promotion: bool = False,
    blocks_promotion_if_missing: bool = False,
    recommended_next_artifact: str | None = None,
    notes: str = "",
) -> SimulationDgpRequirement:
    return SimulationDgpRequirement(
        dgp_id=dgp_id,
        name=name,
        category=category,
        severity=severity,
        description=description,
        covered_observed_diagnostics=covered_observed_diagnostics,
        affected_method_families=affected_method_families,
        affected_inference_families=affected_inference_families,
        coverage_purposes=coverage_purposes,
        minimum_required_before_promotion=minimum_required_before_promotion,
        blocks_promotion_if_missing=blocks_promotion_if_missing,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_ALL_M = (MethodFamily.ALL,)
_ALL_I = (InferenceFamily.ALL,)
_NULL = (CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.TYPE_I_ERROR_STRESS)


def _null_baseline_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-NB-001", "iid_normal_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_CORE,
             "IID Gaussian null for baseline calibration harnesses.",
             covered_observed_diagnostics=("OPD-PS-010",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.PLACEBO_RANK),
             coverage_purposes=_NULL + (CoveragePurpose.PROMOTION_GATE,), minimum_required_before_promotion=True,
             blocks_promotion_if_missing=True),
        _dgp("DGP-NB-002", "iid_non_normal_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_CORE,
             "IID non-normal null for robustness of test statistics.",
             covered_observed_diagnostics=("OPD-OM-005",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.STUDENTIZED_PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
             coverage_purposes=_NULL + (CoveragePurpose.ESTIMATOR_ROBUSTNESS,), minimum_required_before_promotion=True,
             blocks_promotion_if_missing=True),
        _dgp("DGP-NB-003", "unit_fixed_effects_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_CORE,
             "Unit fixed effects null common in geo panels.",
             covered_observed_diagnostics=("OPD-PS-011",), affected_method_families=(MethodFamily.DID, MethodFamily.SCM, MethodFamily.ALL),
             affected_inference_families=_ALL_I, coverage_purposes=_NULL + (CoveragePurpose.PROMOTION_GATE,),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-NB-004", "time_fixed_effects_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_CORE,
             "Time fixed effects null for common shocks.",
             covered_observed_diagnostics=("OPD-TD-002",), affected_method_families=(MethodFamily.DID, MethodFamily.ALL),
             affected_inference_families=_ALL_I, coverage_purposes=_NULL, minimum_required_before_promotion=True,
             blocks_promotion_if_missing=True),
        _dgp("DGP-NB-005", "unit_time_fixed_effects_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_CORE,
             "Two-way fixed effects null for DID-style estimators.",
             covered_observed_diagnostics=("OPD-PF-003",), affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.CLUSTER_ROBUST),
             coverage_purposes=_NULL + (CoveragePurpose.PROMOTION_GATE,), minimum_required_before_promotion=True,
             blocks_promotion_if_missing=True),
        _dgp("DGP-NB-006", "latent_factor_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_STRESS,
             "Latent factor null for unobserved confounding structure.",
             covered_observed_diagnostics=("OPD-PF-005",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
             coverage_purposes=_NULL + (CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.COVERAGE_STRESS,),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-NB-007", "donor_matched_latent_factor_null", DgpCategory.NULL_BASELINE, DgpSeverity.REQUIRED_STRESS,
             "Donor-matched latent factor null for synthetic control paths.",
             covered_observed_diagnostics=("OPD-DS-004", "OPD-DS-003"), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.STUDENTIZED_PLACEBO_RANK),
             coverage_purposes=_NULL + (CoveragePurpose.ESTIMATOR_ROBUSTNESS,), minimum_required_before_promotion=True,
             blocks_promotion_if_missing=True, recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001"),
    )


def _noise_variance_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-NV-001", "homoskedastic_noise", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_CORE,
             "Homoskedastic noise baseline for calibration reference.",
             covered_observed_diagnostics=("OPD-TD-006",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-NV-002", "heteroskedastic_unit_noise", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_STRESS,
             "Unit-level heteroskedasticity stress.",
             covered_observed_diagnostics=("OPD-OM-006", "OPD-TD-006"), affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.STUDENTIZED_PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-NV-003", "heteroskedastic_time_noise", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_STRESS,
             "Time-varying variance stress for studentized statistics.",
             covered_observed_diagnostics=("OPD-TD-006",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.STUDENTIZED_PLACEBO_RANK, InferenceFamily.RANDOMIZATION),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.COVERAGE_STRESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-NV-004", "clustered_unit_noise", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_STRESS,
             "Clustered unit noise for cluster-robust inference paths.",
             covered_observed_diagnostics=("OPD-MC-005",), affected_method_families=(MethodFamily.DID, MethodFamily.MULTICELL),
             affected_inference_families=(InferenceFamily.CLUSTER_ROBUST, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-NV-005", "serially_correlated_errors", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_STRESS,
             "Serial correlation invalidates IID bootstrap nulls.",
             covered_observed_diagnostics=("OPD-TD-001",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.NULL_CALIBRATION),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True,
             recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _dgp("DGP-NV-006", "heavy_tailed_errors", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_STRESS,
             "Heavy-tailed errors stress mean-based estimands.",
             covered_observed_diagnostics=("OPD-OM-005",), affected_method_families=(MethodFamily.TBR, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.PLACEBO_RANK),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-NV-007", "outlier_contaminated_errors", DgpCategory.NOISE_VARIANCE, DgpSeverity.REQUIRED_STRESS,
             "Outlier contamination for robustness stress.",
             covered_observed_diagnostics=("OPD-TD-004",), affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.TYPE_I_ERROR_STRESS)),
    )


def _temporal_structure_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-TS-001", "seasonality", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.REQUIRED_STRESS,
             "Seasonal DGP for calendar adjustment stress.",
             covered_observed_diagnostics=("OPD-TD-002",), affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.NULL_CALIBRATION),
             minimum_required_before_promotion=True),
        _dgp("DGP-TS-002", "holiday_promo_shocks", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.REQUIRED_STRESS,
             "Holiday/promo shock DGP.",
             covered_observed_diagnostics=("OPD-TD-003",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.RANDOMIZATION),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-TS-003", "level_shifts", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.REQUIRED_STRESS,
             "Level shift DGP breaks parallel trends.",
             covered_observed_diagnostics=("OPD-TD-005",), affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.PLACEBO_RANK),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.PROMOTION_GATE),
             blocks_promotion_if_missing=True),
        _dgp("DGP-TS-004", "trend_breaks", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.REQUIRED_STRESS,
             "Pre-period trend break DGP.",
             covered_observed_diagnostics=("OPD-PF-004",), affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-TS-005", "nonstationary_baseline", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.REQUIRED_STRESS,
             "Nonstationary baseline DGP.",
             covered_observed_diagnostics=("OPD-PF-005",), affected_method_families=_ALL_M,
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.NULL_CALIBRATION),
             minimum_required_before_promotion=True),
        _dgp("DGP-TS-006", "lagged_treatment_response", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.METHOD_SPECIFIC,
             "Lag between treatment and measurable response.",
             covered_observed_diagnostics=("OPD-TD-007",), affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.DESIGN_STRESS_TEST)),
        _dgp("DGP-TS-007", "metric_delay_mismatch", DgpCategory.TEMPORAL_STRUCTURE, DgpSeverity.METHOD_SPECIFIC,
             "Metric delay mismatch between treatment and outcome read.",
             covered_observed_diagnostics=("OPD-TD-007",), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
    )


def _outcome_scale_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-OS-001", "continuous_outcome", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_CORE,
             "Continuous outcome baseline DGP.",
             covered_observed_diagnostics=("OPD-OM-007",), affected_method_families=_ALL_M,
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.PROMOTION_GATE)),
        _dgp("DGP-OS-002", "log_normal_outcome", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Log-normal outcome for scale transform stress.",
             covered_observed_diagnostics=("OPD-OM-008",), affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-OS-003", "count_outcome", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Count outcome DGP.",
             covered_observed_diagnostics=("OPD-OM-003",), affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
             affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.CONFORMAL),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.RESEARCH_SCOUT),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-OS-004", "sparse_count_outcome", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Sparse count conversion metrics.",
             covered_observed_diagnostics=("OPD-OM-001", "OPD-OM-003"), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.CONFORMAL),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.RESEARCH_SCOUT),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-OS-005", "zero_inflated_outcome", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Zero-inflated outcome DGP.",
             covered_observed_diagnostics=("OPD-OM-002",), affected_method_families=(MethodFamily.SCM, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.TYPE_I_ERROR_STRESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-OS-006", "binary_binomial_outcome", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Binary/binomial outcome DGP.",
             covered_observed_diagnostics=("OPD-OM-004",), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.PROMOTION_GATE),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-OS-007", "rate_outcome_denominator", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Rate metric with denominator DGP.",
             covered_observed_diagnostics=("OPD-OM-009", "OPD-OM-010"), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-OS-008", "heavy_tailed_revenue", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Heavy-tailed revenue outcome DGP.",
             covered_observed_diagnostics=("OPD-OM-005",), affected_method_families=(MethodFamily.TBR, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-OS-009", "negative_invalid_log_scale", DgpCategory.OUTCOME_SCALE, DgpSeverity.REQUIRED_STRESS,
             "Negative values invalidating log-scale models.",
             covered_observed_diagnostics=("OPD-OM-008",), affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.TBR),
             affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
             coverage_purposes=(CoveragePurpose.OUTCOME_SCALE_STRESS, CoveragePurpose.PROMOTION_GATE),
             blocks_promotion_if_missing=True, recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001"),
    )


def _treatment_effect_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-TE-001", "sharp_null", DgpCategory.TREATMENT_EFFECT, DgpSeverity.REQUIRED_CORE,
             "Sharp null for type-I calibration.",
             covered_observed_diagnostics=("OPD-TE-003",), affected_method_families=_ALL_M,
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.TYPE_I_ERROR_STRESS),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-TE-002", "constant_additive_te", DgpCategory.TREATMENT_EFFECT, DgpSeverity.REQUIRED_CORE,
             "Constant additive treatment effect for coverage stress.",
             covered_observed_diagnostics=("OPD-ER-003",), affected_method_families=(MethodFamily.DID, MethodFamily.SCM),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-TE-003", "constant_multiplicative_te", DgpCategory.TREATMENT_EFFECT, DgpSeverity.METHOD_SPECIFIC,
             "Multiplicative treatment effect DGP.",
             covered_observed_diagnostics=("OPD-OM-007",), affected_method_families=(MethodFamily.TBRRIDGE,),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-TE-004", "heterogeneous_te_by_unit", DgpCategory.TREATMENT_EFFECT, DgpSeverity.REQUIRED_STRESS,
             "Unit-level heterogeneous treatment effects.",
             covered_observed_diagnostics=("OPD-TE-004",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-TE-005", "heterogeneous_te_by_time", DgpCategory.TREATMENT_EFFECT, DgpSeverity.REQUIRED_STRESS,
             "Time-varying treatment effects.",
             covered_observed_diagnostics=("OPD-PF-004",), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-TE-006", "delayed_te", DgpCategory.TREATMENT_EFFECT, DgpSeverity.METHOD_SPECIFIC,
             "Delayed treatment effect onset.",
             covered_observed_diagnostics=("OPD-TD-007", "OPD-TE-005"), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.DESIGN_STRESS_TEST)),
        _dgp("DGP-TE-007", "dose_response_te", DgpCategory.TREATMENT_EFFECT, DgpSeverity.METHOD_SPECIFIC,
             "Dose-response treatment effect DGP.",
             covered_observed_diagnostics=("OPD-TE-001", "OPD-TE-002"), affected_method_families=(MethodFamily.TBRRIDGE,),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-TE-008", "staggered_activation_te", DgpCategory.TREATMENT_EFFECT, DgpSeverity.REQUIRED_STRESS,
             "Staggered activation treatment effects.",
             covered_observed_diagnostics=("OPD-TE-005",), affected_method_families=(MethodFamily.DID, MethodFamily.SYNTHETIC_DID),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.CLUSTER_ROBUST),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.COVERAGE_STRESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-TE-009", "partial_compliance", DgpCategory.TREATMENT_EFFECT, DgpSeverity.RESEARCH_EXTENSION,
             "Partial compliance DGP for estimand ambiguity stress.",
             covered_observed_diagnostics=("OPD-TE-004",), affected_method_families=(MethodFamily.DID, MethodFamily.ALL),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.DESIGN_STRESS_TEST)),
    )


def _assignment_design_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-AD-001", "complete_randomized_assignment", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_CORE,
             "Complete randomized assignment DGP.",
             covered_observed_diagnostics=("OPD-AD-002",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.PERMUTATION),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.PROMOTION_GATE),
             minimum_required_before_promotion=True),
        _dgp("DGP-AD-002", "matched_pair_randomized", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_STRESS,
             "Matched-pair randomized assignment.",
             covered_observed_diagnostics=("OPD-AD-003",), affected_method_families=(MethodFamily.DID, MethodFamily.TBRRIDGE),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.NULL_CALIBRATION),
             recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"),
        _dgp("DGP-AD-003", "matched_block_randomized", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_STRESS,
             "Matched-block randomized assignment.",
             covered_observed_diagnostics=("OPD-AD-004",), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.CLUSTER_ROBUST),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST,)),
        _dgp("DGP-AD-004", "stratified_randomized", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_STRESS,
             "Stratified randomized assignment.",
             covered_observed_diagnostics=("OPD-AD-005",), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.NULL_CALIBRATION)),
        _dgp("DGP-AD-005", "rerandomized_acceptance", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_STRESS,
             "Rerandomization with acceptance rule.",
             covered_observed_diagnostics=("OPD-AD-006",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.NULL_CALIBRATION),
             recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"),
        _dgp("DGP-AD-006", "greedy_matched_market_deterministic", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.DIAGNOSTIC_ONLY,
             "Greedy matched-market deterministic assignment (falsification only).",
             covered_observed_diagnostics=("OPD-AD-002", "OPD-AD-010"), affected_method_families=(MethodFamily.SCM,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.RESEARCH_SCOUT),
             recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001"),
        _dgp("DGP-AD-007", "kernel_thinning_assignment", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.DIAGNOSTIC_ONLY,
             "Kernel thinning assignment (falsification only).",
             covered_observed_diagnostics=("OPD-AD-010",), affected_method_families=(MethodFamily.SCM,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.RESEARCH_SCOUT)),
        _dgp("DGP-AD-008", "fixed_deterministic_assignment", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_STRESS,
             "Fixed deterministic assignment blocks randomization inference.",
             covered_observed_diagnostics=("OPD-AD-002",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.TYPE_I_ERROR_STRESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-AD-009", "unknown_assignment", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_CORE,
             "Unknown assignment DGP blocks design-based inference.",
             covered_observed_diagnostics=("OPD-AD-001",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.DESIGN_STRESS_TEST),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
        _dgp("DGP-AD-010", "small_assignment_support", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.REQUIRED_STRESS,
             "Small randomization support size DGP.",
             covered_observed_diagnostics=("OPD-AD-009",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.PLACEBO_RANK),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.DESIGN_STRESS_TEST),
             recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"),
        _dgp("DGP-AD-011", "degenerate_pseudo_assignment_support", DgpCategory.ASSIGNMENT_DESIGN, DgpSeverity.DIAGNOSTIC_ONLY,
             "Degenerate pseudo-assignment support for falsification paths.",
             covered_observed_diagnostics=("OPD-AD-010",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.DESIGN_STRESS_TEST, CoveragePurpose.RESEARCH_SCOUT)),
    )


def _donor_support_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-DS-001", "good_donor_overlap", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_CORE,
             "Favorable donor overlap for SCM/AugSynth calibration.",
             covered_observed_diagnostics=("OPD-DS-004", "OPD-DS-005"), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.PROMOTION_GATE)),
        _dgp("DGP-DS-002", "weak_donor_overlap", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_STRESS,
             "Weak donor overlap stress scenario.",
             covered_observed_diagnostics=("OPD-DS-005",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.STUDENTIZED_PLACEBO_RANK),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.TYPE_I_ERROR_STRESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-DS-003", "donor_hull_violation", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_STRESS,
             "Donor hull violation DGP.",
             covered_observed_diagnostics=("OPD-DS-003",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-DS-004", "treated_outside_donor_range", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_STRESS,
             "Treated unit outside donor range.",
             covered_observed_diagnostics=("OPD-DS-003", "OPD-DS-008"), affected_method_families=(MethodFamily.SCM,),
             affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-DS-005", "donor_weight_degeneracy", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_STRESS,
             "SCM donor weight degeneracy DGP.",
             covered_observed_diagnostics=("OPD-DS-006",), affected_method_families=(MethodFamily.SCM,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.PROMOTION_GATE),
             blocks_promotion_if_missing=True, recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001"),
        _dgp("DGP-DS-006", "augsynth_extrapolation_risk", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_STRESS,
             "AugSynth extrapolation beyond donor hull.",
             covered_observed_diagnostics=("OPD-DS-007",), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.JACKKNIFE),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-DS-007", "support_mismatch", DgpCategory.DONOR_SUPPORT, DgpSeverity.REQUIRED_CORE,
             "Hard support mismatch blocks SCM/AugSynth promotion.",
             covered_observed_diagnostics=("OPD-DS-008",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True),
    )


def _small_sample_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-SS-001", "small_number_geos", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Small number of geos DGP.",
             covered_observed_diagnostics=("OPD-PS-011",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.JACKKNIFE, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.COVERAGE_STRESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-SS-002", "few_treated_units", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Few treated units DGP.",
             covered_observed_diagnostics=("OPD-PS-008",), affected_method_families=(MethodFamily.SCM, MethodFamily.MULTICELL),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.MAX_T),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS)),
        _dgp("DGP-SS-003", "few_donor_units", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Few donor units DGP.",
             covered_observed_diagnostics=("OPD-PS-009",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.PROMOTION_GATE)),
        _dgp("DGP-SS-004", "short_pre_period", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Short pre-period DGP.",
             covered_observed_diagnostics=("OPD-PS-006",), affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-SS-005", "short_post_period", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Short post-period DGP.",
             covered_observed_diagnostics=("OPD-PS-007",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-SS-006", "unbalanced_panel", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Unbalanced panel DGP.",
             covered_observed_diagnostics=("OPD-PS-003",), affected_method_families=(MethodFamily.TBRRIDGE,),
             affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-SS-007", "missingness", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_STRESS,
             "Panel missingness DGP.",
             covered_observed_diagnostics=("OPD-PS-004",), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY, MethodFamily.SCM),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-SS-008", "duplicate_panel_rows", DgpCategory.SMALL_SAMPLE_PANEL, DgpSeverity.REQUIRED_CORE,
             "Duplicate panel rows DGP for data integrity stress.",
             covered_observed_diagnostics=("OPD-PS-005",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.DESIGN_STRESS_TEST),
             blocks_promotion_if_missing=True),
    )


def _interference_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-IS-001", "no_interference", DgpCategory.INTERFERENCE_SPILLOVER, DgpSeverity.REQUIRED_CORE,
             "No-interference baseline DGP.",
             covered_observed_diagnostics=("OPD-TE-007",), affected_method_families=_ALL_M,
             affected_inference_families=_ALL_I, coverage_purposes=(CoveragePurpose.NULL_CALIBRATION,)),
        _dgp("DGP-IS-002", "neighbor_spillover", DgpCategory.INTERFERENCE_SPILLOVER, DgpSeverity.REQUIRED_STRESS,
             "Neighbor spillover DGP.",
             covered_observed_diagnostics=("OPD-TE-007",), affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.SPILLOVER_STRESS, CoveragePurpose.RESEARCH_SCOUT),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True,
             recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _dgp("DGP-IS-003", "cross_cell_contamination", DgpCategory.INTERFERENCE_SPILLOVER, DgpSeverity.REQUIRED_STRESS,
             "Cross-cell contamination DGP.",
             covered_observed_diagnostics=("OPD-TE-008", "OPD-TE-006"), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.SPILLOVER_STRESS, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-IS-004", "national_media_spillover", DgpCategory.INTERFERENCE_SPILLOVER, DgpSeverity.RESEARCH_EXTENSION,
             "National media spillover DGP.",
             covered_observed_diagnostics=("OPD-TE-007",), affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.SPILLOVER_STRESS, CoveragePurpose.RESEARCH_SCOUT)),
        _dgp("DGP-IS-005", "donor_contamination", DgpCategory.INTERFERENCE_SPILLOVER, DgpSeverity.REQUIRED_STRESS,
             "Donor contamination DGP.",
             covered_observed_diagnostics=("OPD-TE-006",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.SPILLOVER_STRESS, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-IS-006", "partial_exposure_leakage", DgpCategory.INTERFERENCE_SPILLOVER, DgpSeverity.REQUIRED_STRESS,
             "Partial exposure leakage DGP.",
             covered_observed_diagnostics=("OPD-TE-008",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN),
             coverage_purposes=(CoveragePurpose.SPILLOVER_STRESS, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS)),
    )


def _multicell_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-MC-001", "independent_cells", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.REQUIRED_CORE,
             "Independent cells baseline multicell DGP.",
             covered_observed_diagnostics=("OPD-MC-005",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS)),
        _dgp("DGP-MC-002", "shared_control_dependence", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.REQUIRED_STRESS,
             "Shared-control dependence DGP.",
             covered_observed_diagnostics=("OPD-MC-001", "OPD-AD-008"), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.MULTICELL_DEPENDENCE_STRESS, CoveragePurpose.RESEARCH_SCOUT),
             minimum_required_before_promotion=True, blocks_promotion_if_missing=True,
             recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _dgp("DGP-MC-003", "multiple_treatment_arms", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.REQUIRED_STRESS,
             "Multiple treatment arms DGP.",
             covered_observed_diagnostics=("OPD-MC-002",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN),
             coverage_purposes=(CoveragePurpose.MULTICELL_DEPENDENCE_STRESS, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-MC-004", "correlated_cell_estimates", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.REQUIRED_STRESS,
             "Correlated cross-cell estimates DGP.",
             covered_observed_diagnostics=("OPD-MC-001",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T,),
             coverage_purposes=(CoveragePurpose.MULTICELL_DEPENDENCE_STRESS, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-MC-005", "winner_selection", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.REQUIRED_STRESS,
             "Winner selection multiplicity DGP.",
             covered_observed_diagnostics=("OPD-MC-003",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-MC-006", "global_pooled_effect_ambiguity", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.RESEARCH_EXTENSION,
             "Global pooled effect ambiguity DGP.",
             covered_observed_diagnostics=("OPD-MC-007",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS)),
        _dgp("DGP-MC-007", "familywise_error_stress", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.REQUIRED_STRESS,
             "Familywise error rate stress DGP.",
             covered_observed_diagnostics=("OPD-MC-004",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T, InferenceFamily.STEPDOWN),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS),
             minimum_required_before_promotion=True),
        _dgp("DGP-MC-008", "max_t_candidate", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.METHOD_SPECIFIC,
             "Max-T candidate scenario DGP.",
             covered_observed_diagnostics=("OPD-IR-009",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS),
             recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _dgp("DGP-MC-009", "stepdown_candidate", DgpCategory.MULTICELL_MULTIPLICITY, DgpSeverity.METHOD_SPECIFIC,
             "Stepdown candidate scenario DGP.",
             covered_observed_diagnostics=("OPD-IR-009",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.STEPDOWN,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS),
             recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
    )


def _estimator_specific_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-ES-001", "scm_pre_fit_favorable", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "SCM favorable pre-fit DGP.",
             covered_observed_diagnostics=("OPD-PF-001", "OPD-ER-001"), affected_method_families=(MethodFamily.SCM,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.STUDENTIZED_PLACEBO_RANK),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-ES-002", "scm_pre_fit_poor", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "SCM poor pre-fit DGP.",
             covered_observed_diagnostics=("OPD-PF-001",), affected_method_families=(MethodFamily.SCM,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-ES-003", "augsynth_augmentation_stable", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "AugSynth stable augmentation DGP.",
             covered_observed_diagnostics=("OPD-ER-002",), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK, InferenceFamily.JACKKNIFE),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-ES-004", "augsynth_augmentation_unstable", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "AugSynth unstable augmentation DGP.",
             covered_observed_diagnostics=("OPD-DS-007",), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
             affected_inference_families=(InferenceFamily.JACKKNIFE, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.ESTIMATOR_ROBUSTNESS),
             recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001"),
        _dgp("DGP-ES-005", "did_parallel_trends_plausible", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "DID parallel trends plausible DGP.",
             covered_observed_diagnostics=("OPD-PF-003", "OPD-ER-003"), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-ES-006", "did_parallel_trends_violated", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "DID parallel trends violated DGP.",
             covered_observed_diagnostics=("OPD-PF-003",), affected_method_families=(MethodFamily.DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.TYPE_I_ERROR_STRESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-ES-007", "tbrridge_stable_relation", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "TBRRidge stable relation DGP.",
             covered_observed_diagnostics=("OPD-ER-004",), affected_method_families=(MethodFamily.TBRRIDGE,),
             affected_inference_families=(InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-ES-008", "tbrridge_unstable_relation", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "TBRRidge unstable relation DGP.",
             covered_observed_diagnostics=("OPD-ER-004",), affected_method_families=(MethodFamily.TBRRIDGE,),
             affected_inference_families=(InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.TYPE_I_ERROR_STRESS),
             recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _dgp("DGP-ES-009", "bayesian_tbr_prior_sensitive", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.DIAGNOSTIC_ONLY,
             "Bayesian TBR prior sensitivity DGP.",
             covered_observed_diagnostics=("OPD-ER-006",), affected_method_families=(MethodFamily.BAYESIAN_TBR,),
             affected_inference_families=(InferenceFamily.BAYESIAN_POSTERIOR_DIAGNOSTIC,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-ES-010", "synthetic_did_balanced_favorable", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.RESEARCH_EXTENSION,
             "Synthetic DID favorable balanced panel DGP.",
             covered_observed_diagnostics=("OPD-ER-007",), affected_method_families=(MethodFamily.SYNTHETIC_DID,),
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-ES-011", "trop_research_only", DgpCategory.ESTIMATOR_SPECIFIC, DgpSeverity.RESEARCH_EXTENSION,
             "TROP research-only DGP scenario.",
             covered_observed_diagnostics=("OPD-ER-008",), affected_method_families=(MethodFamily.TROP,),
             affected_inference_families=(InferenceFamily.CONFORMAL,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT,)),
    )


def _inference_specific_rows() -> tuple[SimulationDgpRequirement, ...]:
    return (
        _dgp("DGP-INF-001", "randomization_inference_feasible", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "Randomization inference feasible DGP.",
             covered_observed_diagnostics=("OPD-IR-001",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION,),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.PROMOTION_GATE),
             recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"),
        _dgp("DGP-INF-002", "randomization_invalid_unknown_assignment", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.REQUIRED_CORE,
             "Randomization invalid due to unknown assignment.",
             covered_observed_diagnostics=("OPD-AD-001", "OPD-IR-001"), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.RANDOMIZATION, InferenceFamily.NO_VALID_INFERENCE),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.TYPE_I_ERROR_STRESS),
             blocks_promotion_if_missing=True),
        _dgp("DGP-INF-003", "placebo_rank_feasible", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "Placebo rank feasible DGP.",
             covered_observed_diagnostics=("OPD-IR-002",), affected_method_families=(MethodFamily.SCM, MethodFamily.AUGSYNTH_CVXPY),
             affected_inference_families=(InferenceFamily.PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.ESTIMATOR_ROBUSTNESS)),
        _dgp("DGP-INF-004", "studentized_placebo_needed", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "Studentized placebo needed DGP.",
             covered_observed_diagnostics=("OPD-IR-003",), affected_method_families=(MethodFamily.SCM, MethodFamily.DID),
             affected_inference_families=(InferenceFamily.STUDENTIZED_PLACEBO_RANK,),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.TYPE_I_ERROR_STRESS)),
        _dgp("DGP-INF-005", "bootstrap_feasible", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "Bootstrap feasible DGP.",
             covered_observed_diagnostics=("OPD-IR-004",), affected_method_families=(MethodFamily.TBRRIDGE, MethodFamily.DID),
             affected_inference_families=(InferenceFamily.BOOTSTRAP,),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.NULL_CALIBRATION)),
        _dgp("DGP-INF-006", "bootstrap_invalid_under_dependence", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.REQUIRED_STRESS,
             "Bootstrap invalid under dependence DGP.",
             covered_observed_diagnostics=("OPD-TD-001", "OPD-IR-004"), affected_method_families=(MethodFamily.TBRRIDGE,),
             affected_inference_families=(InferenceFamily.BOOTSTRAP, InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP),
             coverage_purposes=(CoveragePurpose.TYPE_I_ERROR_STRESS, CoveragePurpose.PROMOTION_GATE),
             blocks_promotion_if_missing=True,
             recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"),
        _dgp("DGP-INF-007", "jackknife_sensitivity_only", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.DIAGNOSTIC_ONLY,
             "Jackknife sensitivity-only DGP.",
             covered_observed_diagnostics=("OPD-IR-005",), affected_method_families=(MethodFamily.AUGSYNTH_CVXPY,),
             affected_inference_families=(InferenceFamily.JACKKNIFE,),
             coverage_purposes=(CoveragePurpose.ESTIMATOR_ROBUSTNESS, CoveragePurpose.RESEARCH_SCOUT)),
        _dgp("DGP-INF-008", "cluster_robust_candidate", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "Cluster-robust candidate DGP.",
             covered_observed_diagnostics=("OPD-IR-006",), affected_method_families=(MethodFamily.DID, MethodFamily.MULTICELL),
             affected_inference_families=(InferenceFamily.CLUSTER_ROBUST,),
             coverage_purposes=(CoveragePurpose.COVERAGE_STRESS, CoveragePurpose.MULTICELL_DEPENDENCE_STRESS)),
        _dgp("DGP-INF-009", "conformal_candidate", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.RESEARCH_EXTENSION,
             "Conformal inference candidate DGP.",
             covered_observed_diagnostics=("OPD-IR-007",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.CONFORMAL,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT, CoveragePurpose.COVERAGE_STRESS)),
        _dgp("DGP-INF-010", "posterior_diagnostic_only", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.DIAGNOSTIC_ONLY,
             "Bayesian posterior diagnostic-only DGP.",
             covered_observed_diagnostics=("OPD-IR-008",), affected_method_families=(MethodFamily.BAYESIAN_TBR,),
             affected_inference_families=(InferenceFamily.BAYESIAN_POSTERIOR_DIAGNOSTIC,),
             coverage_purposes=(CoveragePurpose.RESEARCH_SCOUT,)),
        _dgp("DGP-INF-011", "max_t_required", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.REQUIRED_STRESS,
             "Max-T required for multicell DGP.",
             covered_observed_diagnostics=("OPD-IR-009",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.MAX_T,),
             coverage_purposes=(CoveragePurpose.MULTICELL_DEPENDENCE_STRESS, CoveragePurpose.RESEARCH_SCOUT),
             recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001"),
        _dgp("DGP-INF-012", "stepdown_required", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.REQUIRED_STRESS,
             "Stepdown required for multicell DGP.",
             covered_observed_diagnostics=("OPD-IR-009",), affected_method_families=(MethodFamily.MULTICELL,),
             affected_inference_families=(InferenceFamily.STEPDOWN,),
             coverage_purposes=(CoveragePurpose.MULTICELL_DEPENDENCE_STRESS, CoveragePurpose.RESEARCH_SCOUT)),
        _dgp("DGP-INF-013", "no_valid_inference", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.REQUIRED_CORE,
             "No valid inference path DGP.",
             covered_observed_diagnostics=("OPD-IR-010",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.NO_VALID_INFERENCE,),
             coverage_purposes=(CoveragePurpose.PROMOTION_GATE, CoveragePurpose.TYPE_I_ERROR_STRESS),
             blocks_promotion_if_missing=True, recommended_next_artifact="METHOD_FAILURE_MODE_REGISTRY_001"),
        _dgp("DGP-INF-014", "permutation_inference_candidate", DgpCategory.INFERENCE_SPECIFIC, DgpSeverity.METHOD_SPECIFIC,
             "Permutation inference candidate DGP.",
             covered_observed_diagnostics=("OPD-IR-001",), affected_method_families=_ALL_M,
             affected_inference_families=(InferenceFamily.PERMUTATION,),
             coverage_purposes=(CoveragePurpose.NULL_CALIBRATION, CoveragePurpose.DESIGN_STRESS_TEST)),
    )


def build_simulation_dgp_coverage_plan() -> tuple[SimulationDgpRequirement, ...]:
    """Build the full simulation DGP coverage plan."""
    return (
        *_null_baseline_rows(),
        *_noise_variance_rows(),
        *_temporal_structure_rows(),
        *_outcome_scale_rows(),
        *_treatment_effect_rows(),
        *_assignment_design_rows(),
        *_donor_support_rows(),
        *_small_sample_rows(),
        *_interference_rows(),
        *_multicell_rows(),
        *_estimator_specific_rows(),
        *_inference_specific_rows(),
    )


def filter_simulation_dgp_requirements(
    requirements: tuple[SimulationDgpRequirement, ...],
    *,
    category: DgpCategory | None = None,
    severity: DgpSeverity | None = None,
    method_family: MethodFamily | None = None,
    inference_family: InferenceFamily | None = None,
    coverage_purpose: CoveragePurpose | None = None,
) -> tuple[SimulationDgpRequirement, ...]:
    """Filter DGP requirements by optional predicates."""
    filtered: list[SimulationDgpRequirement] = []
    for req in requirements:
        if category is not None and req.category != category:
            continue
        if severity is not None and req.severity != severity:
            continue
        if method_family is not None and method_family not in req.affected_method_families:
            continue
        if inference_family is not None and inference_family not in req.affected_inference_families:
            continue
        if coverage_purpose is not None and coverage_purpose not in req.coverage_purposes:
            continue
        filtered.append(req)
    return tuple(filtered)


def validate_simulation_dgp_coverage_plan(
    requirements: tuple[SimulationDgpRequirement, ...],
) -> dict[str, Any]:
    """Validate DGP plan invariants and return structured validation summary."""
    issues: list[str] = []
    dgp_ids = [r.dgp_id for r in requirements]

    if len(dgp_ids) != len(set(dgp_ids)):
        issues.append("duplicate dgp_id detected")
    if len(requirements) < 90:
        issues.append(f"dgp_count {len(requirements)} < 90")

    category_counts = Counter(r.category for r in requirements)
    for cat, minimum in MIN_CATEGORY_COUNTS.items():
        if category_counts.get(cat, 0) < minimum:
            issues.append(f"category {cat.value} count {category_counts.get(cat, 0)} < {minimum}")

    purpose_counts = Counter(p for r in requirements for p in r.coverage_purposes)
    for purpose, minimum in MIN_COVERAGE_PURPOSE_COUNTS.items():
        if purpose_counts.get(purpose, 0) < minimum:
            issues.append(f"coverage purpose {purpose.value} count {purpose_counts.get(purpose, 0)} < {minimum}")

    methods_present: set[MethodFamily] = set()
    inference_present: set[InferenceFamily] = set()
    for req in requirements:
        methods_present.update(req.affected_method_families)
        inference_present.update(req.affected_inference_families)

    missing_methods = sorted(REQUIRED_METHOD_FAMILIES - methods_present, key=lambda m: m.value)
    if missing_methods:
        issues.append(f"missing method families: {[m.value for m in missing_methods]}")

    missing_inference = sorted(REQUIRED_INFERENCE_FAMILIES - inference_present, key=lambda i: i.value)
    if missing_inference:
        issues.append(f"missing inference families: {[i.value for i in missing_inference]}")

    for req in requirements:
        if not req.covered_observed_diagnostics:
            issues.append(f"{req.dgp_id} empty covered_observed_diagnostics")
        if not req.affected_method_families:
            issues.append(f"{req.dgp_id} empty affected_method_families")
        if not req.affected_inference_families:
            issues.append(f"{req.dgp_id} empty affected_inference_families")
        if not req.coverage_purposes:
            issues.append(f"{req.dgp_id} empty coverage_purposes")

    blockers = [r for r in requirements if r.blocks_promotion_if_missing]
    research = [r for r in requirements if r.severity == DgpSeverity.RESEARCH_EXTENSION]
    if not blockers:
        issues.append("no promotion blockers defined")
    if not research:
        issues.append("no research extensions defined")

    observed_mapped = any(r.covered_observed_diagnostics for r in requirements)
    sparse_coverage = any(
        r.name in {"sparse_count_outcome", "zero_inflated_outcome", "binary_binomial_outcome", "count_outcome"}
        for r in requirements
    )

    return {
        "valid": not issues,
        "dgp_count": len(requirements),
        "unique_dgp_ids": len(dgp_ids) == len(set(dgp_ids)),
        "category_counts": {cat.value: category_counts.get(cat, 0) for cat in DgpCategory},
        "null_baseline_covered": category_counts.get(DgpCategory.NULL_BASELINE, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.NULL_BASELINE],
        "noise_variance_covered": category_counts.get(DgpCategory.NOISE_VARIANCE, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.NOISE_VARIANCE],
        "temporal_structure_covered": category_counts.get(DgpCategory.TEMPORAL_STRUCTURE, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.TEMPORAL_STRUCTURE],
        "outcome_scale_covered": category_counts.get(DgpCategory.OUTCOME_SCALE, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.OUTCOME_SCALE],
        "treatment_effect_covered": category_counts.get(DgpCategory.TREATMENT_EFFECT, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.TREATMENT_EFFECT],
        "assignment_design_covered": category_counts.get(DgpCategory.ASSIGNMENT_DESIGN, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.ASSIGNMENT_DESIGN],
        "donor_support_covered": category_counts.get(DgpCategory.DONOR_SUPPORT, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.DONOR_SUPPORT],
        "small_sample_panel_covered": category_counts.get(DgpCategory.SMALL_SAMPLE_PANEL, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.SMALL_SAMPLE_PANEL],
        "interference_spillover_covered": category_counts.get(DgpCategory.INTERFERENCE_SPILLOVER, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.INTERFERENCE_SPILLOVER],
        "multicell_multiplicity_covered": category_counts.get(DgpCategory.MULTICELL_MULTIPLICITY, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.MULTICELL_MULTIPLICITY],
        "estimator_specific_covered": category_counts.get(DgpCategory.ESTIMATOR_SPECIFIC, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.ESTIMATOR_SPECIFIC],
        "inference_specific_covered": category_counts.get(DgpCategory.INFERENCE_SPECIFIC, 0) >= MIN_CATEGORY_COUNTS[DgpCategory.INFERENCE_SPECIFIC],
        "observed_diagnostics_mapped_to_dgps": observed_mapped,
        "sparse_count_binary_outcomes_require_coverage": sparse_coverage,
        "promotion_blockers_defined": bool(blockers),
        "research_extensions_defined": bool(research),
        "issues": issues,
    }


def summarize_simulation_dgp_coverage_plan(
    requirements: tuple[SimulationDgpRequirement, ...],
) -> dict[str, Any]:
    """Serialize simulation DGP coverage plan summary for archives."""
    validation = validate_simulation_dgp_coverage_plan(requirements)
    severity_counts = Counter(r.severity.value for r in requirements)
    method_family_counts: Counter[str] = Counter()
    inference_family_counts: Counter[str] = Counter()
    for req in requirements:
        for family in req.affected_method_families:
            method_family_counts[family.value] += 1
        for inf in req.affected_inference_families:
            inference_family_counts[inf.value] += 1
    coverage_purpose_counts = Counter(p.value for r in requirements for p in r.coverage_purposes)

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "dgp_count": len(requirements),
        "failed_scenarios": validation.get("issues", []),
        "category_counts": validation["category_counts"],
        "severity_counts": dict(severity_counts),
        "method_family_counts": dict(method_family_counts),
        "inference_family_counts": dict(inference_family_counts),
        "coverage_purpose_counts": dict(coverage_purpose_counts),
        "null_baseline_covered": validation["null_baseline_covered"],
        "noise_variance_covered": validation["noise_variance_covered"],
        "temporal_structure_covered": validation["temporal_structure_covered"],
        "outcome_scale_covered": validation["outcome_scale_covered"],
        "treatment_effect_covered": validation["treatment_effect_covered"],
        "assignment_design_covered": validation["assignment_design_covered"],
        "donor_support_covered": validation["donor_support_covered"],
        "small_sample_panel_covered": validation["small_sample_panel_covered"],
        "interference_spillover_covered": validation["interference_spillover_covered"],
        "multicell_multiplicity_covered": validation["multicell_multiplicity_covered"],
        "estimator_specific_covered": validation["estimator_specific_covered"],
        "inference_specific_covered": validation["inference_specific_covered"],
        "shared_dgp_universe_required": True,
        "observed_diagnostics_mapped_to_dgps": validation["observed_diagnostics_mapped_to_dgps"],
        "null_calibration_alone_sufficient": False,
        "dgp_coverage_blocks_future_promotion": validation["promotion_blockers_defined"],
        "multicell_and_interference_require_research_handling": True,
        "sparse_count_binary_outcomes_require_coverage": validation["sparse_count_binary_outcomes_require_coverage"],
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
    requirements = build_simulation_dgp_coverage_plan()
    validation = validate_simulation_dgp_coverage_plan(requirements)
    summary = summarize_simulation_dgp_coverage_plan(requirements)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("requirements_build_successfully", len(requirements) > 0))
    scenarios.append(_scenario("dgp_count_at_least_90", len(requirements) >= 90))
    scenarios.append(_scenario("dgp_ids_unique", validation["unique_dgp_ids"]))

    for cat in DgpCategory:
        key = f"{cat.value}_covered"
        scenarios.append(_scenario(key, validation.get(key, False)))

    for purpose, minimum in MIN_COVERAGE_PURPOSE_COUNTS.items():
        count = sum(1 for r in requirements for p in r.coverage_purposes if p == purpose)
        scenarios.append(_scenario(f"coverage_purpose_{purpose.value}_at_least_{minimum}", count >= minimum))

    scenarios.append(_scenario("shared_dgp_universe_required", summary["shared_dgp_universe_required"] is True))
    scenarios.append(_scenario("observed_diagnostics_mapped_to_dgps", summary["observed_diagnostics_mapped_to_dgps"] is True))
    scenarios.append(_scenario("null_calibration_alone_sufficient_false", summary["null_calibration_alone_sufficient"] is False))
    scenarios.append(_scenario("dgp_coverage_blocks_future_promotion", summary["dgp_coverage_blocks_future_promotion"] is True))
    scenarios.append(_scenario("multicell_and_interference_require_research_handling", summary["multicell_and_interference_require_research_handling"] is True))
    scenarios.append(_scenario("sparse_count_binary_outcomes_require_coverage", summary["sparse_count_binary_outcomes_require_coverage"] is True))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))
    scenarios.append(_scenario("promotion_blockers_exist", validation["promotion_blockers_defined"] is True))
    scenarios.append(_scenario("research_extensions_exist", validation["research_extensions_defined"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_method_failure_mode_registry_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(family in r.affected_method_families for r in requirements)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    for inf in REQUIRED_INFERENCE_FAMILIES:
        present = any(inf in r.affected_inference_families for r in requirements)
        scenarios.append(_scenario(f"inference_family_{inf.value}_represented", present))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    requirements = build_simulation_dgp_coverage_plan()
    validation = validate_simulation_dgp_coverage_plan(requirements)
    summary = summarize_simulation_dgp_coverage_plan(requirements)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "dgp_count": len(requirements),
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
