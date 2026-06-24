"""BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001 validation harness."""

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

_ARTIFACT_ID = "BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001"
_ARTIFACT_VERSION = "1.0.0"
_VERDICT = "bayesian_tbr_and_tbr_retirement_boundary_audit_completed_no_downstream_authorization"
_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_SUMMARY = (
    _REPO / "docs/track_d/archives/BAYESIAN_TBR_AND_TBR_RETIREMENT_BOUNDARY_AUDIT_001_summary.json"
)

RECOMMENDED_NEXT_ARTIFACTS = (
    "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001",
    "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001",
)

MIN_BOUNDARY_ROW_COUNT = 45

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
    "bayesian_tbr_posterior_intervals_not_causal_ci": True,
    "bayesian_tbr_production_inference_authorized": False,
    "bayesian_tbr_production_p_value_authorized": False,
    "bayesian_tbr_causal_ci_authorized": False,
    "bayesian_tbr_posterior_diagnostic_only_until_calibrated": True,
    "bayesian_tbr_requires_calibration_replay_before_promotion": True,
    "classic_tbr_aggregate_overclaim_blocked": True,
    "classic_tbr_retire_or_replace_paths_defined": True,
    "classic_tbr_production_inference_authorized": False,
    "classic_tbr_production_p_value_authorized": False,
    "classic_tbr_causal_ci_authorized": False,
    "multicell_shared_control_blocked_without_dependence_handling": True,
    "tbrridge_prior_boundary_preserved": True,
    "observed_diagnostics_required": True,
    "dgp_coverage_required": True,
    "design_assignment_stress_required": True,
    "failure_registry_consulted": True,
    "downstream_work_paused": True,
}


class MethodFamily(str, Enum):
    CLASSIC_TBR = "classic_tbr"
    BAYESIAN_TBR = "bayesian_tbr"
    BOTH = "both"


class PathType(str, Enum):
    CLASSIC_POINT = "classic_tbr_point_estimate"
    CLASSIC_AGGREGATE_GLOBAL = "classic_tbr_aggregate_global"
    CLASSIC_PER_CELL_MARGINAL = "classic_tbr_per_cell_marginal"
    CLASSIC_RESIDUAL_BOOTSTRAP = "classic_tbr_residual_bootstrap"
    CLASSIC_PLACEBO_RANK = "classic_tbr_placebo_rank"
    CLASSIC_DETERMINISTIC_UNKNOWN = "classic_tbr_deterministic_unknown_assignment"
    CLASSIC_MULTICELL = "classic_tbr_multicell_shared_control"
    BAYESIAN_POSTERIOR_DIAGNOSTIC = "bayesian_tbr_posterior_diagnostic"
    BAYESIAN_POSTERIOR_INTERVAL = "bayesian_tbr_posterior_interval"
    BAYESIAN_CREDIBLE_AS_CAUSAL_CI = "bayesian_tbr_credible_as_causal_ci"
    BAYESIAN_PRIOR_SENSITIVITY = "bayesian_tbr_prior_sensitivity"
    BAYESIAN_PPC = "bayesian_tbr_posterior_predictive_check"
    BAYESIAN_CALIBRATION_REPLAY = "bayesian_tbr_calibration_replay"
    BAYESIAN_SPARSE_COUNT_RATE = "bayesian_tbr_sparse_count_rate"
    BAYESIAN_MULTICELL = "bayesian_tbr_multicell_shared_control"
    VS_TBRRIDGE = "tbr_vs_tbrridge_boundary"
    VS_DID = "tbr_vs_did_boundary"
    VS_SCM_AUGSYNTH = "tbr_vs_scm_augsynth_boundary"


class BoundaryStatus(str, Enum):
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    POSTERIOR_DIAGNOSTIC_ONLY = "posterior_diagnostic_only"
    RETIRE_OR_REPLACE = "retire_or_replace"
    REMEDIATION_REQUIRED = "remediation_required"
    CANDIDATE_AFTER_CALIBRATION_REPLAY = "candidate_after_calibration_replay"
    CANDIDATE_AFTER_SIMULATION = "candidate_after_simulation"


REQUIRED_PATHS = frozenset(PathType)
REQUIRED_STATUSES = frozenset(BoundaryStatus)


@dataclass(frozen=True)
class TbrBoundaryRow:
    boundary_id: str
    name: str
    method_family: MethodFamily
    path_type: PathType
    current_status: BoundaryStatus
    known_blockers: tuple[str, ...]
    required_diagnostics: tuple[str, ...]
    required_dgp_coverage: tuple[str, ...]
    required_assignment_stress: tuple[str, ...]
    required_failure_registry_checks: tuple[str, ...]
    required_calibration_evidence: tuple[str, ...]
    allowed_current_use: tuple[str, ...]
    forbidden_current_use: tuple[str, ...]
    retire_or_replace_candidate: bool
    promotion_hypothesis: bool
    promotion_evidence_required: tuple[str, ...]
    recommended_next_artifact: str | None
    notes: str


