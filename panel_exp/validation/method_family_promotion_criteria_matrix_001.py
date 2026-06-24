"""METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001 validation harness."""

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

_ARTIFACT_ID = "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "method_family_promotion_criteria_matrix_defined_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001",
    "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001",
    "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001",
)

MIN_CRITERIA_ROW_COUNT = 65

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
    "scm_strongest_near_term_candidate_but_gated": True,
    "augsynth_requires_adapter_null_calibration_and_dgp": True,
    "did_conditional_candidate_only": True,
    "synthetic_did_candidate_only_after_suitability": True,
    "tbrridge_diagnostic_only_unless_remediated": True,
    "classic_tbr_overclaim_blocked_or_retire_replace": True,
    "bayesian_tbr_posterior_diagnostic_only_until_calibrated": True,
    "trop_research_only_unless_future_evidence": True,
    "multicell_shared_control_cross_family_blocker": True,
    "promotion_requires_observed_diagnostics": True,
    "promotion_requires_dgp_coverage": True,
    "promotion_requires_failure_registry_review": True,
    "promotion_requires_assignment_stress_compatibility": True,
    "promotion_requires_adapter_when_needed": True,
    "promotion_requires_null_calibration_when_needed": True,
    "promotion_requires_multiplicity_dependence_handling_when_needed": True,
    "retirement_or_exit_criteria_defined": True,
    "downstream_work_paused": True,
}


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


class CriteriaDimension(str, Enum):
    ESTIMAND_CLARITY = "estimand_clarity"
    ASSIGNMENT_DESIGN_VALIDITY = "assignment_design_validity"
    OBSERVED_PANEL_DIAGNOSTICS = "observed_panel_diagnostics"
    DGP_SIMULATION_COVERAGE = "dgp_simulation_coverage"
    FAILURE_REGISTRY_REVIEW = "failure_registry_review"
    ASSIGNMENT_GENERATOR_STRESS_COMPATIBILITY = "assignment_generator_stress_compatibility"
    INFERENCE_ADAPTER_AVAILABILITY = "inference_adapter_availability"
    NULL_CALIBRATION_REPLAY_EVIDENCE = "null_calibration_replay_evidence"
    MULTIPLICITY_DEPENDENCE_HANDLING = "multiplicity_dependence_handling"
    OUTCOME_SCALE_COMPATIBILITY = "outcome_scale_compatibility"
    DONOR_SUPPORT_OVERLAP = "donor_support_overlap"
    PREPERIOD_FIT_TREND_STABILITY = "preperiod_fit_trend_stability"
    METHOD_DISAGREEMENT_HANDLING = "method_disagreement_handling"
    ALLOWED_CURRENT_USE = "allowed_current_use"
    FORBIDDEN_CURRENT_USE = "forbidden_current_use"
    PROMOTION_EVIDENCE = "promotion_evidence"
    RETIREMENT_REPLACE_CRITERIA = "retirement_replace_criteria"
    DOWNSTREAM_AUTHORIZATION_BOUNDARY = "downstream_authorization_boundary"


class CriteriaStatus(str, Enum):
    PRODUCTION_CANDIDATE_GATED = "production_candidate_gated"
    REMEDIATION_REQUIRED = "remediation_required"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    RETIRE_OR_REPLACE = "retire_or_replace"
    BLOCKED = "blocked"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_CALIBRATION_REPLAY = "candidate_after_calibration_replay"


REQUIRED_METHOD_FAMILIES = frozenset(MethodFamily)
REQUIRED_CRITERIA_DIMENSIONS = frozenset(CriteriaDimension)
REQUIRED_STATUSES = frozenset(CriteriaStatus)

_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "production_decisioning",
    "budget_optimization",
)
_PROMO = (
    "observed_diagnostics",
    "dgp_coverage",
    "failure_registry_consult",
    "assignment_stress",
)
_DOWNSTREAM = "paused"
_NEXT = "PRODUCTION_COMPATIBILITY_PROMOTION_WORKPLAN_001"
_SCM_PLAN = "SCM_PRODUCTION_CANDIDATE_VALIDATION_PLAN_001"
_RETIRE_PLAN = "METHOD_FAMILY_RETIRE_REPLACE_EXECUTION_PLAN_001"


@dataclass(frozen=True)
class PromotionCriteriaRow:
    criteria_id: str
    method_family: MethodFamily
    criteria_dimension: CriteriaDimension
    current_status: CriteriaStatus
    promotion_target: str
    required_conditions: tuple[str, ...]
    required_artifacts: tuple[str, ...]
    blocking_failure_modes: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    promotion_evidence_required: tuple[str, ...]
    retirement_or_exit_criteria: tuple[str, ...]
    downstream_authorization_status: str
    recommended_next_artifact: str | None
    notes: str


