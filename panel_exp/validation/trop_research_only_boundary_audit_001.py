"""TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001 validation harness."""

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

_ARTIFACT_ID = "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "trop_research_only_boundary_audit_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = _REPO / "docs/track_d/archives/TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001_summary.json"

RECOMMENDED_NEXT_ARTIFACTS = ("METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",)

MIN_BOUNDARY_ROW_COUNT = 35

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
    "trop_research_only_unless_future_evidence": True,
    "trop_production_inference_authorized": False,
    "trop_production_p_value_authorized": False,
    "trop_causal_ci_authorized": False,
    "trop_production_recommendation_authorized": False,
    "trop_budget_allocation_authorized": False,
    "trop_decisioning_authorized": False,
    "trop_heterogeneous_effect_claims_require_design_valid_causal_evidence": True,
    "future_simulation_required": True,
    "future_calibration_replay_required": True,
    "observed_diagnostics_required": True,
    "dgp_coverage_required": True,
    "design_assignment_stress_required": True,
    "failure_registry_consulted": True,
    "multicell_shared_control_blocked_without_dependence_handling": True,
    "comparison_against_scm_required": True,
    "comparison_against_did_required": True,
    "comparison_against_synthetic_did_required": True,
    "comparison_against_tbrridge_required": True,
    "downstream_work_paused": True,
}

_REQUIRED_COMPARISONS = frozenset({"scm", "did", "synthetic_did", "tbrridge"})


class TropPath(str, Enum):
    POINT_SCORE_DIAGNOSTIC = "trop_point_score_diagnostic"
    TREATMENT_RESPONSE_RANKING = "trop_treatment_response_ranking"
    POLICY_RECOMMENDATION = "trop_policy_recommendation"
    BUDGET_ALLOCATION = "trop_budget_allocation_recommendation"
    HETEROGENEOUS_EFFECT = "trop_heterogeneous_effect_claim"
    OBSERVATIONAL_UPLIFT = "trop_observational_uplift_claim"
    CAUSAL_INFERENCE = "trop_causal_inference_claim"
    UNCERTAINTY_INTERVAL = "trop_uncertainty_interval"
    CALIBRATION_REPLAY = "trop_calibration_replay_candidate"
    SIMULATION_STRESS = "trop_simulation_stress_candidate"
    VS_SCM = "trop_comparison_against_scm"
    VS_DID = "trop_comparison_against_did"
    VS_SYNTHETIC_DID = "trop_comparison_against_synthetic_did"
    VS_TBRRIDGE = "trop_comparison_against_tbrridge"
    MULTICELL_SHARED_CONTROL = "trop_multicell_shared_control"
    SPARSE_COUNT_RATE = "trop_sparse_count_rate_outcomes"
    UNKNOWN_DETERMINISTIC = "trop_unknown_deterministic_assignment"
    RESEARCH_SCOUT = "trop_research_only_method_scout"
    RETIRE_REPLACE = "trop_retire_replace_candidate"


class BoundaryStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    METHOD_SCOUT_CANDIDATE = "method_scout_candidate"
    REMEDIATION_REQUIRED = "remediation_required"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"
    CANDIDATE_AFTER_CALIBRATION_REPLAY = "candidate_after_calibration_replay"
    RETIRE_OR_REPLACE = "retire_or_replace"


REQUIRED_PATHS = frozenset(TropPath)
REQUIRED_STATUSES = frozenset(BoundaryStatus)


@dataclass(frozen=True)
class TropBoundaryRow:
    boundary_id: str
    name: str
    trop_path: TropPath
    current_status: BoundaryStatus
    known_blockers: tuple[str, ...]
    required_observed_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_calibration_evidence: tuple[str, ...]
    comparison_methods: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    promotion_hypothesis: bool
    promotion_evidence_required: tuple[str, ...]
    retire_or_replace_candidate: bool
    recommended_next_artifact: str | None
    notes: str


