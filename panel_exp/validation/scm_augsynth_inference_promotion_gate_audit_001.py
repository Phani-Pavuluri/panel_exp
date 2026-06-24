"""SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001 validation harness."""

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

_ARTIFACT_ID = "SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "scm_augsynth_inference_promotion_gate_audit_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SCM_AUGSYNTH_INFERENCE_PROMOTION_GATE_AUDIT_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001",
    "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
    "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",
)

MIN_GATE_ROW_COUNT = 55

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

_GATE_FLAGS = {
    "scm_strongest_near_term_candidate": True,
    "scm_production_inference_authorized": False,
    "scm_production_p_value_authorized": False,
    "scm_causal_ci_authorized": False,
    "augsynth_production_inference_authorized": False,
    "augsynth_production_p_value_authorized": False,
    "augsynth_causal_ci_authorized": False,
    "scm_unit_jackknife_requires_calibration": True,
    "scm_placebo_requires_valid_assignment_support": True,
    "treated_set_placebo_requires_adapter_and_null_calibration": True,
    "multi_treated_and_multicell_blocked_without_dependence_handling": True,
    "augsynth_requires_statistic_adapter": True,
    "augsynth_requires_null_calibration": True,
    "augsynth_requires_donor_support_diagnostics": True,
    "scm_augsynth_disagreement_blocks_or_warns": True,
    "observed_diagnostics_required": True,
    "dgp_coverage_required": True,
    "failure_registry_consulted": True,
    "design_assignment_stress_required": True,
    "downstream_work_paused": True,
}


class EstimatorFamily(str, Enum):
    SCM = "scm"
    AUGSYNTH_CVXPY = "augsynth_cvxpy"
    BOTH = "both"


class InferencePath(str, Enum):
    SCM_POINT_ESTIMATE = "scm_point_estimate"
    SCM_UNIT_JACKKNIFE = "scm_unit_jackknife"
    SCM_PLACEBO_RANK = "scm_placebo_rank"
    SCM_STUDENTIZED_PLACEBO_RANK = "scm_studentized_placebo_rank"
    SCM_TREATED_SET_PLACEBO = "scm_treated_set_placebo"
    SCM_MULTI_TREATED = "scm_multi_treated"
    SCM_DONOR_SUPPORT_CONVEX_HULL = "scm_donor_support_convex_hull"
    SCM_PRE_PERIOD_FIT_TREND = "scm_pre_period_fit_trend"
    SCM_SPARSE_COUNT_RATE = "scm_sparse_count_rate"
    SCM_MULTICELL_SHARED_CONTROL = "scm_multicell_shared_control"
    AUGSYNTH_POINT_ESTIMATE = "augsynth_point_estimate"
    AUGSYNTH_JACKKNIFE = "augsynth_jackknife"
    AUGSYNTH_PLACEBO_RANK = "augsynth_placebo_rank"
    AUGSYNTH_STUDENTIZED_ADAPTER = "augsynth_studentized_adapter"
    AUGSYNTH_DONOR_SUPPORT_EXTRAPOLATION = "augsynth_donor_support_extrapolation"
    AUGSYNTH_METHOD_DISAGREEMENT = "augsynth_method_disagreement"
    AUGSYNTH_SCALE_BRIDGE = "augsynth_scale_bridge"
    AUGSYNTH_SPARSE_COUNT_RATE = "augsynth_sparse_count_rate"
    AUGSYNTH_MULTICELL_SHARED_CONTROL = "augsynth_multicell_shared_control"
    SCM_AUGSYNTH_DISAGREEMENT_GATE = "scm_augsynth_disagreement_gate"


class GateStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESTRICTED_RESEARCH = "restricted_research"
    REMEDIATION_REQUIRED = "remediation_required"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    CANDIDATE_AFTER_PROMOTION_GATE = "candidate_after_promotion_gate"
    RETIRE_OR_REPLACE = "retire_or_replace"


REQUIRED_PATHS = frozenset(InferencePath)
REQUIRED_STATUSES = frozenset(GateStatus)


@dataclass(frozen=True)
class PromotionGateRow:
    gate_id: str
    name: str
    estimator_family: EstimatorFamily
    inference_path: InferencePath
    current_status: GateStatus
    required_design_conditions: tuple[str, ...]
    required_observed_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_statistic_adapter: tuple[str, ...]
    required_null_calibration: tuple[str, ...]
    promotion_evidence_required: tuple[str, ...]
    blocking_failure_modes: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    recommended_next_artifact: str | None
    notes: str


