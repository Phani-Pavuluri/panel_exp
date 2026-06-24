"""SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001 validation harness."""

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

_ARTIFACT_ID = "SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "synthetic_did_method_scout_and_suitability_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/SYNTHETIC_DID_METHOD_SCOUT_AND_SUITABILITY_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001",
    "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",
    "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",
)

MIN_SCOUT_ROW_COUNT = 50

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

_SCOUT_FLAGS = {
    "synthetic_did_research_scout_candidate": True,
    "synthetic_did_implementation_candidate_only_after_suitability": True,
    "synthetic_did_production_inference_authorized": False,
    "synthetic_did_production_p_value_authorized": False,
    "synthetic_did_causal_ci_authorized": False,
    "future_adapter_required": True,
    "future_null_calibration_required": True,
    "observed_diagnostics_required": True,
    "dgp_coverage_required": True,
    "design_assignment_stress_required": True,
    "failure_registry_consulted": True,
    "multicell_shared_control_blocked_without_dependence_handling": True,
    "comparison_against_scm_required": True,
    "comparison_against_augsynth_required": True,
    "comparison_against_did_required": True,
    "comparison_against_tbrridge_required": True,
    "downstream_work_paused": True,
}


class SyntheticDidComponent(str, Enum):
    POINT_ESTIMATE = "point_estimate"
    UNIT_WEIGHTS = "unit_weights"
    TIME_WEIGHTS = "time_weights"
    REGULARIZATION = "regularization"
    BALANCED_PANEL = "balanced_panel"
    MISSING_DATA = "missing_data"
    DONOR_SUPPORT_OVERLAP = "donor_support_overlap"
    PRE_PERIOD_FIT_TREND = "pre_period_fit_trend"
    SPARSE_COUNT_RATE = "sparse_count_rate"
    PLACEBO_RANK = "placebo_rank"
    BOOTSTRAP = "bootstrap"
    JACKKNIFE = "jackknife"
    RANDOMIZATION_PERMUTATION = "randomization_permutation"
    DETERMINISTIC_UNKNOWN_ASSIGNMENT = "deterministic_unknown_assignment"
    MULTI_TREATED = "multi_treated"
    MULTICELL_SHARED_CONTROL = "multicell_shared_control"
    VS_SCM = "vs_scm"
    VS_DID = "vs_did"
    VS_AUGSYNTH = "vs_augsynth"
    VS_TBRRIDGE = "vs_tbrridge"


class ScoutStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    METHOD_SCOUT_CANDIDATE = "method_scout_candidate"
    IMPLEMENTATION_CANDIDATE = "implementation_candidate"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    CANDIDATE_AFTER_ADAPTER = "candidate_after_adapter"
    CANDIDATE_AFTER_NULL_CALIBRATION = "candidate_after_null_calibration"
    REMEDIATION_REQUIRED = "remediation_required"
    RETIRE_OR_REPLACE = "retire_or_replace"


REQUIRED_COMPONENTS = frozenset(SyntheticDidComponent)
REQUIRED_STATUSES = frozenset(ScoutStatus)


@dataclass(frozen=True)
class SyntheticDidScoutRow:
    scout_id: str
    name: str
    synthetic_did_component: SyntheticDidComponent
    current_status: ScoutStatus
    required_design_conditions: tuple[str, ...]
    required_observed_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_inference_adapter: tuple[str, ...]
    required_null_calibration: tuple[str, ...]
    comparison_methods: tuple[str, ...]
    promotion_evidence_required: tuple[str, ...]
    blocking_failure_modes: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    recommended_next_artifact: str | None
    notes: str


