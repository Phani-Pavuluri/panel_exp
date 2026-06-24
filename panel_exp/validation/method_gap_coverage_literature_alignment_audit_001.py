"""METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001 validation harness."""

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

_ARTIFACT_ID = "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "method_gap_coverage_and_literature_alignment_audit_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001_summary.json"
)

ROADMAP_SPINE = [
    "ROADMAP_REFOCUS_METHOD_VALIDATION_001",
    "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001",
    "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001",
    "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001",
    "SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",
    "ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001",
    "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001",
    "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001",
]

RECOMMENDED_NEXT_ARTIFACTS = (
    "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",
    "SIMULATION_DGP_COVERAGE_PLAN_001",
    "METHOD_FAILURE_MODE_REGISTRY_001",
    "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",
    "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
    "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",
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

REQUIRED_DESIGN_FAMILIES = frozenset(
    {
        "single_treated_geo",
        "multi_treated_geo",
        "matched_pair",
        "matched_block",
        "stratified",
        "rerandomized",
        "greedy_matched_market",
        "kernel_thinning",
        "fixed_deterministic",
        "multicell_shared_control",
        "multicell_independent_cells",
        "unknown_assignment",
    }
)

REQUIRED_ESTIMATOR_FAMILIES = frozenset(
    {
        "scm",
        "augsynth_cvxpy",
        "did",
        "tbrridge",
        "tbr",
        "bayesian_tbr",
        "synthetic_did",
        "trop",
        "future_method_scout",
    }
)

REQUIRED_INFERENCE_FAMILIES = frozenset(
    {
        "unit_jackknife",
        "leave_one_treated_out_sensitivity",
        "treated_set_placebo_rank",
        "studentized_placebo_rank",
        "design_based_randomization",
        "permutation",
        "bootstrap",
        "block_residual_bootstrap",
        "kfold_cross_fit",
        "conformal",
        "bayesian_posterior_interval",
        "bayesian_posterior_predictive_check",
        "cluster_robust_analytic",
        "did_bootstrap",
        "max_t_multiplicity",
        "stepdown_multiplicity",
        "no_valid_inference",
    }
)

REQUIRED_OBSERVED_DATA_CONDITIONS = frozenset(
    {
        "small_n_geo_panel",
        "few_treated_units",
        "weak_donor_overlap",
        "poor_pre_period_fit",
        "short_pre_period",
        "short_post_period",
        "heteroskedasticity",
        "autocorrelation",
        "seasonality",
        "holiday_or_promo_shocks",
        "outlier_weeks",
        "metric_sparsity",
        "zero_inflation",
        "nonstationary_baseline",
        "spillover_risk",
        "contamination_risk",
        "treatment_heterogeneity",
        "shared_control_dependence",
    }
)

REQUIRED_SIMULATION_DGPS = frozenset(
    {
        "iid_null",
        "unit_fixed_effects",
        "unit_time_fixed_effects",
        "latent_factor",
        "donor_matched_latent_factor",
        "heteroskedasticity",
        "autocorrelation",
        "outliers",
        "seasonality_shocks",
        "sparse_conversion_metrics",
        "small_n_geo_panels",
        "spillover_scenarios",
        "heterogeneous_treatment_effects",
        "multicell_shared_control_dependence",
    }
)

REQUIRED_LITERATURE_BUCKETS = frozenset(
    {
        "synthetic_control_literature",
        "augmented_synthetic_control_literature",
        "difference_in_differences_literature",
        "geo_experiment_design_literature",
        "randomization_inference_literature",
        "permutation_placebo_literature",
        "bootstrap_panel_literature",
        "conformal_panel_literature",
        "bayesian_structural_time_series_literature",
        "multiple_testing_max_t_literature",
        "interference_spillover_literature",
        "small_sample_causal_inference_literature",
    }
)


class CoverageStatus(str, Enum):
    COVERED = "covered"
    PARTIALLY_COVERED = "partially_covered"
    PLANNED = "planned"
    GAP = "gap"
    BLOCKED = "blocked"
    RESEARCH_REQUIRED = "research_required"


class MethodAction(str, Enum):
    KEEP_RESTRICTED = "keep_restricted"
    REPAIR = "repair"
    REPLACE = "replace"
    RETIRE = "retire"
    BLOCK = "block"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SENSITIVITY_ONLY = "sensitivity_only"
    SCOUT_NEW_METHOD = "scout_new_method"
    DEFER_RESEARCH = "defer_research"


class EvidenceSource(str, Enum):
    REPO_REPORT = "repo_report"
    SUMMARY_JSON = "summary_json"
    VALIDATION_TEST = "validation_test"
    SUITABILITY_MATRIX = "suitability_matrix"
    PRIOR_AUDIT = "prior_audit"
    LITERATURE_BUCKET = "literature_bucket"
    PLANNED_ARTIFACT = "planned_artifact"
    MISSING = "missing"


@dataclass(frozen=True)
class GapCoverageRow:
    row_id: str
    dimension: str
    item: str
    current_status: CoverageStatus
    evidence_sources: tuple[EvidenceSource, ...]
    evidence_refs: tuple[str, ...]
    observed_gap: str
    literature_alignment_bucket: str | None
    recommended_action: MethodAction
    recommended_artifact: str | None
    downstream_blocking: bool
    notes: str


def _row(
    row_id: str,
    dimension: str,
    item: str,
    *,
    current_status: CoverageStatus,
    evidence_sources: tuple[EvidenceSource, ...],
    evidence_refs: tuple[str, ...],
    observed_gap: str,
    literature_alignment_bucket: str | None = None,
    recommended_action: MethodAction,
    recommended_artifact: str | None = None,
    downstream_blocking: bool = True,
    notes: str = "",
) -> GapCoverageRow:
    return GapCoverageRow(
        row_id=row_id,
        dimension=dimension,
        item=item,
        current_status=current_status,
        evidence_sources=evidence_sources,
        evidence_refs=evidence_refs,
        observed_gap=observed_gap,
        literature_alignment_bucket=literature_alignment_bucket,
        recommended_action=recommended_action,
        recommended_artifact=recommended_artifact,
        downstream_blocking=downstream_blocking,
        notes=notes,
    )


def _design_rows() -> tuple[GapCoverageRow, ...]:
    specs: list[tuple[str, CoverageStatus, MethodAction, str | None, str]] = [
        ("single_treated_geo", CoverageStatus.COVERED, MethodAction.KEEP_RESTRICTED, None, "Suitability matrix and D5 trust rows cover single-treated SCM/DID paths"),
        ("multi_treated_geo", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "AUGSYNTH_ESTIMATOR_BACKED_RANDOMIZATION_CALIBRATION_001", "Multi-treated paths need estimator-backed calibration"),
        ("matched_pair", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001", "DID matched-pair bootstrap present; design stress tests pending"),
        ("matched_block", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001", "Cluster-robust DID candidate requires design stress test"),
        ("stratified", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "STRATIFIED_POOLED_ESTIMAND_CONTRACT_001", "Per-stratum paths exist; pooled heterogeneity policy incomplete"),
        ("rerandomized", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001", "Null calibration exists; assignment-generator stress tests pending"),
        ("greedy_matched_market", CoverageStatus.PARTIALLY_COVERED, MethodAction.DIAGNOSTIC_ONLY, "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001", "Falsification-only placebo paths in suitability matrix"),
        ("kernel_thinning", CoverageStatus.PARTIALLY_COVERED, MethodAction.DIAGNOSTIC_ONLY, "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001", "Kernel thinning falsification-only in matrix"),
        ("fixed_deterministic", CoverageStatus.PARTIALLY_COVERED, MethodAction.DIAGNOSTIC_ONLY, None, "Deterministic assignment falsification-only documented"),
        ("multicell_shared_control", CoverageStatus.RESEARCH_REQUIRED, MethodAction.DEFER_RESEARCH, "MULTICELL_MAX_T_RESEARCH_SCOUT_001", "Dependence and max-T research required"),
        ("multicell_independent_cells", CoverageStatus.RESEARCH_REQUIRED, MethodAction.DEFER_RESEARCH, "MULTICELL_MAX_T_RESEARCH_SCOUT_001", "Stepdown multiplicity research required"),
        ("unknown_assignment", CoverageStatus.BLOCKED, MethodAction.BLOCK, None, "Unknown assignment blocks design-based inference across matrix"),
    ]
    return tuple(
        _row(
            f"design_{item}",
            "design_family",
            item,
            current_status=status,
            evidence_sources=(EvidenceSource.SUITABILITY_MATRIX, EvidenceSource.REPO_REPORT),
            evidence_refs=("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001", "docs/track_d/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_REPORT.md"),
            observed_gap=gap,
            literature_alignment_bucket="geo_experiment_design_literature",
            recommended_action=action,
            recommended_artifact=artifact,
            notes=gap,
        )
        for item, status, action, artifact, gap in specs
    )


def _estimator_rows() -> tuple[GapCoverageRow, ...]:
    specs: list[tuple[str, CoverageStatus, MethodAction, str | None, str, str | None]] = [
        ("scm", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, None, "SCM paths mapped; observed-panel diagnostics not yet formalized", "synthetic_control_literature"),
        ("augsynth_cvxpy", CoverageStatus.PARTIALLY_COVERED, MethodAction.REPAIR, "SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001", "JK retire/replace; adapter contracts exist", "augmented_synthetic_control_literature"),
        ("did", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001", "DID bootstrap restricted research; calibration incomplete", "difference_in_differences_literature"),
        ("tbrridge", CoverageStatus.GAP, MethodAction.REPAIR, "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001", "BRB/KFold/placebo failures documented", "bootstrap_panel_literature"),
        ("tbr", CoverageStatus.BLOCKED, MethodAction.BLOCK, None, "Aggregate geometry mismatch blocked", "bayesian_structural_time_series_literature"),
        ("bayesian_tbr", CoverageStatus.RESEARCH_REQUIRED, MethodAction.DIAGNOSTIC_ONLY, None, "Posterior diagnostic-only; no decision-safe path", "bayesian_structural_time_series_literature"),
        ("synthetic_did", CoverageStatus.GAP, MethodAction.SCOUT_NEW_METHOD, None, "Not implemented; research scout warranted", "synthetic_control_literature"),
        ("trop", CoverageStatus.GAP, MethodAction.SCOUT_NEW_METHOD, None, "TROP research deferred; audit program only", "synthetic_control_literature"),
        ("future_method_scout", CoverageStatus.PLANNED, MethodAction.SCOUT_NEW_METHOD, "METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001", "Explicit scout lane for weak existing paths", None),
    ]
    return tuple(
        _row(
            f"estimator_{item}",
            "estimator_family",
            item,
            current_status=status,
            evidence_sources=(EvidenceSource.SUITABILITY_MATRIX, EvidenceSource.PRIOR_AUDIT),
            evidence_refs=("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001", "METHOD_ACCURACY_COMPATIBILITY_REFOCUS_AUDIT_001"),
            observed_gap=gap,
            literature_alignment_bucket=lit,
            recommended_action=action,
            recommended_artifact=artifact,
            notes=gap,
        )
        for item, status, action, artifact, gap, lit in specs
    )


def _inference_rows() -> tuple[GapCoverageRow, ...]:
    specs: list[tuple[str, CoverageStatus, MethodAction, str | None, str, str | None]] = [
        ("unit_jackknife", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, None, "SCM JK restricted research; AugSynth JK retire", "randomization_inference_literature"),
        ("leave_one_treated_out_sensitivity", CoverageStatus.COVERED, MethodAction.SENSITIVITY_ONLY, None, "Sensitivity-only path in matrix", None),
        ("treated_set_placebo_rank", CoverageStatus.PARTIALLY_COVERED, MethodAction.DIAGNOSTIC_ONLY, "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001", "Null calibration harness exists; not production", "permutation_placebo_literature"),
        ("studentized_placebo_rank", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001", "Calibration candidate after null harness", "randomization_inference_literature"),
        ("design_based_randomization", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001", "One inference family only; not full layer", "randomization_inference_literature"),
        ("permutation", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001", "DID permutation candidate; not fully validated", "permutation_placebo_literature"),
        ("bootstrap", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, None, "Multiple bootstrap paths; TBRRidge blocked", "bootstrap_panel_literature"),
        ("block_residual_bootstrap", CoverageStatus.GAP, MethodAction.REPAIR, "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001", "TBRRidge BRB known failure", "bootstrap_panel_literature"),
        ("kfold_cross_fit", CoverageStatus.GAP, MethodAction.DIAGNOSTIC_ONLY, "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001", "TBRRidge KFold elevated null FPR", "bootstrap_panel_literature"),
        ("conformal", CoverageStatus.BLOCKED, MethodAction.SCOUT_NEW_METHOD, None, "Conformal blocked; scout panel conformal literature", "conformal_panel_literature"),
        ("bayesian_posterior_interval", CoverageStatus.RESEARCH_REQUIRED, MethodAction.DIAGNOSTIC_ONLY, None, "Posterior diagnostic-only", "bayesian_structural_time_series_literature"),
        ("bayesian_posterior_predictive_check", CoverageStatus.RESEARCH_REQUIRED, MethodAction.DIAGNOSTIC_ONLY, None, "Predictive check diagnostic-only", "bayesian_structural_time_series_literature"),
        ("cluster_robust_analytic", CoverageStatus.RESEARCH_REQUIRED, MethodAction.DEFER_RESEARCH, "DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001", "Not credible at geo counts per scout", "difference_in_differences_literature"),
        ("did_bootstrap", CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001", "Restricted research candidate", "difference_in_differences_literature"),
        ("max_t_multiplicity", CoverageStatus.GAP, MethodAction.DEFER_RESEARCH, "MULTICELL_MAX_T_RESEARCH_SCOUT_001", "Multicell dependence research required", "multiple_testing_max_t_literature"),
        ("stepdown_multiplicity", CoverageStatus.GAP, MethodAction.DEFER_RESEARCH, "MULTICELL_MAX_T_RESEARCH_SCOUT_001", "Familywise calibration unresolved", "multiple_testing_max_t_literature"),
        ("no_valid_inference", CoverageStatus.COVERED, MethodAction.BLOCK, None, "Explicit blocked paths registered in matrix", None),
    ]
    return tuple(
        _row(
            f"inference_{item}",
            "inference_family",
            item,
            current_status=status,
            evidence_sources=(EvidenceSource.SUITABILITY_MATRIX, EvidenceSource.SUMMARY_JSON),
            evidence_refs=("ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001", "docs/track_d/archives/ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001_summary.json"),
            observed_gap=gap,
            literature_alignment_bucket=lit,
            recommended_action=action,
            recommended_artifact=artifact,
            notes=gap,
        )
        for item, status, action, artifact, gap, lit in specs
    )


def _observed_data_rows() -> tuple[GapCoverageRow, ...]:
    return tuple(
        _row(
            f"observed_{item}",
            "observed_data_condition",
            item,
            current_status=CoverageStatus.PLANNED,
            evidence_sources=(EvidenceSource.PLANNED_ARTIFACT, EvidenceSource.MISSING),
            evidence_refs=("ROADMAP_INFERENCE_AND_METHOD_GAP_CONTROL_REFOCUS_001",),
            observed_gap=f"No formal observed-panel diagnostic contract for {item.replace('_', ' ')}",
            literature_alignment_bucket="small_sample_causal_inference_literature",
            recommended_action=MethodAction.DEFER_RESEARCH,
            recommended_artifact="OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",
            notes="Observed-panel diagnostics required before production-like method selection",
        )
        for item in sorted(REQUIRED_OBSERVED_DATA_CONDITIONS)
    )


def _simulation_dgp_rows() -> tuple[GapCoverageRow, ...]:
    return tuple(
        _row(
            f"simulation_dgp_{item}",
            "simulation_dgp_condition",
            item,
            current_status=CoverageStatus.PLANNED if item != "iid_null" else CoverageStatus.PARTIALLY_COVERED,
            evidence_sources=(
                (EvidenceSource.PRIOR_AUDIT, EvidenceSource.PLANNED_ARTIFACT)
                if item != "iid_null"
                else (EvidenceSource.PRIOR_AUDIT, EvidenceSource.VALIDATION_TEST)
            ),
            evidence_refs=(
                ("STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001", "SIMULATION_DGP_COVERAGE_PLAN_001")
                if item != "iid_null"
                else ("STUDENTIZED_RANDOMIZATION_NULL_CALIBRATION_001", "SCM_TREATED_SET_PLACEBO_NULL_CALIBRATION_001")
            ),
            observed_gap=(
                "Toy null grids in individual harnesses; master DGP plan missing"
                if item != "iid_null"
                else "Partial iid null coverage in existing calibration harnesses only"
            ),
            literature_alignment_bucket="randomization_inference_literature",
            recommended_action=MethodAction.DEFER_RESEARCH,
            recommended_artifact="SIMULATION_DGP_COVERAGE_PLAN_001",
            notes="Centralize simulation DGP coverage before expanding calibration harnesses",
        )
        for item in sorted(REQUIRED_SIMULATION_DGPS)
    )


def _literature_rows() -> tuple[GapCoverageRow, ...]:
    bucket_notes: dict[str, tuple[CoverageStatus, MethodAction, str]] = {
        "synthetic_control_literature": (CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "SCM suitability matrix rows; formal literature review pending"),
        "augmented_synthetic_control_literature": (CoverageStatus.PARTIALLY_COVERED, MethodAction.REPAIR, "AugSynth adapter contract; JK retire path documented"),
        "difference_in_differences_literature": (CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "DID bootstrap candidate; suitability audit pending"),
        "geo_experiment_design_literature": (CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "Design assignment generators; stress tests pending"),
        "randomization_inference_literature": (CoverageStatus.PARTIALLY_COVERED, MethodAction.KEEP_RESTRICTED, "Studentized null calibration; not production-validated"),
        "permutation_placebo_literature": (CoverageStatus.PARTIALLY_COVERED, MethodAction.DIAGNOSTIC_ONLY, "Placebo one family only; falsification paths documented"),
        "bootstrap_panel_literature": (CoverageStatus.GAP, MethodAction.REPAIR, "TBRRidge BRB failure; panel bootstrap theory not aligned"),
        "conformal_panel_literature": (CoverageStatus.GAP, MethodAction.SCOUT_NEW_METHOD, "Conformal blocked; formal panel conformal scout needed"),
        "bayesian_structural_time_series_literature": (CoverageStatus.RESEARCH_REQUIRED, MethodAction.DIAGNOSTIC_ONLY, "Bayesian TBR posterior diagnostic-only"),
        "multiple_testing_max_t_literature": (CoverageStatus.GAP, MethodAction.DEFER_RESEARCH, "Multicell max-T/stepdown research scout required"),
        "interference_spillover_literature": (CoverageStatus.GAP, MethodAction.SCOUT_NEW_METHOD, "Spillover scenarios not in master DGP plan"),
        "small_sample_causal_inference_literature": (CoverageStatus.PLANNED, MethodAction.DEFER_RESEARCH, "Small-N geo diagnostics planned via observed-panel requirements"),
    }
    return tuple(
        _row(
            f"literature_{bucket}",
            "literature_alignment_bucket",
            bucket,
            current_status=bucket_notes[bucket][0],
            evidence_sources=(EvidenceSource.LITERATURE_BUCKET, EvidenceSource.SUITABILITY_MATRIX),
            evidence_refs=("METHOD_GAP_COVERAGE_AND_LITERATURE_ALIGNMENT_AUDIT_001", "ESTIMATOR_DESIGN_INFERENCE_SUITABILITY_MATRIX_001"),
            observed_gap="Formal literature alignment review required before promotion",
            literature_alignment_bucket=bucket,
            recommended_action=bucket_notes[bucket][1],
            recommended_artifact=(
                "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001"
                if bucket == "small_sample_causal_inference_literature"
                else "METHOD_FAILURE_MODE_REGISTRY_001"
                if bucket in {"bootstrap_panel_literature", "multiple_testing_max_t_literature"}
                else "MULTICELL_MAX_T_RESEARCH_SCOUT_001"
                if bucket in {"multiple_testing_max_t_literature", "interference_spillover_literature"}
                else None
            ),
            notes=bucket_notes[bucket][2],
        )
        for bucket in sorted(REQUIRED_LITERATURE_BUCKETS)
    )


def build_method_gap_coverage_rows() -> tuple[GapCoverageRow, ...]:
    """Return governed method-gap coverage and literature-alignment audit rows."""
    return (
        *_design_rows(),
        *_estimator_rows(),
        *_inference_rows(),
        *_observed_data_rows(),
        *_simulation_dgp_rows(),
        *_literature_rows(),
    )


def filter_gap_coverage_rows(
    rows: tuple[GapCoverageRow, ...],
    *,
    dimension: str | None = None,
    status: CoverageStatus | None = None,
    action: MethodAction | None = None,
) -> tuple[GapCoverageRow, ...]:
    """Filter audit rows by optional dimension predicates."""
    filtered: list[GapCoverageRow] = []
    for row in rows:
        if dimension is not None and row.dimension != dimension:
            continue
        if status is not None and row.current_status != status:
            continue
        if action is not None and row.recommended_action != action:
            continue
        filtered.append(row)
    return tuple(filtered)


def validate_method_gap_coverage(rows: tuple[GapCoverageRow, ...]) -> dict[str, Any]:
    """Validate audit invariants and return structured validation summary."""
    issues: list[str] = []
    row_ids = [row.row_id for row in rows]

    if len(row_ids) != len(set(row_ids)):
        issues.append("duplicate row_id detected")
    if len(rows) < 60:
        issues.append(f"row_count {len(rows)} < 60")

    def _missing(required: frozenset[str], present: set[str], label: str) -> None:
        missing = sorted(required - present)
        if missing:
            issues.append(f"missing {label}: {missing}")

    _missing(REQUIRED_DESIGN_FAMILIES, {r.item for r in rows if r.dimension == "design_family"}, "design families")
    _missing(REQUIRED_ESTIMATOR_FAMILIES, {r.item for r in rows if r.dimension == "estimator_family"}, "estimator families")
    _missing(REQUIRED_INFERENCE_FAMILIES, {r.item for r in rows if r.dimension == "inference_family"}, "inference families")
    _missing(
        REQUIRED_OBSERVED_DATA_CONDITIONS,
        {r.item for r in rows if r.dimension == "observed_data_condition"},
        "observed-data conditions",
    )
    _missing(
        REQUIRED_SIMULATION_DGPS,
        {r.item for r in rows if r.dimension == "simulation_dgp_condition"},
        "simulation DGP conditions",
    )
    _missing(
        REQUIRED_LITERATURE_BUCKETS,
        {r.item for r in rows if r.dimension == "literature_alignment_bucket"},
        "literature buckets",
    )

    actions = {row.recommended_action for row in rows}
    artifacts = {row.recommended_artifact for row in rows if row.recommended_artifact}

    if MethodAction.REPAIR not in actions:
        issues.append("no rows recommend repair")
    if not ({MethodAction.RETIRE, MethodAction.BLOCK} & actions):
        issues.append("no rows recommend retire or block")
    if MethodAction.SCOUT_NEW_METHOD not in actions:
        issues.append("no rows recommend scout_new_method")
    if "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001" not in artifacts:
        issues.append("no rows recommend observed-panel diagnostics artifact")
    if "SIMULATION_DGP_COVERAGE_PLAN_001" not in artifacts:
        issues.append("no rows recommend simulation DGP coverage artifact")
    if "METHOD_FAILURE_MODE_REGISTRY_001" not in artifacts:
        issues.append("no rows recommend failure-mode registry artifact")

    return {
        "valid": not issues,
        "row_count": len(rows),
        "unique_row_ids": len(row_ids) == len(set(row_ids)),
        "required_designs_covered": not (REQUIRED_DESIGN_FAMILIES - {r.item for r in rows if r.dimension == "design_family"}),
        "required_estimators_covered": not (REQUIRED_ESTIMATOR_FAMILIES - {r.item for r in rows if r.dimension == "estimator_family"}),
        "required_inference_families_covered": not (
            REQUIRED_INFERENCE_FAMILIES - {r.item for r in rows if r.dimension == "inference_family"}
        ),
        "required_observed_data_conditions_covered": not (
            REQUIRED_OBSERVED_DATA_CONDITIONS - {r.item for r in rows if r.dimension == "observed_data_condition"}
        ),
        "required_simulation_dgps_covered": not (
            REQUIRED_SIMULATION_DGPS - {r.item for r in rows if r.dimension == "simulation_dgp_condition"}
        ),
        "required_literature_buckets_covered": not (
            REQUIRED_LITERATURE_BUCKETS - {r.item for r in rows if r.dimension == "literature_alignment_bucket"}
        ),
        "issues": issues,
    }


def summarize_method_gap_coverage(rows: tuple[GapCoverageRow, ...]) -> dict[str, Any]:
    """Serialize method-gap coverage audit summary for validation archives."""
    validation = validate_method_gap_coverage(rows)
    status_counts = Counter(row.current_status.value for row in rows)
    action_counts = Counter(row.recommended_action.value for row in rows)
    dimension_counts = Counter(row.dimension for row in rows)

    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "coverage_status_counts": dict(status_counts),
        "recommended_action_counts": dict(action_counts),
        "dimension_counts": dict(dimension_counts),
        "required_designs_covered": validation["required_designs_covered"],
        "required_estimators_covered": validation["required_estimators_covered"],
        "required_inference_families_covered": validation["required_inference_families_covered"],
        "required_observed_data_conditions_covered": validation["required_observed_data_conditions_covered"],
        "required_simulation_dgps_covered": validation["required_simulation_dgps_covered"],
        "required_literature_buckets_covered": validation["required_literature_buckets_covered"],
        "suitability_matrix_sufficient_alone": False,
        "observed_panel_diagnostics_required": True,
        "simulation_dgp_coverage_plan_required": True,
        "failure_mode_registry_required": True,
        "literature_alignment_required_before_promotion": True,
        "new_method_scouts_required": True,
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
    rows = build_method_gap_coverage_rows()
    validation = validate_method_gap_coverage(rows)
    summary = summarize_method_gap_coverage(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("row_count_at_least_60", len(rows) >= 60))
    scenarios.append(_scenario("row_ids_unique", validation["unique_row_ids"]))
    scenarios.append(_scenario("required_designs_covered", validation["required_designs_covered"]))
    scenarios.append(_scenario("required_estimators_covered", validation["required_estimators_covered"]))
    scenarios.append(_scenario("required_inference_families_covered", validation["required_inference_families_covered"]))
    scenarios.append(_scenario("required_observed_data_conditions_covered", validation["required_observed_data_conditions_covered"]))
    scenarios.append(_scenario("required_simulation_dgps_covered", validation["required_simulation_dgps_covered"]))
    scenarios.append(_scenario("required_literature_buckets_covered", validation["required_literature_buckets_covered"]))
    scenarios.append(_scenario("has_repair_recommendations", MethodAction.REPAIR in {r.recommended_action for r in rows}))
    scenarios.append(_scenario("has_retire_or_block_recommendations", bool({MethodAction.RETIRE, MethodAction.BLOCK} & {r.recommended_action for r in rows})))
    scenarios.append(_scenario("has_scout_new_method_recommendations", MethodAction.SCOUT_NEW_METHOD in {r.recommended_action for r in rows}))
    scenarios.append(_scenario("recommends_observed_panel_diagnostics", any(r.recommended_artifact == "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001" for r in rows)))
    scenarios.append(_scenario("recommends_simulation_dgp_plan", any(r.recommended_artifact == "SIMULATION_DGP_COVERAGE_PLAN_001" for r in rows)))
    scenarios.append(_scenario("recommends_failure_mode_registry", any(r.recommended_artifact == "METHOD_FAILURE_MODE_REGISTRY_001" for r in rows)))
    scenarios.append(_scenario("suitability_matrix_not_sufficient_alone", summary["suitability_matrix_sufficient_alone"] is False))
    scenarios.append(_scenario("observed_panel_diagnostics_required", summary["observed_panel_diagnostics_required"] is True))
    scenarios.append(_scenario("simulation_dgp_plan_required", summary["simulation_dgp_coverage_plan_required"] is True))
    scenarios.append(_scenario("failure_mode_registry_required", summary["failure_mode_registry_required"] is True))
    scenarios.append(_scenario("literature_alignment_required", summary["literature_alignment_required_before_promotion"] is True))
    scenarios.append(_scenario("new_method_scouts_required", summary["new_method_scouts_required"] is True))
    scenarios.append(_scenario("downstream_work_paused", summary["downstream_work_paused"] is True))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    for idx, artifact in enumerate(RECOMMENDED_NEXT_ARTIFACTS[:3]):
        scenarios.append(_scenario(f"recommended_next_artifact_rank_{idx + 1}_{artifact.lower()}", summary["recommended_next_artifacts"][idx] == artifact))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_method_gap_coverage_rows()
    validation = validate_method_gap_coverage(rows)
    summary = summarize_method_gap_coverage(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "roadmap_spine": ROADMAP_SPINE,
        "row_count": len(rows),
        "failed_scenarios": failed,
        "scenario_results": scenarios,
        "validation": validation,
        **summary,
    }

    if write_summary:
        out = summary_path or _DEFAULT_SUMMARY
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=_ARTIFACT_ID)
    parser.add_argument("--summary", type=Path, default=_DEFAULT_SUMMARY)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = run_validation(write_summary=not args.no_write, summary_path=args.summary)
    print(json.dumps({"verdict": result["verdict"], "failed_scenarios": result["failed_scenarios"]}, indent=2))
    if result["failed_scenarios"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
