"""DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001 validation harness."""

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

_ARTIFACT_ID = "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "did_randomization_and_bootstrap_suitability_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = ("MULTICELL_MAX_T_RESEARCH_SCOUT_001",)

MIN_AUDIT_ROW_COUNT = 50

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

_DID_AUTH_FLAGS = {
    "did_point_diagnostic_allowed": True,
    "did_production_inference_authorized": False,
    "did_production_p_value_authorized": False,
    "did_causal_ci_authorized": False,
    "did_randomization_candidate_requires_known_assignment": True,
    "did_permutation_candidate_requires_valid_assignment_support": True,
    "did_bootstrap_candidate_requires_dependence_validation": True,
    "bootstrap_does_not_fix_invalid_assignment": True,
    "parallel_trends_required_before_promotion": True,
    "staggered_timing_requires_research_handling": True,
    "small_n_and_few_clusters_block_promotion": True,
    "sparse_count_binary_outcomes_require_dgp_coverage": True,
    "multicell_did_requires_multiplicity_research": True,
    "observed_diagnostics_required": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "design_assignment_stress_required": True,
    "downstream_work_paused": True,
}


class DidPath(str, Enum):
    POINT_ESTIMATE = "did_point_estimate"
    DESIGN_RANDOMIZATION = "did_design_randomization"
    PERMUTATION = "did_permutation"
    BOOTSTRAP = "did_bootstrap"
    CLUSTER_BOOTSTRAP = "did_cluster_bootstrap"
    BLOCK_BOOTSTRAP_DEPENDENCE = "did_block_bootstrap_dependence"
    CLUSTER_ROBUST = "did_cluster_robust"
    MATCHED_PAIR = "did_matched_pair"
    MATCHED_BLOCK_STRATIFIED = "did_matched_block_stratified"
    STAGGERED_ACTIVATION = "did_staggered_activation"
    DETERMINISTIC_UNKNOWN_ASSIGNMENT = "did_deterministic_unknown_assignment"
    MULTICELL_SHARED_CONTROL = "did_multicell_shared_control"
    SPARSE_COUNT_BINARY_RATE_OUTCOMES = "did_sparse_count_binary_rate_outcomes"
    TREND_VIOLATION_SHORT_PRE_SMALL_N = "did_trend_violation_short_pre_small_n"


class AuditStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    RESTRICTED_RESEARCH = "restricted_research"
    REMEDIATION_REQUIRED = "remediation_required"
    CANDIDATE_AFTER_FUTURE_VALIDATION = "candidate_after_future_validation"
    RETIRE_OR_REPLACE = "retire_or_replace"


class AuditRequiredAction(str, Enum):
    BLOCK = "block"
    MARK_DIAGNOSTIC_ONLY = "mark_diagnostic_only"
    MARK_SENSITIVITY_ONLY = "mark_sensitivity_only"
    KEEP_RESEARCH_ONLY = "keep_research_only"
    REMEDIATE = "remediate"
    RETIRE_OR_REPLACE = "retire_or_replace"
    CANDIDATE_AFTER_FUTURE_VALIDATION = "candidate_after_future_validation"
    REQUIRE_NULL_CALIBRATION = "require_null_calibration"
    REQUIRE_DGP_COVERAGE = "require_dgp_coverage"
    REQUIRE_OBSERVED_DIAGNOSTICS = "require_observed_diagnostics"
    REQUIRE_DESIGN_STRESS_TEST = "require_design_stress_test"
    REQUIRE_FAILURE_REGISTRY_CONSULT = "require_failure_registry_consult"
    REQUIRE_PARALLEL_TRENDS = "require_parallel_trends"
    REQUIRE_CLUSTER_COUNT = "require_cluster_count"


class DesignContext(str, Enum):
    SINGLE_TREATED_GEO = "single_treated_geo"
    MULTI_TREATED_GEO = "multi_treated_geo"
    MATCHED_PAIR = "matched_pair"
    MATCHED_BLOCK = "matched_block"
    STRATIFIED = "stratified"
    STAGGERED = "staggered"
    FIXED_DETERMINISTIC = "fixed_deterministic"
    UNKNOWN_ASSIGNMENT = "unknown_assignment"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    ALL = "all"


class InferenceContext(str, Enum):
    POINT_ONLY = "point_only"
    RANDOMIZATION = "randomization"
    PERMUTATION = "permutation"
    BOOTSTRAP = "bootstrap"
    CLUSTER_BOOTSTRAP = "cluster_bootstrap"
    BLOCK_BOOTSTRAP = "block_bootstrap"
    CLUSTER_ROBUST = "cluster_robust"
    NO_VALID_INFERENCE = "no_valid_inference"
    MAX_T = "max_t"
    ALL = "all"


REQUIRED_PATHS = frozenset(DidPath)
REQUIRED_STATUSES = frozenset(AuditStatus)
REQUIRED_ACTIONS = frozenset(AuditRequiredAction)


@dataclass(frozen=True)
class DidSuitabilityAuditRow:
    path_id: str
    name: str
    did_path: DidPath
    current_status: AuditStatus
    required_design_conditions: tuple[str, ...]
    observed_diagnostic_triggers: tuple[str, ...]
    dgp_triggers: tuple[str, ...]
    failure_registry_links: tuple[str, ...]
    affected_designs: tuple[DesignContext, ...]
    affected_inference_paths: tuple[InferenceContext, ...]
    required_action: AuditRequiredAction
    promotion_blocking: bool
    bootstrap_allowed_as_research_candidate: bool
    randomization_allowed_as_research_candidate: bool
    recommended_next_artifact: str | None
    notes: str


