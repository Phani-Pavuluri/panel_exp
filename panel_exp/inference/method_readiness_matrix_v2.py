"""METHOD_READINESS_MATRIX_V2_001 — governed method-readiness matrix v2.

Consolidates the method-validity spine into a test-backed readiness classification matrix.
Evidence-index and readiness classification only — not a downstream release gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

_ARTIFACT_ID = "METHOD_READINESS_MATRIX_V2_001"
_VERDICT = "method_readiness_matrix_v2_defined_no_downstream_authorization"

MATRIX_WARNING = (
    "Method-readiness matrix v2 is an evidence-index only — not production authorization, "
    "TrustReport expansion, CalibrationSignal, or downstream decisioning."
)

CANDIDATE_FORBIDDEN_OUTPUTS = (
    "final_p_value",
    "causal_confidence_interval",
    "trustreport_authorization",
    "calibration_signal",
    "mmm_ingestion",
    "llm_decisioning",
    "production_decisioning",
)

DOWNSTREAM_FLAG_KEYS = (
    "trustreport_authorized",
    "calibration_signal_allowed",
    "mmm_ingestion_allowed",
    "llm_decisioning_allowed",
    "production_decisioning_allowed",
    "live_api_authorized",
    "scheduler_authorized",
    "budget_optimization_allowed",
)

REQUIRED_METHOD_IDS = frozenset(
    {
        "scm_unit_jackknife_restricted_research",
        "did_bootstrap_restricted_research",
        "scm_treated_set_placebo_candidate",
        "scm_studentized_treated_set_placebo_candidate",
        "augsynth_point_randomization_candidate",
        "multicell_per_cell_marginal_only",
        "stratified_pooled_estimand_contract_candidate",
        "scm_single_treated_placebo_null_monitor",
        "augsynth_jackknife_diagnostic_only",
        "tbrridge_brb_diagnostic_only",
        "tbrridge_kfold_diagnostic_only",
        "tbrridge_placebo_diagnostic_only",
        "stratified_scm_jk_aggregate_diagnostic_only",
        "scm_leave_one_treated_out_sensitivity_only",
        "multicell_shared_control_unresolved",
        "multicell_multiple_cell_family_adjustment_required",
        "stratified_pooling_heterogeneity_review_required",
        "tbr_aggregate_geometry_blocked",
        "tbrridge_jackknife_blocked",
        "multicell_global_decision_blocked",
        "multicell_winner_selection_blocked",
        "multicell_pooled_effect_blocked",
        "stratified_posthoc_pooling_blocked",
        "augsynth_jk_production_inference_blocked",
        "dcm_009_019_adapters_research_deferred",
    }
)

class ReadinessTier(str, Enum):
    RESTRICTED_RESEARCH_MODE_USABLE = "restricted_research_mode_usable"
    FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE = "framework_level_randomization_candidate"
    PER_CELL_MARGINAL_ONLY = "per_cell_marginal_only"
    CONTRACT_CANDIDATE = "contract_candidate"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    HETEROGENEITY_REVIEW_REQUIRED = "heterogeneity_review_required"
    MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED = "multiplicity_or_dependence_unresolved"
    RESEARCH_DEFERRED = "research_deferred"
    BLOCKED = "blocked"


class MethodFamilyV2(str, Enum):
    SCM = "scm"
    SCM_STUDENTIZED = "scm_studentized"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    DID = "did"
    TBRRIDGE = "tbrridge"
    TBR = "tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    MULTICELL = "multicell"
    STRATIFIED_POOLED = "stratified_pooled"
    UNKNOWN = "unknown"


class InferenceModeV2(str, Enum):
    UNIT_JACKKNIFE = "unit_jackknife"
    DID_BOOTSTRAP = "did_bootstrap"
    TREATED_SET_PLACEBO = "treated_set_placebo"
    STUDENTIZED_PLACEBO_RANK = "studentized_placebo_rank"
    AUGSYNTH_POINT_RANDOMIZATION = "augsynth_point_randomization"
    AUGSYNTH_JACKKNIFE = "augsynth_jackknife"
    BLOCK_RESIDUAL_BOOTSTRAP = "block_residual_bootstrap"
    KFOLD = "kfold"
    PLACEBO = "placebo"
    POOLED = "pooled"
    MULTICELL_FAMILY = "multicell_family"
    UNKNOWN = "unknown"


class GeometryV2(str, Enum):
    SINGLE_TREATED = "single_treated"
    MULTI_TREATED_SET = "multi_treated_set"
    PER_CELL_MARGINAL = "per_cell_marginal"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    STRATIFIED = "stratified"
    POOLED_MULTICELL = "pooled_multicell"
    GLOBAL = "global"
    WINNER_SELECTION = "winner_selection"
    UNKNOWN = "unknown"


class UsageBoundaryV2(str, Enum):
    RESEARCH_MODE_REPORTING_ONLY = "research_mode_reporting_only"
    FRAMEWORK_LEVEL_CANDIDATE_ONLY = "framework_level_candidate_only"
    DIAGNOSTIC_SUMMARY_ONLY = "diagnostic_summary_only"
    SENSITIVITY_REVIEW_ONLY = "sensitivity_review_only"
    PER_CELL_ONLY_NO_GLOBAL_CLAIM = "per_cell_only_no_global_claim"
    CONTRACT_ONLY_NO_INFERENCE_AUTHORIZATION = "contract_only_no_inference_authorization"
    BLOCKED_FROM_DOWNSTREAM = "blocked_from_downstream"


CANDIDATE_TIERS = frozenset(
    {
        ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
        ReadinessTier.CONTRACT_CANDIDATE,
        ReadinessTier.PER_CELL_MARGINAL_ONLY,
    }
)


@dataclass(frozen=True)
class MethodReadinessEvidenceRef:
    artifact_id: str
    summary_json: str | None = None
    report_path: str | None = None
    commit: str | None = None
    evidence_note: str = ""


@dataclass(frozen=True)
class MethodReadinessMatrixRow:
    method_id: str
    method_family: MethodFamilyV2
    estimator: str
    inference_mode: InferenceModeV2
    geometry: GeometryV2
    estimand_scope: str
    interval_or_tail_semantics: str
    readiness_tier: ReadinessTier
    usage_boundary: UsageBoundaryV2
    allowed_outputs: tuple[str, ...]
    forbidden_outputs: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    required_next_evidence: tuple[str, ...]
    evidence_refs: tuple[MethodReadinessEvidenceRef, ...]
    trustreport_authorized: bool = False
    calibration_signal_allowed: bool = False
    mmm_ingestion_allowed: bool = False
    llm_decisioning_allowed: bool = False
    production_decisioning_allowed: bool = False
    live_api_authorized: bool = False
    scheduler_authorized: bool = False
    budget_optimization_allowed: bool = False


@dataclass(frozen=True)
class MethodReadinessMatrixV2:
    artifact_id: str
    rows: tuple[MethodReadinessMatrixRow, ...]
    verdict: str
    summary_counts: Mapping[str, int]
    downstream_authorization_flags: Mapping[str, bool]
    warnings: tuple[str, ...]


def _downstream_flags_false() -> dict[str, bool]:
    return {k: False for k in DOWNSTREAM_FLAG_KEYS}


def _evidence(
    artifact_id: str,
    *,
    summary: str | None = None,
    report: str | None = None,
    note: str = "",
) -> MethodReadinessEvidenceRef:
    return MethodReadinessEvidenceRef(
        artifact_id=artifact_id,
        summary_json=summary,
        report_path=report,
        evidence_note=note,
    )


def _row(
    method_id: str,
    *,
    method_family: MethodFamilyV2,
    estimator: str,
    inference_mode: InferenceModeV2,
    geometry: GeometryV2,
    estimand_scope: str,
    interval_or_tail_semantics: str,
    readiness_tier: ReadinessTier,
    usage_boundary: UsageBoundaryV2,
    allowed_outputs: tuple[str, ...],
    forbidden_outputs: tuple[str, ...],
    blocked_reasons: tuple[str, ...] = (),
    required_next_evidence: tuple[str, ...] = (),
    evidence_refs: tuple[MethodReadinessEvidenceRef, ...],
) -> MethodReadinessMatrixRow:
    return MethodReadinessMatrixRow(
        method_id=method_id,
        method_family=method_family,
        estimator=estimator,
        inference_mode=inference_mode,
        geometry=geometry,
        estimand_scope=estimand_scope,
        interval_or_tail_semantics=interval_or_tail_semantics,
        readiness_tier=readiness_tier,
        usage_boundary=usage_boundary,
        allowed_outputs=allowed_outputs,
        forbidden_outputs=forbidden_outputs,
        blocked_reasons=blocked_reasons,
        required_next_evidence=required_next_evidence,
        evidence_refs=evidence_refs,
    )


def _build_rows() -> tuple[MethodReadinessMatrixRow, ...]:
    candidate_forbidden = CANDIDATE_FORBIDDEN_OUTPUTS
    return (
        _row(
            "scm_unit_jackknife_restricted_research",
            method_family=MethodFamilyV2.SCM,
            estimator="scm",
            inference_mode=InferenceModeV2.UNIT_JACKKNIFE,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="cell_level_ate",
            interval_or_tail_semantics="jackknife_interval_research_mode",
            readiness_tier=ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE,
            usage_boundary=UsageBoundaryV2.RESEARCH_MODE_REPORTING_ONLY,
            allowed_outputs=("restricted_research_mode_point_estimate", "jackknife_interval"),
            forbidden_outputs=(*candidate_forbidden, "calibration_signal", "live_api", "scheduler"),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    summary="docs/track_d/archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json",
                    report="docs/track_d/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_REPORT.md",
                    note="SCM unit jackknife restricted research-mode usable per prior D5 trust characterization",
                ),
            ),
        ),
        _row(
            "did_bootstrap_restricted_research",
            method_family=MethodFamilyV2.DID,
            estimator="did",
            inference_mode=InferenceModeV2.DID_BOOTSTRAP,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="cell_level_ate",
            interval_or_tail_semantics="bootstrap_interval_research_mode",
            readiness_tier=ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE,
            usage_boundary=UsageBoundaryV2.RESEARCH_MODE_REPORTING_ONLY,
            allowed_outputs=("restricted_research_mode_point_estimate", "bootstrap_interval"),
            forbidden_outputs=(*candidate_forbidden, "live_api", "scheduler"),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    summary="docs/track_d/archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json",
                    note="DID bootstrap restricted research-mode usable without comparable pseudo point statistics",
                ),
            ),
        ),
        _row(
            "scm_treated_set_placebo_candidate",
            method_family=MethodFamilyV2.SCM,
            estimator="scm",
            inference_mode=InferenceModeV2.TREATED_SET_PLACEBO,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="multi_treated_set_ate",
            interval_or_tail_semantics="empirical_tail_fraction_not_production_p_value",
            readiness_tier=ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
            usage_boundary=UsageBoundaryV2.FRAMEWORK_LEVEL_CANDIDATE_ONLY,
            allowed_outputs=("placebo_rank", "empirical_tail_fraction", "framework_level_candidate"),
            forbidden_outputs=candidate_forbidden,
            evidence_refs=(
                _evidence(
                    "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
                    summary="docs/track_d/archives/SCM_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json",
                    report="docs/track_d/SCM_TREATED_SET_PLACEBO_INTEGRATION_001_REPORT.md",
                    note="SCM treated-set placebo integration defined as framework candidate",
                ),
                _evidence(
                    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
                    note="Design-aware pseudo-assignment framework prerequisite",
                ),
            ),
        ),
        _row(
            "scm_studentized_treated_set_placebo_candidate",
            method_family=MethodFamilyV2.SCM_STUDENTIZED,
            estimator="scm",
            inference_mode=InferenceModeV2.STUDENTIZED_PLACEBO_RANK,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="multi_treated_set_ate",
            interval_or_tail_semantics="studentized_empirical_tail_fraction_not_production_p_value",
            readiness_tier=ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
            usage_boundary=UsageBoundaryV2.FRAMEWORK_LEVEL_CANDIDATE_ONLY,
            allowed_outputs=(
                "studentized_placebo_rank",
                "empirical_tail_fraction",
                "framework_level_candidate",
            ),
            forbidden_outputs=candidate_forbidden,
            evidence_refs=(
                _evidence(
                    "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
                    summary="docs/track_d/archives/SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001_summary.json",
                    report="docs/track_d/SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001_REPORT.md",
                ),
                _evidence(
                    "STUDENTIZED_PLACEBO_RANK_INFERENCE_001",
                    summary="docs/track_d/archives/STUDENTIZED_PLACEBO_RANK_INFERENCE_001_summary.json",
                ),
            ),
        ),
        _row(
            "augsynth_point_randomization_candidate",
            method_family=MethodFamilyV2.AUGSYNTH_CVXPY,
            estimator="augsynth_cvxpy",
            inference_mode=InferenceModeV2.AUGSYNTH_POINT_RANDOMIZATION,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="augsynth_point_effect",
            interval_or_tail_semantics="empirical_tail_fraction_not_production_p_value",
            readiness_tier=ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE,
            usage_boundary=UsageBoundaryV2.FRAMEWORK_LEVEL_CANDIDATE_ONLY,
            allowed_outputs=("placebo_rank", "empirical_tail_fraction", "framework_level_candidate"),
            forbidden_outputs=(*candidate_forbidden, "augsynth_jk_authorization"),
            evidence_refs=(
                _evidence(
                    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
                    summary="docs/track_d/archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json",
                    report="docs/track_d/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_REPORT.md",
                    note="AugSynth point randomization candidate; JK remains diagnostic-only",
                ),
            ),
        ),
        _row(
            "multicell_per_cell_marginal_only",
            method_family=MethodFamilyV2.MULTICELL,
            estimator="multicell",
            inference_mode=InferenceModeV2.MULTICELL_FAMILY,
            geometry=GeometryV2.PER_CELL_MARGINAL,
            estimand_scope="per_cell_marginal_ate",
            interval_or_tail_semantics="per_cell_marginal_readout_only",
            readiness_tier=ReadinessTier.PER_CELL_MARGINAL_ONLY,
            usage_boundary=UsageBoundaryV2.PER_CELL_ONLY_NO_GLOBAL_CLAIM,
            allowed_outputs=("per_cell_marginal_readout",),
            forbidden_outputs=(
                *candidate_forbidden,
                "global_multicell_decision",
                "winner_selection",
                "pooled_multicell_effect",
            ),
            evidence_refs=(
                _evidence(
                    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
                    summary="docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json",
                    report="docs/track_d/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_REPORT.md",
                    note="Per-cell marginal allowed as separate readout only",
                ),
            ),
        ),
        _row(
            "stratified_pooled_estimand_contract_candidate",
            method_family=MethodFamilyV2.STRATIFIED_POOLED,
            estimator="stratified_aggregate",
            inference_mode=InferenceModeV2.POOLED,
            geometry=GeometryV2.STRATIFIED,
            estimand_scope="pooled_estimand_contract",
            interval_or_tail_semantics="contract_candidate_no_inference_authorization",
            readiness_tier=ReadinessTier.CONTRACT_CANDIDATE,
            usage_boundary=UsageBoundaryV2.CONTRACT_ONLY_NO_INFERENCE_AUTHORIZATION,
            allowed_outputs=("pooled_estimand_contract_candidate", "pre_specified_weights"),
            forbidden_outputs=(
                *candidate_forbidden,
                "production_pooled_effect",
                "global_summary",
                "winner_selected_summary",
            ),
            required_next_evidence=("valid_pooling_inference", "multiplicity_or_dependence_resolution"),
            evidence_refs=(
                _evidence(
                    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
                    summary="docs/track_d/archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json",
                    report="docs/track_d/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_REPORT.md",
                    note="Contract candidate only — not production pooled effect",
                ),
            ),
        ),
        _row(
            "scm_single_treated_placebo_null_monitor",
            method_family=MethodFamilyV2.SCM,
            estimator="scm",
            inference_mode=InferenceModeV2.PLACEBO,
            geometry=GeometryV2.SINGLE_TREATED,
            estimand_scope="single_treated_null_monitor",
            interval_or_tail_semantics="placebo_tail_fraction_falsification_only",
            readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY,
            usage_boundary=UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY,
            allowed_outputs=("null_monitor_diagnostic", "falsification_diagnostic"),
            forbidden_outputs=candidate_forbidden,
            evidence_refs=(
                _evidence(
                    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
                    note="SCM single-treated placebo is null-monitor/falsification only",
                ),
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    summary="docs/track_d/archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json",
                ),
            ),
        ),
        _row(
            "augsynth_jackknife_diagnostic_only",
            method_family=MethodFamilyV2.AUGSYNTH_CVXPY,
            estimator="augsynth_cvxpy",
            inference_mode=InferenceModeV2.AUGSYNTH_JACKKNIFE,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="augsynth_jk_interval",
            interval_or_tail_semantics="jackknife_interval_diagnostic_only",
            readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY,
            usage_boundary=UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY,
            allowed_outputs=("augsynth_jk_diagnostic", "characterized_interval"),
            forbidden_outputs=(*candidate_forbidden, "augsynth_jk_authorization"),
            evidence_refs=(
                _evidence(
                    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
                    summary="docs/track_d/archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json",
                    note="AugSynth JK diagnostic-only / characterized-only",
                ),
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    note="AugSynth JK interval is diagnostic-only per method-specific validation",
                ),
            ),
        ),
        _row(
            "tbrridge_brb_diagnostic_only",
            method_family=MethodFamilyV2.TBRRIDGE,
            estimator="tbrridge",
            inference_mode=InferenceModeV2.BLOCK_RESIDUAL_BOOTSTRAP,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="cell_level_ate",
            interval_or_tail_semantics="bootstrap_interval_diagnostic_only",
            readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY,
            usage_boundary=UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY,
            allowed_outputs=("diagnostic_bootstrap_interval",),
            forbidden_outputs=candidate_forbidden,
            required_next_evidence=("tbrridge_replacement_inference_required",),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    summary="docs/track_d/archives/METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001_summary.json",
                    note="TBRRidge BRB path diagnostic-only — replacement inference required",
                ),
            ),
        ),
        _row(
            "tbrridge_kfold_diagnostic_only",
            method_family=MethodFamilyV2.TBRRIDGE,
            estimator="tbrridge",
            inference_mode=InferenceModeV2.KFOLD,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="cell_level_ate",
            interval_or_tail_semantics="kfold_diagnostic_only",
            readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY,
            usage_boundary=UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY,
            allowed_outputs=("kfold_diagnostic",),
            forbidden_outputs=candidate_forbidden,
            required_next_evidence=("tbrridge_replacement_inference_required",),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    note="TBRRidge KFold tuning rejected as production inference",
                ),
            ),
        ),
        _row(
            "tbrridge_placebo_diagnostic_only",
            method_family=MethodFamilyV2.TBRRIDGE,
            estimator="tbrridge",
            inference_mode=InferenceModeV2.PLACEBO,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="cell_level_ate",
            interval_or_tail_semantics="placebo_tail_fraction_diagnostic_only",
            readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY,
            usage_boundary=UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY,
            allowed_outputs=("placebo_tail_fraction_diagnostic",),
            forbidden_outputs=candidate_forbidden,
            required_next_evidence=("tbrridge_replacement_inference_required",),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    note="TBRRidge placebo path diagnostic-only",
                ),
            ),
        ),
        _row(
            "stratified_scm_jk_aggregate_diagnostic_only",
            method_family=MethodFamilyV2.SCM,
            estimator="scm",
            inference_mode=InferenceModeV2.UNIT_JACKKNIFE,
            geometry=GeometryV2.STRATIFIED,
            estimand_scope="stratified_aggregate",
            interval_or_tail_semantics="jackknife_aggregate_diagnostic_only",
            readiness_tier=ReadinessTier.DIAGNOSTIC_ONLY,
            usage_boundary=UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY,
            allowed_outputs=("stratified_aggregate_diagnostic_summary",),
            forbidden_outputs=(
                *candidate_forbidden,
                "production_pooled_effect",
                "global_summary",
            ),
            evidence_refs=(
                _evidence(
                    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
                    summary="docs/track_d/archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json",
                    note="Stratified SCM+JK aggregate remains diagnostic-only without pooled estimand contract",
                ),
            ),
        ),
        _row(
            "scm_leave_one_treated_out_sensitivity_only",
            method_family=MethodFamilyV2.SCM,
            estimator="scm",
            inference_mode=InferenceModeV2.PLACEBO,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="treated_unit_sensitivity",
            interval_or_tail_semantics="not_placebo_inference",
            readiness_tier=ReadinessTier.SENSITIVITY_ONLY,
            usage_boundary=UsageBoundaryV2.SENSITIVITY_REVIEW_ONLY,
            allowed_outputs=("leave_one_treated_out_sensitivity",),
            forbidden_outputs=(*candidate_forbidden, "treated_set_placebo_substitute"),
            blocked_reasons=("leave_one_treated_out_rejected_as_placebo",),
            evidence_refs=(
                _evidence(
                    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
                    note="LOTO is sensitivity analysis only — not multi-treated placebo inference",
                ),
            ),
        ),
        _row(
            "multicell_shared_control_unresolved",
            method_family=MethodFamilyV2.MULTICELL,
            estimator="multicell",
            inference_mode=InferenceModeV2.MULTICELL_FAMILY,
            geometry=GeometryV2.MULTICELL_SHARED_CONTROL,
            estimand_scope="shared_control_family",
            interval_or_tail_semantics="independent_fwer_proxy_only",
            readiness_tier=ReadinessTier.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=("familywise_false_positive_risk_proxy",),
            forbidden_outputs=(
                *candidate_forbidden,
                "global_multicell_decision",
                "winner_selection",
                "pooled_multicell_effect",
            ),
            blocked_reasons=("shared_control_dependence_model_required",),
            required_next_evidence=(
                "joint_null_distribution",
                "shared_control_dependence_model",
            ),
            evidence_refs=(
                _evidence(
                    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
                    summary="docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json",
                    report="docs/track_d/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_REPORT.md",
                ),
            ),
        ),
        _row(
            "multicell_multiple_cell_family_adjustment_required",
            method_family=MethodFamilyV2.MULTICELL,
            estimator="multicell",
            inference_mode=InferenceModeV2.MULTICELL_FAMILY,
            geometry=GeometryV2.MULTICELL_SHARED_CONTROL,
            estimand_scope="multiple_cell_family",
            interval_or_tail_semantics="multiplicity_adjustment_required",
            readiness_tier=ReadinessTier.MULTIPLICITY_OR_DEPENDENCE_UNRESOLVED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=("bonferroni_alpha", "multiplicity_adjustment_required"),
            forbidden_outputs=(
                *candidate_forbidden,
                "global_multicell_decision",
                "winner_selection",
            ),
            blocked_reasons=("multiplicity_adjustment_required",),
            required_next_evidence=("pre_registered_hypothesis_family", "closed_testing_validation"),
            evidence_refs=(
                _evidence(
                    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
                    summary="docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json",
                ),
            ),
        ),
        _row(
            "stratified_pooling_heterogeneity_review_required",
            method_family=MethodFamilyV2.STRATIFIED_POOLED,
            estimator="stratified_aggregate",
            inference_mode=InferenceModeV2.POOLED,
            geometry=GeometryV2.STRATIFIED,
            estimand_scope="pooled_estimand_pre_contract",
            interval_or_tail_semantics="heterogeneity_review_required",
            readiness_tier=ReadinessTier.HETEROGENEITY_REVIEW_REQUIRED,
            usage_boundary=UsageBoundaryV2.CONTRACT_ONLY_NO_INFERENCE_AUTHORIZATION,
            allowed_outputs=("heterogeneity_review_required", "stratum_level_readout"),
            forbidden_outputs=(
                *candidate_forbidden,
                "production_pooled_effect",
            ),
            required_next_evidence=(
                "heterogeneity_assessment",
                "pre_specified_heterogeneity_policy",
            ),
            evidence_refs=(
                _evidence(
                    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
                    summary="docs/track_d/archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json",
                ),
            ),
        ),
        _row(
            "tbr_aggregate_geometry_blocked",
            method_family=MethodFamilyV2.TBR,
            estimator="tbr",
            inference_mode=InferenceModeV2.UNKNOWN,
            geometry=GeometryV2.UNKNOWN,
            estimand_scope="aggregate",
            interval_or_tail_semantics="blocked",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=candidate_forbidden,
            blocked_reasons=("aggregate_geometry_mismatch",),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    note="TBR aggregate geometry blocked per method-specific validation",
                ),
            ),
        ),
        _row(
            "tbrridge_jackknife_blocked",
            method_family=MethodFamilyV2.TBRRIDGE,
            estimator="tbrridge",
            inference_mode=InferenceModeV2.UNIT_JACKKNIFE,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="cell_level_ate",
            interval_or_tail_semantics="jackknife_known_failure_mode",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=candidate_forbidden,
            blocked_reasons=("tbrridge_jk_known_failure_mode",),
            required_next_evidence=("tbrridge_replacement_inference_required",),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    note="TBRRidge JK known failure mode — not randomization candidate",
                ),
            ),
        ),
        _row(
            "multicell_global_decision_blocked",
            method_family=MethodFamilyV2.MULTICELL,
            estimator="multicell",
            inference_mode=InferenceModeV2.MULTICELL_FAMILY,
            geometry=GeometryV2.GLOBAL,
            estimand_scope="global_multicell_decision",
            interval_or_tail_semantics="blocked",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=(*candidate_forbidden, "global_multicell_decision"),
            blocked_reasons=(
                "multiplicity_or_shared_control_dependence_unresolved",
                "global_multicell_decision_blocked",
            ),
            evidence_refs=(
                _evidence(
                    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
                    summary="docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json",
                ),
            ),
        ),
        _row(
            "multicell_winner_selection_blocked",
            method_family=MethodFamilyV2.MULTICELL,
            estimator="multicell",
            inference_mode=InferenceModeV2.MULTICELL_FAMILY,
            geometry=GeometryV2.WINNER_SELECTION,
            estimand_scope="winner_selected_summary",
            interval_or_tail_semantics="blocked",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=(*candidate_forbidden, "winner_selection"),
            blocked_reasons=(
                "selection_adjusted_inference_missing",
                "winner_selected_summary_blocked",
            ),
            evidence_refs=(
                _evidence(
                    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
                    summary="docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json",
                ),
            ),
        ),
        _row(
            "multicell_pooled_effect_blocked",
            method_family=MethodFamilyV2.MULTICELL,
            estimator="multicell",
            inference_mode=InferenceModeV2.MULTICELL_FAMILY,
            geometry=GeometryV2.POOLED_MULTICELL,
            estimand_scope="pooled_multicell_effect",
            interval_or_tail_semantics="blocked",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=(*candidate_forbidden, "pooled_multicell_effect"),
            blocked_reasons=(
                "pooled_estimand_contract_and_dependence_aware_inference_missing",
                "pooled_multicell_effect_blocked",
            ),
            evidence_refs=(
                _evidence(
                    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
                    summary="docs/track_d/archives/MULTICELL_SHARED_CONTROL_MULTIPLICITY_001_summary.json",
                ),
                _evidence(
                    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
                    note="Pooled multi-cell requires stratified/pooled estimand contract",
                ),
            ),
        ),
        _row(
            "stratified_posthoc_pooling_blocked",
            method_family=MethodFamilyV2.STRATIFIED_POOLED,
            estimator="stratified_aggregate",
            inference_mode=InferenceModeV2.POOLED,
            geometry=GeometryV2.STRATIFIED,
            estimand_scope="post_hoc_weighted_aggregate",
            interval_or_tail_semantics="blocked",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=(*candidate_forbidden, "production_pooled_effect"),
            blocked_reasons=("post_hoc_effect_size_weights_blocked", "weights_not_pre_specified"),
            evidence_refs=(
                _evidence(
                    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
                    summary="docs/track_d/archives/STRATIFIED_POOLED_ESTIMAND_CONTRACT_001_summary.json",
                ),
            ),
        ),
        _row(
            "augsynth_jk_production_inference_blocked",
            method_family=MethodFamilyV2.AUGSYNTH_CVXPY,
            estimator="augsynth_cvxpy",
            inference_mode=InferenceModeV2.AUGSYNTH_JACKKNIFE,
            geometry=GeometryV2.MULTI_TREATED_SET,
            estimand_scope="augsynth_jk_production_request",
            interval_or_tail_semantics="blocked",
            readiness_tier=ReadinessTier.BLOCKED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=(*candidate_forbidden, "augsynth_jk_authorization"),
            blocked_reasons=("augsynth_jk_production_inference_not_authorized",),
            evidence_refs=(
                _evidence(
                    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
                    summary="docs/track_d/archives/AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001_summary.json",
                ),
            ),
        ),
        _row(
            "dcm_009_019_adapters_research_deferred",
            method_family=MethodFamilyV2.UNKNOWN,
            estimator="dcm_adapter",
            inference_mode=InferenceModeV2.UNKNOWN,
            geometry=GeometryV2.UNKNOWN,
            estimand_scope="adapter_qualification_pending",
            interval_or_tail_semantics="research_deferred",
            readiness_tier=ReadinessTier.RESEARCH_DEFERRED,
            usage_boundary=UsageBoundaryV2.BLOCKED_FROM_DOWNSTREAM,
            allowed_outputs=(),
            forbidden_outputs=candidate_forbidden,
            required_next_evidence=("dcm_adapter_qualification_evidence",),
            evidence_refs=(
                _evidence(
                    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
                    note="DCM-009–019 adapter methods research-deferred pending qualification",
                ),
                _evidence(
                    "METHOD_ROADMAP_ALIGNMENT_AUDIT_001",
                    report="docs/track_d/METHOD_ROADMAP_ALIGNMENT_AUDIT_001.md",
                ),
            ),
        ),
    )


def _tier_counts(rows: tuple[MethodReadinessMatrixRow, ...]) -> dict[str, int]:
    counts: dict[str, int] = {tier.value: 0 for tier in ReadinessTier}
    for row in rows:
        counts[row.readiness_tier.value] += 1
    return counts


def build_method_readiness_matrix_v2() -> MethodReadinessMatrixV2:
    """Build the governed method-readiness matrix v2."""
    rows = _build_rows()
    return MethodReadinessMatrixV2(
        artifact_id=_ARTIFACT_ID,
        rows=rows,
        verdict=_VERDICT,
        summary_counts=_tier_counts(rows),
        downstream_authorization_flags=_downstream_flags_false(),
        warnings=(MATRIX_WARNING,),
    )


def find_method_readiness_row(
    matrix: MethodReadinessMatrixV2,
    method_id: str,
) -> MethodReadinessMatrixRow | None:
    """Return matrix row by method_id, or None if not found."""
    for row in matrix.rows:
        if row.method_id == method_id:
            return row
    return None


def filter_method_readiness_rows(
    matrix: MethodReadinessMatrixV2,
    readiness_tier: ReadinessTier | None = None,
    method_family: MethodFamilyV2 | None = None,
    geometry: GeometryV2 | None = None,
) -> tuple[MethodReadinessMatrixRow, ...]:
    """Filter matrix rows by tier, family, and/or geometry."""
    result: list[MethodReadinessMatrixRow] = []
    for row in matrix.rows:
        if readiness_tier is not None and row.readiness_tier != readiness_tier:
            continue
        if method_family is not None and row.method_family != method_family:
            continue
        if geometry is not None and row.geometry != geometry:
            continue
        result.append(row)
    return tuple(result)


def _serialize_row(row: MethodReadinessMatrixRow) -> dict[str, Any]:
    return {
        "method_id": row.method_id,
        "method_family": row.method_family.value,
        "estimator": row.estimator,
        "inference_mode": row.inference_mode.value,
        "geometry": row.geometry.value,
        "estimand_scope": row.estimand_scope,
        "interval_or_tail_semantics": row.interval_or_tail_semantics,
        "readiness_tier": row.readiness_tier.value,
        "usage_boundary": row.usage_boundary.value,
        "allowed_outputs": list(row.allowed_outputs),
        "forbidden_outputs": list(row.forbidden_outputs),
        "blocked_reasons": list(row.blocked_reasons),
        "required_next_evidence": list(row.required_next_evidence),
        "evidence_refs": [
            {
                "artifact_id": ref.artifact_id,
                "summary_json": ref.summary_json,
                "report_path": ref.report_path,
                "commit": ref.commit,
                "evidence_note": ref.evidence_note,
            }
            for ref in row.evidence_refs
        ],
        "trustreport_authorized": row.trustreport_authorized,
        "calibration_signal_allowed": row.calibration_signal_allowed,
        "mmm_ingestion_allowed": row.mmm_ingestion_allowed,
        "llm_decisioning_allowed": row.llm_decisioning_allowed,
        "production_decisioning_allowed": row.production_decisioning_allowed,
        "live_api_authorized": row.live_api_authorized,
        "scheduler_authorized": row.scheduler_authorized,
        "budget_optimization_allowed": row.budget_optimization_allowed,
    }


def summarize_method_readiness_matrix_v2(matrix: MethodReadinessMatrixV2) -> dict[str, Any]:
    """Serialize method-readiness matrix v2 for validation archives."""
    return {
        "artifact_id": matrix.artifact_id,
        "verdict": matrix.verdict,
        "row_count": len(matrix.rows),
        "summary_counts": dict(matrix.summary_counts),
        "downstream_authorization_flags": dict(matrix.downstream_authorization_flags),
        "warnings": list(matrix.warnings),
        "rows": [_serialize_row(row) for row in matrix.rows],
    }


def validate_method_readiness_matrix_v2(matrix: MethodReadinessMatrixV2) -> dict[str, Any]:
    """Validate matrix invariants and return structured validation summary."""
    issues: list[str] = []
    method_ids = [row.method_id for row in matrix.rows]
    unique_ids = len(method_ids) == len(set(method_ids))

    if not unique_ids:
        issues.append("duplicate method_id detected")

    missing_required = sorted(REQUIRED_METHOD_IDS - set(method_ids))
    if missing_required:
        issues.append(f"missing required method_ids: {missing_required}")

    for row in matrix.rows:
        for key in DOWNSTREAM_FLAG_KEYS:
            if getattr(row, key):
                issues.append(f"{row.method_id}: downstream flag {key} must be false")

        if not row.evidence_refs:
            issues.append(f"{row.method_id}: missing evidence_refs")

        if row.readiness_tier in CANDIDATE_TIERS:
            for forbidden in ("final_p_value", "causal_confidence_interval"):
                if forbidden not in row.forbidden_outputs:
                    issues.append(f"{row.method_id}: candidate missing forbidden {forbidden}")
            for forbidden in ("trustreport_authorization", "calibration_signal"):
                if forbidden not in row.forbidden_outputs:
                    issues.append(f"{row.method_id}: candidate missing forbidden {forbidden}")

        if row.readiness_tier == ReadinessTier.RESTRICTED_RESEARCH_MODE_USABLE:
            if row.usage_boundary != UsageBoundaryV2.RESEARCH_MODE_REPORTING_ONLY:
                issues.append(f"{row.method_id}: restricted row must be research-mode only")

        if row.readiness_tier == ReadinessTier.DIAGNOSTIC_ONLY:
            if row.usage_boundary != UsageBoundaryV2.DIAGNOSTIC_SUMMARY_ONLY:
                issues.append(f"{row.method_id}: diagnostic row must be diagnostic-only boundary")

        if row.readiness_tier == ReadinessTier.SENSITIVITY_ONLY:
            if row.usage_boundary != UsageBoundaryV2.SENSITIVITY_REVIEW_ONLY:
                issues.append(f"{row.method_id}: sensitivity row must be sensitivity-only boundary")

        if row.readiness_tier == ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE:
            if row.usage_boundary != UsageBoundaryV2.FRAMEWORK_LEVEL_CANDIDATE_ONLY:
                issues.append(f"{row.method_id}: framework candidate must have framework-only boundary")

        if row.method_id == "augsynth_jackknife_diagnostic_only":
            if row.readiness_tier != ReadinessTier.DIAGNOSTIC_ONLY:
                issues.append("augsynth_jackknife_diagnostic_only must be diagnostic-only")

        if row.method_id == "augsynth_point_randomization_candidate":
            if row.readiness_tier != ReadinessTier.FRAMEWORK_LEVEL_RANDOMIZATION_CANDIDATE:
                issues.append("augsynth_point_randomization_candidate must be framework candidate")

        if row.geometry in {
            GeometryV2.GLOBAL,
            GeometryV2.WINNER_SELECTION,
            GeometryV2.POOLED_MULTICELL,
        }:
            if row.readiness_tier != ReadinessTier.BLOCKED:
                issues.append(f"{row.method_id}: global/winner/pooled geometry must be blocked")

    global_flags = matrix.downstream_authorization_flags
    for key in DOWNSTREAM_FLAG_KEYS:
        if global_flags.get(key):
            issues.append(f"matrix downstream flag {key} must be false")

    return {
        "valid": not issues,
        "row_count": len(matrix.rows),
        "unique_method_ids": unique_ids,
        "required_rows_present": not missing_required,
        "missing_required_method_ids": missing_required,
        "readiness_tier_counts": dict(matrix.summary_counts),
        "issues": issues,
    }


__all__ = [
    "GeometryV2",
    "InferenceModeV2",
    "MethodFamilyV2",
    "MethodReadinessEvidenceRef",
    "MethodReadinessMatrixRow",
    "MethodReadinessMatrixV2",
    "ReadinessTier",
    "UsageBoundaryV2",
    "REQUIRED_METHOD_IDS",
    "build_method_readiness_matrix_v2",
    "filter_method_readiness_rows",
    "find_method_readiness_row",
    "summarize_method_readiness_matrix_v2",
    "validate_method_readiness_matrix_v2",
]
