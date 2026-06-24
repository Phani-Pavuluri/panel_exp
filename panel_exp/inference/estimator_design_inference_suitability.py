"""ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001 — cross-estimator inference suitability matrix.

Method architecture and inference-selection artifact only — not production authorization.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any

_ARTIFACT_ID = "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"
_VERDICT = "estimator_design_inference_suitability_matrix_defined_no_downstream_authorization"

MATRIX_WARNING = (
    "Estimator × design × inference suitability matrix is an architecture and selection "
    "artifact only — not production authorization, TrustReport expansion, CalibrationSignal, "
    "or downstream decisioning."
)

FORBIDDEN_OUTPUTS = (
    "production_p_value",
    "causal_confidence_interval",
    "trustreport_authorization",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "production_decisioning",
    "live_api",
    "scheduler",
    "budget_optimization",
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
    "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
    "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
    "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
)

INFERENCE_LAYER_DECISIONS = (
    "placebo_randomization_is_one_inference_family_not_the_full_inference_layer",
    "no_estimator_has_universal_default_inference",
    "inference_suitability_depends_on_estimator_design_assignment_estimand_geometry_adapter_and_calibration",
    "reusable_inference_requires_statistic_adapter_contracts",
    "estimator_specific_inference_requires_custom_validation",
    "tbrridge_remains_remediation_or_retirement",
    "bayesian_tbr_remains_posterior_diagnostic_or_research",
    "multicell_requires_dependence_and_multiplicity_research",
    "stratified_pooled_requires_heterogeneity_and_pooling_policy",
    "downstream_authorization_remains_paused",
)


class EstimatorFamily(str, Enum):
    SCM = "scm"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    DID = "did"
    TBRRIDGE = "tbrridge"
    TBR = "tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    SYNTHETIC_DID = "synthetic_did"
    TROP = "trop"


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


class InferenceFamily(str, Enum):
    UNIT_JACKKNIFE = "unit_jackknife"
    LEAVE_ONE_TREATED_OUT_SENSITIVITY = "leave_one_treated_out_sensitivity"
    TREATED_SET_PLACEBO_RANK = "treated_set_placebo_rank"
    STUDENTIZED_PLACEBO_RANK = "studentized_placebo_rank"
    DESIGN_BASED_RANDOMIZATION = "design_based_randomization"
    PERMUTATION = "permutation"
    BOOTSTRAP = "bootstrap"
    BLOCK_RESIDUAL_BOOTSTRAP = "block_residual_bootstrap"
    KFOLD_CROSS_FIT = "kfold_cross_fit"
    CONFORMAL = "conformal"
    BAYESIAN_POSTERIOR_INTERVAL = "bayesian_posterior_interval"
    BAYESIAN_POSTERIOR_PREDICTIVE_CHECK = "bayesian_posterior_predictive_check"
    CLUSTER_ROBUST_ANALYTIC = "cluster_robust_analytic"
    DID_BOOTSTRAP = "did_bootstrap"
    MAX_T_MULTIPLICITY = "max_t_multiplicity"
    STEPDOWN_MULTIPLICITY = "stepdown_multiplicity"
    NO_VALID_INFERENCE = "no_valid_inference"


class SuitabilityStatus(str, Enum):
    SUPPORTED_RESTRICTED_RESEARCH = "supported_restricted_research"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_REQUIRES_ADAPTER = "candidate_requires_adapter"
    CANDIDATE_REQUIRES_DESIGN_STRESS_TEST = "candidate_requires_design_stress_test"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    POSTERIOR_DIAGNOSTIC_ONLY = "posterior_diagnostic_only"
    MULTIPLICITY_RESEARCH_REQUIRED = "multiplicity_research_required"
    DEPENDENCE_RESEARCH_REQUIRED = "dependence_research_required"
    GEOMETRY_MISMATCH_BLOCKED = "geometry_mismatch_blocked"
    ASSIGNMENT_UNKNOWN_BLOCKED = "assignment_unknown_blocked"
    KNOWN_FAILURE_BLOCKED = "known_failure_blocked"
    RESEARCH_DEFERRED = "research_deferred"
    RETIRE_OR_REPLACE = "retire_or_replace"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class InferenceSuitabilityRow:
    row_id: str
    estimator_family: EstimatorFamily
    design_family: DesignFamily
    inference_family: InferenceFamily
    estimand_scope: str
    geometry: str
    assignment_requirement: str
    statistic_adapter_requirement: str
    null_calibration_requirement: str
    multiplicity_requirement: str
    suitability_status: SuitabilityStatus
    usage_boundary: str
    known_failure_modes: tuple[str, ...]
    required_evidence: tuple[str, ...]
    recommended_next_artifact: str | None
    forbidden_outputs: tuple[str, ...]


def _row(
    row_id: str,
    *,
    estimator_family: EstimatorFamily,
    design_family: DesignFamily,
    inference_family: InferenceFamily,
    estimand_scope: str,
    geometry: str,
    assignment_requirement: str,
    statistic_adapter_requirement: str,
    null_calibration_requirement: str,
    multiplicity_requirement: str,
    suitability_status: SuitabilityStatus,
    usage_boundary: str,
    known_failure_modes: tuple[str, ...] = (),
    required_evidence: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> InferenceSuitabilityRow:
    return InferenceSuitabilityRow(
        row_id=row_id,
        estimator_family=estimator_family,
        design_family=design_family,
        inference_family=inference_family,
        estimand_scope=estimand_scope,
        geometry=geometry,
        assignment_requirement=assignment_requirement,
        statistic_adapter_requirement=statistic_adapter_requirement,
        null_calibration_requirement=null_calibration_requirement,
        multiplicity_requirement=multiplicity_requirement,
        suitability_status=suitability_status,
        usage_boundary=usage_boundary,
        known_failure_modes=known_failure_modes,
        required_evidence=required_evidence,
        recommended_next_artifact=recommended_next_artifact,
        forbidden_outputs=FORBIDDEN_OUTPUTS,
    )


def build_estimator_design_inference_suitability_matrix() -> tuple[InferenceSuitabilityRow, ...]:
    """Return the governed estimator × design × inference suitability matrix."""
    return (
        # --- SCM ---
        _row(
            "scm_single_treated_unit_jackknife",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.SINGLE_TREATED_GEO,
            inference_family=InferenceFamily.UNIT_JACKKNIFE,
            estimand_scope="cell_level_att",
            geometry="single_treated",
            assignment_requirement="observed_assignment_known",
            statistic_adapter_requirement="none",
            null_calibration_requirement="not_required_for_jk_research_mode",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.SUPPORTED_RESTRICTED_RESEARCH,
            usage_boundary="restricted_research_mode_reporting_only",
            required_evidence=("METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",),
            recommended_next_artifact=None,
        ),
        _row(
            "scm_single_treated_placebo_rank",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.SINGLE_TREATED_GEO,
            inference_family=InferenceFamily.TREATED_SET_PLACEBO_RANK,
            estimand_scope="cell_level_att",
            geometry="single_treated",
            assignment_requirement="design_aware_assignment_required",
            statistic_adapter_requirement="scm_placebo_semantics",
            null_calibration_requirement="null_monitor_only",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="falsification_null_monitor_only",
            known_failure_modes=("single_treated_placebo_not_primary_inference",),
            required_evidence=("SCM_PLACEBO_GOVERNED_SEMANTICS_001",),
        ),
        _row(
            "scm_multi_treated_treated_set_placebo",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.TREATED_SET_PLACEBO_RANK,
            estimand_scope="treated_set_att",
            geometry="multi_treated_set",
            assignment_requirement="design_aware_assignment_required",
            statistic_adapter_requirement="scm_treated_set_statistic",
            null_calibration_requirement="scm_treated_set_placebo_null_calibration_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            usage_boundary="framework_candidate_after_calibration",
            required_evidence=(
                "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
                "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",
            ),
            recommended_next_artifact="AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001",
        ),
        _row(
            "scm_multi_treated_studentized_placebo",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.STUDENTIZED_PLACEBO_RANK,
            estimand_scope="treated_set_att",
            geometry="multi_treated_set",
            assignment_requirement="design_aware_assignment_required",
            statistic_adapter_requirement="scm_augsynth_shared_adapter",
            null_calibration_requirement="studentized_randomization_null_calibration_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            usage_boundary="framework_candidate_after_calibration",
            required_evidence=(
                "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
                "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
            ),
        ),
        _row(
            "scm_leave_one_treated_out",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
            estimand_scope="treated_set_att",
            geometry="multi_treated_set",
            assignment_requirement="observed_assignment_known",
            statistic_adapter_requirement="none",
            null_calibration_requirement="not_applicable",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.SENSITIVITY_ONLY,
            usage_boundary="sensitivity_review_only",
            known_failure_modes=("not_primary_inference_path",),
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
        ),
        _row(
            "scm_unknown_assignment_randomization",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.UNKNOWN_ASSIGNMENT,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="cell_level_att",
            geometry="unknown",
            assignment_requirement="assignment_mechanism_must_be_known",
            statistic_adapter_requirement="blocked_without_assignment",
            null_calibration_requirement="blocked",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.ASSIGNMENT_UNKNOWN_BLOCKED,
            usage_boundary="blocked_from_inference_selection",
            known_failure_modes=("assignment_unknown_blocks_design_inference",),
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "scm_stratified_stratum_level",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.STRATIFIED,
            inference_family=InferenceFamily.UNIT_JACKKNIFE,
            estimand_scope="per_stratum_att",
            geometry="stratified_per_stratum",
            assignment_requirement="stratum_assignment_known",
            statistic_adapter_requirement="per_stratum_scm_config",
            null_calibration_requirement="stratum_level_calibration_research",
            multiplicity_requirement="stratum_multiplicity_review",
            suitability_status=SuitabilityStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            usage_boundary="restricted_research_per_stratum_only",
            required_evidence=("STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",),
        ),
        _row(
            "scm_stratified_pooled_aggregate",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.STRATIFIED,
            inference_family=InferenceFamily.NO_VALID_INFERENCE,
            estimand_scope="pooled_aggregate_att",
            geometry="stratified_pooled",
            assignment_requirement="heterogeneity_policy_required",
            statistic_adapter_requirement="pooling_adapter_required",
            null_calibration_requirement="heterogeneity_review_required",
            multiplicity_requirement="aggregate_claim_blocked",
            suitability_status=SuitabilityStatus.GEOMETRY_MISMATCH_BLOCKED,
            usage_boundary="blocked_until_pooling_policy",
            known_failure_modes=("aggregate_without_heterogeneity_policy",),
            required_evidence=("STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",),
        ),
        _row(
            "scm_conformal_blocked",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.SINGLE_TREATED_GEO,
            inference_family=InferenceFamily.CONFORMAL,
            estimand_scope="cell_level_att",
            geometry="single_treated",
            assignment_requirement="exchangeability_assumption",
            statistic_adapter_requirement="not_validated",
            null_calibration_requirement="not_validated",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.KNOWN_FAILURE_BLOCKED,
            usage_boundary="blocked_pending_new_design",
            known_failure_modes=("conformal_blocked_pending_new_design",),
            required_evidence=("D5_INF_AUGSYNTH_CONFORMAL_FAILURE_001",),
        ),
        # --- AugSynth ---
        _row(
            "augsynth_multi_treated_design_randomization",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="treated_set_att",
            geometry="multi_treated_set",
            assignment_requirement="design_aware_assignment_required",
            statistic_adapter_requirement="scm_augsynth_shared_adapter_required",
            null_calibration_requirement="estimator_backed_calibration_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_REQUIRES_ADAPTER,
            usage_boundary="framework_candidate_requires_adapter",
            required_evidence=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            recommended_next_artifact="AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001",
        ),
        _row(
            "augsynth_point_randomization_studentized",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.RERANDOMIZED,
            inference_family=InferenceFamily.STUDENTIZED_PLACEBO_RANK,
            estimand_scope="point_effect",
            geometry="multi_treated_set",
            assignment_requirement="rerandomized_design",
            statistic_adapter_requirement="augsynth_point_statistic_adapter",
            null_calibration_requirement="studentized_null_calibration_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            usage_boundary="framework_candidate_after_calibration",
            required_evidence=(
                "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
                "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
            ),
        ),
        _row(
            "augsynth_jackknife_retire",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.UNIT_JACKKNIFE,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="observed_assignment_known",
            statistic_adapter_requirement="none",
            null_calibration_requirement="jk_unsafe_under_diagnostics",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RETIRE_OR_REPLACE,
            usage_boundary="diagnostic_only_jk_unsafe",
            known_failure_modes=("jk_unsafe_under_diagnostics", "false_confidence_risk"),
            required_evidence=("D5_INF_AUGSYNTH_JK_CALIBRATION_001", "METHOD_READINESS_MATRIX_V2_001"),
            recommended_next_artifact="SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001",
        ),
        _row(
            "augsynth_unknown_assignment",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.UNKNOWN_ASSIGNMENT,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="unknown",
            assignment_requirement="assignment_mechanism_must_be_known",
            statistic_adapter_requirement="blocked_without_assignment",
            null_calibration_requirement="blocked",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.ASSIGNMENT_UNKNOWN_BLOCKED,
            usage_boundary="blocked_from_inference_selection",
            known_failure_modes=("assignment_unknown_blocks_design_inference",),
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
        ),
        _row(
            "augsynth_stratified_pooled",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.STRATIFIED,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="pooled_aggregate_att",
            geometry="stratified_pooled",
            assignment_requirement="heterogeneity_and_pooling_policy",
            statistic_adapter_requirement="stratified_pooling_adapter",
            null_calibration_requirement="pooling_research_required",
            multiplicity_requirement="aggregate_claim_blocked",
            suitability_status=SuitabilityStatus.CANDIDATE_REQUIRES_ADAPTER,
            usage_boundary="contract_candidate_no_aggregate_inference",
            required_evidence=("STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",),
        ),
        # --- DID ---
        _row(
            "did_matched_stratified_bootstrap",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.MATCHED_PAIR,
            inference_family=InferenceFamily.DID_BOOTSTRAP,
            estimand_scope="cell_level_att",
            geometry="matched_pair",
            assignment_requirement="matched_design_documented",
            statistic_adapter_requirement="none",
            null_calibration_requirement="did_bootstrap_calibration_research",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.SUPPORTED_RESTRICTED_RESEARCH,
            usage_boundary="restricted_research_mode_reporting_only",
            required_evidence=("METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",),
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "did_stratified_bootstrap",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.STRATIFIED,
            inference_family=InferenceFamily.DID_BOOTSTRAP,
            estimand_scope="per_stratum_att",
            geometry="stratified_per_stratum",
            assignment_requirement="stratum_assignment_known",
            statistic_adapter_requirement="none",
            null_calibration_requirement="stratum_calibration_research",
            multiplicity_requirement="stratum_multiplicity_review",
            suitability_status=SuitabilityStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            usage_boundary="restricted_research_per_stratum_only",
            required_evidence=("STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",),
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "did_cluster_robust_analytic",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.MATCHED_BLOCK,
            inference_family=InferenceFamily.CLUSTER_ROBUST_ANALYTIC,
            estimand_scope="cell_level_att",
            geometry="matched_block",
            assignment_requirement="cluster_structure_documented",
            statistic_adapter_requirement="none",
            null_calibration_requirement="cluster_count_credibility_review",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_REQUIRES_DESIGN_STRESS_TEST,
            usage_boundary="research_candidate_requires_stress_test",
            known_failure_modes=("cluster_robust_not_credible_at_geo_counts",),
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "did_permutation_randomization",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.RERANDOMIZED,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="rerandomized",
            assignment_requirement="rerandomized_design",
            statistic_adapter_requirement="did_statistic_for_permutation",
            null_calibration_requirement="randomization_null_calibration_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            usage_boundary="framework_candidate_after_calibration",
            required_evidence=("STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",),
            recommended_next_artifact="DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
        ),
        _row(
            "did_unknown_assignment",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.UNKNOWN_ASSIGNMENT,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="cell_level_att",
            geometry="unknown",
            assignment_requirement="assignment_mechanism_must_be_known",
            statistic_adapter_requirement="blocked_without_assignment",
            null_calibration_requirement="blocked",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.ASSIGNMENT_UNKNOWN_BLOCKED,
            usage_boundary="blocked_from_inference_selection",
            known_failure_modes=("assignment_unknown_blocks_design_inference",),
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
        ),
        # --- TBRRidge ---
        _row(
            "tbrridge_brb",
            estimator_family=EstimatorFamily.TBRRIDGE,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.BLOCK_RESIDUAL_BOOTSTRAP,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="observed_assignment_known",
            statistic_adapter_requirement="estimand_alignment_required",
            null_calibration_requirement="variance_calibration_failed",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.KNOWN_FAILURE_BLOCKED,
            usage_boundary="diagnostic_only_until_remediation",
            known_failure_modes=("estimand_mismatch", "interval_miscentering", "variance_miscalibration"),
            required_evidence=("D5-TRUST-TBRRIDGE-BRB-001", "TBRRIDGE_BRB_ESTIMAND_ALIGNMENT_CORRECTION_001"),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        _row(
            "tbrridge_kfold",
            estimator_family=EstimatorFamily.TBRRIDGE,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.KFOLD_CROSS_FIT,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="observed_assignment_known",
            statistic_adapter_requirement="none",
            null_calibration_requirement="null_fpr_elevated",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="diagnostic_summary_only",
            known_failure_modes=("elevated_null_fpr", "unstable_cross_fit"),
            required_evidence=("INV-TBRRIDGE-KFOLD-NULL-FPR-001",),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        _row(
            "tbrridge_placebo_rank",
            estimator_family=EstimatorFamily.TBRRIDGE,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.TREATED_SET_PLACEBO_RANK,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="design_aware_assignment_required",
            statistic_adapter_requirement="tbrridge_statistic_adapter_missing",
            null_calibration_requirement="remediation_required_before_calibration",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="diagnostic_only_until_remediation",
            known_failure_modes=("governed_semantics_not_validated",),
            required_evidence=("INV-TBRRIDGE-PLACEBO-GOVERNED-SEMANTICS-001",),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        _row(
            "tbrridge_jackknife",
            estimator_family=EstimatorFamily.TBRRIDGE,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.UNIT_JACKKNIFE,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="observed_assignment_known",
            statistic_adapter_requirement="none",
            null_calibration_requirement="not_applicable",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.KNOWN_FAILURE_BLOCKED,
            usage_boundary="blocked_known_failure",
            known_failure_modes=("jackknife_blocked_for_tbrridge",),
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        _row(
            "tbrridge_remediation_retire",
            estimator_family=EstimatorFamily.TBRRIDGE,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.NO_VALID_INFERENCE,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="remediation_decision_required",
            statistic_adapter_requirement="remediation_or_retirement_audit",
            null_calibration_requirement="all_paths_blocked_until_remediation",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RETIRE_OR_REPLACE,
            usage_boundary="remediation_or_retirement_required",
            known_failure_modes=("no_valid_production_inference_path",),
            required_evidence=("METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001",),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
        # --- TBR / Bayesian TBR ---
        _row(
            "tbr_aggregate_geometry_mismatch",
            estimator_family=EstimatorFamily.TBR,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.BOOTSTRAP,
            estimand_scope="aggregate_att",
            geometry="aggregate_geometry",
            assignment_requirement="aggregate_geometry_documented",
            statistic_adapter_requirement="geometry_alignment_required",
            null_calibration_requirement="blocked",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.GEOMETRY_MISMATCH_BLOCKED,
            usage_boundary="blocked_geometry_mismatch",
            known_failure_modes=("tbr_aggregate_geometry_blocked",),
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
        ),
        _row(
            "bayesian_tbr_posterior_interval",
            estimator_family=EstimatorFamily.BAYESIAN_TBR,
            design_family=DesignFamily.SINGLE_TREATED_GEO,
            inference_family=InferenceFamily.BAYESIAN_POSTERIOR_INTERVAL,
            estimand_scope="cell_level_att",
            geometry="single_treated",
            assignment_requirement="bayesian_model_specified",
            statistic_adapter_requirement="posterior_contract_required",
            null_calibration_requirement="decision_safe_path_not_validated",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.POSTERIOR_DIAGNOSTIC_ONLY,
            usage_boundary="posterior_diagnostic_research_only",
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
            recommended_next_artifact=None,
        ),
        _row(
            "bayesian_tbr_posterior_predictive",
            estimator_family=EstimatorFamily.BAYESIAN_TBR,
            design_family=DesignFamily.SINGLE_TREATED_GEO,
            inference_family=InferenceFamily.BAYESIAN_POSTERIOR_PREDICTIVE_CHECK,
            estimand_scope="cell_level_att",
            geometry="single_treated",
            assignment_requirement="bayesian_model_specified",
            statistic_adapter_requirement="posterior_predictive_contract",
            null_calibration_requirement="not_validated_for_decisioning",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.POSTERIOR_DIAGNOSTIC_ONLY,
            usage_boundary="posterior_diagnostic_research_only",
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
        ),
        _row(
            "bayesian_tbr_placebo_rank",
            estimator_family=EstimatorFamily.BAYESIAN_TBR,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.TREATED_SET_PLACEBO_RANK,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="design_aware_assignment_required",
            statistic_adapter_requirement="adapter_and_null_calibration_missing",
            null_calibration_requirement="not_validated",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="diagnostic_only_without_adapter",
            known_failure_modes=("no_adapter_null_calibration",),
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
        ),
        _row(
            "bayesian_tbr_bootstrap_research",
            estimator_family=EstimatorFamily.BAYESIAN_TBR,
            design_family=DesignFamily.MATCHED_PAIR,
            inference_family=InferenceFamily.BOOTSTRAP,
            estimand_scope="cell_level_att",
            geometry="matched_pair",
            assignment_requirement="matched_design_documented",
            statistic_adapter_requirement="not_implemented",
            null_calibration_requirement="research_deferred",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RESEARCH_DEFERRED,
            usage_boundary="research_deferred_not_implemented",
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
        ),
        # --- Synthetic DID / TROP ---
        _row(
            "synthetic_did_bootstrap_permutation",
            estimator_family=EstimatorFamily.SYNTHETIC_DID,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.BOOTSTRAP,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="synthetic_control_design",
            statistic_adapter_requirement="not_implemented",
            null_calibration_requirement="research_deferred",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RESEARCH_DEFERRED,
            usage_boundary="research_deferred_not_implemented",
            required_evidence=("METHOD_READINESS_MATRIX_V2_001", "INFERENCE_REPLACEMENT_SCOUT_001"),
        ),
        _row(
            "synthetic_did_placebo_randomization",
            estimator_family=EstimatorFamily.SYNTHETIC_DID,
            design_family=DesignFamily.RERANDOMIZED,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="rerandomized_design",
            statistic_adapter_requirement="synthetic_did_adapter_required",
            null_calibration_requirement="adapter_and_calibration_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_REQUIRES_ADAPTER,
            usage_boundary="framework_candidate_requires_adapter",
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
        ),
        _row(
            "trop_permutation_randomization",
            estimator_family=EstimatorFamily.TROP,
            design_family=DesignFamily.MULTI_TREATED_GEO,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="multi_treated_set",
            assignment_requirement="trop_design_assumptions",
            statistic_adapter_requirement="not_implemented",
            null_calibration_requirement="research_deferred",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RESEARCH_DEFERRED,
            usage_boundary="research_deferred_not_implemented",
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
        ),
        _row(
            "trop_unknown_assignment",
            estimator_family=EstimatorFamily.TROP,
            design_family=DesignFamily.UNKNOWN_ASSIGNMENT,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="unknown",
            assignment_requirement="assignment_mechanism_must_be_known",
            statistic_adapter_requirement="blocked_without_assignment",
            null_calibration_requirement="blocked",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.ASSIGNMENT_UNKNOWN_BLOCKED,
            usage_boundary="blocked_from_inference_selection",
            known_failure_modes=("assignment_unknown_blocks_design_inference",),
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
        ),
        # --- Multicell ---
        _row(
            "multicell_shared_control_max_t",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.MULTICELL_SHARED_CONTROL,
            inference_family=InferenceFamily.MAX_T_MULTIPLICITY,
            estimand_scope="per_cell_marginal_att",
            geometry="multicell_shared_control",
            assignment_requirement="shared_control_dependence_documented",
            statistic_adapter_requirement="per_cell_statistic",
            null_calibration_requirement="dependence_model_required",
            multiplicity_requirement="max_t_dependence_research",
            suitability_status=SuitabilityStatus.DEPENDENCE_RESEARCH_REQUIRED,
            usage_boundary="per_cell_marginal_only_no_global",
            known_failure_modes=("cross_cell_correlation_unresolved",),
            required_evidence=("MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",),
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "multicell_independent_cells_stepdown",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.MULTICELL_INDEPENDENT_CELLS,
            inference_family=InferenceFamily.STEPDOWN_MULTIPLICITY,
            estimand_scope="per_cell_marginal_att",
            geometry="multicell_independent",
            assignment_requirement="independent_cell_design",
            statistic_adapter_requirement="per_cell_statistic",
            null_calibration_requirement="familywise_calibration_required",
            multiplicity_requirement="stepdown_multiplicity_research",
            suitability_status=SuitabilityStatus.MULTIPLICITY_RESEARCH_REQUIRED,
            usage_boundary="per_cell_marginal_only_no_global",
            known_failure_modes=("familywise_type_i_unresolved",),
            required_evidence=("MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",),
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        _row(
            "multicell_global_winner_blocked",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.MULTICELL_SHARED_CONTROL,
            inference_family=InferenceFamily.NO_VALID_INFERENCE,
            estimand_scope="global_winner_selection",
            geometry="global_winner",
            assignment_requirement="multiplicity_correction_required",
            statistic_adapter_requirement="blocked",
            null_calibration_requirement="blocked",
            multiplicity_requirement="global_winner_without_correction_blocked",
            suitability_status=SuitabilityStatus.BLOCKED,
            usage_boundary="blocked_global_winner_selection",
            known_failure_modes=("multicell_global_decision_blocked", "winner_selection_blocked"),
            required_evidence=("MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",),
        ),
        _row(
            "multicell_pooled_effect_blocked",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.MULTICELL_SHARED_CONTROL,
            inference_family=InferenceFamily.NO_VALID_INFERENCE,
            estimand_scope="pooled_multicell_att",
            geometry="pooled_multicell",
            assignment_requirement="pooling_policy_required",
            statistic_adapter_requirement="blocked",
            null_calibration_requirement="blocked",
            multiplicity_requirement="pooled_effect_blocked",
            suitability_status=SuitabilityStatus.GEOMETRY_MISMATCH_BLOCKED,
            usage_boundary="blocked_pooled_multicell_effect",
            known_failure_modes=("multicell_pooled_effect_blocked",),
            required_evidence=("MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",),
        ),
        # --- Stratified aggregate ---
        _row(
            "stratified_aggregate_no_heterogeneity",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.STRATIFIED,
            inference_family=InferenceFamily.NO_VALID_INFERENCE,
            estimand_scope="pooled_aggregate_att",
            geometry="stratified_pooled",
            assignment_requirement="heterogeneity_policy_required",
            statistic_adapter_requirement="pooling_adapter_required",
            null_calibration_requirement="heterogeneity_review_required",
            multiplicity_requirement="aggregate_claim_blocked",
            suitability_status=SuitabilityStatus.BLOCKED,
            usage_boundary="blocked_without_heterogeneity_policy",
            known_failure_modes=("stratified_posthoc_pooling_blocked",),
            required_evidence=("STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",),
        ),
        # --- Unknown / deterministic / falsification-only ---
        _row(
            "unknown_assignment_design_inference",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.UNKNOWN_ASSIGNMENT,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="unknown",
            assignment_requirement="assignment_mechanism_must_be_known",
            statistic_adapter_requirement="blocked_without_assignment",
            null_calibration_requirement="blocked",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.ASSIGNMENT_UNKNOWN_BLOCKED,
            usage_boundary="blocked_from_inference_selection",
            known_failure_modes=("assignment_unknown_blocks_design_inference",),
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
        ),
        _row(
            "fixed_deterministic_placebo_falsification",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.FIXED_DETERMINISTIC,
            inference_family=InferenceFamily.TREATED_SET_PLACEBO_RANK,
            estimand_scope="cell_level_att",
            geometry="fixed_deterministic",
            assignment_requirement="deterministic_assignment_documented",
            statistic_adapter_requirement="falsification_only",
            null_calibration_requirement="falsification_monitor_only",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="falsification_null_monitor_only",
            known_failure_modes=("not_valid_randomization_inference",),
            required_evidence=("SCM_PLACEBO_GOVERNED_SEMANTICS_001",),
        ),
        _row(
            "greedy_matched_market_placebo_falsification",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.GREEDY_MATCHED_MARKET,
            inference_family=InferenceFamily.STUDENTIZED_PLACEBO_RANK,
            estimand_scope="cell_level_att",
            geometry="greedy_matched_market",
            assignment_requirement="greedy_match_documented",
            statistic_adapter_requirement="falsification_only",
            null_calibration_requirement="falsification_monitor_only",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="falsification_null_monitor_only",
            known_failure_modes=("greedy_match_not_valid_randomization",),
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "kernel_thinning_placebo_falsification",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.KERNEL_THINNING,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="cell_level_att",
            geometry="kernel_thinning",
            assignment_requirement="kernel_thinning_documented",
            statistic_adapter_requirement="falsification_only",
            null_calibration_requirement="falsification_monitor_only",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="falsification_null_monitor_only",
            known_failure_modes=("kernel_thinning_falsification_only",),
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        # --- Coverage rows for design/inference families ---
        _row(
            "tbr_matched_pair_no_inference",
            estimator_family=EstimatorFamily.TBR,
            design_family=DesignFamily.MATCHED_PAIR,
            inference_family=InferenceFamily.NO_VALID_INFERENCE,
            estimand_scope="cell_level_att",
            geometry="matched_pair",
            assignment_requirement="matched_design_documented",
            statistic_adapter_requirement="not_validated",
            null_calibration_requirement="not_validated",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RESEARCH_DEFERRED,
            usage_boundary="research_deferred",
            required_evidence=("METHOD_READINESS_MATRIX_V2_001",),
        ),
        _row(
            "synthetic_did_matched_block_permutation",
            estimator_family=EstimatorFamily.SYNTHETIC_DID,
            design_family=DesignFamily.MATCHED_BLOCK,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="matched_block",
            assignment_requirement="matched_block_design",
            statistic_adapter_requirement="not_implemented",
            null_calibration_requirement="research_deferred",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RESEARCH_DEFERRED,
            usage_boundary="research_deferred_not_implemented",
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
        ),
        _row(
            "augsynth_matched_block_bootstrap",
            estimator_family=EstimatorFamily.AUGSYNTH_CVXPY,
            design_family=DesignFamily.MATCHED_BLOCK,
            inference_family=InferenceFamily.BOOTSTRAP,
            estimand_scope="cell_level_att",
            geometry="matched_block",
            assignment_requirement="matched_block_design",
            statistic_adapter_requirement="augsynth_bootstrap_adapter",
            null_calibration_requirement="not_validated",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.CANDIDATE_REQUIRES_ADAPTER,
            usage_boundary="framework_candidate_requires_adapter",
            required_evidence=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
        ),
        _row(
            "did_greedy_matched_permutation",
            estimator_family=EstimatorFamily.DID,
            design_family=DesignFamily.GREEDY_MATCHED_MARKET,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="greedy_matched_market",
            assignment_requirement="greedy_match_documented",
            statistic_adapter_requirement="falsification_statistic",
            null_calibration_requirement="falsification_monitor_only",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="falsification_null_monitor_only",
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
        ),
        _row(
            "scm_kernel_thinning_sensitivity",
            estimator_family=EstimatorFamily.SCM,
            design_family=DesignFamily.KERNEL_THINNING,
            inference_family=InferenceFamily.LEAVE_ONE_TREATED_OUT_SENSITIVITY,
            estimand_scope="cell_level_att",
            geometry="kernel_thinning",
            assignment_requirement="kernel_thinning_documented",
            statistic_adapter_requirement="none",
            null_calibration_requirement="not_applicable",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.SENSITIVITY_ONLY,
            usage_boundary="sensitivity_review_only",
            required_evidence=("DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",),
        ),
        _row(
            "trop_rerandomized_design_randomization",
            estimator_family=EstimatorFamily.TROP,
            design_family=DesignFamily.RERANDOMIZED,
            inference_family=InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            estimand_scope="cell_level_att",
            geometry="rerandomized",
            assignment_requirement="rerandomized_design",
            statistic_adapter_requirement="not_implemented",
            null_calibration_requirement="research_deferred",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.RESEARCH_DEFERRED,
            usage_boundary="research_deferred_not_implemented",
            required_evidence=("INFERENCE_REPLACEMENT_SCOUT_001",),
        ),
        _row(
            "bayesian_tbr_multicell_posterior",
            estimator_family=EstimatorFamily.BAYESIAN_TBR,
            design_family=DesignFamily.MULTICELL_INDEPENDENT_CELLS,
            inference_family=InferenceFamily.BAYESIAN_POSTERIOR_INTERVAL,
            estimand_scope="per_cell_marginal_att",
            geometry="multicell_independent",
            assignment_requirement="independent_cell_design",
            statistic_adapter_requirement="posterior_per_cell",
            null_calibration_requirement="multiplicity_research_required",
            multiplicity_requirement="per_cell_only_no_global",
            suitability_status=SuitabilityStatus.POSTERIOR_DIAGNOSTIC_ONLY,
            usage_boundary="posterior_diagnostic_per_cell_only",
            required_evidence=("MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",),
        ),
        _row(
            "tbrridge_permutation_diagnostic",
            estimator_family=EstimatorFamily.TBRRIDGE,
            design_family=DesignFamily.RERANDOMIZED,
            inference_family=InferenceFamily.PERMUTATION,
            estimand_scope="cell_level_att",
            geometry="rerandomized",
            assignment_requirement="rerandomized_design",
            statistic_adapter_requirement="tbrridge_statistic_adapter_missing",
            null_calibration_requirement="remediation_required",
            multiplicity_requirement="none",
            suitability_status=SuitabilityStatus.DIAGNOSTIC_ONLY,
            usage_boundary="diagnostic_only_until_remediation",
            known_failure_modes=("estimand_alignment_unresolved",),
            required_evidence=("METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001",),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
        ),
    )


def filter_suitability_rows(
    rows: tuple[InferenceSuitabilityRow, ...],
    *,
    estimator_family: EstimatorFamily | None = None,
    design_family: DesignFamily | None = None,
    inference_family: InferenceFamily | None = None,
    suitability_status: SuitabilityStatus | None = None,
) -> tuple[InferenceSuitabilityRow, ...]:
    """Filter matrix rows by optional dimension predicates."""
    filtered: list[InferenceSuitabilityRow] = []
    for row in rows:
        if estimator_family is not None and row.estimator_family != estimator_family:
            continue
        if design_family is not None and row.design_family != design_family:
            continue
        if inference_family is not None and row.inference_family != inference_family:
            continue
        if suitability_status is not None and row.suitability_status != suitability_status:
            continue
        filtered.append(row)
    return tuple(filtered)


def _count_by(rows: tuple[InferenceSuitabilityRow, ...], attr: str) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[getattr(row, attr).value] += 1
    return dict(counter)


def summarize_estimator_design_inference_suitability_matrix(
    rows: tuple[InferenceSuitabilityRow, ...],
) -> dict[str, Any]:
    """Serialize suitability matrix summary for validation archives."""
    validation = validate_estimator_design_inference_suitability_matrix(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "estimator_family_counts": _count_by(rows, "estimator_family"),
        "design_family_counts": _count_by(rows, "design_family"),
        "inference_family_counts": _count_by(rows, "inference_family"),
        "suitability_status_counts": _count_by(rows, "suitability_status"),
        "placebo_is_only_inference_layer": False,
        "downstream_work_paused": True,
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        "inference_layer_decisions": list(INFERENCE_LAYER_DECISIONS),
        "next_required_evidence": [
            "TBRRidge inference failure inventory and remediation decision",
            "DID bootstrap/randomization suitability validation",
            "assignment-generator stress tests",
            "multicell max-T / stepdown research scout",
            "estimator-backed AugSynth randomization calibration",
            "SCM/AugSynth disagreement diagnostics",
        ],
        "forbidden_outputs": list(FORBIDDEN_OUTPUTS),
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
        "warnings": [MATRIX_WARNING],
        "valid": validation["valid"],
    }


def validate_estimator_design_inference_suitability_matrix(
    rows: tuple[InferenceSuitabilityRow, ...],
) -> dict[str, Any]:
    """Validate matrix invariants and return structured validation summary."""
    issues: list[str] = []
    row_ids = [row.row_id for row in rows]

    if len(row_ids) != len(set(row_ids)):
        issues.append("duplicate row_id detected")

    if len(rows) < 35:
        issues.append(f"row_count {len(rows)} < 35")

    present_estimators = {row.estimator_family for row in rows}
    for est in EstimatorFamily:
        if est not in present_estimators:
            issues.append(f"missing estimator family: {est.value}")

    present_designs = {row.design_family for row in rows}
    for design in DesignFamily:
        if design not in present_designs:
            issues.append(f"missing design family: {design.value}")

    present_inference = {row.inference_family for row in rows}
    for inf in InferenceFamily:
        if inf not in present_inference:
            issues.append(f"missing inference family: {inf.value}")

    for row in rows:
        if not row.required_evidence and not row.known_failure_modes:
            issues.append(f"{row.row_id}: missing required_evidence and known_failure_modes")
        if not row.forbidden_outputs:
            issues.append(f"{row.row_id}: missing forbidden_outputs")
        for forbidden in FORBIDDEN_OUTPUTS:
            if forbidden not in row.forbidden_outputs:
                issues.append(f"{row.row_id}: missing forbidden output {forbidden}")

    non_placebo_inference = {
        row.inference_family
        for row in rows
        if row.inference_family
        not in {
            InferenceFamily.TREATED_SET_PLACEBO_RANK,
            InferenceFamily.STUDENTIZED_PLACEBO_RANK,
            InferenceFamily.DESIGN_BASED_RANDOMIZATION,
            InferenceFamily.PERMUTATION,
            InferenceFamily.NO_VALID_INFERENCE,
        }
    }
    if len(non_placebo_inference) < 5:
        issues.append("matrix must include multiple non-placebo/randomization inference families")

    return {
        "valid": not issues,
        "row_count": len(rows),
        "unique_row_ids": len(row_ids) == len(set(row_ids)),
        "estimator_families_present": len(present_estimators) == len(EstimatorFamily),
        "design_families_present": len(present_designs) == len(DesignFamily),
        "inference_families_present": len(present_inference) == len(InferenceFamily),
        "issues": issues,
    }