def _row(
    boundary_id: str,
    name: str,
    trop_path: TropPath,
    current_status: BoundaryStatus,
    notes: str,
    *,
    known_blockers: tuple[str, ...],
    required_observed_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_calibration_evidence: tuple[str, ...],
    comparison_methods: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    promotion_hypothesis: bool = False,
    promotion_evidence_required: tuple[str, ...],
    retire_or_replace_candidate: bool = False,
    recommended_next_artifact: str | None = None,
) -> TropBoundaryRow:
    return TropBoundaryRow(
        boundary_id=boundary_id,
        name=name,
        trop_path=trop_path,
        current_status=current_status,
        known_blockers=known_blockers,
        required_observed_diagnostics=required_observed_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_calibration_evidence=required_calibration_evidence,
        comparison_methods=comparison_methods,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        promotion_hypothesis=promotion_hypothesis,
        promotion_evidence_required=promotion_evidence_required,
        retire_or_replace_candidate=retire_or_replace_candidate,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_FORBID = (
    "production_p_value",
    "causal_ci",
    "trustreport",
    "production_inference",
    "production_recommendation",
    "budget_allocation",
    "decisioning",
)
_NEXT = "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
_DIAG = ("OPD-PF-001", "OPD-DS-005")
_DGP = ("DGP-ES-009", "DGP-CP-003")
_STRESS = ("ST-AD-001", "ST-AD-009")
_FM = ("FM-ES-009", "FM-INF-012")
_ALL_CMP = ("scm", "did", "synthetic_did", "tbrridge")


def build_trop_research_only_boundary_audit() -> tuple[TropBoundaryRow, ...]:
    """Return metadata-only TROP boundary audit rows."""
    return (
        # Point/score diagnostic
        _row(
            "TROP-BND-001", "trop_point_score_diagnostic_readout", TropPath.POINT_SCORE_DIAGNOSTIC,
            BoundaryStatus.DIAGNOSTIC_ONLY,
            "TROP point/score may support research diagnostic readout only.",
            known_blockers=("no_production_estimand", "research_only_codebase"),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_diagnostic_score",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            "TROP-BND-002", "trop_point_score_production_blocked", TropPath.POINT_SCORE_DIAGNOSTIC,
            BoundaryStatus.BLOCKED,
            "TROP production point estimate remains unauthorized.",
            known_blockers=("production_inference_unauthorized",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress", "calibration_replay"),
        ),
        # Treatment-response ranking
        _row(
            "TROP-BND-003", "trop_ranking_research_only", TropPath.TREATMENT_RESPONSE_RANKING,
            BoundaryStatus.RESEARCH_ONLY,
            "Treatment-response ranking requires design-valid causal evidence before promotion.",
            known_blockers=("heterogeneous_ranking_overclaim", "no_design_valid_causal_evidence"),
            required_observed_diagnostics=("OPD-PF-001", "OPD-AD-003"),
            required_dgp_coverage=("DGP-ES-009", "DGP-HT-002"),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-INF-012", "FM-DA-010"),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_ranking_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_valid_causal_evidence", "simulation_stress"),
        ),
        _row(
            "TROP-BND-004", "trop_ranking_production_blocked", TropPath.TREATMENT_RESPONSE_RANKING,
            BoundaryStatus.BLOCKED,
            "Production treatment-response ranking is blocked.",
            known_blockers=("production_recommendation_unauthorized",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay",),
        ),
        # Policy recommendation
        _row(
            "TROP-BND-005", "trop_policy_recommendation_blocked", TropPath.POLICY_RECOMMENDATION,
            BoundaryStatus.BLOCKED,
            "TROP must not produce production policy recommendations.",
            known_blockers=("policy_recommendation_risk", "decisioning_unauthorized"),
            required_observed_diagnostics=("OPD-PF-001", "OPD-OM-002"),
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-INF-012",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_valid_causal_evidence", "calibration_replay"),
        ),
        _row(
            "TROP-BND-006", "trop_policy_research_exploration", TropPath.POLICY_RECOMMENDATION,
            BoundaryStatus.RESEARCH_ONLY,
            "Policy recommendation paths remain research-only exploration.",
            known_blockers=("no_production_decisioning",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_policy_simulation",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress",),
        ),
        # Budget/allocation
        _row(
            "TROP-BND-007", "trop_budget_allocation_blocked", TropPath.BUDGET_ALLOCATION,
            BoundaryStatus.BLOCKED,
            "TROP budget/allocation recommendation is blocked.",
            known_blockers=("budget_optimization_unauthorized",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-MC-004"),
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-CP-005",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay", "simulation_stress"),
        ),
        _row(
            "TROP-BND-008", "trop_budget_research_scout", TropPath.BUDGET_ALLOCATION,
            BoundaryStatus.METHOD_SCOUT_CANDIDATE,
            "Budget allocation scout path for future evidence only.",
            known_blockers=("no_budget_optimization",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("method_scout_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress", "calibration_replay"),
            recommended_next_artifact=_NEXT,
        ),
        # Heterogeneous effect
        _row(
            "TROP-BND-009", "trop_heterogeneous_effect_blocked", TropPath.HETEROGENEOUS_EFFECT,
            BoundaryStatus.BLOCKED,
            "Heterogeneous-effect claims require design-valid causal evidence.",
            known_blockers=("heterogeneous_overclaim", "no_design_valid_causal_evidence"),
            required_observed_diagnostics=("OPD-AD-003", "OPD-HT-001"),
            required_dgp_coverage=("DGP-HT-002", "DGP-ES-009"),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-INF-012", "FM-DA-010"),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_valid_causal_evidence",),
        ),
        _row(
            "TROP-BND-010", "trop_heterogeneous_research_only", TropPath.HETEROGENEOUS_EFFECT,
            BoundaryStatus.RESEARCH_ONLY,
            "Heterogeneous-effect research path without production claims.",
            known_blockers=("research_only_estimator",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=("DGP-HT-002",),
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_heterogeneity_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress",),
        ),
        # Observational/uplift
        _row(
            "TROP-BND-011", "trop_observational_uplift_blocked", TropPath.OBSERVATIONAL_UPLIFT,
            BoundaryStatus.BLOCKED,
            "Observational/uplift-style causal claims are blocked.",
            known_blockers=("observational_uplift_overclaim", "unknown_assignment"),
            required_observed_diagnostics=("OPD-AD-001", "OPD-PF-001"),
            required_dgp_coverage=("DGP-CP-003",),
            required_assignment_stress=("ST-AD-011",),
            required_failure_registry_checks=("FM-DA-009",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_valid_causal_evidence",),
        ),
        _row(
            "TROP-BND-012", "trop_observational_research_scout", TropPath.OBSERVATIONAL_UPLIFT,
            BoundaryStatus.METHOD_SCOUT_CANDIDATE,
            "Observational uplift scout for method comparison research.",
            known_blockers=("uplift_identification_gap",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=("ST-AD-011",),
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("method_scout_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress",),
        ),
        # Causal inference
        _row(
            "TROP-BND-013", "trop_causal_inference_blocked", TropPath.CAUSAL_INFERENCE,
            BoundaryStatus.BLOCKED,
            "TROP production causal inference remains unauthorized.",
            known_blockers=("production_inference_unauthorized", "triply_robust_unvalidated"),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay", "simulation_stress"),
        ),
        _row(
            "TROP-BND-014", "trop_causal_remediation_required", TropPath.CAUSAL_INFERENCE,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "Causal inference path requires full audit ladder before promotion hypothesis.",
            known_blockers=("implementation_gap", "validation_runner_skipped"),
            required_observed_diagnostics=("OPD-PF-001", "OPD-DS-005", "OPD-AD-003"),
            required_dgp_coverage=("DGP-ES-009", "DGP-CP-003", "DGP-HT-002"),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-ES-009", "FM-INF-012"),
            required_calibration_evidence=("null_calibration",),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("remediation_planning",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=("calibration_replay", "simulation_stress", "method_comparison"),
            recommended_next_artifact=_NEXT,
        ),
        # Uncertainty interval
        _row(
            "TROP-BND-015", "trop_uncertainty_interval_research", TropPath.UNCERTAINTY_INTERVAL,
            BoundaryStatus.RESEARCH_ONLY,
            "TROP uncertainty intervals are research-only; not causal CIs.",
            known_blockers=("interval_not_causal_ci",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-INF-012",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_uncertainty_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay",),
        ),
        _row(
            "TROP-BND-016", "trop_uncertainty_production_blocked", TropPath.UNCERTAINTY_INTERVAL,
            BoundaryStatus.BLOCKED,
            "Production causal CIs from TROP are blocked.",
            known_blockers=("causal_ci_unauthorized",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay", "simulation_stress"),
        ),
        # Calibration/replay
        _row(
            "TROP-BND-017", "trop_calibration_replay_candidate", TropPath.CALIBRATION_REPLAY,
            BoundaryStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            "Promotion requires calibration/replay evidence before any hypothesis.",
            known_blockers=("no_calibration_replay_yet",),
            required_observed_diagnostics=("OPD-PF-001", "OPD-OM-001"),
            required_dgp_coverage=("DGP-ES-009", "DGP-CP-003"),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=_FM,
            required_calibration_evidence=("null_fpr_gate", "coverage_replay"),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("calibration_replay_planning",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=("calibration_replay",),
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "TROP-BND-018", "trop_calibration_blocked_until_evidence", TropPath.CALIBRATION_REPLAY,
            BoundaryStatus.BLOCKED,
            "No promotion until calibration/replay completes.",
            known_blockers=("calibration_replay_missing",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=("null_calibration",),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay",),
        ),
        # Simulation/stress
        _row(
            "TROP-BND-019", "trop_simulation_stress_candidate", TropPath.SIMULATION_STRESS,
            BoundaryStatus.CANDIDATE_AFTER_SIMULATION,
            "Simulation/stress-test evidence required before promotion.",
            known_blockers=("simulation_coverage_incomplete",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=("DGP-ES-009", "DGP-HT-002", "DGP-CP-003"),
            required_assignment_stress=("ST-AD-009", "ST-AD-010", "ST-AD-011"),
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("simulation_planning",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=("simulation_stress",),
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "TROP-BND-020", "trop_simulation_research_only", TropPath.SIMULATION_STRESS,
            BoundaryStatus.RESEARCH_ONLY,
            "Simulation stress paths remain research-only today.",
            known_blockers=("dgp_coverage_gaps",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=("DGP-ES-009",),
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_simulation",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress",),
        ),
        # Comparisons
        _row(
            "TROP-BND-021", "trop_vs_scm_comparison_required", TropPath.VS_SCM,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "TROP must be compared against SCM before any promotion.",
            known_blockers=("scm_stronger_near_term_candidate",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=("DGP-ES-009", "DGP-SCM-001"),
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-ES-009",),
            required_calibration_evidence=(),
            comparison_methods=("scm", "did", "synthetic_did", "tbrridge"),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("scm_head_to_head", "simulation_stress"),
        ),
        _row(
            "TROP-BND-022", "trop_vs_scm_research_only", TropPath.VS_SCM,
            BoundaryStatus.RESEARCH_ONLY,
            "TROP vs SCM comparison remains research-only.",
            known_blockers=("no_head_to_head_calibration",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=("scm",),
            allowed_current_use=("research_comparison",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("scm_head_to_head",),
        ),
        _row(
            "TROP-BND-023", "trop_vs_did_comparison_required", TropPath.VS_DID,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "TROP must be compared against DID before promotion.",
            known_blockers=("did_randomization_baseline_exists",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=("DGP-ES-009", "DGP-DID-001"),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-009",),
            required_calibration_evidence=(),
            comparison_methods=("did", "scm", "synthetic_did", "tbrridge"),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("did_head_to_head",),
        ),
        _row(
            "TROP-BND-024", "trop_vs_did_research_scout", TropPath.VS_DID,
            BoundaryStatus.METHOD_SCOUT_CANDIDATE,
            "TROP vs DID scout for design-based benchmark.",
            known_blockers=("design_aware_placebo_pending",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=("did",),
            allowed_current_use=("method_scout_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("did_head_to_head",),
        ),
        _row(
            "TROP-BND-025", "trop_vs_synthetic_did_required", TropPath.VS_SYNTHETIC_DID,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "TROP must be compared against Synthetic DID before promotion.",
            known_blockers=("synthetic_did_scout_complete",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=("DGP-ES-009", "DGP-SDID-001"),
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=("synthetic_did", "scm", "did", "tbrridge"),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("synthetic_did_head_to_head",),
        ),
        _row(
            "TROP-BND-026", "trop_vs_synthetic_did_research", TropPath.VS_SYNTHETIC_DID,
            BoundaryStatus.RESEARCH_ONLY,
            "Synthetic DID comparison research path.",
            known_blockers=("synthetic_did_research_scout_only",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=("synthetic_did",),
            allowed_current_use=("research_comparison",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("synthetic_did_head_to_head",),
        ),
        _row(
            "TROP-BND-027", "trop_vs_tbrridge_required", TropPath.VS_TBRRIDGE,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "TROP must be compared against TBRRidge; TBRRidge audit preserved.",
            known_blockers=("tbrridge_remediation_audit_active",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-INF-008",),
            required_calibration_evidence=(),
            comparison_methods=("tbrridge", "scm", "did", "synthetic_did"),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("tbrridge_head_to_head",),
        ),
        _row(
            "TROP-BND-028", "trop_vs_tbrridge_research_only", TropPath.VS_TBRRIDGE,
            BoundaryStatus.RESEARCH_ONLY,
            "TBRRidge comparison research; does not reverse TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001.",
            known_blockers=("tbrridge_boundary_preserved",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-INF-008",),
            required_calibration_evidence=(),
            comparison_methods=("tbrridge",),
            allowed_current_use=("research_comparison",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("tbrridge_head_to_head",),
        ),
        # Multicell
        _row(
            "TROP-BND-029", "trop_multicell_blocked", TropPath.MULTICELL_SHARED_CONTROL,
            BoundaryStatus.BLOCKED,
            "Multicell/shared-control TROP blocked without dependence handling.",
            known_blockers=("multicell_dependence_unhandled", "multiplicity_unhandled"),
            required_observed_diagnostics=("OPD-MC-004", "OPD-MC-005"),
            required_dgp_coverage=("DGP-MC-001",),
            required_assignment_stress=("ST-AD-012",),
            required_failure_registry_checks=("FM-CP-004",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("multicell_dependence_remediation",),
        ),
        _row(
            "TROP-BND-030", "trop_multicell_research_only", TropPath.MULTICELL_SHARED_CONTROL,
            BoundaryStatus.RESEARCH_ONLY,
            "Multicell TROP paths remain research-only per MULTICELL_MAX_T_RESEARCH_SCOUT_001.",
            known_blockers=("shared_control_dependence",),
            required_observed_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-MC-001",),
            required_assignment_stress=("ST-AD-012",),
            required_failure_registry_checks=("FM-CP-004",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("multicell_research_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("multicell_dependence_remediation",),
        ),
        # Sparse/count/rate
        _row(
            "TROP-BND-031", "trop_sparse_count_rate_remediation", TropPath.SPARSE_COUNT_RATE,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "Sparse/count/rate outcomes require outcome-scale remediation.",
            known_blockers=("outcome_scale_mismatch",),
            required_observed_diagnostics=("OPD-OM-002", "OPD-PF-001"),
            required_dgp_coverage=("DGP-OM-001", "DGP-CP-003"),
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-CP-005",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("outcome_scale_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("outcome_scale_dgp",),
        ),
        _row(
            "TROP-BND-032", "trop_sparse_count_rate_blocked", TropPath.SPARSE_COUNT_RATE,
            BoundaryStatus.BLOCKED,
            "Production TROP on sparse/count/rate outcomes blocked.",
            known_blockers=("sparse_outcome_unvalidated",),
            required_observed_diagnostics=("OPD-OM-002",),
            required_dgp_coverage=("DGP-OM-001",),
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("outcome_scale_dgp", "simulation_stress"),
        ),
        # Unknown/deterministic assignment
        _row(
            "TROP-BND-033", "trop_unknown_assignment_blocked", TropPath.UNKNOWN_DETERMINISTIC,
            BoundaryStatus.BLOCKED,
            "Unknown/deterministic assignment blocks causal promotion.",
            known_blockers=("assignment_unknown", "deterministic_assignment"),
            required_observed_diagnostics=("OPD-AD-001", "OPD-AD-003"),
            required_dgp_coverage=("DGP-CP-003",),
            required_assignment_stress=("ST-AD-011",),
            required_failure_registry_checks=("FM-DA-009",),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_valid_causal_evidence",),
        ),
        _row(
            "TROP-BND-034", "trop_assignment_stress_research", TropPath.UNKNOWN_DETERMINISTIC,
            BoundaryStatus.RESEARCH_ONLY,
            "Assignment stress research path for TROP.",
            known_blockers=("assignment_stress_incomplete",),
            required_observed_diagnostics=("OPD-AD-001",),
            required_dgp_coverage=_DGP,
            required_assignment_stress=("ST-AD-011", "ST-AD-001"),
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("assignment_stress_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_assignment_stress",),
        ),
        # Research scout
        _row(
            "TROP-BND-035", "trop_method_scout_candidate", TropPath.RESEARCH_SCOUT,
            BoundaryStatus.METHOD_SCOUT_CANDIDATE,
            "TROP remains research-only method scout per TRIPLY_ROBUST_ESTIMATOR_AUDIT_PROGRAM_001.",
            known_blockers=("validation_runner_skipped", "research_only_codebase"),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("method_scout_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress", "calibration_replay"),
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "TROP-BND-036", "trop_research_only_default", TropPath.RESEARCH_SCOUT,
            BoundaryStatus.RESEARCH_ONLY,
            "Default TROP posture: research-only unless future evidence proves otherwise.",
            known_blockers=("no_promotion_evidence",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("research_only_default",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("calibration_replay", "simulation_stress"),
        ),
        # Retire/replace
        _row(
            "TROP-BND-037", "trop_production_decisioning_retire", TropPath.RETIRE_REPLACE,
            BoundaryStatus.RETIRE_OR_REPLACE,
            "Production decisioning/recommendation paths are retire/replace candidates.",
            known_blockers=("production_decisioning_unauthorized",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            retire_or_replace_candidate=True,
            promotion_evidence_required=("full_audit_ladder",),
        ),
        _row(
            "TROP-BND-038", "trop_causal_overclaim_retire", TropPath.RETIRE_REPLACE,
            BoundaryStatus.RETIRE_OR_REPLACE,
            "TROP causal overclaim without triply-robust validation is retire/replace.",
            known_blockers=("triply_robust_unvalidated", "causal_overclaim"),
            required_observed_diagnostics=("OPD-PF-001", "OPD-AD-003"),
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=("FM-INF-012", "FM-ES-009"),
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            retire_or_replace_candidate=True,
            promotion_evidence_required=("calibration_replay", "method_comparison"),
        ),
        # Extra diagnostic rows for path coverage depth
        _row(
            "TROP-BND-039", "trop_point_scout_diagnostic", TropPath.POINT_SCORE_DIAGNOSTIC,
            BoundaryStatus.METHOD_SCOUT_CANDIDATE,
            "Point/score scout for triply-robust diagnostic exploration.",
            known_blockers=("research_only",),
            required_observed_diagnostics=_DIAG,
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("method_scout_exploration",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("simulation_stress",),
        ),
        _row(
            "TROP-BND-040", "trop_policy_remediation", TropPath.POLICY_RECOMMENDATION,
            BoundaryStatus.REMEDIATION_REQUIRED,
            "Policy paths require remediation before any scout promotion.",
            known_blockers=("policy_identification_gap",),
            required_observed_diagnostics=("OPD-OM-002",),
            required_dgp_coverage=_DGP,
            required_assignment_stress=_STRESS,
            required_failure_registry_checks=_FM,
            required_calibration_evidence=(),
            comparison_methods=_ALL_CMP,
            allowed_current_use=("remediation_planning",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("design_valid_causal_evidence",),
        ),
    )


def filter_trop_research_only_boundary_audit(
    rows: tuple[TropBoundaryRow, ...],
    *,
    trop_path: TropPath | None = None,
    current_status: BoundaryStatus | None = None,
    retire_or_replace_candidate: bool | None = None,
    comparison_method: str | None = None,
) -> tuple[TropBoundaryRow, ...]:
    """Filter TROP boundary audit rows by optional criteria."""
    result: list[TropBoundaryRow] = []
    for row in rows:
        if trop_path is not None and row.trop_path != trop_path:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if retire_or_replace_candidate is not None and row.retire_or_replace_candidate != retire_or_replace_candidate:
            continue
        if comparison_method is not None and comparison_method not in row.comparison_methods:
            continue
        result.append(row)
    return tuple(result)


def _comparison_method_counts(rows: tuple[TropBoundaryRow, ...]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        for method in row.comparison_methods:
            counts[method] += 1
    return dict(counts)


def validate_trop_research_only_boundary_audit(
    rows: tuple[TropBoundaryRow, ...],
) -> dict[str, Any]:
    """Validate TROP boundary audit registry thresholds and coverage."""
    issues: list[str] = []
    boundary_ids = [r.boundary_id for r in rows]

    if len(rows) < MIN_BOUNDARY_ROW_COUNT:
        issues.append(f"boundary_row_count {len(rows)} < {MIN_BOUNDARY_ROW_COUNT}")
    if len(boundary_ids) != len(set(boundary_ids)):
        issues.append("duplicate boundary_id values")

    status_counts = Counter(r.current_status for r in rows)
    path_counts = Counter(r.trop_path.value for r in rows)
    comparison_counts = _comparison_method_counts(rows)

    for path in REQUIRED_PATHS:
        if not any(r.trop_path == path for r in rows):
            issues.append(f"missing trop_path: {path.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    retire_rows = [r for r in rows if r.retire_or_replace_candidate]
    if not retire_rows:
        issues.append("no retire_or_replace_candidate rows")

    for cmp_method in _REQUIRED_COMPARISONS:
        if comparison_counts.get(cmp_method, 0) == 0:
            issues.append(f"missing comparison_method: {cmp_method}")

    het_blocked = any(
        r.trop_path == TropPath.HETEROGENEOUS_EFFECT and r.current_status == BoundaryStatus.BLOCKED
        for r in rows
    )
    if not het_blocked:
        issues.append("heterogeneous effect blocked row missing")

    unlinked = [r.boundary_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "boundary_row_count": len(rows),
        "unique_boundary_ids": len(boundary_ids) == len(set(boundary_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in BoundaryStatus},
        "trop_path_counts": dict(path_counts),
        "comparison_method_counts": comparison_counts,
        "all_required_paths_covered": all(any(r.trop_path == p for r in rows) for p in REQUIRED_PATHS),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "retire_or_replace_paths_defined": bool(retire_rows),
        "issues": issues,
    }


def summarize_trop_research_only_boundary_audit(
    rows: tuple[TropBoundaryRow, ...],
) -> dict[str, Any]:
    """Serialize TROP boundary audit summary for archives."""
    validation = validate_trop_research_only_boundary_audit(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "boundary_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "trop_path_counts": validation["trop_path_counts"],
        "comparison_method_counts": validation["comparison_method_counts"],
        "all_required_paths_covered": validation["all_required_paths_covered"],
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
    rows = build_trop_research_only_boundary_audit()
    validation = validate_trop_research_only_boundary_audit(rows)
    summary = summarize_trop_research_only_boundary_audit(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("boundary_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("boundary_row_count_at_least_35", len(rows) >= MIN_BOUNDARY_ROW_COUNT))
    scenarios.append(_scenario("boundary_ids_unique", validation["unique_boundary_ids"]))

    for path in REQUIRED_PATHS:
        present = any(r.trop_path == path for r in rows)
        scenarios.append(_scenario(f"trop_path_{path.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for cmp_method in _REQUIRED_COMPARISONS:
        count = validation["comparison_method_counts"].get(cmp_method, 0)
        scenarios.append(_scenario(f"comparison_{cmp_method}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_method_family_promotion_criteria_matrix_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_trop_research_only_boundary_audit()
    validation = validate_trop_research_only_boundary_audit(rows)
    summary = summarize_trop_research_only_boundary_audit(rows)
    scenarios = build_scenarios()
    failed = [s["scenario_id"] for s in scenarios if not s["passed"]]

    payload: dict[str, Any] = {
        "artifact_id": _ARTIFACT_ID,
        "artifact_version": _ARTIFACT_VERSION,
        "status": "completed",
        "verdict": _VERDICT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "boundary_row_count": len(rows),
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