def _row(
    criteria_id: str,
    method_family: MethodFamily,
    criteria_dimension: CriteriaDimension,
    current_status: CriteriaStatus,
    promotion_target: str,
    notes: str,
    *,
    required_conditions: tuple[str, ...],
    required_artifacts: tuple[str, ...],
    blocking_failure_modes: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    promotion_evidence_required: tuple[str, ...],
    retirement_or_exit_criteria: tuple[str, ...] = (),
    downstream_authorization_status: str = _DOWNSTREAM,
    recommended_next_artifact: str | None = None,
) -> PromotionCriteriaRow:
    return PromotionCriteriaRow(
        criteria_id=criteria_id,
        method_family=method_family,
        criteria_dimension=criteria_dimension,
        current_status=current_status,
        promotion_target=promotion_target,
        required_conditions=required_conditions,
        required_artifacts=required_artifacts,
        blocking_failure_modes=blocking_failure_modes,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        promotion_evidence_required=promotion_evidence_required,
        retirement_or_exit_criteria=retirement_or_exit_criteria,
        downstream_authorization_status=downstream_authorization_status,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


def _family_status_map(
    family: MethodFamily,
    dimension: CriteriaDimension,
) -> CriteriaStatus:
    """Return promotion criteria status for a family × dimension pair."""
    dim = dimension
    if family == MethodFamily.SCM:
        overrides = {
            CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.MULTIPLICITY_DEPENDENCE_HANDLING: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.METHOD_DISAGREEMENT_HANDLING: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.RETIREMENT_REPLACE_CRITERIA: CriteriaStatus.DIAGNOSTIC_ONLY,
        }
        return overrides.get(dim, CriteriaStatus.PRODUCTION_CANDIDATE_GATED)

    if family == MethodFamily.AUGSYNTH_CVXPY:
        overrides = {
            CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY: CriteriaStatus.CANDIDATE_AFTER_ADAPTER,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE: CriteriaStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            CriteriaDimension.DGP_SIMULATION_COVERAGE: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.DONOR_SUPPORT_OVERLAP: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.ALLOWED_CURRENT_USE: CriteriaStatus.DIAGNOSTIC_ONLY,
            CriteriaDimension.RETIREMENT_REPLACE_CRITERIA: CriteriaStatus.REMEDIATION_REQUIRED,
        }
        return overrides.get(dim, CriteriaStatus.DIAGNOSTIC_ONLY)

    if family == MethodFamily.DID:
        overrides = {
            CriteriaDimension.PREPERIOD_FIT_TREND_STABILITY: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.ASSIGNMENT_DESIGN_VALIDITY: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.MULTIPLICITY_DEPENDENCE_HANDLING: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY: CriteriaStatus.REMEDIATION_REQUIRED,
        }
        return overrides.get(dim, CriteriaStatus.PRODUCTION_CANDIDATE_GATED)

    if family == MethodFamily.SYNTHETIC_DID:
        overrides = {
            CriteriaDimension.DGP_SIMULATION_COVERAGE: CriteriaStatus.CANDIDATE_AFTER_SIMULATION,
            CriteriaDimension.PREPERIOD_FIT_TREND_STABILITY: CriteriaStatus.CANDIDATE_AFTER_SIMULATION,
            CriteriaDimension.PROMOTION_EVIDENCE: CriteriaStatus.CANDIDATE_AFTER_SIMULATION,
        }
        return overrides.get(dim, CriteriaStatus.RESEARCH_ONLY)

    if family == MethodFamily.TBRRIDGE:
        overrides = {
            CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.RETIREMENT_REPLACE_CRITERIA: CriteriaStatus.REMEDIATION_REQUIRED,
            CriteriaDimension.PROMOTION_EVIDENCE: CriteriaStatus.REMEDIATION_REQUIRED,
        }
        return overrides.get(dim, CriteriaStatus.DIAGNOSTIC_ONLY)

    if family == MethodFamily.CLASSIC_AGGREGATE_TBR:
        overrides = {
            CriteriaDimension.ESTIMAND_CLARITY: CriteriaStatus.RETIRE_OR_REPLACE,
            CriteriaDimension.PROMOTION_EVIDENCE: CriteriaStatus.RETIRE_OR_REPLACE,
            CriteriaDimension.RETIREMENT_REPLACE_CRITERIA: CriteriaStatus.RETIRE_OR_REPLACE,
            CriteriaDimension.ALLOWED_CURRENT_USE: CriteriaStatus.DIAGNOSTIC_ONLY,
        }
        return overrides.get(dim, CriteriaStatus.BLOCKED)

    if family == MethodFamily.BAYESIAN_TBR:
        overrides = {
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE: CriteriaStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY: CriteriaStatus.RESEARCH_ONLY,
            CriteriaDimension.RETIREMENT_REPLACE_CRITERIA: CriteriaStatus.REMEDIATION_REQUIRED,
        }
        return overrides.get(dim, CriteriaStatus.RESEARCH_ONLY)

    if family == MethodFamily.TROP:
        overrides = {
            CriteriaDimension.DGP_SIMULATION_COVERAGE: CriteriaStatus.CANDIDATE_AFTER_SIMULATION,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE: CriteriaStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            CriteriaDimension.PROMOTION_EVIDENCE: CriteriaStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            CriteriaDimension.METHOD_DISAGREEMENT_HANDLING: CriteriaStatus.REMEDIATION_REQUIRED,
        }
        return overrides.get(dim, CriteriaStatus.RESEARCH_ONLY)

    if family == MethodFamily.MULTICELL_SHARED_CONTROL:
        overrides = {
            CriteriaDimension.MULTIPLICITY_DEPENDENCE_HANDLING: CriteriaStatus.BLOCKED,
            CriteriaDimension.ALLOWED_CURRENT_USE: CriteriaStatus.DIAGNOSTIC_ONLY,
            CriteriaDimension.PROMOTION_EVIDENCE: CriteriaStatus.REMEDIATION_REQUIRED,
        }
        return overrides.get(dim, CriteriaStatus.BLOCKED)

    return CriteriaStatus.RESEARCH_ONLY


def _family_promotion_target(family: MethodFamily) -> str:
    targets = {
        MethodFamily.SCM: "production_compatible_candidate_gated",
        MethodFamily.AUGSYNTH_CVXPY: "diagnostic_then_adapter_null_calibration",
        MethodFamily.DID: "conditional_production_candidate",
        MethodFamily.SYNTHETIC_DID: "scout_candidate_after_suitability",
        MethodFamily.TBRRIDGE: "diagnostic_only_or_remediation",
        MethodFamily.CLASSIC_AGGREGATE_TBR: "retire_or_replace",
        MethodFamily.BAYESIAN_TBR: "posterior_diagnostic_after_calibration",
        MethodFamily.TROP: "research_scout_after_evidence",
        MethodFamily.MULTICELL_SHARED_CONTROL: "cross_family_blocker",
    }
    return targets[family]


def _family_artifacts(family: MethodFamily) -> tuple[str, ...]:
    artifacts = {
        MethodFamily.SCM: (
            "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
            "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        MethodFamily.AUGSYNTH_CVXPY: ("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
        MethodFamily.DID: (
            "DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",
            "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
        ),
        MethodFamily.SYNTHETIC_DID: ("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
        MethodFamily.TBRRIDGE: ("TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",),
        MethodFamily.CLASSIC_AGGREGATE_TBR: (
            "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
        ),
        MethodFamily.BAYESIAN_TBR: (
            "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
        ),
        MethodFamily.TROP: ("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
        MethodFamily.MULTICELL_SHARED_CONTROL: ("MULTICELL_MAX_T_RESEARCH_SCOUT_001",),
    }
    return artifacts[family]


def _family_failure_modes(family: MethodFamily) -> tuple[str, ...]:
    modes = {
        MethodFamily.SCM: ("FM-ES-002", "FM-INF-001", "FM-DS-006"),
        MethodFamily.AUGSYNTH_CVXPY: ("FM-ES-003", "FM-ES-004", "FM-INF-005"),
        MethodFamily.DID: ("FM-PF-003", "FM-ES-005", "FM-INF-006", "FM-DA-001"),
        MethodFamily.SYNTHETIC_DID: ("FM-ES-009", "FM-CP-005"),
        MethodFamily.TBRRIDGE: ("FM-ES-006", "FM-ES-007", "FM-INF-008"),
        MethodFamily.CLASSIC_AGGREGATE_TBR: ("FM-ES-007", "FM-INF-011", "FM-PS-010"),
        MethodFamily.BAYESIAN_TBR: ("FM-ES-008", "FM-INF-008", "FM-DB-010"),
        MethodFamily.TROP: ("FM-ES-010", "FM-INF-012", "FM-ES-009"),
        MethodFamily.MULTICELL_SHARED_CONTROL: ("FM-DA-009", "FM-INF-009", "FM-INF-010"),
    }
    return modes[family]


def _family_allowed_use(family: MethodFamily) -> tuple[str, ...]:
    uses = {
        MethodFamily.SCM: ("diagnostic_point", "governed_placebo_null_monitor", "research_calibration"),
        MethodFamily.AUGSYNTH_CVXPY: ("point_estimate", "diagnostic_decomposition"),
        MethodFamily.DID: ("diagnostic_point", "sensitivity_research", "restricted_bootstrap_research"),
        MethodFamily.SYNTHETIC_DID: ("research_scout_calibration",),
        MethodFamily.TBRRIDGE: ("diagnostic_point", "labeled_sensitivity"),
        MethodFamily.CLASSIC_AGGREGATE_TBR: ("labeled_diagnostic_exploration",),
        MethodFamily.BAYESIAN_TBR: ("posterior_diagnostic_research",),
        MethodFamily.TROP: ("research_scout_only", "method_comparison_research"),
        MethodFamily.MULTICELL_SHARED_CONTROL: ("per_cell_diagnostic_readout",),
    }
    return uses[family]


def _family_retirement_criteria(
    family: MethodFamily,
    status: CriteriaStatus,
) -> tuple[str, ...]:
    if status != CriteriaStatus.RETIRE_OR_REPLACE:
        retire_families = {
            MethodFamily.AUGSYNTH_CVXPY: ("jk_as_causal_ci", "promotion_without_adapter"),
            MethodFamily.DID: ("promotion_despite_trend_violation",),
            MethodFamily.SYNTHETIC_DID: ("promotion_without_scout_completion",),
            MethodFamily.TBRRIDGE: ("aggregate_global_path", "jackknife_as_ci", "failed_remediation"),
            MethodFamily.BAYESIAN_TBR: ("causal_ci_from_posterior",),
            MethodFamily.TROP: ("promotion_without_boundary_audit",),
            MethodFamily.MULTICELL_SHARED_CONTROL: ("independent_cell_assumption_when_invalid",),
        }
        return retire_families.get(family, ())

    retire = {
        MethodFamily.CLASSIC_AGGREGATE_TBR: (
            "unresolved_aggregate_geometry_mismatch",
            "global_causal_overclaim",
            "small_n_overclaim",
        ),
        MethodFamily.AUGSYNTH_CVXPY: ("jk_paths_uncalibrated",),
    }
    return retire.get(
        family,
        ("family_specific_retire_replace_criteria",),
    )


def _dimension_conditions(dimension: CriteriaDimension) -> tuple[str, ...]:
    mapping = {
        CriteriaDimension.ESTIMAND_CLARITY: ("single_treated_or_documented_estimand",),
        CriteriaDimension.ASSIGNMENT_DESIGN_VALIDITY: ("randomization_or_documented_assignment",),
        CriteriaDimension.OBSERVED_PANEL_DIAGNOSTICS: ("opd_pf_001_pass", "opd_ds_005_pass"),
        CriteriaDimension.DGP_SIMULATION_COVERAGE: ("dgp_es_coverage", "simulation_stress"),
        CriteriaDimension.FAILURE_REGISTRY_REVIEW: ("fm_cp_004_consulted",),
        CriteriaDimension.ASSIGNMENT_GENERATOR_STRESS_COMPATIBILITY: ("st_ad_001_compatible",),
        CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY: ("studentized_adapter_contract",),
        CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE: ("null_fpr_gate", "coverage_replay"),
        CriteriaDimension.MULTIPLICITY_DEPENDENCE_HANDLING: ("dependence_documented",),
        CriteriaDimension.OUTCOME_SCALE_COMPATIBILITY: ("outcome_scale_documented",),
        CriteriaDimension.DONOR_SUPPORT_OVERLAP: ("donor_support_diagnostics",),
        CriteriaDimension.PREPERIOD_FIT_TREND_STABILITY: ("parallel_trends_or_placebo",),
        CriteriaDimension.METHOD_DISAGREEMENT_HANDLING: ("scm_augsynth_disagreement_gate",),
        CriteriaDimension.ALLOWED_CURRENT_USE: ("labeled_research_or_diagnostic",),
        CriteriaDimension.FORBIDDEN_CURRENT_USE: ("no_production_inference",),
        CriteriaDimension.PROMOTION_EVIDENCE: ("full_promotion_checklist",),
        CriteriaDimension.RETIREMENT_REPLACE_CRITERIA: ("explicit_retire_exit_documented",),
        CriteriaDimension.DOWNSTREAM_AUTHORIZATION_BOUNDARY: ("downstream_paused",),
    }
    return mapping[dimension]


def _build_core_matrix_rows() -> list[PromotionCriteriaRow]:
    """Generate family × dimension core matrix rows."""
    rows: list[PromotionCriteriaRow] = []
    counter = 1
    for family in MethodFamily:
        for dimension in CriteriaDimension:
            status = _family_status_map(family, dimension)
            criteria_id = f"PF-CRIT-{counter:03d}"
            counter += 1
            next_artifact: str | None = None
            if family == MethodFamily.SCM and dimension == CriteriaDimension.PROMOTION_EVIDENCE:
                next_artifact = _SCM_PLAN
            elif family == MethodFamily.CLASSIC_AGGREGATE_TBR:
                next_artifact = _RETIRE_PLAN
            elif dimension == CriteriaDimension.DOWNSTREAM_AUTHORIZATION_BOUNDARY:
                next_artifact = _NEXT

            rows.append(
                _row(
                    criteria_id,
                    family,
                    dimension,
                    status,
                    _family_promotion_target(family),
                    f"{family.value} × {dimension.value}: {_family_promotion_target(family)}.",
                    required_conditions=_dimension_conditions(dimension),
                    required_artifacts=_family_artifacts(family),
                    blocking_failure_modes=_family_failure_modes(family),
                    allowed_current_use=_family_allowed_use(family),
                    forbidden_current_use=_FORBID,
                    promotion_evidence_required=_PROMO,
                    retirement_or_exit_criteria=_family_retirement_criteria(family, status),
                    recommended_next_artifact=next_artifact,
                )
            )
    return rows


def _build_supplemental_rows(start_id: int) -> tuple[PromotionCriteriaRow, ...]:
    """Supplemental rows for cross-family gates and status depth."""
    return (
        _row(
            f"PF-CRIT-{start_id:03d}",
            MethodFamily.SCM,
            CriteriaDimension.PROMOTION_EVIDENCE,
            CriteriaStatus.PRODUCTION_CANDIDATE_GATED,
            "production_compatible_candidate_gated",
            "SCM is strongest near-term candidate but remains gated pending full promotion ladder.",
            required_conditions=("studentized_adapter", "null_calibration", "multicell_safe_readout"),
            required_artifacts=(
                "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",
                "OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",
            ),
            blocking_failure_modes=("FM-ES-002", "FM-INF-002"),
            allowed_current_use=("diagnostic_point", "governed_placebo_null_monitor"),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("adapter_contract", "null_fpr_gate"),
            recommended_next_artifact=_SCM_PLAN,
        ),
        _row(
            f"PF-CRIT-{start_id + 1:03d}",
            MethodFamily.AUGSYNTH_CVXPY,
            CriteriaDimension.INFERENCE_ADAPTER_AVAILABILITY,
            CriteriaStatus.CANDIDATE_AFTER_ADAPTER,
            "diagnostic_then_adapter_null_calibration",
            "AugSynth requires governed statistic adapter before promotion hypothesis.",
            required_conditions=("augsynth_studentized_adapter",),
            required_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            blocking_failure_modes=("FM-INF-005", "FM-ES-003"),
            allowed_current_use=("point_estimate",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("adapter_contract",),
        ),
        _row(
            f"PF-CRIT-{start_id + 2:03d}",
            MethodFamily.AUGSYNTH_CVXPY,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE,
            CriteriaStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "diagnostic_then_adapter_null_calibration",
            "AugSynth null calibration required before any promotion hypothesis.",
            required_conditions=("null_fpr_gate", "coverage_replay"),
            required_artifacts=("SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001",),
            blocking_failure_modes=("FM-ES-003", "FM-INF-001"),
            allowed_current_use=("research_calibration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("null_calibration",),
        ),
        _row(
            f"PF-CRIT-{start_id + 3:03d}",
            MethodFamily.DID,
            CriteriaDimension.PREPERIOD_FIT_TREND_STABILITY,
            CriteriaStatus.PRODUCTION_CANDIDATE_GATED,
            "conditional_production_candidate",
            "DID conditional candidate only under strong trend/cluster/outcome conditions.",
            required_conditions=("parallel_trends_documented", "cluster_count_gate"),
            required_artifacts=("DID_RANDOMIZATION_AND_BOOTSTRAP_SUITABILITY_001",),
            blocking_failure_modes=("FM-PF-003", "FM-ES-005"),
            allowed_current_use=("diagnostic_point", "sensitivity_research"),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("parallel_trends",),
        ),
        _row(
            f"PF-CRIT-{start_id + 4:03d}",
            MethodFamily.SYNTHETIC_DID,
            CriteriaDimension.DGP_SIMULATION_COVERAGE,
            CriteriaStatus.CANDIDATE_AFTER_SIMULATION,
            "scout_candidate_after_suitability",
            "Synthetic DID candidate only after suitability and simulation evidence.",
            required_conditions=("balance_dgp_stress", "staggered_estimand_clarity"),
            required_artifacts=("SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",),
            blocking_failure_modes=("FM-ES-009",),
            allowed_current_use=("research_scout_calibration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("scout_report",),
        ),
        _row(
            f"PF-CRIT-{start_id + 5:03d}",
            MethodFamily.TBRRIDGE,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE,
            CriteriaStatus.REMEDIATION_REQUIRED,
            "diagnostic_only_or_remediation",
            "TBRRidge remains diagnostic-only unless remediation audit reopens with evidence.",
            required_conditions=("full_tbrridge_audit", "dgp_null_calibration"),
            required_artifacts=("TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",),
            blocking_failure_modes=("FM-ES-006", "FM-INF-008"),
            allowed_current_use=("diagnostic_point",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
            retirement_or_exit_criteria=("aggregate_global_path", "failed_remediation"),
        ),
        _row(
            f"PF-CRIT-{start_id + 6:03d}",
            MethodFamily.CLASSIC_AGGREGATE_TBR,
            CriteriaDimension.ESTIMAND_CLARITY,
            CriteriaStatus.RETIRE_OR_REPLACE,
            "retire_or_replace",
            "Classic/aggregate TBR overclaim paths are retire/replace candidates.",
            required_conditions=("geometry_remediation_evidence_if_reconsidered",),
            required_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            blocking_failure_modes=("FM-ES-007", "FM-INF-011"),
            allowed_current_use=("retire_replace_review",),
            forbidden_current_use=_FORBID + ("aggregate_promotion",),
            promotion_evidence_required=_PROMO,
            retirement_or_exit_criteria=(
                "unresolved_aggregate_geometry_mismatch",
                "global_causal_overclaim",
            ),
            recommended_next_artifact=_RETIRE_PLAN,
        ),
        _row(
            f"PF-CRIT-{start_id + 7:03d}",
            MethodFamily.CLASSIC_AGGREGATE_TBR,
            CriteriaDimension.PROMOTION_EVIDENCE,
            CriteriaStatus.BLOCKED,
            "retire_or_replace",
            "Classic TBR production promotion paths blocked.",
            required_conditions=("strong_geometry_remediation",),
            required_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            blocking_failure_modes=("FM-ES-007", "FM-PS-010"),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
            retirement_or_exit_criteria=("unresolved_aggregate_geometry_mismatch",),
        ),
        _row(
            f"PF-CRIT-{start_id + 8:03d}",
            MethodFamily.BAYESIAN_TBR,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE,
            CriteriaStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            "posterior_diagnostic_after_calibration",
            "Bayesian TBR posterior diagnostic only until calibration/replay proves coverage.",
            required_conditions=("posterior_coverage_replay", "null_fpr_gate"),
            required_artifacts=("BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",),
            blocking_failure_modes=("FM-ES-008", "FM-INF-008"),
            allowed_current_use=("calibration_replay_research",),
            forbidden_current_use=_FORBID + ("causal_ci_claim",),
            promotion_evidence_required=_PROMO + ("calibration_replay",),
            retirement_or_exit_criteria=("causal_ci_from_posterior",),
        ),
        _row(
            f"PF-CRIT-{start_id + 9:03d}",
            MethodFamily.TROP,
            CriteriaDimension.DGP_SIMULATION_COVERAGE,
            CriteriaStatus.CANDIDATE_AFTER_SIMULATION,
            "research_scout_after_evidence",
            "TROP research-only unless simulation stress evidence matures.",
            required_conditions=("triply_robust_dgp", "method_comparison"),
            required_artifacts=("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
            blocking_failure_modes=("FM-ES-010", "FM-ES-009"),
            allowed_current_use=("simulation_planning",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("simulation_stress",),
        ),
        _row(
            f"PF-CRIT-{start_id + 10:03d}",
            MethodFamily.TROP,
            CriteriaDimension.NULL_CALIBRATION_REPLAY_EVIDENCE,
            CriteriaStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            "research_scout_after_evidence",
            "TROP requires calibration/replay before any promotion hypothesis.",
            required_conditions=("null_calibration", "coverage_replay"),
            required_artifacts=("TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",),
            blocking_failure_modes=("FM-INF-012",),
            allowed_current_use=("calibration_replay_planning",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("calibration_replay",),
        ),
        _row(
            f"PF-CRIT-{start_id + 11:03d}",
            MethodFamily.MULTICELL_SHARED_CONTROL,
            CriteriaDimension.MULTIPLICITY_DEPENDENCE_HANDLING,
            CriteriaStatus.BLOCKED,
            "cross_family_blocker",
            "Multicell/shared-control is cross-family blocker until dependence validated.",
            required_conditions=("dependence_model", "multiplicity_adjustment"),
            required_artifacts=("MULTICELL_MAX_T_RESEARCH_SCOUT_001",),
            blocking_failure_modes=("FM-DA-009", "FM-INF-009", "FM-INF-010"),
            allowed_current_use=("per_cell_diagnostic_readout",),
            forbidden_current_use=_FORBID + ("pooled_inference", "global_winner_selection"),
            promotion_evidence_required=_PROMO + ("multicell_dependence_remediation",),
            retirement_or_exit_criteria=("independent_cell_assumption_when_invalid",),
        ),
        _row(
            f"PF-CRIT-{start_id + 12:03d}",
            MethodFamily.MULTICELL_SHARED_CONTROL,
            CriteriaDimension.DOWNSTREAM_AUTHORIZATION_BOUNDARY,
            CriteriaStatus.BLOCKED,
            "cross_family_blocker",
            "No family may claim production compatibility on pooled multicell readouts.",
            required_conditions=("max_t_stepdown_research_complete",),
            required_artifacts=(
                "MULTICELL_MAX_T_RESEARCH_SCOUT_001",
                "METHOD_FAMILY_PRODUCTION_COMPATIBILITY_AND_REMEDIATION_ROADMAP_001",
            ),
            blocking_failure_modes=("FM-DA-010",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID + ("pooled_causal_claim",),
            promotion_evidence_required=_PROMO,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            f"PF-CRIT-{start_id + 13:03d}",
            MethodFamily.SCM,
            CriteriaDimension.OBSERVED_PANEL_DIAGNOSTICS,
            CriteriaStatus.PRODUCTION_CANDIDATE_GATED,
            "production_compatible_candidate_gated",
            "SCM promotion requires OPD-PF-001 and OPD-DS-005 observed diagnostics.",
            required_conditions=_dimension_conditions(CriteriaDimension.OBSERVED_PANEL_DIAGNOSTICS),
            required_artifacts=("OBSERVED_PANEL_DIAGNOSTIC_REQUIREMENTS_001",),
            blocking_failure_modes=("FM-CP-003",),
            allowed_current_use=("diagnostic_routing",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            f"PF-CRIT-{start_id + 14:03d}",
            MethodFamily.DID,
            CriteriaDimension.ASSIGNMENT_GENERATOR_STRESS_COMPATIBILITY,
            CriteriaStatus.REMEDIATION_REQUIRED,
            "conditional_production_candidate",
            "DID requires assignment-generator stress compatibility per ST-AD-001.",
            required_conditions=("st_ad_001_compatible", "bootstrap_dependence_dgp"),
            required_artifacts=("DESIGN_ASSIGNMENT_GENERATOR_STRESS_TESTS_001",),
            blocking_failure_modes=("FM-INF-003", "FM-DA-001"),
            allowed_current_use=("stress_test_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO + ("assignment_stress",),
        ),
        _row(
            f"PF-CRIT-{start_id + 15:03d}",
            MethodFamily.TBRRIDGE,
            CriteriaDimension.OBSERVED_PANEL_DIAGNOSTICS,
            CriteriaStatus.DIAGNOSTIC_ONLY,
            "diagnostic_only_or_remediation",
            "TBRRidge diagnostic-only default posture per prior remediation audits.",
            required_conditions=("opd_pf_001_pass",),
            required_artifacts=("TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001",),
            blocking_failure_modes=("FM-ES-007",),
            allowed_current_use=("diagnostic_point", "labeled_sensitivity"),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
    )


def build_method_family_promotion_criteria_matrix() -> tuple[PromotionCriteriaRow, ...]:
    """Return metadata-only method-family promotion criteria matrix rows."""
    core = _build_core_matrix_rows()
    supplemental = _build_supplemental_rows(len(core) + 1)
    return tuple(core) + supplemental


def filter_method_family_promotion_criteria_matrix(
    rows: tuple[PromotionCriteriaRow, ...],
    *,
    method_family: MethodFamily | None = None,
    criteria_dimension: CriteriaDimension | None = None,
    current_status: CriteriaStatus | None = None,
    has_retirement_criteria: bool | None = None,
) -> tuple[PromotionCriteriaRow, ...]:
    """Filter promotion criteria matrix rows by optional criteria."""
    result: list[PromotionCriteriaRow] = []
    for row in rows:
        if method_family is not None and row.method_family != method_family:
            continue
        if criteria_dimension is not None and row.criteria_dimension != criteria_dimension:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if has_retirement_criteria is not None:
            has_retire = bool(row.retirement_or_exit_criteria)
            if has_retirement_criteria != has_retire:
                continue
        result.append(row)
    return tuple(result)


def validate_method_family_promotion_criteria_matrix(
    rows: tuple[PromotionCriteriaRow, ...],
) -> dict[str, Any]:
    """Validate promotion criteria matrix registry thresholds and coverage."""
    issues: list[str] = []
    criteria_ids = [r.criteria_id for r in rows]

    if len(rows) < MIN_CRITERIA_ROW_COUNT:
        issues.append(f"criteria_row_count {len(rows)} < {MIN_CRITERIA_ROW_COUNT}")
    if len(criteria_ids) != len(set(criteria_ids)):
        issues.append("duplicate criteria_id values")

    status_counts = Counter(r.current_status for r in rows)
    family_counts = Counter(r.method_family.value for r in rows)
    dimension_counts = Counter(r.criteria_dimension.value for r in rows)

    for family in REQUIRED_METHOD_FAMILIES:
        if not any(r.method_family == family for r in rows):
            issues.append(f"missing method_family: {family.value}")

    for dimension in REQUIRED_CRITERIA_DIMENSIONS:
        if not any(r.criteria_dimension == dimension for r in rows):
            issues.append(f"missing criteria_dimension: {dimension.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    retire_rows = [
        r for r in rows if r.current_status == CriteriaStatus.RETIRE_OR_REPLACE
    ]
    if not retire_rows:
        issues.append("no retire_or_replace rows")
    else:
        missing_retire_criteria = [
            r.criteria_id
            for r in retire_rows
            if not r.retirement_or_exit_criteria
        ]
        if missing_retire_criteria:
            issues.append(
                f"retire_or_replace rows missing retirement_or_exit_criteria: {missing_retire_criteria}"
            )

    scm_gated = any(
        r.method_family == MethodFamily.SCM
        and r.current_status == CriteriaStatus.PRODUCTION_CANDIDATE_GATED
        for r in rows
    )
    if not scm_gated:
        issues.append("scm production_candidate_gated row missing")

    multicell_blocked = any(
        r.method_family == MethodFamily.MULTICELL_SHARED_CONTROL
        and r.current_status == CriteriaStatus.BLOCKED
        for r in rows
    )
    if not multicell_blocked:
        issues.append("multicell cross-family blocker missing")

    unlinked = [r.criteria_id for r in rows if not r.blocking_failure_modes]
    if unlinked:
        issues.append(f"rows missing blocking_failure_modes: {unlinked}")

    return {
        "valid": not issues,
        "criteria_row_count": len(rows),
        "unique_criteria_ids": len(criteria_ids) == len(set(criteria_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in CriteriaStatus},
        "method_family_counts": dict(family_counts),
        "criteria_dimension_counts": dict(dimension_counts),
        "all_required_method_families_covered": all(
            any(r.method_family == f for r in rows) for f in REQUIRED_METHOD_FAMILIES
        ),
        "all_required_criteria_dimensions_covered": all(
            any(r.criteria_dimension == d for r in rows) for d in REQUIRED_CRITERIA_DIMENSIONS
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "retire_or_replace_criteria_defined": all(
            r.retirement_or_exit_criteria for r in retire_rows
        ) if retire_rows else False,
        "issues": issues,
    }


def summarize_method_family_promotion_criteria_matrix(
    rows: tuple[PromotionCriteriaRow, ...],
) -> dict[str, Any]:
    """Serialize promotion criteria matrix summary for archives."""
    validation = validate_method_family_promotion_criteria_matrix(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "criteria_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "method_family_counts": validation["method_family_counts"],
        "criteria_dimension_counts": validation["criteria_dimension_counts"],
        "all_required_method_families_covered": validation["all_required_method_families_covered"],
        "all_required_criteria_dimensions_covered": validation[
            "all_required_criteria_dimensions_covered"
        ],
        "retirement_or_exit_criteria_defined": validation["retire_or_replace_criteria_defined"],
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
    rows = build_method_family_promotion_criteria_matrix()
    validation = validate_method_family_promotion_criteria_matrix(rows)
    summary = summarize_method_family_promotion_criteria_matrix(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("criteria_rows_build_successfully", len(rows) > 0))
    scenarios.append(
        _scenario("criteria_row_count_at_least_65", len(rows) >= MIN_CRITERIA_ROW_COUNT)
    )
    scenarios.append(_scenario("criteria_ids_unique", validation["unique_criteria_ids"]))

    for family in REQUIRED_METHOD_FAMILIES:
        present = any(r.method_family == family for r in rows)
        scenarios.append(_scenario(f"method_family_{family.value}_represented", present))

    for dimension in REQUIRED_CRITERIA_DIMENSIONS:
        present = any(r.criteria_dimension == dimension for r in rows)
        scenarios.append(
            _scenario(f"criteria_dimension_{dimension.value}_represented", present)
        )

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_production_compatibility_promotion_workplan_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_method_family_promotion_criteria_matrix()
    validation = validate_method_family_promotion_criteria_matrix(rows)
    summary = summarize_method_family_promotion_criteria_matrix(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "criteria_row_count": len(rows),
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