def _row(
    boundary_id: str,
    name: str,
    method_family: MethodFamily,
    path_type: PathType,
    current_status: BoundaryStatus,
    notes: str,
    *,
    known_blockers: tuple[str, ...],
    required_diagnostics: tuple[str, ...],
    required_dgp_coverage: tuple[str, ...],
    required_assignment_stress: tuple[str, ...],
    required_failure_registry_checks: tuple[str, ...],
    required_calibration_evidence: tuple[str, ...],
    allowed_current_use: tuple[str, ...],
    forbidden_current_use: tuple[str, ...],
    retire_or_replace_candidate: bool = False,
    promotion_hypothesis: bool = False,
    promotion_evidence_required: tuple[str, ...],
    recommended_next_artifact: str | None = None,
) -> TbrBoundaryRow:
    return TbrBoundaryRow(
        boundary_id=boundary_id,
        name=name,
        method_family=method_family,
        path_type=path_type,
        current_status=current_status,
        known_blockers=known_blockers,
        required_diagnostics=required_diagnostics,
        required_dgp_coverage=required_dgp_coverage,
        required_assignment_stress=required_assignment_stress,
        required_failure_registry_checks=required_failure_registry_checks,
        required_calibration_evidence=required_calibration_evidence,
        allowed_current_use=allowed_current_use,
        forbidden_current_use=forbidden_current_use,
        retire_or_replace_candidate=retire_or_replace_candidate,
        promotion_hypothesis=promotion_hypothesis,
        promotion_evidence_required=promotion_evidence_required,
        recommended_next_artifact=recommended_next_artifact,
        notes=notes,
    )


_PROMO = ("null_calibration", "dgp_coverage", "failure_registry_consult", "observed_diagnostics")
_FORBID = ("production_p_value", "causal_ci", "trustreport", "production_inference")
_NEXT = "METHOD_FAMILY_PROMOTION_CRITERIA_MATRIX_001"
_TROP = "TROP_RESEARCH_ONLY_BOUNDARY_AUDIT_001"
_TBRRIDGE_AUDIT = "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001"


