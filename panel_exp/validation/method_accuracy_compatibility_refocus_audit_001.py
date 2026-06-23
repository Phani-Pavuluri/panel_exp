"""METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001 validation harness."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

_ARTIFACT_ID = "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "refocus_on_method_accuracy_and_compatibility"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001_summary.json"
)

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "INFERENCE_REPLACEMENT_SCOUT_001",
    "DESIGN_AWARE_ASSIGNMENT_GENERATORS_001",
    "MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
    "SCM_PLACEBO_GOVERNED_SEMANTICS_001",
    "METHOD_SPECIFIC_RANDOMIZATION_INFERENCE_VALIDATION_001",
    "SCM_TREATED_SET_PLACEBO_INTEGRATION_001",
    "STUDENTIZED_PLACEBO_RANK_INFERENCE_001",
    "SCM_STUDENTIZED_TREATED_SET_PLACEBO_INTEGRATION_001",
    "MULTICELL_SHARED_CONTROL_MULTIPLICITY_001",
    "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001",
    "AUGSYNTH_POINT_RANDOMIZATION_INTEGRATION_001",
    "METHOD_READINESS_MATRIX_V2_001",
    "CALIBRATION_SIGNAL_METHOD_GATE_DRAFT_001",
    "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001",
]

FORBIDDEN_DOWNSTREAM_OUTPUTS = (
    "calibration_signal_authorization",
    "calibration_signal_creation",
    "trustreport_expansion",
    "mmm_ingestion",
    "llm_decisioning",
    "production_decisioning",
    "live_api_execution",
    "scheduler_execution",
    "budget_optimization",
)

PAUSED_DOWNSTREAM_ARTIFACTS = (
    "CALIBRATION_SIGNAL_SCHEMA_ALIGNMENT_DRAFT_001",
    "TRUSTREPORT_METHOD_GATE_DRAFT_001",
    "MMM_INGESTION_DRAFT_001",
    "LLM_DECISIONING_DRAFT_001",
    "LIVE_API_OR_SCHEDULER_WORK",
)

REFOCUS_DECISIONS = (
    "pause_downstream_schema_and_ingestion_work",
    "prioritize_empirical_null_calibration",
    "prioritize_estimator_statistic_adapter_compatibility",
    "treat_tbrridge_as_remediation_or_retirement",
    "treat_multicell_shared_control_as_research_prototype",
    "keep_augsynth_jk_diagnostic_or_retire",
    "keep_all_downstream_authorization_false",
)


class AccuracyCompatibilityWorkBucket(str, Enum):
    NULL_CALIBRATION = "null_calibration"
    ESTIMATOR_STATISTIC_ADAPTER = "estimator_statistic_adapter"
    INFERENCE_REMEDIATION = "inference_remediation"
    DESIGN_COMPATIBILITY = "design_compatibility"
    GEOMETRY_ESTIMAND_COMPATIBILITY = "geometry_estimand_compatibility"
    MULTICELL_DEPENDENCE_RESEARCH = "multicell_dependence_research"
    POOLING_HETEROGENEITY_RESEARCH = "pooling_heterogeneity_research"
    RETIRE_OR_PERMANENT_BLOCK = "retire_or_permanent_block"
    DOWNSTREAM_PAUSE = "downstream_pause"


class RefocusPriority(str, Enum):
    P0 = "p0_immediate"
    P1 = "p1_high"
    P2 = "p2_medium"
    P3 = "p3_low"


class FixabilityStatus(str, Enum):
    FIXABLE_NOW = "fixable_now"
    RESEARCH_PROTOTYPE_REQUIRED = "research_prototype_required"
    NEEDS_EMPIRICAL_EVIDENCE = "needs_empirical_evidence"
    LIKELY_RETIRE = "likely_retire"
    PERMANENT_BLOCK = "permanent_block"


@dataclass(frozen=True)
class MethodRefocusBacklogItem:
    item_id: str
    title: str
    affected_methods: tuple[str, ...]
    current_readiness_status: str
    work_bucket: AccuracyCompatibilityWorkBucket
    priority: RefocusPriority
    fixability: FixabilityStatus
    root_issue: str
    why_it_matters: str
    required_evidence: tuple[str, ...]
    recommended_next_artifact: str
    stop_go_criteria: tuple[str, ...]
    forbidden_outputs: tuple[str, ...]


def _item(
    item_id: str,
    title: str,
    *,
    affected_methods: tuple[str, ...],
    current_readiness_status: str,
    work_bucket: AccuracyCompatibilityWorkBucket,
    priority: RefocusPriority,
    fixability: FixabilityStatus,
    root_issue: str,
    why_it_matters: str,
    required_evidence: tuple[str, ...],
    recommended_next_artifact: str,
    stop_go_criteria: tuple[str, ...],
) -> MethodRefocusBacklogItem:
    return MethodRefocusBacklogItem(
        item_id=item_id,
        title=title,
        affected_methods=affected_methods,
        current_readiness_status=current_readiness_status,
        work_bucket=work_bucket,
        priority=priority,
        fixability=fixability,
        root_issue=root_issue,
        why_it_matters=why_it_matters,
        required_evidence=required_evidence,
        recommended_next_artifact=recommended_next_artifact,
        stop_go_criteria=stop_go_criteria,
        forbidden_outputs=FORBIDDEN_DOWNSTREAM_OUTPUTS,
    )


def build_method_accuracy_compatibility_backlog() -> tuple[MethodRefocusBacklogItem, ...]:
    """Build ranked method-accuracy and compatibility remediation backlog."""
    return (
        _item(
            "studentized_randomization_null_calibration",
            "Studentized randomization null calibration",
            affected_methods=(
                "scm_studentized_treated_set_placebo_candidate",
                "studentized_placebo_rank",
            ),
            current_readiness_status="framework_level_randomization_candidate",
            work_bucket=AccuracyCompatibilityWorkBucket.NULL_CALIBRATION,
            priority=RefocusPriority.P0,
            fixability=FixabilityStatus.NEEDS_EMPIRICAL_EVIDENCE,
            root_issue=(
                "Empirical type-I behavior under null simulations is not yet validated "
                "across design-aware assignment generators."
            ),
            why_it_matters=(
                "Studentized placebo-rank candidates cannot advance without null-calibrated "
                "tail fractions under governed assignment families."
            ),
            required_evidence=(
                "null_simulation_grid",
                "assignment_family_coverage",
                "empirical_type_i_at_alpha_levels",
                "tail_fraction_calibration_diagnostics",
                "minimum_pseudo_assignment_sensitivity",
                "false_confidence_checks",
            ),
            recommended_next_artifact="STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
            stop_go_criteria=(
                "continue_if_type_i_controlled_under_governed_designs",
                "restrict_to_diagnostic_only_if_false_positives_exceed_tolerance",
            ),
        ),
        _item(
            "scm_treated_set_placebo_null_calibration",
            "SCM treated-set placebo null calibration",
            affected_methods=("scm_treated_set_placebo_candidate",),
            current_readiness_status="framework_level_randomization_candidate",
            work_bucket=AccuracyCompatibilityWorkBucket.NULL_CALIBRATION,
            priority=RefocusPriority.P0,
            fixability=FixabilityStatus.NEEDS_EMPIRICAL_EVIDENCE,
            root_issue=(
                "Treated-set placebo candidate exists, but empirical null calibration "
                "is not yet established."
            ),
            why_it_matters=(
                "SCM multi-treated placebo integration remains framework-level only until "
                "empirical tail fractions behave under known null assignments."
            ),
            required_evidence=(
                "null_assignment_simulations",
                "empirical_tail_fraction_under_null",
                "pseudo_assignment_count_sensitivity",
                "design_aware_assignment_coverage",
            ),
            recommended_next_artifact="SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
            stop_go_criteria=(
                "continue_if_empirical_tail_fractions_behave_under_known_null_assignments",
                "keep_framework_level_only_if_calibration_incomplete",
            ),
        ),
        _item(
            "scm_augsynth_statistic_adapter_contract",
            "SCM/AugSynth statistic adapter contract",
            affected_methods=(
                "scm_treated_set_placebo_candidate",
                "scm_studentized_treated_set_placebo_candidate",
                "augsynth_point_randomization_candidate",
            ),
            current_readiness_status="framework_level_randomization_candidate",
            work_bucket=AccuracyCompatibilityWorkBucket.ESTIMATOR_STATISTIC_ADAPTER,
            priority=RefocusPriority.P0,
            fixability=FixabilityStatus.FIXABLE_NOW,
            root_issue=(
                "SCM and AugSynth candidates rely on statistic-first contracts; a shared "
                "adapter contract is needed to guarantee observed/pseudo statistic comparability."
            ),
            why_it_matters=(
                "Without a shared adapter contract, randomization candidates risk "
                "incomparable observed and pseudo statistics across estimators."
            ),
            required_evidence=(
                "common_statistic_interface",
                "observed_pseudo_recomputation_contract",
                "metric_scale_time_window_estimand_compatibility",
                "donor_eligibility_compatibility",
                "estimator_config_provenance",
            ),
            recommended_next_artifact="SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",
            stop_go_criteria=(
                "continue_if_adapter_contract_validates_across_scm_and_augsynth",
                "block_promotion_if_observed_pseudo_incomparable",
            ),
        ),
        _item(
            "multicell_max_t_research_scout",
            "Multi-cell max-T research scout",
            affected_methods=(
                "multicell_shared_control_unresolved",
                "multicell_multiple_cell_family_adjustment_required",
                "multicell_global_decision_blocked",
                "multicell_winner_selection_blocked",
                "multicell_pooled_effect_blocked",
            ),
            current_readiness_status="multiplicity_or_dependence_unresolved",
            work_bucket=AccuracyCompatibilityWorkBucket.MULTICELL_DEPENDENCE_RESEARCH,
            priority=RefocusPriority.P1,
            fixability=FixabilityStatus.RESEARCH_PROTOTYPE_REQUIRED,
            root_issue=(
                "Shared-control dependence and multiple testing are unresolved; "
                "independent FWER proxy is not enough."
            ),
            why_it_matters=(
                "Global, winner, and pooled multi-cell claims remain blocked without "
                "dependence-aware inference research."
            ),
            required_evidence=(
                "joint_null_definition",
                "max_t_closed_testing_step_down_candidates",
                "dependence_aware_simulation",
                "shared_control_covariance_handling",
                "winner_selection_correction_policy",
            ),
            recommended_next_artifact="MULTICELL_MAX_T_RESEARCH_SCOUT_001",
            stop_go_criteria=(
                "continue_if_dependence_aware_prototype_shows_credible_familywise_control",
                "keep_blocked_if_only_independent_proxy_available",
            ),
        ),
        _item(
            "tbrridge_inference_remediation_or_retirement",
            "TBRRidge inference remediation or retirement",
            affected_methods=(
                "tbrridge_brb_diagnostic_only",
                "tbrridge_kfold_diagnostic_only",
                "tbrridge_placebo_diagnostic_only",
                "tbrridge_jackknife_blocked",
            ),
            current_readiness_status="diagnostic_only_or_blocked",
            work_bucket=AccuracyCompatibilityWorkBucket.INFERENCE_REMEDIATION,
            priority=RefocusPriority.P1,
            fixability=FixabilityStatus.LIKELY_RETIRE,
            root_issue=(
                "TBRRidge inference variants have diagnostic-only or blocked status due to "
                "prior null/type-I/geometry failures."
            ),
            why_it_matters=(
                "TBRRidge should not receive incremental governance; it needs remediation "
                "evidence or explicit retirement."
            ),
            required_evidence=(
                "failure_mode_inventory",
                "geometry_specific_restrictions",
                "null_simulation_reruns",
                "comparison_against_scm_did_augsynth_candidates",
                "retirement_criteria",
            ),
            recommended_next_artifact="TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
            stop_go_criteria=(
                "retire_if_null_failures_reproduce",
                "remediate_only_if_replacement_inference_path_validated",
            ),
        ),
        _item(
            "augsynth_jk_retirement_or_replacement",
            "AugSynth JK retirement or replacement",
            affected_methods=(
                "augsynth_jackknife_diagnostic_only",
                "augsynth_jk_production_inference_blocked",
            ),
            current_readiness_status="diagnostic_only",
            work_bucket=AccuracyCompatibilityWorkBucket.RETIRE_OR_PERMANENT_BLOCK,
            priority=RefocusPriority.P1,
            fixability=FixabilityStatus.PERMANENT_BLOCK,
            root_issue=(
                "AugSynth JK remains diagnostic-only and should not linger as implied future "
                "production inference unless a replacement path is defined."
            ),
            why_it_matters=(
                "AugSynth point/studentized randomization is the candidate path; JK must be "
                "retired or explicitly replaced to prevent downstream drift."
            ),
            required_evidence=(
                "diagnostic_value_assessment",
                "replacement_path_through_point_studentized_randomization",
                "retirement_criteria",
            ),
            recommended_next_artifact="AUGSYNTH_JK_RETIREMENT_OR_REPLACEMENT_AUDIT_001",
            stop_go_criteria=(
                "retire_jk_from_active_roadmap_unless_diagnostic_value_justified",
                "never_promote_jk_to_production_inference",
            ),
        ),
        _item(
            "stratified_pooling_inference_scout",
            "Stratified pooling inference scout",
            affected_methods=(
                "stratified_pooled_estimand_contract_candidate",
                "stratified_pooling_heterogeneity_review_required",
                "stratified_scm_jk_aggregate_diagnostic_only",
            ),
            current_readiness_status="contract_candidate_or_diagnostic_only",
            work_bucket=AccuracyCompatibilityWorkBucket.POOLING_HETEROGENEITY_RESEARCH,
            priority=RefocusPriority.P2,
            fixability=FixabilityStatus.RESEARCH_PROTOTYPE_REQUIRED,
            root_issue=(
                "Pooled estimand contract exists, but inference and heterogeneity policy "
                "are not validated."
            ),
            why_it_matters=(
                "Stratified aggregates remain diagnostic until pooling variance, weights, "
                "and heterogeneity rules are empirically assessed."
            ),
            required_evidence=(
                "pre_specified_weights",
                "heterogeneity_decision_rule",
                "pooling_variance_dependence_assumptions",
                "stratum_compatibility_simulation",
            ),
            recommended_next_artifact="STRATIFIED_POOLING_INFERENCE_SCOUT_001",
            stop_go_criteria=(
                "continue_if_heterogeneity_and_pooling_inference_evidence_complete",
                "keep_diagnostic_only_if_contract_without_inference",
            ),
        ),
        _item(
            "design_assignment_generator_stress_tests",
            "Design assignment generator stress tests",
            affected_methods=(
                "scm_treated_set_placebo_candidate",
                "scm_studentized_treated_set_placebo_candidate",
                "augsynth_point_randomization_candidate",
            ),
            current_readiness_status="design_based_randomization_candidate",
            work_bucket=AccuracyCompatibilityWorkBucket.DESIGN_COMPATIBILITY,
            priority=RefocusPriority.P2,
            fixability=FixabilityStatus.FIXABLE_NOW,
            root_issue=(
                "Assignment generators are defined, but need stress tests for edge cases, "
                "support size, imbalance, and pseudo-assignment degeneracy."
            ),
            why_it_matters=(
                "All randomization candidates depend on valid pseudo-assignments; generator "
                "degeneracy undermines null calibration and adapter work."
            ),
            required_evidence=(
                "support_size_diagnostics",
                "duplicate_assignment_checks",
                "balance_acceptance_rate_checks",
                "degeneracy_checks",
                "seed_stability_reproducibility_checks",
            ),
            recommended_next_artifact="DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
            stop_go_criteria=(
                "continue_if_generators_pass_stress_suite",
                "block_candidates_if_degeneracy_detected",
            ),
        ),
        _item(
            "dcm_009_019_adapter_disposition",
            "DCM-009–019 adapter disposition",
            affected_methods=("dcm_009_019_adapters_research_deferred",),
            current_readiness_status="research_deferred",
            work_bucket=AccuracyCompatibilityWorkBucket.RETIRE_OR_PERMANENT_BLOCK,
            priority=RefocusPriority.P3,
            fixability=FixabilityStatus.LIKELY_RETIRE,
            root_issue=(
                "Deferred adapters should either receive evidence requirements or be "
                "retired from the active roadmap."
            ),
            why_it_matters=(
                "Research-deferred adapter rows consume roadmap attention without "
                "method-validity progress."
            ),
            required_evidence=(
                "adapter_qualification_inventory",
                "retirement_or_evidence_requirements_per_dcm_row",
            ),
            recommended_next_artifact="DCM_009_019_ADAPTER_DISPOSITION_AUDIT_001",
            stop_go_criteria=(
                "retire_adapters_without_evidence_path",
                "defer_only_with_explicit_qualification_plan",
            ),
        ),
        _item(
            "downstream_work_pause_marker",
            "Downstream work pause marker",
            affected_methods=PAUSED_DOWNSTREAM_ARTIFACTS,
            current_readiness_status="downstream_pause",
            work_bucket=AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE,
            priority=RefocusPriority.P0,
            fixability=FixabilityStatus.PERMANENT_BLOCK,
            root_issue=(
                "Downstream drafts are getting ahead of method accuracy work."
            ),
            why_it_matters=(
                "CalibrationSignal schema alignment, TrustReport expansion, MMM, and LLM "
                "work must pause until P0 calibration and adapter checkpoints pass."
            ),
            required_evidence=(),
            recommended_next_artifact="none_until_method_calibration_checkpoints_pass",
            stop_go_criteria=(
                "resume_only_after_p0_calibration_adapters_complete",
                "updated_readiness_matrix_and_explicit_resume_decision_required",
            ),
        ),
    )


def _priority_counts(backlog: tuple[MethodRefocusBacklogItem, ...]) -> dict[str, int]:
    counts = {p.value: 0 for p in RefocusPriority}
    for item in backlog:
        counts[item.priority.value] += 1
    return counts


def _bucket_counts(backlog: tuple[MethodRefocusBacklogItem, ...]) -> dict[str, int]:
    counts = {b.value: 0 for b in AccuracyCompatibilityWorkBucket}
    for item in backlog:
        counts[item.work_bucket.value] += 1
    return counts


def summarize_method_accuracy_compatibility_backlog(
    backlog: tuple[MethodRefocusBacklogItem, ...],
) -> dict[str, Any]:
    """Serialize method-accuracy compatibility backlog for archives."""
    return {
        "backlog_count": len(backlog),
        "priority_counts": _priority_counts(backlog),
        "bucket_counts": _bucket_counts(backlog),
        "items": [
            {
                "item_id": item.item_id,
                "title": item.title,
                "affected_methods": list(item.affected_methods),
                "current_readiness_status": item.current_readiness_status,
                "work_bucket": item.work_bucket.value,
                "priority": item.priority.value,
                "fixability": item.fixability.value,
                "root_issue": item.root_issue,
                "why_it_matters": item.why_it_matters,
                "required_evidence": list(item.required_evidence),
                "recommended_next_artifact": item.recommended_next_artifact,
                "stop_go_criteria": list(item.stop_go_criteria),
                "forbidden_outputs": list(item.forbidden_outputs),
            }
            for item in backlog
        ],
    }


def validate_method_accuracy_compatibility_refocus_audit(
    backlog: tuple[MethodRefocusBacklogItem, ...],
) -> dict[str, Any]:
    """Validate refocus audit backlog invariants."""
    issues: list[str] = []
    ids = [item.item_id for item in backlog]

    if len(ids) != len(set(ids)):
        issues.append("duplicate backlog item_id")

    if len(backlog) < 10:
        issues.append("backlog must have at least 10 items")

    required_ids = {
        "studentized_randomization_null_calibration",
        "scm_treated_set_placebo_null_calibration",
        "scm_augsynth_statistic_adapter_contract",
        "multicell_max_t_research_scout",
        "tbrridge_inference_remediation_or_retirement",
        "augsynth_jk_retirement_or_replacement",
        "stratified_pooling_inference_scout",
        "design_assignment_generator_stress_tests",
        "dcm_009_019_adapter_disposition",
        "downstream_work_pause_marker",
    }
    missing = required_ids - set(ids)
    if missing:
        issues.append(f"missing required backlog items: {sorted(missing)}")

    p0_ids = {i.item_id for i in backlog if i.priority == RefocusPriority.P0}
    if "studentized_randomization_null_calibration" not in p0_ids:
        issues.append("P0 must include studentized_randomization_null_calibration")

    for item in backlog:
        if not item.root_issue:
            issues.append(f"{item.item_id}: missing root_issue")
        if not item.stop_go_criteria:
            issues.append(f"{item.item_id}: missing stop_go_criteria")
        if item.work_bucket != AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE:
            if not item.required_evidence:
                issues.append(f"{item.item_id}: missing required_evidence")
        if not item.recommended_next_artifact:
            issues.append(f"{item.item_id}: missing recommended_next_artifact")
        for forbidden in (
            "calibration_signal_authorization",
            "trustreport_expansion",
            "mmm_ingestion",
        ):
            if forbidden not in item.forbidden_outputs:
                issues.append(f"{item.item_id}: missing forbidden {forbidden}")

    pause_items = [
        i for i in backlog if i.work_bucket == AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE
    ]
    downstream_paused = len(pause_items) >= 1

    first_artifact = "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001"
    p0_next = [
        i.recommended_next_artifact
        for i in backlog
        if i.priority == RefocusPriority.P0
        and i.work_bucket != AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE
    ]
    if first_artifact not in p0_next:
        issues.append("P0 must recommend STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001")

    return {
        "valid": not issues,
        "backlog_count": len(backlog),
        "priority_counts": _priority_counts(backlog),
        "bucket_counts": _bucket_counts(backlog),
        "downstream_work_paused": downstream_paused,
        "recommended_first_implementation_artifact": first_artifact,
        "issues": issues,
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


def build_scenarios(
    backlog: tuple[MethodRefocusBacklogItem, ...],
    validation: dict[str, Any],
) -> list[dict[str, Any]]:
    by_id = {item.item_id: item for item in backlog}
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("backlog_builds_successfully", len(backlog) >= 10))
    scenarios.append(_scenario("backlog_at_least_10_items", len(backlog) >= 10))

    for item_id in (
        "studentized_randomization_null_calibration",
        "scm_treated_set_placebo_null_calibration",
        "scm_augsynth_statistic_adapter_contract",
    ):
        item = by_id.get(item_id)
        scenarios.append(
            _scenario(
                f"p0_{item_id}_exists",
                item is not None and item.priority == RefocusPriority.P0,
            )
        )

    for item_id, bucket in (
        ("multicell_max_t_research_scout", AccuracyCompatibilityWorkBucket.MULTICELL_DEPENDENCE_RESEARCH),
        ("tbrridge_inference_remediation_or_retirement", AccuracyCompatibilityWorkBucket.INFERENCE_REMEDIATION),
        ("augsynth_jk_retirement_or_replacement", AccuracyCompatibilityWorkBucket.RETIRE_OR_PERMANENT_BLOCK),
    ):
        item = by_id.get(item_id)
        scenarios.append(
            _scenario(
                f"p1_{item_id}_exists",
                item is not None
                and item.priority == RefocusPriority.P1
                and item.work_bucket == bucket,
            )
        )

    for item_id in (
        "stratified_pooling_inference_scout",
        "design_assignment_generator_stress_tests",
    ):
        item = by_id.get(item_id)
        scenarios.append(
            _scenario(
                f"p2_{item_id}_exists",
                item is not None and item.priority == RefocusPriority.P2,
            )
        )

    scenarios.append(
        _scenario(
            "p3_dcm_adapter_disposition_exists",
            by_id.get("dcm_009_019_adapter_disposition") is not None
            and by_id["dcm_009_019_adapter_disposition"].priority == RefocusPriority.P3,
        )
    )
    scenarios.append(
        _scenario(
            "downstream_pause_item_exists",
            by_id.get("downstream_work_pause_marker") is not None,
        )
    )

    scenarios.append(
        _scenario(
            "every_item_has_root_issue",
            all(item.root_issue for item in backlog),
        )
    )
    scenarios.append(
        _scenario(
            "non_pause_items_have_required_evidence",
            all(
                item.required_evidence
                for item in backlog
                if item.work_bucket != AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE
            ),
        )
    )
    scenarios.append(
        _scenario(
            "every_item_has_recommended_next_artifact",
            all(item.recommended_next_artifact for item in backlog),
        )
    )
    scenarios.append(
        _scenario(
            "every_item_has_stop_go_criteria",
            all(item.stop_go_criteria for item in backlog),
        )
    )
    scenarios.append(
        _scenario(
            "every_item_has_forbidden_downstream_outputs",
            all(
                "calibration_signal_authorization" in item.forbidden_outputs
                for item in backlog
            ),
        )
    )

    for flag in (
        "calibration_signal_authorization",
        "trustreport_expansion",
        "mmm_ingestion",
        "llm_decisioning",
        "production_decisioning",
        "live_api_execution",
        "scheduler_execution",
        "budget_optimization",
    ):
        scenarios.append(
            _scenario(
                f"no_item_authorizes_{flag}",
                all(flag in item.forbidden_outputs for item in backlog),
            )
        )

    scenarios.append(
        _scenario(
            "summary_priority_counts_match",
            sum(validation["priority_counts"].values()) == validation["backlog_count"],
        )
    )
    scenarios.append(
        _scenario(
            "summary_bucket_counts_match",
            sum(validation["bucket_counts"].values()) == validation["backlog_count"],
        )
    )
    scenarios.append(
        _scenario(
            "recommended_first_artifact_studentized_null_calibration",
            validation["recommended_first_implementation_artifact"]
            == "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
        )
    )
    scenarios.append(
        _scenario("downstream_work_marked_paused", validation["downstream_work_paused"])
    )
    scenarios.append(
        _scenario(
            "audit_validation_passes",
            validation["valid"],
            detail="; ".join(validation.get("issues", [])),
        )
    )

    return scenarios


def run_method_accuracy_compatibility_refocus_audit() -> dict[str, Any]:
    """Run deterministic method-accuracy compatibility refocus audit."""
    backlog = build_method_accuracy_compatibility_backlog()
    validation = validate_method_accuracy_compatibility_refocus_audit(backlog)
    scenarios = build_scenarios(backlog, validation)
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    governance = {
        "calibration_signal_allowed": False,
        "trustreport_authorized": False,
        "mmm_ingestion_allowed": False,
        "llm_decisioning_allowed": False,
        "production_decisioning_allowed": False,
        "live_api_authorized": False,
        "scheduler_authorized": False,
        "budget_optimization_allowed": False,
    }

    p0_backlog = [
        i.recommended_next_artifact
        for i in backlog
        if i.priority == RefocusPriority.P0
        and i.work_bucket != AccuracyCompatibilityWorkBucket.DOWNSTREAM_PAUSE
    ]
    p1_backlog = [
        i.recommended_next_artifact
        for i in backlog
        if i.priority == RefocusPriority.P1
    ]
    p2_backlog = [
        i.recommended_next_artifact
        for i in backlog
        if i.priority == RefocusPriority.P2
    ]
    p3_backlog = [
        i.recommended_next_artifact
        for i in backlog
        if i.priority == RefocusPriority.P3
    ]

    return {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "verdict": _VERDICT,
        "governance_verdict": _VERDICT,
        "roadmap_spine": ROADMAP_SPINE,
        "backlog_count": validation["backlog_count"],
        "scenario_count": len(scenarios),
        "passed_scenarios": sum(1 for s in scenarios if s["passed"]),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "priority_counts": validation["priority_counts"],
        "bucket_counts": validation["bucket_counts"],
        "downstream_work_paused": validation["downstream_work_paused"],
        "paused_downstream_artifacts": list(PAUSED_DOWNSTREAM_ARTIFACTS),
        "recommended_first_implementation_artifact": validation[
            "recommended_first_implementation_artifact"
        ],
        "refocus_decisions": list(REFOCUS_DECISIONS),
        "p0_backlog": p0_backlog,
        "p1_backlog": p1_backlog,
        "p2_backlog": p2_backlog,
        "p3_backlog": p3_backlog,
        "backlog_summary": summarize_method_accuracy_compatibility_backlog(backlog),
        "next_artifact": "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
        **governance,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path, default=_DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = run_method_accuracy_compatibility_refocus_audit()
    if args.strict and summary["failed_scenarios"]:
        raise SystemExit(f"failed scenarios: {summary['failed_scenarios']}")

    if args.overwrite:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"artifact_id": _ARTIFACT_ID, "verdict": summary["verdict"]}))


if __name__ == "__main__":
    main()