def _row(
    path_id: str,
    name: str,
    did_path: DidPath,
    current_status: AuditStatus,
    description_note: str,
    *,
    required_design_conditions: tuple[str, ...],
    observed_diagnostic_triggers: tuple[str, ...],
    dgp_triggers: tuple[str, ...],
    failure_registry_links: tuple[str, ...],
    affected_designs: tuple[DesignContext, ...],
    affected_inference_paths: tuple[InferenceContext, ...],
    required_action: AuditRequiredAction,
    promotion_blocking: bool = False,
    bootstrap_allowed_as_research_candidate: bool = False,
    randomization_allowed_as_research_candidate: bool = False,
    recommended_next_artifact: str | None = None,
) -> DidSuitabilityAuditRow:
    return DidSuitabilityAuditRow(
        path_id=path_id,
        name=name,
        did_path=did_path,
        current_status=current_status,
        required_design_conditions=required_design_conditions,
        observed_diagnostic_triggers=observed_diagnostic_triggers,
        dgp_triggers=dgp_triggers,
        failure_registry_links=failure_registry_links,
        affected_designs=affected_designs,
        affected_inference_paths=affected_inference_paths,
        required_action=required_action,
        promotion_blocking=promotion_blocking,
        bootstrap_allowed_as_research_candidate=bootstrap_allowed_as_research_candidate,
        randomization_allowed_as_research_candidate=randomization_allowed_as_research_candidate,
        recommended_next_artifact=recommended_next_artifact,
        notes=description_note,
    )


_ALL_D = (DesignContext.ALL,)
_ALL_I = (InferenceContext.ALL,)