def build_bayesian_tbr_and_tbr_retirement_boundary_audit() -> tuple[TbrBoundaryRow, ...]:
    """Return metadata-only TBR/Bayesian TBR boundary audit rows."""
    return (
        # Classic TBR point
        _row(
            "TBR-BND-001", "classic_tbr_point_diagnostic", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_POINT, BoundaryStatus.DIAGNOSTIC_ONLY,
            "Classic TBR point may support diagnostic readout only.",
            known_blockers=("aggregate_geometry_mismatch",),
            required_diagnostics=("OPD-PF-001", "OPD-DS-005"),
            required_dgp_coverage=("DGP-ES-007",),
            required_assignment_stress=("ST-AD-001",),
            required_failure_registry_checks=("FM-ES-007",),
            required_calibration_evidence=(),
            allowed_current_use=("diagnostic_point_readout",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            "TBR-BND-002", "classic_tbr_point_production_blocked", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_POINT, BoundaryStatus.BLOCKED,
            "Classic TBR production inference remains unauthorized.",
            known_blockers=("no_valid_inference_path",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_calibration_evidence=("null_fpr_gate",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-003", "classic_tbr_point_research_only", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_POINT, BoundaryStatus.RESEARCH_ONLY,
            "Classic TBR point remains research-only pending boundary audit.",
            known_blockers=("small_n_overclaim",),
            required_diagnostics=("OPD-PS-010",),
            required_dgp_coverage=("DGP-PS-010",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PS-010",),
            required_calibration_evidence=(),
            allowed_current_use=("labeled_research",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO,
        ),
        # Classic aggregate/global
        _row(
            "TBR-BND-004", "classic_tbr_aggregate_blocked", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_AGGREGATE_GLOBAL, BoundaryStatus.BLOCKED,
            "Classic/aggregate TBR overclaim paths are blocked.",
            known_blockers=("aggregate_geometry_mismatch", "global_causal_overclaim"),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-ES-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-007", "FM-INF-011"),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID + ("aggregate_promotion",),
            retire_or_replace_candidate=True,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-005", "classic_tbr_aggregate_retire_or_replace", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_AGGREGATE_GLOBAL, BoundaryStatus.RETIRE_OR_REPLACE,
            "Aggregate/global TBR is retire/replace candidate.",
            known_blockers=("geo_aggregate_mismatch",),
            required_diagnostics=("OPD-DS-005",),
            required_dgp_coverage=("DGP-ES-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-007",),
            required_calibration_evidence=(),
            allowed_current_use=("retire_replace_review",),
            forbidden_current_use=_FORBID,
            retire_or_replace_candidate=True,
            promotion_evidence_required=_PROMO,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "TBR-BND-006", "classic_tbr_aggregate_remediation", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_AGGREGATE_GLOBAL, BoundaryStatus.REMEDIATION_REQUIRED,
            "Aggregate readout requires explicit estimand remediation.",
            known_blockers=("pooled_estimand_ambiguity",),
            required_diagnostics=("OPD-AD-005",),
            required_dgp_coverage=("DGP-AD-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DA-006",),
            required_calibration_evidence=(),
            allowed_current_use=("estimand_remediation",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # Classic per-cell/marginal
        _row(
            "TBR-BND-007", "classic_tbr_per_cell_diagnostic", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_PER_CELL_MARGINAL, BoundaryStatus.DIAGNOSTIC_ONLY,
            "Per-cell marginal TBR is diagnostic-only.",
            known_blockers=("multiplicity_unresolved",),
            required_diagnostics=("OPD-MC-004",),
            required_dgp_coverage=("DGP-MC-001",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DA-009",),
            required_calibration_evidence=(),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID + ("pooled_inference",),
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            "TBR-BND-008", "classic_tbr_per_cell_research", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_PER_CELL_MARGINAL, BoundaryStatus.RESEARCH_ONLY,
            "Per-cell TBR remains research-only without multiplicity handling.",
            known_blockers=("familywise_risk",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-002",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-009",),
            required_calibration_evidence=(),
            allowed_current_use=("multicell_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # Classic residual/bootstrap
        _row(
            "TBR-BND-009", "classic_tbr_bootstrap_blocked", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_RESIDUAL_BOOTSTRAP, BoundaryStatus.BLOCKED,
            "Classic TBR bootstrap/residual inference not production-valid.",
            known_blockers=("bootstrap_uncalibrated",),
            required_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-INF-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-003",),
            required_calibration_evidence=("bootstrap_null_calibration",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-010", "classic_tbr_bootstrap_research", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_RESIDUAL_BOOTSTRAP, BoundaryStatus.RESEARCH_ONLY,
            "Bootstrap paths require research DGP before any promotion hypothesis.",
            known_blockers=("dependence_unmodeled",),
            required_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-INF-003", "DGP-CP-002"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-003",),
            required_calibration_evidence=("bootstrap_null_calibration",),
            allowed_current_use=("bootstrap_research",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO,
        ),
        # Classic placebo/rank
        _row(
            "TBR-BND-011", "classic_tbr_placebo_blocked", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_PLACEBO_RANK, BoundaryStatus.BLOCKED,
            "Classic TBR placebo blocked without valid assignment support.",
            known_blockers=("invalid_assignment",),
            required_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001", "FM-INF-001"),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-012", "classic_tbr_placebo_diagnostic", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_PLACEBO_RANK, BoundaryStatus.DIAGNOSTIC_ONLY,
            "Placebo rank may support null-monitor diagnostic only.",
            known_blockers=("overinterpretation_risk",),
            required_diagnostics=("OPD-AD-009", "OPD-TE-001"),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-INF-001",),
            required_calibration_evidence=(),
            allowed_current_use=("null_monitor_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        # Classic deterministic/unknown
        _row(
            "TBR-BND-013", "classic_tbr_unknown_assignment_blocked", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_DETERMINISTIC_UNKNOWN, BoundaryStatus.BLOCKED,
            "Unknown assignment blocks classic TBR inference.",
            known_blockers=("unknown_assignment",),
            required_diagnostics=("OPD-AD-001",),
            required_dgp_coverage=("DGP-DA-001",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-DA-001",),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-014", "classic_tbr_deterministic_falsification", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_DETERMINISTIC_UNKNOWN, BoundaryStatus.DIAGNOSTIC_ONLY,
            "Deterministic designs may support falsification-only readouts.",
            known_blockers=("causal_claim_blocked",),
            required_diagnostics=("OPD-AD-002",),
            required_dgp_coverage=("DGP-DA-002",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DA-002",),
            required_calibration_evidence=(),
            allowed_current_use=("falsification_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        # Classic multicell
        _row(
            "TBR-BND-015", "classic_tbr_multicell_blocked", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_MULTICELL, BoundaryStatus.BLOCKED,
            "TBR multicell blocked without dependence/multiplicity handling.",
            known_blockers=("shared_control_dependence",),
            required_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009", "FM-INF-009"),
            required_calibration_evidence=(),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID + ("pooled_inference",),
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-016", "classic_tbr_multicell_research", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_MULTICELL, BoundaryStatus.RESEARCH_ONLY,
            "Multicell classic TBR remains research-only.",
            known_blockers=("multiplicity_unresolved",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-001",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009",),
            required_calibration_evidence=(),
            allowed_current_use=("multicell_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # Bayesian posterior diagnostic
        _row(
            "TBR-BND-017", "bayesian_tbr_posterior_diagnostic", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_POSTERIOR_DIAGNOSTIC, BoundaryStatus.POSTERIOR_DIAGNOSTIC_ONLY,
            "Bayesian TBR may remain posterior-diagnostic until calibrated.",
            known_blockers=("posterior_not_causal",),
            required_diagnostics=("OPD-PF-001",),
            required_dgp_coverage=("DGP-ES-008",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-008",),
            required_calibration_evidence=(),
            allowed_current_use=("posterior_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-018", "bayesian_tbr_production_blocked", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_POSTERIOR_DIAGNOSTIC, BoundaryStatus.BLOCKED,
            "Bayesian TBR production inference remains unauthorized.",
            known_blockers=("no_production_authorization",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_calibration_evidence=("null_fpr_gate",),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # Bayesian posterior interval
        _row(
            "TBR-BND-019", "bayesian_tbr_posterior_interval_diagnostic", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_POSTERIOR_INTERVAL, BoundaryStatus.POSTERIOR_DIAGNOSTIC_ONLY,
            "Posterior intervals are diagnostic uncertainty, not causal CIs.",
            known_blockers=("interval_semantics_mismatch",),
            required_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-ES-008",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-008", "FM-INF-008"),
            required_calibration_evidence=(),
            allowed_current_use=("posterior_interval_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            "TBR-BND-020", "bayesian_tbr_posterior_interval_research", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_POSTERIOR_INTERVAL, BoundaryStatus.RESEARCH_ONLY,
            "Posterior interval research requires calibration/replay evidence.",
            known_blockers=("uncalibrated_posterior",),
            required_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-ES-008", "DGP-INF-008"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-008",),
            required_calibration_evidence=("posterior_coverage_replay",),
            allowed_current_use=("posterior_research",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO,
        ),
        # Credible as causal CI - blocked
        _row(
            "TBR-BND-021", "bayesian_tbr_credible_as_causal_ci_blocked", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_CREDIBLE_AS_CAUSAL_CI, BoundaryStatus.BLOCKED,
            "Credible intervals interpreted as causal CIs are blocked.",
            known_blockers=("posterior_as_causal_ci",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-008",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-008", "FM-INF-008", "FM-DB-010"),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID + ("causal_ci_claim",),
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-022", "bayesian_tbr_credible_interval_mislabel_blocked", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_CREDIBLE_AS_CAUSAL_CI, BoundaryStatus.BLOCKED,
            "Mislabeled credible intervals must not authorize TrustReport.",
            known_blockers=("trustreport_misuse",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-010",),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID + ("trustreport",),
            promotion_evidence_required=_PROMO,
        ),
        # Prior sensitivity
        _row(
            "TBR-BND-023", "bayesian_tbr_prior_sensitivity_research", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_PRIOR_SENSITIVITY, BoundaryStatus.RESEARCH_ONLY,
            "Prior sensitivity analysis is research-only.",
            known_blockers=("prior_dominance",),
            required_diagnostics=("OPD-ES-008",),
            required_dgp_coverage=("DGP-ES-008",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-008",),
            required_calibration_evidence=("prior_sensitivity_report",),
            allowed_current_use=("prior_sensitivity_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-024", "bayesian_tbr_prior_sensitivity_remediation", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_PRIOR_SENSITIVITY, BoundaryStatus.REMEDIATION_REQUIRED,
            "Prior specification requires remediation before promotion hypothesis.",
            known_blockers=("informative_prior_risk",),
            required_diagnostics=("OPD-ES-008",),
            required_dgp_coverage=("DGP-ES-008",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-008",),
            required_calibration_evidence=("prior_justification",),
            allowed_current_use=("prior_remediation",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # PPC
        _row(
            "TBR-BND-025", "bayesian_tbr_ppc_diagnostic", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_PPC, BoundaryStatus.POSTERIOR_DIAGNOSTIC_ONLY,
            "Posterior predictive checks are diagnostic-only.",
            known_blockers=("model_misfit",),
            required_diagnostics=("OPD-PF-001", "OPD-PF-003"),
            required_dgp_coverage=("DGP-PF-001",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-001",),
            required_calibration_evidence=(),
            allowed_current_use=("ppc_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            "TBR-BND-026", "bayesian_tbr_ppc_research", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_PPC, BoundaryStatus.RESEARCH_ONLY,
            "PPC research supports model adequacy assessment only.",
            known_blockers=("ppc_not_inference",),
            required_diagnostics=("OPD-PF-003",),
            required_dgp_coverage=("DGP-PF-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-PF-003",),
            required_calibration_evidence=("ppc_calibration",),
            allowed_current_use=("ppc_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # Calibration/replay
        _row(
            "TBR-BND-027", "bayesian_tbr_calibration_replay_candidate", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_CALIBRATION_REPLAY, BoundaryStatus.CANDIDATE_AFTER_CALIBRATION_REPLAY,
            "Promotion requires calibration/replay evidence for causal coverage.",
            known_blockers=("uncalibrated_posterior",),
            required_diagnostics=("OPD-IR-004", "OPD-IR-005"),
            required_dgp_coverage=("DGP-ES-008", "DGP-INF-008"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-INF-008",),
            required_calibration_evidence=("posterior_coverage_replay", "null_fpr_gate"),
            allowed_current_use=("calibration_replay_research",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO + ("calibration_replay",),
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "TBR-BND-028", "bayesian_tbr_calibration_replay_simulation", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_CALIBRATION_REPLAY, BoundaryStatus.CANDIDATE_AFTER_SIMULATION,
            "Simulation DGP required before calibration/replay promotion.",
            known_blockers=("no_simulation_evidence",),
            required_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-CP-002", "DGP-ES-008"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-002",),
            required_calibration_evidence=("simulation_null_calibration",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO,
        ),
        # Bayesian sparse/count/rate
        _row(
            "TBR-BND-029", "bayesian_tbr_sparse_blocked", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_SPARSE_COUNT_RATE, BoundaryStatus.BLOCKED,
            "Sparse/count/rate outcomes block Bayesian TBR without DGP.",
            known_blockers=("outcome_scale_mismatch",),
            required_diagnostics=("OPD-OM-003", "OPD-OM-004"),
            required_dgp_coverage=("DGP-OM-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_calibration_evidence=(),
            allowed_current_use=("outcome_scale_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-030", "bayesian_tbr_sparse_simulation", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_SPARSE_COUNT_RATE, BoundaryStatus.CANDIDATE_AFTER_SIMULATION,
            "Outcome-scale Bayesian TBR requires simulation before promotion.",
            known_blockers=("likelihood_misspecification",),
            required_diagnostics=("OPD-OM-003",),
            required_dgp_coverage=("DGP-OM-003", "DGP-OM-005"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-OM-003",),
            required_calibration_evidence=("outcome_scale_calibration",),
            allowed_current_use=("simulation_research",),
            forbidden_current_use=_FORBID,
            promotion_hypothesis=True,
            promotion_evidence_required=_PROMO,
        ),
        # Bayesian multicell
        _row(
            "TBR-BND-031", "bayesian_tbr_multicell_blocked", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_MULTICELL, BoundaryStatus.BLOCKED,
            "Bayesian TBR multicell blocked without dependence handling.",
            known_blockers=("multicell_dependence",),
            required_diagnostics=("OPD-MC-001", "OPD-MC-004"),
            required_dgp_coverage=("DGP-MC-002",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-DA-009",),
            required_calibration_evidence=(),
            allowed_current_use=("per_cell_diagnostic",),
            forbidden_current_use=_FORBID + ("pooled_inference",),
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-032", "bayesian_tbr_multicell_research", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_MULTICELL, BoundaryStatus.RESEARCH_ONLY,
            "Bayesian multicell remains research-only.",
            known_blockers=("multiplicity_unresolved",),
            required_diagnostics=("OPD-MC-001",),
            required_dgp_coverage=("DGP-MC-001",),
            required_assignment_stress=("ST-AD-010",),
            required_failure_registry_checks=("FM-INF-009",),
            required_calibration_evidence=(),
            allowed_current_use=("multicell_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # vs TBRRidge
        _row(
            "TBR-BND-033", "tbr_vs_tbrridge_boundary_preserved", MethodFamily.BOTH,
            PathType.VS_TBRRIDGE, BoundaryStatus.BLOCKED,
            "TBRRidge prior audit decision must not be reversed.",
            known_blockers=("tbrridge_audit_supersedes",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-ES-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006",),
            required_calibration_evidence=(),
            allowed_current_use=("boundary_consultation",),
            forbidden_current_use=_FORBID + ("tbrridge_promotion_override",),
            promotion_evidence_required=("tbrridge_audit_consult",),
            recommended_next_artifact=_TBRRIDGE_AUDIT,
        ),
        _row(
            "TBR-BND-034", "tbr_vs_tbrridge_diagnostic_separation", MethodFamily.BOTH,
            PathType.VS_TBRRIDGE, BoundaryStatus.DIAGNOSTIC_ONLY,
            "TBR and TBRRidge diagnostic lanes remain separate.",
            known_blockers=("method_conflation",),
            required_diagnostics=("OPD-ES-006",),
            required_dgp_coverage=("DGP-ES-006", "DGP-ES-007"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006", "FM-ES-007"),
            required_calibration_evidence=(),
            allowed_current_use=("method_separation_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("tbrridge_audit_consult",),
        ),
        # vs DID
        _row(
            "TBR-BND-035", "tbr_vs_did_boundary", MethodFamily.BOTH,
            PathType.VS_DID, BoundaryStatus.RESEARCH_ONLY,
            "TBR vs DID comparison is research-only.",
            known_blockers=("parallel_trend_ambiguity",),
            required_diagnostics=("OPD-PF-003",),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-ES-005",),
            required_calibration_evidence=(),
            allowed_current_use=("method_comparison_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-036", "tbr_vs_did_did_suitability_gate", MethodFamily.BOTH,
            PathType.VS_DID, BoundaryStatus.REMEDIATION_REQUIRED,
            "DID suitability audit must pass before TBR-DID comparison.",
            known_blockers=("did_suitability_unmet",),
            required_diagnostics=("OPD-PF-003", "OPD-AD-009"),
            required_dgp_coverage=("DGP-ES-005",),
            required_assignment_stress=("ST-AD-009",),
            required_failure_registry_checks=("FM-ES-005",),
            required_calibration_evidence=(),
            allowed_current_use=("did_comparison_remediation",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        # vs SCM/AugSynth
        _row(
            "TBR-BND-037", "tbr_vs_scm_augsynth_boundary", MethodFamily.BOTH,
            PathType.VS_SCM_AUGSYNTH, BoundaryStatus.RETIRE_OR_REPLACE,
            "TBR family is retire/replace relative to SCM/AugSynth for causal claims.",
            known_blockers=("scm_stronger_candidate",),
            required_diagnostics=("OPD-ES-005",),
            required_dgp_coverage=("DGP-ES-001", "DGP-ES-003"),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-002", "FM-ES-003"),
            required_calibration_evidence=(),
            allowed_current_use=("retire_replace_review",),
            forbidden_current_use=_FORBID,
            retire_or_replace_candidate=True,
            promotion_evidence_required=_PROMO,
            recommended_next_artifact=_NEXT,
        ),
        _row(
            "TBR-BND-038", "tbr_vs_scm_augsynth_diagnostic_only", MethodFamily.BOTH,
            PathType.VS_SCM_AUGSYNTH, BoundaryStatus.DIAGNOSTIC_ONLY,
            "TBR may remain diagnostic when SCM/AugSynth promotion gates pass.",
            known_blockers=("causal_overclaim",),
            required_diagnostics=("OPD-DS-005", "OPD-PF-001"),
            required_dgp_coverage=("DGP-ES-001",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-007",),
            required_calibration_evidence=(),
            allowed_current_use=("complementary_diagnostic",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("scm_augsynth_comparison",),
        ),
        # Cross-cutting gates
        _row(
            "TBR-BND-039", "observed_diagnostics_global_gate", MethodFamily.BOTH,
            PathType.CLASSIC_POINT, BoundaryStatus.REMEDIATION_REQUIRED,
            "Observed diagnostics required before TBR method selection.",
            known_blockers=("diagnostics_missing",),
            required_diagnostics=("OPD-PS-001", "OPD-PF-001"),
            required_dgp_coverage=("DGP-CP-003",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-003",),
            required_calibration_evidence=(),
            allowed_current_use=("diagnostic_routing",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("observed_diagnostics",),
        ),
        _row(
            "TBR-BND-040", "dgp_coverage_global_gate", MethodFamily.BOTH,
            PathType.BAYESIAN_POSTERIOR_INTERVAL, BoundaryStatus.REMEDIATION_REQUIRED,
            "DGP coverage required before TBR-family promotion.",
            known_blockers=("dgp_coverage_gap",),
            required_diagnostics=("OPD-IR-004",),
            required_dgp_coverage=("DGP-CP-002",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-002",),
            required_calibration_evidence=(),
            allowed_current_use=("dgp_planning",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-041", "failure_registry_global_gate", MethodFamily.BOTH,
            PathType.CLASSIC_POINT, BoundaryStatus.REMEDIATION_REQUIRED,
            "Failure registry consultation required.",
            known_blockers=("registry_not_consulted",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-CP-004",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-004",),
            required_calibration_evidence=(),
            allowed_current_use=("registry_consultation",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=("failure_registry_consult",),
        ),
        _row(
            "TBR-BND-042", "design_stress_global_gate", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_PLACEBO_RANK, BoundaryStatus.REMEDIATION_REQUIRED,
            "Design assignment stress required for placebo paths.",
            known_blockers=("assignment_stress_missing",),
            required_diagnostics=("OPD-AD-009",),
            required_dgp_coverage=("DGP-AD-010",),
            required_assignment_stress=("ST-AD-009", "ST-AD-010"),
            required_failure_registry_checks=("FM-DA-001",),
            required_calibration_evidence=(),
            allowed_current_use=("stress_test_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-043", "classic_tbr_pvalue_global_block", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_POINT, BoundaryStatus.BLOCKED,
            "Global block on classic TBR production p-values.",
            known_blockers=("production_pvalue_blocked",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-044", "classic_tbr_causal_ci_global_block", MethodFamily.CLASSIC_TBR,
            PathType.CLASSIC_RESIDUAL_BOOTSTRAP, BoundaryStatus.BLOCKED,
            "Global block on classic TBR causal confidence intervals.",
            known_blockers=("causal_ci_blocked",),
            required_diagnostics=("OPD-IR-005",),
            required_dgp_coverage=("DGP-INF-007",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-010",),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-045", "bayesian_tbr_pvalue_global_block", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_POSTERIOR_INTERVAL, BoundaryStatus.BLOCKED,
            "Global block on Bayesian TBR production p-values.",
            known_blockers=("production_pvalue_blocked",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-013",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-DB-009",),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-046", "bayesian_tbr_posterior_not_causal_ci_gate", MethodFamily.BAYESIAN_TBR,
            PathType.BAYESIAN_CREDIBLE_AS_CAUSAL_CI, BoundaryStatus.BLOCKED,
            "Posterior intervals are not causal confidence intervals — global gate.",
            known_blockers=("posterior_as_causal_ci",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-INF-008",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-008", "FM-INF-008"),
            required_calibration_evidence=(),
            allowed_current_use=(),
            forbidden_current_use=_FORBID + ("causal_ci_claim",),
            promotion_evidence_required=_PROMO,
        ),
        _row(
            "TBR-BND-047", "tbrridge_audit_reference_preserved", MethodFamily.BOTH,
            PathType.VS_TBRRIDGE, BoundaryStatus.BLOCKED,
            "TBRRIDGE_INFERENCE_REMEDIATION_OR_RETIREMENT_AUDIT_001 decisions preserved.",
            known_blockers=("tbrridge_reversal_forbidden",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-ES-006",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-ES-006",),
            required_calibration_evidence=(),
            allowed_current_use=("audit_reference",),
            forbidden_current_use=("tbrridge_promotion_override",),
            promotion_evidence_required=("tbrridge_audit_consult",),
            recommended_next_artifact=_TBRRIDGE_AUDIT,
        ),
        _row(
            "TBR-BND-048", "tbr_family_downstream_paused", MethodFamily.BOTH,
            PathType.CLASSIC_POINT, BoundaryStatus.RESEARCH_ONLY,
            "TBR-family downstream work paused pending promotion criteria matrix.",
            known_blockers=("downstream_paused",),
            required_diagnostics=("OPD-IR-010",),
            required_dgp_coverage=("DGP-CP-005",),
            required_assignment_stress=(),
            required_failure_registry_checks=("FM-CP-005",),
            required_calibration_evidence=(),
            allowed_current_use=("labeled_research",),
            forbidden_current_use=_FORBID,
            promotion_evidence_required=_PROMO,
            recommended_next_artifact=_TROP,
        ),
    )


def filter_bayesian_tbr_and_tbr_retirement_boundary_audit(
    rows: tuple[TbrBoundaryRow, ...],
    *,
    path_type: PathType | None = None,
    current_status: BoundaryStatus | None = None,
    method_family: MethodFamily | None = None,
    retire_or_replace_candidate: bool | None = None,
) -> tuple[TbrBoundaryRow, ...]:
    """Filter boundary audit rows by optional criteria."""
    result: list[TbrBoundaryRow] = []
    for row in rows:
        if path_type is not None and row.path_type != path_type:
            continue
        if current_status is not None and row.current_status != current_status:
            continue
        if method_family is not None and row.method_family != method_family:
            continue
        if retire_or_replace_candidate is not None and row.retire_or_replace_candidate != retire_or_replace_candidate:
            continue
        result.append(row)
    return tuple(result)


def validate_bayesian_tbr_and_tbr_retirement_boundary_audit(
    rows: tuple[TbrBoundaryRow, ...],
) -> dict[str, Any]:
    """Validate boundary audit registry thresholds and coverage."""
    issues: list[str] = []
    boundary_ids = [r.boundary_id for r in rows]

    if len(rows) < MIN_BOUNDARY_ROW_COUNT:
        issues.append(f"boundary_row_count {len(rows)} < {MIN_BOUNDARY_ROW_COUNT}")
    if len(boundary_ids) != len(set(boundary_ids)):
        issues.append("duplicate boundary_id values")

    status_counts = Counter(r.current_status for r in rows)
    family_counts = Counter(r.method_family.value for r in rows)
    path_counts = Counter(r.path_type.value for r in rows)

    for path in REQUIRED_PATHS:
        if not any(r.path_type == path for r in rows):
            issues.append(f"missing path_type: {path.value}")

    for status in REQUIRED_STATUSES:
        if status_counts.get(status, 0) == 0:
            issues.append(f"missing status: {status.value}")

    retire_rows = [r for r in rows if r.retire_or_replace_candidate]
    if not retire_rows:
        issues.append("no retire_or_replace_candidate rows")

    blocked_aggregate = any(
        r.path_type == PathType.CLASSIC_AGGREGATE_GLOBAL
        and r.current_status == BoundaryStatus.BLOCKED
        for r in rows
    )
    if not blocked_aggregate:
        issues.append("classic aggregate overclaim blocker missing")

    tbrridge_preserved = any(
        r.path_type == PathType.VS_TBRRIDGE
        and "tbrridge" in r.notes.lower()
        for r in rows
    )
    if not tbrridge_preserved:
        issues.append("TBRRidge boundary preservation row missing")

    unlinked = [r.boundary_id for r in rows if not r.required_failure_registry_checks]
    if unlinked:
        issues.append(f"rows missing required_failure_registry_checks: {unlinked}")

    return {
        "valid": not issues,
        "boundary_row_count": len(rows),
        "unique_boundary_ids": len(boundary_ids) == len(set(boundary_ids)),
        "status_counts": {s.value: status_counts.get(s, 0) for s in BoundaryStatus},
        "method_family_counts": dict(family_counts),
        "path_type_counts": dict(path_counts),
        "all_required_paths_covered": all(
            any(r.path_type == p for r in rows) for p in REQUIRED_PATHS
        ),
        "all_statuses_represented": all(status_counts.get(s, 0) > 0 for s in REQUIRED_STATUSES),
        "retire_or_replace_paths_defined": bool(retire_rows),
        "issues": issues,
    }


def summarize_bayesian_tbr_and_tbr_retirement_boundary_audit(
    rows: tuple[TbrBoundaryRow, ...],
) -> dict[str, Any]:
    """Serialize TBR boundary audit summary for archives."""
    validation = validate_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    return {
        "artifact_id": _ARTIFACT_ID,
        "status": "completed",
        "verdict": _VERDICT,
        "boundary_row_count": len(rows),
        "failed_scenarios": validation.get("issues", []),
        "status_counts": validation["status_counts"],
        "method_family_counts": validation["method_family_counts"],
        "path_type_counts": validation["path_type_counts"],
        "all_required_paths_covered": validation["all_required_paths_covered"],
        "classic_tbr_retire_or_replace_paths_defined": validation["retire_or_replace_paths_defined"],
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
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    validation = validate_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    summary = summarize_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    scenarios: list[dict[str, Any]] = []

    scenarios.append(_scenario("boundary_rows_build_successfully", len(rows) > 0))
    scenarios.append(_scenario("boundary_row_count_at_least_45", len(rows) >= MIN_BOUNDARY_ROW_COUNT))
    scenarios.append(_scenario("boundary_ids_unique", validation["unique_boundary_ids"]))

    for path in REQUIRED_PATHS:
        present = any(r.path_type == path for r in rows)
        scenarios.append(_scenario(f"path_type_{path.value}_represented", present))

    for status in REQUIRED_STATUSES:
        count = sum(1 for r in rows if r.current_status == status)
        scenarios.append(_scenario(f"status_{status.value}_represented", count > 0))

    for flag, expected in _BOUNDARY_FLAGS.items():
        scenarios.append(_scenario(flag, summary[flag] is expected))

    for flag, expected in _AUTH_FLAGS.items():
        scenarios.append(_scenario(f"authorization_{flag}_false", summary[flag] is expected))

    scenarios.append(_scenario(
        "recommended_next_artifact_rank_1_trop_research_only_boundary_audit_001",
        summary["recommended_next_artifacts"][0] == RECOMMENDED_NEXT_ARTIFACTS[0],
    ))

    scenarios.append(_scenario("validation_issues_empty", validation["valid"]))
    scenarios.append(_scenario("failed_scenarios_empty", all(s["passed"] for s in scenarios)))

    return scenarios


def run_validation(*, write_summary: bool = True, summary_path: Path | None = None) -> dict[str, Any]:
    rows = build_bayesian_tbr_and_tbr_retirement_boundary_audit()
    validation = validate_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
    summary = summarize_bayesian_tbr_and_tbr_retirement_boundary_audit(rows)
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