def _row(
    gate_id: str,
    name: str,
    estimator_family: EstimatorFamily,
    inference_path: InferencePath,
    current_status: GateStatus,
    notes: str,
    *,
    required_design_conditions: tuple[str, ...],
    required_observed_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_statistic_adapter: tuple[str, ...],
    required_null_calibration: tuple[str, ...],
    promotion_evidence_required: tuple[str, ...],
    blocking_failure_modes: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> PromotionGateRow:
    return PromotionGateRow(
        gate_id=gate_id,
        name=name,
        estimator_family=estimator_family,
        inference_path=inference_path,
        current_status=current_status,
        required_design_conditions=required_design_conditions,
        required_observed_diagnostics=required_observed_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_statistic_adapter=required_statistic_adapter,
        required_null_calibration=required_null_calibration,
        promotion_evidence_required=promotion_evidence_required,
        blocking_failure_modes=blocking_failure_modes,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_PROMO = ("null_calibration", "dgp_coverage", "failure_registry_consult", "observed_diagnostics")
_FORBID = ("production_p_value", "causal_ci", "trustreport", "production_inference")
_NEXT = "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
_SYNTH = "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001"


def build_scm_augsynth_inference_promotion_gate_audit() -> tuple[PromotionGateRow, ...]:
    """Return metadata-only SCM/AugSynth promotion gate audit rows."""
    return (
        # SCM point estimate
        _row(
            "SAG-GATE-001", "scm_point_diagnostic_only", EstimatorFamily.SCM,
            InferencePath.SCM_POINT_ESTIMATE, GateStatus.DIAGNOSTIC_ONLY,
            "SCM point estimate is strongest near-term candidate but diagnostic-only until gates pass.",
            required_design_conditions=("single_treated_or_documented_estimand",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-DS-005"),
            required_dgp_coverage=("DGP-ES-001",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-002",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-011",),
            allowed_current_use=("diagnostic_point_readout",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SAG-GATE-002", "scm_point_production_inference_blocked", EstimatorFamily.SCM,
            InferencePath.SCM_POINT_ESTIMATE, GateStatus.BLOCKED,
            "SCM production inference remains unauthorized.",
            required_design_conditions=("promotion_gate_evidence_complete",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DB-009",),
            required_statistic_adapter=(),
            required_null_calibration=("null_fpr_gate", "coverage_gate"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-011", "FM-DB-009"),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-003", "scm_point_candidate_after_promotion_gate", EstimatorFamily.SCM,
            InferencePath.SCM_POINT_ESTIMATE, GateStatus.CANDIDATE_AFTER_PROMOTION_GATE,
            "SCM may advance to production-compatible candidate lane only after full promotion gate.",
            required_design_conditions=("all_scm_gates_satisfied",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-DS-006"),
            required_dgp_coverage=("DGP-CP-001",),
            required_assignment_stress=("ST-AD-001", "ST-AD-010"),
            required_failure_registry_checks=("FM-CP-004",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO + ("promotion_criteria_matrix",),
            blocking_failure_modes=(),
            allowed_current_use=("labeled_candidate_lane",),
            forbidden_current_use=("unlabeled_production",),
            recommended_next_artifact=_NEXT,
        ),
        # SCM unit jackknife
        _row(
            "SAG-GATE-004", "scm_unit_jackknife_restricted", EstimatorFamily.SCM,
            InferencePath.SCM_UNIT_JACKKNIFE, GateStatus.RESTRICTED_RESEARCH,
            "SCM unit jackknife remains restricted unless null calibrated.",
            required_design_conditions=("single_treated_unit",),
            required_observed_diagnostics=("OPD-IR-005", "OPD-PS-006"),
            required_dgp_coverage=("DGP-INF-007",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-INF-005",),
            required_statistic_adapter=(),
            required_null_calibration=("jackknife_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("restricted_research_jackknife",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-005", "scm_unit_jackknife_requires_calibration", EstimatorFamily.SCM,
            InferencePath.SCM_UNIT_JACKKNIFE, GateStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Unit jackknife requires null calibration before promotion.",
            required_design_conditions=("jackknife_support_documented",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007", "DGP-INF-011"),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-INF-005",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate", "coverage_gate"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("calibration_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SAG-GATE-006", "scm_unit_jackknife_diagnostic_only", EstimatorFamily.SCM,
            InferencePath.SCM_UNIT_JACKKNIFE, GateStatus.DIAGNOSTIC_ONLY,
            "Uncalibrated SCM jackknife is diagnostic-only.",
            required_design_conditions=("single_treated_unit",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-005",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("diagnostic_variance_probe",),
            forbidden_current_use=_FORBID,
        ),
        # SCM placebo rank
        _row(
            "SAG-GATE-007", "scm_placebo_rank_assignment_support", EstimatorFamily.SCM,
            InferencePath.SCM_PLACEBO_RANK, GateStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "SCM placebo rank requires valid assignment support and null calibration.",
            required_design_conditions=("known_assignment_mechanism", "valid_placebo_support"),
            required_observed_diagnostics=("OPD-AD-009", "OPD-AD-010"),
            required_dgp_coverage=("DGP-AD-010", "DGP-INF-011"),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-INF-001", "FM-DA-001"),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("placebo_null_fpr",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001", "FM-DA-002"),
            allowed_current_use=("null_monitor_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-008", "scm_placebo_rank_blocked_invalid_assignment", EstimatorFamily.SCM,
            InferencePath.SCM_PLACEBO_RANK, GateStatus.BLOCKED,
            "Placebo rank blocked when assignment support invalid.",
            required_design_conditions=("valid_placebo_support",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001", "FM-DA-002"),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-009", "scm_placebo_rank_diagnostic_null_monitor", EstimatorFamily.SCM,
            InferencePath.SCM_PLACEBO_RANK, GateStatus.DIAGNOSTIC_ONLY,
            "Single-treated SCM placebo is null-monitor-only per governed semantics.",
            required_design_conditions=("single_treated_unit",),
            required_observed_diagnostics=("OPD-TE-001",),
            required_dgp_coverage=("DGP-TE-001",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-002", "FM-INF-001"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-INF-001",),
            allowed_current_use=("null_monitor_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # SCM studentized placebo
        _row(
            "SAG-GATE-010", "scm_studentized_placebo_adapter_required", EstimatorFamily.SCM,
            InferencePath.SCM_STUDENTIZED_PLACEBO_RANK, GateStatus.CANDIDATE_AFTER_ADAPTER,
            "Studentized placebo requires statistic adapter contract.",
            required_design_conditions=("studentized_adapter_contract",),
            required_observed_diagnostics=("OPD-IR-002", "OPD-AD-009"),
            required_dgp_coverage=("DGP-INF-002",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-INF-002",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("studentized_null_calibration",),
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=("adapter_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SAG-GATE-011", "scm_studentized_placebo_null_calibration", EstimatorFamily.SCM,
            InferencePath.SCM_STUDENTIZED_PLACEBO_RANK, GateStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Studentized placebo requires null calibration after adapter.",
            required_design_conditions=("adapter_implemented",),
            required_observed_diagnostics=("OPD-IR-002",),
            required_dgp_coverage=("DGP-INF-002", "DGP-INF-011"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-002",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate", "coverage_gate"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=("calibration_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-012", "scm_studentized_placebo_blocked_no_adapter", EstimatorFamily.SCM,
            InferencePath.SCM_STUDENTIZED_PLACEBO_RANK, GateStatus.BLOCKED,
            "Studentized placebo blocked without adapter.",
            required_design_conditions=("studentized_adapter_contract",),
            required_observed_diagnostics=("OPD-IR-002",),
            required_dgp_coverage=("DGP-INF-002",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-002",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # SCM treated-set placebo
        _row(
            "SAG-GATE-013", "scm_treated_set_placebo_adapter_null", EstimatorFamily.SCM,
            InferencePath.SCM_TREATED_SET_PLACEBO, GateStatus.CANDIDATE_AFTER_ADAPTER,
            "Treated-set placebo requires adapter before promotion.",
            required_design_conditions=("multi_treated_documented", "treated_set_semantics"),
            required_observed_diagnostics=("OPD-TE-003", "OPD-AD-009"),
            required_dgp_coverage=("DGP-TE-003",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-003",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("treated_set_null_calibration",),
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-TE-003",),
            allowed_current_use=("treated_set_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-014", "scm_treated_set_placebo_null_calibration_gate", EstimatorFamily.SCM,
            InferencePath.SCM_TREATED_SET_PLACEBO, GateStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Treated-set placebo requires null calibration before promotion.",
            required_design_conditions=("adapter_implemented",),
            required_observed_diagnostics=("OPD-TE-003",),
            required_dgp_coverage=("DGP-TE-003", "DGP-INF-011"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-TE-003",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-003",),
            allowed_current_use=("calibration_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-015", "scm_treated_set_placebo_restricted_research", EstimatorFamily.SCM,
            InferencePath.SCM_TREATED_SET_PLACEBO, GateStatus.RESTRICTED_RESEARCH,
            "Treated-set placebo remains restricted research until adapter+calibration complete.",
            required_design_conditions=("multi_treated_documented",),
            required_observed_diagnostics=("OPD-TE-003",),
            required_dgp_coverage=("DGP-TE-003",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-003",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-003",),
            allowed_current_use=("restricted_research",),
            forbidden_current_use=_FORBID,
        ),
        # SCM multi-treated
        _row(
            "SAG-GATE-016", "scm_multi_treated_blocked", EstimatorFamily.SCM,
            InferencePath.SCM_MULTI_TREATED, GateStatus.BLOCKED,
            "SCM multi-treated inference blocked without dependence handling.",
            required_design_conditions=("dependence_model_or_restriction",),
            required_observed_diagnostics=("OPD-TE-004", "OPD-MC-001"),
            required_dgp_coverage=("DGP-TE-004",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-004", "FM-DA-009"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-004",),
            allowed_current_use=("diagnostic_decomposition",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-017", "scm_multi_treated_remediation", EstimatorFamily.SCM,
            InferencePath.SCM_MULTI_TREATED, GateStatus.REMEDIATION_REQUIRED,
            "Multi-treated SCM requires design-aware placebo framework remediation.",
            required_design_conditions=("treated_set_semantics",),
            required_observed_diagnostics=("OPD-TE-004",),
            required_dgp_coverage=("DGP-TE-004",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-004",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("multi_treated_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-004",),
            allowed_current_use=("remediation_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact="MULTITREATED_TREATED_SET_PLACEBO_FRAMEWORK_001",
        ),
        _row(
            "SAG-GATE-018", "scm_multi_treated_simulation_candidate", EstimatorFamily.SCM,
            InferencePath.SCM_MULTI_TREATED, GateStatus.CANDIDATE_AFTER_SIMULATION,
            "Multi-treated promotion candidate only after simulation DGP coverage.",
            required_design_conditions=("multi_treated_estimand_documented",),
            required_observed_diagnostics=("OPD-TE-004",),
            required_dgp_coverage=("DGP-TE-004", "DGP-MC-002"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-TE-004",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-004",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # SCM donor-support / convex hull
        _row(
            "SAG-GATE-019", "scm_donor_support_convex_hull_blocked", EstimatorFamily.SCM,
            InferencePath.SCM_DONOR_SUPPORT_CONVEX_HULL, GateStatus.BLOCKED,
            "Poor donor support or outside convex hull blocks SCM promotion.",
            required_design_conditions=("donor_in_convex_hull", "minimum_donor_support"),
            required_observed_diagnostics=("OPD-DS-006", "OPD-DS-007"),
            required_dgp_coverage=("DGP-DS-006", "DGP-DS-007"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006", "FM-DS-007"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-DS-006", "FM-DS-007"),
            allowed_current_use=("donor_support_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-020", "scm_donor_support_remediation", EstimatorFamily.SCM,
            InferencePath.SCM_DONOR_SUPPORT_CONVEX_HULL, GateStatus.REMEDIATION_REQUIRED,
            "Donor pool remediation required when support is marginal.",
            required_design_conditions=("donor_eligibility_review",),
            required_observed_diagnostics=("OPD-DS-006",),
            required_dgp_coverage=("DGP-DS-006",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-DS-006",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DS-006",),
            allowed_current_use=("donor_pool_remediation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-021", "scm_donor_support_diagnostic", EstimatorFamily.SCM,
            InferencePath.SCM_DONOR_SUPPORT_CONVEX_HULL, GateStatus.DIAGNOSTIC_ONLY,
            "Donor support diagnostics required before any SCM inference path.",
            required_design_conditions=("donor_pool_documented",),
            required_observed_diagnostics=("OPD-DS-005", "OPD-DS-006"),
            required_dgp_coverage=("DGP-DS-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("donor_support_check",),
            forbidden_current_use=_FORBID,
        ),
        # SCM pre-period fit / trend
        _row(
            "SAG-GATE-022", "scm_pre_period_fit_blocked", EstimatorFamily.SCM,
            InferencePath.SCM_PRE_PERIOD_FIT_TREND, GateStatus.BLOCKED,
            "Poor pre-period fit blocks SCM inference promotion.",
            required_design_conditions=("adequate_pre_period",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-PF-003"),
            required_dgp_coverage=("DGP-PF-001", "DGP-PF-003"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-001", "FM-PF-003"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-PF-001", "FM-PF-003"),
            allowed_current_use=("pre_fit_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-023", "scm_pre_period_trend_sensitivity", EstimatorFamily.SCM,
            InferencePath.SCM_PRE_PERIOD_FIT_TREND, GateStatus.DIAGNOSTIC_ONLY,
            "Pre-period trend stress routes SCM to diagnostic-only.",
            required_design_conditions=("pre_period_length_documented",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-PF-002"),
            required_dgp_coverage=("DGP-PF-001",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-001",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-PF-001",),
            allowed_current_use=("trend_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-024", "scm_pre_period_remediation", EstimatorFamily.SCM,
            InferencePath.SCM_PRE_PERIOD_FIT_TREND, GateStatus.REMEDIATION_REQUIRED,
            "Marginal pre-period fit requires remediation or shorter estimand window.",
            required_design_conditions=("estimand_window_review",),
            required_observed_diagnostics=("OPD-PF-003",),
            required_dgp_coverage=("DGP-PF-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-003",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-PF-003",),
            allowed_current_use=("window_remediation",),
            forbidden_current_use=_FORBID,
        ),
        # SCM sparse/count/rate
        _row(
            "SAG-GATE-025", "scm_sparse_count_rate_blocked", EstimatorFamily.SCM,
            InferencePath.SCM_SPARSE_COUNT_RATE, GateStatus.BLOCKED,
            "Sparse/count/rate outcomes block SCM promotion without DGP coverage.",
            required_design_conditions=("outcome_scale_documented",),
            required_observed_diagnostics=("OPD-OM-003", "OPD-OM-004"),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-004"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003", "FM-OM-004"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-OM-003",),
            allowed_current_use=("outcome_scale_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-026", "scm_sparse_count_rate_simulation", EstimatorFamily.SCM,
            InferencePath.SCM_SPARSE_COUNT_RATE, GateStatus.CANDIDATE_AFTER_SIMULATION,
            "Sparse/count/rate SCM paths require simulation DGP before promotion.",
            required_design_conditions=("outcome_transform_documented",),
            required_observed_diagnostics=("OPD-OM-003",),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-005"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("outcome_scale_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-OM-003",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # SCM multicell/shared-control
        _row(
            "SAG-GATE-027", "scm_multicell_blocked", EstimatorFamily.SCM,
            InferencePath.SCM_MULTICELL_SHARED_CONTROL, GateStatus.BLOCKED,
            "SCM multicell/shared-control inference blocked without dependence handling.",
            required_design_conditions=("dependence_model_or_per_cell_restriction",),
            required_observed_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009", "FM-INF-009"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-009", "FM-INF-009"),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID + ("pooled_inference",),
        ),
        _row(
            "SAG-GATE-028", "scm_multicell_restricted_research", EstimatorFamily.SCM,
            InferencePath.SCM_MULTICELL_SHARED_CONTROL, GateStatus.RESTRICTED_RESEARCH,
            "SCM multicell remains research-only until multiplicity scout downstream work.",
            required_design_conditions=("cell_structure_documented",),
            required_observed_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-001", "DGP-MC-002"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("multicell_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-009",),
            allowed_current_use=("multicell_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-029", "scm_multicell_candidate_after_simulation", EstimatorFamily.SCM,
            InferencePath.SCM_MULTICELL_SHARED_CONTROL, GateStatus.CANDIDATE_AFTER_SIMULATION,
            "SCM multicell promotion candidate only after shared-control simulation.",
            required_design_conditions=("dependence_structure_documented",),
            required_observed_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002", "DGP-MC-003"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-009",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-009",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        # AugSynth point estimate
        _row(
            "SAG-GATE-030", "augsynth_point_diagnostic", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_POINT_ESTIMATE, GateStatus.DIAGNOSTIC_ONLY,
            "AugSynth point estimates may remain diagnostic/restricted research.",
            required_design_conditions=("augmentation_documented",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-DS-005"),
            required_dgp_coverage=("DGP-ES-003",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-003",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-ES-003",),
            allowed_current_use=("diagnostic_point_readout",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-031", "augsynth_point_production_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_POINT_ESTIMATE, GateStatus.BLOCKED,
            "AugSynth production inference remains unauthorized.",
            required_design_conditions=("promotion_gate_evidence_complete",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_statistic_adapter=(),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-011",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-032", "augsynth_point_restricted_research", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_POINT_ESTIMATE, GateStatus.RESTRICTED_RESEARCH,
            "AugSynth point without calibrated inference is restricted research.",
            required_design_conditions=("augmentation_stability_check",),
            required_observed_diagnostics=("OPD-ES-004",),
            required_dgp_coverage=("DGP-ES-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-004",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-ES-004",),
            allowed_current_use=("restricted_research",),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth jackknife
        _row(
            "SAG-GATE-033", "augsynth_jackknife_retire_or_replace", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_JACKKNIFE, GateStatus.RETIRE_OR_REPLACE,
            "AugSynth jackknife paths are retire/replace candidates unless adapter proves viability.",
            required_design_conditions=("jackknife_viability_documented",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-005",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("jackknife_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("retire_replace_review",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-034", "augsynth_jackknife_candidate_after_adapter", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_JACKKNIFE, GateStatus.CANDIDATE_AFTER_ADAPTER,
            "AugSynth jackknife requires statistic adapter before any promotion.",
            required_design_conditions=("adapter_contract_satisfied",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-005",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("jackknife_null_calibration",),
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("adapter_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-035", "augsynth_jackknife_diagnostic_only", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_JACKKNIFE, GateStatus.DIAGNOSTIC_ONLY,
            "Uncalibrated AugSynth jackknife is diagnostic-only.",
            required_design_conditions=("single_treated_or_documented",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-005",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("diagnostic_variance_probe",),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth placebo/rank
        _row(
            "SAG-GATE-036", "augsynth_placebo_rank_adapter_required", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_PLACEBO_RANK, GateStatus.CANDIDATE_AFTER_ADAPTER,
            "AugSynth placebo/rank requires statistic adapter.",
            required_design_conditions=("valid_placebo_support",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-INF-001",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("placebo_null_fpr",),
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-INF-001",),
            allowed_current_use=("placebo_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-037", "augsynth_placebo_rank_null_calibration", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_PLACEBO_RANK, GateStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "AugSynth placebo requires null calibration after adapter.",
            required_design_conditions=("adapter_implemented",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-INF-011",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-001",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-001",),
            allowed_current_use=("calibration_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-038", "augsynth_placebo_rank_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_PLACEBO_RANK, GateStatus.BLOCKED,
            "AugSynth placebo blocked without assignment support and adapter.",
            required_design_conditions=("known_assignment_mechanism",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001", "FM-INF-001"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth studentized adapter
        _row(
            "SAG-GATE-039", "augsynth_studentized_adapter_gate", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_STUDENTIZED_ADAPTER, GateStatus.CANDIDATE_AFTER_ADAPTER,
            "AugSynth studentized path requires governed statistic adapter.",
            required_design_conditions=("studentized_adapter_contract",),
            required_observed_diagnostics=("OPD-IR-002",),
            required_dgp_coverage=("DGP-INF-002",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-INF-002",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("studentized_null_calibration",),
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=("adapter_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-040", "augsynth_studentized_null_calibration", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_STUDENTIZED_ADAPTER, GateStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "AugSynth studentized requires null calibration.",
            required_design_conditions=("adapter_implemented",),
            required_observed_diagnostics=("OPD-IR-002",),
            required_dgp_coverage=("DGP-INF-002", "DGP-INF-011"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-002",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate", "coverage_gate"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=("calibration_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-041", "augsynth_studentized_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_STUDENTIZED_ADAPTER, GateStatus.BLOCKED,
            "AugSynth studentized blocked without adapter contract.",
            required_design_conditions=("studentized_adapter_contract",),
            required_observed_diagnostics=("OPD-IR-002",),
            required_dgp_coverage=("DGP-INF-002",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-002",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth donor-support / extrapolation
        _row(
            "SAG-GATE-042", "augsynth_donor_extrapolation_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_DONOR_SUPPORT_EXTRAPOLATION, GateStatus.BLOCKED,
            "AugSynth extrapolation/donor-support issues are promotion blockers.",
            required_design_conditions=("donor_in_support_set", "no_extrapolation"),
            required_observed_diagnostics=("OPD-DS-006", "OPD-DS-007"),
            required_dgp_coverage=("DGP-DS-006", "DGP-DS-007"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006", "FM-DS-007"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-DS-006", "FM-DS-007"),
            allowed_current_use=("extrapolation_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-043", "augsynth_donor_support_remediation", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_DONOR_SUPPORT_EXTRAPOLATION, GateStatus.REMEDIATION_REQUIRED,
            "Marginal donor support requires remediation before AugSynth promotion.",
            required_design_conditions=("donor_pool_review",),
            required_observed_diagnostics=("OPD-DS-006",),
            required_dgp_coverage=("DGP-DS-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DS-006",),
            allowed_current_use=("donor_remediation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-044", "augsynth_donor_support_diagnostic", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_DONOR_SUPPORT_EXTRAPOLATION, GateStatus.DIAGNOSTIC_ONLY,
            "Donor-support diagnostics required for all AugSynth paths.",
            required_design_conditions=("donor_pool_documented",),
            required_observed_diagnostics=("OPD-DS-005", "OPD-DS-006"),
            required_dgp_coverage=("DGP-DS-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("donor_support_check",),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth method-disagreement
        _row(
            "SAG-GATE-045", "augsynth_method_disagreement_warning", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_METHOD_DISAGREEMENT, GateStatus.DIAGNOSTIC_ONLY,
            "AugSynth method-disagreement triggers diagnostic warning.",
            required_design_conditions=("both_estimators_run",),
            required_observed_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-005",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("disagreement_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("disagreement_diagnostic",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact="SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001",
        ),
        _row(
            "SAG-GATE-046", "augsynth_method_disagreement_blocks_promotion", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_METHOD_DISAGREEMENT, GateStatus.BLOCKED,
            "Large SCM/AugSynth disagreement blocks promotion.",
            required_design_conditions=("disagreement_threshold_defined",),
            required_observed_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-005",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("disagreement_resolution",),
            blocking_failure_modes=("FM-ES-005",),
            allowed_current_use=("disagreement_investigation",),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth scale bridge
        _row(
            "SAG-GATE-047", "augsynth_scale_bridge_remediation", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_SCALE_BRIDGE, GateStatus.REMEDIATION_REQUIRED,
            "Scale-bridge stress requires remediation before AugSynth promotion.",
            required_design_conditions=("scale_bridge_documented",),
            required_observed_diagnostics=("OPD-OM-006",),
            required_dgp_coverage=("DGP-OM-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-006",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("scale_bridge_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-OM-006",),
            allowed_current_use=("scale_bridge_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-048", "augsynth_scale_bridge_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_SCALE_BRIDGE, GateStatus.BLOCKED,
            "Unresolved scale bridge blocks AugSynth inference promotion.",
            required_design_conditions=("comparable_outcome_scales",),
            required_observed_diagnostics=("OPD-OM-006",),
            required_dgp_coverage=("DGP-OM-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-006",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-OM-006",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth sparse/count/rate
        _row(
            "SAG-GATE-049", "augsynth_sparse_count_rate_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_SPARSE_COUNT_RATE, GateStatus.BLOCKED,
            "Sparse/count/rate outcomes block AugSynth without DGP coverage.",
            required_design_conditions=("outcome_scale_documented",),
            required_observed_diagnostics=("OPD-OM-003", "OPD-OM-004"),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-004"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-OM-003",),
            allowed_current_use=("outcome_scale_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-050", "augsynth_sparse_count_rate_simulation", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_SPARSE_COUNT_RATE, GateStatus.CANDIDATE_AFTER_SIMULATION,
            "AugSynth sparse/count/rate requires simulation before promotion.",
            required_design_conditions=("outcome_transform_documented",),
            required_observed_diagnostics=("OPD-OM-003",),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-005"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("outcome_scale_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-OM-003",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # AugSynth multicell
        _row(
            "SAG-GATE-051", "augsynth_multicell_blocked", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_MULTICELL_SHARED_CONTROL, GateStatus.BLOCKED,
            "AugSynth multicell blocked without dependence/multiplicity handling.",
            required_design_conditions=("dependence_model_or_per_cell_restriction",),
            required_observed_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009", "FM-INF-009"),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-009",),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID + ("pooled_inference",),
        ),
        _row(
            "SAG-GATE-052", "augsynth_multicell_restricted_research", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_MULTICELL_SHARED_CONTROL, GateStatus.RESTRICTED_RESEARCH,
            "AugSynth multicell remains research-only.",
            required_design_conditions=("cell_structure_documented",),
            required_observed_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-001",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("multicell_null_calibration",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-009",),
            allowed_current_use=("multicell_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-053", "augsynth_multicell_candidate_after_simulation", EstimatorFamily.AUGSYNTH_CVXPY,
            InferencePath.AUGSYNTH_MULTICELL_SHARED_CONTROL, GateStatus.CANDIDATE_AFTER_SIMULATION,
            "AugSynth multicell candidate only after shared-control simulation.",
            required_design_conditions=("dependence_structure_documented",),
            required_observed_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002", "DGP-MC-003"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-009",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("null_fpr_gate",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-009",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # SCM vs AugSynth disagreement gate
        _row(
            "SAG-GATE-054", "scm_augsynth_disagreement_gate_warn", EstimatorFamily.BOTH,
            InferencePath.SCM_AUGSYNTH_DISAGREEMENT_GATE, GateStatus.DIAGNOSTIC_ONLY,
            "SCM/AugSynth disagreement must trigger diagnostic warning.",
            required_design_conditions=("both_estimators_comparable",),
            required_observed_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-005",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("disagreement_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("disagreement_warning",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact="SCM_AUGSYNTH_DISAGREEMENT_DIAGNOSTICS_001",
        ),
        _row(
            "SAG-GATE-055", "scm_augsynth_disagreement_gate_block", EstimatorFamily.BOTH,
            InferencePath.SCM_AUGSYNTH_DISAGREEMENT_GATE, GateStatus.BLOCKED,
            "SCM/AugSynth disagreement blocks promotion when threshold exceeded.",
            required_design_conditions=("disagreement_threshold_defined",),
            required_observed_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-005",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("disagreement_resolution",),
            blocking_failure_modes=("FM-ES-005",),
            allowed_current_use=("disagreement_investigation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-056", "scm_augsynth_disagreement_candidate_after_gate", EstimatorFamily.BOTH,
            InferencePath.SCM_AUGSYNTH_DISAGREEMENT_GATE, GateStatus.CANDIDATE_AFTER_PROMOTION_GATE,
            "Promotion proceeds only when disagreement gate satisfied.",
            required_design_conditions=("disagreement_resolved_or_within_tolerance",),
            required_observed_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-005",),
            required_statistic_adapter=("SCM_AUGSYNTH_STATISTIC_ADAPTER_CONTRACT_001",),
            required_null_calibration=("disagreement_null_calibration",),
            promotion_evidence_required=_PROMO + ("disagreement_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("labeled_candidate_lane",),
            forbidden_current_use=("unlabeled_production",),
            recommended_next_artifact=_NEXT,
        ),
        # Cross-cutting control gates
        _row(
            "SAG-GATE-057", "observed_diagnostics_global_gate", EstimatorFamily.BOTH,
            InferencePath.SCM_POINT_ESTIMATE, GateStatus.REMEDIATION_REQUIRED,
            "Observed-panel diagnostics required before SCM/AugSynth method selection.",
            required_design_conditions=("panel_structure_documented",),
            required_observed_diagnostics=("OPD-PS-001", "OPD-PF-001", "OPD-DS-005"),
            required_dgp_coverage=("DGP-CP-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-003",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-CP-003",),
            allowed_current_use=("diagnostic_routing",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-058", "dgp_coverage_global_gate", EstimatorFamily.BOTH,
            InferencePath.AUGSYNTH_POINT_ESTIMATE, GateStatus.REMEDIATION_REQUIRED,
            "Simulation DGP coverage required before inference promotion.",
            required_design_conditions=("dgp_coverage_plan_satisfied",),
            required_observed_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-CP-002",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-002",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-CP-002",),
            allowed_current_use=("dgp_planning",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_SYNTH,
        ),
        _row(
            "SAG-GATE-059", "failure_registry_global_gate", EstimatorFamily.BOTH,
            InferencePath.SCM_PLACEBO_RANK, GateStatus.REMEDIATION_REQUIRED,
            "Failure registry consultation required for all promotion paths.",
            required_design_conditions=("failure_registry_consulted",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-CP-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-004",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=("failure_registry_consult",),
            blocking_failure_modes=("FM-CP-004",),
            allowed_current_use=("registry_consultation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SAG-GATE-060", "design_assignment_stress_global_gate", EstimatorFamily.BOTH,
            InferencePath.SCM_PLACEBO_RANK, GateStatus.REMEDIATION_REQUIRED,
            "Design assignment stress tests required for placebo/randomization paths.",
            required_design_conditions=("assignment_mechanism_documented",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-DA-001",),
            required_statistic_adapter=(),
            required_null_calibration=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001",),
            allowed_current_use=("stress_test_research",),
            forbidden_current_use=_FORBID,
        ),
    )


def filter_scm_augsynth_inference_promotion_gate_audit(
    rows: tuple[PromotionGateRow, ...],
    *,
    inference_path: InferencePath | None = None,
    current_status: GateStatus | None = None,
    estimator_family: EstimatorFamily | None = None,
) -> tuple[PromotionGateRow, ...]:
    """Filter promotion gate rows by optional criteria."""
    result: list[PromotionGateRow] = []
    for row in rows:
        if inference_path is not None and row.inference_path != inference_path:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if estimator_family is not None and row.estimator_family != estimator_family:
            continue
        result.append(row)
    return tuple(result)


def validate_scm_augsynth_inference_promotion_gate_audit(
    rows: tuple[PromotionGateRow, ...],
) -> dict[str, Any]:
    """Validate promotion gate registry thresholds and coverage."""
    issues: list[str] = []
    gate_ids = [r.gate_id for r in rows]

    if len(rows) < MIN_GATE_ROW_COUNT:
        issues.append(f"gate_row_count {len(rows)} < {MIN_GATE_ROW_COUNT}")
    if len(gate_ids) != len(set(gate_ids)):
        issues.append("duplicate gate_id values")

    status_counts = Counter(r.current_status for r in rows)
    family_counts = Counter(r.estimator_family.value for r in rows)
    path_counts = Counter(r.inference_path.value for r in rows)

    for path in REQUIRED_PATHS:
        if not any(r.inference_path == path for r in rows):
            issues.append(f"missing inference path: {path.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    blocked_scm_prod = any(
        r.inference_path == InferencePath.SCM_POINT_ESTIMATE
        and r.current_status == GateStatus.BLOCKED
        and "production" in r.notes.lower()
        for r in rows
    )
    if not blocked_scm_prod:
        issues.append("SCM production inference blocker missing")

    unlinked_fm = [r.gate_id for r in rows if not r.required_failure_registry_checks]
    if unlinked_fm:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked_fm}")

    return {
        "valid": not issues,
        "gate_row_count": len(rows),
        "unique_gate_ids": len(gate_ids) == len(set(gate_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in GateStatus},
        "estimator_family_counts": dict(family_counts),
        "inference_path_counts": dict(path_counts),
        "all_required_paths_covered": all(
            any(r.inference_path == p for r in rows) for p in REQUIRED_PATHS
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "issues": issues,
    }


def summarize_scm_augsynth_inference_promotion_gate_audit(
    rows: tuple[PromotionGateRow, ...],
) -> dict[str, Any]:
    """Serialize SCM/AugSynth promotion gate summary for archives."""
    validation = validate_scm_augsynth_inference_promotion_gate_audit(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "gate_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "estimator_family_counts": validation["estimator_family_counts"],
        "inference_path_counts": validation["inference_path_counts"],
        "all_required_paths_covered": validation["all_required_paths_covered"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_GATE_FLAGS,
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
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    validation = validate_scm_augsynth_inference_promotion_gate_audit(rows)
    summary = summarize_scm_augsynth_inference_promotion_gate_audit(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("gate_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("gate_row_count_at_least_55", len(rows) >= MIN_GATE_ROW_COUNT))
    scenarios.append(_scenario("gate_ids_unique", validation["unique_gate_ids"]))

    for path in REQUIRED_PATHS:
        present = any(r.inference_path == path for r in rows)
        scenarios.append(_scenario(f"inference_path_{path.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for flag, expected in _GATE_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_synthetic_did_method_scout_and_suitability_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_scm_augsynth_inference_promotion_gate_audit()
    validation = validate_scm_augsynth_inference_promotion_gate_audit(rows)
    summary = summarize_scm_augsynth_inference_promotion_gate_audit(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "gate_row_count": len(rows),
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