def build_did_randomization_bootstrap_suitability_audit() -> tuple[DidSuitabilityAuditRow, ...]:
    """Return metadata-only DID randomization/bootstrap suitability audit rows."""
    return (
        # Point estimate
        _row(
            "DID-AUD-001", "did_point_estimate_diagnostic", DidPath.POINT_ESTIMATE,
            AuditStatus.DIAGNOSTIC_ONLY,
            "DID point estimate may support diagnostic ATT readouts when parallel-trend diagnostics pass.",
            required_design_conditions=("parallel_trends_plausible", "adequate_pre_period"),
            observed_diagnostic_triggers=("OPD-PF-001", "OPD-PF-003"),
            dgp_triggers=("DGP-PF-001", "DGP-PF-003"),
            failure_registry_links=("FM-ES-005",),
            affected_designs=(DesignContext.SINGLE_TREATED_GEO, DesignContext.MULTI_TREATED_GEO),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-002", "did_point_production_pvalue_blocked", DidPath.POINT_ESTIMATE,
            AuditStatus.BLOCKED,
            "DID point estimate alone does not authorize production p-values.",
            required_design_conditions=("no_production_pvalue_from_point",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            failure_registry_links=("FM-INF-011", "FM-DB-009"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-003", "did_point_causal_ci_blocked", DidPath.POINT_ESTIMATE,
            AuditStatus.BLOCKED,
            "DID causal confidence intervals remain unauthorized without validated inference path.",
            required_design_conditions=("validated_inference_path_required",),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-007",),
            failure_registry_links=("FM-DB-010",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-004", "did_point_requires_observed_diagnostics", DidPath.POINT_ESTIMATE,
            AuditStatus.REMEDIATION_REQUIRED,
            "Observed-panel diagnostics required before DID point use.",
            required_design_conditions=("observed_diagnostics_complete",),
            observed_diagnostic_triggers=("OPD-PS-001", "OPD-PF-001"),
            dgp_triggers=("DGP-CP-003",),
            failure_registry_links=("FM-CP-003",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS,
            promotion_blocking=True,
        ),
        # Design/randomization inference
        _row(
            "DID-AUD-010", "did_randomization_known_assignment_required", DidPath.DESIGN_RANDOMIZATION,
            AuditStatus.BLOCKED,
            "DID randomization inference requires known assignment mechanism.",
            required_design_conditions=("known_assignment_mechanism", "complete_randomization_or_documented_rerandomization"),
            observed_diagnostic_triggers=("OPD-AD-001",),
            dgp_triggers=("DGP-AD-009", "DGP-INF-002"),
            failure_registry_links=("FM-DA-001",),
            affected_designs=(DesignContext.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=False,
        ),
        _row(
            "DID-AUD-011", "did_randomization_valid_support_required", DidPath.DESIGN_RANDOMIZATION,
            AuditStatus.RESTRICTED_RESEARCH,
            "Randomization candidate requires non-degenerate assignment support.",
            required_design_conditions=("assignment_support_non_degenerate", "treatment_count_preserved"),
            observed_diagnostic_triggers=("OPD-AD-009", "OPD-AD-010"),
            dgp_triggers=("DGP-AD-010", "DGP-INF-001"),
            failure_registry_links=("FM-DA-007", "FM-DA-008"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=True,
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "DID-AUD-012", "did_randomization_not_production", DidPath.DESIGN_RANDOMIZATION,
            AuditStatus.BLOCKED,
            "DID randomization inference is not production-authorized.",
            required_design_conditions=("null_calibration_passed", "assignment_stress_passed"),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-001",),
            failure_registry_links=("FM-INF-011", "FM-DB-009"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-013", "did_randomization_future_validation", DidPath.DESIGN_RANDOMIZATION,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Randomization may become research candidate after null calibration and stress tests.",
            required_design_conditions=("known_assignment", "valid_support", "null_calibration"),
            observed_diagnostic_triggers=("OPD-AD-002",),
            dgp_triggers=("DGP-INF-001", "DGP-CP-001"),
            failure_registry_links=("FM-CP-001",),
            affected_designs=(DesignContext.MATCHED_PAIR, DesignContext.MATCHED_BLOCK, DesignContext.STRATIFIED),
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.CANDIDATE_AFTER_FUTURE_VALIDATION,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-014", "did_randomization_deterministic_blocked", DidPath.DESIGN_RANDOMIZATION,
            AuditStatus.BLOCKED,
            "Deterministic assignment cannot support randomization inference for DID.",
            required_design_conditions=("randomized_assignment_only",),
            observed_diagnostic_triggers=("OPD-AD-002",),
            dgp_triggers=("DGP-AD-008",),
            failure_registry_links=("FM-DA-002",),
            affected_designs=(DesignContext.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        # Permutation
        _row(
            "DID-AUD-020", "did_permutation_valid_support_required", DidPath.PERMUTATION,
            AuditStatus.RESTRICTED_RESEARCH,
            "Permutation requires valid pseudo-assignment support.",
            required_design_conditions=("permutation_support_non_degenerate",),
            observed_diagnostic_triggers=("OPD-AD-009",),
            dgp_triggers=("DGP-INF-003",),
            failure_registry_links=("FM-DA-007", "FM-DA-008"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PERMUTATION,),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-021", "did_permutation_not_production_pvalue", DidPath.PERMUTATION,
            AuditStatus.BLOCKED,
            "Permutation rank is not a production p-value for DID.",
            required_design_conditions=("governed_permutation_semantics",),
            observed_diagnostic_triggers=("OPD-IR-002",),
            dgp_triggers=("DGP-INF-003",),
            failure_registry_links=("FM-INF-001", "FM-DB-009"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PERMUTATION,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-022", "did_permutation_diagnostic_only", DidPath.PERMUTATION,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Permutation may remain diagnostic null-monitor only.",
            required_design_conditions=("assignment_support_documented",),
            observed_diagnostic_triggers=("OPD-IR-002",),
            dgp_triggers=("DGP-INF-003",),
            failure_registry_links=("FM-INF-001",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PERMUTATION,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-023", "did_permutation_bootstrap_substitution_blocked", DidPath.PERMUTATION,
            AuditStatus.BLOCKED,
            "Permutation cannot be substituted by bootstrap when assignment invalid.",
            required_design_conditions=("valid_assignment_before_permutation",),
            observed_diagnostic_triggers=("OPD-AD-001",),
            dgp_triggers=("DGP-INF-002",),
            failure_registry_links=("FM-INF-003", "FM-DA-001"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.PERMUTATION, InferenceContext.BOOTSTRAP),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        # Bootstrap
        _row(
            "DID-AUD-030", "did_bootstrap_dependence_validation_required", DidPath.BOOTSTRAP,
            AuditStatus.REMEDIATION_REQUIRED,
            "Bootstrap requires dependence/outcome/DGP validation.",
            required_design_conditions=("dependence_structure_documented", "outcome_scale_valid"),
            observed_diagnostic_triggers=("OPD-TD-001", "OPD-OM-001"),
            dgp_triggers=("DGP-INF-006", "DGP-NV-005"),
            failure_registry_links=("FM-INF-003", "FM-CP-002"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BOOTSTRAP,),
            required_action=AuditRequiredAction.REMEDIATE,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-031", "did_bootstrap_not_production", DidPath.BOOTSTRAP,
            AuditStatus.BLOCKED,
            "DID bootstrap is not production-valid causal inference.",
            required_design_conditions=("null_calibration_passed",),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-INF-006",),
            failure_registry_links=("FM-INF-004", "FM-DB-010"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BOOTSTRAP,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-032", "did_bootstrap_does_not_fix_assignment", DidPath.BOOTSTRAP,
            AuditStatus.BLOCKED,
            "Bootstrap cannot substitute for invalid assignment mechanism.",
            required_design_conditions=("valid_assignment_or_diagnostic_only",),
            observed_diagnostic_triggers=("OPD-AD-001", "OPD-AD-002"),
            dgp_triggers=("DGP-INF-002",),
            failure_registry_links=("FM-INF-003", "FM-DA-001", "FM-DA-002"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BOOTSTRAP, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-033", "did_bootstrap_research_candidate", DidPath.BOOTSTRAP,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Bootstrap may be research candidate after dependence DGP validation.",
            required_design_conditions=("parallel_trends_plausible", "dependence_validated"),
            observed_diagnostic_triggers=("OPD-PF-003", "OPD-TD-001"),
            dgp_triggers=("DGP-INF-006", "DGP-CP-001"),
            failure_registry_links=("FM-CP-001",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BOOTSTRAP,),
            required_action=AuditRequiredAction.CANDIDATE_AFTER_FUTURE_VALIDATION,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-034", "did_bootstrap_requires_null_calibration", DidPath.BOOTSTRAP,
            AuditStatus.RESTRICTED_RESEARCH,
            "Bootstrap promotion requires null calibration harness.",
            required_design_conditions=("null_calibration_harness",),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-CP-001",),
            failure_registry_links=("FM-CP-001",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BOOTSTRAP,),
            required_action=AuditRequiredAction.REQUIRE_NULL_CALIBRATION,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        # Cluster bootstrap
        _row(
            "DID-AUD-040", "did_cluster_bootstrap_few_clusters_blocked", DidPath.CLUSTER_BOOTSTRAP,
            AuditStatus.BLOCKED,
            "Cluster bootstrap blocked when cluster count too small.",
            required_design_conditions=("minimum_cluster_count",),
            observed_diagnostic_triggers=("OPD-IR-006",),
            dgp_triggers=("DGP-INF-008",),
            failure_registry_links=("FM-INF-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.CLUSTER_BOOTSTRAP,),
            required_action=AuditRequiredAction.REQUIRE_CLUSTER_COUNT,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-041", "did_cluster_bootstrap_research_only", DidPath.CLUSTER_BOOTSTRAP,
            AuditStatus.RESTRICTED_RESEARCH,
            "Cluster bootstrap remains restricted research when clusters marginal.",
            required_design_conditions=("cluster_count_marginal", "dependence_validated"),
            observed_diagnostic_triggers=("OPD-IR-006", "OPD-PS-006"),
            dgp_triggers=("DGP-INF-008",),
            failure_registry_links=("FM-INF-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.CLUSTER_BOOTSTRAP,),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-042", "did_cluster_bootstrap_not_production_ci", DidPath.CLUSTER_BOOTSTRAP,
            AuditStatus.BLOCKED,
            "Cluster bootstrap intervals are not production causal CIs.",
            required_design_conditions=("null_calibration_passed",),
            observed_diagnostic_triggers=("OPD-IR-005",),
            dgp_triggers=("DGP-INF-008",),
            failure_registry_links=("FM-DB-010",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.CLUSTER_BOOTSTRAP,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        # Block bootstrap under dependence
        _row(
            "DID-AUD-050", "did_block_bootstrap_temporal_dependence", DidPath.BLOCK_BOOTSTRAP_DEPENDENCE,
            AuditStatus.RESTRICTED_RESEARCH,
            "Block bootstrap under temporal dependence requires DGP validation.",
            required_design_conditions=("block_structure_matches_dependence",),
            observed_diagnostic_triggers=("OPD-TD-001", "OPD-IR-004"),
            dgp_triggers=("DGP-INF-006", "DGP-NV-005"),
            failure_registry_links=("FM-INF-003", "FM-TD-001"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_BOOTSTRAP,),
            required_action=AuditRequiredAction.REQUIRE_DGP_COVERAGE,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-051", "did_block_bootstrap_invalid_dependence_blocked", DidPath.BLOCK_BOOTSTRAP_DEPENDENCE,
            AuditStatus.BLOCKED,
            "Block bootstrap blocked under misspecified dependence.",
            required_design_conditions=("dependence_correctly_specified",),
            observed_diagnostic_triggers=("OPD-TD-001",),
            dgp_triggers=("DGP-NV-005",),
            failure_registry_links=("FM-INF-003",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_BOOTSTRAP,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-052", "did_block_bootstrap_diagnostic_only", DidPath.BLOCK_BOOTSTRAP_DEPENDENCE,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Block bootstrap may remain diagnostic instability probe only.",
            required_design_conditions=("diagnostic_use_only",),
            observed_diagnostic_triggers=("OPD-IR-004",),
            dgp_triggers=("DGP-INF-006",),
            failure_registry_links=("FM-INF-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BLOCK_BOOTSTRAP,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        # Cluster robust
        _row(
            "DID-AUD-060", "did_cluster_robust_few_clusters_blocked", DidPath.CLUSTER_ROBUST,
            AuditStatus.BLOCKED,
            "Cluster-robust inference blocked with too few clusters.",
            required_design_conditions=("minimum_cluster_count",),
            observed_diagnostic_triggers=("OPD-IR-006",),
            dgp_triggers=("DGP-INF-008",),
            failure_registry_links=("FM-INF-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.CLUSTER_ROBUST,),
            required_action=AuditRequiredAction.REQUIRE_CLUSTER_COUNT,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-061", "did_cluster_robust_research_candidate", DidPath.CLUSTER_ROBUST,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Cluster-robust may be research candidate with adequate clusters and diagnostics.",
            required_design_conditions=("adequate_cluster_count", "cluster_homogeneity_plausible"),
            observed_diagnostic_triggers=("OPD-IR-006",),
            dgp_triggers=("DGP-INF-008",),
            failure_registry_links=("FM-INF-006",),
            affected_designs=(DesignContext.MATCHED_BLOCK, DesignContext.STRATIFIED),
            affected_inference_paths=(InferenceContext.CLUSTER_ROBUST,),
            required_action=AuditRequiredAction.CANDIDATE_AFTER_FUTURE_VALIDATION,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-062", "did_cluster_robust_not_production", DidPath.CLUSTER_ROBUST,
            AuditStatus.BLOCKED,
            "Cluster-robust analytic inference not production-authorized.",
            required_design_conditions=("null_calibration_passed",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            failure_registry_links=("FM-INF-011",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.CLUSTER_ROBUST,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        # Matched-pair
        _row(
            "DID-AUD-070", "did_matched_pair_integrity_required", DidPath.MATCHED_PAIR,
            AuditStatus.BLOCKED,
            "Matched-pair DID requires pair integrity for randomization inference.",
            required_design_conditions=("pair_membership_complete", "exactly_one_treated_per_pair"),
            observed_diagnostic_triggers=("OPD-AD-003",),
            dgp_triggers=("DGP-AD-002",),
            failure_registry_links=("FM-DA-004",),
            affected_designs=(DesignContext.MATCHED_PAIR,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=True,
        ),
        _row(
            "DID-AUD-071", "did_matched_pair_research_only", DidPath.MATCHED_PAIR,
            AuditStatus.RESTRICTED_RESEARCH,
            "Matched-pair DID randomization remains restricted research.",
            required_design_conditions=("pair_support_valid",),
            observed_diagnostic_triggers=("OPD-AD-003",),
            dgp_triggers=("DGP-AD-002",),
            failure_registry_links=("FM-DA-004",),
            affected_designs=(DesignContext.MATCHED_PAIR,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.PERMUTATION),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=True,
        ),
        # Matched-block/stratified
        _row(
            "DID-AUD-080", "did_matched_block_integrity_required", DidPath.MATCHED_BLOCK_STRATIFIED,
            AuditStatus.BLOCKED,
            "Matched-block integrity failure blocks block randomization inference.",
            required_design_conditions=("block_membership_complete", "block_treatment_counts_preserved"),
            observed_diagnostic_triggers=("OPD-AD-004",),
            dgp_triggers=("DGP-AD-003",),
            failure_registry_links=("FM-DA-005",),
            affected_designs=(DesignContext.MATCHED_BLOCK,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.CLUSTER_ROBUST),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-081", "did_stratified_heterogeneity_sensitivity", DidPath.MATCHED_BLOCK_STRATIFIED,
            AuditStatus.SENSITIVITY_ONLY,
            "Stratified DID heterogeneity routes to sensitivity-only analysis.",
            required_design_conditions=("stratum_quotas_preserved",),
            observed_diagnostic_triggers=("OPD-AD-005",),
            dgp_triggers=("DGP-AD-004",),
            failure_registry_links=("FM-DA-006",),
            affected_designs=(DesignContext.STRATIFIED,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.POINT_ONLY),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-082", "did_stratified_research_candidate", DidPath.MATCHED_BLOCK_STRATIFIED,
            AuditStatus.RESTRICTED_RESEARCH,
            "Stratified DID randomization candidate after stress tests.",
            required_design_conditions=("stratum_support_non_degenerate",),
            observed_diagnostic_triggers=("OPD-AD-005",),
            dgp_triggers=("DGP-AD-004",),
            failure_registry_links=("FM-DA-006",),
            affected_designs=(DesignContext.STRATIFIED,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            randomization_allowed_as_research_candidate=True,
        ),
        # Staggered activation
        _row(
            "DID-AUD-090", "did_staggered_timing_research_required", DidPath.STAGGERED_ACTIVATION,
            AuditStatus.RESTRICTED_RESEARCH,
            "Staggered activation requires explicit timing/estimand research handling.",
            required_design_conditions=("staggered_estimand_specified", "no_twfe_overclaim"),
            observed_diagnostic_triggers=("OPD-TE-004",),
            dgp_triggers=("DGP-TE-004",),
            failure_registry_links=("FM-TE-004",),
            affected_designs=(DesignContext.STAGGERED,),
            affected_inference_paths=(InferenceContext.POINT_ONLY, InferenceContext.CLUSTER_ROBUST),
            required_action=AuditRequiredAction.KEEP_RESEARCH_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-091", "did_staggered_twfe_blocked", DidPath.STAGGERED_ACTIVATION,
            AuditStatus.BLOCKED,
            "Naive TWFE over staggered timing blocked without heterogeneity-robust estimand.",
            required_design_conditions=("heterogeneity_robust_estimand",),
            observed_diagnostic_triggers=("OPD-TE-004",),
            dgp_triggers=("DGP-TE-004",),
            failure_registry_links=("FM-TE-004", "FM-ES-005"),
            affected_designs=(DesignContext.STAGGERED,),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-092", "did_staggered_diagnostic_only", DidPath.STAGGERED_ACTIVATION,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Staggered DID may remain diagnostic timing decomposition only.",
            required_design_conditions=("timing_decomposition_documented",),
            observed_diagnostic_triggers=("OPD-TE-001", "OPD-TE-004"),
            dgp_triggers=("DGP-TE-004",),
            failure_registry_links=("FM-TE-001",),
            affected_designs=(DesignContext.STAGGERED,),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        # Deterministic/unknown assignment
        _row(
            "DID-AUD-100", "did_unknown_assignment_blocks_inference", DidPath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.BLOCKED,
            "Unknown assignment blocks DID design-based inference.",
            required_design_conditions=("known_assignment_mechanism",),
            observed_diagnostic_triggers=("OPD-AD-001",),
            dgp_triggers=("DGP-AD-009",),
            failure_registry_links=("FM-DA-001",),
            affected_designs=(DesignContext.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-101", "did_deterministic_not_randomized", DidPath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.BLOCKED,
            "Deterministic assignment cannot support DID randomization inference.",
            required_design_conditions=("randomized_or_documented_falsification",),
            observed_diagnostic_triggers=("OPD-AD-002",),
            dgp_triggers=("DGP-AD-008",),
            failure_registry_links=("FM-DA-002",),
            affected_designs=(DesignContext.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferenceContext.RANDOMIZATION,),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-102", "did_deterministic_diagnostic_only", DidPath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Deterministic DID may remain falsification/diagnostic-only.",
            required_design_conditions=("falsification_contract",),
            observed_diagnostic_triggers=("OPD-AD-002",),
            dgp_triggers=("DGP-AD-008",),
            failure_registry_links=("FM-DA-002",),
            affected_designs=(DesignContext.FIXED_DETERMINISTIC,),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-103", "did_bootstrap_cannot_fix_unknown_assignment", DidPath.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            AuditStatus.BLOCKED,
            "Bootstrap cannot fix unknown assignment for DID.",
            required_design_conditions=("assignment_known_before_bootstrap",),
            observed_diagnostic_triggers=("OPD-AD-001",),
            dgp_triggers=("DGP-INF-002",),
            failure_registry_links=("FM-INF-003", "FM-DA-001"),
            affected_designs=(DesignContext.UNKNOWN_ASSIGNMENT,),
            affected_inference_paths=(InferenceContext.BOOTSTRAP, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        # Multicell/shared-control
        _row(
            "DID-AUD-110", "did_multicell_shared_control_blocked", DidPath.MULTICELL_SHARED_CONTROL,
            AuditStatus.BLOCKED,
            "Shared-control dependence blocks naive multicell DID inference.",
            required_design_conditions=("dependence_handling_specified",),
            observed_diagnostic_triggers=("OPD-MC-001", "OPD-AD-008"),
            dgp_triggers=("DGP-MC-002",),
            failure_registry_links=("FM-DA-009",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.MAX_T, InferenceContext.NO_VALID_INFERENCE),
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "DID-AUD-111", "did_multicell_winner_selection_risk", DidPath.MULTICELL_SHARED_CONTROL,
            AuditStatus.RETIRE_OR_REPLACE,
            "Winner-selection risk requires retire/replace or multiplicity research.",
            required_design_conditions=("multiplicity_adjustment",),
            observed_diagnostic_triggers=("OPD-MC-003", "OPD-MC-004"),
            dgp_triggers=("DGP-MC-004", "DGP-INF-011"),
            failure_registry_links=("FM-DA-010", "FM-INF-009"),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.MAX_T,),
            required_action=AuditRequiredAction.RETIRE_OR_REPLACE,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "DID-AUD-112", "did_multicell_multiplicity_research_required", DidPath.MULTICELL_SHARED_CONTROL,
            AuditStatus.CANDIDATE_AFTER_FUTURE_VALIDATION,
            "Multicell DID requires max-T/stepdown research before promotion.",
            required_design_conditions=("max_t_or_stepdown_research",),
            observed_diagnostic_triggers=("OPD-MC-004", "OPD-IR-009"),
            dgp_triggers=("DGP-INF-011", "DGP-MC-007"),
            failure_registry_links=("FM-INF-009", "FM-INF-010"),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.MAX_T,),
            required_action=AuditRequiredAction.CANDIDATE_AFTER_FUTURE_VALIDATION,
            promotion_blocking=True,
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "DID-AUD-113", "did_multicell_pooled_estimand_sensitivity", DidPath.MULTICELL_SHARED_CONTROL,
            AuditStatus.SENSITIVITY_ONLY,
            "Pooled multicell DID estimand ambiguity routes to sensitivity-only.",
            required_design_conditions=("per_cell_estimand_preferred",),
            observed_diagnostic_triggers=("OPD-MC-005",),
            dgp_triggers=("DGP-MC-005",),
            failure_registry_links=("FM-DA-010",),
            affected_designs=(DesignContext.MULTICELL_SHARED_CONTROL,),
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        # Sparse/count/binary/rate outcomes
        _row(
            "DID-AUD-120", "did_sparse_count_gaussian_blocked", DidPath.SPARSE_COUNT_BINARY_RATE_OUTCOMES,
            AuditStatus.BLOCKED,
            "Sparse counts modeled as Gaussian DID blocked without outcome diagnostics.",
            required_design_conditions=("outcome_scale_match",),
            observed_diagnostic_triggers=("OPD-OM-003", "OPD-OM-004"),
            dgp_triggers=("DGP-OM-003", "DGP-OM-004"),
            failure_registry_links=("FM-OM-003", "FM-OM-004"),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY, InferenceContext.BOOTSTRAP),
            required_action=AuditRequiredAction.REQUIRE_DGP_COVERAGE,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-121", "did_binary_binomial_required", DidPath.SPARSE_COUNT_BINARY_RATE_OUTCOMES,
            AuditStatus.REMEDIATION_REQUIRED,
            "Binary outcomes require binomial/logit-scale diagnostics and DGP coverage.",
            required_design_conditions=("binary_outcome_model",),
            observed_diagnostic_triggers=("OPD-OM-005",),
            dgp_triggers=("DGP-OM-005",),
            failure_registry_links=("FM-OM-005",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.REQUIRE_OBSERVED_DIAGNOSTICS,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-122", "did_rate_denominator_required", DidPath.SPARSE_COUNT_BINARY_RATE_OUTCOMES,
            AuditStatus.SENSITIVITY_ONLY,
            "Rate outcomes without denominator diagnostics are sensitivity-only.",
            required_design_conditions=("rate_denominator_present",),
            observed_diagnostic_triggers=("OPD-OM-006",),
            dgp_triggers=("DGP-OM-006",),
            failure_registry_links=("FM-OM-006",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-123", "did_zero_inflation_dgp_required", DidPath.SPARSE_COUNT_BINARY_RATE_OUTCOMES,
            AuditStatus.RESTRICTED_RESEARCH,
            "Zero-inflated outcomes require explicit DGP coverage before promotion.",
            required_design_conditions=("zero_inflation_handled",),
            observed_diagnostic_triggers=("OPD-OM-004",),
            dgp_triggers=("DGP-OM-004",),
            failure_registry_links=("FM-OM-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.BOOTSTRAP,),
            required_action=AuditRequiredAction.REQUIRE_DGP_COVERAGE,
            promotion_blocking=True,
            bootstrap_allowed_as_research_candidate=True,
        ),
        # Trend violation / short pre / small-N
        _row(
            "DID-AUD-130", "did_parallel_trends_violation_blocked", DidPath.TREND_VIOLATION_SHORT_PRE_SMALL_N,
            AuditStatus.BLOCKED,
            "Parallel-trend violations block DID promotion.",
            required_design_conditions=("parallel_trends_pass_or_waived",),
            observed_diagnostic_triggers=("OPD-PF-003",),
            dgp_triggers=("DGP-PF-003",),
            failure_registry_links=("FM-PF-003", "FM-ES-005"),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_PARALLEL_TRENDS,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-131", "did_short_pre_period_blocked", DidPath.TREND_VIOLATION_SHORT_PRE_SMALL_N,
            AuditStatus.BLOCKED,
            "Short pre-period blocks DID inference promotion.",
            required_design_conditions=("minimum_pre_period_length",),
            observed_diagnostic_triggers=("OPD-PS-004",),
            dgp_triggers=("DGP-PS-004",),
            failure_registry_links=("FM-PS-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-132", "did_small_n_panel_blocked", DidPath.TREND_VIOLATION_SHORT_PRE_SMALL_N,
            AuditStatus.BLOCKED,
            "Small-N panels block DID inference promotion.",
            required_design_conditions=("minimum_panel_size",),
            observed_diagnostic_triggers=("OPD-PS-006", "OPD-PS-010"),
            dgp_triggers=("DGP-PS-010",),
            failure_registry_links=("FM-PS-010", "FM-PS-006"),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-133", "did_trend_violation_sensitivity_only", DidPath.TREND_VIOLATION_SHORT_PRE_SMALL_N,
            AuditStatus.SENSITIVITY_ONLY,
            "Trend violations may allow sensitivity-only DID readouts.",
            required_design_conditions=("sensitivity_label_required",),
            observed_diagnostic_triggers=("OPD-PF-003", "OPD-PF-006"),
            dgp_triggers=("DGP-PF-003",),
            failure_registry_links=("FM-PF-003",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_SENSITIVITY_ONLY,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-134", "did_poor_pre_fit_diagnostic_only", DidPath.TREND_VIOLATION_SHORT_PRE_SMALL_N,
            AuditStatus.DIAGNOSTIC_ONLY,
            "Poor pre-period fit routes DID to diagnostic-only.",
            required_design_conditions=("pre_fit_acceptable_or_labeled",),
            observed_diagnostic_triggers=("OPD-PF-001", "OPD-PF-002"),
            dgp_triggers=("DGP-PF-001",),
            failure_registry_links=("FM-PF-001",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.POINT_ONLY,),
            required_action=AuditRequiredAction.MARK_DIAGNOSTIC_ONLY,
            promotion_blocking=True,
        ),
        # Cross-cutting governance
        _row(
            "DID-AUD-140", "did_failure_registry_consult_required", DidPath.POINT_ESTIMATE,
            AuditStatus.REMEDIATION_REQUIRED,
            "All DID promotion paths must consult failure registry.",
            required_design_conditions=("failure_registry_consulted",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-CP-004",),
            failure_registry_links=("FM-CP-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.REQUIRE_FAILURE_REGISTRY_CONSULT,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-141", "did_design_stress_gate", DidPath.DESIGN_RANDOMIZATION,
            AuditStatus.REMEDIATION_REQUIRED,
            "Design assignment stress tests required for randomization/permutation paths.",
            required_design_conditions=("assignment_stress_tests_passed",),
            observed_diagnostic_triggers=("OPD-AD-009",),
            dgp_triggers=("DGP-AD-010",),
            failure_registry_links=("FM-CP-004",),
            affected_designs=_ALL_D,
            affected_inference_paths=(InferenceContext.RANDOMIZATION, InferenceContext.PERMUTATION),
            required_action=AuditRequiredAction.REQUIRE_DESIGN_STRESS_TEST,
            promotion_blocking=True,
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "DID-AUD-142", "did_trend_despite_violation_blocked", DidPath.TREND_VIOLATION_SHORT_PRE_SMALL_N,
            AuditStatus.RETIRE_OR_REPLACE,
            "DID promoted despite trend violation must be retired or replaced.",
            required_design_conditions=("parallel_trends_required",),
            observed_diagnostic_triggers=("OPD-PF-003",),
            dgp_triggers=("DGP-PF-003",),
            failure_registry_links=("FM-ES-005",),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.RETIRE_OR_REPLACE,
            promotion_blocking=True,
        ),
        _row(
            "DID-AUD-143", "did_global_production_block", DidPath.POINT_ESTIMATE,
            AuditStatus.BLOCKED,
            "Global block on DID production inference across all paths.",
            required_design_conditions=("production_inference_blocked",),
            observed_diagnostic_triggers=("OPD-IR-010",),
            dgp_triggers=("DGP-INF-013",),
            failure_registry_links=("FM-INF-011", "FM-DB-009", "FM-DB-010"),
            affected_designs=_ALL_D,
            affected_inference_paths=_ALL_I,
            required_action=AuditRequiredAction.BLOCK,
            promotion_blocking=True,
        ),
    )


def filter_did_randomization_bootstrap_suitability_audit(
    rows: tuple[DidSuitabilityAuditRow, ...],
    *,
    did_path: DidPath | None = None,
    current_status: AuditStatus | None = None,
    required_action: AuditRequiredAction | None = None,
    promotion_blocking: bool | None = None,
    bootstrap_allowed_as_research_candidate: bool | None = None,
    randomization_allowed_as_research_candidate: bool | None = None,
) -> tuple[DidSuitabilityAuditRow, ...]:
    """Filter DID suitability audit rows by optional criteria."""
    result: list[DidSuitabilityAuditRow] = []
    for row in rows:
        if did_path is not None and row.did_path != did_path:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if required_action is not None and row.required_action != required_action:
            continue
        if promotion_blocking is not None and row.promotion_blocking != promotion_blocking:
            continue
        if bootstrap_allowed_as_research_candidate is not None and row.bootstrap_allowed_as_research_candidate != bootstrap_allowed_as_research_candidate:
            continue
        if randomization_allowed_as_research_candidate is not None and row.randomization_allowed_as_research_candidate != randomization_allowed_as_research_candidate:
            continue
        result.append(row)
    return tuple(result)


def validate_did_randomization_bootstrap_suitability_audit(
    rows: tuple[DidSuitabilityAuditRow, ...],
) -> dict[str, Any]:
    """Validate DID suitability audit thresholds and linkage requirements."""
    issues: list[str] = []
    path_ids = [r.path_id for r in rows]

    if len(rows) < MIN_AUDIT_ROW_COUNT:
        issues.append(f"audit_row_count {len(rows)} < {MIN_AUDIT_ROW_COUNT}")
    if len(path_ids) != len(set(path_ids)):
        issues.append("duplicate path_id values")

    status_counts = Counter(r.current_status for r in rows)
    action_counts = Counter(r.required_action for r in rows)
    failure_mode_counts: Counter[str] = Counter()
    for row in rows:
        for fm in row.failure_registry_links:
            failure_mode_counts[fm] += 1

    for path in REQUIRED_PATHS:
        if not any(r.did_path == path for r in rows):
            issues.append(f"missing did path: {path.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for action in REQUIRED_ACTIONS:
        if action_counts.get(action, 0) == 0:
            issues.append(f"missing required_action: {action.value}")

    bootstrap_candidates = [r for r in rows if r.bootstrap_allowed_as_research_candidate]
    randomization_candidates = [r for r in rows if r.randomization_allowed_as_research_candidate]
    promotion_blockers = [r for r in rows if r.promotion_blocking]

    if not bootstrap_candidates:
        issues.append("no bootstrap_allowed_as_research_candidate rows")
    if not randomization_candidates:
        issues.append("no randomization_allowed_as_research_candidate rows")
    if not promotion_blockers:
        issues.append("no promotion_blocking rows")

    unlinked_observed = [r.path_id for r in rows if not r.observed_diagnostic_triggers]
    if unlinked_observed:
        issues.append(f"rows missing observed_diagnostic_triggers: {unlinked_observed}")

    unlinked_dgp = [r.path_id for r in rows if not r.dgp_triggers]
    if unlinked_dgp:
        issues.append(f"rows missing dgp_triggers: {unlinked_dgp}")

    unlinked_fm = [r.path_id for r in rows if not r.failure_registry_links]
    if unlinked_fm:
        issues.append(f"rows missing failure_registry_links: {unlinked_fm}")

    unlinked_design = [r.path_id for r in rows if not r.required_design_conditions]
    if unlinked_design:
        issues.append(f"rows missing required_design_conditions: {unlinked_design}")

    return {
        "valid": not issues,
        "audit_row_count": len(rows),
        "unique_path_ids": len(path_ids) == len(set(path_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in AuditStatus},
        "required_action_counts": {a.value: action_counts.get(a, 0) for a in AuditRequiredAction},
        "failure_mode_counts": dict(failure_mode_counts),
        "bootstrap_candidates_defined": bool(bootstrap_candidates),
        "randomization_candidates_defined": bool(randomization_candidates),
        "promotion_blockers_defined": bool(promotion_blockers),
        "all_paths_represented": all(any(r.did_path == p for r in rows) for p in REQUIRED_PATHS),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "all_actions_represented": all(action_counts.get(a, 0) > 0 for a in REQUIRED_ACTIONS),
        "issues": issues,
    }


def summarize_did_randomization_bootstrap_suitability_audit(
    rows: tuple[DidSuitabilityAuditRow, ...],
) -> dict[str, Any]:
    """Serialize DID suitability audit summary for archives."""
    validation = validate_did_randomization_bootstrap_suitability_audit(rows)
    path_counts = Counter(r.did_path.value for r in rows)

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "audit_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "required_action_counts": validation["required_action_counts"],
        "failure_mode_counts": validation["failure_mode_counts"],
        "did_path_counts": dict(path_counts),
        "downstream_work_paused": True,
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_DID_AUTH_FLAGS,
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
    rows = build_did_randomization_bootstrap_suitability_audit()
    validation = validate_did_randomization_bootstrap_suitability_audit(rows)
    summary = summarize_did_randomization_bootstrap_suitability_audit(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("audit_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("audit_row_count_at_least_50", len(rows) >= MIN_AUDIT_ROW_COUNT))
    scenarios.append(_scenario("path_ids_unique", validation["unique_path_ids"]))

    for path in REQUIRED_PATHS:
        present = any(r.did_path == path for r in rows)
        scenarios.append(_scenario(f"did_path_{path.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for action in REQUIRED_ACTIONS:
        count = sum(1 for r in rows if r.required_action == action)
        scenarios.append(_scenario(f"action_{action.value}_represented", count > 0))

    scenarios.append(_scenario("did_point_diagnostic_allowed", summary["did_point_diagnostic_allowed"] is True))
    scenarios.append(_scenario("did_production_inference_authorized_false", summary["did_production_inference_authorized"] is False))
    scenarios.append(_scenario("did_production_p_value_authorized_false", summary["did_production_p_value_authorized"] is False))
    scenarios.append(_scenario("did_causal_ci_authorized_false", summary["did_causal_ci_authorized"] is False))
    scenarios.append(_scenario("did_randomization_candidate_requires_known_assignment", summary["did_randomization_candidate_requires_known_assignment"] is True))
    scenarios.append(_scenario("did_permutation_candidate_requires_valid_assignment_support", summary["did_permutation_candidate_requires_valid_assignment_support"] is True))
    scenarios.append(_scenario("did_bootstrap_candidate_requires_dependence_validation", summary["did_bootstrap_candidate_requires_dependence_validation"] is True))
    scenarios.append(_scenario("bootstrap_does_not_fix_invalid_assignment", summary["bootstrap_does_not_fix_invalid_assignment"] is True))
    scenarios.append(_scenario("parallel_trends_required_before_promotion", summary["parallel_trends_required_before_promotion"] is True))
    scenarios.append(_scenario("staggered_timing_requires_research_handling", summary["staggered_timing_requires_research_handling"] is True))
    scenarios.append(_scenario("small_n_and_few_clusters_block_promotion", summary["small_n_and_few_clusters_block_promotion"] is True))
    scenarios.append(_scenario("sparse_count_binary_outcomes_require_dgp_coverage", summary["sparse_count_binary_outcomes_require_dgp_coverage"] is True))
    scenarios.append(_scenario("multicell_did_requires_multiplicity_research", summary["multicell_did_requires_multiplicity_research"] is True))
    scenarios.append(_scenario("observed_diagnostics_required", summary["observed_diagnostics_required"] is True))
    scenarios.append(_scenario("dgp_coverage_required", summary["dgp_coverage_required"] is True))
    scenarios.append(_scenario("failure_registry_consulted", summary["failure_registry_consulted"] is True))
    scenarios.append(_scenario("design_assignment_stress_required", summary["design_assignment_stress_required"] is True))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_multicell_max_t_research_scout_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_did_randomization_bootstrap_suitability_audit()
    validation = validate_did_randomization_bootstrap_suitability_audit(rows)
    summary = summarize_did_randomization_bootstrap_suitability_audit(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "audit_row_count": len(rows),
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