def _row(
    scout_id: str,
    name: str,
    component: SyntheticDidComponent,
    current_status: ScoutStatus,
    notes: str,
    *,
    required_design_conditions: tuple[str, ...],
    required_observed_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_inference_adapter: tuple[str, ...],
    required_null_calibration: tuple[str, ...],
    comparison_methods: tuple[str, ...],
    promotion_evidence_required: tuple[str, ...],
    blocking_failure_modes: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> SyntheticDidScoutRow:
    return SyntheticDidScoutRow(
        scout_id=scout_id,
        name=name,
        synthetic_did_component=component,
        current_status=current_status,
        required_design_conditions=required_design_conditions,
        required_observed_diagnostics=required_observed_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_inference_adapter=required_inference_adapter,
        required_null_calibration=required_null_calibration,
        comparison_methods=comparison_methods,
        promotion_evidence_required=promotion_evidence_required,
        blocking_failure_modes=blocking_failure_modes,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_PROMO = ("null_calibration", "dgp_coverage", "failure_registry_consult", "observed_diagnostics")
_FORBID = ("production_p_value", "causal_ci", "trustreport", "production_inference")
_CMP_ALL = ("scm", "augsynth", "did", "tbrridge")
_NEXT = "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
_BAYES = "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001"


def build_synthetic_did_method_scout_suitability() -> tuple[SyntheticDidScoutRow, ...]:
    """Return metadata-only Synthetic DID scout/suitability rows."""
    return (
        # Point estimate
        _row(
            "SDID-SCT-001", "sdid_point_method_scout", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.METHOD_SCOUT_CANDIDATE,
            "Synthetic DID point estimate is research/scout candidate, not production-ready.",
            required_design_conditions=("treated_control_panel", "pre_post_structure"),
            required_observed_diagnostics=("OPD-PF-001", "OPD-DS-005"),
            required_dgp_coverage=("DGP-ES-009",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-009",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-CP-005",),
            allowed_current_use=("method_scout_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SDID-SCT-002", "sdid_point_production_blocked", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.BLOCKED,
            "Synthetic DID production inference remains unauthorized.",
            required_design_conditions=("promotion_evidence_complete",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_inference_adapter=(),
            required_null_calibration=("null_fpr_gate",),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-011", "FM-DB-009"),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-003", "sdid_point_diagnostic_only", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.DIAGNOSTIC_ONLY,
            "Uncalibrated SDID point may support diagnostic readout only.",
            required_design_conditions=("panel_balance_documented",),
            required_observed_diagnostics=("OPD-PF-001",),
            required_dgp_coverage=("DGP-ES-009",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-009",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "did"),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("diagnostic_point_readout",),
            forbidden_current_use=_FORBID,
        ),
        # Unit weights
        _row(
            "SDID-SCT-004", "sdid_unit_weights_research", SyntheticDidComponent.UNIT_WEIGHTS,
            ScoutStatus.RESEARCH_ONLY,
            "Unit weight estimation requires research validation before implementation.",
            required_design_conditions=("donor_pool_sufficient",),
            required_observed_diagnostics=("OPD-DS-006",),
            required_dgp_coverage=("DGP-DS-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "augsynth"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DS-006",),
            allowed_current_use=("weight_diagnostics",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-005", "sdid_unit_weights_implementation_candidate", SyntheticDidComponent.UNIT_WEIGHTS,
            ScoutStatus.IMPLEMENTATION_CANDIDATE,
            "Unit weights may be worth implementing after suitability evidence.",
            required_design_conditions=("weight_stability_documented",),
            required_observed_diagnostics=("OPD-DS-005", "OPD-DS-006"),
            required_dgp_coverage=("DGP-ES-009", "DGP-DS-006"),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-009",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=(),
            comparison_methods=("scm", "augsynth"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("implementation_scout",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SDID-SCT-006", "sdid_unit_weights_degenerate_blocked", SyntheticDidComponent.UNIT_WEIGHTS,
            ScoutStatus.BLOCKED,
            "Degenerate unit weights block SDID promotion.",
            required_design_conditions=("non_degenerate_weights",),
            required_observed_diagnostics=("OPD-DS-007",),
            required_dgp_coverage=("DGP-DS-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-007",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm",),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-DS-007",),
            allowed_current_use=("degeneracy_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # Time weights
        _row(
            "SDID-SCT-007", "sdid_time_weights_research", SyntheticDidComponent.TIME_WEIGHTS,
            ScoutStatus.RESEARCH_ONLY,
            "Time weight paths require research before implementation.",
            required_design_conditions=("pre_post_length_adequate",),
            required_observed_diagnostics=("OPD-PF-002",),
            required_dgp_coverage=("DGP-PF-002",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-001",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-PF-001",),
            allowed_current_use=("time_weight_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-008", "sdid_time_weights_staggered_remediation", SyntheticDidComponent.TIME_WEIGHTS,
            ScoutStatus.REMEDIATION_REQUIRED,
            "Staggered timing requires explicit estimand remediation for time weights.",
            required_design_conditions=("staggered_estimand_documented",),
            required_observed_diagnostics=("OPD-TE-004",),
            required_dgp_coverage=("DGP-TE-004",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-004",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-004",),
            allowed_current_use=("staggered_remediation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-009", "sdid_time_weights_implementation_candidate", SyntheticDidComponent.TIME_WEIGHTS,
            ScoutStatus.IMPLEMENTATION_CANDIDATE,
            "Time weights implementation candidate after panel diagnostics pass.",
            required_design_conditions=("balanced_pre_post",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-PF-002"),
            required_dgp_coverage=("DGP-PF-001",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-PF-001",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=(),
            comparison_methods=("did", "scm"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("implementation_scout",),
            forbidden_current_use=_FORBID,
        ),
        # Regularization
        _row(
            "SDID-SCT-010", "sdid_regularization_ridge_research", SyntheticDidComponent.REGULARIZATION,
            ScoutStatus.RESEARCH_ONLY,
            "Ridge-style regularization requires simulation evidence.",
            required_design_conditions=("regularization_lambda_documented",),
            required_observed_diagnostics=("OPD-ES-004",),
            required_dgp_coverage=("DGP-ES-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("tbrridge", "augsynth"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-ES-006",),
            allowed_current_use=("regularization_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-011", "sdid_regularization_simulation_candidate", SyntheticDidComponent.REGULARIZATION,
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Regularization tuning requires DGP simulation before promotion.",
            required_design_conditions=("lambda_selection_protocol",),
            required_observed_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-ES-009", "DGP-CP-002"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("regularization_null_calibration",),
            comparison_methods=("tbrridge",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-012", "sdid_regularization_overfit_blocked", SyntheticDidComponent.REGULARIZATION,
            ScoutStatus.BLOCKED,
            "Over-regularization masking instability blocks promotion.",
            required_design_conditions=("stability_diagnostics_pass",),
            required_observed_diagnostics=("OPD-ES-004",),
            required_dgp_coverage=("DGP-ES-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("tbrridge",),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-ES-006",),
            allowed_current_use=("instability_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # Balanced panel
        _row(
            "SDID-SCT-013", "sdid_balanced_panel_required", SyntheticDidComponent.BALANCED_PANEL,
            ScoutStatus.REMEDIATION_REQUIRED,
            "Unbalanced panels require remediation or explicit missing-data protocol.",
            required_design_conditions=("balanced_panel_or_imputation_protocol",),
            required_observed_diagnostics=("OPD-PS-004",),
            required_dgp_coverage=("DGP-PS-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PS-004",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-PS-004",),
            allowed_current_use=("balance_remediation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-014", "sdid_balanced_panel_diagnostic", SyntheticDidComponent.BALANCED_PANEL,
            ScoutStatus.DIAGNOSTIC_ONLY,
            "Panel balance diagnostics required before SDID method selection.",
            required_design_conditions=("panel_structure_documented",),
            required_observed_diagnostics=("OPD-PS-001", "OPD-PS-004"),
            required_dgp_coverage=("DGP-PS-001",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PS-004",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=(),
            allowed_current_use=("balance_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # Missing data
        _row(
            "SDID-SCT-015", "sdid_missing_data_sensitivity", SyntheticDidComponent.MISSING_DATA,
            ScoutStatus.RESEARCH_ONLY,
            "Missing-data sensitivity requires research DGP coverage.",
            required_design_conditions=("missingness_mechanism_documented",),
            required_observed_diagnostics=("OPD-PS-005",),
            required_dgp_coverage=("DGP-PS-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PS-005",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "did"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-PS-005",),
            allowed_current_use=("missingness_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-016", "sdid_missing_data_blocked", SyntheticDidComponent.MISSING_DATA,
            ScoutStatus.BLOCKED,
            "High missingness blocks SDID without imputation protocol.",
            required_design_conditions=("missingness_below_threshold",),
            required_observed_diagnostics=("OPD-PS-005",),
            required_dgp_coverage=("DGP-PS-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PS-005",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=(),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-PS-005",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # Donor support / overlap
        _row(
            "SDID-SCT-017", "sdid_donor_overlap_stress", SyntheticDidComponent.DONOR_SUPPORT_OVERLAP,
            ScoutStatus.BLOCKED,
            "Poor donor overlap blocks SDID promotion.",
            required_design_conditions=("donor_overlap_adequate",),
            required_observed_diagnostics=("OPD-DS-006", "OPD-DS-005"),
            required_dgp_coverage=("DGP-DS-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DS-006",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "augsynth"),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-DS-006",),
            allowed_current_use=("overlap_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-018", "sdid_donor_overlap_simulation", SyntheticDidComponent.DONOR_SUPPORT_OVERLAP,
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Donor overlap stress requires simulation before implementation.",
            required_design_conditions=("overlap_metrics_defined",),
            required_observed_diagnostics=("OPD-DS-006",),
            required_dgp_coverage=("DGP-DS-006", "DGP-ES-009"),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-DS-006",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=(),
            comparison_methods=("scm",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # Pre-period fit / trend
        _row(
            "SDID-SCT-019", "sdid_pre_period_fit_blocked", SyntheticDidComponent.PRE_PERIOD_FIT_TREND,
            ScoutStatus.BLOCKED,
            "Poor pre-period fit blocks SDID inference promotion.",
            required_design_conditions=("adequate_pre_period_fit",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-PF-003"),
            required_dgp_coverage=("DGP-PF-001", "DGP-PF-003"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-001", "FM-PF-003"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "did"),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-PF-003",),
            allowed_current_use=("pre_fit_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-020", "sdid_pre_period_trend_research", SyntheticDidComponent.PRE_PERIOD_FIT_TREND,
            ScoutStatus.RESEARCH_ONLY,
            "Pre-period trend stress remains research-only for SDID.",
            required_design_conditions=("parallel_trend_assessment",),
            required_observed_diagnostics=("OPD-PF-003",),
            required_dgp_coverage=("DGP-PF-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-003", "FM-ES-005"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-ES-005",),
            allowed_current_use=("trend_research",),
            forbidden_current_use=_FORBID,
        ),
        # Sparse/count/rate
        _row(
            "SDID-SCT-021", "sdid_sparse_count_rate_blocked", SyntheticDidComponent.SPARSE_COUNT_RATE,
            ScoutStatus.BLOCKED,
            "Sparse/count/rate outcomes block SDID without DGP coverage.",
            required_design_conditions=("outcome_scale_documented",),
            required_observed_diagnostics=("OPD-OM-003", "OPD-OM-004"),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-004"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "augsynth"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-OM-003",),
            allowed_current_use=("outcome_scale_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-022", "sdid_sparse_count_rate_simulation", SyntheticDidComponent.SPARSE_COUNT_RATE,
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Outcome-scale SDID requires simulation DGP before promotion.",
            required_design_conditions=("outcome_transform_documented",),
            required_observed_diagnostics=("OPD-OM-003",),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-005"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("outcome_scale_null_calibration",),
            comparison_methods=("scm",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # Placebo/rank
        _row(
            "SDID-SCT-023", "sdid_placebo_rank_adapter", SyntheticDidComponent.PLACEBO_RANK,
            ScoutStatus.CANDIDATE_AFTER_ADAPTER,
            "Placebo/rank inference requires future adapter work.",
            required_design_conditions=("valid_placebo_support",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010", "DGP-INF-011"),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-INF-001",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("placebo_null_fpr",),
            comparison_methods=("scm",),
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-INF-001",),
            allowed_current_use=("placebo_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-024", "sdid_placebo_rank_null_calibration", SyntheticDidComponent.PLACEBO_RANK,
            ScoutStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Placebo rank candidate only after null calibration.",
            required_design_conditions=("adapter_implemented",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-INF-011",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-001",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("null_fpr_gate",),
            comparison_methods=("scm",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("calibration_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-025", "sdid_placebo_rank_blocked", SyntheticDidComponent.PLACEBO_RANK,
            ScoutStatus.BLOCKED,
            "Placebo rank blocked without assignment support.",
            required_design_conditions=("known_assignment_mechanism",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # Bootstrap
        _row(
            "SDID-SCT-026", "sdid_bootstrap_research", SyntheticDidComponent.BOOTSTRAP,
            ScoutStatus.RESEARCH_ONLY,
            "Bootstrap inference is research-only for SDID.",
            required_design_conditions=("dependence_structure_documented",),
            required_observed_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-INF-003", "DGP-CP-002"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-003",),
            required_inference_adapter=(),
            required_null_calibration=("bootstrap_null_calibration",),
            comparison_methods=("did", "tbrridge"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-003",),
            allowed_current_use=("bootstrap_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-027", "sdid_bootstrap_simulation_candidate", SyntheticDidComponent.BOOTSTRAP,
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Bootstrap requires DGP dependence validation.",
            required_design_conditions=("cluster_structure_documented",),
            required_observed_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-INF-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-003",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("bootstrap_null_calibration",),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=(),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # Jackknife
        _row(
            "SDID-SCT-028", "sdid_jackknife_research", SyntheticDidComponent.JACKKNIFE,
            ScoutStatus.RESEARCH_ONLY,
            "Jackknife paths are research-only until calibrated.",
            required_design_conditions=("jackknife_support_documented",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-005",),
            required_inference_adapter=(),
            required_null_calibration=("jackknife_null_calibration",),
            comparison_methods=("scm", "augsynth"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("jackknife_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-029", "sdid_jackknife_retire_or_replace", SyntheticDidComponent.JACKKNIFE,
            ScoutStatus.RETIRE_OR_REPLACE,
            "SDID jackknife may be retire/replace if bootstrap/placebo preferred.",
            required_design_conditions=("inference_path_comparison_complete",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-005",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "augsynth", "tbrridge"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("retire_replace_review",),
            forbidden_current_use=_FORBID,
        ),
        # Randomization/permutation
        _row(
            "SDID-SCT-030", "sdid_randomization_assignment_stress", SyntheticDidComponent.RANDOMIZATION_PERMUTATION,
            ScoutStatus.CANDIDATE_AFTER_NULL_CALIBRATION,
            "Randomization/permutation requires assignment stress and null calibration.",
            required_design_conditions=("known_assignment_mechanism",),
            required_observed_diagnostics=("OPD-AD-009", "OPD-AD-010"),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-DA-001", "FM-INF-001"),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("null_fpr_gate",),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001",),
            allowed_current_use=("randomization_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-031", "sdid_randomization_blocked", SyntheticDidComponent.RANDOMIZATION_PERMUTATION,
            ScoutStatus.BLOCKED,
            "Randomization blocked when assignment invalid.",
            required_design_conditions=("valid_assignment_support",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001", "FM-DA-002"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=(),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-002",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        # Deterministic/unknown assignment
        _row(
            "SDID-SCT-032", "sdid_unknown_assignment_blocked", SyntheticDidComponent.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            ScoutStatus.BLOCKED,
            "Unknown assignment blocks SDID inference promotion.",
            required_design_conditions=("assignment_mechanism_known",),
            required_observed_diagnostics=("OPD-AD-001",),
            required_dgp_coverage=("DGP-DA-001",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001", "FM-DA-002"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-033", "sdid_deterministic_falsification_only", SyntheticDidComponent.DETERMINISTIC_UNKNOWN_ASSIGNMENT,
            ScoutStatus.DIAGNOSTIC_ONLY,
            "Deterministic designs may support falsification-only readouts.",
            required_design_conditions=("deterministic_assignment_documented",),
            required_observed_diagnostics=("OPD-AD-002",),
            required_dgp_coverage=("DGP-DA-002",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-DA-002",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm",),
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-DA-002",),
            allowed_current_use=("falsification_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # Multi-treated
        _row(
            "SDID-SCT-034", "sdid_multi_treated_blocked", SyntheticDidComponent.MULTI_TREATED,
            ScoutStatus.BLOCKED,
            "Multi-treated SDID blocked without estimand clarity.",
            required_design_conditions=("multi_treated_estimand_documented",),
            required_observed_diagnostics=("OPD-TE-004",),
            required_dgp_coverage=("DGP-TE-004",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-004",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm", "did"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-004",),
            allowed_current_use=("multi_treated_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-035", "sdid_multi_treated_research", SyntheticDidComponent.MULTI_TREATED,
            ScoutStatus.RESEARCH_ONLY,
            "Multi-treated SDID remains research-only.",
            required_design_conditions=("treated_set_semantics",),
            required_observed_diagnostics=("OPD-TE-003", "OPD-TE-004"),
            required_dgp_coverage=("DGP-TE-003", "DGP-TE-004"),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-TE-004",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=(),
            comparison_methods=("scm",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-TE-004",),
            allowed_current_use=("multi_treated_research",),
            forbidden_current_use=_FORBID,
        ),
        # Multicell/shared-control
        _row(
            "SDID-SCT-036", "sdid_multicell_blocked", SyntheticDidComponent.MULTICELL_SHARED_CONTROL,
            ScoutStatus.BLOCKED,
            "Multicell/shared-control SDID blocked without dependence handling.",
            required_design_conditions=("dependence_model_or_per_cell_restriction",),
            required_observed_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009", "FM-INF-009"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-009", "FM-INF-009"),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID + ("pooled_inference",),
        ),
        _row(
            "SDID-SCT-037", "sdid_multicell_research_only", SyntheticDidComponent.MULTICELL_SHARED_CONTROL,
            ScoutStatus.RESEARCH_ONLY,
            "Multicell SDID is research-only until multiplicity scout downstream work.",
            required_design_conditions=("cell_structure_documented",),
            required_observed_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-001", "DGP-MC-002"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("multicell_null_calibration",),
            comparison_methods=("scm", "did"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-009",),
            allowed_current_use=("multicell_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-038", "sdid_multicell_simulation_candidate", SyntheticDidComponent.MULTICELL_SHARED_CONTROL,
            ScoutStatus.CANDIDATE_AFTER_SIMULATION,
            "Multicell SDID candidate only after shared-control simulation.",
            required_design_conditions=("dependence_structure_documented",),
            required_observed_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002", "DGP-MC-003"),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-009",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("null_fpr_gate",),
            comparison_methods=("scm", "did"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-INF-009",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
        ),
        # vs SCM
        _row(
            "SDID-SCT-039", "sdid_vs_scm_comparison_required", SyntheticDidComponent.VS_SCM,
            ScoutStatus.METHOD_SCOUT_CANDIDATE,
            "SDID must be compared against SCM before promotion.",
            required_design_conditions=("comparable_estimand",),
            required_observed_diagnostics=("OPD-ES-005", "OPD-DS-005"),
            required_dgp_coverage=("DGP-ES-009", "DGP-ES-001"),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-009", "FM-ES-002"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm",),
            promotion_evidence_required=_PROMO + ("scm_comparison",),
            blocking_failure_modes=(),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SDID-SCT-040", "sdid_vs_scm_scm_preferred_diagnostic", SyntheticDidComponent.VS_SCM,
            ScoutStatus.DIAGNOSTIC_ONLY,
            "When SCM diagnostics pass and SDID does not, prefer SCM diagnostic lane.",
            required_design_conditions=("scm_diagnostics_pass",),
            required_observed_diagnostics=("OPD-DS-006", "OPD-PF-001"),
            required_dgp_coverage=("DGP-ES-001",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-002",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("scm",),
            promotion_evidence_required=("scm_comparison",),
            blocking_failure_modes=(),
            allowed_current_use=("scm_preference_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # vs DID
        _row(
            "SDID-SCT-041", "sdid_vs_did_comparison_required", SyntheticDidComponent.VS_DID,
            ScoutStatus.METHOD_SCOUT_CANDIDATE,
            "SDID must be compared against DID before promotion.",
            required_design_conditions=("parallel_trend_assessable",),
            required_observed_diagnostics=("OPD-PF-003",),
            required_dgp_coverage=("DGP-ES-005", "DGP-PF-003"),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-ES-005",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO + ("did_comparison",),
            blocking_failure_modes=(),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-042", "sdid_vs_did_did_suitability_gate", SyntheticDidComponent.VS_DID,
            ScoutStatus.REMEDIATION_REQUIRED,
            "DID suitability audit gates must pass before SDID-DID comparison promotion.",
            required_design_conditions=("did_suitability_audit_passed",),
            required_observed_diagnostics=("OPD-PF-003", "OPD-AD-009"),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-ES-005", "FM-INF-003"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did",),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-ES-005",),
            allowed_current_use=("did_comparison_remediation",),
            forbidden_current_use=_FORBID,
        ),
        # vs AugSynth
        _row(
            "SDID-SCT-043", "sdid_vs_augsynth_comparison_required", SyntheticDidComponent.VS_AUGSYNTH,
            ScoutStatus.METHOD_SCOUT_CANDIDATE,
            "SDID must be compared against AugSynth before promotion.",
            required_design_conditions=("augmentation_comparable",),
            required_observed_diagnostics=("OPD-ES-004", "OPD-ES-005"),
            required_dgp_coverage=("DGP-ES-003", "DGP-ES-004"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-003", "FM-ES-004"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("augsynth",),
            promotion_evidence_required=_PROMO + ("augsynth_comparison",),
            blocking_failure_modes=(),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-044", "sdid_vs_augsynth_disagreement_gate", SyntheticDidComponent.VS_AUGSYNTH,
            ScoutStatus.BLOCKED,
            "Large SDID/AugSynth disagreement blocks promotion.",
            required_design_conditions=("disagreement_threshold_defined",),
            required_observed_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-005",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("augsynth", "scm"),
            promotion_evidence_required=("disagreement_resolution",),
            blocking_failure_modes=("FM-ES-005",),
            allowed_current_use=("disagreement_investigation",),
            forbidden_current_use=_FORBID,
        ),
        # vs TBRRidge
        _row(
            "SDID-SCT-045", "sdid_vs_tbrridge_comparison_required", SyntheticDidComponent.VS_TBRRIDGE,
            ScoutStatus.METHOD_SCOUT_CANDIDATE,
            "SDID must be compared against TBRRidge before promotion.",
            required_design_conditions=("regularization_comparable",),
            required_observed_diagnostics=("OPD-ES-006",),
            required_dgp_coverage=("DGP-ES-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("tbrridge",),
            promotion_evidence_required=_PROMO + ("tbrridge_comparison",),
            blocking_failure_modes=(),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-046", "sdid_vs_tbrridge_tbrridge_diagnostic_only", SyntheticDidComponent.VS_TBRRIDGE,
            ScoutStatus.DIAGNOSTIC_ONLY,
            "TBRRidge remains diagnostic-only; SDID should not inherit TBRRidge inference.",
            required_design_conditions=("tbrridge_audit_consulted",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-ES-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006", "FM-INF-005"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("tbrridge",),
            promotion_evidence_required=("tbrridge_comparison",),
            blocking_failure_modes=("FM-INF-005",),
            allowed_current_use=("tbrridge_boundary_diagnostic",),
            forbidden_current_use=_FORBID,
        ),
        # Cross-cutting gates
        _row(
            "SDID-SCT-047", "sdid_implementation_candidate_after_suitability", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.IMPLEMENTATION_CANDIDATE,
            "Implementation worth pursuing only after full suitability evidence.",
            required_design_conditions=("suitability_scout_complete",),
            required_observed_diagnostics=("OPD-PS-001", "OPD-PF-001", "OPD-DS-005"),
            required_dgp_coverage=("DGP-CP-002", "DGP-ES-009"),
            required_assignment_stress=("ST-AD-001", "ST-AD-009"),
            required_failure_registry_checks=("FM-CP-004", "FM-ES-009"),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("null_fpr_gate",),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO + ("suitability_evidence",),
            blocking_failure_modes=(),
            allowed_current_use=("implementation_scout",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SDID-SCT-048", "sdid_observed_diagnostics_global_gate", SyntheticDidComponent.BALANCED_PANEL,
            ScoutStatus.REMEDIATION_REQUIRED,
            "Observed diagnostics required before SDID method selection.",
            required_design_conditions=("panel_structure_documented",),
            required_observed_diagnostics=("OPD-PS-001", "OPD-PF-001"),
            required_dgp_coverage=("DGP-CP-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-003",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=("observed_diagnostics",),
            blocking_failure_modes=("FM-CP-003",),
            allowed_current_use=("diagnostic_routing",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-049", "sdid_dgp_coverage_global_gate", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.REMEDIATION_REQUIRED,
            "DGP coverage required before SDID implementation promotion.",
            required_design_conditions=("dgp_coverage_plan_satisfied",),
            required_observed_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-CP-002", "DGP-ES-009"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-002",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-CP-002",),
            allowed_current_use=("dgp_planning",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-050", "sdid_failure_registry_global_gate", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.REMEDIATION_REQUIRED,
            "Failure registry consultation required for all SDID paths.",
            required_design_conditions=("failure_registry_consulted",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-CP-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-004", "FM-ES-009"),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=("failure_registry_consult",),
            blocking_failure_modes=("FM-CP-004",),
            allowed_current_use=("registry_consultation",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-051", "sdid_design_stress_global_gate", SyntheticDidComponent.RANDOMIZATION_PERMUTATION,
            ScoutStatus.REMEDIATION_REQUIRED,
            "Design assignment stress required for inference paths.",
            required_design_conditions=("assignment_mechanism_documented",),
            required_observed_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-DA-001",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=("did", "scm"),
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DA-001",),
            allowed_current_use=("stress_test_research",),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-052", "sdid_production_pvalue_global_block", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.BLOCKED,
            "Global block on Synthetic DID production p-values.",
            required_design_conditions=("promotion_evidence_complete",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_inference_adapter=(),
            required_null_calibration=("null_fpr_gate",),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DB-009",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-053", "sdid_causal_ci_global_block", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.BLOCKED,
            "Global block on Synthetic DID causal confidence intervals.",
            required_design_conditions=("promotion_evidence_complete",),
            required_observed_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-010",),
            required_inference_adapter=(),
            required_null_calibration=("coverage_gate",),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-DB-010",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
        ),
        _row(
            "SDID-SCT-054", "sdid_adapter_null_calibration_gate", SyntheticDidComponent.PLACEBO_RANK,
            ScoutStatus.CANDIDATE_AFTER_ADAPTER,
            "SDID inference needs future adapter before null calibration.",
            required_design_conditions=("adapter_contract_defined",),
            required_observed_diagnostics=("OPD-IR-002",),
            required_dgp_coverage=("DGP-INF-002",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-INF-002",),
            required_inference_adapter=("SYNTHETIC_DID_INFERENCE_ADAPTER_001",),
            required_null_calibration=("studentized_null_calibration",),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO + ("adapter_contract",),
            blocking_failure_modes=("FM-INF-002",),
            allowed_current_use=("adapter_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "SDID-SCT-055", "sdid_research_not_production_posture", SyntheticDidComponent.POINT_ESTIMATE,
            ScoutStatus.RESEARCH_ONLY,
            "Synthetic DID is research/scout candidate per family roadmap.",
            required_design_conditions=("research_only_labeled",),
            required_observed_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-CP-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-005",),
            required_inference_adapter=(),
            required_null_calibration=(),
            comparison_methods=_CMP_ALL,
            promotion_evidence_required=_PROMO,
            blocking_failure_modes=("FM-CP-005",),
            allowed_current_use=("labeled_research",),
            forbidden_current_use=_FORBID,
            recommended_next_artifact=_BAYES,
        ),
    )


def filter_synthetic_did_method_scout_suitability(
    rows: tuple[SyntheticDidScoutRow, ...],
    *,
    synthetic_did_component: SyntheticDidComponent | None = None,
    current_status: ScoutStatus | None = None,
    comparison_method: str | None = None,
) -> tuple[SyntheticDidScoutRow, ...]:
    """Filter scout rows by optional criteria."""
    result: list[SyntheticDidScoutRow] = []
    for row in rows:
        if synthetic_did_component is not None and row.synthetic_did_component != synthetic_did_component:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if comparison_method is not None and comparison_method not in row.comparison_methods:
            continue
        result.append(row)
    return tuple(result)


def validate_synthetic_did_method_scout_suitability(
    rows: tuple[SyntheticDidScoutRow, ...],
) -> dict[str, Any]:
    """Validate scout registry thresholds and coverage."""
    issues: list[str] = []
    scout_ids = [r.scout_id for r in rows]

    if len(rows) < MIN_SCOUT_ROW_COUNT:
        issues.append(f"scout_row_count {len(rows)} < {MIN_SCOUT_ROW_COUNT}")
    if len(scout_ids) != len(set(scout_ids)):
        issues.append("duplicate scout_id values")

    status_counts = Counter(r.current_status for r in rows)
    component_counts = Counter(r.synthetic_did_component.value for r in rows)
    comparison_counts: Counter[str] = Counter()
    for row in rows:
        for cm in row.comparison_methods:
            comparison_counts[cm] += 1

    for component in REQUIRED_COMPONENTS:
        if not any(r.synthetic_did_component == component for r in rows):
            issues.append(f"missing component: {component.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    for method in ("scm", "augsynth", "did", "tbrridge"):
        if comparison_counts.get(method, 0) == 0:
            issues.append(f"missing comparison method: {method}")

    unlinked = [r.scout_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "scout_row_count": len(rows),
        "unique_scout_ids": len(scout_ids) == len(set(scout_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in ScoutStatus},
        "component_counts": dict(component_counts),
        "comparison_method_counts": dict(comparison_counts),
        "all_required_paths_covered": all(
            any(r.synthetic_did_component == c for r in rows) for c in REQUIRED_COMPONENTS
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "issues": issues,
    }


def summarize_synthetic_did_method_scout_suitability(
    rows: tuple[SyntheticDidScoutRow, ...],
) -> dict[str, Any]:
    """Serialize Synthetic DID scout summary for archives."""
    validation = validate_synthetic_did_method_scout_suitability(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "scout_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "component_counts": validation["component_counts"],
        "comparison_method_counts": validation["comparison_method_counts"],
        "all_required_paths_covered": validation["all_required_paths_covered"],
        "recommended_next_artifacts": list(RECOMMENDED_NEXT_ARTIFACTS),
        **_SCOUT_FLAGS,
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
    rows = build_synthetic_did_method_scout_suitability()
    validation = validate_synthetic_did_method_scout_suitability(rows)
    summary = summarize_synthetic_did_method_scout_suitability(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("scout_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("scout_row_count_at_least_50", len(rows) >= MIN_SCOUT_ROW_COUNT))
    scenarios.append(_scenario("scout_ids_unique", validation["unique_scout_ids"]))

    for component in REQUIRED_COMPONENTS:
        present = any(r.synthetic_did_component == component for r in rows)
        scenarios.append(_scenario(f"component_{component.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for flag, expected in _SCOUT_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_bayesian_tbr_and_tbr_retirement_boundary_audit_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_synthetic_did_method_scout_suitability()
    validation = validate_synthetic_did_method_scout_suitability(rows)
    summary = summarize_synthetic_did_method_scout_suitability(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "scout_row_count": len(rows),
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
